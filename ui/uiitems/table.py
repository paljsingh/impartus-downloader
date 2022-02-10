import os
from datetime import datetime
from functools import partial
from typing import List
from pathlib import Path

import qtawesome as qta

from PySide2 import QtCore, QtWidgets
from PySide2.QtCore import QItemSelection
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QWidget, QPushButton, QAbstractItemView

from lib.config import Config, ConfigType
from lib.core.impartus import Impartus
from lib.data.labels import Labels
from lib.finder import Finder
from lib.threadlogging import ThreadLogger
from lib.utils import Utils
from ui.callbacks.utils import CallbackUtils
from ui.callbacks.menucallbacks import MenuCallbacks
from ui.helpers.datautils import DataUtils
from ui.helpers.widgetcreator import WidgetCreator
from ui.uiitems.customwidgets.tablewidgetitem import CustomTableWidgetItem
from lib.data.Icons import Icons
from lib.data.actionitems import ActionItems
from lib.data.columns import Columns
from ui.uiitems.progressbar import SortableRoundProgressbar
from ui.delegates.rodelegate import ReadOnlyDelegate
from ui.delegates.writedelegate import WriteDelegate


class Table:
    """
    Table class:
    Creates a table and provides methods to get / set table headers and its properties, as well as the table data..
    Also own the handler methods called by the widgets contained in the table.

    The handler methods defined here can/should be reused by the menu items event handlers (defined in callbacks.py).
    Except for the difference that,
    while the table class widgets have the required video / slides / captions available to them when creating the
    widgets, the menu items handler first need to collect this info from the currently selected row / content
    and then pass on that info to the handlers defined in this class.
    """

    def __init__(self, table_widget: QTableWidget, impartus: Impartus, callbacks):
        self.signal_connected = False
        self.conf = Config.load(ConfigType.IMPARTUS)
        self.impartus = impartus
        self.callbacks = callbacks

        self.readonly_delegate = ReadOnlyDelegate()
        self.write_delegate = WriteDelegate(self.get_data)
        self.logger = ThreadLogger(self.__class__.__name__).logger

        self.table_widget = self._setup_table(table_widget)
        self.table_widget.selectionModel().selectionChanged.connect(self.on_row_select)

        self.video_ids = dict()
        self.selected_checkbox = None
        self.index = 0      # table rows

    def get_data(self):
        return self.video_ids

    def reset_content(self):
        self.video_ids = dict()
        self.index = 0
        self.table_widget = self._setup_table(self.table_widget)
        self.table_widget.setSortingEnabled(False)

    def _setup_table(self, table_widget):
        table_widget.setSortingEnabled(False)
        table_widget.clear()
        table_widget.setRowCount(0)

        # table height/width adjustment
        app_width = QtWidgets.QApplication.primaryScreen().size().width()
        app_height = QtWidgets.QApplication.primaryScreen().size().height()
        tab_width = 20
        margin = 20

        log_window_height = 200
        search_window_height = 50
        splitter_height = 10

        table_max_width = app_width - tab_width - 2*margin
        table_max_height = app_height - log_window_height - search_window_height - splitter_height - 3*margin
        table_widget.setMaximumWidth(table_max_width)
        table_widget.setMaximumHeight(table_max_height)

        col_count = len(Columns.get_video_columns()) + 1
        table_widget.setColumnCount(col_count)
        table_widget = self._set_headers(table_widget)
        table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        return table_widget

    def post_fill_tasks(self):
        self.table_widget = self._set_resizable_headers(self.table_widget)
        self.table_widget.setSortingEnabled(True)
        self.table_widget.sortByColumn(
            Columns.get_video_column_index_by_key('startDate'), QtCore.Qt.SortOrder.DescendingOrder)

    def _set_headers(self, table_widget):
        # header item for checkboxes column
        widget = QTableWidgetItem()
        widget.setText('')
        table_widget.setHorizontalHeaderItem(0, widget)
        table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        table_widget.setColumnHidden(0, True)

        for i, (col, item) in enumerate(Columns.get_video_columns().items(), 1):
            if item.get('initial_size') and item['resize_policy'] != QHeaderView.ResizeMode.Stretch:
                table_widget.horizontalHeader().resizeSection(i, item.get('initial_size'))

        # enumerate from 1.
        for index, (key, val) in enumerate(Columns.get_video_columns().items(), 1):
            widget = QTableWidgetItem()
            widget.setText(val['display_name'])

            # make the column read-only if editable property not set.
            if not val['editable']:
                table_widget.setItemDelegateForColumn(index, self.readonly_delegate)
            else:
                widget.setIcon(qta.icon(Icons.TABLE__EDITABLE_COLUMN.value))
                table_widget.setItemDelegateForColumn(index, self.write_delegate)

            table_widget.horizontalHeader().setSectionResizeMode(index, val['resize_policy'])
            if val.get('hidden'):
                table_widget.setColumnHidden(index, True)
                pass

            table_widget.setHorizontalHeaderItem(index, widget)

        table_widget.horizontalHeader().setSortIndicatorShown(True)
        return table_widget

    def set_widget_statuses(self, video_id, video_downloaded=False, chat_downloaded=False):
        if self.video_ids.get(video_id):
            download_video_button = self.video_ids[video_id]['download_video_button']
            play_video_button = self.video_ids[video_id]['play_video_button']
            download_chat_button = self.video_ids[video_id]['download_chat_button']
            open_folder_button = self.video_ids[video_id]['open_folder_button']
            progressbar_widget = self.video_ids[video_id]['progressbar']

            download_video_button: QPushButton
            play_video_button: QPushButton
            progressbar_widget: SortableRoundProgressbar
            if video_downloaded:
                download_video_button.setEnabled(False)
                play_video_button.setEnabled(True)
                open_folder_button.setEnabled(True)
                progressbar_widget.setValue(100, int(datetime.utcnow().timestamp()))
            else:
                download_video_button.setEnabled(True)
                play_video_button.setEnabled(False)
                progressbar_widget.setValue(0, None)

            download_chat_button: QPushButton
            if self.impartus.is_authenticated() and not chat_downloaded:
                download_chat_button.setEnabled(True)
            else:
                download_chat_button.setEnabled(False)
                open_folder_button.setEnabled(True)

    def add_row_item(self, video_id, video_metadata, captions_path=None, is_flipped=False, video_downloaded=False):
        chat_downloaded = True if captions_path else False
        if video_downloaded:
            if self.video_ids.get(video_id):
                # the id is listed already (from online content) => update existing metadata
                self.video_ids[video_id]['metadata']['offline_filepath'] = video_metadata['offline_filepath']
                self.set_widget_statuses(video_id, video_downloaded, chat_downloaded)
                return

        self.table_widget.setRowCount(self.index + 1)

        # for each row, add a checkbox first.
        data = {
            'is_flipped': is_flipped,
            'video_id': video_id,
        }
        checkbox_container = WidgetCreator.add_checkbox_widget(data)
        self.table_widget.setCellWidget(self.index, 0, checkbox_container)

        # enumerate rest of the columns from 1
        for col, (key, val) in enumerate(Columns.get_video_data_columns().items(), 1):
            widget = QTableWidgetItem(str(video_metadata[key]))
            widget.setTextAlignment(val['alignment'])
            self.table_widget.setItem(self.index, col, widget)

        # total columns so far...
        col = len(Columns.get_video_data_columns()) + 1

        # flipped icon column.
        flipped_col = Columns.get_video_widget_columns()['flipped']
        flipped_icon = qta.icon(flipped_col['icon']) if is_flipped else QIcon()
        flipped_icon_widget = CustomTableWidgetItem()
        flipped_icon_widget.setIcon(flipped_icon)
        flipped_icon_widget.setTextAlignment(Columns.get_video_widget_columns()['flipped']['alignment'])
        int_value = 1 if is_flipped else 0
        flipped_icon_widget.setValue(int_value)
        flipped_icon_widget.setToolTip(Columns.get_video_widget_columns()['flipped']['menu_tooltip'])

        self.table_widget.setItem(self.index, col, flipped_icon_widget)
        col += 1

        # progress bar.
        progress_bar_widget = SortableRoundProgressbar()
        progress_bar_widget.setValue(0, None)
        progress_bar_widget.setAlignment(Columns.get_video_widget_columns()['progress_bar']['alignment'])
        self.table_widget.setItem(self.index, col, progress_bar_widget.table_widget_item)
        self.table_widget.setCellWidget(self.index, col, progress_bar_widget)
        if video_metadata.get('offline_filepath'):
            progress_bar_widget.setValue(100, None)
        col += 1

        video_actions_widget, cell_value = self.add_video_actions_buttons(video_metadata)
        self.table_widget.setCellWidget(self.index, col, video_actions_widget)
        self.table_widget.cellWidget(self.index, col).setContentsMargins(0, 0, 0, 0)

        custom_item = CustomTableWidgetItem()
        custom_item.setValue(cell_value)
        self.table_widget.setItem(self.index, col, custom_item)

        col += 1

        DataUtils.save_metadata(video_metadata)
        self.video_ids[video_id] = {
            'metadata': video_metadata,
            'checkbox': checkbox_container.layout().itemAt(0).widget(),
            'progressbar':  progress_bar_widget,
            'download_video_button': video_actions_widget.layout().itemAt(0).widget(),
            'play_video_button': video_actions_widget.layout().itemAt(1).widget(),
            'download_chat_button': video_actions_widget.layout().itemAt(2).widget(),
            'open_folder_button': video_actions_widget.layout().itemAt(3).widget(),
        }

        self.table_widget.setRowHeight(self.index, 48)
        self.set_widget_statuses(video_id, video_downloaded, chat_downloaded)
        CallbackUtils().processEvents()
        self.index += 1

    def _set_resizable_headers(self, table_widget):     # noqa
        for i in range(len(Columns.get_video_columns()) + 1):
            table_widget.horizontalHeader().setSectionResizeMode(i, QHeaderView.Interactive)
        return table_widget

    def on_row_deselect(self, row_index):
        progress_bar = self.table_widget.cellWidget(row_index, Columns.get_video_column_index_by_key('progressbar')).layout().itemAt(0).widget()
        progress_bar.setTextColor()

    def check_selected_row(self, row_index):
        cell_widget = self.table_widget.cellWidget(row_index, 0)  # current table row/cell
        if not cell_widget:
            return

        self.table_widget.scrollToItem(self.table_widget.item(row_index, 0))

        checkbox = cell_widget.layout().itemAt(0).widget()
        checkbox.setChecked(True)
        self.selected_checkbox = checkbox

    def set_progressbar_color(self, row_index, highlight=False):
        cell_widget = self.table_widget.cellWidget(row_index, 0)  # current table row/cell
        if not cell_widget:
            return

        progress_bar = self.table_widget.cellWidget(row_index, Columns.get_video_column_index_by_key(Labels.VIDEO__PROGRESSBAR.value))
        progress_bar.setTextColorHighlight() if highlight else progress_bar.setTextColorNormal()

    def on_row_select(self, selected_row: QItemSelection, deselected_row: QItemSelection):
        if len(selected_row.indexes()) > 0:
            selected_row_index = selected_row.indexes().pop().row()
            self.check_selected_row(selected_row_index)
            self.set_progressbar_color(selected_row_index, highlight=True)
        if len(deselected_row.indexes()) > 0:
            self.set_progressbar_color(deselected_row.indexes().pop().row(), highlight=False)

        MenuCallbacks().set_menu_statuses()

    def show_hide_column(self, column):
        col_index = None
        for i, col_name in enumerate(Columns.get_video_columns(), 1):
            if col_name == column:
                col_index = i
                break

        if self.table_widget.isColumnHidden(col_index):
            self.table_widget.setColumnHidden(col_index, False)
        else:
            self.table_widget.setColumnHidden(col_index, True)

    def set_button_state(self, row: int, action_item: str, field: str, status: bool):
        col_index = Columns.get_video_column_index_by_key(action_item)
        field_index = ActionItems.get_action_item_index(action_item, field)
        self.table_widget.cellWidget(row, col_index).layout().itemAt(field_index).widget().setEnabled(status)

    """
    MISC
    """
    def get_selected_row(self):
        for i in range(self.table_widget.rowCount()):
            if self.table_widget.cellWidget(i, 0).layout().itemAt(0).widget().isChecked():
                return i

    def add_video_actions_buttons(self, metadata):
        widget = QWidget()
        widget.setContentsMargins(0, 0, 0, 0)
        widget_layout = WidgetCreator.get_layout_widget(widget)
        widget_layout.setAlignment(Columns.get_video_widget_columns().get('video_actions')['alignment'])

        # make the widget searchable based on button states.
        download_video_state = None
        play_video_state = None
        download_chats_state = None

        is_authenticated = self.impartus.is_authenticated()

        is_flipped = False if metadata.get('ttid') else True
        rf_id = metadata.get('fcid') if is_flipped else metadata.get('ttid')

        for key, pushbutton in WidgetCreator.add_actions_buttons(ActionItems.video_actions):
            widget_layout.addWidget(pushbutton)

            # disable download button, if video exists locally.
            if pushbutton.objectName() == ActionItems.video_actions['download_video']['icon']:
                pushbutton.clicked.connect(partial(self.callbacks['download_video'], rf_id))

                if metadata.get('offline_filepath'):
                    download_video_state = False
                else:
                    if is_authenticated:
                        download_video_state = True
                    else:
                        download_video_state = False

                pushbutton.setEnabled(download_video_state)
            elif pushbutton.objectName() == ActionItems.video_actions['play_video']['icon']:
                pushbutton.clicked.connect(partial(self.callbacks['play_video'], rf_id))

                if metadata.get('offline_filepath'):
                    # enable play button, if video exists locally.
                    play_video_state = True
                else:
                    play_video_state = False

                pushbutton.setEnabled(play_video_state)
            elif pushbutton.objectName() == ActionItems.video_actions['download_chats']['icon']:
                pushbutton.clicked.connect(partial(self.callbacks['download_chats'], rf_id))

                # enable download chats button, if lecture chats file does not exist.
                filepath = Utils.get_captions_path(metadata)
                if filepath and os.path.exists(filepath):
                    download_chats_state = False
                else:
                    if is_authenticated:
                        download_chats_state = True
                    else:
                        download_chats_state = False

                pushbutton.setEnabled(download_chats_state)
            elif pushbutton.objectName() == ActionItems.video_actions['open_folder']['icon']:
                pushbutton.clicked.connect(partial(self.callbacks['open_folder'], rf_id))

                # enable download chats button, if lecture chats file does not exist.
                filepath = metadata.get('offline_filepath')
                if filepath and os.path.exists(filepath):
                    open_folder_state = True
                else:
                    open_folder_state = False

                pushbutton.setEnabled(open_folder_state)

        # a slightly hackish way to sort widgets -
        # create an integer out of the (button1_state, button2_state, ...)
        # pass it to a Custom TableWidgetItem with __lt__ overridden to provide numeric sort.
        cell_value = '{}{}{}'.format(int(download_video_state), int(play_video_state), int(download_chats_state))
        return widget, int(cell_value)

    def get_widgets(self, video_id):
        dl_button = self.video_ids[video_id]['download_video_button']
        pl_button = self.video_ids[video_id]['play_video_button']
        cc_button = self.video_ids[video_id]['download_chat_button']
        of_button = self.video_ids[video_id]['open_folder_button']
        progresbar_widget = self.video_ids[video_id]['progressbar']
        return progresbar_widget, (dl_button, pl_button, cc_button, of_button)

    def auto_organize__pre(self):
        # read mappings.
        # For each known video(and wtt) / document
        #   get current path, also get new (expected) path as per the mappings dict.
        #   if paths differ ->
        #       collect the items that need to be moved.
        # return items and show table.

        mappings_conf = Config.load(ConfigType.MAPPINGS).get('subjectNameShort')
        offline_videos_data = {k: v for k, v, _, _ in Finder().get_offline_videos()}

        commands = list()
        for video_id, video_info in self.video_ids.items():
            if video_id <= 0:
                continue
            video_metadata = video_info['metadata']

            # update shortSubjectName in metadata with lst known mapping if exists.
            if video_metadata.get('subjectNameShort') is not None \
                    and mappings_conf is not None \
                    and mappings_conf.get(video_metadata['subjectName']) is not None \
                    and video_metadata['subjectNameShort'] != mappings_conf[video_metadata['subjectName']]:
                video_metadata['subjectNameShort'] = mappings_conf[video_metadata['subjectName']]

            # the video (and vtt) should be placed here...
            expected_path = Utils.get_mkv_path(video_metadata)

            offline_video = offline_videos_data.get(video_id)

            # the actual path as found on disk...
            current_path = offline_video.get('offline_filepath')

            current_dir = os.path.dirname(current_path)
            expected_dir = os.path.dirname(expected_path)

            # collect all files that belong to this directory...
            if current_path != expected_path:
                for file in os.listdir(current_dir):
                    source_file = os.path.join(current_dir, file)
                    dest_file = os.path.join(expected_dir, file)
                    if source_file != dest_file:
                        commands.append({
                            'id': video_id,
                            'source': os.path.join(current_dir, file),
                            'dest': os.path.join(expected_dir, file)
                        })
        return commands

    def auto_organize__post(self, commands: List):
        for cmd in commands:
            # only videos and vtt captions.
            if cmd['source'].endswith('.mkv') or cmd['source'].endswith('.vtt'):
                Utils.move_and_rename_file(cmd['source'], cmd['dest'])
                Utils.cleanup_dir(Path(cmd['source']).parent.absolute())

                # update in-memory metadata.
                self.video_ids[cmd['id']]['metadata']['offline_filepath'] = cmd['dest']

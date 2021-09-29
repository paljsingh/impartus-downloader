import os
from functools import partial

import qtawesome as qta

from PySide2 import QtCore, QtWidgets
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QWidget, QPushButton, \
    QAbstractItemView

from lib.config import Config, ConfigType
from lib.core.impartus import Impartus
from lib.data import columns
from lib.threadlogging import ThreadLogger
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
        selection_model = self.table_widget.selectionModel()
        selection_model.currentChanged.connect(self.on_row_select)

    def _setup_table(self, table_widget):
        table_widget.setSortingEnabled(False)
        table_widget.clear()
        table_widget.setRowCount(0)
        borders = 10
        tab_width = 10
        table_widget.parentWidget().setMaximumWidth(QtWidgets.QApplication.primaryScreen().size().width() - 2 * borders)
        table_widget.setMaximumWidth(QtWidgets.QApplication.primaryScreen().size().width() - 2 * borders - tab_width)

        col_count = Columns.get_video_columns_count()
        table_widget.setColumnCount(col_count)
        table_widget = self._set_headers(table_widget)
        table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)

        return table_widget

    def post_fill_tasks(self):
        self.table_widget = self._set_resizable_headers(self.table_widget)
        self.table_widget.setSortingEnabled(True)
        self.table_widget.sortByColumn(
            Columns.get_column_index_by_key('startDate'), QtCore.Qt.SortOrder.DescendingOrder)

    def _set_headers(self, table_widget):
        # header item for checkboxes column
        widget = QTableWidgetItem()
        widget.setText('')
        table_widget.setHorizontalHeaderItem(0, widget)
        table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        table_widget.setColumnHidden(0, True)

        for i, (col, item) in enumerate(Columns.get_video_columns_dict().items(), 1):
            if item.get('initial_size') and item['resize_policy'] != QHeaderView.ResizeMode.Stretch:
                table_widget.horizontalHeader().resizeSection(i, item.get('initial_size'))

        # enumerate from 1.
        for index, (key, val) in enumerate(Columns.get_video_columns_dict().items(), 1):
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
                progressbar_widget.setValue(100)
            else:
                download_video_button.setEnabled(True)
                play_video_button.setEnabled(False)
                progressbar_widget.setValue(0)

            download_chat_button: QPushButton
            if self.impartus.is_authenticated() and not chat_downloaded:
                download_chat_button.setEnabled(True)
            else:
                download_chat_button.setEnabled(False)
                open_folder_button.setEnabled(True)

    def add_row_item(self, video_id, video_metadata, chats_path=None, is_flipped=False, video_downloaded=False):
        chat_downloaded = True if chats_path else False
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
        checkbox_container = WidgetCreator.add_checkbox_widget(data, self.on_click_checkbox)
        self.table_widget.setCellWidget(self.index, 0, checkbox_container)

        # enumerate rest of the columns from 1
        for col, (key, val) in enumerate(columns.video_data_columns.items(), 1):
            widget = QTableWidgetItem(str(video_metadata[key]))
            widget.setTextAlignment(val['alignment'])
            self.table_widget.setItem(self.index, col, widget)

        # total columns so far...
        col = len(columns.video_data_columns) + 1

        # flipped icon column.
        flipped_col = columns.video_widget_columns['flipped']
        flipped_icon = qta.icon(flipped_col['icon']) if is_flipped else QIcon()
        flipped_icon_widget = CustomTableWidgetItem()
        flipped_icon_widget.setIcon(flipped_icon)
        flipped_icon_widget.setTextAlignment(columns.video_widget_columns['flipped']['alignment'])
        int_value = 1 if is_flipped else 0
        flipped_icon_widget.setValue(int_value)
        flipped_icon_widget.setToolTip(columns.video_widget_columns['flipped']['menu_tooltip'])

        self.table_widget.setItem(self.index, col, flipped_icon_widget)
        col += 1

        # progress bar.
        progress_bar_widget = SortableRoundProgressbar()
        progress_bar_widget.setValue(0)
        progress_bar_widget.setAlignment(columns.video_widget_columns['progress_bar']['alignment'])
        self.table_widget.setItem(self.index, col, progress_bar_widget.table_widget_item)
        self.table_widget.setCellWidget(self.index, col, progress_bar_widget)
        if video_metadata.get('offline_filepath'):
            progress_bar_widget.setValue(100)
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

        # for index in range(len(online_data)):
        self.table_widget.setRowHeight(self.index, 48)
        self.set_widget_statuses(video_id, video_downloaded, chat_downloaded)
        CallbackUtils().processEvents()
        self.index += 1

    def _set_resizable_headers(self, table_widget):
        # Todo ...

        for i in range(len(['id', *columns.video_data_columns, *columns.video_widget_columns])):
            table_widget.horizontalHeader().setSectionResizeMode(i, QHeaderView.Interactive)
        return table_widget

    def on_row_select(self, row_index):
        checkbox = self.table_widget.cellWidget(row_index.row(), 0).layout().itemAt(0).widget()
        self.table_widget.scrollToItem(self.table_widget.item(row_index.row(), 0))
        if self.selected_checkbox and self.selected_checkbox != checkbox:
            self.selected_checkbox.setChecked(False)
        self.selected_checkbox = checkbox
        MenuCallbacks().set_menu_statuses()

    def on_click_checkbox(self, checkbox: QCheckBox):
        if self.selected_checkbox and self.selected_checkbox != checkbox:
            self.selected_checkbox.setChecked(False)
        self.selected_checkbox = checkbox
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
        col_index = Columns.get_column_index_by_key(action_item)
        field_index = ActionItems.get_action_item_index(action_item, field)
        self.table_widget.cellWidget(row, col_index).layout().itemAt(field_index).widget().setEnabled(status)

    """
    MISC
    """
    def get_selected_row(self):
        for i in range(self.table_widget.rowCount()):
            if self.table_widget.cellWidget(i, 0).layout().itemAt(0).widget().isChecked():
                return i

    def get_row_from_rfid(self, video_id, is_flipped):
        col = 0     # checkbox
        for i in range(self.table_widget.rowCount()-1, -1, -1):
            if self.table_widget.item(i, col).text() == str(video_id):
                return i
        return None

    def add_video_actions_buttons(self, metadata):
        widget = QWidget()
        widget.setContentsMargins(0, 0, 0, 0)
        widget_layout = WidgetCreator.get_layout_widget(widget)
        widget_layout.setAlignment(columns.video_widget_columns.get('video_actions')['alignment'])

        # make the widget searchable based on button states.
        download_video_state = None
        play_video_state = None
        download_chats_state = None

        is_authenticated = self.impartus.is_authenticated()

        is_flipped = False if metadata.get('ttid') else True
        rf_id = metadata.get('fcid') if is_flipped else metadata.get('ttid')

        for pushbutton in WidgetCreator.add_actions_buttons(ActionItems.video_actions):
            widget_layout.addWidget(pushbutton)

            # disable download button, if video exists locally.
            if pushbutton.objectName() == ActionItems.video_actions['download_video']['text']:
                pushbutton.clicked.connect(partial(self.callbacks['download_video'], rf_id, is_flipped))

                if metadata.get('offline_filepath'):
                    download_video_state = False
                else:
                    if is_authenticated:
                        download_video_state = True
                    else:
                        download_video_state = False

                pushbutton.setEnabled(download_video_state)
            elif pushbutton.objectName() == ActionItems.video_actions['play_video']['text']:
                pushbutton.clicked.connect(partial(self.callbacks['play_video'], rf_id))

                if metadata.get('offline_filepath'):
                    # enable play button, if video exists locally.
                    play_video_state = True
                else:
                    play_video_state = False

                pushbutton.setEnabled(play_video_state)
            elif pushbutton.objectName() == ActionItems.video_actions['download_chats']['text']:
                pushbutton.clicked.connect(partial(self.callbacks['download_chats'], rf_id))

                # enable download chats button, if lecture chats file does not exist.
                filepath = metadata.get('chats')
                if filepath and os.path.exists(filepath):
                    download_chats_state = False
                else:
                    if is_authenticated:
                        download_chats_state = True
                    else:
                        download_chats_state = False

                pushbutton.setEnabled(download_chats_state)
            elif pushbutton.objectName() == ActionItems.video_actions['open_folder']['text']:
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

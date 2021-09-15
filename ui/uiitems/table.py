import os
from functools import partial

import qtawesome as qta

from PySide2 import QtCore
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox, QWidget

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

    def __init__(self, videos, impartus: Impartus, table: QTableWidget):
        self.signal_connected = False
        self.conf = Config.load(ConfigType.IMPARTUS)
        self.impartus = impartus
        self.videos = videos

        self.readonly_delegate = ReadOnlyDelegate()
        self.write_delegate = WriteDelegate(self.get_data)
        self.logger = ThreadLogger(self.__class__.__name__).logger

        self.table = table
        self.data = dict()
        self.prev_checkbox = None

    def get_data(self):
        return self.data

    def _set_headers(self):
        # header item for checkboxes column (TODO: check if it is possible to add a 'select all' checkbox here.)
        widget = QTableWidgetItem()
        widget.setText('')
        self.table.setHorizontalHeaderItem(0, widget)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)

        # enumerate from 1.
        for index, (key, val) in enumerate(Columns.get_video_columns_dict(), 1):
            widget = QTableWidgetItem()
            widget.setText(val['display_name'])

            # make the column read-only if editable property not set.
            if not val['editable']:
                self.table.setItemDelegateForColumn(index, self.readonly_delegate)
            else:
                widget.setIcon(qta.icon(Icons.TABLE__EDITABLE_COLUMN.value))
                self.table.setItemDelegateForColumn(index, self.write_delegate)

            self.table.horizontalHeader().setSectionResizeMode(index, val['resize_policy'])
            if val['hidden']:
                self.table.setColumnHidden(index, True)
                pass

            self.table.setHorizontalHeaderItem(index, widget)

        self.table.horizontalHeader().setSortIndicatorShown(True)
        return self

    def set_row_content(self, offline_data, online_data_gen=None):
        # if we have generator for fetching online data
        # pick one item at a time, merge it with offline data item if present (that gives you it's offline location,
        # attached slides and chats location etc.
        # Later, add any remaining offline videos (which might have been downloaded from other sources, or
        # the ones that may not be accessible online any more.)
        index = 0
        if online_data_gen:
            while True:
                online_item = next(online_data_gen, None)
                if not online_item:
                    DataUtils.save_metadata(self.data)
                    break
                if online_item.get('ttid'):
                    rf_id = online_item['ttid']
                else:
                    rf_id = online_item['fcid']

                if offline_data.get(rf_id):
                    online_item = DataUtils.merge_items(online_item, offline_data[rf_id])
                    del offline_data[rf_id]
                self.data[rf_id] = online_item
                self.add_row_item(index, online_item)
                index += 1
        for i, (rf_id, offline_item) in enumerate(offline_data.items(), index):
            self.data[rf_id] = offline_item
            self.add_row_item(i, offline_item)

    def add_row_item(self, index, data_item):
        self.table.setRowCount(index + 1)

        # for each row, add a checkbox first.
        container_widget = WidgetCreator.add_checkbox_widget(self.on_click_checkbox)
        self.table.setCellWidget(index, 0, container_widget)

        # enumerate rest of the columns from 1
        for col, (key, val) in enumerate(columns.video_data_columns.items(), 1):
            widget = QTableWidgetItem(str(data_item[key]))
            widget.setTextAlignment(val['alignment'])
            self.table.setItem(index, col, widget)

        # total columns so far...
        col = len(columns.video_data_columns) + 1

        # flipped icon column.

        flipped_col = columns.video_widget_columns['flipped']
        flipped_icon = qta.icon(flipped_col['icon']) if data_item.get('fcid') else QIcon()
        flipped_icon_widget = CustomTableWidgetItem()
        flipped_icon_widget.setIcon(flipped_icon)
        flipped_icon_widget.setTextAlignment(columns.video_widget_columns['flipped']['alignment'])
        int_value = 1 if data_item.get('fcid') else 0
        flipped_icon_widget.setValue(int_value)
        flipped_icon_widget.setToolTip(columns.video_widget_columns['flipped']['menu_tooltip'])

        self.table.setItem(index, col, flipped_icon_widget)
        col += 1

        # progress bar.
        progress_bar_widget = SortableRoundProgressbar()
        progress_bar_widget.setValue(0)
        progress_bar_widget.setAlignment(columns.video_widget_columns['progress_bar']['alignment'])
        self.table.setItem(index, col, progress_bar_widget.table_widget_item)
        self.table.setCellWidget(index, col, progress_bar_widget)
        if data_item.get('offline_filepath'):
            progress_bar_widget.setValue(100)
        col += 1

        video_actions_widget, cell_value = self.add_video_actions_buttons(data_item)
        self.table.setCellWidget(index, col, video_actions_widget)
        self.table.cellWidget(index, col).setContentsMargins(0, 0, 0, 0)

        custom_item = CustomTableWidgetItem()
        custom_item.setValue(cell_value)
        self.table.setItem(index, col, custom_item)

        col += 1

        # hidden columns
        for col_index, (key, val) in enumerate(columns.hidden_columns.items(), col):
            str_value = str(data_item[key]) if data_item.get(key) else ''
            widget = QTableWidgetItem(str_value)
            widget.setTextAlignment(columns.hidden_columns[key]['alignment'])
            self.table.setItem(index, col_index, widget)

        # for index in range(len(online_data)):
        self.table.setRowHeight(index, 48)
        CallbackUtils().processEvents()

    def resizable_headers(self):
        # Todo ...
        for i, (col, item) in enumerate(Columns.get_displayable_video_columns_dict().items(), 1):
            if item.get('initial_size') and item['resize_policy'] != QHeaderView.ResizeMode.Stretch:
                self.table.horizontalHeader().resizeSection(i, item.get('initial_size'))

        for i in range(len(['id', *columns.video_data_columns, *columns.video_widget_columns])):
            self.table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Interactive)

    def on_click_checkbox(self, checkbox: QCheckBox):
        if self.prev_checkbox and self.prev_checkbox != checkbox:
            self.prev_checkbox.setChecked(False)
        self.prev_checkbox = checkbox
        MenuCallbacks().set_menu_statuses()

    def show_hide_column(self, column):
        col_index = None
        for i, col_name in enumerate(Columns.get_displayable_video_columns_dict().items(), 1):
            if col_name == column:
                col_index = i
                break

        if self.table.isColumnHidden(col_index):
            self.table.setColumnHidden(col_index, False)
        else:
            self.table.setColumnHidden(col_index, True)

    def fill_table(self, offline_data, online_data=None):
        # clear does not reset the table size, do it explicitly.
        self.table.setSortingEnabled(False)
        self.table.clear()

        col_count = Columns.get_video_columns_count()
        self.table.setColumnCount(col_count)

        self.prev_checkbox = None

        self._set_headers()

        self.set_row_content(offline_data, online_data)
        self.resizable_headers()
        self.table.setSortingEnabled(True)

        # show most recent lectures first.
        self.table.sortByColumn(
            Columns.get_column_index_by_key('startDate'), QtCore.Qt.SortOrder.DescendingOrder)

    def set_button_state(self, row: int, action_item: str, field: str, status: bool):
        col_index = Columns.get_column_index_by_key(action_item)
        field_index = ActionItems.get_action_item_index(action_item, field)
        self.table.cellWidget(row, col_index).layout().itemAt(field_index).widget().setEnabled(status)

    """
    MISC
    """
    def get_selected_row(self):
        for i in range(self.table.rowCount()):
            if self.table.cellWidget(i, 0).layout().itemAt(0).widget().isChecked():
                return i

    def get_selected_row_rfid(self):
        """
        Return ttid or fcid, whichever applicable, also return a flag 'flipped'=True if it is a flipped lecture.
        """
        row_index = self.get_selected_row()
        if row_index is None:
            return None, False

        ttid_col = Columns.get_column_index_by_key('ttid')
        if ttid_col:
            ttid = self.table.item(row_index, ttid_col).text()
            if ttid:
                return int(ttid), False

        fcid_col = Columns.get_column_index_by_key('fcid')
        if fcid_col:
            fcid = self.table.item(row_index, fcid_col).text()
            if fcid:
                return int(fcid), True

        return None, False

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

        # video actions
        callbacks = {
            'download_video': partial(self.videos.on_click_download_video, rf_id, is_flipped),
            'play_video': partial(self.videos.on_click_play_video, rf_id),
            'download_chats': partial(self.videos.on_click_download_chats, rf_id)
        }

        for pushbutton in WidgetCreator.add_actions_buttons(ActionItems.video_actions):
            widget_layout.addWidget(pushbutton)

            # disable download button, if video exists locally.
            if pushbutton.objectName() == ActionItems.video_actions['download_video']['text']:
                pushbutton.clicked.connect(callbacks['download_video'])

                if metadata.get('offline_filepath'):
                    download_video_state = False
                else:
                    if is_authenticated:
                        download_video_state = True
                    else:
                        download_video_state = False

                pushbutton.setEnabled(download_video_state)
            elif pushbutton.objectName() == ActionItems.video_actions['play_video']['text']:
                pushbutton.clicked.connect(callbacks['play_video'])

                if metadata.get('offline_filepath'):
                    # enable play button, if video exists locally.
                    play_video_state = True
                else:
                    play_video_state = False

                pushbutton.setEnabled(play_video_state)
            elif pushbutton.objectName() == ActionItems.video_actions['download_chats']['text']:
                pushbutton.clicked.connect(callbacks['download_chats'])

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

        # a slightly hackish way to sort widgets -
        # create an integer out of the (button1_state, button2_state, ...)
        # pass it to a Custom TableWidgetItem with __lt__ overridden to provide numeric sort.
        cell_value = '{}{}{}'.format(int(download_video_state), int(play_video_state), int(download_chats_state))
        return widget, int(cell_value)

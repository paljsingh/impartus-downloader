import os
import platform
import shutil
from functools import partial
from typing import Dict
import concurrent.futures
from threading import Event

import qtawesome as qta

from PySide2 import QtCore
from PySide2.QtCore import QThread
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QCheckBox

from lib.captions import Captions
from lib.config import Config, ConfigType
from lib.impartus import Impartus
from lib.threadlogging import ThreadLogger
from lib.utils import Utils
from ui.common import Common
from ui.customwidgets.tablewidgetitem import CustomTableWidgetItem
from ui.data.Icons import Icons
from ui.data.actionitems import ActionItems
from ui.data.callbacks import Callbacks
from ui.data.columns import Columns
from lib.variables import Variables
from ui.progressbar import SortableRoundProgressbar
from ui.customwidgets.pushbutton import CustomPushButton
from ui.rodelegate import ReadOnlyDelegate
from ui.slides import Slides
from ui.videos import Videos
from ui.worker import Worker
from ui.writedelegate import WriteDelegate


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

    def __init__(self, impartus: Impartus, table: QTableWidget):
        self.signal_connected = False
        self.workers = dict()
        self.conf = Config.load(ConfigType.IMPARTUS)
        self.impartus = impartus

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
        for index, (key, val) in enumerate(
                [*Columns.data_columns.items(), *Columns.widget_columns.items(), *Columns.hidden_columns.items()], 1):
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
                    self.save_metadata(self.data)
                    break
                if online_item.get('ttid'):
                    rf_id = online_item['ttid']
                    is_flipped = False
                else:
                    rf_id = online_item['fcid']
                    is_flipped = True

                if offline_data.get(rf_id):
                    online_item = self.merge_items(online_item, offline_data[rf_id])
                    del offline_data[rf_id]
                self.data[rf_id] = online_item
                self.add_row_item(index, rf_id, online_item, is_flipped)
                index += 1
        for i, (rf_id, offline_item) in enumerate(offline_data.items(), index):
            self.data[rf_id] = offline_item
            self.add_row_item(i, rf_id, offline_item)

    def add_row_item(self, index, rf_id, data_item, is_flipped=False):
        self.table.setRowCount(index + 1)

        # for each row, add a checkbox first.
        container_widget = Common.add_checkbox_widget(self.on_click_checkbox)
        self.table.setCellWidget(index, 0, container_widget)

        # enumerate rest of the columns from 1
        for col, (key, val) in enumerate(Columns.data_columns.items(), 1):
            widget = QTableWidgetItem(str(data_item[key]))
            widget.setTextAlignment(val['alignment'])
            self.table.setItem(index, col, widget)

        # total columns so far...
        col = len(Columns.data_columns) + 1

        # flipped icon column.

        flipped_col = Columns.widget_columns['flipped']
        flipped_icon = qta.icon(flipped_col['icon']) if data_item.get('fcid') else QIcon()
        flipped_icon_widget = CustomTableWidgetItem()
        flipped_icon_widget.setIcon(flipped_icon)
        flipped_icon_widget.setTextAlignment(Columns.widget_columns['flipped']['alignment'])
        int_value = 1 if data_item.get('fcid') else 0
        flipped_icon_widget.setValue(int_value)
        flipped_icon_widget.setToolTip(Columns.widget_columns['flipped']['menu_tooltip'])

        self.table.setItem(index, col, flipped_icon_widget)
        col += 1

        # progress bar.
        progress_bar_widget = SortableRoundProgressbar()
        progress_bar_widget.setValue(0)
        progress_bar_widget.setAlignment(Columns.widget_columns['progress_bar']['alignment'])
        self.table.setItem(index, col, progress_bar_widget.table_widget_item)
        self.table.setCellWidget(index, col, progress_bar_widget)
        if data_item.get('offline_filepath'):
            progress_bar_widget.setValue(100)
        col += 1

        # video actions
        callbacks = {
            'download_video': partial(self.on_click_download_video, rf_id, is_flipped),
            'play_video': partial(self.on_click_play_video, rf_id),
            'download_chats': partial(self.on_click_download_chats, rf_id)
        }
        video_actions_widget, cell_value = Videos.add_video_actions_buttons(data_item, self.impartus, callbacks)
        self.table.setCellWidget(index, col, video_actions_widget)
        self.table.cellWidget(index, col).setContentsMargins(0, 0, 0, 0)

        custom_item = CustomTableWidgetItem()
        custom_item.setValue(cell_value)
        self.table.setItem(index, col, custom_item)

        col += 1

        # slides actions
        callbacks = {
            'download_slides': partial(self.on_click_download_slides, rf_id),
            'open_folder': partial(self.on_click_open_folder, rf_id),
            'attach_slides': partial(self.on_click_attach_slides, rf_id),
        }
        slides_actions_widget, cell_value = Slides.add_slides_actions_buttons(data_item, self.impartus, callbacks)
        self.table.setCellWidget(index, col, slides_actions_widget)

        # numeric sort implemented via a Custom QTableWidgetItem
        custom_item = CustomTableWidgetItem()
        custom_item.setValue(cell_value)
        self.table.setItem(index, col, custom_item)

        col += 1

        # hidden columns
        for col_index, (key, val) in enumerate(Columns.hidden_columns.items(), col):
            str_value = str(data_item[key]) if data_item.get(key) else ''
            widget = QTableWidgetItem(str_value)
            widget.setTextAlignment(Columns.hidden_columns[key]['alignment'])
            self.table.setItem(index, col_index, widget)

        # for index in range(len(online_data)):
        self.table.setRowHeight(index, 48)
        Callbacks().processEvents()

    def resizable_headers(self):
        # Todo ...
        for i, (col, item) in enumerate([*Columns.data_columns.items(), *Columns.widget_columns.items()], 1):
            if item.get('initial_size') and item['resize_policy'] != QHeaderView.ResizeMode.Stretch:
                self.table.horizontalHeader().resizeSection(i, item.get('initial_size'))

        for i in range(len(['id', *Columns.data_columns, *Columns.widget_columns])):
            self.table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Interactive)

    def on_click_checkbox(self, checkbox: QCheckBox):
        if self.prev_checkbox and self.prev_checkbox != checkbox:
            self.prev_checkbox.setChecked(False)
        self.prev_checkbox = checkbox
        Callbacks().set_menu_statuses()

    def show_hide_column(self, column):
        col_index = None
        for i, col_name in enumerate([*Columns.data_columns.keys(), *Columns.widget_columns.keys()], 1):
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

        col_count = Columns.get_columns_count()
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
    VIDEOS
    """

    def pause_resume_button_click(self, download_button: CustomPushButton, pause_event, resume_event):   # noqa
        if pause_event.is_set():
            download_button.setIcon(Icons.VIDEO__PAUSE_DOWNLOAD.value)
            download_button.setToolTip('Pause Download')
            resume_event.set()
            pause_event.clear()
        else:
            download_button.setIcon(Icons.VIDEO__RESUME_DOWNLOAD.value)
            download_button.setToolTip('Resume Download')
            pause_event.set()
            resume_event.clear()

    def progress_callback(self, download_button: CustomPushButton,  # noqa
                          progressbar_widget: SortableRoundProgressbar, value: int):
        progressbar_widget.setValue(value)
        if value == 100:
            # update download button to show 'video under processing'
            download_button.setIcon(Icons.VIDEO__VIDEO_PROCESSING.value, animate=True)
            download_button.setToolTip('Processing Video...')

    def _download_video(self, video_metadata, video_filepath, progressbar_widget: SortableRoundProgressbar,
                        pushbuttons: Dict, pause_ev, resume_ev):

        self.impartus.process_video(
            video_metadata,
            video_filepath,
            pause_ev,
            resume_ev,
            partial(self.progress_callback, pushbuttons['download_video'], progressbar_widget),
            video_quality=Variables().flipped_lecture_quality()
        )

    def on_click_download_video(self, rf_id: int, is_flipped=False):
        """
        callback function for Download button.
        Creates a thread to download the request video.
        """
        row = self.get_row_from_rfid(rf_id, is_flipped)
        video_metadata = self.data[rf_id]
        video_filepath = self.impartus.get_mkv_path(video_metadata)

        # as pause/resume uses the same download button,
        # the event will show up here.
        # pass the earlier saved fields to pause_resume_button_callback.
        if self.workers.get(rf_id):
            pushbutton = self.workers.get(rf_id)['pushbuttons']['download_video']
            pause_ev = self.workers.get(rf_id)['pause_event']
            resume_ev = self.workers.get(rf_id)['resume_event']
            self.pause_resume_button_click(pushbutton, pause_ev, resume_ev)
            return

        # A fresh download reaches here..
        col = Columns.get_column_index_by_key('video_actions')
        dl_field = ActionItems.get_action_item_index('video_actions', 'download_video')
        dl_button = self.table.cellWidget(row, col).layout().itemAt(dl_field).widget()

        pl_field = ActionItems.get_action_item_index('video_actions', 'play_video')
        pl_button = self.table.cellWidget(row, col).layout().itemAt(pl_field).widget()

        cc_field = ActionItems.get_action_item_index('video_actions', 'download_chats')
        cc_button = self.table.cellWidget(row, col).layout().itemAt(cc_field).widget()

        col = Columns.get_column_index_by_key('slides_actions')
        of_field = ActionItems.get_action_item_index('slides_actions', 'open_folder')
        of_button = self.table.cellWidget(row, col).layout().itemAt(of_field).widget()

        pb_col = Columns.get_column_index_by_key('progress_bar')
        progresbar_widget = self.table.cellWidget(row, pb_col)

        pushbuttons = {
            'download_video': dl_button,
            'play_video': pl_button,
            'download_chats': cc_button,
            'open_folder': of_button,
        }
        pause_event = Event()
        resume_event = Event()

        thread = Worker()
        thread.set_task(partial(self._download_video, video_metadata, video_filepath, progresbar_widget, pushbuttons,
                                pause_event, resume_event))
        thread.finished.connect(partial(self.thread_finished, pushbuttons))

        # we don't want to enable user to start another thread while this one is going on.
        pushbuttons['download_video'].setIcon(Icons.VIDEO__PAUSE_DOWNLOAD.value)
        pushbuttons['download_video'].setToolTip('Pause Download')

        self.workers[rf_id] = {
            'pause_event': pause_event,
            'resume_event': resume_event,
            'pushbuttons': pushbuttons,
            'thread':   thread,
        }
        thread.start(priority=QThread.Priority.IdlePriority)
        self.data[rf_id]['offline_filepath'] = video_filepath

    def thread_finished(self, pushbuttons):     # noqa
        pushbuttons['download_video'].setIcon(Icons.VIDEO__DOWNLOAD_VIDEO.value)
        pushbuttons['download_video'].setToolTip('Download Video')
        pushbuttons['download_video'].setEnabled(False)
        pushbuttons['open_folder'].setEnabled(True)
        pushbuttons['play_video'].setEnabled(True)

    def on_click_play_video(self, rf_id: int):
        video_file = self.data[rf_id]['offline_filepath']
        if video_file:
            Utils.open_file(video_file)

    def on_click_download_chats(self, rf_id: int):
        row = self.get_row_from_rfid(rf_id)
        col = Columns.get_column_index_by_key('video_actions')
        dc_field = ActionItems.get_action_item_index('video_actions', 'download_chats')
        dc_button = self.table.cellWidget(row, col).layout().itemAt(dc_field).widget()

        col = Columns.get_column_index_by_key('slides_actions')
        of_field = ActionItems.get_action_item_index('slides_actions', 'open_folder')
        of_button = self.table.cellWidget(row, col).layout().itemAt(of_field).widget()

        dc_button.setEnabled(False)
        chat_msgs = self.impartus.get_chats(self.data[rf_id])
        captions_path = self.impartus.get_captions_path(self.data[rf_id])
        status = Captions.save_as_captions(rf_id, self.data.get(rf_id), chat_msgs, captions_path)

        # also update local copy of data
        self.data[rf_id]['captions_path'] = captions_path

        # set chat button false
        if not status:
            dc_button.setEnabled(True)
        else:
            dc_button.setEnabled(False)
            of_button.setEnabled(True)

    """
    Slides.
    """

    def _download_slides(self, rf_id: int, slide_url: str, filepath: str):
        """
        Download a slide doc in a thread. Update the UI upon completion.
        """
        # create a new Impartus session reusing existing token.
        imp = Impartus(self.impartus.token)
        if imp.download_slides(rf_id, slide_url, filepath):
            return True
        else:
            # self.log_window.logger.error('Error', 'Error downloading slides.')
            return False

    def on_click_download_slides(self, rf_id: int):  # noqa
        """
        callback function for Download button.
        Creates a thread to download the request video.
        """
        metadata = self.data.get(rf_id)
        slide_url = metadata.get('slide_url')
        filepath = self.impartus.get_slides_path(metadata)

        row = self.get_row_from_rfid(rf_id)
        col = Columns.get_column_index_by_key('slides_actions')
        ds_field = ActionItems.get_action_item_index('slides_actions', 'download_slides')
        ds_button = self.table.cellWidget(row, col).layout().itemAt(ds_field).widget()

        of_field = ActionItems.get_action_item_index('slides_actions', 'open_folder')
        of_button = self.table.cellWidget(row, col).layout().itemAt(of_field).widget()

        ss_field = ActionItems.get_action_item_index('slides_actions', 'show_slides')
        ss_combo = self.table.cellWidget(row, col).layout().itemAt(ss_field).widget()

        widgets = {
            'download_slides': ds_button,
            'open_folder': of_button,
            'show_slides': ss_combo,
        }
        ds_button.setEnabled(False)
        with concurrent.futures.ThreadPoolExecutor(3) as executor:
            future = executor.submit(self._download_slides, rf_id, slide_url, filepath)
            return_value = future.result()

            if return_value:
                widgets['show_slides'].add_items([filepath])
            else:
                widgets['download_slides'].setEnabled(True)

    def on_click_open_folder(self, rf_id: int):     # noqa
        folder_path = self.get_folder_from_rfid(rf_id)
        Utils.open_file(folder_path)

    def on_click_attach_slides(self, rf_id: int):       # noqa
        folder_path = self.get_folder_from_rfid(rf_id)
        conf = Config.load(ConfigType.IMPARTUS)
        filters = ['{} files (*.{})'.format(str(x).title(), x) for x in conf.get('allowed_ext')]
        filters_str = ';;'.join(filters)
        filepaths = QFileDialog().getOpenFileNames(
            None,
            caption="Select files to attach...",
            dir=folder_path,
            filter=filters_str
        )
        if not filepaths:
            return

        row = self.get_row_from_rfid(rf_id)
        col = Columns.get_column_index_by_key('slides_actions')
        ss_field = ActionItems.get_action_item_index('slides_actions', 'show_slides')
        ss_combobox = self.table.cellWidget(row, col).layout().itemAt(ss_field).widget()

        for filepath in filepaths[0]:
            dest_path = shutil.copy(filepath, folder_path)
            ss_combobox.add_items([dest_path])

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

    def get_row_from_rfid(self, rf_id: int, flipped=False):
        if flipped:
            fcid_col_index = Columns.get_column_index_by_key('fcid')
            for i in range(self.table.rowCount()):
                if int(self.table.item(i, fcid_col_index).text()) == rf_id:
                    return i
        else:
            ttid_col_index = Columns.get_column_index_by_key('ttid')
            for i in range(self.table.rowCount()):
                if int(self.table.item(i, ttid_col_index).text()) == rf_id:
                    return i

    def get_folder_from_rfid(self, rf_id: int):
        video_path = self.data.get(rf_id)['offline_filepath'] if self.data.get(rf_id).get('offline_filepath') else None
        if video_path:
            return os.path.dirname(video_path)
        slides_path = self.data.get(rf_id)['backpack_slides'][0]\
            if self.data.get(rf_id).get('backpack_slides') else None
        if slides_path:
            return os.path.dirname(slides_path)
        captions_path = self.data.get(rf_id)['captions_path'] if self.data.get(rf_id).get('captions_path') else None
        if captions_path:
            return os.path.dirname(captions_path)

    def merge_items(self, offline_item, online_item):   # noqa
        for key, val in offline_item.items():
            if not online_item.get(key):
                online_item[key] = offline_item[key]
        return online_item

    def save_metadata(self, online_data):   # noqa
        conf = Config.load(ConfigType.IMPARTUS)
        if conf.get('config_dir') and conf.get('config_dir').get(platform.system()) \
                and conf.get('save_offline_lecture_metadata'):
            folder = conf['config_dir'][platform.system()]
            os.makedirs(folder, exist_ok=True)
            for ttid, item in online_data.items():
                filepath = os.path.join(folder, '{}.json'.format(ttid))
                if not os.path.exists(filepath):
                    Utils.save_json(item, filepath)

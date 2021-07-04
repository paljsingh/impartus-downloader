import logging
import os
import shutil
import threading
from functools import partial
from typing import Dict
import concurrent.futures
from threading import Event

import qtawesome as qta

from PySide2 import QtCore, QtWidgets
from PySide2.QtWidgets import QTableWidget, QAbstractScrollArea, QTableWidgetItem, QHeaderView, QFileDialog, \
    QAbstractItemView, QCheckBox

from lib.captions import Captions
from lib.config import Config, ConfigType
from lib.impartus import Impartus
from lib.utils import Utils
from ui.common import Common
from ui.customwidgets.tablewidgetitem import CustomTableWidgetItem
from ui.data.Icons import Icons
from ui.data.actionitems import ActionItems
from ui.data.callbacks import Callbacks
from ui.data.columns import Columns
from ui.progressbar import SortableRoundProgressbar
from ui.customwidgets.pushbutton import CustomPushButton
from ui.rodelegate import ReadOnlyDelegate
from ui.slides import Slides
from ui.videos import Videos
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

    def __init__(self, impartus: Impartus):
        self.threads = dict()
        self.conf = Config.load(ConfigType.IMPARTUS)
        self.impartus = impartus
        self.table = None
        self.data = None
        self.prev_checkbox = None

        self.readonly_delegate = ReadOnlyDelegate()
        self.write_delegate = WriteDelegate(self.get_data)

    def get_data(self):
        return self.data

    def add_table(self):    # noqa
        table = QTableWidget()

        table.setAlternatingRowColors(True)
        table.setContentsMargins(5, 0, 5, 0)
        table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)

        # disable multiple selection
        table.setSelectionMode(QAbstractItemView.SingleSelection)

        screen_width = QtWidgets.QApplication.primaryScreen().size().width()
        buffer = 70     # includes the window borders, vertical scrollbar, padding, row number field...
        table.viewport().setMaximumWidth(screen_width - buffer)
        self.table = table
        return table

    def _set_size(self, row_count: int, col_count: int):
        self.table.setColumnCount(col_count)
        self.table.setRowCount(row_count)

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

            # disable sorting for some columns.
            if not val['sortable']:
                # TODO -
                pass

            self.table.horizontalHeader().setSectionResizeMode(index, val['resize_policy'])
            if val['hidden']:
                self.table.setColumnHidden(index, True)
                pass

            self.table.setHorizontalHeaderItem(index, widget)

        self.table.horizontalHeader().setSortIndicatorShown(True)
        return self

    def set_row_content(self, data: Dict):
        self.data = data
        for index, (ttid, item) in enumerate(data.items()):
            # for each row, add a checkbox first.
            container_widget = Common.add_checkbox_widget(self.on_click_checkbox)
            self.table.setCellWidget(index, 0, container_widget)

            # enumerate rest of the columns from 1
            for col, (key, val) in enumerate(Columns.data_columns.items(), 1):
                widget = QTableWidgetItem(str(item.get(key)))
                widget.setTextAlignment(val['alignment'])
                self.table.setItem(index, col, widget)

            # total columns so far...
            col = len(Columns.data_columns) + 1

            # progress bar.
            progress_bar_widget = SortableRoundProgressbar()
            progress_bar_widget.setValue(0)
            progress_bar_widget.setAlignment(Columns.widget_columns['progress_bar']['alignment'])
            self.table.setItem(index, col, progress_bar_widget.table_widget_item)
            self.table.setCellWidget(index, col, progress_bar_widget)
            if item.get('offline_filepath'):
                progress_bar_widget.setValue(100)
            col += 1

            # video actions
            callbacks = {
                'download_video': partial(self.on_click_download_video, ttid),
                'play_video': partial(self.on_click_play_video, ttid),
                'download_chats': partial(self.on_click_download_chats, ttid)
            }
            video_actions_widget, cell_value = Videos.add_video_actions_buttons(item, self.impartus, callbacks)
            self.table.setCellWidget(index, col, video_actions_widget)
            self.table.cellWidget(index, col).setContentsMargins(0, 0, 0, 0)

            custom_item = CustomTableWidgetItem()
            custom_item.setValue(cell_value)
            self.table.setItem(index, col, custom_item)

            col += 1

            # slides actions
            callbacks = {
                'download_slides': partial(self.on_click_download_slides, ttid),
                'open_folder': partial(self.on_click_open_folder, ttid),
                'attach_slides': partial(self.on_click_attach_slides, ttid),
            }
            slides_actions_widget, cell_value = Slides.add_slides_actions_buttons(item, self.impartus, callbacks)
            self.table.setCellWidget(index, col, slides_actions_widget)

            # numeric sort implemented via a Custom QTableWidgetItem
            custom_item = CustomTableWidgetItem()
            custom_item.setValue(cell_value)
            self.table.setItem(index, col, custom_item)

            col += 1

            # hidden columns
            for col_index, (key, val) in enumerate(Columns.hidden_columns.items(), col):
                widget = QTableWidgetItem(str(item[key]))
                widget.setTextAlignment(Columns.hidden_columns[key]['alignment'])
                self.table.setItem(index, col_index, widget)

        for index in range(len(data)):
            self.table.setRowHeight(index, 48)
        return self

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

    def fill_table(self, data):
        # clear does not reset the table size, do it explicitly.
        self.table.setSortingEnabled(False)
        self.table.clear()
        self._set_size(0, 0)

        self.prev_checkbox = None

        col_count = Columns.get_columns_count()
        row_count = len(data)

        self._set_size(row_count, col_count)
        self._set_headers()

        self.set_row_content(data)
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
        pushbuttons['download_video'].setIcon(Icons.VIDEO__PAUSE_DOWNLOAD.value)
        pushbuttons['download_video'].setToolTip('Pause Download')

        self.impartus.process_video(
            video_metadata,
            video_filepath,
            pause_ev,
            resume_ev,
            partial(self.progress_callback, pushbuttons['download_video'], progressbar_widget),
            video_quality='highest'
        )
        pushbuttons['download_video'].setIcon(Icons.VIDEO__DOWNLOAD_VIDEO.value)
        pushbuttons['download_video'].setToolTip('Download Video')
        pushbuttons['download_video'].setEnabled(False)
        pushbuttons['open_folder'].setEnabled(True)
        pushbuttons['play_video'].setEnabled(True)

    def on_click_download_video(self, ttid: int):
        """
        callback function for Download button.
        Creates a thread to download the request video.
        """
        row = self.get_row_from_ttid(ttid)
        video_metadata = self.data[ttid]
        video_filepath = self.impartus.get_mkv_path(video_metadata)

        # as pause/resume uses the same download button,
        # the event will show up here.
        # pass the earlier saved fields to pause_resume_button_callback.
        if self.threads.get(ttid):
            pushbutton = self.threads.get(ttid)['pushbuttons']['download_video']
            pause_ev = self.threads.get(ttid)['pause_event']
            resume_ev = self.threads.get(ttid)['resume_event']
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

        # note: args is a tuple.
        thread = threading.Thread(
            target=self._download_video,
            args=(video_metadata, video_filepath, progresbar_widget, pushbuttons,
                  pause_event, resume_event,)
        )
        self.threads[ttid] = {
            'pause_event': pause_event,
            'resume_event': resume_event,
            'pushbuttons': pushbuttons,
        }
        thread.start()
        self.data[ttid]['offline_filepath'] = video_filepath

    def on_click_play_video(self, ttid):
        video_file = self.data[ttid]['offline_filepath']
        if video_file:
            Utils.open_file(video_file)

    def on_click_download_chats(self, ttid):
        row = self.get_row_from_ttid(ttid)
        col = Columns.get_column_index_by_key('video_actions')
        dc_field = ActionItems.get_action_item_index('video_actions', 'download_chats')
        dc_button = self.table.cellWidget(row, col).layout().itemAt(dc_field).widget()

        col = Columns.get_column_index_by_key('slides_actions')
        of_field = ActionItems.get_action_item_index('slides_actions', 'open_folder')
        of_button = self.table.cellWidget(row, col).layout().itemAt(of_field).widget()

        dc_button.setEnabled(False)
        chat_msgs = self.impartus.get_chats(self.data[ttid])
        captions_path = self.impartus.get_captions_path(self.data[ttid])
        status = Captions.save_as_captions(self.data.get(ttid), chat_msgs, captions_path)

        # also update local copy of data
        self.data[ttid]['captions_path'] = captions_path

        # set chat button false
        if not status:
            dc_button.setEnabled(True)
        else:
            dc_button.setEnabled(False)
            of_button.setEnabled(True)

    """
    Slides.
    """

    def _download_slides(self, ttid, slide_url, filepath):
        """
        Download a slide doc in a thread. Update the UI upon completion.
        """
        # create a new Impartus session reusing existing token.
        imp = Impartus(self.impartus.token)
        if imp.download_slides(ttid, slide_url, filepath):
            return True
        else:
            logger = logging.getLogger(self.__class__.__name__)
            logger.error('Error', 'Error downloading slides, see console logs for details.')
            return False

    def on_click_download_slides(self, ttid):  # noqa
        """
        callback function for Download button.
        Creates a thread to download the request video.
        """
        metadata = self.data.get(ttid)
        slide_url = metadata.get('slide_url')
        filepath = self.impartus.get_slides_path(metadata)

        row = self.get_row_from_ttid(ttid)
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
            future = executor.submit(self._download_slides, ttid, slide_url, filepath)
            return_value = future.result()

            if return_value:
                widgets['show_slides'].add_items([filepath])
            else:
                widgets['download_slides'].setEnabled(True)

    def on_click_open_folder(self, ttid):     # noqa
        folder_path = self.get_folder_from_ttid(ttid)
        Utils.open_file(folder_path)

    def on_click_attach_slides(self, ttid):       # noqa
        folder_path = self.get_folder_from_ttid(ttid)
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

        row = self.get_row_from_ttid(ttid)
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

    def get_ttid_col(self):      # noqa
        for i, key in enumerate(Columns.hidden_columns.keys(),
                                1 + len(Columns.data_columns) + len(Columns.widget_columns)):
            if key == 'ttid':
                return i

    def get_selected_row_ttid(self):
        row_index = self.get_selected_row()
        if row_index is None:
            return

        col = self.get_ttid_col()
        if col:
            return int(self.table.item(row_index, col).text())

    def get_row_from_ttid(self, ttid: int):
        ttid_col_index = self.get_ttid_col()
        for i in range(self.table.rowCount()):
            if int(self.table.item(i, ttid_col_index).text()) == ttid:
                return i

    def get_folder_from_ttid(self, ttid: int):
        video_path = self.data.get(ttid)['offline_filepath'] if self.data.get(ttid).get('offline_filepath') else None
        if video_path:
            return os.path.dirname(video_path)
        slides_path = self.data.get(ttid)['backpack_slides'][0] if self.data.get(ttid).get('backpack_slides') else None
        if slides_path:
            return os.path.dirname(slides_path)
        captions_path = self.data.get(ttid)['captions_path'] if self.data.get(ttid).get('captions_path') else None
        if captions_path:
            return os.path.dirname(captions_path)

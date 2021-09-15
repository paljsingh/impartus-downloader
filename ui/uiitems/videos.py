import os
from functools import partial
from typing import Dict
from threading import Event

from PySide2.QtCore import QThread
from lib.captions import Captions
from lib.threadlogging import ThreadLogger
from lib.utils import Utils
from lib.data.Icons import Icons
from lib.data.actionitems import ActionItems
from lib.data.columns import Columns
from lib.variables import Variables
from ui.uiitems.progressbar import SortableRoundProgressbar
from ui.uiitems.customwidgets.pushbutton import CustomPushButton
from ui.helpers.worker import Worker


class Videos:
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
    def __init__(self, impartus, table):
        self.table = table
        self.impartus = impartus
        self.workers = dict()
        self.logger = ThreadLogger(self.__class__.__name__).logger
        self.data = None

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

        return self.impartus.process_video(
            video_metadata,
            video_filepath,
            pause_ev,
            resume_ev,
            partial(Videos.progress_callback, pushbuttons['download_video'], progressbar_widget),
            video_quality=Variables().flipped_lecture_quality()
        )

    def on_click_download_video(self, rf_id: int, is_flipped=False):
        """
        callback function for Download button.
        Creates a thread to download the request video.
        """
        row = self.get_row_from_rfid(rf_id, is_flipped)
        video_metadata = self.data[rf_id]
        video_filepath = Utils.get_mkv_path(video_metadata)

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

        # col = Columns.get_column_index_by_key('slides_actions')
        # of_field = ActionItems.get_action_item_index('slides_actions', 'open_folder')
        # of_button = self.table.cellWidget(row, col).layout().itemAt(of_field).widget()
        #
        # as_field = ActionItems.get_action_item_index('slides_actions', 'attach_slides')
        # as_button = self.table.cellWidget(row, col).layout().itemAt(as_field).widget()

        pb_col = Columns.get_column_index_by_key('progress_bar')
        progresbar_widget = self.table.cellWidget(row, pb_col)

        pushbuttons = {
            'download_video': dl_button,
            'play_video': pl_button,
            'download_chats': cc_button,
            # 'open_folder': of_button,
            # 'attach_slides': as_button,
        }
        pause_event = Event()
        resume_event = Event()

        thread = Worker()
        thread.set_task(partial(self._download_video, video_metadata, video_filepath, progresbar_widget, pushbuttons,
                                pause_event, resume_event))
        thread.finished.connect(partial(self.thread_finished, pushbuttons, rf_id))

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

    def thread_finished(self, pushbuttons, rf_id):     # noqa

        if self.workers.get(rf_id):
            # successful run.
            if self.workers[rf_id]['thread'].status:
                pushbuttons['download_video'].setIcon(Icons.VIDEO__DOWNLOAD_VIDEO.value)
                pushbuttons['download_video'].setToolTip('Download Video')
                pushbuttons['download_video'].setEnabled(False)
                pushbuttons['open_folder'].setEnabled(True)
                pushbuttons['play_video'].setEnabled(True)
                # pushbuttons['attach_slides'].setEnabled(True)
            else:
                try:
                    pushbuttons['download_video'].setEnabled(True)
                except RuntimeError as ex:
                    self.logger.error("Error in downloading video: {}".format(ex))
                    pass
            del self.workers[rf_id]

    def on_click_play_video(self, rf_id: int):
        video_file = self.data[rf_id]['offline_filepath']
        if video_file:
            Utils.open_file(video_file)

    def on_click_download_chats(self, rf_id: int):
        row = self.get_row_from_rfid(rf_id)
        col = Columns.get_column_index_by_key('video_actions')
        dc_field = ActionItems.get_action_item_index('video_actions', 'download_chats')
        dc_button = self.table.cellWidget(row, col).layout().itemAt(dc_field).widget()

        # col = Columns.get_column_index_by_key('slides_actions')
        # of_field = ActionItems.get_action_item_index('slides_actions', 'open_folder')
        # of_button = self.table.cellWidget(row, col).layout().itemAt(of_field).widget()
        #
        # as_field = ActionItems.get_action_item_index('slides_actions', 'attach_slides')
        # as_button = self.table.cellWidget(row, col).layout().itemAt(as_field).widget()

        dc_button.setEnabled(False)
        chat_msgs = self.impartus.get_chats(self.data[rf_id])
        captions_path = Utils.get_captions_path(self.data[rf_id])
        status = Captions.save_as_captions(rf_id, self.data.get(rf_id), chat_msgs, captions_path)

        # also update local copy of data
        self.data[rf_id]['captions_path'] = captions_path

        # set chat button false
        if not status:
            dc_button.setEnabled(True)
        else:
            dc_button.setEnabled(False)
            # of_button.setEnabled(True)
            # as_button.setEnabled(True)

    """
    MISC
    """
    @staticmethod
    def get_selected_row(table):
        for i in range(table.rowCount()):
            if table.cellWidget(i, 0).layout().itemAt(0).widget().isChecked():
                return i

    def get_selected_row_rfid(self):
        """
        Return ttid or fcid, whichever applicable, also return a flag 'flipped'=True if it is a flipped lecture.
        """
        row_index = self.get_selected_row(self.table)
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

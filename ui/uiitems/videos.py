import os
from datetime import datetime
from functools import partial
from typing import Tuple
from threading import Event

from PySide2.QtCore import QThread
from PySide2.QtWidgets import QTableWidget

from lib.captions import Captions
from lib.core.impartus import Impartus
from lib.threadlogging import ThreadLogger
from lib.utils import Utils
from lib.data.Icons import Icons
from lib.variables import Variables
from ui.uiitems.progressbar import SortableRoundProgressbar
from ui.uiitems.customwidgets.pushbutton import CustomPushButton
from ui.helpers.worker import Worker
from ui.uiitems.table import Table


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
    def __init__(self, table: QTableWidget, impartus: Impartus):
        self.impartus = impartus

        # video actions
        callbacks = {
            'download_video': partial(self.on_click_download_video),
            'play_video': partial(self.on_click_play_video),
            'download_chats': partial(self.on_click_download_chats),
            'open_folder': partial(self.on_click_open_folder),
        }
        self.table = Table(table, self.impartus, callbacks)
        self.workers = dict()
        self.logger = ThreadLogger(self.__class__.__name__).logger

    def reset_content(self):
        self.table.reset_content()

    def pause_resume_button_click(self, pushbuttons: Tuple, pause_event, resume_event):   # noqa
        download_button = pushbuttons[0]
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

    @staticmethod
    def progress_callback(download_button: CustomPushButton, progressbar_widget: SortableRoundProgressbar, value: int):
        progressbar_widget.setValue(value, int(datetime.utcnow().timestamp()))
        if value == 100:
            # update download button to show 'video under processing'
            download_button.setIcon(Icons.VIDEO__VIDEO_PROCESSING.value, animate=True)
            download_button.setToolTip('Processing Video...')

    def _download_video(self, video_metadata, video_filepath, progressbar_widget: SortableRoundProgressbar,
                        pushbuttons: Tuple, pause_ev, resume_ev):

        dl_button = pushbuttons[0]
        return self.impartus.process_video(
            video_metadata,
            video_filepath,
            pause_ev,
            resume_ev,
            partial(Videos.progress_callback, dl_button, progressbar_widget),
            video_quality=Variables().flipped_lecture_quality()
        )

    def on_click_download_video(self, video_id):
        """
        callback function for Download button.
        Creates a thread to download the request video.
        """
        video_metadata = self.table.video_ids[video_id]['metadata']
        video_filepath = Utils.get_mkv_path(video_metadata)

        # as pause/resume uses the same download button,
        # the event will show up here.
        # pass the earlier saved fields to pause_resume_button_callback.
        if self.workers.get(video_id):
            pushbuttons = self.workers.get(video_id)['pushbuttons']
            pause_ev = self.workers.get(video_id)['pause_event']
            resume_ev = self.workers.get(video_id)['resume_event']
            self.pause_resume_button_click(pushbuttons, pause_ev, resume_ev)
            return

        # A fresh download reaches here..
        progressbar, pushbuttons = self.table.get_widgets(video_id)
        dl_button, pl_button, cc_button, of_button, = pushbuttons

        pause_event = Event()
        resume_event = Event()

        thread = Worker()
        thread.set_task(partial(self._download_video, video_metadata, video_filepath, progressbar, pushbuttons,
                                pause_event, resume_event))
        thread.finished.connect(partial(self.thread_finished, pushbuttons, video_id))

        # we don't want to enable user to start another thread while this one is going on.
        dl_button.setIcon(Icons.VIDEO__PAUSE_DOWNLOAD.value)
        dl_button.setToolTip('Pause Download')

        self.workers[video_id] = {
            'pause_event': pause_event,
            'resume_event': resume_event,
            'pushbuttons': pushbuttons,
            'thread':   thread,
        }
        thread.start(priority=QThread.Priority.IdlePriority)
        self.table.video_ids[video_id]['metadata']['offline_filepath'] = video_filepath

    def thread_finished(self, pushbuttons, video_id):     # noqa

        if self.workers.get(video_id):
            # successful run.
            dl_button, pl_button, cc_button, of_button, = pushbuttons
            if self.workers[video_id]['thread'].status:
                dl_button.setIcon(Icons.VIDEO__DOWNLOAD_VIDEO.value)
                dl_button.setToolTip('Download Video')
                dl_button.setEnabled(False)
                pl_button.setEnabled(True)
                of_button.setEnabled(True)
            else:
                try:
                    dl_button.setEnabled(True)
                    of_button.setEnabled(False)
                except RuntimeError as ex:
                    self.logger.error("Error in downloading video: {}".format(ex))
                    pass
            del self.workers[video_id]

    def on_click_open_folder(self, video_id):
        video_metadata = self.table.video_ids.get(video_id).get('metadata')
        if video_metadata and video_metadata.get('offline_filepath'):
            Utils.open_file(os.path.dirname(video_metadata.get('offline_filepath')))

    def on_click_play_video(self, video_id: int):
        video_metadata = self.table.video_ids.get(video_id).get('metadata')
        if video_metadata and video_metadata.get('offline_filepath'):
            Utils.open_file(video_metadata.get('offline_filepath'))

    def on_click_download_chats(self, video_id: int):
        video_data = self.table.video_ids.get(video_id)
        if video_data and video_data.get('download_chat_button'):
            dc_button = video_data['download_chat_button']
            video_metadata = video_data.get('metadata')
            chat_msgs = self.impartus.get_chats(video_metadata)
            captions_path = Utils.get_captions_path(video_metadata)
            status = Captions.save_as_captions(video_id, video_metadata, chat_msgs, captions_path)

            # also update local copy of data
            video_metadata['captions_path'] = captions_path

            # set chat button false
            if not status:
                dc_button.setEnabled(True)
            else:
                dc_button.setEnabled(False)

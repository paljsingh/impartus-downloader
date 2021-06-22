import os
from functools import partial

from PySide2.QtWidgets import QWidget

from lib.utils import Utils
from qtui.common import Common
from ui.data import ActionItems, ConfigKeys


class Videos:

    @classmethod
    def add_video_actions_buttons(cls, metadata):
        widget = QWidget()
        widget_layout = Common.get_layout_widget(widget)
        for pushbutton in Common.add_actions_buttons(ActionItems.video_actions):
            widget_layout.addWidget(pushbutton)

            # disable download button, if video exists locally.
            if metadata.get('offline_filepath') \
                    and pushbutton.text() == ActionItems.video_actions['download_video']['text']:
                pushbutton.setEnabled(False)
            else:
                pushbutton.setEnabled(True)

            # enable play button, if video exists locally.
            if metadata.get('offline_filepath') \
                    and pushbutton.text() == ActionItems.video_actions['play_video']['text']:
                pushbutton.setEnabled(True)
                pushbutton.clicked.connect(partial(Utils.open_file, metadata['offline_filepath']))
            else:
                pushbutton.setEnabled(False)

            # enable download chats button, if lecture chats file does not exist.
            if pushbutton.text() == ActionItems.video_actions['download_captions']['text']:
                filepath = metadata.get(ConfigKeys.CAPTIONS_PATH.value)
                if filepath and not os.path.exists(filepath):
                    pushbutton.setEnabled(True)
                else:
                    pushbutton.setEnabled(False)

        return widget

import os
from typing import Dict

from PySide2.QtWidgets import QWidget

from ui.common import Common
from ui.data import ActionItems


class Videos:

    @classmethod
    def add_video_actions_buttons(cls, metadata, callbacks: Dict):
        widget = QWidget()
        widget_layout = Common.get_layout_widget(widget)
        for pushbutton in Common.add_actions_buttons(ActionItems.video_actions):
            widget_layout.addWidget(pushbutton)

            # disable download button, if video exists locally.
            if pushbutton.text() == ActionItems.video_actions['download_video']['text']:
                pushbutton.clicked.connect(callbacks['download_video'])

                if metadata.get('offline_filepath'):
                    pushbutton.setEnabled(False)
                else:
                    pushbutton.setEnabled(True)
            elif pushbutton.text() == ActionItems.video_actions['play_video']['text']:
                pushbutton.clicked.connect(callbacks['play_video'])

                if metadata.get('offline_filepath'):
                    # enable play button, if video exists locally.
                    pushbutton.setEnabled(True)
                else:
                    pushbutton.setEnabled(False)
            elif pushbutton.text() == ActionItems.video_actions['download_chats']['text']:
                pushbutton.clicked.connect(callbacks['download_chats'])

                # enable download chats button, if lecture chats file does not exist.
                filepath = metadata.get('chats')
                if filepath and os.path.exists(filepath):
                    pushbutton.setEnabled(False)
                else:
                    pushbutton.setEnabled(True)

        return widget

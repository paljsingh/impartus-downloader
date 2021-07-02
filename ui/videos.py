import os
from functools import partial
from typing import Dict, List

from PySide2.QtCore import QEvent
from PySide2.QtWidgets import QWidget, QTableWidget

from ui.common import Common
from ui.data.actionitems import ActionItems
from ui.data.columns import Columns


class Videos:
    """
    class responsible for creating widgets [download_video, play_video, download_chats] grouped under 'video' header.
    """

    @classmethod
    def add_video_actions_buttons(cls, metadata, callbacks: Dict):
        widget = QWidget()
        widget.setContentsMargins(0,0,0,0)
        widget_layout = Common.get_layout_widget(widget)
        widget_layout.setAlignment(Columns.widget_columns.get('video_actions')['alignment'])

        for pushbutton in Common.add_actions_buttons(ActionItems.video_actions):
            widget_layout.addWidget(pushbutton)

            # disable download button, if video exists locally.
            if pushbutton.objectName() == ActionItems.video_actions['download_video']['text']:
                pushbutton.clicked.connect(callbacks['download_video'])

                if metadata.get('offline_filepath'):
                    pushbutton.setEnabled(False)
                else:
                    pushbutton.setEnabled(True)
            elif pushbutton.objectName() == ActionItems.video_actions['play_video']['text']:
                pushbutton.clicked.connect(callbacks['play_video'])

                if metadata.get('offline_filepath'):
                    # enable play button, if video exists locally.
                    pushbutton.setEnabled(True)
                else:
                    pushbutton.setEnabled(False)
            elif pushbutton.objectName() == ActionItems.video_actions['download_chats']['text']:
                pushbutton.clicked.connect(callbacks['download_chats'])

                # enable download chats button, if lecture chats file does not exist.
                filepath = metadata.get('chats')
                if filepath and os.path.exists(filepath):
                    pushbutton.setEnabled(False)
                else:
                    pushbutton.setEnabled(True)
        return widget

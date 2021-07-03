import os
from typing import Dict

from PySide2.QtWidgets import QWidget

from lib.impartus import Impartus
from ui.common import Common
from ui.data.actionitems import ActionItems
from ui.data.columns import Columns


class Videos:
    """
    class responsible for creating widgets [download_video, play_video, download_chats] grouped under 'video' header.
    """

    @classmethod
    def add_video_actions_buttons(cls, metadata, impartus: Impartus, callbacks: Dict):
        widget = QWidget()
        widget.setContentsMargins(0, 0, 0, 0)
        widget_layout = Common.get_layout_widget(widget)
        widget_layout.setAlignment(Columns.widget_columns.get('video_actions')['alignment'])

        # make the widget searchable based on button states.
        download_video_state = None
        play_video_state = None
        download_chats_state = None

        is_authenticated = impartus.is_authenticated()
        for pushbutton in Common.add_actions_buttons(ActionItems.video_actions):
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

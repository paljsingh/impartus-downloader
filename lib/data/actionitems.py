from PySide2.QtWidgets import QPushButton

from lib.data.Icons import Icons
from lib.data.labels import Labels


class ActionItems:
    """
    Data required for the action items in table.py
    """

    video_actions = {
        'download_video': {
            'tooltip': 'Download Video',
            'text': Icons.VIDEO__DOWNLOAD_VIDEO.value,
            'type': QPushButton,
        },
        'play_video': {
            'tooltip': 'Play Video',
            'text': Icons.VIDEO__PLAY_VIDEO.value,
            'type': QPushButton,
        },
        'download_chats': {
            'tooltip': 'Download Lecture Chats',
            'text': Icons.VIDEO__DOWNLOAD_CAPTIONS.value,
            'type': QPushButton,
        },
        'open_folder': {
            'tooltip': 'Open Video Folder',
            'text': Icons.VIDEO__OPEN_FOLDER.value,
            'type': QPushButton,
        },
    }

    slides_actions = {
        Labels.DOCUMENT__DOWNLOAD_DOCUMENT.value: {
            'tooltip': 'Download Backpack Document',
            'text': Icons.SLIDES__DOWNLOAD_SLIDES.value,
            'type': QPushButton,
            # 'callback': Columns.widget_columns['']
        },
        Labels.DOCUMENT__OPEN_DOCUMENT.value: {
            'tooltip': 'Show Backpack Document',
            'text': Icons.SLIDES__SHOW_SLIDES.value,
            'type': QPushButton,
        },
        Labels.DOCUMENT__OPEN_FOLDER.value: {
            'tooltip': 'Open Folder',
            'text': Icons.VIDEO__OPEN_FOLDER.value,
            'type': QPushButton,
        },
        Labels.DOCUMENT__ATTACH_DOCUMENT.value: {
            'tooltip': 'Attach Slides',
            'text': Icons.SLIDES__ATTACH_SLIDES.value,
            'type': QPushButton,
        },
    }

    @classmethod
    def get_action_item_index(cls, action_item, field):    # noqa
        for i, key in enumerate(getattr(ActionItems, action_item).keys()):
            if key == field:
                return i

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
            'icon': Icons.VIDEO__DOWNLOAD_VIDEO.value,
            'type': QPushButton,
        },
        'play_video': {
            'tooltip': 'Play Video',
            'icon': Icons.VIDEO__PLAY_VIDEO.value,
            'type': QPushButton,
        },
        'download_chats': {
            'tooltip': 'Download Lecture Chats',
            'icon': Icons.VIDEO__DOWNLOAD_CAPTIONS.value,
            'type': QPushButton,
        },
        'open_folder': {
            'tooltip': 'Open Video Folder',
            'icon': Icons.VIDEO__OPEN_FOLDER.value,
            'type': QPushButton,
        },
    }

    slides_actions = {
        Labels.DOCUMENT__DOWNLOAD_DOCUMENT.value: {
            'tooltip': 'Download Backpack Document',
            'icon': Icons.DOCUMENT__DOWNLOAD_SLIDES.value,
            'type': QPushButton,
        },
        Labels.DOCUMENT__OPEN_DOCUMENT.value: {
            'tooltip': 'Show Backpack Document',
            'icon': None,   # infer from extension.
            'type': QPushButton,
        },
        Labels.DOCUMENT__OPEN_FOLDER.value: {
            'tooltip': 'Open Folder',
            'icon': Icons.VIDEO__OPEN_FOLDER.value,
            'type': QPushButton,
        },
        Labels.DOCUMENT__ATTACH_DOCUMENT.value: {
            'tooltip': 'Attach Slides',
            'icon': Icons.DOCUMENT__ATTACH_SLIDES.value,
            'type': QPushButton,
        },
    }

    @classmethod
    def get_action_item_index(cls, action_item, field):    # noqa
        for i, key in enumerate(getattr(ActionItems, action_item).keys()):
            if key == field:
                return i

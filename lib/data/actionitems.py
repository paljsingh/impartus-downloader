from PySide2.QtWidgets import QPushButton, QComboBox

from lib.data.Icons import Icons


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
            'text': Icons.SLIDES__DOWNLOAD_CAPTIONS.value,
            'type': QPushButton,
        },
    }
    slides_actions = {
        'show_slides': {
            'tooltip': 'Show Backpack Slides',
            'text': Icons.SLIDES__DOWNLOAD_SLIDES.value,
            'type': QComboBox,
        },
        'download_slides': {
            'tooltip': 'Download Backpack Slides',
            'text': Icons.SLIDES__DOWNLOAD_SLIDES.value,
            'type': QPushButton,
        },
        'open_folder': {
            'tooltip': 'Open Folder',
            'text': Icons.VIDEO__OPEN_FOLDER.value,
            'type': QPushButton,
        },
        'attach_slides': {
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

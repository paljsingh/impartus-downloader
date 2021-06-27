from PySide2.QtWidgets import QPushButton, QComboBox

from ui.data.Icons import Icons


class ActionItems:
    video_actions = {
        'download_video': {
            'tooltip': '{} Download Video'.format(Icons.DOWNLOAD_VIDEO.value),
            'text': Icons.DOWNLOAD_VIDEO.value,
            'type': QPushButton,
        },
        'play_video': {
            'tooltip': '{} Play Video'.format(Icons.PLAY_VIDEO.value),
            'text': Icons.PLAY_VIDEO.value,
            'type': QPushButton,
        },
        'download_chats': {
            'tooltip': '{} Download Lecture Chats'.format(Icons.DOWNLOAD_CAPTIONS.value),
            'text': Icons.DOWNLOAD_CAPTIONS.value,
            'type': QPushButton,
        },
    }
    slides_actions = {
        'show_slides': {
            'tooltip': '{} Show Backpack Slides'.format(Icons.SHOW_SLIDES.value),
            'text': Icons.DOWNLOAD_SLIDES.value,
            'type': QComboBox,
        },
        'download_slides': {
            'tooltip': '{} Download Backpack Slides'.format(Icons.DOWNLOAD_SLIDES.value),
            'text': Icons.DOWNLOAD_SLIDES.value,
            'type': QPushButton,
        },
        'open_folder': {
            'tooltip': '{} Open Folder'.format(Icons.OPEN_FOLDER.value),
            'text': Icons.OPEN_FOLDER.value,
            'type': QPushButton,
        },
        'attach_slides': {
            'tooltip': '{} Attach Slides'.format(Icons.ATTACH_SLIDES.value),
            'text': Icons.ATTACH_SLIDES.value,
            'type': QPushButton,
        },
    }

    @classmethod
    def get_action_item_index(cls, action_item, field):    # noqa
        for i, key in enumerate(getattr(ActionItems, action_item).keys()):
            if key == field:
                return i


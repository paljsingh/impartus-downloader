import enum

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QHeaderView, QPushButton, QComboBox


class Icons(enum.Enum):

    DOWNLOAD_VIDEO = '⬇'
    PLAY_VIDEO = '▶'
    OPEN_FOLDER = '⏏'
    DOWNLOAD_SLIDES = '⬇'
    DOWNLOAD_CAPTIONS = '㏄'
    SHOW_SLIDES = '▤'
    ATTACH_SLIDES = '📎'
    PAUSE_DOWNLOAD = '❘❘'
    RESUME_DOWNLOAD = '❘❘▶'
    VIDEO_PROCESSING = '⧗'
    VIDEO_DOWNLOADED = '✓'
    VIDEO_NOT_DOWNLOADED = '⃠'
    SLIDES_DOWNLOADED = '▤'
    MOVED_TO = '⇨'

    def __str__(self):
        return str(self.value)


class Labels(enum.Enum):
    RELOAD = '⟳  Reload'
    AUTO_ORGANIZE = '⇄  Auto Organize Lectures'
    COLUMNS = '❘❘❘  Columns'
    FLIPPED_QUALITY = '☇  Flipped Lecture Quality'
    QUIT = 'Quit'
    ACTIONS = 'Actions'
    COLORSCHEME = 'Color Scheme'
    VIEW = 'View'
    VIDEO = 'Video'
    DOCUMENTATION = 'Documentation...'
    CHECK_FOR_UPDATES = 'Check for updates...'
    HELP = 'Help'
    APPLICATION_TITLE = 'Impartus Downloader'
    LOGIN_TITLE = 'Login - Impartus'

    def __str__(self):
        return str(self.value)


class Columns:
    data_columns = {
        'subjectNameShort': {
            'alignment': Qt.AlignLeft,
            'display_name': 'Subject',
            'editable': True,
            'hidden': False,
            'menu_tooltip': 'Subject',
            'original_values_col': 'subjectName',
            'resize_policy': QHeaderView.ResizeMode.ResizeToContents,
            'sortable': True,
            'title_case': False,
        },
        'seqNo': {
            'alignment': Qt.AlignRight,
            'display_name': 'Lecture #',
            'editable': False,
            'hidden': False,
            'menu_tooltip': 'Lecture id',
            'original_values_col': None,
            'resize_policy': QHeaderView.ResizeMode.ResizeToContents,
            'sortable': True,
            'title_case': False,
        },
        'professorName': {
            'alignment': Qt.AlignLeft,
            'display_name': 'Faculty',
            'editable': False,
            'hidden': False,
            'menu_tooltip': 'Faculty Name',
            'original_values_col': None,
            'resize_policy': QHeaderView.ResizeMode.ResizeToContents,
            'sortable': True,
            'title_case': True,
        },
        'topic': {
            'alignment': Qt.AlignLeft,
            'display_name': 'Topic',
            'editable': False,
            'hidden': False,
            'menu_tooltip': 'Lecture Topic',
            'original_values_col': None,
            'resize_policy': QHeaderView.ResizeMode.Stretch,
            'sortable': True,
            'title_case': True,
        },
        'actualDurationReadable': {
            'alignment': Qt.AlignRight,
            'display_name': 'Duration',
            'editable': False,
            'hidden': False,
            'menu_tooltip': 'Lecture Duration',
            'original_values_col': None,
            'resize_policy': QHeaderView.ResizeMode.ResizeToContents,
            'sortable': True,
            'title_case': False,
        },
        'tapNToggle': {
            'alignment': Qt.AlignRight,
            'display_name': 'Tracks',
            'editable': False,
            'hidden': False,
            'menu_tooltip': 'Number of tracks / view',
            'original_values_col': None,
            'resize_policy': QHeaderView.ResizeMode.ResizeToContents,
            'sortable': True,
            'title_case': False,
        },
        'startDate': {
            'alignment': Qt.AlignRight,
            'display_name': 'Date',
            'editable': False,
            'hidden': False,
            'menu_tooltip': 'Lecture Date',
            'original_values_col': None,
            'resize_policy': QHeaderView.ResizeMode.ResizeToContents,
            'sortable': True,
            'title_case': False,
        },
    }

    widget_columns = {
        'progress_bar': {
            'alignment': Qt.AlignCenter,
            'display_name': 'Downloaded?',
            'editable': False,
            'hidden': False,
            'menu_tooltip': 'Download Status',
            'original_values_col': None,
            'resize_policy': QHeaderView.ResizeMode.Fixed,
            'sortable': False,
            'title_case': False,
        },
        'video_actions': {
            'alignment': Qt.AlignCenter,
            'display_name': 'Video',
            'editable': False,
            'hidden': False,
            'menu_tooltip': 'Video Actions',
            'original_values_col': None,
            'resize_policy': QHeaderView.ResizeMode.ResizeToContents,
            'sortable': False,
            'title_case': False,
        },
        'slides_actions': {
            'alignment': Qt.AlignRight,
            'display_name': 'Slides',
            'editable': False,
            'hidden': False,
            'menu_tooltip': 'Slides Actions',
            'original_values_col': None,
            'resize_policy': QHeaderView.ResizeMode.ResizeToContents,
            'sortable': False,
            'title_case': False,
        },
    }

    hidden_columns = {
        'ttid': {
            'alignment': Qt.AlignRight,
            'display_name': 'ttid',
            'editable': False,
            'hidden': True,
            'menu_tooltip': 'ttid',
            'original_values_col': None,
            'resize_policy': QHeaderView.ResizeMode.ResizeToContents,
            'sortable': True,
            'title_case': False,
        },
    }

    @classmethod
    def get_display_columns(cls):
        return [*Columns.data_columns, *Columns.widget_columns]

    @classmethod
    def get_column_index_by_key(cls, key_name):
        return [*Columns.data_columns.keys(), *Columns.widget_columns.keys(), *Columns.hidden_columns.keys()].index(
            key_name) + 1

    @classmethod
    def get_column_index_by_display_name(cls, display_name):
        for index, value in enumerate([*Columns.data_columns.values(), *Columns.widget_columns.values(), *Columns.hidden_columns.values()]):
            if value['display_name'] == display_name:
                return index + 1

    @classmethod
    def get_columns_count(cls):
        return 1 + len(Columns.data_columns) + len(Columns.widget_columns) + len(Columns.hidden_columns)

    @classmethod
    def get_button_order(cls):
        return 1 + len(Columns.data_columns) + len(Columns.widget_columns) + len(Columns.hidden_columns)


class ConfigKeys(enum.Enum):
    URL = 'impartus_url'
    EMAIL = 'login_email'
    PASSWORD = 'password'
    TARGET_DIR = 'target_dir'
    CONFIG_DIR = 'config_dir'
    ALLOWED_EXT = 'allowed_ext'
    VIDEO_PATH = 'video_path'
    SLIDES_PATH = 'slides_path'
    CAPTIONS_PATH = 'captions_path'
    COLORSCHEME_DEFAULT = 'default'
    RESIZE_POLICY = 'resize_policy'

    def __str__(self):
        return str(self.value)


class IconFiles(enum.Enum):

    SORT_UP_ARROW = 'images/sort-up.png'
    SORT_DOWN_ARROW = 'images/sort-down.png'
    EDITABLE_BLUE = 'images/editable-blue.png'
    EDITABLE_RED = 'images/editable-red.png'
    APP_LOGO = 'images/logo.png'

    def __str__(self):
        return str(self.value)


class DocFiles(enum.Enum):

    HELPDOC = 'docs/helpdoc.pdf'

    def __str__(self):
        return str(self.value)


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


class SearchDirection(enum.Enum):
    FORWARD = 1
    BACKWARD = -1



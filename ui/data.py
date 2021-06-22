import enum

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QHeaderView


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
    CAPTIONS_DOWNLOADED = '[㏄]'
    CAPTIONS_NOT_DOWNLOADED = '[㏄ ⬇]'
    CAPTIONS_NOT_AVAILABLE = '[no ㏄]'
    SLIDES_DOWNLOADED = '▤'
    SLIDES_NOT_DOWNLOADED = '[▤ ⬇]'
    SLIDES_NOT_AVAILABLE = '[no ▤]'
    SORT_DESC = '▼'
    SORT_ASC = '▲'
    UNSORTED = '⇅'
    EDITABLE = '✎'
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

    def __str__(self):
        return str(self.value)


class Columns:
    data_columns = {
        'subjectNameShort': {
            'alignment': Qt.AlignLeft,
            'display_name': 'Subject',
            'editable': True,
            'original_values_col': 'subjectName',
            'resize_policy': QHeaderView.ResizeMode.ResizeToContents,
            'sortable': True,
            'title_case': False,
        },
        'seqNo': {
            'alignment': Qt.AlignRight,
            'display_name': 'Lecture #',
            'editable': False,
            'original_values_col': None,
            'resize_policy': QHeaderView.ResizeMode.ResizeToContents,
            'sortable': True,
            'title_case': False,
        },
        'professorName': {
            'alignment': Qt.AlignLeft,
            'display_name': 'Professor',
            'editable': False,
            'original_values_col': None,
            'resize_policy': QHeaderView.ResizeMode.ResizeToContents,
            'sortable': True,
            'title_case': True,
        },
        'topic': {
            'alignment': Qt.AlignLeft,
            'display_name': 'Topic',
            'editable': False,
            'original_values_col': None,
            'resize_policy': QHeaderView.ResizeMode.Stretch,
            'sortable': True,
            'title_case': True,
        },
        'actualDurationReadable': {
            'alignment': Qt.AlignRight,
            'display_name': 'Duration',
            'editable': False,
            'original_values_col': None,
            'resize_policy': QHeaderView.ResizeMode.ResizeToContents,
            'sortable': True,
            'title_case': False,
        },
        'tapNToggle': {
            'alignment': Qt.AlignRight,
            'display_name': 'Tracks',
            'editable': False,
            'original_values_col': None,
            'resize_policy': QHeaderView.ResizeMode.ResizeToContents,
            'sortable': True,
            'title_case': False,
        },
        'startDate': {
            'alignment': Qt.AlignRight,
            'display_name': 'Date',
            'editable': False,
            'original_values_col': None,
            'resize_policy': QHeaderView.ResizeMode.ResizeToContents,
            'sortable': True,
            'title_case': False,
        },
    }

    widget_columns = {
        'progress_bar': {
            'alignment': Qt.AlignCenter,
            'display_name': 'Download %',
            'editable': False,
            'original_values_col': None,
            'resize_policy': QHeaderView.ResizeMode.Fixed,
            'sortable': False,
            'title_case': False,
        },
        'video_actions': {
            'alignment': Qt.AlignCenter,
            'display_name': 'Video',
            'editable': False,
            'original_values_col': None,
            'resize_policy': QHeaderView.ResizeMode.ResizeToContents,
            'sortable': False,
            'title_case': False,
        },
        'slides_actions': {
            'alignment': Qt.AlignRight,
            'display_name': 'Slides',
            'editable': False,
            'original_values_col': None,
            'resize_policy': QHeaderView.ResizeMode.ResizeToContents,
            'sortable': False,
            'title_case': False,
        },
    }
    # progress bar
    progressbar_column = {
        'downloaded': {'display_name': 'Downloaded?', 'title_case': False, 'sortable': True,
                       'editable': False, 'type': 'progressbar'}
    }
    button_columns = {
        'download_video': {'type': 'button', 'editable': False, 'display_name': 'Video',
                           'function': 'download_video', 'text': Icons.DOWNLOAD_VIDEO.value,
                           'state': 'download_video_state'
                           },
        'play_video': {'type': 'button', 'editable': False, 'display_name': 'Video',
                       'function': 'play_video', 'text': Icons.PLAY_VIDEO.value,
                       'state': 'play_video_state'
                       },
        'open_folder': {'type': 'button', 'editable': False, 'display_name': 'Folder',
                        'function': 'open_folder', 'text': Icons.OPEN_FOLDER.value,
                        'state': 'open_folder_state'
                        },
        'download_slides': {'type': 'button', 'editable': False, 'display_name': 'Slides',
                            'function': 'download_slides', 'text': Icons.DOWNLOAD_SLIDES.value,
                            'state': 'download_slides_state'
                            },
        'show_slides': {'type': 'button', 'editable': False, 'display_name': 'Slides',
                        'function': 'show_slides', 'text': Icons.SHOW_SLIDES.value,
                        'state': 'show_slides_state'
                        },
        'attach_slides': {'type': 'button', 'editable': False, 'display_name': 'Slides',
                          'function': 'attach_slides', 'text': Icons.ATTACH_SLIDES.value,
                          'state': 'attach_slides_state'
                          },
    }

    button_state_columns = {k: {'display_name': k, 'type': 'button_state'} for k in [
        'download_video_state',
        'play_video_state',
        'open_folder_state',
        'download_slides_state',
        'show_slides_state',
        'attach_slides_state',
    ]}

    # index
    index_column = {'index': {'display_name': 'index', 'type': 'auto'}}
    metadata_column = {'metadata': {'display_name': 'metadata', 'type': 'metadata'}}

    # video / slides data
    orig_value_columns = {k: {'display_name': k, 'type': 'original_value'} for k in [
        'subjectName',
    ]}

    display_columns = {**data_columns, **progressbar_column, **button_columns}
    all_columns = {**data_columns, **progressbar_column, **button_columns,
                   **button_state_columns, **orig_value_columns, **index_column,
                   **metadata_column}
    column_names = [k for k in all_columns.keys()]
    headers = [v['display_name'] for v in data_columns.values()]


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


class ActionItems:
    video_actions = {
        'download_video': {
            'tooltip': '{} Download Video'.format(Icons.DOWNLOAD_VIDEO.value),
            'text': Icons.DOWNLOAD_VIDEO.value,
        },
        'play_video': {
            'tooltip': '{} Play Video'.format(Icons.PLAY_VIDEO.value),
            'text': Icons.PLAY_VIDEO.value,
        },
        'download_captions': {
            'tooltip': '{} Download Lecture Chats'.format(Icons.DOWNLOAD_CAPTIONS.value),
            'text': Icons.DOWNLOAD_CAPTIONS.value,
        },
    }
    slides_actions = {
        'download_slides': {
            'tooltip': '{} Download Backpack Slides'.format(Icons.DOWNLOAD_SLIDES.value),
            'text': Icons.DOWNLOAD_SLIDES.value,
        },
        'open_folder': {
            'tooltip': '{} Open Folder'.format(Icons.OPEN_FOLDER.value),
            'text': Icons.OPEN_FOLDER.value,
        },
        'attach_slides': {
            'tooltip': '{} Attach Slides'.format(Icons.ATTACH_SLIDES.value),
            'text': Icons.ATTACH_SLIDES.value,
        },
    }


class SearchDirection(enum.Enum):
    FORWARD = 1
    BACKWARD = -1


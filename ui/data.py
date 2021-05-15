import enum


class Icons(enum.Enum):

    DOWNLOAD_VIDEO = '⬇'
    PLAY_VIDEO = '▶'
    OPEN_FOLDER = '⏏'
    DOWNLOAD_SLIDES = '⬇'
    SHOW_SLIDES = '▤'
    ADD_SLIDES = '📎'
    PAUSE_DOWNLOAD = '❘❘'
    RESUME_DOWNLOAD = '❘❘▶'
    VIDEO_PROCESSING = '⧗'
    VIDEO_DOWNLOADED = '✓'
    VIDEO_NOT_DOWNLOADED = '⃠'
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
    ABOUT = 'About...'
    HELP = 'Help'

    def __str__(self):
        return str(self.value)



class Columns:
    data_columns = {
        'subjectNameShort': {'display_name': 'Subject', 'title_case': False, 'sortable': True, 'editable': True,
                             'original_values_col': 'subjectName', 'type': 'data'},
        'seqNo': {'display_name': 'Lecture #', 'title_case': False, 'sortable': True, 'editable': False,
                  'original_values_col': None, 'type': 'data'},
        'professorName': {'display_name': 'Professor', 'title_case': True, 'sortable': True, 'editable': False,
                          'original_values_col': None, 'type': 'data'},
        'topic': {'display_name': 'Topic', 'title_case': True, 'sortable': True, 'editable': False,
                  'original_values_col': None, 'type': 'data'},
        'actualDurationReadable': {'display_name': 'Duration', 'title_case': False, 'sortable': True,
                                   'editable': False, 'original_values_col': None, 'type': 'data'},
        'tapNToggle': {'display_name': 'Tracks', 'title_case': False, 'sortable': True, 'editable': False,
                       'original_values_col': None, 'type': 'data'},
        'startDate': {'display_name': 'Date', 'title_case': False, 'sortable': True, 'editable': False,
                      'original_values_col': None, 'type': 'data'},
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
        'add_slides': {'type': 'button', 'editable': False, 'display_name': 'Slides',
                       'function': 'add_slides', 'text': Icons.ADD_SLIDES.value,
                       'state': 'add_slides_state'
                       },
    }

    button_state_columns = {k: {'display_name': k, 'type': 'button_state'} for k in [
        'download_video_state',
        'play_video_state',
        'open_folder_state',
        'download_slides_state',
        'show_slides_state',
        'add_slides_state',
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
    headers = [v['display_name'] for v in display_columns.values()]

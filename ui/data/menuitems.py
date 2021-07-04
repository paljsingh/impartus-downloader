import sys
from functools import partial

from lib.config import ConfigType, Config
from lib.utils import Utils
from ui.data.callbacks import Callbacks
from ui.data.columns import Columns


class MenuItems:
    """
    declarative styled menu items.
    """

    conf = Config.load(ConfigType.IMPARTUS)
    menu_items = {
        'Actions': {
            'Login': {
                'shortcut': 'Ctrl+L',
                'status_tip': 'Login to Impartus',
                'callback': Callbacks().on_login_click,
            },
            'Reload': {
                'shortcut': 'Ctrl+R',
                'status_tip': 'Reload Table Content',
                'callback': Callbacks().on_reload_click,
            },
            'Auto Organize': {
                'shortcut': 'Ctrl+/',
                'status_tip': 'Rename lecture videos, download missing captions...',
                'callback': Callbacks().on_auto_organize_click,
            },
            'sep1': {
                'type': 'separator',
            },
            'Logout': {
                'shortcut': 'Ctrl+Shift+L',
                'status_tip': 'Logout from Impartus',
                'callback': Callbacks().on_logout_click,
            },
            'sep2': {
                'type': 'separator',
            },
            'Quit': {
                'shortcut': 'Ctrl+Q',
                'status_tip': 'Quit Application',
                'callback': partial(sys.exit, 0)
            },
        },
        'View': {
            'Columns': {
                'shortcut': None,
                'status_tip': None,
                'type': 'list',
                'status': 'disabled',
                'behavior': 'multiselect',
                'child_items':
                    [x['display_name'] for x in [*Columns.data_columns.values(), *Columns.widget_columns.values()]],
                'child_callbacks': [partial(Callbacks().on_column_click, key)
                                    for key in [*Columns.data_columns.keys(), *Columns.widget_columns.keys()]]
            },
            'sep': {
                'type': 'separator',
            },
            'Search': {
                'shortcut': 'Ctrl+F',
                'status_tip': 'Search Content...',
                'callback': Callbacks().on_search_click,
            },
        },
        'Video': {
            'Flipped Video Lecture Quality': {
                'shortcut': None,
                'type': 'list',
                'status_tip': None,
                'status': 'disabled',
                'behavior': 'singleselect',
                'child_items': [
                    'highest',
                    *[x for x in conf.get('flipped_lecture_quality_order')],
                    'lowest'
                ],
                'default': conf.get('flipped_lecture_quality'),
                'child_callbacks': [
                    partial(Callbacks().on_video_quality_click, video_quality)
                    for video_quality in ['highest', *conf.get('flipped_lecture_quality_order'), 'lowest']
                ],
            },
            'sep': {
                'type': 'separator',
            },
            'Download Video': {
                'shortcut': 'Ctrl+J',
                'status_tip': 'Download Lecture Video',
                'callback': Callbacks().on_download_video_click,
            },
            'Play Video': {
                'shortcut': 'Ctrl+P',
                'status_tip': 'Play Lecture Video',
                'callback': Callbacks().on_play_video_click,
            },
            'Download Lecture Chats': {
                'shortcut': 'Shift+Ctrl+J',
                'status_tip': 'Download Lecture Chats',
                'callback': Callbacks().on_download_chats_click,
            },
        },
        'Slides': {
            'Download Backpack Slides': {
                'shortcut': 'Ctrl+K',
                'status_tip': 'Download Lecture Slides',
                'callback': Callbacks().on_download_slides_click,
            },
            'Open Folder': {
                'shortcut': 'Ctrl+O',
                'status_tip': 'Open Lecture Content Folder',
                'callback': Callbacks().on_open_folder_click,
            },
            'Attach Lecture Slides': {
                'shortcut': 'Shift+Ctrl+O',
                'status_tip': 'Attach Downloaded Slides to a Lecture',
                'callback': Callbacks().on_attach_slides_click,
            },
        },
        'Help': {
            'Help': {
                'shortcut': None,
                'status_tip': 'Help docs',
                'callback': Callbacks().on_help_doc,
            },
            'Check For Updates': {
                'shortcut': None,
                'status_tip': 'Check for new version, release notes...',
                'callback': Callbacks().on_check_for_updates_click,
            },
        }
    }


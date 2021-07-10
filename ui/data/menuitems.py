import sys
from functools import partial

from lib.config import ConfigType, Config
from ui.data.Icons import Icons
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
                'icon': Icons.MENU__LOGIN.value,
                'shortcut': 'Ctrl+L',
                'status_tip': 'Login to Impartus',
                'callback': Callbacks().on_menu_login_click,
            },
            'Reload': {
                'icon': Icons.MENU__RELOAD.value,
                'shortcut': 'Ctrl+R',
                'status_tip': 'Reload Table Content',
                'callback': Callbacks().on_menu_reload_click,
            },
            'Auto Organize': {
                'icon': Icons.MENU__AUTO_ORGANIZE.value,
                'shortcut': 'Ctrl+/',
                'status_tip': 'Rename lecture videos, download missing captions...',
                'callback': Callbacks().on_menu_auto_organize_click,
            },
            'sep1': {
                'type': 'separator',
            },
            'Logout': {
                'icon': Icons.MENU__LOGOUT.value,
                'shortcut': 'Ctrl+Shift+L',
                'status_tip': 'Logout from Impartus',
                'callback': Callbacks().on_menu_logout_click,
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
                'icon': Icons.MENU__COLUMNS.value,
                'shortcut': None,
                'status_tip': None,
                'type': 'list',
                'status': 'disabled',
                'behavior': 'multiselect',
                'child_items': {k: v['menu_name'] for k, v in
                                {**Columns.data_columns, **Columns.widget_columns}.items()},
                'child_callbacks': [partial(Callbacks().on_menu_column_click, key)
                                    for key in [*Columns.data_columns.keys(), *Columns.widget_columns.keys()]]
            },
            'sep': {
                'type': 'separator',
            },
            'Search': {
                'icon': Icons.MENU__SEARCH.value,
                'shortcut': 'Ctrl+F',
                'status_tip': 'Search Content...',
                'callback': Callbacks().on_menu_search_click,
            },
        },
        'Video': {
            'Flipped Video Lecture Quality': {
                'icon': Icons.MENU__FLIPPED_VIDEO_QUALITY.value,
                'shortcut': None,
                'type': 'list',
                'status_tip': None,
                'status': 'disabled',
                'behavior': 'singleselect',
                'child_items': {
                    **{'highest': 'Highest'},
                    **{x: x for x in conf.get('flipped_lecture_quality_order')},
                    **{'lowest': 'Lowest'}
                },
                'default': conf.get('flipped_lecture_quality').title(),
                'child_callbacks': [
                    partial(Callbacks().on_menu_video_quality_click, video_quality)
                    for video_quality in ['highest', *conf.get('flipped_lecture_quality_order'), 'lowest']
                ],
            },
            'sep': {
                'type': 'separator',
            },
            'Download Video': {
                'icon': Icons.MENU__DOWNLOAD_VIDEO.value,
                'shortcut': 'Ctrl+J',
                'status_tip': 'Download Lecture Video',
                'callback': Callbacks().on_menu_download_video_click,
            },
            'Play Video': {
                'icon': Icons.MENU__PLAY_VIDEO.value,
                'shortcut': 'Ctrl+P',
                'status_tip': 'Play Lecture Video',
                'callback': Callbacks().on_menu_play_video_click,
            },
            'Download Lecture Chats': {
                'icon': Icons.MENU__DOWNLOAD_CAPTIONS.value,
                'shortcut': 'Shift+Ctrl+J',
                'status_tip': 'Download Lecture Chats',
                'callback': Callbacks().on_menu_download_chats_click,
            },
        },
        'Slides': {
            'Download Backpack Slides': {
                'icon': Icons.MENU__DOWNLOAD_SLIDES.value,
                'shortcut': 'Ctrl+K',
                'status_tip': 'Download Lecture Slides',
                'callback': Callbacks().on_menu_download_slides_click,
            },
            'Open Folder': {
                'icon': Icons.MENU__OPEN_FOLDER.value,
                'shortcut': 'Ctrl+O',
                'status_tip': 'Open Lecture Content Folder',
                'callback': Callbacks().on_menu_open_folder_click,
            },
            'Attach Lecture Slides': {
                'icon': Icons.MENU__ATTACH_SLIDES.value,
                'shortcut': 'Shift+Ctrl+O',
                'status_tip': 'Attach Downloaded Slides to a Lecture',
                'callback': Callbacks().on_menu_attach_slides_click,
            },
        },
        'Help': {
            'Help': {
                'icon': Icons.MENU__HELP.value,
                'shortcut': None,
                'status_tip': 'Help docs',
                'callback': Callbacks().on_menu_help_doc_click,
            },
            'Check For Updates': {
                'icon': Icons.MENU__RELEASE_NOTES.value,
                'shortcut': None,
                'status_tip': 'Check for new version, release notes...',
                'callback': Callbacks().on_menu_check_for_updates_click,
            },
        }
    }


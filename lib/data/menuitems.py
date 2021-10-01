import sys
from functools import partial

from lib.config import ConfigType, Config
from lib.data.columns import Columns
from ui.callbacks.menucallbacks import MenuCallbacks
from lib.data.Icons import Icons


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
                'callback': MenuCallbacks().on_click__menu__actions_login,
            },
            'Reload': {
                'icon': Icons.MENU__RELOAD.value,
                'shortcut': 'Ctrl+R',
                'status_tip': 'Reload Table Content',
                'callback': MenuCallbacks().on_click__menu__actions_reload,
            },
            'Auto Organize': {
                'icon': Icons.MENU__AUTO_ORGANIZE.value,
                'shortcut': 'Ctrl+/',
                'status_tip': 'Rename lecture videos, download missing captions...',
                'callback': MenuCallbacks().on_click__menu__actions_auto_organize,
            },
            'sep1': {
                'type': 'separator',
            },
            'Logout': {
                'icon': Icons.MENU__LOGOUT.value,
                'shortcut': 'Ctrl+Shift+L',
                'status_tip': 'Logout from Impartus',
                'callback': MenuCallbacks().on_click__menu__actions_logout,
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
                'child_items': {k: v['menu_name'] for k, v in Columns.get_video_columns().items()},
                'child_callbacks': [partial(MenuCallbacks().on_click__menu__view_columns, key)
                                    for key in Columns.get_video_columns()]
            },
            'sep': {
                'type': 'separator',
            },
            'Search': {
                'icon': Icons.MENU__SEARCH.value,
                'shortcut': 'Ctrl+F',
                'status_tip': 'Search Content...',
                'callback': MenuCallbacks().on_click__menu__view_search,
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
                    partial(MenuCallbacks().on_click__menu__video_flipped_video_lecture_quality, video_quality)
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
                'callback': MenuCallbacks().on_click__menu__video_download_video,
            },
            'Play Video': {
                'icon': Icons.MENU__PLAY_VIDEO.value,
                'shortcut': 'Ctrl+P',
                'status_tip': 'Play Lecture Video',
                'callback': MenuCallbacks().on_click__menu__video_play_video,
            },
            'Download Lecture Chats': {
                'icon': Icons.MENU__DOWNLOAD_CAPTIONS.value,
                'shortcut': 'Shift+Ctrl+J',
                'status_tip': 'Download Lecture Chats',
                'callback': MenuCallbacks().on_click__menu__video_download_lecture_chats,
            },
            'Open Folder': {
                'icon': Icons.MENU__OPEN_FOLDER.value,
                'shortcut': 'Ctrl+O',
                'status_tip': 'Open Video Folder',
                'callback': MenuCallbacks().on_click__menu__video_open_folder,
            },
        },
        'Slides': {
            'Download Backpack Document': {
                'icon': Icons.MENU__DOWNLOAD_SLIDES.value,
                'shortcut': 'Ctrl+K',
                'status_tip': 'Download Lecture Slides',
                'callback': MenuCallbacks().on_click__menu__slides_download_backpack_slides,
            },
            'View Document': {
                'icon': Icons.MENU__SHOW_SLIDES.value,
                'shortcut': 'Shift+Ctrl+P',
                'status_tip': 'View Document',
                'callback': MenuCallbacks().on_click__menu__slides_view_document,
            },
            'Open Folder': {
                'icon': Icons.MENU__OPEN_FOLDER.value,
                'shortcut': 'Shift+Ctrl+O',
                'status_tip': 'Open Lecture Content Folder',
                'callback': MenuCallbacks().on_click__menu__slides_open_folder,
            },
            'Attach Lecture Slides': {
                'icon': Icons.MENU__ATTACH_SLIDES.value,
                'shortcut': 'Shift+Ctrl+A',
                'status_tip': 'Attach Downloaded Slides to a Lecture',
                'callback': MenuCallbacks().on_click__menu__slides_attach_lecture_slides,
            },
        },
        'Help': {
            'Help': {
                'icon': Icons.MENU__HELP.value,
                'shortcut': None,
                'status_tip': 'Help docs',
                'callback': MenuCallbacks().on_click__menu__help_help,
            },
            'Check For Updates': {
                'icon': Icons.MENU__RELEASE_NOTES.value,
                'shortcut': None,
                'status_tip': 'Check for new version, release notes...',
                'callback': MenuCallbacks().on_click__menu__help_check_for_updates,
            },
        }
    }

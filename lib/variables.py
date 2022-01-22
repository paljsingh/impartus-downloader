from lib.config import Config, ConfigType


class Variables(object):
    """
    Class to hold shared variables, implements a singleton.
    """

    _login_url = None
    _login_email = None
    _login_password = None

    _flipped_lecture_quality = None

    _menu_actions_login_item = None
    _menu_actions_reload_item = None
    _menu_actions_auto_organize_item = None

    _menu_video_download_video_item = None
    _menu_video_play_video_item = None
    _menu_video_download_chats_item = None

    _menu_slides_download_slides_item = None
    _menu_slides_open_folder_item = None
    _menu_slides_attach_slides_item = None
    _menu_slides_show_slides_item = None

    _log_window = None
    _tab_widget = None

    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(Variables, cls)
            cls._instance = orig.__new__(cls)

        # any other initializations.
        cls._flipped_lecture_quality = Config.load(ConfigType.IMPARTUS).get('flipped_lecture_quality')

        return cls._instance

    @classmethod
    def login_url(cls):
        return cls._login_url

    @classmethod
    def set_login_url(cls, value: str):
        cls._login_url = value

    @classmethod
    def login_email(cls):
        return cls._login_email

    @classmethod
    def set_login_email(cls, value: str):
        cls._login_email = value

    @classmethod
    def login_password(cls):
        return cls._login_password

    @classmethod
    def set_login_password(cls, value: str):
        cls._login_password = value

    @classmethod
    def flipped_lecture_quality(cls):
        return cls._flipped_lecture_quality

    @classmethod
    def set_flipped_lecture_quality(cls, value: str):
        cls._flipped_lecture_quality = value

    @classmethod
    def log_window(cls):
        return cls._log_window

    @classmethod
    def set_log_window(cls, _log_window):
        cls._log_window = _log_window

    @classmethod
    def set_current_tab_widget(cls, widget):
        cls._tab_widget = widget

    @classmethod
    def get_current_tab_widget(cls):
        return cls._tab_widget

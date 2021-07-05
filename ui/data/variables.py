from lib.config import Config, ConfigType


class Variables(object):
    """
    Class to hold shared variables, implements a singleton.
    TODO: Should table.offline_data / table.online_data be moved here?
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

    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(Variables, cls)
            cls._instance = orig.__new__(cls)

        # any other initializations.
        cls._flipped_lecture_quality = Config.load(ConfigType.IMPARTUS).get('flipped_lecture_quality')
        return cls._instance

    def login_url(self):
        return self._login_url

    def set_login_url(self, value: str):
        self._login_url = value

    def login_email(self):
        return self._login_email

    def set_login_email(self, value: str):
        self._login_email = value

    def login_password(self):
        return self._login_password

    def set_login_password(self, value: str):
        self._login_password = value

    def flipped_lecture_quality(self):
        return self._flipped_lecture_quality

    def set_flipped_lecture_quality(self, value: str):
        self._flipped_lecture_quality = value


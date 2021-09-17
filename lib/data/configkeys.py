import enum


class ConfigKeys(enum.Enum):
    """
    class to hold all the entries specified in configuration files.
    TODO: Ensure no code file directly uses a config key.
    """
    URL = 'impartus_url'
    EMAIL = 'login_email'
    PASSWORD = 'password'
    TARGET_DIR = 'target_dir'
    CONFIG_DIR = 'config_dir'
    ALLOWED_EXT = 'allowed_ext'
    VIDEO_PATH = 'video_path'
    SLIDES_PATH = 'documents_path'
    CAPTIONS_PATH = 'captions_path'
    COLORSCHEME_DEFAULT = 'default'
    RESIZE_POLICY = 'resize_policy'
    USE_SAFE_PATHS = 'use_safe_paths'
    FLIPPED_LECTURE_QUALITY_ORDER = 'flipped_lecture_quality_order'

    def __str__(self):
        return str(self.value)

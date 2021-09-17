import enum


class Icons(enum.Enum):
    """
    fontawesome icons (https://fontawesome.com/v5.15/icons) loaded as QIcon via
    qtawesome (https://pypi.org/project/QtAwesome/)
    """

    VIDEO__DOWNLOAD_VIDEO = 'fa5s.download'
    VIDEO__PLAY_VIDEO = 'fa5.play-circle'
    VIDEO__DOWNLOAD_CAPTIONS = 'fa5.closed-captioning'
    VIDEO__OPEN_FOLDER = 'fa5.folder-open'

    SLIDES__DOWNLOAD_SLIDES = 'fa5s.file-download'
    SLIDES__SHOW_SLIDES = 'fa5.file-pdf'
    SLIDES__ATTACH_SLIDES = 'fa5s.link'

    SLIDES__FILETYPE_DOC_ARCHIVE = 'fa5.file-pdf'
    SLIDES__FILETYPE_DOC = 'fa5.file-word'
    SLIDES__FILETYPE_PRESENTATION = 'fa5.file-powerpoint'
    SLIDES__FILETYPE_IMAGE = 'fa5.file-image'
    SLIDES__FILETYPE_SPREADSHEET = 'fa5.file-excel'
    SLIDES__FILETYPE_CODE = 'fa5.file-code'
    SLIDES__FILETYPE_ARCHIVE = 'fa5.file-archive'
    SLIDES__FILETYPE_AUDIO = 'fa5.file-audio'
    SLIDES__FILETYPE_CSV = 'fa5s.file-csv'
    SLIDES__FILETYPE_MISC = 'fa5.file-alt'

    VIDEO__PAUSE_DOWNLOAD = 'fa5.pause-circle'
    VIDEO__RESUME_DOWNLOAD = 'fa5s.chevron-circle-right'
    VIDEO__VIDEO_PROCESSING = 'fa5s.spinner'

    TABLE__EDITABLE_COLUMN = 'fa.edit'
    TABLE__SORT_DESC = 'fa5s.sort-down'
    TABLE__SORT_ASC = 'fa5s.sort-up'

    MENU__LOGIN = 'fa5s.sign-in-alt'
    MENU__RELOAD = 'fa5s.redo-alt'
    MENU__AUTO_ORGANIZE = 'fa5s.magic'
    MENU__LOGOUT = 'fa5s.sign-out-alt'
    # MENU__QUIT = ''

    MENU__COLUMNS = 'fa5s.columns'
    MENU__SEARCH = 'fa5s.search'

    MENU__FLIPPED_VIDEO_QUALITY = 'fa5s.exchange-alt'
    MENU__DOWNLOAD_VIDEO = 'fa5s.download'
    MENU__PLAY_VIDEO = 'fa5.play-circle'
    MENU__OPEN_FOLDER = 'fa5.folder-open'

    MENU__DOWNLOAD_SLIDES = 'fa5s.file-download'
    MENU__DOWNLOAD_CAPTIONS = 'fa5.closed-captioning'
    MENU__ATTACH_SLIDES = 'fa5s.link'

    MENU__HELP = 'fa5s.info'
    MENU__RELEASE_NOTES = 'fa5s.list-ul'

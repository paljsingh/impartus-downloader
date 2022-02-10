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

    DOCUMENT__DOWNLOAD_SLIDES = 'fa5s.file-download'
    DOCUMENT__SHOW_SLIDES = 'fa5.file-pdf'
    DOCUMENT__ATTACH_SLIDES = 'fa5s.link'

    DOCUMENT__FILETYPE_DOC_ARCHIVE = 'fa5.file-pdf'
    DOCUMENT__FILETYPE_DOC = 'fa5.file-word'
    DOCUMENT__FILETYPE_PRESENTATION = 'fa5.file-powerpoint'
    DOCUMENT__FILETYPE_IMAGE = 'fa5.file-image'
    DOCUMENT__FILETYPE_SPREADSHEET = 'fa5.file-excel'
    DOCUMENT__FILETYPE_CODE = 'fa5.file-code'
    DOCUMENT__FILETYPE_ARCHIVE = 'fa5.file-archive'
    DOCUMENT__FILETYPE_AUDIO = 'fa5.file-audio'
    DOCUMENT__FILETYPE_CSV = 'fa5s.file-csv'
    DOCUMENT__FILETYPE_MISC = 'fa5.file-alt'

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
    MENU__SHOW_SLIDES = 'fa5.file-pdf'
    MENU__DOWNLOAD_CAPTIONS = 'fa5.closed-captioning'
    MENU__ATTACH_SLIDES = 'fa5s.link'

    MENU__HELP = 'fa5s.info'
    MENU__RELEASE_NOTES = 'fa5s.list-ul'

    SEARCH__CASE_SENSITIVE = 'mdi.format-letter-case'
    SEARCH__WILDCARD = 'mdi.regex'
    SEARCH__CHATS = 'mdi.comment-search-outline'
    SEARCH__DOCUMENTS = 'mdi.file-search-outline'

    APP_LOGO = 'ui/images/logo.png'


class DocumentIcons:

    filetypes = {
        'pdf': Icons.DOCUMENT__FILETYPE_DOC_ARCHIVE.value,

        'doc': Icons.DOCUMENT__FILETYPE_DOC.value,
        'docx': Icons.DOCUMENT__FILETYPE_DOC.value,
        'rtf': Icons.DOCUMENT__FILETYPE_DOC.value,
        'odf': Icons.DOCUMENT__FILETYPE_DOC.value,
        'pages': Icons.DOCUMENT__FILETYPE_DOC.value,

        'ppt': Icons.DOCUMENT__FILETYPE_PRESENTATION.value,
        'pptx': Icons.DOCUMENT__FILETYPE_PRESENTATION.value,
        'ppsx': Icons.DOCUMENT__FILETYPE_PRESENTATION.value,
        'odp': Icons.DOCUMENT__FILETYPE_PRESENTATION.value,
        'key': Icons.DOCUMENT__FILETYPE_PRESENTATION.value,

        'xls': Icons.DOCUMENT__FILETYPE_SPREADSHEET.value,
        'xlsx': Icons.DOCUMENT__FILETYPE_SPREADSHEET.value,
        'ods': Icons.DOCUMENT__FILETYPE_SPREADSHEET.value,
        'numbers': Icons.DOCUMENT__FILETYPE_SPREADSHEET.value,

        'csv': Icons.DOCUMENT__FILETYPE_CSV.value,

        'zip': Icons.DOCUMENT__FILETYPE_ARCHIVE.value,
        'rar': Icons.DOCUMENT__FILETYPE_ARCHIVE.value,
        'tar': Icons.DOCUMENT__FILETYPE_ARCHIVE.value,
        'gz': Icons.DOCUMENT__FILETYPE_ARCHIVE.value,
        'bz2': Icons.DOCUMENT__FILETYPE_ARCHIVE.value,
        '7z': Icons.DOCUMENT__FILETYPE_ARCHIVE.value,

        'jpg': Icons.DOCUMENT__FILETYPE_IMAGE.value,
        'jpeg': Icons.DOCUMENT__FILETYPE_IMAGE.value,
        'png': Icons.DOCUMENT__FILETYPE_IMAGE.value,
        'gif': Icons.DOCUMENT__FILETYPE_IMAGE.value,

        'exe': Icons.DOCUMENT__FILETYPE_CODE.value,
        'py': Icons.DOCUMENT__FILETYPE_CODE.value,
        'ipynb': Icons.DOCUMENT__FILETYPE_CODE.value,
        'r': Icons.DOCUMENT__FILETYPE_CODE.value,
        'java': Icons.DOCUMENT__FILETYPE_CODE.value,
        'dmg': Icons.DOCUMENT__FILETYPE_CODE.value,

        'txt': Icons.DOCUMENT__FILETYPE_CODE.value,
        'text': Icons.DOCUMENT__FILETYPE_CODE.value,
        'html': Icons.DOCUMENT__FILETYPE_CODE.value,
        'htm': Icons.DOCUMENT__FILETYPE_CODE.value,
    }

    @classmethod
    def get_icon_type(cls, slide_path: str):
        ext = slide_path.split('.')[-1]
        if DocumentIcons.filetypes.get(ext):
            return DocumentIcons.filetypes[ext]
        else:
            return Icons.DOCUMENT__FILETYPE_MISC.value

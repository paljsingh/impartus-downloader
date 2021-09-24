import enum


class Labels(enum.Enum):
    """
    Labels used throughout the application.
    TODO: Remove unicode chars as their size and rendering can be platform and font specific, leading to uneven sized
        or incorrectly displayed widgets.
    """
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
    LOGIN_TITLE = 'Login - Impartus'

    VIDEO__SUBJECT_NAME = 'subjectNameShort'
    VIDEO__PROFESSOR_NAME = 'professorName'
    VIDEO__TOPIC = 'topic'
    VIDEO__SEQ = 'seqNo'
    VIDEO__DURATION = 'actualDurationReadable'
    VIDEO__CHANNELS = 'tapNToggle'
    VIDEO__DATE = 'startDate'
    VIDEO__FLIPPED = 'flipped'
    VIDEO__PROGRESSBAR = 'progress_bar'
    VIDEO__ACTIONS = 'video_actions'
    VIDEO__REGULAR_ID = 'ttid'
    VIDEO__FLIPPED_ID = 'fcid'

    DOCUMENT__SUBJECT_NAME = 'subjectNameShort'
    DOCUMENT__SEQ = 'seqNo'
    DOCUMENT__FILENAME = 'fileName'
    DOCUMENT__FILESIZE = 'fileLength'
    DOCUMENT__DATE = 'fileDate'
    DOCUMENT__ACTIONS = 'slides_actions'

    SUBJECT_NAME = 'subjectName'
    SUBJECT_NAME_SHORT = 'subjectNameShort'

    DOCUMENT__OPEN_FOLDER = 'open_folder'
    DOCUMENT__OPEN_DOCUMENT = 'open_document'
    DOCUMENT__ATTACH_DOCUMENT = 'attach_document'
    DOCUMENT__DOWNLOAD_DOCUMENT = 'download_document'

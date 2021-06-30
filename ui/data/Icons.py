import enum


class Icons(enum.Enum):
    """
    Unicode chars for Icons
    TODO: Use images instead of unicode chars due to their issues with size and rendering.
    """

    DOWNLOAD_VIDEO = '⬇'
    PLAY_VIDEO = '▶'
    OPEN_FOLDER = '⏏'
    DOWNLOAD_SLIDES = '⬇'
    DOWNLOAD_CAPTIONS = '㏄'
    SHOW_SLIDES = '▤'
    ATTACH_SLIDES = '📎'
    PAUSE_DOWNLOAD = '❘❘'
    RESUME_DOWNLOAD = '❘❘▶'
    VIDEO_PROCESSING = '⧗'
    VIDEO_DOWNLOADED = '✓'
    VIDEO_NOT_DOWNLOADED = '⃠'
    SLIDES_DOWNLOADED = '▤'
    MOVED_TO = '⇨'

    def __str__(self):
        return str(self.value)


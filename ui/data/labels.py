import enum


class Labels(enum.Enum):
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

    def __str__(self):
        return str(self.value)


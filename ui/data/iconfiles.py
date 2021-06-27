import enum


class IconFiles(enum.Enum):

    SORT_UP_ARROW = 'images/sort-up.png'
    SORT_DOWN_ARROW = 'images/sort-down.png'
    EDITABLE_BLUE = 'images/editable-blue.png'
    EDITABLE_RED = 'images/editable-red.png'
    APP_LOGO = 'images/logo.png'

    def __str__(self):
        return str(self.value)


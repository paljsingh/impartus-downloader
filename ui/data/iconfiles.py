import enum


class IconFiles(enum.Enum):

    SORT_UP_ARROW = 'ui/images/sort-up.png'
    SORT_DOWN_ARROW = 'ui/images/sort-down.png'
    EDITABLE_BLUE = 'ui/images/editable-blue.png'
    EDITABLE_RED = 'ui/images/editable-red.png'
    APP_LOGO = 'ui/images/logo.png'

    def __str__(self):
        return str(self.value)


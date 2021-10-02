import typing

from PySide2.QtWidgets import QCheckBox


class CustomCheckBox(QCheckBox):

    def __init__(self):
        super().__init__()
        self.value = None

    def setValue(self, value: typing.Dict):     # noqa
        self.value = value

    def getValue(self):     # noqa
        return self.value

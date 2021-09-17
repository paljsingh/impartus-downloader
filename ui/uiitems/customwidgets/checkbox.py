import typing

from PySide2.QtWidgets import QCheckBox


class CustomCheckBox(QCheckBox):

    def __init__(self):
        super().__init__()
        self.value = None

    def setValue(self, value: typing.Dict):
        self.value = value

    def getValue(self):
        return self.value

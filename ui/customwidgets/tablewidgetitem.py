from PySide2.QtWidgets import QTableWidgetItem


class CustomTableWidgetItem(QTableWidgetItem):

    def __init__(self):
        super().__init__()
        self.value = None

    def setValue(self, value: int):
        self.value = value

    def __lt__(self, other):
        return self.value < other.value

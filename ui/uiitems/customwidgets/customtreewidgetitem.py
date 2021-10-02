from PySide2.QtWidgets import QTreeWidgetItem


class CustomTreeWidgetItem(QTreeWidgetItem):
    """
    A custom table widget item holds a numeric value and allows the columns to be numerically sorted
    by the value.
    Used by
        progressbar to sort records by download percentage value
        slide items column to sort records by the number of lecture slides downloaded.
        video items column to sort by the status of its pushbuttons.
    """
    def __init__(self):
        super().__init__()
        self.value = None

    def setValue(self, value: int):     # noqa
        self.value = value

    def __lt__(self, other):
        return self.value < other.value

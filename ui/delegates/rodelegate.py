from PySide2.QtCore import QModelIndex
from PySide2.QtWidgets import QStyledItemDelegate, QWidget, QStyleOptionViewItem


class ReadOnlyDelegate(QStyledItemDelegate):
    """
    Disable content editor for given table columns, to set them as readonly.
    """

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        return

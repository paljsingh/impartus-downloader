from PySide2.QtCore import QModelIndex
from PySide2.QtWidgets import QStyledItemDelegate, QWidget, QStyleOptionViewItem


class ReadOnlyDelegate(QStyledItemDelegate):

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        return


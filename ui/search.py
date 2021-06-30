from PySide2 import QtCore
from PySide2.QtWidgets import QHBoxLayout, QWidget, QLabel, QLineEdit, QMainWindow, QTableWidget

from ui.data.searchdirections import SearchDirection


class SearchBox:
    """
    Class to provide search functionality.
    TODO: separate the search_box creation code from the content search logic.
    """

    def __init__(self, window: QMainWindow):
        self.window = window
        self.last_index = -1    # first search should yield position 0 (for 0 based indexed results)
        self.search_results = None
        self.search_term = None

        self.search_box = None
        self.results_label = None

        self.table = None
        pass

    def add_search_box(self):
        search_box = QLineEdit()
        search_box.setPlaceholderText('Search...')
        search_box.textChanged.connect(self.search)
        QtCore.QMetaObject.connectSlotsByName(self.window)

        results_label = QLabel()

        # create a horizontal container.
        widget = QWidget()
        hbox_layout = QHBoxLayout(widget)
        hbox_layout.addWidget(search_box)
        hbox_layout.addWidget(results_label)

        self.search_box = search_box
        self.results_label = results_label
        return widget

    def set_table_widget_to_search(self, table: QTableWidget):
        self.table = table

    def search_next(self, direction: int = SearchDirection.FORWARD.value):
        if not self.search_results:
            return

        count = len(self.search_results)
        self.table.clearSelection()
        new_index = (self.last_index + direction) % count
        self.table.scrollToItem(self.search_results[new_index])
        self.search_results[new_index].setSelected(True)

        # also, update results label.
        self.last_index = new_index
        self.results_label.setText('{} / {} matches'.format(new_index + 1, count))  # 1 based output.

    def search_prev(self):
        self.search_next(SearchDirection.BACKWARD.value)

    def search(self):
        self.table.clearSelection()
        self.results_label.clear()
        self.search_results = None
        text = self.search_box.text().lower()
        # do not search for short text.
        if len(text) <= 2:
            return True

        self.search_results = self.table.findItems(text, QtCore.Qt.MatchFlag.MatchContains)
        self.search_term = self.search_box.text()
        self.last_index = -1  # first search shall be index 0.
        self.search_next()
        return True

    def set_focus(self):
        self.search_box.setFocus()
        self.search_box.selectAll()

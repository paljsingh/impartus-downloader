from abc import ABC, abstractmethod

from PySide2 import QtCore
from PySide2.QtWidgets import QLabel, QLineEdit, QMainWindow, QTableWidget, QTreeWidget

from lib.data.searchdirections import SearchDirection
from lib.variables import Variables


class SearchBox:
    """
    Class to provide search functionality.
    TODO: separate the search_box creation code from the content search logic.
    """
    search_edit: QLineEdit
    results_label: QLabel

    def __init__(self, content_window: QMainWindow):
        self.content_window = content_window

        self.search_edit = self.content_window.findChild(QLineEdit, "search_box")        # noqa
        self.search_edit.textChanged.connect(self.search)        # noqa
        QtCore.QMetaObject.connectSlotsByName(self.content_window)
        self.results_label = self.content_window.findChild(QLabel, "results_label")     # noqa

    def highlight_next(self):
        search_type = SearchFactory().get_search_type()
        new_index, count = search_type.highlight_next()

        # also, update results label.
        self.update_results_label(new_index, count)

    def highlight_prev(self):
        search_type = SearchFactory().get_search_type()
        search_type.highlight_prev()
        self.update_results_label()

    def search(self):
        self.results_label.clear()
        text = self.search_edit.text().lower()
        # do not search for short text.
        if len(text) <= 2:
            return True

        search_type = SearchFactory().get_search_type()
        new_index, count = search_type.search(text)
        self.update_results_label(new_index, count)

    def update_search_edit_text(self):
        search_type = SearchFactory().get_search_type()
        self.search_edit.setText(search_type.get_search_term())

    def update_results_label(self, current_index: int = None, total: int = None):
        if total:
            self.results_label.setText('{} / {} matches'.format(current_index + 1, total))  # 1 based output.
        else:
            self.results_label.setText('No matches found.')

    def set_focus(self):
        self.search_edit.setFocus()
        self.search_edit.selectAll()


class SearchType(ABC):

    def __init__(self):
        self.search_term = None

    def set_search_term(self, search_term: str):
        self.search_term = search_term

    @abstractmethod
    def search(self, text: str):
        pass

    @abstractmethod
    def highlight_next(self):
        pass

    @abstractmethod
    def highlight_prev(self):
        pass

    def get_search_term(self):
        return self.search_term


class SearchTable(SearchType):

    def __init__(self, table_widget: QTableWidget):
        super().__init__()
        self.last_index = -1    # first search should yield position 0 (for 0 based indexed results)
        self.search_results = None
        self.table = table_widget

    def search(self, text: str):
        self.set_search_term(text)
        self.table.clearSelection()
        self.search_results = self.table.findItems(text, QtCore.Qt.MatchFlag.MatchContains)
        self.last_index = -1  # first search shall be index 0.
        return self.highlight_next()

    def highlight_next(self, direction: int = SearchDirection.FORWARD.value):
        if self.search_results is None or len(self.search_results) == 0:
            return None, None

        count = len(self.search_results)
        self.table.clearSelection()
        new_index = (self.last_index + direction) % count
        self.table.scrollToItem(self.search_results[new_index])
        self.search_results[new_index].setSelected(True)

        # also, update results label.
        self.last_index = new_index
        return new_index, count

    def highlight_prev(self):
        return self.highlight_next(SearchDirection.BACKWARD.value)


class SearchTree(SearchType):

    def __init__(self, tree_widget: QTreeWidget):
        super().__init__()
        self.last_index = -1    # first search should yield position 0 (for 0 based indexed results)
        self.search_results = None
        self.tree_widget = tree_widget

    def search(self, text: str):
        self.set_search_term(text)
        self.tree_widget.clearSelection()

        # search all columns.
        results = list()
        for i in range(self.tree_widget.columnCount()):
            results.extend(self.tree_widget.findItems(text, QtCore.Qt.MatchFlag.MatchContains | QtCore.Qt.MatchFlag.MatchRecursive, i))
        self.search_results = results
        self.last_index = -1  # first search shall be index 0.
        return self.highlight_next()

    def highlight_next(self, direction: int = SearchDirection.FORWARD.value):
        if self.search_results is None or len(self.search_results) == 0:
            return None, None

        count = len(self.search_results)
        self.tree_widget.clearSelection()
        new_index = (self.last_index + direction) % count
        self.tree_widget.scrollToItem(self.search_results[new_index])
        self.search_results[new_index].setSelected(True)

        # also, update results label.
        self.last_index = new_index
        return new_index, count

    def highlight_prev(self):
        return self.highlight_next(SearchDirection.BACKWARD.value)


class SearchFactory:
    search_table = None
    search_tree = None

    @classmethod
    def get_search_type(cls):
        widget = Variables().get_current_tab_widget()
        if type(widget) == QTableWidget:
            if not cls.search_table:
                cls.search_table = SearchTable(widget)
            return cls.search_table
        else:
            if not cls.search_tree:
                cls.search_tree = SearchTree(widget)
            return cls.search_tree

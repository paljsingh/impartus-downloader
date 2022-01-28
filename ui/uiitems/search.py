import os
from abc import ABC, abstractmethod
from typing import Dict
import qtawesome as qta
import webvtt

from PySide2 import QtCore
from PySide2.QtWidgets import QLabel, QLineEdit, QMainWindow, QTableWidget, QTreeWidget, QPushButton

from lib.data.Icons import Icons
from lib.data.columns import Columns
from lib.data.labels import Labels
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

        self.case_sensitive_search = False
        self.case_sensitive_search_button = self.content_window.findChild(QPushButton, "caseSensitiveSearch")
        self.case_sensitive_search_button.setCheckable(True)
        self.case_sensitive_search_button.setToolTip("Case Sensitive")
        self.case_sensitive_search_button.setIcon(qta.icon(Icons.SEARCH__CASE_SENSITIVE.value))
        self.case_sensitive_search_button.clicked.connect(self.on_click_case_sensitive_button)

        self.wildcard_search = False
        self.wildcard_search_button = self.content_window.findChild(QPushButton, "wildcardSearch")
        self.wildcard_search_button.setCheckable(True)
        self.wildcard_search_button.setToolTip("Wildcard Search")
        self.wildcard_search_button.setIcon(qta.icon(Icons.SEARCH__WILDCARD.value))
        self.wildcard_search_button.clicked.connect(self.on_click_wildcard_search_button)

        self.search_in_chats = False
        self.search_chats_button = self.content_window.findChild(QPushButton, "chatSearch")
        self.search_chats_button.setCheckable(True)
        self.search_chats_button.setToolTip("Search Lecture Chats")
        self.search_chats_button.setVisible(True)
        self.search_chats_button.setIcon(qta.icon(Icons.SEARCH__CHATS.value))
        self.search_chats_button.clicked.connect(self.on_click_search_chats_button)

        self.search_in_documents = False
        self.search_documents_button = self.content_window.findChild(QPushButton, "documentSearch")
        self.search_documents_button.setCheckable(True)
        self.search_documents_button.setToolTip("Search Documents")
        self.search_documents_button.setVisible(False)
        self.search_documents_button.setIcon(qta.icon(Icons.SEARCH__DOCUMENTS.value))
        self.search_documents_button.clicked.connect(self.on_click_search_documents_button)

        self.search_prev_button = self.content_window.findChild(QPushButton, "prevSearch")
        self.search_prev_button.setIcon(qta.icon("fa5s.chevron-left"))
        self.search_prev_button.clicked.connect(self.on_click_search_prev_button)

        self.search_next_button = self.content_window.findChild(QPushButton, "nextSearch")
        self.search_next_button.setIcon(qta.icon("fa5s.chevron-right"))
        self.search_next_button.clicked.connect(self.on_click_search_next_button)

    def highlight_next(self):
        search_type = SearchFactory().get_search_type()
        new_index, count = search_type.highlight_next()

        # also, update results label.
        self.update_results_label(new_index, count)

    def highlight_prev(self):
        search_type = SearchFactory().get_search_type()
        new_index, count = search_type.highlight_prev()
        self.update_results_label(new_index, count)

    def get_search_options(self):
        return {
            'case_sensitive_search': self.case_sensitive_search,
            'wildcard_search': self.wildcard_search,
            'search_in_chats': self.search_in_chats,
            'search_in_documents': self.search_in_documents,
        }

    def search(self):
        self.results_label.clear()
        text = self.search_edit.text()
        # do not search for short text.
        if len(text) <= 2:
            return True

        search_type = SearchFactory().get_search_type()
        new_index, count = search_type.search(text, self.get_search_options())
        self.update_results_label(new_index, count)

    def update_search_edit_text(self):
        search_type = SearchFactory().get_search_type()
        self.search_edit.setText(search_type.get_search_term())

    def update_results_label(self, current_index: int = None, total: int = None):
        if total:
            self.results_label.setText('{} / {} matches'.format(current_index + 1, total))  # 1 based output.
        else:
            self.results_label.setText('No matches found.')

    def update_search_buttons(self):
        search_type = SearchFactory().get_search_type()
        if type(search_type) == SearchTable:
            self.search_chats_button.setVisible(True)
            self.search_documents_button.setVisible(False)
        else:
            self.search_chats_button.setVisible(False)
            self.search_documents_button.setVisible(True)

    def set_focus(self):
        self.search_edit.setFocus()
        self.search_edit.selectAll()

    def on_click_case_sensitive_button(self):
        self.case_sensitive_search = not self.case_sensitive_search
        self.case_sensitive_search_button.setDown(self.case_sensitive_search)
        self.search()

    def on_click_wildcard_search_button(self):
        self.wildcard_search = not self.wildcard_search
        self.wildcard_search_button.setDown(self.wildcard_search)
        self.search()

    def on_click_search_chats_button(self):
        self.search_in_chats = not self.search_in_chats
        self.search_chats_button.setDown(self.search_in_chats)
        self.search()

    def on_click_search_documents_button(self):
        self.search_in_documents = not self.search_in_documents
        self.search_documents_button.setDown(self.search_in_documents)
        self.search()

    def on_click_search_prev_button(self):
        self.highlight_prev()

    def on_click_search_next_button(self):
        self.highlight_next()


class SearchType(ABC):

    def __init__(self):
        self.search_term = None

    def set_search_term(self, search_term: str):
        self.search_term = search_term

    @abstractmethod
    def search(self, text: str, search_options: Dict):
        pass

    @abstractmethod
    def highlight_next(self):
        pass

    @abstractmethod
    def highlight_prev(self):
        pass

    def get_search_term(self):
        return self.search_term

    def get_search_flags(self, search_options: Dict):
        if search_options.get('wildcard_search'):
            search_flags = QtCore.Qt.MatchFlag.MatchWildcard
        else:
            search_flags = QtCore.Qt.MatchFlag.MatchContains

        if search_options.get('case_sensitive_search'):
            search_flags |= QtCore.Qt.MatchFlag.MatchCaseSensitive
        return search_flags


class SearchTable(SearchType):

    def __init__(self, table_widget: QTableWidget):
        super().__init__()
        self.last_index = -1    # first search should yield position 0 (for 0 based indexed results)
        self.search_results = None
        self.table = table_widget

    def search(self, text: str, search_options: Dict):
        self.set_search_term(text)
        self.table.clearSelection()
        self.search_results = self.table.findItems(text, self.get_search_flags(search_options))

        if search_options.get('search_in_chats'):
            self.search_results.extend(self.search_in_chats())

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

    def index_chats(self):
        if self.search_results_extra:
            return

        rows = self.table.rowCount()
        col = Columns.get_video_column_index_by_key(Labels.DOCUMENT__OFFLINE_FILEPATH.value)
        # rfid_col = Columns.get_video_column_index_by_key(Labels.V.value)

        captions_list = dict()
        for i in range(rows):
            mkvfile = self.table.item(i, col).text()
            if mkvfile:
                file = '{}.vtt'.format(mkvfile.removesuffix('.mkv'))
                if os.path.exists(file) and os.path.isfile(file):
                    captions_list[mkvfile] = webvtt.read(file)
        self.search_results_extra = captions_list


class SearchTree(SearchType):

    def __init__(self, tree_widget: QTreeWidget):
        super().__init__()
        self.last_index = -1    # first search should yield position 0 (for 0 based indexed results)
        self.search_results = None
        self.tree_widget = tree_widget

    def search(self, text: str, search_options: Dict):
        self.set_search_term(text)
        self.tree_widget.clearSelection()

        # search all columns.
        results = list()
        for i, (name, col) in enumerate(Columns.get_document_columns().items()):
            if not col.get('hidden'):
                search_flags = self.get_search_flags(search_options) | QtCore.Qt.MatchFlag.MatchRecursive
                results.extend(self.tree_widget.findItems(text, search_flags, i))

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

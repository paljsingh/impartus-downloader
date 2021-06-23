from PySide2 import QtCore
from PySide2.QtWidgets import QMainWindow, QWidget, QVBoxLayout

from qtui.menubar import Menubar
from lib.finder import Finder
from qtui.search import Search
from qtui.table import Table
from ui.data import Columns, Labels


class ContentWindow(QMainWindow):

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        offline_data = Finder().get_offline_content()

        self.menu_bar = Menubar(self).add_menu()
        self._set_window_properties()

        # extra checkbox column
        col_count = 1 + len([*Columns.data_columns, *Columns.widget_columns, *Columns.hidden_columns])
        row_count = len(offline_data)
        table_obj = Table(row_count, col_count).set_headers().set_row_content(offline_data).resizable_headers()
        table = table_obj.table

        # create a vbox layout and add search button, table to it.
        vcontainer_widget = QWidget()
        vbox_layout = QVBoxLayout(vcontainer_widget)

        self.search = Search(self, table)
        search_widget = self.search.add_search_box()
        vbox_layout.addWidget(search_widget)
        vbox_layout.addWidget(table)
        self.setCentralWidget(vcontainer_widget)
        table.show()

    def _set_window_properties(self):
        # full screen
        self.setGeometry(0, 0, self.maximumWidth(), self.maximumHeight())
        # window title
        self.setWindowTitle(Labels.APPLICATION_TITLE.value)

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Enter or e.key() == QtCore.Qt.Key_Return:
            self.search.search_next()
        elif e.key() == QtCore.Qt.Key_G and (e.modifiers() & QtCore.Qt.ShiftModifier) \
                and (e.modifiers() & QtCore.Qt.ControlModifier):
            self.search.search_prev()
        elif e.key() == QtCore.Qt.Key_G and (e.modifiers() & QtCore.Qt.ControlModifier):
            self.search.search_next()

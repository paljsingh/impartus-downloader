from PySide2 import QtCore, QtWidgets
from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QMainWindow, QTableWidget, QPlainTextEdit

from lib.finder import Finder
from lib.impartus import Impartus
from ui.data.callbacks import Callbacks
from ui.data.labels import Labels
from ui.uiitems.search import SearchBox
from ui.uiitems.table import Table


class ContentWindow(QMainWindow):
    """
    Content Window - provides a QTableWidget for displaying content, a search box for searching through the content.
    Also maintains a copy of the data obtained from the online and offline workflows and responsible for merging the
    two.
    """

    def __init__(self, impartus: Impartus):
        super().__init__()
        self.impartus = impartus

        loader = QUiLoader()
        file = QFile("ui/views/content.ui")
        file.open(QFile.ReadOnly)
        self.content_form = loader.load(file, self)
        file.close()

        self.setWindowTitle(Labels.APPLICATION_TITLE.value)
        self.setGeometry(0, 0, self.maximumWidth(), self.maximumHeight())

        self.table_widget = self.content_form.findChild(QTableWidget, "table")
        self.table_container = Table(self.impartus, self.table_widget)  # noqa

        self.setContentsMargins(5, 0, 5, 0)
        screen_size = QtWidgets.QApplication.primaryScreen().size()
        self.setMaximumSize(screen_size)

        self.search_box = SearchBox(self.content_form, self.table_widget)   # noqa
        self.log_window = self.content_form.findChild(QPlainTextEdit, "log_window")

        self.data = list()
        self.root_url = None
        self.lecture_slides_mapping = dict()

    def setup(self):
        pass

    def keyPressEvent(self, e):
        # TODO: this can be moved to search class.
        if e.key() == QtCore.Qt.Key_Enter or e.key() == QtCore.Qt.Key_Return:
            self.search_box.search_next()
        elif e.key() == QtCore.Qt.Key_G and (e.modifiers() & QtCore.Qt.ShiftModifier) \
                and (e.modifiers() & QtCore.Qt.ControlModifier):
            self.search_box.search_prev()
        elif e.key() == QtCore.Qt.Key_G and (e.modifiers() & QtCore.Qt.ControlModifier):
            self.search_box.search_next()

    def work_offline(self):
        offline_data = Finder().get_offline_content()
        self.table_container.fill_table(offline_data)

        Callbacks().set_menu_statuses()
        Callbacks().set_pushbutton_statuses()

    def work_online(self):
        online_data_gen = self.impartus.get_online_lectures()
        offline_data = Finder().get_offline_content()

        self.table_container.fill_table(offline_data, online_data_gen)

        Callbacks().set_menu_statuses()
        Callbacks().set_pushbutton_statuses()

    def needs_lecture_rename(self):     # noqa
        return False

    def needs_video_download(self):     # noqa
        return False

    def needs_chat_download(self):      # noqa
        return False

    def needs_backpack_slides_download(self):   # noqa
        return False

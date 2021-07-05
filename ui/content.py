import os
import platform

from PySide2 import QtCore
from PySide2.QtWidgets import QMainWindow, QWidget, QVBoxLayout

from lib.config import Config, ConfigType
from lib.finder import Finder
from lib.impartus import Impartus
from lib.utils import Utils
from ui.data.callbacks import Callbacks
from ui.data.labels import Labels
from ui.search import SearchBox
from ui.table import Table


class ContentWindow(QMainWindow):
    """
    Content Window - provides a QTableWidget for displaying content, a search box for searching through the content.
    Also maintains a copy of the data obtained from the online and offline workflows and responsible for merging the
    two.
    """

    def __init__(self, impartus: Impartus):
        QMainWindow.__init__(self, None)
        self.impartus = impartus
        self._set_window_properties()
        self.search_box = SearchBox(self)

        self.table_container = Table(self.impartus)
        self.table_widget = self.table_container.add_table()
        self.offline_data = None
        self.online_data = None
        self.root_url = None
        self.lecture_slides_mapping = dict()

    def _set_window_properties(self):
        # full screen
        self.setGeometry(0, 0, self.maximumWidth(), self.maximumHeight())
        # window title
        self.setWindowTitle(Labels.APPLICATION_TITLE.value)

    def set_layout(self):
        # create a vbox layout and add search button, table to it.
        vcontainer_widget = QWidget()
        vbox_layout = QVBoxLayout(vcontainer_widget)

        search_lineedit = self.search_box.add_search_box()
        vbox_layout.addWidget(search_lineedit)
        vbox_layout.addWidget(self.table_widget)
        self.setCentralWidget(vcontainer_widget)

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
        self.offline_data = Finder().get_offline_content()
        self.table_container.fill_table(self.offline_data)
        self.search_box.set_table_widget_to_search(self.table_widget)

        Callbacks().set_menu_statuses()
        Callbacks().set_pushbutton_statuses()

    def work_online(self):
        self.online_data = self.impartus.get_online_lectures()
        self.save_metadata(self.online_data)

        self.offline_data = Finder().get_offline_content()

        # merge the two..
        for ttid, offline_item in self.offline_data.items():
            if self.online_data.get(ttid):
                self.online_data[ttid] = self.merge_items(offline_item, self.online_data[ttid])
            else:
                self.online_data[ttid] = offline_item

        self.table_container.fill_table(self.online_data)
        self.search_box.set_table_widget_to_search(self.table_widget)

        Callbacks().set_menu_statuses()
        Callbacks().set_pushbutton_statuses()

    def save_metadata(self, online_data):   # noqa
        # TODO: move elsewhere.
        conf = Config.load(ConfigType.IMPARTUS)
        if conf.get('config_dir') and conf.get('config_dir').get(platform.system()) \
                and conf.get('save_offline_lecture_metadata'):
            folder = conf['config_dir'][platform.system()]
            os.makedirs(folder, exist_ok=True)
            for ttid, item in online_data.items():
                filepath = os.path.join(folder, '{}.json'.format(ttid))
                if not os.path.exists(filepath):
                    Utils.save_json(item, filepath)

    def merge_items(self, offline_item, online_item):   # noqa
        for key, val in offline_item.items():
            if not online_item.get(key):
                online_item[key] = offline_item[key]
        return online_item

    def needs_lecture_rename(self):
        return False

    def needs_video_download(self):
        return False

    def needs_chat_download(self):
        return False

    def needs_backpack_slides_download(self):
        return False

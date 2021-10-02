import math

from PySide2 import QtCore, QtWidgets
from PySide2.QtCore import QFile, QObject, Qt
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QMainWindow, QTableWidget, QPlainTextEdit, QTreeWidget, QTabWidget, QLabel, QProgressBar

from lib.finder import Finder
from lib.core.impartus import Impartus
from ui.callbacks.buttoncallbacks import ButtonCallbacks
from ui.callbacks.menucallbacks import MenuCallbacks
from lib.data.labels import Labels
from ui.callbacks.utils import CallbackUtils
from ui.helpers.datautils import DataUtils
from ui.splash import SplashScreen
from ui.uiitems.search import SearchBox
from ui.uiitems.videos import Videos
from ui.uiitems.documents import Documents


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
        self.table_widget: QTableWidget
        self.videos_tab = Videos(self.table_widget, self.impartus)

        self.tree_widget = self.content_form.findChild(QTreeWidget, "lectures_treewidget")
        self.tree_widget: QTreeWidget
        self.documents_tab = Documents(self.tree_widget, self.impartus)

        # events for tab switch
        self.tab_widget = self.content_form.findChild(QTabWidget, "tab_widget")
        self.tab_widget: QTabWidget
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.currentChanged.connect(self.on_click_tab_change)

        self.setContentsMargins(5, 0, 5, 0)
        screen_size = QtWidgets.QApplication.primaryScreen().size()
        self.setMaximumSize(screen_size)

        # type hints
        self.table_widget: QTableWidget
        self.tree_widget: QTreeWidget
        self.search_box = SearchBox(self.content_form, self.table_widget, self.tree_widget)
        self.log_window = self.content_form.findChild(QPlainTextEdit, "log_window")

        self.data = list()
        self.root_url = None
        self.lecture_slides_mapping = dict()
        self.splashscreen = SplashScreen(self)

    def setup(self):
        pass

    def on_click_tab_change(self, index: int):
        tabs = {0: 'Video', 1: 'Slides'}
        for i, tab_name in tabs.items():
            menu_item = CallbackUtils().content_window.menuBar().findChild(QObject, tab_name)
            if i == index:
                MenuCallbacks().enable_menu_items(menu_item)
            else:
                MenuCallbacks().disable_menu_items(menu_item)

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
        self.splashscreen.show(widgets_to_disable=[self.table_widget, self.tree_widget])
        self.reset_content()
        count = 0
        for rf_id, video_metadata, is_flipped, chats_path in Finder().get_offline_videos():
            self.videos_tab.table.add_row_item(rf_id, video_metadata, captions_path=chats_path, is_flipped=is_flipped,
                                               video_downloaded=True)
            count += 1
            self.splashscreen.setText("Found {} offline videos.".format(count))

        # when scanning offline documents, we get 1 document at a time, and identify it's subject (metadata)
        count = 0
        for subject, document in Finder().get_offline_backpack_slides():
            self.documents_tab.tree.add_row_items(subject, [document])
            count += 1
            self.splashscreen.setText("Found {} offline documents.".format(count))

        MenuCallbacks().set_menu_statuses()
        ButtonCallbacks().set_pushbutton_statuses()
        self.splashscreen.hide(widgets_to_enable=[self.table_widget, self.tree_widget])

    def reset_content(self):
        self.videos_tab.reset_content()
        self.documents_tab.reset_content()

    def work_online(self):
        self.splashscreen.show(widgets_to_disable=[self.table_widget, self.tree_widget])
        self.reset_content()

        subjects = self.impartus.get_subjects()
        mapping_by_id, mapping_by_name = DataUtils.get_subject_mappings(subjects)

        # videos tab
        count = 0
        for video_id, video_metadata, is_flipped in self.impartus.get_lecture_videos(subjects):
            # for online videos, we won't know if lecture chats exist or not, until the api is called,
            # so consider caption_path=False (not downloaded) and enable the chat download button.
            self.videos_tab.table.add_row_item(video_id, video_metadata, is_flipped=is_flipped, captions_path=False)
            count += 1
            self.splashscreen.setText("Found {} online videos.".format(count))

        for (video_id, video_metadata, is_flipped, chats_path) in Finder().get_offline_videos():
            self.videos_tab.table.add_row_item(video_id, video_metadata, captions_path=chats_path,
                                               is_flipped=is_flipped, video_downloaded=True)

        self.videos_tab.table.post_fill_tasks()

        # when fetching online documents, the api returns all the available documents (metadata) for a given subject.
        count = 0
        for subject_metadata, documents in self.impartus.get_slides(subjects):
            self.documents_tab.tree.add_row_items(subject_metadata, documents)
            count += len(documents)
            self.splashscreen.setText("Found {} online documents.".format(count))

        # when scanning offline documents, we get 1 document at a time, and identify it's subject (metadata).
        for subject_metadata, document in Finder().get_offline_backpack_slides(mapping_by_name):
            self.documents_tab.tree.add_row_items(subject_metadata, [document])

        MenuCallbacks().set_menu_statuses()
        ButtonCallbacks().set_pushbutton_statuses()

        self.splashscreen.hide(widgets_to_enable=[self.table_widget, self.tree_widget])

    @staticmethod
    def needs_lecture_rename():
        return True

    @staticmethod
    def needs_video_download():
        return True

    @staticmethod
    def needs_chat_download():
        return True

    @staticmethod
    def needs_backpack_slides_download():
        return True

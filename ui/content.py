from PySide2 import QtCore, QtWidgets
from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QMainWindow, QTableWidget, QPlainTextEdit, QTreeWidget

from lib.finder import Finder
from lib.core.impartus import Impartus
from ui.callbacks.buttoncallbacks import ButtonCallbacks
from ui.callbacks.menucallbacks import MenuCallbacks
from lib.data.labels import Labels
from ui.helpers.datautils import DataUtils
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
        self.table_container = Videos(self.impartus, self.table_widget)  # noqa

        self.tree_widget = self.content_form.findChild(QTreeWidget, "lectures_treewidget")
        self.tree_container = Documents(self.impartus, self.tree_widget)  # noqa

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
        offline_video_data = Finder().get_offline_videos()
        self.table_container.fill_table(offline_video_data)

        offline_backpack_slides = Finder().get_offline_backpack_slides()
        self.tree_container.fill_table(offline_backpack_slides)

        MenuCallbacks().set_menu_statuses()
        ButtonCallbacks().set_pushbutton_statuses()

    def work_online(self):
        subjects = self.impartus.get_subjects()
        mapping_by_id, mapping_by_name = self.get_subject_mappings(subjects)

        # videos tab
        regular_videos, flipped_videos = self.impartus.get_lecture_videos(subjects)
        offline_video_data = Finder().get_offline_videos()
        merged_video_data = DataUtils.merge_items(offline_video_data, {**regular_videos, **flipped_videos})
        DataUtils.save_metadata(merged_video_data)
        self.table_container.fill_table(offline_video_data, merged_video_data)

        # slides tab
        online_backpack_docs = self.impartus.get_slides(subjects)
        online_backpack_docs = self.subject_id_to_subject_name(online_backpack_docs, mapping_by_id)
        offline_backpack_docs = Finder().get_offline_backpack_slides(mapping_by_name)

        merged_slides_data = DataUtils.merge_slides_items(offline_backpack_docs, online_backpack_docs, mapping_by_id)
        self.tree_container.fill_table(merged_slides_data)

        MenuCallbacks().set_menu_statuses()
        ButtonCallbacks().set_pushbutton_statuses()

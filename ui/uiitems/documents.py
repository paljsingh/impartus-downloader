import shutil
from functools import partial

from PySide2.QtCore import QThread
from PySide2.QtWidgets import QFileDialog, QTreeWidget

from lib.config import Config, ConfigType
from lib.core.impartus import Impartus
from lib.data.labels import Labels
from lib.threadlogging import ThreadLogger
from lib.utils import Utils
from lib.data.actionitems import ActionItems
from lib.data.columns import Columns
from ui.helpers.worker import Worker
from ui.uiitems.tree import Tree


class Documents:
    """
    LectureContent class:
    Creates a treeview and provides methods to get / set treewidget headers and its properties,
    also the treewidget data.
    """

    def __init__(self, treewidget: QTreeWidget, impartus: Impartus):
        self.impartus = impartus
        self.conf = Config.load(ConfigType.IMPARTUS)
        self.workers = dict()
        self.logger = ThreadLogger(self.__class__.__name__).logger
        self.data = None

        # video actions
        self.callbacks = {
            Labels.DOCUMENT__DOWNLOAD_DOCUMENT.value: partial(self.on_click_download_document),
            Labels.DOCUMENT__OPEN_DOCUMENT.value: partial(self.on_click_open_document),
            Labels.DOCUMENT__OPEN_FOLDER.value: partial(self.on_click_open_folder),
            Labels.DOCUMENT__ATTACH_DOCUMENT.value: partial(self.on_click_attach_slides),
        }

        # construct treeview
        self.tree = Tree(treewidget, self.impartus, self.callbacks)

    def reset_content(self):
        self.data = None
        self.tree.reset_content()

    def _download_document(self, file_url: str, filepath: str):
        """
        Download a slide doc in a thread. Update the UI upon completion.
        """
        # create a new Impartus session reusing existing token.
        imp = Impartus(self.impartus.token)
        return imp.download_slides(file_url, filepath)

    def on_click_download_document(self, index, subject, metadata ):  # noqa
        """
        callback function for Download button.
        Creates a thread to download the request video.
        """

        document_index = metadata.get('seqNo') - 1
        slide_url = metadata.get('fileUrl')
        filepath = Utils.get_documents_path(metadata)

        doc_col = Columns.get_document_column_index_by_key(Labels.DOCUMENT__ACTIONS.value)
        tree_widget_item = self.tree.treewidget.topLevelItem(index).child(document_index)

        dd_col = ActionItems.get_action_item_index(
            Labels.DOCUMENT__ACTIONS.value, Labels.DOCUMENT__DOWNLOAD_DOCUMENT.value)
        dd_button = self.tree.treewidget.itemWidget(tree_widget_item, doc_col).layout().itemAt(dd_col).widget()

        od_col = ActionItems.get_action_item_index(
            Labels.DOCUMENT__ACTIONS.value, Labels.DOCUMENT__OPEN_DOCUMENT.value)
        od_button = self.tree.treewidget.itemWidget(tree_widget_item, doc_col).layout().itemAt(od_col).widget()

        of_col = ActionItems.get_action_item_index(
            Labels.DOCUMENT__ACTIONS.value, Labels.DOCUMENT__OPEN_FOLDER.value)
        of_button = self.tree.treewidget.itemWidget(tree_widget_item, doc_col).layout().itemAt(of_col).widget()

        ad_col = ActionItems.get_action_item_index(
            Labels.DOCUMENT__ACTIONS.value, Labels.DOCUMENT__ATTACH_DOCUMENT.value)
        ad_button = self.tree.treewidget.itemWidget(tree_widget_item, doc_col).layout().itemAt(ad_col).widget()

        pushbuttons = {
            'download_doc': dd_button,
            'open_doc': od_button,
            'open_folder': of_button,
            'attach_doc': ad_button,
        }
        dd_button.setEnabled(False)

        thread = Worker()
        thread.set_task(partial(self._download_document, slide_url, filepath))
        thread.finished.connect(partial(self.thread_finished, pushbuttons, filepath))

        self.workers[filepath] = {
            'pushbuttons': pushbuttons,
            'thread':   thread,
        }

        thread.start(priority=QThread.Priority.IdlePriority)


    def thread_finished(self, pushbuttons, filepath):     # noqa
        if self.workers.get(filepath):
            # successful run.
            return_status = self.workers[filepath]['thread'].status
            if return_status:
                pushbuttons['open_doc'].setEnabled(True)
                pushbuttons['open_folder'].setEnabled(True)
                pushbuttons['attach_doc'].setEnabled(True)
                pushbuttons['download_doc'].setEnabled(False)
            else:
                try:
                    pushbuttons['open_doc'].setEnabled(False)
                    pushbuttons['open_folder'].setEnabled(False)
                    pushbuttons['attach_doc'].setEnabled(False)
                    pushbuttons['download_doc'].setEnabled(True)
                except RuntimeError as ex:
                    self.logger.error("Error in downloading document: {}".format(ex))
                    pass
            del self.workers[filepath]



    def on_click_open_document(self, file_path: str):
        Utils.open_file(file_path)

    def on_click_open_folder(self, folder_path: str):
        Utils.open_file(folder_path)

    def on_click_attach_slides(self, folder_path: str):
        conf = Config.load(ConfigType.IMPARTUS)
        filters = ['{} files (*.{})'.format(str(x).title(), x) for x in conf.get('allowed_ext')]
        filters_str = ';;'.join(filters)
        filepaths = QFileDialog().getOpenFileNames(
            None,
            caption="Select files to attach...",
            dir=folder_path,
            filter=filters_str
        )
        if not filepaths:
            return

        for filepath in filepaths[0]:
            dest_path = shutil.copy(filepath, folder_path)
            # ss_combobox.add_items([dest_path])

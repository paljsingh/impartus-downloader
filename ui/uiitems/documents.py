import concurrent
import shutil
import concurrent.futures
from functools import partial

from PySide2.QtWidgets import QFileDialog, QTreeWidget

from lib.config import Config, ConfigType
from lib.core.impartus import Impartus
from lib.threadlogging import ThreadLogger
from lib.utils import Utils
from lib.data.actionitems import ActionItems
from lib.data.columns import Columns
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
        callbacks = {
            'download_slides': partial(self.on_click_download_slides),
            'attach_slides': partial(self.on_click_attach_slides),
            'open_folder': partial(self.on_click_open_folder)
        }
        self.tree = Tree(treewidget, self.impartus, callbacks)

    def reset_content(self):
        self.data = None
        self.tree.reset_content()

    def _download_slides(self, rf_id: int, slide_url: str, filepath: str):
        """
        Download a slide doc in a thread. Update the UI upon completion.
        """
        # create a new Impartus session reusing existing token.
        imp = Impartus(self.impartus.token)
        if imp.download_slides(rf_id, slide_url, filepath):
            return True
        else:
            self.logger.error('Error', 'Error downloading slides.')
            return False

    def on_click_download_slides(self, metadata):  # noqa
        """
        callback function for Download button.
        Creates a thread to download the request video.
        """
        # metadata = self.data.get(rf_id)
        slide_url = metadata.get('slide_url')
        filepath = Utils.get_slides_path(metadata)

        # row = self.get_row_from_rfid(rf_id)
        col = Columns.get_column_index_by_key('slides_actions')
        ds_field = ActionItems.get_action_item_index('slides_actions', 'download_slides')
        # ds_button = self.treewidget.cellWidget(row, col).layout().itemAt(ds_field).widget()

        of_field = ActionItems.get_action_item_index('slides_actions', 'open_folder')
        # of_button = self.treewidget.cellWidget(row, col).layout().itemAt(of_field).widget()

        ss_field = ActionItems.get_action_item_index('slides_actions', 'show_slides')
        # ss_combo = self.treewidget.cellWidget(row, col).layout().itemAt(ss_field).widget()

        as_field = ActionItems.get_action_item_index('slides_actions', 'attach_slides')
        # as_button = self.treewidget.cellWidget(row, col).layout().itemAt(as_field).widget()

        # widgets = {
        #     'download_slides': ds_button,
        #     'open_folder': of_button,
        #     'show_slides': ss_combo,
        #     'attach_slides': as_button,
        # }
        # ds_button.setEnabled(False)
        with concurrent.futures.ThreadPoolExecutor(3) as executor:
            future = executor.submit(self._download_slides, slide_url, filepath)
            return_value = future.result()

            # if return_value:
            #     # add new slides file to the existing list.
            #     if not self.data[rf_id].get('backpack_slides'):
            #         self.data[rf_id]['backpack_slides'] = list()
            #     self.data.get(rf_id)['backpack_slides'].append(filepath)
            #
            #     widgets['show_slides'].add_items([filepath])
            #     widgets['open_folder'].setEnabled(True)
            #     widgets['attach_slides'].setEnabled(True)
            # else:
            #     widgets['download_slides'].setEnabled(True)

    def on_click_open_folder(self, folder_path: str):
        # folder_path = self.get_folder_from_rfid(rf_id)
        Utils.open_file(folder_path)

    def on_click_attach_slides(self, folder_path: str):
        # folder_path = self.get_folder_from_rfid(rf_id)
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

        # row = self.get_row_from_rfid(rf_id)
        # col = Columns.get_column_index_by_key('slides_actions')
        # ss_field = ActionItems.get_action_item_index('slides_actions', 'show_slides')
        # ss_combobox = self.treewidget.cellWidget(row, col).layout().itemAt(ss_field).widget()

        for filepath in filepaths[0]:
            dest_path = shutil.copy(filepath, folder_path)
            # ss_combobox.add_items([dest_path])

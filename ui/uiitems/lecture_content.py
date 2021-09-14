import concurrent
import os
import shutil
from functools import partial
import concurrent.futures


from PySide2 import QtCore
from PySide2.QtWidgets import QTreeWidget, QTreeWidgetItem, QHeaderView, QFileDialog, QCheckBox

from lib.config import Config, ConfigType
from lib.core.impartus import Impartus
from lib.threadlogging import ThreadLogger
from lib.utils import Utils
from ui.callbacks.menucallbacks import MenuCallbacks
from ui.callbacks.utils import CallbackUtils
from ui.data.actionitems import ActionItems
from ui.data.columns import Columns
from ui.delegates.rodelegate import ReadOnlyDelegate
from ui.delegates.writedelegate import WriteDelegate
from ui.uiitems.customwidgets.customtreewidgetitem import CustomTreeWidgetItem
from ui.uiitems.customwidgets.tablewidgetitem import CustomTableWidgetItem
from ui.uiitems.slide_items import Slides


class LectureContent:
    """
    LectureContent class:
    Creates a treeview and provides methods to get / set treewidget headers and its properties,
    also the treewidget data.
    """

    def __init__(self, impartus: Impartus, treewidget: QTreeWidget):
        self.signal_connected = False
        self.workers = dict()
        self.conf = Config.load(ConfigType.IMPARTUS)
        self.impartus = impartus

        self.readonly_delegate = ReadOnlyDelegate()
        self.write_delegate = WriteDelegate(self.get_data)
        self.logger = ThreadLogger(self.__class__.__name__).logger

        self.treewidget = treewidget
        self.treewidget.setAlternatingRowColors(True)
        self.treewidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        self.data = dict()
        self.prev_checkbox = None

    def get_data(self):
        return self.data

    def _set_headers(self):
        self.treewidget.header().setAlternatingRowColors(True)
        headers = [x['display_name'] for x in {**Columns.slides_data_columns, **Columns.slides_widget_columns}.values()]
        self.treewidget.setHeaderLabels(headers)
        self.treewidget.header().setSortIndicatorShown(True)
        return self

    def set_row_content(self, documents_by_subjects):
        # if we have generator for fetching online data
        # pick one item at a time, merge it with offline data item if present (that gives you it's offline location,
        # attached slides and chats location etc.
        # Later, add any remaining offline videos (which might have been downloaded from other sources, or
        # the ones that may not be accessible online any more.)
        index = 0
        for subject_name, documents in documents_by_subjects.items():
            item = QTreeWidgetItem(self.treewidget)
            item.setText(0, subject_name)
            item.setTextAlignment(0, QtCore.Qt.AlignmentFlag.AlignTop)
            self.treewidget.addTopLevelItem(item)

            for document in documents:
                self.add_row_item(item, document)
            index += 1

    def add_row_item(self, item, document):
        item_child = QTreeWidgetItem(item)
        for col, key in enumerate([x for x in Columns.slides_data_columns.keys()][1:], 1):
            item_child.setText(col, str(document.get(key)))
        item.addChild(item_child)

        # total columns so far...
        col = len(Columns.slides_data_columns)

        # slides actions
        callbacks = {
            'download_slides': partial(self.on_click_download_slides, document['filePath']),
            'open_folder': partial(self.on_click_open_folder, document['filePath']),
            'attach_slides': partial(self.on_click_attach_slides, document['filePath']),
        }
        slides_actions_widget, cell_value = Slides.add_slides_actions_buttons(document, self.impartus, callbacks)

        # custom_item = QTreeWidgetItem()
        # custom_item.setData(cell_value)
        # numeric sort implemented via a Custom QTableWidgetItem
        custom_item = CustomTreeWidgetItem()
        custom_item.setValue(cell_value)
        self.treewidget.setItemWidget(item_child, col, slides_actions_widget)
        CallbackUtils().processEvents()

    def resizable_headers(self):
        # Todo ...
        for i, (col, item) in enumerate([*Columns.slides_data_columns.items(), *Columns.slides_widget_columns.items()], 1):
            if item.get('initial_size') and item['resize_policy'] != QHeaderView.ResizeMode.Stretch:
                self.treewidget.header().resizeSection(i, item.get('initial_size'))

        for i in range(len(['id', *Columns.slides_data_columns, *Columns.slides_widget_columns])):
            self.treewidget.header().setSectionResizeMode(i, QHeaderView.Interactive)

    def on_click_checkbox(self, checkbox: QCheckBox):
        if self.prev_checkbox and self.prev_checkbox != checkbox:
            self.prev_checkbox.setChecked(False)
        self.prev_checkbox = checkbox
        MenuCallbacks().set_menu_statuses()

    def show_hide_column(self, column):
        col_index = None
        for i, col_name in enumerate([*Columns.slides_data_columns.keys(), *Columns.slides_widget_columns.keys()], 1):
            if col_name == column:
                col_index = i
                break

        if self.treewidget.isColumnHidden(col_index):
            self.treewidget.setColumnHidden(col_index, False)
        else:
            self.treewidget.setColumnHidden(col_index, True)

    def fill_table(self, items):
        # clear does not reset the table size, do it explicitly.
        self.treewidget.setSortingEnabled(False)
        self.treewidget.clear()

        col_count = len(Columns.slides_data_columns.keys()) + len(Columns.slides_widget_columns) + 1
        self.treewidget.setColumnCount(col_count)

        # self.prev_checkbox = None

        self._set_headers()

        self.set_row_content(items)
        self.resizable_headers()
        self.treewidget.setSortingEnabled(True)

        # show most recent lectures first.
        self.treewidget.sortByColumn(
            Columns.get_column_index_by_key('startDate'), QtCore.Qt.SortOrder.DescendingOrder)

    def set_button_state(self, row: int, action_item: str, field: str, status: bool):
        col_index = Columns.get_column_index_by_key(action_item)
        field_index = ActionItems.get_action_item_index(action_item, field)
        self.treewidget.cellWidget(row, col_index).layout().itemAt(field_index).widget().setEnabled(status)

    """
    Slides.
    """

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

    def on_click_download_slides(self, rf_id: int):  # noqa
        """
        callback function for Download button.
        Creates a thread to download the request video.
        """
        metadata = self.data.get(rf_id)
        slide_url = metadata.get('slide_url')
        filepath = self.impartus.get_slides_path(metadata)

        row = self.get_row_from_rfid(rf_id)
        col = Columns.get_column_index_by_key('slides_actions')
        ds_field = ActionItems.get_action_item_index('slides_actions', 'download_slides')
        ds_button = self.treewidget.cellWidget(row, col).layout().itemAt(ds_field).widget()

        of_field = ActionItems.get_action_item_index('slides_actions', 'open_folder')
        of_button = self.treewidget.cellWidget(row, col).layout().itemAt(of_field).widget()

        ss_field = ActionItems.get_action_item_index('slides_actions', 'show_slides')
        ss_combo = self.treewidget.cellWidget(row, col).layout().itemAt(ss_field).widget()

        as_field = ActionItems.get_action_item_index('slides_actions', 'attach_slides')
        as_button = self.treewidget.cellWidget(row, col).layout().itemAt(as_field).widget()

        widgets = {
            'download_slides': ds_button,
            'open_folder': of_button,
            'show_slides': ss_combo,
            'attach_slides': as_button,
        }
        ds_button.setEnabled(False)
        with concurrent.futures.ThreadPoolExecutor(3) as executor:
            future = executor.submit(self._download_slides, rf_id, slide_url, filepath)
            return_value = future.result()

            if return_value:
                # add new slides file to the existing list.
                if not self.data[rf_id].get('backpack_slides'):
                    self.data[rf_id]['backpack_slides'] = list()
                self.data.get(rf_id)['backpack_slides'].append(filepath)

                widgets['show_slides'].add_items([filepath])
                widgets['open_folder'].setEnabled(True)
                widgets['attach_slides'].setEnabled(True)
            else:
                widgets['download_slides'].setEnabled(True)

    def on_click_open_folder(self, rf_id: int):     # noqa
        folder_path = self.get_folder_from_rfid(rf_id)
        Utils.open_file(folder_path)

    def on_click_attach_slides(self, rf_id: int):       # noqa
        folder_path = self.get_folder_from_rfid(rf_id)
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

        row = self.get_row_from_rfid(rf_id)
        col = Columns.get_column_index_by_key('slides_actions')
        ss_field = ActionItems.get_action_item_index('slides_actions', 'show_slides')
        ss_combobox = self.treewidget.cellWidget(row, col).layout().itemAt(ss_field).widget()

        for filepath in filepaths[0]:
            dest_path = shutil.copy(filepath, folder_path)
            ss_combobox.add_items([dest_path])

    #
    # """
    # MISC
    # """
    def get_selected_row(self):
        for i in range(self.treewidget.rowCount()):
            if self.treewidget.cellWidget(i, 0).layout().itemAt(0).widget().isChecked():
                return i

    def get_selected_row_rfid(self):
        """
        Return ttid or fcid, whichever applicable, also return a flag 'flipped'=True if it is a flipped lecture.
        """
        row_index = self.get_selected_row()
        if row_index is None:
            return None, False

        ttid_col = Columns.get_column_index_by_key('ttid')
        if ttid_col:
            ttid = self.treewidget.item(row_index, ttid_col).text()
            if ttid:
                return int(ttid), False

        fcid_col = Columns.get_column_index_by_key('fcid')
        if fcid_col:
            fcid = self.treewidget.item(row_index, fcid_col).text()
            if fcid:
                return int(fcid), True

        return None, False

    def get_row_from_rfid(self, rf_id: int, flipped=False):
        if flipped:
            fcid_col_index = Columns.get_column_index_by_key('fcid')
            for i in range(self.treewidget.rowCount()):
                if int(self.treewidget.item(i, fcid_col_index).text()) == rf_id:
                    return i
        else:
            ttid_col_index = Columns.get_column_index_by_key('ttid')
            for i in range(self.treewidget.rowCount()):
                if int(self.treewidget.item(i, ttid_col_index).text()) == rf_id:
                    return i

    def get_folder_from_rfid(self, rf_id: int):
        video_path = self.data.get(rf_id)['offline_filepath'] if self.data.get(rf_id).get('offline_filepath') else None
        if video_path:
            return os.path.dirname(video_path)
        slides_path = self.data.get(rf_id)['backpack_slides'][0]\
            if self.data.get(rf_id).get('backpack_slides') else None
        if slides_path:
            return os.path.dirname(slides_path)
        captions_path = self.data.get(rf_id)['captions_path'] if self.data.get(rf_id).get('captions_path') else None
        if captions_path:
            return os.path.dirname(captions_path)

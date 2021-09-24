import os
from functools import partial
from typing import Dict
from PySide2 import QtCore
from PySide2.QtWidgets import QHeaderView, QWidget, QTreeWidget, QTreeWidgetItem

from lib.config import Config, ConfigType
from lib.core.impartus import Impartus
from lib.data import columns
from lib.data.labels import Labels
from lib.threadlogging import ThreadLogger
from lib.utils import Utils
from lib.variables import Variables
from ui.callbacks.utils import CallbackUtils
from ui.helpers.widgetcreator import WidgetCreator
from ui.uiitems.customwidgets.customtreewidgetitem import CustomTreeWidgetItem
from lib.data.actionitems import ActionItems
from lib.data.columns import Columns


class Tree:
    """
    Trre class:
    Creates a table and provides methods to get / set table headers and its properties, as well as the table data..
    Also own the handler methods called by the widgets contained in the table.

    The handler methods defined here can/should be reused by the menu items event handlers (defined in callbacks.py).
    Except for the difference that,
    while the table class widgets have the required video / slides / captions available to them when creating the
    widgets, the menu items handler first need to collect this info from the currently selected row / content
    and then pass on that info to the handlers defined in this class.
    """

    def __init__(self, treewidget: QTreeWidget, impartus: Impartus, callbacks):
        self.signal_connected = False
        self.conf = Config.load(ConfigType.IMPARTUS)
        self.impartus = impartus
        self.callbacks = callbacks

        self.logger = ThreadLogger(self.__class__.__name__).logger

        self.treewidget = self.setup_tree(treewidget)
        self.documents = dict()
        self.items = dict()
        self.top_level_index = 0

    def reset_content(self):
        self.documents = dict()
        self.items = dict()
        self.top_level_index = 0
        self.treewidget = self.setup_tree(self.treewidget)

    def setup_tree(self, treewidget):
        treewidget.setSortingEnabled(False)
        treewidget.setAlternatingRowColors(True)
        treewidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        treewidget.clear()

        col_count = Columns.get_document_columns_count()
        treewidget.setColumnCount(col_count)

        treewidget = self._set_headers(treewidget)
        return treewidget

    def _set_headers(self, treewidget):
        treewidget.header().setAlternatingRowColors(True)
        headers = [x['display_name'] for x in Columns.get_document_columns_dict().values()]
        treewidget.setHeaderLabels(headers)
        treewidget.header().setSortIndicatorShown(True)
        return treewidget

    def new_root_subject_item(self, subject_name):
        item = QTreeWidgetItem(self.treewidget)
        item.setText(0, subject_name)
        item.setTextAlignment(0, QtCore.Qt.AlignmentFlag.AlignTop)
        self.items[subject_name] = {
            'index': len(self.items),
            'item': item,
        }
        self.treewidget.addTopLevelItem(item)
        return item

    def add_row_items(self, subject_metadata: Dict, documents: Dict, document_downloaded=False):

        subject_name = subject_metadata['subjectName']
        if not self.items.get(subject_name):
            self.new_root_subject_item(subject_name)

        item_info = self.items.get(subject_name)
        item = item_info['item']
        index = item_info['index']

        seq_no = item.childCount() + 1
        for document in documents:
            professor_name = document['createdBy']['fname'] \
                if document.get('createdBy') and document['createdBy'].get('fname') else '-'
            document['professorName'] = professor_name

            file_url = '{}/{}'.format(Variables().login_url(), document['filePath']) if document.get('filePath') else ''
            document['fileUrl'] = file_url

            if not document.get('ext'):
                document['ext'] = str.split(document['filePath'], '.')[-1]

            document['subjectNameShort'] = subject_name
            document['seqNo'] = seq_no
            if not document.get('offline_filepath'):
                document['offline_filepath'] = Utils.get_documents_path(document)

            self.add_row_item(index, item, document, subject_name, document_downloaded)
            seq_no += 1

            key = document.get('offline_filepath')
            self.documents[key] = {
                'subject_name': subject_name,
                'metadata': document,
                'root_widget': item,
            }

    def add_row_item(self, index, item, document, subject_name, downloaded=False):

        item_child = QTreeWidgetItem(item)
        for i, (key, val) in enumerate([x for x in columns.document_data_columns.items()][1:], 1):
            item_child.setText(i, str(document.get(key)))

        # total columns so far...
        col = len(columns.document_data_columns)

        slides_actions_widget, cell_value = self.add_slides_actions_buttons(index, subject_name, document)
        custom_item = CustomTreeWidgetItem()
        custom_item.setValue(cell_value)
        self.treewidget.setItemWidget(item_child, col, slides_actions_widget)

        item.addChild(item_child)

        CallbackUtils().processEvents()

    def resizable_headers(self):
        # Todo ...
        for i, (col, item) in enumerate(Columns.get_document_columns_dict().items()):
            if item.get('initial_size') and item['resize_policy'] != QHeaderView.ResizeMode.Stretch:
                self.treewidget.header().resizeSection(i, item.get('initial_size'))

        for i in range(Columns.get_document_columns_count()):
            self.treewidget.header().setSectionResizeMode(i, QHeaderView.Interactive)

    def show_hide_column(self, column):
        col_index = None
        for i, col_name in enumerate(Columns.get_document_columns(), 1):
            if col_name == column:
                col_index = i
                break

        if self.treewidget.isColumnHidden(col_index):
            self.treewidget.setColumnHidden(col_index, False)
        else:
            self.treewidget.setColumnHidden(col_index, True)

    def get_selected_row(self):
        for i in range(self.treewidget.rowCount()):
            if self.treewidget.cellWidget(i, 0).layout().itemAt(0).widget().isChecked():
                return i

    def add_slides_actions_buttons(self, index, subject, metadata: Dict):
        widget = QWidget()
        widget_layout = WidgetCreator.get_layout_widget(widget)
        widget_layout.setAlignment(columns.widget_columns.get('slides_actions')['alignment'])

        cell_value = ''
        for pushbutton in WidgetCreator.add_actions_buttons(ActionItems.slides_actions):
            widget_layout.addWidget(pushbutton)
            btn_type, btn_state = self.set_pushbutton_statuses(pushbutton, metadata, self.callbacks, index, subject)

            # a slightly hackish way to sort widgets -
            # create an integer out of the (slide count, button1_state, button2_state, ...)
            # pass it to a Custom TableWidgetItem with __lt__ overridden to provide numeric sort.
            cell_value = '{}{}'.format(cell_value, int(btn_state))

        return widget, int(cell_value)

    def set_pushbutton_statuses(self, pushbutton, metadata, callbacks, index=None, subject=None):
        filepath = metadata.get('offline_filepath')
        assert(filepath is not None)
        # slides download is enabled if the slides file exists on server, but not locally.
        if pushbutton.objectName() == ActionItems.slides_actions[Labels.DOCUMENT__DOWNLOAD_DOCUMENT.value]['text']:
            assert(index is not None)
            assert(subject is not None)
            btn_type = Labels.DOCUMENT__DOWNLOAD_DOCUMENT.value
            pushbutton.clicked.connect(partial(callbacks[Labels.DOCUMENT__DOWNLOAD_DOCUMENT.value],
                                               index, subject, metadata))

            if self.impartus.is_authenticated():
                file_url = metadata.get('fileUrl')
                if file_url and not os.path.exists(filepath):
                    btn_state = True
                else:
                    btn_state = False
            else:
                btn_state = False
        elif pushbutton.objectName() == ActionItems.slides_actions[Labels.DOCUMENT__OPEN_DOCUMENT.value]['text']:
            btn_type = Labels.DOCUMENT__OPEN_DOCUMENT.value
            pushbutton.clicked.connect(partial(self.callbacks[Labels.DOCUMENT__OPEN_DOCUMENT.value], filepath))

            # open document is enabled if the document file exists locally.
            if os.path.exists(filepath):
                btn_state = True
            else:
                btn_state = False
        elif pushbutton.objectName() == ActionItems.slides_actions[Labels.DOCUMENT__OPEN_FOLDER.value]['text']:
            btn_type = Labels.DOCUMENT__OPEN_FOLDER.value
            folder_path = os.path.dirname(filepath)
            pushbutton.clicked.connect(partial(self.callbacks[Labels.DOCUMENT__OPEN_FOLDER.value], folder_path))

            # open folder should be enabled, if folder exist

            if folder_path and os.path.exists(folder_path):
                btn_state = True
            else:
                btn_state = False
        elif pushbutton.objectName() == ActionItems.slides_actions[Labels.DOCUMENT__ATTACH_DOCUMENT.value]['text']:
            btn_type = Labels.DOCUMENT__ATTACH_DOCUMENT.value

            # attach slides is enabled, if at least one of the files exist.
            folder_path = os.path.dirname(filepath)
            pushbutton.clicked.connect(partial(self.callbacks[Labels.DOCUMENT__ATTACH_DOCUMENT.value], folder_path))

            if folder_path and os.path.exists(folder_path):
                btn_state = True
            else:
                btn_state = False
        else:
            btn_type = None
            btn_state = False
            assert False

        pushbutton.setEnabled(btn_state)
        return btn_type, btn_state

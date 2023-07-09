import os
from functools import partial
from pathlib import Path
from typing import Dict, List
from PySide2 import QtCore, QtWidgets
from PySide2.QtCore import QModelIndex
from PySide2.QtWidgets import QHeaderView, QWidget, QTreeWidget, QTreeWidgetItem
import re

from lib.config import Config, ConfigType
from lib.core.impartus import Impartus
from lib.data.Icons import DocumentIcons
from lib.data.labels import Labels
from lib.threadlogging import ThreadLogger
from lib.utils import Utils
from lib.variables import Variables
from ui.callbacks.menucallbacks import MenuCallbacks
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

        self.tree_widget = self.setup_tree(treewidget)
        self.tree_widget.selectionModel().currentChanged.connect(self.on_row_select)

        self.documents = dict()
        self.items = dict()
        self.top_level_index = 0
        self.selected = None

    def get_data(self):
        return self.documents

    def reset_content(self):
        self.documents = dict()
        self.items = dict()
        self.top_level_index = 0
        self.tree_widget.setSortingEnabled(False)
        self.tree_widget.clear()

    def setup_tree(self, treewidget):
        treewidget.setSortingEnabled(False)
        treewidget.setAlternatingRowColors(True)
        treewidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        treewidget.clear()

        col_count = len(Columns.get_document_columns())
        treewidget.setColumnCount(col_count)

        treewidget = self._set_headers(treewidget)

        # tree height/width adjustment
        app_width = QtWidgets.QApplication.primaryScreen().size().width()
        app_height = QtWidgets.QApplication.primaryScreen().size().height()
        tab_width = 20
        margin = 20

        log_window_height = 200
        search_window_height = 50
        splitter_height = 10

        treewidget_max_width = app_width - tab_width - 2*margin
        treewidget_max_height = app_height - log_window_height - search_window_height - splitter_height - 3*margin
        treewidget.setMaximumWidth(treewidget_max_width)
        treewidget.setMaximumHeight(treewidget_max_height)

        return treewidget

    def _set_headers(self, treewidget):     # noqa
        headers = [x['display_name'] for x in Columns.get_document_columns().values()]
        treewidget.setHeaderLabels(headers)

        for i, (key, val) in enumerate(Columns.get_document_columns().items()):
            if val.get('hidden'):
                treewidget.hideColumn(i)

            if val.get('initial_size') and val.get('resize_policy') != QHeaderView.ResizeMode.Stretch:
                treewidget.header().resizeSection(i, val.get('initial_size'))

        treewidget.header().setSortIndicatorShown(True)
        return treewidget

    def new_root_subject_item(self, subject_name):
        item = QTreeWidgetItem(self.tree_widget)
        item.setText(0, subject_name)
        item.setTextAlignment(0, QtCore.Qt.AlignmentFlag.AlignTop)
        self.items[subject_name] = {
            'index': len(self.items),
            'item': item,
        }
        self.tree_widget.addTopLevelItem(item)
        return item

    def add_row_items(self, subject_metadata: Dict, documents: Dict):

        # get top level tree item for this subject.
        subject_name = subject_metadata['subjectName']
        if not self.items.get(subject_name):
            self.new_root_subject_item(subject_name)

        item_info = self.items.get(subject_name)
        item = item_info['item']

        seq_no = item.childCount() + 1
        for document in documents:
            professor_name = document['createdBy']['fname'] \
                if document.get('createdBy') and document['createdBy'].get('fname') else '-'
            document['professorName'] = professor_name

            file_url = '{}/{}'.format(Variables().login_url(), document['filePath']) if document.get('filePath') else ''
            document['fileUrl'] = file_url

            if not document.get('ext'):
                document['ext'] = str.split(document['filePath'], '.')[-1]
            document['fileName'] = re.sub('.{}$'.format(re.escape(document['ext'])), '', document['fileName'])
            document['fileLengthKB'] = document['fileLength'] // 1024
            document['fileLengthMB'] = '{:.1f}'.format(document['fileLength'] / (1024 * 1024))

            document['subjectNameShort'] = subject_name
            document['seqNo'] = seq_no
            if not document.get('offline_filepath'):
                document['offline_filepath'] = Utils.get_documents_path(document)

            child_widget = self.add_row_item(item, document, subject_name)
            if child_widget:
                seq_no += 1

                key = document.get('offline_filepath')
                self.documents[key] = {
                    'subject': subject_name,
                    'metadata': document,
                    'widget': child_widget,
                }

    def post_fill_tasks(self):
        self._set_resizable_headers()

    def _set_resizable_headers(self):  # noqa
        self.tree_widget: QTreeWidget
        self.tree_widget.header().setStretchLastSection(False)
        self.tree_widget.header().setMinimumSectionSize(100)
        for i, (key, val) in enumerate(Columns.get_document_columns().items()):
            self.tree_widget.header().resizeSection(i, val.get('initial_size'))
            self.tree_widget.header().setSectionResizeMode(i, QHeaderView.ResizeMode.Interactive)
        self.tree_widget.collapseAll()

    def add_row_item(self, item_parent, document, subject_name):

        if self.documents.get(document['offline_filepath']):
            return
        else:
            item_child = QTreeWidgetItem(item_parent)

            for i, (key, val) in enumerate(Columns.get_document_data_columns().items()):
                if i == 0:
                    continue
                col_name = val['original_values_col'] if val.get('original_values_col') else key
                item_child.setText(i, str(document.get(col_name)))

            # total columns so far...
            col = len(Columns.get_document_data_columns())

            slides_actions_widget, cell_value = self.add_slides_actions_buttons(subject_name, document)
            custom_item = CustomTreeWidgetItem()
            custom_item.setValue(cell_value)
            self.tree_widget.setItemWidget(item_child, col, slides_actions_widget)

            item_parent.addChild(item_child)

            CallbackUtils().processEvents()
            return item_child

    def resizable_headers(self):
        # Todo ...
        for i, (col, item) in enumerate(Columns.get_document_columns().items()):
            if item.get('initial_size') and item['resize_policy'] != QHeaderView.ResizeMode.Stretch:
                self.tree_widget.header().resizeSection(i, item.get('initial_size'))

        for i in range(len(Columns.get_document_columns())):
            self.tree_widget.header().setSectionResizeMode(i, QHeaderView.Interactive)

    def show_hide_column(self, column):
        col_index = None
        for i, col_name in enumerate(Columns.get_document_columns(), 1):
            if col_name == column:
                col_index = i
                break

        if self.tree_widget.isColumnHidden(col_index):
            self.tree_widget.setColumnHidden(col_index, False)
        else:
            self.tree_widget.setColumnHidden(col_index, True)

    def get_selected_row(self):
        for i in range(self.tree_widget.rowCount()):
            if self.tree_widget.cellWidget(i, 0).layout().itemAt(0).widget().isChecked():
                return i

    def add_slides_actions_buttons(self, subject, metadata: Dict):
        widget = QWidget()
        widget_layout = WidgetCreator.get_layout_widget(widget)
        widget_layout.setAlignment(Columns.get_document_widget_columns().get('slides_actions')['alignment'])

        cell_value = ''
        # add pushbuttons grouped under a QWidget, assign a numeric cell_value to QWidget to enable sorting.
        for key, pushbutton in WidgetCreator.add_actions_buttons(ActionItems.slides_actions, metadata.get('ext')):
            widget_layout.addWidget(pushbutton)
            btn_type, btn_state = self.set_pushbutton_status(key, pushbutton, metadata, self.callbacks, widget, subject)

            # a slightly hackish way to sort widgets -
            # create an integer out of the (slide count, button1_state, button2_state, ...)
            # pass it to a Custom TableWidgetItem with __lt__ overridden to provide numeric sort.
            cell_value = '{}{}'.format(cell_value, int(btn_state))

        return widget, int(cell_value)

    def set_pushbutton_status(self, btn_type, pushbutton, metadata, callbacks, widget, subject=None):
        """
        Set pushbutton status
        """
        filepath = metadata.get('offline_filepath')
        assert(filepath is not None)

        # slides download is enabled if the slides file exists on server, but not locally.
        if btn_type == Labels.DOCUMENT__OPEN_DOCUMENT.value:
            pushbutton.clicked.connect(partial(self.callbacks[btn_type], filepath))
            # open document is enabled if the document file exists locally.
            if os.path.exists(filepath):
                btn_state = True
            else:
                btn_state = False
        elif btn_type == Labels.DOCUMENT__OPEN_FOLDER.value:
            folder_path = os.path.dirname(filepath)
            pushbutton.clicked.connect(partial(self.callbacks[btn_type], folder_path))

            # open folder should be enabled, if folder exist
            if folder_path and os.path.exists(folder_path):
                btn_state = True
            else:
                btn_state = False
        elif btn_type == Labels.DOCUMENT__ATTACH_DOCUMENT.value:
            # attach slides is enabled, if at least one of the files exist.
            folder_path = os.path.dirname(filepath)
            pushbutton.clicked.connect(partial(self.callbacks[btn_type], folder_path))

            if folder_path and os.path.exists(folder_path):
                btn_state = True
            else:
                btn_state = False
        elif btn_type == Labels.DOCUMENT__DOWNLOAD_DOCUMENT.value:
            assert(widget is not None)
            assert(subject is not None)
            pushbutton.clicked.connect(partial(callbacks[btn_type], subject, metadata, widget))

            if self.impartus.is_authenticated():
                file_url = metadata.get('fileUrl')
                if file_url and not os.path.exists(filepath):
                    btn_state = True
                else:
                    btn_state = False
            else:
                btn_state = False
        else:
            assert False

        pushbutton.setEnabled(btn_state)
        return btn_type, btn_state

    def on_row_select(self, selected: QModelIndex, deselected: QModelIndex):    # noqa
        self.tree_widget: QTreeWidget
        top_level_item = self.tree_widget.topLevelItem(selected.parent().row())
        widget_item = top_level_item.child(selected.row()) if top_level_item else None
        if not widget_item:
            self.selected = {}
            return

        key_col = Columns.get_document_column_index_by_key(Labels.DOCUMENT__OFFLINE_FILEPATH.value)
        document_key = widget_item.text(key_col)
        self.selected = self.documents.get(document_key)
        MenuCallbacks().set_menu_statuses()

    def auto_organize__post(self, commands: List):
        for cmd in commands:
            # only documents.
            if not cmd['source'].endswith('.mkv') and not cmd['source'].endswith('.vtt'):
                Utils.move_and_rename_file(cmd['source'], cmd['dest'])
                Utils.cleanup_dir(Path(cmd['source']).parent.absolute())

                # update in-memory metadata.
                if self.documents.get(cmd['source']):
                    self.documents[cmd['dest']] = self.documents.pop(cmd['source'])

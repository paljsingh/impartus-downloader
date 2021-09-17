import os
from functools import partial
from typing import Dict
from PySide2 import QtCore
from PySide2.QtWidgets import QHeaderView, QWidget, QTreeWidget, QTreeWidgetItem, QPushButton

from lib.config import Config, ConfigType
from lib.core.impartus import Impartus
from lib.data import columns
from lib.threadlogging import ThreadLogger
from lib.utils import Utils
from lib.variables import Variables
from ui.callbacks.utils import CallbackUtils
from ui.helpers.widgetcreator import WidgetCreator
from ui.uiitems.customwidgets.customtreewidgetitem import CustomTreeWidgetItem
from lib.data.actionitems import ActionItems
from lib.data.columns import Columns
from ui.delegates.writedelegate import WriteDelegate


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

        # self.write_delegate = WriteDelegate(self.get_data)
        self.logger = ThreadLogger(self.__class__.__name__).logger

        self.treewidget = self.setup_tree(treewidget)
        self.documents = dict()
        self.items = dict()

    def reset_content(self):
        self.documents = dict()
        self.items = dict()
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
        # professorName = subject_metadata['professorName']
        item = QTreeWidgetItem(self.treewidget)
        item.setText(0, subject_name)
        item.setTextAlignment(0, QtCore.Qt.AlignmentFlag.AlignTop)
        self.items[subject_name] = item
        self.treewidget.addTopLevelItem(item)
        return item

    def add_row_items(self, subject_metadata: Dict, documents: Dict, documents_downloaded=False):
        subject_name = subject_metadata['subjectName']
        item = self.items.get(subject_name)
        if not item:
            item = self.new_root_subject_item(subject_name)

        seq_no = item.childCount() + 1
        for document in documents:
            # document = DataUtils.subject_id_to_subject_name(document, mapping_by_id)
            professor_name = document['createdBy']['fname'] \
                if document.get('createdBy') and document['createdBy'].get('fname') else ''
            document['professorName'] = professor_name
            document['fileUrl'] = '{}/{}'.format(Variables().login_url(), document.get('filePath'))
            document['subjectNameShort'] = subject_name
            document['seqNo'] = seq_no
            document['ext'] = '.'.split(document['filePath'])[-1]
            self.add_row_item(item, document)
            seq_no += 1

    def add_row_item(self, item, document, downloaded=False):

        item_child = QTreeWidgetItem(item)
        for col, key in enumerate([x for x in Columns.get_document_columns()][1:], 1):
            item_child.setText(col, str(document.get(key)))
        item.addChild(item_child)

        # total columns so far...
        col = Columns.get_document_columns_count()

        slides_actions_widget, cell_value = self.add_slides_actions_buttons(document)

        custom_item = CustomTreeWidgetItem()
        custom_item.setValue(cell_value)
        self.treewidget.setItemWidget(item_child, col, slides_actions_widget)
        CallbackUtils().processEvents()

        self.set_pushbutton_statuses(slides_actions_widget, downloaded)

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

    def set_pushbutton_statuses(self, widget_group: QWidget, downloaded=False):
        download_doc_button = widget_group.layout().itemAt(0).widget()
        open_doc_button = widget_group.layout().itemAt(1).widget()

        download_doc_button: QPushButton
        open_doc_button: QPushButton
        if downloaded:
            download_doc_button.setEnabled(False)
            open_doc_button.setEnabled(True)
        else:
            download_doc_button.setEnabled(True)
            open_doc_button.setEnabled(False)

    def get_selected_row(self):
        for i in range(self.treewidget.rowCount()):
            if self.treewidget.cellWidget(i, 0).layout().itemAt(0).widget().isChecked():
                return i

    # def get_selected_row_rfid(self):
    #     """
    #     Return ttid or fcid, whichever applicable, also return a flag 'flipped'=True if it is a flipped lecture.
    #     """
    #     row_index = self.get_selected_row()
    #     if row_index is None:
    #         return None, False
    #
        # ttid_col = Columns.get_column_index_by_key('ttid')
        # if ttid_col:
        #     ttid = self.treewidget.item(row_index, ttid_col).text()
        #     if ttid:
        #         return int(ttid), False
        #
        # fcid_col = Columns.get_column_index_by_key('fcid')
        # if fcid_col:
        #     fcid = self.treewidget.item(row_index, fcid_col).text()
        #     if fcid:
        #         return int(fcid), True
        #
        # return None, False

    def add_slides_actions_buttons(self, metadata: Dict):
        widget = QWidget()
        widget_layout = WidgetCreator.get_layout_widget(widget)
        widget_layout.setAlignment(columns.widget_columns.get('slides_actions')['alignment'])

        # make the widget searchable based on button states.
        download_slides_state = None
        open_folder_state = None
        attach_slides_state = None

        # show slides combo box.
        # combo_box = CustomComboBox()
        # if metadata.get('backpack_slides'):
        #     combo_box.show()
        #     combo_box.add_items(metadata['backpack_slides'])
        #     combobox_count = combo_box.count() - 1
        # else:
        #     combo_box.hide()
        #     combobox_count = 0
        # widget_layout.addWidget(combo_box)

        filepath = metadata.get('filePath')
        folder_path = os.path.dirname(metadata.get('filePath'))
        file_url = metadata.get('fileUrl')
        # callbacks = {
        #     'download_video': partial(self.documents.on_click_attach_slides(filepath)),
        #     'play_video': partial(self.documents.on_click_open_folder(folder_path)),
        #     'download_chats': partial(self.documents.on_click_download_slides(file_url)),
        # }

        for pushbutton in WidgetCreator.add_actions_buttons(ActionItems.slides_actions):
            widget_layout.addWidget(pushbutton)

            # slides download is enabled if the slides file exists on server, but not locally.
            if pushbutton.objectName() == ActionItems.slides_actions['download_slides']['text']:
                pushbutton.clicked.connect(self.callbacks['download_slides'])

                if self.impartus.is_authenticated():
                    filepath = Utils.get_slides_path(metadata)
                    if metadata.get('slide_url') and metadata.get('slide_url') != '' \
                            and filepath and not os.path.exists(filepath):
                        download_slides_state = True
                    else:
                        download_slides_state = False
                else:
                    download_slides_state = False

                pushbutton.setEnabled(download_slides_state)

            # open folder should be enabled, if folder exist
            elif pushbutton.objectName() == ActionItems.slides_actions['open_folder']['text']:
                pushbutton.clicked.connect(partial(self.callbacks['open_folder'], folder_path))

                folder = None
                if metadata.get('offline_filepath'):
                    folder = os.path.dirname(metadata['offline_filepath'])
                elif metadata.get('backpack_slides'):
                    folder = os.path.dirname(metadata['backpack_slides'][0])

                if folder and os.path.exists(folder):
                    open_folder_state = True
                    pushbutton.clicked.connect(partial(Utils.open_file, folder))
                else:
                    open_folder_state = False

                pushbutton.setEnabled(open_folder_state)

            elif pushbutton.objectName() == ActionItems.slides_actions['attach_slides']['text']:

                # attach slides is enabled, if at least one of the files exist.
                video_path = metadata.get('offline_filepath')
                slides_path = metadata.get('slides_path')
                captions_path = metadata.get('captions_path')
                if (video_path and os.path.exists(video_path)) or \
                        (slides_path and os.path.exists(slides_path)) or \
                        (captions_path and os.path.exists(captions_path)):
                    attach_slides_state = True
                else:
                    attach_slides_state = False

                pushbutton.clicked.connect(partial(self.callbacks['attach_slides'], filepath))
                pushbutton.setEnabled(attach_slides_state)

        # a slightly hackish way to sort widgets -
        # create an integer out of the (slide count, button1_state, button2_state, ...)
        # pass it to a Custom TableWidgetItem with __lt__ overridden to provide numeric sort.
        cell_value = '{}{}{}'.format(
            int(download_slides_state), int(open_folder_state), int(attach_slides_state))

        return widget, int(cell_value)

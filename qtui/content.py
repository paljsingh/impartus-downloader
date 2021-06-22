import os
from functools import partial
from typing import Dict, List

from PySide2 import QtCore
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QMainWindow, QWidget, QAbstractScrollArea, QVBoxLayout, QHBoxLayout, QCheckBox, \
    QHeaderView
from PySide2.QtWidgets import QTableWidgetItem, QTableWidget, QStyleOptionProgressBar, QStyle
from PySide2.QtWidgets import QLabel, QPushButton, QComboBox, QLineEdit, QProgressBar

from lib.impartus import Impartus
from qtui.menubar import Menubar
from qtui.rodelegate import ReadOnlyDelegate
from lib.config import Config, ConfigType
from lib.finder import Finder
from lib.utils import Utils
from qtui.search import Search
from ui.data import ConfigKeys, ActionItems, Icons, Columns, IconFiles, Labels


class ContentWindow(QMainWindow):

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        colorscheme_config = Config.load(ConfigType.COLORSCHEMES)
        self.default_color_scheme = colorscheme_config.get(colorscheme_config.get(ConfigKeys.COLORSCHEME_DEFAULT.value))

        self.conf = Config.load(ConfigType.IMPARTUS)
        offline_data = Finder(self.conf).get_offline_content()

        self.impartus = Impartus()

        self.menu_bar = Menubar(self, self.impartus, self.conf).add_menu()
        self._set_window_properties()

        table = QTableWidget()
        table = self._set_table_properties(
            table, len(offline_data),
            # extra column for checkbox
            len([*Columns.data_columns, *Columns.widget_columns, *Columns.hidden_columns]) + 1
        )

        table = self._set_header_properties(table)
        table = self._set_row_content(table, offline_data)
        table.show()
        self.table = table

        # create a vbox layout and add search button, table to it.
        vcontainer_widget = QWidget()
        vbox_layout = QVBoxLayout(vcontainer_widget)

        self.search = Search(self, self.table)
        search_widget = self.search.add_search_box()
        vbox_layout.addWidget(search_widget)
        vbox_layout.addWidget(self.table)
        self.setCentralWidget(vcontainer_widget)

    def _set_window_properties(self):
        # full screen
        self.setGeometry(0, 0, self.maximumWidth(), self.maximumHeight())
        # window title
        self.setWindowTitle(Labels.APPLICATION_TITLE.value)

    def _set_table_properties(self, table: QTableWidget, row_count: int, col_count: int):   # noqa
        table.setColumnCount(col_count)
        table.setRowCount(row_count)
        table.setSortingEnabled(True)

        table.setAlternatingRowColors(True)
        table.setStyleSheet('QTableView::item {{padding: 5px; margin: 0px;}}')
        table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        table.viewport().setMaximumWidth(4000)
        return table

    def _set_header_properties(self, table: QTableWidget):      # noqa
        readonly_delegate = ReadOnlyDelegate()

        widget = QTableWidgetItem()
        widget.setText('')
        table.setHorizontalHeaderItem(0, widget)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)

        # enumerate from 1.
        for index, (key, val) in enumerate(
                [*Columns.data_columns.items(), *Columns.widget_columns.items(), *Columns.hidden_columns.items()], 1):
            widget = QTableWidgetItem()
            widget.setText(val['display_name'])

            # set resizable property
            mode = val[ConfigKeys.RESIZE_POLICY.value]
            table.horizontalHeader().setSectionResizeMode(index, mode)

            # make the column read-only if editable property not set.
            if not val['editable']:
                table.setItemDelegateForColumn(index, readonly_delegate)
            else:
                widget.setIcon(QIcon(IconFiles.EDITABLE_BLUE.value))

            # disable sorting for some columns.
            if not val['sortable']:
                # TODO -
                pass

            if val['hidden']:
                table.setColumnHidden(index, True)

            table.setHorizontalHeaderItem(index, widget)

        # sort icons.
        table.horizontalHeader().setStyleSheet(
            '''
            QHeaderView::down-arrow {{image: url({sortdown}); width: 10px; height:9px; padding-right: 5px}}
            QHeaderView::up-arrow {{image: url({sortup}); width: 10px; height:9px; padding-right: 5px}}
            '''.format(
                sortdown=IconFiles.SORT_DOWN_ARROW.value,
                sortup=IconFiles.SORT_UP_ARROW.value,
            )
        )

        table.horizontalHeader().setSortIndicatorShown(True)

        return table

    def _add_checkbox_widget(self, row: int):
        container_widget = QWidget()
        checkbox = QCheckBox()
        checkbox.clicked.connect(partial(self.on_checkbox_click, row))
        container_widget_layout = QHBoxLayout(container_widget)
        container_widget_layout.addWidget(checkbox)
        container_widget_layout.setAlignment(QtCore.Qt.AlignCenter)
        container_widget_layout.setContentsMargins(0, 0, 0, 0)
        container_widget.setLayout(container_widget_layout)
        return container_widget

    def on_checkbox_click(self, row):
        # if the same item is clicked again, do not do anything.
        clicked_widget = self.table.cellWidget(row, 0).layout().itemAt(0).widget()
        if not clicked_widget.isChecked():
            return

        # keep only one checkbox selected at a time.
        for i in range(self.table.rowCount()):
            self.table.cellWidget(i, 0).layout().itemAt(0).widget().setChecked(False)
        clicked_widget.setChecked(True)

    def _set_row_content(self, table: QTableWidget, data: Dict):
        for index, (ttid, item) in enumerate(data.items()):
            # for each row, add a checkbox first.
            container_widget = self._add_checkbox_widget(index)
            table.setCellWidget(index, 0, container_widget)

            # enumerate rest of the columns from 1
            for col, (key, val) in enumerate(Columns.data_columns.items(), 1):
                widget = QTableWidgetItem(str(item[key]))
                widget.setTextAlignment(Columns.data_columns[key]['alignment'])
                table.setItem(index, col, widget)

            # total columns so far...
            col = len(Columns.data_columns) + 1

            # progress bar.
            progress_bar = self._add_progress_bar(item)
            table.setCellWidget(index, col, progress_bar)
            col += 1

            # video actions
            video_actions_widget = self._add_video_actions_buttons(item)
            table.setCellWidget(index, col, video_actions_widget)
            col += 1

            # slides actions
            slides_actions_widget = self._add_slides_actions_buttons(item, index)
            table.setCellWidget(index, col, slides_actions_widget)
            col += 1

            # hidden columns
            for col_index, (key, val) in enumerate(Columns.hidden_columns.items(), col):
                widget = QTableWidgetItem(str(item[key]))
                widget.setTextAlignment(Columns.hidden_columns[key]['alignment'])
                table.setItem(index, col, widget)

        for index in range(len(data)):
            table.setRowHeight(index, 48)

        return table

    def _add_slides_combobox(self, item, index):
        if item.get('backpack_slides'):
            combo_box = QComboBox()
            combo_box.addItem('{:4s} {:2d}'.format(Icons.SHOW_SLIDES, len(item['backpack_slides'])))
            for slide in item['backpack_slides']:
                combo_box.addItem(os.path.basename(slide))
            combo_box.activated.connect(
                partial(self._show_slides, item['backpack_slides'])
            )
            combo_box.model().item(0).setEnabled(False)
            combo_box.setMaximumWidth(100)
            return combo_box
        else:
            return

    def _add_progress_bar(self, item):
        progress_bar = QProgressBar(self)
        progress_bar.setValue(0)
        progress_bar.setTextVisible(True)
        if item['offline_filepath']:
            progress_bar.setValue(100)
        progressbar_options = QStyleOptionProgressBar()
        progressbar_options.state = QStyle.State_Enabled | QStyle.State_Active
        progress_bar.initStyleOption(progressbar_options)
        # style = "QProgressBar {border: solid grey; border-radius: 15px; color: black; text-align: center;}"
        # style += "QProgressBar::chunk {{background-color: {}; border-radius: 15px;}}".format(
        #     self.default_color_scheme.get('progressbar')['fg']
        # )
        # progress_bar.setStyleSheet(style)
        return progress_bar

    def _add_actions_buttons(self, actions: Dict):      # noqa
        for key, val in actions.items():
            pushbutton = QPushButton()
            pushbutton.setText(val['text'])
            pushbutton.setToolTip(val['tooltip'])
            pushbutton.setMaximumWidth(40)
            yield pushbutton

    def _get_layout_widget(self, widget: QWidget):      # noqa
        widget_layout = QHBoxLayout(widget)
        widget_layout.setSpacing(0)
        widget_layout.setMargin(0)
        return widget_layout

    def _add_slides_actions_buttons(self, metadata, index):
        widget = QWidget()
        widget_layout = self._get_layout_widget(widget)
        widget_layout.setAlignment(Columns.widget_columns.get('slides_actions')['alignment'])

        # show slides combo box.
        combo_box = self._add_slides_combobox(metadata, index)
        if combo_box:
            widget_layout.addWidget(combo_box)
        else:
            widget_layout.addWidget(QLabel())

        for pushbutton in self._add_actions_buttons(ActionItems.slides_actions):
            widget_layout.addWidget(pushbutton)

            # open folder should be enabled, if folder exist
            if pushbutton.text() == ActionItems.slides_actions['open_folder']['text']:
                folder = None
                if metadata.get('offline_filepath'):
                    folder = os.path.dirname(metadata['offline_filepath'])
                elif metadata['backpack_slides']:
                    folder = os.path.dirname(metadata['backpack_slides'][0])

                if folder and os.path.exists(folder):
                    pushbutton.setEnabled(True)
                    pushbutton.clicked.connect(partial(Utils.open_file, folder))
                else:
                    pushbutton.setEnabled(False)

            # slides download is enabled if the slides file exists on server, but not locally.
            if pushbutton.text() == ActionItems.slides_actions['download_slides']['text']:
                filepath = metadata.get(ConfigKeys.SLIDES_PATH.value)
                if metadata.get('slideCount') and filepath and not os.path.exists(filepath):
                    pushbutton.setEnabled(True)
                else:
                    pushbutton.setEnabled(False)

            # attach slides is enabled always (creates a folder if one does not exist).
            if pushbutton.text() == ActionItems.slides_actions['attach_slides']['text']:
                pushbutton.setEnabled(True)
        return widget

    def _add_video_actions_buttons(self, metadata):
        widget = QWidget()
        widget_layout = self._get_layout_widget(widget)
        for pushbutton in self._add_actions_buttons(ActionItems.video_actions):
            widget_layout.addWidget(pushbutton)

            # disable download button, if video exists locally.
            if metadata.get('offline_filepath') \
                    and pushbutton.text() == ActionItems.video_actions['download_video']['text']:
                pushbutton.setEnabled(False)
            else:
                pushbutton.setEnabled(True)

            # enable play button, if video exists locally.
            if metadata.get('offline_filepath') \
                    and pushbutton.text() == ActionItems.video_actions['play_video']['text']:
                pushbutton.setEnabled(True)
                pushbutton.clicked.connect(partial(Utils.open_file, metadata['offline_filepath']))
            else:
                pushbutton.setEnabled(False)

            # enable download chats button, if lecture chats file does not exist.
            if pushbutton.text() == ActionItems.video_actions['download_captions']['text']:
                filepath = metadata.get(ConfigKeys.CAPTIONS_PATH.value)
                if filepath and not os.path.exists(filepath):
                    pushbutton.setEnabled(True)
                else:
                    pushbutton.setEnabled(False)

        return widget

    def _show_slides(self, slides: List, index: int):  # noqa
        Utils.open_file(slides[index - 1])

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Enter or e.key() == QtCore.Qt.Key_Return:
            self.search.search_next()
        elif e.key() == QtCore.Qt.Key_G and (e.modifiers() & QtCore.Qt.ShiftModifier) \
                and (e.modifiers() & QtCore.Qt.ControlModifier):
            self.search.search_prev()
        elif e.key() == QtCore.Qt.Key_G and (e.modifiers() & QtCore.Qt.ControlModifier):
            self.search.search_next()


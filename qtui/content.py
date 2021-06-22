import os
from functools import partial
from typing import Dict, List

from PySide2 import QtCore
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QMainWindow, QWidget, QAbstractScrollArea, QVBoxLayout, QHBoxLayout
from PySide2.QtWidgets import QTableWidgetItem, QTableWidget, QStyleOptionProgressBar, QStyle
from PySide2.QtWidgets import QLabel, QPushButton, QComboBox, QLineEdit, QProgressBar

from qtui.rodelegate import ReadOnlyDelegate
from lib.config import Config, ConfigType
from lib.finder import Finder
from lib.utils import Utils
from ui.data import ConfigKeys, ActionItems, Icons, Columns, IconFiles, Labels, SearchDirection


class ContentWindow(QMainWindow):

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.last_index = 0
        self.search_term = None

        colorscheme_config = Config.load(ConfigType.COLORSCHEMES)
        self.default_color_scheme = colorscheme_config.get(colorscheme_config.get(ConfigKeys.COLORSCHEME_DEFAULT.value))

        self.conf = Config.load(ConfigType.IMPARTUS)
        offline_data = Finder(self.conf).get_offline_content()

        self._set_window_properties()

        table = QTableWidget()
        table = self._set_table_properties(
            table, len(offline_data), len([*Columns.data_columns, *Columns.widget_columns]))

        table = self._set_header_properties(table)
        table = self._set_row_content(table, offline_data)
        table.show()
        self.table = table

        # create a vbox layout and add search button, table to it.
        vcontainer_widget = QWidget()
        vbox_layout = QVBoxLayout(vcontainer_widget)

        self.search_results = None
        self.search_box, self.results_label, search_widget = self._add_search_box()

        vbox_layout.addWidget(search_widget)
        vbox_layout.addWidget(self.table)
        self.setCentralWidget(vcontainer_widget)

    def _add_search_box(self):
        search_box = QLineEdit()
        search_box.setPlaceholderText('Search...')
        search_box.textChanged.connect(self.search)
        QtCore.QMetaObject.connectSlotsByName(self)

        results_label = QLabel()

        # create a horizontal container.
        widget = QWidget()
        hbox_layout = QHBoxLayout(widget)
        hbox_layout.addWidget(search_box)
        hbox_layout.addWidget(results_label)
        return search_box, results_label, widget

    def search_next(self, direction: int = SearchDirection.FORWARD.value):
        if not self.search_results:
            return

        # if search term is not changed
        if self.search_box.text() == self.search_term:
            count = len(self.search_results)
            self.search_results[self.last_index % count].setSelected(False)
            new_index = (self.last_index + direction) % count
            self.search_results[new_index].setSelected(True)
            self.table.scrollToItem(self.search_results[new_index])

            # also, update results label.
            self.last_index = new_index
            self.results_label.setText('{} / {} matches'.format(new_index + 1, count))  # 1 based output.
        else:
            # reset, and fall through the loop / yield again.
            self.last_index = -1
            self.search_term = self.search_box.text()

    def search_prev(self):
        self.search_next(SearchDirection.BACKWARD.value)

    def search(self):
        self.table.clearSelection()
        self.results_label.clear()
        self.search_results = None
        text = self.search_box.text().lower()
        # do not search for short text.
        if len(text) <= 2:
            return True

        self.search_results = self.table.findItems(text, QtCore.Qt.MatchFlag.MatchContains)
        self.search_term = self.search_box.text()
        self.last_index = -1    # first search shall be index 0.
        self.search_next()
        return True

    def _set_window_properties(self):
        # full screen
        self.setGeometry(0, 0, self.maximumWidth(), self.maximumHeight())
        # window title
        self.setWindowTitle(Labels.APPLICATION_TITLE.value)

    def _set_table_properties(self, table: QTableWidget, row_count: int, col_count: int):
        table.setColumnCount(col_count)
        table.setRowCount(row_count)
        table.setSortingEnabled(True)

        table.setAlternatingRowColors(True)
        # table.setStyleSheet(
        #     '''
        #     QTableView::item {{ background-color: {evencolor};}}
        #     QTableView::item:alternate {{ background-color: {oddcolor};}}
        #     QTableView::item {{
        #         padding: 5px;
        #         border-left: 1px solid {gridcolor}; border-top: 1px solid {gridcolor};
        #         margin: 0px;
        #         selection-color: {selcolor};
        #     }}
        #     '''.format(
        #         oddcolor=self.default_color_scheme.get('odd_row')['bg'],
        #         evencolor=self.default_color_scheme.get('even_row')['bg'],
        #         gridcolor=self.default_color_scheme.get('table')['grid'],
        #         selcolor=self.default_color_scheme.get('highlight'),
        # ))
        table.setStyleSheet('''
                QTableView::item {{
                padding: 5px;
                margin: 0px;
                selection-color: {selcolor};
            }}'''.format(selcolor=self.default_color_scheme.get('highlight')))

        table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        table.viewport().setMaximumWidth(4000)
        return table

    def _set_header_properties(self, table: QTableWidget):
        readonly_delegate = ReadOnlyDelegate()

        for index, (key, val) in enumerate([*Columns.data_columns.items(), *Columns.widget_columns.items()]):
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
            table.setHorizontalHeaderItem(index, widget)

        # set header colors, sort icons
        # QHeaderView::section
        # {{color: {color};
        # background - color: {bgcolor};}}
        table.horizontalHeader().setStyleSheet(
            '''
            QHeaderView::down-arrow {{image: url({sortdown}); width: 10px; height:9px; padding-right: 5px}}
            QHeaderView::up-arrow {{image: url({sortup}); width: 10px; height:9px; padding-right: 5px}}
            '''.format(
                # color=self.default_color_scheme.get('header')['fg'],
                # bgcolor=self.default_color_scheme.get('header')['bg'],
                sortdown=IconFiles.SORT_DOWN_ARROW.value,
                sortup=IconFiles.SORT_UP_ARROW.value,
            )
        )
        table.horizontalHeader().setSortIndicatorShown(True)

        return table

    def _set_row_content(self, table: QTableWidget, data: Dict):
        for index, (ttid, item) in enumerate(data.items()):
            for col, (key, val) in enumerate(Columns.data_columns.items()):
                widget = QTableWidgetItem(str(item[key]))
                widget.setTextAlignment(Columns.data_columns[key]['alignment'])
                table.setItem(index, col, widget)

            # download % progress bar
            col = len(Columns.data_columns)
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
        widget_layout.setAlignment(QtCore.Qt.AlignCenter)
        return widget_layout

    def _add_slides_actions_buttons(self, metadata, index):
        widget = QWidget()
        widget_layout = self._get_layout_widget(widget)

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
            self.search_next()
        elif e.key() == QtCore.Qt.Key_G and (e.modifiers() & QtCore.Qt.ShiftModifier) \
                and (e.modifiers() & QtCore.Qt.ControlModifier):
            self.search_prev()
        elif e.key() == QtCore.Qt.Key_G and (e.modifiers() & QtCore.Qt.ControlModifier):
            self.search_next()

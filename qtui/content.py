from functools import partial
from typing import Dict

from PySide2 import QtCore
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QMainWindow, QWidget, QAbstractScrollArea, QVBoxLayout, QHeaderView
from PySide2.QtWidgets import QTableWidgetItem, QTableWidget

from lib.impartus import Impartus
from qtui.common import Common
from qtui.menubar import Menubar
from qtui.progressbar import ProgressBar
from qtui.rodelegate import ReadOnlyDelegate
from lib.config import Config, ConfigType
from lib.finder import Finder
from qtui.search import Search
from qtui.slides import Slides
from qtui.videos import Videos
from ui.data import ConfigKeys, Columns, IconFiles, Labels


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
            table,
            len(offline_data),  # row count
            # col count: extra column for checkbox
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

        # header item for checkboxes column (TODO: check if it is possible to add a 'select all' checkbox here.)
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

            # hidden columns.
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
            container_widget = Common.add_checkbox_widget(partial(self.on_checkbox_click))
            table.setCellWidget(index, 0, container_widget)

            # enumerate rest of the columns from 1
            for col, (key, val) in enumerate(Columns.data_columns.items(), 1):
                widget = QTableWidgetItem(str(item[key]))
                widget.setTextAlignment(Columns.data_columns[key]['alignment'])
                table.setItem(index, col, widget)

            # total columns so far...
            col = len(Columns.data_columns) + 1

            # progress bar.
            progress_bar = ProgressBar.add_progress_bar(item)
            table.setCellWidget(index, col, progress_bar)
            col += 1

            # video actions
            video_actions_widget = Videos.add_video_actions_buttons(item)
            table.setCellWidget(index, col, video_actions_widget)
            col += 1

            # slides actions
            slides_actions_widget = Slides.add_slides_actions_buttons(item)
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

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Enter or e.key() == QtCore.Qt.Key_Return:
            self.search.search_next()
        elif e.key() == QtCore.Qt.Key_G and (e.modifiers() & QtCore.Qt.ShiftModifier) \
                and (e.modifiers() & QtCore.Qt.ControlModifier):
            self.search.search_prev()
        elif e.key() == QtCore.Qt.Key_G and (e.modifiers() & QtCore.Qt.ControlModifier):
            self.search.search_next()

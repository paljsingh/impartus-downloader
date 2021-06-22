from functools import partial
from typing import Dict, Callable

from PySide2 import QtCore
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QTableWidget, QAbstractScrollArea, QTableWidgetItem, QHeaderView

from qtui.common import Common
from qtui.progressbar import ProgressBar
from qtui.rodelegate import ReadOnlyDelegate
from qtui.slides import Slides
from qtui.videos import Videos
from ui.data import IconFiles, ConfigKeys, Columns


class Table:

    def __init__(self, row_count: int, col_count: int):
        self.row_count = row_count
        self.col_count = col_count
        self.table = self._add_table()

    def _add_table(self):
        table = QTableWidget()
        table.setColumnCount(self.col_count)
        table.setRowCount(self.row_count)
        table.setSortingEnabled(True)

        table.setAlternatingRowColors(True)
        table.setStyleSheet('QTableView::item {{padding: 5px; margin: 0px;}}')
        table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        table.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        table.viewport().setMaximumWidth(4000)
        return table

    def set_headers(self):
        readonly_delegate = ReadOnlyDelegate()

        # header item for checkboxes column (TODO: check if it is possible to add a 'select all' checkbox here.)
        widget = QTableWidgetItem()
        widget.setText('')
        self.table.setHorizontalHeaderItem(0, widget)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)

        # enumerate from 1.
        for index, (key, val) in enumerate(
                [*Columns.data_columns.items(), *Columns.widget_columns.items(), *Columns.hidden_columns.items()], 1):
            widget = QTableWidgetItem()
            widget.setText(val['display_name'])

            # set resizable property
            mode = val[ConfigKeys.RESIZE_POLICY.value]
            self.table.horizontalHeader().setSectionResizeMode(index, mode)

            # make the column read-only if editable property not set.
            if not val['editable']:
                self.table.setItemDelegateForColumn(index, readonly_delegate)
            else:
                widget.setIcon(QIcon(IconFiles.EDITABLE_BLUE.value))

            # disable sorting for some columns.
            if not val['sortable']:
                # TODO -
                pass

            # hidden columns.
            if val['hidden']:
                self.table.setColumnHidden(index, True)

            self.table.setHorizontalHeaderItem(index, widget)

        # sort icons.
        self.table.horizontalHeader().setStyleSheet(
            '''
            QHeaderView::down-arrow {{image: url({sortdown}); width: 10px; height:9px; padding-right: 5px}}
            QHeaderView::up-arrow {{image: url({sortup}); width: 10px; height:9px; padding-right: 5px}}
            '''.format(
                sortdown=IconFiles.SORT_DOWN_ARROW.value,
                sortup=IconFiles.SORT_UP_ARROW.value,
            )
        )
        self.table.horizontalHeader().setSortIndicatorShown(True)
        return self

    def set_row_content(self, data: Dict):
        for index, (ttid, item) in enumerate(data.items()):
            # for each row, add a checkbox first.
            container_widget = Common.add_checkbox_widget(partial(self.on_checkbox_click, index))
            self.table.setCellWidget(index, 0, container_widget)

            # enumerate rest of the columns from 1
            for col, (key, val) in enumerate(Columns.data_columns.items(), 1):
                widget = QTableWidgetItem(str(item[key]))
                widget.setTextAlignment(Columns.data_columns[key]['alignment'])
                self.table.setItem(index, col, widget)

            # total columns so far...
            col = len(Columns.data_columns) + 1

            # progress bar.
            progress_bar = ProgressBar.add_progress_bar(item)
            self.table.setCellWidget(index, col, progress_bar)
            col += 1

            # video actions
            video_actions_widget = Videos.add_video_actions_buttons(item)
            self.table.setCellWidget(index, col, video_actions_widget)
            col += 1

            # slides actions
            slides_actions_widget = Slides.add_slides_actions_buttons(item)
            self.table.setCellWidget(index, col, slides_actions_widget)
            col += 1

            # hidden columns
            for col_index, (key, val) in enumerate(Columns.hidden_columns.items(), col):
                widget = QTableWidgetItem(str(item[key]))
                widget.setTextAlignment(Columns.hidden_columns[key]['alignment'])
                self.table.setItem(index, col, widget)

        for index in range(len(data)):
            self.table.setRowHeight(index, 48)
        return self

    def on_checkbox_click(self, row):
        # if the same item is clicked again, do not do anything.
        clicked_widget = self.table.cellWidget(row, 0).layout().itemAt(0).widget()
        if not clicked_widget.isChecked():
            return

        # keep only one checkbox selected at a time.
        for i in range(self.table.rowCount()):
            self.table.cellWidget(i, 0).layout().itemAt(0).widget().setChecked(False)
        clicked_widget.setChecked(True)

    def show(self):
        self.table.show()

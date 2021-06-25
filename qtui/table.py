import os
import shutil
from functools import partial
from typing import Dict

from PySide2 import QtCore
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QTableWidget, QAbstractScrollArea, QTableWidgetItem, QHeaderView, QFileDialog

from lib.config import Config, ConfigType
from lib.utils import Utils
from qtui.common import Common
from qtui.progressbar import ProgressBar
from qtui.rodelegate import ReadOnlyDelegate
from qtui.slides import Slides
from qtui.videos import Videos
from ui.data import IconFiles, Columns


class Table:

    def __init__(self, row_count: int, col_count: int):
        self.conf = Config.load(ConfigType.IMPARTUS)
        self.row_count = row_count
        self.col_count = col_count
        self.table = self._add_table()
        self.data = None

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

            # make the column read-only if editable property not set.
            if not val['editable']:
                self.table.setItemDelegateForColumn(index, readonly_delegate)
            else:
                widget.setIcon(QIcon(IconFiles.EDITABLE_BLUE.value))

            # disable sorting for some columns.
            if not val['sortable']:
                # TODO -
                pass

            self.table.horizontalHeader().setSectionResizeMode(index, val['resize_policy'])
            if val['hidden']:
                # self.table.horizontalHeader().setSectionHidden(index, True)
                self.table.setColumnHidden(index, True)
                pass

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
        self.data = data
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
            progress_bar = ProgressBar('round')
            self.table.setCellWidget(index, col, progress_bar)
            if item['offline_filepath']:
                progress_bar.setValue(100)
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
                self.table.setItem(index, col_index, widget)

        for index in range(len(data)):
            self.table.setRowHeight(index, 48)
        return self

    def resizable_headers(self):
        # self.table.horizontalHeader().setCascadingSectionResizes(True)
        # for i in range(self.table.columnCount()):
        #     self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

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

    def show_hide_column(self, column):
        col_index = None
        for i, col_name in enumerate([*Columns.data_columns.keys(), *Columns.widget_columns.keys()], 1):
            if col_name == column:
                col_index = i
                break

        if self.table.isColumnHidden(col_index):
            self.table.setColumnHidden(col_index, False)
        else:
            self.table.setColumnHidden(col_index, True)

    def _get_checked_row_index(self):
        for i in range(self.table.rowCount()):
            if self.table.cellWidget(i, 0).layout().itemAt(0).widget().isChecked():
                return i
        return -1

    def _get_ttid_col_index(self):
        for i, key in enumerate(Columns.hidden_columns.keys(), 1 + len(Columns.data_columns) + len(Columns.widget_columns)):
            if key == 'ttid':
                return i
        return -1

    def _get_ttid(self, row_index, ttid_col_index):
        return self.table.item(row_index, ttid_col_index).text()

    def _get_ttid_for_checked_row(self):
        if not self.data:
            return

        ttid_col_index = self._get_ttid_col_index()
        if ttid_col_index < 0:
            return

        checked_row_index = self._get_checked_row_index()
        if checked_row_index < 0:
            return

        return self._get_ttid(checked_row_index, ttid_col_index)

    def play_video(self):
        ttid = self._get_ttid_for_checked_row()
        video_file = self.data.get(ttid)['offline_filepath']
        if video_file:
            Utils.open_file(video_file)

    def _get_folder_path(self):
        ttid = self._get_ttid_for_checked_row()

        video_path = self.data.get(ttid)['offline_filepath'] if self.data.get(ttid).get('offline_filepath') else None
        if video_path:
            return os.path.dirname(video_path)
        slides_path = self.data.get(ttid)['backpack_slides'][0] if self.data.get(ttid).get('backpack_slides') else None
        if slides_path:
            return os.path.dirname(slides_path)
        captions_path = self.data.get(ttid)['captions'][0] if self.data.get(ttid).get('captions') else None
        if captions_path:
            return os.path.dirname(captions_path)

    def open_folder(self):
        folder_path = self._get_folder_path()
        Utils.open_file(folder_path)

    def attach_slides(self):
        folder_path = self._get_folder_path()
        filters = ['{} files (*.{})'.format(str(x).title(), x) for x in self.conf.get('allowed_ext')]
        filters_str = ';;'.join(filters)
        filepaths = QFileDialog().getOpenFileNames(None,
                                                   caption="Select files to attach...",
                                                   dir=folder_path,
                                                   filter=filters_str)
        if not filepaths:
            return
        for filepath in filepaths[0]:
            shutil.copy(filepath, folder_path)
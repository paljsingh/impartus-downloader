from functools import partial

from PySide2.QtCore import QModelIndex
from PySide2.QtWidgets import QWidget, QStyleOptionViewItem, QLineEdit
from PySide2.QtWidgets import QStyledItemDelegate
from typing import Callable

from lib.config import ConfigType, Config
from lib.data.columns import Columns


class WriteDelegate(QStyledItemDelegate):
    def __init__(self, data_callback: Callable, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.orig_value = None
        self.data_callback = data_callback

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex) -> QWidget:
        # if column index belongs to one of the editable columns...
        if index.column() in [i for i, v in enumerate(Columns.data_columns.values(), 1) if v['editable']]:
            editor = super().createEditor(parent, option, index)
            editor.editingFinished.connect(partial(self.on_editing_finish, editor, index, index.data()))
            return editor

    def on_editing_finish(self, editor: QLineEdit, index: QModelIndex, old_value: str):
        """
        Replace all instances of 'old value' with 'new value' in the table.
        Update the config map
        'original value': 'old value'  =>  'original value': 'new value'
        """
        table = editor.parent().parent()
        ttid_col_index = Columns.get_column_index_by_key('ttid')
        fcid_col_index = Columns.get_column_index_by_key('fcid')
        ttid_text = table.item(index.row(), ttid_col_index).text()
        fcid_text = table.item(index.row(), fcid_col_index).text()
        rf_id = 0
        if ttid_text and ttid_text != '0':
            rf_id = int(ttid_text)
        elif fcid_text and fcid_text != '0':
            rf_id = int(fcid_text)

        column_name = Columns.get_displayable_video_columns()[index.column() - 1]
        original_value = self.data_callback()[rf_id][column_name]
        new_value = editor.text()

        # update mapping config.
        mappings = Config.load(ConfigType.MAPPINGS)
        if mappings.get(column_name):
            mappings[column_name][original_value] = new_value
        else:
            mappings[column_name] = {original_value: new_value}
        Config.save(ConfigType.MAPPINGS)

        for i in range(table.rowCount()):

            if table.item(i, index.column()).text() == old_value:
                table.item(i, index.column()).setText(new_value)

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QHeaderView


class Columns:
    """
    Table data headers and their properties.
    Also provides a few helper methods for table header data.
    """
    data_columns = {
        'subjectNameShort': {
            'alignment': Qt.AlignLeft | Qt.AlignVCenter,
            'display_name': 'Subject',
            'editable': True,
            'hidden': False,
            'menu_tooltip': 'Subject',
            # provide a mapping to original values column, if you want to present a column values differently, *and*
            # need to persist the changes via etc/mappings.conf
            'original_values_col': 'subjectName',
            'resize_policy': QHeaderView.ResizeMode.Fixed,
            'initial_size': 200,
            'sortable': True,
            'title_case': False,
        },
        'professorName': {
            'alignment': Qt.AlignLeft | Qt.AlignVCenter,
            'display_name': 'Faculty',
            'editable': False,
            'hidden': False,
            'menu_tooltip': 'Faculty Name',
            'original_values_col': None,
            'resize_policy': QHeaderView.ResizeMode.ResizeToContents,
            'inital_size': 150,
            'sortable': True,
            'title_case': True,
        },
        'topic': {
            'alignment': Qt.AlignLeft | Qt.AlignVCenter,
            'display_name': 'Topic',
            'editable': False,
            'hidden': False,
            'menu_tooltip': 'Lecture Topic',
            'original_values_col': None,
            'resize_policy': QHeaderView.ResizeMode.Stretch,    # only 1 column can be 'Stretch'
            'initial_size': 200,
            'sortable': True,
            'title_case': True,
        },
        'seqNo': {
            'alignment': Qt.AlignRight | Qt.AlignVCenter,
            'display_name': 'Lecture #',
            'editable': False,
            'hidden': False,
            'menu_tooltip': 'Lecture id',
            'original_values_col': None,
            'resize_policy': QHeaderView.ResizeMode.ResizeToContents,
            'initial_size': 50,
            'sortable': True,
            'title_case': False,
        },
        'actualDurationReadable': {
            'alignment': Qt.AlignRight | Qt.AlignVCenter,
            'display_name': 'Duration',
            'editable': False,
            'hidden': False,
            'menu_tooltip': 'Lecture Duration',
            'original_values_col': None,
            'resize_policy': QHeaderView.ResizeMode.ResizeToContents,
            'initial_size': 50,
            'sortable': True,
            'title_case': False,
        },
        'tapNToggle': {
            'alignment': Qt.AlignRight | Qt.AlignVCenter,
            'display_name': 'Tracks',
            'editable': False,
            'hidden': False,
            'menu_tooltip': 'Number of tracks / view',
            'original_values_col': None,
            'resize_policy': QHeaderView.ResizeMode.ResizeToContents,
            'initial_size': 50,
            'sortable': True,
            'title_case': False,
        },
        'startDate': {
            'alignment': Qt.AlignRight | Qt.AlignVCenter,
            'display_name': 'Date',
            'editable': False,
            'hidden': False,
            'menu_tooltip': 'Lecture Date',
            'original_values_col': None,
            'resize_policy': QHeaderView.ResizeMode.ResizeToContents,
            'initial_size': 50,
            'sortable': True,
            'title_case': False,
        },
    }

    widget_columns = {
        'progress_bar': {
            'alignment': Qt.AlignHCenter | Qt.AlignVCenter,
            'display_name': 'Downloaded?',
            'editable': False,
            'hidden': False,
            'menu_tooltip': 'Download Status',
            'original_values_col': None,
            'resize_policy': QHeaderView.ResizeMode.Fixed,
            'initial_size': 100,
            'sortable': False,
            'title_case': False,
        },
        'video_actions': {
            'alignment': Qt.AlignHCenter | Qt.AlignVCenter,
            'display_name': 'Video',
            'editable': False,
            'hidden': False,
            'menu_tooltip': 'Video Actions',
            'original_values_col': None,
            'resize_policy': QHeaderView.ResizeMode.Fixed,
            'initial_size': 125,
            'sortable': False,
            'title_case': False,
        },
        'slides_actions': {
            'alignment': Qt.AlignHCenter | Qt.AlignVCenter,
            'display_name': 'Slides',
            'editable': False,
            'hidden': False,
            'menu_tooltip': 'Slides Actions',
            'original_values_col': None,
            'resize_policy': QHeaderView.ResizeMode.Fixed,
            'initial_size': 225,
            'sortable': False,
            'title_case': False,
        },
    }

    hidden_columns = {
        'ttid': {
            'alignment': Qt.AlignRight,
            'display_name': 'ttid',
            'editable': False,
            'hidden': True,
            'initial_size': 50,
            'menu_tooltip': 'ttid',
            'original_values_col': None,
            'resize_policy': QHeaderView.ResizeMode.Fixed,
            'sortable': True,
            'title_case': False,
        },
    }

    @classmethod
    def get_display_columns(cls):
        return [*Columns.data_columns, *Columns.widget_columns]

    @classmethod
    def get_column_index_by_key(cls, key_name):
        return [*Columns.data_columns.keys(), *Columns.widget_columns.keys(), *Columns.hidden_columns.keys()].index(
            key_name) + 1

    @classmethod
    def get_column_index_by_display_name(cls, display_name):
        for index, value in enumerate(
                [*Columns.data_columns.values(), *Columns.widget_columns.values(), *Columns.hidden_columns.values()]):
            if value['display_name'] == display_name:
                return index + 1

    @classmethod
    def get_columns_count(cls):
        return 1 + len(Columns.data_columns) + len(Columns.widget_columns) + len(Columns.hidden_columns)

    @classmethod
    def get_button_order(cls):
        return 1 + len(Columns.data_columns) + len(Columns.widget_columns) + len(Columns.hidden_columns)

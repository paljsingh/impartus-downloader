from PySide2.QtCore import Qt
from PySide2.QtWidgets import QHeaderView

from lib.data.Icons import Icons
from lib.data.labels import Labels


"""
Table data headers and their properties.
Also provides a few helper methods for table header data.
"""
data_columns = {
    Labels.VIDEO__SUBJECT_NAME.value: {
        'alignment': Qt.AlignLeft | Qt.AlignVCenter,
        'display_name': 'Subject',
        'editable': True,
        'hidden': False,
        'menu_name': 'Subject',
        'menu_tooltip': 'Subject',
        # provide a mapping to original values column, if you want to present a column values differently, *and*
        # need to persist the changes via etc/mappings.conf
        'original_values_col': 'subjectName',
        'resize_policy': QHeaderView.ResizeMode.Fixed,
        'initial_size': 200,
        'sortable': True,
        'title_case': False,
    },
    Labels.VIDEO__PROFESSOR_NAME.value: {
        'alignment': Qt.AlignLeft | Qt.AlignVCenter,
        'display_name': 'Faculty',
        'editable': False,
        'hidden': False,
        'menu_name': 'Faculty',
        'menu_tooltip': 'Faculty Name',
        'original_values_col': None,
        'resize_policy': QHeaderView.ResizeMode.Fixed,
        'initial_size': 200,
        'sortable': True,
        'title_case': True,
    },
    Labels.VIDEO__TOPIC.value: {
        'alignment': Qt.AlignLeft | Qt.AlignVCenter,
        'display_name': 'Topic',
        'editable': False,
        'hidden': False,
        'menu_name': 'Topic',
        'menu_tooltip': 'Lecture Topic',
        'original_values_col': None,
        'resize_policy': QHeaderView.ResizeMode.Stretch,  # only 1 column can be 'Stretch'
        'initial_size': 300,
        'sortable': True,
        'title_case': True,
    },
    Labels.VIDEO__SEQ.value: {
        'alignment': Qt.AlignRight | Qt.AlignVCenter,
        'display_name': 'Lecture #',
        'editable': False,
        'hidden': False,
        'menu_name': 'Lecture #',
        'menu_tooltip': 'Lecture id',
        'original_values_col': None,
        'resize_policy': QHeaderView.ResizeMode.ResizeToContents,
        'initial_size': 50,
        'sortable': True,
        'title_case': False,
    },
    Labels.VIDEO__DURATION.value: {
        'alignment': Qt.AlignRight | Qt.AlignVCenter,
        'display_name': 'Duration',
        'editable': False,
        'hidden': False,
        'menu_name': 'Duration',
        'menu_tooltip': 'Lecture Duration',
        'original_values_col': None,
        'resize_policy': QHeaderView.ResizeMode.ResizeToContents,
        'initial_size': 50,
        'sortable': True,
        'title_case': False,
    },
    Labels.VIDEO__CHANNELS.value: {
        'alignment': Qt.AlignRight | Qt.AlignVCenter,
        'display_name': 'Tracks',
        'editable': False,
        'hidden': False,
        'menu_name': 'Tracks',
        'menu_tooltip': 'Number of tracks / view',
        'original_values_col': None,
        'resize_policy': QHeaderView.ResizeMode.ResizeToContents,
        'initial_size': 50,
        'sortable': True,
        'title_case': False,
    },
    Labels.VIDEO__DATE.value: {
        'alignment': Qt.AlignRight | Qt.AlignVCenter,
        'display_name': 'Date',
        'editable': False,
        'hidden': False,
        'menu_name': 'Date',
        'menu_tooltip': 'Lecture Date',
        'original_values_col': None,
        'resize_policy': QHeaderView.ResizeMode.ResizeToContents,
        'initial_size': 75,
        'sortable': True,
        'title_case': False,
    },
    Labels.DOCUMENT__FILENAME.value: {
        'alignment': Qt.AlignLeft | Qt.AlignVCenter,
        'display_name': 'File Name',
        'editable': False,
        'hidden': False,
        'menu_name': 'File Name',
        'menu_tooltip': 'File Name',
        'original_values_col': None,
        'resize_policy': QHeaderView.ResizeMode.Stretch,
        'initial_size': 300,
        'sortable': True,
        'title_case': True,
    },
    Labels.DOCUMENT__FILESIZE.value: {
        'alignment': Qt.AlignLeft | Qt.AlignVCenter,
        'display_name': 'File Size (KB)',
        'editable': False,
        'hidden': False,
        'menu_name': 'File Size',
        'menu_tooltip': 'File Size in KB',
        'original_values_col': None,
        'resize_policy': QHeaderView.ResizeMode.Fixed,
        'initial_size': 75,
        'sortable': True,
        'title_case': True,
    },
    Labels.DOCUMENT__DATE.value: {
        'alignment': Qt.AlignLeft | Qt.AlignVCenter,
        'display_name': 'Created On',
        'editable': False,
        'hidden': False,
        'menu_name': 'Created On',
        'menu_tooltip': 'Created On',
        'original_values_col': None,
        'resize_policy': QHeaderView.ResizeMode.Fixed,
        'initial_size': 150,
        'sortable': True,
        'title_case': True,
    },
}

widget_columns = {
    Labels.VIDEO__FLIPPED.value: {
        'alignment': Qt.AlignRight | Qt.AlignVCenter,
        'display_name': 'F',
        'editable': False,
        'hidden': True,
        'menu_name': 'Flipped?',
        'menu_tooltip': 'Flipped Lecture ?',
        'original_values_col': None,
        'resize_policy': QHeaderView.ResizeMode.ResizeToContents,
        'initial_size': 50,
        'sortable': True,
        'title_case': False,
        'icon': Icons.MENU__FLIPPED_VIDEO_QUALITY.value,
    },
    Labels.VIDEO__PROGRESSBAR.value: {
        'alignment': Qt.AlignHCenter | Qt.AlignVCenter,
        'display_name': 'Downloaded?',
        'editable': False,
        'hidden': False,
        'menu_name': 'Downloaded?',
        'menu_tooltip': 'Download Status',
        'original_values_col': None,
        'resize_policy': QHeaderView.ResizeMode.ResizeToContents,
        'initial_size': 100,
        'sortable': False,
        'title_case': False,
    },
    Labels.VIDEO__ACTIONS.value: {
        'alignment': Qt.AlignHCenter | Qt.AlignVCenter,
        'display_name': 'Video',
        'editable': False,
        'hidden': False,
        'menu_name': 'Video',
        'menu_tooltip': 'Video Actions',
        'original_values_col': None,
        'resize_policy': QHeaderView.ResizeMode.ResizeToContents,
        'initial_size': 150,
        'sortable': False,
        'title_case': False,
    },
    Labels.DOCUMENT__ACTIONS.value: {
        'alignment': Qt.AlignHCenter | Qt.AlignVCenter,
        'display_name': 'Slides',
        'editable': False,
        'hidden': False,
        'menu_name': 'Slides',
        'menu_tooltip': 'Slides Actions',
        'original_values_col': None,
        'resize_policy': QHeaderView.ResizeMode.ResizeToContents,
        'initial_size': 225,
        'sortable': False,
        'title_case': False,
    }
}

video_data_columns = {
    k: data_columns.get(k) for k in
    [Labels.VIDEO__SUBJECT_NAME.value, Labels.VIDEO__PROFESSOR_NAME.value, Labels.VIDEO__TOPIC.value,
     Labels.VIDEO__SEQ.value, Labels.VIDEO__DURATION.value, Labels.VIDEO__CHANNELS.value,
     Labels.VIDEO__DATE.value]
}

document_data_columns = {
    k: data_columns.get(k) for k in
    [Labels.DOCUMENT__SUBJECT_NAME.value, Labels.DOCUMENT__FILENAME.value, Labels.DOCUMENT__FILESIZE.value,
     Labels.DOCUMENT__DATE.value]
}

video_widget_columns = {
    k: widget_columns.get(k) for k in
    [Labels.VIDEO__FLIPPED.value, Labels.VIDEO__PROGRESSBAR.value, Labels.VIDEO__ACTIONS.value]
}

document_widget_columns = {
    k: widget_columns.get(k) for k in [Labels.DOCUMENT__ACTIONS.value]}


class Columns:

    @staticmethod
    def get_video_columns():
        return [*video_data_columns, *video_widget_columns]

    @staticmethod
    def get_video_columns_dict():
        return {**video_data_columns, **video_widget_columns}

    @staticmethod
    def get_video_columns_count():
        return 1 + len(video_data_columns) + len(video_widget_columns)

    @staticmethod
    def get_document_columns():
        return [*document_data_columns, *document_widget_columns]

    @classmethod
    def get_document_columns_count(cls):
        return len(document_data_columns) + len(document_widget_columns)

    @staticmethod
    def get_document_columns_dict():
        return {**document_data_columns, **document_widget_columns}

    @staticmethod
    def get_column_index_by_key(key_name):
        return [*video_data_columns.keys(),
                *video_widget_columns.keys(),
                ].index(key_name) + 1

    @staticmethod
    def get_document_column_index_by_key(key_name):
        return [*document_data_columns.keys(),
                *document_widget_columns.keys(),
                ].index(key_name)

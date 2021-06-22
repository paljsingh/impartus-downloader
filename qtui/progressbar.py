from PySide2.QtWidgets import QProgressBar, QStyleOptionProgressBar, QStyle


class ProgressBar:

    @classmethod
    def add_progress_bar(cls, item):
        progress_bar = QProgressBar()
        progress_bar.setValue(0)
        progress_bar.setTextVisible(True)
        if item['offline_filepath']:
            progress_bar.setValue(100)
        progressbar_options = QStyleOptionProgressBar()
        progressbar_options.state = QStyle.State_Enabled | QStyle.State_Active
        progress_bar.initStyleOption(progressbar_options)
        return progress_bar

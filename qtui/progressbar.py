from PySide2.QtWidgets import QWidget, QHBoxLayout, QProgressBar, QStyleOptionProgressBar, QStyle
from PySide2extn.RoundProgressBar import roundProgressBar


class ProgressBar(QWidget):

    def __init__(self, pb_type: str):
        super().__init__()
        self.widget = None
        self.pb_type = pb_type
        if pb_type == 'round':
            self.progress_bar = self._add_round_progress_bar()
        else:
            self.progress_bar = self._add_progress_bar()

    def setValue(self, value: int):     # noqa
        if self.pb_type == 'round':
            self.progress_bar.rpb_setValue(value)
        else:
            self.progress_bar.setValue(value)

    def _add_round_progress_bar(self):
        widget_layout = QHBoxLayout(self)
        widget_layout.setMargin(0)
        widget_layout.setSpacing(0)

        progress_bar = roundProgressBar()
        progress_bar.rpb_setMinimumSize(44, 44)
        progress_bar.rpb_setMaximumSize(44, 44)
        progress_bar.rpb_setTextRatio(5)
        progress_bar.rpb_setValue(0)
        progress_bar.rpb_setTextFormat('Value')
        progress_bar.rpb_setBarStyle('Pizza')

        widget_layout.addWidget(progress_bar)
        return progress_bar

    def _add_progress_bar(self):     # noqa
        progress_bar = QProgressBar()
        progress_bar.setValue(0)
        progress_bar.setTextVisible(True)
        progressbar_options = QStyleOptionProgressBar()
        progressbar_options.state = QStyle.State_Enabled | QStyle.State_Active
        progress_bar.initStyleOption(progressbar_options)
        return progress_bar

    # def get_progress_bar(self):
    #     if self.pb_type == 'round':
    #         return self.widget
    #     else:
    #         return self.progress_bar

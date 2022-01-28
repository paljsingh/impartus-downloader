from datetime import datetime

import PySide2
from PySide2 import QtCore
from PySide2.QtCore import QEvent
from PySide2.QtGui import QPalette
from PySide2.QtWidgets import QApplication, QHBoxLayout, QWidget
from PySide2extn.RoundProgressBar import roundProgressBar

from ui.uiitems.customwidgets.tablewidgetitem import CustomTableWidgetItem


class SortableRoundProgressbar(QWidget):
    """
    Hacky implementation of a round sortable progressbar widget.

    A row column field in a QTable can be assigned both a QTableWidgetItem (table.setItem())
    and a QTableCellWidget (table.setCellWidget()).
    The former is used for sorting (default: alphabetical sort), while the latter can be used to display a widget.

    The class SortableRoundProgressbar, thus contains the following:
    - A customized QTableWidgetItem class instance, with __lt__ overridden to provide numeric sort.
    - A customized PySide2extn.RoundProgressBar.roundProgressBar, with additional change event method that can respond
      and adapt to the change in system theme / colors.
    - A QHBoxLayout item to keep the roundProgressBar horizontally center aligned.

    Every change in the SortableRoundProgressBar item must be updated to both the roundProgressBar
    instance (for display) and QTableWidgetItem (for sorting)
    """

    def __init__(self):
        super().__init__()

        # layout container.
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        # add a progress bar to the layout.
        self.pct_progress_bar = CustomRoundProgressBar(parent=self)
        self.pct_progress_bar.rpb_setTextFormat('Percentage')
        self.pct_progress_bar.rpb_setValue(0)
        self.pct_progress_bar.show()
        self.layout.addWidget(self.pct_progress_bar)

        # and one for eta...
        self.eta_progress_bar = CustomRoundProgressBar(parent=self)
        self.eta_progress_bar.rpb_setTextFormat('Value')
        self.eta_progress_bar.rpb_setValue(0)
        self.eta_progress_bar.hide()
        self.layout.addWidget(self.eta_progress_bar)

        # and another one for elapsed time...
        self.elap_progress_bar = CustomRoundProgressBar(parent=self)
        self.elap_progress_bar.rpb_setTextFormat('Value')
        self.elap_progress_bar.rpb_setValue(0)
        self.elap_progress_bar.hide()
        self.layout.addWidget(self.elap_progress_bar)

        # add a TableWidgetItem based on which the table can be sorted.
        self.table_widget_item = CustomTableWidgetItem()
        self.table_widget_item.setValue(0)

        # % value, to control progressbar's progress
        self.pctValue = 0

        # calculate ETA using last n updates at max.
        self.n = 10

        # history of past timestamp updates and progressbar values.
        # when a download is paused, history is cleared to not impact the ETA adversely.
        self.history = []

        # set when a download is started.
        self.start_epoch = None

        # collect the display metrics in this order.
        self.display_order = [self.percentageValue, self.eta, self.elapsed]

        # cycle through the display metrics in this order.
        self.set_order = [self.setPercentageValue, self.setEta, self.setElapsed]

        # cycle through the progress bars in this order.
        self.progressbars = [self.pct_progress_bar, self.eta_progress_bar, self.elap_progress_bar]

        # currently selected display metric.
        self.current_display_index = 0

        # initialize the widget item to 0
        self.setLayout(self.layout)

    def mouseReleaseEvent(self, event: PySide2.QtGui.QMouseEvent) -> None:
        """
        When this widget is clicked, switch the view to next progressbar.
        """
        self.current_display_index = (self.current_display_index + 1) % len(self.display_order)
        value = self.display_order[self.current_display_index]()
        self.set_order[self.current_display_index](value)
        for pb in self.progressbars:
            pb.hide()
        self.progressbars[self.current_display_index].show()

    def setAlignment(self, alignment=QtCore.Qt.AlignCenter):        # noqa
        self.layout.setAlignment(alignment)

    def changeEvent(self, event: QEvent) -> None:
        """
        On system theme change, update the progress bar colors.
        """
        super().changeEvent(event)
        if event.type() == QEvent.PaletteChange:
            self.pct_progress_bar.set_palette_color()
            self.eta_progress_bar.set_palette_color()
            self.elap_progress_bar.set_palette_color()
            return

    def setEta(self, value: int):
        """
        ETA display value for download
        --:-- when not started / paused.
        -mm:ss otherwise
        """
        if not self.start_epoch or not self.history:
            eta_format = '--:--'
        else:
            eta_format = '-{:d}:{:02d}'.format(int(value) // 60, int(value) % 60)
        self.eta_progress_bar.rpb_setValue(self.pctValue)
        self.eta_progress_bar.setText(eta_format)

    def eta(self):
        """
        calculated ETA (numeric)
        0 when video already downloaded.
        <0 / undefined when paused or not started the download.
        int no. of seconds when download in progress.
        """
        if self.pctValue == 100:
            return 0

        if not len(self.history):
            return -1

        timestamps = [x['timestamp'] for x in self.history]
        values = [x['value'] for x in self.history]
        time_last_n = max(timestamps) - min(timestamps)
        progress_last_n = max(values) - min(values)
        time_per_unit = time_last_n / progress_last_n if progress_last_n > 0 else 0

        eta_value = (100 - self.pctValue) * time_per_unit
        return int(eta_value)

    def setElapsed(self, value: int):
        """
        Elapsed time display format
        mm:ss when download in progress / paused
        --:-- when download not started.
        """
        if not self.start_epoch:
            eta_format = '--:--'
        else:
            eta_format = '{:d}:{:02d}'.format(int(value) // 60, int(value) % 60)
        self.elap_progress_bar.rpb_setValue(self.pctValue)
        self.elap_progress_bar.setText(eta_format)

    def elapsed(self):
        """
        Elapsed time (numeric) in seconds
        0 - if video is downloaded (previously), but not in this session.
        (last recorded timestamp - start timestamp) - if downloaded fully in this session.
        0 - if video is yet to be downloaded.
        (current timestamp - start timestamp) - if download in is progress.
        """
        if self.pctValue == 100:
            if self.history:
                return max([x['timestamp'] for x in self.history]) - self.start_epoch
            else:
                return 0
        elif self.pctValue == 0:
            return 0
        else:
            return int(datetime.utcnow().timestamp()) - self.start_epoch

    def setPercentageValue(self, value: int):
        """
        percentage Value - display format
        """
        self.pctValue = value
        self.pct_progress_bar.rpb_setValue(value)

    def percentageValue(self):
        """
        percentage value (numeric)
        """
        return self.pctValue

    def setValue(self, value: int, timestamp: int = None):     # noqa
        """
        The controller api for all the display units.
        Takes a value (pct value) and timestamp (can be None when the progressbar is initialized to 0 or 100.)

        If timestamp provided
            initialize start epoch for download if not already set.
            maintain a queue(circular) of previous values/timestamps of upto N size.
        If no timestamp provided
            clear history if exists (useful when a video download is paused)

        update the text value of progressbar as per the currently selected metric.
        """

        if timestamp:
            if not self.start_epoch:
                self.start_epoch = timestamp
            self.history.insert(len(self.history) % self.n, {
                'timestamp': timestamp,
                'value': value,
            })
        else:
            # reset
            self.history = []

        self.table_widget_item.setValue(value)      # for numeric sort
        self.setPercentageValue(value)              # for progressbar display (arc value)

        current_value_format = self.display_order[self.current_display_index]()
        self.set_order[self.current_display_index](current_value_format)    # set the text of progressbar.

    def setTextColor(self, text_color):
        self.pct_progress_bar.rpb_setTextColor(text_color)
        self.eta_progress_bar.rpb_setTextColor(text_color)
        self.elap_progress_bar.rpb_setTextColor(text_color)

    def setTextColorNormal(self):
        text_color = QApplication.palette().color(QPalette.Text).getRgb()
        self.setTextColor(text_color)

    def setTextColorHighlight(self):
        text_color = QApplication.palette().color(QPalette.Background).getRgb()
        self.setTextColor(text_color)


class CustomRoundProgressBar(roundProgressBar):
    """
    Customized round progress bar that can respond to change in system theme settings and adopt to the new QPalette.
    Also provides a similar interface as to a QTableWidgetItem to read/set values.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.rpb_setMinimumSize(48, 48)
        self.rpb_setMaximumSize(48, 48)
        self.rpb_setTextRatio(6)
        self.rpb_setTextFont('Avant Garde')
        self.rpb_setTextFormat('Percent')
        self.rpb_setLineWidth(3)
        self.set_palette_color()
        self.show()

    def set_palette_color(self):
        """
        Update the progress bar colors to match currently selected theme.
        """
        path_color = QApplication.palette().color(QPalette.Background).getRgb()
        line_color = QApplication.palette().color(QPalette.Highlight).getRgb()
        text_color = QApplication.palette().color(QPalette.Text).getRgb()
        self.rpb_setTextColor(text_color)
        self.rpb_setLineColor(line_color)
        self.rpb_setPathColor(path_color)

    def setValue(self, value: int):     # noqa
        self.rpb_setValue(value)

    def setText(self, value: str):
        self.rpb_textValue = str(value)
        self.update()

    def value(self):
        return self.rpb_getValue()

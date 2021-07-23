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
    instance (for displau) and QTableWidgetItem (for sorting)
    """

    def __init__(self):
        super().__init__()

        # layout container.
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        # add a progress bar to the layout.
        self.progress_bar = CustomRoundProgressBar(parent=self)
        self.layout.addWidget(self.progress_bar)

        # add a TableWidgetItem based on which the table can be sorted.
        self.table_widget_item = CustomTableWidgetItem()

        # initialize both the progressbar and the widget item to 0
        self.setValue(0)

        self.setLayout(self.layout)

    def setAlignment(self, alignment=QtCore.Qt.AlignCenter):
        self.layout.setAlignment(alignment)

    def changeEvent(self, event: QEvent) -> None:
        """
        On system theme change, update the progress bar colors.
        """
        super().changeEvent(event)
        if event.type() == QEvent.PaletteChange:
            self.progress_bar.set_palette_color()

    def setValue(self, value: int):
        self.progress_bar.rpb_setValue(value)
        self.table_widget_item.setValue(value)

    def value(self):
        self.table_widget_item.value()


class CustomRoundProgressBar(roundProgressBar):
    """
    Customized round progress bar that can respond to change in system theme settings and adopt to the new QPalette.
    Also provides a similar interface as to a QTableWidgetItem to read/set values.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.rpb_setMinimumSize(36, 36)
        self.rpb_setMaximumSize(48, 48)
        self.rpb_setTextRatio(5)
        self.rpb_setTextFont('Arial')
        self.rpb_setTextFormat('Percent')
        self.rpb_setLineWidth(4)
        self.rpb_setTextWidth(9)
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

    def setValue(self, value: int):
        self.rpb_setValue(value)

    def value(self):
        return self.rpb_getValue()

from PySide2.QtCore import QEvent
from PySide2.QtGui import QPalette
from PySide2.QtWidgets import QPushButton, QApplication
import qtawesome as qta


class CustomPushButton(QPushButton):
    def __init__(self):
        super().__init__()
        pass

    def changeEvent(self, event: QEvent) -> None:
        """
        On system theme change, update the progress bar colors.
        """
        super(CustomPushButton, self).changeEvent(event)
        if event.type() == QEvent.PaletteChange:
            self.apply_current_palette()

    def setIcon(self, icon_name: str, animate=False):
        self.setObjectName(icon_name)
        self.apply_current_palette(animate=animate)

    def apply_current_palette(self, animate=False):
        highlight_color = QApplication.palette().color(QPalette.Highlight)
        text_color = QApplication.palette().color(QPalette.Text)

        if animate:
            qicon = qta.icon(
                self.objectName(),
                color=text_color,
                color_active=highlight_color,
                animation=qta.Spin(self)
            )
        else:
            qicon = qta.icon(
                self.objectName(),
                color=text_color,
                color_active=highlight_color,
            )
        super().setIcon(qicon)

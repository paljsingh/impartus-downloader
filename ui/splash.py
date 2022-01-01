from typing import List

from PySide2 import QtCore
from PySide2.QtCore import Qt, QTimer
from PySide2.QtCore import QFile
from PySide2.QtGui import QGuiApplication
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QDialog, QLabel, QProgressBar

from ui.callbacks.utils import CallbackUtils


class SplashScreen(QDialog):

    def __init__(self, parent_widget):
        super().__init__(parent_widget)

        loader = QUiLoader()

        file = QFile("ui/views/splash.ui")
        file.open(QFile.ReadOnly)
        self.splash = loader.load(file, parent_widget)
        self.splash.setWindowFlag(Qt.FramelessWindowHint)
        self.splash.setFocus()
        self.splash.setAttribute(Qt.WA_TranslucentBackground, True)
        self.splash.setWindowModality(Qt.WindowModality.ApplicationModal)
        file.close()
        self.timer = QTimer()
        self.splash.setMinimumWidth(parent_widget.maximumWidth())
        self.splash.setMaximumWidth(parent_widget.maximumWidth())
        self.splash.move(parent_widget.maximumWidth() / 2 - 200, parent_widget.maximumHeight() / 2 - 100)

        self.label = self.splash.findChild(QLabel, "label")
        self.progressbar = self.splash.findChild(QProgressBar, "progressBar")

    def show(self, widgets_to_disable: List = None):
        if not widgets_to_disable:
            return
        for widget in widgets_to_disable:
            widget.setDisabled(True)
        self.splash.show()

    def hide(self, widgets_to_enable: List = None):
        if not widgets_to_enable:
            return
        for widget in widgets_to_enable:
            widget.setDisabled(False)
        self.timer.singleShot(1000, self.splash.close)

    def setText(self, text):
        self.label: QLabel
        self.label.setText(text)

        self.progressbar: QProgressBar
        self.progressbar.show()
        self.progressbar.setValue(1)    # indeterminate / busy
        CallbackUtils().processEvents()


if __name__ == '__main__':
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    QGuiApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QGuiApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication([])
    SplashScreen(app).show()
    app.exec_()

from PySide2 import QtWidgets, QtCore
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QMainWindow

from lib.impartus import Impartus
from ui.content import ContentWindow
from ui.login import LoginWindow
from ui.menubar import Menubar
from ui.data import IconFiles


class App:
    def __init__(self):
        self.app = QtWidgets.QApplication([])
        self.app.setWindowIcon(QIcon(IconFiles.APP_LOGO.value))

        self.impartus = Impartus()
        self.login_window = LoginWindow(self.impartus)
        self.content_window = ContentWindow(self.impartus)
        self.content_window.set_layout()

        self.login_window.setup_ui(self.content_window, self.switch_window_callback)
        self.login_window.show()

        self.menu_bar = Menubar(self.login_window, self.content_window).add_menu(self.switch_window_callback)


    def switch_window_callback(self, from_window: QMainWindow, to_window: QMainWindow):  # noqa
        """
        switch between two windows.
        """
        to_window.show()
        from_window.hide()
        to_window.setFocus()
        return to_window

    def run(self):
        self.app.exec_()


if __name__ == '__main__':
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    App().run()


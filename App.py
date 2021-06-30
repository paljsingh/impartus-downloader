from PySide2 import QtWidgets, QtCore
from PySide2.QtGui import QIcon

from lib.impartus import Impartus
from ui.data.callbacks import Callbacks
from ui.content import ContentWindow
from ui.data.iconfiles import IconFiles
from ui.login import LoginWindow
from ui.menubar import Menubar


class App:
    """
    Launches Qt application.
    """

    def __init__(self):
        self.app = QtWidgets.QApplication([])
        self.app.setWindowIcon(QIcon(IconFiles.APP_LOGO.value))

        self.impartus = Impartus()
        self.login_window = LoginWindow(self.impartus)
        self.content_window = ContentWindow(self.impartus)

        # initialize callbacks
        Callbacks().setup(
            impartus=self.impartus,
            login_window=self.login_window,
            content_window=self.content_window
        )
        self.content_window.set_layout()

        self.login_window.setup_ui(self.content_window)
        self.login_window.show()

        self.menu_bar = Menubar(self.login_window, self.content_window).add_menu()

    def run(self):
        self.app.exec_()


if __name__ == '__main__':
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    App().run()

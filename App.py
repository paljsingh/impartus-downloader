from PySide2 import QtWidgets, QtCore
from PySide2.QtGui import QIcon, QGuiApplication, Qt

from lib.impartus import Impartus
from lib.threadlogging import ThreadLogger
from lib.variables import Variables
from ui.callbacks.utils import CallbackUtils
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

        Variables().set_log_window(self.content_window.log_window)
        self.thread_logger = ThreadLogger(self.__class__.__name__)
        self.logger = self.thread_logger.logger

        # initialize callbacks
        CallbackUtils().setup(
            impartus=self.impartus,
            login_window=self.login_window,
            content_window=self.content_window,
            app=self.app,
        )

        self.login_window.setup_ui(self.content_window)
        self.login_window.show()

        self.menu_bar = Menubar(self.login_window, self.content_window).add_menu()

    def run(self):
        self.app.exec_()


if __name__ == '__main__':
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    QGuiApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QGuiApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    App().run()

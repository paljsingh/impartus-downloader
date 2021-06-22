from PySide2 import QtWidgets, QtCore
from PySide2.QtGui import QIcon
from qtui.login import LoginWindow
from ui.data import IconFiles


if __name__ == '__main__':
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QtWidgets.QApplication([])
    app.setWindowIcon(QIcon(IconFiles.APP_LOGO.value))
    login_window = LoginWindow().setup_ui()
    login_window.show()

    app.exec_()

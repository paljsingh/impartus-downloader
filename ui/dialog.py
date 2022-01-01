from PySide2 import QtWidgets
from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader


class Dialog:
    """
    A generic dialog class that can be reused to display customized dialogs.
    Presently used in Help -> Check for Updates
    """

    def __init__(self, file, parent):
        loader = QUiLoader()
        file = QFile(file)
        file.open(QFile.ReadOnly)
        self.dialog = loader.load(file, parent)

        self.dialog.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        file.close()
        self.dialog.show()
        pass

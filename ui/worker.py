from typing import Callable

from PySide2 import QtCore

from lib.threadlogging import ThreadLogHandler


class Worker(QtCore.QThread):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.task = None
        self.log_handler = ThreadLogHandler()

    def set_task(self, func: Callable):
        self.task = func

    def run(self):
        if self.task:
            self.task()

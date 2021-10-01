import logging
from PySide2 import QtCore
from PySide2.QtCore import Signal

from lib.variables import Variables


class Model(QtCore.QObject):
    update = Signal(str)

    def __init__(self):
        super().__init__()
        pass


class ThreadLogHandler(logging.Handler):

    def __init__(self):
        super().__init__()
        self.model = Model()

    # logging.Handler.emit() is intended to be implemented by subclasses
    def emit(self, record):
        msg = self.format(record)
        self.model.update.emit(msg)     # noqa

    @QtCore.Slot(str)       # noqa
    def write_log(self, log_text):
        Variables().log_window().appendPlainText(log_text)
        Variables().log_window().centerCursor()  # scroll to the bottom


class ConsoleLogHandler(logging.Handler):

    def __init__(self):
        super().__init__()
        self.model = Model()

    # logging.Handler.emit() is intended to be implemented by subclasses
    def emit(self, record):
        msg = self.format(record)
        self.model.update.emit(msg)     # noqa

    @QtCore.Slot(str)       # noqa
    def write_log(self, log_text):
        print(log_text)


class ThreadLogger:

    loggers = dict()

    def __init__(self, logger_name: str = 'Worker'):

        # create logger for this class, and add it to a class dict.
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(logging.DEBUG)
        self.__class__.loggers[logger_name] = self.logger

        if not self.logger.hasHandlers():
            self.add_handler(self.logger, ConsoleLogHandler())

        # we want to direct all the logs to a ui text edit, which may not be available for till the content window
        # is drawn.
        # collect all the logger objects that are returned before creation of content_window
        # once the log window is available, map all the loggers with a handler.
        logger: logging.Logger
        for name, logger in self.__class__.loggers.items():
            # add threadlog handler only if the content window is available.
            if Variables().log_window() and len(logger.handlers) <= 1:
                self.add_handler(logger, ThreadLogHandler())

    def add_handler(self, logger, handler):  # noqa
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s'))

        # emit signal and write to app log window.
        handler.model.update.connect(handler.write_log)     # noqa
        logger.addHandler(handler)

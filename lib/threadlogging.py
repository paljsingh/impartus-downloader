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
        self.model.update.emit(msg)

    @QtCore.Slot(str)
    def write_log(self, log_text):
        Variables().log_window().appendPlainText(log_text)
        Variables().log_window().centerCursor()  # scroll to the bottom


class ThreadLogger:

    loggers = dict()

    def __init__(self, logger_name: str ='Worker'):

        # create logger for this class, and add it to a class dict.
        self.logger = logging.getLogger(logger_name)
        self.__class__.loggers[logger_name] = self.logger

        # we want to direct all the logs to a ui text edit, which may not be available for till the content window
        # is drawn.
        # collect all the logger objects that are returned before creation of content_window
        # once the log window is available, map all the loggers with a handler.
        if Variables().log_window():
            for name, logger in self.__class__.loggers.items():
                if not logger.hasHandlers():
                    self.add_handler(logger)

    def add_handler(self, logger):  # noqa
        # set up log handler
        log_handler = ThreadLogHandler()
        log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s'))
        # set the logging level
        logger.setLevel(logging.DEBUG)

        # emit signal and write to app log window.
        log_handler.model.update.connect(log_handler.write_log)
        logger.addHandler(log_handler)



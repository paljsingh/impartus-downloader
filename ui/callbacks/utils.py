from datetime import datetime

from PySide2.QtWidgets import QMainWindow


class CallbackUtils:

    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(CallbackUtils, cls)
            cls._instance = orig.__new__(cls)
        return cls._instance

    impartus = None
    login_window = None
    content_window = None
    app = None
    last_timestamp = 0.0

    def setup(self, impartus, login_window, content_window, app):
        self.impartus = impartus
        self.login_window = login_window
        self.content_window = content_window
        self.app = app

    def switch_windows(self, from_window: QMainWindow, to_window: QMainWindow):     # noqa
        """
        switch between two windows.
        """
        to_window.show()
        to_window.setVisible(True)
        to_window.setFocus()
        from_window.hide()
        return to_window

    def processEvents(self):    # noqa
        # process every n seconds at most
        n = 0.5
        if datetime.now().timestamp() - self.last_timestamp >= n:
            self.app.processEvents()
            self.last_timestamp = datetime.now().timestamp()

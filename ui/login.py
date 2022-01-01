from functools import partial
from typing import Callable

from PySide2 import QtWidgets
from PySide2.QtCore import QFile, QTimer
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QMainWindow

from lib.config import Config, ConfigType
from lib.core.impartus import Impartus
from ui.callbacks.utils import CallbackUtils
from lib.data.labels import ConfigKeys
from lib.data.labels import Labels
from lib.variables import Variables


class LoginWindow(QMainWindow):
    """
    Provides a Login window with a form to fill in credentials.
    Also owns a few handler methods to act upon the events on the login form.
    """

    def __init__(self, impartus: Impartus):
        super().__init__()
        self.conf = Config.load(ConfigType.CREDENTIALS)
        self.impartus = impartus
        self.login_form = None
        self.login_button = None
        self.content_window = None
        self.splashscreen = None

    def setup_ui(self, content_window):
        self.content_window = content_window
        loader = QUiLoader()
        file = QFile("ui/views/login.ui")
        file.open(QFile.ReadOnly)
        login_form = loader.load(file, self)
        self.setGeometry(400, 200, 800, 300)
        # window title
        self.setWindowTitle(Labels.LOGIN_TITLE.value)
        self.login_form = login_form
        file.close()

        # add connect to update values to python variables.
        self.login_form.url_box.textChanged.connect(partial(Variables().set_login_url))
        self.login_form.email_box.textChanged.connect(partial(Variables().set_login_email))
        self.login_form.password_box.textChanged.connect(partial(Variables().set_login_password))

        # credentials from config.
        url = self.conf[ConfigKeys.URL.value] if self.conf.get(ConfigKeys.URL.value) else ''
        login_form.url_box.setText(url)

        email = self.conf[ConfigKeys.EMAIL.value] if self.conf.get(ConfigKeys.EMAIL.value) else ''
        login_form.email_box.setText(email)

        password = self.conf[ConfigKeys.PASSWORD.value] if self.conf.get(ConfigKeys.PASSWORD.value) else ''
        login_form.password_box.setText(password)

        # mark the save credentials box checked, if credentials are prefilled.
        if url != '' and email != '' and password != '':
            self.login_form.save_credentials_checkbox.setChecked(True)

        # set focus to an unfilled box.
        if not url or url == '':
            login_form.url_box.setFocus()
        elif not email or email == '':
            login_form.email_box.setFocus()
        else:
            login_form.password_box.setFocus()

        # enable/disable login button when input changes...
        login_form.email_box.textChanged.connect(lambda: self.validate_inputs())
        login_form.password_box.textChanged.connect(lambda: self.validate_inputs())
        login_form.url_box.textChanged.connect(lambda: self.validate_inputs())

        # validate the prefilled inputs and enable login button if needed.
        self.validate_inputs()

        login_form.login_button.clicked.connect(partial(self.on_login_click, CallbackUtils().switch_windows))

        login_form.work_offline_button.clicked.connect(
            partial(self.on_work_offline_click, CallbackUtils().switch_windows))
        login_form.show()
        return self.login_form

    def validate_inputs(self):
        if self.login_form.email_box.text() == '' or self.login_form.password_box.text() == '' or \
                self.login_form.url_box.text() == '':
            self.login_form.login_button.setEnabled(False)
        else:
            self.login_form.login_button.setEnabled(True)
        pass

    def on_login_click(self, switch_window_callback: Callable):
        url = self.login_form.url_box.text()
        email = self.login_form.email_box.text()
        password = self.login_form.password_box.text()

        if url == '' or email == '' or password == '':
            return

        # save credentials / forget credentials (email/password only).
        if self.login_form.save_credentials_checkbox.isChecked():
            self.conf[ConfigKeys.URL.value] = url
            self.conf[ConfigKeys.EMAIL.value] = email
            self.conf[ConfigKeys.PASSWORD.value] = password
        else:
            self.conf[ConfigKeys.EMAIL.value] = ''
            self.conf[ConfigKeys.PASSWORD.value] = ''
        Config.save(ConfigType.CREDENTIALS)

        status = self.impartus.login()
        if status:
            switch_window_callback(
                from_window=self,
                to_window=self.content_window
            )
            QTimer.singleShot(1, self.content_window.work_online)
        else:
            QtWidgets.QErrorMessage(self).showMessage(
                'Error authenticating to {}. See console logs for details.'.format(url)
            )

    def on_work_offline_click(self, switch_window_callback: Callable):
        switch_window_callback(
            from_window=self,
            to_window=self.content_window
        )

        QTimer.singleShot(1, self.content_window.work_offline)

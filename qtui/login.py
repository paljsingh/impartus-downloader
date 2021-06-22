from PySide2 import QtWidgets
from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader

from qtui.content import ContentWindow
from lib.config import Config, ConfigType
from lib.impartus import Impartus
from ui.data import ConfigKeys


class LoginWindow:
    def __init__(self):
        self.conf = Config.load(ConfigType.CREDENTIALS)
        self.impartus = Impartus()
        self.login_form = None
        self.login_button = None

    def setup_ui(self):
        loader = QUiLoader()
        file = QFile("qtui/login.ui")
        file.open(QFile.ReadOnly)
        login_form = loader.load(file, None)
        self.login_form = login_form
        file.close()

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

        login_form.login_button.clicked.connect(lambda: self.on_login_click())

        login_form.work_offline_button.clicked.connect(lambda: self.on_work_offline_click())
        return self.login_form

    def validate_inputs(self):
        if self.login_form.email_box.text() == '' or self.login_form.password_box.text() == '' or \
                self.login_form.url_box.text() == '':
            self.login_form.login_button.setEnabled(False)
        else:
            self.login_form.login_button.setEnabled(True)
        pass

    def on_login_click(self):
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

        status = self.impartus.authenticate(email, password, url)
        if status:
            self._switch_to_content_window()
        else:
            QtWidgets.QErrorMessage().showMessage(
                'Error authenticating to {}. See console logs for details.'.format(url)
            )

    def on_work_offline_click(self):
        self._switch_to_content_window()

    def _switch_to_content_window(self):
        content_window = ContentWindow()
        content_window.show()
        self.login_form.close()


from ui.callbacks.utils import CallbackUtils


class ButtonCallbacks:

    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(ButtonCallbacks, cls)
            cls._instance = orig.__new__(cls)
        return cls._instance

    def set_pushbutton_statuses(self):  # noqa
        if CallbackUtils().impartus.is_authenticated():
            CallbackUtils().login_window.login_form.login_button.setEnabled(False)
        else:
            CallbackUtils().login_window.login_form.login_button.setEnabled(True)

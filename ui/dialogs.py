import logging
import tkinter as tk


class Dialogs:

    dialog = None
    logger = None

    def __new__(cls):
        if not hasattr(cls, '_instance'):
            orig = super(Dialogs, cls)
            cls._instance = orig.__new__(cls)

            cls.dialog = None
            cls.logger = logging.getLogger(cls.__name__)

        return cls._instance

    @classmethod
    def create_dialog(cls, on_close_callback=None, size='1000x500+100+100', title='Alert!'):
        if cls.dialog:
            cls.logger.warning('A top level dialog already exists.')
            return

        if not on_close_callback:
            on_close_callback = cls.on_dialog_close

        cls.dialog = tk.Toplevel()
        cls.dialog.protocol("WM_DELETE_WINDOW", on_close_callback)
        cls.dialog.geometry(size)
        cls.dialog.title(title)
        cls.dialog.grab_set()
        return cls.dialog

    @classmethod
    def on_dialog_close(cls, event=None):
        cls.dialog.destroy()
        cls.dialog = None

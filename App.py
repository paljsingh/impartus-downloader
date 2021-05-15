#!/usr/bin/env python3
import tkinter.messagebox
import tkinter.filedialog
import tkinter as tk
from functools import partial
from tkinter import font
import platform

from lib.config import Config, ConfigType
from lib.impartus import Impartus
from ui.colorschemes import ColorSchemes

from ui.login_form import LoginForm
from ui.content import Content
from ui.menubar import Menubar
from ui.toolbar import Toolbar


class App:
    def __init__(self):
        self.impartus = Impartus()
        self.app = self.create_app()

        self._init_ui()

    def create_app(self):   # noqa
        app = tkinter.Tk()

        # fix: askopenfiles dialog on linux by default shows white fg (foreground) on white bg
        # explicitely set foreground for TkFDialog to black.
        app.option_add('*TkFDialog*foreground', '#000000')
        app.option_add('*TkFDialog*background', '#dddddd')

        pad = 3
        screen_width = app.winfo_screenwidth() - pad
        screen_height = app.winfo_screenheight() - pad
        geometry = '{}x{}+0+0'.format(screen_width, screen_height)
        app.geometry(geometry)
        app.title('Impartus Downloader')
        app.rowconfigure(0, weight=0)
        app.rowconfigure(1, weight=1)
        app.columnconfigure(0, weight=1)

        img = tk.Image("photo", file='etc/id.png')
        app.iconphoto(True, img)

        conf = Config.load(ConfigType.IMPARTUS)
        content_font = conf.get('content_font').get(platform.system())
        content_font_size = conf.get('content_font_size')

        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family=content_font, size=content_font_size)
        text_font = font.nametofont("TkTextFont")
        text_font.configure(family=content_font, size=content_font_size)

        return app

    def _init_ui(self):
        """
        UI initialization.
        """
        self.menubar = Menubar()
        self.login = LoginForm()
        self.toolbar = Toolbar(self.app)
        self.content = Content(self.app, self.login, self.toolbar, self.menubar, self.impartus)
        self.colorschemes = ColorSchemes()

        callbacks_functions = {
            'authentication_callback': partial(self.content.show_video_callback, self.impartus),
            'auto_organize_callback': self.content.auto_organize,
            'set_display_columns_callback': self.content.set_display_columns,
            'set_colorscheme_callback': self.colorschemes.set_colorscheme,
        }
        self.menubar.add_menu(self.app, callbacks_functions)
        self.toolbar.add_toolbar(self.app, callbacks_functions)
        self.login.add_login_form(self.app, partial(self.content.show_video_callback, self.impartus))

        self.app.rowconfigure(0, weight=0)
        self.app.rowconfigure(1, weight=0)
        self.app.rowconfigure(2, weight=1)

        # register all the components for colorscheme updates.
        for comp in [self, self.content, self.toolbar, self.login]:
            self.colorschemes.register_component(comp)

        # set default color scheme.
        cs_configs = Config.load(ConfigType.COLORSCHEMES)
        default_cs = cs_configs[cs_configs['default']]
        self.colorschemes.set_colorscheme(default_cs)

        self.app.mainloop()

    def set_colorscheme(self, cs):
        self.app.config(bg=cs['root']['bg'])


if __name__ == '__main__':
    App()

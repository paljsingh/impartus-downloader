import os
import sys
import tkinter
from functools import partial

import tkinter as tk
from typing import Dict

from lib.config import Config, ConfigType
from lib.utils import Utils
from ui.colorschemes import ColorSchemes
from ui.columns import Columns
from ui.toolbar import Toolbar
from ui.vars import Variables


class Menubar:

    def __init__(self):
        self.dialog = None

    def add_menu(self, anchor, toolbar: Toolbar, callbacks: Dict):
        variables = Variables()
        menubar = tkinter.Menu(anchor)
        actions_menu = tkinter.Menu(menubar, tearoff=0)
        actions_menu.add_command(label=toolbar.labels.get('reload'), command=callbacks['authentication_callback'])
        actions_menu.add_command(label=toolbar.labels.get('auto_organize'), command=callbacks['auto_organize_callback'])
        actions_menu.add_separator()
        actions_menu.add_command(label="Quit", command=partial(sys.exit, 0))

        menubar.add_cascade(label="Actions", menu=actions_menu)

        view_menu = tkinter.Menu(menubar, tearoff=0)
        view_menu.add_command(label=toolbar.labels.get('columns'), state=tk.DISABLED)
        for key, item in Columns.display_columns.items():
            view_menu.add_checkbutton(
                label=item.get('display_name'), variable=variables.display_columns_vars(key),
                onvalue=1, offvalue=0, command=callbacks['set_display_columns_callback']
            )

        view_menu.add_separator()
        view_menu.add_command(label='Color Scheme', state=tk.DISABLED)
        for name, item in ColorSchemes.get_color_schemes().items():
            view_menu.add_radiobutton(label='⦿ {}'.format(name), variable=variables.colorscheme_var(), value=name,
                                      command=partial(callbacks['set_colorscheme_callback'], item),
                                      )
        view_menu.add_separator()
        menubar.add_cascade(label="View", menu=view_menu)

        video_menu = tkinter.Menu(menubar, tearoff=0)
        video_menu.add_command(label=toolbar.labels.get('flipped_quality'), state=tk.DISABLED)

        conf = Config.load(ConfigType.IMPARTUS)
        for item in ['highest', *conf.get('video_quality_order'), 'lowest']:
            video_menu.add_radiobutton(label=item, variable=variables.lecture_quality_var())
        menubar.add_cascade(label="Video", menu=video_menu)

        helpmenu = tkinter.Menu(menubar, tearoff=0)
        helpmenu.add_command(
            label="Documentation...",
            command=partial(Utils.open_file, os.path.join(os.path.abspath(os.curdir), 'etc/helpdoc.pdf'))
        )
        helpmenu.add_command(label="About...", command=self.about_dialog)
        menubar.add_cascade(label="Help", menu=helpmenu)

        anchor.config(menu=menubar)
        return menubar

    def about_dialog(self):
        # only 1 dialog at a time.
        if self.dialog:
            return

        dialog = tk.Toplevel()
        dialog.protocol("WM_DELETE_WINDOW", self.on_about_dialog_close)
        dialog.geometry("600x400+100+100")
        dialog.title('About...')
        dialog.grab_set()

        tk.Label(dialog, text='Version').grid(row=0, column=0, sticky='w', ipadx=10, ipady=10)
        tk.Label(dialog, text='foo').grid(row=0, column=1, sticky='w', ipadx=10, ipady=10)

        tk.Label(dialog, text='Check for updates', ).grid(row=1, column=0, sticky='w', ipadx=10, ipady=10)
        self.dialog = dialog

    def on_about_dialog_close(self):
        self.dialog.destroy()
        self.dialog = None

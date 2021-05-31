import os
import sys
import tkinter
from functools import partial

import tkinter as tk
from typing import Dict

import requests

from lib.config import Config, ConfigType
from lib.utils import Utils
from ui.colorschemes import ColorSchemes
from ui.data import Columns, Labels
from ui.dialogs import Dialogs
from ui.vars import Variables

from lib import version



class Menubar:

    def __init__(self):
        self.dialog = None
        self.main_menu = None
        self.help_menu = None
        self.video_menu = None
        self.view_menu = None
        self.actions_menu = None

        self.img = None

    def add_menu(self, anchor, callbacks: Dict):
        variables = Variables()
        menubar = tkinter.Menu(anchor)
        actions_menu = tkinter.Menu(menubar, tearoff=0)
        actions_menu.add_command(label=Labels.RELOAD, command=callbacks['authentication_callback'])
        actions_menu.add_command(label=Labels.AUTO_ORGANIZE, command=callbacks['auto_organize_callback'])
        actions_menu.add_separator()
        actions_menu.add_command(label=Labels.QUIT, command=partial(sys.exit, 0))

        menubar.add_cascade(label=Labels.ACTIONS, menu=actions_menu)

        view_menu = tkinter.Menu(menubar, tearoff=0)
        view_menu.add_command(label=Labels.COLUMNS, state=tk.DISABLED)
        for key, item in Columns.display_columns.items():
            view_menu.add_checkbutton(
                label=item.get('display_name'), variable=variables.display_columns_vars(key),
                onvalue=1, offvalue=0, command=callbacks['set_display_columns_callback']
            )

        view_menu.add_separator()
        view_menu.add_command(label=Labels.COLORSCHEME, state=tk.DISABLED)
        for name, item in ColorSchemes.get_color_schemes().items():
            view_menu.add_radiobutton(label='⦿ {}'.format(name), variable=variables.colorscheme_var(), value=name,
                                      command=partial(callbacks['set_colorscheme_callback'], item),
                                      )
        view_menu.add_separator()
        menubar.add_cascade(label=Labels.VIEW, menu=view_menu)

        video_menu = tkinter.Menu(menubar, tearoff=0)
        video_menu.add_command(label=str(Labels.FLIPPED_QUALITY), state=tk.DISABLED)

        conf = Config.load(ConfigType.IMPARTUS)
        for item in ['highest', *conf.get('video_quality_order'), 'lowest']:
            video_menu.add_radiobutton(label=item, variable=variables.lecture_quality_var())
        menubar.add_cascade(label=Labels.VIDEO, menu=video_menu)

        helpmenu = tkinter.Menu(menubar, tearoff=0)
        helpmenu.add_command(
            label=Labels.DOCUMENTATION,
            command=partial(Utils.open_file, os.path.join(os.path.abspath(os.curdir), 'docs/helpdoc.pdf'))
        )
        helpmenu.add_command(label=Labels.CHECK_FOR_UPDATES, command=self.about_dialog)
        menubar.add_cascade(label=Labels.HELP, menu=helpmenu)

        anchor.config(menu=menubar)
        self.main_menu = menubar
        self.help_menu = helpmenu
        self.video_menu = video_menu
        self.view_menu = view_menu
        self.actions_menu = actions_menu
        return menubar

    def about_dialog(self):
        current_version = version.__version_info__
        dialog = Dialogs.create_dialog(title='About...', size="600x600+100+100")

        frame1 = tk.Frame(dialog)
        frame1.grid(row=0, column=0, sticky='nsew', ipadx=10, ipady=10)

        # Logo
        self.img = tk.PhotoImage(file='etc/id.png')
        self.img = self.img.subsample(4, 4)
        lbl = tk.Label(frame1, image=self.img)
        lbl.grid(row=0, column=1, sticky='e', ipadx=10, ipady=10)

        # App title
        tk.Label(frame1, text='Impartus Downloader', font=("Arial Bold Italic", 16)).grid(
            row=0, column=3, sticky='w', ipadx=0, ipady=0)

        # current version
        tk.Label(frame1, text='version - {}'.format(current_version)).grid(
            row=1, column=2, sticky='ew', ipadx=10, ipady=10)

        releases = self.get_releases()
        latest_version = releases[0]['tag_name']
        if latest_version > current_version:
            download_link1 = tk.Label(frame1, text="latest - {}".format(latest_version), fg="yellow", cursor="hand2")
            download_link1.grid(row=2, column=2, sticky='ew', ipadx=10, ipady=10)
            download_link1.bind("<Button-1>", partial(Utils.open_file, releases[0]['zipball_url']))
        else:
            tk.Label(frame1, text="(latest)").grid(row=2, column=2, sticky='ew', ipadx=10, ipady=10)

        frame1.columnconfigure(0, weight=1)
        frame1.columnconfigure(3, weight=1)

        frame2 = tk.Frame(dialog)
        frame2.grid(row=1, column=0, sticky='nsew', ipadx=10, ipady=10)

        textbox = tk.Text(frame2)
        for rel in releases:
            textbox.insert(tk.END, '{}: {}\n\n'.format(rel['tag_name'], rel['name']))
            textbox.insert(tk.END, 'Published on: {}\n\n'.format(rel['published_at']))
            textbox.insert(tk.END, 'Changelist:\n\n{}\n\n'.format(rel['body'].strip()))
            textbox.insert(tk.END, '---------------\n\n')

        textbox.configure(state=tk.DISABLED)
        textbox.grid(row=0, column=0, sticky='nsew', ipadx=10, ipady=10)

        frame2.columnconfigure(0, weight=1)
        frame2.columnconfigure(2, weight=1)

        tk.Button(frame2, text='Close', command=Dialogs.on_dialog_close).grid(row=1, column=0, sticky='ew')
        dialog.bind("<Escape>", Dialogs.on_dialog_close)

        self.dialog = dialog

    def get_releases(self):
        url = 'https://api.github.com/repos/paljsingh/impartus-downloader/releases'
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()



from functools import partial
import tkinter as tk

from lib.config import ConfigType, Config
from ui.colorschemes import ColorSchemes
from ui.data import Columns, Labels
from ui.vars import Variables


class Toolbar:

    def __init__(self, app: tk.Tk):

        self.app = app

        # toolbar buttons
        self.reload_button = None
        self.auto_organize_button = None
        self.display_columns_dropdown = None
        self.flipped_video_quality_dropdown = None
        self.expected_real_paths_differ = False

        self.frame_toolbar = None

    def add_toolbar(self, anchor, callback_functions):
        variables = Variables()

        button_options = {
            'borderwidth': 0
        }
        grid_options = {
            'padx': 10, 'pady': 0, 'ipadx': 10, 'ipady': 0,
        }
        self.frame_toolbar = tk.Frame(anchor, padx=0, pady=0)

        # reload button
        self.reload_button = tk.Button(self.frame_toolbar, text=Labels.RELOAD,
                                       command=callback_functions['authentication_callback'], **button_options)
        self.reload_button.grid(row=0, column=1, **grid_options)

        # auto organize button
        self.auto_organize_button = tk.Button(self.frame_toolbar, text=Labels.AUTO_ORGANIZE,
                                              command=callback_functions['auto_organize_callback'], **button_options)
        self.auto_organize_button.grid(row=0, column=2, **grid_options)

        # columns dropdown
        columns_dropdown = tk.Menubutton(self.frame_toolbar, text=Labels.COLUMNS,
                                         **button_options)
        columns_dropdown.menu = tk.Menu(columns_dropdown, tearoff=1)
        columns_dropdown['menu'] = columns_dropdown.menu

        for key, item in Columns.display_columns.items():
            columns_dropdown.menu.add_checkbutton(
                label=item['display_name'], variable=variables.display_columns_vars(key), onvalue=1, offvalue=0,
                command=callback_functions['set_display_columns_callback']
            )
        columns_dropdown.grid(row=0, column=3, **grid_options)
        self.display_columns_dropdown = columns_dropdown

        # flipped lecture quality dropdown.
        lecture_quality_dropdown = tk.Menubutton(
            self.frame_toolbar, text=Labels.FLIPPED_QUALITY, **button_options
        )
        lecture_quality_dropdown.menu = tk.Menu(lecture_quality_dropdown, tearoff=1)
        lecture_quality_dropdown['menu'] = lecture_quality_dropdown.menu
        conf = Config.load(ConfigType.IMPARTUS)
        for display_name in ['highest', *conf.get('video_quality_order'), 'lowest']:
            lecture_quality_dropdown.menu.add_radiobutton(
                label=display_name, variable=variables.lecture_quality_var()
            )
        lecture_quality_dropdown.grid(row=0, column=4, **grid_options)
        self.flipped_video_quality_dropdown = lecture_quality_dropdown

        # color scheme change.
        grid_options_cs = {
            'padx': 0, 'pady': 0, 'ipadx': 0, 'ipady': 0,
        }

        i = 0
        for name, item in ColorSchemes.get_color_schemes().items():
            colorscheme_button = tk.Radiobutton(
                self.frame_toolbar, var=variables.colorscheme_var(), value=name, selectcolor="#000000",
                bg=item.get('theme_color'),
                command=partial(callback_functions['set_colorscheme_callback'], item)
            )
            colorscheme_button.grid(row=0, column=5 + i, **grid_options_cs, sticky='e')
            # Set the radio button to indicate currently active color scheme.
            i += 1

        # empty column, to keep columns 1-5 centered
        self.frame_toolbar.columnconfigure(0, weight=1)
        # move the color scheme buttons to extreme right
        self.frame_toolbar.columnconfigure(5, weight=1)

    def set_colorscheme(self, cs):
        self.frame_toolbar.configure(bg=cs['root']['bg'])

    def update(self, flipped=False):
        if flipped:
            self.flipped_video_quality_dropdown.configure(state='normal')
        else:
            self.flipped_video_quality_dropdown.configure(state='disabled')

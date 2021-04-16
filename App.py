#!/usr/bin/env python3

import tkinter.messagebox
import tkinter.filedialog
import tkinter as tk
from tkinter import font
from functools import partial
from tksheet import Sheet
import os
import ast
import threading
import shutil
import logging

from config import Config
from impartus import Impartus
from utils import Utils


class App:
    def __init__(self):
        # ui elements
        self.url_label = None
        self.url_box = None
        self.user_label = None
        self.user_box = None
        self.pass_label = None
        self.pass_box = None
        self.show_videos_button = None
        self.save_credentials_var = None
        self.save_credentials_button = None

        # element groups
        self.frame_auth = None
        self.frame_toolbar = None
        self.frame_content = None

        # content table
        self.sheet = None

        # sort options
        self.sort_by = None
        self.sort_order = None

        # threads for downloading videos / slides.
        self.threads = list()

        # root container
        self.app = None

        # backend
        self.impartus = None

        # dialog
        self.dialog = None

        # toolbar buttons
        self.reload_button = None
        self.move_files_button = None
        self.display_columns_dropdown = None
        self.colorscheme_buttons = list()
        self.display_columns_vars = list()
        self.expected_real_paths_differ = False

        # configs
        self.conf = Config.load('impartus')
        self.creds_config = Config.load('creds')
        self.colorscheme_config = Config.load('colorschemes')
        self.mappings_config = Config.load('mappings')
        self.colorscheme = self.colorscheme_config.get(self.colorscheme_config.get('default'))
        self.color_var = None   # to hold color-scheme value

        # content
        self.videos = None
        self.video_slide_mapping = None
        self.offline_video_ttid_mapping = None

        self._init_backend()
        self._init_ui()

    def _init_backend(self):
        """
        backend initialization.
        """
        self.impartus = Impartus()
        self.conf = Config.load('impartus')

        self.data_columns = {
            'subjectNameShort': {'display_name': 'Subject', 'title_case': False, 'sortable': True, 'editable': True,
                                 'original_values_col': 'subjectName', 'type': 'data'},
            'seqNo': {'display_name': 'Lecture #', 'title_case': False, 'sortable': True, 'editable': False,
                      'original_values_col': None, 'type': 'data'},
            'professorName': {'display_name': 'Professor', 'title_case': True, 'sortable': True, 'editable': False,
                              'original_values_col': None, 'type': 'data'},
            'topic': {'display_name': 'Topic', 'title_case': True, 'sortable': True, 'editable': False,
                      'original_values_col': None, 'type': 'data'},
            'actualDurationReadable': {'display_name': 'Duration', 'title_case': False, 'sortable': True,
                                       'editable': False, 'original_values_col': None, 'type': 'data'},
            'tapNToggle': {'display_name': 'Tracks', 'title_case': False, 'sortable': True, 'editable': False,
                           'original_values_col': None, 'type': 'data'},
            'startDate': {'display_name': 'Date', 'title_case': False, 'sortable': True, 'editable': False,
                          'original_values_col': None, 'type': 'data'},
        }
        # progress bar
        self.progressbar_column = {'downloaded': {'display_name': 'Downloaded?', 'title_case': False, 'sortable': True,
                                                  'type': 'progressbar'}}
        self.button_columns = {
            'download_video': {'display_name': 'Video', 'function': self.download_video, 'text': '⬇', 'type': 'button',
                               'state': 'download_video_state'},
            'play_video': {'display_name': 'Video', 'function': self.play_video, 'text': '▶', 'type': 'button',
                           'state': 'play_video_state'},
            'open_folder': {'display_name': 'Folder', 'function': self.open_folder, 'text': '⏏', 'type': 'button',
                            'state': 'open_folder_state'},
            'download_slides': {'display_name': 'Slides', 'function': self.download_slides, 'text': '⬇',
                                'type': 'button', 'state': 'download_slides_state'},
            'show_slides': {'display_name': 'Slides', 'function': self.show_slides, 'text': '▤', 'type': 'button',
                            'state': 'show_slides_state'},
            'add_slides': {'display_name': 'Slides', 'function': self.add_slides, 'text': '📎', 'type': 'button',
                           'state': 'add_slides_state'},
        }

        self.button_state_columns = {k: {'display_name': k, 'type': 'button_state'} for k in [
            'download_video_state',
            'play_video_state',
            'open_folder_state',
            'download_slides_state',
            'show_slides_state',
            'add_slides_state',
        ]}

        # index
        self.index_column = {'index': {'display_name': 'index', 'type': 'auto'}}
        self.metadata_column = {'metadata': {'display_name': 'metadata', 'type': 'metadata'}}

        # video / slides data
        self.orig_value_columns = {k: {'display_name': k, 'type': 'original_value'} for k in [
            'subjectName',
        ]}

        self.display_columns = {**self.data_columns, **self.progressbar_column, **self.button_columns}
        self.all_columns = {**self.data_columns, **self.progressbar_column, **self.button_columns,
                            **self.button_state_columns, **self.orig_value_columns, **self.index_column,
                            **self.metadata_column}
        self.column_names = [k for k in self.all_columns.keys()]
        self.headers = [v['display_name'] for v in self.display_columns.values()]

    def _init_ui(self):
        """
        UI initialization.
        """
        self.app = tkinter.Tk()

        pad = 3
        self.screen_width = self.app.winfo_screenwidth() - pad
        self.screen_height = self.app.winfo_screenheight() - pad
        geometry = '{}x{}+0+0'.format(self.screen_width, self.screen_height)
        self.app.geometry(geometry)
        self.app.title('Impartus Downloader')
        self.app.rowconfigure(0, weight=0)
        self.app.rowconfigure(1, weight=1)
        self.app.columnconfigure(0, weight=1)

        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family=self.conf.get('content_font'), size=self.conf.get('content_font_size'))
        text_font = font.nametofont("TkTextFont")
        text_font.configure(family=self.conf.get('content_font'), size=self.conf.get('content_font_size'))

        self.add_authentication_form(self.app)
        self.add_toolbar(self.app)
        self.add_content_frame(self.app)
        self.app.rowconfigure(0, weight=0)
        self.app.rowconfigure(1, weight=0)
        self.app.rowconfigure(2, weight=1)

        self.set_color_scheme()
        self.app.mainloop()

    def add_authentication_form(self, anchor):
        """
        Adds authentication widgets and blank frame for holding video/lectures data.
        """
        cs = self.colorscheme
        grid_options = {
            'padx': 10,
            'pady': 5,
            'sticky': 'w',
        }

        frame_auth = tk.Frame(anchor, padx=0, pady=0)
        frame_auth.grid(row=0, column=0)
        self.frame_auth = frame_auth

        # URL Label and Entry box.
        self.url_label = tk.Label(frame_auth, text='URL')
        self.url_label.grid(row=0, column=0, **grid_options)
        self.url_box = tk.Entry(frame_auth, width=30)
        self.url_box.insert(tk.END, self.conf.get('impartus_url'))
        self.url_box.grid(row=0, column=1, **grid_options)

        # Login Id Label and Entry box.
        self.user_label = tk.Label(frame_auth, text='Login (email) ')
        self.user_label.grid(row=1, column=0, **grid_options)
        self.user_box = tk.Entry(frame_auth, width=30)
        self.user_box.insert(tk.END, self.creds_config.get('login_email'))
        self.user_box.grid(row=1, column=1, **grid_options)

        self.pass_label = tk.Label(frame_auth, text='Password ')
        self.pass_label.grid(row=2, column=0, **grid_options)
        self.pass_box = tk.Entry(frame_auth, show="*", width=30)
        self.pass_box.insert(tk.END, self.creds_config.get('password'))
        self.pass_box.bind("<Return>", self.get_videos)
        self.pass_box.grid(row=2, column=1, **grid_options)

        self.save_credentials_var = tk.IntVar()
        self.save_credentials_button = tk.Checkbutton(frame_auth, text='Save Credentials', bg=cs['root']['bg'],
                                                      fg=cs['root']['fg'], variable=self.save_credentials_var)
        self.save_credentials_button.grid(row=2, column=2, **grid_options)

        self.show_videos_button = tk.Button(frame_auth, text='Show Videos', command=self.get_videos)
        self.show_videos_button.grid(row=3, column=1, **grid_options)

        # set focus to user entry if it is empty, else to password box.
        if self.user_box.get() == '':
            self.user_box.focus()
        else:
            self.pass_box.focus()

    def add_toolbar(self, anchor):
        button_options = {
            'borderwidth': 0
        }
        grid_options = {
            'padx': 10, 'pady': 0, 'ipadx': 10, 'ipady': 0,
        }
        self.frame_toolbar = tk.Frame(anchor, padx=0, pady=0)

        self.reload_button = tk.Button(self.frame_toolbar, text='Reload ⟳', command=self.get_videos, **button_options)
        self.reload_button.grid(row=0, column=1, **grid_options)

        self.move_files_button = tk.Button(self.frame_toolbar, text='Move / Rename Videos  ⇄', command=self.move_files,
                                           **button_options)
        self.move_files_button.grid(row=0, column=2, **grid_options)

        dropdown = tk.Menubutton(self.frame_toolbar, text='Columns', **button_options)
        dropdown.menu = tk.Menu(dropdown, tearoff=1)
        dropdown['menu'] = dropdown.menu
        for display_name in self.headers:
            item = tk.IntVar(None, 1)
            dropdown.menu.add_checkbutton(label=display_name, variable=item, onvalue=1, offvalue=0,
                                          command=self.set_display_columns)
            self.display_columns_vars.append(item)
        dropdown.grid(row=0, column=3, **grid_options)
        self.display_columns_dropdown = dropdown

        # empty column, to keep columns 1-5 centered
        self.frame_toolbar.columnconfigure(0, weight=1)
        # move the color scheme buttons to extreme right
        self.frame_toolbar.columnconfigure(4, weight=1)

        color_var = tk.IntVar()
        self.color_var = color_var
        grid_options_cs = {
            'padx': 0, 'pady': 0, 'ipadx': 0, 'ipady': 0,
        }

        i = 0
        for k in self.colorscheme_config.keys():
            # skip non-dict keys, skip nested keys
            if type(self.colorscheme_config[k]) == dict and '.' not in k:
                colorscheme_button = tk.Radiobutton(
                    self.frame_toolbar, var=color_var, value=i, bg=self.colorscheme_config[k].get('theme_color'),
                    command=partial(self.set_color_scheme, self.colorscheme_config[k])
                )
                colorscheme_button.grid(row=0, column=4+i, **grid_options_cs, sticky='e')
                self.colorscheme_buttons.append(colorscheme_button)

                # Set the radio button to indicate currently active color scheme.
                if self.colorscheme_config.get('default') == k:
                    self.color_var.set(i)
                i += 1

    def set_display_columns(self):
        column_states = [i for i, v in enumerate(self.display_columns_vars) if v.get() == 1]
        self.sheet.display_columns(indexes=column_states, enable=True, redraw=False)
        self.reset_column_sizes()
        self.sheet.refresh()

    def set_color_scheme(self, colorscheme=None):
        if colorscheme:
            self.colorscheme = colorscheme

        if not self.colorscheme:
            self.colorscheme = self.colorscheme_config.get(self.colorscheme_config.get('default'))

        cs = self.colorscheme
        self.app.config(bg=cs['root']['bg'])
        self.frame_auth.configure(bg=cs['root']['bg'])
        self.frame_content.configure(bg=cs['root']['bg'])
        self.frame_toolbar.configure(bg=cs['root']['bg'])

        color_options = {
            'fg': cs['root']['fg'],
            'bg': cs['root']['bg'],
        }
        self.url_label.configure(**color_options)
        self.url_box.configure(**color_options)
        self.user_label.configure(**color_options)
        self.user_box.configure(**color_options)
        self.pass_label.configure(**color_options)
        self.pass_box.configure(**color_options)

        if self.sheet:
            self.sheet.set_options(
                frame_bg=cs['table']['bg'],
                table_bg=cs['table']['bg'],
                table_fg=cs['table']['fg'],
                header_bg=cs['header']['bg'],
                header_fg=cs['header']['fg'],
                header_grid_fg=cs['table']['grid'],
                index_grid_fg=cs['table']['grid'],
                header_border_fg=cs['table']['grid'],
                index_border_fg=cs['table']['grid'],
                table_grid_fg=cs['table']['grid'],
                top_left_bg=cs['header']['bg'],
                top_left_fg=cs['header']['bg']
            )

            self.odd_even_color(redraw=False)
            self.progress_bar_color(redraw=False)
            self.set_button_status(redraw=False)
            self.sheet.refresh()

    def add_content_frame(self, anchor):
        frame_content = tk.Frame(anchor, padx=0, pady=0)
        frame_content.grid(row=2, column=0, sticky='nsew')
        self.frame_content = frame_content

    def get_videos(self, event=None):  # noqa
        """
        Callback function for 'Show Videos' button.
        Fetch video/lectures available to the user and display on the UI.
        """

        if self.save_credentials_var.get():
            self.creds_config['login_email'] = self.user_box.get()
            self.creds_config['password'] = self.pass_box.get()
            Config.save('creds')

        self.show_videos_button.config(state='disabled')
        self.reload_button.config(state='disabled')
        self.move_files_button.config(state='disabled')

        username = self.user_box.get()
        password = self.pass_box.get()
        root_url = self.url_box.get()
        if username == '' or password == '' or root_url == '':
            return

        if not self.impartus.session:
            success = self.impartus.authenticate(username, password, root_url)
            if not success:
                self.impartus.session = None
                tkinter.messagebox.showerror('Error', 'Error authenticating, see console logs for details.')
                self.show_videos_button.config(state='normal')
                return

        # hide the authentication frame.
        self.frame_auth.grid_forget()

        # show toolbar now.
        self.frame_toolbar.grid(row=1, column=0, sticky='ew')

        # show table of videos under frame_content
        self.set_display_widgets(self.frame_content)
        self.reload_button.config(state='normal')
        if self.expected_real_paths_differ:
            self.move_files_button.config(state='normal')

    def sort_table(self, args):
        """
        Sorts the table content.
        """
        col = args[1]
        real_col = self.get_real_col(col)
        self.sheet.deselect("all")

        col_name = self.column_names[real_col]
        if not self.all_columns[col_name].get('sortable'):
            return

        sort_by = col_name
        if sort_by == self.sort_by:
            sort_order = 'asc' if self.sort_order == 'desc' else 'desc'
        else:
            sort_order = 'desc'
        self.sort_by = sort_by
        self.sort_order = sort_order

        reverse = True if sort_order == 'desc' else False

        table_data = self.sheet.get_sheet_data()
        table_data.sort(key=lambda x: x[real_col], reverse=reverse)

        self.set_headers(sort_by, sort_order)
        self.set_button_status()
        self.sheet.refresh()

    def set_display_widgets(self, anchor):
        """
        Create the table/sheet.
        Fill in the data for table content, Set the buttons and their states.
        """
        sheet = Sheet(
            anchor,
            header_font=(self.conf.get("content_font"), self.conf.get('header_font_size'), "bold"),
            font=(self.conf.get('content_font'), self.conf.get('content_font_size'), "normal"),
            align='w',
            row_height="1",  # str value for row height in number of lines.
            row_index_align="w",
            auto_resize_default_row_index=False,
            row_index_width=40,
            header_align='center',
            empty_horizontal=0,
            empty_vertical=0,
        )
        self.sheet = sheet
        self.sheet.grid(row=0, column=0, sticky='nsew')

        self.sheet.enable_bindings((
            "single_select",
            "column_select",
            "column_width_resize",
            "double_click_column_resize",
            "edit_cell"
        ))

        self.set_headers()

        self.set_display_columns()
        anchor.columnconfigure(0, weight=1)
        anchor.rowconfigure(0, weight=1)
        self.sheet.extra_bindings('column_select', self.sort_table)
        self.sheet.extra_bindings('cell_select', self.on_click_button_handler)
        self.fetch_content()
        self.fill_content()

    def fetch_content(self):
        root_url = self.url_box.get()
        subject_dicts = self.impartus.get_subjects(root_url)
        self.videos = dict()
        self.video_slide_mapping = dict()
        for subject_dict in subject_dicts:
            videos_by_subject = self.impartus.get_videos(root_url, subject_dict)
            slides = self.impartus.get_slides(root_url, subject_dict)
            self.video_slide_mapping = self.impartus.map_slides_to_videos(videos_by_subject, slides)
            self.videos[subject_dict.get('subjectId')] = {x['ttid']:  x for x in videos_by_subject}

    def fill_content(self):
        # A mapping dict containing previously downloaded, and possibly moved around / renamed videos.
        # extract their ttid and map those to the correct records, to avoid forcing the user to re-download.
        self.offline_video_ttid_mapping = self.impartus.get_mkv_ttid_map()

        row = 0
        for subject_id, videos in self.videos.items():
            for ttid, video_metadata in videos.items():
                video_metadata = Utils.add_new_fields(video_metadata, self.video_slide_mapping)

                video_path = self.impartus.get_mkv_path(video_metadata)
                if not os.path.exists(video_path):
                    # or search from the downloaded videos, using video_ttid_map
                    video_path_moved = self.offline_video_ttid_mapping.get(str(ttid))

                    if video_path_moved:
                        # For now, use the offline path if a video found. Also set the flag to enable move/rename button
                        video_path = video_path_moved
                        self.expected_real_paths_differ = True

                slides_path = self.impartus.get_slides_path(video_metadata)

                video_exists_on_disk = video_path and os.path.exists(video_path)
                slides_exist_on_server = self.video_slide_mapping.get(ttid)
                slides_exist_on_disk, slides_path = self.impartus.slides_exist_on_disk(slides_path)

                metadata = {
                    'video_metadata': video_metadata,
                    'video_path': video_path,
                    'video_exists_on_disk': video_exists_on_disk,
                    'slides_exist_on_server': slides_exist_on_server,
                    'slides_exist_on_disk': slides_exist_on_disk,
                    'slides_url': self.video_slide_mapping.get(ttid),
                    'slides_path': slides_path,
                }
                row_items = list()
                button_states = list()

                # data items
                for col, (key, item) in enumerate(self.all_columns.items()):
                    text = ''
                    if item['type'] == 'data':
                        text = video_metadata[key]
                        # title case
                        if item.get('title_case'):
                            text = " ".join(text.splitlines()).strip().title()
                    elif item['type'] == 'auto':
                        text = row
                    elif item['type'] == 'progressbar':
                        if video_exists_on_disk:
                            text = self.progress_bar_text(100, processed=True)
                        else:
                            text = self.progress_bar_text(0)
                    elif item['type'] == 'button':
                        button_states.append(self.get_button_state(
                            key, video_exists_on_disk, slides_exist_on_server, slides_exist_on_disk)
                        )
                        text = item.get('text')
                    elif item['type'] == 'button_state':
                        text = button_states.pop(0)
                    elif item['type'] == 'metadata':
                        text = metadata
                    elif item['type'] == 'original_value':
                        text = video_metadata[key]
                    row_items.append(text)

                self.sheet.insert_row(values=row_items, idx='end')
                row += 1

        self.reset_column_sizes()
        self.decorate()

        # update button status
        self.set_button_status(redraw=True)
        self.sheet.grid(row=0, column=0, sticky='nsew')

    def set_headers(self, sort_by=None, sort_order=None):
        """
        Set the table headers.
        """
        # set column title to reflect sort status
        headers = list()
        for name, value in self.display_columns.items():
            if value.get('sortable'):
                if name == sort_by:
                    sort_icon = '▼' if sort_order == 'desc' else '▲'
                else:
                    sort_icon = '⇅'
                text = '{} {}'.format(value['display_name'], sort_icon)
            else:
                text = value['display_name']

            if value.get('editable'):
                text = '✎ {}'.format(text)

            headers.append(text)
        self.sheet.headers(headers)

    def decorate(self):
        """
        calls multiple ui related tweaks.
        """
        self.align_columns()
        self.set_color_scheme()
        self.odd_even_color()
        self.progress_bar_color()

    def align_columns(self):
        # data and progressbar west/left aligned, button center aligned.
        self.sheet.align_columns([self.column_names.index(k) for k in self.data_columns.keys()], align='w')
        self.sheet.align_columns([self.column_names.index(k) for k in self.progressbar_column.keys()], align='w')
        self.sheet.align_columns([self.column_names.index(k) for k in self.button_columns.keys()], align='center')

    def progress_bar_color(self, redraw=True):
        """
        Set progress bar color.
        """
        col = self.column_names.index('downloaded')
        num_rows = self.sheet.total_rows()
        cs = self.colorscheme

        for row in range(num_rows):
            odd_even_bg = cs['odd_row']['bg'] if row % 2 else cs['even_row']['bg']
            self.sheet.highlight_cells(
                row, col, fg=cs['progressbar']['fg'], bg=odd_even_bg, redraw=redraw)

    def odd_even_color(self, redraw=False):
        """
        Apply odd/even colors for table for better looking UI.
        """
        cs = self.colorscheme
        num_rows = self.sheet.total_rows()

        self.sheet.highlight_rows(
            list(range(0, num_rows, 2)),
            bg=cs['even_row']['bg'],
            fg=cs['even_row']['fg'],
            redraw=redraw
        )
        self.sheet.highlight_rows(
            list(range(1, num_rows, 2)),
            bg=cs['odd_row']['bg'],
            fg=cs['odd_row']['fg'],
            redraw=redraw
        )

    def reset_column_sizes(self):
        """
        Adjust column sizes after data has been filled.
        """
        # resize cells
        self.sheet.set_all_column_widths()

        # reset column widths to fill the screen
        pad = 5
        column_widths = self.sheet.get_column_widths()
        table_width = self.sheet.RI.current_width + sum(column_widths) + len(column_widths) + pad
        diff_width = self.frame_content.winfo_width() - table_width

        # adjust extra width only to top N data columns
        n = 3
        column_states = [v.get() for v in self.display_columns_vars]
        count = 0
        for k, v in enumerate(column_states):
            if self.column_names[k] == 'downloaded':
                break
            count += v
        # range(0..count) is all data columns.
        data_col_widths = {k: v for k, v in enumerate(column_widths[:count])}
        top_n_cols = sorted(data_col_widths, key=data_col_widths.get, reverse=True)[:n]
        for i in top_n_cols:
            self.sheet.column_width(i, column_widths[i] + diff_width // n)

    def set_button_status(self, redraw=False):
        """
        reads the states of the buttons from the hidden state columns, and sets the button states appropriately.
        """
        col_indexes = [x for x, v in enumerate(self.all_columns.values()) if v['type'] == 'button_state']
        num_buttons = len(col_indexes)
        for row, row_item in enumerate(self.sheet.get_sheet_data()):
            for col in col_indexes:
                # data set via sheet.insert_row retains tuple/list's element data type,
                # data set via sheet.set_cell_data makes everything a string.
                # Consider everything coming out of a sheet as string to avoid any issues.
                state = str(row_item[col])

                if state == 'True':
                    self.enable_button(row, col - num_buttons, redraw=redraw)
                elif state == 'False':
                    self.disable_button(row, col - num_buttons, redraw=redraw)

    def get_button_state(self, key, video_exists_on_disk, slides_exist_on_server, slides_exist_on_disk):  # noqa
        """
        Checks to identify when certain buttons should be enabled/disabled.
        """
        state = True
        if key == 'download_video' and video_exists_on_disk:
            state = False
        elif key == 'open_folder' and not video_exists_on_disk:
            state = False
        elif key == 'play_video' and not video_exists_on_disk:
            state = False
        elif key == 'download_slides' and (slides_exist_on_disk or not slides_exist_on_server):
            state = False
        elif key == 'show_slides' and not slides_exist_on_disk:
            state = False
        return state

    def get_real_col(self, col):
        """
        with configurable column list, the col number returned by tksheet may not be the same as
        column no from self.all_columns/self.display_columns. Use self.display_column_vars to identify and return
        the correct column.
        """
        # find n-th visible column, where n=col
        i = 0
        for c, state in enumerate(self.display_columns_vars):
            if state.get() == 1:
                if i == col:
                    return c
                i += 1

    def end_edit_cell(self, old_value, event=None):
        row, col = (event[0], event[1])
        new_value = self.sheet.get_text_editor_value(
            event,
            r=row,
            c=col,
            set_data_ref_on_destroy=True,
            move_down=True,
            redraw=True,
            recreate=True
        )

        # empty value or escape pressed.
        if not new_value or new_value == '':
            return

        # no changes made.
        if old_value == new_value:
            return

        self.expected_real_paths_differ = True
        self.move_files_button.config(state='normal')
        col_name = self.column_names[self.get_real_col(col)]
        columns_item = self.data_columns[col_name]
        orig_values_col_name = columns_item.get('original_values_col')
        original_value = self.sheet.get_cell_data(row, self.column_names.index(orig_values_col_name))
        for i, data in enumerate(self.sheet.get_column_data(self.column_names.index(orig_values_col_name))):
            if data == original_value:
                self.sheet.set_cell_data(i, col, new_value)
        self.update_mappings(orig_values_col_name, original_value, new_value)
        self.reset_column_sizes()
        self.sheet.refresh()

    def update_mappings(self, mapping_name, old_value, new_value):
        if not self.mappings_config.get(mapping_name):
            self.mappings_config[mapping_name] = {}
        self.mappings_config.get(mapping_name)[old_value] = new_value
        Config.save('mappings')

    def on_click_button_handler(self, args):
        """
        On click handler for all the buttons, calls the corresponding function as defined by self.button_columns
        """
        (event, row, col) = args
        real_col = self.get_real_col(col)

        # is subject field
        col_name = self.column_names[real_col]
        if self.all_columns[col_name].get('editable'):
            old_value = self.sheet.get_cell_data(row, real_col)
            self.sheet.create_text_editor(
                row=row,
                column=real_col,
                text=old_value,
                set_data_ref_on_destroy=False,
                binding=partial(self.end_edit_cell, old_value)
            )

        # not a button.
        if self.all_columns[col_name].get('type') != 'button':
            self.sheet.deselect('all', redraw=True)
            return

        # disabled button
        state_button_col_name, state_button_col_num = self.get_state_button(col_name)
        state = self.sheet.get_cell_data(row, state_button_col_num)
        if state == 'False':    # data read from sheet is all string.
            self.sheet.deselect('all', redraw=True)
            return

        # disable the button if it is one of the Download buttons, to prevent a re-download.
        if col_name in ['download_video', 'download_slides']:
            self.disable_button(row, real_col)

        func = self.all_columns[col_name]['function']
        func(row, real_col)

    def get_state_button(self, button_name):
        if self.all_columns[button_name].get('state'):
            state_col_name = self.all_columns[button_name].get('state')
            state_col_number = self.column_names.index(state_col_name)
            return state_col_name, state_col_number
        else:
            return None, None

    def disable_button(self, row, col, redraw=True):
        """
        Disable a button given it's row/col position.
        """
        cs = self.colorscheme
        self.sheet.highlight_cells(
            row, col, bg=cs['disabled']['bg'],
            fg=cs['disabled']['fg'],
            redraw=redraw
        )
        # update state field.
        state_button_col_name, state_button_col_num = self.get_state_button(self.column_names[col])
        self.sheet.set_cell_data(row, state_button_col_num, False, redraw=redraw)

    def enable_button(self, row, col, redraw=True):
        """
        Enable a button given it's row/col position.
        """
        cs = self.colorscheme
        odd_even_bg = cs['odd_row']['bg'] if row % 2 else cs['even_row']['bg']
        odd_even_fg = cs['odd_row']['fg'] if row % 2 else cs['even_row']['fg']
        self.sheet.highlight_cells(row, col, bg=odd_even_bg, fg=odd_even_fg, redraw=redraw)

        # update state field.
        state_button_col_name, state_button_col_num = self.get_state_button(self.column_names[col])
        self.sheet.set_cell_data(row, state_button_col_num, True, redraw=redraw)

    def get_index(self, row):
        """
        Find the values stored in the hidden column named 'Index', given a row record.
        In case the row value has been updated due to sorting the table, Index field helps identify the new location
        of the associated record.
        """
        # find where is the Index column
        index_col = self.column_names.index('index')
        # original row value as per the index column
        return self.sheet.get_cell_data(row, index_col)

    def get_row_after_sort(self, index_value):
        # find the new correct location of the row_index
        col_index = self.column_names.index('index')
        col_data = self.sheet.get_column_data(col_index)
        return col_data.index(index_value)

    def progress_bar_text(self, value, processed=False):
        """
        return progress bar text, calls the unicode/ascii implementation.
        """
        if self.conf.get('progress_bar') == 'unicode':
            text = self.progress_bar_text_unicode(value)
        else:
            text = self.progress_bar_text_ascii(value)

        pad = ' ' * 2
        if 0 < value < 100:
            percent_text = '{:2d}%'.format(value)
            status = percent_text
        elif value == 0:
            status = pad + '⃠' + pad
        else:   # 100 %
            if processed:
                status = pad + '✓' + pad
            else:
                status = pad + '⧗' + pad
        return '{} {}{}'.format(text, status, pad)

    def progress_bar_text_ascii(self, value):   # noqa
        """
        progress bar implementation with ascii characters.
        """
        bars = 50
        ascii_space = " "
        if value > 0:
            progress_text = '{}'.format('❘' * (value * bars // 100))
            empty_text = '{}'.format(ascii_space * (bars - len(progress_text)))
            full_text = '{}{} '.format(progress_text, empty_text)
        else:
            full_text = '{}'.format(ascii_space * bars)

        return full_text

    def progress_bar_text_unicode(self, value):    # noqa
        """
        progress bar implementation with unicode blocks.
        """
        chars = ['▏', '▎', '▍', '▌', '▋', '▊', '▉', '█']

        # 1 full unicode block = 8 percent values
        # => 13 unicode blocks needed to represent counter 100.
        unicode_space = ' '
        if value > 0:
            # progress_text: n characters, empty_text: 13-n characters
            progress_text = '{}{}'.format(chars[-1] * (value // 8), chars[value % 8])
            empty_text = '{}'.format(unicode_space * (13-len(progress_text)))
            full_text = '{}{}'.format(progress_text, empty_text)
        else:
            # all 13 unicode whitespace.
            full_text = '{} '.format(unicode_space * 13)
        return full_text

    def progress_bar_callback(self, count, row, col, processed=False):
        """
        Callback function passed to the backend, where it computes the download progress.
        Every time the function is called, it will update the progress bar value.
        """
        updated_row = self.get_row_after_sort(row)
        new_text = self.progress_bar_text(count, processed)
        if new_text != self.sheet.get_cell_data(updated_row, col):
            self.sheet.set_cell_data(updated_row, col, new_text, redraw=True)

    def _download_video(self, video_metadata, filepath, root_url, row, col):    # noqa
        """
        Download a video in a thread. Update the UI upon completion.
        """

        # create a new Impartus session reusing existing token.
        imp = Impartus(self.impartus.token)
        pb_col = self.column_names.index('downloaded')

        # # voodoo alert:
        # It is possible for user to sort the table while download is in progress.
        # In such a case, the row index supplied to the function call won't match the row index
        # required to update the correct progressbar/open/play buttons, which now exists at a new
        # location.
        # The hidden column index keeps the initial row index, and remains unchanged.
        # Use row_index to identify the new correct location of the progress bar.
        row_index = self.get_index(row)
        imp.process_video(video_metadata, filepath, root_url, 0,
                          partial(self.progress_bar_callback, row=row_index, col=pb_col))

        # download complete, enable open / play buttons
        updated_row = self.get_row_after_sort(row_index)
        # update progress bar status to complete.
        self.progress_bar_callback(row=row_index, col=pb_col, count=100, processed=True)

        # enable buttons.
        self.enable_button(updated_row, self.column_names.index('open_folder'))
        self.enable_button(updated_row, self.column_names.index('play_video'))

    def add_slides(self, row, col):     # noqa
        filepaths = tkinter.filedialog.askopenfilenames()

        data = self.read_metadata(row)
        slides_folder_path = os.path.dirname(data.get('video_path'))

        for filepath in filepaths:
            shutil.copy(filepath, slides_folder_path)

    def download_video(self, row, col):
        """
        callback function for Download button.
        Creates a thread to download the request video.
        """
        data = self.read_metadata(row)

        video_metadata = data.get('video_metadata')
        filepath = data.get('video_path')
        root_url = self.url_box.get()

        # note: args is a tuple.
        thread = threading.Thread(target=self._download_video, args=(video_metadata, filepath, root_url, row, col,))
        self.threads.append(thread)
        thread.start()

    def _download_slides(self, ttid, file_url, filepath, root_url, row):
        """
        Download a slide doc in a thread. Update the UI upon completion.
        """
        # create a new Impartus session reusing existing token.
        imp = Impartus(self.impartus.token)
        if imp.download_slides(ttid, file_url, filepath, root_url):
            # download complete, enable show slides buttons
            self.enable_button(row, self.column_names.index('show_slides'))
        else:
            tkinter.messagebox.showerror('Error', 'Error downloading slides, see console logs for details.')
            self.enable_button(row, self.column_names.index('download_slides'))

    def download_slides(self, row, col):    # noqa
        """
        callback function for Download button.
        Creates a thread to download the request video.
        """
        data = self.read_metadata(row)

        video_metadata = data.get('video_metadata')
        ttid = video_metadata['ttid']
        file_url = data.get('slides_url')
        filepath = data.get('slides_path')
        root_url = self.url_box.get()

        # note: args is a tuple.
        thread = threading.Thread(target=self._download_slides,
                                  args=(ttid, file_url, filepath, root_url, row,))
        self.threads.append(thread)
        thread.start()

    def read_metadata(self, row):
        """
        We saved a hidden column 'metadata' containing metadata for each record.
        Extract it, and eval it as python dict.
        """
        metadata_col = self.column_names.index('metadata')
        data = self.sheet.get_cell_data(row, metadata_col)
        return ast.literal_eval(data)

    def open_folder(self, row, col):    # noqa
        """
        fetch video_path's folder from metadata column's cell and open system launcher with it.
        """
        data = self.read_metadata(row)
        video_folder_path = os.path.dirname(data.get('video_path'))
        Utils.open_file(video_folder_path)

    def play_video(self, row, col):     # noqa
        """
        fetch video_path from metadata column's cell and open system launcher with it.
        """
        data = self.read_metadata(row)
        Utils.open_file(data.get('video_path'))

    def show_slides(self, row, col):    # noqa
        """
        fetch slides_path from metadata column's cell and open system launcher with it.
        """
        data = self.read_metadata(row)
        Utils.open_file(data.get('slides_path'))

    def move_files(self):
        self.move_files_button.config(state='disabled')

        logger = logging.getLogger(self.__class__.__name__)
        moved_files = dict()
        for subject_id, videos in self.videos.items():
            for ttid, video_metadata in videos.items():
                video_metadata = Utils.add_new_fields(video_metadata, self.video_slide_mapping)
                # for videos
                expected_video_path = self.impartus.get_mkv_path(video_metadata)
                real_video_path = self.offline_video_ttid_mapping.get(str(ttid))

                if real_video_path and expected_video_path != real_video_path and os.path.exists(real_video_path):
                    Utils.move_and_rename_file(real_video_path, expected_video_path)
                    logger.info('moved {} -> {}'.format(real_video_path, expected_video_path))
                    moved_files[real_video_path] = expected_video_path

                    # also check any slides.
                    for ext in self.conf.get('allowed_ext'):
                        slides_path = '{}.{}'.format(real_video_path[:-len(".mkv")], ext)
                        if os.path.exists(slides_path):
                            expected_slides_path = '{}.{}'.format(expected_video_path[:-len(".mkv")], ext)
                            Utils.move_and_rename_file(slides_path, expected_slides_path)
                            logger.info('moved {} -> {}'.format(slides_path, expected_slides_path))
                            moved_files[slides_path] = expected_slides_path

                    # is the folder empty, remove it.?
                    old_video_dir = os.path.dirname(real_video_path)
                    if len(os.listdir(old_video_dir)) == 0:
                        os.rmdir(old_video_dir)
                        logger.info('removed empty directory: {}'.format(old_video_dir))

        # show a dialog with the output.
        self.move_file_info_dialog(moved_files)
        self.expected_real_paths_differ = False

    def move_file_info_dialog(self, moved_files):
        # only 1 dialog at a time.
        if self.dialog:
            return
        dialog = tk.Toplevel()
        dialog.protocol("WM_DELETE_WINDOW", self.on_dialog_close)
        dialog.geometry("1000x400+100+100")
        dialog.title('Alert - file rename!')
        dialog.grab_set()

        title = tk.Label(dialog, text='Following files were moved / renamed -', )
        title.grid(row=0, column=0, sticky='w', ipadx=10, ipady=10)

        sheet = Sheet(
            dialog,
            header_font=(self.conf.get("content_font"), self.conf.get('header_font_size'), "bold"),
            font=(self.conf.get('content_font'), self.conf.get('content_font_size'), "normal"),
            align='w',
            row_height="1",  # str value for row height in number of lines.
            row_index_align="w",
            auto_resize_default_row_index=False,
            row_index_width=40,
            header_align='center',
            empty_horizontal=0,
            empty_vertical=0,
        )

        sheet.headers(['Source', '', 'Destination'])
        target_parent = os.path.dirname(self.impartus.download_dir)
        for row, (source, destination) in enumerate(moved_files.items()):
            source = source[len(target_parent)+1:]
            destination = destination[len(target_parent)+1:]
            sheet.insert_row([source, '⇨', destination])
            dialog.columnconfigure(0, weight=1)

        sheet.set_all_column_widths()
        sheet.grid(row=1, column=0, sticky='nsew')

        ok_button = tk.Button(dialog, text='OK', command=self.on_dialog_close)
        ok_button.grid(row=2, column=0, padx=10, pady=10)

        self.dialog = dialog

    def on_dialog_close(self):
        self.dialog.destroy()
        self.dialog = None
        self.get_videos()


if __name__ == '__main__':
    App()

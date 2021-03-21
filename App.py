#!/usr/bin/env python3
import tkinter.messagebox
import tkinter as tk
import tkinter.ttk as ttk
from tkscrolledframe import ScrolledFrame
from functools import partial
import os
import threading

from impartus import Impartus
from utils import Utils


class App:
    def __init__(self):
        # ui elements
        self.user_box = None
        self.pass_box = None
        self.url_box = None
        self.show_videos_button = None

        # element groups
        self.frame_auth = None
        self.frame_videos = None
        self.scrollable_frame = None

        # sort options
        self.sort_by = 'date'
        self.sort_order = None

        # for holding the widgets
        self.table_widgets = None
        self.header_widgets = None

        # hold the buttons
        self.progress_bar_values = list()
        self.download_video_buttons = list()
        self.download_slides_buttons = list()
        self.open_folder_buttons = list()
        self.play_video_buttons = list()
        self.show_slides_buttons = list()

        # style for buttons
        self.style = None

        # and threads ...
        self.threads = list()

        # root container
        self.app = None

        # backend
        self.impartus = None

        # fields
        self.columns = None

        self._init_backend()
        self._init_ui()

    def _init_ui(self):
        """
        UI initialization.
        """
        self.app = tkinter.Tk()
        pad = 3
        self.screen_width = self.app.winfo_screenwidth()-pad
        self.screen_height = self.app.winfo_screenheight()-pad
        geometry = '{}x{}+0+0'.format(self.screen_width, self.screen_height)
        self.app.geometry(geometry)
        self.app.title('Impartus Downloader')
        self.app.rowconfigure(0, weight=0)
        self.app.rowconfigure(1, weight=1)
        self.app.columnconfigure(0, weight=1)

        # style for buttons
        style = ttk.Style()
        style.map("TButton", foreground=[("active", "white"), ("disabled", "gray")])
        self.style = style

        self.add_auth_frame(self.app)
        self.app.mainloop()

    def _init_backend(self):
        """
        backend initialization.
        """
        self.impartus = Impartus()
        self.columns = {
            'sno': {'type': 'label', 'width': 5, 'header': '#', 'sortable': 0},
            'subject': {
                'type': 'label', 'width': 30, 'header': 'Subject', 'mapping': 'subjectNameShort', 'sortable': 1
            },
            'lec_no': {'type': 'label', 'width': 5, 'header': 'Lecture #', 'mapping': 'seqNo', 'sortable': 1},
            'prof': {
                'type': 'label', 'width': 30, 'header': 'Professor', 'mapping': 'professorName_raw', 'sortable': 1
            },
            'topic': {'type': 'label', 'width': 40, 'header': 'Topic', 'mapping': 'topic_raw', 'sortable': 1},
            'date': {'type': 'label', 'width': 10, 'header': 'Date', 'mapping': 'startDate', 'sortable': 1},
            'duration': {
                'type': 'label', 'width': 6, 'header': 'Duration', 'mapping': 'actualDurationReadable', 'sortable': 1
            },
            'tracks': {'type': 'label', 'width': 2, 'header': 'Tracks', 'mapping': 'tapNToggle', 'sortable': 1},
            'status': {'type': 'progressbar', 'width': 30, 'header': 'Downloaded?', 'sortable': 0},
        }

    def add_auth_frame(self, anchor):
        """
        Adds authentication widgets and blank frame for holding video/lectures data.
        """
        label_options = {
            'padx': 5,
            'pady': 5,
            'sticky': 'ew',
        }
        entry_options = {
            'padx': 5,
            'pady': 5,
        }

        frame_auth = tk.Frame(anchor, padx=0, pady=0)
        frame_auth.grid(row=0, column=0)
        self.frame_auth = frame_auth

        frame_videos = tk.Frame(anchor, padx=0, pady=0)
        frame_videos.grid(row=1, column=0, sticky='nsew')
        self.frame_videos = frame_videos

        # URL Label and Entry box.
        ttk.Label(frame_auth, text='URL').grid(row=0, column=0, **label_options)
        url_box = ttk.Entry(frame_auth, width=30)
        url_box.insert(tk.END, self.impartus.conf.get('impartus_url'))
        url_box.grid(row=0, column=1, **entry_options)

        # Login Id Label and Entry box.
        ttk.Label(frame_auth, text='Login (email) ').grid(row=1, column=0, **label_options)
        user_box = ttk.Entry(frame_auth, width=30)
        user_box.insert(tk.END, self.impartus.conf.get('login_email'))
        user_box.grid(row=1, column=1, **entry_options)

        ttk.Label(frame_auth, text='Password ').grid(row=2, column=0, **label_options)
        pass_box = ttk.Entry(frame_auth, text='', show="*", width=30)
        pass_box.bind("<Return>", self.get_videos)
        pass_box.grid(row=2, column=1, **entry_options)

        self.show_videos_button = ttk.Button(frame_auth, text='Show Videos', command=self.get_videos)
        self.show_videos_button.grid(row=2, column=2)

        self.user_box = user_box
        self.pass_box = pass_box
        self.url_box = url_box
        # set focus to user entry if it is empty, else to password box.
        if self.user_box.get() == '':
            self.user_box.focus()
        else:
            self.pass_box.focus()

    def get_videos(self, event=None):   # noqa
        """
        Callback function for 'Show Videos' button.
        Fetch video/lectures available to the user and display on the UI.
        """

        self.show_videos_button.config(state='disabled')
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
                return
        subjects = self.impartus.get_subjects(root_url)

        # show table of videos under frame_videos
        frame = self.frame_videos

        # make it scrollable.
        sf = ScrolledFrame(frame, use_ttk=True, width=self.screen_width-20, height=self.screen_height-300)
        sf.grid(row=0, column=0, sticky='nsew')

        # Bind the arrow keys and scroll wheel
        sf.bind_arrow_keys(frame)
        sf.bind_scroll_wheel(frame)

        frame_table = sf.display_widget(tk.Frame)

        self.scrollable_frame = sf
        self.scrollable_frame.focus()

        self.set_display_widgets(subjects, root_url, frame_table)
        self.sort_and_draw_widgets()

    def draw_widgets(self):     # noqa

        # hack #1 , hide and redisplay the table to speed up ui refresh.
        self.frame_videos.grid_remove()
        for key, item in self.header_widgets.items():
            display_text = self.columns.get(key)['header']
            if self.columns.get(key)['sortable']:
                if key == self.sort_by:
                    if self.sort_order == 'asc':
                        text = '{} ▲'.format(display_text)
                    else:
                        text = '{} ▼'.format(display_text)
                else:
                    text = '{} ↕'.format(display_text)
            else:
                text = '{}'.format(display_text)

            item.config(text=text)

        options = {'padx': 2, 'pady': 1}
        for row, row_widgets in enumerate(self.table_widgets):
            for col, cell_widget in enumerate(row_widgets):
                if col == 0:
                    cell_widget.config(text=row+1)

                cell_widget.grid(row=row+1, column=col, **options)
        self.frame_videos.grid(row=1, column=0)
        self.app.update_idletasks()

        # hack #2... bring focus on one of the widgets to force refresh.
        self.table_widgets[0][0].focus()

    def sort_and_draw_widgets(self, sort_by='date', event=None):    # noqa
        if not self.columns[sort_by].get('sortable'):
            return

        sort_orders = ['desc', 'asc']
        if sort_by == self.sort_by:
            if self.sort_order:
                sort_order = sort_orders[(sort_orders.index(self.sort_order)+1) % len(sort_orders)]
            else:
                sort_order = 'desc'
        else:
            sort_order = sort_orders[0]
        self.sort_by = sort_by
        self.sort_order = sort_order

        sort_by_index = list(self.columns.keys()).index(sort_by)
        self.table_widgets = sorted(self.table_widgets, key=lambda x: x[sort_by_index]['text'])
        if sort_order == 'desc':
            self.table_widgets.reverse()
        self.draw_widgets()

    def set_display_widgets(self, subjects, root_url, anchor):
        columns = self.columns
        widget_headers = dict()
        for i, key in enumerate(columns.keys()):
            item = columns.get(key)
            text = item.get('header') if item.get('header') else ''
            label = tk.Label(anchor, text=text, background='#666666')
            label.bind("<Button-1>", partial(self.sort_and_draw_widgets, key))
            label.grid(row=0, column=i, sticky='ew')
            widget_headers[key] = label
        self.header_widgets = widget_headers

        row = 1
        widgets_table = list()

        for subject in subjects:
            videos = self.impartus.get_videos(root_url, subject)
            slides = self.impartus.get_slides(root_url, subject)
            video_slide_mapping = self.impartus.map_slides_to_videos(videos, slides)

            for video_metadata in videos:
                video_metadata = Utils.add_fields(video_metadata, video_slide_mapping)
                video_metadata = Utils.sanitize(video_metadata)

                video_path = self.impartus.get_mkv_path(video_metadata)
                slides_path = self.impartus.get_slides_path(video_metadata)
                video_exists = os.path.exists(video_path)
                slides_exist_on_disk = os.path.exists(slides_path)

                widgets_row = list()

                for col_num, col_key in enumerate(columns.keys()):
                    col_item = columns[col_key]
                    if col_item['type'] == 'label':

                        width = col_item.get('width')
                        # truncate text for display purposes, if needed.
                        text = video_metadata[col_item.get('mapping')] if col_item.get('mapping') else row
                        text = ('{}..'.format(text[:width])) if len(str(text)) > width else text
                        widget_cell = ttk.Label(anchor, text=text)
                        widgets_row.append(widget_cell)
                        anchor.columnconfigure(col_num, weight=1)

                # progress bar
                progress_bar_value = tk.DoubleVar()
                if video_exists:
                    progress_bar = ttk.Progressbar(
                        anchor, orient=tk.HORIZONTAL, length=100, value=100, mode='determinate')
                else:
                    progress_bar = ttk.Progressbar(
                        anchor, orient=tk.HORIZONTAL, length=100, value=0, variable=progress_bar_value,
                        mode='determinate')
                widgets_row.append(progress_bar)
                self.progress_bar_values.append(progress_bar_value)

                # download button
                download_video_button = ttk.Button(anchor, text='⬇ Video', command=partial(
                    self.download_video, video_metadata, video_path, root_url, row))
                if video_exists:
                    download_video_button.config(state='disabled')
                widgets_row.append(download_video_button)
                self.download_video_buttons.append(download_video_button)

                # open button
                open_button = ttk.Button(anchor, text='⏏ Open', command=partial(
                    Utils.open_file, os.path.dirname(video_path)))
                if not video_exists:
                    open_button.config(state='disabled')
                widgets_row.append(open_button)
                self.open_folder_buttons.append(open_button)

                # play button
                play_button = ttk.Button(anchor, text='▶ Play', command=partial(Utils.open_file, video_path))
                if not video_exists:
                    play_button.config(state='disabled')
                widgets_row.append(play_button)
                self.play_video_buttons.append(play_button)

                # download slides button
                download_slides_button = ttk.Button(anchor, text='⬇ Slides', command=partial(
                    self.download_slides, video_metadata['ttid'], video_slide_mapping.get(video_metadata['ttid']),
                    slides_path, root_url, row))
                if slides_exist_on_disk or not video_slide_mapping.get(video_metadata['ttid']):
                    download_slides_button.config(state='disabled')
                widgets_row.append(download_slides_button)
                self.download_slides_buttons.append(download_slides_button)

                # show slides button
                show_slides_button = ttk.Button(anchor, text='▤ Slides', command=partial(
                    Utils.open_file, slides_path))
                if not slides_exist_on_disk:
                    show_slides_button.config(state='disabled')
                show_slides_button.grid(row=row, column=13)
                self.show_slides_buttons.append(show_slides_button)

                row += 1
                widgets_table.append(widgets_row)
        self.table_widgets = widgets_table

    def _download_video(self, video_metadata, filepath, root_url, index):
        """
        Download a video in a thread. Update the UI upon completion.
        """
        # create a new Impartus session reusing existing token.
        imp = Impartus(self.impartus.token)
        imp.process_video(video_metadata, filepath, root_url, self.progress_bar_values[index-1])

        # download complete, enable open / play buttons
        self.open_folder_buttons[index-1].config(state='active')
        self.play_video_buttons[index-1].config(state='active')

    def download_video(self, video_metadata, filepath, root_url, index):
        """
        callback function for Download button.
        Creates a thread to download the request video.
        """
        # disable download button.
        self.download_video_buttons[index-1].config(state='disabled')

        # note: args is a tuple.
        thread = threading.Thread(target=self._download_video, args=(video_metadata, filepath, root_url, index,))
        self.threads.append(thread)
        thread.start()

    def _download_slides(self, ttid, file_url, filepath, root_url, index):
        """
        Download a slide doc in a thread. Update the UI upon completion.
        """
        # create a new Impartus session reusing existing token.
        imp = Impartus(self.impartus.token)
        if imp.download_slides(ttid, file_url, filepath, root_url):
            # download complete, enable open / play buttons
            self.show_slides_buttons[index-1].config(state='active')
        else:
            tkinter.messagebox.showerror('Error', 'Error downloading slides, see console logs for details.')
            self.download_slides_buttons[index - 1].config(state='active')

    def download_slides(self, ttid, file_url, filepath, root_url, index):
        """
        callback function for Download button.
        Creates a thread to download the request video.
        """
        # disable download button.
        self.download_slides_buttons[index-1].config(state='disabled')

        # note: args is a tuple.
        thread = threading.Thread(target=self._download_slides, args=(ttid, file_url, filepath, root_url, index,))
        self.threads.append(thread)
        thread.start()


if __name__ == '__main__':
    App()

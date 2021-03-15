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
        self.frame_auth = None
        self.frame_videos = None
        self.user_box = None
        self.pass_box = None
        self.url_box = None
        self.scrollable_frame = None
        self.show_videos_button = None
        self.style = None

        self.progress_bar_values = list()
        self.download_video_buttons = list()
        self.download_slides_buttons = list()
        self.open_folder_buttons = list()
        self.play_video_buttons = list()
        self.show_slides_buttons = list()

        self.threads = list()

        self.app = None
        self.impartus = None
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

        self._add_content(self.app)
        self.app.mainloop()

    def _init_backend(self):
        """
        backend initialization.
        """
        self.impartus = Impartus()

    def _add_content(self, anchor):
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
        self.show_videos_button.grid(row=3, column=0)

        self.user_box = user_box
        self.pass_box = pass_box
        self.url_box = url_box
        # set focus to user entry if it is empty, else to password box.
        if self.user_box.get() == '':
            self.user_box.focus()
        else:
            self.pass_box.focus()

    def get_videos(self, event=None):
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

        columns = {
            'sno': {'display': '#', 'width': 5},
            'subject': {'display': 'Subject', 'width': 20, 'mapping_field': 'Subject'},
            'lec_no': {'display': 'Lecture #', 'width': 5, 'mapping_field': 'seqNo'},
            'prof': {'display': 'Professor', 'width': 20, 'mapping_field': 'professorName'},
            'topic': {'display': 'Topic', 'width': 40, 'mapping_field': 'topic'},
            'date': {'display': 'Date', 'width': 11, 'mapping_field': 'startDate'},
            'duration': {'display': 'Duration', 'width': 6, 'mapping_field': 'actualDurationReadable'},
            'tracks': {'display': 'Tracks', 'width': 2, 'mapping_field': 'tapNToggle'},
            'downloaded': {'display': 'Downloaded?', 'width': 10},
            'icon_download_video': {'display': ' ', 'width': 6},
            'icon_open_folder': {'display': ' ', 'width': 6},
            'icon_play_video': {'display': ' ', 'width': 6},
            'icon_download_slides': {'display': ' ', 'width': 6},
            'icon_show_slides': {'display': ' ', 'width': 6}
        }

        # make it scrollable.
        sf = ScrolledFrame(frame, use_ttk=True, width=self.screen_width-20, height=self.screen_height-300)
        sf.rowconfigure(0, weight=0)
        sf.columnconfigure(0, weight=1)
        sf.grid(row=0, column=0, sticky='nsew')

        # Bind the arrow keys and scroll wheel
        sf.bind_arrow_keys(frame)
        sf.bind_scroll_wheel(frame)

        frame_table = sf.display_widget(tk.Frame)

        self.scrollable_frame = sf

        for i, col in enumerate(columns.values()):
            tk.Label(frame_table, text=col.get('display')).grid(row=0, column=i)

        row = 1
        for subject in subjects:
            videos = self.impartus.get_videos(root_url, subject)
            slides = self.impartus.get_slides(root_url, subject)
            video_slide_mapping = self.impartus.map_slides_to_videos(videos, slides)
            for video_metadata in videos:
                video_metadata = Utils.sanitize(video_metadata)
                if video_metadata.get('subjectNameShort'):
                    subject_name = video_metadata.get('subjectNameShort')
                else:
                    subject_name = video_metadata.get('subjectName')

                video_path = self.impartus.get_mkv_path(video_metadata)
                slides_path = self.impartus.get_slides_path(video_metadata)
                video_exists = os.path.exists(video_path)
                slides_exist_on_disk = os.path.exists(slides_path)

                ttk.Label(frame_table, text=row).grid(row=row, column=0)
                ttk.Label(frame_table, text=subject_name).grid(row=row, column=1)
                ttk.Label(frame_table, text=video_metadata.get('seqNo')).grid(row=row, column=2)
                ttk.Label(frame_table, text=video_metadata.get('professorName')).grid(row=row, column=3)
                ttk.Label(frame_table, text=video_metadata.get('topic')).grid(row=row, column=4)
                ttk.Label(frame_table, text=video_metadata.get('startDate')).grid(row=row, column=5)
                ttk.Label(frame_table, text=video_metadata.get('actualDurationReadable')).grid(row=row, column=6)
                ttk.Label(frame_table, text=video_metadata.get('tapNToggle')).grid(row=row, column=7)

                # progress bar
                progress_bar_value = tk.DoubleVar()
                if video_exists:
                    ttk.Progressbar(frame_table, orient=tk.HORIZONTAL, length=100, value=100,
                                    mode='determinate').grid(row=row, column=8)
                else:
                    ttk.Progressbar(frame_table, orient=tk.HORIZONTAL, length=100, value=0,
                                    variable=progress_bar_value, mode='determinate').grid(row=row, column=8)
                self.progress_bar_values.append(progress_bar_value)

                # download button
                download_video_button = ttk.Button(frame_table, text='⬇ Video', command=partial(
                    self.download_video, video_metadata, video_path, root_url, row))
                if video_exists:
                    download_video_button.config(state='disabled')
                download_video_button.grid(row=row, column=9)
                self.download_video_buttons.append(download_video_button)

                # open button
                open_button = ttk.Button(frame_table, text='⏏ Open', command=partial(
                    Utils.open_file, os.path.dirname(video_path)))
                if not video_exists:
                    open_button.config(state='disabled')
                open_button.grid(row=row, column=10)
                self.open_folder_buttons.append(open_button)

                # play button
                play_button = ttk.Button(frame_table, text='▶ Play', command=partial(Utils.open_file, video_path))
                if not video_exists:
                    play_button.config(state='disabled')
                play_button.grid(row=row, column=11)
                self.play_video_buttons.append(play_button)

                # download slides button
                download_slides_button = ttk.Button(frame_table, text='⬇ Slides', command=partial(
                    self.download_slides, video_metadata['ttid'], video_slide_mapping.get(video_metadata['ttid']), slides_path, root_url, row))
                if slides_exist_on_disk or not video_slide_mapping.get(video_metadata['ttid']):
                    download_slides_button.config(state='disabled')
                download_slides_button.grid(row=row, column=12)
                self.download_slides_buttons.append(download_slides_button)

                # show pdf button
                show_slides_button = ttk.Button(frame_table, text='▤ Slides', command=partial(Utils.open_file, slides_path))
                if not slides_exist_on_disk:
                    show_slides_button.config(state='disabled')
                show_slides_button.grid(row=row, column=13)
                self.show_slides_buttons.append(show_slides_button)

                row += 1
                sf.rowconfigure(row, weight=1)
        # set focus
        self.scrollable_frame.focus()

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
        Download a slide/pdf in a thread. Update the UI upon completion.
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


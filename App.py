#!/usr/bin/env python3

import tkinter.filedialog 
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
        self.style = None

        self.progress_bar_values = list()
        self.download_buttons = list()
        self.open_buttons = list()
        self.play_buttons = list()

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
        geometry = '{}x{}+0+0'.format(self.app.winfo_screenwidth()-pad, self.app.winfo_screenheight()-pad)
        self.app.geometry(geometry)

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
        grid_options = {
            'padx': 5,
            'pady': 5,
        }
        label_options = {
            'padx': 5,
            'pady': 5,
            'sticky': tk.E,
        }
        entry_options = {
            'padx': 5,
            'pady': 5,
            'sticky': tk.E,
        }

        tk.Grid.rowconfigure(anchor, 0, weight=1)
        tk.Grid.columnconfigure(anchor, 0, weight=1)
        frame_auth = tk.Frame(anchor, width=1000, height=200, padx=10, pady=10, bg='grey')
        frame_auth.grid(row=0, column=0, **grid_options)
        self.frame_auth = frame_auth

        frame_videos = tk.Frame(anchor, width=1000, height=600, padx=10, pady=10)
        frame_videos.grid(row=1, column=0, **grid_options)
        self.frame_videos = frame_videos

        # URL Label and Entry box.
        ttk.Label(frame_auth, text='URL').grid(row=0, column=0, **label_options)
        url_box = ttk.Entry(frame_auth, width=30)
        url_box.insert(tk.END, self.impartus.conf.get('impartus_url'))
        url_box.grid(row=0, column=1, **entry_options)

        # Username Label and Entry box.
        ttk.Label(frame_auth, text='Username ').grid(row=1, column=0, **label_options)
        user_box = ttk.Entry(frame_auth, width=30)
        user_box.insert(tk.END, self.impartus.conf.get('username'))
        user_box.grid(row=1, column=1, **entry_options)

        ttk.Label(frame_auth, text='Password ').grid(row=2, column=0, **label_options)
        pass_box = ttk.Entry(frame_auth, text='', show="*", width=30)
        pass_box.bind("<Return>", self.get_videos)
        pass_box.grid(row=2, column=1, **entry_options)

        ttk.Button(frame_auth, text='Show Videos', command=self.get_videos).grid(row=3, column=0, **grid_options)

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
        Callback function for 'List Videos' button.
        Fetch video/lectures list available to the user and display on the UI.
        """

        username = self.user_box.get()
        password = self.pass_box.get()
        root_url = self.url_box.get()
        if username == '' or password == '':
            return
        self.progress_bar_values.clear()
        self.download_buttons.clear()
        self.open_buttons.clear()
        self.play_buttons.clear()

        if not self.impartus.session:
            success = self.impartus.authenticate(username, password, root_url)
            if not success:
                self.impartus.session = None
                tkinter.messagebox.showerror('Error', 'Error authenticating.')
                return
        subjects = self.impartus.get_subjects(root_url)

        # show table of videos under frame_videos
        frame = self.frame_videos

        # make it scrollable.
        sf = ScrolledFrame(frame, width=1400, height=600, use_ttk=True)
        sf.grid(row=0, column=0)

        # Bind the arrow keys and scroll wheel
        sf.bind_arrow_keys(frame)
        sf.bind_scroll_wheel(frame)

        frame_table = sf.display_widget(tk.Frame)

        self.scrollable_frame = sf

        for i, col in enumerate(list(['Subject', 'Lecture No.', 'Professor', 'Topic', 'Date', 'Duration', 'Tracks', 'Downloaded?'])):
            tk.Label(frame_table, text=col).grid(row=0, column=i)

        row = 1
        for subject in subjects:
            videos = self.impartus.get_videos(root_url, subject)
            for video_metadata in videos:
                video_metadata = Utils.sanitize(video_metadata)
                if video_metadata.get('subjectNameShort'):
                    subject_name = video_metadata.get('subjectNameShort')
                else:
                    subject_name = video_metadata.get('subjectName')
                ttk.Label(frame_table, text=subject_name).grid(row=row, column=0)
                ttk.Label(frame_table, text=video_metadata.get('seqNo')).grid(row=row, column=1)
                ttk.Label(frame_table, text=video_metadata.get('professorName')).grid(row=row, column=2)
                ttk.Label(frame_table, text=video_metadata.get('topic')).grid(row=row, column=3)
                ttk.Label(frame_table, text=video_metadata.get('startDate')).grid(row=row, column=4)
                ttk.Label(frame_table, text=video_metadata.get('actualDurationReadable')).grid(row=row, column=5)
                ttk.Label(frame_table, text=video_metadata.get('tapNToggle')).grid(row=row, column=6)
                filepath = self.impartus.get_mkv_path(video_metadata)
                file_exists = os.path.exists(filepath)

                # progress bar
                progress_bar_value = tk.DoubleVar()
                if file_exists:
                    ttk.Progressbar(frame_table, orient=tk.HORIZONTAL, length=100, value=100,
                                    mode='determinate').grid(row=row, column=7)
                else:
                    ttk.Progressbar(frame_table, orient=tk.HORIZONTAL, length=100, value=0,
                                    variable=progress_bar_value, mode='determinate').grid(row=row, column=7)
                self.progress_bar_values.append(progress_bar_value)

                # download button
                download_button = ttk.Button(frame_table, text='Download', command=partial(
                    self.download_video, video_metadata, filepath, root_url, row))
                if os.path.exists(filepath):
                    download_button.config(state='disabled')
                download_button.grid(row=row, column=8)
                self.download_buttons.append(download_button)

                # open button
                open_button = ttk.Button(frame_table, text='Open', command=partial(
                    Utils.open_file, os.path.dirname(filepath)))
                if not os.path.exists(filepath):
                    open_button.config(state='disabled')
                open_button.grid(row=row, column=9)
                self.open_buttons.append(open_button)

                # play button
                play_button = ttk.Button(frame_table, text='Play️', command=partial(Utils.open_file, filepath))
                if not os.path.exists(filepath):
                    play_button.config(state='disabled')
                play_button.grid(row=row, column=10)
                self.play_buttons.append(play_button)

                row += 1
        # set focus
        self.scrollable_frame.focus()

    def _download_video_thread(self, video_metadata, filepath, root_url, index):
        """
        Download a video in a thread. Update the UI upon completion.
        """
        # create a new Impartus session reusing existing token.
        imp = Impartus(self.impartus.token)
        imp.process_video(video_metadata, filepath, root_url, self.progress_bar_values[index-1])

        # download complete, enable open / play buttons
        self.open_buttons[index-1].config(state='active')

        self.play_buttons[index-1].config(state='active')

    def download_video(self, video_metadata, filepath, root_url, index):
        """
        callback function for Download button.
        Creates a thread to download the request video.
        """
        # disable download button.
        self.download_buttons[index-1].config(state='disabled')

        thread = threading.Thread(target=self._download_video_thread, args=(video_metadata, filepath, root_url, index,))
        self.threads.append(thread)
        thread.start()


if __name__ == '__main__':
    App()


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
        self.pass_box = None
        self.pass_box = None
        self.url_box = None
        self.progress_bar_values = list()
        self.threads = list()

        self.app = None
        self.impartus = None
        self._init_backend()
        self._init_ui()

    def _init_ui(self):
        self.app = tkinter.Tk()
        pad = 3
        geometry = '{}x{}+0+0'.format(self.app.winfo_screenwidth()-pad, self.app.winfo_screenheight()-pad)
        self.app.geometry(geometry)
        self._add_content(self.app)
        self.app.mainloop()

    def _init_backend(self):
        self.impartus = Impartus()

    def donothing(self):
        pass

    def _add_content(self, anchor):
        options = {
            'padx': 20,
            'pady': 5,
        }
        root_url = self.impartus.conf.get('impartus_url')
        frame_auth = tk.Frame(anchor, width=600, height=200, padx=100, pady=20, bg='grey')
        frame_auth.grid(row=0, column=0, **options)
        self.frame_auth = frame_auth

        frame_videos = tk.Frame(anchor, width=600, height=600, padx=100, pady=20, bg='grey')
        frame_videos.grid(row=1, column=0, **options)
        self.frame_videos = frame_videos

        tk.Label(frame_auth, borderwidth=1, text='URL').grid(row=0, column=0, **options)
        url_box = tk.Entry(frame_auth)
        url_box.insert(tk.END, root_url)
        url_box.grid(row=0, column=1, **options)

        tk.Label(frame_auth, text='Username ').grid(row=1, column=0, **options)
        user_box = tk.Entry(frame_auth, text='')
        user_box.grid(row=1, column=1, **options)

        tk.Label(frame_auth, text='Password ').grid(row=2, column=0, **options)
        pass_box = tk.Entry(frame_auth, text='', show="*")
        pass_box.grid(row=2, column=1, **options)

        tk.Button(frame_auth, text='List Videos', command=self.get_videos).grid(row=3, column=0, **options)

        self.user_box = user_box
        self.pass_box = pass_box
        self.url_box = url_box

    def get_videos(self):
        username = self.user_box.get()
        password = self.pass_box.get()
        root_url = self.url_box.get()
        if not self.impartus.session:
            success = self.impartus.authenticate(username, password, root_url)
            if not success:
                tkinter.messagebox.showerror('Error', 'Error authenticating.')
                return
        else:
            print("already authenticated")
        subjects = self.impartus.get_subjects(root_url)

        # show only the subjects user is interested in.
        if len(subjects):
            subjects = self.impartus.filter_subjects(subjects)

        # show table of videos under frame_videos
        frame = self.frame_videos

        # make it scrollable.
        sf = ScrolledFrame(frame, width=1200, height=600)
        sf.grid(row=0, column=0)
        # Bind the arrow keys and scroll wheel
        sf.bind_arrow_keys(frame)
        sf.bind_scroll_wheel(frame)

        frame_table = sf.display_widget(tk.Frame)
        for i, col in enumerate(list(['Subject', 'Lecture No.', 'Professor', 'Topic', 'Date', 'Duration', 'Channels', 'Downloaded ?'])):
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
                tk.Label(frame_table, text=subject_name).grid(row=row, column=0)
                tk.Label(frame_table, text=video_metadata.get('seqNo')).grid(row=row, column=1)
                tk.Label(frame_table, text=video_metadata.get('professorName')).grid(row=row, column=2)
                tk.Label(frame_table, text=video_metadata.get('topic')).grid(row=row, column=3)
                tk.Label(frame_table, text=video_metadata.get('startDate')).grid(row=row, column=4)
                duration_hour = int(video_metadata.get('actualDuration')) // 3600
                duration_min = (int(video_metadata.get('actualDuration')) % 3600 ) // 60
                tk.Label(frame_table, text='{}h{}m'.format(duration_hour, duration_min)).grid(row=row, column=5)
                tk.Label(frame_table, text=video_metadata.get('tapNToggle')).grid(row=row, column=6)
                filepath = self.impartus.get_mkv_path(video_metadata)
                progress_bar_value = tk.DoubleVar()
                if os.path.exists(filepath):
                    ttk.Progressbar(frame_table, orient=tk.HORIZONTAL, length=100, value=100,
                                    mode='determinate').grid(row=row, column=7)
                else:
                    ttk.Progressbar(frame_table, orient=tk.HORIZONTAL, length=100, value=0,
                                    variable=progress_bar_value, mode='determinate').grid(row=row, column=7)
                self.progress_bar_values.append(progress_bar_value)
                tk.Button(frame_table, text='Download', command=partial(self.download_video, video_metadata, filepath,
                                                                        root_url, row)).grid(row=row, column=8)
                
                row += 1

    def _download_video_thread(self, video_metadata, filepath, root_url, index):
        # create a new Impartus session reusing existing token.
        imp = Impartus(self.impartus.token)
        imp.process_video(video_metadata, filepath, root_url, self.progress_bar_values[index-1])

    def download_video(self, video_metadata, filepath, root_url, index):
        thread = threading.Thread(target=self._download_video_thread, args=(video_metadata, filepath, root_url, index,))
        self.threads.append(thread)
        thread.start()
        print("download video button pressed")


if __name__ == '__main__':
    App()


import tkinter.messagebox
import tkinter as tk
from lib.impartus import Impartus

from lib.config import Config, ConfigType


class LoginForm:

    def __init__(self):
        # ui elements
        self.frame_auth = None
        self.url_label = None
        self.url_box = None
        self.user_label = None
        self.user_box = None
        self.pass_label = None
        self.pass_box = None
        self.save_credentials_var = None
        self.save_credentials_button = None
        self.show_videos_button = None

    def add_login_form(self, anchor: tk.Tk, show_video_callback):
        """
        Adds authentication widgets and blank frame for holding video/lectures data.
        """
        colorschemes_config = Config.load(ConfigType.COLORSCHEMES)
        cs = colorschemes_config[colorschemes_config['default']]
        grid_options = {
            'padx': 10,
            'pady': 5,
            'sticky': 'w',
        }

        frame_auth = tk.Frame(anchor, padx=0, pady=0)
        frame_auth.grid(row=0, column=0, sticky='ns')
        self.frame_auth = frame_auth

        # URL Label and Entry box.
        creds_conf = Config.load(ConfigType.CREDENTIALS)
        self.url_label = tk.Label(frame_auth, text='URL')
        self.url_label.grid(row=0, column=0, **grid_options)
        self.url_box = tk.Entry(frame_auth, width=30)
        self.url_box.insert(tk.END, creds_conf.get('impartus_url'))
        self.url_box.grid(row=0, column=1, **grid_options)

        # Login Id Label and Entry box.
        self.user_label = tk.Label(frame_auth, text='Login (email) ')
        self.user_label.grid(row=1, column=0, **grid_options)
        self.user_box = tk.Entry(frame_auth, width=30)
        self.user_box.insert(tk.END, creds_conf.get('login_email'))
        self.user_box.grid(row=1, column=1, **grid_options)

        self.pass_label = tk.Label(frame_auth, text='Password ')
        self.pass_label.grid(row=2, column=0, **grid_options)
        self.pass_box = tk.Entry(frame_auth, show="*", width=30)
        self.pass_box.insert(tk.END, creds_conf.get('password'))
        self.pass_box.bind("<Return>", show_video_callback)
        self.pass_box.grid(row=2, column=1, **grid_options)

        self.save_credentials_var = tk.IntVar()
        self.save_credentials_button = tk.Checkbutton(
            frame_auth, text='Save Credentials',
            selectcolor="#000000", variable=self.save_credentials_var,
        )
        if creds_conf.get('login_email') and creds_conf.get('password'):
            self.save_credentials_var.set(1)  # select the checkbox if credentials already saved.
        self.save_credentials_button.grid(row=2, column=2, **grid_options)

        self.show_videos_button = tk.Button(self.frame_auth, text='Show Videos', command=show_video_callback)
        self.show_videos_button.grid(row=3, column=1, **grid_options)

        # set focus to user entry if it is empty, else to password box.
        if self.user_box.get() == '':
            self.user_box.focus()
        else:
            self.pass_box.focus()

    def authenticate(self, impartus: Impartus, event=None):  # noqa
        """
        Callback function for 'Show Videos' button.
        Fetch video/lectures available to the user and display on the UI.
        """

        creds_conf = Config.load(ConfigType.CREDENTIALS)
        if self.save_credentials_var.get():
            creds_conf['login_email'] = self.user_box.get()
            creds_conf['password'] = self.pass_box.get()
        else:
            creds_conf['login_email'] = ''
            creds_conf['password'] = ''
        Config.save(ConfigType.CREDENTIALS)

        self.show_videos_button.config(state='disabled')

        username = self.user_box.get()
        password = self.pass_box.get()
        root_url = self.url_box.get()
        if username == '' or password == '' or root_url == '':
            return

        if not impartus.session:
            success = impartus.authenticate(username, password, root_url)
            if not success:
                tkinter.messagebox.showerror('Error', 'Error authenticating, see console logs for details.')
                self.show_videos_button.config(state='normal')
                return

        # hide the authentication frame.
        self.frame_auth.grid_forget()

    def set_colorscheme(self, cs):
        self.frame_auth.configure(bg=cs['root']['bg'])

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
        self.save_credentials_button.configure(**color_options)

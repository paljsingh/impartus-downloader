import sys
from functools import partial

from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QAction, QMainWindow

from lib.config import ConfigType, Config
from lib.impartus import Impartus
from lib.utils import Utils
from ui.data import Columns, DocFiles


class Menubar:

    def __init__(self, login_window: QMainWindow, content_window: QMainWindow):
        self.login_window = login_window
        self.content_window = content_window
        self.impartus = Impartus()
        self.conf = Config.load(ConfigType.IMPARTUS)
        pass

    def add_menu(self, switch_window_callback):
        main_menu = self.content_window.menuBar()

        actions_menu = main_menu.addMenu('Actions')
        view_menu = main_menu.addMenu('View')
        video_menu = main_menu.addMenu('Video')
        slides_menu = main_menu.addMenu('Slides')
        help_menu = main_menu.addMenu('Help')

        # actions menu - login button
        login_button = QAction(QIcon.fromTheme('dialog-password'), 'Login', self.content_window)
        login_button.setShortcut('Ctrl+L')
        login_button.setStatusTip('Login')
        login_button.triggered.connect(partial(
            self.login_window.on_login_click,
            switch_window_callback
        ))
        actions_menu.addAction(login_button)
        if self.impartus.is_authenticated():
            login_button.setEnabled(False)

        # actions menu - reload button
        reload_button = QAction(QIcon.fromTheme('view-refresh'), 'Reload', self.content_window)
        reload_button.setShortcut('Ctrl+R')
        reload_button.setStatusTip('Refresh content')
        reload_button.triggered.connect(self.reload_content)
        actions_menu.addAction(reload_button)
        if not self.impartus.is_authenticated():
            reload_button.setEnabled(False)

        # actions menu - auto organize button
        auto_organize_button = QAction(QIcon.fromTheme('tools-check-spelling'), 'Auto Organize', self.content_window)
        auto_organize_button.setShortcut('Ctrl+/')
        auto_organize_button.setStatusTip('Rename video files, download chats...')
        auto_organize_button.triggered.connect(self.auto_organize)
        actions_menu.addAction(auto_organize_button)
        # disable auto-organize, if working offline, or
        # online but all up to date.
        if not self.impartus.is_authenticated() or \
                (not self.needs_lecture_rename() and not self.needs_chat_download()):
            auto_organize_button.setEnabled(False)

        # actions menu - exit button.
        exit_button = QAction(QIcon.fromTheme('application-exit'), 'Quit', self.content_window)
        exit_button.setShortcut('Ctrl+Q')
        exit_button.setStatusTip('Quit application')
        exit_button.triggered.connect(partial(sys.exit, 0))
        actions_menu.addAction(exit_button)

        # view menu - columns list
        for key, val in [*Columns.data_columns.items(), *Columns.widget_columns.items()]:
            submenu_item = QAction(QIcon(), val['display_name'], self.content_window)
            submenu_item.setStatusTip(val['menu_tooltip'])
            submenu_item.triggered.connect(partial(self.content_window.table_container.show_hide_column, key))
            submenu_item.setCheckable(True)
            submenu_item.setChecked(True)
            view_menu.addAction(submenu_item)
        view_menu.addSeparator()

        # view menu - search button.
        search_button = QAction(QIcon.fromTheme('system-search'), 'Search...', self.content_window)
        search_button.setShortcut('Ctrl+F')
        search_button.setStatusTip('Search content')
        search_button.triggered.connect(self.content_window.search_box.set_focus)
        view_menu.addAction(search_button)

        # video menu - flipped lecture quality button.
        flipped_lecture_quality_button = QAction(QIcon(), 'Flipped Lecture Video Quality', self.content_window)
        flipped_lecture_quality_button.setStatusTip('Flipped lecture video quality')
        flipped_lecture_quality_button.setEnabled(False)
        video_menu.addAction(flipped_lecture_quality_button)
        for video_quality in ['highest', *self.conf.get('video_quality_order'), 'lowest']:
            submenu_item = QAction(QIcon(), video_quality, self.content_window)
            submenu_item.triggered.connect(partial(self.set_video_quality, video_quality))
            submenu_item.setCheckable(True)
            if video_quality == self.conf.get('video_quality'):
                submenu_item.setChecked(True)
            else:
                submenu_item.setChecked(False)
            video_menu.addAction(submenu_item)
        video_menu.addSeparator()

        # video menu - download_video button.
        download_video_button = QAction(QIcon(), 'Download Video', self.content_window)
        download_video_button.setShortcut('Ctrl+J')
        download_video_button.setStatusTip('Download Video')
        download_video_button.triggered.connect(self.content_window.table_container.download_video)
        video_menu.addAction(download_video_button)

        # video menu - play video button.
        play_video_button = QAction(QIcon(), 'Play Video', self.content_window)
        play_video_button.setShortcut('Ctrl+P')
        play_video_button.setStatusTip('Play Video')
        play_video_button.triggered.connect(self.content_window.table_container.play_video)
        video_menu.addAction(play_video_button)

        # video menu - download chats button.
        download_chats_button = QAction(QIcon(), 'Download Lecture Chats', self.content_window)
        download_chats_button.setShortcut('Ctrl+Shift+J')
        download_chats_button.setStatusTip('Download Lecture Chats')
        download_chats_button.triggered.connect(self.content_window.table_container.download_chats)
        video_menu.addAction(download_chats_button)

        # slides menu - download_slides button.
        download_slides_button = QAction(QIcon(), 'Download Backpack Slides', self.content_window)
        download_slides_button.setShortcut('Ctrl+K')
        download_slides_button.setStatusTip('Download Backpack Slides')
        # download_slides_button.triggered.connect(self.download_slides)
        slides_menu.addAction(download_slides_button)

        # slides menu - open_folder button.
        open_folder_button = QAction(QIcon(), 'Open Folder', self.content_window)
        open_folder_button.setShortcut('Ctrl+O')
        open_folder_button.setStatusTip('Open Folder')
        open_folder_button.triggered.connect(partial(self.content_window.table_container.open_folder))
        slides_menu.addAction(open_folder_button)

        # slides menu - attach_slides button.
        attach_slides_button = QAction(QIcon(), 'Attach Lecture Slides', self.content_window)
        attach_slides_button.setShortcut('Ctrl+Shift+O')
        attach_slides_button.setStatusTip('Attach Lecture Slides')
        attach_slides_button.triggered.connect(partial(
            self.content_window.table_container.attach_slides
        ))
        slides_menu.addAction(attach_slides_button)

        # help menu - Documentation button.
        helpdoc_button = QAction(QIcon(), 'Help', self.content_window)
        helpdoc_button.setStatusTip('Help doc')
        helpdoc_button.triggered.connect(self.help_doc)
        help_menu.addAction(helpdoc_button)

        # help menu - Documentation button.
        check_updates_button = QAction(QIcon(), 'Check for Updates...', self.content_window)
        check_updates_button.setStatusTip('Release Notes, Check for Updates')
        check_updates_button.triggered.connect(self.check_updates)
        help_menu.addAction(check_updates_button)

        return main_menu

    def set_video_quality(self, quality):
        self.conf['flipped_lecture_quality'] = quality

    def auto_organize(self):
        pass

    def reload_content(self):
        pass

    def help_doc(self):  # noqa
        Utils.open_file(DocFiles.HELPDOC.value)

    def check_updates(self):
        pass

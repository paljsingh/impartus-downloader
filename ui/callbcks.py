import os

from PySide2.QtCore import QObject
from PySide2.QtWidgets import QMainWindow


class Callbacks:

    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(Callbacks, cls)
            cls._instance = orig.__new__(cls)
        return cls._instance

    impartus = None
    login_window = None
    content_window = None

    def setup(self, impartus, login_window, content_window):
        self.impartus = impartus
        self.login_window = login_window
        self.content_window = content_window

    def set_pushbutton_statuses(self):
        if self.impartus.is_authenticated():
            self.login_window.login_form.login_button.setEnabled(False)
        else:
            self.login_window.login_form.login_button.setEnabled(True)

    def get_action(self, menu, action_name):
        for act in menu.actions():
            if act.objectName() == action_name:
                return act

    def set_menu_statuses(self):
        is_authenticated = self.impartus.is_authenticated()

        actions_menu = self.content_window.menuBar().findChild(QObject, 'Actions')
        login_menu = self.get_action(actions_menu, 'Login')
        reload_menu = self.get_action(actions_menu, 'Reload')
        auto_organize_menu = self.get_action(actions_menu, 'Auto Organize')
        if is_authenticated:
            login_menu.setEnabled(False)
        else:
            login_menu.setEnabled(True)

        # if lecture files need update in their name / location, or video /chats / backpack slides need to be
        # downloaded, enable auto organize menu.
        if is_authenticated and (
                self.content_window.needs_lecture_rename() or
                self.content_window.needs_video_download() or
                self.content_window.needs_chat_download() or
                self.content_window.needs_backpack_slides_download()):
            auto_organize_menu.setEnabled(True)
        else:
            auto_organize_menu.setEnabled(False)

        # disable reload menu if any downloads are in progress.
        if len(self.content_window.table_container.threads) > 0:
            reload_menu.setEnabled(False)
        else:
            reload_menu.setEnabled(True)

        table = self.content_window.table_container
        selected_row = table.get_selected_row()
        ttid = table.get_selected_row_ttid(selected_row) if selected_row else None

        # video menu
        video_menu = self.content_window.menuBar().findChild(QObject, 'Video')
        download_video_menu = self.get_action(video_menu, 'Download Video')
        play_video_menu = self.get_action(video_menu, 'Play Video')
        download_chats_menu = self.get_action(video_menu, 'Download Lecture Chats')
        # enable video download menu, when -
        # a row is checked, and the checked row needs a download.
        if is_authenticated and selected_row and not table.data[ttid].get('offline_filepath'):
            download_video_menu.setEnabled(True)
        else:
            download_video_menu.setEnabled(False)

        if selected_row and table.data[ttid].get('offline_filepath') \
                and os.path.exists(table.data[ttid].get('offline_filepath')):
            play_video_menu.setEnabled(True)
        else:
            play_video_menu.setEnabled(False)

        # enable download captions, if captions file does not exist locally.
        if is_authenticated and selected_row and table.data[ttid].get('captions_path') \
                and not os.path.exists(table.data[ttid].get('captions_path')):
            download_chats_menu.setEnabled(True)
        else:
            download_chats_menu.setEnabled(False)

        # slides menu...
        slides_menu = self.content_window.menuBar().findChild(QObject, 'Slides')
        download_slides_menu = self.get_action(slides_menu, 'Download Backpack Slides')
        open_folder_menu = self.get_action(slides_menu, 'Open Folder')
        attach_slides_menu = self.get_action(slides_menu, 'Attach Lecture Slides')

        # download slides button will ve enabled, if the slide exists on server, but not locally.
        if is_authenticated and selected_row and table.data[ttid].get('slide_url') and \
                table.data[ttid].get('slide_path') and not os.path.exists(table.data[ttid].get('slide_path')):
            download_slides_menu.setEnabled(True)
        else:
            download_slides_menu.setEnabled(False)

        filepath = None
        if selected_row:
            for field in ['offline_filepath', 'slide_path', 'captions_path']:
                if table.data[ttid].get(field):
                    filepath = table.data[ttid].get(field)
                    break

        directory = os.path.dirname(filepath) if filepath else None
        if selected_row and table.data[ttid].get('offline_filepath') and os.path.exists(directory):
            open_folder_menu.setEnabled(True)
            attach_slides_menu.setEnabled(True)
        else:
            open_folder_menu.setEnabled(False)
            attach_slides_menu.setEnabled(False)

    def switch_windows(self, from_window: QMainWindow, to_window: QMainWindow):  # noqa
        """
        switch between two windows.
        """
        to_window.show()
        from_window.hide()
        to_window.setFocus()
        return to_window

    def on_login_click(self):
        self.switch_windows(
            from_window=self.content_window,
            to_window=self.login_window
        )
        self.set_menu_statuses()

    def on_reload_click(self):
        pass

    def on_auto_organize_click(self):
        pass

    def on_column_click(self):
        pass

    def on_search_click(self):
        pass

    def on_video_quality_click(self):
        pass

    def on_download_video_click(self):
        pass

    def on_play_video_click(self):
        pass

    def on_download_chats_click(self):
        pass

    def on_download_slides_click(self):
        pass

    def on_open_folder_click(self):
        pass

    def on_attach_slides_click(self):
        pass

    def on_check_for_updates_click(self):

        pass

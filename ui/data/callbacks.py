from datetime import datetime
import os

import requests
from PySide2 import QtCore
from PySide2.QtCore import QObject
from PySide2.QtWidgets import QMainWindow, QLabel, QTreeWidget, QTreeWidgetItem

from lib import version
from lib.utils import Utils
from ui.data.docs import Docs
from lib.variables import Variables
from ui.dialog import Dialog


class Callbacks:
    """
    Class to implement most (if not all) action handlers methods.
    Presently owns almost all the menu item event handler.

    Todo: Move the remaining menu items handlers here for better readability.
    """

    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(Callbacks, cls)
            cls._instance = orig.__new__(cls)
        return cls._instance

    impartus = None
    login_window = None
    content_window = None
    app = None
    last_timestamp = 0.0

    def setup(self, impartus, login_window, content_window, app):
        self.impartus = impartus
        self.login_window = login_window
        self.content_window = content_window
        self.app = app

    def set_pushbutton_statuses(self):
        if self.impartus.is_authenticated():
            self.login_window.login_form.login_button.setEnabled(False)
        else:
            self.login_window.login_form.login_button.setEnabled(True)

    def get_action(self, menu, action_name):    # noqa
        for act in menu.actions():
            if act.objectName() == action_name:
                return act

    def set_menu_statuses(self):
        is_authenticated = self.impartus.is_authenticated()

        actions_menu = self.content_window.menuBar().findChild(QObject, 'Actions')
        login_menu = self.get_action(actions_menu, 'Login')
        reload_menu = self.get_action(actions_menu, 'Reload')
        auto_organize_menu = self.get_action(actions_menu, 'Auto Organize')
        logout_menu = self.get_action(actions_menu, 'Logout')
        if is_authenticated:
            login_menu.setEnabled(False)
        else:
            login_menu.setEnabled(True)

        # disable reload menu if any downloads are in progress, or working offline.
        if not is_authenticated or len(self.content_window.table_container.workers) > 0:
            reload_menu.setEnabled(False)
        else:
            reload_menu.setEnabled(True)

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

        if is_authenticated:
            logout_menu.setEnabled(True)
        else:
            logout_menu.setEnabled(False)

        table = self.content_window.table_container
        rf_id, is_flipped = table.get_selected_row_rfid()

        # video menu
        video_menu = self.content_window.menuBar().findChild(QObject, 'Video')
        download_video_menu = self.get_action(video_menu, 'Download Video')
        play_video_menu = self.get_action(video_menu, 'Play Video')
        download_chats_menu = self.get_action(video_menu, 'Download Lecture Chats')
        # enable video download menu, when -
        # a row is checked, and the checked row needs a download.
        if is_authenticated and rf_id and not table.data[rf_id].get('offline_filepath'):
            download_video_menu.setEnabled(True)
        else:
            download_video_menu.setEnabled(False)

        if rf_id and table.data[rf_id].get('offline_filepath') \
                and os.path.exists(table.data[rf_id].get('offline_filepath')):
            play_video_menu.setEnabled(True)
        else:
            play_video_menu.setEnabled(False)

        # enable download captions, if captions file does not exist locally.
        if is_authenticated and rf_id and table.data[rf_id]:
            captions_path = self.impartus.get_captions_path(table.data[rf_id])
            if captions_path and not os.path.exists(captions_path):
                download_chats_menu.setEnabled(True)
            else:
                download_chats_menu.setEnabled(False)
        else:
            download_chats_menu.setEnabled(False)

        # slides menu...
        slides_menu = self.content_window.menuBar().findChild(QObject, 'Slides')
        download_slides_menu = self.get_action(slides_menu, 'Download Backpack Slides')
        open_folder_menu = self.get_action(slides_menu, 'Open Folder')
        attach_slides_menu = self.get_action(slides_menu, 'Attach Lecture Slides')

        # download slides button will ve enabled, if the slide exists on server, but not locally.
        if is_authenticated and rf_id and table.data[rf_id].get('slide_url') and \
                table.data[rf_id].get('slide_path') and not os.path.exists(table.data[rf_id].get('slide_path')):
            download_slides_menu.setEnabled(True)
        else:
            download_slides_menu.setEnabled(False)

        filepath = None
        if rf_id:
            for field in ['offline_filepath', 'slide_path', 'captions_path']:
                if table.data[rf_id].get(field):
                    filepath = table.data[rf_id].get(field)
                    break

        directory = os.path.dirname(filepath) if filepath else None
        if rf_id and table.data[rf_id].get('offline_filepath') and os.path.exists(directory):
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
        to_window.setVisible(True)
        to_window.setFocus()
        from_window.hide()
        return to_window

    def processEvents(self):
        # process every n seconds at most
        n = 0.5
        if datetime.now().timestamp() - self.last_timestamp >= n:
            self.app.processEvents()
            self.last_timestamp = datetime.now().timestamp()

    def on_menu_login_click(self):
        self.switch_windows(
            from_window=self.content_window,
            to_window=self.login_window
        )
        self.set_menu_statuses()

    def on_menu_reload_click(self):
        self.content_window.work_online()

    def on_menu_auto_organize_click(self):   # noqa
        print('auto organize called...')

    def on_menu_logout_click(self):
        self.impartus.logout()
        self.switch_windows(
            from_window=self.content_window,
            to_window=self.login_window,
        )
        self.set_menu_statuses()
        self.login_window.validate_inputs()

    def on_menu_column_click(self, column_name: str):
        self.content_window.table_container.show_hide_column(column_name)

    def on_menu_search_click(self):
        self.content_window.search_box.set_focus()

    def on_menu_video_quality_click(self, video_quality: str):   # noqa
        Variables().set_flipped_lecture_quality(video_quality)

    def on_menu_download_video_click(self):
        rf_id, is_flipped = self.content_window.table_container.get_selected_row_rfid()
        self.content_window.table_container.on_click_download_video(rf_id, is_flipped)

    def on_menu_play_video_click(self):
        rf_id, is_flipped = self.content_window.table_container.get_selected_row_rfid()
        self.content_window.table_container.on_click_play_video(rf_id)

    def on_menu_download_chats_click(self):
        rf_id, is_flipped = self.content_window.table_container.get_selected_row_rfid()
        self.content_window.table_container.on_click_download_chats(rf_id)

    def on_menu_download_slides_click(self):
        rf_id, is_flipped = self.content_window.table_container.get_selected_row_rfid()
        self.content_window.table_container.on_click_download_slides(rf_id)

    def on_menu_open_folder_click(self):
        rf_id, is_flipped = self.content_window.table_container.get_selected_row_rfid()
        self.content_window.table_container.on_click_open_folder(rf_id)

    def on_menu_attach_slides_click(self):
        rf_id, is_flipped = self.content_window.table_container.get_selected_row_rfid()
        self.content_window.table_container.on_click_attach_slides(rf_id)

    def on_menu_check_for_updates_click(self):
        current_version = version.__version_info__
        releases = self.get_releases()

        dialog = Dialog(file='ui/views/about.ui', parent=self.content_window).dialog

        latest_version = releases[0]['tag_name']
        version_label = dialog.findChild(QLabel, 'version_label')
        new_version_label = dialog.findChild(QLabel, 'new_version_label')
        dl_link1 = dialog.findChild(QLabel, 'dl_link1_label')
        dl_link2 = dialog.findChild(QLabel, 'dl_link2_label')
        version_label.setText(current_version)

        # update version label
        if latest_version > current_version:
            new_version_label.setText('A new version {} is available.'.format(releases[0]['tag_name']))
            dl_link1.setText('<a href="{}">zip download </a>'.format(releases[0]['zipball_url']))
            dl_link2.setText('<a href="{}"> tar download</a>'.format(releases[0]['tarball_url']))
            dl_link1.setOpenExternalLinks(True)
            dl_link2.setOpenExternalLinks(True)
        else:
            new_version_label.hide()
            dl_link1.hide()
            dl_link2.hide()

        # update changelist in the treewidget
        treewidget = dialog.findChild(QTreeWidget, 'release_notes_treeview')
        treewidget.setColumnCount(2)
        treewidget.setHeaderLabels(['', ''])
        treewidget.setAlternatingRowColors(True)
        treewidget.header().setAlternatingRowColors(True)
        for i, rel in enumerate(releases):

            item = QTreeWidgetItem(treewidget)
            item.setText(0, rel['tag_name'])
            item.setTextAlignment(0, QtCore.Qt.AlignmentFlag.AlignTop)
            treewidget.addTopLevelItem(item)

            item1 = QTreeWidgetItem(item)
            item1.setText(0, 'Summary')
            item1.setTextAlignment(0, QtCore.Qt.AlignmentFlag.AlignTop)
            item1.setText(1, rel['name'])
            item.addChild(item1)

            item2 = QTreeWidgetItem(item)
            item2.setText(0, 'Published on')
            item2.setTextAlignment(0, QtCore.Qt.AlignmentFlag.AlignTop)
            item2.setText(1, rel['published_at'])
            item.addChild(item2)

            item3 = QTreeWidgetItem(item)
            item3.setText(0, 'Release Notes')
            item3.setTextAlignment(0, QtCore.Qt.AlignmentFlag.AlignTop)
            item3.setText(1, rel['body'])
            item.addChild(item3)

            # must expand every item for resizeColumnToContents policy to take effect.
            item.setExpanded(True)

        treewidget.resizeColumnToContents(0)
        treewidget.resizeColumnToContents(1)
        treewidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        for i in range(1, len(releases)):
            index = treewidget.model().index(i, 0)
            treewidget.collapse(index)

    def on_menu_help_doc_click(self):      # noqa
        document_path = os.path.join(os.path.abspath(os.curdir), Docs.HELPDOC.value)
        Utils.open_file(document_path)

    def get_releases(self):     # noqa
        url = 'https://api.github.com/repos/paljsingh/impartus-downloader/releases'
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()

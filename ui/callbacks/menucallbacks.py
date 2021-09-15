import os

from PySide2 import QtCore
from PySide2.QtCore import QObject
from PySide2.QtWidgets import QLabel, QTreeWidget, QTreeWidgetItem, QMessageBox

from lib import version
from lib.utils import Utils
from ui.callbacks.utils import CallbackUtils
from lib.data.docs import Docs
from lib.variables import Variables
from ui.dialog import Dialog
from ui.helpers.datautils import DataUtils


class MenuCallbacks:

    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(MenuCallbacks, cls)
            cls._instance = orig.__new__(cls)
        return cls._instance

    @classmethod
    def get_action(cls, menu, action_name):
        for act in menu.actions():
            if act.objectName() == action_name:
                return act

    @classmethod
    def set_menu_statuses(cls):
        is_authenticated = CallbackUtils().impartus.is_authenticated()

        actions_menu = CallbackUtils().content_window.menuBar().findChild(QObject, 'Actions')
        login_menu = cls.get_action(actions_menu, 'Login')
        reload_menu = cls.get_action(actions_menu, 'Reload')
        auto_organize_menu = cls.get_action(actions_menu, 'Auto Organize')
        logout_menu = cls.get_action(actions_menu, 'Logout')
        if is_authenticated:
            login_menu.setEnabled(False)
        else:
            login_menu.setEnabled(True)

        # disable reload menu if working offline.
        if not is_authenticated:
            reload_menu.setEnabled(False)
        else:
            reload_menu.setEnabled(True)

        # if lecture files need update in their name / location, or video /chats / backpack slides need to be
        # downloaded, enable auto organize menu.
        if is_authenticated and (
                CallbackUtils().content_window.needs_lecture_rename() or
                CallbackUtils().content_window.needs_video_download() or
                CallbackUtils().content_window.needs_chat_download() or
                CallbackUtils().content_window.needs_backpack_slides_download()):
            auto_organize_menu.setEnabled(True)
        else:
            auto_organize_menu.setEnabled(False)

        if is_authenticated:
            logout_menu.setEnabled(True)
        else:
            logout_menu.setEnabled(False)

        table = CallbackUtils().content_window.table_container
        rf_id, is_flipped = table.get_selected_row_rfid()

        # video menu
        video_menu = CallbackUtils().content_window.menuBar().findChild(QObject, 'Video')
        download_video_menu = cls.get_action(video_menu, 'Download Video')
        play_video_menu = cls.get_action(video_menu, 'Play Video')
        download_chats_menu = cls.get_action(video_menu, 'Download Lecture Chats')
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
            captions_path = CallbackUtils().impartus.get_captions_path(table.data[rf_id])
            if captions_path and not os.path.exists(captions_path):
                download_chats_menu.setEnabled(True)
            else:
                download_chats_menu.setEnabled(False)
        else:
            download_chats_menu.setEnabled(False)

        # slides menu...
        slides_menu = CallbackUtils().content_window.menuBar().findChild(QObject, 'Slides')
        download_slides_menu = cls.get_action(slides_menu, 'Download Backpack Slides')
        open_folder_menu = cls.get_action(slides_menu, 'Open Folder')
        attach_slides_menu = cls.get_action(slides_menu, 'Attach Lecture Slides')

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

    # Actions menu
    @classmethod
    def on_click__menu__actions_login(cls):
        CallbackUtils().switch_windows(
            from_window=CallbackUtils().content_window,
            to_window=CallbackUtils().login_window
        )
        cls.set_menu_statuses()

    @classmethod
    def on_click__menu__actions_reload(cls):
        reload = True

        # downloads in progress? warn the user.
        if len(CallbackUtils().content_window.table_container.workers) > 0:
            question = "1 or more downloads are in progress.\nYou may lose the progress on refreshing the page.\n" \
                       "Do you want to continue ? "
            dialog = QMessageBox()
            dialog.setIcon(QMessageBox.Icon.Warning)
            reply = dialog.question(CallbackUtils().content_window, "Warning!",
                                    question, QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.No:
                reload = False

        if reload:
            CallbackUtils().content_window.work_online()

    @classmethod
    def on_click__menu__actions_auto_organize(cls):
        print('auto organize called...')

    def on_click__menu__actions_logout(self):
        CallbackUtils().impartus.logout()
        CallbackUtils().switch_windows(
            from_window=CallbackUtils().content_window,
            to_window=CallbackUtils().login_window,
        )
        self.set_menu_statuses()
        CallbackUtils().login_window.validate_inputs()

    # View menu
    @classmethod
    def on_click__menu__view_columns(cls, column_name: str):
        CallbackUtils().content_window.table_container.show_hide_column(column_name)

    @classmethod
    def on_click__menu__view_search(cls):
        CallbackUtils().content_window.search_box.set_focus()

    # Video menu
    @classmethod
    def on_click__menu__video_flipped_video_lecture_quality(cls, video_quality: str):
        Variables().set_flipped_lecture_quality(video_quality)

    @classmethod
    def on_click__menu__video_download_video(cls):
        rf_id, is_flipped = CallbackUtils().content_window.table_container.get_selected_row_rfid()
        CallbackUtils().content_window.table_container.on_click_download_video(rf_id, is_flipped)

    @classmethod
    def on_click__menu__video_play_video(cls):
        rf_id, is_flipped = CallbackUtils().content_window.table_container.get_selected_row_rfid()
        CallbackUtils().content_window.table_container.on_click_play_video(rf_id)

    @classmethod
    def on_click__menu__video_download_lecture_videos(cls):
        rf_id, is_flipped = CallbackUtils().content_window.table_container.get_selected_row_rfid()
        CallbackUtils().content_window.table_container.on_click_download_chats(rf_id)

    # Slides menu
    @classmethod
    def on_click__menu__slides_download_backpack_slides(cls):
        rf_id, is_flipped = CallbackUtils().content_window.table_container.get_selected_row_rfid()
        CallbackUtils().content_window.table_container.on_click_download_slides(rf_id)

    @classmethod
    def on_click__menu__slides_open_folder(cls):
        rf_id, is_flipped = CallbackUtils().content_window.table_container.get_selected_row_rfid()
        CallbackUtils().content_window.table_container.on_click_open_folder(rf_id)

    @classmethod
    def on_click__menu__slides_attach_lecture_slides(cls):
        rf_id, is_flipped = CallbackUtils().content_window.table_container.get_selected_row_rfid()
        CallbackUtils().content_window.table_container.on_click_attach_slides(rf_id)

    # Help Menu
    @classmethod
    def on_click__menu__help_help(cls):
        document_path = os.path.join(os.path.abspath(os.curdir), Docs.HELPDOC.value)
        Utils.open_file(document_path)

    @classmethod
    def on_click__menu__help_check_for_updates(cls):
        current_version = version.__version_info__
        releases = DataUtils.get_releases()

        dialog = Dialog(file='ui/views/about.ui', parent=CallbackUtils().content_window).dialog

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

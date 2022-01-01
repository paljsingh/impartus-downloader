import os
from functools import partial
from typing import List

from PySide2 import QtCore
from PySide2.QtCore import QObject
from PySide2.QtWidgets import QLabel, QTreeWidget, QTreeWidgetItem, QMessageBox, QTableWidget, QTableWidgetItem, \
    QDialogButtonBox

from lib import version
from lib.data.labels import Labels
from lib.utils import Utils
from ui.callbacks.utils import CallbackUtils
from lib.variables import Variables
from ui.dialog import Dialog
from ui.helpers.datautils import DataUtils
from ui.splash import SplashScreen


class MenuCallbacks:

    auto_organize_window = None

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
    def _set_video_menu_statuses(cls):
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

        auto_organize_menu.setEnabled(True)

        if is_authenticated:
            logout_menu.setEnabled(True)
        else:
            logout_menu.setEnabled(False)

        table = CallbackUtils().content_window.videos_tab.table
        video_info = table.selected_checkbox.getValue() if table.selected_checkbox else None
        video_menu = CallbackUtils().content_window.menuBar().findChild(QObject, 'Video')

        if not video_info:
            cls.disable_menu_items(video_menu)
            return

        video_id = video_info.get('video_id')
        if not video_id or not table.video_ids.get(video_id):
            cls.disable_menu_items(video_menu)
            return

        video_metadata = table.video_ids[video_id]['metadata']

        # video menu
        download_video_menu = cls.get_action(video_menu, 'Download Video')
        play_video_menu = cls.get_action(video_menu, 'Play Video')
        download_chats_menu = cls.get_action(video_menu, 'Download Lecture Chats')

        # enable video download menu, when -
        # user logged in to impartus and video is not yet downloaded.
        if is_authenticated and not video_metadata.get('offline_filepath'):
            download_video_menu.setEnabled(True)
        else:
            download_video_menu.setEnabled(False)

        # enable play video menu, when -
        # video is downloaded and video file exists on disk.
        video_path = video_metadata.get('offline_filepath')
        if video_path and os.path.exists(video_path):
            play_video_menu.setEnabled(True)
        else:
            play_video_menu.setEnabled(False)

        # enable download chats menu, when -
        # user logged in to to impartus and and chats file is not yet downloaded.
        captions_path = Utils.get_captions_path(video_metadata)
        if is_authenticated and captions_path and not os.path.exists(captions_path):
            download_chats_menu.setEnabled(True)
        else:
            download_chats_menu.setEnabled(False)

        video_open_folder_menu = cls.get_action(video_menu, 'Open Folder')
        if (video_path and os.path.exists(video_path)) or (captions_path and os.path.exists(captions_path)):
            video_open_folder_menu.setEnabled(True)
        else:
            video_open_folder_menu.setEnabled(False)

    @classmethod
    def _set_slides_menu_statuses(cls):
        is_authenticated = CallbackUtils().impartus.is_authenticated()

        # Slides menu
        tree = CallbackUtils().content_window.documents_tab.tree
        slides_menu = CallbackUtils().content_window.menuBar().findChild(QObject, 'Slides')
        if not tree.selected:
            cls.disable_menu_items(slides_menu)
            return

        document_metadata = tree.selected['metadata']
        download_slides_menu = cls.get_action(slides_menu, 'Download Backpack Document')
        slides_view_document_menu = cls.get_action(slides_menu, 'View Document')
        slides_open_folder_menu = cls.get_action(slides_menu, 'Open Folder')
        attach_slides_menu = cls.get_action(slides_menu, 'Attach Lecture Slides')

        # enable document download menu, when -
        # user logged in to to impartus and document file is not yet downloaded.
        documents_path = document_metadata.get('offline_filepath')
        if is_authenticated and document_metadata.get('fileUrl') and documents_path \
                and not os.path.exists(documents_path):
            download_slides_menu.setEnabled(True)
        else:
            download_slides_menu.setEnabled(False)

        # enable open folder menu, when -
        # a document exists.
        if documents_path and os.path.exists(documents_path):
            slides_view_document_menu.setEnabled(True)
            slides_open_folder_menu.setEnabled(True)
        else:
            slides_view_document_menu.setEnabled(False)
            slides_open_folder_menu.setEnabled(False)

        if os.path.exists(documents_path):
            attach_slides_menu.setEnabled(True)
        else:
            attach_slides_menu.setEnabled(False)

    @classmethod
    def set_menu_statuses(cls):
        cls._set_video_menu_statuses()
        cls._set_slides_menu_statuses()

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
        if len(CallbackUtils().content_window.videos_tab.workers) > 0:
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
        splashscreen = SplashScreen(CallbackUtils().content_window)
        splashscreen.show(widgets_to_disable=[CallbackUtils().content_window.table_widget,
                                              CallbackUtils().content_window.tree_widget])

        splashscreen.setText("Re-collecting videos and documents info, please wait...")
        splashscreen.update()

        commands = CallbackUtils().content_window.videos_tab.table.auto_organize__pre()

        splashscreen.hide(widgets_to_enable=[CallbackUtils().content_window.table_widget,
                          CallbackUtils().content_window.tree_widget])
        if len(commands) > 0:
            dialog = Dialog(file='ui/views/auto_organize.ui', parent=CallbackUtils().content_window).dialog

            button_box: QDialogButtonBox
            button_box = dialog.findChild(QDialogButtonBox, "buttonBox")

            table_widget: QTableWidget
            table_widget = dialog.findChild(QTableWidget, "tableWidget")
            table_widget.setAlternatingRowColors(True)

            num_columns = 3
            table_widget.setColumnCount(num_columns)
            table_widget.setColumnWidth(0, table_widget.width() * 0.46)
            table_widget.setColumnWidth(1, table_widget.width() * 0.08)
            table_widget.setColumnWidth(2, table_widget.width() * 0.46)

            for i, cmd in enumerate(commands):
                table_widget.setRowCount(i+1)
                table_widget.setItem(i, 0, QTableWidgetItem(Utils.strip_root_dir(cmd['source'])))
                table_widget.setItem(i, 1, QTableWidgetItem('-->'))
                table_widget.setItem(i, 2, QTableWidgetItem(Utils.strip_root_dir(cmd['dest'])))
                table_widget.setRowHeight(i, 32)

            button_box.accepted.connect(partial(cls.on_click_auto_organize_ok_button, commands))
        else:
            dialog = QMessageBox()
            dialog.setIcon(QMessageBox.Icon.Information)
            dialog.information(CallbackUtils().content_window, "Auto Organize",
                               "All files and folders are up to date!", QMessageBox.Ok)

    @classmethod
    def on_click_auto_organize_ok_button(cls, commands: List):
        CallbackUtils().content_window.videos_tab.table.auto_organize__post(commands)
        CallbackUtils().content_window.documents_tab.tree.auto_organize__post(commands)

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
        CallbackUtils().content_window.videos_tab.table.show_hide_column(column_name)

    @classmethod
    def on_click__menu__view_search(cls):
        CallbackUtils().content_window.search_box.set_focus()

    # Video menu
    @classmethod
    def on_click__menu__video_flipped_video_lecture_quality(cls, video_quality: str):
        Variables().set_flipped_lecture_quality(video_quality)

    @classmethod
    def on_click__menu__video_download_video(cls):
        video_info = cls.get_selected_video_info()
        if video_info:
            CallbackUtils().content_window.videos_tab.on_click_download_video(video_info['video_id'])

    @classmethod
    def on_click__menu__video_play_video(cls):
        video_info = cls.get_selected_video_info()
        if video_info:
            CallbackUtils().content_window.videos_tab.on_click_play_video(video_info['video_id'])

    @classmethod
    def on_click__menu__video_open_folder(cls):
        video_info = cls.get_selected_video_info()
        if video_info:
            CallbackUtils().content_window.videos_tab.on_click_open_folder(video_info['video_id'])

    @classmethod
    def on_click__menu__video_download_lecture_chats(cls):
        video_info = cls.get_selected_video_info()
        if video_info:
            CallbackUtils().content_window.videos_tab.on_click_download_chats(video_info['video_id'])

    # Slides menu
    @classmethod
    def on_click__menu__slides_download_backpack_slides(cls):
        doc_info = cls.get_selected_document()
        if doc_info:
            CallbackUtils().content_window.documents_tab.on_click_download_document(
                doc_info['subject'], doc_info['metadata'], doc_info['widget'])

    @classmethod
    def on_click__menu__slides_open_folder(cls):
        doc_info = cls.get_selected_document()
        if doc_info:
            CallbackUtils().content_window.documents_tab.on_click_open_folder(
                os.path.dirname(doc_info['metadata']['offline_filepath']))

    @classmethod
    def on_click__menu__slides_view_document(cls):
        doc_info = cls.get_selected_document()
        if doc_info:
            CallbackUtils().content_window.documents_tab.on_click_view_document(
                doc_info['metadata']['offline_filepath'])

    @classmethod
    def on_click__menu__slides_attach_lecture_slides(cls):
        doc_info = cls.get_selected_document()
        if doc_info:
            CallbackUtils().content_window.documents_tab.on_click_attach_document(
                os.path.dirname(doc_info['metadata']['offline_filepath']))

    # Help Menu
    @classmethod
    def on_click__menu__help_help(cls):
        document_path = os.path.join(os.path.abspath(os.curdir), Labels.HELPDOC.value)
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

    @classmethod
    def disable_menu_items(cls, parent_menu_item):
        for child_menu_item in parent_menu_item.actions():
            child_menu_item.setEnabled(False)

    @classmethod
    def enable_menu_items(cls, parent_menu_item):
        for child_menu_item in parent_menu_item.actions():
            child_menu_item.setEnabled(True)

    @classmethod
    def get_selected_video_metadata(cls):
        video_info = cls.get_selected_video_info()
        if video_info:
            video_id = video_info['video_id']
            return CallbackUtils().content_window.videos_tab.table.video_ids.get(video_id)['metadata']

    @classmethod
    def get_selected_video_info(cls):
        selected_checkbox = CallbackUtils().content_window.videos_tab.table.selected_checkbox
        if selected_checkbox:
            return selected_checkbox.getValue()

    @classmethod
    def get_selected_document(cls):
        return CallbackUtils().content_window.documents_tab.tree.selected

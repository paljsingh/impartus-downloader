import os

from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QAction, QMainWindow

from lib.config import ConfigType, Config
from lib.impartus import Impartus
from lib.utils import Utils
from ui.data.docs import Docs
from ui.data.menuitems import MenuItems


class Menubar:
    """
    Responsible for creating menu entries. It picks up the menu items data specified in ui/data/menuitems.py
    TODO: Move the remaining handler functions to callbacks.py
    """

    def __init__(self, login_window: QMainWindow, content_window: QMainWindow):
        self.login_window = login_window
        self.content_window = content_window
        self.impartus = Impartus()
        self.conf = Config.load(ConfigType.IMPARTUS)
        pass

    def add_menu(self):
        main_menu = self.content_window.menuBar()

        # for Actions: {}, View: {}, Video: {} ... in
        for name, value in MenuItems.menu_items.items():
            level_1 = main_menu.addMenu(name)       # level_1: Actions_menu, View_menu ...
            level_1.setObjectName(name)

            # for Login: {}, Reload: {} ... in
            for child_name, properties in value.items():
                if properties.get('type') == 'separator':
                    level_1.addSeparator()
                elif properties.get('type') == 'list':
                    submenu_item = QAction(QIcon(), child_name, self.content_window)
                    submenu_item.setCheckable(False)
                    submenu_item.setObjectName(child_name)  # submenu_item: Col1_menu, Col2_menu ...
                    submenu_item.setEnabled(False)
                    level_1.addAction(submenu_item)
                    for level2_child_name in properties['child_items']:     # level_2: View:Col1, View:Col2, Video: ...
                        submenu_item = QAction(QIcon(), level2_child_name, self.content_window)
                        submenu_item.setCheckable(True)
                        submenu_item.setObjectName(level2_child_name)       # submenu_item: Col1_menu, Col2_menu ...
                        submenu_item.setEnabled(True)
                        if properties.get('behavior') == 'checkall':
                            submenu_item.setChecked(True)
                        elif properties.get('behavior') == 'checkone':
                            submenu_item.setChecked(True) if level2_child_name == properties.get('default') \
                                else submenu_item.setChecked(False)
                        else:
                            pass
                        level_1.addAction(submenu_item)
                else:
                    level_2 = QAction(QIcon(), child_name, self.content_window)
                    level_2.setShortcut(properties['shortcut'])
                    level_2.setStatusTip(properties['status_tip'])
                    level_2.setObjectName(child_name)
                    level_2.triggered.connect(properties['callback'])
                    level_1.addAction(level_2)

        return main_menu

    def set_video_quality(self, quality):
        self.conf['flipped_lecture_quality'] = quality

    def auto_organize(self):
        pass

    def reload_content(self):
        pass

    def help_doc(self):  # noqa
        document_path = os.path.join(os.path.abspath(os.curdir), Docs.HELPDOC.value)
        Utils.open_file(document_path)

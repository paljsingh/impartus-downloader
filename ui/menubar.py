from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QAction, QMainWindow, QActionGroup

from lib.config import ConfigType, Config
from lib.core.impartus import Impartus
from lib.data.columns import Columns
from lib.data.menuitems import MenuItems
import qtawesome as qta


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

            # for Login: {}, Reload: {}, flipped lecture quality: {}, columns: {} ... in
            for child_name, properties in value.items():
                if properties.get('type') == 'separator':
                    level_1.addSeparator()
                elif properties.get('type') == 'list':
                    # list root    [flipped lecture video, Columns ... ]
                    icon = qta.icon(properties['icon']) if properties.get('icon') else QIcon()
                    submenu_item = QAction(icon, child_name, self.content_window)
                    submenu_item.setCheckable(False)
                    submenu_item.setObjectName(child_name)
                    submenu_item.setEnabled(False)
                    level_1.addAction(submenu_item)

                    action_group = QActionGroup(level_1)
                    if properties.get('behavior') == 'multiselect':
                        action_group.setExclusive(False)
                    else:
                        action_group.setExclusive(True)

                    # level_2: View:Col1,  View:Col2, Video: ...
                    for i, ((level2_child_key, level2_child_display_name), callback) in enumerate(
                            zip(properties['child_items'].items(), properties['child_callbacks'])):
                        submenu_item = QAction(QIcon(), level2_child_display_name, self.content_window)
                        submenu_item.setCheckable(True)
                        submenu_item.setObjectName(level2_child_display_name)   # submenu_item: Col1_menu, Col2_menu ...
                        submenu_item.setEnabled(True)
                        action_group.addAction(submenu_item)

                        if properties.get('behavior') == 'multiselect':
                            submenu_item.setChecked(True)
                        elif properties.get('behavior') == 'singleselect':
                            submenu_item.setChecked(True) if level2_child_display_name == properties.get('default') \
                                else submenu_item.setChecked(False)
                        else:
                            pass

                        # however, if the column is default hidden, set the menu item to unchecked.
                        if Columns.get_video_columns().get(level2_child_key) \
                                and Columns.get_video_columns().get(level2_child_key).get('hidden'):
                            submenu_item.setChecked(False)

                        submenu_item.triggered.connect(callback)    # noqa

                        level_1.addAction(submenu_item)

                else:
                    icon = qta.icon(properties['icon']) if properties.get('icon') else QIcon()
                    level_2 = QAction(icon, child_name, self.content_window)
                    level_2.setShortcut(properties['shortcut'])
                    level_2.setStatusTip(properties['status_tip'])
                    level_2.setObjectName(child_name)
                    level_2.triggered.connect(properties['callback'])   # noqa
                    level_1.addAction(level_2)

        return main_menu

    def set_video_quality(self, quality):
        self.conf['flipped_lecture_quality'] = quality

    def reload_content(self):
        pass

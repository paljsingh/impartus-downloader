import os

from PySide2.QtWidgets import QComboBox
from typing import List
import qtawesome as qta

from lib.utils import Utils
from ui.data.Icons import Icons
from ui.data.slideicons import SlideIcons


class CustomComboBox(QComboBox):

    def __init__(self):
        super().__init__()

        self.setMinimumWidth(100)
        self.setMaximumWidth(100)

        # retain size when hidden
        retain_size_policy = self.sizePolicy()
        retain_size_policy.setRetainSizeWhenHidden(True)
        self.setSizePolicy(retain_size_policy)

        self.connection = None

    def add_items(self, items: List):
        if not len(items):
            return

        prev_item_count = self.count()
        if prev_item_count > 0:
            # update item 0
            self.setItemText(0, '{}'.format(prev_item_count - 1 + len(items)))
        else:
            # add item : 0
            self.addItem(qta.icon(Icons.SLIDES__SHOW_SLIDES.value), '{}'.format(len(items)), '')
            self.model().item(0).setEnabled(False)

        self.show()

        for item in items:
            icon_name = SlideIcons.get_icon_type(item)
            self.addItem(qta.icon(icon_name), os.path.basename(item), item)
            # self.insertItem(i, qta.icon(icon_name), os.path.basename(item), item)

        print('item earlier {},  now {}'.format(prev_item_count, self.count()))

        if self.connection:
            self.activated.disconnect()
        self.activated.connect(self.show_slides)
        self.connection = True

    def show_slides(self, index: int):    # noqa
        Utils.open_file(self.itemData(index))

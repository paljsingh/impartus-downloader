import os

from PySide2.QtCore import QEvent
from PySide2.QtGui import QPalette
from PySide2.QtWidgets import QComboBox, QApplication
from typing import List
import qtawesome as qta

from lib.utils import Utils
from lib.data.Icons import Icons, DocumentIcons


class CustomComboBox(QComboBox):

    def __init__(self):
        super().__init__()

        self.setMinimumWidth(100)
        self.setMaximumWidth(100)

        # retain size when hidden => do not shrink 'slides' tab when no slides dropdown present.
        retain_size_policy = self.sizePolicy()
        retain_size_policy.setRetainSizeWhenHidden(True)
        self.setSizePolicy(retain_size_policy)

        self.connection = None

    def add_items(self, items: List):
        """
        Add one or more items to the combo box.
        Items in the input list are expected to be file paths.
        """
        if not len(items):
            return

        prev_item_count = self.count()
        if prev_item_count > 0:
            # update item 0
            self.setItemText(0, '{}'.format(prev_item_count - 1 + len(items)))
        else:
            # add item : 0
            self.addItem(qta.icon(Icons.DOCUMENT__SHOW_SLIDES.value), '{}'.format(len(items)), '')
            self.model().item(0).setEnabled(False)

        self.show()

        for item in items:
            icon_name = DocumentIcons.get_icon_type(item)
            self.addItem(qta.icon(icon_name), os.path.basename(item), item)

        if self.connection:
            self.activated.disconnect()
        self.activated.connect(self.show_slides)
        self.connection = True

        self.apply_current_palette()

    def show_slides(self, index: int):    # noqa
        """
        Open the select lecture slides doc.
        """
        Utils.open_file(self.itemData(index))

    def changeEvent(self, event: QEvent) -> None:
        """
        On system theme change, update the progress bar colors.
        """
        super().changeEvent(event)
        if event.type() == QEvent.PaletteChange:
            self.apply_current_palette()

    def apply_current_palette(self):
        highlight_color = QApplication.palette().color(QPalette.Highlight)
        text_color = QApplication.palette().color(QPalette.Text)

        for i in range(self.count()):
            qicon = qta.icon(
                DocumentIcons.get_icon_type(self.itemData(i)),
                color=text_color,
                color_active=highlight_color,
            )
            super().setItemIcon(i, qicon)

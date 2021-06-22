import os
from functools import partial
from typing import List

from PySide2.QtWidgets import QComboBox, QLabel, QWidget

from lib.utils import Utils
from qtui.common import Common
from ui.data import Icons, ActionItems, ConfigKeys, Columns


class Slides:

    @classmethod
    def add_slides_actions_buttons(cls, metadata):
        widget = QWidget()
        widget_layout = Common.get_layout_widget(widget)
        widget_layout.setAlignment(Columns.widget_columns.get('slides_actions')['alignment'])

        # show slides combo box.
        combo_box = Slides.add_slides_combobox(metadata)
        if combo_box:
            widget_layout.addWidget(combo_box)
        else:
            widget_layout.addWidget(QLabel())

        for pushbutton in Common.add_actions_buttons(ActionItems.slides_actions):
            widget_layout.addWidget(pushbutton)

            # open folder should be enabled, if folder exist
            if pushbutton.text() == ActionItems.slides_actions['open_folder']['text']:
                folder = None
                if metadata.get('offline_filepath'):
                    folder = os.path.dirname(metadata['offline_filepath'])
                elif metadata['backpack_slides']:
                    folder = os.path.dirname(metadata['backpack_slides'][0])

                if folder and os.path.exists(folder):
                    pushbutton.setEnabled(True)
                    pushbutton.clicked.connect(partial(Utils.open_file, folder))
                else:
                    pushbutton.setEnabled(False)

            # slides download is enabled if the slides file exists on server, but not locally.
            if pushbutton.text() == ActionItems.slides_actions['download_slides']['text']:
                filepath = metadata.get(ConfigKeys.SLIDES_PATH.value)
                if metadata.get('slideCount') and filepath and not os.path.exists(filepath):
                    pushbutton.setEnabled(True)
                else:
                    pushbutton.setEnabled(False)

            # attach slides is enabled always (creates a folder if one does not exist).
            if pushbutton.text() == ActionItems.slides_actions['attach_slides']['text']:
                pushbutton.setEnabled(True)
        return widget

    @classmethod
    def add_slides_combobox(cls, item):
        if item.get('backpack_slides'):
            combo_box = QComboBox()
            combo_box.addItem('{:4s} {:2d}'.format(Icons.SHOW_SLIDES, len(item['backpack_slides'])))
            for slide in item['backpack_slides']:
                combo_box.addItem(os.path.basename(slide))
            combo_box.activated.connect(
                partial(Slides.show_slides, item['backpack_slides'])
            )
            combo_box.model().item(0).setEnabled(False)
            combo_box.setMaximumWidth(100)
            return combo_box
        else:
            return

    @classmethod
    def show_slides(cls, slides: List, index: int):
        Utils.open_file(slides[index - 1])



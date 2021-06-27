import os
from functools import partial
from typing import Dict, List

from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QComboBox, QWidget

from lib.impartus import Impartus
from lib.utils import Utils
from ui.common import Common
from ui.data.Icons import Icons
from ui.data.actionitems import ActionItems
from ui.data.columns import Columns


class Slides:

    @classmethod
    def add_slides_actions_buttons(cls, metadata, impartus: Impartus, callbacks: Dict):
        widget = QWidget()
        widget_layout = Common.get_layout_widget(widget)
        widget_layout.setAlignment(Columns.widget_columns.get('slides_actions')['alignment'])

        # show slides combo box.
        combo_box = Slides.add_slides_combobox(metadata)
        widget_layout.addWidget(combo_box)
        if metadata.get('backpack_slides'):
            combo_box.show()
        else:
            combo_box.hide()

        for pushbutton in Common.add_actions_buttons(ActionItems.slides_actions):
            widget_layout.addWidget(pushbutton)

            # slides download is enabled if the slides file exists on server, but not locally.
            if pushbutton.text() == ActionItems.slides_actions['download_slides']['text']:
                pushbutton.clicked.connect(callbacks['download_slides'])

                filepath = impartus.get_slides_path(metadata)
                if metadata.get('slide_url') and metadata.get('slide_url') != '' \
                        and filepath and not os.path.exists(filepath):
                    pushbutton.setEnabled(True)
                else:
                    pushbutton.setEnabled(False)
            # open folder should be enabled, if folder exist
            elif pushbutton.text() == ActionItems.slides_actions['open_folder']['text']:
                pushbutton.clicked.connect(callbacks['open_folder'])

                folder = None
                if metadata.get('offline_filepath'):
                    folder = os.path.dirname(metadata['offline_filepath'])
                elif metadata.get('backpack_slides'):
                    folder = os.path.dirname(metadata['backpack_slides'][0])

                if folder and os.path.exists(folder):
                    pushbutton.setEnabled(True)
                    pushbutton.clicked.connect(partial(Utils.open_file, folder))
                else:
                    pushbutton.setEnabled(False)

            # attach slides is enabled always (creates a folder if one does not exist).
            elif pushbutton.text() == ActionItems.slides_actions['attach_slides']['text']:
                pushbutton.clicked.connect(callbacks['attach_slides'])
                pushbutton.setEnabled(True)

        return widget

    @classmethod
    def add_slides_combobox(cls, item):
        combo_box = QComboBox()
        combo_box.setMinimumWidth(100)
        combo_box.setMaximumWidth(100)
        # combo_box.setItemDelegate()

        # retain size when hidden
        retain_size_policy = combo_box.sizePolicy()
        retain_size_policy.setRetainSizeWhenHidden(True)
        combo_box.setSizePolicy(retain_size_policy)
        if item.get('backpack_slides'):
            combo_box.addItem('{:4s} {:2d}'.format(Icons.SHOW_SLIDES, len(item['backpack_slides'])))
            for slide in item['backpack_slides']:
                combo_box.addItem(QIcon(), os.path.basename(slide), slide)
            combo_box.activated.connect(
                partial(Slides.show_slides, item['backpack_slides'])
            )
            combo_box.model().item(0).setEnabled(False)

        return combo_box

    @classmethod
    def add_combobox_items(cls, combo_box: QComboBox, items_text: List, items_data: List):
        combo_box.addItem('{:4s} {:2d}'.format(Icons.SHOW_SLIDES, len(items_text)))
        for text, data in zip(items_text, items_data):
            combo_box.addItem(QIcon(), text, data)
        combo_box.activated.connect(partial(Slides.show_slides, items_data))
        combo_box.model().item(0).setEnabled(False)
        combo_box.show()

    @classmethod
    def show_slides(cls, slides: List, index: int, *vargs, **kvargs):
        print(index, *vargs, **kvargs)
        Utils.open_file(slides[index - 1])

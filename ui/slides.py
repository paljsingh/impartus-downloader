import os
from functools import partial
from typing import Dict, List

import qtawesome as qta
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QComboBox, QWidget

from lib.impartus import Impartus
from lib.utils import Utils
from ui.common import Common
from ui.data.Icons import Icons
from ui.data.actionitems import ActionItems
from ui.data.columns import Columns
from ui.data.slideicons import SlideIcons


class Slides:
    """
    Responsible for creating widgets [slides_combobox, download_slides, open_folder, attach_slides] grouped under the
    'Slides' header.
    """

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
            if pushbutton.objectName() == ActionItems.slides_actions['download_slides']['text']:
                pushbutton.clicked.connect(callbacks['download_slides'])

                if impartus.is_authenticated():
                    filepath = impartus.get_slides_path(metadata)
                    if metadata.get('slide_url') and metadata.get('slide_url') != '' \
                            and filepath and not os.path.exists(filepath):
                        pushbutton.setEnabled(True)
                    else:
                        pushbutton.setEnabled(False)
                else:
                    pushbutton.setEnabled(False)

            # open folder should be enabled, if folder exist
            elif pushbutton.objectName() == ActionItems.slides_actions['open_folder']['text']:
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

            elif pushbutton.objectName() == ActionItems.slides_actions['attach_slides']['text']:

                # attach slides is enabled, if at least one of the files exist.
                video_path = metadata.get('offline_filepath')
                slides_path = metadata.get('slides_path')
                captions_path = metadata.get('captions_path')
                if (video_path and os.path.exists(video_path)) or \
                        (slides_path and os.path.exists(slides_path)) or \
                        (captions_path and os.path.exists(captions_path)):
                    pushbutton.setEnabled(True)
                    pushbutton.clicked.connect(callbacks['attach_slides'])
                else:
                    pushbutton.setEnabled(False)

        return widget

    @classmethod
    def add_slides_combobox(cls, item):
        combo_box = QComboBox()
        combo_box.setMinimumWidth(100)
        combo_box.setMaximumWidth(100)

        # retain size when hidden
        retain_size_policy = combo_box.sizePolicy()
        retain_size_policy.setRetainSizeWhenHidden(True)
        combo_box.setSizePolicy(retain_size_policy)
        if item.get('backpack_slides'):
            combo_box.addItem('{:2d}'.format(len(item['backpack_slides'])))
            combo_box.setItemIcon(0, qta.icon(Icons.SLIDES__SHOW_SLIDES.value))

            for slide in item['backpack_slides']:
                combo_box.addItem(
                    qta.icon(cls.get_icon_type(slide)),
                    os.path.basename(slide),
                    slide
                )
            combo_box.activated.connect(
                partial(Slides.show_slides, item['backpack_slides'])
            )
            combo_box.model().item(0).setEnabled(False)

        return combo_box

    @classmethod
    def add_combobox_items(cls, combo_box: QComboBox, items_text: List, items_data: List):
        combo_box.addItem('{:4s} {:2d}'.format(Icons.SLIDES__SHOW_SLIDES, len(items_text)))
        for text, data in zip(items_text, items_data):
            combo_box.addItem(QIcon(), text, data)
        combo_box.activated.connect(partial(Slides.show_slides, items_data))
        combo_box.model().item(0).setEnabled(False)
        combo_box.show()

    @classmethod
    def show_slides(cls, slides: List, index: int):
        Utils.open_file(slides[index - 1])

    @classmethod
    def get_icon_type(cls, slide_path: str):
        ext = slide_path.split('.')[-1]
        if SlideIcons.filetypes.get(ext):
            return SlideIcons.filetypes[ext]
        else:
            return Icons.SLIDES__FILETYPE_MISC.value

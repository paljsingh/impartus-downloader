import os
from functools import partial
from typing import Dict

from PySide2.QtWidgets import QWidget

from lib.impartus import Impartus
from lib.utils import Utils
from ui.combobox import CustomComboBox
from ui.common import Common
from ui.data.actionitems import ActionItems
from ui.data.columns import Columns


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
        combo_box = CustomComboBox()
        if metadata.get('backpack_slides'):
            combo_box.show()
            combo_box.add_items(metadata['backpack_slides'])
        else:
            combo_box.hide()
        widget_layout.addWidget(combo_box)

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

import os
from functools import partial
from typing import Dict

from PySide2.QtWidgets import QWidget

from lib.impartus import Impartus
from lib.utils import Utils
from ui.customwidgets.combobox import CustomComboBox
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

        # make the widget searchable based on button states.
        combobox_count = None
        download_slides_state = None
        open_folder_state = None
        attach_slides_state = None

        # show slides combo box.
        combo_box = CustomComboBox()
        if metadata.get('backpack_slides'):
            combo_box.show()
            combo_box.add_items(metadata['backpack_slides'])
            combobox_count = combo_box.count() - 1
        else:
            combo_box.hide()
            combobox_count = 0
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
                        download_slides_state = True
                    else:
                        download_slides_state = False
                else:
                    download_slides_state = False

                pushbutton.setEnabled(download_slides_state)

            # open folder should be enabled, if folder exist
            elif pushbutton.objectName() == ActionItems.slides_actions['open_folder']['text']:
                pushbutton.clicked.connect(callbacks['open_folder'])

                folder = None
                if metadata.get('offline_filepath'):
                    folder = os.path.dirname(metadata['offline_filepath'])
                elif metadata.get('backpack_slides'):
                    folder = os.path.dirname(metadata['backpack_slides'][0])

                if folder and os.path.exists(folder):
                    open_folder_state = True
                    pushbutton.clicked.connect(partial(Utils.open_file, folder))
                else:
                    open_folder_state = False

                pushbutton.setEnabled(open_folder_state)

            elif pushbutton.objectName() == ActionItems.slides_actions['attach_slides']['text']:

                # attach slides is enabled, if at least one of the files exist.
                video_path = metadata.get('offline_filepath')
                slides_path = metadata.get('slides_path')
                captions_path = metadata.get('captions_path')
                if (video_path and os.path.exists(video_path)) or \
                        (slides_path and os.path.exists(slides_path)) or \
                        (captions_path and os.path.exists(captions_path)):
                    attach_slides_state = True
                    pushbutton.clicked.connect(callbacks['attach_slides'])
                else:
                    attach_slides_state = False

                pushbutton.setEnabled(attach_slides_state)

        # a slightly hackish way to sort widgets -
        # create an integer out of the (slide count, button1_state, button2_state, ...)
        # pass it to a Custom TableWidgetItem with __lt__ overridden to provide numeric sort.
        cell_value = '{}{}{}{}'.format(
            combobox_count, int(download_slides_state), int(open_folder_state), int(attach_slides_state))

        return widget, int(cell_value)

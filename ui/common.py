from functools import partial
from typing import Dict, Callable

from PySide2 import QtCore
from PySide2.QtWidgets import QHBoxLayout, QWidget, QPushButton, QCheckBox

from ui.customwidgets.pushbutton import CustomPushButton


class Common:
    """
    Common utility methods around ui/widget creation.
    """

    @classmethod
    def get_layout_widget(cls, widget: QWidget):
        widget_layout = QHBoxLayout(widget)
        widget_layout.setSpacing(0)
        widget_layout.setMargin(0)
        widget_layout.setContentsMargins(0, 0, 0, 0)
        return widget_layout

    @classmethod
    def add_actions_buttons(cls, actions: Dict):
        for key, val in actions.items():
            if val['type'] == QPushButton:
                pushbutton = CustomPushButton()
                pushbutton.setText('')
                pushbutton.setObjectName(val['text'])
                pushbutton.setToolTip(val['tooltip'])
                pushbutton.setMaximumWidth(48)
                pushbutton.setIcon(val['text'])

                yield pushbutton

    @classmethod
    def add_checkbox_widget(cls, callback: Callable):
        container_widget = QWidget()
        checkbox = QCheckBox()
        checkbox.clicked.connect(partial(callback, checkbox))       # noqa
        container_widget_layout = QHBoxLayout(container_widget)
        container_widget_layout.addWidget(checkbox)
        container_widget_layout.setAlignment(QtCore.Qt.AlignCenter)
        container_widget_layout.setContentsMargins(0, 0, 0, 0)
        container_widget.setLayout(container_widget_layout)
        return container_widget


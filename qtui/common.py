from typing import Dict, Callable

from PySide2 import QtCore
from PySide2.QtWidgets import QHBoxLayout, QWidget, QPushButton, QCheckBox


class Common:

    @classmethod
    def get_layout_widget(cls, widget: QWidget):
        widget_layout = QHBoxLayout(widget)
        widget_layout.setSpacing(0)
        widget_layout.setMargin(0)
        return widget_layout

    @classmethod
    def add_actions_buttons(cls, actions: Dict):
        for key, val in actions.items():
            pushbutton = QPushButton()
            pushbutton.setText(val['text'])
            pushbutton.setToolTip(val['tooltip'])
            pushbutton.setMaximumWidth(40)
            yield pushbutton

    @classmethod
    def add_checkbox_widget(cls, callback: Callable):
        container_widget = QWidget()
        checkbox = QCheckBox()
        checkbox.clicked.connect(callback)
        container_widget_layout = QHBoxLayout(container_widget)
        container_widget_layout.addWidget(checkbox)
        container_widget_layout.setAlignment(QtCore.Qt.AlignCenter)
        container_widget_layout.setContentsMargins(0, 0, 0, 0)
        container_widget.setLayout(container_widget_layout)
        return container_widget


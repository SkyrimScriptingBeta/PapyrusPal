from dataclasses import field

from PySide6.QtWidgets import QLabel, QMainWindow, QWidget

from qt_helpers.widget import widget
from qt_helpers.window import window


@widget()
class SomeWidget(QWidget):
    some_text: QLabel = QLabel("I am the central widget")


@window()
class AppMainWindow(QMainWindow):
    central_widget: SomeWidget = field(default_factory=SomeWidget)

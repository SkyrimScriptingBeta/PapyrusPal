"""Line number area widget for the source code editor."""

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget


class LineNumberArea(QWidget):
    """Widget for displaying line numbers."""

    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)

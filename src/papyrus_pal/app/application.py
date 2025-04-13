from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication


class Application(QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setApplicationName("Papyrus Pal")
        self.setApplicationDisplayName("Papyrus Pal")
        self.setStyle("Fusion")

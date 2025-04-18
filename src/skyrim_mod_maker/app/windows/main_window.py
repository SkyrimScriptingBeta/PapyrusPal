from PySide6.QtWidgets import QWidget


class MainWindow(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Skyrim Mod Maker")

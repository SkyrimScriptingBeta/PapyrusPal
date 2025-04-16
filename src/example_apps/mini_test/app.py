from PySide6.QtWidgets import *
from PySide6.QtCore import QTimer, Qt
import sys


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Top Tabs with Docking")
        self.resize(800, 600)

        # Dock widgets
        dock1 = QDockWidget("Tab One", self)
        dock1.setWidget(QTextEdit("Hello from Tab One"))
        dock1.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.addDockWidget(Qt.RightDockWidgetArea, dock1)

        dock2 = QDockWidget("Tab Two", self)
        dock2.setWidget(QTextEdit("Hello from Tab Two"))
        dock2.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.addDockWidget(Qt.RightDockWidgetArea, dock2)

        # Tabify
        self.tabifyDockWidget(dock1, dock2)
        dock1.raise_()

        # Schedule fix for tab bar position
        QTimer.singleShot(0, self._move_tab_bar_to_top)

    def _move_tab_bar_to_top(self) -> None:
        for bar in self.findChildren(QTabBar):
            tab_parent = bar.parentWidget()
            if isinstance(tab_parent, QWidget):
                layout = tab_parent.layout()
                if layout is not None:
                    layout.removeWidget(bar)
                    layout.insertWidget(0, bar)  # Move to top
                    bar.setDocumentMode(True)  # Optional: makes it look slick
                    bar.setElideMode(Qt.ElideRight)
                    bar.setMovable(True)


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

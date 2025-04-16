import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QDockWidget,
    QTextEdit,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QToolBar,
)
from PySide6.QtGui import QAction, QFont
from PySide6.QtCore import Qt


class EditorWidget(QWidget):
    def __init__(self, filename: str) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"<b>{filename}</b>"))
        layout.addWidget(QTextEdit(f"// Editing {filename}"))
        self.setLayout(layout)


class PanelWidget(QWidget):
    def __init__(self, title: str) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"<h3>{title}</h3>"))
        layout.addWidget(QPushButton(f"{title} Button"))
        layout.addStretch()
        self.setLayout(layout)


class IDEMainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Qt Docking — No Lies Edition")
        self.resize(1200, 800)
        self.setDockNestingEnabled(True)

        # Panels
        self.left_panel: QDockWidget = self._make_panel("Left Panel")
        self.right_panel: QDockWidget = self._make_panel("Right Panel")
        self.top_panel: QDockWidget = self._make_panel("Top Panel")
        self.bottom_panel: QDockWidget = self._make_panel("Bottom Panel")

        self.addDockWidget(Qt.TopDockWidgetArea, self.top_panel)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.bottom_panel)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.left_panel)

        self.editor_docks: list[QDockWidget] = []
        first_editor = self._make_editor("main.cpp")
        self.addDockWidget(Qt.RightDockWidgetArea, first_editor)
        self.editor_docks.append(first_editor)

        # ✅ Fix right panel so it shows beside editors, not stacked
        self.addDockWidget(Qt.RightDockWidgetArea, self.right_panel)
        self.splitDockWidget(first_editor, self.right_panel, Qt.Horizontal)

        for filename in ["engine.cpp", "ui.cpp"]:
            dock = self._make_editor(filename)
            self.addDockWidget(Qt.RightDockWidgetArea, dock)
            self.tabifyDockWidget(first_editor, dock)
            self.editor_docks.append(dock)

        first_editor.raise_()
        self._setup_toolbar()

    def _setup_toolbar(self) -> None:
        toolbar = QToolBar("Toggles", self)
        self.addToolBar(toolbar)

        for label, dock in [
            ("Top Panel", self.top_panel),
            ("Bottom Panel", self.bottom_panel),
            ("Left Panel", self.left_panel),
            ("Right Panel", self.right_panel),
        ]:
            action = QAction(label, self, checkable=True)
            action.setChecked(True)
            action.toggled.connect(lambda checked, d=dock: d.setVisible(checked))
            toolbar.addAction(action)

    def _make_panel(self, title: str) -> QDockWidget:
        dock = QDockWidget(title, self)
        dock.setWidget(PanelWidget(title))
        dock.setAllowedAreas(Qt.AllDockWidgetAreas)
        dock.setFeatures(
            QDockWidget.DockWidgetClosable
            | QDockWidget.DockWidgetMovable
            | QDockWidget.DockWidgetFloatable
        )
        return dock

    def _make_editor(self, filename: str) -> QDockWidget:
        dock = QDockWidget(filename, self)
        dock.setWidget(EditorWidget(filename))
        dock.setAllowedAreas(Qt.AllDockWidgetAreas)
        dock.setFeatures(
            QDockWidget.DockWidgetClosable
            | QDockWidget.DockWidgetMovable
            | QDockWidget.DockWidgetFloatable
        )
        return dock


def main() -> None:
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 9))
    window = IDEMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

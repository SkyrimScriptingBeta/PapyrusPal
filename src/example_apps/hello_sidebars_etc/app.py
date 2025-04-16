import sys
from typing import Optional
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
        self.setWindowTitle("Qt IDE Docking (Really Working)")
        self.resize(1200, 800)
        self.setDockNestingEnabled(True)

        self.left_panel: Optional[QDockWidget] = None
        self.right_panel: Optional[QDockWidget] = None
        self.top_panel: Optional[QDockWidget] = None
        self.bottom_panel: Optional[QDockWidget] = None
        self.editor_anchor: Optional[QDockWidget] = None
        self.editor_docks: list[QDockWidget] = []

        self._setup_fixed_layout()
        self._setup_toolbar()

    def _setup_fixed_layout(self) -> None:
        # Step 1: Start with a dummy dock on the far left
        self.left_panel = self._make_panel("Left Panel")
        self.addDockWidget(Qt.LeftDockWidgetArea, self.left_panel)

        # Step 2: Add main editor dock to the right of left panel
        self.editor_anchor = QDockWidget("main.cpp", self)
        self.editor_anchor.setWidget(EditorWidget("main.cpp"))
        self.editor_anchor.setFeatures(
            QDockWidget.DockWidgetMovable
            | QDockWidget.DockWidgetClosable
            | QDockWidget.DockWidgetFloatable
        )
        self.editor_anchor.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.addDockWidget(Qt.RightDockWidgetArea, self.editor_anchor)
        self.splitDockWidget(self.left_panel, self.editor_anchor, Qt.Horizontal)
        self.editor_docks.append(self.editor_anchor)

        # Step 3: Split TOP and BOTTOM from editor
        self.top_panel = self._make_panel("Top Panel")
        self.addDockWidget(Qt.TopDockWidgetArea, self.top_panel)
        self.splitDockWidget(self.editor_anchor, self.top_panel, Qt.Vertical)

        self.bottom_panel = self._make_panel("Bottom Panel")
        self.addDockWidget(Qt.BottomDockWidgetArea, self.bottom_panel)
        self.splitDockWidget(self.editor_anchor, self.bottom_panel, Qt.Vertical)

        # Step 4: Add right panel to the right of the editor
        self.right_panel = self._make_panel("Right Panel")
        self.addDockWidget(Qt.RightDockWidgetArea, self.right_panel)
        self.splitDockWidget(self.editor_anchor, self.right_panel, Qt.Horizontal)

        # Step 5: Add more editors and tabify
        for name in ["engine.cpp", "ui.cpp"]:
            dock = QDockWidget(name, self)
            dock.setWidget(EditorWidget(name))
            dock.setAllowedAreas(Qt.AllDockWidgetAreas)
            dock.setFeatures(
                QDockWidget.DockWidgetMovable
                | QDockWidget.DockWidgetClosable
                | QDockWidget.DockWidgetFloatable
            )
            self.addDockWidget(Qt.RightDockWidgetArea, dock)
            self.tabifyDockWidget(self.editor_anchor, dock)
            self.editor_docks.append(dock)

        self.editor_anchor.raise_()

    def _setup_toolbar(self) -> None:
        toolbar = QToolBar("Toggles", self)
        self.addToolBar(toolbar)

        for label, dock in [
            ("Left Panel", self.left_panel),
            ("Top Panel", self.top_panel),
            ("Right Panel", self.right_panel),
            ("Bottom Panel", self.bottom_panel),
        ]:
            action = QAction(label, self, checkable=True)
            action.setChecked(True)
            action.toggled.connect(
                lambda checked, d=dock: d.setVisible(checked) if d else None
            )
            toolbar.addAction(action)

    def _make_panel(self, title: str) -> QDockWidget:
        dock = QDockWidget(title, self)
        dock.setWidget(PanelWidget(title))
        dock.setAllowedAreas(Qt.AllDockWidgetAreas)
        dock.setFeatures(
            QDockWidget.DockWidgetMovable
            | QDockWidget.DockWidgetClosable
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

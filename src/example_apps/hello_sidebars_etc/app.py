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
    QTabBar,
    QTabWidget,
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
        self.resize(2048, 1152)
        self.setDockNestingEnabled(True)

        # Panels
        self.left_panel: QDockWidget = self._make_panel("Left Panel")
        self.right_panel: QDockWidget = self._make_panel("Right Panel")
        self.top_panel: QDockWidget = self._make_panel("Top Panel")
        self.bottom_panel: QDockWidget = self._make_panel("Bottom Panel")

        self.addDockWidget(Qt.TopDockWidgetArea, self.top_panel)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.bottom_panel)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.left_panel)

        # Editors tabified in the center (one dock anchor, others tabified into it)
        self.editor_docks: list[QDockWidget] = []
        first_editor = self._make_editor("main.cpp")
        self.addDockWidget(Qt.RightDockWidgetArea, first_editor)
        self.editor_docks.append(first_editor)

        self.addDockWidget(Qt.RightDockWidgetArea, self.right_panel)
        self.splitDockWidget(first_editor, self.right_panel, Qt.Horizontal)

        for filename in ["engine.cpp", "ui.cpp"]:
            dock = self._make_editor(filename)
            self.addDockWidget(Qt.RightDockWidgetArea, dock)
            self.tabifyDockWidget(first_editor, dock)
            self.editor_docks.append(dock)

        first_editor.raise_()
        self._setup_toolbar()
        self._make_tabs_closable()

        # Resize initial layout to ideal proportions
        self.resizeDocks(
            [self.left_panel, first_editor, self.right_panel],
            [200, 1648, 200],
            Qt.Horizontal,
        )
        self.resizeDocks(
            [self.top_panel, first_editor, self.bottom_panel],
            [100, 902, 150],
            Qt.Vertical,
        )

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

    def _make_tabs_closable(self) -> None:
        self.setTabPosition(Qt.AllDockWidgetAreas, QTabWidget.TabPosition.North)

        for tab_bar in self.findChildren(QTabBar):
            tab_bar.setTabsClosable(True)
            tab_bar.tabCloseRequested.connect(self._handle_tab_close)

    def _handle_tab_close(self, index: int) -> None:
        tab_bar = self.sender()
        if isinstance(tab_bar, QTabBar):
            tab_text = tab_bar.tabText(index)
            for dock in self.editor_docks:
                if dock.windowTitle() == tab_text:
                    self.removeDockWidget(dock)
                    dock.deleteLater()
                    self.editor_docks.remove(dock)
                    break

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

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
from PySide6.QtCore import QEvent, Qt

from PySide6.QtWidgets import QTabBar
from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QMouseEvent


class DockTabBar(QTabBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._drag_start_pos: Optional[QPoint] = None

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self._drag_start_pos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if (
            self._drag_start_pos is not None
            and (event.pos() - self._drag_start_pos).manhattanLength()
            > QApplication.startDragDistance()
        ):
            index = self.tabAt(self._drag_start_pos)
            if index != -1:
                tab_text = self.tabText(index)
                self.parent()._undock_tab(
                    tab_text
                )  # We'll define this on the main window
                self._drag_start_pos = None  # prevent multiple triggers
        super().mouseMoveEvent(event)


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
            tab_bar.setMovable(True)
            tab_bar.tabCloseRequested.connect(self._handle_tab_close)
            tab_bar.installEventFilter(self)

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

    def _undock_tab(self, tab_text: str) -> None:
        print(f"Undocking tab: {tab_text}")
        dock_to_undock: Optional[QDockWidget] = None

        for dock in self.editor_docks:
            if dock.windowTitle() == tab_text:
                dock_to_undock = dock
                break

        if not dock_to_undock:
            return

        # Undock cleanly by moving it away from the tab group first
        self.removeDockWidget(dock_to_undock)
        self.addDockWidget(Qt.RightDockWidgetArea, dock_to_undock)

        # Make it float and show
        dock_to_undock.setFloating(True)
        dock_to_undock.show()

        # Ensure one tab remains focused/raised if we still have them
        remaining_tabs = [d for d in self.editor_docks if d != dock_to_undock]
        if remaining_tabs:
            remaining_tabs[0].raise_()

    def eventFilter(self, obj, event):
        if isinstance(obj, QTabBar):
            if (
                event.type() == QEvent.Type.MouseButtonPress
                and event.button() == Qt.MouseButton.LeftButton
            ):
                self._drag_start_pos = event.pos()
                self._drag_tab_index = obj.tabAt(event.pos())
                self._drag_tab_text = (
                    obj.tabText(self._drag_tab_index)
                    if self._drag_tab_index != -1
                    else None
                )

            elif (
                event.type() == QEvent.Type.MouseMove
                and hasattr(self, "_drag_tab_index")
                and self._drag_tab_index != -1
                and self._drag_tab_text
            ):
                distance = (event.pos() - self._drag_start_pos).manhattanLength()
                if distance > QApplication.startDragDistance():
                    tab_bar_rect = obj.rect()
                    margin = 50
                    inflated_rect = tab_bar_rect.adjusted(
                        -margin, -margin, margin, margin
                    )
                    if not inflated_rect.contains(event.pos()):
                        print(f"Undocking tab: {self._drag_tab_text}")
                        self._undock_tab(self._drag_tab_text)
                        self._drag_tab_index = -1
                        self._drag_tab_text = None

            elif event.type() in {QEvent.Type.MouseButtonRelease, QEvent.Type.Leave}:
                self._drag_tab_index = -1
                self._drag_tab_text = None

        return super().eventFilter(obj, event)


def main() -> None:
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 9))
    window = IDEMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

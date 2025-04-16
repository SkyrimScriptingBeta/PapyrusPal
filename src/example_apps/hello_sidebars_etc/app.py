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
from PySide6.QtCore import QEvent, Qt, QTimer, QPoint


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
        self.left_panel = self._make_panel("Left Panel")
        self.right_panel = self._make_panel("Right Panel")
        self.top_panel = self._make_panel("Top Panel")
        self.bottom_panel = self._make_panel("Bottom Panel")

        self.addDockWidget(Qt.TopDockWidgetArea, self.top_panel)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.bottom_panel)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.left_panel)

        # Center editors (tabbified)
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

            QTimer.singleShot(0, lambda d=dock: self._update_title_bar_for(d))

        for dock in self.editor_docks + [
            self.left_panel,
            self.right_panel,
            self.top_panel,
            self.bottom_panel,
        ]:
            dock.topLevelChanged.connect(self._update_title_bar_for)
            dock.dockLocationChanged.connect(
                lambda _, d=dock: self._update_title_bar_for(d)
            )

        first_editor.raise_()
        self._update_title_bar_for(first_editor)  # 🔥 FIX for main.cpp title bar

        self._setup_toolbar()
        self._make_tabs_closable()

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
            if self.editor_docks:
                self.editor_docks[0].raise_()
                self._update_title_bar_for(self.editor_docks[0])

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
        dock_to_undock: Optional[QDockWidget] = None

        for dock in self.editor_docks:
            if dock.windowTitle() == tab_text:
                dock_to_undock = dock
                break

        if not dock_to_undock:
            return

        self.removeDockWidget(dock_to_undock)
        self.addDockWidget(Qt.RightDockWidgetArea, dock_to_undock)
        dock_to_undock.setFloating(True)
        dock_to_undock.show()

        remaining_tabs = [d for d in self.editor_docks if d != dock_to_undock]
        if remaining_tabs:
            remaining_tabs[0].raise_()

        QTimer.singleShot(0, lambda d=dock_to_undock: self._update_title_bar_for(d))

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
                        self._undock_tab(self._drag_tab_text)
                        self._drag_tab_index = -1
                        self._drag_tab_text = None

            elif event.type() in {QEvent.Type.MouseButtonRelease, QEvent.Type.Leave}:
                self._drag_tab_index = -1
                self._drag_tab_text = None

        return super().eventFilter(obj, event)

    def _update_title_bar_for(self, dock: QDockWidget) -> None:
        is_tabbified = any(
            other in self.tabifiedDockWidgets(dock)
            for other in self.findChildren(QDockWidget)
            if other is not dock
        )

        should_hide = is_tabbified
        current = dock.titleBarWidget()

        if should_hide:
            if (
                current is None
                or not isinstance(current, QWidget)
                or current.sizeHint().height() > 0
            ):
                hidden_bar = QWidget()
                hidden_bar.setFixedHeight(0)
                dock.setTitleBarWidget(hidden_bar)
        else:
            if current is not None:
                dock.setTitleBarWidget(None)


def main() -> None:
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 9))
    window = IDEMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

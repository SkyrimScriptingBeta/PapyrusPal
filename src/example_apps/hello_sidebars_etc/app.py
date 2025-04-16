import sys
from typing import cast, List, override
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
from PySide6.QtGui import QAction, QFont, QMouseEvent
from PySide6.QtCore import QEvent, Qt, QPoint, QObject


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

        # Initialize instance variables for type checking
        self._drag_tab_start_pos: QPoint = QPoint()
        self._drag_tab_index: int = -1
        self._drag_tab_text: str | None = None

        self.left_panel = self._make_panel("Left Panel")
        self.right_panel = self._make_panel("Right Panel")
        self.top_panel = self._make_panel("Top Panel")
        self.bottom_panel = self._make_panel("Bottom Panel")

        self.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, self.top_panel)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.bottom_panel)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.left_panel)

        self.editor_docks: List[QDockWidget] = []
        first_editor = self._make_editor("main.cpp")
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, first_editor)
        self.editor_docks.append(first_editor)

        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.right_panel)
        self.splitDockWidget(first_editor, self.right_panel, Qt.Orientation.Horizontal)

        for filename in ["engine.cpp", "ui.cpp"]:
            dock = self._make_editor(filename)
            self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
            self.tabifyDockWidget(first_editor, dock)
            self.editor_docks.append(dock)

        for dock in self.findChildren(QDockWidget):
            dock.topLevelChanged.connect(self._update_title_bar_for)
            # Use a typed lambda
            dock.dockLocationChanged.connect(
                lambda _ignored, d=dock: self._update_title_bar_for(d)
            )

        first_editor.raise_()
        self._update_title_bar_for(first_editor)

        self._setup_toolbar()
        self._make_tabs_closable()

        self.resizeDocks(
            [self.left_panel, first_editor, self.right_panel],
            [200, 1648, 200],
            Qt.Orientation.Horizontal,
        )
        self.resizeDocks(
            [self.top_panel, first_editor, self.bottom_panel],
            [100, 902, 150],
            Qt.Orientation.Vertical,
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
            # Use a typed lambda with a captured dock variable
            action.toggled.connect(
                lambda checked_state, d=dock: self._toggle_dock_visibility(
                    d, bool(checked_state)
                )
            )
            toolbar.addAction(action)

    def _toggle_dock_visibility(self, dock: QDockWidget, visible: bool) -> None:
        dock.setVisible(visible)
        if visible:
            self._update_title_bar_for(dock)

    def _make_tabs_closable(self) -> None:
        self.setTabPosition(
            Qt.DockWidgetArea.AllDockWidgetAreas, QTabWidget.TabPosition.North
        )

    # Override the event method from QMainWindow
    @override
    def event(self, event: QEvent) -> bool:
        if event.type() == QEvent.Type.LayoutRequest:
            self._install_tab_features()
        return super().event(event)

    def _install_tab_features(self) -> None:
        for tab_bar in self.findChildren(QTabBar):
            if not tab_bar.property("_customized"):
                tab_bar.setTabsClosable(True)
                tab_bar.setMovable(True)
                tab_bar.tabCloseRequested.connect(self._handle_tab_close)
                tab_bar.installEventFilter(self)
                tab_bar.setProperty("_customized", True)

    @override
    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if isinstance(watched, QTabBar):
            tab_bar = watched
            if event.type() == QEvent.Type.MouseButtonPress:
                mouse_event = cast(QMouseEvent, event)
                self._drag_tab_start_pos = mouse_event.pos()
                self._drag_tab_index = tab_bar.tabAt(self._drag_tab_start_pos)
                if self._drag_tab_index >= 0:
                    self._drag_tab_text = tab_bar.tabText(self._drag_tab_index)
            elif (
                event.type() == QEvent.Type.MouseMove
                and self._drag_tab_text is not None
            ):
                mouse_event = cast(QMouseEvent, event)
                margin = 50
                padded = tab_bar.rect().adjusted(-margin, -margin, margin, margin)
                if not padded.contains(mouse_event.pos()):
                    self._undock_tab(self._drag_tab_text)
                    self._drag_tab_text = None
            elif event.type() in {QEvent.Type.MouseButtonRelease, QEvent.Type.Leave}:
                self._drag_tab_text = None
        return super().eventFilter(watched, event)

    def _handle_tab_close(self, index: int) -> None:
        tab_bar = self.sender()
        if isinstance(tab_bar, QTabBar):
            tab_text = tab_bar.tabText(index)
            for dock in self.findChildren(QDockWidget):
                if dock.windowTitle() == tab_text:
                    self.removeDockWidget(dock)
                    dock.deleteLater()
                    if dock in self.editor_docks:
                        self.editor_docks.remove(dock)
                    break

    def _make_panel(self, title: str) -> QDockWidget:
        dock = QDockWidget(title, self)
        dock.setWidget(PanelWidget(title))
        dock.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable
            | QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        return dock

    def _make_editor(self, filename: str) -> QDockWidget:
        dock = QDockWidget(filename, self)
        dock.setWidget(EditorWidget(filename))
        dock.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable
            | QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        return dock

    def _undock_tab(self, tab_text: str) -> None:
        for dock in self.findChildren(QDockWidget):
            if dock.windowTitle() == tab_text:
                siblings = self.tabifiedDockWidgets(dock)
                self.removeDockWidget(dock)
                self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
                dock.setFloating(True)
                dock.show()

                # Update all previously tabified docks (including the undocked one)
                for d in siblings + [dock]:
                    self._update_title_bar_for(d)
                break

    def _update_title_bar_for(self, dock: QDockWidget) -> None:
        tab_group = self.tabifiedDockWidgets(dock)
        if dock not in tab_group:
            tab_group.append(dock)

        for w in tab_group:
            # Skip non-QDockWidget items (should not happen, but type check)
            if not isinstance(w, QDockWidget):
                continue

            is_tabbified = any(
                other in self.tabifiedDockWidgets(w)
                for other in self.findChildren(QDockWidget)
                if other is not w
            )

            if is_tabbified:
                current = w.titleBarWidget()
                # Check if we need to hide the title bar
                if current is None or current.sizeHint().height() > 0:
                    hidden = QWidget()
                    hidden.setFixedHeight(0)
                    w.setTitleBarWidget(hidden)
            else:
                # Show the title bar by creating a temporary widget first
                # This is a workaround for the None issue
                temp_widget = QWidget()
                w.setTitleBarWidget(temp_widget)
                w.setTitleBarWidget(None)


def main() -> None:
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 9))
    window = IDEMainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

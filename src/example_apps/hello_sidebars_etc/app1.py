import sys
from typing import Optional
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget,
    QWidget,
    QDockWidget,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QToolBar,
    QStatusBar,
    QTabBar,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QFont


class CentralWidget(QWidget):
    def __init__(self, title: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        label = QLabel(f"<h1>{title}</h1>")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        text = QTextEdit()
        text.setPlaceholderText(f"This is the content area for {title} content...")
        layout.addWidget(text)
        self.setLayout(layout)


class SideWidget1(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        label = QLabel("<h2>Side Widget 1</h2>")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        btn = QPushButton("Test Button")
        layout.addWidget(btn)
        layout.addStretch()
        self.setLayout(layout)


class SideWidget2(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        label = QLabel("<h2>Side Widget 2</h2>")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        btn = QPushButton("Right Side Button")
        layout.addWidget(btn)
        layout.addStretch()
        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Docking Example - IDE Style")
        self.resize(1000, 600)
        self.setDockNestingEnabled(True)
        self.setTabPosition(
            Qt.DockWidgetArea.AllDockWidgetAreas, QTabWidget.TabPosition.North
        )
        self.setStatusBar(QStatusBar(self))
        self.central_docks: list[QDockWidget] = []
        self.dock_widgets: dict[str, QDockWidget] = {}
        self._setup_central_docks()
        self._setup_side_dock()
        self._setup_toolbar()
        self._make_tabs_closable()

    def _setup_central_docks(self) -> None:
        titles = ["Tab 1", "Tab 2", "Tab 3"]
        for i, title in enumerate(titles):
            dock = QDockWidget(title, self)
            dock.setWidget(CentralWidget(title, self))
            dock.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
            dock.setFeatures(
                QDockWidget.DockWidgetFeature.DockWidgetClosable
                | QDockWidget.DockWidgetFeature.DockWidgetMovable
                | QDockWidget.DockWidgetFeature.DockWidgetFloatable
            )
            if i == 0:
                self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
            else:
                self.tabifyDockWidget(self.central_docks[0], dock)
            self.central_docks.append(dock)
            self.dock_widgets[title] = dock
        self.central_docks[0].raise_()

    def _setup_side_dock(self) -> None:
        # Left side dock
        self.side_dock1 = QDockWidget("Side Widget 1", self)
        self.side_dock1.setWidget(SideWidget1(self))
        self.side_dock1.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.side_dock1)
        self.side_dock1.hide()
        self.dock_widgets["side_widget1"] = self.side_dock1

        # Right side dock
        self.side_dock2 = QDockWidget("Side Widget 2", self)
        self.side_dock2.setWidget(SideWidget2(self))
        self.side_dock2.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.side_dock2)
        self.side_dock2.hide()
        self.dock_widgets["side_widget2"] = self.side_dock2

    def _setup_toolbar(self) -> None:
        toolbar = QToolBar("Toolbar", self)
        self.addToolBar(toolbar)

        # Left panel toggle
        toggle_left_action = QAction("Toggle Left Panel", self)
        toggle_left_action.setCheckable(True)
        toggle_left_action.toggled.connect(self.toggle_left_panel)
        toolbar.addAction(toggle_left_action)

        # Right panel toggle
        toggle_right_action = QAction("Toggle Right Panel", self)
        toggle_right_action.setCheckable(True)
        toggle_right_action.toggled.connect(self.toggle_right_panel)
        toolbar.addAction(toggle_right_action)

        # Add tab action
        add_tab_action = QAction("Add Tab", self)
        add_tab_action.triggered.connect(self.add_new_tab)
        toolbar.addAction(add_tab_action)

    def _make_tabs_closable(self) -> None:
        for tab_bar in self.findChildren(QTabBar):
            tab_bar.setTabsClosable(True)
            tab_bar.tabCloseRequested.connect(self._handle_tab_close)

    def _handle_tab_close(self, index: int) -> None:
        tab_bar = self.sender()
        if isinstance(tab_bar, QTabBar):
            tab_text = tab_bar.tabText(index)
            dock = self.dock_widgets.get(tab_text)
            if dock:
                self.removeDockWidget(dock)
                dock.deleteLater()
                self.central_docks = [d for d in self.central_docks if d != dock]
                del self.dock_widgets[tab_text]

    def toggle_left_panel(self, checked: bool) -> None:
        if checked:
            self.side_dock1.show()
        else:
            self.side_dock1.hide()

    def get_first_right_dock(self) -> Optional[QDockWidget]:
        """Find the first dock widget in the right dock area."""
        for dock in self.findChildren(QDockWidget):
            area = self.dockWidgetArea(dock)
            if (
                area == Qt.DockWidgetArea.RightDockWidgetArea
                and dock != self.side_dock2
            ):
                return dock
        return None

    def toggle_right_panel(self, checked: bool) -> None:
        if checked:
            # Only add it once
            if self.side_dock2 not in self.findChildren(QDockWidget):
                # Add it to the right dock area
                self.addDockWidget(
                    Qt.DockWidgetArea.RightDockWidgetArea, self.side_dock2
                )

                # Find a dock widget in the right area to split with
                dock_to_split = self.get_first_right_dock()
                if dock_to_split:
                    # Split it horizontally with the found dock
                    self.splitDockWidget(
                        dock_to_split,
                        self.side_dock2,
                        Qt.Orientation.Horizontal,
                    )

            # Show the dock
            self.side_dock2.show()
        else:
            self.side_dock2.hide()

    def add_new_tab(self) -> None:
        tab_count = len([k for k in self.dock_widgets if k.startswith("Tab ")]) + 1
        title = f"Tab {tab_count}"
        dock = QDockWidget(title, self)
        dock.setWidget(CentralWidget(title, self))
        dock.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetClosable
            | QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
        if self.central_docks:
            self.tabifyDockWidget(self.central_docks[0], dock)
        self.central_docks.append(dock)
        self.dock_widgets[title] = dock
        dock.raise_()


def main() -> None:
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 9))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

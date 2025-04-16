import sys
from typing import Optional, Dict, cast, List
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QDockWidget,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QToolBar,
    QStatusBar,
    QMenu,
    QTabWidget,
    QSizePolicy,
    QTabBar,
)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QAction, QFont


class CentralWidget(QWidget):
    """Widget to be used as the central content in tabs."""

    def __init__(self, title: str = "Central Widget", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.title = title

        # Set background color
        self.setStyleSheet(
            "background-color: #263238; color: #ffffff;"
        )  # Dark blue-gray

        # Create layout
        layout = QVBoxLayout(self)

        # Add content
        title_label = QLabel(f"<h1>{title}</h1>")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(
            "background-color: #37474f; color: #ffffff;"
        )  # Darker blue-gray

        content = QTextEdit()
        content.setPlaceholderText(
            f"This is the content area for {title}.\n\n"
            + f"You can type here to test the widget."
        )
        content.setStyleSheet(
            "background-color: #455a64; color: #ffffff;"
        )  # Medium blue-gray

        layout.addWidget(title_label)
        layout.addWidget(content)

        self.setLayout(layout)


class SideWidget1(QWidget):
    """Widget to be docked on the left side."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        # Set background color
        self.setStyleSheet("background-color: #3e2723; color: #ffffff;")  # Dark brown

        # Create layout
        layout = QVBoxLayout(self)

        # Add content
        title_label = QLabel("<h2>Side Widget 1</h2>")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(
            "background-color: #4e342e; color: #ffffff;"
        )  # Darker brown

        description = QLabel(
            "This widget is docked on the LEFT side.\n"
            + "You can toggle it from the View menu."
        )
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setWordWrap(True)
        description.setStyleSheet(
            "background-color: #5d4037; color: #ffffff;"
        )  # Medium brown

        button = QPushButton("Test Button")
        button.clicked.connect(
            lambda: cast(QMainWindow, self.parent().parent())
            .statusBar()
            .showMessage("Side Widget 1 button clicked", 2000)
        )
        button.setStyleSheet(
            "background-color: #6d4c41; color: #ffffff;"
        )  # Lighter brown

        layout.addWidget(title_label)
        layout.addWidget(description)
        layout.addWidget(button)
        layout.addStretch()

        self.setMinimumWidth(200)
        self.setLayout(layout)


class SideWidget2(QWidget):
    """Widget to be docked on the right side."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        # Set background color
        self.setStyleSheet("background-color: #1b5e20; color: #ffffff;")  # Dark green

        # Create layout
        layout = QVBoxLayout(self)

        # Add content
        title_label = QLabel("<h2>Side Widget 2</h2>")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(
            "background-color: #2e7d32; color: #ffffff;"
        )  # Darker green

        description = QLabel(
            "This widget is docked on the RIGHT side.\n"
            + "You can toggle it from the View menu."
        )
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setWordWrap(True)
        description.setStyleSheet(
            "background-color: #388e3c; color: #ffffff;"
        )  # Medium green

        button = QPushButton("Test Button")
        button.clicked.connect(
            lambda: cast(QMainWindow, self.parent().parent())
            .statusBar()
            .showMessage("Side Widget 2 button clicked", 2000)
        )
        button.setStyleSheet(
            "background-color: #43a047; color: #ffffff;"
        )  # Lighter green

        layout.addWidget(title_label)
        layout.addWidget(description)
        layout.addWidget(button)
        layout.addStretch()

        self.setMinimumWidth(200)
        self.setLayout(layout)


class DockableWidget(QDockWidget):
    """A dockable widget that can be moved, closed, and docked in different areas."""

    def __init__(
        self,
        title: str,
        parent: Optional[QMainWindow] = None,
        content: Optional[QWidget] = None,
    ):
        super().__init__(title, parent)

        # Set docking features
        self.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
            | QDockWidget.DockWidgetFeature.DockWidgetClosable
        )

        # Set allowed areas
        self.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)

        # Set content
        if content:
            self.setWidget(content)


class MainWindow(QMainWindow):
    """Main application window with docking functionality."""

    def __init__(self):
        super().__init__()

        # Initialize instance variables
        self.view_menu: Optional[QMenu] = None
        self.side_widget1_action: Optional[QAction] = None
        self.side_widget2_action: Optional[QAction] = None
        self.dock_widgets: Dict[str, QDockWidget] = {}
        self.central_docks: List[DockableWidget] = []

        # Window setup
        self.setWindowTitle("PySide6 Docking Example")
        self.resize(1000, 600)

        # Enable docking in central area
        self.setDockNestingEnabled(True)

        # Ensure tabs appear at the top for all dock areas
        self.setTabPosition(
            Qt.DockWidgetArea.AllDockWidgetAreas, QTabWidget.TabPosition.North
        )

        # Set up UI components
        self._setup_menu_bar()
        self._setup_status_bar()
        self._setup_tool_bar()

        # Set main window background color
        self.setStyleSheet("background-color: #212121; color: #ffffff;")  # Dark gray

        # Set up central widget - a placeholder to ensure proper layout
        central_widget = QWidget()
        central_widget.setStyleSheet(
            "background-color: #424242; color: #ffffff;"
        )  # Medium gray
        self.setCentralWidget(central_widget)

        # --- Central Dock Setup ---
        self._setup_central_docks()

        # Make tabs closable
        QTimer.singleShot(0, self._make_tabs_closable)

        # Show a welcome message
        self.statusBar().showMessage("Application started", 3000)

    def _setup_central_docks(self) -> None:
        """Set up the central area with dockable widgets."""
        for i in range(1, 4):
            title = f"Tab {i}"
            content = CentralWidget(f"{title} Content")
            dock_widget = DockableWidget(title, self, content)

            # Allow docking anywhere
            dock_widget.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)

            # Ensure dock widgets expand to fill available space
            dock_widget.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
            )

            # Add to the main window
            self.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, dock_widget)

            # Keep track of dock widgets
            self.dock_widgets[title] = dock_widget
            self.central_docks.append(dock_widget)

            # Tabify dock widgets
            if i > 1:
                self.tabifyDockWidget(self.central_docks[0], dock_widget)

        # Activate the first dock widget
        self.central_docks[0].raise_()

    def add_new_tab(self) -> None:
        """Add a new dockable widget."""
        tab_count = len(self.central_docks) + 1
        title = f"Tab {tab_count}"
        content = CentralWidget(f"{title} Content")
        dock_widget = DockableWidget(title, self, content)

        # Allow docking anywhere
        dock_widget.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)

        # Add to the main window
        self.addDockWidget(Qt.DockWidgetArea.TopDockWidgetArea, dock_widget)

        # Tabify with the first central dock
        self.tabifyDockWidget(self.central_docks[0], dock_widget)

        # Keep track of dock widgets
        self.dock_widgets[title] = dock_widget
        self.central_docks.append(dock_widget)

        # Activate the new dock widget
        dock_widget.raise_()

        self.statusBar().showMessage(f"Added new tab: {title}", 2000)

    def _setup_menu_bar(self) -> None:
        """Set up the menu bar with menus and actions."""
        # Create menu bar
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("&File")

        new_action = QAction("&New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(
            lambda: self.statusBar().showMessage("New file action triggered", 2000)
        )
        file_menu.addAction(new_action)

        open_action = QAction("&Open", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(
            lambda: self.statusBar().showMessage("Open file action triggered", 2000)
        )
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menu_bar.addMenu("&Edit")

        cut_action = QAction("Cu&t", self)
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(
            lambda: self.statusBar().showMessage("Cut action triggered", 2000)
        )
        edit_menu.addAction(cut_action)

        copy_action = QAction("&Copy", self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(
            lambda: self.statusBar().showMessage("Copy action triggered", 2000)
        )
        edit_menu.addAction(copy_action)

        paste_action = QAction("&Paste", self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(
            lambda: self.statusBar().showMessage("Paste action triggered", 2000)
        )
        edit_menu.addAction(paste_action)

        # View menu
        self.view_menu = menu_bar.addMenu("&View")

        # Side Widget 1 action (left dock)
        self.side_widget1_action = QAction("Side Widget &1", self)
        self.side_widget1_action.setCheckable(True)
        self.side_widget1_action.triggered.connect(self.toggle_side_widget1)
        self.view_menu.addAction(self.side_widget1_action)

        # Side Widget 2 action (right dock)
        self.side_widget2_action = QAction("Side Widget &2", self)
        self.side_widget2_action.setCheckable(True)
        self.side_widget2_action.triggered.connect(self.toggle_side_widget2)
        self.view_menu.addAction(self.side_widget2_action)

        # Help menu
        help_menu = menu_bar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(
            lambda: self.statusBar().showMessage(
                "This is a PySide6 docking example application", 3000
            )
        )
        help_menu.addAction(about_action)

    def _setup_status_bar(self) -> None:
        """Set up the status bar."""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)

    def _setup_tool_bar(self) -> None:
        """Set up the toolbar with buttons."""
        tool_bar = QToolBar("Main Toolbar")
        tool_bar.setIconSize(QSize(16, 16))
        tool_bar.setStyleSheet(
            "background-color: #0d47a1; color: #ffffff;"
        )  # Dark blue
        self.addToolBar(tool_bar)

        # Add some buttons to the toolbar
        new_tab_action = QAction("New Tab", self)
        new_tab_action.triggered.connect(self.add_new_tab)
        tool_bar.addAction(new_tab_action)

        toggle_side1_action = QAction("Toggle Left Panel", self)
        toggle_side1_action.triggered.connect(self.toggle_side_widget1)
        tool_bar.addAction(toggle_side1_action)

        toggle_side2_action = QAction("Toggle Right Panel", self)
        toggle_side2_action.triggered.connect(self.toggle_side_widget2)
        tool_bar.addAction(toggle_side2_action)

    def _make_tabs_closable(self) -> None:
        """Find the QTabBar and make its tabs closable."""
        for tab_bar in self.findChildren(QTabBar):
            tab_bar.setTabsClosable(True)
            tab_bar.tabCloseRequested.connect(self._handle_tab_close)

    def _handle_tab_close(self, index: int) -> None:
        """Handle the tab close request by closing the corresponding dock widget."""
        tab_bar = self.sender()
        if isinstance(tab_bar, QTabBar):
            tab_text = tab_bar.tabText(index)
            for dock_name, dock_widget in list(self.dock_widgets.items()):
                if dock_widget.windowTitle() == tab_text:
                    self.removeDockWidget(dock_widget)
                    dock_widget.deleteLater()
                    del self.dock_widgets[dock_name]

                    # Also remove from central_docks if it's there
                    for i, dock in enumerate(self.central_docks):
                        if dock.windowTitle() == tab_text:
                            self.central_docks.pop(i)
                            break

                    self.statusBar().showMessage(f"Closed {tab_text}", 2000)
                    break

    def toggle_side_widget1(self) -> None:
        """Toggle the visibility of SideWidget1 (left dock)."""
        dock_name = "side_widget1"

        if dock_name in self.dock_widgets:
            # Remove existing dock widget
            dock_widget = self.dock_widgets[dock_name]
            self.removeDockWidget(dock_widget)
            dock_widget.deleteLater()
            del self.dock_widgets[dock_name]
            if self.side_widget1_action:
                self.side_widget1_action.setChecked(False)
            self.statusBar().showMessage("Side Widget 1 closed", 2000)
        else:
            # Create new dock widget
            dock_widget = DockableWidget("Side Widget 1", self, SideWidget1(self))

            # Allow docking anywhere for maximum flexibility
            dock_widget.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)

            # First, remove all existing dock widgets
            for existing_dock in list(self.dock_widgets.values()):
                self.removeDockWidget(existing_dock)

            # Add the side widget to the left dock area
            self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock_widget)

            # Store the dock widget
            self.dock_widgets[dock_name] = dock_widget

            # Re-add all other dock widgets
            for name, existing_dock in list(self.dock_widgets.items()):
                if name != dock_name:
                    if name.startswith("Tab "):
                        # Add central docks to the right of the side widget
                        self.addDockWidget(
                            Qt.DockWidgetArea.RightDockWidgetArea, existing_dock
                        )

                        # Tabify with the first central dock if not the first one
                        first_tab = next(
                            (
                                d
                                for n, d in self.dock_widgets.items()
                                if n.startswith("Tab ") and n != name
                            ),
                            None,
                        )
                        if first_tab:
                            self.tabifyDockWidget(first_tab, existing_dock)
                    elif name == "side_widget2":
                        # Add right side widget
                        self.addDockWidget(
                            Qt.DockWidgetArea.RightDockWidgetArea, existing_dock
                        )

            # Store the dock widget
            self.dock_widgets[dock_name] = dock_widget

            if self.side_widget1_action:
                self.side_widget1_action.setChecked(True)
            self.statusBar().showMessage("Side Widget 1 opened", 2000)

    def toggle_side_widget2(self) -> None:
        """Toggle the visibility of SideWidget2 (right dock)."""
        dock_name = "side_widget2"

        if dock_name in self.dock_widgets:
            # Remove existing dock widget
            dock_widget = self.dock_widgets[dock_name]
            self.removeDockWidget(dock_widget)
            dock_widget.deleteLater()
            del self.dock_widgets[dock_name]
            if self.side_widget2_action:
                self.side_widget2_action.setChecked(False)
            self.statusBar().showMessage("Side Widget 2 closed", 2000)
        else:
            # Create new dock widget
            dock_widget = DockableWidget("Side Widget 2", self, SideWidget2(self))

            # Allow docking anywhere for maximum flexibility
            dock_widget.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)

            # First, remove all existing dock widgets
            for existing_dock in list(self.dock_widgets.values()):
                self.removeDockWidget(existing_dock)

            # Add the side widget to the right dock area
            self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock_widget)

            # Store the dock widget
            self.dock_widgets[dock_name] = dock_widget

            # Re-add all other dock widgets
            for name, existing_dock in list(self.dock_widgets.items()):
                if name != dock_name:
                    if name.startswith("Tab "):
                        # Add central docks to the left of the side widget
                        self.addDockWidget(
                            Qt.DockWidgetArea.LeftDockWidgetArea, existing_dock
                        )

                        # Tabify with the first central dock if not the first one
                        first_tab = next(
                            (
                                d
                                for n, d in self.dock_widgets.items()
                                if n.startswith("Tab ") and n != name
                            ),
                            None,
                        )
                        if first_tab:
                            self.tabifyDockWidget(first_tab, existing_dock)
                    elif name == "side_widget1":
                        # Add left side widget
                        self.addDockWidget(
                            Qt.DockWidgetArea.LeftDockWidgetArea, existing_dock
                        )

            # Store the dock widget
            self.dock_widgets[dock_name] = dock_widget

            if self.side_widget2_action:
                self.side_widget2_action.setChecked(True)
            self.statusBar().showMessage("Side Widget 2 opened", 2000)


def main() -> None:
    """Main application entry point."""
    app = QApplication(sys.argv)

    # Set application-wide font (optional)
    app.setFont(QFont("Segoe UI", 9))

    # Create and show main window
    window = MainWindow()
    window.show()

    # Start the event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

import sys
from typing import Optional, Dict, cast
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QDockWidget,
    QTabWidget,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QToolBar,
    QStatusBar,
    QMenu,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QFont


class CentralWidget(QWidget):
    """Widget to be used as the central content in tabs."""

    def __init__(self, title: str = "Central Widget", parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.title = title

        # Create layout
        layout = QVBoxLayout(self)

        # Add content
        title_label = QLabel(f"<h1>{title}</h1>")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        content = QTextEdit()
        content.setPlaceholderText(
            f"This is the content area for {title}.\n\n"
            + f"You can type here to test the widget."
        )

        layout.addWidget(title_label)
        layout.addWidget(content)

        self.setLayout(layout)


class SideWidget1(QWidget):
    """Widget to be docked on the left side."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        # Create layout
        layout = QVBoxLayout(self)

        # Add content
        title_label = QLabel("<h2>Side Widget 1</h2>")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        description = QLabel(
            "This widget is docked on the LEFT side.\n"
            + "You can toggle it from the View menu."
        )
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setWordWrap(True)

        button = QPushButton("Test Button")
        button.clicked.connect(
            lambda: cast(QMainWindow, self.parent())
            .statusBar()
            .showMessage("Side Widget 1 button clicked", 2000)
        )

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

        # Create layout
        layout = QVBoxLayout(self)

        # Add content
        title_label = QLabel("<h2>Side Widget 2</h2>")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        description = QLabel(
            "This widget is docked on the RIGHT side.\n"
            + "You can toggle it from the View menu."
        )
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setWordWrap(True)

        button = QPushButton("Test Button")
        button.clicked.connect(
            lambda: cast(QMainWindow, self.parent())
            .statusBar()
            .showMessage("Side Widget 2 button clicked", 2000)
        )

        layout.addWidget(title_label)
        layout.addWidget(description)
        layout.addWidget(button)
        layout.addStretch()

        self.setMinimumWidth(200)
        self.setLayout(layout)


class MainWindow(QMainWindow):
    """Main application window with docking functionality."""

    def __init__(self):
        super().__init__()

        # Initialize instance variables
        self.tab_widget = QTabWidget()
        self.view_menu: Optional[QMenu] = None  # Will be initialized in _setup_menu_bar
        self.side_widget1_action: Optional[QAction] = (
            None  # Will be initialized in _setup_menu_bar
        )
        self.side_widget2_action: Optional[QAction] = (
            None  # Will be initialized in _setup_menu_bar
        )
        self.dock_widgets: Dict[str, QDockWidget] = {}

        # Window setup
        self.setWindowTitle("PySide6 Docking Example")
        self.resize(1000, 600)

        # Set up UI components
        self._setup_central_widget()
        self._setup_menu_bar()
        self._setup_status_bar()
        self._setup_tool_bar()

        # Show a welcome message
        self.statusBar().showMessage("Application started", 3000)

    def _setup_central_widget(self) -> None:
        """Set up the central widget with tabs."""
        # Configure tab widget
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setMovable(True)
        self.tab_widget.setTabsClosable(True)

        # Add tabs with CentralWidget instances
        for i in range(1, 4):
            tab = CentralWidget(f"Tab {i} Content")
            self.tab_widget.addTab(tab, f"Tab {i}")

        # Set as central widget
        self.setCentralWidget(self.tab_widget)

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

    def add_new_tab(self) -> None:
        """Add a new tab with a CentralWidget instance."""
        tab_count = self.tab_widget.count() + 1
        new_tab = CentralWidget(f"Tab {tab_count} Content")
        self.tab_widget.addTab(new_tab, f"Tab {tab_count}")
        self.tab_widget.setCurrentIndex(tab_count - 1)
        self.statusBar().showMessage(f"Added new tab: Tab {tab_count}", 2000)

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
            dock_widget = QDockWidget("Side Widget 1", self)
            dock_widget.setWidget(SideWidget1(self))
            dock_widget.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)

            self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock_widget)
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
            dock_widget = QDockWidget("Side Widget 2", self)
            dock_widget.setWidget(SideWidget2(self))
            dock_widget.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)

            self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock_widget)
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

import sys
from typing import Optional, cast
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QToolBar,
    QStatusBar,
    QMenu,
    QTabWidget,
    QSplitter,
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
            lambda: cast(QMainWindow, self.window())
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
            lambda: cast(QMainWindow, self.window())
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
        self.view_menu: Optional[QMenu] = None
        self.side_widget1_action: Optional[QAction] = None
        self.side_widget2_action: Optional[QAction] = None

        # Window setup
        self.setWindowTitle("PySide6 Docking Example")
        self.resize(1000, 600)

        # Create a central widget with a splitter layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Create a main layout for the central widget
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Create a splitter to divide the window into regions
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.splitter)

        # Create containers for each region
        self.left_container = QWidget()
        self.left_container.setVisible(False)  # Initially hidden

        self.center_container = QTabWidget()
        self.center_container.setTabsClosable(True)
        self.center_container.setMovable(True)
        self.center_container.setTabPosition(QTabWidget.TabPosition.North)
        self.center_container.tabCloseRequested.connect(self._handle_tab_close)

        self.right_container = QWidget()
        self.right_container.setVisible(False)  # Initially hidden

        # Add containers to splitter
        self.splitter.addWidget(self.left_container)
        self.splitter.addWidget(self.center_container)
        self.splitter.addWidget(self.right_container)

        # Set initial sizes (left hidden, center takes most space, right hidden)
        self.splitter.setSizes([0, 800, 0])

        # Set up UI components
        self._setup_menu_bar()
        self._setup_status_bar()
        self._setup_tool_bar()

        # --- Central Tabs Setup ---
        self._setup_central_tabs()

        # Show a welcome message
        self.statusBar().showMessage("Application started", 3000)

    def _setup_central_tabs(self) -> None:
        """Set up the central area with tabs."""
        for i in range(1, 4):
            title = f"Tab {i}"
            content = CentralWidget(f"{title} Content")

            # Add tab to the center container
            self.center_container.addTab(content, title)

    def add_new_tab(self) -> None:
        """Add a new tab to the central area."""
        tab_count = self.center_container.count() + 1
        title = f"Tab {tab_count}"
        content = CentralWidget(f"{title} Content")

        # Add tab to the center container
        index = self.center_container.addTab(content, title)

        # Activate the new tab
        self.center_container.setCurrentIndex(index)

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

    def _handle_tab_close(self, index: int) -> None:
        """Handle the tab close request."""
        # Get the tab text
        tab_text = self.center_container.tabText(index)

        # Remove the tab
        self.center_container.removeTab(index)

        self.statusBar().showMessage(f"Closed {tab_text}", 2000)

    def toggle_side_widget1(self) -> None:
        """Toggle the visibility of SideWidget1 (left side)."""
        if self.left_container.isVisible():
            # Hide the left container
            self.left_container.setVisible(False)

            # Update splitter sizes to give more space to center
            sizes = self.splitter.sizes()
            center_size = sizes[1] + sizes[0]
            self.splitter.setSizes([0, center_size, sizes[2]])

            if self.side_widget1_action:
                self.side_widget1_action.setChecked(False)

            self.statusBar().showMessage("Side Widget 1 closed", 2000)
        else:
            # Create the left container content if it doesn't exist
            if self.left_container.layout() is None:
                left_layout = QVBoxLayout(self.left_container)
                left_layout.setContentsMargins(0, 0, 0, 0)
                left_layout.addWidget(SideWidget1(self))

            # Show the left container
            self.left_container.setVisible(True)

            # Update splitter sizes
            sizes = self.splitter.sizes()
            left_size = 200
            center_size = max(400, sizes[1] - left_size)
            self.splitter.setSizes([left_size, center_size, sizes[2]])

            if self.side_widget1_action:
                self.side_widget1_action.setChecked(True)

            self.statusBar().showMessage("Side Widget 1 opened", 2000)

    def toggle_side_widget2(self) -> None:
        """Toggle the visibility of SideWidget2 (right side)."""
        if self.right_container.isVisible():
            # Hide the right container
            self.right_container.setVisible(False)

            # Update splitter sizes to give more space to center
            sizes = self.splitter.sizes()
            center_size = sizes[1] + sizes[2]
            self.splitter.setSizes([sizes[0], center_size, 0])

            if self.side_widget2_action:
                self.side_widget2_action.setChecked(False)

            self.statusBar().showMessage("Side Widget 2 closed", 2000)
        else:
            # Create the right container content if it doesn't exist
            if self.right_container.layout() is None:
                right_layout = QVBoxLayout(self.right_container)
                right_layout.setContentsMargins(0, 0, 0, 0)
                right_layout.addWidget(SideWidget2(self))

            # Show the right container
            self.right_container.setVisible(True)

            # Update splitter sizes
            sizes = self.splitter.sizes()
            right_size = 200
            center_size = max(400, sizes[1] - right_size)
            self.splitter.setSizes([sizes[0], center_size, right_size])

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

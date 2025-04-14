from dataclasses import field
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QLabel, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QToolBar, QComboBox

from qt_helpers.widget import widget
from qt_helpers.window import window
from papyrus_pal.widgets.source_code_textbox import SourceCodeTextBox


@widget()
class EditorWidget(QWidget):
    """Main editor widget containing the source code editor."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        print("EditorWidget initialized")
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create toolbar for editor
        editor_toolbar = QHBoxLayout()
        editor_toolbar.setContentsMargins(5, 5, 5, 5)
        
        # Add syntax highlighting dropdown
        self.highlighting_combo = QComboBox()
        self.highlighting_combo.addItems(["Papyrus", "None"])
        self.highlighting_combo.setCurrentIndex(0)
        self.highlighting_combo.currentTextChanged.connect(self.update_highlighting)
        editor_toolbar.addWidget(QLabel("Syntax:"))
        editor_toolbar.addWidget(self.highlighting_combo)
        
        # Add theme selector dropdown
        self.theme_combo = QComboBox()
        editor_toolbar.addWidget(QLabel("Theme:"))
        editor_toolbar.addWidget(self.theme_combo)
        
        editor_toolbar.addStretch()
        
        layout.addLayout(editor_toolbar)
        
        # Create source code textbox
        self.editor = SourceCodeTextBox()
        layout.addWidget(self.editor)
        
        # Populate theme dropdown and connect it
        self.populate_themes()
        self.theme_combo.currentTextChanged.connect(self.update_theme)
        
        # Initial highlighting setup
        self.update_highlighting("Papyrus")
    
    def populate_themes(self):
        """Populate the themes dropdown with available themes."""
        themes = self.editor.get_available_themes()
        self.theme_combo.addItems(themes)
        current_theme = self.editor.get_current_theme()
        index = self.theme_combo.findText(current_theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
    
    def update_theme(self, theme_name):
        """Update the editor theme."""
        self.editor.set_theme(theme_name)
        
        # Apply theme to entire application - use the singleton directly
        from papyrus_pal.app import app
        
        # Set application style based on theme
        if theme_name == "light":
            app.set_app_theme("light")
        else:
            # All other themes use dark mode
            app.set_app_theme("dark")
        
        # If Papyrus highlighting is active, reapply it with the new theme
        if self.highlighting_combo.currentText() == "Papyrus":
            self.editor.configure_papyrus_highlighting()
    
    def update_highlighting(self, highlighting_type):
        """Update the syntax highlighting based on the selected type."""
        if highlighting_type == "Papyrus":
            self.editor.configure_papyrus_highlighting()
        else:
            # Clear highlighting
            self.editor.configure_custom_highlighting()


@window()
class AppMainWindow(QMainWindow):
    """Main application window for PapyrusPal."""
    
    central_widget: EditorWidget = field(default_factory=EditorWidget)
    
    def _init(self):
        self.setWindowTitle("PapyrusPal - Papyrus Script Editor")
        self.resize(1000, 800)
        self.create_toolbar()
    
    def create_toolbar(self):
        """Create the main application toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        
        # Add actions
        new_action = QAction("New", self)
        new_action.setStatusTip("Create a new script")
        toolbar.addAction(new_action)
        
        open_action = QAction("Open", self)
        open_action.setStatusTip("Open an existing script")
        toolbar.addAction(open_action)
        
        save_action = QAction("Save", self)
        save_action.setStatusTip("Save current script")
        toolbar.addAction(save_action)
        
        self.addToolBar(toolbar)

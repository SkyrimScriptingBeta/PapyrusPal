
from dataclasses import field
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QLabel, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QToolBar, QComboBox

from qt_helpers.widget import widget
from qt_helpers.window import window
from papyrus_pal.app.widgets.source_code_textbox import SourceCodeTextBox


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
        editor_toolbar.addStretch()
        
        layout.addLayout(editor_toolbar)
        
        # Create source code textbox
        self.editor = SourceCodeTextBox()
        layout.addWidget(self.editor)
        
        # Initial highlighting setup
        self.update_highlighting("Papyrus")
    
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

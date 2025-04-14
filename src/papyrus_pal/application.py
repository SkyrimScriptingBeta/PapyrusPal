from PySide6.QtWidgets import QApplication, QStyleFactory
from PySide6.QtGui import QPalette, QColor


class Application(QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setApplicationName("Papyrus Pal")
        self.setApplicationDisplayName("Papyrus Pal")
        
        # Set default theme to dark mode (for Nord theme)
        self.set_app_theme("dark")
    
    def set_app_theme(self, theme_type):
        """Set application-wide theme to either 'light' or 'dark'"""
        if theme_type == "light":
            # Switch to light mode
            self.setStyle(QStyleFactory.create("Fusion"))
            palette = QPalette()
            # Use default palette (light)
            self.setPalette(palette)
        else:
            # Switch to dark mode
            self.setStyle(QStyleFactory.create("Fusion"))
            palette = QPalette()
            # Dark palette
            palette.setColor(QPalette.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
            palette.setColor(QPalette.Base, QColor(35, 35, 35))
            palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ToolTipBase, QColor(25, 25, 25))
            palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
            palette.setColor(QPalette.Text, QColor(255, 255, 255))
            palette.setColor(QPalette.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
            palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
            palette.setColor(QPalette.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
            
            # Set the modified palette
            self.setPalette(palette)

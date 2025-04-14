from PySide6.QtWidgets import QApplication

class Application(QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setApplicationName("Papyrus Pal")
        self.setApplicationDisplayName("Papyrus Pal")
        
        # Set default theme to dark mode (for Nord theme)
        self.set_app_theme("dark")
    
    def set_app_theme(self, theme_type):
        """Set application-wide theme to either 'light' or 'dark'"""
        pass

from PySide6.QtCore import QRegularExpression, Qt, QRect, QSize
from PySide6.QtGui import QColor, QTextCharFormat, QFont, QPainter, QSyntaxHighlighter
from PySide6.QtWidgets import QPlainTextEdit, QWidget

class SyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for the source code editor."""

    def __init__(self, document):
        super().__init__(document)
        self._highlighting_rules = []
        self._formats = {}
        
    def add_rule(self, pattern, format_name):
        """Add a highlighting rule based on a regex pattern and format name."""
        self._highlighting_rules.append((QRegularExpression(pattern), format_name))
        
    def add_format(self, format_name, foreground=None, background=None, bold=False, italic=False):
        """Define a named format with specified styling."""
        text_format = QTextCharFormat()
        
        if foreground:
            text_format.setForeground(QColor(foreground))
        if background:
            text_format.setBackground(QColor(background))
        if bold:
            text_format.setFontWeight(QFont.Bold)
        if italic:
            text_format.setFontItalic(True)
            
        self._formats[format_name] = text_format
    
    def highlightBlock(self, text):
        """Apply highlighting to the given block of text."""
        for pattern, format_name in self._highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(
                    match.capturedStart(), 
                    match.capturedLength(), 
                    self._formats.get(format_name, QTextCharFormat())
                )


class LineNumberArea(QWidget):
    """Widget for displaying line numbers."""
    
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
        
    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)
        
    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)


class SourceCodeTextBox(QPlainTextEdit):
    """Source code editor with configurable syntax highlighting and line numbers."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set up the editor
        font = QFont("Monospace", 10)
        font.setFixedPitch(True)
        self.setFont(font)
        
        # Set up line numbers
        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.update_line_number_area_width(0)
        
        # Initialize highlighter (but don't apply any rules yet)
        self.highlighter = SyntaxHighlighter(self.document())
    
    def configure_papyrus_highlighting(self):
        """Configure syntax highlighting for Papyrus language."""
        highlighter = self.highlighter
        
        # Clear any existing rules
        highlighter._highlighting_rules = []
        highlighter._formats = {}
        
        # Define formats
        highlighter.add_format("keyword", foreground="#569CD6", bold=True)
        highlighter.add_format("type", foreground="#4EC9B0")
        highlighter.add_format("string", foreground="#CE9178")
        highlighter.add_format("comment", foreground="#6A9955", italic=True)
        highlighter.add_format("function", foreground="#DCDCAA")
        highlighter.add_format("number", foreground="#B5CEA8")
        
        # Keywords
        keywords = [
            "if", "else", "elseif", "endif", 
            "while", "endwhile", 
            "function", "endfunction", 
            "return", "property", 
            "event", "endevent", 
            "scriptname", "extends", 
            "as", "new", "auto", "autoreadonly", 
            "native", "global"
        ]
        keyword_pattern = "\\b(" + "|".join(keywords) + ")\\b"
        highlighter.add_rule(keyword_pattern, "keyword")
        
        # Types
        types = ["int", "float", "string", "bool", "none"]
        type_pattern = "\\b(" + "|".join(types) + ")\\b"
        highlighter.add_rule(type_pattern, "type")
        
        # Strings
        highlighter.add_rule('"[^"\\\\]*(\\\\.[^"\\\\]*)*"', "string")
        
        # Comments
        highlighter.add_rule(";[^\n]*", "comment")
        
        # Functions
        highlighter.add_rule("\\b[A-Za-z0-9_]+(?=\\s*\\()", "function")
        
        # Numbers
        highlighter.add_rule("\\b\\d+\\.?\\d*\\b", "number")
        
        # Rehighlight
        highlighter.rehighlight()
    
    def configure_custom_highlighting(self, rules=None, formats=None):
        """
        Configure custom syntax highlighting.
        
        Args:
            rules: List of tuples (pattern, format_name)
            formats: Dict mapping format_name to dict of format properties
        """
        highlighter = self.highlighter
        
        # Clear existing rules
        highlighter._highlighting_rules = []
        highlighter._formats = {}
        
        # Add custom formats
        if formats:
            for name, properties in formats.items():
                highlighter.add_format(
                    name,
                    foreground=properties.get("foreground"),
                    background=properties.get("background"),
                    bold=properties.get("bold", False),
                    italic=properties.get("italic", False)
                )
        
        # Add custom rules
        if rules:
            for pattern, format_name in rules:
                highlighter.add_rule(pattern, format_name)
                
        # Rehighlight
        highlighter.rehighlight()
    
    def line_number_area_width(self):
        """Calculate the width of the line number area."""
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
            
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space
    
    def update_line_number_area_width(self, _):
        """Update the margin according to the line number area width."""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
    
    def update_line_number_area(self, rect, dy):
        """Update the line number area when the editor viewport scrolls."""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
            
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)
    
    def resizeEvent(self, event):
        """Handle resize events to adjust the line number area."""
        super().resizeEvent(event)
        
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )
    
    def line_number_area_paint_event(self, event):
        """Paint line numbers in the line number area."""
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), Qt.lightGray)
        
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(Qt.black)
                painter.drawText(
                    0, top, self.line_number_area.width(), self.fontMetrics().height(),
                    Qt.AlignRight, number
                )
            
            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_number += 1
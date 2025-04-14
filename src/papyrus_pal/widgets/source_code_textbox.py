from PySide6.QtCore import QRegularExpression, Qt, QRect, QSize
from PySide6.QtGui import QColor, QTextCharFormat, QFont, QPainter, QSyntaxHighlighter
from PySide6.QtWidgets import QPlainTextEdit, QWidget

# Define theme color dictionaries
THEMES = {
    "light": {
        "background": "#FFFFFF",
        "default": "#000000",
        "operator": "#000000",
        "flow_control": "#C000C0",
        "type": "#6060FF",
        "keyword": "#C000C0",
        "keyword2": "#6060FF",
        "fold_open": "#C000C0",
        "fold_middle": "#C000C0",
        "fold_close": "#C000C0",
        "comment": "#008000",
        "number": "#606060",
        "string": "#AA2200",
        "property": "#005555",
        "class": "#0000FF",
        "function": "#555500",
    },
    "dark": {
        "background": "#1E1E1E",
        "default": "#D4D4D4",
        "operator": "#D4D4D4",
        "flow_control": "#C586C0",
        "type": "#569CD6",
        "keyword": "#C586C0",
        "keyword2": "#9CDCFE",
        "fold_open": "#C586C0",
        "fold_middle": "#C586C0",
        "fold_close": "#C586C0",
        "comment": "#6A9955",
        "number": "#B5CEA8",
        "string": "#CE9178",
        "property": "#4EC9B0",
        "class": "#4EC9B0",
        "function": "#DCDCAA",
    },
    "nord": {
        "background": "#2E3440",
        "default": "#D8DEE9",
        "operator": "#81A1C1",
        "flow_control": "#81A1C1",
        "type": "#8FBCBB",
        "keyword": "#81A1C1",
        "keyword2": "#88C0D0",
        "fold_open": "#81A1C1",
        "fold_middle": "#81A1C1",
        "fold_close": "#81A1C1",
        "comment": "#616E88",
        "number": "#B48EAD",
        "string": "#A3BE8C",
        "property": "#8FBCBB",
        "class": "#8FBCBB",
        "function": "#88C0D0",
    },
    "monokai": {
        "background": "#272822",
        "default": "#F8F8F2",
        "operator": "#F92672",
        "flow_control": "#F92672",
        "type": "#66D9EF",
        "keyword": "#F92672",
        "keyword2": "#FD971F",
        "fold_open": "#F92672",
        "fold_middle": "#F92672",
        "fold_close": "#F92672",
        "comment": "#75715E",
        "number": "#AE81FF",
        "string": "#E6DB74",
        "property": "#A6E22E",
        "class": "#A6E22E",
        "function": "#A6E22E",
    }
}

class SyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for the source code editor."""

    def __init__(self, document):
        super().__init__(document)
        self._highlighting_rules = []
        self._formats = {}
        
    def add_rule(self, pattern, format_name):
        """Add a highlighting rule based on a regex pattern and format name."""
        regex = QRegularExpression(pattern)
        regex.setPatternOptions(QRegularExpression.CaseInsensitiveOption)
        self._highlighting_rules.append((regex, format_name))
        
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
    
    def __init__(self, parent=None, theme="nord"):
        super().__init__(parent)
        
        # Store current theme name
        self._current_theme = theme
        
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
        
        # Set background color based on theme
        self.set_theme(theme)
    
    def set_theme(self, theme_name):
        """Set the editor theme."""
        if theme_name not in THEMES:
            theme_name = "light"  # Default to light theme if not found
        
        self._current_theme = theme_name
        theme = THEMES[theme_name]
        
        # Set background color
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(theme["background"]))
        palette.setColor(self.foregroundRole(), QColor(theme["default"]))
        self.setPalette(palette)
        
        # If we have highlighting rules configured, re-apply them with new theme
        if hasattr(self, '_papyrus_highlighting_configured') and self._papyrus_highlighting_configured:
            self.configure_papyrus_highlighting()
        
        # Update line number area background
        self.update()
    
    def get_current_theme(self):
        """Get the current theme name."""
        return self._current_theme
    
    def get_available_themes(self):
        """Get list of available theme names."""
        return list(THEMES.keys())
    
    def configure_papyrus_highlighting(self):
        """Configure syntax highlighting for Papyrus language."""
        highlighter = self.highlighter
        theme = THEMES[self._current_theme]
        
        # Set flag to indicate this has been configured
        self._papyrus_highlighting_configured = True
        
        # Clear any existing rules
        highlighter._highlighting_rules = []
        highlighter._formats = {}
        
        # Define formats based on current theme
        highlighter.add_format("default", foreground=theme["default"])
        highlighter.add_format("operator", foreground=theme["operator"])
        highlighter.add_format("flow_control", foreground=theme["flow_control"])
        highlighter.add_format("type", foreground=theme["type"])
        highlighter.add_format("keyword", foreground=theme["keyword"])
        highlighter.add_format("keyword2", foreground=theme["keyword2"])
        highlighter.add_format("fold_open", foreground=theme["fold_open"])
        highlighter.add_format("fold_middle", foreground=theme["fold_middle"])
        highlighter.add_format("fold_close", foreground=theme["fold_close"])
        highlighter.add_format("comment", foreground=theme["comment"], italic=True)
        highlighter.add_format("number", foreground=theme["number"])
        highlighter.add_format("string", foreground=theme["string"])
        highlighter.add_format("property", foreground=theme["property"], bold=True)
        highlighter.add_format("class", foreground=theme["class"])
        highlighter.add_format("function", foreground=theme["function"])
        
        # Operators - instre1
        operators = r"\(|\)|\[|\]|\,|\=|\+|\-|\*|\/|\%|\.|\!|\>|\<|\||\&"
        highlighter.add_rule(operators, "operator")

        # Flow control - instre2
        flow_control = r"\b(if|else|elseif|endif|while|endwhile)\b"
        highlighter.add_rule(flow_control, "flow_control")
        
        # Types - type1
        types = r"\b(bool|float|int|string|var)\b"
        highlighter.add_rule(types, "type")
        
        # Keywords - type2
        keywords = (
            r"\b(scriptname|extends|import|debugonly|betaonly|default|event|endevent|"
            r"state|endstate|function|endfunction|global|native|struct|endstruct|"
            r"property|endproperty|auto|autoreadonly|conditional|hidden|const|"
            r"mandatory|group|endgroup|collapsed|collapsedonref|collapsedonbase|"
            r"new|return|length)\b"
        )
        highlighter.add_rule(keywords, "keyword")
        
        # Constants - type3
        constants = r"\b(none|parent|self|true|false)\b"
        highlighter.add_rule(constants, "keyword2")
        
        # Fold opening keywords - type4
        fold_open = r"\b(if|while|function|struct|property|group|event|state)\b"
        highlighter.add_rule(fold_open, "fold_open")
        
        # Fold middle keywords - type5
        fold_middle = r"\b(else|elseif)\b"
        highlighter.add_rule(fold_middle, "fold_middle")
        
        # Fold closing keywords - type6
        fold_close = (
            r"\b(endif|endwhile|endfunction|native|endstruct|endproperty|"
            r"auto|autoreadonly|endgroup|endevent|endstate)\b"
        )
        highlighter.add_rule(fold_close, "fold_close")
        
        # Single line comments
        highlighter.add_rule(r";.*$", "comment")
        
        # Multi-line comments - from Sublime Text pattern
        highlighter.add_rule(r";/.*?/;", "comment")
        
        # Documentation comments - from Sublime Text pattern
        highlighter.add_rule(r"\{.*?\}", "comment")
        
        # Numbers (integers and floats)
        highlighter.add_rule(r"\b(?:0x[0-9a-fA-F]+|\d+\.\d*|\d+)\b", "number")
        
        # Strings
        highlighter.add_rule(r'"[^"\\]*(\\.[^"\\]*)*"', "string")
        
        # Function calls
        highlighter.add_rule(r"\b[A-Za-z0-9_]+(?=\s*\()", "function")
        
        # Script name (class)
        highlighter.add_rule(r"(?<=scriptname\s+)[A-Za-z0-9_]+", "class")
        
        # Property names
        highlighter.add_rule(r"(?<=property\s+)[A-Za-z0-9_]+", "property")
        
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
        
        # Use theme colors for line number area
        theme = THEMES[self._current_theme]
        bg_color = QColor(theme["background"])
        bg_color = QColor(bg_color.red(), bg_color.green(), bg_color.blue(), 240)  # Add slight transparency
        
        painter.fillRect(event.rect(), bg_color)
        
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + round(self.blockBoundingRect(block).height())
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor(theme["comment"]))  # Use comment color for line numbers
                painter.drawText(
                    0, top, self.line_number_area.width(), self.fontMetrics().height(),
                    Qt.AlignRight, number
                )
            
            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_number += 1
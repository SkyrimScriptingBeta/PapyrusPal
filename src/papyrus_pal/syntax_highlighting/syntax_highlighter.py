"""Syntax highlighter for the source code editor."""

from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter

from papyrus_pal.syntax_highlighting.themes import light, dark, nord, monokai

# Dictionary to store all available themes
THEMES = {
    "light": light.THEME,
    "dark": dark.THEME,
    "nord": nord.THEME,
    "monokai": monokai.THEME,
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

    def add_format(
        self, format_name, foreground=None, background=None, bold=False, italic=False
    ):
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
                    self._formats.get(format_name, QTextCharFormat()),
                )

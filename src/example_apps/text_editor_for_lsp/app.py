"""
Simple text editor with LSP integration using PySide6 and pylspclient.
"""

import os
import sys
import threading
import subprocess
from pathlib import Path
from typing import List, Tuple

from PySide6.QtCore import Qt, QRect, QSize, Signal, QObject, QTimer
from PySide6.QtGui import (
    QColor,
    QTextCursor,
    QFont,
    QPainter,
    QKeyEvent,
    QMouseEvent,
    QFontMetrics,
    QTextCharFormat,
)
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPlainTextEdit,
    QStatusBar,
    QWidget,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QFrame,
)

# Import pylspclient for LSP functionality
try:
    import pylspclient

    HAS_PYLSPCLIENT = True
except ImportError:
    print("Warning: pylspclient not found. Using mock LSP implementation.")
    HAS_PYLSPCLIENT = False


# Mock LSP client implementation for when pylspclient is not available
if not HAS_PYLSPCLIENT:

    class MockJsonRpcEndpoint:
        def __init__(self, *args, **kwargs):
            pass

        def get_notification(self):
            return None

    class MockLspClient:
        def __init__(self, *args, **kwargs):
            pass

        def initialize(self, **kwargs):
            return {"capabilities": {}}

        def initialized(self, *args, **kwargs):
            pass

        def shutdown(self):
            pass

        def exit(self):
            pass

        def didOpen(self, **kwargs):
            pass

        def didChange(self, **kwargs):
            pass

        def completion(self, **kwargs):
            # Return some mock completion items
            return [
                {
                    "label": "mock_function",
                    "kind": 3,
                    "detail": "Mock function",
                    "documentation": {
                        "kind": "markdown",
                        "value": "This is a mock function",
                    },
                },
                {
                    "label": "mock_variable",
                    "kind": 6,
                    "detail": "Mock variable",
                    "documentation": "A mock variable",
                },
                {
                    "label": "mock_class",
                    "kind": 7,
                    "detail": "Mock class",
                    "documentation": {"kind": "markdown", "value": "A mock class"},
                },
            ]

        def hover(self, **kwargs):
            # Return mock hover information
            return {
                "contents": {
                    "kind": "markdown",
                    "value": "**Mock Documentation**\n\nThis is mock hover information provided when pylspclient is not available.",
                }
            }

    # Replace the actual classes with our mocks
    pylspclient = type("", (), {})
    pylspclient.JsonRpcEndpoint = MockJsonRpcEndpoint
    pylspclient.LspClient = MockLspClient


# Define LSP struct classes since pylspclient.lsp_structs is not available
class CompletionItem:
    def __init__(
        self,
        label,
        kind=None,
        detail=None,
        documentation=None,
        insertText=None,
        textEdit=None,
    ):
        self.label = label
        self.kind = kind
        self.detail = detail
        self.documentation = documentation
        self.insertText = insertText
        self.textEdit = textEdit


class Range:
    def __init__(self, start, end):
        self.start = start
        self.end = end


class Position:
    def __init__(self, line, character):
        self.line = line
        self.character = character


class TextEdit:
    def __init__(self, range, newText):
        self.range = range
        self.newText = newText


class MarkupContent:
    def __init__(self, kind, value):
        self.kind = kind
        self.value = value


class MarkupKind:
    PlainText = "plaintext"
    Markdown = "markdown"


class Hover:
    def __init__(self, contents=None, range=None):
        self.contents = contents
        self.range = range


# Constants
DEFAULT_FONT_FAMILY = "Consolas, 'Courier New', monospace"
DEFAULT_FONT_SIZE = 10
COMPLETION_TRIGGER_CHARS = [".", "(", "[", "{", ",", " "]
HOVER_DELAY_MS = 500  # Delay before showing hover tooltip


class LineNumberArea(QWidget):
    """Widget for displaying line numbers in the editor."""

    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.editor.paint_line_numbers(event)


class CompletionPopup(QListWidget):
    """Popup widget for displaying completion suggestions."""

    item_selected = Signal(CompletionItem)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setFrameStyle(QFrame.StyledPanel)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Store completion items
        self.completion_items: List[CompletionItem] = []

        # Connect signals
        self.itemClicked.connect(self.on_item_clicked)

    def set_completion_items(self, items: List[CompletionItem]):
        """Set the completion items to display."""
        self.completion_items = items
        self.clear()

        for item in items:
            list_item = QListWidgetItem(item.label)
            # Set tooltip with documentation if available
            if hasattr(item, "documentation") and item.documentation:
                if isinstance(item.documentation, MarkupContent):
                    list_item.setToolTip(item.documentation.value)
                else:
                    list_item.setToolTip(str(item.documentation))
            self.addItem(list_item)

        # Select first item
        if self.count() > 0:
            self.setCurrentRow(0)

    def on_item_clicked(self, item):
        """Handle item click event."""
        index = self.row(item)
        if 0 <= index < len(self.completion_items):
            self.item_selected.emit(self.completion_items[index])

    def keyPressEvent(self, event):
        """Handle key press events."""
        key = event.key()
        if key == Qt.Key_Escape:
            self.hide()
            event.accept()
        elif key in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Tab):
            current_row = self.currentRow()
            if 0 <= current_row < len(self.completion_items):
                self.item_selected.emit(self.completion_items[current_row])
            self.hide()
            event.accept()
        else:
            super().keyPressEvent(event)


class HoverTooltip(QLabel):
    """Tooltip widget for displaying hover information."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)
        self.setFrameStyle(QFrame.StyledPanel)
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setWordWrap(True)
        self.setTextFormat(Qt.RichText)

        # Set maximum width
        self.setMaximumWidth(400)

    def set_hover_content(self, hover: Hover):
        """Set the hover content to display."""
        if hover.contents:
            if isinstance(hover.contents, MarkupContent):
                if hover.contents.kind == MarkupKind.Markdown:
                    # Simple markdown to HTML conversion for basic formatting
                    text = hover.contents.value
                    # Convert code blocks
                    text = text.replace("```", "<pre>")
                    # Convert bold
                    text = text.replace("**", "<b>")
                    # Convert italic
                    text = text.replace("*", "<i>")
                    self.setText(text)
                else:
                    self.setText(hover.contents.value)
            else:
                self.setText(str(hover.contents))
        else:
            self.setText("No information available")


class LSPClient(QObject):
    """LSP client for communicating with language servers."""

    # Signals for LSP events
    completion_response = Signal(list)  # List of CompletionItem
    hover_response = Signal(object)  # Hover object
    diagnostics_updated = Signal(list)  # List of Diagnostic objects

    def __init__(self, parent=None):
        super().__init__(parent)
        self.server_process = None
        self.json_rpc_endpoint = None
        self.lsp_client = None
        self.lsp_endpoint = None
        self.server_capabilities = None
        self.initialized = False
        self.document_version = 0
        self.root_uri = None
        self.document_uri = None
        self.notification_thread = None

    def start_server(self):
        """Start the language server process."""
        try:
            print("DEBUG: Starting language server process...")
            # Start python-lsp-server process with simpler approach
            # Based on examples from other implementations
            self.server_process = subprocess.Popen(
                ["pylsp"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=0,  # No buffering to ensure immediate communication
            )
            print("DEBUG: Server process started")

            print("DEBUG: Creating JSON-RPC endpoint...")
            # Create JSON-RPC endpoint using binary streams
            self.json_rpc_endpoint = pylspclient.JsonRpcEndpoint(
                self.server_process.stdin,
                self.server_process.stdout,
            )
            print("DEBUG: JSON-RPC endpoint created")

            print("DEBUG: Creating LSP endpoint...")
            # Create LSP endpoint with increased timeout
            self.lsp_endpoint = pylspclient.LspEndpoint(
                self.json_rpc_endpoint, timeout=30  # Longer timeout for initialization
            )
            print("DEBUG: LSP endpoint created")

            print("DEBUG: Creating LSP client...")
            # Create LSP client
            self.lsp_client = pylspclient.LspClient(self.lsp_endpoint)
            print("DEBUG: LSP client created")

            print("DEBUG: Initializing server...")
            # Initialize the server
            self._initialize_server()
            print("DEBUG: Server initialized")

            print("DEBUG: Creating notification thread...")
            # Start listening for notifications in a separate thread
            self.notification_thread = threading.Thread(
                target=self._handle_notifications, daemon=True
            )
            print("DEBUG: Starting notification thread...")
            self.notification_thread.start()
            print("DEBUG: Notification thread started")

            return True
        except Exception as e:
            print(f"Error starting language server: {e}")
            import traceback

            traceback.print_exc()
            self.stop_server()
            return False

    def stop_server(self):
        """Stop the language server process."""
        if self.lsp_client:
            try:
                self.lsp_client.shutdown()
                self.lsp_client.exit()
            except:
                pass

        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=1)
            except:
                if self.server_process:
                    self.server_process.kill()

        self.server_process = None
        self.json_rpc_endpoint = None
        self.lsp_client = None
        self.server_capabilities = None
        self.initialized = False

    def _initialize_server(self):
        """Initialize the language server."""
        # Set root URI to current directory
        self.root_uri = f"file://{os.path.abspath(os.getcwd())}"

        # Initialize request
        initialize_params = {
            "processId": os.getpid(),
            "rootUri": self.root_uri,
            "capabilities": {
                "textDocument": {
                    "completion": {
                        "dynamicRegistration": False,
                        "contextSupport": True,
                        "completionItem": {
                            "snippetSupport": False,
                            "documentationFormat": ["plaintext", "markdown"],
                        },
                    },
                    "hover": {
                        "dynamicRegistration": False,
                        "contentFormat": ["plaintext", "markdown"],
                    },
                    "synchronization": {
                        "dynamicRegistration": False,
                        "willSave": False,
                        "willSaveWaitUntil": False,
                        "didSave": True,
                    },
                },
                "workspace": {"workspaceFolders": True},
            },
            "workspaceFolders": [{"uri": self.root_uri, "name": "workspace"}],
        }

        # Send initialize request
        response = self.lsp_client.initialize(
            processId=initialize_params["processId"],
            rootPath=None,  # Not used in newer LSP versions
            rootUri=initialize_params["rootUri"],
            initializationOptions=None,
            capabilities=initialize_params["capabilities"],
            trace="off",
            workspaceFolders=initialize_params["workspaceFolders"],
        )
        self.server_capabilities = response.get("capabilities", {})

        # Send initialized notification
        self.lsp_client.initialized({})
        self.initialized = True

    def _handle_notifications(self):
        """Handle notifications from the language server."""
        while self.json_rpc_endpoint:
            try:
                notification = self.json_rpc_endpoint.get_notification()
                if notification:
                    method = notification.get("method")
                    params = notification.get("params")

                    if method == "textDocument/publishDiagnostics" and params:
                        # Handle diagnostics
                        diagnostics = params.get("diagnostics", [])
                        self.diagnostics_updated.emit(diagnostics)
            except:
                # If we get an exception, the server might have closed
                break

    def open_document(self, file_path: str, language_id: str, text: str):
        """Notify the server that a document has been opened."""
        if not self.initialized:
            return

        self.document_uri = f"file://{os.path.abspath(file_path)}"
        self.document_version = 1

        # Send textDocument/didOpen notification
        self.lsp_client.didOpen(
            textDocument={
                "uri": self.document_uri,
                "languageId": language_id,
                "version": self.document_version,
                "text": text,
            }
        )

    def update_document(self, text: str):
        """Notify the server that a document has been changed."""
        if not self.initialized or not self.document_uri:
            return

        self.document_version += 1

        # Send textDocument/didChange notification
        self.lsp_client.didChange(
            textDocument={
                "uri": self.document_uri,
                "version": self.document_version,
            },
            contentChanges=[{"text": text}],
        )

    def request_completion(self, position: Tuple[int, int], trigger_char: str = None):
        """Request completion items at the given position."""
        if not self.initialized or not self.document_uri:
            return

        # Create completion context
        context = {}
        if trigger_char:
            context = {
                "triggerKind": 2,  # TriggerCharacter
                "triggerCharacter": trigger_char,
            }
        else:
            context = {"triggerKind": 1}  # Invoked

        # Send completion request
        try:
            response = self.lsp_client.completion(
                textDocument={"uri": self.document_uri},
                position={"line": position[0], "character": position[1]},
                context=context,
            )

            # Process completion items
            completion_items = []
            raw_items = []

            if isinstance(response, dict) and "items" in response:
                raw_items = response["items"]
            elif isinstance(response, list):
                raw_items = response

            # Convert raw items to CompletionItem objects
            for item in raw_items:
                label = item.get("label", "")
                kind = item.get("kind")
                detail = item.get("detail")

                # Handle documentation
                documentation = None
                if "documentation" in item:
                    doc = item["documentation"]
                    if isinstance(doc, dict) and "kind" in doc and "value" in doc:
                        documentation = MarkupContent(doc["kind"], doc["value"])
                    else:
                        documentation = doc

                # Handle text edit
                text_edit = None
                if "textEdit" in item:
                    te = item["textEdit"]
                    if "range" in te and "newText" in te:
                        range_obj = te["range"]
                        start_pos = Position(
                            range_obj["start"]["line"], range_obj["start"]["character"]
                        )
                        end_pos = Position(
                            range_obj["end"]["line"], range_obj["end"]["character"]
                        )
                        text_edit = TextEdit(Range(start_pos, end_pos), te["newText"])

                # Create CompletionItem
                completion_item = CompletionItem(
                    label,
                    kind=kind,
                    detail=detail,
                    documentation=documentation,
                    insertText=item.get("insertText"),
                    textEdit=text_edit,
                )
                completion_items.append(completion_item)

            self.completion_response.emit(completion_items)
        except Exception as e:
            print(f"Error requesting completion: {e}")
            self.completion_response.emit([])

    def request_hover(self, position: Tuple[int, int]):
        """Request hover information at the given position."""
        if not self.initialized or not self.document_uri:
            return

        # Send hover request
        try:
            response = self.lsp_client.hover(
                textDocument={"uri": self.document_uri},
                position={"line": position[0], "character": position[1]},
            )

            # Convert response to Hover object
            hover_obj = None
            if response and isinstance(response, dict):
                contents = None

                # Handle contents
                if "contents" in response:
                    content_data = response["contents"]
                    if (
                        isinstance(content_data, dict)
                        and "kind" in content_data
                        and "value" in content_data
                    ):
                        # MarkupContent
                        contents = MarkupContent(
                            content_data["kind"], content_data["value"]
                        )
                    elif isinstance(content_data, str):
                        # Plain string
                        contents = content_data
                    elif isinstance(content_data, list) and len(content_data) > 0:
                        # Array of content items - use the first one
                        first_item = content_data[0]
                        if isinstance(first_item, dict) and "value" in first_item:
                            contents = first_item["value"]
                        elif isinstance(first_item, str):
                            contents = first_item

                # Handle range if present
                range_obj = None
                if "range" in response:
                    range_data = response["range"]
                    start_pos = Position(
                        range_data["start"]["line"], range_data["start"]["character"]
                    )
                    end_pos = Position(
                        range_data["end"]["line"], range_data["end"]["character"]
                    )
                    range_obj = Range(start_pos, end_pos)

                hover_obj = Hover(contents, range_obj)

            self.hover_response.emit(hover_obj)
        except Exception as e:
            print(f"Error requesting hover: {e}")
            self.hover_response.emit(None)


class TextEditorWithLSP(QPlainTextEdit):
    """Text editor with LSP integration."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Set up editor appearance
        self.setup_editor()

        # Set up line numbers
        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.update_line_number_area_width(0)

        # Set up LSP client
        self.lsp_client = LSPClient(self)
        self.lsp_client.completion_response.connect(self.handle_completion_response)
        self.lsp_client.hover_response.connect(self.handle_hover_response)
        self.lsp_client.diagnostics_updated.connect(self.handle_diagnostics)

        # Start LSP server
        self.lsp_client.start_server()

        # Set up completion popup
        self.completion_popup = CompletionPopup()
        self.completion_popup.item_selected.connect(self.apply_completion)

        # Set up hover tooltip
        self.hover_tooltip = HoverTooltip()

        # Track hover state
        self.hover_position = None
        self.hover_timer = QTimer(self)
        self.hover_timer.setSingleShot(True)
        self.hover_timer.timeout.connect(self.request_hover_info)

        # Track diagnostics
        self.diagnostics = []
        self.diagnostic_format = QTextCharFormat()
        self.diagnostic_format.setUnderlineStyle(QTextCharFormat.WaveUnderline)
        self.diagnostic_format.setUnderlineColor(QColor("#FF0000"))  # Red for errors

        # Set up temporary file for LSP
        self.current_file = None
        self.setup_temp_file()

    def request_hover_info(self):
        """Request hover information at the current hover position."""
        if self.hover_position:
            self.lsp_client.request_hover(self.hover_position)

    def handle_hover_response(self, hover):
        """Handle hover response from LSP."""
        if not hover:
            self.hover_tooltip.hide()
            return

        # Set hover content
        self.hover_tooltip.set_hover_content(hover)

        # Position tooltip near cursor
        cursor = self.textCursor()
        rect = self.cursorRect(cursor)
        pos = self.mapToGlobal(rect.topRight())

        # Show tooltip
        self.hover_tooltip.move(pos)
        self.hover_tooltip.adjustSize()
        self.hover_tooltip.show()

    def handle_diagnostics(self, diagnostics):
        """Handle diagnostics from LSP."""
        # Clear existing diagnostics
        cursor = QTextCursor(self.document())
        cursor.movePosition(QTextCursor.Start)
        cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
        cursor.setCharFormat(QTextCharFormat())  # Clear formatting

        # Store diagnostics
        self.diagnostics = diagnostics

        # Apply diagnostics
        for diagnostic in diagnostics:
            # Get diagnostic range
            start_line = diagnostic.get("range", {}).get("start", {}).get("line", 0)
            start_char = (
                diagnostic.get("range", {}).get("start", {}).get("character", 0)
            )
            end_line = diagnostic.get("range", {}).get("end", {}).get("line", 0)
            end_char = diagnostic.get("range", {}).get("end", {}).get("character", 0)

            # Get severity (1=Error, 2=Warning, 3=Info, 4=Hint)
            severity = diagnostic.get("severity", 1)

            # Create cursor at start position
            cursor = QTextCursor(self.document())
            cursor.movePosition(QTextCursor.Start)
            cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, start_line)
            cursor.movePosition(QTextCursor.Right, QTextCursor.MoveAnchor, start_char)

            # Select to end position
            if start_line == end_line:
                # Same line
                cursor.movePosition(
                    QTextCursor.Right, QTextCursor.KeepAnchor, end_char - start_char
                )
            else:
                # Multiple lines
                cursor.movePosition(
                    QTextCursor.Down, QTextCursor.KeepAnchor, end_line - start_line
                )
                cursor.movePosition(QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
                cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, end_char)

            # Apply formatting
            cursor.setCharFormat(self.diagnostic_format)

    def setup_editor(self):
        """Set up the editor appearance."""
        # Set font
        font = QFont(DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE)
        font.setFixedPitch(True)
        self.setFont(font)

        # Set tab width
        self.setTabStopDistance(QFontMetrics(font).horizontalAdvance(" ") * 4)

        # Set colors
        self.set_colors()

    def set_colors(self):
        """Set editor colors."""
        # Set background and text colors
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor("#1E1E1E"))
        palette.setColor(self.foregroundRole(), QColor("#D4D4D4"))
        self.setPalette(palette)

    def setup_temp_file(self):
        """Set up a temporary file for LSP."""
        # Create a temporary Python file
        temp_dir = Path.home() / ".lsp_editor_temp"
        temp_dir.mkdir(exist_ok=True)

        self.current_file = str(temp_dir / "temp_file.py")

        # Open the document in LSP
        self.lsp_client.open_document(self.current_file, "python", self.toPlainText())

        # Set some initial Python content
        initial_content = """# LSP-enabled editor example
import math
import os
import sys

def example_function(param1, param2):
    \"\"\"
    This is an example function with docstring.
    
    Args:
        param1: The first parameter
        param2: The second parameter
        
    Returns:
        The result of the computation
    \"\"\"
    result = param1 + param2
    return result

class ExampleClass:
    def __init__(self, value):
        self.value = value
        
    def get_value(self):
        return self.value
        
    def set_value(self, new_value):
        self.value = new_value

# Try typing below this line and use autocompletion
# Type 'math.' to see available methods
# Hover over functions or classes to see documentation

"""
        self.setPlainText(initial_content)
        self.lsp_client.update_document(initial_content)

    def line_number_area_width(self):
        """Calculate the width of the line number area."""
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1

        space = 3 + self.fontMetrics().horizontalAdvance("9") * digits
        return space

    def update_line_number_area_width(self, _):
        """Update the margin according to the line number area width."""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        """Update the line number area when the editor viewport scrolls."""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(
                0, rect.y(), self.line_number_area.width(), rect.height()
            )

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        """Handle resize events to adjust the line number area."""
        super().resizeEvent(event)

        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )

    def paint_line_numbers(self, event):
        """Paint line numbers in the line number area."""
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#1E1E1E"))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = round(
            self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        )
        bottom = top + round(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor("#6D6D6D"))
                painter.drawText(
                    0,
                    top,
                    self.line_number_area.width(),
                    self.fontMetrics().height(),
                    Qt.AlignRight,
                    number,
                )

            block = block.next()
            top = bottom
            bottom = top + round(self.blockBoundingRect(block).height())
            block_number += 1

    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press events."""
        # Check if completion popup is visible
        if self.completion_popup.isVisible():
            # Forward key events to completion popup
            if event.key() in (
                Qt.Key_Up,
                Qt.Key_Down,
                Qt.Key_Enter,
                Qt.Key_Return,
                Qt.Key_Tab,
                Qt.Key_Escape,
            ):
                self.completion_popup.keyPressEvent(event)
                return

        # Check for completion trigger
        if event.text() in COMPLETION_TRIGGER_CHARS:
            super().keyPressEvent(event)
            self.request_completion(event.text())
        elif event.key() == Qt.Key_Space and event.modifiers() & Qt.ControlModifier:
            # Ctrl+Space triggers completion
            self.request_completion()
        else:
            super().keyPressEvent(event)

        # Update document in LSP
        self.lsp_client.update_document(self.toPlainText())

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move events."""
        super().mouseMoveEvent(event)

        # Get position under cursor
        position = self.cursorForPosition(event.pos())
        line = position.blockNumber()
        character = position.positionInBlock()

        # Check if position changed
        new_position = (line, character)
        if new_position != self.hover_position:
            self.hover_position = new_position
            self.hover_timer.start(HOVER_DELAY_MS)

    def leaveEvent(self, event):
        """Handle mouse leave events."""
        super().leaveEvent(event)
        self.hover_timer.stop()
        self.hover_tooltip.hide()

    def request_completion(self, trigger_char=None):
        """Request completion at the current cursor position."""
        cursor = self.textCursor()
        line = cursor.blockNumber()
        character = cursor.positionInBlock()

        self.lsp_client.request_completion((line, character), trigger_char)

    def handle_completion_response(self, items):
        """Handle completion response from LSP."""
        if not items:
            self.completion_popup.hide()
            return

        # Set completion items
        self.completion_popup.set_completion_items(items)

        # Position popup below current cursor position
        cursor = self.textCursor()
        rect = self.cursorRect(cursor)
        pos = self.mapToGlobal(rect.bottomLeft())

        # Adjust position to ensure popup is visible
        screen_rect = QApplication.primaryScreen().availableGeometry()
        popup_width = min(400, screen_rect.width() // 3)
        popup_height = min(300, screen_rect.height() // 3)

        if pos.x() + popup_width > screen_rect.right():
            pos.setX(screen_rect.right() - popup_width)
        if pos.y() + popup_height > screen_rect.bottom():
            pos.setY(rect.top() - popup_height)

        # Show popup
        self.completion_popup.setFixedWidth(popup_width)
        self.completion_popup.setFixedHeight(popup_height)
        self.completion_popup.move(pos)
        self.completion_popup.show()

    def apply_completion(self, item: CompletionItem):
        """Apply the selected completion item."""
        # Get current cursor position
        cursor = self.textCursor()

        # If we have a text edit, use it
        if hasattr(item, "textEdit") and item.textEdit:
            # Get range from text edit
            start_line = item.textEdit.range.start.line
            start_char = item.textEdit.range.start.character
            end_line = item.textEdit.range.end.line
            end_char = item.textEdit.range.end.character

            # Create new cursor at start position
            start_cursor = QTextCursor(self.document())
            start_cursor.movePosition(QTextCursor.Start)
            start_cursor.movePosition(
                QTextCursor.Down, QTextCursor.MoveAnchor, start_line
            )
            start_cursor.movePosition(
                QTextCursor.Right, QTextCursor.MoveAnchor, start_char
            )

            # Create new cursor at end position
            end_cursor = QTextCursor(self.document())
            end_cursor.movePosition(QTextCursor.Start)
            end_cursor.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, end_line)
            end_cursor.movePosition(QTextCursor.Right, QTextCursor.MoveAnchor, end_char)

            # Select text between start and end
            cursor.setPosition(start_cursor.position())
            cursor.setPosition(end_cursor.position(), QTextCursor.KeepAnchor)

            # Replace selected text
            cursor.insertText(item.textEdit.newText)


class MainWindow(QMainWindow):
    """Main window for the LSP-enabled text editor."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("LSP-Enabled Text Editor")
        self.resize(800, 600)

        # Create editor
        self.editor = TextEditorWithLSP()

        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(
            "LSP server started. Try typing 'math.' to see completions or hover over functions."
        )

        # Set central widget
        self.setCentralWidget(self.editor)

    def closeEvent(self, event):
        """Handle window close event."""
        # Stop LSP server
        if hasattr(self.editor, "lsp_client"):
            self.editor.lsp_client.stop_server()
        event.accept()


def main():
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

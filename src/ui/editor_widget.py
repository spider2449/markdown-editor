"""
Editor Widget - Markdown text editor with syntax highlighting
"""

from PySide6.QtWidgets import QTextEdit, QWidget, QVBoxLayout, QHBoxLayout, QApplication
from PySide6.QtCore import Signal, QTimer, Qt
from PySide6.QtGui import QKeyEvent, QFont, QPainter, QColor, QTextCursor
from .syntax_highlighter import MarkdownHighlighter
from .line_number_widget import LineNumberWidget
from .find_replace_dialog import FindReplaceDialog
from .editor_themes import EditorThemeManager


class CustomTextEdit(QTextEdit):
    """Custom QTextEdit that handles image paste detection and advanced features"""
    paste_requested = Signal()
    find_requested = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.line_number_widget = None
        self.current_line_highlight = True
        
    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press events"""
        # Handle Ctrl+V for image paste
        if event.key() == Qt.Key_V and event.modifiers() == Qt.ControlModifier:
            # Check if clipboard contains an image
            clipboard = QApplication.clipboard()
            if clipboard.mimeData().hasImage():
                print("CustomTextEdit: Ctrl+V detected with image in clipboard, emitting paste_requested signal")
                self.paste_requested.emit()
                return  # Don't call super() to prevent default paste behavior
            else:
                print("CustomTextEdit: Ctrl+V detected but no image in clipboard, allowing normal paste")
                # Allow normal text paste by calling super()
        
        # Handle Ctrl+F for find
        elif event.key() == Qt.Key_F and event.modifiers() == Qt.ControlModifier:
            self.find_requested.emit()
            return
        
        # Handle Ctrl+H for find and replace
        elif event.key() == Qt.Key_H and event.modifiers() == Qt.ControlModifier:
            self.find_requested.emit()
            return
        
        super().keyPressEvent(event)
    
    def set_line_number_widget(self, widget):
        """Set the line number widget"""
        self.line_number_widget = widget
    
    def resizeEvent(self, event):
        """Handle resize events to update line number widget"""
        super().resizeEvent(event)
        if self.line_number_widget:
            cr = self.contentsRect()
            self.line_number_widget.setGeometry(
                cr.left(), cr.top(), 
                self.line_number_widget.width(), cr.height()
            )
    
    def paintEvent(self, event):
        """Paint event with current line highlighting"""
        super().paintEvent(event)
        
        if self.current_line_highlight:
            self.highlight_current_line()
    
    def highlight_current_line(self):
        """Highlight the current line"""
        if not self.isReadOnly():
            selection = QTextCursor(self.textCursor())
            selection.clearSelection()
            
            # Create a selection for the entire line
            selection.select(QTextCursor.LineUnderCursor)
            
            # Apply highlighting (this is handled by the theme manager)


class EditorWidget(QWidget):
    text_changed = Signal(str)  # Emits markdown content
    paste_requested = Signal()  # Emits when Ctrl+V is pressed
    scroll_changed = Signal(float)  # Emits scroll position (0.0 to 1.0)
    
    def __init__(self):
        super().__init__()
        self.theme_manager = EditorThemeManager()
        self.find_replace_dialog = None
        self.line_numbers_enabled = True
        self.setup_ui()
        self.setup_timer()
        self.apply_current_theme()
    
    def setup_ui(self):
        """Setup the editor UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create horizontal layout for editor and line numbers
        editor_layout = QHBoxLayout()
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(0)
        
        # Create text editor
        self.text_edit = CustomTextEdit()
        self.text_edit.setAcceptRichText(False)  # Plain text only
        
        # Create line number widget
        self.line_number_widget = LineNumberWidget(self.text_edit)
        self.text_edit.set_line_number_widget(self.line_number_widget)
        
        # Set font
        font = QFont("Consolas", 12)
        font.setStyleHint(QFont.Monospace)
        self.text_edit.setFont(font)
        
        # Setup syntax highlighter
        self.highlighter = MarkdownHighlighter(self.text_edit.document(), self.theme_manager)
        
        # Connect signals
        self.text_edit.textChanged.connect(self._on_text_changed)
        self.text_edit.paste_requested.connect(self.paste_requested.emit)
        self.text_edit.find_requested.connect(self.show_find_replace)
        
        # Connect scroll bar signals
        scrollbar = self.text_edit.verticalScrollBar()
        scrollbar.valueChanged.connect(self._on_scroll_changed)
        
        # Add widgets to layout
        if self.line_numbers_enabled:
            editor_layout.addWidget(self.line_number_widget)
        editor_layout.addWidget(self.text_edit)
        
        # Create container widget for the editor layout
        editor_container = QWidget()
        editor_container.setLayout(editor_layout)
        
        layout.addWidget(editor_container)
    
    def setup_timer(self):
        """Setup debounced timer for text change events"""
        self.change_timer = QTimer()
        self.change_timer.setSingleShot(True)
        self.change_timer.timeout.connect(self._emit_text_changed)
        self.change_timer.setInterval(300)  # 300ms debounce
    
    def _on_text_changed(self):
        """Handle text change with debouncing"""
        self.change_timer.start()
    
    def _emit_text_changed(self):
        """Emit the text changed signal"""
        self.text_changed.emit(self.text_edit.toPlainText())
    
    def _on_scroll_changed(self, value):
        """Handle scroll position changes"""
        scrollbar = self.text_edit.verticalScrollBar()
        if scrollbar.maximum() > 0:
            # Calculate scroll position as percentage (0.0 to 1.0)
            scroll_percentage = value / scrollbar.maximum()
            self.scroll_changed.emit(scroll_percentage)
    

    
    def set_content(self, content: str):
        """Set the editor content"""
        self.text_edit.setPlainText(content)
    
    def get_content(self) -> str:
        """Get the editor content"""
        return self.text_edit.toPlainText()
    
    def insert_text(self, text: str):
        """Insert text at current cursor position"""
        cursor = self.text_edit.textCursor()
        cursor.insertText(text)
        self.text_edit.setTextCursor(cursor)
    
    def focus(self):
        """Set focus to the text editor"""
        self.text_edit.setFocus()
    
    def show_find_replace(self):
        """Show find and replace dialog"""
        if not self.find_replace_dialog:
            self.find_replace_dialog = FindReplaceDialog(self.text_edit, self)
        
        # Get selected text to pre-fill search
        cursor = self.text_edit.textCursor()
        selected_text = cursor.selectedText() if cursor.hasSelection() else ""
        
        self.find_replace_dialog.show_and_focus(selected_text)
    
    def toggle_line_numbers(self):
        """Toggle line number display"""
        self.line_numbers_enabled = not self.line_numbers_enabled
        
        if self.line_numbers_enabled:
            self.line_number_widget.show()
        else:
            self.line_number_widget.hide()
    
    def set_line_numbers_enabled(self, enabled: bool):
        """Enable or disable line numbers"""
        self.line_numbers_enabled = enabled
        self.toggle_line_numbers() if self.line_numbers_enabled != enabled else None
    
    def get_theme_manager(self):
        """Get the theme manager"""
        return self.theme_manager
    
    def set_theme(self, theme_name: str):
        """Set editor theme"""
        self.theme_manager.set_current_theme(theme_name)
        self.apply_current_theme()
    
    def apply_current_theme(self):
        """Apply current theme to editor"""
        self.theme_manager.apply_theme_to_editor(self.text_edit, self.line_number_widget)
        
        # Update syntax highlighter colors
        if hasattr(self.highlighter, 'update_theme'):
            self.highlighter.update_theme(self.theme_manager)
    
    def get_available_themes(self):
        """Get list of available theme names"""
        return self.theme_manager.get_theme_names()
    
    def get_current_theme(self):
        """Get current theme name"""
        return self.theme_manager.current_theme_name
    
    def set_font_size(self, size: int):
        """Set editor font size"""
        current_theme = self.theme_manager.get_current_theme()
        current_theme.font_size = size
        self.apply_current_theme()
    
    def set_font_family(self, family: str):
        """Set editor font family"""
        current_theme = self.theme_manager.get_current_theme()
        current_theme.font_family = family
        self.apply_current_theme()
    
    def zoom_in(self):
        """Increase font size"""
        current_theme = self.theme_manager.get_current_theme()
        current_theme.font_size = min(current_theme.font_size + 1, 24)
        self.apply_current_theme()
    
    def zoom_out(self):
        """Decrease font size"""
        current_theme = self.theme_manager.get_current_theme()
        current_theme.font_size = max(current_theme.font_size - 1, 8)
        self.apply_current_theme()
    
    def reset_zoom(self):
        """Reset font size to default"""
        current_theme = self.theme_manager.get_current_theme()
        current_theme.font_size = 12
        self.apply_current_theme()
    
    def insert_table(self, rows: int = 3, cols: int = 3):
        """Insert a markdown table at cursor position"""
        if rows < 1 or cols < 1:
            return
        
        # Create table header
        header_cells = ["Header"] * cols
        header_row = "| " + " | ".join(header_cells) + " |"
        
        # Create separator row
        separator_cells = ["---"] * cols
        separator_row = "| " + " | ".join(separator_cells) + " |"
        
        # Create data rows
        data_rows = []
        for i in range(rows - 1):  # -1 because header is already one row
            data_cells = ["Cell"] * cols
            data_row = "| " + " | ".join(data_cells) + " |"
            data_rows.append(data_row)
        
        # Combine all rows
        table_lines = [header_row, separator_row] + data_rows
        table_text = "\n".join(table_lines) + "\n\n"
        
        # Insert table at cursor position
        cursor = self.text_edit.textCursor()
        
        # If cursor is not at start of line, add newline before table
        if cursor.columnNumber() > 0:
            table_text = "\n" + table_text
        
        cursor.insertText(table_text)
        self.text_edit.setTextCursor(cursor)
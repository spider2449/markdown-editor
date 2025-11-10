"""
Find and Replace Dialog - Advanced search functionality for the editor
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, 
                               QPushButton, QCheckBox, QLabel, QTextEdit,
                               QMessageBox, QFrame)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QTextCursor, QTextDocument


class FindReplaceDialog(QDialog):
    """Dialog for find and replace functionality"""
    
    def __init__(self, text_edit: QTextEdit, parent=None):
        super().__init__(parent)
        self.text_edit = text_edit
        self.last_search_position = 0
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle("Find and Replace")
        self.setModal(False)  # Allow interaction with main window
        self.resize(400, 200)
        
        layout = QVBoxLayout(self)
        
        # Find section
        find_layout = QHBoxLayout()
        find_layout.addWidget(QLabel("Find:"))
        self.find_input = QLineEdit()
        self.find_input.setPlaceholderText("Enter text to find...")
        find_layout.addWidget(self.find_input)
        layout.addLayout(find_layout)
        
        # Replace section
        replace_layout = QHBoxLayout()
        replace_layout.addWidget(QLabel("Replace:"))
        self.replace_input = QLineEdit()
        self.replace_input.setPlaceholderText("Enter replacement text...")
        replace_layout.addWidget(self.replace_input)
        layout.addLayout(replace_layout)
        
        # Options section
        options_frame = QFrame()
        options_layout = QHBoxLayout(options_frame)
        
        self.case_sensitive_cb = QCheckBox("Case sensitive")
        self.whole_words_cb = QCheckBox("Whole words only")
        self.regex_cb = QCheckBox("Regular expressions")
        
        options_layout.addWidget(self.case_sensitive_cb)
        options_layout.addWidget(self.whole_words_cb)
        options_layout.addWidget(self.regex_cb)
        options_layout.addStretch()
        
        layout.addWidget(options_frame)
        
        # Buttons section
        buttons_layout = QHBoxLayout()
        
        self.find_next_btn = QPushButton("Find Next")
        self.find_prev_btn = QPushButton("Find Previous")
        self.replace_btn = QPushButton("Replace")
        self.replace_all_btn = QPushButton("Replace All")
        self.close_btn = QPushButton("Close")
        
        buttons_layout.addWidget(self.find_next_btn)
        buttons_layout.addWidget(self.find_prev_btn)
        buttons_layout.addWidget(self.replace_btn)
        buttons_layout.addWidget(self.replace_all_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.close_btn)
        
        layout.addLayout(buttons_layout)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #888888; font-size: 11px;")
        layout.addWidget(self.status_label)
    
    def setup_connections(self):
        """Setup signal connections"""
        self.find_next_btn.clicked.connect(self.find_next)
        self.find_prev_btn.clicked.connect(self.find_previous)
        self.replace_btn.clicked.connect(self.replace_current)
        self.replace_all_btn.clicked.connect(self.replace_all)
        self.close_btn.clicked.connect(self.close)
        
        # Enter key in find input triggers find next
        self.find_input.returnPressed.connect(self.find_next)
        self.replace_input.returnPressed.connect(self.replace_current)
        
        # Reset search position when search text changes
        self.find_input.textChanged.connect(self.reset_search_position)
    
    def reset_search_position(self):
        """Reset search position when search text changes"""
        self.last_search_position = 0
        self.status_label.setText("")
    
    def get_search_flags(self):
        """Get search flags based on options"""
        flags = QTextDocument.FindFlag(0)
        
        if self.case_sensitive_cb.isChecked():
            flags |= QTextDocument.FindCaseSensitively
        
        if self.whole_words_cb.isChecked():
            flags |= QTextDocument.FindWholeWords
        
        return flags
    
    def find_next(self):
        """Find next occurrence"""
        search_text = self.find_input.text()
        if not search_text:
            self.status_label.setText("Enter text to find")
            return
        
        cursor = self.text_edit.textCursor()
        
        # Start search from current position or last search position
        if cursor.hasSelection():
            cursor.setPosition(cursor.selectionEnd())
        else:
            cursor.setPosition(self.last_search_position)
        
        # Perform search
        flags = self.get_search_flags()
        found_cursor = self.text_edit.document().find(search_text, cursor, flags)
        
        if not found_cursor.isNull():
            self.text_edit.setTextCursor(found_cursor)
            self.last_search_position = found_cursor.selectionEnd()
            self.status_label.setText(f"Found: {search_text}")
        else:
            # Try from beginning if not found
            cursor.setPosition(0)
            found_cursor = self.text_edit.document().find(search_text, cursor, flags)
            
            if not found_cursor.isNull():
                self.text_edit.setTextCursor(found_cursor)
                self.last_search_position = found_cursor.selectionEnd()
                self.status_label.setText(f"Found: {search_text} (wrapped)")
            else:
                self.status_label.setText(f"Not found: {search_text}")
    
    def find_previous(self):
        """Find previous occurrence"""
        search_text = self.find_input.text()
        if not search_text:
            self.status_label.setText("Enter text to find")
            return
        
        cursor = self.text_edit.textCursor()
        
        # Start search from current position
        if cursor.hasSelection():
            cursor.setPosition(cursor.selectionStart())
        
        # Perform backward search
        flags = self.get_search_flags() | QTextDocument.FindBackward
        found_cursor = self.text_edit.document().find(search_text, cursor, flags)
        
        if not found_cursor.isNull():
            self.text_edit.setTextCursor(found_cursor)
            self.last_search_position = found_cursor.selectionStart()
            self.status_label.setText(f"Found: {search_text}")
        else:
            # Try from end if not found
            cursor.setPosition(self.text_edit.document().characterCount())
            found_cursor = self.text_edit.document().find(search_text, cursor, flags)
            
            if not found_cursor.isNull():
                self.text_edit.setTextCursor(found_cursor)
                self.last_search_position = found_cursor.selectionStart()
                self.status_label.setText(f"Found: {search_text} (wrapped)")
            else:
                self.status_label.setText(f"Not found: {search_text}")
    
    def replace_current(self):
        """Replace current selection"""
        search_text = self.find_input.text()
        replace_text = self.replace_input.text()
        
        if not search_text:
            self.status_label.setText("Enter text to find")
            return
        
        cursor = self.text_edit.textCursor()
        
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            
            # Check if selection matches search text
            if self.case_sensitive_cb.isChecked():
                matches = selected_text == search_text
            else:
                matches = selected_text.lower() == search_text.lower()
            
            if matches:
                cursor.insertText(replace_text)
                self.status_label.setText(f"Replaced: {search_text}")
                # Find next occurrence
                self.find_next()
            else:
                self.status_label.setText("Selection doesn't match search text")
        else:
            self.status_label.setText("No text selected")
    
    def replace_all(self):
        """Replace all occurrences"""
        search_text = self.find_input.text()
        replace_text = self.replace_input.text()
        
        if not search_text:
            self.status_label.setText("Enter text to find")
            return
        
        # Confirm replace all
        reply = QMessageBox.question(
            self, 
            "Replace All", 
            f"Replace all occurrences of '{search_text}' with '{replace_text}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Perform replace all
        cursor = QTextCursor(self.text_edit.document())
        cursor.setPosition(0)
        
        flags = self.get_search_flags()
        replacements = 0
        
        while True:
            found_cursor = self.text_edit.document().find(search_text, cursor, flags)
            if found_cursor.isNull():
                break
            
            found_cursor.insertText(replace_text)
            cursor = found_cursor
            replacements += 1
        
        if replacements > 0:
            self.status_label.setText(f"Replaced {replacements} occurrences")
        else:
            self.status_label.setText(f"Not found: {search_text}")
    
    def show_and_focus(self, search_text=""):
        """Show dialog and focus on find input"""
        if search_text:
            self.find_input.setText(search_text)
            self.find_input.selectAll()
        
        self.show()
        self.raise_()
        self.activateWindow()
        self.find_input.setFocus()
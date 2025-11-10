"""
Hotkey Dialog - Display all keyboard shortcuts
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget,
                               QTableWidgetItem, QPushButton, QLabel, QHeaderView,
                               QAbstractItemView, QTabWidget, QWidget)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class HotkeyDialog(QDialog):
    """Dialog to display all keyboard shortcuts"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle("Keyboard Shortcuts")
        self.setMinimumSize(700, 600)
        
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Keyboard Shortcuts Reference")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Create tab widget for categories
        self.tab_widget = QTabWidget()
        
        # Add tabs for different categories
        self.tab_widget.addTab(self._create_general_tab(), "General")
        self.tab_widget.addTab(self._create_editing_tab(), "Editing")
        self.tab_widget.addTab(self._create_formatting_tab(), "Formatting")
        self.tab_widget.addTab(self._create_view_tab(), "View")
        self.tab_widget.addTab(self._create_navigation_tab(), "Navigation")
        
        layout.addWidget(self.tab_widget)
        
        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        close_button.setDefault(True)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
    
    def _create_shortcut_table(self, shortcuts: list) -> QTableWidget:
        """Create a table widget with shortcuts"""
        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Shortcut", "Action"])
        table.setRowCount(len(shortcuts))
        
        # Configure table
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionMode(QAbstractItemView.NoSelection)
        table.setAlternatingRowColors(True)
        table.verticalHeader().setVisible(False)
        
        # Set column widths
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        
        # Populate table
        for row, (shortcut, action) in enumerate(shortcuts):
            # Shortcut column
            shortcut_item = QTableWidgetItem(shortcut)
            shortcut_font = QFont()
            shortcut_font.setBold(True)
            shortcut_item.setFont(shortcut_font)
            table.setItem(row, 0, shortcut_item)
            
            # Action column
            action_item = QTableWidgetItem(action)
            table.setItem(row, 1, action_item)
        
        return table
    
    def _create_general_tab(self) -> QWidget:
        """Create general shortcuts tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        shortcuts = [
            ("Ctrl+N", "New Document"),
            ("Ctrl+S", "Save Document"),
            ("Ctrl+Q", "Quit Application"),
            ("Ctrl+Shift+F", "Search All Documents"),
            ("Ctrl+E", "Focus Editor"),
        ]
        
        table = self._create_shortcut_table(shortcuts)
        layout.addWidget(table)
        
        return widget
    
    def _create_editing_tab(self) -> QWidget:
        """Create editing shortcuts tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        shortcuts = [
            ("Ctrl+F", "Find in Document"),
            ("Ctrl+H", "Find and Replace"),
            ("Ctrl+V", "Paste (or Paste Image)"),
            ("Ctrl+Shift+V", "Paste Image"),
            ("Ctrl+Z", "Undo"),
            ("Ctrl+Y", "Redo"),
            ("Ctrl+X", "Cut"),
            ("Ctrl+C", "Copy"),
            ("Ctrl+A", "Select All"),
        ]
        
        table = self._create_shortcut_table(shortcuts)
        layout.addWidget(table)
        
        return widget
    
    def _create_formatting_tab(self) -> QWidget:
        """Create formatting shortcuts tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        shortcuts = [
            ("Ctrl+B", "Bold"),
            ("Ctrl+I", "Italic"),
            ("Ctrl+Q", "Toggle Quote/Blockquote"),
            ("Ctrl+T", "Insert Table"),
        ]
        
        table = self._create_shortcut_table(shortcuts)
        layout.addWidget(table)
        
        # Add note
        note_label = QLabel("Note: Formatting shortcuts insert markdown syntax at cursor position.")
        note_label.setStyleSheet("color: #888888; font-size: 11px; padding: 5px;")
        note_label.setWordWrap(True)
        layout.addWidget(note_label)
        
        return widget
    
    def _create_view_tab(self) -> QWidget:
        """Create view shortcuts tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        shortcuts = [
            ("Ctrl+=", "Zoom In (increase font size)"),
            ("Ctrl++", "Zoom In (alternative)"),
            ("Ctrl+-", "Zoom Out (decrease font size)"),
            ("Ctrl+_", "Zoom Out (alternative)"),
            ("Ctrl+0", "Reset Zoom (default size)"),
            ("Ctrl+L", "Toggle Line Numbers"),
            ("Ctrl+P", "Print Preview"),
        ]
        
        table = self._create_shortcut_table(shortcuts)
        layout.addWidget(table)
        
        # Add note
        note_label = QLabel("Tip: For zoom in, Ctrl+= is easier than Ctrl++ (no Shift key needed).")
        note_label.setStyleSheet("color: #888888; font-size: 11px; padding: 5px;")
        note_label.setWordWrap(True)
        layout.addWidget(note_label)
        
        return widget
    
    def _create_navigation_tab(self) -> QWidget:
        """Create navigation shortcuts tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        shortcuts = [
            ("Click Outline Item", "Navigate to heading in document"),
            ("Double-click Document", "Rename document"),
            ("Right-click Document", "Show context menu (Rename/Delete)"),
            ("Double-click Result", "Open document from search results"),
        ]
        
        table = self._create_shortcut_table(shortcuts)
        layout.addWidget(table)
        
        # Add note
        note_label = QLabel("Navigation: Use the Outline tab to quickly jump to headings in your document.")
        note_label.setStyleSheet("color: #888888; font-size: 11px; padding: 5px;")
        note_label.setWordWrap(True)
        layout.addWidget(note_label)
        
        return widget
    
    @staticmethod
    def show_hotkeys(parent=None):
        """Static method to show the hotkey dialog"""
        dialog = HotkeyDialog(parent)
        dialog.exec()

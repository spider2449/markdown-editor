"""
Sidebar Widget - Document navigation and outline view
"""

import re
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, 
                               QTreeWidgetItem, QPushButton, QListWidget, 
                               QListWidgetItem, QTabWidget, QInputDialog, 
                               QMessageBox, QMenu, QLabel, QTableWidget,
                               QTableWidgetItem, QHeaderView, QAbstractItemView)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QAction
from core.document_manager import Document


class SidebarWidget(QWidget):
    document_selected = Signal(int)  # Emits document ID
    document_created = Signal(str)   # Emits document title
    document_deleted = Signal(int)   # Emits document ID
    document_renamed = Signal(int, str)  # Emits document ID and new title
    outline_item_clicked = Signal(str)  # Emits heading text
    
    def __init__(self):
        super().__init__()
        self.documents = []
        self.heading_data = []  # Store heading info for navigation
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the sidebar UI"""
        layout = QVBoxLayout(self)
        
        # Create tab widget for documents and outline
        self.tab_widget = QTabWidget()
        
        # Documents tab
        self.documents_widget = self._create_documents_tab()
        self.tab_widget.addTab(self.documents_widget, "Documents")
        
        # Outline tab
        self.outline_widget = self._create_outline_tab()
        self.tab_widget.addTab(self.outline_widget, "Outline")
        
        layout.addWidget(self.tab_widget)
    
    def _create_documents_tab(self) -> QWidget:
        """Create the documents tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Buttons and count label
        button_layout = QHBoxLayout()
        
        self.new_button = QPushButton("New")
        self.new_button.clicked.connect(self._create_new_document)
        
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self._delete_document)
        self.delete_button.setEnabled(False)
        
        button_layout.addWidget(self.new_button)
        button_layout.addWidget(self.delete_button)
        
        # Add document count label
        self.doc_count_label = QLabel("0 documents")
        self.doc_count_label.setStyleSheet("color: #888888; font-size: 11px; padding: 2px;")
        self.doc_count_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        button_layout.addWidget(self.doc_count_label)
        
        # Document table
        self.document_table = QTableWidget()
        self.document_table.setColumnCount(2)
        self.document_table.setHorizontalHeaderLabels(["#", "Document"])
        
        # Configure table appearance
        self.document_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.document_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.document_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.document_table.setAlternatingRowColors(True)
        self.document_table.verticalHeader().setVisible(False)
        
        # Set column widths
        header = self.document_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Index column
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Title column
        
        # Connect signals
        self.document_table.cellClicked.connect(self._on_document_cell_clicked)
        self.document_table.cellDoubleClicked.connect(self._on_document_cell_double_clicked)
        self.document_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.document_table.customContextMenuRequested.connect(self._show_context_menu)
        
        layout.addLayout(button_layout)
        layout.addWidget(self.document_table)
        
        return widget
    
    def _create_outline_tab(self) -> QWidget:
        """Create the outline tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Add heading count label
        self.heading_count_label = QLabel("0 headings")
        self.heading_count_label.setStyleSheet("color: #888888; font-size: 11px; padding: 2px;")
        self.heading_count_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(self.heading_count_label)
        
        self.outline_list = QListWidget()
        self.outline_list.itemClicked.connect(self._on_outline_item_clicked)
        layout.addWidget(self.outline_list)
        
        return widget
    
    def _on_outline_item_clicked(self, item: QListWidgetItem):
        """Handle outline item click"""
        # Get the heading text from item data
        heading_text = item.data(Qt.UserRole)
        if heading_text:
            self.outline_item_clicked.emit(heading_text)
    
    def _create_new_document(self):
        """Handle new document creation"""
        title, ok = QInputDialog.getText(self, "New Document", "Document title:")
        if ok and title.strip():
            self.document_created.emit(title.strip())
    
    def _delete_document(self):
        """Handle document deletion"""
        current_row = self.document_table.currentRow()
        if current_row >= 0:
            title_item = self.document_table.item(current_row, 1)
            if title_item:
                doc_id = title_item.data(Qt.UserRole)
                title = title_item.text()
                
                reply = QMessageBox.question(
                    self, "Delete Document", 
                    f"Are you sure you want to delete '{title}'?",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    self.document_deleted.emit(doc_id)
    
    def _on_document_cell_clicked(self, row: int, column: int):
        """Handle document cell click"""
        title_item = self.document_table.item(row, 1)
        if title_item:
            doc_id = title_item.data(Qt.UserRole)
            if doc_id:
                self.document_selected.emit(doc_id)
                self.delete_button.setEnabled(True)
    
    def _on_document_cell_double_clicked(self, row: int, column: int):
        """Handle document cell double-click for renaming"""
        self._rename_document(row)
    
    def _show_context_menu(self, position):
        """Show context menu for document table"""
        row = self.document_table.rowAt(position.y())
        if row >= 0:
            menu = QMenu(self)
            
            rename_action = QAction("Rename", self)
            rename_action.triggered.connect(lambda: self._rename_document(row))
            menu.addAction(rename_action)
            
            delete_action = QAction("Delete", self)
            delete_action.triggered.connect(lambda: self._delete_document_item(row))
            menu.addAction(delete_action)
            
            menu.exec(self.document_table.viewport().mapToGlobal(position))
    
    def _rename_document(self, row: int):
        """Handle document renaming"""
        if row < 0:
            return
            
        title_item = self.document_table.item(row, 1)
        if not title_item:
            return
            
        doc_id = title_item.data(Qt.UserRole)
        current_title = title_item.text()
        
        new_title, ok = QInputDialog.getText(
            self, "Rename Document", 
            "New title:", text=current_title
        )
        
        if ok and new_title.strip() and new_title.strip() != current_title:
            # Emit signal to update database
            self.document_renamed.emit(doc_id, new_title.strip())
    
    def _delete_document_item(self, row: int):
        """Delete a specific document item"""
        if row < 0:
            return
            
        title_item = self.document_table.item(row, 1)
        if not title_item:
            return
            
        doc_id = title_item.data(Qt.UserRole)
        title = title_item.text()
        
        reply = QMessageBox.question(
            self, "Delete Document", 
            f"Are you sure you want to delete '{title}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.document_deleted.emit(doc_id)
    
    def update_documents(self, documents: list[Document]):
        """Update the document table with numbered indices"""
        self.documents = documents
        self.document_table.setRowCount(0)
        
        for index, doc in enumerate(documents, start=1):
            row_position = self.document_table.rowCount()
            self.document_table.insertRow(row_position)
            
            # Index column
            index_item = QTableWidgetItem(str(index))
            index_item.setTextAlignment(Qt.AlignCenter)
            self.document_table.setItem(row_position, 0, index_item)
            
            # Title column
            title_item = QTableWidgetItem(doc.title)
            title_item.setData(Qt.UserRole, doc.id)
            self.document_table.setItem(row_position, 1, title_item)
        
        # Update document count label
        count = len(documents)
        if count == 1:
            self.doc_count_label.setText("1 document")
        else:
            self.doc_count_label.setText(f"{count} documents")
        
        # Select first document if available
        if documents:
            self.document_table.selectRow(0)
            self.delete_button.setEnabled(True)
        else:
            self.delete_button.setEnabled(False)
    
    def update_outline(self, markdown_content: str):
        """Update the outline from markdown content"""
        self.outline_list.clear()
        self.heading_data = []
        
        # Extract headers from markdown
        headers = re.findall(r'^(#{1,6})\s+(.+)$', markdown_content, re.MULTILINE)
        
        for level_str, title in headers:
            level = len(level_str)
            indent = "  " * (level - 1)
            item_text = f"{indent}{title}"
            
            item = QListWidgetItem(item_text)
            # Store the original heading text for navigation
            item.setData(Qt.UserRole, title.strip())
            self.outline_list.addItem(item)
            
            # Store heading data for reference
            self.heading_data.append({
                'level': level,
                'text': title.strip(),
                'display': item_text
            })
        
        # Update heading count label
        count = len(headers)
        if count == 1:
            self.heading_count_label.setText("1 heading")
        else:
            self.heading_count_label.setText(f"{count} headings")
    
    def select_document(self, doc_id: int):
        """Programmatically select a document"""
        for i in range(self.document_list.topLevelItemCount()):
            item = self.document_list.topLevelItem(i)
            if item.data(0, Qt.UserRole) == doc_id:
                self.document_list.setCurrentItem(item)
                self.delete_button.setEnabled(True)
                break
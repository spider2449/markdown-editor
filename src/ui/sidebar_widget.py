"""
Sidebar Widget - Document navigation and outline view
"""

import re
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, 
                               QTreeWidgetItem, QPushButton, QListWidget, 
                               QListWidgetItem, QTabWidget, QInputDialog, 
                               QMessageBox, QMenu)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QAction
from core.document_manager import Document


class SidebarWidget(QWidget):
    document_selected = Signal(int)  # Emits document ID
    document_created = Signal(str)   # Emits document title
    document_deleted = Signal(int)   # Emits document ID
    document_renamed = Signal(int, str)  # Emits document ID and new title
    
    def __init__(self):
        super().__init__()
        self.documents = []
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
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.new_button = QPushButton("New")
        self.new_button.clicked.connect(self._create_new_document)
        
        self.delete_button = QPushButton("Delete")
        self.delete_button.clicked.connect(self._delete_document)
        self.delete_button.setEnabled(False)
        
        button_layout.addWidget(self.new_button)
        button_layout.addWidget(self.delete_button)
        
        # Document list
        self.document_list = QTreeWidget()
        self.document_list.setHeaderHidden(True)
        self.document_list.itemClicked.connect(self._on_document_selected)
        self.document_list.itemDoubleClicked.connect(self._on_document_double_clicked)
        self.document_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.document_list.customContextMenuRequested.connect(self._show_context_menu)
        
        layout.addLayout(button_layout)
        layout.addWidget(self.document_list)
        
        return widget
    
    def _create_outline_tab(self) -> QWidget:
        """Create the outline tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.outline_list = QListWidget()
        layout.addWidget(self.outline_list)
        
        return widget
    
    def _create_new_document(self):
        """Handle new document creation"""
        title, ok = QInputDialog.getText(self, "New Document", "Document title:")
        if ok and title.strip():
            self.document_created.emit(title.strip())
    
    def _delete_document(self):
        """Handle document deletion"""
        current_item = self.document_list.currentItem()
        if current_item:
            doc_id = current_item.data(0, Qt.UserRole)
            title = current_item.text(0)
            
            reply = QMessageBox.question(
                self, "Delete Document", 
                f"Are you sure you want to delete '{title}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.document_deleted.emit(doc_id)
    
    def _on_document_selected(self, item: QTreeWidgetItem):
        """Handle document selection"""
        doc_id = item.data(0, Qt.UserRole)
        if doc_id:
            self.document_selected.emit(doc_id)
            self.delete_button.setEnabled(True)
    
    def _on_document_double_clicked(self, item: QTreeWidgetItem):
        """Handle document double-click for renaming"""
        self._rename_document(item)
    
    def _show_context_menu(self, position):
        """Show context menu for document list"""
        item = self.document_list.itemAt(position)
        if item:
            menu = QMenu(self)
            
            rename_action = QAction("Rename", self)
            rename_action.triggered.connect(lambda: self._rename_document(item))
            menu.addAction(rename_action)
            
            delete_action = QAction("Delete", self)
            delete_action.triggered.connect(lambda: self._delete_document_item(item))
            menu.addAction(delete_action)
            
            menu.exec(self.document_list.mapToGlobal(position))
    
    def _rename_document(self, item: QTreeWidgetItem):
        """Handle document renaming"""
        if not item:
            return
            
        doc_id = item.data(0, Qt.UserRole)
        current_title = item.text(0)
        
        new_title, ok = QInputDialog.getText(
            self, "Rename Document", 
            "New title:", text=current_title
        )
        
        if ok and new_title.strip() and new_title.strip() != current_title:
            # Update the item text immediately
            item.setText(0, new_title.strip())
            # Emit signal to update database
            self.document_renamed.emit(doc_id, new_title.strip())
    
    def _delete_document_item(self, item: QTreeWidgetItem):
        """Delete a specific document item"""
        doc_id = item.data(0, Qt.UserRole)
        title = item.text(0)
        
        reply = QMessageBox.question(
            self, "Delete Document", 
            f"Are you sure you want to delete '{title}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.document_deleted.emit(doc_id)
    
    def update_documents(self, documents: list[Document]):
        """Update the document list"""
        self.documents = documents
        self.document_list.clear()
        
        for doc in documents:
            item = QTreeWidgetItem([doc.title])
            item.setData(0, Qt.UserRole, doc.id)
            self.document_list.addTopLevelItem(item)
        
        # Select first document if available
        if documents:
            self.document_list.setCurrentItem(self.document_list.topLevelItem(0))
            self.delete_button.setEnabled(True)
        else:
            self.delete_button.setEnabled(False)
    
    def update_outline(self, markdown_content: str):
        """Update the outline from markdown content"""
        self.outline_list.clear()
        
        # Extract headers from markdown
        headers = re.findall(r'^(#{1,6})\s+(.+)$', markdown_content, re.MULTILINE)
        
        for level_str, title in headers:
            level = len(level_str)
            indent = "  " * (level - 1)
            item_text = f"{indent}{title}"
            
            item = QListWidgetItem(item_text)
            self.outline_list.addItem(item)
    
    def select_document(self, doc_id: int):
        """Programmatically select a document"""
        for i in range(self.document_list.topLevelItemCount()):
            item = self.document_list.topLevelItem(i)
            if item.data(0, Qt.UserRole) == doc_id:
                self.document_list.setCurrentItem(item)
                self.delete_button.setEnabled(True)
                break
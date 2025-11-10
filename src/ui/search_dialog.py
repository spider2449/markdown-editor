"""
Search Dialog - Global search across all documents
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, 
                               QPushButton, QTreeWidget, QTreeWidgetItem, 
                               QLabel, QCheckBox, QMessageBox)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont


class SearchDialog(QDialog):
    document_selected = Signal(int)  # Emits document ID to open
    
    def __init__(self, document_manager, parent=None):
        super().__init__(parent)
        self.document_manager = document_manager
        self.search_results = []
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the search dialog UI"""
        self.setWindowTitle("Search Documents")
        self.setMinimumSize(700, 500)
        
        layout = QVBoxLayout(self)
        
        # Search input area
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter search query...")
        self.search_input.returnPressed.connect(self.perform_search)
        search_layout.addWidget(self.search_input)
        
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.perform_search)
        search_layout.addWidget(self.search_button)
        
        layout.addLayout(search_layout)
        
        # Options
        options_layout = QHBoxLayout()
        
        self.case_sensitive_checkbox = QCheckBox("Case sensitive")
        options_layout.addWidget(self.case_sensitive_checkbox)
        
        options_layout.addStretch()
        
        self.result_label = QLabel("Enter a search query")
        options_layout.addWidget(self.result_label)
        
        layout.addLayout(options_layout)
        
        # Results tree
        self.results_tree = QTreeWidget()
        self.results_tree.setHeaderLabels(["Document", "Matches"])
        self.results_tree.setColumnWidth(0, 400)
        self.results_tree.itemDoubleClicked.connect(self.on_result_double_clicked)
        self.results_tree.setAlternatingRowColors(True)
        layout.addWidget(self.results_tree)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.open_button = QPushButton("Open Document")
        self.open_button.clicked.connect(self.open_selected_document)
        self.open_button.setEnabled(False)
        button_layout.addWidget(self.open_button)
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        # Connect tree selection
        self.results_tree.itemSelectionChanged.connect(self.on_selection_changed)
    
    def perform_search(self):
        """Perform the search"""
        query = self.search_input.text().strip()
        
        if not query:
            QMessageBox.warning(self, "Empty Query", "Please enter a search query.")
            return
        
        # Clear previous results
        self.results_tree.clear()
        self.search_results = []
        
        # Perform search
        case_sensitive = self.case_sensitive_checkbox.isChecked()
        results = self.document_manager.search_documents(query, case_sensitive)
        
        if not results:
            self.result_label.setText("No results found")
            self.open_button.setEnabled(False)
            return
        
        # Display results
        self.search_results = results
        self.result_label.setText(f"Found {len(results)} document(s)")
        
        for result in results:
            # Create parent item for document
            doc_item = QTreeWidgetItem([
                result['title'],
                f"{result['match_count']} match(es)"
            ])
            doc_item.setData(0, Qt.UserRole, result['id'])
            
            # Make document title bold
            font = doc_item.font(0)
            font.setBold(True)
            doc_item.setFont(0, font)
            
            self.results_tree.addTopLevelItem(doc_item)
            
            # Add title matches
            if result['title_matches']:
                title_match_item = QTreeWidgetItem(["Title match", ""])
                title_match_item.setForeground(0, Qt.gray)
                doc_item.addChild(title_match_item)
            
            # Add content matches with context
            for i, context in enumerate(result['content_matches'], 1):
                match_item = QTreeWidgetItem([context, ""])
                match_item.setData(0, Qt.UserRole, result['id'])
                
                # Highlight the query in the context
                match_item.setToolTip(0, context)
                
                doc_item.addChild(match_item)
            
            # Expand the first few results
            if len(self.search_results) <= 3:
                doc_item.setExpanded(True)
        
        # Select first result
        if self.results_tree.topLevelItemCount() > 0:
            self.results_tree.setCurrentItem(self.results_tree.topLevelItem(0))
    
    def on_selection_changed(self):
        """Handle selection change in results tree"""
        selected_items = self.results_tree.selectedItems()
        self.open_button.setEnabled(len(selected_items) > 0)
    
    def on_result_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle double-click on result item"""
        self.open_selected_document()
    
    def open_selected_document(self):
        """Open the selected document"""
        selected_items = self.results_tree.selectedItems()
        if not selected_items:
            return
        
        item = selected_items[0]
        
        # Get document ID from item or its parent
        doc_id = item.data(0, Qt.UserRole)
        if doc_id is None and item.parent():
            doc_id = item.parent().data(0, Qt.UserRole)
        
        if doc_id:
            self.document_selected.emit(doc_id)
            self.close()
    
    def show_and_focus(self, initial_query: str = ""):
        """Show dialog and focus search input"""
        if initial_query:
            self.search_input.setText(initial_query)
            self.perform_search()
        
        self.show()
        self.search_input.setFocus()
        self.search_input.selectAll()

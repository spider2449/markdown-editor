"""
Test script for document and heading count display
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QWidget, QSplitter, QPushButton, QVBoxLayout
from PySide6.QtCore import Qt, QTimer

# Add src to path
sys.path.insert(0, 'src')

from ui.sidebar_widget import SidebarWidget
from ui.editor_widget import EditorWidget
from core.document_manager import DocumentManager, Document


class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Document Count Test")
        self.setGeometry(100, 100, 1000, 700)
        
        # Create document manager
        self.doc_manager = DocumentManager(":memory:")
        
        # Create central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        
        # Create splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Create widgets
        self.sidebar = SidebarWidget()
        self.editor = EditorWidget()
        
        splitter.addWidget(self.sidebar)
        splitter.addWidget(self.editor)
        splitter.setSizes([250, 750])
        
        main_layout.addWidget(splitter)
        
        # Add test buttons
        button_layout = QHBoxLayout()
        
        add_doc_btn = QPushButton("Add Test Document")
        add_doc_btn.clicked.connect(self.add_test_document)
        button_layout.addWidget(add_doc_btn)
        
        add_multiple_btn = QPushButton("Add 5 Documents")
        add_multiple_btn.clicked.connect(self.add_multiple_documents)
        button_layout.addWidget(add_multiple_btn)
        
        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self.clear_all_documents)
        button_layout.addWidget(clear_btn)
        
        main_layout.addLayout(button_layout)
        
        # Connect signals
        self.sidebar.document_created.connect(self.create_document)
        self.sidebar.document_deleted.connect(self.delete_document)
        self.editor.text_changed.connect(self.update_outline)
        
        # Create initial test documents
        QTimer.singleShot(100, self.create_initial_documents)
        
        print("="*60)
        print("DOCUMENT TABLE VIEW TEST")
        print("="*60)
        print("\nFeatures to test:")
        print("1. Table view with separate # and Document columns")
        print("2. Document count in Documents tab (top right)")
        print("3. Numbered index in dedicated column (1, 2, 3, etc.)")
        print("4. Heading count in Outline tab (top right)")
        print("5. Indices update automatically when documents change")
        print("6. Alternating row colors for better readability")
        print("\nInstructions:")
        print("- Notice the table has two columns: # and Document")
        print("- Click 'Add Test Document' to add one document")
        print("- Click 'Add 5 Documents' to add multiple documents")
        print("- Click 'Clear All' to remove all documents")
        print("- Try renaming a document (double-click or right-click)")
        print("- Try deleting a document and watch indices reorder")
        print("- Edit the document to add/remove headings")
        print("- Notice how the # column stays narrow and centered")
        print("="*60)
    
    def create_initial_documents(self):
        """Create some initial test documents"""
        # Document 1
        self.doc_manager.create_document(
            "Welcome Document",
            """# Welcome to Markdown Editor

## Features
This editor has many great features.

### Document Management
Create, edit, and delete documents.

### Real-time Preview
See your markdown rendered instantly.
"""
        )
        
        # Document 2
        self.doc_manager.create_document(
            "Quick Notes",
            """# Quick Notes

## Todo
- Task 1
- Task 2

## Ideas
Some random ideas here.
"""
        )
        
        # Document 3
        self.doc_manager.create_document(
            "Simple Doc",
            "Just a simple document without many headings."
        )
        
        self.refresh_documents()
    
    def refresh_documents(self):
        """Refresh the document list"""
        documents = self.doc_manager.get_all_documents(load_content=False)
        self.sidebar.update_documents(documents)
        
        # Load first document if available
        if documents:
            doc = self.doc_manager.get_document(documents[0].id)
            if doc:
                self.editor.set_content(doc.content)
                self.sidebar.update_outline(doc.content)
    
    def add_test_document(self):
        """Add a single test document"""
        import random
        doc_num = random.randint(1000, 9999)
        
        content = f"""# Test Document {doc_num}

## Section 1
Some content here.

### Subsection 1.1
More details.

## Section 2
Another section.

### Subsection 2.1
Even more content.

#### Deep Section
Very nested.
"""
        
        self.doc_manager.create_document(f"Test Doc {doc_num}", content)
        self.refresh_documents()
        print(f"✓ Added Test Doc {doc_num}")
    
    def add_multiple_documents(self):
        """Add multiple test documents"""
        for i in range(5):
            import random
            doc_num = random.randint(1000, 9999)
            
            num_headings = random.randint(2, 6)
            content = f"# Document {doc_num}\n\n"
            
            for j in range(num_headings):
                content += f"## Heading {j+1}\n\nSome content for heading {j+1}.\n\n"
            
            self.doc_manager.create_document(f"Doc {doc_num}", content)
        
        self.refresh_documents()
        print("✓ Added 5 documents")
    
    def clear_all_documents(self):
        """Clear all documents"""
        documents = self.doc_manager.get_all_documents(load_content=False)
        for doc in documents:
            self.doc_manager.delete_document(doc.id)
        
        self.refresh_documents()
        self.editor.set_content("")
        self.sidebar.update_outline("")
        print("✓ Cleared all documents")
    
    def create_document(self, title: str):
        """Create a new document"""
        self.doc_manager.create_document(title, f"# {title}\n\n")
        self.refresh_documents()
    
    def delete_document(self, doc_id: int):
        """Delete a document"""
        self.doc_manager.delete_document(doc_id)
        self.refresh_documents()
    
    def update_outline(self, content: str):
        """Update outline when content changes"""
        self.sidebar.update_outline(content)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())

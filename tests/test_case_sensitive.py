"""
Test script to verify case-sensitive search functionality
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout

# Add src to path
sys.path.insert(0, 'src')

from ui.editor_widget import EditorWidget
from ui.search_dialog import SearchDialog
from core.document_manager import DocumentManager


class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Case Sensitive Test")
        self.setGeometry(100, 100, 900, 700)
        
        # Create document manager with test data
        self.doc_manager = DocumentManager(":memory:")
        self.create_test_documents()
        
        # Create central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Create editor
        self.editor = EditorWidget()
        layout.addWidget(self.editor)
        
        # Set test content
        test_text = """# Test Document

This is a test with Python and python.
PYTHON is also mentioned here.

The word Function and function appear multiple times.
FUNCTION is in uppercase.

JavaScript, javascript, and JAVASCRIPT are all different when case-sensitive.
"""
        self.editor.set_content(test_text)
        
        # Add buttons
        button_layout = QHBoxLayout()
        
        find_btn = QPushButton("Open Find/Replace (Ctrl+F)")
        find_btn.clicked.connect(self.editor.show_find_replace)
        button_layout.addWidget(find_btn)
        
        search_btn = QPushButton("Search All Documents (Ctrl+Shift+F)")
        search_btn.clicked.connect(self.show_search)
        button_layout.addWidget(search_btn)
        
        layout.addLayout(button_layout)
        
        print("="*60)
        print("CASE SENSITIVE TESTING")
        print("="*60)
        print("\nTest Instructions:")
        print("\n1. FIND/REPLACE DIALOG (Current Document):")
        print("   - Click 'Open Find/Replace' or press Ctrl+F")
        print("   - Try searching for 'python' without case-sensitive")
        print("     → Should find: Python, python, PYTHON")
        print("   - Enable 'Case sensitive' checkbox")
        print("   - Search for 'python' again")
        print("     → Should only find: python")
        print("   - Try 'Python' with case-sensitive")
        print("     → Should only find: Python")
        print("\n2. GLOBAL SEARCH (All Documents):")
        print("   - Click 'Search All Documents' or press Ctrl+Shift+F")
        print("   - Search for 'test' without case-sensitive")
        print("     → Should find matches in multiple documents")
        print("   - Enable 'Case sensitive' checkbox")
        print("   - Search for 'Test' with case-sensitive")
        print("     → Should only find exact case matches")
        print("\n3. OTHER OPTIONS:")
        print("   - Try 'Whole words only' in Find/Replace")
        print("   - Try 'Regular expressions' for advanced patterns")
        print("="*60)
    
    def create_test_documents(self):
        """Create test documents with various cases"""
        self.doc_manager.create_document(
            "Test Document 1",
            "This is a TEST document with test and Test words."
        )
        
        self.doc_manager.create_document(
            "Python Guide",
            "Python programming. python is great. PYTHON rocks!"
        )
        
        self.doc_manager.create_document(
            "JavaScript Tutorial",
            "JavaScript basics. javascript functions. JAVASCRIPT everywhere!"
        )
    
    def show_search(self):
        """Show global search dialog"""
        dialog = SearchDialog(self.doc_manager, self)
        dialog.show_and_focus()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())

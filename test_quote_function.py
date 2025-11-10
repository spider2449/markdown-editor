"""
Test script for quote function
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PySide6.QtCore import Qt

# Add src to path
sys.path.insert(0, 'src')

from ui.editor_widget import EditorWidget


class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quote Function Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Create editor
        self.editor = EditorWidget()
        layout.addWidget(self.editor)
        
        # Add test button
        btn = QPushButton("Toggle Quote (Ctrl+Q)")
        btn.clicked.connect(self.editor.toggle_quote)
        layout.addWidget(btn)
        
        # Set test content
        test_text = """This is a normal line
This is another line
This is a third line

> This is already quoted
> This is also quoted"""
        
        self.editor.set_content(test_text)
        
        print("Test Instructions:")
        print("1. Select some text and click the button or press Ctrl+Q")
        print("2. Try selecting already quoted text and toggle it")
        print("3. Try with no selection (should quote current line)")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())

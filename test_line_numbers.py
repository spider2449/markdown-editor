#!/usr/bin/env python3
"""
Test script for line number widget
"""

import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtCore import Qt

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ui.editor_widget import EditorWidget

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Line Number Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Create editor
        self.editor = EditorWidget()
        layout.addWidget(self.editor)
        
        # Set sample text with many lines
        sample_text = "\n".join([
            f"Line {i+1}: This is a test line with some content to see if line numbers align correctly."
            for i in range(100)
        ])
        
        self.editor.set_content(sample_text)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Line Number Test")
    
    window = TestWindow()
    window.show()
    
    print("\n=== Line Number Test ===")
    print("✓ Window created")
    print("✓ Editor with 100 lines loaded")
    print("\nTest:")
    print("  - Scroll up and down")
    print("  - Check if line numbers align with text")
    print("  - Add/remove lines")
    print("  - Check if line numbers update correctly")
    print("\nPress Ctrl+C to exit\n")
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()

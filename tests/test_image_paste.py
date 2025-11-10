#!/usr/bin/env python3
"""
Test script to verify image paste functionality
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QClipboard
from PySide6.QtWebEngineCore import QWebEngineUrlScheme
from ui.preview_widget import PreviewWidget
from core.document_manager import DocumentManager
from core.image_handler import ImageHandler


def main():
    # Register custom URL scheme BEFORE creating QApplication
    scheme = QWebEngineUrlScheme(b"image")
    scheme.setFlags(QWebEngineUrlScheme.SecureScheme | QWebEngineUrlScheme.LocalScheme)
    QWebEngineUrlScheme.registerScheme(scheme)
    
    app = QApplication(sys.argv)
    
    # Create test components
    doc_manager = DocumentManager()
    image_handler = ImageHandler(doc_manager)
    
    # Create a test document
    doc_id = doc_manager.create_document("Test Document", "# Test\n\nThis is a test document.\n\n")
    image_handler.set_current_document(doc_id)
    
    # Create test window
    window = QMainWindow()
    window.setWindowTitle("Image Paste Test")
    window.setGeometry(100, 100, 800, 600)
    
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)
    
    # Add preview widget
    preview = PreviewWidget(image_handler)
    layout.addWidget(preview)
    
    # Add test button
    test_button = QPushButton("Test Image Paste")
    layout.addWidget(test_button)
    
    status_label = QLabel("Ready - Copy an image to clipboard and click the button")
    layout.addWidget(status_label)
    
    def test_paste():
        try:
            if image_handler.handle_paste():
                status_label.setText("Image pasted successfully!")
                # Update preview with test content including the pasted image
                content = doc_manager.get_document(doc_id).content
                preview.update_content(content)
            else:
                status_label.setText("No image in clipboard")
        except Exception as e:
            status_label.setText(f"Error: {str(e)}")
    
    test_button.clicked.connect(test_paste)
    
    # Connect image handler signal
    def on_image_pasted(markdown_syntax):
        # Add the image to the document content
        current_doc = doc_manager.get_document(doc_id)
        new_content = current_doc.content + "\n\n" + markdown_syntax + "\n"
        doc_manager.update_document(doc_id, content=new_content)
        status_label.setText(f"Image added: {markdown_syntax}")
    
    image_handler.image_pasted.connect(on_image_pasted)
    
    # Set initial content
    preview.update_content("# Test Document\n\nThis is a test document.\n\nPaste an image to test the functionality.")
    
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
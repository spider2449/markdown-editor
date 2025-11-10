#!/usr/bin/env python3
"""
Debug script to test image paste functionality step by step
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QTextEdit
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
    import os
    os.makedirs("tests/doc", exist_ok=True)
    doc_manager = DocumentManager("tests/doc/debug_image_paste.db")
    image_handler = ImageHandler(doc_manager)
    
    # Create a test document
    doc_id = doc_manager.create_document("Test Document", "# Test Document\n\nThis is a test.\n\n")
    image_handler.set_current_document(doc_id)
    
    # Create test window
    window = QMainWindow()
    window.setWindowTitle("Debug Image Paste")
    window.setGeometry(100, 100, 1000, 700)
    
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)
    
    # Add text editor to show markdown
    text_edit = QTextEdit()
    text_edit.setPlainText("# Test Document\n\nThis is a test.\n\n")
    text_edit.setMaximumHeight(150)
    layout.addWidget(text_edit)
    
    # Add preview widget
    preview = PreviewWidget(image_handler)
    layout.addWidget(preview)
    
    # Add test buttons
    button_layout = QVBoxLayout()
    
    test_button = QPushButton("Test Image Paste (Ctrl+V)")
    button_layout.addWidget(test_button)
    
    create_test_image_button = QPushButton("Create Test Image in Clipboard")
    button_layout.addWidget(create_test_image_button)
    
    status_label = QLabel("Ready - Click 'Create Test Image' then 'Test Image Paste'")
    button_layout.addWidget(status_label)
    
    layout.addLayout(button_layout)
    
    def create_test_image():
        """Create a simple test image and put it in clipboard"""
        try:
            # Create a simple colored pixmap
            pixmap = QPixmap(200, 100)
            pixmap.fill(Qt.blue)
            
            # Put it in clipboard
            clipboard = QApplication.clipboard()
            clipboard.setPixmap(pixmap)
            
            status_label.setText("Test image created and copied to clipboard")
            print("Created test image in clipboard")
        except Exception as e:
            status_label.setText(f"Error creating test image: {e}")
            print(f"Error creating test image: {e}")
    
    def test_paste():
        """Test the paste functionality"""
        try:
            print("=== Starting paste test ===")
            if image_handler.handle_paste():
                status_label.setText("Image pasted successfully!")
                # Update preview with current document content
                current_doc = doc_manager.get_document(doc_id)
                if current_doc:
                    text_edit.setPlainText(current_doc.content)
                    preview.update_content(current_doc.content)
                    print("Updated preview with new content")
            else:
                status_label.setText("No image in clipboard or paste failed")
        except Exception as e:
            status_label.setText(f"Error: {str(e)}")
            print(f"Error in test_paste: {e}")
    
    def on_image_pasted(markdown_syntax):
        """Handle image pasted signal"""
        print(f"=== Image pasted signal received: {markdown_syntax} ===")
        try:
            # Add the image to the document content
            current_doc = doc_manager.get_document(doc_id)
            if current_doc:
                new_content = current_doc.content + "\n\n" + markdown_syntax + "\n"
                doc_manager.update_document(doc_id, content=new_content)
                print(f"Updated document content with image")
                
                # Update UI
                text_edit.setPlainText(new_content)
                preview.update_content(new_content)
                status_label.setText(f"Image added: {markdown_syntax}")
        except Exception as e:
            print(f"Error in on_image_pasted: {e}")
            status_label.setText(f"Error updating document: {e}")
    
    # Connect signals
    test_button.clicked.connect(test_paste)
    create_test_image_button.clicked.connect(create_test_image)
    image_handler.image_pasted.connect(on_image_pasted)
    
    # Set initial preview content
    preview.update_content("# Test Document\n\nThis is a test.\n\n")
    
    window.show()
    
    print("Debug window opened. Use the buttons to test image paste functionality.")
    print("1. Click 'Create Test Image in Clipboard'")
    print("2. Click 'Test Image Paste'")
    print("3. Check if image appears in preview")
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
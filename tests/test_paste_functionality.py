#!/usr/bin/env python3
"""
Test script to verify both text and image paste functionality
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QTextEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWebEngineCore import QWebEngineUrlScheme
from ui.editor_widget import EditorWidget
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
    doc_manager = DocumentManager("tests/doc/test_paste.db")
    image_handler = ImageHandler(doc_manager)
    
    # Create a test document
    doc_id = doc_manager.create_document("Paste Test", "# Paste Test\n\nTest both text and image pasting:\n\n")
    image_handler.set_current_document(doc_id)
    
    # Create test window
    window = QMainWindow()
    window.setWindowTitle("Paste Functionality Test")
    window.setGeometry(100, 100, 1200, 800)
    
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)
    
    # Add editor widget
    editor = EditorWidget()
    editor.set_content("# Paste Test\n\nTest both text and image pasting:\n\n")
    layout.addWidget(editor)
    
    # Add preview widget
    preview = PreviewWidget(image_handler)
    layout.addWidget(preview)
    
    # Add test buttons
    button_layout = QVBoxLayout()
    
    copy_text_button = QPushButton("Copy Test Text to Clipboard")
    button_layout.addWidget(copy_text_button)
    
    copy_image_button = QPushButton("Copy Test Image to Clipboard")
    button_layout.addWidget(copy_image_button)
    
    status_label = QLabel("Ready - Copy text or image, then paste with Ctrl+V in the editor")
    button_layout.addWidget(status_label)
    
    layout.addLayout(button_layout)
    
    def copy_test_text():
        """Copy test text to clipboard"""
        clipboard = QApplication.clipboard()
        clipboard.setText("This is test text that should paste normally!")
        status_label.setText("Test text copied to clipboard - now try Ctrl+V in editor")
    
    def copy_test_image():
        """Copy test image to clipboard"""
        # Create a simple colored pixmap
        pixmap = QPixmap(200, 100)
        pixmap.fill(Qt.red)
        
        clipboard = QApplication.clipboard()
        clipboard.setPixmap(pixmap)
        status_label.setText("Test image copied to clipboard - now try Ctrl+V in editor")
    
    def on_editor_text_changed(content):
        """Update preview when editor content changes"""
        preview.update_content(content)
        # Update document
        doc_manager.update_document(doc_id, content=content)
    
    def on_paste_requested():
        """Handle paste request from editor"""
        print("=== Paste requested from editor ===")
        if image_handler.handle_paste():
            status_label.setText("Image pasted successfully!")
        else:
            status_label.setText("Paste request handled but no image found")
    
    def on_image_pasted(markdown_syntax):
        """Handle image pasted signal"""
        print(f"=== Image pasted signal: {markdown_syntax} ===")
        status_label.setText(f"Image inserted: {markdown_syntax}")
    
    # Connect signals
    copy_text_button.clicked.connect(copy_test_text)
    copy_image_button.clicked.connect(copy_test_image)
    editor.text_changed.connect(on_editor_text_changed)
    editor.paste_requested.connect(on_paste_requested)
    image_handler.image_pasted.connect(on_image_pasted)
    
    # Set initial preview content
    preview.update_content("# Paste Test\n\nTest both text and image pasting:\n\n")
    
    window.show()
    
    print("Test window opened.")
    print("1. Click 'Copy Test Text' then Ctrl+V in editor (should paste text)")
    print("2. Click 'Copy Test Image' then Ctrl+V in editor (should paste image)")
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
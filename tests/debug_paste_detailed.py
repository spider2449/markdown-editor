#!/usr/bin/env python3
"""
Detailed debug script to trace image paste functionality
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
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
    doc_manager = DocumentManager("tests/doc/debug_paste_detailed.db")
    image_handler = ImageHandler(doc_manager)
    
    # Create a test document
    doc_id = doc_manager.create_document("Debug Test", "# Debug Test\n\nTesting image paste:\n\n")
    image_handler.set_current_document(doc_id)
    
    # Create test window
    window = QMainWindow()
    window.setWindowTitle("Debug Image Paste")
    window.setGeometry(100, 100, 1200, 800)
    
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)
    
    # Add editor widget
    editor = EditorWidget()
    editor.set_content("# Debug Test\n\nTesting image paste:\n\n")
    layout.addWidget(editor)
    
    # Add preview widget
    preview = PreviewWidget(image_handler)
    layout.addWidget(preview)
    
    # Add test buttons
    button_layout = QVBoxLayout()
    
    create_image_button = QPushButton("1. Create Test Image in Clipboard")
    button_layout.addWidget(create_image_button)
    
    check_clipboard_button = QPushButton("2. Check Clipboard Contents")
    button_layout.addWidget(check_clipboard_button)
    
    manual_paste_button = QPushButton("3. Manual Paste Test")
    button_layout.addWidget(manual_paste_button)
    
    status_label = QLabel("Ready - Follow the numbered steps")
    button_layout.addWidget(status_label)
    
    layout.addLayout(button_layout)
    
    def create_test_image():
        """Create test image in clipboard"""
        try:
            pixmap = QPixmap(300, 200)
            pixmap.fill(Qt.green)
            
            clipboard = QApplication.clipboard()
            clipboard.setPixmap(pixmap)
            
            status_label.setText("✅ Test image created in clipboard - now try Ctrl+V in editor")
            print("=== Created test image in clipboard ===")
        except Exception as e:
            status_label.setText(f"❌ Error creating image: {e}")
            print(f"Error creating test image: {e}")
    
    def check_clipboard():
        """Check what's in clipboard"""
        try:
            clipboard = QApplication.clipboard()
            mime_data = clipboard.mimeData()
            
            print("=== Clipboard Contents ===")
            print(f"Has image: {mime_data.hasImage()}")
            print(f"Has text: {mime_data.hasText()}")
            print(f"Has HTML: {mime_data.hasHtml()}")
            print(f"Has URLs: {mime_data.hasUrls()}")
            print(f"Formats: {mime_data.formats()}")
            
            if mime_data.hasImage():
                pixmap = clipboard.pixmap()
                print(f"Pixmap size: {pixmap.width()}x{pixmap.height()}")
                print(f"Pixmap is null: {pixmap.isNull()}")
                status_label.setText(f"✅ Clipboard has image: {pixmap.width()}x{pixmap.height()}")
            else:
                status_label.setText("❌ No image in clipboard")
                
        except Exception as e:
            status_label.setText(f"❌ Error checking clipboard: {e}")
            print(f"Error checking clipboard: {e}")
    
    def manual_paste_test():
        """Manually trigger paste test"""
        try:
            print("=== Manual Paste Test ===")
            if image_handler.handle_paste():
                status_label.setText("✅ Manual paste successful!")
                # Update editor and preview
                current_doc = doc_manager.get_document(doc_id)
                if current_doc:
                    editor.set_content(current_doc.content)
                    preview.update_content(current_doc.content)
            else:
                status_label.setText("❌ Manual paste failed - no image found")
        except Exception as e:
            status_label.setText(f"❌ Manual paste error: {e}")
            print(f"Manual paste error: {e}")
    
    def on_editor_text_changed(content):
        """Update preview when editor content changes"""
        preview.update_content(content)
        doc_manager.update_document(doc_id, content=content)
    
    def on_paste_requested():
        """Handle paste request from editor"""
        print("=== Editor paste_requested signal received ===")
        try:
            if image_handler.handle_paste():
                status_label.setText("✅ Image paste from editor successful!")
            else:
                status_label.setText("❌ Image paste from editor failed")
        except Exception as e:
            status_label.setText(f"❌ Editor paste error: {e}")
            print(f"Editor paste error: {e}")
    
    def on_image_pasted(markdown_syntax):
        """Handle image pasted signal"""
        print(f"=== Image pasted signal received: {markdown_syntax} ===")
        status_label.setText(f"✅ Image inserted: {markdown_syntax}")
    
    # Connect signals
    create_image_button.clicked.connect(create_test_image)
    check_clipboard_button.clicked.connect(check_clipboard)
    manual_paste_button.clicked.connect(manual_paste_test)
    editor.text_changed.connect(on_editor_text_changed)
    editor.paste_requested.connect(on_paste_requested)
    image_handler.image_pasted.connect(on_image_pasted)
    
    # Set initial preview content
    preview.update_content("# Debug Test\n\nTesting image paste:\n\n")
    
    window.show()
    
    print("=== Debug Window Opened ===")
    print("Steps to test:")
    print("1. Click 'Create Test Image in Clipboard'")
    print("2. Click 'Check Clipboard Contents' to verify")
    print("3. Try Ctrl+V in the editor")
    print("4. Or click 'Manual Paste Test'")
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
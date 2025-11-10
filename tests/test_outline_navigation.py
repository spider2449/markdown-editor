"""
Test script for outline navigation
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QWidget, QSplitter
from PySide6.QtCore import Qt

# Add src to path
sys.path.insert(0, 'src')

from ui.sidebar_widget import SidebarWidget
from ui.editor_widget import EditorWidget
from ui.preview_widget_js import PreviewWidgetJS


class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Outline Navigation Test")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        
        # Create splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Create widgets
        self.sidebar = SidebarWidget()
        self.editor = EditorWidget()
        self.preview = PreviewWidgetJS()
        
        splitter.addWidget(self.sidebar)
        splitter.addWidget(self.editor)
        splitter.addWidget(self.preview)
        splitter.setSizes([240, 480, 480])
        
        layout.addWidget(splitter)
        
        # Connect signals
        self.sidebar.outline_item_clicked.connect(self.navigate_to_heading)
        self.editor.text_changed.connect(self.on_text_changed)
        
        # Set test content
        test_markdown = """# Main Title

This is the introduction paragraph.

## Section 1

Content for section 1.

### Subsection 1.1

More detailed content here.

### Subsection 1.2

Another subsection.

## Section 2

Content for section 2.

### Subsection 2.1

Details about subsection 2.1.

## Section 3

Final section content.

### Subsection 3.1

Last subsection.

#### Deep Heading 3.1.1

Very nested content.
"""
        
        self.editor.set_content(test_markdown)
        self.preview.update_content(test_markdown)
        self.sidebar.update_outline(test_markdown)
        
        # Switch to outline tab
        self.sidebar.tab_widget.setCurrentIndex(1)
        
        print("Test Instructions:")
        print("1. Look at the outline in the left sidebar")
        print("2. Click on any heading in the outline")
        print("3. Both editor and preview should scroll to that heading")
        print("4. The heading should be highlighted briefly")
    
    def on_text_changed(self, content):
        """Update preview and outline when text changes"""
        self.preview.update_content(content)
        self.sidebar.update_outline(content)
    
    def navigate_to_heading(self, heading_text):
        """Navigate to a specific heading"""
        print(f"Navigating to: {heading_text}")
        self.editor.scroll_to_heading(heading_text)
        self.preview.scroll_to_heading(heading_text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())

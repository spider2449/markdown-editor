#!/usr/bin/env python3
"""
Test script for JavaScript-based preview widget
"""

import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTextEdit, QSplitter
from PySide6.QtCore import Qt

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ui.preview_widget_js import PreviewWidgetJS

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JavaScript Preview Test")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Create splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Create editor
        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Type markdown here...")
        self.editor.textChanged.connect(self.on_text_changed)
        
        # Create preview
        self.preview = PreviewWidgetJS()
        
        # Add to splitter
        splitter.addWidget(self.editor)
        splitter.addWidget(self.preview)
        splitter.setSizes([600, 600])
        
        layout.addWidget(splitter)
        
        # Set sample markdown
        sample_markdown = """# JavaScript Preview Test

This is a test of the **JavaScript-based** preview implementation.

## Features

- Real-time markdown rendering
- Syntax highlighting
- Multiple themes
- Image support

## Code Example

```python
def hello_world():
    print("Hello, World!")
    return True
```

```javascript
function helloWorld() {
    console.log("Hello, World!");
    return true;
}
```

## Table Example

| Feature | Status |
|---------|--------|
| Markdown | ✓ |
| Highlighting | ✓ |
| Themes | ✓ |

## Blockquote

> This is a blockquote.
> It can span multiple lines.

## Links

Check out [marked.js](https://marked.js.org/) and [highlight.js](https://highlightjs.org/)!

---

**Note**: This preview uses JavaScript libraries for rendering.
"""
        
        self.editor.setPlainText(sample_markdown)
    
    def on_text_changed(self):
        """Handle editor text changes"""
        markdown = self.editor.toPlainText()
        self.preview.update_content(markdown)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("JS Preview Test")
    
    window = TestWindow()
    window.show()
    
    print("\n=== JavaScript Preview Test ===")
    print("✓ Window created")
    print("✓ Editor and preview initialized")
    print("\nTry:")
    print("  - Edit the markdown in the left pane")
    print("  - Watch the preview update in real-time")
    print("  - Test code highlighting with different languages")
    print("\nPress Ctrl+C to exit\n")
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()

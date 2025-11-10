"""
Test script for preview theme switching
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from PySide6.QtCore import QTimer

# Add src to path
sys.path.insert(0, 'src')

from ui.preview_widget_js import PreviewWidgetJS


class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Theme Switch Test")
        self.setGeometry(100, 100, 900, 700)
        
        # Create central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Create preview widget
        self.preview = PreviewWidgetJS()
        layout.addWidget(self.preview)
        
        # Add theme buttons
        button_layout = QHBoxLayout()
        
        dark_btn = QPushButton("Dark Theme")
        dark_btn.clicked.connect(lambda: self.change_theme('dark'))
        button_layout.addWidget(dark_btn)
        
        light_btn = QPushButton("Light Theme")
        light_btn.clicked.connect(lambda: self.change_theme('light'))
        button_layout.addWidget(light_btn)
        
        sepia_btn = QPushButton("Sepia Theme")
        sepia_btn.clicked.connect(lambda: self.change_theme('sepia'))
        button_layout.addWidget(sepia_btn)
        
        layout.addLayout(button_layout)
        
        # Set test content after a delay to ensure page is loaded
        QTimer.singleShot(1000, self.set_test_content)
        
        print("Test Instructions:")
        print("1. Wait for the preview to load")
        print("2. Click the theme buttons to switch themes")
        print("3. Observe the color changes in the preview")
    
    def set_test_content(self):
        test_markdown = """# Theme Test Document

This is a test document to verify theme switching.

## Features to Test

- **Bold text**
- *Italic text*
- `inline code`

### Code Block

```python
def hello_world():
    print("Hello, World!")
    return True
```

### Blockquote

> This is a blockquote.
> It should change color with the theme.

### Links

[This is a link](https://example.com)

### Table

| Header 1 | Header 2 | Header 3 |
|----------|----------|----------|
| Cell 1   | Cell 2   | Cell 3   |
| Cell 4   | Cell 5   | Cell 6   |

---

### List

1. First item
2. Second item
3. Third item

- Bullet point
- Another bullet
- Last bullet
"""
        self.preview.update_content(test_markdown)
        print("✓ Test content loaded")
    
    def change_theme(self, theme_name):
        print(f"Changing theme to: {theme_name}")
        self.preview.set_theme(theme_name)
        print(f"✓ Theme changed to {theme_name}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())

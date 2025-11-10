"""
Test script for zoom hotkey functionality
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QHBoxLayout
from PySide6.QtCore import Qt

# Add src to path
sys.path.insert(0, 'src')

from ui.editor_widget import EditorWidget


class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Zoom Hotkey Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Add info label
        info_layout = QHBoxLayout()
        info_label = QLabel("Current Font Size:")
        self.size_label = QLabel("12")
        self.size_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        info_layout.addWidget(info_label)
        info_layout.addWidget(self.size_label)
        info_layout.addStretch()
        layout.addLayout(info_layout)
        
        # Create editor
        self.editor = EditorWidget()
        layout.addWidget(self.editor)
        
        # Set test content
        test_text = """# Zoom Test Document

Try the following hotkeys:

## Zoom In
- **Ctrl++** (Ctrl and Plus)
- **Ctrl+=** (Ctrl and Equals)

## Zoom Out
- **Ctrl+-** (Ctrl and Minus)

## Reset Zoom
- **Ctrl+0** (Ctrl and Zero)

You should see the font size change in real-time.
The current font size is displayed at the top.

## Test Instructions
1. Press Ctrl++ or Ctrl+= to zoom in
2. Press Ctrl+- to zoom out
3. Press Ctrl+0 to reset to default (12)
4. Watch the font size label update
5. Notice the text getting larger/smaller
"""
        
        self.editor.set_content(test_text)
        
        # Connect to track font size changes
        self.editor.text_edit.textChanged.connect(self.update_font_size_display)
        
        # Initial display
        self.update_font_size_display()
        
        print("="*60)
        print("ZOOM HOTKEY TEST")
        print("="*60)
        print("\nHotkeys to test:")
        print("  ZOOM IN:")
        print("    • Ctrl+=  (Ctrl and Equals - recommended)")
        print("    • Ctrl++  (Ctrl and Plus - also works)")
        print("\n  ZOOM OUT:")
        print("    • Ctrl+-  (Ctrl and Minus - recommended)")
        print("    • Ctrl+_  (Ctrl and Underscore - also works)")
        print("\n  RESET ZOOM:")
        print("    • Ctrl+0  (Ctrl and Zero)")
        print("\nWhat to check:")
        print("  1. Font size label updates at the top")
        print("  2. Text in editor gets larger/smaller")
        print("  3. All hotkeys work correctly")
        print("  4. Font size range: 8 (min) to 24 (max)")
        print("\nHow it works:")
        print("  • Direct key handling in editor (most reliable)")
        print("  • Menu shortcuts as backup")
        print("  • No ambiguous shortcut conflicts")
        print("="*60)
    
    def update_font_size_display(self):
        """Update the font size display"""
        current_theme = self.editor.get_theme_manager().get_current_theme()
        font_size = current_theme.font_size
        self.size_label.setText(str(font_size))
        
        # Update color based on size
        if font_size < 12:
            self.size_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #ff6b6b;")
        elif font_size > 12:
            self.size_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #51cf66;")
        else:
            self.size_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #339af0;")
    
    def keyPressEvent(self, event):
        """Override to track key presses for debugging"""
        # Handle zoom shortcuts manually as fallback
        if event.modifiers() == Qt.ControlModifier:
            if event.key() in (Qt.Key_Plus, Qt.Key_Equal):
                print("✓ Detected: Ctrl++ or Ctrl+= → Zoom In")
                self.editor.zoom_in()
                self.update_font_size_display()
                return
            elif event.key() in (Qt.Key_Minus, Qt.Key_Underscore):
                print("✓ Detected: Ctrl+- or Ctrl+_ → Zoom Out")
                self.editor.zoom_out()
                self.update_font_size_display()
                return
            elif event.key() == Qt.Key_0:
                print("✓ Detected: Ctrl+0 → Reset Zoom")
                self.editor.reset_zoom()
                self.update_font_size_display()
                return
        
        super().keyPressEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())

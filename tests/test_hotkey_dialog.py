"""
Test script for hotkey dialog
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton

# Add src to path
sys.path.insert(0, 'src')

from ui.hotkey_dialog import HotkeyDialog


class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hotkey Dialog Test")
        self.setGeometry(100, 100, 400, 200)
        
        # Create central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Add button to show hotkeys
        show_button = QPushButton("Show Keyboard Shortcuts (F1)")
        show_button.clicked.connect(self.show_hotkeys)
        show_button.setStyleSheet("font-size: 14px; padding: 20px;")
        layout.addWidget(show_button)
        
        print("="*60)
        print("HOTKEY DIALOG TEST")
        print("="*60)
        print("\nInstructions:")
        print("1. Click the button or press F1 to show hotkeys")
        print("2. Browse through different tabs:")
        print("   • General - Basic application shortcuts")
        print("   • Editing - Text editing shortcuts")
        print("   • Formatting - Markdown formatting")
        print("   • View - Zoom and display options")
        print("   • Navigation - Document navigation")
        print("3. Check that all shortcuts are listed correctly")
        print("4. Notice the organized, tabbed layout")
        print("="*60)
    
    def show_hotkeys(self):
        """Show the hotkey dialog"""
        HotkeyDialog.show_hotkeys(self)
    
    def keyPressEvent(self, event):
        """Handle F1 key press"""
        if event.key() == 0x01000030:  # F1 key
            self.show_hotkeys()
        else:
            super().keyPressEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())

"""
Quick test to verify editor scrolling works when clicking outline headings
"""

import sys
from PySide6.QtWidgets import QApplication

# Add src to path
sys.path.insert(0, 'src')

from ui.main_window import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    print("\n" + "="*60)
    print("EDITOR SCROLL TEST")
    print("="*60)
    print("\nInstructions:")
    print("1. Select a document from the sidebar (or create a new one)")
    print("2. Add some markdown headings to the document:")
    print("   # Heading 1")
    print("   ## Heading 2")
    print("   ### Heading 3")
    print("3. Switch to the 'Outline' tab in the sidebar")
    print("4. Click on any heading in the outline")
    print("5. VERIFY: The editor should:")
    print("   - Scroll to the heading")
    print("   - Select/highlight the heading line")
    print("   - Focus on the editor")
    print("6. VERIFY: The preview should also scroll to the heading")
    print("="*60 + "\n")
    
    sys.exit(app.exec())

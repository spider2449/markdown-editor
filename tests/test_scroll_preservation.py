"""
Test scroll position preservation after content updates
"""

import sys
import time
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from ui.preview_widget import PreviewWidget

def test_scroll_preservation():
    """Test that scroll position is preserved after content updates"""
    app = QApplication(sys.argv)
    
    # Create preview widget
    preview = PreviewWidget()
    preview.show()
    preview.resize(800, 600)
    
    # Create a large document
    large_doc = []
    for i in range(50):
        large_doc.append(f"## Section {i}\n")
        large_doc.append(f"This is paragraph {i} with some content that makes the document scrollable.\n")
        large_doc.append(f"More content here to ensure we have enough height.\n\n")
    
    markdown_content = "\n".join(large_doc)
    
    print("Step 1: Loading initial content...")
    preview.update_content(markdown_content)
    
    # Wait for initial render
    app.processEvents()
    time.sleep(0.2)
    app.processEvents()
    
    print("Step 2: Scrolling to middle of document...")
    # Scroll to middle
    scroll_script = """
    (function() {
        var body = document.body;
        var html = document.documentElement;
        var height = Math.max(body.scrollHeight, body.offsetHeight, 
                             html.clientHeight, html.scrollHeight, html.offsetHeight);
        var scrollTop = (height - window.innerHeight) * 0.5;
        window.scrollTo(0, scrollTop);
        return window.pageYOffset || document.documentElement.scrollTop;
    })();
    """
    
    def on_scrolled(position):
        print(f"  Scrolled to position: {position}")
        
        # Wait a bit then modify content
        QTimer.singleShot(500, modify_content)
    
    def modify_content():
        print("\nStep 3: Modifying content (changing one section)...")
        modified_doc = markdown_content.replace("Section 25", "Section 25 MODIFIED")
        preview.update_content(modified_doc)
        
        # Wait for render
        QTimer.singleShot(300, check_scroll_position)
    
    def check_scroll_position():
        print("\nStep 4: Checking if scroll position was preserved...")
        check_script = """
        (function() {
            return window.pageYOffset || document.documentElement.scrollTop;
        })();
        """
        
        def on_position_checked(final_position):
            print(f"  Final scroll position: {final_position}")
            
            # Check if position is approximately the same
            if abs(final_position - preview._saved_scroll_position) < 50:
                print("\n✓ SUCCESS: Scroll position preserved!")
            else:
                print(f"\n✗ FAILED: Position changed from {preview._saved_scroll_position} to {final_position}")
            
            print(f"\nSaved position: {preview._saved_scroll_position}")
            print(f"Final position: {final_position}")
            print(f"Difference: {abs(final_position - preview._saved_scroll_position)} pixels")
            
            # Exit after a moment
            QTimer.singleShot(1000, app.quit)
        
        preview.web_view.page().runJavaScript(check_script, on_position_checked)
    
    preview.web_view.page().runJavaScript(scroll_script, on_scrolled)
    
    # Run the app
    sys.exit(app.exec())

if __name__ == "__main__":
    test_scroll_preservation()

"""
Test that scroll position is restored without visible flash/jump
"""

import sys
import time
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from ui.preview_widget import PreviewWidget

def test_no_scroll_flash():
    """Test that scroll position restoration happens without visible jump"""
    app = QApplication(sys.argv)
    
    # Create preview widget
    preview = PreviewWidget()
    preview.show()
    preview.resize(800, 600)
    
    # Create a large document
    large_doc = []
    for i in range(100):
        large_doc.append(f"## Section {i}\n")
        large_doc.append(f"This is paragraph {i} with content.\n")
        large_doc.append(f"More text to ensure scrollable height.\n\n")
    
    markdown_content = "\n".join(large_doc)
    
    print("=" * 60)
    print("Testing Scroll Position Preservation Without Flash")
    print("=" * 60)
    
    print("\n[1] Loading initial content...")
    preview.update_content(markdown_content)
    
    # Wait for initial render
    app.processEvents()
    time.sleep(0.2)
    app.processEvents()
    
    print("[2] Scrolling to position 800px...")
    # Scroll to specific position
    scroll_script = """
    (function() {
        window.scrollTo(0, 800);
        return window.pageYOffset || document.documentElement.scrollTop;
    })();
    """
    
    scroll_positions = []
    
    def on_scrolled(position):
        scroll_positions.append(("Initial scroll", position))
        print(f"    ✓ Scrolled to: {position}px")
        
        # Monitor scroll position during update
        QTimer.singleShot(100, monitor_before_update)
    
    def monitor_before_update():
        print("\n[3] Monitoring scroll position before update...")
        check_script = """
        (function() {
            return window.pageYOffset || document.documentElement.scrollTop;
        })();
        """
        
        def on_position_before(pos):
            scroll_positions.append(("Before update", pos))
            print(f"    Position before update: {pos}px")
            
            # Now modify content
            QTimer.singleShot(50, modify_content)
        
        preview.web_view.page().runJavaScript(check_script, on_position_before)
    
    def modify_content():
        print("\n[4] Modifying content...")
        modified_doc = markdown_content.replace("Section 50", "Section 50 MODIFIED")
        
        # Monitor immediately after setHtml call
        preview.update_content(modified_doc)
        
        print("    Content update triggered")
        print("    Inline script should restore position immediately")
        
        # Check position multiple times during load
        QTimer.singleShot(50, lambda: check_during_load(1))
        QTimer.singleShot(100, lambda: check_during_load(2))
        QTimer.singleShot(200, lambda: check_during_load(3))
        QTimer.singleShot(350, check_final_position)
    
    def check_during_load(check_num):
        check_script = """
        (function() {
            return window.pageYOffset || document.documentElement.scrollTop;
        })();
        """
        
        def on_position_during(pos):
            scroll_positions.append((f"During load #{check_num}", pos))
            print(f"    Position during load #{check_num}: {pos}px")
        
        preview.web_view.page().runJavaScript(check_script, on_position_during)
    
    def check_final_position():
        print("\n[5] Checking final position...")
        check_script = """
        (function() {
            return window.pageYOffset || document.documentElement.scrollTop;
        })();
        """
        
        def on_final_position(final_pos):
            scroll_positions.append(("Final position", final_pos))
            print(f"    Final position: {final_pos}px")
            
            # Analyze results
            QTimer.singleShot(100, analyze_results)
        
        preview.web_view.page().runJavaScript(check_script, on_final_position)
    
    def analyze_results():
        print("\n" + "=" * 60)
        print("ANALYSIS")
        print("=" * 60)
        
        print("\nScroll position timeline:")
        for label, pos in scroll_positions:
            print(f"  {label:25s}: {pos:6.1f}px")
        
        # Check if position ever went to 0 (flash to top)
        positions_during_load = [pos for label, pos in scroll_positions if "During load" in label]
        
        print("\n" + "-" * 60)
        if any(pos < 100 for pos in positions_during_load):
            print("⚠ WARNING: Scroll position dropped below 100px during load")
            print("  This indicates a visible flash/jump occurred")
        else:
            print("✓ SUCCESS: Scroll position remained stable during load")
            print("  No visible flash/jump detected")
        
        # Check final position accuracy
        initial_pos = scroll_positions[0][1]
        final_pos = scroll_positions[-1][1]
        difference = abs(final_pos - initial_pos)
        
        print(f"\nPosition accuracy:")
        print(f"  Initial: {initial_pos:.1f}px")
        print(f"  Final:   {final_pos:.1f}px")
        print(f"  Diff:    {difference:.1f}px")
        
        if difference < 10:
            print("  ✓ Excellent accuracy (< 10px difference)")
        elif difference < 50:
            print("  ✓ Good accuracy (< 50px difference)")
        else:
            print("  ✗ Poor accuracy (> 50px difference)")
        
        print("=" * 60)
        
        # Exit
        QTimer.singleShot(1000, app.quit)
    
    preview.web_view.page().runJavaScript(scroll_script, on_scrolled)
    
    # Run the app
    sys.exit(app.exec())

if __name__ == "__main__":
    test_no_scroll_flash()

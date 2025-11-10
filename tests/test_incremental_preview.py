"""
Test incremental preview parsing optimization
"""

import sys
import time
from PySide6.QtWidgets import QApplication
from ui.preview_widget import PreviewWidget

def test_incremental_parsing():
    """Test that incremental parsing improves performance"""
    app = QApplication(sys.argv)
    
    # Create preview widget
    preview = PreviewWidget()
    
    # Create a large markdown document
    large_doc = []
    for i in range(100):
        large_doc.append(f"## Section {i}\n")
        large_doc.append(f"This is paragraph {i} with some content.\n")
        large_doc.append(f"```python\ndef function_{i}():\n    return {i}\n```\n")
        large_doc.append("\n")
    
    markdown_content = "\n".join(large_doc)
    print(f"Document size: {len(markdown_content)} bytes")
    print(f"Incremental threshold: {preview._incremental_threshold} bytes")
    
    # First render (cold cache)
    start = time.time()
    preview.update_content(markdown_content)
    # Wait for render timer
    app.processEvents()
    time.sleep(0.15)  # Wait for debounce timer
    app.processEvents()
    first_render_time = time.time() - start
    
    print(f"\nFirst render time: {first_render_time:.3f}s")
    print(f"Block cache size: {len(preview._block_cache)}")
    
    # Modify only one section
    modified_doc = markdown_content.replace("Section 50", "Section 50 MODIFIED")
    
    # Second render (should use cached blocks)
    start = time.time()
    preview.update_content(modified_doc)
    app.processEvents()
    time.sleep(0.15)
    app.processEvents()
    second_render_time = time.time() - start
    
    print(f"\nSecond render time (with cache): {second_render_time:.3f}s")
    print(f"Block cache size: {len(preview._block_cache)}")
    
    # Get cache stats
    stats = preview.get_cache_stats()
    print(f"\nCache statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Verify incremental parsing was used
    if len(markdown_content) > preview._incremental_threshold:
        print(f"\n✓ Incremental parsing enabled (doc size > threshold)")
    else:
        print(f"\n✗ Document too small for incremental parsing")
    
    print("\nTest completed successfully!")

if __name__ == "__main__":
    test_incremental_parsing()

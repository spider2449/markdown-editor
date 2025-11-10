#!/usr/bin/env python3
"""
Test script for the Markdown Editor
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from PySide6.QtWidgets import QApplication
    from ui.main_window import MainWindow
    print("✓ All imports successful")
    
    # Test database initialization
    from core.document_manager import DocumentManager
    os.makedirs("tests/doc", exist_ok=True)
    dm = DocumentManager("tests/doc/test.db")  # Use file database for testing
    print("✓ Database initialization successful")
    
    # Test document operations
    doc_id = dm.create_document("Test Document", "# Hello World\n\nThis is a test.")
    doc = dm.get_document(doc_id)
    print(f"✓ Document operations successful: {doc.title}")
    
    print("\nAll tests passed! You can run the application with: python main.py")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Make sure to install dependencies: pip install -r requirements.txt")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
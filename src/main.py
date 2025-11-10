#!/usr/bin/env python3
"""
Markdown Editor - A PySide6-based markdown editor with real-time preview
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtWebEngineCore import QWebEngineUrlScheme

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow


def main():
    # Register custom URL scheme BEFORE creating QApplication
    scheme = QWebEngineUrlScheme(b"image")
    scheme.setFlags(QWebEngineUrlScheme.SecureScheme | QWebEngineUrlScheme.LocalScheme)
    QWebEngineUrlScheme.registerScheme(scheme)
    
    app = QApplication(sys.argv)
    app.setApplicationName("Markdown Editor")
    app.setApplicationVersion("1.0.0")
    
    # Set application style
    app.setStyle('Fusion')
    
    # Load and apply dark theme
    try:
        styles_path = os.path.join(os.path.dirname(__file__), 'resources', 'styles.qss')
        with open(styles_path, 'r') as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("Warning: styles.qss not found, using default theme")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
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
    # Register custom URL schemes BEFORE creating QApplication
    
    # Register image:// scheme for embedded images
    image_scheme = QWebEngineUrlScheme(b"image")
    image_scheme.setFlags(QWebEngineUrlScheme.SecureScheme | QWebEngineUrlScheme.LocalScheme)
    QWebEngineUrlScheme.registerScheme(image_scheme)
    
    # Register local:// scheme for local resources (JS/CSS files)
    local_scheme = QWebEngineUrlScheme(b"local")
    local_scheme.setFlags(QWebEngineUrlScheme.SecureScheme | 
                          QWebEngineUrlScheme.LocalScheme | 
                          QWebEngineUrlScheme.LocalAccessAllowed)
    QWebEngineUrlScheme.registerScheme(local_scheme)
    
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
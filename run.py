#!/usr/bin/env python3
"""
Convenience launcher for Markdown Editor
"""
import sys
import os

# Add src to path and run main
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import main

if __name__ == '__main__':
    main()

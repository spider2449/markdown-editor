# Product Overview

A desktop markdown editor with real-time preview and image management capabilities. Built for efficient document creation and editing with a three-pane layout (sidebar, editor, preview).

## Core Features

- Real-time markdown preview with syntax highlighting
- Direct image pasting from clipboard (Ctrl+V, Ctrl+Shift+V)
- SQLite-based document storage with embedded images
- Auto-save functionality (2-second delay)
- Document outline navigation
- Find and replace functionality
- Table insertion dialog
- Multiple editor and preview themes
- Performance optimization with caching and lazy loading

## Key Capabilities

- Handles large documents (>50KB) with progressive loading
- Image optimization and compression for storage efficiency
- LRU cache management for documents and images
- Session persistence (window state, last document, theme preferences)

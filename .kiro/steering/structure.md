# Project Structure

## Directory Layout

```
markdown_editor/
├── requirements.txt           # Python dependencies
├── documents.db              # SQLite database (auto-created)
├── settings.json             # User settings (auto-created)
├── src/                      # Source code
│   ├── main.py               # Application entry point
│   ├── core/                 # Core business logic
│   │   ├── document_manager.py   # SQLite operations, caching
│   │   ├── image_handler.py      # Image paste/storage
│   │   └── settings_manager.py   # Settings persistence
│   ├── ui/                   # UI components
│   │   ├── main_window.py        # Main window, menus, toolbar
│   │   ├── editor_widget.py      # Markdown editor
│   │   ├── preview_widget.py     # HTML preview panel (Python-based)
│   │   ├── preview_widget_js.py  # HTML preview panel (JavaScript-based)
│   │   ├── sidebar_widget.py     # Document list/outline
│   │   ├── syntax_highlighter.py # Markdown syntax highlighting
│   │   ├── line_number_widget.py # Line numbers for editor
│   │   ├── find_replace_dialog.py # Find/replace functionality
│   │   ├── table_dialog.py       # Table insertion dialog
│   │   └── editor_themes.py      # Editor theme definitions
│   └── resources/            # Static resources
│       ├── styles.qss            # Qt stylesheet (dark theme)
│       ├── preview_themes.py     # HTML preview themes (Python)
│       ├── preview_template.html # HTML template (JavaScript preview)
│       ├── preview_renderer.js   # JavaScript markdown renderer
│       └── js/                   # Downloaded JS libraries (optional)
│           ├── marked.min.js
│           ├── highlight.min.js
│           └── *.min.js          # Language packs
├── tests/                    # Test files
│   ├── test_app.py
│   ├── test_image_paste.py
│   ├── test_incremental_preview.py
│   ├── test_no_scroll_flash.py
│   ├── test_paste_functionality.py
│   ├── test_scroll_preservation.py
│   ├── debug_image_paste.py
│   └── debug_paste_detailed.py
├── build/                    # Build artifacts (generated)
├── dist/                     # Distribution artifacts (generated)
├── test_js_preview.py        # Test script for JavaScript preview
├── download_js_libs.py       # Download JS libraries for offline use
├── JAVASCRIPT_PREVIEW.md     # JavaScript preview documentation
└── JAVASCRIPT_PREVIEW_QUICKSTART.md  # Quick start guide
```

## Architecture Patterns

### Separation of Concerns

- **src/**: All source code
  - **core/**: Data management, business logic, no UI dependencies
  - **ui/**: UI components, Qt widgets, user interactions
  - **resources/**: Static assets, themes, stylesheets
- **tests/**: All test and debug files

### Component Communication

- **Signals/Slots**: Qt signal-slot pattern for component communication
- **Manager Pattern**: DocumentManager, ImageHandler, SettingsManager as central coordinators
- **Observer Pattern**: Editor changes trigger preview updates via signals

### Data Flow

1. User edits in EditorWidget
2. Signal emitted to MainWindow
3. MainWindow updates PreviewWidget and triggers auto-save
4. DocumentManager handles database operations with caching
5. ImageHandler manages clipboard images and storage

## Key Design Decisions

### Performance Optimization

- **Lazy Loading**: Documents >50KB load metadata first, content on demand
- **LRU Caching**: Document and image caches with automatic eviction
- **Debounced Rendering**: Preview updates batched with 100ms delay
- **Image Compression**: JPEG compression for large images (>500KB)

### Database Schema

- **documents**: id, title, content, created_at, updated_at
- **images**: id, document_id, filename, data (BLOB), created_at

### Custom URL Scheme

- Images referenced as `image://{image_id}` in markdown
- Custom QWebEngineUrlSchemeHandler resolves to database BLOBs
- JavaScript preview converts to data URLs for browser rendering

### Preview Implementation

The application uses **JavaScript-based preview (preview_widget_js.py)**:
- Uses marked.js for markdown parsing
- highlight.js for syntax highlighting
- Client-side rendering for better performance
- Requires internet for CDN resources (first load)
- Can be configured for offline use with `download_js_libs.py`

Note: The original Python-based preview (preview_widget.py) is kept for reference but not used.

# JavaScript Preview Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Markdown Editor Application                  │
└─────────────────────────────────────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
            ┌───────▼────────┐       ┌───────▼────────┐
            │  EditorWidget  │       │  SidebarWidget │
            │   (QTextEdit)  │       │   (QListView)  │
            └───────┬────────┘       └────────────────┘
                    │
                    │ textChanged signal
                    │
            ┌───────▼────────┐
            │  MainWindow    │
            │  (Controller)  │
            └───────┬────────┘
                    │
                    │ update_content()
                    │
        ┌───────────┴────────────┐
        │                        │
┌───────▼────────┐      ┌───────▼────────────┐
│ PreviewWidget  │      │ PreviewWidgetJS    │
│  (Python)      │      │  (JavaScript)      │
└────────────────┘      └───────┬────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
            ┌───────▼────────┐     ┌───────▼────────┐
            │ QWebEngineView │     │ Image Handler  │
            │   (Qt Widget)  │     │ (Data URLs)    │
            └───────┬────────┘     └────────────────┘
                    │
                    │ HTML + JavaScript
                    │
        ┌───────────▼───────────┐
        │  preview_template.html │
        └───────────┬───────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
┌───────▼────────┐     ┌───────▼────────┐
│   marked.js    │     │  highlight.js  │
│  (CDN/Local)   │     │  (CDN/Local)   │
└───────┬────────┘     └───────┬────────┘
        │                       │
        └───────────┬───────────┘
                    │
        ┌───────────▼───────────┐
        │ preview_renderer.js   │
        │  (Local JavaScript)   │
        └───────────┬───────────┘
                    │
                    │ Rendered HTML
                    │
            ┌───────▼────────┐
            │   Browser DOM  │
            │  (Chromium)    │
            └────────────────┘
```

## Data Flow

### Python Preview (Original)

```
User Types
    │
    ▼
EditorWidget.textChanged
    │
    ▼
MainWindow.on_text_changed()
    │
    ▼
PreviewWidget.update_content(markdown)
    │
    ├─► Python markdown.parse()
    │   └─► HTML string
    │
    ├─► Pygments.highlight()
    │   └─► Syntax highlighted HTML
    │
    ├─► PreviewThemes.get_theme()
    │   └─► CSS styles
    │
    └─► QWebEngineView.setHtml()
        └─► Browser renders HTML
```

### JavaScript Preview (New)

```
User Types
    │
    ▼
EditorWidget.textChanged
    │
    ▼
MainWindow.on_text_changed()
    │
    ▼
PreviewWidgetJS.update_content(markdown)
    │
    ├─► ImageHandler.process_images()
    │   └─► Convert image:// to data URLs
    │
    ├─► Escape for JavaScript
    │   └─► Safe string
    │
    └─► QWebEngineView.runJavaScript()
        │
        ▼
    JavaScript: markdownRenderer.updateContent()
        │
        ├─► Check cache
        │   ├─► Cache hit → Use cached HTML
        │   └─► Cache miss ↓
        │
        ├─► marked.parse(markdown)
        │   └─► HTML string
        │
        ├─► hljs.highlightElement()
        │   └─► Syntax highlighted code
        │
        ├─► Update DOM
        │   └─► document.getElementById('preview-content').innerHTML
        │
        └─► Restore scroll position
            └─► window.scrollTo()
```

## Component Interaction

### Python Side

```
┌─────────────────────────────────────────┐
│         PreviewWidgetJS                 │
├─────────────────────────────────────────┤
│                                         │
│  + __init__(image_handler)              │
│  + setup_ui()                           │
│  + update_content(markdown)             │
│  + set_theme(theme_name)                │
│  + sync_scroll(percentage)              │
│  + clear_cache()                        │
│  + print_preview()                      │
│                                         │
│  - _load_template()                     │
│  - _on_load_finished()                  │
│  - _process_pending_updates()           │
│  - _replace_image_urls()                │
│  - _apply_theme()                       │
│                                         │
└─────────────────────────────────────────┘
            │
            │ uses
            ▼
┌─────────────────────────────────────────┐
│      ResourceSchemeHandler              │
├─────────────────────────────────────────┤
│                                         │
│  + requestStarted(request)              │
│  - _detect_mime_type(path)              │
│                                         │
│  Handles: qrc:///filename.js            │
│                                         │
└─────────────────────────────────────────┘
```

### JavaScript Side

```
┌─────────────────────────────────────────┐
│     MarkdownPreviewRenderer             │
├─────────────────────────────────────────┤
│                                         │
│  + constructor()                        │
│  + updateContent(markdown)              │
│  + parseMarkdown(markdown)              │
│  + setTheme(themeName)                  │
│  + syncScroll(percentage)               │
│  + clearCache()                         │
│  + getCacheStats()                      │
│                                         │
│  - setupMessageHandler()                │
│  - highlightCodeBlocks()                │
│  - saveScrollPosition()                 │
│  - restoreScrollPosition()              │
│  - generateCacheKey(markdown)           │
│  - cacheContent(key, html)              │
│                                         │
│  Properties:                            │
│  - currentTheme                         │
│  - scrollPosition                       │
│  - contentCache (Map)                   │
│  - cacheHits, cacheMisses               │
│                                         │
└─────────────────────────────────────────┘
```

## File Structure

```
markdown_editor/
│
├── src/
│   ├── ui/
│   │   ├── preview_widget.py          ← Python implementation
│   │   └── preview_widget_js.py       ← JavaScript implementation
│   │
│   └── resources/
│       ├── preview_themes.py          ← Python themes
│       ├── preview_template.html      ← HTML template
│       ├── preview_renderer.js        ← JavaScript renderer
│       └── js/                        ← Downloaded libraries (optional)
│           ├── marked.min.js
│           ├── highlight.min.js
│           └── *.min.js
│
├── switch_preview.py                  ← Switch implementations
├── test_js_preview.py                 ← Test application
└── download_js_libs.py                ← Download for offline
```

## Communication Flow

### Python → JavaScript

```python
# Python sends markdown to JavaScript
script = f"""
if (window.markdownRenderer) {{
    window.markdownRenderer.updateContent(`{escaped_markdown}`);
}}
"""
web_view.page().runJavaScript(script)
```

### JavaScript → Python (Future)

```javascript
// JavaScript can send messages back (not implemented yet)
if (typeof qt !== 'undefined' && qt.webChannelTransport) {
    // Use Qt WebChannel
    qt.webChannelTransport.send({
        action: 'scrollChanged',
        position: window.pageYOffset
    });
}
```

## Caching Strategy

### Python Preview

```
┌─────────────────────────────────────┐
│         HTML Cache (LRU)            │
├─────────────────────────────────────┤
│                                     │
│  Key: hash(markdown + theme)        │
│  Value: Complete HTML document      │
│  Size: 200 entries                  │
│  Eviction: LRU (25% at a time)      │
│                                     │
└─────────────────────────────────────┘
```

### JavaScript Preview

```
┌─────────────────────────────────────┐
│      Content Cache (Map)            │
├─────────────────────────────────────┤
│                                     │
│  Key: hash(markdown + theme)        │
│  Value: Parsed HTML content         │
│  Size: 200 entries                  │
│  Eviction: FIFO (oldest first)      │
│                                     │
└─────────────────────────────────────┘
```

## Theme System

### Theme Application

```
User selects theme
    │
    ▼
MainWindow.on_theme_changed()
    │
    ▼
PreviewWidgetJS.set_theme('dark')
    │
    ├─► Update highlight.js theme
    │   └─► Change CSS link href
    │
    ├─► Update body class
    │   └─► document.body.className = 'theme-dark'
    │
    └─► Trigger content refresh
        └─► Re-render with new theme
```

### Theme CSS

```css
/* Base styles (all themes) */
body { font-family: ...; }
h1 { font-size: 2em; }

/* Dark theme */
body.theme-dark {
    color: #d4d4d4;
    background-color: #1e1e1e;
}

/* Light theme */
body.theme-light {
    color: #24292e;
    background-color: #ffffff;
}

/* Sepia theme */
body.theme-sepia {
    color: #5c4b37;
    background-color: #f4f1ea;
}
```

## Performance Optimizations

### Debouncing

```
User types: "H" "e" "l" "l" "o"
    │    │    │    │    │
    ▼    ▼    ▼    ▼    ▼
[Queue: "H", "e", "l", "l", "o"]
    │
    │ Wait 100ms
    │
    ▼
Process only: "Hello" (latest)
```

### Scroll Preservation

```
Before Update:
    │
    ├─► Save scroll position
    │   └─► scrollPosition = window.pageYOffset
    │
Update Content:
    │
    ├─► Update DOM
    │   └─► container.innerHTML = newHTML
    │
After Update:
    │
    └─► Restore scroll position
        └─► window.scrollTo(0, scrollPosition)
```

## Error Handling

```
┌─────────────────────────────────────┐
│         Error Scenarios             │
├─────────────────────────────────────┤
│                                     │
│  1. CDN libraries fail to load      │
│     → Show error message            │
│     → Suggest offline mode          │
│                                     │
│  2. JavaScript parsing error        │
│     → Log to console                │
│     → Show error in preview         │
│                                     │
│  3. Image conversion fails          │
│     → Show placeholder              │
│     → Log error                     │
│                                     │
│  4. Theme not found                 │
│     → Fall back to dark theme       │
│     → Log warning                   │
│                                     │
└─────────────────────────────────────┘
```

## Summary

The JavaScript preview architecture:

1. **Separates concerns**: Python handles UI, JavaScript handles rendering
2. **Uses modern libraries**: marked.js and highlight.js
3. **Optimizes performance**: Caching, debouncing, scroll preservation
4. **Maintains compatibility**: Drop-in replacement for Python preview
5. **Enables extensibility**: Easy to add new features in JavaScript

**Result**: Faster, more maintainable, and more extensible preview system!

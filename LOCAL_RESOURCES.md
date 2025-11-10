# Local Resources Configuration

The markdown editor now uses **local JavaScript libraries** instead of CDN links for offline functionality.

## What Changed

### 1. Preview Template (`src/resources/preview_template.html`)
- **Before**: Used CDN links (jsdelivr.net) for marked.js and highlight.js
- **After**: Uses local files via `local:///js/` URLs

### 2. Preview Widget (`src/ui/preview_widget_js.py`)
- Added `ResourceSchemeHandler` class to handle `local://` URL scheme
- Loads local JS/CSS files from `src/resources/js/` directory
- Theme switching now uses local CSS files

### 3. Main Application (`src/main.py`)
- Registered `local://` URL scheme for local resource loading
- Must be registered before QApplication is created

## Local Files

All JavaScript libraries are stored in `src/resources/js/`:

```
src/resources/js/
├── marked.min.js              # Markdown parser
├── highlight.min.js           # Syntax highlighting core
├── github-dark.min.css        # Dark theme for code
├── github.min.css             # Light theme for code
└── [language].min.js          # Language packs (python, javascript, etc.)
```

## Benefits

✅ **Offline functionality** - No internet required  
✅ **Faster loading** - No CDN latency  
✅ **Privacy** - No external requests  
✅ **Reliability** - No CDN downtime issues  
✅ **Version control** - Locked library versions  

## How It Works

1. **URL Scheme Registration**: The `local://` scheme is registered in `main.py` before creating QApplication
2. **Custom Handler**: `ResourceSchemeHandler` intercepts `local://` requests and serves files from disk
3. **MIME Type Detection**: Automatically sets correct content types (JS, CSS, etc.)
4. **Base URL**: HTML is loaded with `local:///` as base URL for relative resource loading

**Note**: We use `local://` instead of `qrc://` because `qrc://` is reserved by Qt for compiled Qt Resource files.

## Updating Libraries

To update the JavaScript libraries:

```bash
python download_js_libs.py
```

This will download the latest versions to `src/resources/js/`.

**Note**: After downloading, the template already uses `local://` URLs, so no changes are needed.

## Troubleshooting

If resources fail to load:

1. **Check files exist**: Verify all files are in `src/resources/js/`
2. **Check console**: Look for "Resource not found" messages
3. **Verify scheme registration**: Ensure `local://` is registered before QApplication
4. **Check handler installation**: Verify `ResourceSchemeHandler` is installed on the profile
5. **Check paths**: The handler prints debug info showing file paths being accessed

## Technical Details

### URL Scheme Handler

```python
class ResourceSchemeHandler(QWebEngineUrlSchemeHandler):
    def requestStarted(self, request):
        # Intercepts qrc:// URLs
        # Loads files from src/resources/
        # Sets appropriate MIME types
        # Returns file content
```

### Scheme Registration

```python
local_scheme = QWebEngineUrlScheme(b"local")
local_scheme.setFlags(
    QWebEngineUrlScheme.SecureScheme | 
    QWebEngineUrlScheme.LocalScheme | 
    QWebEngineUrlScheme.LocalAccessAllowed
)
QWebEngineUrlScheme.registerScheme(local_scheme)
```

**Important**: Do not use `qrc://` as it's reserved by Qt for compiled resources.

## Migration Notes

If you were using the CDN version:
- No changes needed to markdown content
- Preview functionality remains the same
- Themes work identically
- All features preserved

The only difference is where the JavaScript files are loaded from.

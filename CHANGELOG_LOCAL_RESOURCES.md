# Changelog: Local Resources Implementation

## Summary

Successfully migrated the markdown editor from CDN-based JavaScript libraries to local file loading for complete offline functionality.

## Changes Made

### 1. URL Scheme: `qrc://` → `local://`

**Why the change?**
- `qrc://` is reserved by Qt for compiled Qt Resource files (.qrc)
- Attempting to override it causes: "Cannot install a URL scheme handler overriding internal scheme: qrc"
- Solution: Use custom `local://` scheme instead

### 2. Files Modified

#### `src/main.py`
- Registered `local://` URL scheme before QApplication creation
- Added proper flags for secure local access

#### `src/ui/preview_widget_js.py`
- Added `ResourceSchemeHandler` class to serve local files
- Handles `local://` URL requests
- Loads files from `src/resources/` directory
- Automatic MIME type detection
- Buffer management to keep resources alive

#### `src/resources/preview_template.html`
- Changed all CDN URLs to `local://` URLs
- Updated marked.js, highlight.js, and language packs
- Updated preview_renderer.js reference

### 3. Documentation Created

- `LOCAL_RESOURCES.md` - Complete guide on local resources
- `CHANGELOG_LOCAL_RESOURCES.md` - This file

## Technical Details

### URL Scheme Registration

```python
# In src/main.py - BEFORE QApplication creation
local_scheme = QWebEngineUrlScheme(b"local")
local_scheme.setFlags(
    QWebEngineUrlScheme.SecureScheme | 
    QWebEngineUrlScheme.LocalScheme | 
    QWebEngineUrlScheme.LocalAccessAllowed
)
QWebEngineUrlScheme.registerScheme(local_scheme)
```

### Resource Handler

```python
class ResourceSchemeHandler(QWebEngineUrlSchemeHandler):
    def requestStarted(self, request):
        # 1. Parse URL path
        # 2. Build absolute file path
        # 3. Read file content
        # 4. Detect MIME type
        # 5. Create buffer and reply
        # 6. Keep buffer alive
```

### Resource Loading Flow

1. HTML template loaded with `local:///` base URL
2. Browser requests `local:///js/marked.min.js`
3. `ResourceSchemeHandler` intercepts request
4. Handler reads file from `src/resources/js/marked.min.js`
5. Returns file content with correct MIME type
6. Browser executes JavaScript

## Testing Results

✅ All JavaScript libraries load successfully  
✅ Syntax highlighting works  
✅ Markdown rendering works  
✅ Theme switching works  
✅ No internet connection required  
✅ No CDN errors or warnings  

### Files Loaded Successfully

- marked.min.js (34,919 bytes)
- highlight.min.js (121,727 bytes)
- github-dark.min.css (1,315 bytes)
- 14 language packs (python, javascript, typescript, etc.)
- preview_renderer.js (7,206 bytes)

**Total**: ~210 KB of JavaScript libraries loaded from disk

## Benefits

1. **Offline Functionality** - Works without internet
2. **Performance** - No CDN latency
3. **Privacy** - No external requests
4. **Reliability** - No CDN downtime
5. **Version Control** - Locked library versions
6. **Security** - No third-party CDN dependencies

## Migration Notes

### For Users
- No changes needed to existing documents
- Preview functionality identical
- All features preserved
- Faster initial load after first run

### For Developers
- Use `local://` for custom resources
- Place files in `src/resources/`
- Handler automatically serves files
- MIME types detected automatically

## Troubleshooting

If resources don't load:

1. Check files exist in `src/resources/js/`
2. Run `python download_js_libs.py` to download missing files
3. Check console for "Resource not found" errors
4. Verify `local://` scheme registered before QApplication
5. Ensure ResourceSchemeHandler installed on profile

## Future Improvements

- [ ] Add resource caching for better performance
- [ ] Compress resources for smaller file size
- [ ] Add resource integrity checking
- [ ] Support for additional resource types
- [ ] Resource preloading optimization

## Version Info

- **Date**: 2025-11-10
- **Python**: 3.11+
- **PySide6**: 6.5.0+
- **marked.js**: 11.0.0
- **highlight.js**: 11.9.0

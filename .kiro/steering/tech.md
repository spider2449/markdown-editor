# Technology Stack

## Core Technologies

- **Python**: 3.11+
- **UI Framework**: PySide6 (Qt for Python) 6.5.0+
- **Database**: SQLite3 (embedded)
- **Markdown Processing**: markdown 3.4.0+
- **Syntax Highlighting**: Pygments 2.15.0+

## Key Libraries

- **PySide6.QtWidgets**: UI components and layouts
- **PySide6.QtWebEngineWidgets**: HTML preview rendering (Chromium-based)
- **PySide6.QtGui**: Graphics, fonts, and input handling
- **markdown**: Markdown to HTML conversion
- **Pygments**: Code syntax highlighting in markdown

## Build System

### Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run application
python src/main.py

# Run tests
python tests/test_app.py
```

### Building Executables

Uses PyInstaller for creating standalone executables:

```cmd
# Optimized single-file build (181 MB)
pyinstaller --clean MarkdownEditor_optimized.spec

# Output: dist\MarkdownEditor.exe
```

Alternative build options:
- **UPX compression**: Can reduce size by 30-50% (~90-120 MB)
- **Nuitka**: Native compilation for faster execution (~100-150 MB)
- **Directory build**: Faster startup but larger total size (461 MB)

### Size Considerations

- Qt libraries: ~100 MB
- WebEngine (Chromium): ~80 MB
- Total optimized: 181 MB single file

## Optional Dependencies

- **psutil**: Memory usage monitoring (optional, for performance stats)

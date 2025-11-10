# Markdown Editor - Build Guide

## Size Comparison

| Build Type | Size | Pros | Cons |
|------------|------|------|------|
| **Original** | 215 MB | Single file | Large |
| **Optimized** | 181 MB | Single file, excluded unused modules | Still large |
| **Directory** | 461 MB | Faster startup | Multiple files, larger total |

## Recommended: Optimized Single File (181 MB)

```cmd
pyinstaller --clean MarkdownEditor_optimized.spec
```

Output: `dist\MarkdownEditor.exe` (181 MB)

## Further Optimization Options

### 1. Install UPX for Compression (Can reduce by 30-50%)

Download UPX from: https://github.com/upx/upx/releases

```cmd
# Extract upx.exe to a folder in PATH, then:
pyinstaller --clean MarkdownEditor_optimized.spec
```

Expected size: ~90-120 MB

### 2. Use Nuitka (Compiles to native code)

```cmd
pip install nuitka
python -m nuitka --standalone --windows-disable-console --enable-plugin=pyside6 main.py
```

Pros: Faster execution, smaller size (~100-150 MB)
Cons: Longer compile time

### 3. Split WebEngine (Advanced)

If you can make WebEngine optional or use a lighter preview:
- Replace QtWebEngine with QtWebKit or markdown-to-HTML only
- Could reduce to ~50-80 MB
- Requires code refactoring

## Why PySide6 is Large

PySide6 includes:
- Qt libraries (~100 MB)
- WebEngine (Chromium-based, ~80 MB)
- Multiple platform binaries

The WebEngine component alone is 80+ MB because it's essentially embedding a web browser.

## Alternative: Installer Package

Instead of single EXE, create an installer:

```cmd
pip install pynsist
```

This creates a smaller installer that downloads Python components on first run.

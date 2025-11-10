# Markdown Editor

A desktop markdown editor built with Python 3.11, PySide6, and SQLite featuring real-time preview and image pasting capabilities.

## Features

- **Three-pane layout**: Document sidebar, markdown editor, and live preview
- **Real-time preview**: See rendered HTML as you type
- **Syntax highlighting**: Markdown syntax highlighting in the editor
- **Image pasting**: Paste images directly from clipboard (Ctrl+V)
- **Document management**: Create, edit, and delete documents
- **Auto-save**: Documents are automatically saved as you type
- **Dark theme**: Professional dark theme interface
- **Document outline**: Navigate through document headers

## Installation

1. Ensure you have Python 3.11 installed
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the application:
```bash
python src/main.py
# or use the convenience launcher
python run.py
```

### Keyboard Shortcuts

- **Ctrl+N**: New document
- **Ctrl+S**: Save document
- **Ctrl+V**: Paste (including images)
- **Ctrl+Shift+V**: Paste image
- **Ctrl+E**: Focus editor
- **Ctrl+B**: Bold text
- **Ctrl+I**: Italic text

### Toolbar Features

- **Bold/Italic**: Format selected text
- **Headers**: Insert H1, H2, H3 headers
- **Lists**: Create bullet or numbered lists
- **Links/Images**: Insert links and images

## Project Structure

```
markdown_editor/
├── src/                    # Source code
│   ├── main.py             # Application entry point
│   ├── ui/                 # UI components
│   │   ├── main_window.py      # Main application window
│   │   ├── editor_widget.py    # Markdown editor with syntax highlighting
│   │   ├── preview_widget.py   # HTML preview panel
│   │   ├── sidebar_widget.py   # Document navigation sidebar
│   │   └── syntax_highlighter.py # Markdown syntax highlighter
│   ├── core/               # Core business logic
│   │   ├── document_manager.py # SQLite document storage
│   │   └── image_handler.py    # Image pasting functionality
│   └── resources/          # Static resources
│       └── styles.qss          # Dark theme stylesheet
├── tests/                  # Test files
├── run.py                  # Convenience launcher
└── requirements.txt        # Python dependencies
```

## Database

The application uses SQLite to store:
- Document content and metadata
- Embedded images as BLOBs
- Creation and modification timestamps

Database file: `documents.db` (created automatically)

## Testing

Run the test script to verify installation:
```bash
python tests/test_app.py
```

## Requirements

- Python 3.11+
- PySide6 6.5.0+
- markdown 3.4.0+
- Pygments 2.15.0+
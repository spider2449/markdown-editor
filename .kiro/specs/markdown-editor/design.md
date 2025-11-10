# Design Document

## Architecture Overview

The markdown editor follows a Model-View-Controller (MVC) architecture using PySide6 for the GUI framework. The application consists of several key components:

- **MainWindow**: The primary application window managing the three-pane layout
- **EditorWidget**: The center pane with syntax-highlighted markdown editing
- **PreviewWidget**: The right pane displaying rendered HTML output
- **SidebarWidget**: The left pane with document navigation and outline
- **DocumentManager**: Handles document operations and SQLite storage
- **ImageHandler**: Manages image pasting and storage functionality

## UI Layout Design

Based on the Markdown Monster reference, the application uses a three-pane layout:

```
┌─────────────────────────────────────────────────────────────┐
│ Menu Bar & Toolbar                                          │
├──────────┬─────────────────────┬────────────────────────────┤
│          │                     │                            │
│ Sidebar  │    Editor Pane      │     Preview Pane           │
│          │                     │                            │
│ - Docs   │  # Markdown Content │  Rendered HTML Output      │
│ - Outline│    with syntax      │    with styling            │
│          │    highlighting     │                            │
│          │                     │                            │
├──────────┴─────────────────────┴────────────────────────────┤
│ Status Bar                                                  │
└─────────────────────────────────────────────────────────────┘
```

## Component Design

### MainWindow
- **Purpose**: Primary application window and layout manager
- **Responsibilities**:
  - Initialize three-pane splitter layout
  - Manage menu bar and toolbar
  - Coordinate between components
  - Handle application-level events

### EditorWidget
- **Purpose**: Markdown text editor with syntax highlighting
- **Technology**: QTextEdit with custom syntax highlighter
- **Features**:
  - Real-time syntax highlighting for markdown
  - Line numbers
  - Auto-indentation
  - Text change signals for preview updates
  - Table creation with customizable dimensions
  - Find and replace functionality
  - Theme support and customization

### PreviewWidget
- **Purpose**: HTML preview of markdown content
- **Technology**: QWebEngineView
- **Features**:
  - Renders markdown to HTML using python-markdown
  - Synchronized scrolling with editor
  - Custom CSS styling for consistent appearance

### SidebarWidget
- **Purpose**: Document navigation and outline view
- **Components**:
  - Document tree view (QTreeWidget)
  - Document outline view (QListWidget)
  - New/Delete document buttons
- **Features**:
  - Hierarchical document organization
  - Real-time outline generation from headers

### DocumentManager
- **Purpose**: Document persistence and management
- **Technology**: SQLite database with custom ORM
- **Schema**:
```sql
CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER,
    filename TEXT NOT NULL,
    data BLOB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents (id)
);
```

### ImageHandler
- **Purpose**: Handle image pasting and storage
- **Features**:
  - Detect clipboard image content
  - Store images as BLOBs in SQLite
  - Generate markdown image syntax
  - Serve images to preview widget

## Data Flow

1. **Document Loading**:
   - User selects document from sidebar
   - DocumentManager retrieves content from SQLite
   - EditorWidget displays content
   - PreviewWidget renders HTML

2. **Real-time Preview**:
   - EditorWidget emits textChanged signal
   - MainWindow processes markdown to HTML
   - PreviewWidget updates display
   - Scroll positions synchronize

3. **Image Pasting**:
   - User pastes image (Ctrl+V)
   - ImageHandler detects clipboard content
   - Image stored in SQLite with unique ID
   - Markdown syntax inserted at cursor
   - PreviewWidget displays image

4. **Document Saving**:
   - Auto-save on text changes (debounced)
   - DocumentManager updates SQLite
   - Sidebar updates modification indicators

## Technology Stack

- **Python 3.11**: Core application language
- **PySide6**: GUI framework
  - QMainWindow: Main application window
  - QSplitter: Three-pane layout
  - QTextEdit: Markdown editor
  - QWebEngineView: HTML preview
  - QTreeWidget/QListWidget: Sidebar components
- **SQLite**: Document and image storage
- **python-markdown**: Markdown to HTML conversion
- **Pygments**: Syntax highlighting for code blocks
- **QSyntaxHighlighter**: Custom markdown syntax highlighting

## File Structure

```
markdown_editor/
├── main.py                 # Application entry point
├── ui/
│   ├── __init__.py
│   ├── main_window.py      # MainWindow class
│   ├── editor_widget.py    # EditorWidget class
│   ├── preview_widget.py   # PreviewWidget class
│   ├── sidebar_widget.py   # SidebarWidget class
│   ├── syntax_highlighter.py # Markdown syntax highlighter
│   ├── find_replace_dialog.py # Find and replace dialog
│   ├── line_number_widget.py # Line number display
│   ├── editor_themes.py    # Editor theme management
│   └── table_dialog.py     # Table creation dialog
├── core/
│   ├── __init__.py
│   ├── document_manager.py # DocumentManager class
│   └── image_handler.py    # ImageHandler class
├── resources/
│   ├── styles.qss          # Application styling
│   └── icons/              # UI icons
└── requirements.txt        # Python dependencies
```

## Styling and Theming

The application uses a dark theme similar to the reference design:
- Dark background colors (#2b2b2b, #3c3c3c)
- Syntax highlighting with appropriate colors
- Custom QSS stylesheet for consistent appearance
- Responsive layout that adapts to window resizing

## Performance Considerations

- **Debounced Updates**: Preview updates are debounced to avoid excessive rendering
- **Lazy Loading**: Documents loaded on-demand from database
- **Image Optimization**: Images compressed before storage
- **Efficient Rendering**: HTML preview uses caching where possible
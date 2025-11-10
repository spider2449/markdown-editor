"""
Main Window - Primary application window managing the three-pane layout
"""

from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QSplitter, 
                               QMenuBar, QToolBar, QStatusBar, QMessageBox,
                               QApplication)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QIcon, QKeySequence, QActionGroup

from .editor_widget import EditorWidget
from .preview_widget_js import PreviewWidgetJS as PreviewWidget
from .sidebar_widget import SidebarWidget
from .table_dialog import TableDialog
from .search_dialog import SearchDialog
from .hotkey_dialog import HotkeyDialog
from core.document_manager import DocumentManager
from core.image_handler import ImageHandler
from core.settings_manager import SettingsManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_document_id = None
        self.search_dialog = None
        self.setup_core_components()
        self.setup_ui()
        self.setup_connections()
        self.load_documents()
        self.restore_session()
        
        # Auto-save timer
        self.auto_save_timer = QTimer()
        self.auto_save_timer.setSingleShot(True)
        self.auto_save_timer.timeout.connect(self.auto_save)
        self.auto_save_timer.setInterval(2000)  # 2 seconds
        
        # Setup performance optimization timer
        self.setup_performance_timer()
    
    def setup_core_components(self):
        """Initialize core components"""
        try:
            self.document_manager = DocumentManager()
            self.image_handler = ImageHandler(self.document_manager)
            self.settings_manager = SettingsManager()
        except Exception as e:
            QMessageBox.critical(self, "Initialization Error", 
                               f"Failed to initialize application components: {str(e)}")
            QApplication.quit()
    
    def setup_ui(self):
        """Setup the main UI"""
        self.setWindowTitle("Markdown Editor")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget with splitter layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create splitter for three-pane layout
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Create widgets
        self.sidebar = SidebarWidget()
        self.editor = EditorWidget()
        self.preview = PreviewWidget(self.image_handler)
        
        # Add widgets to splitter
        self.splitter.addWidget(self.sidebar)
        self.splitter.addWidget(self.editor)
        self.splitter.addWidget(self.preview)
        
        # Set splitter proportions (sidebar: 20%, editor: 40%, preview: 40%)
        self.splitter.setSizes([240, 480, 480])
        
        # Connect splitter moved signal to save settings
        self.splitter.splitterMoved.connect(self.save_splitter_state)
        
        layout.addWidget(self.splitter)
        
        # Setup menu bar and toolbar
        self.setup_menu_bar()
        self.setup_toolbar()
        self.setup_status_bar()
    
    def setup_menu_bar(self):
        """Setup the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("New Document", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self.sidebar._create_new_document)
        file_menu.addAction(new_action)
        
        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_current_document)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        # Find and Replace
        find_action = QAction("Find...", self)
        find_action.setShortcut(QKeySequence.Find)
        find_action.triggered.connect(self.editor.show_find_replace)
        edit_menu.addAction(find_action)
        
        find_replace_action = QAction("Find and Replace...", self)
        find_replace_action.setShortcut(QKeySequence("Ctrl+H"))
        find_replace_action.triggered.connect(self.editor.show_find_replace)
        edit_menu.addAction(find_replace_action)
        
        edit_menu.addSeparator()
        
        # Global search
        search_action = QAction("Search All Documents...", self)
        search_action.setShortcut(QKeySequence("Ctrl+Shift+F"))
        search_action.triggered.connect(self.show_search_dialog)
        edit_menu.addAction(search_action)
        
        edit_menu.addSeparator()
        
        paste_image_action = QAction("Paste Image", self)
        paste_image_action.setShortcut(QKeySequence("Ctrl+Shift+V"))
        paste_image_action.triggered.connect(self.paste_image)
        edit_menu.addAction(paste_image_action)
        
        edit_menu.addSeparator()
        
        # Quote action
        quote_action = QAction("Toggle Quote", self)
        quote_action.setShortcut(QKeySequence("Ctrl+Q"))
        quote_action.triggered.connect(self.editor.toggle_quote)
        edit_menu.addAction(quote_action)
        
        # Table insertion
        table_action = QAction("Insert Table", self)
        table_action.setShortcut(QKeySequence("Ctrl+T"))
        table_action.triggered.connect(self.insert_table)
        edit_menu.addAction(table_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        focus_editor_action = QAction("Focus Editor", self)
        focus_editor_action.setShortcut(QKeySequence("Ctrl+E"))
        focus_editor_action.triggered.connect(self.editor.focus)
        view_menu.addAction(focus_editor_action)
        
        view_menu.addSeparator()
        
        # Editor options
        toggle_line_numbers_action = QAction("Toggle Line Numbers", self)
        toggle_line_numbers_action.setShortcut(QKeySequence("Ctrl+L"))
        toggle_line_numbers_action.triggered.connect(self.editor.toggle_line_numbers)
        view_menu.addAction(toggle_line_numbers_action)
        
        # Zoom actions
        zoom_in_action = QAction("Zoom In", self)
        # Use Ctrl+= to avoid conflict with direct key handler (Ctrl++ is handled there)
        zoom_in_action.setShortcut(QKeySequence("Ctrl+="))
        zoom_in_action.triggered.connect(self.editor.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Zoom Out", self)
        # Use only underscore to avoid conflict with direct key handler
        zoom_out_action.setShortcut(QKeySequence("Ctrl+_"))
        zoom_out_action.triggered.connect(self.editor.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        reset_zoom_action = QAction("Reset Zoom", self)
        reset_zoom_action.setShortcut(QKeySequence("Ctrl+0"))
        reset_zoom_action.triggered.connect(self.editor.reset_zoom)
        view_menu.addAction(reset_zoom_action)
        
        view_menu.addSeparator()
        
        # Editor theme submenu
        editor_theme_menu = view_menu.addMenu("Editor Theme")
        
        # Create editor theme actions
        self.editor_theme_group = QActionGroup(self)
        
        for theme_name in self.editor.get_available_themes():
            theme_action = QAction(theme_name.replace('_', ' ').title(), self)
            theme_action.setCheckable(True)
            theme_action.setData(theme_name)
            theme_action.triggered.connect(lambda checked, name=theme_name: self.change_editor_theme(name))
            self.editor_theme_group.addAction(theme_action)
            editor_theme_menu.addAction(theme_action)
            
            # Set default theme as checked
            if theme_name == self.editor.get_current_theme():
                theme_action.setChecked(True)
        
        view_menu.addSeparator()
        
        # Preview theme submenu
        theme_menu = view_menu.addMenu("Preview Theme")
        
        # Create theme actions
        self.theme_group = QActionGroup(self)
        
        for theme_name in self.preview.get_available_themes():
            theme_action = QAction(theme_name.title(), self)
            theme_action.setCheckable(True)
            theme_action.setData(theme_name)
            theme_action.triggered.connect(lambda checked, name=theme_name: self.change_theme(name))
            self.theme_group.addAction(theme_action)
            theme_menu.addAction(theme_action)
            
            # Set default theme as checked
            if theme_name == self.preview.get_current_theme():
                theme_action.setChecked(True)
        
        view_menu.addSeparator()
        
        # Print action
        print_action = QAction("Print Preview", self)
        print_action.setShortcut(QKeySequence.Print)
        print_action.triggered.connect(self.print_preview)
        view_menu.addAction(print_action)
        
        view_menu.addSeparator()
        
        clear_cache_action = QAction("Clear Caches", self)
        clear_cache_action.triggered.connect(self.clear_caches)
        view_menu.addAction(clear_cache_action)
        
        optimize_action = QAction("Optimize Performance", self)
        optimize_action.triggered.connect(self.optimize_performance)
        view_menu.addAction(optimize_action)
        
        stats_action = QAction("Performance Statistics", self)
        stats_action.triggered.connect(self.show_performance_stats)
        view_menu.addAction(stats_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        hotkeys_action = QAction("Keyboard Shortcuts", self)
        hotkeys_action.setShortcut(QKeySequence("F1"))
        hotkeys_action.triggered.connect(self.show_hotkeys)
        help_menu.addAction(hotkeys_action)
    
    def setup_toolbar(self):
        """Setup the toolbar"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Bold button
        bold_action = QAction("Bold", self)
        bold_action.setShortcut(QKeySequence.Bold)
        bold_action.triggered.connect(lambda: self.insert_markdown("**", "**"))
        toolbar.addAction(bold_action)
        
        # Italic button
        italic_action = QAction("Italic", self)
        italic_action.setShortcut(QKeySequence.Italic)
        italic_action.triggered.connect(lambda: self.insert_markdown("*", "*"))
        toolbar.addAction(italic_action)
        
        toolbar.addSeparator()
        
        # Header buttons
        h1_action = QAction("H1", self)
        h1_action.triggered.connect(lambda: self.insert_markdown("# ", ""))
        toolbar.addAction(h1_action)
        
        h2_action = QAction("H2", self)
        h2_action.triggered.connect(lambda: self.insert_markdown("## ", ""))
        toolbar.addAction(h2_action)
        
        h3_action = QAction("H3", self)
        h3_action.triggered.connect(lambda: self.insert_markdown("### ", ""))
        toolbar.addAction(h3_action)
        
        toolbar.addSeparator()
        
        # List buttons
        ul_action = QAction("• List", self)
        ul_action.triggered.connect(lambda: self.insert_markdown("- ", ""))
        toolbar.addAction(ul_action)
        
        ol_action = QAction("1. List", self)
        ol_action.triggered.connect(lambda: self.insert_markdown("1. ", ""))
        toolbar.addAction(ol_action)
        
        toolbar.addSeparator()
        
        # Quote button
        quote_action = QAction("Quote", self)
        quote_action.triggered.connect(self.editor.toggle_quote)
        toolbar.addAction(quote_action)
        
        toolbar.addSeparator()
        
        # Link and image buttons
        link_action = QAction("Link", self)
        link_action.triggered.connect(lambda: self.insert_markdown("[", "](url)"))
        toolbar.addAction(link_action)
        
        image_action = QAction("Image", self)
        image_action.triggered.connect(lambda: self.insert_markdown("![", "](url)"))
        toolbar.addAction(image_action)
        
        toolbar.addSeparator()
        
        # Table button
        table_action = QAction("Table", self)
        table_action.triggered.connect(self.insert_table)
        toolbar.addAction(table_action)
    
    def setup_status_bar(self):
        """Setup the status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def setup_connections(self):
        """Setup signal connections between components"""
        # Sidebar connections
        self.sidebar.document_selected.connect(self.load_document)
        self.sidebar.document_created.connect(self.create_document)
        self.sidebar.document_deleted.connect(self.delete_document)
        self.sidebar.document_renamed.connect(self.rename_document)
        self.sidebar.outline_item_clicked.connect(self.navigate_to_heading)
        
        # Editor connections
        self.editor.text_changed.connect(self.on_text_changed)
        self.editor.paste_requested.connect(self.paste_image)
        self.editor.scroll_changed.connect(self.preview.sync_scroll)
        
        # Image handler connections
        self.image_handler.image_pasted.connect(self.editor.insert_text)
    
    def load_documents(self):
        """Load all documents from database with lazy loading"""
        try:
            # Load documents without content for sidebar display (performance optimization)
            documents = self.document_manager.get_all_documents(load_content=False)
            self.sidebar.update_documents(documents)
            
            # Load first document if available
            if documents:
                self.load_document(documents[0].id)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load documents: {str(e)}")
            self.status_bar.showMessage("Failed to load documents")
    
    def load_document(self, doc_id: int):
        """Load a specific document with enhanced lazy loading and progress indication"""
        try:
            # Check if document is large and use progressive loading
            if self.document_manager.is_large_document(doc_id):
                self.status_bar.showMessage("Loading large document...")
                
                # Load metadata first for immediate UI feedback
                document = self.document_manager.get_document(doc_id, load_content=False)
                if document:
                    # Show document info immediately
                    size_kb = document.content_length / 1024
                    self.status_bar.showMessage(f"Loading: {document.title} ({size_kb:.1f} KB)...")
                    
                    # Process events to update UI
                    QApplication.processEvents()
                    
                    # Load content with streaming support
                    content = self.document_manager.load_document_content(doc_id, use_streaming=True)
                    if content is not None:
                        document.content = content
                        document._is_content_loaded = True
                    else:
                        raise RuntimeError("Failed to load document content")
                else:
                    raise RuntimeError("Document metadata not found")
            else:
                # Load normally for small documents
                document = self.document_manager.get_document(doc_id, load_content=True)
            
            if document:
                self.current_document_id = doc_id
                
                # Set content with progress indication for large documents
                if document.content_length > 100000:  # 100KB threshold
                    self.status_bar.showMessage("Rendering content...")
                    QApplication.processEvents()
                
                self.editor.set_content(document.content)
                self.preview.update_content(document.content)
                self.sidebar.update_outline(document.content)
                self.image_handler.set_current_document(doc_id)
                
                # Show final status with performance info
                if document.content_length > 50000:
                    size_kb = document.content_length / 1024
                    cache_stats = self.document_manager.get_cache_stats()
                    self.status_bar.showMessage(f"Loaded: {document.title} ({size_kb:.1f} KB) - Cache: {cache_stats['document_cache_size']}/{cache_stats['document_cache_max']}")
                else:
                    self.status_bar.showMessage(f"Loaded: {document.title}")
                
                # Save as last opened document
                self.settings_manager.set_last_document_id(doc_id)
                self.settings_manager.add_recent_document(doc_id, document.title)
            else:
                QMessageBox.warning(self, "Warning", f"Document with ID {doc_id} not found")
                self.status_bar.showMessage("Document not found")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load document: {str(e)}")
            self.status_bar.showMessage("Failed to load document")
    
    def create_document(self, title: str):
        """Create a new document"""
        try:
            doc_id = self.document_manager.create_document(title, "# " + title + "\n\n")
            self.load_documents()  # Refresh document list
            self.load_document(doc_id)  # Load the new document
            self.status_bar.showMessage(f"Created: {title}")
        except (RuntimeError, ValueError) as e:
            QMessageBox.critical(self, "Error", f"Failed to create document: {str(e)}")
            self.status_bar.showMessage("Failed to create document")
    
    def delete_document(self, doc_id: int):
        """Delete a document"""
        try:
            self.document_manager.delete_document(doc_id)
            self.load_documents()  # Refresh document list
            
            # Clear editor if deleted document was current
            if self.current_document_id == doc_id:
                self.current_document_id = None
                self.editor.set_content("")
                self.preview.update_content("")
                self.sidebar.update_outline("")
                self.settings_manager.set_last_document_id(None)
            
            # Remove from recent documents
            self.settings_manager.remove_recent_document(doc_id)
            
            self.status_bar.showMessage("Document deleted")
        except (RuntimeError, ValueError) as e:
            QMessageBox.critical(self, "Error", f"Failed to delete document: {str(e)}")
            self.status_bar.showMessage("Failed to delete document")
    
    def rename_document(self, doc_id: int, new_title: str):
        """Rename a document"""
        try:
            self.document_manager.update_document(doc_id, title=new_title)
            self.status_bar.showMessage(f"Document renamed to: {new_title}", 2000)
        except (RuntimeError, ValueError) as e:
            QMessageBox.critical(self, "Error", f"Failed to rename document: {str(e)}")
            self.status_bar.showMessage("Failed to rename document")
            # Refresh document list to revert UI changes
            self.load_documents()
    
    def on_text_changed(self, content: str):
        """Handle text changes in editor"""
        # Update preview
        self.preview.update_content(content)
        self.sidebar.update_outline(content)
        
        # Start auto-save timer
        if self.current_document_id:
            self.auto_save_timer.start()
    
    def auto_save(self):
        """Auto-save current document"""
        if self.current_document_id:
            try:
                content = self.editor.get_content()
                self.document_manager.update_document(self.current_document_id, content=content)
                self.status_bar.showMessage("Auto-saved", 2000)
            except (RuntimeError, ValueError) as e:
                self.status_bar.showMessage("Auto-save failed", 2000)
    
    def save_current_document(self):
        """Manually save current document"""
        if self.current_document_id:
            try:
                content = self.editor.get_content()
                self.document_manager.update_document(self.current_document_id, content=content)
                self.status_bar.showMessage("Saved", 2000)
            except (RuntimeError, ValueError) as e:
                QMessageBox.critical(self, "Error", f"Failed to save document: {str(e)}")
                self.status_bar.showMessage("Save failed")
    
    def paste_image(self):
        """Handle image pasting"""
        print("MainWindow: paste_image() called")
        try:
            if self.current_document_id is None:
                print("MainWindow: No current document selected")
                QMessageBox.warning(self, "Warning", "Please select a document first")
                self.status_bar.showMessage("No document selected")
                return
                
            print(f"MainWindow: Attempting to paste image for document {self.current_document_id}")
            if self.image_handler.handle_paste():
                print("MainWindow: Image paste successful")
                self.status_bar.showMessage("Image pasted", 2000)
            else:
                print("MainWindow: No image in clipboard")
                self.status_bar.showMessage("No image in clipboard", 2000)
        except Exception as e:
            print(f"MainWindow: Error pasting image: {e}")
            QMessageBox.critical(self, "Error", f"Failed to paste image: {str(e)}")
            self.status_bar.showMessage("Failed to paste image")
    
    def insert_markdown(self, prefix: str, suffix: str):
        """Insert markdown formatting"""
        self.editor.insert_text(prefix + suffix)
        self.editor.focus()
    
    def insert_table(self):
        """Insert a markdown table with custom dimensions"""
        rows, cols = TableDialog.get_table_dimensions(self)
        if rows and cols:
            self.editor.insert_table(rows, cols)
            self.editor.focus()
    
    def restore_session(self):
        """Restore previous session state"""
        try:
            # Restore window geometry
            geometry = self.settings_manager.get_window_geometry()
            if geometry:
                self.restoreGeometry(geometry)
            
            # Restore splitter sizes
            sizes = self.settings_manager.get_splitter_sizes()
            if sizes:
                self.splitter.setSizes(sizes)
            
            # Restore preview theme
            saved_theme = self.settings_manager.get_preview_theme()
            self.preview.set_theme(saved_theme)
            
            # Update theme menu selection
            for action in self.theme_group.actions():
                if action.data() == saved_theme:
                    action.setChecked(True)
                    break
            
            # Restore editor theme
            saved_editor_theme = self.settings_manager.get_editor_theme()
            self.editor.set_theme(saved_editor_theme)
            
            # Update editor theme menu selection
            for action in self.editor_theme_group.actions():
                if action.data() == saved_editor_theme:
                    action.setChecked(True)
                    break
            
            # Restore editor settings
            line_numbers_enabled = self.settings_manager.get_line_numbers_enabled()
            self.editor.set_line_numbers_enabled(line_numbers_enabled)
            
            font_size = self.settings_manager.get_editor_font_size()
            self.editor.set_font_size(font_size)
            
            font_family = self.settings_manager.get_editor_font_family()
            self.editor.set_font_family(font_family)
            
            # Restore last opened document
            last_doc_id = self.settings_manager.get_last_document_id()
            if last_doc_id:
                # Check if document still exists
                document = self.document_manager.get_document(last_doc_id)
                if document:
                    self.load_document(last_doc_id)
                    self.sidebar.select_document(last_doc_id)
                else:
                    # Document no longer exists, clear from settings
                    self.settings_manager.set_last_document_id(None)
                    self.settings_manager.remove_recent_document(last_doc_id)
            
        except Exception as e:
            # If session restore fails, just continue with defaults
            pass
    
    def save_session_state(self):
        """Save current session state"""
        try:
            # Save window geometry
            self.settings_manager.set_window_geometry(self.saveGeometry())
            
            # Save splitter sizes
            self.settings_manager.set_splitter_sizes(self.splitter.sizes())
            
            # Save current document
            if self.current_document_id:
                self.settings_manager.set_last_document_id(self.current_document_id)
                
                # Add to recent documents
                document = self.document_manager.get_document(self.current_document_id)
                if document:
                    self.settings_manager.add_recent_document(self.current_document_id, document.title)
        except Exception as e:
            # If session save fails, just continue
            pass
    
    def save_splitter_state(self):
        """Save splitter state when moved"""
        try:
            self.settings_manager.set_splitter_sizes(self.splitter.sizes())
        except Exception as e:
            pass
    
    def clear_caches(self):
        """Clear all performance caches"""
        try:
            self.document_manager.clear_caches()
            self.preview.clear_cache()
            self.status_bar.showMessage("Caches cleared", 2000)
        except Exception as e:
            self.status_bar.showMessage("Failed to clear caches", 2000)
    
    def optimize_performance(self):
        """Optimize application performance by managing caches"""
        try:
            # Optimize document and image caches
            self.document_manager.optimize_caches()
            
            # Optimize HTML preview cache
            self.preview.optimize_cache()
            
            self.status_bar.showMessage("Performance optimized", 2000)
        except Exception as e:
            self.status_bar.showMessage("Performance optimization failed", 2000)
    
    def show_performance_stats(self):
        """Show enhanced performance statistics dialog"""
        try:
            doc_stats = self.document_manager.get_cache_stats()
            preview_stats = self.preview.get_cache_stats()
            image_stats = self.image_handler.get_image_stats()
            
            # Get memory usage if available
            memory_info = self.get_memory_usage()
            
            stats_message = f"""Performance Statistics:

Document Cache:
- Size: {doc_stats['document_cache_size']}/{doc_stats['document_cache_max']}
- Metadata Cache: {doc_stats['metadata_cache_size']} items

Image Cache:
- Size: {image_stats['image_cache_size']}/{image_stats['image_cache_max']}
- Compression Quality: {image_stats['compression_quality']}%
- Max Image Size: {image_stats['max_image_size'][0]}x{image_stats['max_image_size'][1]}

HTML Preview Cache:
- Size: {preview_stats['cache_size']}/{preview_stats['cache_max_size']}
- Hit Rate: {preview_stats['hit_rate_percent']}%
- Hits: {preview_stats['cache_hits']}, Misses: {preview_stats['cache_misses']}

Memory Usage:
{memory_info}

Performance Features:
- Lazy loading for documents > 50KB
- LRU cache eviction for optimal memory usage
- Batched HTML rendering with 100ms debounce
- Image compression for files > 100KB
- CSS precompilation for themes
"""
            
            QMessageBox.information(self, "Performance Statistics", stats_message)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to get performance statistics: {str(e)}")
    
    def get_memory_usage(self) -> str:
        """Get current memory usage information"""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            return f"- Current Usage: {memory_mb:.1f} MB"
        except ImportError:
            return "- Memory monitoring not available (install psutil)"
        except Exception as e:
            return f"- Memory info unavailable: {str(e)}"
    
    def monitor_memory_usage(self):
        """Monitor memory usage and optimize if needed"""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            # If memory usage is high (> 500MB), trigger optimization
            if memory_mb > 500:
                self.optimize_performance()
                self.status_bar.showMessage(f"Memory optimized ({memory_mb:.1f} MB)", 3000)
        except ImportError:
            # psutil not available, disable memory monitoring
            self.memory_timer.stop()
        except Exception:
            # Error in memory monitoring, continue silently
            pass
    
    def setup_performance_timer(self):
        """Setup timer for periodic performance optimization"""
        self.performance_timer = QTimer()
        self.performance_timer.timeout.connect(self.optimize_performance)
        self.performance_timer.start(180000)  # Optimize every 3 minutes for better performance
        
        # Setup memory monitoring timer
        self.memory_timer = QTimer()
        self.memory_timer.timeout.connect(self.monitor_memory_usage)
        self.memory_timer.start(60000)  # Check memory every minute
    
    def change_theme(self, theme_name: str):
        """Change the preview theme"""
        try:
            self.preview.set_theme(theme_name)
            # Save theme preference
            self.settings_manager.set_preview_theme(theme_name)
            self.status_bar.showMessage(f"Preview theme changed to {theme_name.title()}", 2000)
        except Exception as e:
            self.status_bar.showMessage(f"Failed to change preview theme: {str(e)}", 3000)
    
    def change_editor_theme(self, theme_name: str):
        """Change the editor theme"""
        try:
            self.editor.set_theme(theme_name)
            # Save editor theme preference
            self.settings_manager.set_editor_theme(theme_name)
            self.status_bar.showMessage(f"Editor theme changed to {theme_name.replace('_', ' ').title()}", 2000)
        except Exception as e:
            self.status_bar.showMessage(f"Failed to change editor theme: {str(e)}", 3000)
    
    def print_preview(self):
        """Print the preview content"""
        try:
            self.preview.print_preview()
        except Exception as e:
            QMessageBox.warning(self, "Print Error", f"Failed to print preview: {str(e)}")
    
    def navigate_to_heading(self, heading_text: str):
        """Navigate to a specific heading in both editor and preview"""
        try:
            # Scroll editor to heading
            self.editor.scroll_to_heading(heading_text)
            
            # Scroll preview to heading
            self.preview.scroll_to_heading(heading_text)
            
            # Focus the editor
            self.editor.focus()
            
            self.status_bar.showMessage(f"Navigated to: {heading_text}", 2000)
        except Exception as e:
            self.status_bar.showMessage(f"Navigation failed: {str(e)}", 2000)
    
    def show_search_dialog(self):
        """Show the global search dialog"""
        if not self.search_dialog:
            self.search_dialog = SearchDialog(self.document_manager, self)
            self.search_dialog.document_selected.connect(self.load_document)
        
        self.search_dialog.show_and_focus()
    
    def show_hotkeys(self):
        """Show the keyboard shortcuts dialog"""
        HotkeyDialog.show_hotkeys(self)
    
    def closeEvent(self, event):
        """Handle application close"""
        # Auto-save before closing
        if self.current_document_id:
            self.auto_save()
        
        # Save session state
        self.save_session_state()
        
        # Clear caches to free memory
        self.clear_caches()
        
        event.accept()
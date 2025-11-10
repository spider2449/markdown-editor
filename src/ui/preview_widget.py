"""
Preview Widget - HTML preview of markdown content
"""

import markdown
import re
import hashlib
import os
import sys
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import (QWebEngineUrlScheme, QWebEngineUrlSchemeHandler, 
                                      QWebEngineProfile, QWebEngineUrlRequestJob)
from PySide6.QtCore import QUrl, QBuffer, QIODevice, Signal, QByteArray

# Add resources directory to path for theme imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'resources'))
from preview_themes import PreviewThemes

# Register custom scheme before any QWebEngine usage
def register_custom_schemes():
    """Register custom URL schemes for the web engine"""
    if not hasattr(register_custom_schemes, '_registered'):
        scheme = QWebEngineUrlScheme(b"image")
        scheme.setFlags(QWebEngineUrlScheme.Flag.SecureScheme | 
                       QWebEngineUrlScheme.Flag.LocalScheme |
                       QWebEngineUrlScheme.Flag.LocalAccessAllowed)
        QWebEngineUrlScheme.registerScheme(scheme)
        register_custom_schemes._registered = True

# Register schemes immediately when module is imported
register_custom_schemes()


class ImageSchemeHandler(QWebEngineUrlSchemeHandler):
    """Custom URL scheme handler for embedded images"""
    
    def __init__(self, image_handler):
        super().__init__()
        self.image_handler = image_handler
    
    def requestStarted(self, request):
        """Handle image:// URL requests"""
        url = request.requestUrl()
        print(f"ImageSchemeHandler: Handling URL: {url.toString()}")
        
        if url.scheme() == "image":
            try:
                image_id = int(url.host())
                print(f"ImageSchemeHandler: Looking for image ID: {image_id}")
                
                result = self.image_handler.get_image_data(image_id)
                
                if result:
                    image_data = result
                    print(f"ImageSchemeHandler: Found image data, size: {len(image_data)} bytes")
                    
                    # Detect image format from data
                    mime_type = self._detect_image_mime_type(image_data)
                    print(f"ImageSchemeHandler: Detected MIME type: {mime_type}")
                    
                    buffer = QBuffer()
                    buffer.setData(QByteArray(image_data))
                    buffer.open(QIODevice.ReadOnly)
                    request.reply(mime_type.encode(), buffer)
                    print("ImageSchemeHandler: Successfully replied with image data")
                else:
                    print(f"ImageSchemeHandler: Image ID {image_id} not found")
                    request.fail(QWebEngineUrlRequestJob.UrlNotFound)
            except (ValueError, TypeError) as e:
                print(f"ImageSchemeHandler: Invalid URL format: {e}")
                request.fail(QWebEngineUrlRequestJob.UrlInvalid)
        else:
            print(f"ImageSchemeHandler: Non-image scheme: {url.scheme()}")
            request.fail(QWebEngineUrlRequestJob.UrlInvalid)
    
    def _detect_image_mime_type(self, image_data: bytes) -> str:
        """Detect MIME type from image data"""
        if image_data.startswith(b'\x89PNG'):
            return "image/png"
        elif image_data.startswith(b'\xff\xd8\xff'):
            return "image/jpeg"
        elif image_data.startswith(b'GIF87a') or image_data.startswith(b'GIF89a'):
            return "image/gif"
        elif image_data.startswith(b'RIFF') and b'WEBP' in image_data[:12]:
            return "image/webp"
        else:
            return "image/png"  # Default fallback


class PreviewWidget(QWidget):
    def __init__(self, image_handler=None):
        super().__init__()
        self.image_handler = image_handler
        self._updating_scroll = False  # Flag to prevent scroll loops
        self._html_cache = {}  # Cache for rendered HTML content
        self._cache_max_size = 200  # Increased cache size for better performance
        self._cache_hit_count = 0  # Track cache performance
        self._cache_miss_count = 0
        self._last_content_hash = None  # Track last rendered content
        self._current_theme = 'dark'  # Default theme
        self._cache_access_times = {}  # Track access times for LRU eviction
        self._render_queue = []  # Queue for batched rendering
        self._render_timer = None  # Timer for debounced rendering
        self._precompiled_css = {}  # Cache for precompiled CSS themes
        
        # Incremental parsing optimization
        self._last_markdown_content = ""  # Track last content for diffing
        self._block_cache = {}  # Cache for individual markdown blocks
        self._block_separator = "\n\n"  # Markdown block separator
        self._incremental_threshold = 5000  # Use incremental parsing for docs > 5KB
        
        # Scroll position preservation
        self._saved_scroll_position = 0  # Store scroll position before update
        self._restore_scroll_pending = False  # Flag to restore scroll after load
        
        self.setup_ui()
        self.setup_markdown()
        self.setup_render_timer()
    
    def setup_ui(self):
        """Setup the preview UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create web view
        self.web_view = QWebEngineView()
        
        # Configure web engine profile to allow external content
        profile = self.web_view.page().profile()
        
        # Set custom scheme handler for images
        if self.image_handler:
            handler = ImageSchemeHandler(self.image_handler)
            profile.installUrlSchemeHandler(b"image", handler)
        
        # Enable loading of external images and resources
        from PySide6.QtWebEngineCore import QWebEngineSettings
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.AutoLoadImages, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        
        # Connect to load finished signal to restore scroll position
        self.web_view.loadFinished.connect(self._on_load_finished)
        
        layout.addWidget(self.web_view)
    
    def setup_render_timer(self):
        """Setup timer for batched rendering to improve performance"""
        from PySide6.QtCore import QTimer
        self._render_timer = QTimer()
        self._render_timer.setSingleShot(True)
        self._render_timer.timeout.connect(self._process_render_queue)
        self._render_timer.setInterval(100)  # 100ms debounce for better performance
    
    def setup_markdown(self):
        """Setup markdown processor with extensions"""
        self.md = markdown.Markdown(
            extensions=[
                'codehilite',
                'fenced_code',
                'tables',
                'toc',
                'nl2br'
            ],
            extension_configs={
                'codehilite': {
                    'css_class': 'highlight',
                    'use_pygments': True
                }
            }
        )
    
    def update_content(self, markdown_content: str):
        """Update the preview with enhanced caching and batched rendering"""
        # Add to render queue for batched processing
        self._render_queue.append(markdown_content)
        
        # Start/restart the render timer
        if self._render_timer:
            self._render_timer.start()
    
    def _process_render_queue(self):
        """Process the render queue with optimized batching and incremental parsing"""
        if not self._render_queue:
            return
        
        # Get the latest content from queue (discard intermediate updates)
        markdown_content = self._render_queue[-1]
        self._render_queue.clear()
        
        # Generate cache key from content hash and theme
        content_key = f"{markdown_content}_{self._current_theme}"
        content_hash = hashlib.md5(content_key.encode('utf-8')).hexdigest()
        
        # Skip update if content and theme haven't changed
        if content_hash == self._last_content_hash:
            return
        
        self._last_content_hash = content_hash
        
        # Save current scroll position before updating
        self._save_scroll_position()
        
        # Check cache first with LRU tracking
        if content_hash in self._html_cache:
            full_html = self._html_cache[content_hash]
            self._cache_hit_count += 1
            self._update_cache_access_time(content_hash)
        else:
            self._cache_miss_count += 1
            
            # Replace image:// URLs with data URLs before processing markdown
            if self.image_handler:
                processed_content = self._replace_image_urls(markdown_content)
            else:
                processed_content = markdown_content
            
            # Use incremental parsing for large documents
            if len(processed_content) > self._incremental_threshold:
                html_content = self._incremental_parse(processed_content)
            else:
                # Reset markdown processor to clear any state
                self.md.reset()
                html_content = self.md.convert(processed_content)
            
            # Wrap in complete HTML document with optimized styling
            full_html = self._create_html_document_optimized(html_content)
            
            # Cache the result with LRU management
            self._cache_html_lru(content_hash, full_html)
        
        # Store for theme switching
        self._last_markdown_content = markdown_content
        
        # Mark that we need to restore scroll position after load
        self._restore_scroll_pending = True
        
        # Use setHtml with a base URL to allow external content
        from PySide6.QtCore import QUrl
        base_url = QUrl("https://localhost/")
        self.web_view.setHtml(full_html, base_url)
    
    def _update_cache_access_time(self, cache_key: str):
        """Update access time for LRU cache management"""
        from datetime import datetime
        self._cache_access_times[cache_key] = datetime.now()
    
    def _incremental_parse(self, markdown_content: str) -> str:
        """Parse markdown incrementally by caching individual blocks"""
        # Split content into blocks (paragraphs, code blocks, etc.)
        blocks = self._split_into_blocks(markdown_content)
        
        html_parts = []
        for block in blocks:
            block_hash = hashlib.md5(block.encode('utf-8')).hexdigest()
            
            # Check block cache
            if block_hash in self._block_cache:
                html_parts.append(self._block_cache[block_hash])
            else:
                # Parse only this block
                self.md.reset()
                block_html = self.md.convert(block)
                
                # Cache the block
                self._block_cache[block_hash] = block_html
                html_parts.append(block_html)
                
                # Limit block cache size
                if len(self._block_cache) > 500:
                    self._evict_block_cache()
        
        return '\n'.join(html_parts)
    
    def _split_into_blocks(self, content: str) -> list:
        """Split markdown content into cacheable blocks"""
        blocks = []
        current_block = []
        in_code_block = False
        
        lines = content.split('\n')
        for line in lines:
            # Detect code block boundaries
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                current_block.append(line)
                if not in_code_block:
                    # End of code block
                    blocks.append('\n'.join(current_block))
                    current_block = []
                continue
            
            if in_code_block:
                current_block.append(line)
            else:
                # Split on empty lines (paragraph boundaries)
                if line.strip() == '':
                    if current_block:
                        blocks.append('\n'.join(current_block))
                        current_block = []
                else:
                    current_block.append(line)
        
        # Add remaining content
        if current_block:
            blocks.append('\n'.join(current_block))
        
        return blocks
    
    def _evict_block_cache(self):
        """Evict oldest entries from block cache"""
        # Remove oldest 25% of entries
        entries_to_remove = len(self._block_cache) // 4
        cache_keys = list(self._block_cache.keys())
        for key in cache_keys[:entries_to_remove]:
            del self._block_cache[key]
    
    def _create_html_document_optimized(self, content: str) -> str:
        """Create HTML document with optimized CSS caching"""
        # Check if CSS is already compiled for this theme
        if self._current_theme not in self._precompiled_css:
            theme_css = PreviewThemes.get_theme(self._current_theme)
            self._precompiled_css[self._current_theme] = theme_css
        else:
            theme_css = self._precompiled_css[self._current_theme]
        
        return self._create_html_document_with_css(content, theme_css)
    
    def _create_html_document_with_css(self, content: str, theme_css: str) -> str:
        """Create HTML document with provided CSS (optimized version)"""
        # Inject scroll restoration script to prevent visible jump
        scroll_position = self._saved_scroll_position if self._restore_scroll_pending else 0
        
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="default-src 'self' data: https: http:; img-src 'self' data: https: http:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline';">
    <title>Markdown Preview</title>
    <style>
        {theme_css}
        
        /* Performance optimizations */
        * {{
            box-sizing: border-box;
        }}
        
        /* Prevent flash during scroll restoration */
        html {{
            {f'opacity: 0;' if scroll_position > 0 else ''}
        }}
        
        html.scroll-restored {{
            opacity: 1;
            transition: opacity 0.05s ease-in;
        }}
        
        body {{
            text-rendering: optimizeLegibility;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            contain: layout style paint;
        }}
        
        /* Optimized code block styling */
        .codehilite {{
            border-radius: 6px;
            margin: 16px 0;
            overflow-x: auto;
            position: relative;
            contain: layout style paint;
        }}
        
        .codehilite pre {{
            margin: 0;
            border: none;
            font-size: 0.9em;
            line-height: 1.4;
            will-change: scroll-position;
        }}
        
        /* Optimized image handling */
        img {{
            max-width: 100%;
            height: auto;
            will-change: auto;
            contain: layout style paint;
        }}
        
        /* Optimized table styling */
        table {{
            border-radius: 6px;
            overflow: hidden;
            contain: layout style paint;
        }}
        
        /* Performance improvements for large documents */
        @media (min-height: 1000px) {{
            body {{
                contain: layout style paint size;
            }}
        }}
    </style>
    <script>
        // Restore scroll position immediately on load to prevent flash
        (function() {{
            var savedPosition = {scroll_position};
            
            function restoreScroll() {{
                if (savedPosition > 0) {{
                    window.scrollTo(0, savedPosition);
                    // Show content after scroll is restored
                    document.documentElement.classList.add('scroll-restored');
                }} else {{
                    // No scroll to restore, show immediately
                    document.documentElement.classList.add('scroll-restored');
                }}
            }}
            
            // Restore as early as possible
            if (document.readyState === 'loading') {{
                document.addEventListener('DOMContentLoaded', restoreScroll);
            }} else {{
                restoreScroll();
            }}
            
            // Fallback: ensure content is visible after short delay
            setTimeout(function() {{
                document.documentElement.classList.add('scroll-restored');
            }}, 100);
        }})();
    </script>
</head>
<body>
    {content}
</body>
</html>"""
    
    def sync_scroll(self, scroll_percentage: float):
        """Synchronize scroll position with editor"""
        if self._updating_scroll:
            return
            
        self._updating_scroll = True
        
        # Use JavaScript to scroll the web view
        script = f"""
        var body = document.body;
        var html = document.documentElement;
        var height = Math.max(body.scrollHeight, body.offsetHeight, 
                             html.clientHeight, html.scrollHeight, html.offsetHeight);
        var scrollTop = (height - window.innerHeight) * {scroll_percentage};
        window.scrollTo(0, scrollTop);
        """
        
        self.web_view.page().runJavaScript(script, lambda result: setattr(self, '_updating_scroll', False))
    
    def _save_scroll_position(self):
        """Save current scroll position before content update"""
        script = """
        (function() {
            return window.pageYOffset || document.documentElement.scrollTop;
        })();
        """
        self.web_view.page().runJavaScript(script, self._on_scroll_position_saved)
    
    def _on_scroll_position_saved(self, position):
        """Callback when scroll position is retrieved"""
        if position is not None:
            self._saved_scroll_position = position
    
    def _on_load_finished(self, ok):
        """Handle load finished event"""
        if ok and self._restore_scroll_pending:
            self._restore_scroll_pending = False
            # Scroll position is already restored via inline script in HTML
            # This is just for cleanup and potential fallback
            if self._saved_scroll_position > 0:
                # Double-check scroll position as fallback
                script = f"""
                (function() {{
                    var currentScroll = window.pageYOffset || document.documentElement.scrollTop;
                    if (currentScroll === 0 && {self._saved_scroll_position} > 0) {{
                        window.scrollTo(0, {self._saved_scroll_position});
                    }}
                }})();
                """
                self.web_view.page().runJavaScript(script)
    
    def _replace_image_urls(self, markdown_content: str) -> str:
        """Replace image:// URLs with data URLs, leave online URLs unchanged"""
        import re
        import base64
        
        def replace_local_image_url(match):
            try:
                image_id = int(match.group(1))
                print(f"PreviewWidget: Converting image://{image_id} to data URL")
                
                result = self.image_handler.get_image_data(image_id)
                if result:
                    image_data = result
                    # Convert to base64 data URL
                    base64_data = base64.b64encode(image_data).decode('utf-8')
                    data_url = f"data:image/png;base64,{base64_data}"
                    print(f"PreviewWidget: Created data URL of length {len(data_url)}")
                    return data_url
                else:
                    print(f"PreviewWidget: Image {image_id} not found")
                    return match.group(0)  # Return original if not found
            except Exception as e:
                print(f"PreviewWidget: Error converting image URL: {e}")
                return match.group(0)  # Return original on error
        
        # Replace only image://ID with data URLs, leave http/https URLs unchanged
        pattern = r'image://(\d+)'
        result = re.sub(pattern, replace_local_image_url, markdown_content)
        return result
  
    def _create_html_document(self, content: str) -> str:
        """Create a complete HTML document with enhanced styling and theming"""
        theme_css = PreviewThemes.get_theme(self._current_theme)
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta http-equiv="Content-Security-Policy" content="default-src 'self' data: https: http:; img-src 'self' data: https: http:; style-src 'self' 'unsafe-inline';">
            <title>Markdown Preview</title>
            <style>
                {theme_css}
                
                /* Enhanced readability improvements */
                body {{
                    text-rendering: optimizeLegibility;
                    -webkit-font-smoothing: antialiased;
                    -moz-osx-font-smoothing: grayscale;
                }}
                
                /* Better spacing for readability */
                p + p {{
                    margin-top: 16px;
                }}
                
                /* Enhanced code block styling */
                .codehilite {{
                    border-radius: 6px;
                    margin: 16px 0;
                    overflow-x: auto;
                    position: relative;
                }}
                
                .codehilite pre {{
                    margin: 0;
                    border: none;
                    font-size: 0.9em;
                    line-height: 1.4;
                }}
                
                /* Syntax highlighting improvements */
                .codehilite .k {{ font-weight: bold; }} /* Keywords */
                .codehilite .s {{ font-style: italic; }} /* Strings */
                .codehilite .c {{ font-style: italic; opacity: 0.7; }} /* Comments */
                .codehilite .n {{ }} /* Names */
                .codehilite .o {{ font-weight: bold; }} /* Operators */
                
                /* Better table styling */
                table {{
                    border-radius: 6px;
                    overflow: hidden;
                }}
                
                /* Enhanced blockquote styling */
                blockquote p:last-child {{
                    margin-bottom: 0;
                }}
                
                /* Better list styling */
                ul ul, ol ol, ul ol, ol ul {{
                    margin-top: 0;
                    margin-bottom: 0;
                }}
                
                /* Definition lists */
                dl {{
                    margin: 16px 0;
                }}
                
                dt {{
                    font-weight: 600;
                    margin-top: 16px;
                }}
                
                dd {{
                    margin-left: 24px;
                    margin-bottom: 8px;
                }}
                
                /* Keyboard shortcuts styling */
                kbd {{
                    display: inline-block;
                    padding: 3px 5px;
                    font-size: 11px;
                    line-height: 10px;
                    vertical-align: middle;
                    border: solid 1px;
                    border-radius: 3px;
                    font-family: 'Consolas', 'Monaco', monospace;
                }}
                
                /* Mark/highlight text */
                mark {{
                    padding: 2px 4px;
                    border-radius: 3px;
                }}
                
                /* Footnotes */
                .footnote {{
                    font-size: 0.9em;
                    margin-top: 32px;
                    border-top: 1px solid;
                    padding-top: 16px;
                }}
                
                /* Math expressions */
                .math {{
                    font-family: 'Times New Roman', serif;
                }}
                
                /* Responsive images */
                @media (max-width: 768px) {{
                    body {{
                        padding: 12px;
                    }}
                    
                    table {{
                        font-size: 0.9em;
                    }}
                    
                    pre {{
                        padding: 12px;
                    }}
                }}
            </style>
        </head>
        <body>
            {content}
        </body>
        </html>
        """
    
    def _cache_html_lru(self, content_hash: str, html: str):
        """Cache HTML content with LRU management"""
        # If cache is full, remove LRU entries
        if len(self._html_cache) >= self._cache_max_size:
            self._evict_lru_html()
        
        self._html_cache[content_hash] = html
        self._update_cache_access_time(content_hash)
    
    def _evict_lru_html(self):
        """Evict least recently used HTML cache entries"""
        if not self._cache_access_times:
            # Fallback to removing oldest entries
            entries_to_remove = max(1, self._cache_max_size // 4)
            cache_keys = list(self._html_cache.keys())
            for key in cache_keys[:entries_to_remove]:
                del self._html_cache[key]
            return
        
        # Sort by access time and remove oldest 25%
        sorted_keys = sorted(self._cache_access_times.items(), key=lambda x: x[1])
        entries_to_remove = max(1, len(sorted_keys) // 4)
        
        for key, _ in sorted_keys[:entries_to_remove]:
            if key in self._html_cache:
                del self._html_cache[key]
            if key in self._cache_access_times:
                del self._cache_access_times[key]
    
    def get_cache_stats(self) -> dict:
        """Get cache performance statistics"""
        total_requests = self._cache_hit_count + self._cache_miss_count
        hit_rate = (self._cache_hit_count / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "cache_size": len(self._html_cache),
            "cache_max_size": self._cache_max_size,
            "cache_hits": self._cache_hit_count,
            "cache_misses": self._cache_miss_count,
            "hit_rate_percent": round(hit_rate, 2),
            "block_cache_size": len(self._block_cache),
            "incremental_threshold": self._incremental_threshold
        }
    
    def optimize_cache(self):
        """Optimize cache using LRU eviction"""
        if len(self._html_cache) > self._cache_max_size * 0.8:
            self._evict_lru_html()
        
        # Clean up orphaned access times
        valid_keys = set(self._html_cache.keys())
        orphaned_keys = set(self._cache_access_times.keys()) - valid_keys
        for key in orphaned_keys:
            del self._cache_access_times[key]
    
    def clear_cache(self):
        """Clear HTML cache and reset statistics"""
        self._html_cache.clear()
        self._cache_access_times.clear()
        self._precompiled_css.clear()
        self._render_queue.clear()
        self._block_cache.clear()
        self._cache_hit_count = 0
        self._cache_miss_count = 0
        self._last_content_hash = None
        self._last_markdown_content = ""
    
    def set_theme(self, theme_name: str):
        """Set the preview theme and refresh content with optimized cache handling"""
        if theme_name in PreviewThemes.get_available_themes():
            self._current_theme = theme_name
            # Precompile CSS for new theme
            if theme_name not in self._precompiled_css:
                self._precompiled_css[theme_name] = PreviewThemes.get_theme(theme_name)
            
            # Clear HTML cache but keep CSS cache
            self._html_cache.clear()
            self._cache_access_times.clear()
            self._last_content_hash = None
            
            # Trigger content refresh if we have content
            if hasattr(self, '_last_markdown_content'):
                self.update_content(self._last_markdown_content)
    
    def get_current_theme(self) -> str:
        """Get the current theme name"""
        return self._current_theme
    
    def get_available_themes(self) -> list:
        """Get list of available theme names"""
        return PreviewThemes.get_available_themes()
    
    def print_preview(self):
        """Trigger print dialog for the preview content"""
        self.web_view.page().triggerAction(self.web_view.page().WebAction.Print)
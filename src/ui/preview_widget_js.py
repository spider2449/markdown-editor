"""
JavaScript-based Preview Widget - HTML preview using JavaScript markdown parser
"""

import os
import sys
import base64
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import (QWebEngineUrlScheme, QWebEngineUrlSchemeHandler,
                                      QWebEngineProfile, QWebEngineUrlRequestJob, QWebEngineSettings)
from PySide6.QtCore import QUrl, QBuffer, QIODevice, QByteArray, QTimer

# Note: We don't need to register custom schemes for local file access
# Qt WebEngine can load local files directly


# No custom scheme handler needed - we'll embed JavaScript directly


class PreviewWidgetJS(QWidget):
    """JavaScript-based preview widget"""

    def __init__(self, image_handler=None):
        super().__init__()
        self.image_handler = image_handler
        self._current_theme = 'dark'
        self._last_markdown_content = ""
        self._page_loaded = False
        self._pending_updates = []
        self._update_timer = QTimer()
        self._update_timer.setSingleShot(True)
        self._update_timer.timeout.connect(self._process_pending_updates)
        self._update_timer.setInterval(100)  # 100ms debounce

        self.setup_ui()

    def setup_ui(self):
        """Setup the preview UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create web view
        self.web_view = QWebEngineView()

        # Enable necessary settings
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.AutoLoadImages, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, True)

        # Connect to load finished signal
        self.web_view.loadFinished.connect(self._on_load_finished)

        layout.addWidget(self.web_view)

        # Load the HTML template
        self._load_template()

    def _load_template(self):
        """Load the HTML template with embedded JavaScript"""
        template_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'preview_template_simple.html')
        renderer_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'preview_renderer.js')

        try:
            # Read template
            with open(template_path, 'r', encoding='utf-8') as f:
                html_content = f.read()

            # Read JavaScript renderer
            with open(renderer_path, 'r', encoding='utf-8') as f:
                js_content = f.read()

            # Embed JavaScript into template
            html_content = html_content.replace(
                '<!-- RENDERER_SCRIPT_PLACEHOLDER -->',
                f'<script>\n{js_content}\n</script>'
            )

            # Load HTML with base URL for external resources (CDN)
            base_url = QUrl("https://localhost/")
            self.web_view.setHtml(html_content, base_url)
            print("✓ Template loaded with embedded JavaScript")
        except Exception as e:
            print(f"✗ Error loading template: {e}")
            import traceback
            traceback.print_exc()
            self.web_view.setHtml(f"<html><body><p>Error loading template: {e}</p></body></html>")

    def _on_load_finished(self, ok):
        """Handle page load finished"""
        if ok:
            self._page_loaded = True
            print("Preview page loaded successfully")

            # Set initial theme
            self._apply_theme(self._current_theme)

            # Process any pending updates
            if self._pending_updates:
                self._process_pending_updates()
        else:
            print("Preview page failed to load")

    def update_content(self, markdown_content: str):
        """Update the preview with new markdown content"""
        self._last_markdown_content = markdown_content

        # Add to pending updates queue
        self._pending_updates.append(markdown_content)

        # Start/restart the update timer for debouncing
        self._update_timer.start()

    def _process_pending_updates(self):
        """Process pending content updates"""
        if not self._pending_updates:
            return

        # Get the latest content (discard intermediate updates)
        markdown_content = self._pending_updates[-1]
        self._pending_updates.clear()

        if not self._page_loaded:
            # Page not loaded yet, keep in queue
            self._pending_updates.append(markdown_content)
            return

        # Process image URLs to data URLs
        if self.image_handler:
            processed_content = self._replace_image_urls(markdown_content)
        else:
            processed_content = markdown_content

        # Escape content for JavaScript (handle special characters)
        escaped_content = (processed_content
                          .replace('\\', '\\\\')
                          .replace('`', '\\`')
                          .replace('$', '\\$')
                          .replace('\r\n', '\\n')
                          .replace('\n', '\\n')
                          .replace('\r', '\\n'))

        # Send update to JavaScript with fallback rendering
        script = f"""
        (function() {{
            if (typeof marked === 'undefined') {{
                document.getElementById('preview-content').innerHTML = '<p style="color: #ff6b6b;">⚠️ marked.js library not loaded. Check internet connection.</p>';
                return;
            }}
            
            if (window.markdownRenderer) {{
                window.markdownRenderer.updateContent(`{escaped_content}`);
            }} else {{
                // Fallback: render directly if renderer not initialized
                try {{
                    var html = marked.parse(`{escaped_content}`);
                    document.getElementById('preview-content').innerHTML = html;
                    
                    // Apply syntax highlighting
                    if (typeof hljs !== 'undefined') {{
                        document.querySelectorAll('pre code').forEach((block) => {{
                            hljs.highlightElement(block);
                        }});
                    }}
                }} catch (e) {{
                    console.error('Rendering error:', e);
                    document.getElementById('preview-content').innerHTML = '<p style="color: #ff6b6b;">Error rendering markdown: ' + e.message + '</p>';
                }}
            }}
        }})();
        """

        self.web_view.page().runJavaScript(script)

    def _replace_image_urls(self, markdown_content: str) -> str:
        """Replace image:// URLs with data URLs"""
        import re

        def replace_local_image_url(match):
            try:
                image_id = int(match.group(1))
                result = self.image_handler.get_image_data(image_id)

                if result:
                    image_data = result
                    # Convert to base64 data URL
                    base64_data = base64.b64encode(image_data).decode('utf-8')

                    # Detect image format
                    if image_data.startswith(b'\x89PNG'):
                        mime_type = 'image/png'
                    elif image_data.startswith(b'\xff\xd8\xff'):
                        mime_type = 'image/jpeg'
                    elif image_data.startswith(b'GIF'):
                        mime_type = 'image/gif'
                    else:
                        mime_type = 'image/png'

                    data_url = f"data:{mime_type};base64,{base64_data}"
                    return data_url
                else:
                    return match.group(0)
            except Exception as e:
                print(f"Error converting image URL: {e}")
                return match.group(0)

        # Replace only image://ID with data URLs
        pattern = r'image://(\d+)'
        result = re.sub(pattern, replace_local_image_url, markdown_content)
        return result

    def set_theme(self, theme_name: str):
        """Set the preview theme"""
        self._current_theme = theme_name
        self._apply_theme(theme_name)

        # Trigger content refresh
        if self._last_markdown_content:
            self.update_content(self._last_markdown_content)

    def _apply_theme(self, theme_name: str):
        """Apply theme via JavaScript"""
        if not self._page_loaded:
            return

        # Update highlight.js theme
        highlight_themes = {
            'dark': 'github-dark',
            'light': 'github',
            'sepia': 'github'
        }
        highlight_theme = highlight_themes.get(theme_name, 'github-dark')

        script = f"""
        // Update highlight.js theme
        var highlightLink = document.getElementById('highlight-theme');
        if (highlightLink) {{
            highlightLink.href = 'https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/styles/{highlight_theme}.min.css';
        }}

        // Update renderer theme
        if (window.markdownRenderer) {{
            window.markdownRenderer.setTheme('{theme_name}');
        }}
        """

        self.web_view.page().runJavaScript(script)

    def get_current_theme(self) -> str:
        """Get the current theme name"""
        return self._current_theme

    def get_available_themes(self) -> list:
        """Get list of available theme names"""
        return ['dark', 'light', 'sepia']

    def sync_scroll(self, scroll_percentage: float):
        """Synchronize scroll position with editor"""
        if not self._page_loaded:
            return

        script = f"""
        if (window.markdownRenderer) {{
            window.markdownRenderer.syncScroll({scroll_percentage});
        }}
        """

        self.web_view.page().runJavaScript(script)

    def clear_cache(self):
        """Clear the renderer cache"""
        if not self._page_loaded:
            return

        script = """
        if (window.markdownRenderer) {
            window.markdownRenderer.clearCache();
        }
        """

        self.web_view.page().runJavaScript(script)

    def get_cache_stats(self) -> dict:
        """Get cache performance statistics"""
        # This would need a callback mechanism to get data from JavaScript
        # For now, return a placeholder
        return {
            "cache_size": 0,
            "cache_max_size": 200,
            "cache_hits": 0,
            "cache_misses": 0,
            "hit_rate_percent": 0
        }

    def print_preview(self):
        """Trigger print dialog for the preview content"""
        if self._page_loaded:
            self.web_view.page().triggerAction(self.web_view.page().WebAction.Print)

"""
Preview themes for the markdown editor
Provides different styling themes for the preview panel
"""

class PreviewThemes:
    """Collection of CSS themes for the markdown preview"""
    
    @staticmethod
    def get_base_styles():
        """Common base styles used by all themes"""
        return """
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                line-height: 1.6;
                max-width: none;
                margin: 0;
                padding: 20px;
                word-wrap: break-word;
            }
            
            h1, h2, h3, h4, h5, h6 {
                margin-top: 24px;
                margin-bottom: 16px;
                font-weight: 600;
                line-height: 1.25;
            }
            
            h1 { font-size: 2em; }
            h2 { font-size: 1.5em; }
            h3 { font-size: 1.25em; }
            h4 { font-size: 1em; }
            h5 { font-size: 0.875em; }
            h6 { font-size: 0.85em; }
            
            p {
                margin-bottom: 16px;
            }
            
            code {
                padding: 2px 4px;
                border-radius: 3px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 0.9em;
            }
            
            pre {
                border-radius: 6px;
                padding: 16px;
                overflow-x: auto;
                line-height: 1.45;
                margin: 16px 0;
            }
            
            pre code {
                background-color: transparent;
                padding: 0;
                border-radius: 0;
            }
            
            blockquote {
                border-left: 4px solid;
                margin: 0 0 16px 0;
                padding-left: 16px;
                font-style: italic;
            }
            
            a {
                text-decoration: none;
            }
            
            a:hover {
                text-decoration: underline;
            }
            
            img {
                max-width: 100%;
                height: auto;
                border-radius: 6px;
                margin: 8px 0;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            }
            
            table {
                border-collapse: collapse;
                width: 100%;
                margin: 16px 0;
                border-spacing: 0;
            }
            
            th, td {
                padding: 8px 12px;
                text-align: left;
                border: 1px solid;
            }
            
            th {
                font-weight: 600;
            }
            
            ul, ol {
                padding-left: 24px;
                margin: 16px 0;
            }
            
            li {
                margin: 4px 0;
            }
            
            hr {
                border: none;
                height: 1px;
                margin: 24px 0;
            }
            
            .highlight {
                border-radius: 6px;
                margin: 16px 0;
            }
            
            /* Task list styling */
            ul.task-list {
                list-style: none;
                padding-left: 0;
            }
            
            ul.task-list li {
                position: relative;
                padding-left: 24px;
            }
            
            ul.task-list li input[type="checkbox"] {
                position: absolute;
                left: 0;
                top: 4px;
            }
        """
    
    @staticmethod
    def get_dark_theme():
        """Dark theme for preview panel"""
        return PreviewThemes.get_base_styles() + """
            body {
                color: #d4d4d4;
                background-color: #1e1e1e;
            }
            
            h1, h2, h3, h4, h5, h6 {
                color: #569cd6;
            }
            
            h1 { border-bottom: 1px solid #3c3c3c; padding-bottom: 8px; }
            h2 { border-bottom: 1px solid #3c3c3c; padding-bottom: 4px; }
            
            code {
                background-color: #2d2d2d;
                color: #ce9178;
            }
            
            pre {
                background-color: #2d2d2d;
                border: 1px solid #3c3c3c;
            }
            
            blockquote {
                border-left-color: #6a9955;
                color: #6a9955;
            }
            
            a {
                color: #4ec9b0;
            }
            
            th, td {
                border-color: #3c3c3c;
            }
            
            th {
                background-color: #2d2d2d;
            }
            
            tr:nth-child(even) {
                background-color: #252526;
            }
            
            hr {
                background-color: #3c3c3c;
            }
            
            .highlight {
                background-color: #2d2d2d;
            }
            
            /* Dark theme specific enhancements */
            kbd {
                background-color: #3c3c3c;
                color: #d4d4d4;
                border-color: #555555;
            }
            
            mark {
                background-color: #4a4a00;
                color: #ffff88;
            }
            
            .footnote {
                border-top-color: #3c3c3c;
            }
        """
    
    @staticmethod
    def get_light_theme():
        """Light theme for preview panel"""
        return PreviewThemes.get_base_styles() + """
            body {
                color: #24292e;
                background-color: #ffffff;
            }
            
            h1, h2, h3, h4, h5, h6 {
                color: #1f2328;
            }
            
            h1 { border-bottom: 1px solid #d0d7de; padding-bottom: 8px; }
            h2 { border-bottom: 1px solid #d0d7de; padding-bottom: 4px; }
            
            code {
                background-color: #f6f8fa;
                color: #d73a49;
            }
            
            pre {
                background-color: #f6f8fa;
                border: 1px solid #d0d7de;
            }
            
            blockquote {
                border-left-color: #d0d7de;
                color: #656d76;
            }
            
            a {
                color: #0969da;
            }
            
            th, td {
                border-color: #d0d7de;
            }
            
            th {
                background-color: #f6f8fa;
            }
            
            tr:nth-child(even) {
                background-color: #f6f8fa;
            }
            
            hr {
                background-color: #d0d7de;
            }
            
            .highlight {
                background-color: #f6f8fa;
            }
            
            /* Light theme specific enhancements */
            kbd {
                background-color: #f6f8fa;
                color: #24292e;
                border-color: #d0d7de;
            }
            
            mark {
                background-color: #fff3cd;
                color: #856404;
            }
            
            .footnote {
                border-top-color: #d0d7de;
            }
        """
    
    @staticmethod
    def get_sepia_theme():
        """Sepia theme for comfortable reading"""
        return PreviewThemes.get_base_styles() + """
            body {
                color: #5c4b37;
                background-color: #f4f1ea;
            }
            
            h1, h2, h3, h4, h5, h6 {
                color: #8b4513;
            }
            
            h1 { border-bottom: 1px solid #d2b48c; padding-bottom: 8px; }
            h2 { border-bottom: 1px solid #d2b48c; padding-bottom: 4px; }
            
            code {
                background-color: #ede0d3;
                color: #a0522d;
            }
            
            pre {
                background-color: #ede0d3;
                border: 1px solid #d2b48c;
            }
            
            blockquote {
                border-left-color: #cd853f;
                color: #8b7355;
            }
            
            a {
                color: #8b4513;
            }
            
            th, td {
                border-color: #d2b48c;
            }
            
            th {
                background-color: #ede0d3;
            }
            
            tr:nth-child(even) {
                background-color: #f5f0e8;
            }
            
            hr {
                background-color: #d2b48c;
            }
            
            .highlight {
                background-color: #ede0d3;
            }
            
            /* Sepia theme specific enhancements */
            kbd {
                background-color: #ede0d3;
                color: #5c4b37;
                border-color: #d2b48c;
            }
            
            mark {
                background-color: #f5deb3;
                color: #8b4513;
            }
            
            .footnote {
                border-top-color: #d2b48c;
            }
        """
    
    @staticmethod
    def get_print_styles():
        """Print-friendly styles"""
        return """
            @media print {
                body {
                    color: #000000 !important;
                    background-color: #ffffff !important;
                    font-size: 12pt;
                    line-height: 1.5;
                    margin: 0;
                    padding: 0;
                }
                
                h1, h2, h3, h4, h5, h6 {
                    color: #000000 !important;
                    page-break-after: avoid;
                    break-after: avoid;
                }
                
                h1 { font-size: 18pt; }
                h2 { font-size: 16pt; }
                h3 { font-size: 14pt; }
                h4 { font-size: 12pt; }
                h5 { font-size: 11pt; }
                h6 { font-size: 10pt; }
                
                p, li {
                    orphans: 3;
                    widows: 3;
                }
                
                blockquote {
                    border-left: 2pt solid #000000 !important;
                    color: #000000 !important;
                    page-break-inside: avoid;
                    break-inside: avoid;
                }
                
                pre, code {
                    background-color: #f5f5f5 !important;
                    color: #000000 !important;
                    border: 1pt solid #cccccc !important;
                    page-break-inside: avoid;
                    break-inside: avoid;
                }
                
                table {
                    page-break-inside: avoid;
                    break-inside: avoid;
                }
                
                th, td {
                    border: 1pt solid #000000 !important;
                    background-color: transparent !important;
                    color: #000000 !important;
                }
                
                th {
                    background-color: #f0f0f0 !important;
                }
                
                img {
                    max-width: 100% !important;
                    page-break-inside: avoid;
                    break-inside: avoid;
                }
                
                a {
                    color: #000000 !important;
                    text-decoration: underline !important;
                }
                
                a[href]:after {
                    content: " (" attr(href) ")";
                    font-size: 10pt;
                    color: #666666;
                }
                
                .highlight {
                    background-color: #f5f5f5 !important;
                    border: 1pt solid #cccccc !important;
                }
                
                /* Hide non-essential elements when printing */
                .no-print {
                    display: none !important;
                }
            }
        """
    
    @staticmethod
    def get_theme(theme_name: str) -> str:
        """Get a specific theme by name"""
        themes = {
            'dark': PreviewThemes.get_dark_theme,
            'light': PreviewThemes.get_light_theme,
            'sepia': PreviewThemes.get_sepia_theme
        }
        
        if theme_name in themes:
            return themes[theme_name]() + PreviewThemes.get_print_styles()
        else:
            return PreviewThemes.get_dark_theme() + PreviewThemes.get_print_styles()
    
    @staticmethod
    def get_available_themes() -> list:
        """Get list of available theme names"""
        return ['dark', 'light', 'sepia']
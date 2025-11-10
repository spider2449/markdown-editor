"""
Markdown Syntax Highlighter - Custom syntax highlighting for markdown text
"""

import re
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter, QTextDocument


class MarkdownHighlighter(QSyntaxHighlighter):
    def __init__(self, parent: QTextDocument = None, theme_manager=None):
        super().__init__(parent)
        self.theme_manager = theme_manager
        self.highlighting_rules = []
        self._setup_highlighting_rules()
    
    def _setup_highlighting_rules(self):
        """Setup syntax highlighting rules for markdown"""
        self.highlighting_rules.clear()
        
        # Get colors from theme manager or use defaults
        def get_color(element, default):
            if self.theme_manager:
                return QColor(self.theme_manager.get_syntax_color(element))
            return QColor(default)
        
        # Headers (# ## ### etc.)
        header_format = QTextCharFormat()
        header_format.setForeground(get_color('header', "#569cd6"))
        header_format.setFontWeight(QFont.Bold)
        self.highlighting_rules.append((
            re.compile(r'^#{1,6}\s.*$', re.MULTILINE),
            header_format
        ))
        
        # Bold text (**text** or __text__)
        bold_format = QTextCharFormat()
        bold_format.setFontWeight(QFont.Bold)
        bold_format.setForeground(get_color('bold', "#dcdcaa"))
        self.highlighting_rules.append((
            re.compile(r'\*\*([^*]+)\*\*'),
            bold_format
        ))
        self.highlighting_rules.append((
            re.compile(r'__([^_]+)__'),
            bold_format
        ))
        
        # Italic text (*text* or _text_)
        italic_format = QTextCharFormat()
        italic_format.setFontItalic(True)
        italic_format.setForeground(get_color('italic', "#ce9178"))
        self.highlighting_rules.append((
            re.compile(r'\*([^*]+)\*'),
            italic_format
        ))
        self.highlighting_rules.append((
            re.compile(r'_([^_]+)_'),
            italic_format
        ))
        
        # Code blocks (```code```)
        code_block_format = QTextCharFormat()
        code_block_format.setForeground(get_color('code', "#ce9178"))
        code_block_format.setFontFamily("Consolas")
        self.highlighting_rules.append((
            re.compile(r'```.*?```', re.DOTALL),
            code_block_format
        ))
        
        # Inline code (`code`)
        inline_code_format = QTextCharFormat()
        inline_code_format.setForeground(get_color('code', "#ce9178"))
        inline_code_format.setFontFamily("Consolas")
        self.highlighting_rules.append((
            re.compile(r'`([^`]+)`'),
            inline_code_format
        ))
        
        # Links [text](url)
        link_format = QTextCharFormat()
        link_format.setForeground(get_color('link', "#4ec9b0"))
        link_format.setUnderlineStyle(QTextCharFormat.SingleUnderline)
        self.highlighting_rules.append((
            re.compile(r'\[([^\]]+)\]\([^)]+\)'),
            link_format
        ))
        
        # Images ![alt](url)
        image_format = QTextCharFormat()
        image_format.setForeground(get_color('link', "#4ec9b0"))
        self.highlighting_rules.append((
            re.compile(r'!\[([^\]]*)\]\([^)]+\)'),
            image_format
        ))
        
        # Lists (- or * or +)
        list_format = QTextCharFormat()
        list_format.setForeground(get_color('list', "#c586c0"))
        self.highlighting_rules.append((
            re.compile(r'^[\s]*[-*+]\s', re.MULTILINE),
            list_format
        ))
        
        # Numbered lists (1. 2. etc.)
        numbered_list_format = QTextCharFormat()
        numbered_list_format.setForeground(get_color('list', "#c586c0"))
        self.highlighting_rules.append((
            re.compile(r'^[\s]*\d+\.\s', re.MULTILINE),
            numbered_list_format
        ))
        
        # Blockquotes (>)
        blockquote_format = QTextCharFormat()
        blockquote_format.setForeground(get_color('quote', "#6a9955"))
        blockquote_format.setFontItalic(True)
        self.highlighting_rules.append((
            re.compile(r'^>.*$', re.MULTILINE),
            blockquote_format
        ))
    
    def update_theme(self, theme_manager):
        """Update theme and refresh highlighting rules"""
        self.theme_manager = theme_manager
        self._setup_highlighting_rules()
        self.rehighlight()
    
    def highlightBlock(self, text: str):
        """Apply syntax highlighting to a block of text"""
        for pattern, format in self.highlighting_rules:
            for match in pattern.finditer(text):
                start = match.start()
                length = match.end() - start
                self.setFormat(start, length, format)
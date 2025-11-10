"""
Editor Themes - Theme management for the text editor
"""

from PySide6.QtGui import QColor, QFont, QPalette
from PySide6.QtCore import QObject, Signal
from typing import Dict, Any


class EditorTheme:
    """Represents an editor theme with colors and styling"""
    
    def __init__(self, name: str, **kwargs):
        self.name = name
        
        # Default theme values
        self.background = kwargs.get('background', '#1e1e1e')
        self.foreground = kwargs.get('foreground', '#d4d4d4')
        self.selection_background = kwargs.get('selection_background', '#264f78')
        self.selection_foreground = kwargs.get('selection_foreground', '#ffffff')
        self.current_line = kwargs.get('current_line', '#2a2d2e')
        self.line_numbers_background = kwargs.get('line_numbers_background', '#3c3c3c')
        self.line_numbers_foreground = kwargs.get('line_numbers_foreground', '#858585')
        
        # Font settings
        self.font_family = kwargs.get('font_family', 'Consolas')
        self.font_size = kwargs.get('font_size', 12)
        self.font_weight = kwargs.get('font_weight', 'normal')
        
        # Syntax highlighting colors
        self.syntax_colors = kwargs.get('syntax_colors', {
            'header': '#569cd6',
            'bold': '#dcdcaa',
            'italic': '#ce9178',
            'code': '#d7ba7d',
            'link': '#4ec9b0',
            'list': '#c586c0',
            'quote': '#6a9955',
            'comment': '#6a9955'
        })


class EditorThemeManager(QObject):
    """Manages editor themes and applies them to the editor"""
    
    theme_changed = Signal(str)  # Emits theme name when changed
    
    def __init__(self):
        super().__init__()
        self.themes = {}
        self.current_theme_name = "dark"
        self.setup_default_themes()
    
    def setup_default_themes(self):
        """Setup default editor themes"""
        
        # Dark theme (default)
        self.themes["dark"] = EditorTheme(
            name="Dark",
            background='#1e1e1e',
            foreground='#d4d4d4',
            selection_background='#264f78',
            selection_foreground='#ffffff',
            current_line='#2a2d2e',
            line_numbers_background='#3c3c3c',
            line_numbers_foreground='#858585',
            font_family='Consolas',
            font_size=12,
            syntax_colors={
                'header': '#569cd6',
                'bold': '#dcdcaa',
                'italic': '#ce9178',
                'code': '#d7ba7d',
                'link': '#4ec9b0',
                'list': '#c586c0',
                'quote': '#6a9955',
                'comment': '#6a9955'
            }
        )
        
        # Light theme
        self.themes["light"] = EditorTheme(
            name="Light",
            background='#ffffff',
            foreground='#000000',
            selection_background='#0078d4',
            selection_foreground='#ffffff',
            current_line='#f3f3f3',
            line_numbers_background='#f5f5f5',
            line_numbers_foreground='#666666',
            font_family='Consolas',
            font_size=12,
            syntax_colors={
                'header': '#0000ff',
                'bold': '#800000',
                'italic': '#008000',
                'code': '#a31515',
                'link': '#0000ee',
                'list': '#800080',
                'quote': '#008000',
                'comment': '#008000'
            }
        )
        
        # High contrast theme
        self.themes["high_contrast"] = EditorTheme(
            name="High Contrast",
            background='#000000',
            foreground='#ffffff',
            selection_background='#ffffff',
            selection_foreground='#000000',
            current_line='#333333',
            line_numbers_background='#1a1a1a',
            line_numbers_foreground='#ffffff',
            font_family='Consolas',
            font_size=12,
            syntax_colors={
                'header': '#00ffff',
                'bold': '#ffff00',
                'italic': '#00ff00',
                'code': '#ff00ff',
                'link': '#00ffff',
                'list': '#ffff00',
                'quote': '#00ff00',
                'comment': '#00ff00'
            }
        )
        
        # Monokai theme
        self.themes["monokai"] = EditorTheme(
            name="Monokai",
            background='#272822',
            foreground='#f8f8f2',
            selection_background='#49483e',
            selection_foreground='#f8f8f2',
            current_line='#3e3d32',
            line_numbers_background='#3c3c3c',
            line_numbers_foreground='#90908a',
            font_family='Consolas',
            font_size=12,
            syntax_colors={
                'header': '#66d9ef',
                'bold': '#f92672',
                'italic': '#fd971f',
                'code': '#e6db74',
                'link': '#a6e22e',
                'list': '#ae81ff',
                'quote': '#75715e',
                'comment': '#75715e'
            }
        )
        
        # Solarized Dark theme
        self.themes["solarized_dark"] = EditorTheme(
            name="Solarized Dark",
            background='#002b36',
            foreground='#839496',
            selection_background='#073642',
            selection_foreground='#93a1a1',
            current_line='#073642',
            line_numbers_background='#073642',
            line_numbers_foreground='#586e75',
            font_family='Consolas',
            font_size=12,
            syntax_colors={
                'header': '#268bd2',
                'bold': '#cb4b16',
                'italic': '#2aa198',
                'code': '#859900',
                'link': '#268bd2',
                'list': '#6c71c4',
                'quote': '#586e75',
                'comment': '#586e75'
            }
        )
    
    def get_theme_names(self) -> list:
        """Get list of available theme names"""
        return list(self.themes.keys())
    
    def get_theme(self, name: str) -> EditorTheme:
        """Get theme by name"""
        return self.themes.get(name, self.themes["dark"])
    
    def get_current_theme(self) -> EditorTheme:
        """Get current theme"""
        return self.themes[self.current_theme_name]
    
    def set_current_theme(self, name: str):
        """Set current theme"""
        if name in self.themes:
            self.current_theme_name = name
            self.theme_changed.emit(name)
    
    def apply_theme_to_editor(self, editor, line_number_widget=None):
        """Apply current theme to editor and line number widget"""
        theme = self.get_current_theme()
        
        # Apply editor styling
        editor.setStyleSheet(f"""
            QTextEdit {{
                background-color: {theme.background};
                color: {theme.foreground};
                selection-background-color: {theme.selection_background};
                selection-color: {theme.selection_foreground};
                border: 1px solid #3c3c3c;
                font-family: '{theme.font_family}';
                font-size: {theme.font_size}px;
                line-height: 1.4;
            }}
        """)
        
        # Apply font
        font = QFont(theme.font_family, theme.font_size)
        if theme.font_weight == 'bold':
            font.setBold(True)
        editor.setFont(font)
        
        # Update line number widget if provided
        if line_number_widget:
            line_number_widget.theme = theme
            line_number_widget.update()
    
    def get_syntax_color(self, element: str) -> str:
        """Get syntax highlighting color for an element"""
        theme = self.get_current_theme()
        return theme.syntax_colors.get(element, theme.foreground)
    
    def add_custom_theme(self, theme: EditorTheme):
        """Add a custom theme"""
        self.themes[theme.name.lower().replace(' ', '_')] = theme
    
    def export_theme(self, name: str) -> Dict[str, Any]:
        """Export theme as dictionary"""
        theme = self.get_theme(name)
        if not theme:
            return {}
        
        return {
            'name': theme.name,
            'background': theme.background,
            'foreground': theme.foreground,
            'selection_background': theme.selection_background,
            'selection_foreground': theme.selection_foreground,
            'current_line': theme.current_line,
            'line_numbers_background': theme.line_numbers_background,
            'line_numbers_foreground': theme.line_numbers_foreground,
            'font_family': theme.font_family,
            'font_size': theme.font_size,
            'font_weight': theme.font_weight,
            'syntax_colors': theme.syntax_colors
        }
    
    def import_theme(self, theme_data: Dict[str, Any]):
        """Import theme from dictionary"""
        if 'name' not in theme_data:
            return False
        
        theme = EditorTheme(**theme_data)
        self.add_custom_theme(theme)
        return True
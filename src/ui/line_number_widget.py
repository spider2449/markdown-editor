"""
Line Number Widget - Displays line numbers for the text editor
"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QPainter, QColor, QTextBlock


class LineNumberWidget(QWidget):
    """Widget that displays line numbers for a text editor"""
    
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
        self.theme = None  # Will be set by theme manager
        self.setup_widget()
    
    def setup_widget(self):
        """Setup the line number widget"""
        self.setFixedWidth(50)  # Initial width
        
        # Connect to editor document signals
        self.editor.document().blockCountChanged.connect(self.update_width)
        self.editor.document().blockCountChanged.connect(self.update)
        self.editor.verticalScrollBar().valueChanged.connect(self.update)
        self.editor.textChanged.connect(self.update)
        self.editor.cursorPositionChanged.connect(self.update)
        
        # Update initial width
        self.update_width()
    
    def update_width(self):
        """Update widget width based on number of lines"""
        # Calculate width needed for line numbers
        digits = len(str(max(1, self.editor.document().blockCount())))
        width = 15 + self.editor.fontMetrics().horizontalAdvance('9') * digits
        
        if self.width() != width:
            self.setFixedWidth(width)
            self.editor.setViewportMargins(width, 0, 0, 0)
    

    
    def paintEvent(self, event):
        """Paint the line numbers"""
        painter = QPainter(self)
        
        # Set background color from theme or default
        bg_color = QColor("#3c3c3c")
        text_color = QColor("#858585")
        
        if self.theme:
            bg_color = QColor(self.theme.line_numbers_background)
            text_color = QColor(self.theme.line_numbers_foreground)
        
        painter.fillRect(event.rect(), bg_color)
        
        # Set text color and font
        painter.setPen(text_color)
        painter.setFont(self.editor.font())
        
        # Get document and cursor
        document = self.editor.document()
        cursor = self.editor.cursorForPosition(self.editor.viewport().rect().topLeft())
        
        # Get the first visible block
        block = document.findBlock(cursor.position())
        block_number = block.blockNumber()
        
        # Get the geometry for the first visible block
        layout = block.layout()
        block_rect = layout.boundingRect()
        
        # Calculate the top position
        cursor.setPosition(block.position())
        rect = self.editor.cursorRect(cursor)
        top = rect.top()
        
        # Paint line numbers for visible blocks
        while block.isValid():
            # Get block geometry
            cursor.setPosition(block.position())
            rect = self.editor.cursorRect(cursor)
            
            # Check if block is visible
            if rect.top() > event.rect().bottom():
                break
            
            if rect.bottom() >= event.rect().top():
                number = str(block_number + 1)
                painter.drawText(
                    0, rect.top(),
                    self.width() - 5, rect.height(),
                    Qt.AlignRight | Qt.AlignVCenter, number
                )
            
            # Move to next block
            block = block.next()
            block_number += 1
        
        painter.end()
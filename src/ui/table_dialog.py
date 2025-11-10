"""
Table Dialog - Dialog for creating custom tables
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QSpinBox, QPushButton, QFormLayout)
from PySide6.QtCore import Qt


class TableDialog(QDialog):
    """Dialog for creating custom markdown tables"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Insert Table")
        self.setModal(True)
        self.setFixedSize(300, 150)
        
        self.rows = 3
        self.cols = 3
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)
        
        # Form layout for inputs
        form_layout = QFormLayout()
        
        # Rows input
        self.rows_spinbox = QSpinBox()
        self.rows_spinbox.setMinimum(1)
        self.rows_spinbox.setMaximum(20)
        self.rows_spinbox.setValue(3)
        form_layout.addRow("Rows:", self.rows_spinbox)
        
        # Columns input
        self.cols_spinbox = QSpinBox()
        self.cols_spinbox.setMinimum(1)
        self.cols_spinbox.setMaximum(10)
        self.cols_spinbox.setValue(3)
        form_layout.addRow("Columns:", self.cols_spinbox)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setDefault(True)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def get_dimensions(self):
        """Get the selected table dimensions"""
        return self.rows_spinbox.value(), self.cols_spinbox.value()
    
    @staticmethod
    def get_table_dimensions(parent=None):
        """Static method to get table dimensions"""
        dialog = TableDialog(parent)
        if dialog.exec() == QDialog.Accepted:
            return dialog.get_dimensions()
        return None, None
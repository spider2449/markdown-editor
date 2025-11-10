"""
Settings Manager - Handles application settings and session state
"""

import json
import os
import logging
from typing import Optional, Dict, Any
from PySide6.QtCore import QSettings

logger = logging.getLogger(__name__)


class SettingsManager:
    def __init__(self, settings_file: str = "settings.json"):
        self.settings_file = settings_file
        self.qt_settings = QSettings("MarkdownEditor", "MarkdownEditor")
        self._settings = self._load_settings()
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    logger.info("Settings loaded successfully")
                    return settings
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
        
        # Return default settings
        return {
            "last_document_id": None,
            "window_geometry": None,
            "splitter_sizes": None,
            "recent_documents": [],
            "preview_theme": "dark",
            "editor_theme": "dark",
            "line_numbers_enabled": True,
            "editor_font_size": 12,
            "editor_font_family": "Consolas"
        }
    
    def _save_settings(self):
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self._settings, f, indent=2)
                logger.info("Settings saved successfully")
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
    
    def get_last_document_id(self) -> Optional[int]:
        """Get the last opened document ID"""
        return self._settings.get("last_document_id")
    
    def set_last_document_id(self, doc_id: int):
        """Set the last opened document ID"""
        self._settings["last_document_id"] = doc_id
        self._save_settings()
    
    def get_window_geometry(self) -> Optional[bytes]:
        """Get saved window geometry"""
        geometry_data = self._settings.get("window_geometry")
        if geometry_data:
            return bytes.fromhex(geometry_data)
        return None
    
    def set_window_geometry(self, geometry: bytes):
        """Save window geometry"""
        self._settings["window_geometry"] = geometry.hex()
        self._save_settings()
    
    def get_splitter_sizes(self) -> Optional[list]:
        """Get saved splitter sizes"""
        return self._settings.get("splitter_sizes")
    
    def set_splitter_sizes(self, sizes: list):
        """Save splitter sizes"""
        self._settings["splitter_sizes"] = sizes
        self._save_settings()
    
    def add_recent_document(self, doc_id: int, title: str):
        """Add a document to recent documents list"""
        recent = self._settings.get("recent_documents", [])
        
        # Remove if already exists
        recent = [doc for doc in recent if doc["id"] != doc_id]
        
        # Add to beginning
        recent.insert(0, {"id": doc_id, "title": title})
        
        # Keep only last 10
        recent = recent[:10]
        
        self._settings["recent_documents"] = recent
        self._save_settings()
    
    def get_recent_documents(self) -> list:
        """Get recent documents list"""
        return self._settings.get("recent_documents", [])
    
    def remove_recent_document(self, doc_id: int):
        """Remove a document from recent documents"""
        recent = self._settings.get("recent_documents", [])
        recent = [doc for doc in recent if doc["id"] != doc_id]
        self._settings["recent_documents"] = recent
        self._save_settings()
    
    def get_preview_theme(self) -> str:
        """Get the saved preview theme"""
        return self._settings.get("preview_theme", "dark")
    
    def set_preview_theme(self, theme_name: str):
        """Save the preview theme preference"""
        self._settings["preview_theme"] = theme_name
        self._save_settings()
    
    def get_editor_theme(self) -> str:
        """Get the saved editor theme"""
        return self._settings.get("editor_theme", "dark")
    
    def set_editor_theme(self, theme_name: str):
        """Save the editor theme preference"""
        self._settings["editor_theme"] = theme_name
        self._save_settings()
    
    def get_line_numbers_enabled(self) -> bool:
        """Get line numbers enabled setting"""
        return self._settings.get("line_numbers_enabled", True)
    
    def set_line_numbers_enabled(self, enabled: bool):
        """Save line numbers enabled setting"""
        self._settings["line_numbers_enabled"] = enabled
        self._save_settings()
    
    def get_editor_font_size(self) -> int:
        """Get editor font size"""
        return self._settings.get("editor_font_size", 12)
    
    def set_editor_font_size(self, size: int):
        """Save editor font size"""
        self._settings["editor_font_size"] = size
        self._save_settings()
    
    def get_editor_font_family(self) -> str:
        """Get editor font family"""
        return self._settings.get("editor_font_family", "Consolas")
    
    def set_editor_font_family(self, family: str):
        """Save editor font family"""
        self._settings["editor_font_family"] = family
        self._save_settings()
"""
Image Handler - Manages image pasting and storage functionality
"""

import uuid
import logging
from io import BytesIO
from PySide6.QtGui import QClipboard, QPixmap
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication
from .document_manager import DocumentManager

logger = logging.getLogger(__name__)


class ImageHandler(QObject):
    image_pasted = Signal(str)  # Emits markdown syntax for pasted image
    
    def __init__(self, document_manager: DocumentManager):
        super().__init__()
        self.document_manager = document_manager
        self.current_document_id = None
        self._compression_quality = 85  # JPEG compression quality for optimization
        self._max_image_size = (1920, 1080)  # Max dimensions for optimization
    
    def set_current_document(self, doc_id: int):
        """Set the current document ID for image associations"""
        self.current_document_id = doc_id
    
    def handle_paste(self) -> bool:
        """Handle paste operation, return True if image was pasted"""
        try:
            print("ImageHandler: handle_paste() called")
            clipboard = QApplication.clipboard()
            
            print(f"ImageHandler: Checking clipboard, hasImage: {clipboard.mimeData().hasImage()}")
            if clipboard.mimeData().hasImage():
                pixmap = clipboard.pixmap()
                print(f"ImageHandler: Got pixmap, isNull: {pixmap.isNull()}")
                if not pixmap.isNull():
                    self._store_and_insert_image(pixmap)
                    return True
            
            print("ImageHandler: No image found in clipboard")
            return False
        except Exception as e:
            print(f"ImageHandler: Exception in handle_paste: {e}")
            logger.error(f"Failed to handle paste operation: {e}")
            return False
    
    def _store_and_insert_image(self, pixmap: QPixmap):
        """Store optimized image in database and emit markdown syntax"""
        try:
            print(f"ImageHandler: _store_and_insert_image called, current_document_id: {self.current_document_id}")
            if self.current_document_id is None:
                print("ImageHandler: No current document set for image storage")
                logger.warning("No current document set for image storage")
                return
            
            # Optimize image size and quality for better performance
            optimized_pixmap = self._optimize_image(pixmap)
            
            # Convert pixmap to bytes with optimized format
            from PySide6.QtCore import QBuffer, QIODevice
            buffer = QBuffer()
            buffer.open(QIODevice.WriteOnly)
            
            # Use JPEG for photos (better compression) or PNG for graphics
            format_type = self._determine_optimal_format(optimized_pixmap)
            print(f"ImageHandler: Converting pixmap to {format_type} bytes")
            
            if format_type == 'JPEG':
                if not optimized_pixmap.save(buffer, 'JPEG', self._compression_quality):
                    raise RuntimeError("Failed to convert image to JPEG format")
            else:
                if not optimized_pixmap.save(buffer, 'PNG'):
                    raise RuntimeError("Failed to convert image to PNG format")
            
            image_data = buffer.data().data()
            print(f"ImageHandler: Converted to {len(image_data)} bytes (optimized from {pixmap.width()}x{pixmap.height()} to {optimized_pixmap.width()}x{optimized_pixmap.height()})")
            if not image_data:
                raise RuntimeError("Image data is empty")
            
            # Generate unique filename with appropriate extension
            extension = 'jpg' if format_type == 'JPEG' else 'png'
            filename = f"image_{uuid.uuid4().hex[:8]}.{extension}"
            print(f"ImageHandler: Generated filename: {filename}")
            
            # Store in database
            image_id = self.document_manager.store_image(
                self.current_document_id, filename, image_data
            )
            print(f"ImageHandler: Stored image with ID: {image_id}")
            
            # Generate markdown syntax
            markdown_syntax = f"![{filename}](image://{image_id})"
            print(f"ImageHandler: Generated markdown: {markdown_syntax}")
            
            # Emit signal with markdown syntax
            self.image_pasted.emit(markdown_syntax)
            print("ImageHandler: Emitted image_pasted signal")
            logger.info(f"Successfully stored and inserted optimized image {filename}")
            
        except Exception as e:
            print(f"ImageHandler: Exception in _store_and_insert_image: {e}")
            logger.error(f"Failed to store and insert image: {e}")
            raise
    
    def _optimize_image(self, pixmap: QPixmap) -> QPixmap:
        """Optimize image size and quality for better performance"""
        try:
            # Check if image needs resizing
            if (pixmap.width() > self._max_image_size[0] or 
                pixmap.height() > self._max_image_size[1]):
                
                # Calculate scaling to maintain aspect ratio
                from PySide6.QtCore import Qt
                scaled_pixmap = pixmap.scaled(
                    self._max_image_size[0], 
                    self._max_image_size[1], 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                logger.info(f"Resized image from {pixmap.width()}x{pixmap.height()} to {scaled_pixmap.width()}x{scaled_pixmap.height()}")
                return scaled_pixmap
            
            return pixmap
        except Exception as e:
            logger.error(f"Failed to optimize image: {e}")
            return pixmap  # Return original if optimization fails
    
    def _determine_optimal_format(self, pixmap: QPixmap) -> str:
        """Determine optimal image format based on content"""
        try:
            # Simple heuristic: use JPEG for larger images (likely photos)
            # and PNG for smaller images (likely graphics/screenshots)
            pixel_count = pixmap.width() * pixmap.height()
            
            # If image is large (> 500K pixels), use JPEG for better compression
            if pixel_count > 500000:
                return 'JPEG'
            else:
                return 'PNG'
        except Exception as e:
            logger.error(f"Failed to determine optimal format: {e}")
            return 'PNG'  # Default to PNG
    
    def get_image_data(self, image_id: int) -> bytes:
        """Get image data for preview rendering with decompression support"""
        try:
            result = self.document_manager.get_image(image_id)
            if result:
                image_data = result[1]  # Get image data
                # Decompress if needed
                return self.document_manager._decompress_image_data(image_data)
            return None
        except Exception as e:
            logger.error(f"Failed to get image data for ID {image_id}: {e}")
            return None
    
    def get_image_stats(self) -> dict:
        """Get image handling statistics"""
        cache_stats = self.document_manager.get_cache_stats()
        return {
            "image_cache_size": cache_stats.get("image_cache_size", 0),
            "image_cache_max": cache_stats.get("image_cache_max", 0),
            "compression_quality": self._compression_quality,
            "max_image_size": self._max_image_size
        }
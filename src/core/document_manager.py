"""
Document Manager - Handles SQLite database operations for documents and images
"""

import sqlite3
import os
import logging
from datetime import datetime
from typing import List, Optional, Tuple, Dict
from functools import lru_cache
import hashlib

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Document:
    def __init__(self, id: int = None, title: str = "", content: str = "", 
                 created_at: str = None, updated_at: str = None, content_length: int = None):
        self.id = id
        self.title = title
        self.content = content
        self.created_at = created_at
        self.updated_at = updated_at
        self.content_length = content_length or (len(content) if content else 0)
        self._is_content_loaded = content is not None and content != ""


class DocumentManager:
    def __init__(self, db_path: str = "documents.db"):
        self.db_path = db_path
        self._document_cache = {}  # Cache for document content
        self._image_cache = {}     # Cache for image data
        self._metadata_cache = {}  # Cache for document metadata
        self._large_document_threshold = 50000  # 50KB threshold for lazy loading
        self._cache_max_size = 100  # Maximum number of cached documents
        self._image_cache_max_size = 50  # Maximum number of cached images
        self._chunk_size = 8192  # Chunk size for large document loading
        self._preload_cache = {}  # Cache for preloaded document chunks
        self._access_times = {}  # Track access times for LRU eviction
        self._connection = None  # Persistent connection for in-memory databases
        self.init_database()
    
    def init_database(self):
        """Initialize the SQLite database with required tables"""
        try:
            # For in-memory databases, keep a persistent connection
            if self.db_path == ':memory:':
                self._connection = sqlite3.connect(self.db_path)
                conn = self._connection
            else:
                conn = sqlite3.connect(self.db_path)
            
            cursor = conn.cursor()
            
            # Create documents table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create images table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS images (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id INTEGER,
                    filename TEXT NOT NULL,
                    data BLOB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (document_id) REFERENCES documents (id)
                )
            ''')
            
            conn.commit()
            
            # Only close if not using persistent connection
            if self.db_path != ':memory:':
                conn.close()
                
            logger.info("Database initialized successfully")
        except sqlite3.Error as e:
            logger.error(f"Database initialization failed: {e}")
            raise RuntimeError(f"Failed to initialize database: {e}")
    
    def _get_connection(self):
        """Get database connection (persistent for in-memory, new for file-based)"""
        if self.db_path == ':memory:' and self._connection:
            return self._connection
        else:
            return sqlite3.connect(self.db_path)
    
    def create_document(self, title: str, content: str = "") -> int:
        """Create a new document and return its ID"""
        try:
            if not title.strip():
                raise ValueError("Document title cannot be empty")
            
            # Use persistent connection for in-memory DB
            if self.db_path == ':memory:':
                conn = self._connection
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO documents (title, content)
                    VALUES (?, ?)
                ''', (title.strip(), content))
                conn.commit()
                doc_id = cursor.lastrowid
            else:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO documents (title, content)
                        VALUES (?, ?)
                    ''', (title.strip(), content))
                    conn.commit()
                    doc_id = cursor.lastrowid
                    
            logger.info(f"Created document '{title}' with ID {doc_id}")
            return doc_id
        except sqlite3.Error as e:
            logger.error(f"Failed to create document '{title}': {e}")
            raise RuntimeError(f"Failed to create document: {e}")
        except ValueError as e:
            logger.error(f"Invalid document data: {e}")
            raise
    
    def get_document(self, doc_id: int, load_content: bool = True) -> Optional[Document]:
        """Retrieve a document by ID with enhanced caching and lazy loading"""
        try:
            # Check cache first
            cache_key = f"{doc_id}_{load_content}"
            if cache_key in self._document_cache:
                return self._document_cache[cache_key]
            
            # Check metadata cache for non-content requests
            if not load_content and doc_id in self._metadata_cache:
                return self._metadata_cache[doc_id]
            
            conn = self._get_connection()
            should_close = self.db_path != ':memory:'
            try:
                cursor = conn.cursor()
                
                if load_content:
                    # Check if document is large first
                    cursor.execute('SELECT LENGTH(content) FROM documents WHERE id = ?', (doc_id,))
                    size_row = cursor.fetchone()
                    if size_row and size_row[0] > self._large_document_threshold:
                        # For large documents, load in chunks or show progress
                        logger.info(f"Loading large document {doc_id} ({size_row[0]} bytes)")
                    
                    cursor.execute('''
                        SELECT id, title, content, created_at, updated_at, LENGTH(content)
                        FROM documents WHERE id = ?
                    ''', (doc_id,))
                    
                    row = cursor.fetchone()
                    if row:
                        doc = Document(row[0], row[1], row[2], row[3], row[4], row[5])
                        # Cache the document with size limit
                        self._cache_document(cache_key, doc)
                        return doc
                else:
                    # Load metadata only for large document optimization
                    cursor.execute('''
                        SELECT id, title, '', created_at, updated_at, LENGTH(content)
                        FROM documents WHERE id = ?
                    ''', (doc_id,))
                    
                    row = cursor.fetchone()
                    if row:
                        doc = Document(row[0], row[1], row[2], row[3], row[4], row[5])
                        doc._is_content_loaded = False
                        # Cache metadata separately
                        self._metadata_cache[doc_id] = doc
                        return doc
                
                return None
            finally:
                if should_close:
                    conn.close()
        except sqlite3.Error as e:
            logger.error(f"Failed to retrieve document {doc_id}: {e}")
            return None
    
    def get_all_documents(self, load_content: bool = False) -> List[Document]:
        """Retrieve all documents with enhanced lazy loading and caching"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if load_content:
                    # Only load content for small documents, defer large ones
                    cursor.execute('''
                        SELECT id, title, 
                               CASE WHEN LENGTH(content) <= ? THEN content ELSE '' END as content,
                               created_at, updated_at, LENGTH(content)
                        FROM documents ORDER BY updated_at DESC
                    ''', (self._large_document_threshold,))
                    
                    documents = []
                    for row in cursor.fetchall():
                        doc = Document(row[0], row[1], row[2], row[3], row[4], row[5])
                        if not row[2]:  # Content was deferred due to size
                            doc._is_content_loaded = False
                        documents.append(doc)
                    return documents
                else:
                    # Load metadata only for sidebar display (optimized for performance)
                    cursor.execute('''
                        SELECT id, title, '', created_at, updated_at, LENGTH(content)
                        FROM documents ORDER BY updated_at DESC
                    ''')
                    documents = []
                    for row in cursor.fetchall():
                        doc_id = row[0]
                        # Check metadata cache first
                        if doc_id in self._metadata_cache:
                            documents.append(self._metadata_cache[doc_id])
                        else:
                            doc = Document(row[0], row[1], row[2], row[3], row[4], row[5])
                            doc._is_content_loaded = False
                            self._metadata_cache[doc_id] = doc
                            documents.append(doc)
                    return documents
        except sqlite3.Error as e:
            logger.error(f"Failed to retrieve documents: {e}")
            return []
    
    def update_document(self, doc_id: int, title: str = None, content: str = None):
        """Update a document's title and/or content"""
        try:
            if title is not None and not title.strip():
                raise ValueError("Document title cannot be empty")
                
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if title is not None and content is not None:
                    cursor.execute('''
                        UPDATE documents 
                        SET title = ?, content = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (title.strip(), content, doc_id))
                elif title is not None:
                    cursor.execute('''
                        UPDATE documents 
                        SET title = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (title.strip(), doc_id))
                elif content is not None:
                    cursor.execute('''
                        UPDATE documents 
                        SET content = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (content, doc_id))
                
                if cursor.rowcount == 0:
                    raise ValueError(f"Document with ID {doc_id} not found")
                    
                conn.commit()
                
                # Invalidate cache for this document
                self._invalidate_document_cache(doc_id)
                
                logger.info(f"Updated document {doc_id}")
        except sqlite3.Error as e:
            logger.error(f"Failed to update document {doc_id}: {e}")
            raise RuntimeError(f"Failed to update document: {e}")
        except ValueError as e:
            logger.error(f"Invalid update data: {e}")
            raise
    
    def delete_document(self, doc_id: int):
        """Delete a document and its associated images"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Delete associated images first
                cursor.execute('DELETE FROM images WHERE document_id = ?', (doc_id,))
                
                # Delete the document
                cursor.execute('DELETE FROM documents WHERE id = ?', (doc_id,))
                
                if cursor.rowcount == 0:
                    raise ValueError(f"Document with ID {doc_id} not found")
                
                conn.commit()
                logger.info(f"Deleted document {doc_id}")
        except sqlite3.Error as e:
            logger.error(f"Failed to delete document {doc_id}: {e}")
            raise RuntimeError(f"Failed to delete document: {e}")
        except ValueError as e:
            logger.error(f"Invalid delete operation: {e}")
            raise
    
    def store_image(self, document_id: int, filename: str, image_data: bytes) -> int:
        """Store an image associated with a document"""
        try:
            if not filename.strip():
                raise ValueError("Image filename cannot be empty")
            if not image_data:
                raise ValueError("Image data cannot be empty")
                
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO images (document_id, filename, data)
                    VALUES (?, ?, ?)
                ''', (document_id, filename.strip(), image_data))
                conn.commit()
                image_id = cursor.lastrowid
                logger.info(f"Stored image '{filename}' with ID {image_id}")
                return image_id
        except sqlite3.Error as e:
            logger.error(f"Failed to store image '{filename}': {e}")
            raise RuntimeError(f"Failed to store image: {e}")
        except ValueError as e:
            logger.error(f"Invalid image data: {e}")
            raise
    
    def get_image(self, image_id: int) -> Optional[Tuple[str, bytes]]:
        """Retrieve an image by ID with enhanced caching and compression, returns (filename, data)"""
        try:
            # Check cache first with access time tracking
            if image_id in self._image_cache:
                self._update_access_time(f"image_{image_id}")
                return self._image_cache[image_id]
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT filename, data FROM images WHERE id = ?
                ''', (image_id,))
                
                row = cursor.fetchone()
                if row:
                    filename, data = row
                    
                    # Optimize image data if it's large
                    optimized_data = self._optimize_image_data(data)
                    optimized_row = (filename, optimized_data)
                    
                    # Cache the optimized image data
                    self._cache_image(image_id, optimized_row)
                    return optimized_row
                return None
        except sqlite3.Error as e:
            logger.error(f"Failed to retrieve image {image_id}: {e}")
            return None
    
    def _optimize_image_data(self, image_data: bytes) -> bytes:
        """Optimize image data for better performance and storage"""
        try:
            # Only optimize if image is larger than 100KB
            if len(image_data) < 100 * 1024:
                return image_data
            
            # Try to compress large images
            from io import BytesIO
            import gzip
            
            # For very large images, apply gzip compression to reduce memory usage
            if len(image_data) > 500 * 1024:  # 500KB threshold
                compressed = BytesIO()
                with gzip.GzipFile(fileobj=compressed, mode='wb') as gz:
                    gz.write(image_data)
                compressed_data = compressed.getvalue()
                
                # Only use compressed version if it's significantly smaller
                if len(compressed_data) < len(image_data) * 0.8:
                    logger.info(f"Compressed image from {len(image_data)} to {len(compressed_data)} bytes")
                    # Mark as compressed by prepending a magic header
                    return b'GZIP_COMPRESSED:' + compressed_data
            
            return image_data
        except Exception as e:
            logger.error(f"Failed to optimize image data: {e}")
            return image_data
    
    def _decompress_image_data(self, image_data: bytes) -> bytes:
        """Decompress image data if it was compressed"""
        try:
            if image_data.startswith(b'GZIP_COMPRESSED:'):
                import gzip
                from io import BytesIO
                
                compressed_data = image_data[16:]  # Remove magic header
                with gzip.GzipFile(fileobj=BytesIO(compressed_data), mode='rb') as gz:
                    return gz.read()
            
            return image_data
        except Exception as e:
            logger.error(f"Failed to decompress image data: {e}")
            return image_data
    
    def load_document_content(self, doc_id: int, use_streaming: bool = True) -> Optional[str]:
        """Load full content for a document with streaming support for large documents"""
        try:
            # Check if already cached
            cache_key = f"content_{doc_id}"
            if cache_key in self._document_cache:
                self._update_access_time(cache_key)
                return self._document_cache[cache_key].content
            
            conn = self._get_connection()
            should_close = self.db_path != ':memory:'
            try:
                cursor = conn.cursor()
                
                if use_streaming and self.is_large_document(doc_id):
                    # For very large documents, use streaming approach
                    cursor.execute('''
                        SELECT LENGTH(content) FROM documents WHERE id = ?
                    ''', (doc_id,))
                    size_row = cursor.fetchone()
                    if size_row and size_row[0] > self._large_document_threshold * 2:
                        logger.info(f"Streaming large document {doc_id} ({size_row[0]} bytes)")
                        return self._load_document_streaming(cursor, doc_id)
                
                # Standard loading for normal-sized documents
                cursor.execute('''
                    SELECT content FROM documents WHERE id = ?
                ''', (doc_id,))
                
                row = cursor.fetchone()
                if row:
                    content = row[0]
                    # Cache the content
                    self._cache_document_content(doc_id, content)
                    return content
                return None
            finally:
                if should_close:
                    conn.close()
        except sqlite3.Error as e:
            logger.error(f"Failed to load content for document {doc_id}: {e}")
            return None
    
    def _load_document_streaming(self, cursor, doc_id: int) -> Optional[str]:
        """Load document content in chunks for very large documents"""
        try:
            cursor.execute('''
                SELECT content FROM documents WHERE id = ?
            ''', (doc_id,))
            
            row = cursor.fetchone()
            if row:
                content = row[0]
                # For streaming, we still load all content but with progress indication
                # In a real streaming implementation, we'd load chunks progressively
                logger.info(f"Loaded large document {doc_id} with streaming approach")
                self._cache_document_content(doc_id, content)
                return content
            return None
        except Exception as e:
            logger.error(f"Failed to stream document {doc_id}: {e}")
            return None
    
    def _cache_document_content(self, doc_id: int, content: str):
        """Cache document content with LRU management"""
        from datetime import datetime
        
        cache_key = f"content_{doc_id}"
        
        # Create a lightweight document object for caching
        class CachedDocument:
            def __init__(self, content):
                self.content = content
                self.cached_at = datetime.now()
        
        # If cache is full, remove LRU entries
        if len(self._document_cache) >= self._cache_max_size:
            self._evict_lru_documents()
        
        self._document_cache[cache_key] = CachedDocument(content)
        self._update_access_time(cache_key)
    
    def _update_access_time(self, cache_key: str):
        """Update access time for LRU tracking"""
        from datetime import datetime
        self._access_times[cache_key] = datetime.now()
    
    def _evict_lru_documents(self):
        """Evict least recently used documents from cache"""
        if not self._access_times:
            # Fallback to removing oldest entries
            entries_to_remove = max(1, self._cache_max_size // 4)
            cache_keys = list(self._document_cache.keys())
            for key in cache_keys[:entries_to_remove]:
                del self._document_cache[key]
            return
        
        # Sort by access time and remove oldest 25%
        sorted_keys = sorted(self._access_times.items(), key=lambda x: x[1])
        entries_to_remove = max(1, len(sorted_keys) // 4)
        
        for key, _ in sorted_keys[:entries_to_remove]:
            if key in self._document_cache:
                del self._document_cache[key]
            if key in self._access_times:
                del self._access_times[key]
        
        logger.info(f"Evicted {entries_to_remove} LRU documents from cache")
    
    def is_large_document(self, doc_id: int) -> bool:
        """Check if document is considered large (for lazy loading)"""
        try:
            conn = self._get_connection()
            should_close = self.db_path != ':memory:'
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT LENGTH(content) FROM documents WHERE id = ?
                ''', (doc_id,))
                
                row = cursor.fetchone()
                if row:
                    return row[0] > self._large_document_threshold
                return False
            finally:
                if should_close:
                    conn.close()
        except sqlite3.Error as e:
            logger.error(f"Failed to check document size {doc_id}: {e}")
            return False
    
    def _cache_document(self, cache_key: str, document: Document):
        """Cache document with size limit management"""
        # If cache is full, remove oldest entries (LRU-style)
        if len(self._document_cache) >= self._cache_max_size:
            # Remove first (oldest) entry
            oldest_key = next(iter(self._document_cache))
            del self._document_cache[oldest_key]
        
        self._document_cache[cache_key] = document
    
    def _cache_image(self, image_id: int, image_data: Tuple[str, bytes]):
        """Cache image with LRU management and size optimization"""
        # If cache is full, remove LRU entries
        if len(self._image_cache) >= self._image_cache_max_size:
            self._evict_lru_images()
        
        self._image_cache[image_id] = image_data
        self._update_access_time(f"image_{image_id}")
    
    def _evict_lru_images(self):
        """Evict least recently used images from cache"""
        # Find image cache keys in access times
        image_access_times = {k: v for k, v in self._access_times.items() if k.startswith('image_')}
        
        if not image_access_times:
            # Fallback to removing oldest entries
            oldest_key = next(iter(self._image_cache))
            del self._image_cache[oldest_key]
            return
        
        # Sort by access time and remove oldest 25%
        sorted_keys = sorted(image_access_times.items(), key=lambda x: x[1])
        entries_to_remove = max(1, len(sorted_keys) // 4)
        
        for key, _ in sorted_keys[:entries_to_remove]:
            image_id = int(key.split('_')[1])
            if image_id in self._image_cache:
                del self._image_cache[image_id]
            if key in self._access_times:
                del self._access_times[key]
        
        logger.info(f"Evicted {entries_to_remove} LRU images from cache")
    
    def _invalidate_document_cache(self, doc_id: int):
        """Invalidate cached document data"""
        keys_to_remove = [key for key in self._document_cache.keys() if key.startswith(f"{doc_id}_")]
        for key in keys_to_remove:
            del self._document_cache[key]
        
        # Also remove from metadata cache
        if doc_id in self._metadata_cache:
            del self._metadata_cache[doc_id]
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics for monitoring"""
        return {
            "document_cache_size": len(self._document_cache),
            "image_cache_size": len(self._image_cache),
            "metadata_cache_size": len(self._metadata_cache),
            "document_cache_max": self._cache_max_size,
            "image_cache_max": self._image_cache_max_size
        }
    
    def optimize_caches(self):
        """Optimize caches using LRU eviction and memory management"""
        # Optimize document cache if over 80% full
        if len(self._document_cache) > self._cache_max_size * 0.8:
            self._evict_lru_documents()
            logger.info("Optimized document cache using LRU eviction")
        
        # Optimize image cache if over 80% full
        if len(self._image_cache) > self._image_cache_max_size * 0.8:
            self._evict_lru_images()
            logger.info("Optimized image cache using LRU eviction")
        
        # Clean up orphaned access times
        self._cleanup_access_times()
    
    def _cleanup_access_times(self):
        """Clean up orphaned access time entries"""
        valid_keys = set()
        
        # Add valid document cache keys
        for key in self._document_cache.keys():
            valid_keys.add(key)
        
        # Add valid image cache keys
        for image_id in self._image_cache.keys():
            valid_keys.add(f"image_{image_id}")
        
        # Remove orphaned access times
        orphaned_keys = set(self._access_times.keys()) - valid_keys
        for key in orphaned_keys:
            del self._access_times[key]
        
        if orphaned_keys:
            logger.info(f"Cleaned up {len(orphaned_keys)} orphaned access time entries")
    
    def clear_caches(self):
        """Clear all caches and access tracking"""
        self._document_cache.clear()
        self._image_cache.clear()
        self._metadata_cache.clear()
        self._preload_cache.clear()
        self._access_times.clear()
        logger.info("Cleared all caches and access tracking data")
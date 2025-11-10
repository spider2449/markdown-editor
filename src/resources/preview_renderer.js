/**
 * JavaScript-based Markdown Preview Renderer
 * Handles markdown parsing, syntax highlighting, and rendering
 */

class MarkdownPreviewRenderer {
    constructor() {
        this.currentTheme = 'dark';
        this.scrollPosition = 0;
        this.contentCache = new Map();
        this.maxCacheSize = 200;
        this.cacheHits = 0;
        this.cacheMisses = 0;
        
        // Initialize marked.js options
        if (typeof marked !== 'undefined') {
            marked.setOptions({
                breaks: true,
                gfm: true,
                tables: true,
                highlight: (code, lang) => {
                    if (typeof hljs !== 'undefined' && lang && hljs.getLanguage(lang)) {
                        try {
                            return hljs.highlight(code, { language: lang }).value;
                        } catch (e) {
                            console.error('Highlight error:', e);
                        }
                    }
                    return code;
                }
            });
        }
        
        // Setup message handler for Python communication
        this.setupMessageHandler();
    }
    
    setupMessageHandler() {
        // Listen for messages from Python
        window.addEventListener('message', (event) => {
            const data = event.data;
            
            if (data.action === 'updateContent') {
                this.updateContent(data.markdown);
            } else if (data.action === 'setTheme') {
                this.setTheme(data.theme);
            } else if (data.action === 'syncScroll') {
                this.syncScroll(data.percentage);
            } else if (data.action === 'clearCache') {
                this.clearCache();
            }
        });
    }
    
    updateContent(markdown) {
        // Save current scroll position
        this.saveScrollPosition();
        
        // Generate cache key
        const cacheKey = this.generateCacheKey(markdown);
        
        let html;
        if (this.contentCache.has(cacheKey)) {
            html = this.contentCache.get(cacheKey);
            this.cacheHits++;
        } else {
            // Parse markdown to HTML
            html = this.parseMarkdown(markdown);
            this.cacheContent(cacheKey, html);
            this.cacheMisses++;
        }
        
        // Update DOM
        const container = document.getElementById('preview-content');
        if (container) {
            container.innerHTML = html;
            
            // Apply syntax highlighting to code blocks
            this.highlightCodeBlocks();
            
            // Restore scroll position
            this.restoreScrollPosition();
        }
    }
    
    parseMarkdown(markdown) {
        if (typeof marked === 'undefined') {
            console.error('marked.js not loaded');
            return '<p>Error: Markdown parser not loaded</p>';
        }
        
        try {
            // Process image URLs
            const processedMarkdown = this.processImageUrls(markdown);
            
            // Parse markdown
            return marked.parse(processedMarkdown);
        } catch (e) {
            console.error('Markdown parsing error:', e);
            return `<p>Error parsing markdown: ${e.message}</p>`;
        }
    }
    
    processImageUrls(markdown) {
        // This will be called from Python with already processed data URLs
        // Just pass through for now
        return markdown;
    }
    
    highlightCodeBlocks() {
        if (typeof hljs === 'undefined') {
            return;
        }
        
        document.querySelectorAll('pre code').forEach((block) => {
            // Only highlight if not already highlighted
            if (!block.classList.contains('hljs')) {
                hljs.highlightElement(block);
            }
        });
    }
    
    setTheme(themeName) {
        this.currentTheme = themeName;
        document.body.className = `theme-${themeName}`;
        
        // Clear cache when theme changes
        this.contentCache.clear();
        
        // Notify Python that theme changed
        this.sendMessage({ action: 'themeChanged', theme: themeName });
    }
    
    syncScroll(percentage) {
        const body = document.body;
        const html = document.documentElement;
        const height = Math.max(
            body.scrollHeight,
            body.offsetHeight,
            html.clientHeight,
            html.scrollHeight,
            html.offsetHeight
        );
        const scrollTop = (height - window.innerHeight) * percentage;
        window.scrollTo(0, scrollTop);
    }
    
    saveScrollPosition() {
        this.scrollPosition = window.pageYOffset || document.documentElement.scrollTop;
    }
    
    restoreScrollPosition() {
        requestAnimationFrame(() => {
            window.scrollTo(0, this.scrollPosition);
        });
    }
    
    generateCacheKey(markdown) {
        // Simple hash function for cache key
        let hash = 0;
        const str = markdown + this.currentTheme;
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32bit integer
        }
        return hash.toString();
    }
    
    cacheContent(key, html) {
        // Implement LRU cache
        if (this.contentCache.size >= this.maxCacheSize) {
            // Remove oldest entry
            const firstKey = this.contentCache.keys().next().value;
            this.contentCache.delete(firstKey);
        }
        this.contentCache.set(key, html);
    }
    
    clearCache() {
        this.contentCache.clear();
        this.cacheHits = 0;
        this.cacheMisses = 0;
    }
    
    getCacheStats() {
        return {
            size: this.contentCache.size,
            maxSize: this.maxCacheSize,
            hits: this.cacheHits,
            misses: this.cacheMisses,
            hitRate: this.cacheHits + this.cacheMisses > 0 
                ? (this.cacheHits / (this.cacheHits + this.cacheMisses) * 100).toFixed(2)
                : 0
        };
    }
    
    sendMessage(data) {
        // Send message to Python via Qt bridge
        if (typeof qt !== 'undefined' && qt.webChannelTransport) {
            // Use Qt WebChannel if available
            console.log('Sending message to Python:', data);
        }
    }
}

// Initialize renderer when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.markdownRenderer = new MarkdownPreviewRenderer();
    console.log('Markdown Preview Renderer initialized');
});

// Also try immediate initialization if DOM is already loaded
if (document.readyState === 'loading') {
    // DOM is still loading, wait for DOMContentLoaded
} else {
    // DOM is already loaded, initialize immediately
    window.markdownRenderer = new MarkdownPreviewRenderer();
    console.log('Markdown Preview Renderer initialized (immediate)');
}

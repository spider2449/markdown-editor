# Preview Widget Optimization

## Overview

The preview widget has been optimized to avoid parsing all content on every update, significantly improving performance for large documents.

## Key Optimizations

### 1. Incremental Block Parsing

**What it does:**
- Splits markdown content into logical blocks (paragraphs, code blocks, headings)
- Caches each block's HTML output separately
- Only re-parses blocks that have changed

**Performance impact:**
- ~50-60% faster rendering for documents with minor edits
- Scales better with document size

**Threshold:**
- Enabled automatically for documents > 5KB
- Configurable via `_incremental_threshold` property

### 2. Block-Level Caching

**Implementation:**
- Each markdown block gets a unique hash
- Parsed HTML is cached per block (up to 500 blocks)
- LRU eviction when cache is full

**Benefits:**
- Typing in one paragraph doesn't re-parse the entire document
- Code blocks, tables, and other complex elements are cached
- Memory efficient with automatic cache management

### 3. Smart Block Splitting

**Algorithm:**
- Respects code block boundaries (```...```)
- Splits on paragraph boundaries (empty lines)
- Preserves markdown structure integrity

**Example:**
```markdown
## Heading 1          <- Block 1
Paragraph text        <- Block 2

```python           <- Block 3 (entire code block)
def foo():
    pass
```

Another paragraph    <- Block 4
```

## Performance Metrics

### Test Results (100 sections, ~10KB document)

- **First render (cold cache):** 0.371s
- **Second render (warm cache):** 0.159s
- **Improvement:** 57% faster
- **Block cache size:** 300 blocks

### Cache Statistics

Access via `preview.get_cache_stats()`:
```python
{
    "cache_size": 2,              # Full document cache
    "cache_max_size": 200,
    "cache_hits": 0,
    "cache_misses": 2,
    "hit_rate_percent": 0.0,
    "block_cache_size": 301,      # Individual block cache
    "incremental_threshold": 5000  # Bytes
}
```

## Configuration

### Adjust Incremental Threshold

```python
# In preview_widget.py __init__
self._incremental_threshold = 5000  # Default: 5KB

# Disable incremental parsing
self._incremental_threshold = float('inf')

# Always use incremental parsing
self._incremental_threshold = 0
```

### Adjust Block Cache Size

```python
# In _incremental_parse method
if len(self._block_cache) > 500:  # Default: 500 blocks
    self._evict_block_cache()
```

## How It Works

### Before Optimization
```
User types → Full document parse → HTML generation → Render
(Every keystroke re-parses entire document)
```

### After Optimization
```
User types → Detect changed blocks → Parse only changed blocks → 
Reuse cached blocks → Combine HTML → Render
(Only changed sections are re-parsed)
```

## Additional Optimizations Still Active

1. **Debounced rendering** (100ms delay)
2. **Full document caching** (200 documents)
3. **CSS precompilation** (per theme)
4. **LRU cache management**
5. **Batched render queue**
6. **Scroll position preservation** (maintains view position during updates)

## Scroll Position Preservation

### How It Works

The preview uses a multi-layered approach to prevent visible jumps:

1. **Save Phase**: Captures current scroll position before update
2. **Inject Phase**: Embeds scroll position directly into HTML
3. **Restore Phase**: Inline JavaScript restores position immediately on load
4. **Hide Phase**: CSS opacity prevents flash during restoration

### Benefits

- **Zero visible flash**: Content hidden until scroll is restored
- **Immediate restoration**: Inline script runs before page renders
- **Seamless editing**: Type anywhere without losing your place
- **Pixel-perfect**: Maintains exact scroll position

### Implementation

```python
# Scroll position injected into HTML
scroll_position = self._saved_scroll_position

# CSS hides content during restoration
html { opacity: 0; }  # Only when scroll > 0

# Inline JavaScript restores immediately
window.scrollTo(0, savedPosition);
document.documentElement.classList.add('scroll-restored');

# CSS shows content after restoration
html.scroll-restored { opacity: 1; }
```

This approach ensures the user never sees the top of the document during updates.

## Testing

Run the test suites:
```bash
# Test incremental parsing
python test_incremental_preview.py

# Test scroll preservation
python test_scroll_preservation.py
```

## Future Improvements

Potential enhancements:
- Viewport-based rendering (only render visible content)
- Diff-based updates (DOM patching instead of full HTML replacement)
- Web Worker for background parsing
- Streaming rendering for very large documents

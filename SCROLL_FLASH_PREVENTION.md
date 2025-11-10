# Scroll Flash Prevention

## Problem

When updating preview content, there's a brief moment where:
1. New HTML is loaded
2. Browser resets scroll to top (position 0)
3. JavaScript restores the saved position

This creates a **visible flash** where users briefly see the top of the document before it jumps back to their working position.

## Solution

A multi-layered approach that prevents any visible flash:

### Layer 1: Inline Script Injection

The scroll position is embedded directly into the HTML document:

```javascript
<script>
var savedPosition = 800;  // Injected from Python
window.scrollTo(0, savedPosition);
</script>
```

**Benefit**: Runs immediately, before page renders

### Layer 2: CSS Opacity Masking

Content is hidden during the brief restoration period:

```css
/* Hide content initially if scroll needs restoration */
html {
    opacity: 0;
}

/* Show content after scroll is restored */
html.scroll-restored {
    opacity: 1;
    transition: opacity 0.05s ease-in;
}
```

**Benefit**: User never sees the wrong scroll position

### Layer 3: Early Execution

Script runs at the earliest possible moment:

```javascript
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', restoreScroll);
} else {
    restoreScroll();  // Already loaded, run immediately
}
```

**Benefit**: Minimizes time content is hidden

### Layer 4: Fallback Timer

Ensures content is always visible:

```javascript
setTimeout(function() {
    document.documentElement.classList.add('scroll-restored');
}, 100);
```

**Benefit**: Prevents permanent hiding if something fails

## Technical Flow

```
User types in editor
    ↓
_save_scroll_position()
    ↓ (async JS call)
_on_scroll_position_saved(800)
    ↓
_saved_scroll_position = 800
    ↓
_process_render_queue()
    ↓
_create_html_document_with_css()
    ↓ (inject scroll_position = 800)
HTML with inline script:
    <style>html { opacity: 0; }</style>
    <script>
        window.scrollTo(0, 800);
        html.classList.add('scroll-restored');
    </script>
    ↓
web_view.setHtml(html)
    ↓
Browser loads HTML
    ↓
Inline script executes IMMEDIATELY
    ↓
Scroll restored BEFORE first paint
    ↓
CSS shows content (opacity: 1)
    ↓
User sees content at correct position
```

## Key Advantages

### 1. No Visible Flash
- Content hidden until scroll is correct
- User never sees wrong position
- Smooth, professional experience

### 2. Fast Restoration
- Inline script runs before external resources
- No network delay
- No async callback delay

### 3. Reliable
- Multiple fallback mechanisms
- Works even if timing is off
- Guaranteed to show content eventually

### 4. Performant
- No additional HTTP requests
- Minimal CSS overhead
- Single reflow/repaint

## Comparison: Before vs After

### Before (Callback-based)
```
Load HTML → Render at top → Wait for callback → Restore scroll
         ↑                                    ↑
    User sees top                    User sees jump
         └────────── VISIBLE FLASH ──────────┘
```

### After (Inline + CSS)
```
Load HTML → Execute inline script → Restore scroll → Show content
                                                   ↑
                              User sees correct position
                              └─── NO FLASH ───┘
```

## Browser Compatibility

Works with all modern browsers (Chromium-based QWebEngineView):

- ✓ CSS opacity transitions
- ✓ classList API
- ✓ DOMContentLoaded event
- ✓ window.scrollTo()
- ✓ Inline script execution

## Performance Impact

- **Memory**: +0 bytes (scroll position already stored)
- **CPU**: Negligible (simple CSS + JS)
- **Render time**: +0ms (no additional reflows)
- **User experience**: Significantly improved

## Edge Cases Handled

### First Load (No Scroll)
```python
scroll_position = 0
# CSS: html { } (no opacity rule)
# Script: Immediately adds 'scroll-restored' class
# Result: Content visible immediately
```

### Large Scroll Position
```python
scroll_position = 5000
# CSS: html { opacity: 0; }
# Script: window.scrollTo(0, 5000)
# Result: Content appears at position 5000
```

### Rapid Updates
```python
# Debounced rendering (100ms) prevents conflicts
# Only latest scroll position is used
# No race conditions
```

### Theme Changes
```python
# Scroll position preserved across theme switches
# CSS regenerated with correct opacity rules
# Seamless transition
```

## Testing

### Visual Test
1. Open large document
2. Scroll to middle
3. Edit content
4. Observe: No flash, position maintained

### Automated Test
```bash
python test_no_scroll_flash.py
```

Expected: Position remains stable during all load phases

## Configuration

### Adjust Fade-in Speed
```python
# In _create_html_document_with_css()
transition: opacity 0.05s ease-in;  # Default: 50ms
transition: opacity 0.1s ease-in;   # Slower: 100ms
transition: opacity 0s;             # Instant (no fade)
```

### Disable Flash Prevention
```python
# Remove opacity CSS (not recommended)
# Comment out in _create_html_document_with_css():
# html {{ opacity: 0; }}
```

### Adjust Fallback Timer
```python
# In inline script
setTimeout(function() {
    document.documentElement.classList.add('scroll-restored');
}, 100);  // Default: 100ms
```

## Future Enhancements

Potential improvements:
- Preserve horizontal scroll for wide content
- Smooth scroll animation on large position changes
- Remember scroll position per document ID
- Restore on app restart

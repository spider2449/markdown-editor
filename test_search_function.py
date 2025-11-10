"""
Test script for global document search
"""

import sys
from PySide6.QtWidgets import QApplication

# Add src to path
sys.path.insert(0, 'src')

from core.document_manager import DocumentManager
from ui.search_dialog import SearchDialog


def create_test_documents(doc_manager):
    """Create some test documents for searching"""
    print("Creating test documents...")
    
    # Document 1
    doc_manager.create_document(
        "Python Tutorial",
        """# Python Programming Guide

## Introduction
Python is a high-level programming language that is easy to learn.

## Variables
In Python, you can create variables without declaring their type:
```python
x = 5
name = "John"
```

## Functions
Functions in Python are defined using the def keyword:
```python
def greet(name):
    return f"Hello, {name}!"
```
"""
    )
    
    # Document 2
    doc_manager.create_document(
        "JavaScript Basics",
        """# JavaScript Guide

## Introduction
JavaScript is the programming language of the web.

## Variables
JavaScript has three ways to declare variables:
```javascript
var x = 5;
let name = "John";
const PI = 3.14;
```

## Functions
Functions can be declared in multiple ways:
```javascript
function greet(name) {
    return `Hello, ${name}!`;
}
```
"""
    )
    
    # Document 3
    doc_manager.create_document(
        "Meeting Notes",
        """# Team Meeting - 2024-01-15

## Attendees
- John Smith
- Jane Doe
- Bob Johnson

## Discussion Points
1. Project timeline review
2. Budget allocation
3. Resource planning

## Action Items
- John to prepare Python documentation
- Jane to review JavaScript code
- Bob to schedule follow-up meeting
"""
    )
    
    # Document 4
    doc_manager.create_document(
        "Recipe Collection",
        """# Favorite Recipes

## Chocolate Cake
A delicious chocolate cake recipe.

Ingredients:
- 2 cups flour
- 1 cup sugar
- 1/2 cup cocoa powder

## Pasta Carbonara
Classic Italian pasta dish.

Ingredients:
- 400g spaghetti
- 200g bacon
- 3 eggs
"""
    )
    
    print("✓ Created 4 test documents")


def test_search(doc_manager):
    """Test the search functionality"""
    print("\n" + "="*50)
    print("Testing Search Functionality")
    print("="*50)
    
    # Test 1: Search for "Python"
    print("\n1. Searching for 'Python':")
    results = doc_manager.search_documents("Python")
    print(f"   Found {len(results)} document(s)")
    for result in results:
        print(f"   - {result['title']}: {result['match_count']} match(es)")
    
    # Test 2: Search for "function"
    print("\n2. Searching for 'function' (case-insensitive):")
    results = doc_manager.search_documents("function", case_sensitive=False)
    print(f"   Found {len(results)} document(s)")
    for result in results:
        print(f"   - {result['title']}: {result['match_count']} match(es)")
        if result['content_matches']:
            print(f"     Context: {result['content_matches'][0][:80]}...")
    
    # Test 3: Search for "John"
    print("\n3. Searching for 'John':")
    results = doc_manager.search_documents("John")
    print(f"   Found {len(results)} document(s)")
    for result in results:
        print(f"   - {result['title']}: {result['match_count']} match(es)")
    
    # Test 4: Case-sensitive search
    print("\n4. Searching for 'javascript' (case-sensitive):")
    results = doc_manager.search_documents("javascript", case_sensitive=True)
    print(f"   Found {len(results)} document(s)")
    
    print("\n5. Searching for 'JavaScript' (case-sensitive):")
    results = doc_manager.search_documents("JavaScript", case_sensitive=True)
    print(f"   Found {len(results)} document(s)")


if __name__ == '__main__':
    # Test without GUI first
    print("Testing search functionality (no GUI)...")
    doc_manager = DocumentManager(":memory:")
    create_test_documents(doc_manager)
    test_search(doc_manager)
    
    # Now test with GUI
    print("\n" + "="*50)
    print("Opening Search Dialog GUI")
    print("="*50)
    print("\nInstructions:")
    print("1. Try searching for: Python, function, John, recipe")
    print("2. Test case-sensitive search")
    print("3. Double-click a result to see document selection")
    print("4. Expand document items to see match contexts")
    
    app = QApplication(sys.argv)
    
    dialog = SearchDialog(doc_manager)
    dialog.show_and_focus()
    
    sys.exit(app.exec())

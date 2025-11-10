#!/usr/bin/env python3
"""
Download JavaScript libraries for offline use
"""

import os
import urllib.request
import sys

def download_file(url, destination):
    """Download a file from URL to destination"""
    try:
        print(f"Downloading {os.path.basename(destination)}...")
        urllib.request.urlretrieve(url, destination)
        print(f"✓ Saved to {destination}")
        return True
    except Exception as e:
        print(f"✗ Error downloading {url}: {e}")
        return False

def main():
    # Create resources directory if it doesn't exist
    resources_dir = os.path.join('src', 'resources', 'js')
    os.makedirs(resources_dir, exist_ok=True)
    
    print("\n=== Downloading JavaScript Libraries for Offline Use ===\n")
    
    # Libraries to download
    libraries = [
        {
            'name': 'marked.js',
            'url': 'https://cdn.jsdelivr.net/npm/marked@11.0.0/marked.min.js',
            'file': 'marked.min.js'
        },
        {
            'name': 'highlight.js (core)',
            'url': 'https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/highlight.min.js',
            'file': 'highlight.min.js'
        },
        {
            'name': 'highlight.js (GitHub Dark theme)',
            'url': 'https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/styles/github-dark.min.css',
            'file': 'github-dark.min.css'
        },
        {
            'name': 'highlight.js (GitHub Light theme)',
            'url': 'https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/styles/github.min.css',
            'file': 'github.min.css'
        }
    ]
    
    # Language packs
    languages = [
        'python', 'javascript', 'typescript', 'java', 'cpp', 'csharp',
        'go', 'rust', 'sql', 'bash', 'json', 'xml', 'yaml', 'markdown'
    ]
    
    for lang in languages:
        libraries.append({
            'name': f'highlight.js ({lang})',
            'url': f'https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/languages/{lang}.min.js',
            'file': f'{lang}.min.js'
        })
    
    # Download all libraries
    success_count = 0
    fail_count = 0
    
    for lib in libraries:
        destination = os.path.join(resources_dir, lib['file'])
        if download_file(lib['url'], destination):
            success_count += 1
        else:
            fail_count += 1
    
    print(f"\n=== Download Complete ===")
    print(f"✓ Successfully downloaded: {success_count}")
    print(f"✗ Failed: {fail_count}")
    
    if success_count > 0:
        print(f"\nFiles saved to: {resources_dir}")
        print("\nNext steps:")
        print("1. Update src/resources/preview_template.html to use local files")
        print("2. Change CDN URLs to qrc:///js/filename.js")
        print("\nExample:")
        print("  <script src=\"qrc:///js/marked.min.js\"></script>")
        print("  <script src=\"qrc:///js/highlight.min.js\"></script>")
    
    return 0 if fail_count == 0 else 1

if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""
Simple test to verify the wine cellar app structure
"""

import os
import sys

def test_app_structure():
    """Test that all required files exist"""
    required_files = [
        'app.py',
        'models.py', 
        'wine_scraper.py',
        'requirements.txt',
        'templates/base.html',
        'templates/index.html', 
        'templates/add_wine.html',
        'templates/collection.html'
    ]
    
    print("Testing Wine Cellar App Structure")
    print("=" * 40)
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            print(f"✗ {file}")
            missing_files.append(file)
    
    print("\nSummary:")
    if missing_files:
        print(f"Missing files: {missing_files}")
        return False
    else:
        print("All required files present!")
        return True

def test_imports():
    """Test basic imports"""
    print("\nTesting Python Imports")
    print("=" * 40)
    
    try:
        # Test basic Python modules
        import sqlite3
        print("✓ sqlite3 (built-in)")
        
        import json
        print("✓ json (built-in)")
        
        import re
        print("✓ re (built-in)")
        
        # Note: Flask and other dependencies would need to be installed
        print("\nNote: Flask, SQLAlchemy, requests, and beautifulsoup4 need to be installed")
        print("Run: pip3 install flask sqlalchemy requests beautifulsoup4")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

if __name__ == "__main__":
    structure_ok = test_app_structure()
    imports_ok = test_imports()
    
    if structure_ok and imports_ok:
        print("\n🍷 Wine Cellar App appears ready for deployment!")
        print("\nNext steps:")
        print("1. Install dependencies: pip3 install -r requirements.txt")
        print("2. Run the app: python3 app.py")
        print("3. Open browser to: http://localhost:5000")
    else:
        print("\n❌ Issues found - please address before running")
        sys.exit(1)
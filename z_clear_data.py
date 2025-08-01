#!/usr/bin/env python3
"""
Script to clean up Python cache files and database files
"""

import os
import shutil
import glob

def clear_data():
    """Recursively delete all __pycache__ directories and .db files"""
    print("=== Cleaning up Python cache and database files ===")
    
    # Get current directory
    current_dir = os.getcwd()
    print(f"Cleaning directory: {current_dir}")
    
    # Find and remove __pycache__ directories
    print("\n1. Removing __pycache__ directories...")
    pycache_count = 0
    for root, dirs, files in os.walk(current_dir):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                pycache_path = os.path.join(root, dir_name)
                try:
                    shutil.rmtree(pycache_path)
                    print(f"   ✓ Removed: {pycache_path}")
                    pycache_count += 1
                except Exception as e:
                    print(f"   ✗ Failed to remove {pycache_path}: {e}")
    
    print(f"   Total __pycache__ directories removed: {pycache_count}")
    
    # Find and remove .db files
    print("\n2. Removing .db files...")
    db_count = 0
    for root, dirs, files in os.walk(current_dir):
        for file_name in files:
            if file_name.endswith('.db'):
                db_path = os.path.join(root, file_name)
                try:
                    os.remove(db_path)
                    print(f"   ✓ Removed: {db_path}")
                    db_count += 1
                except Exception as e:
                    print(f"   ✗ Failed to remove {db_path}: {e}")
    
    print(f"   Total .db files removed: {db_count}")
    
    # Also remove .pyc files (compiled Python files)
    print("\n3. Removing .pyc files...")
    pyc_count = 0
    for root, dirs, files in os.walk(current_dir):
        for file_name in files:
            if file_name.endswith('.pyc'):
                pyc_path = os.path.join(root, file_name)
                try:
                    os.remove(pyc_path)
                    print(f"   ✓ Removed: {pyc_path}")
                    pyc_count += 1
                except Exception as e:
                    print(f"   ✗ Failed to remove {pyc_path}: {e}")
    
    print(f"   Total .pyc files removed: {pyc_count}")
    
    # Summary
    total_removed = pycache_count + db_count + pyc_count
    print(f"\n=== Cleanup Complete ===")
    print(f"Total items removed: {total_removed}")
    print(f"  - __pycache__ directories: {pycache_count}")
    print(f"  - .db files: {db_count}")
    print(f"  - .pyc files: {pyc_count}")
    
    return total_removed

if __name__ == '__main__':
    clear_data() 
#!/usr/bin/env python3
"""
Script to fix common misspellings of "maintenance" in files and folder names.
"""

import os
import re
import sys
from pathlib import Path
import argparse

# Common misspellings of "maintenance"
MISSPELLINGS = [
    'maintanance',
    'maintanence', 
    'maintainance',
    'maintainence',
    'maintence',
    'maintenence',
    'maintanence',
    'maintaince',
    'maintenace'
]

CORRECT_SPELLING = 'maintenance'

def find_misspelled_files_and_folders(root_path, exclude_dirs=None):
    """Find files and folders with misspelled 'maintenance'."""
    misspelled_items = []
    
    if exclude_dirs is None:
        exclude_dirs = []
    
    for root, dirs, files in os.walk(root_path):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        # Check directory names
        for dir_name in dirs:
            for misspelling in MISSPELLINGS:
                if misspelling.lower() in dir_name.lower():
                    full_path = os.path.join(root, dir_name)
                    misspelled_items.append({
                        'type': 'directory',
                        'path': full_path,
                        'name': dir_name,
                        'misspelling': misspelling
                    })
                    break
        
        # Check file names
        for file_name in files:
            for misspelling in MISSPELLINGS:
                if misspelling.lower() in file_name.lower():
                    full_path = os.path.join(root, file_name)
                    misspelled_items.append({
                        'type': 'file',
                        'path': full_path,
                        'name': file_name,
                        'misspelling': misspelling
                    })
                    break
    
    return misspelled_items

def find_misspelled_content_in_files(root_path, exclude_dirs=None):
    """Find files containing misspelled 'maintenance' in their content."""
    files_with_misspellings = []
    
    if exclude_dirs is None:
        exclude_dirs = []
    
    # File extensions to check
    text_extensions = {
        '.txt', '.md', '.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', 
        '.scss', '.sass', '.json', '.xml', '.yaml', '.yml', '.ini', '.cfg',
        '.conf', '.sh', '.bash', '.zsh', '.fish', '.sql', '.r', '.java',
        '.cpp', '.c', '.h', '.hpp', '.cs', '.php', '.rb', '.go', '.rs',
        '.swift', '.kt', '.scala', '.clj', '.hs', '.ml', '.fs', '.vb',
        '.pl', '.pm', '.tcl', '.lua', '.dart', '.elm', '.ex', '.exs'
    }
    
    for root, dirs, files in os.walk(root_path):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file_name in files:
            file_path = os.path.join(root, file_name)
            file_ext = Path(file_name).suffix.lower()
            
            # Skip binary files and large files
            if file_ext not in text_extensions:
                continue
                
            try:
                # Check if file is text-based and not too large
                if os.path.getsize(file_path) > 10 * 1024 * 1024:  # Skip files > 10MB
                    continue
                    
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                misspellings_found = []
                for misspelling in MISSPELLINGS:
                    # Case-insensitive search
                    pattern = re.compile(re.escape(misspelling), re.IGNORECASE)
                    matches = pattern.findall(content)
                    if matches:
                        misspellings_found.append({
                            'misspelling': misspelling,
                            'count': len(matches)
                        })
                
                if misspellings_found:
                    files_with_misspellings.append({
                        'path': file_path,
                        'misspellings': misspellings_found
                    })
                    
            except (UnicodeDecodeError, PermissionError, OSError):
                # Skip files that can't be read as text
                continue
    
    return files_with_misspellings

def rename_file_or_folder(old_path, new_name):
    """Rename a file or folder."""
    try:
        new_path = os.path.join(os.path.dirname(old_path), new_name)
        os.rename(old_path, new_path)
        print(f"✅ Renamed: {old_path} -> {new_path}")
        return True
    except OSError as e:
        print(f"❌ Error renaming {old_path}: {e}")
        return False

def fix_file_content(file_path):
    """Fix misspellings in file content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Replace each misspelling with correct spelling
        for misspelling in MISSPELLINGS:
            # Case-insensitive replacement
            pattern = re.compile(re.escape(misspelling), re.IGNORECASE)
            content = pattern.sub(CORRECT_SPELLING, content)
        
        # Only write if content changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Fixed content in: {file_path}")
            return True
        else:
            print(f"ℹ️  No changes needed in: {file_path}")
            return False
            
    except (UnicodeDecodeError, PermissionError, OSError) as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Fix common misspellings of "maintenance"')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be changed without making changes')
    parser.add_argument('--path', default='.', 
                       help='Path to scan (default: current directory)')
    parser.add_argument('--exclude', nargs='*', default=['venv', '__pycache__', '.git'],
                       help='Directories to exclude (default: venv, __pycache__, .git)')
    
    args = parser.parse_args()
    
    root_path = Path(args.path).resolve()
    print(f"🔍 Scanning for misspellings in: {root_path}")
    print(f"📝 Correct spelling: '{CORRECT_SPELLING}'")
    print(f"🔤 Common misspellings: {', '.join(MISSPELLINGS)}")
    print("-" * 60)
    
    # Find misspelled files and folders
    print("📁 Checking file and folder names...")
    misspelled_items = find_misspelled_files_and_folders(root_path, args.exclude)
    
    if misspelled_items:
        print(f"\n📁 Found {len(misspelled_items)} items with misspelled names:")
        for item in misspelled_items:
            print(f"  {item['type'].title()}: {item['path']} (contains '{item['misspelling']}')")
        
        if not args.dry_run:
            print("\n🔄 Renaming files and folders...")
            for item in misspelled_items:
                old_name = item['name']
                new_name = old_name
                for misspelling in MISSPELLINGS:
                    if misspelling.lower() in old_name.lower():
                        # Preserve case
                        if misspelling.lower() == old_name.lower():
                            new_name = CORRECT_SPELLING
                        else:
                            # Handle mixed case
                            new_name = re.sub(
                                re.compile(re.escape(misspelling), re.IGNORECASE),
                                CORRECT_SPELLING,
                                old_name
                            )
                        break
                
                if new_name != old_name:
                    rename_file_or_folder(item['path'], new_name)
    else:
        print("✅ No files or folders with misspelled names found.")
    
    # Find files with misspelled content
    print("\n📄 Checking file contents...")
    files_with_misspellings = find_misspelled_content_in_files(root_path, args.exclude)
    
    if files_with_misspellings:
        print(f"\n📄 Found {len(files_with_misspellings)} files with misspelled content:")
        for file_info in files_with_misspellings:
            print(f"  {file_info['path']}")
            for misspelling_info in file_info['misspellings']:
                print(f"    - '{misspelling_info['misspelling']}': {misspelling_info['count']} occurrences")
        
        if not args.dry_run:
            print("\n🔄 Fixing file contents...")
            for file_info in files_with_misspellings:
                fix_file_content(file_info['path'])
    else:
        print("✅ No files with misspelled content found.")
    
    print("\n" + "=" * 60)
    if args.dry_run:
        print("🔍 Dry run completed. Use without --dry-run to apply changes.")
    else:
        print("✅ Maintenance spelling fix completed!")
    
    total_items = len(misspelled_items) + len(files_with_misspellings)
    if total_items > 0:
        print(f"📊 Summary: Processed {total_items} items")

if __name__ == "__main__":
    main()

# Maintenance Spelling Fix Script

This script automatically finds and fixes common misspellings of the word "maintenance" in your codebase.

## Features

- **File and Folder Names**: Detects and renames files/folders with misspelled "maintenance"
- **File Content**: Scans and fixes misspellings within file contents
- **Multiple Misspellings**: Handles various common misspellings:
  - `maintanance`
  - `maintanence`
  - `maintainance`
  - `maintainence`
  - `maintence`
  - `maintenence`
  - `maintaince`
  - `maintenace`

## Usage

### Basic Usage
```bash
# Fix misspellings in current directory
python3 fix_maintenance_spelling.py

# Fix misspellings in specific directory
python3 fix_maintenance_spelling.py --path /path/to/your/project
```

### Dry Run (Preview Changes)
```bash
# See what would be changed without making changes
python3 fix_maintenance_spelling.py --dry-run
```

### Exclude Directories
```bash
# Exclude specific directories (default: venv, __pycache__, .git)
python3 fix_maintenance_spelling.py --exclude node_modules dist build
```

### Full Example
```bash
# Preview changes in a specific directory, excluding multiple folders
python3 fix_maintenance_spelling.py --path /my/project --exclude venv node_modules dist --dry-run
```

## What It Does

1. **Scans File/Folder Names**: Recursively searches for files and folders containing misspelled "maintenance"
2. **Scans File Contents**: Reads text files and searches for misspellings within the content
3. **Preserves Case**: Maintains the original case when replacing (e.g., "MainTAnance" → "Maintenance")
4. **Safe Operations**: Only modifies files that actually contain misspellings
5. **Excludes Binary Files**: Automatically skips binary files and large files (>10MB)

## Supported File Types

The script scans these text file extensions:
- Code: `.py`, `.js`, `.ts`, `.jsx`, `.tsx`, `.html`, `.css`, `.scss`, `.sass`, `.json`, `.xml`, `.yaml`, `.yml`
- Scripts: `.sh`, `.bash`, `.zsh`, `.fish`, `.sql`
- Documentation: `.txt`, `.md`
- Configuration: `.ini`, `.cfg`, `.conf`
- And many more programming languages

## Safety Features

- **Dry Run Mode**: Always test with `--dry-run` first
- **Backup Recommended**: Consider backing up your project before running
- **Git Integration**: Works well with git repositories (excludes `.git` by default)
- **Error Handling**: Gracefully handles permission errors and unreadable files

## Example Output

```
🔍 Scanning for misspellings in: /home/user/project
📝 Correct spelling: 'maintenance'
🔤 Common misspellings: maintanance, maintanence, maintainance, maintainence, maintence, maintenence, maintanence, maintaince, maintenace
------------------------------------------------------------
📁 Checking file and folder names...
✅ No files or folders with misspelled names found.

📄 Checking file contents...
📄 Found 2 files with misspelled content:
  /home/user/project/src/maintenance.py
    - 'maintanance': 3 occurrences
  /home/user/project/docs/README.md
    - 'maintainance': 1 occurrences

🔄 Fixing file contents...
✅ Fixed content in: /home/user/project/src/maintenance.py
✅ Fixed content in: /home/user/project/docs/README.md

============================================================
✅ Maintenance spelling fix completed!
📊 Summary: Processed 2 items
```

## Requirements

- Python 3.6+
- No additional dependencies required (uses only standard library)

## Notes

- The script is safe to run multiple times
- It only modifies files that actually contain misspellings
- Always review changes in version control before committing

import subprocess
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / 'instance' / 'app.db'
VENV_PYTHON = BASE_DIR / 'venv' / 'bin' / 'python'
REQUIREMENTS = BASE_DIR / 'requirements.txt'
LOG_PATH = BASE_DIR / 'logs'
INSTANCE_PATH = BASE_DIR / 'instance'


def remove_subfiles(directory_path: Path) -> None:
    """
    Remove all files and subdirectories in the specified directory.
    
    Args:
        directory_path (Path): Path to the directory to clear
    """
    if not directory_path.exists():
        print(f"Directory {directory_path} does not exist, skipping.")
        return
    
    if not directory_path.is_dir():
        print(f"{directory_path} is not a directory, skipping.")
        return
    
    print(f"Clearing directory: {directory_path}")
    
    # Remove all files and subdirectories
    for item in directory_path.iterdir():
        if item.is_file():
            item.unlink()
            print(f"  Deleted file: {item.name}")
        elif item.is_dir():
            # Recursively remove subdirectories
            for subitem in item.rglob('*'):
                if subitem.is_file():
                    subitem.unlink()
                elif subitem.is_dir():
                    subitem.rmdir()
            item.rmdir()
            print(f"  Deleted directory: {item.name}")
    
    print(f"Successfully cleared {directory_path}")


def remove_pycache():
    """Remove all __pycache__ folders and .pyc files from the project"""
    print("Removing Python cache files...")
    
    # Find all __pycache__ directories
    pycache_dirs = list(BASE_DIR.rglob('__pycache__'))
    print(f"Found {len(pycache_dirs)} __pycache__ directories")
    
    for pycache_dir in pycache_dirs:
        try:
            # Remove all files in __pycache__ directory
            for file in pycache_dir.iterdir():
                if file.is_file():
                    file.unlink()
                    print(f"  Deleted cache file: {file.name}")
            
            # Remove the __pycache__ directory itself
            pycache_dir.rmdir()
            print(f"  Deleted __pycache__ directory: {pycache_dir}")
        except Exception as e:
            print(f"  Error removing {pycache_dir}: {e}")
    
    # Find and remove all .pyc files
    pyc_files = list(BASE_DIR.rglob('*.pyc'))
    print(f"Found {len(pyc_files)} .pyc files")
    
    for pyc_file in pyc_files:
        try:
            pyc_file.unlink()
            print(f"  Deleted .pyc file: {pyc_file}")
        except Exception as e:
            print(f"  Error removing {pyc_file}: {e}")
    
    # Find and remove all .pyo files (optimized Python files)
    pyo_files = list(BASE_DIR.rglob('*.pyo'))
    print(f"Found {len(pyo_files)} .pyo files")
    
    for pyo_file in pyo_files:
        try:
            pyo_file.unlink()
            print(f"  Deleted .pyo file: {pyo_file}")
        except Exception as e:
            print(f"  Error removing {pyo_file}: {e}")
    
    print("Python cache cleanup completed")


def delete_logs():
    """Remove all files in the logs directory"""
    remove_subfiles(LOG_PATH)


def delete_instance():
    """Remove all files in the instance directory"""
    remove_subfiles(INSTANCE_PATH)


def main():
    print("=== Starting cleanup process ===")
    remove_pycache()
    delete_logs()
    delete_instance()
    print("=== Cleanup process completed ===")
    #run_app()


if __name__ == '__main__':
    main() 
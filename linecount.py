import os
import pathlib

def count_lines_in_python_files_ignore_venv(directory):
    """
    Recursively counts the total number of lines in all Python files within a given directory,
    while specifically ignoring 'venv' and common hidden directories.

    Args:
        directory (str): The path to the starting directory.

    Returns:
        dict: A dictionary where keys are file paths and values are line counts.
    """
    total_lines_per_file = {}
    
    # Define directories to ignore
    ignore_dirs = {'venv', '.venv', '.git', '__pycache__', '.pytest_cache'}

    # os.walk generates file names in a directory tree.
    for root, dirs, files in os.walk(directory):
        
        # --- KEY MODIFICATION: Prune the list of directories to visit ---
        # Modify the 'dirs' list in place to prevent os.walk from descending into ignored folders.
        # This is a highly efficient way to skip entire subtrees.
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        for file_name in files:
            # Check if the file has a .py extension
            if file_name.endswith(".py"):
                file_path = os.path.join(root, file_name)
                try:
                    # Open the file and count the lines
                    with open(file_path, 'r', encoding='utf-8') as f:
                        line_count = sum(1 for line in f)
                    total_lines_per_file[file_path] = line_count
                except IOError as e:
                    print(f"Error reading file {file_path}: {e}")
                except UnicodeDecodeError as e:
                    print(f"Error decoding file {file_path} (not valid UTF-8 text): {e}")

    return total_lines_per_file

# --- Example Usage ---
# Use the current working directory ('.') or specify a path
project_root = 'app/buisness'
line_counts = count_lines_in_python_files_ignore_venv(project_root)

# Print the results
if line_counts:
    print(f"--- Line Counts for Python files in '{os.path.abspath(project_root)}' (ignoring venv) ---")
    total_project_lines = 0
    for file_path, count in line_counts.items():
        # print(f"{count:5d} lines | {file_path}") # Optional: uncomment to see per-file counts
        total_project_lines += count
    print("-" * 50)
    print(f"Total lines across all non-venv Python files: {total_project_lines}")
else:
    print(f"No Python files found (perhaps only venv exists in this dir): {project_root}")


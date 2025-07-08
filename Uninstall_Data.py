import os
import subprocess
import sys
import time
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'instance', 'app.db')
VENV_PYTHON = os.path.join(BASE_DIR, 'venv', 'bin', 'python')
REQUIREMENTS = os.path.join(BASE_DIR, 'requirements.txt')
LOG_PATH = os.path.join(BASE_DIR, 'logs')


def delete_logs():
    if os.path.exists(LOG_PATH):
        print(f"Deleting logs at {LOG_PATH}...")
        shutil.rmtree(LOG_PATH)
    else:
        print(f"No logs found at {LOG_PATH}, skipping delete.")

def delete_database():
    if os.path.exists(DB_PATH):
        print(f"Deleting database at {DB_PATH}...")
        os.remove(DB_PATH)
    else:
        print(f"No database found at {DB_PATH}, skipping delete.")

def install_dependencies():
    print("Installing dependencies...")
    subprocess.check_call([VENV_PYTHON, '-m', 'pip', 'install', '-r', REQUIREMENTS])

def initialize_database():
    print("Initializing database...")
    subprocess.check_call([VENV_PYTHON, 'run.py', 'init'])

def run_app():
    print("Starting Flask app...")
    subprocess.call([VENV_PYTHON, 'run.py'])

def main():
    delete_logs()
    delete_database()
    run_app()

if __name__ == '__main__':
    main() 
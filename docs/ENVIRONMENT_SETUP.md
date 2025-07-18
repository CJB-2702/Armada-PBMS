# Armada PBMS Environment Setup Guide

This guide explains how to set up your development environment for the Armada PBMS project using a simple `.bashrc` and `.envrc` configuration.

## Quick Setup

### 1. Install direnv
```bash
# Ubuntu/Debian
sudo apt install direnv

# macOS
brew install direnv
```

### 2. Add direnv to your shell
Add this line to your `~/.bashrc`:
```bash
eval "$(direnv hook bash)"
```

### 3. Allow the .envrc file
```bash
cd "Armada PBMS"
direnv allow
```

That's it! The environment will automatically activate when you enter the project directory.

## What the setup does

When you enter the project directory, `.envrc` automatically:
- Creates a virtual environment if it doesn't exist
- Activates the virtual environment
- Sets `python` as an alias for `python3`
- Sets up Flask environment variables
- Adds the project directory to `PYTHONPATH`

## Available Commands

Once the environment is activated, you can use:

```bash
# Install dependencies (first time only)
pip install -r requirements.txt
pip install -r requirements-test.txt

# Run tests
python -m pytest tests/
python run_tests.py

# Run the application
python run.py
```

## Troubleshooting

### If direnv isn't working
```bash
# Reload your shell configuration
source ~/.bashrc

# Or restart your terminal
```

### If virtual environment issues occur
```bash
# Remove and recreate the virtual environment
rm -rf venv
direnv reload
```

### If Python alias doesn't work
```bash
# Check if alias is set
alias python

# Should show: alias python='python3'
```

## Manual activation (if needed)

If you need to manually activate the environment:
```bash
source venv/bin/activate
alias python=python3
export PYTHONPATH="${PWD}:${PYTHONPATH}"
export FLASK_APP=run.py
export FLASK_ENV=development
``` 
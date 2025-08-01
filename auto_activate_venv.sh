#!/bin/bash
# Auto-activate virtual environment for asset_management project

# Check if we're in the asset_management directory and venv exists
if [[ "$PWD" == *"asset_management"* ]] && [ -d "venv" ]; then
    # Only activate if not already activated
    if [[ "$VIRTUAL_ENV" != *"asset_management/venv"* ]]; then
        source venv/bin/activate
        echo "✓ Virtual environment activated for asset_management"
    fi
fi 
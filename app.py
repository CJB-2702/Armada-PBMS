#!/usr/bin/env python3
"""
Run script for the Asset Management System
"""

from app import create_app
from app.build import build_database

app = create_app()

if __name__ == '__main__':
    print("Starting Asset Management System...")
    print("Phase 1A: Core Foundation Tables")
    print("Phase 1B: Core System Initialization")
    print("")
    
    # Build database first
    build_database()
    
    print("")
    print("Access the application at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000) 
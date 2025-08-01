#!/usr/bin/env python3
"""
Build-specific Flask app that doesn't automatically initialize data
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_build_app():
    """Create Flask app for building without automatic initialization"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = 'build-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///asset_management.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Import models to ensure they're registered (but don't create tables)
    # This imports all models through the build module
    import app.models.build
    
    return app 
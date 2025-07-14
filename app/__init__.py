from flask import Flask
from app.models import initialize_database_controlled
from app.routes import register_blueprints
from app.utils.logger import get_logger


def create_and_configure_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev'  # Change in production
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    return app

def create_app():
    app = create_and_configure_app()
    logger = get_logger()
    
    try:
        # Initialize database in controlled order
        logger.info("Starting controlled database initialization...")
        initialize_database_controlled(app)
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    
    register_blueprints(app)
    return app 
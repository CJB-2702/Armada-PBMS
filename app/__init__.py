from flask import Flask, render_template
from app.config import get_config
from app.models.BaseModels import initialize_base_models
from app.utils.migrations import run_migrations
from app.utils.logger import get_logger
from app.extensions import db

logger = get_logger()

def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    if config_name:
        from app.config import config
        app.config.from_object(config.get(config_name, config['default']))
    else:
        app.config.from_object(get_config())
    
    # Initialize logging
    logger.info(f"Starting application with config: {app.config.get('ENV', 'development')}")
    
    try:
        # Initialize extensions first
        from app.extensions import db
        from app.models.BaseModels import migrate, login_manager
        db.init_app(app)
        migrate.init_app(app, db)
        login_manager.init_app(app)
        
        # Configure login manager
        login_manager.login_view = 'auth.login'  # type: ignore
        login_manager.login_message = 'Please log in to access this page.'
        login_manager.login_message_category = 'info'
        
        logger.info("✓ Extensions initialized")
        
        # Run schema migrations first to fix any schema issues
        run_migrations(app)
        logger.info("✓ Schema migrations completed successfully")
        
        # Initialize BaseModels (database, initial data)
        initialize_base_models(app)
        logger.info("✓ BaseModels initialized successfully")
        
        # Register blueprints
        register_blueprints(app)
        logger.info("✓ Blueprints registered successfully")
        
        # Register error handlers
        register_error_handlers(app)
        logger.info("✓ Error handlers registered successfully")
        
        logger.info("✓ Application initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Application initialization failed: {e}")
        raise
    
    return app

def register_blueprints(app):
    """Register Flask blueprints"""
    from app.routes import main, events, assets, locations, users, auth
    
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(events.bp)
    app.register_blueprint(assets.bp)
    app.register_blueprint(locations.bp)
    app.register_blueprint(users.bp)

def register_error_handlers(app):
    """Register error handlers"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403 
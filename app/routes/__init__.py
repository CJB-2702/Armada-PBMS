def register_blueprints(app):
    """Register all blueprints with the Flask app"""
    from app.routes.assets import bp as assets_bp
    from app.routes.main import bp as main_bp
    from app.routes.users import bp as users_bp
    from app.routes.events import bp as events_bp
    from app.routes.locations import bp as locations_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(assets_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(locations_bp) 
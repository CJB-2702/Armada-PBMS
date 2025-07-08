from app.routes.assets import bp as assets_bp

def register_blueprints(app):
    app.register_blueprint(assets_bp) 
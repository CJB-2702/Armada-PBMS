from flask import Flask
from app.models.BaseModels import initialize_base_models
from app.models.Utility import initialize_utility_models
# from app.models.Assets import initialize_assets_models
# from app.models.Assets.AssetClasses import initialize_asset_classes
from app.routes import register_blueprints


def create_and_configure_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev'  # Change in production
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    return app

def create_app():
    app = create_and_configure_app()
    
    # Initialize models in explicit order
    initialize_base_models(app)
    initialize_utility_models(app)
    # initialize_assets_models(app)
    # initialize_asset_classes(app)
    
    register_blueprints(app)
    return app 
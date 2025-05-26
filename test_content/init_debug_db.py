from app import create_app, db
from app.models.load_default_model import load_all_default_data, print_all_debug

def init_debug_database():
    """Initialize the database with default data for development"""
    app = create_app()
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Load default data
        if load_all_default_data(debug=True):
            print_all_debug()
            print("Debug database initialized successfully!")
        else:
            print("Error initializing debug database!")

if __name__ == "__main__":
    init_debug_database() 
from flask import Blueprint, render_template
from app.utils.logger import get_logger

logger = get_logger()

# Create blueprint
bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Main application index page"""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering main index: {str(e)}")
        return "Error loading main page", 500

@bp.route('/dashboard')
def dashboard():
    """Main dashboard page"""
    try:
        return render_template('dashboard.html')
    except Exception as e:
        logger.error(f"Error rendering dashboard: {str(e)}")
        return "Error loading dashboard", 500 
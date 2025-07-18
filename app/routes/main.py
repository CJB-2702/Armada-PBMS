from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app.utils.logger import get_logger

logger = get_logger()

# Create blueprint
bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Main application index page"""
    return render_template('index.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard page - requires authentication"""
    return render_template('dashboard.html')

@bp.route('/.well-known/appspecific/com.chrome.devtools.json')
def chrome_devtools():
    """Handle Chrome DevTools Protocol request"""
    return jsonify({"error": "DevTools Protocol not supported"}), 404

#TODO remove this route later
@bp.route('/favicon.ico')
def favicon():
    return ""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from app.models.BaseModels.Users import User
from app.models.BaseModels.Event import Event
from app.extensions import db
from app.utils.logger import get_logger
import re

logger = get_logger()

bp = Blueprint('auth', __name__, url_prefix='/auth')

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_username(username):
    """Validate username format"""
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return re.match(pattern, username) is not None

def log_auth_event(action, user, success=True, extra_info=None):
    """Log authentication events"""
    status = 'Completed' if success else 'Failed'
    title = f"Authentication {action}: {user.username if user else 'Unknown'} (ID: {user.row_id if user else 'N/A'})"
    description = f"Authentication {action.lower()}.\nStatus: {status}"
    
    if user:
        description += f"\nUsername: {user.username}\nEmail: {user.email}"
    
    if extra_info:
        description += f"\n{extra_info}"
    
    event = Event(
        title=title,
        description=description,
        event_type='System',
        status=status,
        location_UID='SYSTEM',
        created_by=0  # SYSTEM user
    )
    db.session.add(event)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return "LOGIN: true"
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        if not username:
            flash('Username is required', 'error')
            return render_template('auth/login.html')
        
        # Special handling for admin user - auto-login without password
        if username.lower() == 'admin':
            user = User.get_by_username('admin')
            if user and user.can_login():
                login_user(user, remember=remember)
                log_auth_event("Login", user, success=True)
                db.session.commit()
                return "LOGIN: true"
            else:
                flash('Admin user not found or cannot login', 'error')
                return render_template('auth/login.html')
        
        # Regular user authentication
        if not password:
            flash('Password is required for non-admin users', 'error')
            return render_template('auth/login.html')
        
        user = User.authenticate(username, password)
        
        if user:
            login_user(user, remember=remember)
            log_auth_event("Login", user, success=True)
            db.session.commit()
            return "LOGIN: true"
        else:
            log_auth_event("Login", None, success=False, extra_info=f"Failed login for username: {username}")
            db.session.commit()
            flash('Invalid username or password', 'error')
            return "LOGIN: false"
    
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    """User logout"""
    username = current_user.username
    logout_user()
    session.clear()
    
    log_auth_event("Logout", current_user, success=True)
    db.session.commit()
    
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('auth.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        display_name = request.form.get('display_name')
        
        # Validation
        errors = []
        
        if not username or not email or not password or not confirm_password:
            errors.append('All fields are required')
        
        if username and not validate_username(username):
            errors.append('Username must be 3-20 characters long and contain only letters, numbers, and underscores')
        
        if email and not validate_email(email):
            errors.append('Please enter a valid email address')
        
        if password and len(password) < 8:
            errors.append('Password must be at least 8 characters long')
        
        if password and confirm_password and password != confirm_password:
            errors.append('Passwords do not match')
        
        # Check if username already exists
        if username and User.get_by_username(username):
            errors.append('Username already exists')
        
        # Check if email already exists
        if email and User.get_by_email(email):
            errors.append('Email already exists')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('auth/register.html')
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            display_name=display_name or username,
            password=password,
            created_by=0  # SYSTEM user
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        log_auth_event("Registration", new_user, success=True)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile management"""
    if request.method == 'POST':
        display_name = request.form.get('display_name')
        email = request.form.get('email')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        errors = []
        
        # Validate current password if changing password
        if new_password:
            if not current_password:
                errors.append('Current password is required to change password')
            elif not current_user.check_password(current_password):
                errors.append('Current password is incorrect')
            elif new_password != confirm_password:
                errors.append('New passwords do not match')
            elif len(new_password) < 8:
                errors.append('New password must be at least 8 characters long')
        
        # Validate email
        if email and not validate_email(email):
            errors.append('Please enter a valid email address')
        
        # Check if email is already taken by another user
        if email and email != current_user.email:
            existing_user = User.get_by_email(email)
            if existing_user:
                errors.append('Email already exists')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('auth/profile.html')
        
        # Update user
        current_user.display_name = display_name
        current_user.email = email
        
        if new_password:
            current_user.set_password(new_password)
        
        current_user.update(updated_by=current_user.row_id)
        db.session.commit()
        
        flash('Profile updated successfully', 'success')
        return redirect(url_for('auth.profile'))
    
    return render_template('auth/profile.html')

@bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password page"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        
        if not email:
            flash('Email is required', 'error')
            return render_template('auth/forgot_password.html')
        
        if not validate_email(email):
            flash('Please enter a valid email address', 'error')
            return render_template('auth/forgot_password.html')
        
        user = User.get_by_email(email)
        
        if user:
            log_auth_event("Password Reset Request", user, success=True)
            db.session.commit()
        
        flash('If an account with that email exists, a password reset link has been sent.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html')

@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password with token"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not new_password or not confirm_password:
            flash('All fields are required', 'error')
            return render_template('auth/reset_password.html')
        
        if new_password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('auth/reset_password.html')
        
        if len(new_password) < 8:
            flash('Password must be at least 8 characters long', 'error')
            return render_template('auth/reset_password.html')
        
        flash('Password reset successfully. Please log in with your new password.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html') 
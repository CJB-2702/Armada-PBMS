from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.BaseModels.Users import User
from app.models.BaseModels.Event import Event
from app.extensions import db
from app.utils.logger import get_logger

logger = get_logger()

# Create blueprint
bp = Blueprint('users', __name__, url_prefix='/users')

def log_user_event(action, user, extra_info=None):
    title = f"User {action}: {user.username} (ID: {user.row_id})"
    description = (
        f"User {action.lower()}.\n"
        f"Username: {user.username}\n"
        f"Display Name: {user.display_name}\n"
        f"Email: {user.email}\n"
        f"Role: {user.role}\n"
        f"Is Admin: {user.is_admin}"
    )
    if extra_info:
        description += f"\n{extra_info}"
    event = Event(
        title=title,
        description=description,
        event_type='SYSTEM',
        status='completed',
        created_by=current_user.row_id if current_user else 0
    )
    db.session.add(event)

@bp.route('/')
@login_required
def index():
    """Display all users"""
    # Only admins can view all users
    if not current_user.is_admin:
        flash('You do not have permission to view all users', 'error')
        return redirect(url_for('main.dashboard'))
    
    users = User.query.all()
    return render_template('users/index.html', users=users)

@bp.route('/<int:user_id>')
@login_required
def view_user(user_id):
    """Display a specific user's details"""
    # Users can only view their own profile unless they're admin
    if not current_user.is_admin and current_user.row_id != user_id:
        flash('You can only view your own profile', 'error')
        return redirect(url_for('auth.profile'))
    
    user = User.query.get_or_404(user_id)
    return render_template('users/view_user.html', user=user)

@bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    """Edit a specific user"""
    # Only admins can edit other users
    if not current_user.is_admin and current_user.row_id != user_id:
        flash('You can only edit your own profile', 'error')
        return redirect(url_for('auth.profile'))
    
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        display_name = request.form.get('display_name')
        email = request.form.get('email')
        role = request.form.get('role')
        is_admin = request.form.get('is_admin') == 'on'
        is_active = request.form.get('is_active') == 'on'
        
        # Validate required fields
        if not username or not display_name or not email:
            flash('All fields are required', 'error')
            return render_template('users/edit_user.html', user=user)
        
        # Check if username is already taken by another user
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.row_id != user_id:
            flash('Username already exists', 'error')
            return render_template('users/edit_user.html', user=user)
        
        # Check if email is already taken by another user
        existing_email = User.query.filter_by(email=email).first()
        if existing_email and existing_email.row_id != user_id:
            flash('Email already exists', 'error')
            return render_template('users/edit_user.html', user=user)
        
        # Update user
        user.username = username
        user.display_name = display_name
        user.email = email
        user.role = role
        user.is_admin = is_admin
        user.is_active = is_active
        
        # Update the updated_by field
        user.update(updated_by=current_user.row_id)
        
        db.session.commit()
        
        log_user_event("Edited", user)
        db.session.commit()
        flash('User updated successfully', 'success')
        return redirect(url_for('users.view_user', user_id=user_id))
    
    return render_template('users/edit_user.html', user=user)

@bp.route('/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    """Delete a user unless username is ADMIN or SYSTEM"""
    # Only admins can delete users
    if not current_user.is_admin:
        flash('Only administrators can delete users', 'error')
        return redirect(url_for('users.index'))
    
    user = User.query.get_or_404(user_id)
    if user.username.strip().lower() in ['admin', 'system']:
        flash('Cannot delete ADMIN or SYSTEM user.', 'error')
        return redirect(url_for('users.edit_user', user_id=user_id))
    
    if user.row_id == current_user.row_id:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('users.edit_user', user_id=user_id))
    
    db.session.delete(user)
    log_user_event("Deleted", user)
    db.session.commit()
    flash('User deleted successfully.', 'success')
    return redirect(url_for('users.index'))

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_user():
    """Create a new user"""
    # Only admins can create users
    if not current_user.is_admin:
        flash('Only administrators can create users', 'error')
        return redirect(url_for('users.index'))
    
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        display_name = request.form.get('display_name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'user')
        is_admin = request.form.get('is_admin') == 'on'
        
        # Validate required fields
        if not username or not display_name or not email or not password:
            flash('All fields are required', 'error')
            return render_template('users/create_user.html')
        
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('users/create_user.html')
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return render_template('users/create_user.html')
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            display_name=display_name,
            role=role,
            is_admin=is_admin,
            password=password,
            created_by=current_user.row_id
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        log_user_event("Created", new_user)
        db.session.commit()
        flash('User created successfully', 'success')
        return redirect(url_for('users.view_user', user_id=new_user.row_id))
    
    return render_template('users/create_user.html') 
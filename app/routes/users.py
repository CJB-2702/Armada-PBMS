from flask import Blueprint, render_template, request, redirect, url_for, flash
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
        created_by=1
    )
    db.session.add(event)

@bp.route('/')
def index():
    """Display all users"""
    try:
        users = User.query.all()
        return render_template('users/index.html', users=users)
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        flash('Error loading users', 'error')
        return render_template('users/index.html', users=[])

@bp.route('/<int:user_id>')
def view_user(user_id):
    """Display a specific user's details"""
    try:
        user = User.query.get_or_404(user_id)
        return render_template('users/view_user.html', user=user)
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {str(e)}")
        flash('Error loading user details', 'error')
        return redirect(url_for('users.index'))

@bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
def edit_user(user_id):
    """Edit a specific user"""
    try:
        user = User.query.get_or_404(user_id)
        
        if request.method == 'POST':
            # Get form data
            username = request.form.get('username')
            display_name = request.form.get('display_name')
            email = request.form.get('email')
            role = request.form.get('role')
            is_admin = request.form.get('is_admin') == 'on'
            
            # Validate required fields
            if not username or not display_name or not email:
                return render_template('users/edit_user.html', user=user, error='All fields are required')
            
            # Check if username is already taken by another user
            existing_user = User.query.filter_by(username=username).first()
            if existing_user and existing_user.row_id != user_id:
                return render_template('users/edit_user.html', user=user, error='Username already exists')
            
            # Check if email is already taken by another user
            existing_email = User.query.filter_by(email=email).first()
            if existing_email and existing_email.row_id != user_id:
                return render_template('users/edit_user.html', user=user, error='Email already exists')
            
            # Update user
            user.username = username
            user.display_name = display_name
            user.email = email
            user.role = role
            user.is_admin = is_admin
            
            # Update the updated_by field (you might want to get this from session)
            user.updated_by = 1  # Assuming admin user ID is 1
            
            db.session.commit()
            
            logger.info(f"User {user_id} updated by admin")
            log_user_event("Edited", user)
            db.session.commit()
            return redirect(url_for('users.view_user', user_id=user_id))
        
        return render_template('users/edit_user.html', user=user)
        
    except Exception as e:
        logger.error(f"Error editing user {user_id}: {str(e)}")
        flash('Error updating user', 'error')
        return redirect(url_for('users.index'))

@bp.route('/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    """Delete a user unless username is ADMIN or SYSTEM"""
    user = User.query.get_or_404(user_id)
    if user.username.strip().lower() in ['admin', 'system']:
        flash('Cannot delete ADMIN or SYSTEM user.', 'error')
        return redirect(url_for('users.edit_user', user_id=user_id))
    try:
        db.session.delete(user)
        log_user_event("Deleted", user)
        db.session.commit()
        logger.info(f"User {user.username} (ID: {user_id}) deleted.")
        flash('User deleted successfully.', 'success')
        return redirect(url_for('users.index'))
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {str(e)}")
        flash('Error deleting user.', 'error')
        return redirect(url_for('users.edit_user', user_id=user_id))

@bp.route('/create', methods=['GET', 'POST'])
def create_user():
    """Create a new user"""
    if request.method == 'POST':
        try:
            # Get form data
            username = request.form.get('username')
            display_name = request.form.get('display_name')
            email = request.form.get('email')
            role = request.form.get('role', 'user')
            is_admin = request.form.get('is_admin') == 'on'
            
            # Validate required fields
            if not username or not display_name or not email:
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
                created_by=1  # Assuming admin user ID is 1
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            logger.info(f"New user created: {username}")
            log_user_event("Created", new_user)
            db.session.commit()
            return redirect(url_for('users.view_user', user_id=new_user.row_id))
            
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            flash('Error creating user', 'error')
            return render_template('users/create_user.html')
    
    return render_template('users/create_user.html') 
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from app.models.BaseModels.Event import Event, EventTypes
from app.models.BaseModels.Locations import MajorLocation
from app.extensions import db
from app.utils.logger import get_logger
import re

logger = get_logger()

bp = Blueprint('events', __name__, url_prefix='/events')

def validate_event_data(title, description, event_type, status, location_UID):
    """Validate event data before saving"""
    errors = []
    
    if not title or not title.strip():
        errors.append("Title is required")
    elif len(title.strip()) > 255:
        errors.append("Title must be less than 255 characters")
    
    if description and len(description) > 65535:  # TEXT field limit
        errors.append("Description is too long")
    
    # Validate event type exists
    if event_type:
        event_type_obj = EventTypes.query.filter_by(value=event_type).first()
        if not event_type_obj:
            errors.append("Invalid event type")
    
    # Validate status
    valid_statuses = ['pending', 'in_progress', 'completed', 'cancelled']
    if status and status not in valid_statuses:
        errors.append("Invalid status")
    
    # Validate location exists
    if location_UID and location_UID != 'SYSTEM':
        location = MajorLocation.query.filter_by(UID=location_UID).first()
        if not location:
            errors.append("Invalid location")
    
    return errors

def sanitize_input(text):
    """Basic input sanitization"""
    if not text:
        return text
    # Remove potentially dangerous characters
    text = re.sub(r'[<>"\']', '', text)
    return text.strip()

@bp.route('/')
@login_required
def index():
    """Display all events"""
    events = Event.query.order_by(Event.created_at.desc()).all()
    return render_template('events/index.html', events=events)

@bp.route('/<int:event_id>')
@login_required
def view_event(event_id):
    """Display a specific event's details"""
    event = Event.query.get_or_404(event_id)
    return render_template('events/view_event.html', event=event)

@bp.route('/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    """Edit a specific event"""
    event = Event.query.get_or_404(event_id)
    event_types = EventTypes.query.all()
    locations = MajorLocation.query.all()
    
    if request.method == 'POST':
        # Get and sanitize form data
        title = sanitize_input(request.form.get('title'))
        description = sanitize_input(request.form.get('description'))
        event_type = request.form.get('event_type')
        status = request.form.get('status')
        location_UID = request.form.get('location_UID', 'SYSTEM')
        
        # Validate input
        errors = validate_event_data(title, description, event_type, status, location_UID)
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('events/edit_event.html', 
                                 event=event, 
                                 event_types=event_types, 
                                 locations=locations)
        
        # Update event
        event.title = title
        event.description = description
        event.event_type = event_type
        event.status = status
        event.location_UID = location_UID
        event.update(updated_by=current_user.row_id if current_user else 1)
        
        db.session.commit()
        flash('Event updated successfully', 'success')
        return redirect(url_for('events.view_event', event_id=event_id))
    
    return render_template('events/edit_event.html', 
                         event=event, 
                         event_types=event_types, 
                         locations=locations)

@bp.route('/<int:event_id>/delete', methods=['POST'])
@login_required
def delete_event(event_id):
    """Delete a specific event"""
    event = Event.query.get_or_404(event_id)
    
    # Check if user has permission to delete (admin or event creator)
    if not current_user.is_admin and event.created_by != current_user.row_id:
        flash('You do not have permission to delete this event', 'error')
        return redirect(url_for('events.view_event', event_id=event_id))
    
    db.session.delete(event)
    db.session.commit()
    flash('Event deleted successfully.', 'success')
    return redirect(url_for('events.index'))

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_event():
    """Create a new event"""
    event_types = EventTypes.query.all()
    locations = MajorLocation.query.all()
    
    if request.method == 'POST':
        # Get and sanitize form data
        title = sanitize_input(request.form.get('title'))
        description = sanitize_input(request.form.get('description'))
        event_type = request.form.get('event_type')
        status = request.form.get('status', 'pending')
        location_UID = request.form.get('location_UID', 'SYSTEM')
        
        # Validate input
        errors = validate_event_data(title, description, event_type, status, location_UID)
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('events/create_event.html', 
                                 event_types=event_types, 
                                 locations=locations)
        
        new_event = Event(
            title=title,
            description=description,
            event_type=event_type,
            status=status,
            location_UID=location_UID,
            created_by=current_user.row_id if current_user else 1
        )
        db.session.add(new_event)
        db.session.commit()
        
        flash('Event created successfully', 'success')
        return redirect(url_for('events.view_event', event_id=new_event.row_id))
    
    return render_template('events/create_event.html', 
                         event_types=event_types, 
                         locations=locations)

@bp.route('/event-types')
@login_required
def event_types_index():
    """Display all event types"""
    event_types = EventTypes.query.all()
    return render_template('event_types/index.html', event_types=event_types)

@bp.route('/event-types/create', methods=['GET', 'POST'])
@login_required
def create_event_type():
    """Create a new event type"""
    # Check if user is admin
    if not current_user.is_admin:
        flash('Only administrators can create event types', 'error')
        return redirect(url_for('events.event_types_index'))
    
    if request.method == 'POST':
        value = sanitize_input(request.form.get('value'))
        description = sanitize_input(request.form.get('description'))
        
        # Validate input
        if not value or not value.strip():
            flash('Event type name is required', 'error')
            return render_template('event_types/create.html')
        
        # Check if event type already exists
        existing_type = EventTypes.query.filter_by(value=value).first()
        if existing_type:
            flash(f'Event type "{value}" already exists', 'error')
            return render_template('event_types/create.html')
        
        new_event_type = EventTypes(
            value=value,
            description=description,
            created_by=current_user.row_id if current_user else 1
        )
        db.session.add(new_event_type)
        db.session.commit()
        
        flash('Event type created successfully', 'success')
        return redirect(url_for('events.event_types_index'))
    
    return render_template('event_types/create.html')

@bp.route('/event-types/<int:type_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event_type(type_id):
    """Edit an event type"""
    # Check if user is admin
    if not current_user.is_admin:
        flash('Only administrators can edit event types', 'error')
        return redirect(url_for('events.event_types_index'))
    
    event_type = EventTypes.query.get_or_404(type_id)
    
    if request.method == 'POST':
        value = sanitize_input(request.form.get('value'))
        description = sanitize_input(request.form.get('description'))
        
        # Validate input
        if not value or not value.strip():
            flash('Event type name is required', 'error')
            return render_template('event_types/edit.html', event_type=event_type)
        
        # Check if the new name conflicts with existing types (excluding current)
        existing_type = EventTypes.query.filter(
            EventTypes.value == value,
            EventTypes.row_id != type_id
        ).first()
        if existing_type:
            flash(f'Event type "{value}" already exists', 'error')
            return render_template('event_types/edit.html', event_type=event_type)
        
        event_type.value = value
        event_type.description = description
        event_type.update(updated_by=current_user.row_id if current_user else 1)
        db.session.commit()
        
        flash('Event type updated successfully', 'success')
        return redirect(url_for('events.event_types_index'))
    
    return render_template('event_types/edit.html', event_type=event_type)

@bp.route('/event-types/<int:type_id>/delete', methods=['POST'])
@login_required
def delete_event_type(type_id):
    """Delete an event type if it's not protected"""
    # Check if user is admin
    if not current_user.is_admin:
        flash('Only administrators can delete event types', 'error')
        return redirect(url_for('events.event_types_index'))
    
    event_type = EventTypes.query.get_or_404(type_id)
    
    # Check if the type can be deleted
    if not event_type.can_be_deleted():
        flash(f'Cannot delete protected event type "{event_type.value}". This is a system-required type.', 'error')
        return redirect(url_for('events.event_types_index'))
    
    # Check if any events are using this type
    events_using_type = Event.query.filter_by(event_type=event_type.value).count()
    if events_using_type > 0:
        flash(f'Cannot delete event type "{event_type.value}" because {events_using_type} event(s) are using it.', 'error')
        return redirect(url_for('events.event_types_index'))
    
    type_name = event_type.value
    db.session.delete(event_type)
    db.session.commit()
    
    flash(f'Event type "{type_name}" deleted successfully', 'success')
    return redirect(url_for('events.event_types_index')) 
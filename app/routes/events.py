from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.BaseModels.Event import Event, EventTypes
from app.models.BaseModels.Locations import MajorLocation
from app.extensions import db
from app.utils.logger import get_logger

logger = get_logger()

bp = Blueprint('events', __name__, url_prefix='/events')

@bp.route('/')
def index():
    """Display all events"""
    try:
        events = Event.query.all()
        return render_template('events/index.html', events=events)
    except Exception as e:
        logger.error(f"Error fetching events: {str(e)}")
        flash('Error loading events', 'error')
        return render_template('events/index.html', events=[])

@bp.route('/<int:event_id>')
def view_event(event_id):
    """Display a specific event's details"""
    try:
        event = Event.query.get_or_404(event_id)
        return render_template('events/view_event.html', event=event)
    except Exception as e:
        logger.error(f"Error fetching event {event_id}: {str(e)}")
        flash('Error loading event details', 'error')
        return redirect(url_for('events.index'))

@bp.route('/<int:event_id>/edit', methods=['GET', 'POST'])
def edit_event(event_id):
    """Edit a specific event"""
    event = Event.query.get_or_404(event_id)
    event_types = EventTypes.query.all()
    locations = MajorLocation.query.all()
    if request.method == 'POST':
        try:
            title = request.form.get('title')
            description = request.form.get('description')
            event_type = request.form.get('event_type')
            status = request.form.get('status')
            location_UID = request.form.get('location_UID', 'SYSTEM')
            if not title or not event_type or not status:
                return render_template('events/edit_event.html', event=event, event_types=event_types, locations=locations, error='All fields are required')
            event.title = title
            event.description = description
            event.event_type = event_type
            event.status = status
            event.location_UID = location_UID
            db.session.commit()
            logger.info(f"Event {event_id} updated")
            flash('Event updated successfully', 'success')
            return redirect(url_for('events.view_event', event_id=event_id))
        except Exception as e:
            logger.error(f"Error editing event {event_id}: {str(e)}")
            flash('Error updating event', 'error')
            return render_template('events/edit_event.html', event=event, event_types=event_types, locations=locations, error='Error updating event')
    return render_template('events/edit_event.html', event=event, event_types=event_types, locations=locations)

@bp.route('/<int:event_id>/delete', methods=['POST'])
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    try:
        db.session.delete(event)
        db.session.commit()
        logger.info(f"Event {event_id} deleted.")
        flash('Event deleted successfully.', 'success')
        return redirect(url_for('events.index'))
    except Exception as e:
        logger.error(f"Error deleting event {event_id}: {str(e)}")
        flash('Error deleting event.', 'error')
        return redirect(url_for('events.edit_event', event_id=event_id))

@bp.route('/create', methods=['GET', 'POST'])
def create_event():
    event_types = EventTypes.query.all()
    locations = MajorLocation.query.all()
    if request.method == 'POST':
        try:
            title = request.form.get('title')
            description = request.form.get('description')
            event_type = request.form.get('event_type')
            status = request.form.get('status', 'pending')
            location_UID = request.form.get('location_UID', 'SYSTEM')
            if not title or not event_type or not status:
                flash('All fields are required', 'error')
                return render_template('events/create_event.html', event_types=event_types, locations=locations)
            new_event = Event(
                title=title,
                description=description,
                event_type=event_type,
                status=status,
                location_UID=location_UID,
                created_by=1
            )
            db.session.add(new_event)
            db.session.commit()
            logger.info(f"New event created: {title}")
            flash('Event created successfully', 'success')
            return redirect(url_for('events.view_event', event_id=new_event.row_id))
        except Exception as e:
            logger.error(f"Error creating event: {str(e)}")
            flash('Error creating event', 'error')
            return render_template('events/create_event.html', event_types=event_types, locations=locations)
    return render_template('events/create_event.html', event_types=event_types, locations=locations)

@bp.route('/event-types')
def event_types_index():
    """Display all event types"""
    try:
        event_types = EventTypes.query.all()
        return render_template('event_types/index.html', event_types=event_types)
    except Exception as e:
        logger.error(f"Error rendering event types index: {str(e)}")
        return "Error loading event types", 500

@bp.route('/event-types/create', methods=['GET', 'POST'])
def create_event_type():
    """Create a new event type"""
    if request.method == 'POST':
        try:
            value = request.form.get('value')
            description = request.form.get('description')
            
            if not value:
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
                created_by=1
            )
            db.session.add(new_event_type)
            db.session.commit()
            
            logger.info(f"New event type created: {value}")
            flash('Event type created successfully', 'success')
            return redirect(url_for('events.event_types_index'))
            
        except Exception as e:
            logger.error(f"Error creating event type: {str(e)}")
            flash('Error creating event type', 'error')
            return render_template('event_types/create.html')
    
    return render_template('event_types/create.html')

@bp.route('/event-types/<int:type_id>/edit', methods=['GET', 'POST'])
def edit_event_type(type_id):
    """Edit an event type"""
    event_type = EventTypes.query.get_or_404(type_id)
    
    if request.method == 'POST':
        try:
            value = request.form.get('value')
            description = request.form.get('description')
            
            if not value:
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
            event_type.update(updated_by=1)
            db.session.commit()
            
            logger.info(f"Event type updated: {value}")
            flash('Event type updated successfully', 'success')
            return redirect(url_for('events.event_types_index'))
            
        except Exception as e:
            logger.error(f"Error updating event type {type_id}: {str(e)}")
            flash('Error updating event type', 'error')
            return render_template('event_types/edit.html', event_type=event_type)
    
    return render_template('event_types/edit.html', event_type=event_type)

@bp.route('/event-types/<int:type_id>/delete', methods=['POST'])
def delete_event_type(type_id):
    """Delete an event type if it's not protected"""
    event_type = EventTypes.query.get_or_404(type_id)
    
    try:
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
        
        logger.info(f"Event type deleted: {type_name}")
        flash(f'Event type "{type_name}" deleted successfully', 'success')
        return redirect(url_for('events.event_types_index'))
        
    except Exception as e:
        logger.error(f"Error deleting event type {type_id}: {str(e)}")
        flash('Error deleting event type', 'error')
        return redirect(url_for('events.event_types_index')) 
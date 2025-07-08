from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.BaseModels.Event import Event, EventTypes
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
    if request.method == 'POST':
        try:
            title = request.form.get('title')
            description = request.form.get('description')
            event_type = request.form.get('event_type')
            status = request.form.get('status')
            if not title or not event_type or not status:
                return render_template('events/edit_event.html', event=event, event_types=event_types, error='All fields are required')
            event.title = title
            event.description = description
            event.event_type = event_type
            event.status = status
            db.session.commit()
            logger.info(f"Event {event_id} updated")
            flash('Event updated successfully', 'success')
            return redirect(url_for('events.view_event', event_id=event_id))
        except Exception as e:
            logger.error(f"Error editing event {event_id}: {str(e)}")
            flash('Error updating event', 'error')
            return render_template('events/edit_event.html', event=event, event_types=event_types, error='Error updating event')
    return render_template('events/edit_event.html', event=event, event_types=event_types)

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
    if request.method == 'POST':
        try:
            title = request.form.get('title')
            description = request.form.get('description')
            event_type = request.form.get('event_type')
            status = request.form.get('status', 'pending')
            if not title or not event_type or not status:
                flash('All fields are required', 'error')
                return render_template('events/create_event.html', event_types=event_types)
            new_event = Event(
                title=title,
                description=description,
                event_type_id=event_type,
                status=status,
                created_by=1
            )
            db.session.add(new_event)
            db.session.commit()
            logger.info(f"New event created: {title}")
            flash('Event created successfully', 'success')
            return redirect(url_for('events.view_event', event_id=new_event.event_row_id))
        except Exception as e:
            logger.error(f"Error creating event: {str(e)}")
            flash('Error creating event', 'error')
            return render_template('events/create_event.html', event_types=event_types)
    return render_template('events/create_event.html', event_types=event_types)

@bp.route('/event-types')
def event_types_index():
    """Display all event types"""
    try:
        event_types = EventTypes.query.all()
        return render_template('event_types/index.html', event_types=event_types)
    except Exception as e:
        logger.error(f"Error rendering event types index: {str(e)}")
        return "Error loading event types", 500 
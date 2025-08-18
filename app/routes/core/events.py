"""
Event management routes
CRUD operations for Event model
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from app.logger import get_logger
from flask_login import login_required, current_user
from app.models.core.event import Event
from app.models.core.asset import Asset
from app.models.core.user import User
from app.models.core.major_location import MajorLocation
from app.models.core.make_model import MakeModel
from app import db

bp = Blueprint('events', __name__)
logger = get_logger("asset_management.routes.bp")

def build_event_query(row_count=50):
    """Helper function to build event query with filters"""
    # Get filter parameters
    event_type = request.args.get('event_type')
    user_id = request.args.get('user_id', type=int)
    asset_id = request.args.get('asset_id')
    major_location_id = request.args.get('major_location_id')
    make_model_id = request.args.get('make_model_id', type=int)
    
    query = Event.query
    
    if event_type:
        query = query.filter(Event.event_type == event_type)
    
    if user_id:
        query = query.filter(Event.user_id == user_id)
    
    # Handle asset filtering (including null)
    if asset_id is not None:
        if asset_id == 'null':
            query = query.filter(Event.asset_id.is_(None))
        elif asset_id != '':
            query = query.filter(Event.asset_id == int(asset_id))
    
    # Handle location filtering (including null)
    if major_location_id is not None:
        if major_location_id == 'null':
            query = query.filter(Event.major_location_id.is_(None))
        elif major_location_id != '':
            query = query.filter(Event.major_location_id == int(major_location_id))
    
    # Handle make/model filtering - filter events related to assets of this make/model
    if make_model_id:
        query = query.join(Asset, Event.asset_id == Asset.id).filter(Asset.make_model_id == make_model_id)
    
    # Order by timestamp (newest first)
    query = query.order_by(Event.timestamp.desc())
    
    return query, {
        'event_type': event_type,
        'user_id': user_id,
        'asset_id': asset_id,
        'major_location_id': major_location_id,
        'make_model_id': make_model_id,
        'row_count': row_count
    }

@bp.route('/events')
@login_required
def list():
    """List all events with optional condensed view"""
    condensed_view = request.args.get('condensed-view', False, type=bool)

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('row_count', 20, type=int)

    if condensed_view:
        page, per_page = 1, 10
    
    # Build query using helper function with row_count limit
    query, filters = build_event_query(row_count=per_page)
    
    # Use pagination for both views
    events = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Get filter options for the form
    users = User.query.all()
    assets = Asset.query.all()
    locations = MajorLocation.query.all()
    make_models = MakeModel.query.all()
    
    # Choose template based on view type
    template = 'core/events/recent_events/recent_events.html' if condensed_view else 'core/events/list.html'
    
    return render_template(template, 
                         events=events,
                         users=users,
                         assets=assets,
                         locations=locations,
                         make_models=make_models,
                         filters=filters)

@bp.route('/events/<int:event_id>')
@login_required
def detail(event_id):
    """View event details"""
    event = Event.query.get_or_404(event_id)
    
    return render_template('core/events/detail.html', event=event)

@bp.route('/events/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create new event"""
    if request.method == 'POST':
        # Validate form data
        event_type = request.form.get('event_type')
        description = request.form.get('description')
        asset_id = request.form.get('asset_id', type=int)
        major_location_id = request.form.get('major_location_id', type=int)
        
        # Validate required fields
        if not event_type or not description:
            flash('Event type and description are required', 'error')
            return render_template('core/events/create.html', 
                                 assets=Asset.query.all(),
                                 locations=MajorLocation.query.all())
        
        # Create new event
        event = Event(
            event_type=event_type,
            description=description,
            user_id=current_user.id,
            asset_id=asset_id,
            major_location_id=major_location_id
        )
        
        db.session.add(event)
        db.session.commit()
        
        flash('Event created successfully', 'success')
        return redirect(url_for('events.detail', event_id=event.id))
    
    # Get form options
    assets = Asset.query.all()
    locations = MajorLocation.query.all()
    
    return render_template('core/events/create.html', 
                         assets=assets,
                         locations=locations)

@bp.route('/events/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(event_id):
    """Edit event"""
    event = Event.query.get_or_404(event_id)
    
    if request.method == 'POST':
        # Validate form data
        event_type = request.form.get('event_type')
        description = request.form.get('description')
        asset_id = request.form.get('asset_id', type=int)
        major_location_id = request.form.get('major_location_id', type=int)
        
        # Update event
        event.event_type = event_type
        event.description = description
        event.asset_id = asset_id
        event.major_location_id = major_location_id
        
        db.session.commit()
        
        flash('Event updated successfully', 'success')
        return redirect(url_for('events.detail', event_id=event.id))
    
    # Get form options
    assets = Asset.query.all()
    locations = MajorLocation.query.all()
    
    return render_template('core/events/edit.html', 
                         event=event,
                         assets=assets,
                         locations=locations)

@bp.route('/events/<int:event_id>/delete', methods=['POST'])
@login_required
def delete(event_id):
    """Delete event"""
    event = Event.query.get_or_404(event_id)
    
    db.session.delete(event)
    db.session.commit()
    
    flash('Event deleted successfully', 'success')
    return redirect(url_for('events.list'))



@bp.route('/events/card')
@login_required
def events_card():
    """HTMX endpoint for events card"""
    condensed_view = request.args.get('condensed-view', False, type=bool)
    
    if condensed_view:
        # Condensed view card format
        row_count = request.args.get('row_count', 10, type=int)
        
        # Build query using helper function with row_count limit
        query, filters = build_event_query(row_count=row_count)
        
        # Limit results
        events = query.limit(row_count).all()
        
        # Add row_count to filters
        filters['row_count'] = row_count
        
        return render_template('core/events/recent_events/recent_events_card.html', 
                             events=events,
                             filters=filters)
    else:
        # Standard events card format (for future use)
        per_page = request.args.get('row_count', 20, type=int)
        
        # Build query using helper function with row_count limit
        query, filters = build_event_query(row_count=per_page)
        
        # Limit results
        events = query.limit(per_page).all()
        
        return render_template('core/events/events_card.html', 
                             events=events,
                             filters=filters) 
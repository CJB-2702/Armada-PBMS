"""
Event management routes
CRUD operations for Event model
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.models.core.event import Event
from app.models.core.asset import Asset
from app.models.core.user import User
from app.models.core.major_location import MajorLocation
from app import db

bp = Blueprint('events', __name__)

@bp.route('/events')
@login_required
def list():
    """List all events"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Basic filtering
    event_type = request.args.get('event_type')
    user_id = request.args.get('user_id', type=int)
    asset_id = request.args.get('asset_id')
    major_location_id = request.args.get('major_location_id')
    
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
    
    # Order by timestamp (newest first)
    query = query.order_by(Event.timestamp.desc())
    
    # Pagination
    events = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Get filter options
    users = User.query.all()
    assets = Asset.query.all()
    locations = MajorLocation.query.all()
    
    return render_template('core/events/list.html', 
                         events=events,
                         users=users,
                         assets=assets,
                         locations=locations)

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
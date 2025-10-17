#!/usr/bin/env python3
"""
Dispatch Routes
CRUD operations for dispatches
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.dispatching.dispatch import Dispatch
from app.models.dispatching.dispatch_status_history import DispatchStatusHistory
from app.models.core.asset import Asset
from app.models.core.user import User
from app.models.core.major_location import MajorLocation
from app.models.dispatching.detail_table_sets.asset_type_dispatch_detail_table_set import AssetTypeDispatchDetailTableSet
from datetime import datetime
import uuid
from app.logger import get_logger

logger = get_logger("asset_management.routes.dispatching")
# Create blueprint
dispatching_bp = Blueprint('dispatching', __name__)

@dispatching_bp.route('/')
@login_required
def index():
    """List all dispatches"""
    logger.debug(f"User {current_user.username} accessing dispatches list")
    dispatches = Dispatch.query.order_by(Dispatch.created_date.desc()).all()
    logger.info(f"Dispatches list returned {len(dispatches)} dispatches")
    return render_template('dispatching/index.html', dispatches=dispatches)

@dispatching_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new dispatch"""
    if request.method == 'POST':
        logger.debug(f"User {current_user.username} creating new dispatch")
        try:
            # Generate unique dispatch number
            dispatch_number = f"DISP-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
            
            # Create dispatch
            dispatch = Dispatch(
                dispatch_number=dispatch_number,
                title=request.form['title'],
                description=request.form.get('description', ''),
                priority=request.form.get('priority', 'Normal'),
                asset_id=request.form.get('asset_id') if request.form.get('asset_id') else None,
                assigned_user_id=request.form.get('assigned_user_id') if request.form.get('assigned_user_id') else None,
                major_location_id=request.form.get('major_location_id') if request.form.get('major_location_id') else None,
                due_date=datetime.strptime(request.form['due_date'], '%Y-%m-%d') if request.form.get('due_date') else None,
                created_by_id=current_user.id
            )
            
            db.session.add(dispatch)
            db.session.commit()
            
            # Note: create_event() is called automatically in Dispatch.__init__() via EventDetailVirtual
            # No need to call it manually here
            
            # Create dispatch detail tables if asset is assigned
            if dispatch.asset_id:
                AssetTypeDispatchDetailTableSet.create_dispatch_detail_table_rows(dispatch.id, dispatch.asset_id)
            
            logger.info(f"Dispatch created successfully - Number: {dispatch_number}, Title: {dispatch.title}")
            flash('Dispatch created successfully!', 'success')
            return redirect(url_for('dispatching.view', dispatch_id=dispatch.id))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating dispatch: {str(e)}")
            flash(f'Error creating dispatch: {str(e)}', 'error')
    else:
        logger.debug(f"User {current_user.username} accessing dispatch creation form")
    
    # Get data for form
    assets = Asset.query.filter_by(status='Active').all()
    users = User.query.filter_by(is_active=True).all()
    locations = MajorLocation.query.filter_by(is_active=True).all()
    
    return render_template('dispatching/create.html', 
                         assets=assets, 
                         users=users, 
                         locations=locations)

@dispatching_bp.route('/<int:dispatch_id>')
@login_required
def view(dispatch_id):
    """View a specific dispatch"""
    logger.debug(f"User {current_user.username} viewing dispatch ID: {dispatch_id}")
    dispatch = Dispatch.query.get_or_404(dispatch_id)
    logger.info(f"Dispatch viewed - Number: {dispatch.dispatch_number}, Title: {dispatch.title}")
    return render_template('dispatching/view.html', dispatch=dispatch)

@dispatching_bp.route('/<int:dispatch_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(dispatch_id):
    """Edit a dispatch"""
    dispatch = Dispatch.query.get_or_404(dispatch_id)
    
    if request.method == 'POST':
        try:
            dispatch.title = request.form['title']
            dispatch.description = request.form.get('description', '')
            dispatch.priority = request.form.get('priority', 'Normal')
            dispatch.asset_id = request.form.get('asset_id') if request.form.get('asset_id') else None
            dispatch.assigned_user_id = request.form.get('assigned_user_id') if request.form.get('assigned_user_id') else None
            dispatch.major_location_id = request.form.get('major_location_id') if request.form.get('major_location_id') else None
            dispatch.due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d') if request.form.get('due_date') else None
            
            db.session.commit()
            flash('Dispatch updated successfully!', 'success')
            return redirect(url_for('dispatching.view', dispatch_id=dispatch.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating dispatch: {str(e)}', 'error')
    
    # Get data for form
    assets = Asset.query.filter_by(status='Active').all()
    users = User.query.filter_by(is_active=True).all()
    locations = MajorLocation.query.filter_by(is_active=True).all()
    
    return render_template('dispatching/edit.html', 
                         dispatch=dispatch,
                         assets=assets, 
                         users=users, 
                         locations=locations)

@dispatching_bp.route('/<int:dispatch_id>/delete', methods=['POST'])
@login_required
def delete(dispatch_id):
    """Delete a dispatch"""
    dispatch = Dispatch.query.get_or_404(dispatch_id)
    
    try:
        db.session.delete(dispatch)
        db.session.commit()
        flash('Dispatch deleted successfully!', 'success')
        return redirect(url_for('dispatching.index'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting dispatch: {str(e)}', 'error')
        return redirect(url_for('dispatching.view', dispatch_id=dispatch.id))

@dispatching_bp.route('/<int:dispatch_id>/status', methods=['POST'])
@login_required
def update_status(dispatch_id):
    """Update dispatch status"""
    dispatch = Dispatch.query.get_or_404(dispatch_id)
    
    try:
        new_status = request.form['status']
        reason = request.form.get('reason', '')
        
        dispatch.update_status(new_status, current_user.id, reason)
        db.session.commit()
        
        flash(f'Status updated to {new_status}', 'success')
        return redirect(url_for('dispatching.view', dispatch_id=dispatch.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating status: {str(e)}', 'error')
        return redirect(url_for('dispatching.view', dispatch_id=dispatch.id))

@dispatching_bp.route('/<int:dispatch_id>/history')
@login_required
def history(dispatch_id):
    """View dispatch status history"""
    dispatch = Dispatch.query.get_or_404(dispatch_id)
    history = DispatchStatusHistory.query.filter_by(dispatch_id=dispatch_id).order_by(DispatchStatusHistory.changed_date.desc()).all()
    
    return render_template('dispatching/history.html', dispatch=dispatch, history=history)

# API endpoints for AJAX requests
@dispatching_bp.route('/api/dispatches')
@login_required
def api_dispatches():
    """API endpoint to get dispatches as JSON"""
    dispatches = Dispatch.query.order_by(Dispatch.created_date.desc()).all()
    
    dispatch_list = []
    for dispatch in dispatches:
        dispatch_data = {
            'id': dispatch.id,
            'dispatch_number': dispatch.dispatch_number,
            'title': dispatch.title,
            'status': dispatch.status,
            'priority': dispatch.priority,
            'created_date': dispatch.created_date.strftime('%Y-%m-%d %H:%M') if dispatch.created_date else None,
            'due_date': dispatch.due_date.strftime('%Y-%m-%d') if dispatch.due_date else None,
            'asset_name': dispatch.asset.name if dispatch.asset else None,
            'assigned_user': dispatch.assigned_user.username if dispatch.assigned_user else None,
            'location': dispatch.major_location.name if dispatch.major_location else None
        }
        dispatch_list.append(dispatch_data)
    
    return jsonify(dispatch_list)

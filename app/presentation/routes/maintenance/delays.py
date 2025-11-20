"""
Maintenance Delay management routes
CRUD operations for MaintenanceDelay model
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.data.maintenance.base.maintenance_delays import MaintenanceDelay
from app.services.maintenance.delay_service import DelayService
from app import db
from app.logger import get_logger
from datetime import datetime

logger = get_logger("asset_management.routes.maintenance.delays")
bp = Blueprint('delays', __name__)

@bp.route('/delays')
@login_required
def list():
    """List all maintenance delays with basic filtering"""
    logger.debug(f"User {current_user.username} accessing maintenance delays list")
    
    page = request.args.get('page', 1, type=int)
    
    # Basic filtering
    maintenance_action_set_id = request.args.get('maintenance_action_set_id', type=int)
    delay_type = request.args.get('delay_type')
    is_resolved_param = request.args.get('is_resolved')
    is_active = None if is_resolved_param is None else (is_resolved_param.lower() == 'false')
    
    logger.debug(f"Maintenance delays list filters - Action Set: {maintenance_action_set_id}, Type: {delay_type}")
    
    # Get list data from service
    delays, form_options = DelayService.get_list_data(
        page=page,
        maintenance_action_set_id=maintenance_action_set_id,
        delay_type=delay_type,
        is_active=is_active
    )
    
    maintenance_action_sets = form_options['maintenance_action_sets']
    
    logger.info(f"Maintenance delays list returned {delays.total} items (page {page})")
    
    return render_template('maintenance/delays/list.html', 
                         delays=delays,
                         maintenance_action_sets=maintenance_action_sets,
                         filters={'maintenance_action_set_id': maintenance_action_set_id,
                                'delay_type': delay_type,
                                'is_resolved': is_resolved_param
                         })

@bp.route('/delays/<int:delay_id>')
@login_required
def detail(delay_id):
    """View individual maintenance delay details"""
    logger.debug(f"User {current_user.username} accessing maintenance delay detail for ID: {delay_id}")
    
    delay = MaintenanceDelay.query.get_or_404(delay_id)
    
    # Get related data through relationships
    maintenance_action_set = delay.maintenance_action_set
    
    logger.info(f"Maintenance delay detail accessed - Type: {delay.delay_type} (ID: {delay_id})")
    
    return render_template('maintenance/delays/detail.html', 
                         delay=delay,
                         maintenance_action_set=maintenance_action_set)

@bp.route('/delays/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create new maintenance delay"""
    if request.method == 'POST':
        # Validate form data
        maintenance_action_set_id = request.form.get('maintenance_action_set_id', type=int)
        delay_type = request.form.get('delay_type')
        delay_reason = request.form.get('delay_reason')
        delay_start_date = request.form.get('delay_start_date')
        delay_end_date = request.form.get('delay_end_date')
        delay_billable_hours = request.form.get('delay_billable_hours', type=float)
        delay_notes = request.form.get('delay_notes')
        
        # Create new maintenance delay
        delay = MaintenanceDelay(
            maintenance_action_set_id=maintenance_action_set_id,
            delay_type=delay_type,
            delay_reason=delay_reason,
            delay_start_date=datetime.fromisoformat(delay_start_date) if delay_start_date else None,
            delay_end_date=datetime.fromisoformat(delay_end_date) if delay_end_date else None,
            delay_billable_hours=delay_billable_hours,
            delay_notes=delay_notes,
            created_by_id=current_user.id,
            updated_by_id=current_user.id
        )
        
        db.session.add(delay)
        db.session.commit()
        
        # Create comment on the maintenance action set
        delay.create_delay_comment(current_user.id)
        db.session.commit()
        
        flash('Maintenance delay created successfully', 'success')
        return redirect(url_for('delays.detail', delay_id=delay.id))
    
    # Get form options from service
    form_options = DelayService.get_form_options()
    
    return render_template('maintenance/delays/create.html',
                         maintenance_action_sets=form_options['maintenance_action_sets'])

@bp.route('/delays/<int:delay_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(delay_id):
    """Edit maintenance delay"""
    delay = MaintenanceDelay.query.get_or_404(delay_id)
    
    if request.method == 'POST':
        # Validate form data
        delay_type = request.form.get('delay_type')
        delay_reason = request.form.get('delay_reason')
        delay_start_date = request.form.get('delay_start_date')
        delay_end_date = request.form.get('delay_end_date')
        delay_billable_hours = request.form.get('delay_billable_hours', type=float)
        delay_notes = request.form.get('delay_notes')
        
        # Update maintenance delay
        delay._set_delay_type(delay_type, current_user.id)
        delay._set_delay_reason(delay_reason, current_user.id)
        
        if delay_start_date:
            delay._set_delay_start_date(datetime.fromisoformat(delay_start_date), current_user.id)
        
        if delay_end_date:
            delay._set_delay_end_date(datetime.fromisoformat(delay_end_date), current_user.id)
        
        delay.delay_billable_hours = delay_billable_hours
        delay.delay_notes = delay_notes
        delay.updated_by_id = current_user.id
        
        db.session.commit()
        
        flash('Maintenance delay updated successfully', 'success')
        return redirect(url_for('delays.detail', delay_id=delay.id))
    
    # Get form options from service
    form_options = DelayService.get_form_options()
    
    return render_template('maintenance/delays/edit.html',
                         delay=delay,
                         maintenance_action_sets=form_options['maintenance_action_sets'])

@bp.route('/delays/<int:delay_id>/delete', methods=['POST'])
@login_required
def delete(delay_id):
    """Delete maintenance delay"""
    delay = MaintenanceDelay.query.get_or_404(delay_id)
    
    db.session.delete(delay)
    db.session.commit()
    
    flash('Maintenance delay deleted successfully', 'success')
    return redirect(url_for('delays.list'))

@bp.route('/delays/<int:delay_id>/resolve', methods=['POST'])
@login_required
def resolve(delay_id):
    """Resolve maintenance delay"""
    delay = MaintenanceDelay.query.get_or_404(delay_id)
    
    if delay.is_resolved:
        flash('Delay is already resolved', 'warning')
        return redirect(url_for('delays.detail', delay_id=delay_id))
    
    delay_end_date = request.form.get('delay_end_date')
    delay_billable_hours = request.form.get('delay_billable_hours', type=float)
    
    if delay_end_date:
        end_date = datetime.fromisoformat(delay_end_date)
    else:
        end_date = None
    
    delay.resolve_delay(current_user.id, end_date, delay_billable_hours)
    db.session.commit()
    
    flash('Maintenance delay resolved successfully', 'success')
    return redirect(url_for('delays.detail', delay_id=delay_id))


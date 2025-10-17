"""
Action management routes
CRUD operations for Action model
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.models.maintenance.base.action import Action
from app.models.maintenance.base.maintenance_action_set import MaintenanceActionSet
from app.models.maintenance.templates.template_action_item import TemplateActionItem
from app import db
from app.logger import get_logger

logger = get_logger("asset_management.routes.maintenance.actions")
bp = Blueprint('actions', __name__)

@bp.route('/actions')
@login_required
def list():
    """List all actions with basic filtering"""
    logger.debug(f"User {current_user.username} accessing actions list")
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Basic filtering
    status = request.args.get('status')
    maintenance_action_set_id = request.args.get('maintenance_action_set_id', type=int)
    action_name = request.args.get('action_name')
    
    logger.debug(f"Actions list filters - Status: {status}, Action Set: {maintenance_action_set_id}")
    
    query = Action.query
    
    if status:
        query = query.filter(Action.status == status)
    
    if maintenance_action_set_id:
        query = query.filter(Action.maintenance_action_set_id == maintenance_action_set_id)
    
    if action_name:
        query = query.filter(Action.action_name.ilike(f'%{action_name}%'))
    
    # Order by creation date (newest first)
    query = query.order_by(Action.created_at.desc())
    
    # Pagination
    actions = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Get filter options
    maintenance_action_sets = MaintenanceActionSet.query.all()
    
    logger.info(f"Actions list returned {actions.total} actions (page {page})")
    
    return render_template('maintenance/actions/list.html', 
                         actions=actions,
                         maintenance_action_sets=maintenance_action_sets,
                         current_filters={
                             'status': status,
                             'maintenance_action_set_id': maintenance_action_set_id,
                             'action_name': action_name
                         })

@bp.route('/actions/<int:action_id>')
@login_required
def detail(action_id):
    """View individual action details"""
    logger.debug(f"User {current_user.username} accessing action detail for action ID: {action_id}")
    
    action = Action.query.get_or_404(action_id)
    
    # Get related data through relationships
    maintenance_action_set = action.maintenance_action_set
    template_action_item = action.template_action_item
    part_demands = action.part_demands
    
    logger.info(f"Action detail accessed - Action: {action.action_name} (ID: {action_id})")
    
    return render_template('maintenance/actions/detail.html', 
                         action=action,
                         maintenance_action_set=maintenance_action_set,
                         template_action_item=template_action_item,
                         part_demands=part_demands)

@bp.route('/actions/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create new action"""
    if request.method == 'POST':
        # Validate form data
        action_name = request.form.get('action_name')
        description = request.form.get('description')
        maintenance_action_set_id = request.form.get('maintenance_action_set_id', type=int)
        template_action_item_id = request.form.get('template_action_item_id', type=int)
        status = request.form.get('status', 'Not Started')
        scheduled_start_time = request.form.get('scheduled_start_time')
        sequence_order = request.form.get('sequence_order', type=int)
        
        # Create new action using factory
        from app.models.maintenance.factories.action_factory import ActionFactory
        
        action = ActionFactory.create_from_dict({
            'action_name': action_name,
            'description': description,
            'maintenance_action_set_id': maintenance_action_set_id,
            'template_action_item_id': template_action_item_id,
            'status': status,
            'scheduled_start_time': scheduled_start_time,
            'sequence_order': sequence_order,
            'created_by_id': current_user.id,
            'updated_by_id': current_user.id
        })
        
        flash('Action created successfully', 'success')
        return redirect(url_for('actions.detail', action_id=action.id))
    
    # Get form options
    maintenance_action_sets = MaintenanceActionSet.query.all()
    template_action_items = TemplateActionItem.query.all()
    
    return render_template('maintenance/actions/create.html',
                         maintenance_action_sets=maintenance_action_sets,
                         template_action_items=template_action_items)

@bp.route('/actions/<int:action_id>/start', methods=['POST'])
@login_required
def start_action(action_id):
    """Start an action"""
    action = Action.query.get_or_404(action_id)
    
    if action.status != 'Not Started':
        flash('Action can only be started if it is not started', 'error')
        return redirect(url_for('actions.detail', action_id=action_id))
    
    action.start_action(current_user.id)
    db.session.commit()
    
    flash('Action started successfully', 'success')
    return redirect(url_for('actions.detail', action_id=action_id))

@bp.route('/actions/<int:action_id>/complete', methods=['POST'])
@login_required
def complete_action(action_id):
    """Complete an action"""
    action = Action.query.get_or_404(action_id)
    
    if action.status not in ['Not Started', 'In Progress']:
        flash('Action can only be completed if it is not started or in progress', 'error')
        return redirect(url_for('actions.detail', action_id=action_id))
    
    notes = request.form.get('completion_notes')
    status = request.form.get('status', 'Completed')
    billable_hours = request.form.get('billable_hours', type=float)
    
    action.complete_action(current_user.id, notes, status, billable_hours)
    db.session.commit()
    
    flash('Action completed successfully', 'success')
    return redirect(url_for('actions.detail', action_id=action_id))

@bp.route('/actions/<int:action_id>/skip', methods=['POST'])
@login_required
def skip_action(action_id):
    """Skip an action"""
    action = Action.query.get_or_404(action_id)
    
    if action.status != 'Not Started':
        flash('Action can only be skipped if it is not started', 'error')
        return redirect(url_for('actions.detail', action_id=action_id))
    
    reason = request.form.get('reason')
    action.skip_action(current_user.id, reason)
    db.session.commit()
    
    flash('Action skipped successfully', 'success')
    return redirect(url_for('actions.detail', action_id=action_id))

@bp.route('/actions/<int:action_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(action_id):
    """Edit action"""
    action = Action.query.get_or_404(action_id)
    
    if request.method == 'POST':
        # Validate form data
        action_name = request.form.get('action_name')
        description = request.form.get('description')
        status = request.form.get('status')
        scheduled_start_time = request.form.get('scheduled_start_time')
        completion_notes = request.form.get('completion_notes')
        billable_hours = request.form.get('billable_hours', type=float)
        
        # Update action
        action.action_name = action_name
        action.description = description
        action.status = status
        if scheduled_start_time:
            from datetime import datetime
            action.scheduled_start_time = datetime.fromisoformat(scheduled_start_time.replace('T', ' '))
        action.completion_notes = completion_notes
        action.billable_hours = billable_hours
        action.updated_by_id = current_user.id
        
        db.session.commit()
        
        flash('Action updated successfully', 'success')
        return redirect(url_for('actions.detail', action_id=action.id))
    
    return render_template('maintenance/actions/edit.html', action=action)

@bp.route('/actions/<int:action_id>/delete', methods=['POST'])
@login_required
def delete(action_id):
    """Delete action"""
    action = Action.query.get_or_404(action_id)
    
    # Check if action has part demands
    if action.part_demands.count() > 0:
        flash('Cannot delete action with part demands', 'error')
        return redirect(url_for('actions.detail', action_id=action.id))
    
    db.session.delete(action)
    db.session.commit()
    
    flash('Action deleted successfully', 'success')
    return redirect(url_for('actions.list'))


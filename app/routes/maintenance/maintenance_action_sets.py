"""
Maintenance Action Set management routes
CRUD operations for MaintenanceActionSet model
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.models.maintenance.base.maintenance_action_set import MaintenanceActionSet
from app.models.maintenance.base.action import Action
from app.models.maintenance.base.maintenance_plan import MaintenancePlan
from app.models.maintenance.templates.template_action_set import TemplateActionSet
from app.models.core.asset import Asset
from app import db
from app.logger import get_logger

logger = get_logger("asset_management.routes.maintenance.maintenance_action_sets")
bp = Blueprint('maintenance_action_sets', __name__)

@bp.route('/maintenance-action-sets')
@login_required
def list():
    """List all maintenance action sets with basic filtering"""
    logger.debug(f"User {current_user.username} accessing maintenance action sets list")
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Basic filtering
    asset_id = request.args.get('asset_id', type=int)
    maintenance_plan_id = request.args.get('maintenance_plan_id', type=int)
    status = request.args.get('status')
    priority = request.args.get('priority')
    task_name = request.args.get('task_name')
    
    logger.debug(f"Maintenance action sets list filters - Asset: {asset_id}, Plan: {maintenance_plan_id}, Status: {status}")
    
    query = MaintenanceActionSet.query
    
    if asset_id:
        query = query.filter(MaintenanceActionSet.asset_id == asset_id)
    
    if maintenance_plan_id:
        query = query.filter(MaintenanceActionSet.maintenance_plan_id == maintenance_plan_id)
    
    if status:
        query = query.filter(MaintenanceActionSet.status == status)
    
    if priority:
        query = query.filter(MaintenanceActionSet.priority == priority)
    
    if task_name:
        query = query.filter(MaintenanceActionSet.task_name.ilike(f'%{task_name}%'))
    
    # Order by scheduled date (most recent first)
    query = query.order_by(MaintenanceActionSet.scheduled_date.desc())
    
    # Pagination
    maintenance_action_sets = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Get filter options
    assets = Asset.query.all()
    maintenance_plans = MaintenancePlan.query.all()
    
    logger.info(f"Maintenance action sets list returned {maintenance_action_sets.total} items (page {page})")
    
    return render_template('maintenance/maintenance_action_sets/list.html',
                         maintenance_action_sets=maintenance_action_sets,
                         assets=assets,
                         maintenance_plans=maintenance_plans,
                         filters={'asset_id': asset_id,
                                'maintenance_plan_id': maintenance_plan_id,
                                'status': status,
                                'priority': priority,
                                'task_name': task_name
                         })

@bp.route('/maintenance-action-sets/<int:action_set_id>')
@login_required
def detail(action_set_id):
    """View individual maintenance action set details"""
    logger.debug(f"User {current_user.username} accessing maintenance action set detail for ID: {action_set_id}")
    
    action_set = MaintenanceActionSet.query.get_or_404(action_set_id)
    
    # Get related data through relationships
    asset = action_set.asset if hasattr(action_set, 'asset') else None
    maintenance_plan = action_set.maintenance_plan
    template_action_set = action_set.template_action_set
    
    # Get actions for this maintenance action set
    actions = Action.query.filter_by(
        maintenance_action_set_id=action_set.id
    ).order_by(Action.sequence_order).all()
    
    logger.info(f"Maintenance action set detail accessed - Set: {action_set.task_name} (ID: {action_set_id})")
    
    return render_template('maintenance/maintenance_action_sets/detail.html', 
                         action_set=action_set,
                         asset=asset,
                         maintenance_plan=maintenance_plan,
                         template_action_set=template_action_set,
                         actions=actions)

@bp.route('/maintenance-action-sets/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create new maintenance action set"""
    if request.method == 'POST':
        # Validate form data
        task_name = request.form.get('task_name')
        task_description = request.form.get('task_description')
        asset_id = request.form.get('asset_id', type=int)
        template_action_set_id = request.form.get('template_action_set_id', type=int)
        maintenance_plan_id = request.form.get('maintenance_plan_id', type=int)
        status = request.form.get('status', 'Planned')
        priority = request.form.get('priority', 'Medium')
        scheduled_date = request.form.get('scheduled_date')
        
        # Create new maintenance action set using factory
        from app.models.maintenance.factories.maintenance_action_set_factory import MaintenanceActionSetFactory
        
        action_set = MaintenanceActionSetFactory.create_from_dict({
            'task_name': task_name,
            'task_description': task_description,
            'asset_id': asset_id,
            'template_action_set_id': template_action_set_id,
            'maintenance_plan_id': maintenance_plan_id,
            'status': status,
            'priority': priority,
            'scheduled_date': scheduled_date,
            'created_by_id': current_user.id,
            'updated_by_id': current_user.id
        })
        
        flash('Maintenance action set created successfully', 'success')
        return redirect(url_for('maintenance_action_sets.detail', action_set_id=action_set.id))
    
    # Get form options
    assets = Asset.query.all()
    template_action_sets = TemplateActionSet.query.all()
    maintenance_plans = MaintenancePlan.query.all()
    
    return render_template('maintenance/maintenance_action_sets/create.html',
                         assets=assets,
                         template_action_sets=template_action_sets,
                         maintenance_plans=maintenance_plans)

@bp.route('/maintenance-action-sets/<int:action_set_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(action_set_id):
    """Edit maintenance action set"""
    action_set = MaintenanceActionSet.query.get_or_404(action_set_id)
    
    if request.method == 'POST':
        # Validate form data
        task_name = request.form.get('task_name')
        task_description = request.form.get('task_description')
        asset_id = request.form.get('asset_id', type=int)
        maintenance_plan_id = request.form.get('maintenance_plan_id', type=int)
        status = request.form.get('status')
        priority = request.form.get('priority')
        scheduled_date = request.form.get('scheduled_date')
        
        # Update maintenance action set
        action_set.task_name = task_name
        action_set.task_description = task_description
        action_set.asset_id = asset_id
        action_set.maintenance_plan_id = maintenance_plan_id
        action_set.status = status
        action_set.priority = priority
        action_set.scheduled_date = scheduled_date
        action_set.updated_by_id = current_user.id
        
        db.session.commit()
        
        flash('Maintenance action set updated successfully', 'success')
        return redirect(url_for('maintenance_action_sets.detail', action_set_id=action_set.id))
    
    # Get form options
    assets = Asset.query.all()
    maintenance_plans = MaintenancePlan.query.all()
    
    return render_template('maintenance/maintenance_action_sets/edit.html',
                         action_set=action_set,
                         assets=assets,
                         maintenance_plans=maintenance_plans)

@bp.route('/maintenance-action-sets/<int:action_set_id>/delete', methods=['POST'])
@login_required
def delete(action_set_id):
    """Delete maintenance action set"""
    action_set = MaintenanceActionSet.query.get_or_404(action_set_id)
    
    task_name = action_set.task_name
    
    db.session.delete(action_set)
    db.session.commit()
    
    flash(f'Maintenance action set "{task_name}" deleted successfully', 'success')
    return redirect(url_for('maintenance_action_sets.list'))

@bp.route('/maintenance-action-sets/<int:action_set_id>/start', methods=['POST'])
@login_required
def start(action_set_id):
    """Start maintenance action set"""
    action_set = MaintenanceActionSet.query.get_or_404(action_set_id)
    
    notes = request.form.get('notes')
    action_set.start_maintenance(current_user.id, notes)
    db.session.commit()
    
    flash('Maintenance action set started', 'success')
    return redirect(url_for('maintenance_action_sets.detail', action_set_id=action_set.id))

@bp.route('/maintenance-action-sets/<int:action_set_id>/complete', methods=['POST'])
@login_required
def complete(action_set_id):
    """Complete maintenance action set"""
    action_set = MaintenanceActionSet.query.get_or_404(action_set_id)
    
    notes = request.form.get('notes')
    action_set.complete_maintenance(current_user.id, notes)
    db.session.commit()
    
    flash('Maintenance action set completed', 'success')
    return redirect(url_for('maintenance_action_sets.detail', action_set_id=action_set_id))

@bp.route('/maintenance-action-sets/<int:action_set_id>/cancel', methods=['POST'])
@login_required
def cancel(action_set_id):
    """Cancel maintenance action set"""
    action_set = MaintenanceActionSet.query.get_or_404(action_set_id)
    
    reason = request.form.get('reason')
    action_set.cancel_maintenance(current_user.id, reason)
    db.session.commit()
    
    flash('Maintenance action set cancelled', 'success')
    return redirect(url_for('maintenance_action_sets.detail', action_set_id=action_set_id))


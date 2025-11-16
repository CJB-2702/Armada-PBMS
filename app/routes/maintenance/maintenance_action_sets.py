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
from app.models.maintenance.templates.template_action_item import TemplateActionItem
from app.models.maintenance.maintenance_event import MaintenanceEvent
from app.models.core.asset import Asset
from app.models.core.major_location import MajorLocation
from app import db
from app.logger import get_logger
from sqlalchemy.orm import joinedload

logger = get_logger("asset_management.routes.maintenance.maintenance_action_sets")
bp = Blueprint('maintenance_action_sets', __name__)

@bp.route('/maintenance-action-sets')
@login_required
def list():
    """List all maintenance action sets with basic filtering"""
    logger.debug(f"User {current_user.username} accessing maintenance action sets list")
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Basic filtering - asset_id is now a string for partial matching
    asset_id_filter = request.args.get('asset_id')  # String for partial match
    maintenance_plan_id = request.args.get('maintenance_plan_id', type=int)
    status = request.args.get('status')
    priority = request.args.get('priority')
    task_name = request.args.get('task_name')
    location = request.args.get('location')
    
    logger.debug(f"Maintenance action sets list filters - Asset ID: {asset_id_filter}, Plan: {maintenance_plan_id}, Status: {status}, Location: {location}")
    
    query = MaintenanceActionSet.query
    
    # Filter by asset name (starts with) through asset relationship
    if asset_id_filter:
        query = query.join(Asset, MaintenanceActionSet.asset_id == Asset.id).filter(
            Asset.name.ilike(f'{asset_id_filter}%')
        )
    
    # Filter by location name through asset relationship
    if location:
        # Only join Asset if we haven't already
        if not asset_id_filter:
            query = query.join(Asset, MaintenanceActionSet.asset_id == Asset.id)
        
        query = query.join(
            MajorLocation, Asset.major_location_id == MajorLocation.id
        ).filter(MajorLocation.name.ilike(f'%{location}%'))
    
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
    
    # Eager load asset and major_location relationships to avoid N+1 queries
    query = query.options(
        joinedload(MaintenanceActionSet.asset).joinedload(Asset.major_location)
    )
    
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
                         filters={'asset_id': asset_id_filter,
                                'maintenance_plan_id': maintenance_plan_id,
                                'status': status,
                                'priority': priority,
                                'task_name': task_name,
                                'location': location
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

    # Build wrapper to compute diagnostics, including template linkage
    maintenance_event = MaintenanceEvent(action_set)
    
    # Phase 6: Get part demands with inventory availability
    part_demand_info = []
    total_parts_needed = 0
    parts_available = 0
    parts_need_purchase = 0
    
    try:
        from app.models.inventory.managers import PartDemandManager
        
        for action in actions:
            if hasattr(action, 'part_demands'):
                for demand in action.part_demands:
                    # Check inventory availability
                    availability = PartDemandManager.check_inventory_availability(demand.id)
                    
                    part_demand_info.append({
                        'demand': demand,
                        'action': action,
                        'availability': availability
                    })
                    
                    total_parts_needed += 1
                    if availability.get('can_fulfill_from_any'):
                        parts_available += 1
                    if availability.get('needs_purchase'):
                        parts_need_purchase += 1
    except ImportError:
        # Phase 6 not available yet
        logger.debug("Phase 6 inventory system not available")
        pass
    
    logger.info(f"Maintenance action set detail accessed - Set: {action_set.task_name} (ID: {action_set_id})")
    
    return render_template('maintenance/maintenance_action_sets/detail.html', 
                         action_set=action_set,
                         asset=asset,
                         maintenance_plan=maintenance_plan,
                         template_action_set=template_action_set,
                         actions=actions,
                         maintenance_event=maintenance_event,
                         part_demand_info=part_demand_info,
                         total_parts_needed=total_parts_needed,
                         parts_available=parts_available,
                         parts_need_purchase=parts_need_purchase)

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

    # Get current actions for this set
    actions = Action.query.filter_by(
        maintenance_action_set_id=action_set.id
    ).order_by(Action.sequence_order).all()

    # Build wrapper to compute diagnostics, including template linkage
    maintenance_event = MaintenanceEvent(action_set)

    return render_template(
        'maintenance/maintenance_action_sets/edit.html',
        action_set=action_set,
        assets=assets,
        maintenance_plans=maintenance_plans,
        actions=actions,
        maintenance_event=maintenance_event,
    )


@bp.route(
    '/maintenance-action-sets/<int:action_set_id>/add-action-from-template',
    methods=['POST'],
)
@login_required
def add_action_from_template(action_set_id):
    """Add a new Action to this maintenance action set using a template action item."""
    action_set = MaintenanceActionSet.query.get_or_404(action_set_id)

    template_action_item_id = request.form.get('template_action_item_id', type=int)
    if not template_action_item_id:
        flash('Please select an action template to add.', 'error')
        return redirect(url_for('maintenance_action_sets.edit', action_set_id=action_set_id))

    template_action_item = TemplateActionItem.query.get_or_404(
        template_action_item_id
    )

    # Determine next sequence order for this set
    from app.models.maintenance.factories.action_factory import ActionFactory

    next_sequence = action_set.get_next_sequence_order()

    # Create action (and its part demands) from the template
    ActionFactory.create_with_part_demands_from_template(
        template_action_item,
        maintenance_action_set_id=action_set.id,
        user_id=current_user.id,
        sequence_order=next_sequence,
    )

    db.session.commit()

    flash(
        f'Action "{template_action_item.action_name}" added from template.',
        'success',
    )
    return redirect(url_for('maintenance_action_sets.edit', action_set_id=action_set.id))


@bp.route(
    '/maintenance-action-sets/<int:action_set_id>/template-actions-search',
    methods=['GET'],
)
@login_required
def template_actions_search(action_set_id):
    """
    HTMX endpoint: search TemplateActionItems to populate the
    'Add Action from Template' modal. Returns only table rows.
    """
    # Ensure the action set exists
    MaintenanceActionSet.query.get_or_404(action_set_id)

    q = request.args.get('q', type=str, default=None)
    page = request.args.get('page', type=int, default=1)
    page_size = 16

    query = TemplateActionItem.query
    if q:
        like = f'%{q}%'
        query = query.filter(
            (TemplateActionItem.action_name.ilike(like))
            | (TemplateActionItem.description.ilike(like))
        )

    query = query.order_by(TemplateActionItem.action_name.asc())
    template_action_items = query.limit(page_size).offset((page - 1) * page_size).all()

    return render_template(
        'maintenance/maintenance_action_sets/_template_action_rows.html',
        template_action_items=template_action_items,
        action_set_id=action_set_id,
    )


@bp.route(
    '/maintenance-action-sets/<int:action_set_id>/add-nonstandard-action',
    methods=['POST'],
)
@login_required
def add_nonstandard_action(action_set_id):
    """
    Create a new 'nonstandard' Action that is not linked to any template.
    Intended for exceptional cases only.
    """
    action_set = MaintenanceActionSet.query.get_or_404(action_set_id)

    # Determine next sequence order for this set
    next_sequence = action_set.get_next_sequence_order()

    # Create a bare action; user can edit details afterwards
    action = Action(
        maintenance_action_set_id=action_set.id,
        template_action_item_id=None,
        action_name='Nonstandard Action',
        description=None,
        status='Not Started',
        sequence_order=next_sequence,
        created_by_id=current_user.id,
        updated_by_id=current_user.id,
    )
    db.session.add(action)
    db.session.commit()

    flash(
        'Nonstandard action added. Consider defining a template action for repeat use.',
        'warning',
    )
    return redirect(url_for('maintenance_action_sets.edit', action_set_id=action_set.id))


@bp.route(
    '/maintenance-action-sets/<int:action_set_id>/actions/<int:action_id>/delete',
    methods=['POST'],
)
@login_required
def delete_action(action_set_id, action_id):
    """Delete a single action from this maintenance action set."""
    action_set = MaintenanceActionSet.query.get_or_404(action_set_id)
    action = Action.query.get_or_404(action_id)

    if action.maintenance_action_set_id != action_set.id:
        flash('Invalid action for this maintenance action set.', 'error')
        return redirect(url_for('maintenance_action_sets.edit', action_set_id=action_set.id))

    db.session.delete(action)
    db.session.commit()

    flash(f'Action "{action.action_name}" deleted.', 'success')
    return redirect(url_for('maintenance_action_sets.edit', action_set_id=action_set.id))


@bp.route(
    '/maintenance-action-sets/<int:action_set_id>/actions/<int:action_id>/move',
    methods=['POST'],
)
@login_required
def move_action(action_set_id, action_id):
    """Reorder actions by moving one action up or down within the set."""
    direction = request.form.get('direction')
    action_set = MaintenanceActionSet.query.get_or_404(action_set_id)
    action = Action.query.get_or_404(action_id)

    if action.maintenance_action_set_id != action_set.id:
        flash('Invalid action for this maintenance action set.', 'error')
        return redirect(url_for('maintenance_action_sets.edit', action_set_id=action_set.id))

    if direction not in ('up', 'down'):
        flash('Invalid move direction.', 'error')
        return redirect(url_for('maintenance_action_sets.edit', action_set_id=action_set.id))

    # Find neighbor based on sequence_order
    if direction == 'up':
        neighbor = (
            Action.query.filter_by(maintenance_action_set_id=action_set.id)
            .filter(Action.sequence_order < action.sequence_order)
            .order_by(Action.sequence_order.desc())
            .first()
        )
    else:  # down
        neighbor = (
            Action.query.filter_by(maintenance_action_set_id=action_set.id)
            .filter(Action.sequence_order > action.sequence_order)
            .order_by(Action.sequence_order.asc())
            .first()
        )

    if not neighbor:
        # Already at top or bottom
        return redirect(url_for('maintenance_action_sets.edit', action_set_id=action_set.id))

    # Swap sequence_order values
    action.sequence_order, neighbor.sequence_order = (
        neighbor.sequence_order,
        action.sequence_order,
    )

    db.session.commit()
    return redirect(url_for('maintenance_action_sets.edit', action_set_id=action_set.id))

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


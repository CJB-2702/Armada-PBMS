"""
Maintenance routes
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.data.maintenance.base.maintenance_plan import MaintenancePlan
from app.data.maintenance.base.maintenance_action_set import MaintenanceActionSet
from app.data.maintenance.base.action import Action
from app.data.core.asset_info.asset import Asset
from app.data.maintenance.templates.template_action_set import TemplateActionSet
from app.buisness.maintenance.maintenance_action_set_context import MaintenanceActionSetContext
from app.buisness.maintenance.factories.maintenance_action_set_factory import MaintenanceActionSetFactory
from app.services.maintenance.maintenance_service import MaintenanceService
from app.logger import get_logger
from app import db
from datetime import datetime

from .maintenance_plans import bp as maintenance_plans_bp
from .actions import bp as actions_bp

logger = get_logger("asset_management.routes.maintenance.main")

# Create main maintenance blueprint
maintenance_bp = Blueprint('maintenance', __name__, url_prefix='/maintenance')

# ROUTE_TYPE: WORK_PORTAL (Complex GET)
# This route coordinates multiple domain operations for dashboard statistics.
# Rationale: Aggregates statistics from multiple sources for dashboard view.
@maintenance_bp.route('/')
@login_required
def index():
    """Maintenance management dashboard with statistics and alerts"""
    logger.debug("Accessing maintenance management dashboard")
    
    # Get statistics from service
    core_stats = MaintenanceService.get_dashboard_statistics()
    template_stats = MaintenanceService.get_template_statistics()
    
    # Get alerts and recent items from service
    overdue_actions = MaintenanceService.get_overdue_actions(limit=10)
    due_soon_actions = MaintenanceService.get_due_soon_actions(limit=10, days=7)
    in_progress_actions = MaintenanceService.get_in_progress_actions(limit=10)
    recent_maintenance_plans = MaintenanceService.get_recent_maintenance_plans(limit=10)
    recent_actions = MaintenanceService.get_recent_actions(limit=10)
    
    # Get status breakdowns from service
    actions_by_status = MaintenanceService.get_actions_by_status()
    plans_by_status = MaintenanceService.get_plans_by_status()
    
    logger.info(f"Maintenance dashboard - Plans: {core_stats['total_maintenance_plans']}, Action Sets: {core_stats['total_maintenance_action_sets']}, Actions: {core_stats['total_actions']}")
    
    return render_template('maintenance/index.html',
                         # Core statistics
                         total_maintenance_plans=core_stats['total_maintenance_plans'],
                         total_maintenance_action_sets=core_stats['total_maintenance_action_sets'],
                         total_actions=core_stats['total_actions'],
                         total_part_demands=core_stats['total_part_demands'],
                         # Template statistics
                         total_template_action_sets=template_stats['total_template_action_sets'],
                         total_template_action_items=template_stats['total_template_action_items'],
                         total_template_part_demands=template_stats['total_template_part_demands'],
                         total_template_action_tools=template_stats['total_template_action_tools'],
                         # Alerts and recent items
                         overdue_actions=overdue_actions,
                         due_soon_actions=due_soon_actions,
                         in_progress_actions=in_progress_actions,
                         recent_maintenance_plans=recent_maintenance_plans,
                         recent_actions=recent_actions,
                         # Status breakdowns
                         actions_by_status=actions_by_status,
                         plans_by_status=plans_by_status)

@maintenance_bp.route('/create_maintenance_event', methods=['GET', 'POST'])
@login_required
def create_maintenance_event():
    """Create a new maintenance event from a template"""
    logger.debug(f"User {current_user.username} accessing create maintenance event")
    
    if request.method == 'POST':
        asset_id = request.form.get('asset_id', type=int)
        template_action_set_id = request.form.get('template_action_set_id', type=int)
        
        if not asset_id or not template_action_set_id:
            flash('Please select both an asset and a template action set', 'error')
            return redirect(url_for('maintenance.create_maintenance_event'))
        
        asset = Asset.query.get_or_404(asset_id)
        template_action_set = TemplateActionSet.query.get_or_404(template_action_set_id)
        
        try:
            # Create maintenance action set with actions from template
            action_set = MaintenanceActionSetFactory.create_with_actions_from_template(
                template_action_set=template_action_set,
                asset_id=asset_id,
                created_by_id=current_user.id,
                updated_by_id=current_user.id,
                scheduled_date=datetime.utcnow()
            )
            
            db.session.commit()
            
            logger.info(f"Created maintenance event {action_set.id} with actions for asset {asset.name}")
            flash(f'Maintenance event created for {asset.name} with {len(action_set.actions)} actions', 'success')
            
            return redirect(url_for('maintenance.do_maintenance', action_set_id=action_set.id))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating maintenance event: {e}")
            flash(f'Error creating maintenance event: {str(e)}', 'error')
            return redirect(url_for('maintenance.create_maintenance_event'))
    
    # GET request - show form
    form_options = MaintenanceService.get_create_event_form_options()
    
    return render_template('maintenance/create_maintenance_event.html',
                         assets=form_options['assets'],
                         template_action_sets=form_options['template_action_sets'])

@maintenance_bp.route('/do_maintenance/<int:action_set_id>')
@login_required
def do_maintenance(action_set_id):
    """Execute maintenance - view and update actions"""
    logger.debug(f"User {current_user.username} accessing do_maintenance for action set {action_set_id}")
    
    # Use MaintenanceActionSetContext for complex data aggregation
    context = MaintenanceActionSetContext(action_set_id)
    
    logger.info(f"Do maintenance page accessed for action set {context.action_set.id}")
    
    return render_template('maintenance/do_maintenance.html',
                         action_set=context.action_set,
                         event=context.event,
                         comments=context.comments,
                         actions=context.actions,
                         asset=context.asset,
                         part_demand_info=context.part_demand_info)

@maintenance_bp.route('/do_maintenance/<int:action_set_id>/add_comment', methods=['POST'])
@login_required
def add_comment(action_set_id):
    """Add a comment to the maintenance event"""
    context = MaintenanceActionSetContext(action_set_id)
    
    comment_content = request.form.get('comment_content')
    
    if comment_content and context.event:
        from app.buisness.core.event_context import EventContext
        event_context = EventContext(context.event.id)
        event_context.add_comment(
            user_id=current_user.id,
            content=comment_content
        )
        db.session.commit()
        
        flash('Comment added successfully', 'success')
    else:
        flash('Failed to add comment', 'error')
    
    return redirect(url_for('maintenance.do_maintenance', action_set_id=action_set_id))

@maintenance_bp.route('/do_maintenance/<int:action_set_id>/complete_action/<int:action_id>', methods=['POST'])
@login_required
def complete_action(action_set_id, action_id):
    """Mark an action as complete"""
    action = Action.query.get_or_404(action_id)
    
    if action.maintenance_action_set_id != action_set_id:
        flash('Invalid action for this maintenance event', 'error')
        return redirect(url_for('maintenance.do_maintenance', action_set_id=action_set_id))
    
    notes = request.form.get('completion_notes')
    billable_hours = request.form.get('billable_hours', type=float)
    
    action.complete_action(current_user.id, notes, 'Completed', billable_hours)
    db.session.commit()
    
    flash(f'Action "{action.action_name}" marked as complete', 'success')
    
    return redirect(url_for('maintenance.do_maintenance', action_set_id=action_set_id))

@maintenance_bp.route('/do_maintenance/<int:action_set_id>/start_action/<int:action_id>', methods=['POST'])
@login_required
def start_action(action_set_id, action_id):
    """Start an action"""
    action = Action.query.get_or_404(action_id)

    if action.maintenance_action_set_id != action_set_id:
        flash('Invalid action for this maintenance event', 'error')
        return redirect(url_for('maintenance.do_maintenance', action_set_id=action_set_id))

    # If this is the first action being started, ensure the maintenance event itself is started
    maintenance_action_set = action.maintenance_action_set
    if maintenance_action_set and maintenance_action_set.is_planned:
        maintenance_action_set.start_maintenance(current_user.id)

    action.start_action(current_user.id)
    db.session.commit()

    flash(f'Action "{action.action_name}" started', 'success')

    return redirect(url_for('maintenance.do_maintenance', action_set_id=action_set_id))

@maintenance_bp.route('/do_maintenance/<int:action_set_id>/skip_action/<int:action_id>', methods=['POST'])
@login_required
def skip_action(action_set_id, action_id):
    """Skip an action"""
    action = Action.query.get_or_404(action_id)
    
    if action.maintenance_action_set_id != action_set_id:
        flash('Invalid action for this maintenance event', 'error')
        return redirect(url_for('maintenance.do_maintenance', action_set_id=action_set_id))
    
    reason = request.form.get('skip_reason', '')
    if not reason:
        flash('Please provide a reason for skipping this action', 'error')
        return redirect(url_for('maintenance.do_maintenance', action_set_id=action_set_id))
    
    action.skip_action(current_user.id, reason)
    db.session.commit()
    
    flash(f'Action "{action.action_name}" skipped', 'success')
    
    return redirect(url_for('maintenance.do_maintenance', action_set_id=action_set_id))

@maintenance_bp.route('/do_maintenance/<int:action_set_id>/complete_maintenance', methods=['POST'])
@login_required
def complete_maintenance(action_set_id):
    """Complete the maintenance event - requires all actions to be completed or skipped"""
    action_set = MaintenanceActionSet.query.get_or_404(action_set_id)
    
    # Check if all actions are finished
    if not action_set.all_actions_finished:
        flash('All actions must be completed or skipped before marking maintenance as complete', 'error')
        return redirect(url_for('maintenance.do_maintenance', action_set_id=action_set_id))
    
    notes = request.form.get('completion_notes', '')
    if not notes:
        flash('Please provide completion notes', 'error')
        return redirect(url_for('maintenance.do_maintenance', action_set_id=action_set_id))
    
    action_set.complete_maintenance(current_user.id, notes)
    db.session.commit()
    
    flash('Maintenance event marked as complete', 'success')
    
    return redirect(url_for('maintenance.do_maintenance', action_set_id=action_set_id))

@maintenance_bp.route('/do_maintenance/<int:action_set_id>/delay_maintenance', methods=['POST'])
@login_required
def delay_maintenance(action_set_id):
    """Delay the maintenance event"""
    action_set = MaintenanceActionSet.query.get_or_404(action_set_id)
    
    reason = request.form.get('delay_reason', '')
    if not reason:
        flash('Please provide a reason for delaying this maintenance', 'error')
        return redirect(url_for('maintenance.do_maintenance', action_set_id=action_set_id))
    
    action_set.delay_maintenance(current_user.id, reason)
    db.session.commit()
    
    flash('Maintenance event marked as delayed', 'success')
    
    return redirect(url_for('maintenance.do_maintenance', action_set_id=action_set_id))

@maintenance_bp.route('/do_maintenance/<int:action_set_id>/cancel_maintenance', methods=['POST'])
@login_required
def cancel_maintenance(action_set_id):
    """Cancel the maintenance event"""
    action_set = MaintenanceActionSet.query.get_or_404(action_set_id)
    
    reason = request.form.get('cancel_reason', '')
    if not reason:
        flash('Please provide a reason for cancelling this maintenance', 'error')
        return redirect(url_for('maintenance.do_maintenance', action_set_id=action_set_id))
    
    action_set.cancel_maintenance(current_user.id, reason)
    db.session.commit()
    
    flash('Maintenance event cancelled', 'success')
    
    return redirect(url_for('maintenance.do_maintenance', action_set_id=action_set_id))

# Register sub-blueprints
maintenance_bp.register_blueprint(maintenance_plans_bp, url_prefix='/plans')
maintenance_bp.register_blueprint(actions_bp, url_prefix='/actions')


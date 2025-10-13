"""
Maintenance routes
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models.maintenance.base.maintenance_plan import MaintenancePlan
from app.models.maintenance.base.maintenance_action_set import MaintenanceActionSet
from app.models.maintenance.base.action import Action
from app.models.maintenance.base.part_demand import PartDemand
from app.models.maintenance.templates.template_action_set import TemplateActionSet
from app.models.maintenance.templates.template_action_item import TemplateActionItem
from app.models.maintenance.templates.template_part_demand import TemplatePartDemand
from app.models.maintenance.templates.template_action_tool import TemplateActionTool
from app.models.core.asset import Asset
from app.models.core.event import Event
from app.models.core.comment import Comment
from app.models.core.attachment import Attachment
from app.logger import get_logger
from app import db
from datetime import datetime, timedelta
from sqlalchemy import func

from .maintenance_plans import bp as maintenance_plans_bp
from .actions import bp as actions_bp

logger = get_logger("asset_management.routes.maintenance.main")

# Create main maintenance blueprint
maintenance_bp = Blueprint('maintenance', __name__, url_prefix='/maintenance')

@maintenance_bp.route('/')
@login_required
def index():
    """Maintenance management dashboard with statistics and alerts"""
    logger.debug("Accessing maintenance management dashboard")
    
    # Get core statistics
    total_maintenance_plans = MaintenancePlan.query.count()
    total_maintenance_action_sets = MaintenanceActionSet.query.count()
    total_actions = Action.query.count()
    total_part_demands = PartDemand.query.count()
    
    # Get template statistics
    total_template_action_sets = TemplateActionSet.query.count()
    total_template_action_items = TemplateActionItem.query.count()
    total_template_part_demands = TemplatePartDemand.query.count()
    total_template_action_tools = TemplateActionTool.query.count()
    
    # Get overdue actions (scheduled start time is in the past and not completed)
    today = datetime.utcnow()
    overdue_actions = Action.query.filter(
        Action.scheduled_start_time < today,
        Action.status.in_(['Not Started', 'In Progress'])
    ).limit(10).all()
    
    # Get actions due soon (within next 7 days)
    due_soon_date = today + timedelta(days=7)
    due_soon_actions = Action.query.filter(
        Action.scheduled_start_time.between(today, due_soon_date),
        Action.status == 'Not Started'
    ).limit(10).all()
    
    # Get actions in progress
    in_progress_actions = Action.query.filter(
        Action.status == 'In Progress'
    ).limit(10).all()
    
    # Get recent maintenance plans (last 10 created)
    recent_maintenance_plans = MaintenancePlan.query.order_by(MaintenancePlan.created_at.desc()).limit(10).all()
    
    # Get recent actions (last 10 created)
    recent_actions = Action.query.order_by(Action.created_at.desc()).limit(10).all()
    
    # Get actions by status
    actions_by_status = dict(
        db.session.query(Action.status, func.count(Action.id))
        .group_by(Action.status)
        .all()
    )
    
    # Get maintenance plans by status
    plans_by_status = dict(
        db.session.query(MaintenancePlan.status, func.count(MaintenancePlan.id))
        .group_by(MaintenancePlan.status)
        .all()
    )
    
    logger.info(f"Maintenance dashboard - Plans: {total_maintenance_plans}, Action Sets: {total_maintenance_action_sets}, Actions: {total_actions}")
    
    return render_template('maintenance/index.html',
                         # Core statistics
                         total_maintenance_plans=total_maintenance_plans,
                         total_maintenance_action_sets=total_maintenance_action_sets,
                         total_actions=total_actions,
                         total_part_demands=total_part_demands,
                         # Template statistics
                         total_template_action_sets=total_template_action_sets,
                         total_template_action_items=total_template_action_items,
                         total_template_part_demands=total_template_part_demands,
                         total_template_action_tools=total_template_action_tools,
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
            from app.models.maintenance.factories.maintenance_action_set_factory import MaintenanceActionSetFactory
            
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
    assets = Asset.query.filter_by(status='Active').order_by(Asset.name).all()
    template_action_sets = TemplateActionSet.query.order_by(TemplateActionSet.task_name).all()
    
    return render_template('maintenance/create_maintenance_event.html',
                         assets=assets,
                         template_action_sets=template_action_sets)

@maintenance_bp.route('/do_maintenance/<int:action_set_id>')
@login_required
def do_maintenance(action_set_id):
    """Execute maintenance - view and update actions"""
    logger.debug(f"User {current_user.username} accessing do_maintenance for action set {action_set_id}")
    
    action_set = MaintenanceActionSet.query.get_or_404(action_set_id)
    
    # Get the associated event
    event = Event.query.get(action_set.event_id) if action_set.event_id else None
    
    # Get comments for the event
    comments = []
    if event:
        comments = Comment.query.filter_by(event_id=event.id).order_by(Comment.created_at.desc()).all()
    
    # Get actions ordered by sequence
    actions = Action.query.filter_by(
        maintenance_action_set_id=action_set.id
    ).order_by(Action.sequence_order).all()
    
    # Get asset if available
    asset = Asset.query.get(action_set.asset_id) if action_set.asset_id else None
    
    logger.info(f"Do maintenance page accessed for action set {action_set.id}")
    
    return render_template('maintenance/do_maintenance.html',
                         action_set=action_set,
                         event=event,
                         comments=comments,
                         actions=actions,
                         asset=asset)

@maintenance_bp.route('/do_maintenance/<int:action_set_id>/add_comment', methods=['POST'])
@login_required
def add_comment(action_set_id):
    """Add a comment to the maintenance event"""
    action_set = MaintenanceActionSet.query.get_or_404(action_set_id)
    
    comment_content = request.form.get('comment_content')
    
    if comment_content and action_set.event_id:
        comment = Comment(
            content=comment_content,
            event_id=action_set.event_id,
            created_by_id=current_user.id
        )
        db.session.add(comment)
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
    
    action.start_action(current_user.id)
    db.session.commit()
    
    flash(f'Action "{action.action_name}" started', 'success')
    
    return redirect(url_for('maintenance.do_maintenance', action_set_id=action_set_id))

# Register sub-blueprints
maintenance_bp.register_blueprint(maintenance_plans_bp, url_prefix='/plans')
maintenance_bp.register_blueprint(actions_bp, url_prefix='/actions')


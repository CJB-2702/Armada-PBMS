"""
Template Action Item management routes
CRUD operations for TemplateActionItem model
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.models.maintenance.templates.template_action_item import TemplateActionItem
from app.models.maintenance.templates.template_action_set import TemplateActionSet
from app.models.maintenance.templates.template_part_demand import TemplatePartDemand
from app.models.maintenance.templates.template_action_tool import TemplateActionTool
from app import db
from app.logger import get_logger

logger = get_logger("asset_management.routes.maintenance.template_action_items")
bp = Blueprint('template_action_items', __name__)

@bp.route('/template-action-items')
@login_required
def list():
    """List all template action items with basic filtering"""
    logger.debug(f"User {current_user.username} accessing template action items list")
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Basic filtering
    template_action_set_id = request.args.get('template_action_set_id', type=int)
    action_name = request.args.get('action_name')
    is_required = request.args.get('is_required')
    
    logger.debug(f"Template action items list filters - Set: {template_action_set_id}, Name: {action_name}")
    
    query = TemplateActionItem.query
    
    if template_action_set_id:
        query = query.filter(TemplateActionItem.template_action_set_id == template_action_set_id)
    
    if action_name:
        query = query.filter(TemplateActionItem.action_name.ilike(f'%{action_name}%'))
    
    if is_required is not None:
        query = query.filter(TemplateActionItem.is_required == (is_required.lower() == 'true'))
    
    # Order by creation date (newest first)
    query = query.order_by(TemplateActionItem.created_at.desc())
    
    # Pagination
    template_action_items = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Get filter options
    template_action_sets = TemplateActionSet.query.all()
    
    logger.info(f"Template action items list returned {template_action_items.total} items (page {page})")
    
    return render_template('maintenance/template_action_items/list.html', 
                         template_action_items=template_action_items,
                         template_action_sets=template_action_sets,
                         filters={'template_action_set_id': template_action_set_id,
                                'action_name': action_name,
                                'is_required': is_required
                         })

@bp.route('/template-action-items/<int:template_action_item_id>')
@login_required
def detail(template_action_item_id):
    """View individual template action item details"""
    logger.debug(f"User {current_user.username} accessing template action item detail for ID: {template_action_item_id}")
    
    template_action_item = TemplateActionItem.query.get_or_404(template_action_item_id)
    
    # Get related data through relationships
    template_action_set = template_action_item.template_action_set
    template_part_demands = TemplatePartDemand.query.filter_by(
        template_action_item_id=template_action_item.id
    ).all()
    template_action_tools = TemplateActionTool.query.filter_by(
        template_action_item_id=template_action_item.id
    ).all()
    
    logger.info(f"Template action item detail accessed - Item: {template_action_item.action_name} (ID: {template_action_item_id})")
    
    return render_template('maintenance/template_action_items/detail.html', 
                         template_action_item=template_action_item,
                         template_action_set=template_action_set,
                         template_part_demands=template_part_demands,
                         template_action_tools=template_action_tools)

@bp.route('/template-action-items/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create new template action item"""
    if request.method == 'POST':
        # Validate form data
        template_action_set_id = request.form.get('template_action_set_id', type=int)
        action_name = request.form.get('action_name')
        description = request.form.get('description')
        sequence_order = request.form.get('sequence_order', type=int)
        is_required = request.form.get('is_required', type=bool, default=True)
        minimum_staff_count = request.form.get('minimum_staff_count', type=int, default=1)
        instructions = request.form.get('instructions')
        instructions_type = request.form.get('instructions_type')
        required_skills = request.form.get('required_skills')
        estimated_duration_hours = request.form.get('estimated_duration_hours', type=float)
        
        # Create new template action item
        template_action_item = TemplateActionItem(
            template_action_set_id=template_action_set_id,
            action_name=action_name,
            description=description,
            sequence_order=sequence_order,
            is_required=is_required,
            minimum_staff_count=minimum_staff_count,
            instructions=instructions,
            instructions_type=instructions_type,
            required_skills=required_skills,
            estimated_duration_hours=estimated_duration_hours,
            created_by_id=current_user.id,
            updated_by_id=current_user.id
        )
        
        db.session.add(template_action_item)
        db.session.commit()
        
        flash('Template action item created successfully', 'success')
        return redirect(url_for('template_action_items.detail', template_action_item_id=template_action_item.id))
    
    # Get form options
    template_action_sets = TemplateActionSet.query.all()
    
    return render_template('maintenance/template_action_items/create.html',
                         template_action_sets=template_action_sets)

@bp.route('/template-action-items/<int:template_action_item_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(template_action_item_id):
    """Edit template action item"""
    template_action_item = TemplateActionItem.query.get_or_404(template_action_item_id)
    
    if request.method == 'POST':
        # Validate form data
        action_name = request.form.get('action_name')
        description = request.form.get('description')
        sequence_order = request.form.get('sequence_order', type=int)
        is_required = request.form.get('is_required') == 'true'
        minimum_staff_count = request.form.get('minimum_staff_count', type=int)
        instructions = request.form.get('instructions')
        instructions_type = request.form.get('instructions_type')
        required_skills = request.form.get('required_skills')
        estimated_duration_hours = request.form.get('estimated_duration_hours', type=float)
        
        # Update template action item
        template_action_item.action_name = action_name
        template_action_item.description = description
        template_action_item.sequence_order = sequence_order
        template_action_item.is_required = is_required
        template_action_item.minimum_staff_count = minimum_staff_count
        template_action_item.instructions = instructions
        template_action_item.instructions_type = instructions_type
        template_action_item.required_skills = required_skills
        template_action_item.estimated_duration_hours = estimated_duration_hours
        template_action_item.updated_by_id = current_user.id
        
        db.session.commit()
        
        flash('Template action item updated successfully', 'success')
        return redirect(url_for('template_action_items.detail', template_action_item_id=template_action_item.id))
    
    # Get form options
    template_action_sets = TemplateActionSet.query.all()
    
    return render_template('maintenance/template_action_items/edit.html',
                         template_action_item=template_action_item,
                         template_action_sets=template_action_sets)

@bp.route('/template-action-items/<int:template_action_item_id>/delete', methods=['POST'])
@login_required
def delete(template_action_item_id):
    """Delete template action item"""
    template_action_item = TemplateActionItem.query.get_or_404(template_action_item_id)
    
    # Check if template action item has associated data
    if template_action_item.actions.count() > 0:
        flash('Cannot delete template action item that has been used in actions', 'error')
        return redirect(url_for('template_action_items.detail', template_action_item_id=template_action_item_id))
    
    action_name = template_action_item.action_name
    
    db.session.delete(template_action_item)
    db.session.commit()
    
    flash(f'Template action item "{action_name}" deleted successfully', 'success')
    return redirect(url_for('template_action_items.list'))


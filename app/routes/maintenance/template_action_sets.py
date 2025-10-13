"""
Template Action Set management routes
CRUD operations for TemplateActionSet model
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.models.maintenance.templates.template_action_set import TemplateActionSet
from app.models.maintenance.templates.template_action_item import TemplateActionItem
from app import db
from app.logger import get_logger

logger = get_logger("asset_management.routes.maintenance.template_action_sets")
bp = Blueprint('template_action_sets', __name__)

@bp.route('/template-action-sets')
@login_required
def list():
    """List all template action sets with basic filtering"""
    logger.debug(f"User {current_user.username} accessing template action sets list")
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Basic filtering
    task_name = request.args.get('task_name')
    
    logger.debug(f"Template action sets list filters - Task Name: {task_name}")
    
    query = TemplateActionSet.query
    
    if task_name:
        query = query.filter(TemplateActionSet.task_name.ilike(f'%{task_name}%'))
    
    # Order by creation date (newest first)
    query = query.order_by(TemplateActionSet.created_at.desc())
    
    # Pagination
    template_action_sets = query.paginate(page=page, per_page=per_page, error_out=False)
    
    logger.info(f"Template action sets list returned {template_action_sets.total} items (page {page})")
    
    return render_template('maintenance/template_action_sets/list.html', 
                         template_action_sets=template_action_sets,
                         filters={'task_name': task_name})

@bp.route('/template-action-sets/<int:template_action_set_id>')
@login_required
def detail(template_action_set_id):
    """View individual template action set details"""
    logger.debug(f"User {current_user.username} accessing template action set detail for ID: {template_action_set_id}")
    
    template_action_set = TemplateActionSet.query.get_or_404(template_action_set_id)
    
    # Get template action items for this template action set
    template_action_items = TemplateActionItem.query.filter_by(
        template_action_set_id=template_action_set.id
    ).order_by(TemplateActionItem.sequence_order).all()
    
    logger.info(f"Template action set detail accessed - Set: {template_action_set.task_name} (ID: {template_action_set_id})")
    
    return render_template('maintenance/template_action_sets/detail.html', 
                         template_action_set=template_action_set,
                         template_action_items=template_action_items)

@bp.route('/template-action-sets/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create new template action set"""
    if request.method == 'POST':
        # Validate form data
        task_name = request.form.get('task_name')
        task_description = request.form.get('task_description')
        estimated_duration_hours = request.form.get('estimated_duration_hours', type=float)
        task_category = request.form.get('task_category')
        
        # Create new template action set
        template_action_set = TemplateActionSet(
            task_name=task_name,
            task_description=task_description,
            estimated_duration_hours=estimated_duration_hours,
            task_category=task_category,
            created_by_id=current_user.id,
            updated_by_id=current_user.id
        )
        
        db.session.add(template_action_set)
        db.session.commit()
        
        flash('Template action set created successfully', 'success')
        return redirect(url_for('template_action_sets.detail', template_action_set_id=template_action_set.id))
    
    return render_template('maintenance/template_action_sets/create.html')

@bp.route('/template-action-sets/<int:template_action_set_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(template_action_set_id):
    """Edit template action set"""
    template_action_set = TemplateActionSet.query.get_or_404(template_action_set_id)
    
    if request.method == 'POST':
        # Validate form data
        task_name = request.form.get('task_name')
        task_description = request.form.get('task_description')
        estimated_duration_hours = request.form.get('estimated_duration_hours', type=float)
        task_category = request.form.get('task_category')
        
        # Update template action set
        template_action_set.task_name = task_name
        template_action_set.task_description = task_description
        template_action_set.estimated_duration_hours = estimated_duration_hours
        template_action_set.task_category = task_category
        template_action_set.updated_by_id = current_user.id
        
        db.session.commit()
        
        flash('Template action set updated successfully', 'success')
        return redirect(url_for('template_action_sets.detail', template_action_set_id=template_action_set.id))
    
    return render_template('maintenance/template_action_sets/edit.html',
                         template_action_set=template_action_set)

@bp.route('/template-action-sets/<int:template_action_set_id>/delete', methods=['POST'])
@login_required
def delete(template_action_set_id):
    """Delete template action set"""
    template_action_set = TemplateActionSet.query.get_or_404(template_action_set_id)
    
    # Check if template action set has template action items
    if template_action_set.template_action_items:
        flash('Cannot delete template action set with template action items', 'error')
        return redirect(url_for('template_action_sets.detail', template_action_set_id=template_action_set_id))
    
    task_name = template_action_set.task_name
    
    db.session.delete(template_action_set)
    db.session.commit()
    
    flash(f'Template action set "{task_name}" deleted successfully', 'success')
    return redirect(url_for('template_action_sets.list'))


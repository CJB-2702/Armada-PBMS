"""
Template Action Tool management routes
CRUD operations for TemplateActionTool model
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.models.maintenance.templates.template_action_tool import TemplateActionTool
from app.models.maintenance.templates.template_action_item import TemplateActionItem
from app.models.supply_items.tool import Tool
from app import db
from app.logger import get_logger

logger = get_logger("asset_management.routes.maintenance.template_action_tools")
bp = Blueprint('template_action_tools', __name__)

@bp.route('/template-action-tools')
@login_required
def list():
    """List all template action tools with basic filtering"""
    logger.debug(f"User {current_user.username} accessing template action tools list")
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Basic filtering
    template_action_item_id = request.args.get('template_action_item_id', type=int)
    tool_id = request.args.get('tool_id', type=int)
    is_required = request.args.get('is_required')
    
    logger.debug(f"Template action tools list filters - Action Item: {template_action_item_id}, Tool: {tool_id}")
    
    query = TemplateActionTool.query
    
    if template_action_item_id:
        query = query.filter(TemplateActionTool.template_action_item_id == template_action_item_id)
    
    if tool_id:
        query = query.filter(TemplateActionTool.tool_id == tool_id)
    
    if is_required is not None:
        query = query.filter(TemplateActionTool.is_required == (is_required.lower() == 'true'))
    
    # Order by creation date (newest first)
    query = query.order_by(TemplateActionTool.created_at.desc())
    
    # Pagination
    template_action_tools = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Get filter options
    template_action_items = TemplateActionItem.query.all()
    tools = Tool.query.all()
    
    logger.info(f"Template action tools list returned {template_action_tools.total} items (page {page})")
    
    return render_template('maintenance/template_action_tools/list.html', 
                         template_action_tools=template_action_tools,
                         template_action_items=template_action_items,
                         tools=tools,
                         filters={'template_action_item_id': template_action_item_id,
                                'tool_id': tool_id,
                                'is_required': is_required
                         })

@bp.route('/template-action-tools/<int:template_action_tool_id>')
@login_required
def detail(template_action_tool_id):
    """View individual template action tool details"""
    logger.debug(f"User {current_user.username} accessing template action tool detail for ID: {template_action_tool_id}")
    
    template_action_tool = TemplateActionTool.query.get_or_404(template_action_tool_id)
    
    # Get related data through relationships
    template_action_item = template_action_tool.template_action_item
    tool = template_action_tool.tool
    
    logger.info(f"Template action tool detail accessed - Tool: {tool.tool_name if tool else 'N/A'} (ID: {template_action_tool_id})")
    
    return render_template('maintenance/template_action_tools/detail.html', 
                         template_action_tool=template_action_tool,
                         template_action_item=template_action_item,
                         tool=tool)

@bp.route('/template-action-tools/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create new template action tool"""
    if request.method == 'POST':
        # Validate form data
        template_action_item_id = request.form.get('template_action_item_id', type=int)
        tool_id = request.form.get('tool_id', type=int)
        is_required = request.form.get('is_required') == 'true'
        quantity_required = request.form.get('quantity_required', type=int, default=1)
        sequence_order = request.form.get('sequence_order', type=int, default=1)
        notes = request.form.get('notes')
        
        # Create new template action tool
        template_action_tool = TemplateActionTool(
            template_action_item_id=template_action_item_id,
            tool_id=tool_id,
            is_required=is_required,
            quantity_required=quantity_required,
            sequence_order=sequence_order,
            notes=notes,
            created_by_id=current_user.id,
            updated_by_id=current_user.id
        )
        
        db.session.add(template_action_tool)
        db.session.commit()
        
        flash('Template action tool created successfully', 'success')
        return redirect(url_for('template_action_tools.detail', template_action_tool_id=template_action_tool.id))
    
    # Get form options
    template_action_items = TemplateActionItem.query.all()
    tools = Tool.query.all()
    
    return render_template('maintenance/template_action_tools/create.html',
                         template_action_items=template_action_items,
                         tools=tools)

@bp.route('/template-action-tools/<int:template_action_tool_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(template_action_tool_id):
    """Edit template action tool"""
    template_action_tool = TemplateActionTool.query.get_or_404(template_action_tool_id)
    
    if request.method == 'POST':
        # Validate form data
        tool_id = request.form.get('tool_id', type=int)
        is_required = request.form.get('is_required') == 'true'
        quantity_required = request.form.get('quantity_required', type=int)
        sequence_order = request.form.get('sequence_order', type=int)
        notes = request.form.get('notes')
        
        # Update template action tool
        template_action_tool.tool_id = tool_id
        template_action_tool.is_required = is_required
        template_action_tool.quantity_required = quantity_required
        template_action_tool.sequence_order = sequence_order
        template_action_tool.notes = notes
        template_action_tool.updated_by_id = current_user.id
        
        db.session.commit()
        
        flash('Template action tool updated successfully', 'success')
        return redirect(url_for('template_action_tools.detail', template_action_tool_id=template_action_tool.id))
    
    # Get form options
    tools = Tool.query.all()
    
    return render_template('maintenance/template_action_tools/edit.html',
                         template_action_tool=template_action_tool,
                         tools=tools)

@bp.route('/template-action-tools/<int:template_action_tool_id>/delete', methods=['POST'])
@login_required
def delete(template_action_tool_id):
    """Delete template action tool"""
    template_action_tool = TemplateActionTool.query.get_or_404(template_action_tool_id)
    
    db.session.delete(template_action_tool)
    db.session.commit()
    
    flash('Template action tool deleted successfully', 'success')
    return redirect(url_for('template_action_tools.list'))


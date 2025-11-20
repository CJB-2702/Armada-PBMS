"""
Tool management routes
CRUD operations for Tool model
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.data.supply_items.tool import Tool
from app.data.supply_items.issuable_tool import IssuableTool
from app.data.core.user_info.user import User
from app.buisness.inventory.tool_context import ToolContext
from app import db
from app.logger import get_logger

logger = get_logger("asset_management.routes.supply.tools")
bp = Blueprint('tools', __name__)

# ROUTE_TYPE: SIMPLE_CRUD (GET)
# EXCEPTION: Direct ORM usage allowed for simple GET operations on Tool/IssuableTool
# This route performs basic list operations with minimal filtering and business logic.
# Rationale: Simple pagination and filtering on single entity type doesn't require domain abstraction.
# NOTE: CREATE/DELETE operations should use domain managers - see create() and delete() routes
@bp.route('/tools')
@login_required
def list():
    """List all tools with basic filtering"""
    logger.debug(f"User {current_user.username} accessing tools list")
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Basic filtering
    tool_type = request.args.get('tool_type')
    status = request.args.get('status')
    manufacturer = request.form.get('manufacturer')
    tool_name = request.args.get('tool_name')
    assigned_to_id = request.args.get('assigned_to_id', type=int)
    
    logger.debug(f"Tools list filters - Type: {tool_type}, Status: {status}, Assigned: {assigned_to_id}")
    
    # For issuance-related filtering, we need to use IssuableTool
    if status or assigned_to_id:
        # Query IssuableTool instances with their associated Tool information
        query = db.session.query(IssuableTool).join(Tool)
        
        if status:
            query = query.filter(IssuableTool.status == status)
        
        if assigned_to_id:
            query = query.filter(IssuableTool.assigned_to_id == assigned_to_id)
        
        # Apply tool definition filters to the joined Tool
        if tool_type:
            query = query.filter(Tool.tool_type == tool_type)
        
        if manufacturer:
            query = query.filter(Tool.manufacturer.ilike(f'%{manufacturer}%'))
        
        if tool_name:
            query = query.filter(Tool.tool_name.ilike(f'%{tool_name}%'))
        
        # Order by tool name
        query = query.order_by(Tool.tool_name)
        
        # Pagination for issuable tools
        tools = query.paginate(page=page, per_page=per_page, error_out=False)
        is_issuable_list = True
    else:
        # For tool definition filtering only, use Tool directly
        query = Tool.query
        
        if tool_type:
            query = query.filter(Tool.tool_type == tool_type)
        
        if manufacturer:
            query = query.filter(Tool.manufacturer.ilike(f'%{manufacturer}%'))
        
        if tool_name:
            query = query.filter(Tool.tool_name.ilike(f'%{tool_name}%'))
        
        # Order by tool name
        query = query.order_by(Tool.tool_name)
        
        # Pagination for tool definitions
        tools = query.paginate(page=page, per_page=per_page, error_out=False)
        is_issuable_list = False
    
    # Get filter options
    tool_types = db.session.query(Tool.tool_type).distinct().all()
    tool_types = [tt[0] for tt in tool_types if tt[0]]
    
    manufacturers = db.session.query(Tool.manufacturer).distinct().all()
    manufacturers = [man[0] for man in manufacturers if man[0]]
    
    users = User.query.all()
    
    logger.info(f"Tools list returned {tools.total} tools (page {page})")
    
    return render_template('supply/tools/list.html', 
                         tools=tools,
                         tool_types=tool_types,
                         manufacturers=manufacturers,
                         users=users,
                         is_issuable_list=is_issuable_list,
                         current_filters={
                             'tool_type': tool_type,
                             'status': status,
                             'manufacturer': manufacturer,
                             'tool_name': tool_name,
                             'assigned_to_id': assigned_to_id
                         })

@bp.route('/tools/<int:tool_id>')
@login_required
def detail(tool_id):
    """View individual tool details"""
    logger.debug(f"User {current_user.username} accessing tool detail for tool ID: {tool_id}")
    
    # Use ToolContext to handle Tool vs IssuableTool complexity
    context = ToolContext(tool_id)
    
    logger.info(f"Tool detail accessed - Tool: {context.tool.tool_name} (ID: {tool_id})")
    
    return render_template('supply/tools/detail.html', 
                         tool=context.tool,
                         assigned_to=context.assigned_to)

@bp.route('/tools/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create new tool"""
    if request.method == 'POST':
        # Validate form data
        tool_name = request.form.get('tool_name')
        description = request.form.get('description')
        tool_type = request.form.get('tool_type')
        manufacturer = request.form.get('manufacturer')
        model_number = request.form.get('model_number')
        serial_number = request.form.get('serial_number')
        location = request.form.get('location')
        status = request.form.get('status', 'Available')
        last_calibration_date = request.form.get('last_calibration_date')
        next_calibration_date = request.form.get('next_calibration_date')
        assigned_to_id = request.form.get('assigned_to_id', type=int)
        
        # Create new tool
        tool = Tool(
            tool_name=tool_name,
            description=description,
            tool_type=tool_type,
            manufacturer=manufacturer,
            model_number=model_number,
            serial_number=serial_number,
            location=location,
            status=status,
            last_calibration_date=last_calibration_date if last_calibration_date else None,
            next_calibration_date=next_calibration_date if next_calibration_date else None,
            assigned_to_id=assigned_to_id,
            created_by_id=current_user.id,
            updated_by_id=current_user.id
        )
        
        db.session.add(tool)
        db.session.commit()
        
        flash('Tool created successfully', 'success')
        return redirect(url_for('supply.tools.detail', tool_id=tool.id))
    
    # Get form options
    users = User.query.all()
    
    return render_template('supply/tools/create.html', users=users)

# ROUTE_TYPE: SIMPLE_CRUD (EDIT)
# EXCEPTION: Direct ORM usage allowed for simple EDIT operations on Tool/IssuableTool
# This route performs basic update operations with minimal business logic.
# Rationale: Simple tool update doesn't require domain abstraction. ToolContext is used for detail view.
# NOTE: CREATE/DELETE operations should use domain managers - see create() and delete() routes
@bp.route('/tools/<int:tool_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(tool_id):
    """Edit tool"""
    tool = Tool.query.get_or_404(tool_id)
    
    if request.method == 'POST':
        # Validate form data
        tool_name = request.form.get('tool_name')
        description = request.form.get('description')
        tool_type = request.form.get('tool_type')
        manufacturer = request.form.get('manufacturer')
        model_number = request.form.get('model_number')
        serial_number = request.form.get('serial_number')
        location = request.form.get('location')
        status = request.form.get('status')
        last_calibration_date = request.form.get('last_calibration_date')
        next_calibration_date = request.form.get('next_calibration_date')
        assigned_to_id = request.form.get('assigned_to_id', type=int)
        
        # Check if this is an IssuableTool or Tool
        issuable_tool = IssuableTool.query.get(tool_id)
        
        if issuable_tool:
            # It's an IssuableTool - update both the base tool and issuance fields
            # Update base tool fields through the relationship
            issuable_tool.tool.tool_name = tool_name
            issuable_tool.tool.description = description
            issuable_tool.tool.tool_type = tool_type
            issuable_tool.tool.manufacturer = manufacturer
            issuable_tool.tool.model_number = model_number
            
            # Update issuance-specific fields
            issuable_tool.serial_number = serial_number
            issuable_tool.location = location
            issuable_tool.status = status
            issuable_tool.last_calibration_date = last_calibration_date if last_calibration_date else None
            issuable_tool.next_calibration_date = next_calibration_date if next_calibration_date else None
            issuable_tool.assigned_to_id = assigned_to_id
            issuable_tool.updated_by_id = current_user.id
        else:
            # It's a Tool definition - only update base tool fields
            tool.tool_name = tool_name
            tool.description = description
            tool.tool_type = tool_type
            tool.manufacturer = manufacturer
            tool.model_number = model_number
            tool.updated_by_id = current_user.id
        
        db.session.commit()
        
        flash('Tool updated successfully', 'success')
        return redirect(url_for('supply.tools.detail', tool_id=tool.id))
    
    # Get form options
    users = User.query.all()
    
    return render_template('supply/tools/edit.html', tool=tool, users=users)

@bp.route('/tools/<int:tool_id>/assign', methods=['POST'])
@login_required
def assign_tool(tool_id):
    """Assign tool to a user"""
    # Check if this is an IssuableTool ID or Tool ID
    issuable_tool = IssuableTool.query.get(tool_id)
    if issuable_tool:
        # It's an IssuableTool
        user_id = request.form.get('user_id', type=int)
        
        if not user_id:
            flash('Please select a user', 'error')
            return redirect(url_for('supply.tools.detail', tool_id=tool_id))
        
        issuable_tool.assign_to_user(user_id)
        issuable_tool.updated_by_id = current_user.id
        db.session.commit()
        
        flash('Tool assigned successfully', 'success')
        return redirect(url_for('supply.tools.detail', tool_id=tool_id))
    else:
        # It might be a Tool ID, but we can't assign a tool definition
        flash('Cannot assign a tool definition. Please select a specific tool instance.', 'error')
        return redirect(url_for('supply.tools.detail', tool_id=tool_id))

@bp.route('/tools/<int:tool_id>/unassign', methods=['POST'])
@login_required
def unassign_tool(tool_id):
    """Unassign tool from user"""
    # Check if this is an IssuableTool ID or Tool ID
    issuable_tool = IssuableTool.query.get(tool_id)
    if issuable_tool:
        # It's an IssuableTool
        issuable_tool.unassign()
        issuable_tool.updated_by_id = current_user.id
        db.session.commit()
        
        flash('Tool unassigned successfully', 'success')
        return redirect(url_for('supply.tools.detail', tool_id=tool_id))
    else:
        # It might be a Tool ID, but we can't unassign a tool definition
        flash('Cannot unassign a tool definition. Please select a specific tool instance.', 'error')
        return redirect(url_for('supply.tools.detail', tool_id=tool_id))

@bp.route('/tools/<int:tool_id>/mark-repair', methods=['POST'])
@login_required
def mark_for_repair(tool_id):
    """Mark tool as out for repair"""
    # Check if this is an IssuableTool ID or Tool ID
    issuable_tool = IssuableTool.query.get(tool_id)
    if issuable_tool:
        # It's an IssuableTool
        issuable_tool.mark_for_repair()
        issuable_tool.updated_by_id = current_user.id
        db.session.commit()
        
        flash('Tool marked for repair', 'success')
        return redirect(url_for('supply.tools.detail', tool_id=tool_id))
    else:
        # It might be a Tool ID, but we can't mark a tool definition for repair
        flash('Cannot mark a tool definition for repair. Please select a specific tool instance.', 'error')
        return redirect(url_for('supply.tools.detail', tool_id=tool_id))

@bp.route('/tools/<int:tool_id>/retire', methods=['POST'])
@login_required
def retire_tool(tool_id):
    """Retire tool"""
    # Check if this is an IssuableTool ID or Tool ID
    issuable_tool = IssuableTool.query.get(tool_id)
    if issuable_tool:
        # It's an IssuableTool
        issuable_tool.retire()
        issuable_tool.updated_by_id = current_user.id
        db.session.commit()
        
        flash('Tool retired successfully', 'success')
        return redirect(url_for('supply.tools.detail', tool_id=tool_id))
    else:
        # It might be a Tool ID, but we can't retire a tool definition
        flash('Cannot retire a tool definition. Please select a specific tool instance.', 'error')
        return redirect(url_for('supply.tools.detail', tool_id=tool_id))

@bp.route('/tools/<int:tool_id>/update-calibration', methods=['POST'])
@login_required
def update_calibration(tool_id):
    """Update calibration dates for tool"""
    # Check if this is an IssuableTool ID or Tool ID
    issuable_tool = IssuableTool.query.get(tool_id)
    if issuable_tool:
        # It's an IssuableTool
        calibration_date = request.form.get('calibration_date')
        next_calibration_date = request.form.get('next_calibration_date')
        
        if not calibration_date:
            flash('Calibration date is required', 'error')
            return redirect(url_for('supply.tools.detail', tool_id=tool_id))
        
        issuable_tool.update_calibration(calibration_date, next_calibration_date)
        issuable_tool.updated_by_id = current_user.id
        db.session.commit()
        
        flash('Calibration updated successfully', 'success')
        return redirect(url_for('supply.tools.detail', tool_id=tool_id))
    else:
        # It might be a Tool ID, but we can't update calibration for a tool definition
        flash('Cannot update calibration for a tool definition. Please select a specific tool instance.', 'error')
        return redirect(url_for('supply.tools.detail', tool_id=tool_id))

@bp.route('/tools/<int:tool_id>/delete', methods=['POST'])
@login_required
def delete(tool_id):
    """Delete tool"""
    tool = Tool.query.get_or_404(tool_id)
    
    db.session.delete(tool)
    db.session.commit()
    
    flash('Tool deleted successfully', 'success')
    return redirect(url_for('supply.tools.list'))


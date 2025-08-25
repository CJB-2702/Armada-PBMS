"""
Tools management routes
CRUD operations for Tool model
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from app.logger import get_logger
from flask_login import login_required, current_user
from app.models.supply.tool import Tool
from app.models.core.user import User
from app import db
from datetime import datetime

bp = Blueprint('tools', __name__)
logger = get_logger("asset_management.routes.supply.tools")

@bp.route('/supply/tools')
@login_required
def list():
    """List all tools"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Basic filtering
    tool_type = request.args.get('tool_type')
    status = request.args.get('status')
    assigned_to = request.args.get('assigned_to')
    
    query = Tool.query
    
    if tool_type:
        query = query.filter(Tool.tool_type == tool_type)
    
    if status:
        query = query.filter(Tool.status == status)
    
    if assigned_to:
        if assigned_to == 'unassigned':
            query = query.filter(Tool.assigned_to_id.is_(None))
        else:
            query = query.filter(Tool.assigned_to_id == assigned_to)
    
    # Order by tool name
    query = query.order_by(Tool.tool_name)
    
    # Pagination
    tools = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Get unique tool types for filter
    tool_types = db.session.query(Tool.tool_type).distinct().filter(Tool.tool_type.isnot(None)).all()
    tool_types = [tt[0] for tt in tool_types]
    
    # Get users for assignment filter
    users = User.query.filter(User.is_active == True).order_by(User.username).all()
    
    return render_template('supply/tools/list.html', tools=tools, tool_types=tool_types, users=users)

@bp.route('/supply/tools/<int:tool_id>')
@login_required
def detail(tool_id):
    """View tool details"""
    tool = Tool.query.get_or_404(tool_id)
    
    return render_template('supply/tools/detail.html', tool=tool)

@bp.route('/supply/tools/create', methods=['GET', 'POST'])
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
        assigned_to_id = request.form.get('assigned_to_id')
        last_calibration_date = request.form.get('last_calibration_date')
        next_calibration_date = request.form.get('next_calibration_date')
        
        # Validate required fields
        if not tool_name:
            flash('Tool name is required', 'error')
            return render_template('supply/tools/create.html')
        
        # Convert dates
        try:
            last_calibration_date = datetime.strptime(last_calibration_date, '%Y-%m-%d').date() if last_calibration_date else None
            next_calibration_date = datetime.strptime(next_calibration_date, '%Y-%m-%d').date() if next_calibration_date else None
        except ValueError:
            flash('Invalid date format for calibration dates', 'error')
            return render_template('supply/tools/create.html')
        
        # Convert assigned_to_id
        if assigned_to_id:
            try:
                assigned_to_id = int(assigned_to_id)
            except ValueError:
                assigned_to_id = None
        
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
            assigned_to_id=assigned_to_id,
            last_calibration_date=last_calibration_date,
            next_calibration_date=next_calibration_date
        )
        
        try:
            db.session.add(tool)
            db.session.commit()
            flash(f'Tool "{tool.tool_name}" created successfully', 'success')
            logger.info(f"User {current_user.username} created tool {tool.tool_name}")
            return redirect(url_for('supply.tools.detail', tool_id=tool.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating tool: {str(e)}', 'error')
            logger.error(f"Error creating tool: {str(e)}")
            return render_template('supply/tools/create.html')
    
    # Get users for assignment dropdown
    users = User.query.filter(User.is_active == True).order_by(User.username).all()
    
    return render_template('supply/tools/create.html', users=users)

@bp.route('/supply/tools/<int:tool_id>/edit', methods=['GET', 'POST'])
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
        assigned_to_id = request.form.get('assigned_to_id')
        last_calibration_date = request.form.get('last_calibration_date')
        next_calibration_date = request.form.get('next_calibration_date')
        
        # Validate required fields
        if not tool_name:
            flash('Tool name is required', 'error')
            return render_template('supply/tools/edit.html', tool=tool)
        
        # Convert dates
        try:
            last_calibration_date = datetime.strptime(last_calibration_date, '%Y-%m-%d').date() if last_calibration_date else None
            next_calibration_date = datetime.strptime(next_calibration_date, '%Y-%m-%d').date() if next_calibration_date else None
        except ValueError:
            flash('Invalid date format for calibration dates', 'error')
            return render_template('supply/tools/edit.html', tool=tool)
        
        # Convert assigned_to_id
        if assigned_to_id:
            try:
                assigned_to_id = int(assigned_to_id)
            except ValueError:
                assigned_to_id = None
        
        # Update tool
        tool.tool_name = tool_name
        tool.description = description
        tool.tool_type = tool_type
        tool.manufacturer = manufacturer
        tool.model_number = model_number
        tool.serial_number = serial_number
        tool.location = location
        tool.status = status
        tool.assigned_to_id = assigned_to_id
        tool.last_calibration_date = last_calibration_date
        tool.next_calibration_date = next_calibration_date
        
        try:
            db.session.commit()
            flash(f'Tool "{tool.tool_name}" updated successfully', 'success')
            logger.info(f"User {current_user.username} updated tool {tool.tool_name}")
            return redirect(url_for('supply.tools.detail', tool_id=tool.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating tool: {str(e)}', 'error')
            logger.error(f"Error updating tool: {str(e)}")
            return render_template('supply/tools/edit.html', tool=tool)
    
    # Get users for assignment dropdown
    users = User.query.filter(User.is_active == True).order_by(User.username).all()
    
    return render_template('supply/tools/edit.html', tool=tool, users=users)

@bp.route('/supply/tools/<int:tool_id>/delete', methods=['POST'])
@login_required
def delete(tool_id):
    """Delete tool"""
    tool = Tool.query.get_or_404(tool_id)
    
    try:
        db.session.delete(tool)
        db.session.commit()
        flash(f'Tool "{tool.tool_name}" deleted successfully', 'success')
        logger.info(f"User {current_user.username} deleted tool {tool.tool_name}")
        return redirect(url_for('supply.tools.list'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting tool: {str(e)}', 'error')
        logger.error(f"Error deleting tool: {str(e)}")
        return redirect(url_for('supply.tools.detail', tool_id=tool.id))

@bp.route('/supply/tools/<int:tool_id>/assign', methods=['POST'])
@login_required
def assign(tool_id):
    """Assign tool to user"""
    tool = Tool.query.get_or_404(tool_id)
    
    user_id = request.form.get('user_id')
    
    if user_id:
        try:
            user_id = int(user_id)
            user = User.query.get(user_id)
            if not user:
                flash('Invalid user selected', 'error')
                return redirect(url_for('supply.tools.detail', tool_id=tool.id))
        except ValueError:
            flash('Invalid user ID', 'error')
            return redirect(url_for('supply.tools.detail', tool_id=tool.id))
        
        tool.assign_to_user(user_id)
        flash(f'Tool assigned to {user.username}', 'success')
    else:
        tool.unassign()
        flash('Tool unassigned', 'success')
    
    try:
        db.session.commit()
        logger.info(f"User {current_user.username} assigned tool {tool.tool_name} to user {user_id}")
    except Exception as e:
        db.session.rollback()
        flash(f'Error assigning tool: {str(e)}', 'error')
        logger.error(f"Error assigning tool: {str(e)}")
    
    return redirect(url_for('supply.tools.detail', tool_id=tool.id))

@bp.route('/supply/tools/<int:tool_id>/mark-repair', methods=['POST'])
@login_required
def mark_repair(tool_id):
    """Mark tool as out for repair"""
    tool = Tool.query.get_or_404(tool_id)
    
    tool.mark_for_repair()
    
    try:
        db.session.commit()
        flash('Tool marked as out for repair', 'success')
        logger.info(f"User {current_user.username} marked tool {tool.tool_name} for repair")
    except Exception as e:
        db.session.rollback()
        flash(f'Error marking tool for repair: {str(e)}', 'error')
        logger.error(f"Error marking tool for repair: {str(e)}")
    
    return redirect(url_for('supply.tools.detail', tool_id=tool.id))

@bp.route('/supply/tools/<int:tool_id>/retire', methods=['POST'])
@login_required
def retire(tool_id):
    """Retire tool"""
    tool = Tool.query.get_or_404(tool_id)
    
    tool.retire()
    
    try:
        db.session.commit()
        flash('Tool retired successfully', 'success')
        logger.info(f"User {current_user.username} retired tool {tool.tool_name}")
    except Exception as e:
        db.session.rollback()
        flash(f'Error retiring tool: {str(e)}', 'error')
        logger.error(f"Error retiring tool: {str(e)}")
    
    return redirect(url_for('supply.tools.detail', tool_id=tool.id))

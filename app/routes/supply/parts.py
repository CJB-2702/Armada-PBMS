"""
Parts management routes
CRUD operations for Part model
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from app.logger import get_logger
from flask_login import login_required, current_user
from app.models.supply.part import Part
from app import db

bp = Blueprint('parts', __name__)
logger = get_logger("asset_management.routes.supply.parts")

@bp.route('/supply/parts')
@login_required
def list():
    """List all parts"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Basic filtering
    category = request.args.get('category')
    status = request.args.get('status')
    stock_status = request.args.get('stock_status')
    
    query = Part.query
    
    if category:
        query = query.filter(Part.category == category)
    
    if status:
        query = query.filter(Part.status == status)
    
    if stock_status:
        if stock_status == 'low':
            query = query.filter(Part.current_stock_level <= Part.minimum_stock_level)
        elif stock_status == 'out':
            query = query.filter(Part.current_stock_level <= 0)
        elif stock_status == 'in_stock':
            query = query.filter(Part.current_stock_level > Part.minimum_stock_level)
    
    # Order by part name
    query = query.order_by(Part.part_name)
    
    # Pagination
    parts = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Get unique categories for filter
    categories = db.session.query(Part.category).distinct().filter(Part.category.isnot(None)).all()
    categories = [cat[0] for cat in categories]
    
    return render_template('supply/parts/list.html', parts=parts, categories=categories)

@bp.route('/supply/parts/<int:part_id>')
@login_required
def detail(part_id):
    """View part details"""
    part = Part.query.get_or_404(part_id)
    
    return render_template('supply/parts/detail.html', part=part)

@bp.route('/supply/parts/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create new part"""
    if request.method == 'POST':
        # Validate form data
        part_number = request.form.get('part_number')
        part_name = request.form.get('part_name')
        description = request.form.get('description')
        category = request.form.get('category')
        manufacturer = request.form.get('manufacturer')
        supplier = request.form.get('supplier')
        unit_cost = request.form.get('unit_cost')
        current_stock_level = request.form.get('current_stock_level')
        minimum_stock_level = request.form.get('minimum_stock_level')
        maximum_stock_level = request.form.get('maximum_stock_level')
        unit_of_measure = request.form.get('unit_of_measure')
        location = request.form.get('location')
        status = request.form.get('status', 'Active')
        
        # Validate required fields
        if not part_number or not part_name:
            flash('Part number and part name are required', 'error')
            return render_template('supply/parts/create.html')
        
        # Check if part number already exists
        if Part.query.filter_by(part_number=part_number).first():
            flash('Part number already exists', 'error')
            return render_template('supply/parts/create.html')
        
        # Convert numeric fields
        try:
            unit_cost = float(unit_cost) if unit_cost else None
            current_stock_level = float(current_stock_level) if current_stock_level else 0.0
            minimum_stock_level = float(minimum_stock_level) if minimum_stock_level else 0.0
            maximum_stock_level = float(maximum_stock_level) if maximum_stock_level else None
        except ValueError:
            flash('Invalid numeric values for cost or stock levels', 'error')
            return render_template('supply/parts/create.html')
        
        # Create new part
        part = Part(
            part_number=part_number,
            part_name=part_name,
            description=description,
            category=category,
            manufacturer=manufacturer,
            supplier=supplier,
            unit_cost=unit_cost,
            current_stock_level=current_stock_level,
            minimum_stock_level=minimum_stock_level,
            maximum_stock_level=maximum_stock_level,
            unit_of_measure=unit_of_measure,
            location=location,
            status=status
        )
        
        try:
            db.session.add(part)
            db.session.commit()
            flash(f'Part "{part.part_name}" created successfully', 'success')
            logger.info(f"User {current_user.username} created part {part.part_number}")
            return redirect(url_for('supply.parts.detail', part_id=part.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating part: {str(e)}', 'error')
            logger.error(f"Error creating part: {str(e)}")
            return render_template('supply/parts/create.html')
    
    return render_template('supply/parts/create.html')

@bp.route('/supply/parts/<int:part_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(part_id):
    """Edit part"""
    part = Part.query.get_or_404(part_id)
    
    if request.method == 'POST':
        # Validate form data
        part_number = request.form.get('part_number')
        part_name = request.form.get('part_name')
        description = request.form.get('description')
        category = request.form.get('category')
        manufacturer = request.form.get('manufacturer')
        supplier = request.form.get('supplier')
        unit_cost = request.form.get('unit_cost')
        current_stock_level = request.form.get('current_stock_level')
        minimum_stock_level = request.form.get('minimum_stock_level')
        maximum_stock_level = request.form.get('maximum_stock_level')
        unit_of_measure = request.form.get('unit_of_measure')
        location = request.form.get('location')
        status = request.form.get('status')
        
        # Validate required fields
        if not part_number or not part_name:
            flash('Part number and part name are required', 'error')
            return render_template('supply/parts/edit.html', part=part)
        
        # Check if part number already exists (excluding current part)
        existing_part = Part.query.filter_by(part_number=part_number).first()
        if existing_part and existing_part.id != part.id:
            flash('Part number already exists', 'error')
            return render_template('supply/parts/edit.html', part=part)
        
        # Convert numeric fields
        try:
            unit_cost = float(unit_cost) if unit_cost else None
            current_stock_level = float(current_stock_level) if current_stock_level else 0.0
            minimum_stock_level = float(minimum_stock_level) if minimum_stock_level else 0.0
            maximum_stock_level = float(maximum_stock_level) if maximum_stock_level else None
        except ValueError:
            flash('Invalid numeric values for cost or stock levels', 'error')
            return render_template('supply/parts/edit.html', part=part)
        
        # Update part
        part.part_number = part_number
        part.part_name = part_name
        part.description = description
        part.category = category
        part.manufacturer = manufacturer
        part.supplier = supplier
        part.unit_cost = unit_cost
        part.current_stock_level = current_stock_level
        part.minimum_stock_level = minimum_stock_level
        part.maximum_stock_level = maximum_stock_level
        part.unit_of_measure = unit_of_measure
        part.location = location
        part.status = status
        
        try:
            db.session.commit()
            flash(f'Part "{part.part_name}" updated successfully', 'success')
            logger.info(f"User {current_user.username} updated part {part.part_number}")
            return redirect(url_for('supply.parts.detail', part_id=part.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating part: {str(e)}', 'error')
            logger.error(f"Error updating part: {str(e)}")
            return render_template('supply/parts/edit.html', part=part)
    
    return render_template('supply/parts/edit.html', part=part)

@bp.route('/supply/parts/<int:part_id>/delete', methods=['POST'])
@login_required
def delete(part_id):
    """Delete part"""
    part = Part.query.get_or_404(part_id)
    
    try:
        db.session.delete(part)
        db.session.commit()
        flash(f'Part "{part.part_name}" deleted successfully', 'success')
        logger.info(f"User {current_user.username} deleted part {part.part_number}")
        return redirect(url_for('supply.parts.list'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting part: {str(e)}', 'error')
        logger.error(f"Error deleting part: {str(e)}")
        return redirect(url_for('supply.parts.detail', part_id=part.id))

@bp.route('/supply/parts/<int:part_id>/adjust-stock', methods=['POST'])
@login_required
def adjust_stock(part_id):
    """Adjust part stock level"""
    part = Part.query.get_or_404(part_id)
    
    quantity = request.form.get('quantity')
    adjustment_type = request.form.get('adjustment_type', 'add')
    
    try:
        quantity = float(quantity)
        if quantity < 0:
            flash('Quantity must be positive', 'error')
            return redirect(url_for('supply.parts.detail', part_id=part.id))
    except ValueError:
        flash('Invalid quantity value', 'error')
        return redirect(url_for('supply.parts.detail', part_id=part.id))
    
    # Adjust stock
    part.adjust_stock(quantity, adjustment_type, current_user.id)
    
    try:
        db.session.commit()
        flash(f'Stock level adjusted successfully. New level: {part.current_stock_level}', 'success')
        logger.info(f"User {current_user.username} adjusted stock for part {part.part_number} by {quantity} ({adjustment_type})")
    except Exception as e:
        db.session.rollback()
        flash(f'Error adjusting stock: {str(e)}', 'error')
        logger.error(f"Error adjusting stock: {str(e)}")
    
    return redirect(url_for('supply.parts.detail', part_id=part.id))

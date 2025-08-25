"""
Part demands management routes
CRUD operations for PartDemand model
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from app.logger import get_logger
from flask_login import login_required, current_user
from app.models.supply.part_demand import PartDemand
from app.models.supply.part import Part
from app.models.core.user import User
from app import db
from datetime import datetime

bp = Blueprint('part_demands', __name__)
logger = get_logger("asset_management.routes.supply.part_demands")

@bp.route('/supply/part-demands')
@login_required
def list():
    """List all part demands"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Basic filtering
    status = request.args.get('status')
    part_id = request.args.get('part_id')
    requested_by = request.args.get('requested_by')
    
    query = PartDemand.query
    
    if status:
        query = query.filter(PartDemand.status == status)
    
    if part_id:
        query = query.filter(PartDemand.part_id == part_id)
    
    if requested_by:
        query = query.filter(PartDemand.requested_by_id == requested_by)
    
    # Order by creation date (newest first)
    query = query.order_by(PartDemand.created_at.desc())
    
    # Pagination
    part_demands = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Get parts for filter
    parts = Part.query.order_by(Part.part_name).all()
    
    # Get users for filter
    users = User.query.filter(User.is_active == True).order_by(User.username).all()
    
    return render_template('supply/part_demands/list.html', 
                         part_demands=part_demands, 
                         parts=parts, 
                         users=users)

@bp.route('/supply/part-demands/<int:demand_id>')
@login_required
def detail(demand_id):
    """View part demand details"""
    part_demand = PartDemand.query.get_or_404(demand_id)
    
    return render_template('supply/part_demands/detail.html', part_demand=part_demand)

@bp.route('/supply/part-demands/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create new part demand"""
    if request.method == 'POST':
        # Validate form data
        part_id = request.form.get('part_id')
        quantity_required = request.form.get('quantity_required')
        notes = request.form.get('notes')
        requested_by_id = request.form.get('requested_by_id')
        
        # Validate required fields
        if not part_id or not quantity_required:
            flash('Part and quantity are required', 'error')
            return render_template('supply/part_demands/create.html')
        
        # Validate part exists
        part = Part.query.get(part_id)
        if not part:
            flash('Selected part does not exist', 'error')
            return render_template('supply/part_demands/create.html')
        
        # Convert numeric fields
        try:
            quantity_required = float(quantity_required)
            if quantity_required <= 0:
                flash('Quantity must be greater than 0', 'error')
                return render_template('supply/part_demands/create.html')
        except ValueError:
            flash('Invalid quantity value', 'error')
            return render_template('supply/part_demands/create.html')
        
        # Convert requested_by_id
        if requested_by_id:
            try:
                requested_by_id = int(requested_by_id)
                user = User.query.get(requested_by_id)
                if not user:
                    flash('Selected user does not exist', 'error')
                    return render_template('supply/part_demands/create.html')
            except ValueError:
                requested_by_id = None
        
        # Create new part demand
        part_demand = PartDemand(
            part_id=part_id,
            quantity_required=quantity_required,
            notes=notes,
            requested_by_id=requested_by_id,
            requested_date=datetime.utcnow(),
            status='Requested'
        )
        
        try:
            db.session.add(part_demand)
            db.session.commit()
            flash(f'Part demand created successfully', 'success')
            logger.info(f"User {current_user.username} created part demand for {part.part_name}")
            return redirect(url_for('supply.part_demands.detail', demand_id=part_demand.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating part demand: {str(e)}', 'error')
            logger.error(f"Error creating part demand: {str(e)}")
            return render_template('supply/part_demands/create.html')
    
    # Get parts for dropdown
    parts = Part.query.order_by(Part.part_name).all()
    
    # Get users for dropdown
    users = User.query.filter(User.is_active == True).order_by(User.username).all()
    
    return render_template('supply/part_demands/create.html', parts=parts, users=users)

@bp.route('/supply/part-demands/<int:demand_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(demand_id):
    """Edit part demand"""
    part_demand = PartDemand.query.get_or_404(demand_id)
    
    if request.method == 'POST':
        # Validate form data
        part_id = request.form.get('part_id')
        quantity_required = request.form.get('quantity_required')
        notes = request.form.get('notes')
        requested_by_id = request.form.get('requested_by_id')
        status = request.form.get('status')
        
        # Validate required fields
        if not part_id or not quantity_required:
            flash('Part and quantity are required', 'error')
            return render_template('supply/part_demands/edit.html', part_demand=part_demand)
        
        # Validate part exists
        part = Part.query.get(part_id)
        if not part:
            flash('Selected part does not exist', 'error')
            return render_template('supply/part_demands/edit.html', part_demand=part_demand)
        
        # Convert numeric fields
        try:
            quantity_required = float(quantity_required)
            if quantity_required <= 0:
                flash('Quantity must be greater than 0', 'error')
                return render_template('supply/part_demands/edit.html', part_demand=part_demand)
        except ValueError:
            flash('Invalid quantity value', 'error')
            return render_template('supply/part_demands/edit.html', part_demand=part_demand)
        
        # Convert requested_by_id
        if requested_by_id:
            try:
                requested_by_id = int(requested_by_id)
                user = User.query.get(requested_by_id)
                if not user:
                    flash('Selected user does not exist', 'error')
                    return render_template('supply/part_demands/edit.html', part_demand=part_demand)
            except ValueError:
                requested_by_id = None
        
        # Update part demand
        part_demand.part_id = part_id
        part_demand.quantity_required = quantity_required
        part_demand.notes = notes
        part_demand.requested_by_id = requested_by_id
        part_demand.status = status
        
        # Calculate expected cost
        part_demand.calculate_expected_cost()
        
        try:
            db.session.commit()
            flash(f'Part demand updated successfully', 'success')
            logger.info(f"User {current_user.username} updated part demand {part_demand.id}")
            return redirect(url_for('supply.part_demands.detail', demand_id=part_demand.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating part demand: {str(e)}', 'error')
            logger.error(f"Error updating part demand: {str(e)}")
            return render_template('supply/part_demands/edit.html', part_demand=part_demand)
    
    # Get parts for dropdown
    parts = Part.query.order_by(Part.part_name).all()
    
    # Get users for dropdown
    users = User.query.filter(User.is_active == True).order_by(User.username).all()
    
    return render_template('supply/part_demands/edit.html', part_demand=part_demand, parts=parts, users=users)

@bp.route('/supply/part-demands/<int:demand_id>/delete', methods=['POST'])
@login_required
def delete(demand_id):
    """Delete part demand"""
    part_demand = PartDemand.query.get_or_404(demand_id)
    
    try:
        db.session.delete(part_demand)
        db.session.commit()
        flash(f'Part demand deleted successfully', 'success')
        logger.info(f"User {current_user.username} deleted part demand {demand_id}")
        return redirect(url_for('supply.part_demands.list'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting part demand: {str(e)}', 'error')
        logger.error(f"Error deleting part demand: {str(e)}")
        return redirect(url_for('supply.part_demands.detail', demand_id=part_demand.id))

@bp.route('/supply/part-demands/<int:demand_id>/approve', methods=['POST'])
@login_required
def approve(demand_id):
    """Approve part demand"""
    part_demand = PartDemand.query.get_or_404(demand_id)
    
    if part_demand.status != 'Requested':
        flash('Only requested demands can be approved', 'error')
        return redirect(url_for('supply.part_demands.detail', demand_id=part_demand.id))
    
    part_demand.status = 'Approved'
    part_demand.approved_by_id = current_user.id
    part_demand.approved_date = datetime.utcnow()
    
    try:
        db.session.commit()
        flash('Part demand approved successfully', 'success')
        logger.info(f"User {current_user.username} approved part demand {demand_id}")
    except Exception as e:
        db.session.rollback()
        flash(f'Error approving part demand: {str(e)}', 'error')
        logger.error(f"Error approving part demand: {str(e)}")
    
    return redirect(url_for('supply.part_demands.detail', demand_id=part_demand.id))

@bp.route('/supply/part-demands/<int:demand_id>/reject', methods=['POST'])
@login_required
def reject(demand_id):
    """Reject part demand"""
    part_demand = PartDemand.query.get_or_404(demand_id)
    
    if part_demand.status not in ['Requested', 'Approved']:
        flash('Only requested or approved demands can be rejected', 'error')
        return redirect(url_for('supply.part_demands.detail', demand_id=part_demand.id))
    
    part_demand.status = 'Rejected'
    
    try:
        db.session.commit()
        flash('Part demand rejected successfully', 'success')
        logger.info(f"User {current_user.username} rejected part demand {demand_id}")
    except Exception as e:
        db.session.rollback()
        flash(f'Error rejecting part demand: {str(e)}', 'error')
        logger.error(f"Error rejecting part demand: {str(e)}")
    
    return redirect(url_for('supply.part_demands.detail', demand_id=part_demand.id))

@bp.route('/supply/part-demands/<int:demand_id>/fulfill', methods=['POST'])
@login_required
def fulfill(demand_id):
    """Fulfill part demand"""
    part_demand = PartDemand.query.get_or_404(demand_id)
    
    if part_demand.status != 'Approved':
        flash('Only approved demands can be fulfilled', 'error')
        return redirect(url_for('supply.part_demands.detail', demand_id=part_demand.id))
    
    # Check if we have enough stock
    if part_demand.part.current_stock_level < part_demand.quantity_required:
        flash(f'Insufficient stock. Available: {part_demand.part.current_stock_level}, Required: {part_demand.quantity_required}', 'error')
        return redirect(url_for('supply.part_demands.detail', demand_id=part_demand.id))
    
    # Reduce stock
    part_demand.part.adjust_stock(part_demand.quantity_required, 'subtract', current_user.id)
    part_demand.status = 'Fulfilled'
    
    try:
        db.session.commit()
        flash('Part demand fulfilled successfully', 'success')
        logger.info(f"User {current_user.username} fulfilled part demand {demand_id}")
    except Exception as e:
        db.session.rollback()
        flash(f'Error fulfilling part demand: {str(e)}', 'error')
        logger.error(f"Error fulfilling part demand: {str(e)}")
    
    return redirect(url_for('supply.part_demands.detail', demand_id=part_demand.id))

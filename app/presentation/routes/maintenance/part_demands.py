"""
Part Demand management routes
CRUD operations for PartDemand model
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.data.maintenance.base.part_demand import PartDemand
from app.buisness.maintenance.factories.part_demand_factory import PartDemandFactory
from app.services.maintenance.part_demand_service import PartDemandService
from app import db
from app.logger import get_logger

logger = get_logger("asset_management.routes.maintenance.part_demands")
bp = Blueprint('part_demands', __name__)

@bp.route('/part-demands')
@login_required
def list():
    """List all part demands with comprehensive filtering via request parameters"""
    logger.debug(f"User {current_user.username} accessing part demands list")
    
    page = request.args.get('page', 1, type=int)
    
    # Comprehensive filtering via request parameters
    action_id = request.args.get('action_id', type=int)
    action_set_id = request.args.get('action_set_id', type=int)
    part_id = request.args.get('part_id', type=int)
    status = request.args.get('status')
    
    logger.debug(f"Part demands list filters - Action: {action_id}, ActionSet: {action_set_id}, Part: {part_id}, Status: {status}")
    
    # Get list data from service
    part_demands, form_options = PartDemandService.get_list_data(
        page=page,
        action_id=action_id,
        action_set_id=action_set_id,
        part_id=part_id,
        status=status
    )
    
    logger.info(f"Part demands list returned {part_demands.total} items (page {page})")
    
    return render_template('maintenance/part_demands/list.html', 
                         part_demands=part_demands,
                         actions=form_options['actions'],
                         action_sets=form_options['action_sets'],
                         parts=form_options['parts'],
                         statuses=form_options['statuses'],
                         filters={'action_id': action_id,
                                'action_set_id': action_set_id,
                                'part_id': part_id,
                                'status': status
                         })

@bp.route('/part-demands/<int:part_demand_id>')
@login_required
def detail(part_demand_id):
    """View individual part demand details"""
    logger.debug(f"User {current_user.username} accessing part demand detail for ID: {part_demand_id}")
    
    part_demand = PartDemand.query.get_or_404(part_demand_id)
    
    # Get related data through relationships
    action = part_demand.action
    part = part_demand.part
    template_part_demand = part_demand.template_part_demand
    
    logger.info(f"Part demand detail accessed - Part: {part.name if part else 'N/A'} (ID: {part_demand_id})")
    
    return render_template('maintenance/part_demands/detail.html', 
                         part_demand=part_demand,
                         action=action,
                         part=part,
                         template_part_demand=template_part_demand)

@bp.route('/part-demands/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create new part demand"""
    if request.method == 'POST':
        # Validate form data
        action_id = request.form.get('action_id', type=int)
        part_id = request.form.get('part_id', type=int)
        template_part_demand_id = request.form.get('template_part_demand_id', type=int)
        quantity_required = request.form.get('quantity_required', type=float)
        quantity_issued = request.form.get('quantity_issued', type=float, default=0)
        status = request.form.get('status', 'Pending')
        notes = request.form.get('notes')
        
        # Create new part demand using factory
        part_demand = PartDemandFactory.create_from_dict({
            'action_id': action_id,
            'part_id': part_id,
            'template_part_demand_id': template_part_demand_id,
            'quantity_required': quantity_required,
            'quantity_issued': quantity_issued,
            'status': status,
            'notes': notes,
            'created_by_id': current_user.id,
            'updated_by_id': current_user.id
        })
        
        flash('Part demand created successfully', 'success')
        return redirect(url_for('part_demands.detail', part_demand_id=part_demand.id))
    
    # Get form options from service
    form_options = PartDemandService.get_form_options()
    
    return render_template('maintenance/part_demands/create.html',
                         actions=form_options['actions'],
                         parts=form_options['parts'],
                         template_part_demands=form_options['template_part_demands'])

@bp.route('/part-demands/<int:part_demand_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(part_demand_id):
    """Edit part demand"""
    part_demand = PartDemand.query.get_or_404(part_demand_id)
    
    if request.method == 'POST':
        # Validate form data
        part_id = request.form.get('part_id', type=int)
        quantity_required = request.form.get('quantity_required', type=float)
        quantity_issued = request.form.get('quantity_issued', type=float)
        status = request.form.get('status')
        notes = request.form.get('notes')
        
        # Update part demand
        part_demand.part_id = part_id
        part_demand.quantity_required = quantity_required
        part_demand.quantity_issued = quantity_issued
        part_demand.status = status
        part_demand.notes = notes
        part_demand.updated_by_id = current_user.id
        
        db.session.commit()
        
        flash('Part demand updated successfully', 'success')
        return redirect(url_for('part_demands.detail', part_demand_id=part_demand.id))
    
    # Get form options from service
    form_options = PartDemandService.get_form_options()
    
    return render_template('maintenance/part_demands/edit.html',
                         part_demand=part_demand,
                         parts=form_options['parts'])

@bp.route('/part-demands/<int:part_demand_id>/delete', methods=['POST'])
@login_required
def delete(part_demand_id):
    """Delete part demand"""
    part_demand = PartDemand.query.get_or_404(part_demand_id)
    
    db.session.delete(part_demand)
    db.session.commit()
    
    flash('Part demand deleted successfully', 'success')
    return redirect(url_for('part_demands.list'))

@bp.route('/part-demands/<int:part_demand_id>/issue', methods=['POST'])
@login_required
def issue(part_demand_id):
    """Issue parts for a part demand"""
    part_demand = PartDemand.query.get_or_404(part_demand_id)
    
    quantity_to_issue = request.form.get('quantity_to_issue', type=float)
    
    if quantity_to_issue:
        part_demand.quantity_issued = (part_demand.quantity_issued or 0) + quantity_to_issue
        
        # Update status if fully issued
        if part_demand.quantity_issued >= part_demand.quantity_required:
            part_demand.status = 'Issued'
        else:
            part_demand.status = 'Partially Issued'
        
        part_demand.updated_by_id = current_user.id
        db.session.commit()
        
        flash(f'Issued {quantity_to_issue} units successfully', 'success')
    else:
        flash('Invalid quantity', 'error')
    
    return redirect(url_for('part_demands.detail', part_demand_id=part_demand_id))


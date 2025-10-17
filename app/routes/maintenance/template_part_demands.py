"""
Template Part Demand management routes
CRUD operations for TemplatePartDemand model
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload
from app.models.maintenance.templates.template_part_demand import TemplatePartDemand
from app.models.maintenance.templates.template_action_item import TemplateActionItem
from app.models.supply_items.part import Part
from app import db
from app.logger import get_logger

logger = get_logger("asset_management.routes.maintenance.template_part_demands")
bp = Blueprint('template_part_demands', __name__)

@bp.route('/template-part-demands')
@login_required
def list():
    """List all template part demands with basic filtering"""
    logger.debug(f"User {current_user.username} accessing template part demands list")
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Basic filtering
    template_action_item_id = request.args.get('template_action_item_id', type=int)
    part_id = request.args.get('part_id', type=int)
    is_optional = request.args.get('is_optional')
    
    logger.debug(f"Template part demands list filters - Action Item: {template_action_item_id}, Part: {part_id}")
    
    query = TemplatePartDemand.query.options(
        joinedload(TemplatePartDemand.template_action_item),
        joinedload(TemplatePartDemand.part)
    )
    
    if template_action_item_id:
        query = query.filter(TemplatePartDemand.template_action_item_id == template_action_item_id)
    
    if part_id:
        query = query.filter(TemplatePartDemand.part_id == part_id)
    
    if is_optional is not None:
        query = query.filter(TemplatePartDemand.is_optional == (is_optional.lower() == 'true'))
    
    # Order by creation date (newest first)
    query = query.order_by(TemplatePartDemand.created_at.desc())
    
    # Pagination
    template_part_demands = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Get filter options
    template_action_items = TemplateActionItem.query.all()
    parts = Part.query.all()
    
    logger.info(f"Template part demands list returned {template_part_demands.total} items (page {page})")
    
    return render_template('maintenance/template_part_demands/list.html', 
                         template_part_demands=template_part_demands,
                         template_action_items=template_action_items,
                         parts=parts,
                         filters={'template_action_item_id': template_action_item_id,
                                'part_id': part_id,
                                'is_optional': is_optional
                         })

@bp.route('/template-part-demands/<int:template_part_demand_id>')
@login_required
def detail(template_part_demand_id):
    """View individual template part demand details"""
    logger.debug(f"User {current_user.username} accessing template part demand detail for ID: {template_part_demand_id}")
    
    template_part_demand = TemplatePartDemand.query.get_or_404(template_part_demand_id)
    
    # Get related data through relationships
    template_action_item = template_part_demand.template_action_item
    part = template_part_demand.part
    
    logger.info(f"Template part demand detail accessed - Part: {part.part_name if part else 'N/A'} (ID: {template_part_demand_id})")
    
    return render_template('maintenance/template_part_demands/detail.html', 
                         template_part_demand=template_part_demand,
                         template_action_item=template_action_item,
                         part=part)

@bp.route('/template-part-demands/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create new template part demand"""
    if request.method == 'POST':
        # Validate form data
        template_action_item_id = request.form.get('template_action_item_id', type=int)
        part_id = request.form.get('part_id', type=int)
        quantity_required = request.form.get('quantity_required', type=float)
        expected_cost = request.form.get('expected_cost', type=float)
        is_optional = request.form.get('is_optional') == 'true'
        sequence_order = request.form.get('sequence_order', type=int, default=1)
        notes = request.form.get('notes')
        
        # Create new template part demand
        template_part_demand = TemplatePartDemand(
            template_action_item_id=template_action_item_id,
            part_id=part_id,
            quantity_required=quantity_required,
            expected_cost=expected_cost,
            is_optional=is_optional,
            sequence_order=sequence_order,
            notes=notes,
            created_by_id=current_user.id,
            updated_by_id=current_user.id
        )
        
        db.session.add(template_part_demand)
        db.session.commit()
        
        flash('Template part demand created successfully', 'success')
        return redirect(url_for('template_part_demands.detail', template_part_demand_id=template_part_demand.id))
    
    # Get form options
    template_action_items = TemplateActionItem.query.all()
    parts = Part.query.all()
    
    return render_template('maintenance/template_part_demands/create.html',
                         template_action_items=template_action_items,
                         parts=parts)

@bp.route('/template-part-demands/<int:template_part_demand_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(template_part_demand_id):
    """Edit template part demand"""
    template_part_demand = TemplatePartDemand.query.get_or_404(template_part_demand_id)
    
    if request.method == 'POST':
        # Validate form data
        part_id = request.form.get('part_id', type=int)
        quantity_required = request.form.get('quantity_required', type=float)
        expected_cost = request.form.get('expected_cost', type=float)
        is_optional = request.form.get('is_optional') == 'true'
        sequence_order = request.form.get('sequence_order', type=int)
        notes = request.form.get('notes')
        
        # Update template part demand
        template_part_demand.part_id = part_id
        template_part_demand.quantity_required = quantity_required
        template_part_demand.expected_cost = expected_cost
        template_part_demand.is_optional = is_optional
        template_part_demand.sequence_order = sequence_order
        template_part_demand.notes = notes
        template_part_demand.updated_by_id = current_user.id
        
        db.session.commit()
        
        flash('Template part demand updated successfully', 'success')
        return redirect(url_for('template_part_demands.detail', template_part_demand_id=template_part_demand.id))
    
    # Get form options
    parts = Part.query.all()
    
    return render_template('maintenance/template_part_demands/edit.html',
                         template_part_demand=template_part_demand,
                         parts=parts)

@bp.route('/template-part-demands/<int:template_part_demand_id>/delete', methods=['POST'])
@login_required
def delete(template_part_demand_id):
    """Delete template part demand"""
    template_part_demand = TemplatePartDemand.query.get_or_404(template_part_demand_id)
    
    db.session.delete(template_part_demand)
    db.session.commit()
    
    flash('Template part demand deleted successfully', 'success')
    return redirect(url_for('template_part_demands.list'))


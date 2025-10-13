"""
Maintenance Plan management routes
CRUD operations for MaintenancePlan model
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.models.maintenance.base.maintenance_plan import MaintenancePlan
from app.models.core.asset_type import AssetType
from app.models.core.make_model import MakeModel
from app.models.maintenance.templates.template_action_set import TemplateActionSet
from app import db
from app.logger import get_logger

logger = get_logger("asset_management.routes.maintenance.maintenance_plans")
bp = Blueprint('maintenance_plans', __name__)

@bp.route('/maintenance-plans')
@login_required
def list():
    """List all maintenance plans with basic filtering"""
    logger.debug(f"User {current_user.username} accessing maintenance plans list")
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Basic filtering
    asset_type_id = request.args.get('asset_type_id', type=int)
    model_id = request.args.get('model_id', type=int)
    status = request.args.get('status')
    frequency_type = request.args.get('frequency_type')
    name = request.args.get('name')
    
    logger.debug(f"Maintenance plans list filters - Type: {asset_type_id}, Model: {model_id}, Status: {status}")
    
    query = MaintenancePlan.query
    
    if asset_type_id:
        query = query.filter(MaintenancePlan.asset_type_id == asset_type_id)
    
    if model_id:
        query = query.filter(MaintenancePlan.model_id == model_id)
    
    if status:
        query = query.filter(MaintenancePlan.status == status)
    
    if frequency_type:
        query = query.filter(MaintenancePlan.frequency_type == frequency_type)
    
    if name:
        query = query.filter(MaintenancePlan.name.ilike(f'%{name}%'))
    
    # Order by creation date (newest first)
    query = query.order_by(MaintenancePlan.created_at.desc())
    
    # Pagination
    maintenance_plans = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Get filter options
    asset_types = AssetType.query.all()
    make_models = MakeModel.query.all()
    
    logger.info(f"Maintenance plans list returned {maintenance_plans.total} plans (page {page})")
    
    return render_template('maintenance/maintenance_plans/list.html', 
                         maintenance_plans=maintenance_plans,
                         asset_types=asset_types,
                         make_models=make_models,
                         current_filters={
                             'asset_type_id': asset_type_id, 
                             'model_id': model_id,
                             'status': status,
                             'frequency_type': frequency_type,
                             'name': name
                         })

@bp.route('/maintenance-plans/<int:plan_id>')
@login_required
def detail(plan_id):
    """View individual maintenance plan details"""
    logger.debug(f"User {current_user.username} accessing maintenance plan detail for plan ID: {plan_id}")
    
    plan = MaintenancePlan.query.get_or_404(plan_id)
    
    # Get related data through relationships
    asset_type = plan.asset_type
    model = plan.model
    template_action_set = plan.template_action_set
    
    # Get maintenance action sets for this plan (most recent first)
    from app.models.maintenance.base.maintenance_action_set import MaintenanceActionSet
    maintenance_action_sets = MaintenanceActionSet.query.filter_by(
        maintenance_plan_id=plan.id
    ).order_by(MaintenanceActionSet.created_at.desc()).limit(10).all()
    
    logger.info(f"Maintenance plan detail accessed - Plan: {plan.name} (ID: {plan_id})")
    
    return render_template('maintenance/maintenance_plans/detail.html', 
                         plan=plan,
                         asset_type=asset_type,
                         model=model,
                         template_action_set=template_action_set,
                         maintenance_action_sets=maintenance_action_sets)

@bp.route('/maintenance-plans/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create new maintenance plan"""
    if request.method == 'POST':
        # Validate form data
        name = request.form.get('name')
        description = request.form.get('description')
        asset_type_id = request.form.get('asset_type_id', type=int)
        model_id = request.form.get('model_id', type=int)
        template_action_set_id = request.form.get('template_action_set_id', type=int)
        frequency_type = request.form.get('frequency_type')
        status = request.form.get('status', 'Active')
        
        # Frequency-specific fields
        delta_hours = request.form.get('delta_hours', type=float)
        delta_m1 = request.form.get('delta_m1', type=float)
        delta_m2 = request.form.get('delta_m2', type=float)
        delta_m3 = request.form.get('delta_m3', type=float)
        delta_m4 = request.form.get('delta_m4', type=float)
        
        # Create new maintenance plan
        plan = MaintenancePlan(
            name=name,
            description=description,
            asset_type_id=asset_type_id,
            model_id=model_id,
            template_action_set_id=template_action_set_id,
            frequency_type=frequency_type,
            status=status,
            delta_hours=delta_hours,
            delta_m1=delta_m1,
            delta_m2=delta_m2,
            delta_m3=delta_m3,
            delta_m4=delta_m4,
            created_by_id=current_user.id,
            updated_by_id=current_user.id
        )
        
        db.session.add(plan)
        db.session.commit()
        
        flash('Maintenance plan created successfully', 'success')
        return redirect(url_for('maintenance_plans.detail', plan_id=plan.id))
    
    # Get form options
    asset_types = AssetType.query.all()
    make_models = MakeModel.query.all()
    template_action_sets = TemplateActionSet.query.all()
    
    return render_template('maintenance/maintenance_plans/create.html', 
                         asset_types=asset_types,
                         make_models=make_models,
                         template_action_sets=template_action_sets)

@bp.route('/maintenance-plans/<int:plan_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(plan_id):
    """Edit maintenance plan"""
    plan = MaintenancePlan.query.get_or_404(plan_id)
    
    if request.method == 'POST':
        # Validate form data
        name = request.form.get('name')
        description = request.form.get('description')
        asset_type_id = request.form.get('asset_type_id', type=int)
        model_id = request.form.get('model_id', type=int)
        template_action_set_id = request.form.get('template_action_set_id', type=int)
        frequency_type = request.form.get('frequency_type')
        status = request.form.get('status')
        
        # Frequency-specific fields
        delta_hours = request.form.get('delta_hours', type=float)
        delta_m1 = request.form.get('delta_m1', type=float)
        delta_m2 = request.form.get('delta_m2', type=float)
        delta_m3 = request.form.get('delta_m3', type=float)
        delta_m4 = request.form.get('delta_m4', type=float)
        
        # Update maintenance plan
        plan.name = name
        plan.description = description
        plan.asset_type_id = asset_type_id
        plan.model_id = model_id
        plan.template_action_set_id = template_action_set_id
        plan.frequency_type = frequency_type
        plan.status = status
        plan.delta_hours = delta_hours
        plan.delta_m1 = delta_m1
        plan.delta_m2 = delta_m2
        plan.delta_m3 = delta_m3
        plan.delta_m4 = delta_m4
        plan.updated_by_id = current_user.id
        
        db.session.commit()
        
        flash('Maintenance plan updated successfully', 'success')
        return redirect(url_for('maintenance_plans.detail', plan_id=plan.id))
    
    # Get form options
    asset_types = AssetType.query.all()
    make_models = MakeModel.query.all()
    template_action_sets = TemplateActionSet.query.all()
    
    return render_template('maintenance/maintenance_plans/edit.html', 
                         plan=plan,
                         asset_types=asset_types,
                         make_models=make_models,
                         template_action_sets=template_action_sets)

@bp.route('/maintenance-plans/<int:plan_id>/delete', methods=['POST'])
@login_required
def delete(plan_id):
    """Delete maintenance plan"""
    plan = MaintenancePlan.query.get_or_404(plan_id)
    
    # Check if plan has maintenance action sets
    if plan.maintenance_action_sets.count() > 0:
        flash('Cannot delete maintenance plan with action sets', 'error')
        return redirect(url_for('maintenance_plans.detail', plan_id=plan.id))
    
    db.session.delete(plan)
    db.session.commit()
    
    flash('Maintenance plan deleted successfully', 'success')
    return redirect(url_for('maintenance_plans.list'))


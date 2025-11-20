"""
Maintenance Plan management routes
CRUD operations for MaintenancePlan model
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.data.maintenance.base.maintenance_plan import MaintenancePlan
from app.buisness.maintenance.maintenance_plan_context import MaintenancePlanContext
from app.services.maintenance.maintenance_plan_service import MaintenancePlanService
from app import db
from app.logger import get_logger

logger = get_logger("asset_management.routes.maintenance.maintenance_plans")
bp = Blueprint('maintenance_plans', __name__)

# ROUTE_TYPE: SIMPLE_CRUD (GET)
# EXCEPTION: Direct ORM usage allowed for simple GET operations on MaintenancePlan
# This route performs basic list operations with minimal filtering and business logic.
# Rationale: Simple pagination and filtering on single entity type doesn't require domain abstraction.
# NOTE: CREATE/DELETE operations should use domain managers - see create() and delete() routes
@bp.route('/maintenance-plans')
@login_required
def list():
    """List all maintenance plans with basic filtering"""
    logger.debug(f"User {current_user.username} accessing maintenance plans list")
    
    page = request.args.get('page', 1, type=int)
    
    # Basic filtering
    asset_type_id = request.args.get('asset_type_id', type=int)
    model_id = request.args.get('model_id', type=int)
    status = request.args.get('status')
    frequency_type = request.args.get('frequency_type')
    name = request.args.get('name')
    
    logger.debug(f"Maintenance plans list filters - Type: {asset_type_id}, Model: {model_id}, Status: {status}")
    
    # Get list data from service
    maintenance_plans, form_options = MaintenancePlanService.get_list_data(
        page=page,
        asset_type_id=asset_type_id,
        model_id=model_id,
        status=status,
        frequency_type=frequency_type,
        name=name
    )
    
    logger.info(f"Maintenance plans list returned {maintenance_plans.total} plans (page {page})")
    
    return render_template('maintenance/maintenance_plans/list.html', 
                         maintenance_plans=maintenance_plans,
                         asset_types=form_options['asset_types'],
                         make_models=form_options['make_models'],
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
    
    # Use MaintenancePlanContext for data aggregation
    context = MaintenancePlanContext(plan_id)
    
    logger.info(f"Maintenance plan detail accessed - Plan: {context.plan.name} (ID: {plan_id})")
    
    return render_template('maintenance/maintenance_plans/detail.html', 
                         plan=context.plan,
                         asset_type=context.asset_type,
                         model=context.model,
                         template_action_set=context.template_action_set,
                         maintenance_action_sets=MaintenancePlanService.get_recent_action_sets(context.plan_id, limit=10))

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
    
    # Get form options from service
    form_options = MaintenancePlanService.get_form_options()
    
    return render_template('maintenance/maintenance_plans/create.html', 
                         asset_types=form_options['asset_types'],
                         make_models=form_options['make_models'],
                         template_action_sets=form_options['template_action_sets'])

# ROUTE_TYPE: SIMPLE_CRUD (EDIT)
# EXCEPTION: Direct ORM usage allowed for simple EDIT operations on MaintenancePlan
# This route performs basic update operations with minimal business logic.
# Rationale: Simple maintenance plan update doesn't require domain abstraction.
# NOTE: CREATE/DELETE operations should use domain managers - see create() and delete() routes
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
    
    # Get form options from service
    form_options = MaintenancePlanService.get_form_options()
    
    return render_template('maintenance/maintenance_plans/edit.html', 
                         plan=plan,
                         asset_types=form_options['asset_types'],
                         make_models=form_options['make_models'],
                         template_action_sets=form_options['template_action_sets'])

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


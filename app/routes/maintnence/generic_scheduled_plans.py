#!/usr/bin/env python3
"""
Generic Scheduled Plans Routes
Handles CRUD operations for generic scheduled maintenance task plans
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.maintnence import GenericScheduledTaskPlan
from app.models.core import AssetType, MakeModel
from app.models.maintnence.templates.template_action_set import TemplateActionSet
from app.logger import get_logger

logger = get_logger(__name__)

# Create blueprint
generic_scheduled_plans_bp = Blueprint('generic_scheduled_plans', __name__)

# ==============================================================================
# GENERIC SCHEDULED TASK PLANS
# ==============================================================================

@generic_scheduled_plans_bp.route('/generic-scheduled-task-plans')
@login_required
def generic_scheduled_task_plans_list():
    """List all generic scheduled task plans"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        plans = GenericScheduledTaskPlan.query.order_by(
            GenericScheduledTaskPlan.name
        ).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return render_template(
            'maintenance/generic_scheduled_task_plans/list.html',
            plans=plans
        )
    except Exception as e:
        logger.error(f"Error loading generic scheduled task plans: {e}")
        flash('Error loading scheduled task plans', 'error')
        return redirect(url_for('maintenance.index'))

@generic_scheduled_plans_bp.route('/generic-scheduled-task-plans/create', methods=['GET', 'POST'])
@login_required
def generic_scheduled_task_plans_create():
    """Create a new generic scheduled task plan"""
    try:
        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description')
            asset_type_id = request.form.get('asset_type_id')
            make_model_id = request.form.get('make_model_id')
            template_action_set_id = request.form.get('template_action_set_id')
            interval_meter1 = request.form.get('interval_meter1', type=int)
            interval_meter2 = request.form.get('interval_meter2', type=int)
            interval_meter3 = request.form.get('interval_meter3', type=int)
            interval_meter4 = request.form.get('interval_meter4', type=int)
            interval_days = request.form.get('interval_days', type=int)
            is_active = request.form.get('is_active') == 'on'
            
            if not all([name, template_action_set_id]):
                flash('Name and template action set are required', 'error')
                return render_template('maintenance/generic_scheduled_task_plans/create.html',
                                     asset_types=AssetType.query.all(),
                                     make_models=MakeModel.query.all(),
                                     action_sets=TemplateActionSet.query.all())
            
            plan = GenericScheduledTaskPlan(
                name=name,
                description=description,
                asset_type_id=asset_type_id if asset_type_id else None,
                make_model_id=make_model_id if make_model_id else None,
                template_action_set_id=template_action_set_id,
                interval_meter1=interval_meter1,
                interval_meter2=interval_meter2,
                interval_meter3=interval_meter3,
                interval_meter4=interval_meter4,
                interval_days=interval_days,
                is_active=is_active,
                created_by_id=current_user.id
            )
            
            db.session.add(plan)
            db.session.commit()
            
            flash(f'Generic scheduled task plan "{name}" created successfully', 'success')
            return redirect(url_for('maintenance.generic_scheduled_task_plans_detail', id=plan.id))
        
        asset_types = AssetType.query.order_by(AssetType.name).all()
        make_models = MakeModel.query.order_by(MakeModel.make, MakeModel.model).all()
        action_sets = TemplateActionSet.query.order_by(TemplateActionSet.name).all()
        
        return render_template('maintenance/generic_scheduled_task_plans/create.html',
                             asset_types=asset_types, make_models=make_models, action_sets=action_sets)
        
    except Exception as e:
        logger.error(f"Error creating generic scheduled task plan: {e}")
        flash('Error creating scheduled task plan', 'error')
        return redirect(url_for('maintenance.generic_scheduled_task_plans_list'))

@generic_scheduled_plans_bp.route('/generic-scheduled-task-plans/<int:id>')
@login_required
def generic_scheduled_task_plans_detail(id):
    """View generic scheduled task plan details"""
    try:
        plan = GenericScheduledTaskPlan.query.get_or_404(id)
        return render_template('maintenance/generic_scheduled_task_plans/detail.html', plan=plan)
    except Exception as e:
        logger.error(f"Error loading generic scheduled task plan {id}: {e}")
        flash('Error loading scheduled task plan', 'error')
        return redirect(url_for('maintenance.generic_scheduled_task_plans_list'))

@generic_scheduled_plans_bp.route('/generic-scheduled-task-plans/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def generic_scheduled_task_plans_edit(id):
    """Edit generic scheduled task plan"""
    try:
        plan = GenericScheduledTaskPlan.query.get_or_404(id)
        
        if request.method == 'POST':
            plan.name = request.form.get('name')
            plan.description = request.form.get('description')
            plan.asset_type_id = request.form.get('asset_type_id') if request.form.get('asset_type_id') else None
            plan.make_model_id = request.form.get('make_model_id') if request.form.get('make_model_id') else None
            plan.template_action_set_id = request.form.get('template_action_set_id')
            plan.interval_meter1 = request.form.get('interval_meter1', type=int)
            plan.interval_meter2 = request.form.get('interval_meter2', type=int)
            plan.interval_meter3 = request.form.get('interval_meter3', type=int)
            plan.interval_meter4 = request.form.get('interval_meter4', type=int)
            plan.interval_days = request.form.get('interval_days', type=int)
            plan.is_active = request.form.get('is_active') == 'on'
            plan.updated_by_id = current_user.id
            
            db.session.commit()
            flash('Generic scheduled task plan updated successfully', 'success')
            return redirect(url_for('maintenance.generic_scheduled_task_plans_detail', id=plan.id))
        
        asset_types = AssetType.query.order_by(AssetType.name).all()
        make_models = MakeModel.query.order_by(MakeModel.make, MakeModel.model).all()
        action_sets = TemplateActionSet.query.order_by(TemplateActionSet.name).all()
        
        return render_template('maintenance/generic_scheduled_task_plans/edit.html',
                             plan=plan, asset_types=asset_types, make_models=make_models, action_sets=action_sets)
        
    except Exception as e:
        logger.error(f"Error editing generic scheduled task plan {id}: {e}")
        flash('Error editing scheduled task plan', 'error')
        return redirect(url_for('maintenance.generic_scheduled_task_plans_detail', id=id))

@generic_scheduled_plans_bp.route('/generic-scheduled-task-plans/<int:id>/delete', methods=['POST'])
@login_required
def generic_scheduled_task_plans_delete(id):
    """Delete generic scheduled task plan"""
    try:
        plan = GenericScheduledTaskPlan.query.get_or_404(id)
        name = plan.name
        
        db.session.delete(plan)
        db.session.commit()
        
        flash(f'Generic scheduled task plan "{name}" deleted successfully', 'success')
        return redirect(url_for('maintenance.generic_scheduled_task_plans_list'))
        
    except Exception as e:
        logger.error(f"Error deleting generic scheduled task plan {id}: {e}")
        flash('Error deleting scheduled task plan', 'error')
        return redirect(url_for('maintenance.generic_scheduled_task_plans_detail', id=id))

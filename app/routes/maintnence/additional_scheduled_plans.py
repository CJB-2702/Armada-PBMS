#!/usr/bin/env python3
"""
Additional Scheduled Plans Routes
Handles CRUD operations for additional scheduled maintenance task plans
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.maintnence import AdditionalScheduledTaskPlan
from app.models.core import Asset
from app.models.maintnence.templates.template_action_set import TemplateActionSet
from app.logger import get_logger

logger = get_logger(__name__)

# Create blueprint
additional_scheduled_plans_bp = Blueprint('additional_scheduled_plans', __name__)

# ==============================================================================
# ADDITIONAL SCHEDULED TASK PLANS
# ==============================================================================

@additional_scheduled_plans_bp.route('/additional-scheduled-task-plans')
@login_required
def additional_scheduled_task_plans_list():
    """List all additional scheduled task plans"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        plans = AdditionalScheduledTaskPlan.query.order_by(
            AdditionalScheduledTaskPlan.asset_id,
            AdditionalScheduledTaskPlan.name
        ).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return render_template(
            'maintenance/additional_scheduled_task_plans/list.html',
            plans=plans
        )
    except Exception as e:
        logger.error(f"Error loading additional scheduled task plans: {e}")
        flash('Error loading scheduled task plans', 'error')
        return redirect(url_for('maintenance.index'))

@additional_scheduled_plans_bp.route('/additional-scheduled-task-plans/create', methods=['GET', 'POST'])
@login_required
def additional_scheduled_task_plans_create():
    """Create a new additional scheduled task plan"""
    try:
        if request.method == 'POST':
            name = request.form.get('name')
            description = request.form.get('description')
            asset_id = request.form.get('asset_id')
            template_action_set_id = request.form.get('template_action_set_id')
            interval_meter1 = request.form.get('interval_meter1', type=int)
            interval_meter2 = request.form.get('interval_meter2', type=int)
            interval_meter3 = request.form.get('interval_meter3', type=int)
            interval_meter4 = request.form.get('interval_meter4', type=int)
            interval_days = request.form.get('interval_days', type=int)
            is_active = request.form.get('is_active') == 'on'
            
            if not all([name, asset_id, template_action_set_id]):
                flash('Name, asset, and template action set are required', 'error')
                return render_template('maintenance/additional_scheduled_task_plans/create.html',
                                     assets=Asset.query.all(),
                                     action_sets=TemplateActionSet.query.all())
            
            plan = AdditionalScheduledTaskPlan(
                name=name,
                description=description,
                asset_id=asset_id,
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
            
            flash(f'Additional scheduled task plan "{name}" created successfully', 'success')
            return redirect(url_for('maintenance.additional_scheduled_task_plans_detail', id=plan.id))
        
        assets = Asset.query.order_by(Asset.name).all()
        action_sets = TemplateActionSet.query.order_by(TemplateActionSet.name).all()
        
        return render_template('maintenance/additional_scheduled_task_plans/create.html',
                             assets=assets, action_sets=action_sets)
        
    except Exception as e:
        logger.error(f"Error creating additional scheduled task plan: {e}")
        flash('Error creating scheduled task plan', 'error')
        return redirect(url_for('maintenance.additional_scheduled_task_plans_list'))

@additional_scheduled_plans_bp.route('/additional-scheduled-task-plans/<int:id>')
@login_required
def additional_scheduled_task_plans_detail(id):
    """View additional scheduled task plan details"""
    try:
        plan = AdditionalScheduledTaskPlan.query.get_or_404(id)
        return render_template('maintenance/additional_scheduled_task_plans/detail.html', plan=plan)
    except Exception as e:
        logger.error(f"Error loading additional scheduled task plan {id}: {e}")
        flash('Error loading scheduled task plan', 'error')
        return redirect(url_for('maintenance.additional_scheduled_task_plans_list'))

@additional_scheduled_plans_bp.route('/additional-scheduled-task-plans/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def additional_scheduled_task_plans_edit(id):
    """Edit additional scheduled task plan"""
    try:
        plan = AdditionalScheduledTaskPlan.query.get_or_404(id)
        
        if request.method == 'POST':
            plan.name = request.form.get('name')
            plan.description = request.form.get('description')
            plan.asset_id = request.form.get('asset_id')
            plan.template_action_set_id = request.form.get('template_action_set_id')
            plan.interval_meter1 = request.form.get('interval_meter1', type=int)
            plan.interval_meter2 = request.form.get('interval_meter2', type=int)
            plan.interval_meter3 = request.form.get('interval_meter3', type=int)
            plan.interval_meter4 = request.form.get('interval_meter4', type=int)
            plan.interval_days = request.form.get('interval_days', type=int)
            plan.is_active = request.form.get('is_active') == 'on'
            plan.updated_by_id = current_user.id
            
            db.session.commit()
            flash('Additional scheduled task plan updated successfully', 'success')
            return redirect(url_for('maintenance.additional_scheduled_task_plans_detail', id=plan.id))
        
        assets = Asset.query.order_by(Asset.name).all()
        action_sets = TemplateActionSet.query.order_by(TemplateActionSet.name).all()
        
        return render_template('maintenance/additional_scheduled_task_plans/edit.html',
                             plan=plan, assets=assets, action_sets=action_sets)
        
    except Exception as e:
        logger.error(f"Error editing additional scheduled task plan {id}: {e}")
        flash('Error editing scheduled task plan', 'error')
        return redirect(url_for('maintenance.additional_scheduled_task_plans_detail', id=id))

@additional_scheduled_plans_bp.route('/additional-scheduled-task-plans/<int:id>/delete', methods=['POST'])
@login_required
def additional_scheduled_task_plans_delete(id):
    """Delete additional scheduled task plan"""
    try:
        plan = AdditionalScheduledTaskPlan.query.get_or_404(id)
        name = plan.name
        
        db.session.delete(plan)
        db.session.commit()
        
        flash(f'Additional scheduled task plan "{name}" deleted successfully', 'success')
        return redirect(url_for('maintenance.additional_scheduled_task_plans_list'))
        
    except Exception as e:
        logger.error(f"Error deleting additional scheduled task plan {id}: {e}")
        flash('Error deleting scheduled task plan', 'error')
        return redirect(url_for('maintenance.additional_scheduled_task_plans_detail', id=id))

"""
Maintenance work and edit routes for maintenance events
"""
from flask import Blueprint, render_template, abort, request, flash, redirect, url_for
from flask_login import login_required, current_user
from datetime import datetime
from app.logger import get_logger
from app import db

logger = get_logger("asset_management.routes.maintenance")

# Create blueprint for maintenance event work/edit routes
maintenance_event_bp = Blueprint('maintenance_event', __name__, url_prefix='/maintenance/maintenance-event')


@maintenance_event_bp.route('/<int:event_id>')
@maintenance_event_bp.route('/<int:event_id>/view')
@login_required
def view_maintenance_event(event_id):
    """View detailed information about a maintenance event"""
    logger.info(f"Viewing maintenance event for event_id={event_id}")
    
    try:
        from app.buisness.maintenance.base.maintenance_action_set_struct import MaintenanceActionSetStruct
        from app.buisness.maintenance.base.maintenance_context import MaintenanceContext
        from app.buisness.maintenance.base.action_struct import ActionStruct
        from app.data.core.event_info.event import Event
        
        # Get the maintenance action set by event_id (ONE-TO-ONE relationship)
        maintenance_struct = MaintenanceActionSetStruct.from_event_id(event_id)
        
        if not maintenance_struct:
            logger.warning(f"No maintenance action set found for event_id={event_id}")
            abort(404)
        
        # Get the event
        event = Event.query.get(event_id)
        if not event:
            logger.warning(f"Event {event_id} not found")
            abort(404)
        
        # Get actions with their structs for convenient access
        action_structs = [ActionStruct(action) for action in maintenance_struct.actions]
        
        # Get context for business logic if needed
        maintenance_context = MaintenanceContext(maintenance_struct)
        
        # Calculate action status counts
        completed_count = sum(1 for a in action_structs if a.action.status == 'Complete')
        in_progress_count = sum(1 for a in action_structs if a.action.status == 'In Progress')
        
        # Get delays for display
        delays = maintenance_struct.delays if hasattr(maintenance_struct, 'delays') else []
        active_delays = [d for d in delays if d.delay_end_date is None]
        
        return render_template(
            'maintenance/view_maintenance_event.html',
            maintenance=maintenance_struct,
            maintenance_context=maintenance_context,
            event=event,
            actions=action_structs,
            completed_count=completed_count,
            in_progress_count=in_progress_count,
            delays=delays,
            active_delays=active_delays,
        )
        
    except ImportError as e:
        logger.error(f"Could not import maintenance modules: {e}")
        abort(500)
    except Exception as e:
        logger.error(f"Error viewing maintenance event {event_id}: {e}")
        abort(500)


@maintenance_event_bp.route('/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_maintenance_event(event_id):
    """Edit a maintenance event"""
    logger.info(f"Editing maintenance event for event_id={event_id}")
    
    try:
        from app.buisness.maintenance.base.maintenance_action_set_struct import MaintenanceActionSetStruct
        from app.buisness.maintenance.base.action_struct import ActionStruct
        from app.buisness.maintenance.base.maintenance_context import MaintenanceContext
        from app.data.core.event_info.event import Event
        from app.data.core.asset_info.asset import Asset
        from app.data.maintenance.base.maintenance_plans import MaintenancePlan
        
        # Get the maintenance action set by event_id (ONE-TO-ONE relationship)
        maintenance_struct = MaintenanceActionSetStruct.from_event_id(event_id)
        
        if not maintenance_struct:
            logger.warning(f"No maintenance action set found for event_id={event_id}")
            abort(404)
        
        # Get the event
        event = Event.query.get(event_id)
        if not event:
            logger.warning(f"Event {event_id} not found")
            abort(404)
        
        # Handle POST request (form submission)
        if request.method == 'POST':
            # ===== FORM PARSING SECTION =====
            task_name = request.form.get('task_name', '').strip()
            description = request.form.get('description', '').strip()
            estimated_duration_str = request.form.get('estimated_duration', '').strip()
            asset_id_str = request.form.get('asset_id', '').strip()
            maintenance_plan_id_str = request.form.get('maintenance_plan_id', '').strip()
            status = request.form.get('status', '').strip()
            priority = request.form.get('priority', '').strip()
            planned_start_datetime_str = request.form.get('planned_start_datetime', '').strip()
            safety_review_required_str = request.form.get('safety_review_required', '').strip()
            staff_count_str = request.form.get('staff_count', '').strip()
            labor_hours_str = request.form.get('labor_hours', '').strip()
            completion_notes = request.form.get('completion_notes', '').strip()
            
            # ===== DATA TYPE CONVERSION SECTION =====
            # Convert description (string or None)
            description = description if description else None
            
            # Convert estimated_duration (float)
            # Allow None/empty to clear the field
            estimated_duration = None
            if estimated_duration_str:
                try:
                    estimated_duration = float(estimated_duration_str)
                    if estimated_duration < 0:
                        flash('Estimated duration must be non-negative', 'error')
                        return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
                except ValueError:
                    flash('Invalid estimated duration', 'error')
                    return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
            # If empty string, estimated_duration stays None (will clear the field via nullable_fields logic)
            
            # Convert asset_id (integer)
            asset_id = None
            if asset_id_str:
                try:
                    asset_id = int(asset_id_str)
                except ValueError:
                    flash('Invalid asset ID', 'error')
                    return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
            
            # Convert maintenance_plan_id (integer)
            maintenance_plan_id = None
            if maintenance_plan_id_str:
                try:
                    maintenance_plan_id = int(maintenance_plan_id_str)
                except ValueError:
                    flash('Invalid maintenance plan ID', 'error')
                    return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
            
            # Convert staff_count (integer)
            staff_count = None
            if staff_count_str:
                try:
                    staff_count = int(staff_count_str)
                except ValueError:
                    flash('Invalid staff count', 'error')
                    return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
            
            # Convert labor_hours (float)
            labor_hours = None
            if labor_hours_str:
                try:
                    labor_hours = float(labor_hours_str)
                except ValueError:
                    flash('Invalid labor hours', 'error')
                    return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
            
            # Convert planned_start_datetime (datetime)
            planned_start_datetime = None
            if planned_start_datetime_str:
                try:
                    planned_start_datetime = datetime.strptime(planned_start_datetime_str, '%Y-%m-%dT%H:%M')
                except ValueError:
                    flash('Invalid planned start datetime format', 'error')
                    return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
            
            # Convert safety_review_required (boolean)
            safety_review_required = safety_review_required_str == 'on'
            
            # Convert completion_notes (string or None)
            completion_notes = completion_notes if completion_notes else None
            
            # ===== BUSINESS LOGIC SECTION =====
            maintenance_context = MaintenanceContext(maintenance_struct)
            maintenance_context.update_action_set_details(
                task_name=task_name,
                description=description,
                estimated_duration=estimated_duration,  # Can be None to clear the field
                asset_id=asset_id,
                maintenance_plan_id=maintenance_plan_id,
                status=status,
                priority=priority,
                planned_start_datetime=planned_start_datetime,
                safety_review_required=safety_review_required,
                staff_count=staff_count,
                labor_hours=labor_hours,
                completion_notes=completion_notes
            )
            
            flash('Maintenance event updated successfully', 'success')
            # Reload the page (redirect back to edit page)
            return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
        
        # Handle GET request (display form)
        # Get actions with their structs (ordered by sequence_order)
        action_structs = [ActionStruct(action) for action in sorted(maintenance_struct.actions, key=lambda a: a.sequence_order)]
        
        # Get selected action ID from query parameter (for action editor panel)
        selected_action_id = request.args.get('action_id', type=int)
        selected_action_struct = None
        if selected_action_id and action_structs:
            selected_action_struct = next((a for a in action_structs if a.action_id == selected_action_id), None)
        # Default to first action if none selected or invalid
        if not selected_action_struct and action_structs:
            selected_action_struct = action_structs[0]
        
        # Get related data for dropdowns
        assets = Asset.query.order_by(Asset.name).all()
        maintenance_plans = MaintenancePlan.query.order_by(MaintenancePlan.name).all()
        
        # Get delays
        delays = maintenance_struct.delays
        active_delays = [d for d in delays if d.delay_end_date is None]
        
        # Get parts and tools for dropdowns
        from app.data.core.supply.part import Part
        from app.data.core.supply.tool import Tool
        from app.data.core.user_info.user import User
        parts = Part.query.filter_by(status='Active').order_by(Part.part_name).all()
        tools = Tool.query.order_by(Tool.tool_name).all()
        users = User.query.order_by(User.username).all()
        
        # Get maintenance context for summaries
        maintenance_context = MaintenanceContext(maintenance_struct)
        
        return render_template(
            'maintenance/edit_maintenance_event.html',
            maintenance=maintenance_struct,
            maintenance_context=maintenance_context,
            event=event,
            actions=action_structs,
            selected_action=selected_action_struct,
            assets=assets,
            maintenance_plans=maintenance_plans,
            delays=delays,
            active_delays=active_delays,
            parts=parts,
            tools=tools,
            users=users,
        )
        
    except ImportError as e:
        logger.error(f"Could not import maintenance modules: {e}")
        abort(500)
    except Exception as e:
        logger.error(f"Error editing maintenance event {event_id}: {e}")
        abort(500)


@maintenance_event_bp.route('/<int:event_id>/work')
@login_required
def work_maintenance_event(event_id):
    """Work on a maintenance event (perform maintenance)"""
    logger.info(f"Working on maintenance event for event_id={event_id}")
    
    try:
        from app.buisness.maintenance.base.maintenance_action_set_struct import MaintenanceActionSetStruct
        from app.buisness.maintenance.base.maintenance_context import MaintenanceContext
        from app.buisness.maintenance.base.action_struct import ActionStruct
        from app.data.core.event_info.event import Event
        
        # Get the maintenance action set by event_id (ONE-TO-ONE relationship)
        maintenance_struct = MaintenanceActionSetStruct.from_event_id(event_id)
        
        if not maintenance_struct:
            logger.warning(f"No maintenance action set found for event_id={event_id}")
            abort(404)
        
        # Check if maintenance is in Delayed status - redirect to view page
        if maintenance_struct.status == 'Delayed':
            flash('Work is paused due to delay. Please end the delay to continue work.', 'warning')
            return redirect(url_for('maintenance_event.view_maintenance_event', event_id=event_id))
        
        # Get the event
        event = Event.query.get(event_id)
        if not event:
            logger.warning(f"Event {event_id} not found")
            abort(404)
        
        # Check if event status is complete - redirect to view page
        if event.status and event.status.lower() == 'complete':
            return redirect(url_for('maintenance_event.view_maintenance_event', event_id=event_id))
        
        # Get actions with their structs
        action_structs = [ActionStruct(action) for action in maintenance_struct.actions]
        
        # Get context for business logic
        maintenance_context = MaintenanceContext(maintenance_struct)
        
        # Get asset if available
        asset = maintenance_struct.asset if hasattr(maintenance_struct, 'asset') else None
        
        # Get delays for display
        delays = maintenance_struct.delays if hasattr(maintenance_struct, 'delays') else []
        active_delays = [d for d in delays if d.delay_end_date is None]
        
        # Get parts for part demand dropdown
        from app.data.core.supply.part import Part
        from app.data.core.user_info.user import User
        parts = Part.query.filter_by(status='Active').order_by(Part.part_name).all()
        users = User.query.order_by(User.username).all()
        
        # Check if all actions are in terminal states
        all_actions_terminal = maintenance_context.all_actions_in_terminal_states()
        
        return render_template(
            'maintenance/work_maintenance_event.html',
            maintenance=maintenance_struct,
            maintenance_context=maintenance_context,
            event=event,
            actions=action_structs,
            asset=asset,
            delays=delays,
            active_delays=active_delays,
            parts=parts,
            users=users,
            all_actions_terminal=all_actions_terminal,
        )
        
    except ImportError as e:
        logger.error(f"Could not import maintenance modules: {e}")
        abort(500)
    except Exception as e:
        logger.error(f"Error working on maintenance event {event_id}: {e}")
        abort(500)


# ============================================================================
# Work Page Interactivity Routes
# ============================================================================

@maintenance_event_bp.route('/<int:event_id>/action/<int:action_id>/update-status', methods=['POST'])
@login_required
def update_action_status(event_id, action_id):
    """Update action status with comment generation and part demand management"""
    try:
        from app.buisness.maintenance.base.maintenance_action_set_struct import MaintenanceActionSetStruct
        from app.buisness.maintenance.base.maintenance_context import MaintenanceContext
        from app.data.maintenance.base.actions import Action
        
        # ===== FORM PARSING SECTION =====
        # Get action and current status (needed for validation)
        action = Action.query.get_or_404(action_id)
        old_status = action.status
        
        # Parse form fields
        new_status = request.form.get('status', '').strip()
        comment = request.form.get('comment', '').strip()
        edited_comment = request.form.get('edited_comment', '').strip()
        billable_hours_str = request.form.get('billable_hours', '').strip()
        completion_notes = request.form.get('completion_notes', '').strip()
        issue_part_demands_str = request.form.get('issue_part_demands', 'false').strip()
        part_demand_action = request.form.get('part_demand_action', 'leave_as_is').strip()
        
        # Convert and validate data types
        # Use edited comment if provided, otherwise use original comment
        # If edited_comment exists, it means user edited it, so mark as human-made
        final_comment = edited_comment if edited_comment else comment
        is_human_made = bool(edited_comment)
        
        # Parse billable hours
        billable_hours = None
        if billable_hours_str:
            try:
                billable_hours = float(billable_hours_str)
                if billable_hours < 0:
                    billable_hours = None
            except ValueError:
                pass  # Ignore invalid values
        
        # Parse issue_part_demands (boolean)
        issue_part_demands = issue_part_demands_str.lower() == 'true'
        
        # Parse part demand actions (boolean flags)
        duplicate_part_demands = part_demand_action == 'duplicate'
        cancel_part_demands = part_demand_action == 'cancel'
        
        # ===== LIGHT VALIDATION SECTION =====
        # Validate status
        valid_statuses = ['Not Started', 'In Progress', 'Complete', 'Failed', 'Skipped', 'Blocked']
        if new_status not in valid_statuses:
            flash('Invalid status', 'error')
            return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        
        # Check if comment is required
        requires_comment = new_status in ['Blocked', 'Failed'] or (old_status in ['Complete', 'Failed'] and new_status in ['Complete', 'Failed'])
        if requires_comment and not final_comment:
            flash(f'Comment is required when marking action as {new_status}', 'error')
            return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        
        # ===== BUSINESS LOGIC SECTION =====
        # Get maintenance context from event_id
        maintenance_struct = MaintenanceActionSetStruct.from_event_id(event_id)
        if not maintenance_struct:
            flash('Maintenance event not found', 'error')
            return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        
        maintenance_context = MaintenanceContext(maintenance_struct)
        maintenance_context.update_action_status(
            action_id=action_id,
            user_id=current_user.id,
            username=current_user.username,
            new_status=new_status,
            old_status=old_status,
            final_comment=final_comment,
            is_human_made=is_human_made,
            billable_hours=billable_hours,
            completion_notes=completion_notes,
            issue_part_demands=issue_part_demands,
            duplicate_part_demands=duplicate_part_demands,
            cancel_part_demands=cancel_part_demands
        )
        
        flash(f'Action status updated to {new_status}', 'success')
        return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        
    except Exception as e:
        logger.error(f"Error updating action status: {e}")
        import traceback
        traceback.print_exc()
        flash('Error updating action status', 'error')
        return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))


@maintenance_event_bp.route('/<int:event_id>/action/<int:action_id>/update', methods=['POST'])
@login_required
def edit_action(event_id, action_id):
    """Full update action form to update all editable fields"""
    try:
        from app.data.maintenance.base.actions import Action
        from app.buisness.maintenance.base.maintenance_action_set_struct import MaintenanceActionSetStruct
        from app.buisness.core.event_context import EventContext
        from app.buisness.maintenance.base.action_context import ActionContext
        from app.buisness.maintenance.base.maintenance_context import MaintenanceContext
        
        # ===== FORM PARSING SECTION =====
        # Get action and current status (needed for validation)
        action = Action.query.get_or_404(action_id)
        old_status = action.status
        
        # Parse all form fields
        # Check redirect target (for edit page vs work page)
        redirect_target = request.form.get('redirect_to', 'work').strip()
        reset_to_in_progress_str = request.form.get('reset_to_in_progress', 'false').strip()
        status_str = request.form.get('status', '').strip()
        scheduled_start_time_str = request.form.get('scheduled_start_time', '').strip()
        start_time_str = request.form.get('start_time', '').strip()
        end_time_str = request.form.get('end_time', '').strip()
        billable_hours_str = request.form.get('billable_hours', '').strip()
        estimated_duration_str = request.form.get('estimated_duration', '').strip()
        expected_billable_hours_str = request.form.get('expected_billable_hours', '').strip()
        completion_notes = request.form.get('completion_notes', '').strip()
        action_name = request.form.get('action_name', '').strip()
        description = request.form.get('description', '').strip()
        safety_notes = request.form.get('safety_notes', '').strip()
        notes = request.form.get('notes', '').strip()
        assigned_user_id_str = request.form.get('assigned_user_id', '').strip()
        sequence_order_str = request.form.get('sequence_order', '').strip()
        maintenance_action_set_id_str = request.form.get('maintenance_action_set_id', '').strip()
        
        # ===== DATA TYPE CONVERSION SECTION =====
        # Prepare update dictionary
        updates = {}
        
        # Convert reset_to_in_progress (boolean)
        reset_to_in_progress = reset_to_in_progress_str.lower() == 'true'
        if reset_to_in_progress:
            updates['reset_to_in_progress'] = True
        
        # Convert status (string)
        if status_str:
            updates['status'] = status_str
        
        # Convert datetime fields
        if scheduled_start_time_str:
            try:
                updates['scheduled_start_time'] = datetime.strptime(scheduled_start_time_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                flash('Invalid scheduled start time format', 'error')
                return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        elif 'scheduled_start_time' in request.form:  # Explicitly cleared
            updates['scheduled_start_time'] = None
        
        if start_time_str:
            try:
                updates['start_time'] = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                flash('Invalid start time format', 'error')
                return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        elif 'start_time' in request.form:  # Explicitly cleared
            updates['start_time'] = None
        
        if end_time_str:
            try:
                end_time = datetime.strptime(end_time_str, '%Y-%m-%dT%H:%M')
                updates['end_time'] = end_time
            except ValueError:
                flash('Invalid end time format', 'error')
                return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        elif 'end_time' in request.form and not reset_to_in_progress:  # Explicitly cleared
            updates['end_time'] = None
        
        # Convert numeric fields
        if billable_hours_str:
            try:
                billable_hours = float(billable_hours_str)
                if billable_hours < 0:
                    flash('Billable hours must be non-negative', 'error')
                    return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
                updates['billable_hours'] = billable_hours
            except ValueError:
                flash('Invalid billable hours value', 'error')
                return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        elif 'billable_hours' in request.form:  # Explicitly cleared
            updates['billable_hours'] = None
        
        if estimated_duration_str:
            try:
                estimated_duration = float(estimated_duration_str)
                if estimated_duration < 0:
                    flash('Estimated duration must be non-negative', 'error')
                    return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
                updates['estimated_duration'] = estimated_duration
            except ValueError:
                flash('Invalid estimated duration value', 'error')
                return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        elif 'estimated_duration' in request.form:  # Explicitly cleared
            updates['estimated_duration'] = None
        
        if expected_billable_hours_str:
            try:
                expected_billable_hours = float(expected_billable_hours_str)
                if expected_billable_hours < 0:
                    flash('Expected billable hours must be non-negative', 'error')
                    return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
                updates['expected_billable_hours'] = expected_billable_hours
            except ValueError:
                flash('Invalid expected billable hours value', 'error')
                return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        elif 'expected_billable_hours' in request.form:  # Explicitly cleared
            updates['expected_billable_hours'] = None
        
        # Convert text fields
        if completion_notes or 'completion_notes' in request.form:
            updates['completion_notes'] = completion_notes if completion_notes else None
        
        if action_name:
            updates['action_name'] = action_name
        
        if description or 'description' in request.form:
            updates['description'] = description if description else None
        
        if safety_notes or 'safety_notes' in request.form:
            updates['safety_notes'] = safety_notes if safety_notes else None
        
        if notes or 'notes' in request.form:
            updates['notes'] = notes if notes else None
        
        # Convert assigned_user_id (integer)
        if assigned_user_id_str:
            try:
                assigned_user_id = int(assigned_user_id_str)
                updates['assigned_user_id'] = assigned_user_id
            except ValueError:
                flash('Invalid assigned user ID', 'error')
                return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        elif 'assigned_user_id' in request.form:  # Explicitly cleared
            updates['assigned_user_id'] = None
        
        # Convert sequence_order (integer)
        if sequence_order_str:
            try:
                sequence_order = int(sequence_order_str)
                if sequence_order < 1:
                    flash('Sequence order must be at least 1', 'error')
                    return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
                updates['sequence_order'] = sequence_order
            except ValueError:
                flash('Invalid sequence order value', 'error')
                return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        
        # Convert maintenance_action_set_id (integer)
        if maintenance_action_set_id_str:
            try:
                maintenance_action_set_id = int(maintenance_action_set_id_str)
                if maintenance_action_set_id == action.maintenance_action_set_id:
                    updates['maintenance_action_set_id'] = maintenance_action_set_id
            except ValueError:
                pass  # Ignore invalid values
        
        # ===== LIGHT VALIDATION SECTION =====
        # Validate: end_time must be after start_time
        if updates.get('end_time') and updates.get('start_time') and updates['end_time'] < updates['start_time']:
            flash('End time must be after start time', 'error')
            return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        
        # ===== BUSINESS LOGIC SECTION =====
        # Get maintenance struct and context
        maintenance_struct = MaintenanceActionSetStruct.from_event_id(event_id)
        if not maintenance_struct or not maintenance_struct.event_id:
            flash('Maintenance event not found', 'error')
            return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        
        # Delegate all business logic to MaintenanceContext
        maintenance_context = MaintenanceContext(maintenance_struct)
        maintenance_context.edit_action(
            action_id=action_id,
            user_id=current_user.id,
            username=current_user.username,
            updates=updates,
            old_status=old_status
        )
        
        flash('Action updated successfully', 'success')
        
        # Redirect based on source
        if redirect_target == 'edit':
            return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
        else:
            return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        
    except ValueError as e:
        flash(str(e), 'error')
        if redirect_target == 'edit':
            return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
        else:
            return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
    except Exception as e:
        logger.error(f"Error editing action: {e}")
        import traceback
        traceback.print_exc()
        flash('Error updating action', 'error')
        if redirect_target == 'edit':
            return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
        else:
            return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))


@maintenance_event_bp.route('/<int:event_id>/action/<int:action_id>/update-billable-hours', methods=['POST'])
@login_required
def update_action_billable_hours(event_id, action_id):
    """Update action billable hours"""
    try:
        from app.data.maintenance.base.actions import Action
        from app.buisness.maintenance.base.maintenance_action_set_struct import MaintenanceActionSetStruct
        from app.buisness.maintenance.base.maintenance_context import MaintenanceContext
        
        # ===== FORM PARSING SECTION =====
        billable_hours_str = request.form.get('billable_hours', '').strip()
        
        # ===== LIGHT VALIDATION SECTION =====
        if not billable_hours_str:
            flash('Billable hours is required', 'error')
            return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        
        # ===== DATA TYPE CONVERSION SECTION =====
        try:
            billable_hours = float(billable_hours_str)
            if billable_hours < 0:
                flash('Billable hours must be non-negative', 'error')
                return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        except ValueError:
            flash('Invalid billable hours value', 'error')
            return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        
        # ===== BUSINESS LOGIC SECTION =====
        action = Action.query.get_or_404(action_id)
        action.billable_hours = billable_hours
        db.session.commit()
        
        # Auto-update MaintenanceActionSet billable hours if sum is greater
        maintenance_struct = MaintenanceActionSetStruct.from_event_id(event_id)
        if maintenance_struct:
            maintenance_context = MaintenanceContext(maintenance_struct)
            maintenance_context.update_actual_billable_hours_auto()
        
        flash('Billable hours updated', 'success')
        return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        
    except Exception as e:
        logger.error(f"Error updating action billable hours: {e}")
        flash('Error updating billable hours', 'error')
        return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))


@maintenance_event_bp.route('/<int:event_id>/update-datetime', methods=['POST'])
@login_required
def update_maintenance_datetime(event_id):
    """Update maintenance start/end dates"""
    try:
        from app.buisness.maintenance.base.maintenance_action_set_struct import MaintenanceActionSetStruct
        
        # ===== FORM PARSING SECTION =====
        start_date_str = request.form.get('start_date', '').strip()
        end_date_str = request.form.get('end_date', '').strip()
        
        # ===== DATA TYPE CONVERSION SECTION =====
        start_date = None
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                flash('Invalid start date format', 'error')
                return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        
        end_date = None
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                flash('Invalid end date format', 'error')
                return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        
        # ===== LIGHT VALIDATION SECTION =====
        # Validate: end_date must be after start_date
        if end_date and start_date and end_date < start_date:
            flash('End date must be after start date', 'error')
            return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        
        # ===== BUSINESS LOGIC SECTION =====
        maintenance_struct = MaintenanceActionSetStruct.from_event_id(event_id)
        if not maintenance_struct:
            abort(404)
        
        if start_date:
            maintenance_struct.maintenance_action_set.start_date = start_date
        if end_date:
            maintenance_struct.maintenance_action_set.end_date = end_date
        
        db.session.commit()
        flash('Maintenance dates updated', 'success')
        return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        
    except Exception as e:
        logger.error(f"Error updating maintenance datetime: {e}")
        flash('Error updating maintenance dates', 'error')
        return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))


@maintenance_event_bp.route('/<int:event_id>/update-billable-hours', methods=['POST'])
@login_required
def update_maintenance_billable_hours(event_id):
    """Update maintenance total billable hours"""
    try:
        from app.buisness.maintenance.base.maintenance_action_set_struct import MaintenanceActionSetStruct
        from app.buisness.maintenance.base.maintenance_context import MaintenanceContext
        
        # ===== FORM PARSING SECTION =====
        billable_hours_str = request.form.get('actual_billable_hours', '').strip()
        
        # ===== LIGHT VALIDATION SECTION =====
        if not billable_hours_str:
            flash('Billable hours is required', 'error')
            return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        
        # ===== DATA TYPE CONVERSION SECTION =====
        try:
            billable_hours = float(billable_hours_str)
        except ValueError:
            flash('Invalid billable hours value', 'error')
            return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        
        # ===== BUSINESS LOGIC SECTION =====
        maintenance_struct = MaintenanceActionSetStruct.from_event_id(event_id)
        if not maintenance_struct:
            abort(404)
        
        maintenance_context = MaintenanceContext(maintenance_struct)
        try:
            maintenance_context.set_actual_billable_hours(billable_hours)
        except ValueError as e:
            flash(str(e), 'error')
            return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        
        flash('Maintenance billable hours updated', 'success')
        return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        
    except Exception as e:
        logger.error(f"Error updating maintenance billable hours: {e}")
        flash('Error updating billable hours', 'error')
        return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))


@maintenance_event_bp.route('/<int:event_id>/complete', methods=['POST'])
@login_required
def complete_maintenance(event_id):
    """Complete maintenance event with validation"""
    try:
        from app.buisness.maintenance.base.maintenance_action_set_struct import MaintenanceActionSetStruct
        from app.buisness.maintenance.base.maintenance_context import MaintenanceContext
        from app.buisness.core.event_context import EventContext
        
        # ===== FORM PARSING SECTION =====
        completion_comment = request.form.get('completion_comment', '').strip()
        start_date_str = request.form.get('actual_start_date', '').strip()
        end_date_str = request.form.get('actual_end_date', '').strip()
        billable_hours_str = request.form.get('actual_billable_hours', '').strip()
        
        # ===== LIGHT VALIDATION SECTION =====
        if not completion_comment:
            flash('Completion comment is required', 'error')
            return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        
        if not start_date_str or not end_date_str:
            flash('Both start and end dates are required', 'error')
            return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        
        if not billable_hours_str:
            flash('Billable hours is required', 'error')
            return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        
        # ===== DATA TYPE CONVERSION SECTION =====
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%dT%H:%M')
            end_date = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Invalid date format', 'error')
            return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        
        try:
            billable_hours = float(billable_hours_str)
        except ValueError:
            flash('Invalid billable hours value', 'error')
            return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        
        # Additional validation after conversion
        if end_date < start_date:
            flash('End date must be after start date', 'error')
            return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        
        if billable_hours < 0.2:
            flash('Billable hours must be at least 0.2 hours (12 minutes)', 'error')
            return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        
        # ===== BUSINESS LOGIC SECTION =====
        maintenance_struct = MaintenanceActionSetStruct.from_event_id(event_id)
        if not maintenance_struct:
            abort(404)
        
        # Check all actions are in terminal states
        blocked_actions = [a for a in maintenance_struct.actions if a.status == 'Blocked']
        if blocked_actions:
            flash('Cannot complete maintenance. Please resolve all blocked actions first.', 'error')
            return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        
        # Update maintenance using context manager
        maintenance_context = MaintenanceContext(maintenance_struct)
        # Set start_date and billable hours before completing
        maintenance_struct.maintenance_action_set.start_date = start_date
        maintenance_context.set_actual_billable_hours(billable_hours)
        # Use complete() method which will sync Event.status
        maintenance_context.complete(
            user_id=current_user.id,
            notes=completion_comment
        )
        # Set end_date after complete() to preserve form value (complete() sets it to utcnow())
        maintenance_struct.maintenance_action_set.end_date = end_date
        db.session.commit()
        
        # Generate automated completion comment
        if maintenance_struct.event_id:
            event_context = EventContext(maintenance_struct.event_id)
            comment_text = f"Maintenance completed by {current_user.username}. {completion_comment}"
            event_context.add_comment(
                user_id=current_user.id,
                content=comment_text,
                is_human_made=False  # Automated comment
            )
            db.session.commit()
        
        flash('Maintenance completed successfully', 'success')
        return redirect(url_for('maintenance_event.view_maintenance_event', event_id=event_id))
        
    except Exception as e:
        logger.error(f"Error completing maintenance: {e}")
        flash('Error completing maintenance', 'error')
        return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))


@maintenance_event_bp.route('/<int:event_id>/action/<int:action_id>/part-demand/create', methods=['POST'])
@login_required
def create_part_demand(event_id, action_id):
    """Create a new part demand for an action"""
    try:
        from app.data.maintenance.base.part_demands import PartDemand
        from app.buisness.maintenance.base.maintenance_action_set_struct import MaintenanceActionSetStruct
        from app.buisness.core.event_context import EventContext
        
        # ===== FORM PARSING SECTION =====
        part_id_str = request.form.get('part_id', '').strip()
        quantity_str = request.form.get('quantity_required', '').strip()
        notes = request.form.get('notes', '').strip()
        
        # ===== LIGHT VALIDATION SECTION =====
        if not part_id_str or not quantity_str:
            flash('Part and quantity are required', 'error')
            return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        
        # ===== DATA TYPE CONVERSION SECTION =====
        try:
            part_id = int(part_id_str)
            quantity = float(quantity_str)
        except ValueError:
            flash('Invalid part ID or quantity', 'error')
            return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        
        if quantity <= 0:
            flash('Quantity must be greater than 0', 'error')
            return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        
        # Create part demand
        part_demand = PartDemand(
            action_id=action_id,
            part_id=part_id,
            quantity_required=quantity,
            notes=notes,
            status='Pending Manager Approval',
            requested_by_id=current_user.id,
            created_by_id=current_user.id,
            updated_by_id=current_user.id
        )
        db.session.add(part_demand)
        db.session.commit()
        
        # Generate automated comment
        maintenance_struct = MaintenanceActionSetStruct.from_event_id(event_id)
        if maintenance_struct and maintenance_struct.event_id:
            event_context = EventContext(maintenance_struct.event_id)
            from app.data.core.supply.part import Part
            part = Part.query.get(part_id)
            part_name = part.part_name if part else f"Part #{part_id}"
            comment_text = f"Part demand created: {part_name} x{quantity} by {current_user.username}"
            if notes:
                comment_text += f". Notes: {notes}"
            event_context.add_comment(
                user_id=current_user.id,
                content=comment_text,
                is_human_made=False  # Automated comment
            )
            db.session.commit()
        
        flash('Part demand created successfully', 'success')
        return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        
    except Exception as e:
        logger.error(f"Error creating part demand: {e}")
        flash('Error creating part demand', 'error')
        return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))


@maintenance_event_bp.route('/<int:event_id>/part-demand/<int:part_demand_id>/issue', methods=['POST'])
@login_required
def issue_part_demand(event_id, part_demand_id):
    """Issue a part demand (any user can issue)"""
    try:
        from app.data.maintenance.base.part_demands import PartDemand
        from app.buisness.maintenance.base.maintenance_action_set_struct import MaintenanceActionSetStruct
        from app.buisness.core.event_context import EventContext
        
        part_demand = PartDemand.query.get_or_404(part_demand_id)
        
        # Update status to Issued
        part_demand.status = 'Issued'
        db.session.commit()
        
        # Generate automated comment
        maintenance_struct = MaintenanceActionSetStruct.from_event_id(event_id)
        if maintenance_struct and maintenance_struct.event_id:
            event_context = EventContext(maintenance_struct.event_id)
            from app.data.core.supply.part import Part
            part = Part.query.get(part_demand.part_id)
            part_name = part.part_name if part else f"Part #{part_demand.part_id}"
            comment_text = f"Part issued: {part_name} x{part_demand.quantity_required} by {current_user.username}"
            event_context.add_comment(
                user_id=current_user.id,
                content=comment_text,
                is_human_made=False  # Automated comment
            )
            db.session.commit()
        
        flash('Part issued successfully', 'success')
        return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        
    except Exception as e:
        logger.error(f"Error issuing part demand: {e}")
        flash('Error issuing part', 'error')
        return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))


@maintenance_event_bp.route('/<int:event_id>/part-demand/<int:part_demand_id>/cancel', methods=['POST'])
@login_required
def cancel_part_demand(event_id, part_demand_id):
    """Cancel a part demand (technician can cancel if not issued)"""
    try:
        from app.data.maintenance.base.part_demands import PartDemand
        from app.buisness.maintenance.base.maintenance_action_set_struct import MaintenanceActionSetStruct
        from app.buisness.core.event_context import EventContext
        
        part_demand = PartDemand.query.get_or_404(part_demand_id)
        
        # Check if already issued
        if part_demand.status == 'Issued':
            flash('Cannot cancel an issued part demand', 'error')
            return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        
        # Require cancellation comment
        cancellation_comment = request.form.get('cancellation_comment', '').strip()
        if not cancellation_comment:
            flash('Cancellation comment is required', 'error')
            return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        
        # Update status
        part_demand.status = 'Cancelled by Technician'
        db.session.commit()
        
        # Generate automated comment
        maintenance_struct = MaintenanceActionSetStruct.from_event_id(event_id)
        if maintenance_struct and maintenance_struct.event_id:
            event_context = EventContext(maintenance_struct.event_id)
            from app.data.core.supply.part import Part
            part = Part.query.get(part_demand.part_id)
            part_name = part.part_name if part else f"Part #{part_demand.part_id}"
            comment_text = f"Part demand cancelled: {part_name} x{part_demand.quantity_required} by {current_user.username}. Reason: {cancellation_comment}"
            event_context.add_comment(
                user_id=current_user.id,
                content=comment_text,
                is_human_made=False  # Automated comment
            )
            db.session.commit()
        
        flash('Part demand cancelled successfully', 'success')
        return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        
    except Exception as e:
        logger.error(f"Error cancelling part demand: {e}")
        flash('Error cancelling part demand', 'error')
        return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))


@maintenance_event_bp.route('/<int:event_id>/part-demand/<int:part_demand_id>/undo', methods=['POST'])
@login_required
def undo_part_demand(event_id, part_demand_id):
    """Undo a cancelled part demand - reset it back to Planned status"""
    try:
        from app.data.maintenance.base.part_demands import PartDemand
        from app.buisness.maintenance.base.maintenance_action_set_struct import MaintenanceActionSetStruct
        from app.buisness.core.event_context import EventContext
        
        part_demand = PartDemand.query.get_or_404(part_demand_id)
        
        # Only allow undo if status is cancelled
        if part_demand.status not in ['Cancelled by Technician', 'Cancelled by Supply']:
            flash('Can only undo cancelled part demands', 'error')
            return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        
        # Reset status to Planned (default state)
        part_demand.status = 'Planned'
        db.session.commit()
        
        # Generate automated comment
        maintenance_struct = MaintenanceActionSetStruct.from_event_id(event_id)
        if maintenance_struct and maintenance_struct.event_id:
            event_context = EventContext(maintenance_struct.event_id)
            from app.data.core.supply.part import Part
            part = Part.query.get(part_demand.part_id)
            part_name = part.part_name if part else f"Part #{part_demand.part_id}"
            comment_text = f"Part demand reset to planned: {part_name} x{part_demand.quantity_required} by {current_user.username}"
            event_context.add_comment(
                user_id=current_user.id,
                content=comment_text,
                is_human_made=False  # Automated comment
            )
            db.session.commit()
        
        flash('Part demand reset to planned successfully', 'success')
        return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        
    except Exception as e:
        logger.error(f"Error undoing part demand: {e}")
        flash('Error undoing part demand', 'error')
        return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))


@maintenance_event_bp.route('/<int:event_id>/part-demand/<int:part_demand_id>/update', methods=['POST'])
@login_required
def update_part_demand(event_id, part_demand_id):
    """Update part demand details"""
    try:
        from app.data.maintenance.base.part_demands import PartDemand
        from app.buisness.maintenance.base.maintenance_action_set_struct import MaintenanceActionSetStruct
        from app.buisness.core.event_context import EventContext
        
        # Get part demand
        part_demand = PartDemand.query.get_or_404(part_demand_id)
        
        # Verify part demand belongs to this event (via action)
        from app.data.maintenance.base.actions import Action
        action = Action.query.get(part_demand.action_id)
        if not action or action.maintenance_action_set.event_id != event_id:
            flash('Part demand does not belong to this maintenance event', 'error')
            return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
        
        # ===== FORM PARSING SECTION =====
        # Note: part_id should NOT be editable per requirements
        quantity_required_str = request.form.get('quantity_required', '').strip()
        status = request.form.get('status', '').strip()
        priority = request.form.get('priority', '').strip()
        notes = request.form.get('notes', '').strip()
        
        # ===== LIGHT VALIDATION SECTION =====
        valid_statuses = [
            'Planned', 'Pending Manager Approval', 'Pending Inventory Approval',
            'Ordered', 'Issued', 'Rejected', 'Backordered',
            'Cancelled by Technician', 'Cancelled by Supply'
        ]
        if status and status not in valid_statuses:
            flash('Invalid status', 'error')
            return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
        
        valid_priorities = ['Low', 'Medium', 'High', 'Critical']
        if priority and priority not in valid_priorities:
            priority = None  # Use existing value if invalid
        
        # ===== DATA TYPE CONVERSION SECTION =====
        quantity_required = None
        if quantity_required_str:
            try:
                quantity_required = float(quantity_required_str)
                if quantity_required <= 0:
                    flash('Quantity must be greater than 0', 'error')
                    return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
            except ValueError:
                flash('Invalid quantity value', 'error')
                return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
        
        # Convert empty strings to None
        status = status if status else None
        priority = priority if priority else None
        notes = notes if notes else None
        
        # ===== BUSINESS LOGIC SECTION =====
        # Update fields
        if quantity_required is not None:
            part_demand.quantity_required = quantity_required
        if status is not None:
            part_demand.status = status
        if priority is not None:
            part_demand.priority = priority
        if notes is not None:
            part_demand.notes = notes
        
        part_demand.updated_by_id = current_user.id
        db.session.commit()
        
        # Generate automated comment
        maintenance_struct = MaintenanceActionSetStruct.from_event_id(event_id)
        if maintenance_struct and maintenance_struct.event_id:
            event_context = EventContext(maintenance_struct.event_id)
            from app.data.core.supply.part import Part
            part = Part.query.get(part_demand.part_id)
            part_name = part.part_name if part else f"Part #{part_demand.part_id}"
            comment_text = f"Part demand updated: {part_name} x{part_demand.quantity_required} by {current_user.username}"
            if status:
                comment_text += f". Status: {status}"
            event_context.add_comment(
                user_id=current_user.id,
                content=comment_text,
                is_human_made=True
            )
            db.session.commit()
        
        flash('Part demand updated successfully', 'success')
        return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
        
    except Exception as e:
        logger.error(f"Error updating part demand: {e}")
        import traceback
        traceback.print_exc()
        flash('Error updating part demand', 'error')
        return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))


@maintenance_event_bp.route('/<int:event_id>/action/<int:action_id>/tool/create', methods=['POST'])
@login_required
def create_action_tool(event_id, action_id):
    """Create a new tool requirement for an action"""
    try:
        from app.data.maintenance.base.action_tools import ActionTool
        from app.data.maintenance.base.actions import Action
        from app.buisness.maintenance.base.maintenance_action_set_struct import MaintenanceActionSetStruct
        from app.buisness.core.event_context import EventContext
        
        # Verify action belongs to this event
        action = Action.query.get_or_404(action_id)
        maintenance_struct = MaintenanceActionSetStruct.from_event_id(event_id)
        if not maintenance_struct or action.maintenance_action_set_id != maintenance_struct.maintenance_action_set_id:
            flash('Action does not belong to this maintenance event', 'error')
            return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
        
        # ===== FORM PARSING SECTION =====
        tool_id_str = request.form.get('tool_id', '').strip()
        
        # ===== LIGHT VALIDATION SECTION =====
        if not tool_id_str:
            flash('Tool ID is required', 'error')
            return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
        
        # ===== DATA TYPE CONVERSION SECTION =====
        try:
            tool_id = int(tool_id_str)
        except ValueError:
            flash('Invalid tool ID', 'error')
            return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
        
        # Verify tool exists
        from app.data.core.supply.tool import Tool
        tool = Tool.query.get(tool_id)
        if not tool:
            flash('Tool not found', 'error')
            return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
        
        # ===== BUSINESS LOGIC SECTION =====
        # Create action tool
        action_tool = ActionTool(
            action_id=action_id,
            tool_id=tool_id,
            quantity_required=1,  # Default
            status='Planned',
            priority='Medium',
            sequence_order=1,  # Default, can be updated later
            created_by_id=current_user.id,
            updated_by_id=current_user.id
        )
        db.session.add(action_tool)
        db.session.commit()
        
        # Generate automated comment
        if maintenance_struct.event_id:
            event_context = EventContext(maintenance_struct.event_id)
            tool_name = tool.tool_name if tool else f"Tool #{tool_id}"
            comment_text = f"Tool requirement created: {tool_name} for action '{action.action_name}' by {current_user.username}"
            event_context.add_comment(
                user_id=current_user.id,
                content=comment_text,
                is_human_made=False  # Automated comment
            )
            db.session.commit()
        
        flash('Tool requirement created successfully', 'success')
        return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
        
    except Exception as e:
        logger.error(f"Error creating tool requirement: {e}")
        import traceback
        traceback.print_exc()
        flash('Error creating tool requirement', 'error')
        return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))


@maintenance_event_bp.route('/<int:event_id>/action/<int:action_id>/tool/<int:tool_id>/update', methods=['POST'])
@login_required
def update_action_tool(event_id, action_id, tool_id):
    """Update tool requirement details"""
    try:
        from app.data.maintenance.base.action_tools import ActionTool
        from app.data.maintenance.base.actions import Action
        from app.buisness.maintenance.base.maintenance_action_set_struct import MaintenanceActionSetStruct
        from app.buisness.core.event_context import EventContext
        
        # Get action tool (tool_id here is ActionTool.id, not Tool.id)
        action_tool = ActionTool.query.get_or_404(tool_id)
        
        # Verify action tool belongs to this action and event
        action = Action.query.get_or_404(action_id)
        if action_tool.action_id != action_id:
            flash('Tool requirement does not belong to this action', 'error')
            return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
        
        maintenance_struct = MaintenanceActionSetStruct.from_event_id(event_id)
        if not maintenance_struct or action.maintenance_action_set_id != maintenance_struct.maintenance_action_set_id:
            flash('Action does not belong to this maintenance event', 'error')
            return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
        
        # ===== FORM PARSING SECTION =====
        tool_id_new_str = request.form.get('tool_id', '').strip()  # Update to different tool
        quantity_required_str = request.form.get('quantity_required', '').strip()
        status = request.form.get('status', '').strip()
        priority = request.form.get('priority', '').strip()
        notes = request.form.get('notes', '').strip()
        
        # ===== LIGHT VALIDATION SECTION =====
        valid_statuses = ['Planned', 'Assigned', 'Returned', 'Missing']
        if status and status not in valid_statuses:
            flash('Invalid status', 'error')
            return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
        
        valid_priorities = ['Low', 'Medium', 'High', 'Critical']
        if priority and priority not in valid_priorities:
            priority = None  # Use existing value if invalid
        
        # ===== DATA TYPE CONVERSION SECTION =====
        tool_id_new = None
        if tool_id_new_str:
            try:
                tool_id_new = int(tool_id_new_str)
                # Verify tool exists
                from app.data.core.supply.tool import Tool
                tool = Tool.query.get(tool_id_new)
                if not tool:
                    flash('Tool not found', 'error')
                    return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
            except ValueError:
                flash('Invalid tool ID', 'error')
                return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
        
        quantity_required = None
        if quantity_required_str:
            try:
                quantity_required = int(quantity_required_str)
                if quantity_required < 1:
                    flash('Quantity must be at least 1', 'error')
                    return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
            except ValueError:
                flash('Invalid quantity value', 'error')
                return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
        
        # Convert empty strings to None
        status = status if status else None
        priority = priority if priority else None
        notes = notes if notes else None
        
        # ===== BUSINESS LOGIC SECTION =====
        # Update fields
        if tool_id_new is not None:
            action_tool.tool_id = tool_id_new
        if quantity_required is not None:
            action_tool.quantity_required = quantity_required
        if status is not None:
            action_tool.status = status
        if priority is not None:
            action_tool.priority = priority
        if notes is not None:
            action_tool.notes = notes
        
        action_tool.updated_by_id = current_user.id
        db.session.commit()
        
        # Generate automated comment
        if maintenance_struct.event_id:
            event_context = EventContext(maintenance_struct.event_id)
            from app.data.core.supply.tool import Tool
            tool = Tool.query.get(action_tool.tool_id)
            tool_name = tool.tool_name if tool else f"Tool #{action_tool.tool_id}"
            comment_text = f"Tool requirement updated: {tool_name} for action '{action.action_name}' by {current_user.username}"
            if status:
                comment_text += f". Status: {status}"
            event_context.add_comment(
                user_id=current_user.id,
                content=comment_text,
                is_human_made=True
            )
            db.session.commit()
        
        flash('Tool requirement updated successfully', 'success')
        return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
        
    except Exception as e:
        logger.error(f"Error updating tool requirement: {e}")
        import traceback
        traceback.print_exc()
        flash('Error updating tool requirement', 'error')
        return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))


@maintenance_event_bp.route('/<int:event_id>/action/<int:action_id>/tool/<int:tool_id>/delete', methods=['POST'])
@login_required
def delete_action_tool(event_id, action_id, tool_id):
    """Delete tool requirement"""
    try:
        from app.data.maintenance.base.action_tools import ActionTool
        from app.data.maintenance.base.actions import Action
        from app.buisness.maintenance.base.maintenance_action_set_struct import MaintenanceActionSetStruct
        from app.buisness.core.event_context import EventContext
        
        # Get action tool (tool_id here is ActionTool.id, not Tool.id)
        action_tool = ActionTool.query.get_or_404(tool_id)
        
        # Verify action tool belongs to this action and event
        action = Action.query.get_or_404(action_id)
        if action_tool.action_id != action_id:
            flash('Tool requirement does not belong to this action', 'error')
            return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
        
        maintenance_struct = MaintenanceActionSetStruct.from_event_id(event_id)
        if not maintenance_struct or action.maintenance_action_set_id != maintenance_struct.maintenance_action_set_id:
            flash('Action does not belong to this maintenance event', 'error')
            return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
        
        # Get tool info before deletion
        from app.data.core.supply.tool import Tool
        tool = Tool.query.get(action_tool.tool_id)
        tool_name = tool.tool_name if tool else f"Tool #{action_tool.tool_id}"
        
        # Delete action tool
        db.session.delete(action_tool)
        db.session.commit()
        
        # Generate automated comment
        if maintenance_struct.event_id:
            event_context = EventContext(maintenance_struct.event_id)
            comment_text = f"Tool requirement deleted: {tool_name} from action '{action.action_name}' by {current_user.username}"
            event_context.add_comment(
                user_id=current_user.id,
                content=comment_text,
                is_human_made=False  # Automated comment
            )
            db.session.commit()
        
        flash('Tool requirement deleted successfully', 'success')
        return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
        
    except Exception as e:
        logger.error(f"Error deleting tool requirement: {e}")
        import traceback
        traceback.print_exc()
        flash('Error deleting tool requirement', 'error')
        return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))


@maintenance_event_bp.route('/<int:event_id>/delay/create', methods=['POST'])
@login_required
def create_delay(event_id):
    """Create a delay for maintenance event"""
    try:
        from app.buisness.maintenance.base.maintenance_action_set_struct import MaintenanceActionSetStruct
        from app.buisness.maintenance.base.maintenance_context import MaintenanceContext
        from app.buisness.core.event_context import EventContext
        from app.data.maintenance.base.maintenance_delays import MaintenanceDelay
        
        # ===== FORM PARSING SECTION =====
        delay_type = request.form.get('delay_type', '').strip()
        delay_reason = request.form.get('delay_reason', '').strip()
        priority = request.form.get('priority', 'Medium').strip()
        delay_notes = request.form.get('delay_notes', '').strip()
        delay_billable_hours_str = request.form.get('delay_billable_hours', '').strip()
        delay_start_date_str = request.form.get('delay_start_date', '').strip()
        
        # ===== LIGHT VALIDATION SECTION =====
        if not delay_type or delay_type not in ['Work in Delay', 'Cancellation Requested']:
            flash('Valid delay type is required', 'error')
            return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        
        if not delay_reason:
            flash('Delay reason is required', 'error')
            return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        
        # ===== DATA TYPE CONVERSION SECTION =====
        from datetime import datetime
        
        delay_start_date = None
        if delay_start_date_str:
            try:
                delay_start_date = datetime.strptime(delay_start_date_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                flash('Invalid delay start date format', 'error')
                return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        
        delay_billable_hours = None
        if delay_billable_hours_str:
            try:
                delay_billable_hours = float(delay_billable_hours_str)
                if delay_billable_hours < 0:
                    flash('Billable hours must be non-negative', 'error')
                    return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
            except ValueError:
                pass  # Ignore invalid values
        
        # ===== BUSINESS LOGIC SECTION =====
        maintenance_struct = MaintenanceActionSetStruct.from_event_id(event_id)
        if not maintenance_struct:
            abort(404)
        
        # Check if there's already an active delay
        active_delays = [d for d in maintenance_struct.delays if d.delay_end_date is None]
        if active_delays:
            flash('An active delay already exists. Please end the current delay before creating a new one.', 'error')
            return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))
        
        # Create delay using MaintenanceContext
        maintenance_context = MaintenanceContext(maintenance_struct)
        delay = maintenance_context.add_delay(
            delay_type=delay_type,
            delay_reason=delay_reason,
            delay_start_date=delay_start_date,
            delay_notes=delay_notes,
            delay_billable_hours=delay_billable_hours,
            priority=priority,
            user_id=current_user.id
        )
        
        # Generate automated comment
        if maintenance_struct.event_id:
            event_context = EventContext(maintenance_struct.event_id)
            comment_text = f"Delay created: {delay_type} by {current_user.username}. Reason: {delay_reason}"
            event_context.add_comment(
                user_id=current_user.id,
                content=comment_text,
                is_human_made=False  # Automated comment
            )
            db.session.commit()
        
        flash('Delay created successfully', 'success')
        return redirect(url_for('maintenance_event.view_maintenance_event', event_id=event_id))
        
    except Exception as e:
        logger.error(f"Error creating delay: {e}")
        flash('Error creating delay', 'error')
        return redirect(url_for('maintenance_event.work_maintenance_event', event_id=event_id))


@maintenance_event_bp.route('/<int:event_id>/delay/<int:delay_id>/end', methods=['POST'])
@login_required
def end_delay(event_id, delay_id):
    """End an active delay"""
    try:
        from app.data.maintenance.base.maintenance_delays import MaintenanceDelay
        from app.buisness.maintenance.base.maintenance_action_set_struct import MaintenanceActionSetStruct
        from app.buisness.maintenance.base.maintenance_context import MaintenanceContext
        from app.buisness.core.event_context import EventContext
        from datetime import datetime
        
        delay = MaintenanceDelay.query.get_or_404(delay_id)
        
        if delay.delay_end_date:
            flash('Delay is already ended', 'warning')
            return redirect(url_for('maintenance_event.view_maintenance_event', event_id=event_id))
        
        # Get form data
        delay_start_date_str = request.form.get('delay_start_date')
        delay_end_date_str = request.form.get('delay_end_date')
        comment = request.form.get('comment', '').strip()
        
        # Parse dates
        delay_start_date = None
        if delay_start_date_str:
            try:
                delay_start_date = datetime.strptime(delay_start_date_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                flash('Invalid delay start date format', 'error')
                return redirect(url_for('maintenance_event.view_maintenance_event', event_id=event_id))
        
        delay_end_date = None
        if delay_end_date_str:
            try:
                delay_end_date = datetime.strptime(delay_end_date_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                flash('Invalid delay end date format', 'error')
                return redirect(url_for('maintenance_event.view_maintenance_event', event_id=event_id))
        
        # Get maintenance struct and use context manager to end delay
        maintenance_struct = MaintenanceActionSetStruct.from_event_id(event_id)
        if not maintenance_struct:
            abort(404)
        
        # Use context manager to end delay (will sync Event.status)
        maintenance_context = MaintenanceContext(maintenance_struct)
        maintenance_context.end_delay(
            delay_id=delay_id, 
            user_id=current_user.id,
            delay_start_date=delay_start_date,
            delay_end_date=delay_end_date
        )
        
        # Generate comment - use user's comment if provided, otherwise use automated one
        if maintenance_struct.event_id:
            event_context = EventContext(maintenance_struct.event_id)
            if comment:
                comment_text = f"Delay ended by {current_user.username}. {comment}"
                event_context.add_comment(
                    user_id=current_user.id,
                    content=comment_text,
                    is_human_made=True
                )
            else:
                comment_text = f"Delay ended by {current_user.username}. Maintenance work resumed."
                event_context.add_comment(
                    user_id=current_user.id,
                    content=comment_text,
                    is_human_made=False  # Automated comment
                )
            db.session.commit()
        
        flash('Delay ended successfully. Work can now continue.', 'success')
        return redirect(url_for('maintenance_event.view_maintenance_event', event_id=event_id))
        
    except Exception as e:
        logger.error(f"Error ending delay: {e}")
        flash('Error ending delay', 'error')
        return redirect(url_for('maintenance_event.view_maintenance_event', event_id=event_id))


@maintenance_event_bp.route('/<int:event_id>/delay/<int:delay_id>/update', methods=['POST'])
@login_required
def update_delay(event_id, delay_id):
    """Update delay details"""
    try:
        from app.data.maintenance.base.maintenance_delays import MaintenanceDelay
        from app.buisness.maintenance.base.maintenance_action_set_struct import MaintenanceActionSetStruct
        from app.buisness.maintenance.base.maintenance_context import MaintenanceContext
        from app.buisness.core.event_context import EventContext
        
        # ===== FORM PARSING SECTION =====
        delay_type = request.form.get('delay_type', '').strip()
        delay_reason = request.form.get('delay_reason', '').strip()
        delay_start_date_str = request.form.get('delay_start_date', '').strip()
        delay_end_date_str = request.form.get('delay_end_date', '').strip()
        delay_billable_hours_str = request.form.get('delay_billable_hours', '').strip()
        delay_notes = request.form.get('delay_notes', '').strip()
        priority = request.form.get('priority', '').strip()
        
        # ===== LIGHT VALIDATION SECTION =====
        if delay_type and delay_type not in ['Work in Delay', 'Cancellation Requested']:
            flash('Invalid delay type', 'error')
            return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
        
        if delay_reason and not delay_reason:
            flash('Delay reason cannot be empty', 'error')
            return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
        
        # ===== DATA TYPE CONVERSION SECTION =====
        delay_start_date = None
        if delay_start_date_str:
            try:
                delay_start_date = datetime.strptime(delay_start_date_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                flash('Invalid delay start date format', 'error')
                return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
        
        delay_end_date = None
        if delay_end_date_str:
            try:
                delay_end_date = datetime.strptime(delay_end_date_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                flash('Invalid delay end date format', 'error')
                return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
        
        delay_billable_hours = None
        if delay_billable_hours_str:
            try:
                delay_billable_hours = float(delay_billable_hours_str)
                if delay_billable_hours < 0:
                    flash('Billable hours must be non-negative', 'error')
                    return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
            except ValueError:
                pass  # Ignore invalid values
        
        if priority and priority not in ['Low', 'Medium', 'High', 'Critical']:
            priority = None  # Use existing value if invalid
        
        # Convert empty strings to None
        delay_type = delay_type if delay_type else None
        delay_reason = delay_reason if delay_reason else None
        delay_notes = delay_notes if delay_notes else None
        priority = priority if priority else None
        
        # ===== BUSINESS LOGIC SECTION =====
        maintenance_struct = MaintenanceActionSetStruct.from_event_id(event_id)
        if not maintenance_struct:
            flash('Maintenance event not found', 'error')
            return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
        
        maintenance_context = MaintenanceContext(maintenance_struct)
        
        # Build update dict with only non-None values
        update_kwargs = {}
        if delay_type is not None:
            update_kwargs['delay_type'] = delay_type
        if delay_reason is not None:
            update_kwargs['delay_reason'] = delay_reason
        if delay_start_date is not None:
            update_kwargs['delay_start_date'] = delay_start_date
        if delay_end_date is not None:
            update_kwargs['delay_end_date'] = delay_end_date
        if delay_billable_hours is not None:
            update_kwargs['delay_billable_hours'] = delay_billable_hours
        if delay_notes is not None:
            update_kwargs['delay_notes'] = delay_notes
        if priority is not None:
            update_kwargs['priority'] = priority
        
        # Update delay
        try:
            maintenance_context.update_delay(delay_id=delay_id, **update_kwargs)
        except ValueError as e:
            flash(str(e), 'error')
            return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
        
        # Generate automated comment
        if maintenance_struct.event_id:
            event_context = EventContext(maintenance_struct.event_id)
            comment_text = f"Delay updated by {current_user.username}."
            if delay_reason:
                comment_text += f" Reason: {delay_reason}"
            event_context.add_comment(
                user_id=current_user.id,
                content=comment_text,
                is_human_made=True
            )
            db.session.commit()
        
        flash('Delay updated successfully', 'success')
        return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
        
    except Exception as e:
        logger.error(f"Error updating delay: {e}")
        import traceback
        traceback.print_exc()
        flash('Error updating delay', 'error')
        return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))


# ============================================================================
# Action Management Routes for Edit Page
# ============================================================================

@maintenance_event_bp.route('/<int:event_id>/action/create', methods=['POST'])
@login_required
def create_action(event_id):
    """Create a new action for maintenance event with position insertion"""
    try:
        from app.data.maintenance.base.actions import Action
        from app.buisness.maintenance.base.maintenance_action_set_struct import MaintenanceActionSetStruct
        from app.buisness.maintenance.base.maintenance_context import MaintenanceContext
        from app.buisness.core.event_context import EventContext
        from app.buisness.maintenance.factories.action_factory import ActionFactory
        
        # Get maintenance struct
        maintenance_struct = MaintenanceActionSetStruct.from_event_id(event_id)
        if not maintenance_struct:
            flash('Maintenance event not found', 'error')
            return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
        
        maintenance_context = MaintenanceContext(maintenance_struct)
        
        # ===== FORM PARSING SECTION =====
        action_name = request.form.get('actionName', '').strip()
        description = request.form.get('actionDescription', '').strip()
        estimated_duration_str = request.form.get('estimatedDuration', '').strip()
        expected_billable_hours_str = request.form.get('expectedBillableHours', '').strip()
        safety_notes = request.form.get('safetyNotes', '').strip()
        notes = request.form.get('notes', '').strip()
        
        # Source references
        template_action_item_id_str = request.form.get('template_action_item_id', '').strip()
        proto_action_item_id_str = request.form.get('proto_action_item_id', '').strip()
        source_action_id_str = request.form.get('source_action_id', '').strip()  # For duplicating from current actions
        
        # Insert position
        insert_position = request.form.get('insertPosition', 'end').strip()
        after_action_id_str = request.form.get('afterActionId', '').strip()
        
        # Copy options
        copy_part_demands = request.form.get('copyPartDemands', 'false').strip().lower() == 'true'
        copy_tools = request.form.get('copyTools', 'false').strip().lower() == 'true'
        
        # ===== LIGHT VALIDATION SECTION =====
        if not action_name:
            flash('Action name is required', 'error')
            return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
        
        if insert_position not in ['end', 'beginning', 'after']:
            flash('Invalid insert position', 'error')
            return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
        
        if insert_position == 'after' and not after_action_id_str:
            flash('After action ID is required when inserting after a specific action', 'error')
            return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
        
        # ===== DATA TYPE CONVERSION SECTION =====
        template_action_item_id = None
        if template_action_item_id_str:
            try:
                template_action_item_id = int(template_action_item_id_str)
            except ValueError:
                pass
        
        proto_action_item_id = None
        if proto_action_item_id_str:
            try:
                proto_action_item_id = int(proto_action_item_id_str)
            except ValueError:
                pass
        
        source_action_id = None
        if source_action_id_str:
            try:
                source_action_id = int(source_action_id_str)
            except ValueError:
                pass
        
        after_action_id = None
        if after_action_id_str:
            try:
                after_action_id = int(after_action_id_str)
            except ValueError:
                pass
        
        estimated_duration = None
        if estimated_duration_str:
            try:
                estimated_duration = float(estimated_duration_str)
            except ValueError:
                pass
        
        expected_billable_hours = None
        if expected_billable_hours_str:
            try:
                expected_billable_hours = float(expected_billable_hours_str)
            except ValueError:
                pass
        
        # ===== BUSINESS LOGIC SECTION =====
        # Calculate sequence order based on insert position
        sequence_order = maintenance_context._calculate_sequence_order(
            insert_position=insert_position,
            after_action_id=after_action_id
        )
        
        # If inserting at beginning or after, need to shift existing actions
        if insert_position in ['beginning', 'after']:
            actions = maintenance_struct.actions
            if insert_position == 'beginning':
                # Shift all actions up by 1
                for action in actions:
                    action.sequence_order += 1
                sequence_order = 1
            else:  # after
                # Shift actions after target down by 1
                target_sequence = None
                for action in actions:
                    if action.id == after_action_id:
                        target_sequence = action.sequence_order
                        break
                if target_sequence is not None:
                    for action in actions:
                        if action.sequence_order > target_sequence:
                            action.sequence_order += 1
                    sequence_order = target_sequence + 1
        
        # Create action
        # If source is template, use ActionFactory
        if template_action_item_id:
            action = ActionFactory.create_from_template_action_item(
                template_action_item_id=template_action_item_id,
                maintenance_action_set_id=maintenance_struct.maintenance_action_set_id,
                user_id=current_user.id,
                commit=False
            )
            # Update sequence order
            action.sequence_order = sequence_order
            # Only copy part demands/tools if explicitly requested
            if not copy_part_demands:
                # Delete part demands that were created
                for part_demand in list(action.part_demands):
                    db.session.delete(part_demand)
            if not copy_tools:
                # Delete tools that were created
                for tool in list(action.action_tools):
                    db.session.delete(tool)
        # If source is proto, create from proto
        elif proto_action_item_id:
            from app.data.maintenance.proto_templates.proto_actions import ProtoActionItem
            from app.data.maintenance.base.part_demands import PartDemand
            proto_action = ProtoActionItem.query.get_or_404(proto_action_item_id)
            
            action = Action(
                maintenance_action_set_id=maintenance_struct.maintenance_action_set_id,
                proto_action_item_id=proto_action_item_id,
                sequence_order=sequence_order,
                action_name=action_name or proto_action.action_name,
                description=description or proto_action.description,
                estimated_duration=estimated_duration or proto_action.estimated_duration,
                expected_billable_hours=expected_billable_hours or proto_action.expected_billable_hours,
                safety_notes=safety_notes or proto_action.safety_notes,
                notes=notes or proto_action.notes,
                status='Not Started',
                created_by_id=current_user.id,
                updated_by_id=current_user.id
            )
            db.session.add(action)
            db.session.flush()
            
            # Copy part demands and tools if requested
            if copy_part_demands:
                for proto_part_demand in proto_action.proto_part_demands:
                    part_demand = PartDemand(
                        action_id=action.id,
                        part_id=proto_part_demand.part_id,
                        quantity_required=proto_part_demand.quantity_required,
                        notes=proto_part_demand.notes,
                        expected_cost=proto_part_demand.expected_cost,
                        status='Planned',
                        priority='Medium',
                        sequence_order=proto_part_demand.sequence_order,
                        created_by_id=current_user.id,
                        updated_by_id=current_user.id
                    )
                    db.session.add(part_demand)
            
            if copy_tools:
                for proto_tool in proto_action.proto_action_tools:
                    from app.data.maintenance.base.action_tools import ActionTool
                    action_tool = ActionTool(
                        action_id=action.id,
                        tool_id=proto_tool.tool_id,
                        quantity_required=proto_tool.quantity_required,
                        notes=proto_tool.notes,
                        status='Planned',
                        priority='Medium',
                        sequence_order=proto_tool.sequence_order,
                        created_by_id=current_user.id,
                        updated_by_id=current_user.id
                    )
                    db.session.add(action_tool)
        # If duplicating from current action
        elif source_action_id:
            source_action = Action.query.get_or_404(source_action_id)
            if source_action.maintenance_action_set_id != maintenance_struct.maintenance_action_set_id:
                flash('Source action does not belong to this maintenance event', 'error')
                return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
            
            # Create duplicate action
            action = Action(
                maintenance_action_set_id=maintenance_struct.maintenance_action_set_id,
                template_action_item_id=source_action.template_action_item_id,
                proto_action_item_id=source_action.proto_action_item_id,
                sequence_order=sequence_order,
                action_name=action_name or source_action.action_name,
                description=description or source_action.description,
                estimated_duration=estimated_duration or source_action.estimated_duration,
                expected_billable_hours=expected_billable_hours or source_action.expected_billable_hours,
                safety_notes=safety_notes or source_action.safety_notes,
                notes=notes or source_action.notes,
                status='Not Started',  # Reset status
                created_by_id=current_user.id,
                updated_by_id=current_user.id
            )
            db.session.add(action)
            db.session.flush()
            
            # Copy part demands and tools if requested
            if copy_part_demands:
                for source_part_demand in source_action.part_demands:
                    part_demand = PartDemand(
                        action_id=action.id,
                        part_id=source_part_demand.part_id,
                        quantity_required=source_part_demand.quantity_required,
                        notes=source_part_demand.notes,
                        expected_cost=source_part_demand.expected_cost,
                        status='Planned',  # Reset status
                        priority=source_part_demand.priority,
                        sequence_order=source_part_demand.sequence_order,
                        created_by_id=current_user.id,
                        updated_by_id=current_user.id
                    )
                    db.session.add(part_demand)
            
            if copy_tools:
                for source_tool in source_action.action_tools:
                    action_tool = ActionTool(
                        action_id=action.id,
                        tool_id=source_tool.tool_id,
                        quantity_required=source_tool.quantity_required,
                        notes=source_tool.notes,
                        status='Planned',  # Reset status
                        priority=source_tool.priority,
                        sequence_order=source_tool.sequence_order,
                        created_by_id=current_user.id,
                        updated_by_id=current_user.id
                    )
                    db.session.add(action_tool)
        # Blank action
        else:
            action = Action(
                maintenance_action_set_id=maintenance_struct.maintenance_action_set_id,
                sequence_order=sequence_order,
                action_name=action_name,
                description=description if description else None,
                estimated_duration=estimated_duration,
                expected_billable_hours=expected_billable_hours,
                safety_notes=safety_notes if safety_notes else None,
                notes=notes if notes else None,
                status='Not Started',
                created_by_id=current_user.id,
                updated_by_id=current_user.id
            )
            db.session.add(action)
        
        db.session.commit()
        
        # Generate automated comment
        if maintenance_struct.event_id:
            event_context = EventContext(maintenance_struct.event_id)
            comment_text = f"Action created: '{action.action_name}' by {current_user.username}"
            event_context.add_comment(
                user_id=current_user.id,
                content=comment_text,
                is_human_made=False  # Automated comment
            )
            db.session.commit()
        
        flash('Action created successfully', 'success')
        return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
        
    except Exception as e:
        logger.error(f"Error creating action: {e}")
        import traceback
        traceback.print_exc()
        flash('Error creating action', 'error')
        return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))


@maintenance_event_bp.route('/<int:event_id>/action/<int:action_id>/delete', methods=['POST'])
@login_required
def delete_action(event_id, action_id):
    """Delete an action and renumber remaining actions"""
    try:
        from app.data.maintenance.base.actions import Action
        from app.buisness.maintenance.base.maintenance_action_set_struct import MaintenanceActionSetStruct
        from app.buisness.maintenance.base.maintenance_context import MaintenanceContext
        from app.buisness.core.event_context import EventContext
        
        # Get action
        action = Action.query.get_or_404(action_id)
        
        # Verify action belongs to this event
        maintenance_struct = MaintenanceActionSetStruct.from_event_id(event_id)
        if not maintenance_struct or action.maintenance_action_set_id != maintenance_struct.maintenance_action_set_id:
            flash('Action does not belong to this maintenance event', 'error')
            return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
        
        # Get action name before deletion
        action_name = action.action_name
        
        # Delete action (cascade will delete part demands and tools)
        db.session.delete(action)
        db.session.commit()
        
        # Renumber remaining actions atomically
        maintenance_context = MaintenanceContext(maintenance_struct)
        maintenance_context._renumber_actions_atomic()
        
        # Generate automated comment
        if maintenance_struct.event_id:
            event_context = EventContext(maintenance_struct.event_id)
            comment_text = f"Action deleted: '{action_name}' by {current_user.username}"
            event_context.add_comment(
                user_id=current_user.id,
                content=comment_text,
                is_human_made=False  # Automated comment
            )
            db.session.commit()
        
        flash('Action deleted successfully', 'success')
        return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
        
    except Exception as e:
        logger.error(f"Error deleting action: {e}")
        import traceback
        traceback.print_exc()
        flash('Error deleting action', 'error')
        return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))


@maintenance_event_bp.route('/<int:event_id>/action/<int:action_id>/move-up', methods=['POST'])
@login_required
def move_action_up(event_id, action_id):
    """Move action up in sequence (decrease sequence_order)"""
    try:
        from app.data.maintenance.base.actions import Action
        from app.buisness.maintenance.base.maintenance_action_set_struct import MaintenanceActionSetStruct
        from app.buisness.maintenance.base.action_context import ActionContext
        
        # Get action
        action = Action.query.get_or_404(action_id)
        
        # Verify action belongs to this event
        maintenance_struct = MaintenanceActionSetStruct.from_event_id(event_id)
        if not maintenance_struct or action.maintenance_action_set_id != maintenance_struct.maintenance_action_set_id:
            flash('Action does not belong to this maintenance event', 'error')
            return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
        
        # Get current sequence order
        current_order = action.sequence_order
        if current_order <= 1:
            flash('Action is already at the top', 'warning')
            return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
        
        # Move up (decrease sequence_order)
        new_order = current_order - 1
        action_context = ActionContext(action)
        action_context.reorder_action(new_order)
        
        flash('Action moved up successfully', 'success')
        return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
        
    except Exception as e:
        logger.error(f"Error moving action up: {e}")
        flash('Error moving action up', 'error')
        return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))


@maintenance_event_bp.route('/<int:event_id>/action/<int:action_id>/move-down', methods=['POST'])
@login_required
def move_action_down(event_id, action_id):
    """Move action down in sequence (increase sequence_order)"""
    try:
        from app.data.maintenance.base.actions import Action
        from app.buisness.maintenance.base.maintenance_action_set_struct import MaintenanceActionSetStruct
        from app.buisness.maintenance.base.action_context import ActionContext
        
        # Get action
        action = Action.query.get_or_404(action_id)
        
        # Verify action belongs to this event
        maintenance_struct = MaintenanceActionSetStruct.from_event_id(event_id)
        if not maintenance_struct or action.maintenance_action_set_id != maintenance_struct.maintenance_action_set_id:
            flash('Action does not belong to this maintenance event', 'error')
            return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
        
        # Get current sequence order and max order
        current_order = action.sequence_order
        max_order = len(maintenance_struct.actions)
        
        if current_order >= max_order:
            flash('Action is already at the bottom', 'warning')
            return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
        
        # Move down (increase sequence_order)
        new_order = current_order + 1
        action_context = ActionContext(action)
        action_context.reorder_action(new_order)
        
        flash('Action moved down successfully', 'success')
        return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
        
    except Exception as e:
        logger.error(f"Error moving action down: {e}")
        flash('Error moving action down', 'error')
        return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))


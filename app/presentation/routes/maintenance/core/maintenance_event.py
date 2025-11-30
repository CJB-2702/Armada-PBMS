"""
Maintenance work and edit routes for maintenance events
"""
import traceback
from datetime import datetime

from flask import Blueprint, render_template, abort, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user

from app import db
from app.logger import get_logger
from app.buisness.core.event_context import EventContext
from app.buisness.maintenance.base.action_struct import ActionStruct
from app.buisness.maintenance.base.maintenance_action_set_struct import MaintenanceActionSetStruct
from app.buisness.maintenance.base.maintenance_context import MaintenanceContext
from app.buisness.maintenance.factories.action_factory import ActionFactory
from app.data.core.asset_info.asset import Asset
from app.data.core.event_info.event import Event
from app.data.core.supply.part import Part
from app.data.core.supply.tool import Tool
from app.data.core.user_info.user import User
from app.data.maintenance.base.actions import Action
from app.data.maintenance.base.action_tools import ActionTool
from app.data.maintenance.base.maintenance_delays import MaintenanceDelay
from app.data.maintenance.base.maintenance_plans import MaintenancePlan
from app.data.maintenance.base.part_demands import PartDemand
from app.data.maintenance.proto_templates.proto_actions import ProtoActionItem
from app.services.maintenance.assign_monitor_service import AssignMonitorService

logger = get_logger("asset_management.routes.maintenance")

# Create blueprint for maintenance event work/edit routes
maintenance_event_bp = Blueprint('maintenance_event', __name__, url_prefix='/maintenance/maintenance-event')


@maintenance_event_bp.route('/<int:event_id>')
@maintenance_event_bp.route('/<int:event_id>/')
@maintenance_event_bp.route('/<int:event_id>/view')
@login_required
def view_maintenance_event(event_id):
    """View detailed information about a maintenance event"""
    logger.info(f"Viewing maintenance event for event_id={event_id}")
    
    try:
        # Get the event
        event = Event.query.get(event_id)
        if not event:
            logger.warning(f"Event {event_id} not found")
            abort(404)
        
        # Get the maintenance action set by event_id (ONE-TO-ONE relationship)
        maintenance_context = MaintenanceContext.from_event(event_id)
        if not maintenance_context:
            logger.warning(f"No maintenance action set found for event_id={event_id}")
            abort(404)
        maintenance_struct = maintenance_context.struct
        if not maintenance_struct:
            logger.warning(f"No maintenance action set found for event_id={event_id}")
            abort(404)
        
        # Get actions with their structs for convenient access
        action_structs = [ActionStruct(action) for action in maintenance_struct.actions]
        
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


@maintenance_event_bp.route('/<int:event_id>/work')
@login_required
def work_maintenance_event(event_id):
    """Work on a maintenance event (perform maintenance)"""
    logger.info(f"Working on maintenance event for event_id={event_id}")
    
    try:
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
        maintenance_context = MaintenanceContext.from_event(event_id)
        
        # Get asset if available
        asset = maintenance_struct.asset if hasattr(maintenance_struct, 'asset') else None
        
        # Get delays for display
        delays = maintenance_struct.delays if hasattr(maintenance_struct, 'delays') else []
        active_delays = [d for d in delays if d.delay_end_date is None]
        
        # Get parts for part demand dropdown
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



@maintenance_event_bp.route('/<int:event_id>/action/create', methods=['POST'])
@login_required
def create_action(event_id):
    """Create a new action for maintenance event with position insertion"""
    try:
        # Get maintenance struct
        maintenance_struct = MaintenanceActionSetStruct.from_event_id(event_id)
        if not maintenance_struct:
            flash('Maintenance event not found', 'error')
            return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))
        
        maintenance_context = MaintenanceContext.from_event(event_id)
        
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
        traceback.print_exc()
        flash('Error creating action', 'error')
        return redirect(url_for('maintenance_event.edit_maintenance_event', event_id=event_id))

@maintenance_event_bp.route('/<int:event_id>/assign', methods=['GET', 'POST'])
@login_required
def assign_event(event_id):
    """
    Assign or reassign maintenance event to technician.
    GET: Show assignment form
    POST: Process assignment (refreshes page and opens view in new tab)
    """
    logger.info(f"Assigning maintenance event for event_id={event_id}")
    
    try:
        # Get the event
        event = Event.query.get(event_id)
        if not event:
            logger.warning(f"Event {event_id} not found")
            abort(404)
        
        # Get the maintenance action set by event_id (ONE-TO-ONE relationship)
        maintenance_context = MaintenanceContext.from_event(event_id)
        maintenance_struct = maintenance_context.struct
        
        if not maintenance_struct:
            logger.warning(f"No maintenance action set found for event_id={event_id}")
            abort(404)
        
        if request.method == 'GET':
            # Get technicians for dropdown
            technicians, _ = AssignMonitorService.get_available_technicians()
            
            # Get assignment history (from comments)
            assignment_history = []
            if maintenance_context.event_context:
                comments = maintenance_context.event_context.comments
                # Filter comments that mention assignment
                for comment in comments:
                    if 'Assigned to' in comment.content or 'assigned' in comment.content.lower():
                        assignment_history.append({
                            'created_at': comment.created_at.isoformat() if comment.created_at else None,
                            'created_by': comment.created_by.username if comment.created_by else None,
                            'content': comment.content,
                        })
            
            return render_template(
                'maintenance/maintenance_event/assign.html',
                maintenance=maintenance_struct,
                maintenance_context=maintenance_context,
                event=event,
                technicians=technicians,
                assignment_history=assignment_history,
            )
        
        # POST: Process assignment
        try:
            assigned_user_id = request.form.get('assigned_user_id', type=int)
            notes = request.form.get('notes', '').strip() or None
            
            # Get optional fields
            planned_start_str = request.form.get('planned_start_datetime')
            planned_start_datetime = None
            if planned_start_str:
                try:
                    planned_start_datetime = datetime.fromisoformat(planned_start_str.replace('Z', '+00:00'))
                except (ValueError, AttributeError):
                    pass
            
            priority = request.form.get('priority')
            
            # Validate required fields
            if not assigned_user_id:
                flash('Technician is required', 'error')
                return redirect(url_for('maintenance_event.assign_event', event_id=event_id))
            
            # Assign event
            AssignMonitorService.assign_event(
                event_id=event_id,
                assigned_user_id=assigned_user_id,
                assigned_by_id=current_user.id,
                planned_start_datetime=planned_start_datetime,
                priority=priority,
                notes=notes
            )
            
            flash('Event assigned successfully', 'success')
            
            # Redirect back to assign page with success parameter
            # JavaScript in template will open view page in new tab
            return redirect(url_for('maintenance_event.assign_event', event_id=event_id, assigned='true'))
            
        except ValueError as e:
            logger.warning(f"Validation error assigning event: {e}")
            flash(str(e), 'error')
            return redirect(url_for('maintenance_event.assign_event', event_id=event_id))
        except Exception as e:
            logger.error(f"Error assigning event: {e}")
            flash('Error assigning event. Please try again.', 'error')
            return redirect(url_for('maintenance_event.assign_event', event_id=event_id))
            
    except ImportError as e:
        logger.error(f"Could not import maintenance modules: {e}")
        abort(500)
    except Exception as e:
        logger.error(f"Error in assign event {event_id}: {e}")
        abort(500)


@maintenance_event_bp.route('/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_maintenance_event(event_id):
    """Edit a maintenance event"""
    logger.info(f"Editing maintenance event for event_id={event_id}")
    
    try:
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
            maintenance_context = MaintenanceContext.from_event(event_id)
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
        parts = Part.query.filter_by(status='Active').order_by(Part.part_name).all()
        tools = Tool.query.order_by(Tool.tool_name).all()
        users = User.query.order_by(User.username).all()
        
        # Get maintenance context for summaries
        maintenance_context = MaintenanceContext.from_event(event_id)
        
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



@maintenance_event_bp.route('/<int:event_id>/update-datetime', methods=['POST'])
@login_required
def update_maintenance_datetime(event_id):
    """Update maintenance start/end dates"""
    try:
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
        
        maintenance_context = MaintenanceContext.from_event(event_id)
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
        maintenance_context = MaintenanceContext.from_event(event_id)
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


@maintenance_event_bp.route('/<int:event_id>/delay/create', methods=['POST'])
@login_required
def create_delay(event_id):
    """Create a delay for maintenance event"""
    try:
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




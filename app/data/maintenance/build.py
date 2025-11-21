"""
Maintenance models build module for the Asset Management System
Handles building and initializing maintenance models and data
"""

from app import db
from app.logger import get_logger
from datetime import datetime

logger = get_logger("asset_management.models.maintenance")

def build_models():
    """
    Build maintenance models - this is a no-op since models are imported
    when the app is created, which registers them with SQLAlchemy
    """
    # Import virtual base classes
    import app.data.maintenance.virtual_action_item
    import app.data.maintenance.virtual_action_set
    import app.data.maintenance.virtual_part_demand
    import app.data.maintenance.virtual_action_tool
    
    # Import base models
    import app.data.maintenance.base.actions
    import app.data.maintenance.base.maintenance_action_sets
    import app.data.maintenance.base.maintenance_plans
    import app.data.maintenance.base.maintenance_delays
    import app.data.maintenance.base.part_demands
    import app.data.maintenance.base.action_tools
    
    # Import template models
    import app.data.maintenance.templates.template_action_sets
    import app.data.maintenance.templates.template_actions
    import app.data.maintenance.templates.template_part_demands
    import app.data.maintenance.templates.template_action_tools
    import app.data.maintenance.templates.template_action_set_attachments
    import app.data.maintenance.templates.template_action_attachments
    
    # Import proto models
    import app.data.maintenance.proto_templates.proto_actions
    import app.data.maintenance.proto_templates.proto_part_demands
    import app.data.maintenance.proto_templates.proto_action_tools
    import app.data.maintenance.proto_templates.proto_action_attachments
    
    # Note: Factories are business logic and are located in app/buisness/maintenance/factories/
    # They are not needed for model building
    
    # Note: Utilities are business logic and are located in app/buisness/maintenance/utils/
    # They are not needed for model building
    
    # Create all tables to ensure they exist
    db.create_all()
    
    logger.info("Maintenance models build completed")


def init_data(build_data):
    """
    Initialize maintenance data from build_data using new structured format
    
    Args:
        build_data (dict): Build data from JSON file with new structure
    """
    # Get system user for audit fields
    from app.data.core.user_info.user import User
    system_user = User.query.filter_by(username='system').first()
    if not system_user:
        logger.warning("System user not found, creating maintenance data without audit trail")
        system_user_id = None
    else:
        system_user_id = system_user.id
    
    logger.info("Initializing maintenance data...")
    
    # Initialize maintenance data from Maintenance section
    if 'Maintenance' in build_data:
        _init_template_action_sets(build_data['Maintenance'], system_user_id)
        _init_proto_action_items(build_data['Maintenance'], system_user_id)
        _init_template_action_items(build_data['Maintenance'], system_user_id)
        _init_proto_part_demands(build_data['Maintenance'], system_user_id)
        _init_template_part_demands(build_data['Maintenance'], system_user_id)
        _init_template_action_tools(build_data['Maintenance'], system_user_id)
        _init_maintenance_plans(build_data['Maintenance'], system_user_id)
        _init_maintenance_action_sets(build_data['Maintenance'], system_user_id)
    
    logger.info("Maintenance data initialization completed")


def _init_template_action_sets(maintenance_data, system_user_id):
    """Initialize template action sets from build data"""
    from app.data.maintenance.templates.template_action_sets import TemplateActionSet
    
    # Check for both 'template_actions' and 'template_action_sets' for backward compatibility
    templates_data = maintenance_data.get('template_action_sets') or maintenance_data.get('template_actions')
    
    if not templates_data:
        logger.info("No template action sets found in maintenance data")
        return
    
    logger.info("Creating template action sets...")
    for template_data in templates_data:
        try:
            template = TemplateActionSet.find_or_create_from_dict(
                template_data,
                user_id=system_user_id,
                lookup_fields=['task_name', 'revision']
            )
            if template[1]:  # If newly created
                logger.info(f"Created template action set: {template_data.get('task_name')}")
            else:
                logger.info(f"Template action set already exists: {template_data.get('task_name')}")
        except Exception as e:
            logger.error(f"Error creating template action set {template_data.get('task_name', 'Unknown')}: {e}")


def _init_template_action_items(maintenance_data, system_user_id):
    """Initialize template action items from build data"""
    from app.data.maintenance.templates.template_actions import TemplateActionItem
    from app.data.maintenance.templates.template_action_sets import TemplateActionSet
    
    # Check for both 'template_action_items' and 'proto_action_items' for backward compatibility
    # Note: In the JSON, proto_action_items are actually TemplateActionItem objects
    items_data = maintenance_data.get('template_action_items') or maintenance_data.get('proto_action_items')
    
    if not items_data:
        logger.info("No template action items found in maintenance data")
        return
    
    logger.info("Creating template action items...")
    for item_data in items_data:
        try:
            # Handle template_action_set_task_name reference
            if 'template_action_set_task_name' in item_data:
                task_name = item_data.pop('template_action_set_task_name')
                template_action_set = TemplateActionSet.query.filter_by(task_name=task_name).first()
                if template_action_set:
                    item_data['template_action_set_id'] = template_action_set.id
                else:
                    logger.warning(f"Template action set '{task_name}' not found for action item {item_data.get('action_name', 'Unknown')}")
                    continue
            
            # Handle proto_action_item reference
            if 'proto_action_item_action_name' in item_data:
                action_name = item_data.pop('proto_action_item_action_name')
                from app.data.maintenance.proto_templates.proto_actions import ProtoActionItem
                proto_action_item = ProtoActionItem.query.filter_by(action_name=action_name).first()
                if proto_action_item:
                    item_data['proto_action_item_id'] = proto_action_item.id
                else:
                    logger.warning(f"Proto action item '{action_name}' not found, continuing without proto reference")
                    # Continue without proto reference - it's optional
            
            item = TemplateActionItem.find_or_create_from_dict(
                item_data,
                user_id=system_user_id,
                lookup_fields=['action_name', 'template_action_set_id', 'sequence_order']
            )
            if item[1]:  # If newly created
                logger.info(f"Created template action item: {item_data.get('action_name')}")
            else:
                logger.info(f"Template action item already exists: {item_data.get('action_name')}")
        except Exception as e:
            logger.error(f"Error creating template action item {item_data.get('action_name', 'Unknown')}: {e}")


def _init_proto_action_items(maintenance_data, system_user_id):
    """Initialize proto action items from build data"""
    from app.data.maintenance.proto_templates.proto_actions import ProtoActionItem
    
    if 'proto_action_items' not in maintenance_data:
        logger.info("No proto action items found in maintenance data")
        return
    
    logger.info("Creating proto action items...")
    for item_data in maintenance_data['proto_action_items']:
        try:
            # Make a copy to avoid modifying the original
            item_data = item_data.copy()
            
            # Remove template-specific fields that shouldn't be in proto actions
            item_data.pop('template_action_set_task_name', None)
            item_data.pop('sequence_order', None)
            
            item = ProtoActionItem.find_or_create_from_dict(
                item_data,
                user_id=system_user_id,
                lookup_fields=['action_name', 'revision']
            )
            if item[1]:  # If newly created
                logger.info(f"Created proto action item: {item_data.get('action_name')}")
            else:
                logger.info(f"Proto action item already exists: {item_data.get('action_name')}")
        except Exception as e:
            logger.error(f"Error creating proto action item {item_data.get('action_name', 'Unknown')}: {e}")


def _init_proto_part_demands(maintenance_data, system_user_id):
    """Initialize proto part demands from build data"""
    from app.data.maintenance.proto_templates.proto_part_demands import ProtoPartDemand
    from app.data.maintenance.proto_templates.proto_actions import ProtoActionItem
    from app.data.supply_items.part import Part
    
    if 'proto_part_demands' not in maintenance_data:
        logger.info("No proto part demands found in maintenance data")
        return
    
    logger.info("Creating proto part demands...")
    for demand_data in maintenance_data['proto_part_demands']:
        try:
            # Make a copy to avoid modifying the original
            demand_data = demand_data.copy()
            
            action_name = None
            part_number = None
            
            # Handle proto_action_item_action_name reference
            if 'proto_action_item_action_name' in demand_data:
                action_name = demand_data.pop('proto_action_item_action_name')
                proto_action_item = ProtoActionItem.query.filter_by(action_name=action_name).first()
                if proto_action_item:
                    demand_data['proto_action_item_id'] = proto_action_item.id
                else:
                    logger.warning(f"Proto action item '{action_name}' not found for proto part demand")
                    continue
            
            # Handle part_number reference
            if 'part_number' in demand_data:
                part_number = demand_data.pop('part_number')
                part = Part.query.filter_by(part_number=part_number).first()
                if part:
                    demand_data['part_id'] = part.id
                else:
                    logger.warning(f"Part '{part_number}' not found for proto part demand")
                    continue
            
            demand = ProtoPartDemand.find_or_create_from_dict(
                demand_data,
                user_id=system_user_id,
                lookup_fields=['proto_action_item_id', 'part_id', 'sequence_order']
            )
            if demand[1]:  # If newly created
                logger.info(f"Created proto part demand: {part_number or 'unknown'} for {action_name or 'unknown'}")
            else:
                logger.info(f"Proto part demand already exists: {part_number or 'unknown'} for {action_name or 'unknown'}")
        except Exception as e:
            logger.error(f"Error creating proto part demand: {e}")


def _init_template_part_demands(maintenance_data, system_user_id):
    """Initialize template part demands from build data"""
    from app.data.maintenance.templates.template_part_demands import TemplatePartDemand
    from app.data.maintenance.templates.template_actions import TemplateActionItem
    from app.data.supply_items.part import Part
    
    if 'template_part_demands' not in maintenance_data:
        logger.info("No template part demands found in maintenance data")
        return
    
    logger.info("Creating template part demands...")
    for demand_data in maintenance_data['template_part_demands']:
        try:
            # Handle template_action_item_action_name reference
            if 'template_action_item_action_name' in demand_data:
                action_name = demand_data.pop('template_action_item_action_name')
                template_action_item = TemplateActionItem.query.filter_by(action_name=action_name).first()
                if template_action_item:
                    demand_data['template_action_item_id'] = template_action_item.id
                else:
                    logger.warning(f"Template action item '{action_name}' not found for part demand")
                    continue
            
            # Handle part_number reference
            if 'part_number' in demand_data:
                part_number = demand_data.pop('part_number')
                part = Part.query.filter_by(part_number=part_number).first()
                if part:
                    demand_data['part_id'] = part.id
                else:
                    logger.warning(f"Part '{part_number}' not found for template part demand")
                    continue
            
            demand = TemplatePartDemand.find_or_create_from_dict(
                demand_data,
                user_id=system_user_id,
                lookup_fields=['template_action_item_id', 'part_id']
            )
            if demand[1]:  # If newly created
                logger.info(f"Created template part demand: {part_number} for {action_name}")
            else:
                logger.info(f"Template part demand already exists: {part_number} for {action_name}")
        except Exception as e:
            logger.error(f"Error creating template part demand: {e}")


def _init_template_action_tools(maintenance_data, system_user_id):
    """Initialize template action tools from build data"""
    from app.data.maintenance.templates.template_action_tools import TemplateActionTool
    from app.data.maintenance.templates.template_actions import TemplateActionItem
    from app.data.supply_items.tool import Tool
    
    if 'template_action_tools' not in maintenance_data:
        logger.info("No template action tools found in maintenance data")
        return
    
    logger.info("Creating template action tools...")
    for tool_data in maintenance_data['template_action_tools']:
        try:
            # Handle template_action_item_action_name reference
            if 'template_action_item_action_name' in tool_data:
                action_name = tool_data.pop('template_action_item_action_name')
                template_action_item = TemplateActionItem.query.filter_by(action_name=action_name).first()
                if template_action_item:
                    tool_data['template_action_item_id'] = template_action_item.id
                else:
                    logger.warning(f"Template action item '{action_name}' not found for tool")
                    continue
            
            # Handle tool_name reference
            if 'tool_name' in tool_data:
                tool_name = tool_data.pop('tool_name')
                tool = Tool.query.filter_by(tool_name=tool_name).first()
                if tool:
                    tool_data['tool_id'] = tool.id
                else:
                    logger.warning(f"Tool '{tool_name}' not found for template action tool")
                    continue
            
            template_tool = TemplateActionTool.find_or_create_from_dict(
                tool_data,
                user_id=system_user_id,
                lookup_fields=['template_action_item_id', 'tool_id']
            )
            if template_tool[1]:  # If newly created
                logger.info(f"Created template action tool: {tool_name} for {action_name}")
            else:
                logger.info(f"Template action tool already exists: {tool_name} for {action_name}")
        except Exception as e:
            logger.error(f"Error creating template action tool: {e}")


def _init_maintenance_plans(maintenance_data, system_user_id):
    """Initialize maintenance plans from build data"""
    from app.data.maintenance.base.maintenance_plans import MaintenancePlan
    from app.data.core.asset_info.asset_type import AssetType
    from app.data.maintenance.templates.template_action_sets import TemplateActionSet
    
    if 'maintenance_plans' not in maintenance_data:
        logger.info("No maintenance plans found in maintenance data")
        return
    
    logger.info("Creating maintenance plans...")
    for plan_data in maintenance_data['maintenance_plans']:
        try:
            # Handle asset_type_name reference
            if 'asset_type_name' in plan_data:
                asset_type_name = plan_data.pop('asset_type_name')
                asset_type = AssetType.query.filter_by(name=asset_type_name).first()
                if asset_type:
                    plan_data['asset_type_id'] = asset_type.id
                else:
                    logger.warning(f"Asset type '{asset_type_name}' not found for maintenance plan {plan_data.get('name', 'Unknown')}")
                    continue
            
            # Handle template_action_set_task_name reference
            if 'template_action_set_task_name' in plan_data:
                task_name = plan_data.pop('template_action_set_task_name')
                template_action_set = TemplateActionSet.query.filter_by(task_name=task_name).first()
                if template_action_set:
                    plan_data['template_action_set_id'] = template_action_set.id
                else:
                    logger.warning(f"Template action set '{task_name}' not found for maintenance plan {plan_data.get('name', 'Unknown')}")
                    continue
            
            plan = MaintenancePlan.find_or_create_from_dict(
                plan_data,
                user_id=system_user_id,
                lookup_fields=['name']
            )
            if plan[1]:  # If newly created
                logger.info(f"Created maintenance plan: {plan_data.get('name')}")
            else:
                logger.info(f"Maintenance plan already exists: {plan_data.get('name')}")
        except Exception as e:
            logger.error(f"Error creating maintenance plan {plan_data.get('name', 'Unknown')}: {e}")


def _init_maintenance_action_sets(maintenance_data, system_user_id):
    """Initialize maintenance action sets from build data"""
    from app.data.maintenance.base.maintenance_action_sets import MaintenanceActionSet
    from app.data.core.asset_info.asset import Asset
    from app.data.maintenance.base.maintenance_plans import MaintenancePlan
    
    # Check for both 'maintenance_events' and 'maintenance_action_sets' for backward compatibility
    events_data = maintenance_data.get('maintenance_events') or maintenance_data.get('maintenance_action_sets')
    
    if not events_data:
        logger.info("No maintenance events found in maintenance data")
        return
    
    logger.info("Creating maintenance action sets...")
    for event_data in events_data:
        try:
            # Make a copy to avoid modifying the original
            event_data = event_data.copy()
            
            # Handle asset_name reference
            asset_name = event_data.pop('asset_name', None)
            if asset_name:
                asset = Asset.query.filter_by(name=asset_name).first()
                if asset:
                    event_data['asset_id'] = asset.id
                else:
                    logger.warning(f"Asset '{asset_name}' not found for maintenance action set {event_data.get('task_name', 'Unknown')}")
                    continue
            
            # Handle maintenance_plan_name reference
            plan_name = event_data.pop('maintenance_plan_name', None)
            if plan_name:
                maintenance_plan = MaintenancePlan.query.filter_by(name=plan_name).first()
                if maintenance_plan:
                    event_data['maintenance_plan_id'] = maintenance_plan.id
                    # Also set template_action_set_id from the plan
                    if maintenance_plan.template_action_set_id:
                        event_data['template_action_set_id'] = maintenance_plan.template_action_set_id
                else:
                    logger.warning(f"Maintenance plan '{plan_name}' not found for maintenance action set {event_data.get('task_name', 'Unknown')}")
                    continue
            
            # Handle planned_start_datetime string conversion (renamed from scheduled_date)
            if 'planned_start_datetime' in event_data and isinstance(event_data.get('planned_start_datetime'), str):
                try:
                    event_data['planned_start_datetime'] = datetime.strptime(event_data['planned_start_datetime'], '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    try:
                        event_data['planned_start_datetime'] = datetime.strptime(event_data['planned_start_datetime'], '%Y-%m-%d')
                    except ValueError:
                        logger.warning(f"Invalid date format for maintenance action set {event_data.get('task_name', 'Unknown')}")
                        event_data.pop('planned_start_datetime', None)
            
            # Also handle legacy scheduled_date field for backward compatibility
            if 'scheduled_date' in event_data and 'planned_start_datetime' not in event_data:
                if isinstance(event_data.get('scheduled_date'), str):
                    try:
                        event_data['planned_start_datetime'] = datetime.strptime(event_data['scheduled_date'], '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        try:
                            event_data['planned_start_datetime'] = datetime.strptime(event_data['scheduled_date'], '%Y-%m-%d')
                        except ValueError:
                            logger.warning(f"Invalid scheduled_date format for maintenance action set {event_data.get('task_name', 'Unknown')}")
                else:
                    event_data['planned_start_datetime'] = event_data.get('scheduled_date')
                event_data.pop('scheduled_date', None)
            
            # Handle start_date string conversion (for In Progress events)
            if 'start_date' in event_data and isinstance(event_data.get('start_date'), str):
                try:
                    # Try datetime format first
                    try:
                        event_data['start_date'] = datetime.strptime(event_data['start_date'], '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        # Try date format
                        event_data['start_date'] = datetime.strptime(event_data['start_date'], '%Y-%m-%d')
                except ValueError:
                    logger.warning(f"Invalid start_date format for maintenance action set {event_data.get('task_name', 'Unknown')}")
                    # Remove invalid start_date
                    event_data.pop('start_date', None)
            
            # Extract actions and part_demands before creating the action set
            actions_data = event_data.pop('actions', [])
            
            action_set = MaintenanceActionSet.find_or_create_from_dict(
                event_data,
                user_id=system_user_id,
                lookup_fields=['task_name', 'asset_id']
            )
            
            action_set_obj = action_set[0]
            is_new = action_set[1]
            
            # Handle actions - either from JSON data or from template
            if actions_data:
                # Create actions from JSON data
                try:
                    from app.data.maintenance.base.actions import Action
                    from app.data.maintenance.templates.template_actions import TemplateActionItem
                    from app.data.supply_items.part import Part
                    from app.data.maintenance.base.part_demands import PartDemand
                    
                    for action_data in actions_data:
                        # Handle template_action_item reference if provided
                        template_action_item_id = None
                        if 'template_action_item_action_name' in action_data:
                            action_name = action_data.pop('template_action_item_action_name')
                            template_action_item = TemplateActionItem.query.filter_by(action_name=action_name).first()
                            if template_action_item:
                                template_action_item_id = template_action_item.id
                        
                        # Extract part_demands before creating action
                        part_demands_data = action_data.pop('part_demands', [])
                        
                        # Handle datetime fields
                        for time_field in ['start_time', 'end_time', 'scheduled_start_time']:
                            if time_field in action_data and isinstance(action_data.get(time_field), str):
                                try:
                                    action_data[time_field] = datetime.strptime(action_data[time_field], '%Y-%m-%d %H:%M:%S')
                                except ValueError:
                                    try:
                                        action_data[time_field] = datetime.strptime(action_data[time_field], '%Y-%m-%d')
                                    except ValueError:
                                        logger.warning(f"Invalid {time_field} format for action {action_data.get('action_name', 'Unknown')}")
                                        action_data.pop(time_field, None)
                        
                        # Create action
                        action_data['maintenance_action_set_id'] = action_set_obj.id
                        if template_action_item_id:
                            action_data['template_action_item_id'] = template_action_item_id
                        action_data['created_by_id'] = system_user_id
                        action_data['updated_by_id'] = system_user_id
                        
                        # Use find_or_create but need to handle the lookup properly
                        # Check if action already exists
                        existing_action = Action.query.filter_by(
                            maintenance_action_set_id=action_set_obj.id,
                            action_name=action_data.get('action_name'),
                            sequence_order=action_data.get('sequence_order', 1)
                        ).first()
                        
                        if existing_action:
                            action_obj = existing_action
                            logger.info(f"Action already exists: {action_data.get('action_name')}")
                        else:
                            action = Action.from_dict(action_data, user_id=system_user_id)
                            db.session.add(action)
                            db.session.flush()  # Get the ID
                            action_obj = action
                            logger.info(f"Created action: {action_data.get('action_name')}")
                        # Create part demands for this action
                        for part_demand_data in part_demands_data:
                            part_demand_data = part_demand_data.copy()
                            # Handle part_number reference
                            if 'part_number' in part_demand_data:
                                part_number = part_demand_data.pop('part_number')
                                part = Part.query.filter_by(part_number=part_number).first()
                                if part:
                                    part_demand_data['part_id'] = part.id
                                else:
                                    logger.warning(f"Part '{part_number}' not found for part demand in action {action_data.get('action_name', 'Unknown')}")
                                    continue
                            
                            part_demand_data['action_id'] = action_obj.id
                            part_demand_data['created_by_id'] = system_user_id
                            part_demand_data['updated_by_id'] = system_user_id
                            
                            # Check if part demand already exists
                            existing_demand = PartDemand.query.filter_by(
                                action_id=action_obj.id,
                                part_id=part_demand_data.get('part_id'),
                                sequence_order=part_demand_data.get('sequence_order', 1)
                            ).first()
                            
                            if not existing_demand:
                                part_demand = PartDemand.from_dict(part_demand_data, user_id=system_user_id)
                                db.session.add(part_demand)
                                part_name = part_number if part_number else f"part_id={part_demand_data.get('part_id')}"
                                logger.info(f"Created part demand: {part_name} x{part_demand_data.get('quantity_required', 1)}")
                            else:
                                part_name = part_number if part_number else f"part_id={part_demand_data.get('part_id')}"
                                logger.info(f"Part demand already exists: {part_name}")
                        
                        logger.info(f"Processed action: {action_data.get('action_name')} with {len(part_demands_data)} part demands")
                    
                    db.session.commit()
                    logger.info(f"Created {len(actions_data)} actions with part demands for: {event_data.get('task_name')}")
                except Exception as e:
                    logger.error(f"Error creating actions from JSON for {event_data.get('task_name', 'Unknown')}: {e}")
                    db.session.rollback()
                    import traceback
                    traceback.print_exc()
            
            elif is_new and event_data.get('template_action_set_id'):
                # Fallback: Create actions from template if no JSON actions provided
                try:
                    from app.data.maintenance.templates.template_action_sets import TemplateActionSet
                    from app.data.maintenance.templates.template_actions import TemplateActionItem
                    
                    template_action_set = TemplateActionSet.query.get(event_data['template_action_set_id'])
                    if template_action_set:
                        # Create actions from template action items
                        from app.data.maintenance.base.actions import Action
                        for template_action_item in template_action_set.template_action_items.order_by(TemplateActionItem.sequence_order):
                            action = Action(
                                maintenance_action_set_id=action_set_obj.id,
                                template_action_item_id=template_action_item.id,
                                action_name=template_action_item.action_name,
                                description=template_action_item.description,
                                estimated_duration=template_action_item.estimated_duration,
                                expected_billable_hours=template_action_item.expected_billable_hours,
                                safety_notes=template_action_item.safety_notes,
                                notes=template_action_item.notes,
                                sequence_order=template_action_item.sequence_order,
                                status='Not Started',
                                created_by_id=system_user_id,
                                updated_by_id=system_user_id
                            )
                            db.session.add(action)
                        
                        db.session.commit()
                        logger.info(f"Created actions from template for: {event_data.get('task_name')}")
                except Exception as e:
                    logger.error(f"Error creating actions from template for {event_data.get('task_name', 'Unknown')}: {e}")
                    db.session.rollback()
            
            if is_new:
                logger.info(f"Created maintenance action set: {event_data.get('task_name')}")
            else:
                logger.info(f"Maintenance action set already exists: {event_data.get('task_name')}")
        except Exception as e:
            logger.error(f"Error creating maintenance action set {event_data.get('task_name', 'Unknown')}: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()


def create_maintenance_from_template(template_action_set_id, asset_id, user_id, **kwargs):
    """
    Convenience function to create maintenance from template using factories
    
    Args:
        template_action_set_id (int): ID of the template to use
        asset_id (int): ID of the asset to maintain
        user_id (int): ID of the user creating the maintenance
        **kwargs: Additional parameters for maintenance creation
    
    Returns:
        dict: Created maintenance objects
    """
    # This will be implemented in business layer factories
    # For now, just raise NotImplementedError
    raise NotImplementedError("This function will be implemented in business layer factories")


def get_template_preview(template_action_set_id):
    """
    Convenience function to get template preview
    
    Args:
        template_action_set_id (int): ID of the template to preview
    
    Returns:
        dict: Template preview information
    """
    # This will be implemented in business layer
    # For now, just raise NotImplementedError
    raise NotImplementedError("This function will be implemented in business layer")

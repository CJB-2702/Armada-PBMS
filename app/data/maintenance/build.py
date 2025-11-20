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
    
    # Import base models
    import app.data.maintenance.base.action
    import app.data.maintenance.base.maintenance_action_set
    import app.data.maintenance.base.maintenance_plan
    import app.data.maintenance.base.maintenance_delays
    import app.data.maintenance.base.part_demand
    
    # Import template models
    import app.data.maintenance.templates.template_action_set
    import app.data.maintenance.templates.template_action_item
    import app.data.maintenance.templates.template_part_demand
    import app.data.maintenance.templates.template_action_tool
    import app.data.maintenance.templates.template_action_attachment
    import app.data.maintenance.templates.template_action_set_attachment
    
    # Note: Factories are business logic and are located in app/buisness/maintenance/factories/
    # They are not needed for model building
    
    # Note: Utilities are business logic and are located in app/buisness/maintenance/utils/
    # They are not needed for model building
    
    # Create all tables to ensure they exist
    db.create_all()
    
    logger.info("Maintenance models build completed")
    pass


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
        _init_template_action_items(build_data['Maintenance'], system_user_id)
        _init_template_part_demands(build_data['Maintenance'], system_user_id)
        _init_template_action_tools(build_data['Maintenance'], system_user_id)
        _init_maintenance_plans(build_data['Maintenance'], system_user_id)
        _init_maintenance_action_sets(build_data['Maintenance'], system_user_id)
    
    logger.info("Maintenance data initialization completed")


def _init_template_action_sets(maintenance_data, system_user_id):
    """Initialize template action sets from build data"""
    from app.data.maintenance.templates.template_action_set import TemplateActionSet
    
    if 'template_action_sets' not in maintenance_data:
        logger.info("No template action sets found in maintenance data")
        return
    
    logger.info("Creating template action sets...")
    for template_data in maintenance_data['template_action_sets']:
        try:
            template = TemplateActionSet.find_or_create_from_dict(
                template_data,
                user_id=system_user_id,
                lookup_fields=['task_name']
            )
            if template[1]:  # If newly created
                logger.info(f"Created template action set: {template_data.get('task_name')}")
            else:
                logger.info(f"Template action set already exists: {template_data.get('task_name')}")
        except Exception as e:
            logger.error(f"Error creating template action set {template_data.get('task_name', 'Unknown')}: {e}")


def _init_template_action_items(maintenance_data, system_user_id):
    """Initialize template action items from build data"""
    from app.data.maintenance.templates.template_action_item import TemplateActionItem
    from app.data.maintenance.templates.template_action_set import TemplateActionSet
    
    if 'template_action_items' not in maintenance_data:
        logger.info("No template action items found in maintenance data")
        return
    
    logger.info("Creating template action items...")
    for item_data in maintenance_data['template_action_items']:
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
            
            item = TemplateActionItem.find_or_create_from_dict(
                item_data,
                user_id=system_user_id,
                lookup_fields=['action_name', 'template_action_set_id']
            )
            if item[1]:  # If newly created
                logger.info(f"Created template action item: {item_data.get('action_name')}")
            else:
                logger.info(f"Template action item already exists: {item_data.get('action_name')}")
        except Exception as e:
            logger.error(f"Error creating template action item {item_data.get('action_name', 'Unknown')}: {e}")


def _init_template_part_demands(maintenance_data, system_user_id):
    """Initialize template part demands from build data"""
    from app.data.maintenance.templates.template_part_demand import TemplatePartDemand
    from app.data.maintenance.templates.template_action_item import TemplateActionItem
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
    from app.data.maintenance.templates.template_action_tool import TemplateActionTool
    from app.data.maintenance.templates.template_action_item import TemplateActionItem
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
    from app.data.maintenance.base.maintenance_plan import MaintenancePlan
    from app.data.core.asset_info.asset_type import AssetType
    from app.data.maintenance.templates.template_action_set import TemplateActionSet
    
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
    from app.data.maintenance.base.maintenance_action_set import MaintenanceActionSet
    from app.data.core.asset_info.asset import Asset
    from app.data.maintenance.base.maintenance_plan import MaintenancePlan
    
    if 'maintenance_action_sets' not in maintenance_data:
        logger.info("No maintenance action sets found in maintenance data")
        return
    
    logger.info("Creating maintenance action sets...")
    for event_data in maintenance_data['maintenance_action_sets']:
        try:
            # Handle asset_name reference
            if 'asset_name' in event_data:
                asset_name = event_data.pop('asset_name')
                asset = Asset.query.filter_by(name=asset_name).first()
                if asset:
                    event_data['asset_id'] = asset.id
                else:
                    logger.warning(f"Asset '{asset_name}' not found for maintenance action set {event_data.get('task_name', 'Unknown')}")
                    continue
            
            # Handle maintenance_plan_name reference
            if 'maintenance_plan_name' in event_data:
                plan_name = event_data.pop('maintenance_plan_name')
                maintenance_plan = MaintenancePlan.query.filter_by(name=plan_name).first()
                if maintenance_plan:
                    event_data['maintenance_plan_id'] = maintenance_plan.id
                    # Also set template_action_set_id from the plan
                    if maintenance_plan.template_action_set_id:
                        event_data['template_action_set_id'] = maintenance_plan.template_action_set_id
                else:
                    logger.warning(f"Maintenance plan '{plan_name}' not found for maintenance action set {event_data.get('task_name', 'Unknown')}")
                    continue
            
            # Handle scheduled_date string conversion
            if 'scheduled_date' in event_data and isinstance(event_data['scheduled_date'], str):
                try:
                    event_data['scheduled_date'] = datetime.strptime(event_data['scheduled_date'], '%Y-%m-%d')
                except ValueError:
                    logger.warning(f"Invalid date format for maintenance action set {event_data.get('task_name', 'Unknown')}")
                    continue
            
            action_set = MaintenanceActionSet.find_or_create_from_dict(
                event_data,
                user_id=system_user_id,
                lookup_fields=['task_name', 'asset_id']
            )
            if action_set[1]:  # If newly created
                logger.info(f"Created maintenance action set: {event_data.get('task_name')}")
            else:
                logger.info(f"Maintenance action set already exists: {event_data.get('task_name')}")
        except Exception as e:
            logger.error(f"Error creating maintenance action set {event_data.get('task_name', 'Unknown')}: {e}")


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
    from app.buisness.maintenance.utils.quick_actions import QuickActions
    
    return QuickActions.create_maintenance_from_template(
        template_action_set_id, asset_id, user_id, **kwargs
    )


def get_template_preview(template_action_set_id):
    """
    Convenience function to get template preview
    
    Args:
        template_action_set_id (int): ID of the template to preview
    
    Returns:
        dict: Template preview information
    """
    from app.buisness.maintenance.utils.quick_actions import QuickActions
    
    return QuickActions.get_template_preview(template_action_set_id)

"""
Maintenance models build module for the Asset Management System
Handles building and initializing maintenance models and data
"""

from app import db
from app.logger import get_logger

logger = get_logger("asset_management.models.maintenance")

def build_models():
    """
    Build maintenance models - this is a no-op since models are imported
    when the app is created, which registers them with SQLAlchemy
    """
    # Base models
    import app.models.maintenance.base.maintenance_plan
    import app.models.maintenance.base.maintenance_event_set
    import app.models.maintenance.base.action
    import app.models.maintenance.base.part_demand_to_action_references
    import app.models.maintenance.base.maintnence_delays
    
    # Template models
    import app.models.maintenance.templates.template_action_set
    import app.models.maintenance.templates.template_action_item
    import app.models.maintenance.templates.template_action_attachment
    import app.models.maintenance.templates.template_action_tool
    import app.models.maintenance.templates.template_part_demand
    
    # Virtual models
    import app.models.maintenance.virtual_action_set
    import app.models.maintenance.virtual_action_item
    
    logger.info("Maintenance models build completed")

def init_data(build_data):
    """
    Initialize maintenance data from build_data
    
    Args:
        build_data (dict): Build data from JSON file
    """
    from app.models.maintenance.base.maintenance_plan import MaintenancePlan
    from app.models.maintenance.templates.template_action_set import TemplateActionSet
    from app.models.maintenance.templates.template_action_item import TemplateActionItem
    from app.models.maintenance.templates.template_part_demand import TemplatePartDemand
    from app.models.maintenance.base.maintenance_event_set import MaintenanceEventSet
    from app.models.core.asset_type import AssetType
    from app.models.core.asset import Asset
    from app.models.core.user import User
    from app.models.supply.part import Part
    
    # Get system user for audit fields
    system_user = User.query.filter_by(username='system').first()
    if not system_user:
        logger.warning("System user not found, creating maintenance data without audit trail")
        system_user_id = None
    else:
        system_user_id = system_user.id
    
    logger.info("Initializing maintenance data...")
    
    # Create maintenance plans from Maintenance section
    if 'Maintenance' in build_data and 'maintenance_plans' in build_data['Maintenance']:
        logger.info("Creating maintenance plans...")
        for plan_data in build_data['Maintenance']['maintenance_plans']:
            # Handle asset_type_name reference
            if 'asset_type_name' in plan_data:
                asset_type_name = plan_data.pop('asset_type_name')
                asset_type = AssetType.query.filter_by(name=asset_type_name).first()
                if asset_type:
                    plan_data['asset_type_id'] = asset_type.id
                else:
                    logger.warning(f"Asset type '{asset_type_name}' not found for maintenance plan {plan_data.get('name')}")
                    continue
            
            MaintenancePlan.find_or_create_from_dict(
                plan_data,
                user_id=system_user_id,
                lookup_fields=['name']
            )
            logger.info(f"Created/updated maintenance plan: {plan_data.get('name')}")
    
    # Create template action sets from Maintenance section
    if 'Maintenance' in build_data and 'template_action_sets' in build_data['Maintenance']:
        logger.info("Creating template action sets...")
        for tas_data in build_data['Maintenance']['template_action_sets']:
            # Handle maintenance_plan_name reference
            if 'maintenance_plan_name' in tas_data:
                plan_name = tas_data.pop('maintenance_plan_name')
                maintenance_plan = MaintenancePlan.query.filter_by(name=plan_name).first()
                if maintenance_plan:
                    tas_data['maintenance_plan_id'] = maintenance_plan.id
                else:
                    logger.warning(f"Maintenance plan '{plan_name}' not found for template action set {tas_data.get('task_name')}")
                    continue
            
            TemplateActionSet.find_or_create_from_dict(
                tas_data,
                user_id=system_user_id,
                lookup_fields=['task_name']
            )
            logger.info(f"Created/updated template action set: {tas_data.get('task_name')}")
    
    # Create template action items from Maintenance section
    if 'Maintenance' in build_data and 'template_action_items' in build_data['Maintenance']:
        logger.info("Creating template action items...")
        for tai_data in build_data['Maintenance']['template_action_items']:
            # Handle template_action_set_task_name reference
            if 'template_action_set_task_name' in tai_data:
                tas_task_name = tai_data.pop('template_action_set_task_name')
                template_action_set = TemplateActionSet.query.filter_by(task_name=tas_task_name).first()
                if template_action_set:
                    tai_data['template_action_set_id'] = template_action_set.id
                else:
                    logger.warning(f"Template action set '{tas_task_name}' not found for template action item {tai_data.get('action_name')}")
                    continue
            
            TemplateActionItem.find_or_create_from_dict(
                tai_data,
                user_id=system_user_id,
                lookup_fields=['action_name', 'template_action_set_id']
            )
            logger.info(f"Created/updated template action item: {tai_data.get('action_name')}")
    
    # Create template part demands from Maintenance section
    if 'Maintenance' in build_data and 'template_part_demands' in build_data['Maintenance']:
        logger.info("Creating template part demands...")
        for tpd_data in build_data['Maintenance']['template_part_demands']:
            # Handle part_number reference
            if 'part_number' in tpd_data:
                part_number = tpd_data.pop('part_number')
                part = Part.query.filter_by(part_number=part_number).first()
                if part:
                    tpd_data['part_id'] = part.id
                else:
                    logger.warning(f"Part '{part_number}' not found for template part demand")
                    continue
            
            # Handle template_action_item_name reference
            if 'template_action_item_name' in tpd_data:
                tai_name = tpd_data.pop('template_action_item_name')
                template_action_item = TemplateActionItem.query.filter_by(action_name=tai_name).first()
                if template_action_item:
                    tpd_data['template_action_item_id'] = template_action_item.id
                else:
                    logger.warning(f"Template action item '{tai_name}' not found for template part demand")
                    continue
            
            TemplatePartDemand.find_or_create_from_dict(
                tpd_data,
                user_id=system_user_id,
                lookup_fields=['part_id', 'template_action_item_id']
            )
            logger.info(f"Created/updated template part demand for part {part_number}")
    
    # Create maintenance event sets from Maintenance section
    if 'Maintenance' in build_data and 'maintenance_event_sets' in build_data['Maintenance']:
        logger.info("Creating maintenance event sets...")
        for mes_data in build_data['Maintenance']['maintenance_event_sets']:
            # Handle maintenance_plan_name reference
            if 'maintenance_plan_name' in mes_data:
                plan_name = mes_data.pop('maintenance_plan_name')
                maintenance_plan = MaintenancePlan.query.filter_by(name=plan_name).first()
                if maintenance_plan:
                    mes_data['maintenance_plan_id'] = maintenance_plan.id
                else:
                    logger.warning(f"Maintenance plan '{plan_name}' not found for maintenance event set")
                    continue
            
            # Handle asset_name reference
            if 'asset_name' in mes_data:
                asset_name = mes_data.pop('asset_name')
                asset = Asset.query.filter_by(name=asset_name).first()
                if asset:
                    mes_data['asset_id'] = asset.id
                else:
                    logger.warning(f"Asset '{asset_name}' not found for maintenance event set")
                    continue
            
            # Handle scheduled_date conversion
            if 'scheduled_date' in mes_data:
                scheduled_date_str = mes_data['scheduled_date']
                try:
                    from datetime import datetime
                    mes_data['scheduled_date'] = datetime.strptime(scheduled_date_str, '%Y-%m-%d').date()
                except ValueError:
                    logger.warning(f"Invalid date format '{scheduled_date_str}' for maintenance event set, skipping")
                    continue
            
            MaintenanceEventSet.find_or_create_from_dict(
                mes_data,
                user_id=system_user_id,
                lookup_fields=['maintenance_plan_id', 'asset_id', 'scheduled_date']
            )
            logger.info(f"Created/updated maintenance event set for asset {asset_name}")
    
    logger.info("Maintenance data initialization completed")

def test_maintenance_independence():
    """
    Test that maintenance can build and accept data independent from supply
    
    Returns:
        bool: True if test passes, False otherwise
    """
    try:
        logger.info("Testing maintenance independence...")
        
        # Test that maintenance models can be imported without supply
        from app.models.maintenance.base.maintenance_plan import MaintenancePlan
        from app.models.maintenance.templates.template_action_set import TemplateActionSet
        from app.models.maintenance.templates.template_action_item import TemplateActionItem
        
        # Test that we can query maintenance tables
        plans_count = MaintenancePlan.query.count()
        tas_count = TemplateActionSet.query.count()
        tai_count = TemplateActionItem.query.count()
        
        logger.info(f"Maintenance independence test passed - Plans: {plans_count}, Action Sets: {tas_count}, Action Items: {tai_count}")
        return True
        
    except Exception as e:
        logger.error(f"Maintenance independence test failed: {e}")
        return False

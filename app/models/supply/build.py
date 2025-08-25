"""
Supply models build module for the Asset Management System
Handles building and initializing supply models and data
"""

from app import db
from app.logger import get_logger

logger = get_logger("asset_management.models.supply")

def build_models():
    """
    Build supply models - this is a no-op since models are imported
    when the app is created, which registers them with SQLAlchemy
    """
    import app.models.supply.part
    import app.models.supply.tool
    import app.models.supply.part_demand
    import app.models.supply.virtual_part_demand
    
    logger.info("Supply models build completed")

def init_data(build_data):
    """
    Initialize supply data from build_data
    
    Args:
        build_data (dict): Build data from JSON file
    """
    from app.models.supply.part import Part
    from app.models.supply.tool import Tool
    from app.models.supply.part_demand import PartDemand
    from app.models.core.user import User
    
    # Get system user for audit fields
    system_user = User.query.filter_by(username='system').first()
    if not system_user:
        logger.warning("System user not found, creating supply data without audit trail")
        system_user_id = None
    else:
        system_user_id = system_user.id
    
    logger.info("Initializing supply data...")
    
    # Create parts from Supply section
    if 'Supply' in build_data and 'parts' in build_data['Supply']:
        logger.info("Creating parts...")
        for part_data in build_data['Supply']['parts']:
            Part.find_or_create_from_dict(
                part_data,
                user_id=system_user_id,
                lookup_fields=['part_number']
            )
            logger.info(f"Created/updated part: {part_data.get('part_number')}")
    
    # Create tools from Supply section
    if 'Supply' in build_data and 'tools' in build_data['Supply']:
        logger.info("Creating tools...")
        for tool_data in build_data['Supply']['tools']:
            # Handle assigned_to_id reference if it exists
            if 'assigned_to_id' in tool_data and tool_data['assigned_to_id']:
                assigned_user = User.query.get(tool_data['assigned_to_id'])
                if not assigned_user:
                    logger.warning(f"Assigned user {tool_data['assigned_to_id']} not found for tool {tool_data.get('tool_name')}")
                    tool_data['assigned_to_id'] = None
            
            # Handle date conversions
            for date_field in ['last_calibration_date', 'next_calibration_date']:
                if date_field in tool_data and tool_data[date_field]:
                    try:
                        from datetime import datetime
                        tool_data[date_field] = datetime.strptime(tool_data[date_field], '%Y-%m-%d').date()
                    except ValueError:
                        logger.warning(f"Invalid date format '{tool_data[date_field]}' for tool {tool_data.get('tool_name')}, removing field")
                        tool_data.pop(date_field, None)
            
            Tool.find_or_create_from_dict(
                tool_data,
                user_id=system_user_id,
                lookup_fields=['serial_number']
            )
            logger.info(f"Created/updated tool: {tool_data.get('tool_name')}")
    
    # Create part demands from Supply section
    if 'Supply' in build_data and 'part_demands' in build_data['Supply']:
        logger.info("Creating part demands...")
        for demand_data in build_data['Supply']['part_demands']:
            # Handle part_number reference
            if 'part_number' in demand_data:
                part_number = demand_data.pop('part_number')
                part = Part.query.filter_by(part_number=part_number).first()
                if part:
                    demand_data['part_id'] = part.id
                else:
                    logger.warning(f"Part '{part_number}' not found for part demand {demand_data.get('notes', 'Unknown')}")
                    continue
            
            # Handle issued_by_id reference if it exists
            if 'issued_by_id' in demand_data and demand_data['issued_by_id']:
                issued_user = User.query.get(demand_data['issued_by_id'])
                if not issued_user:
                    logger.warning(f"Issued by user {demand_data['issued_by_id']} not found for part demand")
                    demand_data['issued_by_id'] = None
            
            PartDemand.find_or_create_from_dict(
                demand_data,
                user_id=system_user_id,
                lookup_fields=['notes']  # Using notes as lookup field
            )
            logger.info(f"Created/updated part demand: {demand_data.get('notes', 'Unknown')}")
    
    logger.info("Supply data initialization completed")

def test_supply_independence():
    """
    Test that supply can build and accept data independent from maintenance
    
    Returns:
        bool: True if test passes, False otherwise
    """
    try:
        logger.info("Testing supply independence...")
        
        # Test that supply models can be imported without maintenance
        from app.models.supply.part import Part
        from app.models.supply.tool import Tool
        from app.models.supply.part_demand import PartDemand
        
        # Test that we can query supply tables
        parts_count = Part.query.count()
        tools_count = Tool.query.count()
        demands_count = PartDemand.query.count()
        
        logger.info(f"Supply independence test passed - Parts: {parts_count}, Tools: {tools_count}, Demands: {demands_count}")
        return True
        
    except Exception as e:
        logger.error(f"Supply independence test failed: {e}")
        return False

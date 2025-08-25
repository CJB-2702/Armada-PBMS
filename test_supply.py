#!/usr/bin/env python3
"""
Test script for supply functionality
"""

from app import create_app, db
from app.models.supply.part import Part
from app.models.supply.tool import Tool
from app.models.supply.part_demand import PartDemand
from app.models.core.user import User
from app.logger import get_logger

logger = get_logger("test_supply")

def test_supply_models():
    """Test supply model creation and relationships"""
    app = create_app()
    
    with app.app_context():
        try:
            # Test creating a part
            part = Part(
                part_number="TEST001",
                part_name="Test Part",
                description="A test part",
                category="Test Category",
                unit_cost=10.50,
                current_stock_level=100,
                minimum_stock_level=10
            )
            db.session.add(part)
            db.session.commit()
            logger.info(f"Created part: {part.part_name}")
            
            # Test creating a tool
            tool = Tool(
                tool_name="Test Tool",
                description="A test tool",
                tool_type="Test Type",
                status="Available"
            )
            db.session.add(tool)
            db.session.commit()
            logger.info(f"Created tool: {tool.tool_name}")
            
            # Test creating a part demand
            # First get a user
            user = User.query.first()
            if user:
                part_demand = PartDemand(
                    part_id=part.id,
                    quantity_required=5,
                    notes="Test demand",
                    requested_by_id=user.id
                )
                db.session.add(part_demand)
                db.session.commit()
                logger.info(f"Created part demand for {part_demand.quantity_required} units")
            
            # Test relationships
            logger.info(f"Part has {len(part.part_demands.all())} demands")
            logger.info(f"Tool status: {tool.status}")
            
            # Clean up
            if user:
                db.session.delete(part_demand)
            db.session.delete(tool)
            db.session.delete(part)
            db.session.commit()
            
            logger.info("Supply model test completed successfully")
            
        except Exception as e:
            logger.error(f"Error testing supply models: {str(e)}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    test_supply_models()

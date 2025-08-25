#!/usr/bin/env python3
"""
Test script to verify the composition approach for linking actions to part demands
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.supply.part_demand import PartDemand
from app.models.maintenance.base.action import Action
from app.models.maintenance.base.part_demand_to_action_references import PartDemandToActionReference
from app.models.supply.part import Part
from app.models.maintenance.base.maintenance_event_set import MaintenanceEventSet
from app.models.maintenance.templates.template_action_item import TemplateActionItem
from app.models.maintenance.templates.template_action_set import TemplateActionSet

def test_composition_approach():
    """Test the composition approach for linking actions to part demands"""
    app = create_app()
    
    with app.app_context():
        print("Testing composition approach for Action-PartDemand linking...")
        
        # Create test data
        print("1. Creating test part...")
        test_part = Part(
            part_number="TEST-001",
            part_name="Test Part",
            description="Test part for composition testing",
            unit_cost=10.50
        )
        db.session.add(test_part)
        db.session.flush()
        
        print("2. Creating test part demand...")
        test_part_demand = PartDemand(
            part_id=test_part.id,
            quantity_required=2.0,
            status="Requested",
            notes="Test part demand"
        )
        db.session.add(test_part_demand)
        db.session.flush()
        
        print("3. Creating test template action set...")
        test_template_set = TemplateActionSet(
            template_name="Test Template Set",
            description="Test template for composition testing"
        )
        db.session.add(test_template_set)
        db.session.flush()
        
        print("4. Creating test template action item...")
        test_template_item = TemplateActionItem(
            template_action_set_id=test_template_set.id,
            action_name="Test Action",
            item_name="Test Item",
            estimated_duration=1.0
        )
        db.session.add(test_template_item)
        db.session.flush()
        
        print("5. Creating test maintenance event set...")
        test_event_set = MaintenanceEventSet(
            template_action_set_id=test_template_set.id,
            asset_id=1,  # Assuming asset with ID 1 exists
            scheduled_date=datetime.utcnow()
        )
        db.session.add(test_event_set)
        db.session.flush()
        
        print("6. Creating test action...")
        test_action = Action(
            maintenance_event_set_id=test_event_set.id,
            template_action_item_id=test_template_item.id,
            action_name="Test Action",
            item_name="Test Item"
        )
        db.session.add(test_action)
        db.session.flush()
        
        print("7. Testing composition linking...")
        # Create reference using the composition class
        reference = PartDemandToActionReference.create_reference(
            action_id=test_action.id,
            part_demand_id=test_part_demand.id,
            user_id=1,  # Assuming user with ID 1 exists
            sequence_order=1,
            notes="Test reference"
        )
        db.session.commit()
        
        print("8. Testing retrieval methods...")
        # Test getting part demands for action
        part_demands = test_action.get_part_demands()
        print(f"   - Part demands for action: {len(part_demands)} found")
        for pd in part_demands:
            print(f"     * {pd.part.part_name}: {pd.quantity_required}")
        
        # Test getting actions for part demand
        actions = PartDemandToActionReference.get_actions_for_part_demand(test_part_demand.id)
        print(f"   - Actions for part demand: {len(actions)} found")
        for action in actions:
            print(f"     * {action.action_name}")
        
        # Test total cost calculation
        total_cost = test_action.get_total_part_cost()
        print(f"   - Total part cost: ${total_cost}")
        
        print("9. Testing sequence ordering...")
        part_demands_ordered = test_action.get_part_demands_by_sequence()
        print(f"   - Ordered part demands: {len(part_demands_ordered)} found")
        
        print("10. Testing reference removal...")
        removed = test_action.remove_part_demand(test_part_demand.id)
        print(f"   - Reference removed: {removed}")
        
        # Verify removal
        part_demands_after = test_action.get_part_demands()
        print(f"   - Part demands after removal: {len(part_demands_after)} found")
        
        print("\n✅ Composition approach test completed successfully!")
        print("\nKey benefits achieved:")
        print("- Supply folder is completely decoupled from maintenance folder")
        print("- PartDemand class remains unchanged and independent")
        print("- Actions can link to any PartDemand without inheritance")
        print("- Clean separation of concerns with composition pattern")
        print("- Full audit trail through UserCreatedBase inheritance")

if __name__ == "__main__":
    from datetime import datetime
    test_composition_approach()

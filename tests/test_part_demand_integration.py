"""
Test that part demands are properly created when actions are added to maintenance action sets
"""

import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app, db
from app.models.core.asset import Asset
from app.models.core.user import User
from app.models.maintenance.templates.template_action_set import TemplateActionSet
from app.models.maintenance.templates.template_action_item import TemplateActionItem
from app.models.maintenance.templates.template_part_demand import TemplatePartDemand
from app.models.maintenance.factories.maintenance_action_set_factory import MaintenanceActionSetFactory
from app.models.maintenance.factories.action_factory import ActionFactory
from app.models.maintenance.base.maintenance_action_set import MaintenanceActionSet
from app.models.maintenance.base.action import Action
from app.models.maintenance.base.part_demand import PartDemand
from app.models.supply_items.part import Part

def test_part_demands_created_from_template():
    """Test that part demands are created when creating maintenance event from template"""
    
    app = create_app()
    
    with app.app_context():
        # Get the Oil Change Procedure template
        template_action_set = TemplateActionSet.query.filter_by(task_name='Oil Change Procedure').first()
        
        if not template_action_set:
            print("❌ FAILED: 'Oil Change Procedure' template not found")
            return False
        
        print(f"✓ Found template: {template_action_set.task_name}")
        
        # Check template has action items with part demands
        template_action_items = TemplateActionItem.query.filter_by(
            template_action_set_id=template_action_set.id
        ).all()
        
        print(f"✓ Template has {len(template_action_items)} action items")
        
        # Count expected part demands from template
        expected_part_demands = 0
        for item in template_action_items:
            part_demand_count = TemplatePartDemand.query.filter_by(
                template_action_item_id=item.id
            ).count()
            expected_part_demands += part_demand_count
            if part_demand_count > 0:
                print(f"  - {item.action_name}: {part_demand_count} part demand(s)")
        
        if expected_part_demands == 0:
            print("❌ FAILED: Template has no part demands configured")
            return False
        
        print(f"✓ Template should generate {expected_part_demands} part demand(s)")
        
        # Get an asset to test with
        asset = Asset.query.filter_by(status='Active').first()
        if not asset:
            print("❌ FAILED: No active asset found")
            return False
        
        print(f"✓ Using asset: {asset.name}")
        
        # Get a user
        user = User.query.filter_by(username='admin').first()
        if not user:
            print("❌ FAILED: Admin user not found")
            return False
        
        print(f"✓ Using user: {user.username}")
        
        # Create maintenance action set from template
        print("\nCreating maintenance action set from template...")
        action_set = MaintenanceActionSetFactory.create_with_actions_from_template(
            template_action_set=template_action_set,
            asset_id=asset.id,
            created_by_id=user.id,
            updated_by_id=user.id
        )
        
        db.session.flush()
        
        print(f"✓ Created maintenance action set: {action_set.task_name} (ID: {action_set.id})")
        
        # Check actions were created
        actions = Action.query.filter_by(maintenance_action_set_id=action_set.id).all()
        print(f"✓ Created {len(actions)} action(s)")
        
        # Check part demands were created
        total_part_demands = 0
        for action in actions:
            part_demands = PartDemand.query.filter_by(action_id=action.id).all()
            total_part_demands += len(part_demands)
            if len(part_demands) > 0:
                print(f"  - Action '{action.action_name}': {len(part_demands)} part demand(s)")
                for pd in part_demands:
                    part = Part.query.get(pd.part_id)
                    if part:
                        print(f"    * {part.part_name} (Qty: {pd.quantity_required})")
        
        # Verify part demands match expected
        if total_part_demands == expected_part_demands:
            print(f"\n✅ SUCCESS: {total_part_demands} part demand(s) created as expected")
            
            # Rollback to not save test data
            db.session.rollback()
            return True
        else:
            print(f"\n❌ FAILED: Expected {expected_part_demands} part demands but got {total_part_demands}")
            db.session.rollback()
            return False


def test_manual_action_creation_with_template():
    """Test that part demands are created when manually adding action from template"""
    
    app = create_app()
    
    with app.app_context():
        # Get a template action item
        template_action_item = TemplateActionItem.query.filter_by(action_name='Add New Oil').first()
        
        if not template_action_item:
            print("❌ FAILED: 'Add New Oil' template action item not found")
            return False
        
        print(f"✓ Found template action item: {template_action_item.action_name}")
        
        # Check if it has part demands
        expected_part_demands = TemplatePartDemand.query.filter_by(
            template_action_item_id=template_action_item.id
        ).count()
        
        print(f"✓ Template action item has {expected_part_demands} part demand(s)")
        
        if expected_part_demands == 0:
            print("⚠ WARNING: Template action item has no part demands, skipping test")
            return True
        
        # Get an existing maintenance action set
        maintenance_action_set = MaintenanceActionSet.query.first()
        if not maintenance_action_set:
            print("❌ FAILED: No maintenance action set found")
            return False
        
        print(f"✓ Using maintenance action set: {maintenance_action_set.task_name}")
        
        # Get a user
        user = User.query.filter_by(username='admin').first()
        if not user:
            print("❌ FAILED: Admin user not found")
            return False
        
        # Create action using create_from_dict (simulating the route behavior)
        print("\nCreating action from template using create_from_dict...")
        action = ActionFactory.create_from_dict({
            'action_name': f'{template_action_item.action_name} TEST',
            'description': template_action_item.description,
            'maintenance_action_set_id': maintenance_action_set.id,
            'template_action_item_id': template_action_item.id,
            'status': 'Not Started',
            'sequence_order': 999,
            'created_by_id': user.id,
            'updated_by_id': user.id
        })
        
        db.session.flush()
        
        print(f"✓ Created action: {action.action_name} (ID: {action.id})")
        
        # Check part demands were created
        part_demands = PartDemand.query.filter_by(action_id=action.id).all()
        actual_part_demands = len(part_demands)
        
        print(f"✓ Created {actual_part_demands} part demand(s)")
        
        for pd in part_demands:
            part = Part.query.get(pd.part_id)
            if part:
                print(f"  - {part.part_name} (Qty: {pd.quantity_required})")
        
        # Verify part demands match expected
        if actual_part_demands == expected_part_demands:
            print(f"\n✅ SUCCESS: {actual_part_demands} part demand(s) created as expected")
            
            # Rollback to not save test data
            db.session.rollback()
            return True
        else:
            print(f"\n❌ FAILED: Expected {expected_part_demands} part demands but got {actual_part_demands}")
            db.session.rollback()
            return False


if __name__ == '__main__':
    print("=" * 80)
    print("Testing Part Demand Integration")
    print("=" * 80)
    
    print("\n" + "=" * 80)
    print("TEST 1: Part demands created from maintenance event template")
    print("=" * 80)
    test1_passed = test_part_demands_created_from_template()
    
    print("\n" + "=" * 80)
    print("TEST 2: Part demands created from manual action creation")
    print("=" * 80)
    test2_passed = test_manual_action_creation_with_template()
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Test 1 (Template Event): {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Test 2 (Manual Action): {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED")
        sys.exit(1)


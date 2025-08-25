#!/usr/bin/env python3
"""
Test TemplateActionTool model
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app import create_app, db
from app.models.maintenance.templates.template_action_tool import TemplateActionTool
from app.models.maintenance.templates.template_action_item import TemplateActionItem
from app.models.maintenance.templates.template_action_set import TemplateActionSet
from app.models.supply.tool import Tool
from app.models.core.user import User
from app.models.core.asset_type import AssetType
from app.models.core.make_model import MakeModel

def test_template_action_tool():
    """Test TemplateActionTool model functionality"""
    
    app = create_app()
    with app.app_context():
        # Create test data
        print("Creating test data...")
        
        # Create a user
        user = User(username='testuser', email='test@example.com')
        user.set_password('password')
        db.session.add(user)
        db.session.flush()
        
        # Create asset type
        asset_type = AssetType(name='Equipment', description='Test equipment')
        db.session.add(asset_type)
        db.session.flush()
        
        # Create make model
        make_model = MakeModel(make='Test', model='Equipment', asset_type_id=asset_type.id)
        db.session.add(make_model)
        db.session.flush()
        
        # Create a tool
        tool = Tool(
            tool_name='Test Wrench',
            description='A test wrench for maintenance',
            tool_type='Hand Tool',
            manufacturer='Test Co',
            status='Available'
        )
        db.session.add(tool)
        db.session.flush()
        
        # Create template action set
        template_set = TemplateActionSet(
            set_name='Test Maintenance Set',
            description='A test maintenance set',
            estimated_duration=120,
            required_skills='Mechanical,Electrical'
        )
        db.session.add(template_set)
        db.session.flush()
        
        # Create template action item
        template_item = TemplateActionItem(
            template_action_set_id=template_set.id,
            item_name='Test Item',
            action_name='Test Action',
            description='A test action item',
            estimated_duration=30,
            sequence_order=1,
            is_required=True
        )
        db.session.add(template_item)
        db.session.flush()
        
        # Create template action tool
        template_tool = TemplateActionTool(
            template_action_item_id=template_item.id,
            tool_id=tool.id,
            is_required=True,
            quantity_required=1,
            sequence_order=1,
            notes='Required for this action'
        )
        db.session.add(template_tool)
        db.session.commit()
        
        print("✓ TemplateActionTool created successfully")
        
        # Test relationships
        print("\nTesting relationships...")
        
        # Test tool relationship
        assert template_tool.tool == tool
        print("✓ Tool relationship works")
        
        # Test template action item relationship
        assert template_tool.template_action_item == template_item
        print("✓ TemplateActionItem relationship works")
        
        # Test backref from template action item
        assert template_tool in template_item.template_action_tools
        print("✓ Backref relationship works")
        
        # Test helper methods
        print("\nTesting helper methods...")
        
        # Test tool name property
        assert template_tool.tool_name == 'Test Wrench'
        print("✓ tool_name property works")
        
        # Test tool status property
        assert template_tool.tool_status == 'Available'
        print("✓ tool_status property works")
        
        # Test availability check
        assert template_tool.is_tool_available() == True
        print("✓ is_tool_available method works")
        
        # Test quantity display
        assert template_tool.get_quantity_display() == '1'
        print("✓ get_quantity_display method works")
        
        # Test requirement display
        assert template_tool.get_requirement_display() == 'Required'
        print("✓ get_requirement_display method works")
        
        # Test TemplateActionItem helper methods
        print("\nTesting TemplateActionItem helper methods...")
        
        required_tools = template_item.get_required_tools()
        assert len(required_tools) == 1
        assert required_tools[0] == tool
        print("✓ get_required_tools method works")
        
        optional_tools = template_item.get_optional_tools()
        assert len(optional_tools) == 0
        print("✓ get_optional_tools method works")
        
        tools_by_sequence = template_item.get_tools_by_sequence()
        assert len(tools_by_sequence) == 1
        assert tools_by_sequence[0] == template_tool
        print("✓ get_tools_by_sequence method works")
        
        # Test string representation
        print("\nTesting string representation...")
        expected_repr = "<TemplateActionTool Test Wrench: Required>"
        assert str(template_tool) == expected_repr
        print("✓ String representation works")
        
        print("\n🎉 All tests passed! TemplateActionTool model is working correctly.")
        
        # Clean up
        db.session.delete(template_tool)
        db.session.delete(template_item)
        db.session.delete(template_set)
        db.session.delete(tool)
        db.session.delete(make_model)
        db.session.delete(asset_type)
        db.session.delete(user)
        db.session.commit()
        
        print("✓ Test data cleaned up")

if __name__ == "__main__":
    test_template_action_tool()

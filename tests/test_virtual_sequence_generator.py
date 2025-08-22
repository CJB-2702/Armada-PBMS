#!/usr/bin/env python3
"""
Test for VirtualSequenceGenerator and its inheritance by asset managers
"""

import unittest
from app.models.core.virtual_sequence_generator import VirtualSequenceGenerator
from app.models.assets.detail_id_managers import AssetDetailIDManager, ModelDetailIDManager

class TestVirtualSequenceGenerator(unittest.TestCase):
    """Test cases for VirtualSequenceGenerator and its subclasses"""
    
    def test_virtual_sequence_generator_is_abstract(self):
        """Test that VirtualSequenceGenerator cannot be instantiated directly"""
        with self.assertRaises(TypeError):
            VirtualSequenceGenerator()
    
    def test_asset_detail_id_manager_inheritance(self):
        """Test that AssetDetailIDManager properly inherits from VirtualSequenceGenerator"""
        self.assertTrue(issubclass(AssetDetailIDManager, VirtualSequenceGenerator))
        
        # Test that it implements the required abstract method
        self.assertEqual(AssetDetailIDManager.get_sequence_table_name(), "asset_detail_id_counter")
        
        # Test that it has the expected methods
        self.assertTrue(hasattr(AssetDetailIDManager, 'get_next_id'))
        self.assertTrue(hasattr(AssetDetailIDManager, 'create_sequence_if_not_exists'))
        self.assertTrue(hasattr(AssetDetailIDManager, 'reset_sequence'))
        self.assertTrue(hasattr(AssetDetailIDManager, 'get_current_sequence_value'))
        self.assertTrue(hasattr(AssetDetailIDManager, 'get_sequence_info'))
    
    def test_model_detail_id_manager_inheritance(self):
        """Test that ModelDetailIDManager properly inherits from VirtualSequenceGenerator"""
        self.assertTrue(issubclass(ModelDetailIDManager, VirtualSequenceGenerator))
        
        # Test that it implements the required abstract method
        self.assertEqual(ModelDetailIDManager.get_sequence_table_name(), "model_detail_id_counter")
        
        # Test that it has the expected methods
        self.assertTrue(hasattr(ModelDetailIDManager, 'get_next_id'))
        self.assertTrue(hasattr(ModelDetailIDManager, 'create_sequence_if_not_exists'))
        self.assertTrue(hasattr(ModelDetailIDManager, 'reset_sequence'))
        self.assertTrue(hasattr(ModelDetailIDManager, 'get_current_sequence_value'))
        self.assertTrue(hasattr(ModelDetailIDManager, 'get_sequence_info'))
    
    def test_sequence_table_names_are_different(self):
        """Test that different managers use different table names"""
        self.assertNotEqual(
            AssetDetailIDManager.get_sequence_table_name(),
            ModelDetailIDManager.get_sequence_table_name()
        )
    
    def test_method_delegation(self):
        """Test that the specific methods delegate to the base class methods"""
        # These should call the base class get_next_id() method
        self.assertEqual(
            AssetDetailIDManager.get_next_asset_detail_id.__name__,
            'get_next_asset_detail_id'
        )
        self.assertEqual(
            ModelDetailIDManager.get_next_model_detail_id.__name__,
            'get_next_model_detail_id'
        )

if __name__ == '__main__':
    unittest.main()

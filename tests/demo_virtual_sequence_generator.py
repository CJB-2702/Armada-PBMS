#!/usr/bin/env python3
"""
Demonstration of VirtualSequenceGenerator and its inheritance by asset managers
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.core.virtual_sequence_generator import VirtualSequenceGenerator
from app.models.assets.detail_id_managers import AssetDetailIDManager, ModelDetailIDManager

def demo_virtual_sequence_generator():
    """Demonstrate the VirtualSequenceGenerator functionality"""
    
    print("=== VirtualSequenceGenerator Demonstration ===\n")
    
    # Show that VirtualSequenceGenerator is abstract
    print("1. VirtualSequenceGenerator is an abstract base class:")
    print(f"   - Cannot be instantiated directly: {VirtualSequenceGenerator.__name__}")
    print(f"   - Is abstract: {VirtualSequenceGenerator.__abstractmethods__}")
    print()
    
    # Show inheritance
    print("2. Asset managers inherit from VirtualSequenceGenerator:")
    print(f"   - AssetDetailIDManager inherits from VirtualSequenceGenerator: {issubclass(AssetDetailIDManager, VirtualSequenceGenerator)}")
    print(f"   - ModelDetailIDManager inherits from VirtualSequenceGenerator: {issubclass(ModelDetailIDManager, VirtualSequenceGenerator)}")
    print()
    
    # Show implemented methods
    print("3. Each manager implements the required abstract method:")
    print(f"   - AssetDetailIDManager table name: {AssetDetailIDManager.get_sequence_table_name()}")
    print(f"   - ModelDetailIDManager table name: {ModelDetailIDManager.get_sequence_table_name()}")
    print()
    
    # Show available methods
    print("4. Both managers have access to base class methods:")
    base_methods = ['get_next_id', 'create_sequence_if_not_exists', 'reset_sequence', 
                   'get_current_sequence_value', 'get_sequence_info']
    
    for method in base_methods:
        print(f"   - {method}: AssetDetailIDManager={hasattr(AssetDetailIDManager, method)}, "
              f"ModelDetailIDManager={hasattr(ModelDetailIDManager, method)}")
    print()
    
    # Show specific methods
    print("5. Each manager has specific methods that delegate to base class:")
    print(f"   - AssetDetailIDManager.get_next_asset_detail_id() calls get_next_id()")
    print(f"   - ModelDetailIDManager.get_next_model_detail_id() calls get_next_id()")
    print()
    
    # Show sequence info structure
    print("6. Sequence info includes table name:")
    asset_info = AssetDetailIDManager.get_sequence_info()
    model_info = ModelDetailIDManager.get_sequence_info()
    print(f"   - Asset sequence info: {asset_info}")
    print(f"   - Model sequence info: {model_info}")
    print()
    
    print("=== Demonstration Complete ===")

if __name__ == '__main__':
    demo_virtual_sequence_generator()

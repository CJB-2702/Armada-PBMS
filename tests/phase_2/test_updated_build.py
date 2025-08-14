#!/usr/bin/env python3
"""
Test script for the updated assets build script
Verifies that the build script works correctly with automatic insertion
"""

import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path.cwd()))

from app import create_app, db
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_build_script():
    """Test the updated build script"""
    logger.info("=== Testing Updated Assets Build Script ===")
    
    # Create Flask app
    app = create_app()
    
    with app.app_context():
        logger.info("1. Testing build_models() function...")
        
        # Import and test the build module
        from app.models.assets.build import build_models, DETAIL_TABLE_REGISTRY
        
        # Test that the registry is properly defined
        logger.info(f"   Registry contains {len(DETAIL_TABLE_REGISTRY)} detail table types:")
        for table_type, config in DETAIL_TABLE_REGISTRY.items():
            logger.info(f"     - {table_type}: {'asset' if config['is_asset_detail'] else 'model'} detail")
        
        # Test build_models function
        try:
            build_models()
            logger.info("   ✓ build_models() executed successfully")
        except Exception as e:
            logger.error(f"   ✗ build_models() failed: {e}")
            return False
        
        logger.info("2. Testing utility functions...")
        
        # Test utility functions
        from app.models.assets.build import get_detail_table_class, is_asset_detail, convert_date_strings
        
        # Test get_detail_table_class
        try:
            purchase_class = get_detail_table_class('purchase_info')
            logger.info(f"   ✓ get_detail_table_class('purchase_info') returned: {purchase_class.__name__}")
        except Exception as e:
            logger.error(f"   ✗ get_detail_table_class failed: {e}")
            return False
        
        # Test is_asset_detail
        try:
            is_asset = is_asset_detail('purchase_info')
            is_model = is_asset_detail('emissions_info')
            logger.info(f"   ✓ is_asset_detail('purchase_info'): {is_asset}")
            logger.info(f"   ✓ is_asset_detail('emissions_info'): {is_model}")
        except Exception as e:
            logger.error(f"   ✗ is_asset_detail failed: {e}")
            return False
        
        # Test convert_date_strings
        try:
            test_data = {
                'purchase_date': '2023-01-15',
                'warranty_end_date': '2026-01-15',
                'purchase_price': 25000.0,
                'purchase_vendor': 'Toyota'
            }
            converted = convert_date_strings(test_data)
            logger.info(f"   ✓ convert_date_strings converted dates: {converted}")
        except Exception as e:
            logger.error(f"   ✗ convert_date_strings failed: {e}")
            return False
        
        logger.info("3. Testing phase_2_init_data with automatic insertion...")
        
        # Import build data
        import json
        build_data_path = Path(__file__).parent / 'app' / 'utils' / 'build_data.json'
        with open(build_data_path, 'r') as f:
            build_data = json.load(f)
        
        # Test phase_2_init_data
        try:
            from app.models.assets.build import phase_2_init_data
            
            # Clear existing data first
            logger.info("   Clearing existing data...")
            from app.models.assets.all_details import AllAssetDetail, AllModelDetail
            from app.models.assets.asset_details.purchase_info import PurchaseInfo
            from app.models.assets.asset_details.vehicle_registration import VehicleRegistration
            from app.models.assets.asset_details.toyota_warranty_receipt import ToyotaWarrantyReceipt
            from app.models.assets.model_details.emissions_info import EmissionsInfo
            from app.models.assets.model_details.model_info import ModelInfo
            
            # Delete existing detail records
            PurchaseInfo.query.delete()
            VehicleRegistration.query.delete()
            ToyotaWarrantyReceipt.query.delete()
            EmissionsInfo.query.delete()
            ModelInfo.query.delete()
            AllAssetDetail.query.delete()
            AllModelDetail.query.delete()
            db.session.commit()
            
            # Run phase_2_init_data
            phase_2_init_data(build_data)
            logger.info("   ✓ phase_2_init_data executed successfully")
            
            # Verify that records were created
            logger.info("4. Verifying automatic insertion worked...")
            
            # Check detail tables
            purchase_count = PurchaseInfo.query.count()
            vehicle_reg_count = VehicleRegistration.query.count()
            warranty_count = ToyotaWarrantyReceipt.query.count()
            emissions_count = EmissionsInfo.query.count()
            model_info_count = ModelInfo.query.count()
            
            logger.info(f"   Detail table counts:")
            logger.info(f"     - PurchaseInfo: {purchase_count}")
            logger.info(f"     - VehicleRegistration: {vehicle_reg_count}")
            logger.info(f"     - ToyotaWarrantyReceipt: {warranty_count}")
            logger.info(f"     - EmissionsInfo: {emissions_count}")
            logger.info(f"     - ModelInfo: {model_info_count}")
            
            # Check master tables
            asset_master_count = AllAssetDetail.query.count()
            model_master_count = AllModelDetail.query.count()
            
            logger.info(f"   Master table counts:")
            logger.info(f"     - AllAssetDetail: {asset_master_count}")
            logger.info(f"     - AllModelDetail: {model_master_count}")
            
            # Verify linking
            if purchase_count > 0 and asset_master_count > 0:
                purchase_record = PurchaseInfo.query.first()
                master_record = AllAssetDetail.query.filter_by(
                    table_name='purchase_info',
                    row_id=purchase_record.id
                ).first()
                
                if master_record:
                    logger.info(f"   ✓ PurchaseInfo properly linked to AllAssetDetail")
                else:
                    logger.error(f"   ✗ PurchaseInfo not properly linked to AllAssetDetail")
                    return False
            
            if emissions_count > 0 and model_master_count > 0:
                emissions_record = EmissionsInfo.query.first()
                master_record = AllModelDetail.query.filter_by(
                    table_name='emissions_info',
                    row_id=emissions_record.id
                ).first()
                
                if master_record:
                    logger.info(f"   ✓ EmissionsInfo properly linked to AllModelDetail")
                else:
                    logger.error(f"   ✗ EmissionsInfo not properly linked to AllModelDetail")
                    return False
            
        except Exception as e:
            logger.error(f"   ✗ phase_2_init_data failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        logger.info("5. Testing error handling...")
        
        # Test with invalid table type
        try:
            invalid_class = get_detail_table_class('invalid_table')
            logger.error(f"   ✗ Should have raised error for invalid table type")
            return False
        except ValueError:
            logger.info(f"   ✓ Properly handled invalid table type")
        
        # Test with invalid detail type check
        try:
            invalid_check = is_asset_detail('invalid_table')
            logger.error(f"   ✗ Should have raised error for invalid table type")
            return False
        except ValueError:
            logger.info(f"   ✓ Properly handled invalid table type in is_asset_detail")
        
        return True

def main():
    """Main test function"""
    logger.info("Updated Assets Build Script Test")
    logger.info("=" * 50)
    
    try:
        success = test_build_script()
        
        if success:
            logger.info("\n=== TEST SUCCESSFUL ===")
            logger.info("Updated assets build script works correctly!")
            logger.info("All functions properly integrated with automatic insertion system.")
        else:
            logger.error("\n=== TEST FAILED ===")
            return 1
            
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())

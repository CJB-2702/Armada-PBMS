#!/usr/bin/env python3
"""
Test script for Phase 2 and Phase 3 functionality
Tests the asset detail table data insertion and automatic detail insertion
"""

import json
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app, db
from app.models.assets.build import phase_2_init_data, phase3_insert_data

def load_build_data():
    """Load build data from JSON file"""
    build_data_path = Path(__file__).parent / "app" / "utils" / "build_data.json"
    with open(build_data_path, 'r') as f:
        return json.load(f)

def test_phase2():
    """Test Phase 2 functionality"""
    logger.debug("=== Testing Phase 2: Asset Detail Tables ===")
    
    app = create_app()
    with app.app_context():
        try:
            # Load build data
            build_data = load_build_data()
            
            # Run phase 2 initialization
            phase_2_init_data(build_data)
            
            logger.debug("✅ Phase 2 completed successfully")
            
            # Verify that detail table rows were created
            from app.models.core.asset import Asset
            from app.models.assets.asset_details.purchase_info import PurchaseInfo
            from app.models.assets.asset_details.vehicle_registration import VehicleRegistration
            from app.models.assets.model_details.emissions_info import EmissionsInfo
            from app.models.assets.model_details.model_info import ModelInfo
            
            assets = Asset.query.all()
            if assets:
                first_asset = assets[0]
                logger.debug(f"📋 Asset: {first_asset.name}")
                
                # Check asset detail tables
                purchase_info = PurchaseInfo.query.filter_by(asset_id=first_asset.id).first()
                if purchase_info:
                    logger.debug(f"  ✅ Purchase Info: {purchase_info.purchase_vendor}")
                
                vehicle_reg = VehicleRegistration.query.filter_by(asset_id=first_asset.id).first()
                if vehicle_reg:
                    logger.debug(f"  ✅ Vehicle Registration: {vehicle_reg.license_plate}")
                
                # Check model detail tables
                if first_asset.make_model_id:
                    emissions_info = EmissionsInfo.query.filter_by(make_model_id=first_asset.make_model_id).first()
                    if emissions_info:
                        logger.debug(f"  ✅ Emissions Info: {emissions_info.emissions_rating}")
                    
                    model_info = ModelInfo.query.filter_by(make_model_id=first_asset.make_model_id).first()
                    if model_info:
                        logger.debug(f"  ✅ Model Info: {model_info.body_style}")
            
        except Exception as e:
            logger.debug(f"❌ Phase 2 failed: {e}")
            import traceback
            traceback.print_exc()

def test_phase3():
    """Test Phase 3 functionality"""
    logger.debug("\n=== Testing Phase 3: Automatic Detail Insertion ===")
    
    app = create_app()
    with app.app_context():
        try:
            # Load build data
            build_data = load_build_data()
            
            # Run phase 3 initialization
            phase3_insert_data(build_data)
            
            logger.debug("✅ Phase 3 completed successfully")
            
            # Verify that assets were created and detail tables were populated
            from app.models.core.asset import Asset
            from app.models.assets.asset_details.purchase_info import PurchaseInfo
            from app.models.assets.asset_details.vehicle_registration import VehicleRegistration
            from app.models.assets.model_details.emissions_info import EmissionsInfo
            from app.models.assets.model_details.model_info import ModelInfo
            
            assets = Asset.query.all()
            logger.debug(f"📊 Total assets in database: {len(assets)}")
            
            for asset in assets:
                logger.debug(f"\n📋 Asset: {asset.name} (ID: {asset.id})")
                
                # Check asset detail tables
                purchase_info = PurchaseInfo.query.filter_by(asset_id=asset.id).first()
                if purchase_info:
                    logger.debug(f"  ✅ Purchase Info: {purchase_info.purchase_vendor} - ${purchase_info.purchase_price}")
                
                vehicle_reg = VehicleRegistration.query.filter_by(asset_id=asset.id).first()
                if vehicle_reg:
                    logger.debug(f"  ✅ Vehicle Registration: {vehicle_reg.license_plate} - {vehicle_reg.state_registered}")
                
                # Check model detail tables
                if asset.make_model_id:
                    emissions_info = EmissionsInfo.query.filter_by(make_model_id=asset.make_model_id).first()
                    if emissions_info:
                        logger.debug(f"  ✅ Emissions Info: {emissions_info.emissions_rating} - {emissions_info.mpg_combined} MPG")
                    
                    model_info = ModelInfo.query.filter_by(make_model_id=asset.make_model_id).first()
                    if model_info:
                        logger.debug(f"  ✅ Model Info: {model_info.body_style} - {model_info.engine_type}")
            
        except Exception as e:
            logger.debug(f"❌ Phase 3 failed: {e}")
            import traceback
            traceback.print_exc()

def main():
    """Main test function"""
    logger.debug("🚀 Starting Phase 2 and Phase 3 Tests")
    logger.debug("=" * 50)
    
    # Test Phase 2
    test_phase2()
    
    # Test Phase 3
    test_phase3()
    
    logger.debug("\n" + "=" * 50)
    logger.debug("🎉 All tests completed!")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Comprehensive test script for all detail tables
Tests the complete flow for both asset and model detail tables
"""

import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path.cwd()))

from app import create_app, db
import logging
from datetime import date

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def build_and_initialize():
    """Build the app and initialize core data"""
    logger.info("=== Building and Initializing Application ===")
    
    # Create Flask app
    app = create_app()
    
    with app.app_context():
        logger.info("1. Creating database tables...")
        
        # Import all necessary models to register them
        logger.info("   Importing core models...")
        import app.models.core.user
        import app.models.core.major_location
        import app.models.core.asset_type
        import app.models.core.make_model
        import app.models.core.asset
        import app.models.core.event
        import app.models.core.attachment
        import app.models.core.comment
        import app.models.core.comment_attachment
        
        logger.info("   Importing asset models...")
        import app.models.assets.all_details
        import app.models.assets.asset_detail_virtual
        import app.models.assets.model_detail_virtual
        import app.models.assets.asset_details.purchase_info
        import app.models.assets.asset_details.vehicle_registration
        import app.models.assets.asset_details.toyota_warranty_receipt
        import app.models.assets.model_details.emissions_info
        import app.models.assets.model_details.model_info
        
        # Create all tables
        db.create_all()
        logger.info("   ✓ All database tables created")
        
        # Insert core data
        logger.info("2. Inserting core data...")
        from app.models.core.build import init_data
        import json
        
        # Load build data from JSON file
        build_data_path = Path(__file__).parent / 'app' / 'utils' / 'build_data.json'
        with open(build_data_path, 'r') as f:
            build_data = json.load(f)
        
        init_data(build_data)
        logger.info("   ✓ Core data inserted")
        
        return app

def test_model_detail_tables():
    """Test model detail table insertions"""
    logger.info("\n=== Testing Model Detail Tables ===")
    
    app = create_app()
    
    with app.app_context():
        # Import the models
        from app.models.assets.model_details.emissions_info import EmissionsInfo
        from app.models.assets.model_details.model_info import ModelInfo
        from app.models.core.make_model import MakeModel
        from app.models.assets.all_details import AllModelDetail
        
        # Get or create a make_model for testing
        logger.info("1. Getting test make_model...")
        make_model = MakeModel.query.first()
        if not make_model:
            logger.error("No make_model found in database.")
            return False
        
        logger.info(f"   Using make_model: {make_model}")
        
        # Test EmissionsInfo
        logger.info("2. Testing EmissionsInfo insertion...")
        emissions = EmissionsInfo(
            make_model_id=make_model.id,
            emissions_standard="EPA Tier 3",
            emissions_rating="ULEV",
            fuel_type="gasoline",
            mpg_city=25.0,
            mpg_highway=32.0,
            mpg_combined=28.0,
            co2_emissions=320.0,
            emissions_test_date=date(2024, 1, 15),
            emissions_certification="EPA-2024-001"
        )
        
        db.session.add(emissions)
        db.session.commit()
        
        logger.info(f"   ✓ EmissionsInfo created with ID: {emissions.id}")
        
        # Test ModelInfo
        logger.info("3. Testing ModelInfo insertion...")
        model_info = ModelInfo(
            make_model_id=make_model.id,
            model_year=2023,
            body_style="sedan",
            engine_type="2.0L 4-cylinder",
            engine_displacement="2.0L",
            transmission_type="automatic",
            drivetrain="FWD",
            seating_capacity=5,
            cargo_capacity=13.1,
            towing_capacity=1500,
            manufacturer_website="https://www.toyota.com/corolla",
            technical_specifications="Standard safety features, Apple CarPlay, Android Auto"
        )
        
        db.session.add(model_info)
        db.session.commit()
        
        logger.info(f"   ✓ ModelInfo created with ID: {model_info.id}")
        
        # Verify master table records
        logger.info("4. Verifying master table records...")
        
        emissions_master = AllModelDetail.query.filter_by(
            table_name='emissions_info',
            row_id=emissions.id
        ).first()
        
        model_info_master = AllModelDetail.query.filter_by(
            table_name='model_info',
            row_id=model_info.id
        ).first()
        
        if emissions_master and model_info_master:
            logger.info(f"   ✓ EmissionsInfo master record: ID {emissions_master.id}, row_id {emissions_master.row_id}")
            logger.info(f"   ✓ ModelInfo master record: ID {model_info_master.id}, row_id {model_info_master.row_id}")
        else:
            logger.error("   ✗ Master table records not found!")
            return False
        
        return True

def test_asset_detail_tables():
    """Test asset detail table insertions"""
    logger.info("\n=== Testing Asset Detail Tables ===")
    
    app = create_app()
    
    with app.app_context():
        # Import the models
        from app.models.assets.asset_details.purchase_info import PurchaseInfo
        from app.models.assets.asset_details.vehicle_registration import VehicleRegistration
        from app.models.assets.asset_details.toyota_warranty_receipt import ToyotaWarrantyReceipt
        from app.models.core.asset import Asset
        from app.models.assets.all_details import AllAssetDetail
        
        # Get or create an asset for testing
        logger.info("1. Getting test asset...")
        asset = Asset.query.first()
        if not asset:
            logger.error("No asset found in database.")
            return False
        
        logger.info(f"   Using asset: {asset}")
        
        # Test PurchaseInfo
        logger.info("2. Testing PurchaseInfo insertion...")
        purchase_info = PurchaseInfo(
            asset_id=asset.id,
            purchase_date=date(2023, 6, 15),
            purchase_price=25000.0,
            purchase_vendor="Toyota of San Diego",
            purchase_order_number="PO-2023-001",
            warranty_start_date=date(2023, 6, 15),
            warranty_end_date=date(2026, 6, 15),
            purchase_notes="Purchased for fleet use"
        )
        
        db.session.add(purchase_info)
        db.session.commit()
        
        logger.info(f"   ✓ PurchaseInfo created with ID: {purchase_info.id}")
        
        # Test VehicleRegistration
        logger.info("3. Testing VehicleRegistration insertion...")
        vehicle_reg = VehicleRegistration(
            asset_id=asset.id,
            license_plate="ABC123",
            registration_number="REG-2023-001",
            registration_expiry=date(2024, 12, 31),
            vin_number="1HGBH41JXMN109186",
            state_registered="CA",
            registration_status="Active",
            insurance_provider="State Farm",
            insurance_policy_number="SF-123456",
            insurance_expiry=date(2024, 6, 30)
        )
        
        db.session.add(vehicle_reg)
        db.session.commit()
        
        logger.info(f"   ✓ VehicleRegistration created with ID: {vehicle_reg.id}")
        
        # Test ToyotaWarrantyReceipt
        logger.info("4. Testing ToyotaWarrantyReceipt insertion...")
        warranty_receipt = ToyotaWarrantyReceipt(
            asset_id=asset.id,
            warranty_receipt_number="TOY-2023-001",
            warranty_type="basic",
            warranty_mileage_limit=36000,
            warranty_time_limit_months=36,
            dealer_name="Toyota of San Diego",
            dealer_contact="John Smith",
            dealer_phone="619-555-0123",
            dealer_email="service@toyotasandiego.com",
            service_history="Initial inspection completed",
            warranty_claims="None"
        )
        
        db.session.add(warranty_receipt)
        db.session.commit()
        
        logger.info(f"   ✓ ToyotaWarrantyReceipt created with ID: {warranty_receipt.id}")
        
        # Verify master table records
        logger.info("5. Verifying master table records...")
        
        purchase_master = AllAssetDetail.query.filter_by(
            table_name='purchase_info',
            row_id=purchase_info.id
        ).first()
        
        vehicle_reg_master = AllAssetDetail.query.filter_by(
            table_name='vehicle_registration',
            row_id=vehicle_reg.id
        ).first()
        
        warranty_master = AllAssetDetail.query.filter_by(
            table_name='toyota_warranty_receipt',
            row_id=warranty_receipt.id
        ).first()
        
        if purchase_master and vehicle_reg_master and warranty_master:
            logger.info(f"   ✓ PurchaseInfo master record: ID {purchase_master.id}, row_id {purchase_master.row_id}")
            logger.info(f"   ✓ VehicleRegistration master record: ID {vehicle_reg_master.id}, row_id {vehicle_reg_master.row_id}")
            logger.info(f"   ✓ ToyotaWarrantyReceipt master record: ID {warranty_master.id}, row_id {warranty_master.row_id}")
        else:
            logger.error("   ✗ Master table records not found!")
            return False
        
        return True

def main():
    """Main test function"""
    logger.info("All Detail Tables Test")
    logger.info("=" * 50)
    
    try:
        # Build and initialize
        app = build_and_initialize()
        
        # Test model detail tables
        model_success = test_model_detail_tables()
        
        # Test asset detail tables
        asset_success = test_asset_detail_tables()
        
        if model_success and asset_success:
            logger.info("\n=== ALL TESTS SUCCESSFUL ===")
            logger.info("All detail tables are working correctly with the updated insert logic!")
            logger.info("\nRun 'python z_view_database.py' to see the database contents.")
        else:
            logger.error("\n=== SOME TESTS FAILED ===")
            return 1
            
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())

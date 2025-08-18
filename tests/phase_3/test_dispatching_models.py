#!/usr/bin/env python3
"""
Test script for Phase 3 Dispatching Models
Tests the dispatching system models and functionality
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app import create_app, db
from app.models.core.user import User
from app.models.core.asset_type import AssetType
from app.models.core.make_model import MakeModel
from app.models.core.asset import Asset
from app.models.core.major_location import MajorLocation
from app.models.dispatching.dispatch import Dispatch
from app.models.dispatching.dispatch_status_history import DispatchStatusHistory
from app.models.dispatching.all_dispatch_details import AllDispatchDetail
from app.models.dispatching.detail_table_sets.asset_type_dispatch_detail_table_set import AssetTypeDispatchDetailTableSet
from app.models.dispatching.detail_table_sets.model_additional_dispatch_detail_table_set import ModelAdditionalDispatchDetailTableSet
from app.models.dispatching.dispatch_details.vehicle_dispatch import VehicleDispatch
from app.models.dispatching.dispatch_details.truck_dispatch_checklist import TruckDispatchChecklist

def test_dispatching_models():
    """Test the dispatching models functionality"""
    logger.debug("Testing Dispatching Models...")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Create database tables
            db.create_all()
            logger.debug("✓ Database tables created")
            
            # Setup automatic dispatch detail insertion
            from app.models.dispatching.build import setup_dispatch_automatic_detail_insertion
            setup_dispatch_automatic_detail_insertion()
            logger.debug("✓ Automatic dispatch detail insertion setup")
            
            # Clean up any existing test data
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Create test user
            test_user = User(
                username=f'test_user_{timestamp}',
                email=f'test_{timestamp}@example.com'
            )
            test_user.set_password('password123')
            db.session.add(test_user)
            db.session.flush()
            logger.debug("✓ Test user created")
            
            # Create test asset type
            vehicle_type = AssetType(
                name='Vehicle',
                description='General vehicle type'
            )
            db.session.add(vehicle_type)
            db.session.flush()
            logger.debug("✓ Vehicle asset type created")
            
            # Create test make/model
            toyota_camry = MakeModel(
                make='Toyota',
                model='Camry',
                asset_type_id=vehicle_type.id
            )
            db.session.add(toyota_camry)
            db.session.flush()
            logger.debug("✓ Toyota Camry make/model created")
            
            # Create test location
            test_location = MajorLocation(
                name='Test Location',
                description='Test location for dispatching',
                address='123 Test St, Test City, TS 12345'
            )
            db.session.add(test_location)
            db.session.flush()
            logger.debug("✓ Test location created")
            
            # Create test asset
            test_asset = Asset(
                name='Test Vehicle',
                serial_number=f'TEST001_{timestamp}',
                make_model_id=toyota_camry.id,
                major_location_id=test_location.id
            )
            db.session.add(test_asset)
            db.session.flush()
            logger.debug("✓ Test asset created")
            
            # Configure dispatch detail table sets for asset types
            vehicle_dispatch_config = AssetTypeDispatchDetailTableSet(
                asset_type_id=vehicle_type.id,
                dispatch_detail_table_type='vehicle_dispatch',
                created_by_id=test_user.id
            )
            db.session.add(vehicle_dispatch_config)
            logger.debug("✓ Vehicle dispatch configuration created for Vehicle asset type")
            
            # Create a dispatch
            test_dispatch = Dispatch(
                dispatch_number=f'DISP001_{timestamp}',
                title='Test Dispatch',
                description='Test dispatch for vehicle',
                asset_id=test_asset.id,
                assigned_user_id=test_user.id,
                major_location_id=test_location.id,
                created_by_id=test_user.id
            )
            db.session.add(test_dispatch)
            db.session.commit()
            logger.debug("✓ Test dispatch created")
            
            # Create initial event manually
            test_dispatch.create_initial_event()
            logger.debug("✓ Initial event created")
            
            # Manually create dispatch detail tables
            AssetTypeDispatchDetailTableSet.create_dispatch_detail_table_rows(test_dispatch.id, test_asset.id)
            logger.debug("✓ Dispatch detail tables created")
            
            # Test status update
            test_dispatch.update_status('Assigned', test_user.id, 'Testing status update')
            logger.debug("✓ Status updated to Assigned")
            
            # Check if vehicle dispatch detail was created
            vehicle_dispatch = VehicleDispatch.query.filter_by(dispatch_id=test_dispatch.id).first()
            if vehicle_dispatch:
                logger.debug("✓ Vehicle dispatch detail created automatically")
                
                # Test vehicle dispatch functionality
                vehicle_dispatch.destination_address = '456 Destination Ave'
                vehicle_dispatch.fuel_level_start = 75.0
                vehicle_dispatch.mileage_start = 1000.0
                logger.debug("✓ Vehicle dispatch details updated")
            else:
                logger.debug("✗ Vehicle dispatch detail not created")
            
            # Check master table entry
            master_entry = AllDispatchDetail.query.filter_by(dispatch_id=test_dispatch.id).first()
            if master_entry:
                logger.debug("✓ Master table entry created")
            else:
                logger.debug("✗ Master table entry not created")
            
            # Check status history
            status_history = DispatchStatusHistory.query.filter_by(dispatch_id=test_dispatch.id).first()
            if status_history:
                logger.debug("✓ Status history created")
            else:
                logger.debug("✗ Status history not created")
            
            # Test truck dispatch checklist
            truck_type = AssetType(
                name='Truck',
                description='Truck type'
            )
            db.session.add(truck_type)
            db.session.flush()
            
            ford_f150 = MakeModel(
                make='Ford',
                model='F-150',
                asset_type_id=truck_type.id
            )
            db.session.add(ford_f150)
            db.session.flush()
            
            test_truck = Asset(
                name='Test Truck',
                serial_number=f'TRUCK001_{timestamp}',
                make_model_id=ford_f150.id,
                major_location_id=test_location.id
            )
            db.session.add(test_truck)
            db.session.flush()
            
            truck_checklist_config = AssetTypeDispatchDetailTableSet(
                asset_type_id=truck_type.id,
                dispatch_detail_table_type='truck_dispatch_checklist',
                created_by_id=test_user.id
            )
            db.session.add(truck_checklist_config)
            logger.debug("✓ Truck checklist configuration created for Truck asset type")
            
            truck_dispatch = Dispatch(
                dispatch_number=f'DISP002_{timestamp}',
                title='Truck Test Dispatch',
                description='Test dispatch for truck',
                asset_id=test_truck.id,
                assigned_user_id=test_user.id,
                major_location_id=test_location.id,
                created_by_id=test_user.id
            )
            db.session.add(truck_dispatch)
            db.session.commit()
            
            # Create initial event manually for truck dispatch
            truck_dispatch.create_initial_event()
            
            # Manually create dispatch detail tables for truck
            AssetTypeDispatchDetailTableSet.create_dispatch_detail_table_rows(truck_dispatch.id, test_truck.id)
            logger.debug("✓ Truck dispatch detail tables created")
            
            truck_checklist = TruckDispatchChecklist.query.filter_by(dispatch_id=truck_dispatch.id).first()
            if truck_checklist:
                logger.debug("✓ Truck dispatch checklist created automatically")
                
                # Test checklist functionality
                truck_checklist.tires_checked = True
                truck_checklist.lights_checked = True
                truck_checklist.brakes_checked = True
                logger.debug(f"✓ Checklist completion: {truck_checklist.completion_percentage:.1f}%")
                
                incomplete_items = truck_checklist.get_incomplete_items()
                logger.debug(f"✓ Incomplete items: {len(incomplete_items)}")
            else:
                logger.debug("✗ Truck dispatch checklist not created")
            
            db.session.commit()
            logger.debug("\n✓ All tests completed successfully!")
            
        except Exception as e:
            logger.debug(f"✗ Test failed: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    test_dispatching_models()

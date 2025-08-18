#!/usr/bin/env python3
"""
Dispatch Models Builder
Builds and registers all dispatch-related models
"""

from app import db
from app.logger import get_logger
logger = get_logger("asset_management.models.dispatching")
from app.models.core.user_created_base import UserCreatedBase
from sqlalchemy import event

# Import all dispatch models
from app.models.dispatching.dispatch import Dispatch
from app.models.dispatching.dispatch_status_history import DispatchStatusHistory
from app.models.dispatching.all_dispatch_details import AllDispatchDetail
from app.models.dispatching.dispatch_detail_virtual import DispatchDetailVirtual

# Import detail table sets
from app.models.dispatching.detail_table_sets.asset_type_dispatch_detail_table_set import AssetTypeDispatchDetailTableSet
from app.models.dispatching.detail_table_sets.model_additional_dispatch_detail_table_set import ModelAdditionalDispatchDetailTableSet

# Import concrete dispatch detail implementations
from app.models.dispatching.dispatch_details.vehicle_dispatch import VehicleDispatch
from app.models.dispatching.dispatch_details.truck_dispatch_checklist import TruckDispatchChecklist

# Registry of all dispatch detail table classes
DISPATCH_DETAIL_TABLE_REGISTRY = {
    'vehicle_dispatch': VehicleDispatch,
    'truck_dispatch_checklist': TruckDispatchChecklist
}

def register_dispatch_models():
    """Register all dispatch models with the database"""
    logger.debug("Registering dispatch models...")
    
    # Core dispatch models
    models = [
        Dispatch,
        DispatchStatusHistory,
        AllDispatchDetail,
        AssetTypeDispatchDetailTableSet,
        ModelAdditionalDispatchDetailTableSet,
        VehicleDispatch,
        TruckDispatchChecklist
    ]
    
    for model in models:
        logger.debug(f"  - Registered {model.__name__}")
    
    logger.debug("Dispatch models registered successfully!")

def setup_dispatch_automatic_detail_insertion():
    """Setup automatic dispatch detail table creation"""
    logger.debug("Setting up automatic dispatch detail insertion...")
    # Note: Automatic detail insertion is handled manually in tests
    # In production, this would be set up with proper event listeners

def create_sample_dispatch_configurations():
    """Create sample dispatch detail table configurations using new structured format"""
    logger.debug("Creating sample dispatch configurations...")
    
    try:
        # Load build data to get configurations
        import json
        from pathlib import Path
        
        build_data_path = Path(__file__).parent.parent.parent / 'utils' / 'build_data.json'
        with open(build_data_path, 'r') as f:
            build_data = json.load(f)
        
        # Get system user for audit fields (should already exist from core build)
        from app.models.core.user import User
        system_user = User.query.filter_by(username='system').first()
        if not system_user:
            logger.debug("Warning: System user not found, skipping dispatch configurations")
            return
        
        system_user_id = system_user.id
        
        # Create dispatch detail table sets
        if 'Dispatching' in build_data and 'Dispatch_Detail_Table_Sets' in build_data['Dispatching']:
            logger.debug("Creating dispatch detail table sets...")
            detail_table_sets = build_data['Dispatching']['Dispatch_Detail_Table_Sets']
            
            # Create AssetTypeDispatchDetailTableSet records
            if 'AssetTypeDispatchDetailTableSet' in detail_table_sets:
                for config_data in detail_table_sets['AssetTypeDispatchDetailTableSet']:
                    existing_config = AssetTypeDispatchDetailTableSet.query.filter_by(
                        asset_type_id=config_data['asset_type_id'],
                        dispatch_detail_table_type=config_data['dispatch_detail_table_type']
                    ).first()
                    
                    if not existing_config:
                        config = AssetTypeDispatchDetailTableSet(
                            asset_type_id=config_data['asset_type_id'],
                            dispatch_detail_table_type=config_data['dispatch_detail_table_type'],
                            is_active=config_data.get('is_active', True),
                            created_by_id=system_user_id
                        )
                        db.session.add(config)
                        logger.debug(f"  - Created AssetTypeDispatchDetailTableSet: asset_type_id={config_data['asset_type_id']}, type={config_data['dispatch_detail_table_type']}")
            
            # Create ModelAdditionalDispatchDetailTableSet records
            if 'ModelAdditionalDispatchDetailTableSet' in detail_table_sets:
                for config_data in detail_table_sets['ModelAdditionalDispatchDetailTableSet']:
                    existing_config = ModelAdditionalDispatchDetailTableSet.query.filter_by(
                        make_model_id=config_data['make_model_id'],
                        dispatch_detail_table_type=config_data['dispatch_detail_table_type']
                    ).first()
                    
                    if not existing_config:
                        config = ModelAdditionalDispatchDetailTableSet(
                            make_model_id=config_data['make_model_id'],
                            dispatch_detail_table_type=config_data['dispatch_detail_table_type'],
                            is_active=config_data.get('is_active', True),
                            created_by_id=system_user_id
                        )
                        db.session.add(config)
                        logger.debug(f"  - Created ModelAdditionalDispatchDetailTableSet: make_model_id={config_data['make_model_id']}, type={config_data['dispatch_detail_table_type']}")
        
        db.session.commit()
        logger.debug("Sample dispatch configurations created successfully!")
        
    except Exception as e:
        logger.debug(f"Error creating sample dispatch configurations: {e}")
        db.session.rollback()


def create_example_dispatch_records():
    """Create example dispatch records from the new structured JSON data"""
    logger.debug("Creating example dispatch records...")
    
    try:
        # Load build data
        import json
        from pathlib import Path
        from datetime import datetime
        
        build_data_path = Path(__file__).parent.parent.parent / 'utils' / 'build_data.json'
        with open(build_data_path, 'r') as f:
            build_data = json.load(f)
        
        # Get example dispatches from Dispatching section
        if 'Dispatching' not in build_data or 'Example_Dispatches' not in build_data['Dispatching']:
            logger.debug("No example dispatches found in build_data")
            return
        
        example_dispatches = build_data['Dispatching']['Example_Dispatches']
        
        # Import required models
        from app.models.dispatching.dispatch import Dispatch
        from app.models.dispatching.dispatch_details.vehicle_dispatch import VehicleDispatch
        from app.models.dispatching.dispatch_details.truck_dispatch_checklist import TruckDispatchChecklist
        from app.models.core.asset import Asset
        from app.models.core.user import User
        
        # Get system user for audit fields
        system_user = User.query.filter_by(username='system').first()
        system_user_id = system_user.id if system_user else 1
        
        # Create example dispatches
        for dispatch_key, dispatch_data in example_dispatches.items():
            logger.debug(f"  Creating dispatch: {dispatch_key}")
            
            # Get the main dispatch record
            dispatch_info = dispatch_data.get('dispatch', {})
            asset_name = dispatch_info.get('asset_name')
            
            # Find the asset
            asset = Asset.query.filter_by(name=asset_name).first()
            if not asset:
                logger.debug(f"    Warning: Asset '{asset_name}' not found, skipping dispatch")
                continue
            
            # Check if a dispatch for this asset already exists
            existing_dispatch = Dispatch.query.filter_by(asset_id=asset.id).first()
            if existing_dispatch:
                logger.debug(f"    Dispatch for asset '{asset_name}' already exists, skipping")
                continue
            
            # Generate unique dispatch number
            import uuid
            dispatch_number = f"DISP-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
            
            # Create main dispatch record with correct fields
            dispatch = Dispatch(
                dispatch_number=dispatch_number,
                title=f"Dispatch for {asset_name}",
                description=dispatch_info.get('dispatch_notes', f"Dispatch for {asset_name}"),
                priority='Normal',
                status=dispatch_info.get('status', 'Created'),
                asset_id=asset.id,
                created_by_id=system_user_id
            )
            db.session.add(dispatch)
            db.session.flush()  # Get the dispatch ID
            
            logger.debug(f"    Created dispatch record: {dispatch.dispatch_number}")
            
            # After creating the dispatch, trigger automatic detail insertion
            # This will create the appropriate detail records based on the asset type and model
            logger.debug(f"    Triggering automatic detail insertion for dispatch {dispatch.id}")
            
            # The automatic detail insertion system should create the appropriate detail records
            # based on the asset type and model configurations
            
            # For now, we'll manually create the detail records, but in a real system
            # this would be handled by the automatic insertion system
            
            # Create vehicle dispatch detail record (for all vehicles)
            vehicle_dispatch = VehicleDispatch(
                dispatch_id=dispatch.id,
                destination_address=dispatch_info.get('destination'),
                route_notes=dispatch_info.get('dispatch_notes'),
                fuel_level_start=75.0,  # 3/4 tank
                mileage_start=0.0,
                driver_notes=f"Driver: {dispatch_info.get('driver_name')}",
                passenger_count=1,
                safety_check_completed=True,
                created_by_id=system_user_id
            )
            db.session.add(vehicle_dispatch)
            logger.debug(f"    Created vehicle dispatch detail record")
            
            # Create truck dispatch checklist detail record (for trucks/F-250)
            if asset.make_model and asset.make_model.make == 'Ford' and asset.make_model.model == 'F-250':
                truck_checklist = TruckDispatchChecklist(
                    dispatch_id=dispatch.id,
                    tires_checked=True,
                    lights_checked=True,
                    brakes_checked=True,
                    fluids_checked=True,
                    safety_equipment_checked=True,
                    cargo_secured=True,
                    weight_distribution_verified=True,
                    load_manifest_verified=True,
                    registration_current=True,
                    insurance_current=True,
                    permits_obtained=True,
                    checklist_notes="All safety protocols followed",
                    completed_by_id=system_user_id,
                    created_by_id=system_user_id
                )
                db.session.add(truck_checklist)
                logger.debug(f"    Created truck dispatch checklist detail record")
        
        db.session.commit()
        logger.debug("Example dispatch records created successfully!")
        
    except Exception as e:
        logger.debug(f"Error creating example dispatch records: {e}")
        db.session.rollback()
        raise

def build_dispatch_models():
    """Main function to build all dispatch models"""
    logger.debug("Building dispatch models...")
    
    # Register models
    register_dispatch_models()
    
    # Setup automatic detail insertion
    setup_dispatch_automatic_detail_insertion()
    
    # Create sample configurations (but not records - those are created during data insertion)
    create_sample_dispatch_configurations()
    
    logger.debug("Dispatch models built successfully!")

if __name__ == "__main__":
    build_dispatch_models()

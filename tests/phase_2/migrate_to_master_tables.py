#!/usr/bin/env python3
"""
Migration script to populate all_asset_details and all_model_details tables
with existing detail data from the current detail tables
"""

import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app, db
from app.models.assets.all_details import AllAssetDetail, AllModelDetail
from app.models.assets.asset_details.purchase_info import PurchaseInfo
from app.models.assets.asset_details.vehicle_registration import VehicleRegistration
from app.models.assets.asset_details.toyota_warranty_receipt import ToyotaWarrantyReceipt
from app.models.assets.model_details.model_info import ModelInfo
from app.models.assets.model_details.emissions_info import EmissionsInfo

def migrate_existing_data():
    """Migrate existing detail data to master tables"""
    app = create_app()
    
    with app.app_context():
        logger.debug("Starting migration to master tables...")
        
        # Migrate asset details
        logger.debug("Migrating asset details...")
        
        # PurchaseInfo
        purchase_records = PurchaseInfo.query.all()
        for record in purchase_records:
            # Check if already exists in master table
            existing = AllAssetDetail.query.filter_by(
                table_name='purchase_info',
                row_id=record.id
            ).first()
            
            if not existing:
                master_record = AllAssetDetail(
                    table_name='purchase_info',
                    row_id=record.id,
                    asset_id=record.asset_id,
                    created_by_id=record.created_by_id,
                    updated_by_id=record.updated_by_id,
                    created_at=record.created_at,
                    updated_at=record.updated_at
                )
                db.session.add(master_record)
                logger.debug(f"Added purchase_info record {record.id} to master table")
        
        # VehicleRegistration
        vehicle_records = VehicleRegistration.query.all()
        for record in vehicle_records:
            existing = AllAssetDetail.query.filter_by(
                table_name='vehicle_registration',
                row_id=record.id
            ).first()
            
            if not existing:
                master_record = AllAssetDetail(
                    table_name='vehicle_registration',
                    row_id=record.id,
                    asset_id=record.asset_id,
                    created_by_id=record.created_by_id,
                    updated_by_id=record.updated_by_id,
                    created_at=record.created_at,
                    updated_at=record.updated_at
                )
                db.session.add(master_record)
                logger.debug(f"Added vehicle_registration record {record.id} to master table")
        
        # ToyotaWarrantyReceipt
        warranty_records = ToyotaWarrantyReceipt.query.all()
        for record in warranty_records:
            existing = AllAssetDetail.query.filter_by(
                table_name='toyota_warranty_receipt',
                row_id=record.id
            ).first()
            
            if not existing:
                master_record = AllAssetDetail(
                    table_name='toyota_warranty_receipt',
                    row_id=record.id,
                    asset_id=record.asset_id,
                    created_by_id=record.created_by_id,
                    updated_by_id=record.updated_by_id,
                    created_at=record.created_at,
                    updated_at=record.updated_at
                )
                db.session.add(master_record)
                logger.debug(f"Added toyota_warranty_receipt record {record.id} to master table")
        
        # Migrate model details
        logger.debug("Migrating model details...")
        
        # ModelInfo
        model_records = ModelInfo.query.all()
        for record in model_records:
            existing = AllModelDetail.query.filter_by(
                table_name='model_info',
                row_id=record.id
            ).first()
            
            if not existing:
                master_record = AllModelDetail(
                    table_name='model_info',
                    row_id=record.id,
                    make_model_id=record.make_model_id,
                    created_by_id=record.created_by_id,
                    updated_by_id=record.updated_by_id,
                    created_at=record.created_at,
                    updated_at=record.updated_at
                )
                db.session.add(master_record)
                logger.debug(f"Added model_info record {record.id} to master table")
        
        # EmissionsInfo
        emissions_records = EmissionsInfo.query.all()
        for record in emissions_records:
            existing = AllModelDetail.query.filter_by(
                table_name='emissions_info',
                row_id=record.id
            ).first()
            
            if not existing:
                master_record = AllModelDetail(
                    table_name='emissions_info',
                    row_id=record.id,
                    make_model_id=record.make_model_id,
                    created_by_id=record.created_by_id,
                    updated_by_id=record.updated_by_id,
                    created_at=record.created_at,
                    updated_at=record.updated_at
                )
                db.session.add(master_record)
                logger.debug(f"Added emissions_info record {record.id} to master table")
        
        # Commit all changes
        try:
            db.session.commit()
            logger.debug("Migration completed successfully!")
        except Exception as e:
            db.session.rollback()
            logger.debug(f"Migration failed: {e}")
            raise

if __name__ == '__main__':
    migrate_existing_data()

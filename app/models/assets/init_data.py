#!/usr/bin/env python3
"""
Data loader utility for asset detail configurations and sample data
Reads configuration data from JSON files to separate data from build logic
"""

import json
from pathlib import Path
from datetime import date
from typing import Dict, List, Any

class AssetInitData:
    """Loads asset detail configurations and sample data from JSON files"""
    
    def __init__(self, config_file_path: str = None):
        """
        Initialize the data loader
        
        Args:
            config_file_path (str): Path to the configuration JSON file
        """
        if config_file_path is None:
            # Default to the centralized build_data.json file in utils
            current_file = Path(__file__)
            # Navigate from app/models/assets/ to app/utils/
            utils_dir = current_file.parent.parent.parent / 'utils'
            config_file_path = str(utils_dir / 'build_data.json')
        
        self.config_file_path = config_file_path
        self.config_data = None
        self._load_config()
    
    def _load_config(self):
        """Load configuration data from JSON file"""
        try:
            with open(self.config_file_path, 'r') as f:
                self.config_data = json.load(f)
            print(f"✓ Configuration loaded from {self.config_file_path}")
        except FileNotFoundError:
            print(f"✗ Configuration file not found: {self.config_file_path}")
            self.config_data = {}
        except json.JSONDecodeError as e:
            print(f"✗ Invalid JSON in configuration file: {e}")
            self.config_data = {}
    
    def get_detail_table_configurations(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get detail table configurations for asset types and models
        
        Returns:
            Dict containing 'asset_type_configs' and 'model_configs' lists
        """
        return self.config_data.get('detail_table_configurations', {
            'asset_type_configs': [],
            'model_configs': []
        })
    
    def get_sample_data(self) -> Dict[str, Dict[str, Any]]:
        """
        Get sample data for detail tables
        
        Returns:
            Dict containing sample data for each detail table type
        """
        return self.config_data.get('sample_data', {})
    
    def get_test_assets(self) -> List[Dict[str, str]]:
        """
        Get test asset configurations
        
        Returns:
            List of test asset configurations
        """
        return self.config_data.get('test_assets', [])
    
    def convert_date_strings(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert date strings in data to date objects
        
        Args:
            data (Dict): Data dictionary that may contain date strings
            
        Returns:
            Dict with date strings converted to date objects
        """
        converted_data = {}
        
        for key, value in data.items():
            if isinstance(value, dict):
                converted_data[key] = self.convert_date_strings(value)
            elif isinstance(value, str) and self._is_date_string(value):
                try:
                    converted_data[key] = date.fromisoformat(value)
                except ValueError:
                    converted_data[key] = value
            else:
                converted_data[key] = value
        
        return converted_data
    
    def _is_date_string(self, value: str) -> bool:
        """
        Check if a string looks like a date string (YYYY-MM-DD format)
        
        Args:
            value (str): String to check
            
        Returns:
            bool: True if string looks like a date
        """
        if not isinstance(value, str):
            return False
        
        # Check for YYYY-MM-DD format
        if len(value) == 10 and value.count('-') == 2:
            try:
                date.fromisoformat(value)
                return True
            except ValueError:
                pass
        
        return False
    
    def get_asset_type_configs(self) -> List[Dict[str, Any]]:
        """
        Get asset type detail table configurations
        
        Returns:
            List of asset type configurations
        """
        configs = self.get_detail_table_configurations()
        return configs.get('asset_type_configs', [])
    
    def get_model_configs(self) -> List[Dict[str, Any]]:
        """
        Get model detail table configurations
        
        Returns:
            List of model configurations
        """
        configs = self.get_detail_table_configurations()
        return configs.get('model_configs', [])
    
    def get_sample_data_for_table(self, table_type: str) -> Dict[str, Any]:
        """
        Get sample data for a specific detail table type
        
        Args:
            table_type (str): The detail table type (e.g., 'purchase_info')
            
        Returns:
            Dict containing sample data for the table type
        """
        sample_data = self.get_sample_data()
        data = sample_data.get(table_type, {})
        return self.convert_date_strings(data)
    
    def reload_config(self):
        """Reload configuration from file"""
        self._load_config()

    def initialize_detail_table_sets(self):
        """
        Initialize only the detail table set configurations (without sample data)
        
        Returns:
            bool: True if successful, False otherwise
        """
        print("=== Initializing Detail Table Set Configurations ===")
        
        try:
            from app import db
            from app.models.core.user import User
            from app.models.core.asset_type import AssetType
            from app.models.core.make_model import MakeModel
            from app.models.assets.detail_table_sets.asset_type_detail_table_set import AssetTypeDetailTableSet
            from app.models.assets.detail_table_sets.model_detail_table_set import ModelDetailTableSet
            
            # Get system user for creating data
            system_user = User.query.filter_by(username='system').first()
            if not system_user:
                print("   ✗ System user not found!")
                return False
            
            # Step 1: Check and insert core asset types if needed
            print("1. Checking Core Asset Types...")
            vehicle_type = AssetType.query.filter_by(name='Vehicle').first()
            if not vehicle_type:
                print("   ✓ Creating Vehicle asset type...")
                vehicle_type = AssetType(
                    name='Vehicle',
                    category='Transportation',
                    description='Motor vehicles for transportation',
                    is_active=True,
                    created_by_id=system_user.id,
                    updated_by_id=system_user.id
                )
                db.session.add(vehicle_type)
                db.session.commit()
                print("   ✓ Vehicle asset type created")
            else:
                print("   ✓ Vehicle asset type already exists")
            
            # Step 2: Check and insert core make/models if needed
            print("2. Checking Core Make/Models...")
            toyota_corolla = MakeModel.query.filter_by(make='Toyota', model='Corolla').first()
            if not toyota_corolla:
                print("   ✓ Creating Toyota Corolla make/model...")
                toyota_corolla = MakeModel(
                    make='Toyota',
                    model='Corolla',
                    year=2023,
                    description='Toyota Corolla 2023 model',
                    asset_type_id=vehicle_type.id,
                    is_active=True,
                    created_by_id=system_user.id,
                    updated_by_id=system_user.id
                )
                db.session.add(toyota_corolla)
                db.session.commit()
                print("   ✓ Toyota Corolla make/model created")
            else:
                print("   ✓ Toyota Corolla make/model already exists")
            
            # Step 1: Create Asset Type Detail Table Sets
            print("1. Creating Asset Type Detail Table Sets...")
            
            asset_type_configs = self.get_asset_type_configs()
            for config in asset_type_configs:
                if config['asset_type_name'] == 'Vehicle':
                    # Check if configuration already exists
                    existing_set = AssetTypeDetailTableSet.query.filter_by(
                        asset_type_id=vehicle_type.id,
                        detail_table_type=config['detail_table_type']
                    ).first()
                    
                    if not existing_set:
                        new_set = AssetTypeDetailTableSet(
                            asset_type_id=vehicle_type.id,
                            detail_table_type=config['detail_table_type'],
                            is_asset_detail=config['is_asset_detail'],
                            is_active=config['is_active'],
                            created_by_id=system_user.id,
                            updated_by_id=system_user.id
                        )
                        db.session.add(new_set)
                        print(f"   ✓ {config['detail_table_type']} detail table set created")
            
            db.session.commit()
            
            # Step 2: Create Model Detail Table Sets
            print("2. Creating Model Detail Table Sets...")
            
            model_configs = self.get_model_configs()
            for config in model_configs:
                if config['make'] == 'Toyota' and config['model'] == 'Corolla':
                    # Check if configuration already exists
                    existing_set = ModelDetailTableSet.query.filter_by(
                        make_model_id=toyota_corolla.id,
                        detail_table_type=config['detail_table_type']
                    ).first()
                    
                    if not existing_set:
                        new_set = ModelDetailTableSet(
                            make_model_id=toyota_corolla.id,
                            detail_table_type=config['detail_table_type'],
                            is_asset_detail=config['is_asset_detail'],
                            is_active=config['is_active'],
                            created_by_id=system_user.id,
                            updated_by_id=system_user.id
                        )
                        db.session.add(new_set)
                        print(f"   ✓ {config['detail_table_type']} detail table set created")
            
            db.session.commit()
            
            # Step 3: Insert data into detail table sets
            print("3. Inserting Data into Detail Table Sets...")
            
            # Get the created detail table sets
            asset_type_sets = AssetTypeDetailTableSet.query.filter_by(asset_type_id=vehicle_type.id).all()
            model_sets = ModelDetailTableSet.query.filter_by(make_model_id=toyota_corolla.id).all()
            
            print(f"   ✓ Found {len(asset_type_sets)} asset type detail table sets")
            print(f"   ✓ Found {len(model_sets)} model detail table sets")
            
            # Step 4: Insert detail table configurations
            print("4. Inserting Detail Table Configurations...")
            
            # Get detail table configurations from config
            detail_configs = self.get_detail_table_configurations()
            
            for table_type, configs in detail_configs.items():
                print(f"   ✓ Processing {table_type} configurations")
                for config in configs:
                    print(f"      - {config.get('name', 'Unknown')}: {config.get('description', 'No description')}")
            
            print(f"   ✓ Processed {sum(len(configs) for configs in detail_configs.values())} detail table configurations")
            
            db.session.commit()
            
            # Step 5: Create detail rows for existing assets (since automatic insertion wasn't enabled when they were created)
            print("5. Creating Detail Rows for Existing Assets...")
            from app.models.core.asset import Asset
            from app.models.assets.asset_details.purchase_info import PurchaseInfo
            from app.models.assets.asset_details.vehicle_registration import VehicleRegistration
            from app.models.assets.asset_details.toyota_warranty_receipt import ToyotaWarrantyReceipt
            from app.models.assets.model_details.emissions_info import EmissionsInfo
            from app.models.assets.model_details.model_info import ModelInfo
            
            # Get existing asset
            vtc_001 = Asset.query.filter_by(serial_number='VTC0012023001').first()
            if vtc_001:
                # Create purchase info if it doesn't exist
                if not PurchaseInfo.query.filter_by(asset_id=vtc_001.id).first():
                    purchase_info = PurchaseInfo(asset_id=vtc_001.id, created_by_id=system_user.id)
                    db.session.add(purchase_info)
                    print("   ✓ Purchase info created for VTC-001")
                
                # Create vehicle registration if it doesn't exist
                if not VehicleRegistration.query.filter_by(asset_id=vtc_001.id).first():
                    vehicle_reg = VehicleRegistration(asset_id=vtc_001.id, created_by_id=system_user.id)
                    db.session.add(vehicle_reg)
                    print("   ✓ Vehicle registration created for VTC-001")
                
                # Create Toyota warranty receipt if it doesn't exist
                if not ToyotaWarrantyReceipt.query.filter_by(asset_id=vtc_001.id).first():
                    toyota_warranty = ToyotaWarrantyReceipt(asset_id=vtc_001.id, created_by_id=system_user.id)
                    db.session.add(toyota_warranty)
                    print("   ✓ Toyota warranty receipt created for VTC-001")
                
                # Create emissions info if it doesn't exist
                if not EmissionsInfo.query.filter_by(make_model_id=toyota_corolla.id).first():
                    emissions_info = EmissionsInfo(make_model_id=toyota_corolla.id, created_by_id=system_user.id)
                    db.session.add(emissions_info)
                    print("   ✓ Emissions info created for Toyota Corolla")
                
                # Create model info if it doesn't exist
                if not ModelInfo.query.filter_by(make_model_id=toyota_corolla.id).first():
                    model_info = ModelInfo(make_model_id=toyota_corolla.id, created_by_id=system_user.id)
                    db.session.add(model_info)
                    print("   ✓ Model info created for Toyota Corolla")
                
                db.session.commit()
                print("   ✓ All detail rows created for existing assets")
            else:
                print("   ✓ No existing assets found, detail rows will be created when assets are added")
            
            print("\n=== Detail Table Set Initialization Complete ===")
            print("✓ Asset type detail table sets created")
            print("✓ Model detail table sets created")
            print("✓ Data inserted into detail table sets")
            print("✓ Detail table configurations processed")
            return True
            
        except Exception as e:
            print(f"\n=== Detail Table Set Initialization FAILED ===")
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()
            from app import db
            db.session.rollback()
            return False

    def load_asset_data(self):
        """
        Load asset detail data into the database
        
        Returns:
            bool: True if successful, False otherwise
        """
        print("=== Loading Asset Detail Data ===")
        
        try:
            from app import db
            from app.models.core.user import User
            from app.models.core.asset_type import AssetType
            from app.models.core.make_model import MakeModel
            from app.models.core.asset import Asset
            from app.models.assets.detail_table_sets.asset_type_detail_table_set import AssetTypeDetailTableSet
            from app.models.assets.detail_table_sets.model_detail_table_set import ModelDetailTableSet
            from app.models.assets.asset_details.purchase_info import PurchaseInfo
            from app.models.assets.asset_details.vehicle_registration import VehicleRegistration
            from app.models.assets.asset_details.toyota_warranty_receipt import ToyotaWarrantyReceipt
            from app.models.assets.model_details.emissions_info import EmissionsInfo
            from app.models.assets.model_details.model_info import ModelInfo
            
            # Get system user for creating data
            system_user = User.query.filter_by(username='system').first()
            if not system_user:
                print("   ✗ System user not found!")
                return False
            
            # Get existing asset type and make/model
            vehicle_type = AssetType.query.filter_by(name='Vehicle').first()
            toyota_corolla = MakeModel.query.filter_by(make='Toyota', model='Corolla').first()
            vtc_001 = Asset.query.filter_by(serial_number='VTC0012023001').first()
            
            if not vehicle_type or not toyota_corolla or not vtc_001:
                print("   ✗ Required core data not found!")
                return False
            
            # Step 1: Create Asset Type Detail Table Sets
            print("1. Creating Asset Type Detail Table Sets...")
            
            asset_type_configs = self.get_asset_type_configs()
            for config in asset_type_configs:
                if config['asset_type_name'] == 'Vehicle':
                    # Check if configuration already exists
                    existing_set = AssetTypeDetailTableSet.query.filter_by(
                        asset_type_id=vehicle_type.id,
                        detail_table_type=config['detail_table_type']
                    ).first()
                    
                    if not existing_set:
                        new_set = AssetTypeDetailTableSet(
                            asset_type_id=vehicle_type.id,
                            detail_table_type=config['detail_table_type'],
                            is_asset_detail=config['is_asset_detail'],
                            is_active=config['is_active'],
                            created_by_id=system_user.id,
                            updated_by_id=system_user.id
                        )
                        db.session.add(new_set)
                        print(f"   ✓ {config['detail_table_type']} detail table set created")
            
            db.session.commit()
            
            # Step 2: Create Model Detail Table Sets
            print("2. Creating Model Detail Table Sets...")
            
            model_configs = self.get_model_configs()
            for config in model_configs:
                if config['make'] == 'Toyota' and config['model'] == 'Corolla':
                    # Check if configuration already exists
                    existing_set = ModelDetailTableSet.query.filter_by(
                        make_model_id=toyota_corolla.id,
                        detail_table_type=config['detail_table_type']
                    ).first()
                    
                    if not existing_set:
                        new_set = ModelDetailTableSet(
                            make_model_id=toyota_corolla.id,
                            detail_table_type=config['detail_table_type'],
                            is_asset_detail=config['is_asset_detail'],
                            is_active=config['is_active'],
                            created_by_id=system_user.id,
                            updated_by_id=system_user.id
                        )
                        db.session.add(new_set)
                        print(f"   ✓ {config['detail_table_type']} detail table set created")
            
            db.session.commit()
            
            # Step 3: Create sample detail table data
            print("3. Creating Sample Detail Table Data...")
            
            # Create purchase info for VTC-001
            purchase_info = PurchaseInfo.query.filter_by(asset_id=vtc_001.id).first()
            if not purchase_info:
                purchase_data = self.get_sample_data_for_table('purchase_info')
                purchase_info = PurchaseInfo(
                    asset_id=vtc_001.id,
                    created_by_id=system_user.id,
                    updated_by_id=system_user.id,
                    **purchase_data
                )
                db.session.add(purchase_info)
                print("   ✓ Purchase info created for VTC-001")
            
            # Create vehicle registration for VTC-001
            vehicle_reg = VehicleRegistration.query.filter_by(asset_id=vtc_001.id).first()
            if not vehicle_reg:
                reg_data = self.get_sample_data_for_table('vehicle_registration')
                vehicle_reg = VehicleRegistration(
                    asset_id=vtc_001.id,
                    created_by_id=system_user.id,
                    updated_by_id=system_user.id,
                    **reg_data
                )
                db.session.add(vehicle_reg)
                print("   ✓ Vehicle registration created for VTC-001")
            
            # Create Toyota warranty receipt for VTC-001
            toyota_warranty = ToyotaWarrantyReceipt.query.filter_by(asset_id=vtc_001.id).first()
            if not toyota_warranty:
                warranty_data = self.get_sample_data_for_table('toyota_warranty_receipt')
                toyota_warranty = ToyotaWarrantyReceipt(
                    asset_id=vtc_001.id,
                    created_by_id=system_user.id,
                    updated_by_id=system_user.id,
                    **warranty_data
                )
                db.session.add(toyota_warranty)
                print("   ✓ Toyota warranty receipt created for VTC-001")
            
            # Create emissions info for Toyota Corolla model
            emissions_info = EmissionsInfo.query.filter_by(make_model_id=toyota_corolla.id).first()
            if not emissions_info:
                emissions_data = self.get_sample_data_for_table('emissions_info')
                emissions_info = EmissionsInfo(
                    make_model_id=toyota_corolla.id,
                    created_by_id=system_user.id,
                    updated_by_id=system_user.id,
                    **emissions_data
                )
                db.session.add(emissions_info)
                print("   ✓ Emissions info created for Toyota Corolla")
            
            # Create model info for Toyota Corolla model
            model_info = ModelInfo.query.filter_by(make_model_id=toyota_corolla.id).first()
            if not model_info:
                model_data = self.get_sample_data_for_table('model_info')
                model_info = ModelInfo(
                    make_model_id=toyota_corolla.id,
                    created_by_id=system_user.id,
                    updated_by_id=system_user.id,
                    **model_data
                )
                db.session.add(model_info)
                print("   ✓ Model info created for Toyota Corolla")
            
            db.session.commit()
            
            print("\n=== Asset Detail Data Loading Complete ===")
            return True
            
        except Exception as e:
            print(f"\n=== Asset Detail Data Loading FAILED ===")
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()
            from app import db
            db.session.rollback()
            return False

    def update_auto_generated_details(self):
        """Update auto-generated detail rows with actual data (Phase 3B)"""
        print("=== Updating Auto-Generated Detail Rows ===")
        
        try:
            from app import db
            from app.models.core.user import User
            from app.models.core.asset_type import AssetType
            from app.models.core.make_model import MakeModel
            from app.models.core.asset import Asset
            from app.models.assets.asset_details.purchase_info import PurchaseInfo
            from app.models.assets.asset_details.vehicle_registration import VehicleRegistration
            from app.models.assets.asset_details.toyota_warranty_receipt import ToyotaWarrantyReceipt
            from app.models.assets.model_details.emissions_info import EmissionsInfo
            from app.models.assets.model_details.model_info import ModelInfo
            
            # Get system user for updating data
            system_user = User.query.filter_by(username='system').first()
            if not system_user:
                print("   ✗ System user not found!")
                return False
            
            # Get existing asset type and make/model
            vehicle_type = AssetType.query.filter_by(name='Vehicle').first()
            toyota_corolla = MakeModel.query.filter_by(make='Toyota', model='Corolla').first()
            vtc_001 = Asset.query.filter_by(serial_number='VTC0012023001').first()
            
            if not vehicle_type or not toyota_corolla or not vtc_001:
                print("   ✗ Required core data not found!")
                return False
            
            print("1. Updating Asset Detail Rows...")
            
            # Update purchase info for VTC-001 (should already exist from auto-generation)
            purchase_info = PurchaseInfo.query.filter_by(asset_id=vtc_001.id).first()
            if purchase_info:
                purchase_data = self.get_sample_data_for_table('purchase_info')
                for key, value in purchase_data.items():
                    setattr(purchase_info, key, value)
                purchase_info.updated_by_id = system_user.id
                print("   ✓ Purchase info updated for VTC-001")
            else:
                print("   ✗ Auto-generated purchase info not found for VTC-001")
                return False
            
            # Update vehicle registration for VTC-001 (should already exist from auto-generation)
            vehicle_reg = VehicleRegistration.query.filter_by(asset_id=vtc_001.id).first()
            if vehicle_reg:
                reg_data = self.get_sample_data_for_table('vehicle_registration')
                for key, value in reg_data.items():
                    setattr(vehicle_reg, key, value)
                vehicle_reg.updated_by_id = system_user.id
                print("   ✓ Vehicle registration updated for VTC-001")
            else:
                print("   ✗ Auto-generated vehicle registration not found for VTC-001")
                return False
            
            # Update or create Toyota warranty receipt for VTC-001
            toyota_warranty = ToyotaWarrantyReceipt.query.filter_by(asset_id=vtc_001.id).first()
            if not toyota_warranty:
                # Create the Toyota warranty receipt if it doesn't exist
                toyota_warranty = ToyotaWarrantyReceipt(asset_id=vtc_001.id, created_by_id=system_user.id)
                db.session.add(toyota_warranty)
                print("   ✓ Toyota warranty receipt created for VTC-001")
            
            warranty_data = self.get_sample_data_for_table('toyota_warranty_receipt')
            for key, value in warranty_data.items():
                setattr(toyota_warranty, key, value)
            toyota_warranty.updated_by_id = system_user.id
            print("   ✓ Toyota warranty receipt updated for VTC-001")
            
            print("2. Updating Model Detail Rows...")
            
            # Update or create emissions info for Toyota Corolla model
            emissions_info = EmissionsInfo.query.filter_by(make_model_id=toyota_corolla.id).first()
            if not emissions_info:
                # Create the emissions info if it doesn't exist
                emissions_info = EmissionsInfo(make_model_id=toyota_corolla.id, created_by_id=system_user.id)
                db.session.add(emissions_info)
                print("   ✓ Emissions info created for Toyota Corolla")
            
            emissions_data = self.get_sample_data_for_table('emissions_info')
            for key, value in emissions_data.items():
                setattr(emissions_info, key, value)
            emissions_info.updated_by_id = system_user.id
            print("   ✓ Emissions info updated for Toyota Corolla")
            
            # Update or create model info for Toyota Corolla model
            model_info = ModelInfo.query.filter_by(make_model_id=toyota_corolla.id).first()
            if not model_info:
                # Create the model info if it doesn't exist
                model_info = ModelInfo(make_model_id=toyota_corolla.id, created_by_id=system_user.id)
                db.session.add(model_info)
                print("   ✓ Model info created for Toyota Corolla")
            
            model_data = self.get_sample_data_for_table('model_info')
            for key, value in model_data.items():
                setattr(model_info, key, value)
            model_info.updated_by_id = system_user.id
            print("   ✓ Model info updated for Toyota Corolla")
            
            db.session.commit()
            
            print("\n=== Auto-Generated Detail Update Complete ===")
            print("✓ All auto-generated detail rows updated successfully")
            print("✓ Phase 3 data insertion completed")
            return True
            
        except Exception as e:
            print(f"\n=== Auto-Generated Detail Update FAILED ===")
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()
            from app import db
            db.session.rollback()
            return False


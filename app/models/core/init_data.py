#!/usr/bin/env python3
"""
Core data initialization module
Handles initialization of all core system data from centralized build_data.json
"""

import json
from pathlib import Path
from datetime import date
from typing import Dict, List, Any

class CoreDataLoader:
    """Loads core system data from centralized build_data.json"""
    
    def __init__(self, config_file_path: str = None):
        """
        Initialize the core data loader
        
        Args:
            config_file_path (str): Path to the configuration JSON file
        """
        if config_file_path is None:
            # Default to the centralized build_data.json file in utils
            current_file = Path(__file__)
            # Navigate from app/models/core/ to app/utils/
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
            print(f"✓ Core configuration loaded from {self.config_file_path}")
        except FileNotFoundError:
            print(f"✗ Configuration file not found: {self.config_file_path}")
            self.config_data = {}
        except json.JSONDecodeError as e:
            print(f"✗ Invalid JSON in configuration file: {e}")
            self.config_data = {}
    
    def get_test_assets(self) -> List[Dict[str, str]]:
        """
        Get test asset configurations
        
        Returns:
            List of test asset configurations
        """
        return self.config_data.get('test_assets', [])
    
    def get_core_users(self) -> List[Dict[str, Any]]:
        """
        Get core user configurations
        
        Returns:
            List of core user configurations
        """
        return self.config_data.get('core_users', [
            {
                "id": 1,
                "username": "admin",
                "email": "admin@assetmanagement.local",
                "is_active": True,
                "is_system": False,
                "is_admin": True,
                "password": "admin-password-change-me"
            },
            {
                "id": 2,
                "username": "system",
                "email": "system@assetmanagement.local",
                "is_active": True,
                "is_system": True,
                "is_admin": False,
                "password": "system-password-not-for-login"
            }
        ])
    
    def get_core_locations(self) -> List[Dict[str, Any]]:
        """
        Get core location configurations
        
        Returns:
            List of core location configurations
        """
        return self.config_data.get('core_locations', [
            {
                "name": "SanDiegoHQ",
                "description": "Main office location",
                "address": "San Diego, CA",
                "is_active": True
            }
        ])
    
    def get_core_asset_types(self) -> List[Dict[str, Any]]:
        """
        Get core asset type configurations
        
        Returns:
            List of core asset type configurations
        """
        return self.config_data.get('core_asset_types', [
            {
                "name": "Vehicle",
                "category": "Transportation",
                "description": "Motor vehicles for transportation",
                "is_active": True
            }
        ])
    
    def get_core_make_models(self) -> List[Dict[str, Any]]:
        """
        Get core make/model configurations
        
        Returns:
            List of core make/model configurations
        """
        return self.config_data.get('core_make_models', [
            {
                "make": "Toyota",
                "model": "Corolla",
                "year": 2023,
                "description": "Toyota Corolla 2023 model",
                "asset_type_name": "Vehicle",
                "is_active": True
            }
        ])
    
    def get_core_events(self) -> List[Dict[str, Any]]:
        """
        Get core event configurations
        
        Returns:
            List of core event configurations
        """
        return self.config_data.get('core_events', [
            {
                "event_type": "System",
                "description": "System initialized with core data",
                "user_username": "system"
            }
        ])
    
    def reload_config(self):
        """Reload configuration from file"""
        self._load_config()

    def load_core_data(self, include_assets=True):
        """
        Load core data into the database
        
        Args:
            include_assets (bool): Whether to include asset creation (default: True)
        
        Returns:
            bool: True if successful, False otherwise
        """
        print("=== Loading Core Data ===")
        
        try:
            from app import db
            from app.models.core.user import User
            from app.models.core.major_location import MajorLocation
            from app.models.core.asset_type import AssetType
            from app.models.core.make_model import MakeModel
            from app.models.core.asset import Asset
            from app.models.core.event import Event
            
            # Step 1: Create Users
            print("1. Creating Users...")
            users_created = {}
            for user_data in self.get_core_users():
                username = user_data['username']
                existing_user = User.query.filter_by(username=username).first()
                if not existing_user:
                    user = User(
                        id=user_data['id'],
                        username=user_data['username'],
                        email=user_data['email'],
                        is_active=user_data['is_active'],
                        is_system=user_data['is_system'],
                        is_admin=user_data['is_admin']
                    )
                    user.set_password(user_data['password'])
                    db.session.add(user)
                    db.session.commit()
                    print(f"   ✓ User '{username}' created (ID: {user_data['id']})")
                else:
                    print(f"   ✓ User '{username}' already exists (ID: {user_data['id']})")
                users_created[username] = existing_user or User.query.filter_by(username=username).first()
            
            # Step 2: Create Major Locations
            print("2. Creating Major Locations...")
            locations_created = {}
            for location_data in self.get_core_locations():
                name = location_data['name']
                existing_location = MajorLocation.query.filter_by(name=name).first()
                if not existing_location:
                    location = MajorLocation(
                        name=location_data['name'],
                        description=location_data['description'],
                        address=location_data['address'],
                        is_active=location_data['is_active'],
                        created_by_id=users_created['system'].id,
                        updated_by_id=users_created['system'].id
                    )
                    db.session.add(location)
                    db.session.commit()
                    print(f"   ✓ Location '{name}' created")
                else:
                    print(f"   ✓ Location '{name}' already exists")
                locations_created[name] = existing_location or MajorLocation.query.filter_by(name=name).first()
            
            # Step 3: Create Asset Types
            print("3. Creating Asset Types...")
            asset_types_created = {}
            for asset_type_data in self.get_core_asset_types():
                name = asset_type_data['name']
                existing_asset_type = AssetType.query.filter_by(name=name).first()
                if not existing_asset_type:
                    asset_type = AssetType(
                        name=asset_type_data['name'],
                        category=asset_type_data['category'],
                        description=asset_type_data['description'],
                        is_active=asset_type_data['is_active'],
                        created_by_id=users_created['system'].id,
                        updated_by_id=users_created['system'].id
                    )
                    db.session.add(asset_type)
                    db.session.commit()
                    print(f"   ✓ Asset Type '{name}' created")
                else:
                    print(f"   ✓ Asset Type '{name}' already exists")
                asset_types_created[name] = existing_asset_type or AssetType.query.filter_by(name=name).first()
            
            # Step 4: Create Make/Models
            print("4. Creating Make/Models...")
            make_models_created = {}
            for make_model_data in self.get_core_make_models():
                make = make_model_data['make']
                model = make_model_data['model']
                existing_make_model = MakeModel.query.filter_by(make=make, model=model).first()
                if not existing_make_model:
                    asset_type = asset_types_created[make_model_data['asset_type_name']]
                    make_model = MakeModel(
                        make=make_model_data['make'],
                        model=make_model_data['model'],
                        year=make_model_data['year'],
                        description=make_model_data['description'],
                        asset_type_id=asset_type.id,
                        is_active=make_model_data['is_active'],
                        created_by_id=users_created['system'].id,
                        updated_by_id=users_created['system'].id
                    )
                    db.session.add(make_model)
                    db.session.commit()
                    print(f"   ✓ Make/Model '{make} {model}' created")
                else:
                    print(f"   ✓ Make/Model '{make} {model}' already exists")
                make_models_created[f"{make}_{model}"] = existing_make_model or MakeModel.query.filter_by(make=make, model=model).first()
            
            # Step 5: Create Assets (if requested)
            if include_assets:
                assets_created = self.add_assets(users_created, locations_created, make_models_created)
            else:
                print("5. Skipping Asset Creation (will be handled by Phase 3)")
                assets_created = {}
            
            # Step 6: Create Events
            print("6. Creating Events...")
            for event_data in self.get_core_events():
                description = event_data['description']
                existing_event = Event.query.filter_by(description=description).first()
                if not existing_event:
                    user = users_created[event_data['user_username']]
                    # Use first asset as default
                    asset = list(assets_created.values())[0] if assets_created else None
                    location = list(locations_created.values())[0] if locations_created else None
                    
                    event = Event(
                        event_type=event_data['event_type'],
                        description=event_data['description'],
                        user_id=user.id,
                        asset_id=asset.id if asset else None,
                        major_location_id=location.id if location else None
                    )
                    db.session.add(event)
                    db.session.commit()
                    print(f"   ✓ Event '{description}' created")
                else:
                    print(f"   ✓ Event '{description}' already exists")
            
            print("\n=== Core Data Loading Complete ===")
            return True
            
        except Exception as e:
            print(f"\n=== Core Data Loading FAILED ===")
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()
            from app import db
            db.session.rollback()
            return False

    def add_assets(self, users_created, locations_created, make_models_created):
        """
        Add assets to the database
        
        Args:
            users_created (dict): Dictionary of created users
            locations_created (dict): Dictionary of created locations
            make_models_created (dict): Dictionary of created make/models
        
        Returns:
            dict: Dictionary of created assets
        """
        print("5. Creating Assets...")
        assets_created = {}
        
        try:
            from app.models.core.asset import Asset
            
            for asset_data in self.get_test_assets():
                serial_number = asset_data['serial_number']
                existing_asset = Asset.query.filter_by(serial_number=serial_number).first()
                if not existing_asset:
                    # Find the corresponding make/model
                    make_model_key = f"{asset_data['make']}_{asset_data['model']}"
                    make_model = make_models_created[make_model_key]
                    location = locations_created['SanDiegoHQ']  # Default location
                    
                    asset = Asset(
                        name=asset_data['name'],
                        serial_number=asset_data['serial_number'],
                        status="Active",
                        major_location_id=location.id,
                        make_model_id=make_model.id,
                        created_by_id=users_created['system'].id,
                        updated_by_id=users_created['system'].id
                    )
                    from app import db
                    db.session.add(asset)
                    db.session.commit()
                    print(f"   ✓ Asset '{asset_data['name']}' created")
                else:
                    print(f"   ✓ Asset '{asset_data['name']}' already exists")
                assets_created[serial_number] = existing_asset or Asset.query.filter_by(serial_number=serial_number).first()
            
            return assets_created
            
        except Exception as e:
            print(f"Error creating assets: {e}")
            return {}



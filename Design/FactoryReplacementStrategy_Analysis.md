# Factory Replacement Strategy - Design & Implementation

## Overview

**Goal**: Move business logic from data layer to business layer by implementing a factory replacement pattern that eliminates import dependencies between core and assets modules.

**Concept**: AssetContext has a static class attribute that holds a factory. Core provides a basic factory, and the assets module can replace it with an enhanced factory when imported.

## Design Principles

- **Dependency Inversion**: Core depends on abstraction (factory interface), not concrete implementation
- **Open/Closed**: AssetContext is open for extension (factory replacement) without modification
- **Module Independence**: Core module has zero imports from assets module
- **Reverse Dependency**: Assets module imports core (allowed direction)

## Architecture Components

1. **AssetFactoryBase** - Abstract factory interface (core)
2. **CoreAssetFactory** - Basic asset creation + events (core)
3. **AssetDetailsFactory** - Extended factory with detail insertion (assets)
4. **AssetContext.asset_factory** - Static class attribute for factory replacement
5. **Assets module registration** - Replaces factory on import

## Implementation

### 1. Factory Interface

```python
# app/buisness/core/asset_factory_base.py
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from app.data.core.asset_info.asset import Asset

class AssetFactoryBase(ABC):
    """Abstract base class for asset creation factories"""
    
    @abstractmethod
    def create_asset(
        self, 
        created_by_id: Optional[int] = None, 
        commit: bool = True, 
        enable_detail_insertion: bool = True,
        **kwargs
    ) -> Asset:
        """Create a new Asset with proper initialization"""
        pass
    
    @abstractmethod
    def create_asset_from_dict(
        self,
        asset_data: Dict[str, Any],
        created_by_id: Optional[int] = None,
        commit: bool = True,
        lookup_fields: Optional[list] = None
    ) -> tuple[Asset, bool]:
        """Create an asset from a dictionary, with optional find_or_create behavior"""
        pass
    
    def get_factory_type(self) -> str:
        """Get the factory type identifier"""
        return "unknown"
```

### 2. Core Asset Factory

```python
# app/buisness/core/core_asset_factory.py
from app.buisness.core.asset_factory_base import AssetFactoryBase
from app.data.core.asset_info.asset import Asset
from app.data.core.event_info.event import Event
from app import db
from app.logger import get_logger

logger = get_logger("asset_management.buisness.core")

class CoreAssetFactory(AssetFactoryBase):
    """Core asset factory - handles basic asset creation and event creation"""
    
    def create_asset(
        self, 
        created_by_id: Optional[int] = None, 
        commit: bool = True, 
        enable_detail_insertion: bool = True,  # Ignored in core factory
        **kwargs
    ) -> Asset:
        """Create asset with basic operations (validation, event creation)"""
        # Validate required fields
        if 'name' not in kwargs:
            raise ValueError("Asset name is required")
        if 'serial_number' not in kwargs:
            raise ValueError("Asset serial number is required")
        
        # Check for duplicate serial number
        existing_asset = Asset.query.filter_by(serial_number=kwargs['serial_number']).first()
        if existing_asset:
            raise ValueError(f"Asset with serial number '{kwargs['serial_number']}' already exists")
        
        # Set audit fields
        if created_by_id:
            kwargs['created_by_id'] = created_by_id
            kwargs['updated_by_id'] = created_by_id
        
        # Create asset
        asset = Asset(**kwargs)
        db.session.add(asset)
        db.session.flush()  # Get ID before creating event
        
        # Create creation event (business logic)
        self._create_creation_event(asset, created_by_id)
        
        # Commit if requested
        if commit:
            db.session.commit()
            logger.info(f"Asset created: {asset.name} (ID: {asset.id})")
        
        return asset
    
    def create_asset_from_dict(
        self,
        asset_data: Dict[str, Any],
        created_by_id: Optional[int] = None,
        commit: bool = True,
        lookup_fields: Optional[list] = None
    ) -> tuple[Asset, bool]:
        """Create asset from dictionary with optional find_or_create"""
        if lookup_fields:
            query_filters = {field: asset_data.get(field) for field in lookup_fields if field in asset_data}
            existing_asset = Asset.query.filter_by(**query_filters).first()
            if existing_asset:
                return existing_asset, False
        
        asset = self.create_asset(created_by_id=created_by_id, commit=commit, **asset_data)
        return asset, True
    
    def _create_creation_event(self, asset: Asset, user_id: Optional[int]):
        """Create asset creation event"""
        event = Event(
            event_type='Asset Created',
            description=f"Asset '{asset.name}' ({asset.serial_number}) was created",
            user_id=user_id,
            asset_id=asset.id,
            major_location_id=asset.major_location_id
        )
        db.session.add(event)
    
    def get_factory_type(self) -> str:
        """Return factory type identifier"""
        return "core"
```

### 3. Asset Details Factory

```python
# app/buisness/assets/asset_details_factory.py
from app.buisness.core.core_asset_factory import CoreAssetFactory
from app.data.core.asset_info.asset import Asset
from app.logger import get_logger

logger = get_logger("asset_management.buisness.assets")

class AssetDetailsFactory(CoreAssetFactory):
    """Extended factory that adds detail table creation"""
    
    def create_asset(
        self, 
        created_by_id: Optional[int] = None, 
        commit: bool = True, 
        enable_detail_insertion: bool = True,
        **kwargs
    ) -> Asset:
        """Create asset with detail table creation if enabled"""
        # Use parent to create asset and event
        asset = super().create_asset(
            created_by_id=created_by_id,
            commit=False,  # Don't commit yet, we may add details
            enable_detail_insertion=enable_detail_insertion,
            **kwargs
        )
        
        # Create detail rows if enabled
        if enable_detail_insertion:
            self._create_detail_rows(asset)
        
        # Now commit if requested
        if commit:
            from app import db
            db.session.commit()
            logger.info(f"Asset with details created: {asset.name} (ID: {asset.id})")
        
        return asset
    
    def _create_detail_rows(self, asset: Asset):
        """Create detail table rows for asset"""
        try:
            from app.buisness.assets.factories.asset_detail_factory import AssetDetailFactory
            AssetDetailFactory.create_detail_table_rows(asset)
        except Exception as e:
            logger.warning(f"Could not create detail rows for asset {asset.id}: {e}")
            # Don't fail asset creation if detail creation fails
    
    def get_factory_type(self) -> str:
        """Return factory type identifier"""
        return "detail factory"
```

### 4. AssetContext Enhancement

```python
# app/buisness/core/asset_context.py
from typing import List, Optional, Union, TYPE_CHECKING
from app.data.core.asset_info.asset import Asset
from app.data.core.event_info.event import Event

if TYPE_CHECKING:
    from app.buisness.core.asset_factory_base import AssetFactoryBase

class AssetContext:
    """
    Core context manager for asset operations.
    
    Uses a factory pattern for asset creation, allowing feature modules
    to replace the factory with enhanced versions.
    """
    
    # Static factory attribute - can be replaced by feature modules
    asset_factory: 'AssetFactoryBase' = None
    
    def __init__(self, asset: Union[Asset, int]):
        """Initialize AssetContext with an Asset instance or asset ID"""
        if isinstance(asset, int):
            self._asset = Asset.query.get_or_404(asset)
            self._asset_id = asset
        else:
            self._asset = asset
            self._asset_id = asset.id
        self._creation_event = None
    
    @classmethod
    def create(
        cls,
        created_by_id: Optional[int] = None,
        commit: bool = True,
        enable_detail_insertion: bool = True,
        **kwargs
    ) -> 'AssetContext':
        """
        Create a new asset using the configured factory
        
        Returns:
            AssetContext instance for the newly created asset
        """
        if cls.asset_factory is None:
            # Lazy initialization - use core factory if not set
            from app.buisness.core.core_asset_factory import CoreAssetFactory
            cls.asset_factory = CoreAssetFactory()
        
        asset = cls.asset_factory.create_asset(
            created_by_id=created_by_id,
            commit=commit,
            enable_detail_insertion=enable_detail_insertion,
            **kwargs
        )
        
        return cls(asset)
    
    @classmethod
    def get_factory_type(cls) -> str:
        """
        Get the type of the current factory (for debugging and introspection)
        
        Returns:
            str: Factory type identifier ("core", "detail factory", or "None")
        """
        if cls.asset_factory is None:
            return "None (will use CoreAssetFactory on first create)"
        return cls.asset_factory.get_factory_type()
    
    # ... rest of AssetContext methods remain the same ...
```

### 5. Assets Module Registration

```python
# app/buisness/assets/__init__.py
"""
Assets business logic module

This module extends core asset functionality with detail table management.
On import, it registers an enhanced asset factory with AssetContext.
"""

from app.buisness.core.asset_context import AssetContext
from app.buisness.assets.asset_details_factory import AssetDetailsFactory
from app.logger import get_logger

logger = get_logger("asset_management.buisness.assets")

# Register factory with type-aware guard (prevents duplicate registration)
if AssetContext.asset_factory is not None:
    current_type = AssetContext.asset_factory.get_factory_type()
    if current_type == "detail factory":
        # Already registered, skip (idempotent)
        logger.debug("AssetDetailsFactory already registered, skipping")
    else:
        # Factory exists but is not details factory (e.g., CoreAssetFactory)
        # Replace it with the enhanced version
        logger.debug(f"Replacing {current_type} factory with AssetDetailsFactory")
        AssetContext.asset_factory = AssetDetailsFactory()
        logger.debug("AssetDetailsFactory registered with AssetContext")
else:
    # No factory set yet, register the details factory
    AssetContext.asset_factory = AssetDetailsFactory()
    logger.debug("AssetDetailsFactory registered with AssetContext")
```

## Key Design Decisions

### Factory Initialization
- **Lazy Initialization**: Factory is created on first use if not set
- **Graceful Degradation**: Core factory used if assets module not imported
- **No Module-Level Init**: Avoids circular dependencies

### Factory Replacement Guard
- **Type-Aware**: Checks factory type, not just existence
- **Idempotent**: Multiple imports don't cause issues
- **Upgrade-Friendly**: Replaces core factory with details factory
- **Defensive**: Handles unknown factory types gracefully

### Module Independence
- **Core Module**: Zero imports from assets module
- **Assets Module**: Imports core (reverse dependency - allowed)
- **Factory Interface**: Core defines abstraction, assets implements extension

## Important Considerations

### Import Order
- Assets module should be imported early in application startup
- Import in `app/__init__.py` or route initialization before asset creation
- Lazy initialization ensures system works even if import order is wrong, but proper order ensures enhanced factory is used from start

### Factory Type Introspection
- `get_factory_type()` provides runtime introspection
- Useful for debugging and logging
- Returns human-readable identifiers ("core" vs "detail factory")

## Migration Path

1. **Phase 1**: Implement factory interface and core factory
2. **Phase 2**: Update AssetContext to use factory (add `create()` method)
3. **Phase 3**: Create AssetDetailsFactory in assets module
4. **Phase 4**: Register factory in assets/__init__.py
5. **Phase 5**: Update all asset creation to use `AssetContext.create()`
6. **Phase 6**: Remove event listeners from Asset model
7. **Phase 7**: Remove business logic from Asset model (enable/disable methods, create_detail_table_rows)

## Benefits

- ✅ **Eliminates Import Dependency**: Core module has zero imports from assets module
- ✅ **Clean Separation**: Business logic moved from data layer to business layer
- ✅ **Explicit Control**: No hidden event listeners, clear execution path
- ✅ **Extensible**: Easy to add more factory implementations
- ✅ **Backward Compatible**: Works even if assets module not imported
- ✅ **Observable**: Factory type is introspectable via `get_factory_type()`

## Dependency Flow

```
Core Module:
  - asset_context.py (defines AssetContext with factory attribute)
  - asset_factory_base.py (defines interface)
  - core_asset_factory.py (implements basic factory)
  
Assets Module:
  - __init__.py (imports AssetContext, replaces factory)
  - asset_details_factory.py (extends CoreAssetFactory)
  
Dependency Direction:
  Core ← Assets (reverse dependency, allowed)
  Core ↛ Assets (no forward dependency, achieved!)
```

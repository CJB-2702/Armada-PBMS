"""
Asset Context (Core)
Provides a clean interface for managing core asset operations.
Only uses models from app.models.core.* to maintain layer separation.

Handles:
- Basic asset information and relationships
- Event queries related to assets
- Core asset properties

Note: Detail table management is handled by AssetDetailsContext in domain.assets
"""

from typing import List, Optional, Union
from app.data.core.asset_info.asset import Asset
from app.data.core.event_info.event import Event


class AssetContext:
    """
    Core context manager for asset operations.
    
    Provides a clean interface for:
    - Accessing asset and related core models (MakeModel, MajorLocation, AssetType)
    - Querying events related to the asset
    - Accessing basic asset properties
    
    Uses only models from app.models.core.*
    """
    
    def __init__(self, asset: Union[Asset, int]):
        """
        Initialize AssetContext with an Asset instance or asset ID.
        
        Args:
            asset: Asset instance or asset ID
        """
        if isinstance(asset, int):
            self._asset = Asset.query.get_or_404(asset)
            self._asset_id = asset
        else:
            self._asset = asset
            self._asset_id = asset.id

        self._creation_event = None
    
    @property
    def asset(self) -> Asset:
        """Get the Asset instance"""
        return self._asset
    
    @property
    def asset_id(self) -> int:
        """Get the asset ID"""
        return self._asset_id
    
    @property
    def make_model(self):
        """Get the MakeModel instance for this asset"""
        return self._asset.make_model
    
    @property
    def major_location(self):
        """Get the MajorLocation instance for this asset"""
        return self._asset.major_location
    
    @property
    def asset_type_id(self) -> Optional[int]:
        """Get the asset type ID through the make_model relationship"""
        return self._asset.asset_type_id
    
    @property
    def asset_type(self):
        """Get the AssetType instance for this asset"""
        if self._asset.asset_type_id and self._asset.make_model:
            return self._asset.make_model.asset_type
        return None
    
    @property
    def creation_event(self) -> Optional[Event]:
        """
        Get the creation event for this asset.
        
        Returns:
            Event instance for asset creation, or None if not found
        """
        if self._creation_event is None:
            # Find the "Asset Created" event for this asset
            self._creation_event = Event.query.filter_by(
                asset_id=self._asset_id,
                event_type='Asset Created'
            ).order_by(Event.timestamp.asc()).first()
        return self._creation_event
    
    def recent_events(self, limit: int = 10) -> List[Event]:
        """
        Get recent events for this asset, ordered by timestamp (newest first).
        
        Args:
            limit: Maximum number of events to return (default: 10)
            
        Returns:
            List of Event instances
        """
        return Event.query.filter_by(asset_id=self._asset_id).order_by(Event.timestamp.desc()).limit(limit).all()
    
    def refresh(self):
        """Refresh cached data from database"""
        self._creation_event = None
    
    def __repr__(self):
        return f'<AssetContext asset_id={self._asset_id}>'


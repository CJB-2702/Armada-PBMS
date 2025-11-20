"""
MakeModel Context (Core)
Provides a clean interface for managing core make/model operations.
Only uses models from app.models.core.* to maintain layer separation.

Handles:
- Basic make/model information and relationships
- Event queries related to models
- Core make/model properties

Note: Detail table management is handled by MakeModelDetailsContext in domain.assets
"""

from typing import List, Optional, Union
from app.data.core.asset_info.make_model import MakeModel
from app.data.core.asset_info.asset import Asset
from app.data.core.event_info.event import Event


class MakeModelContext:
    """
    Core context manager for make/model operations.
    
    Provides a clean interface for:
    - Accessing make/model and related core models (AssetType)
    - Querying events related to the model
    - Accessing assets of this model type
    - Core make/model properties
    
    Uses only models from app.models.core.*
    """
    
    def __init__(self, model: Union[MakeModel, int]):
        """
        Initialize MakeModelContext with a MakeModel instance or model ID.
        
        Args:
            model: MakeModel instance or model ID
        """
        if isinstance(model, int):
            self._model = MakeModel.query.get_or_404(model)
            self._model_id = model
        else:
            self._model = model
            self._model_id = model.id
        
        self._creation_event = None
    
    @property
    def model(self) -> MakeModel:
        """Get the MakeModel instance"""
        return self._model
    
    @property
    def model_id(self) -> int:
        """Get the model ID"""
        return self._model_id
    
    @property
    def creation_event(self) -> Optional[Event]:
        """
        Get the creation event for this model.
        
        Returns:
            Event instance for model creation, or None if not found
        """
        if self._creation_event is None:
            # Find the "Model Created" event for this model
            # Since models don't have a direct model_id in events, we search by description pattern
            # The event description format is: "Model '{make} {model}' ({year}) was created"
            description_pattern = f"Model '{self._model.make} {self._model.model}'"
            if self._model.year:
                description_pattern += f" ({self._model.year})"
            
            self._creation_event = Event.query.filter(
                Event.event_type == 'Model Created',
                Event.description.like(f"{description_pattern}%")
            ).order_by(Event.timestamp.asc()).first()
        return self._creation_event
    
    def get_assets(self) -> List[Asset]:
        """
        Get all assets of this model type.
        
        Note: This does not store asset references in memory, just returns a list.
        Each call queries the database fresh.
        
        Returns:
            List of Asset instances for this model
        """
        return Asset.query.filter_by(make_model_id=self._model_id).order_by(Asset.created_at.desc()).all()
    
    @property
    def asset_count(self) -> int:
        """Get the count of assets using this model"""
        return Asset.query.filter_by(make_model_id=self._model_id).count()
    
    @property
    def asset_type(self):
        """Get the AssetType instance for this model"""
        return self._model.asset_type
    
    @property
    def asset_type_id(self) -> Optional[int]:
        """Get the asset type ID"""
        return self._model.asset_type_id
    
    def refresh(self):
        """Refresh cached data from database"""
        self._creation_event = None
    
    def __repr__(self):
        return f'<MakeModelContext model_id={self._model_id} asset_count={self.asset_count}>'



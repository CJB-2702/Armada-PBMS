"""
Maintenance Action Set Context
Provides a clean interface for managing maintenance action sets, their actions, events, and related data.
Wraps MaintenanceEvent to provide a context-manager-like interface consistent with AssetContext pattern.
"""

from typing import List, Dict, Any, Optional, Union
from app import db
from app.data.maintenance.base.maintenance_action_set import MaintenanceActionSet
from app.data.maintenance.base.action import Action
from app.data.core.asset_info.asset import Asset
from app.data.core.event_info.event import Event
from app.buisness.maintenance.maintenance_event import MaintenanceEvent
from app.buisness.core.event_context import EventContext


class MaintenanceActionSetContext:
    """
    Context manager for maintenance action set operations.
    
    Provides a clean interface for:
    - Accessing action set, asset, maintenance plan, event, actions
    - Aggregating part demand information with inventory availability
    - Accessing related comments and attachments
    
    Uses MaintenanceEvent internally but provides consistent context manager interface.
    """
    
    def __init__(self, action_set: Union[MaintenanceActionSet, int]):
        """
        Initialize MaintenanceActionSetContext with a MaintenanceActionSet instance or ID.
        
        Args:
            action_set: MaintenanceActionSet instance or action set ID
        """
        if isinstance(action_set, int):
            self._action_set = MaintenanceActionSet.query.get_or_404(action_set)
            self._action_set_id = action_set
        else:
            self._action_set = action_set
            self._action_set_id = action_set.id
        
        # Wrap MaintenanceEvent for convenience
        self._maintenance_event = MaintenanceEvent(self._action_set)
        
        # Cache for lazy loading
        self._event_context = None
        self._part_demand_info = None
    
    @property
    def action_set(self) -> MaintenanceActionSet:
        """Get the MaintenanceActionSet instance"""
        return self._action_set
    
    @property
    def action_set_id(self) -> int:
        """Get the action set ID"""
        return self._action_set_id
    
    @property
    def maintenance_event(self) -> MaintenanceEvent:
        """Get the wrapped MaintenanceEvent instance"""
        return self._maintenance_event
    
    @property
    def asset(self) -> Optional[Asset]:
        """Get the associated Asset"""
        if self._action_set.asset_id:
            return self._action_set.asset
        return None
    
    @property
    def maintenance_plan(self):
        """Get the associated MaintenancePlan"""
        return self._action_set.maintenance_plan
    
    @property
    def template_action_set(self):
        """Get the associated TemplateActionSet"""
        return self._action_set.template_action_set
    
    @property
    def event(self) -> Optional[Event]:
        """Get the associated Event"""
        return self._maintenance_event.event
    
    @property
    def actions(self) -> List[Action]:
        """Get all actions linked to this maintenance action set, ordered by sequence"""
        return self._maintenance_event.actions
    
    @property
    def comments(self) -> List[Comment]:
        """Get all comments for the associated event"""
        if self._event_context is None and self.event:
            self._event_context = EventContext(self.event.id)
        if self._event_context:
            return self._event_context.comments
        return []
    
    def get_part_demand_info(self) -> List[Dict[str, Any]]:
        """
        Get part demand information with inventory availability.
        
        Returns:
            List of dictionaries containing part demand info with availability data
        """
        if self._part_demand_info is None:
            self._part_demand_info = []
            try:
                from app.buisness.inventory.managers import PartDemandManager
                
                for action in self.actions:
                    if hasattr(action, 'part_demands'):
                        for demand in action.part_demands:
                            # Check inventory availability
                            availability = PartDemandManager.check_inventory_availability(demand.id)
                            
                            self._part_demand_info.append({
                                'demand': demand,
                                'action': action,
                                'availability': availability
                            })
            except ImportError:
                # Phase 6 inventory system not available yet
                pass
        
        return self._part_demand_info
    
    @property
    def part_demand_info(self) -> List[Dict[str, Any]]:
        """Get part demand information with inventory availability (property access)"""
        return self.get_part_demand_info()
    
    def get_part_demand_statistics(self) -> Dict[str, int]:
        """
        Get statistics about part demands.
        
        Returns:
            Dictionary with total_parts_needed, parts_available, parts_need_purchase
        """
        part_demand_info = self.get_part_demand_info()
        
        total_parts_needed = len(part_demand_info)
        parts_available = 0
        parts_need_purchase = 0
        
        for item in part_demand_info:
            availability = item.get('availability', {})
            if availability.get('can_fulfill_from_any'):
                parts_available += 1
            if availability.get('needs_purchase'):
                parts_need_purchase += 1
        
        return {
            'total_parts_needed': total_parts_needed,
            'parts_available': parts_available,
            'parts_need_purchase': parts_need_purchase
        }
    
    def refresh(self):
        """Refresh all data from database"""
        self._maintenance_event.refresh()
        self._part_demand_info = None
        self._event_context = None
    
    # Convenience properties from MaintenanceEvent
    @property
    def total_actions(self) -> int:
        """Get total number of actions"""
        return self._maintenance_event.total_actions
    
    @property
    def completed_actions(self) -> int:
        """Get number of completed actions"""
        return self._maintenance_event.completed_actions
    
    @property
    def pending_actions(self) -> int:
        """Get number of pending actions"""
        return self._maintenance_event.pending_actions
    
    @property
    def in_progress_actions(self) -> int:
        """Get number of in-progress actions"""
        return self._maintenance_event.in_progress_actions
    
    @property
    def completion_percentage(self) -> float:
        """Calculate completion percentage based on actions"""
        return self._maintenance_event.completion_percentage



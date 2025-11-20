"""
Action Context
Provides a clean interface for managing actions and their related data.
"""

from typing import List, Optional, Union
from app import db
from app.data.maintenance.base.action import Action
from app.data.maintenance.base.maintenance_action_set import MaintenanceActionSet
from app.data.maintenance.base.part_demand import PartDemand


class ActionContext:
    """
    Context manager for action operations.
    
    Provides a clean interface for:
    - Accessing action, maintenance action set, template action item, part demands
    """
    
    def __init__(self, action: Union[Action, int]):
        """
        Initialize ActionContext with an Action instance or ID.
        
        Args:
            action: Action instance or action ID
        """
        if isinstance(action, int):
            self._action = Action.query.get_or_404(action)
            self._action_id = action
        else:
            self._action = action
            self._action_id = action.id
        
        # Cache for lazy loading
        self._part_demands = None
    
    @property
    def action(self) -> Action:
        """Get the Action instance"""
        return self._action
    
    @property
    def action_id(self) -> int:
        """Get the action ID"""
        return self._action_id
    
    @property
    def maintenance_action_set(self) -> Optional[MaintenanceActionSet]:
        """Get the associated MaintenanceActionSet"""
        return self._action.maintenance_action_set
    
    @property
    def template_action_item(self):
        """Get the associated TemplateActionItem"""
        return self._action.template_action_item
    
    @property
    def part_demands(self) -> List[PartDemand]:
        """Get all part demands for this action"""
        if self._part_demands is None:
            self._part_demands = list(self._action.part_demands) if hasattr(self._action, 'part_demands') else []
        return self._part_demands
    
    def get_part_demands(self) -> List[PartDemand]:
        """
        Get all part demands for this action.
        
        Returns:
            List of PartDemand instances
        """
        return self.part_demands
    
    @property
    def part_demand_count(self) -> int:
        """Get the count of part demands for this action"""
        return len(self.part_demands)



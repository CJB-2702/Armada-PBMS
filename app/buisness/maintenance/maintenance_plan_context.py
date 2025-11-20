"""
Maintenance Plan Context
Provides a clean interface for managing maintenance plans and their related data.
"""

from typing import List, Optional, Union
from app import db
from app.data.maintenance.base.maintenance_plan import MaintenancePlan
from app.data.maintenance.base.maintenance_action_set import MaintenanceActionSet
from app.data.core.asset_info.asset_type import AssetType
from app.data.core.asset_info.make_model import MakeModel


class MaintenancePlanContext:
    """
    Context manager for maintenance plan operations.
    
    Provides a clean interface for:
    - Accessing plan, asset type, model, template action set
    - Accessing related maintenance action sets
    """
    
    def __init__(self, plan: Union[MaintenancePlan, int]):
        """
        Initialize MaintenancePlanContext with a MaintenancePlan instance or ID.
        
        Args:
            plan: MaintenancePlan instance or plan ID
        """
        if isinstance(plan, int):
            self._plan = MaintenancePlan.query.get_or_404(plan)
            self._plan_id = plan
        else:
            self._plan = plan
            self._plan_id = plan.id
        
        # Cache for lazy loading
        self._maintenance_action_sets = None
    
    @property
    def plan(self) -> MaintenancePlan:
        """Get the MaintenancePlan instance"""
        return self._plan
    
    @property
    def plan_id(self) -> int:
        """Get the plan ID"""
        return self._plan_id
    
    @property
    def asset_type(self) -> Optional[AssetType]:
        """Get the associated AssetType"""
        return self._plan.asset_type
    
    @property
    def model(self) -> Optional[MakeModel]:
        """Get the associated MakeModel"""
        return self._plan.model
    
    @property
    def template_action_set(self):
        """Get the associated TemplateActionSet"""
        return self._plan.template_action_set
    
    @property
    def maintenance_action_sets(self) -> List[MaintenanceActionSet]:
        """Get all maintenance action sets for this plan"""
        if self._maintenance_action_sets is None:
            self._maintenance_action_sets = MaintenanceActionSet.query.filter_by(
                maintenance_plan_id=self._plan_id
            ).order_by(MaintenanceActionSet.created_at.desc()).all()
        return self._maintenance_action_sets
    
    def get_recent_action_sets(self, limit: int = 10) -> List[MaintenanceActionSet]:
        """
        Get recent maintenance action sets for this plan.
        
        DEPRECATED: This method is deprecated. Use MaintenancePlanService.get_recent_action_sets() instead.
        Kept for backward compatibility but delegates to service layer.
        
        Args:
            limit: Maximum number of action sets to return
            
        Returns:
            List of recent MaintenanceActionSet instances
        """
        # Import here to avoid circular import
        from app.services.maintenance.maintenance_plan_service import MaintenancePlanService
        return MaintenancePlanService.get_recent_action_sets(self._plan_id, limit)
    
    @property
    def action_set_count(self) -> int:
        """Get the count of maintenance action sets for this plan"""
        return len(self.maintenance_action_sets)





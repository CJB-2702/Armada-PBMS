"""
Maintenance Plan Service
Presentation service for maintenance plan data retrieval and formatting.
"""

from typing import Dict, List, Optional, Tuple, Any
from flask_sqlalchemy.pagination import Pagination
from app.data.maintenance.base.maintenance_plan import MaintenancePlan
from app.data.maintenance.base.maintenance_action_set import MaintenanceActionSet
from app.data.core.asset_info.asset_type import AssetType
from app.data.core.asset_info.make_model import MakeModel
from app.data.maintenance.templates.template_action_set import TemplateActionSet


class MaintenancePlanService:
    """
    Service for maintenance plan presentation data.
    
    Provides methods for:
    - Building filtered maintenance plan queries
    - Retrieving form options
    - Getting recent action sets
    """
    
    @staticmethod
    def get_list_data(
        page: int = 1,
        per_page: int = 20,
        asset_type_id: Optional[int] = None,
        model_id: Optional[int] = None,
        status: Optional[str] = None,
        frequency_type: Optional[str] = None,
        name: Optional[str] = None
    ) -> Tuple[Pagination, Dict[str, Any]]:
        """
        Get paginated maintenance plans with filters and form options.
        
        Args:
            page: Page number
            per_page: Items per page
            asset_type_id: Filter by asset type
            model_id: Filter by model
            status: Filter by status
            frequency_type: Filter by frequency type
            name: Filter by name (partial match)
            
        Returns:
            Tuple of (pagination_object, form_options_dict)
        """
        query = MaintenancePlan.query
        
        if asset_type_id:
            query = query.filter(MaintenancePlan.asset_type_id == asset_type_id)
        
        if model_id:
            query = query.filter(MaintenancePlan.model_id == model_id)
        
        if status:
            query = query.filter(MaintenancePlan.status == status)
        
        if frequency_type:
            query = query.filter(MaintenancePlan.frequency_type == frequency_type)
        
        if name:
            query = query.filter(MaintenancePlan.name.ilike(f'%{name}%'))
        
        # Order by creation date (newest first)
        query = query.order_by(MaintenancePlan.created_at.desc())
        
        # Pagination
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Get form options
        form_options = {
            'asset_types': AssetType.query.all(),
            'make_models': MakeModel.query.all()
        }
        
        return pagination, form_options
    
    @staticmethod
    def get_form_options() -> Dict[str, List]:
        """
        Get form options for create/edit forms.
        
        Returns:
            Dictionary with asset_types, make_models, and template_action_sets
        """
        return {
            'asset_types': AssetType.query.all(),
            'make_models': MakeModel.query.all(),
            'template_action_sets': TemplateActionSet.query.all()
        }
    
    @staticmethod
    def get_recent_action_sets(plan_id: int, limit: int = 10) -> List[MaintenanceActionSet]:
        """
        Get recent action sets for a maintenance plan.
        
        Args:
            plan_id: The maintenance plan ID
            limit: Maximum number of action sets to return
            
        Returns:
            List of recent maintenance action sets
        """
        return MaintenanceActionSet.query.filter_by(
            maintenance_plan_id=plan_id
        ).order_by(
            MaintenanceActionSet.created_at.desc()
        ).limit(limit).all()


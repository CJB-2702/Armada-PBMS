"""
Maintenance Action Set Service
Presentation service for maintenance action set data retrieval and formatting.
"""

from typing import Dict, List, Optional, Tuple, Any
from flask_sqlalchemy.pagination import Pagination
from sqlalchemy.orm import joinedload
from app.data.maintenance.base.maintenance_action_set import MaintenanceActionSet
from app.data.maintenance.templates.template_action_item import TemplateActionItem
from app.data.core.asset_info.asset import Asset
from app.data.core.asset_info.make_model import MakeModel
from app.data.core.major_location import MajorLocation
from app.data.maintenance.templates.template_action_set import TemplateActionSet
from app.data.maintenance.base.maintenance_plan import MaintenancePlan


class MaintenanceActionSetService:
    """
    Service for maintenance action set presentation data.
    
    Provides methods for:
    - Building filtered action set queries with complex joins
    - Retrieving form options
    - Searching template action items
    """
    
    @staticmethod
    def get_list_data(
        page: int = 1,
        per_page: int = 20,
        asset_id: Optional[str] = None,  # String for partial match
        location: Optional[str] = None,
        maintenance_plan_id: Optional[int] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        task_name: Optional[str] = None
    ) -> Tuple[Pagination, Dict[str, Any]]:
        """
        Get paginated action sets with filters and form options.
        
        Args:
            page: Page number
            per_page: Items per page
            asset_id: Filter by asset name (partial match, string)
            location: Filter by location name (partial match)
            maintenance_plan_id: Filter by maintenance plan
            status: Filter by status
            priority: Filter by priority
            task_name: Filter by task name (partial match)
            
        Returns:
            Tuple of (pagination_object, form_options_dict)
        """
        query = MaintenanceActionSet.query
        
        # Filter by asset name (starts with) through asset relationship
        if asset_id:
            query = query.join(Asset, MaintenanceActionSet.asset_id == Asset.id).filter(
                Asset.name.ilike(f'{asset_id}%')
            )
        
        # Filter by location name through asset relationship
        if location:
            # Only join Asset if we haven't already
            if not asset_id:
                query = query.join(Asset, MaintenanceActionSet.asset_id == Asset.id)
            
            query = query.join(
                MajorLocation, Asset.major_location_id == MajorLocation.id
            ).filter(MajorLocation.name.ilike(f'%{location}%'))
        
        if maintenance_plan_id:
            query = query.filter(MaintenanceActionSet.maintenance_plan_id == maintenance_plan_id)
        
        if status:
            query = query.filter(MaintenanceActionSet.status == status)
        
        if priority:
            query = query.filter(MaintenanceActionSet.priority == priority)
        
        if task_name:
            query = query.filter(MaintenanceActionSet.task_name.ilike(f'%{task_name}%'))
        
        # Order by scheduled date (most recent first)
        query = query.order_by(MaintenanceActionSet.scheduled_date.desc())
        
        # Eager load asset and major_location relationships to avoid N+1 queries
        query = query.options(
            joinedload(MaintenanceActionSet.asset).joinedload(Asset.major_location)
        )
        
        # Pagination
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Get form options
        form_options = {
            'assets': Asset.query.all(),
            'maintenance_plans': MaintenancePlan.query.all()
        }
        
        return pagination, form_options
    
    @staticmethod
    def get_form_options() -> Dict[str, List]:
        """
        Get form options for create/edit forms.
        
        Returns:
            Dictionary with assets, template_action_sets, and maintenance_plans
        """
        return {
            'assets': Asset.query.all(),
            'template_action_sets': TemplateActionSet.query.all(),
            'maintenance_plans': MaintenancePlan.query.all()
        }
    
    @staticmethod
    def search_template_action_items(
        search_query: Optional[str] = None,
        page: int = 1,
        page_size: int = 16
    ) -> List[TemplateActionItem]:
        """
        Search template action items for HTMX endpoint.
        
        Args:
            search_query: Search string for action name or description
            page: Page number
            page_size: Items per page
            
        Returns:
            List of template action items
        """
        query = TemplateActionItem.query
        
        if search_query:
            like = f'%{search_query}%'
            query = query.filter(
                (TemplateActionItem.action_name.ilike(like))
                | (TemplateActionItem.description.ilike(like))
            )
        
        query = query.order_by(TemplateActionItem.action_name.asc())
        return query.limit(page_size).offset((page - 1) * page_size).all()


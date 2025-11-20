"""
Part Demand Service
Presentation service for part demand data retrieval and formatting.
"""

from typing import Dict, List, Optional, Tuple, Any
from flask_sqlalchemy.pagination import Pagination
from sqlalchemy.orm import joinedload
from app import db
from app.data.maintenance.base.part_demand import PartDemand
from app.data.maintenance.base.action import Action
from app.data.maintenance.base.maintenance_action_set import MaintenanceActionSet
from app.data.maintenance.templates.template_part_demand import TemplatePartDemand
from app.data.supply_items.part import Part


class PartDemandService:
    """
    Service for part demand presentation data.
    
    Provides methods for:
    - Building filtered part demand queries with eager loading
    - Retrieving form options
    - Getting distinct statuses
    """
    
    @staticmethod
    def get_list_data(
        page: int = 1,
        per_page: int = 20,
        action_id: Optional[int] = None,
        action_set_id: Optional[int] = None,
        part_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> Tuple[Pagination, Dict[str, Any]]:
        """
        Get paginated part demands with filters and form options.
        
        Args:
            page: Page number
            per_page: Items per page
            action_id: Filter by action
            action_set_id: Filter by action set
            part_id: Filter by part
            status: Filter by status
            
        Returns:
            Tuple of (pagination_object, form_options_dict)
        """
        # Build query with eager loading for better performance
        query = PartDemand.query.options(
            joinedload(PartDemand.action).joinedload(Action.maintenance_action_set),
            joinedload(PartDemand.part)
        )
        
        # Apply filters
        if action_id:
            query = query.filter(PartDemand.action_id == action_id)
        
        if action_set_id:
            query = query.join(Action).filter(Action.maintenance_action_set_id == action_set_id)
        
        if part_id:
            query = query.filter(PartDemand.part_id == part_id)
        
        if status:
            query = query.filter(PartDemand.status == status)
        
        # Order by creation date (newest first)
        query = query.order_by(PartDemand.created_at.desc())
        
        # Pagination
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Get form options
        form_options = {
            'actions': Action.query.order_by(Action.action_name).all(),
            'action_sets': MaintenanceActionSet.query.order_by(MaintenanceActionSet.task_name).all(),
            'parts': Part.query.order_by(Part.part_name).all(),
            'statuses': PartDemandService.get_distinct_statuses()
        }
        
        return pagination, form_options
    
    @staticmethod
    def get_form_options() -> Dict[str, List]:
        """
        Get form options for create/edit forms.
        
        Returns:
            Dictionary with actions, parts, and template_part_demands
        """
        return {
            'actions': Action.query.all(),
            'parts': Part.query.all(),
            'template_part_demands': TemplatePartDemand.query.all()
        }
    
    @staticmethod
    def get_distinct_statuses() -> List[str]:
        """
        Get all distinct status values for filtering.
        
        Returns:
            List of distinct status strings
        """
        statuses = db.session.query(PartDemand.status).distinct().all()
        return [s[0] for s in statuses if s[0]]


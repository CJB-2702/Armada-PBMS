"""
Action Service
Presentation service for action data retrieval and formatting.
"""

from typing import Dict, List, Optional, Tuple, Any
from flask_sqlalchemy.pagination import Pagination
from app.data.maintenance.base.action import Action
from app.data.maintenance.base.maintenance_action_set import MaintenanceActionSet
from app.data.maintenance.templates.template_action_item import TemplateActionItem


class ActionService:
    """
    Service for action presentation data.
    
    Provides methods for:
    - Building filtered action queries
    - Retrieving form options
    """
    
    @staticmethod
    def get_list_data(
        page: int = 1,
        per_page: int = 20,
        status: Optional[str] = None,
        maintenance_action_set_id: Optional[int] = None,
        action_name: Optional[str] = None
    ) -> Tuple[Pagination, Dict[str, Any]]:
        """
        Get paginated actions with filters and form options.
        
        Args:
            page: Page number
            per_page: Items per page
            status: Filter by status
            maintenance_action_set_id: Filter by maintenance action set
            action_name: Filter by action name (partial match)
            
        Returns:
            Tuple of (pagination_object, form_options_dict)
        """
        query = Action.query
        
        if status:
            query = query.filter(Action.status == status)
        
        if maintenance_action_set_id:
            query = query.filter(Action.maintenance_action_set_id == maintenance_action_set_id)
        
        if action_name:
            query = query.filter(Action.action_name.ilike(f'%{action_name}%'))
        
        # Order by creation date (newest first)
        query = query.order_by(Action.created_at.desc())
        
        # Pagination
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Get form options
        form_options = {
            'maintenance_action_sets': MaintenanceActionSet.query.all()
        }
        
        return pagination, form_options
    
    @staticmethod
    def get_form_options() -> Dict[str, List]:
        """
        Get form options for create form.
        
        Returns:
            Dictionary with maintenance_action_sets and template_action_items
        """
        return {
            'maintenance_action_sets': MaintenanceActionSet.query.all(),
            'template_action_items': TemplateActionItem.query.all()
        }


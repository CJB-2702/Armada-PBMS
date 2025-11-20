"""
Template Action Item Service
Presentation service for template action item data retrieval and formatting.
"""

from typing import Dict, List, Optional, Tuple, Any
from flask_sqlalchemy.pagination import Pagination
from app.data.maintenance.templates.template_action_item import TemplateActionItem
from app.data.maintenance.templates.template_action_set import TemplateActionSet
from app.data.maintenance.templates.template_part_demand import TemplatePartDemand
from app.data.maintenance.templates.template_action_tool import TemplateActionTool


class TemplateActionItemService:
    """
    Service for template action item presentation data.
    
    Provides methods for:
    - Building filtered template action item queries
    - Retrieving form options
    - Getting related data for detail views
    """
    
    @staticmethod
    def get_list_data(
        page: int = 1,
        per_page: int = 20,
        template_action_set_id: Optional[int] = None,
        action_name: Optional[str] = None,
        is_required: Optional[bool] = None
    ) -> Tuple[Pagination, Dict[str, Any]]:
        """
        Get paginated template action items with filters and form options.
        
        Args:
            page: Page number
            per_page: Items per page
            template_action_set_id: Filter by template action set
            action_name: Filter by action name (partial match)
            is_required: Filter by required status
            
        Returns:
            Tuple of (pagination_object, form_options_dict)
        """
        query = TemplateActionItem.query
        
        if template_action_set_id:
            query = query.filter(TemplateActionItem.template_action_set_id == template_action_set_id)
        
        if action_name:
            query = query.filter(TemplateActionItem.action_name.ilike(f'%{action_name}%'))
        
        if is_required is not None:
            query = query.filter(TemplateActionItem.is_required == is_required)
        
        # Order by creation date (newest first)
        query = query.order_by(TemplateActionItem.created_at.desc())
        
        # Pagination
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Get form options
        form_options = {
            'template_action_sets': TemplateActionSet.query.all()
        }
        
        return pagination, form_options
    
    @staticmethod
    def get_form_options() -> Dict[str, List]:
        """
        Get form options for create/edit forms.
        
        Returns:
            Dictionary with template_action_sets
        """
        return {
            'template_action_sets': TemplateActionSet.query.all()
        }
    
    @staticmethod
    def get_related_data(template_action_item_id: int) -> Dict[str, Any]:
        """
        Get related part demands and tools for detail view.
        
        Args:
            template_action_item_id: The template action item ID
            
        Returns:
            Dictionary with template_part_demands and template_action_tools
        """
        return {
            'template_part_demands': TemplatePartDemand.query.filter_by(
                template_action_item_id=template_action_item_id
            ).all(),
            'template_action_tools': TemplateActionTool.query.filter_by(
                template_action_item_id=template_action_item_id
            ).all()
        }


"""
Template Action Tool Service
Presentation service for template action tool data retrieval and formatting.
"""

from typing import Dict, List, Optional, Tuple, Any
from flask_sqlalchemy.pagination import Pagination
from app.data.maintenance.templates.template_action_tool import TemplateActionTool
from app.data.maintenance.templates.template_action_item import TemplateActionItem
from app.data.supply_items.tool import Tool


class TemplateActionToolService:
    """
    Service for template action tool presentation data.
    
    Provides methods for:
    - Building filtered template action tool queries
    - Retrieving form options
    """
    
    @staticmethod
    def get_list_data(
        page: int = 1,
        per_page: int = 20,
        template_action_item_id: Optional[int] = None,
        tool_id: Optional[int] = None,
        is_required: Optional[bool] = None
    ) -> Tuple[Pagination, Dict[str, Any]]:
        """
        Get paginated template action tools with filters and form options.
        
        Args:
            page: Page number
            per_page: Items per page
            template_action_item_id: Filter by template action item
            tool_id: Filter by tool
            is_required: Filter by required status
            
        Returns:
            Tuple of (pagination_object, form_options_dict)
        """
        query = TemplateActionTool.query
        
        if template_action_item_id:
            query = query.filter(TemplateActionTool.template_action_item_id == template_action_item_id)
        
        if tool_id:
            query = query.filter(TemplateActionTool.tool_id == tool_id)
        
        if is_required is not None:
            query = query.filter(TemplateActionTool.is_required == is_required)
        
        # Order by creation date (newest first)
        query = query.order_by(TemplateActionTool.created_at.desc())
        
        # Pagination
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Get form options
        form_options = {
            'template_action_items': TemplateActionItem.query.all(),
            'tools': Tool.query.all()
        }
        
        return pagination, form_options
    
    @staticmethod
    def get_form_options() -> Dict[str, List]:
        """
        Get form options for create/edit forms.
        
        Returns:
            Dictionary with template_action_items and tools
        """
        return {
            'template_action_items': TemplateActionItem.query.all(),
            'tools': Tool.query.all()
        }


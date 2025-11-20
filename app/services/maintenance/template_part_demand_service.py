"""
Template Part Demand Service
Presentation service for template part demand data retrieval and formatting.
"""

from typing import Dict, List, Optional, Tuple, Any
from flask_sqlalchemy.pagination import Pagination
from sqlalchemy.orm import joinedload
from app.data.maintenance.templates.template_part_demand import TemplatePartDemand
from app.data.maintenance.templates.template_action_item import TemplateActionItem
from app.data.supply_items.part import Part


class TemplatePartDemandService:
    """
    Service for template part demand presentation data.
    
    Provides methods for:
    - Building filtered template part demand queries
    - Retrieving form options
    """
    
    @staticmethod
    def get_list_data(
        page: int = 1,
        per_page: int = 20,
        template_action_item_id: Optional[int] = None,
        part_id: Optional[int] = None,
        is_optional: Optional[bool] = None
    ) -> Tuple[Pagination, Dict[str, Any]]:
        """
        Get paginated template part demands with filters and form options.
        
        Args:
            page: Page number
            per_page: Items per page
            template_action_item_id: Filter by template action item
            part_id: Filter by part
            is_optional: Filter by optional status
            
        Returns:
            Tuple of (pagination_object, form_options_dict)
        """
        query = TemplatePartDemand.query.options(
            joinedload(TemplatePartDemand.template_action_item),
            joinedload(TemplatePartDemand.part)
        )
        
        if template_action_item_id:
            query = query.filter(TemplatePartDemand.template_action_item_id == template_action_item_id)
        
        if part_id:
            query = query.filter(TemplatePartDemand.part_id == part_id)
        
        if is_optional is not None:
            query = query.filter(TemplatePartDemand.is_optional == is_optional)
        
        # Order by creation date (newest first)
        query = query.order_by(TemplatePartDemand.created_at.desc())
        
        # Pagination
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Get form options
        form_options = {
            'template_action_items': TemplateActionItem.query.all(),
            'parts': Part.query.all()
        }
        
        return pagination, form_options
    
    @staticmethod
    def get_form_options() -> Dict[str, List]:
        """
        Get form options for create/edit forms.
        
        Returns:
            Dictionary with template_action_items and parts
        """
        return {
            'template_action_items': TemplateActionItem.query.all(),
            'parts': Part.query.all()
        }


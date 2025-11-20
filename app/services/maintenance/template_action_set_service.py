"""
Template Action Set Service
Presentation service for template action set data retrieval and formatting.
"""

from typing import Optional
from flask_sqlalchemy.pagination import Pagination
from app.data.maintenance.templates.template_action_set import TemplateActionSet


class TemplateActionSetService:
    """
    Service for template action set presentation data.
    
    Provides methods for:
    - Building filtered template action set queries
    """
    
    @staticmethod
    def get_list_data(
        page: int = 1,
        per_page: int = 20,
        task_name: Optional[str] = None
    ) -> Pagination:
        """
        Get paginated template action sets with filters.
        
        Args:
            page: Page number
            per_page: Items per page
            task_name: Filter by task name (partial match)
            
        Returns:
            Pagination object
        """
        query = TemplateActionSet.query
        
        if task_name:
            query = query.filter(TemplateActionSet.task_name.ilike(f'%{task_name}%'))
        
        # Order by creation date (newest first)
        query = query.order_by(TemplateActionSet.created_at.desc())
        
        # Pagination
        return query.paginate(page=page, per_page=per_page, error_out=False)


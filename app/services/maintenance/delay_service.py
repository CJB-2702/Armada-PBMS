"""
Delay Service
Presentation service for maintenance delay data retrieval and formatting.
"""

from typing import Dict, List, Optional, Tuple, Any
from flask_sqlalchemy.pagination import Pagination
from app.data.maintenance.base.maintenance_delays import MaintenanceDelay
from app.data.maintenance.base.maintenance_action_set import MaintenanceActionSet


class DelayService:
    """
    Service for maintenance delay presentation data.
    
    Provides methods for:
    - Building filtered delay queries
    - Retrieving form options
    """
    
    @staticmethod
    def get_list_data(
        page: int = 1,
        per_page: int = 20,
        maintenance_action_set_id: Optional[int] = None,
        delay_type: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[Pagination, Dict[str, Any]]:
        """
        Get paginated delays with filters and form options.
        
        Args:
            page: Page number
            per_page: Items per page
            maintenance_action_set_id: Filter by maintenance action set
            delay_type: Filter by delay type
            is_active: Filter by active status (None = all, True = active, False = inactive)
            
        Returns:
            Tuple of (pagination_object, form_options_dict)
        """
        query = MaintenanceDelay.query
        
        if maintenance_action_set_id:
            query = query.filter(MaintenanceDelay.maintenance_action_set_id == maintenance_action_set_id)
        
        if delay_type:
            query = query.filter(MaintenanceDelay.delay_type == delay_type)
        
        if is_active is not None:
            if is_active:
                query = query.filter(MaintenanceDelay.delay_end_date.is_(None))
            else:
                query = query.filter(MaintenanceDelay.delay_end_date.isnot(None))
        
        # Order by creation date (newest first)
        query = query.order_by(MaintenanceDelay.created_at.desc())
        
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
        Get form options for create/edit forms.
        
        Returns:
            Dictionary with maintenance_action_sets
        """
        return {
            'maintenance_action_sets': MaintenanceActionSet.query.all()
        }


"""
Maintenance Service
Presentation service for maintenance dashboard statistics and aggregations.
"""

from typing import Dict, List
from datetime import datetime, timedelta
from sqlalchemy import func
from app import db
from app.data.maintenance.base.maintenance_plan import MaintenancePlan
from app.data.maintenance.base.maintenance_action_set import MaintenanceActionSet
from app.data.maintenance.base.action import Action
from app.data.maintenance.base.part_demand import PartDemand
from app.data.maintenance.templates.template_action_set import TemplateActionSet
from app.data.maintenance.templates.template_action_item import TemplateActionItem
from app.data.maintenance.templates.template_part_demand import TemplatePartDemand
from app.data.maintenance.templates.template_action_tool import TemplateActionTool
from app.data.core.asset_info.asset import Asset
from app.data.maintenance.templates.template_action_set import TemplateActionSet as TemplateActionSetModel


class MaintenanceService:
    """
    Service for maintenance dashboard statistics and aggregations.
    
    Provides methods for:
    - Retrieving dashboard statistics
    - Getting recent items
    - Status breakdowns
    - Form options for maintenance operations
    """
    
    @staticmethod
    def get_dashboard_statistics() -> Dict[str, int]:
        """
        Get core maintenance statistics.
        
        Returns:
            Dictionary with counts for plans, action sets, actions, and part demands
        """
        return {
            'total_maintenance_plans': MaintenancePlan.query.count(),
            'total_maintenance_action_sets': MaintenanceActionSet.query.count(),
            'total_actions': Action.query.count(),
            'total_part_demands': PartDemand.query.count()
        }
    
    @staticmethod
    def get_template_statistics() -> Dict[str, int]:
        """
        Get template-related statistics.
        
        Returns:
            Dictionary with counts for template entities
        """
        return {
            'total_template_action_sets': TemplateActionSet.query.count(),
            'total_template_action_items': TemplateActionItem.query.count(),
            'total_template_part_demands': TemplatePartDemand.query.count(),
            'total_template_action_tools': TemplateActionTool.query.count()
        }
    
    @staticmethod
    def get_overdue_actions(limit: int = 10) -> List[Action]:
        """
        Get overdue actions (scheduled start time is in the past and not completed).
        
        Args:
            limit: Maximum number of actions to return
            
        Returns:
            List of overdue actions
        """
        today = datetime.utcnow()
        return Action.query.filter(
            Action.scheduled_start_time < today,
            Action.status.in_(['Not Started', 'In Progress'])
        ).limit(limit).all()
    
    @staticmethod
    def get_due_soon_actions(limit: int = 10, days: int = 7) -> List[Action]:
        """
        Get actions due soon (within specified days).
        
        Args:
            limit: Maximum number of actions to return
            days: Number of days to look ahead (default: 7)
            
        Returns:
            List of actions due soon
        """
        today = datetime.utcnow()
        due_soon_date = today + timedelta(days=days)
        return Action.query.filter(
            Action.scheduled_start_time.between(today, due_soon_date),
            Action.status == 'Not Started'
        ).limit(limit).all()
    
    @staticmethod
    def get_in_progress_actions(limit: int = 10) -> List[Action]:
        """
        Get actions currently in progress.
        
        Args:
            limit: Maximum number of actions to return
            
        Returns:
            List of in-progress actions
        """
        return Action.query.filter(
            Action.status == 'In Progress'
        ).limit(limit).all()
    
    @staticmethod
    def get_recent_maintenance_plans(limit: int = 10) -> List[MaintenancePlan]:
        """
        Get recent maintenance plans.
        
        Args:
            limit: Maximum number of plans to return
            
        Returns:
            List of recent maintenance plans
        """
        return MaintenancePlan.query.order_by(
            MaintenancePlan.created_at.desc()
        ).limit(limit).all()
    
    @staticmethod
    def get_recent_actions(limit: int = 10) -> List[Action]:
        """
        Get recent actions.
        
        Args:
            limit: Maximum number of actions to return
            
        Returns:
            List of recent actions
        """
        return Action.query.order_by(
            Action.created_at.desc()
        ).limit(limit).all()
    
    @staticmethod
    def get_actions_by_status() -> Dict[str, int]:
        """
        Get action counts grouped by status.
        
        Returns:
            Dictionary mapping status to count
        """
        results = db.session.query(
            Action.status,
            func.count(Action.id)
        ).group_by(Action.status).all()
        
        return dict(results)
    
    @staticmethod
    def get_plans_by_status() -> Dict[str, int]:
        """
        Get maintenance plan counts grouped by status.
        
        Returns:
            Dictionary mapping status to count
        """
        results = db.session.query(
            MaintenancePlan.status,
            func.count(MaintenancePlan.id)
        ).group_by(MaintenancePlan.status).all()
        
        return dict(results)
    
    @staticmethod
    def get_create_event_form_options() -> Dict[str, List]:
        """
        Get form options for creating maintenance event.
        
        Returns:
            Dictionary with assets and template_action_sets
        """
        return {
            'assets': Asset.query.filter_by(status='Active').order_by(Asset.name).all(),
            'template_action_sets': TemplateActionSetModel.query.order_by(
                TemplateActionSetModel.task_name
            ).all()
        }


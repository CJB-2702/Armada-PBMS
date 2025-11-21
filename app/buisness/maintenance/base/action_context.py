"""
Action Context
Business logic context manager for individual actions.
Provides action lifecycle management, statistics, and completion tracking.
"""

from typing import List, Optional, Union, Dict, Any
from datetime import datetime
from app import db
from app.buisness.maintenance.base.action_struct import ActionStruct
from app.data.maintenance.base.actions import Action
from app.data.maintenance.base.part_demands import PartDemand
from app.data.maintenance.base.action_tools import ActionTool


class ActionContext:
    """
    Business logic context manager for individual actions.
    
    Wraps ActionStruct (which wraps Action)
    Provides action lifecycle management, statistics, and completion tracking.
    """
    
    def __init__(self, action: Union[Action, ActionStruct, int]):
        """
        Initialize ActionContext with Action, ActionStruct, or ID.
        
        Args:
            action: Action instance, ActionStruct, or ID
        """
        if isinstance(action, ActionStruct):
            self._struct = action
        elif isinstance(action, Action):
            self._struct = ActionStruct(action)
        else:
            self._struct = ActionStruct(action)
        
        self._action_id = self._struct.action_id
    
    @property
    def struct(self) -> ActionStruct:
        """Get the underlying ActionStruct"""
        return self._struct
    
    @property
    def action(self) -> Action:
        """Get the Action instance"""
        return self._struct.action
    
    @property
    def action_id(self) -> int:
        """Get the action ID"""
        return self._action_id
    
    # Management methods
    def start(self, user_id: Optional[int] = None) -> 'ActionContext':
        """
        Start the action.
        
        Args:
            user_id: ID of user starting the action
            
        Returns:
            self for chaining
        """
        if self.action.status == 'Not Started':
            self.action.status = 'In Progress'
            self.action.start_time = datetime.utcnow()
            if user_id:
                self.action.assigned_by_id = user_id
                self.action.assigned_user_id = user_id
            db.session.commit()
            self.refresh()
        return self
    
    def complete(
        self,
        user_id: Optional[int] = None,
        billable_hours: Optional[float] = None,
        notes: Optional[str] = None
    ) -> 'ActionContext':
        """
        Complete the action.
        
        Args:
            user_id: ID of user completing the action
            billable_hours: Billable hours for the action
            notes: Completion notes
            
        Returns:
            self for chaining
        """
        if self.action.status in ['Not Started', 'In Progress']:
            self.action.status = 'Complete'
            self.action.end_time = datetime.utcnow()
            if billable_hours is not None:
                self.action.billable_hours = billable_hours
            if notes:
                self.action.completion_notes = notes
            db.session.commit()
            self.refresh()
        return self
    
    def assign(self, user_id: int, assigned_by_id: Optional[int] = None) -> 'ActionContext':
        """
        Assign the action to a user.
        
        Args:
            user_id: ID of user to assign to
            assigned_by_id: ID of user making the assignment (defaults to user_id)
            
        Returns:
            self for chaining
        """
        self.action.assigned_user_id = user_id
        self.action.assigned_by_id = assigned_by_id or user_id
        db.session.commit()
        self.refresh()
        return self
    
    # Statistics
    @property
    def total_part_demands(self) -> int:
        """Get total number of part demands"""
        return len(self._struct.part_demands)
    
    @property
    def total_action_tools(self) -> int:
        """Get total number of action tools"""
        return len(self._struct.action_tools)
    
    @property
    def is_complete(self) -> bool:
        """Check if action is complete"""
        return self.action.status == 'Complete'
    
    @property
    def is_in_progress(self) -> bool:
        """Check if action is in progress"""
        return self.action.status == 'In Progress'
    
    @property
    def duration(self) -> Optional[float]:
        """
        Get action duration in hours.
        
        Returns:
            Duration in hours or None if not started/completed
        """
        if self.action.start_time and self.action.end_time:
            delta = self.action.end_time - self.action.start_time
            return delta.total_seconds() / 3600
        return None
    
    # Query methods
    @staticmethod
    def get_by_maintenance_action_set(maintenance_action_set_id: int) -> List['ActionContext']:
        """
        Get all actions for a maintenance action set.
        
        Args:
            maintenance_action_set_id: Maintenance action set ID
            
        Returns:
            List of ActionContext instances, ordered by sequence_order
        """
        actions = Action.query.filter_by(
            maintenance_action_set_id=maintenance_action_set_id
        ).order_by(Action.sequence_order).all()
        return [ActionContext(action) for action in actions]
    
    @staticmethod
    def get_by_user(user_id: int) -> List['ActionContext']:
        """
        Get all actions assigned to a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of ActionContext instances
        """
        actions = Action.query.filter_by(assigned_user_id=user_id).all()
        return [ActionContext(action) for action in actions]
    
    @staticmethod
    def get_by_status(status: str, maintenance_action_set_id: Optional[int] = None) -> List['ActionContext']:
        """
        Get actions by status.
        
        Args:
            status: Status to filter by
            maintenance_action_set_id: Optional maintenance action set ID to filter by
            
        Returns:
            List of ActionContext instances
        """
        query = Action.query.filter_by(status=status)
        if maintenance_action_set_id:
            query = query.filter_by(maintenance_action_set_id=maintenance_action_set_id)
        actions = query.all()
        return [ActionContext(action) for action in actions]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize action to dictionary.
        
        Returns:
            Dictionary representation of action
        """
        return {
            'id': self._action_id,
            'action_name': self._struct.action_name,
            'description': self._struct.description,
            'status': self._struct.status,
            'sequence_order': self._struct.sequence_order,
            'maintenance_action_set_id': self._struct.maintenance_action_set_id,
            'template_action_item_id': self._struct.template_action_item_id,
            'start_time': self.action.start_time.isoformat() if self.action.start_time else None,
            'end_time': self.action.end_time.isoformat() if self.action.end_time else None,
            'billable_hours': self.action.billable_hours,
            'estimated_duration': self.action.estimated_duration,
            'assigned_user_id': self._struct.assigned_user_id,
            'total_part_demands': self.total_part_demands,
            'total_action_tools': self.total_action_tools,
            'is_complete': self.is_complete,
            'duration': self.duration,
        }
    
    def refresh(self):
        """Refresh cached data from database"""
        self._struct.refresh()
    
    def __repr__(self):
        return f'<ActionContext id={self._action_id} action_name="{self._struct.action_name}" status={self._struct.status}>'


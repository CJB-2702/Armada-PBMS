"""
MaintenanceEvent - A comprehensive wrapper class for managing maintenance events

This class provides a high-level interface for working with maintenance events,
encapsulating the event, action set, actions, and part demands into a single
cohesive unit.
"""

from pathlib import Path
from typing import List, Optional
from app import db
from app.models.core.event import Event
from app.models.maintenance.base.maintenance_action_set import MaintenanceActionSet
from app.models.maintenance.base.action import Action
from app.models.maintenance.base.part_demand import PartDemand


class MaintenanceEvent:
    """
    Comprehensive maintenance event manager that holds and manages:
    - An Event (core event record)
    - A MaintenanceActionSet (the maintenance-specific data)
    - All Actions linked to the action set (in order)
    - All PartDemands linked to the actions (in order)
    """
    
    def __init__(self, maintenance_action_set: MaintenanceActionSet):
        """
        Initialize a MaintenanceEvent from a MaintenanceActionSet
        
        Args:
            maintenance_action_set: The MaintenanceActionSet to wrap
        """
        self._action_set = maintenance_action_set
        self._event = None
        self._actions = None
        self._part_demands = None
        self.build()


    def build(self):
        """Build the maintenance event - refresh all lazy-loaded data"""
        # Refresh the action set from the database
        if self._action_set:
            db.session.refresh(self._action_set)
            self._event = None  # Clear event cache to reload
            self._actions = None  # Clear actions cache to reload
            self._part_demands = None  # Clear part demands cache to reload
    
    @property
    def action_set(self) -> MaintenanceActionSet:
        """Get the underlying MaintenanceActionSet"""
        return self._action_set
    
    @property
    def event(self) -> Optional[Event]:
        """Get the associated Event"""
        if self._event is None and self._action_set.event_id:
            self._event = db.session.get(Event, self._action_set.event_id)
        return self._event
    
    @property
    def actions(self) -> List[Action]:
        """Get all actions linked to this maintenance event, ordered by sequence"""
        if self._actions is None:
            self._actions = (
                Action.query
                .filter_by(maintenance_action_set_id=self._action_set.id)
                .order_by(Action.sequence_order)
                .all()
            )
        return self._actions
    
    @property
    def part_demands(self) -> List[PartDemand]:
        """Get all part demands linked to the actions, in action order"""
        if self._part_demands is None:
            self._part_demands = []
            for action in self.actions:
                demands = (
                    PartDemand.query
                    .filter_by(action_id=action.id)
                    .order_by(PartDemand.id)  # Or any other ordering you prefer
                    .all()
                )
                self._part_demands.extend(demands)
        return self._part_demands
    
    # Convenience properties from action_set
    @property
    def id(self):
        """Get the maintenance action set ID"""
        return self._action_set.id
    
    @property
    def task_name(self):
        """Get the task name"""
        return self._action_set.task_name
    
    @property
    def status(self):
        """Get the current status"""
        return self._action_set.status
    
    @property
    def scheduled_date(self):
        """Get the scheduled date"""
        return self._action_set.scheduled_date
    
    @property
    def asset_id(self):
        """Get the asset ID"""
        return self._action_set.asset_id
    
    @property
    def description(self):
        """Get the description"""
        return self._action_set.description
    
    # Management methods
    def start(self, user_id: int, notes: Optional[str] = None):
        """
        Start the maintenance event
        
        Args:
            user_id: ID of the user starting the maintenance
            notes: Optional notes about starting
        """
        self._action_set.start_maintenance(user_id, notes)
        self._clear_cache()
    
    def complete(self, user_id: int, notes: Optional[str] = None):
        """
        Complete the maintenance event
        
        Args:
            user_id: ID of the user completing the maintenance
            notes: Optional completion notes
        """
        self._action_set.complete_maintenance(user_id, notes)
        self._clear_cache()
    
    def cancel(self, user_id: int, reason: Optional[str] = None):
        """
        Cancel the maintenance event
        
        Args:
            user_id: ID of the user cancelling the maintenance
            reason: Reason for cancellation
        """
        self._action_set.cancel_maintenance(user_id, reason)
        self._clear_cache()
    
    def add_comment(self, user_id: int, content: str):
        """
        Add a comment to the maintenance event
        
        Args:
            user_id: ID of the user adding the comment
            content: Comment content
        """
        self._action_set.add_comment_to_event(user_id, content)
    
    def _clear_cache(self):
        """Clear cached data to force reload"""
        self._event = None
        self._actions = None
        self._part_demands = None
    
    def refresh(self):
        """Refresh all data from database"""
        db.session.refresh(self._action_set)
        self._clear_cache()
    
    # Statistics and computed properties
    @property
    def total_actions(self) -> int:
        """Get total number of actions"""
        return len(self.actions)
    
    @property
    def completed_actions(self) -> int:
        """Get number of completed actions"""
        return len([a for a in self.actions if a.status == 'Completed'])
    
    @property
    def pending_actions(self) -> int:
        """Get number of pending actions"""
        return len([a for a in self.actions if a.status == 'Not Started'])
    
    @property
    def in_progress_actions(self) -> int:
        """Get number of in-progress actions"""
        return len([a for a in self.actions if a.status == 'In Progress'])
    
    @property
    def total_part_demands(self) -> int:
        """Get total number of part demands"""
        return len(self.part_demands)
    
    @property
    def completion_percentage(self) -> float:
        """Calculate completion percentage based on actions"""
        if self.total_actions == 0:
            return 0.0
        return (self.completed_actions / self.total_actions) * 100
    
    # Class methods for creation
    @classmethod
    def from_id(cls, action_set_id: int) -> Optional['MaintenanceEvent']:
        """
        Create a MaintenanceEvent from a maintenance action set ID
        
        Args:
            action_set_id: ID of the MaintenanceActionSet
            
        Returns:
            MaintenanceEvent or None if not found
        """
        action_set = db.session.get(MaintenanceActionSet, action_set_id)
        if action_set:
            return cls(action_set)
        return None
    
    @classmethod
    def from_event_id(cls, event_id: int) -> Optional['MaintenanceEvent']:
        """
        Create a MaintenanceEvent from an event ID
        
        Args:
            event_id: ID of the Event
            
        Returns:
            MaintenanceEvent or None if not found
        """
        action_set = MaintenanceActionSet.query.filter_by(event_id=event_id).first()
        if action_set:
            return cls(action_set)
        return None
    
    @classmethod
    def get_all(cls) -> List['MaintenanceEvent']:
        """
        Get all maintenance events
        
        Returns:
            List of MaintenanceEvent objects
        """
        action_sets = MaintenanceActionSet.query.all()
        return [cls(action_set) for action_set in action_sets]
    
    @classmethod
    def get_by_status(cls, status: str) -> List['MaintenanceEvent']:
        """
        Get all maintenance events with a specific status
        
        Args:
            status: Status to filter by
            
        Returns:
            List of MaintenanceEvent objects
        """
        action_sets = MaintenanceActionSet.query.filter_by(status=status).all()
        return [cls(action_set) for action_set in action_sets]
    
    @classmethod
    def get_by_asset(cls, asset_id: int) -> List['MaintenanceEvent']:
        """
        Get all maintenance events for a specific asset
        
        Args:
            asset_id: Asset ID to filter by
            
        Returns:
            List of MaintenanceEvent objects
        """
        action_sets = MaintenanceActionSet.query.filter_by(asset_id=asset_id).all()
        return [cls(action_set) for action_set in action_sets]
    
    def __repr__(self):
        return f'<MaintenanceEvent {self.id}: {self.task_name} ({self.status})>'
    
    def to_dict(self) -> dict:
        """
        Convert to dictionary representation
        
        Returns:
            Dictionary with all maintenance event data
        """
        return {
            'id': self.id,
            'task_name': self.task_name,
            'description': self.description,
            'status': self.status,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'asset_id': self.asset_id,
            'event_id': self._action_set.event_id,
            'actions': [
                {
                    'id': action.id,
                    'action_name': action.action_name,
                    'description': action.description,
                    'status': action.status,
                    'sequence_order': action.sequence_order
                }
                for action in self.actions
            ],
            'part_demands': [
                {
                    'id': pd.id,
                    'part_id': pd.part_id,
                    'part_name': pd.part.part_name,
                    'part_number': pd.part.part_number,
                    'quantity': pd.quantity,
                    'status': pd.status,
                    'action_id': pd.action_id
                }
                for pd in self.part_demands
            ],
            'statistics': {
                'total_actions': self.total_actions,
                'completed_actions': self.completed_actions,
                'pending_actions': self.pending_actions,
                'in_progress_actions': self.in_progress_actions,
                'total_part_demands': self.total_part_demands,
                'completion_percentage': self.completion_percentage
            }
        }


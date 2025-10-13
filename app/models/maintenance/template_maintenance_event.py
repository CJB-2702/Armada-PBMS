"""
TemplateMaintenanceEvent - A comprehensive wrapper class for template maintenance events

This class provides a high-level interface for working with template maintenance events,
encapsulating the template action set, template actions, tools, part demands, and attachments
into a single cohesive unit.
"""

from pathlib import Path
from typing import List, Optional
from app import db
from app.models.maintenance.templates.template_action_set import TemplateActionSet
from app.models.maintenance.templates.template_action_item import TemplateActionItem
from app.models.maintenance.templates.template_part_demand import TemplatePartDemand
from app.models.maintenance.templates.template_action_tool import TemplateActionTool
from app.models.maintenance.templates.template_action_set_attachment import TemplateActionSetAttachment
from app.models.maintenance.templates.template_action_attachment import TemplateActionAttachment


class TemplateMaintenanceEvent:
    """
    Comprehensive template maintenance event manager that holds and manages:
    - A TemplateActionSet (the template definition)
    - All TemplateActionItems linked to the action set (in order)
    - All TemplatePartDemands linked to the action items (in order)
    - All TemplateActionTools linked to the action items (in order)
    - TemplateActionSetAttachments
    - TemplateActionAttachments (loaded on demand)
    """
    
    def __init__(self, template_action_set: TemplateActionSet):
        """
        Initialize a TemplateMaintenanceEvent from a TemplateActionSet
        
        Args:
            template_action_set: The TemplateActionSet to wrap
        """
        self._template_action_set = template_action_set
        self._action_items = None
        self._part_demands = None
        self._tools = None
        self._action_set_attachments = None
        self._action_attachments = None
    
    @property
    def template_action_set(self) -> TemplateActionSet:
        """Get the underlying TemplateActionSet"""
        return self._template_action_set
    
    @property
    def action_items(self) -> List[TemplateActionItem]:
        """Get all template action items linked to this template, ordered by sequence"""
        if self._action_items is None:
            self._action_items = (
                TemplateActionItem.query
                .filter_by(template_action_set_id=self._template_action_set.id)
                .order_by(TemplateActionItem.sequence_order)
                .all()
            )
        return self._action_items
    
    @property
    def part_demands(self) -> List[TemplatePartDemand]:
        """Get all template part demands linked to the action items, in action order"""
        if self._part_demands is None:
            self._part_demands = []
            for action_item in self.action_items:
                demands = (
                    TemplatePartDemand.query
                    .filter_by(template_action_item_id=action_item.id)
                    .order_by(TemplatePartDemand.id)
                    .all()
                )
                self._part_demands.extend(demands)
        return self._part_demands
    
    @property
    def tools(self) -> List[TemplateActionTool]:
        """Get all template action tools linked to the action items, in action order"""
        if self._tools is None:
            self._tools = []
            for action_item in self.action_items:
                tool_templates = (
                    TemplateActionTool.query
                    .filter_by(template_action_item_id=action_item.id)
                    .order_by(TemplateActionTool.id)
                    .all()
                )
                self._tools.extend(tool_templates)
        return self._tools
    
    @property
    def action_set_attachments(self) -> List[TemplateActionSetAttachment]:
        """Get all template action set attachments"""
        if self._action_set_attachments is None:
            self._action_set_attachments = (
                TemplateActionSetAttachment.query
                .filter_by(template_action_set_id=self._template_action_set.id)
                .order_by(TemplateActionSetAttachment.created_at)
                .all()
            )
        return self._action_set_attachments
    
    def get_action_attachments(self, force_reload: bool = False) -> List[TemplateActionAttachment]:
        """
        Get all template action attachments for all action items
        
        This is a method rather than a property because attachments can be large
        and we don't want to load them by default.
        
        Args:
            force_reload: If True, reload from database even if cached
            
        Returns:
            List of TemplateActionAttachment objects
        """
        if self._action_attachments is None or force_reload:
            self._action_attachments = []
            for action_item in self.action_items:
                attachments = (
                    TemplateActionAttachment.query
                    .filter_by(template_action_item_id=action_item.id)
                    .order_by(TemplateActionAttachment.created_at)
                    .all()
                )
                self._action_attachments.extend(attachments)
        return self._action_attachments
    
    # Convenience properties from template_action_set
    @property
    def id(self):
        """Get the template action set ID"""
        return self._template_action_set.id
    
    @property
    def task_name(self):
        """Get the task name"""
        return self._template_action_set.task_name
    
    @property
    def description(self):
        """Get the description"""
        return self._template_action_set.description
    
    @property
    def estimated_duration(self):
        """Get the estimated duration"""
        return self._template_action_set.estimated_duration
    
    @property
    def revision(self):
        """Get the revision"""
        return self._template_action_set.revision
    
    @property
    def safety_review_required(self):
        """Get safety review required flag"""
        return self._template_action_set.safety_review_required
    
    def _clear_cache(self):
        """Clear cached data to force reload"""
        self._action_items = None
        self._part_demands = None
        self._tools = None
        self._action_set_attachments = None
        self._action_attachments = None
    
    def refresh(self):
        """Refresh all data from database"""
        db.session.refresh(self._template_action_set)
        self._clear_cache()
    
    # Statistics and computed properties
    @property
    def total_action_items(self) -> int:
        """Get total number of action items"""
        return len(self.action_items)
    
    @property
    def required_action_items(self) -> int:
        """Get number of required action items"""
        return len([a for a in self.action_items if a.is_required])
    
    @property
    def optional_action_items(self) -> int:
        """Get number of optional action items"""
        return len([a for a in self.action_items if not a.is_required])
    
    @property
    def total_part_demands(self) -> int:
        """Get total number of part demands"""
        return len(self.part_demands)
    
    @property
    def required_part_demands(self) -> int:
        """Get number of required part demands"""
        return len([pd for pd in self.part_demands if pd.is_required])
    
    @property
    def total_tools(self) -> int:
        """Get total number of tools"""
        return len(self.tools)
    
    @property
    def total_estimated_duration(self) -> float:
        """Calculate total estimated duration from all action items"""
        return sum(
            action_item.estimated_duration or 0 
            for action_item in self.action_items 
            if action_item.is_required
        )
    
    @property
    def total_estimated_cost(self) -> float:
        """Calculate total estimated parts cost"""
        total = 0.0
        for pd in self.part_demands:
            if pd.is_required and pd.part and pd.part.unit_cost:
                total += pd.quantity_required * pd.part.unit_cost
        return total
    
    # Class methods for creation
    @classmethod
    def from_id(cls, template_action_set_id: int) -> Optional['TemplateMaintenanceEvent']:
        """
        Create a TemplateMaintenanceEvent from a template action set ID
        
        Args:
            template_action_set_id: ID of the TemplateActionSet
            
        Returns:
            TemplateMaintenanceEvent or None if not found
        """
        template_action_set = db.session.get(TemplateActionSet, template_action_set_id)
        if template_action_set:
            return cls(template_action_set)
        return None
    
    @classmethod
    def from_task_name(cls, task_name: str) -> Optional['TemplateMaintenanceEvent']:
        """
        Create a TemplateMaintenanceEvent from a task name
        
        Args:
            task_name: Name of the task
            
        Returns:
            TemplateMaintenanceEvent or None if not found
        """
        template_action_set = TemplateActionSet.query.filter_by(task_name=task_name).first()
        if template_action_set:
            return cls(template_action_set)
        return None
    
    @classmethod
    def get_all(cls) -> List['TemplateMaintenanceEvent']:
        """
        Get all template maintenance events
        
        Returns:
            List of TemplateMaintenanceEvent objects
        """
        template_action_sets = TemplateActionSet.query.all()
        return [cls(tas) for tas in template_action_sets]
    
    @classmethod
    def get_active(cls) -> List['TemplateMaintenanceEvent']:
        """
        Get all active template maintenance events
        
        Returns:
            List of TemplateMaintenanceEvent objects
        """
        template_action_sets = TemplateActionSet.query.filter_by(is_active=True).all()
        return [cls(tas) for tas in template_action_sets]
    
    def get_part_demands_by_action(self) -> dict:
        """
        Get part demands grouped by action item
        
        Returns:
            Dictionary mapping action_item_id to list of part demands
        """
        result = {}
        for action_item in self.action_items:
            demands = [pd for pd in self.part_demands if pd.template_action_item_id == action_item.id]
            if demands:
                result[action_item.id] = demands
        return result
    
    def get_tools_by_action(self) -> dict:
        """
        Get tools grouped by action item
        
        Returns:
            Dictionary mapping action_item_id to list of tools
        """
        result = {}
        for action_item in self.action_items:
            tools = [t for t in self.tools if t.template_action_item_id == action_item.id]
            if tools:
                result[action_item.id] = tools
        return result
    
    def __repr__(self):
        return f'<TemplateMaintenanceEvent {self.id}: {self.task_name} (Rev {self.revision})>'
    
    def to_dict(self) -> dict:
        """
        Convert to dictionary representation
        
        Returns:
            Dictionary with all template maintenance event data
        """
        return {
            'id': self.id,
            'task_name': self.task_name,
            'description': self.description,
            'revision': self.revision,
            'estimated_duration': self.estimated_duration,
            'safety_review_required': self.safety_review_required,
            'action_items': [
                {
                    'id': action_item.id,
                    'action_name': action_item.action_name,
                    'description': action_item.description,
                    'sequence_order': action_item.sequence_order,
                    'is_required': action_item.is_required,
                    'estimated_duration': action_item.estimated_duration
                }
                for action_item in self.action_items
            ],
            'part_demands': [
                {
                    'id': pd.id,
                    'part_id': pd.part_id,
                    'part_name': pd.part.part_name if pd.part else None,
                    'part_number': pd.part.part_number if pd.part else None,
                    'quantity_required': pd.quantity_required,
                    'is_required': pd.is_required,
                    'action_item_id': pd.template_action_item_id
                }
                for pd in self.part_demands
            ],
            'tools': [
                {
                    'id': tool.id,
                    'tool_id': tool.tool_id,
                    'tool_name': tool.tool.tool_name if tool.tool else None,
                    'quantity_required': tool.quantity_required,
                    'action_item_id': tool.template_action_item_id
                }
                for tool in self.tools
            ],
            'action_set_attachments': [
                {
                    'id': att.id,
                    'attachment_id': att.attachment_id,
                    'notes': att.notes
                }
                for att in self.action_set_attachments
            ],
            'statistics': {
                'total_action_items': self.total_action_items,
                'required_action_items': self.required_action_items,
                'optional_action_items': self.optional_action_items,
                'total_part_demands': self.total_part_demands,
                'required_part_demands': self.required_part_demands,
                'total_tools': self.total_tools,
                'total_estimated_duration': self.total_estimated_duration,
                'total_estimated_cost': self.total_estimated_cost
            }
        }
    
    def summary(self) -> str:
        """
        Get a human-readable summary of the template
        
        Returns:
            String summary
        """
        lines = [
            f"Template: {self.task_name} (Rev {self.revision})",
            f"Description: {self.description}",
            f"",
            f"Action Items: {self.total_action_items} ({self.required_action_items} required, {self.optional_action_items} optional)",
            f"Part Demands: {self.total_part_demands} ({self.required_part_demands} required)",
            f"Tools: {self.total_tools}",
            f"Attachments: {len(self.action_set_attachments)}",
            f"",
            f"Estimated Duration: {self.total_estimated_duration:.1f} hours",
            f"Estimated Parts Cost: ${self.total_estimated_cost:.2f}",
        ]
        
        if self.safety_review_required:
            lines.append("")
            lines.append("⚠️  Safety Review Required")
        
        return "\n".join(lines)


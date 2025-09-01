
from app.models.maintenance.virtual_action_item import VirtualActionItem
from app.models.maintenance.templates.template_action_item import TemplateActionItem
from app.models.maintenance.templates.template_part_demand import TemplatePartDemand
from app.models.core.comment import Comment
from app import db
from datetime import datetime
from sqlalchemy import Index, CheckConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates, relationship

class Action(VirtualActionItem):
    """base class for all actions"""
    __tablename__ = 'actions'
    
    # Table constraints and indexes for better performance and data integrity
    __table_args__ = (
        Index('ix_actions_status_maintenance_event', 'status', 'maintenance_event_set_id'),
        Index('ix_actions_template_action_item', 'template_action_item_id'),
        CheckConstraint('billable_hours >= 0', name='ck_positive_hours'),
        CheckConstraint('sequence_order > 0', name='ck_positive_sequence'),
    )

    # Action-specific fields
    status = db.Column(db.String(20), nullable=False, default='Not Started', index=True)
    scheduled_start_time = db.Column(db.DateTime, nullable=True)
    start_time = db.Column(db.DateTime, nullable=True)
    end_time = db.Column(db.DateTime, nullable=True)
    billable_hours = db.Column(db.Float, nullable=True) 
    completion_notes = db.Column(db.Text, nullable=True)
    
    # Foreign Keys
    maintenance_event_set_id = db.Column(db.Integer, db.ForeignKey('maintenance_event_sets.id'), nullable=False, index=True)
    template_action_item_id = db.Column(db.Integer, db.ForeignKey('template_action_items.id'), nullable=True)
    
    # Improved relationships with proper loading strategies
    template_action_item = relationship('TemplateActionItem', back_populates='actions', lazy='select')
    maintenance_event_set = relationship('MaintenanceEventSet', back_populates='actions')
    part_demand_references = relationship('PartDemandToActionReference', back_populates='action', cascade='all, delete-orphan')
    
    # Association proxy for easier access to part demands
    part_demands = association_proxy('part_demand_references', 'part_demand')
    part_names = association_proxy('part_demand_references', 'part_demand.part.part_name')
    
    def __repr__(self):
        return f'<Action {self.action_name}: {self.status}>'

    #-------------------------------- Init --------------------------------
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not kwargs.get('maintenance_event_set_id'):
            raise ValueError("maintenance_event_set_id is required")

        if not kwargs.get("sequence_order"):
            from app.models.maintenance.base.maintenance_event_set import MaintenanceEventSet
            maintenance_event_set = db.session.get(MaintenanceEventSet, kwargs.get('maintenance_event_set_id'))
            self.sequence_order = maintenance_event_set.get_next_sequence_order()

        if kwargs.get('template_action_item_id'):
            self.template_action_item_id = kwargs.get('template_action_item_id')
            self.copy_details_from_template_action_item(self.template_action_item)
            self.generate_part_demand_from_template_action_item(self.template_action_item)

    def copy_details_from_template_action_item(self, template_action_item: TemplateActionItem):
        """Copy details from template action item"""
        self.action_name = template_action_item.action_name
        self.description = template_action_item.description
        self.estimated_duration = template_action_item.estimated_duration
        self.expected_billable_hours = template_action_item.expected_billable_hours
        self.safety_notes = template_action_item.safety_notes
        self.notes = template_action_item.notes

    
    def generate_part_demand_from_template_action_item(self, template_action_item: TemplateActionItem):
        """Generate part demand from template action item using modern SQLAlchemy"""
        template_part_demands = template_action_item.template_part_demands.order_by(TemplatePartDemand.sequence_order)
        for template_part_demand in template_part_demands:
            self.create_part_demand_from_template(template_part_demand, self.created_by_id)
    
    def create_part_demand_from_template(self, template_part_demand:TemplatePartDemand, user_id):
        """Create a part demand from template part demand - delegates to PartDemandToActionReference"""
        from app.models.maintenance.base.part_demand_to_action_references import PartDemandToActionReference
        
        # Delegate directly to the specialized template method
        return PartDemandToActionReference.add_part_demand_from_template(
            action_id=self.id,
            template_part_demand=template_part_demand,
            user_id=user_id
        )

    #-------------------------------- Part Demands --------------------------------
    def get_part_demands(self):
        """Get all part demands for the action using association proxy"""
        return list(self.part_demands)
    
    def add_part_demand(self, user_id, part_id, quantity_required, notes=None):
        """Add a part demand to this action - delegates to PartDemandToActionReference"""
        from app.models.maintenance.base.part_demand_to_action_references import PartDemandToActionReference
        if quantity_required <= 0:
            return
        
        # Delegate the logic to the reference class which owns this responsibility
        return PartDemandToActionReference.add_part_demand_for_action(
            action_id=self.id,
            part_id=part_id,
            quantity_required=quantity_required,
            user_id=user_id,
            notes=notes
        )
    
    def remove_part_demand(self, part_id, quantity=None):
        """Remove part demand for this action - delegates to PartDemandToActionReference
        
        Args:
            part_id: ID of the part to remove
            quantity: Amount to remove (None = remove all)
            
        Returns:
            bool: True if any part demands were removed, False otherwise
        """
        from app.models.maintenance.base.part_demand_to_action_references import PartDemandToActionReference
        # Find all part demand references for this action and part_id
        part_demand_references = [
            ref for ref in self.part_demand_references
            if ref.part_demand and ref.part_demand.part_id == part_id
        ]
        removed = False
        for part_demand_reference in part_demand_references:
            part_demand_reference.remove_part_demand()
            removed = True
        return removed





    #-------------------------------- Functions --------------------------------

    @hybrid_property
    def duration_hours(self):
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds() / 3600
        return None

    def add_comment_to_event(self, user_id, comment_content):
        """Add a comment to the event"""
        comment=Comment(content=comment_content, event_id=self.maintenance_event_set.event_id, created_by_id=user_id)
        db.session.add(comment)
        db.session.commit()

    def start_action(self, user_id):
        """Start the action"""
        self.start_time = datetime.utcnow()
        self.status = 'In Progress'
    
    def complete_action(self, user_id, notes=None, status='Completed', billable_hours=None):
        """Complete the action"""
        self.end_time = datetime.utcnow()
        self.completion_notes = notes
        self.status = status
        # Calculate duration if start time exists
        if not billable_hours:
            if not self.start_time:
                return
            if not self.end_time:
                self.end_time = datetime.utcnow()  
            duration = (self.end_time - self.start_time).total_seconds() / 3600
            self.billable_hours = round(duration, 2)
        else:
            self.billable_hours = billable_hours
        
        comment_content = f"Action completed: {self.action_name}"
        if notes:
            comment_content += f"\n\nCompletion Notes: {notes}"
        self.add_comment_to_event(user_id, comment_content)
    
    def skip_action(self, user_id, reason=None):
        """Skip the action"""
        self.status = 'Skipped'
        self.completion_notes = f"Skipped: {reason}" if reason else "Skipped"
        self.updated_by_id = user_id
        comment_content = f"Action skipped: {self.action_name}"
        if reason:
            comment_content += f"\n\nReason: {reason}"
        self.add_comment_to_event(user_id, comment_content)
    
    def get_total_part_cost(self):
        """Calculate total cost of parts used"""
        total = 0
        for part_demand in self.get_part_demands():
            if hasattr(part_demand, 'expected_cost') and part_demand.expected_cost:
                total += part_demand.expected_cost
        return total
    
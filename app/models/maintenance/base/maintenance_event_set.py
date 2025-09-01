from app.models.core.event import Event, EventDetailVirtual
from app.models.maintenance.templates.template_action_set import TemplateActionSet
from app import db
from datetime import datetime
from app.models.maintenance.virtual_action_set import VirtualActionSet
from sqlalchemy import Index, CheckConstraint, UniqueConstraint, func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates, relationship
from app.models.core.comment import Comment


class MaintenanceEventSet(EventDetailVirtual, VirtualActionSet):
    __tablename__ = 'maintenance_event_sets'
    
    # Table constraints and indexes for better performance and data integrity
    __table_args__ = (
        Index('ix_maintenance_event_sets_asset_id', 'asset_id'),
        UniqueConstraint('event_id', name='uq_mes_event_id'),
    )

    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=True, unique=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=True, index=True)
    template_action_set_id = db.Column(db.Integer, db.ForeignKey('template_action_sets.id'), nullable=True)
    maintenance_plan_id = db.Column(db.Integer, db.ForeignKey('maintenance_plans.id'), nullable=True)

    # Maintenance-specific fields with proper constraints
    status = db.Column(db.String(20), default='Planned')
    priority = db.Column(db.String(20), default='Medium')
    scheduled_date = db.Column(db.DateTime, nullable=True)
    start_date = db.Column(db.DateTime, nullable=True, index=True)
    end_date = db.Column(db.DateTime, nullable=True)
    completed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    completion_notes = db.Column(db.Text, nullable=True)
    delay_notes = db.Column(db.Text, nullable=True)
    
    # Improved relationships with proper loading strategies
    maintenance_plan = relationship('MaintenancePlan', back_populates='maintenance_event_sets')
    completed_by = relationship('User', foreign_keys=[completed_by_id], backref='completed_maintenance_event_sets')
    template_action_set = relationship('TemplateActionSet', foreign_keys=[template_action_set_id], lazy='select')
    actions = relationship('Action', back_populates='maintenance_event_set', lazy='selectin', order_by='Action.sequence_order')
    delays = relationship('MaintenanceDelay', lazy='selectin')
    
    # Association proxies for easier access
    action_names = association_proxy('actions', 'action_name')
    action_statuses = association_proxy('actions', 'status')



    def __repr__(self):
        return f'<MaintenanceEventSet {self.id}: {self.status}>'

    #-------------------------------- Init --------------------------------
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.status = 'Planned'
        self.scheduled_date = kwargs.get('scheduled_date') or datetime.utcnow()
        if kwargs.get("template_action_set_id"):
            self.template_action_set_id = kwargs.get('template_action_set_id')
            self.copy_details_from_template_action_set(self.template_action_set)
            self.generate_actions_from_template_action_set(self.template_action_set, self.created_by_id)
        self._create_event()

    
    def _create_event(self):
        """Create a maintenance event for this header"""
        from app.models.core.event import Event
        
        event = Event(
            event_type='Maintenance Event',
            description=f"Maintenance event created: {self.task_name}",
            user_id=self.created_by_id,
            asset_id=self.asset_id,
            major_location_id=self.major_location_id if hasattr(self, 'major_location_id') else None
        )
        db.session.add(event)


        db.session.flush()  # Get the event ID
        self.event_id = event.id



    def copy_details_from_template_action_set(self, template_action_set: TemplateActionSet):
        """Copy common details from template action set"""
        self.task_name = template_action_set.task_name
        self.description = template_action_set.description
        self.estimated_duration = template_action_set.estimated_duration
        self.staff_count = template_action_set.staff_count
        self.parts_cost = template_action_set.parts_cost
        self.labor_hours = template_action_set.labor_hours
        self.safety_review_required = template_action_set.safety_review_required
        self.revision = template_action_set.revision
    
    def generate_actions_from_template_action_set(self, template_action_set: TemplateActionSet, user_id):
        """Generate actions from template action set - using delegation pattern"""
        from app.models.maintenance.base.action import Action
        from app.models.maintenance.templates.template_action_item import TemplateActionItem
        template_action_items = template_action_set.template_action_items.order_by(TemplateActionItem.sequence_order)
        for i,template_action_item in enumerate(template_action_items):
            # Delegate to template action item to create its corresponding action
            Action(
                maintenance_event_set_id=self.id,
                template_action_item_id=template_action_item.id,
                created_by_id=user_id,
                sequence_order=i + 1
            )
    




    #-------------------------------- Functions --------------------------------
    def get_next_sequence_order(self):
        """Get the next sequence order for actions in this maintenance event set"""
        if not self.actions:
            return 1
        max_order = max(action.sequence_order for action in self.actions)
        return max_order + 1

    def add_comment_to_event(self, user_id, comment_content):
        """Add a comment to the event"""
        
        comment = Comment(
            content=comment_content,
            event_id=self.event_id,
            created_by_id=user_id)
        db.session.add(comment)
        db.session.commit()
    
    def update_event_status(self, user_id, event_type, description):
        """Update the associated event with new details"""
        if self.event_id:
            from app.models.core.event import Event
            event = db.session.get(Event, self.event_id)
            if event:
                event.status = event_type
                event.updated_by_id = user_id
                event.updated_at = datetime.utcnow()

    def start_maintenance(self, user_id, notes=None):
        """Start the maintenance event"""
        self.status = 'In Progress'
        self.start_date = datetime.utcnow()
        self.updated_by_id = user_id
        
        comment_content = f"Maintenance started: {self.task_name}"
        if notes:
            comment_content += f"\n\nNotes: {notes}"
        self.add_comment_to_event(user_id, comment_content)
        self.update_event_status(user_id, "In Progress", comment_content)
    
    def complete_maintenance(self, user_id, notes=None):
        """Complete the maintenance event"""
        self.status = 'Completed'
        self.end_date = datetime.utcnow()
        self.completed_by_id = user_id
        self.completion_notes = notes
        self.updated_by_id = user_id
        
        comment_content = f"Maintenance completed: {self.task_name}"
        if notes:
            comment_content += f"\n\nCompletion Notes: {notes}"
        self.add_comment_to_event(user_id, comment_content)
        self.update_event_status(user_id, "Completed", comment_content)
    
    def cancel_maintenance(self, user_id, reason=None):
        """Cancel the maintenance event"""
        self.status = 'Cancelled'
        self.completion_notes = f"Cancelled: {reason}" if reason else "Cancelled"
        self.updated_by_id = user_id
        
        # Create comment for maintenance cancellation
        from app.models.core.comment import Comment
        comment_content = f"Maintenance cancelled: {self.task_name}"
        if reason:
            comment_content += f"\n\nCancellation Reason: {reason}"
        
        self.add_comment_to_event(user_id, comment_content)
        self.update_event_status(user_id, "Cancelled", comment_content)
    

from app import db
from app.data.maintenance.virtual_part_demand import VirtualPartDemand
from sqlalchemy.orm import relationship

class PartDemand(VirtualPartDemand):
    """Reference table that links maintenance actions to part demands using composition pattern"""
    __tablename__ = 'part_demands'
    
    # Foreign Keys
    action_id = db.Column(db.Integer, db.ForeignKey('actions.id'), nullable=False)
    
    # Optional fields for additional context
    sequence_order = db.Column(db.Integer, nullable=False, default=1)
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='Planned')
    
    # Relationships
    action = relationship('Action', back_populates='part_demands')
    part = relationship('Part', foreign_keys='PartDemand.part_id')
    
    # Phase 6: Inventory integration relationships 
    # NOTE: These are commented out to avoid circular import issues during build
    # The relationships will be accessible via explicit queries when Phase 6 is active
    # Uncomment these after Phase 6 tables are created:
    # purchase_order_lines = relationship(
    #     'PurchaseOrderLine',
    #     secondary='part_demand_purchase_order_lines',
    #     back_populates='part_demands',
    #     lazy='dynamic'
    # )
    # inventory_movements = relationship(
    #     'InventoryMovement',
    #     back_populates='part_demand',
    #     lazy='dynamic'
    # )
    
    def __repr__(self):
        return f'<PartDemand {self.part_id}: {self.quantity_required}>'
    
    #-------------------------------- Getters and Setters --------------------------------
    
    def _set_status(self, value, user_id=None):
        """Set status with comment tracking"""
        old_value = self.status
        self.status = value
        if user_id and old_value != value:
            self._add_comment_to_maintenance_event(user_id, f"Part demand status changed from '{old_value}' to '{value}'")
    
    def _set_quantity_required(self, value, user_id=None):
        """Set quantity required with comment tracking"""
        old_value = self.quantity_required
        self.quantity_required = value
        if user_id and old_value != value:
            self._add_comment_to_maintenance_event(user_id, f"Part demand quantity changed from '{old_value}' to '{value}'")
    
    def _set_notes(self, value, user_id=None):
        """Set notes with comment tracking"""
        old_value = self.notes
        self.notes = value
        if user_id and old_value != value:
            self._add_comment_to_maintenance_event(user_id, f"Part demand notes updated")
    
    def _add_comment_to_maintenance_event(self, user_id, comment_content):
        """Add comment to the maintenance action set"""
        if self.action and self.action.maintenance_action_set:
            self.action.maintenance_action_set.add_comment_to_event(user_id, comment_content)
    
    # Properties for getters
    @property
    def is_planned(self):
        return self.status == 'Planned'
    
    @property
    def is_received(self):
        return self.status == 'Received'
    
    @property
    def is_used(self):
        return self.status == 'Used'
    
    @property
    def is_cancelled(self):
        return self.status == 'Cancelled'
    
    @property
    def total_cost(self):
        """Calculate total cost if part has unit cost"""
        if hasattr(self, 'part') and self.part and self.part.unit_cost:
            return self.quantity_required * self.part.unit_cost
        return None
    
    #-------------------------------- Part Demand Methods --------------------------------
    
    def mark_received(self, user_id):
        """Mark part demand as received"""
        self._set_status('Received', user_id)
        self.updated_by_id = user_id
    
    def mark_used(self, user_id):
        """Mark part demand as used"""
        self._set_status('Used', user_id)
        self.updated_by_id = user_id
    
    def cancel_demand(self, user_id, reason=None):
        """Cancel the part demand"""
        self._set_status('Cancelled', user_id)
        if reason:
            self._set_notes(f"Cancelled: {reason}", user_id)
        self.updated_by_id = user_id
    
    # Note: split() method moved to PartDemandFactory.split_part_demand()

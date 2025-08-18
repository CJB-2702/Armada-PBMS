#!/usr/bin/env python3
"""
Truck Dispatch Checklist Detail Table
Truck-specific dispatch checklist
"""

from app.models.dispatching.dispatch_detail_virtual import DispatchDetailVirtual
from app import db
from sqlalchemy.ext.declarative import declared_attr
from datetime import datetime

class TruckDispatchChecklist(DispatchDetailVirtual):
    """
    Truck-specific dispatch checklist
    """
    __tablename__ = 'truck_dispatch_checklists'
    
    # Pre-trip checklist
    tires_checked = db.Column(db.Boolean, default=False)
    lights_checked = db.Column(db.Boolean, default=False)
    brakes_checked = db.Column(db.Boolean, default=False)
    fluids_checked = db.Column(db.Boolean, default=False)
    safety_equipment_checked = db.Column(db.Boolean, default=False)
    
    # Cargo and loading
    cargo_secured = db.Column(db.Boolean, default=False)
    weight_distribution_verified = db.Column(db.Boolean, default=False)
    load_manifest_verified = db.Column(db.Boolean, default=False)
    
    # Documentation
    registration_current = db.Column(db.Boolean, default=False)
    insurance_current = db.Column(db.Boolean, default=False)
    permits_obtained = db.Column(db.Boolean, default=False)
    
    # Notes
    checklist_notes = db.Column(db.Text, nullable=True)
    completed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    completed_date = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    completed_by = db.relationship('User', foreign_keys=[completed_by_id], backref='truck_checklist_completions')
    
    def __repr__(self):
        """String representation of the truck dispatch checklist"""
        return f'<TruckDispatchChecklist Dispatch:{self.dispatch_id} Completed:{self.checklist_completed}>'
    
    @property
    def checklist_completed(self):
        """Check if all required checklist items are completed"""
        required_items = [
            self.tires_checked,
            self.lights_checked,
            self.brakes_checked,
            self.fluids_checked,
            self.safety_equipment_checked,
            self.cargo_secured,
            self.weight_distribution_verified,
            self.load_manifest_verified,
            self.registration_current,
            self.insurance_current,
            self.permits_obtained
        ]
        return all(required_items)
    
    @property
    def completion_percentage(self):
        """Calculate the percentage of checklist items completed"""
        total_items = 11  # Total number of checklist items
        completed_items = sum([
            self.tires_checked,
            self.lights_checked,
            self.brakes_checked,
            self.fluids_checked,
            self.safety_equipment_checked,
            self.cargo_secured,
            self.weight_distribution_verified,
            self.load_manifest_verified,
            self.registration_current,
            self.insurance_current,
            self.permits_obtained
        ])
        return (completed_items / total_items) * 100
    
    def complete_checklist(self, user_id, notes=None):
        """Complete the checklist for this truck dispatch"""
        self.completed_by_id = user_id
        self.completed_date = datetime.utcnow()
        if notes:
            self.checklist_notes = notes
    
    def get_incomplete_items(self):
        """Get a list of incomplete checklist items"""
        incomplete_items = []
        
        if not self.tires_checked:
            incomplete_items.append("Tires Check")
        if not self.lights_checked:
            incomplete_items.append("Lights Check")
        if not self.brakes_checked:
            incomplete_items.append("Brakes Check")
        if not self.fluids_checked:
            incomplete_items.append("Fluids Check")
        if not self.safety_equipment_checked:
            incomplete_items.append("Safety Equipment Check")
        if not self.cargo_secured:
            incomplete_items.append("Cargo Secured")
        if not self.weight_distribution_verified:
            incomplete_items.append("Weight Distribution Verified")
        if not self.load_manifest_verified:
            incomplete_items.append("Load Manifest Verified")
        if not self.registration_current:
            incomplete_items.append("Registration Current")
        if not self.insurance_current:
            incomplete_items.append("Insurance Current")
        if not self.permits_obtained:
            incomplete_items.append("Permits Obtained")
        
        return incomplete_items

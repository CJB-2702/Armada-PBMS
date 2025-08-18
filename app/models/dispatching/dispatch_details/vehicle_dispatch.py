#!/usr/bin/env python3
"""
Vehicle Dispatch Detail Table
Vehicle-specific dispatch details
"""

from app.models.dispatching.dispatch_detail_virtual import DispatchDetailVirtual
from app import db
from sqlalchemy.ext.declarative import declared_attr
from datetime import datetime

class VehicleDispatch(DispatchDetailVirtual):
    """
    Vehicle-specific dispatch details
    """
    __tablename__ = 'vehicle_dispatches'
    
    # Vehicle-specific fields
    destination_address = db.Column(db.String(500), nullable=True)
    route_notes = db.Column(db.Text, nullable=True)
    fuel_level_start = db.Column(db.Float, nullable=True)
    fuel_level_end = db.Column(db.Float, nullable=True)
    mileage_start = db.Column(db.Float, nullable=True)
    mileage_end = db.Column(db.Float, nullable=True)
    driver_notes = db.Column(db.Text, nullable=True)
    passenger_count = db.Column(db.Integer, nullable=True)
    
    # Safety and compliance
    safety_check_completed = db.Column(db.Boolean, default=False)
    safety_check_date = db.Column(db.DateTime, nullable=True)
    safety_check_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Relationships
    safety_check_by = db.relationship('User', foreign_keys=[safety_check_by_id], backref='vehicle_safety_checks')
    
    def __repr__(self):
        """String representation of the vehicle dispatch"""
        return f'<VehicleDispatch Dispatch:{self.dispatch_id} Destination:{self.destination_address}>'
    
    def complete_safety_check(self, user_id):
        """Complete the safety check for this vehicle dispatch"""
        self.safety_check_completed = True
        self.safety_check_date = datetime.utcnow()
        self.safety_check_by_id = user_id
    
    @property
    def fuel_consumed(self):
        """Calculate fuel consumed during dispatch"""
        if self.fuel_level_start is not None and self.fuel_level_end is not None:
            return self.fuel_level_start - self.fuel_level_end
        return None
    
    @property
    def distance_traveled(self):
        """Calculate distance traveled during dispatch"""
        if self.mileage_start is not None and self.mileage_end is not None:
            return self.mileage_end - self.mileage_start
        return None
    
    @property
    def fuel_efficiency(self):
        """Calculate fuel efficiency (distance per fuel unit)"""
        fuel_consumed = self.fuel_consumed
        distance = self.distance_traveled
        
        if fuel_consumed and distance and fuel_consumed > 0:
            return distance / fuel_consumed
        return None

#!/usr/bin/env python3
"""
Purchase Information Detail Table
Store purchase-related information for assets
"""

from app.models.assets.asset_details.asset_detail_virtual import AssetDetailVirtual
from app.models.core.event import Event
from app import db
from datetime import datetime
from sqlalchemy.ext.declarative import declared_attr

class PurchaseInfo(AssetDetailVirtual):
    """
    Store purchase-related information for assets
    """
    __tablename__ = 'purchase_info'
    
    # Purchase information fields
    purchase_date = db.Column(db.Date, nullable=True)
    purchase_price = db.Column(db.Float, nullable=True)
    purchase_vendor = db.Column(db.String(200), nullable=True)
    purchase_order_number = db.Column(db.String(100), nullable=True)
    warranty_start_date = db.Column(db.Date, nullable=True)
    warranty_end_date = db.Column(db.Date, nullable=True)
    purchase_notes = db.Column(db.Text, nullable=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=True)
    
    # Relationships
    @declared_attr
    def event(cls):
        return db.relationship('Event', backref='purchase_info')
    
    def __repr__(self):
        """String representation of the purchase info"""
        return f'<PurchaseInfo Asset:{self.asset_id} Vendor:{self.purchase_vendor}>'
    
    def create_event(self):
        """Create an event for this purchase info record"""
        if not self.event_id:
            event = Event(
                event_type="Purchase",
                description=f"Purchase info created for asset {self.asset.name}",
                user_id=self.created_by_id,
                asset_id=self.asset_id
            )
            db.session.add(event)
            db.session.flush()  # Get the event ID
            self.event_id = event.id
            db.session.commit()
    
    @property
    def warranty_days_remaining(self):
        """Calculate warranty days remaining"""
        if self.warranty_end_date:
            remaining = (self.warranty_end_date - datetime.now().date()).days
            return max(0, remaining)
        return None
    
    @property
    def is_under_warranty(self):
        """Check if asset is still under warranty"""
        return self.warranty_days_remaining and self.warranty_days_remaining > 0 
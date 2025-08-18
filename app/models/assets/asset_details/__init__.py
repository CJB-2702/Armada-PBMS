#!/usr/bin/env python3
"""
Asset Details Package
"""

from sqlalchemy import event
from app.models.assets.asset_detail_virtual import set_row_id_after_insert

# Import all asset detail classes
from .purchase_info import PurchaseInfo
from .vehicle_registration import VehicleRegistration
from .toyota_warranty_receipt import ToyotaWarrantyReceipt

# Event listeners removed - will handle row_id setting manually for now

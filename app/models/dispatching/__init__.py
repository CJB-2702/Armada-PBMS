#!/usr/bin/env python3
"""
Dispatching Models Package
Contains all models related to dispatch operations and work order management
"""

from .dispatch import Dispatch
from .dispatch_status_history import DispatchStatusHistory
from .all_dispatch_details import AllDispatchDetail
from .dispatch_detail_virtual import DispatchDetailVirtual

# Import detail table sets
from .detail_table_sets.asset_type_dispatch_detail_table_set import AssetTypeDispatchDetailTableSet
from .detail_table_sets.model_additional_dispatch_detail_table_set import ModelAdditionalDispatchDetailTableSet

# Import concrete dispatch detail implementations
from .dispatch_details.vehicle_dispatch import VehicleDispatch
from .dispatch_details.truck_dispatch_checklist import TruckDispatchChecklist

__all__ = [
    'Dispatch',
    'DispatchStatusHistory', 
    'AllDispatchDetail',
    'DispatchDetailVirtual',
    'AssetTypeDispatchDetailTableSet',
    'ModelAdditionalDispatchDetailTableSet',
    'VehicleDispatch',
    'TruckDispatchChecklist'
]

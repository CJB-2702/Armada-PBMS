# Phase 6 Inventory Models - Quick Start Guide

## ✅ What's Been Implemented

All Phase 6 database models are complete and ready to use:

1. ✅ **PurchaseOrderHeader** - Purchase order documents
2. ✅ **PurchaseOrderLine** - PO line items
3. ✅ **PartDemandPurchaseOrderLine** - Links part demands to POs
4. ✅ **PackageHeader** - Package/shipment tracking
5. ✅ **PartArrival** - Individual part receipts with inspection
6. ✅ **ActiveInventory** - Current stock levels by location
7. ✅ **InventoryMovement** - Movement audit trail with **complete traceability**

## 📦 Import Models

```python
from app.models.inventory import (
    PurchaseOrderHeader,
    PurchaseOrderLine,
    PartDemandPurchaseOrderLine,
    PackageHeader,
    PartArrival,
    ActiveInventory,
    InventoryMovement
)
```

## 🔧 Import Managers

```python
from app.models.inventory.managers import (
    PurchaseOrderManager,
    PartArrivalManager,
    InventoryManager,
    PartDemandManager
)
```

## 🔑 Key Features

### Complete Traceability Chain ⭐
Every inventory movement tracks:
- **`initial_arrival_id`** - Links to original part arrival (preserved forever)
- **`previous_movement_id`** - Links to previous movement (creates chain)

This allows complete traceability from any inventory movement back to:
- Original purchase order
- Vendor information
- Receiving date and quality
- Complete movement history

### Example Usage (in future managers):
```python
# Get complete movement history
movement = InventoryMovement.query.get(movement_id)
chain = movement.get_movement_chain()  # Returns [M4, M3, M2, M1]

# Get original source
original_arrival = movement.get_source_arrival()
original_po = original_arrival.purchase_order_line.purchase_order
```

## 📋 Model Relationships

### Purchase Order Flow
```
PurchaseOrderHeader (1)
    ├── purchase_order_lines (many) → PurchaseOrderLine
    ├── major_location → MajorLocation
    └── event → Event

PurchaseOrderLine (1)
    ├── purchase_order → PurchaseOrderHeader
    ├── part → Part
    ├── part_demands (many) → PartDemand (via association)
    └── part_arrivals (many) → PartArrival
```

### Receiving Flow
```
PackageHeader (1)
    ├── part_arrivals (many) → PartArrival
    ├── major_location → MajorLocation
    └── received_by → User

PartArrival (1)
    ├── package_header → PackageHeader
    ├── purchase_order_line → PurchaseOrderLine
    ├── part → Part
    ├── inventory_movements (many) → InventoryMovement
    └── initial_movements (many) → InventoryMovement (traceability)
```

### Inventory Flow
```
ActiveInventory (1)
    ├── part → Part
    └── major_location → MajorLocation

InventoryMovement (1)
    ├── part → Part
    ├── major_location → MajorLocation
    ├── from_location → MajorLocation (for transfers)
    ├── to_location → MajorLocation (for transfers)
    ├── part_arrival → PartArrival (if arrival)
    ├── part_demand → PartDemand (if issue)
    ├── initial_arrival → PartArrival (traceability)
    └── previous_movement → InventoryMovement (traceability)
```

### Maintenance Integration
```
PartDemand (Phase 5)
    ├── purchase_order_lines (many) → PurchaseOrderLine
    └── inventory_movements (many) → InventoryMovement
```

## 🎯 Status Values

### PurchaseOrderHeader.status
- `Draft` - Being created, not yet submitted
- `Submitted` - Submitted to vendor
- `Partial` - Some lines received
- `Complete` - All lines fully received
- `Cancelled` - Order cancelled

### PurchaseOrderLine.status
- `Pending` - Not yet received
- `Partial` - Partially received
- `Complete` - Fully received
- `Cancelled` - Line cancelled

### PartArrival.status
- `Pending` - Received but not inspected
- `Inspected` - Inspected with results recorded
- `Accepted` - Accepted into inventory
- `Rejected` - Rejected, not added to inventory

### InventoryMovement.movement_type
- `Arrival` - Parts received into inventory
- `Issue` - Parts issued to maintenance/work
- `Adjustment` - Manual inventory adjustment
- `Transfer` - Transfer between locations
- `Return` - Parts returned from maintenance

## 🔧 Next Steps

### To Use These Models:

1. **Update main build.py** to include Phase 6:
   ```python
   from app.models.inventory.build import build_models
   build_models()
   ```

2. **Run database migration** to create tables:
   ```bash
   source venv/bin/activate
   python app.py  # Will create all tables
   ```

3. **Implement Manager Classes** (next phase):
   - `PurchaseOrderManager` - Business logic for POs
   - `PartArrivalManager` - Receiving workflow
   - `InventoryManager` - Movement and stock management
   - `PartDemandManager` - Integration with maintenance

4. **Create Routes and UI** (future):
   - Purchase order creation and management
   - Part receiving and inspection
   - Inventory viewing and adjustments
   - Integration with maintenance workflows

## 📚 Design Philosophy

These models follow the **Manager Pattern**:

- ✅ **Models = Data Structure** (CRUD only)
  - Define database schema
  - Basic properties and methods
  - Simple validation
  - to_dict/from_dict serialization

- 🔄 **Managers = Business Logic** (to be implemented)
  - Complex workflows
  - Multi-table operations
  - Status transitions
  - Event creation
  - Validation rules

**Keep business logic OUT of models - it goes in managers!**

## 🧪 Verify Installation

Run this to verify models and managers are working:

```bash
source venv/bin/activate
python -c "from app.models.inventory import *; from app.models.inventory.managers import *; print('✓ Inventory models and managers ready!')"
```

## 📖 Documentation

- `IMPLEMENTATION_SUMMARY.md` - Complete implementation details
- `../../../Design/Phase6_inventory and purchasing/DataModel.md` - Full data model spec
- `../../../Design/Phase6_inventory and purchasing/SystemDiagram.md` - Visual diagrams
- `../../../Design/Phase6_inventory and purchasing/ImplementationPlan.md` - Step-by-step guide

## 📚 Manager Methods Quick Reference

### PurchaseOrderManager
- `create_from_part_demands()` - Create PO from maintenance demands
- `submit_order()` - Submit PO to vendor
- `cancel_order()` - Cancel PO
- `add_line()` - Add line to PO
- `check_completion_status()` - Update PO status

### PartArrivalManager  
- `create_package()` - Create package for receiving
- `receive_parts()` - Receive parts into package
- `inspect_arrival()` - Record inspection results
- `accept_arrival()` - Accept parts (creates inventory movement)
- `reject_arrival()` - Reject parts

### InventoryManager ⭐
- `record_arrival()` - Record arrival (START of traceability chain)
- `issue_to_demand()` - Issue to maintenance (PRESERVES chain)
- `transfer_between_locations()` - Transfer (MAINTAINS chain)
- `adjust_inventory()` - Manual adjustment
- `return_from_demand()` - Return from maintenance
- `check_availability()` - Check stock availability
- `get_movement_history()` - Get complete movement chain
- `get_movements_from_arrival()` - Get all movements from arrival

### PartDemandManager
- `get_unfulfilled_demands()` - Get pending demands
- `get_purchase_recommendations()` - Generate purchase suggestions
- `check_inventory_availability()` - Check if demand can be fulfilled
- `mark_demand_fulfilled()` - Mark demand as received
- `get_demand_fulfillment_status()` - Get complete status

---

**Status**: Models complete ✅ | Managers complete ✅ | Routes pending ⏳


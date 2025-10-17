# Phase 6 Quick Reference Guide

## Architecture Summary

```
DATA MODELS (CRUD) → MANAGERS (Logic) → ROUTES (UI)
     ↓                    ↓                  ↓
 Database Tables    Business Logic      Web Interface
```

## Key Models at a Glance

| Model | Purpose | Key Fields | Manager |
|-------|---------|------------|---------|
| **PurchaseOrderHeader** | Purchase order document | po_number, vendor_name, status | PurchaseOrderManager |
| **PurchaseOrderLine** | Individual items on PO | part_id, quantity_ordered, quantity_received | PurchaseOrderManager |
| **PackageHeader** | Physical shipment | package_number, tracking_number, received_date | PartArrivalManager |
| **PartArrival** | Parts received in package | quantity_received, quantity_accepted | PartArrivalManager |
| **ActiveInventory** | Current stock levels | part_id, location_id, quantity_on_hand | InventoryManager |
| **InventoryMovement** | Audit trail | movement_type, quantity, reference | InventoryManager |

## Status Values Cheat Sheet

### PurchaseOrderHeader.status
- **Draft** → Being created
- **Submitted** → Sent to vendor
- **Partial** → Some items received
- **Complete** → All items received
- **Cancelled** → Order cancelled

### PurchaseOrderLine.status
- **Pending** → Nothing received yet
- **Partial** → Some quantity received
- **Complete** → Full quantity received
- **Cancelled** → Line cancelled

### PartArrival.status
- **Pending** → Received but not inspected
- **Inspected** → Inspection recorded
- **Accepted** → Added to inventory
- **Rejected** → Not added to inventory

### InventoryMovement.movement_type
- **Arrival** → Parts received (+)
- **Issue** → Parts issued to maintenance (-)
- **Adjustment** → Manual adjustment (+/-)
- **Transfer** → Between locations (+/-)
- **Return** → Parts returned from maintenance (+)

## Manager Responsibilities

### PurchaseOrderManager
- ✅ Create POs from part demands
- ✅ Link demands to PO lines
- ✅ Submit and cancel orders
- ✅ Track order status
- ✅ Calculate totals
- ✅ Create events

**Common Methods**:
```python
PurchaseOrderManager.create_from_part_demands(demands, vendor_info, user_id)
PurchaseOrderManager.submit_order(po_id, user_id)
PurchaseOrderManager.check_completion_status(po_id, user_id)
```

### PartArrivalManager
- ✅ Create packages
- ✅ Receive parts against PO
- ✅ Inspect parts (accept/reject)
- ✅ Update PO line quantities
- ✅ Trigger inventory movements
- ✅ Handle partial fulfillment

**Common Methods**:
```python
PartArrivalManager.create_package(package_number, location_id, received_by_id, user_id)
PartArrivalManager.receive_parts(package_id, po_line_id, quantity, condition, user_id)
PartArrivalManager.inspect_arrival(arrival_id, accepted_qty, rejected_qty, notes, user_id)
PartArrivalManager.accept_arrival(arrival_id, user_id)  # Creates inventory movement
```

### InventoryManager
- ✅ Record all inventory movements
- ✅ Update active inventory
- ✅ Issue parts to maintenance
- ✅ Handle transfers
- ✅ Track allocations
- ✅ Check availability

**Common Methods**:
```python
InventoryManager.record_arrival(part_arrival_id, user_id)  # Called by PartArrivalManager
InventoryManager.issue_to_demand(part_demand_id, quantity, location_id, user_id)
InventoryManager.check_availability(part_id, location_id, quantity)
InventoryManager.transfer_between_locations(part_id, from_loc, to_loc, quantity, user_id)
```

### PartDemandManager
- ✅ Find unfulfilled demands
- ✅ Generate purchase recommendations
- ✅ Check inventory availability
- ✅ Link demands to purchases
- ✅ Mark demands fulfilled

**Common Methods**:
```python
PartDemandManager.get_unfulfilled_demands(location_id, asset_type_id)
PartDemandManager.get_purchase_recommendations()
PartDemandManager.check_inventory_availability(demand_id)
PartDemandManager.mark_demand_fulfilled(demand_id, inventory_movement_id, user_id)
```

## Workflow Diagrams (Simplified)

### Purchase Order Workflow
```
1. Maintenance creates PartDemand
2. PartDemandManager checks inventory
   ├─ In Stock? → Issue from inventory (done)
   └─ Not available? → Continue to step 3
3. User creates PurchaseOrder from demands
4. PurchaseOrderManager.submit_order()
5. Wait for delivery...
```

### Receiving Workflow
```
1. Package arrives
2. PartArrivalManager.create_package()
3. PartArrivalManager.receive_parts() for each item
4. PartArrivalManager.inspect_arrival() 
5. PartArrivalManager.accept_arrival()
   └─ Automatically calls InventoryManager.record_arrival()
6. Inventory updated, PO line quantity updated
```

### Issue to Maintenance Workflow
```
1. Maintenance has PartDemand
2. InventoryManager.check_availability()
3. If available: InventoryManager.issue_to_demand()
4. Creates InventoryMovement (Issue type)
5. Updates ActiveInventory (decrease)
6. Marks PartDemand as fulfilled
```

## Traceability Chain

```
MaintenanceAction → PartDemand → PurchaseOrderLine → PurchaseOrderHeader
                                         ↓
                                   PartArrival → InventoryMovement (Arrival)
                                                        ↓
PartDemand ← InventoryMovement (Issue) ← ActiveInventory
```

**To trace a part**:
1. Start with PartDemand
2. Check `part_demand.purchase_order_lines` → Which PO?
3. Check `po_line.part_arrivals` → When received?
4. Check `part_arrival.inventory_movements` → Inventory movement?
5. Check `part_demand.inventory_movements` → When issued?

## Common Code Patterns

### Creating a Purchase Order
```python
from app.models.purchasing.managers import PurchaseOrderManager

# Get unfulfilled demands
demands = PartDemandManager.get_unfulfilled_demands(location_id=1)

# Create PO
vendor_info = {
    'vendor_name': 'ABC Supply',
    'vendor_contact': 'sales@abc.com',
    'expected_delivery_date': datetime.now() + timedelta(days=7)
}

po = PurchaseOrderManager.create_from_part_demands(
    part_demands=demands,
    vendor_info=vendor_info,
    user_id=current_user.id
)

# Submit for ordering
PurchaseOrderManager.submit_order(po.id, current_user.id)
```

### Receiving Parts
```python
from app.models.purchasing.managers import PartArrivalManager

# Create package
package = PartArrivalManager.create_package(
    package_number='PKG-2024-001',
    location_id=1,
    received_by_id=current_user.id,
    user_id=current_user.id
)

# Receive parts
arrival = PartArrivalManager.receive_parts(
    package_id=package.id,
    po_line_id=po_line.id,
    quantity=50,
    condition='Good',
    user_id=current_user.id
)

# Inspect
PartArrivalManager.inspect_arrival(
    arrival_id=arrival.id,
    accepted_qty=50,
    rejected_qty=0,
    notes='All parts in good condition',
    user_id=current_user.id
)

# Accept (triggers inventory movement)
PartArrivalManager.accept_arrival(
    arrival_id=arrival.id,
    user_id=current_user.id
)
```

### Issuing Parts to Maintenance
```python
from app.models.purchasing.managers import InventoryManager

# Check availability first
available = InventoryManager.check_availability(
    part_id=part.id,
    location_id=1,
    quantity=10
)

if available:
    # Issue parts
    InventoryManager.issue_to_demand(
        part_demand_id=demand.id,
        quantity=10,
        location_id=1,
        user_id=current_user.id
    )
else:
    # Need to order
    flash('Part not available in inventory. Create purchase order.')
```

### Checking Inventory
```python
from app.models.purchasing.base import ActiveInventory

# Get inventory at specific location
inventory = ActiveInventory.query.filter_by(
    part_id=part.id,
    major_location_id=location.id
).first()

if inventory:
    print(f"On Hand: {inventory.quantity_on_hand}")
    print(f"Allocated: {inventory.quantity_allocated}")
    print(f"Available: {inventory.quantity_available}")
    print(f"Value: ${inventory.total_value}")
```

## Database Relationships Quick Reference

```
Part
  ├── purchase_order_lines (One-to-Many)
  ├── part_arrivals (One-to-Many)
  ├── active_inventory (One-to-Many)
  └── inventory_movements (One-to-Many)

PurchaseOrderHeader
  ├── purchase_order_lines (One-to-Many)
  ├── major_location (Many-to-One)
  └── event (Many-to-One)

PurchaseOrderLine
  ├── purchase_order (Many-to-One)
  ├── part (Many-to-One)
  ├── part_demands (Many-to-Many through association table)
  └── part_arrivals (One-to-Many)

PartDemand (from Phase 5)
  ├── purchase_order_lines (Many-to-Many)
  └── inventory_movements (One-to-Many)

PackageHeader
  ├── part_arrivals (One-to-Many)
  └── major_location (Many-to-One)

PartArrival
  ├── package_header (Many-to-One)
  ├── purchase_order_line (Many-to-One)
  ├── part (Many-to-One)
  └── inventory_movements (One-to-Many)

ActiveInventory
  ├── part (Many-to-One)
  └── major_location (Many-to-One)
  [Unique constraint: (part_id, major_location_id)]

InventoryMovement
  ├── part (Many-to-One)
  ├── major_location (Many-to-One)
  ├── part_arrival (Many-to-One, Optional)
  └── part_demand (Many-to-One, Optional)
```

## Testing Checklist

### Model Tests
- [ ] Create record
- [ ] Read record
- [ ] Update record
- [ ] Delete record
- [ ] Test relationships
- [ ] Test properties
- [ ] Test constraints

### Manager Tests
- [ ] Test each manager method independently
- [ ] Test with valid inputs
- [ ] Test with invalid inputs
- [ ] Test error handling
- [ ] Test event creation
- [ ] Test database commits

### Integration Tests
- [ ] PO creation from demands
- [ ] Receiving against PO
- [ ] Inventory update from arrival
- [ ] Issue from inventory
- [ ] Complete traceability chain
- [ ] Partial fulfillment scenarios
- [ ] Multi-location scenarios

## File Structure Reference

```
app/models/purchasing/
├── __init__.py                              # Package imports
├── build.py                                 # Database build
├── base/                                    # DATA MODELS (CRUD)
│   ├── __init__.py
│   ├── purchase_order_header.py            # PO document
│   ├── purchase_order_line.py              # PO line items
│   ├── part_demand_purchase_order_line.py  # Association table
│   ├── package_header.py                   # Shipment/package
│   ├── part_arrival.py                     # Parts received
│   ├── active_inventory.py                 # Current stock
│   └── inventory_movement.py               # Movement audit
├── managers/                                # BUSINESS LOGIC
│   ├── __init__.py
│   ├── purchase_order_manager.py           # PO logic
│   ├── part_arrival_manager.py             # Receiving logic
│   ├── inventory_manager.py                # Inventory logic
│   └── part_demand_manager.py              # Demand analysis
└── utils/                                   # HELPER FUNCTIONS
    ├── __init__.py
    ├── purchasing_helpers.py
    └── inventory_helpers.py
```

## Import Examples

```python
# Import models
from app.models.purchasing.base import (
    PurchaseOrderHeader,
    PurchaseOrderLine,
    ActiveInventory,
    InventoryMovement
)

# Import managers (more common in routes)
from app.models.purchasing.managers import (
    PurchaseOrderManager,
    PartArrivalManager,
    InventoryManager,
    PartDemandManager
)

# Import from Phase 5 (Maintenance)
from app.models.maintenance.base import PartDemand

# Import from Phase 4 (Supply)
from app.models.supply_items import Part

# Import from Phase 1 (Core)
from app.models.core import MajorLocation, Event, User
```

## Common Queries

```python
# Get all open purchase orders
open_pos = PurchaseOrderHeader.query.filter(
    PurchaseOrderHeader.status.in_(['Draft', 'Submitted', 'Partial'])
).all()

# Get pending inspections at a location
pending = PartArrival.query.filter_by(
    status='Pending'
).join(PackageHeader).filter(
    PackageHeader.major_location_id == location_id
).all()

# Get low stock items
low_stock = ActiveInventory.query.join(Part).filter(
    ActiveInventory.quantity_on_hand <= Part.minimum_stock_level
).all()

# Get inventory movements for a part
movements = InventoryMovement.query.filter_by(
    part_id=part_id
).order_by(InventoryMovement.movement_date.desc()).limit(20).all()

# Get unfulfilled demands
unfulfilled = PartDemand.query.filter(
    PartDemand.status != 'Fulfilled'
).all()
```

## Event Integration

All major operations create events for audit trail:

```python
from app.models.core import Event

# Events are created automatically by managers:
# - PO created/submitted/cancelled
# - Parts received
# - Parts inspected/accepted
# - Inventory movements
# - Parts issued to maintenance

# To add comments to an event:
comment = Comment(
    event_id=event.id,
    content='Vendor confirmed delivery for next Tuesday',
    user_id=current_user.id
)
db.session.add(comment)
db.session.commit()
```

## Tips and Best Practices

### DO:
✅ Always use managers for complex operations
✅ Check inventory before creating purchase orders
✅ Create events for audit trail
✅ Track user_id for all operations
✅ Validate data in manager layer
✅ Use transactions for multi-table operations
✅ Test edge cases (partial fulfillment, rejections, etc.)

### DON'T:
❌ Put business logic in models
❌ Bypass managers to modify inventory directly
❌ Forget to update PO line quantities on receiving
❌ Create inventory movements without using InventoryManager
❌ Forget to commit database changes
❌ Skip validation in managers
❌ Assume quantities will always match (handle partials)

## Performance Tips

1. **Use eager loading** for relationships:
```python
po = PurchaseOrderHeader.query.options(
    joinedload(PurchaseOrderHeader.purchase_order_lines)
).get(po_id)
```

2. **Batch operations** when possible:
```python
# Instead of multiple queries
for demand in demands:
    check_inventory(demand)

# Do bulk query
inventory = get_inventory_for_parts([d.part_id for d in demands])
```

3. **Index commonly queried fields**:
- `purchase_order_headers.po_number`
- `active_inventory(part_id, major_location_id)`
- `inventory_movements.movement_date`

## Troubleshooting Common Issues

### Issue: Inventory not updating after receiving
**Check**:
1. Was `PartArrivalManager.accept_arrival()` called?
2. Was the arrival status set to 'Accepted'?
3. Did the inventory movement get created?
4. Check database logs for errors

### Issue: PO status not updating to Complete
**Check**:
1. Are all lines fully received?
2. Was `PurchaseOrderManager.check_completion_status()` called?
3. Check line status values

### Issue: Cannot issue parts from inventory
**Check**:
1. Is quantity available? (on_hand - allocated)
2. Correct location?
3. Part active?
4. Check for database constraints

### Issue: Traceability chain broken
**Check**:
1. Association table populated?
2. Foreign keys correct?
3. Relationships defined in both models?

## Quick SQL Queries for Debugging

```sql
-- Check inventory levels
SELECT p.part_name, l.name as location, 
       ai.quantity_on_hand, ai.quantity_allocated
FROM active_inventory ai
JOIN parts p ON ai.part_id = p.id
JOIN major_locations l ON ai.major_location_id = l.id;

-- Check PO status
SELECT po.po_number, po.status, 
       COUNT(pol.id) as line_count,
       SUM(CASE WHEN pol.status = 'Complete' THEN 1 ELSE 0 END) as complete_lines
FROM purchase_order_headers po
LEFT JOIN purchase_order_lines pol ON po.id = pol.purchase_order_id
GROUP BY po.id;

-- Check recent inventory movements
SELECT im.movement_type, p.part_name, im.quantity, 
       im.movement_date, l.name as location
FROM inventory_movements im
JOIN parts p ON im.part_id = p.id
JOIN major_locations l ON im.major_location_id = l.id
ORDER BY im.movement_date DESC
LIMIT 20;

-- Find demands without POs
SELECT pd.id, p.part_name, pd.quantity_required
FROM part_demands pd
JOIN parts p ON pd.part_id = p.id
LEFT JOIN part_demand_purchase_order_lines pdpol ON pd.id = pdpol.part_demand_id
WHERE pdpol.id IS NULL
  AND pd.status != 'Fulfilled';
```

## Summary

**Phase 6 = Purchasing + Receiving + Inventory**

**Key Pattern**: Models store data, Managers handle logic

**Integration**: Seamlessly connects Maintenance (Phase 5) part demands to purchasing and inventory

**Traceability**: Complete chain from demand → PO → arrival → inventory → issue

**Remember**: Always use managers for complex operations!


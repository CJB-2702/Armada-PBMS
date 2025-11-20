# Phase 6: Inventory and Purchasing System

## Overview
This phase implements a comprehensive inventory and purchasing system with full traceability from maintenance needs through purchasing to inventory usage.

## Documentation Files

### 1. DataModel.md
Complete data model documentation including:
- All entity definitions
- Field specifications
- Relationships
- Manager class responsibilities
- **Enhanced traceability chain** with `initial_arrival_id` and `previous_movement_id`

### 2. SystemDiagram.md
Visual diagrams including:
- System architecture overview
- Complete data flow diagrams
- Entity relationships
- Status state diagrams
- **Enhanced traceability chain visualization**

### 3. ImplementationPlan.md
Step-by-step implementation guide

### 4. QuickReference.md
Quick lookup reference for common operations

## Key Features

### Complete Traceability Chain
The inventory system now includes enhanced traceability through two additional fields on the `InventoryMovement` table:

#### `initial_arrival_id` (Foreign Key to PartArrival)
- Points to the original part arrival that introduced inventory into the system
- Preserved across ALL subsequent movements (transfers, adjustments, issues)
- Enables instant lookup of:
  - Original purchase order
  - Vendor information
  - Receiving date
  - Unit cost at arrival
  - Quality inspection results

#### `previous_movement_id` (Foreign Key to InventoryMovement)
- Points to the immediately preceding movement in the chain
- Creates a linked list of movements
- Enables:
  - Complete movement history reconstruction
  - Forward and backward traversal
  - Chain of custody tracking
  - Movement pattern analysis

### Traceability Benefits

1. **Regulatory Compliance**: Meet requirements for part traceability (aviation, medical, automotive)
2. **Quality Control**: Trace defective parts back to original vendor and batch
3. **Warranty Claims**: Link warranty claims to original purchase
4. **Cost Analysis**: Track actual cost propagation through movements
5. **Audit Trail**: Complete chain of custody for all parts
6. **Root Cause Analysis**: Trace issues back to source
7. **Vendor Performance**: Analyze quality by vendor over time

### Example Traceability Chain

```
Part Arrival [A1] from Vendor XYZ (PO #12345)
  ↓
Inventory Movement M1 (Arrival)
  - initial_arrival_id: A1
  - previous_movement_id: null
  ↓
Inventory Movement M2 (Transfer to Warehouse B)
  - initial_arrival_id: A1  ← Preserved from M1
  - previous_movement_id: M1 ← Links to M1
  ↓
Inventory Movement M3 (Transfer to Field Location)
  - initial_arrival_id: A1  ← Still points to original arrival
  - previous_movement_id: M2 ← Links to M2
  ↓
Inventory Movement M4 (Issue to Maintenance Work)
  - initial_arrival_id: A1  ← Complete traceability to purchase
  - previous_movement_id: M3 ← Links to M3
  - part_demand_id: D1       ← Fulfills maintenance need

From M4, you can:
- Trace back through M3 → M2 → M1 → A1 → PO Line → PO Header
- See complete movement history
- Identify original vendor
- Calculate total transit time
- Analyze movement patterns
```

## Integration Points

### With Phase 5 (Maintenance)
- Part demands link to inventory movements via `part_demand_id`
- When parts are issued to maintenance, full traceability is maintained
- Can track which maintenance work used which parts from which vendor

### With Phase 1 (Core)
- Uses `MajorLocation` for location tracking
- Creates `Event` records for purchase orders
- All models inherit from `UserCreatedBase` for audit trail

### With Phase 4 (Supply)
- References `Part` model throughout
- No changes to existing Part model needed

## Implementation Status

This is a design document. Implementation has not yet begun.

### Next Steps
1. Review and approve data model
2. Create database models
3. Implement manager classes with traceability logic
4. Create routes and UI
5. Write comprehensive tests including traceability chain tests
6. Deploy to development environment

## Database Changes

### New Tables
1. `purchase_order_headers`
2. `purchase_order_lines`
3. `part_demand_purchase_order_lines` (association)
4. `package_headers`
5. `part_arrivals`
6. `active_inventory`
7. `inventory_movements` (includes `initial_arrival_id` and `previous_movement_id`)

### New Indexes
- `inventory_movements.initial_arrival_id` - For traceability queries
- `inventory_movements.previous_movement_id` - For chain traversal
- Additional indexes on all foreign keys

## Testing Requirements

### Traceability-Specific Tests
1. Verify `initial_arrival_id` set correctly on arrival movements
2. Verify `initial_arrival_id` preserved through transfers
3. Verify `previous_movement_id` correctly links movements
4. Test chain traversal backward from any movement
5. Test chain traversal forward from arrival
6. Verify no broken links in chain
7. Test queries for movement history
8. Test queries for all movements from an arrival

## Manager Responsibilities

### InventoryManager
The `InventoryManager` is responsible for maintaining the traceability chain:

- **On Arrival**: Set `initial_arrival_id` = `part_arrival_id`, `previous_movement_id` = null
- **On Transfer**: Copy `initial_arrival_id` from source, set `previous_movement_id` = source movement
- **On Issue**: Copy `initial_arrival_id`, set `previous_movement_id` = source movement
- **On Adjustment**: Maintain `initial_arrival_id` if adjusting existing inventory
- **On Return**: Trace back to original issue to maintain chain

### Query Methods
- `get_movement_history(movement_id)` - Get complete chain back to arrival
- `get_movements_from_arrival(arrival_id)` - Get all movements from an arrival
- `trace_to_purchase_order(movement_id)` - Trace movement to original PO

## Future Enhancements Enabled by Traceability

1. **Lot/Serial Number Tracking**: Extend traceability to individual items
2. **FIFO/LIFO Cost Methods**: Use arrival tracing for cost calculations
3. **Warranty Tracking**: Link warranty periods to arrival dates
4. **Quality Analytics**: Analyze quality by vendor/batch over time
5. **Movement Optimization**: Identify inefficient transfer patterns
6. **Inventory Aging**: Calculate true age from arrival
7. **Compliance Reporting**: Generate chain of custody reports
8. **Vendor Scorecards**: Rate vendors by part quality over time

## Notes

- Traceability fields are **optional** in the database schema but should be populated for all movements
- The `InventoryManager` is responsible for maintaining chain integrity
- Breaking the chain (missing `initial_arrival_id` or `previous_movement_id`) should be avoided
- For inventory adjustments where source is unknown, `initial_arrival_id` may be null
- The system supports both forward and backward tracing through the chain

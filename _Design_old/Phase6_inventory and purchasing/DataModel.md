# Phase 6: Inventory and Purchasing System - Data Model Documentation

## Overview

Phase 6 implements a comprehensive inventory and purchasing system that connects part demand from maintenance operations to purchase orders and tracks inventory movements. The system follows a clean separation between data models (simple CRUD) and business logic (manager classes).

## Design Philosophy

### Core Principles
1. **Simple Data Models**: Table classes define database structure with minimal functionality (CRUD only)
2. **Manager Classes**: Handle all complex business logic, factories, and relationships
3. **Clear Separation**: Data layer vs. business logic layer
4. **Integration**: Seamless connection with Phase 5 (Maintenance) part demands
5. **Traceability**: Full audit trail from demand → purchase → arrival → inventory

## Architecture Overview

### Layer Structure
```
┌─────────────────────────────────────────────────┐
│         Application Layer (Routes)              │
└─────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│    Manager Layer (Business Logic & Factories)   │
│  - PurchaseOrderManager                         │
│  - InventoryManager                             │
│  - PartArrivalManager                           │
└─────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│         Data Layer (Database Models)            │
│  - PurchaseOrderHeader                          │
│  - PurchaseOrderLine                            │
│  - PartArrival                                  │
│  - PackageHeader                                │
│  - InventoryMovement                            │
│  - ActiveInventory                              │
└─────────────────────────────────────────────────┘
```

## Core Concepts

### 1. Purchase Order Flow
**Purchase Order Header** → contains multiple **Purchase Order Lines** (parts to order)
- Each line links to a specific **Part**
- Lines can link to multiple **Part Demands** from maintenance
- Tracks order status, vendor, dates, costs

### 2. Part Arrival Flow
**Package Header** → contains multiple **Part Arrivals**
- Arrivals link back to **Purchase Order Lines**
- Supports partial fulfillment (multiple arrivals per line)
- Tracks receiving dates, quantities, quality checks

### 3. Inventory Flow
**Inventory Movements** track all inventory changes:
- Arrivals (from Part Arrivals)
- Issues (to maintenance/work orders)
- Adjustments, transfers, returns

**Active Inventory** maintains current stock levels by location

## Data Model Entities

### Core Tables (Simple CRUD Models)

#### 1. PurchaseOrderHeader
**Purpose**: Represents a purchase order document

**Fields** (inherits from UserCreatedBase):
- `po_number` (String, Unique, Required) - Purchase order number
- `vendor_name` (String, Required) - Supplier/vendor name
- `vendor_contact` (String, Optional) - Vendor contact info
- `order_date` (Date, Required) - Date order was placed
- `expected_delivery_date` (Date, Optional) - Expected arrival
- `status` (String, Default 'Draft') - Draft/Submitted/Partial/Complete/Cancelled
- `total_cost` (Float, Optional) - Total PO cost
- `shipping_cost` (Float, Optional) - Shipping charges
- `tax_amount` (Float, Optional) - Tax amount
- `notes` (Text, Optional) - Order notes
- `major_location_id` (Integer, Foreign Key to MajorLocation) - Delivery location
- `event_id` (Integer, Foreign Key to Event, Optional) - Related event for tracking

**Relationships**:
- `purchase_order_lines` (One-to-Many to PurchaseOrderLine)
- `major_location` (Many-to-One to MajorLocation)
- `event` (Many-to-One to Event)

**Properties**:
- `is_draft` - Check if status is Draft
- `is_submitted` - Check if status is Submitted
- `is_complete` - Check if status is Complete
- `is_cancelled` - Check if status is Cancelled
- `lines_count` - Count of order lines
- `total_quantity` - Sum of all line quantities

**Methods**:
- `calculate_total()` - Calculate total cost from lines
- `to_dict()` - Convert to dictionary
- `from_dict()` - Create from dictionary

---

#### 2. PurchaseOrderLine
**Purpose**: Individual line items within a purchase order

**Fields** (inherits from UserCreatedBase):
- `purchase_order_id` (Integer, Foreign Key to PurchaseOrderHeader, Required)
- `part_id` (Integer, Foreign Key to Part, Required)
- `quantity_ordered` (Float, Required) - Quantity ordered
- `quantity_received` (Float, Default 0.0) - Quantity received so far
- `unit_cost` (Float, Required) - Cost per unit
- `line_total` (Float, Computed) - Calculated total
- `line_number` (Integer, Required) - Line number on PO
- `expected_delivery_date` (Date, Optional) - Expected arrival for this line
- `notes` (Text, Optional) - Line-specific notes
- `status` (String, Default 'Pending') - Pending/Partial/Complete/Cancelled

**Relationships**:
- `purchase_order` (Many-to-One to PurchaseOrderHeader)
- `part` (Many-to-One to Part)
- `part_demands` (Many-to-Many to PartDemand through association table)
- `part_arrivals` (One-to-Many to PartArrival)

**Properties**:
- `quantity_remaining` - quantity_ordered - quantity_received
- `is_complete` - quantity_received >= quantity_ordered
- `is_partial` - 0 < quantity_received < quantity_ordered
- `fulfillment_percentage` - (quantity_received / quantity_ordered) * 100

**Methods**:
- `calculate_line_total()` - Calculate line total
- `update_quantity_received(amount)` - Update received quantity
- `to_dict()` - Convert to dictionary
- `from_dict()` - Create from dictionary

---

#### 3. PartDemandPurchaseOrderLine (Association Table)
**Purpose**: Links part demands from maintenance to purchase order lines

**Fields** (inherits from UserCreatedBase):
- `part_demand_id` (Integer, Foreign Key to PartDemand, Required)
- `purchase_order_line_id` (Integer, Foreign Key to PurchaseOrderLine, Required)
- `quantity_allocated` (Float, Required) - Quantity allocated from this PO line
- `notes` (Text, Optional) - Allocation notes

**Relationships**:
- `part_demand` (Many-to-One to PartDemand)
- `purchase_order_line` (Many-to-One to PurchaseOrderLine)

**Methods**:
- `to_dict()` - Convert to dictionary
- `from_dict()` - Create from dictionary

---

#### 4. PackageHeader
**Purpose**: Represents a physical package/shipment arrival

**Fields** (inherits from UserCreatedBase):
- `package_number` (String, Unique, Required) - Tracking/package number
- `tracking_number` (String, Optional) - Carrier tracking number
- `carrier` (String, Optional) - Shipping carrier
- `received_date` (Date, Required) - Date package received
- `received_by_id` (Integer, Foreign Key to User) - Who received it
- `major_location_id` (Integer, Foreign Key to MajorLocation) - Where received
- `notes` (Text, Optional) - Package notes
- `status` (String, Default 'Received') - Received/Inspected/Processed

**Relationships**:
- `part_arrivals` (One-to-Many to PartArrival)
- `major_location` (Many-to-One to MajorLocation)
- `received_by` (Many-to-One to User)

**Properties**:
- `total_items` - Count of part arrivals
- `is_processed` - Check if status is Processed

**Methods**:
- `to_dict()` - Convert to dictionary
- `from_dict()` - Create from dictionary

---

#### 5. PartArrival
**Purpose**: Individual parts received in a package

**Fields** (inherits from UserCreatedBase):
- `package_header_id` (Integer, Foreign Key to PackageHeader, Required)
- `purchase_order_line_id` (Integer, Foreign Key to PurchaseOrderLine, Required)
- `part_id` (Integer, Foreign Key to Part, Required)
- `quantity_received` (Float, Required) - Quantity in this arrival
- `quantity_accepted` (Float, Default 0.0) - Quantity passed inspection
- `quantity_rejected` (Float, Default 0.0) - Quantity failed inspection
- `condition` (String, Default 'Good') - Good/Damaged/Mixed
- `inspection_notes` (Text, Optional) - Quality inspection notes
- `received_date` (Date, Required) - Date received
- `status` (String, Default 'Pending') - Pending/Inspected/Accepted/Rejected

**Relationships**:
- `package_header` (Many-to-One to PackageHeader)
- `purchase_order_line` (Many-to-One to PurchaseOrderLine)
- `part` (Many-to-One to Part)
- `inventory_movements` (One-to-Many to InventoryMovement)

**Properties**:
- `is_inspected` - Check if status is Inspected/Accepted/Rejected
- `is_accepted` - Check if status is Accepted
- `acceptance_rate` - (quantity_accepted / quantity_received) * 100

**Methods**:
- `to_dict()` - Convert to dictionary
- `from_dict()` - Create from dictionary

---

#### 6. ActiveInventory
**Purpose**: Current inventory levels by part and location

**Fields** (inherits from UserCreatedBase):
- `part_id` (Integer, Foreign Key to Part, Required)
- `major_location_id` (Integer, Foreign Key to MajorLocation, Required)
- `quantity_on_hand` (Float, Default 0.0) - Current quantity
- `quantity_allocated` (Float, Default 0.0) - Reserved for demands
- `quantity_available` (Float, Computed) - on_hand - allocated
- `last_movement_date` (DateTime, Optional) - Last inventory movement
- `unit_cost_avg` (Float, Optional) - Average unit cost

**Unique Constraint**: (part_id, major_location_id)

**Relationships**:
- `part` (Many-to-One to Part)
- `major_location` (Many-to-One to MajorLocation)

**Properties**:
- `is_available` - quantity_available > 0
- `is_low_stock` - Compare to part.minimum_stock_level
- `total_value` - quantity_on_hand * unit_cost_avg

**Methods**:
- `adjust_quantity(amount, movement_type)` - Adjust inventory
- `to_dict()` - Convert to dictionary
- `from_dict()` - Create from dictionary

---

#### 7. InventoryMovement
**Purpose**: Audit trail for all inventory changes

**Fields** (inherits from UserCreatedBase):
- `part_id` (Integer, Foreign Key to Part, Required)
- `major_location_id` (Integer, Foreign Key to MajorLocation, Required)
- `movement_type` (String, Required) - Arrival/Issue/Adjustment/Transfer/Return
- `quantity` (Float, Required) - Quantity moved (positive or negative)
- `movement_date` (DateTime, Required) - When movement occurred
- `reference_type` (String, Optional) - Type of reference (PartArrival, PartDemand, etc.)
- `reference_id` (Integer, Optional) - ID of reference record
- `from_location_id` (Integer, Foreign Key to MajorLocation, Optional) - For transfers
- `to_location_id` (Integer, Foreign Key to MajorLocation, Optional) - For transfers
- `unit_cost` (Float, Optional) - Cost per unit at time of movement
- `notes` (Text, Optional) - Movement notes
- `part_arrival_id` (Integer, Foreign Key to PartArrival, Optional) - For arrivals
- `part_demand_id` (Integer, Foreign Key to PartDemand, Optional) - For issues
- `initial_arrival_id` (Integer, Foreign Key to PartArrival, Optional) - **Traceability: Original part arrival**
- `previous_movement_id` (Integer, Foreign Key to InventoryMovement, Optional) - **Traceability: Previous movement in chain**

**Relationships**:
- `part` (Many-to-One to Part)
- `major_location` (Many-to-One to MajorLocation)
- `from_location` (Many-to-One to MajorLocation)
- `to_location` (Many-to-One to MajorLocation)
- `part_arrival` (Many-to-One to PartArrival)
- `part_demand` (Many-to-One to PartDemand)
- `initial_arrival` (Many-to-One to PartArrival) - **Links to original arrival**
- `previous_movement` (Many-to-One to InventoryMovement) - **Links to previous movement**
- `subsequent_movements` (One-to-Many to InventoryMovement) - **All movements that followed this one**

**Properties**:
- `is_arrival` - movement_type == 'Arrival'
- `is_issue` - movement_type == 'Issue'
- `is_transfer` - movement_type == 'Transfer'
- `total_value` - quantity * unit_cost

**Methods**:
- `to_dict()` - Convert to dictionary
- `from_dict()` - Create from dictionary
- `get_movement_chain()` - Get complete chain of movements back to arrival
- `get_source_arrival()` - Get original part arrival via initial_arrival_id

---

### Movement Traceability Chain

The `InventoryMovement` table now includes enhanced traceability through two optional fields:

**`initial_arrival_id`** (Foreign Key to PartArrival):
- Points to the original `PartArrival` that introduced this inventory into the system
- Preserved across all subsequent movements (transfers, adjustments)
- Allows instant lookup of original purchase order and receiving information
- Enables cost tracking and quality tracing back to source
- Example: If parts are transferred between locations multiple times, all movements still reference the original arrival

**`previous_movement_id`** (Foreign Key to InventoryMovement):
- Points to the immediately preceding movement in the chain
- Creates a linked list of movements for the same inventory item
- Enables full movement history reconstruction
- Allows tracking of part journey through locations and transactions
- Example: Issue → Transfer → Transfer → Arrival forms a traceable chain

**Usage Pattern**:

1. **Initial Arrival Movement** (when parts are received):
   ```
   movement_type: "Arrival"
   part_arrival_id: [A]
   initial_arrival_id: [A]        # Same as part_arrival_id
   previous_movement_id: null      # First movement
   ```

2. **Subsequent Movements** (transfers, adjustments):
   ```
   movement_type: "Transfer"
   initial_arrival_id: [A]        # Copied from previous movement
   previous_movement_id: [M1]     # Links to previous movement
   ```

3. **Issue to Maintenance**:
   ```
   movement_type: "Issue"
   part_demand_id: [D]
   initial_arrival_id: [A]        # Still traces back to original arrival
   previous_movement_id: [M2]     # Links to previous movement
   ```

**Traceability Benefits**:
- **Forward Trace**: From arrival → all subsequent movements → final usage
- **Backward Trace**: From any movement → complete history → original purchase
- **Cost Tracking**: Follow cost from purchase through all movements
- **Quality Issues**: Trace defective parts back to original vendor/PO
- **Audit Trail**: Complete chain of custody for parts
- **Compliance**: Meet regulatory requirements for part tracking

**Example Scenario**:
```
Part arrives from vendor (Arrival M1, initial_arrival_id=A1)
  ↓
Transferred to main warehouse (Transfer M2, initial_arrival_id=A1, previous=M1)
  ↓
Transferred to field location (Transfer M3, initial_arrival_id=A1, previous=M2)
  ↓
Issued to maintenance work (Issue M4, initial_arrival_id=A1, previous=M3)

At M4, you can trace:
- M4.previous_movement_id → M3 (Transfer)
- M3.previous_movement_id → M2 (Transfer)
- M2.previous_movement_id → M1 (Arrival)
- M4.initial_arrival_id → A1 (Original PartArrival)
- A1.purchase_order_line_id → PO Line
- PO Line.purchase_order_id → Original Purchase Order
```

---

## Manager Classes (Business Logic)

### 1. PurchaseOrderManager
**Purpose**: Handles all purchase order business logic

**Responsibilities**:
- Create purchase orders from part demands
- Link part demands to purchase order lines
- Update order status based on arrivals
- Calculate totals and costs
- Generate purchase order events
- Handle order cancellation and modifications

**Key Methods**:
- `create_from_part_demands(part_demands, vendor_info, user_id)` - Create PO from demands
- `add_line(po_id, part_id, quantity, unit_cost, user_id)` - Add line to PO
- `link_part_demand(po_line_id, part_demand_id, quantity, user_id)` - Link demand to line
- `submit_order(po_id, user_id)` - Submit PO for ordering
- `cancel_order(po_id, reason, user_id)` - Cancel PO
- `update_line_received_quantity(po_line_id, quantity, user_id)` - Update received qty
- `check_completion_status(po_id, user_id)` - Check and update PO status
- `get_unfulfilled_lines(po_id)` - Get lines not yet complete
- `get_linked_part_demands(po_id)` - Get all part demands for PO

---

### 2. PartArrivalManager
**Purpose**: Handles receiving and inspecting parts

**Responsibilities**:
- Create package headers and part arrivals
- Link arrivals to purchase order lines
- Handle inspection and quality control
- Update purchase order line quantities
- Trigger inventory movements upon acceptance
- Handle partial fulfillment tracking

**Key Methods**:
- `create_package(package_number, location_id, received_by_id, user_id)` - Create package
- `receive_parts(package_id, po_line_id, quantity, condition, user_id)` - Receive parts
- `inspect_arrival(arrival_id, accepted_qty, rejected_qty, notes, user_id)` - Inspect
- `accept_arrival(arrival_id, user_id)` - Accept parts (triggers inventory movement)
- `reject_arrival(arrival_id, reason, user_id)` - Reject parts
- `process_package(package_id, user_id)` - Process entire package
- `get_pending_inspections(location_id)` - Get arrivals needing inspection

---

### 3. InventoryManager
**Purpose**: Manages all inventory movements and levels

**Responsibilities**:
- Create inventory movements for all transactions
- Update active inventory levels
- Handle part issues to maintenance
- Process inventory adjustments
- Handle inventory transfers between locations
- Calculate average costs
- Check stock availability
- **Maintain traceability chain via initial_arrival_id and previous_movement_id**

**Key Methods**:
- `record_arrival(part_arrival_id, user_id)` - Record arrival movement
  - Sets initial_arrival_id = part_arrival_id
  - Sets previous_movement_id = null (first in chain)
  
- `issue_to_demand(part_demand_id, quantity, location_id, user_id, source_movement_id=None)` - Issue to maintenance
  - Copies initial_arrival_id from source movement or active inventory
  - Sets previous_movement_id = source_movement_id
  
- `adjust_inventory(part_id, location_id, quantity, reason, user_id, source_movement_id=None)` - Manual adjustment
  - Maintains initial_arrival_id if adjusting existing inventory
  - Links previous_movement_id if adjustment relates to prior movement
  
- `transfer_between_locations(part_id, from_loc, to_loc, quantity, user_id, source_movement_id)` - Transfer
  - Preserves initial_arrival_id from source movement
  - Sets previous_movement_id = source_movement_id
  
- `return_from_demand(part_demand_id, quantity, condition, user_id)` - Return unused
  - Traces back to original issue movement to maintain chain
  - Preserves initial_arrival_id from original issue
  
- `check_availability(part_id, location_id, quantity)` - Check if available
- `get_inventory_by_location(location_id)` - Get all inventory at location
- `get_inventory_by_part(part_id)` - Get inventory across all locations
- `allocate_to_demand(part_demand_id, quantity, location_id, user_id)` - Reserve inventory
- `deallocate_from_demand(part_demand_id, quantity, user_id)` - Release reservation
- `get_movement_history(movement_id)` - Get complete chain from movement back to arrival
- `get_movements_from_arrival(arrival_id)` - Get all movements originating from an arrival

---

### 4. PartDemandManager
**Purpose**: Extends maintenance part demand functionality for purchasing integration

**Responsibilities**:
- Identify unfulfilled part demands
- Generate purchase recommendations
- Link demands to purchase orders
- Track demand fulfillment status
- Handle demand priority and urgency

**Key Methods**:
- `get_unfulfilled_demands(location_id, asset_type_id)` - Get pending demands
- `get_purchase_recommendations()` - Analyze and recommend purchases
- `group_demands_by_part()` - Group demands for bulk ordering
- `calculate_demand_urgency(demand_id)` - Calculate priority score
- `mark_demand_fulfilled(demand_id, inventory_movement_id, user_id)` - Mark complete
- `check_inventory_availability(demand_id)` - Check if parts available in inventory

---

## Data Relationships

### Purchase Order Flow
```
Part (existing)
    ↓
PurchaseOrderLine
    ↓ belongs to
PurchaseOrderHeader
    ↓ has event
Event (tracking)
    ↓ has comments
Comment (discussion)
```

### Part Arrival Flow
```
PurchaseOrderLine
    ↓ fulfilled by
PartArrival
    ↓ belongs to
PackageHeader
    ↓ creates
InventoryMovement (Arrival)
    ↓ updates
ActiveInventory
```

### Part Issue Flow
```
PartDemand (from Maintenance)
    ↓ linked to
PurchaseOrderLine (optional)
    ↓ fulfilled from
ActiveInventory
    ↓ creates
InventoryMovement (Issue)
```

### Complete Traceability Chain
```
Maintenance Action (Phase 5)
    ↓ creates
PartDemand
    ↓ linked to
PurchaseOrderLine
    ↓ part of
PurchaseOrderHeader
    ↓ received as
PartArrival
    ↓ creates
InventoryMovement (Arrival)
    ↓ updates
ActiveInventory
    ↓ creates
InventoryMovement (Issue)
    ↓ fulfills
PartDemand
```

## Integration Points

### With Phase 5 (Maintenance)
1. **PartDemand**: Existing model gets extended relationships
   - Add relationship to PurchaseOrderLine through association table
   - Manager handles checking inventory before creating demands
   - Links issues to inventory movements

2. **Action**: No changes needed
   - Part demands continue to work as before
   - Manager can check inventory availability

### With Phase 1 (Core)
1. **MajorLocation**: Used for inventory location tracking
2. **Event**: Purchase orders create events for tracking
3. **Comment**: Events support comments on POs and arrivals
4. **User**: All operations track user performing action

### With Phase 4 (Supply)
1. **Part**: No changes to existing model
   - Relationships added for purchase orders and inventory
2. **Tool**: Future integration for tool tracking (Phase 7)

## Status Values

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

## Workflow Processes

### 1. Purchase Order Creation
1. User reviews unfulfilled part demands
2. PartDemandManager groups demands by part
3. User creates purchase order header
4. PurchaseOrderManager creates lines from demands
5. Manager links demands to lines
6. User submits order
7. Manager creates event for tracking

### 2. Part Receiving
1. Package arrives at location
2. User creates package header
3. PartArrivalManager receives parts against PO lines
4. User inspects parts
5. Manager records inspection results
6. User accepts parts
7. Manager creates inventory movement (Arrival)
8. InventoryManager updates active inventory
9. Manager updates PO line received quantity
10. Manager checks PO completion status

### 3. Part Issuing to Maintenance
1. Maintenance creates part demand
2. PartDemandManager checks inventory availability
3. If available: User issues parts from inventory
4. InventoryManager creates inventory movement (Issue)
5. Manager updates active inventory
6. Manager marks part demand as fulfilled
7. If not available: Demand remains unfulfilled for purchasing

### 4. Partial Fulfillment
1. First package arrives with partial quantity
2. PartArrivalManager receives partial quantity
3. Manager updates PO line received quantity
4. PO line status → Partial
5. PO header status → Partial
6. Second package arrives
7. Manager receives remaining quantity
8. Line status → Complete
9. Manager checks if all lines complete
10. If yes: PO status → Complete

## Key Benefits

1. **Traceability**: Complete chain from demand → order → arrival → inventory
2. **Flexibility**: Supports partial fulfillment and multiple arrivals
3. **Integration**: Seamless connection with maintenance system
4. **Simplicity**: Clear separation between data and logic
5. **Scalability**: Manager pattern allows complex logic without cluttering models
6. **Audit Trail**: Full tracking of all inventory movements
7. **Location Aware**: Tracks inventory by location
8. **Cost Tracking**: Maintains cost information throughout chain

## Future Enhancements (Phase 7+)

### Potential Additions
1. **Vendor Management**: Vendor table with ratings, contacts, terms
2. **Contract Pricing**: Agreed pricing for parts by vendor
3. **Automatic Reordering**: Trigger POs when stock below minimum
4. **Inventory Valuation**: FIFO, LIFO, average cost methods (enabled by traceability chain)
5. **Lot/Serial Tracking**: Track individual items or lots (extends traceability chain)
6. **Expiration Tracking**: For parts with shelf life
7. **Cycle Counting**: Regular inventory verification
8. **RFQ Process**: Request for Quote workflow
9. **Receiving Inspection**: Detailed quality control checklists
10. **Returns to Vendor**: Process for returning defective parts

### Traceability-Enhanced Features (Enabled by initial_arrival_id and previous_movement_id)
1. **Warranty Tracking**: Trace warranty claims back to original vendor and PO
2. **Quality Analysis**: Identify patterns in defective parts from specific vendors/batches
3. **Cost Analysis**: Track actual cost propagation through inventory movements
4. **Compliance Reporting**: Generate complete chain of custody reports for audits
5. **Root Cause Analysis**: When issues occur, trace back to source
6. **Vendor Performance**: Analyze quality and delivery performance by tracing arrivals
7. **Inventory Age Tracking**: Calculate true age of inventory from arrival date
8. **Movement Pattern Analysis**: Identify inefficient transfer patterns
9. **Lifecycle Reporting**: Complete part lifecycle from purchase to usage
10. **Regulatory Compliance**: Meet requirements for part traceability (aviation, medical, etc.)

## File Structure

```
app/models/purchasing/
├── __init__.py
├── build.py                          # Phase 6 build module
├── base/                             # Data models (CRUD only)
│   ├── __init__.py
│   ├── purchase_order_header.py
│   ├── purchase_order_line.py
│   ├── part_demand_purchase_order_line.py
│   ├── package_header.py
│   ├── part_arrival.py
│   ├── active_inventory.py
│   └── inventory_movement.py
├── managers/                         # Business logic
│   ├── __init__.py
│   ├── purchase_order_manager.py
│   ├── part_arrival_manager.py
│   ├── inventory_manager.py
│   └── part_demand_manager.py
└── utils/                           # Helper functions
    ├── __init__.py
    ├── purchasing_helpers.py
    └── inventory_helpers.py
```

## Database Schema Updates

### New Tables
1. `purchase_order_headers`
2. `purchase_order_lines`
3. `part_demand_purchase_order_lines` (association)
4. `package_headers`
5. `part_arrivals`
6. `active_inventory`
7. `inventory_movements`

### Modified Tables
1. `part_demands` - Add relationships to purchase order lines and inventory movements

### Indexes Needed
1. `purchase_order_headers.po_number` (unique)
2. `purchase_order_lines.purchase_order_id`
3. `part_arrivals.purchase_order_line_id`
4. `active_inventory.part_id`
5. `active_inventory.major_location_id`
6. `active_inventory(part_id, major_location_id)` (unique composite)
7. `inventory_movements.part_id`
8. `inventory_movements.major_location_id`
9. `inventory_movements.movement_date`
10. `inventory_movements.initial_arrival_id` (for traceability queries)
11. `inventory_movements.previous_movement_id` (for chain traversal)
12. `inventory_movements.part_arrival_id`
13. `inventory_movements.part_demand_id`

## Testing Strategy

### Unit Tests
1. Test each model's CRUD operations
2. Test manager class methods independently
3. Test relationships and foreign keys
4. Test property calculations

### Integration Tests
1. Test complete purchase order flow
2. Test part receiving and inspection
3. Test inventory movement creation
4. Test partial fulfillment scenarios
5. Test multi-location inventory
6. **Test traceability chain maintenance across movements**
7. **Test initial_arrival_id preservation through transfers**
8. **Test previous_movement_id linkage correctness**

### End-to-End Tests
1. Create maintenance demand → PO → receive → issue
2. Test multiple arrivals for one PO line
3. Test inventory transfers
4. Test demand fulfillment from inventory
5. **Test complete traceability chain**:
   - Create PO and receive parts (Arrival M1)
   - Transfer to location A (Transfer M2, verify chain: M2→M1, initial_arrival preserved)
   - Transfer to location B (Transfer M3, verify chain: M3→M2→M1, initial_arrival preserved)
   - Issue to maintenance (Issue M4, verify chain: M4→M3→M2→M1, initial_arrival preserved)
   - Verify can trace from M4 back to original PO
6. **Test movement history queries**:
   - Query all movements from initial arrival
   - Query movement chain backwards from any point
   - Verify no broken links in chain

## Success Criteria

- [ ] All data models created and working
- [ ] All manager classes implemented
- [ ] Purchase orders can be created from demands
- [ ] Parts can be received against PO lines
- [ ] Inventory movements track all changes
- [ ] Active inventory updates correctly
- [ ] Partial fulfillment works correctly
- [ ] Complete traceability chain functional
- [ ] Integration with maintenance part demands works
- [ ] **initial_arrival_id correctly set and preserved across all movement types**
- [ ] **previous_movement_id correctly links movements in sequence**
- [ ] **Can trace any movement back to original part arrival and purchase order**
- [ ] **Movement history queries work correctly**
- [ ] All tests pass

## Implementation Order

### Phase 6A: Core Models
1. PurchaseOrderHeader model
2. PurchaseOrderLine model
3. PartDemandPurchaseOrderLine association model
4. PackageHeader model
5. PartArrival model
6. ActiveInventory model
7. InventoryMovement model

### Phase 6B: Manager Classes
1. PurchaseOrderManager
2. PartArrivalManager
3. InventoryManager
4. PartDemandManager (extension)

### Phase 6C: Integration
1. Update PartDemand relationships
2. Create build.py for Phase 6
3. Update main build.py orchestrator
4. Create test data

### Phase 6D: Routes and UI
1. Purchase order routes
2. Receiving routes
3. Inventory routes
4. UI templates

## Notes

- **Manager classes are NOT database tables** - they are Python classes that handle business logic
- All database tables inherit from `UserCreatedBase` for audit trail
- Event system integration for purchase order tracking
- Comment system available for purchase orders and arrivals
- Status fields track lifecycle of orders and arrivals
- Inventory movements create complete audit trail
- Location-based inventory tracking from day one
- **Enhanced traceability**: `initial_arrival_id` and `previous_movement_id` create a complete chain from any inventory movement back to original purchase
- **Traceability fields are optional** but should be populated for all movements to maintain chain integrity
- **Chain maintenance is manager responsibility** - InventoryManager ensures traceability fields are correctly set for all movements


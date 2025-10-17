# Phase 6: Inventory and Purchasing - Implementation Plan

## Overview

This document provides a step-by-step implementation plan for Phase 6 of the Asset Management System. Phase 6 introduces inventory and purchasing capabilities that integrate with the existing maintenance system (Phase 5).

## Implementation Philosophy

### Core Principles
1. **Build incrementally** - Each sub-phase is independently testable
2. **Test continuously** - Write tests as you build
3. **Simple first** - Start with basic CRUD, add complexity via managers
4. **Integration second** - Get core functionality working before complex integrations

## Phase Structure

### Phase 6A: Purchase Order System ✅ TODO
**Focus**: Basic purchase order creation and management
- Purchase order data models
- PurchaseOrderManager for business logic
- Basic CRUD operations
- Event integration

### Phase 6B: Part Receiving System ✅ TODO
**Focus**: Receiving and inspecting parts
- Package and arrival data models
- PartArrivalManager for receiving workflow
- Link arrivals to purchase orders
- Handle partial fulfillment

### Phase 6C: Inventory System ✅ TODO
**Focus**: Inventory tracking and movements
- Inventory movement and active inventory models
- InventoryManager for all inventory operations
- Integration with arrivals and issues
- Location-based tracking

### Phase 6D: Integration and Workflows ✅ TODO
**Focus**: Complete end-to-end integration
- Link maintenance part demands to purchasing
- PartDemandManager extensions
- Complete traceability chain
- End-to-end workflows

### Phase 6E: Routes and UI ✅ TODO
**Focus**: Web interface
- Purchase order routes and templates
- Receiving routes and templates
- Inventory routes and templates
- Dashboards and reports

## Detailed Implementation Steps

---

## Phase 6A: Purchase Order System

### A.1 - Create Base Models ✅ TODO

**Files to Create**:
```
app/models/purchasing/
├── __init__.py
└── base/
    ├── __init__.py
    ├── purchase_order_header.py
    ├── purchase_order_line.py
    └── part_demand_purchase_order_line.py
```

**Implementation Order**:

#### 1. Create directory structure
```bash
mkdir -p app/models/purchasing/base
mkdir -p app/models/purchasing/managers
mkdir -p app/models/purchasing/utils
```

#### 2. Implement PurchaseOrderHeader Model
**File**: `app/models/purchasing/base/purchase_order_header.py`

**Key Features**:
- Inherits from UserCreatedBase
- Fields: po_number, vendor_name, status, dates, costs
- Relationships to lines, location, event
- Properties: is_draft, is_complete, lines_count
- Methods: calculate_total(), to_dict(), from_dict()

**Test Cases**:
- Create purchase order header
- Calculate total from lines
- Status transitions
- Event creation

#### 3. Implement PurchaseOrderLine Model
**File**: `app/models/purchasing/base/purchase_order_line.py`

**Key Features**:
- Inherits from UserCreatedBase
- Fields: part_id, quantities, costs, status
- Relationships to header, part, arrivals
- Properties: quantity_remaining, is_complete, fulfillment_percentage
- Methods: calculate_line_total(), update_quantity_received()

**Test Cases**:
- Create PO line
- Calculate line totals
- Track received quantities
- Fulfillment calculations

#### 4. Implement Association Table
**File**: `app/models/purchasing/base/part_demand_purchase_order_line.py`

**Key Features**:
- Links PartDemand to PurchaseOrderLine
- Tracks quantity allocated
- Many-to-many relationship handler

**Test Cases**:
- Link demand to PO line
- Track allocated quantities
- Multiple demands per line

### A.2 - Create PurchaseOrderManager ✅ TODO

**File**: `app/models/purchasing/managers/purchase_order_manager.py`

**Implementation**:

```python
class PurchaseOrderManager:
    """
    Handles all purchase order business logic
    Models handle CRUD, Manager handles workflow
    """
    
    @staticmethod
    def create_from_part_demands(part_demands, vendor_info, user_id):
        """
        Create PO from maintenance part demands
        
        Args:
            part_demands: List of PartDemand objects
            vendor_info: Dict with vendor details
            user_id: User creating the PO
            
        Returns:
            PurchaseOrderHeader object
        """
        # 1. Group demands by part
        # 2. Create PO header
        # 3. Create lines for each part
        # 4. Link demands to lines
        # 5. Create event
        # 6. Return PO
        pass
    
    @staticmethod
    def add_line(po_id, part_id, quantity, unit_cost, user_id):
        """Add new line to existing PO"""
        pass
    
    @staticmethod
    def submit_order(po_id, user_id):
        """Submit PO for ordering"""
        pass
    
    @staticmethod
    def cancel_order(po_id, reason, user_id):
        """Cancel entire PO"""
        pass
    
    @staticmethod
    def check_completion_status(po_id, user_id):
        """Check if PO is complete and update status"""
        pass
```

**Test Cases**:
- Create PO from multiple demands
- Add/remove lines
- Submit and cancel orders
- Status management

### A.3 - Build System Integration ✅ TODO

**File**: `app/models/purchasing/build.py`

**Implementation**:
```python
def build_models():
    """Register Phase 6A models with SQLAlchemy"""
    from app.models.purchasing.base import (
        PurchaseOrderHeader,
        PurchaseOrderLine,
        PartDemandPurchaseOrderLine
    )
    return True

def init_purchase_order_data():
    """Create initial test data"""
    # Create sample PO
    # Create sample lines
    pass
```

**Update**: `app/build.py` to call Phase 6 build

**Test Cases**:
- Database tables created correctly
- Relationships work
- Sample data loads

---

## Phase 6B: Part Receiving System

### B.1 - Create Receiving Models ✅ TODO

**Files to Create**:
```
app/models/purchasing/base/
├── package_header.py
└── part_arrival.py
```

#### 1. Implement PackageHeader Model
**File**: `app/models/purchasing/base/package_header.py`

**Key Features**:
- Package/shipment tracking
- Links to location and receiver
- Contains part arrivals
- Status tracking

**Test Cases**:
- Create package
- Link to arrivals
- Track status

#### 2. Implement PartArrival Model
**File**: `app/models/purchasing/base/part_arrival.py`

**Key Features**:
- Individual part receipts
- Links to package and PO line
- Inspection results
- Quantity tracking (received, accepted, rejected)

**Test Cases**:
- Create arrival
- Record inspection
- Link to PO line
- Calculate acceptance rate

### B.2 - Create PartArrivalManager ✅ TODO

**File**: `app/models/purchasing/managers/part_arrival_manager.py`

**Implementation**:

```python
class PartArrivalManager:
    """
    Handles receiving and inspection workflow
    """
    
    @staticmethod
    def create_package(package_number, location_id, received_by_id, user_id):
        """Create new package for receiving"""
        pass
    
    @staticmethod
    def receive_parts(package_id, po_line_id, quantity, condition, user_id):
        """Receive parts into package"""
        # 1. Create PartArrival
        # 2. Link to package and PO line
        # 3. Set initial quantities
        # 4. Create event
        pass
    
    @staticmethod
    def inspect_arrival(arrival_id, accepted_qty, rejected_qty, notes, user_id):
        """Record inspection results"""
        # 1. Update accepted/rejected quantities
        # 2. Update status
        # 3. Add inspection notes
        pass
    
    @staticmethod
    def accept_arrival(arrival_id, user_id):
        """Accept parts (triggers inventory movement)"""
        # 1. Validate inspection complete
        # 2. Update arrival status
        # 3. Update PO line received quantity
        # 4. Check PO line completion
        # 5. Trigger InventoryManager.record_arrival()
        # 6. Create event
        pass
    
    @staticmethod
    def reject_arrival(arrival_id, reason, user_id):
        """Reject parts (no inventory movement)"""
        pass
```

**Test Cases**:
- Create package and receive parts
- Inspect with accept/reject
- Update PO line quantities
- Partial vs complete fulfillment

### B.3 - Integration Tests ✅ TODO

**Test Scenarios**:
1. Single arrival completes PO line
2. Multiple arrivals for one PO line (partial fulfillment)
3. Reject entire arrival
4. Mixed acceptance/rejection
5. Multiple PO lines in one package

---

## Phase 6C: Inventory System

### C.1 - Create Inventory Models ✅ TODO

**Files to Create**:
```
app/models/purchasing/base/
├── active_inventory.py
└── inventory_movement.py
```

#### 1. Implement ActiveInventory Model
**File**: `app/models/purchasing/base/active_inventory.py`

**Key Features**:
- Current stock by part and location
- Quantity on hand and allocated
- Average cost tracking
- Unique constraint on (part_id, location_id)

**Test Cases**:
- Create inventory record
- Update quantities
- Calculate available quantity
- Track costs

#### 2. Implement InventoryMovement Model
**File**: `app/models/purchasing/base/inventory_movement.py`

**Key Features**:
- Audit trail for all movements
- Movement types (Arrival, Issue, Adjustment, Transfer, Return)
- References to source records
- Location tracking

**Test Cases**:
- Create movement records
- Link to arrivals and demands
- Track transfers
- Calculate totals

### C.2 - Create InventoryManager ✅ TODO

**File**: `app/models/purchasing/managers/inventory_manager.py`

**Implementation**:

```python
class InventoryManager:
    """
    Manages all inventory movements and levels
    Central hub for inventory operations
    """
    
    @staticmethod
    def record_arrival(part_arrival_id, user_id):
        """
        Record inventory arrival from part arrival
        Called by PartArrivalManager.accept_arrival()
        """
        # 1. Get part arrival details
        # 2. Create InventoryMovement (Arrival type)
        # 3. Update/create ActiveInventory
        # 4. Update average cost
        # 5. Create event
        pass
    
    @staticmethod
    def issue_to_demand(part_demand_id, quantity, location_id, user_id):
        """
        Issue parts to maintenance from inventory
        """
        # 1. Validate availability
        # 2. Create InventoryMovement (Issue type)
        # 3. Update ActiveInventory (decrease)
        # 4. Link to PartDemand
        # 5. Update Part stock level
        # 6. Create event
        pass
    
    @staticmethod
    def adjust_inventory(part_id, location_id, quantity, reason, user_id):
        """Manual inventory adjustment"""
        pass
    
    @staticmethod
    def transfer_between_locations(part_id, from_loc, to_loc, quantity, user_id):
        """Transfer inventory between locations"""
        # 1. Validate from_location has quantity
        # 2. Create movement (Transfer type, negative)
        # 3. Create movement (Transfer type, positive)
        # 4. Update both location inventories
        pass
    
    @staticmethod
    def check_availability(part_id, location_id, quantity):
        """Check if parts available"""
        # Return True/False and available quantity
        pass
    
    @staticmethod
    def allocate_to_demand(part_demand_id, quantity, location_id, user_id):
        """Reserve inventory for demand"""
        # Update quantity_allocated
        pass
    
    @staticmethod
    def deallocate_from_demand(part_demand_id, quantity, user_id):
        """Release reserved inventory"""
        pass
```

**Test Cases**:
- Record arrivals and update inventory
- Issue to maintenance demands
- Handle transfers between locations
- Track allocations
- Validate availability checks
- Calculate average costs

### C.3 - Integration with Phase 6B ✅ TODO

**Connect PartArrivalManager to InventoryManager**:

Update `PartArrivalManager.accept_arrival()`:
```python
def accept_arrival(arrival_id, user_id):
    # ... existing code ...
    
    # Trigger inventory movement
    from app.models.purchasing.managers import InventoryManager
    InventoryManager.record_arrival(arrival_id, user_id)
    
    # ... rest of code ...
```

**Test Cases**:
- Accept arrival creates inventory movement
- Inventory updates correctly
- Events created
- End-to-end from receive to inventory

---

## Phase 6D: Integration and Workflows

### D.1 - Extend PartDemand Integration ✅ TODO

**Update Phase 5 Models**:

**File**: `app/models/maintenance/base/part_demand.py`

Add relationships:
```python
# Add to PartDemand model
purchase_order_lines = relationship(
    'PurchaseOrderLine',
    secondary='part_demand_purchase_order_lines',
    back_populates='part_demands'
)

inventory_movements = relationship(
    'InventoryMovement',
    back_populates='part_demand'
)
```

### D.2 - Create PartDemandManager ✅ TODO

**File**: `app/models/purchasing/managers/part_demand_manager.py`

**Implementation**:

```python
class PartDemandManager:
    """
    Extension of maintenance part demand for purchasing integration
    Bridges Phase 5 and Phase 6
    """
    
    @staticmethod
    def get_unfulfilled_demands(location_id=None, asset_type_id=None):
        """Get all part demands not yet fulfilled"""
        # Query PartDemand where status != 'Fulfilled'
        # Optional filters by location or asset type
        pass
    
    @staticmethod
    def get_purchase_recommendations():
        """
        Analyze unfulfilled demands and recommend purchases
        Groups by part, calculates quantities
        """
        # 1. Get unfulfilled demands
        # 2. Check inventory availability
        # 3. Calculate needed quantities
        # 4. Group by part
        # 5. Return recommendations
        pass
    
    @staticmethod
    def check_inventory_availability(demand_id):
        """Check if demand can be fulfilled from inventory"""
        # Get demand
        # Check ActiveInventory at demand location
        # Return availability info
        pass
    
    @staticmethod
    def mark_demand_fulfilled(demand_id, inventory_movement_id, user_id):
        """Mark demand as fulfilled when issued from inventory"""
        pass
```

**Test Cases**:
- Get unfulfilled demands
- Generate purchase recommendations
- Check inventory before creating demand
- Mark demands fulfilled

### D.3 - Complete Workflow Testing ✅ TODO

**End-to-End Test Scenarios**:

#### Scenario 1: Demand → Purchase → Receive → Inventory → Issue
```python
def test_complete_workflow():
    # 1. Create maintenance action with part demand
    action = create_test_action()
    demand = create_test_part_demand(action)
    
    # 2. Create PO from demand
    po = PurchaseOrderManager.create_from_part_demands(
        [demand], vendor_info, user_id
    )
    
    # 3. Submit PO
    PurchaseOrderManager.submit_order(po.id, user_id)
    
    # 4. Receive parts
    package = PartArrivalManager.create_package(...)
    arrival = PartArrivalManager.receive_parts(
        package.id, po.lines[0].id, quantity, 'Good', user_id
    )
    
    # 5. Inspect and accept
    PartArrivalManager.inspect_arrival(arrival.id, quantity, 0, 'OK', user_id)
    PartArrivalManager.accept_arrival(arrival.id, user_id)
    
    # 6. Verify inventory updated
    inventory = ActiveInventory.query.filter_by(
        part_id=demand.part_id,
        location_id=location_id
    ).first()
    assert inventory.quantity_on_hand == quantity
    
    # 7. Issue to demand
    InventoryManager.issue_to_demand(demand.id, quantity, location_id, user_id)
    
    # 8. Verify demand fulfilled
    demand = PartDemand.query.get(demand.id)
    assert demand.status == 'Fulfilled'
    
    # 9. Verify traceability
    assert demand.purchase_order_lines[0].id == po.lines[0].id
    assert len(demand.inventory_movements) == 1
```

#### Scenario 2: Demand → Inventory (No PO Needed)
```python
def test_fulfill_from_inventory():
    # 1. Create existing inventory
    # 2. Create part demand
    # 3. Check inventory availability
    # 4. Issue directly from inventory
    # 5. Verify demand fulfilled without PO
```

#### Scenario 3: Partial PO Fulfillment
```python
def test_partial_fulfillment():
    # 1. Create PO for quantity 100
    # 2. Receive 40 parts
    # 3. Verify PO line status = Partial
    # 4. Receive 60 more parts
    # 5. Verify PO line status = Complete
    # 6. Verify PO header status = Complete
```

---

## Phase 6E: Routes and UI

### E.1 - Purchase Order Routes ✅ TODO

**File**: `app/routes/purchasing/purchase_orders.py`

**Routes to Implement**:
```python
@bp.route('/purchase-orders')
def list_purchase_orders():
    """List all purchase orders"""
    pass

@bp.route('/purchase-orders/<int:id>')
def view_purchase_order(id):
    """View purchase order details"""
    pass

@bp.route('/purchase-orders/create', methods=['GET', 'POST'])
def create_purchase_order():
    """Create new purchase order"""
    # GET: Show form with unfulfilled demands
    # POST: Create PO using PurchaseOrderManager
    pass

@bp.route('/purchase-orders/<int:id>/submit', methods=['POST'])
def submit_purchase_order(id):
    """Submit PO for ordering"""
    pass

@bp.route('/purchase-orders/<int:id>/cancel', methods=['POST'])
def cancel_purchase_order(id):
    """Cancel PO"""
    pass
```

### E.2 - Receiving Routes ✅ TODO

**File**: `app/routes/purchasing/receiving.py`

**Routes to Implement**:
```python
@bp.route('/receiving/packages')
def list_packages():
    """List all packages"""
    pass

@bp.route('/receiving/packages/create', methods=['GET', 'POST'])
def create_package():
    """Create new receiving package"""
    pass

@bp.route('/receiving/packages/<int:id>')
def view_package(id):
    """View package details"""
    pass

@bp.route('/receiving/packages/<int:id>/receive', methods=['POST'])
def receive_parts(id):
    """Receive parts into package"""
    # Uses PartArrivalManager
    pass

@bp.route('/receiving/arrivals/<int:id>/inspect', methods=['POST'])
def inspect_arrival(id):
    """Inspect and accept/reject parts"""
    pass
```

### E.3 - Inventory Routes ✅ TODO

**File**: `app/routes/purchasing/inventory.py`

**Routes to Implement**:
```python
@bp.route('/inventory')
def list_inventory():
    """List all inventory by location"""
    pass

@bp.route('/inventory/movements')
def list_movements():
    """List inventory movements"""
    pass

@bp.route('/inventory/adjust', methods=['GET', 'POST'])
def adjust_inventory():
    """Manual inventory adjustment"""
    pass

@bp.route('/inventory/transfer', methods=['GET', 'POST'])
def transfer_inventory():
    """Transfer between locations"""
    pass

@bp.route('/inventory/issue', methods=['POST'])
def issue_to_demand():
    """Issue parts to maintenance demand"""
    pass
```

### E.4 - Templates ✅ TODO

**Templates to Create**:
```
app/templates/purchasing/
├── purchase_orders/
│   ├── list.html
│   ├── view.html
│   ├── create.html
│   └── components/
│       ├── po_line_table.html
│       └── demand_selector.html
├── receiving/
│   ├── packages_list.html
│   ├── package_view.html
│   ├── receive_form.html
│   └── inspect_form.html
└── inventory/
    ├── list.html
    ├── movements.html
    ├── adjust_form.html
    └── transfer_form.html
```

### E.5 - Dashboard Integration ✅ TODO

**Update Main Dashboard**:
```html
<!-- Add to dashboard.html -->
<div class="row">
    <div class="col-md-3">
        <div class="card">
            <div class="card-body">
                <h5>Open Purchase Orders</h5>
                <h2>{{ open_po_count }}</h2>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card">
            <div class="card-body">
                <h5>Pending Inspections</h5>
                <h2>{{ pending_inspections }}</h2>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card">
            <div class="card-body">
                <h5>Low Stock Items</h5>
                <h2>{{ low_stock_count }}</h2>
            </div>
        </div>
    </div>
</div>
```

---

## Testing Strategy

### Unit Tests
```
tests/phase_6/
├── test_purchase_order_models.py
├── test_receiving_models.py
├── test_inventory_models.py
├── test_purchase_order_manager.py
├── test_part_arrival_manager.py
├── test_inventory_manager.py
└── test_part_demand_manager.py
```

### Integration Tests
```
tests/phase_6/
├── test_po_to_receiving_integration.py
├── test_receiving_to_inventory_integration.py
├── test_maintenance_to_purchasing_integration.py
└── test_complete_workflows.py
```

### Test Data Setup
```python
# tests/phase_6/conftest.py
@pytest.fixture
def sample_part_demand():
    """Create sample part demand"""
    pass

@pytest.fixture
def sample_purchase_order():
    """Create sample PO"""
    pass

@pytest.fixture
def sample_inventory():
    """Create sample inventory"""
    pass
```

---

## Success Criteria Checklist

### Phase 6A: Purchase Orders
- [ ] PurchaseOrderHeader model created and tested
- [ ] PurchaseOrderLine model created and tested
- [ ] Association table created and tested
- [ ] PurchaseOrderManager implemented
- [ ] Can create PO from part demands
- [ ] Can submit and cancel POs
- [ ] Events created for PO actions
- [ ] Build system updated

### Phase 6B: Receiving
- [ ] PackageHeader model created and tested
- [ ] PartArrival model created and tested
- [ ] PartArrivalManager implemented
- [ ] Can receive parts against PO
- [ ] Can inspect and accept/reject
- [ ] PO line quantities update correctly
- [ ] Partial fulfillment works
- [ ] Events created for arrivals

### Phase 6C: Inventory
- [ ] ActiveInventory model created and tested
- [ ] InventoryMovement model created and tested
- [ ] InventoryManager implemented
- [ ] Arrivals create inventory movements
- [ ] Issues create inventory movements
- [ ] Adjustments work correctly
- [ ] Transfers work correctly
- [ ] Stock levels accurate
- [ ] Location tracking works

### Phase 6D: Integration
- [ ] PartDemand relationships added
- [ ] PartDemandManager implemented
- [ ] Can check inventory before ordering
- [ ] Complete traceability chain works
- [ ] End-to-end workflows tested
- [ ] Integration with Phase 5 seamless

### Phase 6E: UI
- [ ] All routes implemented
- [ ] All templates created
- [ ] Dashboard updated
- [ ] User can create POs from UI
- [ ] User can receive parts from UI
- [ ] User can manage inventory from UI
- [ ] HTMX interactions work

---

## Implementation Timeline Estimate

### Phase 6A: Purchase Orders
- **Time**: 5-7 days
- **Complexity**: Medium
- **Blockers**: None

### Phase 6B: Receiving
- **Time**: 5-7 days
- **Complexity**: Medium
- **Blockers**: Requires Phase 6A

### Phase 6C: Inventory
- **Time**: 7-10 days
- **Complexity**: High (complex logic in manager)
- **Blockers**: Requires Phase 6B

### Phase 6D: Integration
- **Time**: 5-7 days
- **Complexity**: Medium-High
- **Blockers**: Requires Phase 6C

### Phase 6E: UI
- **Time**: 7-10 days
- **Complexity**: Medium
- **Blockers**: Requires Phase 6D

**Total Estimated Time**: 29-41 days (approximately 6-8 weeks)

---

## Key Design Decisions

### 1. Manager Pattern
**Decision**: Use manager classes for all business logic
**Rationale**: 
- Keeps models simple and focused on data
- Centralizes complex logic
- Easier to test and maintain
- Follows existing Phase 5 patterns

### 2. Inventory by Location
**Decision**: Track inventory separately by location from day one
**Rationale**:
- Supports multi-location from start
- Prevents future migration pain
- Aligns with MajorLocation concept

### 3. Separate Arrival and Inventory
**Decision**: PartArrival is separate from InventoryMovement
**Rationale**:
- Clear separation of receiving vs inventory
- Supports rejection without inventory impact
- Better audit trail

### 4. Association Table for Demands
**Decision**: Use junction table instead of direct FK
**Rationale**:
- Multiple demands can link to one PO line
- One demand might be split across multiple lines
- More flexible for future needs

### 5. Movement Types over Subclasses
**Decision**: Single InventoryMovement table with type field
**Rationale**:
- Simpler queries
- Easier to add new types
- Better for reporting

---

## Common Pitfalls to Avoid

### 1. **Don't put business logic in models**
❌ Bad:
```python
class PurchaseOrderHeader(UserCreatedBase):
    def create_from_demands(self, demands):
        # Complex logic in model
```

✅ Good:
```python
class PurchaseOrderManager:
    @staticmethod
    def create_from_demands(demands):
        # Logic in manager
```

### 2. **Don't forget to update PO line quantities**
When accepting arrivals, must update PO line received quantity

### 3. **Don't create inventory movements directly**
Always use InventoryManager to ensure ActiveInventory is updated

### 4. **Don't forget event creation**
Major actions should create events for audit trail

### 5. **Don't forget user_id tracking**
All operations need user_id for audit trail

---

## Quick Reference Commands

### Build Database
```python
# Update app.py to include Phase 6
python app.py
```

### Run Tests
```bash
pytest tests/phase_6/ -v
```

### Clear and Rebuild
```bash
python z_clear_data.py
python app.py
```

### View Database
```bash
python z_view_database.py
```

---

## Next Steps After Phase 6

### Phase 7: Planning and Forecasting
- Maintenance planning
- Part demand forecasting
- Budget management
- Preventive maintenance scheduling

### Phase 8: Vendor Management
- Vendor database
- Vendor ratings and contracts
- RFQ process
- Vendor performance tracking

### Phase 9: Advanced Inventory
- Lot and serial number tracking
- Expiration dates
- Cycle counting
- FIFO/LIFO costing
- Min/max auto-reordering

---

## Summary

Phase 6 brings complete inventory and purchasing capabilities to the asset management system. By following this implementation plan:

1. **Start with simple CRUD models** in Phase 6A
2. **Add receiving workflow** in Phase 6B
3. **Implement inventory tracking** in Phase 6C
4. **Connect everything** in Phase 6D
5. **Build the UI** in Phase 6E

The manager pattern keeps complexity manageable and maintains clean separation between data and logic. This approach has worked well in Phase 5 (Maintenance) and will continue to serve us well in Phase 6.

**Key Principle**: Models define the database, Managers define the business logic.


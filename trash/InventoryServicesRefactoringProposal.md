# Inventory Services Refactoring Proposal

## Overview
This document outlines the proposed refactoring of inventory-related business logic into the `services/inventory` layer, following the same pattern established for `services/core`, `services/assets`, and `services/maintenance`.

## Goals
1. Move read-only, presentation-specific query logic from `business/inventory` to `services/inventory`
2. Prepare services for future inventory presentation routes
3. Create reusable service methods for inventory data retrieval
4. Maintain separation between business logic (managers) and presentation logic (services)

## Current Structure

### Business Layer (`app/buisness/inventory/`)
- **Managers**: Handle complex business operations with data modification
  - `InventoryManager` - Inventory movements, allocations, transfers
  - `PartDemandManager` - Part demand fulfillment, PO integration
  - `PartArrivalManager` - Part arrival processing
  - `PurchaseOrderManager` - Purchase order operations
- **Contexts**: Provide property accessors and business domain access
  - `PartContext` - Part-related data access
  - `ToolContext` - Tool-related data access

## Proposed Service Structure

```
app/services/inventory/
├── __init__.py
├── inventory_service.py          # Inventory queries and availability checks
├── active_inventory_service.py   # Active inventory list/filter/queries
├── inventory_movement_service.py # Movement history queries
├── part_service.py               # Part-related queries (stock status, demands)
├── tool_service.py               # Tool-related queries
└── part_demand_service.py        # Part demand queries (availability, fulfillment status)
```

---

## 1. Inventory Service (`inventory_service.py`)

### Logic to Move from `business/inventory/managers/inventory_manager.py`:

**Methods to Move:**
- `check_availability(part_id, location_id, quantity)` - Read-only availability check
- `get_inventory_by_location(location_id)` - Read-only query for location inventory
- `get_inventory_by_part(part_id)` - Read-only query for part inventory across locations
- `get_movement_history(part_id, location_id)` - Read-only movement history query

**Proposed Methods:**
```python
class InventoryService:
    @staticmethod
    def check_availability(part_id: int, location_id: int, quantity: float) -> Dict[str, Any]:
        """Check if parts are available at location (read-only)"""
        
    @staticmethod
    def get_inventory_by_location(location_id: int) -> List[ActiveInventory]:
        """Get all inventory at a location (read-only)"""
        
    @staticmethod
    def get_inventory_by_part(part_id: int) -> List[ActiveInventory]:
        """Get inventory for a part across all locations (read-only)"""
        
    @staticmethod
    def get_movement_history(
        part_id: Optional[int] = None,
        location_id: Optional[int] = None,
        limit: Optional[int] = None
    ) -> List[InventoryMovement]:
        """Get inventory movement history with optional filters (read-only)"""
        
    @staticmethod
    def get_stock_summary(part_id: int) -> Dict[str, Any]:
        """Get stock summary for a part across all locations"""
        # Returns: total_on_hand, total_allocated, total_available, by_location
```

**Keep in Business Layer:**
- `record_arrival()` - Creates inventory movements (data modification)
- `issue_to_demand()` - Issues parts (data modification)
- `return_from_demand()` - Returns parts (data modification)
- `adjust_inventory()` - Adjusts inventory (data modification)
- `transfer_inventory()` - Transfers inventory (data modification)
- `allocate_to_demand()` - Allocates inventory (data modification)
- `get_traceability_chain()` - Complex business logic with data access

---

## 2. Active Inventory Service (`active_inventory_service.py`)

### Purpose:
Centralize queries for `ActiveInventory` model - the current stock levels view.

**Proposed Methods:**
```python
class ActiveInventoryService:
    @staticmethod
    def get_list_data(
        page: int = 1,
        per_page: int = 20,
        part_id: Optional[int] = None,
        location_id: Optional[int] = None,
        low_stock_only: bool = False,
        out_of_stock_only: bool = False
    ) -> Tuple[Pagination, Dict[str, Any]]:
        """Get paginated active inventory with filters"""
        # Returns: (pagination_object, form_options_dict)
        
    @staticmethod
    def get_by_part_and_location(part_id: int, location_id: int) -> Optional[ActiveInventory]:
        """Get active inventory for specific part and location"""
        
    @staticmethod
    def get_low_stock_items(threshold: Optional[float] = None) -> List[ActiveInventory]:
        """Get items that are low on stock"""
        
    @staticmethod
    def get_out_of_stock_items() -> List[ActiveInventory]:
        """Get items that are out of stock"""
        
    @staticmethod
    def get_stock_levels_by_location(location_id: int) -> Dict[int, Dict[str, float]]:
        """Get stock levels for all parts at a location"""
        # Returns: {part_id: {'on_hand': ..., 'allocated': ..., 'available': ...}}
```

---

## 3. Inventory Movement Service (`inventory_movement_service.py`)

### Purpose:
Handle read-only queries for inventory movement history and traceability.

**Proposed Methods:**
```python
class InventoryMovementService:
    @staticmethod
    def get_list_data(
        page: int = 1,
        per_page: int = 20,
        part_id: Optional[int] = None,
        location_id: Optional[int] = None,
        movement_type: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Tuple[Pagination, Dict[str, Any]]:
        """Get paginated inventory movements with filters"""
        # Returns: (pagination_object, form_options_dict)
        
    @staticmethod
    def get_movement_history(
        part_id: Optional[int] = None,
        location_id: Optional[int] = None,
        limit: Optional[int] = None
    ) -> List[InventoryMovement]:
        """Get movement history for part/location"""
        
    @staticmethod
    def get_traceability_chain(initial_arrival_id: int) -> List[InventoryMovement]:
        """Get full traceability chain for an arrival (read-only view)"""
        # This is different from InventoryManager.get_traceability_chain() which may modify
        
    @staticmethod
    def get_movements_by_demand(part_demand_id: int) -> List[InventoryMovement]:
        """Get all movements associated with a part demand"""
```

**Note:** Complex traceability operations that modify data stay in `InventoryManager`.

---

## 4. Part Service (`part_service.py`)

### Logic to Move from `business/inventory/part_context.py`:

**Methods to Move:**
- `part_demands` property - Read-only query (move to service method)
- `get_recent_demands(limit)` - Read-only query for recent demands

**Proposed Methods:**
```python
class PartService:
    @staticmethod
    def get_part_demands(part_id: int) -> List[PartDemand]:
        """Get all part demands for a part (read-only)"""
        
    @staticmethod
    def get_recent_demands(part_id: int, limit: int = 10) -> List[PartDemand]:
        """Get recent part demands for a part (read-only)"""
        
    @staticmethod
    def get_stock_status(part_id: int) -> Dict[str, Any]:
        """Get stock status for a part"""
        # Returns: is_low_stock, is_out_of_stock, stock_status, current_stock_level
        
    @staticmethod
    def get_stock_summary(part_id: int) -> Dict[str, Any]:
        """Get comprehensive stock summary for a part"""
        # Combines inventory data with part info
        
    @staticmethod
    def get_demand_count(part_id: int) -> int:
        """Get count of part demands for a part"""
```

**Keep in Business Layer:**
- `PartContext.part` - Property accessor (business domain)
- `PartContext.part_id` - Property accessor
- `PartContext.is_low_stock` - Computed property (business logic)
- `PartContext.is_out_of_stock` - Computed property (business logic)
- `PartContext.stock_status` - Computed property (business logic)
- `PartContext.demand_count` - Computed property (business logic)

---

## 5. Tool Service (`tool_service.py`)

### Purpose:
Handle read-only queries for tools and issuable tools.

**Proposed Methods:**
```python
class ToolService:
    @staticmethod
    def get_list_data(
        page: int = 1,
        per_page: int = 20,
        tool_name: Optional[str] = None,
        is_issuable: Optional[bool] = None,
        assigned_to_user_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> Tuple[Pagination, Dict[str, Any]]:
        """Get paginated tools with filters"""
        # Returns: (pagination_object, form_options_dict)
        
    @staticmethod
    def get_issuable_tools(assigned_to_user_id: Optional[int] = None) -> List[Tool]:
        """Get issuable tools, optionally filtered by assignment"""
        
    @staticmethod
    def get_tool_assignment_info(tool_id: int) -> Dict[str, Any]:
        """Get assignment information for a tool"""
        # Returns: is_issuable, assigned_to, status, location, etc.
        
    @staticmethod
    def get_tools_needing_calibration(days_ahead: int = 30) -> List[Tool]:
        """Get tools that need calibration within specified days"""
```

**Keep in Business Layer:**
- `ToolContext.tool` - Property accessor (business domain)
- `ToolContext.tool_id` - Property accessor
- `ToolContext.issuable_tool` - Property accessor
- `ToolContext.is_issuable` - Computed property (business logic)
- `ToolContext.assigned_to` - Property accessor (business domain)
- `ToolContext.status` - Property accessor (business domain)
- `ToolContext.serial_number` - Property accessor (business domain)
- `ToolContext.location` - Property accessor (business domain)
- `ToolContext.next_calibration_date` - Property accessor (business domain)
- `ToolContext.last_calibration_date` - Property accessor (business domain)

---

## 6. Part Demand Service (`part_demand_service.py`)

### Logic to Move from `business/inventory/managers/part_demand_manager.py`:

**Methods to Move:**
- `check_inventory_availability(demand_id)` - Read-only availability check
- `get_demands_by_purchase_order(po_id)` - Read-only query for PO demands
- `get_demand_fulfillment_status(demand_id)` - Read-only fulfillment status
- `get_unfulfilled_demands()` - Read-only query for unfulfilled demands

**Proposed Methods:**
```python
class PartDemandInventoryService:
    @staticmethod
    def check_inventory_availability(demand_id: int) -> Dict[str, Any]:
        """Check if demand can be fulfilled from inventory (read-only)"""
        # Returns detailed availability info
        
    @staticmethod
    def get_demands_by_purchase_order(po_id: int) -> List[PartDemand]:
        """Get all demands linked to a purchase order (read-only)"""
        
    @staticmethod
    def get_demand_fulfillment_status(demand_id: int) -> Dict[str, Any]:
        """Get detailed fulfillment status for a demand (read-only)"""
        
    @staticmethod
    def get_unfulfilled_demands(
        part_id: Optional[int] = None,
        location_id: Optional[int] = None,
        asset_type_id: Optional[int] = None
    ) -> List[PartDemand]:
        """Get unfulfilled part demands with optional filters (read-only)"""
        
    @staticmethod
    def get_demands_needing_purchase() -> List[PartDemand]:
        """Get demands that need purchase orders (read-only)"""
```

**Keep in Business Layer:**
- `create_purchase_order_from_demands()` - Creates PO (data modification)
- `link_demand_to_po()` - Links demand to PO (data modification)
- `mark_demand_fulfilled()` - Marks demand fulfilled (data modification)
- `allocate_from_inventory()` - Allocates inventory (data modification)

---

## Business Layer Methods Review

### Methods to Keep in Business Layer:

#### InventoryManager:
- All methods that modify data (record_arrival, issue_to_demand, return_from_demand, adjust_inventory, transfer_inventory, allocate_to_demand)
- Complex business logic operations

#### PartDemandManager:
- All methods that modify data or create business entities
- Methods that create purchase orders or link demands

#### PartArrivalManager:
- All methods that process arrivals and modify data

#### PurchaseOrderManager:
- All methods that create or modify purchase orders

#### Contexts:
- All property accessors (provide business domain access)
- Computed properties (business logic calculations)

### Methods to Move to Services:

#### InventoryManager:
- `check_availability()` - Read-only query
- `get_inventory_by_location()` - Read-only query
- `get_inventory_by_part()` - Read-only query
- `get_movement_history()` - Read-only query

#### PartDemandManager:
- `check_inventory_availability()` - Read-only availability check
- `get_demands_by_purchase_order()` - Read-only query
- `get_demand_fulfillment_status()` - Read-only status check
- `get_unfulfilled_demands()` - Read-only query (if exists)

#### PartContext:
- `part_demands` property logic - Move to `PartService.get_part_demands()`
- `get_recent_demands()` - Move to `PartService.get_recent_demands()`

---

## Implementation Plan

### Phase 1: Create Service Structure
1. Create `app/services/inventory/` directory
2. Create `__init__.py` with service exports
3. Create all service class files with empty classes

### Phase 2: Implement Core Inventory Services
1. Implement `InventoryService` with availability and query methods
2. Implement `ActiveInventoryService` with list/filter methods
3. Implement `InventoryMovementService` with history queries

### Phase 3: Implement Part and Tool Services
1. Implement `PartService` with part-related queries
2. Implement `ToolService` with tool-related queries
3. Move methods from `PartContext` to `PartService`

### Phase 4: Implement Part Demand Service
1. Implement `PartDemandInventoryService` with availability and status methods
2. Move read-only methods from `PartDemandManager`

### Phase 5: Update Business Layer
1. Update `PartContext` to delegate queries to `PartService` (maintain backward compatibility)
2. Document deprecation for moved methods

### Phase 6: Testing and Verification
1. Test all services independently
2. Verify backward compatibility
3. Check for any circular import issues

---

## Benefits

1. **Separation of Concerns**: Clear separation between business logic (managers) and presentation logic (services)
2. **Reusability**: Services can be used by multiple routes or API endpoints
3. **Testability**: Services can be unit tested independently
4. **Consistency**: Follows the same pattern as core, assets, and maintenance modules
5. **Future-Proof**: Ready for inventory presentation routes when needed
6. **Maintainability**: Query logic centralized and easy to modify

---

## Notes

- All services should use `from flask_sqlalchemy.pagination import Pagination` for type hints
- Form options should be retrieved in service methods to avoid N+1 queries
- Eager loading should be applied in service methods where needed
- Filter logic should be in service methods, not routes
- Business layer managers remain for complex business operations and data modification
- Business layer contexts remain for property accessors and business domain access
- Services are read-only - no data modification methods
- For backward compatibility, context methods may delegate to services but should be deprecated

---

## Considerations

### Inventory vs Supply Routes
- Currently, there are `supply` routes but no `inventory` routes
- Supply routes may handle part/tool CRUD
- Inventory routes would handle inventory movements, stock levels, transfers
- Services created here can be used by both supply and future inventory routes

### Manager Classes
- Manager classes contain complex business logic with data modification
- They should remain in business layer
- Services will only handle read-only queries and data retrieval
- Managers may use services internally for read operations if needed




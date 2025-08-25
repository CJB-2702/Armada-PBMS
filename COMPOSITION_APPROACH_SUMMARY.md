# Composition Approach for Action-PartDemand Linking

## Overview

This document describes the implementation of a composition pattern to decouple the supply folder from the maintenance folder, specifically for linking maintenance actions to part demands.

## Problem Solved

Previously, the system used inheritance where `MaintenancePartDemand` extended `PartDemand`, creating tight coupling between the supply and maintenance modules. This approach had several issues:

1. **Tight Coupling**: Supply module was directly dependent on maintenance concepts
2. **Data Visibility Issues**: Queries on `PartDemand` could miss maintenance-specific data
3. **Schema Pollution**: Base `PartDemand` table contained maintenance-specific columns
4. **Circular Dependencies**: Maintenance imported from supply, but supply referenced maintenance

## Solution: Composition Pattern

### New Architecture

```
Supply Module (Independent)
├── PartDemand (unchanged)
├── Part
└── VirtualPartDemand

Maintenance Module (Independent)
├── Action
├── MaintenanceEventSet
└── PartDemandToActionReference (NEW - composition class)
```

### Key Components

#### 1. PartDemandToActionReference Class
- **Location**: `app/models/maintenance/base/part_demand_to_action_references.py`
- **Inheritance**: Extends `UserCreatedBase` for audit trail
- **Purpose**: Links maintenance actions to part demands using composition

```python
class PartDemandToActionReference(UserCreatedBase):
    __tablename__ = 'part_demand_to_action_references'
    
    action_id = db.Column(db.Integer, db.ForeignKey('actions.id'), nullable=False)
    part_demand_id = db.Column(db.Integer, db.ForeignKey('part_demands.id'), nullable=False)
    sequence_order = db.Column(db.Integer, nullable=True, default=1)
    notes = db.Column(db.Text, nullable=True)
```

#### 2. Updated Action Class
- **New Methods**:
  - `get_part_demands()`: Uses composition to retrieve linked part demands
  - `get_part_demands_by_sequence()`: Returns ordered part demands
  - `add_part_demand()`: Creates new reference
  - `remove_part_demand()`: Removes reference
  - `get_total_part_cost()`: Calculates total cost using composition

#### 3. Unchanged PartDemand Class
- **Status**: Remains completely unchanged
- **Independence**: No knowledge of maintenance concepts
- **Reusability**: Can be used by any module without modification

## Benefits Achieved

### 1. Complete Decoupling
- ✅ Supply folder has no dependencies on maintenance folder
- ✅ Maintenance folder has no dependencies on supply folder
- ✅ Each module can evolve independently

### 2. Data Integrity
- ✅ No data visibility issues - each query is explicit
- ✅ No risk of mismatches between related data
- ✅ Clear ownership boundaries

### 3. Flexibility
- ✅ Actions can link to any PartDemand without inheritance constraints
- ✅ Easy to add new part demand types in the future
- ✅ Support for sequence ordering and additional metadata

### 4. Audit Trail
- ✅ Full audit trail through UserCreatedBase inheritance
- ✅ Tracks who created/modified references and when

### 5. Performance
- ✅ Efficient queries using proper foreign key relationships
- ✅ No complex inheritance queries
- ✅ Clear indexing strategy

## Usage Examples

### Creating a Reference
```python
# Link a part demand to an action
reference = PartDemandToActionReference.create_reference(
    action_id=action.id,
    part_demand_id=part_demand.id,
    user_id=current_user.id,
    sequence_order=1,
    notes="Primary part for this action"
)
```

### Retrieving Part Demands for an Action
```python
# Get all part demands for an action
part_demands = action.get_part_demands()

# Get ordered part demands
ordered_demands = action.get_part_demands_by_sequence()

# Calculate total cost
total_cost = action.get_total_part_cost()
```

### Retrieving Actions for a Part Demand
```python
# Get all actions that use a specific part demand
actions = PartDemandToActionReference.get_actions_for_part_demand(part_demand.id)
```

### Removing References
```python
# Remove a part demand from an action
success = action.remove_part_demand(part_demand.id)
```

## Database Schema

### New Table: part_demand_to_action_references
```sql
CREATE TABLE part_demand_to_action_references (
    id INTEGER PRIMARY KEY,
    action_id INTEGER NOT NULL REFERENCES actions(id),
    part_demand_id INTEGER NOT NULL REFERENCES part_demands(id),
    sequence_order INTEGER DEFAULT 1,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by_id INTEGER REFERENCES users(id),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by_id INTEGER REFERENCES users(id)
);
```

### Removed Dependencies
- ❌ Removed `maintenance_event_set_id` from `part_demands` table
- ❌ Removed `action_id` from `part_demands` table
- ❌ Removed direct relationships between Action and PartDemand

## Migration Strategy

1. **Phase 1**: Create new `part_demand_to_action_references` table
2. **Phase 2**: Migrate existing action-part_demand relationships to new table
3. **Phase 3**: Remove maintenance-specific columns from `part_demands` table
4. **Phase 4**: Update application code to use composition pattern

## Testing

A test script `test_composition_approach.py` has been created to verify:
- Reference creation and retrieval
- Sequence ordering
- Cost calculations
- Reference removal
- Data integrity

## Future Extensibility

This composition pattern can easily be extended for:
- **Emergency Part Demands**: New reference table for emergency scenarios
- **Project Part Demands**: New reference table for project-based part demands
- **Multi-Action Part Demands**: Single part demand linked to multiple actions
- **Temporary Part Demands**: Time-limited references

## Conclusion

The composition approach successfully decouples the supply and maintenance modules while maintaining all functionality. It provides a clean, maintainable, and extensible solution that follows SOLID principles and eliminates the tight coupling issues of the previous inheritance-based approach.

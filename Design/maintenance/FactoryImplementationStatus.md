# Maintenance Factory Implementation Status

## Overview

This document reviews the existing factory classes and identifies what needs to be added or modified to support the Create & Assign Portal functionality.

## Existing Factory Classes

### 1. MaintenanceFactory ✅ **Fully Implemented**
**Location**: `app/buisness/maintenance/factories/maintenance_factory.py`

**Current Implementation**:
- ✅ `create_from_template()` - Creates complete maintenance event from template
- ✅ `create_from_maintenance_plan()` - Creates event from maintenance plan
- ✅ Coordinates all sub-factories
- ✅ Handles transaction management
- ✅ Validates business rules

**What It Does**:
- Creates MaintenanceActionSet (via MaintenanceActionSetFactory)
- Creates all Actions (via ActionFactory)
- Creates PartDemand records
- Creates ActionTool records

**Missing for Create & Assign Portal**:
- ❌ Does not accept `assigned_user_id` or `assigned_by_id` parameters
- ❌ Does not set assignment fields during creation
- ❌ Does not accept `priority` parameter (currently defaults to 'Medium')
- ❌ Does not accept `notes` parameter for assignment notes

### 2. MaintenanceActionSetFactory ✅ **Partially Implemented**
**Location**: `app/buisness/maintenance/factories/maintenance_action_set_factory.py`

**Current Implementation**:
- ✅ `create_from_template()` - Creates MaintenanceActionSet from TemplateActionSet
- ✅ Creates Event (ONE-TO-ONE relationship)
- ✅ Copies metadata from template
- ✅ Sets up relationships (asset, plan, template)
- ✅ Initializes status and planned_start_datetime

**What It Does**:
- Creates Event via `Event.add_event()`
- Creates MaintenanceActionSet with all metadata
- Sets status to 'Planned'
- Sets priority to 'Medium' (hardcoded)

**Missing for Create & Assign Portal**:
- ❌ Does not accept `assigned_user_id` parameter
- ❌ Does not accept `assigned_by_id` parameter
- ❌ Does not accept `priority` parameter (hardcoded to 'Medium')
- ❌ Does not set assignment fields during creation

### 3. ActionFactory ✅ **Fully Implemented**
**Location**: `app/buisness/maintenance/factories/action_factory.py`

**Current Implementation**:
- ✅ `create_from_template_action_item()` - Creates single Action from TemplateActionItem
- ✅ `create_from_template_action_set()` - Creates all Actions from TemplateActionSet
- ✅ Copies action details and sequence_order
- ✅ Creates PartDemand records (standalone copies)
- ✅ Creates ActionTool records (standalone copies)

**What It Does**:
- Creates Action records with all metadata
- Creates PartDemand records from TemplatePartDemand
- Creates ActionTool records from TemplateActionTool
- Maintains sequence_order from template

**Status**: ✅ **No changes needed** - ActionFactory is complete for Create & Assign Portal needs

## Required Changes

### 1. Update MaintenanceActionSetFactory

**File**: `app/buisness/maintenance/factories/maintenance_action_set_factory.py`

**Changes Needed**:
```python
@classmethod
def create_from_template(
    cls,
    template_action_set_id: int,
    asset_id: int,
    planned_start_datetime: Optional[datetime] = None,
    maintenance_plan_id: Optional[int] = None,
    user_id: Optional[int] = None,
    assigned_user_id: Optional[int] = None,  # NEW
    assigned_by_id: Optional[int] = None,      # NEW
    priority: str = 'Medium',                  # NEW (currently hardcoded)
    commit: bool = True
) -> MaintenanceActionSet:
```

**Implementation**:
- Add `assigned_user_id` parameter and set it on MaintenanceActionSet
- Add `assigned_by_id` parameter and set it on MaintenanceActionSet
- Add `priority` parameter and use it instead of hardcoded 'Medium'
- Update MaintenanceActionSet creation to include these fields

### 2. Update MaintenanceFactory

**File**: `app/buisness/maintenance/factories/maintenance_factory.py`

**Changes Needed**:
```python
@classmethod
def create_from_template(
    cls,
    template_action_set_id: int,
    asset_id: int,
    planned_start_datetime: Optional[datetime] = None,
    maintenance_plan_id: Optional[int] = None,
    user_id: Optional[int] = None,
    assigned_user_id: Optional[int] = None,  # NEW
    assigned_by_id: Optional[int] = None,      # NEW
    priority: str = 'Medium',                  # NEW
    notes: Optional[str] = None,                # NEW (for assignment notes)
    commit: bool = True
) -> MaintenanceActionSet:
```

**Implementation**:
- Add `assigned_user_id` parameter and pass to MaintenanceActionSetFactory
- Add `assigned_by_id` parameter and pass to MaintenanceActionSetFactory
- Add `priority` parameter and pass to MaintenanceActionSetFactory
- Add `notes` parameter (for future use - assignment notes could be added as Event comment)
- After creation, optionally add comment to Event if notes provided

### 3. Update create_from_maintenance_plan (if needed)

**File**: `app/buisness/maintenance/factories/maintenance_factory.py`

**Changes Needed**:
- May need to add assignment parameters to `create_from_maintenance_plan()` as well
- Pass through to `create_from_template()`

## Data Model Support

### MaintenanceActionSet Model ✅ **Ready**
**Location**: `app/data/maintenance/base/maintenance_action_sets.py`

**Fields Available**:
- ✅ `assigned_user_id` (line 34) - ForeignKey to users.id, nullable=True
- ✅ `assigned_by_id` (line 35) - ForeignKey to users.id, nullable=True
- ✅ `priority` (line 28) - String(20), default='Medium'
- ✅ Relationships defined (lines 50-51)

**Status**: ✅ **No changes needed** - Model already supports assignment

## Summary

### ✅ Already Implemented
1. **MaintenanceFactory** - Core creation logic complete
2. **MaintenanceActionSetFactory** - Core creation logic complete
3. **ActionFactory** - Complete, no changes needed
4. **Data Model** - Assignment fields exist in MaintenanceActionSet

### ❌ Needs Implementation
1. **MaintenanceActionSetFactory.create_from_template()** - Add assignment parameters
2. **MaintenanceFactory.create_from_template()** - Add assignment parameters and pass through
3. **Optional**: Add comment creation for assignment notes in MaintenanceFactory

### Implementation Priority
1. **High**: Add `assigned_user_id` and `assigned_by_id` to factories (required for assignment during creation)
2. **Medium**: Add `priority` parameter to factories (currently hardcoded)
3. **Low**: Add `notes` parameter for assignment notes (can be added later via MaintenanceContext)

## Testing Considerations

After implementing changes, test:
- Creating event with assignment
- Creating event without assignment (should still work)
- Creating event with priority other than 'Medium'
- Verifying assigned_user_id and assigned_by_id are set correctly
- Verifying priority is set correctly
- Verifying existing functionality still works (backward compatibility)


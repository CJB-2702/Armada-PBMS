# Maintenance Event Edit Screen Integration Plan

## Document Purpose
This document outlines the integration plan for the `edit_maintenance_event_mockup.html` mockup into the application. It identifies all form field submissions, required endpoints, transformations needed, and additional functionality considerations.

**Date Created**: 2024-01-15  
**Status**: Planning Phase - No Code Edits  
**Mockup File**: `edit_maintenance_event_mockup.html`

---

## Table of Contents
1. [Form Field Analysis](#form-field-analysis)
2. [Current Routes and Endpoints](#current-routes-and-endpoints)
3. [Required New Routes](#required-new-routes)
4. [Field Transformation Requirements](#field-transformation-requirements)
5. [Additional Functionality Opportunities](#additional-functionality-opportunities)
6. [Maintenance Context Enhancements](#maintenance-context-enhancements)
7. [Implementation Phases](#implementation-phases)
8. [Data Model Considerations](#data-model-considerations)

---

## 1. Form Field Analysis

### 1.1 Maintenance Event Details Form

**Location**: Lines 98-228 in mockup  
**Endpoint**: `POST /maintenance/maintenance-event/<event_id>/edit`
update endpoint to POST /maintenance/maintenance-event/<event_id>/maintenance-action-set/edit

#### Form Fields:

| Field Name | HTML Input Type | Data Type | Required | Current Status | Notes |
|------------|----------------|-----------|----------|----------------|-------|
| `task_name` | text | String | Yes | ✅ Exists | Updates `MaintenanceActionSet.task_name` |
| `estimated_duration` | number (step=0.1) | Float | No | ✅ Exists | Updates `MaintenanceActionSet.estimated_duration` |
| `description` | textarea | Text | No | ✅ Exists | Updates `MaintenanceActionSet.description` |
| `asset_id` | select | Integer (FK) | No | ✅ Exists | Updates `MaintenanceActionSet.asset_id` |
| `maintenance_plan_id` | select | Integer (FK) | No | ✅ Exists | Updates `MaintenanceActionSet.maintenance_plan_id` |
| `status` | select | String | No | ✅ Exists | Updates `MaintenanceActionSet.status`, syncs `Event.status` |
| `priority` | select | String | No | ✅ Exists | Updates `MaintenanceActionSet.priority` |
| `planned_start_datetime` | datetime-local | DateTime | No | ✅ Exists | Updates `MaintenanceActionSet.planned_start_datetime` |
| `safety_review_required` | checkbox | Boolean | No | ✅ Exists | Updates `MaintenanceActionSet.safety_review_required` |
| `staff_count` | number | Integer | No | ✅ Exists | Updates `MaintenanceActionSet.staff_count` |
| `labor_hours` | number (step=0.1) | Float | No | ✅ Exists | Updates `MaintenanceActionSet.labor_hours` |
| `completion_notes` | textarea | Text | No | ✅ Exists | Updates `MaintenanceActionSet.completion_notes` |

**Status**: ✅ **FULLY IMPLEMENTED** - All fields are handled in current `edit_maintenance_event()` route

---

### 1.2 Event Activity - Comments Form

**Location**: Lines 286-309 in mockup  
**Endpoint**: `POST /events/<event_id>/comments` (✅ **EXISTS**)

**Blueprint**: `comments.create`  
**File**: `app/presentation/routes/core/events/comments.py`

#### Form Fields:

| Field Name | HTML Input Type | Data Type | Required | Current Status | Notes |
|------------|----------------|-----------|----------|----------------|-------|
| `content` | textarea | Text | Yes | ✅ Complete | Uses `EventContext.add_comment()` |
| `attachments` | file (multiple) | File[] | No | ✅ Complete | Handled via `EventContext.add_comment_with_attachments()` |
| `is_private` | checkbox | Boolean | No | ✅ Complete | Parameter exists and working |

**Status**: ✅ **FULLY IMPLEMENTED** - Endpoint already exists with full functionality

**Existing Implementation**:
- Endpoint: `POST /events/<event_id>/comments` 
- Handles file attachments via `request.files.getlist('attachments')`
- Supports private comments via `is_private` checkbox
- Uses `EventContext.add_comment()` or `EventContext.add_comment_with_attachments()`
- Supports HTMX for partial page updates
- Returns event widget on HTMX requests

**Action Required**:
- ✅ **NONE** - Endpoint already exists and is working
- Use `url_for('comments.create', event_id=event.id)` in edit page template
- Form should use `enctype="multipart/form-data"` for file uploads

---

### 1.3 Delay Edit Form (Active Delay)

**Location**: Lines 488-539 in mockup  
**Endpoint**: `POST /maintenance/maintenance-event/<event_id>/delay/<delay_id>/update` (NEW)

#### Form Fields:

| Field Name | HTML Input Type | Data Type | Required | Current Status | Notes |
|------------|----------------|-----------|----------|----------------|-------|
| `delay_id` | hidden | Integer | Yes | ✅ Exists | Part of URL |
| `delay_type` | select | String | Yes | ✅ Exists | Options: "Work in Delay", "Cancellation Requested" |
| `priority` | select | String | No | ✅ Exists | Low, Medium, High, Critical |
| `delay_reason` | textarea | Text | Yes | ✅ Exists | Required field |
| `delay_start_date` | datetime-local | DateTime | No | ❌ Missing | Needs update capability |
| `delay_end_date` | datetime-local | DateTime | No | ⚠️ Partial | End delay sets to now, but manual setting missing |
| `expected_resolution_date` | datetime-local | DateTime | No | ❌ Missing | **Field does not exist in MaintenanceDelay model** - requires database migration to add |
| `delay_billable_hours` | number (step=0.1) | Float | No | ✅ Exists | Updates `MaintenanceDelay.delay_billable_hours` |
| `delay_notes` | textarea | Text | No | ✅ Exists | Updates `MaintenanceDelay.delay_notes` |

**Status**: ⚠️ **PARTIALLY IMPLEMENTED** - Delay creation exists, but update/edit functionality is missing

**Action Required**:
- Create delay update endpoint
- Verify if `expected_resolution_date` field exists in `MaintenanceDelay` model
- Add ability to manually set `delay_start_date` and `delay_end_date`
- Remember always use the datamodel as the source of truth do not make any edits to data layer, change presentation and buisness layers if needed

---

### 1.4 Delay Edit Form (Historical Delay)

**Location**: Lines 573-625 in mockup  
**Endpoint**: Same as above - `POST /maintenance/maintenance-event/<event_id>/delay/<delay_id>/update`

**Note**: Historical delays can also be edited. Same fields as active delay.
Generate comment with new delay information on edit

---

### 1.5 Action Edit Form (Action Editor Panel - Middle Panel)

**Location**: Lines 831-916 in mockup  
**Endpoint**: `POST /maintenance/maintenance-event/<event_id>/action/<action_id>/update` (EXISTS)

#### Form Fields:

| Field Name | HTML Input Type | Data Type | Required | Current Status | Notes |
|------------|----------------|-----------|----------|----------------|-------|
| `action_name` | text | String | Yes | ✅ Exists | Updates `Action.action_name` |
| `description` | textarea | Text | No | ✅ Exists | Updates `Action.description` |
| `status` | select | String | No | ✅ Exists | Updates `Action.status` |
| `sequence_order` | number | Integer | No | ✅ Exists | Updates `Action.sequence_order` |
| `estimated_duration` | number (step=0.1) | Float | No | ✅ Exists | Updates `Action.estimated_duration` |
| `expected_billable_hours` | number (step=0.1) | Float | No | ✅ Exists | Updates `Action.expected_billable_hours` |
| `scheduled_start_time` | datetime-local | DateTime | No | ✅ Exists | Updates `Action.scheduled_start_time` |
| `start_time` | datetime-local | DateTime | No | ✅ Exists | Updates `Action.start_time` |
| `end_time` | datetime-local | DateTime | No | ✅ Exists | Updates `Action.end_time` |
| `billable_hours` | number (step=0.1) | Float | No | ✅ Exists | Updates `Action.billable_hours` |
| `safety_notes` | textarea | Text | No | ✅ Exists | Updates `Action.safety_notes` |
| `completion_notes` | textarea | Text | No | ✅ Exists | Updates `Action.completion_notes` |
| `notes` | textarea | Text | No | ✅ Exists | Updates `Action.notes` |

**Status**: ✅ **FULLY IMPLEMENTED** - All fields are handled in current `edit_action()` route

**Additional Operations**:
- Delete Action button (line 909) - Needs dedicated endpoint: `POST /maintenance/maintenance-event/<event_id>/action/<action_id>/delete` (NEW)

---

### 1.6 Part Demand Edit Form (First Part Demand)

**Location**: Lines 958-1003 in mockup  
**Endpoint**: `POST /maintenance/maintenance-event/<event_id>/part-demand/<part_demand_id>/update` (NEW)

#### Form Fields:

| Field Name | HTML Input Type | Data Type | Required | Current Status | Notes |
|------------|----------------|-----------|----------|----------------|-------|
| `part_demand_id` | URL parameter | Integer | Yes | ✅ Exists | Part of URL |
| `part_id` | number | Integer (FK) | Yes | ✅ Exists | Updates `PartDemand.part_id` |
| `quantity_required` | number (step=0.1) | Float | Yes | ✅ Exists | Updates `PartDemand.quantity_required` |
| `status` | select | String | Yes | ✅ Exists | Updates `PartDemand.status` |
| `priority` | select | String | No | ✅ Exists | Updates `PartDemand.priority` |
| `notes` | textarea | Text | No | ✅ Exists | Updates `PartDemand.notes` |

**Status**: ❌ **NOT IMPLEMENTED** - Part demand creation exists, but update/edit functionality is missing

**Action Required**:
- Create part demand update endpoint
- Validate part demand can be edited (check status restrictions)
- Ensure status transitions are valid
- in the UI disable changing the part ID users can cancel the demand but if they want to add a new part they need to add an additional demand request so that things don't accidentally get ordered. 

---

### 1.7 Part Demand Edit Form (Second Part Demand)

**Location**: Lines 1030-1075 in mockup  
**Endpoint**: Same as above

**Note**: Same fields as first part demand.

---

### 1.8 Add Part Demand Form

**Location**: Lines 1086-1103 in mockup  
**Endpoint**: `POST /maintenance/maintenance-event/<event_id>/action/<action_id>/part-demand/create` (EXISTS)

#### Form Fields:

| Field Name | HTML Input Type | Data Type | Required | Current Status | Notes |
|------------|----------------|-----------|----------|----------------|-------|
| `action_id` | URL parameter | Integer | Yes | ✅ Exists | Part of URL |
| `part_id` | number | Integer (FK) | Yes | ✅ Exists | Creates `PartDemand.part_id` |
| `quantity_required` | number (step=0.1) | Float | Yes | ✅ Exists | Creates `PartDemand.quantity_required` |

**Status**: ✅ **FULLY IMPLEMENTED** - Part demand creation exists in route `create_part_demand()`

---

### 1.9 Tool Edit Form (First Tool)

**Location**: Lines 1145-1186 in mockup  
**Endpoint**: `POST /maintenance/maintenance-event/<event_id>/action/<action_id>/tool/<tool_id>/update` (NEW)

#### Form Fields:

| Field Name | HTML Input Type | Data Type | Required | Current Status | Notes |
|------------|----------------|-----------|----------|----------------|-------|
| `tool_id` | number | Integer (FK) | Yes | ✅ Exists | Updates `ActionTool.tool_id` |
| `quantity_required` | number | Integer | Yes | ✅ Exists | Updates `ActionTool.quantity_required` |
| `status` | select | String | Yes | ✅ Exists | Updates `ActionTool.status` |
| `priority` | select | String | No | ✅ Exists | Updates `ActionTool.priority` |
| `notes` | textarea | Text | No | ✅ Exists | Updates `ActionTool.notes` |

**Status**: ❌ **NOT IMPLEMENTED** - Tool creation/edit functionality is completely missing

**Action Required**:
- Create tool update endpoint
- Verify tool creation endpoint exists
- Implement tool management in routes

---

### 1.10 Add Tool Form

**Location**: Lines 1197-1205 in mockup  
**Endpoint**: `POST /maintenance/maintenance-event/<event_id>/action/<action_id>/tool/create` (NEW)

#### Form Fields:

| Field Name | HTML Input Type | Data Type | Required | Current Status | Notes |
|------------|----------------|-----------|----------|----------------|-------|
| `action_id` | URL parameter | Integer | Yes | ✅ Exists | Part of URL |
| `tool_id` | number | Integer (FK) | Yes | ✅ Exists | Creates `ActionTool.tool_id` |

**Status**: ❌ **NOT IMPLEMENTED** - Tool creation is missing

---

### 1.11 Action Creator Portal - Edit Before Insert Modal

**Location**: Lines 1532-1681 in mockup  
**Endpoint**: `POST /maintenance/maintenance-event/<event_id>/action/create` (NEW)



#### Form Fields:

| Field Name | HTML Input Type | Data Type | Required | Current Status | Notes |
|------------|----------------|-----------|----------|----------------|-------|
| `actionName` | text | String | Yes | ⚠️ Partial | Need to create action from form data |
| `actionDescription` | textarea | Text | No | ⚠️ Partial | Need to create action from form data |
| `estimatedDuration` | number (step=0.1) | Float | No | ⚠️ Partial | Need to create action from form data |
| `expectedBillableHours` | number (step=0.1) | Float | No | ⚠️ Partial | Need to create action from form data |
| `safetyNotes` | textarea | Text | No | ⚠️ Partial | Need to create action from form data |
| `notes` | textarea | Text | No | ⚠️ Partial | Need to create action from form data |
| `linkToSource` | checkbox | Boolean | No | ❌ Missing | Option to link to template/proto/action |
| `copyPartDemands` | checkbox | Boolean | No | ⚠️ Partial | ActionFactory supports this |
| `copyTools` | checkbox | Boolean | No | ⚠️ Partial | ActionFactory supports this |
| `copySafetyNotes` | checkbox | Boolean | No | ⚠️ Partial | Already copied via ActionFactory |
| `insertPosition` | select | String | No | ❌ Missing | Options: "end", "beginning", "after" |
| `afterActionId` | select | Integer | No | ❌ Missing | If insertPosition == "after" |

**Status**: ⚠️ **PARTIALLY IMPLEMENTED** - ActionFactory exists but needs wrapper endpoint for edit page

**Action Required**:
- Create action creation endpoint that handles position insertion
- Implement source linking logic (template_action_item_id, proto_action_item_id)
- Implement insert position logic (beginning, end, after specific action)
- Handle sequence_order calculation for insertion

---

### 1.12 Action Sequence Order Controls

**Location**: Lines 722-729, 745-751, etc. (Up/Down arrows)  
**Endpoint**: `POST /maintenance/maintenance-event/<event_id>/action/<action_id>/move-up` (NEW)  
**Endpoint**: `POST /maintenance/maintenance-event/<event_id>/action/<action_id>/move-down` (NEW)
**Endpoint**: `POST /maintenance/maintenance-event/<event_id>/action/<action_id>/reset-sequence` (NEW)

**Status**: ❌ **NOT IMPLEMENTED** - Sequence order movement needs implementation

**Action Required**:
- Create move-up endpoint (decrease sequence_order, renumber others)
- Create move-down endpoint (increase sequence_order, renumber others)
- In case sequence somehow has an error, order by current sequence number re-assign starting at 1 
No comments needed

---

## 2. Current Routes and Endpoints

### 2.1 Maintenance Event Routes (Existing)

**Base Path**: `/maintenance/maintenance-event/<event_id>`

| Route | Method | Handler | Status | Notes |
|-------|--------|---------|--------|-------|
| `/view` | GET | `view_maintenance_event()` | ✅ Working | View-only page |
| `/edit` | GET, POST | `edit_maintenance_event()` | ✅ Working | Handles event details form |
| `/work` | GET | `work_maintenance_event()` | ✅ Working | Work execution page |

### 2.2 Action Routes (Existing)

**Base Path**: `/maintenance/maintenance-event/<event_id>/action/<action_id>`

| Route | Method | Handler | Status | Notes |
|-------|--------|---------|--------|-------|
| `/update-status` | POST | `update_action_status()` | ✅ Working | Status changes with business logic |
| `/update` | POST | `edit_action()` | ✅ Working | Full action edit form, includes billable hours auto-update |
| `/update-billable-hours` | POST | `update_action_billable_hours()` | ⚠️ **REDUNDANT** | **SHOULD BE ELIMINATED** - functionality already integrated into `/update` route with auto-update logic |
| `/part-demand/create` | POST | `create_part_demand()` | ✅ Working | Create part demand for action |

### 2.3 Part Demand Routes (Existing)

**Base Path**: `/maintenance/maintenance-event/<event_id>/part-demand/<part_demand_id>`

| Route | Method | Handler | Status | Notes |
|-------|--------|---------|--------|-------|
| `/issue` | POST | `issue_part_demand()` | ✅ Working | Issue part demand |
| `/cancel` | POST | `cancel_part_demand()` | ✅ Working | Cancel part demand |
| `/undo` | POST | `undo_part_demand()` | ✅ Working | Undo cancelled part demand |

### 2.4 Delay Routes (Existing)

**Base Path**: `/maintenance/maintenance-event/<event_id>/delay`

| Route | Method | Handler | Status | Notes |
|-------|--------|---------|--------|-------|
| `/create` | POST | `create_delay()` | ✅ Working | Create new delay |
| `/<delay_id>/end` | POST | `end_delay()` | ✅ Working | End active delay |

### 2.5 Maintenance-Level Routes (Existing)

**Base Path**: `/maintenance/maintenance-event/<event_id>`

| Route | Method | Handler | Status | Notes |
|-------|--------|---------|--------|-------|
| `/update-datetime` | POST | `update_maintenance_datetime()` | ✅ Working | Update start/end dates |
| `/update-billable-hours` | POST | `update_maintenance_billable_hours()` | ✅ Working | Update total billable hours |
| `/complete` | POST | `complete_maintenance()` | ✅ Working | Complete maintenance event |

---

## 3. Required New Routes

### 3.1 Action Management Routes

| Route | Method | Purpose | Handler Name | Priority |
|-------|--------|---------|--------------|----------|
| `/maintenance/maintenance-event/<event_id>/action/create` | POST | Create new action (Action Creator Portal) | `create_action()` | High |
| `/maintenance/maintenance-event/<event_id>/action/<action_id>/delete` | POST | Delete action | `delete_action()` | High |
| `/maintenance/maintenance-event/<event_id>/action/<action_id>/move-up` | POST | Move action up in sequence | `move_action_up()` | High |
| `/maintenance/maintenance-event/<event_id>/action/<action_id>/move-down` | POST | Move action down in sequence | `move_action_down()` | High |
| `/maintenance/maintenance-event/<event_id>/actions/renumber` | POST | Bulk renumber all actions | `renumber_actions()` | Medium |
| `/maintenance/maintenance-event/<event_id>/action/<action_id>/duplicate` | POST | Duplicate action | `duplicate_action()` | Medium |

**Note**: The existing `/update-billable-hours` route (lines 779-819 in `main.py`) **SHOULD BE ELIMINATED** - billable hours updates are already handled by the main `/update` route (line 763 calls `update_actual_billable_hours_auto()`).

**Verification**: ✅ **SAFE TO REMOVE** - Grep search confirmed no templates reference `update-billable-hours` or `update_action_billable_hours`.

**Optimization Opportunity**: The `/update` route should be enhanced to only call `update_actual_billable_hours_auto()` when billable_hours actually changed:

**Implementation Approach**:
```python
# At start of edit_action() route, after loading action:
old_billable_hours = action.billable_hours

# ... existing update logic ...

# After applying updates (action_context.edit_action(**updates)):
new_billable_hours = action.billable_hours  # Get updated value

# Only auto-update if billable_hours changed
if old_billable_hours != new_billable_hours:
    maintenance_context = MaintenanceContext(maintenance_struct)
    maintenance_context.update_actual_billable_hours_auto()
```

**Benefits**:
- Avoids unnecessary database operations when billable_hours wasn't modified
- More efficient - only updates maintenance-level totals when needed
- Eliminates need for separate `/update-billable-hours` endpoint

**Action Required**: 
1. Enhance `/update` route with before/after billable_hours comparison
2. Remove the `/update-billable-hours` endpoint after verifying no templates reference it
3. Search for references: `grep -r "update-billable-hours\|update_action_billable_hours" app/presentation/templates/`

### 3.2 Part Demand Routes

| Route | Method | Purpose | Handler Name | Priority |
|-------|--------|---------|--------------|----------|
| `/maintenance/maintenance-event/<event_id>/part-demand/<part_demand_id>/update` | POST | Update part demand | `update_part_demand()` | High |
| `/maintenance/maintenance-event/<event_id>/part-demand/<part_demand_id>/delete` | POST | Delete part demand | `delete_part_demand()` | Medium |

### 3.3 Tool Routes

| Route | Method | Purpose | Handler Name | Priority |
|-------|--------|---------|--------------|----------|
| `/maintenance/maintenance-event/<event_id>/action/<action_id>/tool/create` | POST | Create tool requirement | `create_action_tool()` | High |
| `/maintenance/maintenance-event/<event_id>/action/<action_id>/tool/<tool_id>/update` | POST | Update tool requirement | `update_action_tool()` | High |
| `/maintenance/maintenance-event/<event_id>/action/<action_id>/tool/<tool_id>/delete` | POST | Delete tool requirement | `delete_action_tool()` | High |

### 3.4 Delay Routes

| Route | Method | Purpose | Handler Name | Priority |
|-------|--------|---------|--------------|----------|
| `/maintenance/maintenance-event/<event_id>/delay/<delay_id>/update` | POST | Update delay details | `update_delay()` | High |
| `/maintenance/maintenance-event/<event_id>/delay/<delay_id>/delete` | POST | Delete delay | `delete_delay()` | Low |

### 3.5 Comment Routes

**Status**: ✅ **ALREADY IMPLEMENTED** - No new routes needed

| Route | Method | Purpose | Handler Name | Status |
|-------|--------|---------|--------------|--------|
| `/events/<event_id>/comments` | POST | Create event comment | `comments.create()` | ✅ Exists |
| `/events/<event_id>/widget` | GET | Get event widget (HTMX) | `comments.event_widget()` | ✅ Exists |
| `/comments/<comment_id>/edit` | GET, POST | Edit comment | `comments.edit()` | ✅ Exists |
| `/comments/<comment_id>/delete` | POST | Delete comment | `comments.delete()` | ✅ Exists |

**Blueprint**: `comments` (registered in `app/presentation/routes/__init__.py`)  
**URL Pattern**: Use `url_for('comments.create', event_id=event.id)` in templates

### 3.6 Action Creator Portal Search Routes

| Route | Method | Purpose | Handler Name | Priority |
|-------|--------|---------|--------------|----------|
| `/maintenance/maintenance-event/<event_id>/template-actions/search` | GET | Search template actions | `search_template_actions()` | Medium |
| `/maintenance/maintenance-event/<event_id>/proto-actions/search` | GET | Search proto actions | `search_proto_actions()` | Medium |
| `/maintenance/maintenance-event/<event_id>/current-actions/list` | GET | List current actions for duplication | `list_current_actions()` | Medium |

---

## 4. Field Transformation Requirements

### 4.1 DateTime Field Transformations

**Issue**: HTML `datetime-local` inputs provide strings in format `YYYY-MM-DDTHH:mm` but need conversion to Python `datetime` objects.

**Fields Affected**:
- `planned_start_datetime` (Event Details)
- `delay_start_date` (Delay Edit)
- `delay_end_date` (Delay Edit)
- `expected_resolution_date` (Delay Edit) - **Needs verification if field exists**
- `scheduled_start_time` (Action Edit)
- `start_time` (Action Edit)
- `end_time` (Action Edit)

**Transformation Logic**:
```python
# In routes layer (before passing to context/service)
datetime_str = request.form.get('field_name', '').strip()
if datetime_str:
    try:
        parsed_datetime = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M')
    except ValueError:
        flash('Invalid datetime format', 'error')
        return redirect(...)
```

**Current Status**: ✅ Implemented in `edit_maintenance_event()` and `edit_action()` routes

**Action Required**: Apply same transformation pattern to new delay update endpoint

---

### 4.2 Numeric Field Transformations

**Issue**: HTML number inputs provide strings, need conversion to `int` or `float`.

**Fields Affected**:
- `estimated_duration` (Float, step=0.1)
- `labor_hours` (Float, step=0.1)
- `staff_count` (Integer)
- `billable_hours` (Float, step=0.1)
- `quantity_required` (Float, step=0.1 for parts, Integer for tools)
- `sequence_order` (Integer)

**Transformation Logic**:
```python
# Float fields
value_str = request.form.get('field_name', '').strip()
if value_str:
    try:
        value = float(value_str)
        if value < 0:
            flash('Value must be non-negative', 'error')
            return redirect(...)
    except ValueError:
        flash('Invalid numeric value', 'error')
        return redirect(...)

# Integer fields
value_str = request.form.get('field_name', '').strip()
if value_str:
    try:
        value = int(value_str)
        if value < 1:
            flash('Value must be at least 1', 'error')
            return redirect(...)
    except ValueError:
        flash('Invalid integer value', 'error')
        return redirect(...)
```

**Current Status**: ✅ Implemented in existing routes

**Action Required**: Apply same validation pattern to new endpoints

---

### 4.3 Checkbox Field Transformations

**Issue**: HTML checkboxes only send value when checked. Need boolean conversion.

**Fields Affected**:
- `safety_review_required` (Event Details)
- `is_private` (Comment)
- `linkToSource` (Action Creator)
- `copyPartDemands` (Action Creator)
- `copyTools` (Action Creator)
- `copySafetyNotes` (Action Creator)

**Transformation Logic**:
```python
# Standard checkbox pattern
checkbox_value = request.form.get('field_name') == 'on'  # or == 'true' if using hidden input
```

**Current Status**: ✅ Implemented for `safety_review_required`

**Action Required**: Apply to new checkbox fields

---

### 4.4 Select Field Validations

**Issue**: Need to validate select field values against allowed options.

**Fields Affected**:
- `status` (Event Details, Action Edit, Part Demand Edit, Tool Edit, Delay Edit)
- `priority` (Event Details, Part Demand Edit, Tool Edit, Delay Edit)
- `delay_type` (Delay Edit)
- `insertPosition` (Action Creator)

**Transformation Logic**:
```python
# Status validation
valid_statuses = ['Planned', 'In Progress', 'Complete', 'Cancelled', 'Delayed']
status = request.form.get('status', '').strip()
if status and status not in valid_statuses:
    flash('Invalid status', 'error')
    return redirect(...)

# Priority validation
valid_priorities = ['Low', 'Medium', 'High', 'Critical']
priority = request.form.get('priority', 'Medium').strip()
if priority not in valid_priorities:
    priority = 'Medium'  # Default fallback
```

**Current Status**: ⚠️ Partial - Some validations exist, need comprehensive validation for all endpoints

**Action Required**: Create centralized validation functions or use enums/constants

---

### 4.5 Foreign Key Field Transformations

**Issue**: Need to validate foreign key references exist in database.

**Fields Affected**:
- `asset_id` (Event Details)
- `maintenance_plan_id` (Event Details)
- `part_id` (Part Demand)
- `tool_id` (Tool)
- `assigned_user_id` (Action Edit)

**Transformation Logic**:
```python
# Foreign key validation
fk_id_str = request.form.get('field_name', '').strip()
fk_id = None
if fk_id_str:
    try:
        fk_id = int(fk_id_str)
        # Verify exists
        related_obj = Model.query.get(fk_id)
        if not related_obj:
            flash(f'Invalid {field_name}', 'error')
            return redirect(...)
    except ValueError:
        flash(f'Invalid {field_name}', 'error')
        return redirect(...)
```

**Current Status**: ✅ Implemented for `asset_id` and `maintenance_plan_id`

**Action Required**: Apply to new foreign key fields in part demand and tool endpoints

---

### 4.6 Sequence Order Transformations (Special Case)

**Issue**: When inserting actions at specific positions, need to recalculate all sequence orders.

**Transformation Logic**:
```python
# Insert at end
max_sequence = max([a.sequence_order for a in actions], default=0)
new_sequence_order = max_sequence + 1

# Insert at beginning
# Shift all existing actions up by 1
for action in actions:
    action.sequence_order += 1
new_sequence_order = 1

# Insert after specific action
target_sequence = target_action.sequence_order
# Shift all actions after target down by 1
for action in actions:
    if action.sequence_order > target_sequence:
        action.sequence_order += 1
new_sequence_order = target_sequence + 1

# After any sequence order change, ensure no gaps and commit atomically
db.session.commit()
```

**Status**: ❌ **NOT IMPLEMENTED** - Critical for Action Creator Portal

**Action Required**: Create service/helper function for sequence order management

---

## 5. Additional Functionality Opportunities

### 5.1 Action Management Enhancements

#### 5.1.1 Action Reordering
- **Current**: No way to reorder actions
- **Opportunity**: Up/Down arrow buttons (mocked in lines 722-729)
- **Implementation**: Move action and renumber all actions atomically
- **Business Logic**: Maintain sequence_order uniqueness and continuity

#### 5.1.2 Action Duplication
- **Current**: No duplication feature
- **Opportunity**: Duplicate button on action card
- **Implementation**: Copy action with all fields, part demands, and tools
- **Business Logic**: Increment sequence_order, reset status to "Not Started"

### 5.2 Part Demand Enhancements


#### 5.2.2 Part Demand Priority Management
- **Current**: Priority field exists but may not be prominently displayed
- **Opportunity**: Visual priority indicators, sortable by priority
- **Implementation**: Color-coded badges, priority-based sorting
- **Business Logic**: Validate priority values (Low, Medium, High, Critical)



### 5.3 Tool Management Enhancements



#### 5.3.3 Tool Quantity Management
- **Current**: `quantity_required` field exists
- **Opportunity**: Track available quantity vs required quantity
- **Implementation**: Integration with tool inventory system (if exists)
- **Business Logic**: Check tool availability before assignment

### 5.4 Delay Management Enhancements

#### 5.4.1 Delay Resolution Tracking
- **Current**: `delay_end_date` set manually or via "end delay" button
- **Opportunity**: Resolution notes, resolution date tracking
- **Implementation**: Add resolution notes field, track resolution separately from end date
- **Business Logic**: Require resolution notes when ending delay

#### 5.4.2 Delay Impact Analysis
- **Current**: Delays tracked but impact not quantified
- **Opportunity**: Calculate delay duration, billable hours impact
- **Implementation**: Helper methods to calculate delay metrics
- **Business Logic**: Sum delay billable hours, calculate total delay time

#### 5.4.3 Expected Resolution Date
- **Current**: ❌ **Field does NOT exist in MaintenanceDelay model**
- **Opportunity**: Set expected resolution date when creating/editing delay
- **Implementation**: **REQUIRED** - Add `expected_resolution_date` field to MaintenanceDelay model via database migration
- **Business Logic**: Track expected vs actual resolution dates, provide alerts when overdue
DO NOT IMPLEMENT.remove from forms

### 5.5 Action Creator Portal Enhancements

#### 5.5.1 Template Action Set Search
- **Current**: No search functionality for templates in edit context
- **Opportunity**: Search template action sets, browse by category
- **Implementation**: Search endpoint, filter by task name, description
- **Business Logic**: Return template action sets with action count
Do not implement, just add a link to the view template actions page

#### 5.5.2 Proto Action Search
- **Current**: No search functionality for proto actions in edit context
- **Opportunity**: Search proto action library, filter by keywords
- **Implementation**: Search endpoint, filter by action name, description
- **Business Logic**: Return proto actions with part/tool counts

#### 5.5.3 Current Action Duplication
- **Current**: No way to duplicate existing actions from same event
- **Opportunity**: List current actions, duplicate with option to copy execution data
- **Implementation**: List endpoint, duplication with copy options
- **Business Logic**: Reset status to "Not Started", preserve/copy part demands and tools

#### 5.5.4 Source Linking
- **Current**: `template_action_item_id` and `proto_action_item_id` fields exist but linking optional
- **Opportunity**: Maintain link to source template/proto for updates
- **Implementation**: Checkbox option to link, store reference ID
- **Business Logic**: Future: Auto-update actions when template/proto changes (Phase 2+)

### 5.6 Event Activity Enhancements

#### 5.6.1 Comment Attachment Handling
- **Current**: ✅ **ALREADY IMPLEMENTED** - File uploads fully supported
- **Implementation**: `EventContext.add_comment_with_attachments()` handles file uploads
- **Status**: Endpoint at `/events/<event_id>/comments` supports multiple file attachments
- **Files**: Stored via `CommentAttachment` model, accessible via `EventContext.attachments`

#### 5.6.2 Private Comments
- **Current**: ✅ **ALREADY IMPLEMENTED** - Private comments supported
- **Implementation**: `is_private` flag stored on Comment model, endpoint handles checkbox
- **Status**: Private comment functionality exists, visibility filtering may need verification
- **Business Logic**: `EventContext.get_human_comments()` and comment queries should filter by privacy



---

## 6. Maintenance Context Enhancements

### 6.1 Current MaintenanceContext Methods

**Location**: `app/buisness/maintenance/base/maintenance_context.py`

**Existing Methods**:
- `start()` - Start maintenance event
- `complete()` - Complete maintenance event
- `cancel()` - Cancel maintenance event
- `add_delay()` - Add delay to maintenance event
- `end_delay()` - End active delay
- `add_comment()` - Add comment to event
- `update_action_set_details()` - Update maintenance action set fields
- `update_actual_billable_hours_auto()` - Auto-update billable hours
- `set_actual_billable_hours()` - Manually set billable hours
- `sync_actual_billable_hours_to_calculated()` - Sync to calculated sum

### 6.2 Proposed Additional Methods

#### 6.2.1 Action Management Methods

```python
def add_action(
    self,
    action_name: str,
    sequence_order: Optional[int] = None,
    insert_position: str = 'end',  # 'end', 'beginning', 'after'
    after_action_id: Optional[int] = None,
    template_action_item_id: Optional[int] = None,
    proto_action_item_id: Optional[int] = None,
    copy_part_demands: bool = False,
    copy_tools: bool = False,
    **action_kwargs
) -> Action:
    """
    Add new action to maintenance event.
    
    Args:
        action_name: Name of action
        sequence_order: Explicit sequence order (calculated if None)
        insert_position: Where to insert ('end', 'beginning', 'after')
        after_action_id: Action ID to insert after (if insert_position == 'after')
        template_action_item_id: Link to template action (optional)
        proto_action_item_id: Link to proto action (optional)
        copy_part_demands: Copy part demands from template/proto
        copy_tools: Copy tools from template/proto
        **action_kwargs: Additional action fields
        
    Returns:
        Created Action instance
    """
    # Implementation: Calculate sequence_order, create action, copy part demands/tools if requested
    pass

def delete_action(self, action_id: int, preserve_part_demands: bool = False) -> bool:
    """
    Delete action from maintenance event.
    
    Args:
        action_id: Action ID to delete
        preserve_part_demands: If True, move part demands to event level (future)
        
    Returns:
        True if deleted, False if not found
    """
    # Implementation: Delete action (cascade deletes part demands and tools), renumber remaining actions
    pass

def move_action(self, action_id: int, direction: str) -> bool:
    """
    Move action up or down in sequence.
    
    Args:
        action_id: Action ID to move
        direction: 'up' or 'down'
        
    Returns:
        True if moved, False if at boundary
    """
    # Implementation: Swap sequence_order with adjacent action, renumber all actions atomically
    pass

def duplicate_action(self, action_id: int, copy_part_demands: bool = True, copy_tools: bool = True) -> Action:
    """
    Duplicate action with all fields, part demands, and tools.
    
    Args:
        action_id: Action ID to duplicate
        copy_part_demands: Copy part demands from source
        copy_tools: Copy tools from source
        
    Returns:
        Duplicated Action instance with status reset to "Not Started"
    """
    # Implementation: Create copy, reset status, duplicate part demands and tools
    pass

def renumber_actions(self) -> int:
    """
    Renumber all actions to consecutive sequence orders (1, 2, 3, ...).
    
    Returns:
        Number of actions renumbered
    """
    # Implementation: Sort by current sequence_order, assign consecutive orders, commit atomically
    pass
```

#### 6.2.2 Delay Management Methods

```python
def update_delay(
    self,
    delay_id: int,
    delay_type: Optional[str] = None,
    delay_reason: Optional[str] = None,
    delay_start_date: Optional[datetime] = None,
    delay_end_date: Optional[datetime] = None,
    expected_resolution_date: Optional[datetime] = None,
    delay_billable_hours: Optional[float] = None,
    delay_notes: Optional[str] = None,
    priority: Optional[str] = None
) -> MaintenanceDelay:
    """
    Update delay details.
    
    Args:
        delay_id: Delay ID to update
        delay_type: Update delay type
        delay_reason: Update delay reason
        delay_start_date: Update start date
        delay_end_date: Update end date (ending delay)
        expected_resolution_date: Update expected resolution date
        delay_billable_hours: Update billable hours
        delay_notes: Update notes
        priority: Update priority
        
    Returns:
        Updated MaintenanceDelay instance
    """
    # Implementation: Update delay fields, sync maintenance status if ending delay
    pass

def delete_delay(self, delay_id: int) -> bool:
    """
    Delete delay (only if ended).
    
    Args:
        delay_id: Delay ID to delete
        
    Returns:
        True if deleted, False if active or not found
    """
    # Implementation: Only allow deletion of ended delays, update maintenance status if needed
    pass
```

#### 6.2.3 Part Demand Management Methods

```python
def update_part_demand(
    self,
    part_demand_id: int,
    part_id: Optional[int] = None,
    quantity_required: Optional[float] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    notes: Optional[str] = None
) -> PartDemand:
    """
    Update part demand details.
    
    Args:
        part_demand_id: Part demand ID to update
        part_id: Update part
        quantity_required: Update quantity
        status: Update status (with validation)
        priority: Update priority
        notes: Update notes
        
    Returns:
        Updated PartDemand instance
        
    Raises:
        ValueError: If status transition is invalid or part demand belongs to different event
    """
    # Implementation: Validate status transitions, update fields
    pass

def approve_part_demand(
    self,
    part_demand_id: int,
    user_id: int,
    notes: Optional[str] = None
) -> PartDemand:
    """
    Approve part demand (manager approval).
    
    Args:
        part_demand_id: Part demand ID to approve
        user_id: User ID approving
        notes: Approval notes
        
    Returns:
        Updated PartDemand instance with status "Pending Inventory Approval"
        
    Raises:
        ValueError: If part demand not in "Pending Manager Approval" status
    """
    # Implementation: Validate status, set approval fields, transition status, generate comment
    pass

def reject_part_demand(
    self,
    part_demand_id: int,
    user_id: int,
    reason: str
) -> PartDemand:
    """
    Reject part demand (manager rejection).
    
    Args:
        part_demand_id: Part demand ID to reject
        user_id: User ID rejecting
        reason: Rejection reason (required)
        
    Returns:
        Updated PartDemand instance with status "Rejected"
        
    Raises:
        ValueError: If part demand not in "Pending Manager Approval" status
    """
    # Implementation: Validate status, set rejection reason, transition status, generate comment
    pass
```

#### 6.2.4 Tool Management Methods

```python
def create_action_tool(
    self,
    action_id: int,
    tool_id: int,
    quantity_required: int = 1,
    status: str = 'Planned',
    priority: str = 'Medium',
    notes: Optional[str] = None
) -> ActionTool:
    """
    Create tool requirement for action.
    
    Args:
        action_id: Action ID
        tool_id: Tool ID
        quantity_required: Quantity needed
        status: Initial status
        priority: Priority level
        notes: Notes
        
    Returns:
        Created ActionTool instance
    """
    # Implementation: Create ActionTool, validate action belongs to this maintenance event
    pass

def update_action_tool(
    self,
    tool_id: int,  # ActionTool.id, not Tool.id
    tool_id_new: Optional[int] = None,  # Update to different tool
    quantity_required: Optional[int] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    notes: Optional[str] = None
) -> ActionTool:
    """
    Update tool requirement.
    
    Args:
        tool_id: ActionTool ID to update
        tool_id_new: Update to different tool (Tool.id)
        quantity_required: Update quantity
        status: Update status
        priority: Update priority
        notes: Update notes
        
    Returns:
        Updated ActionTool instance
    """
    # Implementation: Update ActionTool fields, validate status transitions
    pass

def delete_action_tool(self, tool_id: int) -> bool:
    """
    Delete tool requirement.
    
    Args:
        tool_id: ActionTool ID to delete
        
    Returns:
        True if deleted, False if not found
    """
    # Implementation: Delete ActionTool
    pass
```

#### 6.2.5 Sequence Order Management Helper

```python
def _calculate_sequence_order(
    self,
    insert_position: str = 'end',
    after_action_id: Optional[int] = None
) -> int:
    """
    Calculate sequence order for new action based on insert position.
    
    Args:
        insert_position: 'end', 'beginning', or 'after'
        after_action_id: Action ID to insert after (if 'after')
        
    Returns:
        Calculated sequence_order
    """
    # Implementation: Calculate appropriate sequence_order based on position
    pass

def _renumber_actions_atomic(self) -> None:
    """
    Renumber all actions atomically to ensure no gaps or duplicates.
    """
    # Implementation: Sort actions, assign consecutive sequence orders, commit
    pass
```

---

## 7. Implementation Phases

### Phase 1: Core Action Management (High Priority)

**Goal**: Enable basic action creation, deletion, and reordering.

**Tasks**:
1. Create `create_action()` endpoint with position insertion logic
2. Create `delete_action()` endpoint with renumbering
3. Create `move_action_up()` and `move_action_down()` endpoints
4. Add sequence order management helper methods to MaintenanceContext
5. Integrate Action Creator Portal modal (template/proto/blank actions)
6. Test action creation from templates, proto actions, and blank

**Estimated Complexity**: High  
**Dependencies**: ActionFactory exists, need wrapper endpoints

---

### Phase 2: Part Demand and Tool Management (High Priority)

**Goal**: Enable full CRUD for part demands and tools.

**Tasks**:
1. Create `update_part_demand()` endpoint
2. Create `delete_part_demand()` endpoint
3. Create `create_action_tool()` endpoint
4. Create `update_action_tool()` endpoint
5. Create `delete_action_tool()` endpoint
6. Add tool management methods to MaintenanceContext
7. Integrate part demand and tool edit panels in UI

**Estimated Complexity**: Medium  
**Dependencies**: Data models exist, need endpoints and context methods

---

### Phase 3: Delay Management Enhancements (Medium Priority)

**Goal**: Enable delay editing and deletion.

**Tasks**:
1. Create `update_delay()` endpoint
2. Create `delete_delay()` endpoint (if needed)
3. Add delay update methods to MaintenanceContext
4. Verify `expected_resolution_date` field exists in MaintenanceDelay model
5. Integrate delay edit panels in UI

**Estimated Complexity**: Low  
**Dependencies**: Delay model exists, need update functionality

---

### Phase 4: Action Creator Portal Search (Medium Priority)

**Goal**: Enable search functionality for Action Creator Portal.

**Tasks**:
1. Create `search_template_actions()` endpoint
2. Create `search_proto_actions()` endpoint
3. Create `list_current_actions()` endpoint
4. Implement search filters (by name, description, keywords)
5. Integrate search in Action Creator Portal UI

**Estimated Complexity**: Medium  
**Dependencies**: Template and proto action models exist

---

### Phase 5: Additional Enhancements (Low Priority)

**Goal**: Polish and additional features.

**Tasks**:
1. Part demand approval workflow integration
2. Comment attachment handling
3. Action duplication feature
4. Bulk renumber actions endpoint
5. Private comment visibility logic
6. UI/UX improvements

**Estimated Complexity**: Varies  
**Dependencies**: Phase 1-4 completion

---

## 8. Data Model Considerations

### 8.1 Field Verification Needed

**Priority**: High

1. **MaintenanceDelay.expected_resolution_date**
   - **Question**: Does this field exist in the model?
   - **Answer**: ❌ **NO** - Field does not exist in `app/data/maintenance/base/maintenance_delays.py`
   - **Action**: Create database migration to add `expected_resolution_date` field to `maintenance_delays` table
   - **Impact**: Required for mockup functionality - field shown in delay edit form
   - **Fields Currently in Model**: `delay_start_date`, `delay_end_date`, but NOT `expected_resolution_date`

2. **ActionTool Model Fields**
   - **Question**: Verify all fields from mockup exist
   - **Fields to Check**: `tool_id`, `quantity_required`, `status`, `priority`, `notes`
   - **Action**: Review `app/data/maintenance/base/action_tools.py`

3. **PartDemand Model Fields**
   - **Question**: Verify approval workflow fields exist
   - **Fields to Check**: `maintenance_approval_by_id`, `maintenance_approval_date`, `supply_approval_by_id`, `supply_approval_date`
   - **Action**: Review `app/data/maintenance/base/part_demands.py` (confirmed exists from earlier analysis)

### 8.2 Sequence Order Constraints

**Priority**: High

**Issue**: Need to ensure sequence_order uniqueness and handle renumbering atomically.

**Considerations**:
- Unique constraint on (maintenance_action_set_id, sequence_order)?
- Or allow gaps but enforce uniqueness?
- Atomic renumbering to prevent race conditions

**Action**: Review current sequence_order implementation in Action model

### 8.3 Cascading Deletes

**Priority**: Medium

**Issue**: When deleting actions, need to handle part demands and tools.

**Current Status**: 
- `part_demands` relationship has `cascade='all, delete-orphan'`
- `action_tools` relationship has `cascade='all, delete-orphan'`

**Action**: Verify cascading behavior is correct for delete operations

### 8.4 Status Transition Validation

**Priority**: Medium

**Issue**: Need business rules for valid status transitions.

**Considerations**:
- Part Demand: Can status go backwards? (e.g., "Issued" → "Pending Manager Approval"?)
- Action Tool: Valid status transitions? (Planned → Assigned → Returned)
- Delay: Can ended delays be reopened?

**Action**: Document status transition rules, implement validation in context methods

---

## 9. Testing Considerations

### 9.1 Unit Tests Needed

1. **MaintenanceContext Methods**:
   - `add_action()` with various insert positions
   - `delete_action()` with renumbering
   - `move_action()` up and down
   - `duplicate_action()` with copy options
   - `renumber_actions()` atomic behavior
   - `update_delay()` with various scenarios
   - `update_part_demand()` with status validation
   - `create_action_tool()` and `update_action_tool()`

2. **Sequence Order Logic**:
   - Insert at beginning, end, after specific action
   - Move up/down at boundaries
   - Concurrent renumbering (race conditions)

### 9.2 Integration Tests Needed

1. **Action Creation Workflow**:
   - Create from template
   - Create from proto
   - Create blank
   - Verify part demands and tools copied correctly

2. **Action Reordering**:
   - Move action up/down
   - Verify sequence_order updated correctly
   - Verify no gaps or duplicates

3. **Part Demand and Tool CRUD**:
   - Create, update, delete part demands
   - Create, update, delete tools
   - Verify cascade deletes work correctly

### 9.3 End-to-End Tests Needed

1. **Edit Page Workflow**:
   - Load edit page
   - Edit event details
   - Add action from template
   - Edit action
   - Add part demand
   - Add tool
   - Create delay
   - Verify all changes persist

---

## 10. Summary

### 10.1 Implementation Status Summary

| Category | Status | Completion |
|----------|--------|------------|
| Event Details Form | ✅ Complete | 100% |
| Action Edit Form | ✅ Complete | 100% |
| Action Creation | ⚠️ Partial | 40% (Factory exists, needs endpoints) |
| Action Deletion | ❌ Missing | 0% |
| Action Reordering | ❌ Missing | 0% |
| Part Demand Edit | ❌ Missing | 0% |
| Part Demand Create | ✅ Complete | 100% |
| Tool Management | ❌ Missing | 0% |
| Delay Edit | ❌ Missing | 0% |
| Delay Create | ✅ Complete | 100% |
| Comment Create | ✅ Complete | 100% (endpoint exists at `/events/<event_id>/comments`) |
| Action Creator Portal | ⚠️ Partial | 30% (needs search and creation endpoints) |

### 10.2 Critical Path Items

1. **Sequence Order Management** - Required for action reordering and insertion
2. **Action Creation Endpoint** - Required for Action Creator Portal
3. **Part Demand Update Endpoint** - Required for part demand editing
4. **Tool Management Endpoints** - Required for tool CRUD operations
5. **Delay Update Endpoint** - Required for delay editing

### 10.3 Estimated Implementation Timeline

- **Phase 1**: 2-3 weeks (Action Management)
- **Phase 2**: 1-2 weeks (Part Demand and Tool Management)
- **Phase 3**: 1 week (Delay Management)
- **Phase 4**: 1-2 weeks (Action Creator Portal Search)
- **Phase 5**: 2-3 weeks (Enhancements)

**Total Estimated Time**: 7-11 weeks for full implementation

---

## Appendix A: Field Mapping Reference

### A.1 Maintenance Event Details → MaintenanceActionSet

| Form Field | Model Field | Type | Notes |
|------------|-------------|------|-------|
| `task_name` | `task_name` | String | From VirtualActionSet |
| `description` | `description` | Text | From VirtualActionSet |
| `estimated_duration` | `estimated_duration` | Float | From VirtualActionSet |
| `asset_id` | `asset_id` | Integer (FK) | Direct field |
| `maintenance_plan_id` | `maintenance_plan_id` | Integer (FK) | Direct field |
| `status` | `status` | String | Direct field, syncs Event.status |
| `priority` | `priority` | String | Direct field |
| `planned_start_datetime` | `planned_start_datetime` | DateTime | Direct field |
| `safety_review_required` | `safety_review_required` | Boolean | From VirtualActionSet |
| `staff_count` | `staff_count` | Integer | From VirtualActionSet |
| `labor_hours` | `labor_hours` | Float | From VirtualActionSet |
| `completion_notes` | `completion_notes` | Text | Direct field |

### A.2 Action Edit → Action

| Form Field | Model Field | Type | Notes |
|------------|-------------|------|-------|
| `action_name` | `action_name` | String | From VirtualActionItem |
| `description` | `description` | Text | From VirtualActionItem |
| `status` | `status` | String | Direct field |
| `sequence_order` | `sequence_order` | Integer | Direct field |
| `estimated_duration` | `estimated_duration` | Float | From VirtualActionItem |
| `expected_billable_hours` | `expected_billable_hours` | Float | From VirtualActionItem |
| `scheduled_start_time` | `scheduled_start_time` | DateTime | Direct field |
| `start_time` | `start_time` | DateTime | Direct field |
| `end_time` | `end_time` | DateTime | Direct field |
| `billable_hours` | `billable_hours` | Float | Direct field |
| `safety_notes` | `safety_notes` | Text | From VirtualActionItem |
| `completion_notes` | `completion_notes` | Text | Direct field |
| `notes` | `notes` | Text | From VirtualActionItem |

### A.3 Part Demand Edit → PartDemand

| Form Field | Model Field | Type | Notes |
|------------|-------------|------|-------|
| `part_id` | `part_id` | Integer (FK) | From VirtualPartDemand |
| `quantity_required` | `quantity_required` | Float | From VirtualPartDemand |
| `status` | `status` | String | Direct field |
| `priority` | `priority` | String | Direct field |
| `notes` | `notes` | Text | From VirtualPartDemand |

### A.4 Tool Edit → ActionTool

| Form Field | Model Field | Type | Notes |
|------------|-------------|------|-------|
| `tool_id` | `tool_id` | Integer (FK) | From VirtualActionTool |
| `quantity_required` | `quantity_required` | Integer | From VirtualActionTool |
| `status` | `status` | String | Direct field |
| `priority` | `priority` | String | Direct field |
| `notes` | `notes` | Text | From VirtualActionTool |

### A.5 Delay Edit → MaintenanceDelay

| Form Field | Model Field | Type | Notes |
|------------|-------------|------|-------|
| `delay_type` | `delay_type` | String | Direct field |
| `delay_reason` | `delay_reason` | String | Direct field |
| `delay_start_date` | `delay_start_date` | DateTime | Direct field |
| `delay_end_date` | `delay_end_date` | DateTime | Direct field |
| `expected_resolution_date` | `expected_resolution_date` | DateTime | **❌ FIELD DOES NOT EXIST - Requires database migration** |
| `delay_billable_hours` | `delay_billable_hours` | Float | Direct field |
| `delay_notes` | `delay_notes` | Text | Direct field |
| `priority` | `priority` | String | Direct field |

---

## Document Revision History

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2024-01-15 | 1.0 | Planning | Initial planning document creation |

---

**END OF DOCUMENT**


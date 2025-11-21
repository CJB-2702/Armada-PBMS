# Business Core Refactoring Review - Impact Analysis

## Overview
This document reviews the impact of moving read-only, presentation-specific methods from business layer context managers to services layer.

## Proposed Changes

### 1. Move `AssetContext.recent_events()` → `AssetService.get_recent_events()`

**Current Location**: `app/buisness/core/asset_context.py` (line 95-105)

**New Location**: `app/services/core/asset_service.py`

**Reason**: Read-only, presentation-specific query method that formats data for display.

---

## Impact Analysis

### Routes Using `AssetContext.recent_events()`

#### 1. `app/presentation/routes/core/assets.py`

**File**: `app/presentation/routes/core/assets.py`

**Usages**:
- **Line 60**: `detail()` route
  ```python
  events=asset_context.recent_events(limit=10)
  ```
  - **Impact**: Needs update to use `AssetService.get_recent_events(asset_id, limit=10)`
  - **Complexity**: Low - Direct replacement
  
- **Line 211**: `asset_details_card()` route
  ```python
  events=asset_context.recent_events(limit=5)
  ```
  - **Note**: Uses `AssetDetailsContext` which extends `AssetContext`, so inherits `recent_events()`
  - **Impact**: Needs update to use `AssetService.get_recent_events(asset_id, limit=5)`
  - **Complexity**: Low - Direct replacement

**Summary**: 2 occurrences, both simple replacements

---

### 2. Move `EventContext.get_human_comments()` → `EventService.get_human_comments()`

**Current Location**: `app/buisness/core/event_context.py` (line 68-78)

**New Location**: `app/services/core/event_service.py`

**Reason**: Read-only, presentation-specific filter method for displaying comments.

---

## Impact Analysis

### Routes Using `EventContext.get_human_comments()`

#### 1. `app/presentation/routes/core/events/comments.py`

**File**: `app/presentation/routes/core/events/comments.py`

**Usages**:
- **Line 58**: `create()` route (HTMX response)
  ```python
  comments = event_context.get_human_comments()
  ```
  - **Context**: After adding a comment, returns filtered widget for HTMX update
  - **Impact**: Needs update to use `EventService.get_human_comments(event_id)`
  - **Complexity**: Low - Direct replacement

- **Line 90**: `event_widget()` route
  ```python
  comments = event_context.get_human_comments()
  ```
  - **Context**: Widget endpoint that can filter to human comments only
  - **Impact**: Needs update to use `EventService.get_human_comments(event_id)`
  - **Complexity**: Low - Direct replacement

**Summary**: 2 occurrences, both simple replacements

---

#### 2. `app/presentation/routes/maintenance/main.py`

**File**: `app/presentation/routes/maintenance/main.py`

**Usage Check**:
- **Line 194-195**: Uses `EventContext` but **ONLY** for `add_comment()` method
  ```python
  event_context = EventContext(context.event.id)
  event_context.add_comment(...)
  ```
  - **Impact**: **NO IMPACT** - Only uses data modification method which stays in business layer
  - **Action**: No changes required

**Summary**: No impact - only uses business logic methods

---

## Routes Not Affected

### `app/presentation/routes/assets/`
- **Status**: No usage of `recent_events()` or `get_human_comments()` found
- **Action**: No changes required

### `app/presentation/routes/maintenance/`
- **Status**: Uses `EventContext` but only for `add_comment()` (data modification)
- **Action**: No changes required

---

## Implementation Plan

### Step 1: Add Methods to Services

1. **Add to `AssetService`**:
   ```python
   @staticmethod
   def get_recent_events(asset_id: int, limit: int = 10) -> List[Event]:
       """Get recent events for an asset"""
       return Event.query.filter_by(asset_id=asset_id)\
                         .order_by(Event.timestamp.desc())\
                         .limit(limit).all()
   ```

2. **Add to `EventService`**:
   ```python
   @staticmethod
   def get_human_comments(event_id: int) -> List[Comment]:
       """Get only human-made comments for an event"""
       return Comment.query.filter_by(
           event_id=event_id,
           is_human_made=True
       ).order_by(Comment.created_at.desc()).all()
   ```

### Step 2: Update Routes

**Files to Update**:
1. `app/presentation/routes/core/assets.py` (2 occurrences)
2. `app/presentation/routes/core/events/comments.py` (2 occurrences)

**Total Updates**: 4 locations across 2 files

### Step 3: Update Context Managers (Optional)

- Keep methods in context managers for backward compatibility (if needed)
- Add deprecation notices if desired
- Or remove methods entirely since all routes will be updated

---

## Benefits

1. **Clear Separation**: Presentation queries separated from business logic
2. **Reusability**: Service methods can be used by multiple routes easily
3. **Testability**: Service methods can be tested independently
4. **Consistency**: Follows the same pattern as other list/filter operations

---

## Backward Compatibility

**Note**: `AssetDetailsContext` extends `AssetContext`, so it inherits `recent_events()`. 
- If we remove the method from `AssetContext`, `AssetDetailsContext` will lose access
- **Recommendation**: Remove method from `AssetContext` after updating all routes (only 2 occurrences)
- Or keep as deprecated for one release cycle

---

## Risk Assessment

- **Risk Level**: **LOW**
- **Affected Routes**: 4 occurrences across 2 files
- **Complexity**: Simple replacements
- **Testing Required**: Verify all 4 routes work correctly after changes

---

## Approval Status

- ✅ **Impact Analysis Complete**
- ✅ **Routes Identified**
- ⏳ **Awaiting Approval**
- ⏳ **Implementation Pending**


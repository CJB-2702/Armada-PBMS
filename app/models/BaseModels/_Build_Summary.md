# Initial Data Summary and Build Order Verification

## Build Order (from create_tables function)

The tables are created in this specific order to avoid circular dependencies:

1. **Users** - No dependencies
2. **Asset Types** - No dependencies  
3. **Major Locations** - Depends on Asset Types
4. **Minor Locations** - Depends on Asset Types
5. **Event Types** - No dependencies
6. **Events** - Depends on Users, Locations, and Event Types

## Initial Data Summary by Model

### 1. Users (Table: `users`)
**Creation Method:** SQLAlchemy event listener (auto-created when table is created)
**Expected Count:** 2 users

```python
Required_users = [
    {
        "row_id": 0,
        "username": "SYSTEM",
        "email": "system@null.null",
        "is_admin": True,
        "display_name": "System",
        "role": "admin",
        "created_by": 0,
    },
    {
        "row_id": 1,
        "username": "admin",
        "email": "admin@null.com",
        "is_admin": True,
        "display_name": "System Administrator",
        "role": "admin",
        "created_by": 0,
    }
]
```

### 2. Asset Types (Table: `types_assets`)
**Creation Method:** `ensure_required_asset_types()` function
**Expected Count:** 2 asset types

```python
initial_asset_types = [
    {
        "name": "System",
        "description": "System assets",
        "created_by": 0
    },
    {
        "name": "General",
        "description": "General assets",
        "created_by": 0
    }
]
```

### 3. Major Locations (Table: `MajorLocations`)
**Creation Method:** `ensure_required_system_location()` function
**Expected Count:** 1 system location
**Dependencies:** Asset Types (uses "MajorLocation" asset type)

```python
Required_system_location = [
    {
        "UID": "SYSTEM",
        "common_name": "System Location",
        "description": "Virtual system location for internal system operations",
        "status": "active",
        "created_by": 0,
        "location_id": 0
    }
]
```

### 4. Minor Locations (Table: `MinorLocations`)
**Creation Method:** No initial data
**Expected Count:** 0 (no initial minor locations)
**Dependencies:** Asset Types (uses "MinorLocation" asset type)

### 5. Event Types (Table: `types_events`)
**Creation Method:** `ensure_required_event_types()` function
**Expected Count:** 2 event types

```python
Required_event_types = [
    {
        "name": "System",
        "description": "System events",
        "created_by": 0
    },
    {
        "name": "General",
        "description": "Basic Events, only a title and description",
        "created_by": 0
    }
]
```

### 6. Events (Table: `events`)
**Creation Method:** `create_initial_events()` function
**Expected Count:** 3 events
**Dependencies:** Users, Locations, and Event Types

```python
initial_events = [
    {
        "title": "User Created: SYSTEM (ID: 0)",
        "description": "User created.\nUsername: SYSTEM\nDisplay Name: System\nEmail: system@null.null\nRole: admin\nIs Admin: True",
        "event_type_id": "SYSTEM",
        "status": "completed",
        "created_by": 0
    },
    {
        "title": "User Created: admin (ID: 1)",
        "description": "User created.\nUsername: admin\nDisplay Name: System Administrator\nEmail: admin@null.com\nRole: admin\nIs Admin: True",
        "event_type_id": "SYSTEM",
        "status": "completed",
        "created_by": 0
    },
    {
        "title": "System Location Created: System Location (ID: 0)",
        "description": "System location created.\nUID: SYSTEM\nCommon Name: System Location\nDescription: Virtual system location for internal system operations\nStatus: active",
        "event_type_id": "SYSTEM",
        "status": "completed",
        "created_by": 0
    }
]
```

## Data Insertion Order (from insert_initial_data function)

The data is inserted in this order to respect dependencies:

1. **Step 1:** Verify Users (auto-created via event listener)
2. **Step 2:** Create Asset Types (no dependencies)
3. **Step 3:** Create System Location (depends on asset types)
4. **Step 4:** Create Event Types (no dependencies)
5. **Step 5:** Create Initial Events (depends on users, locations, and event types)

## Verification Summary

✅ **Build Order Consistency:** The data insertion order perfectly matches the table creation order and respects all dependencies.

✅ **Dependency Resolution:** All foreign key relationships are properly handled:
- Users are created first (no dependencies)
- Asset Types are created second (no dependencies)
- Major Locations depend on Asset Types ✓
- Minor Locations depend on Asset Types ✓
- Event Types are created independently ✓
- Events depend on Users, Locations, and Event Types ✓

✅ **Data Completeness:** All required initial data is properly defined and will be created.

✅ **Count Verification:** The expected counts in the verification functions match the actual data definitions:
- Users: 2 ✓
- Asset Types: 2 ✓
- Major Locations: 1 ✓
- Event Types: 2 ✓
- Events: 3 ✓


## Recommendations

1. **Consider adding validation** to ensure asset types "System" and "General" exist before creating locations
2. **Add error handling** for cases where required data is missing during event creation

The build order and initial data are correctly structured and should work as expected. 
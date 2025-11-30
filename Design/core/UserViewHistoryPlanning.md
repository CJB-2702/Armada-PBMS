# User View History System - Planning Document

## Overview

This document outlines the design and implementation plan for a user view history tracking system. The system will track user navigation patterns, store view history in a database table, and provide utility functions for analyzing viewing patterns.

## Goals

1. **Track User Navigation**: Record when users view specific pages/routes, particularly maintenance events
2. **Enable "Recently Viewed" Features**: Support the "View Recent Events" QoL feature from TechnicianPortalQOLFeatures.md
3. **Analytics**: Provide insights into most commonly viewed events and maintenance events
4. **Data Management**: Automatically clean up old view history data (>2 weeks old)
5. **Performance**: Use in-memory caching to reduce database writes while maintaining data persistence

---

## Architecture Overview

The system is divided into three main components:

1. **Data Model** (`UserViewHistory`): Stores raw view history records with `resource_type` and `resource_id`
2. **ViewHistoryManager** (Business Layer): Handles recording views with in-memory caching to prevent duplicates
3. **ViewHistoryService** (Service Layer): Handles all queries and analytics, understands resource type relationships

**Key Design Decision**: The manager focuses solely on storing data efficiently. The service layer handles all the complexity of understanding that:
- `resource_type='maintenance_event'` with `resource_id=MaintenanceActionSet.id` is an `event_id` and can be joined to get `asset_id`
- Both resource types `resource_type='event'` and `resource_type='maintenance_event'` should be combined when counting "event views"
- `resource_type='event'` with `resource_id=Event.id` can be joined to get `asset_id`


---

## Architecture Components

### 1. Data Model: `UserViewHistory` Table

**Location**: `app/data/core/user_info/user_view_history.py`

**Purpose**: Persistent storage of all user view history records

**Routes to Track** (Design Decision):

The following specific routes will be tracked with view history:

1. `/core/events/<id>` - Core event detail view
   - `resource_type='event'`
   - `resource_id=Event.id`

2. `/core/assets/<id>` - Core asset detail view
   - `resource_type='asset'`
   - `resource_id=Asset.id`

3. `/assets/all-details/<id>` - Asset all-details view
   - `resource_type='asset'`
   - `resource_id=Asset.id`

4. `/maintenance/maintenance-event/<id>/view` - Maintenance event view
   - `resource_type='maintenance_event'`
   - `resource_id=MaintenanceActionSet.id`

5. `/maintenance/maintenance-event/<id>/edit` - Maintenance event edit
   - `resource_type='maintenance_event'`
   - `resource_id=MaintenanceActionSet.id`

**Note**: Only these specific routes are tracked. Other routes are not tracked to avoid performance issues and privacy concerns.


**Inheritance**: Inherits from `UserCreatedBase` which provides:
- `id` (Primary Key) - serial int
- `created_at` (DateTime) - Timestamp of the view (automatically set)
- `created_by_id` (Integer, FK to `users.id`) - The user who viewed (set to `current_user.id`)
- `updated_at` (DateTime) - Automatically updated (not used for view history)
- `updated_by_id` (Integer, FK to `users.id`, nullable) - Set to `None` (view history is not updated)

**Additional Fields**:
- `route_name` (String) - The Flask route name (e.g., `'maintenance.view_event'`)
- `route_path` (String) - The actual URL path (e.g., `/maintenance/events/123`)
- `resource_type` (String, nullable) - Type of resource viewed: `'maintenance_event'`, `'asset'`, `'event'`, etc.
- `resource_id` (Integer, nullable) - ID of the resource (e.g., MaintenanceActionSet.id, Event.id, Asset.id)

**Note**: `current_user` from Flask-Login is a `User` object with an `id` attribute. The decorator will set `created_by_id = current_user.id`.

**Relationships**:
- Many-to-one with `User` via `created_by_id` (inherited from `UserCreatedBase`)

**Indexes**:
- `(created_by_id, created_at)` - For querying user's recent views
- `(resource_type, resource_id, created_at)` - For querying most common views
- `created_at` - For cleanup operations

---

### 2. ViewHistoryManager

**Location**: `app/buisness/core/user_info/view_history_manager.py`

**Purpose**: Centralized manager for recording view history with in-memory caching. Focuses solely on storing view history data.

**Design Decisions**:

1. **Singleton Pattern**: The manager is implemented as a singleton (single instance shared across all requests)

2. **Concurrent Request Handling**: If a user makes concurrent requests to the same `route_path`, the manager immediately returns without recording (prevents duplicate consecutive views). The check compares `route_path` (without query parameters) against the cached `last_route` for that user.

3. **Thread Safety**: The dict is **not** thread-safe for now. Flask is typically single-threaded per request, but if using multiple workers/async, occasional duplicate records may occur (acceptable for MVP).

4. **Application Restart**: On application restart, the cache dict starts empty. The cache is not persisted between sessions. Database records persist, so no data loss occurs.

5. **Cache Clearing**: Application should recycle once a day. For now, ignore periodic cache clearing. Create a `clear_cache()` function but leave automatic cycle clearing as a TODO.

**Proposed Structure**:

#### In-Memory State
- `_view_cache` (Dict): `{user_id: {'last_route': str, 'last_viewed_at': datetime}}`
  - Stores the last route path viewed by each user
  - Used to prevent recording duplicate consecutive views
  - Cleared on application restart (not persisted)

#### Core Methods

**`record_view(user_id, route_name, route_path, resource_type=None, resource_id=None)`**

- Check if this view is different from user's last view (compare route_path without query parameters)
  - If different: 
    - Create `UserViewHistory` record with:
      - `created_by_id = user_id` (from `current_user.id`)
      - `route_name`, `route_path`, `resource_type`, `resource_id`
      - `updated_by_id = None` (view history is never updated)
    - Add record to database
    - Update `_view_cache[user_id]` with new route info
  - If same: Skip (don't record duplicate consecutive views)

**`cleanup_old_history(days=14)`**
- Delete `UserViewHistory` records where `created_at < (now - days)`
- **Implementation**: Since the application is restarted daily, call this method on application startup to clear records older than 2 weeks
- Can also be called manually via Flask CLI command or admin endpoint if needed

**`clear_cache()`**
- Manually clear the in-memory cache (for testing or manual intervention)

#### Initialization
- `_view_cache` starts as empty dict `{}`

---

### 3. ViewHistoryService

**Location**: `app/services/core/user_info/view_history_service.py`

**Purpose**: Service layer for querying and analyzing view history data. Handles all read operations and analytics.

**Key Responsibilities**:
- Query view history for recently viewed items
- Aggregate view counts for analytics
- Join with Event/MaintenanceActionSet/Asset tables to resolve relationships
- Understand that both `resource_type='maintenance_event'` and `resource_type='event'` count towards event views
- Understand that the event_id can be used to query for an asset_id  and count towards asset views

#### Core Methods

**`get_recently_viewed_events(user_id, limit=5, days=7)`**
- Query `UserViewHistory` for user's recent event views
- Filter by `created_by_id = user_id` and `created_at >= (now - days)`
- Filter by `resource_type IN ('maintenance_event', 'event')`
- For `resource_type='maintenance_event'`: Join with `MaintenanceActionSet` to get `event_id`
- For `resource_type='event'`: `resource_id` is already the `event_id`
- Return list of event IDs or event objects, ordered by `created_at DESC`

**`get_most_common_events_viewed(limit=10, days=30)`**
- Aggregate views for events across all users
- Filter by `created_at >= (now - days)`
- Handle both resource types:
  - `resource_type='maintenance_event'`: Join `MaintenanceActionSet` to get `event_id`, then count views per `event_id`
  - `resource_type='event'`: Count views per `resource_id` (which is `event_id`)
- Combine counts from both resource types for the same `event_id`
- Group by `event_id`, order by total count descending
- Return list of `(event_id, view_count)` tuples

**`get_most_common_maintenance_events_viewed(limit=10, days=30)`**
- Similar to `get_most_common_events_viewed()` but filter only `resource_type='maintenance_event'`
- Filter by `created_at >= (now - days)`
- Join `MaintenanceActionSet` to get `event_id`
- Group by `event_id`, order by count descending
- Return list of `(event_id, view_count)` tuples

**`get_most_viewed_assets(limit=10, days=30)`**
- Aggregate views for assets across all users
- Filter by `created_at >= (now - days)`
- Handle multiple resource types:
  - `resource_type='asset'`: `resource_id` is already `asset_id`
  - `resource_type='maintenance_event'`: Join `MaintenanceActionSet` to get `asset_id`
  - `resource_type='event'`: Join `Event` to get `asset_id`
- Combine counts from all resource types for the same `asset_id`
- Group by `asset_id`, order by total count descending
- Return list of `(asset_id, view_count)` tuples

**`get_recently_viewed_assets(user_id, limit=5, days=7)`**
- Query `UserViewHistory` for user's recent asset views
- Filter by `created_by_id = user_id` and `created_at >= (now - days)`
- Handle multiple resource types:
  - `resource_type='asset'`: `resource_id` is already `asset_id`
  - `resource_type='maintenance_event'`: Join `MaintenanceActionSet` to get `asset_id`
  - `resource_type='event'`: Join `Event` to get `asset_id`
- Return list of asset IDs or asset objects, ordered by `created_at DESC`

**Query Logic for Resource Type Resolution**:

**For Event Views**:
- `resource_type='maintenance_event'` + `resource_id=MaintenanceActionSet.id`:
  - Join: `UserViewHistory` → `MaintenanceActionSet` (on `resource_id = MaintenanceActionSet.id`)
  - Get: `MaintenanceActionSet.event_id` and `MaintenanceActionSet.asset_id`
- `resource_type='event'` + `resource_id=Event.id`:
  - `resource_id` is already `Event.id`
  - Join: `UserViewHistory` → `Event` (on `resource_id = Event.id`)
  - Get: `Event.asset_id`

**For Asset Views**:
- `resource_type='asset'` + `resource_id=Asset.id`:
  - `resource_id` is already `Asset.id`
- `resource_type='maintenance_event'` + `resource_id=MaintenanceActionSet.id`:
  - Join: `UserViewHistory` → `MaintenanceActionSet` → get `asset_id`
- `resource_type='event'` + `resource_id=Event.id`:
  - Join: `UserViewHistory` → `Event` → get `asset_id`

---

### 4. Route Decorator

**Location**: `app/presentation/decorators/view_history.py` (or similar)

**Purpose**: Decorator to automatically track views on specific routes

**Key Design Questions**:
- Should the decorator extract `resource_type` and `resource_id` automatically from route parameters?
- How do we handle routes with different parameter names? (e.g., `event_id` vs `maintenance_event_id`)
- Should the decorator be configurable to specify what to track?

**Proposed Decorator**:

**`@track_view_history(resource_type=None, resource_id_param=None)`**

**Parameters**:
- `resource_type` (str, optional): Type of resource ('maintenance_event', 'asset', 'event', etc.)
  - If not provided, decorator attempts to infer from route name
- `resource_id_param` (str, optional): Name of route parameter containing resource ID
  - If not provided, decorator attempts common names (e.g., 'event_id', 'maintenance_event_id', 'asset_id')

**Usage Examples** (for all tracked routes):
```python
# Track core event views
@bp.route('/core/events/<int:event_id>')
@login_required
@track_view_history(resource_type='event', resource_id_param='event_id')
def view_event(event_id):
    # Route implementation
    pass

# Track core asset views
@bp.route('/core/assets/<int:asset_id>')
@login_required
@track_view_history(resource_type='asset', resource_id_param='asset_id')
def view_asset(asset_id):
    # Route implementation
    pass

# Track asset all-details views
@bp.route('/assets/all-details/<int:asset_id>')
@login_required
@track_view_history(resource_type='asset', resource_id_param='asset_id')
def view_asset_all_details(asset_id):
    # Route implementation
    pass

# Track maintenance event view
@bp.route('/maintenance/maintenance-event/<int:maintenance_action_set_id>/view')
@login_required
@track_view_history(resource_type='maintenance_event', resource_id_param='maintenance_action_set_id')
def view_maintenance_event(maintenance_action_set_id):
    # Route implementation
    pass

# Track maintenance event edit
@bp.route('/maintenance/maintenance-event/<int:maintenance_action_set_id>/edit')
@login_required
@track_view_history(resource_type='maintenance_event', resource_id_param='maintenance_action_set_id')
def edit_maintenance_event(maintenance_action_set_id):
    # Route implementation
    pass
```

**Decorator Logic**:
1. Extract `user_id` from `current_user.id` (must be authenticated - `current_user` is a `User` object)
2. Extract `route_name` from Flask's `request.endpoint`
3. Extract `route_path` from Flask's `request.path` and **strip query parameters** (everything after `?`)
   - Example: `/maintenance/events/123?filter=active` → `/maintenance/events/123`
   - **Decision**: Do not record anything to the right of a question mark in the route_path
4. Extract `resource_id` from route kwargs using `resource_id_param`
5. **There should be no route listeners if route is an API endpoint** (check if route path starts with `/api/` or route name contains `api`)
   - **Decision**: No tracking allowed on API endpoints. Tracking is primarily for portal usage.
6. Call `ViewHistoryManager.record_view(user_id, route_name, route_path, resource_type, resource_id)` with extracted data
   - Manager will set `created_by_id = user_id` when creating the record
7. Continue to original route function


**Error Handling**:
- If `current_user` is not authenticated log warning reject path
- If `resource_id_param` is specified but not found in kwargs, log warning but continue
- If `ViewHistoryManager.record_view()` fails, log error but don't break the route

---

## Data Flow

### Recording a View

1. User navigates to a route decorated with `@track_view_history`
2. Decorator extracts route information (`route_name`, `route_path`, `resource_type`, `resource_id`) and user context
3. Decorator calls `ViewHistoryManager.record_view(user_id, route_name, route_path, resource_type, resource_id)`
4. Manager checks if this view differs from user's last view (compares `route_path` without query parameters)
5. If different:
   - Insert record into `UserViewHistory` table with all extracted data
   - Update in-memory cache `{user_id: {'last_route': route_path, 'last_viewed_at': datetime}}`
6. If same: Skip (don't record duplicate consecutive views)
7. Route continues normally

### Querying View History

1. Route or service calls `ViewHistoryService.get_recently_viewed_events(user_id)`
2. Service queries `UserViewHistory` table with appropriate joins
3. Service resolves resource types and combines counts as needed
4. Returns formatted results

---

## Cleanup Logic

### Automatic Cleanup of Old History

**Requirement**: Delete view history records older than 2 weeks

**Options**:

1. **Cleanup on system start** execute cleanup function on Manager init
3. **Separate Cleanup Endpoint**
   - Admin-only endpoint to trigger cleanup
   - **Concern**: Requires manual intervention

**Recommendation**: Use option 1 on start cleanup , with option 3 as a backup for manual cleanup if needed.

---

## Questions and Clarifications Needed

### 1. Scope of Tracking
- **Decision**: Track only specific routes (not all routes)
- **Tracked Routes**:
  - `/core/events/<id>` - Core event detail view
  - `/core/assets/<id>` - Core asset detail view
  - `/assets/all-details/<id>` - Asset all-details view
  - `/maintenance/maintenance-event/<id>/view` - Maintenance event view
  - `/maintenance/maintenance-event/<id>/edit` - Maintenance event edit
- **Rationale**: Tracking only specific routes avoids performance issues and privacy concerns. Can expand to additional routes as needed.

### 2. Resource Identification
- **Q**: How do we identify what type of resource is being viewed?
  - Option A: Decorator explicitly specifies `resource_type` and `resource_id_param`
  - Option B: Infer from route name patterns (e.g., routes with `/maintenance/events/` are maintenance events)
  - Option C: Store route name only, infer resource type when querying
- **Recommendation**: Option A (explicit) is clearest and most maintainable, with Option B as fallback for common patterns.

### 3. In-Memory Dict vs Database-Only
- **Decision**: Use in-memory dict to prevent duplicate consecutive views from being recorded
- **Rationale**: Dict is faster than querying database for last view on every request
- **Trade-off**: Dict uses memory but provides better performance; database query adds latency
- **Note**: Dict is not thread-safe (see Thread Safety section below)

### 4. Thread Safety
- **Decision**: Dict is **not** thread-safe for MVP
- **Concurrent Request Handling**: If same user makes concurrent requests to the same `route_path`, the manager immediately returns without recording (prevents duplicate consecutive views)
- **Rationale**: Flask is typically single-threaded per request. If using multiple workers/async, occasional duplicate records may occur (acceptable for MVP)
- **Future Enhancement**: If thread safety becomes an issue, add locking or use database-level deduplication

### 5. Cache Clear Strategy
- **Decision**: Ignore periodic cache clearing for now. Create `clear_cache()` function but leave automatic cycle clearing as a TODO
- **Rationale**: Application recycles once a day, so cache is naturally cleared on restart
- **Future Enhancement**: If needed, implement per-user TTL (clear individual user entries after inactivity period)

### 6. "Most Common" Definition
- **Q**: What does "most common" mean?
  - Total views by count
- **Recommendation**: Provide both options:
  - `get_most_common_events_viewed(user_id)` - Total views by count for a user
  - 

### 7. Integration with PortalUserData
- **Q**: Should view history be stored in `PortalUserData.maintenance_cache` or separate table?
- ignore PortalUserData for now. later ill want to store summary information in the cache.


### 8. Event vs Maintenance Event
- **Q**: What's the difference between "events" and "maintenance events"?
- **Context**: `Event` is a generic event table, `MaintenanceActionSet` is linked to events (one-to-one)

- **Answer**: 
  - `/core/events/<id>` tracks `resource_type='event'` with `resource_id=Event.id`
  - `/maintenance/maintenance-event/<id>` tracks `resource_type='maintenance_event'` with `resource_id=MaintenanceActionSet.id`
  - Both should count towards "event views" - the service joins `MaintenanceActionSet` to get `event_id` when needed
  - The service understands this relationship and combines counts appropriately

---

## Recommendations

### 1. Start Simple, Iterate
- Begin with tracking only maintenance event views
- Add other resource types (assets, generic events) as needed
- Monitor performance and adjust caching strategy

### 2. Use Database for Persistence, Cache for Performance
- Always write to database for data persistence
- Use in-memory cache only to prevent duplicate consecutive writes
- Don't rely on cache for queries (always query database)

### 3. Make Decorator Explicit
- Require explicit `resource_type` and `resource_id_param` in decorator
- This makes it clear what's being tracked and avoids magic/inference
- Can add helper functions later for common patterns

### 4. Cache Management
- For MVP: Cache is cleared on application restart (application recycles daily)
- Cache clearing function exists but automatic periodic clearing is deferred as TODO
- Future: If needed, implement per-user TTL (clear individual user entries after inactivity period)

### 5. Scheduled Cleanup Task
- Use a scheduled background task (Flask CLI command or Celery) for cleanup
- Run daily or weekly, not on every cache clear
- Keep cleanup separate from view recording logic

### 6. Add Indexes Early
- Index `(created_by_id, created_at)` for user queries
- Index `(resource_type, resource_id, created_at)` for analytics queries
- Index `created_at` for cleanup queries
- Consider index on `(resource_type, created_at)` for filtering by resource type

### 7. Consider View Deduplication
- If same user views same resource within X seconds (e.g., 30 seconds), treat as single view
- Prevents accidental double-counting from page refreshes or navigation loops

### 8. Add Admin Interface
- Consider adding admin view to see view history statistics
- Useful for debugging and understanding usage patterns

---

## Implementation Phases

### Phase 1: Core Infrastructure
1. Create `UserViewHistory` data model with `resource_type` and `resource_id` fields
2. Create database migration
3. Create `ViewHistoryManager` with basic `record_view()` method and in-memory cache
4. Create decorator `@track_view_history`

### Phase 2: Caching and Deduplication
1. Implement in-memory cache dict
2. Implement cache clear logic (per-user TTL)
3. Implement duplicate detection (compare last view)

### Phase 3: Service Layer
1. Create `ViewHistoryService` class
2. Implement `get_recently_viewed_events()` with resource type resolution
3. Implement `get_most_common_events_viewed()` combining both resource types
4. Implement `get_most_common_maintenance_events_viewed()`
5. Implement `get_most_viewed_assets()` with joins to resolve asset_id
6. Implement `get_recently_viewed_assets()` with joins to resolve asset_id

### Phase 4: Cleanup
1. Implement `cleanup_old_history(days=14)` method
2. Call `cleanup_old_history()` on application startup to clear records older than 14 days
3. Test cleanup with old data

### Phase 5: Integration
1. Add `@track_view_history` decorator to the following routes:
   - `/core/events/<id>` - Core event detail view
   - `/core/assets/<id>` - Core asset detail view
   - `/assets/all-details/<id>` - Asset all-details view
   - `/maintenance/maintenance-event/<id>/view` - Maintenance event view
   - `/maintenance/maintenance-event/<id>/edit` - Maintenance event edit
2. Test end-to-end flow for each route
3. Monitor performance and verify view history is being recorded correctly

### Phase 6: Analytics and UI
1. Create admin portal routes to view history:
   - `/admin/view-history/all` - Admin view of all view history (admin only)
   - `/user/<id>/view-history/` - User view of their own history (self or admin only)
2. Implement access control:
   - Users can only view their own history
   - Admins can view any user's history
3. Integrate with "Recently Viewed" feature in Technician Portal
4. Add dashboard widgets showing most common events
5. Add admin interface for view statistics

---

## Design Decisions - Open Questions Answered

### 1. Route Parameters Tracking
- **Decision**: Do not record anything to the right of a question mark in the route_path
- **Implementation**: Strip query parameters from `request.path` before storing
- **Example**: `/maintenance/events/123?filter=active&page=2` → `/maintenance/events/123`

### 2. Failed Views Tracking
- **Decision**: Do not track failed views (404s, permission denied)
- **Rationale**: Only track successful page loads to maintain data quality

### 3. View Duration Tracking
- **Decision**: Do not track view duration (time spent on page)
- **Rationale**: Keep the system simple and focused on "what was viewed" not "how long"

### 4. API Endpoints vs HTML Pages
- **Decision**: No tracking allowed on API endpoints. Tracking is primarily for portal usage.
- **Implementation**: Decorator should check if route is an API endpoint and skip tracking
- **Detection**: Check if route path starts with `/api/` or route name contains `api`

### 5. User Visibility
- **Decision**: View history is ONLY self-visible unless admin
- **Implementation**:
  - Users can view their own history at `/user/<id>/view-history/` (only if `<id>` matches their user_id)
  - Admins can view any user's history
  - Non-admin users cannot view other users' history

### 6. Privacy and Data Retention
- **Decision**: Delete view history after 14 days
- **Implementation**: `cleanup_old_history(days=14)` runs on application startup
- **Rationale**: Balances usefulness of recent history with privacy concerns 

---

## Implementation Questions

Before beginning implementation, please clarify the following:

### 1. Route Path Storage Format
- **Question**: Should `route_path` be stored with or without the base URL?
  - Option A: Store full path only (e.g., `/maintenance/events/123`)
  - Option B: Store with query params stripped but keep full path structure
  - **Current Plan**: Store path without query parameters (everything after `?` is removed)
  - **Clarification Needed**: Is this the desired behavior, or should we also normalize paths in any other way?

### 2. Decorator Placement and Route Detection
- **Question**: How should the decorator detect API endpoints?
  - Option A: Check if `request.path.startswith('/api/')`
  - Option B: Check if route name contains `'api'` or `'API'`
  - Option C: Both checks (path and route name)
  - Option D: Add explicit parameter to decorator `@track_view_history(allow_api=False)`
  - **Recommendation**: Option C (both checks) for safety, but need confirmation

### 3. Error Handling for Missing Resource IDs
- **Question**: What should happen if a route is decorated but the `resource_id_param` is not found in route kwargs?
  - Option A: Skip tracking silently (log debug message)
  - Option B: Skip tracking with warning log
  - Option C: Raise an error (fail fast)
  - **Current Plan**: Option B (log warning but continue), but need confirmation

### 4. Database Migration Strategy
- **Question**: Should the `UserViewHistory` table be created in a new migration or added to an existing migration?
  - **Clarification Needed**: What's the current migration strategy/numbering system?

### 5. Service Method Return Types
- **Question**: What format should service methods return?
  - For `get_recently_viewed_events()`:
    - Option A: List of event IDs `[1, 2, 3, ...]`
    - Option B: List of Event objects
    - Option C: List of dicts with metadata `[{'event_id': 1, 'viewed_at': ..., 'route_path': ...}, ...]`
  - For `get_most_common_events_viewed()`:
    - Option A: List of tuples `[(event_id, count), ...]`
    - Option B: List of dicts `[{'event_id': 1, 'view_count': 5, 'asset_id': 10}, ...]`
  - **Recommendation**: Need to know what format the consuming code expects

### 6. Admin Portal Implementation Details
- **Question**: What should the admin portal display?
  - Option A: Simple list of all view history records with filters (user, date range, resource type)
  - Option B: Aggregated statistics (most viewed events, most active users, etc.)
  - Option C: Both - list view with statistics dashboard
  - **Clarification Needed**: What level of detail is needed for admin debugging/monitoring?

### 7. Integration with Application Startup
- **Question**: Where should `cleanup_old_history()` be called on application startup?
  - Option A: In `app/__init__.py` in `create_app()` function
  - Option B: Create a Flask CLI command `flask cleanup-view-history`
  - Option C: Both - CLI command for manual use, auto-call on startup
  - **Recommendation**: Option C, but need confirmation on startup hook location

### 8. Testing Strategy
- **Question**: What level of testing is required?
  - Unit tests for manager/service methods?
  - Integration tests for decorator on actual routes?
  - Performance tests for cache behavior?
  - **Clarification Needed**: Testing requirements and scope

---

## Next Steps

1. **Answer the implementation questions above**
2. **Review final design decisions** in this document
3. **Begin Phase 1 implementation** once all questions are resolved


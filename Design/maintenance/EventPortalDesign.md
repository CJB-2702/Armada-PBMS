# Event Portal Design - Reusable Event View Module

## Overview

This document outlines the design for creating a reusable `render_view_events_module` function that can be used in both the **Technician Portal** and **Manager Portal** for viewing and filtering maintenance events. The goal is to consolidate the overlapping filtering logic currently found in `/maintenance/manager/view-maintenance?type=events` and create a shared, enhanced event viewing module.

## Goals

1. **Code Reusability**: Create a single, well-structured function that can be used across multiple portals
2. **Enhanced Functionality**: Add new features including:
   - Assigned technician information
   - Action completion fraction (completed actions / total actions)
   - Last comment date
3. **Comprehensive Filtering**: Support filtering by:
   - Major location
   - User created by
   - User assigned to
   - Asset
   - Make/Model
   - Action title (containing actions with specific title)
   - Status (existing)
   - Priority (existing)
4. **Service Layer**: Create reusable services and filters that can be shared between portals
5. **Separation of Concerns**: Move all event viewing logic to a dedicated module

## Current State Analysis

### Existing Implementation

**Location**: `/app/presentation/routes/maintenance/manager/main.py`
- Route: `view_maintenance()` at `/maintenance/manager/view-maintenance`
- Current filters: `status`, `asset_id`
- Basic pagination (20 items per page)
- Simple query building with minimal filtering

**Overlapping Logic Found In**:
- `/app/presentation/routes/maintenance/manager/create_assign.py` - `unassigned_events()` route
- `/app/services/maintenance/assign_monitor_service.py` - `get_unassigned_events()` method
- `/app/services/core/event_service.py` - `build_event_query()` method (for general events)

### Current Data Model Relationships

```
MaintenanceActionSet
├── event_id (FK → Event) [ONE-TO-ONE]
├── asset_id (FK → Asset)
├── assigned_user_id (FK → User)
├── assigned_by_id (FK → User)
├── created_by_id (FK → User) [from UserCreatedBase]
└── actions (List[Action])

Event
├── user_id (FK → User) [created by]
├── asset_id (FK → Asset)
├── major_location_id (FK → MajorLocation)
└── comments (List[Comment])

Asset
├── make_model_id (FK → MakeModel)
└── major_location_id (FK → MajorLocation)

MakeModel
└── asset_type_id (FK → AssetType)
```

## Proposed Architecture

### File Structure

```
app/presentation/routes/maintenance/
├── event_portal.py          # NEW: Main event viewing module
└── manager/
    └── main.py              # MODIFY: Use render_view_events_module()

app/services/maintenance/
└── event_portal_service.py  # NEW: Service for event query building and filtering
```

### Function Signature

```python
def render_view_events_module(
    request: Request,
    current_user: User,
    portal_type: str = 'manager',  # 'manager' or 'technician'
    default_filters: Optional[Dict] = None,
    per_page: int = 20,
    template_name: str = 'maintenance/event_portal/view_events.html'
) -> str:
    """
    Render the events view module with filtering and pagination.
    
    Args:
        request: Flask request object
        current_user: Current logged-in user
        portal_type: Type of portal ('manager' or 'technician')
        default_filters: Optional default filter values
        per_page: Number of items per page
        template_name: Template to render
        
    Returns:
        Rendered HTML string
    """
```

## Service Layer Design

### EventPortalService

**Location**: `/app/services/maintenance/event_portal_service.py`

**Purpose**: Build and execute queries for maintenance events with comprehensive filtering, enhanced data, and filter management.

**Key Methods**:

```python
class EventPortalService:
    # Query Building Methods
    @staticmethod
    def build_events_query(
        # Filter parameters
        status: Optional[str] = None,
        priority: Optional[str] = None,
        assigned_user_id: Optional[int] = None,
        created_by_user_id: Optional[int] = None,
        asset_id: Optional[int] = None,
        make_model_id: Optional[int] = None,
        major_location_id: Optional[int] = None,
        action_title: Optional[str] = None,  # Filter events containing actions with this title
        
        # Portal-specific filters
        portal_type: str = 'manager',
        current_user_id: Optional[int] = None,  # For technician portal
        
        # Date filters
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        
        # Search
        search_term: Optional[str] = None,
        
        # Ordering
        order_by: str = 'created_at',
        order_direction: str = 'desc'
    ) -> Query:
        """
        Build a SQLAlchemy query for maintenance events with all filters applied.
        
        Returns:
            SQLAlchemy Query object ready for pagination
        """
    
    @staticmethod
    def get_events_with_enhanced_data(
        query: Query,
        page: int = 1,
        per_page: int = 20
    ) -> Pagination:
        """
        Execute query with pagination and add enhanced data to each event.
        
        Enhanced data includes:
        - assigned_user (User object)
        - created_by_user (User object)
        - asset (Asset object with make_model)
        - major_location (MajorLocation object)
        - action_completion_fraction (float: completed/total)
        - total_actions (int)
        - completed_actions (int)
        - last_comment_date (datetime or None)
        
        Returns:
            Flask-SQLAlchemy Pagination object with enhanced items
        """
    
    @staticmethod
    def get_event_enhanced_data(event: MaintenanceActionSet) -> Dict:
        """
        Get enhanced data for a single maintenance event.
        
        Returns:
            Dictionary with enhanced fields:
            {
                'assigned_user': User or None,
                'created_by_user': User or None,
                'asset': Asset or None,
                'major_location': MajorLocation or None,
                'make_model': MakeModel or None,
                'action_completion_fraction': float,
                'total_actions': int,
                'completed_actions': int,
                'last_comment_date': datetime or None,
                'last_comment_by': User or None
            }
        """
    
    # Filter Management Methods
    @staticmethod
    def get_filter_options() -> Dict:
        """
        Get all available filter options for dropdowns.
        
        Returns:
            Dictionary with filter options:
            {
                'statuses': List[str],
                'priorities': List[str],
                'users': List[User],  # For assigned/created by
                'assets': List[Asset],
                'make_models': List[MakeModel],
                'major_locations': List[MajorLocation],
                'asset_types': List[AssetType]  # For make_model filtering
            }
        """
    
    @staticmethod
    def extract_filters_from_request(request: Request) -> Dict:
        """
        Extract filter parameters from Flask request.
        
        Returns:
            Dictionary with filter values:
            {
                'status': Optional[str],
                'priority': Optional[str],
                'assigned_user_id': Optional[int],
                'created_by_user_id': Optional[int],
                'asset_id': Optional[int],
                'make_model_id': Optional[int],
                'major_location_id': Optional[int],
                'action_title': Optional[str],
                'date_from': Optional[datetime],
                'date_to': Optional[datetime],
                'search_term': Optional[str],
                'page': int
            }
        """
    
    @staticmethod
    def get_active_filters(filters: Dict) -> Dict:
        """
        Get only the active (non-None) filters for display.
        
        Returns:
            Dictionary of active filter key-value pairs
        """
```

## Enhanced Functionality Details

### 1. Assigned To

**Data Source**: `MaintenanceActionSet.assigned_user_id` → `User`

**Display**: Show assigned technician username with link to user profile (if applicable)

**Filter**: Filter by `assigned_user_id` in query

**Implementation**:
- Join `MaintenanceActionSet.assigned_user` relationship
- Include in enhanced data dictionary
- Display in template with badge/icon

### 2. Action Completion Fraction

**Data Source**: 
- Total: `len(MaintenanceActionSet.actions)`
- Completed: `len([a for a in MaintenanceActionSet.actions if a.status == 'Complete'])`
- Fraction: `completed_actions / total_actions` (0.0 if total_actions == 0)

**Display**: 
- Progress bar or fraction display (e.g., "3/5" or "60%")
- Color coding: Green (100%), Yellow (50-99%), Red (<50%)

**Implementation**:
- Calculate in `get_event_enhanced_data()`
- Use existing `MaintenanceContext.completion_percentage` if available
- Cache calculation to avoid N+1 queries

### 3. Last Comment Date

**Data Source**: `Event.comments` → `Comment.created_at` (max)

**Display**: 
- Show date/time of most recent comment
- Show comment author if available
- Display "No comments" if none exist

**Implementation**:
- Query: `Comment.query.filter_by(event_id=event_id).order_by(Comment.created_at.desc()).first()`
- Filter out deleted/hidden comments (where `user_viewable` is not 'deleted' or 'edit')
- Use subquery or join to avoid N+1 queries
- Consider using `func.max()` in SQLAlchemy for efficiency

**Query Optimization**:
```python
from sqlalchemy import func, select

# Subquery for last comment date per event
last_comment_subq = (
    select(
        Comment.event_id,
        func.max(Comment.created_at).label('last_comment_date'),
        func.max(Comment.id).label('last_comment_id')
    )
    .where(Comment.user_viewable.is_(None))  # Only visible comments
    .group_by(Comment.event_id)
    .subquery()
)
```

## Filter Specifications

### 1. Major Location Filter

**Filter Parameter**: `major_location_id` (int)

**Query Logic**:
```python
if major_location_id:
    # Filter via Event.major_location_id or Asset.major_location_id
    query = query.join(Event).filter(
        or_(
            Event.major_location_id == major_location_id,
            Asset.major_location_id == major_location_id
        )
    )
```

- verify that the MaintenanceEventfactory is setting the event major location to the asset major location by default, allow a parameter to overrwite, update creation forms at a later date

**Options Source**: `MajorLocation.query.filter_by(is_active=True).order_by(MajorLocation.name).all()`

### 2. User Created By Filter

**Filter Parameter**: `created_by_user_id` (int)

**Query Logic**:
```python
if created_by_user_id:
    query = query.filter(MaintenanceActionSet.created_by_id == created_by_user_id)
```

**Options Source**: `User.query.filter_by(is_active=True).order_by(User.username).all()`

### 3. User Assigned To Filter

**Filter Parameter**: `assigned_user_id` (int)

**Query Logic**:
```python
if assigned_user_id:
    query = query.filter(MaintenanceActionSet.assigned_user_id == assigned_user_id)
```

**Options Source**: 
- For manager portal: All active users
- For technician portal: Only current user (auto-filtered)

### 4. Asset Filter

**Filter Parameter**: `asset_id` (int)

**Query Logic**:
```python
if asset_id:
    query = query.filter(MaintenanceActionSet.asset_id == asset_id)
```

**Options Source**: `Asset.query.filter_by(status='Active').order_by(Asset.name).all()`

### 5. Make/Model Filter

**Filter Parameter**: `make_model_id` (int)

**Query Logic**:
```python
if make_model_id:
    query = query.join(Asset).filter(Asset.make_model_id == make_model_id)
```

**Options Source**: `MakeModel.query.filter_by(is_active=True).order_by(MakeModel.make, MakeModel.model).all()`

### 6. Status Filter (Existing)

**Filter Parameter**: `status` (str)

**Query Logic**:
```python
if status:
    query = query.filter(MaintenanceActionSet.status == status)
```

**Options**: `['Planned', 'In Progress', 'Delayed', 'Complete']`

### 7. Priority Filter (Existing)

**Filter Parameter**: `priority` (str)

**Query Logic**:
```python
if priority:
    query = query.filter(MaintenanceActionSet.priority == priority)
```

**Options**: `['Low', 'Medium', 'High', 'Critical']`

### 8. Action Title Filter

**Filter Parameter**: `action_title` (str)

**Query Logic**:
```python
if action_title:
    # Filter events that contain at least one action with matching title
    # Uses ILIKE for case-insensitive partial matching
    query = query.join(Action).filter(
        Action.action_name.ilike(f'%{action_title}%')
    ).distinct()  # Use distinct to avoid duplicate events when multiple actions match
```

**Options Source**: 
- Text input field (search/filter by action name)
- Can optionally provide autocomplete suggestions from existing action names:
  ```python
  Action.query.with_entities(Action.action_name).distinct().order_by(Action.action_name).all()
  ```
  review searchbar guidence in [ApplictionDesign.md]

**Implementation Notes**:
- Uses `ILIKE` for case-insensitive partial matching
- Requires `distinct()` to avoid duplicate events when multiple actions in the same event match
- Can be combined with other filters
- Consider adding an index on `Action.action_name` if performance becomes an issue

## Implementation Plan

### Phase 1: Service Layer

1. **Create EventPortalService** (`/app/services/maintenance/event_portal_service.py`)
   - Implement `build_events_query()` with all filters
   - Implement `get_events_with_enhanced_data()` with pagination
   - Implement `get_event_enhanced_data()` for single event
   - Implement `get_filter_options()` to fetch all dropdown options
   - Implement `extract_filters_from_request()` to parse query parameters
   - Implement `get_active_filters()` for display
   - Add query optimization for last comment date (subquery)
   - Add query optimization for action counts (aggregation)

### Phase 2: Route Module

3. **Create event_portal.py** (`/app/presentation/routes/maintenance/event_portal.py`)
   - Implement `render_view_events_module()` function
   - Handle request parsing
   - Call services to get data
   - Prepare template context
   - Return rendered HTML

4. **Create Blueprint** (if needed)
   - Register routes for technician portal
   - Share routes between portals if applicable

### Phase 3: Template

5. **Create Template** (`/app/presentation/templates/maintenance/event_portal/view_events.html`)
   - Event list display with enhanced data
   - Filter form with all filter options
   - Pagination controls
   - Action completion progress indicators
   - Last comment date display
   - Responsive design

6. **Create Filter Partial** (`/app/presentation/templates/maintenance/event_portal/filters.html`)
   - Reusable filter form component
   - Can be included in other templates

### Phase 4: Integration

7. **Update Manager Portal**
   - Modify `/app/presentation/routes/maintenance/manager/main.py`
   - Replace `view_maintenance()` event logic with `render_view_events_module()`
   - Update template to use new module

8. **Create Technician Portal**
   - Create new routes in `event_portal.py` or separate technician routes
   - Use `render_view_events_module()` with `portal_type='technician'`
   - Apply technician-specific filters (e.g., only show assigned events)

### Phase 5: Testing & Refinement

9. **Test Filter Combinations**
   - Test all filter combinations
   - Verify query performance
   - Test pagination with filters

10. **Optimize Queries**
    - Add database indexes if needed
    - Optimize N+1 queries
    - Add query result caching if appropriate

## Query Optimization Considerations

### Avoiding N+1 Queries

**Problem**: Loading related data (users, assets, comments) for each event individually.

**Solutions**:

1. **Eager Loading**:
```python
from sqlalchemy.orm import joinedload, selectinload

query = query.options(
    joinedload(MaintenanceActionSet.assigned_user),
    joinedload(MaintenanceActionSet.asset).joinedload(Asset.make_model),
    joinedload(MaintenanceActionSet.event).selectinload(Event.comments)
)
```

2. **Subqueries for Aggregations**:
```python
# Action counts subquery
action_counts_subq = (
    select(
        Action.maintenance_action_set_id,
        func.count(Action.id).label('total_actions'),
        func.sum(case((Action.status == 'Complete', 1), else_=0)).label('completed_actions')
    )
    .group_by(Action.maintenance_action_set_id)
    .subquery()
)

# Last comment subquery (as shown above)
```

3. **Batch Loading**:
   - Load all events first
   - Collect all related IDs
   - Load related objects in batches
   - Map back to events

## Template Context Structure

```python
{
    'events': Pagination object with enhanced items,
    'filter_options': {
        'statuses': List[str],
        'priorities': List[str],
        'users': List[User],
        'assets': List[Asset],
        'make_models': List[MakeModel],
        'major_locations': List[MajorLocation]
    },
    'active_filters': Dict[str, Any],
    'portal_type': str,  # 'manager' or 'technician'
    'current_user': User
}
```

## Portal-Specific Behavior

### Manager Portal
- View all events (no default user filter)
- Can filter by any assigned user
- Can filter by any created user
- Full access to all filters

### Technician Portal
- Default filter: `assigned_user_id == current_user.id`
- Can optionally view unassigned events
- Limited filter options (may hide some filters)
- Focus on "my work" view

## Future Enhancements

1. **Export Functionality**: Export filtered events to CSV/Excel
2. **Saved Filters**: Save commonly used filter combinations
3. **Advanced Search**: Full-text search across event descriptions, comments
4. **Bulk Actions**: Select multiple events for bulk operations
5. **Real-time Updates**: WebSocket updates for event status changes
6. **Customizable Columns**: Allow users to show/hide columns
7. **Sorting**: Multi-column sorting
8. **Date Range Presets**: "Last 7 days", "This month", etc.

## Dependencies

- Flask
- Flask-SQLAlchemy
- Flask-Login
- SQLAlchemy (for advanced queries)

## Related Files to Review

- `/app/presentation/routes/maintenance/manager/main.py` - Current implementation
- `/app/presentation/routes/maintenance/manager/create_assign.py` - Unassigned events
- `/app/services/maintenance/assign_monitor_service.py` - Existing service patterns
- `/app/services/core/event_service.py` - Event filtering patterns
- `/app/buisness/maintenance/base/maintenance_context.py` - Business logic
- `/app/data/maintenance/base/maintenance_action_sets.py` - Data model

## Notes

- Consider creating a base class for portal-specific behavior if more portals are planned
- The enhanced data calculation should be efficient - consider caching if performance becomes an issue
- Last comment date query should filter out deleted/hidden comments using `user_viewable` field
- Action completion calculation can leverage existing `MaintenanceContext.completion_percentage` property
- Ensure all filters work correctly with pagination (filters should persist across pages)


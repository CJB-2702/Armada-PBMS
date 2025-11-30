# Technician Portal Quality of Life Features - Brainstorming Document

## Overview

This document outlines quality of life (QoL) features for the technician portal, organized by implementation complexity. These features focus on quick access, workflow optimization, and improving daily productivity.

## Features by Complexity

### Single Event Quick Access Features

These features provide direct links to individual events, not list views
they also show information about the action list and event activity module with the comments collapsed

---

#### 1. Most Recently Assigned Event
**Description**: Quick link/button to jump directly to the most recently assigned event to the technician.

**Use Case**: When a technician receives a new assignment notification, they can quickly navigate to it without searching through lists.

**Implementation**:
- Query: `MaintenanceActionSet.query.filter_by(assigned_user_id=current_user.id).order_by(assigned_at.desc()).first()`
- Dashboard widget with "Go to Latest Assignment" button
- Direct link in navigation bar

**Priority**: High

---

#### 2. Most Recently Commented On Event
**Description**: Quick access to the event the technician last commented on, useful for following up on ongoing work.

**Use Case**: Technician wants to check if there's a response to their comment or continue a conversation thread.

**Implementation**:
- Query: Join `Comment` with `Event` and `MaintenanceActionSet`, filter by `comment.user_id == current_user.id`, order by `comment.created_at.desc()`, limit 1
- "Continue Discussion" button on dashboard
- Link in navigation with timestamp ("Last commented: 2 hours ago")

**Priority**: High

---

### Prepared Queries - Event List Views

These features display filtered lists of events and can leverage the `/maintenance/view-events` portal with HTMX for dashboard widgets.

---

#### 3. View Assigned Events
**Description**: Quick filter/view showing all events currently assigned to the technician.
- show top 5 , with link to view events page with filters

**Use Case**: Primary work queue view - see everything on your plate.

**HTMX Implementation**: ✅ **Can use HTMX**
- URL: `/maintenance/view-events?assigned_user_id={current_user.id}&per_page=5`
- HTMX target: Dashboard card showing top 5 assigned events
- Full view link: `/maintenance/view-events?assigned_user_id={current_user.id}`

**Filters Used**: 
- `assigned_user_id` ✅ (Already implemented)
- `status` ✅ (Already implemented - optional filter)

**Priority**: High (Core Feature)

---

#### 4. View Recently Completed Events
**Description**: Quick access to events the technician recently completed, useful for reference or follow-up.
- show top 5 , with link to view events page with filters

**Use Case**: 
- Technician needs to reference a similar completed job
- Manager asks about a recently completed event
- Technician wants to review their completion history

**HTMX Implementation**: ✅ **Can use HTMX**
- URL: `/maintenance/view-events?assigned_user_id={current_user.id}&status=Complete&order_by=updated_at&order_direction=desc&per_page=5`
- HTMX target: Dashboard card showing top 5 recently completed events
- Full view link: `/maintenance/view-events?assigned_user_id={current_user.id}&status=Complete`

**Filters Used**: 
- `assigned_user_id` ✅ (Already implemented)
- `status=Complete` ✅ (Already implemented)
- `order_by=updated_at` ✅ (Already implemented)
- `date_from` / `date_to` ✅ (Already implemented - for date range filtering)

**Priority**: Low-Medium

---

#### 5. Assigned Events Planned This Week
**Description**: List of all events in planned state or in progress state assigned to technician with planned start date +/- 7 days

**Use Case**: Plan the day's work, see time conflicts, estimate completion.

**HTMX Implementation**: ✅ **Can use HTMX**
- URL: `/maintenance/view-events?assigned_user_id={current_user.id}&status=Planned&date_from={start_of_week}&date_to={end_of_week}&per_page=5`
- HTMX target: Dashboard card showing top 5 planned events this week
- Full view link: `/maintenance/view-events?assigned_user_id={current_user.id}&status=Planned&date_from={start_of_week}&date_to={end_of_week}`

**Filters Used**: 
- `assigned_user_id` ✅ (Already implemented)
- `status=Planned` ✅ (Already implemented)
- `date_from` / `date_to` ✅ (Already implemented)

**Priority**: Medium-High

---

#### 6. View Events with Comments from You
**Description**: Filter showing all events where the technician has left comments, useful for tracking ongoing discussions. show 5 most recent with link to view events page

**Use Case**: 
- Technician wants to see all events they're actively discussing
- Follow up on questions they asked
- Track events where they need to respond

**HTMX Implementation**: ⚠️ **Requires new filter**
- URL: `/maintenance/view-events?assigned_user_id={current_user.id}&has_my_comments=true&order_by=last_comment_date&order_direction=desc&per_page=5`
- HTMX target: Dashboard card showing top 5 events with your comments
- Full view link: `/maintenance/view-events?assigned_user_id={current_user.id}&has_my_comments=true`

**Filters Used**: 
- `assigned_user_id` ✅ (Already implemented)
- `has_my_comments` ❌ (Needs implementation - see Advanced Filters section)
- `order_by=last_comment_date` ❌ (Needs implementation - see Advanced Filters section)

**Priority**: Medium

---

#### 7. View Recent Events (Recently Viewed)
**Description**: Quick access to recently viewed or interacted with events, regardless of status.

**Use Case**: Technician needs to quickly return to events they were working on earlier in the day or week.

**HTMX Implementation**: ⚠️ **Requires view tracking**
- URL: `/maintenance/view-events?recently_viewed=true&per_page=5` (after tracking implemented)
- HTMX target: Dashboard card showing top 5 recently viewed events
- Full view link: `/maintenance/view-events?recently_viewed=true`

**Filters Used**: 
- `recently_viewed` ❌ (Needs implementation - requires EventView tracking table)
- Requires tracking: Store event views in session or database table (`EventView` with `user_id`, `event_id`, `viewed_at`)

**Priority**: skip for now requires caching system

---

#### 8. Quick Asset Lookup
**Description**: Fast search/autocomplete to jump directly to an asset's maintenance history.

**Use Case**: Technician needs to quickly check an asset's maintenance history or find related events.

**Implementation**:
- Global search bar in navigation
- Asset autocomplete with recent assets first
- Query: `Asset.query.filter(Asset.name.ilike(f'%{search_term}%')).limit(10)`
- Keyboard shortcut (e.g., `Ctrl+K` for quick search)
- **Link to portal**: `/maintenance/view-events?asset_id={selected_asset_id}`

**Priority**: High

---

#### 8. Top Five Assets with Most Actions Completed by You in last six months
**Description**: Dashboard widget showing the technician's most frequently worked-on assets.

**Use Case**: 
- Quick access to familiar assets
- Understanding work patterns
- Personal statistics/achievement tracking

**Implementation**:
- Query: Join `Action` with `MaintenanceActionSet` and `Asset`, filter by `assigned_user_id == current_user.id` and `status == 'Complete'`, group by `asset_id`, count actions, order by count desc, limit 5
- Card widget with asset names and completion counts
- Click to filter events for that asset
- Time period selector (all time, this month, this year)

**Priority**: Low-Medium

---



### Custom Queries
#### 9. Ten Most Recent Part Demands with Status Updates
**Description**: Show the ten most recent part demands with status updates on events assigned to you and their new status.

**Use Case**: 
- Track part request status changes
- Know when parts are approved or available
- Follow up on part requests

**Implementation**:
- Query: Join `PartDemand` with `Action`, `MaintenanceActionSet`, and `Event`, filter by `assigned_user_id == current_user.id`, filter for status changes (track `updated_at` or use audit log), order by `updated_at.desc()`, limit 10
- Display: Part name, quantity, old status → new status, event link, timestamp
- May require tracking status changes (audit log or `updated_at` comparison)

**Priority**: Medium-High

---

#### 10. Ten Oldest Part Demands Needing Approval
**Description**: Show the ten oldest part demands from events you are assigned to that need approval.

**Use Case**: 
- Identify parts waiting longest for approval
- Prioritize follow-up on delayed approvals
- Track approval bottlenecks

**Implementation**:
- Query: Join `PartDemand` with `Action`, `MaintenanceActionSet`, filter by `assigned_user_id == current_user.id`, filter by `status == 'Requested'` or `maintenance_approval_by_id == None`, order by `created_at.asc()`, limit 10
- Display: Part name, quantity, days waiting, event link, priority
- Show approval status (maintenance approval, supply approval)

**Priority**: Medium-High

---

#### 11.
Ten oldest Not issued, recjected, pending manager approval, or canceled part demands
- Identify parts that were approved but havent been recieved, basically parts approved by the manager or supply or have been ordered backoredered but not recieved



### High Complexity Features

Require user preference storage, complex data structures, advanced tracking, or sophisticated UI components.

---

#### 12. Favorite/Labeled Events (Pin up to 5)
**Description**: Allow technicians to pin up to 5 events to the top of the dashboard.

**Use Case**: 
- Mark important events for quick access
- Prioritize critical work
- Create personal work groups

**Implementation**:
- Requires new table: `UserEventPin` with `user_id`, `maintenance_action_set_id`, `pinned_at`, `display_order`
- Enforce limit: Maximum 5 pins per user
- Query: Join `UserEventPin` with `MaintenanceActionSet`, filter by `user_id == current_user.id`, order by `display_order`
- UI: Star/pin button on event cards, drag-and-drop reordering
- Display pinned events at top of dashboard

**Priority**: Low-Medium

---

#### 13. Work History Timeline
**Description**: Visual timeline showing technician's work history over time.

**Use Case**: 
- Review past work
- Understand work patterns
- Reference completed events

**Implementation**:
- Query: `MaintenanceActionSet.query.filter_by(assigned_user_id=current_user.id).order_by(created_at)`
- Group by day/week/month
- Visual timeline widget (calendar or horizontal timeline)
- Filter by date range
- Show completion status with colors
- May require charting library (e.g., Chart.js, D3.js)

**Priority**: Low

---

## Feature Summary Table

| Feature | Type | HTMX Ready | Complexity | Priority | Key Implementation |
|---------|------|------------|-----------|----------|-------------------|
| Most Recently Assigned Event | Single Event | N/A | Low | High | Simple query with order_by |
| Most Recently Commented On Event | Single Event | N/A | Low | High | Join Comment with Event |
| View Assigned Events | Event List | ✅ Yes | Low | High | Filter by assigned_user_id |
| View Recently Completed Events | Event List | ✅ Yes | Low | Low-Medium | Filter by status='Complete' |
| Assigned Events Planned This Week | Event List | ✅ Yes | Low | Medium-High | Filter by status='Planned' + date |
| View Events with Comments from You | Event List | ⚠️ Needs Filter | Medium | Medium | Join + group by event |
| View Recent Events | Event List | ⚠️ Needs Tracking | Medium | Medium | Requires view tracking |
| Quick Asset Lookup | Search | N/A | Low | High | Search/autocomplete |
| Top Five Assets with Most Actions | Aggregation | N/A | Medium | Low-Medium | Aggregation query |
| Recent Part Demand Status Updates | Part Demands | N/A | Medium | Medium-High | Join + status change tracking |
| Oldest Part Demands Needing Approval | Part Demands | N/A | Medium | Medium-High | Join + filter by approval status |
| Favorite/Labeled Events (Pin 5) | User Preference | N/A | High | Low-Medium | New table + UI for pinning |
| Work History Timeline | Visualization | N/A | High | Low | Complex visualization |

## Implementation Considerations

### User Experience Considerations
- **Discoverability**: Features should be easy to find and understand
- **Consistency**: Follow existing UI patterns
- **Accessibility**: Ensure features work for all users
- **Performance**: Quick access features should be fast (cached queries, indexed database)

### Technical Considerations
- **Database Indexes**: Add indexes on frequently queried fields (`assigned_user_id`, `status`, `created_at`, `updated_at`)
- **Query Optimization**: Use eager loading to avoid N+1 queries
- **Caching**: Consider caching for aggregations (top assets, statistics)
- **Tracking**: For "Recent Events" feature, decide between session-based (simpler) or database tracking (persistent)

### Data Considerations
- **Privacy**: Personal preferences (pinned events) should be user-specific
- **Performance**: Aggregations (statistics, top assets) may need caching
- **History**: Recent events/views may need cleanup of old data
- **Status Tracking**: Part demand status updates may require audit log or `updated_at` field comparison

## HTMX Dashboard Widget Implementation

### Overview

Several prepared query features can be implemented as HTMX-powered dashboard widgets that load the top 5 events from the `/maintenance/view-events` portal. This approach:
- Reuses existing event portal infrastructure
- Provides consistent UI/UX
- Allows "View All" links to full filtered views
- Reduces code duplication

### Implementation Pattern

```html
<!-- Dashboard Card Example -->
<div class="card">
    <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="mb-0">Assigned Events</h5>
        <a href="/maintenance/view-events?assigned_user_id={current_user.id}" class="btn btn-sm btn-outline-primary">
            View All
        </a>
    </div>
    <div class="card-body" 
         hx-get="/maintenance/view-events?assigned_user_id={current_user.id}&per_page=5"
         hx-trigger="load"
         hx-target="this"
         hx-swap="innerHTML">
        <div class="text-center">
            <div class="spinner-border spinner-border-sm" role="status"></div>
            <span class="ms-2">Loading events...</span>
        </div>
    </div>
</div>
```

### Features Suitable for HTMX Implementation

| Feature | HTMX Ready | Requires New Filter | Notes |
|---------|------------|---------------------|-------|
| View Assigned Events | ✅ Yes | No | Uses existing `assigned_user_id` filter |
| View Recently Completed Events | ✅ Yes | No | Uses existing `status` and `order_by` filters |
| Assigned Events Planned This Week | ✅ Yes | No | Uses existing `status` and `date_from/date_to` filters |
| View Events with Comments from You | ⚠️ Partial | Yes | Needs `has_my_comments` filter |
| View Recent Events | ⚠️ Partial | Yes | Needs `recently_viewed` filter + tracking |

## Advanced Filters - Implementation Status

### Already Implemented Filters ✅

These filters are available in the `/maintenance/view-events` portal and can be used immediately:

1. **`assigned_user_id`** (int)
   - Filters events by assigned technician
   - Query: `MaintenanceActionSet.assigned_user_id == assigned_user_id`
   - Example: `?assigned_user_id=5`

2. **`status`** (str)
   - Filters by event status
   - Options: `['Planned', 'In Progress', 'Delayed', 'Complete']`
   - Query: `MaintenanceActionSet.status == status`
   - Example: `?status=Complete`

3. **`priority`** (str)
   - Filters by event priority
   - Options: `['Low', 'Medium', 'High', 'Critical']`
   - Query: `MaintenanceActionSet.priority == priority`
   - Example: `?priority=High`

4. **`asset_id`** (int)
   - Filters events by asset
   - Query: `MaintenanceActionSet.asset_id == asset_id`
   - Example: `?asset_id=123`

5. **`make_model_id`** (int)
   - Filters events by asset make/model
   - Query: Join with Asset, filter by `Asset.make_model_id == make_model_id`
   - Example: `?make_model_id=45`

6. **`major_location_id`** (int)
   - Filters events by major location
   - Query: Join with Event/Asset, filter by `major_location_id`
   - Example: `?major_location_id=10`

7. **`created_by_user_id`** (int)
   - Filters events by creator
   - Query: `MaintenanceActionSet.created_by_id == created_by_user_id`
   - Example: `?created_by_user_id=3`

8. **`action_title`** (str)
   - Filters events containing actions with matching title
   - Query: Join with Action, filter by `Action.action_name.ilike('%action_title%')`
   - Example: `?action_title=oil%20change`

9. **`date_from`** (date: YYYY-MM-DD)
   - Filters events created/updated after this date
   - Query: Filter by date range
   - Example: `?date_from=2024-01-01`

10. **`date_to`** (date: YYYY-MM-DD)
    - Filters events created/updated before this date
    - Query: Filter by date range
    - Example: `?date_to=2024-12-31`

11. **`search_term`** (str)
    - Full-text search across events
    - Query: Search in event descriptions, comments, etc.
    - Example: `?search=brake`

12. **`order_by`** (str)
    - Sort field
    - Options: `['created_at', 'updated_at', 'assigned_at', 'priority']`
    - Example: `?order_by=updated_at`

13. **`order_direction`** (str)
    - Sort direction
    - Options: `['asc', 'desc']`
    - Example: `?order_direction=desc`

14. **`per_page`** (int)
    - Number of items per page
    - Default: 20
    - Example: `?per_page=5` (for HTMX widgets)

### Filters Needing Implementation ❌

These filters need to be added to the event portal service:

1. **`has_my_comments`** (bool)
   - **Purpose**: Filter events where the current user has left comments
   - **Query Logic**: 
     ```python
     if has_my_comments:
         query = query.join(Event).join(Comment).filter(
             Comment.user_id == current_user_id
         ).distinct()
     ```
   - **Use Case**: "View Events with Comments from You" feature
   - **Complexity**: Medium (requires join with Comment table)
   - **Example**: `?has_my_comments=true`

2. **`last_comment_date`** (sort option)
   - **Purpose**: Sort events by most recent comment date
   - **Query Logic**: 
     ```python
     # Subquery for last comment date per event
     last_comment_subq = (
         select(
             Comment.event_id,
             func.max(Comment.created_at).label('last_comment_date')
         )
         .where(Comment.user_viewable.is_(None))
         .group_by(Comment.event_id)
         .subquery()
     )
     query = query.outerjoin(last_comment_subq).order_by(
         last_comment_subq.c.last_comment_date.desc()
     )
     ```
   - **Use Case**: Sort events by most recent comment activity
   - **Complexity**: Medium-High (requires subquery)
   - **Example**: `?order_by=last_comment_date&order_direction=desc`

3. **`recently_viewed`** (bool)
   - **Purpose**: Filter events recently viewed by the current user
   - **Query Logic**: 
     ```python
     if recently_viewed:
         # Requires EventView tracking table
         query = query.join(EventView).filter(
             EventView.user_id == current_user_id
         ).order_by(EventView.viewed_at.desc())
     ```
   - **Use Case**: "View Recent Events" feature
   - **Complexity**: High (requires new EventView table and tracking mechanism)
   - **Prerequisites**: 
     - Create `EventView` table with `user_id`, `event_id`, `viewed_at`
     - Implement view tracking (on event detail page load)
   - **Example**: `?recently_viewed=true`

4. **`completion_percentage`** (sort/filter option)
   - **Purpose**: Sort or filter by action completion percentage
   - **Query Logic**: 
     ```python
     # Calculate completion percentage in subquery
     completion_subq = (
         select(
             Action.maintenance_action_set_id,
             func.count(Action.id).label('total_actions'),
             func.sum(case((Action.status == 'Complete', 1), else_=0)).label('completed_actions')
         )
         .group_by(Action.maintenance_action_set_id)
         .subquery()
     )
     # Calculate percentage and filter/sort
     ```
   - **Use Case**: Sort by completion progress
   - **Complexity**: Medium-High (requires aggregation subquery)
   - **Example**: `?order_by=completion_percentage&order_direction=desc`

5. **`days_overdue`** (filter/sort option)
   - **Purpose**: Filter or sort events by days overdue
   - **Query Logic**: 
     ```python
     # Calculate days overdue based on due_date or created_at
     # Filter events where days_overdue > threshold
     ```
   - **Use Case**: Show overdue events first
   - **Complexity**: Medium (requires date calculation)
   - **Example**: `?days_overdue_min=7` or `?order_by=days_overdue`

### Filter Implementation Priority

1. **High Priority** (Needed for HTMX widgets):
   - `has_my_comments` - Enables "View Events with Comments from You" widget
   - `last_comment_date` - Enables sorting by comment activity

2. **Medium Priority** (Nice to have):
   - `completion_percentage` - Useful for progress tracking
   - `days_overdue` - Useful for prioritization

3. **Low Priority** (Requires infrastructure):
   - `recently_viewed` - Requires EventView table and tracking system

## Notes

- Features should be tested with actual technicians for usability
- Consider A/B testing for feature adoption
- Monitor usage analytics to prioritize future development
- Some features may require additional permissions or role-based access
- Consider impact on mobile data usage for field technicians
- Start with Low complexity features for quick wins, then move to Medium complexity
- HTMX widgets should gracefully handle loading states and errors
- Consider caching HTMX widget responses for performance

# Create & Assign Portal Design Document

## Overview

The Create & Assign Portal (`/maintenance/manager/create-assign`) is a manager-focused interface for creating maintenance events from templates and assigning them to assets and technicians. This portal streamlines the workflow of converting planned maintenance into actionable work assignments.

**Note**: Monitoring and viewing of maintenance events is handled by the separate View Maintenance portal (`/maintenance/manager/view-maintenance`). This portal focuses exclusively on creation and assignment workflows.

**Note**: The MaintenanceActionSet is the data structure that holds assignment information. The event `user_id` holds who created the event. Assignment should be done through the MaintenanceContext.

## Purpose

The portal enables managers to:
1. **Create maintenance events from templates** - Select a template and create a real maintenance event
2. **Assign to assets** - Link the maintenance event to a specific asset
3. **Assign to technicians** - Assign the work to a technician for execution

## Key Features

### Phase 1 (Current Focus)
- Create maintenance event from template
- Assign to asset (during creation)
- Assign to technician (during creation or after)
- Reassign existing events to different technicians
- View unassigned maintenance events
- Bulk assign unassigned events to the same technician


### Future Phases
- Create blank maintenance events (not in scope for Phase 1)
- **Bulk Operations**: Create multiple events from template for multiple assets (with option to assign all to same technician during creation)
- Advanced filtering and search for templates and assets
- Workload balancing visualization for technician assignment

## Architecture

### Route Structure

```
/maintenance/manager/create-assign
├── GET  /                              # Main portal page (create event form)
├── GET  /create                        # Create event from template form
├── POST /create                        # Submit event creation (redirects back to portal homepage)
├── GET  /unassigned                    # View unassigned maintenance events
└── POST /unassigned/bulk-assign        # Bulk assign unassigned events to technician

/maintenance/maintenance-event/<event_id>
├── POST /assign                        # Submit assignment (default redirect to view, from this portal override: refreshes page and opens view in new tab)
```

### Business Layer Components

#### MaintenanceFactory
**Location**: `app/buisness/maintenance/factories/maintenance_factory.py`

**Key Method**:
```python
MaintenanceFactory.create_from_template(
    template_action_set_id: int,
    asset_id: int,
    planned_start_datetime: Optional[datetime] = None,
    maintenance_plan_id: Optional[int] = None,
    user_id: Optional[int] = None,
    commit: bool = True
) -> MaintenanceActionSet
```

**Responsibilities**:
- Creates complete maintenance event from template
- Creates Event (ONE-TO-ONE relationship)
- Creates MaintenanceActionSet
- Creates all Actions from TemplateActionItems
- Creates PartDemand records (standalone copies)
- Creates ActionTool records (standalone copies)

#### MaintenanceContext
**Location**: `app/buisness/maintenance/base/maintenance_context.py`

**Key Methods**:
```python
# Assignment
maintenance_action_set.assigned_user_id = technician_id
maintenance_action_set.assigned_by_id = manager_id

# Status management
maintenance_context.start(user_id)
maintenance_context.complete(user_id, notes)
maintenance_context.cancel(user_id, notes)
```

**Responsibilities**:
- Wraps MaintenanceActionSetStruct (which wraps MaintenanceActionSet)
- Provides business logic for maintenance events
- Manages status transitions
- Syncs Event.status with MaintenanceActionSet.status
- Provides statistics (total_actions, completed_actions, completion_percentage)

#### TemplateMaintenanceContext
**Location**: `app/buisness/maintenance/templates/template_maintenance_context.py`

**Note**: This business layer context is used internally by the service layer. Routes should not call TemplateMaintenanceContext methods directly. Use `AssignMonitorService` methods instead.

**Responsibilities**:
- Wraps TemplateActionSetStruct (which wraps TemplateActionSet)
- Provides business logic for template operations
- Provides template summary information and statistics
- Used by service layer for template data access

## User Interface Components

### 1. Main Portal Page (`/maintenance/manager/create-assign`)

**Layout**: Single-page form focused on creating and assigning events

**Purpose**: Create new maintenance events from templates and assign them

**Components**:
- **Template Selection**
  - Dropdown or searchable list of active templates
  - Filter by: Asset type, Make/Model (if template has these filters)
  - Display: Template name, description, revision, estimated duration
  - Show template summary (number of actions, estimated cost)
  - Template preview card showing:
    - Task name and description
    - Number of actions
    - Estimated duration
    - Estimated cost
    - Required parts summary
    - Required tools summary
  
- **Asset Selection**
  - Searchable asset selector
  - Filter by: Asset type, Make/Model, Location
  - Display: Asset name, type, location, current status
  - Show recent maintenance history for selected asset
  - Asset preview card showing:
    - Asset name and type
    - Location
    - Make/Model
    - Recent maintenance history
    - Upcoming scheduled maintenance
  
- **Assignment Details**
  - **Technician Assignment** (optional at creation)
    - Dropdown of active technicians
    - Show current workload indicator for each technician
    - Can be assigned later if not selected during creation
  - **Planned Start Date/Time**
    - Date/time picker
    - Default: Current date/time
  - **Priority** (optional)
    - Dropdown: Low, Medium, High, Critical
    - Default: Medium
  - **Notes** (optional)
    - Text area for additional instructions

- **Create & Assign Button**
  - Validates: Template selected, Asset selected
  - Creates maintenance event via MaintenanceFactory
  - If technician assigned, sets assigned_user_id and assigned_by_id
  - Adds comment to event: "Created from template [template_name] and assigned to [technician] by [manager]"
  - Redirects back to portal homepage (`/maintenance/manager/create-assign`)

### 2. Create Event Form (`/maintenance/manager/create-assign/create`)

**Purpose**: Dedicated page for creating maintenance events

**Layout**: Multi-step form or single-page form

**Form Fields**:
1. **Step 1: Select Template**
   - Template search/filter
   - Template preview card showing:
     - Task name
     - Description
     - Number of actions
     - Estimated duration
     - Estimated cost
     - Required parts summary
     - Required tools summary

2. **Step 2: Select Asset**
   - Asset search/filter
   - Asset preview card showing:
     - Asset name and type
     - Location
     - Make/Model
     - Recent maintenance history
     - Upcoming scheduled maintenance

3. **Step 3: Assignment & Scheduling**
   - Technician assignment (optional)
   - Planned start date/time
   - Priority selection
   - Notes/instructions

4. **Step 4: Review & Create**
   - Summary of selections
   - Template details
   - Asset details
   - Assignment details
   - Create button

**Validation**:
- Template must be selected and active
- Asset must be selected
- Planned start date/time must be valid
- If technician assigned, technician must be active user

**Post-Creation Behavior**:
- After successful event creation, redirects back to portal homepage (`/maintenance/manager/create-assign`)
- Flashes success message with new event ID
- User can continue creating additional events from the main portal page


### 3. Assign Event Page (`/maintenance/maintenance-event/<event_id>/assign`)

**Purpose**: Assign or reassign maintenance event to technician

**Components**:
- **Event Information Card**
  - Task name and description
  - Asset information
  - Current status
  - Current assignment (if any)
  - Progress summary

- **Assignment Form**
  - **Technician Selection**
    - Dropdown of active technicians
    - Show current workload for each technician
    - Show technician skills/certifications (if applicable)
  - **Assignment Notes** (optional)
    - Text area for special instructions
  - **Planned Start Date/Time** (if not started)
    - Date/time picker
    - Can update planned start
  - **Priority** (if not started)
    - Can update priority

- **Assignment History**
  - Table of previous assignments
  - Columns: Technician, Assigned By, Assigned Date, Notes
  - Shows reassignment history

- **Actions**
  - Save Assignment button
  - Cancel button
  - View Full Event Details link

**Workflow**:
1. Manager selects technician
2. Optionally adds notes or updates planned start/priority
3. Clicks "Assign"
4. System updates:
   - `assigned_user_id` = selected technician
   - `assigned_by_id` = current manager
   - `planned_start_datetime` = updated if changed
   - `priority` = updated if changed
5. System adds comment to event: "Assigned to [technician] by [manager]"
6. **Post-assignment behavior**: Page refreshes (stays on assign page) AND opens new tab to view page (`/maintenance/maintenance-event/<event_id>/view`)
   - Implementation note: Use JavaScript `window.open()` after successful assignment to open view page in new tab

### 4. Unassigned Events Page (`/maintenance/manager/create-assign/unassigned`)

**Purpose**: View and bulk assign unassigned maintenance events

**Components**:
- **Unassigned Events List**
  - Table with columns:
    - Checkbox for selection
    - Event ID / Task Name
    - Asset (with link to asset detail)
    - Status
    - Planned Start Date/Time
    - Created Date
    - Priority
    - Actions (View Details, Assign Individually)
  - Filterable by:
    - Asset
    - Asset Type
    - Status
    - Priority
    - Date range (planned start)
  - Sortable by all columns
  - Pagination support
  - Select All / Deselect All checkbox

- **Bulk Assignment Section**
  - **Technician Selection**
    - Dropdown of active technicians
    - Show current workload for each technician (count of currently assigned maintenance action sets)
  - **Assignment Notes** (optional)
    - Text area for notes to apply to all selected events
  - **Bulk Assign Button**
    - Validates: At least one event selected, technician selected
    - Assigns all selected events to the chosen technician
    - Adds comment to each event: "Bulk assigned to [technician] by [manager]"
    - Shows success message with count of assigned events
    - Redirects back to unassigned events list (filtered to show remaining unassigned)

**Workflow**:
1. Manager views unassigned events list
2. Selects one or more events using checkboxes
3. Selects technician from dropdown
4. Optionally adds notes
5. Clicks "Bulk Assign"
6. System assigns all selected events to technician
7. System adds comment to each assigned event
8. Redirects to unassigned events list showing remaining unassigned events

## Data Flow

### Creating Maintenance Event from Template

```
User Action: Select template + asset + technician
    ↓
Route Handler: /create (POST)
    ↓
Service Layer: AssignMonitorService.create_event_from_template()
    ↓
Business Layer: MaintenanceFactory.create_from_template()
    ├── Creates Event (via Event.add_event())
    ├── Creates MaintenanceActionSet
    │   ├── Links to Event (event_id)
    │   ├── Links to Asset (asset_id)
    │   ├── Links to Template (template_action_set_id)
    │   ├── Sets status = 'Planned'
    │   ├── Sets planned_start_datetime
    │   └── Sets assigned_user_id, assigned_by_id (if manager provided)
    ├── Creates Actions from TemplateActionItems
    │   ├── Copies action details
    │   ├── Sets sequence_order from template
    │   └── Links to MaintenanceActionSet
    ├── Creates PartDemand records (standalone copies)
    └── Creates ActionTool records (standalone copies)
    ↓
MaintenanceContext: Wraps created MaintenanceActionSet
    ↓
Response: Redirect back to portal homepage (/maintenance/manager/create-assign) with flash success message including new event ID
```

### Assigning Event to Technician

```
User Action: Select technician + submit assignment
    ↓
Route Handler: /maintenance/maintenance-event/<event_id>/assign (POST)
    ↓
Service Layer: AssignMonitorService.assign_event()
    ↓
Business Layer: MaintenanceContext
    ├── Updates maintenance_action_set.assigned_user_id
    ├── Updates maintenance_action_set.assigned_by_id
    ├── Updates planned_start_datetime (if changed)
    ├── Updates priority (if changed)
    └── Adds comment via event_context.add_comment()
    ↓
Response: Refresh current page (stay on assign page) + JavaScript opens new tab to view page
    - Implementation: Use window.open('/maintenance/maintenance-event/<event_id>/view', '_blank')
```

### Bulk Assigning Unassigned Events

```
User Action: Select multiple events + technician + submit bulk assignment
    ↓
Route Handler: /unassigned/bulk-assign (POST)
    ↓
Service Layer: AssignMonitorService.bulk_assign_events()
    ↓
For each event_id:
    Business Layer: MaintenanceContext
        ├── Updates maintenance_action_set.assigned_user_id
        ├── Updates maintenance_action_set.assigned_by_id
        └── Adds comment via event_context.add_comment()
    ↓
Service Layer: Collects results (success_count, failed_count, failed_event_ids)
    ↓
Response: Redirect to unassigned events list with success/failure message
```

### Bulk Creating Events from Template (Future Phase)

```
User Action: Select template + multiple assets + technician (optional) + submit
    ↓
Route Handler: /create/bulk (POST)
    ↓
Service Layer: AssignMonitorService.bulk_create_events_from_template()
    ↓
For each asset_id:
    Business Layer: MaintenanceFactory.create_from_template()
        ├── Creates Event
        ├── Creates MaintenanceActionSet
        │   └── Sets assigned_user_id, assigned_by_id (if manager provided)
        ├── Creates Actions
        ├── Creates PartDemand records
        └── Creates ActionTool records
    ↓
Service Layer: Collects results (success_count, failed_count, created_event_ids)
    ↓
Response: Redirect to success page showing created events with assignment status
```

## Service Layer

### AssignMonitorService
**Location**: `app/services/maintenance/assign_monitor_service.py`

**Note**: Service methods are defined conceptually. Implementation details will be developed during the build phase.

**Key Methods**:

- **`get_active_templates()`** - Retrieves active templates for selection, with optional filtering by asset type, make/model, and search terms. Returns formatted template data for presentation layer.

- **`get_template_summary(template_id)`** - Gets detailed summary of a specific template including actions, parts, and tools for preview purposes.

- **`get_available_assets()`** - Retrieves assets available for assignment with optional filtering by asset type, make/model, location, and search terms. Includes recent maintenance history.

- **`get_available_technicians()`** - Gets list of active technicians with current workload information for assignment selection.

- **`create_event_from_template()`** - Creates a maintenance event from a template, linking it to an asset and optionally assigning to a technician. Uses MaintenanceFactory internally.

- **`assign_event()`** - Assigns or reassigns a maintenance event to a technician. Updates MaintenanceActionSet and adds comment to Event.

- **`get_unassigned_events()`** - Retrieves maintenance events where assigned_user_id is None, with filtering options. Returns formatted event data for display.

- **`bulk_assign_events()`** - Assigns multiple events to the same technician in a single operation. Returns success/failure counts and failed event IDs.

- **`get_event_summary(event_id)`** - Gets comprehensive summary of a maintenance event including details, asset info, assignment status, actions, parts, and comments.

## Route Handlers

### Routes
**Location**: `app/presentation/routes/maintenance/manager/create_assign.py`

**Note**: Implementation details will be developed during the build phase. Routes are defined conceptually here.

```python
@manager_bp.route('/create-assign')
@login_required
def create_assign():
    """
    Main create & assign portal page.
    Displays create event form with template selection, asset selection, and assignment options.
    """
    # Implementation: Get templates and technicians via service layer, render form
    pass

@manager_bp.route('/create-assign/create', methods=['GET', 'POST'])
@login_required
def create_event():
    """
    Create maintenance event from template.
    GET: Show creation form
    POST: Process creation and redirect back to portal homepage
    """
    # Implementation: Validate form, create event via service, redirect back to portal homepage with flash message
    pass

@manager_bp.route('/create-assign/unassigned')
@login_required
def unassigned_events():
    """
    View unassigned maintenance events with filtering options.
    Displays list of events where assigned_user_id is None.
    """
    # Implementation: Get unassigned events via service, apply filters, render list
    pass

@manager_bp.route('/create-assign/unassigned/bulk-assign', methods=['POST'])
@login_required
def bulk_assign_events():
    """
    Bulk assign multiple unassigned events to a technician.
    Processes selected events and assigns them all to the chosen technician.
    """
    # Implementation: Validate selection, bulk assign via service, show results
    pass

# Note: Single assignment routes are located in maintenance_event routes
# Route: /maintenance/maintenance-event/<event_id>/assign
# Implementation: Get event context, validate assignment, update via service
# After successful POST: Refresh current page and use JavaScript window.open() to open view page in new tab
```

## Templates

### assign_monitor.html
**Location**: `app/presentation/templates/maintenance/manager/assign_monitor.html`

**Structure**:
- Header with page title "Create & Assign Maintenance"
- Single-page create event form
- Template selection section
- Asset selection section
- Assignment and scheduling section
- Uses Bootstrap components
- HTMX for dynamic updates (optional, for template/asset previews)

### create_event.html
**Location**: `app/presentation/templates/maintenance/manager/create_event.html`

**Structure**:
- Multi-step form or single-page form
- Template selection with preview
- Asset selection with preview
- Assignment and scheduling fields
- Review and create step

### assign_event.html
**Location**: `app/presentation/templates/maintenance/maintenance_event/assign.html`

**Structure**:
- Event information card
- Assignment form
- Assignment history table
- Action buttons
- JavaScript to handle post-assignment: refresh page and open view in new tab

**Note**: This template is part of the maintenance event routes, not the assign-monitor portal routes.

## Business Rules

### Event Creation
1. **Template must be active** - Only active templates can be used to create events
2. **Asset must exist** - Asset must be valid and accessible
3. **One MaintenanceActionSet per Event** - Each event has exactly one MaintenanceActionSet
4. **Template reference preserved** - `template_action_set_id` links to the template revision used
5. **Initial status** - New events start with status 'Planned'
6. **Event creation** - Event is created automatically via factory class

### Assignment
1. **Technician must be active** - Only active users can be assigned
2. **Assignment tracking** - `assigned_user_id` and `assigned_by_id` are set
3. **Assignment comment** - System automatically adds comment to event
4. **Reassignment allowed** - Events can be reassigned to different technicians
5. **Assignment history** - Previous assignments are preserved by MaintenanceContext (via comments)

### Status Management
1. **Status sync** - `MaintenanceActionSet.status` syncs with `Event.status`
2. **Status transitions** - Managed by `MaintenanceContext` methods
3. **Planned status** - New events start as 'Planned'
4. **In Progress** - Changed when technician starts work
5. **Delayed** - Set when delays are added
6. **Complete** - Set when all actions are complete

## Integration Points

### With Template System
- Uses `AssignMonitorService.get_active_templates()` to query active templates (service layer)
- Service layer uses `TemplateMaintenanceContext` internally for business logic
- References template via `template_action_set_id` in MaintenanceActionSet

### With Event System
- MaintenanceFactory handles event creation
- Uses `MaintenanceContext` for comments
- `MaintenanceContext` syncs status between MaintenanceActionSet and Event

### With Asset System
- Links maintenance to assets via `asset_id`
- Displays asset information in UI
- Shows asset maintenance history

### With User System
- Uses `MaintenanceContext` for technician assignment
- Tracks assignment via `assigned_user_id` and `assigned_by_id` in MaintenanceActionSet


### With View Maintenance Portal
- Redirects to View Maintenance portal (`/maintenance/manager/view-maintenance`) for viewing created events
- View Maintenance portal handles all monitoring, filtering, and viewing of maintenance events
- This portal focuses exclusively on creation and assignment workflows

## Future Enhancements

### Phase 2
- **Bulk Operations**: Create multiple events from template for multiple assets, with option to assign all created events to the same technician during the creation process

### Phase 3
- **Advanced Filtering**: More filter options for templates, assets, and events
- **Template Recommendations**: Suggest templates based on asset type/model

### Phase 4
- **Workload Balancing**: Visualize technician workload and suggest assignments
- **Blank Event Creation**: Create maintenance events without templates


## Related Documents

- `MaintenancePortalImplementationPlan.md` - Overall maintenance portal architecture (includes View Maintenance portal details)
- `MaintnenceModel.md` - Data model and business layer structure
- `TemplateBuilderDesign.md` - Template creation system
- `SystemDesign.md` - Overall system architecture

## Notes

- **Monitoring is handled separately**: The View Maintenance portal (`/maintenance/manager/view-maintenance`) handles all viewing, filtering, and monitoring of maintenance events. This portal focuses exclusively on the creation and assignment workflows.
- **Route naming**: The route will change from  `/assign-monitor` to `/create-assign`


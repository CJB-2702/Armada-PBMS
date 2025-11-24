Notes to change this doc from dev
**Assigned user and assigned by columns need to be added to datamodel for both actions and action sets**
maintnence delays need to be incorperated into this design document
datamodel Part demand and maintnence delays need priority statuses
datamodel part demand needs five new columns requested_by "maintnence approval by" and "maintnence approval date"  and "supply approval by" and "supply approval date"

Explicitly clarify that 
template maintnence events have a set of template action set rows which link the template maintence set to template actions
 a template maintnence set is a set of refrences to template actions
 a regular maintnence set has actions directly linked to the event header

document start
# Maintenance Portal Implementation Plan

## Overview

This document outlines the implementation plan for redesigning the maintenance section of the Asset Management System to serve three distinct user types with role-specific workflows and interfaces:

1. **Technicians**: Focus on completing assigned work efficiently
2. **Managers**: Focus on planning, scheduling, and assigning maintenance work
3. **Leaders/Admin**: Focus on fleet-wide oversight and system administration

Each portal will have its own optimized interface, workflows, and feature set tailored to the specific needs of that user role.

## Portal Architecture

### Portal Access Control

Portals are accessed based on user roles:
- **Technician Role**: Access to Technician Portal
- **Manager Role**: Access to Manager Portal (may also access Technician Portal)
- **Leader/Admin Role**: Access to Leader/Admin Portal (may also access Manager and Technician Portals)

Portal routes:
- `/maintenance/` - Splash page, simple links to other portal home pages
- `/maintenance/technician/*` - Technician Portal
- `/maintenance/manager/*` - Manager Portal
- `/maintenance/fleet/*` - Leader/Admin Portal

### Shared Components

All portals share:
- Core data models (MaintenanceEvent, MaintenanceActionSet, Action, PartDemand, MaintenanceDelay, etc.)
- Business layer context managers and factories
- Event system (comments, attachments)
- Asset and location data
- User authentication and authorization

## Data Model Requirements

### Required Data Model Changes

The following changes are required to the data model to fully support the portal system:

#### 1. Assignment Tracking (Actions and Action Sets)

**Action Model** (`app/data/maintenance/base/action.py`):
- Add `assigned_user_id` column (Integer, ForeignKey('users.id'), nullable=True)
- Add `assigned_by_id` column (Integer, ForeignKey('users.id'), nullable=True)
- Add relationships:
  - `assigned_user` → relationship('User', foreign_keys=[assigned_user_id])
  - `assigned_by` → relationship('User', foreign_keys=[assigned_by_id])

**MaintenanceActionSet Model** (`app/data/maintenance/base/maintenance_action_set.py`):
- Add `assigned_user_id` column (Integer, ForeignKey('users.id'), nullable=True)
- Add `assigned_by_id` column (Integer, ForeignKey('users.id'), nullable=True)
- Add relationships:
  - `assigned_user` → relationship('User', foreign_keys=[assigned_user_id])
  - `assigned_by` → relationship('User', foreign_keys=[assigned_by_id])

**Use Cases**:
- Managers assign maintenance work to technicians
- Track who assigned work and when
- Filter work by assigned technician
- Display assignment history

#### 2. Priority Statuses

**PartDemand Model** (`app/data/maintenance/base/part_demand.py`):
- Add `priority` column (String(20), nullable=False, default='Medium')
  - Values: 'Low', 'Medium', 'High', 'Critical'
  - Used for prioritizing part approval workflows

**MaintenanceDelay Model** (`app/data/maintenance/base/maintenance_delays.py`):
- Add `priority` column (String(20), nullable=False, default='Medium')
  - Values: 'Low', 'Medium', 'High', 'Critical'
  - Used for prioritizing delay resolution and reporting

**Use Cases**:
- Managers prioritize part demands for approval
- Technicians can request high-priority parts
- Track high-priority delays requiring immediate attention
- Analytics and reporting by priority level

#### 3. Part Demand Approval Workflow

**PartDemand Model** (`app/data/maintenance/base/part_demand.py`):
- Add `requested_by_id` column (Integer, ForeignKey('users.id'), nullable=True)
  - Tracks which technician requested the part
- Add `maintenance_approval_by_id` column (Integer, ForeignKey('users.id'), nullable=True)
  - Tracks which manager approved the part request
- Add `maintenance_approval_date` column (DateTime, nullable=True)
  - When the maintenance manager approved the request
- Add `supply_approval_by_id` column (Integer, ForeignKey('users.id'), nullable=True)
  - Tracks which supply/inventory manager approved the purchase
- Add `supply_approval_date` column (DateTime, nullable=True)
  - When the supply manager approved the purchase

**Relationships**:
- `requested_by` → relationship('User', foreign_keys=[requested_by_id])
- `maintenance_approval_by` → relationship('User', foreign_keys=[maintenance_approval_by_id])
- `supply_approval_by` → relationship('User', foreign_keys=[supply_approval_by_id])

**Approval Workflow States**:
1. **Requested**: Technician requests part (`requested_by_id` set)
2. **Maintenance Approved**: Manager approves (`maintenance_approval_by_id` and `maintenance_approval_date` set)
3. **Supply Approved**: Supply manager approves (`supply_approval_by_id` and `supply_approval_date` set)
4. **Ordered**: Part added to purchase order
5. **Received**: Part received in inventory
6. **Used**: Part used in maintenance

**Use Cases**:
- Two-tier approval process (maintenance manager → supply manager)
- Audit trail of who approved what and when
- Filter pending approvals by approver
- Track approval timelines for analytics

### Data Model Structure Clarifications

#### Template Maintenance Events Structure

**Template Maintenance Event Hierarchy**:
```
TemplateMaintenanceEvent (wrapper class)
└── TemplateActions (template maintenance sets)
    └── ProtoActionItems (template actions)
        ├── TemplatePartDemands (template part requirements)
        └── TemplateActionTools (template tool requirements)
```

**Key Points**:
- **Template Maintenance Events** (`TemplateMaintenanceEvent`) have a set of **TemplateActions** rows
- A **TemplateActions** links the template maintenance event to **ProtoActionItems ** (template actions)
- A **TemplateActions** is a set of references to **ProtoActionItems ** (not direct actions, but templates)
- A **TemplateActions** row should copy the information from the **ProtoActionItems ** row its refrencing
- **TemplateActions** rows are ordered by `sequence_order` within the TemplateActions
- **ProtoActionItems ** do not have order

#### Regular Maintenance Events Structure

**Regular Maintenance Event Hierarchy**:
```
MaintenanceActionSet (maintenance event header - extends EventDetailVirtual)
└── Actions (directly linked to the maintenance event header)
    └── PartDemands (linked to actions)
```

**Key Points**:
- A regular **MaintenanceActionSet** has **Actions** directly linked to the event header via `maintenance_action_set_id` foreign key and a row 
- Actions are NOT linked through an intermediate table - they are directly linked to the MaintenanceActionSet
- Each Action can have multiple PartDemands
- Actions are ordered by `sequence_order` within the MaintenanceActionSet

**Comparison**:
- **Templates**: TemplateActions → ProtoActionItems (template references, reusable)
- **Regular Maintenance**: MaintenanceActionSet → Actions (actual work instances, asset-specific)

### Maintenance Delays Integration

**MaintenanceDelay Model** (`app/data/maintenance/base/maintenance_delays.py`):
- Linked to MaintenanceActionSet via `maintenance_action_set_id`
- Tracks delay information: type, reason, dates, billable hours
- Supports multiple delays per maintenance action set
- Priority status (as noted above)

**Use Cases**:
- Track why maintenance was delayed (parts, weather, other work, etc.)
- Calculate delay costs (billable hours)
- Analytics on common delay reasons
- Technician and Manager portals display active delays
- Admin portal shows delay statistics and trends

**Portal Integration**:
- **Technician Portal**: View delays affecting assigned work, add delay notes
- **Manager Portal**: Approve delays, review delay reasons, prioritize delayed work
- **Admin Portal**: Delay analytics, common delay patterns, cost analysis

## Technician Portal

### Goal
Provide a workflow-focused interface that allows technicians to efficiently view, complete, and record maintenance work.

### Key Features

#### 1. Dashboard View (`/maintenance/technician/`)
**Purpose**: Central hub showing technician's work queue and priorities

**Components**:
- **My Assigned Work** - List of action sets/actions assigned to the technician
  - Filterable by: Status (Pending, In Progress,Delayed, Completed), Priority, Due Date
  - Grouped by: Maintenance Event, Asset
  - Quick actions: Start, View Details
- **Available Work** list of action sets not complete at current location. should generally mirror My Assigned Work Portal
- **Schedule** - Calendar view of assigned work orderable by initially created or last event update / comment time
- **Overdue Items** - Alert banner showing overdue assignments
- **Quick Stats** - Number of assigned items, completed today, completion rate

**Data Requirements**:
- Actions assigned to current user
- Maintnence Action Sets assigned to current user
- Maintenance events linked to those actions
- Asset information for context
- Action completion status and timestamps

#### 2. Work Detail View (`/maintenance/technician/work/<action_set_id>`)
**Purpose**: Comprehensive view of a maintenance action set with all actions and related information
use /maintenance/do_maintenance/<Action_set_id> as refrence

**Components**:
- **Action Set Header**
  - Asset information
  - Maintenance event details
  - Due date and status
  - Assigned technician(s)

- **Actions List**
  - All actions in the set
  - Status indicators (Not Started, In Progress, Complete)
  - Action descriptions and requirements
  - Tools required
  - Parts required
  - Completion checkboxes/buttons
  
- **Parts Needed Section**
  - List of part demands
  - Request parts button (if not already requested)
  - View part request status
- **Comments and Attachments**
  - Add comments
  - Upload attachments
  - View history
- **Delay history**
 - Add delays
 - View Delays
- **Complete Action Set** - Button to mark entire set as complete


**Workflow**:
1. Technician views assigned action set
2. Technician updates action status as work progresses
3. Technician adds comments/attachments as needed
4. Technician requests parts if needed
5. Technician marks actions as complete
6. Technician adds maintnence delay which updates status and comments if blocked
7. Technician marks action set as complete when all actions done

#### 3. Action Detail View (`/maintenance/technician/action/<action_id>`)
**Purpose**: Detailed view of a single action for completion

**Components**:
- Action description and requirements
- Related asset information
- Status update controls
- Parts and tools needed
- Comments and attachments specific to this action
- Complete action button
- Navigation to parent action set

#### 4. Part Request (`/maintenance/technician/parts/request`)
**Purpose**: Interface for requesting parts needed for maintenance

**Components**:
- List of parts required for current action set
- Quantity input
- Location/storage preference
- Priority/urgency selector
- Submit request button
- View existing requests status

#### 5. My Maintenance History (`/maintenance/technician/history`)
**Purpose**: View completed maintenance work

**Components**:
- List of completed action sets (paginated)
- Filterable by: Date range, Asset, Maintenance type, Status
- Search functionality
- View details of past work
- Export history (if needed)

#### 6. Maintenance Delays (`/maintenance/technician/delays`)
**Purpose**: View and manage delays affecting assigned work

**Components**:
- **Active Delays** - List of delays affecting assigned work
  - Delay type and reason
  - Start and end dates
  - Billable hours
  - Priority status
- **Add Delay** - Form to record new delays
  - Delay type selection
  - Reason text field
  - Billable hours (if applicable)
  - Priority selection
- **Resolve Delay** - Mark delay as resolved
  - End date selection
  - Update billable hours
- **Delay History** - View all delays for assigned work

### Technical Implementation

#### Routes
```python
# app/presentation/routes/maintenance/technician/__init__.py
technician_bp = Blueprint('technician_portal', __name__, url_prefix='/maintenance/technician')

@technician_bp.route('/')
@technician_bp.route('/dashboard')
def dashboard():
    """Technician dashboard with assigned work"""

@technician_bp.route('/work/<int:action_set_id>')
def work_detail(action_set_id):
    """Detail view of assigned action set"""

@technician_bp.route('/action/<int:action_id>')
def action_detail(action_id):
    """Detail view of single action"""

@technician_bp.route('/action/<int:action_id>/complete', methods=['POST'])
def complete_action(action_id):
    """Mark action as complete"""

@technician_bp.route('/action-set/<int:action_set_id>/complete', methods=['POST'])
def complete_action_set(action_set_id):
    """Mark action set as complete"""

@technician_bp.route('/parts/request', methods=['GET', 'POST'])
def request_parts():
    """Request parts for maintenance"""

@technician_bp.route('/history')
def history():
    """View completed maintenance history"""
```

#### Services
```python
# app/services/maintenance/technician_service.py
class TechnicianService:
    @staticmethod
    def get_assigned_work(user_id, filters=None):
        """Get all action sets assigned to technician"""
    
    @staticmethod
    def get_action_set_detail(action_set_id, user_id):
        """Get detailed action set information"""
    
    @staticmethod
    def update_action_status(action_id, status, user_id):
        """Update action completion status"""
    
    @staticmethod
    def get_parts_for_action_set(action_set_id):
        """Get required parts for action set"""
    
    @staticmethod
    def get_completion_history(user_id, filters=None):
        """Get completed maintenance history"""
```

### User Workflows

#### Workflow 1: Complete Assigned Maintenance
1. Technician logs in → Redirected to Technician Dashboard
2. Views assigned work → Clicks on action set
3. Reviews actions and asset details → Starts work
4. Updates action status as work progresses → Adds comments/attachments
5. Completes all actions → Marks action set complete
6. System updates maintenance event status

#### Workflow 2: Request Parts
1. Technician working on action set → Needs additional part
2. Clicks "Request Parts" → Modal popup quick search bar shows 16 parts or has option to go to parts lookup page
3. Selects part → Enters quantity and urgency
4. Submits request → Request sent to manager for approval
5. Can view request status → Parts approved/rejected

## Manager Portal

### Goal
Provide a planning and oversight interface for managers to create maintenance templates, schedules, assign work, and monitor progress.

### Key Features

#### 1. Dashboard View (`/maintenance/manager/`)
**Purpose**: Overview of maintenance operations requiring manager attention

**Components**:
- **Assets Due for Maintenance** - List of assets with maintenance due based on schedules
  - Filterable by: Asset type, Location, Due date range
  - Grouped by: Maintenance plan, Asset type
  - Quick actions: Create maintenance event, View schedule
- **Active Maintenance** - List of in-progress maintenance events
  - Filterable by: Technician, Asset, Status, Start date
  - Progress indicators
  - Quick actions: View details, Reassign, Add delay
- **Part Demands Pending Approval** - List of part requests requiring approval
  - Filterable by: Technician, Asset, Priority, Request date
  - Quick actions: Approve, Reject, View details
- **Onsite Events** - Recent events at locations
  - Filterable by: Location, Event type, Date range
  - Real-time updates
- **Quick Stats** - Maintenance KPIs (completion rate, overdue count, etc.)

#### 2. Template Management (`/maintenance/manager/templates/`)
**Purpose**: Create and manage maintenance templates (maintnence event,action sets, actions, part demands)
Show a graphic explaining that 
a template maintnence event is a set of refrences to template action items and that warn that template part demand can only be associated with a maintnence event if items are linked correctly, have a details summary that explains the process

**Sections**:
##### 2.0 Template Maintnence Event (`/maintenance/manager/templates/maintnence-event`)
 - list of template maintnence events
 - create edit and delete template events
 - select template actions and create action set rows that link the template action to the template maintnence event


##### 2.1 Action Set Templates (`/maintenance/manager/templates/action-sets`)
- List of template action sets
    - add warnings to action set template rows that do not have template action items
- Create/Edit/Delete
    - force to associate action set template item to template maintnence event
    - Search and associate action template item
        - Copy information from action template item 
        - hevily suggest and warn that should be linked to an action template item to copy information from

- Template details: copy of its refrence Template action item  Name, description, estimated duration with the option to add notes and make minor changes

##### 2.2 Action Templates (`/maintenance/manager/templates/actions`)
- List of template actions
- Create actions
- Edit/Delete Warn users that this is the protoype for other action sets and these should not be changed
    - block if any template action sets have refrences to this action
- Action details: Description, sequence order, estimated time
- Link to part demands and tools
- Attachments (manuals, procedures)

##### 2.3 Part Demand Templates (`/maintenance/manager/templates/part-demands`)
- List of template part demands
- Create/Edit/Delete part demands
- Link parts to actions
- Quantity specifications

**Workflow**: Managers create reusable templates that are used when creating maintenance plans or individual maintenance events.

#### 3. Maintenance Plans (`/maintenance/manager/plans/`)
**Purpose**: Create and manage maintenance plans that generate scheduled maintenance events

**Components**:
- **Plan List** - All maintenance plans
  - Filterable by: Asset type, Model, Status, Frequency
  - Create/Edit/Delete plans
- **Plan Detail** - Full plan configuration
  - Asset selection criteria
  - Template action sets to use
  - Frequency and scheduling rules
  - Next due dates calculation
  - Plan activation/deactivation

**Workflow**:
1. Manager creates maintenance plan
2. Selects asset type/model criteria
3. Selects template action sets to include
4. Sets frequency (time-based, mileage-based, etc.)
5. System calculates next due dates for matching assets
    - system performs check every day at 5 am
    - Manager has button to manually have the system start a check
6. Plan generates maintenance events when due


#### 4. Assets Due for Maintenance (`/maintenance/manager/assets-due/`)
**Purpose**: View and manage assets that have maintenance due based on plans

**Components**:
- **Due Assets List** - Assets with maintenance due
  - Sortable columns: Asset name, Type, Location, Due date, Overdue days
  - Filterable by: Asset type, Location, Due date range, Overdue status
  - Bulk actions: Create events for selected assets
- **Asset Detail** - Full asset information
  - Maintenance Event history
  - Upcoming maintenance schedule
  - Create maintenance event button

**Workflow**:
1. Manager views assets due for maintenance
2. Reviews asset details and maintenance history
3. Creates maintenance event for asset
4. System uses plan templates to populate event

#### 5. Maintenance Event Assignment (`/maintenance/manager/events/<event_id>/assign`)
**Purpose**: Assign maintenance events to technicians

**Components**:
- Maintenance event details
- Available technicians list (with current workload)
- Assignment form: Select technician(s), Set due date, Add notes
- Assignment history
- Reassignment capability

#### 6. Active Maintenance Monitoring (`/maintenance/manager/active/`)
**Purpose**: View and manage in-progress maintenance

**Components**:
- **Active Events List** - All maintenance events in progress
  - Filterable by: Technician, Asset, Status, Start date
  - Progress indicators
  - Status: Not Started, In Progress, Delayed, Complete
- **Event Detail** - Full event information
  - Action set progress
  - Technician assignment
  - Comments and updates
  - Delays and issues
  - Reassignment option

#### 7. Part Demand Approval (`/maintenance/manager/part-demands/`)
**Purpose**: Approve or reject part requests from technicians

**Components**:
- **Pending Requests List** - All part demands awaiting approval
  - Sortable by: Priority, Request date, Technician, Asset
  - Request details: Part, Quantity, Urgency, Reason
  - Requested by technician (`requested_by_id`)
  - Inventory availability check
  - Maintenance approval status (first tier)
- **Request Detail** - Full request information
  - Part information and inventory levels
  - Requesting technician (`requested_by`) and asset
  - Maintenance approval section:
    - Approve/Reject button
    - Set `maintenance_approval_by_id` and `maintenance_approval_date` on approval
    - Add approval notes
  - Supply approval status (second tier - handled by inventory system)
  - View approval history (`maintenance_approval_by`, `maintenance_approval_date`, `supply_approval_by`, `supply_approval_date`)

**Approval Workflow**:
1. Technician requests part → `requested_by_id` set, status = 'Requested'
2. Manager approves → `maintenance_approval_by_id` and `maintenance_approval_date` set, status = 'Maintenance Approved'
3. Supply manager approves → `supply_approval_by_id` and `supply_approval_date` set (handled by inventory system), status = 'Supply Approved'
4. Part ordered → status = 'Ordered'
5. Part received → status = 'Received'
6. Part used → status = 'Used'

#### 8. Maintenance Delays (`/maintenance/manager/delays`)
**Purpose**: View and manage maintenance delays

**Components**:
- **Active Delays List** - All active delays
  - Filterable by: Priority, Delay type, Asset, Technician, Date range
  - Sortable by: Priority, Start date, Duration
  - Delay details: Type, Reason, Dates, Billable hours, Priority
- **Delay Detail** - Full delay information
  - Related maintenance action set and asset
  - Technician who reported delay
  - Approve delay resolution
  - Update priority
  - Add notes
- **Delay Analytics** - Common delay reasons, cost analysis

**Workflow**:
1. Manager views pending part demands
2. Reviews request details and inventory
3. Approves or rejects request
4. If approved, inventory system is updated
5. Technician is notified

#### 8. Onsite Events (`/maintenance/manager/events/onsite`)
**Purpose**: View and filter events occurring at locations

**Components**:
- **Events List** - Filterable event feed
  - Filterable by: Location, Event type, Date range, Technician
  - Real-time updates
  - Event details popup
- **Event Detail** - Full event information
  - Event type and description
  - Asset and location
  - Technician and timestamps
  - Comments and attachments

### Technical Implementation

#### Routes
```python
# app/presentation/routes/maintenance/manager/__init__.py
manager_bp = Blueprint('manager_portal', __name__, url_prefix='/maintenance/manager')

@manager_bp.route('/')
@manager_bp.route('/dashboard')
def dashboard():
    """Manager dashboard"""

@manager_bp.route('/templates/action-sets')
def template_actions():
    """Manage action set templates"""

@manager_bp.route('/templates/actions')
def template_actions():
    """Manage action templates"""

@manager_bp.route('/templates/part-demands')
def template_part_demands():
    """Manage part demand templates"""

@manager_bp.route('/plans')
def maintenance_plans():
    """Manage maintenance plans"""

@manager_bp.route('/assets-due')
def assets_due():
    """View assets due for maintenance"""

@manager_bp.route('/events/<int:event_id>/assign', methods=['GET', 'POST'])
def assign_event(event_id):
    """Assign maintenance event to technician"""

@manager_bp.route('/active')
def active_maintenance():
    """View active maintenance"""

@manager_bp.route('/part-demands')
def part_demands():
    """Approve part demands"""

@manager_bp.route('/events/onsite')
def onsite_events():
    """View onsite events"""
```

#### Services
```python
# app/services/maintenance/manager_service.py
class ManagerService:
    @staticmethod
    def get_assets_due_for_maintenance(filters=None):
        """Get assets with maintenance due"""
    
    @staticmethod
    def get_active_maintenance(filters=None):
        """Get active maintenance events"""
    
    @staticmethod
    def get_pending_part_demands():
        """Get part demands pending approval"""
    
    @staticmethod
    def get_onsite_events(filters=None):
        """Get onsite events"""
    
    @staticmethod
    def create_maintenance_event_from_plan(plan_id, asset_id):
        """Create maintenance event from plan"""
    
    @staticmethod
    def assign_event_to_technician(event_id, technician_id, due_date):
        """Assign maintenance event to technician"""
    
    @staticmethod
    def approve_part_demand(demand_id, approved_by_id):
        """Approve part demand (maintenance approval tier)"""
    
    @staticmethod
    def get_active_delays(filters=None):
        """Get active maintenance delays"""
    
    @staticmethod
    def get_delay_analytics(filters=None):
        """Get delay analytics and statistics"""
    
    @staticmethod
    def approve_delay_resolution(delay_id, approved_by_id):
        """Approve delay resolution"""
```

### User Workflows

#### Workflow 1: Create Maintenance Plan
1. Manager navigates to Maintenance Plans
2. Creates new plan → Selects asset type/model criteria
3. Selects template action set rows → Configures frequency
4. Saves plan → System calculates due dates for matching assets
5. Plan appears in Assets Due when maintenance is due

#### Workflow 2: Assign Maintenance to Technician
1. Manager views assets due for maintenance
2. Selects asset → Creates maintenance event
3. System populates event from plan templates
4. Manager assigns to technician → Sets due date
5. Technician receives notification and assignment appears in their portal

#### Workflow 3: Approve Part Demand
1. Technician requests parts → Manager sees in pending part demands
2. Manager reviews request → Checks inventory availability
3. Manager approves or rejects → Adds notes if needed
4. Supply approves or rejects -> inventory updated and technician notified
    manager can also approve on behalf of supply in this portal

## Leader/Admin Portal

### Goal
Provide a comprehensive fleet-wide dashboard and administration interface for viewing, filtering, editing, and managing all maintenance operations and data.

### Key Features

#### 1. Fleet Maintenance Dashboard (`/maintenance/admin/dashboard`)
**Purpose**: High-level overview of fleet maintenance status

**Components**:
- **Fleet Health Overview**
  - Total assets count
  - Assets due for maintenance count
  - Overdue maintenance count
  - Active maintenance count
  - Completion rate (weekly/monthly)
  - Average maintenance duration
- **KPIs and Metrics**
  - Maintenance cost trends
  - Technician productivity metrics
  - Asset reliability metrics
  - Part demand trends
  - Schedule adherence rate
- **Alert Dashboard**
  - Critical maintenance overdue
  - High-priority part demands
  - Maintenance delays
  - System issues
- **Recent Activity Feed**
  - Latest maintenance completions
  - New maintenance events created
  - Part demand approvals
  - System changes

#### 2. Fleet Maintenance Table (`/maintenance/admin/fleet`)
**Purpose**: Comprehensive table view of all maintenance data with filtering and editing

**Data Views** (Tabs or Filters):
- **Maintenance Events** - All maintenance events
- **Action Sets** - All action sets
- **Actions** - All individual actions
- **Maintenance Plans** - All maintenance plans
- **Templates** - All templates
- **Part Demands** - All part demands

**Table Features**:
- **Advanced Filtering**
  - Multiple filter criteria
  - Date range filters
  - Asset type/location filters
  - Status filters
  - Technician/user filters
  - Save filter presets
- **Sorting**
  - Multi-column sorting
  - Custom sort orders
- **Search**
  - Global search across all fields
  - Column-specific search
- **Bulk Actions**
  - Bulk status updates
  - Bulk assignment
  - Bulk export
- **Inline Editing**
  - Edit table cells directly
  - Save changes per row or bulk
  - Validation and error handling
- **Export**
  - Export filtered data to CSV/Excel
  - PDF reports
  - Scheduled exports
- **Pagination**
  - Configurable page size
  - Server-side pagination for performance

#### 3. Maintenance Event Detail (`/maintenance/admin/events/<event_id>`)
**Purpose**: Full detail view with editing capabilities for any maintenance event

**Components**:
- **Event Information** (Editable)
  - Event metadata (status, dates, assigned technician)
  - Related asset information
  - Maintenance plan reference
- **Action Sets and Actions** (Editable)
  - View all action sets in event
  - Edit action set details
  - View and edit individual actions
  - Add/remove actions
- **Part Demands** (Editable)
  - View all part demands
  - Edit part demand details
  - Approve/reject demands
- **History and Audit Trail**
  - Complete event history
  - All changes with user and timestamp
  - Comments and attachments
- **Related Data**
  - Asset details
  - Maintenance history for asset
  - Related events

#### 4. Asset Maintenance View (`/maintenance/admin/assets/<asset_id>/maintenance`)
**Purpose**: Complete maintenance history and schedule for specific asset

**Components**:
- **Asset Information**
  - Asset details
  - Current location and status
- **Maintenance History**
  - Timeline of all maintenance events
  - Completion status and dates
  - Associated technicians
  - Cost tracking (if available)
- **Upcoming Maintenance**
  - Scheduled maintenance from plans
  - Due dates
  - Can create events manually
- **Maintenance Statistics**
  - Total maintenance count
  - Average maintenance duration
  - Reliability metrics
  - Cost totals

#### 5. Analytics and Reporting (`/maintenance/admin/analytics`)
**Purpose**: Advanced analytics and reporting capabilities

**Components**:
- **Reports**
  - Maintenance completion reports
  - Technician productivity reports
  - Asset maintenance history reports
  - Cost analysis reports
  - Schedule adherence reports
- **Charts and Visualizations**
  - Maintenance trends over time
  - Technician workload distribution
  - Asset type maintenance frequency
  - Part demand patterns
- **Export Options**
  - PDF reports
  - Excel exports
  - CSV data exports
  - Scheduled report generation

#### 6. System Configuration (`/maintenance/admin/config`)
**Purpose**: System-wide maintenance configuration

**Components**:
- **Maintenance Settings**
  - Default frequencies
  - Notification settings
  - Auto-assignment rules
  - Alert thresholds
- **Template Management**
  - System-wide template library
  - Template categories and organization
  - Template versioning
- **User and Role Management**
  - Assign technicians to assets/types
  - Role-based access configuration
  - Permission management

### Technical Implementation

#### Routes
```python
# app/presentation/routes/maintenance/admin/__init__.py
admin_bp = Blueprint('admin_portal', __name__, url_prefix='/maintenance/admin')

@admin_bp.route('/')
@admin_bp.route('/dashboard')
def dashboard():
    """Admin dashboard with fleet overview"""

@admin_bp.route('/fleet')
def fleet_table():
    """Comprehensive table view of all maintenance data"""

@admin_bp.route('/events/<int:event_id>')
def event_detail(event_id):
    """Detailed view of maintenance event with editing"""

@admin_bp.route('/events/<int:event_id>/edit', methods=['POST'])
def edit_event(event_id):
    """Edit maintenance event"""

@admin_bp.route('/assets/<int:asset_id>/maintenance')
def asset_maintenance(asset_id):
    """Maintenance history for asset"""

@admin_bp.route('/analytics')
def analytics():
    """Analytics and reporting"""

@admin_bp.route('/config')
def system_config():
    """System configuration"""
```

#### Services
```python
# app/services/maintenance/admin_service.py
class AdminService:
    @staticmethod
    def get_fleet_maintenance_status():
        """Get fleet-wide maintenance status and KPIs"""
    
    @staticmethod
    def get_maintenance_table_data(filters, pagination):
        """Get filtered and paginated maintenance data for table"""
    
    @staticmethod
    def update_maintenance_event(event_id, data):
        """Update maintenance event (with validation)"""
    
    @staticmethod
    def get_asset_maintenance_history(asset_id):
        """Get complete maintenance history for asset"""
    
    @staticmethod
    def generate_maintenance_report(report_type, filters):
        """Generate maintenance reports"""
    
    @staticmethod
    def get_maintenance_analytics(filters):
        """Get maintenance analytics data"""
```

### User Workflows

#### Workflow 1: Fleet Overview and Monitoring
1. Leader/Admin logs in → Redirected to Admin Dashboard
2. Views fleet health KPIs → Identifies issues or trends
3. Navigates to specific area → Drills down into details
4. Takes corrective action if needed → Edits events, reassigns work

#### Workflow 2: Admin Filter and Edit Maintenance Data
1. admin has simple CRUD and filter access to the rows of each table directly
5. System warns and updates 

#### Workflow 3: Generate Reports
1. Leader/Admin navigates to Analytics
2. Selects report type → Applies filters
3. Views generated report → Exports if needed
4. Schedules recurring reports if desired

## Implementation Phases

### Phase 1: Foundation (Weeks 1-2)
**Goal**: Set up portal structure and basic routing

**Tasks**:
1. Create portal blueprint structure
   - `app/presentation/routes/maintenance/technician/`
   - `app/presentation/routes/maintenance/manager/`
   - `app/presentation/routes/maintenance/admin/`
2. Implement basic authentication and role-based access
3. Create base templates for each portal
4. Set up portal navigation and routing
5. Create shared components and utilities

**Deliverables**:
- Portal route structure
- Role-based access control
- Base templates
- Navigation structure

### Phase 2: Technician Portal (Weeks 3-4)
**Goal**: Complete Technician Portal with all core features

**Tasks**:
1. Implement Technician Dashboard
   - Assigned work list
   - Quick stats
   - Today's schedule
2. Implement Work Detail View
   - Action set display
   - Action status updates
   - Comments and attachments
3. Implement Action Detail View
4. Implement Part Request interface
5. Implement Maintenance History
6. Testing and refinement

**Deliverables**:
- Complete Technician Portal
- Technician workflows functional
- User acceptance testing

### Phase 3: Manager Portal - Core Features (Weeks 5-7)
**Goal**: Implement Manager Portal core planning and oversight features

**Tasks**:
1. Implement Manager Dashboard
2. Implement Template Management (Action Sets, Actions, Part Demands)
3. Implement Maintenance Plans
4. Implement Assets Due for Maintenance
5. Implement Maintenance Event Assignment
6. Testing and refinement

**Deliverables**:
- Manager Portal core features
- Template and plan management functional
- Assignment workflows functional

### Phase 4: Manager Portal - Oversight Features (Weeks 8-9)
**Goal**: Complete Manager Portal with oversight and approval features

**Tasks**:
1. Implement Active Maintenance Monitoring
2. Implement Part Demand Approval
3. Implement Onsite Events view
4. Testing and refinement

**Deliverables**:
- Complete Manager Portal
- All oversight features functional
- User acceptance testing

### Phase 5: Admin Portal - Dashboard and Tables (Weeks 10-12)
**Goal**: Implement Admin Portal dashboard and comprehensive table views

**Tasks**:
1. Implement Fleet Maintenance Dashboard
   - KPIs and metrics
   - Alert dashboard
   - Recent activity feed
2. Implement Fleet Maintenance Table
   - Data views for all maintenance entities
   - Advanced filtering
   - Inline editing
   - Export functionality
3. Testing and refinement

**Deliverables**:
- Admin Portal dashboard
- Comprehensive table views with filtering and editing
- User acceptance testing

### Phase 6: Admin Portal - Analytics and Configuration (Weeks 13-14)
**Goal**: Complete Admin Portal with analytics and configuration

**Tasks**:
1. Implement Analytics and Reporting
   - Reports generation
   - Charts and visualizations
   - Export options
2. Implement System Configuration
   - Maintenance settings
   - Template management
   - User and role management
3. Testing and refinement

**Deliverables**:
- Complete Admin Portal
- Analytics and reporting functional
- System configuration functional
- Final user acceptance testing

### Phase 7: Integration and Polish (Weeks 15-16)
**Goal**: Integration testing, performance optimization, and final polish

**Tasks**:
1. Integration testing across all portals
2. Performance optimization
3. UI/UX refinements
4. Documentation
5. Training materials
6. Final deployment

**Deliverables**:
- Fully integrated maintenance portal system
- Performance optimized
- Complete documentation
- Deployed and operational

## Technical Considerations

### Data Layer
- No changes needed to existing data models
- May need additional indexes for performance on frequently filtered queries
- Consider materialized views for dashboard statistics

### Business Layer
- Leverage existing context managers (MaintenanceEvent, MaintenanceActionSetContext, etc.)
- May need new context managers for portal-specific operations
- Ensure business logic validation for all portal actions

### Services Layer
- Create portal-specific service classes:
  - `TechnicianService`
  - `ManagerService`
  - `AdminService`
- Services handle data aggregation, filtering, and presentation logic
- Services should be stateless and reusable

### Presentation Layer
- Use HTMX for dynamic interactions
- Implement responsive design for mobile access
- Ensure consistent UI patterns across portals
- Use widget pattern for reusable components (see widgets.md)

### Performance
- Implement pagination for large data sets
- Use server-side filtering and sorting
- Cache frequently accessed data (dashboard stats)
- Optimize database queries with proper indexes
- Consider background jobs for heavy analytics

### Security
- Role-based access control on all routes
- Validate permissions in business layer
- Audit all data modifications
- Protect sensitive data from unauthorized access
- Input validation and sanitization


## Success Metrics

### Technician Portal
- Technician can view all assigned work within 2 seconds
- Technician can complete an action set in under 5 minutes (excluding actual work time)
- 95% of technicians can use portal without training

### Manager Portal
- Manager can create a maintenance plan in under 10 minutes
- Manager can view and assign maintenance for 100+ assets in under 5 minutes
- 90% of part demands approved within 24 hours

### Admin Portal
- Dashboard loads within 3 seconds
- Table view handles 10,000+ records with filtering in under 2 seconds
- Reports generate in under 30 seconds for typical data volumes

## References
- **System Design**: See [SystemDesign.md](SystemDesign.md) for overall architecture
- **Implementation Plan**: See [ImplementationPlan.md](ImplementationPlan.md) for overall phase structure
- **Widget Components**: See [widgets.md](widgets.md) for reusable UI components
- **Application Design**: See [ApplicationDesign.md](ApplicationDesign.md) for coding standards


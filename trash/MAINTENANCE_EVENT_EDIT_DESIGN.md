# Maintenance Event Edit Screen Design Document

## Overview
The edit screen will be an enhanced version of the work screen (`work_maintenance_event.html`) with additional tools for comprehensive maintenance event management. The screen will maintain the existing maintenance event details card unchanged and add powerful editing capabilities for actions, part demands, and tools.

## Core Principles
- **Preserve existing functionality**: The maintenance event details card remains unchanged
- **Audit trail**: All changes must leave a comment stating the event was changed with a brief description
- **Enhanced workflow**: Build upon the work screen foundation rather than creating a separate interface
- **Action management**: Easy add, remove, and renumbering of actions
- **Template integration**: Leverage existing template actions and proto actions for quick action creation

## Screen Layout

### Main Structure
The edit screen will mirror the work screen layout with the following enhancements:

1. **Header Section** (unchanged from work screen)
   - Page title with edit indicator
   - Back to view/work navigation

2. **Status Card** (enhanced)
   - Existing progress indicators
   - Add "Edit Mode" badge/indicator
   - Note: All changes save immediately via full page reloads (no separate save button needed)

3. **Maintenance Event Details Card** (UNCHANGED)
   - All existing fields and display remain exactly as-is
   - No modifications to this section

4. **Actions List** (enhanced with editing capabilities)
   - Existing action cards with status indicators
   - Add inline editing controls (button-based, full page reloads):
     - Up arrow button (↑) - Move action earlier in sequence
     - Down arrow button (↓) - Move action later in sequence
     - Delete action button (with confirmation modal)
     - Duplicate action button
     - Edit action button (existing modal)
   - All operations redirect back to edit page after completion
   - Action creator portal integration (see below)

5. **Sidebar** (enhanced)
   - Existing quick actions and event information
   - New "Action Creator Portal" section

## Action Creator Portal

### Purpose
A dedicated interface for creating new actions with four creation methods:

1. **From Template Action**
   - Search/browse existing template action sets
   - Select template action items
   - Copy all values (action_name, description, estimated_duration, safety_notes, etc.)
   - Option to link to template_action_item_id or create standalone

2. **From Proto Action**
   - Search/browse proto action library
   - Select proto action items
   - Copy all values from proto action
   - Option to link to proto_action_item_id or create standalone

3. **From Current Action Set**
   - Browse actions already in the current maintenance event
   - Select existing actions to duplicate/copy
   - Copy all values including current status, notes, part demands, and tools
   - Useful for creating variations or repeating similar actions
   - Option to copy part demands and tools from source action

4. **Blank Action**
   - Create empty action with minimal defaults
   - User fills in all fields manually

### Portal Features
- **Search Interface**: Filter template/proto/current actions by name, description, or keywords
- **Preview Panel**: Show selected action details before copying
- **Bulk Selection**: Select multiple template/proto/current actions to add in sequence
- **Smart Copying**: 
  - Copy part demands from template/proto/current action (if applicable)
  - Copy tool requirements from template/proto/current action (if applicable)
  - Copy safety notes, estimated duration, etc.
  - For current action set: Option to copy current status, completion notes, and other execution data
- **Position Selection**: Choose where to insert new action (beginning, end, after specific action)

## Enhanced Action Management

### Action Operations
1. **Add Action**
   - Via Action Creator Portal (primary method)
   - Quick add button (opens portal)
   - Keyboard shortcut (Ctrl+N or Cmd+N)

2. **Remove Action**
   - Delete button on each action card
   - Confirmation modal with impact warning
   - Option to preserve part demands/tools (move to event level or delete)
   - Auto-renumber remaining actions

3. **Renumber Actions**
   - "Renumber All" button (auto-assigns sequence_order 1, 2, 3...)
   - Up/Down arrow buttons on each action card to move action in sequence
   - Up arrow: Decrease sequence_order (move earlier in sequence)
   - Down arrow: Increase sequence_order (move later in sequence)
   - Auto-renumber all actions after each move operation
   - Full page reload after each operation (HTMX enhancements to come later)

4. **Edit Action**
   - Enhanced edit modal (existing functionality)
   - Inline quick edits for common fields
   - Bulk edit multiple actions (select checkboxes)

5. **Duplicate Action**
   - Duplicate button on action card
   - Creates copy with incremented sequence_order
   - Option to duplicate part demands and tools

## Part Demand Management (Manager Approval Screen)

### Purpose
A dedicated manager approval interface for reviewing and approving/rejecting part demands within the maintenance event. This screen enables managers to efficiently process part requests with full context of the maintenance event.

### Part Demand Status States
Based on the maintenance work page design, part demands have the following statuses:
- **Pending Manager Approval**: Initial request, awaiting maintenance manager review
- **Pending Inventory Approval**: Manager approved, awaiting supply/inventory team review
- **Ordered**: Supply has placed order for the part (awaiting delivery)
- **Issued**: Part has been provided/issued to technician
- **Rejected**: Request was denied (manager or inventory)
- **Cancelled by Technician**: Technician cancelled the request
- **Cancelled by Supply**: Supply/inventory team cancelled the request
- **Backordered**: Part is on backorder, request remains active


### Manager Approval Workflow

1. **View Pending Requests**: Manager sees all part demands with status "Pending Manager Approval"
2. **Review Request Details**: 
   - Part information (name, number, quantity)
   - Requesting technician (`requested_by`)
   - Associated action and maintenance event
   - Request date and any notes
   - Priority level
   - Inventory availability (if available)
3. **Approve or Reject**:
   - **Approve**: Sets `maintenance_approval_by_id` and `maintenance_approval_date`, transitions status to "Pending Inventory Approval" Custom route in buisness model event context to manage approval interaction for later when inventory module is developed
   - **Reject**: Transitions status to "Rejected", requires rejection reason/notes
   - Both actions generate event comments automatically

### Screen Components

1. **Part Demands List View**
   - Filterable by status (Pending Manager Approval, All, etc.)
   - Sortable by: Priority, Request date, Technician, Part name, Action
   - Group by action or show unified list
   - Color-coded status badges
   - Quick actions: Approve, Reject, View Details

2. **Part Demand Detail View** (Modal or Inline)
   - Full part information
   - Requesting technician and date
   - Associated action and maintenance event context
   - Current status and approval history
   - Inventory availability check (if available)
   - Approval section:
     - Approve button (with notes field)
     - Reject button (with reason field, required)
     - View approval history (`maintenance_approval_by`, `maintenance_approval_date`)

### Approval Actions
- **Approve Part Demand**:
  - Sets `maintenance_approval_by_id` = current_user.id
  - Sets `maintenance_approval_date` = current timestamp
  - Updates status to "Pending Inventory Approval"
  - Generates event comment: `"[Part Demand Approved] Approved part demand: [Part Name] x[Quantity] by [username]. Notes: [approval notes]"`
  - Full page reload after approval

- **Reject Part Demand**:
  - Updates status to "Rejected"
  - Requires rejection reason (mandatory field)
  - Generates event comment: `"[Part Demand Rejected] Rejected part demand: [Part Name] x[Quantity] by [username]. Reason: [rejection reason]"`
  - Full page reload after rejection

### Additional Features
1. **Add Part Demand** (for managers)
   - Existing modal functionality
   - Quick add from action card
   - Manager can create part demands on behalf of technicians

2. **Edit Part Demand** (limited)
   - Edit quantity (if not yet issued)
   - Edit notes
   - Change priority
   - Move part demand between actions (if not yet issued)

3. **View Approval History**
   - Display `maintenance_approval_by` and `maintenance_approval_date`
   - Display `supply_approval_by` and `supply_approval_date` (if available)
   - Show approval/rejection notes

4. **Part Demand Import** (for adding from templates)
   - Import from template action's part demands
   - Import from proto action's part demands
   - Useful when creating actions from templates/proto actions

## Tool Management

### New Features
1. **Add Tool**
   - Similar to part demand modal
   - Link to tool inventory (if available)
   - Add tool requirements to actions

2. **Tool Operations**
   - Edit tool requirements
   - Remove tools
   - Bulk operations

3. **Tool Import**
   - Import from template action's tools
   - Import from proto action's tools

## Change Tracking & Comments

### Comment Generation
Every change operation must generate an event comment with format:
```
"[Operation Type] [Description] by [username]. [Brief details]"
```

### Comment Examples
- `"[Action Added] Added action 'Inspect bearings' from template 'Monthly PM' by admin. Inserted at position 3."`
- `"[Action Removed] Removed action 'Check oil level' by admin. Part demands preserved."`
- `"[Actions Renumbered] Renumbered all actions by admin. New sequence: 1-5."`
- `"[Part Demand Added] Added part demand: Oil Filter x2 to action 'Change oil' by admin."`
- `"[Tool Added] Added tool requirement: Torque Wrench to action 'Tighten bolts' by admin."`

### Change Summary
- Track all changes in current session
- Show "Unsaved Changes" indicator
- Option to view change log before saving

## Technical Implementation Notes

### Implementation Philosophy
- **Start Simple**: Initial implementation uses traditional form submissions and full page reloads
- **Button-Based**: All interactions use buttons/forms - no complex JavaScript initially
- **Progressive Enhancement**: Foundation built for future HTMX/Alpine.js enhancements
- **Reliable**: Full page reloads ensure consistent state and work without JavaScript
- **User Feedback**: Flash messages and redirects provide clear feedback after each operation

### Backend Routes Needed
- `POST /maintenance-event/<event_id>/action/create` - Create new action (redirects back to edit page)
- `POST /maintenance-event/<event_id>/action/<action_id>/delete` - Delete action (redirects back to edit page)
- `POST /maintenance-event/<event_id>/action/<action_id>/move-up` - Move action up in sequence (redirects back)
- `POST /maintenance-event/<event_id>/action/<action_id>/move-down` - Move action down in sequence (redirects back)
- `POST /maintenance-event/<event_id>/actions/renumber` - Bulk renumber all actions (redirects back)
- `POST /maintenance-event/<event_id>/action/<action_id>/duplicate` - Duplicate action (redirects back)
- `GET /maintenance-event/<event_id>/template-actions/search` - Search template actions (for Action Creator Portal)
- `GET /maintenance-event/<event_id>/proto-actions/search` - Search proto actions (for Action Creator Portal)
- `POST /maintenance-event/<event_id>/action/<action_id>/tool/create` - Add tool (redirects back)
- `POST /maintenance-event/<event_id>/action/<action_id>/tool/<tool_id>/delete` - Remove tool (redirects back)
- `POST /maintenance-event/<event_id>/part-demand/<part_demand_id>/approve` - Approve part demand (manager approval, redirects back)
- `POST /maintenance-event/<event_id>/part-demand/<part_demand_id>/reject` - Reject part demand (manager rejection, redirects back)

### Frontend Implementation Approach
- **Initial Implementation**: Full page reloads for all operations
- **Button-based interactions**: All operations use form submissions or button clicks
- **Modal system**: Bootstrap modals for Action Creator Portal and confirmations
- **Search/filter components**: Standard form inputs with server-side filtering
- **Future Enhancements** (Phase 2+):
  - HTMX for partial page updates and hx-boost for progressive enhancement
  - Alpine.js for basic client-side interactions (show/hide, simple state)
  - No drag-and-drop libraries needed

### Database Considerations
- Ensure sequence_order updates are atomic
- Handle cascading deletes appropriately
- Maintain referential integrity for template_action_item_id links

## Questions & Considerations

### Design Questions
1. **Action Creator Portal Location**: 
   - Should it be a persistent sidebar panel or a modal that opens on demand?
   - **Recommendation**: Modal with quick access button, can be pinned to sidebar

2. **Template/Proto Action Linking**:
   - When copying from template/proto, should we maintain the link (template_action_item_id/proto_action_item_id)?
   - **Recommendation**: Optional checkbox - "Link to source template/proto" (default: unchecked for flexibility)


4. **Undo/Redo**:
   - Should we implement undo/redo for edit operations?
   - **Recommendation**: Start without, add if user feedback indicates need

5. **Action Status During Editing**:
   - Should actions be editable if they're in "Complete" or "In Progress" status?
   - **Recommendation**: Allow editing but show warning, preserve status history

6. **Part Demand/Tool Preservation**:
   - When deleting an action, what happens to associated part demands and tools?
   - **Recommendation**: Modal with options: "Delete all", "Move to event level", "Cancel operation"

7. **Sequence Order Gaps**:
   - Should we allow gaps in sequence_order (e.g., 1, 3, 5) or always enforce consecutive?
   - **Recommendation**: Allow gaps for flexibility, but provide "compact" button to remove gaps

8. **Template Action Set Context**:
   - Should we show which template action set the event was created from?
   - **Recommendation**: Display in event details card (already exists), show in action creator for reference

9. **Validation**:
   - What validation should occur when adding/editing actions?
   - **Recommendation**: Required fields (action_name, sequence_order), validate sequence_order uniqueness, validate dates

10. **Performance**:
    - How should we handle events with many actions (100+)?
    - **Recommendation**: Lazy loading, pagination, or virtual scrolling for action list

### Implementation Priority
1. **Phase 1**: Basic action add/remove/move (up/down arrows) + Action Creator Portal (template/proto/blank)
   - All operations use full page reloads
   - Button-based interactions only
   - Bootstrap modals for confirmations and Action Creator Portal
2. **Phase 2**: Enhanced editing (duplicate, bulk operations, renumber all)
   - Continue with full page reloads
   - Add bulk selection and operations
3. **Phase 3**: Part demand and tool management enhancements
   - Full page reloads maintained
4. **Phase 4**: Progressive enhancement with HTMX
   - Add hx-boost for smoother navigation
   - Partial page updates for action list
   - Alpine.js for simple client-side interactions (modals, show/hide)

## Success Criteria
- Users can easily add actions from templates, proto actions, or create blank
- Actions can be reordered using up/down arrow buttons (no manual sequence_order editing)
- All operations use simple button clicks with full page reloads
- All changes are tracked with descriptive comments
- The interface feels like a natural extension of the work screen
- Maintenance event details card remains completely unchanged
- No disruption to existing work screen functionality
- Foundation ready for HTMX/Alpine.js enhancements in future phases


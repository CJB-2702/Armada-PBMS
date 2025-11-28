# Maintenance Work Page Design

## Overview

This document outlines the conceptual design for the Maintenance Work Page (`/maintenance/maintenance-event/<event_id>/work`). The page enables technicians and authorized users to perform maintenance work, track progress, manage actions, and handle delays and part requests. This is a conceptual design document focusing on features, user workflows, and business concepts rather than implementation details.

---

## Core Domains

### 1. Task Completion and State Management

#### Action State Transitions

**Available States:**
- **Not Started**: Default state when action is first created
- **In Progress**: Action has been initiated by technician (work is actively being performed)
- **Skipped**: Action was intentionally bypassed (e.g., not applicable to this specific maintenance instance)
- **Blocked**: Action cannot proceed due to external factors (e.g., waiting on parts, equipment unavailable, safety concerns)
- **Complete**: Action has been successfully finished
- **Failed**: Action was attempted but could not be completed successfully

**State Transition Rules:**
- Any state can transition to "Blocked" (external interruption)
- "Not Started" → "In Progress" → "Complete"
- "Not Started" → "In Progress" → "Failed"
- "Not Started" or "In Progress" → "Skipped"
- "Blocked" can transition to "In Progress" (when blocking condition resolved)
- "Failed" can transition to "In Progress" (retry scenario)
- **Terminal State Changes**: Actions can be moved between "Complete" and "Failed" states after initial completion, but this requires a comment explaining the change

**State Change Behavior:**
- Every state change automatically generates a system comment on the Event
- System comments are flagged as automated (not human-made) but have the user's ID as the created_by person
- Format: "[Action: <action_name>] Status changed from <old_status> to <new_status> by <user>"
- **Comment Requirements:**
  - Initial transition to "Blocked" requires a comment explaining the blocking condition
  - Transition from "Blocked" back to "In Progress" does not require a comment (resolution can be implied)
  - Changes between "Complete" and "Failed" states require a comment explaining the change
- State changes preserve timestamp information for audit trail

#### Action Completion Workflow

**Completion Modal Requirements:**
- Modal appears when user attempts to mark action as "Complete", "Failed", "Skipped", or "Blocked"
- **Required Fields:**
  - Status selection (if multiple completion states are available for the transition)
  - Completion comment (text area, required for all state changes)
  - **Special Requirement**: User must provide a comment if action is being marked as "Failed" or "Blocked" (these states require explanation)
- **Optional Fields:**
  - Billable hours (editable by user, but NOT auto-calculated from start/end times)
  - Additional notes (optional detailed notes beyond the required comment)
- **Note**: Billable hours represent actual work time, which may differ from the time elapsed between start and end times (due to breaks, waiting, etc.)
- **Comment Flagging:**
  - If user provides any text in completion comment or notes fields → flag as human-made comment
  - Human-made comments should be visually distinguishable from automated comments
- **Validation:**
  - Dates must be logical (end_time >= start_time)
  - Billable hours must be non-negative

---

### 2. Date and Time Editing

#### Actual Start and Actual End Editing

**Editable Fields:**
- `start_date` (MaintenanceActionSet)
- `end_date` (MaintenanceActionSet)
- `start_time` (Action)
- `end_time` (Action)

**Editing Interface:**
- Inline editing or dedicated date/time picker fields
- Show both planned and actual dates for comparison
- Highlight discrepancies between planned and actual
- Allow manual adjustment for corrections and retroactive updates

**Business Rules:**
- Start date/time must be before end date/time (if both are set)
- Both start and end times can be blank
- Only start time can be set (end time can remain blank until completion)
- Cannot set end time before start time
- Billable hours do not have to match calculated duration from start/end times (allows for manual adjustment)
- **Planned Start Time**: MaintenanceActionSet has a `planned_start_datetime` field for scheduling purposes
- No validation preventing dates that are too far in the past (allows users to correct mistakes)

**Use Cases:**
- Correcting incorrect timestamps
- Retroactively recording work performed
- Adjusting times after reviewing work logs
- Synchronizing with external time tracking systems

---

### 3. Billable Hours Management

#### Actual Billable Hours Field

**New Field:**
- `actual_billable_hours` (MaintenanceActionSet) - Total billable hours for entire maintenance event

**Default Calculation:**
- On initial load or calculation trigger: Sum of all action `billable_hours` values
- Formula: `actual_billable_hours = SUM(actions.billable_hours)`
- **Auto-update Behavior**: Updates automatically and immediately when individual action billable hours change
  - **Auto-update rule**: If an action's billable hours is updated and the new sum of all action billable hours is greater than the current MaintenanceActionSet billable hours, automatically update the MaintenanceActionSet billable hours to the new sum immediately
  - **Manual override allowed**: It is acceptable for users to set actual total billable hours less than the sum of action billable hours, but the UI should display a warning when this occurs
  - **Warning threshold**: Display warning if actual billable hours is less than calculated sum OR if actual is 4x greater than calculated sum (no maximum cap, just warning)

**Manual Override:**
- User can edit `actual_billable_hours` independently
- When manually edited, show visual indicator that it differs from sum
- Display both calculated sum and manually entered value
- Allow user to "sync to sum" button to reset to calculated value
  - **Note**: This sync action only updates the front-end form field; user must submit the form to save the change 

**Business Context:**
- Actual billable hours may differ from sum due to:
  - Non-action work (setup, teardown, waiting)
  - Multi-person work overlap
  - Administrative time
  - Rework or additional troubleshooting

**Display and Validation:**
- Show calculated sum prominently
- Highlight if manual value differs from sum
- Provide warnings if actual is less than calculated sum OR if actual is 4x greater than calculated sum
- No maximum cap on billable hours (warnings only, no hard limits)

---

### 4. Maintenance Completion Workflow

#### Completion Modal and Requirements

**When User Clicks "Mark Complete" in Status Card:**
- Modal popup appears with required fields
- Cannot proceed without completing all required fields
- **Prerequisite**: All actions must be in terminal states (Complete, Failed, or Skipped) before maintenance can be marked complete
  - **Blocked Actions**: If any actions are in "Blocked" state, user must first change them to "Skipped" (or another terminal state)
  - System displays an error message: "Cannot complete maintenance. Please skip all blocked actions first."
  - User cannot proceed until all blocked actions are resolved

**Required Fields:**
- **Completion Comment**: Text area (required, cannot be empty)
  - Purpose: Capture final notes about the maintenance work
  - Format: Free-form text
- **Verify Dates**: Display dates for user confirmation and editing
  - Actual start date/time (required, editable, can be set earlier than event creation date)
  - Actual end date/time (required, editable)
  - Duration calculation (automatically calculated: end - start)
- **Verify Billable Hours**: Display for user confirmation
  - Actual billable hours (editable in modal - only MaintenanceActionSet total, not individual action billable hours)
  - Sum of action billable hours (read-only, for comparison)
  - Difference indicator (if different)
  - Warning if actual is less than sum or 4x greater than sum

**Validation:**
- Completion comment must be provided (cannot be empty)
- Dates must be logical and complete (start date before end date, both required)
- Billable hours must be non-negative and greater than 0.2 hours (12 minutes minimum)
  - **Note**: No auto-calculation of billable hours from start/end times - only basic validation that value is > 0.2 hours
- All actions must be in terminal states (Complete, Failed, Skipped, or Cancelled) - blocked actions must be resolved first

**Workflow:**
- User fills out required fields
- System validates all inputs
- On submit:
  - Update MaintenanceActionSet status to "Complete"
  - Set `end_date` to current time (if not already set)
  - Save completion notes
  - Update actual billable hours
  - Generate automated completion comment on Event
  - Redirect to view page or show success message

---

### 5. Part Demands Management

#### Part Demand Lifecycle

**Available Statuses:**
- **Pending Manager Approval**: Initial request, awaiting maintenance manager review
- **Pending Inventory Approval**: Manager approved, awaiting supply/inventory team review
- **Ordered**: Supply has placed order for the part (awaiting delivery)
- **Issued**: Part has been provided/issued to technician
- **Rejected**: Request was denied (manager or inventory)
- **Cancelled by Technician**: Technician cancelled the request
- **Cancelled by Supply**: Supply/inventory team cancelled the request
- **Backordered**: Part is on backorder, request remains active

**Status Transition Rules (Full Lifecycle):**
- Requests start in "Pending Manager Approval"
- Manager can approve → "Pending Inventory Approval" or reject → "Rejected"
- Inventory/Supply can:
  - Issue → "Issued"
  - Reject → "Rejected"
  - Mark as ordered → "Ordered"
  - Mark → "Backordered"
- Technician can cancel → "Cancelled by Technician" (only if not yet issued - can cancel from "Pending Manager Approval", "Pending Inventory Approval", "Ordered", or "Backordered")
- Supply can cancel → "Cancelled by Supply" (only if not yet issued)
- "Ordered" requests can transition to "Issued" when part is received and provided
- Backordered requests can transition to "Issued" when part becomes available

**Work Page Actions (Limited):**
- From the work page, users have limited actions available:
  - **Issue**: Any user can issue parts directly (no restrictions - technicians sometimes acquire parts without formal permission)
    - This action automatically leaves a comment on the Event
    - Transitions part demand status to "Issued"
  - **Cancel by Technician**: Technician can cancel pending requests
    - Available if part demand is not yet issued (can cancel from: "Pending Manager Approval", "Pending Inventory Approval", "Ordered", or "Backordered")
    - **Required**: Cancellation comment must be provided (cannot be empty)
    - This action automatically leaves a comment on the Event
    - Transitions part demand status to "Cancelled by Technician"
- **Note**: Other status transitions (manager approval, inventory approval, supply cancellation) occur on other pages/workflows, not from the work page
- **Page Refresh Behavior**: Changes made in other tabs (e.g., viewing part demand details) are not reflected on work page until user refreshes or performs an action on the current page

#### Part Demand Display on Work Page

**Visual Indicators:**
- Show part demands grouped by action or as unified list
- Color-coded status badges for quick identification
- Show quantity, part name/number, and current status
- Display approval workflow progress (manager approved ✓, inventory approved ✓)

**Actions Available:**
- **Add Part Demand**: Create new part request for any action
- **Issue Part**: Any user can issue parts directly from work page
- **Cancel Own Request**: Technician can cancel pending requests (only if not yet issued, requires comment)
- **View Part Demand Details**: Opens new tab to `/part-demand/<id>/view` to see full request information and approval history
- **Track Status**: Opens new tab to `/part-demand/<id>/view` for status updates

**Comment Generation:**
- Adding a part demand should automatically leave a comment on the Event
- Canceling a part demand should automatically leave a comment on the Event

**Information Display:**
- Part name, part number, quantity required
- Requested by (technician name)
- Date requested
- Current status with visual indicator

---

### 6. Status and Delay Management

#### Status Card

**Purpose:** 
Provide immediate access to critical maintenance event-level actions and display current maintenance status

**Visual Style Reference:**
- Review the builder header card at `/template-builder/1` for styling inspiration
- Should be prominent and clearly indicate current maintenance status

**Status Display:**
- Show maintenance completion percentage prominently
- Display current status badge (Planned, In Progress, Delayed, Complete, Cancelled)
- **Planned State**: Default state for new maintenance events
  - Users cannot set maintenance event to "Planned" if any actions are completed
  - This prevents regression of maintenance status after work has begun

**Available Actions:**
- **Mark Complete**: Trigger maintenance completion workflow (requires completion modal)
- **Place in Delay**: Open delay creation modal

**Display Rules:**
- Show "Mark Complete" when maintenance is in "In Progress" or "Planned" state
- Show "Place in Delay" when maintenance is in "In Progress", "Planned", or active delay state
- Hide or disable actions based on current status and user permissions
- Disable all work editing features when in delay status

#### Delay Modes

**Two Delay Types:**

1. **Work in Delay**
   - **Concept**: Maintenance work is temporarily paused but will resume
   - **Use Cases**: Waiting for parts, equipment unavailable, weather conditions, scheduling conflicts
   - **Behavior**: 
     - Maintenance status changes to "Delayed"
     - User is blocked from accessing work page and redirected to view page
     - Work can be resumed when delay ends via "End Delay" action
   - **Delay Record**: Creates MaintenanceDelay with `delay_type = "Work in Delay"`

2. **Cancellation Requested**
   - **Concept**: Request to cancel the maintenance work
   - **Use Cases**: Asset no longer needs maintenance, safety concerns, major issues discovered
   - **Behavior**:
     - Maintenance status changes to "Delayed"
     - User is blocked from accessing work page and redirected to view page
     - Manager can go to edit page and manually change status to "Cancelled" to complete the cancellation
   - **Delay Record**: Creates MaintenanceDelay with `delay_type = "Cancellation Requested"`

#### Delay Creation Modal

**Required Fields:**
- **Delay Type**: Dropdown selection ("Work in Delay" or "Cancellation Requested")
- **Reason**: Text area (required, cannot be empty)
  - Purpose: Explain why maintenance is being delayed/cancelled
  - Format: Free-form text
  - Minimum length requirement

**Optional Fields:**
- **Priority**: Dropdown (Low, Medium, High, Critical)
  - Default: Medium
  - Used for escalation and reporting
- **Delay Notes**: Additional detailed information
- **Expected Resolution Date**: When the delay is expected to end
- **Billable Hours**: Hours associated with delay (if applicable)

**Delay Record Creation:**
- Creates MaintenanceDelay record with all provided information
- Sets `delay_start_date` to current timestamp
- Links to current user as creator
- Generates automated comment on Event describing the delay
- Updates MaintenanceActionSet `delay_notes` if provided

**Validation:**
- Delay type must be selected
- Reason must be provided and not empty
- **One Delay at a Time**: Only one active delay can exist at a time - user must end current delay before creating a new one

#### Delay Card Display

**Purpose:**
- Display active and historical delays for the maintenance event
- Provide read-only view of delay information
- Show delay status and timeline

**Card Location:**
- Displayed on work page (when not in delay status) and view page
- Positioned in sidebar
- Shows all delays associated with the maintenance event

**Card Content (Read-Only):**

**Active Delay (if present):**
- **Delay Type**: Badge showing "Work in Delay" or "Cancellation Requested"
  - Color coding: "Work in Delay" = warning/yellow, "Cancellation Requested" = danger/red
- **Priority**: Badge showing priority level (Low, Medium, High, Critical)
  - Color coding based on priority level
- **Reason**: Full text of delay reason (read-only)
- **Start Date/Time**: When delay began
- **Duration**: How long delay has been active (calculated from start date to now or end date)
- **Created By**: User who created the delay
- **Delay Notes**: Additional notes if provided (read-only)
- **Expected Resolution Date**: If provided, show expected end date
- **Billable Hours**: If provided, show hours associated with delay

**Historical Delays (if any):**
- Show completed delays (those with `delay_end_date` set)
- Display in chronological order (most recent first or oldest first)
- Show same information as active delay plus:
  - **End Date/Time**: When delay was resolved
  - **Total Duration**: Complete duration of delay
  - **Ended By**: User who ended the delay (if applicable)

**Visual Design:**
- Card-based layout with clear visual hierarchy
- Active delays should be visually distinct (highlighted, border, or different background)
- Historical delays can be in collapsed/expandable sections or separate cards
- Use icons to indicate delay type (clock for "Work in Delay", warning for "Cancellation Requested")
- Show timeline visualization if multiple delays exist

**User Interactions:**
- **Read-Only**: Users cannot edit delay information on work or view pages
- **View Only**: All delay fields are displayed as read-only text
- **Add Delay**: Any user can add new delays via "Place in Delay" quick action (only if no active delay exists)
- **End Delay**: Any user can end active delays via "End Delay" quick action
  - Ending delay does not require a reason/comment (resolution can be implied)
- **Manager Editing**: Any user can edit delays on the edit page (`/maintenance/maintenance-event/<event_id>/edit`)

**Display Rules:**
- If no delays exist, card may be hidden or show "No delays recorded"
- Active delays should always be prominently displayed
- **Always Visible**: Delay card should always be fully visible (not collapsible/expandable)
- **Historical Delays**: All delays (active and historical) should be displayed in the same card on the sidebar
- Card should match the delay display on the view page for consistency
- Show count of total delays (active and historical)

**Information Hierarchy:**
- Most important: Delay type, reason, start date
- Secondary: Priority, duration, created by
- Tertiary: Notes, expected resolution, billable hours
- Historical: End date, ended by, total duration

#### Status-Based Feature Enabling/Disabling

**When in Delay Status:**

**Redirect Behavior:**
- If maintenance event is in "Delayed" status, automatically redirect from work page to view page
- Work page should not be accessible when in delay status
- View page provides appropriate read-only information and delay management actions

**View Page Modifications When in Delay:**

**Disabled/Modified Features:**
- "Do Work" button in Quick Actions card is greyed out (disabled)
- Button tooltip or text indicates: "Work is paused due to delay"
- All work-related actions are unavailable on view page

**Enabled Features on View Page:**
- View all information (read-only)
- View event activity/comments
- View part demands and their statuses
- Add comments to event
- View delay details and information

**End Delay Quick Action:**
- New button in Quick Actions card: "End Delay"
- Available when maintenance is in "Delayed" status
- **Action Behavior:**
  - Closes the active delay (sets `delay_end_date` to current timestamp)
  - Updates MaintenanceActionSet status from "Delayed" to "In Progress"
  - Generates automated comment on Event: "Delay ended by <user>. Maintenance work resumed."
  - Redirects user to work page (`/maintenance/maintenance-event/<event_id>/work`)
- **Validation:**
  - Requires user confirmation (confirmation dialog)
  - Delay end reason/notes are optional (resolution can be implied)
- **Visual Feedback:**
  - Clear indication that delay is ending
  - Success message after redirect to work page
  - Work page shows maintenance is now "In Progress"
- **Permissions**: Any user can end delays (no role restrictions)

**Delay Status Indicators:**
- View page should clearly display delay information
- Show current delay type, reason, start date, and duration
- Visual banner or alert indicating work is paused
- Link to view full delay details if needed
- **Consistency**: Same delay card displayed in sidebar on both work page and view page

---

### 7. Comments and Audit Trail

#### Automated vs Human-Made Comments

**Automated Comments:**
- Generated by system when state changes occur
- Format: Structured, consistent format with system-generated text
- Flag: System flag indicating automated generation (`is_human_made = False`)
- **User Attribution**: Automated comments have the user's ID as the `created_by` person (the user who triggered the state change)
- Examples:
  - Action state changes
  - Maintenance status changes
  - Delay creation
  - Completion events

**Human-Made Comments:**
- Created by users through:
  - Completion modals (when user provides text)
  - Comment forms
  - Notes fields that get converted to comments
- Flag: User flag indicating human creation (`is_human_made = True`)
- Display: Visually distinct from automated comments (different styling, icon, or badge)
- Purpose: Capture user insights, observations, and detailed information

**Comment Requirements:**
- All state changes generate automated comments (with user as created_by)
- User-provided text in completion modals creates a single human-made comment (not split into automated + human-made)
- Comments are stored on the Event (not directly on Actions or MaintenanceActionSet)
- Comments provide complete audit trail of all maintenance work activities

**Comment Editing and Deletion:**
- **Editable**: Comments created by the active user can be edited
- **Deletable**: Comments created by the active user can be deleted (soft delete with `deleted` flag)
- **Edit Behavior**: When a comment is edited, create a new comment linked to the previous comment, mark previous comment as "previous edit", and hide previous edits from users
- **Automated Comments**: Cannot be edited or deleted (permanently locked)
- **Character Limits**: Based on data model (`app/data/core/event_info/comment.py`), comments use `db.Text` field which has no character limit - comments are unlimited in length

---

### 8. User Experience Concepts

#### Progressive Disclosure

**Information Hierarchy:**
- Most critical information (status, quick actions) at top
- Action list in main content area with expandable details
- **Action Display Order**: Actions are always displayed in sequence order (as defined by `sequence_order` field), never grouped by status
- Metadata and summary information in sidebar
- Detailed views available on demand (modals, expandable sections)

#### Status Indicators

**Visual Status Representation:**
- Color-coded badges for all statuses
- Consistent color scheme across action and maintenance statuses
- Progress indicators showing completion percentage
- Clear visual distinction between active and terminal states

#### Workflow Guidance

**Contextual Help:**
- Tooltips explaining state transitions
- Help text for complex fields (billable hours calculation)
- Validation messages explaining requirements
- Success/error feedback for all actions

**Workflow Clarity:**
- Clear indication of next steps
- Disabled states with explanatory text (why disabled)
- Confirmation dialogs for critical actions
- Progress tracking showing what's been done and what remains

---

### 9. Data Model Concepts

#### Relationships and References

**MaintenanceActionSet → Actions:**
- One-to-many relationship
- Actions ordered by `sequence_order`
- Actions can exist independently but logically grouped by maintenance event

**Actions → PartDemands:**
- One-to-many relationship
- Part demands track parts needed for specific actions
- Part demands have approval workflow separate from action completion

**MaintenanceActionSet → MaintenanceDelays:**
- One-to-many relationship
- Multiple delays can occur during one maintenance event
- Delays track interruptions and cancellation requests

**Event Comments:**
- Comments stored on Event, not directly on Actions or MaintenanceActionSet
- Provides unified audit trail for all maintenance activities
- Supports attachments and rich content

#### Calculated Fields

**Derived Values:**
- Completion percentage = (completed actions / total actions) * 100
- Actual billable hours = sum of action billable hours (default, can override)
- Duration = end_date - start_date
- Action duration = end_time - start_time

**Validation Dependencies:**
- Billable hours should be reasonable compared to duration
- Action billable hours sum should align with total billable hours
- Dates must be logically ordered
- Status transitions must follow allowed paths

---

### 10. Future Enhancement Concepts

#### Potential Features (Not in Initial Scope)

**Advanced Workflow:**
- Parallel action execution tracking
- Dependency management between actions
- Conditional action skipping based on results
- Action retry workflows

**Collaboration:**
- Multi-technician work assignment
- Real-time collaboration features
- Work handoff between technicians
- Team-based completion

**Reporting and Analytics:**
- Time tracking and analysis
- Efficiency metrics
- Cost tracking
- Predictive maintenance insights

**Integration:**
- External time tracking systems
- Inventory system integration
- Work order systems
- Reporting dashboards

---

## Summary

The Maintenance Work Page is designed to provide a comprehensive interface for performing maintenance work with robust state management, clear workflows, and complete audit trails. Key concepts include:

- **Five action states** (Not Started, In Progress, Skipped, Blocked, Complete, Failed) with clear transition rules
- **Planned state** as default for maintenance events, with protection against regression after work begins
- **Automated comment generation** for all state changes with user attribution and human-made comment flagging
- **Flexible date and billable hours editing** with auto-calculation from action sums and manual override capabilities
- **Comprehensive completion workflow** requiring user verification of dates and hours, with blocked action resolution
- **Complete part demand lifecycle** with eight statuses (including Ordered), universal issue capability, and required cancellation comments
- **Two delay modes** (Work in Delay, Cancellation Requested) with single-delay enforcement and redirect behavior
- **Status-based feature enabling/disabling** to prevent work during delays with automatic redirects
- **Unified comment system** on Events providing complete audit trail with edit/delete capabilities

All features should initially use basic forms with full page reloads, with HTMX integration planned for future enhancements to improve user experience and reduce page refreshes.

---

## Additional Questions for Clarification

### State Management
1. **Planned State Protection**: When blocking users from setting maintenance event to "Planned" if actions are completed - should this block if ANY action is not in "Not Started" state, or only if actions are in terminal states (Complete, Failed, Skipped)? What about actions that are "In Progress" or "Blocked"?

yes it should be in any state

2. **Blocked Action Resolution**: The design states that blocked actions must be set to "Cancelled" before maintenance can be completed. However, "Cancelled" is not listed as one of the available action states. Should "Cancelled" be added as a new action state, or should blocked actions be changed to "Skipped" instead?
change to skipped

### Billable Hours
3. **Billable Hours Editing After State Change**: If an action's billable hours are locked after being marked Complete, but the action can be changed from Complete to Failed (or vice versa), should billable hours become editable again when the state changes, or remain locked permanently once initially set?
remain locked, defer to manager


make sure form fields are all converted to the proper datatypes for the buisness layer in the presentation or services layers
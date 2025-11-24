# Template Builder System Design Document

## Overview

The Template Builder System provides a draft/workspace mechanism for users to construct maintenance templates incrementally before committing them to the production template system. This allows users to build complex templates over multiple sessions without creating incomplete or invalid template records in the main template tables.

## Core Concept

The system introduces a **Template Builder** as an intermediate staging area where users can:
- Start building a template with a name and type
- Incrementally add and modify template components (actions, parts, tools, attachments)
- Save their progress at any point
- Review and validate the template before final submission
- Convert the draft template into a real `TemplateActionSet` when ready

## Data Model

### TemplateBuilder Table

A new database table `template_build_memory` that inherits from `UserCreatedBase` to provide user tracking and basic meta information:

**Core Fields:**
- **User Information**: Inherited from `UserCreatedBase` (created_by_id, updated_by_id, created_at, updated_at)
- **Template Name**: The intended name for the final template (e.g., "Monthly Truck Inspection")
- **Build Type**: Classification of the template being built (e.g., "Preventive", "Corrective", "Inspection", "Overhaul")
- **Build State (JSON)**: A JSON field containing the complete draft template structure including:
  - Template-level metadata (task_name, description, estimated_duration, safety_review_required, staff_count, parts_cost, labor_hours)
  - Array of template action items with their properties (sequence_order, instructions, minimum_staff_count, etc.)
  - Array of part demands associated with each action
  - Array of tools required for each action
  - Array of attachments at both template and action levels
  - Any other template-related data

**Status Fields:**
- **Build Status**: Current state of the builder (e.g., "Draft", "In Progress", "Ready for Review", "Submitted")
- **Last Modified**: Timestamp of last change (can use updated_at from UserCreatedBase)

## Architecture Components

### 1. TemplateBuilderMemory Data Model

The `TemplateBuilderMemory` class inherits from `UserCreatedBase` and provides:
- Database persistence for draft templates
- JSON serialization/deserialization methods for build state

### 1.1 TemplateBuilderAttachmentReference Data Model

A new database table `template_builder_attachment_references` that tracks **newly uploaded** attachments during template building:

**Purpose**: Track attachment references for builds so that canceled or deleted attachments don't get lost. Provides a reference table separate from the build state JSON.

**Core Fields:**
- **User Information**: Inherited from `UserCreatedBase`
- **Builder Reference**: `template_builder_memory_id` (FK to `template_build_memory`)
- **Attachment Reference**: `attachment_id` (FK to `attachments`)
- **Attachment Level**: `attachment_level` (String: 'action_set' or 'action')
- **Action Index**: `action_index` (Integer, nullable) - Index of action if attachment_level is 'action'
- **Metadata**: `description`, `sequence_order`, `is_required` (matching TemplateActionSetAttachment/TemplateActionAttachment structure)
- **Status**: `is_finalized` (Boolean, default=False) - Marks reference as finalized after template submission

**Important Rules**:
- **Copied attachments DO NOT create records**: When copying attachments from existing `TemplateActionSet` or `TemplateActionItem`, only the attachment_id is stored in build state JSON. No `TemplateBuilderAttachmentReference` record is created because the attachment already exists in the system.
- **New uploads DO create records**: When a user uploads a new attachment during building, a `TemplateBuilderAttachmentReference` record is created to track it.
- **Submission finalizes references**: Upon successful template submission, all `TemplateBuilderAttachmentReference` records for that builder are marked as `is_finalized=True` (or deleted/archived based on business rules).

**Rationale**: 
- Attachments are references (not duplicates), so we track them separately
- Only new uploads need tracking - existing attachments are already in the system
- If a builder is deleted or canceled, newly uploaded attachments can be identified and cleaned up
- Allows for future attachment reference manager implementation
- Build state JSON contains attachment reference IDs, this table provides the mapping for new uploads only


### 2. TemplateBuilder (Business Logic Layer)

- JSON serialization/deserialization of build state
- Validation methods to check template completeness
- Methods to convert build state to template structure

A buisness class that manages the template building workflow:
- **Create Builder**: Initialize a new template builder with name, type, and user
- **Update Build State**: Modify the JSON build state incrementally as user adds/removes components
- **Validate Build State**: Check that the template structure is valid and complete
- **Save Draft**: Persist current build state to database
- **Load Draft**: Retrieve and restore a saved draft template
- **Submit Template**: Convert the build state JSON into actual `TemplateActionSet` and related records, then optionally archive or delete the builder record

### 3. Template Builder Context (Business Logic Wrapper)

Similar to `TemplateMaintenanceContext`, provides a high-level interface:

**Data Structure: Hybrid Approach (Dict Wrappers with Methods)**
- Core data stored as dicts (matches JSON structure exactly)
- Lightweight wrapper classes with their own methods:
    - **`BuildAction`** wrapper:
        - Wraps a dict internally (`self._data: dict`) containing action fields
        - Contains `part_demands: List[BuildPartDemand]`, `tools: List[BuildActionTool]`, and `attachments: List[BuildAttachment]`
        - Methods: `add_tool(tool_data)`, `add_part_demand(part_data)`, `add_attachment(attachment_data)`, `remove_tool(tool_id)`, `remove_part_demand(part_id)`, `remove_attachment(attachment_id)`, `link_to_proto_action(proto_id)`, `unlink_proto_action()`, getters/setters for action fields
        - Validates fields using `TemplateActionItem.get_column_dict()` (excludes `template_action_set_id`)
    - **`BuildPartDemand`** wrapper:
        - Wraps a dict internally with part demand fields
        - Methods: getters/setters for part demand fields
        - Validates fields using `TemplatePartDemand.get_column_dict()` (excludes `template_action_item_id`)
    - **`BuildActionTool`** wrapper:
        - Wraps a dict internally with tool fields
        - Methods: getters/setters for tool fields
        - Validates fields using `TemplateActionTool.get_column_dict()` (excludes `template_action_item_id`)
    - **`BuildAttachment`** wrapper:
        - Wraps a dict internally with attachment reference fields
        - Methods: getters/setters for attachment fields
        - Validates fields using `TemplateActionAttachment.get_column_dict()` or `TemplateActionSetAttachment.get_column_dict()`
- `TemplateBuilderContext` maintains:
    - `_build_metadata: dict` (template-level fields from `TemplateActionSet`, excludes `maintenance_plan_id`)
    - `_build_actions: List[BuildAction]` (list of BuildAction wrappers)
    - `_build_attachments: List[BuildAttachment]` (list of action-set level attachments)
- **Interaction Pattern**: Context calls methods on wrapper instances (e.g., `action.add_tool(tool_data)`, `action.add_part_demand(part_data)`)
- **Benefits**: 
    - Simple serialization (dicts → JSON via `{action._data for action in actions}`)
    - Type safety via wrapper methods
    - Clean separation of concerns (each wrapper manages its own data)
    - Automatic field validation (check against SQLAlchemy model columns)
    - Minimal maintenance (if `VirtualActionItem` adds a field, wrapper can access it without code changes)

**Initialization**:
- Deserializes JSON from `TemplateBuilderMemory` into Python dicts
- Stores template action set metadata in `_build_metadata` dict
- Creates `BuildAction` wrapper instances from action data in JSON
- Each `BuildAction` contains `BuildPartDemand` and `BuildActionTool` wrappers

**Creation Options**:
- `copy_from_template(template_action_set_id, is_revision=False)` - Copies all data from existing template (attachments, proto references); presentation layer asks user if this should be a new revision or new template
- `create_blank(name, build_type)` - Creates empty builder with just name and type

**Building Functions** (Context delegates to wrapper methods):
- `add_action_from_template_item(template_action_item_id)` → Creates `BuildAction` using `TemplateActionItem.get_column_dict()`, calls `action.add_tool()`, `action.add_part_demand()`, and `action.add_attachment()` for each
- `add_action_from_proto(proto_action_id)` → Creates `BuildAction` using `TemplateActionItem.get_column_dict()`, calls `action.add_tool()`, `action.add_part_demand()`, and `action.link_to_proto_action()`
- `add_action_from_dict(action_dict)` → Creates `BuildAction` from dict (for custom actions from presentation layer)
- `add_part_demand_to_action(action_index, part_data)` → Calls `build_actions[action_index].add_part_demand(part_data)` using `TemplatePartDemand.get_column_dict()`
- `add_tool_to_action(action_index, tool_data)` → Calls `build_actions[action_index].add_tool(tool_data)` using `TemplateActionTool.get_column_dict()`
- `add_attachment_to_action_set(attachment_data)` → Adds action-set level attachment, creates `TemplateBuilderAttachmentReference` record
- `add_attachment_to_action(action_index, attachment_data)` → Calls `build_actions[action_index].add_attachment(attachment_data)`, creates `TemplateBuilderAttachmentReference` record

**Functions to Remove Items** (Context delegates to wrapper methods):
- `remove_action(action_index)` → Removes action, automatically renumbers sequence_order for remaining actions
- `remove_part_demand_from_action(action_index, part_demand_index)` → Calls `build_actions[action_index].remove_part_demand(part_demand_index)`
- `remove_tool_from_action(action_index, tool_index)` → Calls `build_actions[action_index].remove_tool(tool_index)`
- `remove_attachment_from_action_set(attachment_index)` → Removes action-set level attachment
- `remove_attachment_from_action(action_index, attachment_index)` → Calls `build_actions[action_index].remove_attachment(attachment_index)`
- `unlink_proto_from_action(action_index)` → Calls `build_actions[action_index].unlink_proto_action()` (removes reference but keeps all copied data)

**Edit Functions**:
- Getters/setters for all template set metadata (task_name, description, estimated_duration, etc.)
- Getters/setters for all template action details (action_name, description, sequence_order, etc.)

**Auto-save**:
- Saves JSON to `TemplateBuilderMemory` after each edit or change
- Updates `updated_at` timestamp
- Simplicity of this approach is worth the extra database writes

- Handles JSON serialization/deserialization transparently
- Provides statistics and validation on draft templates
- **Template Creation**: Manages the conversion process from builder to template, creating `TemplateActionSet` and all related records directly (no factory pattern for now, with plan to refactor to factory pattern later). Returns a `TemplateMaintenanceContext` once created.

## Workflow

### Building Phase

1. User initiates template creation → `TemplateBuilder` record created with initial name and type
  - User can specify an existing template to copy all information as a starting point
2. User adds template metadata → Build state JSON updated with template-level fields
3. User adds action items → Build state JSON updated with action array
4. User adds parts/tools/attachments → Build state JSON updated incrementally
5. User saves progress → Build state persisted to database
6. User can return later → Load builder by ID, restore build state from JSON

### Submission Phase

1. User reviews draft template → Validation checks performed (only validation point in the workflow)
2. User submits template → `submit_template()` method called
3. System creates `TemplateActionSet` from build state JSON (using direct creation, no factory pattern yet)
4. System creates all related records (`TemplateActionItem`, `TemplatePartDemand`, `TemplateActionTool`, attachments) within a database transaction
5. If any step fails, entire transaction is rolled back and builder state remains unchanged in `TemplateBuilderMemory`
6. If successful, system sets template as active and ready for use
7. Builder record can be archived (status = "Submitted") or deleted based on business rules

## Key Design Decisions

### JSON Build State Structure

The build state JSON should mirror the structure of the actual template data model to simplify conversion:
- Top-level object contains template metadata
- Nested arrays for actions, with each action containing nested arrays for parts, tools, and attachments
- This structure allows direct mapping during template creation

### Build State Updates

The build state is rewritten entirely on each save operation:
- Each user action (add action, modify part, etc.) rebuilds the complete JSON structure from the current in-memory state
- The builder class maintains the current template structure and serializes it to JSON when saving
- This approach simplifies implementation, ensures data consistency, and makes debugging easier
- Future undo/redo functionality can be implemented by storing JSON snapshots if needed

### Validation Strategy

Validation occurs only at submission/translation time:
- **On Submit**: Complete validation (all required components present, no orphaned references, valid structure)
- No validation during building phase - users can create incomplete drafts freely

### Sequence Order Management

Sequence order is automatically managed when actions are added, removed, or reordered:
- When adding an action, it is assigned the next available sequence_order (highest existing + 1, or 1 if first action)
- When removing an action, all subsequent actions are automatically renumbered to maintain consecutive sequence_order values
- When reordering actions (e.g., moving action from position 3 to position 1), all affected actions are renumbered accordingly
- This ensures sequence_order always represents the actual execution order without gaps

### Builder Lifecycle

Builders can exist in multiple states:
- **Initialized**: Initial creation, minimal data
- **In Progress**: Active building, regular saves
- **Ready for Review**: User has completed building, ready for submission
- **Submitted**: Successfully converted to template, builder can be archived
- **Abandoned**: User stopped working, can be cleaned up after retention period

### Error Handling

- **During Building**: If a save to `TemplateBuilderMemory` fails, the previous in-memory state is preserved so the user can retry
- **During Template Creation**: If template creation fails (e.g., one action fails to create), all database changes are rolled back using transaction management. The builder state remains in `TemplateBuilderMemory` unchanged, allowing the user to fix issues and retry submission

## Benefits

1. **User Experience**: Users can work on templates incrementally without pressure to complete in one session
2. **Data Integrity**: Incomplete templates don't pollute the production template system
4. **Flexibility**: JSON structure allows for future template features without schema changes
5. **Performance**: Draft templates don't create complex relational structures until finalized
6. **Recovery**: Users can recover from accidental data loss by loading saved drafts

## Column Dictionary Methods

### Data Model get_column_dict() Methods

All template data model classes will implement `get_column_dict()` class methods that return a set of column names (excluding audit fields and relationship-only fields):

**VirtualAttachmentReference.get_column_dict()**:
- Returns: `{'attachment_id', 'all_attachment_references_id', 'attached_to_type', 'display_order', 'attachment_type', 'caption'}`

**TemplateActionSet.get_column_dict()**:
- Returns: Base fields from `VirtualActionSet.get_column_dict()` plus `{'revision', 'prior_revision_id', 'is_active', 'asset_type_id', 'make_model_id'}`
- **Excludes**: `maintenance_plan_id` (not assigned during building)

**TemplateActionItem.get_column_dict()**:
- Returns: Base fields from `VirtualActionItem.get_column_dict()` plus `{'sequence_order', 'is_required', 'instructions', 'instructions_type', 'minimum_staff_count', 'required_skills', 'proto_action_item_id', 'revision', 'prior_revision_id'}`
- **Excludes**: `template_action_set_id` (action is associated with builder via dict structure)

**TemplatePartDemand.get_column_dict()**:
- Returns: Base fields from `VirtualPartDemand.get_column_dict()` plus `{'is_optional', 'sequence_order'}`
- **Excludes**: `template_action_item_id` (part demand is associated with BuildAction via dict structure)

**TemplateActionTool.get_column_dict()**:
- Returns: Base fields from `VirtualActionTool.get_column_dict()` plus `{'is_required', 'sequence_order'}`
- **Excludes**: `template_action_item_id` (tool is associated with BuildAction via dict structure)

**TemplateActionSetAttachment.get_column_dict()**:
- Returns: Base fields from `VirtualAttachmentReference.get_column_dict()` plus `{'description', 'sequence_order', 'is_required'}`
- **Excludes**: `template_action_set_id` (attachment is associated with builder via dict structure)

**TemplateActionAttachment.get_column_dict()**:
- Returns: Base fields from `VirtualAttachmentReference.get_column_dict()` plus `{'description', 'sequence_order', 'is_required'}`
- **Excludes**: `template_action_item_id` (attachment is associated with BuildAction via dict structure)

### Builder Usage

Wrapper classes use these methods directly instead of SQLAlchemy inspection:
- `BuildAction._get_valid_fields()` → Uses `TemplateActionItem.get_column_dict()`
- `BuildPartDemand._get_valid_fields()` → Uses `TemplatePartDemand.get_column_dict()`
- `BuildActionTool._get_valid_fields()` → Uses `TemplateActionTool.get_column_dict()`
- `TemplateBuilderContext._get_valid_metadata_fields()` → Uses `TemplateActionSet.get_column_dict()`
- `BuildAction.from_template_item()` → Uses `TemplateActionItem.get_column_dict()` for field iteration
- `BuildAction.from_proto()` → Uses `TemplateActionItem.get_column_dict()` for field iteration

## Attachment Handling

### Attachment Reference Model

**TemplateBuilderAttachmentReference** table tracks attachments uploaded during template building:
- Links attachments to builders via `template_builder_memory_id`
- Stores attachment level (`action_set` or `action`) and action index
- Preserves attachment metadata (description, sequence_order, is_required)
- Allows attachments to persist even if builder is deleted/canceled
- Future: Can be used by attachment reference manager for cleanup/orphan detection

### Attachment Wrapper Classes

**BuildAttachment** wrapper:
- Wraps attachment reference data (attachment_id, description, sequence_order, etc.)
- Validates against `TemplateActionSetAttachment.get_column_dict()` or `TemplateActionAttachment.get_column_dict()`
- Methods: getters/setters for attachment fields

### Attachment Management in Builder

**Action-Set Level Attachments**:
- Stored in `TemplateBuilderContext._build_attachments: List[BuildAttachment]`
- Methods: `add_attachment_to_action_set(attachment_data)`, `remove_attachment_from_action_set(index)`
- When added: Creates `TemplateBuilderAttachmentReference` record with `attachment_level='action_set'`
- Stored in build state JSON under `metadata.attachments`

**Action Level Attachments**:
- Stored in each `BuildAction._attachments: List[BuildAttachment]`
- Methods: `BuildAction.add_attachment(attachment_data)`, `BuildAction.remove_attachment(index)`
- When added: Creates `TemplateBuilderAttachmentReference` record with `attachment_level='action'` and `action_index`
- Stored in build state JSON under `actions[].attachments`

### Attachment Copying

When copying from existing template:
- Action-set attachments: Copied to `_build_attachments` with attachment reference IDs
- Action attachments: Copied to each `BuildAction._attachments` with attachment reference IDs
- Attachment records themselves are NOT duplicated (references only)
- **NO `TemplateBuilderAttachmentReference` records created** - these attachments already exist in the system, only their IDs are stored in build state JSON

### Attachment Uploading

When user uploads new attachment during building:
- New `Attachment` record created (via existing attachment upload system)
- `TemplateBuilderAttachmentReference` record created to track the new upload
- Attachment reference ID stored in build state JSON
- Allows tracking of attachments that would be orphaned if builder is deleted/canceled

### Attachment Submission

When submitting template:
- Action-set attachments: Create `TemplateActionSetAttachment` records referencing same attachment IDs (both copied and newly uploaded)
- Action attachments: Create `TemplateActionAttachment` records referencing same attachment IDs (both copied and newly uploaded)
- **All `TemplateBuilderAttachmentReference` records for the builder are marked as `is_finalized=True`** (or deleted/archived based on business rules)
- This indicates the attachments have been successfully linked to the production template and no longer need builder-level tracking

## Integration Points

- **Template Creation**: Builder converts to `TemplateActionSet` using existing template creation patterns
- **User Management**: Leverages existing `UserCreatedBase` for user tracking
- **Validation**: Reuses validation logic from existing template structures
- **UI Layer**: Frontend can serialize form data to build state JSON and submit incrementally
- **Attachment System**: Integrates with existing attachment reference system, uses `TemplateBuilderAttachmentReference` for tracking

## Next Steps - Implementation Plan

### Phase 1: Column Dictionary Methods (Current)
- ✅ Add `get_column_dict()` to virtual base classes
- ⏳ Add `get_column_dict()` to template classes with extended fields
- ⏳ Update wrapper classes to use template class methods directly
- ⏳ Remove logic that adds template-specific fields separately

### Phase 2: Attachment Support
- Add `get_column_dict()` to `VirtualAttachmentReference`
- Add `get_column_dict()` to `TemplateActionSetAttachment`
- Add `get_column_dict()` to `TemplateActionAttachment`
- Create `TemplateBuilderAttachmentReference` data model
- Create `BuildAttachment` wrapper class
- Add attachment methods to `BuildAction` wrapper
- Add attachment methods to `TemplateBuilderContext`
- Update build state JSON structure to include attachments
- Update submission logic to create attachment references

### Phase 3: Portal Enhancement (Search Infrastructure)
- Build search infrastructure for proto actions
- Build search infrastructure for template actions
- Add search UI to template builder portal
- Implement browse/select interfaces

### Phase 4: Advanced Features
- Attachment reference manager for cleanup
- Template builder versioning/history
- Bulk operations (copy multiple actions, etc.)


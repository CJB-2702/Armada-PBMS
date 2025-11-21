# Maintenance Structure Planning Document

## Purpose

This document defines **how the maintenance data structure SHOULD be** to enable a full model rebuild of maintenance data, business services, and presentation layers. This is a **planning document** focused on the desired state, not a description of the current implementation.

The goal is to establish clear, consistent patterns that will guide the rebuild of:
- **Data Layer**: Database models and relationships
- **Business Layer**: Context managers, factories, and business logic
- **Presentation Layer**: Routes, services, and UI components

---

## Core Design Principles

### 1. Three-Tier Hierarchy
The maintenance system uses three parallel structures that work together:
- **Base Items** (`base/`): Actual maintenance work executed by workers
- **Template Items** (`templates/`): Blueprints created by supervisors
- **Proto Templates** (`proto_templates/`): Reusable library of generic actions

### 2. Copy vs Reference Pattern
- **Action Sets and Actions**: Copied with **reference** to source (traceability)
- **Parts, Tools**: **Copied without reference** (standalone, allows real-world substitution)
- **Attachments**: Templates have direct attachment tables; base/maintenance use Event comments
- **Rationale**: Parts/tools can be substituted during execution; traceability maintained via parent action. Attachments follow different patterns: templates need direct support for reference documentation, while base/maintenance use Event comments for execution documentation.

### 3. Event Coupling
- **Base Items**: Tightly coupled to `Event` (real work has event_id)
- **Template Items**: NO event coupling (templates are blueprints, not real work)
- **Proto Items**: NO event coupling (library items, not work)

### 4. Sequence Order Flow
- **TemplateActionSet**: NO `sequence_order` (standalone templates, can be used in any order)
- **TemplateActionItem**: Have `sequence_order` (defines order within template action set)
- **Base**: Copy `sequence_order` from template action items when creating maintenance events
- **Proto**: NO `sequence_order` (standalone library items, not ordered)

### 5. Virtual Base Classes
- Shared fields between base/template/proto go in virtual base classes
- Promotes consistency and reduces duplication
- Examples: `VirtualActionSet`, `VirtualActionItem`, `VirtualPartDemand`, `VirtualActionTool`

---

## Part 1: Data Model (How It SHOULD Be)

The data model consists of **real database tables** with clear foreign key relationships.

### 1.1 Base Items (Actual Maintenance Work)

**Location**: `app/data/maintenance/base/`

**Purpose**: Represent actual maintenance work executed by technicians.

#### `MaintenanceActionSet` (Table: `maintenance_action_sets`)
**Inheritance**: `EventDetailVirtual, VirtualActionSet`

**Purpose**: Container for a maintenance event - holds metadata and links to Event. **Only one MaintenanceActionSet per Event**.

**Key Fields**:
- **Event Coupling**: `event_id` (FK to `events`) - **REQUIRED** - this is real work, **ONE-TO-ONE relationship**
- **Template Reference**: `template_action_set_id` (FK to `template_action_sets`) - nullable, references source template
- **Asset**: `asset_id` (FK to `assets`) - which asset is being maintained
- **Plan**: `maintenance_plan_id` (FK to `maintenance_plans`) - optional, if from scheduled plan
- **From VirtualActionSet**: `task_name`, `description`, `estimated_duration`, `safety_review_required`, `staff_count`, `parts_cost`, `labor_hours`
- **Planning**: `planned_start_datetime` - when maintenance is planned to start (adjustable by planners)
- **Execution Tracking**: `status`, `priority`, `start_date`, `end_date`
- **Assignment**: `assigned_user_id`, `assigned_by_id`, `completed_by_id`
- **Notes**: `completion_notes`, `delay_notes`

**Relationships**:
- Has many `Action` records (ordered by `sequence_order`)
- Belongs to one `Event` (via `event_id`) - **REQUIRED, ONE-TO-ONE**
- References one `TemplateActionSet` (via `template_action_set_id`) - nullable
- Belongs to one `Asset` (via `asset_id`)
- Has many `MaintenanceDelay` records
- **NO direct attachment relationship** - attachments are added via Event comments

**Key Design Decision for Attachments**: MaintenanceActionSet and Action do NOT have direct attachment tables. The expected way to add attachments and information is to leave a comment on the Event with an attachment. Attachments can be added to an Event, providing a unified audit trail and information flow for real maintenance work.

**Key Design Decisions**: 
1. `event_id` is REQUIRED - base items represent real work and must have an Event.
2. **Only ONE MaintenanceActionSet per Event** - maintenance planners can create multiple events with different `planned_start_datetime` instead of multiple action sets on the same event.
3. **NO `sequence_order`** - not needed since only one action set per event.
4. **NO `revision`** - MaintenanceActionSet records what actually happened. The `template_action_set_id` reference points to a specific template revision, providing traceability without needing revision on the base record.

#### `Action` (Table: `actions`)
**Inheritance**: `VirtualActionItem`

**Purpose**: Individual action within a maintenance event.

**Key Fields**:
- **Parent**: `maintenance_action_set_id` (FK to `maintenance_action_sets`) - **REQUIRED**
- **Template Reference**: `template_action_item_id` (FK to `template_actions`) - nullable, references source template action item
- **From VirtualActionItem**: `action_name`, `description`, `estimated_duration`, `expected_billable_hours`, `safety_notes`, `notes`
- **Execution Tracking**: `status`, `scheduled_start_time`, `start_time`, `end_time`, `billable_hours`, `completion_notes`
- **Assignment**: `assigned_user_id`, `assigned_by_id`
- **Ordering**: `sequence_order` - **COPIED from template** when created

**Relationships**:
- Belongs to one `MaintenanceActionSet` (via `maintenance_action_set_id`)
- References one `TemplateActionItem` (via `template_action_item_id`) - nullable
- Has many `PartDemand` records
- Has many `ActionTool` records (when implemented)
- **NO direct attachment relationship** - attachments are added via Event comments

**Key Design Decisions**: 
1. `sequence_order` is copied from template to maintain order.
2. **NO direct attachments** - attachments for actions are added via Event comments, providing unified audit trail for real maintenance work.

#### `PartDemand` (Table: `part_demands`)
**Inheritance**: `VirtualPartDemand`

**Purpose**: Parts required for actions during maintenance execution.

**Key Fields**:
- **Parent**: `action_id` (FK to `actions`) - **REQUIRED**
- **From VirtualPartDemand**: `part_id`, `quantity_required`, `notes`, `expected_cost`
- **Execution Tracking**: `status`, `priority`, `sequence_order`
- **Approval Workflow**: `requested_by_id`, `maintenance_approval_by_id`, `maintenance_approval_date`, `supply_approval_by_id`, `supply_approval_date`

**Relationships**:
- Belongs to one `Action` (via `action_id`)
- References one `Part` (via `part_id`)

**Key Design Decision**: **NO `template_part_demand_id`** - standalone copy. Associated by `part_id`, allows real-world substitution, traceable via parent Action.

#### `ActionTool` (Table: `action_tools`) - **TO BE IMPLEMENTED**
**Inheritance**: `VirtualActionTool` (to be created)

**Purpose**: Tools required for actions during maintenance execution.

**Key Fields**:
- **Parent**: `action_id` (FK to `actions`) - **REQUIRED**
- **From VirtualActionTool**: `tool_id`, `quantity_required`, `notes`
- **Execution Tracking**: `status`, `priority`, `sequence_order`
- **Assignment Tracking**: `assigned_to_user_id`, `assigned_by_id`, `assigned_date`, `returned_date`

**Relationships**:
- Belongs to one `Action` (via `action_id`)
- References one `Tool` (via `tool_id`)

**Key Design Decision**: **NO `template_action_tool_id`** - standalone copy. Same rationale as PartDemand.

#### `MaintenanceDelay` (Table: `maintenance_delays`)
**Purpose**: Delays encountered during maintenance execution.

**Key Fields**:
- `maintenance_action_set_id` (FK to `maintenance_action_sets`)
- `delay_type`, `delay_reason`, `delay_start_date`, `delay_end_date`, `delay_billable_hours`, `delay_notes`, `priority`

#### `MaintenancePlan` (Table: `maintenance_plans`)
**Purpose**: Scheduled maintenance plans that generate maintenance events.

**Key Fields**:
- `name`, `description`, `asset_type_id`, `model_id`, `status`
- `template_action_set_id` (FK to `template_action_sets`) - which template to use
- `frequency_type`, `delta_hours`, `delta_m1`, `delta_m2`, `delta_m3`, `delta_m4`

**Data Model Relationships for Base Items**:
```
Event (core event table)
    ↑ referenced by (REQUIRED, ONE-TO-ONE)
MaintenanceActionSet (holds event_id, planned_start_datetime)
    ↑ referenced by
Action (holds maintenance_action_set_id, sequence_order)
    ↑ referenced by
PartDemand (holds action_id) - NO template reference
ActionTool (holds action_id) - NO template reference
```

---

### 1.2 Template Items (Maintenance Blueprints)

**Location**: `app/data/maintenance/templates/`

**Purpose**: Reusable blueprints created by supervisors to generate maintenance events.

#### `TemplateActionSet` (Table: `template_action_sets`)
**Inheritance**: `VirtualActionSet`

**Purpose**: Template maintenance procedure - container for template actions. Templates can change over time and need versioning for traceability.

**Key Fields**:
- **From VirtualActionSet**: `task_name`, `description`, `estimated_duration`, `safety_review_required`, `staff_count`, `parts_cost`, `labor_hours`
- **Template-Specific**: `revision` (String, nullable) - version number for this template revision
- **Versioning**: `prior_revision_id` (FK to `template_action_sets.id`) - references the previous revision of this template
- **Template Metadata**: `is_active` - whether template is active
- **Plan**: `maintenance_plan_id` (FK to `maintenance_plans`) - optional

**Relationships**:
- Has many `TemplateActionItem` records (ordered by `sequence_order`)
- Referenced by `MaintenanceActionSet` (via `template_action_set_id`)
- Has many `TemplateActionSetAttachment` records - attachments at the template action set level
- References one `TemplateActionSet` (via `prior_revision_id`) - the previous revision
- Referenced by other `TemplateActionSet` (via `prior_revision_id`) - subsequent revisions

**Key Design Decisions**: 
1. **NO `event_id`** - templates are blueprints, not real work.
2. **NO `sequence_order`** - TemplateActionSet is a standalone template meant to be used in any order or event
3. **`revision` and `prior_revision_id`** - Templates can change over time. When a template is edited and a real MaintenanceActionSet references it, a new revision is created to preserve traceability to the original information given to the event.
4. **Template Versioning**: Real events and action sets record what happened. Template versioning allows tracing back to the exact template version that was used when the maintenance event was created. When a template is edited, a new revision is created with `prior_revision_id` pointing to the previous version.

#### `TemplateActionItem` (Table: `template_actions`) - **TO BE RENAMED**
**Current Name**: `ProtoActionItems` (incorrect - should be `TemplateActionItem`)
**Current Table Name**: `template_action_items` (incorrect - should be `template_actions`)

**Inheritance**: `VirtualActionItem`

**Purpose**: Individual template action items within a template action set.

**Key Fields**:
- **Parent**: `template_action_set_id` (FK to `template_action_sets`) - **REQUIRED**
- **Proto Reference**: `proto_action_item_id` (FK to `proto_actions`) - nullable, references source proto action
- **From VirtualActionItem**: `action_name`, `description`, `estimated_duration`, `expected_billable_hours`, `safety_notes`, `notes`
- **Template-Specific**: `is_required`, `instructions`, `instructions_type`, `minimum_staff_count`, `required_skills`
- **Ordering**: `sequence_order` - **REQUIRED** - defines order within template action set
- **Versioning**: `revision`, `prior_revision_id` (FK to `template_actions.id`, nullable) - references previous revision of this template action item

**Relationships**:
- Belongs to one `TemplateActionSet` (via `template_action_set_id`)
- References one `ProtoActionItem` (via `proto_action_item_id`) - nullable
- Referenced by `Action` (via `template_action_item_id`)
- Has many `TemplatePartDemand` records
- Has many `TemplateActionTool` records
- Has many `TemplateActionAttachment` records - attachments at the template action item level

**Key Design Decision**: `sequence_order` is REQUIRED - template action items define ordered procedures within a template action set.

#### `TemplatePartDemand` (Table: `template_part_demands`) 
**Inheritance**: `VirtualPartDemand`

**Purpose**: Parts required for template actions.

**Key Fields**:
- **Parent**: `template_action_item_id` (FK to `template_actions`) - **REQUIRED**
- **From VirtualPartDemand**: `part_id`, `quantity_required`, `notes`, `expected_cost`
- **Template-Specific**: `is_optional`, `sequence_order`

**Relationships**:
- Belongs to one `TemplateActionItem` (via `template_action_item_id`)
- References one `Part` (via `part_id`)

**Key Design Decision**: **NO `proto_part_demand_id`** - standalone copy. Same rationale as base level.

#### `TemplateActionTool` (Table: `template_action_tools`) 
**Inheritance**: `VirtualActionTool` (to be created)

**Purpose**: Tools required for template actions.

**Key Fields**:
- **Parent**: `template_action_item_id` (FK to `template_actions`) - **REQUIRED**
- **From VirtualActionTool**: `tool_id`, `quantity_required`, `notes`
- **Template-Specific**: `is_required`, `sequence_order`

**Relationships**:
- Belongs to one `TemplateActionItem` (via `template_action_item_id`)
- References one `Tool` (via `tool_id`)

**Key Design Decision**: **NO `proto_action_tool_id`** - standalone copy.

#### `TemplateActionSetAttachment` (Table: `template_action_set_attachments`)
**Inheritance**: `VirtualAttachmentReference`

**Purpose**: Attachments for template action sets. Some information and attachments are not directly linked to any individual action but are related to the template action set as a whole.

**Key Fields**:
- **From VirtualAttachmentReference**: `attachment_id` (FK to `attachments`), `all_attachment_references_id`, `attached_to_type`, `display_order`, `attachment_type`, `caption`
- `template_action_set_id` (FK to `template_action_sets`) - **REQUIRED** - direct reference to template action set (serves as `attached_to_id`)
- `description` (Text, nullable) - description of the attachment
- `sequence_order` (Integer, default=1) - order of attachments
- `is_required` (Boolean, default=False) - whether attachment is required

**Relationships**:
- Belongs to one `TemplateActionSet` (via `template_action_set_id`)

**Key Design Decision**: Template action sets need direct attachment support because some information (e.g., overall procedure diagrams, safety documentation, general notes) applies to the entire template, not individual actions.

#### `TemplateActionAttachment` (Table: `template_action_attachments`)
**Inheritance**: `VirtualAttachmentReference`

**Purpose**: Attachments for individual template action items. Some information or attachments are related directly to a specific action.

**Key Fields**:
- **From VirtualAttachmentReference**: `attachment_id` (FK to `attachments`), `all_attachment_references_id`, `attached_to_type`, `display_order`, `attachment_type`, `caption`
- `template_action_item_id` (FK to `template_actions`) - **REQUIRED** - direct reference to template action item (serves as `attached_to_id`)
- `description` (Text, nullable) - description of the attachment
- `sequence_order` (Integer, default=1) - order of attachments within the action
- `is_required` (Boolean, default=False) - whether attachment is required

**Relationships**:
- Belongs to one `TemplateActionItem` (via `template_action_item_id`)

**Key Design Decision**: Template action items need direct attachment support for action-specific documentation, diagrams, or instructions.

**Data Model Relationships for Template Items**:
```
TemplateActionSet (template action set - real table, NO sequence_order)
    ↑ referenced by
TemplateActionItem (holds template_action_set_id, has sequence_order)
    ↑ referenced by
TemplatePartDemand (holds template_action_item_id) - NO proto reference
TemplateActionTool (holds template_action_item_id) - NO proto reference
TemplateActionAttachment (holds template_action_item_id) - action-level attachments
TemplateActionSetAttachment (holds template_action_set_id) - action set-level attachments
```

---

### 1.3 Proto Templates (Generic Reusable Actions)

**Location**: `app/data/maintenance/proto_templates/`

**Purpose**: Reusable library of generic action definitions that can be referenced by templates.

#### `ProtoActionItem` (Table: `proto_actions`) - **TO BE RENAMED**
**Current Name**: `ProtoActionItems` (should be singular `ProtoActionItem`)
**Current Table Name**: `proto_action_items` (should be plural `proto_actions`)

**Inheritance**: `VirtualActionItem`

**Purpose**: Generic, reusable action definition - standalone library item.

**Key Fields**:
- **From VirtualActionItem**: `action_name`, `description`, `estimated_duration`, `expected_billable_hours`, `safety_notes`, `notes`
- **Proto-Specific**: `is_required`, `instructions`, `instructions_type`, `minimum_staff_count`, `required_skills`
- **Versioning**: `revision`, `prior_revision_id` (FK to `proto_actions.id`, nullable) - references previous revision of this proto action item

**Relationships**:
- Referenced by `TemplateActionItem` (via `proto_action_item_id`)
- Has many `ProtoPartDemand` records (if needed for library)
- Has many `ProtoActionTool` records (if needed for library)
- Has many `ProtoActionAttachment` records

**Key Design Decisions**:
1. **NO `template_action_set_id`** - proto items are standalone, not in sets
2. **NO `sequence_order`** - proto items are library items, not ordered
3. **NO references to other maintenance entities** - proto is the "leaf" in dependency tree

#### `ProtoPartDemand` (Table: `proto_part_demands`) - **TO BE IMPLEMENTED**
**Purpose**: Generic part requirements that can be referenced by templates.

**Key Fields**:
- **Parent**: `proto_action_item_id` (FK to `proto_actions`) - **REQUIRED**
- **From VirtualPartDemand**: `part_id`, `quantity_required`, `notes`, `expected_cost`
- **Proto-Specific**: `is_optional`, `sequence_order`

**Relationships**:
- Belongs to one `ProtoActionItem` (via `proto_action_item_id`)
- References one `Part` (via `part_id`)

**Key Design Decision**: Optional - templates can copy from proto or define independently. When used, parts belong to specific proto action items.

#### `ProtoActionTool` (Table: `proto_action_tools`) - **TO BE IMPLEMENTED**
**Purpose**: Generic tool requirements that can be referenced by templates.

**Key Fields**:
- **Parent**: `proto_action_item_id` (FK to `proto_actions`) - **REQUIRED**
- **From VirtualActionTool**: `tool_id`, `quantity_required`, `notes`
- **Proto-Specific**: `is_required`, `sequence_order`

**Relationships**:
- Belongs to one `ProtoActionItem` (via `proto_action_item_id`)
- References one `Tool` (via `tool_id`)

**Key Design Decision**: Optional - templates can copy from proto or define independently. When used, tools belong to specific proto action items.

---

### 1.4 Virtual Base Classes

**Location**: `app/data/maintenance/`

#### `VirtualActionSet` (Abstract)
**Inheritance**: `UserCreatedBase`

**Purpose**: Shared fields for action sets (MaintenanceActionSet, TemplateActionSet).

**Fields**:
- `task_name` (String, required)
- `description` (Text, nullable)
- `estimated_duration` (Float, nullable) - in hours
- `safety_review_required` (Boolean, default=False)
- `staff_count` (Integer, nullable)
- `parts_cost` (Float, nullable)
- `labor_hours` (Float, nullable)

**Notes**: 
1. Does NOT include `sequence_order` - TemplateActionSet is a standalone template that can be used in any order. Only TemplateActionItem (within a set) have sequence_order.
2. Does NOT include `revision` - revision is only for TemplateActionSet to track template versioning over time. MaintenanceActionSet records what actually happened and doesn't need revision tracking.

#### `VirtualActionItem` (Abstract)
**Inheritance**: `UserCreatedBase`

**Purpose**: Shared fields for actions (Action, TemplateActionItem, ProtoActionItem).

**Fields**:
- `action_name` (String, required)
- `description` (Text, nullable)
- `estimated_duration` (Float, nullable) - in hours
- `expected_billable_hours` (Float, nullable)
- `safety_notes` (Text, nullable)
- `notes` (Text, nullable)

#### `VirtualPartDemand` (Abstract)
**Inheritance**: `UserCreatedBase`

**Purpose**: Shared fields for part demands (PartDemand, TemplatePartDemand, ProtoPartDemand).

**Fields**:
- `part_id` (FK to `parts`, required)
- `quantity_required` (Float, required, default=1.0)
- `notes` (Text, nullable)
- `expected_cost` (Float, nullable)

#### `VirtualActionTool` (Abstract) - **TO BE CREATED**
**Inheritance**: `UserCreatedBase`

**Purpose**: Shared fields for tool requirements (ActionTool, TemplateActionTool, ProtoActionTool).

**Fields**:
- `tool_id` (FK to `tools`, required)
- `quantity_required` (Integer, default=1)
- `notes` (Text, nullable)

---

### 1.5 Data Flow: Creating Templates from Proto Actions

**Process**: Proto → Template (supervisor creates maintenance procedure templates)

1. **Create `TemplateActionSet`**:
   - Supervisor defines a new maintenance procedure template
   - Set `task_name`, `description`, `estimated_duration`, etc. from `VirtualActionSet` fields
   - Set `revision` (e.g., "1.0") and `prior_revision_id` to NULL for initial version
   - Set `is_active=True`
   - **NO `proto_action_set_id`** - TemplateActionSet is standalone, not directly derived from proto
   - **NO `sequence_order`** - TemplateActionSet is a standalone template that can be used in any order
   - **Note**: TemplateActionSet can be created from scratch or by copying from existing templates

2. **Create `TemplateActionItem` records**:
   - For each action in the maintenance procedure:
     - Supervisor can reference a `ProtoActionItem` from the library OR create a custom action
     - If referencing proto: Set `proto_action_item_id` to reference the specific `ProtoActionItem`
     - Copy action details from `ProtoActionItem` if referenced (action_name, description, estimated_duration, etc.)
     - OR define custom action details directly
     - Set `template_action_set_id` to reference the `TemplateActionSet` **REQUIRED**
     - **Set `sequence_order`** - **REQUIRED** - defines the order of actions within this template
     - Set template-specific fields (is_required, instructions, minimum_staff_count, etc.)
     - **Template Versioning**: Set `revision` and `prior_revision_id` if creating a new revision of an existing template action item

3. **Create `TemplatePartDemand` records** (optional):
   - For each part requirement:
     - Supervisor can reference `ProtoPartDemand` from the proto action item OR define independently
     - **Copy data** from `ProtoPartDemand` if referenced (part_id, quantity_required, notes, expected_cost)
     - **Do NOT create foreign key** to `proto_part_demand_id` - standalone copy
     - Set `template_action_item_id` to reference the `TemplateActionItem`
     - Set template-specific fields (is_optional, sequence_order)
     - **Rationale**: Allows real-world substitution and template-specific customization

4. **Create `TemplateActionTool` records** (optional):
   - For each tool requirement:
     - Supervisor can reference `ProtoActionTool` from the proto action item OR define independently
     - **Copy data** from `ProtoActionTool` if referenced (tool_id, quantity_required, notes)
     - **Do NOT create foreign key** to `proto_action_tool_id` - standalone copy
     - Set `template_action_item_id` to reference the `TemplateActionItem`
     - Set template-specific fields (is_required, sequence_order)
     - **Rationale**: Allows real-world substitution and template-specific customization

5. **Create `TemplateActionSetAttachment` and `TemplateActionAttachment` records** (optional):
   - Add attachments at the template action set level for overall procedure documentation
   - Add attachments at the template action item level for action-specific documentation
   - **Do NOT copy from proto attachments** - templates define their own reference documentation
   - Template attachments remain in templates for reference when creating maintenance events

**Key Design Decisions**:
- **TemplateActionItem reference ProtoActionItem**: Provides traceability to the reusable library while allowing template-specific customization
- **Parts and Tools are standalone copies**: NO foreign keys to proto parts/tools, allowing template-specific modifications and real-world substitutions
- **Sequence order is set at template level**: TemplateActionItem defines the ordered procedure within a TemplateActionSet
- **Templates can mix proto and custom**: Supervisors can reference proto actions, define custom actions, or combine both in a single template

---

### 1.6 Data Flow: Creating Maintenance from Templates

**Process**: Template → Base (with Event creation)

1. **Create `MaintenanceActionSet`**:
   - Copy metadata from `TemplateActionSet` (task_name, description, estimated_duration, etc.)
   - Set `template_action_set_id` to reference the specific `TemplateActionSet` revision
   - **Create and link to an Event** via `event_id` - **REQUIRED, ONE-TO-ONE**
   - Set `asset_id`, `planned_start_datetime`, `status='Planned'`
   - **Note**: Only one MaintenanceActionSet per Event - planners create multiple events for different planned start times
   - **Template Versioning**: The `template_action_set_id` reference is frozen at creation time. If the template is later edited (creating a new revision), existing MaintenanceActionSet records continue to reference the original template revision, preserving traceability to what was actually used.

2. **Create `Action` records**:
   - For each `TemplateActionItem` in the `TemplateActionSet`:
     - Copy action details (action_name, description, estimated_duration, etc.)
     - Set `template_action_item_id` to reference `TemplateActionItem`
     - Set `maintenance_action_set_id` to reference `MaintenanceActionSet`
     - **Copy `sequence_order`** from template action item
     - Set `status='Not Started'`

3. **Create `PartDemand` records**:
   - For each `TemplatePartDemand` associated with template action items:
     - **Copy data** (part_id, quantity_required, notes, etc.)
     - **Do NOT create foreign key** to template part demand
     - Set `action_id` to reference base `Action`
     - Standalone copy, associated by `part_id`

4. **Create `ActionTool` records** (when implemented):
   - For each `TemplateActionTool` associated with template action items:
     - **Copy data** (tool_id, quantity_required, notes, etc.)
     - **Do NOT create foreign key** to template action tool
     - Set `action_id` to reference base `Action`
     - Standalone copy, associated by `tool_id`

5. **Attachments**:
   - **Do NOT copy template attachments** to base/maintenance items
   - Template attachments (`TemplateActionSetAttachment`, `TemplateActionAttachment`) remain in templates for reference
   - For base/maintenance items, attachments are added via Event comments
   - This provides unified audit trail and execution documentation for real maintenance work

---

### 1.7 Data Model Summary Table

| Table | References Action Set? | References Template? | References Event? | Has Sequence Order? | Notes |
|-------|----------------------|---------------------|------------------|---------------------|-------|
| `MaintenanceActionSet` | N/A | ✅ Yes (`template_action_set_id`) | ✅ Yes (`event_id`) **REQUIRED, ONE-TO-ONE** | ❌ No | Real work, tightly coupled to Event, only one per event |
| `Action` | ✅ Yes (`maintenance_action_set_id`) | ✅ Yes (`template_action_item_id`) | ❌ No (via MaintenanceActionSet) | ✅ Yes (copied from template) | Belongs to action set |
| `PartDemand` | ❌ No | ❌ No | ❌ No | ✅ Yes | Standalone copy, NO template reference |
| `ActionTool` | ❌ No | ❌ No | ❌ No | ✅ Yes | **TO BE IMPLEMENTED** - Standalone copy |
| `TemplateActionSet` | N/A | N/A | ❌ No | ❌ No | Template blueprint, NO Event, NO sequence_order |
| `TemplateActionItem` | ✅ Yes (`template_action_set_id`) | ✅ Yes (`proto_action_item_id`) | ❌ No | ✅ Yes **REQUIRED** | Ordered within template action set |
| `TemplatePartDemand` | ❌ No | ✅ Yes (`template_action_item_id`) | ❌ No | ✅ Yes | Standalone copy, NO proto reference |
| `TemplateActionTool` | ❌ No | ✅ Yes (`template_action_item_id`) | ❌ No | ✅ Yes | Standalone copy, NO proto reference |
| `TemplateActionSetAttachment` | ❌ No | ✅ Yes (`template_action_set_id`) | ❌ No | ✅ Yes | Direct attachment for template action set |
| `TemplateActionAttachment` | ❌ No | ✅ Yes (`template_action_item_id`) | ❌ No | ✅ Yes | Direct attachment for template action item |
| `ProtoActionItem` | ❌ No | N/A | ❌ No | ❌ No | Standalone library item, NO set membership |
| `ProtoPartDemand` | ❌ No | ✅ Yes (`proto_action_item_id`) | ❌ No | ✅ Yes | **OPTIONAL** - Generic part requirements for proto actions |
| `ProtoActionTool` | ❌ No | ✅ Yes (`proto_action_item_id`) | ❌ No | ✅ Yes | **OPTIONAL** - Generic tool requirements for proto actions |

---

## Part 2: Business Model (How It SHOULD Be)

The business model provides **abstraction classes** that wrap data models to provide business logic and convenient access patterns.

### 2.1 Business Layer Wrappers

#### `MaintenanceEventStruct` (Business Wrapper)
**Location**: `app/data/maintenance/base/maintenance_event.py`

**Purpose**: Data wrapper around `MaintenanceActionSet` for convenient access.

**Wraps**: `MaintenanceActionSet` (the real table)

**NOT a database table** - provides cached access and convenience methods.

**Provides**:
- Cached access to actions, part demands, event
- Data access properties (status, planned_start_datetime, asset_id, etc.)
- Basic creation methods (`from_id`, `from_event_id`)
- Simple data access - **NO business logic**

**For business logic**: Use `MaintenanceContext` in `app/buisness/maintenance/maintenance_context`

#### `TemplateMaintenanceEventStruct` (Business Wrapper)
**Location**: `app/data/maintenance/templates/template_maintenance_event.py`

**Purpose**: Data wrapper around `TemplateActionSet` for convenient access.

**Wraps**: `TemplateActionSet` (the real table)

**NOT a database table** - provides cached access and convenience methods.

**Provides**:
- Cached access to template action items, part demands, tools, action set attachments, action attachments
- Data access properties (revision, estimated_duration, safety_review_required, etc.)
- Basic creation methods (`from_id`, `from_task_name`)
- Simple data access - **NO business logic**

**For business logic**: Use `TemplateMaintenanceContext` in `app/buisness/maintenance/template_maintenance_context`

---

### 2.2 Business Layer Context Classes

**Location**: `app/buisness/maintenance/`

#### `MaintenanceContext` (Business Logic)
**Wraps**: `MaintenanceEventStruct` (which wraps `MaintenanceActionSet`)

**Purpose**: Business logic context manager for maintenance events.

**Provides**:
- **Management methods**: `start()`, `complete()`, `cancel()`, `add_comment()`, `delay()`
- **Attachment management**: Add attachments via Event comments (not direct attachment tables)
- **Statistics**: `total_actions`, `completed_actions`, `completion_percentage`, `total_part_demands`
- **Query methods**: `get_all()`, `get_by_status()`, `get_by_asset()`, `get_by_user()`
- **Serialization**: `to_dict()`
- **Business rules**: Validation, state transitions, workflow management

#### `TemplateMaintenanceContext` (Business Logic)
**Wraps**: `TemplateMaintenanceEventStruct` (which wraps `TemplateActionSet`)

**Purpose**: Business logic context manager for template maintenance events.

**Provides**:
- **Statistics**: `total_action_items`, `total_estimated_duration`, `total_estimated_cost`
- **Grouping methods**: `get_part_demands_by_action()`, `get_tools_by_action()`
- **Attachment access**: `get_action_set_attachments()`, `get_action_attachments()` - direct attachment support for templates
- **Query methods**: `get_all()`, `get_active()`, `get_by_task_name()`
- **Serialization**: `to_dict()`, `summary()`
- **Template management**: Create from proto, versioning, activation

#### `ActionContext` (Business Logic)
**Wraps**: `Action` data table

**Purpose**: Business logic context manager for individual actions.

**Provides**:
- Action lifecycle management
- Statistics and completion tracking
- Part demand and tool management

#### `MaintenancePlanContext` (Business Logic)
**Wraps**: `MaintenancePlan` data table

**Purpose**: Business logic context manager for maintenance plans.

**Provides**:
- Plan scheduling and frequency management
- Template assignment
- Asset type and model matching
- Maintnence Event Creation

---

### 2.3 Business Layer Factories

**Location**: `app/buisness/maintenance/factories/`

#### `MaintenanceActionSetFactory`
**Purpose**: Create `MaintenanceActionSetStruct` from `TemplateActionSet`.

**Responsibilities**:
- Copy metadata from template
- Create and link Event (ONE-TO-ONE relationship)
- Set up relationships (asset, plan)
- Initialize status and `planned_start_datetime`
- **Ensure only one MaintenanceActionSet per Event**

#### `ActionFactory`
**Purpose**: Create `Action` records from `TemplateActionItem` records.

**Responsibilities**:
- Copy action details from template
- Copy `sequence_order` from template
- Set up relationships (action set, template reference)
- Initialize status
- Create `PartDemand` records from `TemplateActionItem`'s `TemplatePartDemand` records and associate to action
- Create `ActionTool` records from `TemplateActionItem`'s `TemplateActionTool` records and associate to action


#### `MaintenanceFactory`
**Purpose**: Main factory for creating complete maintenance workflows from templates.

**Responsibilities**:
- Coordinate all factories
- Create complete maintenance event with all actions, parts, tools
- Handle transaction management
- Validate business rules

---

### 2.4 Business Model Layer Structure

```
Business Layer (app/buisness/maintenance/)
    ↓ uses
Data Layer Wrappers (app/data/maintenance/)
    MaintenanceEventStruct → wraps → MaintenanceActionSet (real table)
    TemplateMaintenanceEventStruct → wraps → TemplateActionSet (real table)
    ↓ wraps
Data Layer Tables (real database tables)
    MaintenanceActionSet, Action, PartDemand, ActionTool
    TemplateActionSet, TemplateActionItem, TemplatePartDemand, TemplateActionTool, TemplateActionSetAttachment, TemplateActionAttachment
    ProtoActionItem, ProtoPartDemand, ProtoActionTool
```

---

## Part 3: Presentation Layer (How It SHOULD Be)

**Location**: `app/presentation/routes/maintenance/`

### 3.1 Layer Responsibilities

**Presentation Layer** should:
- Handle HTTP requests and responses
- Render templates with data
- Delegate business logic to business layer
- Use services for complex data retrieval
- Be **thin** - minimal logic in routes

### 3.2 Route Organization

**Should follow parallel structure**:
```
app/presentation/routes/maintenance/
├── base/              # Base maintenance routes
│   ├── events.py      # Maintenance events (MaintenanceActionSet)
│   ├── actions.py     # Individual actions
│   ├── part_demands.py
│   └── delays.py
├── templates/         # Template management routes
│   ├── action_sets.py # TemplateActionSet
│   ├── action_items.py # TemplateActionItem
│   ├── part_demands.py
│   └── tools.py
├── proto/             # Proto library routes (if needed)
│   └── actions.py
├── plans/             # Maintenance plan routes
│   └── plans.py
├── technician/        # Technician portal
│   ├── dashboard.py
│   ├── work.py
│   └── history.py
├── manager/           # Manager portal
│   ├── dashboard.py
│   ├── templates.py
│   └── assignments.py
└── fleet/             # Fleet/Admin portal
    ├── dashboard.py
    └── analytics.py
```

### 3.3 Services Layer

**Location**: `app/services/maintenance/`

**Purpose**: Presentation-specific services for complex data retrieval and formatting.

**Should provide**:
- Query services for filtered lists
- Statistics and aggregation services
- Form option builders
- Data formatting and serialization for UI
- Pagination and sorting helpers

**Examples**:
- `MaintenanceEventService.get_by_filters()`
- `MaintenanceStatisticsService.get_dashboard_stats()`
- `TemplateService.get_active_templates()`

---

## Part 4: Key Design Decisions and Rationale

### 4.1 Why Parts/Tools Don't Have Direct Template References

**Decision**: `PartDemand` and `ActionTool` have **NO** `template_part_demand_id` or `template_action_tool_id` fields.

**Rationale**:
1. **Real-World Substitution**: Workers may use different parts/tools than specified
2. **Association by ID**: Can be associated by `part_id`/`tool_id` with template versions
3. **Traceability Through Parent**: Traceable via `Action.template_action_item_id` → `TemplateActionItem`
4. **Independent Modification**: Base part demands can be modified during execution
5. **Execution Tracking**: Base level needs execution-specific fields (status, approval workflow) that templates don't have

**Same logic applies** at Template → Proto level: `TemplatePartDemand` has NO `proto_part_demand_id`.

### 4.2 Why Actions Reference Templates (Not Proto)

**Decision**: `Action` references `TemplateActionItem` via `template_action_item_id`, NOT `proto_action_item_id`.

**Rationale**:
1. **Template is the Blueprint**: The template is what was actually used to create the maintenance event
2. **Supervisor Customization**: Templates may have been customized from proto by supervisors
3. **Traceability Chain**: Base → TemplateActionItem → ProtoActionItem (never Base → Proto directly)
4. **Versioning**: Template versioning is what matters for maintenance events, not proto versioning

### 4.3 Why Proto Has No Set Membership

**Decision**: `ProtoActionItem` has **NO** `template_action_set_id` or `sequence_order`.

**Rationale**:
1. **Library Items**: Proto items are standalone, reusable library items
2. **Multiple Usage**: Same proto action can be used in multiple different templates
3. **No Ordering**: Order is defined at template level, not proto level
4. **Flexibility**: Templates can pick and choose which proto items to use and in what order

### 4.4 Why TemplateActionItem Have Sequence Order

**Decision**: `TemplateActionItem` has `sequence_order` (REQUIRED), but `TemplateActionSet` does NOT have `sequence_order`.

**Rationale**:
1. **Ordered Procedures**: TemplateActionItem defines ordered maintenance procedures within a template action set
2. **Copy to Base**: Sequence order is copied to base actions when creating maintenance events
3. **Supervisor Control**: Supervisors define the order of operations in template action items
4. **Workflow Definition**: TemplateActionItem is a workflow definition within a set
5. **TemplateActionSet is Standalone**: TemplateActionSet is a standalone template that can be used in any order or event, so it doesn't need sequence_order

### 4.5 Why TemplateActionSet Have Revision (But MaintenanceActionSet Does Not)

**Decision**: `TemplateActionSet` has `revision` and `prior_revision_id`, but `MaintenanceActionSet` does NOT have `revision`.

**Rationale**:
1. **Real Events Record What Happened**: MaintenanceActionSet records what actually happened during maintenance execution. It doesn't need revision tracking because it's a historical record.
2. **Templates Change Over Time**: Templates are living documents that supervisors edit to improve procedures. They need versioning to track changes.
3. **Traceability**: When a MaintenanceActionSet is created from a TemplateActionSet, the `template_action_set_id` reference is frozen to that specific template revision. This preserves traceability to the exact template version that was used.
4. **Template Editing Creates New Revisions**: When a template is edited and a real MaintenanceActionSet references it, a new revision is created with `prior_revision_id` pointing to the previous version. Existing MaintenanceActionSet records continue to reference the original revision.
5. **Historical Accuracy**: This ensures that maintenance events always reference the exact template information that was available when the event was created, not the current (possibly changed) template version.

### 4.6 Why Base Items Require Event (One-to-One)

**Decision**: `MaintenanceActionSet` has `event_id` (REQUIRED, ONE-TO-ONE), `TemplateActionSet` has NO `event_id`.

**Rationale**:
1. **Real Work**: Base items represent actual maintenance work that happened
2. **Audit Trail**: Events provide audit trail and timeline
3. **Templates are Blueprints**: Templates are not real work, so no event needed
4. **Event System Integration**: Base maintenance integrates with core event system
5. **One MaintenanceActionSet Per Event**: Only one MaintenanceActionSet per Event - maintenance planners create multiple events with different `planned_start_datetime` instead of multiple action sets on the same event
6. **Planning Flexibility**: Planners can adjust `planned_start_datetime` on individual events rather than managing sequence_order across multiple action sets

### 4.7 Why Templates Have Direct Attachments But Base Items Use Event Comments

**Decision**: `TemplateActionSet` and `TemplateActionItem` have direct attachment tables (`TemplateActionSetAttachment`, `TemplateActionAttachment`), but `MaintenanceActionSet` and `Action` do NOT have direct attachment tables.

**Rationale**:
1. **Templates Need Direct Attachments**: Some information and attachments are not directly linked to any individual action but are related to the template action set as a whole (e.g., overall procedure diagrams, safety documentation, general notes). Some attachments are related directly to specific action items (e.g., action-specific diagrams, instructions).
2. **Templates Have No Event**: Templates are blueprints without events, so they need direct attachment support for documentation and reference materials.
3. **Base Items Use Event Comments**: For `MaintenanceActionSet` and `Action`, the expected way to add attachments and information is to leave a comment on the Event with an attachment. Attachments can be added to an Event.
4. **Unified Audit Trail**: Using Event comments for base/maintenance attachments provides a unified audit trail and information flow for real maintenance work, with timestamps, user attribution, and chronological ordering.
5. **Event Integration**: This leverages the existing Event system's comment and attachment capabilities, avoiding duplication and ensuring consistency with other event-based workflows.
6. **Separation of Concerns**: Templates store reference documentation; Events store execution documentation and real-world information gathered during maintenance.

---

## Part 5: Naming Conventions (How They SHOULD Be)
file name should be lowercase snake case plural
class name should be PascalCase singular

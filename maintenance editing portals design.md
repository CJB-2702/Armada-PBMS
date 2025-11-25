# Maintenance Editing Portals Design

## Overview
This document outlines the design for add and edit pages for Maintenance Event Templates (TemplateActionSet) and Proto Actions (ProtoActionItem). These portals enable supervisors to create and modify reusable maintenance templates and action prototypes.

## Current State Review

### Existing Templates
- **TemplateActionSet**: Has comprehensive view page (`view_maintenance_template.html`) and simple list/detail pages. Missing add/edit pages.
- **ProtoActionItem**: Has comprehensive view page (`view_proto_action.html`). Missing add/edit pages and list page.

### Key Differences
- **TemplateActionSet**: Container for multiple template actions, has revision tracking, can be linked to maintenance plans and asset types. NO sequence_order (standalone templates).
- **ProtoActionItem**: Standalone library item, referenced by template actions. NO template_action_set_id or sequence_order (library items are independent).

## Design Requirements

### TemplateActionSet Add/Edit Pages

**Purpose**: Create and edit maintenance template containers that define complete maintenance procedures.

**Fields to Edit**:
- **Core Fields** (from VirtualActionSet): task_name (required), description, estimated_duration (hours), safety_review_required (checkbox), staff_count, parts_cost, labor_hours
- **Template Metadata**: revision (string), is_active (checkbox), maintenance_plan_id (dropdown), asset_type_id (dropdown), make_model_id (dropdown)
- **Versioning**: prior_revision_id (dropdown, disabled for new, read-only for edits)

**Workflow**:
- **Add Page**: Form to create new template. Action items are added separately via template builder or management interface after creation.
- **Edit Page**: Form to edit existing template metadata. Versioning fields should be read-only (revision tracking is managed separately).
- **Navigation**: Save button returns to view page. Cancel button returns to list/view page.

**UI Considerations**:
- Use standard form layout with sections for core fields, metadata, and relationships.
- Dropdowns for foreign keys should allow "None" option for optional relationships.
- Revision field should be auto-calculated for new templates or disabled for existing (versioning handled separately).

### ProtoActionItem Add/Edit Pages

**Purpose**: Create and edit reusable action prototypes that can be referenced by template actions.

**Fields to Edit**:
- **Core Fields** (from VirtualActionItem): action_name (required), description, estimated_duration (hours), expected_billable_hours, safety_notes (textarea), notes (textarea)
- **Proto-Specific**: is_required (checkbox), instructions (textarea), instructions_type (dropdown/text), minimum_staff_count (integer, default 1), required_skills (textarea)
- **Versioning**: revision (string), prior_revision_id (dropdown, disabled for new, read-only for edits)

**Workflow**:
- **Add Page**: Form to create new proto action. Parts, tools, and attachments are managed separately after creation.
- **Edit Page**: Form to edit existing proto action. Versioning fields should be read-only.
- **Navigation**: Save button returns to view page. Cancel button returns to list (to be created) or view page.

**UI Considerations**:
- Use form layout with sections for core action fields, proto-specific fields, and versioning.
- Textarea fields for instructions, safety_notes, and required_skills should be appropriately sized.
- Minimum_staff_count should default to 1 and have validation (min 1).

## Common Patterns

**Form Structure**:
- Use standard Bootstrap form layout with clear field groupings
- Required fields marked with asterisk (*)
- Help text for complex fields (e.g., revision tracking)
- HTMX for form submission with proper loading indicators
- Client-side validation for required fields and data types

**Navigation Flow**:
- Add: List/Index → Add Form → Save → View Page
- Edit: View/List → Edit Form → Save → View Page
- Cancel: Any form → Previous page (maintain navigation context)

**Access Control**:
- Both portals should require supervisor/manager role permissions
- Versioning changes should be restricted (create new revision workflow separate from direct edits)

## Implementation Notes

- Follow existing template patterns (similar to maintenance_plans create/edit pages)
- Use HTMX for form submissions to enable partial page updates
- Integrate with existing business layer context managers for data validation
- Ensure proper error handling and user feedback for validation failures
- Consider wizard-style interface for complex templates with many action items (future enhancement)


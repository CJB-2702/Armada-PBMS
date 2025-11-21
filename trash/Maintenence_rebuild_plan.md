### 5.1 Current Naming Issues

**Issues to Fix**:
1. `ProtoActionItems` (plural) → Should be `ProtoAction` (singular)
2. `ProtoActionItems` is currently used for what should be `TemplateActionItems`
3. `TemplateActions` → Should be `TemplateActionSets` for clarity
4. Inconsistent naming between base/template/proto levels

### 5.2 Desired Naming

**Base Level** (actual work):
- `MaintenanceActionSet` ✅
- `Action` ✅
- `PartDemand` ✅
- `ActionTool` ✅

**Template Level** (blueprints):
- `TemplateActions` → **RENAME to** `TemplateActionSets` (plural, standalone templates)
- `ProtoActionItems` → **RENAME to** `TemplateActionItems` (plural, items within a set)
- `TemplatePartDemand` ✅
- `TemplateActionTool` ✅

**Proto Level** (library):
- `ProtoActionItems` → **RENAME to** `ProtoAction` (singular)
- `ProtoPartDemand` ✅
- `ProtoActionTool` ✅

---


## Part 6: Implementation Priorities

### 6.1 Phase 1: Data Model Rebuild
1. Create `VirtualActionSet` with correct fields (NO `sequence_order`, NO `revision`)
2. Create `VirtualActionTool` base class
3. Rename `TemplateActions` → `TemplateActionSets` (in templates/)
4. Rename `ProtoActionItems` → `TemplateActionItems` (in templates/)
5. Remove `sequence_order` from `TemplateActionSets` (standalone templates)
6. Remove `sequence_order` from `MaintenanceActionSet` (only one per event)
7. Remove `revision` from `VirtualActionSet` and `MaintenanceActionSet`
8. Add `revision` and `prior_revision_id` to `TemplateActionSets` only
9. Add `planned_start_datetime` to `MaintenanceActionSet` (replaces `scheduled_date`)
10. Enforce ONE-TO-ONE relationship between `Event` and `MaintenanceActionSet`
11. Create new `ProtoActionItem` (in proto_templates/) without `template_action_set_id`
12. Implement `ActionTool` table and model
13. Ensure all virtual base classes are properly used
14. Fix foreign key relationships (update FK references to `template_action_sets`)
15. Remove incorrect references (e.g., `template_part_demand_id` if exists)
16. Implement template versioning logic: when template is edited, create new revision with `prior_revision_id`
17. Create `TemplateActionSetAttachment` table and model for template action set-level attachments
18. Ensure `TemplateActionAttachment` is clearly for action-level attachments only
19. Ensure `MaintenanceActionSet` and `Action` do NOT have direct attachment tables - use Event comments instead

### 6.2 Phase 2: Business Layer Rebuild
1. Update factories to follow new data model
2. Ensure context classes wrap correct data models
3. Implement business logic for copying (with/without references)
4. Update sequence_order copying logic (from TemplateActionItems to Actions)
5. Implement Event creation in factories with ONE-TO-ONE enforcement
6. Update factories to set `planned_start_datetime` instead of `scheduled_date`
7. Implement template versioning: when TemplateActionSets is edited, create new revision with `prior_revision_id`
8. Ensure `template_action_set_id` reference in MaintenanceActionSet is frozen at creation time
9. Implement attachment handling: templates use direct attachment tables, base/maintenance use Event comments
10. Create `ActionToolFactory`
11. Update business logic to enforce only one MaintenanceActionSet per Event
12. Update context classes to provide Event comment-based attachment methods for base/maintenance items

### 6.3 Phase 3: Presentation Layer Rebuild
1. Update routes to use new business layer
2. Create/update services for presentation needs
3. Update templates to reflect new structure
4. Ensure three-tier portal system works with new model

### 6.4 Phase 4: Migration and Testing
1. Create database migration scripts
2. Migrate existing data to new structure
3. Update all tests
4. Verify end-to-end workflows

---




## Part 7: Open Questions and Decisions Needed

### 7.1 Questions for Discussion

1. **Naming**: ✅ `TemplateActions` → `TemplateActionSets` (confirmed)
2. **Naming**: ✅ `TemplateActionItem` → `TemplateActionItems` (confirmed)
3. **Proto Part Demands**: Should proto level have part demands and tools, or are templates sufficient?
4. **Sequence Order**: ✅ `TemplateActionSets` should NOT have `sequence_order` (confirmed - standalone templates)
5. **Sequence Order**: ✅ `MaintenanceActionSet` should NOT have `sequence_order` (confirmed - only one per event, planners create multiple events instead)
6. **One-to-One Relationship**: ✅ `MaintenanceActionSet` has ONE-TO-ONE relationship with `Event` (confirmed)
7. **Planned Start Datetime**: ✅ `MaintenanceActionSet` has `planned_start_datetime` field (confirmed - replaces `scheduled_date`)
8. **Virtual Classes**: ✅ `VirtualActionSet` should NOT include `sequence_order` or `revision` (confirmed)
9. **Template Versioning**: ✅ `TemplateActionSets` has `revision` and `prior_revision_id`, `MaintenanceActionSet` does NOT have `revision` (confirmed)
10. **Business Wrappers**: Should `MaintenanceEvent` and `TemplateMaintenanceEvent` stay in data layer or move to business layer?
11. **Services**: What specific services are needed for presentation layer?
12. **Migration Strategy**: How to handle existing data during rebuild?

### 7.2 Areas Requiring User Input

- **Naming conventions**: Confirm desired names for all entities
- **Field requirements**: Confirm which fields are required vs optional
- **Relationship patterns**: Confirm copy vs reference decisions
- **Business logic placement**: Confirm where business logic should live
- **Presentation needs**: Confirm what UI patterns are needed

---

## Summary

This document defines **how the maintenance structure SHOULD be** to enable a full model rebuild. Key principles:

1. **Three-tier hierarchy**: Base (work) → Template (blueprints) → Proto (library)
2. **Copy vs Reference**: Actions reference templates; parts/tools are standalone copies
3. **Event coupling**: Base requires Event (ONE-TO-ONE); templates/proto do not
4. **One MaintenanceActionSet per Event**: Planners create multiple events with different `planned_start_datetime` instead of multiple action sets
5. **Sequence order**: TemplateActionItems have it (within a set), base copies it, TemplateActionSets and MaintenanceActionSet don't have it
6. **Planning**: `planned_start_datetime` on MaintenanceActionSet allows planners to adjust timing per event
7. **Template versioning**: `revision` and `prior_revision_id` only on TemplateActionSets (not MaintenanceActionSet). Real events record what happened; template versioning preserves traceability to the exact template version used when the event was created. Template edits create new revisions.
8. **Attachments**: Templates have direct attachment tables (`TemplateActionSetAttachment`, `TemplateActionAttachment`). Base/maintenance items use Event comments for attachments, providing unified audit trail for real maintenance work.
9. **Virtual base classes**: Shared fields in abstract bases
10. **Layered architecture**: Clear separation of data, business, presentation
11. **Parallel structure**: All layers mirror data layer organization

**Next Steps**: Review this document, provide input on open questions, and proceed with phased implementation.

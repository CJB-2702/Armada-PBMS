# Refactoring TODO: TemplateActionItem → ProtoActionItems 

**Date**: 2024-11-19  
**Status**: ✅ Class and file rename completed

## Completed ✅

- [x] Renamed class `TemplateActionItem` → `ProtoActionItems `
- [x] Renamed file `template_action_item.py` → `proto_action_item.py`
- [x] Updated all import statements across data, business, services, and presentation layers
- [x] Updated all class references in code
- [x] Ran `z_clear_data` and build process successfully
- [x] Verified application starts without errors
- [x] Updated design documentation (application_structure.json, application_structure.md)

## Review Decision: Template vs Proto Terminology

### Recommendation: **KEEP "template" terminology** at database, API, and variable levels

After reviewing the data model and business logic across all layers:

| Level | Current | Decision | Rationale |
|-------|---------|----------|-----------|
| **Class Name** | `ProtoActionItems ` | ✅ Keep | Implementation detail, already changed |
| **Table Name** | `proto_action_items` | ✅ Keep | Database consistency, no migration needed |
| **FK Columns** | `template_action_item_id` | ✅ Keep | Consistent with other template tables |
| **Relationships** | `template_action_item` | ✅ Keep | Domain concept clarity |
| **Variables** | `template_action_item` | ✅ Keep | Domain terminology consistency |
| **URL Params** | `template_action_item_id` | ✅ Keep | API consistency, user-facing clarity |
| **Routes** | `/template-action-items` | ✅ Keep | Intuitive for users |

### Key Findings

1. **Database Schema**: 169 references to `template_action_item_id` across 30 files
   - Changing would require complex migrations
   - Consistent with `template_actions`, `template_part_demands`, etc.

2. **Business Logic**: Factory methods use `template_action_item` parameter names
   - `ActionFactory.create_from_template(template_action_item: ProtoActionItems )`
   - Type hints specify `ProtoActionItems ` class
   - Parameter names reflect domain concept

3. **API Layer**: URLs and parameters use "template-action-items"
   - `/template-action-items` is more intuitive than `/proto-action-items`
   - Consistent with other template endpoints
   - Changing would break existing links

## Conclusion

**Keep "template" terminology** throughout the system except for the class name itself. The class `ProtoActionItems ` is an implementation detail that better reflects its role as a prototype for creating Actions, while "template action item" remains the appropriate domain terminology.

## No Further Action Required

The refactoring is complete. The class rename to `ProtoActionItems ` provides better semantic clarity at the implementation level without requiring changes to the broader system's domain language.

---

See `REFACTORING_REVIEW_TemplateActionItem_to_ProtoActionItem.md` for detailed analysis.



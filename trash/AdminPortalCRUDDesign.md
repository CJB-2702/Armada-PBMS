# Admin Portal CRUD System - Design Document

## Overview

This document outlines the design for building out the admin portal to have view and CRUD pages for all data model tables, allowing direct access and editing of all database tables through a unified interface.

**Base Route**: `http://localhost:5000/maintenance/fleet/dashboard`

**Purpose**: Transform the fleet dashboard into a comprehensive admin portal with links to all table management routes.

---

## Current State Analysis

### Existing Fleet Dashboard
- **Location**: `app/presentation/routes/maintenance/fleet/main.py`
- **Template**: `app/presentation/templates/maintenance/fleet/dashboard.html`
- **Current Functionality**: Basic stats display with placeholder content
- **Route**: `/maintenance/fleet/dashboard`

### Leftover Templates Review

**Location**: `app/presentation/templates/maintenance/`

#### Templates That May Be Outdated/Leftover:
1. **`actions/`** - `detail.html`, `edit.html`, `list.html` - May be from old version
2. **`delays/`** - `detail.html`, `list.html` - May be from old version
3. **`maintenance_action_sets/`** - `detail.html`, `edit.html`, `list.html`, `_template_action_rows.html` - May be from old version
4. **`maintenance_plans/`** - `create.html`, `detail.html`, `edit.html`, `list.html` - May be from old version
5. **`part_demands/`** - `detail.html`, `list.html` - May be from old version
6. **`template_action_items/`** - `detail.html`, `list.html` - May be from old version
7. **`template_action_sets/`** - `detail.html`, `list.html` - May be from old version
8. **`template_action_tools/`** - `detail.html`, `list.html` - May be from old version
9. **`template_part_demands/`** - `detail.html`, `list.html` - May be from old version
10. **`manager/`** - Multiple templates including `template_builder.html`, `view_drafts.html`, etc. - May be from old version
11. **`create_maintenance_event.html`** - May be from old version
12. **`do_maintenance.html`** - May be from old version
13. **`view_maintenance_event.html`** - May be from old version
14. **`view_maintenance_template.html`** - May be from old version
15. **`view_proto_action.html`** - May be from old version
16. **`splash.html`** - Portal selection page (likely still in use)
17. **`index.html`** - Maintenance dashboard (may be from old version)
18. **`stub.html`** - Development placeholder (likely not in use)

#### Recommendation:
- **Review each template** to determine if it's still used by existing routes
- **Archive or delete** templates that are no longer referenced
- **Keep** templates that are actively used (e.g., `splash.html`, `technician/dashboard.html`, `fleet/dashboard.html`)
- **Consider** creating a new unified template system for the admin CRUD interface

---

## Complete Data Model Inventory

### Core Models (app/data/core/)

#### User Management
1. **User** (`users`) - `app/data/core/user_info/user.py`
   - Not inheriting from UserCreatedBase (special case)
   - Fields: username, email, password_hash, is_active, is_admin, is_system

#### Core Asset Management
2. **MajorLocation** (`major_locations`) - `app/data/core/major_location.py`
3. **AssetType** (`asset_types`) - `app/data/core/asset_info/asset_type.py`
4. **MakeModel** (`make_models`) - `app/data/core/asset_info/make_model.py`
5. **Asset** (`assets`) - `app/data/core/asset_info/asset.py`

#### Event System
6. **Event** (`events`) - `app/data/core/event_info/event.py`
7. **Comment** (`comments`) - `app/data/core/event_info/comment.py`
8. **Attachment** (`attachments`) - `app/data/core/event_info/attachment.py`
9. **CommentAttachment** (`comment_attachments`) - `app/data/core/event_info/comment.py`
10. **VirtualAttachmentReference** (`virtual_attachment_references`) - `app/data/core/event_info/attachment.py`

#### Supply/Inventory Core
11. **Part** (`parts`) - `app/data/core/supply/part.py`
12. **Tool** (`tools`) - `app/data/core/supply/tool.py`
13. **IssuableTool** (`issuable_tools`) - `app/data/core/supply/issuable_tool.py`

### Asset Detail Models (app/data/assets/)

#### Asset Details
14. **AssetDetailVirtual** (`asset_detail_virtuals`) - `app/data/assets/asset_detail_virtual.py`
15. **PurchaseInfo** (`purchase_info`) - `app/data/assets/asset_details/purchase_info.py`
16. **VehicleRegistration** (`vehicle_registrations`) - `app/data/assets/asset_details/vehicle_registration.py`
17. **ToyotaWarrantyReceipt** (`toyota_warranty_receipts`) - `app/data/assets/asset_details/toyota_warranty_receipt.py`

#### Model Details
18. **ModelDetailVirtual** (`model_detail_virtuals`) - `app/data/assets/model_detail_virtual.py`
19. **EmissionsInfo** (`emissions_info`) - `app/data/assets/model_details/emissions_info.py`
20. **ModelInfo** (`model_info`) - `app/data/assets/model_details/model_info.py`

#### Detail Table Templates
21. **ModelDetailTableTemplate** (`model_detail_template`) - `app/data/assets/detail_table_templates/model_detail_table_template.py`
22. **AssetDetailTemplateByModelType** (`asset_details_from_model_type`) - `app/data/assets/detail_table_templates/asset_details_from_model_type.py`
23. **AssetDetailTemplateByAssetType** (`asset_details_from_asset_type`) - `app/data/assets/detail_table_templates/asset_details_from_asset_type.py`

### Maintenance Models (app/data/maintenance/)

#### Base Maintenance (Actual Work)
24. **MaintenanceActionSet** (`maintenance_action_sets`) - `app/data/maintenance/base/maintenance_action_sets.py`
25. **Action** (`actions`) - `app/data/maintenance/base/actions.py`
26. **PartDemand** (`part_demands`) - `app/data/maintenance/base/part_demands.py`
27. **ActionTool** (`action_tools`) - `app/data/maintenance/base/action_tools.py`
28. **MaintenanceDelay** (`maintenance_delays`) - `app/data/maintenance/base/maintenance_delays.py`
29. **MaintenancePlan** (`maintenance_plans`) - `app/data/maintenance/base/maintenance_plans.py`

#### Template Maintenance (Blueprints)
30. **TemplateActionSet** (`template_action_sets`) - `app/data/maintenance/templates/template_action_sets.py`
31. **TemplateActionItem** (`template_actions`) - `app/data/maintenance/templates/template_actions.py`
32. **TemplatePartDemand** (`template_part_demands`) - `app/data/maintenance/templates/template_part_demands.py`
33. **TemplateActionTool** (`template_action_tools`) - `app/data/maintenance/templates/template_action_tools.py`
34. **TemplateActionSetAttachment** (`template_action_set_attachments`) - `app/data/maintenance/templates/template_action_set_attachments.py`
35. **TemplateActionAttachment** (`template_action_attachments`) - `app/data/maintenance/templates/template_action_attachments.py`

#### Proto Templates (Reusable Library)
36. **ProtoActionItem** (`proto_actions`) - `app/data/maintenance/proto_templates/proto_actions.py`
37. **ProtoPartDemand** (`proto_part_demands`) - `app/data/maintenance/proto_templates/proto_part_demands.py`
38. **ProtoActionTool** (`proto_action_tools`) - `app/data/maintenance/proto_templates/proto_action_tools.py`
39. **ProtoActionAttachment** (`proto_action_attachments`) - `app/data/maintenance/proto_templates/proto_action_attachments.py`

#### Maintenance Builders
40. **TemplateBuilderMemory** (`template_build_memory`) - `app/data/maintenance/builders/template_builder_memory.py`
41. **TemplateBuilderAttachmentReference** (`template_builder_attachment_references`) - `app/data/maintenance/builders/template_builder_attachment_reference.py`

#### Maintenance Virtual Classes (Abstract - No Tables)
- **VirtualActionSet** - Abstract base class
- **VirtualActionItem** - Abstract base class
- **VirtualPartDemand** - Abstract base class
- **VirtualActionTool** - Abstract base class
- **VirtualActionItem** - Abstract base class
- **VirtualActionSet** - Abstract base class
- **VirtualPartDemand** - Abstract base class
- **VirtualActionTool** - Abstract base class

### Inventory Models (app/data/inventory/)

42. **ActiveInventory** (`active_inventory`) - `app/data/inventory/base/active_inventory.py`
43. **InventoryMovement** (`inventory_movements`) - `app/data/inventory/base/inventory_movement.py`
44. **PartArrival** (`part_arrivals`) - `app/data/inventory/base/part_arrival.py`
45. **PackageHeader** (`package_headers`) - `app/data/inventory/base/package_header.py`
46. **PurchaseOrderHeader** (`purchase_order_headers`) - `app/data/inventory/base/purchase_order_header.py`
47. **PurchaseOrderLine** (`purchase_order_lines`) - `app/data/inventory/base/purchase_order_line.py`
48. **PartDemandPurchaseOrderLine** (`part_demand_purchase_order_lines`) - `app/data/inventory/base/part_demand_purchase_order_line.py`

### Dispatch Models (app/data/dispatching/)

49. **DispatchRequest** (`dispatch_requests`) - `app/data/dispatching/request.py`
50. **StandardDispatch** (`dispatches`) - `app/data/dispatching/outcomes/standard_dispatch.py`
51. **DispatchReject** (`dispatch_reject_details`) - `app/data/dispatching/outcomes/reject.py`
52. **DispatchContract** (`dispatch_contract_details`) - `app/data/dispatching/outcomes/contract.py`
53. **DispatchReimbursement** (`dispatch_reimbursement_details`) - `app/data/dispatching/outcomes/reimbursement.py`
54. **VirtualDispatchOutcome** (`virtual_dispatch_outcomes`) - `app/data/dispatching/virtual_dispatch_outcome.py`

### Event Detail Virtual
55. **EventDetailVirtual** (`event_detail_virtuals`) - `app/data/core/event_info/event.py` (Abstract - No table)

---

## Route Structure Design

### Option 1: Without "tables" Prefix (Recommended)

**Pattern**:
```
maintenance/<classname>/              # List view with filtering
maintenance/<classname>/<id>          # Detail view (default)
maintenance/<classname>/<id>/view     # Explicit detail view
maintenance/<classname>/<id>/edit     # Edit form
maintenance/<classname>/<id>/admin/delete  # Delete action
```

**Example Routes**:
```
maintenance/asset/                    # List all assets with filtering
maintenance/asset/123                 # View asset 123
maintenance/asset/123/view            # Explicit view (same as above)
maintenance/asset/123/edit            # Edit asset 123
maintenance/asset/123/admin/delete    # Delete asset 123

maintenance/maintenanceactionset/     # List all maintenance action sets
maintenance/maintenanceactionset/456   # View maintenance action set 456
maintenance/maintenanceactionset/456/edit  # Edit maintenance action set 456
maintenance/maintenanceactionset/456/admin/delete  # Delete maintenance action set 456
```

**Pros**:
- Shorter URLs
- More intuitive (maintenance is the context)
- Consistent with existing route patterns
- Easier to remember

**Cons**:
- May conflict with existing maintenance workflow routes
- Less explicit that these are table management routes

### Option 2: With "tables" Prefix

**Pattern**:
```
maintenance/tables/<classname>/              # List view with filtering
maintenance/tables/<classname>/<id>          # Detail view (default)
maintenance/tables/<classname>/<id>/view     # Explicit detail view
maintenance/tables/<classname>/<id>/edit     # Edit form
maintenance/tables/<classname>/<id>/admin/delete  # Delete action
```

**Example Routes**:
```
maintenance/tables/asset/                    # List all assets with filtering
maintenance/tables/asset/123                 # View asset 123
maintenance/tables/asset/123/view            # Explicit view (same as above)
maintenance/tables/asset/123/edit           # Edit asset 123
maintenance/tables/asset/123/admin/delete    # Delete asset 123
```

**Pros**:
- Very explicit that these are table management routes
- Clear separation from workflow routes
- Less likely to conflict with existing routes
- Better for admin-only access

**Cons**:
- Longer URLs
- More verbose
- "tables" may be confusing (these are models/entities, not just tables)

### Recommendation: **Option 1 (Without "tables" prefix)**

**Rationale**:
1. The `/maintenance/fleet/` prefix already indicates this is an admin/fleet portal
2. Shorter, cleaner URLs are better for usability
3. The classname in the URL makes it clear what entity is being managed
4. Can add route protection to ensure only admins access these routes
5. Consistent with RESTful conventions

**Alternative Consideration**: Use `/maintenance/admin/` instead of `/maintenance/fleet/` for these routes to make it more explicit that these are admin-only table management routes.

---

## Complete Route List

### Core Models

#### User Management
- `maintenance/user/` - List users
- `maintenance/user/<id>` - View user
- `maintenance/user/<id>/view` - View user (explicit)
- `maintenance/user/<id>/edit` - Edit user
- `maintenance/user/<id>/admin/delete` - Delete user

#### Core Asset Management
- `maintenance/majorlocation/` - List locations
- `maintenance/majorlocation/<id>` - View location
- `maintenance/majorlocation/<id>/view` - View location (explicit)
- `maintenance/majorlocation/<id>/edit` - Edit location
- `maintenance/majorlocation/<id>/admin/delete` - Delete location

- `maintenance/assettype/` - List asset types
- `maintenance/assettype/<id>` - View asset type
- `maintenance/assettype/<id>/view` - View asset type (explicit)
- `maintenance/assettype/<id>/edit` - Edit asset type
- `maintenance/assettype/<id>/admin/delete` - Delete asset type

- `maintenance/makemodel/` - List make/models
- `maintenance/makemodel/<id>` - View make/model
- `maintenance/makemodel/<id>/view` - View make/model (explicit)
- `maintenance/makemodel/<id>/edit` - Edit make/model
- `maintenance/makemodel/<id>/admin/delete` - Delete make/model

- `maintenance/asset/` - List assets
- `maintenance/asset/<id>` - View asset
- `maintenance/asset/<id>/view` - View asset (explicit)
- `maintenance/asset/<id>/edit` - Edit asset
- `maintenance/asset/<id>/admin/delete` - Delete asset

#### Event System
- `maintenance/event/` - List events
- `maintenance/event/<id>` - View event
- `maintenance/event/<id>/view` - View event (explicit)
- `maintenance/event/<id>/edit` - Edit event
- `maintenance/event/<id>/admin/delete` - Delete event

- `maintenance/comment/` - List comments
- `maintenance/comment/<id>` - View comment
- `maintenance/comment/<id>/view` - View comment (explicit)
- `maintenance/comment/<id>/edit` - Edit comment
- `maintenance/comment/<id>/admin/delete` - Delete comment

- `maintenance/attachment/` - List attachments
- `maintenance/attachment/<id>` - View attachment
- `maintenance/attachment/<id>/view` - View attachment (explicit)
- `maintenance/attachment/<id>/edit` - Edit attachment
- `maintenance/attachment/<id>/admin/delete` - Delete attachment

- `maintenance/commentattachment/` - List comment attachments
- `maintenance/commentattachment/<id>` - View comment attachment
- `maintenance/commentattachment/<id>/view` - View comment attachment (explicit)
- `maintenance/commentattachment/<id>/edit` - Edit comment attachment
- `maintenance/commentattachment/<id>/admin/delete` - Delete comment attachment

- `maintenance/virtualattachmentreference/` - List virtual attachment references
- `maintenance/virtualattachmentreference/<id>` - View virtual attachment reference
- `maintenance/virtualattachmentreference/<id>/view` - View virtual attachment reference (explicit)
- `maintenance/virtualattachmentreference/<id>/edit` - Edit virtual attachment reference
- `maintenance/virtualattachmentreference/<id>/admin/delete` - Delete virtual attachment reference

#### Supply/Inventory Core
- `maintenance/part/` - List parts
- `maintenance/part/<id>` - View part
- `maintenance/part/<id>/view` - View part (explicit)
- `maintenance/part/<id>/edit` - Edit part
- `maintenance/part/<id>/admin/delete` - Delete part

- `maintenance/tool/` - List tools
- `maintenance/tool/<id>` - View tool
- `maintenance/tool/<id>/view` - View tool (explicit)
- `maintenance/tool/<id>/edit` - Edit tool
- `maintenance/tool/<id>/admin/delete` - Delete tool

- `maintenance/issuabletool/` - List issuable tools
- `maintenance/issuabletool/<id>` - View issuable tool
- `maintenance/issuabletool/<id>/view` - View issuable tool (explicit)
- `maintenance/issuabletool/<id>/edit` - Edit issuable tool
- `maintenance/issuabletool/<id>/admin/delete` - Delete issuable tool

### Asset Detail Models

#### Asset Details
- `maintenance/assetdetailvirtual/` - List asset detail virtuals
- `maintenance/assetdetailvirtual/<id>` - View asset detail virtual
- `maintenance/assetdetailvirtual/<id>/view` - View asset detail virtual (explicit)
- `maintenance/assetdetailvirtual/<id>/edit` - Edit asset detail virtual
- `maintenance/assetdetailvirtual/<id>/admin/delete` - Delete asset detail virtual

- `maintenance/purchaseinfo/` - List purchase info records
- `maintenance/purchaseinfo/<id>` - View purchase info
- `maintenance/purchaseinfo/<id>/view` - View purchase info (explicit)
- `maintenance/purchaseinfo/<id>/edit` - Edit purchase info
- `maintenance/purchaseinfo/<id>/admin/delete` - Delete purchase info

- `maintenance/vehicleregistration/` - List vehicle registrations
- `maintenance/vehicleregistration/<id>` - View vehicle registration
- `maintenance/vehicleregistration/<id>/view` - View vehicle registration (explicit)
- `maintenance/vehicleregistration/<id>/edit` - Edit vehicle registration
- `maintenance/vehicleregistration/<id>/admin/delete` - Delete vehicle registration

- `maintenance/toyotawarrantyreceipt/` - List Toyota warranty receipts
- `maintenance/toyotawarrantyreceipt/<id>` - View Toyota warranty receipt
- `maintenance/toyotawarrantyreceipt/<id>/view` - View Toyota warranty receipt (explicit)
- `maintenance/toyotawarrantyreceipt/<id>/edit` - Edit Toyota warranty receipt
- `maintenance/toyotawarrantyreceipt/<id>/admin/delete` - Delete Toyota warranty receipt

#### Model Details
- `maintenance/modeldetailvirtual/` - List model detail virtuals
- `maintenance/modeldetailvirtual/<id>` - View model detail virtual
- `maintenance/modeldetailvirtual/<id>/view` - View model detail virtual (explicit)
- `maintenance/modeldetailvirtual/<id>/edit` - Edit model detail virtual
- `maintenance/modeldetailvirtual/<id>/admin/delete` - Delete model detail virtual

- `maintenance/emissionsinfo/` - List emissions info records
- `maintenance/emissionsinfo/<id>` - View emissions info
- `maintenance/emissionsinfo/<id>/view` - View emissions info (explicit)
- `maintenance/emissionsinfo/<id>/edit` - Edit emissions info
- `maintenance/emissionsinfo/<id>/admin/delete` - Delete emissions info

- `maintenance/modelinfo/` - List model info records
- `maintenance/modelinfo/<id>` - View model info
- `maintenance/modelinfo/<id>/view` - View model info (explicit)
- `maintenance/modelinfo/<id>/edit` - Edit model info
- `maintenance/modelinfo/<id>/admin/delete` - Delete model info

#### Detail Table Templates
- `maintenance/modeldetailtabletemplate/` - List model detail table templates
- `maintenance/modeldetailtabletemplate/<id>` - View model detail table template
- `maintenance/modeldetailtabletemplate/<id>/view` - View model detail table template (explicit)
- `maintenance/modeldetailtabletemplate/<id>/edit` - Edit model detail table template
- `maintenance/modeldetailtabletemplate/<id>/admin/delete` - Delete model detail table template

- `maintenance/assetdetailtemplatebymodeltype/` - List asset detail templates by model type
- `maintenance/assetdetailtemplatebymodeltype/<id>` - View asset detail template by model type
- `maintenance/assetdetailtemplatebymodeltype/<id>/view` - View asset detail template by model type (explicit)
- `maintenance/assetdetailtemplatebymodeltype/<id>/edit` - Edit asset detail template by model type
- `maintenance/assetdetailtemplatebymodeltype/<id>/admin/delete` - Delete asset detail template by model type

- `maintenance/assetdetailtemplatebyassettype/` - List asset detail templates by asset type
- `maintenance/assetdetailtemplatebyassettype/<id>` - View asset detail template by asset type
- `maintenance/assetdetailtemplatebyassettype/<id>/view` - View asset detail template by asset type (explicit)
- `maintenance/assetdetailtemplatebyassettype/<id>/edit` - Edit asset detail template by asset type
- `maintenance/assetdetailtemplatebyassettype/<id>/admin/delete` - Delete asset detail template by asset type

### Maintenance Models

#### Base Maintenance
- `maintenance/maintenanceactionset/` - List maintenance action sets
- `maintenance/maintenanceactionset/<id>` - View maintenance action set
- `maintenance/maintenanceactionset/<id>/view` - View maintenance action set (explicit)
- `maintenance/maintenanceactionset/<id>/edit` - Edit maintenance action set
- `maintenance/maintenanceactionset/<id>/admin/delete` - Delete maintenance action set

- `maintenance/action/` - List actions
- `maintenance/action/<id>` - View action
- `maintenance/action/<id>/view` - View action (explicit)
- `maintenance/action/<id>/edit` - Edit action
- `maintenance/action/<id>/admin/delete` - Delete action

- `maintenance/partdemand/` - List part demands
- `maintenance/partdemand/<id>` - View part demand
- `maintenance/partdemand/<id>/view` - View part demand (explicit)
- `maintenance/partdemand/<id>/edit` - Edit part demand
- `maintenance/partdemand/<id>/admin/delete` - Delete part demand

- `maintenance/actiontool/` - List action tools
- `maintenance/actiontool/<id>` - View action tool
- `maintenance/actiontool/<id>/view` - View action tool (explicit)
- `maintenance/actiontool/<id>/edit` - Edit action tool
- `maintenance/actiontool/<id>/admin/delete` - Delete action tool

- `maintenance/maintenancedelay/` - List maintenance delays
- `maintenance/maintenancedelay/<id>` - View maintenance delay
- `maintenance/maintenancedelay/<id>/view` - View maintenance delay (explicit)
- `maintenance/maintenancedelay/<id>/edit` - Edit maintenance delay
- `maintenance/maintenancedelay/<id>/admin/delete` - Delete maintenance delay

- `maintenance/maintenanceplan/` - List maintenance plans
- `maintenance/maintenanceplan/<id>` - View maintenance plan
- `maintenance/maintenanceplan/<id>/view` - View maintenance plan (explicit)
- `maintenance/maintenanceplan/<id>/edit` - Edit maintenance plan
- `maintenance/maintenanceplan/<id>/admin/delete` - Delete maintenance plan

#### Template Maintenance
- `maintenance/templateactionset/` - List template action sets
- `maintenance/templateactionset/<id>` - View template action set
- `maintenance/templateactionset/<id>/view` - View template action set (explicit)
- `maintenance/templateactionset/<id>/edit` - Edit template action set
- `maintenance/templateactionset/<id>/admin/delete` - Delete template action set

- `maintenance/templateactionitem/` - List template action items
- `maintenance/templateactionitem/<id>` - View template action item
- `maintenance/templateactionitem/<id>/view` - View template action item (explicit)
- `maintenance/templateactionitem/<id>/edit` - Edit template action item
- `maintenance/templateactionitem/<id>/admin/delete` - Delete template action item

- `maintenance/templatepartdemand/` - List template part demands
- `maintenance/templatepartdemand/<id>` - View template part demand
- `maintenance/templatepartdemand/<id>/view` - View template part demand (explicit)
- `maintenance/templatepartdemand/<id>/edit` - Edit template part demand
- `maintenance/templatepartdemand/<id>/admin/delete` - Delete template part demand

- `maintenance/templateactiontool/` - List template action tools
- `maintenance/templateactiontool/<id>` - View template action tool
- `maintenance/templateactiontool/<id>/view` - View template action tool (explicit)
- `maintenance/templateactiontool/<id>/edit` - Edit template action tool
- `maintenance/templateactiontool/<id>/admin/delete` - Delete template action tool

- `maintenance/templateactionsetattachment/` - List template action set attachments
- `maintenance/templateactionsetattachment/<id>` - View template action set attachment
- `maintenance/templateactionsetattachment/<id>/view` - View template action set attachment (explicit)
- `maintenance/templateactionsetattachment/<id>/edit` - Edit template action set attachment
- `maintenance/templateactionsetattachment/<id>/admin/delete` - Delete template action set attachment

- `maintenance/templateactionattachment/` - List template action attachments
- `maintenance/templateactionattachment/<id>` - View template action attachment
- `maintenance/templateactionattachment/<id>/view` - View template action attachment (explicit)
- `maintenance/templateactionattachment/<id>/edit` - Edit template action attachment
- `maintenance/templateactionattachment/<id>/admin/delete` - Delete template action attachment

#### Proto Templates
- `maintenance/protoactionitem/` - List proto action items
- `maintenance/protoactionitem/<id>` - View proto action item
- `maintenance/protoactionitem/<id>/view` - View proto action item (explicit)
- `maintenance/protoactionitem/<id>/edit` - Edit proto action item
- `maintenance/protoactionitem/<id>/admin/delete` - Delete proto action item

- `maintenance/protopartdemand/` - List proto part demands
- `maintenance/protopartdemand/<id>` - View proto part demand
- `maintenance/protopartdemand/<id>/view` - View proto part demand (explicit)
- `maintenance/protopartdemand/<id>/edit` - Edit proto part demand
- `maintenance/protopartdemand/<id>/admin/delete` - Delete proto part demand

- `maintenance/protoactiontool/` - List proto action tools
- `maintenance/protoactiontool/<id>` - View proto action tool
- `maintenance/protoactiontool/<id>/view` - View proto action tool (explicit)
- `maintenance/protoactiontool/<id>/edit` - Edit proto action tool
- `maintenance/protoactiontool/<id>/admin/delete` - Delete proto action tool

- `maintenance/protoactionattachment/` - List proto action attachments
- `maintenance/protoactionattachment/<id>` - View proto action attachment
- `maintenance/protoactionattachment/<id>/view` - View proto action attachment (explicit)
- `maintenance/protoactionattachment/<id>/edit` - Edit proto action attachment
- `maintenance/protoactionattachment/<id>/admin/delete` - Delete proto action attachment

#### Maintenance Builders
- `maintenance/templatebuildermemory/` - List template builder memory records
- `maintenance/templatebuildermemory/<id>` - View template builder memory
- `maintenance/templatebuildermemory/<id>/view` - View template builder memory (explicit)
- `maintenance/templatebuildermemory/<id>/edit` - Edit template builder memory
- `maintenance/templatebuildermemory/<id>/admin/delete` - Delete template builder memory

- `maintenance/templatebuilderattachmentreference/` - List template builder attachment references
- `maintenance/templatebuilderattachmentreference/<id>` - View template builder attachment reference
- `maintenance/templatebuilderattachmentreference/<id>/view` - View template builder attachment reference (explicit)
- `maintenance/templatebuilderattachmentreference/<id>/edit` - Edit template builder attachment reference
- `maintenance/templatebuilderattachmentreference/<id>/admin/delete` - Delete template builder attachment reference

### Inventory Models
- `maintenance/activeinventory/` - List active inventory records
- `maintenance/activeinventory/<id>` - View active inventory
- `maintenance/activeinventory/<id>/view` - View active inventory (explicit)
- `maintenance/activeinventory/<id>/edit` - Edit active inventory
- `maintenance/activeinventory/<id>/admin/delete` - Delete active inventory

- `maintenance/inventorymovement/` - List inventory movements
- `maintenance/inventorymovement/<id>` - View inventory movement
- `maintenance/inventorymovement/<id>/view` - View inventory movement (explicit)
- `maintenance/inventorymovement/<id>/edit` - Edit inventory movement
- `maintenance/inventorymovement/<id>/admin/delete` - Delete inventory movement

- `maintenance/partarrival/` - List part arrivals
- `maintenance/partarrival/<id>` - View part arrival
- `maintenance/partarrival/<id>/view` - View part arrival (explicit)
- `maintenance/partarrival/<id>/edit` - Edit part arrival
- `maintenance/partarrival/<id>/admin/delete` - Delete part arrival

- `maintenance/packageheader/` - List package headers
- `maintenance/packageheader/<id>` - View package header
- `maintenance/packageheader/<id>/view` - View package header (explicit)
- `maintenance/packageheader/<id>/edit` - Edit package header
- `maintenance/packageheader/<id>/admin/delete` - Delete package header

- `maintenance/purchaseorderheader/` - List purchase order headers
- `maintenance/purchaseorderheader/<id>` - View purchase order header
- `maintenance/purchaseorderheader/<id>/view` - View purchase order header (explicit)
- `maintenance/purchaseorderheader/<id>/edit` - Edit purchase order header
- `maintenance/purchaseorderheader/<id>/admin/delete` - Delete purchase order header

- `maintenance/purchaseorderline/` - List purchase order lines
- `maintenance/purchaseorderline/<id>` - View purchase order line
- `maintenance/purchaseorderline/<id>/view` - View purchase order line (explicit)
- `maintenance/purchaseorderline/<id>/edit` - Edit purchase order line
- `maintenance/purchaseorderline/<id>/admin/delete` - Delete purchase order line

- `maintenance/partdemandpurchaseorderline/` - List part demand purchase order lines
- `maintenance/partdemandpurchaseorderline/<id>` - View part demand purchase order line
- `maintenance/partdemandpurchaseorderline/<id>/view` - View part demand purchase order line (explicit)
- `maintenance/partdemandpurchaseorderline/<id>/edit` - Edit part demand purchase order line
- `maintenance/partdemandpurchaseorderline/<id>/admin/delete` - Delete part demand purchase order line

### Dispatch Models
- `maintenance/dispatchrequest/` - List dispatch requests
- `maintenance/dispatchrequest/<id>` - View dispatch request
- `maintenance/dispatchrequest/<id>/view` - View dispatch request (explicit)
- `maintenance/dispatchrequest/<id>/edit` - Edit dispatch request
- `maintenance/dispatchrequest/<id>/admin/delete` - Delete dispatch request

- `maintenance/standarddispatch/` - List standard dispatches
- `maintenance/standarddispatch/<id>` - View standard dispatch
- `maintenance/standarddispatch/<id>/view` - View standard dispatch (explicit)
- `maintenance/standarddispatch/<id>/edit` - Edit standard dispatch
- `maintenance/standarddispatch/<id>/admin/delete` - Delete standard dispatch

- `maintenance/dispatchreject/` - List dispatch rejects
- `maintenance/dispatchreject/<id>` - View dispatch reject
- `maintenance/dispatchreject/<id>/view` - View dispatch reject (explicit)
- `maintenance/dispatchreject/<id>/edit` - Edit dispatch reject
- `maintenance/dispatchreject/<id>/admin/delete` - Delete dispatch reject

- `maintenance/dispatchcontract/` - List dispatch contracts
- `maintenance/dispatchcontract/<id>` - View dispatch contract
- `maintenance/dispatchcontract/<id>/view` - View dispatch contract (explicit)
- `maintenance/dispatchcontract/<id>/edit` - Edit dispatch contract
- `maintenance/dispatchcontract/<id>/admin/delete` - Delete dispatch contract

- `maintenance/dispatchreimbursement/` - List dispatch reimbursements
- `maintenance/dispatchreimbursement/<id>` - View dispatch reimbursement
- `maintenance/dispatchreimbursement/<id>/view` - View dispatch reimbursement (explicit)
- `maintenance/dispatchreimbursement/<id>/edit` - Edit dispatch reimbursement
- `maintenance/dispatchreimbursement/<id>/admin/delete` - Delete dispatch reimbursement

- `maintenance/virtualdispatchoutcome/` - List virtual dispatch outcomes
- `maintenance/virtualdispatchoutcome/<id>` - View virtual dispatch outcome
- `maintenance/virtualdispatchoutcome/<id>/view` - View virtual dispatch outcome (explicit)
- `maintenance/virtualdispatchoutcome/<id>/edit` - Edit virtual dispatch outcome
- `maintenance/virtualdispatchoutcome/<id>/admin/delete` - Delete virtual dispatch outcome

---

## Dashboard Design

### Fleet Dashboard Layout

The dashboard at `/maintenance/fleet/dashboard` should display:

1. **Quick Stats Section** (Current - Keep)
   - Total Assets
   - Assets Due
   - Overdue Maintenance
   - Active Maintenance

2. **Data Model Navigation Section** (New - Add)
   - Organized by category (Core, Assets, Maintenance, Inventory, Dispatch)
   - Each category shows a card with links to all tables in that category
   - Each table link goes to the list view (`maintenance/<classname>/`)

3. **Recent Activity Section** (Optional)
   - Recently viewed/edited records
   - Quick access to frequently used tables

### Category Organization

#### Core Models
- User Management
  - Users
- Asset Management
  - Major Locations
  - Asset Types
  - Make/Models
  - Assets
- Event System
  - Events
  - Comments
  - Attachments
  - Comment Attachments
  - Virtual Attachment References
- Supply/Inventory Core
  - Parts
  - Tools
  - Issuable Tools

#### Asset Details
- Asset Details
  - Asset Detail Virtuals
  - Purchase Info
  - Vehicle Registrations
  - Toyota Warranty Receipts
- Model Details
  - Model Detail Virtuals
  - Emissions Info
  - Model Info
- Detail Templates
  - Model Detail Table Templates
  - Asset Detail Templates by Model Type
  - Asset Detail Templates by Asset Type

#### Maintenance
- Base Maintenance
  - Maintenance Action Sets
  - Actions
  - Part Demands
  - Action Tools
  - Maintenance Delays
  - Maintenance Plans
- Template Maintenance
  - Template Action Sets
  - Template Action Items
  - Template Part Demands
  - Template Action Tools
  - Template Action Set Attachments
  - Template Action Attachments
- Proto Templates
  - Proto Action Items
  - Proto Part Demands
  - Proto Action Tools
  - Proto Action Attachments
- Builders
  - Template Builder Memory
  - Template Builder Attachment References

#### Inventory
- Active Inventory
- Inventory Movements
- Part Arrivals
- Package Headers
- Purchase Order Headers
- Purchase Order Lines
- Part Demand Purchase Order Lines

#### Dispatch
- Dispatch Requests
- Standard Dispatches
- Dispatch Rejects
- Dispatch Contracts
- Dispatch Reimbursements
- Virtual Dispatch Outcomes

---

## View Types and Functionality

### List View (`maintenance/<classname>/`)

**Purpose**: Display all records in a table with filtering and pagination

**Features**:
- Table display with sortable columns
- Column-based filtering (dropdowns, text inputs, date ranges)
- Pagination (e.g., 25, 50, 100 records per page)
- Search functionality (full-text search across relevant columns)
- Quick actions (View, Edit, Delete buttons per row)
- Export options (CSV, Excel)
- Bulk actions (if applicable)

**URL Parameters**:
- `?page=1` - Page number
- `?per_page=25` - Records per page
- `?sort=name&order=asc` - Sort column and order
- `?filter_column=status&filter_value=Active` - Filter by column value
- `?search=query` - Full-text search

### Detail View (`maintenance/<classname>/<id>` or `maintenance/<classname>/<id>/view`)

**Purpose**: Display a single record with all fields and relationships

**Features**:
- All fields displayed in a readable format
- Related records displayed (e.g., Asset's Events, Maintenance Action Set's Actions)
- Navigation links to related records
- Edit button (links to edit view)
- Delete button (with confirmation)
- Audit trail information (created_by, updated_by, timestamps)
- History/change log (if implemented)

### Edit View (`maintenance/<classname>/<id>/edit`)

**Purpose**: Edit a single record

**Features**:
- Form with all editable fields
- Field validation
- Foreign key relationships as dropdowns/selects
- Save button (updates record)
- Cancel button (returns to detail view)
- Delete button (with confirmation)
- Relationship management (add/remove related records if applicable)

### Delete Action (`maintenance/<classname>/<id>/admin/delete`)

**Purpose**: Delete a record (admin-only)

**Features**:
- Confirmation dialog/page
- Cascade delete warnings (if record has related records)
- Soft delete option (if implemented)
- Audit trail (who deleted, when)

---

## Implementation Considerations

### 1. Route Generation

**Option A: Manual Route Registration**
- Manually create routes for each model
- More control, but repetitive

**Option B: Dynamic Route Generation**
- Use a registry of models
- Generate routes automatically
- More maintainable, but less explicit

**Recommendation**: Start with **Option A** for critical models, then consider **Option B** for less-used models.

### 2. Template System

**Option A: Generic Templates**
- Single set of templates that work for all models
- Use Jinja2 macros and includes
- More maintainable, but may be less flexible

**Option B: Model-Specific Templates**
- Custom templates for each model
- More flexible, but more maintenance

**Recommendation**: Use **Option A** with model-specific overrides where needed.

### 3. Form Generation

**Option A: Automatic Form Generation**
- Generate forms from SQLAlchemy model definitions
- Use WTForms with model introspection
- More maintainable, but less control

**Option B: Manual Form Definitions**
- Define forms manually for each model
- More control, but more maintenance

**Recommendation**: Use **Option A** with custom field types and validators where needed.

### 4. Access Control

- All routes should require admin access (`@admin_required` or `@login_required` with `is_admin` check)
- Consider role-based access control for specific tables
- Audit logging for all CRUD operations

### 5. Data Validation

- Server-side validation for all inputs
- Respect model constraints (required fields, foreign keys, etc.)
- Display helpful error messages
- Prevent invalid data from being saved

### 6. Relationship Handling

- Display related records in detail views
- Allow editing relationships (add/remove related records)
- Handle cascade deletes appropriately
- Warn users about relationship impacts before deletion

### 7. Performance Considerations

- Pagination for large tables
- Lazy loading for relationships
- Database query optimization
- Caching for frequently accessed data

---

## Portal-Based Views vs. Direct Table Access

### Current Approach: Portal-Based Views

**Pros**:
- Workflow-focused interfaces
- Role-appropriate views
- Business logic integration
- Better user experience for specific tasks

**Cons**:
- May not expose all data
- Limited direct access to tables
- May require multiple portals for different views

### Proposed Approach: Direct Table Access (Admin Portal)

**Pros**:
- Complete access to all data
- Direct editing capabilities
- No workflow restrictions
- Useful for data migration, debugging, and administration

**Cons**:
- May bypass business logic
- Risk of data inconsistency if not careful
- Less user-friendly for non-technical users
- May conflict with workflow-based portals

### Recommendation: **Hybrid Approach**

1. **Keep Portal-Based Views** for regular users and workflows
   - Technician Portal
   - Manager Portal
   - Fleet Portal (for analytics and reporting)

2. **Add Admin Portal CRUD** for administrators
   - Direct table access
   - Full CRUD capabilities
   - Data management and debugging
   - Clearly marked as admin-only

3. **Integration Points**
   - Portal views can link to admin views for detailed editing
   - Admin views can link back to portal views for context
   - Both use the same underlying data models

---

## Next Steps

1. **Review and Clean Up Templates**
   - Audit all templates in `app/presentation/templates/maintenance/`
   - Identify which are still in use
   - Archive or delete unused templates

2. **Implement Dashboard Updates**
   - Add data model navigation section to fleet dashboard
   - Organize by categories
   - Add links to all table list views

3. **Implement Core CRUD Routes**
   - Start with most-used models (Assets, Users, Maintenance Action Sets)
   - Create generic route handlers
   - Create generic templates

4. **Expand to All Models**
   - Gradually add routes for all models
   - Test each model's CRUD operations
   - Document any model-specific requirements

5. **Add Advanced Features**
   - Filtering and search
   - Export functionality
   - Bulk operations
   - Relationship management

---

## Questions to Resolve

1. **Route Prefix**: Use `/maintenance/` or `/maintenance/admin/` or `/maintenance/tables/`?
   - **Recommendation**: `/maintenance/` (simpler, cleaner)

2. **Class Name Format**: Use camelCase (`MaintenanceActionSet`) or lowercase (`maintenanceactionset`)?
   - **Recommendation**: Lowercase for URLs (`maintenanceactionset`)

3. **Virtual/Abstract Classes**: Should abstract base classes (VirtualActionSet, etc.) have routes?
   - **Recommendation**: No, only concrete tables

4. **Create Routes**: Should there be create routes (`maintenance/<classname>/create`)?
   - **Recommendation**: Yes, add create routes for completeness

5. **Bulk Operations**: Should there be bulk edit/delete routes?
   - **Recommendation**: Yes, but as a later enhancement

---

## Summary

This design document outlines a comprehensive admin portal CRUD system for all data model tables. The system will provide:

- **55+ data models** with full CRUD capabilities
- **275+ routes** (5 routes per model: list, view, view-explicit, edit, delete)
- **Unified dashboard** with links to all tables
- **Category organization** for easy navigation
- **Generic templates and route handlers** for maintainability
- **Admin-only access** with proper security
- **Integration** with existing portal-based views

The implementation should start with the dashboard updates and core models, then expand to all models gradually.


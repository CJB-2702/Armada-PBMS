# Application Structure Summary

This document provides a comprehensive overview of all files and classes in the application.

## .

### app.py

- *No classes defined*

### z_clear_data.py

- *No classes defined*

## app

### app/__init__.py

- *No classes defined*

### app/auth.py

- *No classes defined*

### app/build.py

- *No classes defined*

### app/logger.py

- *No classes defined*

### app/routes.py

- *No classes defined*

## app/buisness

### app/buisness/__init__.py

- *No classes defined*

## app/buisness/assets

### app/buisness/assets/__init__.py

- *No classes defined*

### app/buisness/assets/asset_details_context.py

- **AssetDetailsContext** (AssetContext): Extended context manager for asset operations including detail tables.

### app/buisness/assets/detail_table_context.py

- **DetailTableContext**: Context manager for asset detail table operations.

### app/buisness/assets/make_model_context.py

- **MakeModelDetailsContext** (MakeModelContext): Extended context manager for make/model operations including detail tables.

### app/buisness/assets/model_detail_context.py

- **ModelDetailContext**: Context manager for model detail table operations.

## app/buisness/assets/asset_details

### app/buisness/assets/asset_details/__init__.py

- *No classes defined*

### app/buisness/assets/asset_details/asset_details_struct.py

- **AssetDetailsStruct**: Structured representation of all asset detail records for an asset.

### app/buisness/assets/asset_details/details_union.py

- **AssetDetailsUnionService**: Service class for performing union queries across all asset detail tables.

## app/buisness/assets/factories

### app/buisness/assets/factories/__init__.py

- *No classes defined*

### app/buisness/assets/factories/asset_detail_factory.py

- **AssetDetailFactory** (DetailFactory): Factory class for creating asset detail table rows

### app/buisness/assets/factories/asset_factory.py

- **AssetFactory**: Factory class for creating Asset instances

### app/buisness/assets/factories/detail_factory.py

- **DetailFactory** (ABC): Abstract base class for detail table row creation

### app/buisness/assets/factories/make_model_factory.py

- **MakeModelFactory**: Factory class for creating MakeModel instances

### app/buisness/assets/factories/model_detail_factory.py

- **ModelDetailFactory** (DetailFactory): Factory class for creating model detail table rows

## app/buisness/assets/model_details

### app/buisness/assets/model_details/__init__.py

- *No classes defined*

### app/buisness/assets/model_details/details_union.py

- **ModelDetailsUnionService**: Service class for performing union queries across all model detail tables.

### app/buisness/assets/model_details/model_details_struct.py

- **ModelDetailsStruct**: Structured representation of all model detail records for a make/model.

## app/buisness/core

### app/buisness/core/__init__.py

- *No classes defined*

### app/buisness/core/asset_context.py

- **AssetContext**: Core context manager for asset operations.

### app/buisness/core/data_insertion_mixin.py

- **DataInsertionMixin**: Mixin that provides generic data insertion capabilities for SQLAlchemy models

### app/buisness/core/event_context.py

- **EventContext**: Context manager for event operations including comments and attachments.

### app/buisness/core/make_model_context.py

- **MakeModelContext**: Core context manager for make/model operations.

## app/buisness/dispatching

### app/buisness/dispatching/__init__.py

- *No classes defined*

### app/buisness/dispatching/dispatch.py

- **DispatchContext**: Context class that holds references to event, request, and all outcomes.

### app/buisness/dispatching/dispatch_manager.py

- **DispatchManager**: Simple manager with CRUD helpers.

## app/buisness/inventory

### app/buisness/inventory/__init__.py

- *No classes defined*

### app/buisness/inventory/part_context.py

- **PartContext**: Context manager for part operations.

### app/buisness/inventory/tool_context.py

- **ToolContext**: Context manager for tool operations.

## app/buisness/inventory/managers

### app/buisness/inventory/managers/__init__.py

- *No classes defined*

### app/buisness/inventory/managers/inventory_manager.py

- **InventoryManager**: Manages all inventory movements and levels

### app/buisness/inventory/managers/part_arrival_manager.py

- **PartArrivalManager**: Handles receiving and inspection workflow

### app/buisness/inventory/managers/part_demand_manager.py

- **PartDemandManager**: Extends maintenance part demand for purchasing integration

### app/buisness/inventory/managers/purchase_order_manager.py

- **PurchaseOrderManager**: Handles all purchase order business logic

## app/buisness/maintenance

### app/buisness/maintenance/__init__.py

- *No classes defined*

### app/buisness/maintenance/action_context.py

- **ActionContext**: Context manager for action operations.

### app/buisness/maintenance/maintenance_action_set_context.py

- **MaintenanceActionSetContext**: Context manager for maintenance action set operations.

### app/buisness/maintenance/maintenance_event.py

- **MaintenanceEvent**: Comprehensive maintenance event manager that holds and manages:

### app/buisness/maintenance/maintenance_plan_context.py

- **MaintenancePlanContext**: Context manager for maintenance plan operations.

### app/buisness/maintenance/template_maintenance_event.py

- **TemplateMaintenanceEvent**: Comprehensive template maintenance event manager that holds and manages:

## app/buisness/maintenance/factories

### app/buisness/maintenance/factories/__init__.py

- *No classes defined*

### app/buisness/maintenance/factories/action_factory.py

- **ActionFactory**: Factory for creating Actions from ProtoActionItems 

### app/buisness/maintenance/factories/maintenance_action_set_factory.py

- **MaintenanceActionSetFactory**: Factory for creating MaintenanceActionSet from TemplateActions

### app/buisness/maintenance/factories/maintenance_event_factory.py

- **MaintenanceActionSetFactory**: Factory for creating MaintenanceActionSet from TemplateActions

### app/buisness/maintenance/factories/maintenance_factory.py

- **MaintenanceFactory**: Main factory for creating complete maintenance workflows from templates

### app/buisness/maintenance/factories/maintenance_plan_factory.py

- **MaintenancePlanFactory**: Factory for creating MaintenancePlans and related operations

### app/buisness/maintenance/factories/part_demand_factory.py

- **PartDemandFactory**: Factory for creating PartDemands from TemplatePartDemands

## app/buisness/maintenance/utils

### app/buisness/maintenance/utils/__init__.py

- *No classes defined*

### app/buisness/maintenance/utils/maintenance_helpers.py

- **MaintenanceHelpers**: Utility functions for maintenance operations

### app/buisness/maintenance/utils/quick_actions.py

- **QuickActions**: Quick action functions for common maintenance operations

### app/buisness/maintenance/utils/template_helpers.py

- **TemplateHelpers**: Utility functions for template operations

## app/data

### app/data/__init__.py

- *No classes defined*

## app/data/assets

### app/data/assets/__init__.py

- *No classes defined*

### app/data/assets/asset_detail_virtual.py

- **AssetDetailVirtual** (UserCreatedBase): Base class for all asset-specific detail tables

### app/data/assets/build.py

- *No classes defined*

### app/data/assets/model_detail_virtual.py

- **ModelDetailVirtual** (UserCreatedBase): Base class for all model-specific detail tables

## app/data/assets/asset_details

### app/data/assets/asset_details/__init__.py

- *No classes defined*

### app/data/assets/asset_details/purchase_info.py

- **PurchaseInfo** (AssetDetailVirtual): Store purchase-related information for assets

### app/data/assets/asset_details/toyota_warranty_receipt.py

- **ToyotaWarrantyReceipt** (AssetDetailVirtual): Store Toyota-specific warranty and service information

### app/data/assets/asset_details/vehicle_registration.py

- **VehicleRegistration** (AssetDetailVirtual): Store vehicle registration and licensing information

## app/data/assets/detail_table_templates

### app/data/assets/detail_table_templates/__init__.py

- *No classes defined*

### app/data/assets/detail_table_templates/asset_details_from_asset_type.py

- **AssetDetailTemplateByAssetType** (UserCreatedBase): Configuration container that defines which detail table types are available for a specific asset type

### app/data/assets/detail_table_templates/asset_details_from_model_type.py

- **AssetDetailTemplateByModelType** (UserCreatedBase): Configuration container that defines which detail table types are available for a specific asset type

### app/data/assets/detail_table_templates/model_detail_table_template.py

- **ModelDetailTableTemplate** (UserCreatedBase): Configuration container that defines additional detail table types for a specific model beyond what the asset type provides

## app/data/assets/model_details

### app/data/assets/model_details/__init__.py

- *No classes defined*

### app/data/assets/model_details/details_union.py

- **ModelDetailsUnionService**: Service class for performing union queries across all model detail tables.

### app/data/assets/model_details/emissions_info.py

- **EmissionsInfo** (ModelDetailVirtual): Store emissions specifications for vehicle models

### app/data/assets/model_details/model_info.py

- **ModelInfo** (ModelDetailVirtual): Store general model specifications and information

## app/data/core

### app/data/core/__init__.py

- *No classes defined*

### app/data/core/build.py

- *No classes defined*

### app/data/core/major_location.py

- **MajorLocation** (UserCreatedBase): No description available

### app/data/core/user_created_base.py

- **UserCreatedBase** (db.Model, DataInsertionMixin): Abstract base class for all user-created entities with audit trail

### app/data/core/virtual_sequence_generator.py

- **VirtualSequenceGenerator** (ABC): Abstract base class for sequence generators

## app/data/core/asset_info

### app/data/core/asset_info/asset.py

- **Asset** (UserCreatedBase): No description available

### app/data/core/asset_info/asset_type.py

- **AssetType** (UserCreatedBase): No description available

### app/data/core/asset_info/make_model.py

- **MakeModel** (UserCreatedBase): No description available

## app/data/core/event_info

### app/data/core/event_info/attachment.py

- **Attachment** (UserCreatedBase): No description available
- **VirtualAttachmentReference** (UserCreatedBase): No description available

### app/data/core/event_info/comment.py

- **Comment** (UserCreatedBase): No description available
- **CommentAttachment** (VirtualAttachmentReference): No description available

### app/data/core/event_info/event.py

- **Event** (UserCreatedBase, DataInsertionMixin): No description available
- **EventDetailVirtual** (UserCreatedBase): Base class for all event-specific detail tables

## app/data/core/sequences

### app/data/core/sequences/__init__.py

- *No classes defined*

### app/data/core/sequences/attachment_id_manager.py

- **AttachmentIDManager** (VirtualSequenceGenerator): Manages all_attachments_id sequence for AttachmentReference tables

### app/data/core/sequences/detail_id_managers.py

- **AssetDetailIDManager** (VirtualSequenceGenerator): Manages all_asset_detail_id sequence for AssetDetailVirtual tables
- **ModelDetailIDManager** (VirtualSequenceGenerator): Manages all_model_detail_id sequence for ModelDetailVirtual tables

### app/data/core/sequences/event_detail_id_manager.py

- **EventDetailIDManager** (VirtualSequenceGenerator): Manages all_event_detail_id sequence for EventDetailVirtual tables

## app/data/core/user_info

### app/data/core/user_info/user.py

- **User** (UserMixin, DataInsertionMixin, db.Model): No description available

## app/data/dispatching

### app/data/dispatching/__init__.py

- *No classes defined*

### app/data/dispatching/build.py

- *No classes defined*

### app/data/dispatching/dispatch.py

- **DispatchContext**: Context class that holds references to event, request, and all outcomes.

### app/data/dispatching/dispatch_manager.py

- **DispatchManager**: Simple manager with CRUD helpers.

### app/data/dispatching/request.py

- **DispatchRequest** (EventDetailVirtual): No description available

### app/data/dispatching/virtual_dispatch_outcome.py

- **VirtualDispatchOutcome** (UserCreatedBase): Base class for dispatch outcomes (StandardDispatch, Contract, Reimbursement)

## app/data/dispatching/outcomes

### app/data/dispatching/outcomes/__init__.py

- *No classes defined*

### app/data/dispatching/outcomes/contract.py

- **Contract** (VirtualDispatchOutcome): No description available

### app/data/dispatching/outcomes/reimbursement.py

- **Reimbursement** (VirtualDispatchOutcome): No description available

### app/data/dispatching/outcomes/reject.py

- **Reject** (VirtualDispatchOutcome): No description available

### app/data/dispatching/outcomes/standard_dispatch.py

- **StandardDispatch** (VirtualDispatchOutcome): No description available

## app/data/inventory

### app/data/inventory/__init__.py

- *No classes defined*

### app/data/inventory/build.py

- *No classes defined*

## app/data/inventory/base

### app/data/inventory/base/__init__.py

- *No classes defined*

### app/data/inventory/base/active_inventory.py

- **ActiveInventory** (UserCreatedBase): Current inventory levels by part and location

### app/data/inventory/base/inventory_movement.py

- **InventoryMovement** (UserCreatedBase): Audit trail for all inventory changes with complete traceability chain

### app/data/inventory/base/package_header.py

- **PackageHeader** (UserCreatedBase): Represents a physical package/shipment arrival

### app/data/inventory/base/part_arrival.py

- **PartArrival** (UserCreatedBase): Individual parts received in a package

### app/data/inventory/base/part_demand_purchase_order_line.py

- **PartDemandPurchaseOrderLine** (UserCreatedBase): Association table linking part demands to purchase order lines

### app/data/inventory/base/purchase_order_header.py

- **PurchaseOrderHeader** (UserCreatedBase): Purchase order header - represents a purchase order document

### app/data/inventory/base/purchase_order_line.py

- **PurchaseOrderLine** (UserCreatedBase): Individual line items within a purchase order

## app/data/maintenance

### app/data/maintenance/__init__.py

- *No classes defined*

### app/data/maintenance/build.py

- *No classes defined*

### app/data/maintenance/maintenance_event.py

- **MaintenanceEvent**: Comprehensive maintenance event manager that holds and manages:

### app/data/maintenance/template_maintenance_event.py

- **TemplateMaintenanceEvent**: Comprehensive template maintenance event manager that holds and manages:

### app/data/maintenance/virtual_action_item.py

- **VirtualActionItem** (UserCreatedBase): Virtual action items created from templates

### app/data/maintenance/virtual_action_set.py

- **VirtualActionSet** (UserCreatedBase): Virtual action sets created from templates

### app/data/maintenance/virtual_part_demand.py

- **VirtualPartDemand** (UserCreatedBase): Virtual part demands created from templates

## app/data/maintenance/base

### app/data/maintenance/base/__init__.py

- *No classes defined*

### app/data/maintenance/base/action.py

- **Action** (VirtualActionItem): Base class for all actions

### app/data/maintenance/base/maintenance_action_set.py

- **MaintenanceActionSet** (EventDetailVirtual, VirtualActionSet): No description available

### app/data/maintenance/base/maintenance_delays.py

- **MaintenanceDelay** (UserCreatedBase): No description available

### app/data/maintenance/base/maintenance_plan.py

- **MaintenancePlan** (UserCreatedBase): No description available

### app/data/maintenance/base/part_demand.py

- **PartDemand** (VirtualPartDemand): Reference table that links maintenance actions to part demands using composition pattern

## app/data/maintenance/templates

### app/data/maintenance/templates/__init__.py

- *No classes defined*

### app/data/maintenance/templates/proto_action_item.py

- **ProtoActionItems ** (VirtualActionItem): No description available

### app/data/maintenance/templates/template_action_attachment.py

- **TemplateActionAttachment** (VirtualAttachmentReference): No description available

### app/data/maintenance/templates/template_action_set.py

- **TemplateActions** (VirtualActionSet): No description available

### app/data/maintenance/templates/template_action_set_attachment.py

- **TemplateActionAttachment** (VirtualAttachmentReference): No description available

### app/data/maintenance/templates/template_action_tool.py

- **TemplateActionTool** (UserCreatedBase): No description available

### app/data/maintenance/templates/template_part_demand.py

- **TemplatePartDemand** (VirtualPartDemand): No description available

## app/data/supply_items

### app/data/supply_items/__init__.py

- *No classes defined*

### app/data/supply_items/build.py

- *No classes defined*

### app/data/supply_items/issuable_tool.py

- **IssuableTool** (UserCreatedBase): Issuable Tool class - represents a tool that can be issued/assigned to users

### app/data/supply_items/part.py

- **Part** (UserCreatedBase): No description available

### app/data/supply_items/tool.py

- **Tool** (UserCreatedBase): No description available

## app/presentation/routes

### app/presentation/routes/__init__.py

- *No classes defined*

### app/presentation/routes/asset_management.py

- *No classes defined*

### app/presentation/routes/main.py

- *No classes defined*

### app/presentation/routes/main_routes.py

- *No classes defined*

## app/presentation/routes/assets

### app/presentation/routes/assets/__init__.py

- *No classes defined*

### app/presentation/routes/assets/detail_tables.py

- *No classes defined*

### app/presentation/routes/assets/model_details.py

- *No classes defined*

## app/presentation/routes/core

### app/presentation/routes/core/__init__.py

- *No classes defined*

### app/presentation/routes/core/asset_types.py

- *No classes defined*

### app/presentation/routes/core/assets.py

- *No classes defined*

### app/presentation/routes/core/locations.py

- *No classes defined*

### app/presentation/routes/core/make_models.py

- *No classes defined*

### app/presentation/routes/core/users.py

- *No classes defined*

## app/presentation/routes/core/events

### app/presentation/routes/core/events/__init__.py

- *No classes defined*

### app/presentation/routes/core/events/attachments.py

- *No classes defined*

### app/presentation/routes/core/events/comments.py

- *No classes defined*

### app/presentation/routes/core/events/events.py

- *No classes defined*

## app/presentation/routes/dispatching

### app/presentation/routes/dispatching/__init__.py

- *No classes defined*

### app/presentation/routes/dispatching/api.py

- *No classes defined*

### app/presentation/routes/dispatching/views.py

- *No classes defined*

## app/presentation/routes/maintenance

### app/presentation/routes/maintenance/__init__.py

- *No classes defined*

### app/presentation/routes/maintenance/actions.py

- *No classes defined*

### app/presentation/routes/maintenance/delays.py

- *No classes defined*

### app/presentation/routes/maintenance/main.py

- *No classes defined*

### app/presentation/routes/maintenance/maintenance_action_sets.py

- *No classes defined*

### app/presentation/routes/maintenance/maintenance_plans.py

- *No classes defined*

### app/presentation/routes/maintenance/part_demands.py

- *No classes defined*

### app/presentation/routes/maintenance/proto_action_items.py

- *No classes defined*

### app/presentation/routes/maintenance/template_actions.py

- *No classes defined*

### app/presentation/routes/maintenance/template_action_tools.py

- *No classes defined*

### app/presentation/routes/maintenance/template_part_demands.py

- *No classes defined*

## app/presentation/routes/maintenance/fleet

### app/presentation/routes/maintenance/fleet/__init__.py

- *No classes defined*

### app/presentation/routes/maintenance/fleet/analytics.py

- *No classes defined*

### app/presentation/routes/maintenance/fleet/assets.py

- *No classes defined*

### app/presentation/routes/maintenance/fleet/dashboard.py

- *No classes defined*

### app/presentation/routes/maintenance/fleet/events.py

- *No classes defined*

### app/presentation/routes/maintenance/fleet/fleet_table.py

- *No classes defined*

## app/presentation/routes/maintenance/manager

### app/presentation/routes/maintenance/manager/__init__.py

- *No classes defined*

### app/presentation/routes/maintenance/manager/active.py

- *No classes defined*

### app/presentation/routes/maintenance/manager/assets_due.py

- *No classes defined*

### app/presentation/routes/maintenance/manager/assignments.py

- *No classes defined*

### app/presentation/routes/maintenance/manager/dashboard.py

- *No classes defined*

### app/presentation/routes/maintenance/manager/delays.py

- *No classes defined*

### app/presentation/routes/maintenance/manager/events.py

- *No classes defined*

### app/presentation/routes/maintenance/manager/part_demands.py

- *No classes defined*

### app/presentation/routes/maintenance/manager/plans.py

- *No classes defined*

### app/presentation/routes/maintenance/manager/templates.py

- *No classes defined*

## app/presentation/routes/maintenance/technician

### app/presentation/routes/maintenance/technician/__init__.py

- *No classes defined*

### app/presentation/routes/maintenance/technician/actions.py

- *No classes defined*

### app/presentation/routes/maintenance/technician/dashboard.py

- *No classes defined*

### app/presentation/routes/maintenance/technician/delays.py

- *No classes defined*

### app/presentation/routes/maintenance/technician/history.py

- *No classes defined*

### app/presentation/routes/maintenance/technician/parts.py

- *No classes defined*

### app/presentation/routes/maintenance/technician/work.py

- *No classes defined*

## app/presentation/routes/supply

### app/presentation/routes/supply/__init__.py

- *No classes defined*

### app/presentation/routes/supply/main.py

- *No classes defined*

### app/presentation/routes/supply/parts.py

- *No classes defined*

### app/presentation/routes/supply/tools.py

- *No classes defined*

## app/services

### app/services/__init__.py

- *No classes defined*

## app/services/assets

### app/services/assets/__init__.py

- *No classes defined*

### app/services/assets/asset_detail_service.py

- **AssetDetailService**: Service for asset detail table presentation data.

### app/services/assets/asset_detail_union_service.py

- **AssetDetailUnionService**: Service class for performing union queries across all asset detail tables.

### app/services/assets/model_detail_service.py

- **ModelDetailService**: Service for model detail table presentation data.

### app/services/assets/model_detail_union_service.py

- **ModelDetailUnionService**: Service class for performing union queries across all model detail tables.

## app/services/core

### app/services/core/__init__.py

- *No classes defined*

### app/services/core/asset_service.py

- **AssetService**: Service for asset presentation data.

### app/services/core/asset_type_service.py

- **AssetTypeService**: Service for asset type presentation data.

### app/services/core/event_service.py

- **EventService**: Service for event presentation data.

### app/services/core/location_service.py

- **LocationService**: Service for location presentation data.

### app/services/core/make_model_service.py

- **MakeModelService**: Service for make/model presentation data.

### app/services/core/user_service.py

- **UserService**: Service for user presentation data.

## app/services/inventory

### app/services/inventory/__init__.py

- *No classes defined*

### app/services/inventory/active_inventory_service.py

- **ActiveInventoryService**: Service for active inventory presentation data.

### app/services/inventory/inventory_movement_service.py

- **InventoryMovementService**: Service for inventory movement presentation data.

### app/services/inventory/inventory_service.py

- **InventoryService**: Service for inventory availability checks and queries.

### app/services/inventory/part_demand_service.py

- **PartDemandInventoryService**: Service for part demand inventory-related queries.

### app/services/inventory/part_service.py

- **PartService**: Service for part-related presentation data.

### app/services/inventory/tool_service.py

- **ToolService**: Service for tool-related presentation data.

## app/services/maintenance

### app/services/maintenance/__init__.py

- *No classes defined*

### app/services/maintenance/action_service.py

- **ActionService**: Service for action presentation data.

### app/services/maintenance/admin_service.py

- **AdminService**: Service for fleet/admin portal presentation data.

### app/services/maintenance/delay_service.py

- **DelayService**: Service for maintenance delay presentation data.

### app/services/maintenance/maintenance_action_set_service.py

- **MaintenanceActionSetService**: Service for maintenance action set presentation data.

### app/services/maintenance/maintenance_plan_service.py

- **MaintenancePlanService**: Service for maintenance plan presentation data.

### app/services/maintenance/maintenance_service.py

- **MaintenanceService**: Service for maintenance dashboard statistics and aggregations.

### app/services/maintenance/manager_service.py

- **ManagerService**: Service for manager portal presentation data.

### app/services/maintenance/part_demand_service.py

- **PartDemandService**: Service for part demand presentation data.

### app/services/maintenance/technician_service.py

- **TechnicianService**: Service for technician portal presentation data.

### app/services/maintenance/template_action_item_service.py

- **ProtoActionItemService**: Service for template action item presentation data.

### app/services/maintenance/template_action_set_service.py

- **TemplateActionsService**: Service for template action set presentation data.

### app/services/maintenance/template_action_tool_service.py

- **TemplateActionToolService**: Service for template action tool presentation data.

### app/services/maintenance/template_part_demand_service.py

- **TemplatePartDemandService**: Service for template part demand presentation data.

## app/utils

### app/utils/__init__.py

- *No classes defined*

### app/utils/_build_structure_summary.py

- *No classes defined*

### app/utils/_view_database.py

- *No classes defined*

### app/utils/logger.py

- **SingletonLogger**: Singleton logger that ensures only one logger instance is created per application run.
- **JsonFormatter** (logging.Formatter): Formatter that outputs JSON strings after parsing the LogRecord.


# Asset Management System - Planned File Structure

This document outlines the planned file structure for the Asset Management System, organized to mirror the model structure and provide clear separation of concerns.

```
asset_management/
├── app/
│   ├── __init__.py
│   ├── build.py                    # Main build orchestrator
│   ├── auth.py                     # Authentication system
│   ├── routes.py                   # Main routing
│   ├── models/
│   │   ├── __init__.py
│   │   ├── build.py               # Model build coordinator
│   │   ├── core/                  # Core foundation models
│   │   │   ├── __init__.py
│   │   │   ├── build.py          # Core models builder
│   │   │   ├── user.py
│   │   │   ├── user_created_base.py
│   │   │   ├── major_location.py
│   │   │   ├── asset_type.py
│   │   │   ├── make_model.py
│   │   │   ├── asset.py
│   │   │   ├── event.py
│   │   │   └── data_insertion_mixin.py
│   │   ├── assets/                # Asset detail system
│   │   │   ├── __init__.py
│   │   │   ├── build.py          # Asset models builder
│   │   │   ├── detail_virtual_template.py        # Base virtual template classes
│   │   │   ├── asset_details/                    # Asset-specific detail tables
│   │   │   │   ├── __init__.py
│   │   │   │   ├── asset_detail_virtual.py       # Asset detail base class
│   │   │   │   ├── purchase_info.py              # Purchase information
│   │   │   │   ├── vehicle_registration.py       # Vehicle registration details
│   │   │   │   └── toyota_warranty_receipt.py    # Toyota-specific warranty info
│   │   │   ├── model_details/                    # Model-specific detail tables
│   │   │   │   ├── __init__.py
│   │   │   │   ├── model_detail_virtual.py       # Model detail base class
│   │   │   │   ├── emissions_info.py             # Emissions specifications
│   │   │   │   └── model_info.py                 # General model information
│   │   │   └── detail_table_sets/                # Detail table set containers
│   │   │       ├── __init__.py
│   │   │       ├── asset_type_detail_table_set.py   # Asset detail table set
│   │   │       └── model_detail_table_set.py        # Model detail table set
│   │   ├── maintenance/           # Maintenance system (future)
│   │   │   ├── __init__.py
│   │   │   ├── build.py          # Maintenance models builder
│   │   │   ├── maintenance_event.py
│   │   │   ├── maintenance_status.py
│   │   │   ├── template_action_set.py
│   │   │   ├── template_action_set_header.py
│   │   │   ├── template_action_item.py
│   │   │   ├── action.py
│   │   │   ├── template_action_attachment.py
│   │   │   └── template_part_demand.py
│   │   ├── inventory/             # Inventory system (future)
│   │   │   ├── __init__.py
│   │   │   ├── build.py          # Inventory models builder
│   │   │   ├── part.py
│   │   │   ├── part_alias.py
│   │   │   ├── inventory.py
│   │   │   ├── inventory_location_history.py
│   │   │   ├── part_demand.py
│   │   │   ├── related_part_demand_set.py
│   │   │   ├── purchase_order.py
│   │   │   ├── purchase_order_part_set.py
│   │   │   ├── part_relocation_request.py
│   │   │   ├── relocation_status_update.py
│   │   │   └── location/
│   │   │       ├── __init__.py
│   │   │       ├── sub_address.py
│   │   │       └── precise_location.py
│   │   ├── dispatch/              # Dispatch system (future)
│   │   │   ├── __init__.py
│   │   │   ├── build.py          # Dispatch models builder
│   │   │   ├── dispatch.py
│   │   │   ├── dispatch_status.py
│   │   │   └── dispatch_change_history.py
│   │   ├── planning/              # Planning system (future)
│   │   │   ├── __init__.py
│   │   │   ├── build.py          # Planning models builder
│   │   │   ├── asset_type_scheduled_task_plan.py
│   │   │   ├── model_additional_scheduled_task_plan.py
│   │   │   ├── asset_additional_scheduled_task_plan.py
│   │   │   ├── planned_maintenance.py
│   │   │   └── planned_maintenance_status.py
│   │   └── communication/         # Communication system (future)
│   │       ├── __init__.py
│   │       ├── build.py          # Communication models builder
│   │       ├── comment.py
│   │       ├── comment_attachment.py
│   │       ├── comment_history.py
│   │       └── attachment.py
│   ├── templates/
│   │   ├── base.html              # Base template with navigation
│   │   ├── index.html             # Dashboard/home page
│   │   ├── components/            # Reusable template components
│   │   │   ├── __init__.py
│   │   │   ├── forms/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── asset_form.html
│   │   │   │   ├── user_form.html
│   │   │   │   ├── location_form.html
│   │   │   │   ├── asset_type_form.html
│   │   │   │   └── make_model_form.html
│   │   │   ├── tables/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── asset_table.html
│   │   │   │   ├── user_table.html
│   │   │   │   ├── location_table.html
│   │   │   │   └── event_table.html
│   │   │   ├── modals/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── confirmation.html
│   │   │   │   └── details.html
│   │   │   └── detail_tables/     # Detail table components
│   │   │       ├── __init__.py
│   │   │       ├── purchase_info.html
│   │   │       ├── vehicle_registration.html
│   │   │       ├── toyota_warranty_receipt.html
│   │   │       ├── emissions_info.html
│   │   │       └── model_info.html
│   │   ├── auth/                  # Authentication templates
│   │   │   ├── __init__.py
│   │   │   ├── login.html
│   │   │   ├── logout.html
│   │   │   └── error.html
│   │   ├── core/                  # Core entity templates
│   │   │   ├── __init__.py
│   │   │   ├── users/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── list.html
│   │   │   │   ├── detail.html
│   │   │   │   ├── create.html
│   │   │   │   └── edit.html
│   │   │   ├── locations/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── list.html
│   │   │   │   ├── detail.html
│   │   │   │   ├── create.html
│   │   │   │   └── edit.html
│   │   │   ├── asset_types/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── list.html
│   │   │   │   ├── detail.html
│   │   │   │   ├── create.html
│   │   │   │   └── edit.html
│   │   │   ├── make_models/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── list.html
│   │   │   │   ├── detail.html
│   │   │   │   ├── create.html
│   │   │   │   └── edit.html
│   │   │   └── events/
│   │   │       ├── __init__.py
│   │   │       ├── list.html
│   │   │       ├── detail.html
│   │   │       ├── create.html
│   │   │       └── edit.html
│   │   ├── assets/                # Asset templates (mirrors model structure)
│   │   │   ├── __init__.py
│   │   │   ├── list.html          # Asset list view
│   │   │   ├── view.html          # Asset detail view
│   │   │   ├── create.html        # Asset creation form
│   │   │   ├── edit.html          # Asset edit form
│   │   │   ├── detail_tables/     # Asset detail table views
│   │   │   │   ├── __init__.py
│   │   │   │   ├── purchase_info.html
│   │   │   │   ├── vehicle_registration.html
│   │   │   │   └── toyota_warranty_receipt.html
│   │   │   └── model_details/     # Model detail table views
│   │   │       ├── __init__.py
│   │   │       ├── emissions_info.html
│   │   │       └── model_info.html
│   │   ├── maintenance/           # Maintenance templates (future)
│   │   │   ├── __init__.py
│   │   │   ├── events/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── list.html
│   │   │   │   ├── detail.html
│   │   │   │   ├── create.html
│   │   │   │   └── edit.html
│   │   │   ├── templates/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── list.html
│   │   │   │   ├── detail.html
│   │   │   │   ├── create.html
│   │   │   │   └── edit.html
│   │   │   └── actions/
│   │   │       ├── __init__.py
│   │   │       ├── list.html
│   │   │       ├── detail.html
│   │   │       ├── create.html
│   │   │       └── edit.html
│   │   ├── inventory/             # Inventory templates (future)
│   │   │   ├── __init__.py
│   │   │   ├── parts/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── list.html
│   │   │   │   ├── detail.html
│   │   │   │   ├── create.html
│   │   │   │   └── edit.html
│   │   │   ├── inventory/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── list.html
│   │   │   │   ├── detail.html
│   │   │   │   ├── create.html
│   │   │   │   └── edit.html
│   │   │   ├── purchase_orders/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── list.html
│   │   │   │   ├── detail.html
│   │   │   │   ├── create.html
│   │   │   │   └── edit.html
│   │   │   └── relocations/
│   │   │       ├── __init__.py
│   │   │       ├── list.html
│   │   │       ├── detail.html
│   │   │       ├── create.html
│   │   │       └── edit.html
│   │   ├── dispatch/              # Dispatch templates (future)
│   │   │   ├── __init__.py
│   │   │   ├── list.html
│   │   │   ├── detail.html
│   │   │   ├── create.html
│   │   │   └── edit.html
│   │   └── planning/              # Planning templates (future)
│   │       ├── __init__.py
│   │       ├── scheduled_tasks.html
│   │       ├── planned_maintenance.html
│   │       └── templates.html
│   ├── static/
│   │   ├── css/
│   │   │   ├── base.css
│   │   │   ├── components.css
│   │   │   └── utilities.css
│   │   ├── js/
│   │   │   ├── htmx-extensions.js
│   │   │   └── alpine-components.js
│   │   └── uploads/
│   │       ├── attachments/
│   │       └── images/
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── build_data.json        # Build configuration data
│   │   ├── database.py
│   │   ├── validators.py
│   │   ├── helpers.py
│   │   └── decorators.py
│   └── config/
│       ├── __init__.py
│       ├── settings.py
│       └── database.py
├── migrations/
├── tests/
│   ├── __init__.py
│   ├── test_models/
│   │   ├── __init__.py
│   │   ├── test_core/
│   │   │   ├── __init__.py
│   │   │   ├── test_user.py
│   │   │   ├── test_asset.py
│   │   │   ├── test_location.py
│   │   │   └── test_event.py
│   │   ├── test_assets/
│   │   │   ├── __init__.py
│   │   │   ├── test_detail_tables.py
│   │   │   └── test_virtual_templates.py
│   │   ├── test_maintenance.py
│   │   ├── test_inventory.py
│   │   └── test_dispatch.py
│   ├── test_routes/
│   │   ├── __init__.py
│   │   ├── test_core.py
│   │   ├── test_assets.py
│   │   ├── test_maintenance.py
│   │   └── test_inventory.py
│   └── test_services/
│       ├── __init__.py
│       ├── test_asset_service.py
│       └── test_maintenance_service.py
├── phase_1/                       # Phase 1 testing and validation
│   ├── test_phase1.py
│   └── verifyhelloworld.py
├── phase_2/                       # Phase 2 testing and validation
│   ├── test_phase2.py
│   ├── BUILD_QUICK_REFERENCE.md
│   ├── BUILD_SYSTEM.md
│   └── IMPLEMENTATION_SUMMARY.md
├── phase_3/                       # Phase 3 testing and validation
│   ├── test_phase2_phase3.py
│   └── PHASE3_STATUS.md
├── phase_4/                       # Phase 4 testing and validation
│   ├── test_phase4.py
│   ├── PHASE4_STATUS.md
│   └── QUICK_REFERENCE.md
├── requirements.txt
├── app.py                         # Main application entry point
├── z_clear_data.py                # Database clearing utility
├── z_view_database.py             # Database viewing utility
└── README.md
```

## Key Changes Made

### 1. **Template Structure Mirrors Model Structure**
- **Core Templates**: `templates/core/` matches `models/core/` organization
- **Asset Templates**: `templates/assets/` mirrors `models/assets/` with detail table subdirectories
- **Future Templates**: Organized to match planned model structure

### 2. **Simplified and Realistic Organization**
- Removed overly complex nested template structures
- Aligned template organization with actual model hierarchy
- Made component structure more maintainable

### 3. **Detail Table Integration**
- Added `templates/components/detail_tables/` for reusable detail table components
- Created `templates/assets/detail_tables/` and `templates/assets/model_details/` to mirror model structure
- Separated asset-specific and model-specific detail table views

### 4. **Core Entity Templates**
- Organized core templates by entity type (users, locations, asset_types, make_models, events)
- Each entity has consistent CRUD template structure (list, detail, create, edit)
- Templates follow the same pattern as the model relationships

### 5. **Component Reusability**
- Forms, tables, and modals are organized as reusable components
- Detail table components can be shared across different views
- Consistent naming and structure for maintainability

### 6. **Testing Organization**
- Test structure mirrors the model organization
- Phase-specific testing directories for validation
- Clear separation between model, route, and service tests

## Benefits of This Structure

1. **Consistency**: Template organization mirrors model organization
2. **Maintainability**: Clear separation of concerns and logical grouping
3. **Scalability**: Easy to add new models and corresponding templates
4. **Reusability**: Components can be shared across different views
5. **Clarity**: Developers can easily find templates for specific models
6. **Future-Proof**: Structure supports planned future phases

This structure provides a clear, maintainable organization that grows naturally with the application while maintaining consistency between models and their corresponding user interfaces.
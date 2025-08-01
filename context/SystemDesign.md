# Asset Management System - HTMX Flask App Development Prompt

## Project Overview
Create a comprehensive asset management system using Flask, SQLAlchemy, and HTMX. The application should manage assets, maintenance, dispatch, supply chain, and planning operations with minimal JavaScript and CSS.

## Technology Stack
- **Backend**: Flask with SQLAlchemy ORM
- **Frontend**: HTMX for dynamic interactions, minimal Alpine.js for complex interactions, vanilla JS only when necessary
- **Database**: SQLite (development)
- **Styling**: Minimal CSS, focus on functionality over aesthetics
- **Forms**: Standard HTML forms with HTMX attributes. Minimize form validation during initial development.
- **File Operations**: Use `pathlib.Path` for all file and directory operations instead of `os.path`

## Coding Standards

### File Path Handling
- **Use `pathlib.Path`**: All file and directory operations should use `pathlib.Path` instead of `os.path`
- **Benefits**: More readable, object-oriented, cross-platform compatible
- **Examples**:
  ```python
  # ✅ Good - Use pathlib
  from pathlib import Path
  config_file = Path(__file__).parent.parent / 'utils' / 'build_data.json'
  if config_file.exists():
      data = config_file.read_text()
  
  # ❌ Avoid - Don't use os.path
  import os
  config_file = os.path.join(os.path.dirname(__file__), '..', 'utils', 'build_data.json')
  if os.path.exists(config_file):
      with open(config_file, 'r') as f:
          data = f.read()
  ```

## Tiered Database Building Architecture

### Build System Structure
The database building process follows a tiered approach for clear separation of concerns and dependency management:

```
app.py                    # Main entry point
├── app/build.py         # Main build orchestrator
├── app/models/build.py  # Model build coordinator
├── app/models/core/
│   ├── build.py         # Core models builder
│   └── init_data.py     # Core data initialization
├── app/models/assets/
│   ├── build.py         # Asset detail models builder
│   └── init_data.py     # Asset data initialization
├── app/models/maintenance/
│   ├── build.py         # Maintenance models builder
│   └── init_data.py     # Maintenance data initialization
└── app/models/operations/
    ├── build.py         # Operations models builder
    └── init_data.py     # Operations data initialization
```

### Module Independence
Each module should contain its own independent build and data initialization files:

1. **`build.py`**: Handles table creation and model building for that module
2. **`init_data.py`**: Handles data initialization and configuration loading for that module
3. **Centralized Data**: All modules read from `app/utils/build_data.json` for consistency
4. **Module Isolation**: Each module can be built and initialized independently

### Build Flow
1. **app.py** calls `app.build.build_database()`
2. **app/build.py** orchestrates the overall build process with phase-specific options
3. **app/models/build.py** coordinates all model category builds
4. **Category builders** (core, assets, maintenance, operations) build their specific models

### Build Phase Options
The build system supports flexible phase-specific building:

```python
def build_database(build_phase='all', data_phase='all'):
    """
    build_phase options:
    - 'phase1': Core Foundation Tables only
    - 'phase2': Phase 1 + Asset Detail Tables
    - 'phase3': Phase 1 + Phase 2 + Automatic Detail Insertion
    - 'all': All phases (default = phase3)
    
    data_phase options:
    - 'phase1': Core System Initialization only
    - 'phase2': Phase 1 + Asset Detail Data (manual insertion)
    - 'phase3': Phase 1 + Asset Detail Data Update auto-generated detail rows instead of manually inserting 
    - 'all': highest phase (default = phase3)
    - 'none': Skip data insertion
    """
```

### Phase Structure
- **Phase 1A**: Core Foundation Tables (User, Location, Asset Type, Make/Model, Asset, Event)
- **Phase 1B**: Core System Initialization (Initial Data)
- **Phase 2A**: Asset Detail Tables (Specifications, Configurations, etc.)
- **Phase 2B**: Asset Detail Data (Detail Table Configurations)
- **Phase 3A**: Automatic Detail Insertion System (Automatic Detail Row Creation)
- **Phase 3B**: Automatic Detail Data Updates (Update Auto-Generated Detail Rows)
- **Phase 4**: Maintenance System (Events, Templates, Actions, Parts)
- **Phase 5**: Operations System (Dispatch, Tracking, Reporting)

## Data Models & Relationships

### Asset Relationship Architecture

The asset management system uses a hierarchical relationship structure to ensure data consistency and simplify management:

#### Asset → MakeModel → AssetType Hierarchy

**1. Asset Model**
- Links directly to MakeModel via `make_model_id`
- Contains asset-specific data: name, serial number, status, location, meter readings
- Gets asset type through MakeModel relationship (property)
- Inherits meter units and specifications from MakeModel
- **Phase 3 Enhancement**: Automatically creates detail table rows on asset creation

**2. MakeModel Model** 
- Links to AssetType via `asset_type_id`
- Contains make/model-specific data: make, model, year, revision, description
- Defines meter units for all assets of this model
- All assets of this make/model inherit the same asset type

**3. AssetType Model**
- Top-level categorization (Vehicle, Equipment, Tool, etc.)
- No direct relationship to assets
- Assets access asset type through their make/model

#### Benefits of This Design
- **Consistency**: All assets of the same make/model have identical asset type classification
- **Efficiency**: Asset type is managed once per make/model, not per asset
- **Inheritance**: Assets inherit specifications and units from their make/model
- **Flexibility**: Easy to change asset type for all assets of a make/model
- **Data Integrity**: Prevents inconsistent asset type assignments

### Automatic Detail Insertion System (Phase 3)

The automatic detail insertion system provides seamless, automatic population of detail tables when assets are created. This system consists of three main components:

#### 1. Conditional Import System
- **Dynamic Import**: Detail table sets are imported conditionally based on build phase
- **Phase Control**: Automatic detail insertion can be enabled/disabled per phase
- **Registry Management**: Centralized registry of available detail table types

#### 2. Asset Creation Hook
- **SQLAlchemy Event Listener**: `after_insert` event triggers automatic detail creation
- **Error Handling**: Comprehensive error handling prevents asset creation failures
- **Transaction Management**: Proper database transaction handling for detail creation

#### 3. Detail Table Registry System
- **Centralized Registry**: Maps detail table types to their class implementations
- **Dynamic Class Loading**: Uses `__import__` for flexible detail table loading
- **Extensible Design**: Easy to add new detail table types without code changes

#### Implementation Details
```python
# Class-level state for automatic detail insertion
_automatic_detail_insertion_enabled = False
_detail_table_registry = None

# Conditional import in enable_automatic_detail_insertion()
from app.models.assets.detail_table_sets.asset_type_detail_table_set import AssetTypeDetailTableSet
from app.models.assets.detail_table_sets.model_detail_table_set import ModelDetailTableSet

# SQLAlchemy event listener
event.listen(cls, 'after_insert', cls._create_detail_rows_after_insert)
```

#### Process Flow
1. **Asset Creation**: New asset is created in database
2. **Event Trigger**: `after_insert` event fires
3. **Method Call**: `_create_detail_table_rows()` is called
4. **Configuration Lookup**: Retrieve asset type and model detail table sets
5. **Row Creation**: Create detail table rows based on configurations
6. **Linkage**: Establish proper foreign key relationships

### Core Entities

#### 1. User Management
- **User**: Primary user entity with authentication and role management
- **User Created Base Class**: Abstract base class for all user-created entities
- **System User**: Special "system" user for initial data creation and automated processes
- **Major Location**: Geographic locations managed by users
- **Status Sets**: Reusable status configurations

#### 2. Asset Management
- **Asset**: Physical assets with properties and meter readings
- **Asset Type**: Categories of assets (Vehicle, Equipment, Tool, etc.)
- **Make and Model**: Manufacturer and model information with asset type association
- **Major Location**: Where assets are located
- **Event**: Activity tracking for assets

**Asset Relationship Hierarchy**:
- **Asset** → **MakeModel** (direct relationship via `make_model_id`)
- **MakeModel** → **AssetType** (direct relationship via `asset_type_id`)
- **Asset** → **AssetType** (indirect relationship through MakeModel property)

This hierarchical design ensures:
- All assets of the same make/model have consistent asset type classification
- Asset types are managed at the make/model level for consistency
- Assets inherit meter units and specifications from their make/model
- Simplified relationship management with reduced data redundancy

#### 2.1. Detail Table System
The detail table system provides a flexible, extensible approach to storing detailed specifications and configurations for assets and models. This system uses a virtual template approach to allow dynamic addition of detail information without schema changes.

**Detail Table Architecture**:
- **Detail Table Sets**: Container models that group related detail tables
  - **Asset Type Detail Table Set**: Configuration container that defines which detail table types are available for a specific asset type
    - Links to `AssetType` via foreign key
    - Stores list of detail table types (purchase_info, vehicle_registration, etc.) that apply to this asset type
    - Marks each detail table type as asset_detail or model_detail
  - **Model Detail Table Set**: Configuration container that defines additional detail table types for a specific model beyond what the asset type provides
    - Links to `MakeModel` via foreign key
    - Stores list of additional detail table types that apply to this model
    - Marks each detail table type as asset_detail or model_detail

**Detail Table Types**:
- **Asset Detail Tables**: Store asset-specific information
  - Purchase Information: Purchase dates, prices, vendors, warranty info, event_id for comments/attachments
  - Vehicle Registration: License plates, VIN, registration, insurance
  - Toyota Warranty Receipt: Toyota-specific warranty and service info

- **Model Detail Tables**: Store model-specific specifications
  - Emissions Information: Fuel economy, emissions standards, certifications
  - Model Information: Technical specifications, body styles, capacities

**Virtual Template System**:
- **DetailTableVirtualTemplate**: Abstract base class for all detail table functionality
  - Inherits from `UserCreatedBase` for audit trail
  - Provides common fields: id, created_at, created_by_id, updated_at, updated_by_id
  - Includes abstract methods for detail table operations
- **AssetDetailVirtual**: Base class for asset-specific detail tables
  - Inherits from `DetailTableVirtualTemplate`
  - Adds relationship to `Asset` via foreign key (not to detail table set)
  - Implements asset-specific validation logic
- **ModelDetailVirtual**: Base class for model-specific detail tables
  - Inherits from `DetailTableVirtualTemplate`
  - Adds relationship to `MakeModel` via foreign key (not to detail table set)
  - Implements model-specific validation logic
  - Prevents duplicate model detail rows

**Dynamic Detail Table Assignment System**:
- **No direct relationships**: Assets and models do NOT have relationships to detail table sets
- **Asset Type Detail Table Sets**: Define which detail tables are available for each asset type
- **Model Detail Table Sets**: Define additional detail tables available for specific models
- **Dynamic row creation**: On asset creation, system automatically creates detail table rows

**Asset Creation Detail Table Process**:
When a new asset is created, the system automatically processes detail table assignments through the following steps:

1. **Asset Type Lookup**: Retrieve the AssetTypeDetailTableSet configuration for the asset's type
2. **Model Lookup**: Retrieve the ModelDetailTableSet configuration for the asset's model  
3. **Asset Type Processing**: For each detail table type in the asset type configuration:
   - If asset_detail: Create a new detail table row linked to this specific asset
   - If model_detail: Check if a detail table row exists for this model, create if missing
4. **Model Processing**: For each additional detail table type in the model configuration:
   - If asset_detail: Create a new detail table row linked to this specific asset
   - If model_detail: Check if a detail table row exists for this model, create if missing
5. **Row Creation**: Generate appropriate detail table rows with proper foreign key relationships
6. **Duplicate Prevention**: Ensure model detail rows are only created once per model

**Detail Table Row Creation Logic**:
- **Asset Detail Tables**: Create rows with foreign key to the specific asset
- **Model Detail Tables**: Create rows with foreign key to the model (if not already exists)
- **Duplicate Prevention**: Check for existing model detail rows before creating new ones
- **Cascade Management**: When asset is deleted, remove associated asset detail rows
- **Model Detail Persistence**: Model detail rows persist even when assets are deleted

**Phase 3 Automatic Detail Insertion**:
- **Conditional Import**: Detail table sets imported only when automatic insertion is enabled
- **Event-Driven Creation**: SQLAlchemy `after_insert` event triggers automatic detail creation
- **Registry System**: Centralized registry maps detail table types to their implementations
- **Error Handling**: Comprehensive error handling prevents asset creation failures
- **Phase Control**: Automatic insertion can be enabled/disabled based on build phase

#### 3. Maintenance System
- **Maintenance Event**: Scheduled and reactive maintenance
- **Template Action Set**: Reusable maintenance procedures
- **Template Action Set Header**: Grouping of maintenance actions
- **Template Action Item**: Individual maintenance tasks
- **Actions**: Actual maintenance tasks performed
- **Parts**: Inventory items used in maintenance
- **Part Demand**: Parts needed for maintenance
- **Template Part Demand**: Standard part requirements
- **Attachments**: Files and documents
- **Comments**: Communication and notes
- **Comment Attachments**: Files attached to comments

#### 4. Dispatch System
- **Dispatches**: Work orders and assignments
- **Dispatch Status**: Current state of dispatches
- **Dispatch Change History**: Audit trail of changes
- **Assets**: Assets assigned to dispatches
- **Users**: Personnel involved in dispatches

#### 5. Supply Chain
- **Inventory**: Stock management
- **Parts**: Physical items in inventory
- **Part Aliases**: Alternative names for parts
- **Purchase Order**: Procurement orders
- **Purchase Order Part Set**: Items in purchase orders
- **Part Demand**: Parts needed from inventory
- **Related Part Demand Set**: Grouped part requirements
- **Inventory Location History**: Movement tracking
- **Part Relocation Requests**: Transfer requests
- **Relocation Status Updates**: Transfer status tracking
- **Sub Address**: Detailed location information
- **Precise Location XYZ Tag**: Exact positioning

#### 6. Maintenance Planning
- **Asset Type Scheduled Task Plan**: Maintenance schedules by asset type
- **Model Additional Scheduled Task Plan**: Model-specific schedules
- **Asset Additional Scheduled Task Plan**: Asset-specific schedules
- **Planned Maintenance**: Scheduled maintenance events
- **Planned Maintenance Statuses**: Status tracking for planned work

### Key Relationships
- **User Created Base Class**: All user-created entities inherit from this base class
- **System User**: Handles all initial data creation and automated processes
- **Admin User**: First user created with full system access
- **Asset Hierarchy**: Asset → MakeModel → AssetType (hierarchical relationship)
- Assets belong to Major Locations
- Assets have Make and Model information with inherited asset type
- MakeModels define asset types and meter units for all assets of that model
- **Detail Table Relationships**:
  - Asset Types have Asset Type Detail Table Sets that define available detail table types
  - Models have Model Detail Table Sets that provide additional detail table types
  - Individual assets inherit detail tables from both their asset type and model through dynamic row creation
  - Detail tables maintain audit trail through User Created Base Class
  - No direct relationships between assets/models and detail table sets - assignment is configuration-based
  - Asset detail table rows link directly to specific assets
  - Model detail table rows link directly to models and are shared across all assets of that model
- Maintenance Events are linked to Assets
- Dispatches involve one asset which can be reassigned
- Users create and manage all entities (except system-created initial data)
- Events track all significant activities
- Comments and attachments are linked to various entities
- Inventory tracks part locations and quantities

## Application Features

### 1. Asset Management
- **CRUD Operations**: Create, read, update, delete assets
- **Asset Search**: Filter by type, location, status
- **Asset Details**: Comprehensive asset information display
- **Asset History**: Event timeline for each asset
- **Location Management**: Track asset movements

### 2. Maintenance Management
- **Maintenance Scheduling**: Create and manage maintenance plans
- **Work Orders**: Generate and track maintenance tasks
- **Template Management**: Reusable maintenance procedures
- **Part Requirements**: Track parts needed for maintenance
- **Maintenance History**: Complete audit trail

### 3. Dispatch System
- **Dispatch Creation**: Generate work orders
- **Status Tracking**: Real-time status updates
- **Asset Assignment**: Assign assets to dispatches
- **User Assignment**: Assign personnel to work
- **Approval Workflow**: Multi-level approval process

### 4. Inventory Management
- **Stock Tracking**: Current inventory levels
- **Part Management**: Add, edit, delete parts
- **Location Tracking**: Where parts are stored
- **Movement History**: Track part movements
- **Purchase Orders**: Procurement management
- **Relocation Requests**: Part transfer workflow

### 5. Planning System
- **Scheduled Maintenance**: Automated maintenance planning
- **Task Templates**: Reusable maintenance procedures
- **Interval Planning**: Time and meter-based scheduling
- **Resource Planning**: Personnel and part allocation

## HTMX Implementation Guidelines

### 1. Form Handling
- Use standard HTML forms with `hx-post`, `hx-get`, `hx-put`, `hx-delete`
- Implement form validation with server-side responses
- Use `hx-target` to update specific page sections
- Leverage `hx-swap` for smooth transitions

### 2. Dynamic Content
- Asset lists with real-time filtering
- Maintenance schedules with drag-and-drop (Alpine.js if needed)
- Status updates without page refresh
- Search results with instant feedback

### 3. User Experience
- Loading states with `hx-indicator`
- Error handling with `hx-on::after-request`
- Confirmation dialogs for destructive actions
- Progressive enhancement for better UX

### 4. Alpine.js Integration
- Use only for complex interactions HTMX can't handle
- Form validation with real-time feedback
- Dynamic form field generation
- Complex state management

## User Management System

### 1. User Hierarchy
- **System User**: Special user with ID 1, handles all initial data creation and automated processes
- **Admin User**: First human user created with full system access and privileges
- **Regular Users**: Standard users with role-based permissions
- **Guest Users**: Limited access users (if needed)

### 2. User Created Base Class
```python
class UserCreatedBase:
    """Abstract base class for all user-created entities"""
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    
    # Relationships
    created_by = relationship('User', foreign_keys=[created_by_id])
    updated_by = relationship('User', foreign_keys=[updated_by_id])
```

### 3. System Initialization
- **System User Creation**: Automatically created during database initialization
- **Initial Data**: All seed data (status sets, default asset types, etc.) created by system user
- **Admin Setup**: First human user automatically becomes admin
- **Audit Trail**: All system-created records properly tracked

### 4. User Roles and Permissions
- **Admin**: Full system access, user management, system configuration
- **Manager**: Asset management, maintenance planning, dispatch oversight
- **Technician**: Maintenance execution, inventory access, basic reporting
- **Viewer**: Read-only access to assigned areas

## Database Design Principles

### 1. Foreign Key Relationships
- Follow the "A has B" relationship pattern
- Implement proper cascading deletes where appropriate
- Use composite keys for complex relationships
- Maintain referential integrity

### 2. Audit Trail
- Track all creation and modification events
- Store user information for all changes
- Maintain historical data for compliance
- Implement soft deletes where appropriate

### 3. Performance Considerations
- Index foreign key columns
- Use appropriate data types
- Implement pagination for large datasets
- Optimize queries with eager loading

## File Structure
```
asset_management/
├── app/
│   ├── __init__.py
│   ├── build.py                    # Main build orchestrator
│   ├── models/
│   │   ├── __init__.py
│   │   ├── build.py               # Model build coordinator
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── build.py          # Core models builder
│   │   │   ├── user.py
│   │   │   ├── user_created_base.py
│   │   │   ├── major_location.py
│   │   │   ├── asset_type.py
│   │   │   ├── make_model.py
│   │   │   ├── asset.py
│   │   │   └── event.py
│   │   ├── assets/
│   │   │   ├── __init__.py
│   │   │   ├── build.py                          # Asset models builder
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
│   │   ├── maintenance/
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
│   │   ├── inventory/
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
│   │   ├── dispatch/
│   │   │   ├── __init__.py
│   │   │   ├── build.py          # Dispatch models builder
│   │   │   ├── dispatch.py
│   │   │   ├── dispatch_status.py
│   │   │   └── dispatch_change_history.py
│   │   ├── planning/
│   │   │   ├── __init__.py
│   │   │   ├── build.py          # Planning models builder
│   │   │   ├── asset_type_scheduled_task_plan.py
│   │   │   ├── model_additional_scheduled_task_plan.py
│   │   │   ├── asset_additional_scheduled_task_plan.py
│   │   │   ├── planned_maintenance.py
│   │   │   └── planned_maintenance_status.py
│   │   └── communication/
│   │       ├── __init__.py
│   │       ├── build.py          # Communication models builder
│   │       ├── comment.py
│   │       ├── comment_attachment.py
│   │       ├── comment_history.py
│   │       └── attachment.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── dashboard.py
│   │   │   └── api.py
│   │   ├── assets/
│   │   │   ├── __init__.py
│   │   │   ├── assets.py
│   │   │   ├── asset_types.py
│   │   │   ├── make_models.py
│   │   │   └── locations.py
│   │   ├── maintenance/
│   │   │   ├── __init__.py
│   │   │   ├── events.py
│   │   │   ├── templates.py
│   │   │   ├── actions.py
│   │   │   └── status.py
│   │   ├── inventory/
│   │   │   ├── __init__.py
│   │   │   ├── parts.py
│   │   │   ├── inventory.py
│   │   │   ├── purchase_orders.py
│   │   │   ├── part_demands.py
│   │   │   ├── relocations.py
│   │   │   └── locations.py
│   │   ├── dispatch/
│   │   │   ├── __init__.py
│   │   │   ├── dispatches.py
│   │   │   ├── status.py
│   │   │   └── history.py
│   │   └── planning/
│   │       ├── __init__.py
│   │       ├── scheduled_tasks.py
│   │       ├── planned_maintenance.py
│   │       └── templates.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── components/
│   │   │   ├── __init__.py
│   │   │   ├── forms/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── asset_form.html
│   │   │   │   ├── maintenance_form.html
│   │   │   │   └── inventory_form.html
│   │   │   ├── tables/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── asset_table.html
│   │   │   │   ├── maintenance_table.html
│   │   │   │   └── inventory_table.html
│   │   │   └── modals/
│   │   │       ├── __init__.py
│   │   │       ├── confirmation.html
│   │   │       └── details.html
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── dashboard.html
│   │   │   ├── login.html
│   │   │   └── error.html
│   │   ├── assets/
│   │   │   ├── __init__.py
│   │   │   ├── list.html
│   │   │   ├── detail.html
│   │   │   ├── create.html
│   │   │   ├── edit.html
│   │   │   ├── types/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── list.html
│   │   │   │   └── detail.html
│   │   │   └── locations/
│   │   │       ├── __init__.py
│   │   │       ├── list.html
│   │   │       └── detail.html
│   │   ├── maintenance/
│   │   │   ├── __init__.py
│   │   │   ├── events/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── list.html
│   │   │   │   ├── detail.html
│   │   │   │   └── create.html
│   │   │   ├── templates/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── list.html
│   │   │   │   └── detail.html
│   │   │   └── actions/
│   │   │       ├── __init__.py
│   │   │       ├── list.html
│   │   │       └── detail.html
│   │   ├── inventory/
│   │   │   ├── __init__.py
│   │   │   ├── parts/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── list.html
│   │   │   │   ├── detail.html
│   │   │   │   └── create.html
│   │   │   ├── inventory/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── list.html
│   │   │   │   └── detail.html
│   │   │   ├── purchase_orders/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── list.html
│   │   │   │   └── detail.html
│   │   │   └── relocations/
│   │   │       ├── __init__.py
│   │   │       ├── list.html
│   │   │       └── detail.html
│   │   ├── dispatch/
│   │   │   ├── __init__.py
│   │   │   ├── list.html
│   │   │   ├── detail.html
│   │   │   ├── create.html
│   │   │   └── edit.html
│   │   └── planning/
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
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── asset_service.py
│   │   ├── maintenance_service.py
│   │   ├── inventory_service.py
│   │   ├── dispatch_service.py
│   │   └── planning_service.py
│   ├── utils/
│   │   ├── __init__.py
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
│   │   ├── test_assets.py
│   │   ├── test_maintenance.py
│   │   ├── test_inventory.py
│   │   └── test_dispatch.py
│   ├── test_routes/
│   │   ├── __init__.py
│   │   ├── test_assets.py
│   │   ├── test_maintenance.py
│   │   └── test_inventory.py
│   └── test_services/
│       ├── __init__.py
│       ├── test_asset_service.py
│       └── test_maintenance_service.py
├── requirements.txt
├── config.py
├── run.py
└── README.md
```

## Current Implementation Status

### ✅ Completed Phases
- **Phase 1A**: Core Foundation Tables - Complete
  - User, Location, Asset Type, Make/Model, Asset, Event models implemented
  - Database schema created and tested
  - Build system supports Phase 1 model building

- **Phase 1B**: Core System Initialization - Complete
  - System user creation and initialization
  - Admin user creation workflow
  - Initial data seeding (locations, asset types, make/models, sample assets)
  - User authentication and role management
  - User Created Base Class implementation

- **Phase 2A**: Asset Detail Tables - Complete
  - Detail table infrastructure with virtual template base classes
  - Detail table set containers (AssetTypeDetailTableSet, ModelDetailTableSet)
  - Asset detail tables (PurchaseInfo, VehicleRegistration, ToyotaWarrantyReceipt)
  - Model detail tables (EmissionsInfo, ModelInfo) with duplicate prevention
  - Dynamic assignment system architecture

- **Phase 2B**: Asset Detail Data - Complete
  - Detail table configurations for asset types and models
  - Sample data insertion for testing
  - Configuration management system

- **Phase 3A**: Automatic Detail Insertion System - Complete
  - Conditional import system for detail table sets
  - Asset creation hook with SQLAlchemy event listener
  - Detail table registry system with dynamic class loading
  - Comprehensive error handling and transaction management
  - Automatic detail row creation on asset creation

### 🔄 In Progress
- **Phase 3B**: Automatic Detail Data Updates - In Progress
  - Build system enhancement for Phase 3 support
  - Phase-specific data insertion strategies (update auto-generated rows)
  - Automatic detail row update functionality
  - Testing suite for automatic detail insertion
  - **Key Task**: Implement data update logic for auto-generated detail rows (not manual insertion)

### 📋 Planned Phases
- **Phase 4**: Maintenance System
- **Phase 5**: Dispatch System  
- **Phase 6**: Inventory Management
- **Phase 7**: Planning System

## Development Priorities

### Phase 1A: Core Foundation Tables
1. Flask app setup with SQLAlchemy
2. Core model implementation (User, Location, Asset Type, Make/Model, Asset, Event)
3. Database table creation
4. Basic model relationships

### Phase 1B: Core System Initialization
1. System user creation and initialization
2. Admin user creation workflow
3. Initial data seeding (locations, asset types, make/models, sample assets)
4. User authentication and role management
5. User Created Base Class implementation
6. Database migrations

### Phase 2: Asset Detail Tables
1. **Detail Table Infrastructure**: Implement virtual template base classes with UserCreatedBase inheritance
2. **Detail Table Set Containers**: Create configuration containers for asset type and model detail table assignments
3. **Asset Detail Tables**: Implement purchase info (with event_id), vehicle registration, and Toyota warranty receipt tables
4. **Model Detail Tables**: Implement emissions info and model information tables with duplicate prevention
5. **Dynamic Assignment System**: Implement automatic detail table row creation during asset creation process
6. **Virtual Template System**: Establish base classes with proper foreign key relationships and audit trail functionality
7. **Configuration Management**: Enable admin interface to configure which detail tables apply to which types/models

### Phase 3: Automatic Detail Insertion System
1. **Conditional Import System**: Implement dynamic import of detail table sets based on build phase
2. **Asset Creation Hook**: Add SQLAlchemy event listener for automatic detail row creation
3. **Detail Table Registry**: Implement centralized registry for detail table type management
4. **Error Handling**: Add comprehensive error handling for automatic detail creation
5. **Build System Enhancement**: Update build system to support Phase 3 functionality
6. **Data Insertion Strategy**: Implement phase-specific data insertion with automatic detail updates
7. **Testing Suite**: Create comprehensive tests for automatic detail insertion functionality

#### Phase 3 Data Insertion Strategy
**Key Difference from Phase 2**: Phase 3 data insertion is fundamentally different from Phase 2:

- **Phase 2**: Manually inserts detail table configurations and sample data
- **Phase 3**: Updates automatically generated detail rows that were created during asset creation

**Phase 3 Data Process**:
1. **Asset Creation**: When assets are created in Phase 3, the automatic detail insertion system creates empty detail table rows
2. **Row Population**: Phase 3 data insertion then populates these auto-generated rows with actual information
3. **Update Strategy**: Instead of inserting new rows, the system updates existing auto-generated rows

**Example Flow**:
```
Phase 2 (Manual):
- Create asset → No detail rows created
- Manually insert detail table configurations
- Manually insert sample detail data

Phase 3 (Automatic):
- Create asset → Automatic detail rows created (empty)
- Update auto-generated detail rows with actual data
```

**Benefits of Phase 3 Approach**:
- **Consistency**: All assets automatically get the correct detail table structure
- **Efficiency**: No manual detail table row creation required
- **Flexibility**: Easy to update detail row content without structural changes
- **Automation**: Reduces human error in detail table setup

### Phase 4: Maintenance System
1. Maintenance event creation
2. Template management
3. Work order generation
4. Part demand tracking

### Phase 5: Dispatch System
1. Dispatch creation and management
2. Status tracking
3. User assignment
4. Approval workflows

### Phase 6: Inventory Management
1. Part management
2. Inventory tracking
3. Purchase orders
4. Movement tracking

### Phase 7: Planning System
1. Scheduled maintenance
2. Task templates
3. Resource planning
4. Automated scheduling

## Code Quality Standards
- Follow PEP 8 for Python code
- Use type hints where appropriate
- Implement comprehensive error handling
- Write unit tests for critical functionality
- Use meaningful variable and function names
- Document complex business logic
- Implement proper logging

## System Initialization Process

### 1. Database Setup
```python
def initialize_system():
    """Initialize the system with required base data"""
    # Create system user
    system_user = User(
        id=1,
        username='system',
        email='system@assetmanagement.local',
        is_active=True,
        is_system=True
    )
    
    # Create initial status sets
    status_sets = [
        StatusSet(name='Asset Status', created_by_id=1),
        StatusSet(name='Maintenance Status', created_by_id=1),
        StatusSet(name='Dispatch Status', created_by_id=1),
        StatusSet(name='Inventory Status', created_by_id=1)
    ]
    
    # Create default asset types
    asset_types = [
        AssetType(name='Vehicle', created_by_id=1),
        AssetType(name='Equipment', created_by_id=1),
        AssetType(name='Tool', created_by_id=1)
    ]
```

### 2. Admin User Creation
- First human user registration automatically assigns admin role
- Admin user can then create additional users and assign roles
- System maintains audit trail of all user creation

### 3. Data Migration Strategy
- System user handles all initial data creation
- Migration scripts use system user for data seeding
- User-created data properly tracks creator information

## Security Considerations
- Input validation and sanitization
- SQL injection prevention with SQLAlchemy
- CSRF protection for forms
- User authentication and authorization
- Secure file upload handling
- Audit logging for sensitive operations
- Role-based access control (RBAC)
- System user protection (cannot be modified by regular users)

This prompt provides a comprehensive foundation for building the asset management system. The focus should be on creating a functional, maintainable application that leverages HTMX for dynamic interactions while minimizing JavaScript complexity. 
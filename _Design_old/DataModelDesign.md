# Asset Management System - Data Model Design

## Data Model Overview

The Asset Management System uses a hierarchical, relationship-based data model designed for flexibility, consistency, and maintainability. The system follows a modular approach with clear separation between core entities, asset management, and future system components.

## Core Entities

### 1. User Management
- **User**: Primary user entity with authentication and role management
- **User Created Base Class**: Abstract base class for all user-created entities
- **System User**: Special "system" user for initial data creation and automated processes
- **Major Location**: Geographic locations managed by users
- **Status Sets**: Reusable status configurations

### 2. Asset Management
- **Asset**: Physical assets with properties and meter readings
- **Asset Type**: Categories of assets (Vehicle, Equipment, Tool, etc.)
- **Make and Model**: Manufacturer and model information with asset type association
- **Major Location**: Where assets are located
- **Event**: Activity tracking for assets

## Asset Relationship Architecture

The asset management system uses a hierarchical relationship structure to ensure data consistency and simplify management:

### Asset → MakeModel → AssetType Hierarchy

**1. Asset Model**
- Links directly to MakeModel via `make_model_id`
- Contains asset-specific data: name, serial number, status, location, meter readings
- Gets asset type through MakeModel relationship (property)
- Inherits meter units and specifications from MakeModel
- **Phase 2 Enhancement**: Automatically creates detail table rows on asset creation

**2. MakeModel Model** 
- Links to AssetType via `asset_type_id`
- Contains make/model-specific data: make, model, year, revision, description
- Defines meter units for all assets of this model
- All assets of this make/model inherit the same asset type

**3. AssetType Model**
- Top-level categorization (Vehicle, Equipment, Tool, etc.)
- No direct relationship to assets
- Assets access asset type through their make/model

### Benefits of This Design
- **Consistency**: All assets of the same make/model have identical asset type classification
- **Efficiency**: Asset type is managed once per make/model, not per asset
- **Inheritance**: Assets inherit specifications and units from their make/model
- **Flexibility**: Easy to change asset type for all assets of a make/model
- **Data Integrity**: Prevents inconsistent asset type assignments

## Detail Table System (Phase 2)

The detail table system provides a flexible, extensible approach to storing detailed specifications and configurations for assets and models. This system uses a virtual template approach to allow dynamic addition of detail information without schema changes.

### Detail Table Architecture

**Detail Table Sets**: Container models that group related detail tables
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

### Virtual Template System

**DetailTableVirtualTemplate**: Abstract base class for all detail table functionality
- Inherits from `UserCreatedBase` for audit trail
- Provides common fields: id, created_at, created_by_id, updated_at, updated_by_id
- Includes abstract methods for detail table operations

**AssetDetailVirtual**: Base class for asset-specific detail tables
- Inherits from `DetailTableVirtualTemplate`
- Adds relationship to `Asset` via foreign key (not to detail table set)
- Implements asset-specific validation logic

**ModelDetailVirtual**: Base class for model-specific detail tables
- Inherits from `DetailTableVirtualTemplate`
- Adds relationship to `MakeModel` via foreign key (not to detail table set)
- Implements model-specific validation logic
- Prevents duplicate model detail rows

### Dynamic Detail Table Assignment System

**No direct relationships**: Assets and models do NOT have relationships to detail table sets
**Asset Type Detail Table Sets**: Define which detail tables are available for each asset type
**Model Detail Table Sets**: Define additional detail tables available for specific models
**Dynamic row creation**: On asset creation, system automatically creates detail table rows

### Asset Creation Detail Table Process

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

### Detail Table Row Creation Logic

- **Asset Detail Tables**: Create rows with foreign key to the specific asset
- **Model Detail Tables**: Create rows with foreign key to the model (if not already exists)
- **Duplicate Prevention**: Check for existing model detail rows before creating new ones
- **Cascade Management**: When asset is deleted, remove associated asset detail rows
- **Model Detail Persistence**: Model detail rows persist even when assets are deleted

## Automatic Detail Insertion System (Phase 2)

The automatic detail insertion system provides seamless, automatic population of detail tables when assets are created. This system consists of three main components:

### 1. Conditional Import System
- **Dynamic Import**: Detail table sets are imported conditionally based on build configuration
- **Phase Control**: Automatic detail insertion can be enabled/disabled
- **Registry Management**: Centralized registry of available detail table types

### 2. Asset Creation Hook
- **SQLAlchemy Event Listener**: `after_insert` event triggers automatic detail creation
- **Error Handling**: Comprehensive error handling prevents asset creation failures
- **Transaction Management**: Proper database transaction handling for detail creation

### 3. Detail Table Registry System
- **Centralized Registry**: Maps detail table types to their class model and asset type
- **Dynamic Class Loading**: Uses `__import__` for flexible detail table loading
- **Extensible Design**: Easy to add new detail table types without code changes

### Implementation Details
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

### Process Flow
1. **Asset Creation**: New asset is created in database
2. **Event Trigger**: `after_insert` event fires
3. **Method Call**: `_create_detail_table_rows()` is called
4. **Configuration Lookup**: Retrieve asset type and model detail table sets
5. **Row Creation**: Create detail table rows based on configurations
6. **Linkage**: Establish proper foreign key relationships

## Future System Components

### 3. Maintenance System (Phase 3)
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

### 4. Dispatch System (Phase 4)
- **Dispatches**: Work orders and assignments
- **Dispatch Status**: Current state of dispatches
- **Dispatch Change History**: Audit trail of changes
- **Assets**: Assets assigned to dispatches
- **Users**: Personnel involved in dispatches

### 5. Inventory Management (Phase 5)
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

### 6. Planning System (Phase 6)
- **Asset Type Scheduled Task Plan**: Maintenance schedules by asset type
- **Model Additional Scheduled Task Plan**: Model-specific schedules
- **Asset Additional Scheduled Task Plan**: Asset-specific schedules
- **Planned Maintenance**: Scheduled maintenance events
- **Planned Maintenance Statuses**: Status tracking for planned work

## Key Relationships

### Core Entity Relationships
- **User Created Base Class**: All user-created entities inherit from this base class
- **System User**: Handles all initial data creation and automated processes
- **Admin User**: First user created with full system access
- **Asset Hierarchy**: Asset → MakeModel → AssetType (hierarchical relationship)
- Assets belong to Major Locations
- Assets have Make and Model information with inherited asset type
- MakeModels define asset types and meter units for all assets of that model

### Detail Table Relationships
- **Asset Types have Asset Type Detail Table Sets** that define available detail table types
- **Models have Model Detail Table Sets** that provide additional detail table types
- **Individual assets inherit detail tables** from both their asset type and model through dynamic row creation
- **Detail tables maintain audit trail** through User Created Base Class
- **No direct relationships** between assets/models and detail table sets - assignment is configuration-based
- **Asset detail table rows** link directly to specific assets
- **Model detail table rows** link directly to models and are shared across all assets of that model

### Future System Relationships
- **Maintenance Events** are linked to Assets
- **Dispatches** involve one asset which can be reassigned
- **Users** create and manage all entities (except system-created initial data)
- **Events** track all significant activities
- **Comments and attachments** are linked to various entities
- **Inventory** tracks part locations and quantities

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

## Data Model Evolution

### Phase 1: Core Foundation
- Basic entity relationships established
- User management and authentication
- Asset hierarchy implemented
- Audit trail system in place

### Phase 2: Detail Table System
- Flexible detail table architecture
- Virtual template system
- Automatic detail insertion
- Configuration-based assignments

### Phase 3+: Future Systems
- Maintenance system integration
- Dispatch system relationships
- Inventory management
- Planning system integration

## References
- **Application Design**: See `ApplicationDesign.md` for application architecture and development workflow
- **Implementation Guide**: See `Phase2RestructurePlan.md` for implementation details
- **Development Status**: See individual phase status documents in `phase_*/` directories 
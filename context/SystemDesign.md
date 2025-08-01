# Asset Management System - HTMX Flask App Development Prompt

## Project Overview
Create a comprehensive asset management system using Flask, SQLAlchemy, and HTMX. The application should manage assets, maintenance, dispatch, supply chain, and planning operations with minimal JavaScript and CSS.

## Technology Stack
- **Backend**: Flask with SQLAlchemy ORM
- **Frontend**: HTMX for dynamic interactions, minimal Alpine.js for complex interactions, vanilla JS only when necessary
- **Database**: SQLite (development)
- **Styling**: Minimal CSS, focus on functionality over aesthetics
- **Forms**: Standard HTML forms with HTMX attributes. Minimize form validation during initial development.

## Tiered Database Building Architecture

### Build System Structure
The database building process follows a tiered approach for clear separation of concerns and dependency management:

```
app.py                    # Main entry point
├── app/build.py         # Main build orchestrator
├── app/models/build.py  # Model build coordinator
├── app/models/core/build.py      # Core models builder
├── app/models/assets/build.py    # Asset detail models builder
├── app/models/maintenance/build.py # Maintenance models builder
└── app/models/operations/build.py # Operations models builder
```

### Build Flow
1. **app.py** calls `app.build.build_database()`
2. **app/build.py** orchestrates the overall build process
3. **app/models/build.py** coordinates all model category builds
4. **Category builders** (core, assets, maintenance, operations) build their specific models

### Phase Structure
- **Phase 1A**: Core Foundation Tables (User, Location, Asset Type, Make/Model, Asset, Event)
- **Phase 1B**: Core System Initialization (Initial Data)
- **Phase 2**: Asset Detail Tables (Specifications, Configurations, etc.)
- **Phase 3**: Maintenance System (Events, Templates, Actions, Parts)
- **Phase 4**: Operations System (Dispatch, Tracking, Reporting)

## Data Models & Relationships

### Core Entities

#### 1. User Management
- **User**: Primary user entity with authentication and role management
- **User Created Base Class**: Abstract base class for all user-created entities
- **System User**: Special "system" user for initial data creation and automated processes
- **Major Location**: Geographic locations managed by users
- **Status Sets**: Reusable status configurations

#### 2. Asset Management
- **Asset**: Physical assets with properties
- **Asset Type**: Categories of assets
- **Make and Model**: Manufacturer and model information
- **Major Location**: Where assets are located
- **Event**: Activity tracking for assets

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
- Assets belong to Major Locations
- Assets have Make and Model information
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
│   │   │   ├── build.py          # Asset detail models builder
│   │   │   ├── detail_virtual_template.py
│   │   │   ├── asset_details/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── asset_detail_virtual.py
│   │   │   │   ├── purchase_info.py
│   │   │   │   └── vehicle_registration.py
│   │   │   ├── model_details/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── model_detail_virtual.py
│   │   │   │   └── emissions_info.py
│   │   │   └── detail_table_sets/
│   │   │       ├── __init__.py
│   │   │       ├── asset_detail_table_set.py
│   │   │       └── model_detail_table_set.py
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
1. Asset detail model implementation
2. Virtual template system
3. Asset specifications and configurations
4. Model-specific details

### Phase 3: Maintenance System
1. Maintenance event creation
2. Template management
3. Work order generation
4. Part demand tracking

### Phase 4: Dispatch System
1. Dispatch creation and management
2. Status tracking
3. User assignment
4. Approval workflows

### Phase 5: Inventory Management
1. Part management
2. Inventory tracking
3. Purchase orders
4. Movement tracking

### Phase 6: Planning System
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
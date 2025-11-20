# Asset Management System - System Design

## Overview
This document describes the system architecture, module organization, and design patterns for the Asset Management System. For coding standards and development tools, see [ApplicationDesign.md](ApplicationDesign.md). For phase-by-phase implementation details, see [ImplementationPlan.md](ImplementationPlan.md). Read the [Software Achetecture Patterns](https://www.oreilly.com/content/software-architecture-patterns/) book to understand file structure decisions

## Goals

### Application Features

The Asset Management System provides comprehensive functionality across five major feature areas:

#### 1. Asset Management
- **CRUD Operations**: Create, read, update, delete assets
- **Asset Search**: Filter by type, location, status
- **Asset Details**: Comprehensive asset information display
- **Asset History**: Event timeline for each asset
- **Location Management**: Track asset movements

#### 2. Maintenance Management
- **Maintenance Scheduling**: Create and manage maintenance plans
- **Work Orders**: Generate and track maintenance tasks
- **Template Management**: Reusable maintenance procedures
- **Part Requirements**: Track parts needed for maintenance
- **Maintenance History**: Complete audit trail
- **Three-Tier Portal System**:
  - **Technician Portal**: Workflow-focused interface for completing assigned maintenance tasks
  - **Manager Portal**: Planning and oversight interface for creating templates, schedules, and assigning work
  - **Leader/Admin Portal**: Fleet-wide dashboard for monitoring and managing maintenance operations

#### 3. Dispatch System
- **Dispatch Creation**: 
- **Request portal**
    - allow users to request a vehichle
        - specify details about the request
    - view approval status of request event
    - fill out forms associated with outcome
- **dispatch portal**
    - Allow dispatchers to view requests
    - visualize available assets that fits request criteria
    - assign and edit dispatch outcome
        - Approved
        - Denied
        - Contracted
        - Reimbursed


#### 4. Inventory Management
- **Stock Tracking**: Current inventory levels
- **Part Management**: Add, edit, delete parts
- **Location Tracking**: Where parts are stored
- **Movement History**: Track part movements
- **Purchase Orders**: Procurement management
- **Part Demand** : View Part demand and link purchase orders to demand
- **Relocation Requests**: Part transfer workflow

#### 5. Access Control
 - develop a system that allows admin to assign users to groups and specify which user features assets parts and pages are available to users

### Module Goals

#### Core Module
**Goal**: Provide foundational data models and business logic for users, locations, asset types, make/models, assets, and events.

**Objectives**:
- User management with role-based access control
- Location hierarchy management
- Asset type and make/model categorization
- Asset lifecycle tracking
- Event logging and audit trail

#### Assets Module
**Goal**: Extend core assets with flexible detail table system for asset-specific and model-specific information.

**Objectives**:
- Dynamic detail table creation and management
- Automatic detail table row creation on asset/model creation via factory classes
- Configuration-driven detail table assignments
- Support for both asset-level and model-level details
- Factory-based detail row creation (AssetDetailFactory, ModelDetailFactory)
- SQLAlchemy event listeners that delegate to factory classes

#### Maintenance Module
**Goal**: Provide comprehensive maintenance event management with template-based workflows and three role-based portals optimized for different user needs.

**Objectives**:
- Maintenance event creation and tracking
- Template-based maintenance procedures
- Action item management
- Part demand tracking and approval workflow
- Maintenance workflow automation
- **Technician Portal**:
  - Workflow-focused interface for completing assigned maintenance tasks
  - View and manage assigned work orders and action sets
  - Record maintenance work with comments and attachments
  - Update action status and completion
  - Add tasks to maintenance events
  - Request parts for maintenance
  - View maintenance history and details for assigned assets
- **Manager Portal**:
  - Create and manage maintenance templates (action sets, actions, part demands)
  - Create and manage maintenance plans and schedules
  - View assets with maintenance due based on schedules
  - Assign maintenance events to technicians
  - View active maintenance in progress
  - View and filter onsite events
  - Approve part demands
  - Monitor maintenance progress and completion rates
- **Leader/Admin Portal**:
  - General dashboard for fleet-wide maintenance status
  - View, filter, and edit individual table rows and details
  - Fleet maintenance health overview (KPIs, trends, alerts)
  - Maintenance analytics and reporting
  - System-wide maintenance configuration
  - Access to all maintenance data with full CRUD capabilities

#### Inventory Module
**Goal**: Manage parts, tools, stock levels, and procurement processes with demand-driven purchasing.

**Objectives**:
- Part and tool inventory management
- Stock level tracking and optimization
- Purchase order management
- Movement tracking and location management
- Supplier management
- Part demand viewing and management
- Link purchase orders to part demands
- Relocation request workflow

#### Dispatching Module
**Goal**: Manage vehicle dispatch requests and assignments through dual-portal workflow system.

**Objectives**:
- **Request Portal** (end users):
  - Create vehicle requests with detailed specifications
  - View approval status of requests
  - Fill out forms associated with dispatch outcomes
- **Dispatch Portal** (dispatchers):
  - View all dispatch requests
  - Visualize available assets matching request criteria
  - Assign and edit dispatch outcomes (Approved, Denied, Contracted, Reimbursed)
- Dispatch request creation and management
- Status tracking and updates
- Asset and user assignment
- Multi-level approval workflows

#### Access Control Module
**Goal**: Provide granular permission system for controlling user access to features, assets, parts, and pages.

**Objectives**:
- User group assignment and management
- Feature-level access control
- Asset-level access control
- Part-level access control
- Page/route-level access control
- Admin interface for permission management

## Rules

### Application Architecture

#### Layered Architecture Design

The application follows a **layered architecture pattern** that separates concerns into distinct layers, each with specific responsibilities. This design promotes maintainability, testability, and clear separation of concerns.

#### Layer Structure

```
app/
├── data/              # Data Layer (formerly models/)
│   ├── core/         # Core data models (User, Location, Asset, Event, etc.)
│   ├── assets/       # Asset-related data models
│   ├── maintenance/  # Maintenance data models
│   ├── inventory/    # Inventory data models
│   ├── dispatching/  # Dispatch data models
│   └── supply_items/ # Supply item data models
│
├── buisness/         # Business Logic Layer (formerly domain/)
│   ├── core/         # Core business logic and context managers
│   ├── assets/       # Asset business logic, factories, and context managers
│   ├── maintenance/  # Maintenance business logic, factories, and workflows
│   ├── inventory/    # Inventory business logic and managers
│   └── dispatching/  # Dispatch business logic and managers
│
├── presentation/     # Presentation Layer
│   ├── routes/       # Flask route handlers (formerly routes/)
│   ├── templates/    # Jinja2 HTML templates (formerly templates/)
│   └── static/       # Static files - CSS, JS, images (formerly static/)
│
├── services/         # Services Layer (currently empty)
│   └── [To be populated with presentation services]
│
└── utils/            # Utility functions and helpers
    ├── logger.py     # Logging configuration
    └── build_data.json # Build configuration data
```

#### Layer Responsibilities

##### 1. Data Layer (`app/data/`)
**Purpose**: Database models, schema definitions, and data persistence logic.

**Responsibilities**:
- Define SQLAlchemy models and database tables
- Handle database relationships and foreign keys
- Provide data access abstractions
- Manage database migrations and schema changes
- Contain virtual base classes for inheritance patterns

**Key Principles**:
- Models should be **data-focused** - contain only database structure and basic validation
- No business logic should reside in data models
- Models should be **database-agnostic** where possible (using SQLAlchemy abstractions)
- All models inherit from appropriate base classes (e.g., `UserCreatedBase` for audit trails)

**Example Structure**:
```python
# app/data/core/asset_info/asset.py
class Asset(UserCreatedBase):
    """Data model for assets - contains only database structure"""
    __tablename__ = 'assets'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    # ... database fields only
```

##### 2. Business Logic Layer (`app/buisness/`)
**Purpose**: Business rules, domain logic, context managers, and factories.

**Responsibilities**:
- Implement business rules and validation logic
- Provide context managers for complex operations
- Create factory classes for object creation
- Manage workflows and business processes
- Coordinate between multiple data models
- Handle business-level transactions and operations

**Key Principles**:
- Business logic should be **independent** of presentation concerns
- Context managers should encapsulate complex operations
- Factories should handle object creation with business rules
- Business layer should **not** directly handle HTTP requests/responses
- Business logic should be **reusable** across different presentation layers

**Example Structure**:
```python
# app/buisness/assets/asset_context.py
class AssetContext:
    """Business logic context manager for asset operations"""
    def __init__(self, asset_id):
        self.asset = Asset.query.get(asset_id)
        # Business logic for asset operations
    
    def update_location(self, new_location_id):
        # Business rules for location updates
        # Validation, event creation, etc.
```

##### 3. Presentation Layer (`app/presentation/`)
**Purpose**: User interface, HTTP request handling, and user interaction.

**Responsibilities**:
- Handle HTTP requests and responses
- Render templates with data
- Manage user sessions and authentication
- Process form submissions
- Handle routing and URL generation
- Serve static files (CSS, JavaScript, images)

**Key Principles**:
- Routes should be **thin** - delegate to business layer or services
- Templates should focus on **presentation** only
- Routes should handle HTTP-specific concerns (status codes, headers, etc.)
- Presentation layer should **not** contain business logic
- Use services layer for complex data retrieval needed by routes

**Example Structure**:
```python
# app/presentation/routes/assets/views.py
@assets_bp.route('/<int:asset_id>')
def asset_detail(asset_id):
    # Thin route handler
    ctx = AssetContext(asset_id)
    return render_template('assets/detail.html', asset=ctx.asset)
```

##### 4. Services Layer (`app/services/`)
**Purpose**: Presentation-specific services, data getters, and helper classes used primarily in routes.

**Responsibilities**:
- Provide commonly used classes and functions for presentation
- Create data getters that aggregate information for display
- Handle presentation-specific data transformations
- Provide utilities for routes that don't affect core models or business logic
- Support user browsing and navigation features
- Format data for display (e.g., statistics, summaries, search results)

**Key Principles**:
- Services should **not** modify core data models or business logic
- Services are **presentation-focused** - used primarily by routes
- Services can read from multiple data models to aggregate information
- Services should be **stateless** where possible
- Services should handle presentation-specific concerns (formatting, filtering for display, etc.)

**When to Use Services**:
- Creating dashboard statistics and summaries
- Aggregating data from multiple sources for display
- Formatting data for presentation (dates, numbers, status labels)
- Search and filtering operations for user browsing
- Creating navigation menus and breadcrumbs
- Generating reports and exports for display

**When NOT to Use Services**:
- Business logic that affects core models (use business layer)
- Complex workflows that modify data (use business layer context managers)
- Database operations that change state (use business layer)

**Example Structure** (Future Implementation):
```python
# app/services/dashboard_service.py
class DashboardService:
    """Service for aggregating dashboard statistics"""
    
    @staticmethod
    def get_asset_statistics():
        """Get aggregated asset statistics for dashboard display"""
        return {
            'total_assets': Asset.query.count(),
            'by_location': self._get_assets_by_location(),
            'by_type': self._get_assets_by_type(),
            'recent_activity': self._get_recent_activity()
        }
    
    @staticmethod
    def _get_assets_by_location():
        """Helper to aggregate assets by location"""
        # Presentation-specific data aggregation
        # Does not modify any models
```

#### Layer Interaction Rules

1. **Data → Business**: Business layer can directly use data models
2. **Business → Presentation**: Presentation layer uses business layer for operations
3. **Presentation → Services**: Presentation layer uses services for display data
4. **Services → Data**: Services can read from data models (read-only)
5. **Services → Business**: Services can use business layer for read operations
6. **Presentation → Data** (Exception): Presentation layer can directly use data models **only** under strict conditions (see exception rules below)

**Dependency Flow**:
```
Presentation Layer
    ↓ (uses)
Business Layer
    ↓ (uses)
Data Layer
```

**Services Layer** (side layer):
```
Services Layer
    ↓ (reads from)
Data Layer / Business Layer (read-only)
```

#### Exception: Presentation Layer Direct Data Access

**Rule**: The presentation layer may directly access data models **only** when all of the following conditions are met:

1. **Route is short**: The entire route handler code is **under 20 lines** (excluding comments and docstrings)
2. **Simple read operation**: Only simple query operations (no complex business logic)
3. **Exception comment required**: Must include a visible exception comment explaining why direct data access is used

**Exception Comment Format**:
```python
@main.route('/assets/<int:asset_id>')
def asset_detail(asset_id):
    """
    # EXCEPTION: Direct data access
    # This route directly accesses the data layer because:
    # - Route is simple (under 20 lines)
    # - Only performs basic read operation
    # - No business logic required
    """
    asset = Asset.query.get_or_404(asset_id)  # Direct data access
    return render_template('assets/detail.html', asset=asset)
```

**When to Use Exception**:
- Simple detail views that only fetch and display a single record
- Basic list views with simple filtering
- Simple redirects based on data lookup

**When NOT to Use Exception**:
- Routes with any business logic (use business layer)
- Routes over 20 lines (use business layer or services)
- Routes that modify data (use business layer)
- Routes with complex queries or aggregations (use services)
- Routes that coordinate multiple models (use business layer)

**Example - Valid Exception**:
```python
@assets_bp.route('/<int:asset_id>')
def asset_detail(asset_id):
    """
    # EXCEPTION: Direct data access
    # Simple read-only route under 20 lines
    """
    asset = Asset.query.get_or_404(asset_id)
    return render_template('assets/detail.html', asset=asset)
```

**Example - Invalid (Should Use Business Layer)**:
```python
@assets_bp.route('/<int:asset_id>/update-location', methods=['POST'])
def update_asset_location(asset_id):
    """
    # This route modifies data and has business logic
    # Must use business layer, not direct data access
    """
    asset = Asset.query.get_or_404(asset_id)
    new_location_id = request.form.get('location_id')
    
    # Business logic - should be in business layer
    if asset.current_location_id == new_location_id:
        flash('Asset is already at this location', 'warning')
        return redirect(url_for('assets.detail', asset_id=asset_id))
    
    # Event creation - should be in business layer
    event = Event(
        event_type='location_change',
        description=f'Asset moved to new location',
        asset_id=asset_id
    )
    db.session.add(event)
    
    asset.major_location_id = new_location_id
    db.session.commit()
    flash('Location updated successfully', 'success')
    return redirect(url_for('assets.detail', asset_id=asset_id))
```

**Code Review Checklist**:
When reviewing routes with direct data access exceptions, verify:
- [ ] Route code is under 20 lines (excluding comments/docstrings)
- [ ] Exception comment is present and explains the reason
- [ ] Only read operations are performed
- [ ] No business logic is present
- [ ] No data modifications occur
- [ ] Exception is justified (simple enough to not need business layer)

#### Migration from Old Structure

The application was refactored from a flat structure to a layered architecture:

- **`app/models/`** → **`app/data/`**: Database models moved to data layer
- **`app/domain/`** → **`app/buisness/`**: Business logic moved to business layer
- **`app/routes/`** → **`app/presentation/routes/`**: Routes moved to presentation layer
- **`app/templates/`** → **`app/presentation/templates/`**: Templates moved to presentation layer
- **`app/static/`** → **`app/presentation/static/`**: Static files moved to presentation layer
- **`app/services/`**: New layer created for presentation services

#### Import Guidelines

When importing between layers, follow these patterns:

```python
# ✅ Good - Business layer importing from data layer
from app.data.core.asset_info.asset import Asset

# ✅ Good - Presentation layer importing from business layer
from app.buisness.assets.asset_context import AssetContext

# ✅ Good - Presentation layer importing from services
from app.services.dashboard_service import DashboardService

# ✅ Good - Services importing from data (read-only)
from app.data.core.asset_info.asset import Asset

# ❌ Bad - Data layer importing from business layer
from app.buisness.assets.asset_context import AssetContext  # Don't do this

# ❌ Bad - Business layer importing from presentation layer
from app.presentation.routes.assets import assets_bp  # Don't do this
```

### File Structure Rules

The application follows a layered architecture with the following structure:

```
asset_management/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── auth.py                  # Authentication blueprint
│   ├── build.py                 # Database build orchestrator
│   ├── routes.py                # Legacy routes (deprecated - use presentation/routes)
│   ├── logger.py                # Logger compatibility module
│   │
│   ├── data/                    # Data Layer (database models)
│   │   ├── __init__.py
│   │   ├── core/                # Core data models
│   │   │   ├── user_info/       # User models
│   │   │   ├── asset_info/      # Asset, AssetType, MakeModel
│   │   │   ├── event_info/      # Event, Comment, Attachment
│   │   │   ├── major_location.py
│   │   │   └── build.py
│   │   ├── assets/              # Asset detail models
│   │   │   ├── asset_details/   # Asset-specific detail tables
│   │   │   ├── model_details/   # Model-specific detail tables
│   │   │   └── build.py
│   │   ├── maintenance/         # Maintenance data models
│   │   │   ├── base/            # Base maintenance models
│   │   │   ├── templates/       # Template models
│   │   │   └── build.py
│   │   ├── inventory/           # Inventory data models
│   │   │   ├── base/            # Base inventory models
│   │   │   ├── managers/        # Data layer managers
│   │   │   └── build.py
│   │   ├── dispatching/         # Dispatch data models
│   │   │   ├── outcomes/        # Dispatch outcome models
│   │   │   └── build.py
│   │   └── supply_items/        # Supply item models
│   │       └── build.py
│   │
│   ├── buisness/                # Business Logic Layer
│   │   ├── core/                # Core business logic
│   │   │   ├── asset_context.py
│   │   │   ├── event_context.py
│   │   │   └── make_model_context.py
│   │   ├── assets/              # Asset business logic
│   │   │   ├── factories/       # Asset factories
│   │   │   ├── asset_details_context.py
│   │   │   └── model_detail_context.py
│   │   ├── maintenance/         # Maintenance business logic
│   │   │   ├── factories/       # Maintenance factories
│   │   │   ├── utils/           # Maintenance utilities
│   │   │   └── maintenance_event.py
│   │   ├── inventory/           # Inventory business logic
│   │   │   └── managers/        # Business layer managers
│   │   └── dispatching/          # Dispatch business logic
│   │       └── dispatch_manager.py
│   │
│   ├── presentation/            # Presentation Layer
│   │   ├── routes/              # Flask route handlers
│   │   │   ├── __init__.py      # Route initialization
│   │   │   ├── main.py          # Main routes
│   │   │   ├── core/            # Core entity routes
│   │   │   ├── assets/          # Asset routes
│   │   │   ├── maintenance/     # Maintenance routes
│   │   │   ├── dispatching/     # Dispatch routes
│   │   │   └── supply/          # Supply routes
│   │   ├── templates/           # Jinja2 HTML templates
│   │   │   ├── index.html
│   │   │   ├── core/            # Core entity templates
│   │   │   ├── assets/          # Asset templates
│   │   │   ├── maintenance/     # Maintenance templates
│   │   │   └── ...
│   │   └── static/              # Static files
│   │       ├── css/             # Stylesheets
│   │       └── js/              # JavaScript files
│   │
│   ├── services/                # Services Layer (presentation services)
│   │   └── [To be populated]   # Dashboard services, data getters, etc.
│   │
│   └── utils/                   # Utility functions
│       ├── logger.py            # Logging configuration
│       └── build_data.json      # Build configuration data
│
├── instance/                    # Instance-specific files
├── logs/                        # Application logs
├── migrations/                  # Database migrations
├── Design/                      # Design documentation
├── app.py                       # Application entry point
├── requirements.txt             # Python dependencies
└── README.md                    # Project documentation
```

#### Layer Organization Principles

**Parallel Structure Requirement**: All layers must maintain a **parallel folder structure** that mirrors the data layer organization. This ensures consistency, maintainability, and makes it easy to locate related code across layers.

**Structure Mapping**:
```
Data Layer          →  Business Layer        →  Presentation Layer      →  Services Layer
app/data/           →  app/buisness/         →  app/presentation/routes/ →  app/services/
├── core/           →  ├── core/             →  ├── core/                →  ├── core/
├── assets/          →  ├── assets/           →  ├── assets/             →  ├── assets/
├── maintenance/     →  ├── maintenance/      →  ├── maintenance/         →  ├── maintenance/
├── inventory/       →  ├── inventory/        →  ├── inventory/          →  ├── inventory/
├── dispatching/     →  ├── dispatching/      →  ├── dispatching/        →  ├── dispatching/
└── supply_items/    →  └── supply_items/     →  └── supply/             →  └── supply/
```

**Parallel Structure Rules**:

1. **Data Layer** (`app/data/`): Organized by domain (core, assets, maintenance, etc.)
   - This is the **reference structure** - all other layers mirror this organization
   - Each domain folder contains related data models

2. **Business Layer** (`app/buisness/`): Must mirror data layer structure
   - `app/data/core/` → `app/buisness/core/`
   - `app/data/assets/` → `app/buisness/assets/`
   - `app/data/maintenance/` → `app/buisness/maintenance/`
   - Contains context managers, factories, and business logic for each domain

3. **Presentation Layer Routes** (`app/presentation/routes/`): Must mirror data layer structure
   - `app/data/core/` → `app/presentation/routes/core/`
   - `app/data/assets/` → `app/presentation/routes/assets/`
   - `app/data/maintenance/` → `app/presentation/routes/maintenance/`
   - Contains route handlers organized by domain
   - Routes should generally follow the data layer's subfolder structure as a guideline, with flexibility for practical routing needs (e.g., grouping related routes, RESTful organization)

4. **Services Layer** (`app/services/`): Must mirror data layer structure
   - `app/data/core/` → `app/services/core/`
   - `app/data/assets/` → `app/services/assets/`
   - `app/data/maintenance/` → `app/services/maintenance/`
   - Contains presentation services organized by domain

**Benefits of Parallel Structure**:
- **Easy Navigation**: Find related code across layers quickly
- **Consistency**: Clear organization pattern throughout the codebase
- **Maintainability**: Changes to one domain are localized across all layers
- **Onboarding**: New developers can easily understand the structure
- **Code Review**: Reviewers can check all layers of a feature at once

**Example - Asset Domain Across Layers**:
```
app/data/assets/
├── asset_detail_virtual.py
├── asset_details/
│   ├── purchase_info.py
│   └── vehicle_registration.py
└── model_details/
    └── emissions_info.py

app/buisness/assets/
├── asset_context.py
├── asset_details_context.py
├── factories/
│   ├── asset_factory.py
│   └── asset_detail_factory.py
└── asset_details/
    └── asset_details_struct.py

app/presentation/routes/assets/
├── views.py
├── detail_tables.py
└── model_details.py

app/services/assets/
├── asset_statistics.py
├── asset_search.py
└── asset_formatters.py
```

**Naming Consistency**:
- Use the same domain names across all layers
- If data layer uses `supply_items/`, business layer should use `supply_items/` (or `supply/` if abbreviated consistently)
- Presentation routes may use abbreviated names (e.g., `supply/` instead of `supply_items/`) but should be clearly mappable

**Exception - Presentation Templates and Static**:
- Templates (`app/presentation/templates/`) may have a different structure optimized for template organization but should generally follow the same structure
- Static files (`app/presentation/static/`) may have a different structure optimized for user interface accessability
- These are presentation-specific and don't need to mirror the data layer structure

For detailed file structure information, see [application_structure.md](application_structure.md) and [application_structure.json](application_structure.json).

### Database Building Architecture

#### Build System Structure
The database building process follows a tiered approach for clear separation of concerns and dependency management:

```
app.py                    # Main entry point
├── app/build.py         # Main build orchestrator
├── app/data/core/
│   ├── build.py         # Core models builder
│   └── [init_data via build.py] # Core data initialization
├── app/data/assets/
│   ├── build.py         # Asset detail models builder
│   └── [init_data via build.py] # Asset data initialization
├── app/data/maintenance/
│   ├── build.py         # Maintenance models builder
│   └── [init_data via build.py] # Maintenance data initialization
├── app/data/inventory/
│   ├── build.py         # Inventory models builder
│   └── [init_data via build.py] # Inventory data initialization
└── app/data/dispatching/
    ├── build.py         # Dispatch models builder
    └── [init_data via build.py] # Dispatch data initialization
```

**Note**: The build system now uses `app/data/` instead of `app/models/` to align with the layered architecture.

#### Module Independence
Each module should contain its own independent build and data initialization files:

1. **`build.py`**: Handles table creation and model building for that module
2. **`init_data.py`**: Handles data initialization and configuration loading for that module
3. **Centralized Data**: All modules read from `app/utils/build_data.json` for consistency
4. **Module Isolation**: Each module can be built and initialized independently

#### Build Flow
1. **app.py** calls `app.build.build_database()`
2. **app/build.py** orchestrates the overall build process with phase-specific options
3. **Category builders** in `app/data/*/build.py` coordinate their specific model builds
4. **Data layer builders** (core, assets, maintenance, inventory, dispatching) build their specific models

#### Model Build System
The build system supports flexible phase-specific building:

```python
def build_database(build_phase='all', data_phase='all'):
    """
    build_phase options:
    - 'phase1': Core Foundation Tables only (Model Phase 1A)
    - 'phase2a': Phase 1 + Asset Detail Infrastructure (Model Phase 2A)
    - 'phase2b': Phase 1 + Phase 2A + Automatic Detail Insertion (Model Phase 2B)
    - 'all': All phases (default = phase2b)
    
    data_phase options:
    - 'phase1': Core System Initialization and basic asset and event creation
    - 'phase2a': Phase 1 + Manual Detail Table Testing (Model Phase 2A)
    - 'phase2b': Phase 1 Core System Initialization + Automatic Detail Creation toggle + create assets and details
    - 'all': highest phase (default = phase2b)
    - 'none': Skip data insertion
    """
```

### User Management System

#### 1. User Hierarchy
- **System User**: Special user with ID 1, handles all initial data creation and automated processes
- **Admin User**: First human user created with full system access and privileges
- **Regular Users**: Standard users with role-based permissions
- **Guest Users**: Limited access users (if needed)

#### 2. User Created Base Class
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

#### 3. System Initialization
- **System User Creation**: Automatically created during database initialization
- **Initial Data**: All seed data (status sets, default asset types, etc.) created by system user
- **Admin Setup**: First human user automatically becomes admin
- **Audit Trail**: All system-created records properly tracked

#### 4. User Roles and Permissions
- **Admin**: Full system access, user management, system configuration
- **Manager**: Asset management, maintenance planning, dispatch oversight
- **Technician**: Maintenance execution, inventory access, basic reporting
- **Viewer**: Read-only access to assigned areas

## References
- **Application Design**: See [ApplicationDesign.md](ApplicationDesign.md) for coding standards and development tools
- **Implementation Plan**: See [ImplementationPlan.md](ImplementationPlan.md) for phase-by-phase implementation details
- **Data Model Design**: See `DataModelDesign.md` for detailed entity relationships and database design
- **Widget Components**: See [widgets.md](widgets.md) for tracked widget components
- **Application Structure**: See [application_structure.md](application_structure.md) for detailed file structure

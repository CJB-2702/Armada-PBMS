# Asset Management System - Application Design

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

### Layered Architecture Compliance

All code must follow the layered architecture pattern. This is a **mandatory coding standard**.

#### Layer Placement Rules

1. **Database Models** → `app/data/`
   - All SQLAlchemy models must be in the data layer
   - Models should contain only database structure, no business logic
   - Use `app.data.*` for all model imports
   - **Must maintain parallel structure** - organize by domain (core, assets, maintenance, etc.)

2. **Business Logic** → `app/buisness/`
   - Context managers, factories, and business rules go in business layer
   - Business logic should be independent of presentation
   - Use `app.buisness.*` for business logic imports
   - **Must mirror data layer structure** - `app/data/core/` → `app/buisness/core/`

3. **Route Handlers** → `app/presentation/routes/`
   - All Flask routes must be in the presentation layer
   - Routes should be thin and delegate to business layer or services
   - Use `app.presentation.routes.*` for route imports
   - **Must mirror data layer structure** - `app/data/core/` → `app/presentation/routes/core/`
      - Routes should generally follow the data layer's subfolder structure as a guideline, with flexibility for practical routing needs (e.g., grouping related routes, RESTful organization)

4. **Templates and Static Files** → `app/presentation/`
   - All Jinja2 templates in `app/presentation/templates/`
   - All static files (CSS, JS) in `app/presentation/static/`
   - Templates and static files may have their own optimized structure (exception to parallel structure)

5. **Presentation Services** → `app/services/`
   - Data getters and aggregation functions for routes
   - Presentation-specific utilities that don't modify core models
   - Dashboard statistics, search helpers, formatting utilities
   - Use `app.services.*` for service imports
   - **Must mirror data layer structure** - `app/data/core/` → `app/services/core/`

#### Parallel Structure Requirement

**Mandatory**: All layers (data, business, presentation/routes, services) must maintain parallel folder structures that mirror the data layer organization.

**Example - Core Domain**:
```
app/data/core/              # Reference structure
app/buisness/core/          # Mirrors data/core/
app/presentation/routes/core/  # Mirrors data/core/
app/services/core/          # Mirrors data/core/
```

**Example - Assets Domain**:
```
app/data/assets/            # Reference structure
app/buisness/assets/       # Mirrors data/assets/
app/presentation/routes/assets/  # Mirrors data/assets/
app/services/assets/       # Mirrors data/assets/
```

**Benefits**:
- Easy to find related code across all layers
- Consistent organization throughout codebase
- Domain changes are localized across layers
- Faster onboarding for new developers

#### Import Standards

```python
# ✅ Correct - Data layer imports
from app.data.core.asset_info.asset import Asset
from app.data.core.user_info.user import User

# ✅ Correct - Business layer imports
from app.buisness.assets.asset_context import AssetContext
from app.buisness.maintenance.maintenance_event import MaintenanceEvent

# ✅ Correct - Presentation layer imports
from app.presentation.routes.assets import assets_bp
from app.services.dashboard_service import DashboardService

# ❌ Incorrect - Wrong layer imports
from app.models.core.asset import Asset  # Old path - don't use
from app.domain.assets import AssetContext  # Old path - don't use
```

#### Layer Violation Prevention

- **Never** put business logic in data models
- **Never** put presentation logic in business layer
- **Never** modify core models from services layer (read-only)
- **avoid** putting database queries directly in routes (use business layer or services)

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
## HTMX Implementation Guidelines

### 1. Form Handling
- Use standard HTML forms with `hx-post`, `hx-get`, `hx-put`, `hx-delete`
- Implement form validation with server-side responses
- Use `hx-target` to update specific page sections
- Leverage `hx-swap` for smooth transitions

### 1.1. Card/Widget Updates (Preferred Pattern)
- **Prefer full page GET requests** with `hx-target` and `hx-swap` extracting/replacing the widget container itself

- **Avoid creating dedicated routes** for widget subsection replacement when possible
- This approach simplifies routing, improves cacheability, and maintains consistent page state

**Preferred Pattern**:
```html
<!-- Widget container that updates itself -->
<div id="event-widget-container"
     hx-get="{{ url_for('maintenance.do_maintenance', action_set_id=action_set_id) }}"
     hx-trigger="every 5s"
     hx-target="this"
     hx-select="#event-widget-container"
     hx-swap="outerHTML">
    <!-- Widget content -->
</div>
```

**Benefits**:
- Single route handles both full page and widget updates
- Better browser caching (full page responses are cacheable)
- Consistent state between full page and widget views
- Simpler route structure (no separate widget endpoints)
- Easier debugging (full page always available)

**When to Use Dedicated Widget Routes**:
- Widget requires significantly different data than full page
- Widget updates are very frequent and full page is expensive
- Widget needs to be embeddable in multiple contexts with different parameters

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

## Application Architecture

### Layered Architecture Design

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

### Tiered Database Building Architecture

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



#### Phase Structure - Staged Implementation Approach

**Development Pattern**: Model Phase → App Phase → Validation Phase for each development stage

**Why Staged Implementation?**
This approach provides immediate validation and feedback at each stage:
- **Early Problem Detection**: Issues are caught early before building too much
- **Incremental Testing**: Each phase can be fully tested before moving to the next
- **User Feedback**: Can get user feedback on each completed phase
- **Risk Mitigation**: Smaller, manageable chunks reduce development risk
- **Motivation**: Visible progress keeps development momentum high

**Development Workflow**:
1. **Build Model Phase**: Implement database models and data layer
2. **Build App Phase**: Implement application layer and user interface
3. **Validation Phase**: Test and validate the complete phase
4. **Iterate if Needed**: Refine based on testing and feedback
5. **Move to Next Phase**: Continue with next Model → App → Validation cycle

```
Phase 1: Core Foundation
    Phase 1A: Database Foundation
        Model
               Core table creation (User, Location, Asset Type, Make/Model, Asset, Event)
               Primary key and foreign key validation
               Database schema verification
        App
              Basic CRUD operations for all core entities
              Database connection and setup interface
              Error handling and validation
        Validation
              Backend data insertion testing
              Database integrity verification
              Basic CRUD functionality testing

    Phase 1B: System Initialization
        Model
               System user creation and admin user setup
               Initial data insertion (asset types, locations)
               User authentication model implementation
        App
              Authentication system implementation
              Login/logout functionality
              User session management
              Basic setup interface
        Validation
              User authentication testing
              Session management verification
              Initial data validation

    Phase 1C: Complete Core UI
        Model
               (No additional model changes - foundation complete)
        App
              Complete CRUD interface for all core models
              Advanced filtering and search capabilities
              Relationship-aware forms and displays
              User management interface
              Location management interface
              Asset type management interface
              Make/model management interface
              Asset management interface with relationships
              Event tracking interface
        Validation
              End-to-end user interface testing
              Cross-browser compatibility testing
              User workflow validation
              Performance testing for UI operations

Phase 2: Asset Detail System
    Phase 2A: Detail Infrastructure
        Model
               Detail table creation (purchase info, registration, warranty)
               Virtual template base classes implementation
               Detail table set containers
               Foreign key relationships to assets
        App
              Detail table management interface
              Configuration interface for detail assignments
              Detail table creation and editing forms
        Validation
              Detail table structure testing
              Foreign key relationship validation
              Configuration interface testing

    Phase 2B: Automatic Detail Insertion
        Model
               Asset creation hooks implementation
               Detail table registry system
               SQLAlchemy event listeners
               Automatic detail row creation logic
        App
              Automatic detail creation features
              Asset creation with detail generation
              Detail management interface
              Error handling for automatic insertion
        Validation
              Automatic detail insertion testing
              Asset creation workflow validation
              Error handling verification

    Phase 2C: Detail Data Management
        Model
               Detail data update mechanisms
               Configuration management system
               Data validation rules
        App
              Detail data management interface
              Configuration management tools
              Data update workflows
              Bulk operations interface
        Validation
              Data management workflow testing
              Configuration system validation
              Bulk operations testing
Phase 4: Dispatch System
    Phase 4A: Dispatch Foundation
        Model
               Work order tables
               Status tracking system
               User assignment mechanisms
        App
              Work order management interface
              Status tracking interface
              User assignment tools
        Validation
              Work order workflow testing
              Status tracking validation
              Assignment system testing

    Phase 4B: Dispatch Operations
        Model
               Dispatch optimization
               Route planning
               Real-time tracking
        App
              Dispatch optimization interface
              Route planning tools
              Real-time tracking interface
        Validation
              Optimization testing
              Route planning validation
              Tracking system testing
Phase 3: Maintenance System
    Phase 3A: Maintenance Foundation
        Model
               Maintenance event tables
               Maintenance templates
               Maintenance actions
               Parts and materials tracking
        App
              Maintenance event management interface
              Template management system
              Action tracking interface
              Parts management interface
        Validation
              Maintenance workflow testing
              Template system validation
              Parts tracking verification

    Phase 3B: Maintenance Workflows
        Model
               Workflow state management
               Maintenance scheduling
               Resource allocation
        App
              Workflow management interface
              Scheduling tools
              Resource management interface
        Validation
              Workflow testing
              Scheduling validation
              Resource allocation testing

Phase 5: Inventory Management
    Phase 5A: Inventory Foundation
        Model
               Parts inventory tables
               Stock level tracking
               Purchase order system
        App
              Inventory management interface
              Stock level monitoring
              Purchase order management
        Validation
              Inventory workflow testing
              Stock tracking validation
              Purchase order testing

    Phase 5B: Inventory Operations
        Model
               Reorder point management
               Supplier management
               Cost tracking
        App
              Reorder point interface
              Supplier management tools
              Cost tracking interface
        Validation
              Reorder system testing
              Supplier management validation
              Cost tracking verification

Phase 6: Planning System
    Phase 6A: Planning Foundation
        Model
               Scheduled maintenance tables
               Resource planning system
               Calendar integration
        App
              Scheduled maintenance interface
              Resource planning tools
              Calendar management interface
        Validation
              Scheduling workflow testing
              Resource planning validation
              Calendar integration testing

    Phase 6B: Advanced Planning
        Model
               Predictive maintenance
               Resource optimization
               Budget planning
        App
              Predictive maintenance interface
              Resource optimization tools
              Budget planning interface
        Validation
              Predictive system testing
              Optimization validation
              Budget planning testing
```

**Implementation Flow**:
```
Model 1A → App 1A → Validation 1A → Model 1B → App 1B → Validation 1B → Model 1C → App 1C → Validation 1C →
Model 2A → App 2A → Validation 2A → Model 2B → App 2B → Validation 2B → Model 2C → App 2C → Validation 2C →
Model 3A → App 3A → Validation 3A → Model 3B → App 3B → Validation 3B →
Model 4A → App 4A → Validation 4A → Model 4B → App 4B → Validation 4B →
Model 5A → App 5A → Validation 5A → Model 5B → App 5B → Validation 5B →
Model 6A → App 6A → Validation 6A → Model 6B → App 6B → Validation 6B
```

**Validation Criteria**:
- **Model Validation**: Database structure, relationships, constraints working correctly
- **App Validation**: User interface functional, workflows complete, error handling working
- **Integration Validation**: Model and App work together seamlessly
- **User Validation**: End users can complete intended workflows successfully
- **Performance Validation**: System performs acceptably under expected load

## File Structure

The application follows a layered architecture with the following structure:
When creating files and classes Design application_structure.md should also be updated periodically and before pull requests.

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

### Layer Organization Principles

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

## Development Workflow

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

### Phase 1C: Core Model CRUD Operations and User Interface

> **Note**: This phase implements complete CRUD operations and user interface screens for all core models, respecting the hierarchical relationships defined in the data model.

**Key Focus Areas:**
- Complete CRUD interface for all core models (User, Location, Asset Type, Make/Model, Asset, Event)
- Advanced filtering and search capabilities
- Relationship-aware forms and displays
- Hierarchical navigation reflecting data relationships
- Comprehensive data validation and integrity checks
- Performance optimization for relationship-heavy data

**Implementation Priority:**
1. User Management (foundation for all other operations)
2. Major Location Management (required for asset placement)
3. Asset Type Management (required for make/model categorization)
4. Make and Model Management (required for asset creation)
5. Asset Management Enhancement (builds on existing functionality)
6. Event Management (tracks all system activities)

> **For detailed implementation tasks and specific requirements, see [Phase 1C Application Plan](phase1_Core/ApplicationPlan.md)**

### Phase 2: Asset Detail System Application Implementation

> **Note**: For detailed information about the data model design, entity relationships, and database schema for the Asset Detail System, see the **[Data Model Design Document](DataModelDesign.md)**.

This phase focuses on the application-layer implementation tasks required to support the Asset Detail System.

**Phase Structure:**
- **Phase 2A**: Detail Table Infrastructure Application Layer
- **Phase 2B**: Automatic Detail Insertion Application Layer  
- **Phase 2C**: Detail Data Management Application Layer

**Key Focus Areas:**
- Build system integration and command line interface enhancements
- Asset model integration with automatic detail insertion hooks
- Detail table registry system and SQLAlchemy event listeners
- Configuration management interfaces for detail table assignments
- Comprehensive error handling and transaction management
- Testing framework integration and validation

**Integration Requirements:**
- Builds upon Phase 1 core models and relationships
- Integrates with existing Asset, MakeModel, and AssetType models
- Maintains compatibility with existing user management system
- Preserves audit trail functionality

> **For detailed implementation tasks and specific requirements, see [Phase 2 Application Plan](phase2_AssetDetails/ApplicationPlan.md)**

### Phase 3: Dispatch System
**Key Focus Areas:**
- Work order creation and management
- Real-time status tracking and updates
- User assignment and workload balancing
- Multi-level approval workflows
- Dispatch optimization and route planning

**Integration Requirements:**
- Links dispatches to specific assets and maintenance events
- Integrates with user management and role-based access control
- Connects with maintenance system for work order generation
- Provides real-time tracking and notification capabilities

> **For detailed implementation tasks and specific requirements, see [Phase 3 Application Plan](phase3_Dispatching/ApplicationPlan.md)**

### Phase 4: Maintenance System
**Key Focus Areas:**
- Maintenance event creation and scheduling
- Template-based maintenance procedures
- Work order generation and tracking
- Part demand tracking and management
- Maintenance workflow automation

**Integration Requirements:**
- Links maintenance events to specific assets
- Integrates with inventory system for part requirements
- Connects with dispatch system for work order execution
- Provides predictive maintenance capabilities

> **For detailed implementation tasks and specific requirements, see [Phase 4 Application Plan](Phase4_Maintnence/ApplicationPlan.md)**

### Phase 5: Inventory Management
**Key Focus Areas:**
- Parts and materials management
- Stock level tracking and optimization
- Purchase order management and tracking
- Movement tracking and location management
- Supplier management and cost tracking

**Integration Requirements:**
- Links parts to asset maintenance requirements
- Integrates with maintenance system for part demand
- Connects with planning system for resource optimization
- Provides supply chain management capabilities

> **For detailed implementation tasks and specific requirements, see [Phase 5 Application Plan](Phase5_Supply/ApplicationPlan.md)**

### Phase 6: Planning System
**Key Focus Areas:**
- Scheduled maintenance planning and automation
- Resource planning and optimization
- Budget planning and cost management
- Calendar integration and conflict resolution
- Predictive maintenance and analytics

**Integration Requirements:**
- Integrates with all previous phases for comprehensive planning
- Uses maintenance history for predictive planning
- Connects with inventory system for resource optimization
- Provides advanced analytics and reporting capabilities

> **For detailed implementation tasks and specific requirements, see [Phase 6 Application Plan](Phase6_Planning/ApplicationPlan.md)**

## Code Quality Standards
- Follow PEP 8 for Python code
- Use type hints where appropriate
- Implement comprehensive error handling
- Write unit tests for critical functionality
- Use meaningful variable and function names
- Document complex business logic
- Implement proper logging

## Security Considerations
- Input validation and sanitization
- SQL injection prevention with SQLAlchemy
- CSRF protection for forms
- User authentication and authorization
- Secure file upload handling
- Audit logging for sensitive operations
- Role-based access control (RBAC)
- System user protection (cannot be modified by regular users)

## Current Implementation Status

### ✅ Completed Phases
- **Phase 1A**: Core Foundation Tables - Complete
- **Phase 1B**: Core System Initialization - Complete
- **Phase 2A**: Asset Detail Infrastructure - Complete
- **Phase 2B**: Automatic Detail Insertion - Complete
- **Phase 2C**: Detail Data Management - Complete

### 🔄 In Progress
- None currently

### 📋 Planned Phases
- **Phase 3**: Maintenance System (Events, Templates, Actions, Parts)
- **Phase 4**: Dispatch System (Work Orders, Status Tracking, User Assignment)
- **Phase 5**: Inventory Management (Parts, Stock, Purchase Orders)
- **Phase 6**: Planning System (Scheduled Maintenance, Resource Planning)

## References
- **Data Model Design**: See `DataModelDesign.md` for detailed entity relationships and database design
- **Implementation Guide**: See `Phase2RestructurePlan.md` for implementation details
- **Development Status**: See individual phase status documents in `phase_*/` directories 
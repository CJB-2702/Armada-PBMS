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

### Tiered Database Building Architecture

#### Build System Structure
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

#### Module Independence
Each module should contain its own independent build and data initialization files:

1. **`build.py`**: Handles table creation and model building for that module
2. **`init_data.py`**: Handles data initialization and configuration loading for that module
3. **Centralized Data**: All modules read from `app/utils/build_data.json` for consistency
4. **Module Isolation**: Each module can be built and initialized independently

#### Build Flow
1. **app.py** calls `app.build.build_database()`
2. **app/build.py** orchestrates the overall build process with phase-specific options
3. **app/models/build.py** coordinates all model category builds
4. **Category builders** (core, assets, maintenance, operations) build their specific models

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
See [context/plannedFileStructure.md](context/plannedFileStructure.md) for the detailed planned file structure.


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
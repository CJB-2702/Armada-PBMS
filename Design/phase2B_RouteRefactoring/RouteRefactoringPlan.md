# Phase 3A: Route Refactoring Plan

## Overview
This document provides a detailed plan for refactoring the current route structure to prepare for the new application sections (Core Management, Asset Management, Dispatching, Maintenance, Supply, Planning) while maintaining backward compatibility and ensuring a smooth transition.

## Current State Analysis

### Current Route Structure
```
Current Application Routes:
├── /                           # Main index (dashboard-like content)
├── /dashboard                   # Enhanced dashboard with statistics
├── /search                      # Global search functionality
├── /help                        # Help and documentation
├── /about                       # About page
├── /core/                       # Core management routes
│   ├── /core/assets            # Asset CRUD operations
│   ├── /core/events            # Event management
│   ├── /core/users             # User management
│   ├── /core/locations         # Location management
│   ├── /core/asset-types       # Asset type management
│   └── /core/make-models       # Make/Model management
├── /assets/                     # Asset detail routes
│   ├── /assets/detail-tables   # Asset detail table management
│   └── /assets/model-details   # Model detail management
├── /attachments/                # File attachment handling
└── /comments/                   # Comment system
```

### Current Blueprint Organization
```python
# Current Blueprint Registration (app/routes/__init__.py)
app.register_blueprint(auth)                    # /auth
app.register_blueprint(main)                    # / (main routes)
app.register_blueprint(core.bp, url_prefix='/core')
app.register_blueprint(assets.bp, url_prefix='/assets')
app.register_blueprint(events.bp, url_prefix='/core')
app.register_blueprint(core_assets.bp, url_prefix='/core', name='core_assets')
app.register_blueprint(locations.bp, url_prefix='/core')
app.register_blueprint(asset_types.bp, url_prefix='/core')
app.register_blueprint(make_models.bp, url_prefix='/core')
app.register_blueprint(users.bp, url_prefix='/core')
app.register_blueprint(comments.bp, url_prefix='')
app.register_blueprint(attachments.bp, url_prefix='')
```

## Target State

### New Application Structure
```
New Route Structure:
├── /                           # Application hub (new main index)
├── /core/                      # Core Management
│   ├── /core/dashboard         # Core system dashboard
│   ├── /core/users             # User management
│   ├── /core/locations         # Location management
│   ├── /core/asset-types       # Asset type management
│   ├── /core/make-models       # Make/Model management
│   └── /core/events            # System events
├── /assets/                     # Asset Management
│   ├── /assets/dashboard       # Asset management dashboard
│   ├── /assets/list            # Asset listing and management
│   ├── /assets/<id>            # Asset detail view
│   ├── /assets/create          # Asset creation
│   ├── /assets/<id>/edit       # Asset editing
│   ├── /assets/<id>/all-details # Asset all details view
│   ├── /assets/detail-tables   # Asset detail table management
│   └── /assets/model-details   # Model detail management
├── /dispatch/                   # Dispatching (Phase 3B)
├── /maintenance/                # Maintenance (Phase 4)
├── /supply/                     # Supply Management (Phase 5)
├── /planning/                   # Planning (Phase 6)
├── /attachments/                # File management (global)
├── /comments/                   # Comment system (global)
└── /search                      # Global search (global)
```

## Detailed Migration Plan

### Step 1: Create Application Hub

#### 1.1 Create Hub Blueprint
**File**: `app/routes/hub.py`
```python
from flask import Blueprint, render_template
from flask_login import login_required

bp = Blueprint('hub', __name__)

@bp.route('/')
@login_required
def index():
    """Main application hub with links to all sections"""
    return render_template('hub/index.html')
```

#### 1.2 Create Hub Template
**File**: `app/templates/hub/index.html`
```html
{% extends "base.html" %}

{% block title %}Asset Management System - Home{% endblock %}

{% block content %}
<div class="container">
    <div class="row">
        <div class="col-12">
            <h1>Asset Management System</h1>
            <p class="lead">Welcome to the Asset Management System. Select a section to get started.</p>
        </div>
    </div>
    
    <div class="row">
        <div class="col-md-4">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Core Management</h5>
                    <p class="card-text">Manage users, locations, asset types, and system events.</p>
                    <a href="{{ url_for('core.dashboard') }}" class="btn btn-primary">Go to Core Management</a>
                </div>
            </div>
        </div>
        
        <div class="col-md-4">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Asset Management</h5>
                    <p class="card-text">Manage assets, view details, and handle asset-specific information.</p>
                    <a href="{{ url_for('assets.dashboard') }}" class="btn btn-primary">Go to Asset Management</a>
                </div>
            </div>
        </div>
        
        <div class="col-md-4">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Dispatching</h5>
                    <p class="card-text">Manage work orders, assignments, and dispatch operations.</p>
                    <a href="#" class="btn btn-secondary disabled">Coming Soon</a>
                </div>
            </div>
        </div>
    </div>
    
    <div class="row mt-4">
        <div class="col-md-4">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Maintenance</h5>
                    <p class="card-text">Schedule maintenance, manage work orders, and track maintenance activities.</p>
                    <a href="#" class="btn btn-secondary disabled">Coming Soon</a>
                </div>
            </div>
        </div>
        
        <div class="col-md-4">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Supply</h5>
                    <p class="card-text">Manage inventory, parts, and purchase orders.</p>
                    <a href="#" class="btn btn-secondary disabled">Coming Soon</a>
                </div>
            </div>
        </div>
        
        <div class="col-md-4">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">Planning</h5>
                    <p class="card-text">Plan schedules, forecasts, and strategic planning.</p>
                    <a href="#" class="btn btn-secondary disabled">Coming Soon</a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

### Step 2: Create Core Management Dashboard

#### 2.1 Create Core Dashboard Blueprint
**File**: `app/routes/core/dashboard.py`
```python
from flask import Blueprint, render_template
from flask_login import login_required
from app.models.core.asset import Asset
from app.models.core.asset_type import AssetType
from app.models.core.make_model import MakeModel
from app.models.core.major_location import MajorLocation
from app.models.core.user import User
from app.models.core.event import Event

bp = Blueprint('dashboard', __name__)

@bp.route('/dashboard')
@login_required
def dashboard():
    """Core management dashboard"""
    # Get basic statistics
    total_assets = Asset.query.count()
    total_asset_types = AssetType.query.count()
    total_make_models = MakeModel.query.count()
    total_locations = MajorLocation.query.count()
    total_users = User.query.count()
    total_events = Event.query.count()
    
    # Get recent events
    recent_events = Event.query.order_by(Event.timestamp.desc()).limit(10).all()
    
    # Get assets by location
    locations_with_assets = []
    for location in MajorLocation.query.all():
        asset_count = Asset.query.filter_by(major_location_id=location.id).count()
        if asset_count > 0:
            locations_with_assets.append({
                'location': location,
                'asset_count': asset_count
            })
    
    return render_template('core/dashboard.html',
                         total_assets=total_assets,
                         total_asset_types=total_asset_types,
                         total_make_models=total_make_models,
                         total_locations=total_locations,
                         total_users=total_users,
                         total_events=total_events,
                         recent_events=recent_events,
                         locations_with_assets=locations_with_assets)
```

#### 2.2 Create Core Dashboard Template
**File**: `app/templates/core/dashboard.html`
```html
{% extends "base.html" %}

{% block title %}Core Management Dashboard{% endblock %}

{% block content %}
<div class="container">
    <div class="row">
        <div class="col-12">
            <h1>Core Management Dashboard</h1>
            <p class="lead">System overview and core entity management.</p>
        </div>
    </div>
    
    <!-- Statistics Cards -->
    <div class="row mb-4">
        <div class="col-md-2">
            <div class="card text-center">
                <div class="card-body">
                    <h5 class="card-title">{{ total_assets }}</h5>
                    <p class="card-text">Assets</p>
                </div>
            </div>
        </div>
        <div class="col-md-2">
            <div class="card text-center">
                <div class="card-body">
                    <h5 class="card-title">{{ total_users }}</h5>
                    <p class="card-text">Users</p>
                </div>
            </div>
        </div>
        <div class="col-md-2">
            <div class="card text-center">
                <div class="card-body">
                    <h5 class="card-title">{{ total_locations }}</h5>
                    <p class="card-text">Locations</p>
                </div>
            </div>
        </div>
        <div class="col-md-2">
            <div class="card text-center">
                <div class="card-body">
                    <h5 class="card-title">{{ total_asset_types }}</h5>
                    <p class="card-text">Asset Types</p>
                </div>
            </div>
        </div>
        <div class="col-md-2">
            <div class="card text-center">
                <div class="card-body">
                    <h5 class="card-title">{{ total_make_models }}</h5>
                    <p class="card-text">Make/Models</p>
                </div>
            </div>
        </div>
        <div class="col-md-2">
            <div class="card text-center">
                <div class="card-body">
                    <h5 class="card-title">{{ total_events }}</h5>
                    <p class="card-text">Events</p>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Quick Actions -->
    <div class="row mb-4">
        <div class="col-12">
            <div class="card">
                <div class="card-header">
                    <h5>Quick Actions</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-3">
                            <a href="{{ url_for('users.list') }}" class="btn btn-outline-primary w-100 mb-2">
                                <i class="bi bi-people"></i> Manage Users
                            </a>
                        </div>
                        <div class="col-md-3">
                            <a href="{{ url_for('locations.list') }}" class="btn btn-outline-primary w-100 mb-2">
                                <i class="bi bi-geo-alt"></i> Manage Locations
                            </a>
                        </div>
                        <div class="col-md-3">
                            <a href="{{ url_for('asset_types.list') }}" class="btn btn-outline-primary w-100 mb-2">
                                <i class="bi bi-tags"></i> Manage Asset Types
                            </a>
                        </div>
                        <div class="col-md-3">
                            <a href="{{ url_for('make_models.list') }}" class="btn btn-outline-primary w-100 mb-2">
                                <i class="bi bi-gear"></i> Manage Make/Models
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Recent Events -->
    <div class="row">
        <div class="col-12">
            <div class="card">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h5>Recent System Events</h5>
                    <a href="{{ url_for('events.list') }}" class="btn btn-sm btn-outline-primary">View All Events</a>
                </div>
                <div class="card-body">
                    {% if recent_events %}
                    <div class="table-responsive">
                        <table class="table table-sm">
                            <thead>
                                <tr>
                                    <th>Date/Time</th>
                                    <th>Event Type</th>
                                    <th>Description</th>
                                    <th>User</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for event in recent_events %}
                                <tr>
                                    <td>{{ event.timestamp.strftime('%Y-%m-%d %H:%M:%S') }}</td>
                                    <td><span class="badge bg-secondary">{{ event.event_type }}</span></td>
                                    <td>{{ event.description }}</td>
                                    <td>{{ event.user.username if event.user else 'System' }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                    {% else %}
                    <p class="text-muted">No recent events.</p>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

### Step 3: Create Asset Management Dashboard

#### 3.1 Create Asset Dashboard Blueprint
**File**: `app/routes/assets/dashboard.py`
```python
from flask import Blueprint, render_template
from flask_login import login_required
from app.models.core.asset import Asset
from app.models.core.asset_type import AssetType
from app.models.core.make_model import MakeModel
from app.models.core.major_location import MajorLocation
from app.models.core.event import Event

bp = Blueprint('dashboard', __name__)

@bp.route('/dashboard')
@login_required
def dashboard():
    """Asset management dashboard"""
    # Get basic statistics
    total_assets = Asset.query.count()
    active_assets = Asset.query.filter_by(status='Active').count()
    inactive_assets = Asset.query.filter_by(status='Inactive').count()
    maintenance_assets = Asset.query.filter_by(status='Maintenance').count()
    
    # Get recent assets
    recent_assets = Asset.query.order_by(Asset.created_at.desc()).limit(5).all()
    
    # Get recent events
    recent_events = Event.query.order_by(Event.timestamp.desc()).limit(5).all()
    
    # Get assets by location
    locations_with_assets = []
    for location in MajorLocation.query.all():
        asset_count = Asset.query.filter_by(major_location_id=location.id).count()
        if asset_count > 0:
            locations_with_assets.append({
                'location': location,
                'asset_count': asset_count
            })
    
    # Get assets by type
    asset_types_with_counts = []
    for asset_type in AssetType.query.all():
        make_models = MakeModel.query.filter_by(asset_type_id=asset_type.id).all()
        asset_count = sum(Asset.query.filter_by(make_model_id=make_model.id).count() for make_model in make_models)
        if asset_count > 0:
            asset_types_with_counts.append({
                'asset_type': asset_type,
                'asset_count': asset_count
            })
    
    return render_template('assets/dashboard.html',
                         total_assets=total_assets,
                         active_assets=active_assets,
                         inactive_assets=inactive_assets,
                         maintenance_assets=maintenance_assets,
                         recent_assets=recent_assets,
                         recent_events=recent_events,
                         locations_with_assets=locations_with_assets,
                         asset_types_with_counts=asset_types_with_counts)
```

#### 3.2 Create Asset Dashboard Template
**File**: `app/templates/assets/dashboard.html`
```html
{% extends "base.html" %}

{% block title %}Asset Management Dashboard{% endblock %}

{% block content %}
<div class="container">
    <div class="row">
        <div class="col-12">
            <h1>Asset Management Dashboard</h1>
            <p class="lead">Asset overview and management tools.</p>
        </div>
    </div>
    
    <!-- Asset Statistics -->
    <div class="row mb-4">
        <div class="col-md-3">
            <div class="card text-center">
                <div class="card-body">
                    <h5 class="card-title">{{ total_assets }}</h5>
                    <p class="card-text">Total Assets</p>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card text-center">
                <div class="card-body">
                    <h5 class="card-title text-success">{{ active_assets }}</h5>
                    <p class="card-text">Active Assets</p>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card text-center">
                <div class="card-body">
                    <h5 class="card-title text-warning">{{ inactive_assets }}</h5>
                    <p class="card-text">Inactive Assets</p>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card text-center">
                <div class="card-body">
                    <h5 class="card-title text-info">{{ maintenance_assets }}</h5>
                    <p class="card-text">In Maintenance</p>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Quick Actions -->
    <div class="row mb-4">
        <div class="col-12">
            <div class="card">
                <div class="card-header">
                    <h5>Quick Actions</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-3">
                            <a href="{{ url_for('assets.list') }}" class="btn btn-outline-primary w-100 mb-2">
                                <i class="bi bi-list"></i> View All Assets
                            </a>
                        </div>
                        <div class="col-md-3">
                            <a href="{{ url_for('assets.create') }}" class="btn btn-outline-success w-100 mb-2">
                                <i class="bi bi-plus-circle"></i> Create Asset
                            </a>
                        </div>
                        <div class="col-md-3">
                            <a href="{{ url_for('assets.detail_tables.list', detail_type='purchase_info') }}" class="btn btn-outline-info w-100 mb-2">
                                <i class="bi bi-cart"></i> Purchase Info
                            </a>
                        </div>
                        <div class="col-md-3">
                            <a href="{{ url_for('assets.detail_tables.list', detail_type='vehicle_registration') }}" class="btn btn-outline-info w-100 mb-2">
                                <i class="bi bi-car-front"></i> Vehicle Registration
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Recent Assets and Events -->
    <div class="row">
        <div class="col-md-6">
            <div class="card">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h5>Recent Assets</h5>
                    <a href="{{ url_for('assets.list') }}" class="btn btn-sm btn-outline-primary">View All</a>
                </div>
                <div class="card-body">
                    {% if recent_assets %}
                    <div class="list-group list-group-flush">
                        {% for asset in recent_assets %}
                        <a href="{{ url_for('assets.detail', asset_id=asset.id) }}" class="list-group-item list-group-item-action">
                            <div class="d-flex w-100 justify-content-between">
                                <h6 class="mb-1">{{ asset.name }}</h6>
                                <small>{{ asset.created_at.strftime('%Y-%m-%d') }}</small>
                            </div>
                            <p class="mb-1">{{ asset.serial_number }}</p>
                            <small class="text-muted">{{ asset.status }}</small>
                        </a>
                        {% endfor %}
                    </div>
                    {% else %}
                    <p class="text-muted">No recent assets.</p>
                    {% endif %}
                </div>
            </div>
        </div>
        
        <div class="col-md-6">
            <div class="card">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h5>Recent Asset Events</h5>
                    <a href="{{ url_for('events.list') }}" class="btn btn-sm btn-outline-primary">View All</a>
                </div>
                <div class="card-body">
                    {% if recent_events %}
                    <div class="list-group list-group-flush">
                        {% for event in recent_events %}
                        <div class="list-group-item">
                            <div class="d-flex w-100 justify-content-between">
                                <h6 class="mb-1">{{ event.event_type }}</h6>
                                <small>{{ event.timestamp.strftime('%Y-%m-%d %H:%M') }}</small>
                            </div>
                            <p class="mb-1">{{ event.description }}</p>
                            <small class="text-muted">{{ event.user.username if event.user else 'System' }}</small>
                        </div>
                        {% endfor %}
                    </div>
                    {% else %}
                    <p class="text-muted">No recent events.</p>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

### Step 4: Update Blueprint Registration

#### 4.1 Update Main Routes Registration
**File**: `app/routes/__init__.py`
```python
"""
Routes package for the Asset Management System
Organized in a tiered structure mirroring the model organization
"""

def init_app(app):
    """Initialize all route blueprints with the Flask app"""
    
    # Application hub (new main index)
    from . import hub
    app.register_blueprint(hub.bp, url_prefix='')
    
    # Core management
    from . import core
    app.register_blueprint(core.bp, url_prefix='/core')
    
    # Asset management
    from . import assets
    app.register_blueprint(assets.bp, url_prefix='/assets')
    
    # Global utilities
    from . import attachments, comments
    app.register_blueprint(attachments.bp, url_prefix='')
    app.register_blueprint(comments.bp, url_prefix='')
```

#### 4.2 Update Core Routes
**File**: `app/routes/core/__init__.py`
```python
"""
Core routes package for core foundation models
Includes CRUD operations for User, MajorLocation, AssetType, MakeModel, Event
"""

from flask import Blueprint

bp = Blueprint('core', __name__)

# Import all core route modules
from . import users, locations, asset_types, make_models, events, dashboard
```

#### 4.3 Update Asset Routes
**File**: `app/routes/assets/__init__.py`
```python
"""
Assets routes package for asset management system
Includes routes for asset CRUD operations and detail management
"""

from flask import Blueprint

bp = Blueprint('assets', __name__)

# Import asset management routes
from . import list, detail, create, edit, all_details, dashboard
from . import detail_tables, model_details

# Register the detail blueprints
bp.register_blueprint(detail_tables.bp, url_prefix='/detail-tables')
bp.register_blueprint(model_details.bp, url_prefix='/model-details')
```

### Step 5: Update Navigation

#### 5.1 Update Base Template Navigation
**File**: `app/templates/base.html`
```html
<!-- Update navigation section -->
<nav class="navbar navbar-expand-lg navbar-dark bg-primary">
    <div class="container">
        <a class="navbar-brand" href="{{ url_for('hub.index') }}">Asset Management</a>
        
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
            <span class="navbar-toggler-icon"></span>
        </button>
        
        <div class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav me-auto">
                <li class="nav-item">
                    <a class="nav-link" href="{{ url_for('hub.index') }}">Home</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="{{ url_for('core.dashboard') }}">Core Management</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="{{ url_for('assets.dashboard') }}">Asset Management</a>
                </li>
                <!-- Future sections (commented out for now) -->
                <!--
                <li class="nav-item">
                    <a class="nav-link disabled" href="#">Dispatching</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link disabled" href="#">Maintenance</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link disabled" href="#">Supply</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link disabled" href="#">Planning</a>
                </li>
                -->
            </ul>
            
            <ul class="navbar-nav">
                <li class="nav-item dropdown">
                    <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" data-bs-toggle="dropdown">
                        {{ current_user.username }}
                    </a>
                    <ul class="dropdown-menu">
                        <li><a class="dropdown-item" href="{{ url_for('auth.logout') }}">Logout</a></li>
                    </ul>
                </li>
            </ul>
        </div>
    </div>
</nav>
```

## Implementation Checklist

### Phase 3A Implementation Tasks
- [ ] **Create Application Hub**
  - [ ] Create `app/routes/hub.py`
  - [ ] Create `app/templates/hub/index.html`
  - [ ] Test hub route functionality

- [ ] **Create Core Management Dashboard**
  - [ ] Create `app/routes/core/dashboard.py`
  - [ ] Create `app/templates/core/dashboard.html`
  - [ ] Update `app/routes/core/__init__.py`
  - [ ] Test core dashboard functionality

- [ ] **Create Asset Management Dashboard**
  - [ ] Create `app/routes/assets/dashboard.py`
  - [ ] Create `app/templates/assets/dashboard.html`
  - [ ] Update `app/routes/assets/__init__.py`
  - [ ] Test asset dashboard functionality

- [ ] **Update Blueprint Registration**
  - [ ] Update `app/routes/__init__.py`
  - [ ] Remove old main blueprint registration
  - [ ] Test all blueprint registrations

- [ ] **Update Navigation**
  - [ ] Update `app/templates/base.html`
  - [ ] Test navigation links
  - [ ] Update breadcrumbs in all templates

- [ ] **Update Template References**
  - [ ] Update all `url_for()` calls in templates
  - [ ] Update breadcrumb navigation
  - [ ] Test all template links

- [ ] **Testing and Validation**
  - [ ] Test all route redirects
  - [ ] Test all template functionality
  - [ ] Test navigation between sections
  - [ ] Validate all forms and actions

### Template Updates Required
- [ ] Create `templates/hub/index.html`
- [ ] Create `templates/core/dashboard.html`
- [ ] Create `templates/assets/dashboard.html`
- [ ] Update `templates/base.html` navigation
- [ ] Update all asset template breadcrumbs
- [ ] Update all core template breadcrumbs
- [ ] Update all `url_for()` references

### Code Updates Required
- [ ] Create `app/routes/hub.py`
- [ ] Create `app/routes/core/dashboard.py`
- [ ] Create `app/routes/assets/dashboard.py`
- [ ] Update `app/routes/core/__init__.py`
- [ ] Update `app/routes/assets/__init__.py`
- [ ] Update `app/routes/__init__.py`
- [ ] Update all route references in Python code

## Benefits of This Reorganization

### 1. Clear Separation of Concerns
- **Core Management**: System administration, users, locations, asset types
- **Asset Management**: Asset-specific operations and details
- **Future Sections**: Clear boundaries for dispatch, maintenance, supply, planning

### 2. Improved User Experience
- **Application Hub**: Clear entry point with section overview
- **Dedicated Dashboards**: Each section has its own focused dashboard
- **Logical Navigation**: Intuitive flow between different system areas

### 3. Better Scalability
- **Modular Structure**: Each section can be developed independently
- **Blueprint Organization**: Clear separation of route concerns
- **Future-Ready**: Structure prepared for all planned phases

### 4. Easier Maintenance
- **Clear File Organization**: Routes and templates organized by section
- **Reduced Coupling**: Sections are independent of each other
- **Easier Testing**: Each section can be tested in isolation

## Migration Strategy

### Phase 1: Preparation
1. Create new route files and templates
2. Test new routes in isolation
3. Prepare navigation updates

### Phase 2: Implementation
1. Update blueprint registration
2. Deploy new routes alongside existing ones
3. Test all functionality

### Phase 3: Cleanup
1. Remove old route references
2. Update all template links
3. Final testing and validation

This refactoring plan provides a clear path to reorganize the application routes while maintaining functionality and preparing for future phases of development.

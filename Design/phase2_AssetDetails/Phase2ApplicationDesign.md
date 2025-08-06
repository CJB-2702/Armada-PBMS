# Phase 2: Asset Detail System - Application Design Document

## Overview

This document outlines the application-layer implementation for Phase 2 of the Asset Detail System, focusing on user interface design, CRUD operations, and interactive functionality across three sub-phases.

## Phase 2A: Basic Implementation - CRUD Pages and Card Templates

### 2A.1 Detail Table CRUD Pages

#### Implementation Tasks
1. **Create Base CRUD Templates**
   - Generic list template for detail tables
   - Generic create/edit form template
   - Generic detail view template
   - Generic delete confirmation modal

2. **Asset Detail Table CRUD Pages**
   - PurchaseInfo CRUD pages
   - VehicleRegistration CRUD pages
   - ToyotaWarrantyReceipt CRUD pages
   - AssetDetailVirtual CRUD pages (base functionality)

3. **Model Detail Table CRUD Pages**
   - EmissionsInfo CRUD pages
   - ModelInfo CRUD pages
   - ModelDetailVirtual CRUD pages (base functionality)

#### File Structure
```
templates/
├── assets/
│   ├── detail_tables/
│   │   ├── purchase_info/
│   │   │   ├── list.html
│   │   │   ├── create.html
│   │   │   ├── edit.html
│   │   │   ├── detail.html
│   │   │   └── delete_modal.html
│   │   ├── vehicle_registration/
│   │   │   ├── list.html
│   │   │   ├── create.html
│   │   │   ├── edit.html
│   │   │   ├── detail.html
│   │   │   └── delete_modal.html
│   │   ├── toyota_warranty_receipt/
│   │   │   ├── list.html
│   │   │   ├── create.html
│   │   │   ├── edit.html
│   │   │   ├── detail.html
│   │   │   └── delete_modal.html
│   │   └── forms/
│   │       ├── purchase_info_form.html
│   │       ├── vehicle_registration_form.html
│   │       ├── toyota_warranty_receipt_form.html
│   │       └── base_detail_form.html
│   └── model_details/
│       ├── emissions_info/
│       │   ├── list.html
│       │   ├── create.html
│       │   ├── edit.html
│       │   ├── detail.html
│       │   └── delete_modal.html
│       ├── model_info/
│       │   ├── list.html
│       │   ├── create.html
│       │   ├── edit.html
│       │   ├── detail.html
│       │   └── delete_modal.html
│       └── forms/
│           ├── emissions_info_form.html
│           ├── model_info_form.html
│           └── base_detail_form.html
├── components/
│   ├── detail_tables/
│   │   └── cards/
│   │       ├── small_card.html
│   │       └── large_card.html
```

#### Route Structure
```python
# app/routes/assets/detail_tables.py

# PurchaseInfo Routes
@bp.route('/purchase_info/')
def purchase_info_list():
    """List all purchase info records"""

@bp.route('/purchase_info/create', methods=['GET', 'POST'])
def purchase_info_create():
    """Create new purchase info record"""

@bp.route('/purchase_info/<int:id>/')
def purchase_info_detail(id):
    """View purchase info record details"""

@bp.route('/purchase_info/<int:id>/edit', methods=['GET', 'POST'])
def purchase_info_edit(id):
    """Edit purchase info record"""

@bp.route('/purchase_info/<int:id>/delete', methods=['POST'])
def purchase_info_delete(id):
    """Delete purchase info record"""

# VehicleRegistration Routes
@bp.route('/vehicle_registration/')
def vehicle_registration_list():
    """List all vehicle registration records"""

@bp.route('/vehicle_registration/create', methods=['GET', 'POST'])
def vehicle_registration_create():
    """Create new vehicle registration record"""

@bp.route('/vehicle_registration/<int:id>/')
def vehicle_registration_detail(id):
    """View vehicle registration record details"""

@bp.route('/vehicle_registration/<int:id>/edit', methods=['GET', 'POST'])
def vehicle_registration_edit(id):
    """Edit vehicle registration record"""

@bp.route('/vehicle_registration/<int:id>/delete', methods=['POST'])
def vehicle_registration_delete(id):
    """Delete vehicle registration record"""

# ToyotaWarrantyReceipt Routes
@bp.route('/toyota_warranty_receipt/')
def toyota_warranty_receipt_list():
    """List all Toyota warranty receipt records"""

@bp.route('/toyota_warranty_receipt/create', methods=['GET', 'POST'])
def toyota_warranty_receipt_create():
    """Create new Toyota warranty receipt record"""

@bp.route('/toyota_warranty_receipt/<int:id>/')
def toyota_warranty_receipt_detail(id):
    """View Toyota warranty receipt record details"""

@bp.route('/toyota_warranty_receipt/<int:id>/edit', methods=['GET', 'POST'])
def toyota_warranty_receipt_edit(id):
    """Edit Toyota warranty receipt record"""

@bp.route('/toyota_warranty_receipt/<int:id>/delete', methods=['POST'])
def toyota_warranty_receipt_delete(id):
    """Delete Toyota warranty receipt record"""
```

```python
# app/routes/assets/model_details.py

# EmissionsInfo Routes
@bp.route('/emissions_info/')
def emissions_info_list():
    """List all emissions info records"""

@bp.route('/emissions_info/create', methods=['GET', 'POST'])
def emissions_info_create():
    """Create new emissions info record"""

@bp.route('/emissions_info/<int:id>/')
def emissions_info_detail(id):
    """View emissions info record details"""

@bp.route('/emissions_info/<int:id>/edit', methods=['GET', 'POST'])
def emissions_info_edit(id):
    """Edit emissions info record"""

@bp.route('/emissions_info/<int:id>/delete', methods=['POST'])
def emissions_info_delete(id):
    """Delete emissions info record"""

# ModelInfo Routes
@bp.route('/model_info/')
def model_info_list():
    """List all model info records"""

@bp.route('/model_info/create', methods=['GET', 'POST'])
def model_info_create():
    """Create new model info record"""

@bp.route('/model_info/<int:id>/')
def model_info_detail(id):
    """View model info record details"""

@bp.route('/model_info/<int:id>/edit', methods=['GET', 'POST'])
def model_info_edit(id):
    """Edit model info record"""

@bp.route('/model_info/<int:id>/delete', methods=['POST'])
def model_info_delete(id):
    """Delete model info record"""
```

### 2A.2 Card Template System

#### Small Card Template
```html
<!-- templates/components/detail_tables/cards/small_card.html -->
<div class="card detail-card small-card mb-3">
    <div class="card-header d-flex justify-content-between align-items-center">
        <h6 class="card-title mb-0">
            <i class="bi bi-{{ detail_type_icon }}"></i>
            {{ detail_type_name }}
        </h6>
        <div class="card-actions">
            <a href="{{ url_for('assets.detail_tables.edit', detail_type=detail_type, id=detail.id) }}" 
               class="btn btn-sm btn-outline-primary">
                <i class="bi bi-pencil"></i>
            </a>
            <button class="btn btn-sm btn-outline-danger" 
                    data-bs-toggle="modal" 
                    data-bs-target="#deleteModal{{ detail.id }}">
                <i class="bi bi-trash"></i>
            </button>
        </div>
    </div>
    <div class="card-body">
        <div class="detail-summary">
            {% include 'components/detail_tables/cards/' + detail_type + '_summary.html' %}
        </div>
    </div>
    <div class="card-footer text-muted">
        <small>
            Created: {{ detail.created_at.strftime('%Y-%m-%d') }}
            {% if detail.updated_at != detail.created_at %}
            | Updated: {{ detail.updated_at.strftime('%Y-%m-%d') }}
            {% endif %}
        </small>
    </div>
</div>
```

#### Large Card Template
```html
<!-- templates/components/detail_tables/cards/large_card.html -->
<div class="card detail-card large-card mb-4">
    <div class="card-header">
        <div class="d-flex justify-content-between align-items-center">
            <h5 class="card-title mb-0">
                <i class="bi bi-{{ detail_type_icon }}"></i>
                {{ detail_type_name }} Details
            </h5>
            <div class="card-actions">
                <a href="{{ url_for('assets.detail_tables.edit', detail_type=detail_type, id=detail.id) }}" 
                   class="btn btn-primary">
                    <i class="bi bi-pencil"></i> Edit
                </a>
                <button class="btn btn-danger" 
                        data-bs-toggle="modal" 
                        data-bs-target="#deleteModal{{ detail.id }}">
                    <i class="bi bi-trash"></i> Delete
                </button>
            </div>
        </div>
    </div>
    <div class="card-body">
        <div class="row">
            <div class="col-md-8">
                <div class="detail-content">
                    {% include 'components/detail_tables/cards/' + detail_type + '_content.html' %}
                </div>
            </div>
            <div class="col-md-4">
                <div class="detail-meta">
                    <h6>Metadata</h6>
                    <ul class="list-unstyled">
                        <li><strong>ID:</strong> {{ detail.id }}</li>
                        <li><strong>Created:</strong> {{ detail.created_at.strftime('%Y-%m-%d %H:%M') }}</li>
                        <li><strong>Created By:</strong> {{ detail.created_by.name }}</li>
                        {% if detail.updated_at != detail.created_at %}
                        <li><strong>Updated:</strong> {{ detail.updated_at.strftime('%Y-%m-%d %H:%M') }}</li>
                        <li><strong>Updated By:</strong> {{ detail.updated_by.name }}</li>
                        {% endif %}
                    </ul>
                </div>
            </div>
        </div>
    </div>
</div>
```

### 2A.3 Model Structure and Forms

#### Detail Table Models
Each detail table will have its own model with specific fields:

```python
# app/models/assets/asset_details/purchase_info.py
class PurchaseInfo(AssetDetailVirtual):
    __tablename__ = 'purchase_info'
    
    purchase_date = db.Column(db.Date, nullable=True)
    purchase_price = db.Column(db.Numeric(10, 2), nullable=True)
    vendor = db.Column(db.String(255), nullable=True)
    warranty_expiry = db.Column(db.Date, nullable=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=True)
    
    event = db.relationship('Event', backref='purchase_info')

# app/models/assets/asset_details/vehicle_registration.py
class VehicleRegistration(AssetDetailVirtual):
    __tablename__ = 'vehicle_registration'
    
    license_plate = db.Column(db.String(20), nullable=True)
    vin = db.Column(db.String(17), nullable=True)
    registration_expiry = db.Column(db.Date, nullable=True)
    insurance_expiry = db.Column(db.Date, nullable=True)
    insurance_provider = db.Column(db.String(255), nullable=True)

# app/models/assets/asset_details/toyota_warranty_receipt.py
class ToyotaWarrantyReceipt(AssetDetailVirtual):
    __tablename__ = 'toyota_warranty_receipt'
    
    warranty_number = db.Column(db.String(50), nullable=True)
    service_date = db.Column(db.Date, nullable=True)
    service_type = db.Column(db.String(100), nullable=True)
    dealer_name = db.Column(db.String(255), nullable=True)
    mileage_at_service = db.Column(db.Integer, nullable=True)

# app/models/assets/model_details/emissions_info.py
class EmissionsInfo(ModelDetailVirtual):
    __tablename__ = 'emissions_info'
    
    fuel_economy_city = db.Column(db.Numeric(5, 2), nullable=True)
    fuel_economy_highway = db.Column(db.Numeric(5, 2), nullable=True)
    emissions_standard = db.Column(db.String(50), nullable=True)
    certification_date = db.Column(db.Date, nullable=True)
    co2_emissions = db.Column(db.Numeric(6, 2), nullable=True)

# app/models/assets/model_details/model_info.py
class ModelInfo(ModelDetailVirtual):
    __tablename__ = 'model_info'
    
    body_style = db.Column(db.String(50), nullable=True)
    engine_size = db.Column(db.String(50), nullable=True)
    transmission_type = db.Column(db.String(50), nullable=True)
    seating_capacity = db.Column(db.Integer, nullable=True)
    cargo_capacity = db.Column(db.Numeric(8, 2), nullable=True)
```

### 2A.4 Form Templates

#### Base Detail Form Template
```html
<!-- templates/assets/detail_tables/forms/base_detail_form.html -->
<form method="POST" class="detail-form">
    {{ form.hidden_tag() }}
    
    <div class="row">
        {% for field in form if field.name not in ['csrf_token', 'submit'] %}
        <div class="col-md-6 mb-3">
            <div class="form-group">
                {{ field.label(class="form-label") }}
                {{ field(class="form-control" + (" is-invalid" if field.errors else "")) }}
                {% if field.errors %}
                <div class="invalid-feedback">
                    {% for error in field.errors %}
                    {{ error }}
                    {% endfor %}
                </div>
                {% endif %}
                {% if field.description %}
                <small class="form-text text-muted">{{ field.description }}</small>
                {% endif %}
            </div>
        </div>
        {% endfor %}
    </div>
    
    <div class="form-actions">
        <button type="submit" class="btn btn-primary">
            <i class="bi bi-check"></i> {{ 'Update' if detail else 'Create' }}
        </button>
        <a href="{{ url_for('assets.detail_tables.list', detail_type=detail_type) }}" 
           class="btn btn-secondary">
            <i class="bi bi-x"></i> Cancel
        </a>
    </div>
</form>
```

#### PurchaseInfo Form Template
```html
<!-- templates/assets/detail_tables/forms/purchase_info_form.html -->
{% extends "assets/detail_tables/forms/base_detail_form.html" %}

{% block form_fields %}
<div class="row">
    <div class="col-md-6 mb-3">
        <div class="form-group">
            {{ form.purchase_date.label(class="form-label") }}
            {{ form.purchase_date(class="form-control", type="date") }}
            {% if form.purchase_date.errors %}
            <div class="invalid-feedback">
                {% for error in form.purchase_date.errors %}
                {{ error }}
                {% endfor %}
            </div>
            {% endif %}
        </div>
    </div>
    
    <div class="col-md-6 mb-3">
        <div class="form-group">
            {{ form.purchase_price.label(class="form-label") }}
            {{ form.purchase_price(class="form-control", type="number", step="0.01") }}
            {% if form.purchase_price.errors %}
            <div class="invalid-feedback">
                {% for error in form.purchase_price.errors %}
                {{ error }}
                {% endfor %}
            </div>
            {% endif %}
        </div>
    </div>
    
    <div class="col-md-6 mb-3">
        <div class="form-group">
            {{ form.vendor.label(class="form-label") }}
            {{ form.vendor(class="form-control") }}
            {% if form.vendor.errors %}
            <div class="invalid-feedback">
                {% for error in form.vendor.errors %}
                {{ error }}
                {% endfor %}
            </div>
            {% endif %}
        </div>
    </div>
    
    <div class="col-md-6 mb-3">
        <div class="form-group">
            {{ form.warranty_expiry.label(class="form-label") }}
            {{ form.warranty_expiry(class="form-control", type="date") }}
            {% if form.warranty_expiry.errors %}
            <div class="invalid-feedback">
                {% for error in form.warranty_expiry.errors %}
                {{ error }}
                {% endfor %}
            </div>
            {% endif %}
        </div>
    </div>
    
    <div class="col-md-6 mb-3">
        <div class="form-group">
            {{ form.event_id.label(class="form-label") }}
            {{ form.event_id(class="form-select") }}
            {% if form.event_id.errors %}
            <div class="invalid-feedback">
                {% for error in form.event_id.errors %}
                {{ error }}
                {% endfor %}
            </div>
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}
```

#### VehicleRegistration Form Template
```html
<!-- templates/assets/detail_tables/forms/vehicle_registration_form.html -->
{% extends "assets/detail_tables/forms/base_detail_form.html" %}

{% block form_fields %}
<div class="row">
    <div class="col-md-6 mb-3">
        <div class="form-group">
            {{ form.license_plate.label(class="form-label") }}
            {{ form.license_plate(class="form-control") }}
            {% if form.license_plate.errors %}
            <div class="invalid-feedback">
                {% for error in form.license_plate.errors %}
                {{ error }}
                {% endfor %}
            </div>
            {% endif %}
        </div>
    </div>
    
    <div class="col-md-6 mb-3">
        <div class="form-group">
            {{ form.vin.label(class="form-label") }}
            {{ form.vin(class="form-control") }}
            {% if form.vin.errors %}
            <div class="invalid-feedback">
                {% for error in form.vin.errors %}
                {{ error }}
                {% endfor %}
            </div>
            {% endif %}
        </div>
    </div>
    
    <div class="col-md-6 mb-3">
        <div class="form-group">
            {{ form.registration_expiry.label(class="form-label") }}
            {{ form.registration_expiry(class="form-control", type="date") }}
            {% if form.registration_expiry.errors %}
            <div class="invalid-feedback">
                {% for error in form.registration_expiry.errors %}
                {{ error }}
                {% endfor %}
            </div>
            {% endif %}
        </div>
    </div>
    
    <div class="col-md-6 mb-3">
        <div class="form-group">
            {{ form.insurance_expiry.label(class="form-label") }}
            {{ form.insurance_expiry(class="form-control", type="date") }}
            {% if form.insurance_expiry.errors %}
            <div class="invalid-feedback">
                {% for error in form.insurance_expiry.errors %}
                {{ error }}
                {% endfor %}
            </div>
            {% endif %}
        </div>
    </div>
    
    <div class="col-md-6 mb-3">
        <div class="form-group">
            {{ form.insurance_provider.label(class="form-label") }}
            {{ form.insurance_provider(class="form-control") }}
            {% if form.insurance_provider.errors %}
            <div class="invalid-feedback">
                {% for error in form.insurance_provider.errors %}
                {{ error }}
                {% endfor %}
            </div>
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}
```

## Phase 2B: Interactive Detail Table Set Management

### 2B.1 Detail Table Set Configuration Interface

#### Implementation Tasks
1. **Asset Type Detail Table Set Management**
   - Interface for configuring which detail tables apply to each asset type
   - Drag-and-drop interface for detail table assignment
   - Visual indicators for asset_detail vs model_detail types

2. **Model Detail Table Set Management**
   - Interface for adding model-specific detail tables
   - Override capabilities for asset type configurations
   - Bulk assignment tools

3. **Retroactive Detail Row Creation**
   - Button to add missing detail rows to existing assets/models
   - Progress tracking for bulk operations
   - Validation and error reporting

#### File Structure
```
templates/
├── assets/
│   ├── detail_table_sets/
│   │   ├── asset_type_config.html
│   │   ├── model_config.html
│   │   └── retroactive_creation.html
├── components/
│   ├── detail_table_sets/
│   │   ├── config_interface.html
│   │   ├── detail_table_selector.html
│   │   └── progress_tracker.html
```

#### Configuration Interface Template
```html
<!-- templates/assets/detail_table_sets/asset_type_config.html -->
<div class="container-fluid">
    <div class="row">
        <div class="col-md-4">
            <div class="card">
                <div class="card-header">
                    <h5>Asset Types</h5>
                </div>
                <div class="card-body">
                    <div class="list-group asset-type-list">
                        {% for asset_type in asset_types %}
                        <button class="list-group-item list-group-item-action" 
                                data-asset-type-id="{{ asset_type.id }}"
                                onclick="selectAssetType({{ asset_type.id }})">
                            <i class="bi bi-tag"></i>
                            {{ asset_type.name }}
                        </button>
                        {% endfor %}
                    </div>
                </div>
            </div>
        </div>
        
        <div class="col-md-8">
            <div class="card">
                <div class="card-header">
                    <h5>Detail Table Configuration</h5>
                    <span id="selected-asset-type-name"></span>
                </div>
                <div class="card-body">
                    <div class="detail-table-config">
                        <div class="row">
                            <div class="col-md-6">
                                <h6>Asset Detail Tables</h6>
                                <div class="detail-table-list" id="asset-detail-list">
                                    <!-- Available asset detail tables -->
                                </div>
                            </div>
                            <div class="col-md-6">
                                <h6>Model Detail Tables</h6>
                                <div class="detail-table-list" id="model-detail-list">
                                    <!-- Available model detail tables -->
                                </div>
                            </div>
                        </div>
                        
                        <div class="mt-3">
                            <button class="btn btn-primary" onclick="saveConfiguration()">
                                <i class="bi bi-check"></i> Save Configuration
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
```

### 2B.2 Retroactive Detail Row Creation

#### Implementation Tasks
1. **Bulk Operation Interface**
   - Progress tracking for large operations
   - Error reporting and recovery
   - Background job processing

2. **Validation System**
   - Pre-operation validation
   - Conflict detection and resolution
   - Rollback capabilities

#### Retroactive Creation Template
```html
<!-- templates/assets/detail_table_sets/retroactive_creation.html -->
<div class="container-fluid">
    <div class="row">
        <div class="col-md-6">
            <div class="card">
                <div class="card-header">
                    <h5>Retroactive Detail Row Creation</h5>
                </div>
                <div class="card-body">
                    <form id="retroactive-form">
                        <div class="mb-3">
                            <label class="form-label">Operation Type</label>
                            <select class="form-select" id="operation-type">
                                <option value="assets">Add to Assets</option>
                                <option value="models">Add to Models</option>
                                <option value="both">Add to Both</option>
                            </select>
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label">Asset Type Filter</label>
                            <select class="form-select" id="asset-type-filter">
                                <option value="">All Asset Types</option>
                                {% for asset_type in asset_types %}
                                <option value="{{ asset_type.id }}">{{ asset_type.name }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        
                        <div class="mb-3">
                            <label class="form-label">Detail Table Types</label>
                            <div class="detail-table-checkboxes">
                                {% for detail_type in detail_table_types %}
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" 
                                           value="{{ detail_type.name }}" 
                                           id="detail-{{ detail_type.name }}">
                                    <label class="form-check-label" for="detail-{{ detail_type.name }}">
                                        {{ detail_type.display_name }}
                                    </label>
                                </div>
                                {% endfor %}
                            </div>
                        </div>
                        
                        <button type="submit" class="btn btn-primary">
                            <i class="bi bi-play"></i> Start Operation
                        </button>
                    </form>
                </div>
            </div>
        </div>
        
        <div class="col-md-6">
            <div class="card">
                <div class="card-header">
                    <h5>Operation Progress</h5>
                </div>
                <div class="card-body">
                    <div id="progress-container" style="display: none;">
                        <div class="progress mb-3">
                            <div class="progress-bar" role="progressbar" style="width: 0%"></div>
                        </div>
                        <div class="progress-details">
                            <p><strong>Status:</strong> <span id="status-text">Initializing...</span></p>
                            <p><strong>Processed:</strong> <span id="processed-count">0</span></p>
                            <p><strong>Errors:</strong> <span id="error-count">0</span></p>
                        </div>
                        <div class="error-log" id="error-log">
                            <!-- Error messages will be displayed here -->
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
```

## Phase 2C: Core Integration and HTMX Cards

### 2C.1 Asset and Model Page Integration

#### Implementation Tasks
1. **Asset Detail Page Enhancement**
   - Add detail table cards to asset detail page
   - Show associated detail tables for the asset
   - Quick access to detail table management

2. **Model Detail Page Enhancement**
   - Add model detail table cards
   - Show model-specific configurations
   - Integration with asset type configurations

#### Enhanced Asset Detail Template
```html
<!-- templates/core/assets/detail.html (enhanced) -->
<div class="container-fluid">
    <!-- Existing asset information -->
    <div class="row">
        <div class="col-md-8">
            <!-- Asset basic info -->
        </div>
        <div class="col-md-4">
            <!-- Asset metadata -->
        </div>
    </div>
    
    <!-- New: Asset Detail Tables Section -->
    <div class="row mt-4">
        <div class="col-12">
            <div class="card">
                <div class="card-header">
                    <h5>
                        <i class="bi bi-card-list"></i>
                        Asset Details
                    </h5>
                    <div class="card-actions">
                        <button class="btn btn-sm btn-outline-primary" 
                                hx-get="{{ url_for('assets.detail_tables.add_missing', asset_id=asset.id) }}"
                                hx-target="#detail-tables-container">
                            <i class="bi bi-plus"></i> Add Missing Details
                        </button>
                    </div>
                </div>
                <div class="card-body">
                    <div id="detail-tables-container">
                        {% include 'components/assets/detail_tables_section.html' %}
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
```

### 2C.2 HTMX Integration for Dynamic Detail Cards

#### Implementation Tasks
1. **HTMX Detail Card System**
   - Dynamic loading of detail table cards
   - In-place editing capabilities
   - Real-time updates without page refresh

2. **Interactive Detail Management**
   - Add/remove detail tables dynamically
   - Quick edit functionality
   - Status indicators and notifications

#### HTMX Detail Card Template
```html
<!-- templates/components/assets/htmx_detail_card.html -->
<div class="detail-card htmx-card" 
     hx-get="{{ url_for('assets.detail_tables.card', detail_type=detail_type, id=detail.id) }}"
     hx-trigger="load"
     hx-swap="outerHTML">
    
    <div class="card-header d-flex justify-content-between align-items-center">
        <h6 class="card-title mb-0">
            <i class="bi bi-{{ detail_type_icon }}"></i>
            {{ detail_type_name }}
        </h6>
        <div class="card-actions">
            <button class="btn btn-sm btn-outline-primary"
                    hx-get="{{ url_for('assets.detail_tables.edit_form', detail_type=detail_type, id=detail.id) }}"
                    hx-target="#edit-modal-content"
                    hx-trigger="click"
                    data-bs-toggle="modal"
                    data-bs-target="#edit-modal">
                <i class="bi bi-pencil"></i>
            </button>
            <button class="btn btn-sm btn-outline-danger"
                    hx-delete="{{ url_for('assets.detail_tables.delete', detail_type=detail_type, id=detail.id) }}"
                    hx-confirm="Are you sure you want to delete this detail?"
                    hx-target="closest .detail-card"
                    hx-swap="outerHTML">
                <i class="bi bi-trash"></i>
            </button>
        </div>
    </div>
    
    <div class="card-body">
        <div class="detail-content">
            <!-- Content will be loaded via HTMX -->
            <div class="loading-spinner">
                <i class="bi bi-arrow-clockwise"></i> Loading...
            </div>
        </div>
    </div>
</div>
```

#### HTMX Edit Modal Template
```html
<!-- templates/components/assets/htmx_edit_modal.html -->
<div class="modal fade" id="edit-modal" tabindex="-1">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Edit Detail</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body" id="edit-modal-content">
                <!-- Form will be loaded here via HTMX -->
            </div>
        </div>
    </div>
</div>
```

### 2C.3 JavaScript Integration

#### HTMX Configuration and Event Handling
```javascript
// static/js/htmx_detail_cards.js
document.addEventListener('DOMContentLoaded', function() {
    // Configure HTMX
    htmx.config.globalViewTransitions = true;
    
    // Handle HTMX events
    document.body.addEventListener('htmx:afterRequest', function(evt) {
        if (evt.detail.xhr.status === 200) {
            // Show success notification
            showNotification('Operation completed successfully', 'success');
        } else {
            // Show error notification
            showNotification('Operation failed', 'error');
        }
    });
    
    // Handle form submissions
    document.body.addEventListener('htmx:beforeRequest', function(evt) {
        // Show loading state
        const target = evt.detail.target;
        if (target.classList.contains('detail-card')) {
            target.classList.add('loading');
        }
    });
});

function showNotification(message, type) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-header">
            <strong class="me-auto">${type === 'success' ? 'Success' : 'Error'}</strong>
            <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
        </div>
        <div class="toast-body">${message}</div>
    `;
    
    document.getElementById('toast-container').appendChild(toast);
    new bootstrap.Toast(toast).show();
}
```

## Implementation Timeline

### Phase 2A (Weeks 1-2)
- [ ] Create base CRUD templates
- [ ] Implement detail table CRUD pages
- [ ] Create small and large card templates
- [ ] Set up routing structure

### Phase 2B (Weeks 3-4)
- [ ] Build detail table set configuration interface
- [ ] Implement retroactive detail row creation
- [ ] Add progress tracking and error handling
- [ ] Create bulk operation tools

### Phase 2C (Weeks 5-6)
- [ ] Integrate detail cards into asset/model pages
- [ ] Implement HTMX dynamic loading
- [ ] Add interactive editing capabilities
- [ ] Create notification and feedback systems

## Testing Strategy

### Unit Testing
- Detail table CRUD operations
- Card template rendering
- Form validation

### Integration Testing
- Detail table set configuration
- Retroactive creation workflows
- HTMX interactions

### User Acceptance Testing
- End-to-end workflows
- Performance testing
- Error handling scenarios

## Conclusion

This application design provides a comprehensive roadmap for implementing Phase 2 of the Asset Detail System. The three-phase approach ensures a solid foundation with basic CRUD functionality, followed by advanced configuration management, and culminating in seamless integration with the core system using modern web technologies like HTMX.

The design emphasizes user experience, performance, and maintainability while providing the flexibility needed for future enhancements and integrations. 
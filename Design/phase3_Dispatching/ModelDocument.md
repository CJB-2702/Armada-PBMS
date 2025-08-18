# Phase 3: Dispatching System Data Model

## Overview

The dispatching system extends the existing asset management framework to handle work orders, dispatch assignments, and operational tracking. The system follows the established patterns from the asset details system, using virtual base classes and detail table sets for flexible configuration.

## Core Concepts

### 1. Dispatch Entity
- **Primary Entity**: Represents a work order or dispatch assignment
- **Relationships**: Links to Asset, Event, MajorLocation, and User
- **Lifecycle**: Tracks status changes and creates audit trail

### 2. Dispatch Detail System
- **Asset Type Dispatch Detail Set**: Configures which dispatch detail types are available for specific asset types (e.g., Vehicle Dispatch for Vehicle asset type, Truck Checklist for Truck asset type)
- **Model Additional Dispatch Detail Set**: Provides additional dispatch detail types for specific models (for model-specific requirements beyond asset type)
- **Dispatch Detail Virtual Template**: Base class for all dispatch-specific detail tables
- **Concrete Implementations**: Vehicle Dispatch, Truck Dispatch Checklist, etc.

## Data Model Architecture

### Core Dispatch Model

```python
class Dispatch(UserCreatedBase, db.Model):
    __tablename__ = 'dispatches'
    
    # Core fields
    dispatch_number = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    priority = db.Column(db.String(20), default='Normal')  # Low, Normal, High, Critical
    status = db.Column(db.String(50), default='Created')  # Created, Assigned, In Progress, Completed, Cancelled
    
    # Timing
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    assigned_date = db.Column(db.DateTime, nullable=True)
    started_date = db.Column(db.DateTime, nullable=True)
    completed_date = db.Column(db.DateTime, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=True)
    assigned_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    major_location_id = db.Column(db.Integer, db.ForeignKey('major_locations.id'), nullable=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'), nullable=True)
    
    # Location tracking (copied from asset for historical reference)
    dispatch_location_id = db.Column(db.Integer, db.ForeignKey('major_locations.id'), nullable=True)
    
    # Relationships
    asset = db.relationship('Asset', foreign_keys=[asset_id])
    assigned_user = db.relationship('User', foreign_keys=[assigned_user_id])
    major_location = db.relationship('MajorLocation', foreign_keys=[major_location_id])
    dispatch_location = db.relationship('MajorLocation', foreign_keys=[dispatch_location_id])
    event = db.relationship('Event', foreign_keys=[event_id])
```

### Dispatch Detail Virtual Base Class

```python
class DispatchDetailVirtual(UserCreatedBase, db.Model):
    """
    Base class for all dispatch-specific detail tables
    Provides common functionality for dispatch detail tables
    """
    __abstract__ = True
    
    # Common field for all dispatch detail tables
    dispatch_id = db.Column(db.Integer, db.ForeignKey('dispatches.id'), nullable=False)
    
    # Foreign key to master table
    detail_id = db.Column(db.Integer, db.ForeignKey('all_dispatch_details.id'), nullable=False)
    
    # Relationships
    @declared_attr
    def detail(cls):
        backref_name = f'{cls.__name__.lower()}_records'
        return db.relationship('AllDispatchDetail', backref=backref_name)
    
    @declared_attr
    def dispatch(cls):
        backref_name = f'{cls.__name__.lower()}_details'
        return db.relationship('Dispatch', backref=backref_name)
```

### Master Table for Dispatch Details

```python
class AllDispatchDetail(UserCreatedBase, db.Model):
    """
    Master table that tracks all dispatch detail records
    Provides a unified view of all dispatch detail types
    """
    __tablename__ = 'all_dispatch_details'
    
    # Core fields
    table_name = db.Column(db.String(100), nullable=False)  # Name of the detail table
    dispatch_id = db.Column(db.Integer, db.ForeignKey('dispatches.id'), nullable=False)
    
    # Relationships
    dispatch = db.relationship('Dispatch', backref='all_details')
```

### Asset Type Dispatch Detail Table Set

```python
class AssetTypeDispatchDetailTableSet(UserCreatedBase, db.Model):
    """
    Configuration container that defines which dispatch detail table types 
    are available for a specific asset type
    """
    __tablename__ = 'asset_type_dispatch_detail_table_sets'
    
    # Configuration fields
    asset_type_id = db.Column(db.Integer, db.ForeignKey('asset_types.id'), nullable=False)
    dispatch_detail_table_type = db.Column(db.String(100), nullable=False)  # e.g., 'vehicle_dispatch', 'truck_checklist'
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    asset_type = db.relationship('AssetType', backref='dispatch_detail_table_sets')
```

### Model Additional Dispatch Detail Table Set

```python
class ModelAdditionalDispatchDetailTableSet(UserCreatedBase, db.Model):
    """
    Configuration container that defines additional dispatch detail table types 
    for a specific model beyond what the asset type provides
    """
    __tablename__ = 'model_additional_dispatch_detail_table_sets'
    
    # Configuration fields
    make_model_id = db.Column(db.Integer, db.ForeignKey('make_models.id'), nullable=False)
    dispatch_detail_table_type = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    make_model = db.relationship('MakeModel', backref='additional_dispatch_detail_table_sets')
```

## Concrete Dispatch Detail Implementations

### Vehicle Dispatch

```python
class VehicleDispatch(DispatchDetailVirtual):
    """
    Vehicle-specific dispatch details
    """
    __tablename__ = 'vehicle_dispatches'
    
    # Vehicle-specific fields
    destination_address = db.Column(db.String(500), nullable=True)
    route_notes = db.Column(db.Text, nullable=True)
    fuel_level_start = db.Column(db.Float, nullable=True)
    fuel_level_end = db.Column(db.Float, nullable=True)
    mileage_start = db.Column(db.Float, nullable=True)
    mileage_end = db.Column(db.Float, nullable=True)
    driver_notes = db.Column(db.Text, nullable=True)
    passenger_count = db.Column(db.Integer, nullable=True)
    
    # Safety and compliance
    safety_check_completed = db.Column(db.Boolean, default=False)
    safety_check_date = db.Column(db.DateTime, nullable=True)
    safety_check_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Relationships
    safety_check_by = db.relationship('User', foreign_keys=[safety_check_by_id])
```

### Truck Dispatch Checklist

```python
class TruckDispatchChecklist(DispatchDetailVirtual):
    """
    Truck-specific dispatch checklist
    """
    __tablename__ = 'truck_dispatch_checklists'
    
    # Pre-trip checklist
    tires_checked = db.Column(db.Boolean, default=False)
    lights_checked = db.Column(db.Boolean, default=False)
    brakes_checked = db.Column(db.Boolean, default=False)
    fluids_checked = db.Column(db.Boolean, default=False)
    safety_equipment_checked = db.Column(db.Boolean, default=False)
    
    # Cargo and loading
    cargo_secured = db.Column(db.Boolean, default=False)
    weight_distribution_verified = db.Column(db.Boolean, default=False)
    load_manifest_verified = db.Column(db.Boolean, default=False)
    
    # Documentation
    registration_current = db.Column(db.Boolean, default=False)
    insurance_current = db.Column(db.Boolean, default=False)
    permits_obtained = db.Column(db.Boolean, default=False)
    
    # Notes
    checklist_notes = db.Column(db.Text, nullable=True)
    completed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    completed_date = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    completed_by = db.relationship('User', foreign_keys=[completed_by_id])
```

## Dispatch Status Tracking

### Dispatch Status History

```python
class DispatchStatusHistory(UserCreatedBase, db.Model):
    """
    Track status changes for dispatches
    """
    __tablename__ = 'dispatch_status_history'
    
    # Core fields
    dispatch_id = db.Column(db.Integer, db.ForeignKey('dispatches.id'), nullable=False)
    status_from = db.Column(db.String(50), nullable=True)
    status_to = db.Column(db.String(50), nullable=False)
    change_reason = db.Column(db.Text, nullable=True)
    changed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    changed_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    dispatch = db.relationship('Dispatch', backref='status_history')
    changed_by = db.relationship('User', foreign_keys=[changed_by_id])
```

## Integration with Existing Systems

### Event Integration
- Each dispatch creates an initial event when created
- Status changes create additional events
- Events link to the dispatch for tracking

### Asset Integration
- Dispatches can be assigned to specific assets
- Asset location is copied to dispatch for historical reference
- Asset type determines available dispatch detail types

### User Integration
- Users can be assigned to dispatches
- Users can complete checklists and safety checks
- User actions are tracked in status history

## Automatic Detail Table Creation

Following the existing pattern from asset details:

1. **Asset Type Configuration**: When a dispatch is created, the system looks up the asset's type and creates detail table rows based on `AssetTypeDispatchDetailTableSet`. This handles the primary dispatch detail types (e.g., Vehicle Dispatch for Vehicle asset type, Truck Checklist for Truck asset type).

2. **Model Configuration**: Additional detail table rows are created based on `ModelAdditionalDispatchDetailTableSet` for model-specific requirements beyond what the asset type provides.

3. **Master Table Integration**: All detail table records are automatically linked to the `AllDispatchDetail` master table

## Implementation Notes

### File Structure
```
app/models/dispatching/
├── __init__.py
├── build.py                    # Dispatch models builder
├── dispatch.py                 # Core Dispatch model
├── dispatch_detail_virtual.py  # Base class for dispatch details
├── all_dispatch_details.py     # Master table for dispatch details
├── dispatch_status_history.py  # Status tracking
├── detail_table_sets/
│   ├── __init__.py
│   ├── asset_type_dispatch_detail_table_set.py
│   └── model_additional_dispatch_detail_table_set.py
└── dispatch_details/
    ├── __init__.py
    ├── vehicle_dispatch.py
    └── truck_dispatch_checklist.py
```

### Database Migration Strategy
1. Create core dispatch tables
2. Create detail table sets
3. Create concrete detail implementations
4. Add foreign key relationships
5. Create indexes for performance

### API Design
- RESTful endpoints for dispatch CRUD operations
- Bulk operations for status updates
- Detail table management endpoints
- Reporting and analytics endpoints

## Future Enhancements

### Advanced Features
- **Route Optimization**: Integration with mapping services
- **Real-time Tracking**: GPS integration for mobile assets
- **Automated Scheduling**: AI-powered dispatch optimization
- **Mobile App**: Field worker interface for status updates

### Integration Points
- **Maintenance System**: Link dispatches to maintenance events
- **Supply Chain**: Track parts and materials for dispatch completion
- **Planning System**: Long-term dispatch planning and forecasting
- **Reporting**: Comprehensive dispatch analytics and KPI tracking

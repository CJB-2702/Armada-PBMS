# Armada PBMS Experimental Data Model
## (Unified Asset Approach with Specialized Detail Tables)

## Common Fields
Every table in the system includes these standard fields:
- `created_at` (DateTime) - When the record was created
- `created_by` (Integer, Foreign Key to User) - Who created the record (0 = SYSTEM)
- `updated_at` (DateTime) - When the record was last updated
- `updated_by` (Integer, Foreign Key to User) - Who last updated the record (0 = SYSTEM)

Note: When `created_by` or `updated_by` is 0, it indicates the change was made by the system rather than a human user. This is used for:
- Data imports
- Automated processes
- Manual database overrides
- System maintenance
- Legacy data

## Core Models

### User
- Primary key: `user_row_id` (Integer)
- Common Fields: Yes
- Specific Fields:
  - `username` (String, unique)
  - `display_name` (String)
  - `role` (String) - Defines user permissions (admin, technician, supervisor, viewer)
- Events:
  - Automatically creates a `user_created` event when a new user is added
  - Event includes user details and is created by the admin user (user_row_id=1)

### AssetType
- Primary key: `type_row_id` (Integer)
- Common Fields: Yes
- Specific Fields:
  - `category` (String) - Full English names of the classification type (e.g., 'Vehicles', 'Locations', 'Equipment', 'Dive Equipment')
  - `description` (String)
- Used to categorize assets according to their type

### Asset
- Primary key: `asset_row_id` (Integer)
- Common Fields: Yes
- Specific Fields:
  - `common_name` (String)
  - `asset_type_row_id` (Integer, Foreign Key to AssetType)
  - `status` (String) - Current state of the asset
  - `parent_id` (Integer, Foreign Key to Asset) - For hierarchical relationships
- Related Models:
  - `VehicleDetail` - One-to-one relationship for vehicle assets
  - `LocationDetail` - One-to-one relationship for location assets
  - `EquipmentDetail` - One-to-one relationship for equipment assets
- Events:
  - Events can be associated with assets through `asset_row_id`
  - Asset status changes and maintenance activities are tracked through events

### VehicleDetail
- Primary key: `vehicle_row_id` (Integer)
- Common Fields: Yes
- Specific Fields:
  - `asset_row_id` (Integer, Foreign Key to Asset)
  - `description` (Text)
  - `date_delivered` (Date)
  - `make` (String)
  - `model` (String)
  - `year_manufactured` (Integer)
  - `vin` (String, unique)
  - `license_plate` (String)
  - `fuel_type` (String)
  - `odometer` (Integer)
  - `capacity` (Integer) - in pounds/kilograms
  - `dimensions` (string) - length, width, height
  - `custom_fields` (JSON) - for additional vehicle-specific data
  - `manufacturer_fuel_efficency` (float)

### VehicleKPI
- Primary key: `kpi_row_id` (Integer)
- Common Fields: Yes
- Specific Fields:
  - `asset_row_id` (Integer, Foreign Key to Asset)
  - `current_mileage` (Integer)
  - `current_hours` (Integer) 
  - `last_maintenance_date` (DateTime)
  - `next_maintenance_date` (DateTime)
  - `maintenance_interval_miles` (Integer)
  - `maintenance_interval_hours` (Integer)
  - `fuel_level` (Float) - Current fuel level as percentage
  - `fuel_efficiency` (Float) - Miles per gallon
  - `total_fuel_consumed` (Float) - In gallons
  - `total_maintenance_cost` (Float)
  - `downtime_hours` (Integer)
  - `utilization_rate` (Float) - Percentage of time in use
  - `last_inspection_date` (DateTime)
  - `next_inspection_date` (DateTime)
  - `status_history` (JSON) - Historical status changes

### LocationDetail
- Primary key: `location_row_id` (Integer)
- Common Fields: Yes
- Specific Fields:
  - `asset_row_id` (Integer, Foreign Key to Asset)
  - `description` (Text)
  - `country` (String)
  - `state` (String)
  - `city` (String)
  - `street` (String)
  - `building_number` (String)
  - `room` (String)
  - `floor` (String)
  - `x`, `y`, `z`, `bin` (Float) - Coordinates
  - `custom_fields` (JSON) - for additional location-specific data

### EquipmentDetail
- Primary key: `equipment_row_id` (Integer)
- Common Fields: Yes
- Specific Fields:
  - `asset_row_id` (Integer, Foreign Key to Asset)
  - `description` (Text)
  - `date_delivered` (Date)
  - `equipment_identifier` (String, unique)
  - `manufacturer` (String)
  - `model` (String)
  - `serial_number` (String)
  - `last_calibration_date` (Date)
  - `next_calibration_date` (Date)
  - `calibration_interval` (Integer) - in days
  - `power_requirements` (String)
  - `weight` (Float)
  - `dimensions` (JSON) - length, width, height
  - `custom_fields` (JSON) - for additional equipment-specific data

### EventType
- Primary key: `type_row_id` (Integer)
- Common Fields: Yes
- Specific Fields:
  - `category` (String) - Core category (status_change, maintenance, operational, documentation, system)
  - `description` (Text)
  - `notification_template` (Text) - optional template for who to notify by default

### Event
- Primary key: `event_row_id` (Integer)
- Common Fields: Yes
- Specific Fields:
  - `event_type_row_id` (Integer, Foreign Key to EventType) - default 0 
  - `title` (String)
  - `description` (Text)
  - `asset_row_id` (Integer, Foreign Key to Asset)
  - `related_asset_row_id` (Integer, Foreign Key to Asset, optional)
  - `user_row_id` (Integer, Foreign Key to User, optional)
  - `scheduled_start` (DateTime, optional)
  - `scheduled_end` (DateTime, optional)
  - `actual_start` (DateTime, optional)
  - `actual_end` (DateTime, optional)
  - `priority` (Integer) - 1-5 scale
  - `status` (String) - pending, in_progress, completed, cancelled



## System Initialization Requirements

1. **System User (user_row_id = 0)**
   - Must exist before any other records
   - Required fields:
     - username: "SYSTEM"
     - role: "system"
     - display_name: "System Automation"
   - Used for:
     - Automated processes
     - Data imports
     - System maintenance
     - Manual overrides
   - Cannot be deleted or modified
   - Self-referential (created_by = 0, updated_by = 0)

2. **Meta Records**
   - Must exist before any other assets
   - Required records:
     a. Meta Asset (asset_row_id = 0)
        - common_name: "Meta Asset"
        - status: "meta"
        - created_by: 0 (SYSTEM)
        - Cannot be deleted or modified
     
     b. Default Location (asset_row_id = 1)
        - common_name: "Default Location"
        - status: "active"
        - created_by: 0 (SYSTEM)
        - Used for unassigned assets
        - Cannot be deleted or modified

3. **Initialization Rules**
   - System must verify existence of these records on startup
   - If records are missing, they must be created automatically
   - If records are corrupted, they must be restored to default values
   - All records must be created by the SYSTEM user (user_row_id = 0)
   - Initialization must be atomic (all records created or none)

4. **Validation Rules**
   - Only ABSOLUTELY essential to no validation requirements during initial prototyping and application development

5. **Dependencies**
   - All events depend on a user and an asset
   - All type details must have a linked asset
   - Type detalis cannot depend on System ( id=0 )

6. **Error Handling Requirements**
   - System must log all initialization attempts
   - System must log any corruption or missing records
   - System must prevent startup if critical records cannot be created
   - System must maintain audit trail of all initialization events

### Logging System

1. **Log Table**
   - Primary key: `log_row_id` (Integer)
   - Common Fields: Yes
   - Specific Fields:
     - `log_level` (String) - ERROR, WARNING, INFO, DEBUG
     - `message` (Text)
     - `context` (JSON) - Additional context data
     - `source` (String) - Component generating the log
     - `stack_trace` (Text, optional) - For errors
     - `user_row_id` (Integer, Foreign Key to User, optional)
     - `asset_row_id` (Integer, Foreign Key to Asset, optional)

2. **File Logging Requirements**
   - JSON format
   - Maximum file size: 1KB
   - Rotation: Create new file when size limit reached
   - Naming: `system_log_YYYYMMDD_HHMMSS.json`
   - Fields:
     ```json
     {
       "timestamp": "ISO8601",
       "level": "ERROR|WARNING|INFO|DEBUG",
       "message": "string",
       "context": {},
       "source": "string",
       "user_id": "integer",
       "asset_id": "integer"
     }
     ```
   - Storage: `./instance/logs or equivalent
   - Retention: Keep last 10 files

3. **Database Logging Requirements**
   - All system events must be logged
   - All user actions must be logged
   - All asset changes must be logged
   - All errors must be logged
   - All initialization events must be logged

4. **Log Levels**
   - ERROR: System errors, initialization failures
   - WARNING: Corrupted records, missing data
   - INFO: Normal operations, user actions
   - DEBUG: Detailed operation information

5. **Logging Rules**
   - File logs must be in JSON format
   - Database logs must include all common fields
   - Critical errors must be logged to both
   - User actions must be logged to database
   - System events must be logged to both
   - Asset changes must be logged to database

6. **Performance Considerations**
   - File logging should be asynchronous
   - Database logging should be batched
   - Log rotation should not block operations
   - Log cleanup should be automated

### Default Data
1. **Asset Types**
   - Vehicle categories (e.g., 'Trucks', 'Cars', 'Specialized Vehicles')
   - Location categories (e.g., 'Buildings', 'Rooms', 'Storage Areas')
   - Equipment categories (e.g., 'Tools', 'Machinery', 'Test Equipment')

2. **User Roles**
   - admin: Full system access
   - technician: Asset maintenance and updates
   - supervisor: Team management and approvals
   - viewer: Read-only access
   - system: Automated processes

3. **Sample Data**
   - Test vehicles with maintenance history
   - Common locations and storage areas
   - Standard equipment inventory
   - Historical events for testing

## Event Flow

1. **Asset Creation**
   - New asset added to database
   - `after_insert` event listener triggers
    - Creates `asset_created` event
    - Event linked to new asset via `asset_row_id`
   `
    
2. **Asset Management**
   - Assets can be created, updated, or moved
   - Events track all significant changes
    - `after_update` event listner triggers
    - Creates `asset_edited` event
    - Event linked to new asset via `asset_row_id`
   - Events can be linked to assets via `asset_row_id`
   - Asset details provide additional context

3. **Location Hierarchy**
   - Locations are assets with type "location"
   - Parent-child relationships through `parent_id`
   - Assets can be assigned to locations
   - Location changes tracked through events

4. **Vehicle Management**
   - Vehicles are assets with type "vehicle"
   - Vehicle-specific details in VehicleDetail
   - Can be assigned to locations
   - Maintenance events track vehicle history

## Best Practices

1. **Asset Management**
   - Use appropriate asset types
   - Maintain hierarchical relationships
   - Track all changes through events
   - Ensure detail tables are populated based on asset type

2. **Location Management**
   - Use location assets for all physical spaces
   - Maintain location hierarchy
   - Track location assignments
   - Keep location details in LocationDetail table

3. **Vehicle Management**
   - Use vehicle assets for all vehicles
   - Keep vehicle-specific details in VehicleDetail table
   - Track maintenance history
   - Monitor maintenance schedules

4. **Equipment Management**
   - Use equipment assets for all equipment
   - Keep equipment-specific details in EquipmentDetail table
   - Track calibration schedules
   - Monitor equipment status

5. **Event Creation**
   - Use event listeners for automatic event creation
   - Include relevant entity IDs in events
   - Provide clear, descriptive event messages

6. **Data Integrity**
   - Maintain referential integrity with foreign keys
   - Use appropriate cascade behaviors
   - Validate data before insertion
   - Ensure detail tables are properly linked to assets

## Example Use Cases

1. **Creating a Vehicle**
```python
# Create vehicle asset
vehicle = Asset(
    common_name="Truck 123",
    asset_type_row_id=vehicle_type_row_id,
    status="active"
)
db.session.add(vehicle)
db.session.flush()

# Add vehicle details
details = VehicleDetail(
    asset_row_id=vehicle.asset_row_id,
    make="Ford",
    model="F-150",
    year_manufactured=2020,
    vin="1HGCM82633A123456",
    license_plate="ABC123",
    fuel_type="gasoline",
    odometer=50000,
    maintenance_interval=5000
)
db.session.add(details)
```

2. **Creating a Location**
```python
# Create location asset
location = Asset(
    common_name="Main Garage",
    asset_type_row_id=location_type_row_id,
    status="active"
)
db.session.add(location)
db.session.flush()

# Add location details
details = LocationDetail(
    asset_row_id=location.asset_row_id,
    country="USA",
    state="CA",
    city="San Francisco",
    street="Main St",
    building_number="123",
    area=5000,
    is_outdoor=False,
    has_power=True,
    has_water=True,
    security_level="high"
)
db.session.add(details)
```

3. **Creating Equipment**
```python
# Create equipment asset
equipment = Asset(
    common_name="Diagnostic Tool",
    asset_type_row_id=equipment_type_row_id,
    status="active"
)
db.session.add(equipment)
db.session.flush()

# Add equipment details
details = EquipmentDetail(
    asset_row_id=equipment.asset_row_id,
    manufacturer="Snap-on",
    model="MODIS Ultra",
    serial_number="SN123456",
    last_calibration_date=date(2023, 1, 1),
    calibration_interval=365,
    power_requirements="110V AC"
)
db.session.add(details)
```

4. **Querying Assets with Details**
```python
# Get all vehicles with their details
vehicles = db.session.query(Asset, VehicleDetail)\
    .join(VehicleDetail, Asset.asset_row_id == VehicleDetail.asset_row_id)\
    .filter(Asset.asset_type_row_id == vehicle_type_row_id)\
    .all()

# Get all locations with their details
locations = db.session.query(Asset, LocationDetail)\
    .join(LocationDetail, Asset.asset_row_id == LocationDetail.asset_row_id)\
    .filter(Asset.asset_type_row_id == location_type_row_id)\
    .all()

# Get all equipment with their details
equipment = db.session.query(Asset, EquipmentDetail)\
    .join(EquipmentDetail, Asset.asset_row_id == EquipmentDetail.asset_row_id)\
    .filter(Asset.asset_type_row_id == equipment_type_row_id)\
    .all()
```

### Default Event Types
1. **Status Change Events**
   - status_change
   - availability_change
   - condition_change
   - location_change

2. **Maintenance Events**
   - scheduled_maintenance
   - unscheduled_maintenance
   - inspection
   - calibration
   - component_change

3. **Operational Events**
   - usage_start
   - usage_end
   - performance_measurement
   - resource_consumption
   - assignment_change

4. **Documentation Events**
   - document_added
   - document_updated
   - certification_change
   - compliance_check

5. **System Events**
   - creation
   - modification
   - deletion
   - archive
   - restore

6. **Default/Unspecified**
   - unspecified_event (default type for unclassified events)

### Event Rules
1. **Event Creation**
   - Every event must have an event type
   - If no type specified, use 'unspecified_event'
   - Events can have multiple details
   - Details must be linked to an event

2. **Event Details**
   - Timing details track scheduled vs actual times
   - Impact details track severity and priority
   - Resource details track personnel and materials
   - Relationship details track related assets/events
   - Outcome details track results and follow-ups

3. **Validation Rules**
   - Required details must be provided
   - Detail values must match data type
   - Dates must be in valid ranges
   - Priorities must be 1-5
   - Costs must be non-negative

4. **Relationship Rules**
   - Events must be linked to at least one asset
   - Related assets must exist
   - Users must exist if specified
   - Event types must exist
   - Details must be linked to events

### Example Event Details
```json
{
  "timing": {
    "scheduled_start": "2024-03-20T10:00:00Z",
    "scheduled_end": "2024-03-20T11:00:00Z",
    "actual_start": "2024-03-20T10:05:00Z",
    "actual_end": "2024-03-20T11:15:00Z",
    "duration": 70
  },
  "impact": {
    "severity": "high",
    "priority": 1,
    "business_impact": "critical",
    "response_time": 30
  },
  "resources": {
    "personnel": ["technician_id_1", "supervisor_id_1"],
    "materials": ["part_id_1", "part_id_2"],
    "cost": 1500.00,
    "labor_hours": 2.5
  },
  "relationships": {
    "related_assets": ["asset_id_1", "asset_id_2"],
    "prerequisites": ["event_id_1"],
    "dependencies": ["event_id_2"]
  },
  "outcomes": {
    "result": "completed",
    "findings": "Component replaced successfully",
    "follow_up_required": true,
    "next_action": "Schedule follow-up inspection"
  }
}
``` 
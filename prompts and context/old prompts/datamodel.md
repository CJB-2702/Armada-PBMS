# Armada PBMS Data Model

## Core Models

### User
- Primary key: `user_id` (Integer)
- Fields:
  - `username` (String, unique)
  - `display_name` (String)
  - `role` (String) - Defines user permissions (admin, technician, supervisor, viewer)
  - `created_at` (DateTime)
- Events:
  - Automatically creates a `user_created` event when a new user is added
  - Event includes user details and is created by the admin user (user_id=1)

### Location
- Primary key: `location_id` (Integer)
- Fields:
  - `unique_name` (String, unique)
  - `common_name` (String)
  - `description` (Text)
  - `country`, `state`, `city`, `street`, `building_number`, `room` (String)
  - `x`, `y`, `z` (Float) - Coordinates
  - `bin` (String) - Storage location identifier
  - `created_at`, `updated_at` (DateTime)
- Events:
  - Automatically creates a `location_created` event when a new location is added
  - Event includes location details and is created by the admin user (user_id=1)

### AssetType
- Primary key: `type_id` (Integer)
- Fields:
  - `code` (String, unique) - FHWA classification code
  - `description` (String)
- Used to categorize assets according to FHWA standards

### Asset
- Primary key: `asset_id` (Integer)
- Fields:
  - `common_name` (String)
  - `asset_type_id` (Integer, Foreign Key to AssetType)
  - `status` (String) - Current state of the asset
- Related Models:
  - `AssetDetail` - One-to-one relationship with additional asset information
- Events:
  - Events can be associated with assets through `asset_id`
  - Asset status changes and maintenance activities are tracked through events

### AssetDetail
- Primary key: `asset_id` (Integer, Foreign Key to Asset)
- Fields:
  - Various asset-specific details
  - `date_delivered` (Date)
  - Other custom fields based on asset type

### Event
- Primary key: `event_id` (Integer)
- Fields:
  - `event_type` (String) - Type of event (e.g., 'user_created', 'location_created', 'asset_created')
  - `title` (String)
  - `description` (Text)
  - `created_at` (DateTime)
  - `created_by` (Integer, Foreign Key to User)
  - `asset_id` (Integer, Foreign Key to Asset, optional)
  - `user_id` (Integer, Foreign Key to User, optional)
  - `location_id` (Integer, Foreign Key to Location, optional)

## System Defaults

### Meta Records
- Admin User (user_id=1)
  - Username: 'admin'
  - Role: 'admin'
  - Created automatically on system initialization
- Meta Asset (asset_id=1)
  - Common name: 'Meta Asset'
  - Status: 'meta'
  - Created automatically on system initialization
- Default Location (location_id=1)
  - Unique name: 'DEFAULT_LOC'
  - Common name: 'Default Location'
  - Created automatically on system initialization

### Default Data
- Asset Types: FHWA classification codes and descriptions
- Users: Pre-defined roles (technician, supervisor, viewer)
- Locations: Common storage and work areas
- Assets: Sample assets with details
- Events: Historical events for testing and demonstration

## Event Flow

1. **User Creation**
   - New user added to database
   - `after_insert` event listener triggers
   - Creates `user_created` event
   - Event linked to new user via `user_id`

2. **Location Creation**
   - New location added to database
   - `after_insert` event listener triggers
   - Creates `location_created` event
   - Event linked to new location via `location_id`

3. **Asset Management**
   - Assets can be created, updated, or moved
   - Events track all significant changes
   - Events can be linked to assets via `asset_id`
   - Asset details provide additional context

4. **Event Creation**
   - Events can be created manually or automatically
   - Events can reference multiple entities (user, location, asset)
   - Events maintain an audit trail of system activities

## Data Initialization

The system supports two modes of initialization:
1. **Basic Initialization**
   - Creates meta records (admin user, meta asset, default location)
   - Loads asset types
   - No default data loaded

2. **Debug Initialization**
   - Performs basic initialization
   - Loads all default data (users, locations, assets, events)
   - Used for development and testing

## Best Practices

1. **Event Creation**
   - Use event listeners for automatic event creation
   - Include relevant entity IDs in events
   - Provide clear, descriptive event messages

2. **Data Integrity**
   - Maintain referential integrity with foreign keys
   - Use appropriate cascade behaviors
   - Validate data before insertion

3. **Default Data**
   - Keep default data in JSON files
   - Use consistent IDs across related records
   - Include comprehensive test data

4. **User Management**
   - Always maintain admin user
   - Use role-based access control
   - Track user activities through events 
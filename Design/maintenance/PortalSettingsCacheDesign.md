# Portal Settings and Cache Table Design

## Overview

A single table to store user-specific portal settings and cached data for QoL features. Settings are user preferences, while cache stores computed/aggregated data that can be regenerated.

## Table Structure

**Table Name**: `portal_user_data`

```python
class PortalUserData(UserCreatedBase):
    __tablename__ = 'portal_user_data'
    
    # Foreign Key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # Settings (JSON dicts) - User preferences
    general_settings = db.Column(db.JSON, default=dict)
    core_settings = db.Column(db.JSON, default=dict)
    maintenance_settings = db.Column(db.JSON, default=dict)
    # implement inventory_settings, supply_settings, etc.
    
    # Cache (JSON dicts) - Computed/aggregated data
    general_cache = db.Column(db.JSON, default=dict)
    core_cache = db.Column(db.JSON, default=dict)
    maintenance_cache = db.Column(db.JSON, default=dict)
    # implement inventory_cache, supply_cache, etc.
    
    # Relationships
    user = relationship('User', backref='portal_data')
```

## Usage Examples

### Settings (User Preferences)
```python
# Store pinned events
portal_data.maintenance_settings = {
    'pinned_events': [123, 456, 789],  # max 5
    'preferred_sort': 'priority',
    'dashboard_layout': 'compact'
}

# Store view preferences
portal_data.general_settings = {
    'theme': 'light',
    'items_per_page': 20
}
```

### Cache (Computed Data)
```python
# Cache top assets (regenerated periodically)
portal_data.maintenance_cache = {
    'top_assets_last_6mo': [
        {'asset_id': 1, 'asset_name': 'Truck A', 'action_count': 15},
        {'asset_id': 2, 'asset_name': 'Truck B', 'action_count': 12}
    ],
    'top_assets_updated_at': '2024-01-15T10:30:00',
    'recent_events_viewed': [789, 456, 123]  # Last 20 event IDs
}
```

## Auto-Creation Options

### Option 1: Database Trigger (PostgreSQL/MySQL)
Create an `AFTER INSERT` trigger on `users` table that automatically inserts a row into `portal_user_data` with default empty JSON dicts.

### Option 2: SQLAlchemy Event Listener
Use SQLAlchemy's `after_insert` event listener on the User model to create the portal_data record programmatically.

### Option 3: Application-Level Factory Pattern
Create portal_data record in User factory/creation methods, ensuring it's always created when users are created.

### Option 4: Lazy Creation with Property/Getter
Create portal_data record on first access via a property method that checks existence and creates if missing.

### Option 5: Hybrid Approach
Use application-level creation for normal flows, with database trigger as safety net for direct database inserts.

## Recommended Approach

**Option 2 (SQLAlchemy Event Listener)** - Provides application-level control, works across all databases, and is easier to test and debug than database triggers.

## Access Pattern

```python
# Get or create pattern
def get_portal_data(user_id):
    data = PortalUserData.query.filter_by(user_id=user_id).first()
    if not data:
        data = PortalUserData(user_id=user_id)
        db.session.add(data)
        db.session.commit()
    return data

# Usage
portal_data = get_portal_data(current_user.id)
pinned = portal_data.maintenance_settings.get('pinned_events', [])
```


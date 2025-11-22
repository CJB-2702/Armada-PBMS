# Core Module Redesign - Design Document

## Overview

This document outlines the redesign of the core module's business, services, and presentation layers to create a unified core dashboard that routes to the main core areas: asset_info, event_info, supply, and user_info.

## Objectives

1. Create a central core dashboard that provides navigation to all core areas
2. Simplify the core module architecture - avoid complex services and presentation
3. Keep the core module mostly self-contained
4. Focus on presentation routes and templates
5. Fix all issues related to moving the supply folder into the core folder
6. Do NOT update data/core or business/core layers
7. Avoid adding new services

## Core Areas

The core module consists of four main areas:

### 1. Asset Info (`app/data/core/asset_info/`)
- **Models**: Asset, AssetType, MakeModel
- **Purpose**: Foundation data for asset management
- **Routes**: `/core/assets`, `/core/asset-types`, `/core/make-models`
- **Templates**: `core/assets/`, `core/asset_types/`, `core/make_models/`

### 2. Event Info (`app/data/core/event_info/`)
- **Models**: Event, Comment, Attachment
- **Purpose**: Event tracking and history
- **Routes**: `/core/events`, `/core/events/comments`, `/core/events/attachments`
- **Templates**: `core/events/`

### 3. Supply (`app/data/core/supply/`)
- **Models**: Part, Tool, IssuableTool
- **Purpose**: Inventory and supply management
- **Routes**: `/core/supply`, `/core/supply/parts`, `/core/supply/tools`
- **Templates**: `supply/` (shared templates)

### 4. User Info (`app/data/core/user_info/`)
- **Models**: User
- **Purpose**: User management
- **Routes**: `/core/users`
- **Templates**: `core/users/`

### Additional Core Areas
- **Locations** (`app/data/core/major_location.py`): `/core/locations`
- **Sequences**: Ignored for presentation (as per requirements)

## Architecture Principles

### Keep It Simple
- No complex architecture in core module
- Minimal services - use existing services or direct ORM queries
- Simple CRUD operations where possible
- Self-contained presentation logic

### Self-Contained
- Core dashboard should not depend on other modules
- Routes should be independent and focused
- Templates should be reusable but not overly complex

### Presentation Focus
- Focus on routes and templates
- Avoid adding new services
- Use existing business contexts where available
- Direct ORM queries for simple operations

## Core Dashboard Design

### Route: `/core` or `/core/dashboard`

**Purpose**: Central hub for all core module areas

**Features**:
1. Navigation cards to each core area
2. Quick statistics for each area
3. Recent activity summary
4. Quick access to common operations

**Statistics to Display**:
- Asset Info: Total assets, asset types, make/models
- Event Info: Total events, recent events
- Supply: Total parts, tools, low stock alerts
- User Info: Total users, active users
- Locations: Total locations

**Navigation Structure**:
```
Core Dashboard
├── Asset Info
│   ├── Assets List
│   ├── Asset Types
│   └── Make/Models
├── Event Info
│   ├── Events List
│   ├── Recent Events
│   └── Event Management
├── Supply
│   ├── Supply Dashboard
│   ├── Parts
│   └── Tools
├── User Info
│   └── Users List
└── Locations
    └── Locations List
```

## Route Structure

### Core Dashboard Route
- **File**: `app/presentation/routes/core/__init__.py` or `app/presentation/routes/core/dashboard.py`
- **Blueprint**: `core_dashboard` or extend existing `core` blueprint
- **URL**: `/core` or `/core/dashboard`
- **Template**: `core/dashboard.html`

### Existing Core Routes
All existing core routes remain unchanged:
- `app/presentation/routes/core/assets.py` - `/core/assets`
- `app/presentation/routes/core/asset_types.py` - `/core/asset-types`
- `app/presentation/routes/core/make_models.py` - `/core/make-models`
- `app/presentation/routes/core/events/` - `/core/events`
- `app/presentation/routes/core/users.py` - `/core/users`
- `app/presentation/routes/core/locations.py` - `/core/locations`
- `app/presentation/routes/core/supply/` - `/core/supply`

## Template Structure

### Core Dashboard Template
- **File**: `app/presentation/templates/core/dashboard.html`
- **Layout**: Card-based navigation with statistics
- **Sections**:
  1. Header with title and description
  2. Statistics row (quick counts)
  3. Navigation cards for each area
  4. Recent activity section (optional)

### Template Organization
```
app/presentation/templates/
├── core/
│   ├── dashboard.html (NEW)
│   ├── assets/
│   ├── asset_types/
│   ├── make_models/
│   ├── events/
│   ├── users/
│   └── locations/
└── supply/ (shared by core/supply routes)
    ├── index.html
    ├── parts/
    └── tools/
```

## Implementation Plan

### Phase 1: Fix Supply Folder Issues
1. Remove old `app/presentation/routes/supply/` folder (broken imports)
2. Verify all references use `app/presentation/routes/core/supply/`
3. Update any remaining broken imports
4. Ensure all templates reference correct route names

### Phase 2: Create Core Dashboard
1. Create core dashboard route
2. Create core dashboard template
3. Add statistics queries (simple ORM, no services)
4. Register dashboard route

### Phase 3: Update Navigation
1. Update base template navigation
2. Update index.html to link to core dashboard
3. Ensure all core area links work correctly

### Phase 4: Verification
1. Test all core area routes
2. Verify supply routes work correctly
3. Check for any remaining broken imports
4. Ensure no services are added unnecessarily

## Route Registration

### Blueprint Registration
```python
# In app/presentation/routes/__init__.py
from .core import bp as core_bp
app.register_blueprint(core_bp, url_prefix='/core')

# Core dashboard is part of core blueprint
# Individual area blueprints registered separately
```

### URL Structure
```
/core                          # Core dashboard
/core/assets                   # Assets list
/core/asset-types              # Asset types
/core/make-models              # Make/models
/core/events                   # Events
/core/users                    # Users
/core/locations                # Locations
/core/supply                   # Supply dashboard
/core/supply/parts             # Parts
/core/supply/tools             # Tools
```

## Data Access Strategy

### Avoid Adding Services
- Use existing services where they exist
- For dashboard statistics, use simple ORM queries
- Direct model queries for simple operations
- Use business contexts (e.g., `AssetContext`, `PartContext`) where available

### Example Dashboard Query
```python
# Simple ORM queries - no service needed
total_assets = Asset.query.count()
total_events = Event.query.count()
recent_events = Event.query.order_by(Event.timestamp.desc()).limit(5).all()
```

## Migration Notes

### Supply Folder Migration
The supply folder has been moved from `app/data/supply_items/` to `app/data/core/supply/`.

**Changes Required**:
1. All imports: `app.data.supply_items.*` → `app.data.core.supply.*`
2. Routes: `app/presentation/routes/supply/` → `app/presentation/routes/core/supply/`
3. URL prefixes: `/supply` → `/core/supply`
4. Blueprint names: `supply` → `core_supply`
5. Route names: `supply.parts.list` → `core_supply_parts.list`

### Files to Update
- Remove: `app/presentation/routes/supply/` (old, broken)
- Keep: `app/presentation/routes/core/supply/` (new, correct)
- Update: Any templates referencing old route names
- Update: Navigation menus and links

## Testing Checklist

- [ ] Core dashboard loads at `/core`
- [ ] All core area navigation links work
- [ ] Statistics display correctly
- [ ] Supply routes work at `/core/supply/*`
- [ ] No broken imports
- [ ] Navigation updated in base template
- [ ] No new services added
- [ ] All existing core routes still work

## Notes

- **Sequences**: Ignore presentation for sequences as per requirements
- **Business Core**: Do NOT update `app/buisness/core/` 
- **Data Core**: Do NOT update `app/data/core/` (except supply was already moved)
- **Services**: Avoid adding new services, use existing or direct ORM
- **Self-Contained**: Core module should be mostly independent



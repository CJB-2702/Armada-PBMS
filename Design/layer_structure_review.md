# Layer Structure Review - Core and Assets

This document reviews the current structure of `core` and `assets` modules across all four layers to ensure parallel structure compliance.

## Current Structure

### Data Layer (`app/data/`)

#### Core Module (`app/data/core/`)
```
app/data/core/
├── __init__.py
├── user_info/
│   └── user.py                    # User model
├── asset_info/
│   ├── asset_type.py              # AssetType model
│   ├── make_model.py              # MakeModel model (with after_insert event listener)
│   └── asset.py                   # Asset model (with after_insert event listener)
├── event_info/
│   ├── event.py                   # Event model
│   ├── comment.py                 # Comment model
│   └── attachment.py              # Attachment model
├── major_location.py              # MajorLocation model
├── user_created_base.py           # UserCreatedBase base class
├── sequences/                     # Sequence generators
│   ├── detail_id_managers.py
│   ├── event_detail_id_manager.py
│   └── attachment_id_manager.py
├── virtual_sequence_generator.py
└── build.py                       # Core build orchestrator
```

#### Assets Module (`app/data/assets/`)
```
app/data/assets/
├── __init__.py
├── asset_detail_virtual.py        # Base class for asset detail tables
├── model_detail_virtual.py        # Base class for model detail tables
├── asset_details/                 # Asset-specific detail tables
│   ├── __init__.py
│   ├── purchase_info.py
│   ├── vehicle_registration.py
│   └── toyota_warranty_receipt.py
├── model_details/                 # Model-specific detail tables
│   ├── __init__.py
│   ├── model_info.py
│   ├── emissions_info.py
│   └── details_union.py
├── detail_table_templates/         # Configuration templates
│   ├── __init__.py
│   ├── model_detail_table_template.py
│   ├── asset_details_from_asset_type.py
│   └── asset_details_from_model_type.py
└── build.py                       # Assets build orchestrator
```

### Business Layer (`app/buisness/`)

#### Core Module (`app/buisness/core/`)
```
app/buisness/core/
├── __init__.py
├── asset_context.py               # AssetContext - business logic for assets
├── event_context.py               # EventContext - business logic for events
├── make_model_context.py          # MakeModelContext - business logic for make/models
└── data_insertion_mixin.py        # Mixin for data insertion operations
```

#### Assets Module (`app/buisness/assets/`)
```
app/buisness/assets/
├── __init__.py
├── asset_details_context.py       # AssetDetailsContext - extended asset operations
├── detail_table_context.py        # DetailTableContext - detail table operations
├── make_model_context.py         # MakeModelDetailsContext - make/model with details
├── model_detail_context.py        # ModelDetailContext - model detail operations
├── factories/                     # Factory classes for object creation
│   ├── __init__.py
│   ├── detail_factory.py         # DetailFactory - abstract base for detail creation
│   ├── asset_detail_factory.py   # AssetDetailFactory - creates asset detail rows
│   ├── model_detail_factory.py   # ModelDetailFactory - creates model detail rows
│   ├── asset_factory.py          # AssetFactory - creates Asset instances
│   └── make_model_factory.py     # MakeModelFactory - creates MakeModel instances
├── asset_details/                 # Asset detail business logic
│   ├── __init__.py
│   ├── asset_details_struct.py   # Structured representation of asset details
│   └── details_union.py          # Union query service for asset details
└── model_details/                 # Model detail business logic
    ├── __init__.py
    ├── model_details_struct.py   # Structured representation of model details
    └── details_union.py          # Union query service for model details
```

### Presentation Layer (`app/presentation/routes/`)

#### Core Module (`app/presentation/routes/core/`)
```
app/presentation/routes/core/
├── __init__.py
├── assets.py                      # Core asset routes
├── locations.py                   # Location routes
├── asset_types.py                 # Asset type routes
├── make_models.py                 # Make/model routes
├── users.py                       # User routes
└── events/                        # Event-related routes
    ├── __init__.py
    ├── events.py                  # Event routes
    ├── comments.py                # Comment routes
    └── attachments.py             # Attachment routes
```

#### Assets Module (`app/presentation/routes/assets/`)
```
app/presentation/routes/assets/
├── __init__.py
├── detail_tables.py                # Asset detail table routes
└── model_details.py                # Model detail table routes
```

### Services Layer (`app/services/`)

#### Current Status
```
app/services/
└── [Empty - to be populated]
```

#### Expected Structure (Future)
```
app/services/
├── __init__.py
├── core/                          # Core services (to be created)
│   ├── __init__.py
│   ├── dashboard_service.py       # Dashboard statistics
│   ├── search_service.py          # Search functionality
│   └── formatters.py             # Data formatting utilities
└── assets/                        # Asset services (to be created)
    ├── __init__.py
    ├── asset_statistics.py       # Asset statistics aggregation
    ├── asset_search.py           # Asset search helpers
    └── asset_formatters.py       # Asset data formatting
```

## Automatic Detail Insertion Architecture

### Current Implementation (Factory-Based)

The automatic detail insertion system uses **factory classes** in the business layer, not database triggers:

1. **Data Layer** (`app/data/core/asset_info/`):
   - `Asset` and `MakeModel` models have SQLAlchemy `after_insert` event listeners
   - Event listeners call `create_detail_table_rows()` method on the model instance
   - Models delegate to factory classes in business layer

2. **Business Layer** (`app/buisness/assets/factories/`):
   - `AssetDetailFactory` - Creates asset detail table rows
   - `ModelDetailFactory` - Creates model detail table rows
   - Both inherit from `DetailFactory` base class
   - Use `DETAIL_TABLE_REGISTRY` to map detail table types to classes
   - Query configuration tables to determine which detail tables to create
   - Handle both asset-type-based and model-type-based detail creation

3. **Flow**:
   ```
   Asset/MakeModel Created
       ↓
   SQLAlchemy after_insert event fires
       ↓
   Model.create_detail_table_rows() called
       ↓
   Factory class (AssetDetailFactory/ModelDetailFactory) invoked
       ↓
   Factory queries configuration tables
       ↓
   Factory creates appropriate detail table rows using registry
   ```

### Key Components

- **Event Listeners**: SQLAlchemy `after_insert` events in data models
- **Factory Classes**: Business layer factories handle creation logic
- **Registry System**: `DETAIL_TABLE_REGISTRY` maps detail types to model classes
- **Configuration Tables**: Determine which detail tables apply to which assets/models
- **No Database Triggers**: All logic is in application code

## Structure Compliance

### ✅ Parallel Structure Status

- **Data Layer**: ✅ Organized by domain (core, assets)
- **Business Layer**: ✅ Mirrors data structure (core, assets)
- **Presentation Routes**: ✅ Mirrors data structure (core, assets)
- **Services Layer**: ⚠️ Empty - needs to be created to mirror structure

### Recommendations

1. **Services Layer**: Create `app/services/core/` and `app/services/assets/` folders
2. **Maintain Parallel Structure**: Ensure all new modules follow the same pattern
3. **Documentation**: Keep this review updated as structure evolves


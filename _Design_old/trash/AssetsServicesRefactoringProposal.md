# Assets Services Refactoring Proposal

## Overview
This document proposes the creation of `app/services/assets/` and identifies functions and logic from both the business layer (`app/buisness/assets/`) and presentation layer (`app/presentation/routes/assets/`) that should be moved to services.

## Goals
1. Move read-only, presentation-specific query logic from business layer to services
2. Move data aggregation and formatting from presentation routes to services
3. Keep data modification and business rules in business layer
4. Create reusable service methods for common presentation needs

---

## 1. Business Layer Analysis (`app/buisness/assets/`)

### ✅ KEEP IN BUSINESS LAYER

#### Factories (`factories/`)
**Reason**: Handle data creation with business rules and validation
- `AssetFactory.create_asset()` - Creates assets with validation
- `AssetFactory.update_asset()` - Updates assets with business rules
- `MakeModelFactory.*` - Creates make/models with validation
- `AssetDetailFactory.*` - Creates detail records with business logic
- `ModelDetailFactory.*` - Creates model detail records
- `DetailFactory.*` - Generic detail creation with business rules

#### Context Managers - Data Modification Methods
**Reason**: Handle complex business operations
- `AssetDetailsContext` - Properties for accessing detail structures (business domain)
- `DetailTableContext.create_detail_record()` - Creates records with business logic
- `DetailTableContext.update_detail_record()` - Updates with business rules
- `DetailTableContext.delete_detail_record()` - Deletes with validation
- `ModelDetailContext.*` (CRUD methods) - Business operations

---

### 🔄 MOVE TO SERVICES LAYER

#### 1. Read-Only Query Methods in Context Managers

##### `AssetDetailsContext` (`asset_details_context.py`)
**Current Location**: `app/buisness/assets/asset_details_context.py`

**Methods to Move**:
- `get_asset_details_by_type()` (line 169) - **Presentation-specific grouping**
  - Groups details by type for display
  - Returns Dict[str, List] for template rendering
  - **Move to**: `AssetDetailService.get_asset_details_by_type(asset_id)`

- `get_model_details_by_type()` (line 185) - **Presentation-specific grouping**
  - Groups model details by type for display
  - Returns Dict[str, List] for template rendering
  - **Move to**: `AssetDetailService.get_model_details_by_type(asset_id)`

- `asset_type_configs` property (line 146-155) - **Configuration retrieval for display**
  - Queries configuration templates
  - Used for presentation (template rendering)
  - **Move to**: `AssetDetailService.get_asset_type_configs(asset_type_id)`

- `model_type_configs` property (line 157-167) - **Configuration retrieval for display**
  - Queries configuration templates
  - Used for presentation
  - **Move to**: `AssetDetailService.get_model_type_configs(make_model_id)`

**Keep in Business**:
- `asset_details_struct` property - Business domain access pattern
- `model_details_struct` property - Business domain access pattern
- `asset_details` property - Business domain access pattern
- `model_details` property - Business domain access pattern
- `detail_count` property - Business domain calculation

##### `DetailTableContext` (`detail_table_context.py`)
**Current Location**: `app/buisness/assets/detail_table_context.py`

**Methods to Move**:
- `list_all_details()` (line 100+) - **Read-only query for listing**
  - Used by routes for list views
  - Pure query operation with no business logic
  - **Move to**: `AssetDetailService.list_detail_records(detail_type, filters)`

- `get_detail_by_id()` (line 180+) - **Read-only query for detail view**
  - Simple get operation for display
  - **Move to**: `AssetDetailService.get_detail_record(detail_type, id)`

- `get_all_details_for_asset()` (line 82-92) - **Read-only aggregation**
  - Already delegates to union service
  - Presentation-specific aggregation
  - **Move to**: `AssetDetailService.get_all_details_for_asset(asset_id)`

- `get_details_by_type_for_asset()` (line 94-108) - **Read-only query**
  - Simple query by type
  - **Move to**: `AssetDetailService.get_details_by_type_for_asset(asset_id, detail_type)`

**Keep in Business**:
- `get_detail_table_config()` - Configuration access (used by both layers)
- `get_detail_table_model()` - Model lookup (used by business layer)
- `create_detail_record()` - Data modification with business logic
- `update_detail_record()` - Data modification with business logic
- `delete_detail_record()` - Data modification with business logic

##### `ModelDetailContext` (`model_detail_context.py`)
**Current Location**: `app/buisness/assets/model_detail_context.py`

**Methods to Move**:
- `list_all_details()` - **Read-only query for listing**
  - Used by routes for list views
  - **Move to**: `ModelDetailService.list_detail_records(detail_type)`

- `get_detail_by_id()` - **Read-only query for detail view**
  - Simple get operation
  - **Move to**: `ModelDetailService.get_detail_record(detail_type, id)`

**Keep in Business**:
- `get_model_detail_table_config()` - Configuration access
- `create_detail_record()` - Data modification
- `update_detail_record()` - Data modification
- `delete_detail_record()` - Data modification

#### 2. Union Services (`asset_details/details_union.py`, `model_details/details_union.py`)

**Current Location**: `app/buisness/assets/asset_details/details_union.py`

**Services to Move**:
- `AssetDetailsUnionService` - **Read-only query service**
  - WARNING comment says "for UI integration purposes only"
  - All methods are read-only queries
  - **Move entire class to**: `app/services/assets/asset_detail_union_service.py`

**Methods**:
- `get_all_details_for_asset()` - Union query across all asset detail tables
- `get_details_with_filters()` - Filtered union query
- `search_details()` - Search across detail tables
- All other query methods

- `ModelDetailsUnionService` - **Read-only query service**
  - Same pattern as asset details
  - **Move entire class to**: `app/services/assets/model_detail_union_service.py`

---

## 2. Presentation Routes Analysis (`app/presentation/routes/assets/`)

### Routes File: `detail_tables.py`

#### Patterns to Move to Services

##### 1. Form Options Preparation
**Current Pattern** (lines 46-52, 72-73, 144-145):
```python
all_assets = Asset.query.all()
asset_options = [(asset.id, f"{asset.name} ({asset.serial_number})") for asset in all_assets]

all_models = MakeModel.query.all()
model_options = [(model.id, f"{model.make} {model.model} {model.year or ''}") for model in all_models]
```

**Proposed Service Method**:
```python
# In AssetDetailService
@staticmethod
def get_form_options() -> Dict:
    """Get form options for detail table forms"""
    from app.data.core.asset_info.asset import Asset
    from app.data.core.asset_info.make_model import MakeModel
    
    assets = Asset.query.all()
    make_models = MakeModel.query.all()
    
    return {
        'asset_options': [(a.id, f"{a.name} ({a.serial_number})") for a in assets],
        'model_options': [(m.id, f"{m.make} {m.model} {m.year or ''}") for m in make_models],
        'assets': assets,  # Raw list for flexibility
        'make_models': make_models
    }
```

**Affected Routes**:
- `list()` (lines 46-52)
- `create()` (lines 72-73)
- `edit()` (lines 144-145)

##### 2. Record Filtering Logic
**Current Pattern** (lines 31-43):
```python
asset_id_filter = request.args.get('asset_id', type=int)
model_id_filter = request.args.get('model_id', type=int)

if asset_id_filter:
    records = DetailTableContext.list_all_details(detail_type, asset_id=asset_id_filter)
else:
    records = DetailTableContext.list_all_details(detail_type)

if model_id_filter:
    records = [r for r in records if r.asset and r.asset.make_model_id == model_id_filter]
```

**Proposed Service Method**:
```python
# In AssetDetailService
@staticmethod
def get_list_data(detail_type: str, request: Request) -> Tuple[List, Dict]:
    """Get filtered detail records for list view"""
    asset_id_filter = request.args.get('asset_id', type=int)
    model_id_filter = request.args.get('model_id', type=int)
    
    # Build query with filters
    records = AssetDetailService.list_detail_records(
        detail_type=detail_type,
        asset_id=asset_id_filter,
        model_id=model_id_filter
    )
    
    # Get form options
    form_options = AssetDetailService.get_form_options()
    
    return records, form_options
```

**Affected Route**:
- `list()` (lines 31-61)

##### 3. Configuration Retrieval
**Current Pattern** (lines 17-19, repeated in many routes):
```python
def get_detail_table_config(detail_type):
    """Get configuration for a detail table type"""
    return DetailTableContext.get_detail_table_config(detail_type)
```

**Proposed Service Method**:
```python
# In AssetDetailService
@staticmethod
def get_detail_table_config(detail_type: str) -> Optional[Dict]:
    """Get configuration for a detail table type"""
    # Can delegate to DetailTableContext or store in service
    return DetailTableContext.get_detail_table_config(detail_type)
```

**Note**: This can stay as a simple wrapper or move entirely to service if configuration becomes service concern.

### Routes File: `model_details.py`

#### Patterns to Move to Services

##### 1. Record Listing
**Current Pattern** (lines 34-35):
```python
records = ModelDetailContext.list_all_details(detail_type)
```

**Proposed Service Method**:
```python
# In ModelDetailService
@staticmethod
def get_list_data(detail_type: str) -> List:
    """Get all detail records for list view"""
    return ModelDetailService.list_detail_records(detail_type)
```

**Affected Route**:
- `list()` (line 35)

##### 2. Configuration Retrieval
**Current Pattern** (lines 20-22, repeated):
```python
def get_model_detail_table_config(detail_type):
    """Get configuration for a model detail table type"""
    return ModelDetailContext.get_model_detail_table_config(detail_type)
```

**Proposed Service Method**:
```python
# In ModelDetailService
@staticmethod
def get_model_detail_table_config(detail_type: str) -> Optional[Dict]:
    """Get configuration for a model detail table type"""
    return ModelDetailContext.get_model_detail_table_config(detail_type)
```

##### 3. Direct Queries in Legacy Routes
**Current Pattern** (lines 178-179, 194-195, 250-251, 266-267):
```python
make_model = MakeModel.query.get_or_404(make_model_id)
emissions = EmissionsInfo.query.filter_by(make_model_id=make_model_id).first()
```

**Proposed Service Method**:
```python
# In ModelDetailService
@staticmethod
def get_detail_for_model(detail_type: str, make_model_id: int):
    """Get detail record for a specific model"""
    return ModelDetailService.get_detail_record(detail_type, make_model_id=make_model_id)
```

**Affected Routes**:
- `emissions_info()` (lines 178-179)
- `edit_emissions_info()` (lines 194-195)
- `model_info()` (lines 250-251)
- `edit_model_info()` (lines 266-267)

---

## 3. Proposed Service Structure

### Directory: `app/services/assets/`

```
app/services/assets/
├── __init__.py
├── asset_detail_service.py      # Asset detail table services
├── model_detail_service.py      # Model detail table services
├── asset_detail_union_service.py # Union queries for asset details (moved from business)
└── model_detail_union_service.py # Union queries for model details (moved from business)
```

### Service: `AssetDetailService`

**Location**: `app/services/assets/asset_detail_service.py`

**Responsibilities**:
- List and query asset detail records
- Format data for presentation
- Provide form options
- Group details by type for display
- Get configurations for presentation

**Proposed Methods**:
```python
class AssetDetailService:
    # Configuration
    @staticmethod
    def get_detail_table_config(detail_type: str) -> Optional[Dict]
    
    @staticmethod
    def get_asset_type_configs(asset_type_id: int) -> List
    
    @staticmethod
    def get_model_type_configs(make_model_id: int) -> List
    
    # Querying
    @staticmethod
    def list_detail_records(detail_type: str, asset_id: Optional[int] = None, 
                           model_id: Optional[int] = None) -> List
    
    @staticmethod
    def get_detail_record(detail_type: str, id: int)
    
    @staticmethod
    def get_all_details_for_asset(asset_id: int) -> List[Dict]
    
    @staticmethod
    def get_details_by_type_for_asset(asset_id: int, detail_type: str) -> List
    
    # Presentation-specific
    @staticmethod
    def get_asset_details_by_type(asset_id: int) -> Dict[str, List]
    
    @staticmethod
    def get_model_details_by_type(asset_id: int) -> Dict[str, List]
    
    @staticmethod
    def get_list_data(detail_type: str, request: Request) -> Tuple[List, Dict]
    
    @staticmethod
    def get_form_options() -> Dict
```

### Service: `ModelDetailService`

**Location**: `app/services/assets/model_detail_service.py`

**Responsibilities**:
- List and query model detail records
- Format data for presentation
- Get configurations for presentation

**Proposed Methods**:
```python
class ModelDetailService:
    # Configuration
    @staticmethod
    def get_model_detail_table_config(detail_type: str) -> Optional[Dict]
    
    # Querying
    @staticmethod
    def list_detail_records(detail_type: str) -> List
    
    @staticmethod
    def get_detail_record(detail_type: str, id: int)
    
    @staticmethod
    def get_detail_for_model(detail_type: str, make_model_id: int)
    
    # Presentation-specific
    @staticmethod
    def get_list_data(detail_type: str) -> List
```

---

## 4. Summary of Changes

### Business Layer → Services Layer

| Current Location | Method/Class | New Location | Type |
|-----------------|--------------|--------------|------|
| `AssetDetailsContext` | `get_asset_details_by_type()` | `AssetDetailService` | Presentation grouping |
| `AssetDetailsContext` | `get_model_details_by_type()` | `AssetDetailService` | Presentation grouping |
| `AssetDetailsContext` | `asset_type_configs` property | `AssetDetailService` | Presentation query |
| `AssetDetailsContext` | `model_type_configs` property | `AssetDetailService` | Presentation query |
| `DetailTableContext` | `list_all_details()` | `AssetDetailService` | Read-only query |
| `DetailTableContext` | `get_detail_by_id()` | `AssetDetailService` | Read-only query |
| `DetailTableContext` | `get_all_details_for_asset()` | `AssetDetailService` | Read-only aggregation |
| `DetailTableContext` | `get_details_by_type_for_asset()` | `AssetDetailService` | Read-only query |
| `ModelDetailContext` | `list_all_details()` | `ModelDetailService` | Read-only query |
| `ModelDetailContext` | `get_detail_by_id()` | `ModelDetailService` | Read-only query |
| `AssetDetailsUnionService` | Entire class | `AssetDetailUnionService` | Read-only service |
| `ModelDetailsUnionService` | Entire class | `ModelDetailUnionService` | Read-only service |

### Presentation Routes → Services Layer

| Route File | Pattern | New Service Method | Affected Lines |
|------------|---------|-------------------|----------------|
| `detail_tables.py` | Form options preparation | `AssetDetailService.get_form_options()` | 46-52, 72-73, 144-145 |
| `detail_tables.py` | Record filtering | `AssetDetailService.get_list_data()` | 31-43 |
| `detail_tables.py` | Config retrieval | `AssetDetailService.get_detail_table_config()` | 17-19, multiple |
| `model_details.py` | Record listing | `ModelDetailService.get_list_data()` | 34-35 |
| `model_details.py` | Config retrieval | `ModelDetailService.get_model_detail_table_config()` | 20-22 |
| `model_details.py` | Direct queries | `ModelDetailService.get_detail_for_model()` | 178-179, 194-195, 250-251, 266-267 |

---

## 5. Implementation Plan

### Phase 1: Create Service Structure
1. Create `app/services/assets/` directory
2. Create `__init__.py` with exports
3. Create `asset_detail_service.py` skeleton
4. Create `model_detail_service.py` skeleton
5. Create `asset_detail_union_service.py` (move from business)
6. Create `model_detail_union_service.py` (move from business)

### Phase 2: Move Read-Only Methods from Business Layer
1. Move `AssetDetailsContext` presentation methods to `AssetDetailService`
2. Move `DetailTableContext` read-only methods to `AssetDetailService`
3. Move `ModelDetailContext` read-only methods to `ModelDetailService`
4. Move union services to services layer
5. Update imports in business layer context managers

### Phase 3: Refactor Presentation Routes
1. Update `detail_tables.py` routes to use services
2. Update `model_details.py` routes to use services
3. Remove direct queries from routes
4. Update templates if needed

### Phase 4: Testing and Verification
1. Test all routes still work
2. Verify business layer still functions
3. Check for any remaining direct queries in routes
4. Verify service methods are properly documented

---

## 6. Benefits

1. **Clear Separation**: Read-only presentation queries separated from business logic
2. **Reusability**: Service methods can be used across multiple routes
3. **Maintainability**: Query logic centralized in services
4. **Testability**: Services can be tested independently
5. **Consistency**: Follows same pattern as `core` services
6. **Performance**: Union services in services layer where they belong

---

## 7. Risk Assessment

- **Risk Level**: **MEDIUM**
- **Complexity**: Higher than core services due to detail table system complexity
- **Affected Files**: 
  - 2 business context managers
  - 2 union service classes
  - 2 presentation route files
  - Multiple route handlers
- **Testing Required**: Extensive testing of detail table operations
- **Breaking Changes**: None expected (backward compatible if methods kept in business layer initially)

---

## 8. Approval Status

- ✅ **Analysis Complete**
- ✅ **Proposals Documented**
- ⏳ **Awaiting Approval**
- ⏳ **Implementation Pending**

---

## Notes

- Union services have a WARNING comment saying "for UI integration purposes only" - this confirms they should be in services layer
- Some business layer methods may need to remain as wrappers that delegate to services
- Configuration methods can stay accessible from both layers (non-breaking)
- Consider keeping deprecated methods in business layer for one release cycle


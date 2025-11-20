# Maintenance Services Refactoring Proposal

## Overview
This document outlines the proposed refactoring of maintenance-related business logic and presentation logic into the `services/maintenance` layer, following the same pattern established for `services/core` and `services/assets`.

## Goals
1. Move read-only, presentation-specific query logic from `business/maintenance` to `services/maintenance`
2. Move query building, filtering, and pagination from `presentation/routes/maintenance` to service classes
3. Centralize form option retrieval and data aggregation in service classes
4. Create a parallel folder structure: `app/services/maintenance/` matching `app/buisness/maintenance/`

## Proposed Service Structure

```
app/services/maintenance/
├── __init__.py
├── maintenance_service.py          # Dashboard statistics and aggregations
├── maintenance_plan_service.py     # Maintenance plan list/filter/form data
├── maintenance_action_set_service.py  # Action set list/filter/form data
├── action_service.py               # Action list/filter/form data
├── part_demand_service.py          # Part demand list/filter/form data
├── template_action_set_service.py  # Template action set list/filter
├── template_action_item_service.py # Template action item list/filter
├── template_part_demand_service.py # Template part demand list/filter
├── template_action_tool_service.py # Template action tool list/filter
└── delay_service.py                # Maintenance delay list/filter
```

---

## 1. Maintenance Dashboard Service (`maintenance_service.py`)

### Logic to Move from `presentation/routes/maintenance/main.py` - `index()` route:

**Current Logic:**
- Statistics counting (plans, action sets, actions, part demands)
- Template statistics counting
- Overdue actions query
- Due soon actions query
- In progress actions query
- Recent items queries (plans, actions)
- Status breakdown aggregations

**Proposed Methods:**
```python
class MaintenanceService:
    @staticmethod
    def get_dashboard_statistics() -> Dict[str, int]:
        """Get core maintenance statistics"""
        
    @staticmethod
    def get_template_statistics() -> Dict[str, int]:
        """Get template-related statistics"""
        
    @staticmethod
    def get_overdue_actions(limit: int = 10) -> List[Action]:
        """Get overdue actions"""
        
    @staticmethod
    def get_due_soon_actions(limit: int = 10, days: int = 7) -> List[Action]:
        """Get actions due soon"""
        
    @staticmethod
    def get_in_progress_actions(limit: int = 10) -> List[Action]:
        """Get actions currently in progress"""
        
    @staticmethod
    def get_recent_maintenance_plans(limit: int = 10) -> List[MaintenancePlan]:
        """Get recent maintenance plans"""
        
    @staticmethod
    def get_recent_actions(limit: int = 10) -> List[Action]:
        """Get recent actions"""
        
    @staticmethod
    def get_actions_by_status() -> Dict[str, int]:
        """Get action counts grouped by status"""
        
    @staticmethod
    def get_plans_by_status() -> Dict[str, int]:
        """Get maintenance plan counts grouped by status"""
        
    @staticmethod
    def get_create_event_form_options() -> Dict[str, List]:
        """Get form options for creating maintenance event"""
        # Returns: {'assets': [...], 'template_action_sets': [...]}
```

---

## 2. Maintenance Plan Service (`maintenance_plan_service.py`)

### Logic to Move from `presentation/routes/maintenance/maintenance_plans.py`:

**From `list()` route:**
- Query building with filtering (asset_type_id, model_id, status, frequency_type, name)
- Pagination
- Form option retrieval (asset_types, make_models)

**From `create()` and `edit()` routes:**
- Form option retrieval (asset_types, make_models, template_action_sets)

**Proposed Methods:**
```python
class MaintenancePlanService:
    @staticmethod
    def get_list_data(
        page: int = 1,
        per_page: int = 20,
        asset_type_id: Optional[int] = None,
        model_id: Optional[int] = None,
        status: Optional[str] = None,
        frequency_type: Optional[str] = None,
        name: Optional[str] = None
    ) -> Tuple[Pagination, Dict[str, Any]]:
        """Get paginated maintenance plans with filters and form options"""
        # Returns: (pagination_object, {'asset_types': [...], 'make_models': [...]})
        
    @staticmethod
    def get_form_options() -> Dict[str, List]:
        """Get form options for create/edit forms"""
        # Returns: {'asset_types': [...], 'make_models': [...], 'template_action_sets': [...]}
        
    @staticmethod
    def get_recent_action_sets(plan_id: int, limit: int = 10) -> List[MaintenanceActionSet]:
        """Get recent action sets for a maintenance plan"""
        # This is currently in MaintenancePlanContext.get_recent_action_sets()
        # Move to service layer as it's read-only presentation data
```

### Logic to Move from `business/maintenance/maintenance_plan_context.py`:

**Methods to Move to Service:**
- `get_recent_action_sets(limit)` - Read-only query, presentation-specific

---

## 3. Maintenance Action Set Service (`maintenance_action_set_service.py`)

### Logic to Move from `presentation/routes/maintenance/maintenance_action_sets.py`:

**From `list()` route:**
- Complex query building with joins (Asset, MajorLocation)
- Filtering by asset_id (partial match), location, plan, status, priority, task_name
- Eager loading to prevent N+1 queries
- Pagination
- Form option retrieval (assets, maintenance_plans)

**From `create()` and `edit()` routes:**
- Form option retrieval (assets, template_action_sets, maintenance_plans)

**From `template_actions_search()` route:**
- Template action item search query

**Proposed Methods:**
```python
class MaintenanceActionSetService:
    @staticmethod
    def get_list_data(
        page: int = 1,
        per_page: int = 20,
        asset_id: Optional[str] = None,  # String for partial match
        location: Optional[str] = None,
        maintenance_plan_id: Optional[int] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        task_name: Optional[str] = None
    ) -> Tuple[Pagination, Dict[str, Any]]:
        """Get paginated action sets with filters and form options"""
        # Returns: (pagination_object, {'assets': [...], 'maintenance_plans': [...]})
        
    @staticmethod
    def get_form_options() -> Dict[str, List]:
        """Get form options for create/edit forms"""
        # Returns: {'assets': [...], 'template_action_sets': [...], 'maintenance_plans': [...]}
        
    @staticmethod
    def search_template_action_items(
        query: Optional[str] = None,
        page: int = 1,
        page_size: int = 16
    ) -> List[TemplateActionItem]:
        """Search template action items for HTMX endpoint"""
```

---

## 4. Action Service (`action_service.py`)

### Logic to Move from `presentation/routes/maintenance/actions.py`:

**From `list()` route:**
- Query building with filtering (status, maintenance_action_set_id, action_name)
- Pagination
- Form option retrieval (maintenance_action_sets)

**From `create()` route:**
- Form option retrieval (maintenance_action_sets, template_action_items)

**Proposed Methods:**
```python
class ActionService:
    @staticmethod
    def get_list_data(
        page: int = 1,
        per_page: int = 20,
        status: Optional[str] = None,
        maintenance_action_set_id: Optional[int] = None,
        action_name: Optional[str] = None
    ) -> Tuple[Pagination, Dict[str, Any]]:
        """Get paginated actions with filters and form options"""
        # Returns: (pagination_object, {'maintenance_action_sets': [...]})
        
    @staticmethod
    def get_form_options() -> Dict[str, List]:
        """Get form options for create form"""
        # Returns: {'maintenance_action_sets': [...], 'template_action_items': [...]}
```

---

## 5. Part Demand Service (`part_demand_service.py`)

### Logic to Move from `presentation/routes/maintenance/part_demands.py`:

**From `list()` route:**
- Query building with eager loading
- Filtering by action_id, action_set_id, part_id, status
- Pagination
- Form option retrieval (actions, action_sets, parts, statuses)

**From `create()` and `edit()` routes:**
- Form option retrieval (actions, parts, template_part_demands)

**Proposed Methods:**
```python
class PartDemandService:
    @staticmethod
    def get_list_data(
        page: int = 1,
        per_page: int = 20,
        action_id: Optional[int] = None,
        action_set_id: Optional[int] = None,
        part_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> Tuple[Pagination, Dict[str, Any]]:
        """Get paginated part demands with filters and form options"""
        # Returns: (pagination_object, {'actions': [...], 'action_sets': [...], 'parts': [...], 'statuses': [...]})
        
    @staticmethod
    def get_form_options() -> Dict[str, List]:
        """Get form options for create/edit forms"""
        # Returns: {'actions': [...], 'parts': [...], 'template_part_demands': [...]}
        
    @staticmethod
    def get_distinct_statuses() -> List[str]:
        """Get all distinct status values for filtering"""
```

---

## 6. Template Action Set Service (`template_action_set_service.py`)

### Logic to Move from `presentation/routes/maintenance/template_action_sets.py`:

**From `list()` route:**
- Query building with filtering (task_name)
- Pagination

**Proposed Methods:**
```python
class TemplateActionSetService:
    @staticmethod
    def get_list_data(
        page: int = 1,
        per_page: int = 20,
        task_name: Optional[str] = None
    ) -> Pagination:
        """Get paginated template action sets with filters"""
```

---

## 7. Template Action Item Service (`template_action_item_service.py`)

### Logic to Move from `presentation/routes/maintenance/template_action_items.py`:

**From `list()` route:**
- Query building with filtering (template_action_set_id, action_name, is_required)
- Pagination
- Form option retrieval (template_action_sets)

**From `detail()` route:**
- Related data queries (template_part_demands, template_action_tools)

**From `create()` and `edit()` routes:**
- Form option retrieval (template_action_sets)

**Proposed Methods:**
```python
class TemplateActionItemService:
    @staticmethod
    def get_list_data(
        page: int = 1,
        per_page: int = 20,
        template_action_set_id: Optional[int] = None,
        action_name: Optional[str] = None,
        is_required: Optional[bool] = None
    ) -> Tuple[Pagination, Dict[str, Any]]:
        """Get paginated template action items with filters and form options"""
        # Returns: (pagination_object, {'template_action_sets': [...]})
        
    @staticmethod
    def get_form_options() -> Dict[str, List]:
        """Get form options for create/edit forms"""
        # Returns: {'template_action_sets': [...]}
        
    @staticmethod
    def get_related_data(template_action_item_id: int) -> Dict[str, Any]:
        """Get related part demands and tools for detail view"""
        # Returns: {'template_part_demands': [...], 'template_action_tools': [...]}
```

---

## 8. Template Part Demand Service (`template_part_demand_service.py`)

### Logic to Move from `presentation/routes/maintenance/template_part_demands.py`:

**From `list()` route:**
- Query building with eager loading and filtering
- Pagination
- Form option retrieval (template_action_items, parts)

**From `create()` and `edit()` routes:**
- Form option retrieval (template_action_items, parts)

**Proposed Methods:**
```python
class TemplatePartDemandService:
    @staticmethod
    def get_list_data(
        page: int = 1,
        per_page: int = 20,
        template_action_item_id: Optional[int] = None,
        part_id: Optional[int] = None,
        is_optional: Optional[bool] = None
    ) -> Tuple[Pagination, Dict[str, Any]]:
        """Get paginated template part demands with filters and form options"""
        # Returns: (pagination_object, {'template_action_items': [...], 'parts': [...]})
        
    @staticmethod
    def get_form_options() -> Dict[str, List]:
        """Get form options for create/edit forms"""
        # Returns: {'template_action_items': [...], 'parts': [...]}
```

---

## 9. Template Action Tool Service (`template_action_tool_service.py`)

### Logic to Move from `presentation/routes/maintenance/template_action_tools.py`:

**From `list()` route:**
- Query building with filtering (template_action_item_id, tool_id, is_required)
- Pagination
- Form option retrieval (template_action_items, tools)

**From `create()` and `edit()` routes:**
- Form option retrieval (template_action_items, tools)

**Proposed Methods:**
```python
class TemplateActionToolService:
    @staticmethod
    def get_list_data(
        page: int = 1,
        per_page: int = 20,
        template_action_item_id: Optional[int] = None,
        tool_id: Optional[int] = None,
        is_required: Optional[bool] = None
    ) -> Tuple[Pagination, Dict[str, Any]]:
        """Get paginated template action tools with filters and form options"""
        # Returns: (pagination_object, {'template_action_items': [...], 'tools': [...]})
        
    @staticmethod
    def get_form_options() -> Dict[str, List]:
        """Get form options for create/edit forms"""
        # Returns: {'template_action_items': [...], 'tools': [...]}
```

---

## 10. Delay Service (`delay_service.py`)

### Logic to Move from `presentation/routes/maintenance/delays.py`:

**From `list()` route:**
- Query building with filtering (maintenance_action_set_id, delay_type, is_active)
- Pagination
- Form option retrieval (maintenance_action_sets)

**From `create()` and `edit()` routes:**
- Form option retrieval (maintenance_action_sets)

**Proposed Methods:**
```python
class DelayService:
    @staticmethod
    def get_list_data(
        page: int = 1,
        per_page: int = 20,
        maintenance_action_set_id: Optional[int] = None,
        delay_type: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Tuple[Pagination, Dict[str, Any]]:
        """Get paginated delays with filters and form options"""
        # Returns: (pagination_object, {'maintenance_action_sets': [...]})
        
    @staticmethod
    def get_form_options() -> Dict[str, List]:
        """Get form options for create/edit forms"""
        # Returns: {'maintenance_action_sets': [...]}
```

---

## Business Layer Methods Review

### Methods to Keep in Business Layer:
- `MaintenancePlanContext` - All property accessors (these provide structured business logic access)
- `MaintenanceActionSetContext` - Property accessors, `get_part_demand_info()`, `get_part_demand_statistics()` (complex business logic with inventory integration)
- `ActionContext` - All property accessors (business logic access)
- `MaintenanceEvent` - All methods (wraps business logic for maintenance workflows)
- Factory classes - All factories (business creation logic)

### Methods to Move to Services Layer:
- `MaintenancePlanContext.get_recent_action_sets(limit)` - Read-only query, presentation-specific

**Note:** The business layer context classes primarily provide property accessors and complex business logic. Most of the query logic is already in the presentation routes and should move to services.

---

## Implementation Plan

### Phase 1: Create Service Structure
1. Create `app/services/maintenance/` directory
2. Create `__init__.py` with service exports
3. Create all service class files with empty classes

### Phase 2: Implement Dashboard Service
1. Implement `MaintenanceService` with all dashboard statistics methods
2. Update `maintenance/main.py` `index()` route to use service

### Phase 3: Implement Core Entity Services
1. Implement `MaintenancePlanService`
2. Implement `MaintenanceActionSetService`
3. Implement `ActionService`
4. Implement `PartDemandService`
5. Update respective routes

### Phase 4: Implement Template Services
1. Implement `TemplateActionSetService`
2. Implement `TemplateActionItemService`
3. Implement `TemplatePartDemandService`
4. Implement `TemplateActionToolService`
5. Update respective routes

### Phase 5: Implement Delay Service
1. Implement `DelayService`
2. Update `delays.py` route

### Phase 6: Clean Up Business Layer
1. Move `MaintenancePlanContext.get_recent_action_sets()` to `MaintenancePlanService`
2. Update business layer usage if needed

### Phase 7: Testing and Verification
1. Test all routes still work
2. Verify no N+1 query issues
3. Check pagination works correctly
4. Verify form options are correct

---

## Benefits

1. **Consistency**: Maintenance routes will follow the same pattern as core and assets routes
2. **Testability**: Services can be unit tested independently
3. **Reusability**: Service methods can be used by multiple routes or API endpoints
4. **Maintainability**: Query logic centralized in one place per entity
5. **Performance**: Services can optimize queries with eager loading in one place
6. **Clarity**: Routes become thin controllers focused on HTTP handling

---

## Notes

- All services should use `from flask_sqlalchemy.pagination import Pagination` for type hints
- Form options should be retrieved in service methods to avoid N+1 queries
- Eager loading should be applied in service methods where needed
- Filter logic should be in service methods, not routes
- Business layer contexts remain for complex business logic and property access


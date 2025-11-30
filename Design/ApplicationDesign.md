# Asset Management System - Application Design

## Project Overview
Create a comprehensive asset management system using Flask, SQLAlchemy, and HTMX. The application should manage assets, maintenance, dispatch, supply chain, and planning operations with minimal JavaScript and CSS.

## Technology Stack
- **Backend**: Flask with SQLAlchemy ORM
- **Frontend**: HTMX for dynamic interactions, minimal Alpine.js for complex interactions, vanilla JS only when necessary
- **Database**: SQLite (development)
- **Styling**: Minimal CSS, focus on functionality over aesthetics
- **Forms**: Standard HTML forms with HTMX attributes. Minimize form validation during initial development.
- **File Operations**: Use `pathlib.Path` for all file and directory operations instead of `os.path`

## Coding Standards

### Layered Architecture Compliance

All code must follow the layered architecture pattern. This is a **mandatory coding standard**.

#### Layer Placement Rules

1. **Database Models** → `app/data/`
   - All SQLAlchemy models must be in the data layer
   - Models should contain only database structure, no business logic
   - Use `app.data.*` for all model imports
   - **Must maintain parallel structure** - organize by domain (core, assets, maintenance, etc.)

2. **Business Logic** → `app/buisness/`
   - Context managers, factories, and business rules go in business layer
   - Business logic should be independent of presentation
   - Use `app.buisness.*` for business logic imports
   - **Must mirror data layer structure** - `app/data/core/` → `app/buisness/core/`

3. **Route Handlers** → `app/presentation/routes/`
   - All Flask routes must be in the presentation layer
   - Routes should be thin and delegate to business layer or services
   - Use `app.presentation.routes.*` for route imports
   - **Must mirror data layer structure** - `app/data/core/` → `app/presentation/routes/core/`
      - Routes should generally follow the data layer's subfolder structure as a guideline, with flexibility for practical routing needs (e.g., grouping related routes, RESTful organization)

4. **Templates and Static Files** → `app/presentation/`
   - All Jinja2 templates in `app/presentation/templates/`
   - All static files (CSS, JS) in `app/presentation/static/`
   - Templates and static files may have their own optimized structure (exception to parallel structure)

5. **Presentation Services** → `app/services/`
   - Data getters and aggregation functions for routes
   - Presentation-specific utilities that don't modify core models
   - Dashboard statistics, search helpers, formatting utilities
   - Use `app.services.*` for service imports
   - **Must mirror data layer structure** - `app/data/core/` → `app/services/core/`

#### Parallel Structure Requirement

**Mandatory**: All layers (data, business, presentation/routes, services) must maintain parallel folder structures that mirror the data layer organization.

**Example - Core Domain**:
```
app/data/core/              # Reference structure
app/buisness/core/          # Mirrors data/core/
app/presentation/routes/core/  # Mirrors data/core/
app/services/core/          # Mirrors data/core/
```

**Example - Assets Domain**:
```
app/data/assets/            # Reference structure
app/buisness/assets/       # Mirrors data/assets/
app/presentation/routes/assets/  # Mirrors data/assets/
app/services/assets/       # Mirrors data/assets/
```

**Benefits**:
- Easy to find related code across all layers
- Consistent organization throughout codebase
- Domain changes are localized across layers
- Faster onboarding for new developers

#### Import Standards

```python
# ✅ Correct - Data layer imports
from app.data.core.asset_info.asset import Asset
from app.data.core.user_info.user import User

# ✅ Correct - Business layer imports
from app.buisness.assets.asset_context import AssetContext
from app.buisness.maintenance.maintenance_event import MaintenanceEvent

# ✅ Correct - Presentation layer imports
from app.presentation.routes.assets import assets_bp
from app.services.dashboard_service import DashboardService

# ❌ Incorrect - Wrong layer imports
from app.models.core.asset import Asset  # Old path - don't use
from app.domain.assets import AssetContext  # Old path - don't use
```

#### Layer Violation Prevention

- **Never** put business logic in data models
- **Never** put presentation logic in business layer
- **Never** modify core models from services layer (read-only)
- **avoid** putting database queries directly in routes (use business layer or services)

#### Data Model Priority and Type Conversion

**CRITICAL**: Data models take priority over presentation layer form data.

- **Models define the source of truth** - field names, types, and structure come from the data models
- **Presentation and service layers must convert form data** to match business and data models, not the other way around
- **Form field names should match model field names** - if they don't, convert at the presentation/service layer
- **Type conversion responsibility**: Presentation routes and services must convert string form data to appropriate types (dates, integers, floats, booleans) based on model column types
- **Never modify data models** to match form field names or types - always adapt the form handling code

**Example**:
```python
# ✅ Correct - Convert form data to match model
purchase_date_str = request.form.get('purchase_date')
purchase_date = datetime.strptime(purchase_date_str, '%Y-%m-%d').date() if purchase_date_str else None
purchase_info.purchase_date = purchase_date  # Model expects date object

# ❌ Incorrect - Don't change model to match form
# purchase_info.purchase_date = purchase_date_str  # Wrong - model expects date, not string
```

### File Path Handling
- **Use `pathlib.Path`**: All file and directory operations should use `pathlib.Path` instead of `os.path`
- **Benefits**: More readable, object-oriented, cross-platform compatible
- **Examples**:
  ```python
  # ✅ Good - Use pathlib
  from pathlib import Path
  config_file = Path(__file__).parent.parent / 'utils' / 'build_data.json'
  if config_file.exists():
      data = config_file.read_text()
  
  # ❌ Avoid - Don't use os.path
  import os
  config_file = os.path.join(os.path.dirname(__file__), '..', 'utils', 'build_data.json')
  if os.path.exists(config_file):
      with open(config_file, 'r') as f:
          data = f.read()
  ```

## HTMX Implementation Guidelines

### 1. Form Handling
- Use standard HTML forms with `hx-post`, `hx-get`, `hx-put`, `hx-delete`
- Implement form validation with server-side responses
- Use `hx-target` to update specific page sections
- Leverage `hx-swap` for smooth transitions

### 1.1. Card/Widget Updates (Preferred Pattern)
- **Prefer full page GET requests** with `hx-target` and `hx-swap` extracting/replacing the widget container itself

- **Avoid creating dedicated routes** for widget subsection replacement when possible
- This approach simplifies routing, improves cacheability, and maintains consistent page state

**Preferred Pattern**:
```html
<!-- Widget container that updates itself -->
<div id="event-widget-container"
     hx-get="{{ url_for('maintenance.do_maintenance', action_set_id=action_set_id) }}"
     hx-trigger="every 5s"
     hx-target="this"
     hx-select="#event-widget-container"
     hx-swap="outerHTML">
    <!-- Widget content -->
</div>
```

**Benefits**:
- Single route handles both full page and widget updates
- Better browser caching (full page responses are cacheable)
- Consistent state between full page and widget views
- Simpler route structure (no separate widget endpoints)
- Easier debugging (full page always available)

**When to Use Dedicated Widget Routes**:
- Widget requires significantly different data than full page
- Widget updates are very frequent and full page is expensive
- Widget needs to be embeddable in multiple contexts with different parameters

### 2. Dynamic Content
- Asset lists with real-time filtering
- Maintenance schedules with drag-and-drop (Alpine.js if needed)
- Status updates without page refresh
- Search results with instant feedback

### 3. User Experience
- Loading states with `hx-indicator`
- Error handling with `hx-on::after-request`
- Confirmation dialogs for destructive actions
- Progressive enhancement for better UX

### 4. Alpine.js Integration
- Use only for complex interactions HTMX can't handle
- Form validation with real-time feedback
- Dynamic form field generation
- Complex state management

## Code Quality Standards
- Follow PEP 8 for Python code
- Use type hints where appropriate
- Implement comprehensive error handling
- Write unit tests for critical functionality
- Use meaningful variable and function names
- Document complex business logic
- Implement proper logging

## Security Considerations
- Input validation and sanitization
- SQL injection prevention with SQLAlchemy
- CSRF protection for forms
- User authentication and authorization
- Secure file upload handling
- Audit logging for sensitive operations
- Role-based access control (RBAC)
- System user protection (cannot be modified by regular users)

### HTMX Search Bar Pattern

The application uses a consistent HTMX pattern for search bars that provide autocomplete-style dropdowns with match count feedback.

**Route Pattern**: `{cardname}/search-bars/{title}` (e.g., `/create-assign/search-bars/templates`)

**Implementation Flow**:
1. Search input triggers HTMX request on input (300ms debounce) and focus
2. Route endpoint returns HTML fragment with filtered results
3. Service layer provides filtered data based on search and additional filters
4. Template fragment renders results with match count feedback
5. JavaScript handles item selection and dropdown visibility

**Key Features**:
- Debounced search (300ms delay) prevents excessive requests
- Focused swaps update only the results div, not the entire page
- Match count feedback shows "Showing X of Y matches" when results are limited
- Filter integration via `hx-include` for additional filter fields
- Service layer methods return filtered results with total count

Examples:
- `/create-assign/search-bars/templates` - Template search results
- `/create-assign/search-bars/assets` - Asset search results  
- `/create-assign/search-bars/assignment` - Technician/assignment search results

#### Implementation Structure

1. **User Input Field**: Search input with HTMX attributes
2. **HTMX Request**: Triggers on input with debounce delay
3. **Route Endpoint**: Returns HTML fragment with search results
4. **Service Layer**: Provides filtered data based on search and additional filters
5. **Template Fragment**: Renders results with match count feedback


## Database Build System

### Build Command-Line Flags
The application supports command-line flags for controlling database initialization:

```bash
python app.py [OPTIONS]

Options:
  --build-only          Build database tables only, exit without starting server
  --enable-debug-data   Enable debug data insertion (default: True)
  --no-debug-data       Disable debug data insertion
  --phase1, --phase2a, --phase2b, --all  Build specific phases (default: all)
```

**Usage Examples**:
- `python app.py --build-only`: Initialize database with all data, then exit
- `python app.py --build-only --no-debug-data`: Initialize database with only critical data
- `python app.py`: Normal startup (builds if needed, then starts server)

### Debug Data System
The debug data system (`app/debug/`) provides modular test data insertion:

- **Critical Data**: Always inserted from `app/data/core/build_data_critical.json` (essential production data)
- **Debug Data**: Optionally inserted from `app/debug/data/*.json` when `--enable-debug-data` is set (default)
- **Idempotent**: Automatically skips insertion if data already exists
- **Phase-Aware**: Respects build dependencies (core → assets → dispatching → inventory → maintenance)
- **Factory-Based**: Uses business layer factories and contexts for proper data creation

See [SystemDesign.md](SystemDesign.md) for detailed architecture information.

## References
- **System Design**: See [SystemDesign.md](SystemDesign.md) for architecture, modules, and development patterns
- **Widget Components**: See [widgets.md](widgets.md) for tracked widget components
- **Application Structure**: See [application_structure.md](application_structure.md) for detailed file structure


save work summaries to root directory do not save them in the design folder

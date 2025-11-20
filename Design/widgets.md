# Widget Components

This document tracks reusable subcomponents (widgets) used throughout the application. Widgets are self-contained UI components that can be embedded in multiple pages and updated independently.

## Widget Pattern

Widgets follow the preferred HTMX pattern:
- Full page GET requests with `hx-target` and `hx-swap` extracting/replacing the widget container
- Use `hx-select` to extract widget content from full page responses
- Self-updating containers that replace themselves

## Tracked Widgets

### Event Activity Widget
**Location**: `app/presentation/templates/components/event_widget.html`  
**Route**: `comments.event_widget`  
**Purpose**: Displays event comments, attachments, and metadata in a tabbed interface  
**Usage**: Embedded in maintenance action sets, asset detail pages, and other event-related views  
**Update Pattern**: Uses `hx-get` with `hx-target="#event-widget-card"` and `hx-swap="outerHTML"`  
**Features**:
- Comments tab with filtering (human-only/all comments)
- Attachments tab
- Event metadata display
- Real-time updates via HTMX

**Example Usage**:
```html
<div id="event-widget-container"
     hx-get="{{ url_for('comments.event_widget', event_id=event.id) }}"
     hx-trigger="load"
     hx-target="#event-widget-container"
     hx-swap="outerHTML">
    <div class="card mb-4">
        <div class="card-body text-center text-muted">
            Loading event activity...
        </div>
    </div>
</div>
```

---

### Condensed Events Card
**Location**: `app/presentation/templates/core/events/condensed_events_snippet.html`  
**Route**: `events.events_card`  
**Purpose**: Displays a condensed list of recent events for assets, locations, or users  
**Usage**: Include snippet in templates with context parameters  
**Update Pattern**: Uses `hx-get` with `hx-select` to extract card content  
**Parameters**:
- `row_count` (default: 5) - Number of events to display
- `asset_id` (optional) - Filter by asset
- `major_location_id` (optional) - Filter by location
- `user_id` (optional) - Filter by user

**Example Usage**:
```html
{% include 'core/events/condensed_events_snippet.html' with context %}
{% set asset_id = asset.id %}
{% set row_count = 10 %}
```

---

### Asset Details Card
**Location**: Embedded in asset list templates  
**Route**: `core_assets.asset_details_card`  
**Purpose**: Displays detailed information about a selected asset  
**Usage**: Used in asset list pages to show details without navigation  
**Update Pattern**: Uses `hx-get` with `hx-swap="innerHTML"` to update container content  
**Features**:
- Displays when asset row is clicked
- Shows asset details, history, and related information

**Example Usage**:
```html
<div id="asset-details-container"
     hx-get="{{ url_for('core_assets.asset_details_card') }}"
     hx-trigger="load"
     hx-swap="innerHTML">
    <div class="text-center py-4">
        <i class="bi bi-arrow-up text-muted"></i>
        <p class="text-muted mt-2">Click on any asset row above to view its details here</p>
    </div>
</div>
```

---

### Detail Table Cards
**Location**: `app/presentation/templates/components/detail_tables/cards/`  
**Purpose**: Small cards displaying asset detail table information  
**Usage**: Used in asset detail pages to show various detail table records  
**Types**:
- `small_card.html` - Base card template
- Type-specific summary templates (e.g., `purchase_info_summary.html`)

**Features**:
- Edit and delete actions
- Summary information display
- Creation/update timestamps

---

## Widget Development Guidelines

### Creating New Widgets

1. **Use Full Page Pattern**: Prefer full page GET requests with extraction over dedicated widget routes
2. **Self-Contained**: Widgets should be self-contained and replaceable
3. **Consistent IDs**: Use consistent ID patterns for widget containers
4. **Loading States**: Always include loading states for better UX
5. **Error Handling**: Include error handling for failed requests

### Widget Template Structure

```html
<!-- Widget Container -->
<div id="widget-name-container"
     hx-get="{{ url_for('route.name', param=value) }}"
     hx-trigger="load"
     hx-target="this"
     hx-select="#widget-name-container"
     hx-swap="outerHTML">
    <!-- Loading State -->
    <div class="card">
        <div class="card-body text-center text-muted">
            Loading widget content...
        </div>
    </div>
</div>
```

### Widget Route Pattern

```python
@bp.route('/page/<int:id>')
def page_detail(id):
    """Full page route that also serves widget content"""
    # ... get data ...
    return render_template('page/detail.html', data=data)

# Widget content is extracted from full page using hx-select
```

## Widget Registry

| Widget Name | Template Location | Route | Purpose | Status |
|------------|------------------|-------|---------|--------|
| Event Activity | `components/event_widget.html` | `comments.event_widget` | Event comments/attachments | ✅ Active |
| Condensed Events | `core/events/condensed_events_snippet.html` | `events.events_card` | Recent events list | ✅ Active |
| Asset Details | Embedded in list templates | `core_assets.asset_details_card` | Asset detail display | ✅ Active |
| Detail Table Cards | `components/detail_tables/cards/` | Various | Detail table displays | ✅ Active |

## Future Widgets

Widgets planned for future implementation:

- **Maintenance Progress Widget**: Visual progress indicator for maintenance action sets
- **Asset Status Widget**: Real-time asset status and location display
- **Inventory Level Widget**: Stock level indicators for parts
- **Dispatch Timeline Widget**: Visual timeline of dispatch events

## Notes

- All widgets should follow the HTMX full-page pattern unless there's a specific reason for dedicated routes
- Widgets should be documented here when created
- Update this file when modifying widget behavior or adding new widgets


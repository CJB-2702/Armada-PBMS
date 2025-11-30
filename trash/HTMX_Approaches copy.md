# HTMX Implementation Approaches for Template Builder

## Overview
Multiple approaches to implement HTMX with minimal changes to existing routes and templates.

---

## Approach 1: Full Page Response with HTMX Selector Swap (Easiest)

**Concept**: Routes continue returning full pages, but HTMX extracts and swaps only the target section using CSS selectors.

### How It Works
- Form submits via HTMX POST
- Route returns full page HTML (as it does now)
- HTMX uses `hx-select` to extract only the metadata section from the response
- Swaps the old metadata section with the new one

### Pros
- ✅ Zero route changes needed
- ✅ Minimal template changes (just add HTMX attributes)
- ✅ Works with existing flash messages (they're in the full page response)

### Cons
- ⚠️ Slightly less efficient (sends/receives full page, but only swaps section)
- ⚠️ Need to ensure consistent IDs/classes for swapping

### Example Implementation
```html
<!-- Metadata form with HTMX -->
<form method="POST" 
      action="{{ url_for('template_builder.update_metadata', builder_id=builder.builder_id) }}"
      hx-post="{{ url_for('template_builder.update_metadata', builder_id=builder.builder_id) }}"
      hx-target="#metadata-section"
      hx-select="#metadata-section"
      hx-swap="outerHTML">
    <div id="metadata-section" class="metadata-section">
        <!-- form content -->
    </div>
</form>
```

---

## Approach 2: Fragment Endpoints (Most Efficient)

**Concept**: Create new lightweight routes that return only HTML fragments for specific sections.

### How It Works
- Create new routes like `/template-builder/<id>/metadata/fragment`
- These routes return only the metadata section HTML
- Forms target these fragment endpoints
- HTMX swaps the section directly

### Pros
- ✅ Most efficient (only sends/receives needed HTML)
- ✅ Faster response times
- ✅ Clean separation of concerns

### Cons
- ⚠️ Requires new route endpoints
- ⚠️ Need to handle flash messages separately (via OOB swaps or hx-swap-oob)

### Example Implementation
```python
@template_builder_bp.route('/<int:builder_id>/metadata/fragment', methods=['GET'])
def get_metadata_fragment(builder_id):
    """Get metadata section fragment for HTMX."""
    builder_data = TemplateBuilderService.get_builder_data(builder_id)
    return render_template(
        'maintenance/manager/fragments/metadata_section.html',
        builder=builder_data
    )
```

```html
<form hx-post="{{ url_for('template_builder.update_metadata', builder_id=builder.builder_id) }}"
      hx-target="#metadata-section"
      hx-swap="outerHTML">
    <div id="metadata-section">
        <!-- form content -->
    </div>
</form>
```

---

## Approach 3: Hybrid - Full Page with Fragment Fallback

**Concept**: Use full page responses by default, but add fragment endpoints for optimization later.

### How It Works
- Start with Approach 1 (full page swap)
- Add fragment endpoints incrementally
- Forms can switch between full page and fragment endpoints
- Use `hx-boost="true"` for automatic HTMX on all forms

### Pros
- ✅ Gradual migration path
- ✅ Can optimize specific sections over time
- ✅ Flexible

### Cons
- ⚠️ More code to maintain
- ⚠️ Need to keep both approaches in sync

---

## Approach 4: Out-of-Band (OOB) Swaps for Multiple Updates

**Concept**: Update multiple sections from a single response using HTMX's OOB feature.

### How It Works
- Route returns full page with multiple sections marked with `hx-swap-oob="true"`
- HTMX updates all marked sections in one request
- Useful for updating metadata + actions list + header stats simultaneously

### Pros
- ✅ Update multiple sections in one request
- ✅ Great for complex interactions
- ✅ Maintains consistency across page

### Cons
- ⚠️ More complex template structure
- ⚠️ Need to mark all updateable sections

### Example Implementation
```html
<!-- In response template -->
<div id="metadata-section" hx-swap-oob="true">
    <!-- updated metadata -->
</div>
<div id="actions-list" hx-swap-oob="true">
    <!-- updated actions -->
</div>
<div id="header-stats" hx-swap-oob="true">
    <!-- updated stats -->
</div>
```

---

## Approach 5: Progressive Enhancement with hx-boost

**Concept**: Automatically convert all forms/links to HTMX requests, then customize specific ones.

### How It Works
- Add `hx-boost="true"` to main container
- All forms/links automatically use HTMX
- Override specific forms with custom HTMX attributes
- Use `hx-select` to swap only specific sections

### Pros
- ✅ Minimal changes needed
- ✅ Works automatically for all interactions
- ✅ Can customize specific forms as needed

### Cons
- ⚠️ Need to be careful with selectors
- ⚠️ May need to disable for some forms (like submit template)

---

## Recommended Implementation Strategy

### Phase 1: Start with Approach 1 (Full Page Swap)
- Easiest to implement
- Zero route changes
- Just add HTMX attributes to forms
- Use `hx-select` to extract sections from full page responses


### Phase 3: Use OOB Swaps (Approach 4)
- For complex operations that update multiple sections
- Maintain consistency across page
- Reduce number of requests

---

## Implementation Examples

### Metadata Card Save Button (Approach 1)
```html
<form method="POST" 
      action="{{ url_for('template_builder.update_metadata', builder_id=builder.builder_id) }}"
      hx-post="{{ url_for('template_builder.update_metadata', builder_id=builder.builder_id) }}"
      hx-target="#metadata-section"
      hx-select="#metadata-section"
      hx-swap="outerHTML"
      hx-indicator="#save-metadata-spinner">
    <div id="metadata-section" class="metadata-section">
        <!-- form fields -->
        <button type="submit">
            <span id="save-metadata-spinner" class="spinner-border spinner-border-sm htmx-indicator"></span>
            Save Metadata
        </button>
    </div>
</form>
```

### Actions List Updates
```html
<!-- Add action form -->
<form hx-post="{{ url_for('template_builder.add_action', builder_id=builder.builder_id) }}"
      hx-target="#actions-list-container"
      hx-select="#actions-list-container"
      hx-swap="outerHTML">
    <!-- form fields -->
</form>

<!-- Actions list container -->
<div id="actions-list-container">
    <!-- actions list -->
</div>
```

### Flash Messages with OOB
```html
<!-- In route response template -->
<div id="flash-messages" hx-swap-oob="true">
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
                <div class="alert alert-{{ category }}">{{ message }}</div>
            {% endfor %}
        {% endif %}
    {% endwith %}
</div>
```

---

## Key HTMX Attributes Reference

- `hx-post`, `hx-get`, `hx-put`, `hx-delete` - HTTP method
- `hx-target` - Element to swap into
- `hx-select` - CSS selector to extract from response
- `hx-swap` - How to swap (`innerHTML`, `outerHTML`, `beforebegin`, `afterend`, etc.)
- `hx-swap-oob="true"` - Out-of-band swap (updates multiple elements)
- `hx-indicator` - Element to show during request
- `hx-trigger` - When to trigger (default: `click` for buttons, `submit` for forms)
- `hx-confirm` - Confirmation dialog before request
- `hx-boost="true"` - Automatically convert links/forms to HTMX


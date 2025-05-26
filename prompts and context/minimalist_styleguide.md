# Armada PBMS Minimalist Style Guide

## Core Principles

1. **Native First**
   - Use native HTML elements whenever possible
   - Leverage built-in browser functionality
   - Minimize custom JavaScript
   - Embrace progressive enhancement

2. **Minimal CSS**
   - Use default browser styles
   - Only override when absolutely necessary
   - Keep custom CSS to a minimum
   - Use CSS variables for consistency

3. **Progressive Enhancement**
   - Start with basic HTML
   - Add HTMX for interactivity
   - Use Alpine.js only when necessary
   - Ensure basic functionality without JavaScript

## Typography

### Fonts
- **Lora**: Headers and branding
- **Fira Code**: Numbers and technical data
- **Inclusive Sans**: General content
- Use system fonts as fallback

```css
:root {
  --font-header: 'Lora', serif;
  --font-mono: 'Fira Code', monospace;
  --font-body: 'Inclusive Sans', sans-serif;
}
```

## Interactive Elements

### Collapsible Content
Use native `<details>` and `<summary>` elements:
```html
<details>
  <summary>Asset Details</summary>
  <div>
    <!-- Content -->
  </div>
</details>
```

### Dialogs
Use native `<dialog>` element:
```html
<dialog>
  <h2>Confirm Action</h2>
  <p>Are you sure you want to proceed?</p>
  <form method="dialog">
    <button>Cancel</button>
    <button>Confirm</button>
  </form>
</dialog>
```

### Forms
Use native form elements with minimal styling:
```html
<form>
  <label for="name">Name</label>
  <input type="text" id="name" name="name">
  
  <label for="email">Email</label>
  <input type="email" id="email" name="email">
  
  <button type="submit">Submit</button>
</form>
```

## HTMX Patterns

### Basic Loading
```html
<div hx-get="/api/data" 
     hx-trigger="load">
  Loading...
</div>
```

### Form Submission
```html
<form hx-post="/api/submit">
  <!-- Form fields -->
</form>
```

### Infinite Scroll
```html
<div hx-get="/api/items" 
     hx-trigger="revealed">
  <!-- Items -->
</div>
```

## Minimal CSS

### Buttons
```css
button {
  border: none;
  background: #0066CC;
  color: white;
  padding: 8px 16px;
  cursor: pointer;
}

button:hover {
  background: #0052A3;
}
```

### Layout
```css
:root {
  --spacing: 16px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--spacing);
}
```

## Alpine.js Usage

Only use Alpine.js when native HTML and HTMX are insufficient:

```html
<div x-data="{ open: false }">
  <button @click="open = !open">Toggle</button>
  <div x-show="open">
    <!-- Content -->
  </div>
</div>
```

## Best Practices

1. **HTML First**
   - Use semantic HTML elements
   - Leverage native form validation
   - Use appropriate ARIA attributes
   - Maintain proper heading hierarchy

2. **Minimal Styling**
   - Accept default browser styles
   - Only style buttons and containers
   - Use CSS variables for consistency
   - Keep custom CSS minimal

3. **Progressive Enhancement**
   - Ensure basic functionality without JS
   - Add HTMX for dynamic features, import by default
   - Use Alpine.js as a last resort
   - Do not import Alpine.js unless explitly being used in the page

4. **Accessibility**
   - Use native elements for better a11y
   - Maintain keyboard navigation
   - Ensure proper contrast
   - Test with screen readers

## Examples

### Collapsible Table
```html
<details>
  <summary>Asset List</summary>
  <table>
    <thead>
      <tr>
        <th>ID</th>
        <th>Name</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody>
      <!-- Table content -->
    </tbody>
  </table>
</details>
```

### Form with Validation
```html
<form hx-post="/api/submit">
  <label for="name">Name</label>
  <input type="text" id="name" name="name" required>
  
  <label for="email">Email</label>
  <input type="email" id="email" name="email" required>
  
  <button type="submit">Submit</button>
</form>
```

### Dialog with Form
```html
<dialog id="editDialog">
  <form method="dialog">
    <h2>Edit Asset</h2>
    <label for="assetName">Name</label>
    <input type="text" id="assetName" name="name" required>
    
    <button type="button" onclick="this.closest('dialog').close()">Cancel</button>
    <button type="submit">Save</button>
  </form>
</dialog>
```

## Responsive Design

Use native responsive features:
- `<picture>` for responsive images
- `srcset` for different image sizes
- CSS Grid for layouts
- Media queries only when necessary

## Error Handling

Use native form validation:
```html
<input type="email" required>
<div class="error-message">
  Please enter a valid email address
</div>
```

## Performance

1. **Minimize Dependencies**
   - Use native browser features
   - Keep JavaScript minimal
   - Avoid unnecessary libraries
   - Leverage browser caching

2. **Optimize Loading**
   - Use native lazy loading
   - Minimize CSS
   - Defer non-critical JavaScript
   - Use system fonts when possible 
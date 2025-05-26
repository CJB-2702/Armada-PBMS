# Armada PBMS Style Guide

## Typography

### Fonts
- **Lora**
  - Usage: Logo, branding, and page headers
  - Purpose: Elegance and readability for important text
  - Example: `<h1 class="lora-font">Armada PBMS</h1>`

- **Fira Code**
  - Usage: Numbers, user input, technical data
  - Purpose: Clear monospace display for numerical and technical content
  - Example: `<span class="fira-code">Asset #12345</span>`

- **Inclusive Sans**
  - Usage: General content, buttons, UI controls
  - Purpose: High readability for interactive elements
  - Example: `<button class="inclusive-sans">Submit</button>`

### Text Hierarchy
1. **Headers**
   - H1: Page titles (Lora)
   - H2: Section headers (Lora)
   - H3: Subsection headers (Inclusive Sans)
   - H4: Card headers (Inclusive Sans)

2. **Body Text**
   - Regular text: Inclusive Sans
   - Technical data: Fira Code
   - Links: Inclusive Sans with underline

## Layout

### Grid System
- Based on CSS Grid and Flexbox
- Power-of-two spacing (8px, 16px, 32px, 64px)
- Consistent component hierarchy

### Component Spacing
```css
/* Base spacing units */
:root {
  --spacing-xs: 8px;
  --spacing-sm: 16px;
  --spacing-md: 32px;
  --spacing-lg: 64px;
}
```

### Container Sizes
- Max-width: 1200px
- Sidebar width: 280px
- Card padding: var(--spacing-sm)

## Colors

### Light Mode
```css
:root {
  --primary: #0066CC;
  --secondary: #4D4D4D;
  --background: #FFFFFF;
  --surface: #F4F4F4;
  --text: #161616;
  --text-secondary: #525252;
  --border: #E0E0E0;
  --error: #DA1E28;
  --success: #24A148;
  --warning: #F1C21B;
}
```

### Dark Mode
```css
[data-theme="dark"] {
  --primary: #78A9FF;
  --secondary: #C6C6C6;
  --background: #161616;
  --surface: #262626;
  --text: #FFFFFF;
  --text-secondary: #C6C6C6;
  --border: #393939;
  --error: #FF8389;
  --success: #42BE65;
  --warning: #F1C21B;
}
```

## Components

### Cards
- Square corners (no border-radius)
- Consistent padding (var(--spacing-sm))
- Border: 1px solid var(--border)
- Background: var(--surface)

```html
<div class="card">
  <h3 class="card-header">Card Title</h3>
  <div class="card-body">
    <!-- Card content -->
  </div>
</div>
```

### Buttons
- Square corners
- Consistent padding (8px 16px)
- Clear hover states
- No shadows

```html
<button class="btn btn-primary">Primary Action</button>
<button class="btn btn-secondary">Secondary Action</button>
```

### Forms
- Consistent input heights
- Clear focus states
- Square corners
- Minimal styling

```html
<div class="form-group">
  <label for="input">Label</label>
  <input type="text" id="input" class="form-control">
</div>
```

### Tables
- Clean, minimal design
- Consistent cell padding
- No zebra striping
- Square corners

```html
<table class="table">
  <thead>
    <tr>
      <th>Header</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Content</td>
    </tr>
  </tbody>
</table>
```

## HTMX Patterns

### Loading States
```html
<div hx-get="/api/data" 
     hx-trigger="load" 
     hx-indicator="#loading">
  <!-- Content -->
</div>
<div id="loading" class="htmx-indicator">
  Loading...
</div>
```

### Form Submissions
```html
<form hx-post="/api/submit" 
      hx-swap="outerHTML">
  <!-- Form fields -->
</form>
```

### Infinite Scroll
```html
<div hx-get="/api/items" 
     hx-trigger="revealed" 
     hx-swap="beforeend">
  <!-- Items -->
</div>
```

## Responsive Design

### Breakpoints
```css
/* Mobile first approach */
@media (min-width: 768px) { /* Tablet */ }
@media (min-width: 1024px) { /* Desktop */ }
@media (min-width: 1280px) { /* Large Desktop */ }
```

### Layout Adjustments
- Single column on mobile
- Two columns on tablet
- Three columns on desktop
- Sidebar collapses on mobile

## Icons and Images

### Icons
- Use system icons
- Consistent size (24px)
- Square aspect ratio
- No decorative elements

### Images
- Maintain aspect ratios
- Optimize for web
- Use alt text
- Lazy loading

## Error States

### Form Errors
```html
<div class="form-group">
  <input type="text" class="form-control is-invalid">
  <div class="invalid-feedback">
    Error message
  </div>
</div>
```

### Toast Notifications
```html
<div class="toast toast-error">
  Error message
</div>
```

## Accessibility

### Color Contrast
- Minimum contrast ratio: 4.5:1
- Test with color contrast checker
- Provide alternative text

### Keyboard Navigation
- Focus visible states
- Logical tab order
- Skip links

### Screen Readers
- ARIA labels
- Semantic HTML
- Proper heading hierarchy

## Best Practices

1. **Minimalism**
   - Avoid unnecessary decorations
   - Use whitespace effectively
   - Keep interfaces clean

2. **Consistency**
   - Use consistent spacing
   - Maintain typography hierarchy
   - Follow component patterns

3. **Performance**
   - Minimize CSS
   - Optimize images
   - Use HTMX for dynamic content

4. **Maintenance**
   - Document components
   - Use CSS variables
   - Follow naming conventions 
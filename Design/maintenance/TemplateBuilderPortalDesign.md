# Template Builder Portal Design

## Overview

A web-based interface for building maintenance templates incrementally using the Template Builder system. Users can create templates from scratch, copy existing templates, and modify them before final submission.

## Core Workflow

1. **Start Building**: Create blank template or copy from existing template
2. **Edit Template**: Modify metadata (name, description, duration, etc.)
3. **Manage Actions**: Add, remove, reorder actions within the template
4. **Add Components**: Add parts, tools to actions
5. **Review & Submit**: Validate and convert to production TemplateActionSet

## Implementation Phases

### Phase 1: Basic Template Building
- Create template builder from existing template
- View template metadata and actions list
- Add custom action (from dict)
- Delete action (with auto-renumbering)
- Reorder actions (drag-and-drop or up/down buttons)
- Edit action details (name, description, etc.)
- Edit template metadata

### Phase 2: Add by ID
- Add action from proto action ID (form input)
- Add action from template action ID (form input)
- Add part demand from part ID (form input)
- Add tool from tool ID (form input)
- Basic validation and error handling

### Phase 3: Search Infrastructure - Proto Actions
- Search/filter proto actions
- Display proto action details
- Add proto action to builder from search results
- Browse proto action library

### Phase 4: Search Infrastructure - Template Actions
- Search/filter template actions
- Display template action details
- Add template action to builder from search results
- Browse template action library

## UI Structure

### Main Page: `/maintenance/manager/template-builder/<builder_id>`
- **Header**: Template name, build status, save indicator
- **Metadata Section**: Editable template fields (task_name, description, etc.)
- **Actions List**: 
  - Ordered list of actions with sequence numbers
  - Each action shows: name, description, part count, tool count
  - Action controls: edit, delete, move up/down
- **Action Detail Panel**: Shows selected action details, parts, tools
- **Add Action Section**: Buttons/forms for adding actions
- **Submit Button**: Convert to template (with validation)

### Routes
- `GET /maintenance/manager/template-builder/new` - Create new builder
- `GET /maintenance/manager/template-builder/new?from_template=<id>` - Copy from template
- `GET /maintenance/manager/template-builder/<id>` - View/edit builder
- `POST /maintenance/manager/template-builder/<id>/action/add` - Add action
- `POST /maintenance/manager/template-builder/<id>/action/<index>/delete` - Delete action
- `POST /maintenance/manager/template-builder/<id>/action/<index>/move` - Reorder action
- `POST /maintenance/manager/template-builder/<id>/submit` - Submit template

## Technical Approach

- Use Flask routes in `app/presentation/routes/maintenance/manager/`
- Leverage existing template patterns from maintenance portal
- Use HTMX for dynamic updates (following existing patterns)
- Store builder_id in Flask session for active builder
- Auto-save on each change (already implemented in context)
- Use existing struct/context patterns for data access

## Key Features

- **Real-time Updates**: Actions list updates immediately after changes
- **Sequence Management**: Automatic renumbering when actions are deleted/reordered
- **Validation**: Client-side validation before submission
- **Error Handling**: Clear error messages for invalid operations
- **Session Management**: Builder persists across page refreshes


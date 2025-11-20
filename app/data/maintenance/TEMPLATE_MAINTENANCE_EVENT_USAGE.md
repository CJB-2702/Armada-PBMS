# TemplateMaintenanceEvent Usage Guide

The `TemplateMaintenanceEvent` class provides a high-level interface for working with maintenance templates.

## Basic Usage

```python
from app.models.maintenance import TemplateMaintenanceEvent

# Create from ID
template = TemplateMaintenanceEvent.from_id(1)

# Create from task name
template = TemplateMaintenanceEvent.from_task_name("Engine Oil Change")

# Access properties
print(template.task_name)
print(template.description)
print(template.revision)
```

## Accessing Components

```python
# Get all action items (ordered by sequence)
for action_item in template.action_items:
    print(f"Action: {action_item.action_name}")
    print(f"  Required: {action_item.is_required}")
    print(f"  Duration: {action_item.estimated_duration}")

# Get all part demands (ordered by action)
for part_demand in template.part_demands:
    print(f"Part: {part_demand.part.part_name}")
    print(f"  Quantity: {part_demand.quantity_required}")
    print(f"  Required: {part_demand.is_required}")

# Get all tools (ordered by action)
for tool in template.tools:
    print(f"Tool: {tool.tool.tool_name}")
    print(f"  Quantity: {tool.quantity_required}")

# Get action set attachments (loaded automatically)
for attachment in template.action_set_attachments:
    print(f"Attachment: {attachment.attachment.filename}")
```

## Loading Action Attachments

Action attachments are NOT loaded by default (to save memory/queries).
Call the method when you need them:

```python
# Load action attachments
action_attachments = template.get_action_attachments()

for attachment in action_attachments:
    print(f"Action Attachment: {attachment.attachment.filename}")
    print(f"  For Action: {attachment.template_action_item.action_name}")

# Force reload from database
action_attachments = template.get_action_attachments(force_reload=True)
```

## Grouping by Action

```python
# Get part demands grouped by action
part_demands_by_action = template.get_part_demands_by_action()
for action_id, demands in part_demands_by_action.items():
    print(f"Action {action_id}:")
    for demand in demands:
        print(f"  - {demand.part.part_name}: {demand.quantity_required}")

# Get tools grouped by action
tools_by_action = template.get_tools_by_action()
for action_id, tools in tools_by_action.items():
    print(f"Action {action_id}:")
    for tool in tools:
        print(f"  - {tool.tool.tool_name}: {tool.quantity_required}")
```

## Statistics

```python
# Access statistics
print(f"Total Actions: {template.total_action_items}")
print(f"Required Actions: {template.required_action_items}")
print(f"Optional Actions: {template.optional_action_items}")

print(f"Total Part Demands: {template.total_part_demands}")
print(f"Required Part Demands: {template.required_part_demands}")

print(f"Total Tools: {template.total_tools}")

print(f"Total Estimated Duration: {template.total_estimated_duration} hours")
print(f"Total Estimated Cost: ${template.total_estimated_cost:.2f}")
```

## Export to Dictionary

```python
# Convert to dictionary (useful for JSON/API responses)
data = template.to_dict()

# Includes:
# - Template action set info
# - All action items
# - All part demands
# - All tools
# - All action set attachments
# - Statistics
```

## Human-Readable Summary

```python
# Get a formatted summary
print(template.summary())

# Output:
# Template: Engine Oil Change (Rev 1.0)
# Description: Regular engine oil change procedure
# 
# Action Items: 5 (4 required, 1 optional)
# Part Demands: 3 (3 required)
# Tools: 2
# Attachments: 1
# 
# Estimated Duration: 2.5 hours
# Estimated Parts Cost: $45.00
# 
# ⚠️  Safety Review Required
```

## Batch Operations

```python
# Get all templates
all_templates = TemplateMaintenanceEvent.get_all()

# Get only active templates
active_templates = TemplateMaintenanceEvent.get_active()

# Process multiple templates
for template in active_templates:
    print(f"{template.task_name}: {template.total_action_items} actions")
```

## Refresh Data

```python
# Refresh from database (clears cache)
template.refresh()
```

## Comparison with Direct Queries

### Before (manual queries):
```python
template_set = TemplateActionSet.query.get(1)
action_items = TemplateActionItem.query.filter_by(
    template_action_set_id=template_set.id
).order_by(TemplateActionItem.sequence_order).all()

part_demands = []
for action_item in action_items:
    demands = TemplatePartDemand.query.filter_by(
        template_action_item_id=action_item.id
    ).all()
    part_demands.extend(demands)

# ... and so on ...
```

### After (using TemplateMaintenanceEvent):
```python
template = TemplateMaintenanceEvent.from_id(1)
action_items = template.action_items
part_demands = template.part_demands
tools = template.tools
```

Much cleaner and easier to use!


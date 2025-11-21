# Maintenance System Data Model Documentation

## Overview

The maintenance system is designed to manage equipment maintenance through a template-based approach. It allows users to create reusable maintenance templates and then generate actual maintenance events from those templates. The system tracks the entire maintenance lifecycle from planning to completion.

## Core Concepts

### 1. Maintenance Plans
A **Maintenance Plan** is a high-level strategy for maintaining a specific type of equipment. It defines:
- What type of asset it applies to (e.g., "Trucks", "Forklifts")
- What model of equipment it covers (optional)
- How often maintenance should occur (time-based, meter-based, or condition-based)
- The frequency value (e.g., every 30 days, every 1000 hours)

### 2. Template Action Sets
A **Template Action Set** is a collection of maintenance tasks that can be performed together. Think of it as a "maintenance checklist" that includes:
- A name and description of the maintenance work
- Estimated duration and labor requirements
- Safety requirements
- Cost estimates for parts and labor

### 3. Template Action Items
A **Template Action Item** is an individual task within a maintenance action set. Each item represents a specific step in the maintenance process, such as:
- "Check oil level"
- "Replace air filter"
- "Inspect brake pads"
- "Test safety systems"

### 4. Maintenance Event Sets
A **Maintenance Event Set** is an actual instance of maintenance work being performed. It's created from a template action set and includes:
- The specific asset being maintained
- When the maintenance is scheduled
- Current status (Planned, In Progress, Completed, Cancelled)
- Actual start and completion dates
- Notes and completion details

### 5. Actions
An **Action** is an individual task being performed during maintenance. It's created from a template action item and tracks:
- When the task was started and completed
- Actual time spent on the task
- Completion notes
- Any issues encountered

## Data Relationships

### Template Hierarchy
```
Maintenance Plan
    ↓ (contains)
Template Action Set
    ↓ (contains)
Template Action Item
    ↓ (references)
Template Part Demand, Template Action Tool, Template Action Attachment
```

### Execution Hierarchy
```
Maintenance Event Set (created from Template Action Set)
    ↓ (contains)
Action (created from Template Action Item)
    ↓ (can have)
Part Demand (created from Template Part Demand)
```

### Asset Relationships
```
Asset Type
    ↓ (categorized by)
Asset
    ↓ (has maintenance)
Maintenance Event Set
```

## Key Entities Explained

### User
- **Purpose**: Represents people who use the system
- **Key Fields**: Username, email, password, role permissions
- **Relationships**: Creates all maintenance plans, templates, and events

### Asset
- **Purpose**: Represents physical equipment that needs maintenance
- **Key Fields**: Name, serial number, location, make/model, meter readings
- **Relationships**: Belongs to an asset type and make/model, has maintenance events

### Asset Type
- **Purpose**: Categorizes assets (e.g., "Truck", "Forklift", "Generator")
- **Key Fields**: Name, description
- **Relationships**: Assets belong to asset types, maintenance plans target asset types

### Make Model
- **Purpose**: Represents specific makes and models of equipment
- **Key Fields**: Make, model, asset type
- **Relationships**: Assets belong to make/models, maintenance plans can target specific models

### Maintenance Plan
- **Purpose**: Defines maintenance strategy for equipment types
- **Key Fields**: Name, description, asset type, model, frequency settings
- **Relationships**: Contains template action sets, creates maintenance events

### Template Action Set
- **Purpose**: Reusable collection of maintenance tasks
- **Key Fields**: Task name, description, estimated duration, labor requirements
- **Relationships**: Belongs to maintenance plan, contains template action items

### Template Action Item
- **Purpose**: Individual maintenance task within a set
- **Key Fields**: Action name, description, estimated duration, instructions
- **Relationships**: Belongs to template action set, has part demands and tools

### Template Part Demand
- **Purpose**: Defines parts needed for a maintenance task
- **Key Fields**: Part reference, quantity required, optional flag
- **Relationships**: Belongs to template action item, references part

### Template Action Tool
- **Purpose**: Defines tools needed for a maintenance task
- **Key Fields**: Tool reference, required flag, quantity needed
- **Relationships**: Belongs to template action item, references tool

### Template Action Attachment
- **Purpose**: Links documentation to maintenance tasks
- **Key Fields**: Attachment reference, type, sequence order
- **Relationships**: Belongs to template action item, references attachment

### Maintenance Event Set
- **Purpose**: Actual maintenance work being performed
- **Key Fields**: Asset, scheduled date, status, actual dates, completion notes
- **Relationships**: Created from template action set, contains actions, belongs to asset

### Action
- **Purpose**: Individual task being performed during maintenance
- **Key Fields**: Start/end times, actual duration, completion notes
- **Relationships**: Created from template action item, belongs to maintenance event set

### Part
- **Purpose**: Physical parts used in maintenance
- **Key Fields**: Part number, name, cost, stock levels, supplier
- **Relationships**: Referenced by template part demands and part demands

### Tool
- **Purpose**: Tools used in maintenance work
- **Key Fields**: Tool name, type, location, calibration dates, status
- **Relationships**: Referenced by template action tools, assigned to users

### Part Demand
- **Purpose**: Actual part request for maintenance
- **Key Fields**: Part, quantity, status, approval info
- **Relationships**: Created from template part demand, belongs to action or maintenance event set

### Event
- **Purpose**: System-wide event tracking
- **Key Fields**: Event type, description, timestamp, user, asset
- **Relationships**: Created for maintenance events, has comments and attachments

### Comment
- **Purpose**: User communication about events
- **Key Fields**: Content, author, timestamp
- **Relationships**: Belongs to event, can have attachments

### Attachment
- **Purpose**: File storage for documentation
- **Key Fields**: Filename, file path, size, type
- **Relationships**: Referenced by template action attachments, comment attachments

## Virtual Classes (Abstract Base Classes)

### UserCreatedBase
- **Purpose**: Provides audit trail for all user-created entities
- **Key Fields**: Created/updated timestamps, user references
- **Usage**: Inherited by all user-created entities

### VirtualActionSet
- **Purpose**: Common interface for action sets (templates and actual events)
- **Key Fields**: Task name, description, duration, labor requirements
- **Usage**: Inherited by TemplateActions and MaintenanceEvent

### VirtualActionItem
- **Purpose**: Common interface for action items (templates and actual actions)
- **Key Fields**: Action name, description, duration, notes
- **Usage**: Inherited by ProtoActionItems and Action

### VirtualPartDemand
- **Purpose**: Common interface for part demands (templates and actual demands)
- **Key Fields**: Part reference, quantity, notes
- **Usage**: Inherited by TemplatePartDemand and PartDemand

### EventDetailVirtual
- **Purpose**: Common interface for event detail records
- **Key Fields**: Event reference, global detail ID, asset reference
- **Usage**: Inherited by MaintenanceEvent

## Workflow Process

### 1. Planning Phase
1. User creates a Maintenance Plan for a specific asset type
2. User creates Template Action Sets within the plan
3. User creates Template Action Items within each action set
4. User adds Template Part Demands, Template Action Tools, and Template Action Attachments to action items

### 2. Execution Phase
1. System creates Maintenance Event Sets from templates based on asset meters or schedules
2. System creates Actions from template action items
3. System creates Part Demands from template part demands
4. Users perform the maintenance tasks and update action statuses
5. System tracks completion and generates events and comments

### 3. Completion Phase
1. Users mark actions as completed
2. System calculates actual costs and durations
3. Maintenance event set is marked as completed
4. System generates completion events and documentation

## Key Benefits

1. **Reusability**: Templates can be used multiple times for similar equipment
2. **Consistency**: Standardized maintenance procedures across similar equipment
3. **Tracking**: Complete audit trail of all maintenance activities
4. **Planning**: Automated creation of maintenance events based on schedules
5. **Documentation**: Integrated file attachments and comments
6. **Cost Control**: Tracking of estimated vs. actual costs and time
7. **Safety**: Built-in safety requirements and review processes

## Data Integrity

- All entities inherit from UserCreatedBase for audit trails
- Foreign key relationships ensure data consistency
- Virtual classes provide common interfaces for similar entities
- Event system provides system-wide activity tracking
- Status fields track the lifecycle of maintenance activities

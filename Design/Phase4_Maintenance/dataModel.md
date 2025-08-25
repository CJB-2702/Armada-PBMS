# Phase 4: Maintenance Data Model

## Overview
The Maintenance module manages scheduled and reactive maintenance activities for assets. It provides a comprehensive system for creating maintenance plans, scheduling maintenance events, tracking actions, managing parts and tools, and maintaining detailed records of all maintenance activities.

## Core Entities

### 1. Maintenance Plans
**Purpose**: Define scheduled maintenance strategies for asset types and models

**Key Attributes**:
- Plan ID (Primary Key)
- Plan Name
- Description
- Asset Type ID (Foreign Key)
- Model ID (Foreign Key, optional)
- Created By (User ID)
- Created Date
- Status (Active/Inactive)
- Frequency Type (Time-based, Meter-based, Condition-based)
- Frequency Value
- Last Updated

**Relationships**:
- Belongs to one Asset Type
- Can optionally be associated with a specific Model
- Has multiple Template Action Set Headers
- Creates Maintenance Events

### 2. Maintenance Events
**Purpose**: Individual maintenance activities triggered by plans or manual creation

**Key Attributes**:
- Event ID (Primary Key)
- Maintenance Plan ID (Foreign Key, optional)
- Asset ID (Foreign Key)
- Event Type (Scheduled, Reactive, Emergency)
- Status (Planned, In Progress, Completed, Cancelled)
- Priority (Low, Medium, High, Critical)
- Scheduled Date
- Actual Start Date
- Actual End Date
- Description
- Created By (User ID)
- Created Date
- Completed By (User ID)
- Completion Notes

**Relationships**:
- Inherits from Event (Core module)
- Belongs to one Asset
- Can be created from a Maintenance Plan
- Has one Template Action Set Header
- Has multiple Actions
- Has multiple Comments
- Has multiple Attachments

### 3. Template Action Set Headers
**Purpose**: Define the structure and metadata for maintenance action sets

**Key Attributes**:
- Template Action Set Header ID (Primary Key)
- Header Name
- Description
- Estimated Duration
- Required Skills
- Safety Requirements
- Created By (User ID)
- Created Date
- Status (Active/Inactive)

**Relationships**:
- Belongs to one Maintenance Plan
- Has multiple Template Action Sets
- Has multiple Template Action Items

### 4. Template Action Sets
**Purpose**: Group related action items within a maintenance activity

**Key Attributes**:
- Template Action Set ID (Primary Key)
- Template Action Set Header ID (Foreign Key)
- Set Name
- Description
- Sequence Order
- Estimated Duration
- Required Tools
- Required Parts

**Relationships**:
- Belongs to one Template Action Set Header
- Has multiple Template Action Items

### 5. Template Action Items
**Purpose**: Individual tasks within a maintenance action set

**Key Attributes**:
- Template Action Item ID (Primary Key)
- Template Action Set ID (Foreign Key)
- Item Name
- Description
- Step Instructions
- Estimated Duration
- Required Skills
- Safety Notes
- Sequence Order
- Is Required (Boolean)
- Created By (User ID)
- Created Date

**Relationships**:
- Belongs to one Template Action Set
- Can have multiple Template Action Attachments
- Can have multiple Template Part Demands

### 6. Actions
**Purpose**: Actual execution of maintenance tasks

**Key Attributes**:
- Action ID (Primary Key)
- Maintenance Event ID (Foreign Key)
- Template Action Item ID (Foreign Key)
- Action Name
- Description
- Status (Not Started, In Progress, Completed, Skipped)
- Assigned To (User ID)
- Scheduled Start Time
- Actual Start Time
- Actual End Time
- Duration
- Notes
- Completion Notes
- Created Date
- Updated Date

**Relationships**:
- Belongs to one Maintenance Event
- Based on one Template Action Item
- Can have multiple Part Demands
- Can have multiple Tool Assignments

## Supply Management Entities

### 7. Parts
**Purpose**: Inventory items used in maintenance activities

**Key Attributes**:
- Part ID (Primary Key)
- Part Number
- Part Name
- Description
- Category
- Manufacturer
- Supplier
- Unit Cost
- Current Stock Level
- Minimum Stock Level
- Maximum Stock Level
- Unit of Measure
- Location
- Status (Active/Inactive)
- Created Date
- Last Updated

**Relationships**:
- Has multiple Part Demands
- Referenced by Template Part Demands

### 8. Tools
**Purpose**: Equipment and tools required for maintenance tasks

**Key Attributes**:
- Tool ID (Primary Key)
- Tool Name
- Description
- Tool Type
- Manufacturer
- Model Number
- Serial Number
- Location
- Status (Available, In Use, Out for Repair, Retired)
- Last Calibration Date
- Next Calibration Date
- Assigned To (User ID, optional)
- Created Date
- Last Updated

**Relationships**:
- Can be assigned to multiple Actions
- Referenced by Template Action Sets

### 9. Part Demands
**Purpose**: Track parts required and consumed during maintenance

**Key Attributes**:
- Part Demand ID (Primary Key)
- Action ID (Foreign Key)
- Part ID (Foreign Key)
- Template Part Demand ID (Foreign Key, optional)
- Quantity Required
- Quantity Used
- Unit Cost
- Total Cost
- Status (Requested, Approved, Issued, Consumed)
- Requested By (User ID)
- Requested Date
- Issued By (User ID)
- Issued Date
- Notes

**Relationships**:
- Belongs to one Action
- References one Part
- Can be based on one Template Part Demand

### 10. Template Part Demands
**Purpose**: Predefined part requirements for action items

**Key Attributes**:
- Template Part Demand ID (Primary Key)
- Template Action Item ID (Foreign Key)
- Part ID (Foreign Key)
- Quantity Required
- Is Optional (Boolean)
- Notes
- Created Date

**Relationships**:
- Belongs to one Template Action Item
- References one Part
- Can create multiple Part Demands

## Supporting Entities

### 11. Template Action Attachments
**Purpose**: Reference documents and files for action items

**Key Attributes**:
- Template Action Attachment ID (Primary Key)
- Template Action Item ID (Foreign Key)
- Attachment ID (Foreign Key)
- Attachment Type (Manual, Diagram, Photo, Video, Document)
- Description
- Sequence Order
- Is Required (Boolean)
- Created Date

**Relationships**:
- Belongs to one Template Action Item
- References one Attachment (Core module)

### 12. Comments
**Purpose**: Communication and notes for maintenance events

**Key Attributes**:
- Comment ID (Primary Key)
- Maintenance Event ID (Foreign Key)
- User ID (Foreign Key)
- Comment Text
- Comment Type (General, Issue, Resolution, Note)
- Created Date
- Updated Date

**Relationships**:
- Belongs to one Maintenance Event
- Created by one User
- Can have multiple Comment Attachments

### 13. Comment Attachments
**Purpose**: Files attached to comments

**Key Attributes**:
- Comment Attachment ID (Primary Key)
- Comment ID (Foreign Key)
- Attachment ID (Foreign Key)
- Created Date

**Relationships**:
- Belongs to one Comment
- References one Attachment (Core module)

## Virtual Entities

### 14. Virtual Action Items
**Purpose**: Dynamic action items created from templates

**Key Attributes**:
- Virtual Action Item ID (Primary Key)
- Template Action Item ID (Foreign Key)
- Maintenance Event ID (Foreign Key)
- Status
- Assigned To
- Progress

**Relationships**:
- Based on one Template Action Item
- Belongs to one Maintenance Event

### 15. Virtual Part Demands
**Purpose**: Dynamic part demands created from templates

**Key Attributes**:
- Virtual Part Demand ID (Primary Key)
- Template Part Demand ID (Foreign Key)
- Action ID (Foreign Key)
- Status
- Quantity Required

**Relationships**:
- Based on one Template Part Demand
- Belongs to one Action

### 16. Virtual Action Set Headers
**Purpose**: Dynamic action set headers created from templates

**Key Attributes**:
- Virtual Action Set Header ID (Primary Key)
- Template Action Set Header ID (Foreign Key)
- Maintenance Event ID (Foreign Key)
- Status
- Progress

**Relationships**:
- Based on one Template Action Set Header
- Belongs to one Maintenance Event

### 17. Virtual Attachment References
**Purpose**: Dynamic attachment references for virtual entities

**Key Attributes**:
- Virtual Attachment Reference ID (Primary Key)
- Template Action Attachment ID (Foreign Key)
- Virtual Action Item ID (Foreign Key)
- Status

**Relationships**:
- Based on one Template Action Attachment
- Belongs to one Virtual Action Item

## Key Business Rules

### 1. Maintenance Plan Execution
- When a maintenance plan triggers (based on time, meter reading, or condition), it creates a maintenance event in "Planned" status
- The maintenance event inherits the template action set header from the plan
- Virtual action items are created from the template action items

### 2. Action Assignment
- When a maintenance event is assigned to a template action set header, it automatically creates actions with links to action items from the template action set
- Actions can be assigned to specific users based on required skills

### 3. Part Demand Management
- When an action is assigned to a template action item, it automatically inserts part demands from the template part demands
- Part demands track both required and actual quantities used

### 4. Tool Management
- Tools can be assigned to actions based on requirements defined in template action sets
- Tool availability and calibration status are tracked

### 5. Status Progression
- Maintenance events progress through: Planned → In Progress → Completed
- Actions progress through: Not Started → In Progress → Completed/Skipped
- Part demands progress through: Requested → Approved → Issued → Consumed

## Integration Points

### Core Module Integration
- Maintenance Events inherit from the core Event entity
- Users create and manage maintenance activities
- Assets are the primary subjects of maintenance
- Attachments are shared across the system

### Supply Module Integration
- Parts and Tools are managed in the supply module
- Part demands create supply requests
- Tool assignments track tool usage

### Asset Management Integration
- Maintenance plans are associated with asset types and models
- Maintenance events are linked to specific assets
- Asset meter readings can trigger maintenance events

## Data Flow Summary

1. **Planning Phase**: Maintenance plans are created for asset types/models
2. **Triggering**: Plans create maintenance events based on schedules or conditions
3. **Execution**: Events create actions from templates, assign resources, and track progress
4. **Supply**: Part demands and tool assignments are managed
5. **Completion**: Events and actions are marked complete with documentation
6. **Analysis**: Data is available for maintenance history and optimization

This data model provides a comprehensive foundation for managing maintenance activities while maintaining flexibility through template-based approaches and virtual entities.

# Armada PBMS Event Model

## Core Models

### Event
- Primary key: `event_row_id` (Integer)
- Common Fields: Yes
- Specific Fields:
  - `event_type_row_id` (Integer, Foreign Key to EventType)
  - `major_event_type` (String) - Primary category
  - `minor_event_type` (String) - Specific event subtype
  - `minor_event_id` (Integer, optional) - ID of the specific event record
  - `title` (String)
  - `description` (Text)
  - `asset_row_id` (Integer, Foreign Key to Asset)
  - `related_asset_row_id` (Integer, Foreign Key to Asset, optional)
  - `user_row_id` (Integer, Foreign Key to User, optional)
  - `start` (DateTime, required)
  - `end` (DateTime, optional)
  - `scheduled_start` (DateTime, optional)
  - `scheduled_end` (DateTime, optional)
  - `priority` (Integer) - 1-5 scale
  - `status` (String) - pending, in_progress, completed, cancelled

### EventType
- Primary key: `type_row_id` (Integer)
- Common Fields: Yes
- Specific Fields:
  - `major_type` (String) - Primary category
  - `minor_type` (String) - Specific event subtype
  - `description` (Text)
  - `default_priority` (Integer) - 1-5 scale
  - `table_name` (String) - Table where minor event details are stored
  - `notification_template` (Text) - optional template for notifications

### EventComment
- Primary key: `comment_row_id` (Integer)
- Common Fields: Yes
- Specific Fields:
  - `event_row_id` (Integer, Foreign Key to Event)
  - `comment_text` (Text)
  - `is_system_generated` (Boolean)
  - `context` (String, optional)
  - `context_id` (Integer, optional)

### EventAttachment
- Primary key: `attachment_row_id` (Integer)
- Common Fields: Yes
- Specific Fields:
  - `event_row_id` (Integer, Foreign Key to Event)
  - `comment_row_id` (Integer, Foreign Key to EventComment)
  - `file_name` (String)
  - `file_type` (String)
  - `file_size` (Integer)
  - `is_filesystem_storage` (Boolean)
  - `storage_path` (String) - File path if is_filesystem_storage is true
  - `byte_content` (Bytea) - File content if is_filesystem_storage is false, max 10MB
  - `description` (Text, optional)

### FormType
- Primary key: `form_type_row_id` (Integer)
- Common Fields: Yes
- Specific Fields:
  - `name` (String)
  - `version` (String)
  - `is_active` (Boolean)
  - `description` (Text)
  - `form_structure` (JSON)

### FormTypeEventMapping
- Primary key: `mapping_row_id` (Integer)
- Common Fields: Yes
- Specific Fields:
  - `form_type_row_id` (Integer, Foreign Key to FormType)
  - `major_event_type` (String)
  - `minor_event_type` (String)
  - `is_default` (Boolean)
  - `priority` (Integer)

## Event Categories

### 1. Status Events
- Major Type: "status"
- Minor Types:
  - `change` - General status change
  - `availability` - Availability status change
  - `condition` - Condition status change
- Common Fields: previous_value, new_value, change_reason

### 2. Maintenance Events
- Major Type: "maintenance"
- Minor Types:
  - `scheduled` - Scheduled maintenance
  - `unscheduled` - Unscheduled maintenance
  - `inspection` - Inspection event
- Common Fields: maintenance_type, parts_list, instructions, findings

### 3. Usage Events
- Major Type: "usage"
- Minor Types:
  - `dispatch` - Asset dispatched to external location
  - `local` - Asset used within facility
  - `update` - Usage status update
- Common Fields:
  - usage_type
  - location
  - assigned_to
  - assigned_by
  - notes
  - condition
  - return_notes
  - return_condition

### 4. Documentation Events
- Major Type: "documentation"
- Minor Types:
  - `add` - Document added
  - `update` - Document updated
  - `delete` - Document deleted
- Common Fields: document_type, file_reference, version

### 5. System Events
- Major Type: "system"
- Minor Types:
  - `create` - Record creation
  - `modify` - Record modification
  - `delete` - Record deletion
  - `archive` - Record archive
  - `restore` - Record restore
- Common Fields: entity_type, entity_id, change_summary

## Asset Type Integration

### Asset Type References
- Events can be associated with any asset type:
  - Vehicles
  - Locations
  - Equipment
  - Dive Equipment
- Each event type can specify which asset types it applies to
- Asset type-specific fields are stored in the minor event details table

### Asset Type Validation
- Events must validate against asset type requirements
- Asset type-specific forms are available based on event type
- Asset type determines available event types
- Asset type influences event display and processing

## Model Rules

### Event Rules
1. **Creation Rules**
   - Every event must have an event type
   - Events can have multiple details
   - Initial comment required for event creation
   - Asset association required
   - Start time required

2. **Status Rules**
   - Status must be one of: pending, in_progress, completed, cancelled
   - Priority must be 1-5
   - End time must be after start time
   - Scheduled times must be valid

3. **Relationship Rules**
   - Events must be linked to at least one asset
   - Related assets must exist
   - Users must exist if specified
   - Event types must exist

### Comment Rules
1. **Creation Rules**
   - Comments can only be added to events
   - Comments must have text content
   - System-generated comments must specify context
   - Context ID required if context specified

2. **System Generation Rules**
   - System generates comments for:
     - Event creation
     - Status changes
     - Detail updates
     - Priority changes
     - Assignment changes

### Attachment Rules
1. **Storage Rules**
   - Files ≤ 10MB stored in database
   - Files > 10MB stored in filesystem
   - Storage location indicated by is_filesystem_storage
   - Only one storage method used per attachment

2. **Linkage Rules**
   - Attachments must link to both event and comment
   - File information must be complete
   - File size must be recorded
   - Storage path must be valid for filesystem storage

### Form Rules
1. **Form Type Rules**
   - Form types must have unique name
   - Version must follow semantic versioning
   - Form structure must be valid JSON
   - At least one mapping required

2. **Mapping Rules**
   - Each mapping must reference valid form type
   - Each mapping must reference valid event type
   - Only one default form per event type
   - Priority determines form selection order

## Data Examples

### Event Detail Structure
```json
{
  "timing": {
    "scheduled_start": "2024-03-20T10:00:00Z",
    "scheduled_end": "2024-03-20T11:00:00Z",
    "actual_start": "2024-03-20T10:05:00Z",
    "actual_end": "2024-03-20T11:15:00Z",
    "duration": 70
  },
  "impact": {
    "severity": "high",
    "priority": 1,
    "business_impact": "critical",
    "response_time": 30
  },
  "resources": {
    "personnel": ["technician_id_1", "supervisor_id_1"],
    "materials": ["part_id_1", "part_id_2"],
    "cost": 1500.00,
    "labor_hours": 2.5
  },
  "relationships": {
    "related_assets": ["asset_id_1", "asset_id_2"],
    "prerequisites": ["event_id_1"],
    "dependencies": ["event_id_2"]
  },
  "outcomes": {
    "result": "completed",
    "findings": "Component replaced successfully",
    "follow_up_required": true,
    "next_action": "Schedule follow-up inspection"
  }
}
```

### Form Structure Example
```json
{
  "fields": [
    {
      "name": "driver_info",
      "type": "object",
      "required": true,
      "fields": [
        {"name": "name", "type": "string", "required": true},
        {"name": "id", "type": "string", "required": true},
        {"name": "contact", "type": "string", "required": true}
      ]
    },
    {
      "name": "purpose",
      "type": "string",
      "required": true
    },
    {
      "name": "expected_return",
      "type": "datetime",
      "required": true
    },
    {
      "name": "condition",
      "type": "string",
      "required": true,
      "options": ["excellent", "good", "fair", "poor"]
    }
  ]
}
``` 
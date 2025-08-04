# Core Data Model

## Entity Relationship Diagram

```mermaid
erDiagram
    User {
        int id PK
        string username
        string email
        string password_hash
        boolean is_active
        boolean is_admin
        boolean is_system
        datetime created_at
        datetime updated_at
    }
    
    Asset {
        int id PK
        string name
        string serial_number
        string status
        int major_location_id FK
        int make_model_id FK
        float meter1
        float meter2
        float meter3
        float meter4
        json tags
        datetime created_at
        datetime updated_at
    }
    
    AssetType {
        int id PK
        string name
        text description
        string category
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    
    MakeModel {
        int id PK
        string make
        string model
        int year
        string revision
        text description
        boolean is_active
        int asset_type_id FK
        string meter1_unit
        string meter2_unit
        string meter3_unit
        string meter4_unit
        datetime created_at
        datetime updated_at
    }
    
    MajorLocation {
        int id PK
        string name
        text description
        text address
        boolean is_active
        datetime created_at
        datetime updated_at
    }
    
    Event {
        int id PK
        string event_type
        text description
        datetime timestamp
        int user_id FK
        int asset_id FK
        int major_location_id FK
        datetime created_at
        datetime updated_at
    }
    
    Comment {
        int id PK
        text content
        int event_id FK
        boolean is_private
        boolean is_edited
        datetime edited_at
        int edited_by_id FK
        datetime created_at
        datetime updated_at
    }
    
    Attachment {
        int id PK
        string filename
        int file_size
        string mime_type
        text description
        json tags
        string storage_type
        string file_path
        blob file_data
        datetime created_at
        datetime updated_at
    }
    
    CommentAttachment {
        int id PK
        int comment_id FK
        int attachment_id FK
        int display_order
        string caption
        datetime created_at
        datetime updated_at
    }
    
    Asset ||--o{ MajorLocation : "located_at"
    Asset ||--o{ MakeModel : "has_type"
    MakeModel ||--o{ AssetType : "belongs_to"
    
    Event ||--o{ User : "triggered_by"
    Event ||--o{ Asset : "relates_to"
    Event ||--o{ MajorLocation : "occurs_at"
    
    Comment ||--o{ Event : "attached_to"
    Comment ||--o{ User : "edited_by"
    
    CommentAttachment ||--o{ Comment : "links_to"
    CommentAttachment ||--o{ Attachment : "references"
```

## Key Relationships

### Core Asset Relationships
- **Asset** → **MajorLocation**: Each asset is located at a major location
- **Asset** → **MakeModel**: Each asset has a specific make/model
- **MakeModel** → **AssetType**: Each make/model belongs to an asset type category

### Event System
- **Event** → **User**: Events are triggered by users
- **Event** → **Asset**: Events relate to specific assets
- **Event** → **MajorLocation**: Events occur at specific locations

### Communication System
- **Comment** → **Event**: Comments are attached to events
- **Comment** → **User**: Comments can be edited by users
- **CommentAttachment** → **Comment**: Attachments are linked to comments
- **CommentAttachment** → **Attachment**: Junction table for comment-attachment relationships

## Notes
- All entities inherit audit fields (`created_at`, `updated_at`) from `UserCreatedBase`
- The `created_by` and `updated_by` relationships are excluded as requested
- Foreign keys are clearly marked with (FK) suffix
- Primary keys are marked with (PK) suffix 
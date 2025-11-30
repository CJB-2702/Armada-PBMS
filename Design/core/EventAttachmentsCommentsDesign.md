# Event Attachments and Comments - Design Document

## Overview
Events support a rich commenting system with file attachments. Comments can be created by users or generated automatically by the system. Attachments are always linked to comments (never directly to events), enabling discussion and context around files.

## Architecture

### Data Model
- **Event** → has many **Comments**
- **Comment** → has many **CommentAttachment** (via `VirtualAttachmentReference`)
- **CommentAttachment** → references one **Attachment**
- **Attachment** → stores file data (dual storage: database for ≤1MB, filesystem for >1MB)

### Key Components
- **Data Layer**: `app/data/core/event_info/` - Comment, Attachment, CommentAttachment models
- **Business Layer**: `app/buisness/core/event_context.py` - EventContext for operations
- **Service Layer**: `app/services/core/event_service.py` - Presentation data helpers
- **Presentation Layer**: `app/presentation/routes/core/events/` - comments.py, attachments.py

## Comment Behavior

### Creation
- **Human Comments**: Created via UI with `is_human_made=True`; always require `created_by_id` (user attribution)
- **Automated Comments**: System-generated (e.g., state changes) with `is_human_made=False`; must still set `created_by_id` to triggering user
- **Replies**: Comments can reply to other comments via `replied_to_comment_id`; reply chains preserved
- **Content**: Text content required (unless files provided, then auto-generates "Added N attachment(s)")

### Visibility & State
- **Visible**: `user_viewable=None` (default) - shown in UI
- **Deleted**: `user_viewable='deleted'` - soft deleted, hidden from users
- **Previous Edit**: `user_viewable='edit'` - hidden previous version after edit

### Edit Behavior
- **Immutable Editing**: Edits create a new Comment linked via `previous_comment_id`
- **Original Hidden**: Original comment marked `user_viewable='edit'` (hidden from users)
- **Attachment Migration**: All attachments from original comment move to new comment
- **History Chain**: `EventContext.get_comment_edit_history()` traverses `previous_comment_id` chain chronologically
- **Reply Preservation**: Reply relationships preserved across edits

### Deletion
- **Soft Delete**: Sets `user_viewable='deleted'` (comment and attachments remain in database)
- **Ownership Required**: Only comment creator can delete
- **Attachment Handling**: Attachments remain linked but comment is hidden

### Filtering & Ordering
- **Default View**: Shows all comments (human + automated) where `user_viewable=None`, ordered chronologically (oldest first)
- **Human-Only Filter**: `EventService.get_human_comments()` filters to `is_human_made=True` with visibility filters
- **Hidden Items**: Deleted comments (`user_viewable='deleted'`) and previous edits (`user_viewable='edit'`) excluded from standard views

## Attachment Behavior

### Storage Strategy
- **Threshold**: 1MB (`Attachment.STORAGE_THRESHOLD`)
- **≤1MB**: Stored in database as BLOB (`file_data`, `storage_type='database'`)
- **>1MB**: Stored on filesystem (`file_path`, `storage_type='filesystem'`)
- **Path Structure**: `instance/large_attachments/{year}/{month:02d}/{attachment_id}_{filename}`
- **Max Size**: 100MB (`Attachment.MAX_FILE_SIZE`)

### File Handling
- **Allowed Types**: Images, documents, archives, data files, code files (defined in `Attachment.ALLOWED_EXTENSIONS`)
- **Validation**: `Attachment.is_allowed_file()` checks extension before saving
- **Security**: `secure_filename()` sanitizes filenames; size limits enforced
- **Metadata**: Stores filename, file_size, mime_type, description, tags

### Attachment Linking
- **Via Comments**: Attachments always linked through `CommentAttachment` (never directly to events)
- **Display Order**: `display_order` field controls ordering within comment
- **Captions**: Optional caption per attachment via `caption` field
- **Attachment Type**: Classification (`attachment_type`: 'Image', 'Document', 'Video')
- **Global ID**: `all_attachment_references_id` provides cross-system unique identifier

### File Operations
- **Save**: `attachment.save_file(file_data, filename)` - auto-determines storage type, creates directories if needed
- **Retrieve**: `attachment.get_file_data()` - transparently reads from database or filesystem
- **Delete**: `attachment.delete_file()` - removes file and cleans up empty directories
- **Download**: Route `/attachments/<id>/download` serves file as attachment
- **View**: Route `/attachments/<id>/view` displays in browser (for images, PDFs, text files)

## API Endpoints

### Comments (`/events/<event_id>/comments`)
- **POST**: Create comment with optional attachments and `replied_to_comment_id`
  - HTMX support: Returns updated event widget on `HX-Request`
  - Validates parent comment exists and belongs to same event
  - Prevents replying to deleted comments
- **GET `/widget`**: Get event activity widget (HTMX embeddable)
- **POST `/comments/<id>/edit`**: Edit comment (creates new version)
- **POST `/comments/<id>/delete`**: Soft delete comment
- **GET `/comments/<id>/metadata`**: Get full comment metadata as JSON

### Attachments (`/attachments/<attachment_id>`)
- **GET `/download`**: Download attachment file
- **GET `/view`**: View attachment in browser (images, PDFs, text)
- **POST `/delete`**: Delete attachment (must own attachment)
- **GET `/info`**: Get attachment metadata as JSON
- **GET `/preview`**: Get text preview (first 10 lines for text files)

## Business Logic (EventContext)

### Key Methods
- **`add_comment()`**: Creates comment with validation
- **`add_comment_with_attachments()`**: Handles file uploads, validation, storage selection, linking
- **`edit_comment()`**: Creates new comment version, migrates attachments, marks original as edit
- **`delete_comment()`**: Soft deletes via `user_viewable='deleted'`
- **`get_comment_edit_history()`**: Static method to traverse edit chain
- **`comments` property**: Returns visible comments (excludes deleted/edits), ordered chronologically
- **`attachments` property**: Returns all attachments via comments for event

### Caching
- EventContext caches comments and attachments; call `refresh()` after external changes

## Key Design Decisions

1. **Attachments via Comments**: Attachments always tied to comments, not events directly - enables discussion context
2. **Immutable Editing**: Edit creates new comment rather than modifying existing - preserves audit trail
3. **Soft Delete**: Comments and attachments preserved in database but hidden - supports audit requirements
4. **Dual Storage**: Automatic database/filesystem selection based on size - balances performance and storage
5. **User Attribution**: Even automated comments require `created_by_id` - enables proper audit trail
6. **Chronological Ordering**: Comments displayed oldest-first for conversation flow
7. **Reply Chains**: `replied_to_comment_id` enables threaded discussions

## File Organization
- **Models**: `app/data/core/event_info/comment.py`, `attachment.py`
- **Business Logic**: `app/buisness/core/event_context.py`
- **Services**: `app/services/core/event_service.py`
- **Routes**: `app/presentation/routes/core/events/comments.py`, `attachments.py`
- **Templates**: `app/presentation/templates/core/events/event_activity.html`, `comment_item.html`


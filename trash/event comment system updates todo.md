# Event Comment System Updates - TODO

## Overview

This document outlines required updates to the event activity module and EventContext to support enhanced comment functionality for the maintenance work page. These changes enable user attribution for automated comments, edit/delete capabilities, and improved comment management.

## Current State

**Location**: `app/data/core/event_info/comment.py`

**Current Model Fields:**
- `content` (Text, required)
- `event_id` (FK to events, required)
- `is_private` (Boolean, default=False)
- `is_edited` (Boolean, default=False)
- `edited_at` (DateTime, nullable)
- `edited_by_id` (FK to users, nullable)
- `is_human_made` (Boolean, default=False)

## Required Changes

### 1. User Attribution for Automated Comments

**Requirement**: Automated comments must have the user's ID as the `created_by` person (the user who triggered the state change that generated the comment).

**Implementation Notes:**
- When creating automated comments (e.g., action state changes, maintenance status changes), ensure `created_by_id` is set to the current user
- This allows proper attribution even for system-generated comments
- Review all places where automated comments are created and ensure user ID is passed

### 2. Edit Capability

**Requirement**: Comments created by the active user can be edited.

**Implementation Approach:**
- When a comment is edited, create a NEW comment linked to the previous comment
- Link the new comment to the previous comment (add `previous_comment_id` foreign key)
- Mark the previous comment as "previous edit" (add `is_previous_edit` boolean flag)
- Hide previous edits from users in the UI (filter out comments where `is_previous_edit = True`)
- Update `is_edited` flag on original comment for backward compatibility if needed

**Data Model Changes:**
- Add `previous_comment_id` (Integer, FK to comments.id, nullable=True)
- Add `is_previous_edit` (Boolean, default=False)
- Add relationship: `previous_comment` → relationship('Comment', foreign_keys=[previous_comment_id])

### 3. Delete Capability (Soft Delete)

**Requirement**: Comments created by the active user can be deleted using soft delete.

**Implementation Approach:**
- Add `deleted` flag (Boolean, default=False)
- When deleted, set `deleted = True` instead of removing from database
- Filter out deleted comments from user-facing queries
- Preserve comment for audit trail purposes

**Data Model Changes:**
- Add `deleted` (Boolean, default=False)
- Update queries to filter out deleted comments: `.filter_by(deleted=False)`

### 4. Replace is_private with user_viewable

**Requirement**: Replace `is_private` flag with `user_viewable` column with three states.

**Implementation Approach:**
- Remove `is_private` column
- Add `user_viewable` (String, nullable=True) with three possible values:
  - `null` = Yes (visible to all users, default)
  - `"deleted"` = Comment has been deleted (soft delete state)
  - `"edit"` = Comment is a previous edit (hidden from users)
- This consolidates visibility, deletion, and edit tracking into one field

**Data Model Changes:**
- Remove `is_private` column
- Add `user_viewable` (String(20), nullable=True)
- Migration: Convert existing `is_private=True` to `user_viewable="hidden"` or similar, then decide on final state values

**Alternative Consideration**: 
- If three states are not sufficient, consider keeping `deleted` as separate boolean and using `user_viewable` for visibility states only
- Review with team to determine if `null`, `"deleted"`, `"edit"` covers all use cases

### 5. EventContext Updates

**Location**: `app/buisness/core/event_context.py` (or similar)

**Required Method Updates:**
- `add_comment()`: Ensure `created_by_id` is always set (even for automated comments)
- `edit_comment()`: Create new comment, link to previous, mark previous as edit
- `delete_comment()`: Soft delete by setting `deleted = True` or `user_viewable = "deleted"`
- `get_comments()`: Filter out deleted comments and previous edits
- Review all comment-related methods for proper user attribution

### 6. Event Activity Module Updates

**Location**: Review event activity widget/module that displays comments

**Required Updates:**
- Display logic: Hide comments where `is_previous_edit = True` or `user_viewable = "edit"`
- Display logic: Hide comments where `deleted = True` or `user_viewable = "deleted"`
- Edit UI: Show edit button only for comments created by current user
- Delete UI: Show delete button only for comments created by current user
- Visual indicators: Show edited/deleted status appropriately
- Ensure automated comments show user attribution (created_by)

### 7. Edit History Workflow

**Requirement**: Users who have edited a comment should be able to view their own edit history in the edit modal.

**Implementation Approach:**
- Add method to Comment model: `get_edit_history()` - Returns all previous versions of the comment (following `previous_comment_id` chain backwards)
- The method should return a list of all previous versions, ordered chronologically (oldest first)
- Include the original comment in the history chain
- Update edit route (`/comments/<comment_id>/edit`) to return edit history data when requested
- Add edit history section to the edit modal:
  - Collapsible/expandable section showing "Edit History" 
  - Display each previous version with:
    - Version number (e.g., "Original", "Edit 1", "Edit 2")
    - Content preview
    - Timestamp (created_at)
    - User who created that version (created_by)
  - Only visible to the comment creator (same user who can edit)
  - Styled as a timeline or list showing the progression of edits

**Data Model Support:**
- Use `previous_comment_id` relationship to traverse the edit chain backwards
- Query all comments in the chain where `previous_comment_id` links them together
- Include comments where `user_viewable = "edit"` in the history (these are hidden from main view but visible in history)

**UI/UX Considerations:**
- Edit history section should be collapsible (default collapsed to keep modal clean)
- Show count of edits in the header (e.g., "Edit History (3 versions)")
- Each version should show a clear diff or side-by-side comparison if possible
- Use visual indicators (timeline, version badges) to show progression
- Make it clear which version is the current one being edited

## Implementation Notes

### Migration Strategy
1. Add new columns (`previous_comment_id`, `is_previous_edit`, `deleted`, `user_viewable`)
2. Migrate existing data (set defaults, convert `is_private` to `user_viewable`)
3. Update application code to use new fields
4. Remove old `is_private` column in subsequent migration
5. Test thoroughly to ensure no data loss

### Backward Compatibility
- Keep `is_edited`, `edited_at`, `edited_by_id` fields for backward compatibility if needed
- Or migrate to new edit tracking system (previous_comment_id approach)
- Review existing code that uses `is_private` and update to use `user_viewable`

### Testing Considerations
- Test automated comment creation with user attribution
- Test edit flow (create new comment, link to previous)
- Test soft delete (comment hidden but preserved)
- Test filtering of previous edits and deleted comments
- Test permission checks (only creator can edit/delete)
- Test migration of existing data

## Related Files to Review

- `app/data/core/event_info/comment.py` - Data model
- `app/buisness/core/event_context.py` - Business logic
- Event activity widget/templates - Display logic
- Any routes/services that create or manage comments

## Questions to Resolve

1. Should `user_viewable` have exactly three states (null, "deleted", "edit") or more?
just three
2. Should we keep `is_edited`, `edited_at`, `edited_by_id` for backward compatibility, or fully migrate to previous_comment_id approach?
fully migrate
3. What should happen to existing comments with `is_private = True` during migration?
just delete the column no actions

4. Should there be an admin view that can see deleted comments and previous edits for audit purposes?
not now




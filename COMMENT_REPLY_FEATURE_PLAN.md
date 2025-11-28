# Comment Reply Feature - Implementation Plan

## Document Review - Logical Errors and Workflow Inconsistencies

### Issues Found in `event comment system updates todo.md`:

1. **Inconsistent Field Usage (Section 4)**: 
   - The document proposes replacing `is_private` with `user_viewable` that has three states: `null`, `"deleted"`, `"edit"`
   - However, Section 2 (Edit Capability) mentions adding `is_previous_edit` boolean flag
   - **Issue**: These two approaches conflict - either use `user_viewable="edit"` OR use `is_previous_edit=True`, not both
   - **Resolution**: Use `user_viewable` field only, remove `is_previous_edit` from the plan

2. **Edit Workflow Inconsistency (Section 2)**:
   - Document says to "create a NEW comment linked to the previous comment" for edits
   - But Section 4 says `user_viewable="edit"` should hide previous edits
   - **Issue**: If we create new comments for edits, how do we track which is the "current" version?
   - **Resolution**: Need to clarify: the NEW comment is the visible one, the OLD comment gets `user_viewable="edit"`

3. **Delete vs user_viewable Conflict (Section 3 & 4)**:
   - Section 3 proposes adding `deleted` boolean flag
   - Section 4 proposes using `user_viewable="deleted"` instead
   - **Issue**: Two different approaches for the same feature
   - **Resolution**: Use only `user_viewable="deleted"` approach, remove `deleted` boolean

4. **Backward Compatibility Confusion (Section 7)**:
   - Section 7 mentions keeping `is_edited`, `edited_at`, `edited_by_id` for backward compatibility
   - But Section 2 says to fully migrate to `previous_comment_id` approach
   - **Issue**: If we fully migrate, why keep old fields?
   - **Resolution**: Remove old edit tracking fields after migration is complete

5. **Missing Migration Path**:
   - No clear migration strategy for existing comments with `is_private=True`
   - User answered "just delete the column no actions" - but what about existing data?
   - **Issue**: Need to handle existing `is_private=True` comments
   - **Resolution**: Set `user_viewable=None` for all existing comments (they become visible)

## Reply-to-Comment Feature Plan

### Requirements
- Users can reply to any comment
- Replies are NOT nested/chained - they appear in chronological order
- Each reply shows a visual link/indicator to the parent comment
- Clicking the link scrolls to and highlights the parent comment

### Data Model Changes

#### 1. Add `replied_to_comment_id` field to Comment model

```python
# In app/data/core/event_info/comment.py
replied_to_comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)
replied_to_comment = db.relationship('Comment', remote_side=[id], foreign_keys=[replied_to_comment_id])
```

**Rationale**: 
- Simple foreign key relationship
- Nullable (top-level comments have no parent)
- Self-referential relationship (comment replies to comment)

### Business Logic Changes

#### 1. Update `EventContext.add_comment()` method

Add optional `replied_to_comment_id` parameter:

```python
def add_comment(
    self,
    user_id: int,
    content: str,
    is_private: bool = False,
    is_human_made: bool = False,
    replied_to_comment_id: Optional[int] = None  # NEW
) -> Comment:
    """
    Add a comment to the event.
    
    Args:
        user_id: ID of user creating the comment
        content: Comment content text
        is_private: Whether comment is private (default: False)
        is_human_made: Whether comment was manually inserted by a human (default: False)
        replied_to_comment_id: ID of comment this is replying to (default: None)
        
    Returns:
        Created Comment instance
    """
    comment = Comment(
        content=content,
        event_id=self._event_id,
        created_by_id=user_id,
        updated_by_id=user_id,
        is_private=is_private,
        is_human_made=is_human_made,
        replied_to_comment_id=replied_to_comment_id  # NEW
    )
    # ... rest of method
```

#### 2. Update `EventContext.add_comment_with_attachments()` method

Add same `replied_to_comment_id` parameter and pass it to `add_comment()`.

#### 3. Add helper method to get parent comment info

```python
def get_reply_info(self) -> Optional[dict]:
    """
    Get information about the comment this comment is replying to.
    
    Returns:
        Dict with parent comment info or None if not a reply
    """
    if not self.replied_to_comment_id:
        return None
    
    parent = Comment.query.get(self.replied_to_comment_id)
    if not parent:
        return None
    
    return {
        'id': parent.id,
        'content_preview': parent.get_content_preview(50),
        'created_by_username': parent.created_by.username if parent.created_by else 'System',
        'created_at': parent.created_at
    }
```

### Route Changes

#### 1. Update comment creation route

```python
@bp.route('/events/<int:event_id>/comments', methods=['POST'])
@login_required
def create(event_id):
    """Create a new comment on an event"""
    event_context = EventContext(event_id)
    
    content = request.form.get('content', '').strip()
    is_private = request.form.get('is_private') == 'on'
    replied_to_comment_id = request.form.get('replied_to_comment_id')  # NEW
    
    # Validate replied_to_comment_id if provided
    if replied_to_comment_id:
        try:
            replied_to_comment_id = int(replied_to_comment_id)
            # Verify the parent comment exists and belongs to this event
            parent_comment = Comment.query.get(replied_to_comment_id)
            if not parent_comment or parent_comment.event_id != event_id:
                flash('Invalid reply target', 'error')
                return redirect(url_for('events.detail', event_id=event_id))
        except (ValueError, TypeError):
            replied_to_comment_id = None
    
    # ... rest of create logic, passing replied_to_comment_id
```

### Template Changes

#### 1. Display reply indicator in comment list

Add visual indicator showing which comment a reply is responding to:

```html
{% if comment.replied_to_comment_id %}
    <div class="reply-indicator mb-2">
        <small class="text-muted">
            <i class="bi bi-reply"></i> 
            Replying to 
            <a href="#comment-{{ comment.replied_to_comment_id }}" 
               class="reply-link"
               onclick="scrollToComment({{ comment.replied_to_comment_id }})">
                {{ comment.replied_to_comment.get_content_preview(30) }}
            </a>
        </small>
    </div>
{% endif %}
```

#### 2. Add "Reply" button to each comment

```html
<div class="btn-group btn-group-sm">
    <button class="btn btn-outline-secondary btn-sm" 
            onclick="replyToComment({{ comment.id }})"
            title="Reply to this comment">
        <i class="bi bi-reply"></i> Reply
    </button>
    {% if comment.created_by_id == current_user.id %}
        <button class="btn btn-outline-primary btn-sm" 
                onclick="editComment({{ comment.id }})">
            <i class="bi bi-pencil"></i>
        </button>
        <button class="btn btn-outline-danger btn-sm" 
                onclick="deleteComment({{ comment.id }})">
            <i class="bi bi-trash"></i>
        </button>
    {% endif %}
</div>
```

#### 3. Update comment form to include reply context

When replying, pre-populate form with reply context and hidden field:

```html
<form id="commentForm" method="POST" action="{{ url_for('comments.create', event_id=event.id) }}">
    <input type="hidden" name="replied_to_comment_id" id="replied_to_comment_id" value="">
    
    <div id="reply-context" style="display: none;" class="alert alert-info mb-3">
        <strong>Replying to:</strong>
        <span id="reply-context-text"></span>
        <button type="button" class="btn btn-sm btn-link" onclick="cancelReply()">Cancel</button>
    </div>
    
    <!-- rest of form -->
</form>
```

### JavaScript/Alpine.js Changes

#### 1. Replace vanilla JS with Alpine.js for reply functionality

See example module below for Alpine.js implementation.

#### 2. Add scroll-to-comment functionality

```javascript
function scrollToComment(commentId) {
    const commentElement = document.querySelector(`[data-comment-id="${commentId}"]`);
    if (commentElement) {
        commentElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        // Highlight briefly
        commentElement.classList.add('highlight-comment');
        setTimeout(() => {
            commentElement.classList.remove('highlight-comment');
        }, 2000);
    }
}
```

### CSS Changes

Add styles for reply indicators and highlighting:

```css
.reply-indicator {
    padding: 0.25rem 0.5rem;
    background-color: #f8f9fa;
    border-left: 3px solid #0d6efd;
    border-radius: 3px;
}

.reply-link {
    color: #0d6efd;
    text-decoration: none;
    font-weight: 500;
}

.reply-link:hover {
    text-decoration: underline;
}

.highlight-comment {
    background-color: #fff3cd;
    transition: background-color 0.3s ease;
    border-left: 4px solid #ffc107;
    padding-left: 0.5rem;
}
```

### Implementation Order

1. **Phase 1: Data Model**
   - Add `replied_to_comment_id` field to Comment model
   - Create and run migration
   - Add relationship to Comment model

2. **Phase 2: Business Logic**
   - Update `EventContext.add_comment()` to accept `replied_to_comment_id`
   - Update `EventContext.add_comment_with_attachments()` 
   - Add `get_reply_info()` helper method to Comment model

3. **Phase 3: Routes**
   - Update comment creation route to handle `replied_to_comment_id`
   - Add validation for reply target

4. **Phase 4: Templates**
   - Add reply indicator display in comment list
   - Add "Reply" button to each comment
   - Update comment form to show reply context

5. **Phase 5: Frontend Interactions**
   - Implement Alpine.js component for reply functionality
   - Add scroll-to-comment functionality
   - Add CSS for reply indicators and highlighting

### Testing Considerations

- Test creating a top-level comment (no reply)
- Test creating a reply to an existing comment
- Test that replies appear in chronological order (not nested)
- Test reply indicator displays correctly
- Test scroll-to-comment functionality
- Test that reply link works even if parent comment is far away
- Test reply validation (can't reply to non-existent comment)
- Test reply validation (can't reply to comment from different event)
- Test that deleted comments can't be replied to (if parent is deleted)

### Edge Cases

1. **Parent comment deleted**: Show "Replying to [deleted comment]" or hide reply indicator
2. **Parent comment from different event**: Validation prevents this
3. **Circular replies**: Not possible with single `replied_to_comment_id` field (no chains)
4. **Reply to a reply**: Allowed - shows link to immediate parent only



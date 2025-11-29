# Investigation Plan: Comment Modals Not Appearing in Initial Template

## Problem Statement
After a comment is edited and HTMX swaps in the new content, the "View JSON" (metadata) modal and "Edit Comment History" appear correctly. However, these features do not appear in the initial template render.

## Key Files Involved
- `app/presentation/templates/core/events/event_activity.html` - Initial template
- `app/presentation/templates/core/events/comment_item.html` - Template used after HTMX swap
- `app/presentation/routes/core/events/comments.py` - Route handlers and data preparation
- `app/data/core/event_info/comment.py` - Comment model

## Data Flow Analysis

### Initial Render Flow (`event_activity.html`)
1. `render_event_activity()` is called (line 98-137 in comments.py)
2. Creates `comments_data = [_prepare_comment_data(comment, user_id) for comment in comments]` (line 129)
3. Each `comment_data` dict has structure: `{'comment': Comment_obj, 'edit_history': [...], 'metadata': {...}}`
4. Template receives both `comments` (list of Comment objects) and `comments_data` (list of dicts)
5. Template loops through `comments` (line 369) and tries to find matching data in `comments_data` (lines 374-381)
6. Lookup logic: `{% if cd.comment and cd.comment.id == comment.id %}` (line 376)

### After Edit Flow (`comment_item.html`)
1. `render_single_comment()` is called (line 74-95 in comments.py)
2. Calls `_prepare_comment_data(comment, user_id)` (line 87)
3. Passes `comment_data=comment_data` directly to template (line 92)
4. Template uses `comment_data` directly without lookup (lines 1-3 of comment_item.html)

## Potential Root Causes

### 1. **Object Identity Mismatch in Template Lookup**
**Location**: `event_activity.html` lines 374-381

**Issue**: The lookup `cd.comment.id == comment.id` might fail if:
- SQLAlchemy returns different object instances for the same comment
- The `comments` list and `comments_data` list contain different object instances
- Object comparison fails due to lazy loading or session issues

**Investigation Steps**:
- Add debug logging in `_prepare_comment_data()` to print comment IDs
- Add debug output in template to verify `comments_data` structure
- Check if `cd.comment` is None or if `cd.comment.id` doesn't match `comment.id`
- Verify that `comments_data` array length matches `comments` array length

**Evidence to Collect**:
- Log the comment IDs in both arrays
- Check if lookup loop finds matches
- Verify object types and IDs

### 2. **Conditional Rendering Logic**
**Location**: `event_activity.html` lines 405, 490

**Issue**: 
- Edit history section only shows if `edit_history|length > 1` (line 405)
- Metadata modal only renders if `metadata` is truthy (line 490)
- If lookup fails, `edit_history = []` and `metadata = None` (lines 372-373)

**Investigation Steps**:
- Check if `comment_data` lookup is succeeding (is `comment_data` None after lookup?)
- Verify if `edit_history` has data but length check fails
- Check if `metadata` exists but is falsy (empty dict, None, etc.)
- Compare what `_prepare_comment_data()` returns vs what template receives

**Evidence to Collect**:
- Template variable values after lookup
- Length of `edit_history` array
- Type and content of `metadata` variable

### 3. **Data Preparation Timing Issues**
**Location**: `comments.py` lines 113-129

**Issue**: 
- `event_context.refresh()` is called (line 116) which might reload comments
- The `comments` list might be from a different query than what `_prepare_comment_data()` receives
- Filter logic might create mismatched lists

**Investigation Steps**:
- Verify that `comments` used in template matches `comments` used in `_prepare_comment_data()` loop
- Check if `filter_human_only` affects comment ordering or filtering
- Ensure `EventService.get_human_comments()` returns same objects as `event_context.comments`

**Evidence to Collect**:
- Comment IDs in `comments` list vs IDs in `comments_data`
- Order of comments in both lists
- Whether all comments have corresponding data entries

### 4. **Template Variable Scope or Naming**
**Location**: `event_activity.html` lines 371-382

**Issue**: 
- Variables `comment_data`, `edit_history`, `metadata` are set inside the loop
- Jinja2 variable scoping might cause issues
- Variable names might conflict with other template variables

**Investigation Steps**:
- Verify variable names don't conflict
- Check if variables persist correctly through the loop iteration
- Ensure `comment_data` is properly set before modal rendering

**Evidence to Collect**:
- Variable values at different points in template
- Whether variables are accessible in modal sections

### 5. **Missing Data in `_prepare_comment_data()`**
**Location**: `comments.py` lines 16-71

**Issue**: 
- `_prepare_comment_data()` only populates `edit_history` and `metadata` if `comment.created_by_id == user_id` (line 35)
- If this check fails, data remains empty/None
- Exception handling might silently fail (lines 50-52, 67-69)

**Investigation Steps**:
- Verify `comment.created_by_id == user_id` is True for owned comments
- Check if exceptions are being caught and logged
- Verify `EventContext.get_comment_edit_history()` returns data
- Check if `comment.print_safe_dict()` works correctly

**Evidence to Collect**:
- Log output from `_prepare_comment_data()` (line 66 has print statement)
- Exception logs if any
- Return values from helper methods

### 6. **HTMX Swap Behavior Difference**
**Location**: `comments.py` line 261-267

**Issue**: 
- After edit, `render_single_comment()` is called which uses `comment_item.html`
- `comment_item.html` receives `comment_data` directly (no lookup needed)
- Initial render uses inline HTML in `event_activity.html` with lookup logic

**Investigation Steps**:
- Compare data structure passed to both templates
- Verify if `comment_item.html` would work if included in `event_activity.html`
- Check if HTMX swap preserves any state that initial render doesn't have

**Evidence to Collect**:
- Data structure comparison
- Template rendering differences

## Investigation Priority Order

1. **HIGH PRIORITY**: Check if lookup in `event_activity.html` is finding matches (lines 374-381)
   - Add debug output to verify `comment_data` is found
   - Check if `cd.comment.id == comment.id` comparison works

2. **HIGH PRIORITY**: Verify `_prepare_comment_data()` is returning data correctly
   - Check print output (line 66)
   - Verify `edit_history` and `metadata` are populated for owned comments
   - Check exception logs

3. **MEDIUM PRIORITY**: Check conditional rendering logic
   - Verify `edit_history|length > 1` condition
   - Verify `{% if metadata %}` condition
   - Check if data exists but conditions fail

4. **MEDIUM PRIORITY**: Compare object instances
   - Check if `comments` and `comments_data[].comment` are same objects
   - Verify SQLAlchemy session/identity map behavior

5. **LOW PRIORITY**: Template structure differences
   - Compare why `comment_item.html` works but inline rendering doesn't
   - Consider refactoring to use `comment_item.html` include

## Debugging Strategy

### Step 1: Add Template Debugging
Add temporary debug output in `event_activity.html` after line 381:
```jinja2
<!-- DEBUG: Comment {{ comment.id }} -->
<!-- comment_data found: {{ 'YES' if comment_data else 'NO' }} -->
<!-- edit_history length: {{ edit_history|length }} -->
<!-- metadata exists: {{ 'YES' if metadata else 'NO' }} -->
```

### Step 2: Add Python Debugging
Add logging in `render_event_activity()` after line 129:
```python
logger.debug(f"Prepared {len(comments_data)} comment data entries")
for cd in comments_data:
    logger.debug(f"Comment {cd['comment'].id}: edit_history={len(cd.get('edit_history', []))}, metadata={'exists' if cd.get('metadata') else 'None'}")
```

### Step 3: Verify Lookup Logic
Check if the lookup loop is matching correctly by adding debug output in template.

### Step 4: Compare Working vs Non-Working
After edit, check what data `comment_item.html` receives vs what `event_activity.html` receives.

## Expected Findings

Most likely causes (in order of probability):
1. **Lookup failure**: The `cd.comment.id == comment.id` comparison is failing due to object identity issues
2. **Empty data**: `_prepare_comment_data()` is returning empty `edit_history`/`metadata` even for owned comments
3. **Conditional logic**: Data exists but conditional checks (`length > 1`, `if metadata`) are failing
4. **Template variable scoping**: Variables set in loop aren't accessible in modal sections

## Next Steps After Investigation

Once root cause is identified:
- Fix the lookup logic or data preparation
- Ensure consistent data structure between initial render and HTMX swap
- Consider refactoring to use `comment_item.html` template include for consistency
- Add proper error handling and logging


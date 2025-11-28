from flask import Blueprint, request, jsonify, flash, redirect, url_for, render_template
from app.logger import get_logger
from flask_login import login_required, current_user
from app import db
from app.data.core.event_info.comment import Comment
from app.data.core.event_info.event import Event
from app.buisness.core.event_context import EventContext
from app.services.core.event_service import EventService
import json

bp = Blueprint('comments', __name__)
logger = get_logger("asset_management.routes.bp")


@bp.route('/events/<int:event_id>/comments', methods=['POST'])
@login_required
def create(event_id):
    """Create a new comment on an event"""
    event_context = EventContext(event_id)

    content = request.form.get('content', '').strip()
    replied_to_comment_id = request.form.get('replied_to_comment_id')

    # Validate replied_to_comment_id if provided
    if replied_to_comment_id:
        try:
            replied_to_comment_id = int(replied_to_comment_id)
            # Verify the parent comment exists and belongs to this event
            parent_comment = Comment.query.get(replied_to_comment_id)
            if not parent_comment or parent_comment.event_id != event_id:
                flash('Invalid reply target', 'error')
                return redirect(url_for('events.detail', event_id=event_id))
            # Can't reply to deleted comments
            if parent_comment.user_viewable == 'deleted':
                flash('Cannot reply to deleted comment', 'error')
                return redirect(url_for('events.detail', event_id=event_id))
        except (ValueError, TypeError):
            replied_to_comment_id = None

    # Get files if any
    files = request.files.getlist('attachments')
    has_files = any(file and file.filename for file in files)

    try:
        if has_files:
            # Use EventContext to handle comment with attachments (auto_commit=True handles transaction)
            event_context.add_comment_with_attachments(
                user_id=current_user.id,
                content=content,
                file_objects=files,
                is_human_made=True,  # Comments created via UI are human-made
                replied_to_comment_id=replied_to_comment_id,
                auto_commit=True
            )
        else:
            # Simple comment without attachments
            if not content:
                flash('Comment content is required', 'error')
                return redirect(url_for('events.detail', event_id=event_id))
            
            event_context.add_comment(
                user_id=current_user.id,
                content=content,
                is_human_made=True,  # Comments created via UI are human-made
                replied_to_comment_id=replied_to_comment_id
            )
            db.session.commit()

        # If this is an HTMX request, return the updated event widget instead of redirecting
        if request.headers.get('HX-Request'):
            event_context.refresh()  # Refresh to get latest comments
            # Preserve filter state if it was set
            filter_human_only = request.args.get('human_only', 'false').lower() == 'true'
            if filter_human_only:
                # Use service for presentation-specific filtering
                comments = EventService.get_human_comments(event_id)
            else:
                comments = event_context.comments
            return render_template(
                'core/events/event_activity.html',
                event=event_context.event,
                comments=comments,
                filter_human_only=filter_human_only,
            )

        flash('Comment added successfully', 'success')
        return redirect(url_for('events.detail', event_id=event_id))
    
    except ValueError as e:
        flash(str(e), 'error')
        db.session.rollback()
        return redirect(url_for('events.detail', event_id=event_id))


@bp.route('/events/<int:event_id>/widget', methods=['GET'])
@login_required
def event_widget(event_id):
    """
    Render the reusable Event widget (comments, attachments, metadata)
    for the given event. Intended for embedding via HTMX on any page.
    """
    event_context = EventContext(event_id)
    
    # Check if filtering to human comments only
    filter_human_only = request.args.get('human_only', 'false').lower() == 'true'
    
    if filter_human_only:
        # Use service for presentation-specific filtering
        comments = EventService.get_human_comments(event_id)
    else:
        comments = event_context.comments

    return render_template(
        'core/events/event_activity.html',
        event=event_context.event,
        comments=comments,
        filter_human_only=filter_human_only,
    )


@bp.route('/comments/<int:comment_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(comment_id):
    """Edit an existing comment"""
    comment = Comment.query.get_or_404(comment_id)
    event_context = EventContext(comment.event_id)

    # Check if user can edit this comment
    if comment.created_by_id != current_user.id:
        flash('You can only edit your own comments', 'error')
        return redirect(url_for('events.detail', event_id=comment.event_id))

    if request.method == 'POST':
        content = request.form.get('content', '').strip()

        if not content:
            flash('Comment content is required', 'error')
            if request.headers.get('HX-Request'):
                # Return error response for HTMX
                event_context.refresh()
                filter_human_only = request.args.get('human_only', 'false').lower() == 'true'
                if filter_human_only:
                    comments = EventService.get_human_comments(comment.event_id)
                else:
                    comments = event_context.comments
                return render_template(
                    'core/events/event_activity.html',
                    event=event_context.event,
                    comments=comments,
                    filter_human_only=filter_human_only,
                ), 400
            return redirect(url_for('events.detail', event_id=comment.event_id))

        try:
            # Use EventContext to edit comment (creates new comment, marks old as edit)
            new_comment = event_context.edit_comment(
                comment_id=comment_id,
                user_id=current_user.id,
                new_content=content
            )
            db.session.commit()
            flash('Comment updated successfully', 'success')
        except ValueError as e:
            flash(str(e), 'error')
            db.session.rollback()
            if request.headers.get('HX-Request'):
                # Return error response for HTMX
                event_context.refresh()
                filter_human_only = request.args.get('human_only', 'false').lower() == 'true'
                if filter_human_only:
                    comments = EventService.get_human_comments(comment.event_id)
                else:
                    comments = event_context.comments
                return render_template(
                    'core/events/event_activity.html',
                    event=event_context.event,
                    comments=comments,
                    filter_human_only=filter_human_only,
                ), 400
            return redirect(url_for('events.detail', event_id=comment.event_id))

        # If this is an HTMX request, return the updated event widget instead of redirecting
        if request.headers.get('HX-Request'):
            event_context.refresh()  # Refresh to get latest comments
            # Preserve filter state if it was set
            filter_human_only = request.args.get('human_only', 'false').lower() == 'true'
            if filter_human_only:
                # Use service for presentation-specific filtering
                comments = EventService.get_human_comments(comment.event_id)
            else:
                comments = event_context.comments
            return render_template(
                'core/events/event_activity.html',
                event=event_context.event,
                comments=comments,
                filter_human_only=filter_human_only,
            )

        return redirect(url_for('events.detail', event_id=comment.event_id))

    # GET request - return comment data for AJAX
    # Get edit history if available
    edit_history = []
    try:
        history_comments = EventContext.get_comment_edit_history(comment)
        edit_history = [
            {
                'id': h.id,
                'content': h.content,
                'created_at': h.created_at.isoformat() if h.created_at else None,
                'created_by_id': h.created_by_id,
                'created_by_username': h.created_by.username if h.created_by else None,
                'is_current': h.id == comment.id,
            }
            for h in history_comments
        ]
        # Log if any comments are missing created_at for debugging
        for h in history_comments:
            if not h.created_at:
                logger.warning(f"Comment {h.id} in edit history is missing created_at timestamp")
    except Exception as e:
        # If edit history fails, just return empty list
        logger.error(f"Error getting edit history for comment {comment_id}: {e}")
        edit_history = []
    
    return jsonify(
        {
            'id': comment.id,
            'content': comment.content,
            'edit_history': edit_history,
        }
    )


@bp.route('/comments/<int:comment_id>/metadata', methods=['GET'])
@login_required
def metadata(comment_id):
    """Get comment metadata as JSON"""
    comment = Comment.query.get_or_404(comment_id)
    
    # Build metadata dictionary with all comment information
    metadata = {
        'id': comment.id,
        'content': comment.content,
        'event_id': comment.event_id,
        'is_human_made': comment.is_human_made,
        'user_viewable': comment.user_viewable,
        'previous_comment_id': comment.previous_comment_id,
        'replied_to_comment_id': comment.replied_to_comment_id,
        'created_at': comment.created_at.isoformat() if comment.created_at else None,
        'updated_at': comment.updated_at.isoformat() if comment.updated_at else None,
        'created_by_id': comment.created_by_id,
        'updated_by_id': comment.updated_by_id,
        'created_by_username': comment.created_by.username if comment.created_by else None,
        'updated_by_username': comment.updated_by.username if comment.updated_by else None,
        'event_type': comment.event.event_type if comment.event else None,
        'event_description': comment.event.description if comment.event else None,
        'has_attachments': len(comment.comment_attachments) > 0,
        'attachment_count': len(comment.comment_attachments),
        'attachments': [
            {
                'id': ca.attachment.id,
                'filename': ca.attachment.filename,
                'file_size': ca.attachment.file_size,
                'mime_type': ca.attachment.mime_type,
                'display_order': ca.display_order,
            }
            for ca in comment.comment_attachments
        ] if comment.comment_attachments else [],
    }
    
    return jsonify(metadata)


@bp.route('/comments/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete(comment_id):
    """Delete a comment (soft delete)"""
    comment = Comment.query.get_or_404(comment_id)
    event_context = EventContext(comment.event_id)

    # Check if user can delete this comment
    if comment.created_by_id != current_user.id:
        return jsonify({'error': 'You can only delete your own comments'}), 403

    try:
        # Use EventContext to soft delete comment
        event_context.delete_comment(
            comment_id=comment_id,
            user_id=current_user.id
        )
        db.session.commit()
    except ValueError as e:
        if request.headers.get('Content-Type') == 'application/json':
            return jsonify({'error': str(e)}), 400
        flash(str(e), 'error')
        db.session.rollback()
        return redirect(url_for('events.detail', event_id=comment.event_id))

    if request.headers.get('Content-Type') == 'application/json':
        return jsonify({'success': True})

    flash('Comment deleted successfully', 'success')
    return redirect(url_for('events.detail', event_id=comment.event_id))



from flask import Blueprint, request, jsonify, flash, redirect, url_for
from app.logger import get_logger
from flask_login import login_required, current_user
from app import db
from app.models.core.comment import Comment
from app.models.core.comment import CommentAttachment
from app.models.core.attachment import Attachment
from app.models.core.event import Event
import json

bp = Blueprint('comments', __name__)
logger = get_logger("asset_management.routes.bp")

@bp.route('/events/<int:event_id>/comments', methods=['POST'])
@login_required
def create(event_id):
    """Create a new comment on an event"""
    event = Event.query.get_or_404(event_id)
    
    content = request.form.get('content', '').strip()
    is_private = request.form.get('is_private') == 'on'
    
    # Check if there are any files being uploaded
    files = request.files.getlist('attachments')
    has_files = any(file and file.filename for file in files)
    
    if not content and not has_files:
        flash('Either comment content or file attachments are required', 'error')
        return redirect(url_for('events.detail', event_id=event_id))
    
    # If no content but has files, create a default content
    if not content and has_files:
        content = f"Added {len([f for f in files if f and f.filename])} attachment(s)"
    
    # Create the comment
    comment = Comment(
        content=content,
        event_id=event_id,
        is_private=is_private,
        created_by_id=current_user.id,
        updated_by_id=current_user.id
    )
    
    db.session.add(comment)
    db.session.flush()  # Get the comment ID
    
    # Handle file attachments
    files = request.files.getlist('attachments')
    for file in files:
        if file and file.filename:
            # Validate file
            if not Attachment.is_allowed_file(file.filename):
                flash(f'File type not allowed: {file.filename}', 'error')
                continue
            
            # Read file data
            file_data = file.read()
            file_size = len(file_data)
            
            if file_size > Attachment.MAX_FILE_SIZE:
                flash(f'File too large: {file.filename} ({Attachment.MAX_FILE_SIZE / (1024*1024):.1f}MB max)', 'error')
                continue
            
            # Create attachment
            attachment = Attachment(
                filename=file.filename,
                file_size=file_size,
                mime_type=file.content_type or 'application/octet-stream',
                created_by_id=current_user.id,
                updated_by_id=current_user.id
            )
            
            # Save file to appropriate storage
            attachment.save_file(file_data, file.filename)
            
            db.session.add(attachment)
            db.session.flush()  # Get the attachment ID
            
            # Create comment attachment link
            comment_attachment = CommentAttachment(
                attached_to_id=comment.id,  # Use attached_to_id instead of comment_id
                attachment_id=attachment.id,
                display_order=len(comment.comment_attachments) + 1,  # Add display order
                attachment_type='Document',  # Set attachment type
                created_by_id=current_user.id,
                updated_by_id=current_user.id
            )
            
            db.session.add(comment_attachment)
    
    db.session.commit()
    flash('Comment added successfully', 'success')
    
    return redirect(url_for('events.detail', event_id=event_id))

@bp.route('/comments/<int:comment_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(comment_id):
    """Edit an existing comment"""
    comment = Comment.query.get_or_404(comment_id)
    
    # Check if user can edit this comment
    if comment.created_by_id != current_user.id:
        flash('You can only edit your own comments', 'error')
        return redirect(url_for('events.detail', event_id=comment.event_id))
    
    if request.method == 'POST':
        content = request.form.get('content', '').strip()
        is_private = request.form.get('is_private') == 'on'
        
        if not content:
            flash('Comment content is required', 'error')
            return redirect(url_for('events.detail', event_id=comment.event_id))
        
        # Update comment
        comment.content = content
        comment.is_private = is_private
        comment.mark_as_edited(current_user.id)
        comment.updated_by_id = current_user.id
        
        db.session.commit()
        flash('Comment updated successfully', 'success')
        
        return redirect(url_for('events.detail', event_id=comment.event_id))
    
    # GET request - return comment data for AJAX
    return jsonify({
        'id': comment.id,
        'content': comment.content,
        'is_private': comment.is_private
    })

@bp.route('/comments/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete(comment_id):
    """Delete a comment"""
    comment = Comment.query.get_or_404(comment_id)
    
    # Check if user can delete this comment
    if comment.created_by_id != current_user.id:
        return jsonify({'error': 'You can only delete your own comments'}), 403
    
    event_id = comment.event_id
    
    # Delete associated comment attachments and files
    for comment_attachment in comment.comment_attachments:
        attachment = comment_attachment.attachment
        attachment.delete_file()  # Delete from filesystem if needed
        db.session.delete(attachment)
        db.session.delete(comment_attachment)
    
    # Delete the comment
    db.session.delete(comment)
    db.session.commit()
    
    if request.headers.get('Content-Type') == 'application/json':
        return jsonify({'success': True})
    
    flash('Comment deleted successfully', 'success')
    return redirect(url_for('events.detail', event_id=event_id)) 
from flask import Blueprint, request, send_file, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.core.attachment import Attachment
from app.models.core.event import Event
from werkzeug.utils import secure_filename
import io
import os

bp = Blueprint('attachments', __name__)



@bp.route('/attachments/<int:attachment_id>/download')
@login_required
def download(attachment_id):
    """Download an attachment"""
    attachment = Attachment.query.get_or_404(attachment_id)
    
    # Get file data
    file_data = attachment.get_file_data()
    if not file_data:
        flash('File not found', 'error')
        return redirect(url_for('events.detail', event_id=attachment.event_id))
    
    # Create file-like object
    file_stream = io.BytesIO(file_data)
    file_stream.seek(0)
    
    return send_file(
        file_stream,
        as_attachment=True,
        download_name=attachment.filename,
        mimetype=attachment.mime_type
    )

@bp.route('/attachments/<int:attachment_id>/view')
@login_required
def view(attachment_id):
    """View an attachment in browser (for images, PDFs, etc.)"""
    attachment = Attachment.query.get_or_404(attachment_id)
    
    # Get file data
    file_data = attachment.get_file_data()
    if not file_data:
        flash('File not found', 'error')
        return redirect(url_for('events.detail', event_id=attachment.event_id))
    
    # Create file-like object
    file_stream = io.BytesIO(file_data)
    file_stream.seek(0)
    
    return send_file(
        file_stream,
        mimetype=attachment.mime_type
    )

@bp.route('/attachments/<int:attachment_id>/delete', methods=['POST'])
@login_required
def delete(attachment_id):
    """Delete an attachment"""
    attachment = Attachment.query.get_or_404(attachment_id)
    
    # Check if user can delete this attachment
    if attachment.created_by_id != current_user.id:
        flash('You can only delete your own attachments', 'error')
        return redirect(url_for('events.detail', event_id=attachment.event_id))
    
    # Find the comment that contains this attachment
    from app.models.core.comment_attachment import CommentAttachment
    comment_attachment = CommentAttachment.query.filter_by(attachment_id=attachment_id).first()
    
    if not comment_attachment:
        flash('Attachment not found in any comment', 'error')
        return redirect(url_for('events.list'))
    
    event_id = comment_attachment.comment.event_id
    
    # Delete file from storage
    attachment.delete_file()
    
    # Delete comment attachment link
    db.session.delete(comment_attachment)
    
    # Delete attachment
    db.session.delete(attachment)
    db.session.commit()
    
    flash(f'Attachment "{attachment.filename}" deleted successfully', 'success')
    return redirect(url_for('events.detail', event_id=event_id))

@bp.route('/attachments/<int:attachment_id>/info')
@login_required
def info(attachment_id):
    """Get attachment information"""
    attachment = Attachment.query.get_or_404(attachment_id)
    
    return jsonify({
        'id': attachment.id,
        'filename': attachment.filename,
        'file_size': attachment.file_size,
        'file_size_display': attachment.get_file_size_display(),
        'mime_type': attachment.mime_type,
        'description': attachment.description,
        'tags': attachment.tags,
        'storage_type': attachment.storage_type,
        'is_image': attachment.is_image(),
        'is_document': attachment.is_document(),
        'created_at': attachment.created_at.isoformat(),
        'created_by': attachment.created_by.username if attachment.created_by else 'System'
    }) 
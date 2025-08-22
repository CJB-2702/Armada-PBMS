"""
Core models package for the Asset Management System
"""

from .user import User
from .major_location import MajorLocation
from .asset_type import AssetType
from .make_model import MakeModel
from .asset import Asset
from .event import Event
from .attachment import Attachment, AttachmentIDManager
from .comment import Comment, CommentAttachment
from .virtual_sequence_generator import VirtualSequenceGenerator

__all__ = [
    'User',
    'MajorLocation', 
    'AssetType',
    'MakeModel',
    'Asset',
    'Event',
    'Attachment',
    'AttachmentIDManager',
    'Comment',
    'CommentAttachment',
    'VirtualSequenceGenerator'
] 
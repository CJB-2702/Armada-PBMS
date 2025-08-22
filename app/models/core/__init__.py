"""
Core models package for the Asset Management System
"""

from .user import User
from .major_location import MajorLocation
from .asset_type import AssetType
from .make_model import MakeModel
from .asset import Asset
from .event import Event
from .attachment import Attachment
from .comment import Comment
from .comment_attachment import CommentAttachment
from .virtual_sequence_generator import VirtualSequenceGenerator

__all__ = [
    'User',
    'MajorLocation', 
    'AssetType',
    'MakeModel',
    'Asset',
    'Event',
    'Attachment',
    'Comment',
    'CommentAttachment',
    'VirtualSequenceGenerator'
] 
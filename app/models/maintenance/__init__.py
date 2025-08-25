# Base models
from .base import (
    MaintenancePlan,
    MaintenanceEventSet,
    Action
)

# Template models
from .templates import (
    TemplateActionSet,
    TemplateActionItem,
    TemplateActionAttachment,
    TemplatePartDemand
)

# Core models
from app.models.core.attachment import VirtualAttachmentRefrence

# Virtual models
from .virtual_action_item import VirtualActionItem
from .virtual_action_set import VirtualActionSet

__all__ = [
    # Base models
    'MaintenancePlan',
    'MaintenanceEventSet',
    'Action',
    
    # Template models
    'TemplateActionSet',
    'TemplateActionItem',
    'TemplateActionAttachment',
    'TemplatePartDemand',
    'TemplateActionTool',
    
    # Core models
    'VirtualAttachmentRefrence',
    
    # Virtual models
    'VirtualActionItem',
    'VirtualActionSet'
]

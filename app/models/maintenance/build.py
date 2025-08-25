"""
Build script for maintenance models
This ensures all models are properly imported and registered
"""

# Base models
from app.models.maintenance.base import (
    MaintenancePlan,
    MaintenanceEventSet,
    Action
)

# Template models
from app.models.maintenance.templates import (
    TemplateActionSetHeader,
    TemplateActionSet,
    TemplateActionItem,
    TemplateActionAttachment,
    TemplatePartDemand,
    TemplateActionTool
)

# Core models
from app.models.core.attachment import VirtualAttachmentRefrence

# Supply models
from app.models.supply import (
    Part,
    Tool,
    PartDemand,
    VirtualPartDemand
)

# Virtual models
from app.models.maintenance.virtual_action_item import VirtualActionItem
from app.models.maintenance.virtual_action_set import VirtualActionSet

def build_maintenance_models():
    """Build and register all maintenance models"""
    models = [
        # Base maintenance models
        MaintenancePlan,
        MaintenanceEventSet,
        Action,
        
        # Template models
        TemplateActionSet,
        TemplateActionItem,
        TemplateActionAttachment,
        TemplatePartDemand,
        TemplateActionTool,
        
        # Core models
        VirtualAttachmentRefrence,
        
        # Virtual entities
        VirtualActionItem,
        VirtualActionSet,
        
        # Supply models
        Part,
        Tool,
        PartDemand,
        VirtualPartDemand
    ]
    
    return models

if __name__ == "__main__":
    print("Building maintenance models...")
    models = build_maintenance_models()
    print(f"Built {len(models)} models:")
    
    print("\nBase Models:")
    for model in models[:3]:
        print(f"  - {model.__name__}")
    
    print("\nTemplate Models:")
    for model in models[3:8]:
        print(f"  - {model.__name__}")
    
    print("\nVirtual Models:")
    for model in models[8:11]:
        print(f"  - {model.__name__}")
    
    print("\nSupply Models:")
    for model in models[11:]:
        print(f"  - {model.__name__}")
    
    print("\nMaintenance models build complete!")

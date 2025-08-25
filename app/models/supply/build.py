"""
Build script for supply models
This ensures all models are properly imported and registered
"""

from app.models.supply import (
    Part,
    Tool,
    PartDemand,
    VirtualPartDemand
)

def build_supply_models():
    """Build and register all supply models"""
    models = [
        Part,
        Tool,
        PartDemand,
        VirtualPartDemand
    ]
    
    return models

if __name__ == "__main__":
    print("Building supply models...")
    models = build_supply_models()
    print(f"Built {len(models)} models:")
    for model in models:
        print(f"  - {model.__name__}")
    print("Supply models build complete!")

"""
Assets domain layer.
"""

from .asset_details_context import AssetDetailsContext
from .make_model_context import MakeModelDetailsContext
from .model_detail_context import ModelDetailContext
from .asset_details.asset_details_struct import AssetDetailsStruct
from .model_details.model_details_struct import ModelDetailsStruct

# Backward compatibility aliases
AssetContext = AssetDetailsContext
MakeModelContext = MakeModelDetailsContext

__all__ = ['AssetDetailsContext', 'MakeModelDetailsContext', 'ModelDetailContext', 'AssetDetailsStruct', 'ModelDetailsStruct', 'AssetContext', 'MakeModelContext']


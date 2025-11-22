"""
Assets domain layer.

This module extends core asset functionality with detail table management.
On import, it registers an enhanced asset factory with AssetContext.
"""

from .asset_details_context import AssetDetailsContext
from .make_model_context import MakeModelDetailsContext
from .model_detail_context import ModelDetailContext
from .asset_details.asset_details_struct import AssetDetailsStruct
from .model_details.model_details_struct import ModelDetailsStruct

# Import AssetContext from core to access its factory attribute
from app.buisness.core.asset_context import AssetContext as CoreAssetContext

# Import and register the enhanced factory
from app.buisness.assets.asset_details_factory import AssetDetailsFactory
from app.logger import get_logger

logger = get_logger("asset_management.buisness.assets")

# Register factory with type-aware guard (prevents duplicate registration)
# This replaces the core factory with the details factory, enabling detail creation
# NOTE: We register on CoreAssetContext (the actual class), not the alias below
if CoreAssetContext.asset_factory is not None:
    current_type = CoreAssetContext.asset_factory.get_factory_type()
    if current_type == "detail factory":
        # Already registered, skip (idempotent - prevents issues if module imported multiple times)
        logger.debug("AssetDetailsFactory already registered, skipping")
    else:
        # Factory exists but is not details factory (e.g., CoreAssetFactory)
        # Replace it with the enhanced version
        logger.debug(f"Replacing {current_type} factory with AssetDetailsFactory")
        CoreAssetContext.asset_factory = AssetDetailsFactory()
        logger.debug("AssetDetailsFactory registered with AssetContext")
else:
    # No factory set yet, register the details factory
    CoreAssetContext.asset_factory = AssetDetailsFactory()
    logger.debug("AssetDetailsFactory registered with AssetContext")

# Backward compatibility aliases
# These allow code to import AssetContext from assets module and get AssetDetailsContext
AssetContext = AssetDetailsContext
MakeModelContext = MakeModelDetailsContext

__all__ = ['AssetDetailsContext', 'MakeModelDetailsContext', 'ModelDetailContext', 'AssetDetailsStruct', 'ModelDetailsStruct', 'AssetContext', 'MakeModelContext']


"""
Asset management routes
CRUD operations for Asset model
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.models.core.asset import Asset
from app.models.core.asset_type import AssetType
from app.models.core.make_model import MakeModel
from app.models.core.major_location import MajorLocation
from app.models.core.event import Event
from app.models.assets.detail_table_templates.asset_details_from_asset_type import AssetDetailTemplateByAssetType
from app.models.assets.detail_table_templates.asset_details_from_model_type import AssetDetailTemplateByModelType
from app.models.assets.detail_table_templates.model_detail_table_template import ModelDetailTableTemplate
from app.models.assets.factories.asset_factory import AssetFactory
from app import db
from app.logger import get_logger

logger = get_logger("asset_management.routes.core.assets")
bp = Blueprint('assets', __name__)

@bp.route('/assets')
@login_required
def list():
    """List all assets with basic filtering"""
    logger.debug(f"User {current_user.username} accessing assets list")
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Basic filtering
    asset_type_id = request.args.get('asset_type_id', type=int)
    location_id = request.args.get('location_id', type=int)
    make_model_id = request.args.get('make_model_id', type=int)
    status = request.args.get('status')
    serial_number = request.args.get('serial_number')
    name = request.args.get('name')
    
    logger.debug(f"Assets list filters - Type: {asset_type_id}, Location: {location_id}, Model: {make_model_id}, Status: {status}")
    
    query = Asset.query
    
    if location_id:
        query = query.filter(Asset.major_location_id == location_id)
    
    if make_model_id:
        query = query.filter(Asset.make_model_id == make_model_id)
    
    if status:
        query = query.filter(Asset.status == status)
    
    if serial_number:
        query = query.filter(Asset.serial_number.ilike(f'%{serial_number}%'))
    
    if name:
        query = query.filter(Asset.name.ilike(f'%{name}%'))
    
    # Asset type filtering through make_model relationship
    if asset_type_id:
        query = query.join(Asset.make_model).filter(Asset.make_model.has(asset_type_id=asset_type_id))
    
    # Order by creation date (newest first)
    query = query.order_by(Asset.created_at.desc())
    
    # Pagination
    assets = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Get filter options
    asset_types = AssetType.query.all()
    locations = MajorLocation.query.all()
    make_models = MakeModel.query.all()
    
    logger.info(f"Assets list returned {assets.total} assets (page {page})")
    
    return render_template('core/assets/list.html', 
                         assets=assets,
                         asset_types=asset_types,
                         locations=locations,
                         make_models=make_models,
                         current_filters={
                             'asset_type_id': asset_type_id, 
                             'location_id': location_id,
                             'make_model_id': make_model_id,
                             'status': status,
                             'serial_number': serial_number,
                             'name': name
                         })

@bp.route('/assets/<int:asset_id>')
@login_required
def detail(asset_id):
    """View individual asset details"""
    logger.debug(f"User {current_user.username} accessing asset detail for asset ID: {asset_id}")
    
    asset = Asset.query.get_or_404(asset_id)
    
    # Get related data through relationships
    asset_type_id = asset.asset_type_id  # Use the property
    make_model = asset.make_model  # Use the relationship
    location = asset.major_location  # Use the relationship
    
    # Get asset type object if needed
    asset_type = None
    if asset_type_id:
        from app.models.core.asset_type import AssetType
        asset_type = AssetType.query.get(asset_type_id)
    
    # Get asset events
    events = asset.events.order_by(Event.timestamp.desc()).limit(10).all()
    
    logger.info(f"Asset detail accessed - Asset: {asset.name} (ID: {asset_id}), Type: {asset_type.name if asset_type else 'None'}")
    
    return render_template('core/assets/detail.html', 
                         asset=asset,
                         asset_type=asset_type,
                         make_model=make_model,
                         location=location,
                         events=events)

@bp.route('/assets/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create new asset using AssetFactory"""
    if request.method == 'POST':
        try:
            # Gather form data
            asset_data = {
                'name': request.form.get('name'),
                'serial_number': request.form.get('serial_number'),
                'status': request.form.get('status', 'Active'),
                'major_location_id': request.form.get('major_location_id', type=int),
                'make_model_id': request.form.get('make_model_id', type=int),
                'meter1': request.form.get('meter1', type=float),
                'meter2': request.form.get('meter2', type=float),
                'meter3': request.form.get('meter3', type=float),
                'meter4': request.form.get('meter4', type=float)
            }
            
            # Use AssetFactory to create the asset
            asset = AssetFactory.create_asset(
                created_by_id=current_user.id,
                commit=True,
                **asset_data
            )
            
            flash('Asset created successfully', 'success')
            logger.info(f"User {current_user.username} created asset: {asset.name} (ID: {asset.id})")
            return redirect(url_for('core_assets.detail', asset_id=asset.id))
            
        except ValueError as e:
            flash(str(e), 'error')
            logger.warning(f"Asset creation failed: {e}")
        except Exception as e:
            flash(f'Error creating asset: {str(e)}', 'error')
            logger.error(f"Unexpected error creating asset: {e}")
            db.session.rollback()
    
    # Get form options
    locations = MajorLocation.query.all()
    make_models = MakeModel.query.all()
    
    return render_template('core/assets/create.html', 
                         locations=locations,
                         make_models=make_models)

@bp.route('/assets/<int:asset_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(asset_id):
    """Edit asset using AssetFactory"""
    asset = Asset.query.get_or_404(asset_id)
    
    if request.method == 'POST':
        try:
            # Gather update data
            update_data = {
                'name': request.form.get('name'),
                'serial_number': request.form.get('serial_number'),
                'status': request.form.get('status'),
                'major_location_id': request.form.get('major_location_id', type=int),
                'make_model_id': request.form.get('make_model_id', type=int),
                'meter1': request.form.get('meter1', type=float),
                'meter2': request.form.get('meter2', type=float),
                'meter3': request.form.get('meter3', type=float),
                'meter4': request.form.get('meter4', type=float)
            }
            
            # Use AssetFactory to update the asset
            AssetFactory.update_asset(
                asset=asset,
                updated_by_id=current_user.id,
                commit=True,
                **update_data
            )
            
            flash('Asset updated successfully', 'success')
            logger.info(f"User {current_user.username} updated asset: {asset.name} (ID: {asset.id})")
            return redirect(url_for('core_assets.detail', asset_id=asset.id))
            
        except ValueError as e:
            flash(str(e), 'error')
            logger.warning(f"Asset update failed: {e}")
        except Exception as e:
            flash(f'Error updating asset: {str(e)}', 'error')
            logger.error(f"Unexpected error updating asset: {e}")
            db.session.rollback()
    
    # Get form options
    locations = MajorLocation.query.all()
    make_models = MakeModel.query.all()
    
    return render_template('core/assets/edit.html', 
                         asset=asset,
                         locations=locations,
                         make_models=make_models)

@bp.route('/assets/<int:asset_id>/delete', methods=['POST'])
@login_required
def delete(asset_id):
    """Delete asset"""
    asset = Asset.query.get_or_404(asset_id)
    
    # Check if asset has events
    if Event.query.filter_by(asset_id=asset.id).count() > 0:
        flash('Cannot delete asset with events', 'error')
        return redirect(url_for('core_assets.detail', asset_id=asset.id))
    
    db.session.delete(asset)
    db.session.commit()
    
    flash('Asset deleted successfully', 'success')
    return redirect(url_for('core_assets.list'))

@bp.route('/assets/<int:asset_id>/all-details')
@login_required
def all_details(asset_id):
    """View all detail records for an asset using the new template structure"""
    asset = Asset.query.get_or_404(asset_id)
    
    # Get asset detail records using the new structure
    from app.models.assets.asset_details.purchase_info import PurchaseInfo
    from app.models.assets.asset_details.vehicle_registration import VehicleRegistration
    from app.models.assets.asset_details.toyota_warranty_receipt import ToyotaWarrantyReceipt
    
    # Get all asset detail records for this asset
    asset_details = {}
    asset_details['purchase_info'] = PurchaseInfo.query.filter_by(asset_id=asset_id).all()
    asset_details['vehicle_registration'] = VehicleRegistration.query.filter_by(asset_id=asset_id).all()
    asset_details['toyota_warranty_receipt'] = ToyotaWarrantyReceipt.query.filter_by(asset_id=asset_id).all()
    
    # Get model detail records if asset has a make_model
    model_details = {}
    if asset.make_model_id:
        from app.models.assets.model_details.emissions_info import EmissionsInfo
        from app.models.assets.model_details.model_info import ModelInfo
        
        model_details['emissions_info'] = EmissionsInfo.query.filter_by(make_model_id=asset.make_model_id).all()
        model_details['model_info'] = ModelInfo.query.filter_by(make_model_id=asset.make_model_id).all()
    
    # Get configuration templates to show what detail tables are available
    asset_type_configs = []
    model_type_configs = []
    
    if asset.asset_type_id:
        asset_type_configs = AssetDetailTemplateByAssetType.query.filter_by(asset_type_id=asset.asset_type_id).all()
    
    if asset.make_model_id:
        model_type_configs = AssetDetailTemplateByModelType.query.filter_by(make_model_id=asset.make_model_id).all()
    
    return render_template('core/assets/all_details.html',
                         asset=asset,
                         asset_details=asset_details,
                         model_details=model_details,
                         asset_type_configs=asset_type_configs,
                         model_type_configs=model_type_configs)

@bp.route('/assets/details-card')
@bp.route('/assets/details-card/<int:asset_id>')
@login_required
def asset_details_card(asset_id=None):
    """HTMX endpoint for asset details card"""
    if asset_id is None:
        # Return empty state
        return render_template('core/assets/asset_details_card.html', asset=None)
    
    asset = Asset.query.get_or_404(asset_id)
    
    # Get related data
    asset_type_id = asset.asset_type_id
    make_model = asset.make_model
    location = asset.major_location
    
    # Get asset type object if needed
    asset_type = None
    if asset_type_id:
        from app.models.core.asset_type import AssetType
        asset_type = AssetType.query.get(asset_type_id)
    
    # Get recent events
    from app.models.core.event import Event
    events = asset.events.order_by(Event.timestamp.desc()).limit(5).all()
    
    # Get detail records count using the new structure
    from app.models.assets.asset_details.purchase_info import PurchaseInfo
    from app.models.assets.asset_details.vehicle_registration import VehicleRegistration
    from app.models.assets.asset_details.toyota_warranty_receipt import ToyotaWarrantyReceipt
    
    detail_count = 0
    detail_count += PurchaseInfo.query.filter_by(asset_id=asset_id).count()
    detail_count += VehicleRegistration.query.filter_by(asset_id=asset_id).count()
    detail_count += ToyotaWarrantyReceipt.query.filter_by(asset_id=asset_id).count()
    
    # Add model details if asset has a make_model
    if asset.make_model_id:
        from app.models.assets.model_details.emissions_info import EmissionsInfo
        from app.models.assets.model_details.model_info import ModelInfo
        
        detail_count += EmissionsInfo.query.filter_by(make_model_id=asset.make_model_id).count()
        detail_count += ModelInfo.query.filter_by(make_model_id=asset.make_model_id).count()
    
    return render_template('core/assets/asset_details_card.html',
                         asset=asset,
                         asset_type=asset_type,
                         make_model=make_model,
                         location=location,
                         events=events,
                         detail_count=detail_count) 
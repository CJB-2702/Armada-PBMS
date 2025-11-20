"""
Asset management routes
CRUD operations for Asset model
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.data.core.asset_info.asset import Asset
from app.data.core.event_info.event import Event
from app.buisness.assets.factories.asset_factory import AssetFactory
from app.buisness.core.asset_context import AssetContext as CoreAssetContext
from app.buisness.assets.asset_details_context import AssetDetailsContext
from app.services.core.asset_service import AssetService
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
    
    # Use service to get list data
    assets, filter_options, current_filters = AssetService.get_list_data(
        request=request,
        page=page,
        per_page=per_page
    )
    
    logger.info(f"Assets list returned {assets.total} assets (page {page})")
    
    return render_template('core/assets/list.html', 
                         assets=assets,
                         asset_types=filter_options['asset_types'],
                         locations=filter_options['locations'],
                         make_models=filter_options['make_models'],
                         current_filters=current_filters)

@bp.route('/assets/<int:asset_id>')
@login_required
def detail(asset_id):
    """View individual asset details"""
    logger.debug(f"User {current_user.username} accessing asset detail for asset ID: {asset_id}")
    
    asset_context = CoreAssetContext(asset_id)
    
    logger.info(f"Asset detail accessed - Asset: {asset_context.asset.name} (ID: {asset_id}), Type: {asset_context.asset_type.name if asset_context.asset_type else 'None'}")
    
    # Get recent events from service (presentation-specific query)
    events = AssetService.get_recent_events(asset_id, limit=10)
    
    return render_template('core/assets/detail.html', 
                         asset=asset_context.asset,
                         asset_type=asset_context.asset_type,
                         make_model=asset_context.make_model,
                         location=asset_context.major_location,
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
    
    # Get form options from service
    form_options = AssetService.get_form_options()
    
    return render_template('core/assets/create.html', 
                         locations=form_options['locations'],
                         make_models=form_options['make_models'])

# ROUTE_TYPE: SIMPLE_CRUD (EDIT)
# EXCEPTION: Direct ORM usage allowed for simple EDIT operations on Asset
# This route performs basic update operations with minimal business logic.
# Rationale: Using AssetFactory for validation is acceptable, but direct ORM would also be fine for simple edits.
# NOTE: CREATE/DELETE operations should use domain managers - see create() and delete() routes
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
    
    # Get form options from service
    form_options = AssetService.get_form_options()
    
    return render_template('core/assets/edit.html', 
                         asset=asset,
                         locations=form_options['locations'],
                         make_models=form_options['make_models'])

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
    asset_context = AssetDetailsContext(asset_id)
    
    # Get details grouped by type using service (presentation-specific)
    from app.services.assets.asset_detail_service import AssetDetailService
    asset_details = AssetDetailService.get_asset_details_by_type(asset_id)
    model_details = AssetDetailService.get_model_details_by_type(asset_id)
    
    # Get configurations using service (presentation-specific)
    asset_type_configs = AssetDetailService.get_asset_type_configs(asset_context.asset_type_id) if asset_context.asset_type_id else []
    model_type_configs = AssetDetailService.get_model_type_configs(asset_context.asset.make_model_id) if asset_context.asset.make_model_id else []
    
    return render_template('core/assets/all_details.html',
                         asset=asset_context.asset,
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
    
    asset_context = AssetDetailsContext(asset_id)
    
    # Get recent events from service (presentation-specific query)
    events = AssetService.get_recent_events(asset_id, limit=5)
    
    return render_template('core/assets/asset_details_card.html',
                         asset=asset_context.asset,
                         asset_type=asset_context.asset_type,
                         make_model=asset_context.make_model,
                         location=asset_context.major_location,
                         events=events,
                         detail_count=asset_context.detail_count) 
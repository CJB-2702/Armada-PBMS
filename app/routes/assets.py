from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.BaseModels.Asset import AbstractAsset, AssetTypes
from app.models.BaseModels.Event import Event
from app.extensions import db
from app.utils.logger import get_logger

logger = get_logger()

bp = Blueprint('assets', __name__, url_prefix='/assets')

def log_asset_event(action, asset, extra_info=None):
    title = f"Asset {action}: {asset.common_name} (UID: {asset.UID})"
    description = (
        f"Asset {action.lower()}\n"
        f"UID: {asset.UID}\n"
        f"Common Name: {asset.common_name}\n"
        f"Type: {asset.asset_type}\n"
        f"Description: {asset.description}\n"
        f"Status: {asset.status}"
    )
    if extra_info:
        description += f"\n{extra_info}"
    event = Event(
        title=title,
        description=description,
        event_type='SYSTEM',
        status='completed',
        created_by=1
    )
    db.session.add(event)

@bp.route('/')
def index():
    try:
        assets = AbstractAsset.query.all()
        return render_template('assets/index.html', assets=assets)
    except Exception as e:
        logger.error(f"Error fetching assets: {str(e)}")
        flash('Error loading assets', 'error')
        return render_template('assets/index.html', assets=[])

@bp.route('/<string:uid>')
def view_asset(uid):
    asset = AbstractAsset.query.filter_by(UID=uid).first_or_404()
    return render_template('assets/view_asset.html', asset=asset)

@bp.route('/create', methods=['GET', 'POST'])
def create_asset():
    asset_types = AssetTypes.query.all()
    if request.method == 'POST':
        try:
            UID = request.form.get('UID')
            asset_type = request.form.get('asset_type')
            common_name = request.form.get('common_name')
            description = request.form.get('description')
            status = request.form.get('status', 'active')
            if not UID or not asset_type or not common_name or not status:
                flash('All fields are required', 'error')
                return render_template('assets/create_asset.html', asset_types=asset_types)
            new_asset = AbstractAsset(
                UID=UID,
                asset_type=asset_type,
                common_name=common_name,
                description=description,
                status=status,
                created_by=1
            )
            db.session.add(new_asset)
            db.session.commit()
            log_asset_event("Created", new_asset)
            db.session.commit()
            logger.info(f"New asset created: {common_name}")
            flash('Asset created successfully', 'success')
            return redirect(url_for('assets.view_asset', uid=new_asset.UID))
        except Exception as e:
            logger.error(f"Error creating asset: {str(e)}")
            flash('Error creating asset', 'error')
            return render_template('assets/create_asset.html', asset_types=asset_types)
    return render_template('assets/create_asset.html', asset_types=asset_types)

@bp.route('/<string:uid>/edit', methods=['GET', 'POST'])
def edit_asset(uid):
    asset = AbstractAsset.query.filter_by(UID=uid).first_or_404()
    asset_types = AssetTypes.query.all()
    if request.method == 'POST':
        try:
            asset_type = request.form.get('asset_type')
            common_name = request.form.get('common_name')
            description = request.form.get('description')
            status = request.form.get('status')
            if not asset_type or not common_name or not status:
                return render_template('assets/edit_asset.html', asset=asset, asset_types=asset_types, error='All fields are required')
            asset.asset_type = asset_type
            asset.common_name = common_name
            asset.description = description
            asset.status = status
            db.session.commit()
            log_asset_event("Edited", asset)
            db.session.commit()
            logger.info(f"Asset {uid} updated")
            flash('Asset updated successfully', 'success')
            return redirect(url_for('assets.view_asset', uid=asset.UID))
        except Exception as e:
            logger.error(f"Error editing asset {uid}: {str(e)}")
            flash('Error updating asset', 'error')
            return render_template('assets/edit_asset.html', asset=asset, asset_types=asset_types, error='Error updating asset')
    return render_template('assets/edit_asset.html', asset=asset, asset_types=asset_types)

@bp.route('/<string:uid>/delete', methods=['POST'])
def delete_asset(uid):
    asset = AbstractAsset.query.filter_by(UID=uid).first_or_404()
    try:
        db.session.delete(asset)
        log_asset_event("Deleted", asset)
        db.session.commit()
        logger.info(f"Asset {uid} deleted.")
        flash('Asset deleted successfully.', 'success')
        return redirect(url_for('assets.index'))
    except Exception as e:
        logger.error(f"Error deleting asset {uid}: {str(e)}")
        flash('Error deleting asset.', 'error')
        return redirect(url_for('assets.edit_asset', uid=uid))

@bp.route('/asset-types')
def asset_types_index():
    """Display all asset types"""
    try:
        asset_types = AssetTypes.query.all()
        return render_template('asset_types/index.html', asset_types=asset_types)
    except Exception as e:
        logger.error(f"Error rendering asset types index: {str(e)}")
        return "Error loading asset types", 500

@bp.route('/asset-types/create', methods=['GET', 'POST'])
def create_asset_type():
    """Create a new asset type"""
    if request.method == 'POST':
        try:
            value = request.form.get('value')
            description = request.form.get('description')
            
            if not value:
                flash('Asset type name is required', 'error')
                return render_template('asset_types/create.html')
            
            # Check if asset type already exists
            existing_type = AssetTypes.query.filter_by(value=value).first()
            if existing_type:
                flash(f'Asset type "{value}" already exists', 'error')
                return render_template('asset_types/create.html')
            
            new_asset_type = AssetTypes(
                value=value,
                description=description,
                created_by=1
            )
            db.session.add(new_asset_type)
            db.session.commit()
            
            logger.info(f"New asset type created: {value}")
            flash('Asset type created successfully', 'success')
            return redirect(url_for('assets.asset_types_index'))
            
        except Exception as e:
            logger.error(f"Error creating asset type: {str(e)}")
            flash('Error creating asset type', 'error')
            return render_template('asset_types/create.html')
    
    return render_template('asset_types/create.html')

@bp.route('/asset-types/<int:type_id>/edit', methods=['GET', 'POST'])
def edit_asset_type(type_id):
    """Edit an asset type"""
    asset_type = AssetTypes.query.get_or_404(type_id)
    
    if request.method == 'POST':
        try:
            value = request.form.get('value')
            description = request.form.get('description')
            
            if not value:
                flash('Asset type name is required', 'error')
                return render_template('asset_types/edit.html', asset_type=asset_type)
            
            # Check if the new name conflicts with existing types (excluding current)
            existing_type = AssetTypes.query.filter(
                AssetTypes.value == value,
                AssetTypes.row_id != type_id
            ).first()
            if existing_type:
                flash(f'Asset type "{value}" already exists', 'error')
                return render_template('asset_types/edit.html', asset_type=asset_type)
            
            asset_type.value = value
            asset_type.description = description
            asset_type.update(updated_by=1)
            db.session.commit()
            
            logger.info(f"Asset type updated: {value}")
            flash('Asset type updated successfully', 'success')
            return redirect(url_for('assets.asset_types_index'))
            
        except Exception as e:
            logger.error(f"Error updating asset type {type_id}: {str(e)}")
            flash('Error updating asset type', 'error')
            return render_template('asset_types/edit.html', asset_type=asset_type)
    
    return render_template('asset_types/edit.html', asset_type=asset_type)

@bp.route('/asset-types/<int:type_id>/delete', methods=['POST'])
def delete_asset_type(type_id):
    """Delete an asset type if it's not protected"""
    asset_type = AssetTypes.query.get_or_404(type_id)
    
    try:
        # Check if the type can be deleted
        if not asset_type.can_be_deleted():
            flash(f'Cannot delete protected asset type "{asset_type.value}". This is a system-required type.', 'error')
            return redirect(url_for('assets.asset_types_index'))
        
        # Check if any assets are using this type
        from app.models.BaseModels.Asset import AbstractAsset
        assets_using_type = AbstractAsset.query.filter_by(asset_type=asset_type.value).count()
        if assets_using_type > 0:
            flash(f'Cannot delete asset type "{asset_type.value}" because {assets_using_type} asset(s) are using it.', 'error')
            return redirect(url_for('assets.asset_types_index'))
        
        type_name = asset_type.value
        db.session.delete(asset_type)
        db.session.commit()
        
        logger.info(f"Asset type deleted: {type_name}")
        flash(f'Asset type "{type_name}" deleted successfully', 'success')
        return redirect(url_for('assets.asset_types_index'))
        
    except Exception as e:
        logger.error(f"Error deleting asset type {type_id}: {str(e)}")
        flash('Error deleting asset type', 'error')
        return redirect(url_for('assets.asset_types_index')) 
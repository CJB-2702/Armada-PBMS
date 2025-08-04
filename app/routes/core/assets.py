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
from app import db

bp = Blueprint('assets', __name__)

@bp.route('/assets')
@login_required
def list():
    """List all assets with basic filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Basic filtering
    asset_type_id = request.args.get('asset_type_id', type=int)
    location_id = request.args.get('location_id', type=int)
    make_model_id = request.args.get('make_model_id', type=int)
    status = request.args.get('status')
    serial_number = request.args.get('serial_number')
    name = request.args.get('name')
    
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
    asset = Asset.query.get_or_404(asset_id)
    
    # Get related data through relationships
    asset_type = asset.asset_type  # Use the property
    make_model = asset.make_model  # Use the relationship
    location = asset.major_location  # Use the relationship
    
    # Get asset events
    events = asset.events.order_by(Event.timestamp.desc()).limit(10).all()
    
    return render_template('core/assets/detail.html', 
                         asset=asset,
                         asset_type=asset_type,
                         make_model=make_model,
                         location=location,
                         events=events)

@bp.route('/assets/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create new asset"""
    if request.method == 'POST':
        # Validate form data
        name = request.form.get('name')
        serial_number = request.form.get('serial_number')
        status = request.form.get('status', 'Active')
        major_location_id = request.form.get('major_location_id', type=int)
        make_model_id = request.form.get('make_model_id', type=int)
        meter1 = request.form.get('meter1', type=float)
        meter2 = request.form.get('meter2', type=float)
        meter3 = request.form.get('meter3', type=float)
        meter4 = request.form.get('meter4', type=float)
        
        # Check if serial number already exists
        if Asset.query.filter_by(serial_number=serial_number).first():
            flash('Serial number already exists', 'error')
            return render_template('core/assets/create.html')
        
        # Create new asset
        asset = Asset(
            name=name,
            serial_number=serial_number,
            status=status,
            major_location_id=major_location_id,
            make_model_id=make_model_id,
            meter1=meter1,
            meter2=meter2,
            meter3=meter3,
            meter4=meter4,
            created_by_id=current_user.id,
            updated_by_id=current_user.id
        )
        
        db.session.add(asset)
        db.session.commit()
        
        flash('Asset created successfully', 'success')
        return redirect(url_for('core_assets.detail', asset_id=asset.id))
    
    # Get form options
    locations = MajorLocation.query.all()
    make_models = MakeModel.query.all()
    
    return render_template('core/assets/create.html', 
                         locations=locations,
                         make_models=make_models)

@bp.route('/assets/<int:asset_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(asset_id):
    """Edit asset"""
    asset = Asset.query.get_or_404(asset_id)
    
    if request.method == 'POST':
        # Validate form data
        name = request.form.get('name')
        serial_number = request.form.get('serial_number')
        status = request.form.get('status')
        major_location_id = request.form.get('major_location_id', type=int)
        make_model_id = request.form.get('make_model_id', type=int)
        meter1 = request.form.get('meter1', type=float)
        meter2 = request.form.get('meter2', type=float)
        meter3 = request.form.get('meter3', type=float)
        meter4 = request.form.get('meter4', type=float)
        
        # Check if serial number already exists (excluding current asset)
        existing_asset = Asset.query.filter_by(serial_number=serial_number).first()
        if existing_asset and existing_asset.id != asset.id:
            flash('Serial number already exists', 'error')
            return render_template('core/assets/edit.html', asset=asset)
        
        # Update asset
        asset.name = name
        asset.serial_number = serial_number
        asset.status = status
        asset.major_location_id = major_location_id
        asset.make_model_id = make_model_id
        asset.meter1 = meter1
        asset.meter2 = meter2
        asset.meter3 = meter3
        asset.meter4 = meter4
        asset.updated_by_id = current_user.id
        
        db.session.commit()
        
        flash('Asset updated successfully', 'success')
        return redirect(url_for('core_assets.detail', asset_id=asset.id))
    
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
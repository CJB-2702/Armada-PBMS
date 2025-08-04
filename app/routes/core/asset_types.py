"""
Asset Type management routes
CRUD operations for AssetType model
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.models.core.asset_type import AssetType
from app.models.core.make_model import MakeModel
from app.models.core.asset import Asset
from app import db

bp = Blueprint('asset_types', __name__)

@bp.route('/asset-types')
@login_required
def list():
    """List all asset types"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Basic filtering
    category = request.args.get('category')
    active = request.args.get('active')
    
    query = AssetType.query
    
    if category:
        query = query.filter(AssetType.category == category)
    
    if active is not None:
        query = query.filter(AssetType.is_active == (active.lower() == 'true'))
    
    # Order by name
    query = query.order_by(AssetType.name)
    
    # Pagination
    asset_types = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Get unique categories for filter
    categories = db.session.query(AssetType.category).distinct().all()
    categories = [cat[0] for cat in categories if cat[0]]
    
    # Pre-calculate asset counts for each asset type to avoid N+1 queries
    asset_type_counts = {}
    make_model_counts = {}
    
    for asset_type in asset_types.items:
        # Count make/models for this asset type
        make_model_count = MakeModel.query.filter_by(asset_type_id=asset_type.id).count()
        make_model_counts[asset_type.id] = make_model_count
        
        # Count assets for this asset type (through make/models)
        asset_count = db.session.query(Asset).join(MakeModel).filter(MakeModel.asset_type_id == asset_type.id).count()
        asset_type_counts[asset_type.id] = asset_count
    
    return render_template('core/asset_types/list.html', 
                         asset_types=asset_types,
                         categories=categories,
                         asset_type_counts=asset_type_counts,
                         make_model_counts=make_model_counts)

@bp.route('/asset-types/<int:asset_type_id>')
@login_required
def detail(asset_type_id):
    """View asset type details"""
    asset_type = AssetType.query.get_or_404(asset_type_id)
    
    # Get make/models of this type
    make_models = asset_type.make_models.order_by(MakeModel.make, MakeModel.model).all()
    
    # Get assets of this type (through make/models)
    assets = []
    for make_model in make_models:
        assets.extend(make_model.assets)
    
    return render_template('core/asset_types/detail.html', 
                         asset_type=asset_type,
                         make_models=make_models,
                         assets=assets,
                         Asset=Asset,
                         MakeModel=MakeModel)

@bp.route('/asset-types/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create new asset type"""
    if request.method == 'POST':
        # Validate form data
        name = request.form.get('name')
        description = request.form.get('description')
        category = request.form.get('category')
        is_active = request.form.get('is_active') == 'on'
        
        # Check if name already exists
        if AssetType.query.filter_by(name=name).first():
            flash('Asset type name already exists', 'error')
            return render_template('core/asset_types/create.html')
        
        # Create new asset type
        asset_type = AssetType(
            name=name,
            description=description,
            category=category,
            is_active=is_active,
            created_by_id=current_user.id,
            updated_by_id=current_user.id
        )
        
        db.session.add(asset_type)
        db.session.commit()
        
        flash('Asset type created successfully', 'success')
        return redirect(url_for('asset_types.detail', asset_type_id=asset_type.id))
    
    return render_template('core/asset_types/create.html')

@bp.route('/asset-types/<int:asset_type_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(asset_type_id):
    """Edit asset type"""
    asset_type = AssetType.query.get_or_404(asset_type_id)
    
    if request.method == 'POST':
        # Validate form data
        name = request.form.get('name')
        description = request.form.get('description')
        category = request.form.get('category')
        is_active = request.form.get('is_active') == 'on'
        
        # Check if name already exists (excluding current asset type)
        existing_asset_type = AssetType.query.filter_by(name=name).first()
        if existing_asset_type and existing_asset_type.id != asset_type.id:
            flash('Asset type name already exists', 'error')
            return render_template('core/asset_types/edit.html', asset_type=asset_type, Asset=Asset, MakeModel=MakeModel)
        
        # Update asset type
        asset_type.name = name
        asset_type.description = description
        asset_type.category = category
        asset_type.is_active = is_active
        asset_type.updated_by_id = current_user.id
        
        db.session.commit()
        
        flash('Asset type updated successfully', 'success')
        return redirect(url_for('asset_types.detail', asset_type_id=asset_type.id))
    
    return render_template('core/asset_types/edit.html', asset_type=asset_type, Asset=Asset, MakeModel=MakeModel)

@bp.route('/asset-types/<int:asset_type_id>/delete', methods=['POST'])
@login_required
def delete(asset_type_id):
    """Delete asset type"""
    asset_type = AssetType.query.get_or_404(asset_type_id)
    
    # Check if asset type has make/models
    if MakeModel.query.filter_by(asset_type_id=asset_type.id).count() > 0:
        flash('Cannot delete asset type with make/models', 'error')
        return redirect(url_for('asset_types.detail', asset_type_id=asset_type.id))
    
    db.session.delete(asset_type)
    db.session.commit()
    
    flash('Asset type deleted successfully', 'success')
    return redirect(url_for('asset_types.list')) 
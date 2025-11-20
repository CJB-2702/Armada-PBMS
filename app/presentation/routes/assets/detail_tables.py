"""
Asset detail table routes
Routes for managing asset-specific detail tables
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, jsonify
from app.logger import get_logger
from flask_login import login_required, current_user
from app.data.core.asset_info.asset import Asset
from app.buisness.assets.detail_table_context import DetailTableContext
from app.services.assets.asset_detail_service import AssetDetailService
from app import db
from pathlib import Path

bp = Blueprint('detail_tables', __name__)
logger = get_logger("asset_management.routes.bp")

def get_detail_table_config(detail_type):
    """Get configuration for a detail table type"""
    return AssetDetailService.get_detail_table_config(detail_type)

# Generic CRUD routes for all detail table types

@bp.route('/<detail_type>/')
@login_required
def list(detail_type):
    """List all records for a detail table type"""
    config = get_detail_table_config(detail_type)
    if not config:
        abort(404)
    
    # Use service to get list data with filters and form options
    records, form_options = AssetDetailService.get_list_data(detail_type, request)
    
    # Get filter parameters for template
    asset_id_filter = request.args.get('asset_id', type=int)
    model_id_filter = request.args.get('model_id', type=int)
    
    return render_template('assets/detail_tables/list.html',
                         detail_type=detail_type,
                         config=config,
                         records=records,
                         asset_options=form_options['asset_options'],
                         model_options=form_options['model_options'],
                         current_asset_filter=asset_id_filter,
                         current_model_filter=model_id_filter)

@bp.route('/<detail_type>/create', methods=['GET', 'POST'])
@login_required
def create(detail_type):
    """Create new record for a detail table type"""
    config = get_detail_table_config(detail_type)
    if not config:
        abort(404)
    
    # Get form options from service
    form_options = AssetDetailService.get_form_options()
    
    if request.method == 'POST':
        try:
            # Gather form data
            record_data = {}
            for field in config['fields']:
                value = request.form.get(field)
                if value:
                    record_data[field] = value
            
            # Asset selection is required
            asset_id = request.form.get('asset_id', type=int)
            if not asset_id:
                flash('Asset selection is required', 'error')
                return render_template('assets/detail_tables/create.html',
                                     detail_type=detail_type,
                                     config=config,
                                     asset_options=asset_options)
            
            # Create record using DetailTableContext
            record = DetailTableContext.create_detail_record(
                detail_type=detail_type,
                asset_id=asset_id,
                user_id=current_user.id,
                **record_data
            )
            db.session.commit()
            
            flash(f'{config["name"]} created successfully', 'success')
            return redirect(url_for('assets.detail_tables.list', detail_type=detail_type))
        except Exception as e:
            flash(f'Error creating {config["name"]}: {str(e)}', 'error')
            logger.error(f"Error creating detail record: {e}")
            db.session.rollback()
    
    return render_template('assets/detail_tables/create.html',
                         detail_type=detail_type,
                         config=config,
                         asset_options=form_options['asset_options'])

@bp.route('/<detail_type>/<int:id>/')
@login_required
def detail(detail_type, id):
    """View details of a specific record"""
    config = get_detail_table_config(detail_type)
    if not config:
        abort(404)
    
    # Use service to get detail record
    record = AssetDetailService.get_detail_record(detail_type, id)
    if not record:
        abort(404)
    
    return render_template('assets/detail_tables/detail.html',
                         detail_type=detail_type,
                         config=config,
                         record=record)

@bp.route('/<detail_type>/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(detail_type, id):
    """Edit a specific record"""
    config = get_detail_table_config(detail_type)
    if not config:
        abort(404)
    
    # Use service to get detail record
    record = AssetDetailService.get_detail_record(detail_type, id)
    if not record:
        abort(404)
    
    # Get form options from service
    form_options = AssetDetailService.get_form_options()
    
    if request.method == 'POST':
        try:
            # Gather update data
            update_data = {}
            for field in config['fields']:
                if field in request.form:
                    update_data[field] = request.form.get(field)
            
            # Update asset_id if present
            asset_id = request.form.get('asset_id', type=int)
            if asset_id:
                update_data['asset_id'] = asset_id
            
            # Update record using DetailTableContext
            DetailTableContext.update_detail_record(
                record=record,
                user_id=current_user.id,
                **update_data
            )
            db.session.commit()
            
            flash(f'{config["name"]} updated successfully', 'success')
            return redirect(url_for('assets.detail_tables.detail', detail_type=detail_type, id=id))
        except Exception as e:
            flash(f'Error updating {config["name"]}: {str(e)}', 'error')
            logger.error(f"Error updating detail record: {e}")
            db.session.rollback()
    
    return render_template('assets/detail_tables/edit.html',
                         detail_type=detail_type,
                         config=config,
                         record=record,
                         asset_options=form_options['asset_options'])

@bp.route('/<detail_type>/<int:id>/delete', methods=['POST'])
@login_required
def delete(detail_type, id):
    """Delete a specific record"""
    config = get_detail_table_config(detail_type)
    if not config:
        abort(404)
    
    # Use service to get detail record
    record = AssetDetailService.get_detail_record(detail_type, id)
    if not record:
        abort(404)
    
    try:
        DetailTableContext.delete_detail_record(record)
        db.session.commit()
        flash(f'{config["name"]} deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting {config["name"]}: {str(e)}', 'error')
        logger.error(f"Error deleting detail record: {e}")
        db.session.rollback()
    
    return redirect(url_for('assets.detail_tables.list', detail_type=detail_type))

# Asset-specific routes (for backward compatibility)

# ROUTE_TYPE: SIMPLE_CRUD (GET)
# EXCEPTION: Direct ORM usage allowed for backward-compatibility routes.
# This route duplicates functionality of generic routes above - legacy route.
# Rationale: Exception for backward-compatibility routes that duplicate generic route functionality.
# NOTE: CREATE/DELETE operations should use domain managers - see generic routes above
@bp.route('/assets/<int:asset_id>/purchase-info')
@login_required
def purchase_info(asset_id):
    """View purchase info for asset"""
    asset = Asset.query.get_or_404(asset_id)
    purchase_info = PurchaseInfo.query.filter_by(asset_id=asset_id).first()
    
    return render_template('assets/detail_tables/purchase_info.html', 
                         asset=asset,
                         purchase_info=purchase_info)

# ROUTE_TYPE: SIMPLE_CRUD (EDIT) - EXCEPTION for backward-compatibility
# EXCEPTION: Direct ORM usage allowed for backward-compatibility routes.
# This route duplicates functionality of generic routes above - legacy route.
# Rationale: Exception for backward-compatibility routes that duplicate generic route functionality.
# NOTE: CREATE/DELETE operations should use domain managers - see generic routes above
@bp.route('/assets/<int:asset_id>/purchase-info/edit', methods=['GET', 'POST'])
@login_required
def edit_purchase_info(asset_id):
    """Edit purchase info for asset"""
    asset = Asset.query.get_or_404(asset_id)
    purchase_info = PurchaseInfo.query.filter_by(asset_id=asset_id).first()
    
    if request.method == 'POST':
        # Validate form data
        purchase_date = request.form.get('purchase_date')
        purchase_price = request.form.get('purchase_price', type=float)
        vendor = request.form.get('vendor')
        warranty_expiry = request.form.get('warranty_expiry')
        notes = request.form.get('notes')
        
        if purchase_info:
            # Update existing
            purchase_info.purchase_date = purchase_date
            purchase_info.purchase_price = purchase_price
            purchase_info.vendor = vendor
            purchase_info.warranty_expiry = warranty_expiry
            purchase_info.notes = notes
            purchase_info.updated_by_id = current_user.id
        else:
            # Create new
            purchase_info = PurchaseInfo(
                asset_id=asset_id,
                purchase_date=purchase_date,
                purchase_price=purchase_price,
                vendor=vendor,
                warranty_expiry=warranty_expiry,
                notes=notes,
                created_by_id=current_user.id,
                updated_by_id=current_user.id
            )
            db.session.add(purchase_info)
        
        db.session.commit()
        flash('Purchase info updated successfully', 'success')
        return redirect(url_for('assets.detail_tables.purchase_info', asset_id=asset_id))
    
    return render_template('assets/detail_tables/edit_purchase_info.html', 
                         asset=asset,
                         purchase_info=purchase_info)

# ROUTE_TYPE: SIMPLE_CRUD (GET)
# EXCEPTION: Direct ORM usage allowed for backward-compatibility routes.
# This route duplicates functionality of generic routes above - legacy route.
# Rationale: Exception for backward-compatibility routes that duplicate generic route functionality.
# NOTE: CREATE/DELETE operations should use domain managers - see generic routes above
@bp.route('/assets/<int:asset_id>/vehicle-registration')
@login_required
def vehicle_registration(asset_id):
    """View vehicle registration for asset"""
    asset = Asset.query.get_or_404(asset_id)
    registration = VehicleRegistration.query.filter_by(asset_id=asset_id).first()
    
    return render_template('assets/detail_tables/vehicle_registration.html', 
                         asset=asset,
                         registration=registration)

# ROUTE_TYPE: SIMPLE_CRUD (EDIT) - EXCEPTION for backward-compatibility
# EXCEPTION: Direct ORM usage allowed for backward-compatibility routes.
# This route duplicates functionality of generic routes above - legacy route.
# Rationale: Exception for backward-compatibility routes that duplicate generic route functionality.
# NOTE: CREATE/DELETE operations should use domain managers - see generic routes above
@bp.route('/assets/<int:asset_id>/vehicle-registration/edit', methods=['GET', 'POST'])
@login_required
def edit_vehicle_registration(asset_id):
    """Edit vehicle registration for asset"""
    asset = Asset.query.get_or_404(asset_id)
    registration = VehicleRegistration.query.filter_by(asset_id=asset_id).first()
    
    if request.method == 'POST':
        # Validate form data
        license_plate = request.form.get('license_plate')
        registration_number = request.form.get('registration_number')
        registration_expiry = request.form.get('registration_expiry')
        vin = request.form.get('vin')
        state = request.form.get('state')
        insurance_provider = request.form.get('insurance_provider')
        insurance_policy_number = request.form.get('insurance_policy_number')
        insurance_expiry = request.form.get('insurance_expiry')
        
        if registration:
            # Update existing
            registration.license_plate = license_plate
            registration.registration_number = registration_number
            registration.registration_expiry = registration_expiry
            registration.vin = vin
            registration.state = state
            registration.insurance_provider = insurance_provider
            registration.insurance_policy_number = insurance_policy_number
            registration.insurance_expiry = insurance_expiry
            registration.updated_by_id = current_user.id
        else:
            # Create new
            registration = VehicleRegistration(
                asset_id=asset_id,
                license_plate=license_plate,
                registration_number=registration_number,
                registration_expiry=registration_expiry,
                vin=vin,
                state=state,
                insurance_provider=insurance_provider,
                insurance_policy_number=insurance_policy_number,
                insurance_expiry=insurance_expiry,
                created_by_id=current_user.id,
                updated_by_id=current_user.id
            )
            db.session.add(registration)
        
        db.session.commit()
        flash('Vehicle registration updated successfully', 'success')
        return redirect(url_for('assets.detail_tables.vehicle_registration', asset_id=asset_id))
    
    return render_template('assets/detail_tables/edit_vehicle_registration.html', 
                         asset=asset,
                         registration=registration)

# ROUTE_TYPE: SIMPLE_CRUD (GET)
# EXCEPTION: Direct ORM usage allowed for backward-compatibility routes.
# This route duplicates functionality of generic routes above - legacy route.
# Rationale: Exception for backward-compatibility routes that duplicate generic route functionality.
# NOTE: CREATE/DELETE operations should use domain managers - see generic routes above
@bp.route('/assets/<int:asset_id>/toyota-warranty')
@login_required
def toyota_warranty(asset_id):
    """View Toyota warranty info for asset"""
    asset = Asset.query.get_or_404(asset_id)
    warranty = ToyotaWarrantyReceipt.query.filter_by(asset_id=asset_id).first()
    
    return render_template('assets/detail_tables/toyota_warranty_receipt.html', 
                         asset=asset,
                         warranty=warranty)

# ROUTE_TYPE: SIMPLE_CRUD (EDIT) - EXCEPTION for backward-compatibility
# EXCEPTION: Direct ORM usage allowed for backward-compatibility routes.
# This route duplicates functionality of generic routes above - legacy route.
# Rationale: Exception for backward-compatibility routes that duplicate generic route functionality.
# NOTE: CREATE/DELETE operations should use domain managers - see generic routes above
@bp.route('/assets/<int:asset_id>/toyota-warranty/edit', methods=['GET', 'POST'])
@login_required
def edit_toyota_warranty(asset_id):
    """Edit Toyota warranty info for asset"""
    asset = Asset.query.get_or_404(asset_id)
    warranty = ToyotaWarrantyReceipt.query.filter_by(asset_id=asset_id).first()
    
    if request.method == 'POST':
        # Validate form data
        warranty_number = request.form.get('warranty_number')
        warranty_start_date = request.form.get('warranty_start_date')
        warranty_end_date = request.form.get('warranty_end_date')
        service_center = request.form.get('service_center')
        notes = request.form.get('notes')
        
        if warranty:
            # Update existing
            warranty.warranty_number = warranty_number
            warranty.warranty_start_date = warranty_start_date
            warranty.warranty_end_date = warranty_end_date
            warranty.service_center = service_center
            warranty.notes = notes
            warranty.updated_by_id = current_user.id
        else:
            # Create new
            warranty = ToyotaWarrantyReceipt(
                asset_id=asset_id,
                warranty_number=warranty_number,
                warranty_start_date=warranty_start_date,
                warranty_end_date=warranty_end_date,
                service_center=service_center,
                notes=notes,
                created_by_id=current_user.id,
                updated_by_id=current_user.id
            )
            db.session.add(warranty)
        
        db.session.commit()
        flash('Toyota warranty info updated successfully', 'success')
        return redirect(url_for('assets.detail_tables.toyota_warranty', asset_id=asset_id))
    
    return render_template('assets/detail_tables/edit_toyota_warranty_receipt.html', 
                         asset=asset,
                         warranty=warranty) 
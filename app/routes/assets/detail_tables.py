"""
Asset detail table routes
Routes for managing asset-specific detail tables
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.models.core.asset import Asset
from app.models.assets.asset_details.purchase_info import PurchaseInfo
from app.models.assets.asset_details.vehicle_registration import VehicleRegistration
from app.models.assets.asset_details.toyota_warranty_receipt import ToyotaWarrantyReceipt
from app import db

bp = Blueprint('detail_tables', __name__)

@bp.route('/assets/<int:asset_id>/purchase-info')
@login_required
def purchase_info(asset_id):
    """View purchase info for asset"""
    asset = Asset.query.get_or_404(asset_id)
    purchase_info = PurchaseInfo.query.filter_by(asset_id=asset_id).first()
    
    return render_template('assets/detail_tables/purchase_info.html', 
                         asset=asset,
                         purchase_info=purchase_info)

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

@bp.route('/assets/<int:asset_id>/vehicle-registration')
@login_required
def vehicle_registration(asset_id):
    """View vehicle registration for asset"""
    asset = Asset.query.get_or_404(asset_id)
    registration = VehicleRegistration.query.filter_by(asset_id=asset_id).first()
    
    return render_template('assets/detail_tables/vehicle_registration.html', 
                         asset=asset,
                         registration=registration)

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

@bp.route('/assets/<int:asset_id>/toyota-warranty')
@login_required
def toyota_warranty(asset_id):
    """View Toyota warranty info for asset"""
    asset = Asset.query.get_or_404(asset_id)
    warranty = ToyotaWarrantyReceipt.query.filter_by(asset_id=asset_id).first()
    
    return render_template('assets/detail_tables/toyota_warranty_receipt.html', 
                         asset=asset,
                         warranty=warranty)

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
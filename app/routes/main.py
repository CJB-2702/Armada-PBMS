from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_login import login_user, current_user
from app.models.user import User
from app.models.asset import Asset, AssetDetail
from app.models.location import Location
from app.models.asset_type import AssetType
from app.models.event import Event
from app import db
from datetime import datetime
from sqlalchemy import desc


bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    # For development, automatically log in as admin
    if not current_user.is_authenticated:
        admin = User.query.get(1)
        if admin:
            login_user(admin)
    return render_template('index.html')

@bp.route('/init-db')
def init_db():
    """Initialize database with default data"""
    init_debug_database()
    return redirect(url_for('main.index'))

@bp.route('/assets/create', methods=['GET', 'POST'])
def create_asset():
    if request.method == 'POST':
        # Get asset type
        asset_type = AssetType.query.get(request.form['asset_type_id'])
        if not asset_type:
            return "Invalid asset type", 400

        # Create main asset
        asset = Asset(
            common_name=request.form['common_name'],
            asset_type_id=asset_type.type_id,
            status=request.form['status']
        )
        db.session.add(asset)
        db.session.flush()  # Get the asset_id

        # Convert date string to date object if present
        date_delivered = None
        if request.form.get('date_delivered'):
            try:
                date_delivered = datetime.strptime(request.form['date_delivered'], '%Y-%m-%d').date()
            except ValueError:
                pass  # Keep as None if date is invalid

        # Convert numeric fields
        year_manufactured = request.form.get('year_manufactured')
        if year_manufactured:
            try:
                year_manufactured = int(year_manufactured)
            except ValueError:
                year_manufactured = None

        meter1_reading = request.form.get('meter1_reading')
        if meter1_reading:
            try:
                meter1_reading = float(meter1_reading)
            except ValueError:
                meter1_reading = None

        weight = request.form.get('weight')
        if weight:
            try:
                weight = float(weight)
            except ValueError:
                weight = None

        # Convert empty string to None for location_id
        location_id = request.form.get('location_id')
        if location_id == '':
            location_id = None

        # Create asset details
        details = AssetDetail(
            asset_id=asset.asset_id,
            make=request.form.get('make'),
            model=request.form.get('model'),
            equipment_identifier=request.form.get('equipment_identifier'),
            year_manufactured=year_manufactured,
            date_delivered=date_delivered,
            location_id=location_id,
            meter1_reading=meter1_reading,
            meter1_type=request.form.get('meter1_type'),
            fuel_type=request.form.get('fuel_type'),
            weight=weight,
            registration_category=request.form.get('registration_category')
        )
        db.session.add(details)
        db.session.commit()

        # Create event for new asset
        Asset.create_asset_event(asset.asset_id, current_user.user_id)

        return redirect(url_for('main.view_assets'))

    # Get locations and asset types for the dropdowns
    locations = Location.query.all()
    asset_types = AssetType.query.order_by(AssetType.name).all()
    return render_template('assets/create.html', locations=locations, asset_types=asset_types)

@bp.route('/assets')
def view_assets():
    asset_types = AssetType.query.order_by(AssetType.name).all()
    return render_template('assets/list.html', asset_types=asset_types)

@bp.route('/api/assets/search')
def search_assets():
    try:
        query = Asset.query
        
        # Apply filters
        common_name = request.args.get('common_name')
        asset_type_id = request.args.get('asset_type_id')
        status = request.args.get('status')

        if common_name:
            query = query.filter(Asset.common_name.ilike(f'%{common_name}%'))
        if asset_type_id:
            query = query.filter(Asset.asset_type_id == asset_type_id)
        if status:
            query = query.filter(Asset.status == status)
        
        # Get results with details
        assets = query.all()
        
        # If it's an HTMX request, render the cards
        if request.headers.get('HX-Request'):
            return render_template('assets/_asset_cards.html', assets=assets)
        
        # Otherwise return JSON for API calls
        results = []
        for asset in assets:
            asset_dict = asset.to_dict()
            if asset.details:
                asset_dict.update(asset.details.to_dict())
            results.append(asset_dict)

        return jsonify({
            "data": results,
            "meta": {
                "total": len(results),
                "filters": {
                    "common_name": common_name,
                    "asset_type_id": asset_type_id,
                    "status": status
                }
            }
        })
    except Exception as e:
        if request.headers.get('HX-Request'):
            return render_template('_error.html', error=str(e)), 500
        return jsonify({"error": str(e)}), 500

@bp.route('/api/asset-types')
def get_asset_types():
    """Get all asset types for dropdowns"""
    try:
        asset_types = AssetType.query.order_by(AssetType.name).all()
        
        # If it's an HTMX request, render the options
        if request.headers.get('HX-Request'):
            return render_template('assets/_asset_type_options.html', asset_types=asset_types)
        
        # Otherwise return JSON for API calls
        return jsonify({
            "data": [type.to_dict() for type in asset_types],
            "meta": {
                "total": len(asset_types)
            }
        })
    except Exception as e:
        if request.headers.get('HX-Request'):
            return render_template('_error.html', error=str(e)), 500
        return jsonify({"error": str(e)}), 500

@bp.route('/events/create')
def create_event():
    return render_template('events/create.html')

@bp.route('/locations/create', methods=['GET', 'POST'])
def create_location():
    if request.method == 'POST':
        location = Location(
            unique_name=request.form['unique_name'],
            common_name=request.form['common_name'],
            description=request.form.get('description'),
            country=request.form.get('country'),
            state=request.form.get('state'),
            city=request.form.get('city'),
            street=request.form.get('street'),
            building_number=request.form.get('building_number'),
            room=request.form.get('room'),
            x=request.form.get('x'),
            y=request.form.get('y'),
            z=request.form.get('z'),
            bin=request.form.get('bin')
        )
        db.session.add(location)
        db.session.commit()

        # Create event for new location
        Location.create_location_event(location.location_id, current_user.user_id)

        return redirect(url_for('main.view_locations'))
    
    return render_template('locations/create.html')

@bp.route('/locations')
def view_locations():
    return render_template('locations/list.html')

@bp.route('/api/locations/search')
def search_locations():
    try:
        query = Location.query
        
        # Apply filters
        common_name = request.args.get('common_name')
        unique_name = request.args.get('unique_name')
        city = request.args.get('city')

        if common_name:
            query = query.filter(Location.common_name.ilike(f'%{common_name}%'))
        if unique_name:
            query = query.filter(Location.unique_name.ilike(f'%{unique_name}%'))
        if city:
            query = query.filter(Location.city.ilike(f'%{city}%'))
        
        locations = query.all()
        
        # If it's an HTMX request, render the list
        if request.headers.get('HX-Request'):
            return render_template('locations/_location_list.html', locations=locations)
        
        # Otherwise return JSON for API calls
        return jsonify({
            "data": [location.to_dict() for location in locations],
            "meta": {
                "total": len(locations),
                "filters": {
                    "common_name": common_name,
                    "unique_name": unique_name,
                    "city": city
                }
            }
        })
    except Exception as e:
        if request.headers.get('HX-Request'):
            return render_template('_error.html', error=str(e)), 500
        return jsonify({"error": str(e)}), 500

@bp.route('/events/assets/<int:asset_id>')
def view_asset_events(asset_id):
    """View events for a specific asset"""
    asset = Asset.query.get_or_404(asset_id)
    return render_template('events/list.html', 
                         title=f'Events for {asset.common_name}',
                         asset=asset)

@bp.route('/events/locations/<int:location_id>')
def view_location_events(location_id):
    """View events for a specific location"""
    location = Location.query.get_or_404(location_id)
    return render_template('events/list.html', 
                         title=f'Events for {location.common_name}',
                         location=location)

@bp.route('/api/events')
def get_events():
    """Get events with infinite scroll support"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 20
        asset_id = request.args.get('asset_id', type=int)
        location_id = request.args.get('location_id', type=int)
        
        query = Event.query
        
        if asset_id:
            query = query.filter(Event.asset_id == asset_id)
        if location_id:
            query = query.filter(Event.location_id == location_id)
            
        # Order by most recent first
        query = query.order_by(desc(Event.created_at))
        
        # Get paginated results
        events = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # If it's an HTMX request, render the event cards
        if request.headers.get('HX-Request'):
            return render_template('events/_event_cards.html', 
                                 events=events.items,
                                 has_next=events.has_next,
                                 next_page=page + 1 if events.has_next else None)
        
        # Otherwise return JSON for API calls
        return jsonify({
            "data": [event.to_dict() for event in events.items],
            "meta": {
                "total": events.total,
                "pages": events.pages,
                "current_page": page,
                "per_page": per_page,
                "has_next": events.has_next
            }
        })
    except Exception as e:
        if request.headers.get('HX-Request'):
            return render_template('_error.html', error=str(e)), 500
        return jsonify({"error": str(e)}), 500 
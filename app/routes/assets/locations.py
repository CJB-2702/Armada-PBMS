from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.AssetModels.Locations import MajorLocation
from app.models.BaseModels.Event import Event
from app.extensions import db
from app.utils.logger import get_logger

logger = get_logger()

# Create blueprint
bp = Blueprint('locations', __name__, url_prefix='/locations')

def log_location_event(action, location, extra_info=None):
    title = f"Major Location {action}: {location.common_name} (UID: {location.UID})"
    description = (
        f"Major Location {action.lower()}\n"
        f"UID: {location.UID}\n"
        f"Common Name: {location.common_name}\n"
        f"Description: {location.description}\n"
        f"Status: {location.status}\n"
        f"Country: {location.Country}\n"
        f"State: {location.State}\n"
        f"City: {location.City}\n"
        f"Address: {location.Address}\n"
        f"Zip Code: {location.ZipCode}\n"
        f"Misc: {location.Misc}"
    )
    if extra_info:
        description += f"\n{extra_info}"
    event = Event(
        title=title,
        description=description,
        event_type_id='SYSTEM',
        status='completed',
        created_by=1
    )
    db.session.add(event)

@bp.route('/')
def index():
    """Display all locations"""
    try:
        locations = MajorLocation.query.all()
        return render_template('locations/index.html', locations=locations)
    except Exception as e:
        logger.error(f"Error fetching locations: {str(e)}")
        flash('Error loading locations', 'error')
        return render_template('locations/index.html', locations=[])

@bp.route('/<string:uid>')
def view_location(uid):
    location = MajorLocation.query.filter_by(UID=uid).first_or_404()
    return render_template('locations/view_location.html', location=location)

@bp.route('/create', methods=['GET', 'POST'])
def create_location():
    if request.method == 'POST':
        try:
            UID = request.form.get('UID')
            common_name = request.form.get('common_name')
            description = request.form.get('description')
            status = request.form.get('status', 'active')
            country = request.form.get('country')
            state = request.form.get('state')
            city = request.form.get('city')
            address = request.form.get('address')
            zip_code = request.form.get('zip_code')
            misc = request.form.get('misc')
            
            if not UID or not common_name or not description or not status:
                flash('UID, Common Name, Description, and Status are required', 'error')
                return render_template('locations/create_location.html')
            
            new_location = MajorLocation(
                UID=UID,
                common_name=common_name,
                description=description,
                status=status,
                created_by=1,
                Country=country,
                State=state,
                City=city,
                Address=address,
                ZipCode=zip_code,
                Misc=misc
            )
            db.session.add(new_location)
            db.session.commit()
            log_location_event("Created", new_location)
            db.session.commit()
            logger.info(f"New major location created: {common_name}")
            flash('Location created successfully', 'success')
            return redirect(url_for('locations.view_location', uid=new_location.UID))
        except Exception as e:
            logger.error(f"Error creating location: {str(e)}")
            flash('Error creating location', 'error')
            return render_template('locations/create_location.html')
    return render_template('locations/create_location.html')

@bp.route('/<string:uid>/edit', methods=['GET', 'POST'])
def edit_location(uid):
    location = MajorLocation.query.filter_by(UID=uid).first_or_404()
    if request.method == 'POST':
        try:
            common_name = request.form.get('common_name')
            description = request.form.get('description')
            status = request.form.get('status')
            country = request.form.get('country')
            state = request.form.get('state')
            city = request.form.get('city')
            address = request.form.get('address')
            zip_code = request.form.get('zip_code')
            misc = request.form.get('misc')
            
            if not common_name or not description or not status:
                return render_template('locations/edit_location.html', location=location, error='Common Name, Description, and Status are required')
            
            location.common_name = common_name
            location.description = description
            location.status = status
            location.Country = country
            location.State = state
            location.City = city
            location.Address = address
            location.ZipCode = zip_code
            location.Misc = misc
            
            db.session.commit()
            log_location_event("Edited", location)
            db.session.commit()
            logger.info(f"Location {uid} updated")
            flash('Location updated successfully', 'success')
            return redirect(url_for('locations.view_location', uid=location.UID))
        except Exception as e:
            logger.error(f"Error editing location {uid}: {str(e)}")
            flash('Error updating location', 'error')
            return render_template('locations/edit_location.html', location=location, error='Error updating location')
    return render_template('locations/edit_location.html', location=location)

@bp.route('/<string:uid>/delete', methods=['POST'])
def delete_location(uid):
    location = MajorLocation.query.filter_by(UID=uid).first_or_404()
    try:
        db.session.delete(location)
        log_location_event("Deleted", location)
        db.session.commit()
        logger.info(f"Location {uid} deleted.")
        flash('Location deleted successfully.', 'success')
        return redirect(url_for('locations.index'))
    except Exception as e:
        logger.error(f"Error deleting location {uid}: {str(e)}")
        flash('Error deleting location.', 'error')
        return redirect(url_for('locations.edit_location', uid=uid)) 
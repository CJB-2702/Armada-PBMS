from app.models.Assets.PhysicalAssets import PhysicalAsset


class VehicleModel(UserCreated):
    __tablename__ = 'vehicle_models'

    UID = db.Column(db.String(100), nullable=False, unique=True)
    manufacturer = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    model_subtype = db.Column(db.String(100), nullable=False, default="")
    year = db.Column(db.Integer, nullable=False)
    
    vehicle_class = db.Column(db.String(100))
    NHTSA_classification = db.Column(db.String(100))
    CARB_classification = db.Column(db.String(100))
    fuel_type = db.Column(db.String(100))
    fuel_tank_capacity = db.Column(db.Float)
    miles_per_fuel_type = db.Column(db.Float)
    weight = db.Column(db.Float)
    length = db.Column(db.Float)
    width = db.Column(db.Float)
    height = db.Column(db.Float)
    max_passengers = db.Column(db.Integer)
    max_cargo_capacity = db.Column(db.Float)
    expected_life_years = db.Column(db.Integer)
    expected_life_miles = db.Column(db.Integer)

    def __init__(self, manufacturer, model, model_subtype, year, vehicle_class, NHTSA_classification, CARB_classification, fuel_type, fuel_tank_capacity, miles_per_fuel_type, weight, length, width, height, wheelbase, ground_clearance, max_passengers, max_cargo_capacity, created_by=0):
        super().__init__(created_by)
        self.UID = f"{manufacturer}_{model}_{model_subtype}_{year}"
        self.manufacturer = manufacturer
        self.model = model
        self.model_subtype = model_subtype
        self.year = year
        self.vehicle_class = vehicle_class


class Vehicle(db.Model):
    __tablename__ = 'vehicles'

    asset_UID = db.Column(db.String(100), db.ForeignKey('assets.UID'), nullable=False)
    model_UID = db.Column(db.String(100), db.ForeignKey('vehicle_models.UID'), nullable=False)
    VIN = db.Column(db.String(100))
    color = db.Column(db.String(100))
    license_plate = db.Column(db.String(100))
    license_plate_state = db.Column(db.String(100))
    license_plate_expiration_date = db.Column(db.Date)
    license_plate_renewal_date = db.Column(db.Date)
    previous_license_plates = db.Column(db.String(100))
    purchase_date = db.Column(db.Date)
    purchase_price = db.Column(db.Float)



class VehiclePurchaseInfo(UserCreated):
    __tablename__ = 'VehiclePurchaseInfo'
    vehicle_id = db.Column(db.Integer, db.ForeignKey('Vehicles.row_id'), nullable=False)
    purchase_date = db.Column(db.Date)
    purchase_price = db.Column(db.Float)
    purchase_location_UID = db.Column(db.String(100), db.ForeignKey('misc_locations.UID'))
    attachments = db.Column(db.String(100))


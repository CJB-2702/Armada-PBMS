from app.models.Assets.Assets import Asset
from app.extensions import db
from app.models.BaseModels.ProtoClasses import UserCreated
from app.models.BaseModels.Locations import MajorLocation, MinorLocation
from app.models.Utility.MiscLocations import MiscLocations
from app.models.Utility.Lists import GenericTypes
from datetime import datetime


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


class Vehicle(UserCreated):
    __tablename__ = 'vehicles'

    asset_UID = db.Column(db.String(100), db.ForeignKey('assets.UID'), nullable=False)
    model_UID = db.Column(db.String(100), db.ForeignKey('vehicle_models.UID'), nullable=False)
    VIN = db.Column(db.String(100), unique=True)
    color = db.Column(db.String(100))
    license_plate = db.Column(db.String(100))
    license_plate_state = db.Column(db.String(100))
    license_plate_expiration_date = db.Column(db.Date)
    license_plate_renewal_date = db.Column(db.Date)
    previous_license_plates = db.Column(db.String(100))
    purchase_date = db.Column(db.Date, default=datetime.now())
    purchase_price = db.Column(db.Float)

    def __init__(self, asset_UID, model_UID, VIN=None, color=None, license_plate=None, 
                 license_plate_state=None, license_plate_expiration_date=None,
                 license_plate_renewal_date=None, previous_license_plates=None,
                 purchase_date=datetime.now(), purchase_price=None, created_by=0):    
        super().__init__(created_by)
        self.asset_UID = asset_UID
        self.model_UID = model_UID
        self.VIN = VIN
        self.color = color
        self.license_plate = license_plate
        self.license_plate_state = license_plate_state
        self.license_plate_expiration_date = license_plate_expiration_date
        self.license_plate_renewal_date = license_plate_renewal_date
        self.previous_license_plates = previous_license_plates
        self.purchase_date = purchase_date
        self.purchase_price = purchase_price


class VehiclePurchaseInfo(UserCreated):
    __tablename__ = 'vehicle_purchase_info'

    row_id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.row_id'), nullable=False)
    purchase_date = db.Column(db.Date)
    purchase_price = db.Column(db.Float)
    purchase_location_UID = db.Column(db.String(100), db.ForeignKey('misc_locations.UID'))
    attachments = db.Column(db.String(100))

    def __init__(self, vehicle_id, purchase_date=None, purchase_price=None,
                 purchase_location_UID=None, attachments=None, created_by=0):
        super().__init__(created_by)
        self.vehicle_id = vehicle_id
        self.purchase_date = purchase_date
        self.purchase_price = purchase_price
        self.purchase_location_UID = purchase_location_UID
        self.attachments = attachments

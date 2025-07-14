from app.models.BaseModels.Event import Event
from app.extensions import db

class AssetEvent(Event):
    asset_UID = db.Column(db.String(100), db.ForeignKey('assets.UID'), default=0)
    asset_type = db.Column(db.String(100), db.ForeignKey('assets.asset_type'), nullable=False, default="General")



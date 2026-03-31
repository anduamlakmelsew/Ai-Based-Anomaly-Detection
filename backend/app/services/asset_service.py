from app.models.asset_model import Asset
from app import db

def create_asset(name, ip, owner_id=None):
    asset = Asset(name=name, ip=ip, owner_id=owner_id)
    db.session.add(asset)
    db.session.commit()
    return asset

def get_asset(asset_id):
    return Asset.query.get(asset_id)

def list_assets():
    return Asset.query.all()

def update_asset(asset_id, **kwargs):
    asset = Asset.query.get(asset_id)
    if asset:
        for key, value in kwargs.items():
            setattr(asset, key, value)
        db.session.commit()
        return asset
    return None

def delete_asset(asset_id):
    asset = Asset.query.get(asset_id)
    if asset:
        db.session.delete(asset)
        db.session.commit()
        return True
    return False
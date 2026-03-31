from app.models.baseline_model import Baseline
from app import db

def create_baseline(name, description, asset_id):
    baseline = Baseline(name=name, description=description, asset_id=asset_id)
    db.session.add(baseline)
    db.session.commit()
    return baseline

def list_baselines():
    return Baseline.query.all()

def get_baseline(baseline_id):
    return Baseline.query.get(baseline_id)

def update_baseline(baseline_id, **kwargs):
    baseline = Baseline.query.get(baseline_id)
    if baseline:
        for key, value in kwargs.items():
            setattr(baseline, key, value)
        db.session.commit()
        return baseline
    return None

def delete_baseline(baseline_id):
    baseline = Baseline.query.get(baseline_id)
    if baseline:
        db.session.delete(baseline)
        db.session.commit()
        return True
    return False
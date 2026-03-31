from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.database import db
from app.models import Asset

asset_bp = Blueprint("assets", __name__)


@asset_bp.route("/", methods=["GET"])
@jwt_required()
def get_assets():

    assets = Asset.query.all()

    result = []

    for asset in assets:
        result.append({
            "id": asset.id,
            "name": asset.name,
            "ip_address": asset.ip_address,
            "asset_type": asset.asset_type
        })

    return jsonify(result)


@asset_bp.route("/", methods=["POST"])
@jwt_required()
def create_asset():

    data = request.get_json()

    asset = Asset(
        name=data["name"],
        ip_address=data["ip_address"],
        asset_type=data["asset_type"]
    )

    db.session.add(asset)
    db.session.commit()

    return jsonify({"message": "Asset created"})


@asset_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_asset(id):

    asset = Asset.query.get_or_404(id)

    db.session.delete(asset)
    db.session.commit()

    return jsonify({"message": "Asset deleted"})
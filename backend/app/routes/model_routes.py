"""
AI Model management routes - Upload, versioning, activation
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import hashlib

from app.models.ai_model import AIModel
from app import db

model_bp = Blueprint('models', __name__, url_prefix='/api/models')

# Allowed model file extensions
ALLOWED_EXTENSIONS = {'pkl', 'joblib', 'h5', 'pt', 'pth'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def calculate_checksum(file_path):
    """Calculate SHA-256 checksum of file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for byte_block in iter(lambda: f.read(4096), b''):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


@model_bp.route('', methods=['GET'])
@jwt_required()
def list_models():
    """List all AI models with optional filtering"""
    try:
        model_type = request.args.get('type')  # Filter by type
        status = request.args.get('status')    # Filter by status
        
        query = AIModel.query
        
        if model_type:
            query = query.filter_by(model_type=model_type)
        if status:
            query = query.filter_by(status=status)
        
        models = query.order_by(AIModel.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'data': [m.to_dict() for m in models],
            'count': len(models)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@model_bp.route('/<int:model_id>', methods=['GET'])
@jwt_required()
def get_model(model_id):
    """Get specific model details"""
    try:
        model = AIModel.query.get_or_404(model_id)
        return jsonify({
            'success': True,
            'data': model.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@model_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_model():
    """
    Upload a new AI model file
    
    Form fields:
    - model: File (required)
    - model_type: 'network', 'web', or 'system' (required)
    - version: Semantic version e.g. '1.2.0' (required)
    - description: Text description (optional)
    - change_notes: What changed in this version (optional)
    - accuracy: Model accuracy score (optional)
    - training_data_size: Number of training samples (optional)
    - hyperparameters: JSON string of hyperparameters (optional)
    """
    try:
        user_id = int(get_jwt_identity())
        
        # Check if file is present
        if 'model' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No model file provided'
            }), 400
        
        file = request.files['model']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': f'Invalid file type. Allowed: {ALLOWED_EXTENSIONS}'
            }), 400
        
        # Get form data
        model_type = request.form.get('model_type')
        version = request.form.get('version')
        
        if not model_type or not version:
            return jsonify({
                'success': False,
                'error': 'model_type and version are required'
            }), 400
        
        if model_type not in ['network', 'web', 'system']:
            return jsonify({
                'success': False,
                'error': 'model_type must be network, web, or system'
            }), 400
        
        # Check if version already exists
        existing = AIModel.query.filter_by(
            model_type=model_type,
            version=version
        ).first()
        
        if existing:
            return jsonify({
                'success': False,
                'error': f'Version {version} already exists for {model_type}'
            }), 409
        
        # Create upload directory if needed
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads/models')
        model_dir = os.path.join(upload_folder, model_type)
        os.makedirs(model_dir, exist_ok=True)
        
        # Save file
        filename = secure_filename(file.filename)
        base_name = f"{model_type}_model_v{version}"
        file_ext = filename.rsplit('.', 1)[1].lower()
        new_filename = f"{base_name}.{file_ext}"
        file_path = os.path.join(model_dir, new_filename)
        
        file.save(file_path)
        
        # Calculate checksum
        checksum = calculate_checksum(file_path)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Parse optional metadata
        accuracy = request.form.get('accuracy', type=float)
        training_data_size = request.form.get('training_data_size', type=int)
        hyperparameters = {}
        
        if request.form.get('hyperparameters'):
            try:
                import json
                hyperparameters = json.loads(request.form.get('hyperparameters'))
            except:
                pass
        
        features_used = []
        if request.form.get('features_used'):
            try:
                import json
                features_used = json.loads(request.form.get('features_used'))
            except:
                pass
        
        # Create model record
        new_model = AIModel(
            name=f"{model_type.capitalize()} Model v{version}",
            version=version,
            model_type=model_type,
            filename=new_filename,
            file_path=file_path,
            file_size=file_size,
            checksum=checksum,
            accuracy=accuracy,
            training_data_size=training_data_size,
            hyperparameters=hyperparameters,
            features_used=features_used,
            status='inactive',  # Start as inactive, need to activate
            description=request.form.get('description'),
            change_notes=request.form.get('change_notes'),
            created_by=user_id,
            training_date=datetime.utcnow()
        )
        
        db.session.add(new_model)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Model uploaded successfully',
            'data': new_model.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@model_bp.route('/<int:model_id>/activate', methods=['POST'])
@jwt_required()
def activate_model(model_id):
    """Activate a specific model version"""
    try:
        model = AIModel.query.get_or_404(model_id)
        
        # Activate the model (deactivates others of same type)
        model.activate()
        
        return jsonify({
            'success': True,
            'message': f'Model {model.name} v{model.version} activated successfully',
            'data': model.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@model_bp.route('/<int:model_id>/deprecate', methods=['POST'])
@jwt_required()
def deprecate_model(model_id):
    """Mark a model as deprecated"""
    try:
        model = AIModel.query.get_or_404(model_id)
        model.deprecate()
        
        return jsonify({
            'success': True,
            'message': f'Model {model.name} v{model.version} deprecated'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@model_bp.route('/<int:model_id>', methods=['DELETE'])
@jwt_required()
def delete_model(model_id):
    """Delete a model (only if inactive/deprecated)"""
    try:
        model = AIModel.query.get_or_404(model_id)
        
        # Don't allow deleting active models
        if model.status == 'active':
            return jsonify({
                'success': False,
                'error': 'Cannot delete active model. Deprecate it first.'
            }), 400
        
        # Delete file
        if os.path.exists(model.file_path):
            os.remove(model.file_path)
        
        # Delete record
        db.session.delete(model)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Model deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@model_bp.route('/active/<model_type>', methods=['GET'])
@jwt_required()
def get_active_model(model_type):
    """Get currently active model for a type"""
    try:
        model = AIModel.get_active_model(model_type)
        
        if not model:
            return jsonify({
                'success': False,
                'error': f'No active model found for type {model_type}'
            }), 404
        
        return jsonify({
            'success': True,
            'data': model.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@model_bp.route('/types/<model_type>/history', methods=['GET'])
@jwt_required()
def get_model_history(model_type):
    """Get version history for a model type"""
    try:
        models = AIModel.get_version_history(model_type)
        
        return jsonify({
            'success': True,
            'data': [m.to_dict() for m in models],
            'count': len(models)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

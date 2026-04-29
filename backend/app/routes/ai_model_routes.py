"""
AI Model Upload Routes - Upload and manage trained AI models
"""
import os
import hashlib
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from datetime import datetime

from app import db
from app.models.ai_model import AIModel

ai_model_bp = Blueprint('ai_models', __name__, url_prefix='/api/ai')

ALLOWED_EXTENSIONS = {'pkl', 'joblib', 'h5', 'pt', 'pth', 'onnx'}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def calculate_checksum(file_path):
    """Calculate SHA-256 checksum of file"""
    sha256_hash = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


@ai_model_bp.route('/upload-model', methods=['POST'])
@jwt_required()
def upload_model():
    """
    Upload a new trained AI model file
    
    Form fields:
    - model: File (.pkl, .joblib, .h5, .pt, .pth) - Required
    - model_type: 'network', 'web', or 'system' - Required
    - version: Version string (e.g., '2.0.0') - Required
    - description: Optional description
    - accuracy: Model accuracy score (0-1) - Optional
    
    Returns:
    - success: bool
    - message: str
    - data: model info dict
    """
    try:
        user_id = int(get_jwt_identity())
        
        # Check if file is present
        if 'model' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No model file provided. Use form field name "model".'
            }), 400
        
        file = request.files['model']
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Validate file type
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
                'error': 'model_type must be: network, web, or system'
            }), 400
        
        # Read file content to check size
        file_content = file.read()
        if len(file_content) > MAX_FILE_SIZE:
            return jsonify({
                'success': False,
                'error': f'File too large. Max size: {MAX_FILE_SIZE / (1024*1024)}MB'
            }), 413
        
        # Reset file pointer for saving
        file.seek(0)
        
        # Create models directory if not exists
        models_dir = os.path.join(current_app.root_path, 'ai', 'models')
        os.makedirs(models_dir, exist_ok=True)
        
        # Generate secure filename
        original_filename = secure_filename(file.filename)
        file_ext = original_filename.rsplit('.', 1)[1].lower()
        new_filename = f"{model_type}_model_v{version}.{file_ext}"
        file_path = os.path.join(models_dir, new_filename)
        
        # Handle existing file - backup old version
        if os.path.exists(file_path):
            backup_name = f"{new_filename}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            backup_path = os.path.join(models_dir, backup_name)
            os.rename(file_path, backup_path)
            print(f"📦 Backed up existing model to: {backup_name}")
        
        # Save the file
        file.save(file_path)
        file_size = os.path.getsize(file_path)
        
        # Calculate checksum for integrity
        checksum = calculate_checksum(file_path)
        
        # Parse optional metadata
        accuracy = None
        if request.form.get('accuracy'):
            try:
                accuracy = float(request.form.get('accuracy'))
            except ValueError:
                pass
        
        # Create or update database record
        existing_model = AIModel.query.filter_by(
            model_type=model_type,
            version=version
        ).first()
        
        if existing_model:
            # Update existing record
            existing_model.filename = new_filename
            existing_model.file_path = file_path
            existing_model.file_size = file_size
            existing_model.checksum = checksum
            existing_model.accuracy = accuracy
            existing_model.description = request.form.get('description')
            existing_model.updated_at = datetime.utcnow()
            model_record = existing_model
            message = f'Model {model_type} v{version} updated successfully'
        else:
            # Create new record
            model_record = AIModel(
                name=f"{model_type.capitalize()} Model v{version}",
                version=version,
                model_type=model_type,
                filename=new_filename,
                file_path=file_path,
                file_size=file_size,
                checksum=checksum,
                accuracy=accuracy,
                description=request.form.get('description'),
                status='inactive',  # Start as inactive, user must activate
                created_by=user_id,
                training_date=datetime.utcnow()
            )
            db.session.add(model_record)
            message = f'Model {model_type} v{version} uploaded successfully'
        
        db.session.commit()
        
        print(f"✅ Model uploaded: {new_filename} ({file_size} bytes)")
        
        return jsonify({
            'success': True,
            'message': message,
            'data': {
                'id': model_record.id,
                'model_type': model_type,
                'version': version,
                'filename': new_filename,
                'file_size': file_size,
                'checksum': checksum,
                'accuracy': accuracy,
                'status': model_record.status,
                'uploaded_at': model_record.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Model upload error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Upload failed: {str(e)}'
        }), 500


@ai_model_bp.route('/reload-model/<model_type>', methods=['POST'])
@jwt_required()
def reload_model(model_type):
    """
    Reload AI model for immediate use by the pipeline
    Triggers model cache refresh
    """
    try:
        if model_type not in ['network', 'web', 'system']:
            return jsonify({
                'success': False,
                'error': 'model_type must be: network, web, or system'
            }), 400
        
        # Clear model cache to force reload
        from app.ai import loader
        
        cache_attr = f'_{model_type}_model'
        if hasattr(loader, cache_attr):
            setattr(loader, cache_attr, None)
            print(f"🔄 Cleared cache for {model_type} model")
        
        # Try to load the model
        model = None
        if model_type == 'network':
            model = loader.get_network_model()
        elif model_type == 'web':
            model = loader.get_web_model()
        elif model_type == 'system':
            model = loader.get_system_model()
        
        if model:
            return jsonify({
                'success': True,
                'message': f'{model_type} model reloaded successfully',
                'data': {
                    'model_type': model_type,
                    'loaded': True
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Failed to reload {model_type} model. Check if model file exists.'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Reload failed: {str(e)}'
        }), 500


@ai_model_bp.route('/models', methods=['GET'])
@jwt_required()
def list_models():
    """List all uploaded AI models"""
    try:
        model_type = request.args.get('type')
        
        query = AIModel.query
        if model_type:
            query = query.filter_by(model_type=model_type)
        
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


@ai_model_bp.route('/activate-model/<int:model_id>', methods=['POST'])
@jwt_required()
def activate_model(model_id):
    """Activate a specific model version"""
    try:
        model = AIModel.query.get_or_404(model_id)
        
        # Check if file exists
        if not os.path.exists(model.file_path):
            return jsonify({
                'success': False,
                'error': 'Model file not found on disk'
            }), 404
        
        # Activate this model (deactivates others)
        model.activate()
        
        # Reload the model
        from app.ai import loader
        cache_attr = f'_{model.model_type}_model'
        if hasattr(loader, cache_attr):
            setattr(loader, cache_attr, None)
        
        return jsonify({
            'success': True,
            'message': f'Model {model.name} v{model.version} activated and ready to use'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

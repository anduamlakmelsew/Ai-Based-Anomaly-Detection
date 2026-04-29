"""
AI Model versioning and management model
"""
from app import db
from datetime import datetime
import json


class AIModel(db.Model):
    """
    Stores AI model versions and metadata
    """
    __tablename__ = "ai_models"
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Model identification
    name = db.Column(db.String(100), nullable=False)
    version = db.Column(db.String(20), nullable=False)
    model_type = db.Column(db.String(50), nullable=False)  # 'network', 'web', 'system'
    
    # File storage
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, default=0)
    checksum = db.Column(db.String(64), nullable=True)  # SHA-256 for integrity
    
    # Model performance metrics
    accuracy = db.Column(db.Float, nullable=True)
    precision = db.Column(db.Float, nullable=True)
    recall = db.Column(db.Float, nullable=True)
    f1_score = db.Column(db.Float, nullable=True)
    
    # Training metadata
    training_data_size = db.Column(db.Integer, nullable=True)
    training_date = db.Column(db.DateTime, nullable=True)
    features_used = db.Column(db.JSON, default=list)
    hyperparameters = db.Column(db.JSON, default=dict)
    
    # Status
    status = db.Column(db.String(20), default="inactive")  # active, inactive, deprecated, archived
    is_default = db.Column(db.Boolean, default=False)
    
    # Description and notes
    description = db.Column(db.Text, nullable=True)
    change_notes = db.Column(db.Text, nullable=True)
    
    # User who uploaded/created
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    activated_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    creator = db.relationship('User', backref='uploaded_models')
    
    __table_args__ = (
        db.UniqueConstraint('model_type', 'version', name='unique_model_version'),
    )
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'version': self.version,
            'model_type': self.model_type,
            'filename': self.filename,
            'file_size': self.file_size,
            'checksum': self.checksum,
            'metrics': {
                'accuracy': self.accuracy,
                'precision': self.precision,
                'recall': self.recall,
                'f1_score': self.f1_score
            },
            'training': {
                'data_size': self.training_data_size,
                'date': self.training_date.isoformat() if self.training_date else None,
                'features': self.features_used,
                'hyperparameters': self.hyperparameters
            },
            'status': self.status,
            'is_default': self.is_default,
            'description': self.description,
            'change_notes': self.change_notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'activated_at': self.activated_at.isoformat() if self.activated_at else None,
            'created_by': self.created_by
        }
    
    def activate(self):
        """Activate this model and deactivate others of same type"""
        # Deactivate all other models of same type
        AIModel.query.filter_by(model_type=self.model_type).update({
            'status': 'inactive',
            'is_default': False
        })
        
        # Activate this model
        self.status = 'active'
        self.is_default = True
        self.activated_at = datetime.utcnow()
        
        db.session.commit()
    
    def deprecate(self):
        """Mark model as deprecated"""
        self.status = 'deprecated'
        self.is_default = False
        db.session.commit()
    
    @staticmethod
    def get_active_model(model_type):
        """Get currently active model for a type"""
        return AIModel.query.filter_by(
            model_type=model_type,
            status='active'
        ).first()
    
    @staticmethod
    def get_default_model(model_type):
        """Get default model for a type"""
        return AIModel.query.filter_by(
            model_type=model_type,
            is_default=True
        ).first()
    
    @staticmethod
    def get_version_history(model_type):
        """Get version history for a model type"""
        return AIModel.query.filter_by(
            model_type=model_type
        ).order_by(AIModel.created_at.desc()).all()

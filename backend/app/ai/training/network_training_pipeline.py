"""
network_training_pipeline.py

Production-grade training pipeline for network intrusion detection.
Trains both binary (Normal vs Attack) and multi-class (DoS, Probe, R2L, U2R, Normal)
classifiers using RandomForest and XGBoost.
"""

import os
import sys
import logging
import json
import time
from typing import Tuple, Dict, List, Optional
from datetime import datetime

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import (
    classification_report, confusion_matrix, accuracy_score,
    precision_score, recall_score, f1_score, roc_auc_score
)
from sklearn.preprocessing import LabelBinarizer
import joblib

# Try to import XGBoost, fallback to RF only if not available
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    logging.warning("XGBoost not available. Install with: pip install xgboost")

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from training.network_unified_dataset import NetworkDatasetLoader, load_unified_network_dataset
from training.network_feature_engineering import NetworkFeatureEngineer, FeaturePreprocessor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
os.makedirs(MODEL_DIR, exist_ok=True)

# Output model paths
BINARY_RF_PATH = os.path.join(MODEL_DIR, "network_model_binary.pkl")
BINARY_XGB_PATH = os.path.join(MODEL_DIR, "network_model_binary_xgb.pkl")
MULTI_RF_PATH = os.path.join(MODEL_DIR, "network_model_multiclass.pkl")
MULTI_XGB_PATH = os.path.join(MODEL_DIR, "network_model_multiclass_xgb.pkl")
PREPROCESSOR_PATH = os.path.join(MODEL_DIR, "network_preprocessor.pkl")
FEATURE_ENG_PATH = os.path.join(MODEL_DIR, "network_feature_engineer.pkl")
FEATURE_NAMES_PATH = os.path.join(MODEL_DIR, "network_feature_names.json")
METADATA_PATH = os.path.join(MODEL_DIR, "network_model_metadata.json")


class ModelEvaluator:
    """Evaluate and report model performance."""
    
    @staticmethod
    def evaluate_binary(y_true: np.ndarray, y_pred: np.ndarray, y_proba: Optional[np.ndarray] = None) -> Dict:
        """Evaluate binary classification performance."""
        metrics = {
            'accuracy': float(accuracy_score(y_true, y_pred)),
            'precision': float(precision_score(y_true, y_pred, zero_division=0)),
            'recall': float(recall_score(y_true, y_pred, zero_division=0)),
            'f1': float(f1_score(y_true, y_pred, zero_division=0)),
        }
        
        if y_proba is not None:
            try:
                metrics['auc_roc'] = float(roc_auc_score(y_true, y_proba))
            except Exception as e:
                logger.warning(f"Could not compute AUC-ROC: {e}")
        
        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        metrics['confusion_matrix'] = cm.tolist()
        metrics['true_negatives'] = int(cm[0, 0]) if cm.shape[0] > 0 else 0
        metrics['false_positives'] = int(cm[0, 1]) if cm.shape[1] > 1 else 0
        metrics['false_negatives'] = int(cm[1, 0]) if cm.shape[0] > 1 else 0
        metrics['true_positives'] = int(cm[1, 1]) if cm.shape == (2, 2) else 0
        
        return metrics
    
    @staticmethod
    def evaluate_multiclass(y_true: np.ndarray, y_pred: np.ndarray, class_names: List[str]) -> Dict:
        """Evaluate multi-class classification performance."""
        metrics = {
            'accuracy': float(accuracy_score(y_true, y_pred)),
            'precision_macro': float(precision_score(y_true, y_pred, average='macro', zero_division=0)),
            'recall_macro': float(recall_score(y_true, y_pred, average='macro', zero_division=0)),
            'f1_macro': float(f1_score(y_true, y_pred, average='macro', zero_division=0)),
            'precision_weighted': float(precision_score(y_true, y_pred, average='weighted', zero_division=0)),
            'recall_weighted': float(recall_score(y_true, y_pred, average='weighted', zero_division=0)),
            'f1_weighted': float(f1_score(y_true, y_pred, average='weighted', zero_division=0)),
        }
        
        # Per-class metrics
        cm = confusion_matrix(y_true, y_pred)
        metrics['confusion_matrix'] = cm.tolist()
        
        # Classification report
        report = classification_report(y_true, y_pred, target_names=class_names, output_dict=True, zero_division=0)
        metrics['per_class'] = report
        
        return metrics
    
    @staticmethod
    def print_report(metrics: Dict, model_name: str, class_names: Optional[List[str]] = None):
        """Print formatted evaluation report."""
        print("\n" + "=" * 60)
        print(f"📊 {model_name} EVALUATION REPORT")
        print("=" * 60)
        
        print(f"\n🎯 Overall Metrics:")
        print(f"  Accuracy:  {metrics['accuracy']:.4f}")
        
        if 'auc_roc' in metrics:
            print(f"  AUC-ROC:   {metrics['auc_roc']:.4f}")
        
        if 'precision' in metrics:
            print(f"  Precision: {metrics['precision']:.4f}")
            print(f"  Recall:    {metrics['recall']:.4f}")
            print(f"  F1-Score:  {metrics['f1']:.4f}")
        
        if 'f1_macro' in metrics:
            print(f"  F1 (macro):     {metrics['f1_macro']:.4f}")
            print(f"  F1 (weighted):  {metrics['f1_weighted']:.4f}")
        
        print(f"\n📋 Confusion Matrix:")
        cm = np.array(metrics['confusion_matrix'])
        print("  " + "-" * (cm.shape[1] * 8))
        for row in cm:
            cells = " | ".join(f"{val:6d}" for val in row)
            print(f"  | {cells} |")
        print("  " + "-" * (cm.shape[1] * 8))
        
        if class_names and 'per_class' in metrics:
            print(f"\n📊 Per-Class Metrics:")
            for cls in class_names:
                if cls in metrics['per_class']:
                    cls_metrics = metrics['per_class'][cls]
                    print(f"  {cls:12s}: Precision={cls_metrics['precision']:.3f}, "
                          f"Recall={cls_metrics['recall']:.3f}, F1={cls_metrics['f1-score']:.3f}, "
                          f"Support={cls_metrics['support']:.0f}")


class NetworkTrainer:
    """
    Training pipeline for network intrusion detection models.
    """
    
    def __init__(self, max_samples: Optional[int] = None, test_size: float = 0.2):
        """
        Initialize trainer.
        
        Args:
            max_samples: Limit samples per dataset for testing
            test_size: Fraction of data for testing
        """
        self.max_samples = max_samples
        self.test_size = test_size
        self.dataset_loader = NetworkDatasetLoader(max_samples_per_dataset=max_samples)
        self.feature_engineer = NetworkFeatureEngineer(fit_mode=True)
        self.preprocessor = FeaturePreprocessor()
        
        self.metrics = {}
        
    def load_and_prepare_data(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Load datasets, engineer features, and split into train/test.
        
        Returns:
            Tuple of (X_train, X_test, y_binary_train, y_binary_test, y_multi_train, y_multi_test)
        """
        logger.info("=" * 60)
        logger.info("STEP 1: Loading Unified Datasets")
        logger.info("=" * 60)
        
        # Load unified dataset
        df = self.dataset_loader.load_all_datasets()
        
        logger.info("\n" + "=" * 60)
        logger.info("STEP 2: Feature Engineering")
        logger.info("=" * 60)
        
        # Engineer features
        X = self.feature_engineer.fit_transform(df)
        
        # Save feature engineer for later
        self.feature_engineer.save(FEATURE_ENG_PATH)
        
        # Get labels
        y_binary = self.dataset_loader.get_binary_labels(df)
        y_multi = self.dataset_loader.get_multiclass_labels(df)
        class_names = self.dataset_loader.get_multiclass_names()
        
        logger.info(f"Feature matrix shape: {X.shape}")
        logger.info(f"Binary classes: {np.bincount(y_binary)}")
        logger.info(f"Multi-class distribution: {np.bincount(y_multi, minlength=len(class_names))}")
        
        # Preprocess features
        logger.info("\n" + "=" * 60)
        logger.info("STEP 3: Preprocessing")
        logger.info("=" * 60)
        
        X_scaled = self.preprocessor.fit_transform(X)
        self.preprocessor.save(PREPROCESSOR_PATH)
        
        # Split data
        logger.info("\n" + "=" * 60)
        logger.info("STEP 4: Train/Test Split")
        logger.info("=" * 60)
        
        X_train, X_test, y_bin_train, y_bin_test = train_test_split(
            X_scaled, y_binary, test_size=self.test_size, random_state=42, stratify=y_binary
        )
        
        # Multi-class uses same split indices
        y_multi_train = y_multi[X_train.index if hasattr(X_train, 'index') else range(len(y_multi))[:len(X_train)]]
        y_multi_test = y_multi[X_test.index if hasattr(X_test, 'index') else range(len(y_multi))[len(X_train):]]
        
        if hasattr(X_train, 'index'):
            y_multi_train = y_multi[X_train.index]
            y_multi_test = y_multi[X_test.index]
        else:
            y_multi_train = y_multi[:len(X_train)]
            y_multi_test = y_multi[len(X_train):]
        
        logger.info(f"Training samples: {len(X_train)}")
        logger.info(f"Test samples: {len(X_test)}")
        
        return X_train, X_test, y_bin_train, y_bin_test, y_multi_train, y_multi_test, class_names
    
    def train_random_forest_binary(self, X_train: np.ndarray, y_train: np.ndarray) -> RandomForestClassifier:
        """Train RandomForest binary classifier."""
        logger.info("\n" + "=" * 60)
        logger.info("Training RandomForest Binary Classifier")
        logger.info("=" * 60)
        
        model = RandomForestClassifier(
            n_estimators=200,
            max_depth=25,
            min_samples_split=5,
            min_samples_leaf=2,
            max_features='sqrt',
            class_weight='balanced',
            random_state=42,
            n_jobs=-1,
            verbose=1
        )
        
        start_time = time.time()
        model.fit(X_train, y_train)
        train_time = time.time() - start_time
        
        logger.info(f"Training completed in {train_time:.2f} seconds")
        
        return model
    
    def train_xgboost_binary(self, X_train: np.ndarray, y_train: np.ndarray):
        """Train XGBoost binary classifier."""
        if not XGBOOST_AVAILABLE:
            logger.warning("XGBoost not available, skipping binary XGBoost training")
            return None
        
        logger.info("\n" + "=" * 60)
        logger.info("Training XGBoost Binary Classifier")
        logger.info("=" * 60)
        
        # Calculate scale_pos_weight for imbalanced data
        neg_count = np.sum(y_train == 0)
        pos_count = np.sum(y_train == 1)
        scale_pos_weight = neg_count / pos_count if pos_count > 0 else 1.0
        
        model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=10,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            scale_pos_weight=scale_pos_weight,
            random_state=42,
            n_jobs=-1,
            eval_metric='logloss',
            verbosity=1
        )
        
        start_time = time.time()
        model.fit(X_train, y_train)
        train_time = time.time() - start_time
        
        logger.info(f"Training completed in {train_time:.2f} seconds")
        
        return model
    
    def train_random_forest_multiclass(self, X_train: np.ndarray, y_train: np.ndarray) -> RandomForestClassifier:
        """Train RandomForest multi-class classifier."""
        logger.info("\n" + "=" * 60)
        logger.info("Training RandomForest Multi-Class Classifier")
        logger.info("=" * 60)
        
        model = RandomForestClassifier(
            n_estimators=200,
            max_depth=25,
            min_samples_split=5,
            min_samples_leaf=2,
            max_features='sqrt',
            class_weight='balanced',
            random_state=42,
            n_jobs=-1,
            verbose=1
        )
        
        start_time = time.time()
        model.fit(X_train, y_train)
        train_time = time.time() - start_time
        
        logger.info(f"Training completed in {train_time:.2f} seconds")
        
        return model
    
    def train_xgboost_multiclass(self, X_train: np.ndarray, y_train: np.ndarray):
        """Train XGBoost multi-class classifier."""
        if not XGBOOST_AVAILABLE:
            logger.warning("XGBoost not available, skipping multi-class XGBoost training")
            return None
        
        logger.info("\n" + "=" * 60)
        logger.info("Training XGBoost Multi-Class Classifier")
        logger.info("=" * 60)
        
        num_classes = len(np.unique(y_train))
        
        model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=10,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            n_jobs=-1,
            objective='multi:softprob',
            num_class=num_classes,
            eval_metric='mlogloss',
            verbosity=1
        )
        
        start_time = time.time()
        model.fit(X_train, y_train)
        train_time = time.time() - start_time
        
        logger.info(f"Training completed in {train_time:.2f} seconds")
        
        return model
    
    def get_feature_importance(self, model, feature_names: List[str], top_n: int = 20) -> List[Tuple[str, float]]:
        """Extract top N feature importances from model."""
        if hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
        else:
            return []
        
        # Pair feature names with importances
        feat_imp = list(zip(feature_names, importances))
        feat_imp.sort(key=lambda x: x[1], reverse=True)
        
        return feat_imp[:top_n]
    
    def run_full_pipeline(self):
        """
        Execute complete training pipeline.
        """
        print("\n" + "=" * 60)
        print("🚀 NETWORK INTRUSION DETECTION TRAINING PIPELINE")
        print("=" * 60)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Model Output Directory: {MODEL_DIR}")
        print(f"XGBoost Available: {XGBOOST_AVAILABLE}")
        
        start_time = time.time()
        
        # Load and prepare data
        try:
            X_train, X_test, y_bin_train, y_bin_test, y_multi_train, y_multi_test, class_names = \
                self.load_and_prepare_data()
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        feature_names = self.feature_engineer.ENGINEERED_FEATURES
        
        # Save feature names
        with open(FEATURE_NAMES_PATH, 'w') as f:
            json.dump(feature_names, f, indent=2)
        
        # Train models
        models = {}
        
        # Binary RandomForest
        print("\n" + "=" * 60)
        print("🤖 TRAINING BINARY CLASSIFIERS (Normal vs Attack)")
        print("=" * 60)
        
        rf_binary = self.train_random_forest_binary(X_train, y_bin_train)
        models['binary_rf'] = rf_binary
        
        y_pred = rf_binary.predict(X_test)
        y_proba = rf_binary.predict_proba(X_test)[:, 1] if hasattr(rf_binary, 'predict_proba') else None
        
        metrics = ModelEvaluator.evaluate_binary(y_bin_test, y_pred, y_proba)
        ModelEvaluator.print_report(metrics, "RandomForest Binary")
        self.metrics['binary_rf'] = metrics
        
        # Save model
        joblib.dump(rf_binary, BINARY_RF_PATH)
        logger.info(f"Binary RF model saved to {BINARY_RF_PATH}")
        
        # Binary XGBoost
        if XGBOOST_AVAILABLE:
            xgb_binary = self.train_xgboost_binary(X_train, y_bin_train)
            if xgb_binary:
                models['binary_xgb'] = xgb_binary
                
                y_pred = xgb_binary.predict(X_test)
                y_proba = xgb_binary.predict_proba(X_test)[:, 1]
                
                metrics = ModelEvaluator.evaluate_binary(y_bin_test, y_pred, y_proba)
                ModelEvaluator.print_report(metrics, "XGBoost Binary")
                self.metrics['binary_xgb'] = metrics
                
                joblib.dump(xgb_binary, BINARY_XGB_PATH)
                logger.info(f"Binary XGB model saved to {BINARY_XGB_PATH}")
        
        # Multi-class RandomForest
        print("\n" + "=" * 60)
        print("🤖 TRAINING MULTI-CLASS CLASSIFIERS")
        print("=" * 60)
        
        rf_multi = self.train_random_forest_multiclass(X_train, y_multi_train)
        models['multiclass_rf'] = rf_multi
        
        y_pred = rf_multi.predict(X_test)
        
        metrics = ModelEvaluator.evaluate_multiclass(y_multi_test, y_pred, class_names)
        ModelEvaluator.print_report(metrics, "RandomForest Multi-Class", class_names)
        self.metrics['multiclass_rf'] = metrics
        
        # Save model
        joblib.dump(rf_multi, MULTI_RF_PATH)
        logger.info(f"Multi-class RF model saved to {MULTI_RF_PATH}")
        
        # Multi-class XGBoost
        if XGBOOST_AVAILABLE:
            xgb_multi = self.train_xgboost_multiclass(X_train, y_multi_train)
            if xgb_multi:
                models['multiclass_xgb'] = xgb_multi
                
                y_pred = xgb_multi.predict(X_test)
                
                metrics = ModelEvaluator.evaluate_multiclass(y_multi_test, y_pred, class_names)
                ModelEvaluator.print_report(metrics, "XGBoost Multi-Class", class_names)
                self.metrics['multiclass_xgb'] = metrics
                
                joblib.dump(xgb_multi, MULTI_XGB_PATH)
                logger.info(f"Multi-class XGB model saved to {MULTI_XGB_PATH}")
        
        # Feature importance analysis
        print("\n" + "=" * 60)
        print("📊 FEATURE IMPORTANCE ANALYSIS (Top 20)")
        print("=" * 60)
        
        for model_name, model in models.items():
            if model is None:
                continue
            top_features = self.get_feature_importance(model, feature_names, top_n=20)
            print(f"\n{model_name.upper()}:")
            for i, (feat, imp) in enumerate(top_features, 1):
                bar = "█" * int(imp * 50)
                print(f"  {i:2d}. {feat:25s} | {imp:.4f} {bar}")
            
            # Save to metadata
            self.metrics[model_name]['top_features'] = [(f, float(i)) for f, i in top_features]
        
        # Save metadata
        metadata = {
            'timestamp': datetime.now().isoformat(),
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'num_features': len(feature_names),
            'feature_names': feature_names,
            'class_names': class_names,
            'metrics': self.metrics,
            'models': {
                'binary_rf': BINARY_RF_PATH,
                'binary_xgb': BINARY_XGB_PATH if XGBOOST_AVAILABLE else None,
                'multiclass_rf': MULTI_RF_PATH,
                'multiclass_xgb': MULTI_XGB_PATH if XGBOOST_AVAILABLE else None,
            },
            'xgboost_available': XGBOOST_AVAILABLE,
        }
        
        with open(METADATA_PATH, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        total_time = time.time() - start_time
        
        # Final summary
        print("\n" + "=" * 60)
        print("✅ TRAINING PIPELINE COMPLETE")
        print("=" * 60)
        print(f"Total time: {total_time:.2f} seconds ({total_time/60:.2f} minutes)")
        print(f"\n📁 Output Models:")
        print(f"  Binary RF:        {BINARY_RF_PATH}")
        if XGBOOST_AVAILABLE:
            print(f"  Binary XGB:       {BINARY_XGB_PATH}")
        print(f"  Multi-class RF:   {MULTI_RF_PATH}")
        if XGBOOST_AVAILABLE:
            print(f"  Multi-class XGB:  {MULTI_XGB_PATH}")
        print(f"  Preprocessor:     {PREPROCESSOR_PATH}")
        print(f"  Feature Engineer: {FEATURE_ENG_PATH}")
        print(f"  Metadata:         {METADATA_PATH}")
        
        print(f"\n🎯 Best Model Performance:")
        best_f1 = 0
        best_model = None
        for name, metrics in self.metrics.items():
            f1 = metrics.get('f1', metrics.get('f1_weighted', 0))
            if f1 > best_f1:
                best_f1 = f1
                best_model = name
        print(f"  {best_model}: F1 = {best_f1:.4f}")
        
        return True


def train_network_models(max_samples: Optional[int] = None, test_size: float = 0.2) -> bool:
    """
    Main entry point for training network intrusion detection models.
    
    Args:
        max_samples: Limit samples per dataset (for testing)
        test_size: Fraction of data for testing
        
    Returns:
        True if training succeeded, False otherwise
    """
    trainer = NetworkTrainer(max_samples=max_samples, test_size=test_size)
    return trainer.run_full_pipeline()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Train network intrusion detection models')
    parser.add_argument('--max-samples', type=int, default=None,
                        help='Limit samples per dataset (for testing)')
    parser.add_argument('--test-size', type=float, default=0.2,
                        help='Fraction of data for testing (default: 0.2)')
    parser.add_argument('--quick', action='store_true',
                        help='Quick test mode (1000 samples per dataset)')
    
    args = parser.parse_args()
    
    max_samples = 1000 if args.quick else args.max_samples
    
    success = train_network_models(max_samples=max_samples, test_size=args.test_size)
    
    sys.exit(0 if success else 1)

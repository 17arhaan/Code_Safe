#!/usr/bin/env python3
"""
Advanced Machine Learning Engine
Comprehensive ML pipeline with multiple algorithms and optimization techniques.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder, OneHotEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.svm import SVC, SVR
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.decomposition import PCA, FastICA, TruncatedSVD
from sklearn.feature_selection import SelectKBest, RFE, SelectFromModel
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
                           roc_auc_score, mean_squared_error, r2_score, silhouette_score)
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
import joblib
import pickle
import json
import logging
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from dataclasses import dataclass, field
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Deep Learning imports
try:
    import tensorflow as tf
    from tensorflow.keras.models import Sequential, Model
    from tensorflow.keras.layers import Dense, Dropout, BatchNormalization, Activation
    from tensorflow.keras.optimizers import Adam, RMSprop, SGD
    from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    print("TensorFlow not available. Deep learning features will be disabled.")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """Configuration for machine learning models."""
    model_type: str = "random_forest"
    test_size: float = 0.2
    random_state: int = 42
    cv_folds: int = 5
    scoring: str = "accuracy"
    n_jobs: int = -1
    verbose: int = 1
    
    # Hyperparameter search
    use_grid_search: bool = True
    n_iter: int = 100
    
    # Feature engineering
    feature_selection: bool = True
    n_features: int = 10
    dimensionality_reduction: bool = False
    n_components: int = 5
    
    # Deep learning
    epochs: int = 100
    batch_size: int = 32
    learning_rate: float = 0.001
    early_stopping_patience: int = 10

class DataPreprocessor:
    """Advanced data preprocessing pipeline."""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.scalers = {}
        self.encoders = {}
        self.feature_selector = None
        self.dim_reducer = None
        
    def preprocess_data(self, X: pd.DataFrame, y: pd.Series = None, fit: bool = True) -> Tuple[np.ndarray, np.ndarray]:
        """Preprocess the dataset."""
        logger.info("Starting data preprocessing")
        
        # Handle missing values
        X_processed = self._handle_missing_values(X)
        
        # Encode categorical variables
        X_processed = self._encode_categorical(X_processed, fit)
        
        # Scale numerical features
        X_processed = self._scale_features(X_processed, fit)
        
        # Feature selection
        if self.config.feature_selection and y is not None:
            X_processed = self._select_features(X_processed, y, fit)
        
        # Dimensionality reduction
        if self.config.dimensionality_reduction:
            X_processed = self._reduce_dimensions(X_processed, fit)
        
        # Convert to numpy arrays
        X_array = X_processed.values if isinstance(X_processed, pd.DataFrame) else X_processed
        y_array = y.values if y is not None else None
        
        logger.info(f"Preprocessing completed. Shape: {X_array.shape}")
        return X_array, y_array
    
    def _handle_missing_values(self, X: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values in the dataset."""
        logger.info("Handling missing values")
        
        # For numerical columns, fill with median
        numerical_cols = X.select_dtypes(include=[np.number]).columns
        for col in numerical_cols:
            X[col].fillna(X[col].median(), inplace=True)
        
        # For categorical columns, fill with mode
        categorical_cols = X.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            X[col].fillna(X[col].mode()[0] if not X[col].mode().empty else 'Unknown', inplace=True)
        
        return X
    
    def _encode_categorical(self, X: pd.DataFrame, fit: bool = True) -> pd.DataFrame:
        """Encode categorical variables."""
        logger.info("Encoding categorical variables")
        
        categorical_cols = X.select_dtypes(include=['object']).columns
        
        for col in categorical_cols:
            if fit:
                if X[col].nunique() <= 10:  # Use label encoding for low cardinality
                    encoder = LabelEncoder()
                    X[col] = encoder.fit_transform(X[col].astype(str))
                    self.encoders[col] = encoder
                else:  # Use one-hot encoding for high cardinality
                    encoder = OneHotEncoder(sparse=False, handle_unknown='ignore')
                    encoded = encoder.fit_transform(X[[col]])
                    encoded_df = pd.DataFrame(encoded, columns=[f"{col}_{i}" for i in range(encoded.shape[1])])
                    X = pd.concat([X.drop(columns=[col]), encoded_df], axis=1)
                    self.encoders[col] = encoder
            else:
                if col in self.encoders:
                    if isinstance(self.encoders[col], LabelEncoder):
                        X[col] = self.encoders[col].transform(X[col].astype(str))
                    else:
                        # Handle one-hot encoding for new data
                        pass
        
        return X
    
    def _scale_features(self, X: pd.DataFrame, fit: bool = True) -> pd.DataFrame:
        """Scale numerical features."""
        logger.info("Scaling features")
        
        numerical_cols = X.select_dtypes(include=[np.number]).columns
        
        if fit:
            scaler = StandardScaler()
            X[numerical_cols] = scaler.fit_transform(X[numerical_cols])
            self.scalers['standard'] = scaler
        else:
            if 'standard' in self.scalers:
                X[numerical_cols] = self.scalers['standard'].transform(X[numerical_cols])
        
        return X
    
    def _select_features(self, X: pd.DataFrame, y: pd.Series, fit: bool = True) -> pd.DataFrame:
        """Select the most important features."""
        logger.info("Selecting features")
        
        if fit:
            selector = SelectKBest(k=self.config.n_features)
            X_selected = selector.fit_transform(X, y)
            self.feature_selector = selector
            
            # Get selected feature names
            selected_features = X.columns[selector.get_support()].tolist()
            logger.info(f"Selected features: {selected_features}")
            
            return pd.DataFrame(X_selected, columns=selected_features)
        else:
            if self.feature_selector:
                X_selected = self.feature_selector.transform(X)
                selected_features = X.columns[self.feature_selector.get_support()].tolist()
                return pd.DataFrame(X_selected, columns=selected_features)
        
        return X
    
    def _reduce_dimensions(self, X: pd.DataFrame, fit: bool = True) -> pd.DataFrame:
        """Reduce dimensionality using PCA."""
        logger.info("Reducing dimensions")
        
        if fit:
            reducer = PCA(n_components=self.config.n_components)
            X_reduced = reducer.fit_transform(X)
            self.dim_reducer = reducer
            
            logger.info(f"Explained variance ratio: {reducer.explained_variance_ratio_}")
            return pd.DataFrame(X_reduced, columns=[f"PC{i+1}" for i in range(self.config.n_components)])
        else:
            if self.dim_reducer:
                X_reduced = self.dim_reducer.transform(X)
                return pd.DataFrame(X_reduced, columns=[f"PC{i+1}" for i in range(self.config.n_components)])
        
        return X

class MLModel:
    """Base class for machine learning models."""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.model = None
        self.preprocessor = DataPreprocessor(config)
        self.training_history = {}
        
    def train(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, Any]:
        """Train the model."""
        logger.info(f"Training {self.config.model_type} model")
        
        # Preprocess data
        X_processed, y_processed = self.preprocessor.preprocess_data(X, y, fit=True)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_processed, y_processed, 
            test_size=self.config.test_size, 
            random_state=self.config.random_state
        )
        
        # Create and train model
        self.model = self._create_model()
        
        if self.config.use_grid_search:
            self.model = self._optimize_hyperparameters(X_train, y_train)
        
        # Train the model
        start_time = pd.Timestamp.now()
        self.model.fit(X_train, y_train)
        training_time = (pd.Timestamp.now() - start_time).total_seconds()
        
        # Evaluate model
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        
        # Cross-validation
        cv_scores = cross_val_score(self.model, X_train, y_train, cv=self.config.cv_folds)
        
        self.training_history = {
            'training_time': training_time,
            'train_score': train_score,
            'test_score': test_score,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'cv_scores': cv_scores.tolist()
        }
        
        logger.info(f"Training completed. Test score: {test_score:.4f}")
        return self.training_history
    
    def _create_model(self):
        """Create the model based on configuration."""
        model_type = self.config.model_type.lower()
        
        if model_type == "random_forest":
            return RandomForestClassifier(
                n_estimators=100,
                random_state=self.config.random_state,
                n_jobs=self.config.n_jobs
            )
        elif model_type == "gradient_boosting":
            return GradientBoostingClassifier(random_state=self.config.random_state)
        elif model_type == "logistic_regression":
            return LogisticRegression(random_state=self.config.random_state, max_iter=1000)
        elif model_type == "svm":
            return SVC(random_state=self.config.random_state, probability=True)
        elif model_type == "neural_network":
            if TENSORFLOW_AVAILABLE:
                return self._create_neural_network()
            else:
                return MLPClassifier(random_state=self.config.random_state, max_iter=1000)
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
    
    def _create_neural_network(self):
        """Create a neural network model using TensorFlow."""
        if not TENSORFLOW_AVAILABLE:
            return MLPClassifier(random_state=self.config.random_state)
        
        model = Sequential([
            Dense(128, activation='relu', input_shape=(None,)),
            BatchNormalization(),
            Dropout(0.3),
            Dense(64, activation='relu'),
            BatchNormalization(),
            Dropout(0.3),
            Dense(32, activation='relu'),
            Dropout(0.2),
            Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer=Adam(learning_rate=self.config.learning_rate),
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def _optimize_hyperparameters(self, X_train: np.ndarray, y_train: np.ndarray):
        """Optimize hyperparameters using grid search."""
        logger.info("Optimizing hyperparameters")
        
        model_type = self.config.model_type.lower()
        
        if model_type == "random_forest":
            param_grid = {
                'n_estimators': [50, 100, 200],
                'max_depth': [None, 10, 20, 30],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4]
            }
            base_model = RandomForestClassifier(random_state=self.config.random_state)
            
        elif model_type == "gradient_boosting":
            param_grid = {
                'n_estimators': [50, 100, 200],
                'learning_rate': [0.01, 0.1, 0.2],
                'max_depth': [3, 5, 7],
                'subsample': [0.8, 0.9, 1.0]
            }
            base_model = GradientBoostingClassifier(random_state=self.config.random_state)
            
        elif model_type == "logistic_regression":
            param_grid = {
                'C': [0.1, 1, 10, 100],
                'penalty': ['l1', 'l2', 'elasticnet'],
                'solver': ['liblinear', 'saga']
            }
            base_model = LogisticRegression(random_state=self.config.random_state, max_iter=1000)
            
        else:
            return self._create_model()
        
        if self.config.use_grid_search:
            search = GridSearchCV(
                base_model, param_grid, 
                cv=self.config.cv_folds, 
                scoring=self.config.scoring,
                n_jobs=self.config.n_jobs,
                verbose=self.config.verbose
            )
        else:
            search = RandomizedSearchCV(
                base_model, param_grid, 
                n_iter=self.config.n_iter,
                cv=self.config.cv_folds, 
                scoring=self.config.scoring,
                n_jobs=self.config.n_jobs,
                verbose=self.config.verbose
            )
        
        search.fit(X_train, y_train)
        logger.info(f"Best parameters: {search.best_params_}")
        logger.info(f"Best score: {search.best_score_:.4f}")
        
        return search.best_estimator_
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make predictions on new data."""
        if self.model is None:
            raise ValueError("Model must be trained before making predictions")
        
        X_processed, _ = self.preprocessor.preprocess_data(X, fit=False)
        return self.model.predict(X_processed)
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Get prediction probabilities."""
        if self.model is None:
            raise ValueError("Model must be trained before making predictions")
        
        X_processed, _ = self.preprocessor.preprocess_data(X, fit=False)
        
        if hasattr(self.model, 'predict_proba'):
            return self.model.predict_proba(X_processed)
        else:
            # For models without predict_proba, return confidence scores
            predictions = self.model.predict(X_processed)
            return np.column_stack([1 - predictions, predictions])
    
    def evaluate(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
        """Evaluate the model on test data."""
        predictions = self.predict(X)
        
        # Calculate metrics
        accuracy = accuracy_score(y, predictions)
        precision = precision_score(y, predictions, average='weighted')
        recall = recall_score(y, predictions, average='weighted')
        f1 = f1_score(y, predictions, average='weighted')
        
        metrics = {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1
        }
        
        # Add ROC AUC if binary classification
        if len(np.unique(y)) == 2:
            try:
                proba = self.predict_proba(X)
                roc_auc = roc_auc_score(y, proba[:, 1])
                metrics['roc_auc'] = roc_auc
            except:
                pass
        
        return metrics
    
    def save_model(self, filepath: str):
        """Save the trained model."""
        model_data = {
            'model': self.model,
            'preprocessor': self.preprocessor,
            'config': self.config,
            'training_history': self.training_history
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load a trained model."""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.preprocessor = model_data['preprocessor']
        self.config = model_data['config']
        self.training_history = model_data['training_history']
        
        logger.info(f"Model loaded from {filepath}")

class EnsembleModel:
    """Ensemble model combining multiple algorithms."""
    
    def __init__(self, models: List[MLModel], voting_type: str = 'soft'):
        self.models = models
        self.voting_type = voting_type
        self.ensemble_model = None
        
    def train(self, X: pd.DataFrame, y: pd.Series):
        """Train all models in the ensemble."""
        logger.info("Training ensemble model")
        
        # Train individual models
        for i, model in enumerate(self.models):
            logger.info(f"Training model {i+1}/{len(self.models)}")
            model.train(X, y)
        
        # Create voting classifier
        estimators = [(f"model_{i}", model.model) for i, model in enumerate(self.models)]
        self.ensemble_model = VotingClassifier(estimators, voting=self.voting_type)
        
        # Preprocess data for ensemble
        X_processed, y_processed = self.models[0].preprocessor.preprocess_data(X, y, fit=False)
        
        # Train ensemble
        self.ensemble_model.fit(X_processed, y_processed)
        
        logger.info("Ensemble training completed")
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Make ensemble predictions."""
        if self.ensemble_model is None:
            raise ValueError("Ensemble must be trained before making predictions")
        
        X_processed, _ = self.models[0].preprocessor.preprocess_data(X, fit=False)
        return self.ensemble_model.predict(X_processed)
    
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Get ensemble prediction probabilities."""
        if self.ensemble_model is None:
            raise ValueError("Ensemble must be trained before making predictions")
        
        X_processed, _ = self.models[0].preprocessor.preprocess_data(X, fit=False)
        return self.ensemble_model.predict_proba(X_processed)

def create_sample_data(n_samples: int = 10000, n_features: int = 20) -> Tuple[pd.DataFrame, pd.Series]:
    """Create sample dataset for testing."""
    logger.info(f"Creating sample dataset with {n_samples} samples and {n_features} features")
    
    # Generate random features
    np.random.seed(42)
    X = pd.DataFrame(
        np.random.randn(n_samples, n_features),
        columns=[f'feature_{i}' for i in range(n_features)]
    )
    
    # Add some categorical features
    X['category'] = np.random.choice(['A', 'B', 'C', 'D'], n_samples)
    X['binary'] = np.random.choice([0, 1], n_samples)
    
    # Create target variable with some relationship to features
    y = (X['feature_0'] + X['feature_1'] * 2 + np.random.randn(n_samples) * 0.1 > 0).astype(int)
    
    return X, y

def main():
    """Main function to demonstrate the ML engine."""
    logger.info("Starting Machine Learning Engine Demo")
    
    # Create sample data
    X, y = create_sample_data(n_samples=5000, n_features=15)
    logger.info(f"Dataset shape: {X.shape}, Target distribution: {y.value_counts().to_dict()}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Test different models
    model_types = ['random_forest', 'gradient_boosting', 'logistic_regression', 'svm']
    results = {}
    
    for model_type in model_types:
        logger.info(f"\n{'='*50}")
        logger.info(f"Testing {model_type}")
        logger.info(f"{'='*50}")
        
        # Create and train model
        config = ModelConfig(
            model_type=model_type,
            feature_selection=True,
            n_features=10,
            use_grid_search=True
        )
        
        model = MLModel(config)
        training_history = model.train(X_train, y_train)
        
        # Evaluate model
        metrics = model.evaluate(X_test, y_test)
        
        results[model_type] = {
            'training_history': training_history,
            'metrics': metrics
        }
        
        logger.info(f"Test metrics: {metrics}")
    
    # Create ensemble model
    logger.info(f"\n{'='*50}")
    logger.info("Testing Ensemble Model")
    logger.info(f"{'='*50}")
    
    # Create individual models
    models = []
    for model_type in ['random_forest', 'gradient_boosting', 'logistic_regression']:
        config = ModelConfig(model_type=model_type, feature_selection=True, n_features=10)
        model = MLModel(config)
        model.train(X_train, y_train)
        models.append(model)
    
    # Create ensemble
    ensemble = EnsembleModel(models, voting_type='soft')
    ensemble.train(X_train, y_train)
    
    # Evaluate ensemble
    ensemble_metrics = ensemble.evaluate(X_test, y_test)
    logger.info(f"Ensemble metrics: {ensemble_metrics}")
    
    # Print summary
    logger.info(f"\n{'='*50}")
    logger.info("RESULTS SUMMARY")
    logger.info(f"{'='*50}")
    
    for model_type, result in results.items():
        logger.info(f"{model_type}: {result['metrics']['accuracy']:.4f}")
    
    logger.info(f"Ensemble: {ensemble_metrics['accuracy']:.4f}")
    
    logger.info("Demo completed successfully!")

if __name__ == "__main__":
    main()

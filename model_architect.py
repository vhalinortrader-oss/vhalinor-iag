"""
Model Architect - Sistema de Modelagem de IA
===========================================
Criação e gerenciamento de modelos: redes neurais, árvores de decisão, SVM, etc.
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import os
from pathlib import Path
import hashlib
import pickle
import math

# Importações condicionais
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    import torch.nn.functional as F
    from torch.utils.data import DataLoader, TensorDataset
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False

try:
    from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier, GradientBoostingRegressor
    from sklearn.svm import SVC, SVR
    from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
    from sklearn.linear_model import LogisticRegression, LinearRegression, Ridge, Lasso
    from sklearn.naive_bayes import GaussianNB, MultinomialNB
    from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import xgboost as xgb
    import lightgbm as lgb
    XGB_AVAILABLE = True
except ImportError:
    XGB_AVAILABLE = False

from config import settings
from core import get_logger, log_execution
from .feature_engineering import FeatureSet


class ModelType(str, Enum):
    """Tipos de modelos"""
    NEURAL_NETWORK = "neural_network"
    RANDOM_FOREST = "random_forest"
    GRADIENT_BOOSTING = "gradient_boosting"
    SVM = "svm"
    DECISION_TREE = "decision_tree"
    LOGISTIC_REGRESSION = "logistic_regression"
    LINEAR_REGRESSION = "linear_regression"
    KNN = "knn"
    NAIVE_BAYES = "naive_bayes"
    XGBOOST = "xgboost"
    LIGHTGBM = "lightgbm"
    ENSEMBLE = "ensemble"


class TaskType(str, Enum):
    """Tipos de tarefas"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    DIMENSIONALITY_REDUCTION = "dimensionality_reduction"
    ANOMALY_DETECTION = "anomaly_detection"
    TIME_SERIES = "time_series"
    NLP = "nlp"
    COMPUTER_VISION = "computer_vision"


class ArchitectureType(str, Enum):
    """Tipos de arquitetura de rede neural"""
    MLP = "mlp"
    CNN = "cnn"
    RNN = "rnn"
    LSTM = "lstm"
    GRU = "gru"
    TRANSFORMER = "transformer"
    AUTOENCODER = "autoencoder"
    GAN = "gan"
    RESNET = "resnet"
    VGG = "vgg"
    CUSTOM = "custom"


class ActivationFunction(str, Enum):
    """Funções de ativação"""
    RELU = "relu"
    SIGMOID = "sigmoid"
    TANH = "tanh"
    LEAKY_RELU = "leaky_relu"
    ELU = "elu"
    GELU = "gelu"
    SWISH = "swish"
    SOFTMAX = "softmax"


class OptimizerType(str, Enum):
    """Tipos de otimizadores"""
    ADAM = "adam"
    SGD = "sgd"
    RMSPROP = "rmsprop"
    ADAGRAD = "adagrad"
    ADADELTA = "adadelta"
    ADAMW = "adamw"
    ADAMAX = "adamax"


@dataclass
class ModelConfig:
    """Configuração de modelo"""
    model_type: ModelType
    task_type: TaskType
    architecture_type: Optional[ArchitectureType] = None
    hyperparameters: Dict[str, Any] = field(default_factory=dict)
    input_shape: Optional[Tuple[int, ...]] = None
    output_shape: Optional[Tuple[int, ...]] = None
    activation: ActivationFunction = ActivationFunction.RELU
    optimizer: OptimizerType = OptimizerType.ADAM
    loss_function: Optional[str] = None
    metrics: List[str] = field(default_factory=list)
    regularization: Dict[str, Any] = field(default_factory=dict)
    custom_params: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'model_type': self.model_type.value,
            'task_type': self.task_type.value,
            'architecture_type': self.architecture_type.value if self.architecture_type else None,
            'hyperparameters': self.hyperparameters,
            'input_shape': self.input_shape,
            'output_shape': self.output_shape,
            'activation': self.activation.value,
            'optimizer': self.optimizer.value,
            'loss_function': self.loss_function,
            'metrics': self.metrics,
            'regularization': self.regularization,
            'custom_params': self.custom_params
        }


@dataclass
class ModelInfo:
    """Informações do modelo treinado"""
    name: str
    model_type: ModelType
    task_type: TaskType
    config: ModelConfig
    model: Any
    performance_metrics: Dict[str, float]
    training_history: Dict[str, List[float]]
    feature_importance: Optional[Dict[str, float]] = None
    training_time: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    file_path: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'model_type': self.model_type.value,
            'task_type': self.task_type.value,
            'config': self.config.to_dict(),
            'performance_metrics': self.performance_metrics,
            'training_history': self.training_history,
            'feature_importance': self.feature_importance,
            'training_time': self.training_time,
            'created_at': self.created_at.isoformat(),
            'file_path': self.file_path
        }


class NeuralNetworkBuilder:
    """Construtor de redes neurais"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.models.neural", "neural_builder")
    
    def build_mlp(self, config: ModelConfig) -> nn.Module:
        """Constrói MLP (Multi-Layer Perceptron)"""
        if not PYTORCH_AVAILABLE:
            raise ImportError("torch is required for neural networks")
        
        class MLP(nn.Module):
            def __init__(self, input_dim, hidden_dims, output_dim, activation, dropout_rate=0.0):
                super(MLP, self).__init__()
                
                layers = []
                dims = [input_dim] + hidden_dims + [output_dim]
                
                for i in range(len(dims) - 1):
                    layers.append(nn.Linear(dims[i], dims[i + 1]))
                    
                    if i < len(dims) - 2:  # Não adicionar ativação na última camada
                        if activation == ActivationFunction.RELU:
                            layers.append(nn.ReLU())
                        elif activation == ActivationFunction.SIGMOID:
                            layers.append(nn.Sigmoid())
                        elif activation == ActivationFunction.TANH:
                            layers.append(nn.Tanh())
                        elif activation == ActivationFunction.LEAKY_RELU:
                            layers.append(nn.LeakyReLU(0.01))
                        elif activation == ActivationFunction.ELU:
                            layers.append(nn.ELU())
                        
                        if dropout_rate > 0:
                            layers.append(nn.Dropout(dropout_rate))
                
                self.network = nn.Sequential(*layers)
            
            def forward(self, x):
                return self.network(x)
        
        input_dim = config.input_shape[0] if config.input_shape else 784
        hidden_dims = config.hyperparameters.get('hidden_dims', [128, 64, 32])
        output_dim = config.output_shape[0] if config.output_shape else 10
        activation = config.activation
        dropout_rate = config.hyperparameters.get('dropout_rate', 0.0)
        
        return MLP(input_dim, hidden_dims, output_dim, activation, dropout_rate)
    
    def build_cnn(self, config: ModelConfig) -> nn.Module:
        """Constrói CNN (Convolutional Neural Network)"""
        if not PYTORCH_AVAILABLE:
            raise ImportError("torch is required for neural networks")
        
        class CNN(nn.Module):
            def __init__(self, input_shape, num_classes, conv_layers, fc_layers, activation):
                super(CNN, self).__init__()
                
                # Camadas convolucionais
                self.conv_layers = nn.ModuleList()
                in_channels = input_shape[0] if len(input_shape) == 3 else 1
                
                for conv_config in conv_layers:
                    out_channels, kernel_size, stride, padding = conv_config
                    self.conv_layers.append(nn.Conv2d(in_channels, out_channels, kernel_size, stride, padding))
                    self.conv_layers.append(self._get_activation(activation))
                    self.conv_layers.append(nn.MaxPool2d(2, 2))
                    in_channels = out_channels
                
                # Calcular tamanho da feature map após conv layers
                self._calculate_conv_output_size(input_shape, conv_layers)
                
                # Camadas fully connected
                self.fc_layers = nn.ModuleList()
                fc_input_size = self.conv_output_size
                
                for i, fc_size in enumerate(fc_layers):
                    if i == len(fc_layers) - 1:  # Última camada
                        self.fc_layers.append(nn.Linear(fc_input_size, fc_size))
                    else:
                        self.fc_layers.append(nn.Linear(fc_input_size, fc_size))
                        self.fc_layers.append(self._get_activation(activation))
                        self.fc_layers.append(nn.Dropout(0.5))
                    fc_input_size = fc_size
            
            def _get_activation(self, activation):
                if activation == ActivationFunction.RELU:
                    return nn.ReLU()
                elif activation == ActivationFunction.SIGMOID:
                    return nn.Sigmoid()
                elif activation == ActivationFunction.TANH:
                    return nn.Tanh()
                elif activation == ActivationFunction.LEAKY_RELU:
                    return nn.LeakyReLU(0.01)
                else:
                    return nn.ReLU()
            
            def _calculate_conv_output_size(self, input_shape, conv_layers):
                # Simplified calculation
                h, w = input_shape[1], input_shape[2]
                for _ in conv_layers:
                    h = h // 2  # MaxPool2d
                    w = w // 2
                self.conv_output_size = h * w * conv_layers[-1][0]  # last conv layer out_channels
            
            def forward(self, x):
                for layer in self.conv_layers:
                    x = layer(x)
                
                x = x.view(x.size(0), -1)  # Flatten
                
                for layer in self.fc_layers:
                    x = layer(x)
                
                return x
        
        input_shape = config.input_shape or (1, 28, 28)
        num_classes = config.output_shape[0] if config.output_shape else 10
        conv_layers = config.hyperparameters.get('conv_layers', [(32, 3, 1, 1), (64, 3, 1, 1)])
        fc_layers = config.hyperparameters.get('fc_layers', [128, num_classes])
        activation = config.activation
        
        return CNN(input_shape, num_classes, conv_layers, fc_layers, activation)
    
    def build_lstm(self, config: ModelConfig) -> nn.Module:
        """Constrói LSTM (Long Short-Term Memory)"""
        if not PYTORCH_AVAILABLE:
            raise ImportError("torch is required for neural networks")
        
        class LSTM(nn.Module):
            def __init__(self, input_size, hidden_size, num_layers, output_size, dropout=0.0):
                super(LSTM, self).__init__()
                
                self.hidden_size = hidden_size
                self.num_layers = num_layers
                
                self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=dropout)
                self.fc = nn.Linear(hidden_size, output_size)
                self.dropout = nn.Dropout(dropout)
            
            def forward(self, x):
                # Inicializar hidden state
                h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
                c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
                
                # Forward pass LSTM
                out, _ = self.lstm(x, (h0, c0))
                
                # Pegar última saída
                out = self.dropout(out[:, -1, :])
                out = self.fc(out)
                
                return out
        
        input_size = config.input_shape[1] if config.input_shape and len(config.input_shape) > 1 else 1
        hidden_size = config.hyperparameters.get('hidden_size', 128)
        num_layers = config.hyperparameters.get('num_layers', 2)
        output_size = config.output_shape[0] if config.output_shape else 1
        dropout = config.hyperparameters.get('dropout', 0.0)
        
        return LSTM(input_size, hidden_size, num_layers, output_size, dropout)


class SklearnModelBuilder:
    """Construtor de modelos Scikit-learn"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.models.sklearn", "sklearn_builder")
    
    def build_random_forest(self, config: ModelConfig):
        """Constrói Random Forest"""
        if not SKLEARN_AVAILABLE:
            raise ImportError("sklearn is required for Random Forest")
        
        params = config.hyperparameters
        
        if config.task_type == TaskType.CLASSIFICATION:
            return RandomForestClassifier(
                n_estimators=params.get('n_estimators', 100),
                max_depth=params.get('max_depth', None),
                min_samples_split=params.get('min_samples_split', 2),
                min_samples_leaf=params.get('min_samples_leaf', 1),
                random_state=params.get('random_state', 42),
                n_jobs=params.get('n_jobs', -1)
            )
        else:  # REGRESSION
            return RandomForestRegressor(
                n_estimators=params.get('n_estimators', 100),
                max_depth=params.get('max_depth', None),
                min_samples_split=params.get('min_samples_split', 2),
                min_samples_leaf=params.get('min_samples_leaf', 1),
                random_state=params.get('random_state', 42),
                n_jobs=params.get('n_jobs', -1)
            )
    
    def build_gradient_boosting(self, config: ModelConfig):
        """Constrói Gradient Boosting"""
        if not SKLEARN_AVAILABLE:
            raise ImportError("sklearn is required for Gradient Boosting")
        
        params = config.hyperparameters
        
        if config.task_type == TaskType.CLASSIFICATION:
            return GradientBoostingClassifier(
                n_estimators=params.get('n_estimators', 100),
                learning_rate=params.get('learning_rate', 0.1),
                max_depth=params.get('max_depth', 3),
                random_state=params.get('random_state', 42)
            )
        else:  # REGRESSION
            return GradientBoostingRegressor(
                n_estimators=params.get('n_estimators', 100),
                learning_rate=params.get('learning_rate', 0.1),
                max_depth=params.get('max_depth', 3),
                random_state=params.get('random_state', 42)
            )
    
    def build_svm(self, config: ModelConfig):
        """Constrói SVM"""
        if not SKLEARN_AVAILABLE:
            raise ImportError("sklearn is required for SVM")
        
        params = config.hyperparameters
        
        if config.task_type == TaskType.CLASSIFICATION:
            return SVC(
                C=params.get('C', 1.0),
                kernel=params.get('kernel', 'rbf'),
                gamma=params.get('gamma', 'scale'),
                probability=params.get('probability', True),
                random_state=params.get('random_state', 42)
            )
        else:  # REGRESSION
            return SVR(
                C=params.get('C', 1.0),
                kernel=params.get('kernel', 'rbf'),
                gamma=params.get('gamma', 'scale')
            )
    
    def build_decision_tree(self, config: ModelConfig):
        """Constrói Decision Tree"""
        if not SKLEARN_AVAILABLE:
            raise ImportError("sklearn is required for Decision Tree")
        
        params = config.hyperparameters
        
        if config.task_type == TaskType.CLASSIFICATION:
            return DecisionTreeClassifier(
                max_depth=params.get('max_depth', None),
                min_samples_split=params.get('min_samples_split', 2),
                min_samples_leaf=params.get('min_samples_leaf', 1),
                random_state=params.get('random_state', 42)
            )
        else:  # REGRESSION
            return DecisionTreeRegressor(
                max_depth=params.get('max_depth', None),
                min_samples_split=params.get('min_samples_split', 2),
                min_samples_leaf=params.get('min_samples_leaf', 1),
                random_state=params.get('random_state', 42)
            )
    
    def build_logistic_regression(self, config: ModelConfig):
        """Constrói Logistic Regression"""
        if not SKLEARN_AVAILABLE:
            raise ImportError("sklearn is required for Logistic Regression")
        
        params = config.hyperparameters
        
        return LogisticRegression(
            C=params.get('C', 1.0),
            penalty=params.get('penalty', 'l2'),
            solver=params.get('solver', 'lbfgs'),
            max_iter=params.get('max_iter', 1000),
            random_state=params.get('random_state', 42)
        )
    
    def build_linear_regression(self, config: ModelConfig):
        """Constrói Linear Regression"""
        if not SKLEARN_AVAILABLE:
            raise ImportError("sklearn is required for Linear Regression")
        
        params = config.hyperparameters
        
        if params.get('ridge', False):
            return Ridge(alpha=params.get('alpha', 1.0), random_state=params.get('random_state', 42))
        elif params.get('lasso', False):
            return Lasso(alpha=params.get('alpha', 1.0), random_state=params.get('random_state', 42))
        else:
            return LinearRegression()
    
    def build_knn(self, config: ModelConfig):
        """Constrói KNN"""
        if not SKLEARN_AVAILABLE:
            raise ImportError("sklearn is required for KNN")
        
        params = config.hyperparameters
        
        if config.task_type == TaskType.CLASSIFICATION:
            return KNeighborsClassifier(
                n_neighbors=params.get('n_neighbors', 5),
                weights=params.get('weights', 'uniform'),
                algorithm=params.get('algorithm', 'auto')
            )
        else:  # REGRESSION
            return KNeighborsRegressor(
                n_neighbors=params.get('n_neighbors', 5),
                weights=params.get('weights', 'uniform'),
                algorithm=params.get('algorithm', 'auto')
            )
    
    def build_naive_bayes(self, config: ModelConfig):
        """Constrói Naive Bayes"""
        if not SKLEARN_AVAILABLE:
            raise ImportError("sklearn is required for Naive Bayes")
        
        params = config.hyperparameters
        
        if params.get('multinomial', False):
            return MultinomialNB(alpha=params.get('alpha', 1.0))
        else:
            return GaussianNB()


class EnsembleBuilder:
    """Construtor de modelos ensemble"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.models.ensemble", "ensemble_builder")
    
    def build_voting_ensemble(self, models: List[Tuple[str, Any]], voting: str = 'hard'):
        """Constrói Voting Ensemble"""
        if not SKLEARN_AVAILABLE:
            raise ImportError("sklearn is required for ensemble methods")
        
        from sklearn.ensemble import VotingClassifier, VotingRegressor
        
        if any('classifier' in str(type(model)).lower() for _, model in models):
            return VotingClassifier(estimators=models, voting=voting)
        else:
            return VotingRegressor(estimators=models)
    
    def build_stacking_ensemble(self, models: List[Tuple[str, Any]], meta_model: Any):
        """Constrói Stacking Ensemble"""
        if not SKLEARN_AVAILABLE:
            raise ImportError("sklearn is required for ensemble methods")
        
        from sklearn.ensemble import StackingClassifier, StackingRegressor
        
        if any('classifier' in str(type(model)).lower() for _, model in models):
            return StackingClassifier(estimators=models, final_estimator=meta_model, cv=5)
        else:
            return StackingRegressor(estimators=models, final_estimator=meta_model, cv=5)


class ModelArchitect:
    """Arquiteto principal de modelos"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.models.architect", "model_architect")
        
        # Inicializar builders
        self.neural_builder = NeuralNetworkBuilder()
        self.sklearn_builder = SklearnModelBuilder()
        self.ensemble_builder = EnsembleBuilder()
        
        self.models = {}
        self.model_history = []
    
    @log_execution(component="models", operation="create_model")
    def create_model(self, config: ModelConfig) -> Any:
        """Cria modelo baseado na configuração"""
        self.logger.info(f"Creating {config.model_type.value} model for {config.task_type.value}")
        
        try:
            if config.model_type in [ModelType.NEURAL_NETWORK]:
                # Redes neurais
                if config.architecture_type == ArchitectureType.MLP:
                    return self.neural_builder.build_mlp(config)
                elif config.architecture_type == ArchitectureType.CNN:
                    return self.neural_builder.build_cnn(config)
                elif config.architecture_type == ArchitectureType.LSTM:
                    return self.neural_builder.build_lstm(config)
                else:
                    raise ValueError(f"Unsupported neural architecture: {config.architecture_type}")
            
            elif config.model_type == ModelType.RANDOM_FOREST:
                return self.sklearn_builder.build_random_forest(config)
            
            elif config.model_type == ModelType.GRADIENT_BOOSTING:
                return self.sklearn_builder.build_gradient_boosting(config)
            
            elif config.model_type == ModelType.SVM:
                return self.sklearn_builder.build_svm(config)
            
            elif config.model_type == ModelType.DECISION_TREE:
                return self.sklearn_builder.build_decision_tree(config)
            
            elif config.model_type == ModelType.LOGISTIC_REGRESSION:
                return self.sklearn_builder.build_logistic_regression(config)
            
            elif config.model_type == ModelType.LINEAR_REGRESSION:
                return self.sklearn_builder.build_linear_regression(config)
            
            elif config.model_type == ModelType.KNN:
                return self.sklearn_builder.build_knn(config)
            
            elif config.model_type == ModelType.NAIVE_BAYES:
                return self.sklearn_builder.build_naive_bayes(config)
            
            elif config.model_type == ModelType.XGBOOST:
                if not XGB_AVAILABLE:
                    raise ImportError("xgboost is required for XGBoost models")
                
                params = config.hyperparameters
                if config.task_type == TaskType.CLASSIFICATION:
                    return xgb.XGBClassifier(
                        n_estimators=params.get('n_estimators', 100),
                        learning_rate=params.get('learning_rate', 0.1),
                        max_depth=params.get('max_depth', 6),
                        random_state=params.get('random_state', 42)
                    )
                else:
                    return xgb.XGBRegressor(
                        n_estimators=params.get('n_estimators', 100),
                        learning_rate=params.get('learning_rate', 0.1),
                        max_depth=params.get('max_depth', 6),
                        random_state=params.get('random_state', 42)
                    )
            
            elif config.model_type == ModelType.LIGHTGBM:
                if not XGB_AVAILABLE:
                    raise ImportError("lightgbm is required for LightGBM models")
                
                params = config.hyperparameters
                if config.task_type == TaskType.CLASSIFICATION:
                    return lgb.LGBMClassifier(
                        n_estimators=params.get('n_estimators', 100),
                        learning_rate=params.get('learning_rate', 0.1),
                        max_depth=params.get('max_depth', 6),
                        random_state=params.get('random_state', 42)
                    )
                else:
                    return lgb.LGBMRegressor(
                        n_estimators=params.get('n_estimators', 100),
                        learning_rate=params.get('learning_rate', 0.1),
                        max_depth=params.get('max_depth', 6),
                        random_state=params.get('random_state', 42)
                    )
            
            else:
                raise ValueError(f"Unsupported model type: {config.model_type}")
        
        except Exception as e:
            self.logger.error(f"Error creating model: {e}")
            raise
    
    def create_ensemble(self, models_config: List[ModelConfig], ensemble_type: str = "voting") -> Any:
        """Cria modelo ensemble"""
        self.logger.info(f"Creating {ensemble_type} ensemble with {len(models_config)} models")
        
        try:
            # Criar modelos base
            base_models = []
            for i, config in enumerate(models_config):
                model = self.create_model(config)
                model_name = f"model_{i}_{config.model_type.value}"
                base_models.append((model_name, model))
            
            # Criar ensemble
            if ensemble_type == "voting":
                return self.ensemble_builder.build_voting_ensemble(base_models)
            elif ensemble_type == "stacking":
                # Meta-model simples
                meta_config = ModelConfig(
                    model_type=ModelType.LOGISTIC_REGRESSION,
                    task_type=models_config[0].task_type
                )
                meta_model = self.create_model(meta_config)
                return self.ensemble_builder.build_stacking_ensemble(base_models, meta_model)
            else:
                raise ValueError(f"Unsupported ensemble type: {ensemble_type}")
        
        except Exception as e:
            self.logger.error(f"Error creating ensemble: {e}")
            raise
    
    def get_model_info(self, model_name: str) -> Optional[ModelInfo]:
        """Retorna informações do modelo"""
        return self.models.get(model_name)
    
    def list_models(self) -> List[str]:
        """Lista todos os modelos criados"""
        return list(self.models.keys())
    
    def get_model_architecture(self, model: Any) -> Dict[str, Any]:
        """Retorna arquitetura do modelo"""
        if PYTORCH_AVAILABLE and isinstance(model, nn.Module):
            return {
                'type': 'pytorch_neural_network',
                'parameters': sum(p.numel() for p in model.parameters()),
                'trainable_parameters': sum(p.numel() for p in model.parameters() if p.requires_grad),
                'layers': len(list(model.modules())),
                'architecture': str(model)
            }
        elif SKLEARN_AVAILABLE and hasattr(model, 'get_params'):
            return {
                'type': 'sklearn_model',
                'parameters': model.get_params(),
                'model_class': model.__class__.__name__
            }
        else:
            return {
                'type': 'unknown',
                'model_class': model.__class__.__name__
            }
    
    def create_standard_config(self, model_type: ModelType, task_type: TaskType, input_shape: Optional[Tuple[int, ...]] = None) -> ModelConfig:
        """Cria configuração padrão para tipo de modelo"""
        configs = {
            ModelType.NEURAL_NETWORK: ModelConfig(
                model_type=ModelType.NEURAL_NETWORK,
                task_type=task_type,
                architecture_type=ArchitectureType.MLP,
                input_shape=input_shape,
                hyperparameters={
                    'hidden_dims': [128, 64, 32],
                    'dropout_rate': 0.2
                },
                optimizer=OptimizerType.ADAM,
                loss_function='cross_entropy' if task_type == TaskType.CLASSIFICATION else 'mse'
            ),
            
            ModelType.RANDOM_FOREST: ModelConfig(
                model_type=ModelType.RANDOM_FOREST,
                task_type=task_type,
                hyperparameters={
                    'n_estimators': 100,
                    'max_depth': 10,
                    'random_state': 42
                }
            ),
            
            ModelType.SVM: ModelConfig(
                model_type=ModelType.SVM,
                task_type=task_type,
                hyperparameters={
                    'C': 1.0,
                    'kernel': 'rbf',
                    'gamma': 'scale'
                }
            ),
            
            ModelType.LOGISTIC_REGRESSION: ModelConfig(
                model_type=ModelType.LOGISTIC_REGRESSION,
                task_type=TaskType.CLASSIFICATION,
                hyperparameters={
                    'C': 1.0,
                    'max_iter': 1000
                }
            ),
            
            ModelType.LINEAR_REGRESSION: ModelConfig(
                model_type=ModelType.LINEAR_REGRESSION,
                task_type=TaskType.REGRESSION,
                hyperparameters={}
            )
        }
        
        return configs.get(model_type, ModelConfig(
            model_type=model_type,
            task_type=task_type,
            hyperparameters={}
        ))
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """Retorna modelos disponíveis por tarefa"""
        return {
            'classification': [
                ModelType.NEURAL_NETWORK.value,
                ModelType.RANDOM_FOREST.value,
                ModelType.GRADIENT_BOOSTING.value,
                ModelType.SVM.value,
                ModelType.DECISION_TREE.value,
                ModelType.LOGISTIC_REGRESSION.value,
                ModelType.KNN.value,
                ModelType.NAIVE_BAYES.value,
                ModelType.XGBOOST.value,
                ModelType.LIGHTGBM.value
            ],
            'regression': [
                ModelType.NEURAL_NETWORK.value,
                ModelType.RANDOM_FOREST.value,
                ModelType.GRADIENT_BOOSTING.value,
                ModelType.SVM.value,
                ModelType.DECISION_TREE.value,
                ModelType.LINEAR_REGRESSION.value,
                ModelType.KNN.value,
                ModelType.XGBOOST.value,
                ModelType.LIGHTGBM.value
            ]
        }
    
    def get_architect_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do arquiteto"""
        stats = {
            'total_models': len(self.models),
            'model_types': {},
            'task_types': {},
            'available_models': self.get_available_models(),
            'supported_architectures': [arch.value for arch in ArchitectureType],
            'available_optimizers': [opt.value for opt in OptimizerType]
        }
        
        # Contar modelos por tipo
        for model_info in self.models.values():
            model_type = model_info.model_type.value
            task_type = model_info.task_type.value
            
            stats['model_types'][model_type] = stats['model_types'].get(model_type, 0) + 1
            stats['task_types'][task_type] = stats['task_types'].get(task_type, 0) + 1
        
        return stats


# Função de conveniência
_model_architect_instance = None

def get_model_architect() -> ModelArchitect:
    """Obtém instância singleton do arquiteto de modelos"""
    global _model_architect_instance
    if _model_architect_instance is None:
        _model_architect_instance = ModelArchitect()
    return _model_architect_instance

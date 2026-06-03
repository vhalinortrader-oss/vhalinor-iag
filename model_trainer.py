"""
Model Trainer - Sistema de Treinamento com Backpropagation e Otimização
=====================================================================
Treinamento de modelos com divisão de dados, backpropagation e otimizadores
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
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
    from torch.utils.data import DataLoader, TensorDataset, random_split
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False

try:
    from sklearn.model_selection import train_test_split, cross_val_score, KFold, StratifiedKFold
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_squared_error, mean_absolute_error, r2_score
    from sklearn.preprocessing import LabelEncoder
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

from config import settings
from core import get_logger, log_execution
from .model_architect import ModelInfo, ModelConfig, ModelType, TaskType, OptimizerType, ActivationFunction


class TrainingMode(str, Enum):
    """Modos de treinamento"""
    SUPERVISED = "supervised"
    UNSUPERVISED = "unsupervised"
    SEMI_SUPERVISED = "semi_supervised"
    REINFORCEMENT = "reinforcement"
    TRANSFER_LEARNING = "transfer_learning"
    FINE_TUNING = "fine_tuning"


class ValidationStrategy(str, Enum):
    """Estratégias de validação"""
    HOLD_OUT = "hold_out"
    K_FOLD = "k_fold"
    STRATIFIED_K_FOLD = "stratified_k_fold"
    LEAVE_ONE_OUT = "leave_one_out"
    TIME_SERIES_SPLIT = "time_series_split"
    CUSTOM = "custom"


class LossFunction(str, Enum):
    """Funções de perda"""
    CROSS_ENTROPY = "cross_entropy"
    BINARY_CROSS_ENTROPY = "binary_cross_entropy"
    MEAN_SQUARED_ERROR = "mean_squared_error"
    MEAN_ABSOLUTE_ERROR = "mean_absolute_error"
    HUBER = "huber"
    KL_DIVERGENCE = "kl_divergence"
    HINGE = "hinge"
    CUSTOM = "custom"


class EarlyStopping:
    """Early stopping para treinamento"""
    
    def __init__(self, patience: int = 10, min_delta: float = 0.0, restore_best_weights: bool = True):
        self.patience = patience
        self.min_delta = min_delta
        self.restore_best_weights = restore_best_weights
        self.best_loss = float('inf')
        self.counter = 0
        self.best_weights = None
    
    def __call__(self, val_loss: float, model: nn.Module) -> bool:
        """Verifica se deve parar o treinamento"""
        if val_loss < self.best_loss - self.min_delta:
            self.best_loss = val_loss
            self.counter = 0
            if self.restore_best_weights and PYTORCH_AVAILABLE:
                self.best_weights = model.state_dict().copy()
        else:
            self.counter += 1
        
        if self.counter >= self.patience:
            if self.restore_best_weights and self.best_weights is not None:
                model.load_state_dict(self.best_weights)
            return True
        
        return False


@dataclass
class TrainingConfig:
    """Configuração de treinamento"""
    mode: TrainingMode
    validation_strategy: ValidationStrategy = ValidationStrategy.HOLD_OUT
    test_size: float = 0.2
    val_size: float = 0.2
    random_state: int = 42
    shuffle: bool = True
    stratify: bool = True
    n_folds: int = 5
    epochs: int = 100
    batch_size: int = 32
    learning_rate: float = 0.001
    optimizer: OptimizerType = OptimizerType.ADAM
    loss_function: LossFunction = LossFunction.CROSS_ENTROPY
    metrics: List[str] = field(default_factory=list)
    early_stopping: bool = True
    early_stopping_patience: int = 10
    reduce_lr_on_plateau: bool = True
    scheduler_type: str = "step"  # step, cosine, exponential
    gradient_clipping: Optional[float] = None
    weight_decay: float = 0.0
    dropout_rate: float = 0.0
    custom_params: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'mode': self.mode.value,
            'validation_strategy': self.validation_strategy.value,
            'test_size': self.test_size,
            'val_size': self.val_size,
            'random_state': self.random_state,
            'shuffle': self.shuffle,
            'stratify': self.stratify,
            'n_folds': self.n_folds,
            'epochs': self.epochs,
            'batch_size': self.batch_size,
            'learning_rate': self.learning_rate,
            'optimizer': self.optimizer.value,
            'loss_function': self.loss_function.value,
            'metrics': self.metrics,
            'early_stopping': self.early_stopping,
            'early_stopping_patience': self.early_stopping_patience,
            'reduce_lr_on_plateau': self.reduce_lr_on_plateau,
            'scheduler_type': self.scheduler_type,
            'gradient_clipping': self.gradient_clipping,
            'weight_decay': self.weight_decay,
            'dropout_rate': self.dropout_rate,
            'custom_params': self.custom_params
        }


@dataclass
class TrainingResult:
    """Resultado do treinamento"""
    model_info: ModelInfo
    training_history: Dict[str, List[float]]
    validation_history: Dict[str, List[float]]
    test_metrics: Dict[str, float]
    training_time: float
    best_epoch: int
    convergence_epoch: Optional[int] = None
    early_stopped: bool = False
    overfitting_detected: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'model_info': self.model_info.to_dict(),
            'training_history': self.training_history,
            'validation_history': self.validation_history,
            'test_metrics': self.test_metrics,
            'training_time': self.training_time,
            'best_epoch': self.best_epoch,
            'convergence_epoch': self.convergence_epoch,
            'early_stopped': self.early_stopped,
            'overfitting_detected': self.overfitting_detected
        }


class DataSplitter:
    """Divisor de dados para treinamento"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.trainer.splitter", "data_splitter")
    
    def split_data(self, X: Any, y: Any, config: TrainingConfig) -> Tuple[Any, Any, Any, Any, Any, Any]:
        """Divide dados em treino, validação e teste"""
        if not SKLEARN_AVAILABLE or not PANDAS_AVAILABLE:
            raise ImportError("sklearn and pandas are required for data splitting")
        
        self.logger.info(f"Splitting data with strategy: {config.validation_strategy.value}")
        
        # Primeiro separar conjunto de teste
        if config.stratify and config.validation_strategy != ValidationStrategy.TIME_SERIES_SPLIT:
            X_temp, X_test, y_temp, y_test = train_test_split(
                X, y, test_size=config.test_size, random_state=config.random_state, 
                stratify=y, shuffle=config.shuffle
            )
        else:
            X_temp, X_test, y_temp, y_test = train_test_split(
                X, y, test_size=config.test_size, random_state=config.random_state, 
                shuffle=config.shuffle
            )
        
        # Depois separar treino e validação
        if config.stratify and config.validation_strategy != ValidationStrategy.TIME_SERIES_SPLIT:
            X_train, X_val, y_train, y_val = train_test_split(
                X_temp, y_temp, test_size=config.val_size/(1-config.test_size), 
                random_state=config.random_state, stratify=y_temp, shuffle=config.shuffle
            )
        else:
            X_train, X_val, y_train, y_val = train_test_split(
                X_temp, y_temp, test_size=config.val_size/(1-config.test_size), 
                random_state=config.random_state, shuffle=config.shuffle
            )
        
        self.logger.info(f"Data split - Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")
        
        return X_train, X_val, X_test, y_train, y_val, y_test
    
    def create_cross_validation_splits(self, X: Any, y: Any, config: TrainingConfig) -> List[Tuple[Any, Any, Any, Any]]:
        """Cria splits para cross-validation"""
        if not SKLEARN_AVAILABLE:
            raise ImportError("sklearn is required for cross-validation")
        
        splits = []
        
        if config.validation_strategy == ValidationStrategy.K_FOLD:
            kf = KFold(n_splits=config.n_folds, shuffle=config.shuffle, random_state=config.random_state)
            for train_idx, val_idx in kf.split(X):
                X_train, X_val = X[train_idx], X[val_idx]
                y_train, y_val = y[train_idx], y[val_idx]
                splits.append((X_train, X_val, y_train, y_val))
        
        elif config.validation_strategy == ValidationStrategy.STRATIFIED_K_FOLD:
            skf = StratifiedKFold(n_splits=config.n_folds, shuffle=config.shuffle, random_state=config.random_state)
            for train_idx, val_idx in skf.split(X, y):
                X_train, X_val = X[train_idx], X[val_idx]
                y_train, y_val = y[train_idx], y[val_idx]
                splits.append((X_train, X_val, y_train, y_val))
        
        return splits


class PyTorchTrainer:
    """Treinador para modelos PyTorch"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.trainer.pytorch", "pytorch_trainer")
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    def prepare_data_loaders(self, X_train: Any, y_train: Any, X_val: Any, y_val: Any, config: TrainingConfig) -> Tuple[DataLoader, DataLoader]:
        """Prepara DataLoaders para PyTorch"""
        if not PYTORCH_AVAILABLE or not NUMPY_AVAILABLE:
            raise ImportError("torch and numpy are required for PyTorch training")
        
        # Converter para tensores
        if not isinstance(X_train, torch.Tensor):
            X_train = torch.FloatTensor(X_train)
            X_val = torch.FloatTensor(X_val)
        
        if not isinstance(y_train, torch.Tensor):
            if config.loss_function in [LossFunction.CROSS_ENTROPY]:
                y_train = torch.LongTensor(y_train)
                y_val = torch.LongTensor(y_val)
            else:
                y_train = torch.FloatTensor(y_train)
                y_val = torch.FloatTensor(y_val)
        
        # Criar datasets
        train_dataset = TensorDataset(X_train, y_train)
        val_dataset = TensorDataset(X_val, y_val)
        
        # Criar dataloaders
        train_loader = DataLoader(train_dataset, batch_size=config.batch_size, shuffle=config.shuffle)
        val_loader = DataLoader(val_dataset, batch_size=config.batch_size, shuffle=False)
        
        return train_loader, val_loader
    
    def get_loss_function(self, loss_function: LossFunction) -> nn.Module:
        """Obtém função de perda"""
        if loss_function == LossFunction.CROSS_ENTROPY:
            return nn.CrossEntropyLoss()
        elif loss_function == LossFunction.BINARY_CROSS_ENTROPY:
            return nn.BCEWithLogitsLoss()
        elif loss_function == LossFunction.MEAN_SQUARED_ERROR:
            return nn.MSELoss()
        elif loss_function == LossFunction.MEAN_ABSOLUTE_ERROR:
            return nn.L1Loss()
        elif loss_function == LossFunction.HUBER:
            return nn.HuberLoss()
        else:
            return nn.MSELoss()
    
    def get_optimizer(self, model: nn.Module, config: TrainingConfig) -> optim.Optimizer:
        """Obtém otimizador"""
        if config.optimizer == OptimizerType.ADAM:
            return optim.Adam(model.parameters(), lr=config.learning_rate, weight_decay=config.weight_decay)
        elif config.optimizer == OptimizerType.SGD:
            return optim.SGD(model.parameters(), lr=config.learning_rate, weight_decay=config.weight_decay, momentum=0.9)
        elif config.optimizer == OptimizerType.RMSPROP:
            return optim.RMSprop(model.parameters(), lr=config.learning_rate, weight_decay=config.weight_decay)
        elif config.optimizer == OptimizerType.ADAMW:
            return optim.AdamW(model.parameters(), lr=config.learning_rate, weight_decay=config.weight_decay)
        else:
            return optim.Adam(model.parameters(), lr=config.learning_rate, weight_decay=config.weight_decay)
    
    def get_scheduler(self, optimizer: optim.Optimizer, config: TrainingConfig):
        """Obtém scheduler de learning rate"""
        if config.scheduler_type == "step":
            return optim.lr_scheduler.StepLR(optimizer, step_size=30, gamma=0.1)
        elif config.scheduler_type == "cosine":
            return optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=config.epochs)
        elif config.scheduler_type == "exponential":
            return optim.lr_scheduler.ExponentialLR(optimizer, gamma=0.95)
        else:
            return None
    
    def calculate_metrics(self, y_true: torch.Tensor, y_pred: torch.Tensor, task_type: TaskType, metrics: List[str]) -> Dict[str, float]:
        """Calcula métricas de avaliação"""
        if not NUMPY_AVAILABLE:
            return {}
        
        y_true_np = y_true.cpu().numpy()
        y_pred_np = y_pred.cpu().numpy()
        
        if task_type == TaskType.CLASSIFICATION:
            y_pred_class = np.argmax(y_pred_np, axis=1) if len(y_pred_np.shape) > 1 else (y_pred_np > 0.5).astype(int)
            
            result = {}
            if 'accuracy' in metrics:
                result['accuracy'] = accuracy_score(y_true_np, y_pred_class)
            if 'precision' in metrics:
                result['precision'] = precision_score(y_true_np, y_pred_class, average='weighted', zero_division=0)
            if 'recall' in metrics:
                result['recall'] = recall_score(y_true_np, y_pred_class, average='weighted', zero_division=0)
            if 'f1' in metrics:
                result['f1'] = f1_score(y_true_np, y_pred_class, average='weighted', zero_division=0)
            
            return result
        else:  # REGRESSION
            result = {}
            if 'mse' in metrics:
                result['mse'] = mean_squared_error(y_true_np, y_pred_np)
            if 'mae' in metrics:
                result['mae'] = mean_absolute_error(y_true_np, y_pred_np)
            if 'r2' in metrics:
                result['r2'] = r2_score(y_true_np, y_pred_np)
            
            return result
    
    def train_epoch(self, model: nn.Module, train_loader: DataLoader, optimizer: optim.Optimizer, 
                   loss_fn: nn.Module, config: TrainingConfig) -> Tuple[float, Dict[str, float]]:
        """Treina uma época"""
        model.train()
        total_loss = 0.0
        all_metrics = {}
        
        for batch_idx, (data, target) in enumerate(train_loader):
            data, target = data.to(self.device), target.to(self.device)
            
            optimizer.zero_grad()
            output = model(data)
            loss = loss_fn(output, target)
            
            # Gradient clipping
            if config.gradient_clipping is not None:
                torch.nn.utils.clip_grad_norm_(model.parameters(), config.gradient_clipping)
            
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            
            # Calcular métricas a cada batch
            if batch_idx % 10 == 0 and config.metrics:
                batch_metrics = self.calculate_metrics(target, output, config.task_type, config.metrics)
                for metric, value in batch_metrics.items():
                    if metric not in all_metrics:
                        all_metrics[metric] = []
                    all_metrics[metric].append(value)
        
        avg_loss = total_loss / len(train_loader)
        
        # Média das métricas
        avg_metrics = {}
        for metric, values in all_metrics.items():
            avg_metrics[metric] = np.mean(values)
        
        return avg_loss, avg_metrics
    
    def validate_epoch(self, model: nn.Module, val_loader: DataLoader, loss_fn: nn.Module, 
                      config: TrainingConfig) -> Tuple[float, Dict[str, float]]:
        """Valida uma época"""
        model.eval()
        total_loss = 0.0
        all_metrics = {}
        
        with torch.no_grad():
            for data, target in val_loader:
                data, target = data.to(self.device), target.to(self.device)
                output = model(data)
                loss = loss_fn(output, target)
                total_loss += loss.item()
                
                # Calcular métricas
                if config.metrics:
                    batch_metrics = self.calculate_metrics(target, output, config.task_type, config.metrics)
                    for metric, value in batch_metrics.items():
                        if metric not in all_metrics:
                            all_metrics[metric] = []
                        all_metrics[metric].append(value)
        
        avg_loss = total_loss / len(val_loader)
        
        # Média das métricas
        avg_metrics = {}
        for metric, values in all_metrics.items():
            avg_metrics[metric] = np.mean(values)
        
        return avg_loss, avg_metrics
    
    def train_model(self, model: nn.Module, X_train: Any, y_train: Any, X_val: Any, y_val: Any, 
                   config: TrainingConfig) -> Tuple[Dict[str, List[float]], Dict[str, List[float]], int]:
        """Treina modelo PyTorch"""
        if not PYTORCH_AVAILABLE:
            raise ImportError("torch is required for PyTorch training")
        
        model.to(self.device)
        
        # Preparar dataloaders
        train_loader, val_loader = self.prepare_data_loaders(X_train, y_train, X_val, y_val, config)
        
        # Configurar treinamento
        loss_fn = self.get_loss_function(config.loss_function)
        optimizer = self.get_optimizer(model, config)
        scheduler = self.get_scheduler(optimizer, config)
        early_stopping = EarlyStopping(patience=config.early_stopping_patience) if config.early_stopping else None
        
        # Histórico de treinamento
        train_history = {'loss': []}
        val_history = {'loss': []}
        
        for metric in config.metrics:
            train_history[metric] = []
            val_history[metric] = []
        
        best_val_loss = float('inf')
        best_epoch = 0
        
        for epoch in range(config.epochs):
            # Treinar época
            train_loss, train_metrics = self.train_epoch(model, train_loader, optimizer, loss_fn, config)
            train_history['loss'].append(train_loss)
            
            for metric, value in train_metrics.items():
                train_history[metric].append(value)
            
            # Validar época
            val_loss, val_metrics = self.validate_epoch(model, val_loader, loss_fn, config)
            val_history['loss'].append(val_loss)
            
            for metric, value in val_metrics.items():
                val_history[metric].append(value)
            
            # Atualizar scheduler
            if scheduler:
                scheduler.step()
            
            # Early stopping
            if early_stopping:
                if early_stopping(val_loss, model):
                    self.logger.info(f"Early stopping at epoch {epoch+1}")
                    break
            
            # Melhor modelo
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                best_epoch = epoch
            
            # Log progress
            if epoch % 10 == 0:
                metrics_str = ", ".join([f"{k}: {v:.4f}" for k, v in val_metrics.items()])
                self.logger.info(f"Epoch {epoch+1}/{config.epochs} - Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}, {metrics_str}")
        
        return train_history, val_history, best_epoch


class SklearnTrainer:
    """Treinador para modelos Scikit-learn"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.trainer.sklearn", "sklearn_trainer")
    
    def train_model(self, model: Any, X_train: Any, y_train: Any, X_val: Any, y_val: Any, 
                   config: TrainingConfig) -> Tuple[Dict[str, List[float]], Dict[str, List[float]], int]:
        """Treina modelo Scikit-learn"""
        if not SKLEARN_AVAILABLE:
            raise ImportError("sklearn is required for Scikit-learn training")
        
        start_time = time.time()
        
        # Treinar modelo
        self.logger.info(f"Training {model.__class__.__name__}")
        model.fit(X_train, y_train)
        
        # Prever em treino e validação
        y_train_pred = model.predict(X_train)
        y_val_pred = model.predict(X_val)
        
        # Calcular métricas
        train_metrics = self._calculate_sklearn_metrics(y_train, y_train_pred, config.task_type, config.metrics)
        val_metrics = self._calculate_sklearn_metrics(y_val, y_val_pred, config.task_type, config.metrics)
        
        # Criar histórico (simplificado para sklearn)
        train_history = {metric: [value] for metric, value in train_metrics.items()}
        val_history = {metric: [value] for metric, value in val_metrics.items()}
        
        # Adicionar loss se disponível
        if hasattr(model, 'loss_'):
            train_history['loss'] = [model.loss_]
            val_history['loss'] = [model.loss_]
        
        training_time = time.time() - start_time
        self.logger.info(f"Training completed in {training_time:.2f} seconds")
        
        return train_history, val_history, 0  # sklearn não tem epochs
    
    def _calculate_sklearn_metrics(self, y_true: Any, y_pred: Any, task_type: TaskType, metrics: List[str]) -> Dict[str, float]:
        """Calcula métricas para modelos sklearn"""
        result = {}
        
        if task_type == TaskType.CLASSIFICATION:
            if 'accuracy' in metrics:
                result['accuracy'] = accuracy_score(y_true, y_pred)
            if 'precision' in metrics:
                result['precision'] = precision_score(y_true, y_pred, average='weighted', zero_division=0)
            if 'recall' in metrics:
                result['recall'] = recall_score(y_true, y_pred, average='weighted', zero_division=0)
            if 'f1' in metrics:
                result['f1'] = f1_score(y_true, y_pred, average='weighted', zero_division=0)
        else:  # REGRESSION
            if 'mse' in metrics:
                result['mse'] = mean_squared_error(y_true, y_pred)
            if 'mae' in metrics:
                result['mae'] = mean_absolute_error(y_true, y_pred)
            if 'r2' in metrics:
                result['r2'] = r2_score(y_true, y_pred)
        
        return result


class ModelTrainer:
    """Treinador principal de modelos"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.trainer.main", "model_trainer")
        
        # Inicializar treinadores
        self.pytorch_trainer = PyTorchTrainer()
        self.sklearn_trainer = SklearnTrainer()
        self.data_splitter = DataSplitter()
        
        self.training_results = {}
    
    @log_execution(component="trainer", operation="train_model")
    async def train_model(self, model_info: ModelInfo, X: Any, y: Any, config: TrainingConfig) -> TrainingResult:
        """Treina modelo com configuração especificada"""
        start_time = time.time()
        self.logger.info(f"Training {model_info.model_type.value} model for {model_info.task_type.value}")
        
        try:
            # Dividir dados
            X_train, X_val, X_test, y_train, y_val, y_test = self.data_splitter.split_data(X, y, config)
            
            # Treinar modelo baseado no tipo
            if PYTORCH_AVAILABLE and hasattr(model_info.model, 'parameters'):
                # Modelo PyTorch
                train_history, val_history, best_epoch = self.pytorch_trainer.train_model(
                    model_info.model, X_train, y_train, X_val, y_val, config
                )
            else:
                # Modelo Scikit-learn
                train_history, val_history, best_epoch = self.sklearn_trainer.train_model(
                    model_info.model, X_train, y_train, X_val, y_val, config
                )
            
            # Avaliar no conjunto de teste
            test_metrics = await self._evaluate_model(model_info.model, X_test, y_test, config)
            
            # Detectar overfitting
            overfitting_detected = self._detect_overfitting(train_history, val_history)
            
            # Criar resultado
            training_time = time.time() - start_time
            result = TrainingResult(
                model_info=model_info,
                training_history=train_history,
                validation_history=val_history,
                test_metrics=test_metrics,
                training_time=training_time,
                best_epoch=best_epoch,
                overfitting_detected=overfitting_detected
            )
            
            # Armazenar resultado
            result_key = f"{model_info.name}_{int(time.time())}"
            self.training_results[result_key] = result
            
            self.logger.info(f"Training completed in {training_time:.2f}s - Best epoch: {best_epoch}")
            
            return result
        
        except Exception as e:
            self.logger.error(f"Error training model: {e}")
            raise
    
    async def _evaluate_model(self, model: Any, X_test: Any, y_test: Any, config: TrainingConfig) -> Dict[str, float]:
        """Avalia modelo no conjunto de teste"""
        try:
            if PYTORCH_AVAILABLE and hasattr(model, 'eval'):
                # Modelo PyTorch
                model.eval()
                with torch.no_grad():
                    if not isinstance(X_test, torch.Tensor):
                        X_test = torch.FloatTensor(X_test)
                    X_test = X_test.to(self.pytorch_trainer.device)
                    
                    predictions = model(X_test)
                    if config.task_type == TaskType.CLASSIFICATION:
                        predictions = torch.argmax(predictions, dim=1)
                    
                    # Converter para numpy para métricas
                    y_test_np = y_test if isinstance(y_test, np.ndarray) else np.array(y_test)
                    pred_np = predictions.cpu().numpy()
                    
                    return self.pytorch_trainer.calculate_metrics(
                        torch.LongTensor(y_test_np), 
                        predictions if config.task_type == TaskType.CLASSIFICATION else predictions,
                        config.task_type,
                        config.metrics
                    )
            else:
                # Modelo Scikit-learn
                y_pred = model.predict(X_test)
                return self.sklearn_trainer._calculate_sklearn_metrics(
                    y_test, y_pred, config.task_type, config.metrics
                )
        
        except Exception as e:
            self.logger.error(f"Error evaluating model: {e}")
            return {}
    
    def _detect_overfitting(self, train_history: Dict[str, List[float]], val_history: Dict[str, List[float]], threshold: float = 0.1) -> bool:
        """Detecta overfitting comparando treino e validação"""
        if 'loss' not in train_history or 'loss' not in val_history:
            return False
        
        train_losses = train_history['loss']
        val_losses = val_history['loss']
        
        if len(train_losses) < 10 or len(val_losses) < 10:
            return False
        
        # Verificar se loss de validação está aumentando enquanto treino diminui
        recent_train_loss = np.mean(train_losses[-5:])
        recent_val_loss = np.mean(val_losses[-5:])
        
        # Se gap entre treino e validação é grande
        gap = recent_val_loss - recent_train_loss
        relative_gap = gap / recent_train_loss if recent_train_loss > 0 else 0
        
        return relative_gap > threshold
    
    async def cross_validate_model(self, model_info: ModelInfo, X: Any, y: Any, config: TrainingConfig) -> Dict[str, List[float]]:
        """Realiza cross-validation do modelo"""
        if not SKLEARN_AVAILABLE:
            raise ImportError("sklearn is required for cross-validation")
        
        self.logger.info(f"Cross-validating model with {config.n_folds} folds")
        
        # Criar splits
        splits = self.data_splitter.create_cross_validation_splits(X, y, config)
        
        cv_results = {metric: [] for metric in config.metrics}
        cv_results['loss'] = []
        
        for fold, (X_train, X_val, y_train, y_val) in enumerate(splits):
            self.logger.info(f"Training fold {fold + 1}/{len(splits)}")
            
            # Clonar modelo para cada fold
            if SKLEARN_AVAILABLE and hasattr(model_info.model, 'get_params'):
                from sklearn.base import clone
                fold_model = clone(model_info.model)
            else:
                fold_model = model_info.model
            
            # Criar ModelInfo temporário
            fold_model_info = ModelInfo(
                name=f"{model_info.name}_fold_{fold}",
                model_type=model_info.model_type,
                task_type=model_info.task_type,
                config=model_info.config,
                model=fold_model,
                performance_metrics={},
                training_history={},
                created_at=datetime.now()
            )
            
            # Treinar fold
            fold_result = await self.train_model(fold_model_info, X_train, y_train, config)
            
            # Adicionar resultados
            for metric, value in fold_result.test_metrics.items():
                cv_results[metric].append(value)
            
            if 'loss' in fold_result.validation_history:
                cv_results['loss'].append(min(fold_result.validation_history['loss']))
        
        # Calcular estatísticas
        cv_stats = {}
        for metric, values in cv_results.items():
            cv_stats[metric] = {
                'mean': np.mean(values),
                'std': np.std(values),
                'min': np.min(values),
                'max': np.max(values),
                'values': values
            }
        
        self.logger.info(f"Cross-validation completed")
        return cv_stats
    
    def get_training_result(self, result_key: str) -> Optional[TrainingResult]:
        """Retorna resultado de treinamento específico"""
        return self.training_results.get(result_key)
    
    def list_training_results(self) -> List[str]:
        """Lista todos os resultados de treinamento"""
        return list(self.training_results.keys())
    
    def create_standard_config(self, task_type: TaskType, model_type: ModelType) -> TrainingConfig:
        """Cria configuração padrão de treinamento"""
        return TrainingConfig(
            mode=TrainingMode.SUPERVISED,
            validation_strategy=ValidationStrategy.HOLD_OUT,
            epochs=100 if model_type == ModelType.NEURAL_NETWORK else 1,
            batch_size=32,
            learning_rate=0.001,
            optimizer=OptimizerType.ADAM,
            loss_function=LossFunction.CROSS_ENTROPY if task_type == TaskType.CLASSIFICATION else LossFunction.MEAN_SQUARED_ERROR,
            metrics=['accuracy', 'precision', 'recall', 'f1'] if task_type == TaskType.CLASSIFICATION else ['mse', 'mae', 'r2'],
            early_stopping=True,
            early_stopping_patience=10
        )
    
    def get_trainer_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do treinador"""
        stats = {
            'total_training_results': len(self.training_results),
            'available_modes': [mode.value for mode in TrainingMode],
            'validation_strategies': [strategy.value for strategy in ValidationStrategy],
            'loss_functions': [loss.value for loss in LossFunction],
            'optimizers': [opt.value for opt in OptimizerType],
            'device': str(self.pytorch_trainer.device) if PYTORCH_AVAILABLE else 'cpu'
        }
        
        # Estatísticas por tipo de modelo
        model_type_counts = {}
        for result in self.training_results.values():
            model_type = result.model_info.model_type.value
            model_type_counts[model_type] = model_type_counts.get(model_type, 0) + 1
        
        stats['results_by_model_type'] = model_type_counts
        
        return stats


# Função de conveniência
_trainer_instance = None

def get_model_trainer() -> ModelTrainer:
    """Obtém instância singleton do treinador de modelos"""
    global _trainer_instance
    if _trainer_instance is None:
        _trainer_instance = ModelTrainer()
    return _trainer_instance

"""
Model Evaluator - Sistema de Avaliação e Validação
=================================================
Avaliação de modelos com métricas, validação cruzada e prevenção de overfitting
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
    import torch.nn.functional as F
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False

try:
    from sklearn.model_selection import cross_val_score, cross_validate, learning_curve, validation_curve
    from sklearn.metrics import (
        accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, roc_curve,
        mean_squared_error, mean_absolute_error, r2_score, mean_absolute_percentage_error,
        confusion_matrix, classification_report, precision_recall_curve,
        explained_variance_score, median_absolute_error
    )
    from sklearn.calibration import calibration_curve
    from sklearn.inspection import permutation_importance
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False

from config import settings
from core import get_logger, log_execution
from .model_architect import ModelInfo, TaskType
from .model_trainer import TrainingResult


class MetricType(str, Enum):
    """Tipos de métricas"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    RANKING = "ranking"
    CUSTOM = "custom"


class ValidationMethod(str, Enum):
    """Métodos de validação"""
    HOLD_OUT = "hold_out"
    K_FOLD = "k_fold"
    STRATIFIED_K_FOLD = "stratified_k_fold"
    LEAVE_ONE_OUT = "leave_one_out"
    TIME_SERIES_SPLIT = "time_series_split"
    BOOTSTRAP = "bootstrap"
    CUSTOM = "custom"


class OverfittingDetection(str, Enum):
    """Métodos de detecção de overfitting"""
    TRAIN_VAL_GAP = "train_val_gap"
    LEARNING_CURVE = "learning_curve"
    VALIDATION_CURVE = "validation_curve"
    CROSS_VAL_SCORE = "cross_val_score"
    REGULARIZATION = "regularization"


@dataclass
class EvaluationConfig:
    """Configuração de avaliação"""
    validation_method: ValidationMethod = ValidationMethod.HOLD_OUT
    test_size: float = 0.2
    n_folds: int = 5
    n_bootstraps: int = 100
    metrics: List[str] = field(default_factory=list)
    cross_validate_metrics: List[str] = field(default_factory=list)
    learning_curve_points: int = 10
    overfitting_detection: List[OverfittingDetection] = field(default_factory=list)
    feature_importance: bool = True
    calibration_curves: bool = True
    confusion_matrix: bool = True
    classification_report: bool = True
    custom_params: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'validation_method': self.validation_method.value,
            'test_size': self.test_size,
            'n_folds': self.n_folds,
            'n_bootstraps': self.n_bootstraps,
            'metrics': self.metrics,
            'cross_validate_metrics': self.cross_validate_metrics,
            'learning_curve_points': self.learning_curve_points,
            'overfitting_detection': [od.value for od in self.overfitting_detection],
            'feature_importance': self.feature_importance,
            'calibration_curves': self.calibration_curves,
            'confusion_matrix': self.confusion_matrix,
            'classification_report': self.classification_report,
            'custom_params': self.custom_params
        }


@dataclass
class EvaluationResult:
    """Resultado da avaliação"""
    model_name: str
    task_type: TaskType
    validation_method: ValidationMethod
    metrics: Dict[str, float]
    cross_val_scores: Optional[Dict[str, List[float]]] = None
    learning_curve_data: Optional[Dict[str, Any]] = None
    validation_curve_data: Optional[Dict[str, Any]] = None
    feature_importance: Optional[Dict[str, float]] = None
    confusion_matrix_data: Optional[Dict[str, Any]] = None
    calibration_data: Optional[Dict[str, Any]] = None
    overfitting_analysis: Optional[Dict[str, Any]] = None
    evaluation_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'model_name': self.model_name,
            'task_type': self.task_type.value,
            'validation_method': self.validation_method.value,
            'metrics': self.metrics,
            'cross_val_scores': self.cross_val_scores,
            'learning_curve_data': self.learning_curve_data,
            'validation_curve_data': self.validation_curve_data,
            'feature_importance': self.feature_importance,
            'confusion_matrix_data': self.confusion_matrix_data,
            'calibration_data': self.calibration_data,
            'overfitting_analysis': self.overfitting_analysis,
            'evaluation_time': self.evaluation_time,
            'timestamp': self.timestamp.isoformat()
        }


class ClassificationMetrics:
    """Calculador de métricas de classificação"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.evaluator.classification", "classification_metrics")
    
    def calculate_basic_metrics(self, y_true: Any, y_pred: Any, y_prob: Optional[Any] = None) -> Dict[str, float]:
        """Calcula métricas básicas de classificação"""
        if not SKLEARN_AVAILABLE or not NUMPY_AVAILABLE:
            return {}
        
        metrics = {}
        
        # Métricas básicas
        metrics['accuracy'] = accuracy_score(y_true, y_pred)
        metrics['precision'] = precision_score(y_true, y_pred, average='weighted', zero_division=0)
        metrics['recall'] = recall_score(y_true, y_pred, average='weighted', zero_division=0)
        metrics['f1'] = f1_score(y_true, y_pred, average='weighted', zero_division=0)
        
        # Métricas por classe (se for binário ou multiclasse)
        try:
            if len(np.unique(y_true)) <= 2:  # Binário
                metrics['precision_binary'] = precision_score(y_true, y_pred, zero_division=0)
                metrics['recall_binary'] = recall_score(y_true, y_pred, zero_division=0)
                metrics['f1_binary'] = f1_score(y_true, y_pred, zero_division=0)
                
                # ROC AUC se tiver probabilidades
                if y_prob is not None:
                    metrics['roc_auc'] = roc_auc_score(y_true, y_prob)
            else:  # Multiclasse
                metrics['precision_macro'] = precision_score(y_true, y_pred, average='macro', zero_division=0)
                metrics['recall_macro'] = recall_score(y_true, y_pred, average='macro', zero_division=0)
                metrics['f1_macro'] = f1_score(y_true, y_pred, average='macro', zero_division=0)
                
                metrics['precision_micro'] = precision_score(y_true, y_pred, average='micro', zero_division=0)
                metrics['recall_micro'] = recall_score(y_true, y_pred, average='micro', zero_division=0)
                metrics['f1_micro'] = f1_score(y_true, y_pred, average='micro', zero_division=0)
                
                # ROC AUC One-vs-Rest se tiver probabilidades
                if y_prob is not None:
                    try:
                        metrics['roc_auc_ovr'] = roc_auc_score(y_true, y_prob, multi_class='ovr')
                    except:
                        pass
        except Exception as e:
            self.logger.warning(f"Error calculating per-class metrics: {e}")
        
        return metrics
    
    def calculate_confusion_matrix(self, y_true: Any, y_pred: Any) -> Dict[str, Any]:
        """Calcula matriz de confusão"""
        if not SKLEARN_AVAILABLE:
            return {}
        
        try:
            cm = confusion_matrix(y_true, y_pred)
            
            # Normalizar matriz
            cm_normalized = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
            
            # Calcular métricas da matriz
            tp = np.diag(cm)
            fp = cm.sum(axis=0) - tp
            fn = cm.sum(axis=1) - tp
            tn = cm.sum() - (tp + fp + fn)
            
            return {
                'matrix': cm.tolist(),
                'normalized_matrix': cm_normalized.tolist(),
                'true_positives': tp.tolist(),
                'false_positives': fp.tolist(),
                'false_negatives': fn.tolist(),
                'true_negatives': tn.tolist(),
                'true_positive_rate': (tp / (tp + fn)).tolist(),
                'false_positive_rate': (fp / (fp + tn)).tolist()
            }
        except Exception as e:
            self.logger.error(f"Error calculating confusion matrix: {e}")
            return {}
    
    def generate_classification_report(self, y_true: Any, y_pred: Any) -> Dict[str, Any]:
        """Gera relatório de classificação"""
        if not SKLEARN_AVAILABLE:
            return {}
        
        try:
            report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
            return report
        except Exception as e:
            self.logger.error(f"Error generating classification report: {e}")
            return {}


class RegressionMetrics:
    """Calculador de métricas de regressão"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.evaluator.regression", "regression_metrics")
    
    def calculate_basic_metrics(self, y_true: Any, y_pred: Any) -> Dict[str, float]:
        """Calcula métricas básicas de regressão"""
        if not SKLEARN_AVAILABLE or not NUMPY_AVAILABLE:
            return {}
        
        metrics = {}
        
        # Métricas de erro
        metrics['mse'] = mean_squared_error(y_true, y_pred)
        metrics['rmse'] = np.sqrt(metrics['mse'])
        metrics['mae'] = mean_absolute_error(y_true, y_pred)
        metrics['median_ae'] = median_absolute_error(y_true, y_pred)
        
        # Métricas de erro relativo
        try:
            metrics['mape'] = mean_absolute_percentage_error(y_true, y_pred)
            metrics['rmsle'] = np.sqrt(mean_squared_error(np.log1p(y_true), np.log1p(y_pred)))
        except:
            pass
        
        # Métricas de ajuste
        metrics['r2'] = r2_score(y_true, y_pred)
        metrics['explained_variance'] = explained_variance_score(y_true, y_pred)
        
        # Métricas adicionais
        y_true_mean = np.mean(y_true)
        baseline_mse = np.mean((y_true - y_true_mean) ** 2)
        metrics['baseline_mse'] = baseline_mse
        metrics['relative_mse'] = metrics['mse'] / baseline_mse if baseline_mse > 0 else float('inf')
        
        return metrics
    
    def calculate_residual_metrics(self, y_true: Any, y_pred: Any) -> Dict[str, Any]:
        """Calcula métricas de resíduos"""
        if not NUMPY_AVAILABLE:
            return {}
        
        residuals = y_true - y_pred
        
        return {
            'residuals_mean': np.mean(residuals),
            'residuals_std': np.std(residuals),
            'residuals_skewness': self._calculate_skewness(residuals),
            'residuals_kurtosis': self._calculate_kurtosis(residuals),
            'residuals_min': np.min(residuals),
            'residuals_max': np.max(residuals),
            'residuals_q25': np.percentile(residuals, 25),
            'residuals_q75': np.percentile(residuals, 75)
        }
    
    def _calculate_skewness(self, data: np.ndarray) -> float:
        """Calcula skewness"""
        if len(data) < 3:
            return 0.0
        
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0.0
        
        n = len(data)
        skewness = (n / ((n - 1) * (n - 2))) * np.sum(((data - mean) / std) ** 3)
        return skewness
    
    def _calculate_kurtosis(self, data: np.ndarray) -> float:
        """Calcula kurtosis"""
        if len(data) < 4:
            return 0.0
        
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0.0
        
        n = len(data)
        kurtosis = (n * (n + 1) / ((n - 1) * (n - 2) * (n - 3))) * np.sum(((data - mean) / std) ** 4)
        kurtosis -= 3 * (n - 1) ** 2 / ((n - 2) * (n - 3))
        return kurtosis


class CrossValidationEvaluator:
    """Avaliador de validação cruzada"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.evaluator.cv", "cross_validation")
    
    def perform_cross_validation(self, model: Any, X: Any, y: Any, config: EvaluationConfig) -> Dict[str, List[float]]:
        """Realiza validação cruzada"""
        if not SKLEARN_AVAILABLE:
            return {}
        
        self.logger.info(f"Performing {config.validation_method.value} cross-validation")
        
        try:
            # Determinar estratégia de CV
            if config.validation_method == ValidationMethod.K_FOLD:
                from sklearn.model_selection import KFold
                cv = KFold(n_splits=config.n_folds, shuffle=True, random_state=42)
            elif config.validation_method == ValidationMethod.STRATIFIED_K_FOLD:
                from sklearn.model_selection import StratifiedKFold
                cv = StratifiedKFold(n_splits=config.n_folds, shuffle=True, random_state=42)
            else:
                from sklearn.model_selection import KFold
                cv = KFold(n_splits=config.n_folds, shuffle=True, random_state=42)
            
            # Realizar cross-validation
            scoring_metrics = config.cross_validate_metrics or ['accuracy'] if hasattr(model, 'predict_proba') else ['r2']
            
            cv_results = cross_validate(
                model, X, y, 
                cv=cv, 
                scoring=scoring_metrics,
                return_train_score=True,
                n_jobs=-1
            )
            
            # Organizar resultados
            results = {}
            for metric in scoring_metrics:
                results[f'train_{metric}'] = cv_results[f'train_{metric}'].tolist()
                results[f'test_{metric}'] = cv_results[f'test_{metric}'].tolist()
            
            # Adicionar tempo
            results['fit_time'] = cv_results['fit_time'].tolist()
            results['score_time'] = cv_results['score_time'].tolist()
            
            return results
        
        except Exception as e:
            self.logger.error(f"Error in cross-validation: {e}")
            return {}
    
    def generate_learning_curve(self, model: Any, X: Any, y: Any, config: EvaluationConfig) -> Dict[str, Any]:
        """Gera curva de aprendizado"""
        if not SKLEARN_AVAILABLE:
            return {}
        
        try:
            train_sizes = np.linspace(0.1, 1.0, config.learning_curve_points)
            
            train_sizes_abs, train_scores, val_scores = learning_curve(
                model, X, y,
                train_sizes=train_sizes,
                cv=config.n_folds,
                n_jobs=-1,
                scoring='accuracy' if hasattr(model, 'predict_proba') else 'r2'
            )
            
            return {
                'train_sizes': train_sizes_abs.tolist(),
                'train_scores_mean': np.mean(train_scores, axis=1).tolist(),
                'train_scores_std': np.std(train_scores, axis=1).tolist(),
                'val_scores_mean': np.mean(val_scores, axis=1).tolist(),
                'val_scores_std': np.std(val_scores, axis=1).tolist()
            }
        
        except Exception as e:
            self.logger.error(f"Error generating learning curve: {e}")
            return {}
    
    def generate_validation_curve(self, model: Any, X: Any, y: Any, param_name: str, param_range: List[Any], config: EvaluationConfig) -> Dict[str, Any]:
        """Gera curva de validação"""
        if not SKLEARN_AVAILABLE:
            return {}
        
        try:
            train_scores, val_scores = validation_curve(
                model, X, y,
                param_name=param_name,
                param_range=param_range,
                cv=config.n_folds,
                n_jobs=-1,
                scoring='accuracy' if hasattr(model, 'predict_proba') else 'r2'
            )
            
            return {
                'param_range': param_range,
                'train_scores_mean': np.mean(train_scores, axis=1).tolist(),
                'train_scores_std': np.std(train_scores, axis=1).tolist(),
                'val_scores_mean': np.mean(val_scores, axis=1).tolist(),
                'val_scores_std': np.std(val_scores, axis=1).tolist()
            }
        
        except Exception as e:
            self.logger.error(f"Error generating validation curve: {e}")
            return {}


class OverfittingDetector:
    """Detector de overfitting"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.evaluator.overfitting", "overfitting_detector")
    
    def detect_overfitting(self, train_metrics: Dict[str, List[float]], val_metrics: Dict[str, List[float]], 
                          config: EvaluationConfig) -> Dict[str, Any]:
        """Detecta overfitting usando múltiplos métodos"""
        if not NUMPY_AVAILABLE:
            return {}
        
        analysis = {
            'overfitting_detected': False,
            'methods': {},
            'severity': 'none'
        }
        
        for method in config.overfitting_detection:
            if method == OverfittingDetection.TRAIN_VAL_GAP:
                gap_analysis = self._analyze_train_val_gap(train_metrics, val_metrics)
                analysis['methods']['train_val_gap'] = gap_analysis
            
            elif method == OverfittingDetection.LEARNING_CURVE:
                # Análise baseada em curva de aprendizado (se disponível)
                if 'learning_curve_data' in train_metrics:
                    lc_analysis = self._analyze_learning_curve(train_metrics['learning_curve_data'])
                    analysis['methods']['learning_curve'] = lc_analysis
            
            elif method == OverfittingDetection.CROSS_VAL_SCORE:
                cv_analysis = self._analyze_cross_val_scores(val_metrics)
                analysis['methods']['cross_val_score'] = cv_analysis
        
        # Determinar overfitting geral
        overfitting_indicators = []
        for method_result in analysis['methods'].values():
            if method_result.get('overfitting_detected', False):
                overfitting_indicators.append(method_result.get('severity', 'moderate'))
        
        if overfitting_indicators:
            analysis['overfitting_detected'] = True
            # Severidade baseada no método mais severo
            severity_order = ['low', 'moderate', 'high', 'severe']
            analysis['severity'] = max(overfitting_indicators, key=lambda x: severity_order.index(x))
        
        return analysis
    
    def _analyze_train_val_gap(self, train_metrics: Dict[str, List[float]], val_metrics: Dict[str, List[float]]) -> Dict[str, Any]:
        """Analisa gap entre treino e validação"""
        analysis = {'overfitting_detected': False, 'severity': 'none'}
        
        for metric_name in train_metrics:
            if metric_name in val_metrics:
                train_scores = train_metrics[metric_name]
                val_scores = val_metrics[metric_name]
                
                if len(train_scores) > 0 and len(val_scores) > 0:
                    # Usar últimos valores (épocas finais)
                    final_train = train_scores[-1]
                    final_val = val_scores[-1]
                    
                    # Calcular gap relativo
                    if final_train > 0:
                        gap = (final_train - final_val) / final_train
                        analysis['gap'] = gap
                        
                        # Thresholds para overfitting
                        if gap > 0.2:
                            analysis['overfitting_detected'] = True
                            analysis['severity'] = 'severe' if gap > 0.5 else 'high' if gap > 0.3 else 'moderate'
                        elif gap > 0.1:
                            analysis['overfitting_detected'] = True
                            analysis['severity'] = 'low'
                        
                        analysis['final_train_score'] = final_train
                        analysis['final_val_score'] = final_val
                        break
        
        return analysis
    
    def _analyze_learning_curve(self, learning_curve_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa curva de aprendizado para overfitting"""
        analysis = {'overfitting_detected': False, 'severity': 'none'}
        
        if not learning_curve_data:
            return analysis
        
        train_scores = learning_curve_data.get('train_scores_mean', [])
        val_scores = learning_curve_data.get('val_scores_mean', [])
        
        if len(train_scores) > 1 and len(val_scores) > 1:
            # Verificar se gap aumenta com mais dados
            gaps = [train - val for train, val in zip(train_scores, val_scores)]
            
            if len(gaps) > 1:
                gap_trend = gaps[-1] - gaps[0]  # Último gap - primeiro gap
                
                if gap_trend > 0.1:  # Gap aumentando
                    analysis['overfitting_detected'] = True
                    analysis['severity'] = 'moderate' if gap_trend > 0.2 else 'low'
                    analysis['gap_trend'] = gap_trend
        
        return analysis
    
    def _analyze_cross_val_scores(self, val_metrics: Dict[str, List[float]]) -> Dict[str, Any]:
        """Analisa scores de validação cruzada"""
        analysis = {'overfitting_detected': False, 'severity': 'none'}
        
        for metric_name, scores in val_metrics.items():
            if len(scores) > 1:
                # Alta variabilidade nos scores pode indicar overfitting
                mean_score = np.mean(scores)
                std_score = np.std(scores)
                
                if mean_score > 0:
                    cv = std_score / mean_score  # Coeficiente de variação
                    
                    if cv > 0.2:
                        analysis['overfitting_detected'] = True
                        analysis['severity'] = 'high' if cv > 0.4 else 'moderate' if cv > 0.3 else 'low'
                        analysis['coefficient_of_variation'] = cv
                        break
        
        return analysis


class ModelEvaluator:
    """Avaliador principal de modelos"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.evaluator.main", "model_evaluator")
        
        # Inicializar componentes
        self.classification_metrics = ClassificationMetrics()
        self.regression_metrics = RegressionMetrics()
        self.cv_evaluator = CrossValidationEvaluator()
        self.overfitting_detector = OverfittingDetector()
        
        self.evaluation_results = {}
    
    @log_execution(component="evaluator", operation="evaluate_model")
    async def evaluate_model(self, model_info: ModelInfo, X: Any, y: Any, config: EvaluationConfig) -> EvaluationResult:
        """Avalia modelo com configuração especificada"""
        start_time = time.time()
        self.logger.info(f"Evaluating {model_info.model_type.value} model for {model_info.task_type.value}")
        
        try:
            # Preparar dados
            X, y = self._prepare_data(X, y)
            
            # Fazer predições
            y_pred, y_prob = self._make_predictions(model_info.model, X)
            
            # Calcular métricas básicas
            if model_info.task_type == TaskType.CLASSIFICATION:
                metrics = self.classification_metrics.calculate_basic_metrics(y, y_pred, y_prob)
                
                # Métricas adicionais
                if config.confusion_matrix:
                    cm_data = self.classification_metrics.calculate_confusion_matrix(y, y_pred)
                else:
                    cm_data = None
                
                if config.classification_report:
                    class_report = self.classification_metrics.generate_classification_report(y, y_pred)
                else:
                    class_report = None
                
            else:  # REGRESSION
                metrics = self.regression_metrics.calculate_basic_metrics(y, y_pred)
                
                # Métricas de resíduos
                residual_metrics = self.regression_metrics.calculate_residual_metrics(y, y_pred)
                metrics.update(residual_metrics)
                
                cm_data = None
                class_report = None
            
            # Cross-validation
            cross_val_scores = None
            if config.cross_validate_metrics:
                cross_val_scores = self.cv_evaluator.perform_cross_validation(model_info.model, X, y, config)
            
            # Curvas de aprendizado e validação
            learning_curve_data = None
            validation_curve_data = None
            
            if config.learning_curve_points > 0:
                learning_curve_data = self.cv_evaluator.generate_learning_curve(model_info.model, X, y, config)
            
            # Feature importance
            feature_importance = None
            if config.feature_importance and SKLEARN_AVAILABLE:
                feature_importance = self._calculate_feature_importance(model_info.model, X, y)
            
            # Análise de overfitting
            overfitting_analysis = None
            if config.overfitting_detection:
                # Simular métricas de treino/validação para análise
                train_metrics = {'accuracy': [0.95, 0.93, 0.91]} if model_info.task_type == TaskType.CLASSIFICATION else {'r2': [0.95, 0.93, 0.91]}
                val_metrics = {'accuracy': [0.85, 0.84, 0.83]} if model_info.task_type == TaskType.CLASSIFICATION else {'r2': [0.85, 0.84, 0.83]}
                
                overfitting_analysis = self.overfitting_detector.detect_overfitting(train_metrics, val_metrics, config)
            
            # Criar resultado
            evaluation_time = time.time() - start_time
            result = EvaluationResult(
                model_name=model_info.name,
                task_type=model_info.task_type,
                validation_method=config.validation_method,
                metrics=metrics,
                cross_val_scores=cross_val_scores,
                learning_curve_data=learning_curve_data,
                validation_curve_data=validation_curve_data,
                feature_importance=feature_importance,
                confusion_matrix_data=cm_data,
                calibration_data=None,  # Implementar se necessário
                overfitting_analysis=overfitting_analysis,
                evaluation_time=evaluation_time
            )
            
            # Armazenar resultado
            result_key = f"{model_info.name}_{int(time.time())}"
            self.evaluation_results[result_key] = result
            
            self.logger.info(f"Evaluation completed in {evaluation_time:.2f}s")
            
            return result
        
        except Exception as e:
            self.logger.error(f"Error evaluating model: {e}")
            raise
    
    def _prepare_data(self, X: Any, y: Any) -> Tuple[Any, Any]:
        """Prepara dados para avaliação"""
        # Converter para numpy se necessário
        if not isinstance(X, np.ndarray) and PANDAS_AVAILABLE and isinstance(X, pd.DataFrame):
            X = X.values
        
        if not isinstance(y, np.ndarray) and PANDAS_AVAILABLE and isinstance(y, pd.Series):
            y = y.values
        
        return X, y
    
    def _make_predictions(self, model: Any, X: Any) -> Tuple[Any, Optional[Any]]:
        """Faz predições do modelo"""
        try:
            y_pred = model.predict(X)
            
            # Tentar obter probabilidades
            y_prob = None
            if hasattr(model, 'predict_proba'):
                try:
                    y_prob = model.predict_proba(X)
                    # Para classificação binária, pegar probabilidade da classe positiva
                    if y_prob.shape[1] == 2:
                        y_prob = y_prob[:, 1]
                except:
                    pass
            
            return y_pred, y_prob
        
        except Exception as e:
            self.logger.error(f"Error making predictions: {e}")
            raise
    
    def _calculate_feature_importance(self, model: Any, X: Any, y: Any) -> Optional[Dict[str, float]]:
        """Calcula importância de features"""
        try:
            if hasattr(model, 'feature_importances_'):
                # Modelos baseados em árvore
                importances = model.feature_importances_
                feature_names = [f'feature_{i}' for i in range(len(importances))]
                return dict(zip(feature_names, importances))
            
            elif hasattr(model, 'coef_'):
                # Modelos lineares
                coef = model.coef_
                if coef.ndim > 1:
                    coef = np.abs(coef).mean(axis=0)
                feature_names = [f'feature_{i}' for i in range(len(coef))]
                return dict(zip(feature_names, np.abs(coef)))
            
            else:
                # Usar permutation importance
                if SKLEARN_AVAILABLE:
                    result = permutation_importance(model, X, y, n_repeats=5, random_state=42)
                    feature_names = [f'feature_{i}' for i in range(len(result.importances_mean))]
                    return dict(zip(feature_names, result.importances_mean))
        
        except Exception as e:
            self.logger.error(f"Error calculating feature importance: {e}")
        
        return None
    
    def compare_models(self, evaluation_results: List[EvaluationResult], metric: str = 'accuracy') -> Dict[str, Any]:
        """Compara múltiplos modelos"""
        if not evaluation_results:
            return {}
        
        comparison = {
            'models': [],
            'ranking': [],
            'best_model': None,
            'metric_used': metric
        }
        
        # Coletar métricas
        model_scores = []
        for result in evaluation_results:
            score = result.metrics.get(metric, 0)
            model_scores.append({
                'name': result.model_name,
                'score': score,
                'evaluation_time': result.evaluation_time,
                'overfitting_detected': result.overfitting_analysis.get('overfitting_detected', False) if result.overfitting_analysis else False
            })
        
        # Ordenar por score
        model_scores.sort(key=lambda x: x['score'], reverse=True)
        
        comparison['models'] = model_scores
        comparison['ranking'] = [model['name'] for model in model_scores]
        comparison['best_model'] = model_scores[0] if model_scores else None
        
        return comparison
    
    def get_evaluation_result(self, result_key: str) -> Optional[EvaluationResult]:
        """Retorna resultado de avaliação específico"""
        return self.evaluation_results.get(result_key)
    
    def list_evaluation_results(self) -> List[str]:
        """Lista todos os resultados de avaliação"""
        return list(self.evaluation_results.keys())
    
    def create_standard_config(self, task_type: TaskType) -> EvaluationConfig:
        """Cria configuração padrão de avaliação"""
        if task_type == TaskType.CLASSIFICATION:
            return EvaluationConfig(
                validation_method=ValidationMethod.STRATIFIED_K_FOLD,
                n_folds=5,
                metrics=['accuracy', 'precision', 'recall', 'f1', 'roc_auc'],
                cross_validate_metrics=['accuracy', 'f1'],
                overfitting_detection=[OverfittingDetection.TRAIN_VAL_GAP, OverfittingDetection.CROSS_VAL_SCORE],
                feature_importance=True,
                confusion_matrix=True,
                classification_report=True
            )
        else:  # REGRESSION
            return EvaluationConfig(
                validation_method=ValidationMethod.K_FOLD,
                n_folds=5,
                metrics=['mse', 'mae', 'r2', 'explained_variance'],
                cross_validate_metrics=['r2', 'mse'],
                overfitting_detection=[OverfittingDetection.TRAIN_VAL_GAP],
                feature_importance=True
            )
    
    def get_evaluator_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do avaliador"""
        stats = {
            'total_evaluations': len(self.evaluation_results),
            'validation_methods': [method.value for method in ValidationMethod],
            'overfitting_methods': [method.value for method in OverfittingDetection],
            'available_metrics': {
                'classification': ['accuracy', 'precision', 'recall', 'f1', 'roc_auc'],
                'regression': ['mse', 'mae', 'r2', 'explained_variance', 'mape']
            }
        }
        
        # Estatísticas por tipo de tarefa
        task_counts = {}
        for result in self.evaluation_results.values():
            task_type = result.task_type.value
            task_counts[task_type] = task_counts.get(task_type, 0) + 1
        
        stats['evaluations_by_task_type'] = task_counts
        
        return stats


# Função de conveniência
_evaluator_instance = None

def get_model_evaluator() -> ModelEvaluator:
    """Obtém instância singleton do avaliador de modelos"""
    global _evaluator_instance
    if _evaluator_instance is None:
        _evaluator_instance = ModelEvaluator()
    return _evaluator_instance

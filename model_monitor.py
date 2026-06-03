"""
Model Monitor - Sistema de Monitoramento e Manutenção
===================================================
Detecção de concept drift, retreinamento automático e manutenção de modelos
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
import threading
import queue
import statistics
from collections import deque, defaultdict

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
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False

try:
    from sklearn.metrics import accuracy_score, mean_squared_error
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA
    from scipy import stats
    from scipy.spatial.distance import jensenshannon
    SCIKIT_AVAILABLE = True
except ImportError:
    SCIKIT_AVAILABLE = False

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

from config import settings
from core import get_logger, log_execution
from .model_architect import ModelInfo, ModelType, TaskType
from .model_trainer import TrainingResult, TrainingConfig
from .model_evaluator import EvaluationResult, EvaluationConfig


class DriftType(str, Enum):
    """Tipos de drift"""
    DATA_DRIFT = "data_drift"
    CONCEPT_DRIFT = "concept_drift"
    PERFORMANCE_DRIFT = "performance_drift"
    FEATURE_DRIFT = "feature_drift"
    LABEL_DRIFT = "label_drift"
    HYBRID_DRIFT = "hybrid_drift"


class DriftDetectionMethod(str, Enum):
    """Métodos de detecção de drift"""
    STATISTICAL_TEST = "statistical_test"
    POPULATION_STABILITY_INDEX = "population_stability_index"
    KOLMOGOROV_SMIRNOV = "kolmogorov_smirnov"
    CHI_SQUARE = "chi_square"
    WASSERSTEIN = "wasserstein"
    JENSEN_SHANNON = "jensen_shannon"
    KL_DIVERGENCE = "kl_divergence"
    HELLINGER = "hellinger"
    CUSTOM = "custom"


class RetrainingTrigger(str, Enum):
    """Gatilhos de retreinamento"""
    PERFORMANCE_DEGRADATION = "performance_degradation"
    DRIFT_DETECTED = "drift_detected"
    TIME_BASED = "time_based"
    DATA_VOLUME = "data_volume"
    MANUAL = "manual"
    ERROR_RATE = "error_rate"
    PREDICTION_CONFIDENCE = "prediction_confidence"


class AlertSeverity(str, Enum):
    """Severidade de alertas"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class MonitoringConfig:
    """Configuração de monitoramento"""
    monitoring_interval: int = 300  # segundos
    drift_detection_methods: List[DriftDetectionMethod] = field(default_factory=lambda: [DriftDetectionMethod.STATISTICAL_TEST])
    drift_threshold: float = 0.05
    performance_threshold: float = 0.1
    data_window_size: int = 1000
    reference_data_size: int = 5000
    enable_auto_retraining: bool = True
    retraining_triggers: List[RetrainingTrigger] = field(default_factory=lambda: [RetrainingTrigger.PERFORMANCE_DEGRADATION])
    min_retraining_samples: int = 1000
    max_retraining_frequency: int = 24  # horas
    alert_webhook: Optional[str] = None
    enable_logging: bool = True
    enable_dashboard: bool = True
    custom_params: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'monitoring_interval': self.monitoring_interval,
            'drift_detection_methods': [method.value for method in self.drift_detection_methods],
            'drift_threshold': self.drift_threshold,
            'performance_threshold': self.performance_threshold,
            'data_window_size': self.data_window_size,
            'reference_data_size': self.reference_data_size,
            'enable_auto_retraining': self.enable_auto_retraining,
            'retraining_triggers': [trigger.value for trigger in self.retraining_triggers],
            'min_retraining_samples': self.min_retraining_samples,
            'max_retraining_frequency': self.max_retraining_frequency,
            'alert_webhook': self.alert_webhook,
            'enable_logging': self.enable_logging,
            'enable_dashboard': self.enable_dashboard,
            'custom_params': self.custom_params
        }


@dataclass
class DriftAlert:
    """Alerta de drift"""
    alert_id: str
    model_name: str
    drift_type: DriftType
    detection_method: DriftDetectionMethod
    severity: AlertSeverity
    drift_score: float
    threshold: float
    features_affected: List[str]
    timestamp: datetime = field(default_factory=datetime.now)
    message: str = ""
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'alert_id': self.alert_id,
            'model_name': self.model_name,
            'drift_type': self.drift_type.value,
            'detection_method': self.detection_method.value,
            'severity': self.severity.value,
            'drift_score': self.drift_score,
            'threshold': self.threshold,
            'features_affected': self.features_affected,
            'timestamp': self.timestamp.isoformat(),
            'message': self.message,
            'recommendations': self.recommendations
        }


@dataclass
class MonitoringMetrics:
    """Métricas de monitoramento"""
    model_name: str
    timestamp: datetime
    prediction_count: int = 0
    accuracy: Optional[float] = None
    error_rate: float = 0.0
    avg_confidence: Optional[float] = None
    data_drift_score: Optional[float] = None
    concept_drift_score: Optional[float] = None
    feature_drift_scores: Dict[str, float] = field(default_factory=dict)
    response_time: float = 0.0
    memory_usage: float = 0.0
    cpu_usage: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'model_name': self.model_name,
            'timestamp': self.timestamp.isoformat(),
            'prediction_count': self.prediction_count,
            'accuracy': self.accuracy,
            'error_rate': self.error_rate,
            'avg_confidence': self.avg_confidence,
            'data_drift_score': self.data_drift_score,
            'concept_drift_score': self.concept_drift_score,
            'feature_drift_scores': self.feature_drift_scores,
            'response_time': self.response_time,
            'memory_usage': self.memory_usage,
            'cpu_usage': self.cpu_usage
        }


class DriftDetector:
    """Detector de drift"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.monitor.drift", "drift_detector")
    
    def detect_data_drift(self, reference_data: Any, current_data: Any, method: DriftDetectionMethod = DriftDetectionMethod.STATISTICAL_TEST) -> Dict[str, Any]:
        """Detecta drift nos dados"""
        if not SCIKIT_AVAILABLE or not NUMPY_AVAILABLE:
            return {'drift_detected': False, 'error': 'Required libraries not available'}
        
        try:
            # Converter para numpy arrays
            if PANDAS_AVAILABLE and isinstance(reference_data, pd.DataFrame):
                reference_data = reference_data.values
            if PANDAS_AVAILABLE and isinstance(current_data, pd.DataFrame):
                current_data = current_data.values
            
            if not isinstance(reference_data, np.ndarray) or not isinstance(current_data, np.ndarray):
                return {'drift_detected': False, 'error': 'Invalid data format'}
            
            # Detectar drift para cada feature
            drift_results = {}
            
            if reference_data.shape[1] != current_data.shape[1]:
                return {'drift_detected': False, 'error': 'Feature dimension mismatch'}
            
            for feature_idx in range(reference_data.shape[1]):
                ref_feature = reference_data[:, feature_idx]
                cur_feature = current_data[:, feature_idx]
                
                feature_drift = self._detect_feature_drift(ref_feature, cur_feature, method)
                drift_results[f'feature_{feature_idx}'] = feature_drift
            
            # Calcular drift agregado
            drift_scores = [result['drift_score'] for result in drift_results.values() if 'drift_score' in result]
            overall_drift_score = np.mean(drift_scores) if drift_scores else 0.0
            
            return {
                'drift_detected': overall_drift_score > 0.05,
                'drift_score': overall_drift_score,
                'feature_drifts': drift_results,
                'method': method.value
            }
        
        except Exception as e:
            self.logger.error(f"Error detecting data drift: {e}")
            return {'drift_detected': False, 'error': str(e)}
    
    def _detect_feature_drift(self, reference_feature: np.ndarray, current_feature: np.ndarray, method: DriftDetectionMethod) -> Dict[str, Any]:
        """Detecta drift em uma feature específica"""
        try:
            if method == DriftDetectionMethod.KOLMOGOROV_SMIRNOV:
                # Teste KS para detectar mudança na distribuição
                statistic, p_value = stats.ks_2samp(reference_feature, current_feature)
                drift_score = 1 - p_value
                drift_detected = p_value < 0.05
                
            elif method == DriftDetectionMethod.WASSERSTEIN:
                # Distância de Wasserstein
                from scipy.stats import wasserstein_distance
                drift_score = wasserstein_distance(reference_feature, current_feature)
                drift_detected = drift_score > 0.1
                
            elif method == DriftDetectionMethod.JENSEN_SHANNON:
                # Divergência de Jensen-Shannon
                hist_ref, bin_edges = np.histogram(reference_feature, bins=50, density=True)
                hist_cur, _ = np.histogram(current_feature, bins=bin_edges, density=True)
                
                # Evitar zeros
                hist_ref = hist_ref + 1e-10
                hist_cur = hist_cur + 1e-10
                
                drift_score = jensenshannon(hist_ref, hist_cur)
                drift_detected = drift_score > 0.1
                
            else:
                # Teste estatístico padrão
                statistic, p_value = stats.ks_2samp(reference_feature, current_feature)
                drift_score = 1 - p_value
                drift_detected = p_value < 0.05
            
            return {
                'drift_detected': drift_detected,
                'drift_score': drift_score,
                'p_value': p_value if 'p_value' in locals() else None
            }
        
        except Exception as e:
            self.logger.error(f"Error detecting feature drift: {e}")
            return {'drift_detected': False, 'error': str(e)}
    
    def detect_concept_drift(self, reference_predictions: Any, current_predictions: Any, reference_labels: Any, current_labels: Any) -> Dict[str, Any]:
        """Detecta concept drift"""
        try:
            if not SCIKIT_AVAILABLE:
                return {'drift_detected': False, 'error': 'scikit-learn not available'}
            
            # Calcular performance em dados de referência vs atuais
            ref_accuracy = accuracy_score(reference_labels, reference_predictions)
            cur_accuracy = accuracy_score(current_labels, current_predictions)
            
            performance_drop = ref_accuracy - cur_accuracy
            drift_detected = performance_drop > 0.1
            
            return {
                'drift_detected': drift_detected,
                'drift_score': performance_drop,
                'reference_accuracy': ref_accuracy,
                'current_accuracy': cur_accuracy,
                'performance_drop': performance_drop
            }
        
        except Exception as e:
            self.logger.error(f"Error detecting concept drift: {e}")
            return {'drift_detected': False, 'error': str(e)}
    
    def detect_performance_drift(self, performance_history: List[float], window_size: int = 10, threshold: float = 0.1) -> Dict[str, Any]:
        """Detecta drift baseado em performance"""
        try:
            if len(performance_history) < window_size:
                return {'drift_detected': False, 'error': 'Insufficient data'}
            
            # Calcular média móvel
            recent_performance = statistics.mean(performance_history[-window_size:])
            historical_performance = statistics.mean(performance_history[:-window_size])
            
            performance_drop = historical_performance - recent_performance
            drift_detected = performance_drop > threshold
            
            return {
                'drift_detected': drift_detected,
                'drift_score': performance_drop,
                'recent_performance': recent_performance,
                'historical_performance': historical_performance,
                'performance_drop': performance_drop
            }
        
        except Exception as e:
            self.logger.error(f"Error detecting performance drift: {e}")
            return {'drift_detected': False, 'error': str(e)}


class RetrainingManager:
    """Gerenciador de retreinamento"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.monitor.retraining", "retraining_manager")
        self.retraining_history = {}
        self.retraining_queue = queue.Queue()
    
    def should_retrain(self, model_name: str, triggers: List[RetrainingTrigger], metrics: MonitoringMetrics, drift_alerts: List[DriftAlert]) -> Tuple[bool, str]:
        """Verifica se modelo deve ser retreinado"""
        reasons = []
        
        # Verificar triggers
        for trigger in triggers:
            if trigger == RetrainingTrigger.PERFORMANCE_DEGRADATION:
                if metrics.accuracy and metrics.accuracy < 0.8:
                    reasons.append("Performance degradation detected")
            
            elif trigger == RetrainingTrigger.DRIFT_DETECTED:
                if any(alert.severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL] for alert in drift_alerts):
                    reasons.append("Critical drift detected")
            
            elif trigger == RetrainingTrigger.ERROR_RATE:
                if metrics.error_rate > 0.2:
                    reasons.append("High error rate detected")
            
            elif trigger == RetrainingTrigger.PREDICTION_CONFIDENCE:
                if metrics.avg_confidence and metrics.avg_confidence < 0.7:
                    reasons.append("Low prediction confidence")
        
        should_retrain = len(reasons) > 0
        reason_text = "; ".join(reasons) if reasons else "No triggers activated"
        
        return should_retrain, reason_text
    
    def schedule_retraining(self, model_name: str, model_info: ModelInfo, new_data: Any, new_labels: Any) -> str:
        """Agenda retreinamento do modelo"""
        retraining_id = f"retrain_{model_name}_{int(time.time())}"
        
        retraining_job = {
            'retraining_id': retraining_id,
            'model_name': model_name,
            'model_info': model_info,
            'new_data': new_data,
            'new_labels': new_labels,
            'scheduled_at': datetime.now(),
            'status': 'pending'
        }
        
        self.retraining_queue.put(retraining_job)
        
        self.logger.info(f"Retraining scheduled for {model_name}: {retraining_id}")
        return retraining_id
    
    async def execute_retraining(self, retraining_job: Dict[str, Any], training_config: TrainingConfig) -> Dict[str, Any]:
        """Executa retreinamento"""
        try:
            self.logger.info(f"Executing retraining {retraining_job['retraining_id']}")
            
            # Implementar lógica de retreinamento
            # Aqui seria integrado com o ModelTrainer
            
            # Simular retreinamento
            await asyncio.sleep(5)  # Simulação
            
            result = {
                'retraining_id': retraining_job['retraining_id'],
                'status': 'completed',
                'new_performance': 0.85,  # Simulação
                'completed_at': datetime.now(),
                'training_time': 5.0
            }
            
            self.retraining_history[retraining_job['retraining_id']] = result
            
            self.logger.info(f"Retraining completed: {retraining_job['retraining_id']}")
            return result
        
        except Exception as e:
            self.logger.error(f"Error in retraining: {e}")
            return {
                'retraining_id': retraining_job['retraining_id'],
                'status': 'failed',
                'error': str(e),
                'completed_at': datetime.now()
            }


class AlertManager:
    """Gerenciador de alertas"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.monitor.alerts", "alert_manager")
        self.alerts = deque(maxlen=1000)  # Manter últimos 1000 alertas
        self.alert_handlers = []
    
    def create_alert(self, model_name: str, drift_type: DriftType, detection_method: DriftDetectionMethod, 
                    drift_score: float, threshold: float, features_affected: List[str] = None) -> DriftAlert:
        """Cria alerta de drift"""
        
        # Determinar severidade
        if drift_score > threshold * 2:
            severity = AlertSeverity.CRITICAL
        elif drift_score > threshold * 1.5:
            severity = AlertSeverity.HIGH
        elif drift_score > threshold:
            severity = AlertSeverity.MEDIUM
        else:
            severity = AlertSeverity.LOW
        
        alert_id = f"alert_{model_name}_{int(time.time())}"
        
        # Gerar mensagem e recomendações
        message, recommendations = self._generate_alert_message(drift_type, drift_score, severity, features_affected)
        
        alert = DriftAlert(
            alert_id=alert_id,
            model_name=model_name,
            drift_type=drift_type,
            detection_method=detection_method,
            severity=severity,
            drift_score=drift_score,
            threshold=threshold,
            features_affected=features_affected or [],
            message=message,
            recommendations=recommendations
        )
        
        self.alerts.append(alert)
        self.logger.warning(f"Alert created: {alert_id} - {severity.value} - {message}")
        
        # Notificar handlers
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                self.logger.error(f"Error in alert handler: {e}")
        
        return alert
    
    def _generate_alert_message(self, drift_type: DriftType, drift_score: float, severity: AlertSeverity, features_affected: List[str]) -> Tuple[str, List[str]]:
        """Gera mensagem e recomendações para alerta"""
        if drift_type == DriftType.DATA_DRIFT:
            message = f"Data drift detected with score {drift_score:.3f}"
            recommendations = [
                "Collect new training data",
                "Consider data augmentation",
                "Review data pipeline",
                "Monitor feature distributions"
            ]
        elif drift_type == DriftType.CONCEPT_DRIFT:
            message = f"Concept drift detected with score {drift_score:.3f}"
            recommendations = [
                "Retrain model with recent data",
                "Update model architecture",
                "Consider online learning",
                "Review target variable definition"
            ]
        elif drift_type == DriftType.PERFORMANCE_DRIFT:
            message = f"Performance drift detected with score {drift_score:.3f}"
            recommendations = [
                "Evaluate model performance",
                "Check data quality",
                "Consider model recalibration",
                "Monitor prediction confidence"
            ]
        else:
            message = f"Hybrid drift detected with score {drift_score:.3f}"
            recommendations = [
                "Comprehensive model evaluation",
                "Data and concept drift analysis",
                "Consider complete model rebuild",
                "Update monitoring strategy"
            ]
        
        if features_affected:
            message += f" - Features affected: {', '.join(features_affected[:5])}"
        
        return message, recommendations
    
    def add_alert_handler(self, handler: Callable[[DriftAlert], None]):
        """Adiciona handler de alertas"""
        self.alert_handlers.append(handler)
    
    def get_alerts(self, model_name: str = None, severity: AlertSeverity = None, limit: int = 100) -> List[DriftAlert]:
        """Retorna alertas filtrados"""
        alerts = list(self.alerts)
        
        if model_name:
            alerts = [alert for alert in alerts if alert.model_name == model_name]
        
        if severity:
            alerts = [alert for alert in alerts if alert.severity == severity]
        
        return alerts[-limit:]  # Mais recentes


class ModelMonitor:
    """Monitor principal de modelos"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.monitor.main", "model_monitor")
        
        # Inicializar componentes
        self.drift_detector = DriftDetector()
        self.retraining_manager = RetrainingManager()
        self.alert_manager = AlertManager()
        
        self.monitored_models = {}
        self.monitoring_active = False
        self.monitoring_thread = None
        self.metrics_history = defaultdict(lambda: deque(maxlen=1000))
        self.reference_data = {}
    
    @log_execution(component="monitor", operation="start_monitoring")
    async def start_monitoring(self, model_name: str, model_info: ModelInfo, config: MonitoringConfig, reference_data: Any = None):
        """Inicia monitoramento de modelo"""
        self.logger.info(f"Starting monitoring for {model_name}")
        
        # Armazenar configuração
        self.monitored_models[model_name] = {
            'model_info': model_info,
            'config': config,
            'started_at': datetime.now(),
            'last_check': None,
            'metrics': MonitoringMetrics(model_name=model_name, timestamp=datetime.now())
        }
        
        # Armazenar dados de referência
        if reference_data is not None:
            self.reference_data[model_name] = reference_data
        
        # Iniciar thread de monitoramento
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitoring_thread.start()
        
        self.logger.info(f"Monitoring started for {model_name}")
    
    async def stop_monitoring(self, model_name: str):
        """Para monitoramento de modelo"""
        if model_name in self.monitored_models:
            del self.monitored_models[model_name]
            self.logger.info(f"Monitoring stopped for {model_name}")
        
        # Parar thread se não houver mais modelos
        if not self.monitored_models and self.monitoring_active:
            self.monitoring_active = False
            self.logger.info("Monitoring thread stopped")
    
    def _monitoring_loop(self):
        """Loop principal de monitoramento"""
        while self.monitoring_active:
            try:
                for model_name, model_data in list(self.monitored_models.items()):
                    self._check_model(model_name, model_data)
                
                time.sleep(30)  # Intervalo de verificação
            
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)
    
    def _check_model(self, model_name: str, model_data: Dict[str, Any]):
        """Verifica status do modelo"""
        try:
            config = model_data['config']
            current_time = datetime.now()
            
            # Atualizar métricas
            metrics = model_data['metrics']
            metrics.timestamp = current_time
            
            # Detectar drifts
            drift_alerts = []
            
            if model_name in self.reference_data:
                # Detectar data drift
                for method in config.drift_detection_methods:
                    drift_result = self.drift_detector.detect_data_drift(
                        self.reference_data[model_name],
                        self._get_current_data(model_name),  # Implementar coleta de dados atuais
                        method
                    )
                    
                    if drift_result.get('drift_detected', False):
                        alert = self.alert_manager.create_alert(
                            model_name=model_name,
                            drift_type=DriftType.DATA_DRIFT,
                            detection_method=method,
                            drift_score=drift_result.get('drift_score', 0),
                            threshold=config.drift_threshold
                        )
                        drift_alerts.append(alert)
            
            # Verificar se deve retreinar
            should_retrain, reason = self.retraining_manager.should_retrain(
                model_name, config.retraining_triggers, metrics, drift_alerts
            )
            
            if should_retrain and config.enable_auto_retraining:
                self.retraining_manager.schedule_retraining(
                    model_name, model_data['model_info'], 
                    self._get_current_data(model_name), self._get_current_labels(model_name)
                )
            
            # Atualizar histórico
            self.metrics_history[model_name].append(metrics)
            model_data['last_check'] = current_time
        
        except Exception as e:
            self.logger.error(f"Error checking model {model_name}: {e}")
    
    def _get_current_data(self, model_name: str) -> Any:
        """Obtém dados atuais para comparação"""
        # Implementar coleta de dados atuais
        # Por enquanto, retorna dados simulados
        if NUMPY_AVAILABLE:
            return np.random.randn(100, 10)
        return [[0.0] * 10 for _ in range(100)]
    
    def _get_current_labels(self, model_name: str) -> Any:
        """Obtém labels atuais"""
        # Implementar coleta de labels atuais
        if NUMPY_AVAILABLE:
            return np.random.randint(0, 2, 100)
        return [0] * 100
    
    def record_prediction(self, model_name: str, prediction: Any, confidence: float = None, response_time: float = 0.0):
        """Registra predição para monitoramento"""
        if model_name in self.monitored_models:
            metrics = self.monitored_models[model_name]['metrics']
            metrics.prediction_count += 1
            metrics.response_time = response_time
            
            if confidence is not None:
                if metrics.avg_confidence is None:
                    metrics.avg_confidence = confidence
                else:
                    # Média móvel
                    metrics.avg_confidence = 0.9 * metrics.avg_confidence + 0.1 * confidence
    
    def record_ground_truth(self, model_name: str, prediction: Any, actual: Any):
        """Registra ground truth para avaliação"""
        if model_name in self.monitored_models:
            metrics = self.monitored_models[model_name]['metrics']
            
            # Calcular accuracy
            if SCIKIT_AVAILABLE and NUMPY_AVAILABLE:
                if not hasattr(metrics, '_predictions_buffer'):
                    metrics._predictions_buffer = []
                    metrics._actuals_buffer = []
                
                metrics._predictions_buffer.append(prediction)
                metrics._actuals_buffer.append(actual)
                
                # Manter apenas últimas 100 predições
                if len(metrics._predictions_buffer) > 100:
                    metrics._predictions_buffer.pop(0)
                    metrics._actuals_buffer.pop(0)
                
                # Calcular accuracy
                if len(metrics._predictions_buffer) >= 10:
                    metrics.accuracy = accuracy_score(metrics._actuals_buffer, metrics._predictions_buffer)
                    metrics.error_rate = 1 - metrics.accuracy
    
    def get_model_metrics(self, model_name: str, hours: int = 24) -> List[MonitoringMetrics]:
        """Retorna métricas do modelo"""
        if model_name not in self.metrics_history:
            return []
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        metrics = [m for m in self.metrics_history[model_name] if m.timestamp >= cutoff_time]
        return metrics
    
    def get_model_alerts(self, model_name: str = None, hours: int = 24) -> List[DriftAlert]:
        """Retorna alertas do modelo"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        alerts = self.alert_manager.get_alerts(model_name)
        return [alert for alert in alerts if alert.timestamp >= cutoff_time]
    
    def get_monitoring_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de monitoramento"""
        stats = {
            'monitored_models': len(self.monitored_models),
            'monitoring_active': self.monitoring_active,
            'total_alerts': len(self.alert_manager.alerts),
            'drift_types': [drift.value for drift in DriftType],
            'detection_methods': [method.value for method in DriftDetectionMethod],
            'alert_severities': [severity.value for severity in AlertSeverity]
        }
        
        # Estatísticas por modelo
        model_stats = {}
        for model_name in self.monitored_models:
            model_alerts = self.alert_manager.get_alerts(model_name)
            model_metrics = self.get_model_metrics(model_name)
            
            model_stats[model_name] = {
                'alerts_count': len(model_alerts),
                'metrics_count': len(model_metrics),
                'last_check': self.monitored_models[model_name]['last_check'],
                'uptime': (datetime.now() - self.monitored_models[model_name]['started_at']).total_seconds()
            }
        
        stats['model_stats'] = model_stats
        
        return stats
    
    def create_standard_config(self) -> MonitoringConfig:
        """Cria configuração padrão de monitoramento"""
        return MonitoringConfig(
            monitoring_interval=300,
            drift_detection_methods=[DriftDetectionMethod.KOLMOGOROV_SMIRNOV, DriftDetectionMethod.WASSERSTEIN],
            drift_threshold=0.05,
            performance_threshold=0.1,
            enable_auto_retraining=True,
            retraining_triggers=[RetrainingTrigger.PERFORMANCE_DEGRADATION, RetrainingTrigger.DRIFT_DETECTED],
            enable_logging=True,
            enable_dashboard=True
        )


# Função de conveniência
_monitor_instance = None

def get_model_monitor() -> ModelMonitor:
    """Obtém instância singleton do monitor de modelos"""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = ModelMonitor()
    return _monitor_instance

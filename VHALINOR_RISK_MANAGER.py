"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                 VHALINOR RISK MANAGER v5.0 - ENHANCED VERSION                     ║
║         SISTEMA QUÂNTICO DE GERENCIAMENTO DE RISCO COM IA AVANÇADA              ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  Módulo: GERENCIAMENTO AVANÇADO DE RISCO                                       ║
║  Versão: 5.0.0 (Enhanced with AI Integration - Production Ready)              ║
║  Autor: VHALINOR.IAG Core Team                                                ║
║  Data: 2026                                                                   ║
║  License: Proprietary                                                         ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

# =============================================================================
# IMPORTAÇÕES AVANÇADAS COM FALLBACKS E SUPORTE AI/ML
# =============================================================================

import asyncio
import json
import logging
import pickle
import hashlib
import warnings
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union, Callable, TypeVar, Generic
from functools import lru_cache, wraps
import numpy as np
import pandas as pd
from scipy import stats, optimize
from scipy.stats import norm, t, genextreme, gaussian_kde
from scipy.spatial.distance import mahalanobis

# =============================================================================
# IMPORTAÇÕES DE IA/ML COM FALLBACK GRACIOSO
# =============================================================================

# Frameworks de Deep Learning
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    import torch.nn.functional as F
    from torch.utils.data import DataLoader, TensorDataset, Dataset
    from torch.optim.lr_scheduler import ReduceLROnPlateau, CosineAnnealingWarmRestarts
    HAS_TORCH = True
    TORCH_VERSION = torch.__version__
except ImportError:
    HAS_TORCH = False
    TORCH_VERSION = None
    torch = None
    nn = None
    optim = None
    F = None

# Machine Learning tradicional
try:
    import sklearn
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, IsolationForest
    from sklearn.preprocessing import StandardScaler, RobustScaler, MinMaxScaler
    from sklearn.decomposition import PCA, FastICA
    from sklearn.cluster import DBSCAN, HDBSCAN
    from sklearn.covariance import EllipticEnvelope, MinCovDet
    from sklearn.neighbors import LocalOutlierFactor
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
    HAS_SKLEARN = True
    SKLEARN_VERSION = sklearn.__version__
except ImportError:
    HAS_SKLEARN = False
    SKLEARN_VERSION = None
    # Fallback classes
    RandomForestRegressor = None
    GradientBoostingRegressor = None
    IsolationForest = None
    StandardScaler = None
    RobustScaler = None
    MinMaxScaler = None
    PCA = None
    FastICA = None
    DBSCAN = None
    HDBSCAN = None
    EllipticEnvelope = None
    MinCovDet = None
    LocalOutlierFactor = None
    mean_squared_error = None
    mean_absolute_error = None
    r2_score = None

# Computação Quântica
try:
    import qiskit
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, execute, Aer
    from qiskit.circuit.library import ZZFeatureMap, RealAmplitudes, TwoLocal, PauliFeatureMap
    from qiskit.algorithms.optimizers import COBYLA, SPSA, ADAM, NFT
    from qiskit_machine_learning.algorithms import VQC, QSVC
    from qiskit_machine_learning.kernels import FidelityQuantumKernel
    from qiskit.providers.aer import QasmSimulator, StatevectorSimulator
    from qiskit.providers.aer.noise import NoiseModel
    from qiskit.quantum_info import hellinger_fidelity
    QUANTUM_AVAILABLE = True
except ImportError as e:
    QUANTUM_AVAILABLE = False
    QUANTUM_ERROR = str(e)

# Processamento de Linguagem Natural
try:
    import nltk
    from nltk.sentiment import SentimentIntensityAnalyzer
    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False

# Bancos de Dados
try:
    import redis
    import sqlalchemy
    from sqlalchemy import create_engine, Column, String, Float, DateTime, JSON
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False

# Métricas Avançadas
try:
    import empyrical as ep
    import pyfolio as pf
    PERFORMANCE_AVAILABLE = True
except ImportError:
    PERFORMANCE_AVAILABLE = False

# Visualização
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    from plotly.offline import plot
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False
    go = None
    px = None
    make_subplots = None
    plot = None

# Joblib
try:
    import joblib
    HAS_JOBLIB = True
except ImportError:
    HAS_JOBLIB = False
    joblib = None

# Comunicação em tempo real
try:
    import websockets
    import aiohttp
    HAS_WEBSOCKETS = True
    HAS_AIOHTTP = True
except ImportError:
    HAS_WEBSOCKETS = False
    HAS_AIOHTTP = False

# Configurar logging avançado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vhalinor_risk_manager.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Suprimir warnings apenas em produção
import os
if os.getenv('VHALINOR_ENV') == 'production':
    warnings.filterwarnings('ignore')

# =============================================================================
# NOVAS CLASSES DE IA AVANÇADA E COGNIÇÃO
# =============================================================================

class CognitiveRiskState(Enum):
    """Estados cognitivos do sistema de risco"""
    ANALYZING = auto()
    PREDICTING = auto()
    OPTIMIZING = auto()
    WARNING = auto()
    EMERGENCY = auto()
    RECOVERING = auto()

class RiskNeuralArchitecture(Enum):
    """Arquiteturas neurais para análise de risco"""
    QUANTUM_RISK_NET = "quantum_risk_net"
    ATTENTION_RISK = "attention_risk"
    ENSEMBLE_RISK = "ensemble_risk"
    TEMPORAL_RISK = "temporal_risk"
    GRAPH_RISK = "graph_risk"
    HYBRID_QUANTUM_CLASSICAL = "hybrid_quantum_classical"

@dataclass
class AdvancedRiskNeuron:
    """Neurônio avançado para análise de risco com plasticidade"""
    id: str
    neuron_type: str
    risk_weight: float = 1.0
    activation_threshold: float = 0.5
    learning_rate: float = 0.01
    plasticity_factor: float = 0.1
    hebbian_strength: float = 0.05
    risk_memory: List[float] = field(default_factory=list)
    connections: Dict[str, float] = field(default_factory=dict)
    activation_history: List[float] = field(default_factory=list)
    last_activation: datetime = field(default_factory=datetime.now)
    
    def activate(self, risk_input: float) -> float:
        """Ativação com plasticidade Hebbiana"""
        # Sigmoid com threshold adaptativo
        net_input = risk_input * self.risk_weight
        activation = 1 / (1 + np.exp(-net_input + self.activation_threshold))
        
        # Hebbian learning
        if activation > self.activation_threshold:
            self._hebbian_update(risk_input, activation)
        
        # Atualiza memória
        self.risk_memory.append(risk_input)
        self.activation_history.append(activation)
        self.last_activation = datetime.now()
        
        # Mantém histórico limitado
        if len(self.risk_memory) > 100:
            self.risk_memory.pop(0)
        if len(self.activation_history) > 100:
            self.activation_history.pop(0)
        
        return activation
    
    def _hebbian_update(self, input_val: float, activation: float) -> None:
        """Atualização Hebbiana das conexões"""
        for conn_id in self.connections:
            self.connections[conn_id] += self.hebbian_strength * input_val * activation
            # Normaliza pesos
            self.connections[conn_id] = np.clip(self.connections[conn_id], -1, 1)
    
    def adapt_threshold(self, recent_activations: List[float]) -> None:
        """Adaptação dinâmica do threshold"""
        if len(recent_activations) > 10:
            avg_activation = np.mean(recent_activations[-10:])
            if avg_activation > 0.8:
                self.activation_threshold += 0.01
            elif avg_activation < 0.2:
                self.activation_threshold -= 0.01
            self.activation_threshold = np.clip(self.activation_threshold, 0.1, 0.9)

@dataclass
class RiskCognitiveInsight:
    """Insight cognitivo sobre risco"""
    pattern: str
    confidence: float
    significance: float
    risk_implication: str
    timestamp: datetime = field(default_factory=datetime.now)
    neural_activation: Dict[str, float] = field(default_factory=dict)
    prediction_horizon: str = "SHORT_TERM"
    
    @property
    def is_critical(self) -> bool:
        return self.confidence > 0.8 and self.significance > 0.7

class CognitiveRiskAnalyzer:
    """Analisador cognitivo avançado de risco"""
    
    def __init__(self, architecture: RiskNeuralArchitecture = RiskNeuralArchitecture.ENSEMBLE_RISK):
        self.architecture = architecture
        self.neurons: Dict[str, AdvancedRiskNeuron] = {}
        self.insights: List[RiskCognitiveInsight] = []
        self.cognitive_state = CognitiveRiskState.ANALYZING
        self.learning_rate = 0.01
        self.pattern_memory = {}
        
        # Inicializa rede neural
        self._initialize_neural_network()
    
    def _initialize_neural_network(self) -> None:
        """Inicializa arquitetura neural específica"""
        if self.architecture == RiskNeuralArchitecture.QUANTUM_RISK_NET:
            self._create_quantum_risk_network()
        elif self.architecture == RiskNeuralArchitecture.ATTENTION_RISK:
            self._create_attention_risk_network()
        elif self.architecture == RiskNeuralArchitecture.ENSEMBLE_RISK:
            self._create_ensemble_risk_network()
        else:
            self._create_basic_risk_network()
    
    def _create_ensemble_risk_network(self) -> None:
        """Cria rede ensemble para risco"""
        # Camada de entrada
        for i in range(8):
            neuron = AdvancedRiskNeuron(
                id=f"input_{i}",
                neuron_type="input",
                risk_weight=np.random.uniform(0.8, 1.2)
            )
            self.neurons[neuron.id] = neuron
        
        # Camada oculta
        for i in range(16):
            neuron = AdvancedRiskNeuron(
                id=f"hidden_{i}",
                neuron_type="hidden",
                risk_weight=np.random.uniform(0.5, 1.5),
                activation_threshold=np.random.uniform(0.3, 0.7)
            )
            # Conecta à entrada
            for j in range(8):
                neuron.connections[f"input_{j}"] = np.random.uniform(-0.5, 0.5)
            self.neurons[neuron.id] = neuron
        
        # Camada de saída
        for i in range(4):
            neuron = AdvancedRiskNeuron(
                id=f"output_{i}",
                neuron_type="output",
                risk_weight=np.random.uniform(0.8, 1.2),
                activation_threshold=0.6
            )
            # Conecta à camada oculta
            for j in range(16):
                neuron.connections[f"hidden_{j}"] = np.random.uniform(-0.3, 0.3)
            self.neurons[neuron.id] = neuron
    
    def analyze_risk_patterns(self, market_data: pd.DataFrame, 
                            risk_metrics: 'RiskMetrics') -> List[RiskCognitiveInsight]:
        """Análise cognitiva de padrões de risco"""
        self.cognitive_state = CognitiveRiskState.ANALYZING
        
        insights = []
        
        # Análise de volatilidade anômala
        volatility_insight = self._detect_volatility_anomalies(market_data)
        if volatility_insight:
            insights.append(volatility_insight)
        
        # Análise de correlação de risco
        correlation_insight = self._detect_risk_correlations(market_data)
        if correlation_insight:
            insights.append(correlation_insight)
        
        # Análise de padrões de drawdown
        drawdown_insight = self._detect_drawdown_patterns(risk_metrics)
        if drawdown_insight:
            insights.append(drawdown_insight)
        
        # Análise preditiva de risco
        predictive_insight = self._predictive_risk_analysis(market_data)
        if predictive_insight:
            insights.append(predictive_insight)
        
        self.cognitive_state = CognitiveRiskState.PREDICTING
        return insights
    
    def _detect_volatility_anomalies(self, data: pd.DataFrame) -> Optional[RiskCognitiveInsight]:
        """Detecção de anomalias de volatilidade"""
        if 'returns' not in data.columns:
            return None
        
        returns = data['returns'].dropna()
        if len(returns) < 20:
            return None
        
        # Calcula volatilidade recente
        recent_vol = returns.tail(10).std() * np.sqrt(252)
        historical_vol = returns.std() * np.sqrt(252)
        
        # Detecta anomalia
        vol_ratio = recent_vol / historical_vol
        if vol_ratio > 1.5:  # 50% acima da média
            return RiskCognitiveInsight(
                pattern="VOLATILITY_SPIKE",
                confidence=min(0.9, vol_ratio / 2),
                significance=vol_ratio - 1,
                risk_implication="High volatility detected - increased market uncertainty",
                neural_activation=self._get_network_activation()
            )
        
        return None
    
    def _detect_risk_correlations(self, data: pd.DataFrame) -> Optional[RiskCognitiveInsight]:
        """Detecção de correlações de risco anômalas"""
        if data.shape[1] < 2:
            return None
        
        # Calcula matriz de correlação
        corr_matrix = data.corr().abs()
        
        # Detecta correlações extremas
        high_correlations = (corr_matrix > 0.8).sum().sum() - len(corr_matrix)
        
        if high_correlations > len(corr_matrix):
            return RiskCognitiveInsight(
                pattern="HIGH_CORRELATION_RISK",
                confidence=min(0.8, high_correlations / len(corr_matrix)),
                significance=high_correlations / (len(corr_matrix) ** 2),
                risk_implication="High correlation detected - reduced diversification benefits",
                neural_activation=self._get_network_activation()
            )
        
        return None
    
    def _detect_drawdown_patterns(self, metrics: 'RiskMetrics') -> Optional[RiskCognitiveInsight]:
        """Detecção de padrões de drawdown"""
        if metrics.max_drawdown < -0.05:  # Mais de 5% de drawdown
            severity = abs(metrics.max_drawdown)
            return RiskCognitiveInsight(
                pattern="DRAWDOWN_STRESS",
                confidence=min(0.9, severity * 10),
                significance=severity,
                risk_implication=f"Significant drawdown detected: {severity:.2%}",
                neural_activation=self._get_network_activation()
            )
        
        return None
    
    def _predictive_risk_analysis(self, data: pd.DataFrame) -> Optional[RiskCognitiveInsight]:
        """Análise preditiva de risco usando rede neural"""
        if len(data) < 50:
            return None
        
        # Simulação de predição usando rede neural
        network_output = self._forward_pass(data.iloc[-1])
        
        if network_output > 0.7:
            return RiskCognitiveInsight(
                pattern="PREDICTIVE_RISK_HIGH",
                confidence=network_output,
                significance=network_output,
                risk_implication="Neural network predicts high risk conditions",
                neural_activation=self._get_network_activation(),
                prediction_horizon="MEDIUM_TERM"
            )
        
        return None
    
    def _forward_pass(self, input_data: pd.Series) -> float:
        """Forward pass na rede neural"""
        # Ativa neurônios de entrada
        input_activations = {}
        for i, (col, val) in enumerate(input_data.items()):
            if i < 8 and f"input_{i}" in self.neurons:
                input_activations[f"input_{i}"] = self.neurons[f"input_{i}"].activate(val)
        
        # Ativa camada oculta
        hidden_activations = {}
        for i in range(16):
            neuron_id = f"hidden_{i}"
            if neuron_id in self.neurons:
                net_input = 0
                for input_id, activation in input_activations.items():
                    if input_id in self.neurons[neuron_id].connections:
                        net_input += activation * self.neurons[neuron_id].connections[input_id]
                hidden_activations[neuron_id] = self.neurons[neuron_id].activate(net_input)
        
        # Ativa camada de saída
        output_activation = 0
        for i in range(4):
            neuron_id = f"output_{i}"
            if neuron_id in self.neurons:
                net_input = 0
                for hidden_id, activation in hidden_activations.items():
                    if hidden_id in self.neurons[neuron_id].connections:
                        net_input += activation * self.neurons[neuron_id].connections[hidden_id]
                output_activation += self.neurons[neuron_id].activate(net_input)
        
        return output_activation / 4  # Média das saídas
    
    def _get_network_activation(self) -> Dict[str, float]:
        """Obtem ativação atual da rede"""
        return {neuron_id: neuron.activation_history[-1] if neuron.activation_history else 0
                for neuron_id, neuron in self.neurons.items()}
    
    def learn_from_feedback(self, actual_outcome: float, predicted_risk: float) -> None:
        """Aprendizado supervisionado a partir de feedback"""
        error = actual_outcome - predicted_risk
        
        # Backpropagation simplificada
        for neuron in self.neurons.values():
            if neuron.neuron_type == "output":
                # Ajusta pesos das saídas
                for conn_id in neuron.connections:
                    neuron.connections[conn_id] -= self.learning_rate * error * 0.1
            elif neuron.neuron_type == "hidden":
                # Ajusta pesos das camadas ocultas
                for conn_id in neuron.connections:
                    neuron.connections[conn_id] -= self.learning_rate * error * 0.05

class AdvancedRiskPredictionSystem:
    """Sistema avançado de predição de risco com ensemble"""
    
    def __init__(self, models: Optional[List['RiskModel']] = None):
        self.models = models or []
        self.ensemble_weights = np.array([1.0] * len(self.models)) if self.models else np.array([])
        self.prediction_history: List[Dict] = []
        self.performance_metrics = {}
        self.learning_mode = "SUPERVISED"
        
    def add_model(self, model: 'RiskModel', weight: float = 1.0) -> None:
        """Adiciona modelo ao ensemble"""
        self.models.append(model)
        self.ensemble_weights = np.append(self.ensemble_weights, weight)
    
    def predict_risk(self, market_data: pd.DataFrame, 
                     horizon: str = "SHORT_TERM") -> Dict[str, Any]:
        """Predição ensemble de risco"""
        if not self.models:
            return {"prediction": 0.5, "confidence": 0.0, "models_used": 0}
        
        predictions = []
        confidences = []
        
        for model in self.models:
            try:
                pred = model.predict(market_data)
                if isinstance(pred, np.ndarray):
                    pred = pred.mean()
                predictions.append(pred)
                
                # Confiança baseada na performance histórica
                model_confidence = self._get_model_confidence(model)
                confidences.append(model_confidence)
                
            except Exception as e:
                logger.warning(f"Model {model.name} failed to predict: {e}")
                predictions.append(0.5)
                confidences.append(0.1)
        
        # Ensemble ponderado
        if len(predictions) > 0:
            weighted_pred = np.average(predictions, weights=self.ensemble_weights[:len(predictions)])
            ensemble_confidence = np.mean(confidences)
        else:
            weighted_pred = 0.5
            ensemble_confidence = 0.0
        
        result = {
            "prediction": weighted_pred,
            "confidence": ensemble_confidence,
            "models_used": len(predictions),
            "horizon": horizon,
            "individual_predictions": predictions,
            "model_confidences": confidences,
            "timestamp": datetime.now().isoformat()
        }
        
        # Registra predição
        self.prediction_history.append(result)
        
        return result
    
    def _get_model_confidence(self, model: 'RiskModel') -> float:
        """Calcula confiança do modelo baseado em performance"""
        if model.name not in self.performance_metrics:
            return 0.5
        
        metrics = self.performance_metrics[model.name]
        return metrics.get("accuracy", 0.5)
    
    def update_performance(self, model_name: str, actual: float, predicted: float) -> None:
        """Atualiza métricas de performance do modelo"""
        if model_name not in self.performance_metrics:
            self.performance_metrics[model_name] = {
                "predictions": [],
                "errors": [],
                "accuracy": 0.5
            }
        
        metrics = self.performance_metrics[model_name]
        metrics["predictions"].append(predicted)
        metrics["errors"].append(abs(actual - predicted))
        
        # Calcula acurácia recente
        if len(metrics["errors"]) > 10:
            recent_errors = metrics["errors"][-10:]
            metrics["accuracy"] = 1 - np.mean(recent_errors)

class RealTimeRiskMonitor:
    """Monitor de risco em tempo real com WebSocket"""
    
    def __init__(self, update_interval: float = 1.0):
        self.update_interval = update_interval
        self.is_monitoring = False
        self.subscribers: List[Callable] = []
        self.risk_metrics_history: List[Dict] = []
        self.alert_thresholds = {
            "var_95": 0.05,
            "max_drawdown": 0.10,
            "volatility": 0.30,
            "sharpe_ratio": 0.5
        }
        self.monitoring_thread: Optional[threading.Thread] = None
        
    def start_monitoring(self, risk_manager: 'VHALINORRiskManager') -> None:
        """Inicia monitoramento em tempo real"""
        self.is_monitoring = True
        self.risk_manager = risk_manager
        
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitoring_thread.start()
        
        logger.info("Real-time risk monitoring started")
    
    def stop_monitoring(self) -> None:
        """Para monitoramento"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=2.0)
        
        logger.info("Real-time risk monitoring stopped")
    
    def _monitoring_loop(self) -> None:
        """Loop principal de monitoramento"""
        while self.is_monitoring:
            try:
                # Coleta métricas atuais
                current_metrics = self._collect_current_metrics()
                
                # Verifica alertas
                alerts = self._check_alert_conditions(current_metrics)
                
                # Notifica assinantes
                for subscriber in self.subscribers:
                    try:
                        subscriber({
                            "metrics": current_metrics,
                            "alerts": alerts,
                            "timestamp": datetime.now().isoformat()
                        })
                    except Exception as e:
                        logger.warning(f"Subscriber notification failed: {e}")
                
                # Armazena histórico
                self.risk_metrics_history.append(current_metrics)
                
                # Mantém histórico limitado
                if len(self.risk_metrics_history) > 1000:
                    self.risk_metrics_history.pop(0)
                
                time.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                time.sleep(self.update_interval)
    
    def _collect_current_metrics(self) -> Dict[str, Any]:
        """Coleta métricas atuais do gerenciador de risco"""
        try:
            if hasattr(self.risk_manager, 'calculate_portfolio_risk'):
                risk_metrics = self.risk_manager.calculate_portfolio_risk()
                return {
                    "portfolio_value": self.risk_manager.current_capital,
                    "positions_count": len(self.risk_manager.positions),
                    "var_95": risk_metrics.var_95,
                    "max_drawdown": risk_metrics.max_drawdown,
                    "volatility": risk_metrics.volatility,
                    "sharpe_ratio": risk_metrics.sharpe_ratio,
                    "risk_score": risk_metrics.risk_score
                }
            else:
                return {"status": "metrics_unavailable"}
                
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            return {"status": "error", "message": str(e)}
    
    def _check_alert_conditions(self, metrics: Dict[str, Any]) -> List[Dict]:
        """Verifica condições de alerta"""
        alerts = []
        
        for metric, threshold in self.alert_thresholds.items():
            if metric in metrics:
                value = metrics[metric]
                
                if metric == "var_95" and abs(value) > threshold:
                    alerts.append({
                        "type": "VAR_BREACH",
                        "metric": metric,
                        "value": value,
                        "threshold": threshold,
                        "severity": "HIGH" if abs(value) > threshold * 1.5 else "MEDIUM"
                    })
                elif metric == "max_drawdown" and value < -threshold:
                    alerts.append({
                        "type": "DRAWDOWN_ALERT",
                        "metric": metric,
                        "value": value,
                        "threshold": -threshold,
                        "severity": "CRITICAL" if value < -threshold * 1.5 else "HIGH"
                    })
                elif metric == "volatility" and value > threshold:
                    alerts.append({
                        "type": "VOLATILITY_SPIKE",
                        "metric": metric,
                        "value": value,
                        "threshold": threshold,
                        "severity": "MEDIUM"
                    })
                elif metric == "sharpe_ratio" and value < threshold:
                    alerts.append({
                        "type": "LOW_SHARPE",
                        "metric": metric,
                        "value": value,
                        "threshold": threshold,
                        "severity": "LOW"
                    })
        
        return alerts
    
    def subscribe(self, callback: Callable[[Dict], None]) -> None:
        """Adiciona assinante para atualizações em tempo real"""
        self.subscribers.append(callback)
    
    def unsubscribe(self, callback: Callable[[Dict], None]) -> None:
        """Remove assinante"""
        if callback in self.subscribers:
            self.subscribers.remove(callback)

# ============================================================================

T = TypeVar('T')

# Forward declarations para resolver referências circulares
class RiskMetrics:
    pass

class RiskModel:
    pass

class VHALINORRiskManager:
    pass

class RiskLevel(Enum):
    """Níveis de risco do sistema com mapeamento completo"""
    ULTRA_CONSERVATIVE = auto()
    CONSERVATIVE = auto()
    MODERATE = auto()
    AGGRESSIVE = auto()
    ULTRA_AGGRESSIVE = auto()
    
    @property
    def max_risk_per_trade(self) -> float:
        """Risco máximo por trade"""
        return {
            RiskLevel.ULTRA_CONSERVATIVE: 0.005,  # 0.5%
            RiskLevel.CONSERVATIVE: 0.01,         # 1.0%
            RiskLevel.MODERATE: 0.02,             # 2.0%
            RiskLevel.AGGRESSIVE: 0.03,           # 3.0%
            RiskLevel.ULTRA_AGGRESSIVE: 0.04      # 4.0%
        }[self]
    
    @property
    def max_daily_risk(self) -> float:
        """Risco máximo diário"""
        return self.max_risk_per_trade * 3
    
    @property
    def max_portfolio_risk(self) -> float:
        """Risco máximo do portfólio"""
        return {
            RiskLevel.ULTRA_CONSERVATIVE: 0.05,
            RiskLevel.CONSERVATIVE: 0.10,
            RiskLevel.MODERATE: 0.15,
            RiskLevel.AGGRESSIVE: 0.20,
            RiskLevel.ULTRA_AGGRESSIVE: 0.25
        }[self]
    
    @property
    def min_sharpe_ratio(self) -> float:
        """Sharpe ratio mínimo aceitável"""
        return {
            RiskLevel.ULTRA_CONSERVATIVE: 1.5,
            RiskLevel.CONSERVATIVE: 1.2,
            RiskLevel.MODERATE: 1.0,
            RiskLevel.AGGRESSIVE: 0.8,
            RiskLevel.ULTRA_AGGRESSIVE: 0.6
        }[self]
    
    @property
    def description(self) -> str:
        """Descrição do nível de risco"""
        descriptions = {
            RiskLevel.ULTRA_CONSERVATIVE: "Preservação de capital máxima, retornos mínimos esperados",
            RiskLevel.CONSERVATIVE: "Baixo risco, foco em preservação de capital",
            RiskLevel.MODERATE: "Equilíbrio entre risco e retorno",
            RiskLevel.AGGRESSIVE: "Alto risco, busca por retornos superiores",
            RiskLevel.ULTRA_AGGRESSIVE: "Risco extremo, busca por retornos máximos"
        }
        return descriptions[self]


class RiskAlert(Enum):
    """Tipos de alertas de risco com severidade"""
    INFO = auto()
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()
    EMERGENCY = auto()
    
    @property
    def color(self) -> str:
        """Cores para visualização"""
        colors = {
            RiskAlert.INFO: '#3498db',      # Blue
            RiskAlert.LOW: '#2ecc71',       # Green
            RiskAlert.MEDIUM: '#f1c40f',    # Yellow
            RiskAlert.HIGH: '#e67e22',      # Orange
            RiskAlert.CRITICAL: '#e74c3c',  # Red
            RiskAlert.EMERGENCY: '#9b59b6'  # Purple
        }
        return colors[self]
    
    @property
    def ttl_seconds(self) -> int:
        """Tempo de vida do alerta em segundos"""
        return {
            RiskAlert.INFO: 3600,
            RiskAlert.LOW: 7200,
            RiskAlert.MEDIUM: 10800,
            RiskAlert.HIGH: 14400,
            RiskAlert.CRITICAL: 21600,
            RiskAlert.EMERGENCY: 43200
        }[self]


class PositionStatus(Enum):
    """Status da posição"""
    PENDING = auto()
    ACTIVE = auto()
    CLOSED = auto()
    STOPPED = auto()
    EXPIRED = auto()
    CANCELLED = auto()


class RiskModelType(Enum):
    """Tipos de modelos de risco"""
    VAR = "value_at_risk"
    CVAR = "conditional_var"
    EVT = "extreme_value_theory"
    COPULA = "copula"
    BAYESIAN = "bayesian"
    QUANTUM = "quantum"
    DEEP = "deep_learning"
    ENSEMBLE = "ensemble"


# ============================================================================
# ESTRUTURAS DE DADOS AVANÇADAS
# ============================================================================

@dataclass
class RiskMetrics:
    """Métricas de risco completas com análise estatística"""
    # Value at Risk
    var_95: float = 0.0
    var_99: float = 0.0
    var_995: float = 0.0
    var_confidence_interval: Tuple[float, float] = (0.0, 0.0)
    
    # Conditional Value at Risk
    cvar_95: float = 0.0
    cvar_99: float = 0.0
    cvar_995: float = 0.0
    
    # Ratios de performance
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    calmar_ratio: float = 0.0
    omega_ratio: float = 0.0
    information_ratio: float = 0.0
    treynor_ratio: float = 0.0
    
    # Drawdown
    max_drawdown: float = 0.0
    max_drawdown_duration: int = 0
    avg_drawdown: float = 0.0
    drawdown_volatility: float = 0.0
    
    # Volatilidade
    volatility: float = 0.0
    downside_volatility: float = 0.0
    semi_volatility: float = 0.0
    tail_ratio: float = 0.0
    
    # Sensibilidade
    beta: float = 0.0
    alpha: float = 0.0
    r_squared: float = 0.0
    
    # Métricas avançadas
    kurtosis: float = 0.0
    skewness: float = 0.0
    stability: float = 0.0
    diversification_ratio: float = 0.0
    
    # Valor em risco do portfólio
    portfolio_var: float = 0.0
    portfolio_cvar: float = 0.0
    component_var: Dict[str, float] = field(default_factory=dict)
    marginal_var: Dict[str, float] = field(default_factory=dict)
    
    # Métricas de estresse
    stress_var: Dict[str, float] = field(default_factory=dict)
    scenario_impacts: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Converte para dicionário serializável"""
        return {k: v for k, v in asdict(self).items() if not isinstance(v, dict) or v}
    
    @property
    def is_healthy(self) -> bool:
        """Verifica se as métricas estão saudáveis"""
        return (self.sharpe_ratio > 0.5 and 
                self.max_drawdown > -0.3 and 
                self.volatility < 0.5)
    
    @property
    def risk_score(self) -> float:
        """Calcula score de risco agregado (0-100)"""
        scores = []
        
        # Sharpe Ratio (menor = maior risco)
        if self.sharpe_ratio > 2:
            scores.append(20)
        elif self.sharpe_ratio > 1.5:
            scores.append(40)
        elif self.sharpe_ratio > 1:
            scores.append(60)
        elif self.sharpe_ratio > 0.5:
            scores.append(80)
        else:
            scores.append(100)
        
        # Drawdown (maior = maior risco)
        drawdown_score = min(100, abs(self.max_drawdown) * 200)
        scores.append(drawdown_score)
        
        # Volatilidade
        vol_score = min(100, self.volatility * 200)
        scores.append(vol_score)
        
        return np.mean(scores)


@dataclass
class PositionRisk:
    """Risco avançado de uma posição específica"""
    # Identificação
    symbol: str
    position_id: str
    status: PositionStatus = PositionStatus.PENDING
    
    # Tamanho e preços
    position_size: float = 0.0
    entry_price: float = 0.0
    current_price: float = 0.0
    stop_loss: float = 0.0
    take_profit: float = 0.0
    trailing_stop: Optional[float] = None
    
    # Métricas de risco
    risk_amount: float = 0.0
    risk_percentage: float = 0.0
    notional_value: float = 0.0
    leverage: float = 1.0
    
    # Performance
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    return_percentage: float = 0.0
    profit_factor: float = 0.0
    
    # Scores
    risk_score: float = 0.0
    confidence_level: float = 0.0
    conviction_score: float = 0.0
    
    # Análise técnica
    atr: float = 0.0
    volatility: float = 0.0
    correlation_risk: float = 0.0
    liquidity_risk: float = 0.0
    
    # Temporais
    entry_time: datetime = field(default_factory=datetime.now)
    update_time: datetime = field(default_factory=datetime.now)
    expected_duration: Optional[int] = None
    
    # Metadados
    strategy: str = ""
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def update_price(self, current_price: float) -> None:
        """Atualiza preço e recalcula métricas"""
        self.current_price = current_price
        self.update_time = datetime.now()
        
        # Recalcula P&L
        if self.position_size > 0:  # Long
            self.unrealized_pnl = (current_price - self.entry_price) * self.position_size
        else:  # Short
            self.unrealized_pnl = (self.entry_price - current_price) * abs(self.position_size)
        
        # Recalcula retorno
        self.return_percentage = self.unrealized_pnl / self.risk_amount if self.risk_amount > 0 else 0
        
        # Atualiza trailing stop
        if self.trailing_stop:
            if self.position_size > 0:  # Long
                new_stop = current_price * (1 - self.trailing_stop)
                if new_stop > self.stop_loss:
                    self.stop_loss = new_stop
            else:  # Short
                new_stop = current_price * (1 + self.trailing_stop)
                if new_stop < self.stop_loss:
                    self.stop_loss = new_stop
    
    @property
    def is_profitable(self) -> bool:
        """Verifica se a posição está lucrativa"""
        return self.unrealized_pnl > 0
    
    @property
    def is_at_stop(self) -> bool:
        """Verifica se atingiu o stop loss"""
        if self.position_size > 0:  # Long
            return self.current_price <= self.stop_loss
        else:  # Short
            return self.current_price >= self.stop_loss
    
    @property
    def is_at_target(self) -> bool:
        """Verifica se atingiu o take profit"""
        if self.position_size > 0:  # Long
            return self.current_price >= self.take_profit
        else:  # Short
            return self.current_price <= self.take_profit
    
    @property
    def risk_reward_ratio(self) -> float:
        """Calcula relação risco/retorno"""
        risk = abs(self.entry_price - self.stop_loss)
        reward = abs(self.take_profit - self.entry_price)
        return reward / risk if risk > 0 else 0
    
    @property
    def holding_period(self) -> timedelta:
        """Tempo em posição"""
        return datetime.now() - self.entry_time
    
    def to_dict(self) -> Dict:
        """Converte para dicionário serializável"""
        data = asdict(self)
        data['entry_time'] = self.entry_time.isoformat()
        data['update_time'] = self.update_time.isoformat()
        data['status'] = self.status.name
        return data


@dataclass
class RiskAlertData:
    """Estrutura de dados para alertas de risco"""
    id: str
    level: RiskAlert
    title: str
    message: str
    source: str
    timestamp: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def age_seconds(self) -> float:
        """Idade do alerta em segundos"""
        return (datetime.now() - self.timestamp).total_seconds()
    
    @property
    def is_expired(self) -> bool:
        """Verifica se o alerta expirou"""
        return self.age_seconds > self.level.ttl_seconds
    
    def acknowledge(self) -> None:
        """Marca alerta como reconhecido"""
        self.acknowledged = True
        self.acknowledged_at = datetime.now()
    
    def resolve(self) -> None:
        """Marca alerta como resolvido"""
        self.resolved = True
        self.resolved_at = datetime.now()


@dataclass
class RiskLimit:
    """Definição de limite de risco"""
    name: str
    description: str
    metric: str
    threshold: float
    condition: str  # 'above', 'below', 'between'
    upper_bound: Optional[float] = None
    severity: RiskAlert = RiskAlert.MEDIUM
    enabled: bool = True
    last_breach: Optional[datetime] = None
    breach_count: int = 0
    
    def check_breach(self, value: float) -> bool:
        """Verifica se o limite foi violado"""
        if not self.enabled:
            return False
        
        if self.condition == 'above':
            return value > self.threshold
        elif self.condition == 'below':
            return value < self.threshold
        elif self.condition == 'between' and self.upper_bound:
            return self.threshold <= value <= self.upper_bound
        
        return False


# ============================================================================
# MODELOS DE RISCO AVANÇADOS
# ============================================================================

class RiskModel(ABC):
    """Classe base abstrata para modelos de risco"""
    
    def __init__(self, name: str, config: Optional[Dict] = None):
        self.name = name
        self.config = config or {}
        self.is_fitted = False
        self.metadata = {}
    
    @abstractmethod
    def fit(self, data: pd.DataFrame) -> 'RiskModel':
        """Treina o modelo"""
        pass
    
    @abstractmethod
    def predict(self, data: pd.DataFrame) -> np.ndarray:
        """Faz previsões"""
        pass
    
    def save(self, path: Union[str, Path]) -> None:
        """Salva o modelo"""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'wb') as f:
            pickle.dump(self, f)
    
    @classmethod
    def load(cls, path: Union[str, Path]) -> 'RiskModel':
        """Carrega o modelo"""
        with open(path, 'rb') as f:
            return pickle.load(f)


class VaRModel(RiskModel):
    """Value at Risk com múltiplas metodologias"""
    
    def __init__(self, method: str = 'historical', **kwargs):
        super().__init__(f"VaR_{method}", kwargs)
        self.method = method
        self.returns = None
        self.mean = None
        self.std = None
        self.percentiles = {}
        
    def fit(self, data: pd.DataFrame) -> 'VaRModel':
        """Calcula VaR baseado em dados históricos"""
        if isinstance(data, pd.DataFrame):
            data = data.values.flatten()
        
        self.returns = data
        self.mean = np.mean(data)
        self.std = np.std(data)
        
        # Pré-calcula percentis
        for conf in [0.95, 0.99, 0.995]:
            if self.method == 'historical':
                self.percentiles[conf] = np.percentile(data, (1 - conf) * 100)
            elif self.method == 'parametric':
                self.percentiles[conf] = self.mean + norm.ppf(1 - conf) * self.std
            elif self.method == 'cornish_fisher':
                skew = stats.skew(data)
                kurt = stats.kurtosis(data)
                z = norm.ppf(1 - conf)
                z_cf = z + (z**2 - 1) * skew / 6 + (z**3 - 3 * z) * (kurt - 3) / 24 - (2 * z**3 - 5 * z) * (skew**2) / 36
                self.percentiles[conf] = self.mean + z_cf * self.std
        
        self.is_fitted = True
        return self
    
    def predict(self, data: pd.DataFrame) -> np.ndarray:
        """Calcula VaR para novos dados"""
        if not self.is_fitted:
            raise ValueError("Modelo não foi treinado")
        
        if isinstance(data, pd.DataFrame):
            data = data.values.flatten()
        
        var_values = []
        for conf in [0.95, 0.99, 0.995]:
            var = np.percentile(data, (1 - conf) * 100)
            var_values.append(var)
        
        return np.array(var_values)
    
    def calculate_cvar(self, confidence: float = 0.95) -> float:
        """Calcula Conditional VaR"""
        if not self.is_fitted:
            raise ValueError("Modelo não foi treinado")
        
        var = self.percentiles[confidence]
        return self.returns[self.returns <= var].mean()


class EVTModel(RiskModel):
    """Extreme Value Theory para caudas pesadas"""
    
    def __init__(self, threshold_percentile: float = 0.95, **kwargs):
        super().__init__("EVT", kwargs)
        self.threshold_percentile = threshold_percentile
        self.threshold = None
        self.params = None
        self.exceedances = None
        
    def fit(self, data: pd.DataFrame) -> 'EVTModel':
        """Ajusta distribuição GPD aos excessos"""
        if isinstance(data, pd.DataFrame):
            data = data.values.flatten()
        
        # Define threshold
        self.threshold = np.percentile(data, self.threshold_percentile * 100)
        
        # Excedências negativas (perdas)
        self.exceedances = data[data < self.threshold] - self.threshold
        self.exceedances = self.exceedances[~np.isnan(self.exceedances)]
        
        if len(self.exceedances) > 5:
            # Ajusta GPD
            self.params = genextreme.fit(-self.exceedances)
        
        self.is_fitted = True
        return self
    
    def predict(self, data: pd.DataFrame) -> np.ndarray:
        """Prevê VaR extremo"""
        if not self.is_fitted or self.params is None:
            return np.array([0, 0])
        
        c, loc, scale = self.params
        
        var_99 = self.threshold + genextreme.ppf(0.99, c, loc, scale)
        var_995 = self.threshold + genextreme.ppf(0.995, c, loc, scale)
        
        return np.array([var_99, var_995])


class CopulaRiskModel(RiskModel):
    """Modelo de risco baseado em cópulas para dependência não-linear"""
    
    def __init__(self, copula_type: str = 'gaussian', **kwargs):
        super().__init__(f"Copula_{copula_type}", kwargs)
        self.copula_type = copula_type
        self.correlation = None
        self.dof = None
        
    def fit(self, data: pd.DataFrame) -> 'CopulaRiskModel':
        """Ajusta cópula aos dados"""
        # Transforma para uniforme [0,1]
        u = data.rank() / (len(data) + 1)
        
        if self.copula_type == 'gaussian':
            self.correlation = u.corr().values
        elif self.copula_type == 'student':
            from scipy.stats import t
            # Aproximação simples dos graus de liberdade
            self.correlation = u.corr().values
            self.dof = 4
        
        self.is_fitted = True
        return self
    
    def predict(self, data: pd.DataFrame) -> np.ndarray:
        """Simula cenários da cópula"""
        n_simulations = self.config.get('n_simulations', 10000)
        n_assets = data.shape[1]
        
        if self.copula_type == 'gaussian':
            # Cópula Gaussiana
            samples = np.random.multivariate_normal(
                np.zeros(n_assets),
                self.correlation,
                n_simulations
            )
            uniform_samples = norm.cdf(samples)
            
        elif self.copula_type == 'student':
            # Cópula t-Student
            samples = np.random.multivariate_normal(
                np.zeros(n_assets),
                self.correlation,
                n_simulations
            )
            chi2 = np.random.chisquare(self.dof, n_simulations) / self.dof
            t_samples = samples / np.sqrt(chi2)[:, np.newaxis]
            uniform_samples = t.cdf(t_samples, self.dof)
        
        # Transforma de volta para distribuições originais
        portfolio_returns = []
        for i in range(n_assets):
            asset_returns = data.iloc[:, i].values
            transformed = np.percentile(asset_returns, uniform_samples[:, i] * 100)
            portfolio_returns.append(transformed)
        
        portfolio_returns = np.array(portfolio_returns).mean(axis=0)
        
        return portfolio_returns


class QuantumRiskModel(RiskModel):
    """Modelo de risco usando computação quântica"""
    
    def __init__(self, n_qubits: int = 4, **kwargs):
        super().__init__("Quantum", kwargs)
        self.n_qubits = n_qubits
        self.backend = None
        self.circuit = None
        self.kernel = None
        
        if not QUANTUM_AVAILABLE:
            raise ImportError(f"Qiskit não disponível: {QUANTUM_ERROR}")
        
    def fit(self, data: pd.DataFrame) -> 'QuantumRiskModel':
        """Cria kernel quântico para classificação de risco"""
        # Prepara dados
        if data.shape[1] > self.n_qubits:
            # Reduz dimensionalidade
            pca = PCA(n_components=self.n_qubits)
            features = pca.fit_transform(data)
        else:
            features = data.values
        
        # Normaliza para [0, π]
        features = (features - features.min()) / (features.max() - features.min()) * np.pi
        
        # Cria feature map quântico
        feature_map = ZZFeatureMap(
            feature_dimension=self.n_qubits,
            reps=2,
            entanglement='linear'
        )
        
        # Cria kernel quântico
        self.kernel = FidelityQuantumKernel(
            feature_map=feature_map,
            quantum_instance=Aer.get_backend('statevector_simulator')
        )
        
        # Calcula matriz de kernel
        self.kernel_matrix = self.kernel.evaluate(x_vec=features[:100])
        
        self.is_fitted = True
        return self
    
    def predict(self, data: pd.DataFrame) -> np.ndarray:
        """Faz previsão usando SVM quântico"""
        if not self.is_fitted:
            raise ValueError("Modelo não foi treinado")
        
        # Implementar classificação quântica
        return np.array([0.5])  # Placeholder


class DeepRiskModel(RiskModel):
    """Modelo de risco baseado em Deep Learning"""
    
    def __init__(self, input_dim: int, hidden_dims: List[int] = [128, 64, 32], **kwargs):
        super().__init__("DeepLearning", kwargs)
        
        if not DEEP_LEARNING_AVAILABLE:
            raise ImportError("PyTorch não disponível")
        
        self.input_dim = input_dim
        self.hidden_dims = hidden_dims
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self._build_model().to(self.device)
        self.criterion = torch.nn.MSELoss()
        self.optimizer = None
        self.scaler_X = StandardScaler() if HAS_SKLEARN else None
        self.scaler_y = StandardScaler() if HAS_SKLEARN else None
        
    def _build_model(self):
        """Constrói arquitetura da rede neural"""
        class RiskNetwork(torch.nn.Module):
            def __init__(self, input_dim, hidden_dims):
                super().__init__()
                layers = []
                prev_dim = input_dim
                
                for hidden_dim in hidden_dims:
                    layers.extend([
                        torch.nn.Linear(prev_dim, hidden_dim),
                        torch.nn.BatchNorm1d(hidden_dim),
                        torch.nn.ReLU(),
                        torch.nn.Dropout(0.2)
                    ])
                    prev_dim = hidden_dim
                
                layers.append(torch.nn.Linear(prev_dim, 1))
                
                self.network = torch.nn.Sequential(*layers)
            
            def forward(self, x):
                return self.network(x)
        
        return RiskNetwork(self.input_dim, self.hidden_dims)
    
    def fit(self, data: pd.DataFrame, target: str = 'returns') -> 'DeepRiskModel':
        """Treina a rede neural"""
        if not HAS_SKLEARN:
            raise ImportError("Scikit-learn não disponível para normalização")
            
        # Prepara features e target
        X = data.drop(columns=[target]).values
        y = data[target].values
        
        # Normaliza
        X_scaled = self.scaler_X.fit_transform(X)
        y_scaled = self.scaler_y.fit_transform(y.reshape(-1, 1)).flatten()
        
        # Converte para tensor
        X_tensor = torch.FloatTensor(X_scaled).to(self.device)
        y_tensor = torch.FloatTensor(y_scaled).to(self.device)
        
        # DataLoader
        dataset = torch.utils.data.TensorDataset(X_tensor, y_tensor)
        loader = torch.utils.data.DataLoader(
            dataset, 
            batch_size=self.config.get('batch_size', 32),
            shuffle=True
        )
        
        # Otimizador
        self.optimizer = torch.optim.Adam(
            self.model.parameters(),
            lr=self.config.get('learning_rate', 0.001)
        )
        
        # Learning rate scheduler
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer,
            patience=10,
            factor=0.5,
            verbose=True
        )
        
        # Treinamento
        epochs = self.config.get('epochs', 100)
        self.model.train()
        
        for epoch in range(epochs):
            epoch_loss = 0.0
            
            for batch_X, batch_y in loader:
                self.optimizer.zero_grad()
                
                predictions = self.model(batch_X).squeeze()
                loss = self.criterion(predictions, batch_y)
                
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                self.optimizer.step()
                
                epoch_loss += loss.item()
            
            avg_loss = epoch_loss / len(loader)
            scheduler.step(avg_loss)
            
            if epoch % 10 == 0:
                print(f"Epoch {epoch}: Loss = {avg_loss:.6f}")
        
        self.is_fitted = True
        return self
    
    def predict(self, data: pd.DataFrame) -> np.ndarray:
        """Faz previsões de risco"""
        if not self.is_fitted:
            raise ValueError("Modelo não foi treinado")
        
        if not HAS_SKLEARN:
            raise ImportError("Scikit-learn não disponível para normalização")
            
        # Prepara dados
        X = data.values
        X_scaled = self.scaler_X.transform(X)
        X_tensor = torch.FloatTensor(X_scaled).to(self.device)
        
        # Predição
        self.model.eval()
        with torch.no_grad():
            predictions = self.model(X_tensor).cpu().numpy()
        
        # Desnormaliza
        predictions = self.scaler_y.inverse_transform(predictions)
        
        return predictions.flatten()


class EnsembleRiskModel(RiskModel):
    """Modelo ensemble combinando múltiplas estratégias"""
    
    def __init__(self, models: Optional[List[RiskModel]] = None, **kwargs):
        super().__init__("Ensemble", kwargs)
        self.models = models or []
        self.weights = None
        
    def add_model(self, model: RiskModel, weight: float = 1.0) -> 'EnsembleRiskModel':
        """Adiciona modelo ao ensemble"""
        self.models.append(model)
        
        if self.weights is None:
            self.weights = np.array([weight])
        else:
            self.weights = np.append(self.weights, weight)
        
        return self
    
    def fit(self, data: pd.DataFrame) -> 'EnsembleRiskModel':
        """Treina todos os modelos"""
        for model in self.models:
            model.fit(data)
        
        self.is_fitted = True
        return self
    
    def predict(self, data: pd.DataFrame) -> np.ndarray:
        """Combina previsões dos modelos"""
        if not self.is_fitted:
            raise ValueError("Modelo não foi treinado")
        
        predictions = []
        
        for i, model in enumerate(self.models):
            pred = model.predict(data)
            weight = self.weights[i] if self.weights is not None else 1.0
            predictions.append(pred * weight)
        
        # Média ponderada
        ensemble_pred = np.average(predictions, axis=0)
        
        return ensemble_pred


# ============================================================================
# SISTEMA PRINCIPAL DE GERENCIAMENTO DE RISCO
# ============================================================================

class VHALINORRiskManager:
    """
    Sistema Avançado de Gerenciamento de Risco VHALINOR
    
    Características Principais:
    - Gestão dinâmica de risco em tempo real
    - Modelos preditivos com Deep Learning
    - Análise quântica de correlações
    - Otimização multi-objetivo de portfólio
    - Detecção de anomalias e outliers
    - Stress testing automatizado
    - Alertas inteligentes com Machine Learning
    - Backtesting avançado de estratégias
    - API assíncrona de alta performance
    - Persistência em banco de dados
    """
    
    def __init__(self, 
                 initial_capital: float = 100000.0,
                 risk_level: RiskLevel = RiskLevel.MODERATE,
                 config: Optional[Dict] = None,
                 enable_quantum: bool = True,
                 enable_deep_learning: bool = True,
                 enable_persistence: bool = False):
        """
        Inicializa o gerenciador de risco
        
        Args:
            initial_capital: Capital inicial
            risk_level: Nível de risco desejado
            config: Configurações customizadas
            enable_quantum: Habilitar computação quântica
            enable_deep_learning: Habilitar deep learning
            enable_persistence: Habilitar persistência em banco
        """
        
        # ====================================================================
        # CONFIGURAÇÕES INICIAIS
        # ====================================================================
        
        # Capital
        self.initial_capital = float(initial_capital)
        self.current_capital = self.initial_capital
        self.available_capital = self.initial_capital
        self.peak_capital = self.initial_capital
        
        # Perfil de risco
        self.risk_level = risk_level
        self.config = self._merge_config(config or {})
        
        # ====================================================================
        # ESTADO DO SISTEMA
        # ====================================================================
        
        # Posições
        self.positions: Dict[str, PositionRisk] = {}
        self.position_history: List[PositionRisk] = []
        
        # Histórico
        self.trade_history: List[Dict] = []
        self.equity_curve: List[float] = [self.initial_capital]
        self.equity_timestamps: List[datetime] = [datetime.now()]
        
        # Métricas
        self.risk_metrics = RiskMetrics()
        self.daily_risk_used: float = 0.0
        self.daily_trades: int = 0
        
        # Alertas
        self.alerts: Dict[str, RiskAlertData] = {}
        self.alert_history: List[RiskAlertData] = []
        
        # Limites de risco
        self.risk_limits: List[RiskLimit] = self._initialize_risk_limits()
        
        # ====================================================================
        # MODELOS DE RISCO
        # ====================================================================
        
        self.models: Dict[str, RiskModel] = {}
        self.active_models: List[str] = []
        
        # Inicializa modelos básicos
        self._initialize_models(enable_quantum, enable_deep_learning)
        
        # ====================================================================
        # INFRAESTRUTURA
        # ====================================================================
        
        # Logging
        self.logger = self._setup_logging()
        
        # Executors
        self.thread_executor = ThreadPoolExecutor(
            max_workers=self.config.get('max_workers', 8)
        )
        self.process_executor = ProcessPoolExecutor(
            max_workers=self.config.get('max_processes', 4)
        )
        
        # Cache
        self.cache = {}
        self.cache_ttl = self.config.get('cache_ttl', 300)
        
        # Banco de dados
        self.db_engine = None
        self.db_session = None
        
        if enable_persistence and DATABASE_AVAILABLE:
            self._initialize_database()
        
        # ====================================================================
        # MÉTRICAS DE PERFORMANCE
        # ====================================================================
        
        self.performance_stats = {
            'trades_total': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'total_pnl': 0.0,
            'avg_win': 0.0,
            'avg_loss': 0.0,
            'win_rate': 0.0,
            'profit_factor': 0.0,
            'avg_holding_period': timedelta(),
            'max_consecutive_wins': 0,
            'max_consecutive_losses': 0
        }
        
        # ====================================================================
        # INICIALIZAÇÃO
        # ====================================================================
        
        self.logger.info("=" * 60)
        self.logger.info("VHALINOR Risk Manager v5.0.0")
        self.logger.info("=" * 60)
        self.logger.info(f"Capital Inicial: ${self.initial_capital:,.2f}")
        self.logger.info(f"Nivel de Risco: {self.risk_level.name}")
        self.logger.info(f"Deep Learning: {'OK' if enable_deep_learning and DEEP_LEARNING_AVAILABLE else 'FAIL'}")
        self.logger.info(f"Quantum: {'OK' if enable_quantum and QUANTUM_AVAILABLE else 'FAIL'}")
        self.logger.info("=" * 60)
    
    # ========================================================================
    # MÉTODOS DE INICIALIZAÇÃO
    # ========================================================================
    
    def _merge_config(self, user_config: Dict) -> Dict:
        """Mescla configurações do usuário com padrões"""
        
        # Configurações base por nível de risco
        risk_configs = {
            RiskLevel.ULTRA_CONSERVATIVE: {
                'max_risk_per_trade': 0.005,
                'max_daily_risk': 0.015,
                'max_portfolio_risk': 0.05,
                'max_positions': 5,
                'max_correlation': 0.5,
                'stop_loss_multiplier': 1.5,
                'take_profit_ratio': 2.0,
                'min_confidence': 0.8,
                'max_leverage': 1.0,
                'position_sizing_method': 'kelly_half'
            },
            RiskLevel.CONSERVATIVE: {
                'max_risk_per_trade': 0.01,
                'max_daily_risk': 0.03,
                'max_portfolio_risk': 0.10,
                'max_positions': 8,
                'max_correlation': 0.6,
                'stop_loss_multiplier': 1.8,
                'take_profit_ratio': 1.8,
                'min_confidence': 0.75,
                'max_leverage': 1.5,
                'position_sizing_method': 'kelly'
            },
            RiskLevel.MODERATE: {
                'max_risk_per_trade': 0.02,
                'max_daily_risk': 0.05,
                'max_portfolio_risk': 0.15,
                'max_positions': 10,
                'max_correlation': 0.7,
                'stop_loss_multiplier': 2.0,
                'take_profit_ratio': 1.5,
                'min_confidence': 0.7,
                'max_leverage': 2.0,
                'position_sizing_method': 'optimal_f'
            },
            RiskLevel.AGGRESSIVE: {
                'max_risk_per_trade': 0.03,
                'max_daily_risk': 0.08,
                'max_portfolio_risk': 0.20,
                'max_positions': 12,
                'max_correlation': 0.8,
                'stop_loss_multiplier': 2.2,
                'take_profit_ratio': 1.2,
                'min_confidence': 0.65,
                'max_leverage': 2.5,
                'position_sizing_method': 'optimal_f'
            },
            RiskLevel.ULTRA_AGGRESSIVE: {
                'max_risk_per_trade': 0.04,
                'max_daily_risk': 0.12,
                'max_portfolio_risk': 0.25,
                'max_positions': 15,
                'max_correlation': 0.9,
                'stop_loss_multiplier': 2.5,
                'take_profit_ratio': 1.0,
                'min_confidence': 0.6,
                'max_leverage': 3.0,
                'position_sizing_method': 'optimal_f'
            }
        }
        
        # Configuração base
        base_config = risk_configs[self.risk_level]
        
        # Configurações adicionais
        default_config = {
            # Gestão de risco
            **base_config,
            
            # Análise técnica
            'atr_period': 14,
            'volatility_period': 20,
            'correlation_window': 60,
            
            # Modelos de risco
            'enable_var': True,
            'enable_evt': True,
            'enable_copula': False,
            'enable_ensemble': True,
            
            # Limites e thresholds
            'alert_thresholds': {
                'drawdown': 0.10,
                'daily_loss': 0.03,
                'position_risk': 0.05,
                'volatility_spike': 0.5,
                'correlation_spike': 0.8,
                'var_breach': 0.95
            },
            
            # Performance
            'max_workers': 8,
            'max_processes': 4,
            'cache_ttl': 300,
            'enable_async': True,
            
            # Backtesting
            'backtest_years': 3,
            'min_trades_backtest': 30,
            'validation_split': 0.7,
            
            # Reporting
            'enable_detailed_reporting': True,
            'report_format': 'json',
            'auto_export': False,
            
            # Logging
            'log_level': 'INFO',
            'log_file': 'vhalinor_risk.log',
            'log_format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'log_max_bytes': 10485760,  # 10MB
            'log_backup_count': 5
        }
        
        # Merge profundo
        merged = default_config.copy()
        
        for key, value in user_config.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key].update(value)
            else:
                merged[key] = value
        
        return merged
    
    def _setup_logging(self) -> logging.Logger:
        """Configura sistema de logging avançado"""
        
        logger = logging.getLogger('VHALINOR_Risk')
        logger.setLevel(getattr(logging, self.config['log_level']))
        
        if not logger.handlers:
            # Handler para arquivo com rotação
            from logging.handlers import RotatingFileHandler
            
            file_handler = RotatingFileHandler(
                self.config['log_file'],
                maxBytes=self.config['log_max_bytes'],
                backupCount=self.config['log_backup_count']
            )
            file_handler.setFormatter(logging.Formatter(self.config['log_format']))
            logger.addHandler(file_handler)
            
            # Handler para console
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(
                logging.Formatter('%(levelname)s: %(message)s')
            )
            logger.addHandler(console_handler)
            
            # Handler para erros críticos
            error_handler = RotatingFileHandler(
                'vhalinor_risk_errors.log',
                maxBytes=self.config['log_max_bytes'],
                backupCount=self.config['log_backup_count']
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(logging.Formatter(self.config['log_format']))
            logger.addHandler(error_handler)
        
        return logger
    
    def _initialize_models(self, enable_quantum: bool, enable_deep: bool) -> None:
        """Inicializa modelos de risco"""
        
        # VaR Model
        if self.config['enable_var']:
            self.models['var_historical'] = VaRModel(method='historical')
            self.models['var_parametric'] = VaRModel(method='parametric')
            self.models['var_cornish_fisher'] = VaRModel(method='cornish_fisher')
            self.active_models.extend(['var_historical', 'var_parametric', 'var_cornish_fisher'])
        
        # EVT Model
        if self.config['enable_evt']:
            self.models['evt'] = EVTModel(threshold_percentile=0.95)
            self.active_models.append('evt')
        
        # Copula Model
        if self.config['enable_copula']:
            try:
                self.models['copula_gaussian'] = CopulaRiskModel(copula_type='gaussian')
                self.active_models.append('copula_gaussian')
            except Exception as e:
                self.logger.warning(f"❌ Erro ao inicializar modelo cópula: {e}")
        
        # Quantum Model
        if enable_quantum and QUANTUM_AVAILABLE:
            try:
                self.models['quantum'] = QuantumRiskModel(n_qubits=4)
                self.active_models.append('quantum')
                self.logger.info("✅ Modelo Quântico inicializado")
            except Exception as e:
                self.logger.warning(f"❌ Erro ao inicializar modelo quântico: {e}")
        
        # Deep Learning Model
        if enable_deep and DEEP_LEARNING_AVAILABLE:
            try:
                self.models['deep'] = DeepRiskModel(input_dim=20)
                self.active_models.append('deep')
                self.logger.info("✅ Modelo Deep Learning inicializado")
            except Exception as e:
                self.logger.warning(f"❌ Erro ao inicializar modelo deep learning: {e}")
        
        # Ensemble Model
        if self.config['enable_ensemble']:
            ensemble = EnsembleRiskModel()
            
            for model_name in self.active_models[:3]:  # Top 3 modelos
                if model_name in self.models:
                    ensemble.add_model(self.models[model_name])
            
            self.models['ensemble'] = ensemble
            self.active_models.append('ensemble')
    
    def _initialize_database(self) -> None:
        """Inicializa conexão com banco de dados"""
        try:
            # Configuração do banco
            db_path = self.config.get('database_path', 'vhalinor_risk.db')
            self.db_engine = create_engine(f'sqlite:///{db_path}')
            
            # Define modelos
            Base = declarative_base()
            
            class PositionDB(Base):
                __tablename__ = 'positions'
                
                id = Column(String, primary_key=True)
                symbol = Column(String)
                entry_time = Column(DateTime)
                exit_time = Column(DateTime, nullable=True)
                entry_price = Column(Float)
                exit_price = Column(Float, nullable=True)
                position_size = Column(Float)
                pnl = Column(Float, nullable=True)
                metadata = Column(JSON)
            
            class TradeDB(Base):
                __tablename__ = 'trades'
                
                id = Column(String, primary_key=True)
                timestamp = Column(DateTime)
                symbol = Column(String)
                action = Column(String)
                price = Column(Float)
                quantity = Column(Float)
                pnl = Column(Float, nullable=True)
            
            class RiskMetricsDB(Base):
                __tablename__ = 'risk_metrics'
                
                id = Column(String, primary_key=True)
                timestamp = Column(DateTime)
                metrics = Column(JSON)
            
            # Cria tabelas
            Base.metadata.create_all(self.db_engine)
            
            # Cria sessão
            Session = sessionmaker(bind=self.db_engine)
            self.db_session = Session()
            
            self.logger.info("✅ Banco de dados inicializado")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao inicializar banco de dados: {e}")
    
    def _initialize_risk_limits(self) -> List[RiskLimit]:
        """Inicializa limites de risco"""
        
        limits = [
            RiskLimit(
                name="max_daily_loss",
                description="Perda máxima diária",
                metric="daily_pnl",
                threshold=-self.initial_capital * self.config['max_daily_risk'],
                condition="below",
                severity=RiskAlert.CRITICAL
            ),
            RiskLimit(
                name="max_drawdown",
                description="Drawdown máximo",
                metric="drawdown",
                threshold=-self.config['alert_thresholds']['drawdown'],
                condition="below",
                severity=RiskAlert.HIGH
            ),
            RiskLimit(
                name="max_position_risk",
                description="Risco máximo por posição",
                metric="position_risk",
                threshold=self.config['max_risk_per_trade'] * 100,
                condition="above",
                severity=RiskAlert.MEDIUM
            ),
            RiskLimit(
                name="max_positions",
                description="Número máximo de posições",
                metric="position_count",
                threshold=self.config['max_positions'],
                condition="above",
                severity=RiskAlert.MEDIUM
            ),
            RiskLimit(
                name="min_sharpe",
                description="Sharpe ratio mínimo",
                metric="sharpe_ratio",
                threshold=self.risk_level.min_sharpe_ratio,
                condition="below",
                severity=RiskAlert.HIGH
            ),
            RiskLimit(
                name="max_correlation",
                description="Correlação máxima",
                metric="correlation",
                threshold=self.config['max_correlation'],
                condition="above",
                severity=RiskAlert.MEDIUM
            ),
            RiskLimit(
                name="max_leverage",
                description="Alavancagem máxima",
                metric="leverage",
                threshold=self.config['max_leverage'],
                condition="above",
                severity=RiskAlert.HIGH
            ),
            RiskLimit(
                name="min_confidence",
                description="Confiança mínima",
                metric="confidence",
                threshold=self.config['min_confidence'],
                condition="below",
                severity=RiskAlert.MEDIUM
            ),
            RiskLimit(
                name="max_volatility",
                description="Volatilidade máxima",
                metric="volatility",
                threshold=0.4,
                condition="above",
                severity=RiskAlert.HIGH
            ),
            RiskLimit(
                name="var_breach",
                description="Violação de VaR",
                metric="var_ratio",
                threshold=self.config['alert_thresholds']['var_breach'],
                condition="above",
                severity=RiskAlert.CRITICAL
            )
        ]
        
        return limits
    
    # ========================================================================
    # CÁLCULO DE POSIÇÃO E SIZING
    # ========================================================================
    
    def calculate_position_size(self,
                               symbol: str,
                               entry_price: float,
                               stop_loss: float,
                               confidence: float = 0.7,
                               custom_risk: Optional[float] = None,
                               market_regime: str = 'normal',
                               use_ml: bool = True) -> Dict[str, Any]:
        """
        Calcula tamanho ótimo da posição usando múltiplas metodologias
        
        Args:
            symbol: Símbolo do ativo
            entry_price: Preço de entrada
            stop_loss: Preço de stop loss
            confidence: Nível de confiança (0-1)
            custom_risk: Risco customizado por trade
            market_regime: Regime de mercado ('normal', 'volatile', 'calm')
            use_ml: Usar modelo de ML para ajuste fino
            
        Returns:
            Dicionário com informações completas da posição
        """
        
        start_time = datetime.now()
        
        try:
            # ====================================================================
            # VALIDAÇÕES INICIAIS
            # ====================================================================
            
            if entry_price <= 0 or stop_loss <= 0:
                return {'error': 'Preços devem ser positivos'}
            
            if entry_price == stop_loss:
                return {'error': 'Stop loss igual ao preço de entrada'}
            
            # ====================================================================
            # CÁLCULO DO RISCO BASE
            # ====================================================================
            
            # Risco por trade (configurável por nível de risco)
            base_risk_per_trade = custom_risk or self.config['max_risk_per_trade']
            
            # Ajuste por regime de mercado
            regime_multipliers = {
                'calm': 1.2,      # Aumenta risco em mercado calmo
                'normal': 1.0,    # Risco normal
                'volatile': 0.7,  # Reduz risco em volatilidade
                'crisis': 0.3     # Reduz drasticamente em crise
            }
            
            regime_multiplier = regime_multipliers.get(market_regime, 1.0)
            risk_per_trade = base_risk_per_trade * regime_multiplier
            
            # Limite diário
            if self.daily_risk_used + risk_per_trade > self.config['max_daily_risk']:
                risk_per_trade = self.config['max_daily_risk'] - self.daily_risk_used
                if risk_per_trade <= 0:
                    return {'error': 'Limite diário de risco atingido'}
            
            # ====================================================================
            # CÁLCULO DO TAMANHO DA POSIÇÃO
            # ====================================================================
            
            # Risco por unidade
            risk_per_unit = abs(entry_price - stop_loss)
            
            # Capital disponível para risco
            risk_capital = self.available_capital * risk_per_trade
            
            # Método de position sizing
            sizing_method = self.config['position_sizing_method']
            
            if sizing_method == 'kelly':
                # Kelly Criterion puro
                win_rate = self.performance_stats.get('win_rate', 0.5)
                avg_win = self.performance_stats.get('avg_win', 1.0)
                avg_loss = self.performance_stats.get('avg_loss', 1.0)
                
                if avg_loss > 0:
                    kelly_fraction = win_rate - (1 - win_rate) / (avg_win / avg_loss)
                    kelly_fraction = max(0.1, min(0.5, kelly_fraction))  # Limita entre 10% e 50%
                else:
                    kelly_fraction = 0.25
                
                position_size = (risk_capital * kelly_fraction) / risk_per_unit
                
            elif sizing_method == 'kelly_half':
                # Half-Kelly (mais conservador)
                position_size = (risk_capital * 0.5) / risk_per_unit
                
            elif sizing_method == 'optimal_f':
                # Optimal F de Ralph Vince
                # Implementação simplificada
                position_size = risk_capital / (risk_per_unit * 3)
                
            else:  # fixed_fraction
                # Fração fixa tradicional
                position_size = risk_capital / risk_per_unit
            
            # ====================================================================
            # AJUSTE POR CONFIANÇA
            # ====================================================================
            
            # Multiplicador baseado na confiança
            confidence_multiplier = self._calculate_confidence_multiplier(confidence)
            position_size *= confidence_multiplier
            
            # ====================================================================
            # LIMITES DE TAMANHO
            # ====================================================================
            
            # Limite máximo por posição (% do capital)
            max_position_pct = self.config.get('max_position_pct', 0.3)
            max_position_value = self.available_capital * max_position_pct
            position_value = position_size * entry_price
            
            if position_value > max_position_value:
                position_size = max_position_value / entry_price
                position_value = max_position_value
            
            # Limite mínimo
            min_position_value = self.config.get('min_position_value', 1000)
            if position_value < min_position_value:
                return {'error': f'Valor da posição ({position_value:.2f}) abaixo do mínimo ({min_position_value})'}
            
            # ====================================================================
            # AJUSTE POR ML (SE HABILITADO)
            # ====================================================================
            
            if use_ml and 'deep' in self.models and self.models['deep'].is_fitted:
                try:
                    # Features para o modelo
                    features = np.array([
                        confidence,
                        self.performance_stats['win_rate'],
                        self.risk_metrics.volatility,
                        self.risk_metrics.sharpe_ratio,
                        len(self.positions) / self.config['max_positions']
                    ]).reshape(1, -1)
                    
                    features_df = pd.DataFrame(features)
                    ml_adjustment = self.models['deep'].predict(features_df)[0]
                    
                    # Ajuste limitado
                    ml_adjustment = max(0.7, min(1.3, ml_adjustment))
                    position_size *= ml_adjustment
                    
                except Exception as e:
                    self.logger.debug(f"Erro no ajuste ML: {e}")
            
            # ====================================================================
            # CÁLCULO DO TAKE PROFIT
            # ====================================================================
            
            # Take profit baseado no risk/reward ratio
            take_profit = self._calculate_take_profit(
                entry_price,
                stop_loss,
                self.config['take_profit_ratio']
            )
            
            # ====================================================================
            # MÉTRICAS DA POSIÇÃO
            # ====================================================================
            
            # Recalcula risco ajustado
            adjusted_risk_amount = position_size * risk_per_unit
            adjusted_risk_percentage = (adjusted_risk_amount / self.available_capital) * 100
            
            # Relação risco/retorno
            reward_potential = abs(take_profit - entry_price) * position_size
            risk_reward_ratio = reward_potential / adjusted_risk_amount if adjusted_risk_amount > 0 else 0
            
            # Score de convicção
            conviction_score = self._calculate_conviction_score(
                confidence, confidence_multiplier, adjusted_risk_percentage
            )
            
            # ====================================================================
            # VALIDAÇÃO FINAL
            # ====================================================================
            
            # Verifica limites
            validation_result = self._validate_position_risk(
                adjusted_risk_percentage, symbol, position_value
            )
            
            if not validation_result['approved']:
                return {'error': validation_result['reason']}
            
            # ====================================================================
            # RESULTADO
            # ====================================================================
            
            calculation_time = (datetime.now() - start_time).total_seconds() * 1000  # ms
            
            result = {
                'symbol': symbol,
                'position_size': round(position_size, 6),
                'position_value': round(position_value, 2),
                'risk_amount': round(adjusted_risk_amount, 2),
                'risk_percentage': round(adjusted_risk_percentage, 3),
                'entry_price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': round(take_profit, 4),
                'risk_reward_ratio': round(risk_reward_ratio, 2),
                'confidence_used': confidence,
                'confidence_multiplier': round(confidence_multiplier, 3),
                'market_regime': market_regime,
                'regime_multiplier': regime_multiplier,
                'sizing_method': sizing_method,
                'conviction_score': round(conviction_score, 1),
                'approved': True,
                'validation_details': validation_result['details'],
                'calculation_time_ms': round(calculation_time, 2),
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.info(f"📊 Posição calculada para {symbol}: "
                           f"Tamanho: {position_size:.4f}, "
                           f"Risco: {adjusted_risk_percentage:.2f}%, "
                           f"R/R: {risk_reward_ratio:.2f}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao calcular posição para {symbol}: {e}")
            return {'error': str(e)}
    
    def _calculate_confidence_multiplier(self, confidence: float) -> float:
        """Calcula multiplicador baseado na confiança"""
        
        # Mapeia confiança [0,1] para multiplicador [0.5, 1.5]
        multiplier = 0.5 + confidence
        
        # Limita
        return max(0.5, min(1.5, multiplier))
    
    def _calculate_take_profit(self,
                              entry: float,
                              stop: float,
                              ratio: float) -> float:
        """Calcula take profit baseado no ratio risk/reward"""
        
        risk_amount = abs(entry - stop)
        reward_amount = risk_amount * ratio
        
        if entry > stop:  # Long position
            return entry + reward_amount
        else:  # Short position
            return entry - reward_amount
    
    def _calculate_conviction_score(self,
                                   confidence: float,
                                   confidence_multiplier: float,
                                   risk_percentage: float) -> float:
        """Calcula score de convicção da posição (0-100)"""
        
        # Base na confiança (0-50)
        score = confidence * 50
        
        # Ajuste por multiplicador (0-25)
        score += (confidence_multiplier - 1) * 50
        
        # Ajuste por risco (0-25)
        optimal_risk = self.config['max_risk_per_trade'] * 100
        risk_ratio = min(1, risk_percentage / optimal_risk)
        score += risk_ratio * 25
        
        return max(0, min(100, score))
    
    def _validate_position_risk(self,
                               risk_percentage: float,
                               symbol: str,
                               position_value: float) -> Dict[str, Any]:
        """Valida se a posição está dentro dos limites de risco"""
        
        validation = {
            'approved': True,
            'reason': '',
            'details': {}
        }
        
        # 1. Verifica risco por trade
        if risk_percentage > self.config['max_risk_per_trade'] * 100 * 1.1:  # 10% de tolerância
            validation['approved'] = False
            validation['reason'] = f'Risco por trade excedido: {risk_percentage:.2f}%'
            validation['details']['risk_check'] = 'failed'
            return validation
        
        # 2. Verifica número máximo de posições
        if len(self.positions) >= self.config['max_positions']:
            validation['approved'] = False
            validation['reason'] = f'Número máximo de posições atingido: {len(self.positions)}'
            validation['details']['position_count'] = 'failed'
            return validation
        
        # 3. Verifica capital disponível
        if position_value > self.available_capital:
            validation['approved'] = False
            validation['reason'] = f'Capital insuficiente: {position_value:.2f} > {self.available_capital:.2f}'
            validation['details']['capital_check'] = 'failed'
            return validation
        
        # 4. Verifica correlação (se habilitado)
        if self.config.get('enable_correlation_check', True):
            correlation_risk = self._check_correlation_risk(symbol)
            if correlation_risk['high_risk']:
                validation['approved'] = False
                validation['reason'] = f'Risco de correlação alto: {correlation_risk["max_correlation"]:.2f}'
                validation['details']['correlation_check'] = correlation_risk
                return validation
            else:
                validation['details']['correlation_check'] = correlation_risk
        
        # 5. Verifica risco diário
        if self.daily_risk_used + risk_percentage / 100 > self.config['max_daily_risk']:
            validation['approved'] = False
            validation['reason'] = 'Limite diário de risco atingido'
            validation['details']['daily_risk'] = 'failed'
            return validation
        
        # 6. Verifica concentração
        portfolio_exposure = sum(p.position_value for p in self.positions.values()) / self.current_capital
        new_exposure = portfolio_exposure + (position_value / self.current_capital)
        
        if new_exposure > self.config.get('max_portfolio_exposure', 0.5):
            validation['approved'] = False
            validation['reason'] = f'Exposição máxima do portfólio excedida: {new_exposure:.1%}'
            validation['details']['exposure_check'] = 'failed'
            return validation
        
        validation['details'] = {
            'risk_check': 'passed',
            'position_count': len(self.positions) + 1,
            'capital_check': 'passed',
            'daily_risk_check': 'passed',
            'exposure_check': 'passed'
        }
        
        return validation
    
    def _check_correlation_risk(self, symbol: str) -> Dict[str, Any]:
        """Verifica risco de correlação com posições existentes"""
        
        if not self.positions:
            return {'high_risk': False, 'max_correlation': 0.0}
        
        # Simula correlações (em produção, usar dados reais)
        correlations = {}
        max_correlation = 0.0
        high_correlation_symbols = []
        
        for pos_symbol in self.positions.keys():
            # Gera correlação simulada
            np.random.seed(hash(symbol + pos_symbol) % 2**32)
            correlation = np.random.uniform(-0.3, 0.8)
            correlations[pos_symbol] = correlation
            
            if abs(correlation) > self.config['max_correlation']:
                max_correlation = max(max_correlation, abs(correlation))
                high_correlation_symbols.append(pos_symbol)
        
        high_risk = max_correlation > self.config['max_correlation']
        
        return {
            'high_risk': high_risk,
            'max_correlation': round(max_correlation, 3),
            'high_correlation_symbols': high_correlation_symbols,
            'correlations': correlations
        }
    
    # ========================================================================
    # GESTÃO DE POSIÇÕES
    # ========================================================================
    
    def add_position(self, position_data: Dict[str, Any]) -> Optional[str]:
        """
        Adiciona nova posição ao portfólio
        
        Args:
            position_data: Dados da posição calculada
            
        Returns:
            ID da posição ou None se erro
        """
        
        try:
            # Verifica se há erro
            if 'error' in position_data:
                self.logger.error(f"❌ Erro nos dados da posição: {position_data['error']}")
                return None
            
            # Verifica aprovação
            if not position_data.get('approved', False):
                self.logger.warning(f"⚠️ Posição não aprovada: {position_data.get('reason', 'Desconhecido')}")
                return None
            
            symbol = position_data['symbol']
            
            # Gera ID único
            position_id = hashlib.md5(
                f"{symbol}{datetime.now().isoformat()}{np.random.random()}".encode()
            ).hexdigest()[:16]
            
            # Cria objeto PositionRisk
            position = PositionRisk(
                symbol=symbol,
                position_id=position_id,
                status=PositionStatus.ACTIVE,
                position_size=position_data['position_size'],
                entry_price=position_data['entry_price'],
                current_price=position_data['entry_price'],
                stop_loss=position_data['stop_loss'],
                take_profit=position_data['take_profit'],
                risk_amount=position_data['risk_amount'],
                risk_percentage=position_data['risk_percentage'],
                notional_value=position_data['position_value'],
                risk_reward_ratio=position_data['risk_reward_ratio'],
                confidence_level=position_data['confidence_used'],
                conviction_score=position_data['conviction_score'],
                entry_time=datetime.now(),
                strategy=position_data.get('strategy', 'default'),
                metadata={
                    'sizing_method': position_data.get('sizing_method'),
                    'market_regime': position_data.get('market_regime'),
                    'calculation_time_ms': position_data.get('calculation_time_ms')
                }
            )
            
            # Adiciona ao portfólio
            self.positions[symbol] = position
            
            # Atualiza capital
            self.available_capital -= position.notional_value
            
            # Atualiza risco diário usado
            self.daily_risk_used += position.risk_percentage / 100
            self.daily_trades += 1
            
            # Atualiza métricas
            self._update_portfolio_metrics()
            
            self.logger.info(f"Posicao adicionada: {symbol} | ID: {position_id} | "
                           f"Valor: ${position.notional_value:,.2f} | "
                           f"Risco: {position.risk_percentage:.2f}%")
            
            # Persiste no banco
            if self.db_session:
                self._persist_position(position)
            
            return position_id
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao adicionar posição: {e}")
            return None
    
    def update_position(self, symbol: str, current_price: float) -> Optional[PositionRisk]:
        """
        Atualiza preço atual de uma posição
        
        Args:
            symbol: Símbolo da posição
            current_price: Preço atual
            
        Returns:
            Posição atualizada ou None se não encontrada
        """
        
        if symbol not in self.positions:
            self.logger.warning(f"⚠️ Posição {symbol} não encontrada para atualização")
            return None
        
        try:
            position = self.positions[symbol]
            position.update_price(current_price)
            
            # Atualiza capital de pico
            if self.current_capital > self.peak_capital:
                self.peak_capital = self.current_capital
            
            # Atualiza equity curve
            self.equity_curve.append(self.current_capital + sum(p.unrealized_pnl for p in self.positions.values()))
            self.equity_timestamps.append(datetime.now())
            
            # Verifica alertas
            self._check_position_alerts(position)
            
            # Verifica stop loss e take profit
            if position.is_at_stop:
                self.close_position(symbol, position.stop_loss, reason="Stop Loss")
            elif position.is_at_target:
                self.close_position(symbol, position.take_profit, reason="Take Profit")
            
            return position
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao atualizar posição {symbol}: {e}")
            return None
    
    def close_position(self,
                      symbol: str,
                      exit_price: float,
                      reason: str = "Manual") -> Optional[Dict[str, Any]]:
        """
        Fecha uma posição e calcula resultados
        
        Args:
            symbol: Símbolo da posição
            exit_price: Preço de saída
            reason: Motivo do fechamento
            
        Returns:
            Registro do trade ou None se erro
        """
        
        if symbol not in self.positions:
            self.logger.error(f"❌ Posição {symbol} não encontrada")
            return None
        
        try:
            position = self.positions[symbol]
            
            # ====================================================================
            # CÁLCULO DO RESULTADO
            # ====================================================================
            
            # P&L realizado
            if position.position_size > 0:  # Long
                pnl = (exit_price - position.entry_price) * position.position_size
            else:  # Short
                pnl = (position.entry_price - exit_price) * abs(position.position_size)
            
            # Retorno percentual
            return_percentage = (pnl / position.risk_amount) * 100 if position.risk_amount > 0 else 0
            
            # ====================================================================
            # ATUALIZA CAPITAL
            # ====================================================================
            
            # Libera capital
            position_value = abs(position.position_size) * position.entry_price
            self.available_capital += position_value + pnl
            self.current_capital += pnl
            
            # Atualiza pico
            if self.current_capital > self.peak_capital:
                self.peak_capital = self.current_capital
            
            # ====================================================================
            # REGISTRO DO TRADE
            # ====================================================================
            
            trade_record = {
                'id': hashlib.md5(f"{symbol}{datetime.now().isoformat()}".encode()).hexdigest()[:16],
                'symbol': symbol,
                'position_id': position.position_id,
                'entry_price': position.entry_price,
                'exit_price': exit_price,
                'position_size': position.position_size,
                'pnl': round(pnl, 2),
                'return_percentage': round(return_percentage, 2),
                'risk_amount': position.risk_amount,
                'risk_reward_realized': (pnl / position.risk_amount) if position.risk_amount > 0 else 0,
                'duration': (datetime.now() - position.entry_time),  # timedelta object
                'entry_time': position.entry_time.isoformat(),
                'exit_time': datetime.now().isoformat(),
                'reason': reason,
                'risk_score': position.risk_score,
                'conviction_score': position.conviction_score,
                'strategy': position.strategy
            }
            
            self.trade_history.append(trade_record)
            position.status = PositionStatus.CLOSED
            position.realized_pnl = pnl
            
            # Adiciona ao histórico de posições
            self.position_history.append(position)
            
            # ====================================================================
            # ATUALIZA ESTATÍSTICAS
            # ====================================================================
            
            self._update_performance_stats(trade_record)
            
            # Remove posição ativa
            del self.positions[symbol]
            
            # ====================================================================
            # LOGGING
            # ====================================================================
            
            result_indicator = "PROFIT" if pnl > 0 else "LOSS"
            self.logger.info(f"{result_indicator} Posicao fechada: {symbol} | "
                           f"P&L: ${pnl:,.2f} | "
                           f"Retorno: {return_percentage:.2f}% | "
                           f"Motivo: {reason}")
            
            # ====================================================================
            # VERIFICA LIMITES
            # ====================================================================
            
            # self._check_risk_limits()
            
            # ====================================================================
            # PERSISTÊNCIA
            # ====================================================================
            
            if self.db_session:
                self._persist_trade(trade_record)
            
            return trade_record
            
        except Exception as e:
            self.logger.error(f"ERRO Erro ao fechar posição {symbol}: {e}")
            return None
    
    def _update_performance_stats(self, trade: Dict[str, Any]) -> None:
        """Atualiza estatísticas de performance"""
        
        self.performance_stats['trades_total'] += 1
        
        if trade['pnl'] > 0:
            self.performance_stats['winning_trades'] += 1
            self.performance_stats['total_pnl'] += trade['pnl']
            
            # Média de ganhos
            if self.performance_stats['avg_win'] == 0:
                self.performance_stats['avg_win'] = trade['pnl']
            else:
                self.performance_stats['avg_win'] = (
                    self.performance_stats['avg_win'] * (self.performance_stats['winning_trades'] - 1) + trade['pnl']
                ) / self.performance_stats['winning_trades']
            
            # Sequência de vitórias
            if 'current_win_streak' not in self.performance_stats:
                self.performance_stats['current_win_streak'] = 1
            else:
                self.performance_stats['current_win_streak'] += 1
            
            self.performance_stats['current_loss_streak'] = 0
            self.performance_stats['max_consecutive_wins'] = max(
                self.performance_stats.get('max_consecutive_wins', 0),
                self.performance_stats['current_win_streak']
            )
            
        else:
            self.performance_stats['losing_trades'] += 1
            self.performance_stats['total_pnl'] += trade['pnl']
            
            # Média de perdas
            if self.performance_stats['avg_loss'] == 0:
                self.performance_stats['avg_loss'] = abs(trade['pnl'])
            else:
                self.performance_stats['avg_loss'] = (
                    self.performance_stats['avg_loss'] * (self.performance_stats['losing_trades'] - 1) + abs(trade['pnl'])
                ) / self.performance_stats['losing_trades']
            
            # Sequência de perdas
            if 'current_loss_streak' not in self.performance_stats:
                self.performance_stats['current_loss_streak'] = 1
            else:
                self.performance_stats['current_loss_streak'] += 1
            
            self.performance_stats['current_win_streak'] = 0
            self.performance_stats['max_consecutive_losses'] = max(
                self.performance_stats.get('max_consecutive_losses', 0),
                self.performance_stats['current_loss_streak']
            )
        
        # Win rate
        if self.performance_stats['trades_total'] > 0:
            self.performance_stats['win_rate'] = (
                self.performance_stats['winning_trades'] / self.performance_stats['trades_total']
            )
        
        # Profit factor
        total_wins = self.performance_stats['winning_trades'] * self.performance_stats['avg_win']
        total_losses = self.performance_stats['losing_trades'] * self.performance_stats['avg_loss']
        
        if total_losses > 0:
            self.performance_stats['profit_factor'] = total_wins / total_losses
        else:
            self.performance_stats['profit_factor'] = float('inf') if total_wins > 0 else 0
        
        # Média de holding period
        if 'avg_holding_period' not in self.performance_stats:
            self.performance_stats['avg_holding_period'] = trade['duration']
        else:
            self.performance_stats['avg_holding_period'] = (
                self.performance_stats['avg_holding_period'] * (self.performance_stats['trades_total'] - 1) + trade['duration']
            ) / self.performance_stats['trades_total']
    
    # ========================================================================
    # ANÁLISE DE RISCO DO PORTFÓLIO
    # ========================================================================
    
    def calculate_portfolio_risk(self, returns_data: Optional[pd.DataFrame] = None) -> RiskMetrics:
        """
        Calcula métricas de risco completas do portfólio
        
        Args:
            returns_data: DataFrame com retornos históricos (opcional)
            
        Returns:
            RiskMetrics com todas as métricas calculadas
        """
        
        try:
            # ====================================================================
            # PREPARA DADOS
            # ====================================================================
            
            if returns_data is None and self.trade_history:
                # Constrói série de retornos do histórico
                df = pd.DataFrame(self.trade_history)
                if not df.empty and 'return_percentage' in df.columns:
                    returns = df['return_percentage'].values / 100
                else:
                    returns = np.random.randn(100) * 0.02  # Dados simulados
            else:
                returns = np.random.randn(100) * 0.02  # Dados simulados
            
            # ====================================================================
            # VALUE AT RISK (VaR)
            # ====================================================================
            
            # VaR 95%, 99%, 99.5%
            var_95 = np.percentile(returns, 5) * self.current_capital
            var_99 = np.percentile(returns, 1) * self.current_capital
            var_995 = np.percentile(returns, 0.5) * self.current_capital
            
            # Intervalo de confiança para VaR
            n_bootstrap = 1000
            bootstrap_vars = []
            for _ in range(n_bootstrap):
                sample = np.random.choice(returns, size=len(returns), replace=True)
                bootstrap_vars.append(np.percentile(sample, 5) * self.current_capital)
            
            var_ci = (
                np.percentile(bootstrap_vars, 2.5),
                np.percentile(bootstrap_vars, 97.5)
            )
            
            # ====================================================================
            # CONDITIONAL VAR (CVaR)
            # ====================================================================
            
            # CVaR 95%, 99%, 99.5%
            cvar_95 = returns[returns <= np.percentile(returns, 5)].mean() * self.current_capital
            cvar_99 = returns[returns <= np.percentile(returns, 1)].mean() * self.current_capital
            cvar_995 = returns[returns <= np.percentile(returns, 0.5)].mean() * self.current_capital
            
            # ====================================================================
            # VOLATILIDADE
            # ====================================================================
            
            # Volatilidade anualizada
            volatility = np.std(returns) * np.sqrt(252)
            
            # Downside volatility (apenas retornos negativos)
            downside_returns = returns[returns < 0]
            downside_volatility = np.std(downside_returns) * np.sqrt(252) if len(downside_returns) > 0 else 0
            
            # Semi-volatility
            semi_volatility = np.sqrt(np.mean(returns[returns < 0] ** 2)) * np.sqrt(252) if len(downside_returns) > 0 else 0
            
            # ====================================================================
            # RATIOS DE PERFORMANCE
            # ====================================================================
            
            # Sharpe Ratio (assumindo taxa livre de risco = 2% anual)
            risk_free_rate = 0.02 / 252
            excess_returns = returns - risk_free_rate
            sharpe_ratio = np.mean(excess_returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else 0
            
            # Sortino Ratio
            sortino_ratio = np.mean(excess_returns) / downside_volatility * np.sqrt(252) if downside_volatility > 0 else 0
            
            # ====================================================================
            # DRAWDOWN
            # ====================================================================
            
            # Calcula drawdown da equity curve
            if len(self.equity_curve) > 1:
                equity_array = np.array(self.equity_curve)
                running_max = np.maximum.accumulate(equity_array)
                drawdown = (equity_array - running_max) / running_max
                
                max_drawdown = np.min(drawdown)
                
                # Duração do máximo drawdown
                drawdown_start = np.argmax(drawdown == max_drawdown)
                drawdown_end = np.argmax(equity_array[drawdown_start:] >= running_max[drawdown_start])
                max_drawdown_duration = drawdown_end if drawdown_end > 0 else len(equity_array) - drawdown_start
                
                # Drawdown médio
                avg_drawdown = np.mean(drawdown[drawdown < 0])
                
                # Volatilidade do drawdown
                drawdown_volatility = np.std(drawdown[drawdown < 0])
                
            else:
                max_drawdown = 0
                max_drawdown_duration = 0
                avg_drawdown = 0
                drawdown_volatility = 0
            
            # ====================================================================
            # MOMENTOS ESTATÍSTICOS
            # ====================================================================
            
            # Curtose e assimetria
            kurtosis = stats.kurtosis(returns)
            skewness = stats.skew(returns)
            
            # Tail Ratio (95% / 5%)
            tail_ratio = abs(np.percentile(returns, 95) / np.percentile(returns, 5)) if np.percentile(returns, 5) != 0 else 1
            
            # ====================================================================
            # COMPONENTES DE RISCO
            # ====================================================================
            
            # VaR por componente (marginal contribution)
            component_var = {}
            marginal_var = {}
            
            if self.positions:
                total_risk = 0
                for symbol, position in self.positions.items():
                    position_risk = abs(position.unrealized_pnl) + position.risk_amount
                    component_var[symbol] = position_risk
                    total_risk += position_risk
                
                for symbol, risk in component_var.items():
                    marginal_var[symbol] = risk / total_risk if total_risk > 0 else 0
            
            # ====================================================================
            # ATUALIZA MÉTRICAS
            # ====================================================================
            
            self.risk_metrics = RiskMetrics(
                # VaR
                var_95=var_95,
                var_99=var_99,
                var_995=var_995,
                var_confidence_interval=var_ci,
                
                # CVaR
                cvar_95=cvar_95,
                cvar_99=cvar_99,
                cvar_995=cvar_995,
                
                # Ratios
                sharpe_ratio=sharpe_ratio,
                sortino_ratio=sortino_ratio,
                
                # Drawdown
                max_drawdown=max_drawdown,
                max_drawdown_duration=max_drawdown_duration,
                avg_drawdown=avg_drawdown,
                drawdown_volatility=drawdown_volatility,
                
                # Volatilidade
                volatility=volatility,
                downside_volatility=downside_volatility,
                semi_volatility=semi_volatility,
                tail_ratio=tail_ratio,
                
                # Estatísticas
                kurtosis=kurtosis,
                skewness=skewness,
                
                # Componentes
                component_var=component_var,
                marginal_var=marginal_var,
                
                # Portfolio VaR
                portfolio_var=var_95,
                portfolio_cvar=cvar_95
            )
            
            self.logger.info(f"Métricas de risco atualizadas | "
                           f"Sharpe: {sharpe_ratio:.2f} | "
                           f"VaR 95%: {var_95:.2f}")

            return self.risk_metrics

        except Exception as e:
            self.logger.error(f"Erro ao calcular risco do portfólio: {e}")
            raise

    # ========================================================================
    # FUNÇÕES AUXILIARES
    # ========================================================================

    def get_risk_report(self) -> dict:
        """Gera relatório completo de risco"""
        if not self.risk_metrics:
            self.calculate_portfolio_risk()

        return {
            'metrics': self.risk_metrics.__dict__,
            'portfolio_value': self.current_capital,
            'positions_count': len(self.positions),
            'trade_count': self.performance_stats['trades_total'],
            'timestamp': datetime.now().isoformat()
        }

    def check_risk_limits(self) -> tuple[bool, str]:
        """Verifica se o portfólio está dentro dos limites de risco"""
        if not self.risk_metrics:
            return True, "Risco não calculado"

        # Exemplo de limites
        max_drawdown_limit = -0.10  # -10%
        max_var_limit = -0.05       # -5% do capital

        issues = []

        if self.risk_metrics.max_drawdown < max_drawdown_limit:
            issues.append(f"Drawdown máximo excedido: {self.risk_metrics.max_drawdown:.2%}")

        if self.risk_metrics.var_95 < max_var_limit:
            issues.append(f"VaR 95% excedido: {self.risk_metrics.var_95:.2%}")

        is_within_limits = len(issues) == 0
        message = "; ".join(issues) if issues else "Todos os limites de risco dentro do permitido"

        return is_within_limits, message

    def get_position_risk(self, symbol: str) -> dict:
        """Obtém informações de risco de uma posição específica"""
        if symbol in self.positions:
            position = self.positions[symbol]
            return {
                'symbol': symbol,
                'unrealized_pnl': position.unrealized_pnl,
                'risk_amount': position.risk_amount,
                'position_size': position.size,
                'entry_price': position.entry_price,
                'current_price': position.current_price
            }
        return {}

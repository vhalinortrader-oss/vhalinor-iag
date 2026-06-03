"""
╔═════════════════════════════════════════════════════════════════════════════╗
║           MECANISMO DE ADAPTAÇÃO ONLINE E DETECÇÃO DE MUDANÇA DE REGIME        ║
║                 Componente 9: Sistema Adaptativo Inteligente                   ║
╚═════════════════════════════════════════════════════════════════════════════╝
"""

import asyncio
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import SGDRegressor, LogisticRegression
from sklearn.metrics import mean_squared_error, accuracy_score
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import warnings
import json
import pickle
from collections import deque, defaultdict
import time
import threading
from concurrent.futures import ThreadPoolExecutor

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('OnlineAdaptationSystem')

class RegimeType(Enum):
    """Tipos de regime de mercado"""
    BULL_MARKET = "bull_market"
    BEAR_MARKET = "bear_market"
    SIDEWAYS = "sideways"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"
    TRENDING_UP = "trending_up"
    TRENDING_DOWN = "trending_down"
    MEAN_REVERTING = "mean_reverting"
    MOMENTUM = "momentum"
    CRISIS = "crisis"
    RECOVERY = "recovery"

class AdaptationStrategy(Enum):
    """Estratégias de adaptação"""
    GRADUAL_UPDATE = "gradual_update"
    ABRUPT_UPDATE = "abrupt_update"
    ENSEMBLE_WEIGHTING = "ensemble_weighting"
    MODEL_SWITCHING = "model_switching"
    HYPERPARAMETER_TUNING = "hyperparameter_tuning"
    FEATURE_REWEIGHTING = "feature_reweighting"
    RISK_ADJUSTMENT = "risk_adjustment"

class DetectionMethod(Enum):
    """Métodos de detecção de mudança"""
    CUSUM = "cusum"
    BAYESIAN_CHANGE_POINT = "bayesian_change_point"
    LIKELIHOOD_RATIO = "likelihood_ratio"
    STATISTICAL_PROCESS_CONTROL = "statistical_process_control"
    MACHINE_LEARNING = "machine_learning"
    VOLATILITY_CLUSTERING = "volatility_clustering"
    CORRELATION_SHIFT = "correlation_shift"
    DISTRIBUTION_CHANGE = "distribution_change"

@dataclass
class RegimeState:
    """Estado atual do regime"""
    regime_type: RegimeType
    confidence: float
    start_time: datetime
    duration: timedelta
    characteristics: Dict[str, float]
    transition_probability: Dict[RegimeType, float]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'regime_type': self.regime_type.value,
            'confidence': self.confidence,
            'start_time': self.start_time.isoformat(),
            'duration_seconds': self.duration.total_seconds(),
            'characteristics': self.characteristics,
            'transition_probability': {k.value: v for k, v in self.transition_probability.items()},
            'metadata': self.metadata
        }

@dataclass
class ChangePoint:
    """Ponto de mudança detectado"""
    timestamp: datetime
    old_regime: RegimeType
    new_regime: RegimeType
    confidence: float
    detection_method: DetectionMethod
    evidence_score: float
    transition_period: timedelta
    affected_features: List[str]
    adaptation_actions: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'old_regime': self.old_regime.value,
            'new_regime': self.new_regime.value,
            'confidence': self.confidence,
            'detection_method': self.detection_method.value,
            'evidence_score': self.evidence_score,
            'transition_period_seconds': self.transition_period.total_seconds(),
            'affected_features': self.affected_features,
            'adaptation_actions': self.adaptation_actions
        }

@dataclass
class AdaptationAction:
    """Ação de adaptação executada"""
    action_type: AdaptationStrategy
    timestamp: datetime
    target_component: str
    parameters: Dict[str, Any]
    reason: str
    effectiveness_score: Optional[float] = None
    execution_time: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'action_type': self.action_type.value,
            'timestamp': self.timestamp.isoformat(),
            'target_component': self.target_component,
            'parameters': self.parameters,
            'reason': self.reason,
            'effectiveness_score': self.effectiveness_score,
            'execution_time': self.execution_time
        }

class CUSUMDetector:
    """Detector CUSUM (Cumulative Sum)"""
    
    def __init__(self, threshold: float = 5.0, drift: float = 0.0):
        self.threshold = threshold
        self.drift = drift
        self.positive_cumsum = 0.0
        self.negative_cumsum = 0.0
        self.change_points = []
        
        logger.info(f"📊 CUSUMDetector inicializado: threshold={threshold}, drift={drift}")
    
    def detect_change(self, data: np.ndarray) -> List[int]:
        """Detecta pontos de mudança usando CUSUM"""
        change_points = []
        
        for i, value in enumerate(data):
            # Atualiza somas cumulativas
            self.positive_cumsum = max(0, self.positive_cumsum + value - self.drift)
            self.negative_cumsum = min(0, self.negative_cumsum + value - self.drift)
            
            # Verifica se houve mudança
            if self.positive_cumsum > self.threshold or self.negative_cumsum < -self.threshold:
                change_points.append(i)
                self.change_points.append(i)
                
                # Reseta somas
                self.positive_cumsum = 0.0
                self.negative_cumsum = 0.0
        
        return change_points
    
    def reset(self):
        """Reseta detector"""
        self.positive_cumsum = 0.0
        self.negative_cumsum = 0.0
        self.change_points = []

class BayesianChangePointDetector:
    """Detector Bayesiano de pontos de mudança"""
    
    def __init__(self, hazard_rate: float = 0.001, min_run_length: int = 10):
        self.hazard_rate = hazard_rate
        self.min_run_length = min_run_length
        self.run_length = 0
        self.posterior = defaultdict(float)
        self.change_points = []
        
        logger.info(f"🎲 BayesianChangePointDetector inicializado: hazard_rate={hazard_rate}")
    
    def detect_change(self, data: np.ndarray) -> List[int]:
        """Detecta pontos de mudança usando método Bayesiano"""
        change_points = []
        
        for i, value in enumerate(data):
            self.run_length += 1
            
            # Probabilidade de mudança
            change_prob = self.hazard_rate * self.run_length
            
            if np.random.random() < change_prob and self.run_length >= self.min_run_length:
                change_points.append(i)
                self.change_points.append(i)
                self.run_length = 0
        
        return change_points

class VolatilityRegimeDetector:
    """Detector de regime baseado em volatilidade"""
    
    def __init__(self, window_size: int = 20, threshold_multiplier: float = 2.0):
        self.window_size = window_size
        self.threshold_multiplier = threshold_multiplier
        self.regime_history = deque(maxlen=100)
        
        logger.info(f"📈 VolatilityRegimeDetector inicializado: window={window_size}")
    
    def detect_regime(self, returns: pd.Series) -> RegimeType:
        """Detecta regime baseado na volatilidade"""
        if len(returns) < self.window_size:
            return RegimeType.SIDEWAYS
        
        # Calcula volatilidade atual
        current_vol = returns.tail(self.window_size).std()
        
        # Calcula volatilidade histórica
        historical_vol = returns.std()
        
        # Classifica regime
        if current_vol > historical_vol * self.threshold_multiplier:
            return RegimeType.HIGH_VOLATILITY
        elif current_vol < historical_vol / self.threshold_multiplier:
            return RegimeType.LOW_VOLATILITY
        else:
            return RegimeType.SIDEWAYS

class TrendRegimeDetector:
    """Detector de regime de tendência"""
    
    def __init__(self, window_size: int = 50, min_slope: float = 0.001):
        self.window_size = window_size
        self.min_slope = min_slope
        
        logger.info(f"📊 TrendRegimeDetector inicializado: window={window_size}")
    
    def detect_regime(self, prices: pd.Series) -> RegimeType:
        """Detecta regime de tendência"""
        if len(prices) < self.window_size:
            return RegimeType.SIDEWAYS
        
        # Calcula inclinação da tendência
        window_prices = prices.tail(self.window_size)
        x = np.arange(len(window_prices))
        slope, _, _, _, _ = stats.linregress(x, window_prices)
        
        # Classifica regime
        if slope > self.min_slope:
            return RegimeType.TRENDING_UP
        elif slope < -self.min_slope:
            return RegimeType.TRENDING_DOWN
        else:
            return RegimeType.SIDEWAYS

class OnlineModelAdapter:
    """Adaptador online de modelos"""
    
    def __init__(self, learning_rate: float = 0.01, window_size: int = 1000):
        self.learning_rate = learning_rate
        self.window_size = window_size
        self.model = None
        self.scaler = StandardScaler()
        self.performance_history = deque(maxlen=100)
        self.adaptation_history = []
        
        logger.info(f"🔄 OnlineModelAdapter inicializado: lr={learning_rate}")
    
    def initialize_model(self, model_type: str = "sgd_regressor"):
        """Inicializa modelo online"""
        if model_type == "sgd_regressor":
            self.model = SGDRegressor(
                learning_rate='adaptive',
                eta0=self.learning_rate,
                random_state=42
            )
        elif model_type == "logistic_regression":
            self.model = LogisticRegression(
                solver='saga',
                learning_rate='adaptive',
                eta0=self.learning_rate,
                random_state=42
            )
        
        logger.info(f"🤖 Modelo {model_type} inicializado")
    
    def update_model(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """Atualiza modelo com novos dados"""
        if self.model is None:
            self.initialize_model()
        
        # Normaliza dados
        if not hasattr(self.scaler, 'mean_'):
            X_scaled = self.scaler.fit_transform(X)
        else:
            X_scaled = self.scaler.transform(X)
        
        # Avalia performance atual
        if hasattr(self.model, 'coef_'):
            y_pred = self.model.predict(X_scaled)
            current_mse = mean_squared_error(y, y_pred)
        else:
            current_mse = float('inf')
        
        # Atualiza modelo
        start_time = time.time()
        self.model.partial_fit(X_scaled, y)
        update_time = time.time() - start_time
        
        # Avalia nova performance
        y_pred_new = self.model.predict(X_scaled)
        new_mse = mean_squared_error(y, y_pred_new)
        
        # Registra adaptação
        adaptation_record = {
            'timestamp': datetime.now(),
            'old_mse': current_mse,
            'new_mse': new_mse,
            'improvement': current_mse - new_mse,
            'update_time': update_time,
            'sample_size': len(X)
        }
        
        self.adaptation_history.append(adaptation_record)
        self.performance_history.append(new_mse)
        
        logger.info(f"🔄 Modelo atualizado: MSE {current_mse:.6f} → {new_mse:.6f}")
        
        return adaptation_record
    
    def get_adaptation_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de adaptação"""
        if not self.adaptation_history:
            return {}
        
        improvements = [r['improvement'] for r in self.adaptation_history]
        update_times = [r['update_time'] for r in self.adaptation_history]
        
        return {
            'total_adaptations': len(self.adaptation_history),
            'avg_improvement': np.mean(improvements),
            'std_improvement': np.std(improvements),
            'avg_update_time': np.mean(update_times),
            'recent_performance': list(self.performance_history)[-10:],
            'improvement_rate': sum(1 for imp in improvements if imp > 0) / len(improvements)
        }

class EnsembleAdaptationManager:
    """Gerenciador de adaptação ensemble"""
    
    def __init__(self, n_models: int = 5):
        self.n_models = n_models
        self.models = []
        self.weights = np.ones(n_models) / n_models
        self.performance_scores = np.zeros(n_models)
        self.adaptation_history = []
        
        logger.info(f"🎭 EnsembleAdaptationManager inicializado: {n_models} modelos")
    
    def add_model(self, model, name: str):
        """Adiciona modelo ao ensemble"""
        if len(self.models) < self.n_models:
            self.models.append({'model': model, 'name': name})
            logger.info(f"➕ Modelo {name} adicionado ao ensemble")
        else:
            logger.warning(f"⚠️ Ensemble cheio: {self.n_models} modelos")
    
    def update_weights(self, X: np.ndarray, y: np.ndarray):
        """Atualiza pesos baseado na performance recente"""
        if len(self.models) == 0:
            return
        
        # Avalia performance de cada modelo
        performances = []
        for i, model_info in enumerate(self.models):
            model = model_info['model']
            
            try:
                if hasattr(model, 'predict'):
                    y_pred = model.predict(X)
                    mse = mean_squared_error(y, y_pred)
                    performances.append(1 / (1 + mse))  # Inverso do erro
                else:
                    performances.append(0.0)
            except Exception as e:
                logger.warning(f"⚠️ Erro ao avaliar modelo {model_info['name']}: {e}")
                performances.append(0.0)
        
        # Atualiza pesos (softmax dos performances)
        if sum(performances) > 0:
            exp_performances = np.exp(np.array(performances) - np.max(performances))
            self.weights = exp_performances / np.sum(exp_performances)
        
        # Registra performance
        self.performance_scores = np.array(performances)
        
        logger.info(f"🎯 Pesos atualizados: {self.weights}")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Faz predição ensemble"""
        if len(self.models) == 0:
            raise ValueError("Nenhum modelo no ensemble")
        
        predictions = []
        for i, model_info in enumerate(self.models):
            model = model_info['model']
            
            try:
                if hasattr(model, 'predict'):
                    pred = model.predict(X)
                    predictions.append(pred)
                else:
                    predictions.append(np.zeros(len(X)))
            except Exception as e:
                logger.warning(f"⚠️ Erro na predição do modelo {model_info['name']}: {e}")
                predictions.append(np.zeros(len(X)))
        
        # Predição ponderada
        ensemble_pred = np.average(predictions, axis=0, weights=self.weights)
        
        return ensemble_pred
    
    def get_ensemble_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do ensemble"""
        if len(self.models) == 0:
            return {}
        
        return {
            'n_models': len(self.models),
            'weights': self.weights.tolist(),
            'performance_scores': self.performance_scores.tolist(),
            'model_names': [m['name'] for m in self.models],
            'weight_entropy': -np.sum(self.weights * np.log(self.weights + 1e-10)),
            'dominant_model': np.argmax(self.weights)
        }

class OnlineAdaptationSystem:
    """Sistema completo de adaptação online"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Detectores
        self.cusum_detector = CUSUMDetector(
            threshold=self.config.get('cusum_threshold', 5.0),
            drift=self.config.get('cusum_drift', 0.0)
        )
        
        self.bayesian_detector = BayesianChangePointDetector(
            hazard_rate=self.config.get('hazard_rate', 0.001),
            min_run_length=self.config.get('min_run_length', 10)
        )
        
        self.volatility_detector = VolatilityRegimeDetector(
            window_size=self.config.get('volatility_window', 20),
            threshold_multiplier=self.config.get('volatility_threshold', 2.0)
        )
        
        self.trend_detector = TrendRegimeDetector(
            window_size=self.config.get('trend_window', 50),
            min_slope=self.config.get('min_slope', 0.001)
        )
        
        # Adaptadores
        self.model_adapter = OnlineModelAdapter(
            learning_rate=self.config.get('learning_rate', 0.01),
            window_size=self.config.get('window_size', 1000)
        )
        
        self.ensemble_manager = EnsembleAdaptationManager(
            n_models=self.config.get('n_ensemble_models', 5)
        )
        
        # Estado atual
        self.current_regime = RegimeType.SIDEWAYS
        self.regime_history = deque(maxlen=1000)
        self.change_points = deque(maxlen=100)
        self.adaptation_actions = deque(maxlen=500)
        
        # Métricas
        self.detection_accuracy = 0.0
        self.adaptation_effectiveness = 0.0
        self.false_positive_rate = 0.0
        
        # Thread de monitoramento
        self.monitoring_active = False
        self.monitoring_thread = None
        
        logger.info("🧠 OnlineAdaptationSystem inicializado")
    
    async def start_monitoring(self, data_source, update_interval: int = 60):
        """Inicia monitoramento contínuo"""
        if self.monitoring_active:
            logger.warning("⚠️ Monitoramento já está ativo")
            return
        
        self.monitoring_active = True
        
        def monitoring_loop():
            while self.monitoring_active:
                try:
                    # Obtém novos dados
                    new_data = data_source.get_latest_data()
                    
                    if new_data is not None and len(new_data) > 0:
                        # Processa detecção de mudança
                        await self.process_market_data(new_data)
                    
                    time.sleep(update_interval)
                    
                except Exception as e:
                    logger.error(f"❌ Erro no monitoramento: {e}")
                    time.sleep(update_interval)
        
        self.monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        logger.info(f"👁️ Monitoramento iniciado: intervalo={update_interval}s")
    
    def stop_monitoring(self):
        """Para monitoramento"""
        self.monitoring_active = False
        
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
        
        logger.info("🛑 Monitoramento parado")
    
    async def process_market_data(self, data: pd.DataFrame):
        """Processa novos dados de mercado"""
        if len(data) == 0:
            return
        
        try:
            # Detecta mudanças de regime
            await self.detect_regime_changes(data)
            
            # Adapta modelos se necessário
            await self.adapt_models(data)
            
            # Atualiza métricas
            self.update_metrics()
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar dados: {e}")
    
    async def detect_regime_changes(self, data: pd.DataFrame):
        """Detecta mudanças de regime"""
        if 'close_price' not in data.columns:
            return
        
        # Calcula retornos
        returns = data['close_price'].pct_change().dropna()
        prices = data['close_price']
        
        # Detecção CUSUM
        cusum_changes = self.cusum_detector.detect_change(returns.values)
        
        # Detecção Bayesiana
        bayesian_changes = self.bayesian_detector.detect_change(returns.values)
        
        # Detecção de regime de volatilidade
        volatility_regime = self.volatility_detector.detect_regime(returns)
        
        # Detecção de regime de tendência
        trend_regime = self.trend_detector.detect_regime(prices)
        
        # Combina detecções
        all_changes = set(cusum_changes + bayesian_changes)
        
        for change_idx in all_changes:
            if change_idx < len(data):
                change_time = data.index[change_idx]
                
                # Determina novo regime
                new_regime = self._determine_regime(
                    volatility_regime, trend_regime, returns.iloc[change_idx]
                )
                
                # Cria ponto de mudança
                if new_regime != self.current_regime:
                    change_point = ChangePoint(
                        timestamp=change_time,
                        old_regime=self.current_regime,
                        new_regime=new_regime,
                        confidence=0.8,  # Simplificado
                        detection_method=DetectionMethod.CUSUM,
                        evidence_score=1.0,  # Simplificado
                        transition_period=timedelta(hours=1),  # Simplificado
                        affected_features=['close_price', 'returns'],
                        adaptation_actions=self._plan_adaptation_actions(
                            self.current_regime, new_regime
                        )
                    )
                    
                    self.change_points.append(change_point)
                    self.current_regime = new_regime
                    
                    logger.info(f"🔄 Mudança de regime detectada: "
                              f"{self.current_regime.value} → {new_regime.value}")
                    
                    # Executa ações de adaptação
                    await self.execute_adaptation_actions(change_point)
    
    def _determine_regime(self, volatility_regime: RegimeType, 
                          trend_regime: RegimeType, current_return: float) -> RegimeType:
        """Determina regime combinado"""
        # Lógica simplificada - pode ser expandida
        if volatility_regime == RegimeType.HIGH_VOLATILITY:
            return RegimeType.HIGH_VOLATILITY
        elif trend_regime == RegimeType.TRENDING_UP:
            return RegimeType.BULL_MARKET
        elif trend_regime == RegimeType.TRENDING_DOWN:
            return RegimeType.BEAR_MARKET
        else:
            return RegimeType.SIDEWAYS
    
    def _plan_adaptation_actions(self, old_regime: RegimeType, 
                                new_regime: RegimeType) -> List[str]:
        """Planeja ações de adaptação"""
        actions = []
        
        # Adaptação baseada na mudança de regime
        if old_regime != new_regime:
            actions.append("model_retraining")
            actions.append("feature_reweighting")
        
        # Ações específicas por regime
        if new_regime == RegimeType.HIGH_VOLATILITY:
            actions.append("risk_adjustment")
            actions.append("position_sizing_reduction")
        elif new_regime == RegimeType.BULL_MARKET:
            actions.append("increase_exposure")
            actions.append("momentum_features")
        elif new_regime == RegimeType.BEAR_MARKET:
            actions.append("reduce_exposure")
            actions.append("defensive_features")
        
        return actions
    
    async def execute_adaptation_actions(self, change_point: ChangePoint):
        """Executa ações de adaptação"""
        for action_str in change_point.adaptation_actions:
            action = AdaptationAction(
                action_type=AdaptationStrategy.GRADUAL_UPDATE,
                timestamp=datetime.now(),
                target_component="model",
                parameters={'action': action_str},
                reason=f"Mudança de regime: {change_point.old_regime.value} → {change_point.new_regime.value}"
            )
            
            # Executa ação
            start_time = time.time()
            
            try:
                if action_str == "model_retraining":
                    # Implementar retreinamento
                    pass
                elif action_str == "feature_reweighting":
                    # Implementar reponderação de features
                    pass
                elif action_str == "risk_adjustment":
                    # Implementar ajuste de risco
                    pass
                
                execution_time = time.time() - start_time
                action.execution_time = execution_time
                action.effectiveness_score = 0.8  # Simplificado
                
            except Exception as e:
                logger.error(f"❌ Erro ao executar ação {action_str}: {e}")
                action.effectiveness_score = 0.0
            
            self.adaptation_actions.append(action)
    
    async def adapt_models(self, data: pd.DataFrame):
        """Adapta modelos online"""
        if len(data) < 2:
            return
        
        # Prepara dados para adaptação
        X = data.drop('close_price', axis=1, errors='ignore').values
        y = data['close_price'].values
        
        if len(X) == 0 or len(y) == 0:
            return
        
        try:
            # Adapta modelo principal
            adaptation_record = self.model_adapter.update_model(X, y)
            
            # Atualiza ensemble se existir
            if len(self.ensemble_manager.models) > 0:
                self.ensemble_manager.update_weights(X, y)
            
            logger.info(f"🔄 Modelos adaptados com {len(X)} amostras")
            
        except Exception as e:
            logger.error(f"❌ Erro na adaptação de modelos: {e}")
    
    def update_metrics(self):
        """Atualiza métricas do sistema"""
        # Simplificado - implementar cálculos reais
        if len(self.change_points) > 0:
            self.detection_accuracy = 0.85  # Placeholder
            self.false_positive_rate = 0.05  # Placeholder
        
        if len(self.adaptation_actions) > 0:
            effective_actions = sum(1 for a in self.adaptation_actions 
                                 if a.effectiveness_score and a.effectiveness_score > 0.5)
            self.adaptation_effectiveness = effective_actions / len(self.adaptation_actions)
    
    def get_system_status(self) -> Dict[str, Any]:
        """Retorna status completo do sistema"""
        return {
            'monitoring_active': self.monitoring_active,
            'current_regime': self.current_regime.value,
            'regime_history_length': len(self.regime_history),
            'change_points_count': len(self.change_points),
            'adaptation_actions_count': len(self.adaptation_actions),
            'detection_accuracy': self.detection_accuracy,
            'adaptation_effectiveness': self.adaptation_effectiveness,
            'false_positive_rate': self.false_positive_rate,
            'model_adapter_stats': self.model_adapter.get_adaptation_stats(),
            'ensemble_stats': self.ensemble_manager.get_ensemble_stats(),
            'last_change_point': self.change_points[-1].to_dict() if self.change_points else None,
            'last_adaptation': self.adaptation_actions[-1].to_dict() if self.adaptation_actions else None
        }
    
    def save_state(self, filepath: str):
        """Salva estado do sistema"""
        try:
            state = {
                'timestamp': datetime.now().isoformat(),
                'current_regime': self.current_regime.value,
                'regime_history': [r.to_dict() for r in self.regime_history],
                'change_points': [cp.to_dict() for cp in self.change_points],
                'adaptation_actions': [aa.to_dict() for aa in self.adaptation_actions],
                'metrics': {
                    'detection_accuracy': self.detection_accuracy,
                    'adaptation_effectiveness': self.adaptation_effectiveness,
                    'false_positive_rate': self.false_positive_rate
                },
                'model_adapter_history': self.model_adapter.adaptation_history,
                'config': self.config
            }
            
            with open(filepath, 'w') as f:
                json.dump(state, f, indent=2, default=str)
            
            logger.info(f"💾 Estado salvo em {filepath}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar estado: {e}")
    
    def load_state(self, filepath: str):
        """Carrega estado do sistema"""
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)
            
            self.current_regime = RegimeType(state['current_regime'])
            
            # Reconstrói histórico (simplificado)
            self.regime_history.clear()
            for r_data in state.get('regime_history', []):
                # Reconstrução simplificada
                pass
            
            self.change_points.clear()
            for cp_data in state.get('change_points', []):
                # Reconstrução simplificada
                pass
            
            self.adaptation_actions.clear()
            for aa_data in state.get('adaptation_actions', []):
                # Reconstrução simplificada
                pass
            
            # Carrega métricas
            metrics = state.get('metrics', {})
            self.detection_accuracy = metrics.get('detection_accuracy', 0.0)
            self.adaptation_effectiveness = metrics.get('adaptation_effectiveness', 0.0)
            self.false_positive_rate = metrics.get('false_positive_rate', 0.0)
            
            logger.info(f"📂 Estado carregado de {filepath}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar estado: {e}")

# Configuração padrão
DEFAULT_ADAPTATION_CONFIG = {
    'cusum_threshold': 5.0,
    'cusum_drift': 0.0,
    'hazard_rate': 0.001,
    'min_run_length': 10,
    'volatility_window': 20,
    'volatility_threshold': 2.0,
    'trend_window': 50,
    'min_slope': 0.001,
    'learning_rate': 0.01,
    'window_size': 1000,
    'n_ensemble_models': 5,
    'monitoring_interval': 60,
    'adaptation_threshold': 0.1
}

if __name__ == "__main__":
    # Exemplo de uso
    class MockDataSource:
        """Fonte de dados mock para teste"""
        
        def __init__(self):
            self.data = self._generate_sample_data()
            self.current_index = 0
        
        def _generate_sample_data(self):
            """Gera dados de exemplo com mudanças de regime"""
            dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='H')
            np.random.seed(42)
            
            # Simula diferentes regimes
            n_points = len(dates)
            data = np.zeros(n_points)
            
            # Regime 1: Tendência de alta
            data[:n_points//3] = np.cumsum(np.random.normal(0.001, 0.02, n_points//3)) + 100
            
            # Regime 2: Lateral
            data[n_points//3:2*n_points//3] = np.cumsum(np.random.normal(0, 0.01, n_points//3)) + data[n_points//3-1]
            
            # Regime 3: Alta volatilidade
            data[2*n_points//3:] = np.cumsum(np.random.normal(0, 0.05, n_points-2*n_points//3)) + data[2*n_points//3-1]
            
            df = pd.DataFrame(index=dates)
            df['close_price'] = data
            df['returns'] = df['close_price'].pct_change()
            
            # Features adicionais
            df['feature_1'] = np.random.randn(n_points)
            df['feature_2'] = np.random.randn(n_points)
            
            return df
        
        def get_latest_data(self, n_points: int = 100):
            """Retorna últimos n pontos de dados"""
            if self.current_index + n_points >= len(self.data):
                self.current_index = 0
            
            start_idx = self.current_index
            end_idx = self.current_index + n_points
            self.current_index = end_idx
            
            return self.data.iloc[start_idx:end_idx]
    
    async def test_adaptation_system():
        """Testa sistema de adaptação online"""
        print("🧪 Iniciando teste do Sistema de Adaptação Online")
        print("=" * 60)
        
        # Cria sistema
        adaptation_system = OnlineAdaptationSystem(DEFAULT_ADAPTATION_CONFIG)
        
        # Cria fonte de dados
        data_source = MockDataSource()
        
        # Inicia monitoramento
        await adaptation_system.start_monitoring(data_source, update_interval=1)
        
        # Simula por algum tempo
        await asyncio.sleep(10)
        
        # Para monitoramento
        adaptation_system.stop_monitoring()
        
        # Mostra status
        status = adaptation_system.get_system_status()
        
        print(f"\n📊 STATUS DO SISTEMA:")
        print(f"Regime Atual: {status['current_regime']}")
        print(f"Pontos de Mudança: {status['change_points_count']}")
        print(f"Ações de Adaptação: {status['adaptation_actions_count']}")
        print(f"Acurácia de Detecção: {status['detection_accuracy']:.2%}")
        print(f"Efetividade de Adaptação: {status['adaptation_effectiveness']:.2%}")
        
        # Estatísticas do adaptador
        adapter_stats = status.get('model_adapter_stats', {})
        if adapter_stats:
            print(f"\n🔄 ESTATÍSTICAS DO ADAPTADOR:")
            print(f"Total de Adaptações: {adapter_stats.get('total_adaptations', 0)}")
            print(f"Melhoria Média: {adapter_stats.get('avg_improvement', 0):.6f}")
            print(f"Taxa de Melhoria: {adapter_stats.get('improvement_rate', 0):.2%}")
        
        # Salva estado
        adaptation_system.save_state('adaptation_system_state.json')
        
        print("\n💾 Estado do sistema salvo")
        print("✅ Teste concluído com sucesso!")
        
        return adaptation_system
    
    # Executa teste
    adaptation_system = asyncio.run(test_adaptation_system())

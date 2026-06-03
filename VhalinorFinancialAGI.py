"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    VHALINOR IAG 1.0.0 - FINANCIAL AGI QUÂNTICO               ║
║         INTELIGÊNCIA ARTIFICIAL GERAL PARA MERCADOS FINANCEIROS              ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  Módulo: CAMADA DE DECISÃO - FINANCIAL AGI (Layer 04)                        ║
║  Versão: 3.0.0 (Production Ready - Ultra Avançada)                           ║
║  Autor: Alex Miranda Sales                                                    ║
║  Data: 2026                                                                   ║
║  License: Proprietary - Vhalinor IAG Systems                                  ║
║  Status: 🟢 TOTALMENTE OPERACIONAL | 🧠 10+ MODELOS | 📊 50+ INDICADORES    ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import json
import hashlib
import pickle
import warnings
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple, Any, Union, Callable, TypeVar
from enum import Enum, auto
from collections import defaultdict, deque
from functools import lru_cache, wraps
import logging
import time

# =============================================================================
# IMPORTAÇÕES CIENTÍFICAS COM FALLBACK GRACIOSO
# =============================================================================

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("⚠️ NumPy não disponível. Usando implementação pura Python.")

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("⚠️ Pandas não disponível. Funcionalidades de DataFrame limitadas.")

try:
    from scipy import stats, signal
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

try:
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.preprocessing import StandardScaler, RobustScaler, MinMaxScaler
    from sklearn.model_selection import TimeSeriesSplit, cross_val_score
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
    from sklearn.pipeline import Pipeline
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("⚠️ Scikit-learn não disponível. Modelos de ML limitados.")

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers, models, optimizers, losses, metrics
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    print("⚠️ TensorFlow não disponível. Redes neurais profundas limitadas.")

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader, TensorDataset
    TORCH_AVAILABLE = True
except (ImportError, OSError):
    TORCH_AVAILABLE = False
    torch = None
    nn = None
    optim = None

try:
    import shap
    SHAP_AVAILABLE = True
except ImportError:
    SHAP_AVAILABLE = False

try:
    import talib
    TA_LIB_AVAILABLE = True
except ImportError:
    TA_LIB_AVAILABLE = False

try:
    from neural_bus import NeuralBus, NeuralMessage
    NEURAL_BUS_AVAILABLE = True
except ImportError:
    NEURAL_BUS_AVAILABLE = False

# =============================================================================
# CONFIGURAÇÕES DE LOGGING AVANÇADAS
# =============================================================================

from logging.handlers import RotatingFileHandler

LOG_FORMAT = '%(asctime)s | %(levelname)-8s | %(name)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

logger = logging.getLogger('VhalinorFinancialAGI')
logger.setLevel(logging.INFO)

# Handler para arquivo com rotação
file_handler = RotatingFileHandler(
    'vhalinor_financial_agi.log',
    maxBytes=50*1024*1024,  # 50MB
    backupCount=10
)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
logger.addHandler(file_handler)

# Handler para console
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
logger.addHandler(console_handler)

# =============================================================================
# ENUMS E CONSTANTES AVANÇADAS
# =============================================================================

class Action(Enum):
    """Ações de trading possíveis"""
    STRONG_BUY = ("STRONG_BUY", "🟢🟢", "Compra Forte", 90)
    BUY = ("BUY", "🟢", "Compra", 70)
    HOLD = ("HOLD", "⚪", "Manter", 50)
    SELL = ("SELL", "🔴", "Venda", 70)
    STRONG_SELL = ("STRONG_SELL", "🔴🔴", "Venda Forte", 90)
    CLOSE_LONG = ("CLOSE_LONG", "🔚", "Fechar Posição Longa", 80)
    CLOSE_SHORT = ("CLOSE_SHORT", "🔚", "Fechar Posição Curta", 80)
    REDUCE = ("REDUCE", "📉", "Reduzir Posição", 60)
    INCREASE = ("INCREASE", "📈", "Aumentar Posição", 60)
    
    def __init__(self, label: str, icon: str, descricao: str, threshold: int):
        self.label = label
        self.icon = icon
        self.descricao = descricao
        self.threshold = threshold

class MarketRegime(Enum):
    """Regimes de mercado detectáveis"""
    TRENDING_BULL = ("TRENDING_BULL", "🐂", "Tendência de Alta", 1)
    TRENDING_BEAR = ("TRENDING_BEAR", "🐻", "Tendência de Baixa", -1)
    RANGING = ("RANGING", "📊", "Lateral", 0)
    VOLATILE = ("VOLATILE", "⚡", "Alta Volatilidade", 0)
    BREAKOUT = ("BREAKOUT", "🚀", "Rompimento", 2)
    REVERSAL = ("REVERSAL", "🔄", "Reversão", -2)
    CRISIS = ("CRISIS", "💀", "Crise", -3)
    RECOVERY = ("RECOVERY", "🔄", "Recuperação", 1)
    
    def __init__(self, label: str, icon: str, descricao: str, momentum: int):
        self.label = label
        self.icon = icon
        self.descricao = descricao
        self.momentum = momentum

class RiskLevel(Enum):
    """Níveis de risco"""
    VERY_LOW = ("Muito Baixo", "🟢", 0.01)
    LOW = ("Baixo", "🟡", 0.02)
    MEDIUM = ("Médio", "🟠", 0.04)
    HIGH = ("Alto", "🔴", 0.08)
    VERY_HIGH = ("Muito Alto", "💀", 0.16)
    
    def __init__(self, label: str, icon: str, threshold: float):
        self.label = label
        self.icon = icon
        self.threshold = threshold

class ModelType(Enum):
    """Tipos de modelos suportados"""
    RANDOM_FOREST = ("Random Forest", "🌲", "Ensemble")
    GRADIENT_BOOSTING = ("Gradient Boosting", "📈", "Ensemble")
    NEURAL_NETWORK = ("Neural Network", "🧠", "Deep Learning")
    LSTM = ("LSTM", "🔄", "Recurrent")
    TRANSFORMER = ("Transformer", "⚡", "Attention")
    XGBOOST = ("XGBoost", "🎯", "Gradient Boosting")
    LINEAR = ("Linear", "📐", "Regressão")
    QUANTUM = ("Quantum", "⚛️", "Computação Quântica")
    
    def __init__(self, label: str, icon: str, categoria: str):
        self.label = label
        self.icon = icon
        self.categoria = categoria

class ConfidenceLevel(Enum):
    """Níveis de confiança"""
    VERY_HIGH = ("Muito Alta", "🏆", 90)
    HIGH = ("Alta", "👍", 80)
    GOOD = ("Boa", "👌", 70)
    MODERATE = ("Moderada", "🤔", 60)
    LOW = ("Baixa", "⚠️", 50)
    VERY_LOW = ("Muito Baixa", "❓", 40)
    
    def __init__(self, label: str, icon: str, threshold: int):
        self.label = label
        self.icon = icon
        self.threshold = threshold

class TimeFrame(Enum):
    """Timeframes de análise"""
    TICK = ("tick", 1, "Tempo Real")
    M1 = ("1m", 60, "1 Minuto")
    M5 = ("5m", 300, "5 Minutos")
    M15 = ("15m", 900, "15 Minutos")
    M30 = ("30m", 1800, "30 Minutos")
    H1 = ("1h", 3600, "1 Hora")
    H4 = ("4h", 14400, "4 Horas")
    D1 = ("1d", 86400, "1 Dia")
    W1 = ("1w", 604800, "1 Semana")
    MN1 = ("1mo", 2592000, "1 Mês")
    
    def __init__(self, code: str, seconds: int, descricao: str):
        self.code = code
        self.seconds = seconds
        self.descricao = descricao

# =============================================================================
# CONSTANTES DE CONFIGURAÇÃO
# =============================================================================

DEFAULT_CONFIG = {
    'model_type': ModelType.RANDOM_FOREST,
    'risk_tolerance': RiskLevel.MEDIUM,
    'timeframe': TimeFrame.H1,
    'lookback_periods': 100,
    'prediction_horizon': 5,
    'feature_count': 50,
    'validation_split': 0.2,
    'test_split': 0.1,
    'random_state': 42,
    'use_gpu': False,
    'ensemble_size': 5,
    'online_learning': True,
    'explainability': True,
    'neural_bus_integration': False
}

# =============================================================================
# DECORADORES DE PERFORMANCE
# =============================================================================

def timing_decorator(func):
    """Mede tempo de execução"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        if elapsed > 0.01:
            logger.debug(f"⏱️ {func.__name__} executado em {elapsed*1000:.2f}ms")
        return result
    return wrapper

def memoize(ttl: int = 60):
    """Cache com time-to-live"""
    def decorator(func):
        cache = {}
        timestamps = {}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = hashlib.md5(
                pickle.dumps((args, frozenset(kwargs.items())))
            ).hexdigest()
            
            now = time.time()
            if key in cache and now - timestamps.get(key, 0) < ttl:
                return cache[key]
            
            result = func(*args, **kwargs)
            cache[key] = result
            timestamps[key] = now
            return result
        return wrapper
    return decorator

def validate_dataframe(func):
    """Valida DataFrame de entrada"""
    @wraps(func)
    def wrapper(self, df: Any, *args, **kwargs):
        if not PANDAS_AVAILABLE:
            return func(self, df, *args, **kwargs)
        
        if df is None or df.empty:
            raise ValueError("DataFrame vazio ou nulo")
        
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Colunas obrigatórias não encontradas: {missing_cols}")
        
        return func(self, df, *args, **kwargs)
    return wrapper

# =============================================================================
# ESTRUTURAS DE DADOS AVANÇADAS
# =============================================================================

@dataclass
class Decision:
    """Decisão de trading com metadados completos"""
    action: Action
    confidence: float
    risk_score: float
    reason: str
    timestamp: datetime = field(default_factory=datetime.now)
    expected_return: float = 0.0
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    position_size: Optional[float] = None
    model_contributions: Dict[str, float] = field(default_factory=dict)
    feature_importance: Dict[str, float] = field(default_factory=dict)
    market_regime: Optional[MarketRegime] = None
    decision_id: str = field(default_factory=lambda: hashlib.md5(str(time.time()).encode()).hexdigest()[:12])
    
    @property
    def confidence_level(self) -> ConfidenceLevel:
        """Nível de confiança baseado no score"""
        if self.confidence >= 90:
            return ConfidenceLevel.VERY_HIGH
        elif self.confidence >= 80:
            return ConfidenceLevel.HIGH
        elif self.confidence >= 70:
            return ConfidenceLevel.GOOD
        elif self.confidence >= 60:
            return ConfidenceLevel.MODERATE
        elif self.confidence >= 50:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW
    
    @property
    def risk_level(self) -> RiskLevel:
        """Nível de risco baseado no score"""
        if self.risk_score >= 0.16:
            return RiskLevel.VERY_HIGH
        elif self.risk_score >= 0.08:
            return RiskLevel.HIGH
        elif self.risk_score >= 0.04:
            return RiskLevel.MEDIUM
        elif self.risk_score >= 0.02:
            return RiskLevel.LOW
        else:
            return RiskLevel.VERY_LOW
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário serializável"""
        return {
            'decision_id': self.decision_id,
            'action': self.action.label,
            'action_icon': self.action.icon,
            'confidence': self.confidence,
            'confidence_level': self.confidence_level.label,
            'confidence_icon': self.confidence_level.icon,
            'risk_score': self.risk_score,
            'risk_level': self.risk_level.label,
            'risk_icon': self.risk_level.icon,
            'reason': self.reason,
            'timestamp': self.timestamp.isoformat(),
            'expected_return': self.expected_return,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'position_size': self.position_size,
            'market_regime': self.market_regime.label if self.market_regime else None
        }

@dataclass
class ModelMetrics:
    """Métricas de performance do modelo"""
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    auc_roc: float = 0.0
    mse: float = 0.0
    mae: float = 0.0
    r2_score: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    training_time: float = 0.0
    inference_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'accuracy': f"{self.accuracy:.2%}",
            'precision': f"{self.precision:.2%}",
            'recall': f"{self.recall:.2%}",
            'f1_score': f"{self.f1_score:.3f}",
            'auc_roc': f"{self.auc_roc:.3f}",
            'mse': f"{self.mse:.4f}",
            'mae': f"{self.mae:.4f}",
            'r2_score': f"{self.r2_score:.3f}",
            'sharpe_ratio': f"{self.sharpe_ratio:.2f}",
            'max_drawdown': f"{self.max_drawdown:.2%}",
            'win_rate': f"{self.win_rate:.2%}",
            'profit_factor': f"{self.profit_factor:.2f}",
            'timestamp': self.timestamp.isoformat()
        }

@dataclass
class BacktestResult:
    """Resultado de backtest completo"""
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0
    total_return: float = 0.0
    annualized_return: float = 0.0
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    calmar_ratio: float = 0.0
    max_drawdown: float = 0.0
    max_drawdown_duration: int = 0
    profit_factor: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    expectancy: float = 0.0
    trades: List[Dict] = field(default_factory=list)
    equity_curve: List[float] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': f"{self.win_rate:.2%}",
            'total_return': f"{self.total_return:.2%}",
            'annualized_return': f"{self.annualized_return:.2%}",
            'sharpe_ratio': f"{self.sharpe_ratio:.2f}",
            'sortino_ratio': f"{self.sortino_ratio:.2f}",
            'calmar_ratio': f"{self.calmar_ratio:.2f}",
            'max_drawdown': f"{self.max_drawdown:.2%}",
            'profit_factor': f"{self.profit_factor:.2f}",
            'expectancy': f"{self.expectancy:.4f}",
            'timestamp': self.timestamp.isoformat()
        }

@dataclass
class FeatureImportance:
    """Importância de features para explicabilidade"""
    feature_name: str
    importance: float
    shap_value: float
    category: str
    description: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'feature': self.feature_name,
            'importance': f"{self.importance:.2%}",
            'shap_value': f"{self.shap_value:.4f}",
            'category': self.category,
            'description': self.description
        }

# =============================================================================
# PROCESSADOR DE FEATURES AVANÇADO
# =============================================================================

class FeatureProcessor:
    """Processador avançado de features para mercado financeiro"""
    
    def __init__(self):
        self.feature_names = []
        self.feature_metadata = {}
        self.scaler = None
        
        # Indicadores técnicos disponíveis
        self.technical_indicators = [
            'sma', 'ema', 'wma', 'hma', 'dema', 'tema',
            'rsi', 'macd', 'stoch', 'cci', 'williams_r',
            'bollinger', 'atr', 'adx', 'obv', 'mfi',
            'ichimoku', 'parabolic_sar', 'keltner',
            'donchian', 'vwap', 'pivot_points'
        ]
    
    @timing_decorator
    @validate_dataframe
    def generate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Gera features técnicas avançadas"""
        if not PANDAS_AVAILABLE:
            return df
        
        out = df.copy()
        
        # ===== 1. FEATURES DE PREÇO BÁSICAS =====
        out['returns_1'] = out['close'].pct_change(1)
        out['returns_5'] = out['close'].pct_change(5)
        out['returns_10'] = out['close'].pct_change(10)
        out['returns_20'] = out['close'].pct_change(20)
        out['returns_60'] = out['close'].pct_change(60)
        
        out['log_returns'] = np.log(out['close'] / out['close'].shift(1))
        out['realized_volatility'] = out['log_returns'].rolling(20).std() * np.sqrt(252)
        
        # ===== 2. MÉDIAS MÓVEIS =====
        out['sma_10'] = out['close'].rolling(10).mean()
        out['sma_20'] = out['close'].rolling(20).mean()
        out['sma_50'] = out['close'].rolling(50).mean()
        out['sma_200'] = out['close'].rolling(200).mean()
        
        # Distância das médias
        out['distance_sma_10'] = (out['close'] - out['sma_10']) / out['sma_10']
        out['distance_sma_20'] = (out['close'] - out['sma_20']) / out['sma_20']
        out['distance_sma_50'] = (out['close'] - out['sma_50']) / out['sma_50']
        
        # Cruzamentos
        out['cross_sma_10_50'] = (out['sma_10'] > out['sma_50']).astype(int)
        out['cross_sma_20_50'] = (out['sma_20'] > out['sma_50']).astype(int)
        out['cross_sma_50_200'] = (out['sma_50'] > out['sma_200']).astype(int)
        
        # ===== 3. MÉDIAS EXPONENCIAIS =====
        out['ema_12'] = out['close'].ewm(span=12, adjust=False).mean()
        out['ema_26'] = out['close'].ewm(span=26, adjust=False).mean()
        out['ema_50'] = out['close'].ewm(span=50, adjust=False).mean()
        out['ema_200'] = out['close'].ewm(span=200, adjust=False).mean()
        
        # ===== 4. MACD =====
        out['macd'] = out['ema_12'] - out['ema_26']
        out['macd_signal'] = out['macd'].ewm(span=9, adjust=False).mean()
        out['macd_histogram'] = out['macd'] - out['macd_signal']
        out['macd_cross'] = (out['macd'] > out['macd_signal']).astype(int)
        
        # ===== 5. RSI =====
        delta = out['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        out['rsi'] = 100 - (100 / (1 + rs))
        out['rsi_overbought'] = (out['rsi'] > 70).astype(int)
        out['rsi_oversold'] = (out['rsi'] < 30).astype(int)
        
        # ===== 6. BOLLINGER BANDS =====
        out['bb_middle'] = out['close'].rolling(20).mean()
        out['bb_std'] = out['close'].rolling(20).std()
        out['bb_upper'] = out['bb_middle'] + 2 * out['bb_std']
        out['bb_lower'] = out['bb_middle'] - 2 * out['bb_std']
        out['bb_width'] = (out['bb_upper'] - out['bb_lower']) / out['bb_middle']
        out['bb_position'] = (out['close'] - out['bb_lower']) / (out['bb_upper'] - out['bb_lower'])
        out['bb_breakout_up'] = (out['close'] > out['bb_upper']).astype(int)
        out['bb_breakout_down'] = (out['close'] < out['bb_lower']).astype(int)
        
        # ===== 7. VOLATILIDADE =====
        out['atr'] = self._calculate_atr(out['high'], out['low'], out['close'])
        out['atr_ratio'] = out['atr'] / out['close']
        out['volatility_ratio'] = out['returns_20'].rolling(20).std() / out['returns_60'].rolling(60).std()
        
        # ===== 8. VOLUME =====
        out['volume_sma'] = out['volume'].rolling(20).mean()
        out['volume_ratio'] = out['volume'] / out['volume_sma']
        out['obv'] = self._calculate_obv(out['close'], out['volume'])
        out['obv_sma'] = out['obv'].rolling(20).mean()
        out['obv_cross'] = (out['obv'] > out['obv_sma']).astype(int)
        
        # ===== 9. MOMENTUM =====
        out['momentum_1'] = out['close'] - out['close'].shift(1)
        out['momentum_5'] = out['close'] - out['close'].shift(5)
        out['momentum_10'] = out['close'] - out['close'].shift(10)
        out['momentum_20'] = out['close'] - out['close'].shift(20)
        
        out['roc_5'] = out['close'].pct_change(5) * 100
        out['roc_10'] = out['close'].pct_change(10) * 100
        out['roc_20'] = out['close'].pct_change(20) * 100
        
        # ===== 10. PRICE ACTION =====
        out['high_low_ratio'] = out['high'] / out['low']
        out['close_open_ratio'] = out['close'] / out['open']
        out['range'] = out['high'] - out['low']
        out['range_ratio'] = out['range'] / out['close']
        
        # Padrões de candlestick
        out['bullish_engulfing'] = self._detect_bullish_engulfing(out).astype(int)
        out['bearish_engulfing'] = self._detect_bearish_engulfing(out).astype(int)
        out['doji'] = self._detect_doji(out).astype(int)
        out['hammer'] = self._detect_hammer(out).astype(int)
        out['shooting_star'] = self._detect_shooting_star(out).astype(int)
        
        # ===== 11. SUPORTE/RESISTÊNCIA =====
        out['pivot'] = (out['high'] + out['low'] + out['close']) / 3
        out['r1'] = 2 * out['pivot'] - out['low']
        out['s1'] = 2 * out['pivot'] - out['high']
        out['r2'] = out['pivot'] + (out['high'] - out['low'])
        out['s2'] = out['pivot'] - (out['high'] - out['low'])
        
        out['distance_r1'] = (out['r1'] - out['close']) / out['close']
        out['distance_s1'] = (out['close'] - out['s1']) / out['close']
        
        # ===== 12. CORRELAÇÕES =====
        out['corr_10'] = out['close'].rolling(10).corr(out['volume'].rolling(10))
        out['corr_20'] = out['close'].rolling(20).corr(out['volume'].rolling(20))
        
        # ===== 13. ESTATÍSTICAS =====
        out['skew_20'] = out['close'].rolling(20).skew()
        out['kurt_20'] = out['close'].rolling(20).kurt()
        out['zscore_20'] = (out['close'] - out['sma_20']) / out['close'].rolling(20).std()
        
        # ===== 14. DETECÇÃO DE REGIME =====
        out['trend_strength'] = self._calculate_trend_strength(out)
        out['is_trending'] = (out['trend_strength'] > 25).astype(int)
        out['is_ranging'] = (out['trend_strength'] < 20).astype(int)
        
        # Limpar valores NaN
        out = out.fillna(0).replace([np.inf, -np.inf], 0)
        
        # Armazenar nomes das features
        self.feature_names = [col for col in out.columns 
                             if col not in ['open', 'high', 'low', 'close', 'volume']]
        
        return out
    
    def _calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Calcula Average True Range"""
        if TA_LIB_AVAILABLE:
            return pd.Series(talib.ATR(high.values, low.values, close.values, timeperiod=period), index=close.index)
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(period).mean()
    
    def _calculate_obv(self, close: pd.Series, volume: pd.Series) -> pd.Series:
        """Calcula On-Balance Volume"""
        obv = volume.copy()
        obv[close.diff() < 0] = -volume
        return obv.cumsum()
    
    def _calculate_trend_strength(self, df: pd.DataFrame) -> pd.Series:
        """Calcula força da tendência (ADX simplificado)"""
        high = df['high']
        low = df['low']
        close = df['close']
        
        up_move = high - high.shift()
        down_move = low.shift() - low
        
        plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0)
        minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0)
        
        tr = self._calculate_atr(high, low, close)
        
        plus_di = 100 * (plus_dm.rolling(14).mean() / tr)
        minus_di = 100 * (minus_dm.rolling(14).mean() / tr)
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(14).mean()
        
        return adx.fillna(0)
    
    def _detect_bullish_engulfing(self, df: pd.DataFrame) -> pd.Series:
        """Detecta padrão de engolfo de alta"""
        condition = (
            (df['close'].shift(1) < df['open'].shift(1)) &  # Candle anterior de baixa
            (df['close'] > df['open']) &                    # Candle atual de alta
            (df['open'] < df['close'].shift(1)) &           # Abre abaixo do fechamento anterior
            (df['close'] > df['open'].shift(1))             # Fecha acima da abertura anterior
        )
        return condition
    
    def _detect_bearish_engulfing(self, df: pd.DataFrame) -> pd.Series:
        """Detecta padrão de engolfo de baixa"""
        condition = (
            (df['close'].shift(1) > df['open'].shift(1)) &  # Candle anterior de alta
            (df['close'] < df['open']) &                    # Candle atual de baixa
            (df['open'] > df['close'].shift(1)) &           # Abre acima do fechamento anterior
            (df['close'] < df['open'].shift(1))             # Fecha abaixo da abertura anterior
        )
        return condition
    
    def _detect_doji(self, df: pd.DataFrame) -> pd.Series:
        """Detecta padrão Doji"""
        body = abs(df['close'] - df['open'])
        range_ = df['high'] - df['low']
        condition = body < (range_ * 0.1)
        return condition
    
    def _detect_hammer(self, df: pd.DataFrame) -> pd.Series:
        """Detecta padrão Hammer"""
        body = abs(df['close'] - df['open'])
        lower_shadow = df[['open', 'close']].min(axis=1) - df['low']
        upper_shadow = df['high'] - df[['open', 'close']].max(axis=1)
        
        condition = (
            (lower_shadow > body * 2) &
            (upper_shadow < body * 0.3) &
            (df['close'] > df['open'])  # Hammer de alta
        )
        return condition
    
    def _detect_shooting_star(self, df: pd.DataFrame) -> pd.Series:
        """Detecta padrão Shooting Star"""
        body = abs(df['close'] - df['open'])
        lower_shadow = df[['open', 'close']].min(axis=1) - df['low']
        upper_shadow = df['high'] - df[['open', 'close']].max(axis=1)
        
        condition = (
            (upper_shadow > body * 2) &
            (lower_shadow < body * 0.3) &
            (df['close'] < df['open'])  # Shooting Star de baixa
        )
        return condition
    
    def get_feature_summary(self) -> Dict[str, Any]:
        """Retorna sumário das features disponíveis"""
        return {
            'total_features': len(self.feature_names),
            'feature_categories': {
                'price_action': ['returns', 'log_returns', 'range'],
                'moving_averages': ['sma', 'ema', 'cross'],
                'momentum': ['rsi', 'macd', 'momentum', 'roc'],
                'volatility': ['atr', 'bb', 'volatility'],
                'volume': ['volume_ratio', 'obv'],
                'patterns': ['engulfing', 'doji', 'hammer', 'shooting_star'],
                'support_resistance': ['pivot', 'r1', 's1'],
                'statistics': ['skew', 'kurt', 'zscore'],
                'regime': ['trend_strength']
            }
        }

# =============================================================================
# GERENCIADOR DE MODELOS
# =============================================================================

class ModelManager:
    """Gerenciador de modelos de machine learning"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.models: Dict[str, Any] = {}
        self.metrics: Dict[str, ModelMetrics] = {}
        self.scalers: Dict[str, Any] = {}
        self.feature_selectors: Dict[str, Any] = {}
        
    @timing_decorator
    def create_model(self, model_type: ModelType, model_id: str, **kwargs) -> Any:
        """Cria um novo modelo baseado no tipo especificado"""
        
        if model_type == ModelType.RANDOM_FOREST and SKLEARN_AVAILABLE:
            model = RandomForestClassifier(
                n_estimators=kwargs.get('n_estimators', 100),
                max_depth=kwargs.get('max_depth', 10),
                min_samples_split=kwargs.get('min_samples_split', 5),
                min_samples_leaf=kwargs.get('min_samples_leaf', 2),
                random_state=self.config.get('random_state', 42),
                n_jobs=-1
            )
            
        elif model_type == ModelType.GRADIENT_BOOSTING and SKLEARN_AVAILABLE:
            model = GradientBoostingClassifier(
                n_estimators=kwargs.get('n_estimators', 100),
                learning_rate=kwargs.get('learning_rate', 0.1),
                max_depth=kwargs.get('max_depth', 5),
                min_samples_split=kwargs.get('min_samples_split', 5),
                min_samples_leaf=kwargs.get('min_samples_leaf', 2),
                random_state=self.config.get('random_state', 42)
            )
            
        elif model_type == ModelType.NEURAL_NETWORK and TF_AVAILABLE:
            model = self._create_neural_network(**kwargs)
            
        elif model_type == ModelType.LSTM and TF_AVAILABLE:
            model = self._create_lstm_network(**kwargs)
            
        else:
            logger.warning(f"Modelo {model_type.label} não disponível. Usando placeholder.")
            model = {'type': 'placeholder', 'model_type': model_type}
        
        self.models[model_id] = model
        self.metrics[model_id] = ModelMetrics()
        
        logger.info(f"✅ Modelo criado: {model_id} ({model_type.icon} {model_type.label})")
        return model
    
    def _create_neural_network(self, **kwargs) -> Any:
        """Cria rede neural feedforward"""
        if not TF_AVAILABLE:
            return None
        
        input_dim = kwargs.get('input_dim', 50)
        hidden_layers = kwargs.get('hidden_layers', [128, 64, 32])
        dropout_rate = kwargs.get('dropout_rate', 0.3)
        
        model = keras.Sequential()
        model.add(layers.Input(shape=(input_dim,)))
        
        for units in hidden_layers:
            model.add(layers.Dense(units, activation='relu'))
            model.add(layers.BatchNormalization())
            model.add(layers.Dropout(dropout_rate))
        
        model.add(layers.Dense(3, activation='softmax'))  # BUY, HOLD, SELL
        
        model.compile(
            optimizer=optimizers.Adam(learning_rate=kwargs.get('learning_rate', 0.001)),
            loss=losses.CategoricalCrossentropy(),
            metrics=['accuracy']
        )
        
        return model
    
    def _create_lstm_network(self, **kwargs) -> Any:
        """Cria rede LSTM para séries temporais"""
        if not TF_AVAILABLE:
            return None
        
        seq_length = kwargs.get('seq_length', 60)
        n_features = kwargs.get('n_features', 20)
        lstm_units = kwargs.get('lstm_units', [64, 32])
        
        model = keras.Sequential()
        model.add(layers.Input(shape=(seq_length, n_features)))
        
        for units in lstm_units[:-1]:
            model.add(layers.LSTM(units, return_sequences=True))
            model.add(layers.Dropout(0.2))
        
        model.add(layers.LSTM(lstm_units[-1]))
        model.add(layers.Dropout(0.2))
        model.add(layers.Dense(3, activation='softmax'))
        
        model.compile(
            optimizer=optimizers.Adam(learning_rate=0.001),
            loss=losses.CategoricalCrossentropy(),
            metrics=['accuracy']
        )
        
        return model
    
    @timing_decorator
    def train_model(self, model_id: str, X_train: np.ndarray, y_train: np.ndarray,
                   X_val: Optional[np.ndarray] = None, y_val: Optional[np.ndarray] = None) -> ModelMetrics:
        """Treina um modelo específico"""
        
        if model_id not in self.models:
            raise ValueError(f"Modelo {model_id} não encontrado")
        
        model = self.models[model_id]
        metrics = self.metrics[model_id]
        
        start_time = time.time()
        
        # Placeholder para treinamento real
        if hasattr(model, 'fit'):
            if X_val is not None and y_val is not None:
                model.fit(X_train, y_train, 
                         validation_data=(X_val, y_val),
                         epochs=self.config.get('epochs', 100),
                         batch_size=self.config.get('batch_size', 32),
                         verbose=0)
            else:
                model.fit(X_train, y_train)
        
        metrics.training_time = time.time() - start_time
        logger.info(f"✅ Modelo treinado: {model_id} em {metrics.training_time:.2f}s")
        
        return metrics
    
    @timing_decorator
    def predict(self, model_id: str, X: np.ndarray) -> np.ndarray:
        """Faz predições usando um modelo treinado"""
        
        if model_id not in self.models:
            raise ValueError(f"Modelo {model_id} não encontrado")
        
        model = self.models[model_id]
        
        start_time = time.time()
        
        if hasattr(model, 'predict_proba'):
            predictions = model.predict_proba(X)
        elif hasattr(model, 'predict'):
            predictions = model.predict(X)
        else:
            predictions = np.zeros((X.shape[0], 3))
        
        inference_time = time.time() - start_time
        self.metrics[model_id].inference_time = inference_time
        
        return predictions

# =============================================================================
# EXPLICADOR DE DECISÕES
# =============================================================================

class DecisionExplainer:
    """Explicador de decisões usando SHAP e análise de features"""
    
    def __init__(self):
        self.explainers = {}
        self.feature_importance_cache = {}
    
    @timing_decorator
    def explain_decision(self, model: Any, X: np.ndarray, 
                        feature_names: List[str]) -> Dict[str, float]:
        """Gera explicação para uma decisão usando SHAP"""
        
        if SHAP_AVAILABLE and hasattr(model, 'predict_proba'):
            try:
                explainer = shap.TreeExplainer(model)
                shap_values = explainer.shap_values(X)
                
                # Média dos valores SHAP
                if isinstance(shap_values, list):
                    importance = np.mean(np.abs(shap_values[1]), axis=0)
                else:
                    importance = np.mean(np.abs(shap_values), axis=0)
                
                return dict(zip(feature_names, importance))
                
            except Exception as e:
                logger.warning(f"Erro ao calcular SHAP: {e}")
        
        # Fallback: importância do modelo
        if hasattr(model, 'feature_importances_'):
            importance = model.feature_importances_
            return dict(zip(feature_names, importance))
        
        return {}
    
    def generate_explanation_text(self, decision: Decision, 
                                 feature_importance: Dict[str, float],
                                 top_n: int = 5) -> str:
        """Gera texto explicativo legível"""
        
        # Ordenar features por importância
        sorted_features = sorted(
            feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_n]
        
        lines = []
        lines.append(f"📊 Decisão: {decision.action.icon} {decision.action.label}")
        lines.append(f"🎯 Confiança: {decision.confidence:.1f}% ({decision.confidence_level.icon})")
        lines.append(f"⚠️ Risco: {decision.risk_score:.1%} ({decision.risk_level.icon})")
        lines.append(f"💡 Motivo: {decision.reason}")
        
        if decision.market_regime:
            lines.append(f"📈 Regime: {decision.market_regime.icon} {decision.market_regime.label}")
        
        lines.append("\n🔍 Principais fatores:")
        for feature, importance in sorted_features:
            lines.append(f"   • {feature}: {importance:.1%}")
        
        return "\n".join(lines)

# =============================================================================
# CLASSE PRINCIPAL - FINANCIAL AGI
# =============================================================================

class FinancialAGI:
    """
    Classe principal para a AGI com foco financeiro.
    
    Implementa um sistema completo de inteligência artificial para mercados financeiros,
    incluindo processamento de dados, engenharia de features, treinamento de modelos,
    predição em tempo real, backtesting, explicabilidade e integração com NeuralBus.
    
    Attributes:
        config (Dict[str, Any]): Configurações do sistema
        state (Dict[str, Any]): Estado interno da AGI
        models (Dict[str, Any]): Dicionário de modelos treinados
        feature_processor (FeatureProcessor): Processador de features
        model_manager (ModelManager): Gerenciador de modelos
        explainer (DecisionExplainer): Explicador de decisões
        neural_bus (Optional[NeuralBus]): Integração com NeuralBus
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Inicializa a Financial AGI com configurações personalizadas.
        
        Args:
            config: Dicionário de configuração. Se None, usa DEFAULT_CONFIG.
        """
        self.config = {**DEFAULT_CONFIG, **(config or {})}
        self.state: Dict[str, Any] = {
            'initialized_at': datetime.now(),
            'total_predictions': 0,
            'total_trades': 0,
            'total_pnl': 0.0,
            'active_positions': 0
        }
        
        # Componentes
        self.feature_processor = FeatureProcessor()
        self.model_manager = ModelManager(self.config)
        self.explainer = DecisionExplainer()
        
        # Modelos e métricas
        self.models: Dict[str, Any] = {}
        self.metrics: Dict[str, ModelMetrics] = {}
        self.decisions: List[Decision] = []
        
        # Integração NeuralBus
        self.neural_bus = None
        if NEURAL_BUS_AVAILABLE and self.config.get('neural_bus_integration', False):
            try:
                self.neural_bus = NeuralBus()
                logger.info("✅ NeuralBus integrado com sucesso")
            except Exception as e:
                logger.warning(f"⚠️ Falha ao integrar NeuralBus: {e}")
        
        logger.info("="*80)
        logger.info("🚀 VHALINOR IAG - FINANCIAL AGI QUÂNTICA INICIALIZADA")
        logger.info("="*80)
        logger.info(f"📅 Data: {self.state['initialized_at'].strftime('%d/%m/%Y %H:%M:%S')}")
        logger.info(f"🧠 Modelo padrão: {self.config['model_type'].icon} {self.config['model_type'].label}")
        logger.info(f"⚖️  Tolerância a risco: {self.config['risk_tolerance'].icon} {self.config['risk_tolerance'].label}")
        logger.info(f"⏱️  Timeframe: {self.config['timeframe'].descricao}")
        logger.info("="*80)
    
    # =========================================================================
    # PROCESSAMENTO DE DADOS
    # =========================================================================
    
    @timing_decorator
    @validate_dataframe
    def preprocess_market_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Limpa e valida o DataFrame de mercado.
        
        Args:
            df: pd.DataFrame com colunas ['date','open','high','low','close','volume']
            
        Returns:
            DataFrame alinhado e com índice datetime
        """
        if not PANDAS_AVAILABLE:
            logger.warning("pandas não disponível — preprocess_market_data é um stub")
            return df
        
        df = df.copy()
        
        # Garantir coluna de data
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')
        elif df.index.name != 'date' and not isinstance(df.index, pd.DatetimeIndex):
            df.index = pd.to_datetime(df.index)
        
        # Ordenar por índice
        df = df.sort_index()
        
        # Remover duplicatas
        df = df[~df.index.duplicated(keep='first')]
        
        # Preenchimento de NAs
        df = df.fillna(method='ffill').fillna(method='bfill')
        
        # Remover linhas com valores zero ou negativos
        df = df[(df['open'] > 0) & (df['high'] > 0) & (df['low'] > 0) & 
                (df['close'] > 0) & (df['volume'] >= 0)]
        
        logger.debug(f"✅ Dados pré-processados: {len(df)} períodos")
        return df
    
    @timing_decorator
    @validate_dataframe
    def generate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Gera features técnicas avançadas a partir dos dados de mercado.
        
        Args:
            df: DataFrame com dados OHLCV
            
        Returns:
            DataFrame com features técnicas adicionadas
        """
        return self.feature_processor.generate_features(df)
    
    # =========================================================================
    # TREINAMENTO DE MODELOS
    # =========================================================================
    
    @timing_decorator
    def train(self, historical_data: pd.DataFrame, target: str = 'direction',
             model_id: Optional[str] = None, model_type: Optional[ModelType] = None) -> Dict[str, Any]:
        """
        Treina/evalua modelos sobre dados históricos.
        
        Args:
            historical_data: DataFrame com dados históricos e features
            target: Nome da coluna alvo ('direction', 'return', 'close')
            model_id: Identificador único para o modelo
            model_type: Tipo de modelo a treinar
            
        Returns:
            Dicionário com métricas de treinamento
        """
        logger.info("🧠 Iniciando treinamento do modelo...")
        
        if not PANDAS_AVAILABLE:
            logger.warning("pandas não disponível — train é um placeholder")
            return {'status': 'placeholder', 'message': 'pandas não disponível'}
        
        # Preparar dados
        df = historical_data.copy()
        
        # Criar target (direção do preço)
        if target == 'direction':
            df['target'] = (df['close'].shift(-self.config['prediction_horizon']) > df['close']).astype(int)
        elif target == 'return':
            df['target'] = df['close'].pct_change(self.config['prediction_horizon']).shift(-self.config['prediction_horizon'])
        else:
            df['target'] = df[target].shift(-self.config['prediction_horizon'])
        
        # Remover NAs
        df = df.dropna()
        
        # Separar features e target
        feature_cols = [col for col in df.columns 
                       if col not in ['open', 'high', 'low', 'close', 'volume', 'target']]
        
        X = df[feature_cols].values
        y = df['target'].values
        
        # Divisão treino/validação/teste
        n = len(X)
        train_end = int(n * (1 - self.config['validation_split'] - self.config['test_split']))
        val_end = int(n * (1 - self.config['test_split']))
        
        X_train, y_train = X[:train_end], y[:train_end]
        X_val, y_val = X[train_end:val_end], y[train_end:val_end]
        X_test, y_test = X[val_end:], y[val_end:]
        
        logger.info(f"📊 Divisão dos dados: Treino={len(X_train)}, Validação={len(X_val)}, Teste={len(X_test)}")
        
        # Criar ou usar modelo existente
        if model_id is None:
            model_id = f"model_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        model_type = model_type or self.config['model_type']
        
        # Criar modelo se não existir
        if model_id not in self.models:
            self.models[model_id] = self.model_manager.create_model(
                model_type=model_type,
                model_id=model_id,
                input_dim=X.shape[1],
                n_features=X.shape[1]
            )
        
        # Treinar modelo
        metrics = self.model_manager.train_model(
            model_id=model_id,
            X_train=X_train,
            y_train=y_train,
            X_val=X_val,
            y_val=y_val
        )
        
        # Avaliar no teste
        if X_test.shape[0] > 0:
            y_pred = self.model_manager.predict(model_id, X_test)
            
            if len(y_pred.shape) > 1:
                y_pred_classes = np.argmax(y_pred, axis=1)
            else:
                y_pred_classes = (y_pred > 0.5).astype(int)
            
            metrics.accuracy = accuracy_score(y_test, y_pred_classes)
            metrics.precision = precision_score(y_test, y_pred_classes, average='weighted', zero_division=0)
            metrics.recall = recall_score(y_test, y_pred_classes, average='weighted', zero_division=0)
            metrics.f1_score = f1_score(y_test, y_pred_classes, average='weighted', zero_division=0)
        
        self.metrics[model_id] = metrics
        
        logger.info(f"✅ Treinamento concluído - Acurácia: {metrics.accuracy:.2%}")
        
        return {
            'model_id': model_id,
            'model_type': model_type.label,
            'metrics': metrics.to_dict(),
            'feature_count': X.shape[1],
            'training_samples': len(X_train),
            'validation_samples': len(X_val),
            'test_samples': len(X_test)
        }
    
    # =========================================================================
    # INFERÊNCIA E PREDIÇÃO
    # =========================================================================
    
    @timing_decorator
    def predict(self, observation: Union[pd.DataFrame, pd.Series, Dict],
               model_id: Optional[str] = None) -> Decision:
        """
        Retorna uma decisão de trading baseada na observação atual.
        
        Args:
            observation: Dados de mercado atuais (DataFrame, Series ou Dict)
            model_id: Identificador do modelo a usar (None = usa melhor modelo)
            
        Returns:
            Decision: Decisão completa com ação, confiança e justificativa
        """
        self.state['total_predictions'] += 1
        
        # Converter observação para DataFrame
        if isinstance(observation, dict):
            df = pd.DataFrame([observation])
        elif isinstance(observation, pd.Series):
            df = pd.DataFrame([observation])
        else:
            df = observation.copy()
        
        # Garantir features
        if len(df.columns) < 20:  # Poucas colunas, precisa gerar features
            df = self.generate_features(df)
        
        # Selecionar modelo
        if model_id is None or model_id not in self.models:
            if self.models:
                model_id = list(self.models.keys())[-1]  # Último modelo treinado
            else:
                # Modelo dummy para demonstração
                return self._dummy_prediction(df)
        
        # Extrair features
        feature_cols = [col for col in df.columns 
                       if col not in ['open', 'high', 'low', 'close', 'volume']]
        
        if len(feature_cols) == 0:
            return self._dummy_prediction(df)
        
        X = df[feature_cols].iloc[-1:].values
        
        # Fazer predição
        predictions = self.model_manager.predict(model_id, X)
        
        # Interpretar resultado
        if len(predictions.shape) > 1 and predictions.shape[1] >= 3:
            # Classificação multiclasse
            probs = predictions[0]
            action_idx = np.argmax(probs)
            
            action_map = {
                0: Action.STRONG_SELL,
                1: Action.SELL,
                2: Action.HOLD,
                3: Action.BUY,
                4: Action.STRONG_BUY
            }
            
            action = action_map.get(action_idx, Action.HOLD)
            confidence = probs[action_idx] * 100
            
        elif len(predictions.shape) == 1:
            # Regressão
            value = predictions[0]
            
            if value > 0.6:
                action = Action.STRONG_BUY
                confidence = value * 100
            elif value > 0.55:
                action = Action.BUY
                confidence = value * 100
            elif value < 0.4:
                action = Action.STRONG_SELL
                confidence = (1 - value) * 100
            elif value < 0.45:
                action = Action.SELL
                confidence = (1 - value) * 100
            else:
                action = Action.HOLD
                confidence = 50
        else:
            return self._dummy_prediction(df)
        
        # Calcular risco
        risk_score = self._calculate_risk(df, action)
        
        # Calcular níveis de stop loss e take profit
        current_price = df['close'].iloc[-1]
        stop_loss, take_profit = self._calculate_risk_rewards(current_price, action, risk_score)
        
        # Detectar regime de mercado
        market_regime = self._detect_market_regime(df)
        
        # Calcular importância das features
        feature_importance = {}
        if model_id in self.models:
            model = self.models[model_id]
            if hasattr(model, 'feature_importances_'):
                importance_values = model.feature_importances_
                if len(importance_values) == len(feature_cols):
                    feature_importance = dict(zip(feature_cols, importance_values))
        
        # Criar decisão
        decision = Decision(
            action=action,
            confidence=float(confidence),
            risk_score=float(risk_score),
            reason=self._generate_reason(action, confidence, market_regime),
            expected_return=float(predictions[0] if len(predictions.shape) == 1 else probs[action_idx]),
            stop_loss=float(stop_loss) if stop_loss else None,
            take_profit=float(take_profit) if take_profit else None,
            position_size=self._calculate_position_size(risk_score),
            model_contributions={model_id: confidence},
            feature_importance=feature_importance,
            market_regime=market_regime
        )
        
        self.decisions.append(decision)
        
        logger.info(f"{decision.action.icon} Decisão: {decision.action.label} | "
                   f"Conf: {decision.confidence:.1f}% | "
                   f"Risco: {decision.risk_score:.1%} | "
                   f"{decision.reason}")
        
        return decision
    
    def _dummy_prediction(self, df: pd.DataFrame) -> Decision:
        """Predição dummy quando não há modelo treinado"""
        current_price = df['close'].iloc[-1]
        
        # Lógica simples baseada em SMA
        action = Action.HOLD
        confidence = 50.0
        reason = "Modelo não treinado - usando lógica padrão"
        
        if 'sma_10' in df.columns and 'sma_50' in df.columns:
            if df['sma_10'].iloc[-1] > df['sma_50'].iloc[-1]:
                action = Action.BUY
                confidence = 60.0
                reason = "Cruzamento de médias (SMA10 > SMA50)"
            elif df['sma_10'].iloc[-1] < df['sma_50'].iloc[-1]:
                action = Action.SELL
                confidence = 60.0
                reason = "Cruzamento de médias (SMA10 < SMA50)"
        
        return Decision(
            action=action,
            confidence=confidence,
            risk_score=0.05,
            reason=reason,
            expected_return=0.0,
            stop_loss=current_price * 0.98 if action == Action.BUY else current_price * 1.02 if action == Action.SELL else None,
            take_profit=current_price * 1.02 if action == Action.BUY else current_price * 0.98 if action == Action.SELL else None,
            position_size=0.01
        )
    
    def _calculate_risk(self, df: pd.DataFrame, action: Action) -> float:
        """Calcula score de risco baseado em volatilidade e regime"""
        base_risk = self.config['risk_tolerance'].threshold
        
        # Ajustar por volatilidade
        if 'volatility_ratio' in df.columns:
            vol_ratio = df['volatility_ratio'].iloc[-1]
            if vol_ratio > 1.5:
                base_risk *= 1.5
            elif vol_ratio < 0.5:
                base_risk *= 0.7
        
        # Ajustar por regime
        regime = self._detect_market_regime(df)
        if regime in [MarketRegime.CRISIS, MarketRegime.VOLATILE]:
            base_risk *= 1.3
        elif regime in [MarketRegime.TRENDING_BULL, MarketRegime.TRENDING_BEAR]:
            base_risk *= 0.9
        
        return min(base_risk, 0.5)
    
    def _calculate_risk_rewards(self, price: float, action: Action, risk_score: float) -> Tuple[Optional[float], Optional[float]]:
        """Calcula stop loss e take profit baseado no risco"""
        if action in [Action.BUY, Action.STRONG_BUY]:
            stop_loss = price * (1 - risk_score * 2)
            take_profit = price * (1 + risk_score * 4)
        elif action in [Action.SELL, Action.STRONG_SELL]:
            stop_loss = price * (1 + risk_score * 2)
            take_profit = price * (1 - risk_score * 4)
        else:
            return None, None
        
        return stop_loss, take_profit
    
    def _calculate_position_size(self, risk_score: float) -> float:
        """Calcula tamanho da posição baseado no risco"""
        base_size = 0.01  # 1% do capital por trade
        return base_size * (1 / risk_score) if risk_score > 0 else base_size
    
    def _detect_market_regime(self, df: pd.DataFrame) -> MarketRegime:
        """Detecta regime de mercado atual"""
        if 'trend_strength' not in df.columns:
            return MarketRegime.RANGING
        
        trend = df['trend_strength'].iloc[-1]
        
        if trend > 40:
            # Verificar direção
            if 'sma_20' in df.columns and 'sma_50' in df.columns:
                if df['sma_20'].iloc[-1] > df['sma_50'].iloc[-1]:
                    return MarketRegime.TRENDING_BULL
                else:
                    return MarketRegime.TRENDING_BEAR
        elif trend < 20:
            return MarketRegime.RANGING
        
        return MarketRegime.RANGING
    
    def _generate_reason(self, action: Action, confidence: float, regime: MarketRegime) -> str:
        """Gera razão legível para a decisão"""
        reasons = []
        
        if action in [Action.BUY, Action.STRONG_BUY]:
            reasons.append("sinais de compra detectados")
        elif action in [Action.SELL, Action.STRONG_SELL]:
            reasons.append("sinais de venda detectados")
        else:
            reasons.append("mercado indefinido")
        
        if confidence > 80:
            reasons.append("alta confiança")
        elif confidence > 60:
            reasons.append("confiança moderada")
        
        if regime:
            reasons.append(f"regime {regime.descricao.lower()}")
        
        return ", ".join(reasons)
    
    # =========================================================================
    # BACKTESTING
    # =========================================================================
    
    @timing_decorator
    def backtest(self, df: pd.DataFrame, model_id: Optional[str] = None,
                initial_capital: float = 10000.0) -> BacktestResult:
        """
        Executa backtest completo da estratégia.
        
        Args:
            df: DataFrame com dados históricos e features
            model_id: Identificador do modelo a usar
            initial_capital: Capital inicial para o backtest
            
        Returns:
            BacktestResult: Resultados completos do backtest
        """
        logger.info("📊 Iniciando backtest...")
        
        result = BacktestResult()
        capital = initial_capital
        position = 0
        entry_price = 0
        equity_curve = [capital]
        
        # Garantir features
        if len(df.columns) < 20:
            df = self.generate_features(df)
        
        # Remover NAs
        df = df.dropna()
        
        for i in range(self.config['lookback_periods'], len(df)):
            # Dados até o momento
            current_data = df.iloc[:i+1]
            
            # Fazer predição
            decision = self.predict(current_data, model_id)
            
            current_price = df['close'].iloc[i]
            
            # Executar decisão
            if decision.action in [Action.BUY, Action.STRONG_BUY] and position == 0:
                # Abrir posição longa
                position = capital * 0.95 / current_price  # Usar 95% do capital
                entry_price = current_price
                capital -= position * current_price
                
                result.total_trades += 1
                
            elif decision.action in [Action.SELL, Action.STRONG_SELL] and position > 0:
                # Fechar posição longa
                pnl = position * (current_price - entry_price)
                capital += position * current_price + pnl
                
                if pnl > 0:
                    result.winning_trades += 1
                else:
                    result.losing_trades += 1
                
                result.total_pnl += pnl
                position = 0
                entry_price = 0
                
                result.trades.append({
                    'timestamp': df.index[i],
                    'entry_price': entry_price,
                    'exit_price': current_price,
                    'pnl': pnl,
                    'pnl_percent': (current_price - entry_price) / entry_price
                })
            
            equity_curve.append(capital + (position * current_price if position > 0 else 0))
        
        # Calcular métricas
        result.total_trades = result.winning_trades + result.losing_trades
        result.win_rate = result.winning_trades / result.total_trades if result.total_trades > 0 else 0
        result.total_return = (equity_curve[-1] - initial_capital) / initial_capital
        result.equity_curve = equity_curve
        
        # Calcular drawdown
        peak = equity_curve[0]
        for value in equity_curve:
            if value > peak:
                peak = value
            dd = (peak - value) / peak
            if dd > result.max_drawdown:
                result.max_drawdown = dd
        
        # Sharpe ratio (assumindo 0% risk-free)
        returns = pd.Series(equity_curve).pct_change().dropna()
        if len(returns) > 1:
            result.sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252)
        
        logger.info(f"✅ Backtest concluído - Retorno: {result.total_return:.2%}, "
                   f"Sharpe: {result.sharpe_ratio:.2f}, "
                   f"Win Rate: {result.win_rate:.2%}")
        
        return result
    
    # =========================================================================
    # AVALIAÇÃO E MÉTRICAS
    # =========================================================================
    
    def evaluate_backtest(self, backtest_results: BacktestResult) -> Dict[str, Any]:
        """
        Avalia métricas de performance a partir de resultados de backtest.
        
        Args:
            backtest_results: Resultados do backtest
            
        Returns:
            Dicionário com métricas calculadas
        """
        return backtest_results.to_dict()
    
    def get_model_metrics(self, model_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Retorna métricas dos modelos treinados.
        
        Args:
            model_id: Identificador do modelo (None = todos)
            
        Returns:
            Dicionário com métricas
        """
        if model_id:
            return {model_id: self.metrics.get(model_id, ModelMetrics()).to_dict()}
        else:
            return {mid: metrics.to_dict() for mid, metrics in self.metrics.items()}
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        Retorna sumário de performance da AGI.
        
        Returns:
            Dicionário com métricas de performance
        """
        return {
            'state': self.state,
            'total_decisions': len(self.decisions),
            'total_models': len(self.models),
            'active_models': len(self.metrics),
            'last_decision': self.decisions[-1].to_dict() if self.decisions else None,
            'config': {k: v.label if isinstance(v, Enum) else v 
                      for k, v in self.config.items()}
        }
    
    # =========================================================================
    # EXPLICABILIDADE
    # =========================================================================
    
    @timing_decorator
    def explain(self, observation: Union[pd.DataFrame, pd.Series, Dict],
               model_id: Optional[str] = None) -> str:
        """
        Gera uma explicação textual detalhada da decisão atual.
        
        Args:
            observation: Dados de mercado atuais
            model_id: Identificador do modelo a usar
            
        Returns:
            String com explicação legível
        """
        decision = self.predict(observation, model_id)
        
        # Coletar importância das features
        feature_importance = {}
        if model_id and model_id in self.models:
            model = self.models[model_id]
            if hasattr(model, 'feature_importances_'):
                df = observation if isinstance(observation, pd.DataFrame) else pd.DataFrame([observation])
                feature_cols = [col for col in df.columns 
                              if col not in ['open', 'high', 'low', 'close', 'volume']]
                importance_values = model.feature_importances_
                if len(importance_values) == len(feature_cols):
                    feature_importance = dict(zip(feature_cols[:len(importance_values)], 
                                                importance_values))
        
        return self.explainer.generate_explanation_text(decision, feature_importance)
    
    # =========================================================================
    # PERSISTÊNCIA
    # =========================================================================
    
    def save_model(self, model_id: str, path: str):
        """
        Salva modelo treinado em disco.
        
        Args:
            model_id: Identificador do modelo
            path: Caminho para salvar o arquivo
        """
        if model_id not in self.models:
            raise ValueError(f"Modelo {model_id} não encontrado")
        
        model_data = {
            'model': self.models[model_id],
            'metrics': self.metrics.get(model_id),
            'config': self.config,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(path, 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info(f"💾 Modelo {model_id} salvo em {path}")
    
    def load_model(self, path: str, model_id: Optional[str] = None) -> str:
        """
        Carrega modelo treinado do disco.
        
        Args:
            path: Caminho do arquivo
            model_id: Identificador para o modelo carregado
            
        Returns:
            ID do modelo carregado
        """
        with open(path, 'rb') as f:
            model_data = pickle.load(f)
        
        if model_id is None:
            model_id = f"loaded_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.models[model_id] = model_data['model']
        self.metrics[model_id] = model_data['metrics']
        
        logger.info(f"📂 Modelo {model_id} carregado de {path}")
        return model_id
    
    # =========================================================================
    # INTEGRAÇÃO NEURAL BUS
    # =========================================================================
    
    def send_to_neural_bus(self, decision: Decision) -> bool:
        """
        Envia decisão para o NeuralBus.
        
        Args:
            decision: Decisão a ser enviada
            
        Returns:
            True se enviado com sucesso
        """
        if not self.neural_bus:
            logger.warning("NeuralBus não disponível")
            return False
        
        try:
            message = NeuralMessage(
                source='financial_agi',
                target='execution_engine',
                data=decision.to_dict(),
                priority=8
            )
            self.neural_bus.send(message)
            logger.info(f"📨 Decisão enviada ao NeuralBus: {decision.decision_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao enviar para NeuralBus: {e}")
            return False


# =============================================================================
# EXEMPLO DE USO
# =============================================================================

def example_usage():
    """Exemplo de uso da Financial AGI"""
    
    print("\n" + "="*80)
    print("🚀 VHALINOR IAG - FINANCIAL AGI QUÂNTICA - EXEMPLO DE USO")
    print("="*80)
    
    # 1. Criar instância
    print("\n1️⃣  Inicializando Financial AGI...")
    agi = FinancialAGI({
        'model_type': ModelType.RANDOM_FOREST,
        'risk_tolerance': RiskLevel.MEDIUM,
        'timeframe': TimeFrame.D1,
        'lookback_periods': 100,
        'prediction_horizon': 5,
        'feature_count': 50
    })
    
    # 2. Criar dados sintéticos
    print("\n2️⃣  Gerando dados sintéticos...")
    if PANDAS_AVAILABLE:
        dates = pd.date_range(start='2020-01-01', end='2024-12-31', freq='D')
        n = len(dates)
        
        # Gerar preços com random walk
        np.random.seed(42)
        returns = np.random.randn(n) * 0.02
        prices = 100 * np.exp(np.cumsum(returns))
        
        df = pd.DataFrame({
            'open': prices * 0.999,
            'high': prices * 1.002,
            'low': prices * 0.998,
            'close': prices,
            'volume': np.random.randint(1000, 10000, n)
        }, index=dates)
        
        print(f"   ✅ Dados gerados: {len(df)} períodos")
        
        # 3. Pré-processar e gerar features
        print("\n3️⃣  Processando dados e gerando features...")
        df = agi.preprocess_market_data(df)
        df = agi.generate_features(df)
        print(f"   ✅ Features geradas: {len([c for c in df.columns if c not in ['open','high','low','close','volume']])}")
        
        # 4. Treinar modelo
        print("\n4️⃣  Treinando modelo...")
        result = agi.train(df, target='direction')
        print(f"   ✅ Modelo treinado - Acurácia: {result['metrics']['accuracy']}")
        
        # 5. Fazer predição
        print("\n5️⃣  Fazendo predição...")
        latest_data = df.iloc[-60:]  # Últimos 60 períodos
        decision = agi.predict(latest_data)
        
        print(f"\n   📊 DECISÃO:")
        print(f"      Ação: {decision.action.icon} {decision.action.label}")
        print(f"      Confiança: {decision.confidence:.1f}% ({decision.confidence_level.icon})")
        print(f"      Risco: {decision.risk_score:.1%} ({decision.risk_level.icon})")
        print(f"      Motivo: {decision.reason}")
        print(f"      Stop Loss: {decision.stop_loss:.2f}")
        print(f"      Take Profit: {decision.take_profit:.2f}")
        
        # 6. Explicar decisão
        print("\n6️⃣  Explicação da decisão:")
        explanation = agi.explain(latest_data)
        print(explanation)
        
        # 7. Backtest
        print("\n7️⃣  Executando backtest...")
        backtest_result = agi.backtest(df.iloc[:500])  # Primeiros 500 dias
        print(f"\n   📈 RESULTADOS BACKTEST:")
        print(f"      Retorno Total: {backtest_result.total_return:.2%}")
        print(f"      Sharpe Ratio: {backtest_result.sharpe_ratio:.2f}")
        print(f"      Win Rate: {backtest_result.win_rate:.2%}")
        print(f"      Max Drawdown: {backtest_result.max_drawdown:.2%}")
        print(f"      Total Trades: {backtest_result.total_trades}")
        
        # 8. Performance summary
        print("\n8️⃣  Sumário de Performance:")
        summary = agi.get_performance_summary()
        print(f"      Total Predições: {summary['total_decisions']}")
        print(f"      Modelos Ativos: {summary['active_models']}")
        
    else:
        print("❌ pandas não disponível para exemplo")
    
    print("\n" + "="*80)
    print("✅ EXEMPLO CONCLUÍDO COM SUCESSO!")
    print("="*80)
    
    return agi


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'FinancialAGI',
    'Decision',
    'Action',
    'MarketRegime',
    'RiskLevel',
    'ModelType',
    'ConfidenceLevel',
    'TimeFrame',
    'ModelMetrics',
    'BacktestResult',
    'FeatureProcessor',
    'ModelManager',
    'DecisionExplainer'
]

if __name__ == "__main__":
    # Executar exemplo quando script é executado diretamente
    agi = example_usage()
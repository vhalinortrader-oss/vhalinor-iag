# -*- coding: utf-8 -*-

"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    VHALINOR IAG 1.0.0 - MARKET MONITOR QUÂNTICO              ║
║         SISTEMA DE MONITORAMENTO CONTÍNUO COM IA E ANÁLISE PREDITIVA          ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  Módulo: MONITOR DE MERCADO EM TEMPO REAL                                     ║
║  Versão: 2.0.0 (Production Ready - Ultra Baixa Latência)                     ║
║  Autor: Alex Miranda Sales                                                    ║
║  Data: 2026                                                                   ║
║  License: Proprietary - Vhalinor IAG Systems                                  ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

# =============================================================================
# IMPORTAÇÕES OTIMIZADAS COM LAZY LOADING
# =============================================================================

import threading
import asyncio
import queue
import time
import json
import os
import sys
import warnings
import hashlib
import pickle
import gc
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple, Any, Union, Callable, Set, Deque
from collections import defaultdict, deque
from functools import lru_cache, wraps
from pathlib import Path

# =============================================================================
# IMPORTAÇÕES CIENTÍFICAS COM FALLBACK
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

try:
    from scipy import stats, signal
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import websocket
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False

# =============================================================================
# SISTEMA DE LOGGING AVANÇADO
# =============================================================================

try:
    from loguru import logger
    LOGURU_AVAILABLE = True
except ImportError:
    LOGURU_AVAILABLE = False
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(name)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    logger = logging.getLogger('VhalinorMarketMonitor')

# =============================================================================
# CONFIGURAÇÕES E CONSTANTES AVANÇADAS
# =============================================================================

class AlertSeverity(Enum):
    """Severidade de alertas com prioridade numérica"""
    DEBUG = (0, "DEBUG")
    INFO = (1, "INFO")
    WARNING = (2, "WARNING")
    CRITICAL = (3, "CRITICAL")
    EMERGENCY = (4, "EMERGENCY")
    
    def __init__(self, priority: int, label: str):
        self.priority = priority
        self.label = label

class MarketCondition(Enum):
    """Condições de mercado expandidas"""
    TRENDING_UP = "TRENDING_UP"
    TRENDING_DOWN = "TRENDING_DOWN"
    STRONG_TRENDING_UP = "STRONG_TRENDING_UP"
    STRONG_TRENDING_DOWN = "STRONG_TRENDING_DOWN"
    RANGING = "RANGING"
    BREAKOUT_UP = "BREAKOUT_UP"
    BREAKOUT_DOWN = "BREAKOUT_DOWN"
    BREAKDOWN = "BREAKDOWN"
    CONSOLIDATION = "CONSOLIDATION"
    HIGH_VOLATILITY = "HIGH_VOLATILITY"
    LOW_VOLATILITY = "LOW_VOLATILITY"
    ACCUMULATION = "ACCUMULATION"
    DISTRIBUTION = "DISTRIBUTION"
    REVERSAL_UP = "REVERSAL_UP"
    REVERSAL_DOWN = "REVERSAL_DOWN"
    EXHAUSTION = "EXHAUSTION"
    MANIPULATION = "MANIPULATION"

class AlertType(Enum):
    """Tipos de alerta expandidos"""
    PRICE_JUMP = auto()
    PRICE_DROP = auto()
    VOLUME_SPIKE = auto()
    VOLUME_DROP = auto()
    VOLATILITY_SPIKE = auto()
    TREND_REVERSAL = auto()
    SUPPORT_BREAK = auto()
    RESISTANCE_BREAK = auto()
    PATTERN_DETECTED = auto()
    OVERBOUGHT = auto()
    OVERSOLD = auto()
    DIVERGENCE = auto()
    NEWS_IMPACT = auto()
    ECONOMIC_EVENT = auto()
    CORRELATION_BREAK = auto()
    ARBITRAGE = auto()
    LIQUIDITY_ALERT = auto()
    ORDER_IMBALANCE = auto()

class DataSource(Enum):
    """Fontes de dados suportadas"""
    YAHOO_FINANCE = "yfinance"
    ALPACA = "alpaca"
    BINANCE = "binance"
    COINBASE = "coinbase"
    POLYGON = "polygon"
    QUANDL = "quandl"
    ALPHA_VANTAGE = "alpha_vantage"
    TWELVE_DATA = "twelve_data"
    CUSTOM = "custom"
    WEBSOCKET = "websocket"
    CSV = "csv"
    DATABASE = "database"

class TimeFrame(Enum):
    """Timeframes de análise"""
    TICK = "1s"
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"
    W1 = "1w"
    MN1 = "1mo"
    Q1 = "3mo"
    Y1 = "1y"

class TradingSignal(Enum):
    """Sinais de trading"""
    STRONG_BUY = "STRONG_BUY"
    BUY = "BUY"
    NEUTRAL = "NEUTRAL"
    SELL = "SELL"
    STRONG_SELL = "STRONG_SELL"
    HOLD = "HOLD"
    WATCH = "WATCH"
    AVOID = "AVOID"

# =============================================================================
# CONSTANTES DE DESEMPENHO
# =============================================================================

MAX_HISTORY_SIZE = 10000
MAX_ALERTS_SIZE = 1000
MAX_PRICE_LEVELS = 50
DEFAULT_UPDATE_FREQUENCY = 60  # segundos
WEBSOCKET_RECONNECT_DELAY = 5
API_TIMEOUT = 10
BATCH_SIZE = 100
PARALLEL_WORKERS = min(4, os.cpu_count() or 2)
CACHE_TTL = 300  # 5 minutos

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
        if elapsed > 0.1:  # Apenas log se > 100ms
            logger.debug(f"{func.__name__} executado em {elapsed*1000:.2f}ms")
        return result
    return wrapper

def async_retry(max_retries: int = 3, delay: float = 1.0):
    """Decorador para retry em funções assíncronas"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    logger.warning(f"Tentativa {attempt + 1} falhou para {func.__name__}: {e}")
                    await asyncio.sleep(delay * (attempt + 1))
            return None
        return wrapper
    return decorator

def memoize(ttl: int = CACHE_TTL):
    """Cache com time-to-live"""
    def decorator(func):
        cache = {}
        timestamps = {}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = hashlib.md5(
                pickle.dumps((args, kwargs))
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

# =============================================================================
# ESTRUTURAS DE DADOS OTIMIZADAS
# =============================================================================

@dataclass
class MarketAlert:
    """Alerta de mercado com dados enriquecidos"""
    timestamp: datetime
    symbol: str
    severity: AlertSeverity
    alert_type: AlertType
    message: str
    price: float
    condition: MarketCondition
    confidence: float = 0.8
    data: Dict[str, Any] = field(default_factory=dict)
    alert_id: str = field(default_factory=lambda: hashlib.md5(str(time.time()).encode()).hexdigest()[:8])
    expires_at: Optional[datetime] = None
    
    def __post_init__(self):
        if not self.expires_at:
            self.expires_at = self.timestamp + timedelta(hours=24)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário serializável"""
        return {
            'alert_id': self.alert_id,
            'timestamp': self.timestamp.isoformat(),
            'symbol': self.symbol,
            'severity': self.severity.label,
            'severity_priority': self.severity.priority,
            'alert_type': self.alert_type.name,
            'message': self.message,
            'price': self.price,
            'condition': self.condition.value,
            'confidence': self.confidence,
            'data': self.data,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }

@dataclass
class PriceLevel:
    """Nível de preço importante com análise de força"""
    symbol: str
    level_type: str  # 'SUPPORT', 'RESISTANCE'
    price: float
    strength: float  # 0-100
    touches: int = 0
    first_touch: Optional[datetime] = None
    last_touch: Optional[datetime] = None
    bounce_rate: float = 0.0  # % de vezes que reverteu
    volume_at_level: float = 0.0
    is_major: bool = False
    confidence: float = 0.5
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário serializável"""
        return {
            'symbol': self.symbol,
            'level_type': self.level_type,
            'price': self.price,
            'strength': self.strength,
            'touches': self.touches,
            'first_touch': self.first_touch.isoformat() if self.first_touch else None,
            'last_touch': self.last_touch.isoformat() if self.last_touch else None,
            'bounce_rate': self.bounce_rate,
            'volume_at_level': self.volume_at_level,
            'is_major': self.is_major,
            'confidence': self.confidence
        }

@dataclass
class MarketMetrics:
    """Métricas de mercado completas"""
    symbol: str
    timestamp: datetime
    
    # Preços
    current_price: float
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    vwap: float = 0.0
    
    # Volume
    volume_24h: float = 0.0
    volume_1h: float = 0.0
    volume_relative: float = 1.0
    volume_trend: float = 0.0
    
    # Volatilidade
    volatility: float = 0.0
    historical_volatility: float = 0.0
    implied_volatility: Optional[float] = None
    atr: float = 0.0  # Average True Range
    bollinger_width: float = 0.0
    
    # Tendência
    trend_strength: float = 0.0
    trend_direction: int = 0  # -1: down, 0: sideways, 1: up
    adx: float = 0.0
    macd: float = 0.0
    macd_signal: float = 0.0
    macd_histogram: float = 0.0
    
    # Momentum
    momentum: float = 0.0
    momentum_1h: float = 0.0
    momentum_24h: float = 0.0
    rsi: float = 50.0
    stoch_k: float = 50.0
    stoch_d: float = 50.0
    cci: float = 0.0
    
    # Suporte/Resistência
    nearest_support: float = 0.0
    nearest_resistance: float = 0.0
    support_distance: float = 0.0
    resistance_distance: float = 0.0
    
    # Correlação
    beta: float = 1.0
    correlation_spy: float = 0.0
    correlation_vix: float = 0.0
    
    # Estatísticas
    returns_1h: float = 0.0
    returns_24h: float = 0.0
    returns_7d: float = 0.0
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário serializável"""
        return {
            'symbol': self.symbol,
            'timestamp': self.timestamp.isoformat(),
            'current_price': self.current_price,
            'volume_24h': self.volume_24h,
            'volatility': self.volatility,
            'trend_strength': self.trend_strength,
            'trend_direction': self.trend_direction,
            'rsi': self.rsi,
            'macd': self.macd,
            'momentum': self.momentum,
            'returns_24h': self.returns_24h
        }

@dataclass
class TradingOpportunity:
    """Oportunidade de trading detectada"""
    timestamp: datetime
    symbol: str
    signal: TradingSignal
    confidence: float
    entry_price: float
    target_price: float
    stop_loss: float
    risk_reward: float
    timeframe: TimeFrame
    reasoning: List[str]
    indicators: Dict[str, float] = field(default_factory=dict)
    opportunity_id: str = field(default_factory=lambda: hashlib.md5(str(time.time()).encode()).hexdigest()[:8])
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário serializável"""
        return {
            'opportunity_id': self.opportunity_id,
            'timestamp': self.timestamp.isoformat(),
            'symbol': self.symbol,
            'signal': self.signal.value,
            'confidence': self.confidence,
            'entry_price': self.entry_price,
            'target_price': self.target_price,
            'stop_loss': self.stop_loss,
            'risk_reward': self.risk_reward,
            'timeframe': self.timeframe.value,
            'reasoning': self.reasoning,
            'indicators': self.indicators
        }

# =============================================================================
# PROVEDORES DE DADOS (ABSTRAÇÃO)
# =============================================================================

class DataProvider(ABC):
    """Classe abstrata para provedores de dados"""
    
    @abstractmethod
    async def fetch_price(self, symbol: str) -> Optional[float]:
        pass
    
    @abstractmethod
    async def fetch_historical(self, symbol: str, period: str, interval: str) -> Optional[pd.DataFrame]:
        pass
    
    @abstractmethod
    async def fetch_volume(self, symbol: str) -> Optional[float]:
        pass

class YahooFinanceProvider(DataProvider):
    """Provedor de dados Yahoo Finance"""
    
    def __init__(self):
        self.cache = {}
    
    @async_retry(max_retries=3)
    @timing_decorator
    async def fetch_price(self, symbol: str) -> Optional[float]:
        if not YFINANCE_AVAILABLE:
            logger.error("yfinance não está disponível")
            return None
        
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='1d', interval='1m')
            
            if data.empty:
                return None
            
            return float(data['Close'].iloc[-1])
        except Exception as e:
            logger.error(f"Erro ao buscar preço {symbol}: {e}")
            return None
    
    @async_retry(max_retries=3)
    async def fetch_historical(self, symbol: str, period: str = '1mo', 
                              interval: str = '1h') -> Optional[pd.DataFrame]:
        if not YFINANCE_AVAILABLE:
            return None
        
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            return data
        except Exception as e:
            logger.error(f"Erro ao buscar histórico {symbol}: {e}")
            return None
    
    async def fetch_volume(self, symbol: str) -> Optional[float]:
        data = await self.fetch_historical(symbol, period='1d', interval='1m')
        if data is not None and not data.empty:
            return float(data['Volume'].sum())
        return None

class BinanceProvider(DataProvider):
    """Provedor de dados Binance"""
    
    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3"
        self.cache = {}
    
    @async_retry(max_retries=3)
    async def fetch_price(self, symbol: str) -> Optional[float]:
        if not REQUESTS_AVAILABLE:
            return None
        
        try:
            # Converter formato (BTCUSD -> BTCUSDT)
            if symbol.endswith('USD'):
                symbol = symbol.replace('USD', 'USDT')
            
            url = f"{self.base_url}/ticker/price"
            params = {'symbol': symbol.upper()}
            
            response = requests.get(url, params=params, timeout=API_TIMEOUT)
            data = response.json()
            
            return float(data['price'])
        except Exception as e:
            logger.error(f"Erro ao buscar preço Binance {symbol}: {e}")
            return None
    
    async def fetch_historical(self, symbol: str, period: str = '1mo', 
                              interval: str = '1h') -> Optional[pd.DataFrame]:
        # Implementar se necessário
        return None
    
    async def fetch_volume(self, symbol: str) -> Optional[float]:
        return None

class AlphaVantageProvider(DataProvider):
    """Provedor de dados Alpha Vantage"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.alphavantage.co/query"
    
    @async_retry(max_retries=3)
    async def fetch_price(self, symbol: str) -> Optional[float]:
        if not REQUESTS_AVAILABLE:
            return None
        
        try:
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol,
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=API_TIMEOUT)
            data = response.json()
            
            quote = data.get('Global Quote', {})
            return float(quote.get('05. price', 0))
        except Exception as e:
            logger.error(f"Erro Alpha Vantage {symbol}: {e}")
            return None
    
    async def fetch_historical(self, symbol: str, period: str = '1mo', 
                              interval: str = '1h') -> Optional[pd.DataFrame]:
        return None
    
    async def fetch_volume(self, symbol: str) -> Optional[float]:
        return None

class WebSocketProvider(DataProvider):
    """Provedor de dados via WebSocket para tempo real"""
    
    def __init__(self, url: str, symbols: List[str]):
        self.url = url
        self.symbols = symbols
        self.ws = None
        self.price_callbacks = []
    
    async def fetch_price(self, symbol: str) -> Optional[float]:
        # WebSocket é push, não pull
        return None
    
    async def fetch_historical(self, symbol: str, period: str = '1mo', 
                              interval: str = '1h') -> Optional[pd.DataFrame]:
        return None
    
    async def fetch_volume(self, symbol: str) -> Optional[float]:
        return None
    
    def connect(self):
        """Conectar WebSocket"""
        if not WEBSOCKET_AVAILABLE:
            logger.error("websocket-client não disponível")
            return
        
        def on_message(ws, message):
            data = json.loads(message)
            # Processar mensagem
            for callback in self.price_callbacks:
                callback(data)
        
        def on_error(ws, error):
            logger.error(f"WebSocket error: {error}")
        
        def on_close(ws, close_status_code, close_msg):
            logger.info("WebSocket fechado")
            # Tentar reconectar
            time.sleep(WEBSOCKET_RECONNECT_DELAY)
            self.connect()
        
        def on_open(ws):
            logger.info("WebSocket conectado")
            # Inscrever nos símbolos
            subscribe_msg = {
                "type": "subscribe",
                "symbols": self.symbols
            }
            ws.send(json.dumps(subscribe_msg))
        
        self.ws = websocket.WebSocketApp(
            self.url,
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close
        )
        
        # Iniciar em thread separada
        wst = threading.Thread(target=self.ws.run_forever, daemon=True)
        wst.start()

# =============================================================================
# ANALISADOR TÉCNICO AVANÇADO
# =============================================================================

class TechnicalAnalyzer:
    """Analisador técnico com múltiplos indicadores"""
    
    @staticmethod
    @memoize(ttl=60)
    def calculate_rsi(prices: List[float], period: int = 14) -> float:
        """Calcular RSI"""
        if len(prices) < period + 1:
            return 50.0
        
        if NUMPY_AVAILABLE:
            deltas = np.diff(prices[-period-1:])
            seed = deltas[:period]
            up = seed[seed >= 0].sum() / period
            down = -seed[seed < 0].sum() / period
            rs = up / down if down != 0 else 100
            rsi = 100 - 100 / (1 + rs)
            return rsi
        else:
            # Implementação pura Python
            gains = 0
            losses = 0
            for i in range(-period-1, -1):
                change = prices[i+1] - prices[i]
                if change > 0:
                    gains += change
                else:
                    losses -= change
            
            avg_gain = gains / period
            avg_loss = losses / period
            rs = avg_gain / avg_loss if avg_loss != 0 else 100
            return 100 - 100 / (1 + rs)
    
    @staticmethod
    @memoize(ttl=60)
    def calculate_macd(prices: List[float]) -> Tuple[float, float, float]:
        """Calcular MACD"""
        if len(prices) < 26:
            return 0.0, 0.0, 0.0
        
        if NUMPY_AVAILABLE:
            ema12 = TechnicalAnalyzer._ema(prices, 12)
            ema26 = TechnicalAnalyzer._ema(prices, 26)
            macd = ema12 - ema26
            signal = TechnicalAnalyzer._ema([macd] * len(prices), 9)[0] if isinstance(macd, float) else macd
            histogram = macd - signal
            return macd, signal, histogram
        else:
            return 0.0, 0.0, 0.0
    
    @staticmethod
    def _ema(prices: List[float], period: int) -> float:
        """Exponential Moving Average"""
        if not prices:
            return 0.0
        
        if NUMPY_AVAILABLE:
            weights = np.exp(np.linspace(-1., 0., period))
            weights /= weights.sum()
            ema = np.convolve(prices, weights, mode='valid')[:1]
            return ema[0] if len(ema) > 0 else prices[-1]
        else:
            # SMA como fallback
            return sum(prices[-period:]) / period
    
    @staticmethod
    @memoize(ttl=60)
    def calculate_bollinger(prices: List[float], period: int = 20, 
                           std_dev: float = 2.0) -> Tuple[float, float, float, float, float]:
        """Calcular Bollinger Bands"""
        if len(prices) < period:
            return prices[-1], prices[-1], prices[-1], 0.0, 0.5
        
        if NUMPY_AVAILABLE:
            recent = prices[-period:]
            sma = np.mean(recent)
            std = np.std(recent)
            
            upper = sma + (std * std_dev)
            lower = sma - (std * std_dev)
            bandwidth = (upper - lower) / sma
            position = (prices[-1] - lower) / (upper - lower) if upper != lower else 0.5
            
            return upper, sma, lower, bandwidth, position
        else:
            # Fallback simplificado
            recent = prices[-period:]
            sma = sum(recent) / period
            return sma * 1.02, sma, sma * 0.98, 0.04, 0.5
    
    @staticmethod
    @memoize(ttl=60)
    def calculate_volatility(prices: List[float], annualize: bool = True) -> float:
        """Calcular volatilidade"""
        if len(prices) < 2:
            return 0.0
        
        if NUMPY_AVAILABLE:
            returns = np.diff(prices) / prices[:-1]
            volatility = np.std(returns)
            
            if annualize:
                volatility *= np.sqrt(252 * 6.5)  # Trading days * hours
            return volatility
        else:
            returns = []
            for i in range(1, len(prices)):
                returns.append((prices[i] - prices[i-1]) / prices[i-1])
            
            mean = sum(returns) / len(returns)
            variance = sum((r - mean) ** 2 for r in returns) / len(returns)
            return variance ** 0.5
    
    @staticmethod
    @memoize(ttl=60)
    def calculate_trend_strength(prices: List[float]) -> Tuple[float, int]:
        """Calcular força e direção da tendência"""
        if len(prices) < 20:
            return 0.0, 0
        
        if NUMPY_AVAILABLE:
            # Regressão linear
            x = np.arange(len(prices[-20:]))
            y = np.array(prices[-20:])
            
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            
            strength = abs(r_value)  # R-squared como força
            direction = 1 if slope > 0 else -1 if slope < 0 else 0
            
            return strength, direction
        else:
            # Método simplificado
            sma20 = sum(prices[-20:]) / 20
            sma50 = sum(prices[-50:]) / 50 if len(prices) >= 50 else sma20
            
            if sma20 > sma50:
                return 0.5, 1
            elif sma20 < sma50:
                return 0.5, -1
            else:
                return 0.0, 0
    
    @staticmethod
    def detect_support_resistance(prices: List[float], 
                                 highs: List[float], 
                                 lows: List[float]) -> Tuple[float, float, float, float]:
        """Detectar níveis de suporte e resistência"""
        if len(prices) < 20:
            return 0.0, 0.0, 0.0, 0.0
        
        current = prices[-1]
        
        # Resistência: picos recentes
        resistance_candidates = []
        for i in range(1, len(highs) - 1):
            if highs[i] > highs[i-1] and highs[i] > highs[i+1]:
                resistance_candidates.append(highs[i])
        
        # Suporte: vales recentes
        support_candidates = []
        for i in range(1, len(lows) - 1):
            if lows[i] < lows[i-1] and lows[i] < lows[i+1]:
                support_candidates.append(lows[i])
        
        # Selecionar níveis mais próximos
        nearest_resistance = min([r for r in resistance_candidates if r > current], 
                                default=current * 1.05)
        nearest_support = max([s for s in support_candidates if s < current], 
                             default=current * 0.95)
        
        resistance_distance = (nearest_resistance - current) / current
        support_distance = (current - nearest_support) / current
        
        return nearest_support, nearest_resistance, support_distance, resistance_distance

# =============================================================================
# DETECTOR DE PADRÕES
# =============================================================================

class PatternDetector:
    """Detector de padrões de mercado"""
    
    PATTERNS = {
        'double_top': {
            'name': 'Double Top',
            'type': 'REVERSAL_BEARISH',
            'min_bars': 20,
            'reliability': 0.75
        },
        'double_bottom': {
            'name': 'Double Bottom',
            'type': 'REVERSAL_BULLISH',
            'min_bars': 20,
            'reliability': 0.75
        },
        'head_shoulders': {
            'name': 'Head and Shoulders',
            'type': 'REVERSAL_BEARISH',
            'min_bars': 40,
            'reliability': 0.80
        },
        'inverse_head_shoulders': {
            'name': 'Inverse Head and Shoulders',
            'type': 'REVERSAL_BULLISH',
            'min_bars': 40,
            'reliability': 0.80
        },
        'bull_flag': {
            'name': 'Bull Flag',
            'type': 'CONTINUATION_BULLISH',
            'min_bars': 15,
            'reliability': 0.70
        },
        'bear_flag': {
            'name': 'Bear Flag',
            'type': 'CONTINUATION_BEARISH',
            'min_bars': 15,
            'reliability': 0.70
        },
        'ascending_triangle': {
            'name': 'Ascending Triangle',
            'type': 'BULLISH_BREAKOUT',
            'min_bars': 25,
            'reliability': 0.72
        },
        'descending_triangle': {
            'name': 'Descending Triangle',
            'type': 'BEARISH_BREAKOUT',
            'min_bars': 25,
            'reliability': 0.72
        }
    }
    
    @staticmethod
    def detect_patterns(prices: List[float], highs: List[float], 
                       lows: List[float]) -> List[Dict[str, Any]]:
        """Detectar padrões nos dados"""
        patterns = []
        
        if len(prices) < 50:
            return patterns
        
        # Double Top
        if PatternDetector._is_double_top(prices[-30:]):
            patterns.append({
                'pattern': 'double_top',
                'confidence': 0.7,
                'direction': 'bearish'
            })
        
        # Double Bottom
        if PatternDetector._is_double_bottom(prices[-30:]):
            patterns.append({
                'pattern': 'double_bottom',
                'confidence': 0.7,
                'direction': 'bullish'
            })
        
        # Bull Flag
        if PatternDetector._is_bull_flag(prices[-20:]):
            patterns.append({
                'pattern': 'bull_flag',
                'confidence': 0.65,
                'direction': 'bullish'
            })
        
        # Bear Flag
        if PatternDetector._is_bear_flag(prices[-20:]):
            patterns.append({
                'pattern': 'bear_flag',
                'confidence': 0.65,
                'direction': 'bearish'
            })
        
        return patterns
    
    @staticmethod
    def _is_double_top(prices: List[float], tolerance: float = 0.02) -> bool:
        """Detectar padrão Double Top"""
        if len(prices) < 20:
            return False
        
        # Encontrar picos
        peaks = []
        for i in range(1, len(prices)-1):
            if prices[i] > prices[i-1] and prices[i] > prices[i+1]:
                peaks.append((i, prices[i]))
        
        if len(peaks) < 2:
            return False
        
        # Verificar se dois picos têm altura similar
        peak1 = peaks[-2][1]
        peak2 = peaks[-1][1]
        
        if abs(peak1 - peak2) / peak1 <= tolerance:
            # Verificar se há um vale entre eles
            trough = min(prices[peaks[-2][0]:peaks[-1][0]])
            if trough < peak1 * 0.95:
                return True
        
        return False
    
    @staticmethod
    def _is_double_bottom(prices: List[float], tolerance: float = 0.02) -> bool:
        """Detectar padrão Double Bottom"""
        if len(prices) < 20:
            return False
        
        # Encontrar vales
        troughs = []
        for i in range(1, len(prices)-1):
            if prices[i] < prices[i-1] and prices[i] < prices[i+1]:
                troughs.append((i, prices[i]))
        
        if len(troughs) < 2:
            return False
        
        trough1 = troughs[-2][1]
        trough2 = troughs[-1][1]
        
        if abs(trough1 - trough2) / trough1 <= tolerance:
            peak = max(prices[troughs[-2][0]:troughs[-1][0]])
            if peak > trough1 * 1.05:
                return True
        
        return False
    
    @staticmethod
    def _is_bull_flag(prices: List[float]) -> bool:
        """Detectar padrão Bull Flag"""
        if len(prices) < 15:
            return False
        
        # Flag: consolidação após forte movimento de alta
        recent = prices[-5:]
        previous = prices[-10:-5]
        
        # Movimento forte de alta
        if previous[-1] > previous[0] * 1.05:
            # Consolidação lateral
            if max(recent) / min(recent) < 1.02:
                return True
        
        return False
    
    @staticmethod
    def _is_bear_flag(prices: List[float]) -> bool:
        """Detectar padrão Bear Flag"""
        if len(prices) < 15:
            return False
        
        recent = prices[-5:]
        previous = prices[-10:-5]
        
        # Movimento forte de baixa
        if previous[-1] < previous[0] * 0.95:
            # Consolidação lateral
            if max(recent) / min(recent) < 1.02:
                return True
        
        return False

# =============================================================================
# ESTRATÉGIAS DE TRADING
# =============================================================================

class TradingStrategy(ABC):
    """Classe abstrata para estratégias de trading"""
    
    def __init__(self, name: str):
        self.name = name
        self.performance = {
            'trades': 0,
            'wins': 0,
            'losses': 0,
            'total_pnl': 0.0,
            'win_rate': 0.0
        }
    
    @abstractmethod
    def analyze(self, symbol: str, metrics: MarketMetrics, 
                history: List[float]) -> Optional[TradingOpportunity]:
        pass
    
    def update_performance(self, pnl: float):
        """Atualizar performance da estratégia"""
        self.performance['trades'] += 1
        self.performance['total_pnl'] += pnl
        
        if pnl > 0:
            self.performance['wins'] += 1
        else:
            self.performance['losses'] += 1
        
        if self.performance['trades'] > 0:
            self.performance['win_rate'] = self.performance['wins'] / self.performance['trades']

class RSIMeanReversionStrategy(TradingStrategy):
    """Estratégia de reversão à média baseada em RSI"""
    
    def __init__(self, oversold: int = 30, overbought: int = 70):
        super().__init__("RSI Mean Reversion")
        self.oversold = oversold
        self.overbought = overbought
    
    def analyze(self, symbol: str, metrics: MarketMetrics, 
                history: List[float]) -> Optional[TradingOpportunity]:
        
        if metrics.rsi < self.oversold:
            # Oversold - possível compra
            confidence = (self.oversold - metrics.rsi) / self.oversold
            confidence = min(0.8, max(0.4, confidence))
            
            entry = metrics.current_price
            target = entry * 1.02
            stop = entry * 0.985
            
            return TradingOpportunity(
                timestamp=datetime.now(),
                symbol=symbol,
                signal=TradingSignal.BUY,
                confidence=confidence,
                entry_price=entry,
                target_price=target,
                stop_loss=stop,
                risk_reward=(target - entry) / (entry - stop),
                timeframe=TimeFrame.H1,
                reasoning=[f"RSI em {metrics.rsi:.1f} (oversold)", 
                          "Reversão à média esperada"],
                indicators={'rsi': metrics.rsi, 'oversold_threshold': self.oversold}
            )
        
        elif metrics.rsi > self.overbought:
            # Overbought - possível venda
            confidence = (metrics.rsi - self.overbought) / (100 - self.overbought)
            confidence = min(0.8, max(0.4, confidence))
            
            entry = metrics.current_price
            target = entry * 0.98
            stop = entry * 1.015
            
            return TradingOpportunity(
                timestamp=datetime.now(),
                symbol=symbol,
                signal=TradingSignal.SELL,
                confidence=confidence,
                entry_price=entry,
                target_price=target,
                stop_loss=stop,
                risk_reward=(entry - target) / (stop - entry),
                timeframe=TimeFrame.H1,
                reasoning=[f"RSI em {metrics.rsi:.1f} (overbought)", 
                          "Reversão à média esperada"],
                indicators={'rsi': metrics.rsi, 'overbought_threshold': self.overbought}
            )
        
        return None

class BreakoutStrategy(TradingStrategy):
    """Estratégia de breakout de volatilidade"""
    
    def __init__(self, lookback: int = 20, multiplier: float = 2.0):
        super().__init__("Volatility Breakout")
        self.lookback = lookback
        self.multiplier = multiplier
    
    def analyze(self, symbol: str, metrics: MarketMetrics, 
                history: List[float]) -> Optional[TradingOpportunity]:
        
        if len(history) < self.lookback:
            return None
        
        recent = history[-self.lookback:]
        avg_range = (max(recent) - min(recent)) / len(recent)
        current_range = metrics.high_price - metrics.low_price
        
        if current_range > avg_range * self.multiplier:
            confidence = min(0.75, current_range / (avg_range * self.multiplier) * 0.5)
            
            # Determinar direção
            if metrics.current_price > metrics.vwap:
                signal = TradingSignal.BUY
                target = metrics.current_price * 1.03
                stop = metrics.current_price * 0.98
                reasoning = ["Breakout de volatilidade para cima"]
            else:
                signal = TradingSignal.SELL
                target = metrics.current_price * 0.97
                stop = metrics.current_price * 1.02
                reasoning = ["Breakout de volatilidade para baixo"]
            
            return TradingOpportunity(
                timestamp=datetime.now(),
                symbol=symbol,
                signal=signal,
                confidence=confidence,
                entry_price=metrics.current_price,
                target_price=target,
                stop_loss=stop,
                risk_reward=1.5,
                timeframe=TimeFrame.M15,
                reasoning=reasoning,
                indicators={
                    'current_range': current_range,
                    'avg_range': avg_range,
                    'ratio': current_range / avg_range if avg_range else 0
                }
            )
        
        return None

class TrendFollowingStrategy(TradingStrategy):
    """Estratégia de seguir tendência"""
    
    def __init__(self):
        super().__init__("Trend Following")
    
    def analyze(self, symbol: str, metrics: MarketMetrics, 
                history: List[float]) -> Optional[TradingOpportunity]:
        
        if metrics.trend_strength > 0.6 and abs(metrics.trend_direction) > 0:
            confidence = metrics.trend_strength * 0.8
            
            if metrics.trend_direction > 0:
                signal = TradingSignal.BUY
                target = metrics.current_price * 1.04
                stop = metrics.current_price * 0.98
                reasoning = ["Tendência de alta forte", 
                            f"ADX: {metrics.adx:.1f}",
                            "Médias alinhadas"]
            else:
                signal = TradingSignal.SELL
                target = metrics.current_price * 0.96
                stop = metrics.current_price * 1.02
                reasoning = ["Tendência de baixa forte",
                            f"ADX: {metrics.adx:.1f}",
                            "Médias alinhadas"]
            
            return TradingOpportunity(
                timestamp=datetime.now(),
                symbol=symbol,
                signal=signal,
                confidence=confidence,
                entry_price=metrics.current_price,
                target_price=target,
                stop_loss=stop,
                risk_reward=2.0,
                timeframe=TimeFrame.H4,
                reasoning=reasoning,
                indicators={
                    'trend_strength': metrics.trend_strength,
                    'trend_direction': metrics.trend_direction,
                    'adx': metrics.adx
                }
            )
        
        return None

# =============================================================================
# MONITOR DE MERCADO PRINCIPAL
# =============================================================================

class MarketMonitor:
    """
    Monitor de mercado avançado com análise em tempo real,
    detecção de oportunidades e múltiplas fontes de dados
    """
    
    def __init__(self, 
                 symbols: List[str], 
                 update_frequency: int = DEFAULT_UPDATE_FREQUENCY,
                 data_source: DataSource = DataSource.YAHOO_FINANCE,
                 api_key: Optional[str] = None):
        
        self.symbols = symbols
        self.update_frequency = update_frequency
        self.data_source = data_source
        self.api_key = api_key
        
        # ===== ESTADO DO SISTEMA =====
        self.is_running = False
        self._stop_event = threading.Event()
        self._monitor_thread = None
        self._async_loop = None
        
        # ===== FILAS E BUFFERS =====
        self.price_queue = queue.Queue(maxsize=1000)
        self.alert_queue = queue.Queue(maxsize=500)
        self.opportunity_queue = queue.Queue(maxsize=500)
        
        # ===== DADOS MONITORADOS =====
        self.current_prices: Dict[str, float] = {}
        self.price_history: Dict[str, Deque[float]] = {
            s: deque(maxlen=MAX_HISTORY_SIZE) for s in symbols
        }
        self.high_history: Dict[str, Deque[float]] = {
            s: deque(maxlen=MAX_HISTORY_SIZE) for s in symbols
        }
        self.low_history: Dict[str, Deque[float]] = {
            s: deque(maxlen=MAX_HISTORY_SIZE) for s in symbols
        }
        self.volume_history: Dict[str, Deque[float]] = {
            s: deque(maxlen=MAX_HISTORY_SIZE) for s in symbols
        }
        
        self.alerts: Deque[MarketAlert] = deque(maxlen=MAX_ALERTS_SIZE)
        self.opportunities: Deque[TradingOpportunity] = deque(maxlen=MAX_ALERTS_SIZE)
        self.price_levels: Dict[str, List[PriceLevel]] = {s: [] for s in symbols}
        self.metrics: Dict[str, MarketMetrics] = {}
        self.patterns: Dict[str, List[Dict]] = {s: [] for s in symbols}
        
        # ===== PROVEDORES DE DADOS =====
        self.data_provider = self._create_data_provider()
        
        # ===== ANALISADORES =====
        self.technical_analyzer = TechnicalAnalyzer()
        self.pattern_detector = PatternDetector()
        
        # ===== ESTRATÉGIAS =====
        self.strategies: List[TradingStrategy] = [
            RSIMeanReversionStrategy(),
            BreakoutStrategy(),
            TrendFollowingStrategy()
        ]
        
        # ===== CALLBACKS =====
        self._callbacks = {
            'on_price_update': [],
            'on_alert': [],
            'on_opportunity': [],
            'on_level_break': [],
            'on_pattern': [],
            'on_error': [],
            'on_start': [],
            'on_stop': []
        }
        
        # ===== THREAD POOL =====
        self.thread_pool = ThreadPoolExecutor(max_workers=PARALLEL_WORKERS)
        
        # ===== CONFIGURAÇÕES =====
        self.config = {
            'price_change_threshold': 0.02,  # 2%
            'volatility_threshold': 0.03,    # 3%
            'volume_threshold': 1.5,         # 150%
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'enable_patterns': True,
            'enable_webhooks': False,
            'webhook_url': None,
            'log_level': 'INFO',
            'auto_export': False,
            'export_path': './data'
        }
        
        logger.info(f"✅ Market Monitor Quântico inicializado para {len(symbols)} símbolos")
        logger.info(f"   • Fonte de dados: {data_source.value}")
        logger.info(f"   • Estratégias: {len(self.strategies)}")
        logger.info(f"   • Frequência: {update_frequency}s")
    
    def _create_data_provider(self) -> Optional[DataProvider]:
        """Criar provedor de dados baseado na configuração"""
        if self.data_source == DataSource.YAHOO_FINANCE:
            return YahooFinanceProvider()
        elif self.data_source == DataSource.BINANCE:
            return BinanceProvider()
        elif self.data_source == DataSource.ALPHA_VANTAGE and self.api_key:
            return AlphaVantageProvider(self.api_key)
        else:
            logger.warning(f"⚠️ Provedor {self.data_source.value} não implementado, usando Yahoo Finance")
            return YahooFinanceProvider()
    
    # =========================================================================
    # REGISTRO DE CALLBACKS
    # =========================================================================
    
    def register_callback(self, event_type: str, callback: Callable):
        """Registrar callback para eventos"""
        if event_type in self._callbacks:
            self._callbacks[event_type].append(callback)
            logger.debug(f"Callback registrado para {event_type}")
        else:
            logger.warning(f"Tipo de evento desconhecido: {event_type}")
    
    def unregister_callback(self, event_type: str, callback: Callable):
        """Remover callback registrado"""
        if event_type in self._callbacks and callback in self._callbacks[event_type]:
            self._callbacks[event_type].remove(callback)
            logger.debug(f"Callback removido de {event_type}")
    
    def _trigger_callbacks(self, event_type: str, data: Any = None):
        """Disparar callbacks registrados"""
        if event_type in self._callbacks:
            for callback in self._callbacks[event_type]:
                try:
                    callback(data or {})
                except Exception as e:
                    logger.error(f"❌ Erro em callback {event_type}: {e}")
                    self._trigger_callbacks('on_error', {'callback': event_type, 'error': str(e)})
    
    # =========================================================================
    # CONTROLE DO MONITOR
    # =========================================================================
    
    def start(self):
        """Iniciar monitoramento"""
        if self.is_running:
            logger.warning("⚠️ Monitor já está em execução")
            return
        
        self.is_running = True
        self._stop_event.clear()
        
        # Iniciar thread de monitoramento
        self._monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self._monitor_thread.start()
        
        # Iniciar thread de processamento de filas
        self._queue_thread = threading.Thread(target=self._queue_processor, daemon=True)
        self._queue_thread.start()
        
        # Iniciar loop assíncrono
        self._start_async_loop()
        
        self._trigger_callbacks('on_start', {'timestamp': datetime.now()})
        logger.info("🔍 Market Monitor Quântico iniciado")
    
    def stop(self):
        """Parar monitoramento"""
        self.is_running = False
        self._stop_event.set()
        
        # Parar thread pool
        self.thread_pool.shutdown(wait=False)
        
        self._trigger_callbacks('on_stop', {'timestamp': datetime.now()})
        logger.info("🔍 Market Monitor Quântico parado")
    
    def _start_async_loop(self):
        """Iniciar loop assíncrono em thread separada"""
        def run_async():
            self._async_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._async_loop)
            self._async_loop.run_forever()
        
        async_thread = threading.Thread(target=run_async, daemon=True)
        async_thread.start()
    
    # =========================================================================
    # PROCESSAMENTO PRINCIPAL
    # =========================================================================
    
    def _monitoring_loop(self):
        """Loop principal de monitoramento"""
        while not self._stop_event.is_set():
            try:
                # Processar símbolos em paralelo
                futures = []
                for symbol in self.symbols:
                    future = self.thread_pool.submit(self._process_symbol, symbol)
                    futures.append(future)
                
                # Aguardar conclusão
                for future in futures:
                    future.result(timeout=self.update_frequency)
                
                # Exportar automaticamente se configurado
                if self.config['auto_export']:
                    self._auto_export()
                
                # Aguardar próximo ciclo
                time.sleep(self.update_frequency)
                
            except Exception as e:
                logger.error(f"❌ Erro no loop de monitoramento: {e}")
                self._trigger_callbacks('on_error', {'error': str(e)})
                time.sleep(5)
    
    def _process_symbol(self, symbol: str):
        """Processar um símbolo individual"""
        try:
            # Coletar dados de mercado
            market_data = self._fetch_market_data_sync(symbol)
            
            if market_data:
                # Adicionar à fila para processamento assíncrono
                self.price_queue.put({
                    'symbol': symbol,
                    'data': market_data,
                    'timestamp': datetime.now()
                })
                
                # Processar imediatamente alguns dados críticos
                self._process_market_data(symbol, market_data)
                self._detect_alerts(symbol, market_data)
                
        except Exception as e:
            logger.error(f"❌ Erro ao processar {symbol}: {e}")
    
    def _fetch_market_data_sync(self, symbol: str) -> Optional[Dict]:
        """Buscar dados de mercado (versão síncrona)"""
        if not self.data_provider:
            return None
        
        try:
            # Executar corrotina de forma síncrona
            if self._async_loop and self._async_loop.is_running():
                future = asyncio.run_coroutine_threadsafe(
                    self.data_provider.fetch_price(symbol),
                    self._async_loop
                )
                price = future.result(timeout=API_TIMEOUT)
                
                if price:
                    return {
                        'symbol': symbol,
                        'timestamp': datetime.now(),
                        'price': price,
                        'volume': None  # Seria buscado separadamente
                    }
            
            return None
            
        except Exception as e:
            logger.debug(f"Erro ao buscar dados de {symbol}: {e}")
            return None
    
    def _queue_processor(self):
        """Processador de filas em background"""
        while not self._stop_event.is_set():
            try:
                # Processar fila de preços
                try:
                    item = self.price_queue.get(timeout=0.1)
                    self._process_price_update(item['symbol'], item['data'])
                except queue.Empty:
                    pass
                
                # Processar fila de alertas
                try:
                    alert = self.alert_queue.get(timeout=0.1)
                    self._process_alert(alert)
                except queue.Empty:
                    pass
                
                # Processar fila de oportunidades
                try:
                    opportunity = self.opportunity_queue.get(timeout=0.1)
                    self._process_opportunity(opportunity)
                except queue.Empty:
                    pass
                
            except Exception as e:
                logger.error(f"Erro no processador de filas: {e}")
                time.sleep(0.1)
    
    def _process_price_update(self, symbol: str, data: Dict):
        """Processar atualização de preço"""
        # Implementar se necessário
        pass
    
    # =========================================================================
    # PROCESSAMENTO DE DADOS
    # =========================================================================
    
    @timing_decorator
    def _process_market_data(self, symbol: str, data: Dict):
        """Processar dados de mercado"""
        price = data.get('price', 0)
        volume = data.get('volume')
        
        # Atualizar preço atual
        old_price = self.current_prices.get(symbol, price)
        self.current_prices[symbol] = price
        
        # Atualizar histórico
        if price > 0:
            self.price_history[symbol].append(price)
        
        # Calcular métricas
        metrics = self._calculate_metrics(symbol, data, old_price)
        self.metrics[symbol] = metrics
        
        # Detectar oportunidades
        opportunities = self._detect_opportunities(symbol, metrics)
        for opp in opportunities:
            self.opportunity_queue.put(opp)
        
        # Detectar padrões
        if self.config['enable_patterns']:
            patterns = self.pattern_detector.detect_patterns(
                list(self.price_history[symbol]),
                list(self.high_history[symbol]),
                list(self.low_history[symbol])
            )
            self.patterns[symbol] = patterns
            
            for pattern in patterns:
                self._trigger_callbacks('on_pattern', {
                    'symbol': symbol,
                    'pattern': pattern,
                    'timestamp': datetime.now()
                })
        
        # Disparar callback
        self._trigger_callbacks('on_price_update', {
            'symbol': symbol,
            'price': price,
            'change': price - old_price,
            'change_pct': ((price - old_price) / old_price * 100) if old_price else 0,
            'timestamp': datetime.now()
        })
    
    @timing_decorator
    def _calculate_metrics(self, symbol: str, data: Dict, old_price: float) -> MarketMetrics:
        """Calcular métricas de mercado avançadas"""
        price = data.get('price', 0)
        history = list(self.price_history[symbol])
        
        # Volatilidade
        volatility = self.technical_analyzer.calculate_volatility(history) if history else 0
        
        # Tendência
        trend_strength, trend_direction = self.technical_analyzer.calculate_trend_strength(history) if len(history) > 20 else (0, 0)
        
        # RSI
        rsi = self.technical_analyzer.calculate_rsi(history) if len(history) > 14 else 50
        
        # MACD
        macd, macd_signal, macd_hist = self.technical_analyzer.calculate_macd(history) if len(history) > 26 else (0, 0, 0)
        
        # Bollinger Bands
        bb_upper, bb_mid, bb_lower, bb_width, bb_pos = self.technical_analyzer.calculate_bollinger(history) if len(history) > 20 else (price, price, price, 0, 0.5)
        
        # Suporte/Resistência
        support, resistance, support_dist, resistance_dist = self.technical_analyzer.detect_support_resistance(
            history,
            list(self.high_history[symbol]),
            list(self.low_history[symbol])
        ) if len(history) > 20 else (price * 0.95, price * 1.05, 0.05, 0.05)
        
        # Retornos
        returns_1h = ((price / history[-2]) - 1) if len(history) >= 2 else 0
        returns_24h = ((price / history[-min(24, len(history))]) - 1) if history else 0
        returns_7d = ((price / history[-min(168, len(history))]) - 1) if len(history) >= 168 else 0
        
        return MarketMetrics(
            symbol=symbol,
            timestamp=datetime.now(),
            current_price=price,
            open_price=data.get('open', price),
            high_price=data.get('high', price),
            low_price=data.get('low', price),
            close_price=price,
            vwap=price,  # Simplificado
            volume_24h=data.get('volume', 0),
            volatility=volatility,
            trend_strength=trend_strength,
            trend_direction=trend_direction,
            adx=trend_strength * 50,  # Aproximação
            macd=macd,
            macd_signal=macd_signal,
            macd_histogram=macd_hist,
            momentum=price - old_price,
            momentum_1h=returns_1h * price,
            momentum_24h=returns_24h * price,
            rsi=rsi,
            bollinger_width=bb_width,
            atr=volatility * price,  # Aproximação
            nearest_support=support,
            nearest_resistance=resistance,
            support_distance=support_dist,
            resistance_distance=resistance_dist,
            returns_1h=returns_1h,
            returns_24h=returns_24h,
            returns_7d=returns_7d
        )
    
    # =========================================================================
    # DETECÇÃO DE OPORTUNIDADES
    # =========================================================================
    
    def _detect_opportunities(self, symbol: str, metrics: MarketMetrics) -> List[TradingOpportunity]:
        """Detectar oportunidades usando todas as estratégias"""
        opportunities = []
        history = list(self.price_history[symbol])
        
        for strategy in self.strategies:
            try:
                opportunity = strategy.analyze(symbol, metrics, history)
                if opportunity:
                    opportunities.append(opportunity)
                    logger.info(f"🎯 Oportunidade detectada: {symbol} - {opportunity.signal.value} "
                              f"(Conf: {opportunity.confidence:.1%})")
            except Exception as e:
                logger.error(f"Erro na estratégia {strategy.name} para {symbol}: {e}")
        
        return opportunities
    
    def _process_opportunity(self, opportunity: TradingOpportunity):
        """Processar oportunidade detectada"""
        self.opportunities.append(opportunity)
        self._trigger_callbacks('on_opportunity', opportunity.to_dict())
    
    # =========================================================================
    # DETECÇÃO DE ALERTAS
    # =========================================================================
    
    def _detect_alerts(self, symbol: str, data: Dict):
        """Detectar e gerar alertas"""
        price = data.get('price', 0)
        old_price = self.current_prices.get(symbol, price)
        
        # ALERTA 1: Mudança significativa de preço
        if old_price and old_price > 0:
            change_pct = abs(price - old_price) / old_price
            
            if change_pct > self.config['price_change_threshold']:
                alert_type = AlertType.PRICE_JUMP if price > old_price else AlertType.PRICE_DROP
                severity = AlertSeverity.WARNING if change_pct > 0.05 else AlertSeverity.INFO
                
                alert = MarketAlert(
                    timestamp=datetime.now(),
                    symbol=symbol,
                    severity=severity,
                    alert_type=alert_type,
                    message=f"{'Salto' if price > old_price else 'Queda'} de preço: {change_pct*100:.2f}%",
                    price=price,
                    condition=MarketCondition.VOLATILE if change_pct > 0.03 else MarketCondition.CONSOLIDATION,
                    confidence=min(0.9, change_pct * 10),
                    data={'old_price': old_price, 'change_pct': change_pct}
                )
                self.alert_queue.put(alert)
        
        # ALERTA 2: Volume anormal
        volume = data.get('volume', 0)
        if volume > 0 and symbol in self.volume_history and self.volume_history[symbol]:
            avg_volume = sum(self.volume_history[symbol]) / len(self.volume_history[symbol])
            volume_ratio = volume / avg_volume if avg_volume > 0 else 1
            
            if volume_ratio > self.config['volume_threshold']:
                alert = MarketAlert(
                    timestamp=datetime.now(),
                    symbol=symbol,
                    severity=AlertSeverity.WARNING,
                    alert_type=AlertType.VOLUME_SPIKE,
                    message=f"Volume {volume_ratio:.1f}x acima da média",
                    price=price,
                    condition=MarketCondition.BREAKOUT_UP if price > old_price else MarketCondition.BREAKOUT_DOWN,
                    confidence=min(0.85, volume_ratio * 0.5),
                    data={'volume': volume, 'avg_volume': avg_volume, 'ratio': volume_ratio}
                )
                self.alert_queue.put(alert)
        
        # ALERTA 3: Quebra de suporte/resistência
        metrics = self.metrics.get(symbol)
        if metrics:
            if metrics.support_distance < 0.005:
                alert = MarketAlert(
                    timestamp=datetime.now(),
                    symbol=symbol,
                    severity=AlertSeverity.CRITICAL if price < metrics.nearest_support else AlertSeverity.WARNING,
                    alert_type=AlertType.SUPPORT_BREAK if price < metrics.nearest_support else AlertType.RESISTANCE_BREAK,
                    message=f"Quebra de {'suporte' if price < metrics.nearest_support else 'resistência'}",
                    price=price,
                    condition=MarketCondition.BREAKOUT_DOWN if price < metrics.nearest_support else MarketCondition.BREAKOUT_UP,
                    confidence=0.8,
                    data={'level': metrics.nearest_support if price < metrics.nearest_support else metrics.nearest_resistance,
                          'distance': metrics.support_distance if price < metrics.nearest_support else metrics.resistance_distance}
                )
                self.alert_queue.put(alert)
                self._trigger_callbacks('on_level_break', alert.to_dict())
    
    def _process_alert(self, alert: MarketAlert):
        """Processar alerta gerado"""
        self.alerts.append(alert)
        
        # Log do alerta
        if alert.severity == AlertSeverity.CRITICAL:
            logger.critical(f"🚨 ALERTA {alert.symbol}: {alert.message}")
        elif alert.severity == AlertSeverity.WARNING:
            logger.warning(f"⚠️ ALERTA {alert.symbol}: {alert.message}")
        else:
            logger.info(f"ℹ️ ALERTA {alert.symbol}: {alert.message}")
        
        # Disparar callback
        self._trigger_callbacks('on_alert', alert.to_dict())
        
        # Webhook se configurado
        if self.config['enable_webhooks'] and self.config['webhook_url']:
            self._send_webhook(alert)
    
    def _send_webhook(self, alert: MarketAlert):
        """Enviar alerta via webhook"""
        if not REQUESTS_AVAILABLE:
            return
        
        try:
            requests.post(
                self.config['webhook_url'],
                json=alert.to_dict(),
                timeout=5
            )
        except Exception as e:
            logger.error(f"Erro ao enviar webhook: {e}")
    
    # =========================================================================
    # INTERFACE PÚBLICA
    # =========================================================================
    
    def get_summary(self, symbol: str) -> Dict[str, Any]:
        """Obter resumo do mercado para um símbolo"""
        metrics = self.metrics.get(symbol)
        if not metrics:
            return {'symbol': symbol, 'error': 'No data available'}
        
        patterns = self.patterns.get(symbol, [])
        
        return {
            'symbol': symbol,
            'timestamp': metrics.timestamp.isoformat(),
            'price': metrics.current_price,
            'price_change_24h': f"{metrics.returns_24h*100:.2f}%",
            'volume_24h': metrics.volume_24h,
            'volatility': f"{metrics.volatility*100:.2f}%",
            'trend': {
                'strength': f"{metrics.trend_strength*100:.1f}%",
                'direction': 'UP' if metrics.trend_direction > 0 else 'DOWN' if metrics.trend_direction < 0 else 'SIDEWAYS',
                'adx': metrics.adx
            },
            'momentum': {
                'rsi': metrics.rsi,
                'macd': metrics.macd,
                'macd_signal': metrics.macd_signal
            },
            'levels': {
                'support': metrics.nearest_support,
                'resistance': metrics.nearest_resistance,
                'support_distance': f"{metrics.support_distance*100:.1f}%",
                'resistance_distance': f"{metrics.resistance_distance*100:.1f}%"
            },
            'patterns': len(patterns),
            'top_patterns': patterns[:3] if patterns else []
        }
    
    def get_all_summaries(self) -> Dict[str, Dict[str, Any]]:
        """Obter resumos de todos os símbolos"""
        return {symbol: self.get_summary(symbol) for symbol in self.symbols}
    
    def get_recent_alerts(self, limit: int = 100, severity: Optional[AlertSeverity] = None) -> List[Dict]:
        """Obter alertas recentes"""
        alerts = list(self.alerts)[-limit:]
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        return [a.to_dict() for a in alerts]
    
    def get_recent_opportunities(self, limit: int = 50, signal: Optional[TradingSignal] = None) -> List[Dict]:
        """Obter oportunidades recentes"""
        opportunities = list(self.opportunities)[-limit:]
        
        if signal:
            opportunities = [o for o in opportunities if o.signal == signal]
        
        return [o.to_dict() for o in opportunities]
    
    def get_strategy_performance(self) -> Dict[str, Dict[str, float]]:
        """Obter performance das estratégias"""
        return {
            strategy.name: {
                'trades': strategy.performance['trades'],
                'win_rate': strategy.performance['win_rate'],
                'total_pnl': strategy.performance['total_pnl']
            }
            for strategy in self.strategies
        }
    
    # =========================================================================
    # EXPORTAÇÃO DE DADOS
    # =========================================================================
    
    def export_alerts(self, filepath: Optional[str] = None) -> str:
        """Exportar alertas para arquivo JSON"""
        if not filepath:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = f"alerts_export_{timestamp}.json"
        
        try:
            alerts_data = [a.to_dict() for a in self.alerts]
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(alerts_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 {len(self.alerts)} alertas exportados para {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"❌ Erro ao exportar alertas: {e}")
            raise
    
    def export_opportunities(self, filepath: Optional[str] = None) -> str:
        """Exportar oportunidades para arquivo JSON"""
        if not filepath:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = f"opportunities_export_{timestamp}.json"
        
        try:
            opportunities_data = [o.to_dict() for o in self.opportunities]
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(opportunities_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"💾 {len(self.opportunities)} oportunidades exportadas para {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"❌ Erro ao exportar oportunidades: {e}")
            raise
    
    def export_metrics(self, symbol: Optional[str] = None, filepath: Optional[str] = None) -> str:
        """Exportar métricas para arquivo JSON"""
        if not filepath:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = f"metrics_export_{timestamp}.json"
        
        try:
            if symbol:
                metrics_data = self.metrics.get(symbol)
                data = metrics_data.to_dict() if metrics_data else {}
            else:
                data = {s: m.to_dict() for s, m in self.metrics.items()}
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"💾 Métricas exportadas para {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"❌ Erro ao exportar métricas: {e}")
            raise
    
    def _auto_export(self):
        """Exportação automática de dados"""
        try:
            os.makedirs(self.config['export_path'], exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H')
            base_path = Path(self.config['export_path']) / timestamp
            
            # Exportar a cada hora
            if datetime.now().minute == 0:
                self.export_alerts(str(base_path / 'alerts.json'))
                self.export_opportunities(str(base_path / 'opportunities.json'))
                self.export_metrics(filepath=str(base_path / 'metrics.json'))
                
        except Exception as e:
            logger.error(f"Erro na exportação automática: {e}")
    
    # =========================================================================
    # CONFIGURAÇÃO
    # =========================================================================
    
    def update_config(self, **kwargs):
        """Atualizar configurações"""
        self.config.update(kwargs)
        logger.info(f"⚙️ Configurações atualizadas: {kwargs}")
    
    def add_symbol(self, symbol: str):
        """Adicionar símbolo ao monitoramento"""
        if symbol not in self.symbols:
            self.symbols.append(symbol)
            self.price_history[symbol] = deque(maxlen=MAX_HISTORY_SIZE)
            self.high_history[symbol] = deque(maxlen=MAX_HISTORY_SIZE)
            self.low_history[symbol] = deque(maxlen=MAX_HISTORY_SIZE)
            self.volume_history[symbol] = deque(maxlen=MAX_HISTORY_SIZE)
            self.price_levels[symbol] = []
            self.patterns[symbol] = []
            logger.info(f"➕ Símbolo adicionado: {symbol}")
    
    def remove_symbol(self, symbol: str):
        """Remover símbolo do monitoramento"""
        if symbol in self.symbols:
            self.symbols.remove(symbol)
            del self.price_history[symbol]
            del self.high_history[symbol]
            del self.low_history[symbol]
            del self.volume_history[symbol]
            del self.price_levels[symbol]
            del self.patterns[symbol]
            logger.info(f"➖ Símbolo removido: {symbol}")
    
    def add_strategy(self, strategy: TradingStrategy):
        """Adicionar estratégia"""
        self.strategies.append(strategy)
        logger.info(f"➕ Estratégia adicionada: {strategy.name}")
    
    def remove_strategy(self, strategy_name: str):
        """Remover estratégia"""
        self.strategies = [s for s in self.strategies if s.name != strategy_name]
        logger.info(f"➖ Estratégia removida: {strategy_name}")
    
    # =========================================================================
    # ESTATÍSTICAS E RELATÓRIOS
    # =========================================================================
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obter status do sistema"""
        return {
            'is_running': self.is_running,
            'symbols_monitored': len(self.symbols),
            'total_alerts': len(self.alerts),
            'total_opportunities': len(self.opportunities),
            'active_strategies': len(self.strategies),
            'data_source': self.data_source.value,
            'update_frequency': self.update_frequency,
            'memory_usage': {
                'price_history': sum(len(h) for h in self.price_history.values()),
                'alerts': len(self.alerts),
                'opportunities': len(self.opportunities)
            },
            'performance': {
                'alerts_per_minute': len([a for a in self.alerts if a.timestamp > datetime.now() - timedelta(minutes=60)]) / 60,
                'opportunities_per_hour': len([o for o in self.opportunities if o.timestamp > datetime.now() - timedelta(hours=1)]),
                'strategy_win_rates': self.get_strategy_performance()
            },
            'timestamp': datetime.now()
        }
    
    def generate_report(self) -> str:
        """Gerar relatório de mercado"""
        report = []
        report.append("=" * 80)
        report.append(f"VHALINOR IAG - RELATÓRIO DE MERCADO")
        report.append(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        report.append("=" * 80)
        report.append("")
        
        # Resumo geral
        report.append("[SUMMARY] RESUMO GERAL:")
        report.append(f"   Símbolos monitorados: {len(self.symbols)}")
        report.append(f"   Alertas ativos: {len(self.alerts)}")
        report.append(f"   Oportunidades detectadas: {len(self.opportunities)}")
        report.append(f"   Estratégias ativas: {len(self.strategies)}")
        report.append("")
        
        # Performance das estratégias
        report.append("[PERFORMANCE] PERFORMANCE DAS ESTRATÉGIAS:")
        for strategy in self.strategies:
            perf = strategy.performance
            report.append(f"   {strategy.name}:")
            report.append(f"     - Trades: {perf['trades']}")
            report.append(f"     - Win Rate: {perf['win_rate']:.1%}")
            report.append(f"     - PNL Total: {perf['total_pnl']:.4f}")
        report.append("")
        
        # Top oportunidades
        report.append("[OPPORTUNITIES] TOP OPORTUNIDADES:")
        opportunities = list(self.opportunities)[-5:]
        for opp in reversed(opportunities):
            report.append(f"   {opp.symbol}: {opp.signal.value} "
                        f"(Conf: {opp.confidence:.1%}, R:R: 1:{opp.risk_reward:.2f})")
        report.append("")
        
        # Alertas críticos
        report.append("[ALERTS] ALERTAS CRÍTICOS:")
        critical_alerts = [a for a in self.alerts if a.severity == AlertSeverity.CRITICAL][-5:]
        for alert in reversed(critical_alerts):
            report.append(f"   {alert.symbol}: {alert.message} "
                        f"({alert.timestamp.strftime('%H:%M:%S')})")
        report.append("")
        
        # Resumo por símbolo
        report.append("[SYMBOLS] RESUMO POR SÍMBOLO:")
        for symbol in self.symbols[:10]:  # Limitar a 10 símbolos
            summary = self.get_summary(symbol)
            if 'error' not in summary:
                report.append(f"   {symbol}:")
                report.append(f"     - Preço: {summary['price']:.4f}")
                report.append(f"     - Variação 24h: {summary['price_change_24h']}")
                report.append(f"     - RSI: {summary['momentum']['rsi']:.1f}")
                report.append(f"     - Tendência: {summary['trend']['direction']}")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)


# =============================================================================
# EXEMPLO DE USO
# =============================================================================

async def example_usage():
    """Exemplo de uso do Market Monitor"""
    
    print("=" * 80)
    print("VHALINOR IAG 1.0.0 - Exemplo de Monitor de Mercado")
    print("=" * 80)
    
    # ===== 1. INICIALIZAR MONITOR =====
    print("\n[1] Inicializando Market Monitor...")
    
    monitor = MarketMonitor(
        symbols=['AAPL', 'MSFT', 'GOOGL', 'BTC-USD', 'ETH-USD'],
        update_frequency=30,
        data_source=DataSource.YAHOO_FINANCE
    )
    
    # ===== 2. REGISTRAR CALLBACKS =====
    print("\n[2] Registrando callbacks...")
    
    def on_price_update(data):
        print(f"   📊 {data['symbol']}: ${data['price']:.2f} ({data['change_pct']:+.2f}%)")
    
    def on_alert(alert):
        severity_icon = {
            'INFO': 'ℹ️',
            'WARNING': '⚠️',
            'CRITICAL': '🚨',
            'EMERGENCY': '💀'
        }.get(alert.get('severity'), '🔔')
        
        print(f"   {severity_icon} {alert['symbol']}: {alert['message']}")
    
    def on_opportunity(opp):
        print(f"   🎯 {opp['symbol']}: {opp['signal']} "
              f"(Conf: {opp['confidence']:.1%}, R:R: 1:{opp['risk_reward']:.2f})")
    
    monitor.register_callback('on_price_update', on_price_update)
    monitor.register_callback('on_alert', on_alert)
    monitor.register_callback('on_opportunity', on_opportunity)
    
    # ===== 3. CONFIGURAR =====
    print("\n[3] Configurando monitor...")
    
    monitor.update_config(
        price_change_threshold=0.01,  # 1%
        volume_threshold=1.3,         # 130%
        enable_patterns=True,
        auto_export=False
    )
    
    # ===== 4. INICIAR MONITOR =====
    print("\n[4] Iniciando monitoramento...")
    monitor.start()
    
    # ===== 5. AGUARDAR COLETA DE DADOS =====
    print("\n[5] Aguardando coleta de dados (30 segundos)...")
    await asyncio.sleep(30)
    
    # ===== 6. EXIBIR RESUMO =====
    print("\n[6] Resumo do Mercado:")
    print("-" * 60)
    
    summaries = monitor.get_all_summaries()
    for symbol, summary in summaries.items():
        if 'error' not in summary:
            print(f"\n   📈 {symbol}:")
            print(f"      Preço: ${summary['price']:.2f}")
            print(f"      Variação 24h: {summary['price_change_24h']}")
            print(f"      RSI: {summary['momentum']['rsi']:.1f}")
            print(f"      Tendência: {summary['trend']['direction']} "
                  f"(Força: {summary['trend']['strength']})")

    # ===== 7. EXIBIR PERFORMANCE =====
    print("\n[7] Performance das Estratégias:")
    print("-" * 60)

    performance = monitor.get_strategy_performance()
    for strategy, perf in performance.items():
        print(f"\n   [STRATEGY] {strategy}:")
        print(f"      Trades: {perf['trades']}")
        print(f"      Win Rate: {perf['win_rate']:.1%}")
        print(f"      PNL: {perf['total_pnl']:.4f}")

    # ===== 8. GERAR RELATÓRIO =====
    print("\n[8] Gerando relatório...")
    report = monitor.generate_report()
    print(report)

    
    # ===== 9. EXPORTAR DADOS =====
    print("\n[9] Exportando dados...")
    
    try:
        alerts_file = monitor.export_alerts()
        print(f"   [OK] Alertas exportados: {alerts_file}")
        
        opps_file = monitor.export_opportunities()
        print(f"   [OK] Oportunidades exportadas: {opps_file}")
        
        metrics_file = monitor.export_metrics()
        print(f"   [OK] Métricas exportadas: {metrics_file}")
        
    except Exception as e:
        print(f"   [ERROR] Erro na exportação: {e}")
    
    # ===== 10. PARAR MONITOR =====
    print("\n[10] Parando monitor...")
    monitor.stop()
    
    print("\n" + "=" * 80)
    print("[SUCCESS] Exemplo concluido com sucesso!")
    print("=" * 80)


def main():
    """Função principal"""
    print("VHALINOR IAG - Market Monitor Quântico")
    print("Versão 2.0.0 - Production Ready")
    print()
    
    # Verificar dependências
    print("Verificando dependências...")
    print(f"   • NumPy: {'[OK]' if NUMPY_AVAILABLE else '[FAIL]'}")
    print(f"   • pandas: {'[OK]' if PANDAS_AVAILABLE else '[FAIL]'}")
    print(f"   • SciPy: {'[OK]' if SCIPY_AVAILABLE else '[FAIL]'}")
    print(f"   • yfinance: {'[OK]' if YFINANCE_AVAILABLE else '[FAIL]'}")
    print(f"   • requests: {'[OK]' if REQUESTS_AVAILABLE else '[FAIL]'}")
    print(f"   • websocket: {'[OK]' if WEBSOCKET_AVAILABLE else '[FAIL]'}")
    print(f"   • loguru: {'[OK]' if LOGURU_AVAILABLE else '[FAIL]'}")
    
    asyncio.run(example_usage())


if __name__ == "__main__":
    main()
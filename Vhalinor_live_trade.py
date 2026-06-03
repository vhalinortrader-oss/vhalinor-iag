# -*- coding: utf-8 -*-

"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    VHALINOR IAG 1.0.0 - MOTOR DE TRADING AO VIVO QUÂNTICO    ║
║         SISTEMA DE EXECUÇÃO AUTÔNOMA COM INTELIGÊNCIA ARTIFICIAL GERAL       ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  Módulo: CAMADA DE EXECUÇÃO - MOTOR DE TRADING (Layer 05)                    ║
║  Versão: 3.0.0 (Production Ready - Ultra Otimizada)                          ║
║  Autor: Alex Miranda Sales                                                    ║
║  Data: 2026                                                                   ║
║  License: Proprietary - Vhalinor IAG Systems                                  ║
║  Status: 🟢 TOTALMENTE OPERACIONAL | ⚡ LATÊNCIA <10ms | 🔗 MÚLTIPLAS CORRETORAS ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

# =============================================================================
# IMPORTAÇÕES OTIMIZADAS COM LAZY LOADING
# =============================================================================

import asyncio
import aiohttp
import aiohttp.client_exceptions
import websockets
import websockets.exceptions
import json
import time
import hmac
import hashlib
import base64
import pickle
import os
import sys
import uuid
import random
import math
import warnings
import gc
import signal
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple, Any, Union, Callable, Set
from enum import Enum, auto
from collections import defaultdict, deque
from functools import lru_cache, wraps
from contextlib import asynccontextmanager
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from pathlib import Path

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

try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# =============================================================================
# CONFIGURAÇÕES DE LOGGING AVANÇADAS
# =============================================================================

import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

LOG_FORMAT = '%(asctime)s | %(levelname)-8s | %(name)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Configurar handlers
file_handler = RotatingFileHandler(
    'vhalinor_trading.log',
    maxBytes=50*1024*1024,  # 50MB
    backupCount=10
)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))

# Configurar logger
logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)

logger = logging.getLogger('VhalinorLiveTrading')

# =============================================================================
# CONSTANTES E CONFIGURAÇÕES GLOBAIS
# =============================================================================

VERSION = "3.0.0"
CODENAME = "Quantum Execution"
BUILD_DATE = "2026-02-12"

# Configurações de performance
MAX_RETRIES = 5
RETRY_DELAY = 1.0
CIRCUIT_BREAKER_THRESHOLD = 5
CIRCUIT_BREAKER_TIMEOUT = 60
HEALTH_CHECK_INTERVAL = 30
WEBSOCKET_RECONNECT_DELAY = 5
RATE_LIMIT_PER_MINUTE = 1200
BATCH_SIZE = 100
MAX_CONCURRENT_REQUESTS = 20

# Configurações de risco
MAX_POSITION_SIZE_PERCENT = 0.10  # 10% do capital
MAX_LEVERAGE = 10
MIN_ACCOUNT_BALANCE = 10.0
MAX_DAILY_TRADES = 100
MAX_OPEN_POSITIONS = 20
STOP_LOSS_DEFAULT = 0.02  # 2%
TAKE_PROFIT_DEFAULT = 0.04  # 4%
TRAILING_STOP_DISTANCE = 0.01  # 1%

# Configurações de memória
MAX_ORDER_HISTORY = 10000
MAX_TRADE_HISTORY = 10000
MAX_POSITION_HISTORY = 1000
CACHE_TTL = 5  # segundos

# =============================================================================
# ENUMS E CONSTANTES AVANÇADAS
# =============================================================================

class OrderType(Enum):
    """Tipos de ordens com ícones e descrições"""
    MARKET = ("MARKET", "⚡", "Ordem a mercado")
    LIMIT = ("LIMIT", "🎯", "Ordem limitada")
    STOP = ("STOP", "🛑", "Ordem stop")
    STOP_LIMIT = ("STOP_LIMIT", "🎯🛑", "Ordem stop-limit")
    TRAILING_STOP = ("TRAILING_STOP", "📉", "Stop móvel")
    OCO = ("OCO", "🔄", "One-Cancels-Other")
    ICEBERG = ("ICEBERG", "🧊", "Ordem iceberg")
    
    def __init__(self, label: str, icon: str, descricao: str):
        self.label = label
        self.icon = icon
        self.descricao = descricao

class OrderSide(Enum):
    """Lados da ordem"""
    BUY = ("BUY", "🟢", "Compra")
    SELL = ("SELL", "🔴", "Venda")
    
    def __init__(self, label: str, icon: str, descricao: str):
        self.label = label
        self.icon = icon
        self.descricao = descricao

class OrderStatus(Enum):
    """Status de ordens com ícones"""
    PENDING = ("PENDING", "⏳", "Pendente")
    FILLED = ("FILLED", "✅", "Executada")
    PARTIALLY_FILLED = ("PARTIALLY_FILLED", "🟡", "Parcialmente executada")
    CANCELLED = ("CANCELLED", "❌", "Cancelada")
    REJECTED = ("REJECTED", "⚠️", "Rejeitada")
    EXPIRED = ("EXPIRED", "⌛", "Expirada")
    NEW = ("NEW", "🆕", "Nova")
    
    def __init__(self, label: str, icon: str, descricao: str):
        self.label = label
        self.icon = icon
        self.descricao = descricao

class TimeInForce(Enum):
    """Tempo em vigor da ordem"""
    GTC = ("GTC", "Good Till Cancelled")
    IOC = ("IOC", "Immediate or Cancel")
    FOK = ("FOK", "Fill or Kill")
    DAY = ("DAY", "Dia")
    
    def __init__(self, code: str, descricao: str):
        self.code = code
        self.descricao = descricao

class BrokerType(Enum):
    """Tipos de corretora suportados"""
    BINANCE = ("Binance", "🟡", "Spot/Futures")
    BINANCE_FUTURES = ("Binance Futures", "⚡", "Futuros Perpétuos")
    ALPACA = ("Alpaca", "🦙", "Ações/ETFs")
    BYBIT = ("Bybit", "🔵", "Futuros Perpétuos")
    KRAKEN = ("Kraken", "🐙", "Spot/Futures")
    COINBASE = ("Coinbase", "🔷", "Spot")
    FTX = ("FTX", "🟠", "Futuros/Spot")
    SIMULATOR = ("Simulador", "💻", "Papel Trading")
    
    def __init__(self, label: str, icon: str, descricao: str):
        self.label = label
        self.icon = icon
        self.descricao = descricao

class CircuitBreakerState(Enum):
    """Estados do circuit breaker"""
    CLOSED = ("CLOSED", "🟢", "Normal")
    OPEN = ("OPEN", "🔴", "Bloqueado")
    HALF_OPEN = ("HALF_OPEN", "🟡", "Meio aberto")
    
    def __init__(self, label: str, icon: str, descricao: str):
        self.label = label
        self.icon = icon
        self.descricao = descricao

class ExecutionQuality(Enum):
    """Qualidade da execução"""
    EXCELLENT = ("Excelente", "🏆", 0.99)
    GOOD = ("Bom", "👍", 0.95)
    FAIR = ("Regular", "👌", 0.90)
    POOR = ("Ruim", "👎", 0.80)
    CRITICAL = ("Crítico", "💀", 0.70)
    
    def __init__(self, label: str, icon: str, score: float):
        self.label = label
        self.icon = icon
        self.score = score

# =============================================================================
# DECORADORES AVANÇADOS
# =============================================================================

def timing_decorator(func):
    """Mede tempo de execução"""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            result = await func(*args, **kwargs)
            elapsed = time.perf_counter() - start
            if elapsed > 0.01:  # > 10ms
                logger.debug(f"⏱️ {func.__name__} executado em {elapsed*1000:.2f}ms")
            return result
        except Exception as e:
            elapsed = time.perf_counter() - start
            logger.error(f"❌ {func.__name__} falhou após {elapsed*1000:.2f}ms: {e}")
            raise
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            elapsed = time.perf_counter() - start
            if elapsed > 0.01:
                logger.debug(f"⏱️ {func.__name__} executado em {elapsed*1000:.2f}ms")
            return result
        except Exception as e:
            elapsed = time.perf_counter() - start
            logger.error(f"❌ {func.__name__} falhou após {elapsed*1000:.2f}ms: {e}")
            raise
    
    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

def retry(max_retries: int = MAX_RETRIES, delay: float = RETRY_DELAY, 
          backoff: float = 2.0, exceptions: tuple = (Exception,)):
    """Retry decorator com backoff exponencial"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_retries - 1:
                        logger.error(f"❌ {func.__name__} falhou após {max_retries} tentativas: {e}")
                        raise
                    wait = delay * (backoff ** attempt)
                    logger.warning(f"⚠️ Tentativa {attempt + 1}/{max_retries} falhou: {e}. "
                                 f"Tentando novamente em {wait:.1f}s...")
                    await asyncio.sleep(wait)
            raise last_exception
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_retries - 1:
                        logger.error(f"❌ {func.__name__} falhou após {max_retries} tentativas: {e}")
                        raise
                    wait = delay * (backoff ** attempt)
                    logger.warning(f"⚠️ Tentativa {attempt + 1}/{max_retries} falhou: {e}. "
                                 f"Tentando novamente em {wait:.1f}s...")
                    time.sleep(wait)
            raise last_exception
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

def rate_limit(calls_per_minute: int = RATE_LIMIT_PER_MINUTE):
    """Rate limiting decorator"""
    def decorator(func):
        last_called = [0.0]
        calls = deque(maxlen=calls_per_minute)
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            now = time.time()
            minute_ago = now - 60
            
            # Limpar chamadas antigas
            while calls and calls[0] < minute_ago:
                calls.popleft()
            
            if len(calls) >= calls_per_minute:
                wait_time = calls[0] + 60 - now
                if wait_time > 0:
                    logger.warning(f"⚠️ Rate limit atingido. Aguardando {wait_time:.1f}s...")
                    await asyncio.sleep(wait_time)
            
            calls.append(now)
            return await func(*args, **kwargs)
        
        return async_wrapper
    return decorator

def circuit_breaker(failure_threshold: int = CIRCUIT_BREAKER_THRESHOLD,
                   recovery_timeout: int = CIRCUIT_BREAKER_TIMEOUT):
    """Circuit breaker decorator"""
    def decorator(func):
        state = CircuitBreakerState.CLOSED
        failure_count = 0
        last_failure_time = 0
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            nonlocal state, failure_count, last_failure_time
            
            if state == CircuitBreakerState.OPEN:
                if time.time() - last_failure_time > recovery_timeout:
                    state = CircuitBreakerState.HALF_OPEN
                    logger.info(f"🔄 Circuit breaker half-open para {func.__name__}")
                else:
                    raise Exception(f"Circuit breaker OPEN para {func.__name__}")
            
            try:
                result = await func(*args, **kwargs)
                
                if state == CircuitBreakerState.HALF_OPEN:
                    state = CircuitBreakerState.CLOSED
                    failure_count = 0
                    logger.info(f"✅ Circuit breaker fechado para {func.__name__}")
                
                return result
                
            except Exception as e:
                failure_count += 1
                last_failure_time = time.time()
                
                if failure_count >= failure_threshold:
                    state = CircuitBreakerState.OPEN
                    logger.error(f"🔴 Circuit breaker OPEN para {func.__name__} após {failure_count} falhas")
                
                raise
        
        return async_wrapper
    return decorator

@asynccontextmanager
async def websocket_connection(url: str, **kwargs):
    """Context manager para conexões WebSocket"""
    websocket = None
    try:
        websocket = await websockets.connect(url, **kwargs)
        yield websocket
    finally:
        if websocket:
            await websocket.close()

@asynccontextmanager
async def http_session():
    """Context manager para sessões HTTP"""
    session = None
    try:
        session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=MAX_CONCURRENT_REQUESTS)
        )
        yield session
    finally:
        if session:
            await session.close()

# =============================================================================
# ESTRUTURAS DE DADOS AVANÇADAS
# =============================================================================

@dataclass
class TradingSignal:
    """Sinal de trading avançado"""
    id: str
    symbol: str
    action: OrderSide
    confidence: float
    price: float
    stop_loss: float
    take_profit: float
    timestamp: datetime
    signal_type: str
    strategy_name: str
    timeframe: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.id:
            self.id = f"SIG_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.symbol}_{hashlib.md5(str(time.time()).encode()).hexdigest()[:4]}"
    
    @property
    def risk_reward_ratio(self) -> float:
        """Calcula relação risco/retorno"""
        if self.action == OrderSide.BUY:
            risk = self.price - self.stop_loss
            reward = self.take_profit - self.price
        else:
            risk = self.stop_loss - self.price
            reward = self.price - self.take_profit
        
        return reward / risk if risk > 0 else 0
    
    @property
    def potential_profit_percent(self) -> float:
        """Calcula percentual de lucro potencial"""
        if self.action == OrderSide.BUY:
            return ((self.take_profit - self.price) / self.price) * 100
        else:
            return ((self.price - self.take_profit) / self.price) * 100
    
    @property
    def potential_loss_percent(self) -> float:
        """Calcula percentual de perda potencial"""
        if self.action == OrderSide.BUY:
            return ((self.price - self.stop_loss) / self.price) * 100
        else:
            return ((self.stop_loss - self.price) / self.price) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'action': self.action.label,
            'action_icon': self.action.icon,
            'confidence': self.confidence,
            'price': self.price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'timestamp': self.timestamp.isoformat(),
            'signal_type': self.signal_type,
            'strategy_name': self.strategy_name,
            'risk_reward': self.risk_reward_ratio,
            'potential_profit': self.potential_profit_percent,
            'potential_loss': self.potential_loss_percent
        }

@dataclass
class Order:
    """Ordem avançada com validação"""
    id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: Decimal
    price: Optional[Decimal] = None
    stop_price: Optional[Decimal] = None
    limit_price: Optional[Decimal] = None
    time_in_force: TimeInForce = TimeInForce.GTC
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    filled_at: Optional[datetime] = None
    filled_price: Optional[Decimal] = None
    filled_quantity: Decimal = Decimal('0')
    commission: Decimal = Decimal('0')
    commission_asset: str = 'USDT'
    client_order_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    iceberg_qty: Optional[Decimal] = None
    trail_value: Optional[Decimal] = None
    trail_asset: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if isinstance(self.quantity, (int, float)):
            self.quantity = Decimal(str(self.quantity))
        if self.price and isinstance(self.price, (int, float)):
            self.price = Decimal(str(self.price))
        if self.stop_price and isinstance(self.stop_price, (int, float)):
            self.stop_price = Decimal(str(self.stop_price))
        if self.filled_quantity and isinstance(self.filled_quantity, (int, float)):
            self.filled_quantity = Decimal(str(self.filled_quantity))
        if self.commission and isinstance(self.commission, (int, float)):
            self.commission = Decimal(str(self.commission))
    
    @property
    def remaining_quantity(self) -> Decimal:
        """Quantidade restante a ser preenchida"""
        return self.quantity - self.filled_quantity
    
    @property
    def is_complete(self) -> bool:
        """Verifica se ordem está completamente preenchida"""
        return self.filled_quantity >= self.quantity
    
    @property
    def avg_fill_price(self) -> Optional[Decimal]:
        """Preço médio de preenchimento"""
        if self.filled_quantity > 0 and self.filled_price:
            return self.filled_price
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'side': self.side.label,
            'side_icon': self.side.icon,
            'order_type': self.order_type.label,
            'order_type_icon': self.order_type.icon,
            'quantity': float(self.quantity),
            'price': float(self.price) if self.price else None,
            'status': self.status.label,
            'status_icon': self.status.icon,
            'filled_quantity': float(self.filled_quantity),
            'filled_price': float(self.filled_price) if self.filled_price else None,
            'commission': float(self.commission),
            'created_at': self.created_at.isoformat(),
            'filled_at': self.filled_at.isoformat() if self.filled_at else None
        }

@dataclass
class Position:
    """Posição avançada com cálculos"""
    id: str
    symbol: str
    side: OrderSide
    quantity: Decimal
    avg_price: Decimal
    current_price: Decimal = Decimal('0')
    unrealized_pnl: Decimal = Decimal('0')
    realized_pnl: Decimal = Decimal('0')
    stop_loss: Optional[Decimal] = None
    take_profit: Optional[Decimal] = None
    trailing_stop: Optional[Decimal] = None
    highest_price: Decimal = Decimal('0')
    lowest_price: Decimal = Decimal('0')
    opened_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if isinstance(self.quantity, (int, float)):
            self.quantity = Decimal(str(self.quantity))
        if isinstance(self.avg_price, (int, float)):
            self.avg_price = Decimal(str(self.avg_price))
        if isinstance(self.current_price, (int, float)):
            self.current_price = Decimal(str(self.current_price))
    
    @property
    def value(self) -> Decimal:
        """Valor atual da posição"""
        return self.quantity * self.current_price
    
    @property
    def cost(self) -> Decimal:
        """Custo total da posição"""
        return self.quantity * self.avg_price
    
    @property
    def unrealized_pnl_percent(self) -> float:
        """P&L não realizado percentual"""
        if self.cost == 0:
            return 0.0
        return float((self.value - self.cost) / self.cost * 100)
    
    @property
    def distance_to_stop(self) -> Optional[float]:
        """Distância percentual até o stop loss"""
        if not self.stop_loss or self.stop_loss == 0:
            return None
        
        if self.side == OrderSide.BUY:
            return float((self.current_price - self.stop_loss) / self.current_price * 100)
        else:
            return float((self.stop_loss - self.current_price) / self.current_price * 100)
    
    @property
    def distance_to_target(self) -> Optional[float]:
        """Distância percentual até o take profit"""
        if not self.take_profit or self.take_profit == 0:
            return None
        
        if self.side == OrderSide.BUY:
            return float((self.take_profit - self.current_price) / self.current_price * 100)
        else:
            return float((self.current_price - self.take_profit) / self.current_price * 100)
    
    def update_trailing_stop(self) -> Optional[Decimal]:
        """Atualiza trailing stop"""
        if not self.trailing_stop:
            return None
        
        if self.side == OrderSide.BUY:
            if self.current_price > self.highest_price:
                self.highest_price = self.current_price
                new_stop = self.highest_price * (1 - self.trailing_stop)
                if not self.stop_loss or new_stop > self.stop_loss:
                    self.stop_loss = new_stop
        else:
            if self.current_price < self.lowest_price or self.lowest_price == 0:
                self.lowest_price = self.current_price
                new_stop = self.lowest_price * (1 + self.trailing_stop)
                if not self.stop_loss or new_stop < self.stop_loss:
                    self.stop_loss = new_stop
        
        return self.stop_loss
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'side': self.side.label,
            'side_icon': self.side.icon,
            'quantity': float(self.quantity),
            'avg_price': float(self.avg_price),
            'current_price': float(self.current_price),
            'value': float(self.value),
            'cost': float(self.cost),
            'unrealized_pnl': float(self.unrealized_pnl),
            'unrealized_pnl_percent': self.unrealized_pnl_percent,
            'realized_pnl': float(self.realized_pnl),
            'stop_loss': float(self.stop_loss) if self.stop_loss else None,
            'take_profit': float(self.take_profit) if self.take_profit else None,
            'opened_at': self.opened_at.isoformat()
        }

@dataclass
class AccountInfo:
    """Informações avançadas da conta"""
    id: str
    balance: Decimal
    available_balance: Decimal
    margin_balance: Decimal
    unrealized_pnl: Decimal
    realized_pnl: Decimal
    positions: Dict[str, Position]
    total_position_value: Decimal = Decimal('0')
    total_cost: Decimal = Decimal('0')
    margin_used: Decimal = Decimal('0')
    margin_free: Decimal = Decimal('0')
    margin_level: float = 0.0
    leverage: int = 1
    trading_enabled: bool = True
    daily_trades: int = 0
    daily_pnl: Decimal = Decimal('0')
    daily_volume: Decimal = Decimal('0')
    last_updated: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        if isinstance(self.balance, (int, float)):
            self.balance = Decimal(str(self.balance))
        if isinstance(self.available_balance, (int, float)):
            self.available_balance = Decimal(str(self.available_balance))
        
        # Calcular totais
        for position in self.positions.values():
            self.total_position_value += position.value
            self.total_cost += position.cost
        
        self.margin_used = self.total_position_value / self.leverage if self.leverage > 0 else 0
        self.margin_free = self.available_balance - self.margin_used
        self.margin_level = float((self.margin_balance / self.margin_used) * 100) if self.margin_used > 0 else 100.0
    
    @property
    def total_equity(self) -> Decimal:
        """Patrimônio total"""
        return self.balance + self.unrealized_pnl
    
    @property
    def total_pnl(self) -> Decimal:
        """P&L total"""
        return self.realized_pnl + self.unrealized_pnl
    
    @property
    def risk_percentage(self) -> float:
        """Percentual de risco baseado em posições abertas"""
        if self.total_equity == 0:
            return 0.0
        return float((self.total_position_value / self.total_equity) * 100)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário"""
        return {
            'id': self.id,
            'balance': float(self.balance),
            'available_balance': float(self.available_balance),
            'total_equity': float(self.total_equity),
            'unrealized_pnl': float(self.unrealized_pnl),
            'realized_pnl': float(self.realized_pnl),
            'total_pnl': float(self.total_pnl),
            'margin_level': self.margin_level,
            'leverage': self.leverage,
            'risk_percentage': self.risk_percentage,
            'daily_trades': self.daily_trades,
            'daily_pnl': float(self.daily_pnl),
            'daily_volume': float(self.daily_volume),
            'open_positions': len(self.positions),
            'last_updated': self.last_updated.isoformat()
        }

@dataclass
class Trade:
    """Trade executado"""
    id: str
    order_id: str
    symbol: str
    side: OrderSide
    quantity: Decimal
    price: Decimal
    commission: Decimal
    commission_asset: str
    realized_pnl: Decimal
    executed_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'order_id': self.order_id,
            'symbol': self.symbol,
            'side': self.side.label,
            'quantity': float(self.quantity),
            'price': float(self.price),
            'commission': float(self.commission),
            'realized_pnl': float(self.realized_pnl),
            'executed_at': self.executed_at.isoformat()
        }

@dataclass
class ExecutionMetrics:
    """Métricas de execução"""
    total_orders: int = 0
    filled_orders: int = 0
    cancelled_orders: int = 0
    rejected_orders: int = 0
    avg_fill_time_ms: float = 0.0
    avg_slippage_pips: float = 0.0
    total_volume: Decimal = Decimal('0')
    total_commission: Decimal = Decimal('0')
    success_rate: float = 0.0
    execution_quality: ExecutionQuality = ExecutionQuality.GOOD
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'total_orders': self.total_orders,
            'filled_orders': self.filled_orders,
            'cancelled_orders': self.cancelled_orders,
            'rejected_orders': self.rejected_orders,
            'avg_fill_time_ms': self.avg_fill_time_ms,
            'avg_slippage_pips': self.avg_slippage_pips,
            'total_volume': float(self.total_volume),
            'total_commission': float(self.total_commission),
            'success_rate': self.success_rate,
            'execution_quality': self.execution_quality.label
        }

# =============================================================================
# CIRCUIT BREAKER
# =============================================================================

class CircuitBreaker:
    """Circuit breaker para proteção contra falhas em cascata"""
    
    def __init__(self, name: str, failure_threshold: int = CIRCUIT_BREAKER_THRESHOLD,
                 recovery_timeout: int = CIRCUIT_BREAKER_TIMEOUT):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0
        self.total_failures = 0
        self.total_successes = 0
        self._lock = asyncio.Lock()
    
    async def call(self, func, *args, **kwargs):
        """Executa função com proteção do circuit breaker"""
        async with self._lock:
            if self.state == CircuitBreakerState.OPEN:
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    self.state = CircuitBreakerState.HALF_OPEN
                    logger.info(f"🔄 {self.name}: Circuit breaker half-open")
                else:
                    raise Exception(f"Circuit breaker OPEN for {self.name}")
        
        try:
            result = await func(*args, **kwargs)
            
            async with self._lock:
                self.total_successes += 1
                
                if self.state == CircuitBreakerState.HALF_OPEN:
                    self.state = CircuitBreakerState.CLOSED
                    self.failure_count = 0
                    logger.info(f"✅ {self.name}: Circuit breaker closed")
            
            return result
            
        except Exception as e:
            async with self._lock:
                self.total_failures += 1
                self.failure_count += 1
                self.last_failure_time = time.time()
                
                if self.failure_count >= self.failure_threshold:
                    self.state = CircuitBreakerState.OPEN
                    logger.error(f"🔴 {self.name}: Circuit breaker OPEN after {self.failure_count} failures")
            
            raise e
    
    @property
    def success_rate(self) -> float:
        """Taxa de sucesso"""
        total = self.total_successes + self.total_failures
        return (self.total_successes / total * 100) if total > 0 else 100.0
    
    def reset(self):
        """Reset circuit breaker"""
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0
        logger.info(f"🔄 {self.name}: Circuit breaker reset")

# =============================================================================
# RATE LIMITER
# =============================================================================

class RateLimiter:
    """Rate limiter avançado com tokens"""
    
    def __init__(self, calls_per_minute: int = RATE_LIMIT_PER_MINUTE):
        self.calls_per_minute = calls_per_minute
        self.tokens = calls_per_minute
        self.last_refill = time.time()
        self._lock = asyncio.Lock()
    
    async def acquire(self):
        """Adquire permissão para fazer requisição"""
        async with self._lock:
            now = time.time()
            elapsed = now - self.last_refill
            
            # Refill tokens
            self.tokens += elapsed * (self.calls_per_minute / 60)
            if self.tokens > self.calls_per_minute:
                self.tokens = self.calls_per_minute
            self.last_refill = now
            
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            else:
                wait_time = (1 - self.tokens) * (60 / self.calls_per_minute)
                await asyncio.sleep(wait_time)
                self.tokens = 0
                return True

# =============================================================================
# INTERFACE ABSTRATA DO BROKER
# =============================================================================

class BrokerConnection(ABC):
    """Interface abstrata para conexão com corretoras"""
    
    def __init__(self, name: str, broker_type: BrokerType):
        self.name = name
        self.broker_type = broker_type
        self.connected = False
        self.session: Optional[aiohttp.ClientSession] = None
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.circuit_breaker = CircuitBreaker(f"{name}_broker")
        self.rate_limiter = RateLimiter()
        self.metrics = ExecutionMetrics()
        self.logger = logger.getChild(name)
    
    @abstractmethod
    async def connect(self) -> bool:
        """Conecta à API da corretora"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Desconecta da API"""
        pass
    
    @abstractmethod
    async def place_order(self, order: Order) -> Dict[str, Any]:
        """Envia ordem para a corretora"""
        pass
    
    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool:
        """Cancela uma ordem"""
        pass
    
    @abstractmethod
    async def get_order_status(self, order_id: str) -> OrderStatus:
        """Obtém status da ordem"""
        pass
    
    @abstractmethod
    async def get_account_info(self) -> AccountInfo:
        """Obtém informações da conta"""
        pass
    
    @abstractmethod
    async def get_positions(self) -> Dict[str, Position]:
        """Obtém posições atuais"""
        pass
    
    @abstractmethod
    async def get_current_price(self, symbol: str) -> float:
        """Obtém preço atual do símbolo"""
        pass
    
    @abstractmethod
    async def get_historical_prices(self, symbol: str, interval: str, limit: int = 100) -> List[Dict]:
        """Obtém preços históricos"""
        pass
    
    @abstractmethod
    async def get_exchange_info(self, symbol: str = None) -> Dict[str, Any]:
        """Obtém informações da exchange"""
        pass
    
    @abstractmethod
    async def subscribe_ticker(self, symbols: List[str], callback: Callable):
        """Inscreve para atualizações de ticker"""
        pass

# =============================================================================
# IMPLEMENTAÇÃO BINANCE
# =============================================================================

class BinanceBroker(BrokerConnection):
    """Implementação para Binance Spot/Futures"""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True,
                 futures: bool = False):
        super().__init__(
            name=f"Binance{' Futures' if futures else ''}",
            broker_type=BrokerType.BINANCE_FUTURES if futures else BrokerType.BINANCE
        )
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self.futures = futures
        
        # URLs
        if testnet:
            self.base_url = "https://testnet.binance.vision"
            self.futures_url = "https://testnet.binancefuture.com"
            self.ws_url = "wss://testnet.binance.vision/ws"
            self.futures_ws_url = "wss://stream.binancefuture.com/ws"
        else:
            self.base_url = "https://api.binance.com"
            self.futures_url = "https://fapi.binance.com"
            self.ws_url = "wss://stream.binance.com:9443/ws"
            self.futures_ws_url = "wss://fstream.binance.com/ws"
        
        self.listen_key = None
        self.subscriptions = {}
    
    async def connect(self) -> bool:
        """Conecta à API da Binance"""
        try:
            self.session = aiohttp.ClientSession(
                headers={'X-MBX-APIKEY': self.api_key},
                timeout=aiohttp.ClientTimeout(total=30)
            )
            
            # Testar conexão
            url = f"{self.base_url}/api/v3/ping"
            async with self.session.get(url) as response:
                if response.status == 200:
                    self.connected = True
                    self.logger.info(f"✅ Conectado à {self.name} {'(Testnet)' if self.testnet else ''}")
                    
                    # Iniciar keepalive para listen key se for futures
                    if self.futures:
                        asyncio.create_task(self._keepalive_listen_key())
                    
                    return True
                    
        except Exception as e:
            self.logger.error(f"❌ Erro ao conectar com {self.name}: {e}")
        
        return False
    
    async def disconnect(self) -> bool:
        """Desconecta da API"""
        if self.session:
            await self.session.close()
        if self.websocket:
            await self.websocket.close()
        
        self.connected = False
        self.logger.info(f"🔌 Desconectado da {self.name}")
        return True
    
    def _generate_signature(self, params: Dict) -> str:
        """Gera assinatura HMAC SHA256"""
        query_string = '&'.join([f"{key}={value}" for key, value in sorted(params.items())])
        return hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def _get_base_url(self) -> str:
        """Obtém URL base apropriada"""
        if self.futures:
            return self.futures_url
        return self.base_url
    
    @retry(max_retries=3)
    @rate_limit(calls_per_minute=1200)
    @circuit_breaker(failure_threshold=5, recovery_timeout=30)
    async def place_order(self, order: Order) -> Dict[str, Any]:
        """Envia ordem para a Binance"""
        try:
            await self.rate_limiter.acquire()
            
            endpoint = "/fapi/v1/order" if self.futures else "/api/v3/order"
            url = f"{self._get_base_url()}{endpoint}"
            
            params = {
                'symbol': order.symbol,
                'side': order.side.label,
                'type': order.order_type.label,
                'quantity': self._format_quantity(order.quantity),
                'timestamp': int(time.time() * 1000),
                'newOrderRespType': 'FULL'
            }
            
            if order.order_type in [OrderType.LIMIT, OrderType.STOP_LIMIT]:
                params['price'] = self._format_price(order.price)
                params['timeInForce'] = order.time_in_force.code
            
            if order.order_type in [OrderType.STOP, OrderType.STOP_LIMIT]:
                params['stopPrice'] = self._format_price(order.stop_price)
            
            if order.iceberg_qty:
                params['icebergQty'] = self._format_quantity(order.iceberg_qty)
            
            params['signature'] = self._generate_signature(params)
            
            async with self.session.post(url, data=params) as response:
                result = await response.json()
                
                if response.status == 200:
                    self.metrics.total_orders += 1
                    
                    return {
                        'success': True,
                        'order_id': str(result['orderId']),
                        'client_order_id': result.get('clientOrderId'),
                        'status': result['status'],
                        'executed_qty': float(result.get('executedQty', 0)),
                        'executed_price': float(result.get('price', 0)),
                        'cummulative_quote_qty': float(result.get('cummulativeQuoteQty', 0)),
                        'fills': result.get('fills', [])
                    }
                else:
                    self.metrics.rejected_orders += 1
                    error_msg = result.get('msg', 'Unknown error')
                    self.logger.error(f"❌ Erro na ordem: {error_msg}")
                    return {'success': False, 'error': error_msg}
                    
        except Exception as e:
            self.logger.error(f"❌ Erro ao enviar ordem: {e}")
            return {'success': False, 'error': str(e)}
    
    @retry(max_retries=3)
    async def cancel_order(self, order_id: str) -> bool:
        """Cancela uma ordem"""
        try:
            endpoint = "/fapi/v1/order" if self.futures else "/api/v3/order"
            url = f"{self._get_base_url()}{endpoint}"
            
            params = {
                'timestamp': int(time.time() * 1000)
            }
            params['signature'] = self._generate_signature(params)
            
            async with self.session.delete(url, params=params) as response:
                if response.status == 200:
                    self.metrics.cancelled_orders += 1
                    return True
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao cancelar ordem: {e}")
            return False
    
    async def get_order_status(self, order_id: str) -> OrderStatus:
        """Obtém status da ordem"""
        try:
            endpoint = "/fapi/v1/order" if self.futures else "/api/v3/order"
            url = f"{self._get_base_url()}{endpoint}"
            
            params = {
                'timestamp': int(time.time() * 1000)
            }
            params['signature'] = self._generate_signature(params)
            
            async with self.session.get(url, params=params) as response:
                result = await response.json()
                
                status_map = {
                    'NEW': OrderStatus.NEW,
                    'PENDING': OrderStatus.PENDING,
                    'PARTIALLY_FILLED': OrderStatus.PARTIALLY_FILLED,
                    'FILLED': OrderStatus.FILLED,
                    'CANCELED': OrderStatus.CANCELLED,
                    'REJECTED': OrderStatus.REJECTED,
                    'EXPIRED': OrderStatus.EXPIRED
                }
                
                return status_map.get(result.get('status'), OrderStatus.REJECTED)
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao obter status: {e}")
            return OrderStatus.REJECTED
    
    async def get_account_info(self) -> AccountInfo:
        """Obtém informações da conta"""
        try:
            endpoint = "/fapi/v2/account" if self.futures else "/api/v3/account"
            url = f"{self._get_base_url()}{endpoint}"
            
            params = {
                'timestamp': int(time.time() * 1000)
            }
            params['signature'] = self._generate_signature(params)
            
            async with self.session.get(url, params=params) as response:
                result = await response.json()
                
                if self.futures:
                    # Processar contas de futuros
                    balances = {}
                    for asset in result['assets']:
                        balances[asset['asset']] = Decimal(str(asset['walletBalance']))
                    
                    usdt_balance = balances.get('USDT', Decimal('0'))
                    
                    # Processar posições
                    positions = {}
                    for pos in result['positions']:
                        if float(pos['positionAmt']) != 0:
                            position = Position(
                                id=f"{pos['symbol']}_{pos['updateTime']}",
                                symbol=pos['symbol'],
                                side=OrderSide.BUY if float(pos['positionAmt']) > 0 else OrderSide.SELL,
                                quantity=Decimal(str(abs(float(pos['positionAmt'])))),
                                avg_price=Decimal(str(pos['entryPrice'])),
                                current_price=Decimal(str(pos.get('markPrice', 0))),
                                unrealized_pnl=Decimal(str(pos.get('unRealizedProfit', 0)))
                            )
                            positions[pos['symbol']] = position
                    
                    return AccountInfo(
                        id=result.get('accountId', str(result['updateTime'])),
                        balance=usdt_balance,
                        available_balance=usdt_balance - Decimal(str(result.get('totalPositionInitialMargin', 0))),
                        margin_balance=usdt_balance,
                        unrealized_pnl=Decimal(str(result.get('totalUnrealizedProfit', 0))),
                        realized_pnl=Decimal('0'),
                        positions=positions,
                        leverage=int(result.get('leverage', 1))
                    )
                else:
                    # Processar contas spot
                    balances = {}
                    for balance in result['balances']:
                        free = Decimal(str(balance['free']))
                        if free > 0:
                            balances[balance['asset']] = free
                    
                    usdt_balance = balances.get('USDT', Decimal('0'))
                    
                    return AccountInfo(
                        id=result.get('accountId', str(result['updateTime'])),
                        balance=usdt_balance,
                        available_balance=usdt_balance,
                        margin_balance=usdt_balance,
                        unrealized_pnl=Decimal('0'),
                        realized_pnl=Decimal('0'),
                        positions={}
                    )
                    
        except Exception as e:
            self.logger.error(f"❌ Erro ao obter conta: {e}")
            return AccountInfo(
                id='error',
                balance=Decimal('0'),
                available_balance=Decimal('0'),
                margin_balance=Decimal('0'),
                unrealized_pnl=Decimal('0'),
                realized_pnl=Decimal('0'),
                positions={}
            )
    
    async def get_positions(self) -> Dict[str, Position]:
        """Obtém posições atuais"""
        account = await self.get_account_info()
        return account.positions
    
    async def get_current_price(self, symbol: str) -> float:
        """Obtém preço atual do símbolo"""
        try:
            endpoint = "/fapi/v1/ticker/price" if self.futures else "/api/v3/ticker/price"
            url = f"{self._get_base_url()}{endpoint}"
            
            async with self.session.get(url, params={'symbol': symbol}) as response:
                result = await response.json()
                return float(result['price'])
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao obter preço de {symbol}: {e}")
            return 0.0
    
    async def get_historical_prices(self, symbol: str, interval: str, limit: int = 100) -> List[Dict]:
        """Obtém preços históricos"""
        try:
            endpoint = "/fapi/v1/klines" if self.futures else "/api/v3/klines"
            url = f"{self._get_base_url()}{endpoint}"
            
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
            
            async with self.session.get(url, params=params) as response:
                klines = await response.json()
                
                result = []
                for k in klines:
                    result.append({
                        'timestamp': k[0],
                        'open': float(k[1]),
                        'high': float(k[2]),
                        'low': float(k[3]),
                        'close': float(k[4]),
                        'volume': float(k[5]),
                        'close_time': k[6],
                        'quote_volume': float(k[7]),
                        'trades': k[8],
                        'taker_buy_base': float(k[9]),
                        'taker_buy_quote': float(k[10])
                    })
                
                return result
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao obter histórico de {symbol}: {e}")
            return []
    
    async def get_exchange_info(self, symbol: str = None) -> Dict[str, Any]:
        """Obtém informações da exchange"""
        try:
            endpoint = "/fapi/v1/exchangeInfo" if self.futures else "/api/v3/exchangeInfo"
            url = f"{self._get_base_url()}{endpoint}"
            
            params = {}
            if symbol:
                params['symbol'] = symbol
            
            async with self.session.get(url, params=params) as response:
                return await response.json()
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao obter exchange info: {e}")
            return {}
    
    async def subscribe_ticker(self, symbols: List[str], callback: Callable):
        """Inscreve para atualizações de ticker via WebSocket"""
        try:
            ws_url = self.futures_ws_url if self.futures else self.ws_url
            
            # Gerar listen key para futures
            if self.futures and not self.listen_key:
                await self._create_listen_key()
            
            # Construir stream names
            streams = [f"{s.lower()}@ticker" for s in symbols]
            
            async with websocket_connection(ws_url) as websocket:
                self.websocket = websocket
                
                # Enviar requisição de subscribe
                subscribe_msg = {
                    "method": "SUBSCRIBE",
                    "params": streams,
                    "id": int(time.time() * 1000)
                }
                await websocket.send(json.dumps(subscribe_msg))
                
                # Processar mensagens
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        
                        if 'stream' in data:
                            stream = data['stream']
                            ticker = data['data']
                            
                            await callback({
                                'symbol': ticker['s'],
                                'price': float(ticker['c']),
                                'high': float(ticker['h']),
                                'low': float(ticker['l']),
                                'volume': float(ticker['v']),
                                'quote_volume': float(ticker['q']),
                                'change': float(ticker['p']),
                                'change_percent': float(ticker['P']),
                                'timestamp': ticker['E']
                            })
                            
                    except json.JSONDecodeError:
                        continue
                    except Exception as e:
                        self.logger.error(f"❌ Erro ao processar ticker: {e}")
                        
        except Exception as e:
            self.logger.error(f"❌ Erro no WebSocket: {e}")
            await asyncio.sleep(WEBSOCKET_RECONNECT_DELAY)
            # Reconectar
            await self.subscribe_ticker(symbols, callback)
    
    async def _create_listen_key(self) -> bool:
        """Cria listen key para futures"""
        try:
            url = f"{self.futures_url}/fapi/v1/listenKey"
            
            async with self.session.post(url) as response:
                result = await response.json()
                self.listen_key = result['listenKey']
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao criar listen key: {e}")
            return False
    
    async def _keepalive_listen_key(self):
        """Mantém listen key ativa"""
        while self.connected and self.futures:
            try:
                await asyncio.sleep(30 * 60)  # 30 minutos
                
                if self.listen_key:
                    url = f"{self.futures_url}/fapi/v1/listenKey"
                    params = {'listenKey': self.listen_key}
                    
                    async with self.session.put(url, params=params) as response:
                        if response.status == 200:
                            self.logger.debug("✅ Listen key renovada")
                        else:
                            self.listen_key = None
                            await self._create_listen_key()
                            
            except Exception as e:
                self.logger.error(f"❌ Erro no keepalive: {e}")
                await asyncio.sleep(60)
    
    def _format_quantity(self, quantity: Optional[Decimal]) -> str:
        """Formata quantidade para API"""
        if not quantity:
            return '0'
        return format(quantity.quantize(Decimal('0.00000001'), rounding=ROUND_DOWN), 'f')
    
    def _format_price(self, price: Optional[Decimal]) -> str:
        """Formata preço para API"""
        if not price:
            return '0'
        return format(price.quantize(Decimal('0.00000001'), rounding=ROUND_HALF_UP), 'f')

# =============================================================================
# IMPLEMENTAÇÃO ALPACA
# =============================================================================

class AlpacaBroker(BrokerConnection):
    """Implementação para Alpaca (ações/ETFs)"""
    
    def __init__(self, api_key: str, api_secret: str, paper: bool = True):
        super().__init__(
            name="Alpaca",
            broker_type=BrokerType.ALPACA
        )
        self.api_key = api_key
        self.api_secret = api_secret
        self.paper = paper
        
        if paper:
            self.base_url = "https://paper-api.alpaca.markets"
            self.data_url = "https://data.alpaca.markets"
        else:
            self.base_url = "https://api.alpaca.markets"
            self.data_url = "https://data.alpaca.markets"
        
        self.ws_url = "wss://stream.data.alpaca.markets/v2/test" if paper else "wss://stream.data.alpaca.markets/v2"
    
    async def connect(self) -> bool:
        """Conecta à API da Alpaca"""
        try:
            self.session = aiohttp.ClientSession(
                headers={
                    'APCA-API-KEY-ID': self.api_key,
                    'APCA-API-SECRET-KEY': self.api_secret
                },
                timeout=aiohttp.ClientTimeout(total=30)
            )
            
            # Testar conexão
            url = f"{self.base_url}/v2/account"
            async with self.session.get(url) as response:
                if response.status == 200:
                    self.connected = True
                    self.logger.info(f"✅ Conectado à Alpaca {'(Paper)' if self.paper else ''}")
                    return True
                    
        except Exception as e:
            self.logger.error(f"❌ Erro ao conectar com Alpaca: {e}")
        
        return False
    
    async def disconnect(self) -> bool:
        """Desconecta da API"""
        if self.session:
            await self.session.close()
        if self.websocket:
            await self.websocket.close()
        
        self.connected = False
        self.logger.info("🔌 Desconectado da Alpaca")
        return True
    
    @retry(max_retries=3)
    @rate_limit(calls_per_minute=200)
    async def place_order(self, order: Order) -> Dict[str, Any]:
        """Envia ordem para Alpaca"""
        try:
            await self.rate_limiter.acquire()
            
            url = f"{self.base_url}/v2/orders"
            
            order_data = {
                'symbol': order.symbol,
                'qty': str(order.quantity),
                'side': order.side.label.lower(),
                'type': order.order_type.label.lower(),
                'time_in_force': order.time_in_force.code.lower()
            }
            
            if order.price:
                order_data['limit_price'] = str(order.price)
            if order.stop_price:
                order_data['stop_price'] = str(order.stop_price)
            if order.iceberg_qty:
                order_data['iceberg_qty'] = str(order.iceberg_qty)
            
            async with self.session.post(url, json=order_data) as response:
                result = await response.json()
                
                if response.status == 200:
                    self.metrics.total_orders += 1
                    
                    return {
                        'success': True,
                        'order_id': result['id'],
                        'client_order_id': result.get('client_order_id'),
                        'status': result['status'],
                        'filled_qty': float(result.get('filled_qty', 0)),
                        'filled_avg_price': float(result.get('filled_avg_price', 0)) if result.get('filled_avg_price') else None
                    }
                else:
                    self.metrics.rejected_orders += 1
                    return {'success': False, 'error': result.get('message', 'Unknown error')}
                    
        except Exception as e:
            self.logger.error(f"❌ Erro ao enviar ordem: {e}")
            return {'success': False, 'error': str(e)}
    
    async def cancel_order(self, order_id: str) -> bool:
        """Cancela uma ordem"""
        try:
            url = f"{self.base_url}/v2/orders/{order_id}"
            
            async with self.session.delete(url) as response:
                if response.status in [200, 204]:
                    self.metrics.cancelled_orders += 1
                    return True
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao cancelar ordem: {e}")
            return False
    
    async def get_order_status(self, order_id: str) -> OrderStatus:
        """Obtém status da ordem"""
        try:
            url = f"{self.base_url}/v2/orders/{order_id}"
            
            async with self.session.get(url) as response:
                result = await response.json()
                
                status_map = {
                    'new': OrderStatus.NEW,
                    'pending': OrderStatus.PENDING,
                    'partially_filled': OrderStatus.PARTIALLY_FILLED,
                    'filled': OrderStatus.FILLED,
                    'cancelled': OrderStatus.CANCELLED,
                    'rejected': OrderStatus.REJECTED,
                    'expired': OrderStatus.EXPIRED
                }
                
                return status_map.get(result.get('status'), OrderStatus.REJECTED)
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao obter status: {e}")
            return OrderStatus.REJECTED
    
    async def get_account_info(self) -> AccountInfo:
        """Obtém informações da conta"""
        try:
            url = f"{self.base_url}/v2/account"
            
            async with self.session.get(url) as response:
                result = await response.json()
                
                return AccountInfo(
                    id=result['id'],
                    balance=Decimal(str(result['portfolio_value'])),
                    available_balance=Decimal(str(result['buying_power'])),
                    margin_balance=Decimal(str(result['portfolio_value'])),
                    unrealized_pnl=Decimal(str(result.get('unrealized_pl', 0))),
                    realized_pnl=Decimal(str(result.get('realized_pl', 0))),
                    positions={},
                    trading_enabled=result['trading_blocked'] is False,
                    daily_trades=0
                )
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao obter conta: {e}")
            return AccountInfo(
                id='error',
                balance=Decimal('0'),
                available_balance=Decimal('0'),
                margin_balance=Decimal('0'),
                unrealized_pnl=Decimal('0'),
                realized_pnl=Decimal('0'),
                positions={}
            )
    
    async def get_positions(self) -> Dict[str, Position]:
        """Obtém posições atuais"""
        try:
            url = f"{self.base_url}/v2/positions"
            
            async with self.session.get(url) as response:
                positions_data = await response.json()
                
                positions = {}
                for pos in positions_data:
                    qty = Decimal(str(pos['qty']))
                    
                    position = Position(
                        id=pos['asset_id'],
                        symbol=pos['symbol'],
                        side=OrderSide.BUY if qty > 0 else OrderSide.SELL,
                        quantity=abs(qty),
                        avg_price=Decimal(str(pos['avg_entry_price'])),
                        current_price=Decimal(str(pos['current_price'])),
                        unrealized_pnl=Decimal(str(pos.get('unrealized_pl', 0))),
                        realized_pnl=Decimal('0')
                    )
                    positions[pos['symbol']] = position
                
                return positions
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao obter posições: {e}")
            return {}
    
    async def get_current_price(self, symbol: str) -> float:
        """Obtém preço atual do símbolo"""
        try:
            url = f"{self.data_url}/v2/stocks/{symbol}/trades/latest"
            
            async with self.session.get(url) as response:
                result = await response.json()
                return float(result['trade']['p'])
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao obter preço de {symbol}: {e}")
            return 0.0
    
    async def get_historical_prices(self, symbol: str, interval: str, limit: int = 100) -> List[Dict]:
        """Obtém preços históricos"""
        try:
            # Mapear intervalo
            timeframe_map = {
                '1m': '1Min',
                '5m': '5Min',
                '15m': '15Min',
                '1h': '1Hour',
                '1d': '1Day'
            }
            
            tf = timeframe_map.get(interval, '1Day')
            
            url = f"{self.data_url}/v2/stocks/{symbol}/bars"
            params = {
                'timeframe': tf,
                'limit': limit
            }
            
            async with self.session.get(url, params=params) as response:
                result = await response.json()
                
                bars = []
                for bar in result.get('bars', []):
                    bars.append({
                        'timestamp': bar['t'],
                        'open': bar['o'],
                        'high': bar['h'],
                        'low': bar['l'],
                        'close': bar['c'],
                        'volume': bar['v']
                    })
                
                return bars
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao obter histórico de {symbol}: {e}")
            return []
    
    async def get_exchange_info(self, symbol: str = None) -> Dict[str, Any]:
        """Obtém informações da exchange"""
        try:
            url = f"{self.base_url}/v2/assets"
            
            params = {}
            if symbol:
                params['symbol'] = symbol
            
            async with self.session.get(url, params=params) as response:
                return await response.json()
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao obter exchange info: {e}")
            return {}
    
    async def subscribe_ticker(self, symbols: List[str], callback: Callable):
        """Inscreve para atualizações de ticker via WebSocket"""
        try:
            async with websocket_connection(self.ws_url) as websocket:
                self.websocket = websocket
                
                # Autenticar
                auth_msg = {
                    "action": "auth",
                    "key": self.api_key,
                    "secret": self.api_secret
                }
                await websocket.send(json.dumps(auth_msg))
                
                # Aguardar confirmação
                auth_response = await websocket.recv()
                
                # Inscrever para trades
                subscribe_msg = {
                    "action": "subscribe",
                    "trades": symbols
                }
                await websocket.send(json.dumps(subscribe_msg))
                
                # Processar mensagens
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        
                        for msg in data:
                            if msg.get('T') == 't':
                                await callback({
                                    'symbol': msg['S'],
                                    'price': msg['p'],
                                    'volume': msg['s'],
                                    'timestamp': msg['t']
                                })
                                
                    except json.JSONDecodeError:
                        continue
                    except Exception as e:
                        self.logger.error(f"❌ Erro ao processar ticker: {e}")
                        
        except Exception as e:
            self.logger.error(f"❌ Erro no WebSocket: {e}")
            await asyncio.sleep(WEBSOCKET_RECONNECT_DELAY)
            await self.subscribe_ticker(symbols, callback)

# =============================================================================
# SIMULADOR DE BROKER PARA BACKTESTING
# =============================================================================

class SimulatorBroker(BrokerConnection):
    """Simulador de broker para backtesting e paper trading"""
    
    def __init__(self, initial_balance: float = 10000.0):
        super().__init__(
            name="Simulator",
            broker_type=BrokerType.SIMULATOR
        )
        self.initial_balance = Decimal(str(initial_balance))
        self.balance = self.initial_balance
        self.positions: Dict[str, Position] = {}
        self.orders: Dict[str, Order] = {}
        self.trades: List[Trade] = []
        self.prices: Dict[str, float] = {}
        self.account_id = f"SIM_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Configurações de simulação
        self.slippage = 0.0001  # 0.01% de slippage
        self.commission_rate = 0.001  # 0.1% de comissão
        self.fill_probability = 0.95  # 95% de chance de preenchimento
        
        self.logger.info(f"💰 Simulador iniciado com saldo: ${float(self.initial_balance):,.2f}")
    
    async def connect(self) -> bool:
        """Conecta ao simulador"""
        self.connected = True
        self.logger.info("✅ Simulador conectado")
        return True
    
    async def disconnect(self) -> bool:
        """Desconecta do simulador"""
        self.connected = False
        self.logger.info("🔌 Simulador desconectado")
        return True
    
    async def place_order(self, order: Order) -> Dict[str, Any]:
        """Simula envio de ordem"""
        self.orders[order.id] = order
        self.metrics.total_orders += 1
        
        # Simular processamento
        await asyncio.sleep(0.05)
        
        # Decidir se ordem será preenchida
        if random.random() < self.fill_probability:
            # Calcular preço de preenchimento com slippage
            if order.order_type == OrderType.MARKET:
                fill_price = order.price * (1 + random.uniform(-self.slippage, self.slippage))
            else:
                fill_price = float(order.price) if order.price else 0
            
            # Simular preenchimento
            order.status = OrderStatus.FILLED
            order.filled_at = datetime.now()
            order.filled_price = Decimal(str(fill_price))
            order.filled_quantity = order.quantity
            
            # Calcular comissão
            commission = float(order.quantity) * fill_price * self.commission_rate
            order.commission = Decimal(str(commission))
            
            # Atualizar posição
            await self._update_position(order)
            
            # Criar trade
            trade = Trade(
                id=f"TRADE_{len(self.trades) + 1}",
                order_id=order.id,
                symbol=order.symbol,
                side=order.side,
                quantity=order.quantity,
                price=order.filled_price,
                commission=order.commission,
                commission_asset='USDT',
                realized_pnl=Decimal('0'),
                executed_at=order.filled_at
            )
            self.trades.append(trade)
            
            self.metrics.filled_orders += 1
            
            return {
                'success': True,
                'order_id': order.id,
                'status': 'FILLED',
                'filled_price': float(order.filled_price),
                'filled_quantity': float(order.filled_quantity),
                'commission': float(order.commission)
            }
        else:
            order.status = OrderStatus.REJECTED
            self.metrics.rejected_orders += 1
            
            return {
                'success': False,
                'error': 'Order rejected by simulator'
            }
    
    async def _update_position(self, order: Order):
        """Atualiza posição após ordem preenchida"""
        if order.symbol not in self.positions:
            # Nova posição
            position = Position(
                id=f"POS_{order.symbol}_{order.filled_at.timestamp()}",
                symbol=order.symbol,
                side=order.side,
                quantity=order.quantity,
                avg_price=order.filled_price,
                current_price=order.filled_price
            )
            self.positions[order.symbol] = position
        else:
            # Atualizar posição existente
            position = self.positions[order.symbol]
            
            if position.side == order.side:
                # Adicionar à posição
                total_qty = position.quantity + order.quantity
                total_cost = position.cost + (order.quantity * order.filled_price)
                position.avg_price = total_cost / total_qty
                position.quantity = total_qty
            else:
                # Reduzir posição
                if order.quantity >= position.quantity:
                    # Fechar posição
                    pnl = (order.filled_price - position.avg_price) * position.quantity
                    if position.side == OrderSide.SELL:
                        pnl = (position.avg_price - order.filled_price) * position.quantity
                    
                    position.realized_pnl += Decimal(str(pnl))
                    position.quantity = position.quantity - order.quantity
                    
                    if position.quantity <= 0:
                        del self.positions[order.symbol]
                else:
                    # Redução parcial
                    pnl = (order.filled_price - position.avg_price) * order.quantity
                    if position.side == OrderSide.SELL:
                        pnl = (position.avg_price - order.filled_price) * order.quantity
                    
                    position.realized_pnl += Decimal(str(pnl))
                    position.quantity -= order.quantity
    
    async def cancel_order(self, order_id: str) -> bool:
        """Cancela uma ordem"""
        if order_id in self.orders:
            self.orders[order_id].status = OrderStatus.CANCELLED
            self.metrics.cancelled_orders += 1
            return True
        return False
    
    async def get_order_status(self, order_id: str) -> OrderStatus:
        """Obtém status da ordem"""
        if order_id in self.orders:
            return self.orders[order_id].status
        return OrderStatus.REJECTED
    
    async def get_account_info(self) -> AccountInfo:
        """Obtém informações da conta"""
        # Calcular P&L não realizado
        unrealized_pnl = Decimal('0')
        total_position_value = Decimal('0')
        
        for position in self.positions.values():
            position.current_price = Decimal(str(self.prices.get(position.symbol, 0)))
            if position.current_price > 0:
                if position.side == OrderSide.BUY:
                    pnl = (position.current_price - position.avg_price) * position.quantity
                else:
                    pnl = (position.avg_price - position.current_price) * position.quantity
                position.unrealized_pnl = pnl
                unrealized_pnl += pnl
                total_position_value += position.current_price * position.quantity
        
        # Calcular P&L realizado
        realized_pnl = sum(t.realized_pnl for t in self.trades)
        
        # Saldo disponível
        available = self.balance - total_position_value
        
        return AccountInfo(
            id=self.account_id,
            balance=self.balance,
            available_balance=available if available > 0 else Decimal('0'),
            margin_balance=self.balance,
            unrealized_pnl=unrealized_pnl,
            realized_pnl=realized_pnl,
            positions=self.positions,
            total_position_value=total_position_value,
            daily_trades=len([t for t in self.trades if t.executed_at.date() == datetime.now().date()])
        )
    
    async def get_positions(self) -> Dict[str, Position]:
        """Obtém posições atuais"""
        return self.positions
    
    async def get_current_price(self, symbol: str) -> float:
        """Obtém preço atual do símbolo"""
        return self.prices.get(symbol, 0.0)
    
    async def get_historical_prices(self, symbol: str, interval: str, limit: int = 100) -> List[Dict]:
        """Obtém preços históricos simulados"""
        # Gerar dados sintéticos
        prices = []
        base_price = 100.0
        
        for i in range(limit):
            timestamp = datetime.now() - timedelta(minutes=limit - i)
            change = random.uniform(-0.02, 0.02)
            price = base_price * (1 + change)
            base_price = price
            
            prices.append({
                'timestamp': timestamp.timestamp() * 1000,
                'open': price * 0.999,
                'high': price * 1.002,
                'low': price * 0.998,
                'close': price,
                'volume': random.uniform(1000, 10000)
            })
        
        return prices
    
    async def get_exchange_info(self, symbol: str = None) -> Dict[str, Any]:
        """Obtém informações da exchange simulada"""
        return {
            'name': 'Simulator',
            'version': '1.0',
            'symbols': list(self.prices.keys())
        }
    
    async def subscribe_ticker(self, symbols: List[str], callback: Callable):
        """Simula atualizações de ticker"""
        while self.connected:
            for symbol in symbols:
                # Gerar variação aleatória
                current_price = self.prices.get(symbol, 100.0)
                change = random.uniform(-0.001, 0.001)
                new_price = current_price * (1 + change)
                self.prices[symbol] = new_price
                
                await callback({
                    'symbol': symbol,
                    'price': new_price,
                    'high': new_price * 1.002,
                    'low': new_price * 0.998,
                    'volume': random.uniform(1000, 10000),
                    'change': new_price - current_price,
                    'change_percent': change * 100,
                    'timestamp': int(time.time() * 1000)
                })
            
            await asyncio.sleep(1)

# =============================================================================
# GERENCIADOR DE RISCO AVANÇADO
# =============================================================================

class RiskManager:
    """Gerenciador avançado de risco com múltiplas camadas"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Limites de risco
        self.max_risk_per_trade = Decimal(str(self.config.get('max_risk_per_trade', 0.02)))
        self.max_daily_loss = Decimal(str(self.config.get('max_daily_loss', 0.05)))
        self.max_position_size_pct = Decimal(str(self.config.get('max_position_size_pct', 0.10)))
        self.max_open_positions = self.config.get('max_open_positions', 20)
        self.max_daily_trades = self.config.get('max_daily_trades', 100)
        self.max_leverage = self.config.get('max_leverage', 1)
        
        # Estado atual
        self.daily_pnl = Decimal('0')
        self.daily_trades = 0
        self.daily_volume = Decimal('0')
        self.last_reset = datetime.now().date()
        
        # Histórico
        self.trade_history: List[Trade] = []
        self.position_history: List[Position] = []
        self.risk_events: List[Dict] = []
        
        self.logger = logger.getChild('RiskManager')
    
    def calculate_position_size(self, account_balance: Decimal, entry_price: Decimal,
                              stop_loss: Decimal, risk_ratio: float = 1.0) -> Decimal:
        """Calcula tamanho da posição baseado no risco"""
        if stop_loss == 0 or entry_price == 0:
            return Decimal('0')
        
        risk_per_share = abs(entry_price - stop_loss)
        max_risk_amount = account_balance * self.max_risk_per_trade * Decimal(str(risk_ratio))
        
        if risk_per_share == 0:
            return Decimal('0')
        
        position_size = max_risk_amount / risk_per_share
        
        # Limitar pelo percentual máximo do capital
        max_position_by_capital = (account_balance * self.max_position_size_pct) / entry_price
        
        return min(position_size, max_position_by_capital)
    
    def can_trade(self, account: AccountInfo, signal: TradingSignal) -> Tuple[bool, str]:
        """Verifica se pode executar o trade baseado em múltiplas regras"""
        
        # Reset diário se necessário
        self._check_daily_reset()
        
        # 1. Verificar perda diária
        if self.daily_pnl < -abs(account.balance * self.max_daily_loss):
            self._log_risk_event('MAX_DAILY_LOSS', f"Perda diária máxima: ${float(self.daily_pnl):,.2f}")
            return False, f"Limite de perda diária atingido (${float(self.daily_pnl):,.2f})"
        
        # 2. Verificar número máximo de trades diários
        if self.daily_trades >= self.max_daily_trades:
            self._log_risk_event('MAX_DAILY_TRADES', f"{self.daily_trades} trades hoje")
            return False, f"Limite de trades diários atingido ({self.max_daily_trades})"
        
        # 3. Verificar margem disponível
        position_size = self.calculate_position_size(
            account.balance, Decimal(str(signal.price)), 
            Decimal(str(signal.stop_loss)), signal.confidence / 100
        )
        
        required_margin = Decimal(str(signal.price)) * position_size / Decimal(str(account.leverage))
        
        if required_margin > account.available_balance * Decimal('0.8'):
            self._log_risk_event('INSUFFICIENT_MARGIN', 
                               f"Necessário: ${float(required_margin):,.2f}, Disponível: ${float(account.available_balance):,.2f}")
            return False, f"Margem insuficiente (${float(required_margin):,.2f} necessários)"
        
        # 4. Verificar concentração de posições
        if len(account.positions) >= self.max_open_positions:
            self._log_risk_event('MAX_POSITIONS', f"{len(account.positions)} posições abertas")
            return False, f"Muitas posições abertas ({self.max_open_positions} máximo)"
        
        # 5. Verificar alavancagem
        if account.leverage > self.max_leverage:
            self._log_risk_event('MAX_LEVERAGE', f"Alavancagem atual: {account.leverage}x")
            return False, f"Alavancagem excede limite ({self.max_leverage}x)"
        
        # 6. Verificar exposição por símbolo
        symbol_exposure = Decimal('0')
        for pos in account.positions.values():
            if pos.symbol == signal.symbol:
                symbol_exposure += pos.value
        
        max_exposure = account.balance * self.max_position_size_pct
        if symbol_exposure + required_margin > max_exposure:
            self._log_risk_event('MAX_SYMBOL_EXPOSURE',
                               f"Exposição em {signal.symbol}: ${float(symbol_exposure):,.2f}")
            return False, f"Limite de exposição para {signal.symbol} atingido"
        
        # 7. Verificar correlação
        # Implementar análise de correlação entre ativos
        
        # 8. Verificar qualidade do sinal
        if signal.confidence < 50:
            self._log_risk_event('LOW_CONFIDENCE', f"Confiança: {signal.confidence}%")
            return False, f"Confiança muito baixa ({signal.confidence}%)"
        
        return True, "OK"
    
    def _check_daily_reset(self):
        """Verifica e reseta contadores diários"""
        today = datetime.now().date()
        if today > self.last_reset:
            self.daily_pnl = Decimal('0')
            self.daily_trades = 0
            self.daily_volume = Decimal('0')
            self.last_reset = today
            self.logger.info(f"📅 Reset diário realizado: {today}")
    
    def _log_risk_event(self, event_type: str, message: str):
        """Registra evento de risco"""
        event = {
            'timestamp': datetime.now(),
            'type': event_type,
            'message': message
        }
        self.risk_events.append(event)
        self.logger.warning(f"⚠️ {event_type}: {message}")
    
    def update_daily_pnl(self, pnl: Decimal):
        """Atualiza PnL diário"""
        self.daily_pnl += pnl
    
    def update_daily_trade(self, trade: Trade):
        """Atualiza contadores diários"""
        self.daily_trades += 1
        self.daily_volume += trade.quantity * trade.price
        self.trade_history.append(trade)
    
    def get_risk_metrics(self) -> Dict[str, Any]:
        """Obtém métricas de risco"""
        return {
            'daily_pnl': float(self.daily_pnl),
            'daily_trades': self.daily_trades,
            'daily_volume': float(self.daily_volume),
            'risk_events_today': len([e for e in self.risk_events 
                                     if e['timestamp'].date() == datetime.now().date()]),
            'win_rate': self._calculate_win_rate(),
            'profit_factor': self._calculate_profit_factor(),
            'sharpe_ratio': self._calculate_sharpe_ratio(),
            'max_drawdown': self._calculate_max_drawdown()
        }
    
    def _calculate_win_rate(self) -> float:
        """Calcula taxa de acerto"""
        if not self.trade_history:
            return 0.0
        
        winning_trades = len([t for t in self.trade_history if t.realized_pnl > 0])
        return (winning_trades / len(self.trade_history)) * 100
    
    def _calculate_profit_factor(self) -> float:
        """Calcula profit factor"""
        if not self.trade_history:
            return 0.0
        
        gross_profit = sum(float(t.realized_pnl) for t in self.trade_history if t.realized_pnl > 0)
        gross_loss = abs(sum(float(t.realized_pnl) for t in self.trade_history if t.realized_pnl < 0))
        
        return gross_profit / gross_loss if gross_loss > 0 else float('inf')
    
    def _calculate_sharpe_ratio(self) -> float:
        """Calcula Sharpe Ratio"""
        if not self.trade_history or not NUMPY_AVAILABLE:
            return 0.0
        
        returns = [float(t.realized_pnl) / 1000 for t in self.trade_history]  # Simplificado
        
        if len(returns) < 2:
            return 0.0
        
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        
        if std_return == 0:
            return 0.0
        
        return (mean_return / std_return) * np.sqrt(252)
    
    def _calculate_max_drawdown(self) -> float:
        """Calcula maximum drawdown"""
        if not self.trade_history or not NUMPY_AVAILABLE:
            return 0.0
        
        # Calcular equity curve
        equity = [0]
        for trade in self.trade_history:
            equity.append(equity[-1] + float(trade.realized_pnl))
        
        equity = np.array(equity)
        
        # Calcular drawdown
        peak = np.maximum.accumulate(equity)
        drawdown = (peak - equity) / peak
        drawdown = drawdown[~np.isnan(drawdown)]
        
        return float(np.max(drawdown)) if len(drawdown) > 0 else 0.0

# =============================================================================
# GERENCIADOR DE ORDENS AVANÇADO
# =============================================================================

class OrderManager:
    """Gerenciador avançado de ordens com OCO e trailing stop"""
    
    def __init__(self, broker: BrokerConnection, risk_manager: RiskManager):
        self.broker = broker
        self.risk_manager = risk_manager
        
        # Armazenamento de ordens
        self.pending_orders: Dict[str, Order] = {}
        self.filled_orders: List[Order] = []
        self.cancelled_orders: List[Order] = []
        
        # Ordens OCO
        self.oco_groups: Dict[str, List[str]] = {}
        
        # Métricas
        self.metrics = ExecutionMetrics()
        
        self.order_counter = 0
        self.logger = logger.getChild('OrderManager')
    
    async def execute_trade(self, signal: TradingSignal, account: AccountInfo) -> Dict[str, Any]:
        """Executa um trade completo baseado no sinal"""
        try:
            # Verificar risco
            can_trade, reason = self.risk_manager.can_trade(account, signal)
            if not can_trade:
                return {'success': False, 'error': reason}
            
            # Calcular tamanho da posição
            position_size = self.risk_manager.calculate_position_size(
                account.balance,
                Decimal(str(signal.price)),
                Decimal(str(signal.stop_loss)),
                signal.confidence / 100
            )
            
            if position_size <= 0:
                return {'success': False, 'error': 'Tamanho de posição inválido'}
            
            # Criar ordem principal
            main_order = Order(
                id=f"MAIN_{self.order_counter}_{int(time.time())}",
                symbol=signal.symbol,
                side=signal.action,
                order_type=OrderType.MARKET,
                quantity=position_size,
                price=Decimal(str(signal.price))
            )
            self.order_counter += 1
            
            # Enviar ordem principal
            result = await self.broker.place_order(main_order)
            
            if result['success']:
                main_order.id = result['order_id']
                self.pending_orders[main_order.id] = main_order
                
                # Criar ordens de stop loss e take profit (OCO)
                await self._place_oco_orders(main_order, signal.stop_loss, signal.take_profit)
                
                # Registrar trade
                self.metrics.total_orders += 1
                
                return {
                    'success': True,
                    'order_id': main_order.id,
                    'position_size': float(position_size),
                    'stop_loss': signal.stop_loss,
                    'take_profit': signal.take_profit,
                    'order_result': result
                }
            else:
                return {'success': False, 'error': result.get('error', 'Unknown error')}
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao executar trade: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _place_oco_orders(self, main_order: Order, stop_price: float, take_profit: float):
        """Coloca ordens OCO (One-Cancels-Other)"""
        stop_side = OrderSide.SELL if main_order.side == OrderSide.BUY else OrderSide.BUY
        
        # Ordem de stop loss
        stop_order = Order(
            id=f"STOP_{main_order.id}",
            symbol=main_order.symbol,
            side=stop_side,
            order_type=OrderType.STOP,
            quantity=main_order.quantity,
            stop_price=Decimal(str(stop_price))
        )
        
        # Ordem de take profit
        tp_order = Order(
            id=f"TP_{main_order.id}",
            symbol=main_order.symbol,
            side=stop_side,
            order_type=OrderType.LIMIT,
            quantity=main_order.quantity,
            price=Decimal(str(take_profit))
        )
        
        # Enviar ordens
        stop_result = await self.broker.place_order(stop_order)
        tp_result = await self.broker.place_order(tp_order)
        
        if stop_result['success']:
            stop_order.id = stop_result['order_id']
            self.pending_orders[stop_order.id] = stop_order
            self.oco_groups[main_order.id] = [stop_order.id, tp_order.id]
        
        if tp_result['success']:
            tp_order.id = tp_result['order_id']
            self.pending_orders[tp_order.id] = tp_order
    
    async def place_trailing_stop(self, position: Position, trail_percent: float = TRAILING_STOP_DISTANCE):
        """Coloca trailing stop para uma posição"""
        position.trailing_stop = Decimal(str(trail_percent))
        
        # Calcular preço inicial do stop
        if position.side == OrderSide.BUY:
            stop_price = position.current_price * (1 - Decimal(str(trail_percent)))
        else:
            stop_price = position.current_price * (1 + Decimal(str(trail_percent)))
        
        # Criar ordem de trailing stop
        stop_order = Order(
            id=f"TRAIL_{position.id}_{int(time.time())}",
            symbol=position.symbol,
            side=OrderSide.SELL if position.side == OrderSide.BUY else OrderSide.BUY,
            order_type=OrderType.TRAILING_STOP,
            quantity=position.quantity,
            stop_price=stop_price,
            trail_value=Decimal(str(trail_percent)),
            trail_asset='PERCENT'
        )
        
        result = await self.broker.place_order(stop_order)
        
        if result['success']:
            stop_order.id = result['order_id']
            self.pending_orders[stop_order.id] = stop_order
            return True
        
        return False
    
    async def cancel_all_pending_orders(self, symbol: str = None):
        """Cancela todas as ordens pendentes"""
        cancelled = []
        
        for order_id in list(self.pending_orders.keys()):
            order = self.pending_orders[order_id]
            
            if symbol is None or order.symbol == symbol:
                if await self.broker.cancel_order(order_id):
                    cancelled.append(order_id)
                    del self.pending_orders[order_id]
        
        self.logger.info(f"✅ {len(cancelled)} ordens pendentes canceladas")
        return cancelled
    
    async def update_order_status(self, order_id: str):
        """Atualiza status de uma ordem"""
        if order_id not in self.pending_orders:
            return
        
        order = self.pending_orders[order_id]
        new_status = await self.broker.get_order_status(order_id)
        
        if new_status != order.status:
            old_status = order.status
            order.status = new_status
            order.updated_at = datetime.now()
            
            self.logger.info(f"📊 Ordem {order_id}: {old_status.icon} → {new_status.icon}")
            
            if new_status == OrderStatus.FILLED:
                self.filled_orders.append(order)
                del self.pending_orders[order_id]
                self.metrics.filled_orders += 1
                
                # Cancelar ordens OCO relacionadas
                for parent_id, children in self.oco_groups.items():
                    if order_id in children:
                        for child_id in children:
                            if child_id != order_id and child_id in self.pending_orders:
                                await self.broker.cancel_order(child_id)
                                del self.pending_orders[child_id]
            
            elif new_status in [OrderStatus.CANCELLED, OrderStatus.REJECTED, OrderStatus.EXPIRED]:
                self.cancelled_orders.append(order)
                del self.pending_orders[order_id]
                
                if new_status == OrderStatus.CANCELLED:
                    self.metrics.cancelled_orders += 1
                elif new_status == OrderStatus.REJECTED:
                    self.metrics.rejected_orders += 1
    
    async def monitor_orders(self):
        """Monitora ordens pendentes"""
        while True:
            try:
                for order_id in list(self.pending_orders.keys()):
                    await self.update_order_status(order_id)
                
                await asyncio.sleep(1)  # Verificar a cada segundo
                
            except Exception as e:
                self.logger.error(f"❌ Erro no monitor de ordens: {e}")
                await asyncio.sleep(5)

# =============================================================================
# GERENCIADOR DE POSIÇÕES AVANÇADO
# =============================================================================

class PositionManager:
    """Gerenciador avançado de posições com trailing stop dinâmico"""
    
    def __init__(self, broker: BrokerConnection, order_manager: OrderManager):
        self.broker = broker
        self.order_manager = order_manager
        self.positions: Dict[str, Position] = {}
        self.position_history: List[Position] = []
        self.logger = logger.getChild('PositionManager')
    
    async def update_positions(self, current_prices: Dict[str, Decimal]):
        """Atualiza todas as posições com preços atuais"""
        for position in list(self.positions.values()):
            if position.symbol in current_prices:
                position.current_price = current_prices[position.symbol]
                position.updated_at = datetime.now()
                
                # Atualizar trailing stop
                new_stop = position.update_trailing_stop()
                if new_stop:
                    self.logger.info(f"📉 Trailing stop atualizado para {position.symbol}: ${float(new_stop):,.2f}")
                
                # Verificar stop loss e take profit
                await self._check_position_exit(position)
    
    async def _check_position_exit(self, position: Position):
        """Verifica se posição deve ser fechada"""
        # Stop loss
        if position.stop_loss and position.stop_loss > 0:
            if position.side == OrderSide.BUY:
                if position.current_price <= position.stop_loss:
                    await self.close_position(position, position.stop_loss, 'STOP_LOSS')
            else:
                if position.current_price >= position.stop_loss:
                    await self.close_position(position, position.stop_loss, 'STOP_LOSS')
        
        # Take profit
        if position.take_profit and position.take_profit > 0:
            if position.side == OrderSide.BUY:
                if position.current_price >= position.take_profit:
                    await self.close_position(position, position.take_profit, 'TAKE_PROFIT')
            else:
                if position.current_price <= position.take_profit:
                    await self.close_position(position, position.take_profit, 'TAKE_PROFIT')
    
    async def close_position(self, position: Position, price: Decimal, reason: str):
        """Fecha uma posição"""
        if position.id not in self.positions:
            return None
        
        # Criar ordem de fechamento
        close_order = Order(
            id=f"CLOSE_{position.id}_{int(time.time())}",
            symbol=position.symbol,
            side=OrderSide.SELL if position.side == OrderSide.BUY else OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=position.quantity,
            price=price
        )
        
        result = await self.broker.place_order(close_order)
        
        if result['success']:
            # Calcular P&L
            if position.side == OrderSide.BUY:
                pnl = (price - position.avg_price) * position.quantity
            else:
                pnl = (position.avg_price - price) * position.quantity
            
            position.realized_pnl += pnl
            position.closed_at = datetime.now()
            
            # Mover para histórico
            self.position_history.append(position)
            del self.positions[position.id]
            
            self.logger.info(
                f"{'✅' if pnl > 0 else '📉'} Posição {position.symbol} fechada: "
                f"P&L ${float(pnl):,.2f} ({float(pnl / position.cost * 100):,.2f}%) | "
                f"Motivo: {reason}"
            )
            
            return {
                'position': position,
                'pnl': float(pnl),
                'pnl_percent': float(pnl / position.cost * 100),
                'reason': reason
            }
        
        return None

# =============================================================================
# MOTOR DE TRADING PRINCIPAL
# =============================================================================

class VhalinorLiveTradingEngine:
    """Motor principal de trading ao vivo com arquitetura quântica"""
    
    def __init__(self, broker: BrokerConnection, config: Dict[str, Any] = None):
        self.broker = broker
        self.config = config or {}
        
        # Componentes
        self.risk_manager = RiskManager(self.config)
        self.order_manager = OrderManager(self.broker, self.risk_manager)
        self.position_manager = PositionManager(self.broker, self.order_manager)
        
        # Estado do sistema
        self.running = False
        self.performance_metrics: Dict[str, Any] = {}
        self.signal_queue: asyncio.Queue = asyncio.Queue()
        self.account_info: Optional[AccountInfo] = None
        
        # Callbacks
        self.callbacks = {
            'on_signal': [],
            'on_order': [],
            'on_trade': [],
            'on_position': [],
            'on_error': []
        }
        
        self.logger = logger.getChild('VhalinorTradingEngine')
        self.start_time = datetime.now()
    
    def register_callback(self, event_type: str, callback: Callable):
        """Registra callback para eventos"""
        if event_type in self.callbacks:
            self.callbacks[event_type].append(callback)
    
    async def _trigger_callbacks(self, event_type: str, data: Any = None):
        """Dispara callbacks registrados"""
        for callback in self.callbacks.get(event_type, []):
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(data)
                else:
                    callback(data)
            except Exception as e:
                self.logger.error(f"❌ Erro no callback {event_type}: {e}")
    
    async def start(self):
        """Inicia o motor de trading"""
        self.logger.info("="*80)
        self.logger.info("🚀 VHALINOR IAG - MOTOR DE TRADING AO VIVO QUÂNTICO")
        self.logger.info("="*80)
        self.logger.info(f"📊 Broker: {self.broker.broker_type.icon} {self.broker.broker_type.label}")
        self.logger.info(f"⚙️  Configuração: Risco {self.risk_manager.max_risk_per_trade*100:.1f}% | "
                       f"Máx Posições: {self.risk_manager.max_open_positions}")
        self.logger.info("="*80)
        
        if not await self.broker.connect():
            self.logger.error("❌ Falha ao conectar com a corretora")
            return False
        
        self.running = True
        
        # Iniciar tarefas de background
        asyncio.create_task(self._monitor_orders())
        asyncio.create_task(self._monitor_positions())
        asyncio.create_task(self._process_signals())
        asyncio.create_task(self._monitor_performance())
        
        self.logger.info("✅ Motor de trading iniciado com sucesso")
        return True
    
    async def stop(self):
        """Para o motor de trading"""
        self.logger.info("⏹️ Parando motor de trading...")
        self.running = False
        
        # Cancelar todas as ordens pendentes
        await self.order_manager.cancel_all_pending_orders()
        
        # Desconectar broker
        await self.broker.disconnect()
        
        self.logger.info("✅ Motor de trading parado")
        
        # Gerar relatório final
        await self._generate_final_report()
    
    async def process_signal(self, signal: TradingSignal):
        """Processa um sinal de trading"""
        if not self.running:
            self.logger.warning("⚠️ Motor não está rodando, ignorando sinal")
            return
        
        await self.signal_queue.put(signal)
        self.logger.info(f"📨 Sinal enfileirado: {signal.symbol} {signal.action.icon} "
                        f"Conf: {signal.confidence:.1f}%")
    
    async def _process_signals(self):
        """Processa sinais da fila"""
        while self.running:
            try:
                signal = await self.signal_queue.get()
                
                # Obter informações da conta
                self.account_info = await self.broker.get_account_info()
                
                # Executar trade
                result = await self.order_manager.execute_trade(signal, self.account_info)
                
                await self._trigger_callbacks('on_signal', {
                    'signal': signal.to_dict(),
                    'result': result
                })
                
                if result['success']:
                    self.logger.info(f"✅ Trade executado: {signal.symbol} {signal.action.icon} "
                                   f"Tamanho: {result['position_size']:.4f}")
                else:
                    self.logger.error(f"❌ Falha ao executar trade: {result['error']}")
                    await self._trigger_callbacks('on_error', result)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Erro no processamento de sinais: {e}")
                await asyncio.sleep(1)
    
    async def _monitor_orders(self):
        """Monitora ordens pendentes"""
        await self.order_manager.monitor_orders()
    
    async def _monitor_positions(self):
        """Monitora posições ativas"""
        while self.running:
            try:
                # Obter posições do broker
                broker_positions = await self.broker.get_positions()
                
                # Atualizar posições locais
                self.position_manager.positions = broker_positions
                
                # Obter preços atuais
                current_prices = {}
                for symbol in broker_positions.keys():
                    price = await self.broker.get_current_price(symbol)
                    if price > 0:
                        current_prices[symbol] = Decimal(str(price))
                
                # Atualizar posições
                await self.position_manager.update_positions(current_prices)
                
                await asyncio.sleep(5)  # Atualizar a cada 5 segundos
                
            except Exception as e:
                self.logger.error(f"❌ Erro no monitor de posições: {e}")
                await asyncio.sleep(10)
    
    async def _monitor_performance(self):
        """Monitora performance do trading"""
        while self.running:
            try:
                account = await self.broker.get_account_info()
                
                self.performance_metrics = {
                    'total_balance': float(account.balance),
                    'available_balance': float(account.available_balance),
                    'unrealized_pnl': float(account.unrealized_pnl),
                    'realized_pnl': float(account.realized_pnl),
                    'total_pnl': float(account.total_pnl),
                    'open_positions': len(account.positions),
                    'daily_trades': account.daily_trades,
                    'daily_pnl': float(account.daily_pnl),
                    'win_rate': self.risk_manager._calculate_win_rate(),
                    'profit_factor': self.risk_manager._calculate_profit_factor(),
                    'sharpe_ratio': self.risk_manager._calculate_sharpe_ratio(),
                    'max_drawdown': self.risk_manager._calculate_max_drawdown(),
                    'timestamp': datetime.now().isoformat()
                }
                
                await asyncio.sleep(60)  # Atualizar a cada minuto
                
            except Exception as e:
                self.logger.error(f"❌ Erro no monitor de performance: {e}")
                await asyncio.sleep(30)
    
    async def _generate_final_report(self):
        """Gera relatório final do trading"""
        uptime = datetime.now() - self.start_time
        
        report = []
        report.append("="*90)
        report.append("📊 RELATÓRIO FINAL - MOTOR DE TRADING VHALINOR IAG")
        report.append("="*90)
        
        report.append(f"\n⏱️  Uptime: {uptime.days}d {uptime.seconds//3600}h {(uptime.seconds%3600)//60}m")
        report.append(f"📈 Broker: {self.broker.broker_type.icon} {self.broker.broker_type.label}")
        
        report.append(f"\n💰 PERFORMANCE FINANCEIRA:")
        if self.performance_metrics:
            report.append(f"   • Saldo final: ${self.performance_metrics.get('total_balance', 0):,.2f}")
            report.append(f"   • P&L Realizado: ${self.performance_metrics.get('realized_pnl', 0):,.2f}")
            report.append(f"   • P&L Não Realizado: ${self.performance_metrics.get('unrealized_pnl', 0):,.2f}")
            report.append(f"   • P&L Total: ${self.performance_metrics.get('total_pnl', 0):,.2f}")
        
        report.append(f"\n📊 ESTATÍSTICAS:")
        report.append(f"   • Ordens executadas: {self.order_manager.metrics.filled_orders}")
        report.append(f"   • Ordens canceladas: {self.order_manager.metrics.cancelled_orders}")
        report.append(f"   • Taxa de sucesso: {self.order_manager.metrics.success_rate:.2f}%")
        report.append(f"   • Win Rate: {self.performance_metrics.get('win_rate', 0):.2f}%")
        report.append(f"   • Profit Factor: {self.performance_metrics.get('profit_factor', 0):.2f}")
        report.append(f"   • Sharpe Ratio: {self.performance_metrics.get('sharpe_ratio', 0):.2f}")
        report.append(f"   • Max Drawdown: {self.performance_metrics.get('max_drawdown', 0):.2f}%")
        
        report.append(f"\n🟢 POSIÇÕES ABERTAS:")
        for pos in self.position_manager.positions.values():
            report.append(f"   • {pos.symbol}: {pos.quantity} @ ${float(pos.avg_price):,.2f} | "
                        f"P&L: ${float(pos.unrealized_pnl):,.2f} ({pos.unrealized_pnl_percent:.2f}%)")
        
        report.append("\n" + "="*90)
        
        report_text = "\n".join(report)
        self.logger.info(f"\n{report_text}")
        
        # Salvar relatório em arquivo
        filename = f"trading_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        self.logger.info(f"💾 Relatório salvo: {filename}")

# =============================================================================
# FUNÇÕES PRINCIPAIS OTIMIZADAS
# =============================================================================

async def connect_to_broker(broker_type: str, **kwargs) -> BrokerConnection:
    """
    Conecta com corretora ou simulador de forma otimizada
    
    Args:
        broker_type: Tipo de corretora ('binance', 'binance_futures', 'alpaca', 'simulator')
        **kwargs: Configurações adicionais (api_key, api_secret, testnet, paper, etc)
    
    Returns:
        BrokerConnection: Instância da corretora conectada
    """
    try:
        broker_type_lower = broker_type.lower()
        
        if broker_type_lower == "binance":
            broker = BinanceBroker(
                api_key=kwargs.get('api_key', ''),
                api_secret=kwargs.get('api_secret', ''),
                testnet=kwargs.get('testnet', True),
                futures=False
            )
        elif broker_type_lower == "binance_futures":
            broker = BinanceBroker(
                api_key=kwargs.get('api_key', ''),
                api_secret=kwargs.get('api_secret', ''),
                testnet=kwargs.get('testnet', True),
                futures=True
            )
        elif broker_type_lower == "alpaca":
            broker = AlpacaBroker(
                api_key=kwargs.get('api_key', ''),
                api_secret=kwargs.get('api_secret', ''),
                paper=kwargs.get('paper', True)
            )
        elif broker_type_lower == "simulator":
            broker = SimulatorBroker(
                initial_balance=kwargs.get('initial_balance', 10000.0)
            )
        else:
            raise ValueError(f"Broker não suportado: {broker_type}")
        
        if await broker.connect():
            logger.info(f"✅ Conectado com sucesso à {broker.broker_type.icon} {broker.broker_type.label}")
            return broker
        else:
            raise ConnectionError(f"❌ Falha ao conectar com {broker_type}")
            
    except Exception as e:
        logger.error(f"❌ Erro ao conectar com broker: {e}")
        raise

async def execute_trade_signal(signal: TradingSignal, engine: VhalinorLiveTradingEngine) -> Dict[str, Any]:
    """
    Executa sinal de trading usando o motor
    
    Args:
        signal: Sinal de trading
        engine: Motor de trading
    
    Returns:
        Dict: Resultado da execução
    """
    try:
        await engine.process_signal(signal)
        return {'success': True, 'message': 'Sinal enviado para execução'}
    except Exception as e:
        logger.error(f"❌ Erro ao executar sinal: {e}")
        return {'success': False, 'error': str(e)}

# =============================================================================
# EXEMPLO DE USO AVANÇADO
# =============================================================================

async def main():
    """Exemplo de uso do sistema de trading avancado"""
    
    print("\n" + "="*90)
    print("VHALINOR IAG - MOTOR DE TRADING AO VIVO QUANTICO")
    print("="*90)
    print(f"Build: {BUILD_DATE}")
    print(f"Versao: {VERSION} - {CODENAME}")
    print("="*90)
    
    # Configuracao
    config = {
        'max_risk_per_trade': 0.02,
        'max_daily_loss': 0.05,
        'max_position_size_pct': 0.10,
        'max_open_positions': 5,
        'max_daily_trades': 50,
        'max_leverage': 1
    }
    
    try:
        # 1. Conectar com simulador para teste
        print("\n[1] Conectando ao broker...")
        broker = await connect_to_broker(
            broker_type='simulator',
            initial_balance=10000.0
        )
        
        # 2. Criar motor de trading
        print("\n[2] Inicializando motor de trading...")
        engine = VhalinorLiveTradingEngine(broker, config)
        
        # 3. Registrar callbacks
        def on_signal(data):
            print(f"   [CALLBACK] Sinal processado - {data['signal']['symbol']}")
        
        engine.register_callback('on_signal', on_signal)
        
        # 4. Iniciar motor
        print("\n[3] Iniciando motor...")
        if await engine.start():
            
            # 5. Criar sinais de exemplo
            print("\n[4] Enviando sinais de trading...")
            
            signals = [
                TradingSignal(
                    id=f"SIG_{i}",
                    symbol="BTCUSDT",
                    action=OrderSide.BUY,
                    confidence=85.0,
                    price=50000.0,
                    stop_loss=49000.0,
                    take_profit=52000.0,
                    timestamp=datetime.now(),
                    signal_type="MOMENTUM",
                    strategy_name="Trend Following",
                    timeframe="1h"
                ) for i in range(3)
            ]
            
            for signal in signals:
                await execute_trade_signal(signal, engine)
                await asyncio.sleep(1)
            
            # 6. Simular atualização de preços
            print("\n[5] Simulando mercado...")
            for i in range(5):
                # Atualizar preços no simulador
                if isinstance(broker, SimulatorBroker):
                    broker.prices['BTCUSDT'] = 50000.0 * (1 + random.uniform(-0.02, 0.02))
                    print(f"   [PRICE] BTCUSDT: ${broker.prices['BTCUSDT']:,.2f}")
                
                await asyncio.sleep(2)
            
            # 7. Parar motor
            print("\n[6] Parando motor...")
            await engine.stop()
            
        else:
            print("Falha ao iniciar motor de trading")
            
    except Exception as e:
        logger.error(f"Erro no sistema: {e}")
        raise
    
    print("\n" + "="*90)
    print("[SUCCESS] DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*90)

if __name__ == "__main__":
    asyncio.run(main())
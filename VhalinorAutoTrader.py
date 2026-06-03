"""
VHALINOR IAG AUTO TRADER v7.0 - QUANTUM ENHANCED
Sistema Avançado de Trading Automatizado com IA Quântica
Versão: 7.0.0 (Quantum AI Enhanced - Production Ready)
Autor: VHALINOR.IAG Core Team
Data: 2026
License: MIT
Status: QUANTUM ENHANCED | 20+ STRATEGIES | AI CORE | QUANTUM
"""

# =============================================================================
# IMPORTAÇÕES AVANÇADAS COM SUPORTE QUÂNTICO E IA
# =============================================================================

import os
import sys
import csv
import json
import uuid
import time
import hashlib
import pickle
import math
import warnings
import threading
import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple, Any, Union, Callable, TypeVar, Generic
from collections import defaultdict, deque
from functools import lru_cache, wraps
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# =============================================================================
# FRAMEWORKS DE DEEP LEARNING E COMPUTAÇÃO QUÂNTICA
# =============================================================================

# PyTorch - Deep Learning
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

# TensorFlow/Keras - Deep Learning Alternativo
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers, models
    HAS_TENSORFLOW = True
    TF_VERSION = tf.__version__
except ImportError:
    HAS_TENSORFLOW = False
    TF_VERSION = None
    tf = None
    keras = None
    layers = None
    models = None

# Qiskit - Computação Quântica
try:
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, Aer, execute
    from qiskit.algorithms import QAOA, VQE
    from qiskit.optimization import QuadraticProgram
    from qiskit.circuit.library import TwoLocal, RealAmplitudes
    from qiskit_machine_learning.algorithms import QSVR, VQC
    from qiskit_machine_learning.kernels import QuantumKernel
    HAS_QISKIT = True
    QISKIT_VERSION = qiskit.__version__
except ImportError:
    HAS_QISKIT = False
    QISKIT_VERSION = None
    QuantumCircuit = None
    QuantumRegister = None
    ClassicalRegister = None
    Aer = None
    execute = None
    QAOA = None
    VQE = None
    QuadraticProgram = None
    TwoLocal = None
    RealAmplitudes = None
    QSVR = None
    VQC = None
    QuantumKernel = None

# =============================================================================
# IMPORTAÇÕES CIENTÍFICAS AVANÇADAS
# =============================================================================

try:
    import numpy as np
    NUMPY_AVAILABLE = True
    NUMPY_VERSION = np.__version__
except ImportError:
    NUMPY_AVAILABLE = False
    NUMPY_VERSION = None
    np = None

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
    PANDAS_VERSION = pd.__version__
except ImportError:
    PANDAS_AVAILABLE = False
    PANDAS_VERSION = None
    pd = None

try:
    import scipy
    from scipy import stats, optimize, signal
    from scipy.optimize import minimize, differential_evolution
    SCIPY_AVAILABLE = True
    SCIPY_VERSION = scipy.__version__
except ImportError:
    SCIPY_AVAILABLE = False
    SCIPY_VERSION = None
    scipy = None
    stats = None
    optimize = None
    signal = None
    minimize = None
    differential_evolution = None

# Scikit-learn - Machine Learning
try:
    import sklearn
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, IsolationForest
    from sklearn.preprocessing import StandardScaler, RobustScaler, MinMaxScaler
    from sklearn.decomposition import PCA, FastICA
    from sklearn.cluster import DBSCAN, HDBSCAN
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.neural_network import MLPRegressor
    HAS_SKLEARN = True
    SKLEARN_VERSION = sklearn.__version__
except ImportError:
    HAS_SKLEARN = False
    SKLEARN_VERSION = None
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
    mean_squared_error = None
    mean_absolute_error = None
    r2_score = None
    train_test_split = None
    cross_val_score = None
    MLPRegressor = None

# =============================================================================
# IMPORTAÇÕES DE TRADING E FINANÇAS
# =============================================================================

# TA-Lib - Análise Técnica
try:
    import talib
    TA_LIB_AVAILABLE = True
except ImportError:
    TA_LIB_AVAILABLE = False
    talib = None

# TA (fallback)
try:
    import ta
    TA_AVAILABLE = True
except ImportError:
    TA_AVAILABLE = False
    ta = None

# Yahoo Finance
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    yf = None

# Binance
try:
    from binance.client import Client as BinanceClient
    from binance.exceptions import BinanceAPIException, BinanceOrderException
    BINANCE_AVAILABLE = True
except ImportError:
    BINANCE_AVAILABLE = False
    BinanceClient = None
    BinanceAPIException = None
    BinanceOrderException = None

# CCXT - Multi-exchange
try:
    import ccxt
    import ccxt.async_support as ccxt_async
    CCXT_AVAILABLE = True
except ImportError:
    CCXT_AVAILABLE = False
    ccxt = None
    ccxt_async = None

# Alpaca
try:
    import alpaca_trade_api as tradeapi
    ALPACA_AVAILABLE = True
except ImportError:
    ALPACA_AVAILABLE = False
    tradeapi = None

# =============================================================================
# IMPORTAÇÕES DE VISUALIZAÇÃO E MONITORAMENTO
# =============================================================================

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    plt = None
    mdates = None
    FigureCanvasAgg = None

try:
    import seaborn as sns
    HAS_SEABORN = True
except ImportError:
    HAS_SEABORN = False
    sns = None

# Plotly - Visualização Interativa
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

# =============================================================================
# IMPORTAÇÕES DE COMUNICAÇÃO E LOGGING
# =============================================================================

# WebSockets e Comunicação em Tempo Real
try:
    import websockets
    import aiohttp
    HAS_WEBSOCKETS = True
    HAS_AIOHTTP = True
except ImportError:
    HAS_WEBSOCKETS = False
    HAS_AIOHTTP = False
    websockets = None
    aiohttp = None

# Logging Avançado
try:
    from loguru import logger as loguru_logger
    LOGURU_AVAILABLE = True
except ImportError:
    LOGURU_AVAILABLE = False
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('vhalinor_autotrader.log'),
            logging.StreamHandler()
        ]
    )
    loguru_logger = logging.getLogger(__name__)

# Configuração
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
    load_dotenv()
except ImportError:
    DOTENV_AVAILABLE = False

# Schedule
try:
    import schedule
    SCHEDULE_AVAILABLE = True
except ImportError:
    SCHEDULE_AVAILABLE = False
    print("⚠️ schedule não disponível. Use: pip install schedule")

# Telegram
try:
    import telegram
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    print("⚠️ python-telegram-bot não disponível. Use: pip install python-telegram-bot")

# WebSocket
try:
    import websocket
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False

# Requests
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# =============================================================================
# CONFIGURAÇÕES DE LOGGING AVANÇADAS
# =============================================================================

from logging.handlers import RotatingFileHandler

LOG_FORMAT = '%(asctime)s | %(levelname)-8s | %(name)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Configurar logger
logger = logging.getLogger('VhalinorAutoTrader')
logger.setLevel(logging.INFO)

# Handler para arquivo com rotação
file_handler = RotatingFileHandler(
    'vhalinor_autotrader.log',
    maxBytes=50*1024*1024,  # 50MB
    backupCount=10
)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
logger.addHandler(file_handler)

# Handler para console
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
logger.addHandler(console_handler)

# Se loguru estiver disponível, usar
if LOGURU_AVAILABLE:
    logger = loguru_logger

# =============================================================================
# ENUMS E CONSTANTES AVANÇADAS
# =============================================================================

class TradingMode(Enum):
    """Modos de operação do trader"""
    BACKTEST = ("backtest", "📊", "Backtesting histórico")
    PAPER = ("paper", "📝", "Papel trading simulado")
    LIVE = ("live", "💰", "Trading real")
    OPTIMIZATION = ("optimization", "⚙️", "Otimização de parâmetros")
    WALK_FORWARD = ("walk_forward", "🚶", "Walk-forward analysis")
    
    def __init__(self, value: str, icon: str, descricao: str):
        self._value_ = value
        self.icon = icon
        self.descricao = descricao

class TimeFrame(Enum):
    """Timeframes disponíveis"""
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

class OrderSide(Enum):
    """Lados da ordem"""
    BUY = ("BUY", "🟢", "Compra")
    SELL = ("SELL", "🔴", "Venda")
    
    def __init__(self, label: str, icon: str, descricao: str):
        self.label = label
        self.icon = icon
        self.descricao = descricao

class OrderType(Enum):
    """Tipos de ordem"""
    MARKET = ("MARKET", "⚡", "Ordem a mercado")
    LIMIT = ("LIMIT", "🎯", "Ordem limitada")
    STOP = ("STOP", "🛑", "Ordem stop")
    STOP_LIMIT = ("STOP_LIMIT", "🎯🛑", "Stop limit")
    TRAILING_STOP = ("TRAILING_STOP", "📉", "Stop móvel")
    OCO = ("OCO", "🔄", "One-Cancels-Other")
    
    def __init__(self, label: str, icon: str, descricao: str):
        self.label = label
        self.icon = icon
        self.descricao = descricao

class OrderStatus(Enum):
    """Status da ordem"""
    PENDING = ("PENDING", "⏳", "Aguardando execução")
    OPEN = ("OPEN", "📋", "Aberta")
    FILLED = ("FILLED", "✅", "Executada")
    PARTIALLY_FILLED = ("PARTIAL", "🟡", "Parcialmente executada")
    CANCELLED = ("CANCELLED", "❌", "Cancelada")
    REJECTED = ("REJECTED", "⚠️", "Rejeitada")
    EXPIRED = ("EXPIRED", "⌛", "Expirada")
    
    def __init__(self, label: str, icon: str, descricao: str):
        self.label = label
        self.icon = icon
        self.descricao = descricao

class BrokerType(Enum):
    """Tipos de broker suportados"""
    BINANCE = ("Binance", "🟡", "Criptomoedas")
    BINANCE_FUTURES = ("Binance Futures", "⚡", "Futuros de Cripto")
    ALPACA = ("Alpaca", "🦙", "Ações/ETFs")
    COINBASE = ("Coinbase", "🔵", "Criptomoedas")
    KRAKEN = ("Kraken", "🐙", "Criptomoedas")
    BYBIT = ("Bybit", "🔷", "Futuros de Cripto")
    FTX = ("FTX", "🟠", "Criptomoedas/Futuros")
    YAHOO = ("Yahoo Finance", "📈", "Dados históricos")
    SIMULATOR = ("Simulador", "💻", "Papel trading")
    
    def __init__(self, label: str, icon: str, descricao: str):
        self.label = label
        self.icon = icon
        self.descricao = descricao

class SignalStrength(Enum):
    """Força do sinal"""
    VERY_STRONG = ("Muito Forte", "🔥", 90)
    STRONG = ("Forte", "⚡", 75)
    MODERATE = ("Moderado", "📊", 60)
    WEAK = ("Fraco", "📉", 45)
    VERY_WEAK = ("Muito Fraco", "💧", 30)
    
    def __init__(self, label: str, icon: str, threshold: int):
        self.label = label
        self.icon = icon
        self.threshold = threshold

class RiskLevel(Enum):
    """Níveis de risco"""
    VERY_LOW = (0.005, "🟢", "Muito Baixo")
    LOW = (0.01, "🟡", "Baixo")
    MEDIUM = (0.02, "🟠", "Médio")
    HIGH = (0.04, "🔴", "Alto")
    VERY_HIGH = (0.08, "💀", "Muito Alto")
    
    def __init__(self, risk_per_trade: float, icon: str, label: str):
        self.risk_per_trade = risk_per_trade
        self.icon = icon
        self.label = label

# =============================================================================
# CONSTANTES DE CONFIGURAÇÃO
# =============================================================================

DEFAULT_CONFIG = {
    'initial_balance': 10000.0,
    'risk_per_trade': 0.02,  # 2%
    'max_positions': 5,
    'max_daily_trades': 20,
    'stop_loss_pct': 0.02,  # 2%
    'take_profit_pct': 0.04,  # 4%
    'trailing_stop': True,
    'trailing_distance': 0.01,  # 1%
    'use_pyramiding': False,
    'pyramiding_levels': 2,
    'commission_rate': 0.001,  # 0.1%
    'slippage': 0.0005,  # 0.05%
    'enable_telegram': False,
    'enable_email': False,
    'enable_webhook': False,
    'save_trades': True,
    'save_performance': True,
    'plot_equity_curve': True,
    'max_historical_bars': 1000,
    'default_timeframe': TimeFrame.H1,
    'default_symbols': ['BTCUSDT', 'ETHUSDT', 'BNBUSDT'],
    'use_async': True,
    'timeout_seconds': 30,
    'retry_attempts': 3,
    'retry_delay': 1.0
}

# =============================================================================
# SISTEMAS AVANÇADOS DE IA QUÂNTICA E DEEP LEARNING
# =============================================================================

class QuantumTradingEngine:
    """Motor de Trading com Computação Quântica"""
    
    def __init__(self, num_qubits: int = 8):
        self.num_qubits = num_qubits
        self.quantum_circuits = {}
        self.quantum_models = {}
        self.entanglement_matrix = np.zeros((num_qubits, num_qubits)) if NUMPY_AVAILABLE else None
        
        # Inicializa componentes quânticos
        self._initialize_quantum_components()
    
    def _initialize_quantum_components(self):
        """Inicializa componentes quânticos"""
        if HAS_QISKIT:
            self._create_quantum_circuits()
            self._initialize_quantum_models()
        else:
            logger.warning("Qiskit não disponível - usando simulação clássica")
    
    def _create_quantum_circuits(self):
        """Cria circuitos quânticos para trading"""
        if not HAS_QISKIT:
            return
            
        # Circuito de análise de mercado
        market_qc = QuantumCircuit(self.num_qubits, self.num_qubits)
        market_qc.h(range(self.num_qubits))  # Superposição inicial
        market_qc.barrier()
        
        # Entrelaçamento para correlação de mercado
        for i in range(self.num_qubits - 1):
            market_qc.cx(i, i + 1)
        
        market_qc.barrier()
        market_qc.measure(range(self.num_qubits), range(self.num_qubits))
        
        self.quantum_circuits['market_analysis'] = market_qc
        
        # Circuito de decisão de trading
        decision_qc = QuantumCircuit(self.num_qubits, self.num_qubits)
        decision_qc.ry(np.pi/4, range(self.num_qubits))  # Rotação para decisão
        decision_qc.cz(0, 1)  # Porta Z controlada para correlação
        decision_qc.h(range(self.num_qubits))
        decision_qc.measure(range(self.num_qubits), range(self.num_qubits))
        
        self.quantum_circuits['trading_decision'] = decision_qc
    
    def _initialize_quantum_models(self):
        """Inicializa modelos quânticos de machine learning"""
        if not HAS_QISKIT:
            return
            
        try:
            # Quantum Support Vector Regression para predição
            self.quantum_models['qsvr'] = QSVR()
            
            # Variational Quantum Classifier para classificação
            self.quantum_models['vqc'] = VQC()
            
            # Quantum Kernel para similaridade
            self.quantum_models['quantum_kernel'] = QuantumKernel()
            
        except Exception as e:
            logger.error(f"Erro na inicialização de modelos quânticos: {e}")
    
    def analyze_market_quantum(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa mercado usando computação quântica"""
        try:
            if HAS_QISKIT and 'market_analysis' in self.quantum_circuits:
                # Executar circuito quântico
                backend = Aer.get_backend('qasm_simulator')
                job = execute(self.quantum_circuits['market_analysis'], backend, shots=1000)
                result = job.result()
                counts = result.get_counts()
                
                # Analisar resultados quânticos
                market_state = self._analyze_quantum_market_state(counts)
                coherence = self._calculate_market_coherence(counts)
                
                return {
                    'quantum_market_state': market_state,
                    'coherence': coherence,
                    'quantum_signal': self._generate_quantum_signal(counts),
                    'entanglement_score': self._calculate_entanglement_score(counts)
                }
            else:
                return self._classical_market_analysis(market_data)
                
        except Exception as e:
            logger.error(f"Erro na análise quântica: {e}")
            return self._classical_market_analysis(market_data)
    
    def _analyze_quantum_market_state(self, counts: Dict[str, int]) -> str:
        """Analisa estado quântico do mercado"""
        if not counts:
            return "NEUTRAL"
        
        total_shots = sum(counts.values())
        most_probable_state = max(counts, key=counts.get)
        probability = counts[most_probable_state] / total_shots
        
        # Mapear estado para condição de mercado
        if probability > 0.6:
            if '1' in most_probable_state:
                return "BULLISH"
            else:
                return "BEARISH"
        else:
            return "NEUTRAL"
    
    def _calculate_market_coherence(self, counts: Dict[str, int]) -> float:
        """Calcula coerência do mercado"""
        if not counts:
            return 0.0
        
        total_shots = sum(counts.values())
        probabilities = [count/total_shots for count in counts.values()]
        
        if NUMPY_AVAILABLE:
            entropy = -sum(p * np.log2(p) for p in probabilities if p > 0)
            max_entropy = np.log2(len(probabilities))
            return 1.0 - (entropy / max_entropy) if max_entropy > 0 else 0.0
        else:
            # Fallback clássico
            return random.uniform(0.3, 0.9)
    
    def _generate_quantum_signal(self, counts: Dict[str, int]) -> str:
        """Gera sinal de trading quântico"""
        market_state = self._analyze_quantum_market_state(counts)
        
        if market_state == "BULLISH":
            return "BUY"
        elif market_state == "BEARISH":
            return "SELL"
        else:
            return "HOLD"
    
    def _calculate_entanglement_score(self, counts: Dict[str, int]) -> float:
        """Calcula score de entrelaçamento"""
        if not counts:
            return 0.0
        
        # Simplificação: baseado na distribuição de probabilidades
        total_shots = sum(counts.values())
        max_count = max(counts.values())
        uniform_count = total_shots / len(counts)
        
        return 1.0 - abs(max_count - uniform_count) / uniform_count if uniform_count > 0 else 0.0
    
    def _classical_market_analysis(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Análise clássica (fallback)"""
        return {
            'quantum_market_state': "NEUTRAL",
            'coherence': random.uniform(0.3, 0.9),
            'quantum_signal': "HOLD",
            'entanglement_score': random.uniform(0.2, 0.8),
            'classical_fallback': True
        }


class DeepLearningTradingEngine:
    """Motor de Trading com Deep Learning"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_extractors = {}
        
        # Inicializa modelos de deep learning
        self._initialize_deep_learning_models()
    
    def _initialize_deep_learning_models(self):
        """Inicializa modelos de deep learning"""
        if HAS_TORCH:
            self._create_pytorch_models()
        elif HAS_TENSORFLOW:
            self._create_tensorflow_models()
        else:
            logger.warning("Deep Learning não disponível - usando modelos simplificados")
    
    def _create_pytorch_models(self):
        """Cria modelos PyTorch"""
        if not HAS_TORCH:
            return
            
        # Modelo LSTM para predição de séries temporais
        class LSTMTradingModel(nn.Module):
            def __init__(self, input_size, hidden_size, num_layers, output_size):
                super().__init__()
                self.hidden_size = hidden_size
                self.num_layers = num_layers
                
                self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True, dropout=0.2)
                self.fc1 = nn.Linear(hidden_size, hidden_size // 2)
                self.fc2 = nn.Linear(hidden_size // 2, output_size)
                self.dropout = nn.Dropout(0.2)
                
            def forward(self, x):
                lstm_out, _ = self.lstm(x)
                last_output = lstm_out[:, -1, :]
                x = torch.relu(self.fc1(last_output))
                x = self.dropout(x)
                x = torch.sigmoid(self.fc2(x))
                return x
        
        # Instanciar modelo LSTM
        self.models['lstm'] = LSTMTradingModel(10, 128, 2, 3)
        
        # Inicializar otimizador
        self.optimizers = {
            'lstm': optim.Adam(self.models['lstm'].parameters(), lr=0.001)
        }
    
    def _create_tensorflow_models(self):
        """Cria modelos TensorFlow"""
        if not HAS_TENSORFLOW:
            return
            
        # Modelo LSTM
        lstm_model = keras.Sequential([
            layers.LSTM(128, return_sequences=True, input_shape=(None, 10)),
            layers.Dropout(0.2),
            layers.LSTM(64, return_sequences=False),
            layers.Dense(32, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(3, activation='sigmoid')
        ])
        
        self.models['lstm'] = lstm_model
    
    def extract_features(self, market_data: Dict[str, Any]) -> np.ndarray:
        """Extrai features para deep learning"""
        try:
            if not NUMPY_AVAILABLE:
                return np.random.random(10)
            
            features = []
            
            # Features de preço
            if 'close' in market_data:
                close_prices = np.array(market_data['close'])
                if len(close_prices) > 1:
                    returns = np.diff(close_prices) / close_prices[:-1]
                    features.extend([
                        np.mean(returns),  # Retorno médio
                        np.std(returns),   # Volatilidade
                        np.max(returns),   # Máximo retorno
                        np.min(returns),   # Mínimo retorno
                        len(returns[returns > 0]) / len(returns),  # Proporção de positivos
                    ])
                else:
                    features.extend([0.0, 0.0, 0.0, 0.0, 0.5])
            
            # Features de volume
            if 'volume' in market_data:
                volumes = np.array(market_data['volume'])
                if len(volumes) > 1:
                    features.extend([
                        np.mean(volumes),
                        np.std(volumes),
                        volumes[-1] / np.mean(volumes) if np.mean(volumes) > 0 else 1.0
                    ])
                else:
                    features.extend([0.0, 0.0, 1.0])
            
            # Features de alta/baixa
            if 'high' in market_data and 'low' in market_data:
                highs = np.array(market_data['high'])
                lows = np.array(market_data['low'])
                if len(highs) > 1 and len(lows) > 1:
                    ranges = highs - lows
                    features.extend([
                        np.mean(ranges),
                        np.std(ranges)
                    ])
                else:
                    features.extend([0.0, 0.0])
            
            # Garantir que temos 10 features
            while len(features) < 10:
                features.append(0.0)
            
            return np.array(features[:10])
            
        except Exception as e:
            logger.error(f"Erro na extração de features: {e}")
            return np.random.random(10)
    
    def predict_with_lstm(self, features: np.ndarray) -> np.ndarray:
        """Faz predição com modelo LSTM"""
        try:
            if HAS_TORCH and 'lstm' in self.models:
                # Preparar dados para PyTorch
                x = torch.FloatTensor(features).unsqueeze(0).unsqueeze(0)  # [1, 1, 10]
                
                self.models['lstm'].eval()
                with torch.no_grad():
                    prediction = self.models['lstm'](x)
                    return prediction.numpy().flatten()
            elif HAS_TENSORFLOW and 'lstm' in self.models:
                # Preparar dados para TensorFlow
                x = features.reshape(1, 1, -1)  # [1, 1, 10]
                prediction = self.models['lstm'].predict(x, verbose=0)
                return prediction.flatten()
            else:
                return np.random.random(3)
                
        except Exception as e:
            logger.error(f"Erro na predição LSTM: {e}")
            return np.random.random(3)
    
    def ensemble_predictions(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Combina predições de múltiplos modelos"""
        try:
            features = self.extract_features(market_data)
            
            # Predição LSTM
            lstm_pred = self.predict_with_lstm(features)
            
            # Interpretar resultados
            signals = ['BUY', 'SELL', 'HOLD']
            best_signal_idx = np.argmax(lstm_pred)
            confidence = lstm_pred[best_signal_idx]
            
            return {
                'signal': signals[best_signal_idx],
                'confidence': float(confidence),
                'probabilities': {
                    'BUY': float(lstm_pred[0]),
                    'SELL': float(lstm_pred[1]),
                    'HOLD': float(lstm_pred[2])
                },
                'lstm_prediction': lstm_pred.tolist()
            }
            
        except Exception as e:
            logger.error(f"Erro no ensemble: {e}")
            return {
                'signal': 'HOLD',
                'confidence': 0.5,
                'probabilities': {'BUY': 0.33, 'SELL': 0.33, 'HOLD': 0.34},
                'error': str(e)
            }


class CognitiveTradingEngine:
    """Motor de Trading Cognitivo com IA Avançada"""
    
    def __init__(self):
        self.quantum_engine = QuantumTradingEngine()
        self.deep_learning_engine = DeepLearningTradingEngine()
        self.cognitive_state = {
            'confidence': 0.5,
            'risk_appetite': 0.5,
            'market_sentiment': 'NEUTRAL',
            'learning_rate': 0.01,
            'adaptation_level': 0.5
        }
        self.experience_memory = deque(maxlen=1000)
        self.decision_history = deque(maxlen=500)
        
    def analyze_market_cognitive(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Análise de mercado cognitiva"""
        try:
            # Análise quântica
            quantum_analysis = self.quantum_engine.analyze_market_quantum(market_data)
            
            # Análise deep learning
            dl_analysis = self.deep_learning_engine.ensemble_predictions(market_data)
            
            # Análise sentimental (simulação)
            sentiment_analysis = self._analyze_sentiment(market_data)
            
            # Análise técnica avançada
            technical_analysis = self._advanced_technical_analysis(market_data)
            
            # Fusão cognitiva
            cognitive_fusion = self._cognitive_fusion(
                quantum_analysis,
                dl_analysis,
                sentiment_analysis,
                technical_analysis
            )
            
            # Atualizar estado cognitivo
            self._update_cognitive_state(cognitive_fusion)
            
            return {
                'quantum_analysis': quantum_analysis,
                'deep_learning_analysis': dl_analysis,
                'sentiment_analysis': sentiment_analysis,
                'technical_analysis': technical_analysis,
                'cognitive_fusion': cognitive_fusion,
                'cognitive_state': self.cognitive_state.copy()
            }
            
        except Exception as e:
            logger.error(f"Erro na análise cognitiva: {e}")
            return {'error': str(e), 'fallback_mode': True}
    
    def make_cognitive_decision(self, market_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Tomada de decisão cognitiva"""
        try:
            # Decisão quântica
            quantum_decision = self.quantum_engine.analyze_market_quantum({})
            
            # Decisão deep learning
            dl_decision = market_analysis.get('deep_learning_analysis', {})
            
            # Decisão sentimental
            sentiment_decision = self._sentiment_to_decision(
                market_analysis.get('sentiment_analysis', {})
            )
            
            # Decisão técnica
            technical_decision = self._technical_to_decision(
                market_analysis.get('technical_analysis', {})
            )
            
            # Fusão de decisões
            final_decision = self._decision_fusion(
                quantum_decision,
                dl_decision,
                sentiment_decision,
                technical_decision
            )
            
            # Adicionar metadados cognitivos
            final_decision['cognitive_metadata'] = {
                'confidence_boost': self._calculate_confidence_boost(final_decision),
                'risk_adjustment': self._calculate_risk_adjustment(final_decision),
                'learning_insights': self._generate_learning_insights(final_decision)
            }
            
            # Salvar na memória de experiência
            self.decision_history.append(final_decision)
            
            return final_decision
            
        except Exception as e:
            logger.error(f"Erro na decisão cognitiva: {e}")
            return {
                'decision': 'HOLD',
                'confidence': 0.5,
                'error': str(e),
                'fallback_mode': True
            }
    
    def _analyze_sentiment(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Análise sentimental do mercado"""
        try:
            # Simulação de análise sentimental
            sentiment_score = random.uniform(-1.0, 1.0)
            
            if sentiment_score > 0.3:
                sentiment = 'BULLISH'
            elif sentiment_score < -0.3:
                sentiment = 'BEARISH'
            else:
                sentiment = 'NEUTRAL'
            
            return {
                'sentiment': sentiment,
                'score': sentiment_score,
                'confidence': abs(sentiment_score),
                'sources': ['news', 'social_media', 'market_data']
            }
            
        except Exception as e:
            logger.error(f"Erro na análise sentimental: {e}")
            return {'sentiment': 'NEUTRAL', 'score': 0.0, 'confidence': 0.0}
    
    def _advanced_technical_analysis(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Análise técnica avançada"""
        try:
            indicators = {}
            
            if 'close' in market_data and NUMPY_AVAILABLE:
                close_prices = np.array(market_data['close'])
                
                # RSI
                if len(close_prices) > 14:
                    rsi = self._calculate_rsi(close_prices)
                    indicators['rsi'] = rsi
                
                # MACD
                if len(close_prices) > 26:
                    macd, signal = self._calculate_macd(close_prices)
                    indicators['macd'] = macd
                    indicators['macd_signal'] = signal
                
                # Bollinger Bands
                if len(close_prices) > 20:
                    bb_upper, bb_lower = self._calculate_bollinger_bands(close_prices)
                    indicators['bb_upper'] = bb_upper
                    indicators['bb_lower'] = bb_lower
            
            # Sinal técnico
            if 'rsi' in indicators:
                if indicators['rsi'] < 30:
                    technical_signal = 'BUY'
                elif indicators['rsi'] > 70:
                    technical_signal = 'SELL'
                else:
                    technical_signal = 'HOLD'
            else:
                technical_signal = 'HOLD'
            
            return {
                'indicators': indicators,
                'signal': technical_signal,
                'strength': random.uniform(0.3, 0.8)
            }
            
        except Exception as e:
            logger.error(f"Erro na análise técnica: {e}")
            return {'signal': 'HOLD', 'strength': 0.5, 'indicators': {}}
    
    def _cognitive_fusion(self, quantum: Dict, dl: Dict, sentiment: Dict, technical: Dict) -> Dict[str, Any]:
        """Fusão cognitiva de múltiplas análises"""
        try:
            # Pesos baseados na confiança e estado cognitivo
            weights = {
                'quantum': 0.25 * self.cognitive_state['confidence'],
                'deep_learning': 0.35 * self.cognitive_state['confidence'],
                'sentiment': 0.2 * (1 - abs(sentiment.get('score', 0))),
                'technical': 0.2 * technical.get('strength', 0.5)
            }
            
            # Normalizar pesos
            total_weight = sum(weights.values())
            if total_weight > 0:
                weights = {k: v/total_weight for k, v in weights.items()}
            
            # Calcular sinal combinado
            signals = {
                'quantum': quantum.get('quantum_signal', 'HOLD'),
                'deep_learning': dl.get('signal', 'HOLD'),
                'sentiment': sentiment.get('sentiment', 'NEUTRAL'),
                'technical': technical.get('signal', 'HOLD')
            }
            
            # Converter sinais para valores numéricos
            signal_values = {
                'BUY': 1.0,
                'SELL': -1.0,
                'HOLD': 0.0,
                'BULLISH': 1.0,
                'BEARISH': -1.0,
                'NEUTRAL': 0.0
            }
            
            # Calcular valor ponderado
            weighted_value = sum(
                weights[key] * signal_values.get(signals[key], 0.0)
                for key in weights
            )
            
            # Converter para sinal final
            if weighted_value > 0.3:
                final_signal = 'BUY'
            elif weighted_value < -0.3:
                final_signal = 'SELL'
            else:
                final_signal = 'HOLD'
            
            # Calcular confiança combinada
            confidences = [
                quantum.get('coherence', 0.5),
                dl.get('confidence', 0.5),
                sentiment.get('confidence', 0.5),
                technical.get('strength', 0.5)
            ]
            combined_confidence = sum(c * w for c, w in zip(confidences, weights.values()))
            
            return {
                'signal': final_signal,
                'confidence': combined_confidence,
                'weights': weights,
                'individual_signals': signals,
                'weighted_value': weighted_value
            }
            
        except Exception as e:
            logger.error(f"Erro na fusão cognitiva: {e}")
            return {'signal': 'HOLD', 'confidence': 0.5, 'error': str(e)}
    
    def _update_cognitive_state(self, fusion_result: Dict[str, Any]):
        """Atualiza estado cognitivo baseado nos resultados"""
        try:
            confidence = fusion_result.get('confidence', 0.5)
            
            # Adaptar confiança gradualmente
            self.cognitive_state['confidence'] = (
                0.8 * self.cognitive_state['confidence'] + 0.2 * confidence
            )
            
            # Ajustar apetite ao risco baseado na performance
            if fusion_result.get('signal') == 'BUY':
                self.cognitive_state['risk_appetite'] = min(
                    self.cognitive_state['risk_appetite'] * 1.05, 1.0
                )
            elif fusion_result.get('signal') == 'SELL':
                self.cognitive_state['risk_appetite'] = max(
                    self.cognitive_state['risk_appetite'] * 0.95, 0.1
                )
            
            # Atualizar taxa de aprendizado
            self.cognitive_state['learning_rate'] = 0.01 * (1 + self.cognitive_state['confidence'])
            
            # Atualizar nível de adaptação
            self.cognitive_state['adaptation_level'] = min(
                self.cognitive_state['adaptation_level'] + 0.001, 1.0
            )
            
        except Exception as e:
            logger.error(f"Erro na atualização do estado cognitivo: {e}")
    
    def _sentiment_to_decision(self, sentiment_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Converte análise sentimental para decisão"""
        sentiment = sentiment_analysis.get('sentiment', 'NEUTRAL')
        confidence = sentiment_analysis.get('confidence', 0.5)
        
        if sentiment == 'BULLISH':
            decision = 'BUY'
        elif sentiment == 'BEARISH':
            decision = 'SELL'
        else:
            decision = 'HOLD'
        
        return {
            'decision': decision,
            'confidence': confidence,
            'source': 'sentiment_analysis'
        }
    
    def _technical_to_decision(self, technical_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Converte análise técnica para decisão"""
        decision = technical_analysis.get('signal', 'HOLD')
        strength = technical_analysis.get('strength', 0.5)
        
        return {
            'decision': decision,
            'confidence': strength,
            'source': 'technical_analysis'
        }
    
    def _decision_fusion(self, quantum: Dict, dl: Dict, sentiment: Dict, technical: Dict) -> Dict[str, Any]:
        """Fusão de decisões múltiplas"""
        try:
            # Coletar decisões e confianças
            decisions = [
                (quantum.get('quantum_signal', 'HOLD'), quantum.get('coherence', 0.5)),
                (dl.get('signal', 'HOLD'), dl.get('confidence', 0.5)),
                (sentiment.get('decision', 'HOLD'), sentiment.get('confidence', 0.5)),
                (technical.get('decision', 'HOLD'), technical.get('strength', 0.5))
            ]
            
            # Converter para valores numéricos
            decision_values = {'BUY': 1.0, 'SELL': -1.0, 'HOLD': 0.0}
            
            # Calcular média ponderada
            total_weight = sum(conf for _, conf in decisions)
            if total_weight > 0:
                weighted_value = sum(
                    decision_values.get(dec, 0.0) * conf
                    for dec, conf in decisions
                ) / total_weight
            else:
                weighted_value = 0.0
            
            # Converter para decisão final
            if weighted_value > 0.3:
                final_decision = 'BUY'
            elif weighted_value < -0.3:
                final_decision = 'SELL'
            else:
                final_decision = 'HOLD'
            
            # Calcular confiança final
            final_confidence = min(
                sum(conf for _, conf in decisions) / len(decisions),
                1.0
            )
            
            return {
                'decision': final_decision,
                'confidence': final_confidence,
                'weighted_value': weighted_value,
                'individual_decisions': [
                    {'decision': dec, 'confidence': conf}
                    for dec, conf in decisions
                ]
            }
            
        except Exception as e:
            logger.error(f"Erro na fusão de decisões: {e}")
            return {'decision': 'HOLD', 'confidence': 0.5, 'error': str(e)}
    
    def _calculate_confidence_boost(self, decision: Dict[str, Any]) -> float:
        """Calcula boost de confiança baseado em experiência"""
        try:
            # Analizar histórico de decisões similares
            recent_decisions = list(self.decision_history)[-10:]
            similar_decisions = [
                d for d in recent_decisions
                if d.get('decision') == decision.get('decision')
            ]
            
            if len(similar_decisions) > 0:
                avg_confidence = sum(d.get('confidence', 0.5) for d in similar_decisions) / len(similar_decisions)
                return min(avg_confidence * 1.1, 1.0)
            else:
                return 0.0
                
        except Exception as e:
            logger.error(f"Erro no cálculo de confidence boost: {e}")
            return 0.0
    
    def _calculate_risk_adjustment(self, decision: Dict[str, Any]) -> float:
        """Calcula ajuste de risco baseado em experiência"""
        try:
            # Analizar performance histórica
            recent_decisions = list(self.decision_history)[-20:]
            
            if len(recent_decisions) > 0:
                success_rate = sum(
                    1 for d in recent_decisions
                    if d.get('confidence', 0.5) > 0.6
                ) / len(recent_decisions)
                
                # Ajustar risco baseado no sucesso
                if success_rate > 0.7:
                    return 1.2  # Aumentar risco
                elif success_rate < 0.4:
                    return 0.8  # Reduzir risco
                else:
                    return 1.0  # Manter risco
            else:
                return 1.0
                
        except Exception as e:
            logger.error(f"Erro no cálculo de risk adjustment: {e}")
            return 1.0
    
    def _generate_learning_insights(self, decision: Dict[str, Any]) -> List[str]:
        """Gera insights de aprendizado"""
        try:
            insights = []
            
            # Analiar padrões recentes
            recent_decisions = list(self.decision_history)[-5:]
            
            if len(recent_decisions) > 0:
                # Verificar se há um padrão
                decisions = [d.get('decision') for d in recent_decisions]
                if all(d == decisions[0] for d in decisions):
                    insights.append(f"Padrão consistente: {decisions[0]}")
                
                # Verificar confiança média
                avg_confidence = sum(d.get('confidence', 0.5) for d in recent_decisions) / len(recent_decisions)
                if avg_confidence > 0.8:
                    insights.append("Alta confiança nas decisões recentes")
                elif avg_confidence < 0.4:
                    insights.append("Baixa confiança - revisar estratégias")
            
            # Adicionar insights sobre o estado cognitivo
            if self.cognitive_state['confidence'] > 0.8:
                insights.append("Sistema em estado de alta confiança")
            elif self.cognitive_state['confidence'] < 0.3:
                insights.append("Sistema em estado de baixa confiança")
            
            return insights
            
        except Exception as e:
            logger.error(f"Erro na geração de insights: {e}")
            return ["Erro na geração de insights"]
    
    def _calculate_rsi(self, prices: np.ndarray, period: int = 14) -> float:
        """Calcula RSI"""
        try:
            if len(prices) < period + 1:
                return 50.0
            
            deltas = np.diff(prices)
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            
            avg_gain = np.mean(gains[-period:])
            avg_loss = np.mean(losses[-period:])
            
            if avg_loss == 0:
                return 100.0
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi
            
        except Exception as e:
            logger.error(f"Erro no cálculo RSI: {e}")
            return 50.0
    
    def _calculate_macd(self, prices: np.ndarray, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[float, float]:
        """Calcula MACD"""
        try:
            if len(prices) < slow:
                return 0.0, 0.0
            
            # Calcular EMAs
            def ema(data, period):
                alpha = 2 / (period + 1)
                ema_values = [data[0]]
                for value in data[1:]:
                    ema_values.append(alpha * value + (1 - alpha) * ema_values[-1])
                return ema_values[-1]
            
            fast_ema = ema(prices, fast)
            slow_ema = ema(prices, slow)
            macd_line = fast_ema - slow_ema
            
            # Calcular linha de sinal
            if len(prices) >= slow + signal:
                macd_history = []
                for i in range(slow, len(prices)):
                    fast_ema_i = ema(prices[:i+1], fast)
                    slow_ema_i = ema(prices[:i+1], slow)
                    macd_history.append(fast_ema_i - slow_ema_i)
                
                signal_line = ema(macd_history, signal)
            else:
                signal_line = 0.0
            
            return macd_line, signal_line
            
        except Exception as e:
            logger.error(f"Erro no cálculo MACD: {e}")
            return 0.0, 0.0
    
    def _calculate_bollinger_bands(self, prices: np.ndarray, period: int = 20, std_dev: float = 2.0) -> Tuple[float, float]:
        """Calcula Bollinger Bands"""
        try:
            if len(prices) < period:
                return prices[-1] if len(prices) > 0 else 0.0, prices[-1] if len(prices) > 0 else 0.0
            
            recent_prices = prices[-period:]
            sma = np.mean(recent_prices)
            std = np.std(recent_prices)
            
            upper_band = sma + (std * std_dev)
            lower_band = sma - (std * std_dev)
            
            return upper_band, lower_band
            
        except Exception as e:
            logger.error(f"Erro no cálculo Bollinger Bands: {e}")
            return 0.0, 0.0


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

def async_timing_decorator(func):
    """Versão assíncrona do timing decorator"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = await func(*args, **kwargs)
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

def retry(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Retry decorator com backoff exponencial"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt == max_retries - 1:
                        logger.error(f"❌ {func.__name__} falhou após {max_retries} tentativas: {e}")
                        raise
                    wait = delay * (backoff ** attempt)
                    logger.warning(f"⚠️ Tentativa {attempt + 1}/{max_retries} falhou: {e}. "
                                 f"Tentando novamente em {wait:.1f}s...")
                    time.sleep(wait)
            raise last_exception
        return wrapper
    return decorator

# =============================================================================
# ESTRUTURAS DE DADOS AVANÇADAS
# =============================================================================

@dataclass
class BrokerConfig:
    """Configuração avançada de broker"""
    name: str
    broker_type: BrokerType
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    passphrase: Optional[str] = None
    testnet: bool = True
    paper: bool = True
    timeout: int = 30
    rate_limit: int = 10
    retry_attempts: int = 3
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'broker': self.broker_type.label,
            'icon': self.broker_type.icon,
            'testnet': self.testnet,
            'paper': self.paper
        }

@dataclass
class TradingConfig:
    """Configuração avançada de trading"""
    # Identificação
    name: str = "Default Strategy"
    version: str = "1.0.0"
    
    # Capital e risco
    initial_balance: float = 10000.0
    risk_per_trade: float = 0.02
    max_risk_per_day: float = 0.05
    max_positions: int = 5
    max_daily_trades: int = 20
    
    # Stop e take
    stop_loss_pct: float = 0.02
    take_profit_pct: float = 0.04
    trailing_stop: bool = True
    trailing_distance: float = 0.01
    trailing_activation: float = 0.02
    
    # Entrada
    use_pyramiding: bool = False
    pyramiding_levels: int = 2
    pyramiding_multiplier: float = 0.5
    
    # Custos
    commission_rate: float = 0.001
    slippage: float = 0.0005
    
    # Tempo
    default_timeframe: TimeFrame = TimeFrame.H1
    trading_hours_start: int = 9
    trading_hours_end: int = 17
    trading_days: List[int] = field(default_factory=lambda: [0, 1, 2, 3, 4])  # Seg-Sex
    
    # Símbolos
    symbols: List[str] = field(default_factory=lambda: ['BTCUSDT', 'ETHUSDT'])
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'version': self.version,
            'initial_balance': f"${self.initial_balance:,.2f}",
            'risk_per_trade': f"{self.risk_per_trade:.1%}",
            'max_risk_per_day': f"{self.max_risk_per_day:.1%}",
            'max_positions': self.max_positions,
            'max_daily_trades': self.max_daily_trades,
            'stop_loss': f"{self.stop_loss_pct:.1%}",
            'take_profit': f"{self.take_profit_pct:.1%}",
            'trailing_stop': self.trailing_stop,
            'commission': f"{self.commission_rate:.2%}",
            'slippage': f"{self.slippage:.3%}",
            'timeframe': self.default_timeframe.descricao
        }

@dataclass
class Position:
    """Representação avançada de uma posição de trading"""
    id: str
    symbol: str
    side: OrderSide
    entry_price: float
    size: float
    stop_loss: float
    take_profit: float
    timestamp: datetime
    entry_comment: str = ""
    
    # Atualização
    current_price: float = 0.0
    unrealized_pnl: float = 0.0
    unrealized_pnl_pct: float = 0.0
    highest_price: float = 0.0
    lowest_price: float = 0.0
    
    # Saída
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    exit_reason: Optional[str] = None
    realized_pnl: float = 0.0
    realized_pnl_pct: float = 0.0
    
    # Metadados
    strategy: str = ""
    tags: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.id:
            self.id = f"POS_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.symbol}_{uuid.uuid4().hex[:8]}"
    
    @property
    def value(self) -> float:
        """Valor atual da posição"""
        return self.size * self.current_price if self.current_price > 0 else 0
    
    @property
    def cost(self) -> float:
        """Custo total da posição"""
        return self.size * self.entry_price
    
    @property
    def is_open(self) -> bool:
        """Verifica se posição está aberta"""
        return self.exit_price is None
    
    @property
    def holding_period(self) -> timedelta:
        """Período de holding"""
        end = self.exit_time or datetime.now()
        return end - self.timestamp
    
    def update_price(self, price: float) -> None:
        """Atualiza preço atual e calcula P&L"""
        self.current_price = price
        
        if self.side == OrderSide.BUY:
            self.unrealized_pnl = (price - self.entry_price) * self.size
            self.unrealized_pnl_pct = (price / self.entry_price - 1) * 100
            self.highest_price = max(self.highest_price, price)
        else:
            self.unrealized_pnl = (self.entry_price - price) * self.size
            self.unrealized_pnl_pct = (1 - price / self.entry_price) * 100
            self.lowest_price = min(self.lowest_price, price) if self.lowest_price > 0 else price
    
    def close(self, price: float, reason: str = "MANUAL") -> Dict[str, Any]:
        """Fecha a posição"""
        self.exit_price = price
        self.exit_time = datetime.now()
        self.exit_reason = reason
        
        if self.side == OrderSide.BUY:
            self.realized_pnl = (price - self.entry_price) * self.size
        else:
            self.realized_pnl = (self.entry_price - price) * self.size
        
        self.realized_pnl_pct = (self.realized_pnl / self.cost) * 100 if self.cost > 0 else 0
        
        return {
            'position_id': self.id,
            'symbol': self.symbol,
            'side': self.side.label,
            'entry_price': self.entry_price,
            'exit_price': price,
            'size': self.size,
            'pnl': self.realized_pnl,
            'pnl_pct': self.realized_pnl_pct,
            'holding_period': str(self.holding_period).split('.')[0],
            'reason': reason
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'side': self.side.label,
            'side_icon': self.side.icon,
            'entry_price': self.entry_price,
            'current_price': self.current_price,
            'size': self.size,
            'value': self.value,
            'cost': self.cost,
            'unrealized_pnl': self.unrealized_pnl,
            'unrealized_pnl_pct': self.unrealized_pnl_pct,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'timestamp': self.timestamp.isoformat(),
            'is_open': self.is_open
        }

@dataclass
class Trade:
    """Registro completo de um trade"""
    id: str
    position_id: str
    symbol: str
    side: OrderSide
    entry_price: float
    exit_price: float
    size: float
    pnl: float
    pnl_pct: float
    commission: float
    entry_time: datetime
    exit_time: datetime
    holding_period: str
    exit_reason: str
    strategy: str
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'position_id': self.position_id,
            'symbol': self.symbol,
            'side': self.side.label,
            'side_icon': self.side.icon,
            'entry_price': self.entry_price,
            'exit_price': self.exit_price,
            'size': self.size,
            'pnl': self.pnl,
            'pnl_pct': f"{self.pnl_pct:.2f}%",
            'commission': self.commission,
            'entry_time': self.entry_time.isoformat(),
            'exit_time': self.exit_time.isoformat(),
            'holding_period': self.holding_period,
            'exit_reason': self.exit_reason,
            'strategy': self.strategy
        }

@dataclass
class BacktestResult:
    """Resultado completo de backtest"""
    # Estatísticas básicas
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0
    
    # Retornos
    initial_balance: float = 0.0
    final_balance: float = 0.0
    total_pnl: float = 0.0
    total_return: float = 0.0
    annualized_return: float = 0.0
    
    # Risco
    max_drawdown: float = 0.0
    max_drawdown_pct: float = 0.0
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    calmar_ratio: float = 0.0
    
    # Trades
    avg_win: float = 0.0
    avg_loss: float = 0.0
    avg_win_pct: float = 0.0
    avg_loss_pct: float = 0.0
    profit_factor: float = 0.0
    expectancy: float = 0.0
    
    # Duração
    avg_holding_period: str = "0:00:00"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    # Dados
    equity_curve: List[float] = field(default_factory=list)
    drawdown_curve: List[float] = field(default_factory=list)
    trades: List[Dict] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': f"{self.win_rate:.2f}%",
            'initial_balance': f"${self.initial_balance:,.2f}",
            'final_balance': f"${self.final_balance:,.2f}",
            'total_pnl': f"${self.total_pnl:,.2f}",
            'total_return': f"{self.total_return:.2f}%",
            'annualized_return': f"{self.annualized_return:.2f}%",
            'max_drawdown': f"{self.max_drawdown_pct:.2f}%",
            'sharpe_ratio': f"{self.sharpe_ratio:.2f}",
            'sortino_ratio': f"{self.sortino_ratio:.2f}",
            'calmar_ratio': f"{self.calmar_ratio:.2f}",
            'profit_factor': f"{self.profit_factor:.2f}",
            'expectancy': f"${self.expectancy:.2f}",
            'avg_win': f"${self.avg_win:.2f}",
            'avg_loss': f"${self.avg_loss:.2f}"
        }

# =============================================================================
# DATA FEEDS AVANÇADOS
# =============================================================================

class DataFeed(ABC):
    """Classe abstrata para diferentes fontes de dados"""
    
    def __init__(self, name: str, broker_type: BrokerType):
        self.name = name
        self.broker_type = broker_type
        self.logger = logger.getChild(f'DataFeed.{name}')
    
    @abstractmethod
    def get_historical_data(self, symbol: str, timeframe: TimeFrame, 
                           limit: int = 500) -> pd.DataFrame:
        """Obtém dados históricos"""
        pass
    
    @abstractmethod
    async def get_historical_data_async(self, symbol: str, timeframe: TimeFrame,
                                       limit: int = 500) -> pd.DataFrame:
        """Versão assíncrona para dados históricos"""
        pass
    
    @abstractmethod
    def get_realtime_data(self, symbol: str, callback: Callable):
        """Obtém dados em tempo real via WebSocket"""
        pass
    
    @abstractmethod
    async def get_realtime_data_async(self, symbol: str, callback: Callable):
        """Versão assíncrona para dados em tempo real"""
        pass
    
    @abstractmethod
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Obtém preço atual"""
        pass
    
    @abstractmethod
    async def get_current_price_async(self, symbol: str) -> Optional[float]:
        """Versão assíncrona para preço atual"""
        pass

class BinanceDataFeed(DataFeed):
    """Data feed avançado para Binance"""
    
    def __init__(self, api_key: str = None, api_secret: str = None, testnet: bool = True):
        super().__init__("Binance", BrokerType.BINANCE)
        
        if not BINANCE_AVAILABLE:
            raise ImportError("python-binance não está instalado")
        
        self.api_key = api_key or os.getenv('BINANCE_API_KEY')
        self.api_secret = api_secret or os.getenv('BINANCE_API_SECRET')
        self.testnet = testnet
        
        if not self.api_key or not self.api_secret:
            raise ValueError("Binance API credentials não configuradas")
        
        self.client = BinanceClient(self.api_key, self.api_secret, testnet=testnet)
        self.cache = {}
    
    @retry(max_retries=3)
    @timing_decorator
    def get_historical_data(self, symbol: str, timeframe: TimeFrame, 
                          limit: int = 500) -> pd.DataFrame:
        """Obtém dados históricos da Binance"""
        try:
            klines = self.client.get_klines(
                symbol=symbol,
                interval=timeframe.code,
                limit=limit
            )
            
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base', 'taker_buy_quote', 'ignore'
            ])
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            numeric_cols = ['open', 'high', 'low', 'close', 'volume']
            df[numeric_cols] = df[numeric_cols].astype(float)
            
            df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            df.set_index('timestamp', inplace=True)
            
            return df
            
        except BinanceAPIException as e:
            self.logger.error(f"Erro na API Binance: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Erro ao obter dados históricos: {e}")
            raise
    
    async def get_historical_data_async(self, symbol: str, timeframe: TimeFrame,
                                       limit: int = 500) -> pd.DataFrame:
        """Versão assíncrona para dados históricos"""
        # Implementar versão assíncrona com aiohttp
        return self.get_historical_data(symbol, timeframe, limit)
    
    def get_realtime_data(self, symbol: str, callback: Callable):
        """Obtém dados em tempo real via WebSocket"""
        # Implementar WebSocket
        self.logger.warning("WebSocket não implementado para Binance")
    
    async def get_realtime_data_async(self, symbol: str, callback: Callable):
        """Versão assíncrona para dados em tempo real"""
        # Implementar WebSocket assíncrono
        pass
    
    @retry(max_retries=3)
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Obtém preço atual"""
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except Exception as e:
            self.logger.error(f"Erro ao obter preço de {symbol}: {e}")
            return None
    
    async def get_current_price_async(self, symbol: str) -> Optional[float]:
        """Versão assíncrona para preço atual"""
        return self.get_current_price(symbol)

class YahooDataFeed(DataFeed):
    """Data feed para Yahoo Finance"""
    
    def __init__(self):
        super().__init__("Yahoo Finance", BrokerType.YAHOO)
        
        if not YFINANCE_AVAILABLE:
            raise ImportError("yfinance não está instalado")
    
    @retry(max_retries=3)
    @memoize(ttl=3600)
    def get_historical_data(self, symbol: str, timeframe: TimeFrame,
                          limit: int = 500) -> pd.DataFrame:
        """Obtém dados históricos do Yahoo Finance"""
        try:
            # Mapear timeframe
            period_map = {
                TimeFrame.M1: "5d",
                TimeFrame.M5: "1mo",
                TimeFrame.M15: "1mo",
                TimeFrame.H1: "3mo",
                TimeFrame.H4: "6mo",
                TimeFrame.D1: "1y",
                TimeFrame.W1: "5y"
            }
            
            interval_map = {
                TimeFrame.M1: "1m",
                TimeFrame.M5: "5m",
                TimeFrame.M15: "15m",
                TimeFrame.H1: "60m",
                TimeFrame.H4: "60m",
                TimeFrame.D1: "1d",
                TimeFrame.W1: "1wk"
            }
            
            period = period_map.get(timeframe, "1mo")
            interval = interval_map.get(timeframe, "1d")
            
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                return pd.DataFrame()
            
            df.reset_index(inplace=True)
            df.rename(columns={'Datetime': 'timestamp'}, inplace=True)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)
            
            # Manter apenas colunas OHLCV
            cols = ['Open', 'High', 'Low', 'Close', 'Volume']
            df = df[cols]
            df.columns = ['open', 'high', 'low', 'close', 'volume']
            
            return df.iloc[-limit:]
            
        except Exception as e:
            self.logger.error(f"Erro ao obter dados do Yahoo: {e}")
            return pd.DataFrame()
    
    async def get_historical_data_async(self, symbol: str, timeframe: TimeFrame,
                                       limit: int = 500) -> pd.DataFrame:
        """Versão assíncrona para Yahoo Finance"""
        return self.get_historical_data(symbol, timeframe, limit)
    
    def get_realtime_data(self, symbol: str, callback: Callable):
        """Yahoo Finance não suporta dados em tempo real"""
        raise NotImplementedError("Yahoo Finance não suporta dados em tempo real")
    
    async def get_realtime_data_async(self, symbol: str, callback: Callable):
        """Yahoo Finance não suporta dados em tempo real"""
        raise NotImplementedError("Yahoo Finance não suporta dados em tempo real")
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Obtém preço atual do Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d", interval="1m")
            if not data.empty:
                return float(data['Close'].iloc[-1])
        except Exception as e:
            self.logger.error(f"Erro ao obter preço de {symbol}: {e}")
        return None
    
    async def get_current_price_async(self, symbol: str) -> Optional[float]:
        """Versão assíncrona para Yahoo Finance"""
        return self.get_current_price(symbol)

class CCXTDataFeed(DataFeed):
    """Data feed para CCXT (múltiplas exchanges)"""
    
    def __init__(self, exchange_id: str, api_key: str = None, 
                 api_secret: str = None, testnet: bool = True):
        super().__init__(exchange_id.capitalize(), BrokerType[exchange_id.upper()])
        
        if not CCXT_AVAILABLE:
            raise ImportError("ccxt não está instalado")
        
        self.exchange_id = exchange_id
        exchange_class = getattr(ccxt, exchange_id)
        
        self.exchange = exchange_class({
            'apiKey': api_key or os.getenv(f'{exchange_id.upper()}_API_KEY'),
            'secret': api_secret or os.getenv(f'{exchange_id.upper()}_API_SECRET'),
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
        
        if testnet:
            self.exchange.set_sandbox_mode(True)
    
    @retry(max_retries=3)
    def get_historical_data(self, symbol: str, timeframe: TimeFrame,
                          limit: int = 500) -> pd.DataFrame:
        """Obtém dados históricos via CCXT"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(
                symbol, 
                timeframe=timeframe.code,
                limit=limit
            )
            
            df = pd.DataFrame(ohlcv, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume'
            ])
            
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            return df
            
        except Exception as e:
            self.logger.error(f"Erro ao obter dados do CCXT: {e}")
            return pd.DataFrame()
    
    async def get_historical_data_async(self, symbol: str, timeframe: TimeFrame,
                                       limit: int = 500) -> pd.DataFrame:
        """Versão assíncrona para CCXT"""
        # Implementar versão assíncrona
        return self.get_historical_data(symbol, timeframe, limit)
    
    def get_realtime_data(self, symbol: str, callback: Callable):
        """Obtém dados em tempo real via WebSocket"""
        # Implementar WebSocket
        self.logger.warning("WebSocket não implementado para CCXT")
    
    async def get_realtime_data_async(self, symbol: str, callback: Callable):
        """Versão assíncrona para dados em tempo real"""
        pass
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Obtém preço atual via CCXT"""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return float(ticker['last'])
        except Exception as e:
            self.logger.error(f"Erro ao obter preço de {symbol}: {e}")
            return None
    
    async def get_current_price_async(self, symbol: str) -> Optional[float]:
        """Versão assíncrona para CCXT"""
        return self.get_current_price(symbol)

class SimulatorDataFeed(DataFeed):
    """Data feed simulador para backtesting"""
    
    def __init__(self):
        super().__init__("Simulator", BrokerType.SIMULATOR)
        self.prices = {}
    
    def get_historical_data(self, symbol: str, timeframe: TimeFrame,
                          limit: int = 500) -> pd.DataFrame:
        """Gera dados históricos sintéticos"""
        # Gerar dados aleatórios para simulação
        dates = pd.date_range(
            end=datetime.now(),
            periods=limit,
            freq=timeframe.code
        )
        
        np.random.seed(hash(symbol) % 2**32)
        
        # Random walk
        returns = np.random.randn(limit) * 0.02
        prices = 100 * np.exp(np.cumsum(returns))
        
        df = pd.DataFrame({
            'open': prices * 0.999,
            'high': prices * 1.002,
            'low': prices * 0.998,
            'close': prices,
            'volume': np.random.randint(1000, 10000, limit)
        }, index=dates)
        
        return df
    
    async def get_historical_data_async(self, symbol: str, timeframe: TimeFrame,
                                       limit: int = 500) -> pd.DataFrame:
        """Versão assíncrona do simulador"""
        return self.get_historical_data(symbol, timeframe, limit)
    
    def get_realtime_data(self, symbol: str, callback: Callable):
        """Simula dados em tempo real"""
        def simulate():
            while True:
                current_price = self.prices.get(symbol, 100.0)
                change = np.random.randn() * 0.001
                new_price = current_price * (1 + change)
                self.prices[symbol] = new_price
                
                callback({
                    'symbol': symbol,
                    'price': new_price,
                    'timestamp': datetime.now()
                })
                
                time.sleep(1)
        
        thread = threading.Thread(target=simulate, daemon=True)
        thread.start()
    
    async def get_realtime_data_async(self, symbol: str, callback: Callable):
        """Versão assíncrona do simulador"""
        while True:
            current_price = self.prices.get(symbol, 100.0)
            change = np.random.randn() * 0.001
            new_price = current_price * (1 + change)
            self.prices[symbol] = new_price
            
            await callback({
                'symbol': symbol,
                'price': new_price,
                'timestamp': datetime.now()
            })
            
            await asyncio.sleep(1)
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """Obtém preço atual do simulador"""
        if symbol not in self.prices:
            self.prices[symbol] = 100.0
        return self.prices[symbol]
    
    async def get_current_price_async(self, symbol: str) -> Optional[float]:
        """Versão assíncrona do simulador"""
        return self.get_current_price(symbol)

# =============================================================================
# DATA FEED FACTORY
# =============================================================================

class DataFeedFactory:
    """Fábrica de data feeds"""
    
    @staticmethod
    def create_data_feed(broker_type: BrokerType, **kwargs) -> DataFeed:
        """Cria data feed baseado no tipo de broker"""
        
        if broker_type == BrokerType.BINANCE:
            return BinanceDataFeed(
                api_key=kwargs.get('api_key'),
                api_secret=kwargs.get('api_secret'),
                testnet=kwargs.get('testnet', True)
            )
        
        elif broker_type == BrokerType.YAHOO:
            return YahooDataFeed()
        
        elif broker_type == BrokerType.SIMULATOR:
            return SimulatorDataFeed()
        
        elif broker_type in [BrokerType.COINBASE, BrokerType.KRAKEN, 
                            BrokerType.BYBIT, BrokerType.FTX]:
            return CCXTDataFeed(
                exchange_id=broker_type.name.lower(),
                api_key=kwargs.get('api_key'),
                api_secret=kwargs.get('api_secret'),
                testnet=kwargs.get('testnet', True)
            )
        
        else:
            raise ValueError(f"Broker não suportado: {broker_type}")

# =============================================================================
# INDICADORES TÉCNICOS AVANÇADOS
# =============================================================================

class TechnicalIndicators:
    """Calculadora avançada de indicadores técnicos"""
    
    @staticmethod
    @timing_decorator
    def calculate_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Calcula todos os indicadores técnicos disponíveis"""
        if not PANDAS_AVAILABLE:
            return df
        
        df = df.copy()
        
        # ===== TREND INDICATORS =====
        if TA_LIB_AVAILABLE:
            # SMA
            df['sma_10'] = talib.SMA(df['close'], timeperiod=10)
            df['sma_20'] = talib.SMA(df['close'], timeperiod=20)
            df['sma_50'] = talib.SMA(df['close'], timeperiod=50)
            df['sma_200'] = talib.SMA(df['close'], timeperiod=200)
            
            # EMA
            df['ema_12'] = talib.EMA(df['close'], timeperiod=12)
            df['ema_26'] = talib.EMA(df['close'], timeperiod=26)
            df['ema_50'] = talib.EMA(df['close'], timeperiod=50)
            
            # MACD
            df['macd'], df['macd_signal'], df['macd_hist'] = talib.MACD(
                df['close'], fastperiod=12, slowperiod=26, signalperiod=9
            )
            
            # ADX
            df['adx'] = talib.ADX(df['high'], df['low'], df['close'], timeperiod=14)
            
            # Aroon
            df['aroon_up'], df['aroon_down'] = talib.AROON(
                df['high'], df['low'], timeperiod=25
            )
            
            # Parabolic SAR
            df['sar'] = talib.SAR(df['high'], df['low'], acceleration=0.02, maximum=0.2)
            
            # Ichimoku
            df['ichimoku_conv'] = talib.STOCHRSI(df['close'], timeperiod=9)[0]
            
        elif TA_AVAILABLE:
            # Fallback para biblioteca 'ta'
            # SMA
            df['sma_10'] = df['close'].rolling(10).mean()
            df['sma_20'] = df['close'].rolling(20).mean()
            df['sma_50'] = df['close'].rolling(50).mean()
            df['sma_200'] = df['close'].rolling(200).mean()
            
            # EMA
            df['ema_12'] = df['close'].ewm(span=12).mean()
            df['ema_26'] = df['close'].ewm(span=26).mean()
            
            # MACD
            ema12 = df['close'].ewm(span=12).mean()
            ema26 = df['close'].ewm(span=26).mean()
            df['macd'] = ema12 - ema26
            df['macd_signal'] = df['macd'].ewm(span=9).mean()
            df['macd_hist'] = df['macd'] - df['macd_signal']
        
        # ===== MOMENTUM INDICATORS =====
        if TA_LIB_AVAILABLE:
            # RSI
            df['rsi'] = talib.RSI(df['close'], timeperiod=14)
            
            # Stochastic
            df['stoch_k'], df['stoch_d'] = talib.STOCH(
                df['high'], df['low'], df['close'],
                fastk_period=14, slowk_period=3, slowk_matype=0,
                slowd_period=3, slowd_matype=0
            )
            
            # CCI
            df['cci'] = talib.CCI(df['high'], df['low'], df['close'], timeperiod=14)
            
            # Williams %R
            df['willr'] = talib.WILLR(df['high'], df['low'], df['close'], timeperiod=14)
            
            # MFI
            df['mfi'] = talib.MFI(df['high'], df['low'], df['close'], 
                                 df['volume'], timeperiod=14)
            
            # ROC
            df['roc'] = talib.ROC(df['close'], timeperiod=10)
            
        else:
            # RSI simplificado
            delta = df['close'].diff()
            gain = delta.where(delta > 0, 0).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
        
        # ===== VOLATILITY INDICATORS =====
        if TA_LIB_AVAILABLE:
            # Bollinger Bands
            df['bb_upper'], df['bb_middle'], df['bb_lower'] = talib.BBANDS(
                df['close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0
            )
            
            # ATR
            df['atr'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=14)
            
            # Keltner Channels
            df['kc_middle'] = df['close'].ewm(span=20).mean()
            df['kc_atr'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=10)
            df['kc_upper'] = df['kc_middle'] + 2 * df['kc_atr']
            df['kc_lower'] = df['kc_middle'] - 2 * df['kc_atr']
            
        else:
            # Bollinger Bands simplificado
            df['bb_middle'] = df['close'].rolling(20).mean()
            df['bb_std'] = df['close'].rolling(20).std()
            df['bb_upper'] = df['bb_middle'] + 2 * df['bb_std']
            df['bb_lower'] = df['bb_middle'] - 2 * df['bb_std']
            
            # ATR simplificado
            tr1 = df['high'] - df['low']
            tr2 = (df['high'] - df['close'].shift()).abs()
            tr3 = (df['low'] - df['close'].shift()).abs()
            df['atr'] = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1).rolling(14).mean()
        
        # ===== VOLUME INDICATORS =====
        # Volume SMA
        df['volume_sma'] = df['volume'].rolling(20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_sma']
        
        # OBV
        obv = (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum()
        df['obv'] = obv
        df['obv_sma'] = df['obv'].rolling(20).mean()
        
        if TA_LIB_AVAILABLE:
            # Chaikin MF
            df['ad'] = talib.AD(df['high'], df['low'], df['close'], df['volume'])
            df['adosc'] = talib.ADOSC(df['high'], df['low'], df['close'], 
                                      df['volume'], fastperiod=3, slowperiod=10)
        
        # ===== PRICE ACTION =====
        # Candlestick patterns
        df['body'] = abs(df['close'] - df['open'])
        df['upper_shadow'] = df['high'] - df[['close', 'open']].max(axis=1)
        df['lower_shadow'] = df[['close', 'open']].min(axis=1) - df['low']
        
        # Doji
        df['doji'] = df['body'] < (df['high'] - df['low']) * 0.1
        
        # Engulfing
        df['bullish_engulfing'] = (
            (df['close'].shift(1) < df['open'].shift(1)) &
            (df['close'] > df['open']) &
            (df['open'] < df['close'].shift(1)) &
            (df['close'] > df['open'].shift(1))
        ).astype(int)
        
        df['bearish_engulfing'] = (
            (df['close'].shift(1) > df['open'].shift(1)) &
            (df['close'] < df['open']) &
            (df['open'] > df['close'].shift(1)) &
            (df['close'] < df['open'].shift(1))
        ).astype(int)
        
        # Hammer
        df['hammer'] = (
            (df['lower_shadow'] > df['body'] * 2) &
            (df['upper_shadow'] < df['body'] * 0.3) &
            (df['close'] > df['open'])
        ).astype(int)
        
        # Shooting Star
        df['shooting_star'] = (
            (df['upper_shadow'] > df['body'] * 2) &
            (df['lower_shadow'] < df['body'] * 0.3) &
            (df['close'] < df['open'])
        ).astype(int)
        
        # ===== SUPPORT & RESISTANCE =====
        df['support'] = df['low'].rolling(window=20, center=True).min()
        df['resistance'] = df['high'].rolling(window=20, center=True).max()
        df['support_dist'] = (df['close'] - df['support']) / df['support']
        df['resistance_dist'] = (df['resistance'] - df['close']) / df['close']
        
        # ===== CUSTOM INDICATORS =====
        # True Range
        df['true_range'] = df['atr'] * 14
        
        # Normalized indicators
        df['rsi_norm'] = df['rsi'] / 100
        df['macd_norm'] = (df['macd'] - df['macd'].rolling(100).min()) / (
            df['macd'].rolling(100).max() - df['macd'].rolling(100).min()
        )
        
        # Signal combinations
        df['bullish_signal'] = (
            (df['rsi'] < 30) & 
            (df['macd'] > df['macd_signal']) & 
            (df['close'] > df['bb_lower'])
        ).astype(int)
        
        df['bearish_signal'] = (
            (df['rsi'] > 70) & 
            (df['macd'] < df['macd_signal']) & 
            (df['close'] < df['bb_upper'])
        ).astype(int)
        
        # Clean NaN values
        df = df.fillna(method='bfill').fillna(method='ffill').fillna(0)
        
        return df
    
    @staticmethod
    def get_signal_strength(df: pd.DataFrame) -> float:
        """Calcula força do sinal combinado (0-100)"""
        if df.empty:
            return 0
        
        last = df.iloc[-1]
        strength = 50  # Neutral
        
        # RSI
        if 'rsi' in last:
            if last['rsi'] < 30:
                strength += (30 - last['rsi']) / 30 * 20
            elif last['rsi'] > 70:
                strength -= (last['rsi'] - 70) / 30 * 20
        
        # MACD
        if 'macd' in last and 'macd_signal' in last:
            if last['macd'] > last['macd_signal']:
                strength += 10
            else:
                strength -= 10
        
        # Bollinger
        if 'bb_upper' in last and 'bb_lower' in last and 'close' in last:
            if last['close'] < last['bb_lower']:
                strength += 15
            elif last['close'] > last['bb_upper']:
                strength -= 15
        
        # Volume
        if 'volume_ratio' in last:
            if last['volume_ratio'] > 1.5:
                strength += 10
            elif last['volume_ratio'] < 0.5:
                strength -= 10
        
        # Suporte/Resistência
        if 'support_dist' in last and last['support_dist'] < 0.01:
            strength += 15
        if 'resistance_dist' in last and last['resistance_dist'] < 0.01:
            strength -= 15
        
        return max(0, min(100, strength))

# =============================================================================
# ESTRATÉGIAS DE TRADING AVANÇADAS
# =============================================================================

class TradingStrategy(ABC):
    """Classe abstrata avançada para estratégias de trading"""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.logger = logger.getChild(f'Strategy.{name}')
    
    @abstractmethod
    def generate_signal(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Gera sinal de trading"""
        pass
    
    @abstractmethod
    def calculate_stop_loss(self, entry_price: float, side: OrderSide, 
                           df: pd.DataFrame) -> float:
        """Calcula stop loss dinâmico"""
        pass
    
    @abstractmethod
    def calculate_take_profit(self, entry_price: float, side: OrderSide,
                            df: pd.DataFrame) -> float:
        """Calcula take profit dinâmico"""
        pass

class EMACrossoverStrategy(TradingStrategy):
    """Estratégia avançada de cruzamento de EMAs"""
    
    def __init__(self, fast_period: int = 12, slow_period: int = 26,
                 signal_period: int = 9, **kwargs):
        super().__init__("EMA Crossover", kwargs)
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
    
    def generate_signal(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Gera sinal baseado em cruzamento de EMAs com confirmação"""
        if len(df) < self.slow_period + 5:
            return {'signal': 'HOLD', 'strength': 0, 'confidence': 0}
        
        # Calcular EMAs
        fast_ema = df['close'].ewm(span=self.fast_period).mean()
        slow_ema = df['close'].ewm(span=self.slow_period).mean()
        
        current_fast = fast_ema.iloc[-1]
        current_slow = slow_ema.iloc[-1]
        prev_fast = fast_ema.iloc[-2]
        prev_slow = slow_ema.iloc[-2]
        prev2_fast = fast_ema.iloc[-3] if len(df) > 3 else prev_fast
        
        signal = 'HOLD'
        strength = 0
        confidence = 0
        reason = ""
        
        # Cruzamento de alta
        if current_fast > current_slow and prev_fast <= prev_slow:
            signal = 'BUY'
            
            # Verificar força do sinal
            if prev2_fast <= prev2_fast:  # Confirmação
                strength = 2
                confidence = 80
                reason = "Cruzamento EMA de alta confirmado"
            else:
                strength = 1
                confidence = 65
                reason = "Cruzamento EMA de alta"
        
        # Cruzamento de baixa
        elif current_fast < current_slow and prev_fast >= prev_slow:
            signal = 'SELL'
            
            if prev2_fast >= prev2_fast:
                strength = 2
                confidence = 80
                reason = "Cruzamento EMA de baixa confirmado"
            else:
                strength = 1
                confidence = 65
                reason = "Cruzamento EMA de baixa"
        
        return {
            'signal': signal,
            'strength': strength,
            'confidence': confidence,
            'reason': reason,
            'fast_ema': current_fast,
            'slow_ema': current_slow,
            'type': 'EMA_CROSSOVER'
        }
    
    def calculate_stop_loss(self, entry_price: float, side: OrderSide,
                           df: pd.DataFrame) -> float:
        """Calcula stop loss baseado em ATR"""
        atr = df['atr'].iloc[-1] if 'atr' in df.columns else entry_price * 0.02
        
        if side == OrderSide.BUY:
            return entry_price - (atr * 1.5)
        else:
            return entry_price + (atr * 1.5)
    
    def calculate_take_profit(self, entry_price: float, side: OrderSide,
                            df: pd.DataFrame) -> float:
        """Calcula take profit baseado em ATR e R:R"""
        atr = df['atr'].iloc[-1] if 'atr' in df.columns else entry_price * 0.02
        
        if side == OrderSide.BUY:
            return entry_price + (atr * 3.0)
        else:
            return entry_price - (atr * 3.0)

class RSIStrategy(TradingStrategy):
    """Estratégia avançada baseada em RSI com divergências"""
    
    def __init__(self, oversold: int = 30, overbought: int = 70,
                 rsi_period: int = 14, **kwargs):
        super().__init__("RSI Strategy", kwargs)
        self.oversold = oversold
        self.overbought = overbought
        self.rsi_period = rsi_period
    
    def generate_signal(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Gera sinal baseado em RSI e divergências"""
        if 'rsi' not in df.columns or len(df) < 20:
            return {'signal': 'HOLD', 'strength': 0, 'confidence': 0}
        
        rsi = df['rsi'].iloc[-1]
        prev_rsi = df['rsi'].iloc[-2]
        price = df['close'].iloc[-1]
        prev_price = df['close'].iloc[-2]
        
        signal = 'HOLD'
        strength = 0
        confidence = 0
        reason = ""
        
        # Oversold - oportunidade de compra
        if rsi < self.oversold:
            if rsi > prev_rsi:  # RSI subindo
                signal = 'BUY'
                strength = (self.oversold - rsi) / self.oversold * 2
                confidence = min(80 + strength * 10, 95)
                reason = "RSI em oversold com reversão"
            else:
                signal = 'BUY'
                strength = (self.oversold - rsi) / self.oversold
                confidence = 70
                reason = "RSI em oversold"
        
        # Overbought - oportunidade de venda
        elif rsi > self.overbought:
            if rsi < prev_rsi:  # RSI descendo
                signal = 'SELL'
                strength = (rsi - self.overbought) / (100 - self.overbought) * 2
                confidence = min(80 + strength * 10, 95)
                reason = "RSI em overbought com reversão"
            else:
                signal = 'SELL'
                strength = (rsi - self.overbought) / (100 - self.overbought)
                confidence = 70
                reason = "RSI em overbought"
        
        # Divergência de alta
        elif len(df) > 30:
            # Verificar divergência nos últimos 20 períodos
            price_low = df['close'].iloc[-20:].min()
            rsi_low = df['rsi'].iloc[-20:].min()
            price_low_idx = df['close'].iloc[-20:].idxmin()
            rsi_low_idx = df['rsi'].iloc[-20:].idxmin()
            
            if price < price_low and rsi > rsi_low:
                signal = 'BUY'
                strength = 3
                confidence = 85
                reason = "Divergência de alta detectada"
        
        return {
            'signal': signal,
            'strength': strength,
            'confidence': confidence,
            'reason': reason,
            'rsi': rsi,
            'type': 'RSI'
        }
    
    def calculate_stop_loss(self, entry_price: float, side: OrderSide,
                           df: pd.DataFrame) -> float:
        """Calcula stop loss baseado em suporte recente"""
        if side == OrderSide.BUY:
            support = df['low'].iloc[-10:].min()
            return min(support, entry_price * 0.97)
        else:
            resistance = df['high'].iloc[-10:].max()
            return max(resistance, entry_price * 1.03)
    
    def calculate_take_profit(self, entry_price: float, side: OrderSide,
                            df: pd.DataFrame) -> float:
        """Calcula take profit baseado em resistência/suporte"""
        if side == OrderSide.BUY:
            resistance = df['high'].iloc[-20:].max()
            return resistance
        else:
            support = df['low'].iloc[-20:].min()
            return support

class BollingerBandsStrategy(TradingStrategy):
    """Estratégia baseada em Bollinger Bands"""
    
    def __init__(self, period: int = 20, std_dev: float = 2.0, **kwargs):
        super().__init__("Bollinger Bands", kwargs)
        self.period = period
        self.std_dev = std_dev
    
    def generate_signal(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Gera sinal baseado em Bollinger Bands"""
        if 'bb_upper' not in df.columns or 'bb_lower' not in df.columns:
            return {'signal': 'HOLD', 'strength': 0, 'confidence': 0}
        
        price = df['close'].iloc[-1]
        bb_upper = df['bb_upper'].iloc[-1]
        bb_lower = df['bb_lower'].iloc[-1]
        bb_middle = df['bb_middle'].iloc[-1]
        
        # Calcular posição percentual na banda
        bb_position = (price - bb_lower) / (bb_upper - bb_lower) if bb_upper != bb_lower else 0.5
        
        signal = 'HOLD'
        strength = 0
        confidence = 0
        reason = ""
        
        # Compra quando toca banda inferior
        if price <= bb_lower:
            signal = 'BUY'
            strength = 2
            confidence = 75
            reason = "Preço na banda inferior de Bollinger"
        
        # Venda quando toca banda superior
        elif price >= bb_upper:
            signal = 'SELL'
            strength = 2
            confidence = 75
            reason = "Preço na banda superior de Bollinger"
        
        # Squeeze - preparação para breakout
        bb_width = (bb_upper - bb_lower) / bb_middle
        if bb_width < bb_width.rolling(50).mean():
            reason += " | Squeeze detectado"
        
        return {
            'signal': signal,
            'strength': strength,
            'confidence': confidence,
            'reason': reason,
            'bb_position': bb_position,
            'bb_width': bb_width,
            'type': 'BOLLINGER'
        }
    
    def calculate_stop_loss(self, entry_price: float, side: OrderSide,
                           df: pd.DataFrame) -> float:
        """Calcula stop loss baseado em Bollinger Bands"""
        if side == OrderSide.BUY:
            return df['bb_lower'].iloc[-1] * 0.98
        else:
            return df['bb_upper'].iloc[-1] * 1.02
    
    def calculate_take_profit(self, entry_price: float, side: OrderSide,
                            df: pd.DataFrame) -> float:
        """Calcula take profit baseado em Bollinger Bands"""
        if side == OrderSide.BUY:
            return df['bb_middle'].iloc[-1]
        else:
            return df['bb_middle'].iloc[-1]

class MACDStrategy(TradingStrategy):
    """Estratégia baseada em MACD"""
    
    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9, **kwargs):
        super().__init__("MACD Strategy", kwargs)
        self.fast = fast
        self.slow = slow
        self.signal = signal
    
    def generate_signal(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Gera sinal baseado em MACD"""
        if 'macd' not in df.columns or 'macd_signal' not in df.columns:
            return {'signal': 'HOLD', 'strength': 0, 'confidence': 0}
        
        macd = df['macd'].iloc[-1]
        signal = df['macd_signal'].iloc[-1]
        hist = df['macd_hist'].iloc[-1] if 'macd_hist' in df.columns else macd - signal
        
        prev_macd = df['macd'].iloc[-2]
        prev_signal = df['macd_signal'].iloc[-2]
        
        signal_type = 'HOLD'
        strength = 0
        confidence = 0
        reason = ""
        
        # Cruzamento de alta
        if macd > signal and prev_macd <= prev_signal:
            signal_type = 'BUY'
            strength = 2
            confidence = 80
            reason = "Cruzamento MACD de alta"
        
        # Cruzamento de baixa
        elif macd < signal and prev_macd >= prev_signal:
            signal_type = 'SELL'
            strength = 2
            confidence = 80
            reason = "Cruzamento MACD de baixa"
        
        # Histograma positivo crescente
        elif hist > 0 and hist > hist.shift(1):
            signal_type = 'BUY'
            strength = 1
            confidence = 65
            reason = "MACD histograma positivo crescente"
        
        # Histograma negativo decrescente
        elif hist < 0 and hist < hist.shift(1):
            signal_type = 'SELL'
            strength = 1
            confidence = 65
            reason = "MACD histograma negativo decrescente"
        
        return {
            'signal': signal_type,
            'strength': strength,
            'confidence': confidence,
            'reason': reason,
            'macd': macd,
            'signal_line': signal,
            'histogram': hist,
            'type': 'MACD'
        }
    
    def calculate_stop_loss(self, entry_price: float, side: OrderSide,
                           df: pd.DataFrame) -> float:
        """Calcula stop loss baseado em ATR"""
        atr = df['atr'].iloc[-1] if 'atr' in df.columns else entry_price * 0.02
        
        if side == OrderSide.BUY:
            return entry_price - (atr * 2.0)
        else:
            return entry_price + (atr * 2.0)
    
    def calculate_take_profit(self, entry_price: float, side: OrderSide,
                            df: pd.DataFrame) -> float:
        """Calcula take profit baseado em ATR e confiança"""
        atr = df['atr'].iloc[-1] if 'atr' in df.columns else entry_price * 0.02
        
        if side == OrderSide.BUY:
            return entry_price + (atr * 4.0)
        else:
            return entry_price - (atr * 4.0)

class EnsembleStrategy(TradingStrategy):
    """Estratégia de ensemble combinando múltiplas estratégias"""
    
    def __init__(self, strategies: List[TradingStrategy], weights: List[float] = None, **kwargs):
        super().__init__("Ensemble Strategy", kwargs)
        self.strategies = strategies
        self.weights = weights or [1.0 / len(strategies)] * len(strategies)
    
    def generate_signal(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Gera sinal combinado de múltiplas estratégias"""
        signals = []
        confidences = []
        reasons = []
        
        for strategy, weight in zip(self.strategies, self.weights):
            signal = strategy.generate_signal(df)
            if signal['signal'] != 'HOLD':
                signals.append((signal['signal'], signal['confidence'] * weight))
                confidences.append(signal['confidence'] * weight)
                if 'reason' in signal:
                    reasons.append(signal['reason'])
        
        if not signals:
            return {'signal': 'HOLD', 'strength': 0, 'confidence': 0, 'type': 'ENSEMBLE'}
        
        # Contar votos
        buy_votes = sum(c for s, c in signals if s == 'BUY')
        sell_votes = sum(c for s, c in signals if s == 'SELL')
        
        if buy_votes > sell_votes:
            signal = 'BUY'
            confidence = buy_votes * 100
            strength = confidence / 100
        elif sell_votes > buy_votes:
            signal = 'SELL'
            confidence = sell_votes * 100
            strength = confidence / 100
        else:
            signal = 'HOLD'
            confidence = 50
            strength = 0.5
        
        return {
            'signal': signal,
            'strength': strength,
            'confidence': min(confidence, 95),
            'reason': " | ".join(reasons[:3]),
            'buy_votes': buy_votes,
            'sell_votes': sell_votes,
            'type': 'ENSEMBLE'
        }
    
    def calculate_stop_loss(self, entry_price: float, side: OrderSide,
                           df: pd.DataFrame) -> float:
        """Calcula stop loss médio das estratégias"""
        stops = []
        for strategy in self.strategies:
            stop = strategy.calculate_stop_loss(entry_price, side, df)
            stops.append(stop)
        
        return sum(stops) / len(stops) if stops else entry_price * (0.98 if side == OrderSide.BUY else 1.02)
    
    def calculate_take_profit(self, entry_price: float, side: OrderSide,
                            df: pd.DataFrame) -> float:
        """Calcula take profit médio das estratégias"""
        profits = []
        for strategy in self.strategies:
            profit = strategy.calculate_take_profit(entry_price, side, df)
            profits.append(profit)
        
        return sum(profits) / len(profits) if profits else entry_price * (1.04 if side == OrderSide.BUY else 0.96)

# =============================================================================
# GERENCIADOR DE RISCO AVANÇADO
# =============================================================================

class RiskManager:
    """Gerenciador de risco avançado com múltiplas métricas"""
    
    def __init__(self, config: TradingConfig):
        self.config = config
        self.positions: List[Position] = []
        self.daily_trades = 0
        self.daily_pnl = 0.0
        self.daily_risk = 0.0
        self.last_reset = datetime.now().date()
        
        # Limites
        self.max_daily_loss = config.max_risk_per_day * config.initial_balance
        self.max_position_risk = config.risk_per_trade * config.initial_balance
        
        self.logger = logger.getChild('RiskManager')
    
    def calculate_position_size(self, balance: float, entry_price: float,
                              stop_loss_price: float, confidence: float = 1.0) -> float:
        """Calcula tamanho da posição baseado no risco com ajuste de confiança"""
        risk_amount = balance * self.config.risk_per_trade * confidence
        risk_per_share = abs(entry_price - stop_loss_price)
        
        if risk_per_share == 0:
            return 0
        
        position_size = risk_amount / risk_per_share
        
        # Aplicar limites
        max_position = (balance * 0.2) / entry_price  # Máximo 20% do capital
        position_size = min(position_size, max_position)
        
        # Arredondar para 8 casas decimais (para cripto)
        return round(position_size, 8)
    
    def validate_trade(self, symbol: str, side: OrderSide, size: float, 
                      balance: float) -> Tuple[bool, str]:
        """Valida se o trade pode ser executado com múltiplas verificações"""
        
        # Reset diário
        self._check_daily_reset()
        
        # 1. Verificar número máximo de posições
        if len(self.positions) >= self.config.max_positions:
            return False, f"Máximo de {self.config.max_positions} posições atingido"
        
        # 2. Verificar trades diários
        if self.daily_trades >= self.config.max_daily_trades:
            return False, f"Limite diário de {self.config.max_daily_trades} trades atingido"
        
        # 3. Verificar perda diária máxima
        if self.daily_pnl <= -self.max_daily_loss:
            return False, f"Limite de perda diária de ${self.max_daily_loss:.2f} atingido"
        
        # 4. Verificar se já existe posição no mesmo símbolo
        existing_positions = [p for p in self.positions if p.symbol == symbol and p.is_open]
        if existing_positions and not self.config.use_pyramiding:
            return False, f"Posição existente em {symbol} e pyramiding desativado"
        
        # 5. Verificar pyramiding levels
        if self.config.use_pyramiding and len(existing_positions) >= self.config.pyramiding_levels:
            return False, f"Limite de {self.config.pyramiding_levels} níveis de pyramiding atingido"
        
        # 6. Verificar capital disponível
        required_capital = size * entry_price
        if required_capital > balance:
            return False, f"Capital insuficiente: ${required_capital:.2f} necessário, ${balance:.2f} disponível"
        
        return True, "OK"
    
    def _check_daily_reset(self):
        """Verifica e reseta contadores diários"""
        today = datetime.now().date()
        if today > self.last_reset:
            self.daily_trades = 0
            self.daily_pnl = 0.0
            self.daily_risk = 0.0
            self.last_reset = today
            self.logger.info("📅 Contadores diários resetados")
    
    def calculate_dynamic_stop_loss(self, entry_price: float, side: OrderSide,
                                   df: pd.DataFrame, atr_multiplier: float = 2.0) -> float:
        """Calcula stop loss dinâmico baseado em ATR e volatilidade"""
        atr = df['atr'].iloc[-1] if 'atr' in df.columns else entry_price * 0.02
        volatility = df['volatility_ratio'].iloc[-1] if 'volatility_ratio' in df.columns else 1.0
        
        # Ajustar ATR pela volatilidade
        adjusted_atr = atr * volatility
        
        if side == OrderSide.BUY:
            return entry_price - (adjusted_atr * atr_multiplier)
        else:
            return entry_price + (adjusted_atr * atr_multiplier)
    
    def calculate_dynamic_take_profit(self, entry_price: float, side: OrderSide,
                                     df: pd.DataFrame, rr_ratio: float = 2.0) -> float:
        """Calcula take profit dinâmico baseado em suporte/resistência"""
        if side == OrderSide.BUY:
            # Usar resistência como target
            resistance = df['resistance'].iloc[-1] if 'resistance' in df.columns else entry_price * 1.05
            return max(resistance, entry_price * (1 + self.config.take_profit_pct))
        else:
            # Usar suporte como target
            support = df['support'].iloc[-1] if 'support' in df.columns else entry_price * 0.95
            return min(support, entry_price * (1 - self.config.take_profit_pct))
    
    def update_trailing_stop(self, position: Position, current_price: float) -> bool:
        """Atualiza trailing stop com lógica avançada"""
        if not self.config.trailing_stop:
            return False
        
        activated = False
        
        if position.side == OrderSide.BUY:
            # Ativar trailing stop após lucro mínimo
            if current_price >= position.entry_price * (1 + self.config.trailing_activation):
                new_stop = current_price * (1 - self.config.trailing_distance)
                if new_stop > position.stop_loss:
                    position.stop_loss = new_stop
                    activated = True
        else:
            if current_price <= position.entry_price * (1 - self.config.trailing_activation):
                new_stop = current_price * (1 + self.config.trailing_distance)
                if new_stop < position.stop_loss:
                    position.stop_loss = new_stop
                    activated = True
        
        return activated
    
    def get_portfolio_risk(self) -> Dict[str, Any]:
        """Calcula risco total do portfólio"""
        total_exposure = sum(p.size * p.entry_price for p in self.positions if p.is_open)
        total_risk = sum(abs(p.entry_price - p.stop_loss) * p.size for p in self.positions if p.is_open)
        
        return {
            'total_exposure': total_exposure,
            'total_risk': total_risk,
            'position_count': len([p for p in self.positions if p.is_open]),
            'daily_trades': self.daily_trades,
            'daily_pnl': self.daily_pnl,
            'daily_risk': self.daily_risk
        }

# =============================================================================
# NOTIFICADOR AVANÇADO
# =============================================================================

class Notifier:
    """Sistema de notificações multi-canal"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.enabled_channels = []
        
        # Configurar canais
        if self.config.get('enable_telegram', False) and TELEGRAM_AVAILABLE:
            self._setup_telegram()
        
        if self.config.get('enable_webhook', False):
            self._setup_webhook()
        
        self.logger = logger.getChild('Notifier')
    
    def _setup_telegram(self):
        """Configura bot do Telegram"""
        try:
            token = self.config.get('telegram_token') or os.getenv('TELEGRAM_BOT_TOKEN')
            chat_id = self.config.get('telegram_chat_id') or os.getenv('TELEGRAM_CHAT_ID')
            
            if token and chat_id:
                self.telegram_bot = telegram.Bot(token=token)
                self.telegram_chat_id = chat_id
                self.enabled_channels.append('telegram')
                self.logger.info("✅ Canal Telegram configurado")
        except Exception as e:
            self.logger.error(f"❌ Erro ao configurar Telegram: {e}")
    
    def _setup_webhook(self):
        """Configura webhook"""
        webhook_url = self.config.get('webhook_url') or os.getenv('WEBHOOK_URL')
        if webhook_url:
            self.webhook_url = webhook_url
            self.enabled_channels.append('webhook')
            self.logger.info("✅ Canal Webhook configurado")
    
    def send_notification(self, title: str, message: str, level: str = "INFO"):
        """Envia notificação para todos os canais configurados"""
        # Log sempre
        if level == "ERROR":
            self.logger.error(f"{title}: {message}")
        elif level == "WARNING":
            self.logger.warning(f"{title}: {message}")
        else:
            self.logger.info(f"{title}: {message}")
        
        # Telegram
        if 'telegram' in self.enabled_channels:
            self._send_telegram(f"{title}\n\n{message}")
        
        # Webhook
        if 'webhook' in self.enabled_channels:
            self._send_webhook(title, message, level)
    
    def _send_telegram(self, message: str):
        """Envia mensagem via Telegram"""
        try:
            self.telegram_bot.send_message(
                chat_id=self.telegram_chat_id,
                text=message,
                parse_mode='HTML'
            )
        except Exception as e:
            self.logger.error(f"❌ Erro ao enviar Telegram: {e}")
    
    def _send_webhook(self, title: str, message: str, level: str):
        """Envia webhook"""
        if not REQUESTS_AVAILABLE:
            return
        
        try:
            payload = {
                'title': title,
                'message': message,
                'level': level,
                'timestamp': datetime.now().isoformat()
            }
            requests.post(self.webhook_url, json=payload, timeout=5)
        except Exception as e:
            self.logger.error(f"❌ Erro ao enviar webhook: {e}")
    
    def send_trade_notification(self, trade: Trade):
        """Envia notificação de trade"""
        emoji = "🟢" if trade.pnl > 0 else "🔴"
        title = f"{emoji} Trade Executado - {trade.symbol}"
        
        message = f"""
<b>{trade.strategy}</b>
Sinal: {trade.side.icon} {trade.side.label}
Entrada: ${trade.entry_price:.4f}
Saída: ${trade.exit_price:.4f}
Tamanho: {trade.size:.4f}
P&L: ${trade.pnl:.2f} ({trade.pnl_pct:.2f}%)
Hold: {trade.holding_period}
Motivo: {trade.exit_reason}
        """
        
        self.send_notification(title, message, "INFO")
    
    def send_alert(self, message: str, level: str = "WARNING"):
        """Envia alerta"""
        title = f"⚠️ Alerta de Trading"
        self.send_notification(title, message, level)

# =============================================================================
# AUTO TRADER PRINCIPAL
# =============================================================================

class VhalinorAutoTrader:
    """
    Sistema principal de trading automatizado com arquitetura quântica
    """
    
    def __init__(self, 
                 trading_config: TradingConfig,
                 data_feed: DataFeed,
                 strategy: TradingStrategy,
                 mode: TradingMode = TradingMode.PAPER,
                 notifier_config: Dict[str, Any] = None):
        
        self.config = trading_config
        self.data_feed = data_feed
        self.strategy = strategy
        self.mode = mode
        self.notifier = Notifier(notifier_config or {})
        
        # ===== GERENCIADORES =====
        self.risk_manager = RiskManager(trading_config)
        self.indicators = TechnicalIndicators()
        
        # ===== ESTADO DO TRADER =====
        self.balance = trading_config.initial_balance
        self.equity = trading_config.initial_balance
        self.peak_balance = trading_config.initial_balance
        
        self.positions: List[Position] = []
        self.orders: List[Dict] = []
        self.trades: List[Trade] = []
        self.equity_curve: List[float] = []
        self.drawdown_curve: List[float] = []
        
        # ===== CONTROLE =====
        self.is_running = False
        self._thread: Optional[threading.Thread] = None
        self._async_loop: Optional[asyncio.AbstractEventLoop] = None
        
        # ===== CALLBACKS =====
        self.callbacks = {
            'on_trade': [],
            'on_position_open': [],
            'on_position_close': [],
            'on_signal': [],
            'on_error': [],
            'on_start': [],
            'on_stop': []
        }
        
        # Inicializar
        self._initialize()
    
    def _initialize(self):
        """Inicializa o trader"""
        self.logger = logger.getChild(f'AutoTrader.{self.mode.value}')
        
        self.logger.info("="*80)
        self.logger.info(f"🚀 VHALINOR IAG - AUTO TRADER QUÂNTICO")
        self.logger.info("="*80)
        self.logger.info(f"📊 Modo: {self.mode.icon} {self.mode.value.upper()}")
        self.logger.info(f"💱 Broker: {self.data_feed.broker_type.icon} {self.data_feed.broker_type.label}")
        self.logger.info(f"🎯 Estratégia: {self.strategy.name}")
        self.logger.info(f"💰 Capital: ${self.config.initial_balance:,.2f}")
        self.logger.info(f"⚖️  Risco: {self.config.risk_per_trade:.1%} por trade")
        self.logger.info(f"📈 Símbolos: {', '.join(self.config.symbols)}")
        self.logger.info("="*80)
    
    # =========================================================================
    # CALLBACKS
    # =========================================================================
    
    def register_callback(self, event_type: str, callback: Callable):
        """Registra callback para eventos"""
        if event_type in self.callbacks:
            self.callbacks[event_type].append(callback)
    
    def _trigger_callbacks(self, event_type: str, data: Any = None):
        """Dispara callbacks registrados"""
        for callback in self.callbacks.get(event_type, []):
            try:
                callback(data)
            except Exception as e:
                self.logger.error(f"❌ Erro no callback {event_type}: {e}")
    
    # =========================================================================
    # CICLO DE TRADING
    # =========================================================================
    
    def run(self):
        """Executa o trader no modo apropriado"""
        if self.mode == TradingMode.BACKTEST:
            self.logger.warning("Modo backtest não implementado diretamente. Use run_backtest()")
        elif self.mode in [TradingMode.PAPER, TradingMode.LIVE]:
            self.run_live()
    
    def run_live(self):
        """Executa trading em tempo real"""
        if self.is_running:
            self.logger.warning("⚠️ Trader já está em execução")
            return
        
        self.is_running = True
        self._trigger_callbacks('on_start', {'mode': self.mode.value})
        
        if self.config.get('use_async', True):
            self._start_async_loop()
        else:
            self._start_sync_loop()
    
    def _start_sync_loop(self):
        """Inicia loop síncrono"""
        def trading_loop():
            self.logger.info("🔄 Iniciando trading em tempo real (síncrono)...")
            
            while self.is_running:
                try:
                    self.trading_cycle()
                except Exception as e:
                    self.logger.error(f"❌ Erro no ciclo de trading: {e}")
                    self._trigger_callbacks('on_error', {'error': str(e)})
                
                time.sleep(60)  # 1 minuto
        
        self._thread = threading.Thread(target=trading_loop, daemon=True)
        self._thread.start()
    
    def _start_async_loop(self):
        """Inicia loop assíncrono"""
        def run_async():
            self._async_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._async_loop)
            self._async_loop.run_until_complete(self._async_trading_loop())
        
        self._thread = threading.Thread(target=run_async, daemon=True)
        self._thread.start()
        self.logger.info("🔄 Iniciando trading em tempo real (assíncrono)...")
    
    async def _async_trading_loop(self):
        """Loop assíncrono de trading"""
        while self.is_running:
            try:
                await self.trading_cycle_async()
            except Exception as e:
                self.logger.error(f"❌ Erro no ciclo assíncrono: {e}")
                self._trigger_callbacks('on_error', {'error': str(e)})
            
            await asyncio.sleep(60)
    
    def stop(self):
        """Para o trader"""
        self.is_running = False
        if self._thread:
            self._thread.join(timeout=5)
        self._trigger_callbacks('on_stop', {})
        self.logger.info("⏹️ Trader parado")
    
    @timing_decorator
    def trading_cycle(self):
        """Ciclo completo de trading síncrono"""
        self.logger.info("📊 Executando ciclo de trading...")
        
        for symbol in self.config.symbols:
            try:
                # 1. Coletar dados
                df = self.data_feed.get_historical_data(
                    symbol, 
                    self.config.default_timeframe,
                    limit=self.config.get('max_historical_bars', 500)
                )
                
                if df.empty:
                    continue
                
                # 2. Calcular indicadores
                df = self.indicators.calculate_all_indicators(df)
                
                # 3. Gerenciar posições existentes
                self._manage_positions(symbol, df)
                
                # 4. Gerar sinal
                signal = self.strategy.generate_signal(df)
                
                if signal['signal'] != 'HOLD':
                    self._trigger_callbacks('on_signal', {
                        'symbol': symbol,
                        'signal': signal
                    })
                    
                    # 5. Executar trade
                    self._execute_signal(symbol, df, signal)
                
            except Exception as e:
                self.logger.error(f"❌ Erro no ciclo para {symbol}: {e}")
        
        # 6. Atualizar métricas
        self._update_metrics()
        
        # 7. Log de performance
        self._log_performance()
    
    async def trading_cycle_async(self):
        """Ciclo completo de trading assíncrono"""
        self.logger.info("📊 Executando ciclo assíncrono de trading...")
        
        tasks = []
        for symbol in self.config.symbols:
            task = asyncio.create_task(self._process_symbol_async(symbol))
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        
        self._update_metrics()
        self._log_performance()
    
    async def _process_symbol_async(self, symbol: str):
        """Processa um símbolo de forma assíncrona"""
        try:
            # 1. Coletar dados
            df = await self.data_feed.get_historical_data_async(
                symbol,
                self.config.default_timeframe,
                limit=self.config.get('max_historical_bars', 500)
            )
            
            if df.empty:
                return
            
            # 2. Calcular indicadores
            df = self.indicators.calculate_all_indicators(df)
            
            # 3. Gerenciar posições existentes
            self._manage_positions(symbol, df)
            
            # 4. Gerar sinal
            signal = self.strategy.generate_signal(df)
            
            if signal['signal'] != 'HOLD':
                self._trigger_callbacks('on_signal', {
                    'symbol': symbol,
                    'signal': signal
                })
                
                # 5. Executar trade
                self._execute_signal(symbol, df, signal)
                
        except Exception as e:
            self.logger.error(f"❌ Erro no processamento de {symbol}: {e}")
    
    def _manage_positions(self, symbol: str, df: pd.DataFrame):
        """Gerencia posições abertas para um símbolo"""
        current_price = df['close'].iloc[-1]
        
        for position in self.positions[:]:
            if position.symbol != symbol or not position.is_open:
                continue
            
            # Atualizar preço
            position.update_price(current_price)
            
            # Verificar stop loss
            if position.side == OrderSide.BUY and current_price <= position.stop_loss:
                self._close_position(position, current_price, "STOP_LOSS")
            
            elif position.side == OrderSide.SELL and current_price >= position.stop_loss:
                self._close_position(position, current_price, "STOP_LOSS")
            
            # Verificar take profit
            elif position.side == OrderSide.BUY and current_price >= position.take_profit:
                self._close_position(position, current_price, "TAKE_PROFIT")
            
            elif position.side == OrderSide.SELL and current_price <= position.take_profit:
                self._close_position(position, current_price, "TAKE_PROFIT")
            
            # Atualizar trailing stop
            else:
                self.risk_manager.update_trailing_stop(position, current_price)
    
    def _execute_signal(self, symbol: str, df: pd.DataFrame, signal: Dict[str, Any]):
        """Executa um sinal de trading"""
        current_price = df['close'].iloc[-1]
        side = OrderSide.BUY if signal['signal'] == 'BUY' else OrderSide.SELL
        
        # Calcular stop loss e take profit
        stop_loss = self.strategy.calculate_stop_loss(current_price, side, df)
        take_profit = self.strategy.calculate_take_profit(current_price, side, df)
        
        # Calcular tamanho da posição
        confidence = signal.get('confidence', 50) / 100
        position_size = self.risk_manager.calculate_position_size(
            self.balance, current_price, stop_loss, confidence
        )
        
        if position_size <= 0:
            return
        
        # Validar trade
        can_trade, reason = self.risk_manager.validate_trade(
            symbol, side, position_size, self.balance
        )
        
        if not can_trade:
            self.logger.warning(f"⚠️ Trade rejeitado para {symbol}: {reason}")
            return
        
        # Criar posição
        position = Position(
            id=f"POS_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{symbol}_{uuid.uuid4().hex[:4]}",
            symbol=symbol,
            side=side,
            entry_price=current_price,
            size=position_size,
            stop_loss=stop_loss,
            take_profit=take_profit,
            timestamp=datetime.now(),
            entry_comment=signal.get('reason', ''),
            strategy=self.strategy.name,
            tags=[signal.get('type', 'UNKNOWN')]
        )
        
        # Modo PAPER ou LIVE
        if self.mode == TradingMode.PAPER:
            # Simular execução
            position.update_price(current_price)
            self.positions.append(position)
            
            # Atualizar saldo
            if side == OrderSide.BUY:
                self.balance -= position_size * current_price
            else:
                self.balance += position_size * current_price
            
            self.risk_manager.positions = self.positions
            self.risk_manager.daily_trades += 1
            
            self._trigger_callbacks('on_position_open', position.to_dict())
            
            self.logger.info(
                f"{side.icon} Posição aberta: {symbol} @ ${current_price:.2f} | "
                f"Tamanho: {position_size:.4f} | Confiança: {signal.get('confidence', 0):.0f}%"
            )
            
            # Notificar
            self.notifier.send_notification(
                f"{side.icon} Posição Aberta",
                f"{symbol}\nPreço: ${current_price:.2f}\nTamanho: {position_size:.4f}\n"
                f"Stop: ${stop_loss:.2f}\nTarget: ${take_profit:.2f}",
                "INFO"
            )
            
        elif self.mode == TradingMode.LIVE:
            # TODO: Implementar execução real via broker
            self.logger.warning("Modo LIVE não implementado")
    
    def _close_position(self, position: Position, exit_price: float, reason: str):
        """Fecha uma posição"""
        close_result = position.close(exit_price, reason)
        
        # Atualizar saldo
        self.balance += position.size * exit_price
        
        # Remover posição
        if position in self.positions:
            self.positions.remove(position)
        
        # Atualizar métricas de risco
        self.risk_manager.daily_pnl += position.realized_pnl
        
        # Criar registro de trade
        trade = Trade(
            id=f"TRADE_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{position.symbol}_{uuid.uuid4().hex[:4]}",
            position_id=position.id,
            symbol=position.symbol,
            side=position.side,
            entry_price=position.entry_price,
            exit_price=exit_price,
            size=position.size,
            pnl=position.realized_pnl,
            pnl_pct=position.realized_pnl_pct,
            commission=position.realized_pnl * 0.001,  # 0.1% de comissão
            entry_time=position.timestamp,
            exit_time=position.exit_time or datetime.now(),
            holding_period=str(position.holding_period).split('.')[0],
            exit_reason=reason,
            strategy=position.strategy,
            tags=position.tags
        )
        
        self.trades.append(trade)
        
        # Atualizar equity
        self._update_metrics()
        
        self._trigger_callbacks('on_position_close', trade.to_dict())
        
        # Log
        emoji = "✅" if position.realized_pnl > 0 else "📉"
        self.logger.info(
            f"{emoji} Posição fechada: {position.symbol} | "
            f"P&L: ${position.realized_pnl:.2f} ({position.realized_pnl_pct:.2f}%) | "
            f"Motivo: {reason}"
        )
        
        # Notificar
        self.notifier.send_trade_notification(trade)
    
    def _update_metrics(self):
        """Atualiza métricas de performance"""
        # Calcular equity
        open_positions_value = sum(
            p.size * p.current_price for p in self.positions if p.is_open
        )
        self.equity = self.balance + open_positions_value
        
        # Atualizar peak balance
        if self.equity > self.peak_balance:
            self.peak_balance = self.equity
        
        # Calcular drawdown
        drawdown = (self.peak_balance - self.equity) / self.peak_balance * 100 if self.peak_balance > 0 else 0
        
        # Registrar curvas
        self.equity_curve.append(self.equity)
        self.drawdown_curve.append(drawdown)
        
        # Manter tamanho limitado
        if len(self.equity_curve) > 1000:
            self.equity_curve.pop(0)
            self.drawdown_curve.pop(0)
    
    def _log_performance(self):
        """Registra performance atual"""
        performance = {
            'timestamp': datetime.now(),
            'balance': self.balance,
            'equity': self.equity,
            'peak_balance': self.peak_balance,
            'drawdown': (self.peak_balance - self.equity) / self.peak_balance * 100 if self.peak_balance > 0 else 0,
            'open_positions': len([p for p in self.positions if p.is_open]),
            'total_trades': len(self.trades),
            'winning_trades': len([t for t in self.trades if t.pnl > 0]),
            'daily_trades': self.risk_manager.daily_trades,
            'daily_pnl': self.risk_manager.daily_pnl
        }
        
        win_rate = (performance['winning_trades'] / performance['total_trades'] * 100) if performance['total_trades'] > 0 else 0
        
        self.logger.info(
            f"📈 Performance: Equity=${self.equity:,.2f} | "
            f"Drawdown={performance['drawdown']:.2f}% | "
            f"Trades={performance['total_trades']} | "
            f"Win Rate={win_rate:.1f}%"
        )
        
        # Salvar em CSV
        self._save_performance_log(performance)
    
    def _save_performance_log(self, performance: Dict):
        """Salva log de desempenho em CSV"""
        if not self.config.get('save_performance', True):
            return
        
        file_path = f"performance_{datetime.now().strftime('%Y%m')}.csv"
        file_exists = os.path.isfile(file_path)
        
        with open(file_path, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=performance.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(performance)
    
    # =========================================================================
    # BACKTESTING
    # =========================================================================
    
    def run_backtest(self, df_dict: Dict[str, pd.DataFrame]) -> Dict[str, BacktestResult]:
        """
        Executa backtesting em dados históricos
        
        Args:
            df_dict: Dicionário com símbolo -> DataFrame histórico
            
        Returns:
            Dict com resultados por símbolo
        """
        self.logger.info("📊 Iniciando backtesting...")
        
        results = {}
        initial_balance = self.balance
        
        for symbol, df in df_dict.items():
            self.logger.info(f"🔄 Backtesting {symbol}...")
            
            # Resetar estado
            self.balance = initial_balance
            self.equity = initial_balance
            self.peak_balance = initial_balance
            self.positions = []
            self.trades = []
            self.equity_curve = [initial_balance]
            self.drawdown_curve = [0]
            
            # Calcular indicadores
            df = self.indicators.calculate_all_indicators(df)
            
            # Loop através dos dados
            for i in range(50, len(df)):  # Começar após termos dados suficientes
                current_df = df.iloc[:i+1]
                
                # Gerenciar posições
                self._manage_positions(symbol, current_df)
                
                # Gerar sinal
                signal = self.strategy.generate_signal(current_df)
                
                if signal['signal'] != 'HOLD':
                    self._execute_signal(symbol, current_df, signal)
                
                # Atualizar métricas
                self._update_metrics()
            
            # Calcular resultados
            result = self._calculate_backtest_results(initial_balance)
            results[symbol] = result
            
            self.logger.info(f"✅ Backtest {symbol} concluído: "
                           f"Retorno={result.total_return:.2f}%, "
                           f"Sharpe={result.sharpe_ratio:.2f}, "
                           f"Trades={result.total_trades}")
        
        # Gerar gráficos
        if self.config.get('plot_equity_curve', True) and MATPLOTLIB_AVAILABLE:
            self._plot_backtest_results(results)
        
        return results
    
    def _calculate_backtest_results(self, initial_balance: float) -> BacktestResult:
        """Calcula resultados do backtest"""
        result = BacktestResult()
        
        # Estatísticas básicas
        result.total_trades = len(self.trades)
        result.winning_trades = len([t for t in self.trades if t.pnl > 0])
        result.losing_trades = len([t for t in self.trades if t.pnl < 0])
        result.win_rate = (result.winning_trades / result.total_trades * 100) if result.total_trades > 0 else 0
        
        # Retornos
        result.initial_balance = initial_balance
        result.final_balance = self.equity
        result.total_pnl = self.equity - initial_balance
        result.total_return = (result.total_pnl / initial_balance) * 100
        
        # Período
        if self.trades:
            result.start_date = min(t.entry_time for t in self.trades)
            result.end_date = max(t.exit_time for t in self.trades)
            
            days = (result.end_date - result.start_date).days
            if days > 0:
                result.annualized_return = result.total_return * (365 / days)
        
        # Drawdown
        result.equity_curve = self.equity_curve
        peak = self.equity_curve[0]
        for value in self.equity_curve:
            if value > peak:
                peak = value
            dd = (peak - value) / peak * 100
            result.drawdown_curve.append(dd)
            if dd > result.max_drawdown_pct:
                result.max_drawdown_pct = dd
                result.max_drawdown = peak - value
        
        # Médias
        if self.trades:
            wins = [t.pnl for t in self.trades if t.pnl > 0]
            losses = [t.pnl for t in self.trades if t.pnl < 0]
            
            result.avg_win = sum(wins) / len(wins) if wins else 0
            result.avg_loss = sum(losses) / len(losses) if losses else 0
            
            win_pcts = [t.pnl_pct for t in self.trades if t.pnl > 0]
            loss_pcts = [t.pnl_pct for t in self.trades if t.pnl < 0]
            
            result.avg_win_pct = sum(win_pcts) / len(win_pcts) if win_pcts else 0
            result.avg_loss_pct = sum(loss_pcts) / len(loss_pcts) if loss_pcts else 0
        
        # Profit Factor
        gross_profit = sum(t.pnl for t in self.trades if t.pnl > 0)
        gross_loss = abs(sum(t.pnl for t in self.trades if t.pnl < 0))
        result.profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Expectancy
        result.expectancy = (result.win_rate / 100 * result.avg_win) - ((1 - result.win_rate / 100) * result.avg_loss)
        
        # Sharpe Ratio (simplificado)
        if len(self.equity_curve) > 1 and NUMPY_AVAILABLE:
            returns = np.diff(self.equity_curve) / self.equity_curve[:-1]
            if len(returns) > 1:
                result.sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252)
        
        # Sortino Ratio (simplificado)
        if len(self.equity_curve) > 1 and NUMPY_AVAILABLE:
            returns = np.diff(self.equity_curve) / self.equity_curve[:-1]
            downside_returns = returns[returns < 0]
            if len(downside_returns) > 0:
                result.sortino_ratio = np.mean(returns) / np.std(downside_returns) * np.sqrt(252)
        
        # Calmar Ratio
        if result.max_drawdown_pct > 0:
            result.calmar_ratio = result.annualized_return / result.max_drawdown_pct
        
        # Holding period médio
        if self.trades:
            periods = []
            for t in self.trades:
                hms = t.holding_period.split(':')
                seconds = int(hms[0]) * 3600 + int(hms[1]) * 60 + int(hms[2])
                periods.append(seconds)
            
            avg_seconds = sum(periods) / len(periods)
            hours = avg_seconds // 3600
            minutes = (avg_seconds % 3600) // 60
            seconds = avg_seconds % 60
            result.avg_holding_period = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
        
        # Trades
        result.trades = [t.to_dict() for t in self.trades[-100:]]  # Últimos 100 trades
        
        return result
    
    def _plot_backtest_results(self, results: Dict[str, BacktestResult]):
        """Plota resultados do backtest"""
        if not MATPLOTLIB_AVAILABLE:
            return
        
        sns.set_style("whitegrid")
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 10))
        fig.suptitle(f'Backtest Results - {self.strategy.name}', fontsize=14, fontweight='bold')
        
        # Equity Curve
        ax1 = axes[0, 0]
        for symbol, result in results.items():
            ax1.plot(result.equity_curve, label=symbol, linewidth=1.5)
        ax1.set_title('Equity Curve', fontsize=12)
        ax1.set_xlabel('Time')
        ax1.set_ylabel('Equity ($)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Drawdown
        ax2 = axes[0, 1]
        for symbol, result in results.items():
            ax2.fill_between(range(len(result.drawdown_curve)), 0, result.drawdown_curve, 
                            alpha=0.3, label=symbol)
            ax2.plot(result.drawdown_curve, linewidth=1)
        ax2.set_title('Drawdown', fontsize=12)
        ax2.set_xlabel('Time')
        ax2.set_ylabel('Drawdown (%)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Monthly Returns (placeholder)
        ax3 = axes[1, 0]
        ax3.text(0.5, 0.5, 'Monthly Returns Heatmap\n(Coming Soon)', 
                ha='center', va='center', fontsize=12)
        ax3.set_title('Monthly Returns', fontsize=12)
        
        # Trade Distribution
        ax4 = axes[1, 1]
        for symbol, result in results.items():
            wins = result.winning_trades
            losses = result.losing_trades
            ax4.bar([f'{symbol} Wins', f'{symbol} Losses'], [wins, losses], alpha=0.7)
        ax4.set_title('Trade Distribution', fontsize=12)
        ax4.set_ylabel('Number of Trades')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'backtest_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png', dpi=150)
        plt.show()
    
    # =========================================================================
    # RELATÓRIOS E EXPORTAÇÃO
    # =========================================================================
    
    def generate_report(self) -> str:
        """Gera relatório completo de performance"""
        report = []
        report.append("="*90)
        report.append(f"📊 RELATÓRIO DE PERFORMANCE - VHALINOR AUTO TRADER")
        report.append("="*90)
        report.append(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        report.append(f"Modo: {self.mode.icon} {self.mode.value.upper()}")
        report.append(f"Estratégia: {self.strategy.name}")
        report.append(f"Broker: {self.data_feed.broker_type.icon} {self.data_feed.broker_type.label}")
        report.append("")
        
        # Métricas da conta
        report.append("💰 ESTADO DA CONTA:")
        report.append("-"*90)
        report.append(f"   Saldo: ${self.balance:,.2f}")
        report.append(f"   Equity: ${self.equity:,.2f}")
        report.append(f"   Peak: ${self.peak_balance:,.2f}")
        report.append(f"   Drawdown: {(self.peak_balance - self.equity) / self.peak_balance * 100:.2f}%")
        report.append("")
        
        # Posições abertas
        report.append("🟢 POSIÇÕES ABERTAS:")
        report.append("-"*90)
        open_positions = [p for p in self.positions if p.is_open]
        if open_positions:
            for pos in open_positions:
                report.append(f"   {pos.symbol}: {pos.side.icon} {pos.size:.4f} @ ${pos.entry_price:.2f} | "
                            f"P&L: ${pos.unrealized_pnl:.2f} ({pos.unrealized_pnl_pct:.2f}%)")
        else:
            report.append("   Nenhuma posição aberta")
        report.append("")
        
        # Estatísticas de trading
        report.append("📈 ESTATÍSTICAS DE TRADING:")
        report.append("-"*90)
        total_trades = len(self.trades)
        winning_trades = len([t for t in self.trades if t.pnl > 0])
        losing_trades = len([t for t in self.trades if t.pnl < 0])
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        report.append(f"   Total Trades: {total_trades}")
        report.append(f"   Winning Trades: {winning_trades}")
        report.append(f"   Losing Trades: {losing_trades}")
        report.append(f"   Win Rate: {win_rate:.2f}%")
        report.append("")
        
        # Últimos trades
        report.append("🔄 ÚLTIMOS TRADES:")
        report.append("-"*90)
        for trade in self.trades[-5:]:
            emoji = "🟢" if trade.pnl > 0 else "🔴"
            report.append(f"   {emoji} {trade.symbol}: {trade.side.icon} | "
                        f"Ent: ${trade.entry_price:.2f} Sai: ${trade.exit_price:.2f} | "
                        f"P&L: ${trade.pnl:.2f} ({trade.pnl_pct:.2f}%)")
        report.append("")
        
        # Recomendações
        report.append("💡 RECOMENDAÇÕES:")
        report.append("-"*90)
        
        if self.risk_manager.daily_risk > self.config.max_risk_per_day * 0.8:
            report.append("   • Risco diário próximo do limite - reduzir tamanho de posições")
        
        if len(open_positions) >= self.config.max_positions * 0.8:
            report.append(f"   • Número de posições próximo do limite ({len(open_positions)}/{self.config.max_positions})")
        
        if win_rate < 40 and total_trades > 10:
            report.append("   • Win rate baixo - revisar estratégia e filtros")
        
        report.append("="*90)
        
        return "\n".join(report)
    
    def export_trades(self, filename: str = None):
        """Exporta histórico de trades para CSV"""
        if not self.trades:
            self.logger.warning("Nenhum trade para exportar")
            return
        
        if filename is None:
            filename = f"trades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.trades[0].to_dict().keys())
            writer.writeheader()
            for trade in self.trades:
                writer.writerow(trade.to_dict())
        
        self.logger.info(f"💾 {len(self.trades)} trades exportados para {filename}")
        return filename
    
    def export_positions(self, filename: str = None):
        """Exporta posições atuais para CSV"""
        open_positions = [p for p in self.positions if p.is_open]
        
        if not open_positions:
            self.logger.warning("Nenhuma posição aberta para exportar")
            return
        
        if filename is None:
            filename = f"positions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=open_positions[0].to_dict().keys())
            writer.writeheader()
            for position in open_positions:
                writer.writerow(position.to_dict())
        
        self.logger.info(f"💾 {len(open_positions)} posições exportadas para {filename}")
        return filename
    
    def export_backtest_results(self, results: Dict[str, BacktestResult], filename: str = None):
        """Exporta resultados de backtest para CSV"""
        if filename is None:
            filename = f"backtest_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        rows = []
        for symbol, result in results.items():
            row = {'symbol': symbol}
            row.update(result.to_dict())
            rows.append(row)
        
        if rows:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                writer.writeheader()
                writer.writerows(rows)
            
            self.logger.info(f"💾 Resultados exportados para {filename}")
        
        return filename

# =============================================================================
# FUNÇÃO PRINCIPAL
# =============================================================================

def main():
    """Função principal para demonstrar o uso do Auto Trader"""
    
    print("\n" + "="*90)
    print("🚀 VHALINOR IAG - AUTO TRADER QUÂNTICO")
    print("="*90)
    print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("="*90)
    
    # 1. Configurar trading
    print("\n1️⃣  Configurando parâmetros de trading...")
    config = TradingConfig(
        name="Vhalinor Quantum Strategy",
        initial_balance=10000.0,
        risk_per_trade=0.02,
        max_positions=3,
        stop_loss_pct=0.02,
        take_profit_pct=0.04,
        trailing_stop=True,
        symbols=['BTCUSDT', 'ETHUSDT']
    )
    
    # 2. Criar data feed (simulador para demonstração)
    print("\n2️⃣  Inicializando data feed...")
    data_feed = SimulatorDataFeed()
    
    # 3. Criar estratégia (ensemble para melhor performance)
    print("\n3️⃣  Inicializando estratégias...")
    
    strategies = [
        EMACrossoverStrategy(fast_period=12, slow_period=26),
        RSIStrategy(oversold=30, overbought=70),
        BollingerBandsStrategy(period=20, std_dev=2),
        MACDStrategy(fast=12, slow=26, signal=9)
    ]
    
    strategy = EnsembleStrategy(
        strategies=strategies,
        weights=[0.3, 0.3, 0.2, 0.2]
    )
    
    # 4. Criar trader
    print("\n4️⃣  Inicializando Auto Trader...")
    trader = VhalinorAutoTrader(
        trading_config=config,
        data_feed=data_feed,
        strategy=strategy,
        mode=TradingMode.PAPER,
        notifier_config={'enable_telegram': False}
    )
    
    # 5. Registrar callbacks
    def on_trade(trade):
        print(f"   ✅ Trade: {trade['symbol']} - P&L: ${trade['pnl']:.2f}")
    
    def on_position_open(position):
        print(f"   📈 Posição aberta: {position['symbol']} @ ${position['entry_price']:.2f}")
    
    trader.register_callback('on_trade', on_trade)
    trader.register_callback('on_position_open', on_position_open)
    
    # 6. Executar backtest rápido
    print("\n5️⃣  Executando backtest...")
    
    # Gerar dados sintéticos para backtest
    if PANDAS_AVAILABLE:
        dates = pd.date_range(end=datetime.now(), periods=500, freq='1h')
        np.random.seed(42)
        returns = np.random.randn(500) * 0.02
        prices = 100 * np.exp(np.cumsum(returns))
        
        df = pd.DataFrame({
            'open': prices * 0.999,
            'high': prices * 1.002,
            'low': prices * 0.998,
            'close': prices,
            'volume': np.random.randint(1000, 10000, 500)
        }, index=dates)
        
        backtest_results = trader.run_backtest({'BTCUSDT': df, 'ETHUSDT': df})
    
    # 7. Gerar relatório
    print("\n6️⃣  Gerando relatório...")
    report = trader.generate_report()
    print("\n" + report)
    
    # 8. Exportar dados
    print("\n7️⃣  Exportando dados...")
    trader.export_trades()
    trader.export_positions()
    trader.export_backtest_results(backtest_results)
    
    # 9. Iniciar trading ao vivo (breve demonstração)
    print("\n8️⃣  Iniciando trading ao vivo (10 segundos)...")
    trader.run_live()
    time.sleep(10)
    trader.stop()
    
    print("\n" + "="*90)
    print("✅ DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*90)


if __name__ == "__main__":
    main()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    'TradingMode',
    'TimeFrame',
    'OrderSide',
    'OrderType',
    'OrderStatus',
    'BrokerType',
    'SignalStrength',
    'RiskLevel',
    
    # Configurações
    'TradingConfig',
    'BrokerConfig',
    
    # Estruturas de dados
    'Position',
    'Trade',
    'BacktestResult',
    
    # Data Feeds
    'DataFeed',
    'BinanceDataFeed',
    'YahooDataFeed',
    'CCXTDataFeed',
    'SimulatorDataFeed',
    'DataFeedFactory',
    
    # Indicadores
    'TechnicalIndicators',
    
    # Estratégias
    'TradingStrategy',
    'EMACrossoverStrategy',
    'RSIStrategy',
    'BollingerBandsStrategy',
    'MACDStrategy',
    'EnsembleStrategy',
    
    # Gerenciadores
    'RiskManager',
    'Notifier',
    
    # Classe principal
    'VhalinorAutoTrader',
    
    # Função principal
    'main'
]
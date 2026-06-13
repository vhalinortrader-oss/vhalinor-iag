# 01_config.py
"""
Sistema VhalinorTrade - Configurações Globais
IA de Trading Autônomo com Deep Learning
"""

import os
from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum

class TimeFrame(Enum):
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    H1 = "1h"
    H4 = "4h"
    D1 = "1d"
    W1 = "1w"
    MN = "1M"

class AssetType(Enum):
    SPOT = "spot"
    FUTURES = "futures"
    MARGIN = "margin"

@dataclass
class APIConfig:
    binance_api_key: str = os.getenv("BINANCE_API_KEY", "")
    binance_api_secret: str = os.getenv("BINANCE_API_SECRET", "")
    bybit_api_key: str = os.getenv("BYBIT_API_KEY", "")
    bybit_api_secret: str = os.getenv("BYBIT_API_SECRET", "")
    pionex_api_key: str = os.getenv("PIONEX_API_KEY", "")
    pionex_api_secret: str = os.getenv("PIONEX_API_SECRET", "")

@dataclass
class TradingConfig:
    max_exposure_per_trade: float = 0.02  # 2% do capital
    max_total_exposure: float = 0.30  # 30% do capital total
    stop_loss_percentage: float = 0.015  # 1.5%
    take_profit_percentage: float = 0.03  # 3%
    reserve_fund_percentage: float = 0.20  # 20% reserva
    max_concurrent_trades: int = 5
    reinvestment_rate: float = 0.50  # 50% dos lucros reinvestidos

@dataclass
class NeuralConfig:
    input_sequence_length: int = 100
    hidden_layers: List[int] = None
    learning_rate: float = 0.001
    batch_size: int = 64
    epochs: int = 100
    dropout_rate: float = 0.3
    lstm_units: int = 128
    attention_heads: int = 8
    
    def __post_init__(self):
        if self.hidden_layers is None:
            self.hidden_layers = [256, 128, 64, 32]

@dataclass
class RiskConfig:
    var_confidence: float = 0.95
    max_drawdown: float = 0.15
    volatility_threshold: float = 0.05
    correlation_threshold: float = 0.7
    min_liquidity_usd: float = 100000

class VhalinorConfig:
    def __init__(self):
        self.api = APIConfig()
        self.trading = TradingConfig()
        self.neural = NeuralConfig()
        self.risk = RiskConfig()
        self.symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "ADAUSDT"]
        self.timeframes = [TimeFrame.M1, TimeFrame.M5, TimeFrame.H15, TimeFrame.H1]
        self.data_path = "./data"
        self.models_path = "./models"
        self.logs_path = "./logs"
        
        os.makedirs(self.data_path, exist_ok=True)
        os.makedirs(self.models_path, exist_ok=True)
        os.makedirs(self.logs_path, exist_ok=True)

config = VhalinorConfig()
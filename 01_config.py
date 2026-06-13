# 01_config.py
"""
Sistema VhalinorTrade - Configurações Globais
IA de Trading Autônomo com Deep Learning
"""

import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional


# ------------------------------------------------------------
# Enums
# ------------------------------------------------------------
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


# ------------------------------------------------------------
# Dataclasses de configuração
# ------------------------------------------------------------
@dataclass
class APIConfig:
    """Credenciais de acesso às exchanges."""
    binance_api_key: str = os.getenv("BINANCE_API_KEY", "")
    binance_api_secret: str = os.getenv("BINANCE_API_SECRET", "")
    bybit_api_key: str = os.getenv("BYBIT_API_KEY", "")
    bybit_api_secret: str = os.getenv("BYBIT_API_SECRET", "")
    pionex_api_key: str = os.getenv("PIONEX_API_KEY", "")
    pionex_api_secret: str = os.getenv("PIONEX_API_SECRET", "")


@dataclass
class TradingConfig:
    """Parâmetros de gestão de capital e operações."""
    max_exposure_per_trade: float = 0.02          # 2% do capital
    max_total_exposure: float = 0.30              # 30% do capital total
    stop_loss_percentage: float = 0.015           # 1.5%
    take_profit_percentage: float = 0.03          # 3%
    reserve_fund_percentage: float = 0.20         # 20% reserva
    max_concurrent_trades: int = 5
    reinvestment_rate: float = 0.50               # 50% dos lucros reinvestidos


@dataclass
class NeuralConfig:
    """Hiperparâmetros da rede neural (LSTM + Attention)."""
    input_sequence_length: int = 100
    hidden_layers: Optional[List[int]] = field(default=None)
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
    """Parâmetros de controle de risco e limites."""
    var_confidence: float = 0.95
    max_drawdown: float = 0.15
    volatility_threshold: float = 0.05
    correlation_threshold: float = 0.7
    min_liquidity_usd: float = 100_000


# ------------------------------------------------------------
# Classe central de configuração
# ------------------------------------------------------------
class VhalinorConfig:
    """
    Agrega todas as configurações do sistema e garante
    a existência dos diretórios de dados, modelos e logs.
    """

    def __init__(self):
        self.api = APIConfig()
        self.trading = TradingConfig()
        self.neural = NeuralConfig()
        self.risk = RiskConfig()

        # Ativos monitorados (cripto/spot/futuros via klines da Binance)
        # Adicionados: 10 ativos para aumentar cobertura do universo.
        self.symbols = [
            "BTCUSDT", "ETHUSDT", "BNBUSDT",
            "SOLUSDT", "ADAUSDT",
            # novos (10)
            "XRPUSDT", "DOGEUSDT", "AVAXUSDT", "MATICUSDT", "LINKUSDT",
            "DOTUSDT", "TRXUSDT", "UNIUSDT", "ATOMUSDT", "ETCUSDT"
        ]
        self.timeframes = [
            TimeFrame.M1, TimeFrame.M5,
            TimeFrame.H4, TimeFrame.H1
        ]

        # Caminhos base (utilizando pathlib)
        self.data_path = Path("./data")
        self.models_path = Path("./models")
        self.logs_path = Path("./logs")

        # Cria os diretórios se não existirem
        for path in (self.data_path, self.models_path, self.logs_path):
            path.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------
# Instância global (singleton simples)
# ------------------------------------------------------------
config = VhalinorConfig()
"""
╔════════════════════════════════════════════════════════════════════════════════════════════════╗
║                    VHALINOR TRADING SYSTEM v5.0 - ENHANCED VERSION                        ║
║                SISTEMA INTEGRADO DE TRADING COM IA AVANÇADA                          ║
╠══════════════════════════════════════════════════════════════════════════════════════════════════════╣
║  Versão: 5.0.0 (Enhanced with AI Integration - Production Ready)                    ║
║  Autor: VHALINOR.IAG Core Team                                                     ║
║  Data: 2026                                                                       ║
║  License: Proprietary                                                               ║
╚════════════════════════════════════════════════════════════════════════════════════════════════════╝
"""

# =============================================================================
# IMPORTAÇÕES AVANÇADAS COM FALLBACKS E SUPORTE AI/ML
# =============================================================================

import asyncio
import json
import logging
import time
import threading
import hashlib
import warnings
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union, Callable, TypeVar, Generic
from enum import Enum, auto
from pathlib import Path
from functools import lru_cache, wraps
import numpy as np
import pandas as pd

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
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
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

# Comunicação em tempo real
try:
    import websockets
    import aiohttp
    HAS_WEBSOCKETS = True
    HAS_AIOHTTP = True
except ImportError:
    HAS_WEBSOCKETS = False
    HAS_AIOHTTP = False

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

# Configurar logging avançado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vhalinor_trading_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Importar componentes do sistema
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '01_sensorial'))

try:
    from trading_execution_engine import TradingExecutionEngine
    from decision_engine_master import DecisionEngineMaster
    COMPONENTS_AVAILABLE = True
except ImportError:
    COMPONENTS_AVAILABLE = False
    TradingExecutionEngine = None
    DecisionEngineMaster = None


# =============================================================================
# NOVAS CLASSES DE IA AVANÇADA E TRADING
# =============================================================================

class TradingMode(Enum):
    """Modos de trading avançados"""
    ULTRA_CONSERVATIVE = auto()
    CONSERVATIVE = auto()
    MODERATE = auto()
    AGGRESSIVE = auto()
    ULTRA_AGGRESSIVE = auto()
    AI_POWERED = auto()
    QUANTUM_ENHANCED = auto()

class MarketCondition(Enum):
    """Condições de mercado"""
    BULLISH = auto()
    BEARISH = auto()
    SIDEWAYS = auto()
    VOLATILE = auto()
    TRENDING = auto()
    RANGING = auto()

class SignalType(Enum):
    """Tipos de sinais de trading"""
    BUY_STRONG = auto()
    BUY_WEAK = auto()
    SELL_STRONG = auto()
    SELL_WEAK = auto()
    HOLD = auto()
    NEUTRAL = auto()

@dataclass
class TradingSignal:
    """Sinal de trading avançado"""
    signal_id: str
    symbol: str
    signal_type: SignalType
    confidence: float
    entry_price: float
    stop_loss: float
    take_profit: float
    position_size: float
    risk_reward_ratio: float
    market_condition: MarketCondition
    timestamp: datetime = field(default_factory=datetime.now)
    technical_indicators: Dict[str, float] = field(default_factory=dict)
    ai_predictions: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class AdvancedTradingAI:
    """Sistema de IA avançada para trading"""
    
    def __init__(self):
        self.models = {}
        self.predictions = []
        self.market_conditions = {}
        self.performance_metrics = {}
        
        # Inicializa modelos se disponíveis
        self._initialize_ai_models()
    
    def _initialize_ai_models(self):
        """Inicializa modelos de IA"""
        if HAS_TORCH:
            self._initialize_neural_networks()
        
        if HAS_SKLEARN:
            self._initialize_ml_models()
    
    def _initialize_neural_networks(self):
        """Inicializa redes neurais"""
        self.models['lstm_predictor'] = self._create_lstm_model()
        self.models['transformer'] = self._create_transformer_model()
        self.models['cnn_analyzer'] = self._create_cnn_model()
        logger.info("Redes neurais inicializadas")
    
    def _create_lstm_model(self):
        """Cria modelo LSTM para predição"""
        if not HAS_TORCH:
            return None
            
        class LSTMModel(torch.nn.Module):
            def __init__(self, input_size, hidden_size, num_layers, output_size):
                super().__init__()
                self.hidden_size = hidden_size
                self.num_layers = num_layers
                self.lstm = torch.nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
                self.fc = torch.nn.Linear(hidden_size, output_size)
            
            def forward(self, x):
                lstm_out, _ = self.lstm(x)
                predictions = self.fc(lstm_out[:, -1, :])
                return predictions
        
        return LSTMModel(input_size=10, hidden_size=50, num_layers=2, output_size=1)
    
    def _create_transformer_model(self):
        """Cria modelo Transformer para análise"""
        if not HAS_TORCH:
            return None
            
        class TransformerModel(torch.nn.Module):
            def __init__(self, input_size, d_model, nhead, num_layers):
                super().__init__()
                self.d_model = d_model
                self.embedding = torch.nn.Linear(input_size, d_model)
                encoder_layer = torch.nn.TransformerEncoderLayer(d_model, nhead, batch_first=True)
                self.transformer_encoder = torch.nn.TransformerEncoder(encoder_layer, num_layers)
                self.fc = torch.nn.Linear(d_model, 1)
            
            def forward(self, x):
                x = self.embedding(x)
                x = self.transformer_encoder(x)
                x = x.mean(dim=1)
                return self.fc(x)
        
        return TransformerModel(input_size=10, d_model=64, nhead=8, num_layers=4)
    
    def _create_cnn_model(self):
        """Cria modelo CNN para análise de padrões"""
        if not HAS_TORCH:
            return None
            
        class CNNModel(torch.nn.Module):
            def __init__(self, input_channels, seq_length):
                super().__init__()
                self.conv1 = torch.nn.Conv1d(input_channels, 32, kernel_size=3)
                self.conv2 = torch.nn.Conv1d(32, 64, kernel_size=3)
                self.pool = torch.nn.MaxPool1d(kernel_size=2)
                self.fc = torch.nn.Linear(64 * ((seq_length - 4) // 4), 1)
            
            def forward(self, x):
                x = torch.relu(self.conv1(x))
                x = torch.relu(self.conv2(x))
                x = self.pool(x)
                x = x.view(x.size(0), -1)
                return self.fc(x)
        
        return CNNModel(input_channels=1, seq_length=50)
    
    def analyze_market_condition(self, market_data: pd.DataFrame) -> MarketCondition:
        """Analisa condição atual do mercado"""
        try:
            # Análise técnica básica
            returns = market_data['close'].pct_change().dropna()
            volatility = returns.std() * np.sqrt(252)
            trend = returns.mean() * 252
            
            # Determinar condição
            if trend > 0.1:
                return MarketCondition.BULLISH
            elif trend < -0.1:
                return MarketCondition.BEARISH
            elif volatility > 0.3:
                return MarketCondition.VOLATILE
            elif abs(trend) < 0.05:
                return MarketCondition.SIDEWAYS
            else:
                return MarketCondition.RANGING
                
        except Exception as e:
            logger.error(f"Erro na análise de mercado: {e}")
            return MarketCondition.NEUTRAL
    
    def generate_trading_signal(self, market_data: pd.DataFrame, symbol: str) -> Optional[TradingSignal]:
        """Gera sinal de trading usando IA"""
        try:
            # Análise de mercado
            market_condition = self.analyze_market_condition(market_data)
            
            # Preparar dados para modelos
            features = self._extract_features(market_data)
            
            # Gerar predições
            predictions = {}
            if 'lstm_predictor' in self.models and self.models['lstm_predictor']:
                lstm_pred = self._predict_with_lstm(features)
                predictions['lstm'] = lstm_pred
            
            if 'transformer' in self.models and self.models['transformer']:
                transformer_pred = self._predict_with_transformer(features)
                predictions['transformer'] = transformer_pred
            
            # Combinar predições
            ensemble_prediction = self._ensemble_predictions(predictions)
            
            # Gerar sinal
            if ensemble_prediction > 0.7:
                signal_type = SignalType.BUY_STRONG
                confidence = ensemble_prediction
            elif ensemble_prediction > 0.5:
                signal_type = SignalType.BUY_WEAK
                confidence = ensemble_prediction
            elif ensemble_prediction < -0.7:
                signal_type = SignalType.SELL_STRONG
                confidence = abs(ensemble_prediction)
            elif ensemble_prediction < -0.5:
                signal_type = SignalType.SELL_WEAK
                confidence = abs(ensemble_prediction)
            else:
                signal_type = SignalType.HOLD
                confidence = 0.5
            
            # Calcular preço e parâmetros
            current_price = market_data['close'].iloc[-1]
            atr = self._calculate_atr(market_data)
            
            signal = TradingSignal(
                signal_id=hashlib.md5(f"{symbol}{datetime.now().isoformat()}".encode()).hexdigest()[:16],
                symbol=symbol,
                signal_type=signal_type,
                confidence=confidence,
                entry_price=current_price,
                stop_loss=current_price - (2 * atr),
                take_profit=current_price + (3 * atr),
                position_size=self._calculate_position_size(confidence, atr),
                risk_reward_ratio=1.5,
                market_condition=market_condition,
                ai_predictions=predictions,
                technical_indicators=self._calculate_technical_indicators(market_data)
            )
            
            return signal
            
        except Exception as e:
            logger.error(f"Erro ao gerar sinal: {e}")
            return None
    
    def _extract_features(self, market_data: pd.DataFrame) -> np.ndarray:
        """Extrai features para modelos de IA"""
        try:
            features = []
            
            # Returns
            returns = market_data['close'].pct_change().dropna()
            features.extend([
                returns.mean(),    # Mean return
                returns.std(),     # Volatility
                returns.skew(),    # Skewness
                returns.kurtosis() # Kurtosis
            ])
            
            # Price action
            features.extend([
                market_data['close'].iloc[-1] / market_data['close'].iloc[-5] - 1,  # 5-period return
                market_data['close'].iloc[-1] / market_data['close'].iloc[-10] - 1, # 10-period return
                market_data['close'].iloc[-1] / market_data['close'].iloc[-20] - 1, # 20-period return
            ])
            
            # Volume
            if 'volume' in market_data:
                volume_ratio = market_data['volume'].iloc[-1] / market_data['volume'].mean()
                features.append(volume_ratio)
            else:
                features.append(1.0)
            
            # High-Low
            if 'high' in market_data and 'low' in market_data:
                hl_ratio = (market_data['high'].iloc[-1] - market_data['low'].iloc[-1]) / market_data['close'].iloc[-1]
                features.append(hl_ratio)
            else:
                features.append(0.02)
            
            return np.array(features).reshape(1, -1)
            
        except Exception as e:
            logger.error(f"Erro na extração de features: {e}")
            return np.random.random(10).reshape(1, -1)
    
    def _predict_with_lstm(self, features: np.ndarray) -> float:
        """Faz predição com modelo LSTM"""
        try:
            if not self.models['lstm_predictor']:
                return 0.5
            
            # Converter para tensor
            x = torch.FloatTensor(features)
            
            # Predição
            with torch.no_grad():
                prediction = self.models['lstm_predictor'](x)
                return torch.sigmoid(prediction).item()
                
        except Exception as e:
            logger.error(f"Erro na predição LSTM: {e}")
            return 0.5
    
    def _predict_with_transformer(self, features: np.ndarray) -> float:
        """Faz predição com modelo Transformer"""
        try:
            if not self.models['transformer']:
                return 0.5
            
            # Converter para tensor
            x = torch.FloatTensor(features)
            
            # Predição
            with torch.no_grad():
                prediction = self.models['transformer'](x)
                return torch.sigmoid(prediction).item()
                
        except Exception as e:
            logger.error(f"Erro na predição Transformer: {e}")
            return 0.5
    
    def _ensemble_predictions(self, predictions: Dict[str, float]) -> float:
        """Combina predições de múltiplos modelos"""
        if not predictions:
            return 0.5
        
        # Média ponderada
        weights = {'lstm': 0.4, 'transformer': 0.6}
        ensemble_pred = 0
        total_weight = 0
        
        for model_name, pred in predictions.items():
            if model_name in weights:
                ensemble_pred += pred * weights[model_name]
                total_weight += weights[model_name]
        
        return ensemble_pred / total_weight if total_weight > 0 else 0.5
    
    def _calculate_atr(self, market_data: pd.DataFrame, period: int = 14) -> float:
        """Calcula Average True Range"""
        try:
            high = market_data['high'].rolling(window=period).max()
            low = market_data['low'].rolling(window=period).min()
            close = market_data['close'].shift(1)
            
            tr1 = high - low
            tr2 = abs(high - close)
            tr3 = abs(low - close)
            
            atr = (tr1 + tr2 + tr3).rolling(window=period).mean()
            return atr.iloc[-1] if not pd.isna(atr.iloc[-1]) else 0.02
            
        except Exception as e:
            logger.error(f"Erro no cálculo ATR: {e}")
            return 0.02
    
    def _calculate_position_size(self, confidence: float, atr: float) -> float:
        """Calcula tamanho da posição baseado na confiança e ATR"""
        base_size = 0.01  # 1% do capital
        risk_adjustment = min(confidence, 1.0)
        volatility_adjustment = min(atr / 0.02, 2.0)  # Ajuste pela volatilidade
        
        return base_size * risk_adjustment * volatility_adjustment
    
    def _calculate_technical_indicators(self, market_data: pd.DataFrame) -> Dict[str, float]:
        """Calcula indicadores técnicos"""
        try:
            indicators = {}
            
            # RSI
            delta = market_data['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            indicators['rsi'] = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
            
            # MACD
            exp1 = market_data['close'].ewm(span=12).mean()
            exp2 = market_data['close'].ewm(span=26).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=9).mean()
            indicators['macd'] = macd.iloc[-1] if not pd.isna(macd.iloc[-1]) else 0
            indicators['macd_signal'] = signal.iloc[-1] if not pd.isna(signal.iloc[-1]) else 0
            
            # Bollinger Bands
            sma = market_data['close'].rolling(window=20).mean()
            std = market_data['close'].rolling(window=20).std()
            indicators['bb_upper'] = (sma + 2 * std).iloc[-1] if not pd.isna((sma + 2 * std).iloc[-1]) else 0
            indicators['bb_lower'] = (sma - 2 * std).iloc[-1] if not pd.isna((sma - 2 * std).iloc[-1]) else 0
            
            return indicators
            
        except Exception as e:
            logger.error(f"Erro nos indicadores técnicos: {e}")
            return {}

class RealTimeTradingMonitor:
    """Monitor de trading em tempo real"""
    
    def __init__(self, trading_system: 'IntegratedTradingSystem'):
        self.trading_system = trading_system
        self.is_monitoring = False
        self.subscribers = []
        self.monitoring_thread = None
        
    def start_monitoring(self):
        """Inicia monitoramento em tempo real"""
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        logger.info("Monitoramento em tempo real iniciado")
    
    def stop_monitoring(self):
        """Para monitoramento"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("Monitoramento em tempo real parado")
    
    def _monitoring_loop(self):
        """Loop principal de monitoramento"""
        while self.is_monitoring:
            try:
                # Coletar status
                status = self.trading_system.get_system_status()
                
                # Notificar assinantes
                for subscriber in self.subscribers:
                    try:
                        subscriber(status)
                    except Exception as e:
                        logger.error(f"Erro no subscriber: {e}")
                
                # Aguardar próximo ciclo
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"Erro no monitoramento: {e}")
                time.sleep(10)
    
    def subscribe(self, callback):
        """Adiciona assinante para atualizações"""
        self.subscribers.append(callback)
    
    def unsubscribe(self, callback):
        """Remove assinante"""
        if callback in self.subscribers:
            self.subscribers.remove(callback)


class SystemMode(Enum):
    """Modos de operação do sistema"""
    ANALYSIS_ONLY = "ANALYSIS_ONLY"
    SIMULATION = "SIMULATION"
    LIVE_TRADING = "LIVE_TRADING"


class IntegratedTradingSystem:
    """
    Sistema Integrado de Trading que coordena todos os componentes
    """

    def __init__(self, config_file: str = "system_config.json"):
        """
        Args:
            config_file: Arquivo de configuração do sistema
        """
        self.config_file = config_file
        self.config = self._load_config()
        
        # Inicializar componentes
        self.account_balance = self.config.get('account_balance', 100000)
        
        # Inicializar execution engine apenas se disponível
        if COMPONENTS_AVAILABLE and TradingExecutionEngine:
            self.execution_engine = TradingExecutionEngine(self.account_balance)
        else:
            self.execution_engine = None
            logger.warning("Execution engine não disponível - modo simulado")
            
        self.analysis_interval = timedelta(minutes=15)  # Padrão
        
        # Estado do sistema
        self.system_mode = SystemMode.ANALYSIS_ONLY
        self.is_running = False
        self.last_analysis_time = None
        self.system_stats = {
            'total_sessions': 0,
            'successful_trades': 0,
            'failed_trades': 0,
            'total_profit': 0.0,
            'uptime_start': None
        }

    def _load_config(self) -> Dict:
        """
        Carrega configuração do sistema
        """
        config_path = self.config_file
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info(f"✅ Configuração carregada: {config_path}")
            return config
        except FileNotFoundError:
            logger.warning(f"⚠️  Arquivo de configuração não encontrado: {config_path}")
            return self._create_default_config()
        except Exception as e:
            logger.error(f"❌ Erro ao carregar configuração: {e}")
            return self._create_default_config()

    def _create_default_config(self) -> Dict:
        """
        Cria configuração padrão do sistema
        """
        default_config = {
            "account_balance": 100000,
            "system_mode": "ANALYSIS_ONLY",
            "analysis_interval_minutes": 15,
            "max_daily_trades": 20,
            "risk_management": {
                "max_risk_per_day": 0.05,
                "max_risk_per_trade": 0.02,
                "max_concurrent_trades": 10
            },
            "exchanges": {
                "ctrader": {
                    "name": "cTrader-Demo",
                    "client_id": "your_client_id",
                    "client_secret": "your_client_secret",
                    "environment": "demo",
                    "enabled": False
                },
                "pionex": {
                    "name": "Pionex-Live",
                    "api_key": "your_api_key",
                    "api_secret": "your_api_secret",
                    "environment": "live",
                    "enabled": False
                }
            },
            "notifications": {
                "email_enabled": False,
                "webhook_enabled": False,
                "log_level": "INFO"
            },
            "data_collection": {
                "crypto_pairs": 20,
                "forex_pairs": 20,
                "update_interval_minutes": 5
            }
        }
        
        # Salvar configuração padrão
        self._save_config(default_config)
        return default_config

    def _save_config(self, config: Dict):
        """
        Salva configuração do sistema
        """
        config_path = self.config_file
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            logger.info(f"💾 Configuração salva: {config_path}")
        except Exception as e:
            logger.error(f"❌ Erro ao salvar configuração: {e}")

    # ==================== CONTROLE DO SISTEMA ====================

    def initialize_system(self) -> bool:
        """
        Inicializa o sistema completo
        """
        logger.info("="*80)
        logger.info("🚀 INICIALIZANDO SISTEMA INTEGRADO DE TRADING")
        logger.info("="*80)
        
        try:
            # 1. Configurar exchanges
            logger.info("Configurando exchanges...")
            exchanges_config = self.config.get('exchanges', {})
            
            if self.execution_engine:
                if not self.execution_engine.setup_exchanges(exchanges_config):
                    logger.warning("Nenhuma exchange configurada - modo apenas análise")
            else:
                logger.warning("Execution engine não disponível - modo apenas análise")
            
            # 2. Definir modo do sistema
            mode_str = self.config.get('system_mode', 'ANALYSIS_ONLY')
            self.system_mode = SystemMode(mode_str)
            logger.info(f"Modo do sistema: {self.system_mode.value}")
            
            # 3. Configurar execução automática
            if self.execution_engine:
                if self.system_mode == SystemMode.LIVE_TRADING:
                    self.execution_engine.enable_auto_execution(True)
                    logger.info("Execução automática HABILITADA")
                else:
                    self.execution_engine.enable_auto_execution(False)
                    logger.info("Modo apenas análise/simulação")
            
            # 4. Configurar agendamento (simples sem schedule)
            interval = self.config.get('analysis_interval_minutes', 15)
            self.analysis_interval = timedelta(minutes=interval)
            logger.info(f"Análise configurada a cada {interval} minutos")
            
            # 5. Inicializar estatísticas
            self.system_stats['uptime_start'] = datetime.now()
            
            logger.info("Sistema inicializado com sucesso!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro na inicialização: {e}")
            return False

    def start_system(self):
        """
        Inicia o sistema de trading
        """
        if not self.initialize_system():
            logger.error("❌ Falha na inicialização - sistema não iniciado")
            return
        
        self.is_running = True
        logger.info("🟢 SISTEMA INICIADO - Executando...")
        
        try:
            while self.is_running:
                # Verificar se é hora de análise
                if self._should_run_analysis():
                    self._run_analysis_cycle()
                
                # Pausa para não sobrecarregar
                time.sleep(30)  # 30 segundos
                
        except KeyboardInterrupt:
            logger.info("⏹️  Interrupção pelo usuário")
        except Exception as e:
            logger.error(f"❌ Erro durante execução: {e}")
        finally:
            self.stop_system()

    def stop_system(self):
        """
        Para o sistema de trading
        """
        self.is_running = False
        logger.info("🔴 SISTEMA PARADO")
        
        # Gerar relatório final
        self._generate_final_report()

    def _should_run_analysis(self) -> bool:
        """
        Verifica se deve executar análise
        """
        if self.last_analysis_time is None:
            return True
        
        return datetime.now() - self.last_analysis_time >= self.analysis_interval

    def _scheduled_analysis(self):
        """
        Análise agendada pelo schedule
        """
        logger.info("⏰ Executando análise agendada...")
        self._run_analysis_cycle()

    def _run_analysis_cycle(self):
        """
        Executa um ciclo completo de análise
        """
        try:
            logger.info("🔄 Iniciando ciclo de análise...")
            
            # Executar análise e execução
            session = self.execution_engine.run_complete_analysis_and_execution()
            
            # Atualizar estatísticas
            self._update_system_stats(session)
            
            # Salvar sessão
            self.execution_engine.save_execution_session(session)
            
            # Atualizar tempo da última análise
            self.last_analysis_time = datetime.now()
            
            logger.info("✅ Ciclo de análise concluído")
            
        except Exception as e:
            logger.error(f"❌ Erro no ciclo de análise: {e}")

    def _update_system_stats(self, session: Dict):
        """
        Atualiza estatísticas do sistema
        """
        self.system_stats['total_sessions'] += 1
        
        summary = session.get('summary', {})
        if summary:
            self.system_stats['successful_trades'] += summary.get('executions_successful', 0)
            self.system_stats['failed_trades'] += summary.get('executions_failed', 0)
            self.system_stats['total_profit'] += summary.get('expected_profit', 0)

    # ==================== RELATÓRIOS E MONITORAMENTO ====================

    def get_system_status(self) -> Dict:
        """
        Obtém status atual do sistema
        """
        uptime = None
        if self.system_stats['uptime_start']:
            uptime_delta = datetime.now() - self.system_stats['uptime_start']
            uptime = str(uptime_delta).split('.')[0]  # Remove microsegundos
        
        return {
            'timestamp': datetime.now().isoformat(),
            'is_running': self.is_running,
            'system_mode': self.system_mode.value,
            'uptime': uptime,
            'last_analysis': self.last_analysis_time.isoformat() if self.last_analysis_time else None,
            'account_balance': self.account_balance,
            'statistics': self.system_stats.copy(),
            'active_trades': len(self.execution_engine.active_trades)
        }

    def generate_system_report(self) -> str:
        """
        Gera relatório completo do sistema
        """
        status = self.get_system_status()
        
        report = []
        report.append("="*80)
        report.append("🏢 RELATÓRIO DO SISTEMA INTEGRADO DE TRADING")
        report.append("="*80)
        report.append(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Status geral
        report.append("📊 STATUS GERAL:")
        report.append("-"*80)
        report.append(f"Sistema rodando: {'🟢 Sim' if status['is_running'] else '🔴 Não'}")
        report.append(f"Modo de operação: {status['system_mode']}")
        report.append(f"Tempo ativo: {status['uptime'] or 'N/A'}")
        report.append(f"Última análise: {status['last_analysis'] or 'Nunca'}")
        report.append(f"Saldo da conta: ${status['account_balance']:,.2f}")
        report.append(f"Trades ativos: {status['active_trades']}")

        # Estatísticas
        stats = status['statistics']
        report.append("")
        report.append("📈 ESTATÍSTICAS:")
        report.append("-"*80)
        report.append(f"Total de sessões: {stats['total_sessions']}")
        report.append(f"Trades bem-sucedidos: {stats['successful_trades']}")
        report.append(f"Trades falharam: {stats['failed_trades']}")
        
        total_trades = stats['successful_trades'] + stats['failed_trades']
        success_rate = (stats['successful_trades'] / total_trades * 100) if total_trades > 0 else 0
        report.append(f"Taxa de sucesso: {success_rate:.1f}%")
        report.append(f"Lucro total esperado: ${stats['total_profit']:,.2f}")

        # Configuração atual
        report.append("")
        report.append("⚙️  CONFIGURAÇÃO:")
        report.append("-"*80)
        report.append(f"Intervalo de análise: {self.config.get('analysis_interval_minutes', 15)} min")
        report.append(f"Máx. trades por dia: {self.config.get('max_daily_trades', 20)}")
        
        risk_config = self.config.get('risk_management', {})
        report.append(f"Risco máx. por dia: {risk_config.get('max_risk_per_day', 0.05)*100:.1f}%")
        report.append(f"Risco máx. por trade: {risk_config.get('max_risk_per_trade', 0.02)*100:.1f}%")

        # Status das exchanges
        report.append("")
        report.append("🔗 EXCHANGES:")
        report.append("-"*80)
        
        connectivity = self.execution_engine.exchange_integrator.test_connections()
        for exchange_name, is_connected in connectivity.items():
            status_icon = "🟢" if is_connected else "🔴"
            report.append(f"{status_icon} {exchange_name}")

        report.append("")
        report.append("="*80)
        
        return "\n".join(report)

    def _generate_final_report(self):
        """
        Gera relatório final quando o sistema é parado
        """
        report = self.generate_system_report()
        
        # Salvar relatório
        filename = f"final_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = f"{filename}"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"📄 Relatório final salvo: {filepath}")
        print("\n" + report)

    # ==================== UTILITÁRIOS ====================

    def update_config(self, new_config: Dict):
        """
        Atualiza configuração do sistema
        """
        self.config.update(new_config)
        self._save_config(self.config)
        logger.info("✅ Configuração atualizada")

    def set_system_mode(self, mode: SystemMode):
        """
        Altera modo do sistema
        """
        self.system_mode = mode
        self.config['system_mode'] = mode.value
        self._save_config(self.config)
        
        # Reconfigurar execução automática
        if mode == SystemMode.LIVE_TRADING:
            self.execution_engine.enable_auto_execution(True)
        else:
            self.execution_engine.enable_auto_execution(False)
        
        logger.info(f"🎯 Modo do sistema alterado para: {mode.value}")

    def run_single_analysis(self) -> Dict:
        """
        Executa uma única análise (para testes)
        """
        logger.info("🔍 Executando análise única...")
        session = self.execution_engine.run_complete_analysis_and_execution()
        self._update_system_stats(session)
        return session


def main():
    """
    Função principal - Sistema completo
    """
    print("="*80)
    print("🏢 SISTEMA INTEGRADO DE TRADING - LEXTRADER-IAG 4.0")
    print("="*80)
    
    # Inicializar sistema
    trading_system = IntegratedTradingSystem()
    
    # Menu interativo
    while True:
        print("\n" + "="*50)
        print("🎛️  MENU PRINCIPAL")
        print("="*50)
        print("1. 🚀 Iniciar sistema completo")
        print("2. 🔍 Executar análise única")
        print("3. 📊 Ver status do sistema")
        print("4. 📄 Gerar relatório")
        print("5. ⚙️  Configurar sistema")
        print("6. 🎯 Alterar modo de operação")
        print("7. ❌ Sair")
        
        choice = input("\nEscolha uma opção (1-7): ").strip()
        
        if choice == "1":
            print("\n🚀 Iniciando sistema completo...")
            print("⚠️  Pressione Ctrl+C para parar")
            trading_system.start_system()
            
        elif choice == "2":
            print("\n🔍 Executando análise única...")
            session = trading_system.run_single_analysis()
            report = trading_system.execution_engine.generate_execution_report(session)
            print("\n" + report)
            
        elif choice == "3":
            print("\n📊 Status do sistema:")
            status = trading_system.get_system_status()
            for key, value in status.items():
                if key != 'statistics':
                    print(f"{key}: {value}")
            
        elif choice == "4":
            print("\n📄 Gerando relatório...")
            report = trading_system.generate_system_report()
            print("\n" + report)
            
        elif choice == "5":
            print("\n⚙️  Configuração atual salva em: system_config.json")
            print("Edite o arquivo e reinicie o sistema para aplicar mudanças.")
            
        elif choice == "6":
            print("\n🎯 Modos disponíveis:")
            print("1. ANALYSIS_ONLY - Apenas análise")
            print("2. SIMULATION - Simulação")
            print("3. LIVE_TRADING - Trading real")
            
            mode_choice = input("Escolha o modo (1-3): ").strip()
            modes = {
                "1": SystemMode.ANALYSIS_ONLY,
                "2": SystemMode.SIMULATION,
                "3": SystemMode.LIVE_TRADING
            }
            
            if mode_choice in modes:
                trading_system.set_system_mode(modes[mode_choice])
                print(f"✅ Modo alterado para: {modes[mode_choice].value}")
            else:
                print("❌ Opção inválida")
                
        elif choice == "7":
            print("\n👋 Encerrando sistema...")
            break
            
        else:
            print("❌ Opção inválida. Tente novamente.")
    
    print("\n" + "="*80)
    print("🎉 SISTEMA INTEGRADO DE TRADING FINALIZADO!")
    print("="*80)


if __name__ == "__main__":
    main()
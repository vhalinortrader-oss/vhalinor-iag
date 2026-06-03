"""
Módulo de Predição Avançada
===========================
Implementação com PyTorch, Backtrader e ensemble learning
"""

import asyncio
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import json
import warnings
import math
from collections import deque
import hashlib

# Importações condicionais
try:
    import backtrader as bt
    from backtrader.indicators import MovingAverageSimple, RSI, MACD
    from backtrader.sizers import PercentSizer
    BACKTRADER_AVAILABLE = True
except ImportError:
    BACKTRADER_AVAILABLE = False

try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, VotingRegressor
    from sklearn.preprocessing import StandardScaler, MinMaxScaler
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
    from sklearn.model_selection import TimeSeriesSplit, cross_val_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import talib
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False

from config import settings
from core import get_logger, log_execution


class PredictionType(str, Enum):
    """Tipos de predição disponíveis"""
    PRICE = "price"
    DIRECTION = "direction"
    VOLATILITY = "volatility"
    TREND = "trend"
    SUPPORT_RESISTANCE = "support_resistance"
    MULTI_TIMEFRAME = "multi_timeframe"
    ENSEMBLE = "ensemble"
    RISK_ASSESSMENT = "risk_assessment"


@dataclass
class PredictionResult:
    """Resultado de predição"""
    symbol: str
    prediction_type: PredictionType
    timestamp: datetime
    prediction: float
    confidence: float
    horizon: str  # 1m, 5m, 1h, etc.
    features_used: List[str]
    model_name: str
    metrics: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class BacktestResult:
    """Resultado de backtest"""
    symbol: str
    strategy_name: str
    start_date: datetime
    end_date: datetime
    initial_capital: float
    final_capital: float
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    total_trades: int
    profitable_trades: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        data = asdict(self)
        data['start_date'] = self.start_date.isoformat()
        data['end_date'] = self.end_date.isoformat()
        return data


class LSTMModel(nn.Module):
    """Modelo LSTM para predição de séries temporais"""
    
    def __init__(
        self,
        input_size: int,
        hidden_size: int,
        num_layers: int,
        output_size: int,
        dropout: float = 0.2
    ):
        super(LSTMModel, self).__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # Camadas LSTM
        self.lstm = nn.LSTM(
            input_size,
            hidden_size,
            num_layers,
            batch_first=True,
            dropout=dropout
        )
        
        # Camada de atenção
        self.attention = nn.MultiheadAttention(
            hidden_size,
            num_heads=8,
            dropout=dropout
        )
        
        # Camadas fully connected
        self.fc1 = nn.Linear(hidden_size, hidden_size // 2)
        self.fc2 = nn.Linear(hidden_size // 2, output_size)
        self.dropout = nn.Dropout(dropout)
        
        # Layer norm
        self.layer_norm = nn.LayerNorm(hidden_size)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass"""
        # Passar pela LSTM
        lstm_out, (hidden, cell) = self.lstm(x)
        
        # Aplicar layer norm
        lstm_out = self.layer_norm(lstm_out)
        
        # Aplicar atenção
        attn_out, _ = self.attention(lstm_out, lstm_out, lstm_out)
        
        # Combinar saídas
        combined = lstm_out + attn_out
        
        # Passar pelas camadas fully connected
        out = self.dropout(combined)
        out = torch.relu(self.fc1(out))
        out = self.fc2(out)
        
        return out[:, -1, :]  # Último timestep


class TransformerModel(nn.Module):
    """Modelo Transformer para predição"""
    
    def __init__(
        self,
        input_size: int,
        d_model: int,
        nhead: int,
        num_layers: int,
        output_size: int,
        dropout: float = 0.1
    ):
        super(TransformerModel, self).__init__()
        
        self.d_model = d_model
        self.input_projection = nn.Linear(input_size, d_model)
        
        # Encoder Transformer
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=d_model * 4,
            dropout=dropout,
            batch_first=True
        )
        self.transformer_encoder = nn.TransformerEncoder(
            encoder_layer,
            num_layers=num_layers
        )
        
        # Camada de saída
        self.output_projection = nn.Linear(d_model, output_size)
        self.dropout = nn.Dropout(dropout)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass"""
        # Projetar para d_model
        x = self.input_projection(x)
        x = self.dropout(x)
        
        # Passar pelo Transformer
        encoded = self.transformer_encoder(x)
        
        # Projetar para saída
        out = self.output_projection(encoded)
        
        return out[:, -1, :]  # Último timestep


class Predictor:
    """
    Sistema de predição avançado com ensemble de modelos
    """
    
    def __init__(self):
        self.logger = get_logger().get_logger("vhalinor.predictor", "predictor")
        
        # Modelos de deep learning
        self.models: Dict[str, nn.Module] = {}
        self.scalers: Dict[str, Any] = {}
        
        # Modelos de ensemble
        self.ensemble_models: Dict[str, Any] = {}
        
        # Cache de predições
        self.prediction_cache: Dict[str, List[PredictionResult]] = {}
        
        # Configurações
        self.device = torch.device(settings.ml_device)
        self.batch_size = settings.ml_batch_size
        self.learning_rate = settings.ml_learning_rate
        
        # Métricas de performance
        self.performance_metrics: Dict[str, List[float]] = {
            "mse": [],
            "mae": [],
            "mape": []
        }
        
        # Carregar modelos pré-treinados ou inicializar
        self._initialize_models()
    
    @log_execution(
        component="predictor",
        operation="initialize_models",
        log_exceptions=True
    )
    def _initialize_models(self):
        """Inicializa os modelos de predição"""
        try:
            # Modelo LSTM para BTC
            self.models["lstm_btc"] = LSTMModel(
                input_size=10,  # OHLCV + indicadores
                hidden_size=64,
                num_layers=2,
                output_size=1
            ).to(self.device)
            
            # Modelo Transformer para ETH
            self.models["transformer_eth"] = TransformerModel(
                input_size=10,
                d_model=128,
                nhead=8,
                num_layers=4,
                output_size=1
            ).to(self.device)
            
            # Modelos de ensemble (sklearn)
            if SKLEARN_AVAILABLE:
                self.ensemble_models["rf_price"] = RandomForestRegressor(
                    n_estimators=100,
                    random_state=42
                )
                
                self.ensemble_models["gb_price"] = GradientBoostingRegressor(
                    n_estimators=100,
                    random_state=42
                )
            
            # Scalers
            self.scalers["price"] = StandardScaler()
            
            self.logger.info("Prediction models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize models: {e}")
    
    @log_execution(
        component="predictor",
        operation="prepare_features",
        log_args=True,
        log_result=True
    )
    def prepare_features(
        self,
        data: pd.DataFrame,
        lookback: int = 60
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepara features para treinamento/predição
        
        Args:
            data: DataFrame com dados OHLCV
            lookback: Período de lookback
        
        Returns:
            Tuple com features e targets
        """
        try:
            # Calcular indicadores técnicos
            features = []
            
            for i in range(lookback, len(data)):
                # Features básicas
                row = data.iloc[i]
                basic_features = [
                    row['open'],
                    row['high'],
                    row['low'],
                    row['close'],
                    row['volume']
                ]
                
                # Features técnicas
                if i >= 20:
                    # Médias móveis
                    sma_20 = data.iloc[i-20:i]['close'].mean()
                    sma_50 = data.iloc[i-50:i]['close'].mean()
                    
                    # RSI
                    rsi = self._calculate_rsi(data.iloc[i-14:i]['close'])
                    
                    # Bandas de Bollinger
                    bb = self._calculate_bollinger_bands(data.iloc[i-20:i]['close'])
                    
                    technical_features = [
                        sma_20,
                        sma_50,
                        rsi,
                        bb['upper'],
                        bb['middle'],
                        bb['lower']
                    ]
                else:
                    technical_features = [0] * 6
                
                # Features temporais
                temporal_features = [
                    i / len(data),  # Posição relativa
                    pd.to_datetime(row.name).hour if hasattr(row.name, 'hour') else 0,
                    pd.to_datetime(row.name).dayofweek if hasattr(row.name, 'dayofweek') else 0
                ]
                
                # Combinar features
                all_features = basic_features + technical_features + temporal_features
                features.append(all_features)
            
            # Converter para arrays
            X = np.array(features[:-1])  # Todas menos última
            y = np.array([data['close'].iloc[i] for i in range(lookback, len(data))])
            
            # Normalizar features
            if len(X) > 0:
                X_scaled = self.scalers["price"].fit_transform(X)
            else:
                X_scaled = X
            
            self.logger.info(f"Prepared features: X{X_scaled.shape}, y{y.shape}")
            return X_scaled, y
            
        except Exception as e:
            self.logger.error(f"Feature preparation error: {e}")
            return np.array([]), np.array([])
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calcula RSI"""
        if len(prices) < period + 1:
            return 50.0
        
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50.0
    
    def _calculate_bollinger_bands(
        self,
        prices: pd.Series,
        period: int = 20,
        std_dev: float = 2.0
    ) -> Dict[str, float]:
        """Calcula Bandas de Bollinger"""
        if len(prices) < period:
            return {"upper": 0.0, "middle": 0.0, "lower": 0.0}
        
        middle = prices.rolling(window=period).mean().iloc[-1]
        std = prices.rolling(window=period).std().iloc[-1]
        
        return {
            "upper": middle + (std_dev * std),
            "middle": middle,
            "lower": middle - (std_dev * std)
        }
    
    @log_execution(
        component="predictor",
        operation="train_model",
        log_args=True,
        log_result=True
    )
    async def train_model(
        self,
        symbol: str,
        data: pd.DataFrame,
        model_name: str = "lstm_btc",
        epochs: int = None
    ) -> bool:
        """
        Treina modelo específico
        
        Args:
            symbol: Símbolo do ativo
            data: Dados de treinamento
            model_name: Nome do modelo
            epochs: Número de épocas
        
        Returns:
            True se treinamento bem-sucedido
        """
        try:
            if model_name not in self.models:
                self.logger.error(f"Model {model_name} not found")
                return False
            
            model = self.models[model_name]
            epochs = epochs or settings.ml_epochs
            
            # Preparar features
            X, y = self.prepare_features(data)
            
            if len(X) == 0 or len(y) == 0:
                self.logger.error("Insufficient data for training")
                return False
            
            # Converter para tensores
            X_tensor = torch.FloatTensor(X).to(self.device)
            y_tensor = torch.FloatTensor(y).to(self.device)
            
            # Dividir em treino/validação
            split_idx = int(0.8 * len(X_tensor))
            X_train, X_val = X_tensor[:split_idx], X_tensor[split_idx:]
            y_train, y_val = y_tensor[:split_idx], y_tensor[split_idx:]
            
            # Configurar otimizador e loss
            optimizer = torch.optim.Adam(model.parameters(), lr=self.learning_rate)
            criterion = nn.MSELoss()
            
            # Loop de treinamento
            model.train()
            for epoch in range(epochs):
                # Forward pass
                outputs = model(X_train.unsqueeze(1))  # Adicionar dimensão de sequência
                loss = criterion(outputs.squeeze(), y_train)
                
                # Backward pass
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
                # Validação
                model.eval()
                with torch.no_grad():
                    val_outputs = model(X_val.unsqueeze(1))
                    val_loss = criterion(val_outputs.squeeze(), y_val)
                
                # Métricas
                mse = loss.item()
                val_mse = val_loss.item()
                
                self.performance_metrics["mse"].append(mse)
                
                if epoch % 10 == 0:
                    self.logger.info(
                        f"Epoch {epoch}: Train MSE={mse:.6f}, Val MSE={val_mse:.6f}"
                    )
            
            self.logger.info(f"Model {model_name} trained successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Training error for {model_name}: {e}")
            return False
    
    @log_execution(
        component="predictor",
        operation="predict_price",
        log_args=True,
        log_result=True
    )
    async def predict_price(
        self,
        symbol: str,
        data: pd.DataFrame,
        horizon: str = "1h",
        model_name: str = "lstm_btc"
    ) -> Optional[PredictionResult]:
        """
        Realiza predição de preço
        
        Args:
            symbol: Símbolo do ativo
            data: Dados recentes
            horizon: Horizonte de predição
            model_name: Nome do modelo
        
        Returns:
            Resultado da predição ou None
        """
        try:
            if model_name not in self.models:
                self.logger.error(f"Model {model_name} not found")
                return None
            
            model = self.models[model_name]
            
            # Preparar features
            X, _ = self.prepare_features(data.tail(100))
            
            if len(X) == 0:
                self.logger.error("Insufficient data for prediction")
                return None
            
            # Converter para tensor
            X_tensor = torch.FloatTensor(X[-1:]).to(self.device)
            
            # Predição
            model.eval()
            with torch.no_grad():
                prediction = model(X_tensor.unsqueeze(1))
                predicted_price = prediction.item()
            
            # Calcular confiança baseada na performance histórica
            confidence = self._calculate_prediction_confidence(model_name)
            
            # Criar resultado
            result = PredictionResult(
                symbol=symbol,
                prediction_type=PredictionType.PRICE,
                timestamp=datetime.now(),
                prediction=predicted_price,
                confidence=confidence,
                horizon=horizon,
                features_used=["OHLCV", "SMA", "RSI", "BB"],
                model_name=model_name,
                metrics={"last_mse": self._get_last_metric(model_name, "mse")}
            )
            
            # Adicionar ao cache
            if symbol not in self.prediction_cache:
                self.prediction_cache[symbol] = []
            self.prediction_cache[symbol].append(result)
            
            # Limitar cache
            if len(self.prediction_cache[symbol]) > 100:
                self.prediction_cache[symbol] = self.prediction_cache[symbol][-50:]
            
            self.logger.info(f"Price prediction for {symbol}: {predicted_price:.2f}")
            return result
            
        except Exception as e:
            self.logger.error(f"Prediction error for {symbol}: {e}")
            return None
    
    def _calculate_prediction_confidence(self, model_name: str) -> float:
        """Calcula confiança da predição baseada na performance"""
        last_mse = self._get_last_metric(model_name, "mse")
        
        if last_mse is None or last_mse == 0:
            return 0.5
        
        # Converter MSE para confiança (inverso)
        confidence = max(0.1, min(0.9, 1.0 / (1.0 + last_mse)))
        return confidence
    
    def _get_last_metric(self, model_name: str, metric: str) -> Optional[float]:
        """Obtém última métrica de performance"""
        if model_name in self.performance_metrics:
            metrics = self.performance_metrics[model_name]
            return metrics[-1] if metrics else None
        return None
    
    @log_execution(
        component="predictor",
        operation="ensemble_prediction",
        log_args=True,
        log_result=True
    )
    async def ensemble_prediction(
        self,
        symbol: str,
        data: pd.DataFrame,
        horizon: str = "1h"
    ) -> Optional[PredictionResult]:
        """
        Realiza predição usando ensemble de modelos
        
        Args:
            symbol: Símbolo do ativo
            data: Dados recentes
            horizon: Horizonte de predição
        
        Returns:
            Resultado da predição ensemble ou None
        """
        try:
            # Preparar features
            X, y = self.prepare_features(data.tail(100))
            
            if len(X) == 0 or len(y) == 0:
                self.logger.error("Insufficient data for ensemble prediction")
                return None
            
            # Treinar modelos de ensemble
            if SKLEARN_AVAILABLE:
                for name, model in self.ensemble_models.items():
                    model.fit(X, y)
            
            # Obter predições individuais
            predictions = []
            confidences = []
            
            # Predições dos modelos de deep learning
            for model_name in ["lstm_btc", "transformer_eth"]:
                if model_name in self.models:
                    pred = await self.predict_price(symbol, data, horizon, model_name)
                    if pred:
                        predictions.append(pred.prediction)
                        confidences.append(pred.confidence)
            
            # Predições dos modelos de ensemble
            if SKLEARN_AVAILABLE:
                X_last = X[-1:] if len(X) > 1 else X
                for name, model in self.ensemble_models.items():
                    pred = model.predict(X_last)
                    predictions.append(pred[0] if len(pred) > 0 else 0)
                    confidences.append(0.7)  # Confiança padrão para ensemble
            
            # Calcular predição ensemble (média ponderada)
            if predictions:
                weights = np.array(confidences)
                weighted_prediction = np.average(predictions, weights=weights)
                
                # Calcular confiança ensemble
                ensemble_confidence = np.mean(confidences)
                
                result = PredictionResult(
                    symbol=symbol,
                    prediction_type=PredictionType.PRICE,
                    timestamp=datetime.now(),
                    prediction=weighted_prediction,
                    confidence=ensemble_confidence,
                    horizon=horizon,
                    features_used=["OHLCV", "SMA", "RSI", "BB"],
                    model_name="ensemble",
                    metrics={"ensemble_size": len(predictions)}
                )
                
                self.logger.info(f"Ensemble prediction for {symbol}: {weighted_prediction:.2f}")
                return result
            
            return None
            
        except Exception as e:
            self.logger.error(f"Ensemble prediction error for {symbol}: {e}")
            return None
    
    @log_execution(
        component="predictor",
        operation="run_backtest",
        log_args=True,
        log_result=True
    )
    async def run_backtest(
        self,
        symbol: str,
        data: pd.DataFrame,
        strategy_name: str = "simple_ma_crossover",
        initial_capital: float = 10000.0
    ) -> Optional[BacktestResult]:
        """
        Executa backtest de estratégia
        
        Args:
            symbol: Símbolo do ativo
            data: Dados históricos
            strategy_name: Nome da estratégia
            initial_capital: Capital inicial
        
        Returns:
            Resultado do backtest ou None
        """
        try:
            if not BACKTRADER_AVAILABLE:
                self.logger.warning("Backtrader not available")
                return None
            
            # Criar estratégia simples
            class SimpleMAStrategy(bt.Strategy):
                params = (
                    ('maperiod', 20),
                    ('long_period', 50)
                )
                
                def __init__(self):
                    self.sma_short = bt.indicators.SimpleMovingAverage(
                        self.data.close, period=self.p.maperiod
                    )
                    self.sma_long = bt.indicators.SimpleMovingAverage(
                        self.data.close, period=self.p.long_period
                    )
                
                def next(self):
                    if not self.position:
                        if self.sma_short[0] > self.sma_long[0]:
                            self.buy()
                    else:
                        self.close()
            
            # Configurar backtest
            cerebro = bt.Cerebro()
            
            # Adicionar dados
            data_bt = bt.feeds.PandasData(
                dataname=data,
                datetime=None,
                open='open',
                high='high',
                low='low',
                close='close',
                volume='volume',
                openinterest=None
            )
            
            cerebro.adddata(data_bt)
            
            # Adicionar estratégia
            cerebro.addstrategy(SimpleMAStrategy)
            
            # Configurar capital inicial
            cerebro.broker.setcash(initial_capital)
            
            # Configurar comissão
            cerebro.broker.setcommission(commission=0.001)  # 0.1%
            
            # Executar backtest
            results = cerebro.run()
            
            # Extrair resultados
            final_value = cerebro.broker.getvalue()
            total_return = (final_value - initial_capital) / initial_capital * 100
            
            # Calcular métricas
            strategy = results[0]
            
            # Calcular drawdown máximo
            drawdowns = []
            peak = initial_capital
            for value in strategy.analyzers._drawdown.drawdown.get():
                current_value = initial_capital + (value * total_return / 100)
                if current_value > peak:
                    peak = current_value
                else:
                    drawdown = (peak - current_value) / peak * 100
                    drawdowns.append(drawdown)
            
            max_drawdown = max(drawdowns) if drawdowns else 0
            
            # Calcular Sharpe ratio (simplificado)
            returns = strategy.analyzers._returns.get()
            if len(returns) > 1:
                avg_return = np.mean(returns)
                std_return = np.std(returns)
                sharpe_ratio = avg_return / std_return if std_return > 0 else 0
            else:
                sharpe_ratio = 0
            
            # Contar trades
            total_trades = len(strategy._trades)
            profitable_trades = len([t for t in strategy._trades if t.pnl > 0])
            win_rate = (profitable_trades / total_trades * 100) if total_trades > 0 else 0
            
            result = BacktestResult(
                symbol=symbol,
                strategy_name=strategy_name,
                start_date=data.index[0],
                end_date=data.index[-1],
                initial_capital=initial_capital,
                final_capital=final_value,
                total_return=total_return,
                sharpe_ratio=sharpe_ratio,
                max_drawdown=max_drawdown,
                win_rate=win_rate,
                total_trades=total_trades,
                profitable_trades=profitable_trades
            )
            
            self.logger.info(f"Backtest completed for {symbol}: {total_return:.2f}% return")
            return result
            
        except Exception as e:
            self.logger.error(f"Backtest error for {symbol}: {e}")
            return None
    
    def get_prediction_history(
        self,
        symbol: str,
        limit: int = 50
    ) -> List[PredictionResult]:
        """
        Obtém histórico de predições
        
        Args:
            symbol: Símbolo do ativo
            limit: Número de predições
        
        Returns:
            Lista de predições recentes
        """
        if symbol in self.prediction_cache:
            return self.prediction_cache[symbol][-limit:]
        return []
    
    def get_model_performance(self) -> Dict[str, Any]:
        """Retorna métricas de performance dos modelos"""
        performance = {}
        
        for model_name in self.models:
            performance[model_name] = {
                "mse": self._get_last_metric(model_name, "mse"),
                "mae": self._get_last_metric(model_name, "mae"),
                "predictions_count": len(self.prediction_cache.get(model_name.replace("_btc", "").replace("_eth", ""), []))
            }
        
        return performance
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status do preditor"""
        return {
            "models_loaded": len(self.models),
            "ensemble_models": len(self.ensemble_models),
            "cache_size": {
                symbol: len(predictions) for symbol, predictions in self.prediction_cache.items()
            },
            "device": str(self.device),
            "batch_size": self.batch_size,
            "learning_rate": self.learning_rate,
            "last_update": datetime.now().isoformat()
        }


# Instância global do preditor
_predictor: Optional[Predictor] = None


def get_predictor() -> Predictor:
    """Obtém instância global do Predictor"""
    global _predictor
    if _predictor is None:
        _predictor = Predictor()
    return _predictor


# Exportações principais
__all__ = [
    "Predictor",
    "PredictionResult",
    "BacktestResult",
    "LSTMModel",
    "TransformerModel",
    "PredictionType",
    "get_predictor"
]

# 06_prediction_engine.py
"""
Sistema VhalinorTrade - Motor de Predição
Combina múltiplos modelos para previsões de curto, médio e longo prazo
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

class PredictionHorizon(Enum):
    SHORT_TERM = "short"  # Minutos/Horas
    MEDIUM_TERM = "medium"  # Dias/Semanas
    LONG_TERM = "long"  # Meses/Anos

@dataclass
class PricePrediction:
    symbol: str
    current_price: float
    predicted_price: float
    expected_return: float
    confidence: float
    direction: str  # 'up' or 'down'
    prediction_horizon: PredictionHorizon
    timeframe: str
    supporting_factors: List[str]
    risk_score: float
    timestamp: datetime

class PredictionEngine:
    def __init__(self, config, neural_network, technical_analyzer, pattern_recognition):
        self.config = config
        self.neural_network = neural_network
        self.technical_analyzer = technical_analyzer
        self.pattern_recognition = pattern_recognition
        self.predictions_history = []
        
    async def generate_predictions(self, symbol: str,
                                  market_data: Dict[str, pd.DataFrame]
                                  ) -> List[PricePrediction]:
        """Gera predições para todos os horizontes temporais"""
        predictions = []
        
        for timeframe, df in market_data.items():
            # Predição de curto prazo
            if timeframe in ['1m', '5m', '15m']:
                short_pred = await self._short_term_prediction(
                    symbol, df, timeframe
                )
                if short_pred:
                    predictions.append(short_pred)
                    
            # Predição de médio prazo
            if timeframe in ['1h', '4h']:
                medium_pred = await self._medium_term_prediction(
                    symbol, df, timeframe
                )
                if medium_pred:
                    predictions.append(medium_pred)
                    
            # Predição de longo prazo
            if timeframe in ['1d', '1w']:
                long_pred = await self._long_term_prediction(
                    symbol, df, timeframe
                )
                if long_pred:
                    predictions.append(long_pred)
                    
        return predictions
    
    async def _short_term_prediction(self, symbol: str,
                                    df: pd.DataFrame,
                                    timeframe: str) -> Optional[PricePrediction]:
        """Predição de curto prazo (minutos/horas)"""
        current_price = df['close'].iloc[-1]
        
        # Análise técnica para curto prazo
        rsi = self.technical_analyzer.calculate_rsi(df['close'])
        macd = self.technical_analyzer.calculate_macd(df['close'])
        bb = self.technical_analyzer.calculate_bollinger_bands(df['close'])
        
        # Predição neural
        neural_pred = await self.neural_network.predict(symbol, df)
        
        # Padrões recentes
        patterns = self.pattern_recognition.extract_price_patterns(
            df, window_size=20
        )
        
        if neural_pred is None:
            return None
            
        # Combina sinais
        signals = []
        confidence_factors = []
        
        # RSI
        if rsi.iloc[-1] < 30:
            signals.append(1)  # Bullish
            confidence_factors.append(min(1.0, (30 - rsi.iloc[-1]) / 10))
        elif rsi.iloc[-1] > 70:
            signals.append(-1)  # Bearish
            confidence_factors.append(min(1.0, (rsi.iloc[-1] - 70) / 10))
        else:
            signals.append(0)
            confidence_factors.append(0.5)
            
        # MACD
        if macd['macd'].iloc[-1] > macd['signal'].iloc[-1]:
            signals.append(1)
        else:
            signals.append(-1)
        confidence_factors.append(
            abs(macd['histogram'].iloc[-1]) / df['close'].iloc[-1] * 100
        )
        
        # Bollinger Bands
        if df['close'].iloc[-1] < bb['lower'].iloc[-1]:
            signals.append(1)
            confidence_factors.append(0.8)
        elif df['close'].iloc[-1] > bb['upper'].iloc[-1]:
            signals.append(-1)
            confidence_factors.append(0.8)
        else:
            signals.append(0)
            confidence_factors.append(0.5)
            
        # Neural network
        neural_signal = 1 if neural_pred['direction_prediction'] > 0.5 else -1
        signals.append(neural_signal)
        confidence_factors.append(neural_pred['direction_confidence'])
        
        # Calcula sinal combinado
        weighted_signal = np.average(signals, weights=confidence_factors)
        confidence = np.mean(confidence_factors)
        
        # Calcula preço previsto
        expected_move = neural_pred['price_prediction']
        predicted_price = current_price * (1 + expected_move)
        
        supporting_factors = []
        if rsi.iloc[-1] < 30:
            supporting_factors.append("RSI Oversold")
        elif rsi.iloc[-1] > 70:
            supporting_factors.append("RSI Overbought")
            
        if macd['macd'].iloc[-1] > macd['signal'].iloc[-1]:
            supporting_factors.append("MACD Bullish")
        else:
            supporting_factors.append("MACD Bearish")
            
        if patterns:
            supporting_factors.append(f"Pattern similarity: {len(patterns)}")
            
        return PricePrediction(
            symbol=symbol,
            current_price=current_price,
            predicted_price=predicted_price,
            expected_return=expected_move,
            confidence=confidence,
            direction='up' if weighted_signal > 0 else 'down',
            prediction_horizon=PredictionHorizon.SHORT_TERM,
            timeframe=timeframe,
            supporting_factors=supporting_factors,
            risk_score=1 - confidence,
            timestamp=datetime.now()
        )
    
    async def _medium_term_prediction(self, symbol: str,
                                     df: pd.DataFrame,
                                     timeframe: str) -> Optional[PricePrediction]:
        """Predição de médio prazo (dias/semanas)"""
        current_price = df['close'].iloc[-1]
        
        # Features de médio prazo
        sma_20 = df['close'].rolling(20).mean()
        sma_50 = df['close'].rolling(50).mean()
        trend_strength = (sma_20.iloc[-1] - sma_50.iloc[-1]) / sma_50.iloc[-1]
        
        # Análise de volatilidade
        volatility = self.technical_analyzer.calculate_volatility_metrics(df)
        
        # Análise de padrões ocultos
        hidden_patterns = self.pattern_recognition.detect_hidden_patterns(df)
        
        # Combinação de fatores
        confidence = 0.0
        signals = []
        
        # Tendência
        if trend_strength > 0.02:
            signals.append(1)
            confidence += 0.3
        elif trend_strength < -0.02:
            signals.append(-1)
            confidence += 0.3
            
        # Expoente de Hurst
        if hidden_patterns['is_trending']:
            signals.append(np.sign(trend_strength))
            confidence += 0.2
        elif hidden_patterns['is_mean_reverting']:
            signals.append(-np.sign(trend_strength))
            confidence += 0.2
            
        # Previsão de preço baseada na tendência
        expected_return = trend_strength * 0.5  # Ajuste conservador
        predicted_price = current_price * (1 + expected_return)
        
        return PricePrediction(
            symbol=symbol,
            current_price=current_price,
            predicted_price=predicted_price,
            expected_return=expected_return,
            confidence=min(1.0, confidence),
            direction='up' if expected_return > 0 else 'down',
            prediction_horizon=PredictionHorizon.MEDIUM_TERM,
            timeframe=timeframe,
            supporting_factors=[
                f"Trend: {'Up' if trend_strength > 0 else 'Down'}",
                f"Hurst: {hidden_patterns['hurst_exponent']:.3f}",
                f"Vol: {volatility['historical_volatility']:.3f}"
            ],
            risk_score=0.5,
            timestamp=datetime.now()
        )
    
    async def _long_term_prediction(self, symbol: str,
                                   df: pd.DataFrame,
                                   timeframe: str) -> Optional[PricePrediction]:
        """Predição de longo prazo (meses/anos)"""
        if len(df) < 100:
            return None
            
        current_price = df['close'].iloc[-1]
        
        # Análise fundamental simulada (em produção, usar dados on-chain/reais)
        # Aqui usamos médias de longo prazo como proxy
        
        # Médias de longo prazo
        sma_200 = df['close'].rolling(200).mean()
        sma_50 = df['close'].rolling(50).mean()
        
        # Posição relativa às médias
        position_200 = (current_price - sma_200.iloc[-1]) / sma_200.iloc[-1]
        
        # Tendência de longo prazo
        long_trend = (sma_50.iloc[-1] - sma_50.iloc[-50]) / sma_50.iloc[-50]
        
        # Volatilidade histórica
        returns = df['close'].pct_change().dropna()
        sharpe_ratio = (returns.mean() * 365) / (returns.std() * np.sqrt(365))
        
        confidence = 0.0
        
        # Acima da SMA 200
        if position_200 > 0.05:
            confidence += 0.3
        elif position_200 < -0.05:
            confidence += 0.3
            
        # Sharpe ratio
        if sharpe_ratio > 1:
            confidence += 0.3
        elif sharpe_ratio < -1:
            confidence += 0.3
            
        # Tendência consistente
        if abs(long_trend) > 0.05:
            confidence += 0.3
            
        expected_return = position_200 * 0.3 + long_trend * 0.7
        predicted_price = current_price * (1 + expected_return)
        
        return PricePrediction(
            symbol=symbol,
            current_price=current_price,
            predicted_price=predicted_price,
            expected_return=expected_return,
            confidence=min(1.0, confidence),
            direction='up' if expected_return > 0 else 'down',
            prediction_horizon=PredictionHorizon.LONG_TERM,
            timeframe=timeframe,
            supporting_factors=[
                f"SMA200 position: {position_200:.2%}",
                f"Long trend: {long_trend:.2%}",
                f"Sharpe: {sharpe_ratio:.2f}"
            ],
            risk_score=0.5,
            timestamp=datetime.now()
        )
    
    def ensemble_prediction(self, predictions: List[PricePrediction]) -> Dict:
        """Combina múltiplas predições em um sinal consolidado"""
        if not predictions:
            return None
            
        # Pesos por horizonte
        horizon_weights = {
            PredictionHorizon.SHORT_TERM: 0.5,
            PredictionHorizon.MEDIUM_TERM: 0.3,
            PredictionHorizon.LONG_TERM: 0.2
        }
        
        total_weight = 0
        weighted_direction = 0
        weighted_return = 0
        total_confidence = 0
        
        for pred in predictions:
            weight = horizon_weights.get(pred.prediction_horizon, 0.1)
            signal = 1 if pred.direction == 'up' else -1
            
            weighted_direction += signal * weight * pred.confidence
            weighted_return += pred.expected_return * weight * pred.confidence
            total_confidence += pred.confidence * weight
            total_weight += weight
            
        if total_weight == 0:
            return None
            
        final_direction = 'up' if weighted_direction > 0 else 'down'
        final_confidence = total_confidence / total_weight
        final_return = weighted_return / total_weight
        
        # Gera sinal de trading
        signal = 'STRONG_BUY' if final_direction == 'up' and final_confidence > 0.7 else \
                 'BUY' if final_direction == 'up' and final_confidence > 0.5 else \
                 'STRONG_SELL' if final_direction == 'down' and final_confidence > 0.7 else \
                 'SELL' if final_direction == 'down' and final_confidence > 0.5 else \
                 'NEUTRAL'
                 
        return {
            'signal': signal,
            'direction': final_direction,
            'confidence': final_confidence,
            'expected_return': final_return,
            'predictions_used': len(predictions),
            'timestamp': datetime.now()
        }
# 03_technical_analysis.py
"""
Sistema VhalinorTrade - Análise Técnica Avançada
Indicadores, padrões gráficos e análise de mercado
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from scipy import stats
from scipy.signal import argrelextrema
import talib

@dataclass
class MarketAnalysis:
    trend: str  # 'bullish', 'bearish', 'neutral'
    strength: float  # 0-1
    volatility: float
    momentum: float
    support_levels: List[float]
    resistance_levels: List[float]
    patterns: List[str]
    signals: Dict[str, bool]

class TechnicalAnalyzer:
    def __init__(self, config):
        self.config = config
        
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calcula RSI com divergências"""
        return talib.RSI(prices.values, timeperiod=period)
    
    def calculate_macd(self, prices: pd.Series) -> Dict[str, pd.Series]:
        """Calcula MACD completo"""
        macd, signal, hist = talib.MACD(
            prices.values,
            fastperiod=12,
            slowperiod=26,
            signalperiod=9
        )
        return {
            'macd': pd.Series(macd, index=prices.index),
            'signal': pd.Series(signal, index=prices.index),
            'histogram': pd.Series(hist, index=prices.index)
        }
    
    def calculate_bollinger_bands(self, prices: pd.Series, 
                                  period: int = 20, std_dev: float = 2.0
                                  ) -> Dict[str, pd.Series]:
        """Calcula Bandas de Bollinger"""
        upper, middle, lower = talib.BBANDS(
            prices.values,
            timeperiod=period,
            nbdevup=std_dev,
            nbdevdn=std_dev,
            matype=0
        )
        return {
            'upper': pd.Series(upper, index=prices.index),
            'middle': pd.Series(middle, index=prices.index),
            'lower': pd.Series(lower, index=prices.index)
        }
    
    def calculate_atr(self, high: pd.Series, low: pd.Series, 
                     close: pd.Series, period: int = 14) -> pd.Series:
        """Average True Range para volatilidade"""
        return pd.Series(
            talib.ATR(high.values, low.values, close.values, timeperiod=period),
            index=close.index
        )
    
    def detect_support_resistance(self, df: pd.DataFrame, 
                                  window: int = 20) -> Tuple[List[float], List[float]]:
        """Detecta níveis de suporte e resistência usando método avançado"""
        highs = df['high'].values
        lows = df['low'].values
        
        # Encontra máximos e mínimos locais
        local_max_idx = argrelextrema(highs, np.greater, order=window)[0]
        local_min_idx = argrelextrema(lows, np.less, order=window)[0]
        
        # Agrupa níveis próximos
        resistance_levels = self._cluster_levels(highs[local_max_idx])
        support_levels = self._cluster_levels(lows[local_min_idx])
        
        return support_levels, resistance_levels
    
    def _cluster_levels(self, levels: np.ndarray, threshold: float = 0.02) -> List[float]:
        """Agrupa níveis de preço próximos"""
        if len(levels) == 0:
            return []
            
        levels = np.sort(levels)
        clusters = []
        current_cluster = [levels[0]]
        
        for i in range(1, len(levels)):
            if abs(levels[i] - current_cluster[-1]) / current_cluster[-1] <= threshold:
                current_cluster.append(levels[i])
            else:
                clusters.append(np.mean(current_cluster))
                current_cluster = [levels[i]]
                
        clusters.append(np.mean(current_cluster))
        return clusters
    
    def detect_candlestick_patterns(self, df: pd.DataFrame) -> List[str]:
        """Detecta padrões de candlestick"""
        patterns = []
        
        # Verifica diversos padrões
        pattern_functions = {
            'doji': talib.CDLDOJI,
            'hammer': talib.CDLHAMMER,
            'engulfing_bullish': talib.CDLENGULFING,
            'morning_star': talib.CDLMORNINGSTAR,
            'three_white_soldiers': talib.CDL3WHITESOLDIERS,
            'dark_cloud_cover': talib.CDLDARKCLOUDCOVER,
            'evening_star': talib.CDLEVENINGSTAR,
            'three_black_crows': talib.CDL3BLACKCROWS
        }
        
        for pattern_name, pattern_func in pattern_functions.items():
            result = pattern_func(
                df['open'].values,
                df['high'].values,
                df['low'].values,
                df['close'].values
            )
            if result[-1] != 0:
                patterns.append(pattern_name)
                
        return patterns
    
    def detect_chart_patterns(self, df: pd.DataFrame) -> List[str]:
        """Detecta padrões gráficos maiores"""
        patterns = []
        highs = df['high'].values
        lows = df['low'].values
        
        # Head and Shoulders
        if self._detect_head_and_shoulders(highs, lows):
            patterns.append('head_and_shoulders')
            
        # Double Top
        if self._detect_double_pattern(highs, 'top'):
            patterns.append('double_top')
            
        # Double Bottom
        if self._detect_double_pattern(lows, 'bottom'):
            patterns.append('double_bottom')
            
        # Triangle
        if self._detect_triangle(df):
            patterns.append('triangle')
            
        # Wedge
        if self._detect_wedge(df):
            patterns.append('wedge')
            
        return patterns
    
    def _detect_head_and_shoulders(self, highs: np.ndarray, 
                                   lows: np.ndarray) -> bool:
        """Detecta padrão Head and Shoulders"""
        window = len(highs) // 3
        if window < 5:
            return False
            
        local_max = argrelextrema(highs, np.greater, order=window)[0]
        
        if len(local_max) >= 3:
            last_three = local_max[-3:]
            if len(last_three) == 3:
                left_shoulder = highs[last_three[0]]
                head = highs[last_three[1]]
                right_shoulder = highs[last_three[2]]
                
                if head > left_shoulder and head > right_shoulder:
                    if abs(left_shoulder - right_shoulder) / left_shoulder < 0.1:
                        return True
                        
        return False
    
    def _detect_double_pattern(self, values: np.ndarray, 
                              pattern_type: str) -> bool:
        """Detecta padrões de topo/fundo duplo"""
        window = len(values) // 4
        if window < 3:
            return False
            
        if pattern_type == 'top':
            extrema = argrelextrema(values, np.greater, order=window)[0]
        else:
            extrema = argrelextrema(values, np.less, order=window)[0]
            
        if len(extrema) >= 2:
            last_two = extrema[-2:]
            if len(last_two) == 2:
                if abs(values[last_two[0]] - values[last_two[1]]) / values[last_two[0]] < 0.03:
                    return True
                    
        return False
    
    def calculate_volatility_metrics(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calcula métricas avançadas de volatilidade"""
        returns = df['close'].pct_change().dropna()
        
        return {
            'historical_volatility': returns.std() * np.sqrt(365),
            'parkinson_volatility': self._parkinson_volatility(df),
            'garman_klass_volatility': self._garman_klass_volatility(df),
            'yang_zhang_volatility': self._yang_zhang_volatility(df),
            'skewness': returns.skew(),
            'kurtosis': returns.kurtosis()
        }
    
    def _parkinson_volatility(self, df: pd.DataFrame) -> float:
        """Volatilidade de Parkinson (usa high-low)"""
        hl_ratio = np.log(df['high'] / df['low'])
        return np.sqrt(1 / (4 * np.log(2)) * hl_ratio.var() * 365)
    
    def _garman_klass_volatility(self, df: pd.DataFrame) -> float:
        """Volatilidade de Garman-Klass"""
        log_ho = np.log(df['high'] / df['open'])
        log_lo = np.log(df['low'] / df['open'])
        log_co = np.log(df['close'] / df['open'])
        
        variance = 0.5 * log_ho - log_lo - (2 * np.log(2) - 1) * log_co**2
        return np.sqrt(variance.mean() * 365)
    
    def _yang_zhang_volatility(self, df: pd.DataFrame) -> float:
        """Volatilidade de Yang-Zhang (considera gaps)"""
        log_oc = np.log(df['open'] / df['close'].shift(1))
        log_co = np.log(df['close'] / df['open'])
        log_ho = np.log(df['high'] / df['open'])
        log_lo = np.log(df['low'] / df['open'])
        
        k = 0.34 / (1.34 + (len(df) + 1) / (len(df) - 1))
        
        overnight_vol = log_oc.var()
        open_close_vol = log_co.var()
        rs_vol = self._parkinson_volatility(df)
        
        return np.sqrt(overnight_vol + k * open_close_vol + (1 - k) * rs_vol)
    
    def full_market_analysis(self, df: pd.DataFrame) -> MarketAnalysis:
        """Análise completa de mercado"""
        close = df['close']
        
        # Tendência
        sma_20 = close.rolling(20).mean()
        sma_50 = close.rolling(50).mean()
        
        if sma_20.iloc[-1] > sma_50.iloc[-1]:
            trend = 'bullish'
            strength = min(1.0, (sma_20.iloc[-1] / sma_50.iloc[-1] - 1) * 10)
        elif sma_20.iloc[-1] < sma_50.iloc[-1]:
            trend = 'bearish'
            strength = min(1.0, (1 - sma_20.iloc[-1] / sma_50.iloc[-1]) * 10)
        else:
            trend = 'neutral'
            strength = 0.0
            
        # RSI
        rsi = self.calculate_rsi(close)
        
        # MACD
        macd_data = self.calculate_macd(close)
        
        # Suporte e Resistência
        support, resistance = self.detect_support_resistance(df)
        
        # Padrões
        candlestick_patterns = self.detect_candlestick_patterns(df)
        chart_patterns = self.detect_chart_patterns(df)
        all_patterns = candlestick_patterns + chart_patterns
        
        # Sinais
        signals = {
            'rsi_oversold': rsi.iloc[-1] < 30,
            'rsi_overbought': rsi.iloc[-1] > 70,
            'macd_bullish_cross': (macd_data['macd'].iloc[-1] > 
                                  macd_data['signal'].iloc[-1] and 
                                  macd_data['macd'].iloc[-2] <= 
                                  macd_data['signal'].iloc[-2]),
            'macd_bearish_cross': (macd_data['macd'].iloc[-1] < 
                                  macd_data['signal'].iloc[-1] and 
                                  macd_data['macd'].iloc[-2] >= 
                                  macd_data['signal'].iloc[-2]),
            'price_above_sma20': close.iloc[-1] > sma_20.iloc[-1],
            'price_above_sma50': close.iloc[-1] > sma_50.iloc[-1]
        }
        
        volatility_metrics = self.calculate_volatility_metrics(df)
        
        return MarketAnalysis(
            trend=trend,
            strength=strength,
            volatility=volatility_metrics['historical_volatility'],
            momentum=macd_data['histogram'].iloc[-1],
            support_levels=support,
            resistance_levels=resistance,
            patterns=all_patterns,
            signals=signals
        )
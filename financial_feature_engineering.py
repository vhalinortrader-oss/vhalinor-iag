"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║              PIPELINE DE ENGENHARIA DE FEATURES FINANCEIRAS                    ║
║                 Componente 3: Feature Engineering Financeiro                     ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import asyncio
import numpy as np
import pandas as pd
from scipy import stats, signal
from scipy.fft import fft, fftfreq
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import talib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import warnings
import json
import pickle
from concurrent.futures import ThreadPoolExecutor
import threading
from collections import deque, defaultdict
import time

# Import dos módulos anteriores
from market_data_infrastructure import MarketDataPoint, DataFrequency, DataType
from data_preprocessing_system import DataPreprocessingPipeline

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('FinancialFeatureEngineering')

class FeatureType(Enum):
    """Tipos de features financeiras"""
    TECHNICAL_INDICATORS = "technical_indicators"
    STATISTICAL_FEATURES = "statistical_features"
    MICROSTRUCTURE_FEATURES = "microstructure_features"
    FREQUENCY_DOMAIN_FEATURES = "frequency_domain_features"
    VOLATILITY_FEATURES = "volatility_features"
    MOMENTUM_FEATURES = "momentum_features"
    VOLUME_FEATURES = "volume_features"
    PRICE_FEATURES = "price_features"
    TIME_FEATURES = "time_features"
    SENTIMENT_FEATURES = "sentiment_features"

class FeatureCategory(Enum):
    """Categorias de features"""
    TREND = "trend"
    MOMENTUM = "momentum"
    VOLATILITY = "volatility"
    VOLUME = "volume"
    PRICE_ACTION = "price_action"
    MARKET_MICROSTRUCTURE = "market_microstructure"
    FREQUENCY_ANALYSIS = "frequency_analysis"
    STATISTICAL = "statistical"
    TEMPORAL = "temporal"

@dataclass
class FeatureDefinition:
    """Definição de uma feature"""
    name: str
    feature_type: FeatureType
    category: FeatureCategory
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    output_shape: str = "scalar"  # scalar, vector, matrix
    is_lag_feature: bool = False
    lag_periods: int = 0
    importance_score: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'feature_type': self.feature_type.value,
            'category': self.category.value,
            'description': self.description,
            'parameters': self.parameters,
            'dependencies': self.dependencies,
            'output_shape': self.output_shape,
            'is_lag_feature': self.is_lag_feature,
            'lag_periods': self.lag_periods,
            'importance_score': self.importance_score
        }

@dataclass
class FeatureSet:
    """Conjunto de features geradas"""
    symbol: str
    timestamp: datetime
    features: Dict[str, float]
    feature_metadata: Dict[str, FeatureDefinition]
    quality_score: float = 1.0
    missing_features: List[str] = field(default_factory=list)
    computation_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'symbol': self.symbol,
            'timestamp': self.timestamp.isoformat(),
            'features': self.features,
            'feature_metadata': {k: v.to_dict() for k, v in self.feature_metadata.items()},
            'quality_score': self.quality_score,
            'missing_features': self.missing_features,
            'computation_time': self.computation_time
        }

class TechnicalIndicators:
    """Calculadora de indicadores técnicos"""
    
    def __init__(self):
        self.indicators_cache = {}
        logger.info("📈 Calculadora de indicadores técnicos inicializada")
    
    def calculate_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula todos os indicadores técnicos disponíveis"""
        result_df = df.copy()
        
        # Indicadores de Trend
        result_df = self._calculate_trend_indicators(result_df)
        
        # Indicadores de Momentum
        result_df = self._calculate_momentum_indicators(result_df)
        
        # Indicadores de Volatilidade
        result_df = self._calculate_volatility_indicators(result_df)
        
        # Indicadores de Volume
        result_df = self._calculate_volume_indicators(result_df)
        
        # Indicadores de Price Action
        result_df = self._calculate_price_action_indicators(result_df)
        
        return result_df
    
    def _calculate_trend_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula indicadores de tendência"""
        if 'close_price' not in df.columns:
            return df
        
        close = df['close_price'].values
        
        # Moving Averages
        for period in [5, 10, 20, 50, 100, 200]:
            df[f'sma_{period}'] = talib.SMA(close, timeperiod=period)
            df[f'ema_{period}'] = talib.EMA(close, timeperiod=period)
        
        # Weighted Moving Average
        df['wma_20'] = talib.WMA(close, timeperiod=20)
        
        # Double Exponential Moving Average
        df['dema_20'] = talib.DEMA(close, timeperiod=20)
        
        # Triple Exponential Moving Average
        df['tema_20'] = talib.TEMA(close, timeperiod=20)
        
        # Hull Moving Average
        df['hma_20'] = self._calculate_hma(close, 20)
        
        # Kaufman's Adaptive Moving Average
        df['kama_20'] = talib.KAMA(close, timeperiod=20)
        
        # MESA Adaptive Moving Average
        df['mama'] = talib.MAMA(close)[0]
        df['fama'] = talib.MAMA(close)[1]
        
        # Parabolic SAR
        if 'high_price' in df.columns and 'low_price' in df.columns:
            high = df['high_price'].values
            low = df['low_price'].values
            df['sar'] = talib.SAR(high, low)
        
        # Bollinger Bands
        df['bb_upper'], df['bb_middle'], df['bb_lower'] = talib.BBANDS(close, timeperiod=20)
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        df['bb_position'] = (close - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        # Ichimoku Cloud
        if 'high_price' in df.columns and 'low_price' in df.columns:
            high = df['high_price'].values
            low = df['low_price'].values
            df['ichimoku_tenkan'], df['ichimoku_kijun'], df['ichimoku_senkou_a'], df['ichimoku_senkou_b'] = talib.ICHIMOKU(high, low)
        
        return df
    
    def _calculate_momentum_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula indicadores de momentum"""
        if 'close_price' not in df.columns:
            return df
        
        close = df['close_price'].values
        
        # RSI
        for period in [7, 14, 21]:
            df[f'rsi_{period}'] = talib.RSI(close, timeperiod=period)
        
        # Stochastic Oscillator
        if 'high_price' in df.columns and 'low_price' in df.columns:
            high = df['high_price'].values
            low = df['low_price'].values
            df['stoch_k'], df['stoch_d'] = talib.STOCH(high, low, close)
            df['stoch_rsi_k'], df['stoch_rsi_d'] = talib.STOCHRSI(close)
        
        # MACD
        df['macd'], df['macd_signal'], df['macd_hist'] = talib.MACD(close)
        
        # Momentum
        for period in [10, 20]:
            df[f'momentum_{period}'] = talib.MOM(close, timeperiod=period)
        
        # Rate of Change
        for period in [10, 20]:
            df[f'roc_{period}'] = talib.ROC(close, timeperiod=period)
            df[f'rocp_{period}'] = talib.ROCP(close, timeperiod=period)
        
        # Williams %R
        if 'high_price' in df.columns and 'low_price' in df.columns:
            high = df['high_price'].values
            low = df['low_price'].values
            df['williams_r'] = talib.WILLR(high, low, close)
        
        # Commodity Channel Index
        if 'high_price' in df.columns and 'low_price' in df.columns and 'volume' in df.columns:
            high = df['high_price'].values
            low = df['low_price'].values
            volume = df['volume'].values
            df['cci'] = talib.CCI(high, low, close)
        
        # ADX
        if 'high_price' in df.columns and 'low_price' in df.columns:
            high = df['high_price'].values
            low = df['low_price'].values
            df['adx'] = talib.ADX(high, low, close)
            df['di_plus'] = talib.PLUS_DI(high, low, close)
            df['di_minus'] = talib.MINUS_DI(high, low, close)
        
        # Aroon
        if 'high_price' in df.columns and 'low_price' in df.columns:
            high = df['high_price'].values
            low = df['low_price'].values
            df['aroon_up'], df['aroon_down'] = talib.AROON(high, low)
            df['aroon_osc'] = talib.AROONOSC(high, low)
        
        return df
    
    def _calculate_volatility_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula indicadores de volatilidade"""
        if 'close_price' not in df.columns:
            return df
        
        close = df['close_price'].values
        
        # Average True Range
        if 'high_price' in df.columns and 'low_price' in df.columns:
            high = df['high_price'].values
            low = df['low_price'].values
            df['atr_14'] = talib.ATR(high, low, close, timeperiod=14)
            df['natr_14'] = talib.NATR(high, low, close, timeperiod=14)
        
        # Historical Volatility
        for period in [10, 20, 30]:
            df[f'hist_vol_{period}'] = self._calculate_historical_volatility(close, period)
        
        # Garman-Klass Volatility
        if 'high_price' in df.columns and 'low_price' in df.columns and 'open_price' in df.columns:
            high = df['high_price'].values
            low = df['low_price'].values
            open_price = df['open_price'].values
            df['gk_volatility'] = self._calculate_garman_klass_volatility(high, low, close, open_price)
        
        # Parkinson Volatility
        if 'high_price' in df.columns and 'low_price' in df.columns:
            high = df['high_price'].values
            low = df['low_price'].values
            df['parkinson_volatility'] = self._calculate_parkinson_volatility(high, low)
        
        # Yang-Zhang Volatility
        if all(col in df.columns for col in ['high_price', 'low_price', 'open_price', 'close_price']):
            high = df['high_price'].values
            low = df['low_price'].values
            open_price = df['open_price'].values
            df['yang_zhang_volatility'] = self._calculate_yang_zhang_volatility(high, low, close, open_price)
        
        return df
    
    def _calculate_volume_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula indicadores de volume"""
        if 'volume' not in df.columns:
            return df
        
        volume = df['volume'].values
        
        # On-Balance Volume
        if 'close_price' in df.columns:
            close = df['close_price'].values
            df['obv'] = talib.OBV(close, volume)
        
        # Volume Weighted Average Price (VWAP)
        if all(col in df.columns for col in ['high_price', 'low_price', 'close_price']):
            high = df['high_price'].values
            low = df['low_price'].values
            close = df['close_price'].values
            df['vwap'] = self._calculate_vwap(high, low, close, volume)
        
        # Volume Moving Averages
        for period in [10, 20, 50]:
            df[f'volume_sma_{period}'] = talib.SMA(volume, timeperiod=period)
            df[f'volume_ema_{period}'] = talib.EMA(volume, timeperiod=period)
        
        # Volume Rate of Change
        for period in [10, 20]:
            df[f'volume_roc_{period}'] = talib.ROC(volume, timeperiod=period)
        
        # Accumulation/Distribution Line
        if all(col in df.columns for col in ['high_price', 'low_price', 'close_price']):
            high = df['high_price'].values
            low = df['low_price'].values
            close = df['close_price'].values
            df['ad_line'] = talib.AD(high, low, close, volume)
            df['ad_osc'] = talib.ADOSC(high, low, close, volume)
        
        # Chaikin Money Flow
        if all(col in df.columns for col in ['high_price', 'low_price', 'close_price']):
            high = df['high_price'].values
            low = df['low_price'].values
            close = df['close_price'].values
            df['cmf'] = self._calculate_chaikin_money_flow(high, low, close, volume)
        
        # Ease of Movement
        if all(col in df.columns for col in ['high_price', 'low_price', 'close_price']):
            high = df['high_price'].values
            low = df['low_price'].values
            close = df['close_price'].values
            df['eom'] = talib.ADOSC(high, low, close, volume, fastperiod=14, slowperiod=28)
        
        return df
    
    def _calculate_price_action_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula indicadores de price action"""
        if not all(col in df.columns for col in ['open_price', 'high_price', 'low_price', 'close_price']):
            return df
        
        open_price = df['open_price'].values
        high = df['high_price'].values
        low = df['low_price'].values
        close = df['close_price'].values
        
        # Price Change
        df['price_change'] = np.concatenate([[0], np.diff(close)])
        df['price_change_pct'] = np.concatenate([[0], np.diff(close) / close[:-1]])
        
        # High-Low Spread
        df['hl_spread'] = high - low
        df['hl_spread_pct'] = (high - low) / close
        
        # Open-Close Spread
        df['oc_spread'] = close - open_price
        df['oc_spread_pct'] = (close - open_price) / open_price
        
        # True Range
        df['true_range'] = talib.TRANGE(high, low, close)
        
        # Average Price
        df['avg_price'] = (high + low + close) / 3
        df['median_price'] = (high + low) / 2
        df['typical_price'] = (high + low + close) / 3
        df['weighted_close'] = (high + low + 2 * close) / 4
        
        # Candlestick Patterns
        df['doji'] = talib.CDLDOJI(open_price, high, low, close)
        df['hammer'] = talib.CDLHAMMER(open_price, high, low, close)
        df['engulfing'] = talib.CDLENGULFING(open_price, high, low, close)
        df['harami'] = talib.CDLHARAMI(open_price, high, low, close)
        df['morning_star'] = talib.CDLMORNINGSTAR(open_price, high, low, close)
        df['evening_star'] = talib.CDLEVENINGSTAR(open_price, high, low, close)
        
        return df
    
    def _calculate_hma(self, data: np.ndarray, period: int) -> np.ndarray:
        """Calcula Hull Moving Average"""
        half_period = period // 2
        sqrt_period = int(np.sqrt(period))
        
        wma_half = talib.WMA(data, timeperiod=half_period)
        wma_full = talib.WMA(data, timeperiod=period)
        
        raw_hma = 2 * wma_half - wma_full
        hma = talib.WMA(raw_hma, timeperiod=sqrt_period)
        
        return hma
    
    def _calculate_historical_volatility(self, prices: np.ndarray, period: int) -> np.ndarray:
        """Calcula volatilidade histórica"""
        log_returns = np.log(prices[1:] / prices[:-1])
        log_returns = np.concatenate([[0], log_returns])
        
        volatility = pd.Series(log_returns).rolling(window=period).std() * np.sqrt(252)
        return volatility.values
    
    def _calculate_garman_klass_volatility(self, high: np.ndarray, low: np.ndarray, 
                                         close: np.ndarray, open_price: np.ndarray) -> np.ndarray:
        """Calcula volatilidade de Garman-Klass"""
        log_hl = np.log(high / low)
        log_co = np.log(close / open_price)
        
        gk_vol = 0.5 * log_hl**2 - (2 * np.log(2) - 1) * log_co**2
        return np.sqrt(gk_vol)
    
    def _calculate_parkinson_volatility(self, high: np.ndarray, low: np.ndarray) -> np.ndarray:
        """Calcula volatilidade de Parkinson"""
        log_hl = np.log(high / low)
        parkinson_vol = (1 / (4 * np.log(2))) * log_hl**2
        return np.sqrt(parkinson_vol)
    
    def _calculate_yang_zhang_volatility(self, high: np.ndarray, low: np.ndarray, 
                                       close: np.ndarray, open_price: np.ndarray) -> np.ndarray:
        """Calcula volatilidade de Yang-Zhang"""
        log_hl = np.log(high / low)
        log_co = np.log(close / open_price)
        log_oc_prev = np.log(open_price[1:] / close[:-1])
        log_oc_prev = np.concatenate([[0], log_oc_prev])
        
        k = 0.34 / (1.34 + (20 + 1) / (20 - 1))
        
        rs = log_hl**2
        close_open = log_co**2
        open_close = log_oc_prev**2
        
        yz_vol = rs + k * close_open + (1 - k) * open_close
        return np.sqrt(yz_vol)
    
    def _calculate_vwap(self, high: np.ndarray, low: np.ndarray, close: np.ndarray, volume: np.ndarray) -> np.ndarray:
        """Calcula Volume Weighted Average Price"""
        typical_price = (high + low + close) / 3
        vwap = (typical_price * volume).cumsum() / volume.cumsum()
        return vwap
    
    def _calculate_chaikin_money_flow(self, high: np.ndarray, low: np.ndarray, 
                                     close: np.ndarray, volume: np.ndarray, period: int = 20) -> np.ndarray:
        """Calcula Chaikin Money Flow"""
        money_flow_multiplier = ((close - low) - (high - close)) / (high - low)
        money_flow_volume = money_flow_multiplier * volume
        
        cmf = pd.Series(money_flow_volume).rolling(window=period).sum() / pd.Series(volume).rolling(window=period).sum()
        return cmf.values

class StatisticalFeatures:
    """Calculadora de features estatísticas"""
    
    def __init__(self):
        self.feature_cache = {}
        logger.info("📊 Calculadora de features estatísticas inicializada")
    
    def calculate_all_statistical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula todas as features estatísticas"""
        result_df = df.copy()
        
        if 'close_price' not in df.columns:
            return result_df
        
        close = df['close_price']
        
        # Features de retorno
        result_df = self._calculate_return_features(result_df, close)
        
        # Features de distribuição
        result_df = self._calculate_distribution_features(result_df, close)
        
        # Features de autocorrelação
        result_df = self._calculate_autocorrelation_features(result_df, close)
        
        # Features de estacionariedade
        result_df = self._calculate_stationarity_features(result_df, close)
        
        # Features de entropia
        result_df = self._calculate_entropy_features(result_df, close)
        
        return result_df
    
    def _calculate_return_features(self, df: pd.DataFrame, close: pd.Series) -> pd.DataFrame:
        """Calcula features baseadas em retornos"""
        # Retornos simples
        for period in [1, 5, 10, 20]:
            df[f'return_{period}d'] = close.pct_change(period)
        
        # Retornos logarítmicos
        for period in [1, 5, 10, 20]:
            df[f'log_return_{period}d'] = np.log(close / close.shift(period))
        
        # Retornos compostos
        for period in [1, 5, 10, 20]:
            df[f'comp_return_{period}d'] = (close / close.shift(period)) - 1
        
        # Estatísticas dos retornos
        returns = close.pct_change()
        for window in [5, 10, 20, 50]:
            df[f'return_mean_{window}'] = returns.rolling(window).mean()
            df[f'return_std_{window}'] = returns.rolling(window).std()
            df[f'return_skew_{window}'] = returns.rolling(window).skew()
            df[f'return_kurt_{window}'] = returns.rolling(window).kurt()
        
        # Maximum Drawdown
        df['cummax'] = close.cummax()
        df['drawdown'] = (close - df['cummax']) / df['cummax']
        df['max_drawdown_20'] = df['drawdown'].rolling(20).min()
        df['max_drawdown_50'] = df['drawdown'].rolling(50).min()
        
        return df
    
    def _calculate_distribution_features(self, df: pd.DataFrame, close: pd.Series) -> pd.DataFrame:
        """Calcula features de distribuição"""
        for window in [5, 10, 20, 50]:
            window_data = close.rolling(window)
            
            # Momentos estatísticos
            df[f'price_mean_{window}'] = window_data.mean()
            df[f'price_std_{window}'] = window_data.std()
            df[f'price_skew_{window}'] = window_data.skew()
            df[f'price_kurt_{window}'] = window_data.kurt()
            
            # Quantis
            df[f'price_q25_{window}'] = window_data.quantile(0.25)
            df[f'price_q50_{window}'] = window_data.quantile(0.50)
            df[f'price_q75_{window}'] = window_data.quantile(0.75)
            df[f'price_iqr_{window}'] = df[f'price_q75_{window}'] - df[f'price_q25_{window}']
            
            # Range
            df[f'price_range_{window}'] = window_data.max() - window_data.min()
            df[f'price_range_pct_{window}'] = (window_data.max() - window_data.min()) / window_data.mean()
        
        return df
    
    def _calculate_autocorrelation_features(self, df: pd.DataFrame, close: pd.Series) -> pd.DataFrame:
        """Calcula features de autocorrelação"""
        returns = close.pct_change().dropna()
        
        for lag in [1, 2, 3, 5, 10]:
            df[f'autocorr_{lag}'] = returns.autocorr(lag)
        
        # Partial autocorrelation
        for lag in [1, 2, 3, 5, 10]:
            df[f'pacf_{lag}'] = self._calculate_partial_autocorrelation(returns, lag)
        
        return df
    
    def _calculate_stationarity_features(self, df: pd.DataFrame, close: pd.Series) -> pd.DataFrame:
        """Calcula features de estacionariedade"""
        # Augmented Dickey-Fuller test
        for window in [20, 50, 100]:
            if len(close) >= window:
                window_data = close.iloc[-window:]
                adf_stat = self._calculate_adf_statistic(window_data)
                df[f'adf_stat_{window}'] = adf_stat
        
        # Hurst exponent
        for window in [20, 50, 100]:
            if len(close) >= window:
                window_data = close.iloc[-window:]
                hurst = self._calculate_hurst_exponent(window_data)
                df[f'hurst_{window}'] = hurst
        
        return df
    
    def _calculate_entropy_features(self, df: pd.DataFrame, close: pd.Series) -> pd.DataFrame:
        """Calcula features de entropia"""
        returns = close.pct_change().dropna()
        
        for window in [10, 20, 50]:
            if len(returns) >= window:
                window_data = returns.iloc[-window:]
                
                # Shannon entropy
                entropy = self._calculate_shannon_entropy(window_data)
                df[f'entropy_{window}'] = entropy
                
                # Approximate entropy
                approx_entropy = self._calculate_approximate_entropy(window_data)
                df[f'approx_entropy_{window}'] = approx_entropy
        
        return df
    
    def _calculate_partial_autocorrelation(self, series: pd.Series, lag: int) -> float:
        """Calcula autocorrelação parcial"""
        try:
            from statsmodels.tsa.stattools import pacf
            pacf_values = pacf(series, nlags=lag)
            return pacf_values[lag] if lag < len(pacf_values) else 0.0
        except ImportError:
            # Fallback simples
            return series.autocorr(lag)
    
    def _calculate_adf_statistic(self, series: pd.Series) -> float:
        """Calcula estatística ADF"""
        try:
            from statsmodels.tsa.stattools import adfuller
            result = adfuller(series)
            return result[0]  # ADF statistic
        except ImportError:
            # Fallback simples
            return 0.0
    
    def _calculate_hurst_exponent(self, series: pd.Series) -> float:
        """Calcula expoente de Hurst"""
        try:
            # Implementação simplificada
            lags = range(2, min(20, len(series)//2))
            tau = [np.std(np.subtract(series[lag:], series[:-lag])) for lag in lags]
            poly = np.polyfit(np.log(lags), np.log(tau), 1)
            return poly[0] * 2.0
        except:
            return 0.5  # Random walk
    
    def _calculate_shannon_entropy(self, series: pd.Series, bins: int = 10) -> float:
        """Calcula entropia de Shannon"""
        try:
            hist, _ = np.histogram(series, bins=bins)
            hist = hist[hist > 0]
            prob = hist / hist.sum()
            entropy = -np.sum(prob * np.log2(prob))
            return entropy
        except:
            return 0.0
    
    def _calculate_approximate_entropy(self, series: pd.Series, m: int = 2, r: float = None) -> float:
        """Calcula entropia aproximada"""
        try:
            if r is None:
                r = 0.2 * np.std(series)
            
            def _maxdist(xi, xj, m):
                return max([abs(ua - va) for ua, va in zip(xi, xj)])
            
            def _phi(m):
                x = [[series[j] for j in range(i, i + m - 1 + 1)] for i in range(N - m + 1)]
                C = [len([1 for xj in x if _maxdist(xi, xj, m) <= r]) / (N - m + 1.0) for xi in x]
                return (N - m + 1.0)**(-1) * sum(np.log(C))
            
            N = len(series)
            return abs(_phi(m + 1) - _phi(m))
        except:
            return 0.0

class MicrostructureFeatures:
    """Calculadora de features de microestrutura de mercado"""
    
    def __init__(self):
        self.feature_cache = {}
        logger.info("🏗️ Calculadora de features de microestrutura inicializada")
    
    def calculate_microstructure_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula features de microestrutura"""
        result_df = df.copy()
        
        # Features de spread
        result_df = self._calculate_spread_features(result_df)
        
        # Features de fluxo de ordens
        result_df = self._calculate_order_flow_features(result_df)
        
        # Features de profundidade
        result_df = self._calculate_depth_features(result_df)
        
        # Features de impacto
        result_df = self._calculate_impact_features(result_df)
        
        return result_df
    
    def _calculate_spread_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula features de spread"""
        if 'bid_price' in df.columns and 'ask_price' in df.columns:
            # Absolute spread
            df['absolute_spread'] = df['ask_price'] - df['bid_price']
            
            # Relative spread
            df['relative_spread'] = (df['ask_price'] - df['bid_price']) / df['close_price']
            
            # Mid price
            df['mid_price'] = (df['bid_price'] + df['ask_price']) / 2
            
            # Spread statistics
            for window in [5, 10, 20]:
                df[f'spread_mean_{window}'] = df['relative_spread'].rolling(window).mean()
                df[f'spread_std_{window}'] = df['relative_spread'].rolling(window).std()
                df[f'spread_max_{window}'] = df['relative_spread'].rolling(window).max()
        
        return df
    
    def _calculate_order_flow_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula features de fluxo de ordens"""
        if 'bid_size' in df.columns and 'ask_size' in df.columns:
            # Order flow imbalance
            df['order_flow_imbalance'] = (df['bid_size'] - df['ask_size']) / (df['bid_size'] + df['ask_size'])
            
            # Volume imbalance
            if 'volume' in df.columns:
                df['volume_imbalance'] = (df['bid_size'] - df['ask_size']) / df['volume']
            
            # OFI statistics
            for window in [5, 10, 20]:
                df[f'ofi_mean_{window}'] = df['order_flow_imbalance'].rolling(window).mean()
                df[f'ofi_std_{window}'] = df['order_flow_imbalance'].rolling(window).std()
        
        return df
    
    def _calculate_depth_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula features de profundidade"""
        if 'bid_size' in df.columns and 'ask_size' in df.columns:
            # Total depth
            df['total_depth'] = df['bid_size'] + df['ask_size']
            
            # Depth imbalance
            df['depth_imbalance'] = (df['bid_size'] - df['ask_size']) / (df['bid_size'] + df['ask_size'])
            
            # Depth statistics
            for window in [5, 10, 20]:
                df[f'depth_mean_{window}'] = df['total_depth'].rolling(window).mean()
                df[f'depth_std_{window}'] = df['total_depth'].rolling(window).std()
        
        return df
    
    def _calculate_impact_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula features de impacto"""
        if 'volume' in df.columns and 'close_price' in df.columns:
            # Price impact
            returns = df['close_price'].pct_change()
            df['price_impact'] = returns * df['volume']
            
            # Amihud illiquidity
            df['amihud_illiquidity'] = abs(returns) / df['volume']
            
            # Impact statistics
            for window in [5, 10, 20]:
                df[f'impact_mean_{window}'] = df['price_impact'].rolling(window).mean()
                df[f'illiquidity_mean_{window}'] = df['amihud_illiquidity'].rolling(window).mean()
        
        return df

class FrequencyDomainFeatures:
    """Calculadora de features no domínio da frequência"""
    
    def __init__(self):
        self.feature_cache = {}
        logger.info("🌊 Calculadora de features de frequência inicializada")
    
    def calculate_frequency_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula features no domínio da frequência"""
        result_df = df.copy()
        
        if 'close_price' not in df.columns:
            return result_df
        
        close = df['close_price'].values
        
        # FFT features
        result_df = self._calculate_fft_features(result_df, close)
        
        # Wavelet features
        result_df = self._calculate_wavelet_features(result_df, close)
        
        # Spectral features
        result_df = self._calculate_spectral_features(result_df, close)
        
        return result_df
    
    def _calculate_fft_features(self, df: pd.DataFrame, prices: np.ndarray) -> pd.DataFrame:
        """Calcula features usando FFT"""
        for window in [32, 64, 128]:
            if len(prices) >= window:
                window_data = prices[-window:]
                
                # Apply FFT
                fft_values = fft(window_data)
                fft_freq = fftfreq(window)
                
                # Power spectrum
                power_spectrum = np.abs(fft_values)**2
                
                # Dominant frequency
                dominant_freq_idx = np.argmax(power_spectrum[1:len(power_spectrum)//2]) + 1
                df[f'fft_dominant_freq_{window}'] = fft_freq[dominant_freq_idx]
                
                # Spectral entropy
                power_spectrum_normalized = power_spectrum / np.sum(power_spectrum)
                spectral_entropy = -np.sum(power_spectrum_normalized * np.log2(power_spectrum_normalized + 1e-10))
                df[f'fft_spectral_entropy_{window}'] = spectral_entropy
                
                # Energy in different frequency bands
                total_energy = np.sum(power_spectrum)
                low_freq_energy = np.sum(power_spectrum[:len(power_spectrum)//4])
                mid_freq_energy = np.sum(power_spectrum[len(power_spectrum)//4:3*len(power_spectrum)//4])
                high_freq_energy = np.sum(power_spectrum[3*len(power_spectrum)//4:])
                
                df[f'fft_low_freq_ratio_{window}'] = low_freq_energy / total_energy
                df[f'fft_mid_freq_ratio_{window}'] = mid_freq_energy / total_energy
                df[f'fft_high_freq_ratio_{window}'] = high_freq_energy / total_energy
        
        return df
    
    def _calculate_wavelet_features(self, df: pd.DataFrame, prices: np.ndarray) -> pd.DataFrame:
        """Calcula features usando Wavelet"""
        try:
            import pywt
            
            for window in [32, 64, 128]:
                if len(prices) >= window:
                    window_data = prices[-window:]
                    
                    # Wavelet decomposition
                    coeffs = pywt.wavedec(window_data, 'db4', level=3)
                    
                    # Energy in each level
                    for i, coeff in enumerate(coeffs):
                        energy = np.sum(coeff**2)
                        df[f'wavelet_energy_{i}_{window}'] = energy
                    
                    # Total wavelet energy
                    total_energy = sum(np.sum(c**2) for c in coeffs)
                    df[f'wavelet_total_energy_{window}'] = total_energy
                    
                    # Relative energy
                    for i, coeff in enumerate(coeffs):
                        relative_energy = np.sum(coeff**2) / total_energy if total_energy > 0 else 0
                        df[f'wavelet_rel_energy_{i}_{window}'] = relative_energy
        
        except ImportError:
            logger.warning("PyWavelets não disponível, pulando features wavelet")
        
        return df
    
    def _calculate_spectral_features(self, df: pd.DataFrame, prices: np.ndarray) -> pd.DataFrame:
        """Calcula features espectrais"""
        for window in [32, 64, 128]:
            if len(prices) >= window:
                window_data = prices[-window:]
                
                # Power spectral density
                frequencies, psd = signal.periodogram(window_data)
                
                # Spectral centroid
                spectral_centroid = np.sum(frequencies * psd) / np.sum(psd)
                df[f'spectral_centroid_{window}'] = spectral_centroid
                
                # Spectral bandwidth
                spectral_bandwidth = np.sqrt(np.sum(((frequencies - spectral_centroid)**2) * psd) / np.sum(psd))
                df[f'spectral_bandwidth_{window}'] = spectral_bandwidth
                
                # Spectral rolloff
                cumsum_psd = np.cumsum(psd)
                rolloff_idx = np.where(cumsum_psd >= 0.85 * cumsum_psd[-1])[0][0]
                df[f'spectral_rolloff_{window}'] = frequencies[rolloff_idx]
        
        return df

class FeatureEngineeringPipeline:
    """Pipeline completo de engenharia de features"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.technical_indicators = TechnicalIndicators()
        self.statistical_features = StatisticalFeatures()
        self.microstructure_features = MicrostructureFeatures()
        self.frequency_features = FrequencyDomainFeatures()
        
        # Feature definitions registry
        self.feature_definitions = {}
        self.feature_importance = {}
        
        # Processing statistics
        self.processing_stats = defaultdict(int)
        
        logger.info("🚀 Pipeline de engenharia de features inicializado")
    
    async def generate_features(self, df: pd.DataFrame, symbol: str = None) -> FeatureSet:
        """Gera features para um DataFrame"""
        start_time = time.time()
        
        try:
            result_df = df.copy()
            feature_metadata = {}
            
            # Technical Indicators
            if self.config.get('technical_indicators', True):
                result_df = self.technical_indicators.calculate_all_indicators(result_df)
                self._register_technical_features(feature_metadata)
            
            # Statistical Features
            if self.config.get('statistical_features', True):
                result_df = self.statistical_features.calculate_all_statistical_features(result_df)
                self._register_statistical_features(feature_metadata)
            
            # Microstructure Features
            if self.config.get('microstructure_features', True):
                result_df = self.microstructure_features.calculate_microstructure_features(result_df)
                self._register_microstructure_features(feature_metadata)
            
            # Frequency Domain Features
            if self.config.get('frequency_features', True):
                result_df = self.frequency_features.calculate_frequency_features(result_df)
                self._register_frequency_features(feature_metadata)
            
            # Time Features
            if self.config.get('time_features', True):
                result_df = self._add_time_features(result_df)
                self._register_time_features(feature_metadata)
            
            # Lag Features
            if self.config.get('lag_features', True):
                result_df = self._add_lag_features(result_df)
                self._register_lag_features(feature_metadata)
            
            # Feature Selection
            if self.config.get('feature_selection', False):
                result_df = self._select_features(result_df)
            
            # Create FeatureSet for the last row
            if not result_df.empty:
                last_row = result_df.iloc[-1]
                timestamp = last_row.get('timestamp', datetime.now())
                
                # Extract features (exclude non-feature columns)
                feature_columns = [col for col in result_df.columns if col not in 
                                 ['timestamp', 'open_price', 'high_price', 'low_price', 'close_price', 'volume']]
                
                features = {}
                missing_features = []
                
                for col in feature_columns:
                    if pd.notna(last_row[col]):
                        features[col] = float(last_row[col])
                    else:
                        missing_features.append(col)
                
                # Calculate quality score
                quality_score = 1.0 - (len(missing_features) / len(feature_columns)) if feature_columns else 0.0
                
                computation_time = time.time() - start_time
                
                feature_set = FeatureSet(
                    symbol=symbol or "UNKNOWN",
                    timestamp=timestamp,
                    features=features,
                    feature_metadata=feature_metadata,
                    quality_score=quality_score,
                    missing_features=missing_features,
                    computation_time=computation_time
                )
                
                self.processing_stats['feature_sets_generated'] += 1
                self.processing_stats['total_features_generated'] += len(features)
                
                logger.info(f"✅ {len(features)} features geradas para {symbol} em {computation_time:.3f}s")
                
                return feature_set
            else:
                return FeatureSet(
                    symbol=symbol or "UNKNOWN",
                    timestamp=datetime.now(),
                    features={},
                    feature_metadata=feature_metadata,
                    quality_score=0.0,
                    missing_features=[],
                    computation_time=time.time() - start_time
                )
        
        except Exception as e:
            logger.error(f"Erro ao gerar features para {symbol}: {e}")
            return FeatureSet(
                symbol=symbol or "UNKNOWN",
                timestamp=datetime.now(),
                features={},
                feature_metadata={},
                quality_score=0.0,
                missing_features=[],
                computation_time=time.time() - start_time
            )
    
    def _add_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adiciona features temporais"""
        if 'timestamp' in df.columns:
            df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
            df['day_of_week'] = pd.to_datetime(df['timestamp']).dt.dayofweek
            df['day_of_month'] = pd.to_datetime(df['timestamp']).dt.day
            df['month'] = pd.to_datetime(df['timestamp']).dt.month
            df['quarter'] = pd.to_datetime(df['timestamp']).dt.quarter
            df['is_weekend'] = pd.to_datetime(df['timestamp']).dt.dayofweek >= 5
            
            # Cyclical encoding
            df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
            df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
            df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
            df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
            df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
            df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        
        return df
    
    def _add_lag_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adiciona features de lag"""
        lag_periods = self.config.get('lag_periods', [1, 2, 3, 5, 10])
        
        # Identify feature columns (exclude basic OHLCV)
        feature_columns = [col for col in df.columns if col not in 
                         ['timestamp', 'open_price', 'high_price', 'low_price', 'close_price', 'volume']]
        
        for col in feature_columns:
            for lag in lag_periods:
                df[f'{col}_lag_{lag}'] = df[col].shift(lag)
        
        return df
    
    def _select_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Seleciona features mais importantes"""
        try:
            # Remove features com alta correlação
            feature_columns = [col for col in df.columns if col not in 
                             ['timestamp', 'open_price', 'high_price', 'low_price', 'close_price', 'volume']]
            
            if len(feature_columns) > 100:  # Se tiver muitas features
                corr_matrix = df[feature_columns].corr().abs()
                upper_tri = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
                
                # Remove features com correlação > 0.95
                to_remove = [column for column in upper_tri.columns if any(upper_tri[column] > 0.95)]
                df = df.drop(columns=to_remove)
                
                logger.info(f"Removidas {len(to_remove)} features altamente correlacionadas")
            
            return df
        
        except Exception as e:
            logger.warning(f"Erro na seleção de features: {e}")
            return df
    
    def _register_technical_features(self, metadata: Dict[str, FeatureDefinition]):
        """Registra definições de features técnicas"""
        technical_features = [
            FeatureDefinition("sma_20", FeatureType.TECHNICAL_INDICATORS, FeatureCategory.TREND, 
                           "Simple Moving Average de 20 períodos", {"period": 20}),
            FeatureDefinition("ema_20", FeatureType.TECHNICAL_INDICATORS, FeatureCategory.TREND, 
                           "Exponential Moving Average de 20 períodos", {"period": 20}),
            FeatureDefinition("rsi_14", FeatureType.TECHNICAL_INDICATORS, FeatureCategory.MOMENTUM, 
                           "Relative Strength Index de 14 períodos", {"period": 14}),
            FeatureDefinition("macd", FeatureType.TECHNICAL_INDICATORS, FeatureCategory.MOMENTUM, 
                           "Moving Average Convergence Divergence"),
            FeatureDefinition("bb_upper", FeatureType.TECHNICAL_INDICATORS, FeatureCategory.VOLATILITY, 
                           "Banda superior de Bollinger"),
            FeatureDefinition("atr_14", FeatureType.TECHNICAL_INDICATORS, FeatureCategory.VOLATILITY, 
                           "Average True Range de 14 períodos", {"period": 14}),
            FeatureDefinition("obv", FeatureType.TECHNICAL_INDICATORS, FeatureCategory.VOLUME, 
                           "On-Balance Volume"),
        ]
        
        for feature in technical_features:
            metadata[feature.name] = feature
    
    def _register_statistical_features(self, metadata: Dict[str, FeatureDefinition]):
        """Registra definições de features estatísticas"""
        statistical_features = [
            FeatureDefinition("return_1d", FeatureType.STATISTICAL_FEATURES, FeatureCategory.STATISTICAL, 
                           "Retorno de 1 dia", {"period": 1}, is_lag_feature=True, lag_periods=1),
            FeatureDefinition("return_std_20", FeatureType.STATISTICAL_FEATURES, FeatureCategory.STATISTICAL, 
                           "Desvio padrão dos retornos de 20 dias", {"window": 20}),
            FeatureDefinition("price_skew_20", FeatureType.STATISTICAL_FEATURES, FeatureCategory.STATISTICAL, 
                           "Skewness dos preços de 20 dias", {"window": 20}),
            FeatureDefinition("hurst_50", FeatureType.STATISTICAL_FEATURES, FeatureCategory.STATISTICAL, 
                           "Expoente de Hurst de 50 dias", {"window": 50}),
        ]
        
        for feature in statistical_features:
            metadata[feature.name] = feature
    
    def _register_microstructure_features(self, metadata: Dict[str, FeatureDefinition]):
        """Registra definições de features de microestrutura"""
        microstructure_features = [
            FeatureDefinition("relative_spread", FeatureType.MICROSTRUCTURE_FEATURES, 
                           FeatureCategory.MARKET_MICROSTRUCTURE, "Spread relativo bid-ask"),
            FeatureDefinition("order_flow_imbalance", FeatureType.MICROSTRUCTURE_FEATURES, 
                           FeatureCategory.MARKET_MICROSTRUCTURE, "Desequilíbrio do fluxo de ordens"),
            FeatureDefinition("amihud_illiquidity", FeatureType.MICROSTRUCTURE_FEATURES, 
                           FeatureCategory.MARKET_MICROSTRUCTURE, "Medida de iliquidez de Amihud"),
        ]
        
        for feature in microstructure_features:
            metadata[feature.name] = feature
    
    def _register_frequency_features(self, metadata: Dict[str, FeatureDefinition]):
        """Registra definições de features de frequência"""
        frequency_features = [
            FeatureDefinition("fft_dominant_freq_64", FeatureType.FREQUENCY_DOMAIN_FEATURES, 
                           FeatureCategory.FREQUENCY_ANALYSIS, "Frequência dominante (FFT, janela 64)", {"window": 64}),
            FeatureDefinition("fft_spectral_entropy_64", FeatureType.FREQUENCY_DOMAIN_FEATURES, 
                           FeatureCategory.FREQUENCY_ANALYSIS, "Entropia espectral (FFT, janela 64)", {"window": 64}),
            FeatureDefinition("spectral_centroid_64", FeatureType.FREQUENCY_DOMAIN_FEATURES, 
                           FeatureCategory.FREQUENCY_ANALYSIS, "Centroide espectral (janela 64)", {"window": 64}),
        ]
        
        for feature in frequency_features:
            metadata[feature.name] = feature
    
    def _register_time_features(self, metadata: Dict[str, FeatureDefinition]):
        """Registra definições de features temporais"""
        time_features = [
            FeatureDefinition("hour", FeatureType.TIME_FEATURES, FeatureCategory.TEMPORAL, "Hora do dia"),
            FeatureDefinition("day_of_week", FeatureType.TIME_FEATURES, FeatureCategory.TEMPORAL, "Dia da semana"),
            FeatureDefinition("hour_sin", FeatureType.TIME_FEATURES, FeatureCategory.TEMPORAL, "Encoding senoidal da hora"),
            FeatureDefinition("is_weekend", FeatureType.TIME_FEATURES, FeatureCategory.TEMPORAL, "Indicador de fim de semana"),
        ]
        
        for feature in time_features:
            metadata[feature.name] = feature
    
    def _register_lag_features(self, metadata: Dict[str, FeatureDefinition]):
        """Registra definições de features de lag"""
        lag_periods = self.config.get('lag_periods', [1, 2, 3, 5, 10])
        
        base_features = ['return_1d', 'rsi_14', 'macd', 'volume']
        
        for feature in base_features:
            for lag in lag_periods:
                lag_feature = FeatureDefinition(
                    f"{feature}_lag_{lag}", 
                    FeatureType.STATISTICAL_FEATURES, 
                    FeatureCategory.STATISTICAL,
                    f"Feature {feature} com lag de {lag} períodos",
                    {"base_feature": feature, "lag": lag},
                    is_lag_feature=True,
                    lag_periods=lag
                )
                metadata[lag_feature.name] = lag_feature
    
    def get_feature_definitions(self) -> Dict[str, FeatureDefinition]:
        """Retorna todas as definições de features"""
        return self.feature_definitions.copy()
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de processamento"""
        return dict(self.processing_stats)
    
    def update_feature_importance(self, feature_importance: Dict[str, float]):
        """Atualiza importância das features"""
        self.feature_importance.update(feature_importance)
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Retorna importância das features"""
        return self.feature_importance.copy()

# Configuração padrão
DEFAULT_FEATURE_CONFIG = {
    'technical_indicators': True,
    'statistical_features': True,
    'microstructure_features': True,
    'frequency_features': True,
    'time_features': True,
    'lag_features': True,
    'lag_periods': [1, 2, 3, 5, 10],
    'feature_selection': True
}

if __name__ == "__main__":
    # Exemplo de uso
    async def main():
        # Cria dados de exemplo
        dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='1H')
        np.random.seed(42)
        
        data = {
            'timestamp': dates,
            'open_price': 100 + np.random.randn(len(dates)) * 2,
            'high_price': 102 + np.random.randn(len(dates)) * 2,
            'low_price': 98 + np.random.randn(len(dates)) * 2,
            'close_price': 100 + np.random.randn(len(dates)) * 2,
            'volume': 1000000 + np.random.randn(len(dates)) * 100000,
            'bid_price': 99.5 + np.random.randn(len(dates)) * 1,
            'ask_price': 100.5 + np.random.randn(len(dates)) * 1,
            'bid_size': 500000 + np.random.randn(len(dates)) * 50000,
            'ask_size': 500000 + np.random.randn(len(dates)) * 50000
        }
        
        df = pd.DataFrame(data)
        
        # Cria pipeline
        config = DEFAULT_FEATURE_CONFIG
        pipeline = FeatureEngineeringPipeline(config)
        
        # Gera features
        feature_set = await pipeline.generate_features(df, "EXAMPLE")
        
        print(f"🎯 Features geradas para {feature_set.symbol}:")
        print(f"Timestamp: {feature_set.timestamp}")
        print(f"Quality Score: {feature_set.quality_score:.2f}")
        print(f"Total Features: {len(feature_set.features)}")
        print(f"Missing Features: {len(feature_set.missing_features)}")
        print(f"Computation Time: {feature_set.computation_time:.3f}s")
        
        print("\n📊 Exemplos de features:")
        feature_names = list(feature_set.features.keys())[:10]
        for name in feature_names:
            print(f"{name}: {feature_set.features[name]:.4f}")
        
        print("\n📈 Estatísticas de Processamento:")
        stats = pipeline.get_processing_stats()
        for key, value in stats.items():
            print(f"{key}: {value}")
    
    asyncio.run(main())

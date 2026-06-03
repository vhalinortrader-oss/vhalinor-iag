"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║           SISTEMA DE PRÉ-PROCESSAMENTO E LIMPEZA DE DADOS FINANCEIROS         ║
║                 Componente 2: Processamento de Dados Financeiros              ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import asyncio
import numpy as np
import pandas as pd
from scipy import stats, signal
from sklearn.preprocessing import StandardScaler, RobustScaler, MinMaxScaler
from sklearn.ensemble import IsolationForest
from sklearn.impute import KNNImputer
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import warnings
import json
import pickle
import hashlib
from concurrent.futures import ThreadPoolExecutor
import threading
from collections import deque, defaultdict
import time

# Import do módulo anterior
from market_data_infrastructure import MarketDataPoint, DataFrequency, DataType

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('DataPreprocessingSystem')

class DataQualityLevel(Enum):
    """Níveis de qualidade dos dados"""
    EXCELLENT = (5, "Excelente", "🟢")
    GOOD = (4, "Bom", "🟡")
    FAIR = (3, "Regular", "🟠")
    POOR = (2, "Ruim", "🔴")
    INVALID = (1, "Inválido", "⚫")
    
    def __init__(self, score: int, label: str, icon: str):
        self.score = score
        self.label = label
        self.icon = icon

class OutlierMethod(Enum):
    """Métodos de detecção de outliers"""
    Z_SCORE = "z_score"
    IQR = "iqr"
    ISOLATION_FOREST = "isolation_forest"
    DBSCAN = "dbscan"
    MODIFIED_Z_SCORE = "modified_z_score"
    LOCAL_OUTLIER_FACTOR = "local_outlier_factor"

class ImputationMethod(Enum):
    """Métodos de imputação de dados"""
    FORWARD_FILL = "forward_fill"
    BACKWARD_FILL = "backward_fill"
    LINEAR_INTERPOLATION = "linear_interpolation"
    SPLINE_INTERPOLATION = "spline_interpolation"
    KNN = "knn"
    MEAN = "mean"
    MEDIAN = "median"
    REGRESSION = "regression"

class NormalizationMethod(Enum):
    """Métodos de normalização"""
    STANDARD_SCALER = "standard_scaler"
    ROBUST_SCALER = "robust_scaler"
    MIN_MAX_SCALER = "min_max_scaler"
    UNIT_VECTOR = "unit_vector"
    QUANTILE_TRANSFORM = "quantile_transform"
    POWER_TRANSFORM = "power_transform"

@dataclass
class DataQualityReport:
    """Relatório de qualidade dos dados"""
    symbol: str
    start_time: datetime
    end_time: datetime
    total_records: int
    missing_values: int
    duplicate_records: int
    outliers_detected: int
    data_quality_score: float
    quality_level: DataQualityLevel
    issues_detected: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    processing_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'symbol': self.symbol,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'total_records': self.total_records,
            'missing_values': self.missing_values,
            'duplicate_records': self.duplicate_records,
            'outliers_detected': self.outliers_detected,
            'data_quality_score': self.data_quality_score,
            'quality_level': self.quality_level.label,
            'issues_detected': self.issues_detected,
            'recommendations': self.recommendations,
            'processing_time': self.processing_time
        }

@dataclass
class ProcessingConfig:
    """Configuração de processamento de dados"""
    outlier_method: OutlierMethod = OutlierMethod.Z_SCORE
    outlier_threshold: float = 3.0
    imputation_method: ImputationMethod = ImputationMethod.LINEAR_INTERPOLATION
    normalization_method: NormalizationMethod = NormalizationMethod.STANDARD_SCALER
    remove_duplicates: bool = True
    handle_missing_data: bool = True
    detect_anomalies: bool = True
    validate_ranges: bool = True
    synchronize_time_series: bool = True
    resample_frequency: Optional[DataFrequency] = None
    quality_threshold: float = 0.7

class DataValidator:
    """Validador de dados financeiros"""
    
    def __init__(self):
        self.validation_rules = self._initialize_validation_rules()
        logger.info("✅ Validador de dados inicializado")
    
    def _initialize_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Inicializa regras de validação"""
        return {
            'price_ranges': {
                'min_price': 0.001,
                'max_price': 1000000,
                'max_daily_change': 0.5  # 50%
            },
            'volume_ranges': {
                'min_volume': 0,
                'max_volume': 10**12,
                'max_volume_change': 10.0  # 10x
            },
            'time_validation': {
                'max_future_gap': timedelta(minutes=5),
                'max_past_gap': timedelta(days=365 * 10),
                'required_frequency': True
            },
            'data_completeness': {
                'min_completeness': 0.95,  # 95%
                'max_consecutive_missing': 5
            }
        }
    
    def validate_data_point(self, data_point: MarketDataPoint) -> Tuple[bool, List[str]]:
        """Valida um ponto de dado individual"""
        errors = []
        
        # Validação de preços
        if data_point.open_price:
            if not self._is_valid_price(data_point.open_price):
                errors.append(f"Open price inválido: {data_point.open_price}")
        
        if data_point.high_price:
            if not self._is_valid_price(data_point.high_price):
                errors.append(f"High price inválido: {data_point.high_price}")
        
        if data_point.low_price:
            if not self._is_valid_price(data_point.low_price):
                errors.append(f"Low price inválido: {data_point.low_price}")
        
        if data_point.close_price:
            if not self._is_valid_price(data_point.close_price):
                errors.append(f"Close price inválido: {data_point.close_price}")
        
        # Validação de volume
        if data_point.volume:
            if not self._is_valid_volume(data_point.volume):
                errors.append(f"Volume inválido: {data_point.volume}")
        
        # Validação de consistência OHLC
        if all([data_point.open_price, data_point.high_price, 
                data_point.low_price, data_point.close_price]):
            if not self._is_valid_ohlc(data_point):
                errors.append("Inconsistência nos dados OHLC")
        
        # Validação temporal
        if not self._is_valid_timestamp(data_point.timestamp):
            errors.append(f"Timestamp inválido: {data_point.timestamp}")
        
        return len(errors) == 0, errors
    
    def validate_dataframe(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Valida um DataFrame completo"""
        errors = []
        
        # Verifica se está vazio
        if df.empty:
            errors.append("DataFrame vazio")
            return False, errors
        
        # Verifica colunas obrigatórias
        required_columns = ['timestamp', 'close_price']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            errors.append(f"Colunas obrigatórias faltando: {missing_columns}")
        
        # Verifica duplicatas
        if df.duplicated().any():
            errors.append("Registros duplicados encontrados")
        
        # Verifica ordenação temporal
        if not df['timestamp'].is_monotonic_increasing:
            errors.append("Dados não estão ordenados cronologicamente")
        
        # Verifica gaps temporais
        if 'timestamp' in df.columns:
            time_gaps = df['timestamp'].diff()
            max_gap = time_gaps.max()
            if max_gap > timedelta(hours=24):
                errors.append(f"Gap temporal muito grande: {max_gap}")
        
        # Verifica qualidade dos preços
        price_columns = ['open_price', 'high_price', 'low_price', 'close_price']
        for col in price_columns:
            if col in df.columns:
                if (df[col] <= 0).any():
                    errors.append(f"Preços não positivos encontrados em {col}")
                
                if (df[col] > 1000000).any():
                    errors.append(f"Preços extremamente altos encontrados em {col}")
        
        return len(errors) == 0, errors
    
    def _is_valid_price(self, price: float) -> bool:
        """Verifica se o preço é válido"""
        rules = self.validation_rules['price_ranges']
        return (rules['min_price'] <= price <= rules['max_price'] and 
                not np.isnan(price) and not np.isinf(price))
    
    def _is_valid_volume(self, volume: float) -> bool:
        """Verifica se o volume é válido"""
        rules = self.validation_rules['volume_ranges']
        return (rules['min_volume'] <= volume <= rules['max_volume'] and 
                not np.isnan(volume) and not np.isinf(volume))
    
    def _is_valid_ohlc(self, data_point: MarketDataPoint) -> bool:
        """Verifica consistência dos dados OHLC"""
        return (data_point.low_price <= data_point.open_price <= data_point.high_price and
                data_point.low_price <= data_point.close_price <= data_point.high_price)
    
    def _is_valid_timestamp(self, timestamp: datetime) -> bool:
        """Verifica se o timestamp é válido"""
        now = datetime.now()
        rules = self.validation_rules['time_validation']
        
        return (timestamp <= now + rules['max_future_gap'] and
                timestamp >= now - rules['max_past_gap'])

class OutlierDetector:
    """Detetor de outliers"""
    
    def __init__(self, method: OutlierMethod = OutlierMethod.Z_SCORE):
        self.method = method
        self.models = {}
        logger.info(f"🔍 Detector de outliers inicializado com método: {method.value}")
    
    def detect_outliers(self, data: pd.Series, threshold: float = 3.0) -> pd.Series:
        """Detecta outliers em uma série de dados"""
        if data.empty or data.isna().all():
            return pd.Series([False] * len(data), index=data.index)
        
        if self.method == OutlierMethod.Z_SCORE:
            return self._detect_z_score_outliers(data, threshold)
        elif self.method == OutlierMethod.IQR:
            return self._detect_iqr_outliers(data, threshold)
        elif self.method == OutlierMethod.MODIFIED_Z_SCORE:
            return self._detect_modified_z_score_outliers(data, threshold)
        elif self.method == OutlierMethod.ISOLATION_FOREST:
            return self._detect_isolation_forest_outliers(data, threshold)
        else:
            logger.warning(f"Método {self.method.value} não implementado")
            return pd.Series([False] * len(data), index=data.index)
    
    def _detect_z_score_outliers(self, data: pd.Series, threshold: float) -> pd.Series:
        """Detecta outliers usando Z-Score"""
        z_scores = np.abs(stats.zscore(data.dropna()))
        outliers = pd.Series([False] * len(data), index=data.index)
        outliers.loc[data.dropna().index] = z_scores > threshold
        return outliers
    
    def _detect_iqr_outliers(self, data: pd.Series, multiplier: float = 1.5) -> pd.Series:
        """Detecta outliers usando IQR"""
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - multiplier * IQR
        upper_bound = Q3 + multiplier * IQR
        
        outliers = (data < lower_bound) | (data > upper_bound)
        return outliers.fillna(False)
    
    def _detect_modified_z_score_outliers(self, data: pd.Series, threshold: float = 3.5) -> pd.Series:
        """Detecta outliers usando Modified Z-Score"""
        median = data.median()
        mad = np.median(np.abs(data - median))
        modified_z_scores = 0.6745 * (data - median) / mad
        outliers = np.abs(modified_z_scores) > threshold
        return outliers.fillna(False)
    
    def _detect_isolation_forest_outliers(self, data: pd.Series, contamination: float = 0.1) -> pd.Series:
        """Detecta outliers usando Isolation Forest"""
        try:
            # Prepara dados
            valid_data = data.dropna()
            if len(valid_data) < 10:
                return pd.Series([False] * len(data), index=data.index)
            
            X = valid_data.values.reshape(-1, 1)
            
            # Treina modelo
            iso_forest = IsolationForest(contamination=contamination, random_state=42)
            outlier_labels = iso_forest.fit_predict(X)
            
            outliers = pd.Series([False] * len(data), index=data.index)
            outliers.loc[valid_data.index] = outlier_labels == -1
            
            return outliers
            
        except Exception as e:
            logger.error(f"Erro no Isolation Forest: {e}")
            return pd.Series([False] * len(data), index=data.index)

class DataImputer:
    """Imputador de dados faltantes"""
    
    def __init__(self, method: ImputationMethod = ImputationMethod.LINEAR_INTERPOLATION):
        self.method = method
        self.imputers = {}
        logger.info(f"🔧 Imputador inicializado com método: {method.value}")
    
    def impute_data(self, data: pd.DataFrame, columns: List[str] = None) -> pd.DataFrame:
        """Imputa dados faltantes"""
        if columns is None:
            columns = data.select_dtypes(include=[np.number]).columns.tolist()
        
        result = data.copy()
        
        for column in columns:
            if column not in data.columns:
                continue
            
            if self.method == ImputationMethod.FORWARD_FILL:
                result[column] = self._forward_fill(result[column])
            elif self.method == ImputationMethod.BACKWARD_FILL:
                result[column] = self._backward_fill(result[column])
            elif self.method == ImputationMethod.LINEAR_INTERPOLATION:
                result[column] = self._linear_interpolation(result[column])
            elif self.method == ImputationMethod.SPLINE_INTERPOLATION:
                result[column] = self._spline_interpolation(result[column])
            elif self.method == ImputationMethod.KNN:
                result[column] = self._knn_imputation(result, column)
            elif self.method == ImputationMethod.MEAN:
                result[column] = self._mean_imputation(result[column])
            elif self.method == ImputationMethod.MEDIAN:
                result[column] = self._median_imputation(result[column])
        
        return result
    
    def _forward_fill(self, series: pd.Series) -> pd.Series:
        """Preenche valores faltantes com o último valor válido"""
        return series.fillna(method='ffill')
    
    def _backward_fill(self, series: pd.Series) -> pd.Series:
        """Preenche valores faltantes com o próximo valor válido"""
        return series.fillna(method='bfill')
    
    def _linear_interpolation(self, series: pd.Series) -> pd.Series:
        """Interpolação linear"""
        return series.interpolate(method='linear')
    
    def _spline_interpolation(self, series: pd.Series) -> pd.Series:
        """Interpolação spline"""
        return series.interpolate(method='spline', order=3)
    
    def _knn_imputation(self, df: pd.DataFrame, column: str) -> pd.Series:
        """Imputação usando KNN"""
        try:
            # Seleciona apenas colunas numéricas
            numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
            
            if len(numeric_columns) < 2:
                return df[column].fillna(df[column].median())
            
            # Usa KNNImputer
            imputer = KNNImputer(n_neighbors=5)
            imputed_data = imputer.fit_transform(df[numeric_columns])
            
            # Reconstrói DataFrame
            imputed_df = pd.DataFrame(imputed_data, columns=numeric_columns, index=df.index)
            
            return imputed_df[column]
            
        except Exception as e:
            logger.error(f"Erro na imputação KNN: {e}")
            return df[column].fillna(df[column].median())
    
    def _mean_imputation(self, series: pd.Series) -> pd.Series:
        """Imputação usando média"""
        return series.fillna(series.mean())
    
    def _median_imputation(self, series: pd.Series) -> pd.Series:
        """Imputação usando mediana"""
        return series.fillna(series.median())

class DataNormalizer:
    """Normalizador de dados"""
    
    def __init__(self, method: NormalizationMethod = NormalizationMethod.STANDARD_SCALER):
        self.method = method
        self.scalers = {}
        logger.info(f"📏 Normalizador inicializado com método: {method.value}")
    
    def normalize_data(self, data: pd.DataFrame, columns: List[str] = None, 
                       fit: bool = True) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """Normaliza dados"""
        if columns is None:
            columns = data.select_dtypes(include=[np.number]).columns.tolist()
        
        result = data.copy()
        scaler_info = {}
        
        for column in columns:
            if column not in data.columns:
                continue
            
            if self.method == NormalizationMethod.STANDARD_SCALER:
                result[column], scaler_info[column] = self._standard_scaler(
                    result[column], fit
                )
            elif self.method == NormalizationMethod.ROBUST_SCALER:
                result[column], scaler_info[column] = self._robust_scaler(
                    result[column], fit
                )
            elif self.method == NormalizationMethod.MIN_MAX_SCALER:
                result[column], scaler_info[column] = self._min_max_scaler(
                    result[column], fit
                )
            elif self.method == NormalizationMethod.UNIT_VECTOR:
                result[column], scaler_info[column] = self._unit_vector(
                    result[column]
                )
        
        return result, scaler_info
    
    def _standard_scaler(self, series: pd.Series, fit: bool) -> Tuple[pd.Series, Dict[str, Any]]:
        """Standard Scaler (Z-score normalization)"""
        if fit:
            mean = series.mean()
            std = series.std()
            self.scalers[series.name] = {'mean': mean, 'std': std}
        else:
            scaler = self.scalers.get(series.name, {'mean': 0, 'std': 1})
            mean = scaler['mean']
            std = scaler['std']
        
        normalized = (series - mean) / std
        scaler_info = {'mean': mean, 'std': std}
        
        return normalized, scaler_info
    
    def _robust_scaler(self, series: pd.Series, fit: bool) -> Tuple[pd.Series, Dict[str, Any]]:
        """Robust Scaler (usa mediana e IQR)"""
        if fit:
            median = series.median()
            q75 = series.quantile(0.75)
            q25 = series.quantile(0.25)
            iqr = q75 - q25
            self.scalers[series.name] = {'median': median, 'iqr': iqr}
        else:
            scaler = self.scalers.get(series.name, {'median': 0, 'iqr': 1})
            median = scaler['median']
            iqr = scaler['iqr']
        
        normalized = (series - median) / iqr
        scaler_info = {'median': median, 'iqr': iqr}
        
        return normalized, scaler_info
    
    def _min_max_scaler(self, series: pd.Series, fit: bool) -> Tuple[pd.Series, Dict[str, Any]]:
        """Min-Max Scaler (normalização para [0,1])"""
        if fit:
            min_val = series.min()
            max_val = series.max()
            self.scalers[series.name] = {'min': min_val, 'max': max_val}
        else:
            scaler = self.scalers.get(series.name, {'min': 0, 'max': 1})
            min_val = scaler['min']
            max_val = scaler['max']
        
        normalized = (series - min_val) / (max_val - min_val)
        scaler_info = {'min': min_val, 'max': max_val}
        
        return normalized, scaler_info
    
    def _unit_vector(self, series: pd.Series) -> Tuple[pd.Series, Dict[str, Any]]:
        """Normalização por vetor unitário"""
        norm = np.sqrt(np.sum(series**2))
        if norm == 0:
            normalized = series
        else:
            normalized = series / norm
        
        scaler_info = {'norm': norm}
        return normalized, scaler_info
    
    def inverse_transform(self, data: pd.DataFrame, columns: List[str] = None) -> pd.DataFrame:
        """Desfaz a normalização"""
        if columns is None:
            columns = data.select_dtypes(include=[np.number]).columns.tolist()
        
        result = data.copy()
        
        for column in columns:
            if column not in data.columns or column not in self.scalers:
                continue
            
            scaler = self.scalers[column]
            
            if self.method == NormalizationMethod.STANDARD_SCALER:
                result[column] = result[column] * scaler['std'] + scaler['mean']
            elif self.method == NormalizationMethod.ROBUST_SCALER:
                result[column] = result[column] * scaler['iqr'] + scaler['median']
            elif self.method == NormalizationMethod.MIN_MAX_SCALER:
                result[column] = result[column] * (scaler['max'] - scaler['min']) + scaler['min']
            elif self.method == NormalizationMethod.UNIT_VECTOR:
                result[column] = result[column] * scaler['norm']
        
        return result

class TimeSeriesSynchronizer:
    """Sincronizador de séries temporais"""
    
    def __init__(self):
        logger.info("⏰ Sincronizador de séries temporais inicializado")
    
    def synchronize_series(self, data_dict: Dict[str, pd.DataFrame], 
                          frequency: DataFrequency = DataFrequency.MINUTE) -> Dict[str, pd.DataFrame]:
        """Sincroniza múltiplas séries temporais"""
        if not data_dict:
            return {}
        
        # Encontra o range temporal comum
        start_times = []
        end_times = []
        
        for symbol, df in data_dict.items():
            if not df.empty and 'timestamp' in df.columns:
                start_times.append(df['timestamp'].min())
                end_times.append(df['timestamp'].max())
        
        if not start_times:
            return data_dict
        
        common_start = max(start_times)
        common_end = min(end_times)
        
        # Cria índice temporal comum
        freq_map = {
            DataFrequency.SECOND: '1S',
            DataFrequency.MINUTE: '1T',
            DataFrequency.HOUR: '1H',
            DataFrequency.DAILY: '1D'
        }
        
        freq = freq_map.get(frequency, '1T')
        common_index = pd.date_range(start=common_start, end=common_end, freq=freq)
        
        # Sincroniza cada série
        synchronized_data = {}
        
        for symbol, df in data_dict.items():
            if df.empty or 'timestamp' not in df.columns:
                synchronized_data[symbol] = df
                continue
            
            # Define timestamp como índice
            df_temp = df.set_index('timestamp').sort_index()
            
            # Reamostra para a frequência comum
            df_resampled = self._resample_series(df_temp, freq)
            
            # Alinha com o índice comum
            df_aligned = df_resampled.reindex(common_index)
            
            # Restaura timestamp como coluna
            df_aligned = df_aligned.reset_index().rename(columns={'index': 'timestamp'})
            
            synchronized_data[symbol] = df_aligned
        
        return synchronized_data
    
    def _resample_series(self, df: pd.DataFrame, freq: str) -> pd.DataFrame:
        """Reamostra série temporal"""
        # Define como reamostrar cada tipo de dado
        agg_functions = {
            'open_price': 'first',
            'high_price': 'max',
            'low_price': 'min',
            'close_price': 'last',
            'volume': 'sum'
        }
        
        # Aplica apenas as colunas que existem
        existing_agg = {k: v for k, v in agg_functions.items() if k in df.columns}
        
        if existing_agg:
            resampled = df.resample(freq).agg(existing_agg)
        else:
            resampled = df.resample(freq).mean()
        
        return resampled.dropna(how='all')

class DataPreprocessingPipeline:
    """Pipeline completo de pré-processamento de dados"""
    
    def __init__(self, config: ProcessingConfig = None):
        self.config = config or ProcessingConfig()
        self.validator = DataValidator()
        self.outlier_detector = OutlierDetector(self.config.outlier_method)
        self.imputer = DataImputer(self.config.imputation_method)
        self.normalizer = DataNormalizer(self.config.normalization_method)
        self.synchronizer = TimeSeriesSynchronizer()
        
        # Estatísticas de processamento
        self.processing_stats = defaultdict(int)
        self.quality_reports = {}
        
        logger.info("🚀 Pipeline de pré-processamento inicializado")
    
    async def process_data_point(self, data_point: MarketDataPoint) -> Tuple[Optional[MarketDataPoint], List[str]]:
        """Processa um ponto de dado individual"""
        errors = []
        
        try:
            # Validação
            is_valid, validation_errors = self.validator.validate_data_point(data_point)
            if not is_valid:
                errors.extend(validation_errors)
                self.processing_stats['validation_errors'] += 1
                return None, errors
            
            # Detecção de outliers
            if self.config.detect_anomalies:
                # Converte para Series para detecção
                price_data = pd.Series([data_point.close_price])
                outliers = self.outlier_detector.detect_outliers(price_data)
                
                if outliers.iloc[0]:
                    errors.append("Outlier detectado")
                    self.processing_stats['outliers_detected'] += 1
                    # Pode decidir remover ou corrigir aqui
            
            # Atualiza qualidade
            if data_point.quality_score > 0.8:
                self.processing_stats['high_quality'] += 1
            elif data_point.quality_score > 0.5:
                self.processing_stats['medium_quality'] += 1
            else:
                self.processing_stats['low_quality'] += 1
            
            self.processing_stats['processed_points'] += 1
            
            return data_point, errors
            
        except Exception as e:
            errors.append(f"Erro no processamento: {e}")
            self.processing_stats['processing_errors'] += 1
            return None, errors
    
    async def process_dataframe(self, df: pd.DataFrame, symbol: str = None) -> Tuple[pd.DataFrame, DataQualityReport]:
        """Processa um DataFrame completo"""
        start_time = time.time()
        
        try:
            # Validação inicial
            is_valid, validation_errors = self.validator.validate_dataframe(df)
            if not is_valid:
                logger.warning(f"Erros de validação no DataFrame {symbol}: {validation_errors}")
            
            # Remove duplicatas
            if self.config.remove_duplicates:
                df = df.drop_duplicates()
                self.processing_stats['duplicates_removed'] += df.shape[0]
            
            # Ordena por timestamp
            if 'timestamp' in df.columns:
                df = df.sort_values('timestamp').reset_index(drop=True)
            
            # Trata dados faltantes
            if self.config.handle_missing_data:
                df = self.imputer.impute_data(df)
                self.processing_stats['missing_imputed'] += df.isna().sum().sum()
            
            # Detecção e tratamento de outliers
            if self.config.detect_anomalies:
                numeric_columns = df.select_dtypes(include=[np.number]).columns
                for column in numeric_columns:
                    if column in ['open_price', 'high_price', 'low_price', 'close_price']:
                        outliers = self.outlier_detector.detect_outliers(
                            df[column], 
                            self.config.outlier_threshold
                        )
                        
                        # Opção 1: Remove outliers
                        # df = df[~outliers]
                        
                        # Opção 2: Cap outliers (winsorization)
                        if outliers.any():
                            q1 = df[column].quantile(0.25)
                            q3 = df[column].quantile(0.75)
                            iqr = q3 - q1
                            lower_bound = q1 - 1.5 * iqr
                            upper_bound = q3 + 1.5 * iqr
                            
                            df[column] = df[column].clip(lower=lower_bound, upper_bound=upper_bound)
                            
                            self.processing_stats['outliers_handled'] += outliers.sum()
            
            # Normalização
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            if len(numeric_columns) > 0:
                df, scaler_info = self.normalizer.normalize_data(df)
                self.processing_stats['normalized_columns'] += len(numeric_columns)
            
            # Reamostragem se necessário
            if self.config.resample_frequency and 'timestamp' in df.columns:
                freq_map = {
                    DataFrequency.SECOND: '1S',
                    DataFrequency.MINUTE: '1T',
                    DataFrequency.HOUR: '1H',
                    DataFrequency.DAILY: '1D'
                }
                freq = freq_map.get(self.config.resample_frequency, '1T')
                
                df = df.set_index('timestamp')
                df = self.synchronizer._resample_series(df, freq)
                df = df.reset_index().rename(columns={'index': 'timestamp'})
            
            # Gera relatório de qualidade
            processing_time = time.time() - start_time
            quality_report = self._generate_quality_report(df, symbol, processing_time, validation_errors)
            
            self.quality_reports[symbol] = quality_report
            self.processing_stats['processed_dataframes'] += 1
            
            logger.info(f"✅ DataFrame {symbol} processado em {processing_time:.2f}s")
            
            return df, quality_report
            
        except Exception as e:
            logger.error(f"Erro ao processar DataFrame {symbol}: {e}")
            processing_time = time.time() - start_time
            
            # Relatório de erro
            error_report = DataQualityReport(
                symbol=symbol or "unknown",
                start_time=datetime.now(),
                end_time=datetime.now(),
                total_records=0,
                missing_values=0,
                duplicate_records=0,
                outliers_detected=0,
                data_quality_score=0.0,
                quality_level=DataQualityLevel.INVALID,
                issues_detected=[f"Erro no processamento: {e}"],
                processing_time=processing_time
            )
            
            return df, error_report
    
    async def process_multiple_series(self, data_dict: Dict[str, pd.DataFrame]) -> Dict[str, Tuple[pd.DataFrame, DataQualityReport]]:
        """Processa múltiplas séries temporais"""
        results = {}
        
        try:
            # Sincroniza séries se configurado
            if self.config.synchronize_time_series:
                data_dict = self.synchronizer.synchronize_series(
                    data_dict, 
                    self.config.resample_frequency or DataFrequency.MINUTE
                )
            
            # Processa cada série
            for symbol, df in data_dict.items():
                processed_df, quality_report = await self.process_dataframe(df, symbol)
                results[symbol] = (processed_df, quality_report)
            
            logger.info(f"✅ {len(results)} séries processadas")
            
        except Exception as e:
            logger.error(f"Erro ao processar múltiplas séries: {e}")
        
        return results
    
    def _generate_quality_report(self, df: pd.DataFrame, symbol: str, 
                               processing_time: float, validation_errors: List[str]) -> DataQualityReport:
        """Gera relatório de qualidade dos dados"""
        if df.empty:
            return DataQualityReport(
                symbol=symbol,
                start_time=datetime.now(),
                end_time=datetime.now(),
                total_records=0,
                missing_values=0,
                duplicate_records=0,
                outliers_detected=0,
                data_quality_score=0.0,
                quality_level=DataQualityLevel.INVALID,
                issues_detected=["DataFrame vazio"],
                processing_time=processing_time
            )
        
        # Calcula métricas
        total_records = len(df)
        missing_values = df.isna().sum().sum()
        duplicate_records = df.duplicated().sum()
        
        # Estima outliers (baseado na qualidade dos dados)
        outliers_detected = int(total_records * (1 - df['quality_score'].mean() if 'quality_score' in df.columns else 0.05))
        
        # Calcula score de qualidade
        completeness_score = 1 - (missing_values / (total_records * len(df.columns)))
        uniqueness_score = 1 - (duplicate_records / total_records)
        consistency_score = 0.9 if not validation_errors else 0.5
        
        data_quality_score = (completeness_score + uniqueness_score + consistency_score) / 3
        
        # Determina nível de qualidade
        if data_quality_score >= 0.9:
            quality_level = DataQualityLevel.EXCELLENT
        elif data_quality_score >= 0.8:
            quality_level = DataQualityLevel.GOOD
        elif data_quality_score >= 0.6:
            quality_level = DataQualityLevel.FAIR
        elif data_quality_score >= 0.4:
            quality_level = DataQualityLevel.POOR
        else:
            quality_level = DataQualityLevel.INVALID
        
        # Gera recomendações
        recommendations = []
        if missing_values > 0:
            recommendations.append(f"Considerar melhor estratégia de imputação ({missing_values} valores faltantes)")
        if duplicate_records > 0:
            recommendations.append(f"Remover duplicatas ({duplicate_records} registros)")
        if validation_errors:
            recommendations.append("Investigar erros de validação")
        if data_quality_score < self.config.quality_threshold:
            recommendations.append("Qualidade abaixo do threshold - revisar dados de origem")
        
        return DataQualityReport(
            symbol=symbol,
            start_time=df['timestamp'].min() if 'timestamp' in df.columns else datetime.now(),
            end_time=df['timestamp'].max() if 'timestamp' in df.columns else datetime.now(),
            total_records=total_records,
            missing_values=missing_values,
            duplicate_records=duplicate_records,
            outliers_detected=outliers_detected,
            data_quality_score=data_quality_score,
            quality_level=quality_level,
            issues_detected=validation_errors,
            recommendations=recommendations,
            processing_time=processing_time
        )
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de processamento"""
        return dict(self.processing_stats)
    
    def get_quality_reports(self) -> Dict[str, DataQualityReport]:
        """Retorna relatórios de qualidade"""
        return self.quality_reports.copy()
    
    def reset_stats(self):
        """Reseta estatísticas de processamento"""
        self.processing_stats.clear()
        self.quality_reports.clear()
        logger.info("📊 Estatísticas de processamento resetadas")

# Configuração padrão
DEFAULT_PROCESSING_CONFIG = ProcessingConfig(
    outlier_method=OutlierMethod.IQR,
    outlier_threshold=1.5,
    imputation_method=ImputationMethod.LINEAR_INTERPOLATION,
    normalization_method=NormalizationMethod.ROBUST_SCALER,
    remove_duplicates=True,
    handle_missing_data=True,
    detect_anomalies=True,
    validate_ranges=True,
    synchronize_time_series=True,
    resample_frequency=DataFrequency.MINUTE,
    quality_threshold=0.7
)

if __name__ == "__main__":
    # Exemplo de uso
    async def main():
        # Cria dados de exemplo
        dates = pd.date_range(start='2024-01-01', end='2024-01-10', freq='1H')
        np.random.seed(42)
        
        data = {
            'timestamp': dates,
            'open_price': 100 + np.random.randn(len(dates)) * 2,
            'high_price': 102 + np.random.randn(len(dates)) * 2,
            'low_price': 98 + np.random.randn(len(dates)) * 2,
            'close_price': 100 + np.random.randn(len(dates)) * 2,
            'volume': 1000000 + np.random.randn(len(dates)) * 100000
        }
        
        df = pd.DataFrame(data)
        
        # Introduz alguns problemas nos dados
        df.loc[5:7, 'close_price'] = np.nan  # Dados faltantes
        df.loc[10, 'close_price'] = 1000    # Outlier
        df = pd.concat([df, df.iloc[[0]]])   # Duplicata
        
        # Cria pipeline
        config = DEFAULT_PROCESSING_CONFIG
        pipeline = DataPreprocessingPipeline(config)
        
        # Processa dados
        processed_df, quality_report = await pipeline.process_dataframe(df, "EXAMPLE")
        
        print("📊 Relatório de Qualidade:")
        print(f"Símbolo: {quality_report.symbol}")
        print(f"Score: {quality_report.data_quality_score:.2f}")
        print(f"Nível: {quality_report.quality_level.label}")
        print(f"Registros: {quality_report.total_records}")
        print(f"Valores faltantes: {quality_report.missing_values}")
        print(f"Duplicatas: {quality_report.duplicate_records}")
        print(f"Outliers: {quality_report.outliers_detected}")
        print(f"Tempo de processamento: {quality_report.processing_time:.2f}s")
        print(f"Recomendações: {quality_report.recommendations}")
        
        print("\n📈 Estatísticas de Processamento:")
        stats = pipeline.get_processing_stats()
        for key, value in stats.items():
            print(f"{key}: {value}")
    
    asyncio.run(main())

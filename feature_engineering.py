"""
Feature Engineering - Engenharia de Atributos e Feature Selection
==============================================================
Seleção, extração e criação de características relevantes para modelos de IA
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import os
from pathlib import Path
import hashlib
import re
import math
import itertools

# Importações condicionais
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    from sklearn.feature_selection import (
        SelectKBest, SelectPercentile, RFE, RFECV,
        f_classif, f_regression, mutual_info_classif, mutual_info_regression,
        chi2, VarianceThreshold
    )
    from sklearn.decomposition import PCA, FastICA, TruncatedSVD, LatentDirichletAllocation
    from sklearn.preprocessing import PolynomialFeatures, StandardScaler
    from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
    from sklearn.linear_model import LassoCV, ElasticNetCV
    from sklearn.cluster import KMeans
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    import librosa
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

from config import settings
from core import get_logger, log_execution
from .data_collector import DataSample, DataType
from .data_preprocessor import ProcessingResult


class FeatureType(str, Enum):
    """Tipos de features"""
    NUMERICAL = "numerical"
    CATEGORICAL = "categorical"
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    TEMPORAL = "temporal"
    SPATIAL = "spatial"
    INTERACTION = "interaction"
    POLYNOMIAL = "polynomial"
    STATISTICAL = "statistical"
    DOMAIN_SPECIFIC = "domain_specific"


class SelectionMethod(str, Enum):
    """Métodos de seleção de features"""
    VARIANCE_THRESHOLD = "variance_threshold"
    CORRELATION_FILTER = "correlation_filter"
    MUTUAL_INFORMATION = "mutual_information"
    CHI_SQUARE = "chi_square"
    ANOVA_F = "anova_f"
    RECURSIVE_ELIMINATION = "recursive_elimination"
    LASSO = "lasso"
    RANDOM_FOREST = "random_forest"
    UNIVARIATE_SELECTION = "univariate_selection"
    PCA = "pca"
    LDA = "lda"


@dataclass
class FeatureConfig:
    """Configuração de engenharia de features"""
    feature_type: FeatureType
    method: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    target_columns: List[str] = field(default_factory=list)
    n_features: Optional[int] = None
    threshold: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'feature_type': self.feature_type.value,
            'method': self.method,
            'parameters': self.parameters,
            'target_columns': self.target_columns,
            'n_features': self.n_features,
            'threshold': self.threshold
        }


@dataclass
class FeatureSet:
    """Conjunto de features processadas"""
    name: str
    features: pd.DataFrame
    feature_names: List[str]
    feature_types: Dict[str, FeatureType]
    importance_scores: Optional[Dict[str, float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'feature_names': self.feature_names,
            'feature_types': {k: v.value for k, v in self.feature_types.items()},
            'importance_scores': self.importance_scores,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'n_features': len(self.feature_names),
            'shape': self.features.shape if hasattr(self.features, 'shape') else None
        }


class NumericalFeatureEngineer:
    """Engenheiro de features numéricas"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.features.numerical", "numerical_features")
    
    def create_statistical_features(self, df: pd.DataFrame, columns: List[str] = None) -> pd.DataFrame:
        """Cria features estatísticas"""
        if not PANDAS_AVAILABLE or not NUMPY_AVAILABLE:
            return df
        
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        result_df = df.copy()
        
        for col in columns:
            if col in df.columns:
                # Features básicas
                result_df[f'{col}_mean'] = df[col].mean()
                result_df[f'{col}_std'] = df[col].std()
                result_df[f'{col}_min'] = df[col].min()
                result_df[f'{col}_max'] = df[col].max()
                result_df[f'{col}_median'] = df[col].median()
                result_df[f'{col}_skew'] = df[col].skew()
                result_df[f'{col}_kurtosis'] = df[col].kurtosis()
                
                # Features de posição
                result_df[f'{col}_p25'] = df[col].quantile(0.25)
                result_df[f'{col}_p75'] = df[col].quantile(0.75)
                result_df[f'{col}_iqr'] = result_df[f'{col}_p75'] - result_df[f'{col}_p25']
                
                # Features de variação
                result_df[f'{col}_range'] = df[col].max() - df[col].min()
                result_df[f'{col}_cv'] = df[col].std() / (df[col].mean() + 1e-8)  # Coeficiente de variação
        
        return result_df
    
    def create_ratio_features(self, df: pd.DataFrame, column_pairs: List[Tuple[str, str]] = None) -> pd.DataFrame:
        """Cria features de razão"""
        if not PANDAS_AVAILABLE:
            return df
        
        if column_pairs is None:
            # Criar pares automaticamente para colunas numéricas
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            column_pairs = list(itertools.combinations(numeric_cols[:5], 2))  # Limitar para evitar explosão
        
        result_df = df.copy()
        
        for col1, col2 in column_pairs:
            if col1 in df.columns and col2 in df.columns:
                # Evitar divisão por zero
                safe_col2 = df[col2].replace(0, np.nan)
                result_df[f'{col1}_div_{col2}'] = df[col1] / safe_col2
                result_df[f'{col1}_mul_{col2}'] = df[col1] * df[col2]
                result_df[f'{col1}_sub_{col2}'] = df[col1] - df[col2]
                result_df[f'{col1}_add_{col2}'] = df[col1] + df[col2]
        
        return result_df
    
    def create_lag_features(self, df: pd.DataFrame, columns: List[str], lags: List[int] = [1, 2, 3]) -> pd.DataFrame:
        """Cria features de lag para dados temporais"""
        if not PANDAS_AVAILABLE:
            return df
        
        result_df = df.copy()
        
        for col in columns:
            if col in df.columns:
                for lag in lags:
                    result_df[f'{col}_lag_{lag}'] = df[col].shift(lag)
                    result_df[f'{col}_diff_{lag}'] = df[col].diff(lag)
                    result_df[f'{col}_pct_change_{lag}'] = df[col].pct_change(lag)
        
        return result_df
    
    def create_rolling_features(self, df: pd.DataFrame, columns: List[str], windows: List[int] = [3, 7, 14]) -> pd.DataFrame:
        """Cria features de janela móvel"""
        if not PANDAS_AVAILABLE:
            return df
        
        result_df = df.copy()
        
        for col in columns:
            if col in df.columns:
                for window in windows:
                    result_df[f'{col}_rolling_mean_{window}'] = df[col].rolling(window=window).mean()
                    result_df[f'{col}_rolling_std_{window}'] = df[col].rolling(window=window).std()
                    result_df[f'{col}_rolling_min_{window}'] = df[col].rolling(window=window).min()
                    result_df[f'{col}_rolling_max_{window}'] = df[col].rolling(window=window).max()
                    result_df[f'{col}_rolling_median_{window}'] = df[col].rolling(window=window).median()
        
        return result_df


class TextFeatureEngineer:
    """Engenheiro de features textuais"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.features.text", "text_features")
    
    def create_ngram_features(self, texts: List[str], n_range: Tuple[int, int] = (1, 2), top_n: int = 100) -> Dict[str, int]:
        """Cria features de n-gramas"""
        from collections import Counter
        
        all_ngrams = []
        
        for text in texts:
            words = text.lower().split()
            for n in range(n_range[0], n_range[1] + 1):
                for i in range(len(words) - n + 1):
                    ngram = ' '.join(words[i:i+n])
                    all_ngrams.append(ngram)
        
        # Contar n-gramas mais frequentes
        ngram_counts = Counter(all_ngrams)
        top_ngrams = dict(ngram_counts.most_common(top_n))
        
        return top_ngrams
    
    def create_sentiment_features(self, text: str) -> Dict[str, float]:
        """Cria features de sentimento (simplificado)"""
        # Lista de palavras positivas e negativas (simplificado)
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'like', 'best', 'awesome']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'hate', 'dislike', 'worst', 'poor', 'sad', 'angry']
        
        words = text.lower().split()
        
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        total_words = len(words)
        
        if total_words == 0:
            return {'positive_ratio': 0, 'negative_ratio': 0, 'sentiment_score': 0}
        
        positive_ratio = positive_count / total_words
        negative_ratio = negative_count / total_words
        sentiment_score = positive_ratio - negative_ratio
        
        return {
            'positive_ratio': positive_ratio,
            'negative_ratio': negative_ratio,
            'sentiment_score': sentiment_score,
            'positive_count': positive_count,
            'negative_count': negative_count
        }
    
    def create_readability_features(self, text: str) -> Dict[str, float]:
        """Cria features de legibilidade"""
        sentences = text.split('.')
        words = text.split()
        
        if not sentences or not words:
            return {}
        
        avg_sentence_length = len(words) / len(sentences)
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # Simplified Flesch Reading Ease
        if avg_sentence_length == 0:
            flesch_score = 0
        else:
            flesch_score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_word_length)
        
        return {
            'avg_sentence_length': avg_sentence_length,
            'avg_word_length': avg_word_length,
            'sentence_count': len(sentences),
            'word_count': len(words),
            'flesch_score': max(0, min(100, flesch_score))
        }
    
    def create_text_structure_features(self, text: str) -> Dict[str, int]:
        """Cria features de estrutura textual"""
        return {
            'char_count': len(text),
            'word_count': len(text.split()),
            'sentence_count': len(text.split('.')),
            'paragraph_count': len(text.split('\n\n')),
            'punctuation_count': len(re.findall(r'[^\w\s]', text)),
            'uppercase_count': sum(1 for c in text if c.isupper()),
            'digit_count': sum(1 for c in text if c.isdigit()),
            'space_count': text.count(' '),
            'tab_count': text.count('\t'),
            'newline_count': text.count('\n')
        }


class ImageFeatureEngineer:
    """Engenheiro de features de imagem"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.features.image", "image_features")
    
    def create_color_features(self, image) -> Dict[str, float]:
        """Cria features de cor"""
        if not CV2_AVAILABLE or not NUMPY_AVAILABLE:
            return {}
        
        # Converter para diferentes espaços de cor
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        
        features = {}
        
        # Features HSV
        features['h_mean'] = np.mean(hsv[:, :, 0])
        features['h_std'] = np.std(hsv[:, :, 0])
        features['s_mean'] = np.mean(hsv[:, :, 1])
        features['s_std'] = np.std(hsv[:, :, 1])
        features['v_mean'] = np.mean(hsv[:, :, 2])
        features['v_std'] = np.std(hsv[:, :, 2])
        
        # Features LAB
        features['l_mean'] = np.mean(lab[:, :, 0])
        features['a_mean'] = np.mean(lab[:, :, 1])
        features['b_mean'] = np.mean(lab[:, :, 2])
        
        # Features RGB
        for i, color in enumerate(['b', 'g', 'r']):
            channel = image[:, :, i]
            features[f'{color}_mean'] = np.mean(channel)
            features[f'{color}_std'] = np.std(channel)
            features[f'{color}_min'] = np.min(channel)
            features[f'{color}_max'] = np.max(channel)
        
        return features
    
    def create_texture_features(self, image) -> Dict[str, float]:
        """Cria features de textura"""
        if not CV2_AVAILABLE or not NUMPY_AVAILABLE:
            return {}
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        features = {}
        
        # Histograma de gradientes
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        
        features['gradient_magnitude_mean'] = np.mean(np.sqrt(sobelx**2 + sobely**2))
        features['gradient_magnitude_std'] = np.std(np.sqrt(sobelx**2 + sobely**2))
        
        # Local Binary Pattern (simplificado)
        features['lbp_contrast'] = np.std(gray)
        features['lbp_uniformity'] = len(np.unique(gray)) / (gray.shape[0] * gray.shape[1])
        
        return features
    
    def create_shape_features(self, image) -> Dict[str, float]:
        """Cria features de forma"""
        if not CV2_AVAILABLE or not NUMPY_AVAILABLE:
            return {}
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detectar bordas
        edges = cv2.Canny(gray, 50, 150)
        
        features = {
            'edge_density': np.sum(edges > 0) / (edges.shape[0] * edges.shape[1]),
            'edge_mean': np.mean(edges),
            'edge_std': np.std(edges)
        }
        
        # Contornos
        contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        features['contour_count'] = len(contours)
        
        if contours:
            areas = [cv2.contourArea(contour) for contour in contours]
            features['max_contour_area'] = max(areas)
            features['mean_contour_area'] = np.mean(areas)
            features['std_contour_area'] = np.std(areas)
        
        return features
    
    def create_fourier_features(self, image) -> Dict[str, float]:
        """Cria features de Fourier"""
        if not CV2_AVAILABLE or not NUMPY_AVAILABLE:
            return {}
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Transformada de Fourier
        f_transform = np.fft.fft2(gray)
        f_shift = np.fft.fftshift(f_transform)
        magnitude_spectrum = np.abs(f_shift)
        
        features = {
            'fourier_mean': np.mean(magnitude_spectrum),
            'fourier_std': np.std(magnitude_spectrum),
            'fourier_max': np.max(magnitude_spectrum),
            'fourier_energy': np.sum(magnitude_spectrum**2)
        }
        
        return features


class AudioFeatureEngineer:
    """Engenheiro de features de áudio"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.features.audio", "audio_features")
    
    def create_spectral_features(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """Cria features espectrais"""
        if not AUDIO_AVAILABLE or not NUMPY_AVAILABLE:
            return {}
        
        features = {}
        
        # Espectrograma
        stft = librosa.stft(audio_data)
        magnitude = np.abs(stft)
        
        # Features espectrais básicas
        features['spectral_centroid_mean'] = np.mean(librosa.feature.spectral_centroid(S=magnitude, sr=sample_rate)[0])
        features['spectral_centroid_std'] = np.std(librosa.feature.spectral_centroid(S=magnitude, sr=sample_rate)[0])
        features['spectral_bandwidth_mean'] = np.mean(librosa.feature.spectral_bandwidth(S=magnitude, sr=sample_rate)[0])
        features['spectral_rolloff_mean'] = np.mean(librosa.feature.spectral_rolloff(S=magnitude, sr=sample_rate)[0])
        features['spectral_flatness_mean'] = np.mean(librosa.feature.spectral_flatness(S=magnitude)[0])
        
        # Zero Crossing Rate
        features['zcr_mean'] = np.mean(librosa.feature.zero_crossing_rate(audio_data)[0])
        features['zcr_std'] = np.std(librosa.feature.zero_crossing_rate(audio_data)[0])
        
        return features
    
    def create_mel_features(self, audio_data: np.ndarray, sample_rate: int, n_mels: int = 13) -> Dict[str, float]:
        """Cria features MFCC e Mel"""
        if not AUDIO_AVAILABLE or not NUMPY_AVAILABLE:
            return {}
        
        features = {}
        
        # MFCC
        mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=n_mels)
        
        for i in range(n_mels):
            features[f'mfcc_{i}_mean'] = np.mean(mfccs[i])
            features[f'mfcc_{i}_std'] = np.std(mfccs[i])
            features[f'mfcc_{i}_min'] = np.min(mfccs[i])
            features[f'mfcc_{i}_max'] = np.max(mfccs[i])
        
        # Mel Spectrogram
        mel_spec = librosa.feature.melspectrogram(y=audio_data, sr=sample_rate)
        features['mel_mean'] = np.mean(mel_spec)
        features['mel_std'] = np.std(mel_spec)
        features['mel_max'] = np.max(mel_spec)
        
        return features
    
    def create_temporal_features(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, float]:
        """Cria features temporais"""
        if not AUDIO_AVAILABLE or not NUMPY_AVAILABLE:
            return {}
        
        features = {}
        
        # Features de amplitude
        features['rms_energy'] = np.sqrt(np.mean(audio_data**2))
        features['peak_amplitude'] = np.max(np.abs(audio_data))
        features['amplitude_std'] = np.std(audio_data)
        features['amplitude_range'] = np.max(audio_data) - np.min(audio_data)
        
        # Features de taxa de cruzamento por zero
        zero_crossings = librosa.feature.zero_crossing_rate(audio_data)[0]
        features['zcr_mean'] = np.mean(zero_crossings)
        features['zcr_std'] = np.std(zero_crossings)
        
        # Features de duração
        features['duration'] = len(audio_data) / sample_rate
        
        return features


class FeatureSelector:
    """Seletor de features"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.features.selector", "feature_selector")
    
    def variance_threshold_selection(self, X: pd.DataFrame, threshold: float = 0.0) -> pd.DataFrame:
        """Seleção baseada em limiar de variância"""
        if not SKLEARN_AVAILABLE or not PANDAS_AVAILABLE:
            return X
        
        selector = VarianceThreshold(threshold=threshold)
        X_selected = selector.fit_transform(X)
        
        selected_features = X.columns[selector.get_support()]
        return pd.DataFrame(X_selected, columns=selected_features, index=X.index)
    
    def correlation_filter(self, X: pd.DataFrame, threshold: float = 0.95) -> pd.DataFrame:
        """Filtra features altamente correlacionadas"""
        if not PANDAS_AVAILABLE or not NUMPY_AVAILABLE:
            return X
        
        # Calcular matriz de correlação
        corr_matrix = X.corr().abs()
        
        # Encontrar pares altamente correlacionados
        upper_triangle = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
        
        # Remover features correlacionadas
        to_drop = [column for column in upper_triangle.columns if any(upper_triangle[column] > threshold)]
        
        X_filtered = X.drop(columns=to_drop)
        
        self.logger.info(f"Removed {len(to_drop)} highly correlated features")
        return X_filtered
    
    def mutual_information_selection(self, X: pd.DataFrame, y: pd.Series, k: int = 10) -> pd.DataFrame:
        """Seleção baseada em informação mútua"""
        if not SKLEARN_AVAILABLE or not PANDAS_AVAILABLE:
            return X
        
        selector = SelectKBest(score_func=mutual_info_classif, k=k)
        X_selected = selector.fit_transform(X, y)
        
        selected_features = X.columns[selector.get_support()]
        return pd.DataFrame(X_selected, columns=selected_features, index=X.index)
    
    def recursive_feature_elimination(self, X: pd.DataFrame, y: pd.Series, n_features: int = 10) -> pd.DataFrame:
        """Eliminação recursiva de features"""
        if not SKLEARN_AVAILABLE or not PANDAS_AVAILABLE:
            return X
        
        estimator = RandomForestClassifier(n_estimators=100, random_state=42)
        selector = RFE(estimator=estimator, n_features_to_select=n_features)
        
        X_selected = selector.fit_transform(X, y)
        selected_features = X.columns[selector.get_support()]
        
        return pd.DataFrame(X_selected, columns=selected_features, index=X.index)
    
    def lasso_selection(self, X: pd.DataFrame, y: pd.Series) -> pd.DataFrame:
        """Seleção usando Lasso"""
        if not SKLEARN_AVAILABLE or not PANDAS_AVAILABLE:
            return X
        
        lasso = LassoCV(cv=5, random_state=42)
        lasso.fit(X, y)
        
        # Features com coeficiente não zero
        selected_features = X.columns[lasso.coef_ != 0]
        X_selected = X[selected_features]
        
        importance_scores = dict(zip(selected_features, np.abs(lasso.coef_[lasso.coef_ != 0])))
        
        self.logger.info(f"Lasso selected {len(selected_features)} features")
        return X_selected, importance_scores
    
    def random_forest_importance(self, X: pd.DataFrame, y: pd.Series, threshold: float = 0.01) -> Tuple[pd.DataFrame, Dict[str, float]]:
        """Importância baseada em Random Forest"""
        if not SKLEARN_AVAILABLE or not PANDAS_AVAILABLE:
            return X, {}
        
        rf = RandomForestClassifier(n_estimators=100, random_state=42)
        rf.fit(X, y)
        
        importance_scores = dict(zip(X.columns, rf.feature_importances_))
        
        # Selecionar features acima do limiar
        selected_features = [feat for feat, imp in importance_scores.items() if imp > threshold]
        X_selected = X[selected_features]
        
        self.logger.info(f"Random Forest selected {len(selected_features)} features with importance > {threshold}")
        return X_selected, importance_scores


class FeatureEngineering:
    """Engenharia principal de features"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.features.engineering", "feature_engineering")
        
        # Inicializar engenheiros especializados
        self.numerical_engineer = NumericalFeatureEngineer()
        self.text_engineer = TextFeatureEngineer()
        self.image_engineer = ImageFeatureEngineer()
        self.audio_engineer = AudioFeatureEngineer()
        self.selector = FeatureSelector()
        
        self.feature_sets = {}
        self.engineering_history = []
    
    @log_execution(component="features", operation="engineer_features")
    async def engineer_features(self, data: Any, data_type: DataType, configs: List[FeatureConfig], target: Optional[Any] = None) -> FeatureSet:
        """Engenheira features baseado nos dados e configurações"""
        start_time = time.time()
        self.logger.info(f"Engineering features for {data_type.value} data with {len(configs)} configurations")
        
        feature_name = f"features_{data_type.value}_{int(time.time())}"
        
        try:
            # Converter dados para DataFrame se necessário
            if isinstance(data, pd.DataFrame):
                df = data.copy()
            elif data_type == DataType.STRUCTURED and PANDAS_AVAILABLE:
                df = pd.DataFrame(data)
            else:
                # Criar DataFrame a partir dos dados
                df = self._create_dataframe_from_data(data, data_type)
            
            # Aplicar engenharia de features
            for config in configs:
                df = await self._apply_feature_engineering(df, data_type, config)
            
            # Seleção de features se target fornecido
            importance_scores = None
            if target is not None and SKLEARN_AVAILABLE and PANDAS_AVAILABLE:
                df, importance_scores = self._select_features(df, target)
            
            # Criar FeatureSet
            feature_types = self._determine_feature_types(df.columns, configs)
            
            feature_set = FeatureSet(
                name=feature_name,
                features=df,
                feature_names=list(df.columns),
                feature_types=feature_types,
                importance_scores=importance_scores,
                metadata={
                    'data_type': data_type.value,
                    'original_shape': data.shape if hasattr(data, 'shape') else len(data),
                    'engineering_time': time.time() - start_time,
                    'configs_applied': [config.to_dict() for config in configs]
                }
            )
            
            self.feature_sets[feature_name] = feature_set
            self.engineering_history.append(feature_set.to_dict())
            
            self.logger.info(f"Feature engineering completed: {len(df.columns)} features created")
            return feature_set
        
        except Exception as e:
            self.logger.error(f"Error in feature engineering: {e}")
            raise
    
    async def _apply_feature_engineering(self, df: pd.DataFrame, data_type: DataType, config: FeatureConfig) -> pd.DataFrame:
        """Aplica engenharia de features específica"""
        if config.feature_type == FeatureType.NUMERICAL:
            if config.method == "statistical":
                return self.numerical_engineer.create_statistical_features(df, config.target_columns)
            elif config.method == "ratio":
                return self.numerical_engineer.create_ratio_features(df)
            elif config.method == "lag":
                return self.numerical_engineer.create_lag_features(df, config.target_columns, config.parameters.get('lags', [1, 2, 3]))
            elif config.method == "rolling":
                return self.numerical_engineer.create_rolling_features(df, config.target_columns, config.parameters.get('windows', [3, 7, 14]))
        
        elif config.feature_type == FeatureType.TEXT:
            # Para features textuais, criar colunas adicionais
            if 'text' in df.columns:
                text_features = []
                for text in df['text']:
                    if config.method == "sentiment":
                        features = self.text_engineer.create_sentiment_features(str(text))
                    elif config.method == "readability":
                        features = self.text_engineer.create_readability_features(str(text))
                    elif config.method == "structure":
                        features = self.text_engineer.create_text_structure_features(str(text))
                    else:
                        features = {}
                    text_features.append(features)
                
                # Adicionar features ao DataFrame
                if text_features:
                    feature_df = pd.DataFrame(text_features)
                    df = pd.concat([df.reset_index(drop=True), feature_df], axis=1)
        
        elif config.feature_type == FeatureType.IMAGE:
            # Para features de imagem (simplificado)
            pass  # Implementar conforme necessário
        
        elif config.feature_type == FeatureType.AUDIO:
            # Para features de áudio (simplificado)
            pass  # Implementar conforme necessário
        
        return df
    
    def _create_dataframe_from_data(self, data: Any, data_type: DataType) -> pd.DataFrame:
        """Cria DataFrame a partir dos dados"""
        if not PANDAS_AVAILABLE:
            raise ImportError("pandas is required for feature engineering")
        
        if data_type == DataType.TEXT:
            return pd.DataFrame({'text': [data] if isinstance(data, str) else data})
        elif data_type == DataType.STRUCTURED:
            return pd.DataFrame(data)
        else:
            # Para outros tipos, criar DataFrame genérico
            return pd.DataFrame({'data': [data]})
    
    def _determine_feature_types(self, columns: List[str], configs: List[FeatureConfig]) -> Dict[str, FeatureType]:
        """Determina tipos de features"""
        feature_types = {}
        
        for col in columns:
            # Baseado no nome da coluna e configurações aplicadas
            if any('_mean' in col or '_std' in col or '_min' in col or '_max' in col for col in columns):
                feature_types[col] = FeatureType.STATISTICAL
            elif any('_lag_' in col or '_diff_' in col or '_rolling_' in col for col in columns):
                feature_types[col] = FeatureType.TEMPORAL
            elif any('_div_' in col or '_mul_' in col or '_add_' in col or '_sub_' in col for col in columns):
                feature_types[col] = FeatureType.INTERACTION
            elif any('sentiment' in col or 'readability' in col for col in columns):
                feature_types[col] = FeatureType.TEXT
            else:
                feature_types[col] = FeatureType.NUMERICAL
        
        return feature_types
    
    def _select_features(self, X: pd.DataFrame, y: pd.Series) -> Tuple[pd.DataFrame, Dict[str, float]]:
        """Seleciona features automaticamente"""
        if not SKLEARN_AVAILABLE:
            return X, {}
        
        # Tentar diferentes métodos de seleção
        try:
            # Remover features com baixa variância
            X = self.selector.variance_threshold_selection(X, threshold=0.01)
            
            # Remover features altamente correlacionadas
            X = self.selector.correlation_filter(X, threshold=0.95)
            
            # Seleção baseada em importância
            X, importance_scores = self.selector.random_forest_importance(X, y, threshold=0.01)
            
            return X, importance_scores
        
        except Exception as e:
            self.logger.error(f"Error in feature selection: {e}")
            return X, {}
    
    def create_standard_pipeline(self, data_type: DataType) -> List[FeatureConfig]:
        """Cria pipeline padrão para tipo de dado"""
        pipelines = {
            DataType.STRUCTURED: [
                FeatureConfig(
                    feature_type=FeatureType.NUMERICAL,
                    method="statistical"
                ),
                FeatureConfig(
                    feature_type=FeatureType.NUMERICAL,
                    method="ratio"
                )
            ],
            
            DataType.TEXT: [
                FeatureConfig(
                    feature_type=FeatureType.TEXT,
                    method="structure"
                ),
                FeatureConfig(
                    feature_type=FeatureType.TEXT,
                    method="sentiment"
                ),
                FeatureConfig(
                    feature_type=FeatureType.TEXT,
                    method="readability"
                )
            ],
            
            DataType.IMAGE: [
                FeatureConfig(
                    feature_type=FeatureType.IMAGE,
                    method="color"
                ),
                FeatureConfig(
                    feature_type=FeatureType.IMAGE,
                    method="texture"
                )
            ],
            
            DataType.AUDIO: [
                FeatureConfig(
                    feature_type=FeatureType.AUDIO,
                    method="spectral"
                ),
                FeatureConfig(
                    feature_type=FeatureType.AUDIO,
                    method="temporal"
                )
            ]
        }
        
        return pipelines.get(data_type, [])
    
    async def engineer_batch(self, data_list: List[Tuple[Any, DataType]], configs: List[FeatureConfig]) -> List[FeatureSet]:
        """Engenheira features em lote"""
        results = []
        
        for data, data_type in data_list:
            try:
                feature_set = await self.engineer_features(data, data_type, configs)
                results.append(feature_set)
            except Exception as e:
                self.logger.error(f"Error engineering features for item: {e}")
                continue
        
        return results
    
    def get_feature_set(self, name: str) -> Optional[FeatureSet]:
        """Retorna um conjunto de features específico"""
        return self.feature_sets.get(name)
    
    def get_engineering_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de engenharia de features"""
        stats = {
            'total_feature_sets': len(self.feature_sets),
            'engineering_history_count': len(self.engineering_history),
            'available_feature_types': [ft.value for ft in FeatureType],
            'available_selection_methods': [sm.value for sm in SelectionMethod]
        }
        
        # Estatísticas por tipo
        type_counts = {}
        for feature_set in self.feature_sets.values():
            data_type = feature_set.metadata.get('data_type', 'unknown')
            type_counts[data_type] = type_counts.get(data_type, 0) + 1
        
        stats['feature_sets_by_type'] = type_counts
        
        return stats


# Função de conveniência
_feature_engineering_instance = None

def get_feature_engineering() -> FeatureEngineering:
    """Obtém instância singleton do engenheiro de features"""
    global _feature_engineering_instance
    if _feature_engineering_instance is None:
        _feature_engineering_instance = FeatureEngineering()
    return _feature_engineering_instance

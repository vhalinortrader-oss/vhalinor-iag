"""
Data Preprocessor - Pré-processamento de Dados
============================================
Limpeza, normalização e transformação de dados brutos
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
import base64
import mimetypes

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
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    import librosa
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

try:
    from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, LabelEncoder, OneHotEncoder
    from sklearn.impute import SimpleImputer, KNNImputer
    from sklearn.feature_selection import SelectKBest, f_classif, mutual_info_classif
    from sklearn.decomposition import PCA
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import nltk
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.corpus import stopwords
    from nltk.stem import PorterStemmer, WordNetLemmatizer
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

from config import settings
from core import get_logger, log_execution
from .data_collector import DataSample, DataType


class ProcessingOperation(str, Enum):
    """Operações de pré-processamento"""
    CLEANING = "cleaning"
    NORMALIZATION = "normalization"
    TRANSFORMATION = "transformation"
    FEATURE_ENGINEERING = "feature_engineering"
    DIMENSIONALITY_REDUCTION = "dimensionality_reduction"
    OUTLIER_DETECTION = "outlier_detection"
    MISSING_VALUE_HANDLING = "missing_value_handling"


class CleaningMethod(str, Enum):
    """Métodos de limpeza"""
    REMOVE_NULLS = "remove_nulls"
    FILL_NULLS = "fill_nulls"
    REMOVE_DUPLICATES = "remove_duplicates"
    REMOVE_OUTLIERS = "remove_outliers"
    TEXT_CLEANING = "text_cleaning"
    IMAGE_DENOISING = "image_denoising"
    AUDIO_NOISE_REDUCTION = "audio_noise_reduction"


class NormalizationMethod(str, Enum):
    """Métodos de normalização"""
    STANDARD_SCALER = "standard_scaler"
    MIN_MAX_SCALER = "min_max_scaler"
    ROBUST_SCALER = "robust_scaler"
    UNIT_VECTOR = "unit_vector"
    LOG_TRANSFORM = "log_transform"
    BOX_COX = "box_cox"


@dataclass
class ProcessingConfig:
    """Configuração de pré-processamento"""
    operation: ProcessingOperation
    method: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    target_columns: List[str] = field(default_factory=list)
    condition: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'operation': self.operation.value,
            'method': self.method,
            'parameters': self.parameters,
            'target_columns': self.target_columns,
            'condition': self.condition
        }


@dataclass
class ProcessingResult:
    """Resultado do pré-processamento"""
    original_sample: DataSample
    processed_data: Any
    applied_operations: List[str]
    processing_metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'original_sample_id': self.original_sample.id,
            'applied_operations': self.applied_operations,
            'processing_metadata': self.processing_metadata,
            'processing_time': self.processing_time,
            'timestamp': self.timestamp.isoformat()
        }


class TextPreprocessor:
    """Pré-processador de dados textuais"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.preprocessor.text", "text_preprocessor")
        self.stemmer = PorterStemmer() if NLTK_AVAILABLE else None
        self.lemmatizer = WordNetLemmatizer() if NLTK_AVAILABLE else None
        self.stop_words = set(stopwords.words('english')) if NLTK_AVAILABLE else set()
    
    async def clean_text(self, text: str, config: ProcessingConfig) -> str:
        """Limpa texto baseado na configuração"""
        try:
            cleaned_text = text
            
            # Remover caracteres especiais
            if config.parameters.get('remove_special_chars', True):
                cleaned_text = re.sub(r'[^\w\s]', '', cleaned_text)
            
            # Converter para minúsculas
            if config.parameters.get('lowercase', True):
                cleaned_text = cleaned_text.lower()
            
            # Remover números
            if config.parameters.get('remove_numbers', False):
                cleaned_text = re.sub(r'\d+', '', cleaned_text)
            
            # Remover espaços extras
            if config.parameters.get('remove_extra_spaces', True):
                cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
            
            # Tokenização
            if config.parameters.get('tokenize', False):
                if NLTK_AVAILABLE:
                    tokens = word_tokenize(cleaned_text)
                else:
                    tokens = cleaned_text.split()
                
                # Remover stop words
                if config.parameters.get('remove_stopwords', True):
                    tokens = [token for token in tokens if token not in self.stop_words]
                
                # Stemming
                if config.parameters.get('stemming', False) and self.stemmer:
                    tokens = [self.stemmer.stem(token) for token in tokens]
                
                # Lemmatization
                if config.parameters.get('lemmatization', False) and self.lemmatizer:
                    tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
                
                cleaned_text = ' '.join(tokens)
            
            return cleaned_text
        
        except Exception as e:
            self.logger.error(f"Error cleaning text: {e}")
            return text
    
    async def extract_features(self, text: str) -> Dict[str, Any]:
        """Extrai features do texto"""
        try:
            features = {
                'char_count': len(text),
                'word_count': len(text.split()),
                'sentence_count': len(text.split('.')) if '.' in text else 1,
                'avg_word_length': np.mean([len(word) for word in text.split()]) if text.split() else 0,
                'punctuation_count': len(re.findall(r'[^\w\s]', text)),
                'uppercase_count': sum(1 for c in text if c.isupper()),
                'lowercase_count': sum(1 for c in text if c.islower()),
                'digit_count': sum(1 for c in text if c.isdigit()),
                'space_count': text.count(' ')
            }
            
            if NLTK_AVAILABLE:
                # Features NLTK
                tokens = word_tokenize(text.lower())
                sentences = sent_tokenize(text)
                
                features.update({
                    'unique_words': len(set(tokens)),
                    'lexical_diversity': len(set(tokens)) / len(tokens) if tokens else 0,
                    'avg_sentence_length': np.mean([len(sent.split()) for sent in sentences]) if sentences else 0
                })
            
            return features
        
        except Exception as e:
            self.logger.error(f"Error extracting text features: {e}")
            return {}


class ImagePreprocessor:
    """Pré-processador de dados de imagem"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.preprocessor.image", "image_preprocessor")
    
    async def resize_image(self, image, target_size: Tuple[int, int]) -> Any:
        """Redimensiona imagem"""
        try:
            if not CV2_AVAILABLE:
                return image
            
            return cv2.resize(image, target_size)
        except Exception as e:
            self.logger.error(f"Error resizing image: {e}")
            return image
    
    async def normalize_image(self, image, method: str = "min_max") -> Any:
        """Normaliza valores de pixel"""
        try:
            if not NUMPY_AVAILABLE:
                return image
            
            if method == "min_max":
                return image.astype(np.float32) / 255.0
            elif method == "z_score":
                mean = np.mean(image)
                std = np.std(image)
                return (image - mean) / (std + 1e-8)
            else:
                return image
        except Exception as e:
            self.logger.error(f"Error normalizing image: {e}")
            return image
    
    async def denoise_image(self, image) -> Any:
        """Remove ruído da imagem"""
        try:
            if not CV2_AVAILABLE:
                return image
            
            return cv2.fastNlMeansDenoisingColored(image)
        except Exception as e:
            self.logger.error(f"Error denoising image: {e}")
            return image
    
    async def extract_features(self, image) -> Dict[str, Any]:
        """Extrai features da imagem"""
        try:
            if not NUMPY_AVAILABLE:
                return {}
            
            features = {
                'height': image.shape[0],
                'width': image.shape[1],
                'channels': image.shape[2] if len(image.shape) > 2 else 1,
                'aspect_ratio': image.shape[1] / image.shape[0],
                'mean_pixel_value': np.mean(image),
                'std_pixel_value': np.std(image),
                'min_pixel_value': np.min(image),
                'max_pixel_value': np.max(image)
            }
            
            if len(image.shape) == 3:
                # Features por canal
                for i in range(image.shape[2]):
                    channel = image[:, :, i]
                    features.update({
                        f'channel_{i}_mean': np.mean(channel),
                        f'channel_{i}_std': np.std(channel),
                        f'channel_{i}_min': np.min(channel),
                        f'channel_{i}_max': np.max(channel)
                    })
            
            return features
        except Exception as e:
            self.logger.error(f"Error extracting image features: {e}")
            return {}


class AudioPreprocessor:
    """Pré-processador de dados de áudio"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.preprocessor.audio", "audio_preprocessor")
    
    async def normalize_audio(self, audio_data: np.ndarray, method: str = "peak") -> np.ndarray:
        """Normaliza áudio"""
        try:
            if not NUMPY_AVAILABLE:
                return audio_data
            
            if method == "peak":
                max_val = np.max(np.abs(audio_data))
                return audio_data / (max_val + 1e-8)
            elif method == "rms":
                rms = np.sqrt(np.mean(audio_data ** 2))
                return audio_data / (rms + 1e-8)
            else:
                return audio_data
        except Exception as e:
            self.logger.error(f"Error normalizing audio: {e}")
            return audio_data
    
    async def remove_silence(self, audio_data: np.ndarray, sample_rate: int, threshold: float = 0.01) -> np.ndarray:
        """Remove silêncio do áudio"""
        try:
            if not AUDIO_AVAILABLE:
                return audio_data
            
            # Usar librosa para remover silêncio
            trimmed, _ = librosa.effects.trim(audio_data, top_db=20)
            return trimmed
        except Exception as e:
            self.logger.error(f"Error removing silence: {e}")
            return audio_data
    
    async def extract_features(self, audio_data: np.ndarray, sample_rate: int) -> Dict[str, Any]:
        """Extrai features do áudio"""
        try:
            if not AUDIO_AVAILABLE or not NUMPY_AVAILABLE:
                return {}
            
            features = {
                'duration': len(audio_data) / sample_rate,
                'sample_rate': sample_rate,
                'max_amplitude': np.max(np.abs(audio_data)),
                'rms_energy': np.sqrt(np.mean(audio_data ** 2)),
                'zero_crossing_rate': np.mean(librosa.feature.zero_crossing_rate(audio_data)[0]),
                'spectral_centroid': np.mean(librosa.feature.spectral_centroid(audio_data, sr=sample_rate)[0]),
                'spectral_rolloff': np.mean(librosa.feature.spectral_rolloff(audio_data, sr=sample_rate)[0]),
                'spectral_bandwidth': np.mean(librosa.feature.spectral_bandwidth(audio_data, sr=sample_rate)[0])
            }
            
            # MFCC features
            mfccs = librosa.feature.mfcc(audio_data, sr=sample_rate, n_mfcc=13)
            for i in range(13):
                features[f'mfcc_{i}_mean'] = np.mean(mfccs[i])
                features[f'mfcc_{i}_std'] = np.std(mfccs[i])
            
            return features
        except Exception as e:
            self.logger.error(f"Error extracting audio features: {e}")
            return {}


class StructuredDataPreprocessor:
    """Pré-processador de dados estruturados"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.preprocessor.structured", "structured_preprocessor")
        self.scalers = {}
        self.encoders = {}
        self.imputers = {}
    
    async def handle_missing_values(self, data: pd.DataFrame, config: ProcessingConfig) -> pd.DataFrame:
        """Lida com valores ausentes"""
        try:
            if not PANDAS_AVAILABLE:
                return data
            
            method = config.method
            target_columns = config.target_columns or data.columns.tolist()
            
            processed_data = data.copy()
            
            if method == "remove":
                # Remover linhas com valores ausentes
                processed_data = processed_data.dropna(subset=target_columns)
            
            elif method == "fill_mean":
                # Preencher com média
                for col in target_columns:
                    if processed_data[col].dtype in ['int64', 'float64']:
                        processed_data[col].fillna(processed_data[col].mean(), inplace=True)
            
            elif method == "fill_median":
                # Preencher com mediana
                for col in target_columns:
                    if processed_data[col].dtype in ['int64', 'float64']:
                        processed_data[col].fillna(processed_data[col].median(), inplace=True)
            
            elif method == "fill_mode":
                # Preencher com moda
                for col in target_columns:
                    processed_data[col].fillna(processed_data[col].mode().iloc[0], inplace=True)
            
            elif method == "fill_forward":
                # Preencher com valor anterior
                processed_data[target_columns] = processed_data[target_columns].fillna(method='ffill')
            
            elif method == "interpolate":
                # Interpolação
                for col in target_columns:
                    if processed_data[col].dtype in ['int64', 'float64']:
                        processed_data[col] = processed_data[col].interpolate()
            
            return processed_data
        
        except Exception as e:
            self.logger.error(f"Error handling missing values: {e}")
            return data
    
    async def remove_outliers(self, data: pd.DataFrame, config: ProcessingConfig) -> pd.DataFrame:
        """Remove outliers"""
        try:
            if not PANDAS_AVAILABLE or not NUMPY_AVAILABLE:
                return data
            
            method = config.method
            target_columns = config.target_columns or data.select_dtypes(include=[np.number]).columns.tolist()
            
            processed_data = data.copy()
            
            for col in target_columns:
                if method == "iqr":
                    Q1 = processed_data[col].quantile(0.25)
                    Q3 = processed_data[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower_bound = Q1 - 1.5 * IQR
                    upper_bound = Q3 + 1.5 * IQR
                    processed_data = processed_data[(processed_data[col] >= lower_bound) & (processed_data[col] <= upper_bound)]
                
                elif method == "z_score":
                    z_scores = np.abs((processed_data[col] - processed_data[col].mean()) / processed_data[col].std())
                    threshold = config.parameters.get('threshold', 3)
                    processed_data = processed_data[z_scores < threshold]
                
                elif method == "isolation_forest":
                    if SKLEARN_AVAILABLE:
                        from sklearn.ensemble import IsolationForest
                        iso_forest = IsolationForest(contamination=0.1, random_state=42)
                        outliers = iso_forest.fit_predict(processed_data[[col]])
                        processed_data = processed_data[outliers == 1]
            
            return processed_data
        
        except Exception as e:
            self.logger.error(f"Error removing outliers: {e}")
            return data
    
    async def normalize_data(self, data: pd.DataFrame, config: ProcessingConfig) -> pd.DataFrame:
        """Normaliza dados"""
        try:
            if not PANDAS_AVAILABLE or not SKLEARN_AVAILABLE:
                return data
            
            method = config.method
            target_columns = config.target_columns or data.select_dtypes(include=[np.number]).columns.tolist()
            
            processed_data = data.copy()
            
            if method == "standard_scaler":
                scaler = StandardScaler()
                processed_data[target_columns] = scaler.fit_transform(processed_data[target_columns])
                self.scalers[f"standard_{config.target_columns}"] = scaler
            
            elif method == "min_max_scaler":
                scaler = MinMaxScaler()
                processed_data[target_columns] = scaler.fit_transform(processed_data[target_columns])
                self.scalers[f"minmax_{config.target_columns}"] = scaler
            
            elif method == "robust_scaler":
                scaler = RobustScaler()
                processed_data[target_columns] = scaler.fit_transform(processed_data[target_columns])
                self.scalers[f"robust_{config.target_columns}"] = scaler
            
            return processed_data
        
        except Exception as e:
            self.logger.error(f"Error normalizing data: {e}")
            return data
    
    async def encode_categorical(self, data: pd.DataFrame, config: ProcessingConfig) -> pd.DataFrame:
        """Codifica variáveis categóricas"""
        try:
            if not PANDAS_AVAILABLE or not SKLEARN_AVAILABLE:
                return data
            
            method = config.method
            target_columns = config.target_columns or data.select_dtypes(include=['object']).columns.tolist()
            
            processed_data = data.copy()
            
            for col in target_columns:
                if method == "label_encoder":
                    encoder = LabelEncoder()
                    processed_data[col] = encoder.fit_transform(processed_data[col])
                    self.encoders[f"label_{col}"] = encoder
                
                elif method == "one_hot":
                    encoder = OneHotEncoder(sparse=False, drop='first')
                    encoded = encoder.fit_transform(processed_data[[col]])
                    encoded_df = pd.DataFrame(encoded, columns=[f"{col}_{i}" for i in range(encoded.shape[1])])
                    processed_data = pd.concat([processed_data.drop(col, axis=1), encoded_df], axis=1)
                    self.encoders[f"onehot_{col}"] = encoder
            
            return processed_data
        
        except Exception as e:
            self.logger.error(f"Error encoding categorical data: {e}")
            return data


class DataPreprocessor:
    """Pré-processador principal de dados"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.preprocessor.main", "data_preprocessor")
        
        # Inicializar pré-processadores especializados
        self.text_preprocessor = TextPreprocessor()
        self.image_preprocessor = ImagePreprocessor()
        self.audio_preprocessor = AudioPreprocessor()
        self.structured_preprocessor = StructuredDataPreprocessor()
        
        self.processing_history = []
        self.processing_pipelines = {}
    
    @log_execution(component="preprocessor", operation="preprocess_data")
    async def preprocess_data(self, sample: DataSample, pipeline: List[ProcessingConfig]) -> ProcessingResult:
        """Pré-processa dados baseado no pipeline"""
        start_time = time.time()
        self.logger.info(f"Preprocessing {sample.data_type.value} data with {len(pipeline)} operations")
        
        processed_data = sample.content
        applied_operations = []
        processing_metadata = {}
        
        try:
            for i, config in enumerate(pipeline):
                operation_name = f"{config.operation.value}_{config.method}"
                applied_operations.append(operation_name)
                
                # Aplicar operação baseada no tipo de dado
                if sample.data_type == DataType.TEXT:
                    processed_data = await self._preprocess_text(processed_data, config)
                
                elif sample.data_type == DataType.IMAGE:
                    processed_data = await self._preprocess_image(processed_data, config)
                
                elif sample.data_type == DataType.AUDIO:
                    processed_data = await self._preprocess_audio(processed_data, config)
                
                elif sample.data_type == DataType.STRUCTURED:
                    processed_data = await self._preprocess_structured(processed_data, config)
                
                # Extrair features se solicitado
                if config.operation == ProcessingOperation.FEATURE_ENGINEERING:
                    features = await self._extract_features(sample.data_type, processed_data)
                    processing_metadata[f'features_{i}'] = features
            
            processing_time = time.time() - start_time
            
            result = ProcessingResult(
                original_sample=sample,
                processed_data=processed_data,
                applied_operations=applied_operations,
                processing_metadata=processing_metadata,
                processing_time=processing_time
            )
            
            self.processing_history.append(result)
            self.logger.info(f"Preprocessing completed in {processing_time:.3f}s")
            
            return result
        
        except Exception as e:
            self.logger.error(f"Error preprocessing data: {e}")
            raise
    
    async def _preprocess_text(self, text: str, config: ProcessingConfig) -> Union[str, Dict[str, Any]]:
        """Pré-processa dados textuais"""
        if config.operation == ProcessingOperation.CLEANING:
            return await self.text_preprocessor.clean_text(text, config)
        
        elif config.operation == ProcessingOperation.FEATURE_ENGINEERING:
            features = await self.text_preprocessor.extract_features(text)
            return {'text': text, 'features': features}
        
        else:
            return text
    
    async def _preprocess_image(self, image, config: ProcessingConfig) -> Any:
        """Pré-processa dados de imagem"""
        if config.operation == ProcessingOperation.TRANSFORMATION:
            if config.method == "resize":
                target_size = tuple(config.parameters.get('target_size', (224, 224)))
                return await self.image_preprocessor.resize_image(image, target_size)
        
        elif config.operation == ProcessingOperation.NORMALIZATION:
            method = config.parameters.get('method', 'min_max')
            return await self.image_preprocessor.normalize_image(image, method)
        
        elif config.operation == ProcessingOperation.CLEANING:
            if config.method == "denoise":
                return await self.image_preprocessor.denoise_image(image)
        
        elif config.operation == ProcessingOperation.FEATURE_ENGINEERING:
            features = await self.image_preprocessor.extract_features(image)
            return {'image': image, 'features': features}
        
        return image
    
    async def _preprocess_audio(self, audio_data, config: ProcessingConfig) -> Any:
        """Pré-processa dados de áudio"""
        if isinstance(audio_data, dict):
            audio_array = audio_data['audio']
            sample_rate = audio_data['sample_rate']
        else:
            audio_array = audio_data
            sample_rate = config.parameters.get('sample_rate', 44100)
        
        if config.operation == ProcessingOperation.NORMALIZATION:
            method = config.parameters.get('method', 'peak')
            normalized_audio = await self.audio_preprocessor.normalize_audio(audio_array, method)
            return {'audio': normalized_audio, 'sample_rate': sample_rate}
        
        elif config.operation == ProcessingOperation.CLEANING:
            if config.method == "remove_silence":
                trimmed_audio = await self.audio_preprocessor.remove_silence(audio_array, sample_rate)
                return {'audio': trimmed_audio, 'sample_rate': sample_rate}
        
        elif config.operation == ProcessingOperation.FEATURE_ENGINEERING:
            features = await self.audio_preprocessor.extract_features(audio_array, sample_rate)
            return {'audio': audio_data, 'features': features}
        
        return audio_data
    
    async def _preprocess_structured(self, data: pd.DataFrame, config: ProcessingConfig) -> pd.DataFrame:
        """Pré-processa dados estruturados"""
        if config.operation == ProcessingOperation.CLEANING:
            if config.method in ["remove", "fill_mean", "fill_median", "fill_mode", "fill_forward", "interpolate"]:
                return await self.structured_preprocessor.handle_missing_values(data, config)
            elif config.method in ["iqr", "z_score", "isolation_forest"]:
                return await self.structured_preprocessor.remove_outliers(data, config)
        
        elif config.operation == ProcessingOperation.NORMALIZATION:
            return await self.structured_preprocessor.normalize_data(data, config)
        
        elif config.operation == ProcessingOperation.TRANSFORMATION:
            if config.method == "encode_categorical":
                return await self.structured_preprocessor.encode_categorical(data, config)
        
        return data
    
    async def _extract_features(self, data_type: DataType, data: Any) -> Dict[str, Any]:
        """Extrai features baseado no tipo de dado"""
        if data_type == DataType.TEXT:
            return await self.text_preprocessor.extract_features(data)
        
        elif data_type == DataType.IMAGE:
            return await self.image_preprocessor.extract_features(data)
        
        elif data_type == DataType.AUDIO:
            if isinstance(data, dict):
                audio_array = data['audio']
                sample_rate = data['sample_rate']
            else:
                audio_array = data
                sample_rate = 44100
            return await self.audio_preprocessor.extract_features(audio_array, sample_rate)
        
        return {}
    
    def create_standard_pipeline(self, data_type: DataType) -> List[ProcessingConfig]:
        """Cria pipeline padrão para tipo de dado"""
        pipelines = {
            DataType.TEXT: [
                ProcessingConfig(
                    operation=ProcessingOperation.CLEANING,
                    method="text_cleaning",
                    parameters={
                        'remove_special_chars': True,
                        'lowercase': True,
                        'remove_extra_spaces': True,
                        'remove_stopwords': True
                    }
                ),
                ProcessingConfig(
                    operation=ProcessingOperation.FEATURE_ENGINEERING,
                    method="extract_features"
                )
            ],
            
            DataType.IMAGE: [
                ProcessingConfig(
                    operation=ProcessingOperation.TRANSFORMATION,
                    method="resize",
                    parameters={'target_size': (224, 224)}
                ),
                ProcessingConfig(
                    operation=ProcessingOperation.NORMALIZATION,
                    method="min_max"
                ),
                ProcessingConfig(
                    operation=ProcessingOperation.FEATURE_ENGINEERING,
                    method="extract_features"
                )
            ],
            
            DataType.AUDIO: [
                ProcessingConfig(
                    operation=ProcessingOperation.NORMALIZATION,
                    method="peak"
                ),
                ProcessingConfig(
                    operation=ProcessingOperation.CLEANING,
                    method="remove_silence"
                ),
                ProcessingConfig(
                    operation=ProcessingOperation.FEATURE_ENGINEERING,
                    method="extract_features"
                )
            ],
            
            DataType.STRUCTURED: [
                ProcessingConfig(
                    operation=ProcessingOperation.CLEANING,
                    method="fill_mean"
                ),
                ProcessingConfig(
                    operation=ProcessingOperation.NORMALIZATION,
                    method="standard_scaler"
                )
            ]
        }
        
        return pipelines.get(data_type, [])
    
    async def preprocess_batch(self, samples: List[DataSample], pipeline: List[ProcessingConfig]) -> List[ProcessingResult]:
        """Pré-processa dados em lote"""
        results = []
        
        for sample in samples:
            try:
                result = await self.preprocess_data(sample, pipeline)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Error preprocessing sample {sample.id}: {e}")
                continue
        
        return results
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de pré-processamento"""
        stats = {
            'total_processed': len(self.processing_history),
            'processing_pipelines': len(self.processing_pipelines),
            'available_operations': [op.value for op in ProcessingOperation],
            'supported_data_types': [dt.value for dt in DataType]
        }
        
        # Estatísticas por tipo
        type_stats = {}
        for result in self.processing_history:
            dt = result.original_sample.data_type.value
            type_stats[dt] = type_stats.get(dt, 0) + 1
        
        stats['processed_by_type'] = type_stats
        
        # Estatísticas por operação
        operation_stats = {}
        for result in self.processing_history:
            for operation in result.applied_operations:
                operation_stats[operation] = operation_stats.get(operation, 0) + 1
        
        stats['operations_used'] = operation_stats
        
        return stats


# Função de conveniência
_preprocessor_instance = None

def get_data_preprocessor() -> DataPreprocessor:
    """Obtém instância singleton do pré-processador"""
    global _preprocessor_instance
    if _preprocessor_instance is None:
        _preprocessor_instance = DataPreprocessor()
    return _preprocessor_instance

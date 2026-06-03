"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║              ARQUITETURA DE APRENDIZADO PROFUNDO TEMPORAL                       ║
║                 Componente 4: Deep Learning para Séries Temporais                ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import asyncio
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset, Dataset
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models, optimizers, losses, metrics
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
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
import os
from pathlib import Path

# Import dos módulos anteriores
from financial_feature_engineering import FeatureSet, FeatureType

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('TemporalDeepLearning')

class ModelType(Enum):
    """Tipos de modelos de deep learning temporal"""
    LSTM = "lstm"
    GRU = "gru"
    CNN_LSTM = "cnn_lstm"
    TRANSFORMER = "transformer"
    INFORMER = "informer"
    TIME2VEC = "time2vec"
    TCN = "tcn"
    BILSTM = "bilstm"
    ATTENTION_LSTM = "attention_lstm"
    HYBRID = "hybrid"

class Framework(Enum):
    """Frameworks de deep learning"""
    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"

class TaskType(Enum):
    """Tipos de tarefas"""
    PREDICTION = "prediction"
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    ANOMALY_DETECTION = "anomaly_detection"
    VOLATILITY_FORECASTING = "volatility_forecasting"
    TREND_PREDICTION = "trend_prediction"
    MULTI_STEP_FORECAST = "multi_step_forecast"

@dataclass
class ModelConfig:
    """Configuração do modelo"""
    model_type: ModelType
    framework: Framework
    task_type: TaskType
    input_shape: Tuple[int, int]  # (sequence_length, features)
    output_shape: Tuple[int, ...]  # (output_size,)
    hidden_units: List[int] = field(default_factory=lambda: [128, 64])
    dropout_rate: float = 0.2
    learning_rate: float = 0.001
    batch_size: int = 32
    epochs: int = 100
    sequence_length: int = 60
    prediction_horizon: int = 1
    optimizer: str = "adam"
    loss_function: str = "mse"
    metrics: List[str] = field(default_factory=lambda: ["mae", "mse"])
    early_stopping_patience: int = 10
    reduce_lr_patience: int = 5
    validation_split: float = 0.2
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'model_type': self.model_type.value,
            'framework': self.framework.value,
            'task_type': self.task_type.value,
            'input_shape': self.input_shape,
            'output_shape': self.output_shape,
            'hidden_units': self.hidden_units,
            'dropout_rate': self.dropout_rate,
            'learning_rate': self.learning_rate,
            'batch_size': self.batch_size,
            'epochs': self.epochs,
            'sequence_length': self.sequence_length,
            'prediction_horizon': self.prediction_horizon,
            'optimizer': self.optimizer,
            'loss_function': self.loss_function,
            'metrics': self.metrics,
            'early_stopping_patience': self.early_stopping_patience,
            'reduce_lr_patience': self.reduce_lr_patience,
            'validation_split': self.validation_split
        }

@dataclass
class TrainingMetrics:
    """Métricas de treinamento"""
    epoch: int
    train_loss: float
    val_loss: Optional[float] = None
    train_metrics: Dict[str, float] = field(default_factory=dict)
    val_metrics: Dict[str, float] = field(default_factory=dict)
    learning_rate: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'epoch': self.epoch,
            'train_loss': self.train_loss,
            'val_loss': self.val_loss,
            'train_metrics': self.train_metrics,
            'val_metrics': self.val_metrics,
            'learning_rate': self.learning_rate,
            'timestamp': self.timestamp.isoformat()
        }

@dataclass
class PredictionResult:
    """Resultado de predição"""
    symbol: str
    timestamp: datetime
    prediction: Union[float, np.ndarray]
    confidence: float
    prediction_horizon: int
    input_features: List[str]
    model_version: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'symbol': self.symbol,
            'timestamp': self.timestamp.isoformat(),
            'prediction': self.prediction.tolist() if isinstance(self.prediction, np.ndarray) else self.prediction,
            'confidence': self.confidence,
            'prediction_horizon': self.prediction_horizon,
            'input_features': self.input_features,
            'model_version': self.model_version,
            'metadata': self.metadata
        }

class TimeSeriesDataset(Dataset):
    """Dataset para séries temporais"""
    
    def __init__(self, data: np.ndarray, targets: np.ndarray, sequence_length: int):
        self.data = data
        self.targets = targets
        self.sequence_length = sequence_length
        
        # Validação de dimensões
        assert len(data) == len(targets), "Data e targets devem ter o mesmo comprimento"
        assert len(data) >= sequence_length, f"Data deve ter pelo menos {sequence_length} amostras"
    
    def __len__(self):
        return len(self.data) - self.sequence_length
    
    def __getitem__(self, idx):
        # Retorna sequência e target correspondente
        sequence = self.data[idx:idx + self.sequence_length]
        target = self.targets[idx + self.sequence_length - 1]
        
        return torch.FloatTensor(sequence), torch.FloatTensor(target)

class LSTMModel(nn.Module):
    """Modelo LSTM para séries temporais"""
    
    def __init__(self, config: ModelConfig):
        super(LSTMModel, self).__init__()
        self.config = config
        
        # Camada LSTM
        self.lstm = nn.LSTM(
            input_size=config.input_shape[1],
            hidden_size=config.hidden_units[0],
            num_layers=len(config.hidden_units),
            dropout=config.dropout_rate if len(config.hidden_units) > 1 else 0,
            batch_first=True,
            bidirectional=False
        )
        
        # Camadas fully connected
        layers = []
        for i in range(len(config.hidden_units) - 1):
            layers.extend([
                nn.Linear(config.hidden_units[i], config.hidden_units[i + 1]),
                nn.ReLU(),
                nn.Dropout(config.dropout_rate)
            ])
        
        # Camada de saída
        layers.append(nn.Linear(config.hidden_units[-1], config.output_shape[0]))
        
        self.fc = nn.Sequential(*layers)
        
    def forward(self, x):
        # x shape: (batch_size, sequence_length, features)
        
        # Passa pela LSTM
        lstm_out, (hidden, cell) = self.lstm(x)
        
        # Usa o último output da LSTM
        last_output = lstm_out[:, -1, :]
        
        # Passa pelas camadas fully connected
        output = self.fc(last_output)
        
        return output

class GRUModel(nn.Module):
    """Modelo GRU para séries temporais"""
    
    def __init__(self, config: ModelConfig):
        super(GRUModel, self).__init__()
        self.config = config
        
        # Camada GRU
        self.gru = nn.GRU(
            input_size=config.input_shape[1],
            hidden_size=config.hidden_units[0],
            num_layers=len(config.hidden_units),
            dropout=config.dropout_rate if len(config.hidden_units) > 1 else 0,
            batch_first=True,
            bidirectional=False
        )
        
        # Camadas fully connected
        layers = []
        for i in range(len(config.hidden_units) - 1):
            layers.extend([
                nn.Linear(config.hidden_units[i], config.hidden_units[i + 1]),
                nn.ReLU(),
                nn.Dropout(config.dropout_rate)
            ])
        
        # Camada de saída
        layers.append(nn.Linear(config.hidden_units[-1], config.output_shape[0]))
        
        self.fc = nn.Sequential(*layers)
        
    def forward(self, x):
        # x shape: (batch_size, sequence_length, features)
        
        # Passa pela GRU
        gru_out, hidden = self.gru(x)
        
        # Usa o último output da GRU
        last_output = gru_out[:, -1, :]
        
        # Passa pelas camadas fully connected
        output = self.fc(last_output)
        
        return output

class CNNLSTMModel(nn.Module):
    """Modelo CNN-LSTM híbrido"""
    
    def __init__(self, config: ModelConfig):
        super(CNNLSTMModel, self).__init__()
        self.config = config
        
        # Camadas CNN para extração de features
        self.conv1 = nn.Conv1d(config.input_shape[1], 64, kernel_size=3, padding=1)
        self.conv2 = nn.Conv1d(64, 128, kernel_size=3, padding=1)
        self.pool = nn.MaxPool1d(kernel_size=2)
        self.dropout = nn.Dropout(config.dropout_rate)
        
        # Calcula o tamanho da saída das CNNs
        conv_output_size = (config.sequence_length // 4) * 128
        
        # Camada LSTM
        self.lstm = nn.LSTM(
            input_size=conv_output_size,
            hidden_size=config.hidden_units[0],
            num_layers=len(config.hidden_units),
            dropout=config.dropout_rate if len(config.hidden_units) > 1 else 0,
            batch_first=True
        )
        
        # Camadas fully connected
        layers = []
        for i in range(len(config.hidden_units) - 1):
            layers.extend([
                nn.Linear(config.hidden_units[i], config.hidden_units[i + 1]),
                nn.ReLU(),
                nn.Dropout(config.dropout_rate)
            ])
        
        # Camada de saída
        layers.append(nn.Linear(config.hidden_units[-1], config.output_shape[0]))
        
        self.fc = nn.Sequential(*layers)
        
    def forward(self, x):
        # x shape: (batch_size, sequence_length, features)
        
        # Reorganiza para CNN: (batch_size, features, sequence_length)
        x = x.transpose(1, 2)
        
        # Passa pelas CNNs
        x = self.pool(torch.relu(self.conv1(x)))
        x = self.pool(torch.relu(self.conv2(x)))
        x = self.dropout(x)
        
        # Reorganiza para LSTM: (batch_size, sequence_length, features)
        x = x.transpose(1, 2)
        
        # Passa pela LSTM
        lstm_out, (hidden, cell) = self.lstm(x)
        
        # Usa o último output
        last_output = lstm_out[:, -1, :]
        
        # Passa pelas camadas fully connected
        output = self.fc(last_output)
        
        return output

class TransformerModel(nn.Module):
    """Modelo Transformer para séries temporais"""
    
    def __init__(self, config: ModelConfig):
        super(TransformerModel, self).__init__()
        self.config = config
        
        # Embedding de input
        self.input_projection = nn.Linear(config.input_shape[1], config.hidden_units[0])
        
        # Positional encoding
        self.positional_encoding = PositionalEncoding(config.hidden_units[0], config.sequence_length)
        
        # Encoder layers
        encoder_layers = []
        for _ in range(len(config.hidden_units)):
            encoder_layers.append(
                nn.TransformerEncoderLayer(
                    d_model=config.hidden_units[0],
                    nhead=8,
                    dim_feedforward=config.hidden_units[0] * 4,
                    dropout=config.dropout_rate,
                    batch_first=True
                )
            )
        
        self.transformer_encoder = nn.TransformerEncoder(
            nn.Sequential(*encoder_layers),
            num_layers=len(config.hidden_units)
        )
        
        # Camadas de saída
        layers = []
        for i in range(len(config.hidden_units) - 1):
            layers.extend([
                nn.Linear(config.hidden_units[0], config.hidden_units[i + 1]),
                nn.ReLU(),
                nn.Dropout(config.dropout_rate)
            ])
        
        # Camada de saída final
        layers.append(nn.Linear(config.hidden_units[-1], config.output_shape[0]))
        
        self.fc = nn.Sequential(*layers)
        
    def forward(self, x):
        # x shape: (batch_size, sequence_length, features)
        
        # Projeção do input
        x = self.input_projection(x)
        
        # Adiciona positional encoding
        x = self.positional_encoding(x)
        
        # Passa pelo transformer encoder
        x = self.transformer_encoder(x)
        
        # Usa o último token
        last_output = x[:, -1, :]
        
        # Passa pelas camadas de saída
        output = self.fc(last_output)
        
        return output

class PositionalEncoding(nn.Module):
    """Codificação posicional para Transformer"""
    
    def __init__(self, d_model: int, max_len: int = 5000):
        super(PositionalEncoding, self).__init__()
        
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-np.log(10000.0) / d_model))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        
        pe = pe.unsqueeze(0).transpose(0, 1)
        self.register_buffer('pe', pe)
    
    def forward(self, x):
        # x shape: (batch_size, sequence_length, d_model)
        seq_len = x.size(1)
        x = x + self.pe[:seq_len, :].transpose(0, 1)
        return x

class TensorFlowModels:
    """Modelos usando TensorFlow/Keras"""
    
    @staticmethod
    def create_lstm_model(config: ModelConfig) -> keras.Model:
        """Cria modelo LSTM usando TensorFlow"""
        model = keras.Sequential()
        
        # Primeira camada LSTM
        model.add(layers.LSTM(
            config.hidden_units[0],
            return_sequences=len(config.hidden_units) > 1,
            input_shape=config.input_shape,
            dropout=config.dropout_rate if len(config.hidden_units) > 1 else 0
        ))
        
        # Camadas LSTM adicionais
        for i, units in enumerate(config.hidden_units[1:], 1):
            return_sequences = i < len(config.hidden_units) - 1
            model.add(layers.LSTM(
                units,
                return_sequences=return_sequences,
                dropout=config.dropout_rate if return_sequences else 0
            ))
        
        # Camada de saída
        model.add(layers.Dense(config.output_shape[0]))
        
        return model
    
    @staticmethod
    def create_gru_model(config: ModelConfig) -> keras.Model:
        """Cria modelo GRU usando TensorFlow"""
        model = keras.Sequential()
        
        # Primeira camada GRU
        model.add(layers.GRU(
            config.hidden_units[0],
            return_sequences=len(config.hidden_units) > 1,
            input_shape=config.input_shape,
            dropout=config.dropout_rate if len(config.hidden_units) > 1 else 0
        ))
        
        # Camadas GRU adicionais
        for i, units in enumerate(config.hidden_units[1:], 1):
            return_sequences = i < len(config.hidden_units) - 1
            model.add(layers.GRU(
                units,
                return_sequences=return_sequences,
                dropout=config.dropout_rate if return_sequences else 0
            ))
        
        # Camada de saída
        model.add(layers.Dense(config.output_shape[0]))
        
        return model
    
    @staticmethod
    def create_transformer_model(config: ModelConfig) -> keras.Model:
        """Cria modelo Transformer usando TensorFlow"""
        # Input
        inputs = layers.Input(shape=config.input_shape)
        
        # Projeção do input
        x = layers.Dense(config.hidden_units[0])(inputs)
        
        # Positional encoding
        x = TransformerPositionalEncoding(config.sequence_length, config.hidden_units[0])(x)
        
        # Transformer encoder
        for _ in range(len(config.hidden_units)):
            x = TransformerEncoder(config.hidden_units[0], 8, config.dropout_rate)(x)
        
        # Pega o último token
        x = x[:, -1, :]
        
        # Camadas densas
        for i, units in enumerate(config.hidden_units[1:], 1):
            x = layers.Dense(units, activation='relu')(x)
            x = layers.Dropout(config.dropout_rate)(x)
        
        # Saída
        outputs = layers.Dense(config.output_shape[0])(x)
        
        return keras.Model(inputs=inputs, outputs=outputs)

class TransformerPositionalEncoding(layers.Layer):
    """Codificação posicional para TensorFlow"""
    
    def __init__(self, max_len: int, d_model: int, **kwargs):
        super(TransformerPositionalEncoding, self).__init__(**kwargs)
        self.max_len = max_len
        self.d_model = d_model
    
    def build(self, input_shape):
        # Cria a matriz de positional encoding
        position = tf.range(self.max_len, dtype=tf.float32)[:, tf.newaxis]
        div_term = tf.exp(tf.range(0, self.d_model, 2, dtype=tf.float32) * 
                         (-tf.math.log(10000.0) / self.d_model))
        
        pe = tf.zeros((self.max_len, self.d_model))
        pe = pe.numpy()
        pe[:, 0::2] = tf.sin(position * div_term).numpy()
        pe[:, 1::2] = tf.cos(position * div_term).numpy()
        
        self.pe = self.add_weight(
            name='positional_encoding',
            shape=(self.max_len, self.d_model),
            initializer=tf.keras.initializers.Constant(pe),
            trainable=False
        )
        super(TransformerPositionalEncoding, self).build(input_shape)
    
    def call(self, inputs):
        seq_len = tf.shape(inputs)[1]
        return inputs + self.pe[:seq_len, :]

class TransformerEncoder(layers.Layer):
    """Encoder Transformer para TensorFlow"""
    
    def __init__(self, d_model: int, num_heads: int, dropout_rate: float, **kwargs):
        super(TransformerEncoder, self).__init__(**kwargs)
        self.d_model = d_model
        self.num_heads = num_heads
        self.dropout_rate = dropout_rate
        
        self.attention = layers.MultiHeadAttention(num_heads=num_heads, key_dim=d_model)
        self.norm1 = layers.LayerNormalization(epsilon=1e-6)
        self.norm2 = layers.LayerNormalization(epsilon=1e-6)
        self.ffn = self._create_ffn()
        self.dropout1 = layers.Dropout(dropout_rate)
        self.dropout2 = layers.Dropout(dropout_rate)
    
    def _create_ffn(self):
        return keras.Sequential([
            layers.Dense(self.d_model * 4, activation='relu'),
            layers.Dense(self.d_model),
            layers.Dropout(self.dropout_rate)
        ])
    
    def call(self, inputs, training=None):
        # Self-attention
        attn_output = self.attention(inputs, inputs)
        attn_output = self.dropout1(attn_output, training=training)
        out1 = self.norm1(inputs + attn_output)
        
        # Feed-forward
        ffn_output = self.ffn(out1)
        ffn_output = self.dropout2(ffn_output, training=training)
        out2 = self.norm2(out1 + ffn_output)
        
        return out2

class TemporalDeepLearningPipeline:
    """Pipeline completo de deep learning temporal"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self.model = None
        self.framework = config.framework
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Histórico de treinamento
        self.training_history = []
        self.best_model_path = None
        self.current_epoch = 0
        
        # Métricas
        self.training_metrics = []
        self.validation_metrics = []
        
        # Normalização
        self.scaler = None
        
        logger.info(f"🧠 Pipeline de Deep Learning inicializado com {config.framework.value}")
    
    def create_model(self) -> Union[nn.Module, keras.Model]:
        """Cria o modelo baseado na configuração"""
        if self.framework == Framework.PYTORCH:
            return self._create_pytorch_model()
        elif self.framework == Framework.TENSORFLOW:
            return self._create_tensorflow_model()
        else:
            raise ValueError(f"Framework não suportado: {self.framework}")
    
    def _create_pytorch_model(self) -> nn.Module:
        """Cria modelo PyTorch"""
        if self.config.model_type == ModelType.LSTM:
            model = LSTMModel(self.config)
        elif self.config.model_type == ModelType.GRU:
            model = GRUModel(self.config)
        elif self.config.model_type == ModelType.CNN_LSTM:
            model = CNNLSTMModel(self.config)
        elif self.config.model_type == ModelType.TRANSFORMER:
            model = TransformerModel(self.config)
        else:
            raise ValueError(f"Model type não suportado: {self.config.model_type}")
        
        model.to(self.device)
        return model
    
    def _create_tensorflow_model(self) -> keras.Model:
        """Cria modelo TensorFlow"""
        if self.config.model_type == ModelType.LSTM:
            model = TensorFlowModels.create_lstm_model(self.config)
        elif self.config.model_type == ModelType.GRU:
            model = TensorFlowModels.create_gru_model(self.config)
        elif self.config.model_type == ModelType.TRANSFORMER:
            model = TensorFlowModels.create_transformer_model(self.config)
        else:
            raise ValueError(f"Model type não suportado: {self.config.model_type}")
        
        return model
    
    def prepare_data(self, data: pd.DataFrame, target_column: str, 
                    feature_columns: List[str] = None) -> Tuple[np.ndarray, np.ndarray]:
        """Prepara dados para treinamento"""
        if feature_columns is None:
            feature_columns = [col for col in data.columns if col != target_column]
        
        # Seleciona features e target
        features = data[feature_columns].values
        targets = data[target_column].values
        
        # Normalização
        if self.scaler is None:
            from sklearn.preprocessing import StandardScaler
            self.scaler = StandardScaler()
            features = self.scaler.fit_transform(features)
        else:
            features = self.scaler.transform(features)
        
        # Cria sequências
        X, y = self._create_sequences(features, targets)
        
        return X, y
    
    def _create_sequences(self, features: np.ndarray, targets: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Cria sequências para treinamento"""
        X, y = [], []
        
        for i in range(len(features) - self.config.sequence_length - self.config.prediction_horizon + 1):
            # Sequência de input
            seq = features[i:i + self.config.sequence_length]
            
            # Target (pode ser multi-step)
            if self.config.prediction_horizon == 1:
                target = targets[i + self.config.sequence_length - 1]
            else:
                target = targets[i + self.config.sequence_length - 1:i + self.config.sequence_length - 1 + self.config.prediction_horizon]
            
            X.append(seq)
            y.append(target)
        
        return np.array(X), np.array(y)
    
    def train_pytorch(self, X_train: np.ndarray, y_train: np.ndarray, 
                     X_val: np.ndarray = None, y_val: np.ndarray = None) -> List[TrainingMetrics]:
        """Treina modelo PyTorch"""
        # Cria datasets
        train_dataset = TimeSeriesDataset(X_train, y_train, self.config.sequence_length)
        train_loader = DataLoader(train_dataset, batch_size=self.config.batch_size, shuffle=True)
        
        val_loader = None
        if X_val is not None and y_val is not None:
            val_dataset = TimeSeriesDataset(X_val, y_val, self.config.sequence_length)
            val_loader = DataLoader(val_dataset, batch_size=self.config.batch_size, shuffle=False)
        
        # Configura otimizador e loss
        optimizer = self._get_pytorch_optimizer()
        criterion = self._get_pytorch_loss()
        
        # Loop de treinamento
        metrics_history = []
        best_val_loss = float('inf')
        patience_counter = 0
        
        for epoch in range(self.config.epochs):
            self.model.train()
            train_loss = 0.0
            train_metrics = defaultdict(float)
            
            # Treinamento
            for batch_idx, (data, target) in enumerate(train_loader):
                data, target = data.to(self.device), target.to(self.device)
                
                optimizer.zero_grad()
                output = self.model(data)
                loss = criterion(output, target)
                loss.backward()
                optimizer.step()
                
                train_loss += loss.item()
                
                # Calcula métricas adicionais
                with torch.no_grad():
                    if self.config.task_type == TaskType.REGRESSION:
                        mae = torch.mean(torch.abs(output - target)).item()
                        train_metrics['mae'] += mae
            
            # Validação
            val_loss = None
            val_metrics = {}
            if val_loader is not None:
                val_loss, val_metrics = self._validate_pytorch(val_loader, criterion)
            
            # Média das métricas
            train_loss /= len(train_loader)
            for key in train_metrics:
                train_metrics[key] /= len(train_loader)
            
            # Salva métricas
            epoch_metrics = TrainingMetrics(
                epoch=epoch + 1,
                train_loss=train_loss,
                val_loss=val_loss,
                train_metrics=dict(train_metrics),
                val_metrics=val_metrics,
                learning_rate=optimizer.param_groups[0]['lr']
            )
            metrics_history.append(epoch_metrics)
            
            # Early stopping
            if val_loss is not None:
                if val_loss < best_val_loss:
                    best_val_loss = val_loss
                    patience_counter = 0
                    self._save_best_model()
                else:
                    patience_counter += 1
                
                if patience_counter >= self.config.early_stopping_patience:
                    logger.info(f"Early stopping na época {epoch + 1}")
                    break
            
            # Log
            if epoch % 10 == 0:
                logger.info(f"Epoch {epoch + 1}/{self.config.epochs}, "
                          f"Train Loss: {train_loss:.6f}, "
                          f"Val Loss: {val_loss:.6f if val_loss else 'N/A'}")
        
        return metrics_history
    
    def train_tensorflow(self, X_train: np.ndarray, y_train: np.ndarray,
                       X_val: np.ndarray = None, y_val: np.ndarray = None) -> List[TrainingMetrics]:
        """Treina modelo TensorFlow"""
        # Compila modelo
        optimizer = self._get_tensorflow_optimizer()
        loss_fn = self._get_tensorflow_loss()
        metrics = self._get_tensorflow_metrics()
        
        self.model.compile(optimizer=optimizer, loss=loss_fn, metrics=metrics)
        
        # Callbacks
        callbacks = [
            EarlyStopping(
                monitor='val_loss' if X_val is not None else 'loss',
                patience=self.config.early_stopping_patience,
                restore_best_weights=True
            ),
            ReduceLROnPlateau(
                monitor='val_loss' if X_val is not None else 'loss',
                patience=self.config.reduce_lr_patience,
                factor=0.5
            )
        ]
        
        # Treinamento
        validation_data = (X_val, y_val) if X_val is not None else None
        
        history = self.model.fit(
            X_train, y_train,
            validation_data=validation_data,
            epochs=self.config.epochs,
            batch_size=self.config.batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
        # Converte histórico para TrainingMetrics
        metrics_history = []
        for epoch in range(len(history.history['loss'])):
            epoch_metrics = TrainingMetrics(
                epoch=epoch + 1,
                train_loss=history.history['loss'][epoch],
                val_loss=history.history['val_loss'][epoch] if 'val_loss' in history.history else None,
                train_metrics={key: history.history[key][epoch] 
                             for key in history.history if key.startswith('train_')},
                val_metrics={key: history.history[key][epoch] 
                           for key in history.history if key.startswith('val_')},
                learning_rate=history.history.get('lr', [self.config.learning_rate])[epoch]
            )
            metrics_history.append(epoch_metrics)
        
        return metrics_history
    
    def _validate_pytorch(self, val_loader: DataLoader, criterion) -> Tuple[float, Dict[str, float]]:
        """Validação PyTorch"""
        self.model.eval()
        val_loss = 0.0
        val_metrics = defaultdict(float)
        
        with torch.no_grad():
            for data, target in val_loader:
                data, target = data.to(self.device), target.to(self.device)
                output = self.model(data)
                loss = criterion(output, target)
                val_loss += loss.item()
                
                # Métricas adicionais
                if self.config.task_type == TaskType.REGRESSION:
                    mae = torch.mean(torch.abs(output - target)).item()
                    val_metrics['mae'] += mae
        
        val_loss /= len(val_loader)
        for key in val_metrics:
            val_metrics[key] /= len(val_loader)
        
        return val_loss, dict(val_metrics)
    
    def _get_pytorch_optimizer(self) -> optim.Optimizer:
        """Retorna otimizador PyTorch"""
        if self.config.optimizer.lower() == 'adam':
            return optim.Adam(self.model.parameters(), lr=self.config.learning_rate)
        elif self.config.optimizer.lower() == 'sgd':
            return optim.SGD(self.model.parameters(), lr=self.config.learning_rate)
        elif self.config.optimizer.lower() == 'rmsprop':
            return optim.RMSprop(self.model.parameters(), lr=self.config.learning_rate)
        else:
            return optim.Adam(self.model.parameters(), lr=self.config.learning_rate)
    
    def _get_pytorch_loss(self) -> nn.Module:
        """Retorna função de loss PyTorch"""
        if self.config.loss_function.lower() == 'mse':
            return nn.MSELoss()
        elif self.config.loss_function.lower() == 'mae':
            return nn.L1Loss()
        elif self.config.loss_function.lower() == 'huber':
            return nn.HuberLoss()
        else:
            return nn.MSELoss()
    
    def _get_tensorflow_optimizer(self) -> str:
        """Retorna otimizador TensorFlow"""
        return self.config.optimizer
    
    def _get_tensorflow_loss(self) -> str:
        """Retorna função de loss TensorFlow"""
        return self.config.loss_function
    
    def _get_tensorflow_metrics(self) -> List[str]:
        """Retorna métricas TensorFlow"""
        return self.config.metrics
    
    def _save_best_model(self):
        """Salva o melhor modelo"""
        if self.framework == Framework.PYTORCH:
            torch.save(self.model.state_dict(), 'best_model.pth')
        elif self.framework == Framework.TENSORFLOW:
            self.model.save('best_model.h5')
        
        self.best_model_path = 'best_model.pth' if self.framework == Framework.PYTORCH else 'best_model.h5'
    
    def predict(self, data: np.ndarray) -> PredictionResult:
        """Faz predição"""
        self.model.eval() if self.framework == Framework.PYTORCH else None
        
        with torch.no_grad() if self.framework == Framework.PYTORCH else nullcontext():
            if self.framework == Framework.PYTORCH:
                data_tensor = torch.FloatTensor(data).unsqueeze(0).to(self.device)
                prediction = self.model(data_tensor).cpu().numpy()
            else:
                prediction = self.model.predict(np.expand_dims(data, axis=0))
            
            # Calcula confiança (simplificado)
            confidence = self._calculate_confidence(data, prediction)
            
            return PredictionResult(
                symbol="UNKNOWN",
                timestamp=datetime.now(),
                prediction=prediction[0],
                confidence=confidence,
                prediction_horizon=self.config.prediction_horizon,
                input_features=[],  # Preencher com nomes das features
                model_version="1.0"
            )
    
    def _calculate_confidence(self, data: np.ndarray, prediction: np.ndarray) -> float:
        """Calcula confiança da predição (implementação simplificada)"""
        # Implementação básica - pode ser melhorada com métodos mais sofisticados
        return 0.8  # Placeholder
    
    def load_model(self, path: str):
        """Carrega modelo salvo"""
        if self.framework == Framework.PYTORCH:
            self.model.load_state_dict(torch.load(path, map_location=self.device))
        elif self.framework == Framework.TENSORFLOW:
            self.model = keras.models.load_model(path)
        
        logger.info(f"Modelo carregado de {path}")
    
    def save_model(self, path: str):
        """Salva modelo"""
        if self.framework == Framework.PYTORCH:
            torch.save(self.model.state_dict(), path)
        elif self.framework == Framework.TENSORFLOW:
            self.model.save(path)
        
        logger.info(f"Modelo salvo em {path}")
    
    def get_model_summary(self) -> str:
        """Retorna resumo do modelo"""
        if self.framework == Framework.PYTORCH:
            return str(self.model)
        elif self.framework == Framework.TENSORFLOW:
            return self.model.summary()
    
    def get_training_history(self) -> List[TrainingMetrics]:
        """Retorna histórico de treinamento"""
        return self.training_history.copy()

# Context manager para TensorFlow
class nullcontext:
    def __enter__(self):
        return None
    def __exit__(self, *args):
        pass

# Configuração padrão
DEFAULT_MODEL_CONFIG = ModelConfig(
    model_type=ModelType.LSTM,
    framework=Framework.PYTORCH,
    task_type=TaskType.REGRESSION,
    input_shape=(60, 50),  # 60 timesteps, 50 features
    output_shape=(1,),      # 1 output
    hidden_units=[128, 64],
    dropout_rate=0.2,
    learning_rate=0.001,
    batch_size=32,
    epochs=100,
    sequence_length=60,
    prediction_horizon=1,
    optimizer="adam",
    loss_function="mse",
    metrics=["mae", "mse"],
    early_stopping_patience=10,
    reduce_lr_patience=5,
    validation_split=0.2
)

if __name__ == "__main__":
    # Exemplo de uso
    async def main():
        # Cria dados de exemplo
        np.random.seed(42)
        dates = pd.date_range(start='2020-01-01', end='2023-12-31', freq='D')
        
        # Gera features sintéticas
        n_features = 50
        n_samples = len(dates)
        
        data = np.random.randn(n_samples, n_features)
        target = np.cumsum(np.random.randn(n_samples) * 0.01) + 100
        
        # Cria DataFrame
        feature_names = [f'feature_{i}' for i in range(n_features)]
        df = pd.DataFrame(data, columns=feature_names, index=dates)
        df['target'] = target
        
        # Divide em treino/validação
        train_size = int(len(df) * 0.8)
        train_df = df.iloc[:train_size]
        val_df = df.iloc[train_size:]
        
        # Cria pipeline
        config = DEFAULT_MODEL_CONFIG
        pipeline = TemporalDeepLearningPipeline(config)
        
        # Cria modelo
        pipeline.model = pipeline.create_model()
        
        # Prepara dados
        feature_columns = feature_names
        X_train, y_train = pipeline.prepare_data(train_df, 'target', feature_columns)
        X_val, y_val = pipeline.prepare_data(val_df, 'target', feature_columns)
        
        print(f"📊 Shape dos dados:")
        print(f"X_train: {X_train.shape}")
        print(f"y_train: {y_train.shape}")
        print(f"X_val: {X_val.shape}")
        print(f"y_val: {y_val.shape}")
        
        # Treina modelo
        print(f"\n🚀 Iniciando treinamento...")
        if config.framework == Framework.PYTORCH:
            metrics = pipeline.train_pytorch(X_train, y_train, X_val, y_val)
        else:
            metrics = pipeline.train_tensorflow(X_train, y_train, X_val, y_val)
        
        print(f"✅ Treinamento concluído!")
        print(f"Melhor loss de validação: {min([m.val_loss for m in metrics if m.val_loss is not None]):.6f}")
        
        # Faz predição
        sample_data = X_val[-1]  # Última amostra de validação
        prediction = pipeline.predict(sample_data)
        
        print(f"\n🎯 Predição:")
        print(f"Valor predito: {prediction.prediction}")
        print(f"Confiança: {prediction.confidence:.2f}")
        print(f"Horizonte: {prediction.prediction_horizon}")
    
    asyncio.run(main())

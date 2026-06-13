# 05_neural_network.py
"""
Sistema VhalinorTrade - Rede Neural Completa
Deep Learning para predição de preços com aprendizado contínuo
"""

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, Model
from typing import Tuple, List, Dict, Optional
import pickle
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class AttentionLayer(layers.Layer):
    """Camada de atenção personalizada"""
    def __init__(self, units: int):
        super().__init__()
        self.W = layers.Dense(units)
        self.V = layers.Dense(1)
        
    def call(self, query, values):
        score = self.V(tf.nn.tanh(self.W(query) + self.W(values)))
        attention_weights = tf.nn.softmax(score, axis=1)
        context_vector = attention_weights * values
        context_vector = tf.reduce_sum(context_vector, axis=1)
        return context_vector, attention_weights

class VhalinorNeuralNetwork:
    def __init__(self, config):
        self.config = config
        self.models = {}
        self.model_versions = {}
        self.training_history = {}
        self.last_training = {}
        
    def build_lstm_attention_model(self, input_shape: Tuple[int, int],
                                  output_size: int = 1) -> Model:
        """Constrói modelo LSTM com atenção para predição de preços"""
        inputs = layers.Input(shape=input_shape)
        
        # Múltiplas camadas LSTM com dropout
        lstm1 = layers.LSTM(
            self.config.neural.lstm_units,
            return_sequences=True,
            dropout=self.config.neural.dropout_rate
        )(inputs)
        
        lstm2 = layers.LSTM(
            self.config.neural.lstm_units // 2,
            return_sequences=True,
            dropout=self.config.neural.dropout_rate
        )(lstm1)
        
        lstm3 = layers.LSTM(
            self.config.neural.lstm_units // 4,
            return_sequences=True,
            dropout=self.config.neural.dropout_rate
        )(lstm2)
        
        # Camada de atenção
        attention, attention_weights = AttentionLayer(
            self.config.neural.lstm_units // 4
        )(lstm3, lstm3)
        
        # Camadas densas
        dense1 = layers.Dense(128, activation='relu')(attention)
        dropout1 = layers.Dropout(self.config.neural.dropout_rate)(dense1)
        
        dense2 = layers.Dense(64, activation='relu')(dropout1)
        dropout2 = layers.Dropout(self.config.neural.dropout_rate)(dense2)
        
        dense3 = layers.Dense(32, activation='relu')(dropout2)
        
        # Múltiplas saídas
        price_output = layers.Dense(1, name='price_prediction')(dense3)
        direction_output = layers.Dense(1, activation='sigmoid', 
                                       name='direction_prediction')(dense3)
        volatility_output = layers.Dense(1, activation='relu',
                                        name='volatility_prediction')(dense3)
        
        model = Model(
            inputs=inputs,
            outputs=[price_output, direction_output, volatility_output]
        )
        
        model.compile(
            optimizer=keras.optimizers.Adam(
                learning_rate=self.config.neural.learning_rate
            ),
            loss={
                'price_prediction': 'mse',
                'direction_prediction': 'binary_crossentropy',
                'volatility_prediction': 'mse'
            },
            loss_weights={
                'price_prediction': 1.0,
                'direction_prediction': 0.5,
                'volatility_prediction': 0.3
            },
            metrics={
                'price_prediction': ['mae'],
                'direction_prediction': ['accuracy'],
                'volatility_prediction': ['mae']
            }
        )
        
        return model
    
    def build_transformer_model(self, input_shape: Tuple[int, int],
                               output_size: int = 1) -> Model:
        """Constrói modelo Transformer para predição"""
        inputs = layers.Input(shape=input_shape)
        
        # Embedding temporal
        x = layers.Dense(128, activation='relu')(inputs)
        
        # Múltiplos blocos Transformer
        for _ in range(4):
            # Multi-head attention
            attention_output = layers.MultiHeadAttention(
                num_heads=self.config.neural.attention_heads,
                key_dim=32
            )(x, x)
            
            # Residual connection
            x = layers.Add()([x, attention_output])
            x = layers.LayerNormalization()(x)
            
            # Feed-forward
            ff = layers.Dense(256, activation='relu')(x)
            ff = layers.Dense(128)(ff)
            
            # Residual connection
            x = layers.Add()([x, ff])
            x = layers.LayerNormalization()(x)
            
        # Global pooling
        x = layers.GlobalAveragePooling1D()(x)
        
        # Dense layers
        x = layers.Dense(64, activation='relu')(x)
        x = layers.Dropout(0.3)(x)
        x = layers.Dense(32, activation='relu')(x)
        
        # Outputs
        price_output = layers.Dense(1, name='price')(x)
        direction_output = layers.Dense(1, activation='sigmoid', name='direction')(x)
        
        model = Model(inputs=inputs, outputs=[price_output, direction_output])
        
        model.compile(
            optimizer=keras.optimizers.Adam(
                learning_rate=self.config.neural.learning_rate
            ),
            loss={
                'price': 'mse',
                'direction': 'binary_crossentropy'
            },
            metrics={
                'price': 'mae',
                'direction': 'accuracy'
            }
        )
        
        return model
    
    def prepare_training_data(self, df: pd.DataFrame,
                            sequence_length: int = 100,
                            prediction_horizon: int = 1) -> Tuple[np.ndarray, Dict]:
        """Prepara dados para treinamento da rede neural"""
        # Features técnicas
        df = self._add_technical_features(df)
        
        # Normalização
        feature_columns = ['close', 'volume', 'rsi', 'macd', 'macd_signal',
                          'bb_upper', 'bb_lower', 'atr', 'volume_ratio',
                          'price_change', 'high_low_ratio']
        
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(df[feature_columns])
        
        X, y_price, y_direction, y_volatility = [], [], [], []
        
        for i in range(sequence_length, len(scaled_data) - prediction_horizon):
            X.append(scaled_data[i-sequence_length:i])
            future_price = df['close'].iloc[i + prediction_horizon]
            current_price = df['close'].iloc[i]
            
            y_price.append((future_price - current_price) / current_price)
            y_direction.append(1 if future_price > current_price else 0)
            y_volatility.append(
                df['close'].iloc[i:i+prediction_horizon].std() / current_price
            )
            
        return (
            np.array(X),
            {
                'price_prediction': np.array(y_price).reshape(-1, 1),
                'direction_prediction': np.array(y_direction).reshape(-1, 1),
                'volatility_prediction': np.array(y_volatility).reshape(-1, 1)
            }
        ), scaler
    
    def _add_technical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Adiciona features técnicas ao DataFrame"""
        df = df.copy()
        
        # RSI
        df['rsi'] = talib.RSI(df['close'].values, timeperiod=14)
        
        # MACD
        df['macd'], df['macd_signal'], _ = talib.MACD(df['close'].values)
        
        # Bollinger Bands
        df['bb_upper'], df['bb_middle'], df['bb_lower'] = talib.BBANDS(
            df['close'].values
        )
        
        # ATR
        df['atr'] = talib.ATR(
            df['high'].values,
            df['low'].values,
            df['close'].values,
            timeperiod=14
        )
        
        # Volume relativo
        df['volume_ratio'] = df['volume'] / df['volume'].rolling(20).mean()
        
        # Price change
        df['price_change'] = df['close'].pct_change()
        
        # High-Low ratio
        df['high_low_ratio'] = (df['high'] - df['low']) / df['close']
        
        return df.dropna()
    
    async def train_model(self, symbol: str, df: pd.DataFrame,
                         model_type: str = 'lstm_attention'):
        """Treina o modelo neural"""
        X, y, scaler = self.prepare_training_data(
            df,
            sequence_length=self.config.neural.input_sequence_length
        )
        
        # Split treino/validação
        split_idx = int(len(X) * 0.8)
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train = {k: v[:split_idx] for k, v in y.items()}
        y_val = {k: v[split_idx:] for k, v in y.items()}
        
        # Build model
        if model_type == 'lstm_attention':
            model = self.build_lstm_attention_model(
                input_shape=(X_train.shape[1], X_train.shape[2])
            )
        else:
            model = self.build_transformer_model(
                input_shape=(X_train.shape[1], X_train.shape[2])
            )
        
        # Callbacks
        callbacks = [
            keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=15,
                restore_best_weights=True
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-6
            ),
            keras.callbacks.ModelCheckpoint(
                f"{self.config.models_path}/{symbol}_{model_type}_best.h5",
                monitor='val_loss',
                save_best_only=True
            )
        ]
        
        # Treinamento
        history = model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=self.config.neural.epochs,
            batch_size=self.config.neural.batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
        # Salva modelo e scaler
        model_key = f"{symbol}_{model_type}"
        self.models[model_key] = model
        self.training_history[model_key] = history.history
        self.last_training[model_key] = datetime.now()
        
        # Salva scaler
        with open(f"{self.config.models_path}/{model_key}_scaler.pkl", 'wb') as f:
            pickle.dump(scaler, f)
            
        return model, history
    
    async def predict(self, symbol: str, df: pd.DataFrame,
                     model_type: str = 'lstm_attention') -> Dict[str, any]:
        """Realiza predições com o modelo treinado"""
        model_key = f"{symbol}_{model_type}"
        
        if model_key not in self.models:
            return None
            
        model = self.models[model_key]
        
        # Prepara dados
        X, _, scaler = self.prepare_training_data(
            df,
            sequence_length=self.config.neural.input_sequence_length
        )
        
        if len(X) == 0:
            return None
            
        # Predição
        predictions = model.predict(X[-1:], verbose=0)
        
        return {
            'price_prediction': predictions[0][0][0],
            'direction_prediction': predictions[1][0][0],
            'direction_confidence': abs(predictions[1][0][0] - 0.5) * 2,
            'volatility_prediction': predictions[2][0][0] if len(predictions) > 2 else None,
            'timestamp': datetime.now()
        }
    
    async def continuous_learning(self, symbol: str, new_data: pd.DataFrame):
        """Aprendizado contínuo com novos dados"""
        model_key = f"{symbol}_lstm_attention"
        
        if model_key not in self.models:
            return
            
        model = self.models[model_key]
        last_train = self.last_training.get(model_key)
        
        # Treina novamente se passou mais de 24 horas
        if last_train and (datetime.now() - last_train) > timedelta(hours=24):
            # Fine-tuning com novos dados
            X, y, _ = self.prepare_training_data(
                new_data,
                sequence_length=self.config.neural.input_sequence_length
            )
            
            if len(X) > 0:
                model.fit(
                    X, y,
                    epochs=10,
                    batch_size=self.config.neural.batch_size,
                    verbose=0
                )
                
                self.last_training[model_key] = datetime.now()
                
                # Salva modelo atualizado
                model.save(
                    f"{self.config.models_path}/{model_key}_latest.h5"
                )
    
    def evaluate_model_performance(self, symbol: str,
                                  test_df: pd.DataFrame) -> Dict[str, float]:
        """Avalia performance do modelo"""
        model_key = f"{symbol}_lstm_attention"
        
        if model_key not in self.models:
            return {}
            
        model = self.models[model_key]
        
        X_test, y_test, _ = self.prepare_training_data(
            test_df,
            sequence_length=self.config.neural.input_sequence_length
        )
        
        if len(X_test) == 0:
            return {}
            
        # Avaliação
        evaluation = model.evaluate(X_test, y_test, verbose=0)
        
        metrics = {}
        for name, value in zip(model.metrics_names, evaluation):
            metrics[name] = value
            
        return metrics
    
    def get_model_confidence(self, symbol: str) -> float:
        """Retorna confiança do modelo baseado no histórico recente"""
        model_key = f"{symbol}_lstm_attention"
        
        if model_key not in self.training_history:
            return 0.0
            
        history = self.training_history[model_key]
        
        if 'val_loss' not in history:
            return 0.0
            
        # Últimas 10 épocas de validação
        recent_val_losses = history['val_loss'][-10:]
        
        if len(recent_val_losses) < 2:
            return 0.5
            
        # Melhorando = maior confiança
        loss_trend = recent_val_losses[-1] - recent_val_losses[0]
        avg_loss = np.mean(recent_val_losses)
        
        confidence = 1.0 / (1.0 + np.exp(loss_trend / avg_loss))
        
        return float(confidence)
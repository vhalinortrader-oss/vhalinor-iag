# 05_neural_network.py
"""
Sistema VhalinorTrade - Rede Neural Completa
Deep Learning para predição de preços com aprendizado contínuo
"""

import logging
import pickle
import warnings
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple

import numpy as np
import pandas as pd
import talib
import tensorflow as tf
from sklearn.preprocessing import StandardScaler
from tensorflow import keras
from tensorflow.keras import Model, layers

warnings.filterwarnings("ignore")
logger = logging.getLogger("VhalinorNeuralNetwork")

ModelType = Literal["lstm_attention", "transformer"]

# ---------------------------------------------------------------------------
# Tipos auxiliares
# ---------------------------------------------------------------------------

@dataclass
class PredictionResult:
    price_change: float          # retorno previsto (%, normalizado)
    direction: float             # probabilidade de alta [0, 1]
    direction_confidence: float  # |direction - 0.5| * 2  →  [0, 1]
    volatility: Optional[float]  # volatilidade prevista (pode ser None)
    model_type: str
    symbol: str
    timestamp: datetime = field(default_factory=datetime.utcnow)

    @property
    def is_bullish(self) -> bool:
        return self.direction >= 0.5

    @property
    def signal_strength(self) -> float:
        """Combina confiança direcional e magnitude prevista."""
        return self.direction_confidence * min(1.0, abs(self.price_change) * 100)


@dataclass
class TrainingResult:
    symbol: str
    model_type: str
    best_val_loss: float
    epochs_run: int
    direction_accuracy: float    # acurácia de direção no conjunto de validação
    history: Dict[str, List[float]] = field(default_factory=dict)
    trained_at: datetime = field(default_factory=datetime.utcnow)


# ---------------------------------------------------------------------------
# Camada de atenção
# ---------------------------------------------------------------------------

class BahdanauAttention(layers.Layer):
    """
    Atenção de Bahdanau (additive attention) corrigida.

    O modelo original compartilhava `self.W` entre query e values, o que
    é matematicamente incorreto — query e values têm semânticas diferentes
    e precisam de projeções independentes.
    """

    def __init__(self, units: int, **kwargs) -> None:
        super().__init__(**kwargs)
        self.W_query  = layers.Dense(units, use_bias=False)
        self.W_values = layers.Dense(units, use_bias=False)
        self.V        = layers.Dense(1,     use_bias=False)

    def call(
        self,
        query: tf.Tensor,
        values: tf.Tensor,
    ) -> Tuple[tf.Tensor, tf.Tensor]:
        # score shape: (batch, seq_len, 1)
        score = self.V(tf.nn.tanh(self.W_query(query) + self.W_values(values)))
        weights = tf.nn.softmax(score, axis=1)           # (batch, seq_len, 1)
        context = tf.reduce_sum(weights * values, axis=1) # (batch, units)
        return context, weights

    def get_config(self) -> Dict[str, Any]:
        cfg = super().get_config()
        cfg["units"] = self.W_query.units
        return cfg


# ---------------------------------------------------------------------------
# Rede neural principal
# ---------------------------------------------------------------------------

class VhalinorNeuralNetwork:
    """
    Gerenciador de modelos de Deep Learning para predição de preços.

    Suporta dois arquiteturas:
      - ``lstm_attention``: LSTM pyramidal + Atenção de Bahdanau
      - ``transformer``:    Blocos Transformer com positional encoding
    """

    # Features calculadas por _add_technical_features
    FEATURE_COLUMNS: List[str] = [
        "close", "volume", "rsi", "macd", "macd_signal",
        "bb_upper", "bb_lower", "atr", "volume_ratio",
        "price_change", "high_low_ratio", "obv_norm",
    ]

    def __init__(self, config) -> None:
        self.config = config
        self.models:           Dict[str, Model]           = {}
        self.scalers:          Dict[str, StandardScaler]  = {}
        self.training_history: Dict[str, TrainingResult]  = {}
        self.last_training:    Dict[str, datetime]        = {}
        self._models_path = Path(config.models_path)
        self._models_path.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Construção de modelos
    # ------------------------------------------------------------------

    def build_lstm_attention_model(
        self, input_shape: Tuple[int, int]
    ) -> Model:
        """LSTM pyramidal (128 → 64 → 32) + Atenção de Bahdanau + 3 saídas."""
        units = self.config.neural.lstm_units
        drop  = self.config.neural.dropout_rate
        inputs = layers.Input(shape=input_shape, name="sequence_input")

        x = layers.LSTM(units,      return_sequences=True, dropout=drop, name="lstm_1")(inputs)
        x = layers.LSTM(units // 2, return_sequences=True, dropout=drop, name="lstm_2")(x)
        x = layers.LSTM(units // 4, return_sequences=True, dropout=drop, name="lstm_3")(x)

        context, _ = BahdanauAttention(units // 4, name="attention")(x, x)

        x = layers.Dense(128, activation="relu")(context)
        x = layers.Dropout(drop)(x)
        x = layers.Dense(64, activation="relu")(x)
        x = layers.Dropout(drop)(x)
        x = layers.Dense(32, activation="relu")(x)

        price_out      = layers.Dense(1,                    name="price_prediction")(x)
        direction_out  = layers.Dense(1, activation="sigmoid", name="direction_prediction")(x)
        volatility_out = layers.Dense(1, activation="relu",    name="volatility_prediction")(x)

        model = Model(inputs=inputs, outputs=[price_out, direction_out, volatility_out])
        model.compile(
            optimizer=keras.optimizers.Adam(self.config.neural.learning_rate),
            loss={
                "price_prediction":     "mse",
                "direction_prediction": "binary_crossentropy",
                "volatility_prediction":"mse",
            },
            loss_weights={
                "price_prediction":      1.0,
                "direction_prediction":  0.5,
                "volatility_prediction": 0.3,
            },
            metrics={
                "price_prediction":      ["mae"],
                "direction_prediction":  ["accuracy"],
                "volatility_prediction": ["mae"],
            },
        )
        return model

    def build_transformer_model(
        self, input_shape: Tuple[int, int], num_blocks: int = 4
    ) -> Model:
        """
        Transformer com positional encoding aprendível + 3 saídas.

        Corrige o bug original onde o feed-forward não tinha a mesma dimensão
        que a entrada do bloco, tornando a conexão residual inválida.
        """
        d_model = 128
        inputs = layers.Input(shape=input_shape, name="sequence_input")

        # Projeção para d_model
        x = layers.Dense(d_model, activation="relu", name="input_projection")(inputs)

        # Positional encoding aprendível
        seq_len = input_shape[0]
        positions = tf.range(start=0, limit=seq_len, delta=1)
        pos_embed = layers.Embedding(seq_len, d_model, name="pos_encoding")(positions)
        x = x + pos_embed  # broadcast sobre batch

        for i in range(num_blocks):
            # Multi-head self-attention
            attn = layers.MultiHeadAttention(
                num_heads=self.config.neural.attention_heads,
                key_dim=d_model // self.config.neural.attention_heads,
                name=f"mha_{i}",
            )(x, x)
            x = layers.LayerNormalization(name=f"ln1_{i}")(layers.Add()([x, attn]))

            # Feed-forward (entrada e saída em d_model para residual válido)
            ff = layers.Dense(d_model * 4, activation="gelu", name=f"ff1_{i}")(x)
            ff = layers.Dropout(0.1)(ff)
            ff = layers.Dense(d_model, name=f"ff2_{i}")(ff)
            x = layers.LayerNormalization(name=f"ln2_{i}")(layers.Add()([x, ff]))

        x = layers.GlobalAveragePooling1D(name="gap")(x)
        x = layers.Dense(64, activation="relu")(x)
        x = layers.Dropout(0.2)(x)
        x = layers.Dense(32, activation="relu")(x)

        price_out      = layers.Dense(1,                    name="price_prediction")(x)
        direction_out  = layers.Dense(1, activation="sigmoid", name="direction_prediction")(x)
        volatility_out = layers.Dense(1, activation="relu",    name="volatility_prediction")(x)

        model = Model(inputs=inputs, outputs=[price_out, direction_out, volatility_out])
        model.compile(
            optimizer=keras.optimizers.Adam(self.config.neural.learning_rate),
            loss={
                "price_prediction":      "mse",
                "direction_prediction":  "binary_crossentropy",
                "volatility_prediction": "mse",
            },
            loss_weights={
                "price_prediction":      1.0,
                "direction_prediction":  0.5,
                "volatility_prediction": 0.3,
            },
            metrics={
                "price_prediction":      ["mae"],
                "direction_prediction":  ["accuracy"],
                "volatility_prediction": ["mae"],
            },
        )
        return model

    # ------------------------------------------------------------------
    # Features técnicas
    # ------------------------------------------------------------------

    def _add_technical_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula e anexa features técnicas ao DataFrame.

        Requer colunas: open, high, low, close, volume.
        Retorna cópia sem NaN.
        """
        required = ("open", "high", "low", "close", "volume")
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise ValueError(f"Colunas ausentes para features: {missing}")

        df = df.copy()
        c = df["close"].to_numpy(dtype=float)
        h = df["high"].to_numpy(dtype=float)
        l = df["low"].to_numpy(dtype=float)
        v = df["volume"].to_numpy(dtype=float)

        df["rsi"]         = talib.RSI(c, timeperiod=14)
        df["macd"], df["macd_signal"], _ = talib.MACD(c, 12, 26, 9)
        df["bb_upper"], _, df["bb_lower"] = talib.BBANDS(c, timeperiod=20)
        df["atr"]         = talib.ATR(h, l, c, timeperiod=14)
        df["volume_ratio"]= df["volume"] / df["volume"].rolling(20).mean()
        df["price_change"]= df["close"].pct_change()
        df["high_low_ratio"] = (df["high"] - df["low"]) / df["close"].replace(0, np.nan)

        # On-Balance Volume normalizado (evita valores absolutos gigantes)
        obv = talib.OBV(c, v)
        obv_std = obv.std()
        df["obv_norm"] = (obv - obv.mean()) / (obv_std if obv_std > 0 else 1.0)

        return df.dropna()

    # ------------------------------------------------------------------
    # Preparação de dados
    # ------------------------------------------------------------------

    def prepare_training_data(
        self,
        df: pd.DataFrame,
        sequence_length: int = 100,
        prediction_horizon: int = 1,
    ) -> Tuple[np.ndarray, Dict[str, np.ndarray], StandardScaler]:
        """
        Prepara sequências para treino/inferência.

        Returns:
            (X, y_dict, scaler)
            - X shape: (n_samples, sequence_length, n_features)
            - y_dict: {"price_prediction", "direction_prediction", "volatility_prediction"}
            - scaler: StandardScaler ajustado (necessário para inverter normalização)
        """
        df = self._add_technical_features(df)

        missing_feats = [c for c in self.FEATURE_COLUMNS if c not in df.columns]
        if missing_feats:
            raise ValueError(f"Features ausentes após engenharia: {missing_feats}")

        scaler = StandardScaler()
        scaled = scaler.fit_transform(df[self.FEATURE_COLUMNS].to_numpy(dtype=float))

        close_raw = df["close"].to_numpy(dtype=float)
        n = len(scaled)

        X, y_price, y_direction, y_volatility = [], [], [], []

        for i in range(sequence_length, n - prediction_horizon):
            X.append(scaled[i - sequence_length : i])

            current_price = close_raw[i]
            future_price  = close_raw[i + prediction_horizon]

            if current_price == 0:
                continue

            ret = (future_price - current_price) / current_price
            y_price.append(ret)
            y_direction.append(1 if ret > 0 else 0)
            y_volatility.append(
                float(np.std(close_raw[i : i + prediction_horizon]) / current_price)
            )

        X_arr = np.array(X, dtype=np.float32)
        y_dict = {
            "price_prediction":      np.array(y_price,     dtype=np.float32).reshape(-1, 1),
            "direction_prediction":  np.array(y_direction,  dtype=np.float32).reshape(-1, 1),
            "volatility_prediction": np.array(y_volatility, dtype=np.float32).reshape(-1, 1),
        }
        return X_arr, y_dict, scaler

    # ------------------------------------------------------------------
    # Treinamento
    # ------------------------------------------------------------------

    async def train_model(
        self,
        symbol: str,
        df: pd.DataFrame,
        model_type: ModelType = "lstm_attention",
        val_split: float = 0.2,
    ) -> TrainingResult:
        """
        Treina (ou re-treina) um modelo para o símbolo.

        Salva pesos (.keras), scaler (.pkl) e metadados de treino.
        """
        seq_len = self.config.neural.input_sequence_length
        X, y, scaler = self.prepare_training_data(df, sequence_length=seq_len)

        if len(X) == 0:
            raise ValueError(f"Dados insuficientes para treinar '{symbol}'.")

        split = int(len(X) * (1 - val_split))
        X_train, X_val = X[:split], X[split:]
        y_train = {k: v[:split] for k, v in y.items()}
        y_val   = {k: v[split:] for k, v in y.items()}

        model_key = f"{symbol}_{model_type}"
        if model_type == "lstm_attention":
            model = self.build_lstm_attention_model(
                input_shape=(X_train.shape[1], X_train.shape[2])
            )
        elif model_type == "transformer":
            model = self.build_transformer_model(
                input_shape=(X_train.shape[1], X_train.shape[2])
            )
        else:
            raise ValueError(f"model_type inválido: '{model_type}'")

        ckpt_path = self._models_path / f"{model_key}_best.keras"
        callbacks = [
            keras.callbacks.EarlyStopping(
                monitor="val_loss", patience=15, restore_best_weights=True
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor="val_loss", factor=0.5, patience=5, min_lr=1e-6
            ),
            keras.callbacks.ModelCheckpoint(
                str(ckpt_path), monitor="val_loss", save_best_only=True
            ),
        ]

        logger.info("Treinando '%s' com %d amostras…", model_key, len(X_train))
        history = model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=self.config.neural.epochs,
            batch_size=self.config.neural.batch_size,
            callbacks=callbacks,
            verbose=1,
        )

        # Persiste scaler
        scaler_path = self._models_path / f"{model_key}_scaler.pkl"
        with scaler_path.open("wb") as f:
            pickle.dump(scaler, f)

        # Registra modelo e metadados
        self.models[model_key]  = model
        self.scalers[model_key] = scaler
        self.last_training[model_key] = datetime.utcnow()

        # Extrai acurácia de direção da validação
        hist = history.history
        dir_acc_key = next(
            (k for k in hist if "direction" in k and "accuracy" in k and "val" in k), None
        )
        dir_acc = float(hist[dir_acc_key][-1]) if dir_acc_key else 0.0

        result = TrainingResult(
            symbol=symbol,
            model_type=model_type,
            best_val_loss=float(min(hist.get("val_loss", [float("inf")]))),
            epochs_run=len(hist.get("val_loss", [])),
            direction_accuracy=dir_acc,
            history=hist,
        )
        self.training_history[model_key] = result

        logger.info(
            "Treino concluído — %s | val_loss=%.6f | dir_acc=%.2f%%",
            model_key, result.best_val_loss, dir_acc * 100,
        )
        return result

    # ------------------------------------------------------------------
    # Inferência
    # ------------------------------------------------------------------

    async def predict(
        self,
        symbol: str,
        df: pd.DataFrame,
        model_type: ModelType = "lstm_attention",
    ) -> Optional[PredictionResult]:
        """
        Gera predição para a última janela disponível no DataFrame.

        Carrega o modelo do disco se não estiver em memória.
        """
        model_key = f"{symbol}_{model_type}"

        if model_key not in self.models:
            loaded = self._try_load_model(model_key)
            if not loaded:
                logger.warning("Modelo '%s' não encontrado. Treine primeiro.", model_key)
                return None

        model  = self.models[model_key]
        scaler = self.scalers.get(model_key)

        seq_len = self.config.neural.input_sequence_length
        try:
            X, _, _ = self.prepare_training_data(df, sequence_length=seq_len)
        except Exception as exc:
            logger.error("Erro ao preparar dados para predição '%s': %s", model_key, exc)
            return None

        if len(X) == 0:
            logger.warning("Sem amostras suficientes para predição de '%s'.", symbol)
            return None

        preds = model.predict(X[-1:], verbose=0)  # (3,) list of arrays

        price_pred = float(preds[0][0][0])
        dir_pred   = float(preds[1][0][0])
        vol_pred   = float(preds[2][0][0]) if len(preds) > 2 else None

        return PredictionResult(
            price_change=price_pred,
            direction=dir_pred,
            direction_confidence=abs(dir_pred - 0.5) * 2,
            volatility=vol_pred,
            model_type=model_type,
            symbol=symbol,
        )

    # ------------------------------------------------------------------
    # Aprendizado contínuo
    # ------------------------------------------------------------------

    async def continuous_learning(
        self,
        symbol: str,
        new_data: pd.DataFrame,
        model_type: ModelType = "lstm_attention",
        retrain_interval_hours: int = 24,
        fine_tune_epochs: int = 10,
    ) -> bool:
        """
        Fine-tuning incremental quando o intervalo de retreino foi atingido.

        Returns True se o fine-tuning foi executado.
        """
        model_key = f"{symbol}_{model_type}"

        if model_key not in self.models:
            logger.info("Modelo '%s' ausente — pulando fine-tuning.", model_key)
            return False

        last = self.last_training.get(model_key)
        if last and (datetime.utcnow() - last) < timedelta(hours=retrain_interval_hours):
            return False

        seq_len = self.config.neural.input_sequence_length
        try:
            X, y, _ = self.prepare_training_data(new_data, sequence_length=seq_len)
        except Exception as exc:
            logger.error("Erro ao preparar dados para fine-tuning '%s': %s", model_key, exc)
            return False

        if len(X) == 0:
            return False

        model = self.models[model_key]

        # Usa taxa de aprendizado reduzida para fine-tuning
        keras.backend.set_value(model.optimizer.learning_rate, 1e-5)

        model.fit(
            X, y,
            epochs=fine_tune_epochs,
            batch_size=self.config.neural.batch_size,
            verbose=0,
        )

        self.last_training[model_key] = datetime.utcnow()
        save_path = self._models_path / f"{model_key}_latest.keras"
        model.save(str(save_path))
        logger.info("Fine-tuning concluído e salvo — '%s'.", model_key)
        return True

    # ------------------------------------------------------------------
    # Avaliação
    # ------------------------------------------------------------------

    def evaluate_model_performance(
        self,
        symbol: str,
        test_df: pd.DataFrame,
        model_type: ModelType = "lstm_attention",
    ) -> Dict[str, float]:
        """Avalia o modelo no conjunto de teste e retorna métricas."""
        model_key = f"{symbol}_{model_type}"

        if model_key not in self.models:
            logger.warning("Modelo '%s' não carregado para avaliação.", model_key)
            return {}

        model = self.models[model_key]
        seq_len = self.config.neural.input_sequence_length

        try:
            X_test, y_test, _ = self.prepare_training_data(test_df, sequence_length=seq_len)
        except Exception as exc:
            logger.error("Erro ao preparar dados de teste '%s': %s", model_key, exc)
            return {}

        if len(X_test) == 0:
            return {}

        raw = model.evaluate(X_test, y_test, verbose=0)
        return {name: float(val) for name, val in zip(model.metrics_names, raw)}

    def get_model_confidence(
        self,
        symbol: str,
        model_type: ModelType = "lstm_attention",
    ) -> float:
        """
        Confiança estimada [0, 1] baseada na tendência de val_loss recente.

        Usa sigmoid invertida: loss caindo → confiança alta.
        """
        model_key = f"{symbol}_{model_type}"
        result = self.training_history.get(model_key)

        if result is None or "val_loss" not in result.history:
            return 0.0

        recent = result.history["val_loss"][-10:]
        if len(recent) < 2:
            return 0.5

        trend   = recent[-1] - recent[0]   # negativo = melhorando
        avg     = float(np.mean(recent))
        z       = trend / avg if avg > 0 else 0.0
        return float(1.0 / (1.0 + np.exp(z)))

    def get_model_summary(
        self, symbol: str, model_type: ModelType = "lstm_attention"
    ) -> Dict[str, Any]:
        """Retorna metadados consolidados do modelo."""
        model_key = f"{symbol}_{model_type}"
        result = self.training_history.get(model_key)

        return {
            "model_key":          model_key,
            "loaded":             model_key in self.models,
            "last_training":      self.last_training.get(model_key),
            "best_val_loss":      result.best_val_loss      if result else None,
            "direction_accuracy": result.direction_accuracy if result else None,
            "epochs_run":         result.epochs_run         if result else None,
            "confidence":         self.get_model_confidence(symbol, model_type),
        }

    # ------------------------------------------------------------------
    # Persistência
    # ------------------------------------------------------------------

    def _try_load_model(self, model_key: str) -> bool:
        """Tenta carregar modelo e scaler do disco. Retorna True se bem-sucedido."""
        model_path  = self._models_path / f"{model_key}_best.keras"
        scaler_path = self._models_path / f"{model_key}_scaler.pkl"

        if not model_path.exists():
            return False

        try:
            self.models[model_key] = keras.models.load_model(
                str(model_path),
                custom_objects={"BahdanauAttention": BahdanauAttention},
            )
            if scaler_path.exists():
                with scaler_path.open("rb") as f:
                    self.scalers[model_key] = pickle.load(f)
            logger.info("Modelo '%s' carregado do disco.", model_key)
            return True
        except Exception as exc:
            logger.error("Falha ao carregar modelo '%s': %s", model_key, exc)
            return False

    def save_model(self, symbol: str, model_type: ModelType = "lstm_attention") -> None:
        """Salva modelo e scaler explicitamente."""
        model_key = f"{symbol}_{model_type}"
        if model_key not in self.models:
            raise KeyError(f"Modelo '{model_key}' não está em memória.")

        model_path  = self._models_path / f"{model_key}_best.keras"
        scaler_path = self._models_path / f"{model_key}_scaler.pkl"

        self.models[model_key].save(str(model_path))
        if model_key in self.scalers:
            with scaler_path.open("wb") as f:
                pickle.dump(self.scalers[model_key], f)

        logger.info("Modelo '%s' salvo em '%s'.", model_key, self._models_path)

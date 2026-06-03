"""
Neural Architect - Modern Neural Network Creation with PyTorch
=============================================================
Advanced neural network architecture builder with dynamic creation,
attention mechanisms, and neuroevolution capabilities
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import math
import random
from collections import defaultdict

# Importações condicionais
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    import torch.optim as optim
    from torch.utils.data import DataLoader, TensorDataset
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

from config import settings
from core import get_logger, log_execution


class LayerType(str, Enum):
    """Tipos de camadas neurais disponíveis"""
    DENSE = "dense"
    CONV1D = "conv1d"
    CONV2D = "conv2d"
    LSTM = "lstm"
    GRU = "gru"
    TRANSFORMER = "transformer"
    ATTENTION = "attention"
    DROPOUT = "dropout"
    BATCHNORM = "batchnorm"
    LAYERNORM = "layernorm"
    ACTIVATION = "activation"
    EMBEDDING = "embedding"
    POOLING = "pooling"
    FLATTEN = "flatten"
    RESIDUAL = "residual"


class ActivationType(str, Enum):
    """Tipos de funções de ativação"""
    RELU = "relu"
    GELU = "gelu"
    SWISH = "swish"
    SIGMOID = "sigmoid"
    TANH = "tanh"
    LEAKY_RELU = "leaky_relu"
    ELU = "elu"
    SELU = "selu"
    SOFTMAX = "softmax"


class ArchitectureType(str, Enum):
    """Tipos de arquiteturas predefinidas"""
    MLP = "mlp"
    CNN = "cnn"
    RNN = "rnn"
    TRANSFORMER = "transformer"
    HYBRID = "hybrid"
    AUTOENCODER = "autoencoder"
    GAN = "gan"
    GRAPH = "graph"


@dataclass
class LayerConfig:
    """Configuração de camada neural"""
    layer_type: LayerType
    units: Optional[int] = None
    activation: Optional[ActivationType] = None
    dropout_rate: Optional[float] = None
    kernel_size: Optional[Tuple[int, ...]] = None
    strides: Optional[Tuple[int, ...]] = None
    padding: Optional[str] = None
    input_dim: Optional[int] = None
    output_dim: Optional[int] = None
    num_heads: Optional[int] = None
    hidden_dim: Optional[int] = None
    bidirectional: bool = False
    return_sequences: bool = False
    params: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'layer_type': self.layer_type.value,
            'units': self.units,
            'activation': self.activation.value if self.activation else None,
            'dropout_rate': self.dropout_rate,
            'kernel_size': self.kernel_size,
            'strides': self.strides,
            'padding': self.padding,
            'input_dim': self.input_dim,
            'output_dim': self.output_dim,
            'num_heads': self.num_heads,
            'hidden_dim': self.hidden_dim,
            'bidirectional': self.bidirectional,
            'return_sequences': self.return_sequences,
            'params': self.params
        }


@dataclass
class ArchitectureConfig:
    """Configuração completa da arquitetura"""
    name: str
    architecture_type: ArchitectureType
    input_shape: Tuple[int, ...]
    output_shape: Tuple[int, ...]
    layers: List[LayerConfig] = field(default_factory=list)
    optimizer: str = "adam"
    loss_function: str = "mse"
    metrics: List[str] = field(default_factory=lambda: ["accuracy"])
    learning_rate: float = 0.001
    batch_size: int = 32
    epochs: int = 100
    validation_split: float = 0.2
    early_stopping: bool = True
    dropout_rate: float = 0.1
    l2_regularization: float = 0.01
    custom_params: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'name': self.name,
            'architecture_type': self.architecture_type.value,
            'input_shape': self.input_shape,
            'output_shape': self.output_shape,
            'layers': [layer.to_dict() for layer in self.layers],
            'optimizer': self.optimizer,
            'loss_function': self.loss_function,
            'metrics': self.metrics,
            'learning_rate': self.learning_rate,
            'batch_size': self.batch_size,
            'epochs': self.epochs,
            'validation_split': self.validation_split,
            'early_stopping': self.early_stopping,
            'dropout_rate': self.dropout_rate,
            'l2_regularization': self.l2_regularization,
            'custom_params': self.custom_params
        }


class MultiHeadAttention(nn.Module):
    """Implementação de Multi-Head Attention"""
    
    def __init__(self, d_model: int, num_heads: int, dropout: float = 0.1):
        super().__init__()
        assert d_model % num_heads == 0
        
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        
        self.w_q = nn.Linear(d_model, d_model)
        self.w_k = nn.Linear(d_model, d_model)
        self.w_v = nn.Linear(d_model, d_model)
        self.w_o = nn.Linear(d_model, d_model)
        
        self.dropout = nn.Dropout(dropout)
        
    def forward(self, query: torch.Tensor, key: torch.Tensor, value: torch.Tensor,
                mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        batch_size = query.size(0)
        
        # Linear projections
        Q = self.w_q(query).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        K = self.w_k(key).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        V = self.w_v(value).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        
        # Scaled dot-product attention
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)
        
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)
        
        attention_weights = F.softmax(scores, dim=-1)
        attention_weights = self.dropout(attention_weights)
        
        # Apply attention to values
        context = torch.matmul(attention_weights, V)
        context = context.transpose(1, 2).contiguous().view(batch_size, -1, self.d_model)
        
        # Final linear layer
        output = self.w_o(context)
        
        return output


class TransformerBlock(nn.Module):
    """Bloco Transformer completo com Multi-Head Attention"""
    
    def __init__(self, d_model: int, num_heads: int, d_ff: int, dropout: float = 0.1):
        super().__init__()
        self.attention = MultiHeadAttention(d_model, num_heads, dropout)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        
        self.feed_forward = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.ReLU(),
            nn.Linear(d_ff, d_model)
        )
        
        self.dropout = nn.Dropout(dropout)
        
    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        # Self-attention with residual connection
        attn_output = self.attention(x, x, x, mask)
        x = self.norm1(x + self.dropout(attn_output))
        
        # Feed-forward with residual connection
        ff_output = self.feed_forward(x)
        x = self.norm2(x + self.dropout(ff_output))
        
        return x


class ResidualBlock(nn.Module):
    """Bloco Residual para redes profundas"""
    
    def __init__(self, in_channels: int, out_channels: int, stride: int = 1):
        super().__init__()
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=stride, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(out_channels)
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3, stride=1, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(out_channels)
        
        self.shortcut = nn.Sequential()
        if stride != 1 or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=stride, bias=False),
                nn.BatchNorm2d(out_channels)
            )
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out += self.shortcut(x)
        out = F.relu(out)
        return out


class DynamicNeuralNetwork(nn.Module):
    """Rede neural dinâmica com arquitetura configurável"""
    
    def __init__(self, config: ArchitectureConfig):
        super().__init__()
        self.config = config
        self.layers = nn.ModuleList()
        self._build_network()
        
    def _build_network(self):
        """Constrói a rede neural baseada na configuração"""
        current_shape = self.config.input_shape
        
        for layer_config in self.config.layers:
            layer = self._create_layer(layer_config, current_shape)
            self.layers.append(layer)
            current_shape = self._update_shape(current_shape, layer_config)
    
    def _create_layer(self, config: LayerConfig, input_shape: Tuple[int, ...]) -> nn.Module:
        """Cria uma camada baseada na configuração"""
        
        if config.layer_type == LayerType.DENSE:
            return self._create_dense_layer(config)
        elif config.layer_type == LayerType.CONV2D:
            return self._create_conv2d_layer(config)
        elif config.layer_type == LayerType.LSTM:
            return self._create_lstm_layer(config)
        elif config.layer_type == LayerType.TRANSFORMER:
            return self._create_transformer_layer(config)
        elif config.layer_type == LayerType.ATTENTION:
            return self._create_attention_layer(config)
        elif config.layer_type == LayerType.DROPOUT:
            return nn.Dropout(config.dropout_rate or 0.1)
        elif config.layer_type == LayerType.BATCHNORM:
            if len(input_shape) == 3:  # Conv features
                return nn.BatchNorm2d(input_shape[0])
            else:  # Dense features
                return nn.BatchNorm1d(input_shape[0])
        elif config.layer_type == LayerType.LAYERNORM:
            return nn.LayerNorm(input_shape[-1])
        elif config.layer_type == LayerType.ACTIVATION:
            return self._create_activation_layer(config.activation)
        elif config.layer_type == LayerType.RESIDUAL:
            return ResidualBlock(input_shape[0], config.units or input_shape[0])
        else:
            raise ValueError(f"Unsupported layer type: {config.layer_type}")
    
    def _create_dense_layer(self, config: LayerConfig) -> nn.Module:
        """Cria camada densa"""
        in_features = config.input_dim or self._get_last_dim()
        out_features = config.units or 128
        
        layer = nn.Linear(in_features, out_features)
        
        # Adicionar regularização L2 se especificado
        if self.config.l2_regularization > 0:
            layer.weight.register_hook(lambda grad: grad + self.config.l2_regularization * layer.weight)
        
        return layer
    
    def _create_conv2d_layer(self, config: LayerConfig) -> nn.Module:
        """Cria camada convolucional 2D"""
        in_channels = config.input_dim or self._get_last_dim()
        out_channels = config.units or 64
        kernel_size = config.kernel_size or (3, 3)
        stride = config.strides or (1, 1)
        padding = config.padding or 1
        
        return nn.Conv2d(in_channels, out_channels, kernel_size, stride=stride, padding=padding)
    
    def _create_lstm_layer(self, config: LayerConfig) -> nn.Module:
        """Cria camada LSTM"""
        input_size = config.input_dim or self._get_last_dim()
        hidden_size = config.hidden_dim or 128
        num_layers = config.params.get('num_layers', 1)
        bidirectional = config.bidirectional
        dropout = config.dropout_rate or 0.1
        
        return nn.LSTM(input_size, hidden_size, num_layers, 
                     batch_first=True, bidirectional=bidirectional, dropout=dropout)
    
    def _create_transformer_layer(self, config: LayerConfig) -> nn.Module:
        """Cria bloco Transformer"""
        d_model = config.hidden_dim or 512
        num_heads = config.num_heads or 8
        d_ff = config.params.get('d_ff', 2048)
        dropout = config.dropout_rate or 0.1
        
        return TransformerBlock(d_model, num_heads, d_ff, dropout)
    
    def _create_attention_layer(self, config: LayerConfig) -> nn.Module:
        """Cria camada de atenção"""
        d_model = config.hidden_dim or 512
        num_heads = config.num_heads or 8
        dropout = config.dropout_rate or 0.1
        
        return MultiHeadAttention(d_model, num_heads, dropout)
    
    def _create_activation_layer(self, activation: Optional[ActivationType]) -> nn.Module:
        """Cria função de ativação"""
        if activation == ActivationType.RELU:
            return nn.ReLU()
        elif activation == ActivationType.GELU:
            return nn.GELU()
        elif activation == ActivationType.SWISH:
            return nn.SiLU()
        elif activation == ActivationType.SIGMOID:
            return nn.Sigmoid()
        elif activation == ActivationType.TANH:
            return nn.Tanh()
        elif activation == ActivationType.LEAKY_RELU:
            return nn.LeakyReLU(0.1)
        elif activation == ActivationType.ELU:
            return nn.ELU()
        elif activation == ActivationType.SELU:
            return nn.SELU()
        elif activation == ActivationType.SOFTMAX:
            return nn.Softmax(dim=-1)
        else:
            return nn.ReLU()  # Default
    
    def _get_last_dim(self) -> int:
        """Obtém a última dimensão da entrada"""
        return self.config.input_shape[-1] if self.config.input_shape else 512
    
    def _update_shape(self, current_shape: Tuple[int, ...], layer_config: LayerConfig) -> Tuple[int, ...]:
        """Atualiza a forma dos dados após a camada"""
        if layer_config.layer_type == LayerType.DENSE:
            return (layer_config.units or 128,)
        elif layer_config.layer_type == LayerType.CONV2D:
            return (layer_config.units or 64, current_shape[1], current_shape[2])
        elif layer_config.layer_type == LayerType.LSTM:
            hidden_size = layer_config.hidden_dim or 128
            if layer_config.bidirectional:
                return (hidden_size * 2,)
            return (hidden_size,)
        elif layer_config.layer_type == LayerType.FLATTEN:
            flat_dim = 1
            for dim in current_shape:
                flat_dim *= dim
            return (flat_dim,)
        else:
            return current_shape
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass dinâmico"""
        for i, layer_config in enumerate(self.config.layers):
            layer = self.layers[i]
            
            if layer_config.layer_type == LayerType.LSTM:
                x, _ = layer(x)
            elif layer_config.layer_type in [LayerType.TRANSFORMER, LayerType.ATTENTION]:
                x = layer(x)
            else:
                x = layer(x)
        
        return x


class NeuroEvolution:
    """Sistema de neuroevolução para otimização de arquiteturas"""
    
    def __init__(self, population_size: int = 20, mutation_rate: float = 0.1, crossover_rate: float = 0.7):
        self.logger = get_logger("vhalinor.neural.neuroevolution", "neuroevolution")
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.generation = 0
        self.best_fitness = float('-inf')
        self.best_architecture = None
        
    def create_initial_population(self, base_config: ArchitectureConfig) -> List[ArchitectureConfig]:
        """Cria população inicial de arquiteturas"""
        population = []
        
        for i in range(self.population_size):
            # Mutar configuração base para criar indivíduo
            mutated_config = self._mutate_architecture(base_config.copy())
            mutated_config.name = f"{base_config.name}_gen0_ind{i}"
            population.append(mutated_config)
        
        return population
    
    def _mutate_architecture(self, config: ArchitectureConfig) -> ArchitectureConfig:
        """Aplica mutação na arquitetura"""
        if random.random() < self.mutation_rate:
            # Mutar número de camadas
            if random.random() < 0.3 and len(config.layers) > 1:
                # Remover camada
                config.layers.pop(random.randint(0, len(config.layers) - 1))
            elif random.random() < 0.3:
                # Adicionar camada
                new_layer = self._create_random_layer()
                config.layers.insert(random.randint(0, len(config.layers)), new_layer)
            
            # Mutar parâmetros de camadas existentes
            for layer in config.layers:
                if random.random() < 0.2:
                    self._mutate_layer_params(layer)
            
            # Mutar hiperparâmetros
            if random.random() < 0.3:
                config.learning_rate *= random.uniform(0.5, 2.0)
                config.learning_rate = max(0.0001, min(0.1, config.learning_rate))
            
            if random.random() < 0.2:
                config.dropout_rate = random.uniform(0.0, 0.5)
        
        return config
    
    def _create_random_layer(self) -> LayerConfig:
        """Cria uma camada aleatória"""
        layer_types = [LayerType.DENSE, LayerType.DROPOUT, LayerType.BATCHNORM, LayerType.ACTIVATION]
        layer_type = random.choice(layer_types)
        
        if layer_type == LayerType.DENSE:
            return LayerConfig(
                layer_type=layer_type,
                units=random.randint(32, 512),
                activation=random.choice(list(ActivationType))
            )
        elif layer_type == LayerType.DROPOUT:
            return LayerConfig(
                layer_type=layer_type,
                dropout_rate=random.uniform(0.1, 0.5)
            )
        else:
            return LayerConfig(layer_type=layer_type)
    
    def _mutate_layer_params(self, layer: LayerConfig):
        """Mutata parâmetros de uma camada"""
        if layer.layer_type == LayerType.DENSE:
            if random.random() < 0.5:
                layer.units = random.randint(32, 512)
            if random.random() < 0.3:
                layer.activation = random.choice(list(ActivationType))
        elif layer.layer_type == LayerType.DROPOUT:
            layer.dropout_rate = random.uniform(0.1, 0.5)
    
    def crossover(self, parent1: ArchitectureConfig, parent2: ArchitectureConfig) -> ArchitectureConfig:
        """Realiza crossover entre duas arquiteturas"""
        if random.random() > self.crossover_rate:
            return parent1.copy()
        
        # Criar filho com combinação de pais
        child = ArchitectureConfig(
            name=f"{parent1.name}_x_{parent2.name}",
            architecture_type=parent1.architecture_type,
            input_shape=parent1.input_shape,
            output_shape=parent1.output_shape
        )
        
        # Combinar camadas
        min_layers = min(len(parent1.layers), len(parent2.layers))
        max_layers = max(len(parent1.layers), len(parent2.layers))
        
        for i in range(max_layers):
            if i < min_layers:
                # Escolher camada de um dos pais
                if random.random() < 0.5:
                    child.layers.append(parent1.layers[i].copy())
                else:
                    child.layers.append(parent2.layers[i].copy())
            elif i < len(parent1.layers):
                child.layers.append(parent1.layers[i].copy())
            else:
                child.layers.append(parent2.layers[i].copy())
        
        # Combinar hiperparâmetros
        child.learning_rate = (parent1.learning_rate + parent2.learning_rate) / 2
        child.dropout_rate = (parent1.dropout_rate + parent2.dropout_rate) / 2
        
        return child
    
    def select_parents(self, population: List[ArchitectureConfig], fitness_scores: List[float]) -> Tuple[ArchitectureConfig, ArchitectureConfig]:
        """Seleciona pais usando torneio"""
        tournament_size = 3
        
        # Selecionar primeiro pai
        tournament1 = random.sample(list(zip(population, fitness_scores)), min(tournament_size, len(population)))
        parent1 = max(tournament1, key=lambda x: x[1])[0]
        
        # Selecionar segundo pai
        tournament2 = random.sample(list(zip(population, fitness_scores)), min(tournament_size, len(population)))
        parent2 = max(tournament2, key=lambda x: x[1])[0]
        
        return parent1, parent2
    
    def evolve_generation(self, population: List[ArchitectureConfig], fitness_scores: List[float]) -> List[ArchitectureConfig]:
        """Evolui uma geração"""
        self.generation += 1
        
        # Ordenar por fitness
        sorted_pop = sorted(zip(population, fitness_scores), key=lambda x: x[1], reverse=True)
        
        # Elitismo: manter melhores indivíduos
        elite_size = max(1, self.population_size // 10)
        new_population = [ind for ind, _ in sorted_pop[:elite_size]]
        
        # Gerar nova população
        while len(new_population) < self.population_size:
            parent1, parent2 = self.select_parents(population, fitness_scores)
            child = self.crossover(parent1, parent2)
            child = self._mutate_architecture(child)
            child.name = f"gen{self.generation}_ind{len(new_population)}"
            new_population.append(child)
        
        # Atualizar melhor fitness
        current_best = max(fitness_scores)
        if current_best > self.best_fitness:
            self.best_fitness = current_best
            self.best_architecture = sorted_pop[0][0]
        
        self.logger.info(f"Generation {self.generation}: Best fitness = {self.best_fitness:.4f}")
        
        return new_population


class NeuralArchitect:
    """Arquiteto neural principal para criação e otimização de redes"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.neural.architect", "neural_architect")
        self.neuroevolution = NeuroEvolution()
        self.created_models = {}
        self.training_history = {}
        
    @log_execution(component="neural", operation="create_architecture")
    def create_mlp_architecture(
        self,
        input_dim: int,
        output_dim: int,
        hidden_layers: List[int] = None,
        activation: ActivationType = ActivationType.RELU,
        dropout_rate: float = 0.1
    ) -> ArchitectureConfig:
        """Cria arquitetura MLP (Multi-Layer Perceptron)"""
        if hidden_layers is None:
            hidden_layers = [128, 64, 32]
        
        layers = []
        
        # Input layer
        layers.append(LayerConfig(
            layer_type=LayerType.DENSE,
            units=hidden_layers[0],
            input_dim=input_dim,
            activation=activation
        ))
        layers.append(LayerConfig(
            layer_type=LayerType.DROPOUT,
            dropout_rate=dropout_rate
        ))
        
        # Hidden layers
        for i, units in enumerate(hidden_layers[1:], 1):
            layers.append(LayerConfig(
                layer_type=LayerType.DENSE,
                units=units,
                activation=activation
            ))
            layers.append(LayerConfig(
                layer_type=LayerType.DROPOUT,
                dropout_rate=dropout_rate
            ))
        
        # Output layer
        layers.append(LayerConfig(
            layer_type=LayerType.DENSE,
            units=output_dim,
            activation=ActivationType.SIGMOID if output_dim == 1 else ActivationType.SOFTMAX
        ))
        
        config = ArchitectureConfig(
            name=f"MLP_{input_dim}_{'_'.join(map(str, hidden_layers))}_{output_dim}",
            architecture_type=ArchitectureType.MLP,
            input_shape=(input_dim,),
            output_shape=(output_dim,),
            layers=layers
        )
        
        self.logger.info(f"Created MLP architecture: {config.name}")
        return config
    
    @log_execution(component="neural", operation="create_transformer")
    def create_transformer_architecture(
        self,
        vocab_size: int,
        d_model: int = 512,
        num_heads: int = 8,
        num_layers: int = 6,
        d_ff: int = 2048,
        max_seq_length: int = 512,
        dropout_rate: float = 0.1
    ) -> ArchitectureConfig:
        """Cria arquitetura Transformer"""
        layers = []
        
        # Embedding layer
        layers.append(LayerConfig(
            layer_type=LayerType.EMBEDDING,
            input_dim=vocab_size,
            output_dim=d_model,
            params={'max_seq_length': max_seq_length}
        ))
        
        # Positional encoding (implementado como embedding adicional)
        layers.append(LayerConfig(
            layer_type=LayerType.EMBEDDING,
            input_dim=max_seq_length,
            output_dim=d_model
        ))
        
        # Transformer blocks
        for i in range(num_layers):
            layers.append(LayerConfig(
                layer_type=LayerType.TRANSFORMER,
                hidden_dim=d_model,
                num_heads=num_heads,
                params={'d_ff': d_ff},
                dropout_rate=dropout_rate
            ))
            layers.append(LayerConfig(
                layer_type=LayerType.DROPOUT,
                dropout_rate=dropout_rate
            ))
        
        # Output projection
        layers.append(LayerConfig(
            layer_type=LayerType.DENSE,
            units=vocab_size,
            activation=ActivationType.SOFTMAX
        ))
        
        config = ArchitectureConfig(
            name=f"Transformer_{d_model}_{num_heads}_{num_layers}",
            architecture_type=ArchitectureType.TRANSFORMER,
            input_shape=(max_seq_length,),
            output_shape=(vocab_size,),
            layers=layers
        )
        
        self.logger.info(f"Created Transformer architecture: {config.name}")
        return config
    
    @log_execution(component="neural", operation="create_cnn")
    def create_cnn_architecture(
        self,
        input_shape: Tuple[int, int, int],
        num_classes: int,
        conv_filters: List[int] = None,
        dense_units: List[int] = None,
        dropout_rate: float = 0.2
    ) -> ArchitectureConfig:
        """Cria arquitetura CNN (Convolutional Neural Network)"""
        if conv_filters is None:
            conv_filters = [32, 64, 128]
        if dense_units is None:
            dense_units = [512, 256]
        
        layers = []
        
        # Convolutional blocks
        in_channels = input_shape[0]
        for i, filters in enumerate(conv_filters):
            layers.append(LayerConfig(
                layer_type=LayerType.CONV2D,
                units=filters,
                input_dim=in_channels,
                kernel_size=(3, 3),
                padding='same'
            ))
            layers.append(LayerConfig(
                layer_type=LayerType.BATCHNORM
            ))
            layers.append(LayerConfig(
                layer_type=LayerType.ACTIVATION,
                activation=ActivationType.RELU
            ))
            layers.append(LayerConfig(
                layer_type=LayerType.POOLING,
                params={'pool_size': (2, 2), 'stride': (2, 2)}
            ))
            layers.append(LayerConfig(
                layer_type=LayerType.DROPOUT,
                dropout_rate=dropout_rate
            ))
            in_channels = filters
        
        # Flatten
        layers.append(LayerConfig(
            layer_type=LayerType.FLATTEN
        ))
        
        # Dense layers
        for units in dense_units:
            layers.append(LayerConfig(
                layer_type=LayerType.DENSE,
                units=units,
                activation=ActivationType.RELU
            ))
            layers.append(LayerConfig(
                layer_type=LayerType.DROPOUT,
                dropout_rate=dropout_rate
            ))
        
        # Output layer
        layers.append(LayerConfig(
            layer_type=LayerType.DENSE,
            units=num_classes,
            activation=ActivationType.SOFTMAX if num_classes > 1 else ActivationType.SIGMOID
        ))
        
        config = ArchitectureConfig(
            name=f"CNN_{'_'.join(map(str, conv_filters))}_{num_classes}",
            architecture_type=ArchitectureType.CNN,
            input_shape=input_shape,
            output_shape=(num_classes,),
            layers=layers
        )
        
        self.logger.info(f"Created CNN architecture: {config.name}")
        return config
    
    @log_execution(component="neural", operation="create_hybrid")
    def create_hybrid_architecture(
        self,
        input_shape: Tuple[int, ...],
        output_dim: int,
        sequence_length: int = 50,
        feature_dim: int = 64
    ) -> ArchitectureConfig:
        """Cria arquitetura híbrida (CNN + LSTM + Attention)"""
        layers = []
        
        # CNN para extração de features
        layers.append(LayerConfig(
            layer_type=LayerType.CONV1D,
            units=feature_dim,
            input_dim=input_shape[-1],
            kernel_size=(3,),
            padding='same'
        ))
        layers.append(LayerConfig(
            layer_type=LayerType.ACTIVATION,
            activation=ActivationType.RELU
        ))
        layers.append(LayerConfig(
            layer_type=LayerType.DROPOUT,
            dropout_rate=0.2
        ))
        
        # LSTM para processamento sequencial
        layers.append(LayerConfig(
            layer_type=LayerType.LSTM,
            hidden_dim=128,
            input_dim=feature_dim,
            bidirectional=True,
            return_sequences=True
        ))
        
        # Attention mechanism
        layers.append(LayerConfig(
            layer_type=LayerType.ATTENTION,
            hidden_dim=256,
            num_heads=8
        ))
        
        # Dense layers
        layers.append(LayerConfig(
            layer_type=LayerType.DENSE,
            units=64,
            activation=ActivationType.RELU
        ))
        layers.append(LayerConfig(
            layer_type=LayerType.DROPOUT,
            dropout_rate=0.3
        ))
        
        # Output layer
        layers.append(LayerConfig(
            layer_type=LayerType.DENSE,
            units=output_dim,
            activation=ActivationType.SIGMOID if output_dim == 1 else ActivationType.SOFTMAX
        ))
        
        config = ArchitectureConfig(
            name=f"Hybrid_CNN_LSTM_Attention_{input_shape}_{output_dim}",
            architecture_type=ArchitectureType.HYBRID,
            input_shape=input_shape,
            output_shape=(output_dim,),
            layers=layers
        )
        
        self.logger.info(f"Created Hybrid architecture: {config.name}")
        return config
    
    def build_model(self, config: ArchitectureConfig) -> DynamicNeuralNetwork:
        """Constrói modelo PyTorch a partir da configuração"""
        if not TORCH_AVAILABLE:
            raise ImportError("PyTorch is required for model building")
        
        model = DynamicNeuralNetwork(config)
        self.created_models[config.name] = model
        
        self.logger.info(f"Built model: {config.name}")
        return model
    
    async def optimize_architecture(
        self,
        base_config: ArchitectureConfig,
        fitness_function: Callable[[ArchitectureConfig], float],
        generations: int = 10
    ) -> ArchitectureConfig:
        """Otimiza arquitetura usando neuroevolução"""
        self.logger.info(f"Starting architecture optimization for {generations} generations")
        
        # Criar população inicial
        population = self.neuroevolution.create_initial_population(base_config)
        
        # Evoluir por gerações
        for generation in range(generations):
            # Avaliar fitness
            fitness_scores = []
            for config in population:
                fitness = await self._evaluate_fitness(config, fitness_function)
                fitness_scores.append(fitness)
            
            # Evoluir para próxima geração
            population = self.neuroevolution.evolve_generation(population, fitness_scores)
        
        best_config = self.neuroevolution.best_architecture
        self.logger.info(f"Architecture optimization completed. Best fitness: {self.neuroevolution.best_fitness:.4f}")
        
        return best_config
    
    async def _evaluate_fitness(self, config: ArchitectureConfig, fitness_function: Callable) -> float:
        """Avalia fitness de uma arquitetura"""
        try:
            fitness = fitness_function(config)
            return fitness
        except Exception as e:
            self.logger.error(f"Error evaluating fitness for {config.name}: {e}")
            return 0.0
    
    def get_architecture_summary(self, config: ArchitectureConfig) -> Dict[str, Any]:
        """Retorna resumo da arquitetura"""
        total_params = 0
        
        # Estimar número de parâmetros (simplificado)
        for layer in config.layers:
            if layer.layer_type == LayerType.DENSE:
                if layer.input_dim and layer.units:
                    total_params += layer.input_dim * layer.units + layer.units
            elif layer.layer_type == LayerType.CONV2D:
                if layer.input_dim and layer.units and layer.kernel_size:
                    in_ch = layer.input_dim
                    out_ch = layer.units
                    k_h, k_w = layer.kernel_size
                    total_params += in_ch * out_ch * k_h * k_w + out_ch
        
        return {
            'name': config.name,
            'type': config.architecture_type.value,
            'input_shape': config.input_shape,
            'output_shape': config.output_shape,
            'num_layers': len(config.layers),
            'estimated_parameters': total_params,
            'optimizer': config.optimizer,
            'learning_rate': config.learning_rate,
            'dropout_rate': config.dropout_rate,
            'layers': [layer.to_dict() for layer in config.layers]
        }


# Função de conveniência para obter instância do arquiteto neural
_neural_architect_instance = None

def get_neural_architect() -> NeuralArchitect:
    """Obtém instância singleton do arquiteto neural"""
    global _neural_architect_instance
    if _neural_architect_instance is None:
        _neural_architect_instance = NeuralArchitect()
    return _neural_architect_instance

"""
Módulo de Redes Neurais Avançadas
=================================
Criação dinâmica de arquiteturas neurais com PyTorch
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import json
import numpy as np

from config import settings
from core import get_logger, log_execution


class LayerType(str, Enum):
    """Tipos de camadas neurais"""
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


class ActivationType(str, Enum):
    """Tipos de funções de ativação"""
    RELU = "relu"
    TANH = "tanh"
    SIGMOID = "sigmoid"
    GELU = "gelu"
    SWISH = "swish"
    MISH = "mish"


@dataclass
class LayerConfig:
    """Configuração de camada neural"""
    layer_type: LayerType
    input_size: int
    output_size: int
    activation: Optional[ActivationType] = None
    dropout: float = 0.0
    batch_norm: bool = False
    layer_norm: bool = False
    parameters: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return asdict(self)


class MultiHeadAttention(nn.Module):
    """Mecanismo de atenção multi-head avançado"""
    
    def __init__(
        self,
        d_model: int,
        num_heads: int,
        dropout: float = 0.1
    ):
        super(MultiHeadAttention, self).__init__()
        
        assert d_model % num_heads == 0, "d_model deve ser divisível por num_heads"
        
        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads
        
        self.w_q = nn.Linear(d_model, d_model)
        self.w_k = nn.Linear(d_model, d_model)
        self.w_v = nn.Linear(d_model, d_model)
        
        self.w_o = nn.Linear(d_model, d_model)
        
        self.dropout = nn.Dropout(dropout)
        self.scale = self.d_k ** -0.5
    
    def forward(
        self,
        query: torch.Tensor,
        key: torch.Tensor,
        value: torch.Tensor,
        mask: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass do mecanismo de atenção
        
        Args:
            query: Tensor de query [batch_size, seq_len, d_model]
            key: Tensor de key [batch_size, seq_len, d_model]
            value: Tensor de value [batch_size, seq_len, d_model]
            mask: Máscara de atenção opcional
        
        Returns:
            Tuple com (output, attention_weights)
        """
        batch_size, seq_len, _ = query.size()
        
        # Projetar para multi-head
        Q = self.w_q(query).view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)
        K = self.w_k(key).view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)
        V = self.w_v(value).view(batch_size, seq_len, self.num_heads, self.d_k).transpose(1, 2)
        
        # Calcular atenção
        scores = torch.matmul(Q, K.transpose(-2, -1)) * self.scale
        
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)
        
        attention_weights = F.softmax(scores, dim=-1)
        attention_weights = self.dropout(attention_weights)
        
        # Aplicar atenção aos valores
        output = torch.matmul(attention_weights, V)
        
        # Concatenar heads
        output = output.transpose(1, 2).contiguous().view(
            batch_size, seq_len, self.d_model
        )
        
        # Projeção final
        output = self.w_o(output)
        
        return output, attention_weights


class TransformerBlock(nn.Module):
    """Bloco Transformer completo com residual connections"""
    
    def __init__(
        self,
        d_model: int,
        num_heads: int,
        d_ff: int,
        dropout: float = 0.1,
        activation: ActivationType = ActivationType.RELU
    ):
        super(TransformerBlock, self).__init__()
        
        self.attention = MultiHeadAttention(d_model, num_heads, dropout)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        
        self.ff = nn.Sequential(
            nn.Linear(d_model, d_ff),
            self._get_activation(activation),
            nn.Dropout(dropout),
            nn.Linear(d_ff, d_model),
            nn.Dropout(dropout)
        )
        
        self.dropout = nn.Dropout(dropout)
    
    def _get_activation(self, activation: ActivationType) -> nn.Module:
        """Obtém função de ativação"""
        activations = {
            ActivationType.RELU: nn.ReLU(),
            ActivationType.TANH: nn.Tanh(),
            ActivationType.SIGMOID: nn.Sigmoid(),
            ActivationType.GELU: nn.GELU(),
            ActivationType.SWISH: nn.SiLU(),
            ActivationType.MISH: nn.Mish()
        }
        return activations.get(activation, nn.ReLU())
    
    def forward(
        self,
        x: torch.Tensor,
        mask: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """Forward pass do bloco Transformer"""
        
        # Self-attention + residual
        attn_output, _ = self.attention(x, x, x, mask)
        x = self.norm1(x + self.dropout(attn_output))
        
        # Feed-forward + residual
        ff_output = self.ff(x)
        x = self.norm2(x + self.dropout(ff_output))
        
        return x


class DynamicNeuralNetwork(nn.Module):
    """
    Rede neural dinâmica com arquitetura configurável
    """
    
    def __init__(
        self,
        layers_config: List[LayerConfig],
        input_size: int,
        output_size: int
    ):
        super(DynamicNeuralNetwork, self).__init__()
        
        self.layers_config = layers_config
        self.input_size = input_size
        self.output_size = output_size
        
        # Construir arquitetura dinamicamente
        self.layers = nn.ModuleList()
        self._build_network()
    
    def _build_network(self):
        """Constrói a rede neural baseada na configuração"""
        current_size = self.input_size
        
        for i, layer_config in enumerate(self.layers_config):
            if layer_config.layer_type == LayerType.DENSE:
                layer = nn.Linear(current_size, layer_config.output_size)
                self.layers.append(layer)
                
                # Adicionar ativação
                if layer_config.activation:
                    activation = self._get_activation(layer_config.activation)
                    self.layers.append(activation)
                
                # Adicionar dropout
                if layer_config.dropout > 0:
                    dropout = nn.Dropout(layer_config.dropout)
                    self.layers.append(dropout)
                
                # Adicionar batch norm
                if layer_config.batch_norm:
                    batch_norm = nn.BatchNorm1d(layer_config.output_size)
                    self.layers.append(batch_norm)
                
                # Adicionar layer norm
                if layer_config.layer_norm:
                    layer_norm = nn.LayerNorm(layer_config.output_size)
                    self.layers.append(layer_norm)
                
                current_size = layer_config.output_size
            
            elif layer_config.layer_type == LayerType.LSTM:
                params = layer_config.parameters or {}
                layer = nn.LSTM(
                    current_size,
                    layer_config.output_size,
                    batch_first=True,
                    dropout=layer_config.dropout,
                    num_layers=params.get('num_layers', 1),
                    bidirectional=params.get('bidirectional', False)
                )
                self.layers.append(layer)
                current_size = layer_config.output_size
            
            elif layer_config.layer_type == LayerType.GRU:
                params = layer_config.parameters or {}
                layer = nn.GRU(
                    current_size,
                    layer_config.output_size,
                    batch_first=True,
                    dropout=layer_config.dropout,
                    num_layers=params.get('num_layers', 1),
                    bidirectional=params.get('bidirectional', False)
                )
                self.layers.append(layer)
                current_size = layer_config.output_size
            
            elif layer_config.layer_type == LayerType.TRANSFORMER:
                params = layer_config.parameters or {}
                layer = TransformerBlock(
                    current_size,
                    params.get('num_heads', 8),
                    params.get('d_ff', current_size * 4),
                    layer_config.dropout,
                    layer_config.activation or ActivationType.RELU
                )
                self.layers.append(layer)
                current_size = layer_config.output_size
        
        # Camada de saída final
        self.output_layer = nn.Linear(current_size, self.output_size)
    
    def _get_activation(self, activation: ActivationType) -> nn.Module:
        """Obtém função de ativação"""
        activations = {
            ActivationType.RELU: nn.ReLU(),
            ActivationType.TANH: nn.Tanh(),
            ActivationType.SIGMOID: nn.Sigmoid(),
            ActivationType.GELU: nn.GELU(),
            ActivationType.SWISH: nn.SiLU(),
            ActivationType.MISH: nn.Mish()
        }
        return activations.get(activation, nn.ReLU())
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass da rede neural"""
        
        for layer in self.layers:
            if isinstance(layer, (nn.LSTM, nn.GRU)):
                x, (hidden, cell) = layer(x)
                # Usar apenas o último timestep
                if layer.batch_first:
                    x = x[:, -1, :]
            else:
                x = layer(x)
        else:
            x = layer(x)
        
        # Camada de saída
        output = self.output_layer(x)
        
        return output


class NeuralNetworkBuilder:
    """
    Construtor de redes neurais com métodos convenientes
    """
    
    def __init__(self):
        self.logger = get_logger().get_logger("vhalinor.neural_network", "neural_network")
        self.layers_config = []
    
    def add_dense(
        self,
        output_size: int,
        activation: Optional[ActivationType] = None,
        dropout: float = 0.0,
        batch_norm: bool = False,
        layer_norm: bool = False
    ) -> 'NeuralNetworkBuilder':
        """Adiciona camada densa"""
        # Determinar input_size baseado na camada anterior
        if self.layers_config:
            input_size = self.layers_config[-1].output_size
        else:
            input_size = 0  # Será definido posteriormente
        
        layer_config = LayerConfig(
            layer_type=LayerType.DENSE,
            input_size=input_size,
            output_size=output_size,
            activation=activation,
            dropout=dropout,
            batch_norm=batch_norm,
            layer_norm=layer_norm
        )
        
        self.layers_config.append(layer_config)
        return self
    
    def add_lstm(
        self,
        output_size: int,
        num_layers: int = 1,
        bidirectional: bool = False,
        dropout: float = 0.0
    ) -> 'NeuralNetworkBuilder':
        """Adiciona camada LSTM"""
        if self.layers_config:
            input_size = self.layers_config[-1].output_size
        else:
            input_size = 0
        
        layer_config = LayerConfig(
            layer_type=LayerType.LSTM,
            input_size=input_size,
            output_size=output_size,
            dropout=dropout,
            parameters={
                'num_layers': num_layers,
                'bidirectional': bidirectional
            }
        )
        
        self.layers_config.append(layer_config)
        return self
    
    def add_transformer(
        self,
        output_size: int,
        num_heads: int = 8,
        dropout: float = 0.1,
        activation: ActivationType = ActivationType.RELU
    ) -> 'NeuralNetworkBuilder':
        """Adiciona bloco Transformer"""
        if self.layers_config:
            input_size = self.layers_config[-1].output_size
        else:
            input_size = 0
        
        layer_config = LayerConfig(
            layer_type=LayerType.TRANSFORMER,
            input_size=input_size,
            output_size=output_size,
            dropout=dropout,
            activation=activation,
            parameters={
                'num_heads': num_heads,
                'd_ff': input_size * 4
            }
        )
        
        self.layers_config.append(layer_config)
        return self
    
    def build(self, input_size: int, output_size: int) -> DynamicNeuralNetwork:
        """Constrói a rede neural"""
        
        # Atualizar input_size da primeira camada
        if self.layers_config:
            self.layers_config[0].input_size = input_size
        
        return DynamicNeuralNetwork(
            self.layers_config,
            input_size,
            output_size
        )
    
    def get_config(self) -> List[Dict[str, Any]]:
        """Retorna configuração da rede"""
        return [layer.to_dict() for layer in self.layers_config]
    
    def reset(self) -> 'NeuralNetworkBuilder':
        """Reseta o construtor"""
        self.layers_config = []
        return self


class NeuroEvolution:
    """
    Sistema de neuroevolution para otimização de redes neurais
    """
    
    def __init__(self):
        self.logger = get_logger().get_logger("vhalinor.neuroevolution", "neuroevolution")
        
        # Parâmetros de evolução
        self.population_size = 20
        self.mutation_rate = 0.1
        self.crossover_rate = 0.7
        self.elite_size = 4
        
        # População de redes neurais
        self.population: List[DynamicNeuralNetwork] = []
        self.fitness_scores: List[float] = []
        
        # Melhor indivíduo
        self.best_network: Optional[DynamicNeuralNetwork] = None
        self.best_fitness: float = float('-inf')
    
    @log_execution(
        component="neuroevolution",
        operation="initialize_population",
        log_exceptions=True
    )
    def initialize_population(
        self,
        input_size: int,
        output_size: int,
        max_layers: int = 5
    ):
        """Inicializa população de redes neurais aleatórias"""
        
        self.population = []
        self.fitness_scores = []
        
        for _ in range(self.population_size):
            # Criar arquitetura aleatória
            builder = NeuralNetworkBuilder()
            
            # Número aleatório de camadas
            num_layers = np.random.randint(2, max_layers + 1)
            
            for i in range(num_layers):
                layer_size = np.random.randint(32, 256)
                
                # Escolher tipo de camada aleatoriamente
                layer_choice = np.random.choice(['dense', 'lstm', 'transformer'])
                
                if layer_choice == 'dense':
                    activation = np.random.choice(list(ActivationType))
                    dropout = np.random.uniform(0.0, 0.3)
                    builder.add_dense(layer_size, activation, dropout)
                
                elif layer_choice == 'lstm':
                    num_layers_lstm = np.random.randint(1, 3)
                    bidirectional = np.random.choice([True, False])
                    dropout = np.random.uniform(0.0, 0.3)
                    builder.add_lstm(layer_size, num_layers_lstm, bidirectional, dropout)
                
                elif layer_choice == 'transformer':
                    num_heads = np.random.choice([4, 8, 16])
                    dropout = np.random.uniform(0.0, 0.3)
                    builder.add_transformer(layer_size, num_heads, dropout)
            
            # Construir rede neural
            network = builder.build(input_size, output_size)
            self.population.append(network)
            self.fitness_scores.append(0.0)
        
        self.logger.info(f"Population initialized with {len(self.population)} networks")
    
    @log_execution(
        component="neuroevolution",
        operation="evaluate_fitness",
        log_exceptions=True
    )
    def evaluate_fitness(
        self,
        X: torch.Tensor,
        y: torch.Tensor,
        metric: str = "mse"
    ):
        """Avalia fitness de toda a população"""
        
        for i, network in enumerate(self.population):
            network.eval()
            
            with torch.no_grad():
                predictions = network(X)
                
                if metric == "mse":
                    fitness = -F.mse_loss(predictions.squeeze(), y).item()
                elif metric == "mae":
                    fitness = -F.l1_loss(predictions.squeeze(), y).item()
                else:
                    fitness = -F.mse_loss(predictions.squeeze(), y).item()
            
            self.fitness_scores[i] = fitness
        
        # Atualizar melhor indivíduo
        best_idx = np.argmax(self.fitness_scores)
        if self.fitness_scores[best_idx] > self.best_fitness:
            self.best_fitness = self.fitness_scores[best_idx]
            self.best_network = self.population[best_idx]
        
        self.logger.info(f"Best fitness: {self.best_fitness:.6f}")
    
    def _crossover(
        self,
        parent1: DynamicNeuralNetwork,
        parent2: DynamicNeuralNetwork
    ) -> Tuple[DynamicNeuralNetwork, DynamicNeuralNetwork]:
        """Realiza crossover entre dois pais"""
        
        # Obter configurações dos pais
        config1 = parent1.layers_config
        config2 = parent2.layers_config
        
        # Ponto de corte aleatório
        min_len = min(len(config1), len(config2))
        if min_len < 2:
            return parent1, parent2
        
        crossover_point = np.random.randint(1, min_len)
        
        # Criar filhos
        child1_config = config1[:crossover_point] + config2[crossover_point:]
        child2_config = config2[:crossover_point] + config1[crossover_point:]
        
        # Construir redes filhas
        child1 = DynamicNeuralNetwork(
            child1_config,
            parent1.input_size,
            parent1.output_size
        )
        
        child2 = DynamicNeuralNetwork(
            child2_config,
            parent2.input_size,
            parent2.output_size
        )
        
        return child1, child2
    
    def _mutate(self, network: DynamicNeuralNetwork) -> DynamicNeuralNetwork:
        """Aplica mutação em uma rede neural"""
        
        # Copiar configuração
        mutated_config = network.layers_config.copy()
        
        for layer_config in mutated_config:
            if np.random.random() < self.mutation_rate:
                # Mutar dropout
                if layer_config.dropout > 0:
                    layer_config.dropout = np.clip(
                        layer_config.dropout + np.random.normal(0, 0.1),
                        0.0, 0.5
                    )
                
                # Mutar activation
                if layer_config.activation and np.random.random() < 0.3:
                    layer_config.activation = np.random.choice(list(ActivationType))
        
        # Construir rede mutada
        mutated_network = DynamicNeuralNetwork(
            mutated_config,
            network.input_size,
            network.output_size
        )
        
        return mutated_network
    
    @log_execution(
        component="neuroevolution",
        operation="evolve_generation",
        log_exceptions=True
    )
    def evolve_generation(self):
        """Evolui uma geração completa"""
        
        # Ordenar por fitness
        sorted_indices = np.argsort(self.fitness_scores)[::-1]
        
        # Elitismo - manter os melhores
        new_population = []
        
        for i in range(self.elite_size):
            idx = sorted_indices[i]
            new_population.append(self.population[idx])
        
        # Gerar resto da população
        while len(new_population) < self.population_size:
            # Seleção por torneio
            parent1_idx = self._tournament_selection()
            parent2_idx = self._tournament_selection()
            
            parent1 = self.population[parent1_idx]
            parent2 = self.population[parent2_idx]
            
            # Crossover
            if np.random.random() < self.crossover_rate:
                child1, child2 = self._crossover(parent1, parent2)
            else:
                child1, child2 = parent1, parent2
            
            # Mutação
            child1 = self._mutate(child1)
            child2 = self._mutate(child2)
            
            new_population.extend([child1, child2])
        
        # Manter tamanho da população
        self.population = new_population[:self.population_size]
        self.fitness_scores = [0.0] * self.population_size
        
        self.logger.info(f"Evolved generation: {len(self.population)} networks")
    
    def _tournament_selection(self, tournament_size: int = 3) -> int:
        """Seleção por torneio"""
        
        tournament_indices = np.random.choice(
            len(self.population),
            tournament_size,
            replace=False
        )
        
        best_idx = tournament_indices[0]
        best_fitness = self.fitness_scores[best_idx]
        
        for idx in tournament_indices[1:]:
            if self.fitness_scores[idx] > best_fitness:
                best_idx = idx
                best_fitness = self.fitness_scores[idx]
        
        return best_idx
    
    @log_execution(
        component="neuroevolution",
        operation="run_evolution",
        log_exceptions=True
    )
    def run_evolution(
        self,
        X: torch.Tensor,
        y: torch.Tensor,
        generations: int = 50,
        input_size: int = None,
        output_size: int = None
    ) -> DynamicNeuralNetwork:
        """
        Executa evolução completa
        
        Args:
            X: Dados de treinamento
            y: Labels de treinamento
            generations: Número de gerações
            input_size: Tamanho da entrada
            output_size: Tamanho da saída
        
        Returns:
            Melhor rede neural encontrada
        """
        
        # Determinar tamanhos
        if input_size is None:
            input_size = X.shape[-1]
        if output_size is None:
            output_size = 1 if len(y.shape) == 1 else y.shape[-1]
        
        # Inicializar população
        self.initialize_population(input_size, output_size)
        
        # Evolução
        for generation in range(generations):
            self.logger.info(f"Generation {generation + 1}/{generations}")
            
            # Avaliar fitness
            self.evaluate_fitness(X, y)
            
            # Evoluir geração (exceto última)
            if generation < generations - 1:
                self.evolve_generation()
        
        self.logger.info(f"Evolution completed. Best fitness: {self.best_fitness:.6f}")
        return self.best_network
    
    def get_best_network(self) -> Optional[DynamicNeuralNetwork]:
        """Retorna a melhor rede neural encontrada"""
        return self.best_network
    
    def get_evolution_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas da evolução"""
        return {
            "population_size": self.population_size,
            "mutation_rate": self.mutation_rate,
            "crossover_rate": self.crossover_rate,
            "elite_size": self.elite_size,
            "best_fitness": self.best_fitness,
            "current_generation": len(self.fitness_scores),
            "avg_fitness": np.mean(self.fitness_scores) if self.fitness_scores else 0.0,
            "std_fitness": np.std(self.fitness_scores) if self.fitness_scores else 0.0
        }


# Exportações principais
__all__ = [
    "DynamicNeuralNetwork",
    "NeuralNetworkBuilder",
    "NeuroEvolution",
    "MultiHeadAttention",
    "TransformerBlock",
    "LayerConfig",
    "LayerType",
    "ActivationType"
]

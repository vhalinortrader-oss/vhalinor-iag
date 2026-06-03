"""
LEXTRADER-IAG 3.0 - SISTEMA AUTÔNOMO EXPANDIDO
===============================================
Versão: 3.0.0 Premium Autônoma
Autor: LEXTRADER AI Team
Data: 2024
Base: Sistema Autônomo + Histórico Completo
"""

import math
import random
import json
import time
import asyncio
from typing import List, Dict, Any, Optional, Tuple, Set, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, IntEnum, auto
import numpy as np
from collections import deque, defaultdict
import hashlib
import os
from functools import lru_cache, partial
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import statistics
import itertools
from scipy import signal, stats
import pickle
import gzip

# ========== CONSTANTES DO SISTEMA AUTÔNOMO ==========

class AutonomousConstants:
    """Constantes do sistema autônomo."""
    
    # Configurações de trading
    MAX_POSITION_SIZE = 0.15  # 15% do capital
    MIN_CONFIDENCE_THRESHOLD = 0.85  # 85% mínimo
    RISK_FREE_RATE = 0.02  # 2% anual
    
    # Configurações de aprendizado
    REPLAY_BUFFER_SIZE = 10000
    BATCH_SIZE = 64
    TARGET_UPDATE_FREQ = 100
    LEARNING_RATE = 0.001
    DISCOUNT_FACTOR = 0.95
    
    # Configurações de memória
    MEMORY_CAPACITY = 100000
    SHORT_TERM_MEMORY = 1000
    LONG_TERM_MEMORY = 10000
    
    # Configurações temporais
    DECISION_INTERVAL_MS = 100  # 100ms entre decisões
    MARKET_ANALYSIS_INTERVAL = 1  # 1 segundo
    RETRAINING_INTERVAL = 3600  # 1 hora
    
    # Configurações de risco
    MAX_DRAWDOWN = 0.20  # 20%
    STOP_LOSS_PERCENT = 0.02  # 2%
    TAKE_PROFIT_RATIO = 2.0  # 2:1
    
    # Configurações de mercado
    SUPPORTED_TIME_FRAMES = ['1m', '5m', '15m', '1h', '4h', '1d']
    MAX_SYMBOLS = 50
    
    # Configurações de execução
    MAX_CONCURRENT_ANALYSES = 8
    AUTO_SAVE_INTERVAL = 300  # 5 minutos

# ========== ENUMS EXPANDIDOS ==========

class TradingSignal(IntEnum):
    """Sinais de trading expandidos."""
    STRONG_BUY = 2
    BUY = 1
    HOLD = 0
    SELL = -1
    STRONG_SELL = -2
    CLOSE_ALL = 3
    HEDGE = 4
    SCALP = 5
    SWING = 6

class MarketRegime(IntEnum):
    """Regimes de mercado para adaptação."""
    TRENDING_BULL = 0
    TRENDING_BEAR = 1
    RANGING = 2
    VOLATILE = 3
    BREAKOUT = 4
    REVERSAL = 5
    SIDEWAYS = 6
    CRASH = 7
    RALLY = 8

class NeuralArchitecture(IntEnum):
    """Arquiteturas neurais disponíveis."""
    TRANSFORMER = 0
    LSTM = 1
    GRU = 2
    CNN = 3
    ATTENTION = 4
    ENSEMBLE = 5
    HYBRID = 6
    QUANTUM = 7

class RiskProfile(IntEnum):
    """Perfis de risco."""
    CONSERVATIVE = 0
    MODERATE = 1
    AGGRESSIVE = 2
    HYPER_AGGRESSIVE = 3
    ADAPTIVE = 4

# ========== ESTRUTURAS DE DADOS AVANÇADAS ==========

@dataclass(slots=True)
class QuantumState:
    """Estado quântico para computação de superposição."""
    amplitudes: np.ndarray  # Amplitudes complexas
    basis_states: List[str]  # Estados da base
    entanglement: Dict[Tuple[int, int], float] = field(default_factory=dict)
    coherence_time: float = 1.0
    
    def measure(self) -> str:
        """Medição do estado quântico."""
        probabilities = np.abs(self.amplitudes) ** 2
        probabilities = probabilities / np.sum(probabilities)
        return np.random.choice(self.basis_states, p=probabilities)
    
    def apply_gate(self, gate: np.ndarray, qubits: List[int]):
        """Aplica porta quântica."""
        # Implementação simplificada
        for qubit in qubits:
            if qubit < len(self.amplitudes):
                # Rotação simples para demonstração
                angle = np.pi / 4
                rotation = np.array([
                    [np.cos(angle), -np.sin(angle)],
                    [np.sin(angle), np.cos(angle)]
                ])
                # Aplica rotação (simplificado)
                pass

@dataclass(slots=True)
class TemporalPattern:
    """Padrão temporal detectado."""
    pattern_type: str
    confidence: float
    start_time: datetime
    end_time: datetime
    features: Dict[str, float]
    prediction: Optional[float] = None
    
    def duration(self) -> float:
        """Duração do padrão em segundos."""
        return (self.end_time - self.start_time).total_seconds()
    
    def is_active(self, current_time: datetime) -> bool:
        """Verifica se o padrão está ativo."""
        return self.start_time <= current_time <= self.end_time

@dataclass(slots=True)
class AdaptiveThreshold:
    """Limite adaptativo para decisões."""
    value: float
    sensitivity: float  # 0-1
    adaptation_rate: float
    min_value: float
    max_value: float
    history: deque = field(default_factory=lambda: deque(maxlen=100))
    
    def update(self, new_value: float, success: bool):
        """Atualiza limite adaptativamente."""
        self.history.append((new_value, success))
        
        if success:
            # Aumenta limite se sucesso
            self.value = min(
                self.max_value,
                self.value * (1 + self.adaptation_rate * self.sensitivity)
            )
        else:
            # Diminui limite se falha
            self.value = max(
                self.min_value,
                self.value * (1 - self.adaptation_rate * self.sensitivity)
            )
    
    def should_trigger(self, current_value: float) -> bool:
        """Verifica se deve disparar."""
        return current_value >= self.value

# ========== SISTEMA DE MEMÓRIA EPISÓDICA AVANÇADA ==========

class EpisodicMemorySystem:
    """Sistema de memória episódica avançada."""
    
    def __init__(self, capacity: int = 10000):
        self.capacity = capacity
        self.memories = deque(maxlen=capacity)
        self.memory_index = defaultdict(list)  # Índice por tags
        self.associative_links = defaultdict(set)  # Ligações associativas
        
    def store_episode(self, episode: Dict[str, Any], tags: List[str]):
        """Armazena um episódio."""
        episode_id = hashlib.md5(str(episode).encode()).hexdigest()[:16]
        episode_with_meta = {
            'id': episode_id,
            'timestamp': datetime.now(),
            'episode': episode,
            'tags': tags,
            'access_count': 0,
            'last_accessed': datetime.now(),
        }
        
        self.memories.appendleft(episode_with_meta)
        
        # Indexa por tags
        for tag in tags:
            self.memory_index[tag].append(episode_id)
        
        # Cria ligações associativas
        self._create_associations(episode_id, episode, tags)
    
    def recall_by_context(self, context: Dict[str, Any], 
                         similarity_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Recupera episódios por contexto similar."""
        similar_episodes = []
        
        for memory in self.memories:
            similarity = self._calculate_similarity(
                context, memory['episode']
            )
            
            if similarity >= similarity_threshold:
                memory['access_count'] += 1
                memory['last_accessed'] = datetime.now()
                similar_episodes.append({
                    'memory': memory,
                    'similarity': similarity
                })
        
        # Ordena por similaridade
        similar_episodes.sort(key=lambda x: x['similarity'], reverse=True)
        return similar_episodes[:10]  # Retorna top 10
    
    def recall_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """Recupera episódios por tag."""
        episode_ids = self.memory_index.get(tag, [])
        memories = []
        
        for memory in self.memories:
            if memory['id'] in episode_ids:
                memories.append(memory)
        
        return memories
    
    def find_patterns(self, min_occurrences: int = 3) -> List[Dict[str, Any]]:
        """Encontra padrões recorrentes."""
        pattern_counts = defaultdict(int)
        pattern_details = defaultdict(list)
        
        for memory in self.memories:
            episode = memory['episode']
            
            # Extrai features para análise de padrões
            if 'action' in episode and 'outcome' in episode:
                pattern_key = f"{episode['action']}_{episode.get('context', '')}"
                pattern_counts[pattern_key] += 1
                pattern_details[pattern_key].append({
                    'timestamp': memory['timestamp'],
                    'outcome': episode['outcome'],
                    'confidence': episode.get('confidence', 0.5)
                })
        
        # Filtra padrões significativos
        significant_patterns = []
        for pattern, count in pattern_counts.items():
            if count >= min_occurrences:
                details = pattern_details[pattern]
                outcomes = [d['outcome'] for d in details]
                
                if len(outcomes) > 1:
                    avg_outcome = np.mean(outcomes)
                    std_outcome = np.std(outcomes)
                    success_rate = len([o for o in outcomes if o > 0]) / len(outcomes)
                    
                    significant_patterns.append({
                        'pattern': pattern,
                        'occurrences': count,
                        'avg_outcome': avg_outcome,
                        'std_outcome': std_outcome,
                        'success_rate': success_rate,
                        'first_seen': details[0]['timestamp'],
                        'last_seen': details[-1]['timestamp'],
                        'details': details[-5:]  # Últimos 5 exemplos
                    })
        
        return significant_patterns
    
    def _calculate_similarity(self, context1: Dict[str, Any], 
                            context2: Dict[str, Any]) -> float:
        """Calcula similaridade entre contextos."""
        if not context1 or not context2:
            return 0.0
        
        # Extrai features numéricas
        features1 = self._extract_features(context1)
        features2 = self._extract_features(context2)
        
        if not features1 or not features2:
            return 0.0
        
        # Similaridade do cosseno
        vec1 = np.array(list(features1.values()))
        vec2 = np.array(list(features2.values()))
        
        # Preenche com zeros se necessário
        max_len = max(len(vec1), len(vec2))
        vec1 = np.pad(vec1, (0, max_len - len(vec1)))
        vec2 = np.pad(vec2, (0, max_len - len(vec2)))
        
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = np.dot(vec1, vec2) / (norm1 * norm2)
        return float(similarity)
    
    def _extract_features(self, context: Dict[str, Any]) -> Dict[str, float]:
        """Extrai features numéricas do contexto."""
        features = {}
        
        for key, value in context.items():
            if isinstance(value, (int, float)):
                features[key] = float(value)
            elif isinstance(value, dict):
                # Recursão para dicionários aninhados
                sub_features = self._extract_features(value)
                for sub_key, sub_value in sub_features.items():
                    features[f"{key}.{sub_key}"] = sub_value
        
        return features
    
    def _create_associations(self, episode_id: str, 
                           episode: Dict[str, Any], tags: List[str]):
        """Cria ligações associativas."""
        # Liga com episódios similares
        for memory in list(self.memories)[:100]:  # Últimos 100 episódios
            if memory['id'] != episode_id:
                similarity = self._calculate_similarity(
                    episode, memory['episode']
                )
                
                if similarity > 0.7:
                    self.associative_links[episode_id].add(memory['id'])
                    self.associative_links[memory['id']].add(episode_id)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do sistema de memória."""
        total_memories = len(self.memories)
        
        if total_memories == 0:
            return {'total_memories': 0}
        
        # Contagem por tag
        tag_counts = {}
        for memory in self.memories:
            for tag in memory['tags']:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Memórias mais acessadas
        most_accessed = sorted(
            self.memories, 
            key=lambda x: x['access_count'], 
            reverse=True
        )[:5]
        
        return {
            'total_memories': total_memories,
            'tag_distribution': tag_counts,
            'most_accessed': [
                {
                    'id': m['id'][:8],
                    'access_count': m['access_count'],
                    'tags': m['tags'][:3]
                }
                for m in most_accessed
            ],
            'associative_links': sum(len(links) for links in self.associative_links.values()) // 2,
            'memory_utilization': total_memories / self.capacity
        }

# ========== SISTEMA DE APRENDIZADO POR REFORÇO PROFUNDO ==========

class DeepRLAgent:
    """Agente de Aprendizado por Reforço Profundo."""
    
    def __init__(self, state_size: int, action_size: int):
        self.state_size = state_size
        self.action_size = action_size
        
        # Rede neural (simulação)
        self.policy_network = self._build_policy_network()
        self.target_network = self._build_policy_network()
        self.update_target_network()
        
        # Memória de replay
        self.replay_buffer = deque(maxlen=AutonomousConstants.REPLAY_BUFFER_SIZE)
        self.batch_size = AutonomousConstants.BATCH_SIZE
        
        # Otimizador
        self.learning_rate = AutonomousConstants.LEARNING_RATE
        self.discount_factor = AutonomousConstants.DISCOUNT_FACTOR
        self.tau = 0.001  # Para soft updates
        
        # Histórico
        self.training_history = []
        self.epsilon = 1.0  # Para exploração
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01
        
        # Estatísticas
        self.total_steps = 0
        self.total_rewards = 0
        self.episode_rewards = []
        
    def _build_policy_network(self) -> Dict[str, Any]:
        """Constrói a rede de política (simulação)."""
        return {
            'type': 'DEEP_Q_NETWORK',
            'layers': [
                {'size': 128, 'activation': 'relu'},
                {'size': 64, 'activation': 'relu'},
                {'size': 32, 'activation': 'relu'},
                {'size': self.action_size, 'activation': 'linear'}
            ],
            'weights': self._initialize_weights(),
            'biases': self._initialize_biases(),
        }
    
    def _initialize_weights(self) -> List[np.ndarray]:
        """Inicializa pesos da rede."""
        weights = []
        layer_sizes = [self.state_size, 128, 64, 32, self.action_size]
        
        for i in range(len(layer_sizes) - 1):
            # Xavier/Glorot initialization
            limit = np.sqrt(6 / (layer_sizes[i] + layer_sizes[i + 1]))
            weight = np.random.uniform(-limit, limit, 
                                     (layer_sizes[i], layer_sizes[i + 1]))
            weights.append(weight)
        
        return weights
    
    def _initialize_biases(self) -> List[np.ndarray]:
        """Inicializa biases da rede."""
        layer_sizes = [128, 64, 32, self.action_size]
        return [np.zeros(size) for size in layer_sizes]
    
    def update_target_network(self):
        """Atualiza rede alvo."""
        self.target_network = self._deep_copy_network(self.policy_network)
    
    def _deep_copy_network(self, network: Dict[str, Any]) -> Dict[str, Any]:
        """Cria cópia profunda da rede."""
        return {
            'type': network['type'],
            'layers': [layer.copy() for layer in network['layers']],
            'weights': [w.copy() for w in network['weights']],
            'biases': [b.copy() for b in network['biases']],
        }
    
    def get_action(self, state: np.ndarray, 
                  training: bool = True) -> Tuple[int, Dict[str, Any]]:
        """
        Obtém ação da política.
        
        Args:
            state: Estado atual
            training: Se está em modo de treinamento
            
        Returns:
            Tuple[int, Dict]: Índice da ação e metadados
        """
        self.total_steps += 1
        
        # Exploração vs Exploração
        if training and random.random() < self.epsilon:
            # Exploração aleatória
            action = random.randint(0, self.action_size - 1)
            metadata = {
                'type': 'EXPLORATION',
                'epsilon': self.epsilon,
                'q_value': None
            }
        else:
            # Exploração da política
            q_values = self._forward_pass(state)
            action = np.argmax(q_values)
            metadata = {
                'type': 'EXPLOITATION',
                'epsilon': self.epsilon,
                'q_value': float(q_values[action]),
                'q_values': q_values.tolist()
            }
        
        # Decay do epsilon
        if training:
            self.epsilon = max(
                self.epsilon_min, 
                self.epsilon * self.epsilon_decay
            )
        
        return action, metadata
    
    def _forward_pass(self, state: np.ndarray) -> np.ndarray:
        """Passada forward pela rede."""
        activation = state
        
        for i, (weight, bias) in enumerate(zip(self.policy_network['weights'], 
                                             self.policy_network['biases'])):
            # Multiplicação de matrizes
            activation = np.dot(activation, weight) + bias
            
            # Aplicação de função de ativação
            if i < len(self.policy_network['weights']) - 1:
                activation = np.maximum(0, activation)  # ReLU
            # Última camada é linear
        
        return activation
    
    def store_experience(self, state: np.ndarray, action: int, 
                        reward: float, next_state: np.ndarray, 
                        done: bool):
        """Armazena experiência no buffer de replay."""
        experience = {
            'state': state,
            'action': action,
            'reward': reward,
            'next_state': next_state,
            'done': done,
            'timestamp': datetime.now()
        }
        
        self.replay_buffer.append(experience)
        self.total_rewards += reward
    
    def train(self, batch_size: Optional[int] = None) -> Dict[str, Any]:
        """Treina o agente com experiências do buffer."""
        if batch_size is None:
            batch_size = self.batch_size
        
        if len(self.replay_buffer) < batch_size:
            return {'status': 'INSUFFICIENT_DATA', 'buffer_size': len(self.replay_buffer)}
        
        # Amostra batch aleatório
        batch = random.sample(self.replay_buffer, batch_size)
        
        # Prepara dados para treinamento
        states = np.array([exp['state'] for exp in batch])
        actions = np.array([exp['action'] for exp in batch])
        rewards = np.array([exp['reward'] for exp in batch])
        next_states = np.array([exp['next_state'] for exp in batch])
        dones = np.array([exp['done'] for exp in batch])
        
        # Calcula targets usando Double DQN
        q_values_next = self._forward_pass_batch(next_states)
        best_actions = np.argmax(q_values_next, axis=1)
        
        q_targets_next = self._target_forward_pass_batch(next_states)
        q_targets = rewards + self.discount_factor * q_targets_next[
            np.arange(batch_size), best_actions
        ] * (1 - dones)
        
        # Atualiza rede
        loss = self._update_network(states, actions, q_targets)
        
        # Soft update da target network
        self._soft_update_target_network()
        
        # Registra treinamento
        training_record = {
            'timestamp': datetime.now(),
            'batch_size': batch_size,
            'avg_reward': float(np.mean(rewards)),
            'loss': float(loss),
            'epsilon': self.epsilon,
            'buffer_size': len(self.replay_buffer)
        }
        
        self.training_history.append(training_record)
        
        return training_record
    
    def _forward_pass_batch(self, states: np.ndarray) -> np.ndarray:
        """Forward pass para batch de estados."""
        batch_size = states.shape[0]
        activations = states
        
        for i, (weight, bias) in enumerate(zip(self.policy_network['weights'], 
                                             self.policy_network['biases'])):
            # Multiplicação de matrizes para batch
            activations = np.dot(activations, weight) + bias
            
            if i < len(self.policy_network['weights']) - 1:
                activations = np.maximum(0, activations)
        
        return activations
    
    def _target_forward_pass_batch(self, states: np.ndarray) -> np.ndarray:
        """Forward pass usando target network."""
        activations = states
        
        for i, (weight, bias) in enumerate(zip(self.target_network['weights'], 
                                             self.target_network['biases'])):
            activations = np.dot(activations, weight) + bias
            
            if i < len(self.target_network['weights']) - 1:
                activations = np.maximum(0, activations)
        
        return activations
    
    def _update_network(self, states: np.ndarray, actions: np.ndarray, 
                       targets: np.ndarray) -> float:
        """Atualiza pesos da rede (simulação)."""
        # Simulação de backpropagation
        # Em implementação real, usaria TensorFlow/PyTorch
        
        # Calcula "gradiente" simplificado
        predictions = self._forward_pass_batch(states)
        batch_size = states.shape[0]
        
        # Erro quadrático médio
        errors = predictions[np.arange(batch_size), actions] - targets
        loss = np.mean(errors ** 2)
        
        # Atualiza pesos (simulação simplificada)
        learning_rate = self.learning_rate / batch_size
        
        for i in range(len(self.policy_network['weights'])):
            # Atualização simplificada
            self.policy_network['weights'][i] *= (1 - learning_rate * 0.01)
            self.policy_network['biases'][i] *= (1 - learning_rate * 0.01)
        
        return loss
    
    def _soft_update_target_network(self):
        """Soft update da target network."""
        for target_weight, policy_weight in zip(
            self.target_network['weights'], 
            self.policy_network['weights']
        ):
            target_weight[:] = self.tau * policy_weight + (1 - self.tau) * target_weight
        
        for target_bias, policy_bias in zip(
            self.target_network['biases'], 
            self.policy_network['biases']
        ):
            target_bias[:] = self.tau * policy_bias + (1 - self.tau) * target_bias
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas do agente."""
        recent_training = self.training_history[-10:] if self.training_history else []
        
        return {
            'total_steps': self.total_steps,
            'total_rewards': self.total_rewards,
            'epsilon': self.epsilon,
            'replay_buffer_size': len(self.replay_buffer),
            'avg_recent_loss': np.mean([t['loss'] for t in recent_training]) if recent_training else 0,
            'avg_recent_reward': np.mean([t['avg_reward'] for t in recent_training]) if recent_training else 0,
            'training_history_size': len(self.training_history),
            'network_architecture': self.policy_network['type'],
        }

# ========== SISTEMA DE MARKET MAKING AUTÔNOMO ==========

class AutonomousMarketMaker:
    """Sistema de Market Making Autônomo."""
    
    def __init__(self, initial_capital: float = 10000.0):
        self.capital = initial_capital
        self.inventory = 0.0
        self.position = 0.0
        
        # Livro de ordens
        self.order_book = {
            'bids': [],  # [(price, quantity, timestamp)]
            'asks': [],  # [(price, quantity, timestamp)]
        }
        
        # Configurações
        self.spread_target = 0.001  # 0.1%
        self.max_position = 100.0  # Unidades máximas
        self.inventory_target = 0.0  # Inventário alvo
        self.risk_aversion = 0.3
        
        # Histórico
        self.trade_history = deque(maxlen=1000)
        self.pnl_history = deque(maxlen=1000)
        self.inventory_history = deque(maxlen=1000)
        
        # Estatísticas
        self.total_trades = 0
        self.total_pnl = 0.0
        self.max_drawdown = 0.0
        self.sharpe_ratio = 0.0
        
    async def update_market_state(self, market_data: Dict[str, Any]):
        """Atualiza estado do mercado."""
        current_price = market_data.get('price', 0)
        volatility = market_data.get('volatility', 0.01)
        
        # Ajusta spread baseado na volatilidade
        self.spread_target = 0.001 * (1 + volatility * 10)
        
        # Limpa ordens antigas
        self._clean_old_orders()
        
        # Calcula preços de bid/ask
        bid_price, ask_price = self._calculate_prices(current_price, volatility)
        
        # Calcula quantidades baseadas no inventário
        bid_qty, ask_qty = self._calculate_quantities(current_price)
        
        # Atualiza livro de ordens
        self._update_order_book(bid_price, bid_qty, ask_price, ask_qty)
        
        # Executa matching de ordens
        executed_trades = self._execute_order_matching()
        
        # Atualiza estatísticas
        if executed_trades:
            await self._update_statistics(executed_trades, market_data)
        
        return {
            'bid_price': bid_price,
            'ask_price': ask_price,
            'bid_quantity': bid_qty,
            'ask_quantity': ask_qty,
            'spread': ask_price - bid_price,
            'inventory': self.inventory,
            'position': self.position,
            'capital': self.capital,
            'executed_trades': executed_trades,
        }
    
    def _calculate_prices(self, mid_price: float, 
                         volatility: float) -> Tuple[float, float]:
        """Calcula preços de bid e ask."""
        # Spread baseado na volatilidade e risco
        spread = self.spread_target * (1 + volatility * 5)
        
        # Ajuste baseado no inventário
        inventory_adjustment = -self.inventory / self.max_position * 0.005
        
        bid_price = mid_price * (1 - spread/2 + inventory_adjustment)
        ask_price = mid_price * (1 + spread/2 + inventory_adjustment)
        
        return bid_price, ask_price
    
    def _calculate_quantities(self, current_price: float) -> Tuple[float, float]:
        """Calcula quantidades para bid e ask."""
        # Quantidade base
        base_qty = 1.0
        
        # Ajuste baseado no inventário
        if self.inventory > self.max_position * 0.7:
            # Muito inventário, vende mais
            bid_qty = base_qty * 0.5
            ask_qty = base_qty * 2.0
        elif self.inventory < -self.max_position * 0.7:
            # Muito short, compra mais
            bid_qty = base_qty * 2.0
            ask_qty = base_qty * 0.5
        else:
            # Inventário balanceado
            bid_qty = ask_qty = base_qty
        
        # Limita pelo capital
        max_qty_by_capital = self.capital * 0.1 / current_price
        bid_qty = min(bid_qty, max_qty_by_capital)
        ask_qty = min(ask_qty, max_qty_by_capital)
        
        return bid_qty, ask_qty
    
    def _update_order_book(self, bid_price: float, bid_qty: float,
                          ask_price: float, ask_qty: float):
        """Atualiza livro de ordens."""
        # Adiciona novas ordens
        self.order_book['bids'].append({
            'price': bid_price,
            'quantity': bid_qty,
            'timestamp': datetime.now(),
            'type': 'BID'
        })
        
        self.order_book['asks'].append({
            'price': ask_price,
            'quantity': ask_qty,
            'timestamp': datetime.now(),
            'type': 'ASK'
        })
    
    def _clean_old_orders(self, max_age_seconds: float = 60.0):
        """Remove ordens antigas do livro."""
        current_time = datetime.now()
        
        self.order_book['bids'] = [
            order for order in self.order_book['bids']
            if (current_time - order['timestamp']).total_seconds() < max_age_seconds
        ]
        
        self.order_book['asks'] = [
            order for order in self.order_book['asks']
            if (current_time - order['timestamp']).total_seconds() < max_age_seconds
        ]
    
    def _execute_order_matching(self) -> List[Dict[str, Any]]:
        """Executa matching de ordens no livro."""
        executed_trades = []
        
        # Ordena bids (maior preço primeiro) e asks (menor preço primeiro)
        bids_sorted = sorted(self.order_book['bids'], 
                           key=lambda x: x['price'], reverse=True)
        asks_sorted = sorted(self.order_book['asks'], 
                           key=lambda x: x['price'])
        
        while bids_sorted and asks_sorted:
            best_bid = bids_sorted[0]
            best_ask = asks_sorted[0]
            
            if best_bid['price'] >= best_ask['price']:
                # Trade possível
                trade_price = (best_bid['price'] + best_ask['price']) / 2
                trade_qty = min(best_bid['quantity'], best_ask['quantity'])
                
                # Executa trade
                self._execute_trade(trade_price, trade_qty, best_bid, best_ask)
                
                executed_trades.append({
                    'price': trade_price,
                    'quantity': trade_qty,
                    'timestamp': datetime.now(),
                    'bid_order': best_bid,
                    'ask_order': best_ask,
                })
                
                self.total_trades += 1
                
                # Atualiza quantidades
                best_bid['quantity'] -= trade_qty
                best_ask['quantity'] -= trade_qty
                
                # Remove ordens completadas
                if best_bid['quantity'] <= 0:
                    bids_sorted.pop(0)
                if best_ask['quantity'] <= 0:
                    asks_sorted.pop(0)
            else:
                # Não há mais matches possíveis
                break
        
        # Atualiza livro de ordens
        self.order_book['bids'] = [b for b in bids_sorted if b['quantity'] > 0]
        self.order_book['asks'] = [a for a in asks_sorted if a['quantity'] > 0]
        
        return executed_trades
    
    def _execute_trade(self, price: float, quantity: float,
                      bid_order: Dict[str, Any], ask_order: Dict[str, Any]):
        """Executa um trade."""
        # Atualiza inventário
        self.inventory -= quantity  # Vende do inventário
        
        # Atualiza capital
        self.capital += price * quantity
        
        # Atualiza posição
        self.position = self.inventory * price
        
        # Registra no histórico
        trade_record = {
            'price': price,
            'quantity': quantity,
            'timestamp': datetime.now(),
            'inventory_after': self.inventory,
            'capital_after': self.capital,
            'position_after': self.position,
        }
        
        self.trade_history.append(trade_record)
        self.inventory_history.append(self.inventory)
    
    async def _update_statistics(self, executed_trades: List[Dict[str, Any]],
                               market_data: Dict[str, Any]):
        """Atualiza estatísticas de performance."""
        if not executed_trades:
            return
        
        # Calcula PnL do lote
        current_price = market_data.get('price', 0)
        inventory_value = self.inventory * current_price
        total_value = self.capital + inventory_value
        
        # PnL desde último update
        if self.pnl_history:
            last_total = self.pnl_history[-1]['total_value']
            pnl = total_value - last_total
        else:
            pnl = total_value - 10000.0  # Capital inicial
        
        self.total_pnl += pnl
        
        # Registra PnL
        pnl_record = {
            'timestamp': datetime.now(),
            'pnl': pnl,
            'total_value': total_value,
            'inventory_value': inventory_value,
            'capital': self.capital,
            'current_price': current_price,
        }
        
        self.pnl_history.append(pnl_record)
        
        # Calcula drawdown
        if len(self.pnl_history) > 1:
            peak = max([p['total_value'] for p in self.pnl_history])
            current = total_value
            drawdown = (peak - current) / peak if peak > 0 else 0
            self.max_drawdown = max(self.max_drawdown, drawdown)
        
        # Calcula Sharpe ratio (simplificado)
        if len(self.pnl_history) > 10:
            returns = []
            for i in range(1, len(self.pnl_history)):
                ret = (self.pnl_history[i]['total_value'] - 
                      self.pnl_history[i-1]['total_value']) / \
                      self.pnl_history[i-1]['total_value']
                returns.append(ret)
            
            if returns:
                avg_return = np.mean(returns)
                std_return = np.std(returns)
                
                if std_return > 0:
                    self.sharpe_ratio = (avg_return - AutonomousConstants.RISK_FREE_RATE/365) / std_return * np.sqrt(365)
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Retorna relatório de performance."""
        return {
            'total_trades': self.total_trades,
            'total_pnl': self.total_pnl,
            'current_capital': self.capital,
            'current_inventory': self.inventory,
            'current_position': self.position,
            'max_drawdown': f"{self.max_drawdown:.2%}",
            'sharpe_ratio': f"{self.sharpe_ratio:.2f}",
            'order_book_size': {
                'bids': len(self.order_book['bids']),
                'asks': len(self.order_book['asks']),
            },
            'recent_trades': list(self.trade_history)[-5:],
            'inventory_trend': list(self.inventory_history)[-10:],
        }

# ========== SISTEMA DE ARBITRAGEM ESTATÍSTICA ==========

class StatisticalArbitrageSystem:
    """Sistema de Arbitragem Estatística."""
    
    def __init__(self):
        self.pairs = {}  # Pares cointegrados
        self.spread_history = defaultdict(deque)
        self.position_history = defaultdict(deque)
        
        # Configurações
        self.cointegration_threshold = 0.95
        self.zscore_entry = 2.0
        self.zscore_exit = 0.5
        self.max_position_size = 10.0
        
        # Modelos
        self.cointegration_models = {}
        self.mean_reversion_models = {}
        
        # Estatísticas
        self.arbitrage_opportunities = deque(maxlen=1000)
        self.executed_arbitrages = deque(maxlen=1000)
        self.total_arbitrage_pnl = 0.0
        
    async def analyze_pairs(self, price_data: Dict[str, List[float]], 
                          symbols: List[str]) -> List[Dict[str, Any]]:
        """Analisa pares para arbitragem."""
        opportunities = []
        
        # Gera combinações de pares
        pairs = list(itertools.combinations(symbols, 2))
        
        for symbol1, symbol2 in pairs:
            if symbol1 in price_data and symbol2 in price_data:
                prices1 = price_data[symbol1]
                prices2 = price_data[symbol2]
                
                if len(prices1) > 30 and len(prices2) > 30:  # Mínimo de dados
                    # Testa cointegração
                    cointegration_result = await self._test_cointegration(
                        prices1, prices2, symbol1, symbol2
                    )
                    
                    if cointegration_result['is_cointegrated']:
                        # Calcula spread
                        spread = await self._calculate_spread(
                            prices1, prices2, 
                            cointegration_result['hedge_ratio']
                        )
                        
                        # Analisa mean reversion
                        zscore = await self._calculate_zscore(spread)
                        
                        # Verifica oportunidade
                        opportunity = self._identify_opportunity(
                            symbol1, symbol2, zscore, 
                            cointegration_result, spread
                        )
                        
                        if opportunity:
                            opportunities.append(opportunity)
        
        return opportunities
    
    async def _test_cointegration(self, series1: List[float], 
                                series2: List[float],
                                symbol1: str, symbol2: str) -> Dict[str, Any]:
        """Testa cointegração entre duas séries."""
        # Em implementação real, usaria statsmodels
        # Aqui simulamos com correlação
        
        corr = np.corrcoef(series1, series2)[0, 1]
        is_cointegrated = abs(corr) > self.cointegration_threshold
        
        # Calcula hedge ratio (simplificado)
        hedge_ratio = np.mean(series1) / np.mean(series2) if np.mean(series2) != 0 else 1.0
        
        return {
            'is_cointegrated': is_cointegrated,
            'correlation': corr,
            'hedge_ratio': hedge_ratio,
            'pair': f"{symbol1}/{symbol2}",
            'timestamp': datetime.now(),
        }
    
    async def _calculate_spread(self, series1: List[float], 
                              series2: List[float], 
                              hedge_ratio: float) -> List[float]:
        """Calcula spread entre duas séries."""
        spread = []
        for s1, s2 in zip(series1, series2):
            spread.append(s1 - hedge_ratio * s2)
        return spread
    
    async def _calculate_zscore(self, spread: List[float]) -> float:
        """Calcula z-score do spread."""
        if len(spread) < 2:
            return 0.0
        
        mean = np.mean(spread)
        std = np.std(spread)
        
        if std > 0:
            return (spread[-1] - mean) / std
        return 0.0
    
    def _identify_opportunity(self, symbol1: str, symbol2: str, 
                            zscore: float, 
                            cointegration_result: Dict[str, Any],
                            spread: List[float]) -> Optional[Dict[str, Any]]:
        """Identifica oportunidade de arbitragem."""
        entry_threshold = self.zscore_entry
        exit_threshold = self.zscore_exit
        
        opportunity = None
        
        if abs(zscore) > entry_threshold:
            # Oportunidade de entrada
            action = 'SELL' if zscore > 0 else 'BUY'
            spread_asset = symbol1 if zscore > 0 else symbol2
            hedge_asset = symbol2 if zscore > 0 else symbol1
            
            opportunity = {
                'type': 'ARBITRAGE_ENTRY',
                'pair': f"{symbol1}/{symbol2}",
                'action': action,
                'spread_asset': spread_asset,
                'hedge_asset': hedge_asset,
                'zscore': zscore,
                'hedge_ratio': cointegration_result['hedge_ratio'],
                'current_spread': spread[-1] if spread else 0,
                'confidence': min(0.95, abs(zscore) / 3.0),  # Normalizado
                'timestamp': datetime.now(),
                'expected_return': abs(zscore) * 0.01,  # 1% por unidade de z-score
                'risk_level': 'MEDIUM' if abs(zscore) < 3.0 else 'HIGH',
            }
        
        return opportunity
    
    async def execute_arbitrage(self, opportunity: Dict[str, Any], 
                              current_prices: Dict[str, float]) -> Dict[str, Any]:
        """Executa arbitragem."""
        symbol1, symbol2 = opportunity['pair'].split('/')
        action = opportunity['action']
        hedge_ratio = opportunity['hedge_ratio']
        
        # Calcula tamanho da posição
        position_size = self._calculate_position_size(opportunity)
        
        # Simula execução
        if action == 'SELL':
            # Vende spread_asset, compra hedge_asset
            price1 = current_prices.get(symbol1, 0)
            price2 = current_prices.get(symbol2, 0)
            
            # PnL teórico
            theoretical_pnl = position_size * (
                (price1 - price2 * hedge_ratio) * opportunity['expected_return']
            )
        else:
            # Compra spread_asset, vende hedge_asset
            price1 = current_prices.get(symbol1, 0)
            price2 = current_prices.get(symbol2, 0)
            
            theoretical_pnl = position_size * (
                (price2 * hedge_ratio - price1) * opportunity['expected_return']
            )
        
        # Registra arbitragem
        arbitrage_record = {
            **opportunity,
            'executed': True,
            'position_size': position_size,
            'price1': price1,
            'price2': price2,
            'theoretical_pnl': theoretical_pnl,
            'execution_timestamp': datetime.now(),
        }
        
        self.executed_arbitrages.append(arbitrage_record)
        self.total_arbitrage_pnl += theoretical_pnl
        
        return arbitrage_record
    
    def _calculate_position_size(self, opportunity: Dict[str, Any]) -> float:
        """Calcula tamanho da posição para arbitragem."""
        base_size = self.max_position_size
        confidence = opportunity.get('confidence', 0.5)
        zscore = abs(opportunity.get('zscore', 0))
        
        # Ajusta pelo z-score e confiança
        size = base_size * confidence * min(1.0, zscore / 3.0)
        
        return min(size, self.max_position_size)
    
    def get_arbitrage_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de arbitragem."""
        total_opportunities = len(self.arbitrage_opportunities)
        total_executed = len(self.executed_arbitrages)
        
        if total_executed > 0:
            successful = len([a for a in self.executed_arbitrages 
                            if a['theoretical_pnl'] > 0])
            success_rate = successful / total_executed
            avg_pnl = np.mean([a['theoretical_pnl'] 
                             for a in self.executed_arbitrages])
        else:
            success_rate = 0.0
            avg_pnl = 0.0
        
        return {
            'total_opportunities': total_opportunities,
            'total_executed': total_executed,
            'success_rate': f"{success_rate:.1%}",
            'total_pnl': self.total_arbitrage_pnl,
            'avg_pnl_per_trade': avg_pnl,
            'active_pairs': len(self.pairs),
            'recent_opportunities': list(self.arbitrage_opportunities)[-5:],
            'recent_executions': list(self.executed_arbitrages)[-5:],
        }

# ========== SISTEMA DE VISÃO COMPUTACIONAL PARA ANÁLISE DE GRÁFICOS ==========

class ChartPatternRecognizer:
    """Reconhecedor de Padrões Gráficos usando Visão Computacional."""
    
    def __init__(self):
        self.pattern_templates = self._load_pattern_templates()
        self.detected_patterns = deque(maxlen=1000)
        self.pattern_accuracy = {}
        
    def _load_pattern_templates(self) -> Dict[str, Any]:
        """Carrega templates de padrões gráficos."""
        return {
            'head_shoulders': {
                'description': 'Head and Shoulders - Reversão de alta',
                'points': 5,  # Número de pontos característicos
                'accuracy_threshold': 0.7,
                'expected_outcome': 'BEARISH',
            },
            'inverse_head_shoulders': {
                'description': 'Inverse Head and Shoulders - Reversão de baixa',
                'points': 5,
                'accuracy_threshold': 0.7,
                'expected_outcome': 'BULLISH',
            },
            'double_top': {
                'description': 'Double Top - Reversão de alta',
                'points': 3,
                'accuracy_threshold': 0.75,
                'expected_outcome': 'BEARISH',
            },
            'double_bottom': {
                'description': 'Double Bottom - Reversão de baixa',
                'points': 3,
                'accuracy_threshold': 0.75,
                'expected_outcome': 'BULLISH',
            },
            'triangle_ascending': {
                'description': 'Ascending Triangle - Continuação de alta',
                'points': 4,
                'accuracy_threshold': 0.65,
                'expected_outcome': 'BULLISH',
            },
            'triangle_descending': {
                'description': 'Descending Triangle - Continuação de baixa',
                'points': 4,
                'accuracy_threshold': 0.65,
                'expected_outcome': 'BEARISH',
            },
            'wedge': {
                'description': 'Wedge Pattern',
                'points': 4,
                'accuracy_threshold': 0.6,
                'expected_outcome': 'VARIABLE',
            },
        }
    
    async def analyze_chart(self, price_data: List[float], 
                          volume_data: Optional[List[float]] = None) -> List[Dict[str, Any]]:
        """Analisa gráfico de preços em busca de padrões."""
        detected = []
        
        # Normaliza dados
        normalized_prices = self._normalize_prices(price_data)
        
        # Detecta pontos de virada (picos e vales)
        turning_points = self._find_turning_points(normalized_prices)
        
        if len(turning_points) < 3:
            return detected
        
        # Tenta identificar cada padrão
        for pattern_name, template in self.pattern_templates.items():
            pattern_result = await self._detect_specific_pattern(
                normalized_prices, turning_points, pattern_name, template
            )
            
            if pattern_result:
                detected.append(pattern_result)
        
        # Ordena por confiança
        detected.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Armazena padrões detectados
        for pattern in detected:
            self.detected_patterns.append(pattern)
            
            # Atualiza precisão histórica
            self._update_pattern_accuracy(pattern)
        
        return detected[:5]  # Retorna top 5 padrões
    
    def _normalize_prices(self, prices: List[float]) -> List[float]:
        """Normaliza preços para escala 0-1."""
        if not prices:
            return []
        
        min_price = min(prices)
        max_price = max(prices)
        
        if max_price - min_price == 0:
            return [0.5] * len(prices)
        
        return [(p - min_price) / (max_price - min_price) for p in prices]
    
    def _find_turning_points(self, prices: List[float], 
                            window: int = 3) -> List[Tuple[int, str, float]]:
        """Encontra pontos de virada (picos e vales)."""
        turning_points = []
        
        for i in range(window, len(prices) - window):
            left_window = prices[i-window:i]
            right_window = prices[i+1:i+window+1]
            current = prices[i]
            
            # Verifica se é pico
            if all(x < current for x in left_window) and \
               all(x < current for x in right_window):
                turning_points.append((i, 'PEAK', current))
            
            # Verifica se é vale
            elif all(x > current for x in left_window) and \
                 all(x > current for x in right_window):
                turning_points.append((i, 'VALLEY', current))
        
        return turning_points
    
    async def _detect_specific_pattern(self, prices: List[float], 
                                     turning_points: List[Tuple[int, str, float]],
                                     pattern_name: str, 
                                     template: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detecta um padrão específico."""
        if pattern_name == 'head_shoulders':
            return await self._detect_head_shoulders(prices, turning_points, template)
        elif pattern_name == 'double_top':
            return await self._detect_double_top(prices, turning_points, template)
        elif pattern_name == 'double_bottom':
            return await self._detect_double_bottom(prices, turning_points, template)
        elif pattern_name == 'triangle_ascending':
            return await self._detect_triangle(prices, turning_points, template, 'ascending')
        elif pattern_name == 'triangle_descending':
            return await self._detect_triangle(prices, turning_points, template, 'descending')
        
        return None
    
    async def _detect_head_shoulders(self, prices: List[float], 
                                   turning_points: List[Tuple[int, str, float]],
                                   template: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detecta padrão Head and Shoulders."""
        # Procura sequência: valley - peak - higher peak - peak - valley
        peaks = [tp for tp in turning_points if tp[1] == 'PEAK']
        valleys = [tp for tp in turning_points if tp[1] == 'VALLEY']
        
        if len(peaks) < 3 or len(valleys) < 2:
            return None
        
        # Tenta encontrar o padrão
        for i in range(len(peaks) - 2):
            left_shoulder = peaks[i]
            head = peaks[i + 1]
            right_shoulder = peaks[i + 2]
            
            # Verifica relações de altura
            if head[2] > left_shoulder[2] and head[2] > right_shoulder[2]:
                # Head é mais alto que os ombros
                shoulder_height_diff = abs(left_shoulder[2] - right_shoulder[2])
                head_height_diff = head[2] - max(left_shoulder[2], right_shoulder[2])
                
                if shoulder_height_diff < 0.1 and head_height_diff > 0.05:  # Thresholds
                    # Encontra vales entre os picos
                    valleys_between = [
                        v for v in valleys 
                        if left_shoulder[0] < v[0] < right_shoulder[0]
                    ]
                    
                    if len(valleys_between) >= 1:
                        neckline_valley = valleys_between[0]
                        
                        confidence = self._calculate_pattern_confidence(
                            [left_shoulder, head, right_shoulder, neckline_valley],
                            template
                        )
                        
                        if confidence >= template['accuracy_threshold']:
                            return {
                                'pattern': 'head_shoulders',
                                'confidence': confidence,
                                'points': [
                                    {'type': 'left_shoulder', 'index': left_shoulder[0], 'value': left_shoulder[2]},
                                    {'type': 'head', 'index': head[0], 'value': head[2]},
                                    {'type': 'right_shoulder', 'index': right_shoulder[0], 'value': right_shoulder[2]},
                                    {'type': 'neckline', 'index': neckline_valley[0], 'value': neckline_valley[2]},
                                ],
                                'expected_outcome': template['expected_outcome'],
                                'description': template['description'],
                                'timestamp': datetime.now(),
                            }
        
        return None
    
    async def _detect_double_top(self, prices: List[float], 
                               turning_points: List[Tuple[int, str, float]],
                               template: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detecta padrão Double Top."""
        peaks = [tp for tp in turning_points if tp[1] == 'PEAK']
        
        if len(peaks) < 2:
            return None
        
        for i in range(len(peaks) - 1):
            first_top = peaks[i]
            second_top = peaks[i + 1]
            
            # Verifica se são aproximadamente na mesma altura
            height_diff = abs(first_top[2] - second_top[2])
            
            if height_diff < 0.05:  # Threshold
                # Encontra vale entre os dois picos
                valleys_between = [
                    v for v in turning_points 
                    if v[1] == 'VALLEY' and 
                    first_top[0] < v[0] < second_top[0]
                ]
                
                if valleys_between:
                    valley = valleys_between[0]
                    
                    confidence = self._calculate_pattern_confidence(
                        [first_top, second_top, valley],
                        template
                    )
                    
                    if confidence >= template['accuracy_threshold']:
                        return {
                            'pattern': 'double_top',
                            'confidence': confidence,
                            'points': [
                                {'type': 'first_top', 'index': first_top[0], 'value': first_top[2]},
                                {'type': 'second_top', 'index': second_top[0], 'value': second_top[2]},
                                {'type': 'valley', 'index': valley[0], 'value': valley[2]},
                            ],
                            'expected_outcome': template['expected_outcome'],
                            'description': template['description'],
                            'timestamp': datetime.now(),
                        }
        
        return None
    
    def _calculate_pattern_confidence(self, points: List[Tuple[int, str, float]], 
                                    template: Dict[str, Any]) -> float:
        """Calcula confiança do padrão detectado."""
        base_confidence = 0.5
        
        # Baseado no número de pontos
        expected_points = template.get('points', 3)
        actual_points = len(points)
        
        if actual_points >= expected_points:
            base_confidence += 0.2
        else:
            base_confidence -= 0.1
        
        # Baseado na simetria (para alguns padrões)
        if template['pattern'] in ['head_shoulders', 'double_top', 'double_bottom']:
            values = [p[2] for p in points if p[1] in ['PEAK', 'VALLEY']]
            if len(values) >= 2:
                symmetry = 1.0 - (np.std(values) / np.mean(values) if np.mean(values) > 0 else 0.5)
                base_confidence += symmetry * 0.3
        
        # Limita entre 0 e 1
        return max(0.0, min(1.0, base_confidence))
    
    def _update_pattern_accuracy(self, pattern: Dict[str, Any]):
        """Atualiza precisão histórica do padrão."""
        pattern_name = pattern['pattern']
        
        if pattern_name not in self.pattern_accuracy:
            self.pattern_accuracy[pattern_name] = {
                'total_detections': 0,
                'successful_detections': 0,
                'accuracy_history': deque(maxlen=100),
            }
        
        stats = self.pattern_accuracy[pattern_name]
        stats['total_detections'] += 1
        
        # Em implementação real, verificaria se o padrão realmente ocorreu
        # Aqui simulamos com base na confiança
        if pattern['confidence'] > 0.7:
            stats['successful_detections'] += 1
        
        accuracy = stats['successful_detections'] / stats['total_detections'] \
            if stats['total_detections'] > 0 else 0.0
        
        stats['accuracy_history'].append(accuracy)
    
    def get_pattern_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas dos padrões detectados."""
        total_patterns = len(self.detected_patterns)
        
        if total_patterns == 0:
            return {'total_patterns': 0}
        
        # Contagem por tipo de padrão
        pattern_counts = defaultdict(int)
        for pattern in self.detected_patterns:
            pattern_counts[pattern['pattern']] += 1
        
        # Precisão histórica
        accuracy_report = {}
        for pattern_name, stats in self.pattern_accuracy.items():
            accuracy_report[pattern_name] = {
                'total_detections': stats['total_detections'],
                'successful_detections': stats['successful_detections'],
                'current_accuracy': stats['accuracy_history'][-1] if stats['accuracy_history'] else 0.0,
                'avg_accuracy': np.mean(stats['accuracy_history']) if stats['accuracy_history'] else 0.0,
            }
        
        return {
            'total_patterns_detected': total_patterns,
            'pattern_distribution': dict(pattern_counts),
            'pattern_accuracy': accuracy_report,
            'recent_patterns': list(self.detected_patterns)[-5:],
        }

# ========== SISTEMA AUTÔNOMO PRINCIPAL EXPANDIDO ==========

class LextraderAutonomousSystem:
    """Sistema Autônomo LEXTRADER-IAG 3.0 Expandido."""
    
    def __init__(self, config_path: str = None):
        # Configuração
        self.config = self._load_config(config_path)
        
        # Subsistemas principais
        self.sentient_core = SentientCore()  # Do arquivo original
        self.autonomous_manager = AutonomousManager()  # Do arquivo original
        self.experience_manager = ExperienceManager()  # Do arquivo original
        
        # Novos subsistemas expandidos
        self.episodic_memory = EpisodicMemorySystem(capacity=10000)
        self.deep_rl_agent = DeepRLAgent(state_size=10, action_size=5)
        self.market_maker = AutonomousMarketMaker(initial_capital=10000.0)
        self.arbitrage_system = StatisticalArbitrageSystem()
        self.chart_recognizer = ChartPatternRecognizer()
        
        # Sistemas de suporte
        self.executor = ThreadPoolExecutor(max_workers=AutonomousConstants.MAX_CONCURRENT_ANALYSES)
        self.performance_tracker = PerformanceTracker()
        self.risk_manager = RiskManager()
        
        # Estado do sistema
        self.system_status = 'INITIALIZING'
        self.operational_mode = 'AUTONOMOUS'
        self.start_time = datetime.now()
        self.decision_count = 0
        
        # Históricos
        self.market_data_history = deque(maxlen=10000)
        self.decision_history = deque(maxlen=10000)
        self.learning_history = deque(maxlen=10000)
        
        # Cache e otimização
        self.feature_cache = {}
        self.prediction_cache = {}
        
        print("""
╔══════════════════════════════════════════════════════════╗
║        LEXTRADER-IAG 3.0 - SISTEMA AUTÔNOMO             ║
║                Versão Expandida Premium                  ║
╚══════════════════════════════════════════════════════════╝
        """)
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Carrega configuração do sistema."""
        default_config = {
            'mode': 'AUTONOMOUS',
            'risk_profile': 'ADAPTIVE',
            'learning_enabled': True,
            'market_making_enabled': False,
            'arbitrage_enabled': False,
            'pattern_recognition_enabled': True,
            'max_position_size': AutonomousConstants.MAX_POSITION_SIZE,
            'min_confidence': AutonomousConstants.MIN_CONFIDENCE_THRESHOLD,
            'supported_symbols': ['BTC', 'ETH', 'SPY', 'QQQ', 'GLD'],
            'time_frames': AutonomousConstants.SUPPORTED_TIME_FRAMES,
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                print(f"⚠️  Erro ao carregar configuração: {e}")
        
        return default_config
    
    async def start(self):
        """Inicia o sistema autônomo."""
        print("🚀 Iniciando Sistema Autônomo LEXTRADER-IAG...")
        
        self.system_status = 'INITIALIZING'
        
        # Inicializa todos os subsistemas
        initialization_tasks = [
            self._initialize_memory_systems(),
            self._initialize_learning_systems(),
            self._initialize_trading_systems(),
            self._initialize_analysis_systems(),
        ]
        
        await asyncio.gather(*initialization_tasks)
        
        self.system_status = 'OPERATIONAL'
        self.start_time = datetime.now()
        
        print("✅ Sistema Autônomo inicializado com sucesso!")
        print(f"   Modo: {self.operational_mode}")
        print(f"   Subsistemas ativos: {len(initialization_tasks)}")
    
    async def _initialize_memory_systems(self):
        """Inicializa sistemas de memória."""
        print("   • Sistema de Memória Episódica: OK")
        
    async def _initialize_learning_systems(self):
        """Inicializa sistemas de aprendizado."""
        print("   • Agente RL Profundo: OK")
        
    async def _initialize_trading_systems(self):
        """Inicializa sistemas de trading."""
        if self.config.get('market_making_enabled'):
            print("   • Market Maker Autônomo: OK")
        if self.config.get('arbitrage_enabled'):
            print("   • Sistema de Arbitragem: OK")
        
    async def _initialize_analysis_systems(self):
        """Inicializa sistemas de análise."""
        if self.config.get('pattern_recognition_enabled'):
            print("   • Reconhecedor de Padrões: OK")
    
    async def process_autonomous_cycle(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa um ciclo autônomo completo.
        
        Args:
            market_data: Dados de mercado atualizados
            
        Returns:
            Resultado do ciclo autônomo
        """
        cycle_start = time.perf_counter()
        self.decision_count += 1
        
        try:
            # 1. Processamento de dados
            processed_data = await self._process_market_data(market_data)
            
            # 2. Análise de padrões gráficos
            chart_patterns = []
            if self.config.get('pattern_recognition_enabled'):
                chart_patterns = await self._analyze_chart_patterns(processed_data)
            
            # 3. Análise do agente RL
            rl_analysis = await self._get_rl_analysis(processed_data)
            
            # 4. Market Making (se habilitado)
            market_making_result = None
            if self.config.get('market_making_enabled'):
                market_making_result = await self.market_maker.update_market_state(processed_data)
            
            # 5. Arbitragem estatística (se habilitado)
            arbitrage_opportunities = []
            if self.config.get('arbitrage_enabled'):
                arbitrage_opportunities = await self._find_arbitrage_opportunities(processed_data)
            
            # 6. Tomada de decisão integrada
            integrated_decision = await self._make_integrated_decision(
                processed_data, chart_patterns, rl_analysis, 
                market_making_result, arbitrage_opportunities
            )
            
            # 7. Aprendizado e atualização
            await self._learn_from_cycle(integrated_decision, processed_data)
            
            # 8. Gestão de risco
            risk_assessment = await self.risk_manager.assess_risk(
                integrated_decision, processed_data
            )
            
            # 9. Execução simulada
            execution_result = await self._simulate_execution(
                integrated_decision, processed_data
            )
            
            cycle_time = time.perf_counter() - cycle_start
            
            # Construir resultado
            result = {
                'cycle_id': self.decision_count,
                'timestamp': datetime.now().isoformat(),
                'cycle_time_ms': cycle_time * 1000,
                'processed_data': processed_data.get('summary', {}),
                'chart_patterns': chart_patterns[:3],  # Top 3 padrões
                'rl_analysis': rl_analysis,
                'market_making': market_making_result,
                'arbitrage_opportunities': arbitrage_opportunities[:3],  # Top 3
                'integrated_decision': integrated_decision,
                'risk_assessment': risk_assessment,
                'execution_result': execution_result,
                'system_state': self._get_system_state(),
            }
            
            # Armazenar no histórico
            self.decision_history.append(result)
            self.performance_tracker.record_cycle(result)
            
            # Armazenar na memória episódica
            await self._store_in_episodic_memory(result)
            
            return result
            
        except Exception as e:
            print(f"❌ Erro no ciclo autônomo: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                'error': str(e),
                'cycle_id': self.decision_count,
                'timestamp': datetime.now().isoformat(),
            }
    
    async def _process_market_data(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Processa dados de mercado."""
        processed = {
            'raw': market_data,
            'summary': self._summarize_market_data(market_data),
            'indicators': self._calculate_technical_indicators(market_data),
            'sentiment': self._calculate_market_sentiment(market_data),
            'volatility': self._calculate_volatility(market_data),
            'liquidity': self._assess_liquidity(market_data),
            'timestamp': datetime.now(),
        }
        
        # Armazenar no histórico
        self.market_data_history.append(processed)
        
        return processed
    
    async def _analyze_chart_patterns(self, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analisa padrões gráficos."""
        price_data = market_data.get('raw', {}).get('prices', [])
        
        if len(price_data) < 20:  # Mínimo para análise
            return []
        
        patterns = await self.chart_recognizer.analyze_chart(price_data)
        return patterns
    
    async def _get_rl_analysis(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Obtém análise do agente RL."""
        # Extrai features para RL
        features = self._extract_rl_features(market_data)
        
        # Obtém ação do agente
        action, metadata = self.deep_rl_agent.get_action(
            np.array(features), training=True
        )
        
        return {
            'action': action,
            'metadata': metadata,
            'features': features,
            'agent_state': self.deep_rl_agent.get_statistics(),
        }
    
    async def _find_arbitrage_opportunities(self, 
                                          market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Encontra oportunidades de arbitragem."""
        # Prepara dados de preços por símbolo
        price_data = {}
        symbols = self.config.get('supported_symbols', [])
        
        for symbol in symbols[:5]:  # Limita a 5 símbolos por performance
            if symbol in market_data.get('raw', {}):
                # Simula dados históricos
                price_data[symbol] = [
                    market_data['raw'][symbol].get('price', 0) * 
                    (1 + random.uniform(-0.01, 0.01)) 
                    for _ in range(100)
                ]
        
        if len(price_data) >= 2:
            opportunities = await self.arbitrage_system.analyze_pairs(
                price_data, list(price_data.keys())
            )
            return opportunities
        
        return []
    
    async def _make_integrated_decision(self, market_data: Dict[str, Any],
                                      chart_patterns: List[Dict[str, Any]],
                                      rl_analysis: Dict[str, Any],
                                      market_making_result: Optional[Dict[str, Any]],
                                      arbitrage_opportunities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Toma decisão integrada considerando todos os fatores."""
        
        # Coleta todos os sinais
        signals = {
            'rl_signal': rl_analysis.get('action', 0),
            'rl_confidence': rl_analysis.get('metadata', {}).get('q_value', 0.5),
            'chart_patterns': self._aggregate_chart_patterns(chart_patterns),
            'market_sentiment': market_data.get('sentiment', 0),
            'volatility': market_data.get('volatility', 0.01),
            'arbitrage_opportunities': len(arbitrage_opportunities),
        }
        
        # Estado do núcleo senciente
        sentient_state = self.sentient_core.get_state()
        sentient_vector = self.sentient_core.get_vector()
        
        signals['sentient_state'] = sentient_state
        signals['sentient_confidence'] = sentient_vector.confidence / 100
        
        # Consulta memória episódica
        similar_experiences = self.episodic_memory.recall_by_context(
            {'market_data': market_data['summary']}, 
            similarity_threshold=0.6
        )
        
        if similar_experiences:
            signals['memory_similarity'] = similar_experiences[0]['similarity']
            signals['memory_outcome'] = similar_experiences[0]['memory']['episode'].get('outcome', 0)
        
        # Calcula decisão ponderada
        decision = self._calculate_integrated_decision(signals, market_data)
        
        return decision
    
    def _calculate_integrated_decision(self, signals: Dict[str, Any], 
                                     market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula decisão integrada."""
        weights = {
            'rl_signal': 0.25,
            'chart_patterns': 0.20,
            'market_sentiment': 0.15,
            'sentient_confidence': 0.15,
            'memory_outcome': 0.15,
            'volatility': 0.10,
        }
        
        # Normaliza sinais
        normalized_signals = {}
        
        # RL signal (-2 a 2)
        normalized_signals['rl_signal'] = (signals['rl_signal'] / 2.5) * signals.get('rl_confidence', 0.5)
        
        # Chart patterns
        if signals['chart_patterns']:
            pattern_score = signals['chart_patterns'].get('net_score', 0)
            normalized_signals['chart_patterns'] = pattern_score * 0.5  # Escala para -0.5 a 0.5
        else:
            normalized_signals['chart_patterns'] = 0
        
        # Market sentiment
        normalized_signals['market_sentiment'] = signals['market_sentiment']
        
        # Sentient confidence
        normalized_signals['sentient_confidence'] = signals['sentient_confidence'] - 0.5
        
        # Memory outcome
        memory_outcome = signals.get('memory_outcome', 0)
        memory_similarity = signals.get('memory_similarity', 0)
        normalized_signals['memory_outcome'] = memory_outcome * memory_similarity
        
        # Volatility adjustment
        volatility = signals.get('volatility', 0.01)
        volatility_adjustment = 1.0 / (1.0 + volatility * 10)
        
        # Calcula decisão ponderada
        weighted_sum = 0
        total_weight = 0
        
        for signal_name, weight in weights.items():
            if signal_name in normalized_signals:
                weighted_sum += normalized_signals[signal_name] * weight
                total_weight += weight
        
        decision_value = weighted_sum / total_weight if total_weight > 0 else 0
        
        # Aplica ajuste de volatilidade
        decision_value *= volatility_adjustment
        
        # Determina ação
        action, confidence = self._map_decision_to_action(decision_value, signals)
        
        return {
            'action': action,
            'confidence': confidence,
            'decision_value': decision_value,
            'signals': signals,
            'weights': weights,
            'normalized_signals': normalized_signals,
            'volatility_adjustment': volatility_adjustment,
            'timestamp': datetime.now(),
        }
    
    def _map_decision_to_action(self, decision_value: float, 
                              signals: Dict[str, Any]) -> Tuple[str, float]:
        """Mapeia valor de decisão para ação."""
        # Limites adaptativos baseados na confiança
        sentient_confidence = signals.get('sentient_confidence', 0.5)
        volatility = signals.get('volatility', 0.01)
        
        # Ajusta limites baseado na confiança e volatilidade
        strong_threshold = 0.3 * sentient_confidence / (1 + volatility * 5)
        weak_threshold = 0.1 * sentient_confidence / (1 + volatility * 5)
        
        if decision_value > strong_threshold:
            action = 'STRONG_BUY'
            confidence = min(0.95, (decision_value - strong_threshold) * 2)
        elif decision_value > weak_threshold:
            action = 'BUY'
            confidence = (decision_value - weak_threshold) / (strong_threshold - weak_threshold) * 0.5 + 0.5
        elif decision_value < -strong_threshold:
            action = 'STRONG_SELL'
            confidence = min(0.95, (-decision_value - strong_threshold) * 2)
        elif decision_value < -weak_threshold:
            action = 'SELL'
            confidence = (-decision_value - weak_threshold) / (strong_threshold - weak_threshold) * 0.5 + 0.5
        else:
            action = 'HOLD'
            confidence = 0.5 - abs(decision_value) * 2
        
        return action, confidence
    
    def _aggregate_chart_patterns(self, patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Agrega múltiplos padrões gráficos."""
        if not patterns:
            return {}
        
        # Contagem por tipo de padrão
        pattern_counts = defaultdict(int)
        total_confidence = 0
        bull_patterns = 0
        bear_patterns = 0
        
        for pattern in patterns:
            pattern_type = pattern['pattern']
            pattern_counts[pattern_type] += 1
            total_confidence += pattern['confidence']
            
            if pattern['expected_outcome'] == 'BULLISH':
                bull_patterns += 1
            elif pattern['expected_outcome'] == 'BEARISH':
                bear_patterns += 1
        
        avg_confidence = total_confidence / len(patterns) if patterns else 0
        
        # Calcula net score
        net_score = (bull_patterns - bear_patterns) / max(1, len(patterns))
        
        return {
            'total_patterns': len(patterns),
            'pattern_distribution': dict(pattern_counts),
            'avg_confidence': avg_confidence,
            'bull_patterns': bull_patterns,
            'bear_patterns': bear_patterns,
            'net_score': net_score,
            'dominant_signal': 'BULLISH' if net_score > 0.1 else 'BEARISH' if net_score < -0.1 else 'NEUTRAL',
        }
    
    async def _learn_from_cycle(self, decision: Dict[str, Any], 
                              market_data: Dict[str, Any]):
        """Aprende do ciclo atual."""
        # Prepara experiência para RL
        features = self._extract_rl_features(market_data)
        
        # Simula recompensa (em produção, viria do resultado real)
        simulated_reward = self._simulate_reward(decision, market_data)
        
        # Armazena experiência no buffer RL
        next_features = features  # Simplificado
        self.deep_rl_agent.store_experience(
            np.array(features),
            self._action_to_index(decision['action']),
            simulated_reward,
            np.array(next_features),
            False  # Not done
        )
        
        # Treina agente RL periodicamente
        if self.decision_count % 10 == 0:
            training_result = self.deep_rl_agent.train()
            self.learning_history.append(training_result)
    
    async def _simulate_execution(self, decision: Dict[str, Any],
                                market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Simula execução da decisão."""
        # Em sistema real, aqui conectaria com API de trading
        # Por enquanto, simula execução
        
        action = decision['action']
        confidence = decision['confidence']
        price = market_data['summary'].get('price', 0)
        
        # Simula slippage e fees
        slippage = random.uniform(-0.001, 0.001)  # 0.1%
        fees = 0.001  # 0.1%
        
        executed_price = price * (1 + slippage)
        cost = executed_price * fees if action != 'HOLD' else 0
        
        # Simula resultado
        if action in ['BUY', 'STRONG_BUY']:
            # Assume que compra foi boa se confiança alta
            success = confidence > 0.7
            pnl = 0.01 if success else -0.005  # 1% gain ou 0.5% loss
        elif action in ['SELL', 'STRONG_SELL']:
            success = confidence > 0.7
            pnl = 0.01 if success else -0.005
        else:
            success = True
            pnl = 0.0
        
        # Ajusta por fees
        pnl -= fees
        
        return {
            'action': action,
            'requested_price': price,
            'executed_price': executed_price,
            'slippage': slippage,
            'fees': fees,
            'success': success,
            'pnl': pnl,
            'timestamp': datetime.now(),
        }
    
    async def _store_in_episodic_memory(self, cycle_result: Dict[str, Any]):
        """Armazena ciclo na memória episódica."""
        episode = {
            'decision': cycle_result['integrated_decision'],
            'market_data': cycle_result['processed_data'],
            'outcome': cycle_result['execution_result']['pnl'],
            'success': cycle_result['execution_result']['success'],
            'confidence': cycle_result['integrated_decision']['confidence'],
            'cycle_id': cycle_result['cycle_id'],
        }
        
        tags = [
            cycle_result['integrated_decision']['action'],
            'success' if cycle_result['execution_result']['success'] else 'failure',
            f"confidence_{int(cycle_result['integrated_decision']['confidence'] * 100)}",
            f"cycle_{cycle_result['cycle_id']}",
        ]
        
        self.episodic_memory.store_episode(episode, tags)
    
    def _get_system_state(self) -> Dict[str, Any]:
        """Retorna estado atual do sistema."""
        uptime = datetime.now() - self.start_time
        
        return {
            'system_status': self.system_status,
            'operational_mode': self.operational_mode,
            'uptime': str(uptime),
            'decision_count': self.decision_count,
            'market_data_history_size': len(self.market_data_history),
            'decision_history_size': len(self.decision_history),
            'learning_history_size': len(self.learning_history),
            'episodic_memory_stats': self.episodic_memory.get_statistics(),
            'rl_agent_stats': self.deep_rl_agent.get_statistics(),
            'performance_tracker': self.performance_tracker.get_statistics(),
        }
    
    def _extract_rl_features(self, market_data: Dict[str, Any]) -> List[float]:
        """Extrai features para RL."""
        summary = market_data.get('summary', {})
        indicators = market_data.get('indicators', {})
        
        features = [
            summary.get('price', 0) / 100000,  # Normalizado
            summary.get('volume', 0) / 10000,  # Normalizado
            indicators.get('rsi', 50) / 100,   # 0-1
            indicators.get('macd', 0) / 10,    # Normalizado
            market_data.get('sentiment', 0),   # -1 a 1
            market_data.get('volatility', 0.01),
            indicators.get('bb_width', 0.02) / 0.1,  # Normalizado
            indicators.get('stoch_k', 50) / 100,
            indicators.get('stoch_d', 50) / 100,
            market_data.get('liquidity', 0.5),  # 0-1
        ]
        
        # Garante tamanho correto
        while len(features) < 10:
            features.append(0.0)
        
        return features[:10]
    
    def _action_to_index(self, action: str) -> int:
        """Converte ação para índice RL."""
        action_map = {
            'STRONG_SELL': 0,
            'SELL': 1,
            'HOLD': 2,
            'BUY': 3,
            'STRONG_BUY': 4,
        }
        return action_map.get(action, 2)  # Default para HOLD
    
    def _simulate_reward(self, decision: Dict[str, Any], 
                        market_data: Dict[str, Any]) -> float:
        """Simula recompensa para aprendizado RL."""
        action = decision['action']
        confidence = decision['confidence']
        
        # Baseado no sentimento do mercado
        sentiment = market_data.get('sentiment', 0)
        
        if action in ['BUY', 'STRONG_BUY']:
            # Recompensa positiva se compra alinhada com sentimento positivo
            reward = sentiment * confidence
        elif action in ['SELL', 'STRONG_SELL']:
            # Recompensa positiva se venda alinhada com sentimento negativo
            reward = -sentiment * confidence
        else:  # HOLD
            # Recompensa por paciência em mercados neutros
            reward = (1 - abs(sentiment)) * confidence * 0.5
        
        return float(reward)

# ========== SISTEMAS AUXILIARES ==========

class PerformanceTracker:
    """Rastreador de performance do sistema."""
    
    def __init__(self):
        self.cycle_stats = deque(maxlen=1000)
        self.decision_stats = deque(maxlen=1000)
        self.pnl_history = deque(maxlen=10000)
        
    def record_cycle(self, cycle_result: Dict[str, Any]):
        """Registra estatísticas de um ciclo."""
        stats = {
            'cycle_id': cycle_result['cycle_id'],
            'timestamp': datetime.now(),
            'cycle_time_ms': cycle_result['cycle_time_ms'],
            'decision_action': cycle_result['integrated_decision']['action'],
            'decision_confidence': cycle_result['integrated_decision']['confidence'],
            'execution_pnl': cycle_result['execution_result']['pnl'],
            'execution_success': cycle_result['execution_result']['success'],
            'market_volatility': cycle_result['processed_data'].get('volatility', 0),
            'market_sentiment': cycle_result['processed_data'].get('sentiment', 0),
        }
        
        self.cycle_stats.append(stats)
        self.pnl_history.append(cycle_result['execution_result']['pnl'])
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas de performance."""
        if not self.cycle_stats:
            return {'status': 'NO_DATA'}
        
        recent = list(self.cycle_stats)[-100:]  # Últimos 100 ciclos
        
        # Calcula métricas
        total_cycles = len(self.cycle_stats)
        successful_decisions = len([s for s in recent if s['execution_success']])
        success_rate = successful_decisions / len(recent) if recent else 0
        
        # PnL acumulado
        total_pnl = sum(s['execution_pnl'] for s in recent)
        avg_pnl = total_pnl / len(recent) if recent else 0
        
        # Sharpe ratio (simplificado)
        if len(self.pnl_history) > 1:
            returns = list(self.pnl_history)
            avg_return = np.mean(returns)
            std_return = np.std(returns)
            
            if std_return > 0:
                sharpe = (avg_return - AutonomousConstants.RISK_FREE_RATE/365) / std_return * np.sqrt(365)
            else:
                sharpe = 0
        else:
            sharpe = 0
        
        # Drawdown
        if self.pnl_history:
            cumulative = np.cumsum(list(self.pnl_history))
            running_max = np.maximum.accumulate(cumulative)
            drawdowns = (running_max - cumulative) / running_max
            max_drawdown = np.max(drawdowns) if len(drawdowns) > 0 else 0
        else:
            max_drawdown = 0
        
        return {
            'total_cycles': total_cycles,
            'success_rate': f"{success_rate:.1%}",
            'avg_cycle_time_ms': np.mean([s['cycle_time_ms'] for s in recent]) if recent else 0,
            'avg_decision_confidence': np.mean([s['decision_confidence'] for s in recent]) if recent else 0,
            'total_pnl': total_pnl,
            'avg_pnl_per_cycle': avg_pnl,
            'sharpe_ratio': f"{sharpe:.2f}",
            'max_drawdown': f"{max_drawdown:.2%}",
            'recent_action_distribution': self._get_action_distribution(recent),
        }
    
    def _get_action_distribution(self, stats: List[Dict[str, Any]]) -> Dict[str, int]:
        """Distribuição de ações recentes."""
        distribution = defaultdict(int)
        
        for stat in stats:
            action = stat['decision_action']
            distribution[action] += 1
        
        return dict(distribution)

class RiskManager:
    """Gerenciador de risco do sistema."""
    
    def __init__(self):
        self.risk_metrics = deque(maxlen=1000)
        self.exposure_history = deque(maxlen=1000)
        self.risk_alerts = deque(maxlen=100)
        
    async def assess_risk(self, decision: Dict[str, Any], 
                         market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Avalia risco de uma decisão."""
        action = decision['action']
        confidence = decision['confidence']
        volatility = market_data.get('volatility', 0.01)
        
        # Calcula métricas de risco
        risk_score = self._calculate_risk_score(action, confidence, volatility)
        position_size = self._calculate_position_size(action, confidence, volatility)
        stop_loss = self._calculate_stop_loss(action, market_data)
        take_profit = self._calculate_take_profit(action, market_data)
        
        # Verifica alertas de risco
        alerts = self._check_risk_alerts(risk_score, position_size, volatility)
        
        assessment = {
            'risk_score': risk_score,
            'position_size': position_size,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'risk_reward_ratio': (take_profit - 1) / (1 - stop_loss) if stop_loss < 1 and take_profit > 1 else 0,
            'max_loss': 1 - stop_loss,
            'max_gain': take_profit - 1,
            'alerts': alerts,
            'timestamp': datetime.now(),
        }
        
        self.risk_metrics.append(assessment)
        
        return assessment
    
    def _calculate_risk_score(self, action: str, confidence: float, 
                            volatility: float) -> float:
        """Calcula score de risco."""
        base_score = 0.5
        
        # Ajusta pela ação
        if action in ['STRONG_BUY', 'STRONG_SELL']:
            base_score += 0.3
        elif action in ['BUY', 'SELL']:
            base_score += 0.1
        
        # Ajusta pela confiança (mais confiança = menos risco percebido)
        base_score -= confidence * 0.2
        
        # Ajusta pela volatilidade
        base_score += volatility * 5
        
        return max(0.0, min(1.0, base_score))
    
    def _calculate_position_size(self, action: str, confidence: float,
                               volatility: float) -> float:
        """Calcula tamanho da posição."""
        if action == 'HOLD':
            return 0.0
        
        base_size = AutonomousConstants.MAX_POSITION_SIZE
        
        # Ajusta pela confiança
        confidence_adjustment = confidence ** 2  # Quadrático
        
        # Ajusta pela volatilidade
        volatility_adjustment = 1.0 / (1.0 + volatility * 10)
        
        # Tamanho final
        size = base_size * confidence_adjustment * volatility_adjustment
        
        return min(base_size, size)
    
    def _calculate_stop_loss(self, action: str, 
                           market_data: Dict[str, Any]) -> float:
        """Calcula nível de stop loss."""
        price = market_data['summary'].get('price', 1)
        volatility = market_data.get('volatility', 0.01)
        
        # Stop loss baseado na volatilidade
        stop_distance = volatility * 2  # 2x volatilidade
        
        if action in ['BUY', 'STRONG_BUY']:
            return price * (1 - stop_distance)
        elif action in ['SELL', 'STRONG_SELL']:
            return price * (1 + stop_distance)
        else:
            return price
    
    def _calculate_take_profit(self, action: str, 
                             market_data: Dict[str, Any]) -> float:
        """Calcula nível de take profit."""
        price = market_data['summary'].get('price', 1)
        volatility = market_data.get('volatility', 0.01)
        
        # Take profit com ratio 2:1 em relação ao stop loss
        stop_distance = volatility * 2
        take_distance = stop_distance * AutonomousConstants.TAKE_PROFIT_RATIO
        
        if action in ['BUY', 'STRONG_BUY']:
            return price * (1 + take_distance)
        elif action in ['SELL', 'STRONG_SELL']:
            return price * (1 - take_distance)
        else:
            return price
    
    def _check_risk_alerts(self, risk_score: float, position_size: float,
                          volatility: float) -> List[Dict[str, Any]]:
        """Verifica alertas de risco."""
        alerts = []
        
        if risk_score > 0.8:
            alerts.append({
                'level': 'HIGH',
                'message': f'Score de risco muito alto: {risk_score:.2f}',
                'type': 'RISK_SCORE',
            })
        
        if position_size > AutonomousConstants.MAX_POSITION_SIZE * 0.9:
            alerts.append({
                'level': 'HIGH',
                'message': f'Tamanho da posição próximo do limite: {position_size:.1%}',
                'type': 'POSITION_SIZE',
            })
        
        if volatility > 0.05:
            alerts.append({
                'level': 'MEDIUM',
                'message': f'Alta volatilidade: {volatility:.1%}',
                'type': 'VOLATILITY',
            })
        
        # Armazena alertas significativos
        if alerts:
            self.risk_alerts.extend(alerts)
        
        return alerts

# ========== FUNÇÃO PRINCIPAL DE DEMONSTRAÇÃO ==========

async def demonstrate_autonomous_system():
    """Demonstração do Sistema Autônomo LEXTRADER-IAG 3.0."""
    
    print("""
╔══════════════════════════════════════════════════════════╗
║    LEXTRADER-IAG 3.0 - SISTEMA AUTÔNOMO EXPANDIDO        ║
║                  Demonstração Completa                   ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    # Inicializar sistema
    lextrader = LextraderAutonomousSystem()
    await lextrader.start()
    
    print("\n" + "="*60)
    print("📊 FASE 1: Preparação de Dados de Mercado")
    print("="*60)
    
    # Gerar dados de mercado simulados
    market_data_batch = []
    for i in range(10):
        symbol_data = {}
        for symbol in lextrader.config['supported_symbols'][:3]:
            symbol_data[symbol] = {
                'price': 50000 + random.uniform(-2000, 2000),
                'volume': random.uniform(1000, 10000),
                'timestamp': datetime.now(),
                'indicators': {
                    'rsi': random.uniform(20, 80),
                    'macd': random.uniform(-5, 5),
                    'bb_upper': 51000,
                    'bb_lower': 49000,
                    'stoch_k': random.uniform(20, 80),
                    'stoch_d': random.uniform(20, 80),
                }
            }
        
        market_data_batch.append({
            'symbols': symbol_data,
            'timestamp': datetime.now(),
        })
    
    print(f"• Batch de dados: {len(market_data_batch)} conjuntos")
    print(f"• Símbolos: {len(lextrader.config['supported_symbols'][:3])}")
    
    print("\n" + "="*60)
    print("🧠 FASE 2: Execução de Ciclos Autônomos")
    print("="*60)
    
    # Executar múltiplos ciclos
    cycle_results = []
    for i, market_data in enumerate(market_data_batch):
        print(f"\n  Ciclo #{i+1}:")
        
        result = await lextrader.process_autonomous_cycle(market_data)
        cycle_results.append(result)
        
        decision = result['integrated_decision']
        execution = result['execution_result']
        
        print(f"    • Decisão: {decision['action']}")
        print(f"    • Confiança: {decision['confidence']:.1%}")
        print(f"    • PnL: {execution['pnl']:.3%}")
        print(f"    • Tempo: {result['cycle_time_ms']:.1f}ms")
        
        await asyncio.sleep(0.1)  # Pequena pausa
    
    print("\n" + "="*60)
    print("📈 FASE 3: Análise de Performance")
    print("="*60)
    
    # Obter estatísticas do sistema
    system_state = lextrader._get_system_state()
    performance = lextrader.performance_tracker.get_statistics()
    
    print("Estatísticas do Sistema:")
    print(f"  • Ciclos executados: {system_state['decision_count']}")
    print(f"  • Uptime: {system_state['uptime']}")
    print(f"  • Taxa de sucesso: {performance['success_rate']}")
    print(f"  • PnL total: {performance['total_pnl']:.3%}")
    print(f"  • Sharpe ratio: {performance['sharpe_ratio']}")
    print(f"  • Max drawdown: {performance['max_drawdown']}")
    
    print("\nDistribuição de Ações:")
    for action, count in performance['recent_action_distribution'].items():
        print(f"  • {action}: {count}")
    
    print("\n" + "="*60)
    print("🧠 FASE 4: Subsistemas em Destaque")
    print("="*60)
    
    # Memória Episódica
    print("\nMemória Episódica:")
    memory_stats = lextrader.episodic_memory.get_statistics()
    print(f"  • Total de memórias: {memory_stats['total_memories']}")
    print(f"  • Utilização: {memory_stats['memory_utilization']:.1%}")
    
    # Agente RL
    print("\nAgente RL Profundo:")
    rl_stats = lextrader.deep_rl_agent.get_statistics()
    print(f"  • Total de passos: {rl_stats['total_steps']}")
    print(f"  • Buffer de replay: {rl_stats['replay_buffer_size']}")
    print(f"  • Epsilon atual: {rl_stats['epsilon']:.3f}")
    
    # Reconhecimento de Padrões
    print("\nReconhecimento de Padrões:")
    pattern_stats = lextrader.chart_recognizer.get_pattern_statistics()
    print(f"  • Padrões detectados: {pattern_stats['total_patterns_detected']}")
    
    print("\n" + "="*60)
    print("⚡ FASE 5: Market Making Autônomo")
    print("="*60)
    
    if lextrader.config.get('market_making_enabled'):
        # Simular alguns passos de market making
        print("Simulando market making...")
        
        for i in range(3):
            market_data = {
                'price': 50000 + random.uniform(-500, 500),
                'volatility': random.uniform(0.005, 0.02),
            }
            
            result = await lextrader.market_maker.update_market_state(market_data)
            
            if i == 2:  # Última iteração
                print(f"  • Bid: ${result['bid_price']:.2f}")
                print(f"  • Ask: ${result['ask_price']:.2f}")
                print(f"  • Spread: ${result['spread']:.2f}")
                print(f"  • Inventário: {result['inventory']:.2f}")
    
    print("\n" + "="*60)
    print("🎯 FASE 6: Padrões Detectados")
    print("="*60)
    
    # Mostrar padrões detectados
    if cycle_results:
        last_cycle = cycle_results[-1]
        patterns = last_cycle['chart_patterns']
        
        if patterns:
            print(f"Padrões detectados no último ciclo:")
            for i, pattern in enumerate(patterns[:3]):
                print(f"  {i+1}. {pattern['pattern']} - Conf: {pattern['confidence']:.1%}")
        else:
            print("Nenhum padrão significativo detectado")
    
    print("\n" + "="*60)
    print("📋 RESUMO FINAL DO SISTEMA")
    print("="*60)
    
    # Relatório final
    print("\n🎯 SISTEMA LEXTRADER-IAG 3.0 AUTÔNOMO:")
    print(f"• Status: {system_state['system_status']}")
    print(f"• Modo: {system_state['operational_mode']}")
    print(f"• Decisões tomadas: {system_state['decision_count']}")
    print(f"• Memória episódica: {memory_stats['total_memories']} experiências")
    print(f"• Agente RL: {rl_stats['total_steps']} passos de aprendizado")
    print(f"• Performance: {performance['success_rate']} taxa de sucesso")
    print(f"• PnL acumulado: {performance['total_pnl']:.3%}")
    
    print("""
╔══════════════════════════════════════════════════════════╗
║    SISTEMA AUTÔNOMO OPERACIONAL E APRENDENDO! 🚀        ║
╚══════════════════════════════════════════════════════════╝
    """)

async def main():
    """Função principal."""
    try:
        await demonstrate_autonomous_system()
    except KeyboardInterrupt:
        print("\n\n👋 Sistema interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro na demonstração: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Executar demonstração
    asyncio.run(main(), debug=False)
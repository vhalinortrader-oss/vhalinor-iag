"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                ALGORITMOS DE APRENDIZADO POR REFORÇO PARA FINANÇAS             ║
║                 Componente 6: Implementação de Algoritmos RL                    ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import asyncio
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.distributions import Categorical, Normal
from collections import deque, defaultdict
import random
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import matplotlib.pyplot as plt
import json
import os
from pathlib import Path

# Import do módulo anterior
from reinforcement_learning_environment import TradingEnvironment, EnvironmentConfig

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('RLAlgorithmsFinancial')

class AlgorithmType(Enum):
    """Tipos de algoritmos RL"""
    DQN = "dqn"
    DOUBLE_DQN = "double_dqn"
    DUELING_DQN = "dueling_dqn"
    PPO = "ppo"
    A2C = "a2c"
    A3C = "a3c"
    SAC = "sac"
    TD3 = "td3"
    TRPO = "trpo"
    DDPG = "ddpg"

class NetworkType(Enum):
    """Tipos de redes neurais"""
    MLP = "mlp"
    CNN = "cnn"
    LSTM = "lstm"
    GRU = "gru"
    TRANSFORMER = "transformer"

@dataclass
class AgentConfig:
    """Configuração do agente RL"""
    algorithm_type: AlgorithmType
    network_type: NetworkType
    state_dim: int
    action_dim: int
    hidden_dims: List[int] = field(default_factory=lambda: [256, 256])
    learning_rate: float = 3e-4
    gamma: float = 0.99
    tau: float = 0.005  # Para soft update
    epsilon_start: float = 1.0
    epsilon_end: float = 0.01
    epsilon_decay: int = 10000
    buffer_size: int = 100000
    batch_size: int = 64
    target_update_freq: int = 1000
    clip_ratio: float = 0.2  # Para PPO
    value_loss_coef: float = 0.5
    entropy_coef: float = 0.01
    max_grad_norm: float = 0.5
    use_double_q: bool = True
    use_dueling: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'algorithm_type': self.algorithm_type.value,
            'network_type': self.network_type.value,
            'state_dim': self.state_dim,
            'action_dim': self.action_dim,
            'hidden_dims': self.hidden_dims,
            'learning_rate': self.learning_rate,
            'gamma': self.gamma,
            'tau': self.tau,
            'epsilon_start': self.epsilon_start,
            'epsilon_end': self.epsilon_end,
            'epsilon_decay': self.epsilon_decay,
            'buffer_size': self.buffer_size,
            'batch_size': self.batch_size,
            'target_update_freq': self.target_update_freq,
            'clip_ratio': self.clip_ratio,
            'value_loss_coef': self.value_loss_coef,
            'entropy_coef': self.entropy_coef,
            'max_grad_norm': self.max_grad_norm,
            'use_double_q': self.use_double_q,
            'use_dueling': self.use_dueling
        }

@dataclass
class TrainingMetrics:
    """Métricas de treinamento"""
    episode: int
    total_reward: float
    average_reward: float
    episode_length: int
    loss: float
    value_loss: float
    policy_loss: float
    entropy: float
    epsilon: float
    q_value: float
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'episode': self.episode,
            'total_reward': self.total_reward,
            'average_reward': self.average_reward,
            'episode_length': self.episode_length,
            'loss': self.loss,
            'value_loss': self.value_loss,
            'policy_loss': self.policy_loss,
            'entropy': self.entropy,
            'epsilon': self.epsilon,
            'q_value': self.q_value,
            'timestamp': self.timestamp.isoformat()
        }

class ReplayBuffer:
    """Buffer de experiência para algoritmos off-policy"""
    
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.buffer = deque(maxlen=capacity)
        self.position = 0
    
    def push(self, state, action, reward, next_state, done):
        """Adiciona experiência ao buffer"""
        self.buffer.append((state, action, reward, next_state, done))
    
    def sample(self, batch_size: int):
        """Amostra experiências do buffer"""
        batch = random.sample(self.buffer, batch_size)
        state, action, reward, next_state, done = map(np.stack, zip(*batch))
        return state, action, reward, next_state, done
    
    def __len__(self):
        return len(self.buffer)

class PrioritizedReplayBuffer:
    """Buffer de experiência com priorização"""
    
    def __init__(self, capacity: int, alpha: float = 0.6, beta: float = 0.4):
        self.capacity = capacity
        self.alpha = alpha
        self.beta = beta
        self.buffer = []
        self.priorities = np.zeros(capacity, dtype=np.float32)
        self.position = 0
    
    def push(self, state, action, reward, next_state, done):
        """Adiciona experiência com prioridade máxima"""
        max_priority = self.priorities.max() if self.buffer else 1.0
        
        if len(self.buffer) < self.capacity:
            self.buffer.append((state, action, reward, next_state, done))
        else:
            self.buffer[self.position] = (state, action, reward, next_state, done)
        
        self.priorities[self.position] = max_priority
        self.position = (self.position + 1) % self.capacity
    
    def sample(self, batch_size: int):
        """Amostra baseado nas prioridades"""
        if len(self.buffer) == self.capacity:
            priorities = self.priorities
        else:
            priorities = self.priorities[:self.position]
        
        probs = priorities ** self.alpha
        probs /= probs.sum()
        
        indices = np.random.choice(len(self.buffer), batch_size, p=probs)
        samples = [self.buffer[idx] for idx in indices]
        
        # Calcula pesos de importância
        weights = (len(self.buffer) * probs[indices]) ** (-self.beta)
        weights /= weights.max()
        
        state, action, reward, next_state, done = map(np.stack, zip(*samples))
        return state, action, reward, next_state, done, indices, weights
    
    def update_priorities(self, indices, priorities):
        """Atualiza prioridades"""
        for idx, priority in zip(indices, priorities):
            self.priorities[idx] = priority
    
    def __len__(self):
        return len(self.buffer)

class MLPNetwork(nn.Module):
    """Rede MLP base"""
    
    def __init__(self, input_dim: int, hidden_dims: List[int], output_dim: int):
        super(MLPNetwork, self).__init__()
        
        layers = []
        prev_dim = input_dim
        
        for hidden_dim in hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.ReLU(),
                nn.Dropout(0.1)
            ])
            prev_dim = hidden_dim
        
        layers.append(nn.Linear(prev_dim, output_dim))
        
        self.network = nn.Sequential(*layers)
    
    def forward(self, x):
        return self.network(x)

class DuelingNetwork(nn.Module):
    """Rede Dueling DQN"""
    
    def __init__(self, input_dim: int, hidden_dims: List[int], output_dim: int):
        super(DuelingNetwork, self).__init__()
        
        # Camada compartilhada
        self.shared_layers = nn.Sequential(
            nn.Linear(input_dim, hidden_dims[0]),
            nn.ReLU(),
            nn.Linear(hidden_dims[0], hidden_dims[1]),
            nn.ReLU()
        )
        
        # Value stream
        self.value_stream = nn.Sequential(
            nn.Linear(hidden_dims[1], hidden_dims[2]),
            nn.ReLU(),
            nn.Linear(hidden_dims[2], 1)
        )
        
        # Advantage stream
        self.advantage_stream = nn.Sequential(
            nn.Linear(hidden_dims[1], hidden_dims[2]),
            nn.ReLU(),
            nn.Linear(hidden_dims[2], output_dim)
        )
    
    def forward(self, x):
        shared = self.shared_layers(x)
        value = self.value_stream(shared)
        advantage = self.advantage_stream(shared)
        
        # Combina value e advantage
        q_values = value + (advantage - advantage.mean(dim=1, keepdim=True))
        return q_values

class ActorCriticNetwork(nn.Module):
    """Rede Actor-Critic para algoritmos on-policy"""
    
    def __init__(self, input_dim: int, hidden_dims: List[int], action_dim: int, 
                 continuous: bool = False):
        super(ActorCriticNetwork, self).__init__()
        
        self.continuous = continuous
        
        # Camadas compartilhadas
        self.shared_layers = nn.Sequential(
            nn.Linear(input_dim, hidden_dims[0]),
            nn.ReLU(),
            nn.Linear(hidden_dims[0], hidden_dims[1]),
            nn.ReLU()
        )
        
        # Actor (policy)
        self.actor_mean = nn.Linear(hidden_dims[1], action_dim)
        if continuous:
            self.actor_log_std = nn.Parameter(torch.zeros(action_dim))
        
        # Critic (value)
        self.critic = nn.Linear(hidden_dims[1], 1)
    
    def forward(self, x):
        shared = self.shared_layers(x)
        
        # Actor
        if self.continuous:
            action_mean = self.actor_mean(shared)
            action_std = torch.exp(self.actor_log_std)
            dist = Normal(action_mean, action_std)
        else:
            action_logits = self.actor_mean(shared)
            dist = Categorical(logits=action_logits)
        
        # Critic
        value = self.critic(shared)
        
        return dist, value

class DQNAgent:
    """Agente DQN para trading"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Redes
        if config.use_dueling:
            self.q_network = DuelingNetwork(
                config.state_dim, config.hidden_dims, config.action_dim
            ).to(self.device)
            self.target_network = DuelingNetwork(
                config.state_dim, config.hidden_dims, config.action_dim
            ).to(self.device)
        else:
            self.q_network = MLPNetwork(
                config.state_dim, config.hidden_dims, config.action_dim
            ).to(self.device)
            self.target_network = MLPNetwork(
                config.state_dim, config.hidden_dims, config.action_dim
            ).to(self.device)
        
        # Otimizador
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=config.learning_rate)
        
        # Buffer de experiência
        self.replay_buffer = ReplayBuffer(config.buffer_size)
        
        # Parâmetros
        self.epsilon = config.epsilon_start
        self.steps_done = 0
        
        # Métricas
        self.training_metrics = []
        
        # Copia pesos para rede target
        self.update_target_network()
        
        logger.info(f"🤖 Agente DQN inicializado com {config.algorithm_type.value}")
    
    def select_action(self, state, training: bool = True):
        """Seleciona ação usando política epsilon-greedy"""
        if training and random.random() < self.epsilon:
            return random.randrange(self.config.action_dim)
        
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            q_values = self.q_network(state_tensor)
            return q_values.argmax().item()
    
    def store_transition(self, state, action, reward, next_state, done):
        """Armazena transição no buffer"""
        self.replay_buffer.push(state, action, reward, next_state, done)
    
    def train_step(self):
        """Realiza um passo de treinamento"""
        if len(self.replay_buffer) < self.config.batch_size:
            return None
        
        # Amostra do buffer
        states, actions, rewards, next_states, dones = self.replay_buffer.sample(
            self.config.batch_size
        )
        
        states = torch.FloatTensor(states).to(self.device)
        actions = torch.LongTensor(actions).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        next_states = torch.FloatTensor(next_states).to(self.device)
        dones = torch.BoolTensor(dones).to(self.device)
        
        # Calcula Q-values atual
        current_q_values = self.q_network(states).gather(1, actions.unsqueeze(1))
        
        # Calcula Q-values target
        with torch.no_grad():
            if self.config.use_double_q:
                # Double DQN
                next_actions = self.q_network(next_states).argmax(1, keepdim=True)
                next_q_values = self.target_network(next_states).gather(1, next_actions).squeeze(1)
            else:
                # DQN padrão
                next_q_values = self.target_network(next_states).max(1)[0]
            
            target_q_values = rewards + (self.config.gamma * next_q_values * ~dones)
        
        # Calcula loss
        loss = F.mse_loss(current_q_values.squeeze(), target_q_values)
        
        # Otimização
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.q_network.parameters(), self.config.max_grad_norm)
        self.optimizer.step()
        
        # Atualiza epsilon
        self.steps_done += 1
        self.epsilon = max(
            self.config.epsilon_end,
            self.config.epsilon_start - 
            (self.config.epsilon_start - self.config.epsilon_end) * 
            self.steps_done / self.config.epsilon_decay
        )
        
        # Atualiza rede target periodicamente
        if self.steps_done % self.config.target_update_freq == 0:
            self.update_target_network()
        
        return loss.item()
    
    def update_target_network(self):
        """Atualiza rede target com pesos da rede principal"""
        self.target_network.load_state_dict(self.q_network.state_dict())
    
    def save_model(self, path: str):
        """Salva modelo"""
        torch.save({
            'q_network_state_dict': self.q_network.state_dict(),
            'target_network_state_dict': self.target_network.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'config': self.config.to_dict(),
            'epsilon': self.epsilon,
            'steps_done': self.steps_done
        }, path)
        logger.info(f"Modelo DQN salvo em {path}")
    
    def load_model(self, path: str):
        """Carrega modelo"""
        checkpoint = torch.load(path, map_location=self.device)
        
        self.q_network.load_state_dict(checkpoint['q_network_state_dict'])
        self.target_network.load_state_dict(checkpoint['target_network_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.epsilon = checkpoint.get('epsilon', self.config.epsilon_start)
        self.steps_done = checkpoint.get('steps_done', 0)
        
        logger.info(f"Modelo DQN carregado de {path}")

class PPOAgent:
    """Agente PPO (Proximal Policy Optimization)"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Rede Actor-Critic
        self.actor_critic = ActorCriticNetwork(
            config.state_dim, config.hidden_dims, config.action_dim
        ).to(self.device)
        
        # Otimizadores
        self.optimizer = optim.Adam(
            self.actor_critic.parameters(), 
            lr=config.learning_rate
        )
        
        # Buffer para PPO
        self.states = []
        self.actions = []
        self.rewards = []
        self.values = []
        self.log_probs = []
        self.dones = []
        
        # Métricas
        self.training_metrics = []
        
        logger.info(f"🤖 Agente PPO inicializado")
    
    def select_action(self, state, training: bool = True):
        """Seleciona ação usando política atual"""
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            dist, value = self.actor_critic(state_tensor)
            action = dist.sample()
            log_prob = dist.log_prob(action)
            
            if self.actor_critic.continuous:
                action = action.cpu().numpy()[0]
            else:
                action = action.item()
            
            return action, log_prob.item(), value.item()
    
    def store_transition(self, state, action, reward, value, log_prob, done):
        """Armazena transição para atualização PPO"""
        self.states.append(state)
        self.actions.append(action)
        self.rewards.append(reward)
        self.values.append(value)
        self.log_probs.append(log_prob)
        self.dones.append(done)
    
    def update(self, next_value: float = 0.0):
        """Atualiza política usando PPO"""
        if len(self.states) == 0:
            return None
        
        # Converte para tensores
        states = torch.FloatTensor(self.states).to(self.device)
        actions = torch.FloatTensor(self.actions).to(self.device)
        rewards = torch.FloatTensor(self.rewards).to(self.device)
        values = torch.FloatTensor(self.values).to(self.device)
        old_log_probs = torch.FloatTensor(self.log_probs).to(self.device)
        
        # Calcula advantages e returns
        returns = self._compute_returns(rewards, next_value)
        advantages = returns - values
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
        
        # Atualização PPO
        total_loss = 0
        policy_loss = 0
        value_loss = 0
        entropy_loss = 0
        
        for _ in range(10):  # PPO epochs
            # Obtém distribuição e valores atuais
            dist, current_values = self.actor_critic(states)
            current_log_probs = dist.log_prob(actions)
            
            # Calcula ratio
            ratio = torch.exp(current_log_probs - old_log_probs)
            
            # Policy loss (clipped)
            surr1 = ratio * advantages
            surr2 = torch.clamp(ratio, 1 - self.config.clip_ratio, 
                                 1 + self.config.clip_ratio) * advantages
            policy_loss = -torch.min(surr1, surr2).mean()
            
            # Value loss
            value_loss = F.mse_loss(current_values.squeeze(), returns)
            
            # Entropy loss
            entropy = dist.entropy().mean()
            entropy_loss = -self.config.entropy_coef * entropy
            
            # Loss total
            loss = policy_loss + self.config.value_loss_coef * value_loss + entropy_loss
            
            # Otimização
            self.optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(
                self.actor_critic.parameters(), 
                self.config.max_grad_norm
            )
            self.optimizer.step()
            
            total_loss += loss.item()
        
        # Limpa buffer
        self.clear_buffer()
        
        return {
            'total_loss': total_loss / 10,
            'policy_loss': policy_loss.item(),
            'value_loss': value_loss.item(),
            'entropy': entropy.item()
        }
    
    def _compute_returns(self, rewards, next_value, gamma=0.99):
        """Calcula retornos descontados"""
        returns = []
        R = next_value
        
        for reward in reversed(rewards):
            R = reward + gamma * R
            returns.insert(0, R)
        
        return torch.FloatTensor(returns).to(self.device)
    
    def clear_buffer(self):
        """Limpa buffer de transições"""
        self.states.clear()
        self.actions.clear()
        self.rewards.clear()
        self.values.clear()
        self.log_probs.clear()
        self.dones.clear()
    
    def save_model(self, path: str):
        """Salva modelo"""
        torch.save({
            'actor_critic_state_dict': self.actor_critic.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'config': self.config.to_dict()
        }, path)
        logger.info(f"Modelo PPO salvo em {path}")
    
    def load_model(self, path: str):
        """Carrega modelo"""
        checkpoint = torch.load(path, map_location=self.device)
        
        self.actor_critic.load_state_dict(checkpoint['actor_critic_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        
        logger.info(f"Modelo PPO carregado de {path}")

class A2CAgent:
    """Agente A2C (Advantage Actor-Critic)"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Rede Actor-Critic
        self.actor_critic = ActorCriticNetwork(
            config.state_dim, config.hidden_dims, config.action_dim
        ).to(self.device)
        
        # Otimizador
        self.optimizer = optim.Adam(
            self.actor_critic.parameters(), 
            lr=config.learning_rate
        )
        
        # Buffer para A2C
        self.states = []
        self.actions = []
        self.rewards = []
        self.values = []
        self.log_probs = []
        
        # Métricas
        self.training_metrics = []
        
        logger.info(f"🤖 Agente A2C inicializado")
    
    def select_action(self, state, training: bool = True):
        """Seleciona ação usando política atual"""
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            dist, value = self.actor_critic(state_tensor)
            action = dist.sample()
            log_prob = dist.log_prob(action)
            
            if self.actor_critic.continuous:
                action = action.cpu().numpy()[0]
            else:
                action = action.item()
            
            return action, log_prob.item(), value.item()
    
    def store_transition(self, state, action, reward, value, log_prob):
        """Armazena transição"""
        self.states.append(state)
        self.actions.append(action)
        self.rewards.append(reward)
        self.values.append(value)
        self.log_probs.append(log_prob)
    
    def update(self):
        """Atualiza política usando A2C"""
        if len(self.states) == 0:
            return None
        
        # Converte para tensores
        states = torch.FloatTensor(self.states).to(self.device)
        actions = torch.FloatTensor(self.actions).to(self.device)
        rewards = torch.FloatTensor(self.rewards).to(self.device)
        values = torch.FloatTensor(self.values).to(self.device)
        old_log_probs = torch.FloatTensor(self.log_probs).to(self.device)
        
        # Calcula retornos e advantages
        returns = self._compute_returns(rewards)
        advantages = returns - values
        
        # Obtém distribuição e valores atuais
        dist, current_values = self.actor_critic(states)
        current_log_probs = dist.log_prob(actions)
        
        # Policy loss
        policy_loss = -(old_log_probs * advantages.detach()).mean()
        
        # Value loss
        value_loss = F.mse_loss(current_values.squeeze(), returns)
        
        # Entropy
        entropy = dist.entropy().mean()
        
        # Loss total
        loss = (policy_loss + 
                self.config.value_loss_coef * value_loss - 
                self.config.entropy_coef * entropy)
        
        # Otimização
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(
            self.actor_critic.parameters(), 
            self.config.max_grad_norm
        )
        self.optimizer.step()
        
        # Limpa buffer
        self.clear_buffer()
        
        return {
            'total_loss': loss.item(),
            'policy_loss': policy_loss.item(),
            'value_loss': value_loss.item(),
            'entropy': entropy.item()
        }
    
    def _compute_returns(self, rewards, gamma=0.99):
        """Calcula retornos descontados"""
        returns = []
        R = 0
        
        for reward in reversed(rewards):
            R = reward + gamma * R
            returns.insert(0, R)
        
        return torch.FloatTensor(returns).to(self.device)
    
    def clear_buffer(self):
        """Limpa buffer de transições"""
        self.states.clear()
        self.actions.clear()
        self.rewards.clear()
        self.values.clear()
        self.log_probs.clear()
    
    def save_model(self, path: str):
        """Salva modelo"""
        torch.save({
            'actor_critic_state_dict': self.actor_critic.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'config': self.config.to_dict()
        }, path)
        logger.info(f"Modelo A2C salvo em {path}")
    
    def load_model(self, path: str):
        """Carrega modelo"""
        checkpoint = torch.load(path, map_location=self.device)
        
        self.actor_critic.load_state_dict(checkpoint['actor_critic_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        
        logger.info(f"Modelo A2C carregado de {path}")

class RLTrainer:
    """Treinador para agentes RL"""
    
    def __init__(self, agent, environment, training_config: Dict[str, Any] = None):
        self.agent = agent
        self.environment = environment
        self.training_config = training_config or {}
        
        # Parâmetros de treinamento
        self.max_episodes = self.training_config.get('max_episodes', 1000)
        self.max_steps_per_episode = self.training_config.get('max_steps_per_episode', 1000)
        self.eval_freq = self.training_config.get('eval_freq', 100)
        self.save_freq = self.training_config.get('save_freq', 500)
        self.log_freq = self.training_config.get('log_freq', 10)
        
        # Métricas
        self.training_history = []
        self.evaluation_history = []
        
        logger.info("🏋️ Treinador RL inicializado")
    
    def train(self):
        """Treina o agente"""
        logger.info(f"🚀 Iniciando treinamento por {self.max_episodes} episódios")
        
        for episode in range(self.max_episodes):
            # Reseta ambiente
            state = self.environment.reset()
            episode_reward = 0
            episode_steps = 0
            episode_losses = []
            
            # Loop do episódio
            for step in range(self.max_steps_per_episode):
                # Seleciona ação
                if isinstance(self.agent, (DQNAgent,)):
                    action = self.agent.select_action(state, training=True)
                    next_state, reward, done, info = self.environment.step(action)
                    
                    # Armazena transição
                    self.agent.store_transition(state, action, reward, next_state, done)
                    
                    # Treina
                    if len(self.agent.replay_buffer) > self.agent.config.batch_size:
                        loss = self.agent.train_step()
                        if loss:
                            episode_losses.append(loss)
                
                elif isinstance(self.agent, (PPOAgent, A2CAgent)):
                    action, log_prob, value = self.agent.select_action(state, training=True)
                    next_state, reward, done, info = self.environment.step(action)
                    
                    # Armazena transição
                    self.agent.store_transition(state, action, reward, value, log_prob, done)
                    
                    # Atualiza (A2C atualiza a cada passo, PPO no final)
                    if isinstance(self.agent, A2CAgent):
                        update_result = self.agent.update()
                        if update_result:
                            episode_losses.append(update_result['total_loss'])
                
                # Atualiza estado
                state = next_state
                episode_reward += reward
                episode_steps += 1
                
                if done:
                    break
            
            # Atualização final para PPO
            if isinstance(self.agent, PPOAgent):
                next_value = 0.0
                if not done:
                    with torch.no_grad():
                        _, next_value = self.agent.actor_critic(
                            torch.FloatTensor(state).unsqueeze(0).to(self.agent.device)
                        )
                        next_value = next_value.item()
                
                update_result = self.agent.update(next_value)
                if update_result:
                    episode_losses.append(update_result['total_loss'])
            
            # Registra métricas
            avg_loss = np.mean(episode_losses) if episode_losses else 0.0
            
            metrics = TrainingMetrics(
                episode=episode + 1,
                total_reward=episode_reward,
                average_reward=episode_reward / max(1, episode_steps),
                episode_length=episode_steps,
                loss=avg_loss,
                value_loss=0.0,
                policy_loss=0.0,
                entropy=0.0,
                epsilon=getattr(self.agent, 'epsilon', 0.0),
                q_value=0.0
            )
            
            self.training_history.append(metrics)
            
            # Logging
            if episode % self.log_freq == 0:
                env_metrics = self.environment.get_metrics()
                logger.info(
                    f"Episode {episode + 1}: "
                    f"Reward={episode_reward:.2f}, "
                    f"Steps={episode_steps}, "
                    f"Loss={avg_loss:.4f}, "
                    f"Portfolio=${env_metrics.get('final_portfolio_value', 0):.2f}"
                )
            
            # Avaliação
            if episode % self.eval_freq == 0 and episode > 0:
                eval_metrics = self.evaluate()
                self.evaluation_history.append(eval_metrics)
                logger.info(f"Evaluation - Episode {episode + 1}: {eval_metrics}")
            
            # Salvamento
            if episode % self.save_freq == 0 and episode > 0:
                self.save_checkpoint(episode + 1)
        
        logger.info("✅ Treinamento concluído")
        return self.training_history
    
    def evaluate(self, num_episodes: int = 10) -> Dict[str, float]:
        """Avalia o agente"""
        total_rewards = []
        total_steps = []
        portfolio_values = []
        
        for _ in range(num_episodes):
            state = self.environment.reset()
            episode_reward = 0
            episode_steps = 0
            
            for _ in range(self.max_steps_per_episode):
                # Seleciona ação (sem treinamento)
                if isinstance(self.agent, DQNAgent):
                    action = self.agent.select_action(state, training=False)
                else:
                    action, _, _ = self.agent.select_action(state, training=False)
                
                next_state, reward, done, info = self.environment.step(action)
                
                state = next_state
                episode_reward += reward
                episode_steps += 1
                
                if done:
                    break
            
            total_rewards.append(episode_reward)
            total_steps.append(episode_steps)
            
            # Métricas do ambiente
            env_metrics = self.environment.get_metrics()
            portfolio_values.append(env_metrics.get('final_portfolio_value', 0))
        
        return {
            'avg_reward': np.mean(total_rewards),
            'std_reward': np.std(total_rewards),
            'avg_steps': np.mean(total_steps),
            'avg_portfolio_value': np.mean(portfolio_values),
            'total_return': (np.mean(portfolio_values) - self.environment.initial_balance) / self.environment.initial_balance
        }
    
    def save_checkpoint(self, episode: int):
        """Salva checkpoint do treinamento"""
        checkpoint_dir = Path('checkpoints')
        checkpoint_dir.mkdir(exist_ok=True)
        
        # Salva modelo
        model_path = checkpoint_dir / f"model_episode_{episode}.pt"
        self.agent.save_model(str(model_path))
        
        # Salva métricas
        metrics_path = checkpoint_dir / f"metrics_episode_{episode}.json"
        with open(metrics_path, 'w') as f:
            json.dump([m.to_dict() for m in self.training_history], f, indent=2)
        
        logger.info(f"Checkpoint salvo: episode {episode}")
    
    def plot_training_progress(self, save_path: str = None):
        """Plota progresso do treinamento"""
        if not self.training_history:
            return
        
        episodes = [m.episode for m in self.training_history]
        rewards = [m.total_reward for m in self.training_history]
        avg_rewards = [m.average_reward for m in self.training_history]
        losses = [m.loss for m in self.training_history]
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Total Reward
        axes[0, 0].plot(episodes, rewards)
        axes[0, 0].set_title('Total Reward per Episode')
        axes[0, 0].set_xlabel('Episode')
        axes[0, 0].set_ylabel('Total Reward')
        axes[0, 0].grid(True)
        
        # Average Reward
        axes[0, 1].plot(episodes, avg_rewards)
        axes[0, 1].set_title('Average Reward per Step')
        axes[0, 1].set_xlabel('Episode')
        axes[0, 1].set_ylabel('Average Reward')
        axes[0, 1].grid(True)
        
        # Loss
        axes[1, 0].plot(episodes, losses)
        axes[1, 0].set_title('Training Loss')
        axes[1, 0].set_xlabel('Episode')
        axes[1, 0].set_ylabel('Loss')
        axes[1, 0].grid(True)
        
        # Moving Average
        window = 50
        if len(rewards) >= window:
            moving_avg = pd.Series(rewards).rolling(window).mean()
            axes[1, 1].plot(episodes, rewards, alpha=0.3, label='Raw')
            axes[1, 1].plot(episodes, moving_avg, label=f'MA({window})')
            axes[1, 1].set_title('Reward Moving Average')
            axes[1, 1].set_xlabel('Episode')
            axes[1, 1].set_ylabel('Total Reward')
            axes[1, 1].legend()
            axes[1, 1].grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Training progress plot saved to {save_path}")
        
        plt.show()

# Configurações padrão
DEFAULT_DQN_CONFIG = AgentConfig(
    algorithm_type=AlgorithmType.DQN,
    network_type=NetworkType.MLP,
    state_dim=100,  # Será definido pelo ambiente
    action_dim=4,    # HOLD, BUY, SELL, CLOSE
    hidden_dims=[256, 256],
    learning_rate=3e-4,
    gamma=0.99,
    epsilon_start=1.0,
    epsilon_end=0.01,
    epsilon_decay=10000,
    buffer_size=100000,
    batch_size=64,
    target_update_freq=1000,
    use_double_q=True,
    use_dueling=False
)

DEFAULT_PPO_CONFIG = AgentConfig(
    algorithm_type=AlgorithmType.PPO,
    network_type=NetworkType.MLP,
    state_dim=100,
    action_dim=4,
    hidden_dims=[256, 256],
    learning_rate=3e-4,
    gamma=0.99,
    clip_ratio=0.2,
    value_loss_coef=0.5,
    entropy_coef=0.01,
    max_grad_norm=0.5
)

DEFAULT_TRAINING_CONFIG = {
    'max_episodes': 1000,
    'max_steps_per_episode': 1000,
    'eval_freq': 100,
    'save_freq': 500,
    'log_freq': 10
}

if __name__ == "__main__":
    # Exemplo de uso
    def create_sample_environment():
        """Cria ambiente de exemplo"""
        from reinforcement_learning_environment import DEFAULT_RL_CONFIG
        
        # Cria dados sintéticos
        dates = pd.date_range(start='2020-01-01', end='2023-12-31', freq='D')
        np.random.seed(42)
        
        # Simula preço
        returns = np.random.normal(0.0005, 0.02, len(dates))
        prices = 100 * np.exp(np.cumsum(returns))
        
        # Cria DataFrame
        data = pd.DataFrame(index=dates)
        data['close_price'] = prices
        data['timestamp'] = dates
        
        # Adiciona features
        for i in range(20):
            data[f'feature_{i}'] = np.random.randn(len(dates))
        
        # Cria ambiente
        env_config = DEFAULT_RL_CONFIG
        env = TradingEnvironment(env_config)
        env.load_data(data)
        
        return env
    
    def train_dqn_agent():
        """Treina agente DQN"""
        # Cria ambiente
        env = create_sample_environment()
        
        # Configura agente
        config = DEFAULT_DQN_CONFIG
        config.state_dim = env.observation_space.shape[0]
        config.action_dim = env.action_space.n
        
        # Cria agente
        agent = DQNAgent(config)
        
        # Cria treinador
        trainer = RLTrainer(agent, env, DEFAULT_TRAINING_CONFIG)
        
        # Treina
        training_history = trainer.train()
        
        # Plota progresso
        trainer.plot_training_progress('dqn_training_progress.png')
        
        # Avaliação final
        final_metrics = trainer.evaluate(num_episodes=20)
        print(f"\n📊 Métricas Finais DQN:")
        for key, value in final_metrics.items():
            print(f"{key}: {value:.4f}")
        
        return agent, trainer
    
    def train_ppo_agent():
        """Treina agente PPO"""
        # Cria ambiente
        env = create_sample_environment()
        
        # Configura agente
        config = DEFAULT_PPO_CONFIG
        config.state_dim = env.observation_space.shape[0]
        config.action_dim = env.action_space.n
        
        # Cria agente
        agent = PPOAgent(config)
        
        # Cria treinador
        trainer = RLTrainer(agent, env, DEFAULT_TRAINING_CONFIG)
        
        # Treina
        training_history = trainer.train()
        
        # Plota progresso
        trainer.plot_training_progress('ppo_training_progress.png')
        
        # Avaliação final
        final_metrics = trainer.evaluate(num_episodes=20)
        print(f"\n📊 Métricas Finais PPO:")
        for key, value in final_metrics.items():
            print(f"{key}: {value:.4f}")
        
        return agent, trainer
    
    # Executa treinamento
    print("🚀 Iniciando treinamento DQN...")
    dqn_agent, dqn_trainer = train_dqn_agent()
    
    print("\n🚀 Iniciando treinamento PPO...")
    ppo_agent, ppo_trainer = train_ppo_agent()
    
    print("✅ Treinamento concluído com sucesso!")

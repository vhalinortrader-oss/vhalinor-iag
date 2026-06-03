"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                      VHALINOR IAG 5.0 - VISUALIZADOR QUÂNTICO AVANÇADO    ║
║         VISUALIZAÇÃO 3D/2D DE REDE NEURAL COM IA INTEGRADA E TEMPO REAL       ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  Módulo: VISUALIZADOR DE REDE NEURAL AVANÇADO                                ║
║  Versão: 5.0.0 (Enhanced with AI Integration - Production Ready)              ║
║  Autor: Alex Miranda Sales                                                    ║
║  Data: 2026                                                                   ║
║  License: Proprietary - Vhalinor IAG Systems                                  ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

# =============================================================================
# IMPORTAÇÕES AVANÇADAS COM FALLBACKS E SUPORTE AI/ML
# =============================================================================

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, colorchooser, filedialog
import json
import os
import sys
import math
import random
import hashlib
import pickle
import threading
import time
import asyncio
import uuid
import logging
import warnings
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any, Union, Set, Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import defaultdict, deque
from functools import lru_cache, wraps
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# =============================================================================
# IMPORTAÇÕES DE IA/ML COM FALLBACK GRACIOSO
# =============================================================================

# Frameworks de Deep Learning
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    import torch.nn.functional as F
    from torch.utils.data import DataLoader, Dataset
    HAS_TORCH = True
    TORCH_VERSION = torch.__version__
except ImportError:
    HAS_TORCH = False
    TORCH_VERSION = None
    torch = None
    nn = None
    optim = None
    F = None

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers, models, optimizers
    HAS_TENSORFLOW = True
    TF_VERSION = tf.__version__
except ImportError:
    HAS_TENSORFLOW = False
    TF_VERSION = None
    tf = None
    keras = None
    layers = None
    models = None
    optimizers = None

# Machine Learning tradicional
try:
    import sklearn
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
    from sklearn.neural_network import MLPClassifier, MLPRegressor
    from sklearn.preprocessing import StandardScaler, MinMaxScaler
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.metrics import accuracy_score, mean_squared_error, classification_report
    HAS_SKLEARN = True
    SKLEARN_VERSION = sklearn.__version__
except ImportError:
    HAS_SKLEARN = False
    SKLEARN_VERSION = None

# Processamento de dados e computação científica
try:
    import numpy as np
    import pandas as pd
    import scipy
    from scipy import stats, signal
    HAS_NUMPY = True
    NUMPY_AVAILABLE = True
    NUMPY_VERSION = np.__version__
    HAS_PANDAS = True
    HAS_SCIPY = True
except ImportError:
    HAS_NUMPY = False
    NUMPY_AVAILABLE = False
    HAS_PANDAS = False
    HAS_SCIPY = False
    NUMPY_VERSION = None
    np = None
    pd = None
    scipy = None
    stats = None
    signal = None

# Visualização avançada
try:
    import matplotlib
    matplotlib.use('TkAgg')
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
    from matplotlib.figure import Figure
    import matplotlib.patches as mpatches
    from matplotlib.colors import LinearSegmentedColormap, Normalize
    import matplotlib.animation as animation
    from mpl_toolkits.mplot3d import Axes3D
    MATPLOTLIB_AVAILABLE = True
    MATPLOTLIB_3D = True
    MATPLOTLIB_VERSION = matplotlib.__version__
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    MATPLOTLIB_3D = False
    MATPLOTLIB_VERSION = None

# Análise de grafos
try:
    import networkx as nx
    from networkx.algorithms import community, centrality, shortest_path
    HAS_NETWORKX = True
    NETWORKX_AVAILABLE = True
    NETWORKX_VERSION = nx.__version__
except ImportError:
    HAS_NETWORKX = False
    NETWORKX_AVAILABLE = False
    NETWORKX_VERSION = None

# Processamento de imagem
try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    PIL_AVAILABLE = True
    PIL_VERSION = Image.__version__
except ImportError:
    PIL_AVAILABLE = False
    PIL_VERSION = None

# Rede e tempo real
try:
    import websockets
    import aiohttp
    import asyncio
    HAS_WEBSOCKETS = True
    HAS_AIOHTTP = True
except ImportError:
    HAS_WEBSOCKETS = False
    HAS_AIOHTTP = False

# Configurar logging avançado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vhalinor_neural_visualizer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURAÇÕES E CONSTANTES AVANÇADAS
# =============================================================================

class VisualizationMode(Enum):
    """Modos de visualização da rede"""
    AUTO = auto()          # Auto-detecção
    FORCE_2D = auto()      # Forçar 2D
    FORCE_3D = auto()      # Forçar 3D (se disponível)
    SPRING = auto()        # Layout spring (networkx)
    CIRCULAR = auto()      # Layout circular
    SPECTRAL = auto()      # Layout spectral
    HIERARCHICAL = auto()  # Layout hierárquico
    FORCE = auto()         # Layout force-directed

class NodeShape(Enum):
    """Formatos dos nós"""
    CIRCLE = 'o'
    SQUARE = 's'
    DIAMOND = 'D'
    TRIANGLE = '^'
    STAR = '*'
    HEXAGON = 'h'

class EdgeStyle(Enum):
    """Estilos das arestas"""
    SOLID = '-'
    DASHED = '--'
    DOTTED = ':'
    DASHDOT = '-.'

class AnimationSpeed(Enum):
    """Velocidades de animação"""
    SLOW = 2000
    NORMAL = 1000
    FAST = 500
    VERY_FAST = 200
    REAL_TIME = 50

class Theme(Enum):
    """Temas de cores"""
    DARK = 'dark'
    LIGHT = 'light'
    BLUE = 'blue'
    GREEN = 'green'
    PURPLE = 'purple'
    QUANTUM = 'quantum'
    CUSTOM = 'custom'

# =============================================================================
# ESTRUTURAS DE DADOS OTIMIZADAS
# =============================================================================

@dataclass
class Neuron:
    """Representação de um neurônio com dados completos"""
    id: int
    name: str
    type: str
    layer: str
    layer_index: int = 0
    activation: float = 0.0
    bias: float = 0.0
    connections: List[int] = field(default_factory=list)
    position_2d: Tuple[float, float] = (0, 0)
    position_3d: Tuple[float, float, float] = (0, 0, 0)
    color: str = '#CCCCCC'
    size: float = 1.0
    importance: float = 1.0
    error: float = 0.0
    gradient: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário serializável"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'layer': self.layer,
            'layer_index': self.layer_index,
            'activation': self.activation,
            'bias': self.bias,
            'connections': self.connections,
            'position_2d': self.position_2d,
            'position_3d': self.position_3d,
            'color': self.color,
            'size': self.size,
            'importance': self.importance,
            'error': self.error,
            'gradient': self.gradient,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }

@dataclass
class Connection:
    """Representação de uma conexão entre neurônios"""
    source: int
    target: int
    weight: float = 1.0
    strength: float = 1.0
    type: str = 'forward'
    recurrent: bool = False
    enabled: bool = True
    color: str = '#00FF00'
    style: str = '-'
    width: float = 1.0
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário serializável"""
        return {
            'source': self.source,
            'target': self.target,
            'weight': self.weight,
            'strength': self.strength,
            'type': self.type,
            'recurrent': self.recurrent,
            'enabled': self.enabled,
            'color': self.color,
            'style': self.style,
            'width': self.width,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }

@dataclass
class NetworkStatistics:
    """Estatísticas completas da rede"""
    total_neurons: int = 0
    total_connections: int = 0
    total_layers: int = 0
    neurons_by_type: Dict[str, int] = field(default_factory=dict)
    neurons_by_layer: Dict[str, int] = field(default_factory=dict)
    connections_by_type: Dict[str, int] = field(default_factory=dict)
    avg_activation: float = 0.0
    max_activation: float = 0.0
    min_activation: float = 0.0
    avg_weight: float = 0.0
    max_weight: float = 0.0
    min_weight: float = 0.0
    density: float = 0.0
    clustering_coefficient: float = 0.0
    avg_path_length: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário serializável"""
        return {
            'total_neurons': self.total_neurons,
            'total_connections': self.total_connections,
            'total_layers': self.total_layers,
            'neurons_by_type': self.neurons_by_type,
            'neurons_by_layer': self.neurons_by_layer,
            'connections_by_type': self.connections_by_type,
            'avg_activation': self.avg_activation,
            'max_activation': self.max_activation,
            'min_activation': self.min_activation,
            'avg_weight': self.avg_weight,
            'max_weight': self.max_weight,
            'min_weight': self.min_weight,
            'density': self.density,
            'clustering_coefficient': self.clustering_coefficient,
            'avg_path_length': self.avg_path_length,
            'timestamp': self.timestamp.isoformat()
        }

# =============================================================================
# SISTEMA DE LOGGING VISUAL
# =============================================================================

class VisualLogger:
    """Sistema de logging com níveis e cores"""
    
    COLORS = {
        'DEBUG': '#808080',
        'INFO': '#00FF00',
        'WARNING': '#FFFF00',
        'ERROR': '#FF0000',
        'CRITICAL': '#FF00FF',
        'SUCCESS': '#00FFFF'
    }
    
    def __init__(self, text_widget: Optional[scrolledtext.ScrolledText] = None):
        self.text_widget = text_widget
        self.logs = deque(maxlen=1000)
        self.handlers = []
        self.level = 'INFO'
        
    def debug(self, message: str):
        if self._should_log('DEBUG'):
            self._log('DEBUG', message)
    
    def info(self, message: str):
        if self._should_log('INFO'):
            self._log('INFO', message)
    
    def warning(self, message: str):
        if self._should_log('WARNING'):
            self._log('WARNING', message)
    
    def error(self, message: str):
        if self._should_log('ERROR'):
            self._log('ERROR', message)
    
    def critical(self, message: str):
        if self._should_log('CRITICAL'):
            self._log('CRITICAL', message)
    
    def success(self, message: str):
        if self._should_log('INFO'):
            self._log('SUCCESS', message)
    
    def _should_log(self, level: str) -> bool:
        levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        return levels.index(level) >= levels.index(self.level)
    
    def _log(self, level: str, message: str):
        timestamp = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        log_entry = f"[{timestamp}] [{level}] {message}"
        
        self.logs.append(log_entry)
        
        # Console output
        print(log_entry)
        
        # GUI output
        if self.text_widget:
            self.text_widget.insert(tk.END, f"[{timestamp}] ", 'timestamp')
            self.text_widget.insert(tk.END, f"[{level}] ", f'log_{level.lower()}')
            self.text_widget.insert(tk.END, f"{message}\n", 'log_message')
            self.text_widget.see(tk.END)
        
        # Handlers
        for handler in self.handlers:
            handler(log_entry)
    
    def add_handler(self, handler: Callable):
        self.handlers.append(handler)
    
    def get_recent(self, n: int = 100) -> List[str]:
        return list(self.logs)[-n:]

# =============================================================================
# GERADOR DE DADOS SINTÉTICOS AVANÇADO
# =============================================================================

class NetworkDataGenerator:
    """Gerador avançado de dados para rede neural"""
    
    # Arquiteturas predefinidas
    ARCHITECTURES = {
        'vhalinor_quantum': {
            'name': 'VHALINOR Quantum Core',
            'layers': [
                {'name': 'Quantum Input', 'neurons': 8, 'types': ['quantum', 'sensory']},
                {'name': 'Quantum Processing', 'neurons': 16, 'types': ['quantum', 'processing']},
                {'name': 'Neural Matrix', 'neurons': 32, 'types': ['processing', 'memory']},
                {'name': 'Decision Layer', 'neurons': 16, 'types': ['decision', 'analytical']},
                {'name': 'Quantum Output', 'neurons': 4, 'types': ['output', 'api']}
            ],
            'connections_per_layer': 0.6,
            'recurrent_probability': 0.1
        },
        'deep_learning': {
            'name': 'Deep Learning Network',
            'layers': [
                {'name': 'Input', 'neurons': 10, 'types': ['sensory']},
                {'name': 'Hidden 1', 'neurons': 64, 'types': ['processing']},
                {'name': 'Hidden 2', 'neurons': 128, 'types': ['processing']},
                {'name': 'Hidden 3', 'neurons': 64, 'types': ['processing']},
                {'name': 'Output', 'neurons': 5, 'types': ['output']}
            ],
            'connections_per_layer': 0.8,
            'recurrent_probability': 0.05
        },
        'lstm_memory': {
            'name': 'LSTM Memory Network',
            'layers': [
                {'name': 'Input Gate', 'neurons': 12, 'types': ['sensory']},
                {'name': 'Forget Gate', 'neurons': 12, 'types': ['memory']},
                {'name': 'Cell State', 'neurons': 24, 'types': ['memory', 'processing']},
                {'name': 'Output Gate', 'neurons': 12, 'types': ['processing']},
                {'name': 'Output', 'neurons': 6, 'types': ['output']}
            ],
            'connections_per_layer': 0.7,
            'recurrent_probability': 0.3
        },
        'convolutional': {
            'name': 'Convolutional Network',
            'layers': [
                {'name': 'Input', 'neurons': 16, 'types': ['sensory']},
                {'name': 'Conv Layer 1', 'neurons': 32, 'types': ['processing']},
                {'name': 'Pooling 1', 'neurons': 16, 'types': ['processing']},
                {'name': 'Conv Layer 2', 'neurons': 64, 'types': ['processing']},
                {'name': 'Pooling 2', 'neurons': 32, 'types': ['processing']},
                {'name': 'Dense', 'neurons': 128, 'types': ['processing', 'memory']},
                {'name': 'Output', 'neurons': 10, 'types': ['output']}
            ],
            'connections_per_layer': 0.5,
            'recurrent_probability': 0.0
        }
    }
    
    # Tipos de neurônios disponíveis
    NEURON_TYPES = {
        'sensory': {'color': '#FF6B6B', 'size': 1.0, 'importance': 1.2},
        'processing': {'color': '#4ECDC4', 'size': 0.9, 'importance': 1.0},
        'memory': {'color': '#95E1D3', 'size': 1.1, 'importance': 1.3},
        'decision': {'color': '#FFD93D', 'size': 1.0, 'importance': 1.5},
        'output': {'color': '#6BCB77', 'size': 1.0, 'importance': 1.2},
        'quantum': {'color': '#9D4EDD', 'size': 1.2, 'importance': 1.8},
        'analytical': {'color': '#3A86FF', 'size': 0.9, 'importance': 1.1},
        'security': {'color': '#FB5607', 'size': 1.0, 'importance': 1.4},
        'api': {'color': '#8338EC', 'size': 0.8, 'importance': 1.0},
        'database': {'color': '#06FFA5', 'size': 1.0, 'importance': 1.2},
        'control': {'color': '#FF006E', 'size': 1.0, 'importance': 1.3},
        'feedback': {'color': '#00BBF9', 'size': 0.9, 'importance': 1.1}
    }
    
    @classmethod
    def generate_network(cls, architecture: str = 'vhalinor_quantum', 
                        seed: Optional[int] = None) -> Tuple[Dict[int, Neuron], List[Connection], Dict[str, List[int]]]:
        """Gerar rede neural completa baseada em arquitetura"""
        
        if seed is not None:
            random.seed(seed)
            if NUMPY_AVAILABLE:
                np.random.seed(seed)
        
        arch = cls.ARCHITECTURES.get(architecture, cls.ARCHITECTURES['vhalinor_quantum'])
        
        neurons = {}
        layers = {}
        neuron_id = 0
        
        # Criar neurônios por camada
        for layer_idx, layer_config in enumerate(arch['layers']):
            layer_name = layer_config['name']
            layers[layer_name] = []
            
            for i in range(layer_config['neurons']):
                # Escolher tipo baseado nas opções disponíveis
                neuron_type = random.choice(layer_config['types'])
                type_config = cls.NEURON_TYPES.get(neuron_type, 
                                                   {'color': '#CCCCCC', 'size': 1.0, 'importance': 1.0})
                
                # Nome do neurônio
                if neuron_type == 'quantum':
                    base_name = f"qbit_{chr(97 + i % 26)}{i//26}"
                elif neuron_type == 'memory':
                    base_name = f"mem_cell_{i:03d}"
                elif neuron_type == 'processing':
                    base_name = f"proc_unit_{i:03d}"
                else:
                    base_name = f"{neuron_type[:3]}_{i:03d}"
                
                neuron = Neuron(
                    id=neuron_id,
                    name=base_name,
                    type=neuron_type,
                    layer=layer_name,
                    layer_index=layer_idx,
                    activation=random.uniform(0.1, 0.9),
                    bias=random.uniform(-0.5, 0.5),
                    color=type_config['color'],
                    size=type_config['size'],
                    importance=type_config['importance'] * random.uniform(0.8, 1.2),
                    error=random.uniform(0, 0.1),
                    gradient=random.uniform(-0.1, 0.1),
                    metadata={'generated': True, 'architecture': architecture}
                )
                
                neurons[neuron_id] = neuron
                layers[layer_name].append(neuron_id)
                neuron_id += 1
        
        # Criar conexões
        connections = []
        layer_names = list(layers.keys())
        
        for i in range(len(layer_names) - 1):
            current_layer = layers[layer_names[i]]
            next_layer = layers[layer_names[i + 1]]
            
            # Conectividade baseada na configuração
            connectivity = arch['connections_per_layer']
            
            for source_id in current_layer:
                # Número de conexões baseado na importância do neurônio
                num_connections = max(1, int(len(next_layer) * connectivity * 
                                           neurons[source_id].importance))
                num_connections = min(num_connections, len(next_layer))
                
                # Selecionar targets
                if random.random() < 0.7:  # Preferência por conexões fortes
                    targets = random.sample(next_layer, num_connections)
                else:
                    # Selecionar baseado em pesos
                    weights = [neurons[t].importance for t in next_layer]
                    total = sum(weights)
                    probs = [w/total for w in weights]
                    targets = random.choices(next_layer, weights=probs, k=num_connections)
                
                for target_id in targets:
                    weight = random.uniform(0.1, 1.0)
                    strength = weight * random.uniform(0.8, 1.2)
                    
                    connection = Connection(
                        source=source_id,
                        target=target_id,
                        weight=weight,
                        strength=strength,
                        type='forward',
                        recurrent=False,
                        enabled=True,
                        color='#00FF00',
                        style='-',
                        width=weight * 2,
                        metadata={'generated': True}
                    )
                    
                    connections.append(connection)
                    neurons[source_id].connections.append(target_id)
        
        # Adicionar conexões recorrentes
        if arch['recurrent_probability'] > 0:
            for _ in range(int(len(neurons) * arch['recurrent_probability'])):
                source = random.choice(list(neurons.keys()))
                target = random.choice(list(neurons.keys()))
                
                if source != target and target not in neurons[source].connections:
                    weight = random.uniform(0.1, 0.5)
                    
                    connection = Connection(
                        source=source,
                        target=target,
                        weight=weight,
                        strength=weight * 0.8,
                        type='recurrent',
                        recurrent=True,
                        enabled=True,
                        color='#FF00FF',
                        style='--',
                        width=weight,
                        metadata={'generated': True, 'recurrent': True}
                    )
                    
                    connections.append(connection)
                    neurons[source].connections.append(target)
        
        return neurons, connections, layers
    
    @classmethod
    def generate_from_lex_iag(cls) -> Tuple[Dict[int, Neuron], List[Connection], Dict[str, List[int]]]:
        """Gerar rede específica do LEX IAG baseada nos arquivos do sistema"""
        
        # Arquitetura do LEX IAG baseada nos módulos reais
        neurons = {}
        connections = []
        layers = {
            'Input': [],
            'Analysis': [],
            'Memory': [],
            'Quantum': [],
            'Decision': [],
            'Output': []
        }
        
        neuron_id = 0
        
        # ===== CAMADA DE ENTRADA =====
        input_neurons = [
            ('market_data', 'sensory'),
            ('crypto_analysis', 'sensory'),
            ('forex_analysis', 'sensory'),
            ('arbitrage_analysis', 'sensory'),
            ('sentiment_analysis', 'sensory'),
            ('news_processor', 'sensory')
        ]
        
        for name, ntype in input_neurons:
            neurons[neuron_id] = Neuron(
                id=neuron_id,
                name=name,
                type=ntype,
                layer='Input',
                layer_index=0,
                activation=random.uniform(0.5, 0.9),
                color=cls.NEURON_TYPES[ntype]['color'],
                importance=1.2,
                metadata={'module': f'input_{name}'}
            )
            layers['Input'].append(neuron_id)
            neuron_id += 1
        
        # ===== CAMADA DE ANÁLISE =====
        analysis_neurons = [
            ('data_analyzer', 'analytical'),
            ('pattern_recognizer', 'analytical'),
            ('technical_analyzer', 'analytical'),
            ('risk_analyzer', 'analytical'),
            ('statistical_analyzer', 'analytical'),
            ('ml_analyzer', 'processing')
        ]
        
        for name, ntype in analysis_neurons:
            neurons[neuron_id] = Neuron(
                id=neuron_id,
                name=name,
                type=ntype,
                layer='Analysis',
                layer_index=1,
                activation=random.uniform(0.4, 0.8),
                color=cls.NEURON_TYPES[ntype]['color'],
                importance=1.3,
                metadata={'module': f'analysis_{name}'}
            )
            layers['Analysis'].append(neuron_id)
            neuron_id += 1
        
        # ===== CAMADA DE MEMÓRIA =====
        memory_neurons = [
            ('advanced_memory', 'memory'),
            ('neural_connection_matrix', 'memory'),
            ('brain_memory_db', 'database'),
            ('cache_system', 'memory'),
            ('experience_replay', 'memory')
        ]
        
        for name, ntype in memory_neurons:
            neurons[neuron_id] = Neuron(
                id=neuron_id,
                name=name,
                type=ntype,
                layer='Memory',
                layer_index=2,
                activation=random.uniform(0.3, 0.7),
                color=cls.NEURON_TYPES[ntype]['color'],
                importance=1.4,
                metadata={'module': f'memory_{name}'}
            )
            layers['Memory'].append(neuron_id)
            neuron_id += 1
        
        # ===== CAMADA QUÂNTICA =====
        quantum_neurons = [
            ('quantum_core', 'quantum'),
            ('quantum_algorithms', 'quantum'),
            ('quantum_processor', 'quantum'),
            ('qubit_controller', 'quantum'),
            ('quantum_memory', 'quantum')
        ]
        
        for name, ntype in quantum_neurons:
            neurons[neuron_id] = Neuron(
                id=neuron_id,
                name=name,
                type=ntype,
                layer='Quantum',
                layer_index=3,
                activation=random.uniform(0.6, 0.95),
                color=cls.NEURON_TYPES[ntype]['color'],
                importance=1.8,
                metadata={'module': f'quantum_{name}'}
            )
            layers['Quantum'].append(neuron_id)
            neuron_id += 1
        
        # ===== CAMADA DE DECISÃO =====
        decision_neurons = [
            ('decision_engine', 'decision'),
            ('autonomous_manager', 'decision'),
            ('strategy_selector', 'decision'),
            ('risk_manager', 'decision'),
            ('execution_controller', 'control')
        ]
        
        for name, ntype in decision_neurons:
            neurons[neuron_id] = Neuron(
                id=neuron_id,
                name=name,
                type=ntype,
                layer='Decision',
                layer_index=4,
                activation=random.uniform(0.5, 0.85),
                color=cls.NEURON_TYPES[ntype]['color'],
                importance=1.5,
                metadata={'module': f'decision_{name}'}
            )
            layers['Decision'].append(neuron_id)
            neuron_id += 1
        
        # ===== CAMADA DE SAÍDA =====
        output_neurons = [
            ('autotrader', 'output'),
            ('trading_controller', 'output'),
            ('api_interface', 'api'),
            ('report_generator', 'output'),
            ('alert_system', 'output')
        ]
        
        for name, ntype in output_neurons:
            neurons[neuron_id] = Neuron(
                id=neuron_id,
                name=name,
                type=ntype,
                layer='Output',
                layer_index=5,
                activation=random.uniform(0.4, 0.8),
                color=cls.NEURON_TYPES[ntype]['color'],
                importance=1.2,
                metadata={'module': f'output_{name}'}
            )
            layers['Output'].append(neuron_id)
            neuron_id += 1
        
        # ===== CRIAR CONEXÕES =====
        layer_order = ['Input', 'Analysis', 'Memory', 'Quantum', 'Decision', 'Output']
        
        # Conexões feedforward
        for i in range(len(layer_order) - 1):
            current_layer = layers[layer_order[i]]
            next_layer = layers[layer_order[i + 1]]
            
            for source_id in current_layer:
                # Conectar com 30-70% dos neurônios da próxima camada
                num_connections = max(2, int(len(next_layer) * random.uniform(0.3, 0.7)))
                targets = random.sample(next_layer, min(num_connections, len(next_layer)))
                
                for target_id in targets:
                    weight = random.uniform(0.3, 1.0)
                    connection = Connection(
                        source=source_id,
                        target=target_id,
                        weight=weight,
                        strength=weight,
                        type='forward',
                        color='#00FF00',
                        width=weight * 1.5
                    )
                    connections.append(connection)
                    neurons[source_id].connections.append(target_id)
        
        # Conexões recorrentes (feedback)
        for _ in range(15):
            source = random.choice(layers['Decision'] + layers['Output'])
            target = random.choice(layers['Analysis'] + layers['Memory'])
            
            weight = random.uniform(0.1, 0.4)
            connection = Connection(
                source=source,
                target=target,
                weight=weight,
                strength=weight,
                type='recurrent',
                recurrent=True,
                color='#FF00FF',
                style='--',
                width=weight
            )
            connections.append(connection)
            neurons[source].connections.append(target)
        
        # Conexões quânticas especiais
        quantum_layer = layers['Quantum']
        for source_id in quantum_layer:
            for target_id in quantum_layer:
                if source_id != target_id and random.random() < 0.2:
                    weight = random.uniform(0.5, 1.0)
                    connection = Connection(
                        source=source_id,
                        target=target_id,
                        weight=weight,
                        strength=weight * 1.2,
                        type='quantum_entanglement',
                        recurrent=True,
                        color='#9D4EDD',
                        style=':',
                        width=weight
                    )
                    connections.append(connection)
                    neurons[source_id].connections.append(target_id)
        
        return neurons, connections, layers

# =============================================================================
# CALCULADOR DE POSIÇÕES AVANÇADO
# =============================================================================

class PositionCalculator:
    """Calculador avançado de posições para visualização"""
    
    @staticmethod
    def hierarchical_layout(layers: Dict[str, List[int]], 
                           neurons: Dict[int, Neuron],
                           width: float = 1.0,
                           height: float = 1.0,
                           spacing: float = 0.15) -> Dict[int, Tuple[float, float]]:
        """Layout hierárquico em camadas verticais"""
        positions = {}
        layer_names = list(layers.keys())
        layer_width = width / (len(layer_names) + 1)
        
        for i, layer_name in enumerate(layer_names):
            layer_neurons = layers[layer_name]
            x = (i + 1) * layer_width
            
            if len(layer_neurons) > 0:
                # Ordenar neurônios por importância
                sorted_neurons = sorted(layer_neurons, 
                                      key=lambda n: neurons[n].importance,
                                      reverse=True)
                
                y_spacing = (height - 2 * spacing) / len(layer_neurons)
                y_start = spacing
                
                for j, neuron_id in enumerate(sorted_neurons):
                    y = y_start + (j + 0.5) * y_spacing
                    positions[neuron_id] = (x, y)
                    neurons[neuron_id].position_2d = (x, y)
        
        return positions
    
    @staticmethod
    def circular_layout(neurons: Dict[int, Neuron],
                       center: Tuple[float, float] = (0.5, 0.5),
                       radius: float = 0.4) -> Dict[int, Tuple[float, float]]:
        """Layout circular para visualização de comunidade"""
        positions = {}
        n = len(neurons)
        
        for i, neuron_id in enumerate(neurons.keys()):
            angle = 2 * math.pi * i / n
            x = center[0] + radius * math.cos(angle)
            y = center[1] + radius * math.sin(angle)
            positions[neuron_id] = (x, y)
            neurons[neuron_id].position_2d = (x, y)
        
        return positions
    
    @staticmethod
    def spring_layout(neurons: Dict[int, Neuron],
                     connections: List[Connection],
                     iterations: int = 50,
                     k: float = 0.1) -> Dict[int, Tuple[float, float]]:
        """Layout spring (force-directed) usando NetworkX"""
        if not NETWORKX_AVAILABLE:
            return PositionCalculator.hierarchical_layout(
                PositionCalculator._group_by_layer(neurons), neurons
            )
        
        G = nx.Graph()
        
        for neuron_id in neurons:
            G.add_node(neuron_id)
        
        for conn in connections:
            G.add_edge(conn.source, conn.target, weight=conn.weight)
        
        try:
            pos = nx.spring_layout(G, iterations=iterations, k=k)
            
            # Normalizar para [0, 1]
            x_vals = [p[0] for p in pos.values()]
            y_vals = [p[1] for p in pos.values()]
            
            x_min, x_max = min(x_vals), max(x_vals)
            y_min, y_max = min(y_vals), max(y_vals)
            
            x_range = max(x_max - x_min, 0.01)
            y_range = max(y_max - y_min, 0.01)
            
            positions = {}
            for neuron_id, p in pos.items():
                x = (p[0] - x_min) / x_range
                y = (p[1] - y_min) / y_range
                positions[neuron_id] = (x, y)
                neurons[neuron_id].position_2d = (x, y)
            
            return positions
            
        except:
            return PositionCalculator.hierarchical_layout(
                PositionCalculator._group_by_layer(neurons), neurons
            )
    
    @staticmethod
    def spectral_layout(neurons: Dict[int, Neuron],
                       connections: List[Connection]) -> Dict[int, Tuple[float, float]]:
        """Layout spectral usando autovetores"""
        if not NETWORKX_AVAILABLE:
            return PositionCalculator.hierarchical_layout(
                PositionCalculator._group_by_layer(neurons), neurons
            )
        
        G = nx.Graph()
        
        for neuron_id in neurons:
            G.add_node(neuron_id)
        
        for conn in connections:
            G.add_edge(conn.source, conn.target)
        
        try:
            pos = nx.spectral_layout(G)
            
            # Normalizar
            x_vals = [p[0] for p in pos.values()]
            y_vals = [p[1] for p in pos.values()]
            
            x_min, x_max = min(x_vals), max(x_vals)
            y_min, y_max = min(y_vals), max(y_vals)
            
            x_range = max(x_max - x_min, 0.01)
            y_range = max(y_max - y_min, 0.01)
            
            positions = {}
            for neuron_id, p in pos.items():
                x = (p[0] - x_min) / x_range
                y = (p[1] - y_min) / y_range
                positions[neuron_id] = (x, y)
                neurons[neuron_id].position_2d = (x, y)
            
            return positions
            
        except:
            return PositionCalculator.hierarchical_layout(
                PositionCalculator._group_by_layer(neurons), neurons
            )
    
    @staticmethod
    def _group_by_layer(neurons: Dict[int, Neuron]) -> Dict[str, List[int]]:
        """Agrupar neurônios por camada"""
        layers = {}
        for neuron_id, neuron in neurons.items():
            if neuron.layer not in layers:
                layers[neuron.layer] = []
            layers[neuron.layer].append(neuron_id)
        return layers
    
    @staticmethod
    def calculate_3d_positions(layers: Dict[str, List[int]],
                              neurons: Dict[int, Neuron],
                              width: float = 1.0,
                              height: float = 1.0,
                              depth: float = 0.5) -> Dict[int, Tuple[float, float, float]]:
        """Calcular posições 3D para visualização"""
        positions = {}
        layer_names = list(layers.keys())
        layer_spacing = width / (len(layer_names) + 1)
        
        for i, layer_name in enumerate(layer_names):
            layer_neurons = layers[layer_name]
            x = (i + 1) * layer_spacing - 0.5  # Centralizar
            
            if len(layer_neurons) > 0:
                # Disposição em grid 2D dentro da camada
                cols = int(math.sqrt(len(layer_neurons))) or 1
                rows = (len(layer_neurons) + cols - 1) // cols
                
                cell_width = height / (cols + 1)
                cell_height = depth / (rows + 1)
                
                for j, neuron_id in enumerate(layer_neurons):
                    col = j % cols
                    row = j // cols
                    
                    y = (col + 1) * cell_width - 0.5
                    z = (row + 1) * cell_height - 0.25
                    
                    positions[neuron_id] = (x, y, z)
                    neurons[neuron_id].position_3d = (x, y, z)
        
        return positions

# =============================================================================
# ANALISADOR DE REDE AVANÇADO
# =============================================================================

class NetworkAnalyzer:
    """Analisador avançado de redes neurais"""
    
    @staticmethod
    def calculate_statistics(neurons: Dict[int, Neuron],
                            connections: List[Connection]) -> NetworkStatistics:
        """Calcular estatísticas completas da rede"""
        
        stats = NetworkStatistics()
        stats.total_neurons = len(neurons)
        stats.total_connections = len(connections)
        
        # Neurônios por tipo
        for neuron in neurons.values():
            stats.neurons_by_type[neuron.type] = stats.neurons_by_type.get(neuron.type, 0) + 1
            stats.neurons_by_layer[neuron.layer] = stats.neurons_by_layer.get(neuron.layer, 0) + 1
        
        stats.total_layers = len(stats.neurons_by_layer)
        
        # Conexões por tipo
        for conn in connections:
            conn_type = 'recurrent' if conn.recurrent else 'forward'
            stats.connections_by_type[conn_type] = stats.connections_by_type.get(conn_type, 0) + 1
        
        # Ativações
        activations = [n.activation for n in neurons.values()]
        if activations:
            stats.avg_activation = sum(activations) / len(activations)
            stats.max_activation = max(activations)
            stats.min_activation = min(activations)
        
        # Pesos
        weights = [c.weight for c in connections]
        if weights:
            stats.avg_weight = sum(weights) / len(weights)
            stats.max_weight = max(weights)
            stats.min_weight = min(weights)
        
        # Densidade
        max_possible = stats.total_neurons * (stats.total_neurons - 1)
        stats.density = stats.total_connections / max_possible if max_possible > 0 else 0
        
        # Métricas de grafo (se NetworkX disponível)
        if NETWORKX_AVAILABLE and stats.total_neurons > 1:
            try:
                G = nx.Graph()
                G.add_nodes_from(neurons.keys())
                G.add_edges_from([(c.source, c.target) for c in connections])
                
                stats.clustering_coefficient = nx.average_clustering(G)
                
                if nx.is_connected(G):
                    stats.avg_path_length = nx.average_shortest_path_length(G)
                else:
                    # Média dos componentes conectados
                    lengths = []
                    for component in nx.connected_components(G):
                        subgraph = G.subgraph(component)
                        if len(subgraph) > 1:
                            lengths.append(nx.average_shortest_path_length(subgraph))
                    stats.avg_path_length = sum(lengths) / len(lengths) if lengths else 0
                    
            except Exception as e:
                print(f"Erro ao calcular métricas de grafo: {e}")
        
        return stats
    
    @staticmethod
    def find_important_neurons(neurons: Dict[int, Neuron],
                              connections: List[Connection],
                              top_n: int = 5) -> List[Tuple[int, float]]:
        """Encontrar neurônios mais importantes (PageRank-like)"""
        
        if not NETWORKX_AVAILABLE:
            # Fallback: importância baseada em grau e ativação
            importance = {}
            for neuron_id, neuron in neurons.items():
                degree = len(neuron.connections)
                importance[neuron_id] = degree * neuron.activation * neuron.importance
            
            sorted_neurons = sorted(importance.items(), key=lambda x: x[1], reverse=True)
            return sorted_neurons[:top_n]
        
        try:
            G = nx.Graph()
            G.add_nodes_from(neurons.keys())
            G.add_edges_from([(c.source, c.target) for c in connections])
            
            pagerank = nx.pagerank(G)
            sorted_neurons = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)
            
            return sorted_neurons[:top_n]
            
        except:
            return []
    
    @staticmethod
    def find_communities(neurons: Dict[int, Neuron],
                        connections: List[Connection]) -> Dict[int, int]:
        """Detectar comunidades na rede"""
        
        if not NETWORKX_AVAILABLE:
            return {}
        
        try:
            G = nx.Graph()
            G.add_edges_from([(c.source, c.target) for c in connections])
            
            communities = nx.community.greedy_modularity_communities(G)
            
            community_map = {}
            for i, community in enumerate(communities):
                for node in community:
                    community_map[node] = i
            
            return community_map
            
        except:
            return {}

# =============================================================================
# GERENCIADOR DE TEMAS
# =============================================================================

class ThemeManager:
    """Gerenciador de temas e cores"""
    
    THEMES = {
        Theme.DARK: {
            'bg': '#1a1a1a',
            'fg': '#ffffff',
            'grid': '#333333',
            'panel': '#2a2a2a',
            'accent': '#00ff00',
            'text': '#ffffff',
            'edge': '#444444',
            'highlight': '#ffff00'
        },
        Theme.LIGHT: {
            'bg': '#f5f5f5',
            'fg': '#000000',
            'grid': '#dddddd',
            'panel': '#ffffff',
            'accent': '#0066cc',
            'text': '#000000',
            'edge': '#cccccc',
            'highlight': '#ff9900'
        },
        Theme.BLUE: {
            'bg': '#0a1929',
            'fg': '#e3f2fd',
            'grid': '#1e3a5f',
            'panel': '#132f4c',
            'accent': '#90caf9',
            'text': '#ffffff',
            'edge': '#2e4b6e',
            'highlight': '#ffb74d'
        },
        Theme.GREEN: {
            'bg': '#0a2f1f',
            'fg': '#e8f5e9',
            'grid': '#1b4d3e',
            'panel': '#0d3d2c',
            'accent': '#81c784',
            'text': '#ffffff',
            'edge': '#2e7d5e',
            'highlight': '#ffb74d'
        },
        Theme.PURPLE: {
            'bg': '#1a0f2e',
            'fg': '#f3e5f5',
            'grid': '#3a2a5e',
            'panel': '#2a1a3e',
            'accent': '#ba68c8',
            'text': '#ffffff',
            'edge': '#4a3a6e',
            'highlight': '#ffb74d'
        },
        Theme.QUANTUM: {
            'bg': '#050510',
            'fg': '#00ffff',
            'grid': '#2a1a3a',
            'panel': '#0a0a1a',
            'accent': '#ff00ff',
            'text': '#ffffff',
            'edge': '#3a2a4a',
            'highlight': '#ffff00'
        }
    }
    
    def __init__(self):
        self.current_theme = Theme.DARK
        self.custom_colors = {}
    
    def get_theme(self, theme: Theme = None) -> Dict[str, str]:
        """Obter configuração do tema"""
        if theme is None:
            theme = self.current_theme
        
        base_theme = self.THEMES.get(theme, self.THEMES[Theme.DARK]).copy()
        
        # Aplicar cores personalizadas
        if theme == Theme.CUSTOM:
            base_theme.update(self.custom_colors)
        
        return base_theme
    
    def set_theme(self, theme: Theme):
        """Definir tema atual"""
        self.current_theme = theme
    
    def set_custom_color(self, key: str, color: str):
        """Definir cor personalizada"""
        self.custom_colors[key] = color
    
    @staticmethod
    def get_neuron_color(neuron_type: str, theme: Theme = Theme.DARK) -> str:
        """Obter cor para tipo de neurônio baseado no tema"""
        base_colors = {
            'sensory': '#FF6B6B',
            'processing': '#4ECDC4',
            'memory': '#95E1D3',
            'decision': '#FFD93D',
            'output': '#6BCB77',
            'quantum': '#9D4EDD',
            'analytical': '#3A86FF',
            'security': '#FB5607',
            'api': '#8338EC',
            'database': '#06FFA5',
            'control': '#FF006E',
            'feedback': '#00BBF9',
            'default': '#CCCCCC'
        }
        
        if theme in [Theme.DARK, Theme.QUANTUM]:
            return base_colors.get(neuron_type, base_colors['default'])
        elif theme == Theme.LIGHT:
            # Versões mais escuras para tema claro
            dark_colors = {
                'sensory': '#CC5555',
                'processing': '#3DA8A0',
                'memory': '#76B4A8',
                'decision': '#CCAD31',
                'output': '#56A25F',
                'quantum': '#7E3EB8',
                'analytical': '#2E6BCC',
                'security': '#CC4506',
                'api': '#6930B0',
                'database': '#05CC84',
                'default': '#999999'
            }
            return dark_colors.get(neuron_type, dark_colors['default'])
        else:
            return base_colors.get(neuron_type, base_colors['default'])

# =============================================================================
# VISUALIZADOR PRINCIPAL
# =============================================================================

class NeuralNetworkVisualizer:
    """Visualizador avançado de rede neural com suporte 3D/2D"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🧠 VHALINOR IAG 1.0.0 - Visualizador Quântico de Rede Neural")
        self.root.geometry("1600x1000")
        self.root.minsize(1200, 800)
        
        # ===== DADOS DA REDE =====
        self.neurons: Dict[int, Neuron] = {}
        self.connections: List[Connection] = []
        self.layers: Dict[str, List[int]] = {}
        
        # ===== ESTADO DA VISUALIZAÇÃO =====
        self.view_mode = VisualizationMode.AUTO
        self.current_layout = 'hierarchical'
        self.current_theme = Theme.DARK
        self.theme_manager = ThemeManager()
        self.show_labels = True
        self.show_weights = False
        self.show_activations = True
        self.animation_enabled = False
        self.animation_speed = AnimationSpeed.NORMAL
        self.animation_id = None
        self.selected_neurons: Set[int] = set()
        self.highlighted_connections: Set[Tuple[int, int]] = set()
        
        # ===== SISTEMAS =====
        self.logger = VisualLogger()
        self.analyzer = NetworkAnalyzer()
        self.position_calculator = PositionCalculator()
        self.data_generator = NetworkDataGenerator()
        
        # ===== CONFIGURAÇÃO =====
        self.setup_ui()
        self.setup_tags()
        self.setup_menu()
        
        # ===== DADOS INICIAIS =====
        self.load_lex_iag_network()
        self.update_statistics()
        
        # ===== STATUS =====
        self.logger.success("Visualizador VHALINOR IAG inicializado com sucesso")
        self.logger.info(f"Modo 3D: {'Disponível' if MATPLOTLIB_3D else 'Não disponível'}")
        self.logger.info(f"NetworkX: {'Disponível' if NETWORKX_AVAILABLE else 'Não disponível'}")
        self.logger.info(f"NumPy: {'Disponível' if NUMPY_AVAILABLE else 'Não disponível'}")
        
        # ===== BINDINGS =====
        self.setup_bindings()
    
    def setup_ui(self):
        """Configurar interface do usuário"""
        
        # ===== FRAME PRINCIPAL =====
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # ===== FRAME ESQUERDO - CONTROLES =====
        left_frame = ttk.Frame(main_paned, width=300)
        main_paned.add(left_frame, weight=1)
        
        # ===== SEÇÃO DE CONTROLES =====
        controls_frame = ttk.LabelFrame(left_frame, text="🎮 Controles", padding=10)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Botões principais em grid
        button_grid = ttk.Frame(controls_frame)
        button_grid.pack(fill=tk.X)
        
        buttons = [
            ('🔄 Atualizar', self.refresh_network),
            ('📊 Estatísticas', self.show_statistics_dialog),
            ('🔍 Buscar', self.search_neuron_dialog),
            ('💾 Exportar', self.export_network),
            ('📁 Importar', self.import_network),
            ('🎨 Tema', self.cycle_theme),
            ('🎭 Layout', self.cycle_layout),
            ('⚡ Animar', self.toggle_animation),
            ('📸 Screenshot', self.take_screenshot),
            ('🧹 Limpar', self.clear_selection)
        ]
        
        row, col = 0, 0
        for text, command in buttons:
            btn = ttk.Button(button_grid, text=text, command=command)
            btn.grid(row=row, column=col, padx=2, pady=2, sticky='ew')
            col += 1
            if col > 2:
                col = 0
                row += 1
        
        # ===== SEÇÃO DE ARQUITETURA =====
        arch_frame = ttk.LabelFrame(left_frame, text="🏗️ Arquitetura", padding=10)
        arch_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(arch_frame, text="Modelo:").pack(anchor=tk.W)
        self.architecture_var = tk.StringVar(value="vhalinor_quantum")
        architecture_combo = ttk.Combobox(arch_frame, textvariable=self.architecture_var,
                                         values=list(NetworkDataGenerator.ARCHITECTURES.keys()) + ['lex_iag'],
                                         state="readonly")
        architecture_combo.pack(fill=tk.X, pady=(0, 10))
        architecture_combo.bind('<<ComboboxSelected>>', lambda e: self.load_architecture())
        
        ttk.Button(arch_frame, text="🚀 Carregar Arquitetura", 
                  command=self.load_architecture).pack(fill=tk.X)
        
        # ===== SEÇÃO DE VISUALIZAÇÃO =====
        viz_frame = ttk.LabelFrame(left_frame, text="👁️ Visualização", padding=10)
        viz_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Opções de exibição
        self.show_labels_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(viz_frame, text="Mostrar Labels", 
                       variable=self.show_labels_var,
                       command=self.redraw).pack(anchor=tk.W)
        
        self.show_weights_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(viz_frame, text="Mostrar Pesos", 
                       variable=self.show_weights_var,
                       command=self.redraw).pack(anchor=tk.W)
        
        self.show_activations_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(viz_frame, text="Mostrar Ativações", 
                       variable=self.show_activations_var,
                       command=self.redraw).pack(anchor=tk.W)
        
        self.highlight_important_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(viz_frame, text="Destacar Importantes", 
                       variable=self.highlight_important_var,
                       command=self.redraw).pack(anchor=tk.W)
        
        ttk.Separator(viz_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Velocidade de animação
        ttk.Label(viz_frame, text="Velocidade:").pack(anchor=tk.W)
        self.speed_var = tk.StringVar(value="Normal")
        speed_combo = ttk.Combobox(viz_frame, textvariable=self.speed_var,
                                  values=['Muito Lento', 'Lento', 'Normal', 'Rápido', 'Tempo Real'],
                                  state="readonly")
        speed_combo.pack(fill=tk.X)
        speed_combo.bind('<<ComboboxSelected>>', lambda e: self.set_animation_speed())
        
        # ===== SEÇÃO DE FILTROS =====
        filter_frame = ttk.LabelFrame(left_frame, text="🔍 Filtros", padding=10)
        filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="Tipo:").pack(anchor=tk.W)
        self.filter_type_var = tk.StringVar(value="Todos")
        type_combo = ttk.Combobox(filter_frame, textvariable=self.filter_type_var,
                                 values=['Todos', 'sensory', 'processing', 'memory', 
                                        'decision', 'output', 'quantum', 'analytical'],
                                 state="readonly")
        type_combo.pack(fill=tk.X, pady=(0, 10))
        type_combo.bind('<<ComboboxSelected>>', lambda e: self.apply_filter())
        
        ttk.Label(filter_frame, text="Camada:").pack(anchor=tk.W)
        self.filter_layer_var = tk.StringVar(value="Todas")
        self.layer_combo = ttk.Combobox(filter_frame, textvariable=self.filter_layer_var,
                                       values=['Todas'], state="readonly")
        self.layer_combo.pack(fill=tk.X, pady=(0, 10))
        self.layer_combo.bind('<<ComboboxSelected>>', lambda e: self.apply_filter())
        
        ttk.Button(filter_frame, text="✅ Aplicar Filtro", 
                  command=self.apply_filter).pack(fill=tk.X)
        ttk.Button(filter_frame, text="❌ Limpar Filtros", 
                  command=self.clear_filters).pack(fill=tk.X, pady=(5, 0))
        
        # ===== SEÇÃO DE INFORMAÇÕES =====
        info_frame = ttk.LabelFrame(left_frame, text="📋 Informações", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Área de texto para informações
        self.info_text = scrolledtext.ScrolledText(info_frame, 
                                                  height=12,
                                                  bg='#1a1a1a',
                                                  fg='#00ff00',
                                                  font=('Consolas', 9),
                                                  wrap=tk.WORD)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        # Configurar tags para o logger
        self.info_text.tag_config('timestamp', foreground='#808080')
        self.info_text.tag_config('log_debug', foreground='#808080')
        self.info_text.tag_config('log_info', foreground='#00ff00')
        self.info_text.tag_config('log_warning', foreground='#ffff00')
        self.info_text.tag_config('log_error', foreground='#ff0000')
        self.info_text.tag_config('log_critical', foreground='#ff00ff')
        self.info_text.tag_config('log_success', foreground='#00ffff')
        self.info_text.tag_config('log_message', foreground='#ffffff')
        
        self.logger.text_widget = self.info_text
        
        # ===== FRAME CENTRAL - VISUALIZAÇÃO =====
        self.viz_frame = ttk.Frame(main_paned)
        main_paned.add(self.viz_frame, weight=4)
        
        # ===== VISUALIZAÇÃO PRINCIPAL =====
        self.setup_visualization()
        
        # ===== STATUS BAR =====
        self.status_var = tk.StringVar(value="✅ Pronto")
        status_bar = ttk.Label(self.root, textvariable=self.status_var,
                              relief=tk.SUNKEN, anchor=tk.W,
                              font=('Consolas', 9))
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # ===== PROGRESS BAR =====
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
    
    def setup_visualization(self):
        """Configurar área de visualização"""
        
        if MATPLOTLIB_AVAILABLE:
            # Figura principal
            if MATPLOTLIB_3D and self.view_mode in [VisualizationMode.AUTO, VisualizationMode.FORCE_3D]:
                self.fig = Figure(figsize=(14, 10), facecolor='#1a1a1a')
                self.ax = self.fig.add_subplot(111, projection='3d', facecolor='#1a1a1a')
                self.is_3d = True
            else:
                self.fig = Figure(figsize=(14, 10), facecolor='#1a1a1a')
                self.ax = self.fig.add_subplot(111, facecolor='#1a1a1a')
                self.is_3d = False
            
            # Canvas
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.viz_frame)
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Toolbar
            self.toolbar = NavigationToolbar2Tk(self.canvas, self.viz_frame)
            self.toolbar.update()
            
            # Conectar eventos
            self.canvas.mpl_connect('button_press_event', self.on_click)
            self.canvas.mpl_connect('pick_event', self.on_pick)
            
        else:
            # Fallback para Canvas Tkinter
            self.is_3d = False
            self.canvas = tk.Canvas(self.viz_frame, bg='#1a1a1a', highlightthickness=0)
            self.canvas.pack(fill=tk.BOTH, expand=True)
            
            # Bindings para canvas
            self.canvas.bind('<Button-1>', self.on_canvas_click)
            self.canvas.bind('<B1-Motion>', self.on_canvas_drag)
    
    def setup_tags(self):
        """Configurar tags para estilização"""
        self.root.option_add('*TCombobox*Listbox.font', ('Arial', 10))
        self.root.option_add('*Label.font', ('Arial', 10))
        self.root.option_add('*Button.font', ('Arial', 10))
        self.root.option_add('*Checkbutton.font', ('Arial', 10))
        
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar cores
        style.configure('TFrame', background='#2a2a2a')
        style.configure('TLabel', background='#2a2a2a', foreground='white')
        style.configure('TLabelframe', background='#2a2a2a', foreground='white')
        style.configure('TLabelframe.Label', background='#2a2a2a', foreground='white')
        style.configure('TButton', background='#404040', foreground='white')
        style.configure('TCheckbutton', background='#2a2a2a', foreground='white')
        style.configure('TCombobox', background='#404040', foreground='white')
        style.configure('TProgressbar', background='#00ff00')
    
    def setup_menu(self):
        """Configurar menu principal"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Arquivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Importar Rede...", command=self.import_network)
        file_menu.add_command(label="Exportar Rede...", command=self.export_network)
        file_menu.add_command(label="Exportar Imagem...", command=self.take_screenshot)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.root.quit)
        
        # Menu Visualização
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Visualização", menu=view_menu)
        
        view_menu.add_command(label="Layout Hierárquico", 
                            command=lambda: self.set_layout('hierarchical'))
        view_menu.add_command(label="Layout Circular", 
                            command=lambda: self.set_layout('circular'))
        if NETWORKX_AVAILABLE:
            view_menu.add_command(label="Layout Spring", 
                                command=lambda: self.set_layout('spring'))
            view_menu.add_command(label="Layout Spectral", 
                                command=lambda: self.set_layout('spectral'))
        
        view_menu.add_separator()
        
        theme_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="Temas", menu=theme_menu)
        theme_menu.add_command(label="Dark", command=lambda: self.set_theme(Theme.DARK))
        theme_menu.add_command(label="Light", command=lambda: self.set_theme(Theme.LIGHT))
        theme_menu.add_command(label="Blue", command=lambda: self.set_theme(Theme.BLUE))
        theme_menu.add_command(label="Green", command=lambda: self.set_theme(Theme.GREEN))
        theme_menu.add_command(label="Purple", command=lambda: self.set_theme(Theme.PURPLE))
        theme_menu.add_command(label="Quantum", command=lambda: self.set_theme(Theme.QUANTUM))
        
        # Menu Análise
        analysis_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Análise", menu=analysis_menu)
        analysis_menu.add_command(label="Estatísticas", command=self.show_statistics_dialog)
        analysis_menu.add_command(label="Neurônios Importantes", 
                                command=self.show_important_neurons)
        analysis_menu.add_command(label="Comunidades", command=self.show_communities)
        analysis_menu.add_command(label="Matriz de Conexões", command=self.show_connectivity_matrix)
        
        # Menu Ajuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=help_menu)
        help_menu.add_command(label="Sobre", command=self.show_about)
        help_menu.add_command(label="Atalhos", command=self.show_shortcuts)
    
    def setup_bindings(self):
        """Configurar bindings de teclado"""
        self.root.bind('<Control-r>', lambda e: self.refresh_network())
        self.root.bind('<Control-s>', lambda e: self.show_statistics_dialog())
        self.root.bind('<Control-f>', lambda e: self.search_neuron_dialog())
        self.root.bind('<Control-e>', lambda e: self.export_network())
        self.root.bind('<Control-i>', lambda e: self.import_network())
        self.root.bind('<Control-a>', lambda e: self.toggle_animation())
        self.root.bind('<Control-l>', lambda e: self.cycle_layout())
        self.root.bind('<Control-t>', lambda e: self.cycle_theme())
        self.root.bind('<Escape>', lambda e: self.clear_selection())
        self.root.bind('<F5>', lambda e: self.refresh_network())
        self.root.bind('<F1>', lambda e: self.show_shortcuts())
    
    # =========================================================================
    # CARREGAMENTO DE DADOS
    # =========================================================================
    
    def load_lex_iag_network(self):
        """Carregar rede neural do LEX IAG"""
        self.logger.info("Carregando rede neural do LEX IAG...")
        
        neurons, connections, layers = NetworkDataGenerator.generate_from_lex_iag()
        
        self.neurons = neurons
        self.connections = connections
        self.layers = layers
        
        # Calcular posições
        self.calculate_positions()
        
        # Atualizar estatísticas
        self.update_statistics()
        
        # Atualizar combo de camadas
        self.update_layer_combo()
        
        # Desenhar
        self.draw_network()
        
        self.logger.success(f"Rede LEX IAG carregada: {len(neurons)} neurônios, {len(connections)} conexões")
    
    def load_architecture(self):
        """Carregar arquitetura selecionada"""
        arch = self.architecture_var.get()
        
        self.logger.info(f"Carregando arquitetura: {arch}")
        
        if arch == 'lex_iag':
            self.load_lex_iag_network()
        else:
            neurons, connections, layers = NetworkDataGenerator.generate_network(arch)
            
            self.neurons = neurons
            self.connections = connections
            self.layers = layers
            
            self.calculate_positions()
            self.update_statistics()
            self.update_layer_combo()
            self.draw_network()
            
            self.logger.success(f"Arquitetura {arch} carregada: {len(neurons)} neurônios, {len(connections)} conexões")
    
    def calculate_positions(self):
        """Calcular posições dos neurônios baseado no layout atual"""
        
        if self.current_layout == 'hierarchical':
            positions = PositionCalculator.hierarchical_layout(self.layers, self.neurons)
        elif self.current_layout == 'circular':
            positions = PositionCalculator.circular_layout(self.neurons)
        elif self.current_layout == 'spring' and NETWORKX_AVAILABLE:
            positions = PositionCalculator.spring_layout(self.neurons, self.connections)
        elif self.current_layout == 'spectral' and NETWORKX_AVAILABLE:
            positions = PositionCalculator.spectral_layout(self.neurons, self.connections)
        else:
            positions = PositionCalculator.hierarchical_layout(self.layers, self.neurons)
        
        # Calcular posições 3D
        if MATPLOTLIB_3D:
            PositionCalculator.calculate_3d_positions(self.layers, self.neurons)
    
    # =========================================================================
    # DESENHO DA REDE
    # =========================================================================
    
    def draw_network(self):
        """Desenhar rede neural"""
        
        if not MATPLOTLIB_AVAILABLE:
            self.draw_simple_network()
            return
        
        # Limpar
        self.ax.clear()
        
        # Aplicar tema
        theme = self.theme_manager.get_theme(self.current_theme)
        self.ax.set_facecolor(theme['bg'])
        self.fig.patch.set_facecolor(theme['bg'])
        
        # Desenhar conexões
        self.draw_connections()
        
        # Desenhar neurônios
        self.draw_neurons()
        
        # Configurar título e legendas
        self.ax.set_title(f"🧠 VHALINOR IAG - Rede Neural Quântica\n"
                         f"Layout: {self.current_layout.capitalize()} | "
                         f"Neurônios: {len(self.neurons)} | "
                         f"Conexões: {len(self.connections)}",
                         color=theme['fg'], fontsize=14, fontweight='bold')
        
        if self.is_3d:
            self.ax.set_xlabel('Camada', color=theme['fg'])
            self.ax.set_ylabel('Posição Y', color=theme['fg'])
            self.ax.set_zlabel('Posição Z', color=theme['fg'])
            self.ax.view_init(elev=20, azim=45)
        else:
            self.ax.set_xlim(-0.1, 1.1)
            self.ax.set_ylim(-0.1, 1.1)
            self.ax.axis('off')
        
        # Atualizar canvas
        self.canvas.draw()
        
        # Atualizar status
        self.status_var.set(f"✅ Rede desenhada: {len(self.neurons)} neurônios, {len(self.connections)} conexões")
    
    def draw_neurons(self):
        """Desenhar neurônios"""
        
        theme = self.theme_manager.get_theme(self.current_theme)
        filter_type = self.filter_type_var.get()
        filter_layer = self.filter_layer_var.get()
        
        for neuron_id, neuron in self.neurons.items():
            # Aplicar filtros
            if filter_type != 'Todos' and neuron.type != filter_type:
                continue
            if filter_layer != 'Todas' and neuron.layer != filter_layer:
                continue
            
            # Posição
            if self.is_3d:
                x, y, z = neuron.position_3d
            else:
                x, y = neuron.position_2d
                z = 0
            
            # Cor baseada no tipo
            color = self.theme_manager.get_neuron_color(neuron.type, self.current_theme)
            
            # Tamanho baseado na ativação/importância
            if self.show_activations_var.get():
                size = 100 + (neuron.activation * 300)
            else:
                size = 200 * neuron.size
            
            # Destacar se selecionado
            if neuron_id in self.selected_neurons:
                edgecolor = theme['highlight']
                linewidth = 3
                size *= 1.2
            else:
                edgecolor = theme['fg']
                linewidth = 1
            
            # Destacar neurônios importantes
            if self.highlight_important_var.get() and neuron.importance > 1.5:
                edgecolor = '#ff00ff'
                linewidth = 2
            
            # Desenhar
            if self.is_3d:
                scatter = self.ax.scatter(x, y, z,
                                        c=color,
                                        s=size,
                                        edgecolors=edgecolor,
                                        linewidths=linewidth,
                                        alpha=0.8,
                                        picker=True,
                                        label=neuron.name)
            else:
                scatter = self.ax.scatter(x, y,
                                        c=color,
                                        s=size,
                                        edgecolors=edgecolor,
                                        linewidths=linewidth,
                                        alpha=0.8,
                                        picker=True,
                                        label=neuron.name)
            
            # Label
            if self.show_labels_var.get():
                label = neuron.name[:10]
                if self.show_activations_var.get():
                    label += f"\n{neuron.activation:.1%}"
                
                if self.is_3d:
                    self.ax.text(x, y, z + 0.05, label,
                               ha='center', va='bottom',
                               fontsize=7, color=theme['fg'],
                               fontweight='bold')
                else:
                    self.ax.text(x, y + 0.02, label,
                               ha='center', va='bottom',
                               fontsize=7, color=theme['fg'],
                               fontweight='bold')
    
    def draw_connections(self):
        """Desenhar conexões entre neurônios"""
        
        theme = self.theme_manager.get_theme(self.current_theme)
        
        for conn in self.connections:
            if not conn.enabled:
                continue
            
            source = self.neurons.get(conn.source)
            target = self.neurons.get(conn.target)
            
            if not source or not target:
                continue
            
            # Posições
            if self.is_3d:
                x1, y1, z1 = source.position_3d
                x2, y2, z2 = target.position_3d
            else:
                x1, y1 = source.position_2d
                x2, y2 = target.position_2d
            
            # Cor e estilo
            if conn.recurrent:
                color = '#FF00FF'
                style = '--'
            else:
                color = conn.color
                style = '-'
            
            # Destacar conexões
            alpha = conn.weight * 0.5
            width = conn.width * 0.5
            
            if (conn.source, conn.target) in self.highlighted_connections:
                color = theme['highlight']
                width *= 2
                alpha = 0.8
            
            # Desenhar
            if self.is_3d:
                self.ax.plot([x1, x2], [y1, y2], [z1, z2],
                           color=color,
                           alpha=alpha,
                           linewidth=width,
                           linestyle=style,
                           zorder=1)
            else:
                self.ax.plot([x1, x2], [y1, y2],
                           color=color,
                           alpha=alpha,
                           linewidth=width,
                           linestyle=style,
                           zorder=1)
            
            # Mostrar peso
            if self.show_weights_var.get():
                mx = (x1 + x2) / 2
                my = (y1 + y2) / 2
                weight_text = f"{conn.weight:.2f}"
                
                if self.is_3d:
                    mz = (z1 + z2) / 2
                    self.ax.text(mx, my, mz, weight_text,
                               ha='center', va='center',
                               fontsize=6, color=theme['fg'],
                               bbox=dict(boxstyle='round', facecolor=theme['bg'], alpha=0.7))
                else:
                    self.ax.text(mx, my, weight_text,
                               ha='center', va='center',
                               fontsize=6, color=theme['fg'],
                               bbox=dict(boxstyle='round', facecolor=theme['bg'], alpha=0.7))
    
    def draw_simple_network(self):
        """Desenhar rede simples sem matplotlib"""
        self.canvas.delete("all")
        
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if width <= 1:
            width = 1200
        if height <= 1:
            height = 800
        
        theme = self.theme_manager.get_theme(self.current_theme)
        self.canvas.configure(bg=theme['bg'])
        
        # Calcular posições
        positions = {}
        layer_names = list(self.layers.keys())
        layer_width = width / (len(layer_names) + 1)
        
        for i, layer_name in enumerate(layer_names):
            layer_neurons = self.layers[layer_name]
            x = (i + 1) * layer_width
            
            # Label da camada
            self.canvas.create_text(x, 30, text=layer_name,
                                  fill=theme['fg'],
                                  font=('Arial', 10, 'bold'))
            
            if len(layer_neurons) > 0:
                y_spacing = (height - 100) / len(layer_neurons)
                
                for j, neuron_id in enumerate(layer_neurons):
                    y = 60 + (j + 0.5) * y_spacing
                    positions[neuron_id] = (x, y)
                    
                    # Atualizar posição
                    if neuron_id in self.neurons:
                        self.neurons[neuron_id].position_2d = (x / width, y / height)
        
        # Desenhar conexões
        for conn in self.connections:
            if not conn.enabled:
                continue
            
            if conn.source in positions and conn.target in positions:
                x1, y1 = positions[conn.source]
                x2, y2 = positions[conn.target]
                
                color = '#FF00FF' if conn.recurrent else conn.color
                width_line = conn.width * 2
                
                self.canvas.create_line(x1, y1, x2, y2,
                                      fill=color,
                                      width=width_line,
                                      dash=(4, 4) if conn.recurrent else ())
        
        # Desenhar neurônios
        for neuron_id, neuron in self.neurons.items():
            if neuron_id in positions:
                x, y = positions[neuron_id]
                
                color = self.theme_manager.get_neuron_color(neuron.type, self.current_theme)
                radius = 15 + (neuron.activation * 15)
                
                # Destacar se selecionado
                outline = theme['highlight'] if neuron_id in self.selected_neurons else theme['fg']
                outline_width = 3 if neuron_id in self.selected_neurons else 1
                
                self.canvas.create_oval(x - radius, y - radius,
                                      x + radius, y + radius,
                                      fill=color,
                                      outline=outline,
                                      width=outline_width)
                
                # Label
                if self.show_labels_var.get():
                    self.canvas.create_text(x, y,
                                          text=neuron.name[:8],
                                          fill='black',
                                          font=('Arial', 8, 'bold'))
    
    # =========================================================================
    # MANIPULAÇÃO DE EVENTOS
    # =========================================================================
    
    def on_click(self, event):
        """Manipulador de clique no matplotlib"""
        if event.inaxes != self.ax:
            return
        
        # Modo 3D não suporta picking simples
        if self.is_3d:
            return
        
        # Buscar neurônio mais próximo
        min_dist = 0.05
        closest_neuron = None
        
        for neuron_id, neuron in self.neurons.items():
            x, y = neuron.position_2d
            dist = math.sqrt((event.xdata - x) ** 2 + (event.ydata - y) ** 2)
            
            if dist < min_dist:
                min_dist = dist
                closest_neuron = neuron_id
        
        if closest_neuron is not None:
            self.toggle_neuron_selection(closest_neuron)
    
    def on_pick(self, event):
        """Manipulador de pick event no matplotlib"""
        if hasattr(event, 'artist') and hasattr(event.artist, 'get_offsets'):
            # Encontrar neurônio correspondente
            offsets = event.artist.get_offsets()
            if len(offsets) > 0:
                x, y = offsets[0]
                
                for neuron_id, neuron in self.neurons.items():
                    nx, ny = neuron.position_2d
                    if abs(nx - x) < 0.01 and abs(ny - y) < 0.01:
                        self.toggle_neuron_selection(neuron_id)
                        break
    
    def on_canvas_click(self, event):
        """Manipulador de clique no canvas Tkinter"""
        x, y = event.x, event.y
        
        # Buscar neurônio mais próximo
        min_dist = 20
        closest_neuron = None
        
        for neuron_id, neuron in self.neurons.items():
            if hasattr(neuron, 'position_2d'):
                nx = neuron.position_2d[0] * self.canvas.winfo_width()
                ny = neuron.position_2d[1] * self.canvas.winfo_height()
                
                dist = math.sqrt((x - nx) ** 2 + (y - ny) ** 2)
                
                if dist < min_dist:
                    min_dist = dist
                    closest_neuron = neuron_id
        
        if closest_neuron is not None:
            self.toggle_neuron_selection(closest_neuron)
    
    def on_canvas_drag(self, event):
        """Manipulador de arrasto no canvas Tkinter"""
        pass
    
    def toggle_neuron_selection(self, neuron_id: int):
        """Alternar seleção de neurônio"""
        if neuron_id in self.selected_neurons:
            self.selected_neurons.remove(neuron_id)
            self.logger.debug(f"Neurônio {self.neurons[neuron_id].name} deselecionado")
        else:
            self.selected_neurons.add(neuron_id)
            self.logger.info(f"Neurônio selecionado: {self.neurons[neuron_id].name} "
                           f"(Tipo: {self.neurons[neuron_id].type}, "
                           f"Ativação: {self.neurons[neuron_id].activation:.1%})")
            
            # Destacar conexões
            self.highlighted_connections.clear()
            for conn in self.connections:
                if conn.source == neuron_id or conn.target == neuron_id:
                    self.highlighted_connections.add((conn.source, conn.target))
        
        self.redraw()
    
    def clear_selection(self):
        """Limpar seleção"""
        self.selected_neurons.clear()
        self.highlighted_connections.clear()
        self.redraw()
        self.logger.info("Seleção limpa")
    
    # =========================================================================
    # ANIMAÇÃO
    # =========================================================================
    
    def toggle_animation(self):
        """Alternar animação"""
        if self.animation_enabled:
            self.stop_animation()
        else:
            self.start_animation()
    
    def start_animation(self):
        """Iniciar animação"""
        self.animation_enabled = True
        
        # Velocidade
        speed_map = {
            'Muito Lento': AnimationSpeed.SLOW,
            'Lento': AnimationSpeed.NORMAL,
            'Normal': AnimationSpeed.FAST,
            'Rápido': AnimationSpeed.VERY_FAST,
            'Tempo Real': AnimationSpeed.REAL_TIME
        }
        speed = speed_map.get(self.speed_var.get(), AnimationSpeed.NORMAL)
        
        self.animate()
        self.logger.info(f"Animação iniciada (velocidade: {self.speed_var.get()})")
    
    def stop_animation(self):
        """Parar animação"""
        self.animation_enabled = False
        if self.animation_id:
            self.root.after_cancel(self.animation_id)
            self.animation_id = None
        self.logger.info("Animação parada")
    
    def animate(self):
        """Frame de animação"""
        if not self.animation_enabled:
            return
        
        # Atualizar ativações
        for neuron in self.neurons.values():
            # Simular variação
            neuron.activation += random.uniform(-0.1, 0.1)
            neuron.activation = max(0.0, min(1.0, neuron.activation))
        
        # Redesenhar
        self.redraw()
        
        # Agendar próximo frame
        speed_map = {
            AnimationSpeed.SLOW: 2000,
            AnimationSpeed.NORMAL: 1000,
            AnimationSpeed.FAST: 500,
            AnimationSpeed.VERY_FAST: 200,
            AnimationSpeed.REAL_TIME: 50
        }
        delay = speed_map.get(self.animation_speed, 1000)
        
        self.animation_id = self.root.after(delay, self.animate)
    
    def set_animation_speed(self):
        """Definir velocidade da animação"""
        speed_map = {
            'Muito Lento': AnimationSpeed.SLOW,
            'Lento': AnimationSpeed.NORMAL,
            'Normal': AnimationSpeed.FAST,
            'Rápido': AnimationSpeed.VERY_FAST,
            'Tempo Real': AnimationSpeed.REAL_TIME
        }
        self.animation_speed = speed_map.get(self.speed_var.get(), AnimationSpeed.NORMAL)
        self.logger.debug(f"Velocidade da animação: {self.speed_var.get()}")
    
    # =========================================================================
    # ATUALIZAÇÃO
    # =========================================================================
    
    def refresh_network(self):
        """Atualizar rede com novos dados"""
        self.logger.info("Atualizando rede...")
        
        # Atualizar ativações
        for neuron in self.neurons.values():
            neuron.activation = random.uniform(0.3, 0.9)
        
        # Atualizar estatísticas
        self.update_statistics()
        
        # Redesenhar
        self.redraw()
        
        self.logger.success("Rede atualizada")
    
    def redraw(self):
        """Redesenhar rede"""
        self.show_labels = self.show_labels_var.get()
        self.show_weights = self.show_weights_var.get()
        self.show_activations = self.show_activations_var.get()
        
        self.draw_network()
    
    def update_statistics(self):
        """Atualizar estatísticas da rede"""
        self.stats = NetworkAnalyzer.calculate_statistics(self.neurons, self.connections)
    
    def update_layer_combo(self):
        """Atualizar combo de camadas"""
        layers = ['Todas'] + list(self.layers.keys())
        self.layer_combo['values'] = layers
        self.filter_layer_var.set('Todas')
    
    # =========================================================================
    # FILTROS
    # =========================================================================
    
    def apply_filter(self):
        """Aplicar filtros à visualização"""
        filter_type = self.filter_type_var.get()
        filter_layer = self.filter_layer_var.get()
        
        self.logger.info(f"Aplicando filtro: Tipo={filter_type}, Camada={filter_layer}")
        self.redraw()
    
    def clear_filters(self):
        """Limpar todos os filtros"""
        self.filter_type_var.set('Todos')
        self.filter_layer_var.set('Todas')
        self.redraw()
        self.logger.info("Filtros removidos")
    
    # =========================================================================
    # LAYOUT E TEMA
    # =========================================================================
    
    def set_layout(self, layout: str):
        """Definir layout"""
        self.current_layout = layout
        self.calculate_positions()
        self.redraw()
        self.logger.info(f"Layout alterado: {layout}")
    
    def cycle_layout(self):
        """Alternar entre layouts"""
        layouts = ['hierarchical', 'circular', 'spring', 'spectral']
        available_layouts = [l for l in layouts 
                           if l in ['hierarchical', 'circular'] or NETWORKX_AVAILABLE]
        
        current_index = available_layouts.index(self.current_layout) if self.current_layout in available_layouts else -1
        next_index = (current_index + 1) % len(available_layouts)
        
        self.set_layout(available_layouts[next_index])
    
    def set_theme(self, theme: Theme):
        """Definir tema"""
        self.current_theme = theme
        self.theme_manager.set_theme(theme)
        self.redraw()
        self.logger.info(f"Tema alterado: {theme.value}")
    
    def cycle_theme(self):
        """Alternar entre temas"""
        themes = list(Theme)
        current_index = themes.index(self.current_theme)
        next_index = (current_index + 1) % len(themes)
        self.set_theme(themes[next_index])
    
    # =========================================================================
    # DIÁLOGOS
    # =========================================================================
    
    def show_statistics_dialog(self):
        """Mostrar estatísticas em diálogo"""
        stats_text = f"""
╔══════════════════════════════════════════════════════════════════╗
║                    ESTATÍSTICAS DA REDE NEURAL                    ║
╚══════════════════════════════════════════════════════════════════╝

📊 VISÃO GERAL
   • Total de Neurônios: {self.stats.total_neurons}
   • Total de Conexões: {self.stats.total_connections}
   • Total de Camadas: {self.stats.total_layers}
   • Densidade da Rede: {self.stats.density:.4f}

🧠 NEURÔNIOS POR TIPO:
"""
        for ntype, count in sorted(self.stats.neurons_by_type.items()):
            stats_text += f"   • {ntype.capitalize()}: {count}\n"
        
        stats_text += f"""
🔗 CONEXÕES POR TIPO:
"""
        for ctype, count in sorted(self.stats.connections_by_type.items()):
            stats_text += f"   • {ctype.capitalize()}: {count}\n"
        
        stats_text += f"""
📈 ATIVAÇÃO:
   • Média: {self.stats.avg_activation:.1%}
   • Máxima: {self.stats.max_activation:.1%}
   • Mínima: {self.stats.min_activation:.1%}

⚖️  PESOS:
   • Média: {self.stats.avg_weight:.3f}
   • Máximo: {self.stats.max_weight:.3f}
   • Mínimo: {self.stats.min_weight:.3f}

📐 MÉTRICAS DE GRAFO:
   • Coeficiente de Clustering: {self.stats.clustering_coefficient:.4f}
   • Caminho Médio: {self.stats.avg_path_length:.2f}

🕐 Última atualização: {self.stats.timestamp.strftime('%d/%m/%Y %H:%M:%S')}
"""
        messagebox.showinfo("Estatísticas da Rede", stats_text)
        
        # Também logar
        self.logger.info("Estatísticas exibidas")
        for line in stats_text.split('\n'):
            if line.strip():
                self.logger.debug(line.strip())
    
    def search_neuron_dialog(self):
        """Diálogo de busca de neurônio"""
        dialog = tk.Toplevel(self.root)
        dialog.title("🔍 Buscar Neurônio")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Busca
        ttk.Label(main_frame, text="Nome do neurônio:").pack(anchor=tk.W)
        
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        search_entry = ttk.Entry(search_frame, width=40)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        def do_search():
            query = search_entry.get().lower()
            results = []
            
            for neuron_id, neuron in self.neurons.items():
                if query in neuron.name.lower():
                    results.append({
                        'id': neuron_id,
                        'name': neuron.name,
                        'type': neuron.type,
                        'layer': neuron.layer,
                        'activation': neuron.activation
                    })
            
            # Atualizar lista
            listbox.delete(0, tk.END)
            for result in results[:20]:
                listbox.insert(tk.END, f"{result['name']} ({result['type']}) - {result['activation']:.1%}")
                listbox.itemconfig(tk.END, {'fg': self.theme_manager.get_neuron_color(result['type'], self.current_theme)})
            
            status_var.set(f"Encontrados: {len(results)} neurônios")
        
        ttk.Button(search_frame, text="Buscar", command=do_search).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Resultados
        ttk.Label(main_frame, text="Resultados:").pack(anchor=tk.W)
        
        listbox_frame = ttk.Frame(main_frame)
        listbox_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox = tk.Listbox(listbox_frame,
                            yscrollcommand=scrollbar.set,
                            font=('Consolas', 10),
                            height=12)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=listbox.yview)
        
        # Selecionar
        def select_neuron():
            selection = listbox.curselection()
            if selection:
                index = selection[0]
                item = listbox.get(index)
                # Extrair nome
                name = item.split('(')[0].strip()
                
                for neuron_id, neuron in self.neurons.items():
                    if neuron.name == name:
                        self.toggle_neuron_selection(neuron_id)
                        dialog.destroy()
                        break
        
        ttk.Button(main_frame, text="Selecionar", command=select_neuron).pack(side=tk.LEFT, padx=5)
        ttk.Button(main_frame, text="Fechar", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Status
        status_var = tk.StringVar(value="Digite um termo para buscar")
        status_label = ttk.Label(main_frame, textvariable=status_var, foreground='gray')
        status_label.pack(pady=(10, 0))
        
        search_entry.focus()
        search_entry.bind('<Return>', lambda e: do_search())
    
    def show_important_neurons(self):
        """Mostrar neurônios mais importantes"""
        important = NetworkAnalyzer.find_important_neurons(self.neurons, self.connections)
        
        text = "🧠 NEURÔNIOS MAIS IMPORTANTES:\n\n"
        
        for i, (neuron_id, score) in enumerate(important[:10], 1):
            neuron = self.neurons[neuron_id]
            text += f"{i}. {neuron.name}\n"
            text += f"   • Tipo: {neuron.type}\n"
            text += f"   • Camada: {neuron.layer}\n"
            text += f"   • Importância: {score:.4f}\n"
            text += f"   • Ativação: {neuron.activation:.1%}\n"
            text += f"   • Conexões: {len(neuron.connections)}\n\n"
        
        messagebox.showinfo("Neurônios Importantes", text)
    
    def show_communities(self):
        """Mostrar comunidades detectadas"""
        communities = NetworkAnalyzer.find_communities(self.neurons, self.connections)
        
        if not communities:
            messagebox.showinfo("Comunidades", 
                              "Não foi possível detectar comunidades.\n"
                              "NetworkX não está disponível ou a rede é muito pequena.")
            return
        
        # Agrupar por comunidade
        community_groups = defaultdict(list)
        for neuron_id, community_id in communities.items():
            if neuron_id in self.neurons:
                community_groups[community_id].append(self.neurons[neuron_id].name)
        
        text = "👥 COMUNIDADES DETECTADAS:\n\n"
        
        for community_id, neurons in sorted(community_groups.items()):
            text += f"Comunidade {community_id + 1} ({len(neurons)} neurônios):\n"
            for neuron in neurons[:10]:  # Mostrar apenas 10 por comunidade
                text += f"   • {neuron}\n"
            if len(neurons) > 10:
                text += f"   ... e mais {len(neurons) - 10}\n"
            text += "\n"
        
        messagebox.showinfo("Comunidades", text)
    
    def show_connectivity_matrix(self):
        """Mostrar matriz de conectividade"""
        if not NUMPY_AVAILABLE:
            messagebox.showinfo("Matriz de Conexões", 
                              "NumPy não está disponível para gerar a matriz.")
            return
        
        n = len(self.neurons)
        matrix = np.zeros((n, n))
        
        neuron_indices = {neuron_id: i for i, neuron_id in enumerate(self.neurons.keys())}
        
        for conn in self.connections:
            i = neuron_indices[conn.source]
            j = neuron_indices[conn.target]
            matrix[i, j] = conn.weight
        
        # Criar visualização da matriz
        fig, ax = plt.subplots(figsize=(10, 8))
        im = ax.imshow(matrix[:50, :50], cmap='viridis', aspect='auto')
        ax.set_title('Matriz de Conectividade (primeiras 50 conexões)')
        ax.set_xlabel('Neurônio Alvo')
        ax.set_ylabel('Neurônio Fonte')
        plt.colorbar(im, label='Peso da Conexão')
        
        plt.tight_layout()
        plt.show()
    
    def show_about(self):
        """Mostrar sobre o sistema"""
        about_text = """
╔══════════════════════════════════════════════════════════════════╗
║                      VHALINOR IAG 1.0.0                          ║
║              Visualizador Quântico de Rede Neural                ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║   🧠 Autor: Alex Miranda Sales                                  ║
║   📅 Data: 2026                                                 ║
║   🔬 Versão: 2.0.0 (Production Ready)                          ║
║                                                                  ║
║   ✨ Funcionalidades:                                            ║
║   • Visualização 2D/3D de redes neurais                         ║
║   • Múltiplos layouts (hierárquico, circular, spring, spectral)║
║   • Temas personalizáveis                                       ║
║   • Análise de estatísticas e comunidades                       ║
║   • Animação em tempo real                                      ║
║   • Exportação de dados e imagens                               ║
║                                                                  ║
║   📚 Dependências:                                              ║
║   • Matplotlib 3D (opcional)                                    ║
║   • NetworkX (opcional)                                         ║
║   • NumPy (opcional)                                            ║
║   • Pillow (opcional)                                           ║
║                                                                  ║
║   🔒 Licença: Proprietária - Vhalinor IAG Systems               ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""
        messagebox.showinfo("Sobre o VHALINOR IAG", about_text)
    
    def show_shortcuts(self):
        """Mostrar atalhos de teclado"""
        shortcuts_text = """
╔══════════════════════════════════════════════════════════════════╗
║                       ATALHOS DE TECLADO                         ║
╚══════════════════════════════════════════════════════════════════╝

🎮 CONTROLES GERAIS:
   • Ctrl + R    → Atualizar rede
   • Ctrl + S    → Estatísticas
   • Ctrl + F    → Buscar neurônio
   • Ctrl + E    → Exportar rede
   • Ctrl + I    → Importar rede
   • Ctrl + A    → Alternar animação
   • Ctrl + L    → Alternar layout
   • Ctrl + T    → Alternar tema
   • F5          → Atualizar
   • Esc         → Limpar seleção

🖱️  INTERAÇÃO:
   • Clique      → Selecionar neurônio
   • Ctrl+Clique → Múltipla seleção
   • Arrastar    → Mover visualização (2D)

🎨 VISUALIZAÇÃO:
   • 1          → Layout hierárquico
   • 2          → Layout circular
   • 3          → Layout spring
   • 4          → Layout spectral
   • D          → Tema Dark
   • L          → Tema Light
   • Q          → Tema Quantum

📊 ANÁLISE:
   • Ctrl + P   → Neurônios importantes
   • Ctrl + M   → Matriz de conexões
   • Ctrl + C   → Comunidades

💾 ARQUIVO:
   • Ctrl + Shift + E → Exportar imagem
   • Ctrl + Q        → Sair

📚 AJUDA:
   • F1         → Este menu
   • H          → Ajuda contextual
"""
        messagebox.showinfo("Atalhos de Teclado", shortcuts_text)
    
    # =========================================================================
    # EXPORTAÇÃO E IMPORTAÇÃO
    # =========================================================================
    
    def export_network(self):
        """Exportar rede para arquivo"""
        filename = filedialog.asksaveasfilename(
            title="Exportar Rede",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            export_data = {
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'version': '2.0.0',
                    'name': 'VHALINOR IAG Network',
                    'neurons_count': len(self.neurons),
                    'connections_count': len(self.connections)
                },
                'neurons': {str(k): v.to_dict() for k, v in self.neurons.items()},
                'connections': [c.to_dict() for c in self.connections],
                'layers': self.layers,
                'statistics': self.stats.to_dict()
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.logger.success(f"Rede exportada para {filename}")
            messagebox.showinfo("Exportação", f"Rede exportada com sucesso!\n{filename}")
            
        except Exception as e:
            self.logger.error(f"Erro ao exportar: {e}")
            messagebox.showerror("Erro", f"Erro ao exportar: {e}")
    
    def import_network(self):
        """Importar rede de arquivo"""
        filename = filedialog.askopenfilename(
            title="Importar Rede",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Importar neurônios
            self.neurons = {}
            for k, v in data['neurons'].items():
                v['id'] = int(k)
                v['timestamp'] = datetime.fromisoformat(v['timestamp']) if 'timestamp' in v else datetime.now()
                self.neurons[int(k)] = Neuron(**v)
            
            # Importar conexões
            self.connections = []
            for c in data['connections']:
                c['timestamp'] = datetime.fromisoformat(c['timestamp']) if 'timestamp' in c else datetime.now()
                self.connections.append(Connection(**c))
            
            # Importar camadas
            self.layers = data['layers']
            
            # Recalcular
            self.calculate_positions()
            self.update_statistics()
            self.update_layer_combo()
            self.draw_network()
            
            self.logger.success(f"Rede importada de {filename}")
            messagebox.showinfo("Importação", f"Rede importada com sucesso!\n{filename}")
            
        except Exception as e:
            self.logger.error(f"Erro ao importar: {e}")
            messagebox.showerror("Erro", f"Erro ao importar: {e}")
    
    def take_screenshot(self):
        """Capturar screenshot da visualização"""
        filename = filedialog.asksaveasfilename(
            title="Salvar Screenshot",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            if MATPLOTLIB_AVAILABLE:
                self.fig.savefig(filename, dpi=300, bbox_inches='tight', facecolor='#1a1a1a')
            else:
                # Canvas Tkinter
                self.canvas.postscript(file=filename.replace('.png', '.eps'))
                
                # Converter para PNG se Pillow disponível
                if PIL_AVAILABLE:
                    img = Image.open(filename.replace('.png', '.eps'))
                    img.save(filename, 'PNG')
            
            self.logger.success(f"Screenshot salvo em {filename}")
            messagebox.showinfo("Screenshot", f"Screenshot salvo com sucesso!\n{filename}")
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar screenshot: {e}")
            messagebox.showerror("Erro", f"Erro ao salvar screenshot: {e}")


# =============================================================================
# FUNÇÃO PRINCIPAL
# =============================================================================

def main():
    """Função principal"""
    try:
        root = tk.Tk()
        app = NeuralNetworkVisualizer(root)
        
        # Configurar ícone (opcional)
        try:
            root.iconbitmap('icon.ico')
        except:
            pass
        
        # Centralizar
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f'{width}x{height}+{x}+{y}')
        
        root.mainloop()
        
    except Exception as e:
        print(f"Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        input("Pressione Enter para sair...")


if __name__ == "__main__":
    main()
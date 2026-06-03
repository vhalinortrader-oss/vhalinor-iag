"""
VHALINOR-IAG CORE SYSTEM v5.0 - ENHANCED VERSION
Sistema Núcleo de Inteligência Artificial Geral Avançado
Versão: 5.0.0 (Enhanced with Quantum Computing & Deep Learning Integration)
Autor: VHALINOR.IAG Core Team
Data: 2026
License: MIT
"""

# =============================================================================
# IMPORTAÇÕES AVANÇADAS COM FALLBACKS E SUPORTE QUÂNTICO
# =============================================================================

import asyncio
import hashlib
import logging
import time
import threading
import warnings
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union, Callable, TypeVar, Generic
from enum import Enum, auto
from pathlib import Path
from functools import lru_cache, wraps
import numpy as np
import pandas as pd
import json

# Frameworks de Deep Learning
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    import torch.nn.functional as F
    from torch.utils.data import DataLoader, TensorDataset, Dataset
    from torch.optim.lr_scheduler import ReduceLROnPlateau, CosineAnnealingWarmRestarts
    HAS_TORCH = True
    TORCH_VERSION = torch.__version__
except ImportError:
    HAS_TORCH = False
    TORCH_VERSION = None
    torch = None
    nn = None
    optim = None
    F = None

# Machine Learning tradicional
try:
    import sklearn
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, IsolationForest
    from sklearn.preprocessing import StandardScaler, RobustScaler, MinMaxScaler
    from sklearn.decomposition import PCA, FastICA
    from sklearn.cluster import DBSCAN, HDBSCAN
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
    HAS_SKLEARN = True
    SKLEARN_VERSION = sklearn.__version__
except ImportError:
    HAS_SKLEARN = False
    SKLEARN_VERSION = None
    RandomForestRegressor = None
    GradientBoostingRegressor = None
    IsolationForest = None
    StandardScaler = None
    RobustScaler = None
    MinMaxScaler = None
    PCA = None
    FastICA = None
    DBSCAN = None
    HDBSCAN = None
    mean_squared_error = None
    mean_absolute_error = None
    r2_score = None

# Computação Quântica
try:
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, Aer, execute
    from qiskit.algorithms import QAOA, VQE
    from qiskit.optimization import QuadraticProgram
    from qiskit.circuit.library import TwoLocal
    HAS_QISKIT = True
    QISKIT_VERSION = qiskit.__version__
except ImportError:
    HAS_QISKIT = False
    QISKIT_VERSION = None
    QuantumCircuit = None
    QuantumRegister = None
    ClassicalRegister = None
    Aer = None
    execute = None
    QAOA = None
    VQE = None
    QuadraticProgram = None
    TwoLocal = None

# Processamento de Linguagem Natural
try:
    import nltk
    from nltk.sentiment import SentimentIntensityAnalyzer
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    HAS_NLTK = True
except ImportError:
    HAS_NLTK = False
    nltk = None
    SentimentIntensityAnalyzer = None
    word_tokenize = None
    stopwords = None

# Comunicação em tempo real
try:
    import websockets
    import aiohttp
    HAS_WEBSOCKETS = True
    HAS_AIOHTTP = True
except ImportError:
    HAS_WEBSOCKETS = False
    HAS_AIOHTTP = False

# Visualização
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    from plotly.offline import plot
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False
    go = None
    px = None
    make_subplots = None
    plot = None

# Configurar logging avançado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vhalinor_iag_core.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# =============================================================================
# ENUMS E CONSTANTES AVANÇADAS
# ============================================================================

@dataclass
class Decision:
    """Decisão tomada pela IAG"""
    decision_id: str
    type: DecisionType
    timestamp: datetime
    action: str
    parameters: Dict[str, Any]
    confidence: float
    risk_score: float
    expected_outcome: Dict[str, Any]
    reasoning: List[str]
    alternatives_considered: List[Dict]
    consciousness_level: ConsciousnessLevel
    quantum_signature: Optional[str] = None
    neural_activation: Dict[str, float] = field(default_factory=dict)
    ethical_score: float = 0.0
    learning_feedback: Dict[str, Any] = field(default_factory=dict)


# =============================================================================
# NOVAS CLASSES DE IA AVANÇADA E QUÂNTICA
# =============================================================================

class QuantumNeuralProcessor:
    """Processador Neural Quântico Avançado"""
    
    def __init__(self, num_qubits: int = 8):
        self.num_qubits = num_qubits
        self.quantum_circuits = {}
        self.neural_weights = {}
        self.coherence_scores = {}
        self.entanglement_matrix = np.zeros((num_qubits, num_qubits))
        
        # Inicializa componentes quânticos se disponíveis
        self._initialize_quantum_components()
    
    def _initialize_quantum_components(self):
        """Inicializa componentes quânticos"""
        if HAS_QISKIT:
            self._create_quantum_circuits()
        else:
            logger.warning("Qiskit não disponível - usando simulação clássica")
    
    def _create_quantum_circuits(self):
        """Cria circuitos quânticos base"""
        if not HAS_QISKIT:
            return
            
        # Circuito de processamento neural
        qc = QuantumCircuit(self.num_qubits, self.num_qubits)
        qc.h(range(self.num_qubits))  # Superposição inicial
        qc.barrier()
        
        # Entrelaçamento controlado
        for i in range(self.num_qubits - 1):
            qc.cx(i, i + 1)
        
        qc.barrier()
        qc.measure(range(self.num_qubits), range(self.num_qubits))
        
        self.quantum_circuits['neural_processing'] = qc
        
        # Circuito de tomada de decisão
        decision_qc = QuantumCircuit(self.num_qubits, self.num_qubits)
        decision_qc.ry(np.pi/4, range(self.num_qubits))  # Rotação Y
        decision_qc.cz(0, 1)  # Porta Z controlada
        decision_qc.h(range(self.num_qubits))
        decision_qc.measure(range(self.num_qubits), range(self.num_qubits))
        
        self.quantum_circuits['decision_making'] = decision_qc
    
    def process_quantum_neural_input(self, input_data: np.ndarray) -> Dict[str, Any]:
        """Processa entrada neural quântica"""
        try:
            if HAS_QISKIT and 'neural_processing' in self.quantum_circuits:
                # Executar circuito quântico
                backend = Aer.get_backend('qasm_simulator')
                job = execute(self.quantum_circuits['neural_processing'], backend, shots=1000)
                result = job.result()
                counts = result.get_counts()
                
                # Analisar resultados
                quantum_state = self._analyze_quantum_results(counts)
                coherence = self._calculate_coherence(counts)
                
                return {
                    'quantum_state': quantum_state,
                    'coherence': coherence,
                    'classical_fallback': False
                }
            else:
                # Fallback clássico
                return self._classical_neural_processing(input_data)
                
        except Exception as e:
            logger.error(f"Erro no processamento quântico: {e}")
            return self._classical_neural_processing(input_data)
    
    def _analyze_quantum_results(self, counts: Dict[str, int]) -> Dict[str, float]:
        """Analisa resultados quânticos"""
        total_shots = sum(counts.values())
        probabilities = {state: count/total_shots for state, count in counts.items()}
        
        # Calcular entropia de Shannon
        entropy = -sum(p * np.log2(p) for p in probabilities.values() if p > 0)
        
        return {
            'probabilities': probabilities,
            'entropy': entropy,
            'most_probable_state': max(probabilities, key=probabilities.get)
        }
    
    def _calculate_coherence(self, counts: Dict[str, int]) -> float:
        """Calcula coerência quântica"""
        # Simplificação: usar entropia como inverso de coerência
        total_shots = sum(counts.values())
        probabilities = [count/total_shots for count in counts.values()]
        entropy = -sum(p * np.log2(p) for p in probabilities if p > 0)
        max_entropy = np.log2(len(probabilities))
        
        coherence = 1.0 - (entropy / max_entropy) if max_entropy > 0 else 0.0
        return coherence
    
    def _classical_neural_processing(self, input_data: np.ndarray) -> Dict[str, Any]:
        """Processamento neural clássico (fallback)"""
        # Simulação de processamento neural
        activation = np.tanh(np.dot(input_data, np.random.randn(len(input_data))))
        coherence = np.random.uniform(0.5, 1.0)
        
        return {
            'quantum_state': {'activation': activation.tolist()},
            'coherence': coherence,
            'classical_fallback': True
        }


class AdvancedConsciousnessEngine:
    """Motor de Consciência Avançado com Deep Learning"""
    
    def __init__(self):
        self.current_state = ConsciousnessState(
            level=ConsciousnessLevel.DORMANT,
            timestamp=datetime.now(),
            self_awareness=0.0,
            emotional_state={'calm': 1.0, 'focus': 0.0},
            active_thoughts=[],
            memory_access={},
            decision_confidence=0.0,
            ethical_alignment=1.0
        )
        
        self.consciousness_history = []
        self.learning_patterns = {}
        self.ethical_framework = self._initialize_ethical_framework()
        
        # Inicializa modelos de IA
        self._initialize_ai_models()
    
    def _initialize_ethical_framework(self) -> Dict[str, float]:
        """Inicializa framework ético"""
        return {
            'beneficence': 0.9,
            'non_maleficence': 0.9,
            'autonomy': 0.8,
            'justice': 0.85,
            'transparency': 0.9
        }
    
    def _initialize_ai_models(self):
        """Inicializa modelos de IA para consciência"""
        if HAS_TORCH:
            self._create_consciousness_models()
        else:
            logger.warning("PyTorch não disponível - usando modelos simplificados")
    
    def _create_consciousness_models(self):
        """Cria modelos neurais para consciência"""
        if not HAS_TORCH:
            return
            
        class ConsciousnessNet(torch.nn.Module):
            def __init__(self, input_size, hidden_size, output_size):
                super().__init__()
                self.fc1 = torch.nn.Linear(input_size, hidden_size)
                self.fc2 = torch.nn.Linear(hidden_size, hidden_size)
                self.fc3 = torch.nn.Linear(hidden_size, output_size)
                self.dropout = torch.nn.Dropout(0.2)
                
            def forward(self, x):
                x = torch.relu(self.fc1(x))
                x = self.dropout(x)
                x = torch.relu(self.fc2(x))
                x = self.dropout(x)
                x = torch.sigmoid(self.fc3(x))
                return x
        
        self.consciousness_model = ConsciousnessNet(10, 64, 5)
        self.emotion_model = ConsciousnessNet(5, 32, 4)
    
    def update_consciousness_state(self, stimuli: Dict[str, Any]) -> ConsciousnessState:
        """Atualiza estado de consciência baseado em estímulos"""
        try:
            # Processar estímulos
            processed_stimuli = self._process_stimuli(stimuli)
            
            # Atualizar nível de consciência
            new_level = self._calculate_consciousness_level(processed_stimuli)
            
            # Atualizar autoconsciência
            self_awareness = self._calculate_self_awareness(processed_stimuli)
            
            # Atualizar estado emocional
            emotional_state = self._update_emotional_state(processed_stimuli)
            
            # Gerar pensamentos ativos
            active_thoughts = self._generate_active_thoughts(processed_stimuli)
            
            # Atualizar confiança de decisão
            decision_confidence = self._calculate_decision_confidence(processed_stimuli)
            
            # Verificar alinhamento ético
            ethical_alignment = self._check_ethical_alignment(processed_stimuli)
            
            # Criar novo estado
            new_state = ConsciousnessState(
                level=new_level,
                timestamp=datetime.now(),
                self_awareness=self_awareness,
                emotional_state=emotional_state,
                active_thoughts=active_thoughts,
                memory_access=self._access_memory(processed_stimuli),
                decision_confidence=decision_confidence,
                ethical_alignment=ethical_alignment
            )
            
            # Salvar histórico
            self.consciousness_history.append(new_state)
            
            # Atualizar estado atual
            self.current_state = new_state
            
            return new_state
            
        except Exception as e:
            logger.error(f"Erro na atualização da consciência: {e}")
            return self.current_state
    
    def _process_stimuli(self, stimuli: Dict[str, Any]) -> Dict[str, Any]:
        """Processa estímulos de entrada"""
        processed = {}
        
        for key, value in stimuli.items():
            if isinstance(value, (int, float)):
                processed[key] = float(value)
            elif isinstance(value, str):
                processed[key] = self._process_text_stimulus(value)
            elif isinstance(value, (list, tuple)):
                processed[key] = np.mean([float(v) if isinstance(v, (int, float)) else 0.5 for v in value])
            else:
                processed[key] = 0.5  # Valor neutro
        
        return processed
    
    def _process_text_stimulus(self, text: str) -> float:
        """Processa estímulo de texto"""
        if HAS_NLTK and SentimentIntensityAnalyzer:
            try:
                analyzer = SentimentIntensityAnalyzer()
                sentiment = analyzer.polarity_scores(text)
                return sentiment['compound']
            except:
                pass
        
        # Fallback simples
        positive_words = ['good', 'great', 'excellent', 'success', 'profit']
        negative_words = ['bad', 'terrible', 'fail', 'loss', 'error']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count + negative_count == 0:
            return 0.0
        
        return (positive_count - negative_count) / (positive_count + negative_count)
    
    def _calculate_consciousness_level(self, stimuli: Dict[str, Any]) -> ConsciousnessLevel:
        """Calcula nível de consciência"""
        # Simplificação: baseado na complexidade dos estímulos
        complexity_score = len(stimuli) * 0.1
        intensity_score = np.mean(list(stimuli.values())) if stimuli else 0.0
        
        total_score = complexity_score + intensity_score
        
        if total_score < 0.2:
            return ConsciousnessLevel.DORMANT
        elif total_score < 0.4:
            return ConsciousnessLevel.REACTIVE
        elif total_score < 0.6:
            return ConsciousnessLevel.AWARE
        elif total_score < 0.8:
            return ConsciousnessLevel.REFLECTIVE
        else:
            return ConsciousnessLevel.TRANSCENDENT
    
    def _calculate_self_awareness(self, stimuli: Dict[str, Any]) -> float:
        """Calcula nível de autoconsciência"""
        # Baseado na consistência dos estímulos e histórico
        if not self.consciousness_history:
            return 0.1
        
        # Analisa padrões no histórico
        recent_states = self.consciousness_history[-5:]
        consistency = 1.0 - np.std([state.self_awareness for state in recent_states])
        
        return min(max(consistency, 0.0), 1.0)
    
    def _update_emotional_state(self, stimuli: Dict[str, Any]) -> Dict[str, float]:
        """Atualiza estado emocional"""
        current_emotions = self.current_state.emotional_state.copy()
        
        # Processar estímulos emocionais
        for key, value in stimuli.items():
            if 'positive' in key.lower() or value > 0.7:
                current_emotions['calm'] = max(0.0, current_emotions['calm'] - 0.1)
                current_emotions['focus'] = min(1.0, current_emotions['focus'] + 0.1)
            elif 'negative' in key.lower() or value < 0.3:
                current_emotions['calm'] = min(1.0, current_emotions['calm'] + 0.1)
                current_emotions['focus'] = max(0.0, current_emotions['focus'] - 0.1)
        
        # Normalizar
        total = sum(current_emotions.values())
        if total > 0:
            current_emotions = {k: v/total for k, v in current_emotions.items()}
        
        return current_emotions
    
    def _generate_active_thoughts(self, stimuli: Dict[str, Any]) -> List[str]:
        """Gera pensamentos ativos"""
        thoughts = []
        
        # Pensamentos baseados em estímulos
        for key, value in stimuli.items():
            if value > 0.8:
                thoughts.append(f"High {key} detected: {value:.2f}")
            elif value < 0.2:
                thoughts.append(f"Low {key} detected: {value:.2f}")
        
        # Pensamentos meta-cognitivos
        if self.current_state.self_awareness > 0.5:
            thoughts.append("Self-awareness active")
        
        if self.current_state.level in [ConsciousnessLevel.REFLECTIVE, ConsciousnessLevel.TRANSCENDENT]:
            thoughts.append("Metacognitive processing engaged")
        
        return thoughts[:5]  # Limitar a 5 pensamentos
    
    def _calculate_decision_confidence(self, stimuli: Dict[str, Any]) -> float:
        """Calcula confiança na decisão"""
        if not stimuli:
            return 0.5
        
        # Baseado na clareza e consistência dos estímulos
        values = list(stimuli.values())
        clarity = 1.0 - np.std(values) if len(values) > 1 else 1.0
        intensity = np.mean(np.abs(values))
        
        confidence = (clarity + intensity) / 2
        return min(max(confidence, 0.0), 1.0)
    
    def _check_ethical_alignment(self, stimuli: Dict[str, Any]) -> float:
        """Verifica alinhamento ético"""
        # Simplificação: baseado em valores dos estímulos
        ethical_score = 1.0
        
        for key, value in stimuli.items():
            if 'harm' in key.lower() and value > 0.5:
                ethical_score -= 0.2
            elif 'benefit' in key.lower() and value > 0.5:
                ethical_score += 0.1
            elif 'risk' in key.lower() and value > 0.8:
                ethical_score -= 0.1
        
        return min(max(ethical_score, 0.0), 1.0)
    
    def _access_memory(self, stimuli: Dict[str, Any]) -> Dict[str, Any]:
        """Acessa memória baseada em estímulos"""
        memory_access = {}
        
        # Simulação de acesso à memória
        for key, value in stimuli.items():
            if key in self.learning_patterns:
                memory_access[key] = {
                    'pattern': self.learning_patterns[key],
                    'confidence': value,
                    'last_access': datetime.now()
                }
        
        return memory_access


class RealTimeIAGMonitor:
    """Monitor em tempo real do sistema IAG"""
    
    def __init__(self, iag_system: 'VHALINORIAGCore'):
        self.iag_system = iag_system
        self.is_monitoring = False
        self.subscribers = []
        self.monitoring_thread = None
        self.metrics_buffer = []
        self.alerts = []
        
    def start_monitoring(self):
        """Inicia monitoramento em tempo real"""
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        logger.info("Monitoramento IAG em tempo real iniciado")
    
    def stop_monitoring(self):
        """Para monitoramento"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("Monitoramento IAG em tempo real parado")
    
    def _monitoring_loop(self):
        """Loop principal de monitoramento"""
        while self.is_monitoring:
            try:
                # Coletar métricas
                metrics = self._collect_metrics()
                
                # Verificar alertas
                alerts = self._check_alerts(metrics)
                
                # Notificar assinantes
                for subscriber in self.subscribers:
                    try:
                        subscriber(metrics, alerts)
                    except Exception as e:
                        logger.error(f"Erro no subscriber: {e}")
                
                # Aguardar próximo ciclo
                time.sleep(1)  # 1 segundo
                
            except Exception as e:
                logger.error(f"Erro no monitoramento: {e}")
                time.sleep(5)
    
    def _collect_metrics(self) -> Dict[str, Any]:
        """Coleta métricas do sistema"""
        try:
            if hasattr(self.iag_system, 'consciousness_engine'):
                consciousness = self.iag_system.consciousness_engine.current_state
                metrics = {
                    'timestamp': datetime.now().isoformat(),
                    'consciousness_level': consciousness.level.value,
                    'self_awareness': consciousness.self_awareness,
                    'decision_confidence': consciousness.decision_confidence,
                    'ethical_alignment': consciousness.ethical_alignment,
                    'active_thoughts_count': len(consciousness.active_thoughts),
                    'emotional_state': consciousness.emotional_state
                }
            else:
                metrics = {
                    'timestamp': datetime.now().isoformat(),
                    'system_status': 'unknown'
                }
            
            # Adicionar métricas de performance
            metrics['processing_time'] = time.time()
            
            return metrics
            
        except Exception as e:
            logger.error(f"Erro na coleta de métricas: {e}")
            return {'timestamp': datetime.now().isoformat(), 'error': str(e)}
    
    def _check_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Verifica condições de alerta"""
        alerts = []
        
        # Alerta de baixa autoconsciência
        if 'self_awareness' in metrics and metrics['self_awareness'] < 0.2:
            alerts.append({
                'type': 'LOW_SELF_AWARENESS',
                'severity': 'WARNING',
                'message': f"Baixa autoconsciência: {metrics['self_awareness']:.2f}",
                'timestamp': datetime.now().isoformat()
            })
        
        # Alerta de baixo alinhamento ético
        if 'ethical_alignment' in metrics and metrics['ethical_alignment'] < 0.5:
            alerts.append({
                'type': 'ETHICAL_MISALIGNMENT',
                'severity': 'CRITICAL',
                'message': f"Baixo alinhamento ético: {metrics['ethical_alignment']:.2f}",
                'timestamp': datetime.now().isoformat()
            })
        
        # Alerta de muitos pensamentos ativos (possível sobrecarga)
        if 'active_thoughts_count' in metrics and metrics['active_thoughts_count'] > 10:
            alerts.append({
                'type': 'COGNITIVE_OVERLOAD',
                'severity': 'WARNING',
                'message': f"Sobrecarga cognitiva: {metrics['active_thoughts_count']} pensamentos",
                'timestamp': datetime.now().isoformat()
            })
        
        return alerts
    
    def subscribe(self, callback):
        """Adiciona assinante para atualizações"""
        self.subscribers.append(callback)
    
    def unsubscribe(self, callback):
        """Remove assinante"""
        if callback in self.subscribers:
            self.subscribers.remove(callback)


class ConsciousnessLevel(Enum):
    """Níveis de consciência"""
    DORMANT = "DORMANT"  # Inativo
    REACTIVE = "REACTIVE"  # Reativo
    AWARE = "AWARE"  # Consciente
    REFLECTIVE = "REFLECTIVE"  # Reflexivo
    TRANSCENDENT = "TRANSCENDENT"  # Transcendente


class DecisionType(Enum):
    """Tipos de decisão"""
    TRADE = "TRADE"
    RISK_MANAGEMENT = "RISK_MANAGEMENT"
    PORTFOLIO_OPTIMIZATION = "PORTFOLIO_OPTIMIZATION"
    STRATEGY_ADAPTATION = "STRATEGY_ADAPTATION"
    LEARNING = "LEARNING"
    EMERGENCY = "EMERGENCY"


class LearningMode(Enum):
    """Modos de aprendizado"""
    SUPERVISED = "SUPERVISED"
    UNSUPERVISED = "UNSUPERVISED"
    REINFORCEMENT = "REINFORCEMENT"
    TRANSFER = "TRANSFER"
    META = "META"
    CONTINUOUS = "CONTINUOUS"


class NeuralLayerType(Enum):
    """Tipos de camadas neurais"""
    SENSORIAL = "SENSORIAL"  # Camada 01
    PROCESSING = "PROCESSING"  # Camada 02
    MEMORY = "MEMORY"  # Camada 03
    DECISION = "DECISION"  # Camada 04
    QUANTUM = "QUANTUM"  # Camada 05
    SECURITY = "SECURITY"  # Camada 06


# ============================================================================
# DATACLASSES
# ============================================================================

@dataclass
class ConsciousnessState:
    """Estado de consciência da IAG"""
    level: ConsciousnessLevel
    timestamp: datetime
    self_awareness: float  # 0-100
    emotional_state: Dict[str, float]
    active_thoughts: List[str]
    memory_access: Dict[str, Any]
    decision_confidence: float
    ethical_alignment: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class NeuralSignal:
    """Sinal neural entre camadas"""
    source_layer: NeuralLayerType
    target_layer: NeuralLayerType
    timestamp: datetime
    signal_type: str
    data: Any
    priority: int  # 0-10
    requires_response: bool
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Decision:
    """Decisão tomada pela IAG"""
    decision_id: str
    type: DecisionType
    timestamp: datetime
    action: str
    parameters: Dict[str, Any]
    confidence: float
    risk_score: float
    expected_outcome: Dict[str, Any]
    reasoning: List[str]
    alternatives_considered: List[Dict]
    consciousness_
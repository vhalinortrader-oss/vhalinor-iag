# 15_memory_learning.py
"""
Sistema VhalinorTrade - Memória de Aprendizado
Sistema de memória persistente para evolução contínua
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
from collections import deque
import pickle
import json
from datetime import datetime, timedelta
import hashlib

class MemoryUnit:
    """Unidade de memória individual"""
    def __init__(self, experience: Dict, importance: float):
        self.experience = experience
        self.importance = importance
        self.timestamp = datetime.now()
        self.access_count = 0
        self.success_score = 0.5
        
    def update_importance(self, outcome: float):
        """Atualiza importância baseado no resultado"""
        self.access_count += 1
        self.success_score = (self.success_score * 0.9 + outcome * 0.1)
        self.importance *= (0.5 + self.success_score)

class MemorySystem:
    """
    Sistema de memória de longo prazo para aprendizado
    Inspirado em sistemas de memória humana:
    - Memória sensorial (curto prazo)
    - Memória de trabalho (médio prazo)
    - Memória de longo prazo (persistente)
    """
    
    def __init__(self, config):
        self.config = config
        self.sensory_memory = deque(maxlen=100)  # Últimos 100 eventos
        self.working_memory = deque(maxlen=1000)  # Últimos 1000 eventos
        self.long_term_memory = {}  # Memória persistente
        self.pattern_memory = {}  # Padrões aprendidos
        self.successful_strategies = []  # Estratégias bem-sucedidas
        
        # Carrega memória persistente
        self._load_memory()
        
    def store_experience(self, experience: Dict, importance: float = 0.5):
        """Armazena uma nova experiência"""
        memory_unit = MemoryUnit(experience, importance)
        
        # Memória sensorial (sempre armazena)
        self.sensory_memory.append(memory_unit)
        
        # Memória de trabalho (se importância > threshold)
        if importance > 0.3:
            self.working_memory.append(memory_unit)
            
        # Memória de longo prazo (se importância > threshold alto)
        if importance > 0.6:
            experience_hash = self._hash_experience(experience)
            self.long_term_memory[experience_hash] = memory_unit
            
        # Auto-salvamento periódico
        if len(self.long_term_memory) % 50 == 0:
            self._save_memory()
            
    def retrieve_similar_experiences(self, current_state: Dict,
                                    top_k: int = 5) -> List[Dict]:
        """Recupera experiências similares da memória"""
        similar_experiences = []
        
        # Busca em todas as camadas de memória
        all_memories = list(self.working_memory) + list(self.long_term_memory.values())
        
        for memory in all_memories:
            similarity = self._calculate_similarity(
                current_state, memory.experience
            )
            
            if similarity > 0.7:  # Threshold de similaridade
                similar_experiences.append({
                    'experience': memory.experience,
                    'similarity': similarity,
                    'importance': memory.importance,
                    'success_score': memory.success_score
                })
                
        # Ordena por similaridade * importância * sucesso
        similar_experiences.sort(
            key=lambda x: x['similarity'] * x['importance'] * x['success_score'],
            reverse=True
        )
        
        return similar_experiences[:top_k]
    
    def learn_from_outcome(self, experience: Dict, outcome: float):
        """Aprende com o resultado de uma decisão"""
        experience_hash = self._hash_experience(experience)
        
        # Atualiza importância nas memórias
        for memory_list in [self.sensory_memory, self.working_memory]:
            for memory in memory_list:
                if self._hash_experience(memory.experience) == experience_hash:
                    memory.update_importance(outcome)
                    
        # Atualiza memória de longo prazo
        if experience_hash in self.long_term_memory:
            self.long_term_memory[experience_hash].update_importance(outcome)
            
        # Se foi muito bem-sucedido, armazena como estratégia
        if outcome > 0.8:
            self.successful_strategies.append({
                'experience': experience,
                'outcome': outcome,
                'timestamp': datetime.now()
            })
            
            # Mantém apenas as top 100 estratégias
            self.successful_strategies = sorted(
                self.successful_strategies,
                key=lambda x: x['outcome'],
                reverse=True
            )[:100]
    
    def _calculate_similarity(self, state1: Dict, state2: Dict) -> float:
        """Calcula similaridade entre dois estados"""
        common_keys = set(state1.keys()) & set(state2.keys())
        
        if not common_keys:
            return 0.0
            
        similarities = []
        
        for key in common_keys:
            val1 = state1[key]
            val2 = state2[key]
            
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                # Similaridade numérica
                max_val = max(abs(val1), abs(val2), 1e-8)
                sim = 1 - abs(val1 - val2) / max_val
                similarities.append(max(0, sim))
            elif isinstance(val1, str) and isinstance(val2, str):
                # Similaridade de strings
                sim = 1 if val1 == val2 else 0
                similarities.append(sim)
                
        return np.mean(similarities) if similarities else 0.0
    
    def _hash_experience(self, experience: Dict) -> str:
        """Cria hash único para experiência"""
        exp_str = json.dumps(experience, sort_keys=True, default=str)
        return hashlib.sha256(exp_str.encode()).hexdigest()[:16]
    
    def _save_memory(self):
        """Salva memória em disco"""
        memory_data = {
            'long_term_memory': {
                hash_key: {
                    'experience': mem.experience,
                    'importance': mem.importance,
                    'success_score': mem.success_score,
                    'access_count': mem.access_count,
                    'timestamp': mem.timestamp.isoformat()
                }
                for hash_key, mem in self.long_term_memory.items()
            },
            'successful_strategies': self.successful_strategies,
            'pattern_memory': self.pattern_memory,
            'saved_at': datetime.now().isoformat()
        }
        
        filepath = f"{self.config.data_path}/memory_system.pkl"
        with open(filepath, 'wb') as f:
            pickle.dump(memory_data, f)
            
    def _load_memory(self):
        """Carrega memória do disco"""
        filepath = f"{self.config.data_path}/memory_system.pkl"
        
        try:
            with open(filepath, 'rb') as f:
                memory_data = pickle.load(f)
                
            # Reconstrói memória de longo prazo
            for hash_key, mem_data in memory_data['long_term_memory'].items():
                memory_unit = MemoryUnit(
                    mem_data['experience'],
                    mem_data['importance']
                )
                memory_unit.success_score = mem_data['success_score']
                memory_unit.access_count = mem_data['access_count']
                memory_unit.timestamp = datetime.fromisoformat(mem_data['timestamp'])
                self.long_term_memory[hash_key] = memory_unit
                
            self.successful_strategies = memory_data['successful_strategies']
            self.pattern_memory = memory_data['pattern_memory']
            
        except FileNotFoundError:
            print("Nenhuma memória anterior encontrada. Iniciando fresco.")
            
    def consolidate_memories(self):
        """Consolida memórias (como o sono)"""
        # Move memórias importantes da working para long-term
        for memory in self.working_memory:
            if memory.importance > 0.7 and memory.access_count > 10:
                exp_hash = self._hash_experience(memory.experience)
                if exp_hash not in self.long_term_memory:
                    self.long_term_memory[exp_hash] = memory
                    
        # Remove memórias de baixa importância da long-term
        low_importance = [
            hash_key for hash_key, mem in self.long_term_memory.items()
            if mem.importance < 0.1 and mem.access_count < 5
        ]
        
        for hash_key in low_importance:
            del self.long_term_memory[hash_key]
            
        self._save_memory()
"""
Cognitive Engine - Motor de Resposta Cognitiva Avançada
=====================================================
Implementação com memória, contexto e chain-of-thought reasoning
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import re
from collections import deque, defaultdict
import uuid

# Importações condicionais
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

from config import settings
from core import get_logger, log_execution


class MemoryType(str, Enum):
    """Tipos de memória cognitiva"""
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    WORKING = "working"


class ReasoningType(str, Enum):
    """Tipos de raciocínio"""
    CHAIN_OF_THOUGHT = "chain_of_thought"
    TREE_OF_THOUGHTS = "tree_of_thoughts"
    STEP_BY_STEP = "step_by_step"
    ANALOGICAL = "analogical"
    CAUSAL = "causal"


@dataclass
class MemoryItem:
    """Item de memória cognitiva"""
    id: str
    content: str
    memory_type: MemoryType
    timestamp: datetime
    importance: float = 0.5
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    embedding: Optional[List[float]] = None
    context: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        data = {
            'id': self.id,
            'content': self.content,
            'memory_type': self.memory_type.value,
            'timestamp': self.timestamp.isoformat(),
            'importance': self.importance,
            'access_count': self.access_count,
            'context': self.context,
            'tags': self.tags
        }
        if self.last_accessed:
            data['last_accessed'] = self.last_accessed.isoformat()
        return data


@dataclass
class ReasoningStep:
    """Passo de raciocínio"""
    step_id: str
    description: str
    input_data: Any
    reasoning_type: ReasoningType
    output: Any
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'step_id': self.step_id,
            'description': self.description,
            'input_data': str(self.input_data),
            'reasoning_type': self.reasoning_type.value,
            'output': str(self.output),
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat()
        }


class CognitiveMemory:
    """Sistema de memória cognitiva"""
    
    def __init__(self, max_short_term: int = 100, max_long_term: int = 10000):
        self.logger = get_logger("vhalinor.cognitive.memory", "cognitive_memory")
        self.short_term_memory = deque(maxlen=max_short_term)
        self.long_term_memory = {}
        self.episodic_memory = []
        self.semantic_memory = {}
        self.working_memory = {}
        self.max_short_term = max_short_term
        self.max_long_term = max_long_term
        self.memory_stats = {
            'total_memories': 0,
            'short_term_count': 0,
            'long_term_count': 0,
            'episodic_count': 0,
            'semantic_count': 0
        }
    
    @log_execution(component="cognitive", operation="store_memory")
    async def store_memory(
        self, 
        content: str, 
        memory_type: MemoryType,
        importance: float = 0.5,
        context: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None
    ) -> str:
        """Armazena memória com tipo específico"""
        memory_id = str(uuid.uuid4())
        memory_item = MemoryItem(
            id=memory_id,
            content=content,
            memory_type=memory_type,
            timestamp=datetime.now(),
            importance=importance,
            context=context or {},
            tags=tags or []
        )
        
        # Gerar embedding se disponível
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                model = SentenceTransformer('all-MiniLM-L6-v2')
                memory_item.embedding = model.encode(content).tolist()
            except Exception:
                pass
        
        # Armazenar conforme tipo
        if memory_type == MemoryType.SHORT_TERM:
            self.short_term_memory.append(memory_item)
            self.memory_stats['short_term_count'] += 1
        elif memory_type == MemoryType.LONG_TERM:
            self.long_term_memory[memory_id] = memory_item
            self.memory_stats['long_term_count'] += 1
        elif memory_type == MemoryType.EPISODIC:
            self.episodic_memory.append(memory_item)
            self.memory_stats['episodic_count'] += 1
        elif memory_type == MemoryType.SEMANTIC:
            self.semantic_memory[memory_id] = memory_item
            self.memory_stats['semantic_count'] += 1
        elif memory_type == MemoryType.WORKING:
            self.working_memory[memory_id] = memory_item
        
        self.memory_stats['total_memories'] += 1
        self.logger.info(f"Stored {memory_type.value} memory: {memory_id}")
        
        return memory_id
    
    async def retrieve_memory(
        self, 
        query: str, 
        memory_type: Optional[MemoryType] = None,
        limit: int = 10
    ) -> List[MemoryItem]:
        """Recupera memórias relevantes"""
        candidates = []
        
        # Selecionar candidatos por tipo
        if memory_type == MemoryType.SHORT_TERM:
            candidates = list(self.short_term_memory)
        elif memory_type == MemoryType.LONG_TERM:
            candidates = list(self.long_term_memory.values())
        elif memory_type == MemoryType.EPISODIC:
            candidates = self.episodic_memory
        elif memory_type == MemoryType.SEMANTIC:
            candidates = list(self.semantic_memory.values())
        elif memory_type == MemoryType.WORKING:
            candidates = list(self.working_memory.values())
        else:
            # Todos os tipos
            candidates = (
                list(self.short_term_memory) +
                list(self.long_term_memory.values()) +
                self.episodic_memory +
                list(self.semantic_memory.values()) +
                list(self.working_memory.values())
            )
        
        # Busca por similaridade de texto (simplificada)
        scored_memories = []
        query_lower = query.lower()
        
        for memory in candidates:
            score = 0
            
            # Pontuação por conteúdo
            if query_lower in memory.content.lower():
                score += 0.8
            
            # Pontuação por tags
            for tag in memory.tags:
                if query_lower in tag.lower():
                    score += 0.3
            
            # Pontuação por importância
            score += memory.importance * 0.2
            
            # Pontuação por acesso recente
            if memory.last_accessed:
                days_since_access = (datetime.now() - memory.last_accessed).days
                score += max(0, 0.1 - days_since_access * 0.01)
            
            scored_memories.append((memory, score))
        
        # Ordenar por score e atualizar acesso
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        result = [mem for mem, score in scored_memories[:limit]]
        
        # Atualizar estatísticas de acesso
        for memory in result:
            memory.access_count += 1
            memory.last_accessed = datetime.now()
        
        return result
    
    async def consolidate_memory(self) -> int:
        """Consolida memórias de curto prazo para longo prazo"""
        consolidated = 0
        
        # Mover memórias importantes de curto prazo para longo prazo
        for memory in list(self.short_term_memory):
            if memory.importance > 0.7 or memory.access_count > 5:
                # Mover para memória de longo prazo
                self.long_term_memory[memory.id] = memory
                self.short_term_memory.remove(memory)
                consolidated += 1
        
        # Limpar memórias antigas de baixa importância
        current_time = datetime.now()
        old_memories = []
        
        for memory_id, memory in self.long_term_memory.items():
            days_old = (current_time - memory.timestamp).days
            if days_old > 30 and memory.importance < 0.3 and memory.access_count < 2:
                old_memories.append(memory_id)
        
        for memory_id in old_memories:
            del self.long_term_memory[memory_id]
            consolidated += 1
        
        self.logger.info(f"Consolidated {consolidated} memories")
        return consolidated
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas da memória"""
        return {
            **self.memory_stats,
            'short_term_capacity': f"{len(self.short_term_memory)}/{self.max_short_term}",
            'long_term_capacity': f"{len(self.long_term_memory)}/{self.max_long_term}",
            'working_memory_items': len(self.working_memory),
            'average_importance': self._calculate_average_importance()
        }
    
    def _calculate_average_importance(self) -> float:
        """Calcula importância média das memórias"""
        all_memories = (
            list(self.short_term_memory) +
            list(self.long_term_memory.values()) +
            self.episodic_memory +
            list(self.semantic_memory.values()) +
            list(self.working_memory.values())
        )
        
        if not all_memories:
            return 0.0
        
        return sum(mem.importance for mem in all_memories) / len(all_memories)


class ReasoningEngine:
    """Motor de raciocínio cognitivo"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.cognitive.reasoning", "reasoning_engine")
        self.reasoning_steps = []
        self.reasoning_patterns = {
            'analysis': r'analyze|examine|investigate|evaluate',
            'synthesis': r'combine|integrate|synthesize|merge',
            'comparison': r'compare|contrast|differentiate|distinguish',
            'causation': r'cause|effect|because|therefore|thus',
            'prediction': r'predict|forecast|expect|anticipate'
        }
    
    async def chain_of_thought(
        self, 
        problem: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> List[ReasoningStep]:
        """Executa raciocínio chain-of-thought"""
        steps = []
        step_id = 1
        
        # Passo 1: Compreensão do problema
        understanding = await self._understand_problem(problem, context)
        steps.append(ReasoningStep(
            step_id=f"step_{step_id}",
            description="Understand the problem",
            input_data=problem,
            reasoning_type=ReasoningType.CHAIN_OF_THOUGHT,
            output=understanding,
            confidence=0.9
        ))
        step_id += 1
        
        # Passo 2: Análise de componentes
        components = await self._analyze_components(understanding)
        steps.append(ReasoningStep(
            step_id=f"step_{step_id}",
            description="Analyze problem components",
            input_data=understanding,
            reasoning_type=ReasoningType.CHAIN_OF_THOUGHT,
            output=components,
            confidence=0.8
        ))
        step_id += 1
        
        # Passo 3: Geração de soluções
        solutions = await self._generate_solutions(components)
        steps.append(ReasoningStep(
            step_id=f"step_{step_id}",
            description="Generate potential solutions",
            input_data=components,
            reasoning_type=ReasoningType.CHAIN_OF_THOUGHT,
            output=solutions,
            confidence=0.7
        ))
        step_id += 1
        
        # Passo 4: Avaliação de soluções
        evaluation = await self._evaluate_solutions(solutions)
        steps.append(ReasoningStep(
            step_id=f"step_{step_id}",
            description="Evaluate and select best solution",
            input_data=solutions,
            reasoning_type=ReasoningType.CHAIN_OF_THOUGHT,
            output=evaluation,
            confidence=0.8
        ))
        
        self.reasoning_steps.extend(steps)
        return steps
    
    async def _understand_problem(self, problem: str, context: Optional[Dict[str, Any]]) -> str:
        """Compreende o problema"""
        # Análise simplificada do problema
        understanding = f"Problem identified: {problem}"
        
        if context:
            understanding += f"\nContext: {context}"
        
        # Identificar tipo de problema
        problem_types = {
            'prediction': 'predict|forecast|estimate',
            'analysis': 'analyze|examine|evaluate',
            'decision': 'decide|choose|select',
            'optimization': 'optimize|improve|enhance'
        }
        
        for ptype, patterns in problem_types.items():
            if re.search(patterns, problem.lower()):
                understanding += f"\nProblem type: {ptype}"
                break
        
        return understanding
    
    async def _analyze_components(self, understanding: str) -> Dict[str, Any]:
        """Analisa componentes do problema"""
        components = {
            'main_elements': [],
            'constraints': [],
            'objectives': [],
            'requirements': []
        }
        
        # Extração simplificada de componentes
        sentences = understanding.split('.')
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Identificar elementos principais
            if any(word in sentence.lower() for word in ['data', 'information', 'input']):
                components['main_elements'].append(sentence)
            
            # Identificar restrições
            if any(word in sentence.lower() for word in ['limit', 'constraint', 'restriction']):
                components['constraints'].append(sentence)
            
            # Identificar objetivos
            if any(word in sentence.lower() for word in ['goal', 'objective', 'target']):
                components['objectives'].append(sentence)
        
        return components
    
    async def _generate_solutions(self, components: Dict[str, Any]) -> List[str]:
        """Gera soluções potenciais"""
        solutions = []
        
        # Soluções baseadas em padrões
        if components['objectives']:
            solutions.append("Implement step-by-step approach to achieve objectives")
        
        if components['constraints']:
            solutions.append("Work within identified constraints with optimization")
        
        if components['main_elements']:
            solutions.append("Process main elements systematically")
        
        # Soluções genéricas
        solutions.extend([
            "Use analytical methods for data processing",
            "Apply machine learning techniques for prediction",
            "Implement iterative improvement process"
        ])
        
        return solutions
    
    async def _evaluate_solutions(self, solutions: List[str]) -> Dict[str, Any]:
        """Avalia e seleciona melhor solução"""
        evaluations = []
        
        for i, solution in enumerate(solutions):
            # Avaliação simplificada
            score = 0.5 + (i * 0.1)  # Preferir soluções anteriores
            confidence = min(0.9, 0.6 + (len(solution) / 100))
            
            evaluations.append({
                'solution': solution,
                'score': score,
                'confidence': confidence,
                'ranking': i + 1
            })
        
        # Selecionar melhor solução
        best_solution = max(evaluations, key=lambda x: x['score'])
        
        return {
            'best_solution': best_solution['solution'],
            'confidence': best_solution['confidence'],
            'all_evaluations': evaluations,
            'reasoning_summary': f"Selected solution ranked #{best_solution['ranking']}"
        }


class CognitiveEngine:
    """Motor cognitivo principal"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.cognitive.engine", "cognitive_engine")
        self.memory = CognitiveMemory()
        self.reasoning = ReasoningEngine()
        self.context_window = deque(maxlen=50)
        self.response_history = []
        self.personality_traits = {
            'analytical': 0.8,
            'creative': 0.6,
            'cautious': 0.7,
            'helpful': 0.9
        }
        self.conversation_state = {
            'topic': None,
            'context': {},
            'user_preferences': {},
            'last_interaction': None
        }
    
    @log_execution(component="cognitive", operation="process_input")
    async def process_input(
        self, 
        user_input: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Processa entrada do usuário com raciocínio cognitivo"""
        
        # 1. Armazenar entrada na memória de trabalho
        await self.memory.store_memory(
            content=user_input,
            memory_type=MemoryType.WORKING,
            importance=0.6,
            context=context or {},
            tags=['user_input', 'conversation']
        )
        
        # 2. Recuperar memórias relevantes
        relevant_memories = await self.memory.retrieve_memory(
            query=user_input,
            limit=5
        )
        
        # 3. Analisar intenção do usuário
        intent = await self._analyze_user_intent(user_input, context)
        
        # 4. Gerar raciocínio
        reasoning_steps = await self.reasoning.chain_of_thought(
            problem=user_input,
            context={**context or {}, 'intent': intent, 'memories': relevant_memories}
        )
        
        # 5. Gerar resposta cognitiva
        response = await self._generate_cognitive_response(
            user_input=user_input,
            intent=intent,
            reasoning_steps=reasoning_steps,
            memories=relevant_memories,
            context=context
        )
        
        # 6. Armazenar resposta na memória
        await self.memory.store_memory(
            content=response['text'],
            memory_type=MemoryType.EPISODIC,
            importance=response.get('confidence', 0.5),
            context={
                'user_input': user_input,
                'intent': intent,
                'reasoning_steps': [step.to_dict() for step in reasoning_steps]
            },
            tags=['ai_response', 'conversation']
        )
        
        # 7. Atualizar estado da conversação
        self._update_conversation_state(user_input, response, intent)
        
        return response
    
    async def _analyze_user_intent(self, user_input: str, context: Optional[Dict[str, Any]]) -> str:
        """Analisa intenção do usuário"""
        input_lower = user_input.lower()
        
        # Padrões de intenção
        intents = {
            'question': ['what', 'how', 'why', 'when', 'where', '?'],
            'request': ['please', 'can you', 'would you', 'help'],
            'command': ['do', 'execute', 'run', 'start', 'stop'],
            'information': ['tell me', 'show me', 'explain', 'describe'],
            'analysis': ['analyze', 'evaluate', 'assess', 'review'],
            'prediction': ['predict', 'forecast', 'expect', 'will']
        }
        
        for intent, patterns in intents.items():
            if any(pattern in input_lower for pattern in patterns):
                return intent
        
        return 'general'
    
    async def _generate_cognitive_response(
        self,
        user_input: str,
        intent: str,
        reasoning_steps: List[ReasoningStep],
        memories: List[MemoryItem],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Gera resposta cognitiva contextualizada"""
        
        # Base da resposta no último passo de raciocínio
        final_step = reasoning_steps[-1] if reasoning_steps else None
        
        if final_step and final_step.output:
            base_response = str(final_step.output)
        else:
            base_response = "I understand your request and will help you with that."
        
        # Enriquecer com contexto de memórias
        if memories:
            memory_context = "Based on previous interactions and knowledge: "
            base_response = f"{memory_context} {base_response}"
        
        # Adicionar personalidade
        personality_modifier = self._apply_personality(base_response)
        
        # Estruturar resposta completa
        response = {
            'text': personality_modifier,
            'intent': intent,
            'confidence': final_step.confidence if final_step else 0.5,
            'reasoning_summary': self._summarize_reasoning(reasoning_steps),
            'memory_references': [mem.id for mem in memories],
            'context_used': bool(context),
            'timestamp': datetime.now().isoformat(),
            'response_type': 'cognitive'
        }
        
        return response
    
    def _apply_personality(self, response: str) -> str:
        """Aplica traços de personalidade à resposta"""
        modified_response = response
        
        # Traço analítico: adicionar estrutura
        if self.personality_traits['analytical'] > 0.7:
            if not any(marker in modified_response for marker in ['First,', 'Second,', 'Finally']):
                modified_response = f"Based on my analysis: {modified_response}"
        
        # Traço útil: adicionar oferecimento de ajuda
        if self.personality_traits['helpful'] > 0.8:
            if "Let me know" not in modified_response:
                modified_response += "\n\nLet me know if you need any clarification or additional assistance."
        
        # Traço cauteloso: adicionar qualificação
        if self.personality_traits['cautious'] > 0.7:
            if "might" not in modified_response and "could" not in modified_response:
                words = modified_response.split()
                if words and words[0].lower() not in ['this', 'that', 'it']:
                    modified_response = f"This might {modified_response.lower()}"
        
        return modified_response
    
    def _summarize_reasoning(self, steps: List[ReasoningStep]) -> str:
        """Resume o processo de raciocínio"""
        if not steps:
            return "No reasoning steps recorded."
        
        step_descriptions = [step.description for step in steps]
        return f"Reasoning process: {' -> '.join(step_descriptions)}"
    
    def _update_conversation_state(self, user_input: str, response: Dict[str, Any], intent: str):
        """Atualiza estado da conversação"""
        self.conversation_state.update({
            'last_interaction': datetime.now(),
            'last_intent': intent,
            'interaction_count': self.conversation_state.get('interaction_count', 0) + 1
        })
        
        # Extrair tópicos principais
        if intent == 'question':
            self.conversation_state['topic'] = 'inquiry'
        elif intent == 'request':
            self.conversation_state['topic'] = 'assistance'
        elif intent == 'analysis':
            self.conversation_state['topic'] = 'analysis'
        
        # Armazenar no histórico
        self.response_history.append({
            'timestamp': datetime.now(),
            'user_input': user_input,
            'ai_response': response,
            'intent': intent
        })
        
        # Manter histórico limitado
        if len(self.response_history) > 100:
            self.response_history = self.response_history[-100:]
    
    async def get_cognitive_state(self) -> Dict[str, Any]:
        """Retorna estado cognitivo completo"""
        return {
            'memory_stats': self.memory.get_memory_stats(),
            'reasoning_steps_count': len(self.reasoning.reasoning_steps),
            'conversation_state': self.conversation_state,
            'personality_traits': self.personality_traits,
            'response_history_count': len(self.response_history),
            'context_window_size': len(self.context_window)
        }
    
    async def consolidate_memories(self) -> Dict[str, Any]:
        """Consolida memórias e retorna estatísticas"""
        consolidated = await self.memory.consolidate_memory()
        
        return {
            'memories_consolidated': consolidated,
            'memory_stats': self.memory.get_memory_stats(),
            'timestamp': datetime.now().isoformat()
        }


# Função de conveniência para obter instância do motor cognitivo
_cognitive_engine_instance = None

def get_cognitive_engine() -> CognitiveEngine:
    """Obtém instância singleton do motor cognitivo"""
    global _cognitive_engine_instance
    if _cognitive_engine_instance is None:
        _cognitive_engine_instance = CognitiveEngine()
    return _cognitive_engine_instance

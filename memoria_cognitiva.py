"""
VHALINOR Memória Cognitiva v7.0 - Edição Ultimate
===================================================
Sistema de memória cognitiva multi-camada avançado com:
- Memória sensorial (ultra curto prazo)
- Memória de trabalho (curto prazo)
- Memória de curto prazo
- Memória de longo prazo
- Memória episódica
- Memória semântica
- Memória procedural
- Memória emocional
- Memória holográfica
- Memória quântica
- Memória preditiva
- Memória associativa avançada
- Memória flashbulb
- Memória prospectiva
- Memória autobiográfica

@module memoria_cognitiva
@author VHALINOR Team
@version 7.0.0
@since 2026-04-07
"""

from typing import Dict, List, Any, Optional, Tuple, Set, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum, auto
from collections import deque, defaultdict, Counter
import hashlib
import json
import pickle
import asyncio
import threading
import logging
import numpy as np
from abc import ABC, abstractmethod
import heapq
from concurrent.futures import ThreadPoolExecutor
import weakref

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TipoMemoria(Enum):
    """Tipos de memória cognitiva expandidos"""
    SENSORIAL = "sensorial"              # Milissegundos a segundos
    TRABALHO = "trabalho"                # Segundos a minutos
    CURTO_PRAZO = "curto_prazo"          # Minutos a horas
    LONGO_PRAZO = "longo_prazo"          # Dias a anos
    EPISODICA = "episodica"              # Eventos específicos
    SEMANTICA = "semantica"              # Conhecimento geral
    PROCEDURAL = "procedural"            # Habilidades e procedimentos
    EMOCIONAL = "emocional"              # Memórias com carga emocional
    HOLOGRAPHICA = "holographica"        # Memórias distribuídas
    QUANTICA = "quantica"                # Estados superpostos
    PREDITIVA = "preditiva"              # Previsões futuras
    FLASHBULB = "flashbulb"              # Memórias vívidas de eventos marcantes
    PROSPECTIVA = "prospectiva"          # Planos e intenções futuras
    AUTOBIOGRAFICA = "autobiografica"    # Narrativa pessoal


class EstadoEmocional(Enum):
    """Estados emocionais para memória emocional"""
    ALEGRIA = "alegria"
    TRISTEZA = "tristeza"
    MEDO = "medo"
    RAIVA = "raiva"
    SURPRESA = "surpresa"
    NOJO = "nojo"
    CONFIANCA = "confianca"
    ANTECIPACAO = "anticipacao"
    NEUTRO = "neutro"


class NivelConsolidacao(Enum):
    """Níveis de consolidação da memória"""
    CRUA = auto()      # Não processada
    LEVE = auto()      # Parcialmente processada
    MEDIA = auto()     # Moderadamente consolidada
    FORTE = auto()     # Fortemente consolidada
    PERMANENTE = auto() # Permanente (nunca esquecida)


@dataclass
class EmocaoAssociada:
    """Emoção associada a uma memória"""
    tipo: EstadoEmocional
    intensidade: float  # 0.0 a 1.0
    duracao: timedelta
    impacto: float = 0.0  # Impacto na importância da memória


@dataclass
class ItemMemoria:
    """Item de memória aprimorado"""
    id: str
    conteudo: Any
    tipo: TipoMemoria
    timestamp: datetime
    importancia: float = 0.5  # 0.0 a 1.0
    acessos: int = 0
    ultimo_acesso: Optional[datetime] = None
    associacoes: List[str] = field(default_factory=list)
    contexto: Dict[str, Any] = field(default_factory=dict)
    
    # Novos campos
    emocao: Optional[EmocaoAssociada] = None
    nivel_consolidacao: NivelConsolidacao = NivelConsolidacao.CRUA
    metadados: Dict[str, Any] = field(default_factory=dict)
    tags: Set[str] = field(default_factory=set)
    peso_semantico: float = 0.0
    vetor_embedding: Optional[np.ndarray] = None
    holograma: Optional[bytes] = None
    predicoes_associadas: List[str] = field(default_factory=list)
    flashbulb_intensity: float = 0.0  # Para memórias flashbulb
    reforco_sinaptico: float = 1.0  # Força da conexão neural
    
    @property
    def idade(self) -> timedelta:
        """Calcular idade do item"""
        return datetime.now(timezone.utc) - self.timestamp
    
    @property
    def reforco(self) -> float:
        """Calcular força de reforço da memória (Hebbian learning)"""
        if self.acessos == 0:
            return self.importancia * 0.5
        
        import math
        base = math.log(self.acessos + 1) * 0.1
        
        # Fator emocional
        fator_emocional = 1.0
        if self.emocao:
            fator_emocional = 1.0 + self.emocao.intensidade * 0.5
        
        # Flashbulb intensifica reforço
        fator_flashbulb = 1.0 + self.flashbulb_intensity * 2.0
        
        return min(1.0, self.importancia * (base + 0.5) * fator_emocional * fator_flashbulb)
    
    def to_dict(self) -> Dict:
        """Converter para dicionário"""
        return {
            'id': self.id,
            'conteudo': str(self.conteudo)[:200],  # Limit for serialization
            'tipo': self.tipo.value,
            'timestamp': self.timestamp.isoformat(),
            'importancia': self.importancia,
            'acessos': self.acessos,
            'ultimo_acesso': self.ultimo_acesso.isoformat() if self.ultimo_acesso else None,
            'associacoes': self.associacoes,
            'contexto': self.contexto,
            'tags': list(self.tags),
            'reforco': self.reforco
        }


class ProcessadorMemoria(ABC):
    """Classe base para processadores de memória"""
    
    @abstractmethod
    def processar(self, item: ItemMemoria) -> ItemMemoria:
        pass


class ProcessadorEmocional(ProcessadorMemoria):
    """Processador de emoções para memórias"""
    
    def processar(self, item: ItemMemoria) -> ItemMemoria:
        if item.emocao:
            # Emoções fortes aumentam importância
            item.importancia = min(1.0, item.importancia + item.emocao.intensidade * 0.3)
            
            # Memórias emocionais são consolidadas mais rápido
            if item.emocao.intensidade > 0.7:
                item.nivel_consolidacao = min(
                    NivelConsolidacao.FORTE,
                    NivelConsolidacao(item.nivel_consolidacao.value + 1)
                )
        
        return item


class ProcessadorSemantico(ProcessadorMemoria):
    """Processador semântico para memórias"""
    
    def __init__(self, modelo_embedding: Optional[Any] = None):
        self.modelo_embedding = modelo_embedding
    
    def processar(self, item: ItemMemoria) -> ItemMemoria:
        if isinstance(item.conteudo, str):
            # Calcular peso semântico baseado em palavras raras
            palavras = item.conteudo.lower().split()
            frequencias = Counter(palavras)
            palavras_raras = sum(1 for freq in frequencias.values() if freq == 1)
            item.peso_semantico = min(1.0, palavras_raras / max(1, len(palavras)))
            
            # Extrair tags automaticamente
            stopwords = {'o', 'a', 'os', 'as', 'um', 'uma', 'de', 'da', 'do', 'em', 'para', 'com'}
            item.tags.update({p for p in palavras if len(p) > 3 and p not in stopwords})
        
        return item


class RedeNeuralAssociativa:
    """
    Rede neural para associações entre memórias
    Implementa aprendizado Hebbiano
    """
    
    def __init__(self, tamanho_maximo: int = 10000):
        self.conexoes = defaultdict(lambda: defaultdict(float))
        self.tamanho_maximo = tamanho_maximo
        self.historico_ativacao = deque(maxlen=100)
    
    def criar_associacao(self, id1: str, id2: str, forca: float = 0.5):
        """Criar associação entre duas memórias"""
        self.conexoes[id1][id2] = min(1.0, self.conexoes[id1][id2] + forca * 0.1)
        self.conexoes[id2][id1] = min(1.0, self.conexoes[id2][id1] + forca * 0.1)
    
    def fortalecer_associacao(self, id1: str, id2: str, incremento: float = 0.05):
        """Fortalecer associação existente"""
        if id2 in self.conexoes[id1]:
            self.conexoes[id1][id2] = min(1.0, self.conexoes[id1][id2] + incremento)
            self.conexoes[id2][id1] = min(1.0, self.conexoes[id2][id1] + incremento)
    
    def get_associacoes(self, id_item: str, limite: int = 10) -> List[Tuple[str, float]]:
        """Obter memórias associadas mais fortes"""
        if id_item not in self.conexoes:
            return []
        
        associacoes = list(self.conexoes[id_item].items())
        associacoes.sort(key=lambda x: x[1], reverse=True)
        
        return associacoes[:limite]
    
    def decaimento_sinaptico(self):
        """Aplicar decaimento às conexões sinápticas"""
        for id1 in list(self.conexoes.keys()):
            for id2 in list(self.conexoes[id1].keys()):
                self.conexoes[id1][id2] *= 0.999  # Decaimento lento
                if self.conexoes[id1][id2] < 0.01:
                    del self.conexoes[id1][id2]
            
            if not self.conexoes[id1]:
                del self.conexoes[id1]


class MemoriaHolografica:
    """
    Memória holográfica distribuída
    Permite recuperação parcial de memórias
    """
    
    def __init__(self, tamanho: int = 1000):
        self.hologramas: Dict[str, np.ndarray] = {}
        self.tamanho = tamanho
    
    def armazenar_holograma(self, id_item: str, vetor: np.ndarray):
        """Armazenar representação holográfica"""
        if len(vetor) > self.tamanho:
            vetor = vetor[:self.tamanho]
        elif len(vetor) < self.tamanho:
            vetor = np.pad(vetor, (0, self.tamanho - len(vetor)))
        
        self.hologramas[id_item] = vetor
    
    def recuperar_parcial(self, fragmento: np.ndarray, limiar: float = 0.7) -> List[Tuple[str, float]]:
        """Recuperar memórias a partir de fragmento"""
        resultados = []
        
        for id_item, holograma in self.hologramas.items():
            similaridade = self._cosine_similarity(fragmento, holograma)
            if similaridade > limiar:
                resultados.append((id_item, similaridade))
        
        resultados.sort(key=lambda x: x[1], reverse=True)
        return resultados
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calcular similaridade coseno"""
        if len(a) != len(b):
            return 0.0
        
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return np.dot(a, b) / (norm_a * norm_b)


class MemoriaQuantica:
    """
    Memória quântica simulada
    Estados superpostos de memórias
    """
    
    def __init__(self):
        self.superposicoes: Dict[str, Dict[str, float]] = defaultdict(dict)
    
    def criar_superposicao(self, id_novo: str, ids_existentes: List[str], probabilidades: List[float]):
        """Criar estado de superposição"""
        if len(ids_existentes) != len(probabilidades):
            raise ValueError("IDs e probabilidades devem ter mesmo comprimento")
        
        # Normalizar probabilidades
        total = sum(probabilidades)
        probabilidades = [p / total for p in probabilidades]
        
        for id_existente, prob in zip(ids_existentes, probabilidades):
            self.superposicoes[id_novo][id_existente] = prob
    
    def colapsar(self, id_item: str) -> Optional[str]:
        """Colapsar superposição para um estado definido"""
        if id_item not in self.superposicoes:
            return None
        
        estados = self.superposicoes[id_item]
        if not estados:
            return None
        
        # Selecionar estado baseado em probabilidades
        import random
        r = random.random()
        acumulado = 0
        
        for estado, prob in estados.items():
            acumulado += prob
            if r <= acumulado:
                return estado
        
        return list(estados.keys())[0]


class MemoriaPreditiva:
    """
    Memória preditiva - prevê estados futuros baseado em padrões
    """
    
    def __init__(self, janela_temporal: int = 10):
        self.padroes: Dict[str, List[Any]] = defaultdict(list)
        self.previsoes: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.janela_temporal = janela_temporal
    
    def registrar_padrao(self, id_contexto: str, sequencia: List[Any]):
        """Registrar padrão temporal"""
        self.padroes[id_contexto].extend(sequencia)
        
        # Manter apenas janela mais recente
        if len(self.padroes[id_contexto]) > self.janela_temporal * 10:
            self.padroes[id_contexto] = self.padroes[id_contexto][-self.janela_temporal * 10:]
        
        # Atualizar previsões
        self._atualizar_previsoes(id_contexto)
    
    def _atualizar_previsoes(self, id_contexto: str):
        """Atualizar modelo preditivo"""
        padroes = self.padroes[id_contexto]
        if len(padroes) < self.janela_temporal + 1:
            return
        
        # Contar transições
        transicoes = defaultdict(Counter)
        for i in range(len(padroes) - self.janela_temporal):
            contexto = tuple(padroes[i:i+self.janela_temporal])
            proximo = padroes[i+self.janela_temporal]
            transicoes[contexto][proximo] += 1
        
        # Calcular probabilidades
        previsoes = defaultdict(dict)
        for contexto, contagens in transicoes.items():
            total = sum(contagens.values())
            for proximo, count in contagens.items():
                previsoes[str(contexto)][proximo] = count / total
        
        self.previsoes[id_contexto] = previsoes
    
    def prever(self, id_contexto: str, contexto_atual: Tuple) -> List[Tuple[Any, float]]:
        """Prever próximo estado"""
        if id_contexto not in self.previsoes:
            return []
        
        previsoes_contexto = self.previsoes[id_contexto]
        chave = str(contexto_atual)
        
        if chave not in previsoes_contexto:
            return []
        
        resultados = list(previsoes_contexto[chave].items())
        resultados.sort(key=lambda x: x[1], reverse=True)
        
        return resultados


class MemoriaFlashbulb:
    """
    Memória flashbulb - memórias extremamente vívidas de eventos marcantes
    """
    
    def __init__(self):
        self.flashbulbs: Dict[str, ItemMemoria] = {}
        self.eventos_marcantes: List[Dict] = []
    
    def registrar_evento_marcante(self, evento: Dict, intensidade: float):
        """Registrar evento marcante"""
        evento['intensidade'] = intensidade
        evento['timestamp'] = datetime.now(timezone.utc)
        self.eventos_marcantes.append(evento)
        
        # Manter apenas eventos mais recentes
        if len(self.eventos_marcantes) > 100:
            self.eventos_marcantes = self.eventos_marcantes[-100:]
    
    def criar_flashbulb(self, item: ItemMemoria, intensidade: float) -> ItemMemoria:
        """Criar memória flashbulb"""
        item.flashbulb_intensity = intensidade
        item.importancia = min(1.0, item.importancia + intensidade * 0.5)
        
        # Flashbulb é imediatamente consolidada
        item.nivel_consolidacao = NivelConsolidacao.FORTE
        
        self.flashbulbs[item.id] = item
        
        return item
    
    def get_flashbulbs(self, intensidade_minima: float = 0.5) -> List[ItemMemoria]:
        """Obter flashbulbs acima da intensidade mínima"""
        return [item for item in self.flashbulbs.values() 
                if item.flashbulb_intensity >= intensidade_minima]


class MemoriaCognitiva:
    """
    Sistema completo de memória cognitiva inspirado na arquitetura
    da memória humana - Versão Ultimate
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        
        # Capacidades expandidas por tipo de memória
        self.capacidades = {
            TipoMemoria.SENSORIAL: 1000,      # 1000 itens
            TipoMemoria.TRABALHO: 7,          # 7±2 itens (lei de Miller)
            TipoMemoria.CURTO_PRAZO: 10000,
            TipoMemoria.LONGO_PRAZO: 1000000,
            TipoMemoria.EPISODICA: 100000,
            TipoMemoria.SEMANTICA: 500000,
            TipoMemoria.PROCEDURAL: 100000,
            TipoMemoria.EMOCIONAL: 50000,
            TipoMemoria.HOLOGRAPHICA: 50000,
            TipoMemoria.QUANTICA: 10000,
            TipoMemoria.PREDITIVA: 100000,
            TipoMemoria.FLASHBULB: 1000,
            TipoMemoria.PROSPECTIVA: 10000,
            TipoMemoria.AUTOBIOGRAFICA: 10000
        }
        
        # Decay rates aprimorados (meia-vida em segundos)
        self.decay_rates = {
            TipoMemoria.SENSORIAL: 0.5,       # 0.5 segundo
            TipoMemoria.TRABALHO: 15,         # 15 segundos
            TipoMemoria.CURTO_PRAZO: 1800,    # 30 minutos
            TipoMemoria.LONGO_PRAZO: 86400 * 365 * 2,  # 2 anos
            TipoMemoria.EPISODICA: 86400 * 60,         # 60 dias
            TipoMemoria.SEMANTICA: 86400 * 365 * 20,   # 20 anos
            TipoMemoria.PROCEDURAL: 86400 * 365 * 10,  # 10 anos
            TipoMemoria.EMOCIONAL: 86400 * 90,         # 90 dias
            TipoMemoria.HOLOGRAPHICA: 86400 * 180,     # 180 dias
            TipoMemoria.QUANTICA: 3600,                # 1 hora
            TipoMemoria.PREDITIVA: 86400 * 30,         # 30 dias
            TipoMemoria.FLASHBULB: 86400 * 365 * 50,   # 50 anos
            TipoMemoria.PROSPECTIVA: 86400 * 7,        # 7 dias
            TipoMemoria.AUTOBIOGRAFICA: 86400 * 365 * 100  # 100 anos
        }
        
        # Armazenamentos
        self.memorias: Dict[TipoMemoria, Dict[str, ItemMemoria]] = {
            tipo: {} for tipo in TipoMemoria
        }
        
        # Sistemas avançados
        self.rede_associativa = RedeNeuralAssociativa()
        self.memoria_holografica = MemoriaHolografica()
        self.memoria_quantica = MemoriaQuantica()
        self.memoria_preditiva = MemoriaPreditiva()
        self.memoria_flashbulb = MemoriaFlashbulb()
        
        # Processadores
        self.processadores = [
            ProcessadorEmocional(),
            ProcessadorSemantico()
        ]
        
        # Índices e estruturas de busca
        self.indice_temporal: deque = deque(maxlen=100000)
        self.indice_conteudo: Dict[str, List[str]] = defaultdict(list)
        self.indice_por_tag: Dict[str, Set[str]] = defaultdict(set)
        self.indice_semantico: Dict[str, np.ndarray] = {}
        
        # Fila de prioridade para consolidação
        self.fila_consolidacao = []
        
        # Thread pool para processamento assíncrono
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Métricas e estatísticas
        self.metricas = {
            'total_armazenamentos': 0,
            'total_recuperacoes': 0,
            'total_associacoes': 0,
            'total_consolidacoes': 0,
            'memorias_esquecidas': 0
        }
        
        # Cache de recuperação frequente
        self.cache_recuperacao = {}
        
        logger.info("Sistema de Memória Cognitiva V7.0 inicializado")
    
    async def armazenar(
        self,
        conteudo: Any,
        tipo: TipoMemoria,
        importancia: float = 0.5,
        contexto: Optional[Dict] = None,
        associacoes: Optional[List[str]] = None,
        emocao: Optional[EmocaoAssociada] = None,
        tags: Optional[Set[str]] = None,
        vetor_embedding: Optional[np.ndarray] = None,
        is_flashbulb: bool = False,
        flashbulb_intensity: float = 0.0
    ) -> str:
        """Armazenar item na memória (versão assíncrona)"""
        # Gerar ID único
        id_item = hashlib.sha256(
            f"{conteudo}{datetime.now(timezone.utc).timestamp()}{id(conteudo)}".encode()
        ).hexdigest()[:32]
        
        item = ItemMemoria(
            id=id_item,
            conteudo=conteudo,
            tipo=tipo,
            timestamp=datetime.now(timezone.utc),
            importancia=importancia,
            contexto=contexto or {},
            associacoes=associacoes or [],
            emocao=emocao,
            tags=tags or set(),
            vetor_embedding=vetor_embedding
        )
        
        # Aplicar processadores
        for processador in self.processadores:
            item = processador.processar(item)
        
        # Criar flashbulb se necessário
        if is_flashbulb or flashbulb_intensity > 0:
            item = self.memoria_flashbulb.criar_flashbulb(item, 
                flashbulb_intensity if flashbulb_intensity > 0 else importancia)
        
        # Verificar capacidade
        if len(self.memorias[tipo]) >= self.capacidades[tipo]:
            await self._evict_async(tipo)
        
        # Armazenar
        self.memorias[tipo][id_item] = item
        self.indice_temporal.append((tipo, id_item))
        self.metricas['total_armazenamentos'] += 1
        
        # Indexar
        await self._indexar_conteudo_async(item)
        
        # Criar associações
        if associacoes:
            for assoc_id in associacoes:
                self.rede_associativa.criar_associacao(id_item, assoc_id)
                self.metricas['total_associacoes'] += 1
        
        # Consolidar se necessário
        if importancia > 0.8 or (emocao and emocao.intensidade > 0.7):
            heapq.heappush(self.fila_consolidacao, 
                          (-item.importancia, datetime.now(timezone.utc), id_item))
        
        # Registrar padrão preditivo
        if tipo in [TipoMemoria.EPISODICA, TipoMemoria.SEMANTICA]:
            contexto_key = str(contexto.get('categoria', 'default')) if contexto else 'default'
            self.memoria_preditiva.registrar_padrao(contexto_key, [conteudo])
        
        # Armazenar holograma se disponível
        if vetor_embedding is not None:
            self.memoria_holografica.armazenar_holograma(id_item, vetor_embedding)
        
        logger.debug(f"Memória armazenada: {id_item} ({tipo.value})")
        return id_item
    
    def recuperar(
        self, 
        id_item: str, 
        tipo: Optional[TipoMemoria] = None,
        usar_cache: bool = True
    ) -> Optional[ItemMemoria]:
        """Recuperar item da memória com cache"""
        # Verificar cache
        if usar_cache and id_item in self.cache_recuperacao:
            item = self.cache_recuperacao[id_item]()
            if item is not None:
                item.acessos += 1
                item.ultimo_acesso = datetime.now(timezone.utc)
                return item
        
        if tipo:
            item = self.memorias[tipo].get(id_item)
        else:
            # Buscar em todos os tipos
            item = None
            for t in TipoMemoria:
                if id_item in self.memorias[t]:
                    item = self.memorias[t][id_item]
                    break
        
        if item:
            item.acessos += 1
            item.ultimo_acesso = datetime.now(timezone.utc)
            self.metricas['total_recuperacoes'] += 1
            
            # Atualizar cache (weak reference)
            self.cache_recuperacao[id_item] = weakref.ref(item)
            
            # Fortalecer associações ativadas
            for assoc_id, _ in self.rede_associativa.get_associacoes(id_item, limite=3):
                self.rede_associativa.fortalecer_associacao(id_item, assoc_id, 0.01)
        
        return item
    
    async def buscar_semantica(
        self,
        query: str,
        tipo: Optional[TipoMemoria] = None,
        limite: int = 10,
        usar_holograma: bool = True
    ) -> List[ItemMemoria]:
        """Busca semântica avançada"""
        resultados = []
        
        # Busca por similaridade de embedding
        if usar_holograma and self.indice_semantico:
            # Placeholder para busca por similaridade coseno
            # Implementação real usaria FAISS ou similar
            pass
        
        # Busca tradicional
        tipos_busca = [tipo] if tipo else list(TipoMemoria)
        
        for t in tipos_busca:
            for item in self.memorias[t].values():
                score = await self._calcular_similaridade_avancada(query, item)
                if score > 0.3:
                    resultados.append((item, score))
        
        # Ordenar por score e retornar top N
        resultados.sort(key=lambda x: x[1], reverse=True)
        
        # Atualizar acessos
        for item, _ in resultados[:limite]:
            item.acessos += 1
            item.ultimo_acesso = datetime.now(timezone.utc)
        
        return [item for item, _ in resultados[:limite]]
    
    async def consolidar_memorias(self):
        """Consolidar memórias periodicamente"""
        while self.fila_consolidacao:
            _, tempo, id_item = heapq.heappop(self.fila_consolidacao)
            
            # Verificar se ainda está na memória de curto prazo
            if id_item in self.memorias[TipoMemoria.CURTO_PRAZO]:
                item = self.memorias[TipoMemoria.CURTO_PRAZO][id_item]
                await self._consolidar_para_longo_prazo_async(item)
                del self.memorias[TipoMemoria.CURTO_PRAZO][id_item]
                self.metricas['total_consolidacoes'] += 1
    
    async def lembrar_semelhantes(
        self,
        conteudo: Any,
        limiar: float = 0.5,
        limite: int = 10
    ) -> List[ItemMemoria]:
        """Encontrar memórias semelhantes"""
        resultados = []
        
        for tipo in TipoMemoria:
            for item in self.memorias[tipo].values():
                similaridade = await self._calcular_similaridade_avancada(str(conteudo), item)
                if similaridade > limiar:
                    resultados.append((item, similaridade))
        
        resultados.sort(key=lambda x: x[1], reverse=True)
        return [item for item, _ in resultados[:limite]]
    
    async def associar_memorias(
        self,
        id_item1: str,
        id_item2: str,
        forca: float = 0.5
    ):
        """Criar associação forte entre duas memórias"""
        self.rede_associativa.criar_associacao(id_item1, id_item2, forca)
        
        # Registrar em ambos os itens
        for tipo in TipoMemoria:
            if id_item1 in self.memorias[tipo]:
                if id_item2 not in self.memorias[tipo][id_item1].associacoes:
                    self.memorias[tipo][id_item1].associacoes.append(id_item2)
            if id_item2 in self.memorias[tipo]:
                if id_item1 not in self.memorias[tipo][id_item2].associacoes:
                    self.memorias[tipo][id_item2].associacoes.append(id_item1)
    
    async def revisitar_memoria(self, id_item: str) -> Optional[ItemMemoria]:
        """
        Revisitar memória (como ato de lembrar, reforça a memória)
        """
        item = self.recuperar(id_item)
        if item:
            # Revisitar fortalece a memória
            item.reforco_sinaptico *= 1.1
            item.acessos += 1
            
            # Possível consolidação se revisitada muitas vezes
            if item.acessos >= 5 and item.nivel_consolidacao == NivelConsolidacao.CRUA:
                item.nivel_consolidacao = NivelConsolidacao.LEVE
                await self._consolidar_para_longo_prazo_async(item)
        
        return item
    
    async def _evict_async(self, tipo: TipoMemoria):
        """Remover item menos importante para liberar espaço"""
        if not self.memorias[tipo]:
            return
        
        # Encontrar item com menor score
        menor_score = float('inf')
        id_remover = None
        
        for id_item, item in self.memorias[tipo].items():
            # Score = importância * reforço / idade
            idade_horas = item.idade.total_seconds() / 3600
            if idade_horas > 0:
                score = item.importancia * item.reforco / (1 + idade_horas)
            else:
                score = item.importancia * item.reforco
            
            if score < menor_score:
                menor_score = score
                id_remover = id_item
        
        if id_remover:
            await self._esquecer_async(id_remover, tipo)
            self.metricas['memorias_esquecidas'] += 1
    
    async def _esquecer_async(self, id_item: str, tipo: TipoMemoria):
        """Esquecer memória"""
        if id_item in self.memorias[tipo]:
            del self.memorias[tipo][id_item]
            
            # Remover de índices
            # (Implementação de limpeza de índices)
    
    async def _consolidar_para_longo_prazo_async(self, item: ItemMemoria):
        """Consolidar item para memória de longo prazo"""
        novo_item = ItemMemoria(
            id=item.id,
            conteudo=item.conteudo,
            tipo=TipoMemoria.LONGO_PRAZO,
            timestamp=item.timestamp,
            importancia=item.importancia,
            acessos=item.acessos,
            ultimo_acesso=item.ultimo_acesso,
            associacoes=item.associacoes.copy(),
            contexto=item.contexto.copy(),
            emocao=item.emocao,
            nivel_consolidacao=item.nivel_consolidacao,
            tags=item.tags.copy(),
            vetor_embedding=item.vetor_embedding
        )
        
        if len(self.memorias[TipoMemoria.LONGO_PRAZO]) >= self.capacidades[TipoMemoria.LONGO_PRAZO]:
            await self._evict_async(TipoMemoria.LONGO_PRAZO)
        
        self.memorias[TipoMemoria.LONGO_PRAZO][item.id] = novo_item
    
    async def _indexar_conteudo_async(self, item: ItemMemoria):
        """Indexar conteúdo para busca"""
        # Indexar palavras-chave
        if isinstance(item.conteudo, str):
            palavras = item.conteudo.lower().split()
            for palavra in palavras:
                if len(palavra) > 2:  # Ignorar palavras muito curtas
                    self.indice_conteudo[palavra].append(item.id)
        
        # Indexar tags
        for tag in item.tags:
            self.indice_por_tag[tag].add(item.id)
    
    async def _calcular_similaridade_avancada(self, query: str, item: ItemMemoria) -> float:
        """Calcular similaridade avançada entre query e item"""
        if not isinstance(item.conteudo, str):
            return 0.0
        
        query_lower = query.lower()
        conteudo_lower = item.conteudo.lower()
        
        # Similaridade por palavras
        palavras_query = set(query_lower.split())
        palavras_conteudo = set(conteudo_lower.split())
        
        if not palavras_query:
            return 0.0
        
        # Jaccard similarity
        intersecao = len(palavras_query & palavras_conteudo)
        uniao = len(palavras_query | palavras_conteudo)
        similaridade_palavras = intersecao / uniao if uniao > 0 else 0
        
        # Bônus por tags correspondentes
        tags_query = set(query_lower.split())
        tags_match = len(tags_query & item.tags)
        bonus_tags = tags_match / max(1, len(tags_query)) * 0.3
        
        # Bônus por importância
        bonus_importancia = item.importancia * 0.2
        
        # Score final
        score = similaridade_palavras * 0.5 + bonus_tags * 0.3 + bonus_importancia * 0.2
        
        return min(1.0, score)
    
    def get_status(self) -> Dict[str, Any]:
        """Obter status detalhado da memória cognitiva"""
        return {
            'ocupacao': {
                tipo.value: {
                    'itens': len(self.memorias[tipo]),
                    'capacidade': self.capacidades[tipo],
                    'percentual': round(len(self.memorias[tipo]) / self.capacidades[tipo] * 100, 2)
                }
                for tipo in TipoMemoria
            },
            'metricas': self.metricas,
            'total_itens': sum(len(m) for m in self.memorias.values()),
            'indice_temporal_size': len(self.indice_temporal),
            'indice_conteudo_size': len(self.indice_conteudo),
            'indice_tags_size': len(self.indice_por_tag),
            'associacoes_total': sum(len(conn) for conn in self.rede_associativa.conexoes.values()),
            'flashbulbs_total': len(self.memoria_flashbulb.flashbulbs),
            'cache_size': len(self.cache_recuperacao)
        }
    
    def exportar_memorias(self, formato: str = 'json') -> Union[str, bytes]:
        """Exportar memórias para backup"""
        dados = {
            'versao': '7.0.0',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'memorias': {
                tipo.value: [
                    item.to_dict() for item in memorias.values()
                ] for tipo, memorias in self.memorias.items()
            },
            'associacoes': dict(self.rede_associativa.conexoes),
            'metricas': self.metricas
        }
        
        if formato == 'json':
            return json.dumps(dados, indent=2, default=str)
        elif formato == 'pickle':
            return pickle.dumps(dados)
        else:
            raise ValueError(f"Formato não suportado: {formato}")
    
    async def importar_memorias(self, dados: Union[str, bytes], formato: str = 'json'):
        """Importar memórias de backup"""
        if formato == 'json':
            if isinstance(dados, str):
                dados_dict = json.loads(dados)
            else:
                dados_dict = json.loads(dados.decode())
        elif formato == 'pickle':
            if isinstance(dados, bytes):
                dados_dict = pickle.loads(dados)
            else:
                dados_dict = pickle.loads(dados.encode())
        else:
            raise ValueError(f"Formato não suportado: {formato}")
        
        # Restaurar memórias
        for tipo_str, items in dados_dict['memorias'].items():
            tipo = TipoMemoria(tipo_str)
            for item_dict in items:
                item = ItemMemoria(
                    id=item_dict['id'],
                    conteudo=item_dict['conteudo'],
                    tipo=tipo,
                    timestamp=datetime.fromisoformat(item_dict['timestamp']),
                    importancia=item_dict['importancia'],
                    acessos=item_dict['acessos']
                )
                self.memorias[tipo][item.id] = item
        
        # Restaurar associações
        self.rede_associativa.conexoes.clear()
        for id1, conexoes in dados_dict['associacoes'].items():
            for id2, forca in conexoes.items():
                self.rede_associativa.conexoes[id1][id2] = forca
        
        self.metricas = dados_dict['metricas']
        
        logger.info("Memórias importadas com sucesso")


# Exemplo de uso
async def exemplo_memoria_cognitiva():
    """Exemplo de uso do sistema de memória cognitiva"""
    
    # Inicializar sistema
    memoria = MemoriaCognitiva()
    
    # Armazenar memórias
    id1 = await memoria.armazenar(
        "O preço do Bitcoin subiu 10% hoje devido a notícias positivas",
        TipoMemoria.EPISODICA,
        importancia=0.9,
        tags={"bitcoin", "alta", "mercado"}
    )
    
    id2 = await memoria.armazenar(
        "RSI indica sobrecompra, possível correção",
        TipoMemoria.SEMANTICA,
        importancia=0.7,
        tags={"rsi", "tecnico", "correcao"}
    )
    
    # Criar associação
    await memoria.associar_memorias(id1, id2, forca=0.8)
    
    # Buscar memórias
    resultados = await memoria.buscar_semantica("bitcoin preço", limite=3)
    
    print("Memórias encontradas:")
    for item in resultados:
        print(f"- {item.conteudo} (Importância: {item.importancia})")
    
    # Status do sistema
    status = memoria.get_status()
    print("\nStatus da memória cognitiva:")
    print(f"Total de itens: {status['total_itens']}")
    print(f"Associações: {status['associacoes_total']}")
    
    return memoria


if __name__ == "__main__":
    # Executar exemplo
    asyncio.run(exemplo_memoria_cognitiva())
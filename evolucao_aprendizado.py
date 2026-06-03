"""
VHALINOR Evolução de Aprendizado v7.0 - Edição Evolutiva
==========================================================
Sistema de evolução de aprendizado com:
- Evolução de modelos ao longo do tempo
- Tracking de performance histórica
- Adaptação de estratégias
- Seleção natural de algoritmos
- Memória de longo prazo de aprendizado
- Transferência de conhecimento entre gerações
- Métricas de evolução
- Linhagem de modelos
- Adaptação a mudanças de regime de mercado
- Nichos ecológicos e preservação de diversidade
- Speciation (formação de espécies)
- Coevolução entre modelos
- Lamarckismo (aprendizado durante vida)
- Persistência e checkpointing

@module evolucao_aprendizado
@author VHALINOR Team
@version 7.0.0
@since 2026-04-07
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum, auto
from collections import deque, defaultdict
import hashlib
import json
import pickle
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
import heapq

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TipoEvolucao(Enum):
    """Tipos de evolução de aprendizado"""
    MUTACAO = "mutacao"           # Pequenas alterações no modelo
    CROSSOVER = "crossover"       # Combinação de modelos
    SELECAO = "selecao"           # Seleção natural
    EPIFANIA = "epifania"         # Grande insight/mudança
    CONSOLIDACAO = "consolidacao" # Refinamento gradual
    ADAPTACAO = "adaptacao"       # Adaptação a mudanças
    ESPECIACAO = "speciation"     # Formação de nova espécie
    EXTINCAO = "extincao"         # Extinção de linhagem


class EstagioEvolucao(Enum):
    """Estágios de evolução"""
    GERMINACAO = "germinacao"     # Início, aprendizado básico
    CRESCIMENTO = "crescimento"   # Desenvolvimento rápido
    MATURIDADE = "maturidade"     # Performance estável
    ESPECIALIZACAO = "especializacao"  # Foco em nicho
    FLORACAO = "floracao"         # Pico de performance
    ADAPTACAO = "adaptacao"       # Mudança de estratégia
    ESTAGNACAO = "estagnacao"     # Sem progresso
    RENASCIMENTO = "renascimento" # Reinício após crise


class TipoAdaptacao(Enum):
    """Tipos de adaptação a mudanças"""
    REGIME_VOLATILIDADE = "regime_volatilidade"
    REGIME_TENDENCIA = "regime_tendencia"
    REGIME_RANGE = "regime_range"
    MUDANCA_MACRO = "mudanca_macro"
    EVENTO_EXTERNO = "evento_externo"
    MU DANCA_CORRELACAO = "mudanca_correlacao"
    SHIFT_REGIME = "shift_regime"


class NichoEstrategico(Enum):
    """Nichos ecológicos para especialização"""
    ALTA_FREQUENCIA = "alta_frequencia"
    BAIXA_FREQUENCIA = "baixa_frequencia"
    TREND_FOLLOWING = "trend_following"
    MEAN_REVERSION = "mean_reversion"
    VOLATILIDADE_ALTA = "volatilidade_alta"
    VOLATILIDADE_BAIXA = "volatilidade_baixa"
    MERCADO_BULL = "bull_market"
    MERCADO_BEAR = "bear_market"
    ARBITRAGEM = "arbitragem"
    MOMENTUM = "momentum"


@dataclass
class GenomaModelo:
    """Genoma representando características de um modelo (versão expandida)"""
    id: str
    geracao: int
    caracteristicas: Dict[str, float]  # Pesos, thresholds, etc.
    arquitetura: str
    hiperparametros: Dict[str, Any]
    ancestral_id: Optional[str] = None
    mutacoes: List[str] = field(default_factory=list)
    timestamp_criacao: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    fitness_acumulado: float = 0.0
    idade: int = 0  # Número de gerações vividas
    nicho: Optional[NichoEstrategico] = None
    especie_id: Optional[str] = None
    memoria_lamarck: Dict[str, Any] = field(default_factory=dict)  # Conhecimento adquirido


@dataclass
class FitnessSnapshot:
    """Snapshot de fitness de um modelo"""
    timestamp: str
    fitness_score: float
    sharpe_ratio: float
    win_rate: float
    profit_factor: float
    max_drawdown: float
    trades_realizados: int
    ambiente: str  # "bull", "bear", "sideways", "volatile"
    regime_volatilidade: float = 0.0
    drawdown_duration: int = 0


@dataclass
class EventoEvolucao:
    """Evento de evolução registrado"""
    id: str
    tipo: TipoEvolucao
    geracao: int
    descricao: str
    modelo_origem: str
    modelo_destino: Optional[str]
    impacto_fitness: float
    motivacao: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class LinhagemModelo:
    """Linhagem de um modelo através das gerações"""
    modelo_id: str
    geracao: int
    ancestral_direto: Optional[str]
    descendentes: List[str] = field(default_factory=list)
    irmaos: List[str] = field(default_factory=list)
    caminho_evolucao: List[str] = field(default_factory=list)  # IDs de eventos


@dataclass
class Especie:
    """Grupo de modelos com características similares (espécie)"""
    id: str
    geracao_fundacao: int
    genomas_membros: Set[str]
    caracteristicas_centroides: Dict[str, float]
    fitness_medio: float = 0.0
    idade: int = 0
    extinta: bool = False


class EvolucaoAprendizado:
    """
    Sistema avançado de evolução de aprendizado para VHALINOR.
    Implementa conceitos de evolução natural com nichos, especiação e aprendizado lamarckiano.
    """
    
    def __init__(
        self,
        populacao_maxima: int = 20,
        num_especies_max: int = 5,
        preservar_diversidade: bool = True
    ):
        self.populacao_maxima = populacao_maxima
        self.num_especies_max = num_especies_max
        self.preservar_diversidade = preservar_diversidade
        self.geracao_atual = 0
        
        # População e genética
        self.genomas: Dict[str, GenomaModelo] = {}
        self.fitness_historico: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.linhagens: Dict[str, LinhagemModelo] = {}
        
        # Especiação
        self.especies: Dict[str, Especie] = {}
        self.especie_por_genoma: Dict[str, str] = {}  # genoma_id -> especie_id
        
        # Histórico evolutivo
        self.eventos_evolucao: deque = deque(maxlen=2000)
        self.adaptacoes_realizadas: deque = deque(maxlen=200)
        
        # Regimes de mercado
        self.regime_atual: str = "desconhecido"
        self.historico_regimes: deque = deque(maxlen=100)
        
        # Melhores performers por nicho/regime
        self.campeoes_por_nicho: Dict[str, str] = {}
        self.campeoes_por_regime: Dict[str, str] = {}
        
        # Métricas de evolução
        self.taxa_mutacao = 0.1
        self.taxa_crossover = 0.3
        self.pressao_selecao = 0.5
        self.limiar_especiacao = 0.3  # Distância para formar nova espécie
        
        # Controle de estagnação
        self.geracoes_sem_melhoria = 0
        self.melhor_fitness_historico = 0.0
        
        # Persistência
        self.checkpoint_dir = "checkpoints_evolucao"
        
        # Executor para tarefas assíncronas
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        logger.info(f"Sistema de Evolução v7.0 inicializado (pop_max={populacao_maxima})")
    
    # ------------------- Métodos principais de evolução -------------------
    
    def criar_genoma_inicial(
        self,
        caracteristicas: Dict[str, float],
        arquitetura: str,
        hiperparametros: Dict[str, Any],
        nicho: Optional[NichoEstrategico] = None
    ) -> str:
        """Criar genoma da primeira geração"""
        genoma_id = hashlib.md5(
            f"gen0_{datetime.now(timezone.utc).timestamp()}_{id(caracteristicas)}".encode()
        ).hexdigest()[:16]
        
        genoma = GenomaModelo(
            id=genoma_id,
            geracao=0,
            caracteristicas=caracteristicas,
            arquitetura=arquitetura,
            hiperparametros=hiperparametros,
            nicho=nicho
        )
        
        self.genomas[genoma_id] = genoma
        self.linhagens[genoma_id] = LinhagemModelo(
            modelo_id=genoma_id,
            geracao=0,
            ancestral_direto=None
        )
        
        # Atribuir ou criar espécie
        self._atribuir_especie(genoma_id)
        
        logger.info(f"Genoma inicial criado: {genoma_id} (nicho={nicho})")
        return genoma_id
    
    def registrar_fitness(self, genoma_id: str, snapshot: FitnessSnapshot):
        """Registrar snapshot de fitness e atualizar espécie"""
        if genoma_id not in self.fitness_historico:
            self.fitness_historico[genoma_id] = deque(maxlen=100)
        
        self.fitness_historico[genoma_id].append(snapshot)
        
        # Atualizar fitness acumulado do genoma
        self.genomas[genoma_id].fitness_acumulado = snapshot.fitness_score
        
        # Atualizar campeões por nicho
        genoma = self.genomas[genoma_id]
        if genoma.nicho:
            nicho_key = genoma.nicho.value
            if nicho_key not in self.campeoes_por_nicho:
                self.campeoes_por_nicho[nicho_key] = genoma_id
            else:
                campeao_atual = self.campeoes_por_nicho[nicho_key]
                if snapshot.fitness_score > self._get_ultimo_fitness(campeao_atual) * 1.05:
                    self.campeoes_por_nicho[nicho_key] = genoma_id
        
        # Atualizar campeões por regime
        if snapshot.ambiente not in self.campeoes_por_regime:
            self.campeoes_por_regime[snapshot.ambiente] = genoma_id
        else:
            campeao_atual = self.campeoes_por_regime[snapshot.ambiente]
            fitness_campeao = self._get_ultimo_fitness(campeao_atual)
            if snapshot.fitness_score > fitness_campeao * 1.05:
                self.campeoes_por_regime[snapshot.ambiente] = genoma_id
        
        # Atualizar fitness médio da espécie
        self._atualizar_fitness_especie(genoma_id)
    
    def _get_ultimo_fitness(self, genoma_id: str) -> float:
        """Obter último fitness registrado"""
        if genoma_id in self.fitness_historico and self.fitness_historico[genoma_id]:
            return self.fitness_historico[genoma_id][-1].fitness_score
        return 0.0
    
    def calcular_fitness_medio(self, genoma_id: str, janela: int = 10) -> float:
        """Calcular fitness médio de um genoma"""
        if genoma_id not in self.fitness_historico:
            return 0.0
        
        snapshots = list(self.fitness_historico[genoma_id])[-janela:]
        if not snapshots:
            return 0.0
        
        return float(np.mean([s.fitness_score for s in snapshots]))
    
    def selecionar_pais(self, n_pais: int = 2, considerar_nicho: bool = True) -> List[str]:
        """Selecionar pais para reprodução com seleção por torneio e diversidade de nicho"""
        if len(self.genomas) < n_pais:
            return list(self.genomas.keys())
        
        if considerar_nicho and self.preservar_diversidade:
            # Selecionar pais de diferentes nichos/espécies
            especies_ativas = [e for e in self.especies.values() if not e.extinta]
            if len(especies_ativas) >= n_pais:
                selecionados = []
                # Escolher espécies diferentes
                especies_escolhidas = np.random.choice(
                    especies_ativas,
                    size=min(n_pais, len(especies_ativas)),
                    replace=False
                )
                for especie in especies_escolhidas:
                    # Melhor genoma da espécie
                    melhor = max(especie.genomas_membros, key=lambda g: self.calcular_fitness_medio(g))
                    selecionados.append(melhor)
                return selecionados
        
        # Seleção por torneio padrão
        selecionados = []
        genoma_ids = list(self.genomas.keys())
        
        for _ in range(n_pais):
            torneio = np.random.choice(genoma_ids, min(3, len(genoma_ids)), replace=False)
            melhor = max(torneio, key=lambda g: self.calcular_fitness_medio(g))
            selecionados.append(melhor)
        
        return selecionados
    
    def crossover(
        self,
        pai1_id: str,
        pai2_id: str,
        caracteristicas_dominantes: Optional[List[str]] = None
    ) -> str:
        """Realizar crossover entre dois genomas com herança ponderada"""
        if pai1_id not in self.genomas or pai2_id not in self.genomas:
            raise ValueError("Genomas pais não encontrados")
        
        pai1 = self.genomas[pai1_id]
        pai2 = self.genomas[pai2_id]
        
        # Nova geração
        self.geracao_atual = max(pai1.geracao, pai2.geracao) + 1
        
        # Criar novo ID
        filho_id = hashlib.md5(
            f"gen{self.geracao_atual}_{pai1_id}_{pai2_id}_{datetime.now(timezone.utc).timestamp()}".encode()
        ).hexdigest()[:16]
        
        # Crossover de características com pesos baseados em fitness
        fitness1 = self.calcular_fitness_medio(pai1_id)
        fitness2 = self.calcular_fitness_medio(pai2_id)
        peso_total = fitness1 + fitness2
        
        caracteristicas_filho = {}
        todas_chaves = set(pai1.caracteristicas.keys()) | set(pai2.caracteristicas.keys())
        
        for chave in todas_chaves:
            v1 = pai1.caracteristicas.get(chave, 0.0)
            v2 = pai2.caracteristicas.get(chave, 0.0)
            if peso_total > 0:
                caracteristicas_filho[chave] = (v1 * fitness1 + v2 * fitness2) / peso_total
            else:
                caracteristicas_filho[chave] = (v1 + v2) / 2
        
        # Dominância de características específicas (se fornecido)
        if caracteristicas_dominantes:
            for chave in caracteristicas_dominantes:
                if chave in pai1.caracteristicas:
                    caracteristicas_filho[chave] = pai1.caracteristicas[chave]
        
        # Hiperparâmetros: herança blend
        hiper_filho = {}
        todas_hp = set(pai1.hiperparametros.keys()) | set(pai2.hiperparametros.keys())
        for hp in todas_hp:
            if hp in pai1.hiperparametros and hp in pai2.hiperparametros:
                if peso_total > 0:
                    hiper_filho[hp] = (pai1.hiperparametros[hp] * fitness1 + pai2.hiperparametros[hp] * fitness2) / peso_total
                else:
                    hiper_filho[hp] = pai1.hiperparametros[hp] if fitness1 >= fitness2 else pai2.hiperparametros[hp]
            elif hp in pai1.hiperparametros:
                hiper_filho[hp] = pai1.hiperparametros[hp]
            else:
                hiper_filho[hp] = pai2.hiperparametros[hp]
        
        # Nicho: herdado do pai com maior fitness
        nicho_filho = pai1.nicho if fitness1 >= fitness2 else pai2.nicho
        
        # Criar genoma filho
        filho = GenomaModelo(
            id=filho_id,
            geracao=self.geracao_atual,
            caracteristicas=caracteristicas_filho,
            arquitetura=pai1.arquitetura,
            hiperparametros=hiper_filho,
            ancestral_id=pai1_id,
            nicho=nicho_filho
        )
        
        self.genomas[filho_id] = filho
        
        # Atualizar linhagens
        self.linhagens[filho_id] = LinhagemModelo(
            modelo_id=filho_id,
            geracao=self.geracao_atual,
            ancestral_direto=pai1_id,
            irmaos=[pai2_id]
        )
        
        if pai1_id in self.linhagens:
            self.linhagens[pai1_id].descendentes.append(filho_id)
        
        # Atribuir espécie
        self._atribuir_especie(filho_id)
        
        # Registrar evento
        evento = EventoEvolucao(
            id=f"evo_{len(self.eventos_evolucao)}",
            tipo=TipoEvolucao.CROSSOVER,
            geracao=self.geracao_atual,
            descricao=f"Crossover entre {pai1_id} e {pai2_id}",
            modelo_origem=pai1_id,
            modelo_destino=filho_id,
            impacto_fitness=0.0,
            motivacao="reproducao"
        )
        self.eventos_evolucao.append(evento)
        
        logger.debug(f"Crossover: {pai1_id} x {pai2_id} -> {filho_id}")
        return filho_id
    
    def mutar(
        self,
        genoma_id: str,
        intensidade: float = 0.1,
        caracteristicas_alvo: Optional[List[str]] = None,
        aprender_lamarck: bool = True
    ) -> str:
        """Aplicar mutação com possível aprendizado lamarckiano"""
        if genoma_id not in self.genomas:
            raise ValueError("Genoma não encontrado")
        
        genoma_original = self.genomas[genoma_id]
        
        # Criar novo ID
        mutante_id = hashlib.md5(
            f"mut_{genoma_id}_{datetime.now(timezone.utc).timestamp()}".encode()
        ).hexdigest()[:16]
        
        # Copiar características
        caracteristicas_mutante = genoma_original.caracteristicas.copy()
        
        # Aplicar mutação
        mutacoes_aplicadas = []
        chaves_alvo = caracteristicas_alvo or list(caracteristicas_mutante.keys())
        
        for chave in chaves_alvo:
            if chave in caracteristicas_mutante:
                # Mutação gaussiana
                mutacao = np.random.normal(0, intensidade)
                novo_valor = caracteristicas_mutante[chave] * (1 + mutacao)
                caracteristicas_mutante[chave] = max(0.0, min(1.0, novo_valor))
                mutacoes_aplicadas.append(f"{chave}: {mutacao:.4f}")
        
        # Aprendizado Lamarck: se disponível, ajustar características baseado em experiência
        memoria = genoma_original.memoria_lamarck
        if aprender_lamarck and memoria:
            for chave, ajuste in memoria.items():
                if chave in caracteristicas_mutante:
                    caracteristicas_mutante[chave] += ajuste * 0.1
                    caracteristicas_mutante[chave] = max(0.0, min(1.0, caracteristicas_mutante[chave]))
                    mutacoes_aplicadas.append(f"{chave}_lamarck: {ajuste:.4f}")
        
        # Criar genoma mutante
        mutante = GenomaModelo(
            id=mutante_id,
            geracao=genoma_original.geracao + 1,  # Mutação pode avançar geração
            caracteristicas=caracteristicas_mutante,
            arquitetura=genoma_original.arquitetura,
            hiperparametros=genoma_original.hiperparametros.copy(),
            ancestral_id=genoma_id,
            mutacoes=mutacoes_aplicadas,
            nicho=genoma_original.nicho
        )
        
        self.genomas[mutante_id] = mutante
        
        # Atualizar linhagem
        self.linhagens[mutante_id] = LinhagemModelo(
            modelo_id=mutante_id,
            geracao=mutante.geracao,
            ancestral_direto=genoma_id
        )
        
        if genoma_id in self.linhagens:
            self.linhagens[genoma_id].descendentes.append(mutante_id)
        
        # Atribuir espécie
        self._atribuir_especie(mutante_id)
        
        # Registrar evento
        evento = EventoEvolucao(
            id=f"evo_{len(self.eventos_evolucao)}",
            tipo=TipoEvolucao.MUTACAO,
            geracao=mutante.geracao,
            descricao=f"Mutação de {genoma_id}: {', '.join(mutacoes_aplicadas[:3])}",
            modelo_origem=genoma_id,
            modelo_destino=mutante_id,
            impacto_fitness=0.0,
            motivacao="exploracao"
        )
        self.eventos_evolucao.append(evento)
        
        logger.debug(f"Mutacao: {genoma_id} -> {mutante_id}")
        return mutante_id
    
    def _atribuir_especie(self, genoma_id: str):
        """Atribuir genoma a uma espécie existente ou criar nova espécie"""
        genoma = self.genomas[genoma_id]
        
        # Se já tem espécie, não reatribuir
        if genoma_id in self.especie_por_genoma:
            return
        
        # Encontrar espécie mais próxima
        melhor_especie = None
        menor_distancia = float('inf')
        
        for especie_id, especie in self.especies.items():
            if especie.extinta:
                continue
            # Calcular distância euclidiana entre características do genoma e centroide da espécie
            dist = self._distancia_caracteristicas(
                genoma.caracteristicas,
                especie.caracteristicas_centroides
            )
            if dist < self.limiar_especiacao and dist < menor_distancia:
                menor_distancia = dist
                melhor_especie = especie_id
        
        if melhor_especie is not None:
            # Adicionar à espécie existente
            self.especies[melhor_especie].genomas_membros.add(genoma_id)
            self.especie_por_genoma[genoma_id] = melhor_especie
            # Atualizar centroide
            self._atualizar_centroide_especie(melhor_especie)
        else:
            # Criar nova espécie
            if len(self.especies) < self.num_especies_max:
                nova_especie_id = f"esp_{len(self.especies)}_{self.geracao_atual}"
                nova_especie = Especie(
                    id=nova_especie_id,
                    geracao_fundacao=self.geracao_atual,
                    genomas_membros={genoma_id},
                    caracteristicas_centroides=genoma.caracteristicas.copy(),
                    fitness_medio=0.0,
                    idade=0
                )
                self.especies[nova_especie_id] = nova_especie
                self.especie_por_genoma[genoma_id] = nova_especie_id
                logger.info(f"Nova espécie criada: {nova_especie_id}")
            else:
                # Se já atingiu limite, forçar associação à espécie mais próxima
                if melhor_especie is not None:
                    self.especies[melhor_especie].genomas_membros.add(genoma_id)
                    self.especie_por_genoma[genoma_id] = melhor_especie
                else:
                    # Caso extremo: associar à primeira espécie
                    primeira = next(iter(self.especies.values()))
                    primeira.genomas_membros.add(genoma_id)
                    self.especie_por_genoma[genoma_id] = primeira.id
    
    def _distancia_caracteristicas(self, car1: Dict[str, float], car2: Dict[str, float]) -> float:
        """Calcular distância Euclidiana entre dois conjuntos de características"""
        chaves_comuns = set(car1.keys()) & set(car2.keys())
        if not chaves_comuns:
            return 1.0  # Distância máxima
        
        diff_sq = sum((car1[k] - car2[k])**2 for k in chaves_comuns)
        return np.sqrt(diff_sq / len(chaves_comuns))
    
    def _atualizar_centroide_especie(self, especie_id: str):
        """Recalcular centroide da espécie baseado nos membros"""
        especie = self.especies[especie_id]
        membros = [self.genomas[gid] for gid in especie.genomas_membros if gid in self.genomas]
        if not membros:
            return
        
        # Média das características
        novas_caracteristicas = defaultdict(float)
        for membro in membros:
            for chave, valor in membro.caracteristicas.items():
                novas_caracteristicas[chave] += valor
        
        for chave in novas_caracteristicas:
            novas_caracteristicas[chave] /= len(membros)
        
        especie.caracteristicas_centroides = dict(novas_caracteristicas)
    
    def _atualizar_fitness_especie(self, genoma_id: str):
        """Atualizar fitness médio da espécie do genoma"""
        especie_id = self.especie_por_genoma.get(genoma_id)
        if not especie_id or especie_id not in self.especies:
            return
        
        especie = self.especies[especie_id]
        fitness_membros = [
            self.calcular_fitness_medio(gid)
            for gid in especie.genomas_membros
            if gid in self.genomas
        ]
        if fitness_membros:
            especie.fitness_medio = float(np.mean(fitness_membros))
    
    def adaptar_a_regime(
        self,
        novo_regime: str,
        genoma_base_id: str,
        usar_campeao: bool = True
    ) -> str:
        """Adaptar modelo a novo regime de mercado"""
        if genoma_base_id not in self.genomas:
            raise ValueError("Genoma base não encontrado")
        
        # Verificar se temos campeão para este regime
        if usar_campeao and novo_regime in self.campeoes_por_regime:
            campeao_id = self.campeoes_por_regime[novo_regime]
            logger.info(f"Adaptando via crossover com campeão do regime {novo_regime}")
            return self.crossover(genoma_base_id, campeao_id)
        
        # Se não tem campeão, aplicar mutação direcionada
        # Mutação mais forte para adaptação rápida
        adaptado_id = self.mutar(genoma_base_id, intensidade=0.3)
        
        # Registrar adaptação
        adaptacao = {
            'tipo': TipoAdaptacao.REGIME_VOLATILIDADE if 'volatil' in novo_regime else TipoAdaptacao.REGIME_TENDENCIA,
            'regime_anterior': self.regime_atual,
            'regime_novo': novo_regime,
            'genoma_adaptado': adaptado_id,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        self.adaptacoes_realizadas.append(adaptacao)
        
        self.regime_atual = novo_regime
        self.historico_regimes.append(novo_regime)
        
        logger.info(f"Adaptação ao regime {novo_regime}: {adaptado_id}")
        return adaptado_id
    
    def podar_populacao(self, manter_top_n: Optional[int] = None) -> List[str]:
        """Remover genomas de baixa performance, preservando diversidade de espécies"""
        if manter_top_n is None:
            manter_top_n = self.populacao_maxima
        
        if len(self.genomas) <= manter_top_n:
            return []
        
        # Se preservar diversidade, garantir que cada espécie tenha pelo menos um representante
        if self.preservar_diversidade:
            # Primeiro, selecionar o melhor de cada espécie
            sobreviventes = set()
            for especie in self.especies.values():
                if especie.genomas_membros:
                    # Melhor membro da espécie
                    melhor = max(especie.genomas_membros, key=lambda g: self.calcular_fitness_medio(g))
                    sobreviventes.add(melhor)
            
            # Completar com os melhores restantes até manter_top_n
            restantes = [gid for gid in self.genomas.keys() if gid not in sobreviventes]
            fitness_restantes = [(gid, self.calcular_fitness_medio(gid)) for gid in restantes]
            fitness_restantes.sort(key=lambda x: x[1], reverse=True)
            
            for gid, _ in fitness_restantes[:max(0, manter_top_n - len(sobreviventes))]:
                sobreviventes.add(gid)
        else:
            # Seleção padrão: manter top N por fitness
            fitness_scores = [(gid, self.calcular_fitness_medio(gid)) for gid in self.genomas.keys()]
            fitness_scores.sort(key=lambda x: x[1], reverse=True)
            sobreviventes = set(gid for gid, _ in fitness_scores[:manter_top_n])
        
        # Remover não sobreviventes
        genomas_remover = [gid for gid in self.genomas.keys() if gid not in sobreviventes]
        for gid in genomas_remover:
            # Remover da espécie
            especie_id = self.especie_por_genoma.get(gid)
            if especie_id and especie_id in self.especies:
                self.especies[especie_id].genomas_membros.discard(gid)
                # Se espécie ficou vazia, marcar como extinta
                if not self.especies[especie_id].genomas_membros:
                    self.especies[especie_id].extinta = True
                    logger.info(f"Espécie {especie_id} extinta")
            
            del self.genomas[gid]
            if gid in self.fitness_historico:
                del self.fitness_historico[gid]
            if gid in self.linhagens:
                del self.linhagens[gid]
        
        # Remover espécies extintas
        self.especies = {k: v for k, v in self.especies.items() if not v.extinta}
        
        logger.info(f"Poda concluída: removidos {len(genomas_remover)} genomas")
        return genomas_remover
    
    def evoluir_geracao(self) -> Dict[str, Any]:
        """Executar um ciclo completo de evolução"""
        resultados = {
            'geracao': self.geracao_atual + 1,
            'novos_genomas': [],
            'mutacoes': [],
            'removidos': [],
            'especies_ativas': len(self.especies)
        }
        
        # 1. Selecionar pais (considerando nicho)
        pais = self.selecionar_pais(n_pais=4, considerar_nicho=True)
        
        # 2. Criar offspring via crossover
        for i in range(0, len(pais), 2):
            if i + 1 < len(pais):
                filho_id = self.crossover(pais[i], pais[i+1])
                resultados['novos_genomas'].append(filho_id)
        
        # 3. Aplicar mutações (incluindo mutações em alguns pais)
        for genoma_id in list(self.genomas.keys()):
            if np.random.random() < self.taxa_mutacao:
                mutante_id = self.mutar(genoma_id, intensidade=self.taxa_mutacao)
                resultados['mutacoes'].append(mutante_id)
        
        # 4. Verificar estagnação
        fitness_medio_atual = np.mean([self.calcular_fitness_medio(gid) for gid in self.genomas.keys()]) if self.genomas else 0.0
        if fitness_medio_atual <= self.melhor_fitness_historico * 1.01:
            self.geracoes_sem_melhoria += 1
        else:
            self.geracoes_sem_melhoria = 0
            self.melhor_fitness_historico = fitness_medio_atual
        
        # 5. Se estagnado, aumentar taxa de mutação temporariamente
        if self.geracoes_sem_melhoria > 5:
            logger.warning("Estagnação detectada - aumentando taxa de mutação")
            self.taxa_mutacao = min(0.5, self.taxa_mutacao * 1.5)
        else:
            self.taxa_mutacao = max(0.05, self.taxa_mutacao * 0.95)
        
        # 6. Podar população
        removidos = self.podar_populacao(self.populacao_maxima)
        resultados['removidos'] = removidos
        
        self.geracao_atual += 1
        
        # 7. Registrar evento de geração
        evento = EventoEvolucao(
            id=f"gen_{self.geracao_atual}",
            tipo=TipoEvolucao.SELECAO,
            geracao=self.geracao_atual,
            descricao=f"Evolução geração {self.geracao_atual}",
            modelo_origem="",
            modelo_destino=None,
            impacto_fitness=fitness_medio_atual,
            motivacao="ciclo_evolutivo"
        )
        self.eventos_evolucao.append(evento)
        
        logger.info(f"Geração {self.geracao_atual} concluída. População: {len(self.genomas)}")
        return resultados
    
    def aprender_lamarck(self, genoma_id: str, experiencia: Dict[str, Any]):
        """Aprender durante a vida (Lamarckismo) - ajusta memória do genoma"""
        if genoma_id not in self.genomas:
            return
        
        genoma = self.genomas[genoma_id]
        # Atualizar memória com base na experiência
        for chave, valor in experiencia.items():
            if chave in genoma.caracteristicas:
                if chave not in genoma.memoria_lamarck:
                    genoma.memoria_lamarck[chave] = 0.0
                # Acumular ajuste
                genoma.memoria_lamarck[chave] += valor
    
    def get_melhor_genoma(self, por_nicho: Optional[NichoEstrategico] = None) -> Optional[str]:
        """Obter o melhor genoma da população (opcionalmente por nicho)"""
        if por_nicho:
            candidatos = [gid for gid, g in self.genomas.items() if g.nicho == por_nicho]
            if not candidatos:
                return None
            return max(candidatos, key=lambda g: self.calcular_fitness_medio(g))
        else:
            if not self.genomas:
                return None
            return max(self.genomas.keys(), key=lambda g: self.calcular_fitness_medio(g))
    
    def get_arvore_genealogica(self, genoma_id: str) -> Dict[str, Any]:
        """Obter árvore genealógica de um genoma"""
        if genoma_id not in self.linhagens:
            return {}
        
        linhagem = self.linhagens[genoma_id]
        genoma = self.genomas.get(genoma_id)
        
        return {
            'modelo_id': genoma_id,
            'geracao': linhagem.geracao,
            'fitness_atual': self.calcular_fitness_medio(genoma_id),
            'ancestral': linhagem.ancestral_direto,
            'descendentes': linhagem.descendentes,
            'irmaos': linhagem.irmaos,
            'caracteristicas': genoma.caracteristicas if genoma else {},
            'nicho': genoma.nicho.value if genoma and genoma.nicho else None,
            'especie': self.especie_por_genoma.get(genoma_id),
            'timestamp_criacao': genoma.timestamp_criacao if genoma else None
        }
    
    def exportar_estado(self, formato: str = 'json') -> Union[str, bytes]:
        """Exportar estado completo da evolução para backup"""
        dados = {
            'versao': '7.0.0',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'geracao_atual': self.geracao_atual,
            'genomas': {
                gid: {
                    'id': g.id,
                    'geracao': g.geracao,
                    'caracteristicas': g.caracteristicas,
                    'arquitetura': g.arquitetura,
                    'hiperparametros': g.hiperparametros,
                    'ancestral_id': g.ancestral_id,
                    'mutacoes': g.mutacoes,
                    'timestamp_criacao': g.timestamp_criacao,
                    'fitness_acumulado': g.fitness_acumulado,
                    'nicho': g.nicho.value if g.nicho else None,
                    'memoria_lamarck': g.memoria_lamarck
                } for gid, g in self.genomas.items()
            },
            'linhagens': {
                lid: {
                    'modelo_id': l.modelo_id,
                    'geracao': l.geracao,
                    'ancestral_direto': l.ancestral_direto,
                    'descendentes': l.descendentes,
                    'irmaos': l.irmaos
                } for lid, l in self.linhagens.items()
            },
            'especies': {
                eid: {
                    'id': e.id,
                    'geracao_fundacao': e.geracao_fundacao,
                    'genomas_membros': list(e.genomas_membros),
                    'fitness_medio': e.fitness_medio,
                    'idade': e.idade,
                    'extinta': e.extinta
                } for eid, e in self.especies.items()
            },
            'regime_atual': self.regime_atual,
            'campeoes_por_nicho': self.campeoes_por_nicho,
            'campeoes_por_regime': self.campeoes_por_regime,
            'taxa_mutacao': self.taxa_mutacao,
            'geracoes_sem_melhoria': self.geracoes_sem_melhoria,
            'melhor_fitness_historico': self.melhor_fitness_historico
        }
        
        if formato == 'json':
            return json.dumps(dados, indent=2, default=str)
        elif formato == 'pickle':
            return pickle.dumps(dados)
        else:
            raise ValueError(f"Formato não suportado: {formato}")
    
    def importar_estado(self, dados: Union[str, bytes], formato: str = 'json'):
        """Importar estado de backup"""
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
        
        # Restaurar genomas
        self.genomas.clear()
        for gid, g_data in dados_dict['genomas'].items():
            genoma = GenomaModelo(
                id=g_data['id'],
                geracao=g_data['geracao'],
                caracteristicas=g_data['caracteristicas'],
                arquitetura=g_data['arquitetura'],
                hiperparametros=g_data['hiperparametros'],
                ancestral_id=g_data['ancestral_id'],
                mutacoes=g_data['mutacoes'],
                timestamp_criacao=g_data['timestamp_criacao'],
                fitness_acumulado=g_data.get('fitness_acumulado', 0.0),
                nicho=NichoEstrategico(g_data['nicho']) if g_data.get('nicho') else None,
                memoria_lamarck=g_data.get('memoria_lamarck', {})
            )
            self.genomas[gid] = genoma
        
        # Restaurar linhagens
        self.linhagens.clear()
        for lid, l_data in dados_dict['linhagens'].items():
            linhagem = LinhagemModelo(
                modelo_id=l_data['modelo_id'],
                geracao=l_data['geracao'],
                ancestral_direto=l_data['ancestral_direto'],
                descendentes=l_data['descendentes'],
                irmaos=l_data['irmaos']
            )
            self.linhagens[lid] = linhagem
        
        # Restaurar espécies
        self.especies.clear()
        for eid, e_data in dados_dict['especies'].items():
            especie = Especie(
                id=e_data['id'],
                geracao_fundacao=e_data['geracao_fundacao'],
                genomas_membros=set(e_data['genomas_membros']),
                caracteristicas_centroides={},  # Será recalculado
                fitness_medio=e_data['fitness_medio'],
                idade=e_data['idade'],
                extinta=e_data['extinta']
            )
            self.especies[eid] = especie
        
        # Recalcular centroides
        for eid in self.especies:
            self._atualizar_centroide_especie(eid)
        
        # Reconstruir especie_por_genoma
        self.especie_por_genoma.clear()
        for eid, especie in self.especies.items():
            for gid in especie.genomas_membros:
                self.especie_por_genoma[gid] = eid
        
        self.geracao_atual = dados_dict['geracao_atual']
        self.regime_atual = dados_dict['regime_atual']
        self.campeoes_por_nicho = dados_dict['campeoes_por_nicho']
        self.campeoes_por_regime = dados_dict['campeoes_por_regime']
        self.taxa_mutacao = dados_dict['taxa_mutacao']
        self.geracoes_sem_melhoria = dados_dict['geracoes_sem_melhoria']
        self.melhor_fitness_historico = dados_dict['melhor_fitness_historico']
        
        logger.info("Estado da evolução importado com sucesso")
    
    def get_status(self) -> Dict[str, Any]:
        """Obter status detalhado do sistema de evolução"""
        fitness_medio = 0.0
        if self.genomas:
            fitness_medio = float(np.mean([self.calcular_fitness_medio(gid) for gid in self.genomas.keys()]))
        
        melhor_fitness = 0.0
        if self.genomas:
            melhor_fitness = max([self.calcular_fitness_medio(gid) for gid in self.genomas.keys()])
        
        return {
            'geracao_atual': self.geracao_atual,
            'populacao_atual': len(self.genomas),
            'populacao_maxima': self.populacao_maxima,
            'num_especies': len(self.especies),
            'total_eventos_evolucao': len(self.eventos_evolucao),
            'regime_atual': self.regime_atual,
            'campeoes_por_regime': self.campeoes_por_regime,
            'campeoes_por_nicho': self.campeoes_por_nicho,
            'taxa_mutacao': self.taxa_mutacao,
            'taxa_crossover': self.taxa_crossover,
            'pressao_selecao': self.pressao_selecao,
            'fitness_medio_populacao': fitness_medio,
            'melhor_fitness': melhor_fitness,
            'geracoes_sem_melhoria': self.geracoes_sem_melhoria,
            'diversidade_genetica': self._calcular_diversidade()
        }
    
    def _calcular_diversidade(self) -> float:
        """Calcular diversidade genética da população (0-1)"""
        if len(self.genomas) < 2:
            return 0.0
        
        # Calcular distância média entre pares de genomas
        genoma_ids = list(self.genomas.keys())
        distancias = []
        
        for i in range(len(genoma_ids)):
            for j in range(i+1, len(genoma_ids)):
                g1 = self.genomas[genoma_ids[i]]
                g2 = self.genomas[genoma_ids[j]]
                dist = self._distancia_caracteristicas(g1.caracteristicas, g2.caracteristicas)
                distancias.append(dist)
        
        if not distancias:
            return 0.0
        
        return float(np.mean(distancias))


# Exemplo de uso
async def exemplo_evolucao():
    """Exemplo completo do sistema de evolução"""
    evolucao = EvolucaoAprendizado(populacao_maxima=10, num_especies_max=3)
    
    # Criar população inicial
    genomas_iniciais = []
    for i in range(5):
        caracteristicas = {
            'sensibilidade': np.random.random(),
            'agressividade': np.random.random(),
            'memoria': np.random.random(),
            'risco': np.random.random()
        }
        gid = evolucao.criar_genoma_inicial(
            caracteristicas=caracteristicas,
            arquitetura="MLP",
            hiperparametros={'learning_rate': 0.001, 'layers': [64, 32]},
            nicho=np.random.choice(list(NichoEstrategico))
        )
        genomas_iniciais.append(gid)
    
    # Simular algumas gerações
    for gen in range(10):
        # Registrar fitness simulado
        for gid in genomas_iniciais:
            snapshot = FitnessSnapshot(
                timestamp=datetime.now(timezone.utc).isoformat(),
                fitness_score=np.random.uniform(0.3, 0.9),
                sharpe_ratio=np.random.uniform(0.5, 2.0),
                win_rate=np.random.uniform(0.4, 0.7),
                profit_factor=np.random.uniform(1.0, 1.5),
                max_drawdown=np.random.uniform(0.05, 0.15),
                trades_realizados=np.random.randint(10, 100),
                ambiente=np.random.choice(["bull", "bear", "sideways"])
            )
            evolucao.registrar_fitness(gid, snapshot)
        
        # Evoluir
        resultado = evolucao.evoluir_geracao()
        print(f"Geração {resultado['geracao']}: pop={len(evolucao.genomas)}, especies={resultado['especies_ativas']}")
        
        # Atualizar lista de genomas para próxima iteração
        genomas_iniciais = list(evolucao.genomas.keys())
    
    # Mostrar status final
    status = evolucao.get_status()
    print("\nStatus final:")
    for k, v in status.items():
        print(f"  {k}: {v}")
    
    # Melhor genoma
    melhor = evolucao.get_melhor_genoma()
    if melhor:
        print(f"\nMelhor genoma: {melhor}")
        print(evolucao.get_arvore_genealogica(melhor))
    
    return evolucao


if __name__ == "__main__":
    asyncio.run(exemplo_evolucao())
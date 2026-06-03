"""
VHALINOR Metacognição v7.0 - Edição Evolutiva
===============================================
Sistema avançado de metacognição com:
- Consciência dos próprios processos cognitivos
- Monitoramento adaptativo do aprendizado
- Regulação estratégica multicamada
- Auto-avaliação preditiva
- Adaptação dinâmica de estratégias
- Integração com memória cognitiva
- Calibração Bayesiana de confiança
- Detecção e mitigação de vieses
- Planejamento com contingências

@module metacognicao
@author VHALINOR Team
@version 7.0.0
@since 2026-04-07
"""

from typing import Dict, List, Any, Optional, Callable, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum, auto
from collections import deque, defaultdict
import hashlib
import json
import pickle
import asyncio
import numpy as np
from abc import ABC, abstractmethod
import heapq
import logging
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NivelMetacognicao(Enum):
    """Níveis expandidos de metacognição"""
    INCONSCIENTE = "inconsciente"           # Sem consciência
    CONSCIENTE = "consciente"               # Consciência básica
    MONITORADO = "monitorado"               # Monitoramento ativo
    REGULADO = "regulado"                   # Regulação ativa
    REFLEXIVO = "reflexivo"                 # Reflexão profunda
    META_REFLEXIVO = "meta_reflexivo"       # Reflexão sobre reflexão
    PREDITIVO = "preditivo"                 # Antecipação de estados futuros
    TRANSCENDENTE = "transcendente"         # Integração com outros sistemas


class TipoEstrategia(Enum):
    """Tipos de estratégias cognitivas"""
    ANALITICA = "analitica"
    INTUITIVA = "intuitiva"
    SISTEMATICA = "sistematica"
    HEURISTICA = "heuristica"
    COLABORATIVA = "colaborativa"
    EXPLORATORIA = "exploratoria"
    EXPLICATIVA = "explicativa"
    MONITORAMENTO = "monitoramento"
    REGULACAO = "regulacao"


class ViésCognitivo(Enum):
    """Tipos de vieses cognitivos detectáveis"""
    OTIMISMO = "viés_otimismo"
    PESSIMISMO = "viés_pessimismo"
    ANCORAGEM = "efeito_ancoragem"
    RECENCIA = "viés_recencia"
    CONFIRMACAO = "viés_confirmacao"
    EXCESSO_CONFIANCA = "excesso_confianca"
    SUB_CONFIANCA = "sub_confianca"
    DISPONIBILIDADE = "viés_disponibilidade"
    PLANEJAMENTO = "falacia_planejamento"
    ESTAGNACAO = "viés_estagnacao"


@dataclass
class MonitorCognitivo:
    """Monitoramento detalhado de processo cognitivo"""
    processo_id: str
    descricao: str
    inicio: datetime
    fim: Optional[datetime] = None
    sucesso: Optional[bool] = None
    confianca_inicial: float = 0.5
    confianca_final: float = 0.0
    esforco_estimado: float = 0.5
    esforco_real: float = 0.0
    dificuldades: List[str] = field(default_factory=list)
    estrategias_usadas: List[str] = field(default_factory=list)
    ajustes_realizados: List[Dict] = field(default_factory=list)
    metricas_intermediarias: Dict[str, List[float]] = field(default_factory=dict)
    contexto: Dict[str, Any] = field(default_factory=dict)
    checkpoint_avaliacoes: List[Dict] = field(default_factory=list)


@dataclass
class Estrategia:
    """Modelo de estratégia cognitiva"""
    nome: str
    tipo: TipoEstrategia
    descricao: str
    efetividade_historica: float = 0.5
    vezes_usada: int = 0
    sucessos: int = 0
    tempo_medio_execucao: float = 0.0
    contextos_efetivos: List[str] = field(default_factory=list)
    condicoes_aplicabilidade: Dict[str, Any] = field(default_factory=dict)
    metadados: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def taxa_sucesso(self) -> float:
        return self.sucessos / max(1, self.vezes_usada)
    
    def atualizar_efetividade(self, sucesso: bool, tempo_execucao: float, contexto: str):
        self.vezes_usada += 1
        if sucesso:
            self.sucessos += 1
        self.efetividade_historica = self.taxa_sucesso
        
        # Atualizar tempo médio
        self.tempo_medio_execucao = (self.tempo_medio_execucao * (self.vezes_usada - 1) + tempo_execucao) / self.vezes_usada
        
        # Registrar contexto se efetivo
        if sucesso and contexto not in self.contextos_efetivos:
            self.contextos_efetivos.append(contexto)


@dataclass
class Reflexao:
    """Registro detalhado de reflexão metacognitiva"""
    id: str
    tipo: str
    conteudo: str
    insights: List[str]
    acoes_sugeridas: List[str]
    confianca_insights: float = 0.5
    impacto_estimado: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class CalibradorBayesiano:
    """
    Calibrador de confiança usando inferência Bayesiana
    """
    
    def __init__(self, alpha_prior: float = 2.0, beta_prior: float = 2.0):
        self.alpha = alpha_prior  # Contagem de acertos
        self.beta = beta_prior    # Contagem de erros
        self.historico = deque(maxlen=1000)
    
    def atualizar(self, correto: bool, confianca_declarada: float):
        """Atualizar distribuição Beta"""
        if correto:
            self.alpha += 1
        else:
            self.beta += 1
        
        self.historico.append((correto, confianca_declarada))
    
    def confianca_calibrada(self) -> float:
        """Obter confiança calibrada (média da posterior)"""
        return self.alpha / (self.alpha + self.beta)
    
    def intervalo_confianca(self, nivel: float = 0.95) -> Tuple[float, float]:
        """Intervalo de credibilidade para a confiança"""
        from scipy import stats
        # Aproximação Normal para Beta grande
        media = self.confianca_calibrada()
        var = (self.alpha * self.beta) / ((self.alpha + self.beta)**2 * (self.alpha + self.beta + 1))
        desvio = np.sqrt(var)
        z = stats.norm.ppf(1 - (1 - nivel) / 2)
        return (media - z * desvio, media + z * desvio)
    
    def bem_calibrado(self, limiar: float = 0.15) -> bool:
        """Verificar se há calibração adequada"""
        # Calcula erro médio absoluto entre confiança declarada e acerto observado
        if len(self.historico) < 10:
            return True
        
        erros = []
        for correto, conf in list(self.historico):
            erros.append(abs((1.0 if correto else 0.0) - conf))
        erro_medio = np.mean(erros)
        return erro_medio < limiar


class DetectorVies:
    """Detector e mitigador de vieses cognitivos"""
    
    def __init__(self):
        self.vieses_identificados: Dict[ViésCognitivo, int] = defaultdict(int)
        self.historico_decisoes: deque = deque(maxlen=200)
        self.estrategias_mitigacao = {
            ViésCognitivo.OTIMISMO: ["Revisar casos negativos", "Aplicar análise de cenário pessimista"],
            ViésCognitivo.PESSIMISMO: ["Buscar evidências positivas", "Revisar sucessos passados"],
            ViésCognitivo.ANCORAGEM: ["Considerar valores extremos", "Redefinir ponto de referência"],
            ViésCognitivo.RECENCIA: ["Revisar histórico completo", "Dar peso igual a todas observações"],
            ViésCognitivo.CONFIRMACAO: ["Buscar ativamente evidências contrárias", "Testar hipótese nula"],
            ViésCognitivo.EXCESSO_CONFIANCA: ["Revisar erros passados", "Reduzir confiança em 20%"],
            ViésCognitivo.SUB_CONFIANCA: ["Revisar acertos passados", "Aumentar confiança gradualmente"],
            ViésCognitivo.DISPONIBILIDADE: ["Considerar base de dados completa", "Normalizar por frequência"],
            ViésCognitivo.PLANEJAMENTO: ["Adicionar buffer de tempo (50%)", "Dividir tarefa em sub-tarefas"],
            ViésCognitivo.ESTAGNACAO: ["Introduzir variação nas estratégias", "Revisar objetivos"]
        }
    
    def detectar(self, contexto: Dict[str, Any]) -> List[ViésCognitivo]:
        """Detectar vieses baseado em contexto e histórico"""
        detectados = []
        
        # Viés de otimismo/pessimismo
        sucessos_recentes = contexto.get('sucessos_recentes', 0)
        falhas_recentes = contexto.get('falhas_recentes', 0)
        if sucessos_recentes > 5 and falhas_recentes == 0:
            detectados.append(ViésCognitivo.OTIMISMO)
        elif falhas_recentes > 3:
            detectados.append(ViésCognitivo.PESSIMISMO)
        
        # Viés de ancoragem
        if contexto.get('primeira_impressao') is not None:
            detectados.append(ViésCognitivo.ANCORAGEM)
        
        # Viés de recência
        if contexto.get('informacao_recente', False):
            detectados.append(ViésCognitivo.RECENCIA)
        
        # Viés de confirmação
        if contexto.get('busca_confirmatoria', False):
            detectados.append(ViésCognitivo.CONFIRMACAO)
        
        # Excesso/sub confiança
        conf = contexto.get('confianca_declarada', 0.5)
        acerto = contexto.get('acerto_real', 0.5)
        if conf > acerto + 0.2:
            detectados.append(ViésCognitivo.EXCESSO_CONFIANCA)
        elif conf < acerto - 0.2:
            detectados.append(ViésCognitivo.SUB_CONFIANCA)
        
        # Viés de disponibilidade
        if contexto.get('exemplos_disponiveis', 0) < 3:
            detectados.append(ViésCognitivo.DISPONIBILIDADE)
        
        # Falácia do planejamento
        if contexto.get('tempo_estimado', 0) < contexto.get('tempo_real', 0) * 0.7:
            detectados.append(ViésCognitivo.PLANEJAMENTO)
        
        # Registrar
        for vies in detectados:
            self.vieses_identificados[vies] += 1
        
        return detectados
    
    def obter_mitigacoes(self, vies: ViésCognitivo) -> List[str]:
        """Obter estratégias de mitigação para um viés"""
        return self.estrategias_mitigacao.get(vies, ["Revisar decisão com cuidado"])
    
    def relatorio_vieses(self) -> Dict[str, Any]:
        """Gerar relatório de vieses detectados"""
        total = sum(self.vieses_identificados.values())
        if total == 0:
            return {"vieses_detectados": [], "total": 0, "sugestao": "Nenhum viés identificado ainda"}
        
        vieses_ordenados = sorted(self.vieses_identificados.items(), key=lambda x: x[1], reverse=True)
        principais = [(v.value, c) for v, c in vieses_ordenados[:3]]
        
        return {
            "vieses_detectados": principais,
            "total": total,
            "sugestao": "Aplicar técnicas de de-biasing sistematicamente"
        }


class Metacognicao:
    """
    Sistema avançado de metacognição com auto-consciência, regulação e aprendizado.
    """
    
    def __init__(
        self,
        nivel_inicial: NivelMetacognicao = NivelMetacognicao.CONSCIENTE,
        memoria_cognitiva: Optional[Any] = None
    ):
        self.nivel_atual = nivel_inicial
        self.memoria_cognitiva = memoria_cognitiva  # Integração opcional
        
        # Componentes internos
        self.calibrador = CalibradorBayesiano()
        self.detector_vies = DetectorVies()
        
        # Estruturas de dados
        self.processos_monitorados: Dict[str, MonitorCognitivo] = {}
        self.historico_reflexoes: deque = deque(maxlen=2000)
        self.estrategias: Dict[str, Estrategia] = {}
        self.padroes_aprendizado: Dict[str, Any] = {}
        
        # Auto-conhecimento
        self.pontos_fortes: List[str] = []
        self.pontos_fracos: List[str] = []
        self.preferencias_estrategicas: Dict[str, float] = defaultdict(float)
        
        # Métricas
        self.metricas = {
            'total_processos': 0,
            'total_reflexoes': 0,
            'total_adaptacoes': 0,
            'taxa_melhoria': 0.0
        }
        
        # Thread pool
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # Registrar estratégias padrão
        self._registrar_estrategias_padrao()
        
        logger.info(f"Sistema de Metacognição v7.0 inicializado (nível: {nivel_inicial.value})")
    
    def _registrar_estrategias_padrao(self):
        """Registrar biblioteca de estratégias cognitivas"""
        estrategias_padrao = [
            Estrategia("análise_detalhada", TipoEstrategia.ANALITICA, "Análise passo-a-passo com verificações"),
            Estrategia("intuição_rápida", TipoEstrategia.INTUITIVA, "Decisão baseada em padrões reconhecidos"),
            Estrategia("planejamento_estruturado", TipoEstrategia.SISTEMATICA, "Plano detalhado com marcos"),
            Estrategia("heurística_80_20", TipoEstrategia.HEURISTICA, "Foco nos 20% que geram 80% dos resultados"),
            Estrategia("revisão_colegiada", TipoEstrategia.COLABORATIVA, "Revisão por pares ou IA"),
            Estrategia("exploração_ativa", TipoEstrategia.EXPLORATORIA, "Testar múltiplas abordagens"),
            Estrategia("auto_explicação", TipoEstrategia.EXPLICATIVA, "Explicar o raciocínio em voz alta"),
            Estrategia("checklist_sistemático", TipoEstrategia.MONITORAMENTO, "Verificação de checklist"),
            Estrategia("pausa_reflexiva", TipoEstrategia.REGULACAO, "Pausa para reavaliação")
        ]
        for est in estrategias_padrao:
            self.estrategias[est.nome] = est
    
    async def iniciar_monitoramento(
        self,
        processo_id: str,
        descricao: str,
        contexto: Optional[Dict] = None,
        confianca_inicial: float = 0.5,
        esforco_estimado: float = 0.5
    ) -> str:
        """Iniciar monitoramento de processo cognitivo"""
        monitor = MonitorCognitivo(
            processo_id=processo_id,
            descricao=descricao,
            inicio=datetime.now(timezone.utc),
            confianca_inicial=confianca_inicial,
            esforco_estimado=esforco_estimado,
            contexto=contexto or {}
        )
        
        self.processos_monitorados[processo_id] = monitor
        self.metricas['total_processos'] += 1
        
        # Reflexão inicial
        await self._registrar_reflexao(
            'monitoramento',
            f"Iniciando monitoramento: {descricao}",
            [f"Confiança inicial: {confianca_inicial:.1%}, Esforço estimado: {esforco_estimado:.1%}"],
            confianca=0.8
        )
        
        logger.debug(f"Monitoramento iniciado: {processo_id}")
        return processo_id
    
    async def finalizar_monitoramento(
        self,
        processo_id: str,
        sucesso: bool,
        dificuldades: Optional[List[str]] = None,
        confianca_final: Optional[float] = None,
        esforco_real: Optional[float] = None
    ):
        """Finalizar monitoramento e avaliar desempenho"""
        if processo_id not in self.processos_monitorados:
            logger.warning(f"Processo {processo_id} não encontrado")
            return
        
        monitor = self.processos_monitorados[processo_id]
        monitor.fim = datetime.now(timezone.utc)
        monitor.sucesso = sucesso
        monitor.dificuldades = dificuldades or []
        monitor.confianca_final = confianca_final if confianca_final is not None else monitor.confianca_inicial
        monitor.esforco_real = esforco_real if esforco_real is not None else monitor.esforco_estimado
        
        # Auto-avaliação
        avaliacao = await self._avaliar_processo(monitor)
        
        # Calibrar confiança
        correto = sucesso  # Assumindo que sucesso indica predição correta
        self.calibrador.atualizar(correto, monitor.confianca_inicial)
        
        # Atualizar estratégias
        for estrategia_nome in monitor.estrategias_usadas:
            if estrategia_nome in self.estrategias:
                tempo_exec = (monitor.fim - monitor.inicio).total_seconds()
                contexto = monitor.contexto.get('categoria', 'default')
                self.estrategias[estrategia_nome].atualizar_efetividade(sucesso, tempo_exec, contexto)
        
        # Registrar na memória cognitiva se disponível
        if self.memoria_cognitiva:
            await self._armazenar_na_memoria(monitor, avaliacao)
        
        logger.info(f"Processo {processo_id} finalizado: {'sucesso' if sucesso else 'fracasso'}")
    
    async def _avaliar_processo(self, monitor: MonitorCognitivo) -> Dict[str, Any]:
        """Realizar auto-avaliação detalhada do processo"""
        insights = []
        acoes = []
        impacto_estimado = 0.0
        
        # Análise de sucesso
        if monitor.sucesso:
            insights.append("Processo concluído com sucesso")
            impacto_estimado = 0.8
            
            # Identificar estratégias mais efetivas
            if monitor.estrategias_usadas:
                melhor_estrategia = max(
                    monitor.estrategias_usadas,
                    key=lambda e: self.estrategias.get(e, Estrategia(e, TipoEstrategia.ANALITICA, "")).taxa_sucesso
                )
                insights.append(f"Estratégia '{melhor_estrategia}' foi particularmente efetiva")
                self.preferencias_estrategicas[melhor_estrategia] += 0.1
        else:
            insights.append("Processo enfrentou dificuldades significativas")
            impacto_estimado = 0.3
            
            if monitor.dificuldades:
                insights.append(f"Dificuldades principais: {', '.join(monitor.dificuldades)}")
                acoes.append("Revisar estratégias para este tipo de problema")
                
                # Atualizar pontos fracos
                for diff in monitor.dificuldades:
                    if diff not in self.pontos_fracos:
                        self.pontos_fracos.append(diff)
        
        # Análise de calibração
        erro_confianca = abs(monitor.confianca_final - (1.0 if monitor.sucesso else 0.0))
        if erro_confianca > 0.3:
            insights.append(f"Descalibração significativa: erro de {erro_confianca:.1%}")
            acoes.append("Praticar calibração de confiança em tarefas similares")
        
        # Análise de esforço
        if monitor.esforco_real > monitor.esforco_estimado * 1.5:
            insights.append("Esforço real muito superior ao estimado")
            acoes.append("Adicionar buffer de 50% em estimativas futuras")
        
        # Reflexão sobre checkpoints
        if monitor.checkpoint_avaliacoes:
            tendencia = self._analisar_tendencia_checkpoints(monitor.checkpoint_avaliacoes)
            insights.append(f"Tendência dos checkpoints: {tendencia}")
        
        # Registrar reflexão
        await self._registrar_reflexao(
            'avaliacao',
            f"Auto-avaliação do processo {monitor.processo_id}",
            insights,
            acoes,
            confianca=0.7 + impacto_estimado * 0.3,
            impacto=impacto_estimado
        )
        
        return {
            'insights': insights,
            'acoes': acoes,
            'impacto_estimado': impacto_estimado,
            'erro_confianca': erro_confianca
        }
    
    def _analisar_tendencia_checkpoints(self, checkpoints: List[Dict]) -> str:
        """Analisar tendência de desempenho nos checkpoints"""
        if len(checkpoints) < 2:
            return "dados insuficientes"
        
        scores = [cp.get('score', 0.5) for cp in checkpoints]
        if scores[-1] > scores[0] + 0.2:
            return "melhoria consistente"
        elif scores[-1] < scores[0] - 0.2:
            return "declínio de desempenho"
        else:
            return "desempenho estável"
    
    async def _registrar_reflexao(
        self,
        tipo: str,
        conteudo: str,
        insights: List[str],
        acoes: Optional[List[str]] = None,
        confianca: float = 0.5,
        impacto: float = 0.0
    ):
        """Registrar reflexão metacognitiva"""
        reflexao = Reflexao(
            id=f"ref_{len(self.historico_reflexoes)}_{hashlib.md5(conteudo.encode()).hexdigest()[:8]}",
            tipo=tipo,
            conteudo=conteudo,
            insights=insights,
            acoes_sugeridas=acoes or [],
            confianca_insights=confianca,
            impacto_estimado=impacto
        )
        
        self.historico_reflexoes.append(reflexao)
        self.metricas['total_reflexoes'] += 1
        
        # Armazenar em memória cognitiva se disponível
        if self.memoria_cognitiva:
            try:
                await self.memoria_cognitiva.armazenar(
                    conteudo=reflexao.__dict__,
                    tipo="reflexao_metacognitiva",
                    importancia=impacto,
                    tags={"metacognicao", tipo}
                )
            except Exception as e:
                logger.debug(f"Não foi possível armazenar reflexão na memória: {e}")
    
    async def planejar_abordagem(
        self,
        objetivo: str,
        contexto: Dict[str, Any],
        estrategias_permitidas: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Planejar abordagem adaptativa baseada em metacognição"""
        insights = []
        estrategias_sugeridas = []
        
        # Detectar vieses atuais
        vieses = self.detector_vies.detectar(contexto)
        if vieses:
            insights.append(f"Vieses detectados: {[v.value for v in vieses]}")
            mitigacoes = []
            for v in vieses:
                mitigacoes.extend(self.detector_vies.obter_mitigacoes(v))
            insights.append(f"Mitigações sugeridas: {mitigacoes[:2]}")
        
        # Selecionar estratégias baseadas em histórico e contexto
        complexidade = contexto.get('complexidade', 'media')
        prazo = contexto.get('prazo', 'normal')
        
        # Filtrar estratégias permitidas
        estrategias_candidatas = list(self.estrategias.values())
        if estrategias_permitidas:
            estrategias_candidatas = [e for e in estrategias_candidatas if e.nome in estrategias_permitidas]
        
        # Ordenar por efetividade
        estrategias_candidatas.sort(key=lambda e: e.efetividade_historica, reverse=True)
        
        # Selecionar top 3
        for estrategia in estrategias_candidatas[:3]:
            estrategias_sugeridas.append({
                'nome': estrategia.nome,
                'tipo': estrategia.tipo.value,
                'efetividade': estrategia.efetividade_historica,
                'taxa_sucesso': estrategia.taxa_sucesso,
                'tempo_medio': estrategia.tempo_medio_execucao,
                'racional': f"Efetividade histórica de {estrategia.efetividade_historica:.1%}"
            })
        
        # Ajustar para prazo curto
        if prazo == 'curto' and estrategias_sugeridas:
            # Priorizar estratégias mais rápidas
            estrategias_sugeridas.sort(key=lambda e: e['tempo_medio'] if e['tempo_medio'] > 0 else float('inf'))
        
        # Calibrar confiança no plano
        confianca_plano = self.calibrador.confianca_calibrada()
        if self.nivel_atual.value in ['reflexivo', 'meta_reflexivo', 'preditivo']:
            confianca_plano = min(0.9, confianca_plano + 0.1)
        
        # Verificar se há memória de situações similares
        similaridade = 0.0
        if self.memoria_cognitiva:
            similaridade = await self._buscar_similaridade_contexto(contexto)
        
        plano = {
            'objetivo': objetivo,
            'estrategias': estrategias_sugeridas,
            'vieses_identificados': [v.value for v in vieses],
            'pontos_atencao': insights,
            'checkpoints': [
                {'progresso': 0.25, 'acao': 'Verificar alinhamento inicial'},
                {'progresso': 0.5, 'acao': 'Avaliar progresso e ajustar'},
                {'progresso': 0.75, 'acao': 'Revisar estratégias remanescentes'},
                {'progresso': 1.0, 'acao': 'Auto-avaliação final'}
            ],
            'confianca_plano': confianca_plano,
            'similaridade_contexto': similaridade,
            'sugestao_adaptacao': similaridade > 0.7,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        await self._registrar_reflexao(
            'planejamento',
            f"Planejamento para: {objetivo}",
            insights,
            [e['nome'] for e in estrategias_sugeridas],
            confianca=confianca_plano
        )
        
        return plano
    
    async def _buscar_similaridade_contexto(self, contexto: Dict[str, Any]) -> float:
        """Buscar situações similares na memória cognitiva"""
        if not self.memoria_cognitiva:
            return 0.0
        
        try:
            # Buscar memórias de planejamento anteriores
            resultados = await self.memoria_cognitiva.buscar_semantica(
                str(contexto.get('categoria', '')),
                limite=5
            )
            if resultados:
                # Calcular similaridade média (simplificada)
                return 0.6  # Placeholder
        except Exception:
            pass
        return 0.0
    
    async def calibrar_confianca(
        self,
        predicao_feita: Any,
        resultado_real: Any,
        confianca_declarada: float
    ) -> Dict[str, float]:
        """Calibrar estimativa de confiança usando método Bayesiano"""
        correto = (predicao_feita == resultado_real)
        
        # Atualizar calibrador
        self.calibrador.atualizar(correto, confianca_declarada)
        conf_calibrada = self.calibrador.confianca_calibrada()
        intervalo = self.calibrador.intervalo_confianca()
        
        # Análise de calibração
        if correto and confianca_declarada < 0.7:
            direcao = "subconfiança"
            ajuste = 0.05
        elif not correto and confianca_declarada > 0.8:
            direcao = "superconfiança"
            ajuste = -0.1
        else:
            direcao = "calibrado"
            ajuste = 0.0
        
        # Aplicar ajuste suave
        nova_confianca = conf_calibrada + ajuste * 0.3
        nova_confianca = max(0.3, min(0.95, nova_confianca))
        
        insight = f"Confiança calibrada: {nova_confianca:.1%} (intervalo: {intervalo[0]:.1%}-{intervalo[1]:.1%})"
        
        await self._registrar_reflexao(
            'calibracao',
            f"Calibração para predição {'correta' if correto else 'incorreta'}",
            [insight, f"Direção: {direcao}"],
            confianca=nova_confianca
        )
        
        return {
            'confianca_calibrada': nova_confianca,
            'intervalo_inferior': intervalo[0],
            'intervalo_superior': intervalo[1],
            'bem_calibrado': self.calibrador.bem_calibrado(),
            'direcao_ajuste': direcao,
            'taxa_acerto_estimada': self.calibrador.confianca_calibrada()
        }
    
    async def sugerir_adaptacao(self, processo_id: str) -> Optional[Dict[str, Any]]:
        """Sugerir adaptação em tempo real para um processo ativo"""
        if processo_id not in self.processos_monitorados:
            return None
        
        monitor = self.processos_monitorados[processo_id]
        
        # Analisar progresso baseado em checkpoints
        if monitor.checkpoint_avaliacoes:
            ultimo_score = monitor.checkpoint_avaliacoes[-1].get('score', 0.5)
            if ultimo_score < 0.4:
                # Desempenho baixo - sugerir mudança de estratégia
                estrategias_alternativas = [
                    e for e in self.estrategias.values()
                    if e.nome not in monitor.estrategias_usadas and e.efetividade_historica > 0.6
                ]
                if estrategias_alternativas:
                    return {
                        'tipo': 'mudanca_estrategia',
                        'estrategia_sugerida': estrategias_alternativas[0].nome,
                        'justificativa': f"Baixo desempenho (score {ultimo_score:.1%})",
                        'confianca': 0.7
                    }
        
        # Verificar tempo excessivo
        tempo_decorrido = (datetime.now(timezone.utc) - monitor.inicio).total_seconds()
        if monitor.esforco_estimado > 0 and tempo_decorrido > monitor.esforco_estimado * 1.2:
            return {
                'tipo': 'alerta_tempo',
                'mensagem': f"Tempo excedendo estimativa em {(tempo_decorrido / monitor.esforco_estimado - 1):.1%}",
                'acao': 'Revisar plano ou reduzir escopo',
                'confianca': 0.8
            }
        
        return None
    
    async def registrar_checkpoint(
        self,
        processo_id: str,
        progresso: float,
        score: float,
        observacoes: Optional[str] = None
    ):
        """Registrar checkpoint para avaliação de progresso"""
        if processo_id not in self.processos_monitorados:
            return
        
        checkpoint = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'progresso': progresso,
            'score': score,
            'observacoes': observacoes
        }
        self.processos_monitorados[processo_id].checkpoint_avaliacoes.append(checkpoint)
        
        # Verificar necessidade de adaptação
        adaptacao = await self.sugerir_adaptacao(processo_id)
        if adaptacao:
            await self._registrar_reflexao(
                'adaptacao',
                f"Adaptação sugerida para processo {processo_id}",
                [adaptacao['justificativa']],
                [f"Aplicar: {adaptacao.get('acao', adaptacao.get('estrategia_sugerida', ''))}"],
                confianca=adaptacao['confianca']
            )
            self.metricas['total_adaptacoes'] += 1
    
    async def relatorio_desempenho(self, periodo: timedelta = timedelta(days=7)) -> Dict[str, Any]:
        """Gerar relatório de desempenho metacognitivo"""
        agora = datetime.now(timezone.utc)
        processos_recentes = [
            p for p in self.processos_monitorados.values()
            if p.inicio > agora - periodo
        ]
        
        if not processos_recentes:
            return {"status": "Dados insuficientes", "processos": 0}
        
        sucessos = sum(1 for p in processos_recentes if p.sucesso)
        taxa_sucesso = sucessos / len(processos_recentes)
        
        # Análise de estratégias
        estrategias_usadas = defaultdict(int)
        for p in processos_recentes:
            for e in p.estrategias_usadas:
                estrategias_usadas[e] += 1
        
        estrategias_top = sorted(estrategias_usadas.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Calibração
        bem_calibrado = self.calibrador.bem_calibrado()
        
        # Vieses
        rel_vies = self.detector_vies.relatorio_vieses()
        
        # Melhoria ao longo do tempo
        scores_por_tempo = []
        for p in sorted(processos_recentes, key=lambda x: x.inicio):
            if p.checkpoint_avaliacoes:
                score_medio = np.mean([cp['score'] for cp in p.checkpoint_avaliacoes])
                scores_por_tempo.append((p.inicio, score_medio))
        
        tendencia = "estável"
        if len(scores_por_tempo) > 1:
            primeiros = np.mean([s for _, s in scores_por_tempo[:len(scores_por_tempo)//2]])
            ultimos = np.mean([s for _, s in scores_por_tempo[len(scores_por_tempo)//2:]])
            if ultimos > primeiros + 0.1:
                tendencia = "melhorando"
            elif ultimos < primeiros - 0.1:
                tendencia = "piorando"
        
        return {
            'periodo': f"Últimos {periodo.days} dias",
            'processos': len(processos_recentes),
            'taxa_sucesso': taxa_sucesso,
            'estrategias_mais_usadas': estrategias_top,
            'calibracao': {
                'bem_calibrado': bem_calibrado,
                'confianca_media': self.calibrador.confianca_calibrada()
            },
            'vieses': rel_vies,
            'tendencia_desempenho': tendencia,
            'total_reflexoes': len(self.historico_reflexoes),
            'total_adaptacoes': self.metricas['total_adaptacoes'],
            'recomendacoes': self._gerar_recomendacoes(taxa_sucesso, bem_calibrado, rel_vies)
        }
    
    def _gerar_recomendacoes(self, taxa_sucesso: float, bem_calibrado: bool, rel_vies: Dict) -> List[str]:
        """Gerar recomendações baseadas em desempenho"""
        recomendacoes = []
        
        if taxa_sucesso < 0.5:
            recomendacoes.append("Taxa de sucesso baixa. Considere revisar estratégias fundamentais.")
        elif taxa_sucesso > 0.8:
            recomendacoes.append("Bom desempenho. Continue aplicando estratégias efetivas.")
        
        if not bem_calibrado:
            recomendacoes.append("Trabalhe na calibração de confiança com exercícios específicos.")
        
        if rel_vies.get('total', 0) > 5:
            recomendacoes.append("Múltiplos vieses detectados. Aplique técnicas de de-biasing regularmente.")
        
        if self.metricas['total_adaptacoes'] == 0:
            recomendacoes.append("Nenhuma adaptação foi registrada. Considere ser mais proativo nas correções.")
        
        if not recomendacoes:
            recomendacoes.append("Sistema metacognitivo operando adequadamente. Continue monitorando.")
        
        return recomendacoes
    
    async def _armazenar_na_memoria(self, monitor: MonitorCognitivo, avaliacao: Dict):
        """Armazenar experiência na memória cognitiva"""
        if not self.memoria_cognitiva:
            return
        
        try:
            await self.memoria_cognitiva.armazenar(
                conteudo={
                    'processo_id': monitor.processo_id,
                    'descricao': monitor.descricao,
                    'sucesso': monitor.sucesso,
                    'estrategias': monitor.estrategias_usadas,
                    'contexto': monitor.contexto,
                    'avaliacao': avaliacao
                },
                tipo="experiencia_metacognitiva",
                importancia=0.7 if monitor.sucesso else 0.4,
                tags={"metacognicao", "experiencia"}
            )
        except Exception as e:
            logger.debug(f"Erro ao armazenar na memória: {e}")
    
    def exportar_estado(self, formato: str = 'json') -> Union[str, bytes]:
        """Exportar estado metacognitivo para backup"""
        dados = {
            'versao': '7.0.0',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'nivel_atual': self.nivel_atual.value,
            'calibrador': {
                'alpha': self.calibrador.alpha,
                'beta': self.calibrador.beta,
                'historico': list(self.calibrador.historico)
            },
            'vieses': dict(self.detector_vies.vieses_identificados),
            'estrategias': {
                nome: {
                    'nome': e.nome,
                    'tipo': e.tipo.value,
                    'efetividade': e.efetividade_historica,
                    'vezes_usada': e.vezes_usada,
                    'sucessos': e.sucessos
                } for nome, e in self.estrategias.items()
            },
            'pontos_fortes': self.pontos_fortes,
            'pontos_fracos': self.pontos_fracos,
            'metricas': self.metricas,
            'reflexoes_recentes': [
                {
                    'id': r.id,
                    'tipo': r.tipo,
                    'conteudo': r.conteudo[:200],
                    'insights': r.insights,
                    'timestamp': r.timestamp.isoformat()
                } for r in list(self.historico_reflexoes)[-50:]
            ]
        }
        
        if formato == 'json':
            return json.dumps(dados, indent=2, default=str)
        elif formato == 'pickle':
            return pickle.dumps(dados)
        else:
            raise ValueError(f"Formato não suportado: {formato}")
    
    def get_status(self) -> Dict[str, Any]:
        """Obter status detalhado do sistema metacognitivo"""
        return {
            'nivel_atual': self.nivel_atual.value,
            'processos_monitorados': len(self.processos_monitorados),
            'processos_ativos': sum(1 for p in self.processos_monitorados.values() if p.fim is None),
            'reflexoes_registradas': len(self.historico_reflexoes),
            'estrategias_disponiveis': len(self.estrategias),
            'confianca_calibrada': self.calibrador.confianca_calibrada(),
            'bem_calibrado': self.calibrador.bem_calibrado(),
            'pontos_fortes': len(self.pontos_fortes),
            'pontos_fracos': len(self.pontos_fracos),
            'vieses_identificados': len(self.detector_vies.vieses_identificados),
            'metricas': self.metricas,
            'memoria_integrada': self.memoria_cognitiva is not None
        }


# Exemplo de uso assíncrono
async def exemplo_metacognicao():
    """Exemplo completo de uso do sistema de metacognição"""
    
    # Inicializar sistema (opcionalmente com memória cognitiva)
    metacog = Metacognicao(nivel_inicial=NivelMetacognicao.REFLEXIVO)
    
    # Iniciar monitoramento de um processo
    processo_id = await metacog.iniciar_monitoramento(
        "analise_mercado_001",
        "Análise de tendências de mercado para decisão de investimento",
        contexto={"complexidade": "alta", "prazo": "curto", "categoria": "trading"},
        confianca_inicial=0.75,
        esforco_estimado=300  # 5 minutos
    )
    
    # Registrar checkpoints
    await metacog.registrar_checkpoint(processo_id, 0.25, 0.8, "Análise inicial concluída")
    await metacog.registrar_checkpoint(processo_id, 0.5, 0.65, "Encontrada dificuldade técnica")
    
    # Planejar abordagem
    plano = await metacog.planejar_abordagem(
        "Decidir compra/venda de ativo",
        {"complexidade": "alta", "prazo": "curto", "sucessos_recentes": 3}
    )
    print("Plano sugerido:", plano)
    
    # Simular uso de estratégia
    processo = metacog.processos_monitorados[processo_id]
    processo.estrategias_usadas.append("análise_detalhada")
    
    # Finalizar processo
    await metacog.finalizar_monitoramento(
        processo_id,
        sucesso=True,
        dificuldades=["tempo_subestimado"],
        confianca_final=0.85,
        esforco_real=400
    )
    
    # Calibrar confiança
    calibracao = await metacog.calibrar_confianca("alta", "alta", 0.9)
    print("Calibração:", calibracao)
    
    # Gerar relatório
    relatorio = await metacog.relatorio_desempenho()
    print("Relatório:", relatorio)
    
    # Status
    status = metacog.get_status()
    print("Status:", status)
    
    return metacog


if __name__ == "__main__":
    asyncio.run(exemplo_metacognicao())
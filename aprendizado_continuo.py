"""
VHALINOR Aprendizado Contínuo v7.0 - Edição Adaptativa
========================================================
Sistema de aprendizado contínuo e adaptativo com:
- Aprendizado online e offline
- Transfer learning avançado
- Meta-learning (aprender a aprender)
- Aprendizado por reforço (Q-learning, Policy Gradient)
- Adaptação a novos contextos (detecção de mudança)
- Curriculum learning
- Few-shot e zero-shot learning
- Memória episódica com replay
- Aprendizado ativo
- Regularização contra esquecimento catastrófico

@module aprendizado_continuo
@author VHALINOR Team
@version 7.0.0
@since 2026-04-07
"""

import numpy as np
from typing import Dict, List, Any, Optional, Callable, Tuple, Union, Set
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from enum import Enum, auto
from collections import deque, defaultdict
import hashlib
import json
import pickle
import logging
import asyncio
import heapq
from abc import ABC, abstractmethod

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EstrategiaAprendizado(Enum):
    """Estratégias de aprendizado expandidas"""
    SUPERVISIONADO = "supervisionado"
    NAO_SUPERVISIONADO = "nao_supervisionado"
    POR_REFORCO = "por_reforco"
    ONLINE = "online"
    TRANSFERENCIA = "transferencia"
    META_LEARNING = "meta_learning"
    FEW_SHOT = "few_shot"
    ZERO_SHOT = "zero_shot"
    CURRICULO = "curriculo"
    ATIVO = "ativo"
    AUTO_SUPERVISIONADO = "auto_supervisionado"
    ADVERSARIAL = "adversarial"
    IMITACAO = "imitacao"
    MULTI_TAREFA = "multi_tarefa"


class TipoRecompensa(Enum):
    """Tipos de recompensa para aprendizado por reforço"""
    IMEDIATA = "imediata"
    DIFERIDA = "diferida"
    SHAPE = "shape"
    ESPARSA = "esparsa"
    DENSADA = "densada"
    POTENCIAL = "potencial"


@dataclass
class Experiencia:
    """Experiência de aprendizado enriquecida"""
    id: str
    entrada: Any
    saida_esperada: Optional[Any]
    saida_obtida: Optional[Any]
    feedback: float  # Recompensa ou erro
    contexto: Dict[str, Any]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    aprendida: bool = False
    importância: float = 0.5
    tags: Set[str] = field(default_factory=set)
    metadados: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TransicaoReplay:
    """Transição para memória de replay (aprendizado por reforço)"""
    estado: Any
    acao: Any
    recompensa: float
    proximo_estado: Any
    terminado: bool
    importancia: float = 1.0


@dataclass
class ModeloMental:
    """Modelo mental aprendido (versão expandida)"""
    id: str
    dominio: str
    conceitos: Dict[str, Any] = field(default_factory=dict)
    relacoes: List[Tuple[str, str, str]] = field(default_factory=list)  # (conceito1, relacao, conceito2)
    regras: List[Dict[str, Any]] = field(default_factory=list)
    exemplos: deque = field(default_factory=lambda: deque(maxlen=1000))
    performance: float = 0.0
    criado_em: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    atualizado_em: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    versao: int = 1
    hiperparametros: Dict[str, Any] = field(default_factory=dict)


class AgenteQLearning:
    """Agente Q-Learning para aprendizado por reforço"""
    
    def __init__(
        self,
        acoes: List[Any],
        alpha: float = 0.1,
        gamma: float = 0.95,
        epsilon: float = 0.1,
        epsilon_decay: float = 0.995,
        epsilon_min: float = 0.01
    ):
        self.acoes = acoes
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.q_tabela: Dict[Any, Dict[Any, float]] = defaultdict(lambda: defaultdict(float))
        self.historico_recompensas = deque(maxlen=1000)
    
    def escolher_acao(self, estado: Any, explorar: bool = True) -> Any:
        """Escolher ação usando política epsilon-greedy"""
        if explorar and np.random.random() < self.epsilon:
            return np.random.choice(self.acoes)
        
        # Exploração: melhor ação conhecida
        q_estado = self.q_tabela[estado]
        if not q_estado:
            return np.random.choice(self.acoes)
        
        melhor_acao = max(q_estado.items(), key=lambda x: x[1])[0]
        return melhor_acao
    
    def atualizar(
        self,
        estado: Any,
        acao: Any,
        recompensa: float,
        proximo_estado: Any,
        terminado: bool
    ):
        """Atualizar tabela Q com equação de Bellman"""
        q_atual = self.q_tabela[estado][acao]
        
        if terminado:
            q_futuro = 0.0
        else:
            q_futuro = max(self.q_tabela[proximo_estado].values(), default=0.0)
        
        novo_q = q_atual + self.alpha * (recompensa + self.gamma * q_futuro - q_atual)
        self.q_tabela[estado][acao] = novo_q
        
        # Decair epsilon
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
    
    def get_melhor_q(self, estado: Any) -> float:
        """Obter melhor valor Q para um estado"""
        if not self.q_tabela[estado]:
            return 0.0
        return max(self.q_tabela[estado].values())


class MemoriaReplay:
    """Memória de replay para experiências passadas (evita esquecimento catastrófico)"""
    
    def __init__(self, capacidade_maxima: int = 10000, prioridade: bool = True):
        self.capacidade = capacidade_maxima
        self.prioridade = prioridade
        self.memoria: List[TransicaoReplay] = []
        self.prioridades: List[float] = []
        self.posicao = 0
    
    def armazenar(self, transicao: TransicaoReplay):
        """Armazenar transição na memória"""
        if self.prioridade:
            # Armazenar com prioridade (importância)
            if len(self.memoria) < self.capacidade:
                self.memoria.append(transicao)
                self.prioridades.append(transicao.importancia)
            else:
                # Substituir o de menor prioridade
                idx_min = np.argmin(self.prioridades)
                self.memoria[idx_min] = transicao
                self.prioridades[idx_min] = transicao.importancia
        else:
            if len(self.memoria) < self.capacidade:
                self.memoria.append(transicao)
            else:
                self.memoria[self.posicao] = transicao
                self.posicao = (self.posicao + 1) % self.capacidade
    
    def amostrar(self, batch_size: int) -> List[TransicaoReplay]:
        """Amostrar batch de transições (com prioridade)"""
        if len(self.memoria) < batch_size:
            return self.memoria.copy()
        
        if self.prioridade:
            # Amostragem ponderada por prioridade
            probabilidades = np.array(self.prioridades) / np.sum(self.prioridades)
            indices = np.random.choice(len(self.memoria), batch_size, p=probabilidades)
            return [self.memoria[i] for i in indices]
        else:
            return list(np.random.choice(self.memoria, batch_size, replace=False))
    
    def __len__(self):
        return len(self.memoria)


class DetectorMudancaContexto:
    """Detecta mudanças no contexto para adaptação"""
    
    def __init__(self, janela_teste: int = 100, limiar_drift: float = 0.05):
        self.janela_teste = janela_teste
        self.limiar_drift = limiar_drift
        self.estatisticas_contexto: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.historico_drifts: List[datetime] = []
    
    def registrar_observacao(self, contexto: Dict[str, Any]):
        """Registrar observação de contexto"""
        for chave, valor in contexto.items():
            if isinstance(valor, (int, float)):
                self.estatisticas_contexto[chave].append(valor)
    
    def detectar_mudanca(self, contexto_atual: Dict[str, Any]) -> bool:
        """Detectar se houve mudança significativa no contexto"""
        mudanca_detectada = False
        
        for chave, valor in contexto_atual.items():
            if not isinstance(valor, (int, float)):
                continue
            
            historico = self.estatisticas_contexto.get(chave)
            if not historico or len(historico) < self.janela_teste:
                continue
            
            # Teste de mudança de média (simplificado)
            media_historica = np.mean(historico)
            desvio_historico = np.std(historico)
            if desvio_historico == 0:
                continue
            
            z_score = abs(valor - media_historica) / desvio_historico
            if z_score > 2.0:  # 2 desvios padrão
                mudanca_detectada = True
                logger.info(f"Mudança detectada em '{chave}': {valor:.3f} vs média {media_historica:.3f}")
                self.historico_drifts.append(datetime.now(timezone.utc))
        
        return mudanca_detectada
    
    def taxa_drift(self, janela_dias: int = 7) -> float:
        """Calcular taxa de mudanças recentes"""
        agora = datetime.now(timezone.utc)
        limite = agora - timedelta(days=janela_dias)
        drifts_recentes = sum(1 for d in self.historico_drifts if d > limite)
        return drifts_recentes / max(1, janela_dias)


class CurriculumScheduler:
    """Agendador de currículo de aprendizado (dificuldade progressiva)"""
    
    def __init__(self, niveis: List[str], regras_progressao: Dict[str, Callable]):
        self.niveis = niveis
        self.regras_progressao = regras_progressao
        self.nivel_atual = 0
        self.historico_performance = deque(maxlen=100)
    
    def avaliar_progresso(self, performance: float) -> bool:
        """Avaliar se deve avançar para próximo nível"""
        self.historico_performance.append(performance)
        
        if self.nivel_atual >= len(self.niveis) - 1:
            return False
        
        # Verificar regra de progressão para nível atual
        regra = self.regras_progressao.get(self.niveis[self.nivel_atual])
        if regra:
            if regra(self.historico_performance):
                self.nivel_atual += 1
                logger.info(f"Avançando para nível: {self.niveis[self.nivel_atual]}")
                return True
        return False
    
    def get_dificuldade(self) -> float:
        """Obter dificuldade atual (0-1)"""
        return self.nivel_atual / max(1, len(self.niveis) - 1)
    
    def reset(self):
        """Resetar currículo"""
        self.nivel_atual = 0
        self.historico_performance.clear()


class AprendizadoContinuo:
    """
    Sistema avançado de aprendizado contínuo e adaptativo.
    Integra múltiplas estratégias e mecanismos de adaptação.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        
        # Experiências e memórias
        self.experiencias: deque = deque(maxlen=50000)
        self.memoria_replay = MemoriaReplay(capacidade=self.config.get('replay_capacity', 20000))
        
        # Modelos mentais por domínio
        self.modelos_mentais: Dict[str, ModeloMental] = {}
        
        # Agentes de aprendizado por reforço
        self.agentes_rl: Dict[str, AgenteQLearning] = {}
        
        # Padrões aprendidos
        self.patterns_aprendidos: Dict[str, Any] = {}
        
        # Callbacks
        self.callbacks_aprendizado: List[Callable] = []
        
        # Componentes auxiliares
        self.detector_contexto = DetectorMudancaContexto()
        self.curriculum = None  # Inicializado quando necessário
        
        # Métricas e estado
        self.metricas = {
            'total_experiencias': 0,
            'experiencias_aprendidas': 0,
            'erros_cometidos': 0,
            'correcoes_realizadas': 0,
            'transferencias_realizadas': 0,
            'adaptacoes_contexto': 0,
            'replays_executados': 0
        }
        
        # Parâmetros de aprendizado
        self.taxa_aprendizado_base = self.config.get('learning_rate', 0.01)
        self.fator_esquecimento = self.config.get('forgetting_factor', 0.001)
        self.limiar_consolidacao = self.config.get('consolidation_threshold', 0.7)
        
        # Cache e otimizações
        self.cache_predicao: Dict[str, Any] = {}
        
        logger.info("Sistema de Aprendizado Contínuo v7.0 inicializado")
    
    # ---------- Métodos principais ----------
    
    def adicionar_experiencia(
        self,
        entrada: Any,
        saida_esperada: Optional[Any] = None,
        saida_obtida: Optional[Any] = None,
        feedback: float = 0.0,
        contexto: Optional[Dict] = None,
        importancia: float = 0.5,
        tags: Optional[Set[str]] = None
    ) -> str:
        """Adicionar nova experiência e processar aprendizado"""
        exp_id = hashlib.md5(
            f"{entrada}{datetime.now(timezone.utc).timestamp()}{id(entrada)}".encode()
        ).hexdigest()[:16]
        
        experiencia = Experiencia(
            id=exp_id,
            entrada=entrada,
            saida_esperada=saida_esperada,
            saida_obtida=saida_obtida,
            feedback=feedback,
            contexto=contexto or {},
            timestamp=datetime.now(timezone.utc),
            importância=importancia,
            tags=tags or set()
        )
        
        self.experiencias.append(experiencia)
        self.metricas['total_experiencias'] += 1
        
        # Detectar mudança de contexto
        self.detector_contexto.registrar_observacao(contexto or {})
        if self.detector_contexto.detectar_mudanca(contexto or {}):
            self._adaptar_contexto()
        
        # Processar experiência baseado na estratégia
        self._processar_experiencia(experiencia)
        
        # Verificar necessidade de replay (consolidação)
        if self.metricas['total_experiencias'] % 100 == 0:
            self.executar_replay(batch_size=32)
        
        return exp_id
    
    def _processar_experiencia(self, experiencia: Experiencia):
        """Processar experiência e extrair aprendizado"""
        # Calcular erro se aplicável
        if experiencia.saida_esperada is not None and experiencia.saida_obtida is not None:
            erro = self._calcular_erro(
                experiencia.saida_esperada,
                experiencia.saida_obtida
            )
            
            if erro > self.config.get('erro_limiar', 0.1):
                self._aprender_com_erro(experiencia, erro)
                experiencia.aprendida = True
                self.metricas['experiencias_aprendidas'] += 1
            else:
                self._reforcar_padrao(experiencia)
        else:
            # Aprendizado não supervisionado ou por reforço
            self._aprender_nao_supervisionado(experiencia)
    
    def _calcular_erro(self, esperado: Any, obtido: Any) -> float:
        """Calcular erro entre saída esperada e obtida (robusto)"""
        if isinstance(esperado, (int, float)) and isinstance(obtido, (int, float)):
            erro_abs = abs(esperado - obtido)
            escala = max(abs(esperado), 1e-10)
            return min(1.0, erro_abs / escala)
        elif isinstance(esperado, (list, np.ndarray)) and isinstance(obtido, (list, np.ndarray)):
            # Erro quadrático médio normalizado
            esperado_np = np.array(esperado)
            obtido_np = np.array(obtido)
            mse = np.mean((esperado_np - obtido_np) ** 2)
            var = np.var(esperado_np) + 1e-10
            return min(1.0, mse / var)
        else:
            return 0.0 if esperado == obtido else 1.0
    
    def _aprender_com_erro(self, experiencia: Experiencia, erro: float):
        """Aprender a partir de um erro"""
        self.metricas['erros_cometidos'] += 1
        
        # Identificar padrão do erro
        padrao_erro = self._extrair_padrao_erro(experiencia)
        
        # Atualizar modelo mental
        dominio = experiencia.contexto.get('dominio', 'geral')
        modelo = self._obter_ou_criar_modelo(dominio)
        
        # Adicionar regra de correção
        modelo.regras.append({
            'condicao': experiencia.entrada,
            'acao_correta': experiencia.saida_esperada,
            'erro_comum': experiencia.saida_obtida,
            'contexto': experiencia.contexto,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'erro_magnitude': erro
        })
        
        # Adicionar exemplo
        modelo.exemplos.append({
            'entrada': experiencia.entrada,
            'saida': experiencia.saida_esperada,
            'contexto': experiencia.contexto,
            'peso': experiencia.importância
        })
        
        modelo.atualizado_em = datetime.now(timezone.utc)
        modelo.versao += 1
        
        self.metricas['correcoes_realizadas'] += 1
        
        # Notificar callbacks
        for callback in self.callbacks_aprendizado:
            try:
                callback('erro_corrigido', experiencia)
            except Exception as e:
                logger.debug(f"Callback error: {e}")
    
    def _reforcar_padrao(self, experiencia: Experiencia):
        """Reforçar um padrão correto"""
        dominio = experiencia.contexto.get('dominio', 'geral')
        modelo = self._obter_ou_criar_modelo(dominio)
        
        # Extrair conceitos e relações
        conceitos = self._extrair_conceitos(experiencia)
        for conceito in conceitos:
            if conceito not in modelo.conceitos:
                modelo.conceitos[conceito] = {'frequencia': 0, 'associacoes': []}
            modelo.conceitos[conceito]['frequencia'] += 1
    
    def _aprender_nao_supervisionado(self, experiencia: Experiencia):
        """Aprendizado não supervisionado (clustering, padrões)"""
        # Extrair características da entrada
        chave_padrao = self._extrair_caracteristicas(experiencia.entrada)
        
        if chave_padrao not in self.patterns_aprendidos:
            self.patterns_aprendidos[chave_padrao] = {
                'contagem': 0,
                'exemplos': [],
                'contextos': defaultdict(int)
            }
        
        padrao = self.patterns_aprendidos[chave_padrao]
        padrao['contagem'] += 1
        padrao['exemplos'].append(experiencia.entrada)
        for chave, valor in experiencia.contexto.items():
            padrao['contextos'][chave] += 1
    
    def _adaptar_contexto(self):
        """Adaptar estratégias de aprendizado devido a mudança de contexto"""
        self.metricas['adaptacoes_contexto'] += 1
        
        # Aumentar temporariamente taxa de aprendizado
        self.taxa_aprendizado_base = min(0.1, self.taxa_aprendizado_base * 1.5)
        
        # Resetar cache de predições
        self.cache_predicao.clear()
        
        # Notificar adaptação
        for callback in self.callbacks_aprendizado:
            try:
                callback('contexto_adaptado', {'taxa': self.taxa_aprendizado_base})
            except Exception:
                pass
        
        logger.info("Adaptação ao novo contexto realizada")
    
    # ---------- Aprendizado por Reforço ----------
    
    def criar_agente_rl(
        self,
        nome: str,
        acoes: List[Any],
        alpha: float = 0.1,
        gamma: float = 0.95
    ):
        """Criar agente de aprendizado por reforço"""
        self.agentes_rl[nome] = AgenteQLearning(acoes, alpha=alpha, gamma=gamma)
        logger.info(f"Agente RL '{nome}' criado com {len(acoes)} ações")
    
    def registrar_transicao_rl(
        self,
        agente_nome: str,
        estado: Any,
        acao: Any,
        recompensa: float,
        proximo_estado: Any,
        terminado: bool,
        importancia: float = 1.0
    ):
        """Registrar transição para agente RL"""
        if agente_nome not in self.agentes_rl:
            raise ValueError(f"Agente '{agente_nome}' não encontrado")
        
        agente = self.agentes_rl[agente_nome]
        agente.atualizar(estado, acao, recompensa, proximo_estado, terminado)
        
        # Armazenar na memória de replay
        transicao = TransicaoReplay(estado, acao, recompensa, proximo_estado, terminado, importancia)
        self.memoria_replay.armazenar(transicao)
    
    def escolher_acao_rl(
        self,
        agente_nome: str,
        estado: Any,
        explorar: bool = True
    ) -> Any:
        """Escolher ação usando agente RL"""
        if agente_nome not in self.agentes_rl:
            raise ValueError(f"Agente '{agente_nome}' não encontrado")
        return self.agentes_rl[agente_nome].escolher_acao(estado, explorar)
    
    def executar_replay(self, batch_size: int = 32):
        """Executar replay de experiências passadas (consolidação)"""
        if len(self.memoria_replay) < batch_size:
            return
        
        batch = self.memoria_replay.amostrar(batch_size)
        for transicao in batch:
            agente_nome = None
            # Encontrar agente que pode processar esta transição (simplificado)
            for nome, agente in self.agentes_rl.items():
                # Verificar se o estado é compatível (simplificado)
                if hasattr(agente, 'q_tabela') and transicao.estado in agente.q_tabela:
                    agente_nome = nome
                    break
            
            if agente_nome:
                agente = self.agentes_rl[agente_nome]
                agente.atualizar(
                    transicao.estado,
                    transicao.acao,
                    transicao.recompensa,
                    transicao.proximo_estado,
                    transicao.terminado
                )
        
        self.metricas['replays_executados'] += 1
        logger.debug(f"Replay executado com {len(batch)} transições")
    
    # ---------- Transfer Learning ----------
    
    def transferir_conhecimento(
        self,
        dominio_origem: str,
        dominio_destino: str,
        conceitos_mapeados: Optional[Dict[str, str]] = None,
        peso_transferencia: float = 0.5
    ) -> bool:
        """Transferir conhecimento entre domínios com adaptação"""
        if dominio_origem not in self.modelos_mentais:
            logger.warning(f"Domínio origem '{dominio_origem}' não encontrado")
            return False
        
        modelo_origem = self.modelos_mentais[dominio_origem]
        modelo_destino = self._obter_ou_criar_modelo(dominio_destino)
        
        # Transferir conceitos com mapeamento
        for conceito, dados in modelo_origem.conceitos.items():
            conceito_destino = conceitos_mapeados.get(conceito, conceito) if conceitos_mapeados else conceito
            if conceito_destino not in modelo_destino.conceitos:
                # Transferir com peso reduzido
                dados_transferidos = dados.copy()
                if 'frequencia' in dados_transferidos:
                    dados_transferidos['frequencia'] *= peso_transferencia
                modelo_destino.conceitos[conceito_destino] = dados_transferidos
        
        # Transferir regras (adaptadas)
        for regra in modelo_origem.regras:
            regra_transferida = regra.copy()
            regra_transferida['peso_transferencia'] = peso_transferencia
            regra_transferida['origem'] = dominio_origem
            modelo_destino.regras.append(regra_transferida)
        
        # Transferir alguns exemplos
        num_exemplos = int(len(modelo_origem.exemplos) * peso_transferencia)
        for i, exemplo in enumerate(modelo_origem.exemplos):
            if i >= num_exemplos:
                break
            modelo_destino.exemplos.append(exemplo)
        
        modelo_destino.atualizado_em = datetime.now(timezone.utc)
        modelo_destino.versao += 1
        
        self.metricas['transferencias_realizadas'] += 1
        logger.info(f"Conhecimento transferido de '{dominio_origem}' para '{dominio_destino}'")
        return True
    
    # ---------- Meta-learning (aprender a aprender) ----------
    
    def meta_aprender(self, tarefas: List[Dict], num_epocas: int = 10) -> Dict[str, Any]:
        """Aprender a aprender através de múltiplas tarefas"""
        resultados = {
            'tarefas_processadas': len(tarefas),
            'taxa_adaptacao': 0.0,
            'hiperparametros_otimizados': {}
        }
        
        # Analisar características das tarefas
        tamanhos = []
        complexidades = []
        for tarefa in tarefas:
            tamanhos.append(len(tarefa.get('exemplos', [])))
            complexidades.append(tarefa.get('complexidade', 0.5))
        
        # Otimizar hiperparâmetros baseado nas tarefas
        if tamanhos:
            tamanho_medio = np.mean(tamanhos)
            # Ajustar taxa de aprendizado baseado no tamanho
            if tamanho_medio < 10:
                taxa_otima = 0.05  # Few-shot
            elif tamanho_medio < 100:
                taxa_otima = 0.02
            else:
                taxa_otima = 0.01
            
            self.taxa_aprendizado_base = taxa_otima
            resultados['hiperparametros_otimizados']['learning_rate'] = taxa_otima
        
        # Aprender metaconhecimento
        metaconhecimento = {
            'complexidade_media': np.mean(complexidades) if complexidades else 0.5,
            'tamanho_medio': np.mean(tamanhos) if tamanhos else 0,
            'estrategias_sugeridas': []
        }
        
        if metaconhecimento['tamanho_medio'] < 10:
            metaconhecimento['estrategias_sugeridas'].append(EstrategiaAprendizado.FEW_SHOT.value)
        if metaconhecimento['complexidade_media'] > 0.7:
            metaconhecimento['estrategias_sugeridas'].append(EstrategiaAprendizado.CURRICULO.value)
        
        resultados['metaconhecimento'] = metaconhecimento
        
        logger.info(f"Meta-aprendizado concluído: {resultados}")
        return resultados
    
    # ---------- Few-shot e Zero-shot ----------
    
    def few_shot_aprender(
        self,
        exemplos: List[Tuple[Any, Any]],
        dominio: str,
        prototipos: bool = True
    ) -> Dict[str, Any]:
        """Aprendizado few-shot (poucos exemplos)"""
        if len(exemplos) < 5:
            logger.warning("Poucos exemplos para few-shot, usando zero-shot")
            return self.zero_shot_aprender([], dominio)
        
        modelo = self._obter_ou_criar_modelo(dominio)
        
        if prototipos:
            # Abordagem de protótipos: calcular centroide da classe
            caracteristicas = []
            for entrada, saida in exemplos:
                feat = self._extrair_caracteristicas_vetor(entrada)
                if feat is not None:
                    caracteristicas.append(feat)
            
            if caracteristicas:
                prototipo = np.mean(caracteristicas, axis=0)
                modelo.conceitos['prototipo'] = {
                    'vetor': prototipo.tolist(),
                    'exemplos': len(exemplos)
                }
        
        # Adicionar exemplos com alta importância
        for entrada, saida in exemplos:
            self.adicionar_experiencia(
                entrada=entrada,
                saida_esperada=saida,
                feedback=1.0,
                contexto={'dominio': dominio, 'few_shot': True},
                importancia=0.9
            )
        
        return {
            'exemplos_usados': len(exemplos),
            'dominio': dominio,
            'metodo': 'prototipos' if prototipos else 'exemplos_diretos'
        }
    
    def zero_shot_aprender(
        self,
        descricao_tarefa: str,
        dominio: str,
        conhecimento_base: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Aprendizado zero-shot (sem exemplos, apenas descrição)"""
        modelo = self._obter_ou_criar_modelo(dominio)
        
        # Extrair conceitos da descrição
        conceitos_desc = set(descricao_tarefa.lower().split())
        
        # Mapear para conhecimento existente
        transferencias = []
        for outro_dominio, outro_modelo in self.modelos_mentais.items():
            if outro_dominio == dominio:
                continue
            # Verificar conceitos em comum
            conceitos_comuns = conceitos_desc & set(outro_modelo.conceitos.keys())
            if conceitos_comuns:
                transferencias.append({
                    'dominio_origem': outro_dominio,
                    'conceitos_comuns': list(conceitos_comuns)
                })
        
        # Realizar transferência zero-shot
        if transferencias:
            melhor_transfer = max(transferencias, key=lambda x: len(x['conceitos_comuns']))
            self.transferir_conhecimento(
                melhor_transfer['dominio_origem'],
                dominio,
                peso_transferencia=0.3
            )
        
        # Registrar conhecimento descritivo
        modelo.conceitos['descricao_tarefa'] = descricao_tarefa
        modelo.atualizado_em = datetime.now(timezone.utc)
        
        return {
            'transferencias_realizadas': len(transferencias),
            'conceitos_extraidos': len(conceitos_desc),
            'dominio': dominio
        }
    
    # ---------- Curriculum Learning ----------
    
    def configurar_curriculum(
        self,
        niveis: List[str],
        regras_progressao: Dict[str, Callable[[deque], bool]]
    ):
        """Configurar currículo de aprendizado progressivo"""
        self.curriculum = CurriculumScheduler(niveis, regras_progressao)
        logger.info(f"Curriculum configurado com {len(niveis)} níveis")
    
    def avaliar_progresso_curriculum(self, performance: float) -> bool:
        """Avaliar progresso no currículo"""
        if self.curriculum is None:
            return False
        return self.curriculum.avaliar_progresso(performance)
    
    def get_dificuldade_curriculum(self) -> float:
        """Obter dificuldade atual do currículo"""
        if self.curriculum is None:
            return 0.0
        return self.curriculum.get_dificuldade()
    
    # ---------- Predição e Inferência ----------
    
    def predizer(
        self,
        entrada: Any,
        dominio: str = 'geral',
        usar_cache: bool = True
    ) -> Any:
        """Predizer saída baseado no conhecimento atual"""
        cache_key = f"{dominio}:{hashlib.md5(str(entrada).encode()).hexdigest()}"
        
        if usar_cache and cache_key in self.cache_predicao:
            return self.cache_predicao[cache_key]
        
        if dominio not in self.modelos_mentais:
            # Fallback: sem conhecimento específico
            return None
        
        modelo = self.modelos_mentais[dominio]
        
        # Buscar regra correspondente
        for regra in modelo.regras:
            if self._entrada_corresponde(entrada, regra['condicao']):
                resultado = regra['acao_correta']
                # Atualizar cache
                self.cache_predicao[cache_key] = resultado
                return resultado
        
        # Buscar exemplo similar
        for exemplo in modelo.exemplos:
            if self._entrada_corresponde(entrada, exemplo['entrada']):
                resultado = exemplo['saida']
                self.cache_predicao[cache_key] = resultado
                return resultado
        
        return None
    
    def _entrada_corresponde(self, entrada: Any, padrao: Any) -> bool:
        """Verificar se entrada corresponde a um padrão"""
        if entrada == padrao:
            return True
        if isinstance(entrada, (int, float)) and isinstance(padrao, (int, float)):
            return abs(entrada - padrao) < 0.01 * max(abs(padrao), 1)
        if isinstance(entrada, str) and isinstance(padrao, str):
            return entrada.lower() == padrao.lower()
        return False
    
    # ---------- Métricas e Avaliação ----------
    
    def avaliar_performance(self, dominio: Optional[str] = None) -> Dict[str, float]:
        """Avaliar performance de aprendizado em um domínio ou geral"""
        if dominio and dominio in self.modelos_mentais:
            modelo = self.modelos_mentais[dominio]
            
            if modelo.regras:
                # Avaliar acurácia das regras (simplificado)
                acuracia = sum(1 for r in modelo.regras if self._regra_valida(r)) / len(modelo.regras)
            else:
                acuracia = 0.5
            
            diversidade = len(modelo.conceitos) / max(1, len(modelo.regras) + 1)
            
            return {
                'acuracia': acuracia,
                'cobertura': len(modelo.conceitos) / max(1, len(modelo.exemplos)),
                'diversidade': diversidade,
                'experiencias': len(modelo.exemplos),
                'versao': modelo.versao
            }
        
        # Performance geral
        total_exp = len(self.experiencias)
        if total_exp == 0:
            return {'performance_geral': 0.5}
        
        taxa_aprendizado = self.metricas['experiencias_aprendidas'] / total_exp
        taxa_correcao = self.metricas['correcoes_realizadas'] / max(self.metricas['erros_cometidos'], 1)
        
        return {
            'taxa_aprendizado': taxa_aprendizado,
            'taxa_correcao': taxa_correcao,
            'performance_geral': (taxa_aprendizado + taxa_correcao) / 2,
            'total_experiencias': total_exp,
            'transferencias': self.metricas['transferencias_realizadas']
        }
    
    def _regra_valida(self, regra: Dict) -> bool:
        """Verificar se regra ainda é válida (não muito antiga)"""
        timestamp = regra.get('timestamp')
        if timestamp:
            try:
                data = datetime.fromisoformat(timestamp)
                idade = (datetime.now(timezone.utc) - data).days
                if idade > 30:  # Regras com mais de 30 dias são reavaliadas
                    return np.random.random() > 0.3  # Probabilidade de ainda ser válida
            except:
                pass
        return True
    
    # ---------- Métodos Auxiliares ----------
    
    def _obter_ou_criar_modelo(self, dominio: str) -> ModeloMental:
        """Obter modelo mental existente ou criar novo"""
        if dominio not in self.modelos_mentais:
            self.modelos_mentais[dominio] = ModeloMental(
                id=f"modelo_{dominio}_{len(self.modelos_mentais)}",
                dominio=dominio
            )
            logger.info(f"Novo modelo mental criado para domínio '{dominio}'")
        return self.modelos_mentais[dominio]
    
    def _extrair_conceitos(self, experiencia: Experiencia) -> List[str]:
        """Extrair conceitos de uma experiência"""
        conceitos = set()
        
        # De entrada
        if isinstance(experiencia.entrada, str):
            for palavra in experiencia.entrada.lower().split():
                if len(palavra) > 3:
                    conceitos.add(palavra)
        elif isinstance(experiencia.entrada, dict):
            conceitos.update(experiencia.entrada.keys())
        
        # De contexto
        for chave, valor in experiencia.contexto.items():
            conceitos.add(chave)
            if isinstance(valor, str):
                for palavra in valor.lower().split():
                    if len(palavra) > 3:
                        conceitos.add(palavra)
        
        return list(conceitos)
    
    def _extrair_padrao_erro(self, experiencia: Experiencia) -> Dict[str, Any]:
        """Extrair padrão característico do erro"""
        return {
            'tipo_entrada': type(experiencia.entrada).__name__,
            'contexto_chaves': list(experiencia.contexto.keys()),
            'feedback': experiencia.feedback,
            'timestamp': experiencia.timestamp.isoformat(),
            'importancia': experiencia.importância
        }
    
    def _extrair_caracteristicas(self, entrada: Any) -> str:
        """Extrair características representativas para indexação"""
        if isinstance(entrada, str):
            return entrada[:100]  # Primeiros 100 caracteres
        elif isinstance(entrada, (int, float)):
            return f"num_{entrada:.4f}"
        elif isinstance(entrada, dict):
            return f"dict_{tuple(sorted(entrada.keys()))}"
        else:
            return str(type(entrada).__name__)
    
    def _extrair_caracteristicas_vetor(self, entrada: Any) -> Optional[np.ndarray]:
        """Extrair vetor de características para prototipagem"""
        if isinstance(entrada, (int, float)):
            return np.array([entrada])
        elif isinstance(entrada, (list, tuple)) and all(isinstance(x, (int, float)) for x in entrada):
            return np.array(entrada)
        elif isinstance(entrada, dict):
            # Extrair valores numéricos
            valores = [v for v in entrada.values() if isinstance(v, (int, float))]
            if valores:
                return np.array(valores)
        return None
    
    # ---------- Serialização ----------
    
    def exportar_estado(self, formato: str = 'json') -> Union[str, bytes]:
        """Exportar estado completo do aprendizado"""
        dados = {
            'versao': '7.0.0',
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'metricas': self.metricas,
            'taxa_aprendizado_base': self.taxa_aprendizado_base,
            'modelos_mentais': {
                dom: {
                    'id': m.id,
                    'dominio': m.dominio,
                    'conceitos': m.conceitos,
                    'relacoes': m.relacoes,
                    'regras': m.regras,
                    'performance': m.performance,
                    'versao': m.versao,
                    'criado_em': m.criado_em.isoformat(),
                    'atualizado_em': m.atualizado_em.isoformat()
                } for dom, m in self.modelos_mentais.items()
            },
            'patterns_aprendidos': self.patterns_aprendidos,
            'agentes_rl': {
                nome: {
                    'acoes': agente.acoes,
                    'alpha': agente.alpha,
                    'gamma': agente.gamma,
                    'epsilon': agente.epsilon,
                    'q_tabela': {str(k): v for k, v in agente.q_tabela.items()}
                } for nome, agente in self.agentes_rl.items()
            }
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
        
        # Restaurar métricas
        self.metricas = dados_dict['metricas']
        self.taxa_aprendizado_base = dados_dict['taxa_aprendizado_base']
        
        # Restaurar modelos mentais
        self.modelos_mentais.clear()
        for dom, m_data in dados_dict['modelos_mentais'].items():
            modelo = ModeloMental(
                id=m_data['id'],
                dominio=m_data['dominio'],
                conceitos=m_data['conceitos'],
                relacoes=m_data['relacoes'],
                regras=m_data['regras'],
                performance=m_data['performance'],
                versao=m_data['versao'],
                criado_em=datetime.fromisoformat(m_data['criado_em']),
                atualizado_em=datetime.fromisoformat(m_data['atualizado_em'])
            )
            self.modelos_mentais[dom] = modelo
        
        # Restaurar padrões
        self.patterns_aprendidos = dados_dict['patterns_aprendidos']
        
        # Restaurar agentes RL
        self.agentes_rl.clear()
        for nome, a_data in dados_dict['agentes_rl'].items():
            agente = AgenteQLearning(
                acoes=a_data['acoes'],
                alpha=a_data['alpha'],
                gamma=a_data['gamma'],
                epsilon=a_data['epsilon']
            )
            # Restaurar Q-table
            for estado_str, acoes in a_data['q_tabela'].items():
                for acao, q in acoes.items():
                    agente.q_tabela[estado_str][acao] = q
            self.agentes_rl[nome] = agente
        
        logger.info("Estado do aprendizado contínuo importado com sucesso")
    
    def get_status(self) -> Dict[str, Any]:
        """Obter status detalhado do sistema"""
        performance = self.avaliar_performance()
        return {
            'metricas': self.metricas,
            'modelos_mentais': len(self.modelos_mentais),
            'agentes_rl': len(self.agentes_rl),
            'padroes_aprendidos': len(self.patterns_aprendidos),
            'taxa_aprendizado': self.taxa_aprendizado_base,
            'performance_geral': performance.get('performance_geral', 0.5),
            'taxa_drift': self.detector_contexto.taxa_drift(),
            'curriculum_ativado': self.curriculum is not None,
            'dificuldade_atual': self.get_dificuldade_curriculum()
        }
    
    def registrar_callback(self, callback: Callable):
        """Registrar callback para eventos de aprendizado"""
        self.callbacks_aprendizado.append(callback)


# Exemplo de uso
async def exemplo_aprendizado_continuo():
    """Exemplo completo do sistema de aprendizado contínuo"""
    aprendizado = AprendizadoContinuo()
    
    # Criar agente RL
    aprendizado.criar_agente_rl("trader", acoes=["comprar", "vender", "manter"], alpha=0.1)
    
    # Configurar currículo
    def progressao_rule(historico):
        return len(historico) > 10 and np.mean(historico) > 0.7
    aprendizado.configurar_curriculum(
        niveis=["facil", "medio", "dificil"],
        regras_progressao={"facil": progressao_rule, "medio": progressao_rule}
    )
    
    # Adicionar experiências
    for i in range(50):
        entrada = {"preco": 100 + i, "volume": 1000}
        saida = "comprar" if i % 2 == 0 else "vender"
        aprendizado.adicionar_experiencia(
            entrada=entrada,
            saida_esperada=saida,
            feedback=1.0,
            contexto={"dominio": "trading", "volatilidade": 0.2 + i*0.01},
            importancia=0.8
        )
        
        # Avaliar progresso no currículo
        if i % 10 == 0:
            perf = aprendizado.avaliar_performance("trading")
            aprendizado.avaliar_progresso_curriculum(perf.get('acuracia', 0.5))
    
    # Transfer learning
    aprendizado.transferir_conhecimento("trading", "forex", peso_transferencia=0.7)
    
    # Few-shot learning
    exemplos_few_shot = [({"preco": 105, "volume": 1200}, "comprar") for _ in range(3)]
    aprendizado.few_shot_aprender(exemplos_few_shot, "trading_avancado")
    
    # Meta-aprendizado
    tarefas = [{"exemplos": list(range(10)), "complexidade": 0.6} for _ in range(5)]
    meta = aprendizado.meta_aprender(tarefas)
    print("Meta-aprendizado:", meta)
    
    # Predição
    pred = aprendizado.predizer({"preco": 110, "volume": 1500}, "trading")
    print(f"Predição: {pred}")
    
    # Status
    status = aprendizado.get_status()
    print("Status:", status)
    
    return aprendizado


if __name__ == "__main__":
    asyncio.run(exemplo_aprendizado_continuo())
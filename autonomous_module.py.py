"""
Módulo Autonômico LEXTRADER-IAG 4.0
Controle centralizado das ações autônomas da IA Generativa
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Set, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum, auto
import uuid
from decimal import Decimal
from collections import defaultdict
import heapq
import time
from abc import ABC, abstractmethod


# ============================================================================
# ENUMS E CONSTANTES
# ============================================================================

class ActionType(Enum):
    """Tipos de ações autônomas"""
    MARKET_ANALYSIS = auto()           # Análise de mercado
    PORTFOLIO_REBALANCE = auto()       # Rebalanceamento de portfólio
    RISK_ASSESSMENT = auto()           # Avaliação de risco
    STRATEGY_OPTIMIZATION = auto()     # Otimização de estratégia
    DATA_COLLECTION = auto()           # Coleta de dados
    MODEL_TRAINING = auto()            # Treinamento de modelos
    SENTIMENT_ANALYSIS = auto()        # Análise de sentimento
    ARBITRAGE_DETECTION = auto()       # Detecção de arbitragem
    MARKET_MAKING = auto()             # Market making
    ERROR_RECOVERY = auto()            # Recuperação de erros
    PERFORMANCE_REVIEW = auto()        # Revisão de performance
    SYSTEM_HEALTH_CHECK = auto()       # Verificação de saúde
    COMPLIANCE_CHECK = auto()          # Verificação de compliance
    BACKTEST_EXECUTION = auto()        # Execução de backtest
    REPORT_GENERATION = auto()         # Geração de relatórios


class ActionPriority(Enum):
    """Prioridades de ação"""
    CRITICAL = auto()      # Ação imediata, tempo real
    HIGH = auto()          # Ação em minutos
    MEDIUM = auto()        # Ação em horas
    LOW = auto()           # Ação diária
    BACKGROUND = auto()    # Ação em background


class ActionStatus(Enum):
    """Status de execução da ação"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class ExecutionMode(Enum):
    """Modos de execução"""
    REAL_TIME = "real_time"       # Execução em tempo real
    SCHEDULED = "scheduled"       # Execução agendada
    EVENT_DRIVEN = "event_driven" # Execução por evento
    MANUAL = "manual"             # Execução manual


# ============================================================================
# MODELOS DE DADOS
# ============================================================================

@dataclass
class AutonomousAction:
    """Ação autônoma a ser executada"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: ActionType = ActionType.MARKET_ANALYSIS
    name: str = ""
    description: str = ""
    priority: ActionPriority = ActionPriority.MEDIUM
    execution_mode: ExecutionMode = ExecutionMode.SCHEDULED
    frequency: Optional[str] = None  # Cron expression ou timedelta
    next_execution: Optional[datetime] = None
    last_execution: Optional[datetime] = None
    status: ActionStatus = ActionStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    # Configurações de execução
    timeout: int = 300  # segundos
    retry_count: int = 3
    retry_delay: int = 60  # segundos
    dependencies: List[str] = field(default_factory=list)  # IDs de ações dependentes
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    
    # Controle de execução
    current_retry: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    result: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Inicializa próximas execuções se frequência for fornecida"""
        if self.frequency and not self.next_execution:
            self.schedule_next_execution()
    
    def schedule_next_execution(self):
        """Agenda próxima execução baseada na frequência"""
        if self.frequency:
            if self.frequency.startswith("cron:"):
                # Implementar lógica de cron
                pass
            else:
                # Frequência em segundos
                try:
                    seconds = int(self.frequency)
                    self.next_execution = datetime.now(timezone.utc) + timedelta(seconds=seconds)
                except ValueError:
                    pass
    
    @property
    def is_due(self) -> bool:
        """Verifica se a ação está programada para execução"""
        if self.next_execution is None:
            return False
        return datetime.now(timezone.utc) >= self.next_execution
    
    @property
    def is_running(self) -> bool:
        """Verifica se a ação está em execução"""
        return self.status == ActionStatus.RUNNING
    
    @property
    def can_retry(self) -> bool:
        """Verifica se pode tentar novamente"""
        return self.current_retry < self.retry_count
    
    def start(self):
        """Inicia a execução da ação"""
        self.status = ActionStatus.RUNNING
        self.start_time = datetime.now(timezone.utc)
        self.updated_at = self.start_time
    
    def complete(self, result: Any = None):
        """Completa a execução com sucesso"""
        self.status = ActionStatus.COMPLETED
        self.end_time = datetime.now(timezone.utc)
        self.result = result
        self.updated_at = self.end_time
        self.schedule_next_execution()
    
    def fail(self, error: str):
        """Marca a execução como falha"""
        self.status = ActionStatus.FAILED
        self.end_time = datetime.now(timezone.utc)
        self.error_message = error
        self.updated_at = self.end_time
        self.current_retry += 1
        
        if self.can_retry:
            self.schedule_retry()
    
    def schedule_retry(self):
        """Agenda nova tentativa"""
        retry_time = datetime.now(timezone.utc) + timedelta(seconds=self.retry_delay)
        self.next_execution = retry_time
        self.status = ActionStatus.PENDING
        self.updated_at = datetime.now(timezone.utc)


@dataclass
class ActionScheduler:
    """Agendador de ações"""
    action: AutonomousAction
    callback: Callable[[AutonomousAction], Awaitable[Any]]
    condition: Optional[Callable[[], bool]] = None


@dataclass
class ExecutionMetrics:
    """Métricas de execução"""
    action_id: str
    execution_time: float  # segundos
    success: bool
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    network_usage: Optional[float] = None


@dataclass
class ModuleHealth:
    """Saúde do módulo autônomo"""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    total_actions: int = 0
    running_actions: int = 0
    pending_actions: int = 0
    completed_actions: int = 0
    failed_actions: int = 0
    avg_execution_time: float = 0.0
    success_rate: float = 0.0
    resource_usage: Dict[str, float] = field(default_factory=dict)
    alerts: List[str] = field(default_factory=list)


# ============================================================================
# INTERFACES PARA FUNÇÕES SECUNDÁRIAS
# ============================================================================

class SecondaryFunction(ABC):
    """Interface para funções secundárias"""
    
    @abstractmethod
    async def initialize(self, config: Dict[str, Any]):
        """Inicializa a função"""
        pass
    
    @abstractmethod
    async def execute(self, action: AutonomousAction) -> Any:
        """Executa a função"""
        pass
    
    @abstractmethod
    async def cleanup(self):
        """Limpeza da função"""
        pass
    
    @abstractmethod
    def get_metrics(self) -> Dict[str, Any]:
        """Retorna métricas da função"""
        pass


class MarketAnalyzer(SecondaryFunction):
    """Analisador de mercado"""
    
    async def execute(self, action: AutonomousAction) -> Dict[str, Any]:
        """Executa análise de mercado"""
        return {
            "timestamp": datetime.now(timezone.utc),
            "market_condition": "bullish",
            "volatility": 0.15,
            "correlation_matrix": {},
            "recommendations": []
        }


class PortfolioRebalancer(SecondaryFunction):
    """Rebalanceador de portfólio"""
    
    async def execute(self, action: AutonomousAction) -> Dict[str, Any]:
        """Executa rebalanceamento"""
        return {
            "rebalanced": True,
            "adjustments": [],
            "expected_improvement": 0.02
        }


class RiskAssessor(SecondaryFunction):
    """Avaliador de risco"""
    
    async def execute(self, action: AutonomousAction) -> Dict[str, Any]:
        """Executa avaliação de risco"""
        return {
            "risk_score": 0.3,
            "var_95": 0.05,
            "stress_test_results": {},
            "recommendations": []
        }


class StrategyOptimizer(SecondaryFunction):
    """Otimizador de estratégias"""
    
    async def execute(self, action: AutonomousAction) -> Dict[str, Any]:
        """Otimiza estratégias"""
        return {
            "optimized_strategies": [],
            "performance_improvement": 0.1,
            "new_parameters": {}
        }


class DataCollector(SecondaryFunction):
    """Coletor de dados"""
    
    async def execute(self, action: AutonomousAction) -> Dict[str, Any]:
        """Coleta dados"""
        return {
            "collected_data": {},
            "sources": [],
            "data_quality": 0.95
        }


class ModelTrainer(SecondaryFunction):
    """Treinador de modelos"""
    
    async def execute(self, action: AutonomousAction) -> Dict[str, Any]:
        """Treina modelos"""
        return {
            "trained_models": [],
            "accuracy": 0.85,
            "training_time": 300
        }


# ============================================================================
# MÓDULO AUTÔNOMO PRINCIPAL
# ============================================================================

class AutonomousModule:
    """
    Módulo autônomo principal
    Controla todas as ações autônomas da IAG
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = self._setup_logging()
        
        # Estado do módulo
        self.is_running = False
        self.start_time = None
        
        # Registro de ações
        self.actions: Dict[str, AutonomousAction] = {}
        self.scheduled_actions: List[AutonomousAction] = []
        self.running_actions: Set[str] = set()
        self.action_history: List[AutonomousAction] = []
        
        # Funções secundárias
        self.secondary_functions: Dict[ActionType, SecondaryFunction] = {}
        
        # Métricas
        self.execution_metrics: List[ExecutionMetrics] = []
        self.health_check_interval = config.get('health_check_interval', 60)
        
        # Scheduler
        self.scheduler_task: Optional[asyncio.Task] = None
        self.execution_tasks: Dict[str, asyncio.Task] = {}
        
        # Eventos
        self.action_completed_event = asyncio.Event()
        self.shutdown_event = asyncio.Event()
        
        self.logger.info("Módulo Autônomo inicializado")
    
    def _setup_logging(self) -> logging.Logger:
        """Configura sistema de logging"""
        logger = logging.getLogger("AutonomousModule")
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    async def initialize(self):
        """Inicializa o módulo"""
        self.logger.info("Inicializando módulo autônomo...")
        
        # Inicializar funções secundárias
        await self._initialize_secondary_functions()
        
        # Carregar ações configuradas
        await self._load_configured_actions()
        
        # Iniciar scheduler
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())
        
        # Iniciar monitor de saúde
        asyncio.create_task(self._health_monitor_loop())
        
        self.is_running = True
        self.start_time = datetime.now(timezone.utc)
        
        self.logger.info("Módulo autônomo inicializado com sucesso")
    
    async def _initialize_secondary_functions(self):
        """Inicializa todas as funções secundárias"""
        function_map = {
            ActionType.MARKET_ANALYSIS: MarketAnalyzer(),
            ActionType.PORTFOLIO_REBALANCE: PortfolioRebalancer(),
            ActionType.RISK_ASSESSMENT: RiskAssessor(),
            ActionType.STRATEGY_OPTIMIZATION: StrategyOptimizer(),
            ActionType.DATA_COLLECTION: DataCollector(),
            ActionType.MODEL_TRAINING: ModelTrainer(),
        }
        
        for action_type, function in function_map.items():
            await function.initialize(self.config)
            self.secondary_functions[action_type] = function
        
        self.logger.info(f"Inicializadas {len(self.secondary_functions)} funções secundárias")
    
    async def _load_configured_actions(self):
        """Carrega ações da configuração"""
        default_actions = [
            AutonomousAction(
                name="Análise de Mercado Contínua",
                type=ActionType.MARKET_ANALYSIS,
                description="Análise contínua das condições de mercado",
                priority=ActionPriority.HIGH,
                execution_mode=ExecutionMode.REAL_TIME,
                frequency="300",  # 5 minutos
                timeout=180
            ),
            AutonomousAction(
                name="Rebalanceamento de Portfólio Diário",
                type=ActionType.PORTFOLIO_REBALANCE,
                description="Rebalanceamento automático do portfólio",
                priority=ActionPriority.MEDIUM,
                execution_mode=ExecutionMode.SCHEDULED,
                frequency="86400",  # 24 horas
                timeout=600
            ),
            AutonomousAction(
                name="Avaliação de Risco em Tempo Real",
                type=ActionType.RISK_ASSESSMENT,
                description="Monitoramento contínuo de risco",
                priority=ActionPriority.CRITICAL,
                execution_mode=ExecutionMode.REAL_TIME,
                frequency="60",  # 1 minuto
                timeout=120
            ),
            AutonomousAction(
                name="Otimização Semanal de Estratégias",
                type=ActionType.STRATEGY_OPTIMIZATION,
                description="Otimização periódica das estratégias",
                priority=ActionPriority.LOW,
                execution_mode=ExecutionMode.SCHEDULED,
                frequency="604800",  # 7 dias
                timeout=1800
            ),
            AutonomousAction(
                name="Coleta de Dados de Mercado",
                type=ActionType.DATA_COLLECTION,
                description="Coleta automática de dados",
                priority=ActionPriority.MEDIUM,
                execution_mode=ExecutionMode.SCHEDULED,
                frequency="3600",  # 1 hora
                timeout=900
            ),
            AutonomousAction(
                name="Treinamento de Modelos de IA",
                type=ActionType.MODEL_TRAINING,
                description="Treinamento periódico de modelos",
                priority=ActionPriority.BACKGROUND,
                execution_mode=ExecutionMode.SCHEDULED,
                frequency="2592000",  # 30 dias
                timeout=7200
            ),
            AutonomousAction(
                name="Verificação de Saúde do Sistema",
                type=ActionType.SYSTEM_HEALTH_CHECK,
                description="Verificação periódica da saúde do sistema",
                priority=ActionPriority.HIGH,
                execution_mode=ExecutionMode.SCHEDULED,
                frequency="3600",  # 1 hora
                timeout=300
            ),
        ]
        
        for action in default_actions:
            self.register_action(action)
        
        self.logger.info(f"Carregadas {len(default_actions)} ações padrão")
    
    def register_action(self, action: AutonomousAction) -> str:
        """Registra uma nova ação autônoma"""
        self.actions[action.id] = action
        
        if action.execution_mode == ExecutionMode.SCHEDULED:
            self.scheduled_actions.append(action)
            self.scheduled_actions.sort(key=lambda x: x.next_execution or datetime.max)
        
        self.logger.info(f"Ação registrada: {action.name} (ID: {action.id})")
        return action.id
    
    def unregister_action(self, action_id: str) -> bool:
        """Remove uma ação do registro"""
        if action_id in self.actions:
            action = self.actions[action_id]
            
            if action.is_running:
                self.logger.warning(f"Não é possível remover ação em execução: {action_id}")
                return False
            
            # Remove de scheduled_actions
            self.scheduled_actions = [a for a in self.scheduled_actions if a.id != action_id]
            
            # Remove do registro principal
            del self.actions[action_id]
            
            self.logger.info(f"Ação removida: {action_id}")
            return True
        
        return False
    
    async def _scheduler_loop(self):
        """Loop principal do scheduler"""
        self.logger.info("Scheduler iniciado")
        
        while not self.shutdown_event.is_set():
            try:
                # Verificar ações agendadas
                await self._check_scheduled_actions()
                
                # Executar ações em tempo real
                await self._check_real_time_actions()
                
                # Esperar próximo ciclo
                await asyncio.sleep(1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Erro no scheduler: {e}")
                await asyncio.sleep(5)
    
    async def _check_scheduled_actions(self):
        """Verifica e executa ações agendadas"""
        current_time = datetime.now(timezone.utc)
        
        for action in list(self.scheduled_actions):
            if action.is_due and not action.is_running:
                # Verificar dependências
                if await self._check_dependencies(action):
                    await self.execute_action(action.id)
    
    async def _check_real_time_actions(self):
        """Verifica ações em tempo real"""
        real_time_actions = [
            action for action in self.actions.values()
            if action.execution_mode == ExecutionMode.REAL_TIME 
            and not action.is_running
            and action.status == ActionStatus.PENDING
        ]
        
        for action in real_time_actions:
            if await self._check_dependencies(action):
                await self.execute_action(action.id)
    
    async def _check_dependencies(self, action: AutonomousAction) -> bool:
        """Verifica se as dependências foram satisfeitas"""
        for dep_id in action.dependencies:
            if dep_id in self.actions:
                dep_action = self.actions[dep_id]
                if dep_action.status != ActionStatus.COMPLETED:
                    return False
        return True
    
    async def execute_action(self, action_id: str) -> bool:
        """Executa uma ação específica"""
        if action_id not in self.actions:
            self.logger.error(f"Ação não encontrada: {action_id}")
            return False
        
        action = self.actions[action_id]
        
        if action.is_running:
            self.logger.warning(f"Ação já em execução: {action_id}")
            return False
        
        # Verificar se pode executar
        if not action.can_retry and action.status == ActionStatus.FAILED:
            self.logger.warning(f"Ação falhou e não pode ser reexecutada: {action_id}")
            return False
        
        # Marcar como em execução
        action.start()
        self.running_actions.add(action_id)
        
        # Criar task de execução
        task = asyncio.create_task(
            self._execute_action_task(action),
            name=f"action_{action_id}"
        )
        self.execution_tasks[action_id] = task
        
        self.logger.info(f"Iniciando execução da ação: {action.name}")
        return True
    
    async def _execute_action_task(self, action: AutonomousAction):
        """Task de execução da ação"""
        start_time = time.time()
        
        try:
            # Executar função secundária correspondente
            if action.type in self.secondary_functions:
                function = self.secondary_functions[action.type]
                result = await asyncio.wait_for(
                    function.execute(action),
                    timeout=action.timeout
                )
                
                # Marcar como completada
                action.complete(result)
                self.logger.info(f"Ação completada com sucesso: {action.name}")
                
            else:
                raise ValueError(f"Função secundária não encontrada para tipo: {action.type}")
            
        except asyncio.TimeoutError:
            error_msg = f"Timeout na execução da ação: {action.name}"
            action.fail(error_msg)
            self.logger.error(error_msg)
            
        except Exception as e:
            error_msg = f"Erro na execução da ação {action.name}: {str(e)}"
            action.fail(error_msg)
            self.logger.error(error_msg, exc_info=True)
            
        finally:
            # Limpar recursos
            execution_time = time.time() - start_time
            
            # Registrar métricas
            metrics = ExecutionMetrics(
                action_id=action.id,
                execution_time=execution_time,
                success=action.status == ActionStatus.COMPLETED
            )
            self.execution_metrics.append(metrics)
            
            # Remover de running actions
            self.running_actions.discard(action.id)
            
            # Remover task
            self.execution_tasks.pop(action.id, None)
            
            # Adicionar ao histórico
            self.action_history.append(action)
            
            # Limitar tamanho do histórico
            if len(self.action_history) > 1000:
                self.action_history = self.action_history[-1000:]
            
            # Sinalizar que uma ação foi completada
            self.action_completed_event.set()
            self.action_completed_event.clear()
    
    async def execute_manual_action(self, action_type: ActionType, params: Dict[str, Any] = None) -> Any:
        """Executa uma ação manualmente"""
        action = AutonomousAction(
            name=f"Manual Action - {action_type.name}",
            type=action_type,
            description="Ação manual executada pelo usuário",
            priority=ActionPriority.CRITICAL,
            execution_mode=ExecutionMode.MANUAL,
            metadata=params or {}
        )
        
        self.register_action(action)
        await self.execute_action(action.id)
        
        # Esperar conclusão
        try:
            await asyncio.wait_for(
                self.wait_for_action_completion(action.id),
                timeout=action.timeout + 30
            )
        except asyncio.TimeoutError:
            self.logger.error(f"Timeout aguardando ação manual: {action.id}")
        
        return action.result
    
    async def wait_for_action_completion(self, action_id: str, timeout: Optional[float] = None):
        """Aguarda a conclusão de uma ação"""
        start_time = time.time()
        
        while True:
            if action_id not in self.actions:
                raise ValueError(f"Ação não encontrada: {action_id}")
            
            action = self.actions[action_id]
            if action.status in [ActionStatus.COMPLETED, ActionStatus.FAILED, ActionStatus.CANCELLED]:
                return
            
            if timeout and (time.time() - start_time) > timeout:
                raise asyncio.TimeoutError(f"Timeout aguardando ação: {action_id}")
            
            await asyncio.sleep(0.1)
    
    async def _health_monitor_loop(self):
        """Monitora a saúde do módulo"""
        self.logger.info("Monitor de saúde iniciado")
        
        while not self.shutdown_event.is_set():
            try:
                health = self.get_health()
                
                # Verificar alertas
                await self._check_health_alerts(health)
                
                # Log de saúde periódico
                if len(self.execution_metrics) % 10 == 0:  # A cada 10 execuções
                    self.logger.info(f"Status saúde: {health.success_rate:.1%} sucesso")
                
                await asyncio.sleep(self.health_check_interval)
                
            except Exception as e:
                self.logger.error(f"Erro no monitor de saúde: {e}")
                await asyncio.sleep(30)
    
    async def _check_health_alerts(self, health: ModuleHealth):
        """Verifica e dispara alertas de saúde"""
        alerts = []
        
        # Verificar taxa de sucesso
        if health.success_rate < 0.8:  # 80%
            alerts.append(f"Taxa de sucesso baixa: {health.success_rate:.1%}")
        
        # Verificar ações falhadas
        if health.failed_actions > 10:
            alerts.append(f"Muitas ações falhadas: {health.failed_actions}")
        
        # Verificar tempo médio de execução
        if health.avg_execution_time > 300:  # 5 minutos
            alerts.append(f"Tempo médio de execução alto: {health.avg_execution_time:.1f}s")
        
        # Disparar alertas se necessário
        if alerts:
            health.alerts = alerts
            await self._trigger_alerts(alerts)
    
    async def _trigger_alerts(self, alerts: List[str]):
        """Dispara alertas"""
        for alert in alerts:
            self.logger.warning(f"ALERTA: {alert}")
            # Aqui você poderia integrar com sistemas de notificação
            # como email, Slack, Telegram, etc.
    
    def get_health(self) -> ModuleHealth:
        """Obtém métricas de saúde do módulo"""
        total = len(self.actions)
        running = len(self.running_actions)
        pending = sum(1 for a in self.actions.values() if a.status == ActionStatus.PENDING)
        completed = sum(1 for a in self.action_history if a.status == ActionStatus.COMPLETED)
        failed = sum(1 for a in self.action_history if a.status == ActionStatus.FAILED)
        
        # Calcular tempo médio de execução
        avg_time = 0.0
        if self.execution_metrics:
            avg_time = sum(m.execution_time for m in self.execution_metrics[-100:]) / len(self.execution_metrics[-100:])
        
        # Calcular taxa de sucesso
        success_rate = 0.0
        if completed + failed > 0:
            success_rate = completed / (completed + failed)
        
        return ModuleHealth(
            total_actions=total,
            running_actions=running,
            pending_actions=pending,
            completed_actions=completed,
            failed_actions=failed,
            avg_execution_time=avg_time,
            success_rate=success_rate
        )
    
    def get_action_status(self, action_id: str) -> Optional[Dict[str, Any]]:
        """Obtém status de uma ação específica"""
        if action_id in self.actions:
            action = self.actions[action_id]
            return {
                "id": action.id,
                "name": action.name,
                "status": action.status.value,
                "start_time": action.start_time,
                "end_time": action.end_time,
                "error_message": action.error_message,
                "result": action.result
            }
        return None
    
    def list_actions(self, filter_type: Optional[ActionType] = None) -> List[Dict[str, Any]]:
        """Lista todas as ações"""
        actions = self.actions.values()
        
        if filter_type:
            actions = [a for a in actions if a.type == filter_type]
        
        return [{
            "id": a.id,
            "name": a.name,
            "type": a.type.name,
            "status": a.status.value,
            "priority": a.priority.name,
            "next_execution": a.next_execution,
            "last_execution": a.last_execution
        } for a in actions]
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Gera relatório de performance"""
        health = self.get_health()
        
        # Agrupar métricas por tipo de ação
        type_metrics = defaultdict(lambda: {"count": 0, "success": 0, "total_time": 0.0})
        
        for action in self.action_history[-1000:]:  # Últimas 1000 ações
            metrics = type_metrics[action.type.name]
            metrics["count"] += 1
            if action.status == ActionStatus.COMPLETED:
                metrics["success"] += 1
        
        return {
            "module_uptime": (datetime.now(timezone.utc) - self.start_time).total_seconds() if self.start_time else 0,
            "health_metrics": {
                "total_actions": health.total_actions,
                "success_rate": health.success_rate,
                "avg_execution_time": health.avg_execution_time,
                "alerts": health.alerts
            },
            "action_type_metrics": dict(type_metrics),
            "recent_actions": [
                {
                    "name": a.name,
                    "status": a.status.value,
                    "execution_time": (a.end_time - a.start_time).total_seconds() if a.start_time and a.end_time else None,
                    "timestamp": a.updated_at
                }
                for a in self.action_history[-10:]  # Últimas 10 ações
            ]
        }
    
    async def pause_action(self, action_id: str) -> bool:
        """Pausa uma ação em execução"""
        if action_id in self.running_actions and action_id in self.execution_tasks:
            task = self.execution_tasks[action_id]
            task.cancel()
            
            action = self.actions[action_id]
            action.status = ActionStatus.PAUSED
            action.updated_at = datetime.now(timezone.utc)
            
            self.logger.info(f"Ação pausada: {action_id}")
            return True
        
        return False
    
    async def resume_action(self, action_id: str) -> bool:
        """Retoma uma ação pausada"""
        if action_id in self.actions:
            action = self.actions[action_id]
            if action.status == ActionStatus.PAUSED:
                action.status = ActionStatus.PENDING
                action.updated_at = datetime.now(timezone.utc)
                
                await self.execute_action(action_id)
                return True
        
        return False
    
    async def shutdown(self):
        """Desliga o módulo de forma controlada"""
        self.logger.info("Iniciando shutdown do módulo autônomo...")
        
        # Sinalizar shutdown
        self.shutdown_event.set()
        self.is_running = False
        
        # Cancelar scheduler
        if self.scheduler_task:
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass
        
        # Cancelar tasks em execução
        for task_id, task in list(self.execution_tasks.items()):
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        # Limpar funções secundárias
        for function in self.secondary_functions.values():
            await function.cleanup()
        
        self.logger.info("Módulo autônomo desligado com sucesso")


# ============================================================================
# FÁBRICA DE MÓDULOS AUTÔNOMOS
# ============================================================================

class AutonomousModuleFactory:
    """Fábrica para criação de módulos autônomos"""
    
    @staticmethod
    def create_module(config: Dict[str, Any]) -> AutonomousModule:
        """Cria um novo módulo autônomo"""
        return AutonomousModule(config)
    
    @staticmethod
    def create_default_config() -> Dict[str, Any]:
        """Cria configuração padrão"""
        return {
            "health_check_interval": 60,
            "max_concurrent_actions": 10,
            "log_level": "INFO",
            "alert_channels": ["console"],
            "performance_tracking": True,
            "resource_monitoring": True,
            "auto_recovery": True,
            "default_timeout": 300,
            "default_retry_count": 3,
            "default_retry_delay": 60
        }


# ============================================================================
# EXEMPLO DE USO
# ============================================================================

async def example_usage():
    """Exemplo de uso do módulo autônomo"""
    print("Módulo Autônomo LEXTRADER-IAG 4.0 - Exemplo de Uso")
    print("=" * 60)
    
    # Criar configuração
    config = AutonomousModuleFactory.create_default_config()
    
    # Criar módulo
    module = AutonomousModuleFactory.create_module(config)
    
    try:
        # Inicializar módulo
        await module.initialize()
        
        print(f"\nMódulo inicializado com {len(module.actions)} ações")
        
        # Listar ações registradas
        actions = module.list_actions()
        print(f"\nAções registradas:")
        for action in actions[:3]:  # Mostrar primeiras 3
            print(f"  - {action['name']} ({action['type']}) - {action['status']}")
        
        if len(actions) > 3:
            print(f"  ... e mais {len(actions) - 3} ações")
        
        # Executar ação manualmente
        print("\nExecutando ação manual de análise de mercado...")
        result = await module.execute_manual_action(
            ActionType.MARKET_ANALYSIS,
            {"symbols": ["BTCUSDT", "ETHUSDT"]}
        )
        print(f"Resultado: {result}")
        
        # Obter saúde do módulo
        health = module.get_health()
        print(f"\nSaúde do módulo:")
        print(f"  Total de ações: {health.total_actions}")
        print(f"  Taxa de sucesso: {health.success_rate:.1%}")
        print(f"  Ações em execução: {health.running_actions}")
        
        # Aguardar execução de algumas ações
        print("\nAguardando execução de ações programadas...")
        await asyncio.sleep(10)
        
        # Gerar relatório de performance
        report = module.get_performance_report()
        print(f"\nRelatório de Performance:")
        print(f"  Uptime: {report['module_uptime']:.0f} segundos")
        print(f"  Total de ações executadas: {report['health_metrics']['total_actions']}")
        
        # Mostrar status de ações específicas
        print(f"\nStatus de ações específicas:")
        for action_id in list(module.actions.keys())[:2]:
            status = module.get_action_status(action_id)
            if status:
                print(f"  {status['name']}: {status['status']}")
        
        # Desligar módulo
        print("\nDesligando módulo...")
        
    finally:
        await module.shutdown()
    
    print("\nExemplo concluído com sucesso!")


if __name__ == "__main__":
    # Executar exemplo
    asyncio.run(example_usage())
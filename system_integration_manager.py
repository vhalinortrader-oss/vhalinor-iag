"""
╔═════════════════════════════════════════════════════════════════════════════╗
║                SISTEMA DE INTERAÇÃO ENTRE ARQUIVOS DA PASTA              ║
║                 Componente 16: Orquestrador Central de Integração           ║
╚═════════════════════════════════════════════════════════════════════════════╝
"""

import asyncio
import importlib
import inspect
import os
import sys
import threading
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
import yaml
import pickle
from collections import defaultdict, deque
import weakref
import gc

# Configuração de logging avançado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s - %(message)s',
    handlers=[
        logging.FileHandler('system_integration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('SystemIntegrationManager')

class ComponentType(Enum):
    """Tipos de componentes do sistema"""
    DATA_COLLECTION = "data_collection"
    DATA_PROCESSING = "data_processing"
    FEATURE_ENGINEERING = "feature_engineering"
    DEEP_LEARNING = "deep_learning"
    REINFORCEMENT_LEARNING = "reinforcement_learning"
    RISK_MANAGEMENT = "risk_management"
    VALIDATION = "validation"
    ADAPTATION = "adaptation"
    SIMULATION = "simulation"
    EXECUTION = "execution"
    MONITORING = "monitoring"
    GOVERNANCE = "governance"
    SECURITY = "security"
    INTEGRATION = "integration"

class ComponentStatus(Enum):
    """Status dos componentes"""
    INACTIVE = "inactive"
    INITIALIZING = "initializing"
    ACTIVE = "active"
    BUSY = "busy"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    STOPPING = "stopping"

class MessageType(Enum):
    """Tipos de mensagens entre componentes"""
    DATA = "data"
    COMMAND = "command"
    QUERY = "query"
    RESPONSE = "response"
    ERROR = "error"
    STATUS = "status"
    ALERT = "alert"
    CONFIG_UPDATE = "config_update"
    HEARTBEAT = "heartbeat"

class Priority(Enum):
    """Prioridades das mensagens"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5

@dataclass
class ComponentInfo:
    """Informações sobre um componente"""
    name: str
    component_type: ComponentType
    file_path: str
    class_name: str
    status: ComponentStatus
    last_heartbeat: datetime
    dependencies: List[str] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)
    error_count: int = 0
    last_error: Optional[str] = None
    startup_time: Optional[datetime] = None
    version: str = "1.0.0"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'component_type': self.component_type.value,
            'file_path': self.file_path,
            'class_name': self.class_name,
            'status': self.status.value,
            'last_heartbeat': self.last_heartbeat.isoformat(),
            'dependencies': self.dependencies,
            'dependents': self.dependents,
            'config': self.config,
            'metrics': self.metrics,
            'error_count': self.error_count,
            'last_error': self.last_error,
            'startup_time': self.startup_time.isoformat() if self.startup_time else None,
            'version': self.version
        }

@dataclass
class SystemMessage:
    """Mensagem do sistema"""
    id: str
    source: str
    destination: Union[str, List[str]]
    message_type: MessageType
    priority: Priority
    payload: Any
    timestamp: datetime = field(default_factory=datetime.now)
    ttl: Optional[int] = None
    requires_ack: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'source': self.source,
            'destination': self.destination,
            'message_type': self.message_type.value,
            'priority': self.priority.value,
            'payload': str(self.payload)[:200] + '...' if len(str(self.payload)) > 200 else self.payload,
            'timestamp': self.timestamp.isoformat(),
            'ttl': self.ttl,
            'requires_ack': self.requires_ack,
            'metadata': self.metadata
        }

@dataclass
class SystemMetrics:
    """Métricas do sistema"""
    total_components: int
    active_components: int
    error_components: int
    messages_processed: int
    messages_queued: int
    average_response_time: float
    system_uptime: float
    memory_usage_mb: float
    cpu_usage_percent: float
    disk_usage_gb: float
    last_update: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'total_components': self.total_components,
            'active_components': self.active_components,
            'error_components': self.error_components,
            'messages_processed': self.messages_processed,
            'messages_queued': self.messages_queued,
            'average_response_time': self.average_response_time,
            'system_uptime': self.system_uptime,
            'memory_usage_mb': self.memory_usage_mb,
            'cpu_usage_percent': self.cpu_usage_percent,
            'disk_usage_gb': self.disk_usage_gb,
            'last_update': self.last_update.isoformat()
        }

class ComponentLoader:
    """Carregador dinâmico de componentes"""
    
    def __init__(self, base_path: str = None):
        self.base_path = base_path or os.path.dirname(os.path.abspath(__file__))
        self.loaded_modules = {}
        self.component_instances = {}
        logger.info(f"🔧 ComponentLoader inicializado com base_path: {self.base_path}")
    
    def discover_components(self) -> List[str]:
        """Descobre todos os componentes Python na pasta"""
        components = []
        
        for file_path in Path(self.base_path).glob("*.py"):
            if file_path.name.startswith("__"):
                continue
            
            # Verifica se é um componente válido
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Procura por classes de componentes
                if any(keyword in content.lower() for keyword in 
                      ['class', 'def', 'component', 'system', 'manager']):
                    components.append(str(file_path))
                    
            except Exception as e:
                logger.warning(f"Erro ao ler arquivo {file_path}: {e}")
        
        logger.info(f"📁 Descobertos {len(components)} componentes")
        return components
    
    def load_component(self, file_path: str, class_name: str = None) -> Any:
        """Carrega um componente dinamicamente"""
        try:
            # Converte path para nome de módulo
            module_name = Path(file_path).stem
            
            # Carrega o módulo
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Encontra a classe principal se não especificada
            if class_name is None:
                class_name = self._find_main_class(module)
            
            if class_name and hasattr(module, class_name):
                component_class = getattr(module, class_name)
                instance = component_class()
                
                # Armazena referências
                self.loaded_modules[module_name] = module
                self.component_instances[module_name] = instance
                
                logger.info(f"✅ Componente {class_name} carregado de {file_path}")
                return instance
            else:
                raise ValueError(f"Classe {class_name} não encontrada em {file_path}")
                
        except Exception as e:
            logger.error(f"❌ Erro ao carregar componente {file_path}: {e}")
            raise
    
    def _find_main_class(self, module) -> Optional[str]:
        """Encontra a classe principal de um módulo"""
        for name, obj in inspect.getmembers(module, inspect.isclass):
            # Ignora classes importadas
            if obj.__module__ == module.__name__:
                # Procura por classes que parecem ser componentes principais
                if any(keyword in name.lower() for keyword in 
                      ['system', 'manager', 'engine', 'processor', 'agent', 'environment']):
                    return name
        
        # Se não encontrar, retorna a primeira classe do módulo
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if obj.__module__ == module.__name__:
                return name
        
        return None
    
    def unload_component(self, module_name: str):
        """Descarrega um componente"""
        if module_name in self.loaded_modules:
            del self.loaded_modules[module_name]
        
        if module_name in self.component_instances:
            del self.component_instances[module_name]
        
        # Força garbage collection
        gc.collect()
        
        logger.info(f"🗑️ Componente {module_name} descarregado")
    
    def get_component(self, module_name: str) -> Any:
        """Obtém instância de um componente"""
        return self.component_instances.get(module_name)
    
    def list_loaded_components(self) -> List[str]:
        """Lista componentes carregados"""
        return list(self.component_instances.keys())

class MessageRouter:
    """Roteador de mensagens entre componentes"""
    
    def __init__(self):
        self.message_queue = asyncio.Queue(maxsize=10000)
        self.subscribers = defaultdict(list)
        self.message_history = deque(maxlen=1000)
        self.routing_rules = {}
        self.message_stats = defaultdict(int)
        self.response_times = deque(maxlen=1000)
        
        logger.info("📨 MessageRouter inicializado")
    
    def subscribe(self, component_name: str, message_types: List[MessageType], 
                 callback: Callable):
        """Inscreve componente para receber mensagens"""
        for msg_type in message_types:
            self.subscribers[msg_type.value].append({
                'component': component_name,
                'callback': callback
            })
        
        logger.info(f"📧 Componente {component_name} inscrito para {[mt.value for mt in message_types]}")
    
    def unsubscribe(self, component_name: str):
        """Remove inscrição de componente"""
        for msg_type, subscribers in self.subscribers.items():
            self.subscribers[msg_type] = [
                sub for sub in subscribers 
                if sub['component'] != component_name
            ]
        
        logger.info(f"📤 Componente {component_name} removido das inscrições")
    
    async def send_message(self, message: SystemMessage):
        """Envia mensagem para roteamento"""
        try:
            # Valida mensagem
            if self._validate_message(message):
                await self.message_queue.put(message)
                self.message_stats['sent'] += 1
                
                logger.debug(f"📤 Mensagem {message.id} enfileirada: {message.source} -> {message.destination}")
                
                return True
            else:
                logger.warning(f"⚠️ Mensagem inválida: {message.id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao enviar mensagem {message.id}: {e}")
            return False
    
    async def process_messages(self):
        """Processa fila de mensagens"""
        while True:
            try:
                # Obtém mensagem com timeout
                message = await asyncio.wait_for(
                    self.message_queue.get(), 
                    timeout=1.0
                )
                
                start_time = time.time()
                
                # Processa mensagem
                await self._route_message(message)
                
                # Registra tempo de resposta
                response_time = time.time() - start_time
                self.response_times.append(response_time)
                
                # Atualiza estatísticas
                self.message_stats['processed'] += 1
                self.message_history.append(message)
                
                # Verifica TTL
                if message.ttl and (datetime.now() - message.timestamp).total_seconds() > message.ttl:
                    logger.debug(f"⏰ Mensagem {message.id} expirada")
                    continue
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"❌ Erro ao processar mensagem: {e}")
    
    async def _route_message(self, message: SystemMessage):
        """Roteia mensagem para destinatários"""
        destinations = message.destination if isinstance(message.destination, list) else [message.destination]
        
        for destination in destinations:
            if destination == 'all':
                # Broadcast para todos os inscritos
                for subscriber in self.subscribers.get(message.message_type.value, []):
                    await self._deliver_message(subscriber, message)
            else:
                # Mensagem direcionada
                delivered = False
                for subscriber in self.subscribers.get(message.message_type.value, []):
                    if subscriber['component'] == destination:
                        await self._deliver_message(subscriber, message)
                        delivered = True
                        break
                
                if not delivered:
                    logger.warning(f"⚠️ Destinatário {destination} não encontrado para mensagem {message.id}")
    
    async def _deliver_message(self, subscriber: Dict, message: SystemMessage):
        """Entrega mensagem para um assinante"""
        try:
            callback = subscriber['callback']
            
            if asyncio.iscoroutinefunction(callback):
                await callback(message)
            else:
                # Executa em thread pool para não bloquear
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, callback, message)
                
        except Exception as e:
            logger.error(f"❌ Erro ao entregar mensagem para {subscriber['component']}: {e}")
            
            # Envia mensagem de erro
            error_message = SystemMessage(
                id=f"error_{message.id}",
                source="message_router",
                destination=message.source,
                message_type=MessageType.ERROR,
                priority=Priority.HIGH,
                payload=str(e),
                metadata={'original_message_id': message.id}
            )
            
            await self.message_queue.put(error_message)
    
    def _validate_message(self, message: SystemMessage) -> bool:
        """Valida mensagem"""
        if not message.id or not message.source or not message.destination:
            return False
        
        if not isinstance(message.message_type, MessageType):
            return False
        
        if not isinstance(message.priority, Priority):
            return False
        
        return True
    
    def get_message_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de mensagens"""
        avg_response_time = np.mean(self.response_times) if self.response_times else 0
        
        return {
            'messages_sent': self.message_stats.get('sent', 0),
            'messages_processed': self.message_stats.get('processed', 0),
            'messages_queued': self.message_queue.qsize(),
            'average_response_time_ms': avg_response_time * 1000,
            'total_subscribers': sum(len(subs) for subs in self.subscribers.values()),
            'message_types': list(self.subscribers.keys())
        }

class SystemOrchestrator:
    """Orquestrador central do sistema"""
    
    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.component_loader = ComponentLoader()
        self.message_router = MessageRouter()
        
        # Registro de componentes
        self.components = {}
        self.component_dependencies = {}
        
        # Sistema em execução
        self.running = False
        self.startup_time = datetime.now()
        
        # Métricas
        self.metrics = SystemMetrics(
            total_components=0,
            active_components=0,
            error_components=0,
            messages_processed=0,
            messages_queued=0,
            average_response_time=0.0,
            system_uptime=0.0,
            memory_usage_mb=0.0,
            cpu_usage_percent=0.0,
            disk_usage_gb=0.0
        )
        
        # Tasks em execução
        self.background_tasks = []
        
        logger.info("🎼 SystemOrchestrator inicializado")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Carrega configuração do sistema"""
        default_config = {
            'components': {
                'market_data_infrastructure': {
                    'file': 'market_data_infrastructure.py',
                    'class': 'MarketDataCollector',
                    'type': 'data_collection',
                    'enabled': True,
                    'dependencies': []
                },
                'data_preprocessing_system': {
                    'file': 'data_preprocessing_system.py',
                    'class': 'DataPreprocessingPipeline',
                    'type': 'data_processing',
                    'enabled': True,
                    'dependencies': ['market_data_infrastructure']
                },
                'financial_feature_engineering': {
                    'file': 'financial_feature_engineering.py',
                    'class': 'FeatureEngineeringPipeline',
                    'type': 'feature_engineering',
                    'enabled': True,
                    'dependencies': ['data_preprocessing_system']
                },
                'temporal_deep_learning': {
                    'file': 'temporal_deep_learning.py',
                    'class': 'TemporalDeepLearningPipeline',
                    'type': 'deep_learning',
                    'enabled': True,
                    'dependencies': ['financial_feature_engineering']
                },
                'reinforcement_learning_environment': {
                    'file': 'reinforcement_learning_environment.py',
                    'class': 'TradingEnvironment',
                    'type': 'reinforcement_learning',
                    'enabled': True,
                    'dependencies': ['temporal_deep_learning']
                },
                'rl_algorithms_financial': {
                    'file': 'rl_algorithms_financial.py',
                    'class': 'DQNAgent',
                    'type': 'reinforcement_learning',
                    'enabled': True,
                    'dependencies': ['reinforcement_learning_environment']
                },
                'risk_management_system': {
                    'file': 'risk_management_system.py',
                    'class': 'RiskManagementSystem',
                    'type': 'risk_management',
                    'enabled': True,
                    'dependencies': ['reinforcement_learning_environment']
                }
            },
            'system': {
                'heartbeat_interval': 30,
                'health_check_interval': 60,
                'metrics_collection_interval': 30,
                'auto_restart_failed': True,
                'max_restart_attempts': 3,
                'log_level': 'INFO'
            },
            'performance': {
                'max_concurrent_tasks': 10,
                'message_queue_size': 10000,
                'component_timeout': 300,
                'memory_threshold_mb': 2048,
                'cpu_threshold_percent': 80
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = yaml.safe_load(f)
                
                # Mescla configurações
                for key, value in user_config.items():
                    if key in default_config:
                        if isinstance(default_config[key], dict) and isinstance(value, dict):
                            default_config[key].update(value)
                        else:
                            default_config[key] = value
                    else:
                        default_config[key] = value
                        
            except Exception as e:
                logger.warning(f"⚠️ Erro ao carregar configuração: {e}. Usando padrão.")
        
        return default_config
    
    async def start(self):
        """Inicia o sistema"""
        if self.running:
            logger.warning("⚠️ Sistema já está em execução")
            return
        
        logger.info("🚀 Iniciando Sistema de IA Financeira Autônoma")
        self.running = True
        self.startup_time = datetime.now()
        
        try:
            # Inicia roteador de mensagens
            router_task = asyncio.create_task(self.message_router.process_messages())
            self.background_tasks.append(router_task)
            
            # Carrega componentes
            await self._load_components()
            
            # Inicia monitoramento
            monitor_task = asyncio.create_task(self._system_monitor())
            self.background_tasks.append(monitor_task)
            
            # Inicia coletor de métricas
            metrics_task = asyncio.create_task(self._metrics_collector())
            self.background_tasks.append(metrics_task)
            
            # Inicia heartbeat
            heartbeat_task = asyncio.create_task(self._heartbeat_manager())
            self.background_tasks.append(heartbeat_task)
            
            logger.info("✅ Sistema iniciado com sucesso")
            
            # Aguarda tarefas em background
            await asyncio.gather(*self.background_tasks)
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar sistema: {e}")
            await self.stop()
    
    async def stop(self):
        """Para o sistema"""
        if not self.running:
            return
        
        logger.info("🛑 Parando Sistema de IA Financeira Autônoma")
        self.running = False
        
        # Cancela tarefas em background
        for task in self.background_tasks:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        # Para componentes
        await self._stop_components()
        
        # Salva estado final
        await self._save_system_state()
        
        logger.info("✅ Sistema parado com sucesso")
    
    async def _load_components(self):
        """Carrega todos os componentes configurados"""
        components_config = self.config.get('components', {})
        
        # Descobre componentes disponíveis
        available_files = self.component_loader.discover_components()
        
        for component_name, component_config in components_config.items():
            if not component_config.get('enabled', True):
                logger.info(f"⏭️ Componente {component_name} desabilitado")
                continue
            
            try:
                # Verifica se arquivo existe
                file_path = component_config['file']
                if not any(file_path in f for f in available_files):
                    logger.warning(f"⚠️ Arquivo do componente {component_name} não encontrado: {file_path}")
                    continue
                
                # Carrega componente
                instance = self.component_loader.load_component(
                    os.path.join(self.component_loader.base_path, file_path),
                    component_config.get('class')
                )
                
                # Registra componente
                component_info = ComponentInfo(
                    name=component_name,
                    component_type=ComponentType(component_config['type']),
                    file_path=file_path,
                    class_name=component_config['class'],
                    status=ComponentStatus.INITIALIZING,
                    last_heartbeat=datetime.now(),
                    dependencies=component_config.get('dependencies', []),
                    config=component_config
                )
                
                self.components[component_name] = component_info
                
                # Inscreve para mensagens
                await self._subscribe_component(component_name, instance)
                
                # Inicializa componente se tiver método start
                if hasattr(instance, 'start') and asyncio.iscoroutinefunction(instance.start):
                    await instance.start()
                elif hasattr(instance, 'start'):
                    instance.start()
                
                component_info.status = ComponentStatus.ACTIVE
                component_info.startup_time = datetime.now()
                
                logger.info(f"✅ Componente {component_name} carregado e iniciado")
                
            except Exception as e:
                logger.error(f"❌ Erro ao carregar componente {component_name}: {e}")
                
                if component_name in self.components:
                    self.components[component_name].status = ComponentStatus.ERROR
                    self.components[component_name].last_error = str(e)
        
        # Atualiza métricas
        self._update_metrics()
        
        logger.info(f"📊 {len(self.components)} componentes carregados")
    
    async def _subscribe_component(self, component_name: str, instance: Any):
        """Inscreve componente para receber mensagens"""
        # Determina tipos de mensagem baseado no tipo de componente
        component_info = self.components.get(component_name)
        if not component_info:
            return
        
        message_types = []
        
        # Todos os componentes recebem status e heartbeat
        message_types.extend([MessageType.STATUS, MessageType.HEARTBEAT])
        
        # Tipos específicos por componente
        if component_info.component_type == ComponentType.DATA_COLLECTION:
            message_types.extend([MessageType.DATA, MessageType.COMMAND])
        elif component_info.component_type == ComponentType.DATA_PROCESSING:
            message_types.extend([MessageType.DATA, MessageType.COMMAND])
        elif component_info.component_type == ComponentType.FEATURE_ENGINEERING:
            message_types.extend([MessageType.DATA, MessageType.COMMAND])
        elif component_info.component_type == ComponentType.DEEP_LEARNING:
            message_types.extend([MessageType.DATA, MessageType.COMMAND, MessageType.QUERY])
        elif component_info.component_type == ComponentType.REINFORCEMENT_LEARNING:
            message_types.extend([MessageType.DATA, MessageType.COMMAND, MessageType.QUERY])
        elif component_info.component_type == ComponentType.RISK_MANAGEMENT:
            message_types.extend([MessageType.DATA, MessageType.ALERT, MessageType.COMMAND])
        
        # Cria callback
        async def message_callback(message: SystemMessage):
            try:
                # Verifica se componente tem método para receber mensagens
                if hasattr(instance, 'receive_message'):
                    if asyncio.iscoroutinefunction(instance.receive_message):
                        await instance.receive_message(message)
                    else:
                        instance.receive_message(message)
                else:
                    # Método genérico para processar mensagem
                    await self._process_component_message(component_name, instance, message)
                    
            except Exception as e:
                logger.error(f"❌ Erro ao processar mensagem em {component_name}: {e}")
                
                # Atualiza erro no componente
                if component_name in self.components:
                    self.components[component_name].error_count += 1
                    self.components[component_name].last_error = str(e)
        
        # Inscreve no roteador
        self.message_router.subscribe(component_name, message_types, message_callback)
    
    async def _process_component_message(self, component_name: str, instance: Any, 
                                       message: SystemMessage):
        """Processa mensagem genérica para componente"""
        # Implementação padrão - pode ser sobrescrita por componentes específicos
        if message.message_type == MessageType.COMMAND:
            logger.info(f"🎯 Comando recebido por {component_name}: {message.payload}")
        elif message.message_type == MessageType.DATA:
            logger.debug(f"📊 Dados recebidos por {component_name}")
        elif message.message_type == MessageType.QUERY:
            logger.debug(f"❓ Query recebida por {component_name}")
    
    async def _stop_components(self):
        """Para todos os componentes"""
        for component_name, component_info in self.components.items():
            try:
                instance = self.component_loader.get_component(
                    Path(component_info.file_path).stem
                )
                
                if instance and hasattr(instance, 'stop'):
                    if asyncio.iscoroutinefunction(instance.stop):
                        await instance.stop()
                    else:
                        instance.stop()
                
                component_info.status = ComponentStatus.INACTIVE
                logger.info(f"🛑 Componente {component_name} parado")
                
            except Exception as e:
                logger.error(f"❌ Erro ao parar componente {component_name}: {e}")
    
    async def _system_monitor(self):
        """Monitoramento geral do sistema"""
        while self.running:
            try:
                # Verifica saúde dos componentes
                await self._check_components_health()
                
                # Verifica uso de recursos
                await self._check_system_resources()
                
                # Aguarda próximo ciclo
                await asyncio.sleep(
                    self.config['system']['health_check_interval']
                )
                
            except Exception as e:
                logger.error(f"❌ Erro no monitoramento do sistema: {e}")
                await asyncio.sleep(10)
    
    async def _check_components_health(self):
        """Verifica saúde dos componentes"""
        current_time = datetime.now()
        
        for component_name, component_info in self.components.items():
            # Verifica heartbeat
            time_since_heartbeat = (current_time - component_info.last_heartbeat).total_seconds()
            heartbeat_timeout = self.config['system']['heartbeat_interval'] * 3
            
            if time_since_heartbeat > heartbeat_timeout:
                if component_info.status == ComponentStatus.ACTIVE:
                    logger.warning(f"⚠️ Componente {component_name} sem heartbeat: {time_since_heartbeat:.1f}s")
                    component_info.status = ComponentStatus.ERROR
                    component_info.last_error = f"Heartbeat timeout: {time_since_heartbeat:.1f}s"
            
            # Verifica se precisa reiniciar
            if (component_info.status == ComponentStatus.ERROR and 
                self.config['system']['auto_restart_failed'] and
                component_info.error_count < self.config['system']['max_restart_attempts']):
                
                logger.info(f"🔄 Tentando reiniciar componente {component_name}")
                await self._restart_component(component_name)
    
    async def _check_system_resources(self):
        """Verifica uso de recursos do sistema"""
        try:
            import psutil
            
            # Memória
            memory = psutil.virtual_memory()
            self.metrics.memory_usage_mb = memory.used / 1024 / 1024
            
            # CPU
            self.metrics.cpu_usage_percent = psutil.cpu_percent(interval=1)
            
            # Disco
            disk = psutil.disk_usage('.')
            self.metrics.disk_usage_gb = disk.used / 1024 / 1024 / 1024
            
            # Verifica thresholds
            if self.metrics.memory_usage_mb > self.config['performance']['memory_threshold_mb']:
                logger.warning(f"⚠️ Alto uso de memória: {self.metrics.memory_usage_mb:.1f} MB")
            
            if self.metrics.cpu_usage_percent > self.config['performance']['cpu_threshold_percent']:
                logger.warning(f"⚠️ Alto uso de CPU: {self.metrics.cpu_usage_percent:.1f}%")
                
        except ImportError:
            logger.debug("psutil não disponível para monitoramento de recursos")
        except Exception as e:
            logger.error(f"❌ Erro ao verificar recursos: {e}")
    
    async def _metrics_collector(self):
        """Coletor de métricas do sistema"""
        while self.running:
            try:
                self._update_metrics()
                
                # Salva métricas
                await self._save_metrics()
                
                # Aguarda próximo ciclo
                await asyncio.sleep(
                    self.config['system']['metrics_collection_interval']
                )
                
            except Exception as e:
                logger.error(f"❌ Erro no coletor de métricas: {e}")
                await asyncio.sleep(30)
    
    def _update_metrics(self):
        """Atualiza métricas do sistema"""
        self.metrics.total_components = len(self.components)
        self.metrics.active_components = len([
            c for c in self.components.values() 
            if c.status == ComponentStatus.ACTIVE
        ])
        self.metrics.error_components = len([
            c for c in self.components.values() 
            if c.status == ComponentStatus.ERROR
        ])
        
        # Métricas de mensagens
        message_stats = self.message_router.get_message_stats()
        self.metrics.messages_processed = message_stats['messages_processed']
        self.metrics.messages_queued = message_stats['messages_queued']
        self.metrics.average_response_time = message_stats['average_response_time_ms'] / 1000
        
        # Uptime
        self.metrics.system_uptime = (datetime.now() - self.startup_time).total_seconds()
        self.metrics.last_update = datetime.now()
    
    async def _heartbeat_manager(self):
        """Gerenciador de heartbeat"""
        while self.running:
            try:
                # Envia heartbeat para todos os componentes
                heartbeat_message = SystemMessage(
                    id=f"heartbeat_{int(time.time())}",
                    source="system_orchestrator",
                    destination="all",
                    message_type=MessageType.HEARTBEAT,
                    priority=Priority.LOW,
                    payload={'timestamp': datetime.now().isoformat()}
                )
                
                await self.message_router.send_message(heartbeat_message)
                
                # Aguarda próximo ciclo
                await asyncio.sleep(
                    self.config['system']['heartbeat_interval']
                )
                
            except Exception as e:
                logger.error(f"❌ Erro no heartbeat manager: {e}")
                await asyncio.sleep(30)
    
    async def _restart_component(self, component_name: str):
        """Reinicia um componente"""
        try:
            component_info = self.components[component_name]
            
            # Para componente
            await self._stop_single_component(component_name)
            
            # Pequena pausa
            await asyncio.sleep(2)
            
            # Recarrega componente
            await self._load_single_component(component_name)
            
            logger.info(f"✅ Componente {component_name} reiniciado com sucesso")
            
        except Exception as e:
            logger.error(f"❌ Erro ao reiniciar componente {component_name}: {e}")
            component_info.error_count += 1
            component_info.last_error = str(e)
    
    async def _stop_single_component(self, component_name: str):
        """Para um componente específico"""
        component_info = self.components.get(component_name)
        if not component_info:
            return
        
        try:
            instance = self.component_loader.get_component(
                Path(component_info.file_path).stem
            )
            
            if instance and hasattr(instance, 'stop'):
                if asyncio.iscoroutinefunction(instance.stop):
                    await instance.stop()
                else:
                    instance.stop()
            
            component_info.status = ComponentStatus.STOPPING
            
        except Exception as e:
            logger.error(f"❌ Erro ao parar componente {component_name}: {e}")
    
    async def _load_single_component(self, component_name: str):
        """Carrega um componente específico"""
        component_config = self.config['components'].get(component_name)
        if not component_config:
            return
        
        try:
            # Carrega componente
            instance = self.component_loader.load_component(
                os.path.join(self.component_loader.base_path, component_config['file']),
                component_config.get('class')
            )
            
            # Atualiza informações
            component_info = self.components[component_name]
            component_info.status = ComponentStatus.INITIALIZING
            component_info.last_heartbeat = datetime.now()
            
            # Inscreve para mensagens
            await self._subscribe_component(component_name, instance)
            
            # Inicializa componente
            if hasattr(instance, 'start') and asyncio.iscoroutinefunction(instance.start):
                await instance.start()
            elif hasattr(instance, 'start'):
                instance.start()
            
            component_info.status = ComponentStatus.ACTIVE
            component_info.startup_time = datetime.now()
            
        except Exception as e:
            logger.error(f"❌ Erro ao recarregar componente {component_name}: {e}")
            if component_name in self.components:
                self.components[component_name].status = ComponentStatus.ERROR
                self.components[component_name].last_error = str(e)
    
    async def _save_metrics(self):
        """Salva métricas do sistema"""
        try:
            metrics_file = 'system_metrics.json'
            
            with open(metrics_file, 'w') as f:
                json.dump(self.metrics.to_dict(), f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"❌ Erro ao salvar métricas: {e}")
    
    async def _save_system_state(self):
        """Salva estado completo do sistema"""
        try:
            state_file = 'system_state.json'
            
            system_state = {
                'timestamp': datetime.now().isoformat(),
                'uptime': self.metrics.system_uptime,
                'components': {
                    name: info.to_dict() 
                    for name, info in self.components.items()
                },
                'metrics': self.metrics.to_dict(),
                'message_stats': self.message_router.get_message_stats()
            }
            
            with open(state_file, 'w') as f:
                json.dump(system_state, f, indent=2, default=str)
                
            logger.info(f"💾 Estado do sistema salvo em {state_file}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar estado do sistema: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Retorna status completo do sistema"""
        return {
            'running': self.running,
            'uptime_seconds': self.metrics.system_uptime,
            'components': {
                name: info.to_dict() 
                for name, info in self.components.items()
            },
            'metrics': self.metrics.to_dict(),
            'message_stats': self.message_router.get_message_stats()
        }
    
    async def send_command(self, target: str, command: str, 
                         parameters: Dict[str, Any] = None) -> bool:
        """Envia comando para componente específico"""
        message = SystemMessage(
            id=f"cmd_{int(time.time())}",
            source="system_orchestrator",
            destination=target,
            message_type=MessageType.COMMAND,
            priority=Priority.NORMAL,
            payload={
                'command': command,
                'parameters': parameters or {}
            }
        )
        
        return await self.message_router.send_message(message)
    
    async def broadcast_alert(self, alert_message: str, priority: Priority = Priority.HIGH):
        """Envia alerta para todos os componentes"""
        message = SystemMessage(
            id=f"alert_{int(time.time())}",
            source="system_orchestrator",
            destination="all",
            message_type=MessageType.ALERT,
            priority=priority,
            payload={'alert': alert_message}
        )
        
        return await self.message_router.send_message(message)

# Ponto de entrada principal
if __name__ == "__main__":
    async def main():
        """Função principal do sistema"""
        print("🚀 Iniciando Sistema de IA Financeira Autônoma Vhalinor")
        print("=" * 60)
        
        # Cria orquestrador
        orchestrator = SystemOrchestrator()
        
        try:
            # Inicia sistema
            await orchestrator.start()
            
        except KeyboardInterrupt:
            print("\n🛑 Interrupção do usuário detectada")
            await orchestrator.stop()
        except Exception as e:
            print(f"\n❌ Erro fatal: {e}")
            await orchestrator.stop()
        
        print("\n✅ Sistema finalizado")
    
    # Executa sistema
    asyncio.run(main())

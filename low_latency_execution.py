"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                MÓDULO DE EXECUÇÃO DE ORDENS DE BAIXA LATÊNCIA           ║
║                 Componente 11: Sistema de Execução HFT                    ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

import asyncio
import numpy as np
import pandas as pd
import socket
import ssl
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import threading
from concurrent.futures import ThreadPoolExecutor
import queue
import hashlib
import hmac
from collections import deque, defaultdict
import weakref

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('LowLatencyExecution')

class ConnectionType(Enum):
    """Tipos de conexão"""
    TCP = "tcp"
    UDP = "udp"
    WEBSOCKET = "websocket"
    FIX = "fix"
    BINARY = "binary"

class OrderType(Enum):
    """Tipos de ordens"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    IOC = "ioc"  # Immediate or Cancel
    FOK = "fok"  # Fill or Kill
    AON = "aon"  # All or None

class ExecutionVenue(Enum):
    """Venues de execução"""
    NYSE = "nyse"
    NASDAQ = "nasdaq"
    CME = "cme"
    ICE = "ice"
    BATS = "bats"
    DIRECT_EDGE = "direct_edge"
    DARK_POOL = "dark_pool"
    CRYPTO = "crypto"

class LatencyTier(Enum):
    """Níveis de latência"""
    ULTRA_LOW = "ultra_low"      # < 100μs
    LOW = "low"                  # 100μs - 1ms
    MEDIUM = "medium"              # 1ms - 10ms
    HIGH = "high"                 # > 10ms

@dataclass
class ExecutionRequest:
    """Requisição de execução"""
    id: str
    symbol: str
    side: str  # buy/sell
    order_type: OrderType
    quantity: float
    price: Optional[float]
    time_in_force: str
    account: str
    venue: ExecutionVenue
    timestamp: datetime
    priority: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'symbol': self.symbol,
            'side': self.side,
            'order_type': self.order_type.value,
            'quantity': self.quantity,
            'price': self.price,
            'time_in_force': self.time_in_force,
            'account': self.account,
            'venue': self.venue.value,
            'timestamp': self.timestamp.isoformat(),
            'priority': self.priority,
            'metadata': self.metadata
        }

@dataclass
class ExecutionResponse:
    """Resposta de execução"""
    request_id: str
    order_id: str
    status: str
    filled_quantity: float
    remaining_quantity: float
    average_price: float
    execution_time_ns: int
    venue_timestamp: datetime
    exchange_order_id: str
    fills: List[Dict[str, Any]] = field(default_factory=list)
    error_message: Optional[str] = None
    latency_tier: LatencyTier = LatencyTier.MEDIUM
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'request_id': self.request_id,
            'order_id': self.order_id,
            'status': self.status,
            'filled_quantity': self.filled_quantity,
            'remaining_quantity': self.remaining_quantity,
            'average_price': self.average_price,
            'execution_time_ns': self.execution_time_ns,
            'venue_timestamp': self.venue_timestamp.isoformat(),
            'exchange_order_id': self.exchange_order_id,
            'fills': self.fills,
            'error_message': self.error_message,
            'latency_tier': self.latency_tier.value
        }

@dataclass
class LatencyMetrics:
    """Métricas de latência"""
    timestamp: datetime
    venue: ExecutionVenue
    round_trip_ns: int
    order_ack_ns: int
    first_fill_ns: int
    complete_fill_ns: int
    market_data_latency_ns: int
    network_jitter_ns: float
    packet_loss_rate: float
    queue_depth: int
    cpu_usage_percent: float
    memory_usage_mb: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'venue': self.venue.value,
            'round_trip_ns': self.round_trip_ns,
            'order_ack_ns': self.order_ack_ns,
            'first_fill_ns': self.first_fill_ns,
            'complete_fill_ns': self.complete_fill_ns,
            'market_data_latency_ns': self.market_data_latency_ns,
            'network_jitter_ns': self.network_jitter_ns,
            'packet_loss_rate': self.packet_loss_rate,
            'queue_depth': self.queue_depth,
            'cpu_usage_percent': self.cpu_usage_percent,
            'memory_usage_mb': self.memory_usage_mb
        }

class LowLatencyConnection:
    """Conexão de baixa latência"""
    
    def __init__(self, venue: ExecutionVenue, config: Dict[str, Any] = None):
        self.venue = venue
        self.config = config or {}
        self.connection_type = ConnectionType(self.config.get('connection_type', 'tcp'))
        self.host = self.config.get('host', 'localhost')
        self.port = self.config.get('port', 8080)
        self.socket = None
        self.ssl_context = None
        self.is_connected = False
        self.last_ping_time = 0
        self.sequence_number = 0
        
        # Buffers para performance
        self.send_buffer = bytearray()
        self.recv_buffer = bytearray(65536)  # 64KB buffer
        
        # Métricas
        self.latency_history = deque(maxlen=1000)
        self.connection_attempts = 0
        self.successful_connections = 0
        
        logger.info(f"🔌 LowLatencyConnection inicializado para {venue.value}")
    
    async def connect(self) -> bool:
        """Conecta ao venue com otimização de latência"""
        try:
            # Cria socket otimizado
            self.socket = socket.socket(
                socket.AF_INET if self.connection_type == ConnectionType.TCP else socket.AF_INET,
                socket.SOCK_STREAM if self.connection_type == ConnectionType.TCP else socket.SOCK_DGRAM
            )
            
            # Otimizações de TCP para baixa latência
            if self.connection_type == ConnectionType.TCP:
                self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Configura SSL se necessário
            if self.config.get('use_ssl', False):
                self.ssl_context = ssl.create_default_context()
                self.ssl_context.check_hostname = False
                self.ssl_context.verify_mode = ssl.CERT_NONE
            
            # Conecta de forma assíncrona
            loop = asyncio.get_event_loop()
            
            if self.ssl_context:
                await loop.sock_connect(self.socket, (self.host, self.port))
                self.socket = self.ssl_context.wrap_socket(self.socket, server_hostname=self.host)
            else:
                await loop.sock_connect(self.socket, (self.host, self.port))
            
            self.is_connected = True
            self.successful_connections += 1
            
            # Inicia heartbeat
            asyncio.create_task(self._heartbeat_loop())
            
            logger.info(f"✅ Conectado a {self.venue.value} via {self.connection_type.value}")
            return True
            
        except Exception as e:
            self.connection_attempts += 1
            logger.error(f"❌ Erro ao conectar a {self.venue.value}: {e}")
            return False
    
    async def disconnect(self):
        """Desconecta do venue"""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        
        self.is_connected = False
        logger.info(f"🔌 Desconectado de {self.venue.value}")
    
    async def send_order(self, order: ExecutionRequest) -> bool:
        """Envia ordem com latência mínima"""
        if not self.is_connected:
            return False
        
        try:
            # Serializa ordem
            order_data = self._serialize_order(order)
            
            # Adiciona timestamp e sequence number
            timestamp_ns = time.time_ns()
            self.sequence_number += 1
            
            # Cria pacote otimizado
            packet = self._create_packet(
                message_type='ORDER',
                sequence=self.sequence_number,
                timestamp=timestamp_ns,
                data=order_data
            )
            
            # Envia de forma síncrona para máxima velocidade
            loop = asyncio.get_event_loop()
            await loop.sock_sendall(self.socket, packet)
            
            # Registra timestamp de envio
            order.metadata['sent_timestamp_ns'] = timestamp_ns
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao enviar ordem {order.id}: {e}")
            return False
    
    async def receive_response(self, timeout_ms: int = 100) -> Optional[ExecutionResponse]:
        """Recebe resposta com timeout otimizado"""
        if not self.is_connected:
            return None
        
        try:
            loop = asyncio.get_event_loop()
            
            # Usa select para polling eficiente
            readable, _, _ = await loop.sock_wait_for(
                [self.socket], 
                timeout=timeout_ms / 1000.0
            )
            
            if not readable:
                return None
            
            # Recebe dados
            data = await loop.sock_recv(self.socket, 4096)
            
            if not data:
                return None
            
            # Desserializa resposta
            response = self._deserialize_response(data)
            
            # Calcula latência
            if response and 'sent_timestamp_ns' in response.metadata:
                response.execution_time_ns = time.time_ns() - response.metadata['sent_timestamp_ns']
                response.latency_tier = self._classify_latency(response.execution_time_ns)
            
            return response
            
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            logger.error(f"❌ Erro ao receber resposta: {e}")
            return None
    
    def _serialize_order(self, order: ExecutionRequest) -> bytes:
        """Serializa ordem para formato binário otimizado"""
        # Formato binário customizado para máxima eficiência
        # Header: magic(4) + version(2) + length(4) + timestamp(8)
        header = b'HFT\x01'
        
        # Converte ordem para bytes
        order_dict = order.to_dict()
        order_json = json.dumps(order_dict, separators=(',', ':')).encode('utf-8')
        
        length = len(order_json)
        timestamp = int(time.time_ns())
        
        # Monta pacote
        packet = header + length.to_bytes(4, 'big') + timestamp.to_bytes(8, 'big') + order_json
        
        return packet
    
    def _deserialize_response(self, data: bytes) -> ExecutionResponse:
        """Desserializa resposta do formato binário"""
        try:
            # Verifica header
            if len(data) < 18:  # magic + version + length + timestamp
                return None
            
            magic = data[:4]
            if magic != b'HFT\x01':
                return None
            
            # Extrai informações
            length = int.from_bytes(data[6:10], 'big')
            timestamp = int.from_bytes(data[10:18], 'big')
            
            if len(data) < 18 + length:
                return None
            
            # Extrai JSON
            response_json = data[18:18+length].decode('utf-8')
            response_dict = json.loads(response_json)
            
            # Cria objeto de resposta
            response = ExecutionResponse(
                request_id=response_dict.get('request_id', ''),
                order_id=response_dict.get('order_id', ''),
                status=response_dict.get('status', 'UNKNOWN'),
                filled_quantity=response_dict.get('filled_quantity', 0.0),
                remaining_quantity=response_dict.get('remaining_quantity', 0.0),
                average_price=response_dict.get('average_price', 0.0),
                execution_time_ns=response_dict.get('execution_time_ns', 0),
                venue_timestamp=datetime.fromisoformat(response_dict.get('venue_timestamp', '')),
                exchange_order_id=response_dict.get('exchange_order_id', ''),
                fills=response_dict.get('fills', []),
                error_message=response_dict.get('error_message'),
                metadata=response_dict.get('metadata', {})
            )
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Erro ao desserializar resposta: {e}")
            return None
    
    def _create_packet(self, message_type: str, sequence: int, 
                      timestamp: int, data: bytes) -> bytes:
        """Cria pacote otimizado"""
        # Header simplificado para máxima velocidade
        packet = bytearray()
        
        # Magic e tipo
        packet.extend(b'HFT\x01')
        packet.extend(message_type.encode('ascii')[:4].ljust(4, b'\x00'))
        
        # Sequence e timestamp
        packet.extend(sequence.to_bytes(4, 'big'))
        packet.extend(timestamp.to_bytes(8, 'big'))
        
        # Data
        packet.extend(len(data).to_bytes(4, 'big'))
        packet.extend(data)
        
        return bytes(packet)
    
    def _classify_latency(self, latency_ns: int) -> LatencyTier:
        """Classifica latência em tiers"""
        if latency_ns < 100000:  # < 100μs
            return LatencyTier.ULTRA_LOW
        elif latency_ns < 1000000:  # < 1ms
            return LatencyTier.LOW
        elif latency_ns < 10000000:  # < 10ms
            return LatencyTier.MEDIUM
        else:
            return LatencyTier.HIGH
    
    async def _heartbeat_loop(self):
        """Loop de heartbeat para manter conexão ativa"""
        while self.is_connected:
            try:
                # Envia heartbeat a cada 30 segundos
                await asyncio.sleep(30)
                
                heartbeat_packet = self._create_packet(
                    message_type='PING',
                    sequence=self.sequence_number,
                    timestamp=int(time.time_ns()),
                    data=b'PING'
                )
                
                loop = asyncio.get_event_loop()
                await loop.sock_sendall(self.socket, heartbeat_packet)
                
                self.last_ping_time = time.time()
                
            except Exception as e:
                logger.error(f"❌ Erro no heartbeat: {e}")
                break

class OrderRouter:
    """Roteador inteligente de ordens"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.connections = {}
        self.venue_preferences = {}
        self.load_balancer = LoadBalancer()
        self.order_queue = asyncio.Queue(maxsize=10000)
        self.response_handlers = {}
        self.metrics_collector = LatencyMetricsCollector()
        
        # Thread de processamento
        self.processing_active = False
        self.processing_thread = None
        
        logger.info("🚀 OrderRouter inicializado")
    
    async def initialize(self, venues: List[ExecutionVenue]):
        """Inicializa conexões com múltiplos venues"""
        for venue in venues:
            venue_config = self.config.get('venues', {}).get(venue.value, {})
            
            connection = LowLatencyConnection(venue, venue_config)
            success = await connection.connect()
            
            if success:
                self.connections[venue] = connection
                logger.info(f"✅ Conectado ao venue {venue.value}")
            else:
                logger.warning(f"⚠️ Falha ao conectar ao venue {venue.value}")
        
        # Inicia processamento de ordens
        self.processing_active = True
        self.processing_thread = asyncio.create_task(self._processing_loop())
    
    async def submit_order(self, order: ExecutionRequest) -> str:
        """Submete ordem para roteamento inteligente"""
        # Adiciona timestamp de submissão
        order.metadata['submission_timestamp_ns'] = time.time_ns()
        
        # Seleciona venue ótimo
        optimal_venue = await self._select_optimal_venue(order)
        order.venue = optimal_venue
        
        # Adiciona à fila de processamento
        await self.order_queue.put(order)
        
        logger.info(f"📤 Ordem {order.id} roteada para {optimal_venue.value}")
        return order.id
    
    async def _select_optimal_venue(self, order: ExecutionRequest) -> ExecutionVenue:
        """Seleciona venue ótimo baseado em múltiplos fatores"""
        available_venues = list(self.connections.keys())
        
        if not available_venues:
            return ExecutionVenue.NYSE  # Default
        
        # Fatores de decisão
        factors = {}
        
        for venue in available_venues:
            score = 0.0
            
            # Latência (peso: 40%)
            latency_score = self.load_balancer.get_latency_score(venue)
            score += latency_score * 0.4
            
            # Liquidez (peso: 30%)
            liquidity_score = self.load_balancer.get_liquidity_score(venue, order.symbol)
            score += liquidity_score * 0.3
            
            # Custo (peso: 20%)
            cost_score = self.load_balancer.get_cost_score(venue)
            score += cost_score * 0.2
            
            # Disponibilidade (peso: 10%)
            availability_score = self.load_balancer.get_availability_score(venue)
            score += availability_score * 0.1
            
            factors[venue] = score
        
        # Seleciona venue com maior score
        optimal_venue = max(factors, key=factors.get)
        
        return optimal_venue
    
    async def _processing_loop(self):
        """Loop principal de processamento de ordens"""
        while self.processing_active:
            try:
                # Obtém ordem da fila
                order = await asyncio.wait_for(
                    self.order_queue.get(), 
                    timeout=1.0
                )
                
                # Processa ordem
                await self._process_order(order)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"❌ Erro no processamento de ordens: {e}")
    
    async def _process_order(self, order: ExecutionRequest):
        """Processa ordem individual"""
        start_time = time.time_ns()
        
        try:
            # Obtém conexão do venue
            connection = self.connections.get(order.venue)
            if not connection:
                logger.error(f"❌ Sem conexão para venue {order.venue.value}")
                return
            
            # Envia ordem
            success = await connection.send_order(order)
            if not success:
                logger.error(f"❌ Falha ao enviar ordem {order.id}")
                return
            
            # Aguarda resposta
            response = await connection.receive_response(timeout_ms=100)
            
            if response:
                # Calcula métricas
                total_latency = time.time_ns() - start_time
                self.metrics_collector.record_execution(order, response, total_latency)
                
                # Notifica handler
                if order.id in self.response_handlers:
                    handler = self.response_handlers[order.id]
                    await handler(response)
                
                logger.info(f"✅ Ordem {order.id} executada em {total_latency/1000:.2f}ms")
            else:
                logger.warning(f"⚠️ Sem resposta para ordem {order.id}")
                
        except Exception as e:
            logger.error(f"❌ Erro ao processar ordem {order.id}: {e}")
    
    def register_response_handler(self, order_id: str, handler: Callable):
        """Registra handler para resposta de ordem"""
        self.response_handlers[order_id] = handler
    
    def get_metrics(self) -> Dict[str, Any]:
        """Retorna métricas do roteador"""
        return {
            'active_connections': len(self.connections),
            'queue_depth': self.order_queue.qsize(),
            'processed_orders': self.metrics_collector.get_processed_count(),
            'average_latency_ms': self.metrics_collector.get_average_latency() / 1000000,
            'latency_distribution': self.metrics_collector.get_latency_distribution(),
            'venue_performance': self.metrics_collector.get_venue_performance()
        }

class LoadBalancer:
    """Balanceador de carga para múltiplos venues"""
    
    def __init__(self):
        self.venue_metrics = defaultdict(lambda: {
            'latency_samples': deque(maxlen=100),
            'success_rate': 0.0,
            'liquidity_scores': {},
            'cost_scores': {},
            'last_update': 0
        })
        
        logger.info("⚖️ LoadBalancer inicializado")
    
    def get_latency_score(self, venue: ExecutionVenue) -> float:
        """Calcula score de latência para venue"""
        metrics = self.venue_metrics[venue]
        latencies = metrics['latency_samples']
        
        if not latencies:
            return 0.5  # Score médio para venues sem dados
        
        # Usa mediana para evitar outliers
        median_latency = np.median(latencies)
        
        # Converte para score (0-1, onde 1 é melhor)
        # Assumindo latência ótima de 100μs e máxima de 10ms
        optimal_latency = 100000  # 100μs
        max_latency = 10000000   # 10ms
        
        if median_latency <= optimal_latency:
            return 1.0
        elif median_latency >= max_latency:
            return 0.0
        else:
            # Linear interpolation
            return 1.0 - (median_latency - optimal_latency) / (max_latency - optimal_latency)
    
    def get_liquidity_score(self, venue: ExecutionVenue, symbol: str) -> float:
        """Calcula score de liquidez para símbolo específico"""
        metrics = self.venue_metrics[venue]
        symbol_scores = metrics['liquidity_scores']
        
        if symbol in symbol_scores:
            return symbol_scores[symbol]
        
        # Score padrão baseado no venue
        venue_liquidity = {
            ExecutionVenue.NYSE: 0.8,
            ExecutionVenue.NASDAQ: 0.9,
            ExecutionVenue.CME: 0.7,
            ExecutionVenue.BATS: 0.6,
            ExecutionVenue.DARK_POOL: 0.4
        }
        
        return venue_liquidity.get(venue, 0.5)
    
    def get_cost_score(self, venue: ExecutionVenue) -> float:
        """Calcula score de custo (onde 1 é mais barato)"""
        metrics = self.venue_metrics[venue]
        cost_scores = metrics['cost_scores']
        
        if cost_scores:
            # Usa o custo médio
            avg_cost = np.mean(list(cost_scores.values()))
            # Converte para score (assumindo custo máximo de 0.1%)
            return max(0, 1.0 - avg_cost / 0.001)
        
        # Score padrão baseado no venue
        venue_costs = {
            ExecutionVenue.NYSE: 0.8,    # Mais caro
            ExecutionVenue.NASDAQ: 0.7,
            ExecutionVenue.CME: 0.6,
            ExecutionVenue.BATS: 0.9,    # Mais barato
            ExecutionVenue.DARK_POOL: 0.95
        }
        
        return venue_costs.get(venue, 0.5)
    
    def get_availability_score(self, venue: ExecutionVenue) -> float:
        """Calcula score de disponibilidade"""
        metrics = self.venue_metrics[venue]
        return metrics['success_rate']
    
    def update_metrics(self, venue: ExecutionVenue, latency_ns: int, 
                     success: bool, symbol: str = None, cost_bps: float = None):
        """Atualiza métricas do venue"""
        metrics = self.venue_metrics[venue]
        
        # Atualiza latência
        metrics['latency_samples'].append(latency_ns)
        
        # Atualiza taxa de sucesso
        if success:
            metrics['success_rate'] = metrics['success_rate'] * 0.95 + 0.05
        else:
            metrics['success_rate'] = metrics['success_rate'] * 0.95
        
        # Atualiza liquidez do símbolo
        if symbol and cost_bps is not None:
            metrics['liquidity_scores'][symbol] = max(0.1, 1.0 - cost_bps / 10.0)
        
        metrics['last_update'] = time.time()

class LatencyMetricsCollector:
    """Coletor de métricas de latência"""
    
    def __init__(self):
        self.execution_history = deque(maxlen=10000)
        self.venue_stats = defaultdict(lambda: {
            'count': 0,
            'total_latency': 0,
            'success_count': 0
        })
        
        logger.info("📊 LatencyMetricsCollector inicializado")
    
    def record_execution(self, order: ExecutionRequest, response: ExecutionResponse, 
                       total_latency_ns: int):
        """Registra execução com métricas"""
        execution_record = {
            'timestamp': time.time(),
            'venue': order.venue.value,
            'symbol': order.symbol,
            'order_type': order.order_type.value,
            'quantity': order.quantity,
            'latency_ns': total_latency_ns,
            'success': response.status in ['FILLED', 'PARTIALLY_FILLED'],
            'filled_quantity': response.filled_quantity,
            'average_price': response.average_price
        }
        
        self.execution_history.append(execution_record)
        
        # Atualiza estatísticas do venue
        venue_stats = self.venue_stats[order.venue]
        venue_stats['count'] += 1
        venue_stats['total_latency'] += total_latency_ns
        if execution_record['success']:
            venue_stats['success_count'] += 1
    
    def get_processed_count(self) -> int:
        """Retorna número total de execuções processadas"""
        return len(self.execution_history)
    
    def get_average_latency(self) -> float:
        """Retorna latência média em nanossegundos"""
        if not self.execution_history:
            return 0
        
        return np.mean([e['latency_ns'] for e in self.execution_history])
    
    def get_latency_distribution(self) -> Dict[str, int]:
        """Retorna distribuição de latência por tier"""
        distribution = {
            'ultra_low': 0,  # < 100μs
            'low': 0,        # 100μs - 1ms
            'medium': 0,      # 1ms - 10ms
            'high': 0          # > 10ms
        }
        
        for execution in self.execution_history:
            latency_us = execution['latency_ns'] / 1000
            
            if latency_us < 100:
                distribution['ultra_low'] += 1
            elif latency_us < 1000:
                distribution['low'] += 1
            elif latency_us < 10000:
                distribution['medium'] += 1
            else:
                distribution['high'] += 1
        
        return distribution
    
    def get_venue_performance(self) -> Dict[str, Any]:
        """Retorna performance por venue"""
        performance = {}
        
        for venue, stats in self.venue_stats.items():
            if stats['count'] > 0:
                avg_latency = stats['total_latency'] / stats['count']
                success_rate = stats['success_count'] / stats['count']
                
                performance[venue.value] = {
                    'executions': stats['count'],
                    'average_latency_ms': avg_latency / 1000000,
                    'success_rate': success_rate,
                    'success_rate_percent': success_rate * 100
                }
        
        return performance

class LowLatencyExecutionEngine:
    """Motor principal de execução de baixa latência"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.order_router = OrderRouter(self.config)
        self.is_running = False
        self.execution_stats = {
            'total_orders': 0,
            'successful_orders': 0,
            'failed_orders': 0,
            'average_latency_ms': 0.0
        }
        
        logger.info("🚀 LowLatencyExecutionEngine inicializado")
    
    async def start(self, venues: List[ExecutionVenue]):
        """Inicia motor de execução"""
        if self.is_running:
            logger.warning("⚠️ Motor já está em execução")
            return
        
        logger.info("🚀 Iniciando motor de execução de baixa latência")
        
        # Inicializa roteador
        await self.order_router.initialize(venues)
        
        self.is_running = True
        logger.info("✅ Motor de execução iniciado")
    
    async def stop(self):
        """Para motor de execução"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Desconecta todas as conexões
        for connection in self.order_router.connections.values():
            await connection.disconnect()
        
        logger.info("🛑 Motor de execução parado")
    
    async def submit_order(self, symbol: str, side: str, order_type: OrderType,
                        quantity: float, price: Optional[float] = None,
                        account: str = 'default', venue: ExecutionVenue = None) -> str:
        """Submete ordem para execução"""
        
        # Gera ID único
        order_id = f"ORD_{int(time.time_ns())}"
        
        # Cria requisição
        order = ExecutionRequest(
            id=order_id,
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            time_in_force='IOC',
            account=account,
            venue=venue or ExecutionVenue.NYSE,
            timestamp=datetime.now(),
            priority=1
        )
        
        # Submete ao roteador
        return await self.order_router.submit_order(order)
    
    async def submit_market_order(self, symbol: str, side: str, quantity: float,
                               account: str = 'default') -> str:
        """Submete ordem a mercado"""
        return await self.submit_order(
            symbol=symbol,
            side=side,
            order_type=OrderType.MARKET,
            quantity=quantity,
            account=account
        )
    
    async def submit_limit_order(self, symbol: str, side: str, quantity: float,
                             price: float, account: str = 'default') -> str:
        """Submete ordem limitada"""
        return await self.submit_order(
            symbol=symbol,
            side=side,
            order_type=OrderType.LIMIT,
            quantity=quantity,
            price=price,
            account=account
        )
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Retorna métricas de performance do motor"""
        router_metrics = self.order_router.get_metrics()
        
        return {
            'engine_status': 'running' if self.is_running else 'stopped',
            'router_metrics': router_metrics,
            'execution_stats': self.execution_stats,
            'timestamp': datetime.now().isoformat()
        }
    
    def export_metrics(self, filepath: str):
        """Exporta métricas para arquivo"""
        metrics = self.get_performance_metrics()
        
        with open(filepath, 'w') as f:
            json.dump(metrics, f, indent=2, default=str)
        
        logger.info(f"📊 Métricas exportadas para {filepath}")

# Configuração padrão
DEFAULT_EXECUTION_CONFIG = {
    'venues': {
        'nyse': {
            'host': 'nyse.example.com',
            'port': 8080,
            'connection_type': 'tcp',
            'use_ssl': True
        },
        'nasdaq': {
            'host': 'nasdaq.example.com',
            'port': 8081,
            'connection_type': 'tcp',
            'use_ssl': True
        },
        'bats': {
            'host': 'bats.example.com',
            'port': 8082,
            'connection_type': 'tcp',
            'use_ssl': False
        }
    },
    'load_balancing': {
        'enable': True,
        'weights': {
            'nyse': 0.4,
            'nasdaq': 0.4,
            'bats': 0.2
        }
    },
    'latency_optimization': {
        'enable_tcp_nodelay': True,
        'socket_buffer_size': 65536,
        'heartbeat_interval': 30
    }
}

if __name__ == "__main__":
    # Exemplo de uso
    async def test_low_latency_execution():
        """Testa motor de execução de baixa latência"""
        print("🚀 Iniciando Teste do Motor de Execução de Baixa Latência")
        print("=" * 70)
        
        # Cria motor
        engine = LowLatencyExecutionEngine(DEFAULT_EXECUTION_CONFIG)
        
        # Inicia motor com venues de exemplo
        venues = [
            ExecutionVenue.NYSE,
            ExecutionVenue.NASDAQ,
            ExecutionVenue.BATS
        ]
        
        await engine.start(venues)
        
        # Simula algumas ordens
        print("\n📤 Enviando ordens de teste...")
        
        # Ordem de compra a mercado
        order1_id = await engine.submit_market_order(
            symbol='AAPL',
            side='buy',
            quantity=100
        )
        print(f"Ordem 1 enviada: {order1_id}")
        
        # Ordem de venda limitada
        order2_id = await engine.submit_limit_order(
            symbol='MSFT',
            side='sell',
            quantity=50,
            price=305.0
        )
        print(f"Ordem 2 enviada: {order2_id}")
        
        # Ordem de compra a mercado grande
        order3_id = await engine.submit_market_order(
            symbol='GOOGL',
            side='buy',
            quantity=10
        )
        print(f"Ordem 3 enviada: {order3_id}")
        
        # Aguarda um pouco para processamento
        await asyncio.sleep(2)
        
        # Obtém métricas
        metrics = engine.get_performance_metrics()
        
        print(f"\n📊 MÉTRICAS DE PERFORMANCE:")
        print("=" * 40)
        print(f"Status do Motor: {metrics['engine_status']}")
        print(f"Conexões Ativas: {metrics['router_metrics']['active_connections']}")
        print(f"Profundidade da Fila: {metrics['router_metrics']['queue_depth']}")
        print(f"Ordens Processadas: {metrics['router_metrics']['processed_orders']}")
        print(f"Latência Média: {metrics['router_metrics']['average_latency_ms']:.2f}ms")
        
        # Distribuição de latência
        latency_dist = metrics['router_metrics']['latency_distribution']
        print(f"\n📈 Distribuição de Latência:")
        print(f"Ultra Baixa (<100μs): {latency_dist['ultra_low']}")
        print(f"Baixa (100μs-1ms): {latency_dist['low']}")
        print(f"Média (1ms-10ms): {latency_dist['medium']}")
        print(f"Alta (>10ms): {latency_dist['high']}")
        
        # Performance por venue
        venue_perf = metrics['router_metrics']['venue_performance']
        print(f"\n🏢 Performance por Venue:")
        for venue, perf in venue_perf.items():
            print(f"{venue}:")
            print(f"  Execuções: {perf['executions']}")
            print(f"  Latência Média: {perf['average_latency_ms']:.2f}ms")
            print(f"  Taxa de Sucesso: {perf['success_rate_percent']:.1f}%")
        
        # Exporta métricas
        engine.export_metrics('execution_metrics.json')
        
        # Para motor
        await engine.stop()
        
        print("\n💾 Métricas exportadas")
        print("✅ Teste concluído com sucesso!")
        
        return engine
    
    # Executa teste
    engine = asyncio.run(test_low_latency_execution())

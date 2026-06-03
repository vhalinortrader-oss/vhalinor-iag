"""
╔═════════════════════════════════════════════════════════════════════════════╗
║                    AMBIENTE DE SIMULAÇÃO DE EXECUÇÃO                        ║
║                 Componente 10: Simulador Realista de Trading                 ║
╚═════════════════════════════════════════════════════════════════════════════╝
"""

import asyncio
import numpy as np
import pandas as pd
from scipy import stats
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import pickle
from collections import deque, defaultdict
import time
import threading
import random
from concurrent.futures import ThreadPoolExecutor

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ExecutionSimulationEnvironment')

class OrderType(Enum):
    """Tipos de ordens"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    ICEBERG = "iceberg"
    TWAP = "twap"
    VWAP = "vwap"
    PEG = "peg"
    ALGO = "algo"

class OrderSide(Enum):
    """Lado da ordem"""
    BUY = "buy"
    SELL = "sell"
    BUY_TO_COVER = "buy_to_cover"
    SELL_SHORT = "sell_short"

class OrderStatus(Enum):
    """Status da ordem"""
    NEW = "new"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"
    PENDING_CANCEL = "pending_cancel"
    PENDING_REPLACE = "pending_replace"

class ExecutionAlgorithm(Enum):
    """Algoritmos de execução"""
    SIMPLE = "simple"
    TWAP = "twap"
    VWAP = "vwap"
    POV = "pov"
    IMPLEMENTATION_SHORTFALL = "implementation_shortfall"
    ADAPTIVE = "adaptive"
    LIQUIDITY_SEEKING = "liquidity_seeking"
    DARK_POOL = "dark_pool"

@dataclass
class Order:
    """Ordem de trading"""
    id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: Optional[float]
    stop_price: Optional[float]
    time_in_force: str
    created_time: datetime
    updated_time: datetime
    status: OrderStatus
    filled_quantity: float = 0.0
    remaining_quantity: float = 0.0
    average_fill_price: float = 0.0
    commission: float = 0.0
    slippage: float = 0.0
    parent_order_id: Optional[str] = None
    child_orders: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        self.remaining_quantity = self.quantity - self.filled_quantity
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'symbol': self.symbol,
            'side': self.side.value,
            'order_type': self.order_type.value,
            'quantity': self.quantity,
            'price': self.price,
            'stop_price': self.stop_price,
            'time_in_force': self.time_in_force,
            'created_time': self.created_time.isoformat(),
            'updated_time': self.updated_time.isoformat(),
            'status': self.status.value,
            'filled_quantity': self.filled_quantity,
            'remaining_quantity': self.remaining_quantity,
            'average_fill_price': self.average_fill_price,
            'commission': self.commission,
            'slippage': self.slippage,
            'parent_order_id': self.parent_order_id,
            'child_orders': self.child_orders,
            'metadata': self.metadata
        }

@dataclass
class Fill:
    """Execução de ordem"""
    id: str
    order_id: str
    symbol: str
    side: OrderSide
    quantity: float
    price: float
    timestamp: datetime
    commission: float
    slippage: float
    liquidity_provider: str
    execution_venue: str
    trade_id: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'order_id': self.order_id,
            'symbol': self.symbol,
            'side': self.side.value,
            'quantity': self.quantity,
            'price': self.price,
            'timestamp': self.timestamp.isoformat(),
            'commission': self.commission,
            'slippage': self.slippage,
            'liquidity_provider': self.liquidity_provider,
            'execution_venue': self.execution_venue,
            'trade_id': self.trade_id,
            'metadata': self.metadata
        }

@dataclass
class MarketData:
    """Dados de mercado simulados"""
    timestamp: datetime
    symbol: str
    bid_price: float
    ask_price: float
    bid_size: float
    ask_size: float
    last_price: float
    last_size: float
    volume: float
    vwap: float
    high: float
    low: float
    open_price: float
    close_price: float
    volatility: float
    market_depth: Dict[str, List[Tuple[float, float]]] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.isoformat(),
            'symbol': self.symbol,
            'bid_price': self.bid_price,
            'ask_price': self.ask_price,
            'bid_size': self.bid_size,
            'ask_size': self.ask_size,
            'last_price': self.last_price,
            'last_size': self.last_size,
            'volume': self.volume,
            'vwap': self.vwap,
            'high': self.high,
            'low': self.low,
            'open_price': self.open_price,
            'close_price': self.close_price,
            'volatility': self.volatility,
            'market_depth': self.market_depth
        }

@dataclass
class ExecutionMetrics:
    """Métricas de execução"""
    symbol: str
    order_id: str
    algorithm: ExecutionAlgorithm
    start_time: datetime
    end_time: datetime
    total_quantity: float
    filled_quantity: float
    fill_rate: float
    average_price: float
    vwap: float
    implementation_shortfall: float
    market_impact: float
    timing_cost: float
    commission_total: float
    slippage_total: float
    number_of_fills: int
    execution_time_seconds: float
    efficiency_score: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'symbol': self.symbol,
            'order_id': self.order_id,
            'algorithm': self.algorithm.value,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'total_quantity': self.total_quantity,
            'filled_quantity': self.filled_quantity,
            'fill_rate': self.fill_rate,
            'average_price': self.average_price,
            'vwap': self.vwap,
            'implementation_shortfall': self.implementation_shortfall,
            'market_impact': self.market_impact,
            'timing_cost': self.timing_cost,
            'commission_total': self.commission_total,
            'slippage_total': self.slippage_total,
            'number_of_fills': self.number_of_fills,
            'execution_time_seconds': self.execution_time_seconds,
            'efficiency_score': self.efficiency_score
        }

class MarketSimulator:
    """Simulador de mercado realista"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Parâmetros de mercado
        self.spread_bps = self.config.get('spread_bps', 5)  # 0.05%
        self.depth_levels = self.config.get('depth_levels', 10)
        self.base_volatility = self.config.get('base_volatility', 0.02)
        self.liquidity_factor = self.config.get('liquidity_factor', 1.0)
        
        # Estado do mercado
        self.current_prices = {}
        self.market_data_history = defaultdict(list)
        self.order_book = defaultdict(lambda: {'bids': [], 'asks': []})
        
        # Componentes de simulação
        self.price_generator = PriceGenerator(self.base_volatility)
        self.liquidity_model = LiquidityModel(self.liquidity_factor)
        self.impact_model = MarketImpactModel()
        
        logger.info("📊 MarketSimulator inicializado")
    
    def initialize_market(self, symbols: List[str], initial_prices: Dict[str, float]):
        """Inicializa mercado com símbolos e preços"""
        for symbol in symbols:
            price = initial_prices.get(symbol, 100.0)
            self.current_prices[symbol] = price
            
            # Inicializa order book
            spread = price * self.spread_bps / 10000
            self.order_book[symbol]['bids'] = [(price - spread, 1000)]
            self.order_book[symbol]['asks'] = [(price + spread, 1000)]
        
        logger.info(f"🏪 Mercado inicializado com {len(symbols)} símbolos")
    
    def update_market(self, timestamp: datetime) -> Dict[str, MarketData]:
        """Atualiza estado do mercado"""
        market_data = {}
        
        for symbol in self.current_prices.keys():
            # Gera novo preço
            new_price = self.price_generator.generate_price(
                self.current_prices[symbol], timestamp
            )
            
            # Atualiza order book
            self._update_order_book(symbol, new_price, timestamp)
            
            # Cria market data
            data = self._create_market_data(symbol, timestamp)
            market_data[symbol] = data
            
            # Armazena histórico
            self.market_data_history[symbol].append(data)
            self.current_prices[symbol] = new_price
        
        return market_data
    
    def _update_order_book(self, symbol: str, price: float, timestamp: datetime):
        """Atualiza order book para um símbolo"""
        spread = price * self.spread_bps / 10000
        
        # Atualiza bids e asks
        self.order_book[symbol]['bids'][0] = (price - spread, 
                                                  self.liquidity_model.get_liquidity(symbol, 'bid'))
        self.order_book[symbol]['asks'][0] = (price + spread, 
                                                  self.liquidity_model.get_liquidity(symbol, 'ask'))
        
        # Adiciona ruído e profundidade
        for i in range(1, self.depth_levels):
            bid_price = price - spread * (1 + i * 0.1)
            ask_price = price + spread * (1 + i * 0.1)
            
            if len(self.order_book[symbol]['bids']) <= i:
                self.order_book[symbol]['bids'].append(
                    (bid_price, self.liquidity_model.get_liquidity(symbol, 'bid') * (1 - i * 0.1))
                )
            
            if len(self.order_book[symbol]['asks']) <= i:
                self.order_book[symbol]['asks'].append(
                    (ask_price, self.liquidity_model.get_liquidity(symbol, 'ask') * (1 - i * 0.1))
                )
    
    def _create_market_data(self, symbol: str, timestamp: datetime) -> MarketData:
        """Cria dados de mercado para um símbolo"""
        bids = self.order_book[symbol]['bids']
        asks = self.order_book[symbol]['asks']
        
        if not bids or not asks:
            return None
        
        best_bid = bids[0][0]
        best_ask = asks[0][0]
        mid_price = (best_bid + best_ask) / 2
        
        # Calcula VWAP (simplificado)
        vwap = mid_price  # Simplificado
        
        # Histórico para high/low
        history = self.market_data_history[symbol]
        if history:
            high = max([d.high for d in history[-100:]] + [mid_price])
            low = min([d.low for d in history[-100:]] + [mid_price])
            open_price = history[0].open_price if history else mid_price
        else:
            high = low = open_price = mid_price
        
        return MarketData(
            timestamp=timestamp,
            symbol=symbol,
            bid_price=best_bid,
            ask_price=best_ask,
            bid_size=bids[0][1],
            ask_size=asks[0][1],
            last_price=mid_price,
            last_size=100,  # Simplificado
            volume=np.random.uniform(1000, 10000),  # Simplificado
            vwap=vwap,
            high=high,
            low=low,
            open_price=open_price,
            close_price=mid_price,
            volatility=self.base_volatility,
            market_depth={
                'bids': bids[:5],
                'asks': asks[:5]
            }
        )
    
    def execute_order(self, order: Order) -> List[Fill]:
        """Executa ordem no mercado simulado"""
        fills = []
        symbol = order.symbol
        
        if symbol not in self.order_book:
            return fills
        
        book = self.order_book[symbol]
        
        if order.side in [OrderSide.BUY, OrderSide.BUY_TO_COVER]:
            # Compra: executa contra asks
            remaining_qty = order.quantity
            
            for price, size in book['asks']:
                if remaining_qty <= 0:
                    break
                
                fill_qty = min(remaining_qty, size)
                
                # Calcula slippage
                slippage = self.impact_model.calculate_slippage(
                    fill_qty, size, order.order_type
                )
                fill_price = price * (1 + slippage)
                
                # Cria fill
                fill = Fill(
                    id=f"fill_{order.id}_{len(fills)}",
                    order_id=order.id,
                    symbol=symbol,
                    side=order.side,
                    quantity=fill_qty,
                    price=fill_price,
                    timestamp=datetime.now(),
                    commission=fill_qty * fill_price * 0.001,  # 0.1%
                    slippage=slippage,
                    liquidity_provider="simulator",
                    execution_venue="sim_exchange",
                    trade_id=f"trade_{int(time.time() * 1000)}"
                )
                
                fills.append(fill)
                remaining_qty -= fill_qty
                
                # Atualiza order book
                size -= fill_qty
                if size <= 0:
                    book['asks'].remove((price, 0))
        
        elif order.side in [OrderSide.SELL, OrderSide.SELL_SHORT]:
            # Venda: executa contra bids
            remaining_qty = order.quantity
            
            for price, size in book['bids']:
                if remaining_qty <= 0:
                    break
                
                fill_qty = min(remaining_qty, size)
                
                # Calcula slippage
                slippage = self.impact_model.calculate_slippage(
                    fill_qty, size, order.order_type
                )
                fill_price = price * (1 - slippage)
                
                # Cria fill
                fill = Fill(
                    id=f"fill_{order.id}_{len(fills)}",
                    order_id=order.id,
                    symbol=symbol,
                    side=order.side,
                    quantity=fill_qty,
                    price=fill_price,
                    timestamp=datetime.now(),
                    commission=fill_qty * fill_price * 0.001,
                    slippage=slippage,
                    liquidity_provider="simulator",
                    execution_venue="sim_exchange",
                    trade_id=f"trade_{int(time.time() * 1000)}"
                )
                
                fills.append(fill)
                remaining_qty -= fill_qty
                
                # Atualiza order book
                size -= fill_qty
                if size <= 0:
                    book['bids'].remove((price, 0))
        
        return fills

class PriceGenerator:
    """Gerador de preços realista"""
    
    def __init__(self, base_volatility: float = 0.02):
        self.base_volatility = base_volatility
        self.trend_component = 0.0
        self.mean_reversion_level = 100.0
        self.regime = "normal"
        
    def generate_price(self, current_price: float, timestamp: datetime) -> float:
        """Gera próximo preço baseado em modelo estocástico"""
        # Componente de tendência
        self.trend_component += np.random.normal(0, 0.0001)
        
        # Componente de mean reversion
        mean_reversion_force = (self.mean_reversion_level - current_price) * 0.001
        
        # Componente estocástico
        random_shock = np.random.normal(0, self.base_volatility / np.sqrt(252))
        
        # Mudança de regime (ocasional)
        if np.random.random() < 0.001:  # 0.1% de chance
            self.regime = np.random.choice(["normal", "volatile", "trending"])
            
            if self.regime == "volatile":
                volatility_multiplier = 2.0
            elif self.regime == "trending":
                self.trend_component = np.random.choice([-0.001, 0.001]) * 5
                volatility_multiplier = 1.0
            else:  # normal
                volatility_multiplier = 1.0
                self.trend_component *= 0.5
        else:
            volatility_multiplier = 1.0
        
        # Calcula novo preço
        price_change = (
            self.trend_component +
            mean_reversion_force +
            random_shock * volatility_multiplier
        )
        
        new_price = current_price * (1 + price_change)
        
        # Garante preço positivo
        return max(new_price, 0.01)

class LiquidityModel:
    """Modelo de liquidez"""
    
    def __init__(self, liquidity_factor: float = 1.0):
        self.liquidity_factor = liquidity_factor
        self.base_liquidity = 10000
        self.intraday_pattern = self._generate_intraday_pattern()
        
    def _generate_intraday_pattern(self) -> np.ndarray:
        """Gera padrão intradiário de liquidez"""
        hours = np.arange(24)
        # Padrão: baixa liquidade early morning/late night, alta durante dia
        pattern = np.sin((hours - 6) * np.pi / 12) * 0.5 + 0.5
        pattern = np.maximum(pattern, 0.1)  # Mínimo 10%
        return pattern
    
    def get_liquidity(self, symbol: str, side: str) -> float:
        """Retorna liquidez disponível"""
        hour = datetime.now().hour
        intraday_multiplier = self.intraday_pattern[hour]
        
        # Variação por símbolo
        symbol_multiplier = np.random.uniform(0.5, 2.0)
        
        # Variação por lado
        side_multiplier = 1.0 if side == 'bid' else 0.9
        
        liquidity = (
            self.base_liquidity *
            self.liquidity_factor *
            intraday_multiplier *
            symbol_multiplier *
            side_multiplier
        )
        
        return max(liquidity, 100)  # Mínimo 100

class MarketImpactModel:
    """Modelo de impacto de mercado"""
    
    def __init__(self):
        self.temporary_impact_factor = 0.0001
        self.permanent_impact_factor = 0.0002
        
    def calculate_slippage(self, order_size: float, available_size: float, 
                          order_type: OrderType) -> float:
        """Calcula slippage baseado no tamanho da ordem"""
        if order_type == OrderType.MARKET:
            # Impacto proporcional ao tamanho relativo
            size_ratio = order_size / (order_size + available_size)
            base_slippage = size_ratio * self.temporary_impact_factor
            
            # Ajuste por tipo de ordem
            if order_type in [OrderType.STOP, OrderType.STOP_LIMIT]:
                base_slippage *= 1.5  # Pior slippage para ordens stop
            
            return base_slippage
        
        elif order_type == OrderType.LIMIT:
            # Menor slippage para ordens limitadas
            return self.temporary_impact_factor * 0.1
        
        else:
            # Algoritmos: slippage intermediário
            return self.temporary_impact_factor * 0.3

class ExecutionAlgorithm:
    """Algoritmo de execução base"""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.execution_history = []
        
    def execute(self, order: Order, market_data: MarketData, 
                market_simulator: MarketSimulator) -> List[Fill]:
        """Executa ordem usando algoritmo específico"""
        raise NotImplementedError("Subclasses devem implementar execute()")
    
    def get_metrics(self, order: Order, fills: List[Fill], 
                   market_data: MarketData) -> ExecutionMetrics:
        """Calcula métricas de execução"""
        if not fills:
            return None
        
        # Métricas básicas
        total_quantity = order.quantity
        filled_quantity = sum(f.quantity for f in fills)
        fill_rate = filled_quantity / total_quantity if total_quantity > 0 else 0
        
        # Preços médios
        average_price = sum(f.price * f.quantity for f in fills) / filled_quantity
        vwap = market_data.vwap
        
        # Implementation shortfall
        decision_price = market_data.last_price
        implementation_shortfall = (average_price - decision_price) / decision_price
        
        # Market impact (simplificado)
        market_impact = abs(implementation_shortfall) * 0.5
        
        # Timing cost
        timing_cost = 0.0  # Simplificado
        
        # Comissões e slippage
        commission_total = sum(f.commission for f in fills)
        slippage_total = sum(f.slippage * f.quantity for f in fills)
        
        # Tempo de execução
        start_time = order.created_time
        end_time = max(f.timestamp for f in fills)
        execution_time = (end_time - start_time).total_seconds()
        
        # Score de eficiência
        efficiency_score = self._calculate_efficiency_score(
            fill_rate, implementation_shortfall, slippage_total, commission_total
        )
        
        return ExecutionMetrics(
            symbol=order.symbol,
            order_id=order.id,
            algorithm=ExecutionAlgorithm(self.name),
            start_time=start_time,
            end_time=end_time,
            total_quantity=total_quantity,
            filled_quantity=filled_quantity,
            fill_rate=fill_rate,
            average_price=average_price,
            vwap=vwap,
            implementation_shortfall=implementation_shortfall,
            market_impact=market_impact,
            timing_cost=timing_cost,
            commission_total=commission_total,
            slippage_total=slippage_total,
            number_of_fills=len(fills),
            execution_time_seconds=execution_time,
            efficiency_score=efficiency_score
        )
    
    def _calculate_efficiency_score(self, fill_rate: float, 
                                  implementation_shortfall: float,
                                  slippage_total: float, 
                                  commission_total: float) -> float:
        """Calcula score de eficiência (0-100)"""
        # Componentes normalizados
        fill_score = fill_rate * 40  # 40% do peso
        
        # Menor implementation shortfall é melhor
        shortfall_score = max(0, 20 - abs(implementation_shortfall) * 2000)  # 20% do peso
        
        # Menor slippage é melhor
        slippage_score = max(0, 20 - slippage_total * 1000)  # 20% do peso
        
        # Menor comissão é melhor
        commission_score = max(0, 20 - commission_total * 100)  # 20% do peso
        
        return fill_score + shortfall_score + slippage_score + commission_score

class TWAPAlgorithm(ExecutionAlgorithm):
    """Algoritmo TWAP (Time-Weighted Average Price)"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("TWAP", config)
        self.duration_minutes = self.config.get('duration_minutes', 30)
        self.slice_interval = self.config.get('slice_interval', 60)  # segundos
        
    def execute(self, order: Order, market_data: MarketData, 
                market_simulator: MarketSimulator) -> List[Fill]:
        """Executa ordem usando TWAP"""
        fills = []
        
        # Divide ordem em fatias temporais
        total_duration = self.duration_minutes * 60  # segundos
        n_slices = max(1, total_duration // self.slice_interval)
        slice_size = order.quantity / n_slices
        
        for i in range(n_slices):
            # Cria ordem fatia
            slice_order = Order(
                id=f"{order.id}_slice_{i}",
                symbol=order.symbol,
                side=order.side,
                order_type=OrderType.MARKET,
                quantity=slice_size,
                price=None,
                stop_price=None,
                time_in_force="IOC",
                created_time=datetime.now(),
                updated_time=datetime.now(),
                status=OrderStatus.NEW
            )
            
            # Executa fatia
            slice_fills = market_simulator.execute_order(slice_order)
            fills.extend(slice_fills)
            
            # Aguarda próximo intervalo (simulado)
            time.sleep(0.01)  # Pequena pausa para simulação
        
        return fills

class VWAPAlgorithm(ExecutionAlgorithm):
    """Algoritmo VWAP (Volume-Weighted Average Price)"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__("VWAP", config)
        self.duration_minutes = self.config.get('duration_minutes', 30)
        self.volume_profile = self.config.get('volume_profile', 'uniform')
        
    def execute(self, order: Order, market_data: MarketData, 
                market_simulator: MarketSimulator) -> List[Fill]:
        """Executa ordem usando VWAP"""
        fills = []
        
        # Perfil de volume intradiário
        volume_curve = self._get_volume_curve()
        
        # Divide ordem baseado no perfil de volume
        total_slices = len(volume_curve)
        slice_sizes = [order.quantity * weight for weight in volume_curve]
        
        for i, slice_size in enumerate(slice_sizes):
            # Cria ordem fatia
            slice_order = Order(
                id=f"{order.id}_vwap_{i}",
                symbol=order.symbol,
                side=order.side,
                order_type=OrderType.LIMIT,
                quantity=slice_size,
                price=market_data.mid_price if hasattr(market_data, 'mid_price') else market_data.last_price,
                stop_price=None,
                time_in_force="IOC",
                created_time=datetime.now(),
                updated_time=datetime.now(),
                status=OrderStatus.NEW
            )
            
            # Executa fatia
            slice_fills = market_simulator.execute_order(slice_order)
            fills.extend(slice_fills)
            
            # Pequena pausa
            time.sleep(0.01)
        
        return fills
    
    def _get_volume_curve(self) -> List[float]:
        """Retorna curva de volume normalizada"""
        if self.volume_profile == 'uniform':
            # Distribuição uniforme
            return [1.0 / 10] * 10
        
        elif self.volume_profile == 'u_shaped':
            # Mais volume no início e fim
            hours = np.linspace(0, 1, 10)
            curve = 0.3 * np.exp(-((hours - 0.1) ** 2) / 0.05) + \
                   0.3 * np.exp(-((hours - 0.9) ** 2) / 0.05) + \
                   0.4 * np.ones_like(hours)
            return curve / curve.sum()
        
        else:  # bell_shaped
            # Mais volume no meio
            hours = np.linspace(0, 1, 10)
            curve = np.exp(-((hours - 0.5) ** 2) / 0.1)
            return curve / curve.sum()

class ExecutionSimulationEnvironment:
    """Ambiente de simulação de execução"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Componentes principais
        self.market_simulator = MarketSimulator(self.config.get('market', {}))
        self.algorithms = {
            'simple': ExecutionAlgorithm('Simple'),
            'twap': TWAPAlgorithm(self.config.get('twap', {})),
            'vwap': VWAPAlgorithm(self.config.get('vwap', {}))
        }
        
        # Estado da simulação
        self.orders = {}
        self.fills = []
        self.execution_metrics = []
        self.simulation_active = False
        self.current_time = None
        
        # Métricas agregadas
        self.daily_stats = defaultdict(list)
        
        logger.info("🎭 ExecutionSimulationEnvironment inicializado")
    
    def initialize_simulation(self, symbols: List[str], 
                           initial_prices: Dict[str, float],
                           start_time: datetime = None):
        """Inicializa simulação"""
        self.current_time = start_time or datetime.now()
        self.market_simulator.initialize_market(symbols, initial_prices)
        
        logger.info(f"🚀 Simulação inicializada: {len(symbols)} símbolos")
    
    def submit_order(self, order: Order, algorithm: str = 'simple') -> str:
        """Submete ordem para execução"""
        if order.id in self.orders:
            raise ValueError(f"Ordem {order.id} já existe")
        
        # Valida ordem
        if self._validate_order(order):
            self.orders[order.id] = {
                'order': order,
                'algorithm': algorithm,
                'status': OrderStatus.NEW,
                'submitted_time': self.current_time
            }
            
            logger.info(f"📤 Ordem {order.id} submetida: {order.side.value} {order.quantity} {order.symbol}")
            return order.id
        else:
            order.status = OrderStatus.REJECTED
            raise ValueError("Ordem rejeitada na validação")
    
    def _validate_order(self, order: Order) -> bool:
        """Valida ordem"""
        # Validações básicas
        if order.quantity <= 0:
            return False
        
        if order.side not in [OrderSide.BUY, OrderSide.SELL, OrderSide.BUY_TO_COVER, OrderSide.SELL_SHORT]:
            return False
        
        if order.order_type not in [OrderType.MARKET, OrderType.LIMIT, OrderType.STOP]:
            return False
        
        # Validações de preço
        if order.order_type == OrderType.LIMIT and (not order.price or order.price <= 0):
            return False
        
        if order.order_type == OrderType.STOP and (not order.stop_price or order.stop_price <= 0):
            return False
        
        return True
    
    async def run_simulation(self, duration_minutes: int = 60, 
                          time_step_seconds: int = 1):
        """Executa simulação por período determinado"""
        if not self.current_time:
            raise ValueError("Simulação não inicializada")
        
        self.simulation_active = True
        end_time = self.current_time + timedelta(minutes=duration_minutes)
        
        logger.info(f"⏱️ Iniciando simulação: {duration_minutes} minutos")
        
        simulation_steps = 0
        
        while self.current_time < end_time and self.simulation_active:
            # Atualiza mercado
            market_data = self.market_simulator.update_market(self.current_time)
            
            # Processa ordens pendentes
            await self._process_orders(market_data)
            
            # Coleta estatísticas
            self._collect_statistics(market_data)
            
            # Avança tempo
            self.current_time += timedelta(seconds=time_step_seconds)
            simulation_steps += 1
            
            # Log progresso
            if simulation_steps % 60 == 0:  # A cada minuto
                elapsed = (self.current_time - (end_time - timedelta(minutes=duration_minutes))).total_seconds() / 60
                logger.info(f"⏰ Simulação: {elapsed:.1f}/{duration_minutes} minutos")
        
        self.simulation_active = False
        logger.info("✅ Simulação concluída")
        
        return self.get_simulation_results()
    
    async def _process_orders(self, market_data: Dict[str, MarketData]):
        """Processa ordens pendentes"""
        for order_id, order_info in list(self.orders.items()):
            order = order_info['order']
            algorithm_name = order_info['algorithm']
            
            # Pula ordens já processadas
            if order.status in [OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED]:
                continue
            
            try:
                # Obtém algoritmo
                algorithm = self.algorithms.get(algorithm_name)
                if not algorithm:
                    algorithm = self.algorithms['simple']
                
                # Executa ordem
                symbol_data = market_data.get(order.symbol)
                if symbol_data:
                    fills = algorithm.execute(order, symbol_data, self.market_simulator)
                    
                    # Atualiza ordem
                    if fills:
                        total_filled = sum(f.quantity for f in fills)
                        order.filled_quantity += total_filled
                        order.remaining_quantity = order.quantity - order.filled_quantity
                        order.updated_time = self.current_time
                        
                        # Calcula preço médio
                        if order.filled_quantity > 0:
                            total_value = sum(f.price * f.quantity for f in fills)
                            order.average_fill_price = total_value / order.filled_quantity
                        
                        # Adiciona fills
                        self.fills.extend(fills)
                        
                        # Atualiza status
                        if order.remaining_quantity <= 0:
                            order.status = OrderStatus.FILLED
                        else:
                            order.status = OrderStatus.PARTIALLY_FILLED
                        
                        # Calcula métricas
                        metrics = algorithm.get_metrics(order, fills, symbol_data)
                        if metrics:
                            self.execution_metrics.append(metrics)
                        
                        logger.info(f"✅ Ordem {order.id}: {len(fills)} fills, "
                                  f"{order.filled_quantity}/{order.quantity} preenchido")
            
            except Exception as e:
                logger.error(f"❌ Erro ao processar ordem {order_id}: {e}")
                order.status = OrderStatus.REJECTED
    
    def _collect_statistics(self, market_data: Dict[str, MarketData]):
        """Coleta estatísticas da simulação"""
        for symbol, data in market_data.items():
            self.daily_stats[symbol].append({
                'timestamp': self.current_time,
                'price': data.last_price,
                'volume': data.volume,
                'spread': data.ask_price - data.bid_price,
                'volatility': data.volatility
            })
    
    def get_simulation_results(self) -> Dict[str, Any]:
        """Retorna resultados completos da simulação"""
        # Estatísticas das ordens
        order_stats = {
            'total_orders': len(self.orders),
            'filled_orders': len([o for o in self.orders.values() if o['order'].status == OrderStatus.FILLED]),
            'partially_filled_orders': len([o for o in self.orders.values() if o['order'].status == OrderStatus.PARTIALLY_FILLED]),
            'cancelled_orders': len([o for o in self.orders.values() if o['order'].status == OrderStatus.CANCELLED]),
            'rejected_orders': len([o for o in self.orders.values() if o['order'].status == OrderStatus.REJECTED])
        }
        
        # Estatísticas dos fills
        fill_stats = {
            'total_fills': len(self.fills),
            'total_volume': sum(f.quantity for f in self.fills),
            'total_commission': sum(f.commission for f in self.fills),
            'average_slippage': np.mean([f.slippage for f in self.fills]) if self.fills else 0
        }
        
        # Estatísticas de execução
        if self.execution_metrics:
            avg_efficiency = np.mean([m.efficiency_score for m in self.execution_metrics])
            avg_fill_rate = np.mean([m.fill_rate for m in self.execution_metrics])
            avg_implementation_shortfall = np.mean([m.implementation_shortfall for m in self.execution_metrics])
        else:
            avg_efficiency = avg_fill_rate = avg_implementation_shortfall = 0
        
        execution_stats = {
            'average_efficiency_score': avg_efficiency,
            'average_fill_rate': avg_fill_rate,
            'average_implementation_shortfall': avg_implementation_shortfall,
            'total_execution_metrics': len(self.execution_metrics)
        }
        
        return {
            'simulation_time': {
                'start': self.current_time.isoformat() if self.current_time else None,
                'duration_minutes': (self.current_time - (self.current_time - timedelta(hours=1))).total_seconds() / 60 if self.current_time else 0
            },
            'order_statistics': order_stats,
            'fill_statistics': fill_stats,
            'execution_statistics': execution_stats,
            'orders': {k: v['order'].to_dict() for k, v in self.orders.items()},
            'fills': [f.to_dict() for f in self.fills],
            'execution_metrics': [m.to_dict() for m in self.execution_metrics],
            'market_data_summary': self._summarize_market_data()
        }
    
    def _summarize_market_data(self) -> Dict[str, Any]:
        """Resume dados de mercado da simulação"""
        summary = {}
        
        for symbol, stats_list in self.daily_stats.items():
            if stats_list:
                prices = [s['price'] for s in stats_list]
                volumes = [s['volume'] for s in stats_list]
                spreads = [s['spread'] for s in stats_list]
                
                summary[symbol] = {
                    'initial_price': prices[0],
                    'final_price': prices[-1],
                    'min_price': min(prices),
                    'max_price': max(prices),
                    'total_volume': sum(volumes),
                    'average_spread': np.mean(spreads),
                    'volatility': np.std(prices) / np.mean(prices) if prices else 0
                }
        
        return summary
    
    def save_results(self, filepath: str):
        """Salva resultados da simulação"""
        results = self.get_simulation_results()
        
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"💾 Resultados salvos em {filepath}")
    
    def plot_results(self, save_path: str = None):
        """Plota resultados da simulação"""
        if not self.daily_stats:
            logger.warning("⚠️ Sem dados para plotar")
            return
        
        import matplotlib.pyplot as plt
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Plot para cada símbolo
        for i, (symbol, stats) in enumerate(self.daily_stats.items()):
            if i >= 4:  # Máximo 4 símbolos
                break
            
            timestamps = [s['timestamp'] for s in stats]
            prices = [s['price'] for s in stats]
            volumes = [s['volume'] for s in stats]
            
            # Preço
            axes[i, 0].plot(timestamps, prices)
            axes[i, 0].set_title(f'{symbol} - Preço')
            axes[i, 0].set_ylabel('Preço')
            axes[i, 0].grid(True)
            
            # Volume
            axes[i, 1].plot(timestamps, volumes)
            axes[i, 1].set_title(f'{symbol} - Volume')
            axes[i, 1].set_ylabel('Volume')
            axes[i, 1].grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"📊 Gráfico salvo em {save_path}")
        
        plt.show()

# Configuração padrão
DEFAULT_SIMULATION_CONFIG = {
    'market': {
        'spread_bps': 5,
        'depth_levels': 10,
        'base_volatility': 0.02,
        'liquidity_factor': 1.0
    },
    'twap': {
        'duration_minutes': 30,
        'slice_interval': 60
    },
    'vwap': {
        'duration_minutes': 30,
        'volume_profile': 'u_shaped'
    },
    'simulation': {
        'time_step_seconds': 1,
        'max_orders_per_second': 10
    }
}

if __name__ == "__main__":
    # Exemplo de uso
    async def test_execution_simulation():
        """Testa ambiente de simulação de execução"""
        print("🎭 Iniciando Teste do Ambiente de Simulação de Execução")
        print("=" * 60)
        
        # Cria ambiente
        sim_env = ExecutionSimulationEnvironment(DEFAULT_SIMULATION_CONFIG)
        
        # Inicializa simulação
        symbols = ['AAPL', 'MSFT', 'GOOGL']
        initial_prices = {'AAPL': 150.0, 'MSFT': 300.0, 'GOOGL': 2500.0}
        
        sim_env.initialize_simulation(symbols, initial_prices)
        
        # Cria ordens de teste
        orders = [
            Order(
                id="order_1",
                symbol="AAPL",
                side=OrderSide.BUY,
                order_type=OrderType.MARKET,
                quantity=100,
                price=None,
                stop_price=None,
                time_in_force="IOC",
                created_time=datetime.now(),
                updated_time=datetime.now(),
                status=OrderStatus.NEW
            ),
            Order(
                id="order_2",
                symbol="MSFT",
                side=OrderSide.SELL,
                order_type=OrderType.LIMIT,
                quantity=50,
                price=305.0,
                stop_price=None,
                time_in_force="DAY",
                created_time=datetime.now(),
                updated_time=datetime.now(),
                status=OrderStatus.NEW
            ),
            Order(
                id="order_3",
                symbol="GOOGL",
                side=OrderSide.BUY,
                order_type=OrderType.MARKET,
                quantity=10,
                price=None,
                stop_price=None,
                time_in_force="IOC",
                created_time=datetime.now(),
                updated_time=datetime.now(),
                status=OrderStatus.NEW
            )
        ]
        
        # Submete ordens com diferentes algoritmos
        algorithms = ['simple', 'twap', 'vwap']
        
        for order, algorithm in zip(orders, algorithms):
            try:
                order_id = sim_env.submit_order(order, algorithm)
                print(f"📤 Ordem {order_id} submetida com algoritmo {algorithm}")
            except Exception as e:
                print(f"❌ Erro ao submeter ordem {order.id}: {e}")
        
        # Executa simulação
        print(f"\n⏱️ Executando simulação por 5 minutos...")
        results = await sim_env.run_simulation(duration_minutes=5, time_step_seconds=1)
        
        # Mostra resultados
        print(f"\n📊 RESULTADOS DA SIMULAÇÃO:")
        print("=" * 40)
        
        order_stats = results['order_statistics']
        print(f"Ordens Totais: {order_stats['total_orders']}")
        print(f"Ordens Preenchidas: {order_stats['filled_orders']}")
        print(f"Ordens Parcialmente Preenchidas: {order_stats['partially_filled_orders']}")
        
        fill_stats = results['fill_statistics']
        print(f"Fills Totais: {fill_stats['total_fills']}")
        print(f"Volume Total: {fill_stats['total_volume']:.0f}")
        print(f"Comissão Total: ${fill_stats['total_commission']:.2f}")
        print(f"Slippage Médio: {fill_stats['average_slippage']:.4f}")
        
        exec_stats = results['execution_statistics']
        print(f"Score Eficiência Médio: {exec_stats['average_efficiency_score']:.1f}")
        print(f"Taxa de Preenchimento Média: {exec_stats['average_fill_rate']:.2%}")
        print(f"Implementation Shortfall Médio: {exec_stats['average_implementation_shortfall']:.4f}")
        
        # Salva resultados
        sim_env.save_results('execution_simulation_results.json')
        
        # Plota resultados
        sim_env.plot_results('execution_simulation_plot.png')
        
        print("\n💾 Resultados salvos")
        print("✅ Teste concluído com sucesso!")
        
        return sim_env, results
    
    # Executa teste
    sim_env, sim_results = asyncio.run(test_execution_simulation())

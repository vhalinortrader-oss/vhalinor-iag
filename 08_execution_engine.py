# 08_execution_engine.py
"""
Sistema VhalinorTrade - Motor de Execução Autônoma
Conexão com exchanges e execução de ordens com proteções
"""

import asyncio
import aiohttp
import hmac
import hashlib
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import json

class OrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "STOP_LOSS"
    TAKE_PROFIT = "TAKE_PROFIT"
    TRAILING_STOP = "TRAILING_STOP"

class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderStatus(Enum):
    PENDING = "PENDING"
    FILLED = "FILLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"

class ExecutionEngine:
    def __init__(self, config, risk_manager):
        self.config = config
        self.risk_manager = risk_manager
        self.active_orders = {}
        self.order_history = []
        self.exchange_connections = {}
        
    async def connect_binance(self):
        """Inicializa conexão com Binance"""
        self.exchange_connections['binance'] = {
            'api_key': self.config.api.binance_api_key,
            'api_secret': self.config.api.binance_api_secret,
            'base_url': 'https://api.binance.com',
            'testnet_url': 'https://testnet.binance.vision'
        }
        
    async def connect_bybit(self):
        """Inicializa conexão com Bybit"""
        self.exchange_connections['bybit'] = {
            'api_key': self.config.api.bybit_api_key,
            'api_secret': self.config.api.bybit_api_secret,
            'base_url': 'https://api.bybit.com',
            'testnet_url': 'https://api-testnet.bybit.com'
        }
        
    def _generate_signature(self, exchange: str, params: Dict) -> str:
        """Gera assinatura para autenticação"""
        if exchange == 'binance':
            query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            signature = hmac.new(
                self.config.api.binance_api_secret.encode('utf-8'),
                query_string.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            return signature
        # Adicionar outros exchanges conforme necessário
        
    async def place_order(self, symbol: str, side: OrderSide,
                         order_type: OrderType, quantity: float,
                         price: Optional[float] = None,
                         stop_price: Optional[float] = None,
                         exchange: str = 'binance') -> Dict[str, Any]:
        """Executa ordem na exchange"""
        
        # Verificações pré-execução
        if not self._pre_execution_checks(symbol, quantity, side):
            return {'status': 'REJECTED', 'reason': 'Pre-execution checks failed'}
            
        # Prepara parâmetros da ordem
        params = {
            'symbol': symbol,
            'side': side.value,
            'type': order_type.value,
            'quantity': quantity,
            'timestamp': int(time.time() * 1000)
        }
        
        if price:
            params['price'] = price
            
        if stop_price:
            params['stopPrice'] = stop_price
            
        # Adiciona timestamp para assinatura
        params['recvWindow'] = 5000
        
        # Gera assinatura
        signature = self._generate_signature(exchange, params)
        params['signature'] = signature
        
        # Envia ordem
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.exchange_connections[exchange]['base_url']}/api/v3/order"
                headers = {'X-MBX-APIKEY': self.exchange_connections[exchange]['api_key']}
                
                async with session.post(url, params=params, headers=headers) as response:
                    result = await response.json()
                    
                    if 'orderId' in result:
                        order_id = result['orderId']
                        
                        # Registra ordem
                        self.active_orders[order_id] = {
                            'symbol': symbol,
                            'side': side.value,
                            'type': order_type.value,
                            'quantity': quantity,
                            'price': price,
                            'stop_price': stop_price,
                            'status': OrderStatus.PENDING,
                            'exchange': exchange,
                            'timestamp': datetime.now(),
                            'response': result
                        }
                        
                        # Inicia monitoramento
                        asyncio.create_task(self._monitor_order(order_id))
                        
                        return {'status': 'SUCCESS', 'order_id': order_id, 'details': result}
                    else:
                        return {'status': 'FAILED', 'error': result}
                        
        except Exception as e:
            return {'status': 'ERROR', 'message': str(e)}
    
    async def _monitor_order(self, order_id: str):
        """Monitora status da ordem"""
        if order_id not in self.active_orders:
            return
            
        order_info = self.active_orders[order_id]
        exchange = order_info['exchange']
        
        max_checks = 60
        checks = 0
        
        while checks < max_checks:
            try:
                status = await self._check_order_status(order_id, exchange)
                
                if status in [OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.FAILED]:
                    self.active_orders[order_id]['status'] = status
                    
                    if status == OrderStatus.FILLED:
                        await self._on_order_filled(order_id)
                        
                    self.order_history.append(self.active_orders[order_id])
                    break
                    
                await asyncio.sleep(1)
                checks += 1
                
            except Exception as e:
                print(f"Error monitoring order {order_id}: {e}")
                await asyncio.sleep(5)
                checks += 1
                
    async def _check_order_status(self, order_id: str, 
                                 exchange: str) -> OrderStatus:
        """Verifica status da ordem na exchange"""
        # Implementar chamada à API da exchange
        # Simulado para exemplo
        return OrderStatus.FILLED
    
    async def _on_order_filled(self, order_id: str):
        """Ações após ordem executada"""
        order = self.active_orders[order_id]
        
        # Configura stop-loss e take-profit
        if order['side'] == 'BUY':
            # Coloca stop-loss
            stop_loss_price = order['price'] * (1 - self.config.trading.stop_loss_percentage)
            await self.place_order(
                symbol=order['symbol'],
                side=OrderSide.SELL,
                order_type=OrderType.STOP_LOSS,
                quantity=order['quantity'],
                stop_price=stop_loss_price
            )
            
            # Coloca take-profit
            take_profit_price = order['price'] * (1 + self.config.trading.take_profit_percentage)
            await self.place_order(
                symbol=order['symbol'],
                side=OrderSide.SELL,
                order_type=OrderType.TAKE_PROFIT,
                quantity=order['quantity'],
                price=take_profit_price
            )
    
    def _pre_execution_checks(self, symbol: str, quantity: float,
                             side: OrderSide) -> bool:
        """Verificações antes da execução"""
        # Verifica exposição máxima
        exposure = self.risk_manager.calculate_exposure_limits()
        
        if exposure['total_exposure'] >= exposure['max_allowed']:
            return False
            
        # Verifica limite por operação
        trade_value = quantity * self._get_current_price(symbol)
        max_trade_value = self.risk_manager.total_capital * self.config.trading.max_exposure_per_trade
        
        if trade_value > max_trade_value:
            return False
            
        # Verifica condições de mercado
        if self._check_extreme_conditions():
            return False
            
        return True
    
    def _get_current_price(self, symbol: str) -> float:
        """Obtém preço atual do ativo"""
        # Implementar obtenção de preço em tempo real
        return 0.0
    
    def _check_extreme_conditions(self) -> bool:
        """Verifica condições extremas de mercado"""
        # Implementar verificações
        return False
    
    async def emergency_close_all(self):
        """Fecha todas as posições em emergência"""
        for order_id, order in self.active_orders.items():
            if order['status'] == OrderStatus.FILLED:
                # Cancela ordens abertas
                await self._cancel_order(order_id, order['exchange'])
                
                # Fecha posição a mercado
                close_side = OrderSide.SELL if order['side'] == 'BUY' else OrderSide.BUY
                await self.place_order(
                    symbol=order['symbol'],
                    side=close_side,
                    order_type=OrderType.MARKET,
                    quantity=order['quantity']
                )
                
    async def _cancel_order(self, order_id: str, exchange: str):
        """Cancela uma ordem"""
        # Implementar cancelamento
        pass
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Calcula métricas de performance"""
        filled_orders = [o for o in self.order_history 
                        if o['status'] == OrderStatus.FILLED]
        
        if not filled_orders:
            return {}
            
        total_trades = len(filled_orders)
        winning_trades = 0
        total_pnl = 0
        
        for order in filled_orders:
            # Calcular P&L
            # Implementação simplificada
            pass
            
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'win_rate': winning_trades / total_trades if total_trades > 0 else 0,
            'total_pnl': total_pnl
        }
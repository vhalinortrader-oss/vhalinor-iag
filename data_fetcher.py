"""
Módulo de Coleta de Dados em Tempo Real
=====================================
Implementação avançada com WebSocket, ccxt async e múltiplos fontes
"""

import asyncio
import websockets
import json
import time
from typing import Dict, List, Optional, Any, Callable, AsyncGenerator
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
import ccxt.async_support as ccxt
import yfinance as yf
import pandas as pd
import numpy as np
from collections import deque, defaultdict
import threading
import schedule

# Importações condicionais
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    from rich.console import Console
    from rich.progress import Progress, TaskID
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from config import settings
from core import get_logger, log_execution


class DataSourceType(str, Enum):
    """Tipos de fontes de dados"""
    BINANCE = "binance"
    YFINANCE = "yfinance"
    ALPHA_VANTAGE = "alpha_vantage"
    WEBSOCKET = "websocket"
    REDIS_CACHE = "redis_cache"


@dataclass
class MarketData:
    """Estrutura de dados de mercado"""
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    source: str
    timeframe: str = "1m"
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class OrderBookData:
    """Dados do livro de ofertas"""
    symbol: str
    timestamp: datetime
    bids: List[tuple]  # [(price, quantity), ...]
    asks: List[tuple]  # [(price, quantity), ...]
    source: str
    
    def get_best_bid(self) -> Optional[tuple]:
        """Melhor oferta de compra"""
        return self.bids[0] if self.bids else None
    
    def get_best_ask(self) -> Optional[tuple]:
        """Melhor oferta de venda"""
        return self.asks[0] if self.asks else None
    
    def get_spread(self) -> Optional[float]:
        """Spread bid-ask"""
        best_bid = self.get_best_bid()
        best_ask = self.get_best_ask()
        if best_bid and best_ask:
            return best_ask[0] - best_bid[0]
        return None


class DataFetcher:
    """
    Coletor de dados em tempo real com múltiplos fontes
    """
    
    def __init__(self):
        self.logger = get_logger().get_logger("vhalinor.data_fetcher", "data_fetcher")
        self.console = Console() if RICH_AVAILABLE else None
        
        # Cache de dados
        self.price_cache: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.orderbook_cache: Dict[str, OrderBookData] = {}
        
        # Conexões WebSocket
        self.websocket_connections: Dict[str, Any] = {}
        self.ccxt_exchanges: Dict[str, Any] = {}
        
        # Configurações
        self.symbols = settings.trading_symbols
        self.timeframes = ["1m", "5m", "15m", "1h", "4h", "1d"]
        
        # Callbacks para eventos
        self.callbacks: Dict[str, List[Callable]] = {
            "price_update": [],
            "orderbook_update": [],
            "trade_update": [],
            "error": []
        }
        
        # Redis para cache
        self.redis_client = None
        if REDIS_AVAILABLE and settings.cache_backend == "redis":
            self._init_redis()
        
        # Controle de threads
        self.running = False
        self.threads: List[threading.Thread] = []
    
    @log_execution(
        component="data_fetcher",
        operation="init_redis",
        log_exceptions=True
    )
    def _init_redis(self):
        """Inicializa conexão Redis"""
        try:
            self.redis_client = redis.from_url(
                f"redis://{settings.redis_host}:{settings.redis_port}/{settings.redis_db}",
                encoding="utf-8",
                decode_responses=True
            )
            self.logger.info("Redis client initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize Redis: {e}")
            self.redis_client = None
    
    @log_execution(
        component="data_fetcher",
        operation="setup_ccxt_exchanges",
        log_exceptions=True
    )
    async def setup_ccxt_exchanges(self):
        """Configura exchanges CCxt"""
        for symbol in self.symbols:
            try:
                # Detectar exchange baseado no símbolo
                exchange_name = self._detect_exchange_for_symbol(symbol)
                
                if exchange_name == "binance":
                    exchange = ccxt.binance({
                        'apiKey': settings.trading_api_key.get_secret_value() if settings.trading_api_key else None,
                        'secret': settings.trading_api_secret.get_secret_value() if settings.trading_api_secret else None,
                        'sandbox': not settings.is_production(),
                        'enableRateLimit': True,
                        'options': {
                            'defaultType': 'future',  # ou 'spot'
                            'adjustForTimeDifference': True,
                        }
                    })
                
                await exchange.load_markets()
                self.ccxt_exchanges[symbol] = exchange
                self.logger.info(f"CCxt exchange configured for {symbol}")
                
            except Exception as e:
                self.logger.error(f"Failed to setup CCxt for {symbol}: {e}")
    
    def _detect_exchange_for_symbol(self, symbol: str) -> str:
        """Detecta exchange baseado no símbolo"""
        # Lógica simples para detectar exchange
        if any(s in symbol.upper() for s in ['BTC', 'ETH', 'BNB']):
            return "binance"
        return "binance"  # Default
    
    @log_execution(
        component="data_fetcher",
        operation="fetch_historical_data",
        log_args=True,
        log_result=True
    )
    async def fetch_historical_data(
        self,
        symbol: str,
        timeframe: str = "1h",
        limit: int = 1000,
        source: str = "yfinance"
    ) -> pd.DataFrame:
        """
        Busca dados históricos
        
        Args:
            symbol: Símbolo do ativo
            timeframe: Timeframe dos dados
            limit: Número de candles
            source: Fonte dos dados
        
        Returns:
            DataFrame com dados históricos
        """
        try:
            if source == "yfinance":
                return await self._fetch_yfinance_data(symbol, timeframe, limit)
            elif source == "ccxt":
                return await self._fetch_ccxt_data(symbol, timeframe, limit)
            else:
                raise ValueError(f"Unsupported data source: {source}")
                
        except Exception as e:
            self.logger.error(f"Failed to fetch historical data for {symbol}: {e}")
            return pd.DataFrame()
    
    async def _fetch_yfinance_data(
        self,
        symbol: str,
        timeframe: str,
        limit: int
    ) -> pd.DataFrame:
        """Busca dados usando yfinance"""
        try:
            # Converter timeframe para yfinance
            yf_interval = self._convert_timeframe_yfinance(timeframe)
            
            # Download de dados
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=f"{limit}d", interval=yf_interval)
            
            # Processar dados
            df = data.reset_index()
            df.columns = [col.lower().replace(' ', '_') for col in df.columns]
            
            self.logger.info(f"Fetched {len(df)} candles from yfinance for {symbol}")
            return df
            
        except Exception as e:
            self.logger.error(f"yfinance error for {symbol}: {e}")
            return pd.DataFrame()
    
    async def _fetch_ccxt_data(
        self,
        symbol: str,
        timeframe: str,
        limit: int
    ) -> pd.DataFrame:
        """Busca dados usando CCxt"""
        try:
            if symbol not in self.ccxt_exchanges:
                await self.setup_ccxt_exchanges()
            
            exchange = self.ccxt_exchanges[symbol]
            
            # Converter timeframe
            ccxt_timeframe = self._convert_timeframe_ccxt(timeframe)
            
            # Buscar OHLCV
            ohlcv = await exchange.fetch_ohlcv(
                symbol,
                timeframe=ccxt_timeframe,
                limit=limit
            )
            
            # Converter para DataFrame
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            self.logger.info(f"Fetched {len(df)} candles from CCxt for {symbol}")
            return df
            
        except Exception as e:
            self.logger.error(f"CCxt error for {symbol}: {e}")
            return pd.DataFrame()
    
    def _convert_timeframe_yfinance(self, timeframe: str) -> str:
        """Converte timeframe para formato yfinance"""
        mapping = {
            "1m": "1m",
            "5m": "5m",
            "15m": "15m",
            "1h": "1h",
            "4h": "1d",  # yfinance não tem 4h
            "1d": "1d"
        }
        return mapping.get(timeframe, "1h")
    
    def _convert_timeframe_ccxt(self, timeframe: str) -> str:
        """Converte timeframe para formato CCxt"""
        mapping = {
            "1m": "1m",
            "5m": "5m",
            "15m": "15m",
            "1h": "1h",
            "4h": "4h",
            "1d": "1d"
        }
        return mapping.get(timeframe, "1h")
    
    @log_execution(
        component="data_fetcher",
        operation="start_websocket_stream",
        log_exceptions=True
    )
    async def start_websocket_stream(self, symbol: str):
        """Inicia stream WebSocket para um símbolo"""
        try:
            if not settings.websocket_enabled:
                self.logger.warning("WebSocket streaming is disabled")
                return
            
            # URL do WebSocket Binance
            ws_url = f"wss://stream.binance.com:9443/ws/{symbol.lower()}@kline_{self._convert_timeframe_ccxt('1m')}"
            
            async with websockets.connect(ws_url) as websocket:
                self.websocket_connections[symbol] = websocket
                self.logger.info(f"WebSocket connected for {symbol}")
                
                async for message in websocket:
                    try:
                        data = json.loads(message)
                        await self._process_websocket_data(symbol, data)
                    except Exception as e:
                        self.logger.error(f"Error processing WebSocket data: {e}")
                        
        except Exception as e:
            self.logger.error(f"WebSocket connection failed for {symbol}: {e}")
    
    async def _process_websocket_data(self, symbol: str, data: Dict[str, Any]):
        """Processa dados recebidos via WebSocket"""
        if 'k' in data:
            kline = data['k']
            
            # Criar objeto MarketData
            market_data = MarketData(
                symbol=symbol,
                timestamp=datetime.fromtimestamp(kline['t'] / 1000),
                open=float(kline['o']),
                high=float(kline['h']),
                low=float(kline['l']),
                close=float(kline['c']),
                volume=float(kline['v']),
                source="websocket",
                timeframe="1m"
            )
            
            # Adicionar ao cache
            self.price_cache[symbol].append(market_data)
            
            # Executar callbacks
            await self._execute_callbacks("price_update", market_data)
            
            # Salvar no Redis se disponível
            if self.redis_client:
                await self._save_to_redis(market_data)
    
    async def _save_to_redis(self, data: MarketData):
        """Salva dados no Redis"""
        try:
            key = f"market_data:{data.symbol}:{data.timeframe}"
            value = json.dumps(data.to_dict())
            
            await self.redis_client.setex(
                key,
                settings.cache_ttl,
                value
            )
        except Exception as e:
            self.logger.error(f"Failed to save to Redis: {e}")
    
    def add_callback(self, event_type: str, callback: Callable):
        """Adiciona callback para eventos"""
        if event_type in self.callbacks:
            self.callbacks[event_type].append(callback)
        else:
            self.logger.warning(f"Unknown event type: {event_type}")
    
    async def _execute_callbacks(self, event_type: str, data: Any):
        """Executa callbacks de um evento"""
        for callback in self.callbacks.get(event_type, []):
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(data)
                else:
                    callback(data)
            except Exception as e:
                self.logger.error(f"Callback error for {event_type}: {e}")
    
    @log_execution(
        component="data_fetcher",
        operation="get_latest_price",
        log_args=True,
        log_result=True
    )
    def get_latest_price(self, symbol: str) -> Optional[MarketData]:
        """
        Obtém preço mais recente do cache
        
        Args:
            symbol: Símbolo do ativo
        
        Returns:
            Dados mais recentes ou None
        """
        if symbol in self.price_cache and self.price_cache[symbol]:
            return self.price_cache[symbol][-1]
        return None
    
    def get_price_history(
        self,
        symbol: str,
        limit: int = 100
    ) -> List[MarketData]:
        """
        Obtém histórico de preços do cache
        
        Args:
            symbol: Símbolo do ativo
            limit: Número de registros
        
        Returns:
            Lista de dados históricos
        """
        if symbol in self.price_cache:
            return list(self.price_cache[symbol])[-limit:]
        return []
    
    @log_execution(
        component="data_fetcher",
        operation="start_real_time_collection",
        log_exceptions=True
    )
    async def start_real_time_collection(self):
        """Inicia coleta de dados em tempo real"""
        self.running = True
        self.logger.info("Starting real-time data collection")
        
        # Iniciar streams WebSocket para todos os símbolos
        tasks = []
        for symbol in self.symbols:
            task = asyncio.create_task(self.start_websocket_stream(symbol))
            tasks.append(task)
        
        # Aguardar todas as tasks
        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            self.logger.error(f"Real-time collection error: {e}")
        finally:
            self.running = False
    
    def stop_real_time_collection(self):
        """Para coleta de dados em tempo real"""
        self.running = False
        
        # Fechar conexões WebSocket
        for symbol, websocket in self.websocket_connections.items():
            try:
                asyncio.create_task(websocket.close())
            except Exception as e:
                self.logger.error(f"Error closing WebSocket for {symbol}: {e}")
        
        self.websocket_connections.clear()
        self.logger.info("Real-time data collection stopped")
    
    @log_execution(
        component="data_fetcher",
        operation="get_market_overview",
        log_args=True,
        log_result=True
    )
    async def get_market_overview(self) -> Dict[str, Any]:
        """
        Obtém visão geral do mercado
        
        Returns:
            Dicionário com informações do mercado
        """
        overview = {
            "timestamp": datetime.now().isoformat(),
            "symbols": {},
            "total_volume": 0,
            "market_cap": 0,
            "active_streams": len(self.websocket_connections)
        }
        
        for symbol in self.symbols:
            latest_price = self.get_latest_price(symbol)
            if latest_price:
                overview["symbols"][symbol] = {
                    "price": latest_price.close,
                    "change_24h": self._calculate_24h_change(symbol),
                    "volume_24h": latest_price.volume,
                    "timestamp": latest_price.timestamp.isoformat()
                }
                overview["total_volume"] += latest_price.volume
        
        return overview
    
    def _calculate_24h_change(self, symbol: str) -> Optional[float]:
        """Calcula mudança de 24 horas"""
        history = self.get_price_history(symbol, limit=1440)  # 24h em minutos
        
        if len(history) < 2:
            return None
        
        current_price = history[-1].close
        old_price = history[0].close
        
        return ((current_price - old_price) / old_price) * 100
    
    @log_execution(
        component="data_fetcher",
        operation="get_technical_indicators",
        log_args=True,
        log_result=True
    )
    def get_technical_indicators(
        self,
        symbol: str,
        indicators: List[str] = None
    ) -> Dict[str, Any]:
        """
        Calcula indicadores técnicos
        
        Args:
            symbol: Símbolo do ativo
            indicators: Lista de indicadores desejados
        
        Returns:
            Dicionário com indicadores calculados
        """
        if indicators is None:
            indicators = ["sma", "ema", "rsi", "macd", "bollinger"]
        
        history = self.get_price_history(symbol, limit=200)
        if len(history) < 20:
            return {}
        
        closes = [data.close for data in history]
        highs = [data.high for data in history]
        lows = [data.low for data in history]
        volumes = [data.volume for data in history]
        
        result = {}
        
        try:
            if "sma" in indicators:
                result["sma_20"] = self._calculate_sma(closes, 20)
                result["sma_50"] = self._calculate_sma(closes, 50)
            
            if "ema" in indicators:
                result["ema_20"] = self._calculate_ema(closes, 20)
                result["ema_50"] = self._calculate_ema(closes, 50)
            
            if "rsi" in indicators:
                result["rsi"] = self._calculate_rsi(closes, 14)
            
            if "macd" in indicators:
                macd_data = self._calculate_macd(closes)
                result.update(macd_data)
            
            if "bollinger" in indicators:
                bb_data = self._calculate_bollinger_bands(closes, 20, 2)
                result.update(bb_data)
            
            self.logger.info(f"Calculated {len(result)} indicators for {symbol}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error calculating indicators for {symbol}: {e}")
            return {}
    
    def _calculate_sma(self, prices: List[float], period: int) -> float:
        """Calcula Simple Moving Average"""
        if len(prices) < period:
            return 0.0
        return sum(prices[-period:]) / period
    
    def _calculate_ema(self, prices: List[float], period: int) -> float:
        """Calcula Exponential Moving Average"""
        if len(prices) < period:
            return prices[-1] if prices else 0.0
        
        multiplier = 2 / (period + 1)
        ema = prices[0]
        
        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calcula Relative Strength Index"""
        if len(prices) < period + 1:
            return 50.0
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calculate_macd(self, prices: List[float]) -> Dict[str, float]:
        """Calcula MACD"""
        if len(prices) < 26:
            return {"macd": 0.0, "signal": 0.0, "histogram": 0.0}
        
        ema_12 = self._calculate_ema(prices, 12)
        ema_26 = self._calculate_ema(prices, 26)
        
        macd_line = ema_12 - ema_26
        signal_line = self._calculate_ema([macd_line], 9)
        histogram = macd_line - signal_line
        
        return {
            "macd": macd_line,
            "signal": signal_line,
            "histogram": histogram
        }
    
    def _calculate_bollinger_bands(
        self,
        prices: List[float],
        period: int = 20,
        std_dev: float = 2.0
    ) -> Dict[str, float]:
        """Calcula Bandas de Bollinger"""
        if len(prices) < period:
            return {"upper": 0.0, "middle": 0.0, "lower": 0.0}
        
        middle = self._calculate_sma(prices, period)
        recent_prices = prices[-period:]
        
        variance = sum((price - middle) ** 2 for price in recent_prices) / period
        std_dev = variance ** 0.5
        
        upper = middle + (std_dev * std_dev)
        lower = middle - (std_dev * std_dev)
        
        return {
            "upper": upper,
            "middle": middle,
            "lower": lower
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status do coletor de dados"""
        return {
            "running": self.running,
            "symbols_tracked": len(self.symbols),
            "active_websockets": len(self.websocket_connections),
            "cache_size": {
                symbol: len(cache) for symbol, cache in self.price_cache.items()
            },
            "redis_connected": self.redis_client is not None,
            "last_update": datetime.now().isoformat()
        }


# Instância global do coletor de dados
_data_fetcher: Optional[DataFetcher] = None


def get_data_fetcher() -> DataFetcher:
    """Obtém instância global do DataFetcher"""
    global _data_fetcher
    if _data_fetcher is None:
        _data_fetcher = DataFetcher()
    return _data_fetcher


# Exportações principais
__all__ = [
    "DataFetcher",
    "MarketData",
    "OrderBookData",
    "DataSourceType",
    "get_data_fetcher"
]

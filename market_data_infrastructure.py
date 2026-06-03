"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║           INFRAESTRUTURA DE COLETA E ARMAZENAMENTO DE DADOS DE MERCADO        ║
║                 Componente 1: Sistema de Dados Financeiros                     ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import asyncio
import aiohttp
import websockets
import sqlite3
import psycopg2
import pymongo
import redis
import pandas as pd
import numpy as np
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
import hashlib
import pickle
import gzip
import os
from pathlib import Path

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('MarketDataInfrastructure')

class DataSource(Enum):
    """Fontes de dados de mercado"""
    ALPHAVANTAGE = "alphavantage"
    YAHOO_FINANCE = "yahoo_finance"
    BINANCE = "binance"
    COINBASE = "coinbase"
    REUTERS = "reuters"
    BLOOMBERG = "bloomberg"
    QUANDL = "quandl"
    IEX = "iex"
    FINNHUB = "finnhub"
    POLYGON = "polygon"

class DataType(Enum):
    """Tipos de dados financeiros"""
    PRICE = "price"
    VOLUME = "volume"
    ORDER_BOOK = "order_book"
    TRADES = "trades"
    NEWS = "news"
    ECONOMIC = "economic"
    SOCIAL = "social"
    OPTIONS = "options"
    FUTURES = "futures"
    FOREX = "forex"

class DataFrequency(Enum):
    """Frequências de dados"""
    TICK = "tick"
    SECOND = "second"
    MINUTE = "minute"
    HOUR = "hour"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

@dataclass
class MarketDataPoint:
    """Ponto de dado de mercado"""
    symbol: str
    timestamp: datetime
    open_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    close_price: Optional[float] = None
    volume: Optional[float] = None
    bid_price: Optional[float] = None
    ask_price: Optional[float] = None
    bid_size: Optional[float] = None
    ask_size: Optional[float] = None
    data_source: DataSource = DataSource.YAHOO_FINANCE
    data_type: DataType = DataType.PRICE
    frequency: DataFrequency = DataFrequency.DAILY
    quality_score: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'symbol': self.symbol,
            'timestamp': self.timestamp.isoformat(),
            'open_price': self.open_price,
            'high_price': self.high_price,
            'low_price': self.low_price,
            'close_price': self.close_price,
            'volume': self.volume,
            'bid_price': self.bid_price,
            'ask_price': self.ask_price,
            'bid_size': self.bid_size,
            'ask_size': self.ask_size,
            'data_source': self.data_source.value,
            'data_type': self.data_type.value,
            'frequency': self.frequency.value,
            'quality_score': self.quality_score,
            'metadata': self.metadata
        }

@dataclass
class NewsDataPoint:
    """Ponto de dado de notícia"""
    id: str
    title: str
    content: str
    source: str
    timestamp: datetime
    sentiment_score: Optional[float] = None
    relevance_score: float = 1.0
    symbols_mentioned: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class MarketDataCollector:
    """Coletor de dados de mercado com múltiplas fontes"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session = None
        self.websocket_connections = {}
        self.data_queue = asyncio.Queue(maxsize=10000)
        self.is_running = False
        self.subscribers = []
        self.rate_limiters = {}
        self.cache = {}
        self.cache_ttl = 60  # segundos
        
        # Configurações de APIs
        self.api_keys = config.get('api_keys', {})
        self.base_urls = {
            DataSource.ALPHAVANTAGE: "https://www.alphavantage.co/query",
            DataSource.YAHOO_FINANCE: "https://query1.finance.yahoo.com/v8/finance/chart/",
            DataSource.BINANCE: "https://api.binance.com/api/v3",
            DataSource.COINBASE: "https://api.pro.coinbase.com",
            DataSource.FINNHUB: "https://finnhub.io/api/v1",
            DataSource.POLYGON: "https://api.polygon.io/v2"
        }
        
        logger.info("📊 Coletor de dados de mercado inicializado")
    
    async def start(self):
        """Inicia o coletor de dados"""
        if self.is_running:
            logger.warning("Coletor já está em execução")
            return
        
        self.is_running = True
        self.session = aiohttp.ClientSession()
        
        # Inicia tarefas de coleta
        tasks = []
        for source_config in self.config.get('sources', []):
            if source_config.get('enabled', True):
                tasks.append(
                    asyncio.create_task(
                        self._collect_from_source(source_config)
                    )
                )
        
        # Inicia processamento da fila
        tasks.append(asyncio.create_task(self._process_data_queue()))
        
        logger.info("🚀 Coletor de dados iniciado")
        await asyncio.gather(*tasks)
    
    async def stop(self):
        """Para o coletor de dados"""
        self.is_running = False
        if self.session:
            await self.session.close()
        
        # Fecha conexões websocket
        for ws in self.websocket_connections.values():
            await ws.close()
        
        logger.info("🛑 Coletor de dados parado")
    
    async def _collect_from_source(self, source_config: Dict[str, Any]):
        """Coleta dados de uma fonte específica"""
        source = DataSource(source_config['source'])
        symbols = source_config.get('symbols', [])
        frequency = DataFrequency(source_config.get('frequency', 'daily'))
        
        while self.is_running:
            try:
                if source == DataSource.YAHOO_FINANCE:
                    await self._collect_yahoo_finance(symbols, frequency)
                elif source == DataSource.BINANCE:
                    await self._collect_binance(symbols, frequency)
                elif source == DataSource.ALPHAVANTAGE:
                    await self._collect_alphavantage(symbols, frequency)
                elif source == DataSource.FINNHUB:
                    await self._collect_finnhub(symbols, frequency)
                
                # Espera baseada na frequência
                await asyncio.sleep(self._get_sleep_time(frequency))
                
            except Exception as e:
                logger.error(f"Erro na coleta da fonte {source.value}: {e}")
                await asyncio.sleep(5)
    
    async def _collect_yahoo_finance(self, symbols: List[str], frequency: DataFrequency):
        """Coleta dados do Yahoo Finance"""
        for symbol in symbols:
            try:
                # Verifica cache
                cache_key = f"yahoo_{symbol}_{frequency.value}"
                if cache_key in self.cache:
                    cached_time, cached_data = self.cache[cache_key]
                    if time.time() - cached_time < self.cache_ttl:
                        continue
                
                # Monta URL
                interval = self._get_yahoo_interval(frequency)
                url = f"{self.base_urls[DataSource.YAHOO_FINANCE]}{symbol}"
                params = {
                    'interval': interval,
                    'range': '1d' if frequency != DataFrequency.DAILY else '1mo'
                }
                
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        market_data = self._parse_yahoo_data(symbol, data, frequency)
                        
                        # Atualiza cache
                        self.cache[cache_key] = (time.time(), market_data)
                        
                        # Envia para a fila
                        for data_point in market_data:
                            await self.data_queue.put(data_point)
                
                # Rate limiting
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Erro ao coletar do Yahoo Finance {symbol}: {e}")
    
    async def _collect_binance(self, symbols: List[str], frequency: DataFrequency):
        """Coleta dados da Binance"""
        for symbol in symbols:
            try:
                # Converte símbolo para formato Binance
                binance_symbol = symbol.replace('/', '').upper()
                
                # Determina o intervalo
                interval = self._get_binance_interval(frequency)
                
                url = f"{self.base_urls[DataSource.BINANCE]}/klines"
                params = {
                    'symbol': binance_symbol,
                    'interval': interval,
                    'limit': 100
                }
                
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        market_data = self._parse_binance_data(symbol, data, frequency)
                        
                        for data_point in market_data:
                            await self.data_queue.put(data_point)
                
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Erro ao coletar da Binance {symbol}: {e}")
    
    async def _collect_alphavantage(self, symbols: List[str], frequency: DataFrequency):
        """Coleta dados do Alpha Vantage"""
        api_key = self.api_keys.get('alphavantage')
        if not api_key:
            logger.warning("API Key do Alpha Vantage não configurada")
            return
        
        for symbol in symbols:
            try:
                function = "TIME_SERIES_DAILY" if frequency == DataFrequency.DAILY else "TIME_SERIES_INTRADAY"
                url = self.base_urls[DataSource.ALPHAVANTAGE]
                params = {
                    'function': function,
                    'symbol': symbol,
                    'apikey': api_key,
                    'outputsize': 'compact'
                }
                
                if frequency != DataFrequency.DAILY:
                    params['interval'] = self._get_alphavantage_interval(frequency)
                
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        market_data = self._parse_alphavantage_data(symbol, data, frequency)
                        
                        for data_point in market_data:
                            await self.data_queue.put(data_point)
                
                # Rate limiting do Alpha Vantage (5 chamadas por minuto)
                await asyncio.sleep(12)
                
            except Exception as e:
                logger.error(f"Erro ao coletar do Alpha Vantage {symbol}: {e}")
    
    async def _collect_finnhub(self, symbols: List[str], frequency: DataFrequency):
        """Coleta dados do Finnhub"""
        api_key = self.api_keys.get('finnhub')
        if not api_key:
            logger.warning("API Key do Finnhub não configurada")
            return
        
        for symbol in symbols:
            try:
                resolution = self._get_finnhub_resolution(frequency)
                url = f"{self.base_urls[DataSource.FINNHUB]}/stock/candle"
                params = {
                    'symbol': symbol,
                    'resolution': resolution,
                    'from': int((datetime.now() - timedelta(days=30)).timestamp()),
                    'to': int(datetime.now().timestamp()),
                    'token': api_key
                }
                
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('s') == 'ok':
                            market_data = self._parse_finnhub_data(symbol, data, frequency)
                            
                            for data_point in market_data:
                                await self.data_queue.put(data_point)
                
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Erro ao coletar do Finnhub {symbol}: {e}")
    
    async def _collect_news_data(self):
        """Coleta dados de notícias em tempo real"""
        news_sources = self.config.get('news_sources', [])
        
        while self.is_running:
            try:
                for source_config in news_sources:
                    if source_config.get('enabled', True):
                        news_data = await self._fetch_news_from_source(source_config)
                        for news_item in news_data:
                            await self.data_queue.put(news_item)
                
                await asyncio.sleep(60)  # Coleta de notícias a cada minuto
                
            except Exception as e:
                logger.error(f"Erro na coleta de notícias: {e}")
                await asyncio.sleep(30)
    
    async def _process_data_queue(self):
        """Processa a fila de dados"""
        while self.is_running:
            try:
                data_point = await asyncio.wait_for(
                    self.data_queue.get(), 
                    timeout=1.0
                )
                
                # Notifica subscribers
                for subscriber in self.subscribers:
                    try:
                        if asyncio.iscoroutinefunction(subscriber):
                            await subscriber(data_point)
                        else:
                            subscriber(data_point)
                    except Exception as e:
                        logger.error(f"Erro ao notificar subscriber: {e}")
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Erro ao processar fila de dados: {e}")
    
    def subscribe(self, callback):
        """Adiciona um subscriber para receber dados"""
        self.subscribers.append(callback)
        logger.info(f"Subscriber adicionado. Total: {len(self.subscribers)}")
    
    def unsubscribe(self, callback):
        """Remove um subscriber"""
        if callback in self.subscribers:
            self.subscribers.remove(callback)
            logger.info(f"Subscriber removido. Total: {len(self.subscribers)}")
    
    # Métodos auxiliares
    def _get_sleep_time(self, frequency: DataFrequency) -> float:
        """Retorna tempo de espera baseado na frequência"""
        sleep_times = {
            DataFrequency.TICK: 0.001,
            DataFrequency.SECOND: 1,
            DataFrequency.MINUTE: 60,
            DataFrequency.HOUR: 3600,
            DataFrequency.DAILY: 86400
        }
        return sleep_times.get(frequency, 60)
    
    def _get_yahoo_interval(self, frequency: DataFrequency) -> str:
        """Converte frequência para intervalo do Yahoo Finance"""
        intervals = {
            DataFrequency.MINUTE: "1m",
            DataFrequency.HOUR: "1h",
            DataFrequency.DAILY: "1d"
        }
        return intervals.get(frequency, "1d")
    
    def _get_binance_interval(self, frequency: DataFrequency) -> str:
        """Converte frequência para intervalo da Binance"""
        intervals = {
            DataFrequency.MINUTE: "1m",
            DataFrequency.HOUR: "1h",
            DataFrequency.DAILY: "1d"
        }
        return intervals.get(frequency, "1d")
    
    def _get_alphavantage_interval(self, frequency: DataFrequency) -> str:
        """Converte frequência para intervalo do Alpha Vantage"""
        intervals = {
            DataFrequency.MINUTE: "1min",
            DataFrequency.HOUR: "60min"
        }
        return intervals.get(frequency, "60min")
    
    def _get_finnhub_resolution(self, frequency: DataFrequency) -> str:
        """Converte frequência para resolução do Finnhub"""
        resolutions = {
            DataFrequency.MINUTE: "1",
            DataFrequency.HOUR: "60",
            DataFrequency.DAILY: "D"
        }
        return resolutions.get(frequency, "D")
    
    def _parse_yahoo_data(self, symbol: str, data: Dict, frequency: DataFrequency) -> List[MarketDataPoint]:
        """Parse de dados do Yahoo Finance"""
        result = []
        
        try:
            chart = data.get('chart', {})
            result_data = chart.get('result', [])
            
            if not result_data:
                return result
            
            timestamps = result_data[0].get('timestamp', [])
            indicators = result_data[0].get('indicators', {})
            quote = indicators.get('quote', [{}])[0]
            
            for i, ts in enumerate(timestamps):
                data_point = MarketDataPoint(
                    symbol=symbol,
                    timestamp=datetime.fromtimestamp(ts),
                    open_price=quote.get('open', [])[i],
                    high_price=quote.get('high', [])[i],
                    low_price=quote.get('low', [])[i],
                    close_price=quote.get('close', [])[i],
                    volume=quote.get('volume', [])[i],
                    data_source=DataSource.YAHOO_FINANCE,
                    data_type=DataType.PRICE,
                    frequency=frequency
                )
                result.append(data_point)
                
        except Exception as e:
            logger.error(f"Erro ao parsear dados do Yahoo Finance: {e}")
        
        return result
    
    def _parse_binance_data(self, symbol: str, data: List, frequency: DataFrequency) -> List[MarketDataPoint]:
        """Parse de dados da Binance"""
        result = []
        
        try:
            for item in data:
                data_point = MarketDataPoint(
                    symbol=symbol,
                    timestamp=datetime.fromtimestamp(item[0] / 1000),
                    open_price=float(item[1]),
                    high_price=float(item[2]),
                    low_price=float(item[3]),
                    close_price=float(item[4]),
                    volume=float(item[5]),
                    data_source=DataSource.BINANCE,
                    data_type=DataType.PRICE,
                    frequency=frequency
                )
                result.append(data_point)
                
        except Exception as e:
            logger.error(f"Erro ao parsear dados da Binance: {e}")
        
        return result
    
    def _parse_alphavantage_data(self, symbol: str, data: Dict, frequency: DataFrequency) -> List[MarketDataPoint]:
        """Parse de dados do Alpha Vantage"""
        result = []
        
        try:
            time_series_key = f"Time Series ({frequency.value.capitalize()})"
            time_series = data.get(time_series_key, {})
            
            for timestamp_str, values in time_series.items():
                data_point = MarketDataPoint(
                    symbol=symbol,
                    timestamp=datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S"),
                    open_price=float(values.get('1. open', 0)),
                    high_price=float(values.get('2. high', 0)),
                    low_price=float(values.get('3. low', 0)),
                    close_price=float(values.get('4. close', 0)),
                    volume=float(values.get('5. volume', 0)),
                    data_source=DataSource.ALPHAVANTAGE,
                    data_type=DataType.PRICE,
                    frequency=frequency
                )
                result.append(data_point)
                
        except Exception as e:
            logger.error(f"Erro ao parsear dados do Alpha Vantage: {e}")
        
        return result
    
    def _parse_finnhub_data(self, symbol: str, data: Dict, frequency: DataFrequency) -> List[MarketDataPoint]:
        """Parse de dados do Finnhub"""
        result = []
        
        try:
            timestamps = data.get('t', [])
            opens = data.get('o', [])
            highs = data.get('h', [])
            lows = data.get('l', [])
            closes = data.get('c', [])
            volumes = data.get('v', [])
            
            for i, ts in enumerate(timestamps):
                data_point = MarketDataPoint(
                    symbol=symbol,
                    timestamp=datetime.fromtimestamp(ts),
                    open_price=opens[i] if i < len(opens) else None,
                    high_price=highs[i] if i < len(highs) else None,
                    low_price=lows[i] if i < len(lows) else None,
                    close_price=closes[i] if i < len(closes) else None,
                    volume=volumes[i] if i < len(volumes) else None,
                    data_source=DataSource.FINNHUB,
                    data_type=DataType.PRICE,
                    frequency=frequency
                )
                result.append(data_point)
                
        except Exception as e:
            logger.error(f"Erro ao parsear dados do Finnhub: {e}")
        
        return result

class MarketDataStorage:
    """Sistema de armazenamento de dados de mercado"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connections = {}
        self.compression_enabled = config.get('compression', True)
        self.partitioning_enabled = config.get('partitioning', True)
        
        # Inicializa conexões
        self._initialize_connections()
        
        logger.info("💾 Sistema de armazenamento inicializado")
    
    def _initialize_connections(self):
        """Inicializa conexões com bancos de dados"""
        try:
            # SQLite para dados locais
            if 'sqlite' in self.config:
                sqlite_config = self.config['sqlite']
                self.connections['sqlite'] = sqlite3.connect(
                    sqlite_config['database'],
                    check_same_thread=False
                )
                self._create_sqlite_tables()
            
            # PostgreSQL para dados estruturados
            if 'postgresql' in self.config:
                pg_config = self.config['postgresql']
                self.connections['postgresql'] = psycopg2.connect(
                    host=pg_config['host'],
                    database=pg_config['database'],
                    user=pg_config['user'],
                    password=pg_config['password'],
                    port=pg_config.get('port', 5432)
                )
                self._create_postgresql_tables()
            
            # MongoDB para dados não estruturados
            if 'mongodb' in self.config:
                mongo_config = self.config['mongodb']
                client = pymongo.MongoClient(
                    f"mongodb://{mongo_config['host']}:{mongo_config.get('port', 27017)}"
                )
                self.connections['mongodb'] = client[mongo_config['database']]
            
            # Redis para cache e dados em tempo real
            if 'redis' in self.config:
                redis_config = self.config['redis']
                self.connections['redis'] = redis.Redis(
                    host=redis_config['host'],
                    port=redis_config.get('port', 6379),
                    db=redis_config.get('db', 0),
                    decode_responses=True
                )
                
        except Exception as e:
            logger.error(f"Erro ao inicializar conexões: {e}")
    
    def _create_sqlite_tables(self):
        """Cria tabelas no SQLite"""
        conn = self.connections['sqlite']
        cursor = conn.cursor()
        
        # Tabela de preços
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                open_price REAL,
                high_price REAL,
                low_price REAL,
                close_price REAL,
                volume REAL,
                data_source TEXT,
                data_type TEXT,
                frequency TEXT,
                quality_score REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Índices
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_market_prices_symbol_timestamp 
            ON market_prices(symbol, timestamp)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_market_prices_timestamp 
            ON market_prices(timestamp)
        ''')
        
        conn.commit()
        logger.info("Tabelas SQLite criadas")
    
    def _create_postgresql_tables(self):
        """Cria tabelas no PostgreSQL"""
        conn = self.connections['postgresql']
        cursor = conn.cursor()
        
        # Tabela de preços com particionamento
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_prices (
                id SERIAL PRIMARY KEY,
                symbol VARCHAR(20) NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                open_price DECIMAL(15,8),
                high_price DECIMAL(15,8),
                low_price DECIMAL(15,8),
                close_price DECIMAL(15,8),
                volume BIGINT,
                data_source VARCHAR(50),
                data_type VARCHAR(20),
                frequency VARCHAR(20),
                quality_score DECIMAL(3,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Índices
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_market_prices_symbol_timestamp 
            ON market_prices(symbol, timestamp)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_market_prices_timestamp 
            ON market_prices(timestamp)
        ''')
        
        conn.commit()
        logger.info("Tabelas PostgreSQL criadas")
    
    async def store_market_data(self, data_point: MarketDataPoint):
        """Armazena um ponto de dado de mercado"""
        try:
            # SQLite para backup local
            if 'sqlite' in self.connections:
                await self._store_sqlite(data_point)
            
            # PostgreSQL para consultas analíticas
            if 'postgresql' in self.connections:
                await self._store_postgresql(data_point)
            
            # MongoDB para dados flexíveis
            if 'mongodb' in self.connections:
                await self._store_mongodb(data_point)
            
            # Redis para cache em tempo real
            if 'redis' in self.connections:
                await self._store_redis(data_point)
                
        except Exception as e:
            logger.error(f"Erro ao armazenar dados: {e}")
    
    async def _store_sqlite(self, data_point: MarketDataPoint):
        """Armazena no SQLite"""
        conn = self.connections['sqlite']
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO market_prices 
            (symbol, timestamp, open_price, high_price, low_price, close_price, 
             volume, data_source, data_type, frequency, quality_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data_point.symbol,
            data_point.timestamp,
            data_point.open_price,
            data_point.high_price,
            data_point.low_price,
            data_point.close_price,
            data_point.volume,
            data_point.data_source.value,
            data_point.data_type.value,
            data_point.frequency.value,
            data_point.quality_score
        ))
        
        conn.commit()
    
    async def _store_postgresql(self, data_point: MarketDataPoint):
        """Armazena no PostgreSQL"""
        conn = self.connections['postgresql']
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO market_prices 
            (symbol, timestamp, open_price, high_price, low_price, close_price, 
             volume, data_source, data_type, frequency, quality_score)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            data_point.symbol,
            data_point.timestamp,
            data_point.open_price,
            data_point.high_price,
            data_point.low_price,
            data_point.close_price,
            data_point.volume,
            data_point.data_source.value,
            data_point.data_type.value,
            data_point.frequency.value,
            data_point.quality_score
        ))
        
        conn.commit()
    
    async def _store_mongodb(self, data_point: MarketDataPoint):
        """Armazena no MongoDB"""
        db = self.connections['mongodb']
        collection = db['market_data']
        
        document = data_point.to_dict()
        if self.partitioning_enabled:
            # Particiona por data
            partition_key = data_point.timestamp.strftime("%Y_%m")
            collection = db[f'market_data_{partition_key}']
        
        collection.insert_one(document)
    
    async def _store_redis(self, data_point: MarketDataPoint):
        """Armazena no Redis para cache"""
        redis_client = self.connections['redis']
        
        # Key para o dado mais recente
        latest_key = f"latest:{data_point.symbol}"
        
        # Key para série temporal
        timeseries_key = f"timeseries:{data_point.symbol}"
        
        # Armazena dado mais recente
        latest_data = {
            'symbol': data_point.symbol,
            'timestamp': data_point.timestamp.isoformat(),
            'price': data_point.close_price,
            'volume': data_point.volume,
            'source': data_point.data_source.value
        }
        
        redis_client.setex(
            latest_key, 
            timedelta(minutes=5), 
            json.dumps(latest_data)
        )
        
        # Adiciona à série temporal
        score = data_point.timestamp.timestamp()
        member = json.dumps(data_point.to_dict())
        
        if self.compression_enabled:
            member = gzip.compress(member.encode())
        
        redis_client.zadd(timeseries_key, {member: score})
        
        # Mantém apenas últimos 1000 pontos
        redis_client.zremrangebyrank(timeseries_key, 0, -1001)
    
    async def retrieve_data(self, symbol: str, start_time: datetime, 
                          end_time: datetime, frequency: DataFrequency = None) -> List[MarketDataPoint]:
        """Recupera dados de mercado"""
        results = []
        
        try:
            # Tenta Redis primeiro (cache)
            if 'redis' in self.connections:
                redis_results = await self._retrieve_redis(symbol, start_time, end_time)
                if redis_results:
                    results.extend(redis_results)
            
            # Se não encontrar no cache, busca no PostgreSQL
            if not results and 'postgresql' in self.connections:
                pg_results = await self._retrieve_postgresql(symbol, start_time, end_time, frequency)
                results.extend(pg_results)
            
            # Fallback para SQLite
            if not results and 'sqlite' in self.connections:
                sqlite_results = await self._retrieve_sqlite(symbol, start_time, end_time, frequency)
                results.extend(sqlite_results)
                
        except Exception as e:
            logger.error(f"Erro ao recuperar dados: {e}")
        
        return results
    
    async def _retrieve_redis(self, symbol: str, start_time: datetime, 
                            end_time: datetime) -> List[MarketDataPoint]:
        """Recupera dados do Redis"""
        redis_client = self.connections['redis']
        timeseries_key = f"timeseries:{symbol}"
        
        min_score = start_time.timestamp()
        max_score = end_time.timestamp()
        
        members = redis_client.zrangebyscore(timeseries_key, min_score, max_score)
        
        results = []
        for member in members:
            try:
                if self.compression_enabled:
                    member = gzip.decompress(member).decode()
                
                data = json.loads(member)
                data_point = MarketDataPoint(
                    symbol=data['symbol'],
                    timestamp=datetime.fromisoformat(data['timestamp']),
                    open_price=data.get('open_price'),
                    high_price=data.get('high_price'),
                    low_price=data.get('low_price'),
                    close_price=data.get('close_price'),
                    volume=data.get('volume'),
                    data_source=DataSource(data['data_source']),
                    data_type=DataType(data['data_type']),
                    frequency=DataFrequency(data['frequency']),
                    quality_score=data.get('quality_score', 1.0)
                )
                results.append(data_point)
                
            except Exception as e:
                logger.error(f"Erro ao parsear dado do Redis: {e}")
        
        return results
    
    async def _retrieve_postgresql(self, symbol: str, start_time: datetime, 
                                 end_time: datetime, frequency: DataFrequency = None) -> List[MarketDataPoint]:
        """Recupera dados do PostgreSQL"""
        conn = self.connections['postgresql']
        cursor = conn.cursor()
        
        query = '''
            SELECT symbol, timestamp, open_price, high_price, low_price, 
                   close_price, volume, data_source, data_type, frequency, quality_score
            FROM market_prices
            WHERE symbol = %s AND timestamp BETWEEN %s AND %s
        '''
        
        params = [symbol, start_time, end_time]
        
        if frequency:
            query += ' AND frequency = %s'
            params.append(frequency.value)
        
        query += ' ORDER BY timestamp ASC'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            data_point = MarketDataPoint(
                symbol=row[0],
                timestamp=row[1],
                open_price=row[2],
                high_price=row[3],
                low_price=row[4],
                close_price=row[5],
                volume=row[6],
                data_source=DataSource(row[7]),
                data_type=DataType(row[8]),
                frequency=DataFrequency(row[9]),
                quality_score=row[10]
            )
            results.append(data_point)
        
        return results
    
    async def _retrieve_sqlite(self, symbol: str, start_time: datetime, 
                             end_time: datetime, frequency: DataFrequency = None) -> List[MarketDataPoint]:
        """Recupera dados do SQLite"""
        conn = self.connections['sqlite']
        cursor = conn.cursor()
        
        query = '''
            SELECT symbol, timestamp, open_price, high_price, low_price, 
                   close_price, volume, data_source, data_type, frequency, quality_score
            FROM market_prices
            WHERE symbol = ? AND timestamp BETWEEN ? AND ?
        '''
        
        params = [symbol, start_time, end_time]
        
        if frequency:
            query += ' AND frequency = ?'
            params.append(frequency.value)
        
        query += ' ORDER BY timestamp ASC'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            data_point = MarketDataPoint(
                symbol=row[0],
                timestamp=row[1],
                open_price=row[2],
                high_price=row[3],
                low_price=row[4],
                close_price=row[5],
                volume=row[6],
                data_source=DataSource(row[7]),
                data_type=DataType(row[8]),
                frequency=DataFrequency(row[9]),
                quality_score=row[10]
            )
            results.append(data_point)
        
        return results
    
    def close_connections(self):
        """Fecha todas as conexões"""
        for name, conn in self.connections.items():
            try:
                if name == 'sqlite':
                    conn.close()
                elif name == 'postgresql':
                    conn.close()
                elif name == 'mongodb':
                    conn.client.close()
                elif name == 'redis':
                    conn.close()
                logger.info(f"Conexão {name} fechada")
            except Exception as e:
                logger.error(f"Erro ao fechar conexão {name}: {e}")

# Configuração exemplo
CONFIG_EXAMPLE = {
    'api_keys': {
        'alphavantage': 'YOUR_ALPHA_VANTAGE_KEY',
        'finnhub': 'YOUR_FINNHUB_KEY',
        'polygon': 'YOUR_POLYGON_KEY'
    },
    'sources': [
        {
            'source': 'yahoo_finance',
            'symbols': ['AAPL', 'GOOGL', 'MSFT', 'TSLA'],
            'frequency': 'minute',
            'enabled': True
        },
        {
            'source': 'binance',
            'symbols': ['BTC/USDT', 'ETH/USDT', 'BNB/USDT'],
            'frequency': 'minute',
            'enabled': True
        },
        {
            'source': 'alphavantage',
            'symbols': ['SPY', 'QQQ', 'DIA'],
            'frequency': 'daily',
            'enabled': True
        }
    ],
    'news_sources': [
        {
            'source': 'finnhub_news',
            'enabled': True
        }
    ],
    'storage': {
        'sqlite': {
            'database': 'market_data.db'
        },
        'postgresql': {
            'host': 'localhost',
            'database': 'market_data',
            'user': 'postgres',
            'password': 'password',
            'port': 5432
        },
        'mongodb': {
            'host': 'localhost',
            'database': 'market_data',
            'port': 27017
        },
        'redis': {
            'host': 'localhost',
            'port': 6379,
            'db': 0
        },
        'compression': True,
        'partitioning': True
    }
}

if __name__ == "__main__":
    # Exemplo de uso
    async def main():
        collector = MarketDataCollector(CONFIG_EXAMPLE)
        storage = MarketDataStorage(CONFIG_EXAMPLE['storage'])
        
        # Subscriber para armazenar dados
        async def store_data(data_point):
            await storage.store_market_data(data_point)
            print(f"Dado armazenado: {data_point.symbol} @ {data_point.timestamp}")
        
        collector.subscribe(store_data)
        
        try:
            await collector.start()
        except KeyboardInterrupt:
            await collector.stop()
            storage.close_connections()
    
    asyncio.run(main())

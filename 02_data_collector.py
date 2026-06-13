# 02_data_collector.py
"""
Sistema VhalinorTrade - Coletor de Dados
Integração com múltiplas corretoras e captura em tempo real
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np
import websockets
import aiohttp
from redis import Redis
import pickle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VhalinorDataCollector")

class DataCollector:
    def __init__(self, config):
        self.config = config
        self.redis_client = Redis(host='localhost', port=6379, decode_responses=True)
        self.price_cache = {}
        self.orderbook_cache = {}
        self.trade_history = {}
        
    async def connect_binance_websocket(self, symbols: List[str]):
        """Conecta ao WebSocket da Binance para dados em tempo real"""
        streams = [f"{s.lower()}@ticker" for s in symbols]
        streams += [f"{s.lower()}@depth20" for s in symbols]
        
        url = f"wss://stream.binance.com:9443/stream?streams={'/'.join(streams)}"
        
        async with websockets.connect(url) as websocket:
            logger.info("Conectado ao WebSocket da Binance")
            while True:
                try:
                    response = await websocket.recv()
                    await self.process_binance_message(json.loads(response))
                except Exception as e:
                    logger.error(f"Erro WebSocket Binance: {e}")
                    await asyncio.sleep(5)
                    
    async def connect_bybit_websocket(self, symbols: List[str]):
        """Conecta ao WebSocket da Bybit"""
        url = "wss://stream.bybit.com/v5/public/spot"
        
        async with websockets.connect(url) as websocket:
            subscribe_msg = {
                "op": "subscribe",
                "args": [f"tickers.{s}" for s in symbols]
            }
            await websocket.send(json.dumps(subscribe_msg))
            
            while True:
                try:
                    response = await websocket.recv()
                    await self.process_bybit_message(json.loads(response))
                except Exception as e:
                    logger.error(f"Erro WebSocket Bybit: {e}")
                    await asyncio.sleep(5)

    async def process_binance_message(self, message: Dict[str, Any]):
        """Processa mensagens da Binance"""
        if 'data' in message:
            data = message['data']
            if 'e' in data and data['e'] == '24hrTicker':
                symbol = data['s']
                self.price_cache[symbol] = {
                    'price': float(data['c']),
                    'volume': float(data['v']),
                    'change_24h': float(data['P']),
                    'high_24h': float(data['h']),
                    'low_24h': float(data['l']),
                    'timestamp': datetime.now()
                }
                
    async def fetch_historical_data(self, symbol: str, timeframe: str, 
                                   limit: int = 1000) -> pd.DataFrame:
        """Busca dados históricos da Binance"""
        url = f"https://api.binance.com/api/v3/klines"
        params = {
            'symbol': symbol,
            'interval': timeframe,
            'limit': limit
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
                
        df = pd.DataFrame(data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ])
        
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = df[col].astype(float)
            
        return df
    
    async def capture_orderbook_snapshot(self, symbol: str, exchange: str = 'binance'):
        """Captura snapshot do livro de ordens"""
        url = f"https://api.binance.com/api/v3/depth"
        params = {'symbol': symbol, 'limit': 100}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
                
        self.orderbook_cache[symbol] = {
            'bids': data['bids'][:20],
            'asks': data['asks'][:20],
            'timestamp': datetime.now(),
            'exchange': exchange
        }
        
    def calculate_liquidity_metrics(self, symbol: str) -> Dict[str, float]:
        """Calcula métricas de liquidez"""
        if symbol not in self.orderbook_cache:
            return {}
            
        orderbook = self.orderbook_cache[symbol]
        bids = np.array(orderbook['bids'], dtype=float)
        asks = np.array(orderbook['asks'], dtype=float)
        
        spread = (asks[0][0] - bids[0][0]) / bids[0][0]
        bid_depth = np.sum(bids[:10, 1])
        ask_depth = np.sum(asks[:10, 1])
        
        return {
            'spread': spread,
            'bid_depth': bid_depth,
            'ask_depth': ask_depth,
            'total_depth': bid_depth + ask_depth,
            'imbalance': (bid_depth - ask_depth) / (bid_depth + ask_depth)
        }
    
    async def continuous_data_collection(self):
        """Loop principal de coleta contínua de dados"""
        logger.info("Iniciando coleta contínua de dados...")
        
        while True:
            try:
                for symbol in self.config.symbols:
                    for tf in self.config.timeframes:
                        df = await self.fetch_historical_data(
                            symbol, tf.value, limit=500
                        )
                        
                        # Salva no Redis para acesso rápido
                        key = f"historical:{symbol}:{tf.value}"
                        self.redis_client.setex(
                            key,
                            timedelta(hours=24),
                            pickle.dumps(df)
                        )
                        
                    await self.capture_orderbook_snapshot(symbol)
                    
                await asyncio.sleep(60)  # Atualiza a cada minuto
                
            except Exception as e:
                logger.error(f"Erro na coleta contínua: {e}")
                await asyncio.sleep(10)
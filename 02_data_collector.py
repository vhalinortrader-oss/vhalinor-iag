# 02_data_collector.py
"""
Sistema VhalinorTrade - Coletor de Dados
Integração com múltiplas corretoras e captura em tempo real
"""

import asyncio
import json
import logging
import pickle
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import aiohttp
import numpy as np
import pandas as pd
import websockets
from redis import Redis

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("VhalinorDataCollector")

# TTL padrão para cache Redis (24 horas em segundos)
_CACHE_TTL_SECONDS = 86_400

# Cliente Redis separado para dados binários (pickle) — sem decode_responses
_REDIS_BINARY_CLIENT_KWARGS = dict(host="localhost", port=6379, decode_responses=False)
# Cliente Redis para dados de texto/string
_REDIS_TEXT_CLIENT_KWARGS = dict(host="localhost", port=6379, decode_responses=True)

BINANCE_WS_BASE = "wss://stream.binance.com:9443/stream"
BYBIT_WS_SPOT = "wss://stream.bybit.com/v5/public/spot"
BINANCE_REST_BASE = "https://api.binance.com/api/v3"


class DataCollector:
    def __init__(self, config):
        self.config = config

        # Dois clientes Redis: um binário (para pickle) e um de texto
        self._redis_binary: Redis = Redis(**_REDIS_BINARY_CLIENT_KWARGS)
        self._redis_text: Redis = Redis(**_REDIS_TEXT_CLIENT_KWARGS)

        self.price_cache: Dict[str, Dict[str, Any]] = {}
        self.orderbook_cache: Dict[str, Dict[str, Any]] = {}
        self.trade_history: Dict[str, List] = {}

    # ------------------------------------------------------------------
    # WebSocket — Binance
    # ------------------------------------------------------------------

    async def connect_binance_websocket(
        self, symbols: List[str], reconnect_delay: float = 5.0
    ) -> None:
        """Conecta ao WebSocket combinado da Binance com reconexão automática."""
        streams = [f"{s.lower()}@ticker" for s in symbols]
        streams += [f"{s.lower()}@depth20" for s in symbols]
        url = f"{BINANCE_WS_BASE}?streams={'/'.join(streams)}"

        while True:
            try:
                async with websockets.connect(url, ping_interval=20) as ws:
                    logger.info("Conectado ao WebSocket da Binance.")
                    async for raw in ws:
                        try:
                            await self.process_binance_message(json.loads(raw))
                        except Exception as exc:
                            logger.warning("Erro ao processar mensagem Binance: %s", exc)
            except Exception as exc:
                logger.error("WebSocket Binance desconectado: %s. Reconectando em %.1fs…", exc, reconnect_delay)
                await asyncio.sleep(reconnect_delay)

    # ------------------------------------------------------------------
    # WebSocket — Bybit
    # ------------------------------------------------------------------

    async def connect_bybit_websocket(
        self, symbols: List[str], reconnect_delay: float = 5.0
    ) -> None:
        """Conecta ao WebSocket da Bybit com reconexão automática."""
        subscribe_msg = json.dumps({
            "op": "subscribe",
            "args": [f"tickers.{s}" for s in symbols],
        })

        while True:
            try:
                async with websockets.connect(BYBIT_WS_SPOT, ping_interval=20) as ws:
                    await ws.send(subscribe_msg)
                    logger.info("Conectado ao WebSocket da Bybit.")
                    async for raw in ws:
                        try:
                            await self.process_bybit_message(json.loads(raw))
                        except Exception as exc:
                            logger.warning("Erro ao processar mensagem Bybit: %s", exc)
            except Exception as exc:
                logger.error("WebSocket Bybit desconectado: %s. Reconectando em %.1fs…", exc, reconnect_delay)
                await asyncio.sleep(reconnect_delay)

    # ------------------------------------------------------------------
    # Processadores de mensagens
    # ------------------------------------------------------------------

    async def process_binance_message(self, message: Dict[str, Any]) -> None:
        """Processa e armazena dados de ticker da Binance."""
        data = message.get("data", {})
        if data.get("e") != "24hrTicker":
            return

        symbol: str = data["s"]
        self.price_cache[symbol] = {
            "price": float(data["c"]),
            "volume": float(data["v"]),
            "change_24h": float(data["P"]),
            "high_24h": float(data["h"]),
            "low_24h": float(data["l"]),
            "timestamp": datetime.utcnow(),
        }
        logger.debug("Preço atualizado — %s: %s", symbol, self.price_cache[symbol]["price"])

    async def process_bybit_message(self, message: Dict[str, Any]) -> None:
        """Processa e armazena dados de ticker da Bybit."""
        topic: str = message.get("topic", "")
        if not topic.startswith("tickers."):
            return

        data = message.get("data", {})
        symbol = topic.split(".", 1)[1]
        self.price_cache[f"bybit:{symbol}"] = {
            "price": float(data.get("lastPrice", 0)),
            "volume": float(data.get("volume24h", 0)),
            "change_24h": float(data.get("price24hPcnt", 0)),
            "high_24h": float(data.get("highPrice24h", 0)),
            "low_24h": float(data.get("lowPrice24h", 0)),
            "timestamp": datetime.utcnow(),
        }

    # ------------------------------------------------------------------
    # Dados históricos
    # ------------------------------------------------------------------

    async def fetch_historical_data(
        self,
        symbol: str,
        timeframe: str,
        limit: int = 1000,
        session: Optional[aiohttp.ClientSession] = None,
    ) -> pd.DataFrame:
        """
        Busca dados históricos de klines da Binance.

        Reutiliza `session` quando fornecida, evitando abrir uma nova
        conexão TCP por chamada no loop de coleta contínua.
        """
        url = f"{BINANCE_REST_BASE}/klines"
        params = {"symbol": symbol, "interval": timeframe, "limit": limit}

        _owns_session = session is None
        if _owns_session:
            session = aiohttp.ClientSession()

        try:
            async with session.get(url, params=params) as resp:
                resp.raise_for_status()
                data = await resp.json()
        finally:
            if _owns_session:
                await session.close()

        df = pd.DataFrame(
            data,
            columns=[
                "timestamp", "open", "high", "low", "close", "volume",
                "close_time", "quote_volume", "trades",
                "taker_buy_base", "taker_buy_quote", "ignore",
            ],
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
        df.set_index("timestamp", inplace=True)
        for col in ("open", "high", "low", "close", "volume"):
            df[col] = df[col].astype(float)

        # Remove colunas desnecessárias para economizar memória
        df.drop(columns=["close_time", "ignore"], inplace=True)

        return df

    def _cache_dataframe(self, key: str, df: pd.DataFrame) -> None:
        """Serializa e armazena DataFrame no Redis (cliente binário)."""
        try:
            self._redis_binary.setex(key, _CACHE_TTL_SECONDS, pickle.dumps(df))
        except Exception as exc:
            logger.error("Falha ao salvar '%s' no Redis: %s", key, exc)

    def get_cached_dataframe(self, key: str) -> Optional[pd.DataFrame]:
        """Recupera DataFrame do Redis. Retorna None se não encontrado."""
        try:
            raw = self._redis_binary.get(key)
            return pickle.loads(raw) if raw else None
        except Exception as exc:
            logger.error("Falha ao ler '%s' do Redis: %s", key, exc)
            return None

    # ------------------------------------------------------------------
    # Order book
    # ------------------------------------------------------------------

    async def capture_orderbook_snapshot(
        self,
        symbol: str,
        exchange: str = "binance",
        depth: int = 20,
        session: Optional[aiohttp.ClientSession] = None,
    ) -> None:
        """Captura snapshot do livro de ordens e armazena em cache."""
        url = f"{BINANCE_REST_BASE}/depth"
        params = {"symbol": symbol, "limit": min(depth * 5, 5000)}

        _owns_session = session is None
        if _owns_session:
            session = aiohttp.ClientSession()

        try:
            async with session.get(url, params=params) as resp:
                resp.raise_for_status()
                data = await resp.json()
        finally:
            if _owns_session:
                await session.close()

        self.orderbook_cache[symbol] = {
            "bids": data["bids"][:depth],
            "asks": data["asks"][:depth],
            "last_update_id": data.get("lastUpdateId"),
            "timestamp": datetime.utcnow(),
            "exchange": exchange,
        }

    def calculate_liquidity_metrics(self, symbol: str) -> Dict[str, float]:
        """
        Calcula métricas de liquidez a partir do order book em cache.

        Retorna dicionário vazio se o símbolo não estiver disponível
        ou se o book estiver vazio/mal-formado.
        """
        snapshot = self.orderbook_cache.get(symbol)
        if not snapshot:
            logger.warning("Order book não encontrado para '%s'.", symbol)
            return {}

        try:
            bids = np.array(snapshot["bids"], dtype=float)
            asks = np.array(snapshot["asks"], dtype=float)
        except (ValueError, TypeError) as exc:
            logger.error("Order book inválido para '%s': %s", symbol, exc)
            return {}

        if bids.size == 0 or asks.size == 0:
            return {}

        best_bid = bids[0, 0]
        best_ask = asks[0, 0]

        spread = (best_ask - best_bid) / best_bid if best_bid > 0 else float("nan")
        bid_depth = float(np.sum(bids[:10, 1]))
        ask_depth = float(np.sum(asks[:10, 1]))
        total_depth = bid_depth + ask_depth

        return {
            "spread": spread,
            "bid_depth": bid_depth,
            "ask_depth": ask_depth,
            "total_depth": total_depth,
            "imbalance": (bid_depth - ask_depth) / total_depth if total_depth > 0 else 0.0,
            "best_bid": best_bid,
            "best_ask": best_ask,
        }

    # ------------------------------------------------------------------
    # Loop principal de coleta
    # ------------------------------------------------------------------

    async def continuous_data_collection(self, interval_seconds: float = 60.0) -> None:
        """
        Loop principal de coleta contínua de dados históricos e order books.

        Reutiliza uma única sessão HTTP por ciclo para reduzir overhead de conexão.
        """
        logger.info("Iniciando coleta contínua de dados (intervalo: %.0fs).", interval_seconds)

        while True:
            cycle_start = datetime.utcnow()
            try:
                async with aiohttp.ClientSession() as session:
                    tasks = []
                    for symbol in self.config.symbols:
                        for tf in self.config.timeframes:
                            tasks.append(
                                self._collect_symbol_timeframe(symbol, tf, session)
                            )
                        tasks.append(
                            self.capture_orderbook_snapshot(symbol, session=session)
                        )

                    results = await asyncio.gather(*tasks, return_exceptions=True)

                # Loga erros individuais sem abortar o ciclo
                for result in results:
                    if isinstance(result, Exception):
                        logger.error("Erro em tarefa de coleta: %s", result)

            except Exception as exc:
                logger.error("Erro inesperado no ciclo de coleta: %s", exc)

            elapsed = (datetime.utcnow() - cycle_start).total_seconds()
            sleep_time = max(0.0, interval_seconds - elapsed)
            logger.info("Ciclo concluído em %.1fs. Próximo em %.1fs.", elapsed, sleep_time)
            await asyncio.sleep(sleep_time)

    async def _collect_symbol_timeframe(
        self,
        symbol: str,
        tf,
        session: aiohttp.ClientSession,
    ) -> None:
        """Busca histórico de um (símbolo, timeframe) e persiste no Redis."""
        df = await self.fetch_historical_data(symbol, tf.value, limit=500, session=session)
        key = f"historical:{symbol}:{tf.value}"
        self._cache_dataframe(key, df)
        logger.debug("Cache atualizado — %s", key)

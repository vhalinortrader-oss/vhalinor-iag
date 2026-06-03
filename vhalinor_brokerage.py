import os
import logging
import json
import time
import hmac
import hashlib
import urllib.request
from typing import Dict, Any, Optional

# Configuração de Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VhalinorBrokerage")

try:
    from binance.client import Client
    from binance.exceptions import BinanceAPIException
    BINANCE_AVAILABLE = True
except ImportError:
    BINANCE_AVAILABLE = False
    logger.warning("Biblioteca 'python-binance' não encontrada. Operando apenas em modo PAPER TRADING.")

class BaseBroker:
    """Interface base para corretoras"""
    def get_balance(self, asset: str) -> float:
        raise NotImplementedError
    
    def get_price(self, symbol: str) -> float:
        raise NotImplementedError
    
    def create_order(self, symbol: str, side: str, quantity: float, order_type: str = "MARKET") -> Dict[str, Any]:
        raise NotImplementedError

class BinanceBroker(BaseBroker):
    """Integração real com a API da Binance"""
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        if not BINANCE_AVAILABLE:
            raise ImportError("Biblioteca 'python-binance' é necessária para usar o BinanceBroker.")
        self.client = Client(api_key, api_secret, testnet=testnet)
        self.testnet = testnet
        logger.info(f"BinanceBroker inicializado (Testnet: {testnet})")

    def get_balance(self, asset: str) -> float:
        try:
            balance = self.client.get_asset_balance(asset=asset)
            return float(balance['free']) if balance else 0.0
        except BinanceAPIException as e:
            logger.error(f"Erro ao buscar saldo Binance: {e}")
            return 0.0

    def get_price(self, symbol: str) -> float:
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except BinanceAPIException as e:
            logger.error(f"Erro ao buscar preço Binance: {e}")
            return 0.0

    def create_order(self, symbol: str, side: str, quantity: float, order_type: str = "MARKET") -> Dict[str, Any]:
        """
        Envia uma ordem de compra ou venda.
        side: 'BUY' ou 'SELL'
        """
        try:
            logger.info(f"Enviando ordem {side} de {quantity} {symbol} na Binance...")
            if order_type == "MARKET":
                order = self.client.create_order(
                    symbol=symbol,
                    side=side,
                    type=Client.ORDER_TYPE_MARKET,
                    quantity=quantity
                )
            else:
                # Exemplo para LIMIT (precisaria de price)
                return {"error": "Apenas MARKET orders implementadas neste módulo base."}
            
            logger.info(f"Ordem executada com sucesso: ID {order['orderId']}")
            return order
        except BinanceAPIException as e:
            logger.error(f"Erro ao criar ordem Binance: {e}")
            return {"error": str(e)}

class PaperBroker(BaseBroker):
    """Corretora de Simulação (Paper Trading) para testes seguros"""
    def __init__(self, initial_balance: float = 10000.0):
        self.balances = {"USDT": initial_balance}
        self.positions = {}
        logger.info(f"PaperBroker inicializado com saldo de {initial_balance} USDT")

    def get_balance(self, asset: str) -> float:
        return self.balances.get(asset, 0.0)

    def get_price(self, symbol: str) -> float:
        # Simula preço buscando de uma API pública simples ou retorna mock
        try:
            # Tenta buscar preço real via API pública da Binance (sem chave)
            url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read().decode())
                return float(data['price'])
        except:
            return 50000.0 # Mock fallback

    def create_order(self, symbol: str, side: str, quantity: float, order_type: str = "MARKET") -> Dict[str, Any]:
        price = self.get_price(symbol)
        cost = price * quantity
        asset = symbol.replace("USDT", "")

        if side == "BUY":
            if self.balances.get("USDT", 0) >= cost:
                self.balances["USDT"] -= cost
                self.balances[asset] = self.balances.get(asset, 0) + quantity
                logger.info(f"[PAPER] COMPRA: {quantity} {asset} a {price} USDT")
            else:
                return {"error": "Saldo insuficiente no PaperBroker"}
        
        elif side == "SELL":
            if self.balances.get(asset, 0) >= quantity:
                self.balances[asset] -= quantity
                self.balances["USDT"] += cost
                logger.info(f"[PAPER] VENDA: {quantity} {asset} a {price} USDT")
            else:
                return {"error": "Posição insuficiente no PaperBroker"}

        return {
            "orderId": int(time.time()),
            "symbol": symbol,
            "side": side,
            "price": price,
            "quantity": quantity,
            "status": "FILLED",
            "type": "PAPER_TRADE"
        }

class BrokerFactory:
    """Fábrica para instanciar a corretora correta baseada no ambiente"""
    @staticmethod
    def get_broker() -> BaseBroker:
        api_key = os.getenv("BINANCE_API_KEY")
        api_secret = os.getenv("BINANCE_API_SECRET")
        use_real = os.getenv("USE_REAL_BROKER", "false").lower() == "true"

        if use_real and api_key and api_secret:
            return BinanceBroker(api_key, api_secret, testnet=True) # Default para Testnet por segurança
        else:
            return PaperBroker()

# Instância global para uso no motor
broker = BrokerFactory.get_broker()

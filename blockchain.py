"""
Módulo de Blockchain e Web3
==========================
Implementação completa com Web3.py e integração Ethereum
"""

import asyncio
import json
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import time
import hashlib

# Importações condicionais
try:
    from web3 import Web3
    from web3.exceptions import TransactionNotFound, ContractLogicError
    from web3.middleware import geth_poa_middleware
    from eth_account import Account
    from eth_account.messages import encode_defunct
    from eth_account.signers.local import LocalAccount
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False

from config import settings
from core import get_logger, log_execution


class NetworkType(str, Enum):
    """Tipos de redes blockchain"""
    ETHEREUM_MAINNET = "ethereum_mainnet"
    ETHEREUM_SEPOLIA = "ethereum_sepolia"
    POLYGON_MAINNET = "polygon_mainnet"
    BSC_MAINNET = "bsc_mainnet"
    ARBITRUM_MAINNET = "arbitrum_mainnet"
    LOCAL = "local"


class TransactionStatus(str, Enum):
    """Status de transações"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class WalletAccount:
    """Conta de carteira blockchain"""
    address: str
    private_key: str
    public_key: str
    network: NetworkType
    balance_eth: float = 0.0
    balance_usd: float = 0.0
    created_at: datetime = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        data = asdict(self)
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        return data


@dataclass
class Transaction:
    """Transação blockchain"""
    hash: str
    from_address: str
    to_address: str
    value_eth: float
    gas_price: int
    gas_limit: int
    gas_used: Optional[int] = None
    status: TransactionStatus = TransactionStatus.PENDING
    block_number: Optional[int] = None
    timestamp: Optional[datetime] = None
    confirmations: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        data = asdict(self)
        if self.timestamp:
            data['timestamp'] = self.timestamp.isoformat()
        return data


class BlockchainManager:
    """
    Gerenciador de operações blockchain
    """
    
    def __init__(self):
        self.logger = get_logger().get_logger("vhalinor.blockchain", "blockchain")
        
        # Configurações de rede
        self.network_configs = {
            NetworkType.ETHEREUM_MAINNET: {
                "name": "Ethereum Mainnet",
                "rpc_url": "https://mainnet.infura.io/v3/YOUR-PROJECT-ID",
                "chain_id": 1,
                "currency": "ETH",
                "explorer": "https://etherscan.io"
            },
            NetworkType.ETHEREUM_SEPOLIA: {
                "name": "Ethereum Sepolia",
                "rpc_url": "https://sepolia.infura.io/v3/YOUR-PROJECT-ID",
                "chain_id": 11155111,
                "currency": "ETH",
                "explorer": "https://sepolia.etherscan.io"
            },
            NetworkType.POLYGON_MAINNET: {
                "name": "Polygon Mainnet",
                "rpc_url": "https://polygon-rpc.com",
                "chain_id": 137,
                "currency": "MATIC",
                "explorer": "https://polygonscan.com"
            },
            NetworkType.BSC_MAINNET: {
                "name": "BSC Mainnet",
                "rpc_url": "https://bsc-dataseed.binance.org",
                "chain_id": 56,
                "currency": "BNB",
                "explorer": "https://bscscan.com"
            },
            NetworkType.LOCAL: {
                "name": "Local Hardhat",
                "rpc_url": "http://127.0.0.1:8545",
                "chain_id": 31337,
                "currency": "ETH",
                "explorer": None
            }
        }
        
        # Conexões Web3
        self.connections: Dict[NetworkType, Web3] = {}
        self.accounts: Dict[str, WalletAccount] = {}
        
        # Cache de transações
        self.transaction_cache: Dict[str, Transaction] = {}
        
        # Configurações
        self.default_network = NetworkType.ETHEREUM_SEPOLIA  # Testnet por padrão
        self.gas_limit = settings.web3_gas_limit
        self.gas_price = settings.web3_gas_price
        
        # Inicializar conexões
        self._initialize_connections()
    
    @log_execution(
        component="blockchain",
        operation="initialize_connections",
        log_exceptions=True
    )
    def _initialize_connections(self):
        """Inicializa conexões Web3"""
        if not WEB3_AVAILABLE:
            self.logger.error("Web3 not available")
            return
        
        for network_type, config in self.network_configs.items():
            try:
                # Usar URL configurada ou padrão
                rpc_url = settings.web3_provider_url or config["rpc_url"]
                
                w3 = Web3(Web3.HTTPProvider(rpc_url))
                
                # Adicionar middleware para redes POA
                if network_type in [NetworkType.POLYGON_MAINNET, NetworkType.BSC_MAINNET]:
                    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
                
                # Verificar conexão
                if w3.is_connected():
                    self.connections[network_type] = w3
                    self.logger.info(f"Connected to {config['name']}")
                else:
                    self.logger.warning(f"Failed to connect to {config['name']}")
                    
            except Exception as e:
                self.logger.error(f"Error connecting to {network_type}: {e}")
    
    def get_connection(self, network_type: Optional[NetworkType] = None) -> Optional[Web3]:
        """
        Obtém conexão Web3 para rede especificada
        
        Args:
            network_type: Tipo de rede (opcional)
        
        Returns:
            Conexão Web3 ou None
        """
        network = network_type or self.default_network
        
        if network in self.connections:
            return self.connections[network]
        
        self.logger.error(f"No connection available for {network}")
        return None
    
    @log_execution(
        component="blockchain",
        operation="create_wallet",
        log_args=True,
        log_result=True
    )
    def create_wallet(
        self,
        network: NetworkType = None,
        private_key: Optional[str] = None
    ) -> WalletAccount:
        """
        Cria ou importa carteira
        
        Args:
            network: Tipo de rede
            private_key: Chave privada (opcional)
        
        Returns:
            Conta de carteira criada
        """
        network = network or self.default_network
        
        if private_key:
            # Importar carteira existente
            account = Account.from_key(private_key)
        else:
            # Criar nova carteira
            account = Account.create()
        
        wallet = WalletAccount(
            address=account.address,
            private_key=account.key.hex(),
            public_key=account._public_key,
            network=network,
            created_at=datetime.now()
        )
        
        # Adicionar ao cache
        self.accounts[wallet.address] = wallet
        
        self.logger.info(f"Wallet created: {wallet.address}")
        return wallet
    
    @log_execution(
        component="blockchain",
        operation="get_balance",
        log_args=True,
        log_result=True
    )
    async def get_balance(
        self,
        address: str,
        network: Optional[NetworkType] = None
    ) -> Dict[str, float]:
        """
        Obtém saldo da carteira
        
        Args:
            address: Endereço da carteira
            network: Tipo de rede
        
        Returns:
            Dicionário com saldos ETH e USD
        """
        w3 = self.get_connection(network)
        if not w3:
            return {"eth": 0.0, "usd": 0.0}
        
        try:
            # Obter saldo em wei
            balance_wei = w3.eth.get_balance(address)
            balance_eth = w3.from_wei(balance_wei, 'ether')
            
            # Converter para USD (simulado - em produção usar API de preço)
            eth_price_usd = await self._get_eth_price()
            balance_usd = float(balance_eth) * eth_price_usd
            
            # Atualizar cache
            if address in self.accounts:
                self.accounts[address].balance_eth = float(balance_eth)
                self.accounts[address].balance_usd = balance_usd
            
            self.logger.info(f"Balance for {address}: {balance_eth} ETH (${balance_usd:.2f})")
            
            return {
                "eth": float(balance_eth),
                "usd": balance_usd
            }
            
        except Exception as e:
            self.logger.error(f"Error getting balance for {address}: {e}")
            return {"eth": 0.0, "usd": 0.0}
    
    async def _get_eth_price(self) -> float:
        """Obtém preço atual do ETH em USD (simulado)"""
        # Em produção, integrar com API real (CoinGecko, CoinMarketCap, etc.)
        # Por enquanto, retorna preço simulado
        return 2000.0  # $2,000 ETH
    
    @log_execution(
        component="blockchain",
        operation="send_transaction",
        log_args=True,
        log_result=True
    )
    async def send_transaction(
        self,
        from_address: str,
        to_address: str,
        value_eth: float,
        network: Optional[NetworkType] = None,
        gas_price: Optional[int] = None,
        gas_limit: Optional[int] = None
    ) -> Optional[Transaction]:
        """
        Envia transação blockchain
        
        Args:
            from_address: Endereço de origem
            to_address: Endereço de destino
            value_eth: Valor em ETH
            network: Tipo de rede
            gas_price: Preço do gás (opcional)
            gas_limit: Limite de gás (opcional)
        
        Returns:
            Transação criada ou None
        """
        w3 = self.get_connection(network)
        if not w3:
            return None
        
        try:
            # Obter conta
            if from_address not in self.accounts:
                self.logger.error(f"Wallet not found: {from_address}")
                return None
            
            wallet = self.accounts[from_address]
            account = Account.from_key(wallet.private_key)
            
            # Configurar parâmetros da transação
            nonce = w3.eth.get_transaction_count(from_address)
            gas_price = gas_price or self.gas_price
            gas_limit = gas_limit or self.gas_limit
            
            # Converter valor para wei
            value_wei = w3.to_wei(value_eth, 'ether')
            
            # Criar transação
            transaction = {
                'from': from_address,
                'to': to_address,
                'value': value_wei,
                'gas': gas_limit,
                'gasPrice': gas_price,
                'nonce': nonce,
                'chainId': self.network_configs[network or self.default_network]['chain_id']
            }
            
            # Assinar transação
            signed_txn = w3.eth.account.sign_transaction(transaction, account.key)
            
            # Enviar transação
            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Criar objeto de transação
            transaction = Transaction(
                hash=tx_hash.hex(),
                from_address=from_address,
                to_address=to_address,
                value_eth=value_eth,
                gas_price=gas_price,
                gas_limit=gas_limit,
                status=TransactionStatus.PENDING,
                timestamp=datetime.now()
            )
            
            # Adicionar ao cache
            self.transaction_cache[tx_hash.hex()] = transaction
            
            self.logger.info(f"Transaction sent: {tx_hash.hex()}")
            return transaction
            
        except Exception as e:
            self.logger.error(f"Error sending transaction: {e}")
            return None
    
    @log_execution(
        component="blockchain",
        operation="get_transaction_status",
        log_args=True,
        log_result=True
    )
    async def get_transaction_status(
        self,
        tx_hash: str,
        network: Optional[NetworkType] = None
    ) -> Optional[Transaction]:
        """
        Verifica status de transação
        
        Args:
            tx_hash: Hash da transação
            network: Tipo de rede
        
        Returns:
            Transação atualizada ou None
        """
        w3 = self.get_connection(network)
        if not w3:
            return None
        
        try:
            # Verificar no cache primeiro
            if tx_hash in self.transaction_cache:
                transaction = self.transaction_cache[tx_hash]
            else:
                transaction = Transaction(
                    hash=tx_hash,
                    from_address="",
                    to_address="",
                    value_eth=0.0,
                    gas_price=0,
                    gas_limit=0,
                    status=TransactionStatus.PENDING
                )
                self.transaction_cache[tx_hash] = transaction
            
            # Obter receipt da transação
            try:
                receipt = w3.eth.get_transaction_receipt(tx_hash)
                
                if receipt:
                    transaction.status = TransactionStatus.CONFIRMED if receipt['status'] == 1 else TransactionStatus.FAILED
                    transaction.block_number = receipt['blockNumber']
                    transaction.gas_used = receipt['gasUsed']
                    
                    # Obter timestamp do bloco
                    if receipt['blockNumber']:
                        block = w3.eth.get_block(receipt['blockNumber'])
                        transaction.timestamp = datetime.fromtimestamp(block['timestamp'])
                    
                    # Calcular confirmações
                    current_block = w3.eth.block_number
                    if transaction.block_number:
                        transaction.confirmations = current_block - transaction.block_number
                
            except TransactionNotFound:
                # Transação ainda não foi minerada
                transaction.status = TransactionStatus.PENDING
            
            self.logger.info(f"Transaction status: {tx_hash} - {transaction.status}")
            return transaction
            
        except Exception as e:
            self.logger.error(f"Error getting transaction status: {e}")
            return None
    
    @log_execution(
        component="blockchain",
        operation="deploy_contract",
        log_args=True,
        log_result=True
    )
    async def deploy_contract(
        self,
        contract_bytecode: str,
        contract_abi: List[Dict],
        from_address: str,
        constructor_args: List = None,
        network: Optional[NetworkType] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Implanta contrato inteligente
        
        Args:
            contract_bytecode: Bytecode do contrato
            contract_abi: ABI do contrato
            from_address: Endereço do implantador
            constructor_args: Argumentos do construtor
            network: Tipo de rede
        
        Returns:
            Informações do contrato implantado ou None
        """
        w3 = self.get_connection(network)
        if not w3:
            return None
        
        try:
            # Obter conta
            if from_address not in self.accounts:
                self.logger.error(f"Wallet not found: {from_address}")
                return None
            
            wallet = self.accounts[from_address]
            account = Account.from_key(wallet.private_key)
            
            # Criar contrato
            contract = w3.eth.contract(abi=contract_abi, bytecode=contract_bytecode)
            
            # Construir transação de implantação
            constructor_txn = contract.constructor(*constructor_args or []).build_transaction({
                'from': from_address,
                'gas': self.gas_limit * 2,  # Deployments usam mais gás
                'gasPrice': self.gas_price,
                'nonce': w3.eth.get_transaction_count(from_address),
                'chainId': self.network_configs[network or self.default_network]['chain_id']
            })
            
            # Assinar e enviar
            signed_txn = w3.eth.account.sign_transaction(constructor_txn, account.key)
            tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            self.logger.info(f"Contract deployment sent: {tx_hash.hex()}")
            
            # Aguardar confirmação
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            if receipt['status'] == 1:
                contract_address = receipt['contractAddress']
                self.logger.info(f"Contract deployed: {contract_address}")
                
                return {
                    "contract_address": contract_address,
                    "transaction_hash": tx_hash.hex(),
                    "block_number": receipt['blockNumber'],
                    "gas_used": receipt['gasUsed'],
                    "status": "success"
                }
            else:
                return {
                    "transaction_hash": tx_hash.hex(),
                    "status": "failed",
                    "error": "Contract deployment failed"
                }
                
        except Exception as e:
            self.logger.error(f"Error deploying contract: {e}")
            return None
    
    @log_execution(
        component="blockchain",
        operation="call_contract_method",
        log_args=True,
        log_result=True
    )
    async def call_contract_method(
        self,
        contract_address: str,
        contract_abi: List[Dict],
        method_name: str,
        method_args: List = None,
        from_address: Optional[str] = None,
        network: Optional[NetworkType] = None
    ) -> Optional[Any]:
        """
        Chama método de contrato (view ou write)
        
        Args:
            contract_address: Endereço do contrato
            contract_abi: ABI do contrato
            method_name: Nome do método
            method_args: Argumentos do método
            from_address: Endereço (para métodos write)
            network: Tipo de rede
        
        Returns:
            Resultado da chamada ou None
        """
        w3 = self.get_connection(network)
        if not w3:
            return None
        
        try:
            # Criar instância do contrato
            contract = w3.eth.contract(
                address=contract_address,
                abi=contract_abi
            )
            
            # Obter método
            method = getattr(contract.functions, method_name)
            
            # Chamar método
            if method_args:
                result = method(*method_args)
            else:
                result = method()
            
            # Verificar se é método view ou write
            method_abi = next(
                (item for item in contract_abi if item['name'] == method_name),
                None
            )
            
            if method_abi and method_abi['type'] == 'view':
                # Método view - chamada local
                call_result = result.call()
                self.logger.info(f"Contract view method called: {method_name}")
                return call_result
            else:
                # Método write - criar transação
                if not from_address:
                    self.logger.error("from_address required for write methods")
                    return None
                
                if from_address not in self.accounts:
                    self.logger.error(f"Wallet not found: {from_address}")
                    return None
                
                wallet = self.accounts[from_address]
                account = Account.from_key(wallet.private_key)
                
                # Construir transação
                txn = result.build_transaction({
                    'from': from_address,
                    'gas': self.gas_limit,
                    'gasPrice': self.gas_price,
                    'nonce': w3.eth.get_transaction_count(from_address),
                    'chainId': self.network_configs[network or self.default_network]['chain_id']
                })
                
                # Assinar e enviar
                signed_txn = w3.eth.account.sign_transaction(txn, account.key)
                tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
                
                self.logger.info(f"Contract write method called: {method_name} - {tx_hash.hex()}")
                
                return {
                    "transaction_hash": tx_hash.hex(),
                    "status": "sent"
                }
                
        except Exception as e:
            self.logger.error(f"Error calling contract method {method_name}: {e}")
            return None
    
    def get_network_info(self, network: Optional[NetworkType] = None) -> Dict[str, Any]:
        """
        Obtém informações da rede
        
        Args:
            network: Tipo de rede
        
        Returns:
            Informações da rede
        """
        network = network or self.default_network
        
        if network not in self.network_configs:
            return {}
        
        config = self.network_configs[network]
        w3 = self.get_connection(network)
        
        info = {
            "name": config["name"],
            "chain_id": config["chain_id"],
            "currency": config["currency"],
            "explorer": config["explorer"],
            "connected": w3 is not None and w3.is_connected()
        }
        
        if w3 and w3.is_connected():
            try:
                info["block_number"] = w3.eth.block_number
                info["gas_price"] = w3.eth.gas_price
                info["network_id"] = w3.eth.chain_id
            except Exception as e:
                self.logger.error(f"Error getting network info: {e}")
        
        return info
    
    def get_wallet_info(self, address: str) -> Optional[Dict[str, Any]]:
        """
        Obtém informações da carteira
        
        Args:
            address: Endereço da carteira
        
        Returns:
            Informações da carteira ou None
        """
        if address not in self.accounts:
            return None
        
        wallet = self.accounts[address]
        return wallet.to_dict()
    
    def get_transaction_history(
        self,
        address: str,
        limit: int = 50
    ) -> List[Transaction]:
        """
        Obtém histórico de transações (simulado)
        
        Args:
            address: Endereço da carteira
            limit: Número máximo de transações
        
        Returns:
            Lista de transações
        """
        # Em produção, usar Etherscan API ou similar
        # Por enquanto, retorna transações do cache
        transactions = []
        
        for tx_hash, transaction in self.transaction_cache.items():
            if (transaction.from_address == address or 
                transaction.to_address == address):
                transactions.append(transaction)
        
        # Ordenar por timestamp (mais recentes primeiro)
        transactions.sort(key=lambda x: x.timestamp or datetime.min, reverse=True)
        
        return transactions[:limit]
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status do gerenciador blockchain"""
        return {
            "connected_networks": list(self.connections.keys()),
            "default_network": self.default_network,
            "wallets_count": len(self.accounts),
            "transactions_cached": len(self.transaction_cache),
            "web3_available": WEB3_AVAILABLE,
            "gas_settings": {
                "gas_limit": self.gas_limit,
                "gas_price": self.gas_price
            },
            "last_update": datetime.now().isoformat()
        }


# Instância global do gerenciador
_blockchain_manager: Optional[BlockchainManager] = None


def get_blockchain_manager() -> BlockchainManager:
    """Obtém instância global do BlockchainManager"""
    global _blockchain_manager
    if _blockchain_manager is None:
        _blockchain_manager = BlockchainManager()
    return _blockchain_manager


# Exportações principais
__all__ = [
    "BlockchainManager",
    "WalletAccount",
    "Transaction",
    "NetworkType",
    "TransactionStatus",
    "get_blockchain_manager"
]

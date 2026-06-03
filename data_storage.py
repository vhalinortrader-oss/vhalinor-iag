"""
Data Storage - Armazenamento de Dados
==================================
Bancos de dados estruturados e não estruturados, Data Lakes e Warehouses
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import os
from pathlib import Path
import hashlib
import sqlite3
import pickle
import gzip
import shutil

# Importações condicionais
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    import pymongo
    from pymongo import MongoClient
    MONGO_AVAILABLE = True
except ImportError:
    MONGO_AVAILABLE = False

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

try:
    import boto3
    from botocore.exceptions import ClientError
    S3_AVAILABLE = True
except ImportError:
    S3_AVAILABLE = False

from config import settings
from core import get_logger, log_execution
from .data_collector import DataSample, DataType


class StorageType(str, Enum):
    """Tipos de armazenamento"""
    LOCAL_FILE = "local_file"
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MONGODB = "mongodb"
    REDIS = "redis"
    S3 = "s3"
    DATA_LAKE = "data_lake"
    DATA_WAREHOUSE = "data_warehouse"


class DataFormat(str, Enum):
    """Formatos de dados"""
    JSON = "json"
    CSV = "csv"
    PARQUET = "parquet"
    PICKLE = "pickle"
    BINARY = "binary"
    COMPRESSED = "compressed"


class IndexType(str, Enum):
    """Tipos de índices"""
    BTREE = "btree"
    HASH = "hash"
    FULLTEXT = "fulltext"
    SPATIAL = "spatial"
    COMPOSITE = "composite"


@dataclass
class StorageConfig:
    """Configuração de armazenamento"""
    storage_type: StorageType
    connection_string: Optional[str] = None
    database_name: Optional[str] = None
    table_name: Optional[str] = None
    collection_name: Optional[str] = None
    bucket_name: Optional[str] = None
    format: DataFormat = DataFormat.JSON
    compression: bool = False
    encryption: bool = False
    indexing: List[IndexType] = field(default_factory=list)
    retention_days: Optional[int] = None
    backup_enabled: bool = True
    custom_params: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'storage_type': self.storage_type.value,
            'connection_string': self.connection_string,
            'database_name': self.database_name,
            'table_name': self.table_name,
            'collection_name': self.collection_name,
            'bucket_name': self.bucket_name,
            'format': self.format.value,
            'compression': self.compression,
            'encryption': self.encryption,
            'indexing': [idx.value for idx in self.indexing],
            'retention_days': self.retention_days,
            'backup_enabled': self.backup_enabled,
            'custom_params': self.custom_params
        }


@dataclass
class StorageStats:
    """Estatísticas de armazenamento"""
    total_records: int = 0
    storage_size_bytes: int = 0
    compression_ratio: float = 1.0
    index_size_bytes: int = 0
    last_access: Optional[datetime] = None
    access_count: int = 0
    error_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'total_records': self.total_records,
            'storage_size_bytes': self.storage_size_bytes,
            'storage_size_mb': self.storage_size_bytes / (1024 * 1024),
            'storage_size_gb': self.storage_size_bytes / (1024 * 1024 * 1024),
            'compression_ratio': self.compression_ratio,
            'index_size_bytes': self.index_size_bytes,
            'last_access': self.last_access.isoformat() if self.last_access else None,
            'access_count': self.access_count,
            'error_count': self.error_count
        }


class LocalFileStorage:
    """Armazenamento em arquivos locais"""
    
    def __init__(self, base_path: str = "data/storage"):
        self.logger = get_logger("vhalinor.storage.local", "local_storage")
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.stats = StorageStats()
    
    async def store_data(self, data: Any, key: str, config: StorageConfig) -> str:
        """Armazena dados em arquivo local"""
        try:
            # Criar diretório por tipo de dado
            data_type_dir = self.base_path / "raw" if config.format == DataFormat.BINARY else "processed"
            data_type_dir.mkdir(exist_ok=True)
            
            # Gerar caminho do arquivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{key}_{timestamp}"
            
            if config.format == DataFormat.JSON:
                file_path = data_type_dir / f"{filename}.json"
                content = json.dumps(data, indent=2, default=str)
            elif config.format == DataFormat.CSV and PANDAS_AVAILABLE:
                file_path = data_type_dir / f"{filename}.csv"
                if isinstance(data, pd.DataFrame):
                    content = data.to_csv(index=False)
                else:
                    content = str(data)
            elif config.format == DataFormat.PICKLE:
                file_path = data_type_dir / f"{filename}.pkl"
                content = pickle.dumps(data)
            else:
                file_path = data_type_dir / f"{filename}.bin"
                content = str(data)
            
            # Aplicar compressão se necessário
            if config.compression:
                if config.format == DataFormat.JSON:
                    file_path = data_type_dir / f"{filename}.json.gz"
                    content = gzip.compress(content.encode('utf-8'))
                else:
                    file_path = data_type_dir / f"{filename}.gz"
                    content = gzip.compress(content.encode('utf-8'))
            
            # Escrever arquivo
            if isinstance(content, bytes):
                with open(file_path, 'wb') as f:
                    f.write(content)
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            # Atualizar estatísticas
            file_size = os.path.getsize(file_path)
            self.stats.total_records += 1
            self.stats.storage_size_bytes += file_size
            
            self.logger.info(f"Data stored to {file_path}")
            return str(file_path)
        
        except Exception as e:
            self.logger.error(f"Error storing data locally: {e}")
            self.stats.error_count += 1
            raise
    
    async def retrieve_data(self, key: str, config: StorageConfig) -> Any:
        """Recupera dados de arquivo local"""
        try:
            # Encontrar arquivo mais recente para a chave
            pattern = f"{key}_*"
            files = list(self.base_path.rglob(pattern))
            
            if not files:
                raise FileNotFoundError(f"No files found for key: {key}")
            
            # Ordenar por data de modificação (mais recente primeiro)
            latest_file = max(files, key=os.path.getmtime)
            
            # Ler arquivo
            if latest_file.suffix == '.gz':
                with gzip.open(latest_file, 'rt', encoding='utf-8') as f:
                    content = f.read()
            elif latest_file.suffix in ['.pkl']:
                with open(latest_file, 'rb') as f:
                    return pickle.load(f)
            else:
                with open(latest_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            
            # Parse conteúdo baseado no formato
            if latest_file.suffix in ['.json', '.json.gz']:
                data = json.loads(content)
            elif latest_file.suffix == '.csv':
                if PANDAS_AVAILABLE:
                    data = pd.read_csv(latest_file)
                else:
                    data = content
            else:
                data = content
            
            # Atualizar estatísticas
            self.stats.access_count += 1
            self.stats.last_access = datetime.now()
            
            return data
        
        except Exception as e:
            self.logger.error(f"Error retrieving data locally: {e}")
            self.stats.error_count += 1
            raise
    
    def get_stats(self) -> StorageStats:
        """Retorna estatísticas de armazenamento"""
        # Calcular tamanho total do diretório
        total_size = 0
        for file_path in self.base_path.rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        
        self.stats.storage_size_bytes = total_size
        return self.stats


class SQLiteStorage:
    """Armazenamento em banco SQLite"""
    
    def __init__(self, db_path: str = "data/storage/vhalinor.db"):
        self.logger = get_logger("vhalinor.storage.sqlite", "sqlite_storage")
        self.db_path = db_path
        self.connection = None
        self.stats = StorageStats()
        self._initialize_database()
    
    def _initialize_database(self):
        """Inicializa banco de dados"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            
            # Criar tabelas principais
            self._create_tables()
            
        except Exception as e:
            self.logger.error(f"Error initializing SQLite database: {e}")
            raise
    
    def _create_tables(self):
        """Cria tabelas do banco"""
        cursor = self.connection.cursor()
        
        # Tabela de metadados
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL,
                data_type TEXT NOT NULL,
                storage_path TEXT,
                format TEXT,
                size_bytes INTEGER,
                checksum TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                accessed_at TIMESTAMP,
                access_count INTEGER DEFAULT 0,
                INDEX(key)
            )
        ''')
        
        # Tabela de dados estruturados
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS structured_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL,
                data_type TEXT NOT NULL,
                content TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (key) REFERENCES data_metadata(key)
            )
        ''')
        
        self.connection.commit()
    
    async def store_data(self, data: Any, key: str, config: StorageConfig) -> str:
        """Armazena dados no SQLite"""
        try:
            cursor = self.connection.cursor()
            
            # Serializar dados
            if config.format == DataFormat.JSON:
                content = json.dumps(data, default=str)
            else:
                content = str(data)
            
            # Calcular checksum
            checksum = hashlib.md5(content.encode('utf-8')).hexdigest()
            
            # Inserir metadados
            cursor.execute('''
                INSERT OR REPLACE INTO data_metadata 
                (key, data_type, format, size_bytes, checksum, accessed_at, access_count)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            ''', (key, "structured", config.format.value, len(content), checksum, datetime.now()))
            
            # Inserir dados
            cursor.execute('''
                INSERT OR REPLACE INTO structured_data 
                (key, data_type, content, metadata)
                VALUES (?, ?, ?, ?)
            ''', (key, "structured", content, json.dumps(config.to_dict())))
            
            self.connection.commit()
            
            # Atualizar estatísticas
            self.stats.total_records += 1
            self.stats.storage_size_bytes += len(content.encode('utf-8'))
            
            self.logger.info(f"Data stored in SQLite with key: {key}")
            return key
        
        except Exception as e:
            self.logger.error(f"Error storing data in SQLite: {e}")
            self.stats.error_count += 1
            raise
    
    async def retrieve_data(self, key: str, config: StorageConfig) -> Any:
        """Recupera dados do SQLite"""
        try:
            cursor = self.connection.cursor()
            
            # Buscar dados
            cursor.execute('''
                SELECT content, metadata FROM structured_data 
                WHERE key = ? AND data_type = ?
            ''', (key, "structured"))
            
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"No data found for key: {key}")
            
            # Atualizar estatísticas de acesso
            cursor.execute('''
                UPDATE data_metadata 
                SET accessed_at = ?, access_count = access_count + 1
                WHERE key = ?
            ''', (datetime.now(), key))
            
            self.connection.commit()
            
            # Parse dados
            content = row['content']
            metadata = json.loads(row['metadata']) if row['metadata'] else {}
            format_type = metadata.get('format', 'json')
            
            if format_type == 'json':
                data = json.loads(content)
            else:
                data = content
            
            # Atualizar estatísticas
            self.stats.access_count += 1
            self.stats.last_access = datetime.now()
            
            return data
        
        except Exception as e:
            self.logger.error(f"Error retrieving data from SQLite: {e}")
            self.stats.error_count += 1
            raise
    
    def get_stats(self) -> StorageStats:
        """Retorna estatísticas do SQLite"""
        cursor = self.connection.cursor()
        
        # Contar registros
        cursor.execute('SELECT COUNT(*) as count FROM structured_data')
        self.stats.total_records = cursor.fetchone()['count']
        
        # Calcular tamanho do banco
        self.stats.storage_size_bytes = os.path.getsize(self.db_path)
        
        return self.stats


class MongoDBStorage:
    """Armazenamento em MongoDB"""
    
    def __init__(self, connection_string: str = "mongodb://localhost:27017", database_name: str = "vhalinor"):
        self.logger = get_logger("vhalinor.storage.mongodb", "mongodb_storage")
        self.connection_string = connection_string
        self.database_name = database_name
        self.client = None
        self.database = None
        self.stats = StorageStats()
        
        if MONGO_AVAILABLE:
            self._connect()
    
    def _connect(self):
        """Conecta ao MongoDB"""
        try:
            self.client = MongoClient(self.connection_string)
            self.database = self.client[self.database_name]
            
            # Testar conexão
            self.client.admin.command('ping')
            self.logger.info("Connected to MongoDB")
            
        except Exception as e:
            self.logger.error(f"Error connecting to MongoDB: {e}")
            raise
    
    async def store_data(self, data: Any, key: str, config: StorageConfig) -> str:
        """Armazena dados no MongoDB"""
        try:
            if not MONGO_AVAILABLE:
                raise ImportError("pymongo is required for MongoDB storage")
            
            collection_name = config.collection_name or "data_collection"
            collection = self.database[collection_name]
            
            # Preparar documento
            document = {
                'key': key,
                'data_type': config.custom_params.get('data_type', 'unknown'),
                'content': data,
                'metadata': config.to_dict(),
                'created_at': datetime.now(),
                'accessed_at': datetime.now(),
                'access_count': 1
            }
            
            # Inserir documento
            result = collection.insert_one(document)
            
            # Criar índices se necessário
            if config.indexing:
                await self._create_indexes(collection, config.indexing)
            
            # Atualizar estatísticas
            self.stats.total_records += 1
            self.stats.storage_size_bytes += len(str(document).encode('utf-8'))
            
            self.logger.info(f"Data stored in MongoDB with _id: {result.inserted_id}")
            return str(result.inserted_id)
        
        except Exception as e:
            self.logger.error(f"Error storing data in MongoDB: {e}")
            self.stats.error_count += 1
            raise
    
    async def retrieve_data(self, key: str, config: StorageConfig) -> Any:
        """Recupera dados do MongoDB"""
        try:
            if not MONGO_AVAILABLE:
                raise ImportError("pymongo is required for MongoDB storage")
            
            collection_name = config.collection_name or "data_collection"
            collection = self.database[collection_name]
            
            # Buscar documento
            document = collection.find_one({'key': key})
            if not document:
                raise ValueError(f"No data found for key: {key}")
            
            # Atualizar estatísticas de acesso
            collection.update_one(
                {'_id': document['_id']},
                {
                    '$set': {'accessed_at': datetime.now()},
                    '$inc': {'access_count': 1}
                }
            )
            
            # Atualizar estatísticas
            self.stats.access_count += 1
            self.stats.last_access = datetime.now()
            
            return document['content']
        
        except Exception as e:
            self.logger.error(f"Error retrieving data from MongoDB: {e}")
            self.stats.error_count += 1
            raise
    
    async def _create_indexes(self, collection, index_types: List[IndexType]):
        """Cria índices na coleção"""
        try:
            for index_type in index_types:
                if index_type == IndexType.HASH:
                    collection.create_index('key')
                elif index_type == IndexType.COMPOSITE:
                    collection.create_index([('key', 1), ('created_at', -1)])
                elif index_type == IndexType.FULLTEXT:
                    collection.create_index([('content', 'text')])
            
            self.logger.info(f"Created indexes: {[idx.value for idx in index_types]}")
        
        except Exception as e:
            self.logger.error(f"Error creating indexes: {e}")
    
    def get_stats(self) -> StorageStats:
        """Retorna estatísticas do MongoDB"""
        if not MONGO_AVAILABLE:
            return self.stats
        
        try:
            # Estatísticas do banco
            stats = self.database.command('dbStats')
            self.stats.storage_size_bytes = stats.get('dataSize', 0)
            
            # Contar documentos em todas as coleções
            total_docs = 0
            for collection_name in self.database.list_collection_names():
                collection = self.database[collection_name]
                total_docs += collection.count_documents({})
            
            self.stats.total_records = total_docs
            
        except Exception as e:
            self.logger.error(f"Error getting MongoDB stats: {e}")
        
        return self.stats


class RedisStorage:
    """Armazenamento em Redis (cache)"""
    
    def __init__(self, connection_string: str = "redis://localhost:6379"):
        self.logger = get_logger("vhalinor.storage.redis", "redis_storage")
        self.connection_string = connection_string
        self.client = None
        self.stats = StorageStats()
        
        if REDIS_AVAILABLE:
            self._connect()
    
    def _connect(self):
        """Conecta ao Redis"""
        try:
            self.client = redis.from_url(self.connection_string)
            self.client.ping()
            self.logger.info("Connected to Redis")
        except Exception as e:
            self.logger.error(f"Error connecting to Redis: {e}")
            raise
    
    async def store_data(self, data: Any, key: str, config: StorageConfig, expiry: Optional[int] = None) -> str:
        """Armazena dados no Redis"""
        try:
            if not REDIS_AVAILABLE:
                raise ImportError("redis is required for Redis storage")
            
            # Serializar dados
            if config.format == DataFormat.JSON:
                content = json.dumps(data, default=str)
            elif config.format == DataFormat.PICKLE:
                content = pickle.dumps(data)
            else:
                content = str(data)
            
            # Armazenar com TTL se especificado
            if expiry:
                self.client.setex(key, expiry, content)
            else:
                self.client.set(key, content)
            
            # Atualizar estatísticas
            self.stats.total_records += 1
            self.stats.storage_size_bytes += len(content)
            
            self.logger.info(f"Data stored in Redis with key: {key}")
            return key
        
        except Exception as e:
            self.logger.error(f"Error storing data in Redis: {e}")
            self.stats.error_count += 1
            raise
    
    async def retrieve_data(self, key: str, config: StorageConfig) -> Any:
        """Recupera dados do Redis"""
        try:
            if not REDIS_AVAILABLE:
                raise ImportError("redis is required for Redis storage")
            
            content = self.client.get(key)
            if content is None:
                raise ValueError(f"No data found for key: {key}")
            
            # Deserializar dados
            if config.format == DataFormat.JSON:
                data = json.loads(content)
            elif config.format == DataFormat.PICKLE:
                data = pickle.loads(content)
            else:
                data = content.decode('utf-8')
            
            # Atualizar estatísticas
            self.stats.access_count += 1
            self.stats.last_access = datetime.now()
            
            return data
        
        except Exception as e:
            self.logger.error(f"Error retrieving data from Redis: {e}")
            self.stats.error_count += 1
            raise
    
    def get_stats(self) -> StorageStats:
        """Retorna estatísticas do Redis"""
        if not REDIS_AVAILABLE:
            return self.stats
        
        try:
            info = self.client.info()
            self.stats.storage_size_bytes = info.get('used_memory', 0)
            self.stats.total_records = info.get('db0', {}).get('keys', 0)
        except Exception as e:
            self.logger.error(f"Error getting Redis stats: {e}")
        
        return self.stats


class DataStorageManager:
    """Gerenciador principal de armazenamento"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.storage.manager", "storage_manager")
        self.storages = {}
        self.default_config = StorageConfig(storage_type=StorageType.LOCAL_FILE)
        self.storage_stats = {}
    
    def register_storage(self, name: str, config: StorageConfig):
        """Registra um storage"""
        try:
            if config.storage_type == StorageType.LOCAL_FILE:
                storage = LocalFileStorage(config.custom_params.get('base_path', 'data/storage'))
            elif config.storage_type == StorageType.SQLITE:
                storage = SQLiteStorage(config.custom_params.get('db_path', 'data/storage/vhalinor.db'))
            elif config.storage_type == StorageType.MONGODB:
                storage = MongoDBStorage(config.connection_string, config.database_name)
            elif config.storage_type == StorageType.REDIS:
                storage = RedisStorage(config.connection_string)
            else:
                raise ValueError(f"Unsupported storage type: {config.storage_type}")
            
            self.storages[name] = {
                'storage': storage,
                'config': config,
                'stats': StorageStats()
            }
            
            self.logger.info(f"Registered storage: {name} ({config.storage_type.value})")
        
        except Exception as e:
            self.logger.error(f"Error registering storage {name}: {e}")
            raise
    
    @log_execution(component="storage", operation="store_data")
    async def store_data(self, data: Any, key: str, storage_name: str = "default", config: Optional[StorageConfig] = None) -> str:
        """Armazena dados usando storage especificado"""
        if storage_name not in self.storages:
            if storage_name == "default":
                self.register_storage("default", self.default_config)
            else:
                raise ValueError(f"Storage '{storage_name}' not registered")
        
        storage_info = self.storages[storage_name]
        storage_config = config or storage_info['config']
        storage = storage_info['storage']
        
        return await storage.store_data(data, key, storage_config)
    
    async def retrieve_data(self, key: str, storage_name: str = "default", config: Optional[StorageConfig] = None) -> Any:
        """Recupera dados usando storage especificado"""
        if storage_name not in self.storages:
            if storage_name == "default":
                self.register_storage("default", self.default_config)
            else:
                raise ValueError(f"Storage '{storage_name}' not registered")
        
        storage_info = self.storages[storage_name]
        storage_config = config or storage_info['config']
        storage = storage_info['storage']
        
        return await storage.retrieve_data(key, storage_config)
    
    async def store_batch(self, data_list: List[Tuple[Any, str]], storage_name: str = "default", config: Optional[StorageConfig] = None) -> List[str]:
        """Armazena dados em lote"""
        results = []
        
        for data, key in data_list:
            try:
                result = await self.store_data(data, key, storage_name, config)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Error storing batch item {key}: {e}")
                continue
        
        return results
    
    async def retrieve_batch(self, keys: List[str], storage_name: str = "default", config: Optional[StorageConfig] = None) -> List[Any]:
        """Recupera dados em lote"""
        results = []
        
        for key in keys:
            try:
                result = await self.retrieve_data(key, storage_name, config)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Error retrieving batch item {key}: {e}")
                continue
        
        return results
    
    def get_all_stats(self) -> Dict[str, StorageStats]:
        """Retorna estatísticas de todos os storages"""
        stats = {}
        
        for name, storage_info in self.storages.items():
            try:
                storage = storage_info['storage']
                stats[name] = storage.get_stats()
            except Exception as e:
                self.logger.error(f"Error getting stats for storage {name}: {e}")
                stats[name] = StorageStats(error_count=1)
        
        return stats
    
    def cleanup_expired_data(self, storage_name: str = None):
        """Limpa dados expirados"""
        storages_to_clean = [storage_name] if storage_name else list(self.storages.keys())
        
        for name in storages_to_clean:
            if name in self.storages:
                try:
                    # Implementar limpeza baseada em retention_days
                    config = self.storages[name]['config']
                    if config.retention_days:
                        cutoff_date = datetime.now() - timedelta(days=config.retention_days)
                        # Implementar lógica de limpeza específica para cada storage
                        self.logger.info(f"Cleanup expired data for storage: {name}")
                except Exception as e:
                    self.logger.error(f"Error cleaning storage {name}: {e}")
    
    def backup_storage(self, storage_name: str, backup_path: str):
        """Faz backup de storage"""
        if storage_name not in self.storages:
            raise ValueError(f"Storage '{storage_name}' not registered")
        
        try:
            storage_info = self.storages[storage_name]
            config = storage_info['config']
            
            if config.storage_type == StorageType.LOCAL_FILE:
                # Backup de arquivos locais
                storage = storage_info['storage']
                shutil.make_archive(backup_path, 'zip', storage.base_path)
            
            self.logger.info(f"Backup completed for storage: {storage_name}")
        
        except Exception as e:
            self.logger.error(f"Error backing up storage {storage_name}: {e}")
            raise
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Retorna informações sobre todos os storages"""
        info = {
            'total_storages': len(self.storages),
            'storage_types': {},
            'total_records': 0,
            'total_size_bytes': 0
        }
        
        for name, storage_info in self.storages.items():
            storage_type = storage_info['config'].storage_type.value
            info['storage_types'][storage_type] = info['storage_types'].get(storage_type, 0) + 1
            
            stats = storage_info['storage'].get_stats()
            info['total_records'] += stats.total_records
            info['total_size_bytes'] += stats.storage_size_bytes
        
        return info


# Função de conveniência
_storage_manager_instance = None

def get_storage_manager() -> DataStorageManager:
    """Obtém instância singleton do gerenciador de armazenamento"""
    global _storage_manager_instance
    if _storage_manager_instance is None:
        _storage_manager_instance = DataStorageManager()
        # Registrar storage padrão
        _storage_manager_instance.register_storage("default", StorageConfig(storage_type=StorageType.LOCAL_FILE))
    return _storage_manager_instance

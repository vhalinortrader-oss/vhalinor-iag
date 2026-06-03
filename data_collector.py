"""
Data Collector - Coleta de Dados Brutos
=======================================
Coleta de dados brutos de múltiplas fontes: texto, imagem, áudio, sensores
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union, BinaryIO
from dataclasses import dataclass, field
from enum import Enum
import os
from pathlib import Path
import hashlib
import base64
import mimetypes

# Importações condicionais
try:
    import cv2
    import numpy as np
    from PIL import Image
    import requests
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    import librosa
    import soundfile as sf
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

try:
    import serial
    import pyserial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

from config import settings
from core import get_logger, log_execution


class DataType(str, Enum):
    """Tipos de dados suportados"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    SENSOR = "sensor"
    STRUCTURED = "structured"
    BINARY = "binary"
    STREAM = "stream"


class DataSource(str, Enum):
    """Fontes de dados"""
    FILE = "file"
    URL = "url"
    CAMERA = "camera"
    MICROPHONE = "microphone"
    SERIAL_PORT = "serial_port"
    API = "api"
    DATABASE = "database"
    SENSOR_NETWORK = "sensor_network"
    WEB_SCRAPING = "web_scraping"


@dataclass
class DataSample:
    """Amostra de dados coletada"""
    id: str
    data_type: DataType
    source: DataSource
    content: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    file_path: Optional[str] = None
    size_bytes: int = 0
    checksum: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'id': self.id,
            'data_type': self.data_type.value,
            'source': self.source.value,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat(),
            'file_path': self.file_path,
            'size_bytes': self.size_bytes,
            'checksum': self.checksum
        }


class TextCollector:
    """Coletor de dados textuais"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.data.text_collector", "text_collector")
        self.supported_formats = ['.txt', '.csv', '.json', '.xml', '.html', '.md', '.py', '.js']
    
    async def collect_from_file(self, file_path: str) -> DataSample:
        """Coleta texto de arquivo"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            sample_id = hashlib.md5(f"{file_path}{time.time()}".encode()).hexdigest()
            
            return DataSample(
                id=sample_id,
                data_type=DataType.TEXT,
                source=DataSource.FILE,
                content=content,
                metadata={
                    'file_path': file_path,
                    'file_size': os.path.getsize(file_path),
                    'encoding': 'utf-8',
                    'line_count': len(content.splitlines()),
                    'char_count': len(content),
                    'word_count': len(content.split())
                },
                size_bytes=len(content.encode('utf-8')),
                checksum=hashlib.md5(content.encode('utf-8')).hexdigest()
            )
        except Exception as e:
            self.logger.error(f"Error collecting text from {file_path}: {e}")
            raise
    
    async def collect_from_url(self, url: str, timeout: int = 30) -> DataSample:
        """Coleta texto de URL"""
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            content = response.text
            
            sample_id = hashlib.md5(f"{url}{time.time()}".encode()).hexdigest()
            
            return DataSample(
                id=sample_id,
                data_type=DataType.TEXT,
                source=DataSource.URL,
                content=content,
                metadata={
                    'url': url,
                    'status_code': response.status_code,
                    'content_type': response.headers.get('content-type', ''),
                    'response_time': time.time(),
                    'char_count': len(content),
                    'word_count': len(content.split())
                },
                size_bytes=len(content.encode('utf-8')),
                checksum=hashlib.md5(content.encode('utf-8')).hexdigest()
            )
        except Exception as e:
            self.logger.error(f"Error collecting text from URL {url}: {e}")
            raise
    
    async def collect_from_api(self, api_url: str, headers: Dict[str, str] = None, params: Dict[str, Any] = None) -> DataSample:
        """Coleta texto de API"""
        try:
            response = requests.get(api_url, headers=headers or {}, params=params or {}, timeout=30)
            response.raise_for_status()
            
            if response.headers.get('content-type', '').startswith('application/json'):
                content = json.dumps(response.json(), indent=2)
            else:
                content = response.text
            
            sample_id = hashlib.md5(f"{api_url}{time.time()}".encode()).hexdigest()
            
            return DataSample(
                id=sample_id,
                data_type=DataType.TEXT,
                source=DataSource.API,
                content=content,
                metadata={
                    'api_url': api_url,
                    'status_code': response.status_code,
                    'content_type': response.headers.get('content-type', ''),
                    'params': params,
                    'response_time': time.time()
                },
                size_bytes=len(content.encode('utf-8')),
                checksum=hashlib.md5(content.encode('utf-8')).hexdigest()
            )
        except Exception as e:
            self.logger.error(f"Error collecting text from API {api_url}: {e}")
            raise


class ImageCollector:
    """Coletor de dados de imagem"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.data.image_collector", "image_collector")
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif', '.webp']
        self.camera = None
    
    async def collect_from_file(self, file_path: str) -> DataSample:
        """Coleta imagem de arquivo"""
        try:
            if not CV2_AVAILABLE:
                raise ImportError("OpenCV is required for image processing")
            
            # Ler imagem
            image = cv2.imread(file_path)
            if image is None:
                raise ValueError(f"Could not read image from {file_path}")
            
            # Obter metadados
            height, width, channels = image.shape
            file_size = os.path.getsize(file_path)
            
            sample_id = hashlib.md5(f"{file_path}{time.time()}".encode()).hexdigest()
            
            return DataSample(
                id=sample_id,
                data_type=DataType.IMAGE,
                source=DataSource.FILE,
                content=image,
                metadata={
                    'file_path': file_path,
                    'width': width,
                    'height': height,
                    'channels': channels,
                    'file_size': file_size,
                    'format': Path(file_path).suffix.lower(),
                    'color_space': 'BGR' if channels == 3 else 'Grayscale'
                },
                file_path=file_path,
                size_bytes=file_size,
                checksum=hashlib.md5(open(file_path, 'rb').read()).hexdigest()
            )
        except Exception as e:
            self.logger.error(f"Error collecting image from {file_path}: {e}")
            raise
    
    async def collect_from_url(self, url: str, timeout: int = 30) -> DataSample:
        """Coleta imagem de URL"""
        try:
            if not CV2_AVAILABLE:
                raise ImportError("OpenCV is required for image processing")
            
            response = requests.get(url, timeout=timeout, stream=True)
            response.raise_for_status()
            
            # Salvar temporariamente
            temp_path = f"temp_image_{int(time.time())}.jpg"
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Ler imagem
            image = cv2.imread(temp_path)
            height, width, channels = image.shape
            
            sample_id = hashlib.md5(f"{url}{time.time()}".encode()).hexdigest()
            
            # Limpar arquivo temporário
            os.unlink(temp_path)
            
            return DataSample(
                id=sample_id,
                data_type=DataType.IMAGE,
                source=DataSource.URL,
                content=image,
                metadata={
                    'url': url,
                    'width': width,
                    'height': height,
                    'channels': channels,
                    'content_type': response.headers.get('content-type', ''),
                    'response_time': time.time()
                },
                size_bytes=len(response.content),
                checksum=hashlib.md5(response.content).hexdigest()
            )
        except Exception as e:
            self.logger.error(f"Error collecting image from URL {url}: {e}")
            raise
    
    async def collect_from_camera(self, camera_id: int = 0, resolution: Tuple[int, int] = (640, 480)) -> DataSample:
        """Coleta imagem de câmera"""
        try:
            if not CV2_AVAILABLE:
                raise ImportError("OpenCV is required for camera capture")
            
            if self.camera is None:
                self.camera = cv2.VideoCapture(camera_id)
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
            
            ret, frame = self.camera.read()
            if not ret:
                raise RuntimeError("Failed to capture frame from camera")
            
            height, width, channels = frame.shape
            sample_id = hashlib.md5(f"camera_{camera_id}_{time.time()}".encode()).hexdigest()
            
            return DataSample(
                id=sample_id,
                data_type=DataType.IMAGE,
                source=DataSource.CAMERA,
                content=frame,
                metadata={
                    'camera_id': camera_id,
                    'width': width,
                    'height': height,
                    'channels': channels,
                    'resolution': resolution,
                    'capture_time': datetime.now().isoformat()
                },
                size_bytes=frame.nbytes,
                checksum=hashlib.md5(frame.tobytes()).hexdigest()
            )
        except Exception as e:
            self.logger.error(f"Error collecting image from camera {camera_id}: {e}")
            raise
    
    def release_camera(self):
        """Libera recursos da câmera"""
        if self.camera is not None:
            self.camera.release()
            self.camera = None


class AudioCollector:
    """Coletor de dados de áudio"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.data.audio_collector", "audio_collector")
        self.supported_formats = ['.wav', '.mp3', '.flac', '.ogg', '.m4a']
        self.microphone = None
    
    async def collect_from_file(self, file_path: str) -> DataSample:
        """Coleta áudio de arquivo"""
        try:
            if not AUDIO_AVAILABLE:
                raise ImportError("librosa and soundfile are required for audio processing")
            
            # Carregar áudio
            y, sr = librosa.load(file_path, sr=None)
            duration = len(y) / sr
            
            sample_id = hashlib.md5(f"{file_path}{time.time()}".encode()).hexdigest()
            
            return DataSample(
                id=sample_id,
                data_type=DataType.AUDIO,
                source=DataSource.FILE,
                content={'audio': y, 'sample_rate': sr},
                metadata={
                    'file_path': file_path,
                    'duration': duration,
                    'sample_rate': sr,
                    'channels': 1 if y.ndim == 1 else y.shape[0],
                    'format': Path(file_path).suffix.lower(),
                    'file_size': os.path.getsize(file_path)
                },
                file_path=file_path,
                size_bytes=os.path.getsize(file_path),
                checksum=hashlib.md5(open(file_path, 'rb').read()).hexdigest()
            )
        except Exception as e:
            self.logger.error(f"Error collecting audio from {file_path}: {e}")
            raise
    
    async def collect_from_microphone(self, duration: float = 5.0, sample_rate: int = 44100) -> DataSample:
        """Coleta áudio do microfone"""
        try:
            if not AUDIO_AVAILABLE:
                raise ImportError("librosa and soundfile are required for audio recording")
            
            # Simular gravação (em produção, usar pyaudio ou sounddevice)
            # Aqui criamos dados de exemplo
            samples = int(duration * sample_rate)
            audio_data = np.random.normal(0, 0.1, samples)  # Mock audio data
            
            sample_id = hashlib.md5(f"microphone_{time.time()}".encode()).hexdigest()
            
            return DataSample(
                id=sample_id,
                data_type=DataType.AUDIO,
                source=DataSource.MICROPHONE,
                content={'audio': audio_data, 'sample_rate': sample_rate},
                metadata={
                    'duration': duration,
                    'sample_rate': sample_rate,
                    'channels': 1,
                    'recording_time': datetime.now().isoformat()
                },
                size_bytes=audio_data.nbytes,
                checksum=hashlib.md5(audio_data.tobytes()).hexdigest()
            )
        except Exception as e:
            self.logger.error(f"Error collecting audio from microphone: {e}")
            raise


class SensorCollector:
    """Coletor de dados de sensores"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.data.sensor_collector", "sensor_collector")
        self.serial_connections = {}
        self.sensor_readings = []
    
    async def collect_from_serial_port(self, port: str, baudrate: int = 9600, timeout: float = 1.0) -> DataSample:
        """Coleta dados de porta serial"""
        try:
            if not SERIAL_AVAILABLE:
                raise ImportError("pyserial is required for serial communication")
            
            if port not in self.serial_connections:
                self.serial_connections[port] = serial.Serial(port, baudrate, timeout=timeout)
            
            serial_conn = self.serial_connections[port]
            
            # Ler dados
            if serial_conn.in_waiting > 0:
                raw_data = serial_conn.readline().decode('utf-8').strip()
            else:
                raw_data = ""
            
            sample_id = hashlib.md5(f"{port}_{time.time()}".encode()).hexdigest()
            
            # Tentar parsear como JSON, senão como texto simples
            try:
                parsed_data = json.loads(raw_data)
            except:
                parsed_data = {'raw_data': raw_data}
            
            return DataSample(
                id=sample_id,
                data_type=DataType.SENSOR,
                source=DataSource.SERIAL_PORT,
                content=parsed_data,
                metadata={
                    'port': port,
                    'baudrate': baudrate,
                    'timeout': timeout,
                    'raw_data': raw_data,
                    'timestamp': datetime.now().isoformat()
                },
                size_bytes=len(raw_data.encode('utf-8')),
                checksum=hashlib.md5(raw_data.encode('utf-8')).hexdigest()
            )
        except Exception as e:
            self.logger.error(f"Error collecting sensor data from serial port {port}: {e}")
            raise
    
    async def collect_mock_sensor_data(self, sensor_type: str, value_range: Tuple[float, float] = (0.0, 100.0)) -> DataSample:
        """Coleta dados de sensor simulados"""
        try:
            import random
            
            # Simular leitura de sensor
            value = random.uniform(*value_range)
            timestamp = datetime.now()
            
            sensor_data = {
                'sensor_type': sensor_type,
                'value': value,
                'unit': self._get_sensor_unit(sensor_type),
                'timestamp': timestamp.isoformat(),
                'quality': 'good' if random.random() > 0.1 else 'poor'
            }
            
            sample_id = hashlib.md5(f"{sensor_type}_{value}_{timestamp}".encode()).hexdigest()
            
            return DataSample(
                id=sample_id,
                data_type=DataType.SENSOR,
                source=DataSource.SENSOR_NETWORK,
                content=sensor_data,
                metadata={
                    'sensor_type': sensor_type,
                    'value_range': value_range,
                    'collection_method': 'mock'
                },
                size_bytes=len(json.dumps(sensor_data).encode('utf-8')),
                checksum=hashlib.md5(json.dumps(sensor_data).encode('utf-8')).hexdigest()
            )
        except Exception as e:
            self.logger.error(f"Error collecting mock sensor data: {e}")
            raise
    
    def _get_sensor_unit(self, sensor_type: str) -> str:
        """Obtém unidade do sensor"""
        units = {
            'temperature': '°C',
            'humidity': '%',
            'pressure': 'hPa',
            'light': 'lux',
            'motion': 'binary',
            'sound': 'dB',
            'vibration': 'Hz'
        }
        return units.get(sensor_type.lower(), 'unknown')
    
    def close_all_connections(self):
        """Fecha todas as conexões seriais"""
        for port, conn in self.serial_connections.items():
            try:
                conn.close()
            except:
                pass
        self.serial_connections.clear()


class StructuredDataCollector:
    """Coletor de dados estruturados"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.data.structured_collector", "structured_collector")
        self.supported_formats = ['.csv', '.json', '.xlsx', '.parquet', '.sql']
    
    async def collect_from_csv(self, file_path: str, **kwargs) -> DataSample:
        """Coleta dados de arquivo CSV"""
        try:
            if not PANDAS_AVAILABLE:
                raise ImportError("pandas is required for CSV processing")
            
            df = pd.read_csv(file_path, **kwargs)
            
            sample_id = hashlib.md5(f"{file_path}{time.time()}".encode()).hexdigest()
            
            return DataSample(
                id=sample_id,
                data_type=DataType.STRUCTURED,
                source=DataSource.FILE,
                content=df,
                metadata={
                    'file_path': file_path,
                    'shape': df.shape,
                    'columns': list(df.columns),
                    'dtypes': df.dtypes.to_dict(),
                    'file_size': os.path.getsize(file_path),
                    'null_counts': df.isnull().sum().to_dict()
                },
                file_path=file_path,
                size_bytes=os.path.getsize(file_path),
                checksum=hashlib.md5(open(file_path, 'rb').read()).hexdigest()
            )
        except Exception as e:
            self.logger.error(f"Error collecting CSV from {file_path}: {e}")
            raise
    
    async def collect_from_json(self, file_path: str) -> DataSample:
        """Coleta dados de arquivo JSON"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            sample_id = hashlib.md5(f"{file_path}{time.time()}".encode()).hexdigest()
            
            return DataSample(
                id=sample_id,
                data_type=DataType.STRUCTURED,
                source=DataSource.FILE,
                content=data,
                metadata={
                    'file_path': file_path,
                    'file_size': os.path.getsize(file_path),
                    'data_type': type(data).__name__,
                    'keys': list(data.keys()) if isinstance(data, dict) else None,
                    'length': len(data) if hasattr(data, '__len__') else None
                },
                file_path=file_path,
                size_bytes=os.path.getsize(file_path),
                checksum=hashlib.md5(open(file_path, 'rb').read()).hexdigest()
            )
        except Exception as e:
            self.logger.error(f"Error collecting JSON from {file_path}: {e}")
            raise


class DataCollector:
    """Coletor principal de dados"""
    
    def __init__(self, storage_path: str = "data/raw"):
        self.logger = get_logger("vhalinor.data.collector", "data_collector")
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Inicializar coletores especializados
        self.text_collector = TextCollector()
        self.image_collector = ImageCollector()
        self.audio_collector = AudioCollector()
        self.sensor_collector = SensorCollector()
        self.structured_collector = StructuredDataCollector()
        
        self.collection_history = []
        self.active_collections = {}
    
    @log_execution(component="data", operation="collect_data")
    async def collect_data(self, source: str, data_type: DataType, **kwargs) -> DataSample:
        """Coleta dados baseado no tipo e fonte"""
        self.logger.info(f"Collecting {data_type.value} data from {source}")
        
        try:
            # Determinar coletor apropriado
            if data_type == DataType.TEXT:
                if source.startswith('http'):
                    return await self.text_collector.collect_from_url(source, **kwargs)
                elif source.startswith('api:'):
                    return await self.text_collector.collect_from_api(source[4:], **kwargs)
                else:
                    return await self.text_collector.collect_from_file(source, **kwargs)
            
            elif data_type == DataType.IMAGE:
                if source.startswith('http'):
                    return await self.image_collector.collect_from_url(source, **kwargs)
                elif source.startswith('camera:'):
                    camera_id = int(source.split(':')[1]) if ':' in source else 0
                    return await self.image_collector.collect_from_camera(camera_id, **kwargs)
                else:
                    return await self.image_collector.collect_from_file(source, **kwargs)
            
            elif data_type == DataType.AUDIO:
                if source == 'microphone':
                    return await self.audio_collector.collect_from_microphone(**kwargs)
                else:
                    return await self.audio_collector.collect_from_file(source, **kwargs)
            
            elif data_type == DataType.SENSOR:
                if source.startswith('serial:'):
                    port = source.split(':')[1]
                    return await self.sensor_collector.collect_from_serial_port(port, **kwargs)
                elif source.startswith('mock:'):
                    sensor_type = source.split(':')[1]
                    return await self.sensor_collector.collect_mock_sensor_data(sensor_type, **kwargs)
                else:
                    raise ValueError(f"Unsupported sensor source: {source}")
            
            elif data_type == DataType.STRUCTURED:
                if source.endswith('.csv'):
                    return await self.structured_collector.collect_from_csv(source, **kwargs)
                elif source.endswith('.json'):
                    return await self.structured_collector.collect_from_json(source, **kwargs)
                else:
                    raise ValueError(f"Unsupported structured data format: {source}")
            
            else:
                raise ValueError(f"Unsupported data type: {data_type}")
        
        except Exception as e:
            self.logger.error(f"Error collecting data: {e}")
            raise
    
    async def collect_batch(self, sources: List[Tuple[str, DataType]], **kwargs) -> List[DataSample]:
        """Coleta dados em lote"""
        samples = []
        
        for source, data_type in sources:
            try:
                sample = await self.collect_data(source, data_type, **kwargs)
                samples.append(sample)
                
                # Salvar amostra se necessário
                if kwargs.get('save', True):
                    await self.save_sample(sample)
                
            except Exception as e:
                self.logger.error(f"Error collecting from {source}: {e}")
                continue
        
        return samples
    
    async def save_sample(self, sample: DataSample) -> str:
        """Salva amostra de dados"""
        # Criar diretório por tipo
        type_dir = self.storage_path / sample.data_type.value
        type_dir.mkdir(exist_ok=True)
        
        # Gerar nome de arquivo
        timestamp = sample.timestamp.strftime("%Y%m%d_%H%M%S")
        filename = f"{sample.id}_{timestamp}"
        
        if sample.data_type == DataType.TEXT:
            file_path = type_dir / f"{filename}.txt"
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(sample.content)
        
        elif sample.data_type == DataType.IMAGE:
            file_path = type_dir / f"{filename}.jpg"
            if CV2_AVAILABLE:
                cv2.imwrite(str(file_path), sample.content)
        
        elif sample.data_type == DataType.AUDIO:
            file_path = type_dir / f"{filename}.wav"
            if AUDIO_AVAILABLE:
                sf.write(str(file_path), sample.content['audio'], sample.content['sample_rate'])
        
        elif sample.data_type == DataType.SENSOR:
            file_path = type_dir / f"{filename}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(sample.content, f, indent=2)
        
        elif sample.data_type == DataType.STRUCTURED:
            if isinstance(sample.content, pd.DataFrame):
                file_path = type_dir / f"{filename}.csv"
                sample.content.to_csv(file_path, index=False)
            else:
                file_path = type_dir / f"{filename}.json"
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(sample.content, f, indent=2)
        
        else:
            file_path = type_dir / f"{filename}.bin"
            with open(file_path, 'wb') as f:
                f.write(sample.content)
        
        # Atualizar metadados
        sample.file_path = str(file_path)
        
        self.logger.info(f"Saved sample to {file_path}")
        return str(file_path)
    
    async def start_streaming_collection(self, source: str, data_type: DataType, interval: float = 1.0, duration: Optional[float] = None, **kwargs):
        """Inicia coleta contínua (streaming)"""
        collection_id = hashlib.md5(f"{source}_{data_type}_{time.time()}".encode()).hexdigest()
        
        async def collect_loop():
            start_time = time.time()
            samples_collected = 0
            
            while True:
                try:
                    sample = await self.collect_data(source, data_type, **kwargs)
                    await self.save_sample(sample)
                    
                    samples_collected += 1
                    self.active_collections[collection_id] = {
                        'source': source,
                        'data_type': data_type.value,
                        'samples_collected': samples_collected,
                        'start_time': start_time,
                        'last_collection': time.time()
                    }
                    
                    await asyncio.sleep(interval)
                    
                    # Verificar duração máxima
                    if duration and (time.time() - start_time) >= duration:
                        break
                
                except Exception as e:
                    self.logger.error(f"Error in streaming collection {collection_id}: {e}")
                    await asyncio.sleep(interval)
            
            # Limpar coleção ativa
            if collection_id in self.active_collections:
                del self.active_collections[collection_id]
        
        # Iniciar tarefa em background
        task = asyncio.create_task(collect_loop())
        return collection_id, task
    
    def stop_streaming_collection(self, collection_id: str):
        """Para coleta streaming"""
        # Implementar lógica para parar coleta
        if collection_id in self.active_collections:
            del self.active_collections[collection_id]
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de coleta"""
        stats = {
            'total_samples': len(self.collection_history),
            'active_collections': len(self.active_collections),
            'storage_path': str(self.storage_path),
            'supported_types': [dt.value for dt in DataType],
            'available_collectors': {
                'text': CV2_AVAILABLE,
                'image': CV2_AVAILABLE,
                'audio': AUDIO_AVAILABLE,
                'sensor': SERIAL_AVAILABLE,
                'structured': PANDAS_AVAILABLE
            }
        }
        
        # Adicionar estatísticas por tipo
        type_counts = {}
        for sample in self.collection_history:
            dt = sample.data_type.value
            type_counts[dt] = type_counts.get(dt, 0) + 1
        
        stats['samples_by_type'] = type_counts
        
        return stats
    
    def cleanup(self):
        """Limpa recursos"""
        self.image_collector.release_camera()
        self.sensor_collector.close_all_connections()


# Função de conveniência
_data_collector_instance = None

def get_data_collector(storage_path: str = "data/raw") -> DataCollector:
    """Obtém instância singleton do coletor de dados"""
    global _data_collector_instance
    if _data_collector_instance is None:
        _data_collector_instance = DataCollector(storage_path)
    return _data_collector_instance

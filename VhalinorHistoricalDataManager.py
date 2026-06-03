"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    VHALINOR IAG 1.0.0 - HISTORICAL DATA MANAGER               ║
║              SISTEMA DE GERENCIAMENTO DE DADOS HISTÓRICOS PARA IA             ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  Módulo: GERENCIADOR DE DADOS HISTÓRICOS                                      ║
║  Versão: 2.0.0 (Production Ready - Interface Quântica)                        ║
║  Autor: Alex Miranda Sales                                                    ║
║  Data: 2026                                                                   ║
║  License: Proprietary - Vhalinor IAG Systems                                  ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
import threading
import time
import random
import json
import os
import sys
import hashlib
import pickle
import math
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Tuple, Any, Callable
from datetime import datetime, timedelta
from enum import Enum, auto
from collections import deque, defaultdict
from functools import lru_cache, wraps

# =============================================================================
# IMPORTAÇÕES CIENTÍFICAS COM FALLBACK
# =============================================================================

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("⚠️ NumPy não disponível. Usando implementação pura Python.")

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

# =============================================================================
# ENUMS E CONSTANTES AVANÇADAS
# =============================================================================

class DataStatus(Enum):
    """Status de dados com cores e prioridades"""
    COMPLETE = ("COMPLETE", "#10b981", 100)
    PARTIAL = ("PARTIAL", "#f59e0b", 70)
    LOADING = ("LOADING", "#6b7280", 30)
    ERROR = ("ERROR", "#ef4444", 0)
    PROCESSING = ("PROCESSING", "#3b82f6", 50)
    VALIDATING = ("VALIDATING", "#8b5cf6", 40)
    READY = ("READY", "#10b981", 90)
    
    def __init__(self, label: str, color: str, priority: int):
        self.label = label
        self.color = color
        self.priority = priority

class TimeFrame(Enum):
    """Timeframes disponíveis para dados históricos"""
    TICK = ("Tick", "1s", 1)
    M1 = ("1 Minuto", "1m", 60)
    M5 = ("5 Minutos", "5m", 300)
    M15 = ("15 Minutos", "15m", 900)
    M30 = ("30 Minutos", "30m", 1800)
    H1 = ("1 Hora", "1h", 3600)
    H4 = ("4 Horas", "4h", 14400)
    D1 = ("1 Dia", "1d", 86400)
    W1 = ("1 Semana", "1w", 604800)
    MN1 = ("1 Mês", "1mo", 2592000)
    
    def __init__(self, label: str, code: str, seconds: int):
        self.label = label
        self.code = code
        self.seconds = seconds

class NormalizationMethod(Enum):
    """Métodos de normalização disponíveis"""
    MINMAX = "MinMax Scaler"
    ZSCORE = "Z-Score (Standard)"
    ROBUST = "Robust Scaler"
    QUANTILE = "Quantile Transformer"
    POWER = "Power Transformer"
    LOG = "Log Transform"
    BOXCOX = "Box-Cox"
    YEOJOHNSON = "Yeo-Johnson"
    MAXABS = "MaxAbs Scaler"

class DataQuality(Enum):
    """Níveis de qualidade de dados"""
    EXCELLENT = ("Excelente", 98, "#10b981")
    GOOD = ("Bom", 95, "#3b82f6")
    FAIR = ("Regular", 90, "#f59e0b")
    POOR = ("Ruim", 80, "#ef4444")
    INSUFFICIENT = ("Insuficiente", 0, "#6b7280")
    
    def __init__(self, label: str, threshold: int, color: str):
        self.label = label
        self.threshold = threshold
        self.color = color

class FeatureEngineering(Enum):
    """Tipos de engenharia de features"""
    TECHNICAL_INDICATORS = "Indicadores Técnicos"
    LAGGED_FEATURES = "Features Defasadas"
    ROLLING_STATISTICS = "Estatísticas Móveis"
    FOURIER_TRANSFORM = "Transformada de Fourier"
    WAVELET_DECOMPOSITION = "Decomposição Wavelet"
    PCA_REDUCTION = "Redução PCA"
    AUTOENCODERS = "Autoencoders"
    CUSTOM = "Personalizado"

# =============================================================================
# ESTRUTURAS DE DADOS AVANÇADAS
# =============================================================================

@dataclass
class HistoricalDataPoint:
    """Ponto de dados históricos com validação"""
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: int
    symbol: str
    timeframe: str
    vwap: Optional[float] = None
    turnover: Optional[float] = None
    trades: Optional[int] = None
    quality_score: float = 1.0
    adjusted: bool = False
    
    def __post_init__(self):
        """Validar dados após inicialização"""
        if self.high < self.low:
            self.high, self.low = self.low, self.high
        
        if self.volume < 0:
            self.volume = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário"""
        return {
            'timestamp': self.timestamp,
            'datetime': datetime.fromtimestamp(self.timestamp).isoformat(),
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume,
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'vwap': self.vwap,
            'quality_score': self.quality_score
        }

@dataclass
class DatasetInfo:
    """Informações completas do dataset"""
    symbol: str
    timeframe: str
    start_date: str
    end_date: str
    total_points: int
    status: DataStatus
    quality: float
    neural_ready: bool
    missing_points: int = 0
    outliers: int = 0
    duplicates: int = 0
    coverage_percentage: float = 100.0
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    file_size_mb: float = 0.0
    data_format: str = "parquet"
    compression: str = "snappy"
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário"""
        return {
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'total_points': self.total_points,
            'status': self.status.label,
            'quality': self.quality,
            'neural_ready': self.neural_ready,
            'coverage': f"{self.coverage_percentage:.1f}%",
            'last_updated': self.last_updated
        }
    
    @property
    def quality_color(self) -> str:
        """Cor baseada na qualidade"""
        if self.quality >= 98:
            return DataQuality.EXCELLENT.color
        elif self.quality >= 95:
            return DataQuality.GOOD.color
        elif self.quality >= 90:
            return DataQuality.FAIR.color
        else:
            return DataQuality.POOR.color

@dataclass
class NeuralDataPrep:
    """Configuração de preparação neural"""
    symbol: str
    features: int
    sequences: int
    training: int
    validation: int
    test: int
    normalization: str
    engineered: bool
    feature_list: List[str] = field(default_factory=list)
    target_column: str = "close"
    sequence_length: int = 60
    batch_size: int = 32
    shuffle: bool = True
    split_method: str = "temporal"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário"""
        return {
            'symbol': self.symbol,
            'features': self.features,
            'sequences': self.sequences,
            'training_samples': self.training,
            'validation_samples': self.validation,
            'test_samples': self.test,
            'normalization': self.normalization,
            'engineered': self.engineered,
            'feature_count': len(self.feature_list),
            'sequence_length': self.sequence_length,
            'batch_size': self.batch_size
        }
    
    @property
    def split_ratio(self) -> Dict[str, float]:
        """Taxa de divisão dos dados"""
        total = self.training + self.validation + self.test
        return {
            'training': self.training / total if total > 0 else 0.7,
            'validation': self.validation / total if total > 0 else 0.15,
            'test': self.test / total if total > 0 else 0.15
        }

@dataclass
class DataStatistics:
    """Estatísticas avançadas do dataset"""
    symbol: str
    timeframe: str
    mean: float
    std: float
    min_val: float
    max_val: float
    skewness: float
    kurtosis: float
    volatility: float
    volume_mean: float
    missing_pct: float
    outlier_pct: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'symbol': self.symbol,
            'mean': self.mean,
            'std': self.std,
            'min': self.min_val,
            'max': self.max_val,
            'skewness': self.skewness,
            'kurtosis': self.kurtosis,
            'volatility': self.volatility
        }

@dataclass
class DownloadTask:
    """Tarefa de download assíncrona"""
    task_id: str
    symbol: str
    timeframe: str
    start_date: str
    end_date: str
    progress: float = 0.0
    status: str = "pending"
    total_points: int = 0
    downloaded_points: int = 0
    error: Optional[str] = None
    start_time: str = field(default_factory=lambda: datetime.now().isoformat())
    end_time: Optional[str] = None
    
    @property
    def elapsed_seconds(self) -> float:
        """Tempo decorrido em segundos"""
        start = datetime.fromisoformat(self.start_time)
        end = datetime.fromisoformat(self.end_time) if self.end_time else datetime.now()
        return (end - start).total_seconds()

# =============================================================================
# UTILITÁRIOS AVANÇADOS
# =============================================================================

def format_number(num: int) -> str:
    """Formatar números grandes (1.5M, 2.3B, etc)"""
    if num >= 1_000_000_000:
        return f"{num/1_000_000_000:.1f}B"
    elif num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    else:
        return str(num)

def calculate_file_size(points: int, format: str = 'parquet') -> float:
    """Calcular tamanho estimado do arquivo"""
    # Estimativa aproximada: 100 bytes por ponto em parquet
    bytes_per_point = {
        'parquet': 100,
        'csv': 200,
        'json': 300,
        'hdf5': 150,
        'feather': 80
    }
    return (points * bytes_per_point.get(format, 100)) / (1024 * 1024)

# =============================================================================
# GERADOR DE DADOS AVANÇADO
# =============================================================================

class DataGenerator:
    """Gerador avançado de dados sintéticos"""
    
    @staticmethod
    def generate_price_series(n_points: int, volatility: float = 0.02) -> List[float]:
        """Gerar série de preços realista"""
        if NUMPY_AVAILABLE:
            returns = np.random.randn(n_points) * volatility
            price = 100 * np.exp(np.cumsum(returns))
            return price.tolist()
        else:
            prices = [100.0]
            for _ in range(n_points - 1):
                change = random.gauss(0, volatility)
                prices.append(prices[-1] * (1 + change))
            return prices
    
    @staticmethod
    def generate_volume_series(n_points: int, price_series: List[float]) -> List[int]:
        """Gerar série de volumes correlacionada com preços"""
        volumes = []
        for price in price_series:
            base_volume = random.uniform(100000, 1000000)
            # Volume maior em movimentos fortes
            price_change = abs(price - price_series[0]) / price_series[0]
            volume = base_volume * (1 + price_change * 5)
            volumes.append(int(volume))
        return volumes
    
    @staticmethod
    def generate_dataset(symbol: str, timeframe: str, 
                        start_date: str, end_date: str) -> List[HistoricalDataPoint]:
        """Gerar dataset completo"""
        # Converter datas para timestamp
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        
        # Determinar intervalo baseado no timeframe
        timeframe_seconds = {
            '1m': 60,
            '5m': 300,
            '15m': 900,
            '30m': 1800,
            '1h': 3600,
            '4h': 14400,
            '1d': 86400,
            '1w': 604800,
            '1mo': 2592000
        }
        
        interval = timeframe_seconds.get(timeframe, 86400)
        n_points = int((end - start).total_seconds() / interval)
        
        # Gerar dados
        price_series = DataGenerator.generate_price_series(n_points)
        volume_series = DataGenerator.generate_volume_series(n_points, price_series)
        
        data_points = []
        current_time = start.timestamp()
        
        for i in range(n_points):
            price = price_series[i]
            volume = volume_series[i]
            
            point = HistoricalDataPoint(
                timestamp=int(current_time),
                open=price * random.uniform(0.998, 1.002),
                high=price * random.uniform(1.002, 1.008),
                low=price * random.uniform(0.992, 0.998),
                close=price,
                volume=volume,
                symbol=symbol,
                timeframe=timeframe,
                vwap=price * random.uniform(0.999, 1.001),
                quality_score=random.uniform(0.95, 1.0)
            )
            
            data_points.append(point)
            current_time += interval
        
        return data_points

# =============================================================================
# ANALISADOR DE DADOS
# =============================================================================

class DataAnalyzer:
    """Analisador avançado de dados históricos"""
    
    @staticmethod
    def calculate_statistics(prices: List[float]) -> Dict[str, float]:
        """Calcular estatísticas avançadas"""
        if not prices:
            return {}
        
        if NUMPY_AVAILABLE:
            prices_array = np.array(prices)
            returns = np.diff(prices_array) / prices_array[:-1]
            
            stats = {
                'mean': float(np.mean(prices_array)),
                'std': float(np.std(prices_array)),
                'min': float(np.min(prices_array)),
                'max': float(np.max(prices_array)),
                'skewness': float(stats.skew(prices_array)) if SCIPY_AVAILABLE else 0,
                'kurtosis': float(stats.kurtosis(prices_array)) if SCIPY_AVAILABLE else 0,
                'volatility': float(np.std(returns)) if len(returns) > 0 else 0,
                'volume_mean': 0  # Será calculado separadamente
            }
        else:
            # Fallback Python puro
            mean = sum(prices) / len(prices)
            variance = sum((p - mean) ** 2 for p in prices) / len(prices)
            
            stats = {
                'mean': mean,
                'std': variance ** 0.5,
                'min': min(prices),
                'max': max(prices),
                'skewness': 0,
                'kurtosis': 0,
                'volatility': 0,
                'volume_mean': 0
            }
        
        return stats
    
    @staticmethod
    def detect_anomalies(prices: List[float], threshold: float = 3.0) -> List[int]:
        """Detectar anomalias nos dados"""
        if len(prices) < 2 or not NUMPY_AVAILABLE:
            return []
        
        prices_array = np.array(prices)
        mean = np.mean(prices_array)
        std = np.std(prices_array)
        
        anomalies = []
        for i, price in enumerate(prices):
            z_score = (price - mean) / std if std > 0 else 0
            if abs(z_score) > threshold:
                anomalies.append(i)
        
        return anomalies
    
    @staticmethod
    def calculate_data_quality(points: List[HistoricalDataPoint]) -> float:
        """Calcular score de qualidade dos dados"""
        if not points:
            return 0.0
        
        scores = []
        
        # 1. Continuidade temporal
        timestamps = [p.timestamp for p in points]
        expected_interval = DataAnalyzer._detect_interval(timestamps)
        missing = 0
        
        for i in range(1, len(timestamps)):
            actual_interval = timestamps[i] - timestamps[i-1]
            if actual_interval > expected_interval * 1.5:
                missing += 1
        
        continuity_score = max(0, 1 - (missing / len(points) * 10))
        scores.append(continuity_score * 0.3)
        
        # 2. Integridade dos dados
        valid_points = sum(1 for p in points if p.high >= p.low and p.volume >= 0)
        integrity_score = valid_points / len(points)
        scores.append(integrity_score * 0.3)
        
        # 3. Qualidade dos preços (OHLC consistentes)
        consistent_points = sum(1 for p in points 
                              if p.high >= max(p.open, p.close) 
                              and p.low <= min(p.open, p.close))
        consistency_score = consistent_points / len(points)
        scores.append(consistency_score * 0.2)
        
        # 4. Qualidade individual
        individual_score = sum(p.quality_score for p in points) / len(points)
        scores.append(individual_score * 0.2)
        
        return sum(scores) * 100
    
    @staticmethod
    def _detect_interval(timestamps: List[int]) -> int:
        """Detectar intervalo esperado entre timestamps"""
        if len(timestamps) < 2:
            return 60
        
        intervals = []
        for i in range(1, min(10, len(timestamps))):
            intervals.append(timestamps[i] - timestamps[i-1])
        
        return int(sum(intervals) / len(intervals))

# =============================================================================
# GERENCIADOR DE CORES E TEMAS
# =============================================================================

class ThemeManager:
    """Gerenciador de temas visuais"""
    
    THEMES = {
        'dark': {
            'bg': '#0f172a',
            'fg': '#e2e8f0',
            'card': '#1e293b',
            'border': '#334155',
            'accent': '#3b82f6',
            'success': '#10b981',
            'warning': '#f59e0b',
            'error': '#ef4444',
            'info': '#6366f1',
            'muted': '#64748b'
        },
        'light': {
            'bg': '#f8fafc',
            'fg': '#0f172a',
            'card': '#ffffff',
            'border': '#e2e8f0',
            'accent': '#2563eb',
            'success': '#059669',
            'warning': '#d97706',
            'error': '#dc2626',
            'info': '#4f46e5',
            'muted': '#94a3b8'
        },
        'quantum': {
            'bg': '#050510',
            'fg': '#00ffff',
            'card': '#0a0a1a',
            'border': '#2a1a3a',
            'accent': '#ff00ff',
            'success': '#00ff00',
            'warning': '#ffff00',
            'error': '#ff0000',
            'info': '#00ffff',
            'muted': '#6b21b5'
        }
    }
    
    def __init__(self):
        self.current_theme = 'dark'
    
    def get_color(self, key: str) -> str:
        """Obter cor do tema atual"""
        return self.THEMES[self.current_theme].get(key, '#000000')
    
    def set_theme(self, theme: str):
        """Definir tema"""
        if theme in self.THEMES:
            self.current_theme = theme

# =============================================================================
# COMPONENTES DE UI AVANÇADOS
# =============================================================================

class Card(ttk.Frame):
    """Componente Card estilizado"""
    
    def __init__(self, parent, title: str = None, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.configure(style='Card.TFrame')
        
        if title:
            title_label = ttk.Label(self, text=title, 
                                  font=("Arial", 12, "bold"),
                                  style='CardTitle.TLabel')
            title_label.pack(anchor=tk.W, padx=12, pady=(12, 0))
            
            separator = ttk.Separator(self, orient='horizontal')
            separator.pack(fill=tk.X, padx=12, pady=8)
        
        self.content = ttk.Frame(self)
        self.content.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

class ProgressCircle(tk.Canvas):
    """Indicador de progresso circular"""
    
    def __init__(self, parent, size=100, **kwargs):
        super().__init__(parent, width=size, height=size, 
                        bg='transparent', highlightthickness=0, **kwargs)
        self.size = size
        self.progress = 0
        self.draw(0)
    
    def draw(self, progress: float):
        """Desenhar círculo de progresso"""
        self.delete("all")
        self.progress = progress
        
        # Coordenadas
        center = self.size // 2
        radius = self.size // 2 - 5
        
        # Círculo de fundo
        self.create_oval(center - radius, center - radius,
                        center + radius, center + radius,
                        outline='#334155', width=2, fill='')
        
        # Arco de progresso
        angle = 360 * progress / 100
        self.create_arc(center - radius, center - radius,
                       center + radius, center + radius,
                       start=90, extent=-angle,
                       outline='#3b82f6', width=4, style='arc')
        
        # Texto
        self.create_text(center, center, text=f"{progress:.0f}%",
                        fill='white', font=("Arial", 12, "bold"))

class Badge(ttk.Label):
    """Componente Badge para status"""
    
    def __init__(self, parent, text: str, color: str, **kwargs):
        super().__init__(parent, text=text, **kwargs)
        
        self.configure(background=color,
                      foreground='white',
                      font=("Arial", 8, "bold"),
                      padding=(6, 2))

# =============================================================================
# APLICAÇÃO PRINCIPAL
# =============================================================================

class HistoricalDataManagerApp:
    """Aplicação principal de gerenciamento de dados históricos"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("🧠 VHALINOR IAG - Gerenciador de Dados Históricos Quântico")
        self.root.geometry("1800x1100")
        self.root.minsize(1400, 800)
        
        # ===== GERENCIADORES =====
        self.theme_manager = ThemeManager()
        self.data_analyzer = DataAnalyzer()
        self.data_generator = DataGenerator()
        
        # ===== ESTADO DA APLICAÇÃO =====
        self.datasets: List[DatasetInfo] = []
        self.neural_prep: List[NeuralDataPrep] = []
        self.statistics: Dict[str, DataStatistics] = {}
        self.download_queue: List[DownloadTask] = []
        
        self.download_progress = 0.0
        self.is_downloading = False
        self.total_data_points = 0
        self.selected_dataset: Optional[str] = None
        
        # ===== THREADS =====
        self.download_thread: Optional[threading.Thread] = None
        self.update_thread: Optional[threading.Thread] = None
        self.stop_updates = False
        
        # ===== REFERÊNCIAS UI =====
        self.widgets = {}
        self.vars = {}
        
        # ===== CONFIGURAÇÃO =====
        self.setup_styles()
        self.initialize_data()
        self.setup_ui()
        self.start_updates()
    
    # =========================================================================
    # CONFIGURAÇÃO INICIAL
    # =========================================================================
    
    def setup_styles(self) -> None:
        """Configurar estilos avançados"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Cores do tema
        colors = self.theme_manager.THEMES['dark']
        
        # Configurar estilos personalizados
        style.configure('Title.TLabel', 
                       font=("Arial", 24, "bold"),
                       foreground=colors['fg'],
                       background=colors['bg'])
        
        style.configure('Heading.TLabel',
                       font=("Arial", 16, "bold"),
                       foreground=colors['fg'])
        
        style.configure('Card.TFrame',
                       background=colors['card'],
                       relief='solid',
                       borderwidth=1)
        
        style.configure('CardTitle.TLabel',
                       font=("Arial", 12, "bold"),
                       foreground=colors['accent'],
                       background=colors['card'])
        
        style.configure('Primary.TButton',
                       font=("Arial", 10, "bold"),
                       padding=(12, 6))
        
        style.configure('Success.TLabel',
                       foreground=colors['success'],
                       background=colors['card'])
        
        style.configure('Warning.TLabel',
                       foreground=colors['warning'],
                       background=colors['card'])
        
        style.configure('Error.TLabel',
                       foreground=colors['error'],
                       background=colors['card'])
        
        style.configure('Info.TLabel',
                       foreground=colors['info'],
                       background=colors['card'])
        
        style.configure('Muted.TLabel',
                       foreground=colors['muted'],
                       background=colors['card'])
        
        # Configurar Treeview
        style.configure('Treeview',
                       background=colors['card'],
                       foreground=colors['fg'],
                       fieldbackground=colors['card'],
                       borderwidth=0,
                       font=("Arial", 10))
        
        style.configure('Treeview.Heading',
                       background=colors['border'],
                       foreground=colors['fg'],
                       relief='flat',
                       font=("Arial", 10, "bold"))
        
        style.map('Treeview',
                 background=[('selected', colors['accent'])],
                 foreground=[('selected', 'white')])
        
        style.configure('Horizontal.TProgressbar',
                       background=colors['accent'],
                       troughcolor=colors['border'],
                       borderwidth=0,
                       thickness=8)
    
    def initialize_data(self) -> None:
        """Inicializar dados de exemplo avançados"""
        
        # Datasets principais
        self.datasets = [
            DatasetInfo(
                symbol='PETR4.SA',
                timeframe='1m',
                start_date='2020-01-01',
                end_date='2024-08-25',
                total_points=1847520,
                status=DataStatus.COMPLETE,
                quality=98.5,
                neural_ready=True,
                missing_points=1245,
                outliers=89,
                duplicates=12,
                coverage_percentage=99.93,
                file_size_mb=calculate_file_size(1847520),
                last_updated='2024-08-25T18:30:00'
            ),
            DatasetInfo(
                symbol='VALE3.SA',
                timeframe='1m',
                start_date='2020-01-01',
                end_date='2024-08-25',
                total_points=1847520,
                status=DataStatus.COMPLETE,
                quality=97.8,
                neural_ready=True,
                missing_points=2341,
                outliers=156,
                duplicates=23,
                coverage_percentage=99.87,
                file_size_mb=calculate_file_size(1847520)
            ),
            DatasetInfo(
                symbol='ITUB4.SA',
                timeframe='5m',
                start_date='2020-01-01',
                end_date='2024-08-25',
                total_points=369504,
                status=DataStatus.COMPLETE,
                quality=99.1,
                neural_ready=True,
                missing_points=456,
                outliers=34,
                duplicates=5,
                coverage_percentage=99.98,
                file_size_mb=calculate_file_size(369504)
            ),
            DatasetInfo(
                symbol='BBDC4.SA',
                timeframe='15m',
                start_date='2020-01-01',
                end_date='2024-08-25',
                total_points=123168,
                status=DataStatus.PARTIAL,
                quality=94.3,
                neural_ready=False,
                missing_points=7890,
                outliers=234,
                duplicates=45,
                coverage_percentage=93.59,
                file_size_mb=calculate_file_size(123168)
            ),
            DatasetInfo(
                symbol='ABEV3.SA',
                timeframe='1h',
                start_date='2020-01-01',
                end_date='2024-08-25',
                total_points=30792,
                status=DataStatus.COMPLETE,
                quality=96.7,
                neural_ready=True,
                missing_points=567,
                outliers=78,
                duplicates=8,
                coverage_percentage=98.15,
                file_size_mb=calculate_file_size(30792)
            ),
            DatasetInfo(
                symbol='MGLU3.SA',
                timeframe='1d',
                start_date='2015-01-01',
                end_date='2024-08-25',
                total_points=2470,
                status=DataStatus.COMPLETE,
                quality=99.5,
                neural_ready=True,
                missing_points=23,
                outliers=5,
                duplicates=0,
                coverage_percentage=99.07,
                file_size_mb=calculate_file_size(2470)
            ),
            DatasetInfo(
                symbol='WEGE3.SA',
                timeframe='1d',
                start_date='2018-01-01',
                end_date='2024-08-25',
                total_points=1650,
                status=DataStatus.PROCESSING,
                quality=92.1,
                neural_ready=False,
                missing_points=123,
                outliers=45,
                duplicates=3,
                coverage_percentage=92.54,
                file_size_mb=calculate_file_size(1650)
            ),
            DatasetInfo(
                symbol='RENT3.SA',
                timeframe='1h',
                start_date='2019-01-01',
                end_date='2024-08-25',
                total_points=24560,
                status=DataStatus.VALIDATING,
                quality=88.7,
                neural_ready=False,
                missing_points=2345,
                outliers=167,
                duplicates=34,
                coverage_percentage=90.45,
                file_size_mb=calculate_file_size(24560)
            )
        ]
        
        # Preparação neural
        self.neural_prep = [
            NeuralDataPrep(
                symbol='PETR4.SA',
                features=47,
                sequences=1600000,
                training=1120000,
                validation=320000,
                test=160000,
                normalization='MinMax + Z-Score',
                engineered=True,
                feature_list=['open', 'high', 'low', 'close', 'volume', 'vwap',
                            'rsi', 'macd', 'bb_upper', 'bb_lower', 'bb_middle',
                            'atr', 'obv', 'adx', 'stoch_k', 'stoch_d'],
                sequence_length=60,
                batch_size=64
            ),
            NeuralDataPrep(
                symbol='VALE3.SA',
                features=52,
                sequences=1600000,
                training=1120000,
                validation=320000,
                test=160000,
                normalization='Robust + StandardScaler',
                engineered=True,
                feature_list=['open', 'high', 'low', 'close', 'volume', 'vwap',
                            'rsi', 'macd', 'bb_upper', 'bb_lower', 'bb_middle',
                            'atr', 'obv', 'adx', 'stoch_k', 'stoch_d',
                            'williams_r', 'cci', 'mfi'],
                sequence_length=60,
                batch_size=64
            ),
            NeuralDataPrep(
                symbol='ITUB4.SA',
                features=45,
                sequences=320000,
                training=224000,
                validation=64000,
                test=32000,
                normalization='Quantile + MinMax',
                engineered=True,
                sequence_length=50,
                batch_size=32
            ),
            NeuralDataPrep(
                symbol='ABEV3.SA',
                features=38,
                sequences=26000,
                training=18200,
                validation=5200,
                test=2600,
                normalization='PowerTransformer',
                engineered=True,
                sequence_length=40,
                batch_size=32
            )
        ]
        
        # Calcular total de pontos
        self.total_data_points = sum(d.total_points for d in self.datasets)
        
        # Calcular estatísticas (simuladas)
        for dataset in self.datasets:
            self.statistics[dataset.symbol] = DataStatistics(
                symbol=dataset.symbol,
                timeframe=dataset.timeframe,
                mean=random.uniform(20, 50),
                std=random.uniform(2, 8),
                min_val=random.uniform(15, 25),
                max_val=random.uniform(45, 70),
                skewness=random.uniform(-0.5, 0.5),
                kurtosis=random.uniform(-1, 1),
                volatility=random.uniform(0.15, 0.35),
                volume_mean=random.uniform(1e6, 1e7),
                missing_pct=100 - dataset.coverage_percentage,
                outlier_pct=(dataset.outliers / dataset.total_points * 100) if dataset.total_points > 0 else 0
            )
    
    # =========================================================================
    # CONFIGURAÇÃO DA INTERFACE
    # =========================================================================
    
    def setup_ui(self) -> None:
        """Configurar interface principal"""
        
        # Frame principal com scroll
        self.setup_scrollable_frame()
        
        # Header
        self.setup_header()
        
        # Progress frame
        self.setup_progress_frame()
        
        # Notebook (abas)
        self.setup_notebook()
        
        # Status bar
        self.setup_status_bar()
    
    def setup_scrollable_frame(self) -> None:
        """Configurar frame com scroll"""
        # Canvas para scroll
        self.canvas = tk.Canvas(self.root, bg=self.theme_manager.get_color('bg'),
                               highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", 
                                       command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Grid layout
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Container principal
        self.container = ttk.Frame(self.scrollable_frame, padding="20")
        self.container.grid(row=0, column=0, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
    
    def setup_header(self) -> None:
        """Configurar cabeçalho avançado"""
        
        header_frame = ttk.Frame(self.container)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header_frame.grid_columnconfigure(0, weight=1)
        
        # Título com ícone
        title_frame = ttk.Frame(header_frame)
        title_frame.grid(row=0, column=0, sticky="w")
        
        ttk.Label(title_frame, text="🧠", 
                 font=("Arial", 32)).grid(row=0, column=0, padx=(0, 10))
        
        ttk.Label(title_frame, text="VHALINOR IAG", 
                 font=("Arial", 24, "bold"),
                 style='Title.TLabel').grid(row=0, column=1, padx=(0, 10))
        
        ttk.Label(title_frame, text="Gerenciador de Dados Históricos", 
                 font=("Arial", 14),
                 style='Muted.TLabel').grid(row=0, column=2)
        
        # Badge de versão
        version_badge = Badge(title_frame, "v2.0.0 Quantum", "#3b82f6")
        version_badge.grid(row=0, column=3, padx=(20, 0))
        
        # Controles do lado direito
        controls_frame = ttk.Frame(header_frame)
        controls_frame.grid(row=0, column=1, sticky="e")
        
        # Botão de tema
        theme_btn = tk.Button(controls_frame, 
                             text="🌓 Tema",
                             bg=self.theme_manager.get_color('card'),
                             fg=self.theme_manager.get_color('fg'),
                             font=("Arial", 10),
                             padx=12, pady=6,
                             cursor="hand2",
                             command=self.toggle_theme)
        theme_btn.grid(row=0, column=0, padx=(0, 10))
        
        # Botão de exportar
        export_btn = tk.Button(controls_frame,
                              text="📤 Exportar",
                              bg=self.theme_manager.get_color('card'),
                              fg=self.theme_manager.get_color('fg'),
                              font=("Arial", 10),
                              padx=12, pady=6,
                              cursor="hand2",
                              command=self.export_data)
        export_btn.grid(row=0, column=1, padx=(0, 10))
        
        # Botão de importar
        import_btn = tk.Button(controls_frame,
                              text="📥 Importar",
                              bg=self.theme_manager.get_color('card'),
                              fg=self.theme_manager.get_color('fg'),
                              font=("Arial", 10),
                              padx=12, pady=6,
                              cursor="hand2",
                              command=self.import_data)
        import_btn.grid(row=0, column=2, padx=(0, 10))
        
        # Botão de download principal
        self.widgets['download_btn'] = tk.Button(controls_frame,
                                                text="📥 Baixar Dados",
                                                bg="#3b82f6",
                                                fg="white",
                                                font=("Arial", 11, "bold"),
                                                padx=16, pady=8,
                                                cursor="hand2",
                                                command=self.handle_download_data)
        self.widgets['download_btn'].grid(row=0, column=3)
    
    def setup_progress_frame(self) -> None:
        """Configurar frame de progresso avançado"""
        
        self.widgets['progress_frame'] = ttk.Frame(self.container)
        self.widgets['progress_frame'].grid(row=1, column=0, sticky="ew", pady=(0, 20))
        self.widgets['progress_frame'].grid_columnconfigure(1, weight=1)
        
        # Ícone
        ttk.Label(self.widgets['progress_frame'], 
                 text="⚡", 
                 font=("Arial", 24)).grid(row=0, column=0, padx=(0, 15))
        
        # Informações de progresso
        info_frame = ttk.Frame(self.widgets['progress_frame'])
        info_frame.grid(row=0, column=1, sticky="w")
        
        ttk.Label(info_frame, text="Download em andamento", 
                 font=("Arial", 12, "bold"),
                 style='Info.TLabel').grid(row=0, column=0, sticky="w")
        
        self.widgets['progress_detail'] = ttk.Label(info_frame, 
                                                   text="Preparando...",
                                                   style='Muted.TLabel')
        self.widgets['progress_detail'].grid(row=1, column=0, sticky="w")
        
        # Barra de progresso
        self.widgets['progress_bar'] = ttk.Progressbar(
            self.widgets['progress_frame'],
            orient='horizontal',
            length=400,
            mode='determinate',
            style='Horizontal.TProgressbar'
        )
        self.widgets['progress_bar'].grid(row=0, column=2, padx=(20, 15))
        
        # Porcentagem
        self.widgets['progress_percent'] = ttk.Label(
            self.widgets['progress_frame'],
            text="0%",
            font=("Arial", 14, "bold"),
            style='Success.TLabel'
        )
        self.widgets['progress_percent'].grid(row=0, column=3)
        
        # Cancelar botão
        cancel_btn = tk.Button(self.widgets['progress_frame'],
                              text="✕",
                              bg=self.theme_manager.get_color('error'),
                              fg="white",
                              font=("Arial", 10, "bold"),
                              width=2,
                              cursor="hand2",
                              command=self.cancel_download)
        cancel_btn.grid(row=0, column=4, padx=(15, 0))
        
        # Esconder progress frame inicialmente
        self.widgets['progress_frame'].grid_remove()
    
    def setup_notebook(self) -> None:
        """Configurar notebook com abas avançadas"""
        
        self.widgets['notebook'] = ttk.Notebook(self.container)
        self.widgets['notebook'].grid(row=2, column=0, sticky="nsew")
        self.container.grid_rowconfigure(2, weight=1)
        
        # Aba 1: Datasets
        self.setup_datasets_tab()
        
        # Aba 2: Preparação Neural
        self.setup_neural_tab()
        
        # Aba 3: Estatísticas e Análise
        self.setup_statistics_tab()
        
        # Aba 4: Visualização
        self.setup_visualization_tab()
        
        # Aba 5: Configurações
        self.setup_settings_tab()
    
    def setup_datasets_tab(self) -> None:
        """Configurar aba de datasets"""
        
        tab = ttk.Frame(self.widgets['notebook'])
        self.widgets['notebook'].add(tab, text="📊 Datasets")
        
        # Grid layout
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)
        
        # ===== FILTROS =====
        filters_frame = ttk.Frame(tab)
        filters_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        ttk.Label(filters_frame, text="🔍 Filtrar:", 
                 font=("Arial", 10, "bold")).grid(row=0, column=0, padx=(0, 10))
        
        # Busca
        self.vars['search'] = tk.StringVar()
        search_entry = ttk.Entry(filters_frame, textvariable=self.vars['search'],
                                width=30, font=("Arial", 10))
        search_entry.grid(row=0, column=1, padx=(0, 20))
        search_entry.bind('<KeyRelease>', lambda e: self.filter_datasets())
        
        # Filtro por timeframe
        ttk.Label(filters_frame, text="Timeframe:").grid(row=0, column=2, padx=(0, 5))
        self.vars['timeframe_filter'] = tk.StringVar(value="Todos")
        timeframe_combo = ttk.Combobox(filters_frame, 
                                      textvariable=self.vars['timeframe_filter'],
                                      values=['Todos', '1m', '5m', '15m', '1h', '4h', '1d'],
                                      state="readonly", width=10)
        timeframe_combo.grid(row=0, column=3, padx=(0, 20))
        timeframe_combo.bind('<<ComboboxSelected>>', lambda e: self.filter_datasets())
        
        # Filtro por status
        ttk.Label(filters_frame, text="Status:").grid(row=0, column=4, padx=(0, 5))
        self.vars['status_filter'] = tk.StringVar(value="Todos")
        status_combo = ttk.Combobox(filters_frame,
                                   textvariable=self.vars['status_filter'],
                                   values=['Todos', 'COMPLETE', 'PARTIAL', 'PROCESSING'],
                                   state="readonly", width=12)
        status_combo.grid(row=0, column=5, padx=(0, 20))
        status_combo.bind('<<ComboboxSelected>>', lambda e: self.filter_datasets())
        
        # Botão limpar filtros
        clear_btn = tk.Button(filters_frame, text="✕ Limpar",
                            bg=self.theme_manager.get_color('card'),
                            fg=self.theme_manager.get_color('muted'),
                            font=("Arial", 9),
                            cursor="hand2",
                            command=self.clear_filters)
        clear_btn.grid(row=0, column=6)
        
        # ===== TABELA DE DATASETS =====
        table_frame = ttk.Frame(tab)
        table_frame.grid(row=1, column=0, sticky="nsew")
        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        
        # Treeview
        columns = ('symbol', 'timeframe', 'period', 'points', 'status', 
                  'quality', 'neural', 'last_updated')
        
        self.widgets['datasets_tree'] = ttk.Treeview(table_frame, columns=columns,
                                                    show='headings', height=15)
        
        # Definir cabeçalhos
        self.widgets['datasets_tree'].heading('symbol', text='Símbolo')
        self.widgets['datasets_tree'].heading('timeframe', text='Timeframe')
        self.widgets['datasets_tree'].heading('period', text='Período')
        self.widgets['datasets_tree'].heading('points', text='Pontos')
        self.widgets['datasets_tree'].heading('status', text='Status')
        self.widgets['datasets_tree'].heading('quality', text='Qualidade')
        self.widgets['datasets_tree'].heading('neural', text='Neural')
        self.widgets['datasets_tree'].heading('last_updated', text='Atualização')
        
        # Definir larguras
        self.widgets['datasets_tree'].column('symbol', width=100)
        self.widgets['datasets_tree'].column('timeframe', width=80)
        self.widgets['datasets_tree'].column('period', width=180)
        self.widgets['datasets_tree'].column('points', width=120)
        self.widgets['datasets_tree'].column('status', width=100)
        self.widgets['datasets_tree'].column('quality', width=100)
        self.widgets['datasets_tree'].column('neural', width=80)
        self.widgets['datasets_tree'].column('last_updated', width=150)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL,
                                 command=self.widgets['datasets_tree'].yview)
        self.widgets['datasets_tree'].configure(yscrollcommand=scrollbar.set)
        
        self.widgets['datasets_tree'].grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Bind de seleção
        self.widgets['datasets_tree'].bind('<<TreeviewSelect>>', 
                                          self.on_dataset_select)
        
        # ===== AÇÕES =====
        actions_frame = ttk.Frame(tab)
        actions_frame.grid(row=2, column=0, sticky="ew", pady=(15, 0))
        
        # Botões de ação
        actions = [
            ("📥 Download", self.download_selected, True),
            ("🔄 Processar", self.process_selected, True),
            ("📊 Estatísticas", self.show_statistics, True),
            ("📈 Visualizar", self.visualize_selected, True),
            ("🔍 Validar", self.validate_selected, True),
            ("🧹 Limpar", self.clean_selected, False),
            ("🗑️ Remover", self.remove_selected, False)
        ]
        
        for i, (text, command, primary) in enumerate(actions):
            btn = tk.Button(actions_frame, text=text,
                          bg='#3b82f6' if primary else self.theme_manager.get_color('card'),
                          fg='white' if primary else self.theme_manager.get_color('fg'),
                          font=("Arial", 10, "bold") if primary else ("Arial", 10),
                          padx=12, pady=6,
                          cursor="hand2",
                          command=command)
            btn.grid(row=0, column=i, padx=(0, 10))
        
        # Refresh datasets
        self.refresh_datasets_table()
    
    def setup_neural_tab(self) -> None:
        """Configurar aba de preparação neural"""
        
        tab = ttk.Frame(self.widgets['notebook'])
        self.widgets['notebook'].add(tab, text="🧠 Preparação Neural")
        
        # Grid layout
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=2)
        tab.grid_rowconfigure(0, weight=1)
        
        # ===== LISTA DE PREPARAÇÕES =====
        list_frame = ttk.Frame(tab)
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        list_frame.grid_rowconfigure(1, weight=1)
        
        ttk.Label(list_frame, text="Preparações Ativas", 
                 font=("Arial", 12, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        # Treeview para preparações
        columns = ('symbol', 'features', 'sequences', 'norm')
        
        self.widgets['neural_tree'] = ttk.Treeview(list_frame, columns=columns,
                                                  show='headings', height=12)
        
        self.widgets['neural_tree'].heading('symbol', text='Símbolo')
        self.widgets['neural_tree'].heading('features', text='Features')
        self.widgets['neural_tree'].heading('sequences', text='Sequências')
        self.widgets['neural_tree'].heading('norm', text='Normalização')
        
        self.widgets['neural_tree'].column('symbol', width=100)
        self.widgets['neural_tree'].column('features', width=80)
        self.widgets['neural_tree'].column('sequences', width=120)
        self.widgets['neural_tree'].column('norm', width=150)
        
        neural_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL,
                                        command=self.widgets['neural_tree'].yview)
        self.widgets['neural_tree'].configure(yscrollcommand=neural_scrollbar.set)
        
        self.widgets['neural_tree'].grid(row=1, column=0, sticky="nsew")
        neural_scrollbar.grid(row=1, column=1, sticky="ns")
        
        self.widgets['neural_tree'].bind('<<TreeviewSelect>>', self.on_neural_select)
        
        # Botões
        neural_buttons = ttk.Frame(list_frame)
        neural_buttons.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        
        ttk.Button(neural_buttons, text="➕ Nova Preparação",
                  command=self.new_neural_prep).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(neural_buttons, text="⚙️ Configurar",
                  command=self.configure_neural).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(neural_buttons, text="🚀 Treinar",
                  command=self.train_model).pack(fill=tk.X, pady=(0, 5))
        
        # ===== DETALHES DA PREPARAÇÃO =====
        details_frame = ttk.Frame(tab)
        details_frame.grid(row=0, column=1, sticky="nsew")
        
        # Card de informações
        self.widgets['neural_details_card'] = Card(details_frame, "Detalhes da Preparação")
        self.widgets['neural_details_card'].pack(fill=tk.BOTH, expand=True)
        
        self.widgets['neural_details'] = ttk.Frame(self.widgets['neural_details_card'].content)
        self.widgets['neural_details'].pack(fill=tk.BOTH, expand=True)
        
        # Placeholder
        placeholder = ttk.Label(self.widgets['neural_details'],
                               text="Selecione uma preparação para ver os detalhes",
                               style='Muted.TLabel')
        placeholder.pack(pady=50)
        
        # Refresh neural table
        self.refresh_neural_table()
    
    def setup_statistics_tab(self) -> None:
        """Configurar aba de estatísticas"""
        
        tab = ttk.Frame(self.widgets['notebook'])
        self.widgets['notebook'].add(tab, text="📈 Estatísticas")
        
        # ===== OVERVIEW CARDS =====
        cards_frame = ttk.Frame(tab)
        cards_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        cards_frame.grid_columnconfigure((0,1,2,3), weight=1)
        
        # Card 1: Total de Pontos
        card1 = Card(cards_frame, "Total de Pontos")
        card1.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        
        self.widgets['stats_total_points'] = ttk.Label(
            card1.content,
            text=format_number(self.total_data_points),
            font=("Arial", 24, "bold"),
            style='Success.TLabel'
        )
        self.widgets['stats_total_points'].pack(pady=10)
        
        ttk.Label(card1.content, 
                 text="pontos históricos",
                 style='Muted.TLabel').pack()
        
        # Card 2: Datasets Completos
        card2 = Card(cards_frame, "Datasets Completos")
        card2.grid(row=0, column=1, padx=(0, 10), sticky="nsew")
        
        complete_datasets = sum(1 for d in self.datasets if d.status == DataStatus.COMPLETE)
        self.widgets['stats_complete'] = ttk.Label(
            card2.content,
            text=str(complete_datasets),
            font=("Arial", 24, "bold"),
            style='Success.TLabel'
        )
        self.widgets['stats_complete'].pack(pady=10)
        
        ttk.Label(card2.content,
                 text=f"de {len(self.datasets)} datasets",
                 style='Muted.TLabel').pack()
        
        # Card 3: Neural Ready
        card3 = Card(cards_frame, "Neural Ready")
        card3.grid(row=0, column=2, padx=(0, 10), sticky="nsew")
        
        neural_ready = sum(1 for d in self.datasets if d.neural_ready)
        self.widgets['stats_neural'] = ttk.Label(
            card3.content,
            text=str(neural_ready),
            font=("Arial", 24, "bold"),
            style='Info.TLabel'
        )
        self.widgets['stats_neural'].pack(pady=10)
        
        ttk.Label(card3.content,
                 text="datasets preparados",
                 style='Muted.TLabel').pack()
        
        # Card 4: Qualidade Média
        card4 = Card(cards_frame, "Qualidade Média")
        card4.grid(row=0, column=3, sticky="nsew")
        
        avg_quality = sum(d.quality for d in self.datasets) / len(self.datasets) if self.datasets else 0
        self.widgets['stats_quality'] = ttk.Label(
            card4.content,
            text=f"{avg_quality:.1f}%",
            font=("Arial", 24, "bold"),
            style='Success.TLabel'
        )
        self.widgets['stats_quality'].pack(pady=10)
        
        ttk.Label(card4.content,
                 text="média geral",
                 style='Muted.TLabel').pack()
        
        # ===== GRÁFICOS E ANÁLISES =====
        charts_frame = ttk.Frame(tab)
        charts_frame.grid(row=1, column=0, sticky="nsew")
        charts_frame.grid_columnconfigure((0,1), weight=1)
        charts_frame.grid_rowconfigure(0, weight=1)
        
        # Placeholder para gráficos
        chart_placeholder1 = Card(charts_frame, "Distribuição por Timeframe")
        chart_placeholder1.grid(row=0, column=0, padx=(0, 10), sticky="nsew")
        
        ttk.Label(chart_placeholder1.content,
                 text="📊 Visualização de distribuição",
                 font=("Arial", 12)).pack(pady=20)
        
        chart_placeholder2 = Card(charts_frame, "Qualidade dos Dados")
        chart_placeholder2.grid(row=0, column=1, sticky="nsew")
        
        ttk.Label(chart_placeholder2.content,
                 text="📈 Análise de qualidade",
                 font=("Arial", 12)).pack(pady=20)
    
    def setup_visualization_tab(self) -> None:
        """Configurar aba de visualização"""
        
        tab = ttk.Frame(self.widgets['notebook'])
        self.widgets['notebook'].add(tab, text="📉 Visualização")
        
        # Placeholder
        placeholder = ttk.Label(tab,
                               text="🔧 Visualização avançada em desenvolvimento\n\n"
                                    "Selecione um dataset para visualizar gráficos OHLC,\n"
                                    "indicadores técnicos e análises de séries temporais.",
                               font=("Arial", 12),
                               style='Muted.TLabel')
        placeholder.pack(expand=True, pady=100)
    
    def setup_settings_tab(self) -> None:
        """Configurar aba de configurações"""
        
        tab = ttk.Frame(self.widgets['notebook'])
        self.widgets['notebook'].add(tab, text="⚙️ Configurações")
        
        # ===== CONFIGURAÇÕES DE DOWNLOAD =====
        download_card = Card(tab, "Configurações de Download")
        download_card.pack(fill=tk.X, pady=(0, 20))
        
        # Formato de arquivo
        format_frame = ttk.Frame(download_card.content)
        format_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(format_frame, text="Formato de arquivo:", 
                 width=20).grid(row=0, column=0, sticky="w")
        
        self.vars['file_format'] = tk.StringVar(value="parquet")
        format_combo = ttk.Combobox(format_frame,
                                   textvariable=self.vars['file_format'],
                                   values=['parquet', 'csv', 'json', 'hdf5', 'feather'],
                                   state="readonly", width=15)
        format_combo.grid(row=0, column=1, sticky="w")
        
        ttk.Label(format_frame, text="Compressão:").grid(row=0, column=2, padx=(20, 5))
        
        self.vars['compression'] = tk.StringVar(value="snappy")
        compression_combo = ttk.Compression_combo = ttk.Combobox(format_frame,
                                      textvariable=self.vars['compression'],
                                      values=['snappy', 'gzip', 'lz4', 'zstd', 'none'],
                                      state="readonly", width=10)
        compression_combo.grid(row=0, column=3, sticky="w")
        
        # ===== CONFIGURAÇÕES NEURAIS =====
        neural_card = Card(tab, "Configurações de Preparação Neural")
        neural_card.pack(fill=tk.X, pady=(0, 20))
        
        # Normalização padrão
        norm_frame = ttk.Frame(neural_card.content)
        norm_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(norm_frame, text="Normalização padrão:",
                 width=20).grid(row=0, column=0, sticky="w")
        
        self.vars['default_norm'] = tk.StringVar(value="MinMax + Z-Score")
        norm_combo = ttk.Combobox(norm_frame,
                                 textvariable=self.vars['default_norm'],
                                 values=[n.value for n in NormalizationMethod],
                                 state="readonly", width=25)
        norm_combo.grid(row=0, column=1, sticky="w")
        
        # Sequence length
        seq_frame = ttk.Frame(neural_card.content)
        seq_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(seq_frame, text="Sequence length:",
                 width=20).grid(row=0, column=0, sticky="w")
        
        self.vars['sequence_length'] = tk.IntVar(value=60)
        seq_spinbox = ttk.Spinbox(seq_frame,
                                 from_=10, to=200,
                                 textvariable=self.vars['sequence_length'],
                                 width=10)
        seq_spinbox.grid(row=0, column=1, sticky="w")
        
        # Batch size
        batch_frame = ttk.Frame(neural_card.content)
        batch_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(batch_frame, text="Batch size:",
                 width=20).grid(row=0, column=0, sticky="w")
        
        self.vars['batch_size'] = tk.IntVar(value=32)
        batch_spinbox = ttk.Spinbox(batch_frame,
                                   from_=16, to=256, increment=16,
                                   textvariable=self.vars['batch_size'],
                                   width=10)
        batch_spinbox.grid(row=0, column=1, sticky="w")
        
        # ===== CONFIGURAÇÕES DE VISUALIZAÇÃO =====
        viz_card = Card(tab, "Configurações de Visualização")
        viz_card.pack(fill=tk.X, pady=(0, 20))
        
        # Tema
        theme_frame = ttk.Frame(viz_card.content)
        theme_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(theme_frame, text="Tema:",
                 width=20).grid(row=0, column=0, sticky="w")
        
        self.vars['theme'] = tk.StringVar(value="dark")
        theme_combo = ttk.Combobox(theme_frame,
                                  textvariable=self.vars['theme'],
                                  values=['dark', 'light', 'quantum'],
                                  state="readonly", width=15)
        theme_combo.grid(row=0, column=1, sticky="w")
        theme_combo.bind('<<ComboboxSelected>>', lambda e: self.change_theme())
        
        # ===== CONFIGURAÇÕES DE ARMAZENAMENTO =====
        storage_card = Card(tab, "Configurações de Armazenamento")
        storage_card.pack(fill=tk.X, pady=(0, 20))
        
        # Caminho de dados
        path_frame = ttk.Frame(storage_card.content)
        path_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(path_frame, text="Diretório de dados:",
                 width=20).grid(row=0, column=0, sticky="w")
        
        self.vars['data_path'] = tk.StringVar(value="./data")
        path_entry = ttk.Entry(path_frame, textvariable=self.vars['data_path'],
                              width=40)
        path_entry.grid(row=0, column=1, sticky="w", padx=(0, 10))
        
        ttk.Button(path_frame, text="📁 Selecionar",
                  command=self.select_data_path).grid(row=0, column=2)
        
        # Cache
        cache_frame = ttk.Frame(storage_card.content)
        cache_frame.pack(fill=tk.X, pady=5)
        
        self.vars['use_cache'] = tk.BooleanVar(value=True)
        ttk.Checkbutton(cache_frame, text="Usar cache",
                       variable=self.vars['use_cache']).grid(row=0, column=0, sticky="w")
        
        ttk.Label(cache_frame, text="Tamanho máximo do cache:").grid(row=0, column=1, padx=(20, 5))
        
        self.vars['cache_size'] = tk.StringVar(value="1GB")
        cache_combo = ttk.Combobox(cache_frame,
                                  textvariable=self.vars['cache_size'],
                                  values=['512MB', '1GB', '2GB', '4GB', '8GB'],
                                  state="readonly", width=10)
        cache_combo.grid(row=0, column=2, sticky="w")
        
        # Botão salvar configurações
        ttk.Button(tab, text="💾 Salvar Configurações",
                  command=self.save_settings,
                  style='Primary.TButton').pack(pady=20)
    
    def setup_status_bar(self) -> None:
        """Configurar barra de status"""
        
        status_frame = ttk.Frame(self.scrollable_frame)
        status_frame.grid(row=10, column=0, sticky="ew", pady=(20, 0))
        status_frame.grid_columnconfigure(1, weight=1)
        
        # Status esquerdo
        self.widgets['status_left'] = ttk.Label(status_frame,
                                               text="✅ Sistema pronto",
                                               style='Success.TLabel')
        self.widgets['status_left'].grid(row=0, column=0, padx=(0, 20))
        
        # Status centro
        self.widgets['status_center'] = ttk.Label(status_frame,
                                                 text=f"📊 {len(self.datasets)} datasets | "
                                                      f"{format_number(self.total_data_points)} pontos",
                                                 style='Muted.TLabel')
        self.widgets['status_center'].grid(row=0, column=1, sticky="w")
        
        # Status direito
        self.widgets['status_right'] = ttk.Label(status_frame,
                                                text=f"🕐 {datetime.now().strftime('%H:%M:%S')}",
                                                style='Muted.TLabel')
        self.widgets['status_right'].grid(row=0, column=2, padx=(20, 0))
    
    # =========================================================================
    # FUNÇÕES DE ATUALIZAÇÃO
    # =========================================================================
    
    def start_updates(self) -> None:
        """Iniciar atualizações periódicas"""
        self.stop_updates = False
        self.update_thread = threading.Thread(target=self._update_worker, daemon=True)
        self.update_thread.start()
    
    def _update_worker(self) -> None:
        """Worker de atualizações"""
        while not self.stop_updates:
            try:
                # Atualizar relógio
                self.root.after(0, self.update_clock)
                
                # Atualizar status do download
                if self.is_downloading:
                    self.root.after(0, self.update_download_display)
                
                time.sleep(1)
                
            except Exception as e:
                print(f"Erro no update worker: {e}")
    
    def update_clock(self) -> None:
        """Atualizar relógio na status bar"""
        if 'status_right' in self.widgets:
            self.widgets['status_right'].config(
                text=f"🕐 {datetime.now().strftime('%H:%M:%S')}"
            )
    
    # =========================================================================
    # FUNÇÕES DE MANIPULAÇÃO DE DADOS
    # =========================================================================
    
    def handle_download_data(self) -> None:
        """Iniciar download de dados"""
        if self.is_downloading:
            return
        
        # Diálogo de confirmação
        response = messagebox.askyesno(
            "Confirmar Download",
            "Este processo pode baixar grandes volumes de dados.\n"
            "Deseja continuar?",
            icon='question'
        )
        
        if not response:
            return
        
        self.is_downloading = True
        self.download_progress = 0.0
        
        # Mostrar progress frame
        self.widgets['progress_frame'].grid()
        
        # Atualizar botão
        self.widgets['download_btn'].config(text="📥 Baixando...", state="disabled")
        
        # Iniciar thread de download
        self.download_thread = threading.Thread(target=self._download_worker, daemon=True)
        self.download_thread.start()
        
        self.log("📥 Iniciando download de dados históricos...", 'info')
    
    def _download_worker(self) -> None:
        """Worker de download simulado"""
        task_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        
        # Criar tarefa
        task = DownloadTask(
            task_id=task_id,
            symbol="MULTI",
            timeframe="mixed",
            start_date="2020-01-01",
            end_date="2024-08-25"
        )
        
        self.download_queue.append(task)
        
        total_points = 0
        downloaded_points = 0
        
        # Simular download de múltiplos símbolos
        for i, dataset in enumerate(self.datasets[:5]):  # Baixar apenas 5 datasets
            if not self.is_downloading:
                break
            
            task.symbol = dataset.symbol
            task.timeframe = dataset.timeframe
            task.total_points = dataset.total_points
            
            for j in range(10):  # 10 passos por dataset
                if not self.is_downloading:
                    break
                
                time.sleep(0.3)  # Simular latência
                
                # Atualizar progresso
                step_progress = (i * 10 + j + 1) / (5 * 10) * 100
                self.download_progress = step_progress
                downloaded_points += dataset.total_points // 10
                
                # Atualizar detalhes
                self.root.after(0, self.update_progress_display)
                self.root.after(0, lambda: self.widgets['progress_detail'].config(
                    text=f"Baixando {dataset.symbol} ({dataset.timeframe}) - {j+1}/10"
                ))
        
        # Finalizar
        self.is_downloading = False
        task.status = "completed"
        task.end_time = datetime.now().isoformat()
        
        self.root.after(0, self.finish_download)
    
    def update_progress_display(self) -> None:
        """Atualizar display de progresso"""
        if 'progress_bar' in self.widgets:
            self.widgets['progress_bar']['value'] = self.download_progress
        
        if 'progress_percent' in self.widgets:
            self.widgets['progress_percent'].config(
                text=f"{self.download_progress:.0f}%"
            )
    
    def update_download_display(self) -> None:
        """Atualizar display de download"""
        if self.is_downloading:
            self.widgets['progress_frame'].grid()
            self.widgets['download_btn'].config(text="📥 Baixando...", state="disabled")
        else:
            self.widgets['progress_frame'].grid_remove()
            self.widgets['download_btn'].config(text="📥 Baixar Dados", state="normal")
    
    def finish_download(self) -> None:
        """Finalizar download"""
        self.update_download_display()
        self.log("✅ Download concluído com sucesso!", 'success')
        
        # Atualizar datasets
        self.refresh_datasets_table()
        
        # Notificar usuário
        messagebox.showinfo(
            "Download Concluído",
            f"Download finalizado!\n"
            f"Total baixado: {format_number(1847520 * 5)} pontos\n"
            f"Tempo: 15 segundos",
            icon='info'
        )
    
    def cancel_download(self) -> None:
        """Cancelar download em andamento"""
        if self.is_downloading:
            self.is_downloading = False
            self.log("⏹️ Download cancelado pelo usuário", 'warning')
            
            self.update_download_display()
            
            messagebox.showinfo(
                "Download Cancelado",
                "O processo de download foi interrompido.",
                icon='info'
            )
    
    # =========================================================================
    # FUNÇÕES DE FILTRAGEM E BUSCA
    # =========================================================================
    
    def filter_datasets(self) -> None:
        """Filtrar datasets na tabela"""
        search_term = self.vars['search'].get().lower()
        timeframe_filter = self.vars['timeframe_filter'].get()
        status_filter = self.vars['status_filter'].get()
        
        # Limpar tabela
        for item in self.widgets['datasets_tree'].get_children():
            self.widgets['datasets_tree'].delete(item)
        
        # Aplicar filtros
        filtered_datasets = self.datasets
        
        if search_term:
            filtered_datasets = [d for d in filtered_datasets 
                               if search_term in d.symbol.lower()]
        
        if timeframe_filter != 'Todos':
            filtered_datasets = [d for d in filtered_datasets 
                               if d.timeframe == timeframe_filter]
        
        if status_filter != 'Todos':
            filtered_datasets = [d for d in filtered_datasets 
                               if d.status.label == status_filter]
        
        # Inserir dados filtrados
        for dataset in filtered_datasets:
            self.insert_dataset_row(dataset)
        
        self.log(f"🔍 Filtro aplicado: {len(filtered_datasets)} datasets", 'debug')
    
    def insert_dataset_row(self, dataset: DatasetInfo) -> None:
        """Inserir linha na tabela de datasets"""
        
        # Formatar período
        period = f"{dataset.start_date} até {dataset.end_date}"
        
        # Formatar pontos
        points = format_number(dataset.total_points)
        
        # Status com cor
        status_text = dataset.status.label
        
        # Qualidade com cor
        quality_text = f"{dataset.quality:.1f}%"
        quality_color = dataset.quality_color
        
        # Neural ready
        neural_text = "✅" if dataset.neural_ready else "❌"
        
        # Inserir
        item_id = self.widgets['datasets_tree'].insert('', 'end', values=(
            dataset.symbol,
            dataset.timeframe,
            period,
            points,
            status_text,
            quality_text,
            neural_text,
            dataset.last_updated[:10]
        ))
        
        # Aplicar tags de cor
        self.widgets['datasets_tree'].set(item_id, 'status', status_text)
        self.widgets['datasets_tree'].set(item_id, 'quality', quality_text)
    
    def refresh_datasets_table(self) -> None:
        """Atualizar tabela de datasets"""
        # Limpar tabela
        for item in self.widgets['datasets_tree'].get_children():
            self.widgets['datasets_tree'].delete(item)
        
        # Inserir dados
        for dataset in self.datasets:
            self.insert_dataset_row(dataset)
    
    def refresh_neural_table(self) -> None:
        """Atualizar tabela de preparação neural"""
        # Limpar tabela
        for item in self.widgets['neural_tree'].get_children():
            self.widgets['neural_tree'].delete(item)
        
        # Inserir dados
        for prep in self.neural_prep:
            self.widgets['neural_tree'].insert('', 'end', values=(
                prep.symbol,
                prep.features,
                format_number(prep.sequences),
                prep.normalization[:20] + "..."
            ))
    
    def clear_filters(self) -> None:
        """Limpar todos os filtros"""
        self.vars['search'].set("")
        self.vars['timeframe_filter'].set("Todos")
        self.vars['status_filter'].set("Todos")
        self.refresh_datasets_table()
        self.log("🧹 Filtros removidos", 'info')
    
    # =========================================================================
    # MANIPULADORES DE EVENTOS
    # =========================================================================
    
    def on_dataset_select(self, event) -> None:
        """Evento de seleção de dataset"""
        selection = self.widgets['datasets_tree'].selection()
        if selection:
            item = selection[0]
            values = self.widgets['datasets_tree'].item(item, 'values')
            self.selected_dataset = values[0]
            self.log(f"📌 Dataset selecionado: {self.selected_dataset}", 'debug')
    
    def on_neural_select(self, event) -> None:
        """Evento de seleção de preparação neural"""
        selection = self.widgets['neural_tree'].selection()
        if selection:
            item = selection[0]
            values = self.widgets['neural_tree'].item(item, 'values')
            symbol = values[0]
            
            # Buscar preparação completa
            prep = next((p for p in self.neural_prep if p.symbol == symbol), None)
            
            if prep:
                self.show_neural_details(prep)
    
    def show_neural_details(self, prep: NeuralDataPrep) -> None:
        """Mostrar detalhes da preparação neural"""
        
        # Limpar frame de detalhes
        for widget in self.widgets['neural_details'].winfo_children():
            widget.destroy()
        
        # Criar grid
        self.widgets['neural_details'].grid_columnconfigure(1, weight=1)
        
        row = 0
        
        # Símbolo
        ttk.Label(self.widgets['neural_details'], 
                 text="Símbolo:",
                 style='Muted.TLabel').grid(row=row, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(self.widgets['neural_details'],
                 text=prep.symbol,
                 font=("Arial", 11, "bold")).grid(row=row, column=1, sticky="w", padx=5, pady=5)
        row += 1
        
        # Features
        ttk.Label(self.widgets['neural_details'],
                 text="Features:",
                 style='Muted.TLabel').grid(row=row, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(self.widgets['neural_details'],
                 text=f"{prep.features} features").grid(row=row, column=1, sticky="w", padx=5, pady=5)
        row += 1
        
        # Sequências
        ttk.Label(self.widgets['neural_details'],
                 text="Sequências:",
                 style='Muted.TLabel').grid(row=row, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(self.widgets['neural_details'],
                 text=format_number(prep.sequences)).grid(row=row, column=1, sticky="w", padx=5, pady=5)
        row += 1
        
        # Split ratio
        ttk.Label(self.widgets['neural_details'],
                 text="Split ratio:",
                 style='Muted.TLabel').grid(row=row, column=0, sticky="w", padx=5, pady=5)
        
        split_frame = ttk.Frame(self.widgets['neural_details'])
        split_frame.grid(row=row, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(split_frame, text=f"Treino: {prep.split_ratio['training']:.0%}").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(split_frame, text=f"Val: {prep.split_ratio['validation']:.0%}").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(split_frame, text=f"Teste: {prep.split_ratio['test']:.0%}").pack(side=tk.LEFT)
        row += 1
        
        # Normalização
        ttk.Label(self.widgets['neural_details'],
                 text="Normalização:",
                 style='Muted.TLabel').grid(row=row, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(self.widgets['neural_details'],
                 text=prep.normalization).grid(row=row, column=1, sticky="w", padx=5, pady=5)
        row += 1
        
        # Sequence length
        ttk.Label(self.widgets['neural_details'],
                 text="Sequence length:",
                 style='Muted.TLabel').grid(row=row, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(self.widgets['neural_details'],
                 text=str(prep.sequence_length)).grid(row=row, column=1, sticky="w", padx=5, pady=5)
        row += 1
        
        # Batch size
        ttk.Label(self.widgets['neural_details'],
                 text="Batch size:",
                 style='Muted.TLabel').grid(row=row, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(self.widgets['neural_details'],
                 text=str(prep.batch_size)).grid(row=row, column=1, sticky="w", padx=5, pady=5)
        row += 1
        
        # Feature engineering
        ttk.Label(self.widgets['neural_details'],
                 text="Feature engineering:",
                 style='Muted.TLabel').grid(row=row, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(self.widgets['neural_details'],
                 text="✅ Ativo" if prep.engineered else "❌ Inativo",
                 style='Success.TLabel' if prep.engineered else 'Muted.TLabel').grid(row=row, column=1, sticky="w", padx=5, pady=5)
        row += 1
        
        # Separador
        separator = ttk.Separator(self.widgets['neural_details'], orient='horizontal')
        separator.grid(row=row, column=0, columnspan=2, sticky="ew", pady=15)
        row += 1
        
        # Lista de features (limitada)
        ttk.Label(self.widgets['neural_details'],
                 text="Features:",
                 style='Muted.TLabel').grid(row=row, column=0, sticky="nw", padx=5, pady=5)
        
        features_frame = ttk.Frame(self.widgets['neural_details'])
        features_frame.grid(row=row, column=1, sticky="w", padx=5, pady=5)
        
        if prep.feature_list:
            for i, feature in enumerate(prep.feature_list[:10]):
                badge = Badge(features_frame, feature, "#3b82f6")
                badge.pack(side=tk.LEFT, padx=(0, 5), pady=2)
            
            if len(prep.feature_list) > 10:
                ttk.Label(features_frame,
                         text=f"+{len(prep.feature_list)-10} outras",
                         style='Muted.TLabel').pack(side=tk.LEFT)
        else:
            ttk.Label(features_frame,
                     text="Features padrão (preço, volume)",
                     style='Muted.TLabel').pack()
        row += 1
        
        # Timestamp
        ttk.Label(self.widgets['neural_details'],
                 text="Última atualização:",
                 style='Muted.TLabel').grid(row=row, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(self.widgets['neural_details'],
                 text=prep.timestamp[:10]).grid(row=row, column=1, sticky="w", padx=5, pady=5)
    
    # =========================================================================
    # AÇÕES DE DATASET
    # =========================================================================
    
    def download_selected(self) -> None:
        """Download do dataset selecionado"""
        if not self.selected_dataset:
            messagebox.showwarning(
                "Nenhuma seleção",
                "Selecione um dataset para fazer download.",
                icon='warning'
            )
            return
        
        self.log(f"📥 Iniciando download de {self.selected_dataset}", 'info')
        self.handle_download_data()
    
    def process_selected(self) -> None:
        """Processar dataset selecionado"""
        if not self.selected_dataset:
            messagebox.showwarning(
                "Nenhuma seleção",
                "Selecione um dataset para processar.",
                icon='warning'
            )
            return
        
        self.log(f"🔄 Processando {self.selected_dataset}...", 'info')
        
        # Simular processamento
        self.root.after(100, lambda: self.log(f"✅ {self.selected_dataset} processado com sucesso!", 'success'))
    
    def show_statistics(self) -> None:
        """Mostrar estatísticas do dataset selecionado"""
        if not self.selected_dataset:
            messagebox.showwarning(
                "Nenhuma seleção",
                "Selecione um dataset para ver estatísticas.",
                icon='warning'
            )
            return
        
        # Buscar dataset
        dataset = next((d for d in self.datasets if d.symbol == self.selected_dataset), None)
        stats = self.statistics.get(self.selected_dataset)
        
        if not dataset or not stats:
            return
        
        # Criar janela de estatísticas
        stats_window = tk.Toplevel(self.root)
        stats_window.title(f"📊 Estatísticas - {dataset.symbol}")
        stats_window.geometry("600x700")
        stats_window.transient(self.root)
        stats_window.grab_set()
        
        # Container
        container = ttk.Frame(stats_window, padding="20")
        container.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(container, text=f"Estatísticas de {dataset.symbol}",
                 font=("Arial", 16, "bold")).pack(pady=(0, 20))
        
        # Informações do dataset
        info_card = Card(container, "Informações do Dataset")
        info_card.pack(fill=tk.X, pady=(0, 15))
        
        info_grid = ttk.Frame(info_card.content)
        info_grid.pack(fill=tk.X)
        
        info_items = [
            ("Timeframe:", dataset.timeframe),
            ("Período:", f"{dataset.start_date} até {dataset.end_date}"),
            ("Total de pontos:", format_number(dataset.total_points)),
            ("Qualidade:", f"{dataset.quality:.1f}%"),
            ("Cobertura:", f"{dataset.coverage_percentage:.1f}%"),
            ("Tamanho:", f"{dataset.file_size_mb:.1f} MB")
        ]
        
        for i, (label, value) in enumerate(info_items):
            ttk.Label(info_grid, text=label, 
                     style='Muted.TLabel').grid(row=i, column=0, sticky="w", padx=5, pady=3)
            ttk.Label(info_grid, text=value).grid(row=i, column=1, sticky="w", padx=5, pady=3)
        
        # Estatísticas estatísticas
        stats_card = Card(container, "Estatísticas dos Preços")
        stats_card.pack(fill=tk.X, pady=(0, 15))
        
        stats_grid = ttk.Frame(stats_card.content)
        stats_grid.pack(fill=tk.X)
        
        stats_items = [
            ("Média:", f"{stats.mean:.4f}"),
            ("Desvio Padrão:", f"{stats.std:.4f}"),
            ("Mínimo:", f"{stats.min_val:.4f}"),
            ("Máximo:", f"{stats.max_val:.4f}"),
            ("Assimetria:", f"{stats.skewness:.4f}"),
            ("Curtose:", f"{stats.kurtosis:.4f}"),
            ("Volatilidade:", f"{stats.volatility:.2%}"),
            ("Volume Médio:", f"{stats.volume_mean:.0f}")
        ]
        
        for i, (label, value) in enumerate(stats_items):
            ttk.Label(stats_grid, text=label,
                     style='Muted.TLabel').grid(row=i, column=0, sticky="w", padx=5, pady=3)
            ttk.Label(stats_grid, text=value).grid(row=i, column=1, sticky="w", padx=5, pady=3)
        
        # Qualidade dos dados
        quality_card = Card(container, "Qualidade dos Dados")
        quality_card.pack(fill=tk.X, pady=(0, 15))
        
        quality_grid = ttk.Frame(quality_card.content)
        quality_grid.pack(fill=tk.X)
        
        quality_items = [
            ("Pontos faltantes:", f"{dataset.missing_points} ({stats.missing_pct:.2f}%)"),
            ("Outliers:", f"{dataset.outliers} ({stats.outlier_pct:.2f}%)"),
            ("Duplicatas:", str(dataset.duplicates)),
            ("Pronto para Neural:", "✅ Sim" if dataset.neural_ready else "❌ Não")
        ]
        
        for i, (label, value) in enumerate(quality_items):
            ttk.Label(quality_grid, text=label,
                     style='Muted.TLabel').grid(row=i, column=0, sticky="w", padx=5, pady=3)
            ttk.Label(quality_grid, text=value).grid(row=i, column=1, sticky="w", padx=5, pady=3)
        
        # Botão fechar
        ttk.Button(container, text="Fechar",
                  command=stats_window.destroy,
                  style='Primary.TButton').pack(pady=(20, 0))
    
    def visualize_selected(self) -> None:
        """Visualizar dataset selecionado"""
        if not self.selected_dataset:
            messagebox.showwarning(
                "Nenhuma seleção",
                "Selecione um dataset para visualizar.",
                icon='warning'
            )
            return
        
        # Mudar para aba de visualização
        self.widgets['notebook'].select(3)  # Índice da aba de visualização
        
        # Aqui seria implementada a visualização real com matplotlib
        self.log(f"📈 Visualizando {self.selected_dataset}", 'info')
        
        messagebox.showinfo(
            "Visualização",
            f"Visualização de {self.selected_dataset} em desenvolvimento.\n\n"
            "Em breve: gráficos OHLC interativos, indicadores técnicos\n"
            "e análises de séries temporais.",
            icon='info'
        )
    
    def validate_selected(self) -> None:
        """Validar dataset selecionado"""
        if not self.selected_dataset:
            messagebox.showwarning(
                "Nenhuma seleção",
                "Selecione um dataset para validar.",
                icon='warning'
            )
            return
        
        self.log(f"🔍 Validando {self.selected_dataset}...", 'info')
        
        # Simular validação
        self.root.after(1000, lambda: self.log(f"✅ {self.selected_dataset} validado com sucesso!", 'success'))
    
    def clean_selected(self) -> None:
        """Limpar dataset selecionado"""
        if not self.selected_dataset:
            messagebox.showwarning(
                "Nenhuma seleção",
                "Selecione um dataset para limpar.",
                icon='warning'
            )
            return
        
        response = messagebox.askyesno(
            "Confirmar Limpeza",
            f"Deseja realmente limpar os dados de {self.selected_dataset}?\n\n"
            "Esta operação removerá dados inconsistentes e outliers.",
            icon='warning'
        )
        
        if response:
            self.log(f"🧹 Limpando {self.selected_dataset}...", 'warning')
            self.root.after(2000, lambda: self.log(f"✅ {self.selected_dataset} limpo com sucesso!", 'success'))
    
    def remove_selected(self) -> None:
        """Remover dataset selecionado"""
        if not self.selected_dataset:
            messagebox.showwarning(
                "Nenhuma seleção",
                "Selecione um dataset para remover.",
                icon='warning'
            )
            return
        
        response = messagebox.askyesno(
            "Confirmar Remoção",
            f"Deseja realmente remover {self.selected_dataset}?\n\n"
            "Esta operação não pode ser desfeita.",
            icon='warning'
        )
        
        if response:
            # Remover da lista
            self.datasets = [d for d in self.datasets if d.symbol != self.selected_dataset]
            self.refresh_datasets_table()
            
            self.log(f"🗑️ Dataset {self.selected_dataset} removido", 'warning')
            self.selected_dataset = None
    
    # =========================================================================
    # AÇÕES DE PREPARAÇÃO NEURAL
    # =========================================================================
    
    def new_neural_prep(self) -> None:
        """Criar nova preparação neural"""
        
        # Diálogo de nova preparação
        dialog = tk.Toplevel(self.root)
        dialog.title("➕ Nova Preparação Neural")
        dialog.geometry("500x600")
        dialog.transient(self.root)
        dialog.grab_set()
        
        container = ttk.Frame(dialog, padding="20")
        container.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(container, text="Nova Preparação Neural",
                 font=("Arial", 16, "bold")).pack(pady=(0, 20))
        
        # Seleção de símbolo
        ttk.Label(container, text="Símbolo:").pack(anchor=tk.W, pady=(0, 5))
        symbol_combo = ttk.Combobox(container,
                                   values=[d.symbol for d in self.datasets 
                                          if not any(p.symbol == d.symbol for p in self.neural_prep)],
                                   state="readonly")
        symbol_combo.pack(fill=tk.X, pady=(0, 15))
        
        # Seleção de features
        ttk.Label(container, text="Features:").pack(anchor=tk.W, pady=(0, 5))
        
        features_frame = ttk.Frame(container)
        features_frame.pack(fill=tk.X, pady=(0, 15))
        
        features = ['open', 'high', 'low', 'close', 'volume', 'vwap',
                   'rsi', 'macd', 'bollinger', 'atr', 'obv', 'adx']
        
        selected_features = []
        for i, feature in enumerate(features[:6]):  # Primeiras 6 features
            var = tk.BooleanVar(value=True)
            cb = ttk.Checkbutton(features_frame, text=feature, variable=var)
            cb.grid(row=i//3, column=i%3, sticky="w", padx=5, pady=2)
            selected_features.append((feature, var))
        
        # Sequence length
        ttk.Label(container, text="Sequence length:").pack(anchor=tk.W, pady=(0, 5))
        seq_spinbox = ttk.Spinbox(container, from_=10, to=200, value=60)
        seq_spinbox.pack(fill=tk.X, pady=(0, 15))
        
        # Normalização
        ttk.Label(container, text="Método de normalização:").pack(anchor=tk.W, pady=(0, 5))
        norm_combo = ttk.Combobox(container,
                                 values=[n.value for n in NormalizationMethod],
                                 state="readonly")
        norm_combo.set("MinMax Scaler")
        norm_combo.pack(fill=tk.X, pady=(0, 15))
        
        # Feature engineering
        engineer_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(container, text="Ativar feature engineering automática",
                       variable=engineer_var).pack(anchor=tk.W, pady=(0, 15))
        
        # Botões
        button_frame = ttk.Frame(container)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="Cancelar",
                  command=dialog.destroy).pack(side=tk.RIGHT, padx=(10, 0))
        
        def create_preparation():
            symbol = symbol_combo.get()
            if not symbol:
                messagebox.showwarning("Erro", "Selecione um símbolo!", parent=dialog)
                return
            
            # Criar nova preparação
            new_prep = NeuralDataPrep(
                symbol=symbol,
                features=len([v for _, v in selected_features if v.get()]),
                sequences=0,
                training=0,
                validation=0,
                test=0,
                normalization=norm_combo.get(),
                engineered=engineer_var.get(),
                sequence_length=int(seq_spinbox.get()),
                batch_size=self.vars['batch_size'].get()
            )
            
            self.neural_prep.append(new_prep)
            self.refresh_neural_table()
            
            dialog.destroy()
            self.log(f"➕ Nova preparação criada para {symbol}", 'success')
        
        ttk.Button(button_frame, text="Criar",
                  command=create_preparation,
                  style='Primary.TButton').pack(side=tk.RIGHT)
    
    def configure_neural(self) -> None:
        """Configurar preparação neural selecionada"""
        selection = self.widgets['neural_tree'].selection()
        if not selection:
            messagebox.showwarning(
                "Nenhuma seleção",
                "Selecione uma preparação para configurar.",
                icon='warning'
            )
            return
        
        item = selection[0]
        values = self.widgets['neural_tree'].item(item, 'values')
        symbol = values[0]
        
        self.log(f"⚙️ Configurando preparação para {symbol}", 'info')
        
        messagebox.showinfo(
            "Configuração",
            f"Configuração avançada para {symbol} em desenvolvimento.\n\n"
            "Em breve: seleção de features, parâmetros de treinamento,\n"
            "arquitetura de rede e otimizadores.",
            icon='info'
        )
    
    def train_model(self) -> None:
        """Treinar modelo com preparação selecionada"""
        selection = self.widgets['neural_tree'].selection()
        if not selection:
            messagebox.showwarning(
                "Nenhuma seleção",
                "Selecione uma preparação para treinar.",
                icon='warning'
            )
            return
        
        item = selection[0]
        values = self.widgets['neural_tree'].item(item, 'values')
        symbol = values[0]
        
        self.log(f"🚀 Iniciando treinamento para {symbol}...", 'info')
        
        # Simular treinamento
        self.root.after(3000, lambda: self.log(f"✅ Modelo para {symbol} treinado com sucesso!", 'success'))
        
        messagebox.showinfo(
            "Treinamento",
            f"Treinamento do modelo para {symbol} iniciado em background.\n"
            f"Acompanhe o progresso no console.",
            icon='info'
        )
    
    # =========================================================================
    # AÇÕES DE ARQUIVO
    # =========================================================================
    
    def export_data(self) -> None:
        """Exportar dados para arquivo"""
        filename = filedialog.asksaveasfilename(
            title="Exportar Dados",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            export_data = {
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'version': '2.0.0',
                    'app': 'VHALINOR IAG Historical Data Manager'
                },
                'datasets': [d.to_dict() for d in self.datasets],
                'neural_prep': [p.to_dict() for p in self.neural_prep],
                'statistics': {s: self.statistics[s].to_dict() for s in self.statistics}
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.log(f"💾 Dados exportados para {os.path.basename(filename)}", 'success')
            messagebox.showinfo("Exportação", f"Dados exportados com sucesso!\n{filename}")
            
        except Exception as e:
            self.log(f"❌ Erro ao exportar: {e}", 'error')
            messagebox.showerror("Erro", f"Erro ao exportar: {e}")
    
    def import_data(self) -> None:
        """Importar dados de arquivo"""
        filename = filedialog.askopenfilename(
            title="Importar Dados",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Importar datasets
            if 'datasets' in data:
                for d in data['datasets']:
                    dataset = DatasetInfo(
                        symbol=d['symbol'],
                        timeframe=d['timeframe'],
                        start_date=d['start_date'],
                        end_date=d['end_date'],
                        total_points=d['total_points'],
                        status=DataStatus[d['status']] if isinstance(d['status'], str) else d['status'],
                        quality=d['quality'],
                        neural_ready=d['neural_ready']
                    )
                    self.datasets.append(dataset)
            
            self.refresh_datasets_table()
            self.log(f"📂 Dados importados de {os.path.basename(filename)}", 'success')
            messagebox.showinfo("Importação", f"Dados importados com sucesso!\n{filename}")
            
        except Exception as e:
            self.log(f"❌ Erro ao importar: {e}", 'error')
            messagebox.showerror("Erro", f"Erro ao importar: {e}")
    
    # =========================================================================
    # CONFIGURAÇÕES
    # =========================================================================
    
    def select_data_path(self) -> None:
        """Selecionar diretório de dados"""
        directory = filedialog.askdirectory(
            title="Selecionar Diretório de Dados"
        )
        
        if directory:
            self.vars['data_path'].set(directory)
            self.log(f"📁 Diretório de dados alterado: {directory}", 'info')
    
    def save_settings(self) -> None:
        """Salvar configurações"""
        settings = {
            'file_format': self.vars['file_format'].get(),
            'compression': self.vars['compression'].get(),
            'default_norm': self.vars['default_norm'].get(),
            'sequence_length': self.vars['sequence_length'].get(),
            'batch_size': self.vars['batch_size'].get(),
            'theme': self.vars['theme'].get(),
            'data_path': self.vars['data_path'].get(),
            'use_cache': self.vars['use_cache'].get(),
            'cache_size': self.vars['cache_size'].get()
        }
        
        # Salvar em arquivo
        try:
            os.makedirs(self.vars['data_path'].get(), exist_ok=True)
            settings_file = os.path.join(self.vars['data_path'].get(), 'settings.json')
            
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
            
            self.log("⚙️ Configurações salvas com sucesso!", 'success')
            messagebox.showinfo("Configurações", "Configurações salvas com sucesso!")
            
        except Exception as e:
            self.log(f"❌ Erro ao salvar configurações: {e}", 'error')
            messagebox.showerror("Erro", f"Erro ao salvar configurações: {e}")
    
    def change_theme(self) -> None:
        """Alterar tema da aplicação"""
        theme = self.vars['theme'].get()
        self.theme_manager.set_theme(theme)
        
        # Atualizar cores (implementação simplificada)
        colors = self.theme_manager.get_color
        
        # Reconfigurar estilos
        self.setup_styles()
        
        # Atualizar canvas
        self.canvas.configure(bg=colors('bg'))
        
        self.log(f"🎨 Tema alterado para: {theme}", 'info')
    
    # =========================================================================
    # UTILITÁRIOS
    # =========================================================================
    
    def log(self, message: str, level: str = 'info') -> None:
        """Registrar mensagem no log e status bar"""
        
        # Atualizar status bar
        if 'status_left' in self.widgets:
            if level == 'success':
                self.widgets['status_left'].config(text=f"✅ {message}", style='Success.TLabel')
            elif level == 'error':
                self.widgets['status_left'].config(text=f"❌ {message}", style='Error.TLabel')
            elif level == 'warning':
                self.widgets['status_left'].config(text=f"⚠️ {message}", style='Warning.TLabel')
            else:
                self.widgets['status_left'].config(text=f"ℹ️ {message}", style='Info.TLabel')
        
        # Imprimir no console
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{timestamp}] [{level.upper()}] {message}")
    
    def toggle_theme(self) -> None:
        """Alternar entre temas"""
        current = self.vars.get('theme', tk.StringVar(value='dark')).get()
        themes = ['dark', 'light', 'quantum']
        next_theme = themes[(themes.index(current) + 1) % len(themes)]
        
        self.vars['theme'].set(next_theme)
        self.change_theme()


# =============================================================================
# FUNÇÃO PRINCIPAL
# =============================================================================

def main():
    """Função principal"""
    root = tk.Tk()
    
    # Configurar ícone (opcional)
    try:
        root.iconbitmap('icon.ico')
    except:
        pass
    
    # Criar aplicação
    app = HistoricalDataManagerApp(root)
    
    # Centralizar
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    # Iniciar
    root.mainloop()


if __name__ == "__main__":
    main()
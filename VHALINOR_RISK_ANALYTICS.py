#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VHALINOR RISK ANALYTICS - SISTEMA AVANÇADO DE ANÁLISE DE RISCOS
================================================================
Plataforma Inteligente para Análise Preditiva, Stress Testing e Otimização
com Integração Quântica e Machine Learning

Autor: VHALINOR.IAG Core Team
Versão: 4.5.0
Licença: Proprietary
"""

import asyncio
import json
import logging
import os
import warnings
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from functools import lru_cache, wraps
import hashlib

import numpy as np
import pandas as pd
from scipy import stats, optimize
from scipy.stats import norm, t, gaussian_kde
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.covariance import EllipticEnvelope
from sklearn.metrics import mean_squared_error, mean_absolute_error
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.figure import Figure
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Suprimir warnings apenas em produção
if os.getenv('VHALINOR_ENV') == 'production':
    warnings.filterwarnings('ignore')

# ============================================================================
# IMPORTAÇÕES CONDICIONAIS PARA MÓDULOS OPCIONAIS
# ============================================================================

try:
    import qiskit
    from qiskit import QuantumCircuit, execute, Aer
    from qiskit.circuit.library import ZZFeatureMap, RealAmplitudes
    from qiskit.algorithms.optimizers import COBYLA, SPSA
    from qiskit_machine_learning.algorithms import VQC
    from qiskit_machine_learning.kernels import FidelityQuantumKernel
    QUANTUM_AVAILABLE = True
except ImportError:
    QUANTUM_AVAILABLE = False

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader, TensorDataset
    DEEP_LEARNING_AVAILABLE = True
except ImportError:
    DEEP_LEARNING_AVAILABLE = False

try:
    import ta  # Technical Analysis library
    TA_AVAILABLE = True
except ImportError:
    TA_AVAILABLE = False

# ============================================================================
# CONSTANTES E CONFIGURAÇÕES GLOBAIS
# ============================================================================

class RiskLevel(Enum):
    """Níveis de risco classificados"""
    CRITICAL = auto()
    HIGH = auto()
    MODERATE = auto()
    LOW = auto()
    MINIMAL = auto()
    
    @property
    def color(self) -> str:
        """Cores para visualização"""
        colors = {
            RiskLevel.CRITICAL: '#DC143C',  # Crimson
            RiskLevel.HIGH: '#FF8C00',      # Dark Orange
            RiskLevel.MODERATE: '#FFD700',  # Gold
            RiskLevel.LOW: '#90EE90',       # Light Green
            RiskLevel.MINIMAL: '#006400'    # Dark Green
        }
        return colors.get(self, '#808080')
    
    @property
    def threshold(self) -> float:
        """Limiares de risco"""
        thresholds = {
            RiskLevel.CRITICAL: 0.30,
            RiskLevel.HIGH: 0.20,
            RiskLevel.MODERATE: 0.10,
            RiskLevel.LOW: 0.05,
            RiskLevel.MINIMAL: 0.00
        }
        return thresholds.get(self, 0.0)


class AnalysisType(str, Enum):
    """Tipos de análise disponíveis com descrições"""
    STRESS_TEST = "stress_test"
    MONTE_CARLO = "monte_carlo"
    CORRELATION = "correlation"
    VOLATILITY = "volatility"
    SCENARIO = "scenario"
    BACKTESTING = "backtesting"
    SENSITIVITY = "sensitivity"
    CLUSTER = "cluster"
    FACTOR = "factor"
    EXTREME_VALUE = "extreme_value"
    
    @property
    def description(self) -> str:
        """Descrição do tipo de análise"""
        descriptions = {
            AnalysisType.STRESS_TEST: "Testes de estresse em cenários extremos",
            AnalysisType.MONTE_CARLO: "Simulações estocásticas de Monte Carlo",
            AnalysisType.CORRELATION: "Análise de correlação entre ativos",
            AnalysisType.VOLATILITY: "Previsão e análise de volatilidade",
            AnalysisType.SCENARIO: "Análise de cenários específicos",
            AnalysisType.BACKTESTING: "Validação histórica de estratégias",
            AnalysisType.SENSITIVITY: "Análise de sensibilidade paramétrica",
            AnalysisType.CLUSTER: "Agrupamento de riscos similares",
            AnalysisType.FACTOR: "Análise de fatores de risco",
            AnalysisType.EXTREME_VALUE: "Teoria de valores extremos"
        }
        return descriptions.get(self, "Análise de risco")


class RiskMetric(str, Enum):
    """Métricas de risco padronizadas"""
    VAR = "var"
    CVAR = "cvar"
    VOLATILITY = "volatility"
    BETA = "beta"
    SHARPE = "sharpe"
    SORTINO = "sortino"
    MAX_DRAWDOWN = "max_drawdown"
    CALMAR = "calmar"
    INFORMATION_RATIO = "information_ratio"
    TREYNOR = "treynor"
    
    @property
    def formula(self) -> str:
        """Fórmula da métrica"""
        formulas = {
            RiskMetric.VAR: "VaR(α) = -quantile(returns, 1-α)",
            RiskMetric.CVAR: "CVaR(α) = -E[returns | returns ≤ -VaR(α)]",
            RiskMetric.VOLATILITY: "σ = √(252 * var(returns))",
            RiskMetric.SHARPE: "Sharpe = (Rp - Rf) / σp"
        }
        return formulas.get(self, "Métrica personalizada")


# ============================================================================
# ESTRUTURAS DE DADOS AVANÇADAS
# ============================================================================

@dataclass
class StressTestScenario:
    """Cenário de stress test com metadados completos"""
    name: str
    description: str
    severity: float
    probability: float
    affected_sectors: List[str] = field(default_factory=list)
    affected_regions: List[str] = field(default_factory=list)
    time_horizon_days: int = 30
    recovery_scenario: Optional[Dict] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def validate(self) -> bool:
        """Valida consistência do cenário"""
        if not -1.0 <= self.severity <= 0:
            raise ValueError(f"Severidade deve estar entre -1 e 0: {self.severity}")
        if not 0 <= self.probability <= 1:
            raise ValueError(f"Probabilidade deve estar entre 0 e 1: {self.probability}")
        return True


@dataclass
class StressTestResult:
    """Resultado avançado de stress test"""
    scenario: StressTestScenario
    portfolio_impact: float
    var_impact: float
    cvar_impact: float
    positions_affected: List[Dict[str, Any]]
    recovery_time_days: int
    severity_level: RiskLevel
    confidence_interval: Tuple[float, float]
    simulation_paths: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Converte para dicionário serializável"""
        result = asdict(self)
        result['scenario'] = asdict(self.scenario)
        result['severity_level'] = self.severity_level.name
        if self.simulation_paths is not None:
            result['simulation_paths'] = self.simulation_paths.tolist()
        return result
    
    @property
    def is_critical(self) -> bool:
        """Verifica se o resultado é crítico"""
        return self.severity_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]


@dataclass
class CorrelationAnalysis:
    """Análise de correlação com métricas avançadas"""
    correlation_matrix: np.ndarray
    p_values: np.ndarray
    high_correlations: List[Dict[str, Any]]
    diversification_score: float
    concentration_risk: float
    eigen_values: np.ndarray
    condition_number: float
    partial_correlations: Optional[np.ndarray] = None
    
    def get_clusters(self, threshold: float = 0.5) -> List[List[int]]:
        """Agrupa ativos baseado em correlação"""
        from scipy.cluster.hierarchy import fcluster, linkage
        
        linkage_matrix = linkage(1 - abs(self.correlation_matrix), method='ward')
        clusters = fcluster(linkage_matrix, threshold, criterion='distance')
        
        cluster_groups = {}
        for i, cluster_id in enumerate(clusters):
            cluster_groups.setdefault(cluster_id, []).append(i)
        
        return list(cluster_groups.values())


@dataclass
class VolatilityForecast:
    """Previsão de volatilidade com múltiplos modelos"""
    symbol: str
    current_vol: float
    predicted_vol: float
    confidence_interval: Tuple[float, float]
    forecast_horizon: int
    model_name: str
    model_accuracy: float
    historical_vol: Optional[np.ndarray] = None
    forecast_path: Optional[np.ndarray] = None
    
    @property
    def volatility_change(self) -> float:
        """Mudança percentual na volatilidade"""
        return (self.predicted_vol - self.current_vol) / self.current_vol
    
    @property
    def risk_level(self) -> RiskLevel:
        """Nível de risco baseado na volatilidade"""
        annual_vol = self.predicted_vol * np.sqrt(252)
        if annual_vol > 0.4:
            return RiskLevel.CRITICAL
        elif annual_vol > 0.3:
            return RiskLevel.HIGH
        elif annual_vol > 0.2:
            return RiskLevel.MODERATE
        elif annual_vol > 0.1:
            return RiskLevel.LOW
        else:
            return RiskLevel.MINIMAL


@dataclass
class PortfolioOptimizationResult:
    """Resultado de otimização de portfólio"""
    weights: Dict[str, float]
    expected_return: float
    expected_volatility: float
    sharpe_ratio: float
    var_95: float
    cvar_95: float
    efficient_frontier: Dict[str, List[float]]
    optimization_time: float
    constraints_satisfied: bool


# ============================================================================
# DECORATORS E UTILITÁRIOS
# ============================================================================

def log_execution_time(func: Callable) -> Callable:
    """Decorator para log de tempo de execução"""
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start = datetime.now()
        result = await func(*args, **kwargs)
        elapsed = (datetime.now() - start).total_seconds()
        logger = args[0].logger if hasattr(args[0], 'logger') else logging.getLogger()
        logger.info(f"{func.__name__} executado em {elapsed:.3f}s")
        return result
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start = datetime.now()
        result = func(*args, **kwargs)
        elapsed = (datetime.now() - start).total_seconds()
        logger = args[0].logger if hasattr(args[0], 'logger') else logging.getLogger()
        logger.info(f"{func.__name__} executado em {elapsed:.3f}s")
        return result
    
    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper


def cache_result(ttl_seconds: int = 3600):
    """Cache de resultados com TTL"""
    def decorator(func: Callable) -> Callable:
        cache = {}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = hashlib.md5(
                f"{func.__name__}:{args}:{kwargs}".encode()
            ).hexdigest()
            
            if key in cache:
                result, timestamp = cache[key]
                if (datetime.now() - timestamp).total_seconds() < ttl_seconds:
                    return result
            
            result = func(*args, **kwargs)
            cache[key] = (result, datetime.now())
            return result
        
        return wrapper
    return decorator


class DataValidator:
    """Validador de dados de mercado"""
    
    @staticmethod
    def validate_price_data(df: pd.DataFrame) -> bool:
        """Valida dados de preço"""
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"DataFrame deve conter colunas: {required_columns}")
        
        if df.isnull().any().any():
            raise ValueError("Dados contêm valores nulos")
        
        if (df[['open', 'high', 'low', 'close']] <= 0).any().any():
            raise ValueError("Preços devem ser positivos")
        
        return True
    
    @staticmethod
    def validate_returns(returns: np.ndarray) -> bool:
        """Valida séries de retornos"""
        if len(returns) < 30:
            raise ValueError("Série de retornos muito curta (mínimo 30 observações)")
        
        if np.std(returns) == 0:
            raise ValueError("Série de retornos com variância zero")
        
        return True


# ============================================================================
# MODELOS DE PREVISÃO AVANÇADOS
# ============================================================================

class VolatilityModel:
    """Modelo avançado de previsão de volatilidade"""
    
    def __init__(self, model_type: str = 'garch'):
        self.model_type = model_type
        self.model = None
        self.scaler = RobustScaler()
        self.feature_importance = None
        
    def fit(self, returns: np.ndarray, features: Optional[pd.DataFrame] = None):
        """Treina modelo de volatilidade"""
        if self.model_type == 'garch':
            self._fit_garch(returns)
        elif self.model_type == 'ml':
            self._fit_ml(returns, features)
        elif self.model_type == 'ensemble':
            self._fit_ensemble(returns, features)
        else:
            raise ValueError(f"Modelo desconhecido: {self.model_type}")
    
    def _fit_garch(self, returns: np.ndarray):
        """Ajusta modelo GARCH"""
        try:
            from arch import arch_model
            
            # Otimização automática de parâmetros
            best_aic = np.inf
            best_order = None
            
            for p in [1, 2]:
                for q in [1, 2]:
                    try:
                        model = arch_model(returns * 100, vol='Garch', p=p, q=q)
                        result = model.fit(disp='off')
                        if result.aic < best_aic:
                            best_aic = result.aic
                            best_order = (p, q)
                            self.model = result
                    except:
                        continue
            
            if self.model is None:
                model = arch_model(returns * 100, vol='Garch', p=1, q=1)
                self.model = model.fit(disp='off')
                
        except ImportError:
            # Fallback para EWMA
            self.model = self._fit_ewma(returns)
    
    def _fit_ml(self, returns: np.ndarray, features: Optional[pd.DataFrame] = None):
        """Ajusta modelo baseado em ML"""
        # Cria features de volatilidade realizada
        realized_vol = pd.Series(returns).rolling(20).std().values[19:]
        
        if features is None:
            # Cria features automáticas
            features = pd.DataFrame({
                'return_lag1': returns[:-1],
                'return_lag2': np.roll(returns, 1)[:-1],
                'return_lag3': np.roll(returns, 2)[:-1],
                'vol_lag1': np.roll(realized_vol, 1),
                'vol_lag2': np.roll(realized_vol, 2),
                'abs_return': abs(returns[:-1]),
                'squared_return': returns[:-1] ** 2
            })
            features = features.iloc[2:]
            realized_vol = realized_vol[2:]
        
        # Normaliza features
        X_scaled = self.scaler.fit_transform(features)
        
        # Treina modelo
        self.model = RandomForestRegressor(
            n_estimators=200,
            max_depth=10,
            min_samples_split=5,
            random_state=42
        )
        self.model.fit(X_scaled, realized_vol)
        self.feature_importance = dict(zip(
            features.columns,
            self.model.feature_importances_
        ))
    
    def predict(self, horizon: int = 5) -> np.ndarray:
        """Prevê volatilidade futura"""
        if self.model_type == 'garch':
            forecast = self.model.forecast(horizon=horizon)
            return forecast.variance.values[-1] / 10000  # Converte de volta
        elif self.model_type in ['ml', 'ensemble']:
            # Implementar previsão recursiva
            return np.array([self.model.predict([self._get_last_features()])[0]] * horizon)
    
    def _get_last_features(self) -> np.ndarray:
        """Obtém últimas features para previsão"""
        # Implementar extração de features
        pass


class DeepRiskModel:
    """Modelo de risco baseado em deep learning"""
    
    def __init__(self, input_dim: int, hidden_dims: List[int] = [128, 64, 32]):
        if not DEEP_LEARNING_AVAILABLE:
            raise ImportError("PyTorch não disponível")
        
        self.input_dim = input_dim
        self.hidden_dims = hidden_dims
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = self._build_model().to(self.device)
        self.optimizer = None
        self.criterion = nn.MSELoss()
    
    def _build_model(self) -> nn.Module:
        """Constrói arquitetura da rede neural"""
        layers = []
        prev_dim = self.input_dim
        
        for hidden_dim in self.hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.BatchNorm1d(hidden_dim),
                nn.ReLU(),
                nn.Dropout(0.2)
            ])
            prev_dim = hidden_dim
        
        layers.append(nn.Linear(prev_dim, 1))
        
        return nn.Sequential(*layers)
    
    def fit(self, X: np.ndarray, y: np.ndarray, 
            epochs: int = 100, batch_size: int = 32):
        """Treina o modelo"""
        X_tensor = torch.FloatTensor(X).to(self.device)
        y_tensor = torch.FloatTensor(y).to(self.device)
        
        dataset = TensorDataset(X_tensor, y_tensor)
        loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer, patience=10, factor=0.5
        )
        
        self.model.train()
        for epoch in range(epochs):
            epoch_loss = 0.0
            for batch_X, batch_y in loader:
                self.optimizer.zero_grad()
                predictions = self.model(batch_X).squeeze()
                loss = self.criterion(predictions, batch_y)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                self.optimizer.step()
                epoch_loss += loss.item()
            
            scheduler.step(epoch_loss)
            
            if epoch % 10 == 0:
                print(f"Epoch {epoch}: Loss = {epoch_loss:.4f}")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Faz previsões"""
        self.model.eval()
        with torch.no_grad():
            X_tensor = torch.FloatTensor(X).to(self.device)
            predictions = self.model(X_tensor).cpu().numpy()
        return predictions.squeeze()


# ============================================================================
# SISTEMA PRINCIPAL DE ANALYTICS
# ============================================================================

class VHALINORRiskAnalytics:
    """
    Sistema Avançado de Analytics de Risco VHALINOR
    
    Características Principais:
    - Análise preditiva com múltiplos modelos
    - Stress testing avançado com cenários dinâmicos
    - Simulações Monte Carlo otimizadas
    - Integração com computação quântica
    - Deep learning para detecção de anomalias
    - Otimização de portfólio multi-objetivo
    - Visualizações interativas
    - API assíncrona de alta performance
    """
    
    def __init__(self, risk_manager=None, config: Optional[Dict] = None):
        """Inicializa o sistema de analytics"""
        self.risk_manager = risk_manager
        self.config = self._merge_config(config or {})
        
        # Estado do sistema
        self.market_data: Dict[str, pd.DataFrame] = {}
        self.analysis_cache: Dict[str, Any] = {}
        self.models: Dict[str, Any] = {}
        
        # Configuração de performance
        self.executor = ThreadPoolExecutor(max_workers=self.config['max_workers'])
        self.process_executor = ProcessPoolExecutor(max_workers=self.config['max_processes'])
        
        # Sistema de logging
        self.logger = self._setup_logging()
        
        # Inicializa componentes
        self._initialize_components()
        
        self.logger.info("[START] VHALINOR Risk Analytics v4.5.0 inicializado com sucesso")
    
    def _merge_config(self, user_config: Dict) -> Dict:
        """Mescla configurações do usuário com padrões"""
        default_config = {
            # Análises de risco
            'stress_test_scenarios': self._create_default_scenarios(),
            'monte_carlo_simulations': 50000,
            'correlation_threshold': 0.7,
            'volatility_window': 30,
            'confidence_levels': [0.95, 0.99, 0.995],
            'forecast_horizon': 5,
            
            # Machine Learning
            'enable_ml_models': True,
            'ml_models': ['garch', 'random_forest', 'gradient_boosting', 'deep'],
            'feature_engineering': True,
            'cross_validation_folds': 5,
            
            # Computação Quântica
            'enable_quantum': QUANTUM_AVAILABLE,
            'quantum_backend': 'qasm_simulator',
            'quantum_shots': 1024,
            'quantum_qubits': 4,
            
            # Deep Learning
            'enable_deep_learning': DEEP_LEARNING_AVAILABLE,
            'deep_learning_epochs': 100,
            'deep_learning_batch_size': 32,
            
            # Performance
            'max_workers': 8,
            'max_processes': 4,
            'cache_ttl': 300,  # segundos
            'enable_async': True,
            
            # Visualização
            'enable_plots': True,
            'plot_style': 'seaborn-v0_8-darkgrid',
            'figure_dpi': 120,
            'interactive_plots': True,
            
            # Logging
            'log_level': 'INFO',
            'log_file': 'vhalinor_analytics.log',
            'log_format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
        
        # Merge recursivo
        merged = default_config.copy()
        for key, value in user_config.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key].update(value)
            else:
                merged[key] = value
        
        return merged
    
    def _create_default_scenarios(self) -> Dict[str, StressTestScenario]:
        """Cria cenários de stress test padrão"""
        return {
            'market_crash': StressTestScenario(
                name='Market Crash',
                description='Queda generalizada do mercado (20%)',
                severity=-0.20,
                probability=0.05,
                affected_sectors=['all'],
                affected_regions=['global'],
                time_horizon_days=30
            ),
            'flash_crash': StressTestScenario(
                name='Flash Crash',
                description='Queda rápida seguida de recuperação',
                severity=-0.10,
                probability=0.10,
                affected_sectors=['all'],
                affected_regions=['global'],
                time_horizon_days=5
            ),
            'high_volatility': StressTestScenario(
                name='Alta Volatilidade',
                description='Período de volatilidade elevada',
                severity=-0.05,
                probability=0.20,
                affected_sectors=['all'],
                affected_regions=['global'],
                time_horizon_days=60
            ),
            'currency_crisis': StressTestScenario(
                name='Crise Cambial',
                description='Desvalorização cambial acentuada',
                severity=-0.15,
                probability=0.08,
                affected_sectors=['finance', 'imports'],
                affected_regions=['emerging'],
                time_horizon_days=90
            ),
            'black_swan': StressTestScenario(
                name='Cisne Negro',
                description='Evento extremo de baixa probabilidade',
                severity=-0.30,
                probability=0.01,
                affected_sectors=['all'],
                affected_regions=['global'],
                time_horizon_days=180
            ),
            'interest_rate_shock': StressTestScenario(
                name='Choque de Juros',
                description='Aumento abrupto das taxas de juros',
                severity=-0.12,
                probability=0.06,
                affected_sectors=['finance', 'real_estate'],
                affected_regions=['developed'],
                time_horizon_days=60
            ),
            'liquidity_crisis': StressTestScenario(
                name='Crise de Liquidez',
                description='Redução drástica da liquidez',
                severity=-0.18,
                probability=0.04,
                affected_sectors=['all'],
                affected_regions=['global'],
                time_horizon_days=45
            )
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Configura sistema de logging avançado"""
        logger = logging.getLogger('VHALINOR_Analytics')
        logger.setLevel(getattr(logging, self.config['log_level']))
        
        if not logger.handlers:
            # Handler para arquivo
            file_handler = logging.FileHandler(self.config['log_file'])
            file_handler.setFormatter(logging.Formatter(self.config['log_format']))
            logger.addHandler(file_handler)
            
            # Handler para console
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
            logger.addHandler(console_handler)
        
        return logger
    
    def _initialize_components(self):
        """Inicializa componentes do sistema"""
        # Inicializa modelos de ML
        if self.config['enable_ml_models']:
            self.models['volatility'] = {}
            for model_type in self.config['ml_models']:
                try:
                    if model_type == 'deep' and DEEP_LEARNING_AVAILABLE:
                        self.models['volatility'][model_type] = DeepRiskModel(input_dim=20)
                    else:
                        self.models['volatility'][model_type] = VolatilityModel(model_type)
                except Exception as e:
                    self.logger.warning(f"Falha ao carregar modelo {model_type}: {e}")
        
        # Inicializa backend quântico
        if self.config['enable_quantum'] and QUANTUM_AVAILABLE:
            try:
                self.quantum_backend = Aer.get_backend(self.config['quantum_backend'])
                self.logger.info("[OK] Backend quântico inicializado")
            except Exception as e:
                self.logger.warning(f"[ERROR] Falha ao inicializar backend quântico: {e}")
                self.config['enable_quantum'] = False
        
        # Configura estilo de plots
        if self.config['enable_plots']:
            plt.style.use(self.config['plot_style'])
            sns.set_palette("husl")
    
    # ========================================================================
    # ANÁLISE DE STRESS TEST
    # ========================================================================
    
    @log_execution_time
    async def run_stress_test(
        self,
        portfolio: Dict[str, float],
        scenarios: Optional[List[str]] = None,
        confidence_level: float = 0.95
    ) -> List[StressTestResult]:
        """
        Executa stress testing avançado no portfólio
        
        Args:
            portfolio: Dicionário com ativos e pesos
            scenarios: Lista de cenários a testar (None = todos)
            confidence_level: Nível de confiança para VaR/CVaR
            
        Returns:
            Lista de resultados de stress test
        """
        self.logger.info(f"[STRESS_TEST] Iniciando stress test - {len(portfolio)} ativos")
        
        results = []
        scenarios_to_test = self._get_scenarios(scenarios)
        
        # Prepara dados do portfólio
        portfolio_returns = await self._get_portfolio_returns(portfolio)
        current_var = self._calculate_var(portfolio_returns, confidence_level)
        current_cvar = self._calculate_cvar(portfolio_returns, confidence_level)
        
        for scenario in scenarios_to_test:
            try:
                # Simula impacto do cenário
                impacted_returns = portfolio_returns * (1 + scenario.severity)
                
                # Calcula métricas pós-stress
                stressed_var = self._calculate_var(impacted_returns, confidence_level)
                stressed_cvar = self._calculate_cvar(impacted_returns, confidence_level)
                
                # Simula Monte Carlo para o cenário
                mc_simulations = await self._run_monte_carlo_simulation(
                    portfolio,
                    n_simulations=self.config['monte_carlo_simulations'],
                    scenario_shock=scenario.severity
                )
                
                # Identifica posições mais afetadas
                affected_positions = self._identify_affected_positions(
                    portfolio, scenario
                )
                
                # Calcula tempo estimado de recuperação
                recovery_time = await self._estimate_recovery_time(
                    impacted_returns, scenario
                )
                
                # Determina nível de severidade
                severity_level = self._determine_severity_level(
                    scenario.severity,
                    stressed_var / current_var - 1 if current_var != 0 else 1
                )
                
                # Cria resultado
                result = StressTestResult(
                    scenario=scenario,
                    portfolio_impact=scenario.severity,
                    var_impact=(stressed_var - current_var) / current_var if current_var != 0 else 1,
                    cvar_impact=(stressed_cvar - current_cvar) / current_cvar if current_cvar != 0 else 1,
                    positions_affected=affected_positions,
                    recovery_time_days=recovery_time,
                    severity_level=severity_level,
                    confidence_interval=self._calculate_confidence_interval(
                        mc_simulations['portfolio_values'][:, -1]
                    ),
                    simulation_paths=mc_simulations['portfolio_values'][:100],  # Amostra
                    metadata={
                        'n_simulations': self.config['monte_carlo_simulations'],
                        'confidence_level': confidence_level,
                        'timestamp': datetime.now().isoformat()
                    }
                )
                
                results.append(result)
                
                self.logger.info(f"[OK] Stress test '{scenario.name}' concluído - "
                               f"Impacto: {scenario.severity:.1%}, "
                               f"VaR Impacto: {result.var_impact:.1%}")
                
            except np.linalg.LinAlgError as e:
                self.logger.error(f"[ERROR] Erro de álgebra linear no cenário {scenario.name}: {e}")
            except Exception as e:
                self.logger.error(f"[ERROR] Erro no cenário {scenario.name}: {e}")
        
        return results
    
    # ========================================================================
    # SIMULAÇÕES MONTE CARLO
    # ========================================================================
    
    @cache_result(ttl_seconds=300)
    @log_execution_time
    async def _run_monte_carlo_simulation(
        self,
        portfolio: Dict[str, float],
        n_simulations: int = 10000,
        horizon_days: int = 252,
        scenario_shock: float = 0.0,
        use_gpu: bool = True
    ) -> Dict[str, Any]:
        """
        Executa simulações Monte Carlo otimizadas
        
        Args:
            portfolio: Dicionário com ativos e pesos
            n_simulations: Número de simulações
            horizon_days: Horizonte de simulação em dias
            scenario_shock: Choque adicional no cenário
            use_gpu: Utilizar GPU se disponível
            
        Returns:
            Dicionário com resultados das simulações
        """
        # Obtém retornos históricos
        returns_data = await self._get_historical_returns(list(portfolio.keys()))
        
        # Calcula matriz de covariância
        cov_matrix = returns_data.cov() * 252
        mean_returns = returns_data.mean() * 252 + scenario_shock
        
        # Regulariza matriz de covariância para evitar problemas numéricos
        try:
            # Adiciona pequena diagonal para garantir positividade definida
            epsilon = 1e-8
            cov_matrix = cov_matrix + epsilon * np.eye(len(cov_matrix))
            
            # Verifica se a matriz é numericamente estável
            eigenvalues = np.linalg.eigvals(cov_matrix)
            if np.any(eigenvalues <= 0):
                # Força positividade definida
                cov_matrix = cov_matrix + abs(np.min(eigenvalues)) * np.eye(len(cov_matrix)) + epsilon
        except Exception as e:
            self.logger.warning(f"Problema na matriz de covariância: {e}")
            # Usa matriz diagonal como fallback
            cov_matrix = np.diag(np.diag(cov_matrix))
        
        # Otimiza para uso de GPU se disponível
        if use_gpu and DEEP_LEARNING_AVAILABLE and torch.cuda.is_available():
            return self._run_monte_carlo_gpu(
                mean_returns, cov_matrix, n_simulations, horizon_days, portfolio
            )
        
        # Simulação tradicional
        n_assets = len(portfolio)
        weights = np.array([portfolio[symbol] for symbol in returns_data.columns])
        
        # Gera retornos aleatórios (distribuição normal multivariada)
        try:
            random_returns = np.random.multivariate_normal(
                mean_returns.values,
                cov_matrix.values,
                (horizon_days, n_simulations)
            )
        except np.linalg.LinAlgError as e:
            self.logger.warning(f"SVD não convergiu, usando aproximação diagonal: {e}")
            # Fallback para aproximação diagonal (independente)
            random_returns = np.zeros((horizon_days, n_simulations, len(mean_returns)))
            for i, (mean, vol) in enumerate(zip(mean_returns.values, np.sqrt(np.diag(cov_matrix)))):
                random_returns[:, :, i] = np.random.normal(mean, vol, (horizon_days, n_simulations))
        
        # Calcula retornos do portfólio
        portfolio_returns = np.dot(random_returns, weights)
        
        # Calcula valores do portfólio
        initial_value = 1000000  # Valor inicial arbitrário
        cumulative_returns = np.cumprod(1 + portfolio_returns, axis=0)
        portfolio_values = initial_value * cumulative_returns
        
        # Calcula métricas
        final_values = portfolio_values[-1, :]
        worst_case = np.percentile(final_values, 5)
        best_case = np.percentile(final_values, 95)
        median_case = np.median(final_values)
        
        return {
            'portfolio_values': portfolio_values,
            'final_values': final_values,
            'worst_case': worst_case,
            'best_case': best_case,
            'median_case': median_case,
            'var_95': initial_value - np.percentile(final_values, 5),
            'cvar_95': initial_value - final_values[final_values <= np.percentile(final_values, 5)].mean()
        }
    
    def _run_monte_carlo_gpu(
        self,
        mean_returns: pd.Series,
        cov_matrix: pd.DataFrame,
        n_simulations: int,
        horizon_days: int,
        portfolio: Dict[str, float]
    ) -> Dict[str, Any]:
        """Versão GPU das simulações Monte Carlo"""
        try:
            import cupy as cp
            
            # Move dados para GPU
            mean_gpu = cp.array(mean_returns.values)
            cov_gpu = cp.array(cov_matrix.values)
            weights = cp.array([portfolio[symbol] for symbol in mean_returns.index])
            
            # Gera números aleatórios na GPU
            random_normal = cp.random.normal(
                size=(horizon_days, n_simulations, len(mean_returns))
            )
            
            # Decomposição de Cholesky
            L = cp.linalg.cholesky(cov_gpu)
            
            # Gera retornos correlacionados
            correlated_returns = cp.einsum('ij,klj->kli', L, random_normal)
            correlated_returns += mean_gpu[cp.newaxis, cp.newaxis, :]
            
            # Calcula retornos do portfólio
            portfolio_returns = cp.dot(correlated_returns, weights)
            
            # Calcula valores
            initial_value = 1000000
            cumulative_returns = cp.cumprod(1 + portfolio_returns, axis=0)
            portfolio_values = initial_value * cumulative_returns
            
            # Move resultados de volta para CPU
            final_values_cpu = cp.asnumpy(portfolio_values[-1, :])
            
            return {
                'portfolio_values': cp.asnumpy(portfolio_values),
                'final_values': final_values_cpu,
                'worst_case': np.percentile(final_values_cpu, 5),
                'best_case': np.percentile(final_values_cpu, 95),
                'median_case': np.median(final_values_cpu),
                'var_95': initial_value - np.percentile(final_values_cpu, 5),
                'cvar_95': initial_value - final_values_cpu[
                    final_values_cpu <= np.percentile(final_values_cpu, 5)
                ].mean()
            }
            
        except ImportError:
            self.logger.warning("CuPy não disponível, usando CPU")
            return self._run_monte_carlo_cpu(
                mean_returns, cov_matrix, n_simulations, horizon_days, portfolio
            )
    
    # ========================================================================
    # ANÁLISE DE CORRELAÇÃO
    # ========================================================================
    
    @log_execution_time
    async def analyze_correlations(
        self,
        symbols: List[str],
        window_days: int = 252,
        method: str = 'pearson'
    ) -> CorrelationAnalysis:
        """
        Análise avançada de correlação entre ativos
        
        Args:
            symbols: Lista de símbolos
            window_days: Janela histórica em dias
            method: Método de correlação ('pearson', 'spearman', 'kendall')
            
        Returns:
            Análise completa de correlação
        """
        # Obtém retornos
        returns = await self._get_historical_returns(symbols, window_days)
        
        # Calcula matriz de correlação
        if method == 'pearson':
            corr_matrix = returns.corr().values
            p_values = self._calculate_p_values(returns)
        elif method == 'spearman':
            corr_matrix = returns.corr(method='spearman').values
            p_values = np.zeros_like(corr_matrix)
        else:
            corr_matrix = returns.corr(method='kendall').values
            p_values = np.zeros_like(corr_matrix)
        
        # Identifica correlações altas
        high_correlations = []
        threshold = self.config['correlation_threshold']
        
        for i in range(len(symbols)):
            for j in range(i + 1, len(symbols)):
                if abs(corr_matrix[i, j]) > threshold:
                    high_correlations.append({
                        'symbol_1': symbols[i],
                        'symbol_2': symbols[j],
                        'correlation': corr_matrix[i, j],
                        'p_value': p_values[i, j],
                        'significance': 'high' if p_values[i, j] < 0.05 else 'moderate'
                    })
        
        # Calcula score de diversificação
        diversification_score = 1 - np.mean(abs(corr_matrix[np.triu_indices_from(corr_matrix, k=1)]))
        
        # Calcula risco de concentração
        eigenvalues = np.linalg.eigvals(corr_matrix)
        concentration_risk = np.sum(eigenvalues ** 2) / len(eigenvalues) - 1
        
        # Número de condição
        condition_number = np.max(eigenvalues) / np.min(eigenvalues[eigenvalues > 1e-10])
        
        # Correlações parciais (opcional)
        partial_correlations = None
        if len(symbols) > 2:
            try:
                precision = np.linalg.pinv(corr_matrix)
                partial_correlations = -precision / np.sqrt(
                    np.outer(np.diag(precision), np.diag(precision))
                )
                np.fill_diagonal(partial_correlations, 1)
            except:
                pass
        
        return CorrelationAnalysis(
            correlation_matrix=corr_matrix,
            p_values=p_values,
            high_correlations=high_correlations,
            diversification_score=diversification_score,
            concentration_risk=concentration_risk,
            eigen_values=eigenvalues,
            condition_number=condition_number,
            partial_correlations=partial_correlations
        )
    
    # ========================================================================
    # PREVISÃO DE VOLATILIDADE
    # ========================================================================
    
    @log_execution_time
    async def forecast_volatility(
        self,
        symbol: str,
        horizon_days: int = 5,
        model_type: str = 'ensemble'
    ) -> VolatilityForecast:
        """
        Prevê volatilidade usando múltiplos modelos
        
        Args:
            symbol: Símbolo do ativo
            horizon_days: Horizonte de previsão
            model_type: Tipo de modelo ('garch', 'ml', 'ensemble')
            
        Returns:
            Previsão de volatilidade
        """
        # Obtém dados históricos
        data = await self._get_market_data(symbol)
        returns = data['close'].pct_change().dropna()
        
        # Calcula volatilidade atual (anualizada)
        current_vol = returns.tail(30).std() * np.sqrt(252)
        
        # Seleciona modelo
        if model_type in self.models['volatility']:
            model = self.models['volatility'][model_type]
        else:
            model = VolatilityModel(model_type)
            model.fit(returns.values)
            self.models['volatility'][model_type] = model
        
        # Faz previsão
        predicted_vol = model.predict(horizon_days)[-1] * np.sqrt(252)
        
        # Calcula intervalo de confiança
        ci_lower = predicted_vol * 0.7
        ci_upper = predicted_vol * 1.3
        
        # Calcula acurácia do modelo
        model_accuracy = self._calculate_model_accuracy(model, returns)
        
        return VolatilityForecast(
            symbol=symbol,
            current_vol=current_vol,
            predicted_vol=predicted_vol,
            confidence_interval=(ci_lower, ci_upper),
            forecast_horizon=horizon_days,
            model_name=model_type,
            model_accuracy=model_accuracy,
            historical_vol=returns.rolling(30).std().values * np.sqrt(252)
        )
    
    # ========================================================================
    # OTIMIZAÇÃO DE PORTFÓLIO
    # ========================================================================
    
    @log_execution_time
    async def optimize_portfolio(
        self,
        symbols: List[str],
        objective: str = 'sharpe',
        constraints: Optional[Dict] = None
    ) -> PortfolioOptimizationResult:
        """
        Otimização avançada de portfólio
        
        Args:
            symbols: Lista de símbolos
            objective: Objetivo ('sharpe', 'min_vol', 'max_return', 'min_cvar')
            constraints: Restrições de alocação
            
        Returns:
            Resultado da otimização
        """
        start_time = datetime.now()
        
        # Obtém dados
        returns = await self._get_historical_returns(symbols)
        mean_returns = returns.mean() * 252
        cov_matrix = returns.cov() * 252
        
        n_assets = len(symbols)
        
        # Define restrições padrão
        if constraints is None:
            constraints = {
                'min_weight': 0.0,
                'max_weight': 0.3,
                'target_return': None,
                'sum_to_one': True
            }
        
        # Função objetivo
        def objective_function(weights):
            portfolio_return = np.sum(mean_returns * weights)
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            
            if objective == 'sharpe':
                return -portfolio_return / portfolio_vol  # Minimizar negativo Sharpe
            elif objective == 'min_vol':
                return portfolio_vol
            elif objective == 'max_return':
                return -portfolio_return
            elif objective == 'min_cvar':
                # Implementar minimização de CVaR
                return portfolio_vol
            else:
                return portfolio_vol
        
        # Restrições
        constraints_list = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}  # Soma = 1
        ]
        
        if constraints.get('target_return'):
            constraints_list.append({
                'type': 'eq',
                'fun': lambda x: np.sum(mean_returns * x) - constraints['target_return']
            })
        
        # Limites
        bounds = tuple(
            (constraints.get('min_weight', 0), 
             constraints.get('max_weight', 1))
            for _ in range(n_assets)
        )
        
        # Otimização
        initial_weights = np.array([1/n_assets] * n_assets)
        
        result = optimize.minimize(
            objective_function,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints_list,
            options={'maxiter': 1000, 'ftol': 1e-9}
        )
        
        # Calcula fronteira eficiente
        efficient_frontier = await self._calculate_efficient_frontier(
            mean_returns, cov_matrix, n_assets
        )
        
        # Pesos otimizados
        weights_dict = dict(zip(symbols, result.x))
        
        # Métricas do portfólio otimizado
        portfolio_return = np.sum(mean_returns * result.x)
        portfolio_vol = np.sqrt(np.dot(result.x.T, np.dot(cov_matrix, result.x)))
        sharpe_ratio = portfolio_return / portfolio_vol
        
        # VaR e CVaR
        portfolio_returns = returns.dot(result.x)
        var_95 = self._calculate_var(portfolio_returns, 0.95)
        cvar_95 = self._calculate_cvar(portfolio_returns, 0.95)
        
        optimization_time = (datetime.now() - start_time).total_seconds()
        
        return PortfolioOptimizationResult(
            weights=weights_dict,
            expected_return=portfolio_return,
            expected_volatility=portfolio_vol,
            sharpe_ratio=sharpe_ratio,
            var_95=var_95,
            cvar_95=cvar_95,
            efficient_frontier=efficient_frontier,
            optimization_time=optimization_time,
            constraints_satisfied=result.success
        )
    
    # ========================================================================
    # ANÁLISE QUÂNTICA
    # ========================================================================
    
    async def quantum_risk_analysis(
        self,
        portfolio: Dict[str, float],
        n_qubits: int = 4
    ) -> Dict[str, Any]:
        """
        Análise de risco usando computação quântica
        
        Args:
            portfolio: Dicionário com ativos e pesos
            n_qubits: Número de qubits para simulação
            
        Returns:
            Resultados da análise quântica
        """
        if not self.config['enable_quantum'] or not QUANTUM_AVAILABLE:
            return {'error': 'Módulo quântico não disponível'}
        
        try:
            # Prepara dados
            symbols = list(portfolio.keys())
            weights = np.array([portfolio[s] for s in symbols])
            returns = await self._get_historical_returns(symbols)
            
            # Normaliza dados para qubits
            normalized_returns = (returns + 1) / 2  # Mapeia [-1, 1] para [0, 1]
            
            # Cria feature map quântico
            feature_dim = min(n_qubits, len(symbols))
            feature_map = ZZFeatureMap(feature_dimension=feature_dim, reps=2)
            
            # Cria circuito variacional
            var_form = RealAmplitudes(feature_dim, reps=3)
            
            # Classificador quântico para detecção de risco
            vqc = VQC(
                feature_map=feature_map,
                var_form=var_form,
                optimizer=COBYLA(maxiter=100),
                quantum_instance=self.quantum_backend
            )
            
            # Prepara dados de treinamento
            X = normalized_returns.values[:100, :feature_dim]
            y = np.where(returns.values[:100, 0] < 0, 0, 1)  # Labels binários
            
            # Treina modelo quântico
            vqc.fit(X, y)
            
            # Faz previsões
            X_test = normalized_returns.values[100:120, :feature_dim]
            predictions = vqc.predict(X_test)
            
            return {
                'quantum_model_accuracy': vqc.score(X_test, y[100:120]),
                'quantum_predictions': predictions.tolist(),
                'n_qubits_used': n_qubits,
                'circuit_depth': feature_map.depth() + var_form.depth(),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Erro na análise quântica: {e}")
            return {'error': str(e)}
    
    # ========================================================================
    # VISUALIZAÇÕES
    # ========================================================================
    
    def plot_correlation_matrix(
        self,
        correlation_analysis: CorrelationAnalysis,
        symbols: List[str],
        title: str = "Matriz de Correlação",
        interactive: bool = True
    ) -> Union[Figure, go.Figure]:
        """
        Visualiza matriz de correlação
        
        Args:
            correlation_analysis: Análise de correlação
            symbols: Lista de símbolos
            title: Título do gráfico
            interactive: Usar plotly (True) ou matplotlib (False)
            
        Returns:
            Figura do matplotlib ou plotly
        """
        if interactive and self.config['interactive_plots']:
            fig = go.Figure(data=go.Heatmap(
                z=correlation_analysis.correlation_matrix,
                x=symbols,
                y=symbols,
                colorscale='RdBu_r',
                zmid=0,
                text=np.round(correlation_analysis.correlation_matrix, 2),
                texttemplate='%{text}',
                textfont={"size": 10},
                hoverongaps=False
            ))
            
            fig.update_layout(
                title=title,
                width=800,
                height=800,
                xaxis_title="Ativos",
                yaxis_title="Ativos"
            )
            
            return fig
        
        else:
            fig, ax = plt.subplots(figsize=(12, 10))
            sns.heatmap(
                correlation_analysis.correlation_matrix,
                xticklabels=symbols,
                yticklabels=symbols,
                annot=True,
                fmt='.2f',
                cmap='RdBu_r',
                center=0,
                vmin=-1,
                vmax=1,
                ax=ax
            )
            ax.set_title(title, fontsize=16, pad=20)
            plt.tight_layout()
            return fig
    
    def plot_stress_test_results(
        self,
        results: List[StressTestResult],
        title: str = "Resultados de Stress Testing"
    ) -> go.Figure:
        """
        Visualiza resultados de stress test com gráfico interativo
        """
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                "Impacto no Portfólio",
                "Impacto no VaR",
                "Probabilidade vs Severidade",
                "Tempo de Recuperação"
            ),
            specs=[
                [{"type": "bar"}, {"type": "bar"}],
                [{"type": "scatter"}, {"type": "bar"}]
            ]
        )
        
        # Gráfico 1: Impacto no portfólio
        fig.add_trace(
            go.Bar(
                x=[r.scenario.name for r in results],
                y=[r.portfolio_impact * 100 for r in results],
                name="Impacto Portfólio",
                marker_color=['red' if r.is_critical else 'orange' for r in results],
                text=[f"{r.portfolio_impact:.1%}" for r in results],
                textposition='outside'
            ),
            row=1, col=1
        )
        
        # Gráfico 2: Impacto no VaR
        fig.add_trace(
            go.Bar(
                x=[r.scenario.name for r in results],
                y=[r.var_impact * 100 for r in results],
                name="Impacto VaR",
                marker_color='blue',
                text=[f"{r.var_impact:.1%}" for r in results],
                textposition='outside'
            ),
            row=1, col=2
        )
        
        # Gráfico 3: Probabilidade vs Severidade
        fig.add_trace(
            go.Scatter(
                x=[r.scenario.probability * 100 for r in results],
                y=[abs(r.scenario.severity) * 100 for r in results],
                mode='markers+text',
                text=[r.scenario.name for r in results],
                textposition="top center",
                marker=dict(
                    size=[r.recovery_time_days / 5 for r in results],
                    color=[r.severity_level.value for r in results],
                    colorscale='Viridis',
                    showscale=True
                ),
                name="Cenários"
            ),
            row=2, col=1
        )
        
        # Gráfico 4: Tempo de recuperação
        fig.add_trace(
            go.Bar(
                x=[r.scenario.name for r in results],
                y=[r.recovery_time_days for r in results],
                name="Dias para Recuperação",
                marker_color='green',
                text=[f"{r.recovery_time_days}d" for r in results],
                textposition='outside'
            ),
            row=2, col=2
        )
        
        # Atualiza layout
        fig.update_layout(
            title=title,
            height=800,
            showlegend=False,
            template='plotly_white'
        )
        
        fig.update_xaxes(tickangle=45)
        fig.update_yaxes(title_text="Impacto (%)", row=1, col=1)
        fig.update_yaxes(title_text="Impacto VaR (%)", row=1, col=2)
        fig.update_yaxes(title_text="Probabilidade (%)", row=2, col=1)
        fig.update_xaxes(title_text="Cenário", row=2, col=1)
        fig.update_yaxes(title_text="Dias", row=2, col=2)
        
        return fig
    
    # ========================================================================
    # MÉTODOS UTILITÁRIOS
    # ========================================================================
    
    async def _get_historical_returns(
        self,
        symbols: List[str],
        days: int = 252
    ) -> pd.DataFrame:
        """Obtém retornos históricos"""
        returns_dict = {}
        
        for symbol in symbols:
            data = await self._get_market_data(symbol)
            if data is not None:
                returns = data['close'].pct_change().dropna()
                returns_dict[symbol] = returns.tail(days)
        
        return pd.DataFrame(returns_dict)
    
    async def _get_market_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """Obtém dados de mercado com cache"""
        if symbol in self.market_data:
            return self.market_data[symbol]
        
        # Simula dados para demonstração
        dates = pd.date_range(end=datetime.now(), periods=500, freq='D')
        np.random.seed(hash(symbol) % 2**32)
        
        # Gera preços com random walk
        returns = np.random.normal(0.0005, 0.02, 500)
        prices = 100 * np.exp(np.cumsum(returns))
        
        data = pd.DataFrame({
            'open': prices * np.random.uniform(0.99, 1.01, 500),
            'high': prices * np.random.uniform(1.01, 1.03, 500),
            'low': prices * np.random.uniform(0.97, 0.99, 500),
            'close': prices,
            'volume': np.random.randint(100000, 1000000, 500)
        }, index=dates)
        
        self.market_data[symbol] = data
        return data
    
    async def _get_portfolio_returns(
        self,
        portfolio: Dict[str, float]
    ) -> np.ndarray:
        """Calcula retornos do portfólio"""
        returns_data = await self._get_historical_returns(list(portfolio.keys()))
        weights = np.array([portfolio[symbol] for symbol in returns_data.columns])
        portfolio_returns = returns_data.dot(weights)
        return portfolio_returns.values
    
    def _calculate_var(
        self,
        returns: np.ndarray,
        confidence_level: float = 0.95
    ) -> float:
        """Calcula Value at Risk"""
        return np.percentile(returns, (1 - confidence_level) * 100)
    
    def _calculate_cvar(
        self,
        returns: np.ndarray,
        confidence_level: float = 0.95
    ) -> float:
        """Calcula Conditional Value at Risk"""
        var = self._calculate_var(returns, confidence_level)
        return returns[returns <= var].mean()
    
    def _calculate_p_values(self, returns: pd.DataFrame) -> np.ndarray:
        """Calcula p-valores para correlações"""
        n = len(returns.columns)
        p_values = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    corr, p_value = stats.pearsonr(
                        returns.iloc[:, i],
                        returns.iloc[:, j]
                    )
                    p_values[i, j] = p_value
        
        return p_values
    
    def _get_scenarios(
        self,
        scenario_names: Optional[List[str]]
    ) -> List[StressTestScenario]:
        """Obtém cenários de stress test"""
        if scenario_names is None:
            return list(self.config['stress_test_scenarios'].values())
        
        scenarios = []
        for name in scenario_names:
            if name in self.config['stress_test_scenarios']:
                scenarios.append(self.config['stress_test_scenarios'][name])
        
        return scenarios
    
    def _identify_affected_positions(
        self,
        portfolio: Dict[str, float],
        scenario: StressTestScenario
    ) -> List[Dict[str, Any]]:
        """Identifica posições mais afetadas pelo cenário"""
        affected = []
        
        for symbol, weight in portfolio.items():
            # Calcula fator de impacto baseado no setor
            impact_factor = 1.0
            
            if 'all' in scenario.affected_sectors:
                impact_factor = 1.0
            elif any(sector in symbol.lower() for sector in scenario.affected_sectors):
                impact_factor = 1.5
            
            impact = abs(scenario.severity) * weight * impact_factor
            
            if impact > 0.01:  # Impacto > 1%
                affected.append({
                    'symbol': symbol,
                    'weight': weight,
                    'impact': impact,
                    'severity': 'Alto' if impact > 0.05 else 'Médio'
                })
        
        return sorted(affected, key=lambda x: x['impact'], reverse=True)
    
    async def _estimate_recovery_time(
        self,
        returns: np.ndarray,
        scenario: StressTestScenario
    ) -> int:
        """Estima tempo de recuperação em dias"""
        # Simula processo de recuperação
        volatility = np.std(returns)
        drift = np.mean(returns)
        
        # Tempo para recuperar baseado na severidade
        recovery_time = int(abs(scenario.severity) / max(drift, 0.001))
        
        return min(recovery_time, scenario.time_horizon_days * 2)
    
    def _determine_severity_level(
        self,
        severity: float,
        var_impact: float
    ) -> RiskLevel:
        """Determina nível de severidade"""
        combined_score = abs(severity) * 0.6 + abs(var_impact) * 0.4
        
        if combined_score > 0.25:
            return RiskLevel.CRITICAL
        elif combined_score > 0.15:
            return RiskLevel.HIGH
        elif combined_score > 0.10:
            return RiskLevel.MODERATE
        elif combined_score > 0.05:
            return RiskLevel.LOW
        else:
            return RiskLevel.MINIMAL
    
    def _calculate_confidence_interval(
        self,
        data: np.ndarray,
        confidence: float = 0.95
    ) -> Tuple[float, float]:
        """Calcula intervalo de confiança"""
        mean = np.mean(data)
        sem = stats.sem(data)
        margin = sem * stats.t.ppf((1 + confidence) / 2., len(data) - 1)
        return (mean - margin, mean + margin)
    
    def _calculate_model_accuracy(
        self,
        model: Any,
        returns: pd.Series
    ) -> float:
        """Calcula acurácia do modelo de volatilidade"""
        try:
            # Validação simples
            train_size = int(len(returns) * 0.8)
            train_returns = returns[:train_size]
            test_returns = returns[train_size:]
            
            # Re-treina modelo com dados de treino
            if hasattr(model, 'fit'):
                model.fit(train_returns.values)
            
            # Faz previsões
            predictions = model.predict(len(test_returns))
            
            # Calcula RMSE normalizado
            actual_vol = test_returns.rolling(20).std().values[19:]
            predicted_vol = predictions[:len(actual_vol)] * np.sqrt(252)
            
            if len(actual_vol) > 0 and len(predicted_vol) > 0:
                rmse = np.sqrt(mean_squared_error(actual_vol, predicted_vol))
                return 1 / (1 + rmse)  # Normaliza para [0, 1]
            
        except Exception as e:
            self.logger.debug(f"Erro ao calcular acurácia: {e}")
        
        return 0.7  # Valor padrão
    
    async def _calculate_efficient_frontier(
        self,
        mean_returns: pd.Series,
        cov_matrix: pd.DataFrame,
        n_assets: int,
        n_portfolios: int = 50
    ) -> Dict[str, List[float]]:
        """Calcula fronteira eficiente de Markowitz"""
        returns_list = []
        volatility_list = []
        sharpe_list = []
        
        for _ in range(n_portfolios):
            weights = np.random.random(n_assets)
            weights = weights / np.sum(weights)
            
            portfolio_return = np.sum(mean_returns * weights)
            portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            sharpe_ratio = portfolio_return / portfolio_vol if portfolio_vol > 0 else 0
            
            returns_list.append(portfolio_return)
            volatility_list.append(portfolio_vol)
            sharpe_list.append(sharpe_ratio)
        
        return {
            'returns': returns_list,
            'volatility': volatility_list,
            'sharpe_ratios': sharpe_list
        }
    
    # ========================================================================
    # API PÚBLICA
    # ========================================================================
    
    async def analyze_portfolio_risk(
        self,
        portfolio: Dict[str, float],
        analysis_types: Optional[List[AnalysisType]] = None
    ) -> Dict[str, Any]:
        """
        Análise completa de risco do portfólio
        
        Args:
            portfolio: Dicionário com ativos e pesos
            analysis_types: Tipos de análise a executar
            
        Returns:
            Relatório completo de análise de risco
        """
        if analysis_types is None:
            analysis_types = list(AnalysisType)
        
        results = {}
        
        # Executa análises em paralelo
        tasks = []
        
        if AnalysisType.STRESS_TEST in analysis_types:
            tasks.append(self.run_stress_test(portfolio))
        
        if AnalysisType.CORRELATION in analysis_types:
            tasks.append(self.analyze_correlations(list(portfolio.keys())))
        
        if AnalysisType.MONTE_CARLO in analysis_types:
            tasks.append(self._run_monte_carlo_simulation(portfolio))
        
        if AnalysisType.VOLATILITY in analysis_types:
            for symbol in portfolio.keys():
                tasks.append(self.forecast_volatility(symbol))
        
        if self.config['enable_quantum'] and AnalysisType.SCENARIO in analysis_types:
            tasks.append(self.quantum_risk_analysis(portfolio))
        
        # Aguarda todas as análises
        completed_tasks = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Organiza resultados
        task_index = 0
        
        if AnalysisType.STRESS_TEST in analysis_types:
            results['stress_test'] = completed_tasks[task_index]
            task_index += 1
        
        if AnalysisType.CORRELATION in analysis_types:
            results['correlation'] = completed_tasks[task_index]
            task_index += 1
        
        if AnalysisType.MONTE_CARLO in analysis_types:
            results['monte_carlo'] = completed_tasks[task_index]
            task_index += 1
        
        if AnalysisType.VOLATILITY in analysis_types:
            volatility_results = []
            for i in range(len(portfolio)):
                result = completed_tasks[task_index + i]
                if not isinstance(result, Exception):
                    volatility_results.append(result)
            results['volatility_forecasts'] = volatility_results
            task_index += len(portfolio)
        
        if self.config['enable_quantum'] and AnalysisType.SCENARIO in analysis_types:
            results['quantum_analysis'] = completed_tasks[task_index]
        
        # Adiciona metadados
        results['metadata'] = {
            'timestamp': datetime.now().isoformat(),
            'portfolio_size': len(portfolio),
            'analyses_performed': [at.value for at in analysis_types],
            'version': '4.5.0'
        }
        
        return results
    
    def generate_report(
        self,
        results: Dict[str, Any],
        format: str = 'json',
        output_path: Optional[Path] = None
    ) -> Union[str, Dict]:
        """
        Gera relatório formatado dos resultados
        
        Args:
            results: Resultados da análise
            format: Formato do relatório ('json', 'html', 'pdf')
            output_path: Caminho para salvar o relatório
            
        Returns:
            Relatório no formato especificado
        """
        if format == 'json':
            report = self._generate_json_report(results)
            
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)
            
            return report
        
        elif format == 'html':
            html = self._generate_html_report(results)
            
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(html)
            
            return html
        
        else:
            raise ValueError(f"Formato não suportado: {format}")
    
    def _generate_json_report(self, results: Dict) -> Dict:
        """Gera relatório JSON estruturado"""
        report = {
            'report_metadata': {
                'generated_at': datetime.now().isoformat(),
                'system': 'VHALINOR Risk Analytics',
                'version': '4.5.0'
            },
            'executive_summary': self._generate_executive_summary(results),
            'detailed_analysis': results,
            'recommendations': self._generate_recommendations(results),
            'risk_rating': self._calculate_overall_risk_rating(results)
        }
        
        return report
    
    def _generate_html_report(self, results: Dict) -> str:
        """Gera relatório HTML interativo"""
        # Template HTML simplificado
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>VHALINOR Risk Analytics Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #2c3e50; }}
                h2 {{ color: #34495e; }}
                .metric {{ border: 1px solid #ddd; padding: 10px; margin: 10px 0; }}
                .critical {{ color: #e74c3c; }}
                .high {{ color: #e67e22; }}
                .moderate {{ color: #f39c12; }}
                .low {{ color: #27ae60; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>VHALINOR Risk Analytics Report</h1>
            <p>Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
            
            <h2>Executive Summary</h2>
            <div class="metric">
                {self._format_executive_summary_html(results)}
            </div>
            
            <h2>Detailed Analysis</h2>
            <div class="metric">
                {self._format_detailed_analysis_html(results)}
            </div>
            
            <h2>Recommendations</h2>
            <div class="metric">
                {self._format_recommendations_html(results)}
            </div>
        </body>
        </html>
        """
        
        return html_template
    
    def _generate_executive_summary(self, results: Dict) -> Dict:
        """Gera sumário executivo"""
        summary = {
            'overall_risk': 'MODERATE',
            'key_findings': [],
            'critical_issues': []
        }
        
        # Analisa resultados de stress test
        if 'stress_test' in results:
            critical_scenarios = [
                r for r in results['stress_test'] 
                if r.severity_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]
            ]
            summary['critical_issues'].extend([
                f"Stress test '{r.scenario.name}' mostra impacto de {r.portfolio_impact:.1%}"
                for r in critical_scenarios
            ])
        
        # Analisa correlações
        if 'correlation' in results:
            if results['correlation'].diversification_score < 0.3:
                summary['key_findings'].append(
                    "Baixa diversificação do portfólio"
                )
        
        # Analisa volatilidade
        if 'volatility_forecasts' in results:
            high_vol_assets = [
                f.symbol for f in results['volatility_forecasts']
                if f.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]
            ]
            if high_vol_assets:
                summary['key_findings'].append(
                    f"Alta volatilidade prevista para: {', '.join(high_vol_assets[:3])}"
                )
        
        return summary
    
    def _generate_recommendations(self, results: Dict) -> List[str]:
        """Gera recomendações baseadas nos resultados"""
        recommendations = []
        
        # Recomendações de diversificação
        if 'correlation' in results:
            if results['correlation'].diversification_score < 0.3:
                recommendations.append(
                    "Considere diversificar o portfólio com ativos de baixa correlação"
                )
            
            if results['correlation'].concentration_risk > 0.5:
                recommendations.append(
                    "Alto risco de concentração detectado - reduza exposição a ativos correlacionados"
                )
        
        # Recomendações de hedge
        if 'stress_test' in results:
            high_impact_scenarios = [
                r for r in results['stress_test'] 
                if abs(r.portfolio_impact) > 0.15
            ]
            if high_impact_scenarios:
                recommendations.append(
                    "Implementar estratégias de hedge para cenários de estresse"
                )
        
        # Recomendações de alocação
        if 'volatility_forecasts' in results:
            high_vol_assets = [
                f.symbol for f in results['volatility_forecasts']
                if f.risk_level == RiskLevel.CRITICAL
            ]
            if high_vol_assets:
                recommendations.append(
                    f"Reduzir exposição a ativos de alta volatilidade: {', '.join(high_vol_assets[:3])}"
                )
        
        return recommendations
    
    def _calculate_overall_risk_rating(self, results: Dict) -> Dict:
        """Calcula rating de risco global"""
        risk_scores = []
        
        # Score de stress test
        if 'stress_test' in results:
            for result in results['stress_test']:
                risk_scores.append(result.severity_level.value * 0.3)
        
        # Score de correlação
        if 'correlation' in results:
            risk_scores.append(results['correlation'].concentration_risk * 0.2)
        
        # Score de volatilidade
        if 'volatility_forecasts' in results:
            for forecast in results['volatility_forecasts']:
                risk_scores.append(forecast.risk_level.value * 0.1)
        
        if risk_scores:
            avg_risk = np.mean(risk_scores)
            
            if avg_risk > 0.25:
                overall = 'CRITICAL'
            elif avg_risk > 0.15:
                overall = 'HIGH'
            elif avg_risk > 0.1:
                overall = 'MODERATE'
            elif avg_risk > 0.05:
                overall = 'LOW'
            else:
                overall = 'MINIMAL'
        else:
            overall = 'UNKNOWN'
        
        return {
            'rating': overall,
            'score': float(np.mean(risk_scores)) if risk_scores else 0,
            'confidence': 'HIGH' if len(risk_scores) > 5 else 'MEDIUM'
        }
    
    # Métodos de formatação HTML
    def _format_executive_summary_html(self, results: Dict) -> str:
        summary = self._generate_executive_summary(results)
        html = f"<p><strong>Risco Global:</strong> {summary['overall_risk']}</p>"
        
        if summary['critical_issues']:
            html += "<p><strong>Issues Críticos:</strong></p><ul>"
            for issue in summary['critical_issues']:
                html += f"<li class='critical'>{issue}</li>"
            html += "</ul>"
        
        if summary['key_findings']:
            html += "<p><strong>Principais Achados:</strong></p><ul>"
            for finding in summary['key_findings']:
                html += f"<li>{finding}</li>"
            html += "</ul>"
        
        return html
    
    def _format_detailed_analysis_html(self, results: Dict) -> str:
        html = ""
        
        for key, value in results.items():
            if isinstance(value, list) and value and hasattr(value[0], '__dict__'):
                html += f"<h3>{key.replace('_', ' ').title()}</h3>"
                html += "<table><tr><th>Cenário</th><th>Impacto</th><th>Severidade</th></tr>"
                for item in value[:5]:  # Top 5
                    html += f"<tr><td>{item.scenario.name}</td>"
                    html += f"<td>{item.portfolio_impact:.1%}</td>"
                    html += f"<td class='{item.severity_level.name.lower()}'>{item.severity_level.name}</td></tr>"
                html += "</table>"
        
        return html
    
    def _format_recommendations_html(self, results: Dict) -> str:
        recommendations = self._generate_recommendations(results)
        html = "<ul>"
        for rec in recommendations:
            html += f"<li>{rec}</li>"
        html += "</ul>"
        return html
    
    def __del__(self):
        """Cleanup de recursos"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)
        if hasattr(self, 'process_executor'):
            self.process_executor.shutdown(wait=False)


# ============================================================================
# EXEMPLO DE USO E TESTES
# ============================================================================

async def main_example():
    """Exemplo de uso do sistema"""
    print("=" * 60)
    print("[START] VHALINOR Risk Analytics - Exemplo de Uso")
    print("=" * 60)
    
    # Inicializa o sistema
    analytics = VHALINORRiskAnalytics()
    
    # Define um portfólio de exemplo
    portfolio = {
        'PETR4': 0.25,
        'VALE3': 0.20,
        'ITUB4': 0.15,
        'BBDC4': 0.15,
        'WEGE3': 0.10,
        'ABEV3': 0.15
    }
    
    print(f"\n[PORTFOLIO] Portfólio de teste:")
    for symbol, weight in portfolio.items():
        print(f"  {symbol}: {weight:.1%}")
    
    # Executa análise completa
    print("\n[ANALYSIS] Executando análise de risco...")
    
    results = await analytics.analyze_portfolio_risk(
        portfolio,
        analysis_types=[
            AnalysisType.STRESS_TEST,
            AnalysisType.CORRELATION,
            AnalysisType.MONTE_CARLO,
            AnalysisType.VOLATILITY
        ]
    )
    
    # Gera relatório
    print("\n[REPORT] Gerando relatório...")
    report = analytics.generate_report(results, format='json')
    
    print("\n[SUCCESS] Análise concluída!")
    print(f"   {len(results['stress_test'])} cenários de stress test analisados")
    print(f"   {len(results['correlation'].high_correlations)} correlações altas identificadas")
    print(f"   {results['monte_carlo']['var_95']:.2f} VaR 95%")
    
    # Mostra recomendações
    print("\n[RECOMMENDATIONS] Recomendações:")
    for i, rec in enumerate(report['recommendations'], 1):
        print(f"  {i}. {rec}")
    
    # Visualiza resultados
    if analytics.config['enable_plots']:
        print("\n[PLOTS] Gerando visualizações...")
        
        # Matriz de correlação
        fig_corr = analytics.plot_correlation_matrix(
            results['correlation'],
            list(portfolio.keys()),
            "Matriz de Correlação - Portfólio Exemplo"
        )
        
        # Stress test results
        fig_stress = analytics.plot_stress_test_results(
            results['stress_test'],
            "Resultados de Stress Testing"
        )
        
        print("   [OK] Visualizações geradas")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] Exemplo concluído com sucesso!")
    print("=" * 60)
    
    return results


if __name__ == "__main__":
    # Executa exemplo assíncrono
    asyncio.run(main_example())
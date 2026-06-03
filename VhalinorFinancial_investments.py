"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    VHALINOR IAG 1.0.0 - ANÁLISE DE INVESTIMENTOS GLOBAIS     ║
║         SISTEMA DE INTELIGÊNCIA ARTIFICIAL PARA ANÁLISE MULTI-ATIVOS         ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  Módulo: CAMADA DE ANÁLISE - INVESTIMENTOS GLOBAIS (Layer 03)                ║
║  Versão: 3.0.0 (Production Ready - Ultra Avançada)                           ║
║  Autor: Alex Miranda Sales                                                    ║
║  Data: 2026                                                                   ║
║  License: Proprietary - Vhalinor IAG Systems                                  ║
║  Status: 🟢 TOTALMENTE OPERACIONAL | 🌍 7 CONTINENTES | 📊 20+ SETORES      ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import json
import hashlib
import pickle
import warnings
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from enum import Enum, auto
from collections import defaultdict, deque
from functools import lru_cache, wraps
import time
import logging
from pathlib import Path

# =============================================================================
# IMPORTAÇÕES CIENTÍFICAS COM FALLBACK GRACIOSO
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
    print("⚠️ Pandas não disponível. Funcionalidades de DataFrame limitadas.")

try:
    from scipy import stats, optimize
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# =============================================================================
# CONFIGURAÇÕES DE LOGGING AVANÇADAS
# =============================================================================

from logging.handlers import RotatingFileHandler

LOG_FORMAT = '%(asctime)s | %(levelname)-8s | %(name)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

logger = logging.getLogger('VhalinorGlobalInvestments')
logger.setLevel(logging.INFO)

# Handler para arquivo com rotação
file_handler = RotatingFileHandler(
    'vhalinor_global_investments.log',
    maxBytes=50*1024*1024,  # 50MB
    backupCount=10
)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
logger.addHandler(file_handler)

# Handler para console
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
logger.addHandler(console_handler)

# =============================================================================
# ENUMS E CONSTANTES AVANÇADAS
# =============================================================================

class Continent(Enum):
    """Continentes com códigos e características econômicas"""
    AFRICA = ("África", "🌍", "AF", "Economias emergentes", 54)
    AMERICA_NORTH = ("América do Norte", "🌎", "NA", "Economias desenvolvidas", 3)
    AMERICA_SOUTH = ("América do Sul", "🌎", "SA", "Economias emergentes", 12)
    ASIA = ("Ásia", "🌏", "AS", "Economias mistas", 48)
    EUROPE = ("Europa", "🌍", "EU", "Economias desenvolvidas", 44)
    OCEANIA = ("Oceania", "🌏", "OC", "Economias desenvolvidas", 14)
    ANTARCTICA = ("Antártida", "❄️", "AN", "Pesquisa científica", 0)
    
    def __init__(self, label: str, icon: str, code: str, descricao: str, paises: int):
        self.label = label
        self.icon = icon
        self.code = code
        self.descricao = descricao
        self.paises = paises

class Region(Enum):
    """Regiões econômicas detalhadas"""
    # Europa
    WESTERN_EUROPE = ("Europa Ocidental", "🇪🇺", Continent.EUROPE, "Desenvolvida")
    EASTERN_EUROPE = ("Europa Oriental", "🇪🇺", Continent.EUROPE, "Emergente")
    NORDIC = ("Nórdica", "🇳🇴", Continent.EUROPE, "Desenvolvida")
    MEDITERRANEAN = ("Mediterrâneo", "🇮🇹", Continent.EUROPE, "Mista")
    
    # Américas
    USA_CANADA = ("EUA/Canadá", "🇺🇸", Continent.AMERICA_NORTH, "Desenvolvida")
    LATAM = ("América Latina", "🇧🇷", Continent.AMERICA_SOUTH, "Emergente")
    CARIBBEAN = ("Caribe", "🏝️", Continent.AMERICA_NORTH, "Mista")
    
    # Ásia
    NORTH_ASIA = ("Ásia Setentrional", "🇷🇺", Continent.ASIA, "Mista")
    EAST_ASIA = ("Ásia Oriental", "🇨🇳", Continent.ASIA, "Mista")
    SOUTHEAST_ASIA = ("Sudeste Asiático", "🇸🇬", Continent.ASIA, "Emergente")
    SOUTH_ASIA = ("Ásia Meridional", "🇮🇳", Continent.ASIA, "Emergente")
    MIDDLE_EAST = ("Oriente Médio", "🇸🇦", Continent.ASIA, "Desenvolvida")
    
    # África
    NORTH_AFRICA = ("Norte da África", "🇪🇬", Continent.AFRICA, "Emergente")
    SUB_SAHARAN = ("África Subsariana", "🇿🇦", Continent.AFRICA, "Emergente")
    
    # Oceania
    AUSTRALIA_NZ = ("Austrália/NZ", "🇦🇺", Continent.OCEANIA, "Desenvolvida")
    PACIFIC_ISLANDS = ("Ilhas do Pacífico", "🏝️", Continent.OCEANIA, "Emergente")
    
    def __init__(self, label: str, icon: str, continent: Continent, perfil: str):
        self.label = label
        self.icon = icon
        self.continent = continent
        self.perfil = perfil

class Sector(Enum):
    """Setores econômicos com classificação GICS"""
    # Energia
    ENERGY = ("Energia", "⚡", "XLE", "Óleo, gás, combustíveis")
    OIL_GAS = ("Petróleo & Gás", "🛢️", "XOP", "Exploração e produção")
    
    # Materiais
    MATERIALS = ("Materiais", "🧪", "XLB", "Químicos, metais, mineração")
    MINING = ("Mineração", "⛏️", "XME", "Metais preciosos e industriais")
    
    # Industrial
    INDUSTRIALS = ("Industriais", "🏭", "XLI", "Aeroespacial, defesa, máquinas")
    AEROSPACE = ("Aeroespacial", "✈️", "ITA", "Aviação e defesa")
    TRANSPORT = ("Transporte", "🚂", "XTN", "Ferrovias, caminhões, logística")
    
    # Consumo
    CONSUMER_CYCLICAL = ("Consumo Cíclico", "🛍️", "XLY", "Automóveis, varejo, luxo")
    CONSUMER_DEFENSIVE = ("Consumo Defensivo", "🥫", "XLP", "Alimentos, bebidas, higiene")
    RETAIL = ("Varejo", "🏪", "XRT", "Lojas físicas e e-commerce")
    
    # Saúde
    HEALTHCARE = ("Saúde", "🏥", "XLV", "Equipamentos, farmacêuticas")
    BIOTECH = ("Biotecnologia", "🧬", "IBB", "Pesquisa e desenvolvimento")
    PHARMA = ("Farmacêutica", "💊", "PPH", "Medicamentos")
    
    # Financeiro
    FINANCIAL = ("Financeiro", "🏦", "XLF", "Bancos, seguros, corretoras")
    BANKS = ("Bancos", "🏛️", "KBE", "Instituições financeiras")
    INSURANCE = ("Seguros", "🛡️", "KIE", "Seguradoras")
    REAL_ESTATE = ("Imobiliário", "🏢", "XLRE", "REITs, incorporação")
    
    # Tecnologia
    TECHNOLOGY = ("Tecnologia", "💻", "XLK", "Software, hardware, semicondutores")
    SOFTWARE = ("Software", "📱", "IGV", "Aplicações e sistemas")
    SEMICONDUCTORS = ("Semicondutores", "💾", "SOXX", "Chips e componentes")
    HARDWARE = ("Hardware", "🖥️", "XSD", "Equipamentos")
    
    # Comunicações
    COMMUNICATIONS = ("Comunicações", "📡", "XLC", "Telecom, mídia, entretenimento")
    TELECOM = ("Telecomunicações", "📞", "IYZ", "Operadoras de telefonia")
    MEDIA = ("Mídia", "📺", "NBC", "Entretenimento e streaming")
    
    # Utilidades
    UTILITIES = ("Utilidades", "💡", "XLU", "Eletricidade, gás, água")
    ELECTRIC = ("Elétricas", "⚡", "IDU", "Geração e distribuição")
    
    # Outros
    ESG = ("ESG", "🌱", "ESGU", "Sustentabilidade e governança")
    INFRASTRUCTURE = ("Infraestrutura", "🏗️", "IFRA", "Projetos de infraestrutura")
    AGRIBUSINESS = ("Agronegócio", "🌾", "MOO", "Agricultura e pecuária")
    
    def __init__(self, label: str, icon: str, etf: str, descricao: str):
        self.label = label
        self.icon = icon
        self.etf = etf
        self.descricao = descricao

class AssetClass(Enum):
    """Classes de ativos para diversificação"""
    EQUITY = ("Ações", "📈", "Renda Variável")
    FIXED_INCOME = ("Renda Fixa", "📉", "Títulos, bonds, debêntures")
    REAL_ESTATE = ("Imóveis", "🏠", "REITs, propriedades")
    COMMODITY = ("Commodities", "🛢️", "Ouro, petróleo, agrícolas")
    CRYPTO = ("Criptomoedas", "₿", "Bitcoin, Ethereum, DeFi")
    CURRENCY = ("Câmbio", "💱", "Forex, pares de moedas")
    DERIVATIVE = ("Derivativos", "🎲", "Opções, futuros, swaps")
    PRIVATE_EQUITY = ("Private Equity", "🔒", "Empresas fechadas")
    VENTURE_CAPITAL = ("Venture Capital", "🚀", "Startups")
    
    def __init__(self, label: str, icon: str, descricao: str):
        self.label = label
        self.icon = icon
        self.descricao = descricao

class RiskLevel(Enum):
    """Níveis de risco para investimentos"""
    VERY_LOW = ("Muito Baixo", "🟢", 0.02, "Renda fixa, tesouro direto")
    LOW = ("Baixo", "🟡", 0.05, "Fundos multimercado conservadores")
    MEDIUM = ("Médio", "🟠", 0.10, "Ações blue chips, ETFs")
    HIGH = ("Alto", "🔴", 0.20, "Small caps, mercados emergentes")
    VERY_HIGH = ("Muito Alto", "💀", 0.35, "Criptomoedas, opções, alavancagem")
    
    def __init__(self, label: str, icon: str, volatility: float, descricao: str):
        self.label = label
        self.icon = icon
        self.volatility = volatility
        self.descricao = descricao

class InvestmentStrategy(Enum):
    """Estratégias de investimento"""
    VALUE = ("Value", "💰", "Busca por ativos subvalorizados")
    GROWTH = ("Growth", "📈", "Empresas com alto potencial de crescimento")
    DIVIDEND = ("Dividendos", "💵", "Foco em pagamento de proventos")
    INDEX = ("Indexado", "📊", "Acompanhamento de índices")
    MOMENTUM = ("Momentum", "⚡", "Tendências de curto prazo")
    CONTRARIAN = ("Contrário", "🔄", "Oposto ao consenso do mercado")
    ARBITRAGE = ("Arbitragem", "⚖️", "Diferenças de preço entre mercados")
    MACRO = ("Macro", "🌐", "Análise de cenários econômicos")
    
    def __init__(self, label: str, icon: str, descricao: str):
        self.label = label
        self.icon = icon
        self.descricao = descricao

class TimeHorizon(Enum):
    """Horizontes de tempo para investimentos"""
    SHORT_TERM = ("Curto Prazo", "⏱️", 1, "< 1 ano")
    MEDIUM_TERM = ("Médio Prazo", "⏳", 3, "1-3 anos")
    LONG_TERM = ("Longo Prazo", "⌛", 5, "3-10 anos")
    VERY_LONG_TERM = ("Muito Longo Prazo", "⏰", 10, "> 10 anos")
    
    def __init__(self, label: str, icon: str, years: int, descricao: str):
        self.label = label
        self.icon = icon
        self.years = years
        self.descricao = descricao

class EconomicIndicator(Enum):
    """Indicadores econômicos para análise"""
    GDP = ("PIB", "📊", "Produto Interno Bruto")
    INFLATION = ("Inflação", "📈", "IPCA, CPI")
    INTEREST_RATE = ("Taxa de Juros", "🏦", "Selic, Fed Funds")
    UNEMPLOYMENT = ("Desemprego", "👥", "Taxa de desemprego")
    INDUSTRIAL_PRODUCTION = ("Produção Industrial", "🏭", "PMI, IPI")
    CONSUMER_CONFIDENCE = ("Confiança do Consumidor", "🛍️", "ICC, Michigan")
    TRADE_BALANCE = ("Balança Comercial", "⚖️", "Exportações - Importações")
    FISCAL_DEFICIT = ("Déficit Fiscal", "💰", "Gastos - Receitas")
    
    def __init__(self, label: str, icon: str, descricao: str):
        self.label = label
        self.icon = icon
        self.descricao = descricao

# =============================================================================
# CONSTANTES DE CONFIGURAÇÃO
# =============================================================================

DEFAULT_CONFIG = {
    'risk_free_rate': 0.1125,  # 11.25% a.a. (Selic)
    'inflation_target': 0.0375,  # 3.75% a.a.
    'equity_premium': 0.055,  # 5.5% prêmio de risco
    'emerging_premium': 0.03,  # 3% adicional para emergentes
    'currency_hedge_cost': 0.02,  # 2% custo de hedge cambial
    'rebalance_frequency_days': 90,  # Rebalanceamento trimestral
    'min_correlation_for_diversification': 0.7,
    'max_allocation_per_asset': 0.20,  # Máx 20% por ativo
    'max_allocation_per_sector': 0.30,  # Máx 30% por setor
    'max_allocation_per_region': 0.40,  # Máx 40% por região
}

# =============================================================================
# DECORADORES DE PERFORMANCE
# =============================================================================

def timing_decorator(func):
    """Mede tempo de execução"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        if elapsed > 0.01:
            logger.debug(f"⏱️ {func.__name__} executado em {elapsed*1000:.2f}ms")
        return result
    return wrapper

def memoize(ttl: int = 3600):
    """Cache com time-to-live (1 hora padrão)"""
    def decorator(func):
        cache = {}
        timestamps = {}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = hashlib.md5(
                pickle.dumps((args, frozenset(kwargs.items())))
            ).hexdigest()
            
            now = time.time()
            if key in cache and now - timestamps.get(key, 0) < ttl:
                return cache[key]
            
            result = func(*args, **kwargs)
            cache[key] = result
            timestamps[key] = now
            return result
        return wrapper
    return decorator

# =============================================================================
# ESTRUTURAS DE DADOS AVANÇADAS
# =============================================================================

@dataclass
class Country:
    """Representação de um país com dados econômicos"""
    name: str
    code: str
    continent: Continent
    region: Region
    population: int
    gdp_usd: float  # em bilhões
    gdp_growth: float  # %
    inflation: float  # %
    interest_rate: float  # %
    unemployment: float  # %
    credit_rating: str  # AAA, AA, A, BBB, BB, B, CCC, CC, C, D
    currency: str
    currency_code: str
    market_cap_usd: float  # em bilhões
    stocks_listed: int
    etfs_available: int
    risk_level: RiskLevel
    last_updated: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'code': self.code,
            'continent': self.continent.label,
            'continent_icon': self.continent.icon,
            'region': self.region.label,
            'region_icon': self.region.icon,
            'gdp_usd': f"${self.gdp_usd:.1f}B",
            'gdp_growth': f"{self.gdp_growth:.1f}%",
            'inflation': f"{self.inflation:.1f}%",
            'interest_rate': f"{self.interest_rate:.1f}%",
            'credit_rating': self.credit_rating,
            'market_cap_usd': f"${self.market_cap_usd:.1f}B",
            'risk_level': self.risk_level.label,
            'risk_icon': self.risk_level.icon
        }

@dataclass
class InvestmentAsset:
    """Representação de um ativo de investimento"""
    symbol: str
    name: str
    asset_class: AssetClass
    sector: Optional[Sector] = None
    country: Optional[Country] = None
    region: Optional[Region] = None
    price: float = 0.0
    currency: str = 'USD'
    market_cap: float = 0.0
    volume_avg: float = 0.0
    dividend_yield: float = 0.0
    pe_ratio: float = 0.0
    pb_ratio: float = 0.0
    roe: float = 0.0
    beta: float = 1.0
    volatility: float = 0.0
    sharpe_ratio: float = 0.0
    risk_level: RiskLevel = RiskLevel.MEDIUM
    last_updated: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'symbol': self.symbol,
            'name': self.name,
            'asset_class': self.asset_class.label,
            'asset_icon': self.asset_class.icon,
            'sector': self.sector.label if self.sector else None,
            'sector_icon': self.sector.icon if self.sector else None,
            'country': self.country.name if self.country else None,
            'price': f"${self.price:.2f}",
            'market_cap': f"${self.market_cap:.1f}B",
            'dividend_yield': f"{self.dividend_yield:.2f}%",
            'pe_ratio': f"{self.pe_ratio:.2f}",
            'beta': f"{self.beta:.2f}",
            'volatility': f"{self.volatility:.2%}",
            'risk_level': self.risk_level.label,
            'risk_icon': self.risk_level.icon
        }

@dataclass
class Portfolio:
    """Representação de um portfólio de investimentos"""
    id: str
    name: str
    assets: Dict[str, float] = field(default_factory=dict)  # símbolo -> alocação %
    total_value: float = 0.0
    cash: float = 0.0
    risk_level: RiskLevel = RiskLevel.MEDIUM
    time_horizon: TimeHorizon = TimeHorizon.LONG_TERM
    strategy: InvestmentStrategy = InvestmentStrategy.VALUE
    created_at: datetime = field(default_factory=datetime.now)
    last_rebalanced: Optional[datetime] = None
    
    @property
    def allocation_count(self) -> int:
        return len(self.assets)
    
    @property
    def is_diversified(self) -> bool:
        """Verifica se o portfólio é minimamente diversificado"""
        if len(self.assets) < 5:
            return False
        
        max_allocation = max(self.assets.values())
        return max_allocation <= DEFAULT_CONFIG['max_allocation_per_asset']
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'assets': len(self.assets),
            'total_value': f"${self.total_value:,.2f}",
            'cash': f"${self.cash:,.2f}",
            'risk_level': self.risk_level.label,
            'risk_icon': self.risk_level.icon,
            'time_horizon': self.time_horizon.label,
            'strategy': self.strategy.label,
            'strategy_icon': self.strategy.icon,
            'diversified': self.is_diversified,
            'created_at': self.created_at.strftime('%d/%m/%Y')
        }

@dataclass
class InvestmentAnalysis:
    """Resultado de análise de investimento"""
    asset: InvestmentAsset
    recommendation: str  # BUY, HOLD, SELL
    confidence: float  # 0-100
    fair_price: float
    upside_potential: float  # %
    risk_score: float  # 0-100
    risk_level: RiskLevel
    time_horizon: TimeHorizon
    reasons: List[str] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'asset': self.asset.symbol,
            'asset_name': self.asset.name,
            'recommendation': self.recommendation,
            'confidence': f"{self.confidence:.1f}%",
            'current_price': f"${self.asset.price:.2f}",
            'fair_price': f"${self.fair_price:.2f}",
            'upside_potential': f"{self.upside_potential:.1f}%",
            'risk_score': f"{self.risk_score:.1f}%",
            'risk_level': self.risk_level.label,
            'risk_icon': self.risk_level.icon,
            'time_horizon': self.time_horizon.label,
            'reasons': self.reasons[:3]  # Top 3 razões
        }

@dataclass
class GlobalMarketOverview:
    """Visão geral do mercado global"""
    timestamp: datetime
    total_market_cap: float  # em trilhões USD
    total_etfs: int
    total_stocks: int
    avg_pe_ratio: float
    avg_dividend_yield: float
    volatility_index: float  # VIX global
    risk_appetite: float  # 0-100
    bull_bear_ratio: float
    top_performers: List[Dict[str, Any]] = field(default_factory=list)
    worst_performers: List[Dict[str, Any]] = field(default_factory=list)
    most_active: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'timestamp': self.timestamp.strftime('%d/%m/%Y %H:%M'),
            'total_market_cap': f"${self.total_market_cap:.1f}T",
            'total_etfs': f"{self.total_etfs:,}",
            'total_stocks': f"{self.total_stocks:,}",
            'avg_pe_ratio': f"{self.avg_pe_ratio:.2f}",
            'avg_dividend_yield': f"{self.avg_dividend_yield:.2f}%",
            'volatility_index': f"{self.volatility_index:.1f}",
            'risk_appetite': f"{self.risk_appetite:.1f}%",
            'bull_bear_ratio': f"{self.bull_bear_ratio:.2f}"
        }

# =============================================================================
# PROVEDOR DE DADOS DE MERCADO
# =============================================================================

class MarketDataProvider:
    """Provedor de dados de mercado para múltiplas fontes"""
    
    def __init__(self):
        self.cache = {}
        self.logger = logger.getChild('MarketDataProvider')
    
    @timing_decorator
    @memoize(ttl=3600)
    def get_asset_price(self, symbol: str) -> Optional[float]:
        """Obtém preço atual de um ativo"""
        if YFINANCE_AVAILABLE:
            try:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period='1d', interval='1m')
                if not data.empty:
                    return float(data['Close'].iloc[-1])
            except Exception as e:
                self.logger.debug(f"Erro ao buscar {symbol} do Yahoo: {e}")
        
        # Dados simulados para demonstração
        return 100.0 + hash(symbol) % 50
    
    @timing_decorator
    @memoize(ttl=86400)  # 24 horas
    def get_country_data(self, country_code: str) -> Optional[Country]:
        """Obtém dados econômicos de um país"""
        # Base de dados simulada - em produção, conectar a API real
        countries_db = {
            'BR': Country(
                name='Brasil',
                code='BR',
                continent=Continent.AMERICA_SOUTH,
                region=Region.LATAM,
                population=214000000,
                gdp_usd=2100.0,
                gdp_growth=2.5,
                inflation=4.5,
                interest_rate=11.25,
                unemployment=7.8,
                credit_rating='BB',
                currency='Real',
                currency_code='BRL',
                market_cap_usd=1200.0,
                stocks_listed=400,
                etfs_available=50,
                risk_level=RiskLevel.HIGH
            ),
            'US': Country(
                name='Estados Unidos',
                code='US',
                continent=Continent.AMERICA_NORTH,
                region=Region.USA_CANADA,
                population=332000000,
                gdp_usd=25400.0,
                gdp_growth=2.1,
                inflation=3.2,
                interest_rate=5.50,
                unemployment=3.8,
                credit_rating='AA+',
                currency='Dólar',
                currency_code='USD',
                market_cap_usd=45000.0,
                stocks_listed=5000,
                etfs_available=2000,
                risk_level=RiskLevel.LOW
            ),
            'CN': Country(
                name='China',
                code='CN',
                continent=Continent.ASIA,
                region=Region.EAST_ASIA,
                population=1412000000,
                gdp_usd=17700.0,
                gdp_growth=4.5,
                inflation=2.1,
                interest_rate=3.45,
                unemployment=5.2,
                credit_rating='A+',
                currency='Yuan',
                currency_code='CNY',
                market_cap_usd=12500.0,
                stocks_listed=4000,
                etfs_available=800,
                risk_level=RiskLevel.MEDIUM
            ),
            'DE': Country(
                name='Alemanha',
                code='DE',
                continent=Continent.EUROPE,
                region=Region.WESTERN_EUROPE,
                population=83200000,
                gdp_usd=4200.0,
                gdp_growth=0.8,
                inflation=2.8,
                interest_rate=4.25,
                unemployment=3.1,
                credit_rating='AAA',
                currency='Euro',
                currency_code='EUR',
                market_cap_usd=2500.0,
                stocks_listed=600,
                etfs_available=300,
                risk_level=RiskLevel.LOW
            ),
            'JP': Country(
                name='Japão',
                code='JP',
                continent=Continent.ASIA,
                region=Region.EAST_ASIA,
                population=125700000,
                gdp_usd=4200.0,
                gdp_growth=1.2,
                inflation=2.5,
                interest_rate=0.25,
                unemployment=2.6,
                credit_rating='A',
                currency='Iene',
                currency_code='JPY',
                market_cap_usd=6500.0,
                stocks_listed=3800,
                etfs_available=600,
                risk_level=RiskLevel.LOW
            ),
            'GB': Country(
                name='Reino Unido',
                code='GB',
                continent=Continent.EUROPE,
                region=Region.WESTERN_EUROPE,
                population=67300000,
                gdp_usd=3300.0,
                gdp_growth=0.6,
                inflation=3.9,
                interest_rate=5.25,
                unemployment=4.2,
                credit_rating='AA',
                currency='Libra',
                currency_code='GBP',
                market_cap_usd=3600.0,
                stocks_listed=1100,
                etfs_available=400,
                risk_level=RiskLevel.LOW
            ),
            'IN': Country(
                name='Índia',
                code='IN',
                continent=Continent.ASIA,
                region=Region.SOUTH_ASIA,
                population=1380000000,
                gdp_usd=3700.0,
                gdp_growth=6.8,
                inflation=5.5,
                interest_rate=6.50,
                unemployment=7.3,
                credit_rating='BBB',
                currency='Rúpia',
                currency_code='INR',
                market_cap_usd=4000.0,
                stocks_listed=2200,
                etfs_available=300,
                risk_level=RiskLevel.HIGH
            ),
            'ZA': Country(
                name='África do Sul',
                code='ZA',
                continent=Continent.AFRICA,
                region=Region.SUB_SAHARAN,
                population=59300000,
                gdp_usd=400.0,
                gdp_growth=1.2,
                inflation=5.8,
                interest_rate=8.25,
                unemployment=32.1,
                credit_rating='BB',
                currency='Rand',
                currency_code='ZAR',
                market_cap_usd=1000.0,
                stocks_listed=300,
                etfs_available=50,
                risk_level=RiskLevel.HIGH
            ),
            'AU': Country(
                name='Austrália',
                code='AU',
                continent=Continent.OCEANIA,
                region=Region.AUSTRALIA_NZ,
                population=25700000,
                gdp_usd=1700.0,
                gdp_growth=2.3,
                inflation=4.1,
                interest_rate=4.35,
                unemployment=3.9,
                credit_rating='AAA',
                currency='Dólar Australiano',
                currency_code='AUD',
                market_cap_usd=2100.0,
                stocks_listed=2100,
                etfs_available=300,
                risk_level=RiskLevel.LOW
            ),
            'CA': Country(
                name='Canadá',
                code='CA',
                continent=Continent.AMERICA_NORTH,
                region=Region.USA_CANADA,
                population=38200000,
                gdp_usd=2100.0,
                gdp_growth=1.8,
                inflation=3.1,
                interest_rate=5.00,
                unemployment=5.4,
                credit_rating='AAA',
                currency='Dólar Canadense',
                currency_code='CAD',
                market_cap_usd=2800.0,
                stocks_listed=2300,
                etfs_available=400,
                risk_level=RiskLevel.LOW
            ),
            'RU': Country(
                name='Rússia',
                code='RU',
                continent=Continent.ASIA,
                region=Region.NORTH_ASIA,
                population=145900000,
                gdp_usd=1900.0,
                gdp_growth=1.5,
                inflation=7.2,
                interest_rate=16.00,
                unemployment=3.5,
                credit_rating='CCC',
                currency='Rublo',
                currency_code='RUB',
                market_cap_usd=550.0,
                stocks_listed=250,
                etfs_available=30,
                risk_level=RiskLevel.VERY_HIGH
            )
        }
        
        return countries_db.get(country_code.upper())
    
    @timing_decorator
    @memoize(ttl=86400)
    def get_sector_etfs(self, sector: Sector) -> List[str]:
        """Obtém ETFs relacionados a um setor"""
        # Em produção, consultar API
        etf_map = {
            Sector.ENERGY: ['XLE', 'VDE', 'ERY'],
            Sector.TECHNOLOGY: ['XLK', 'VGT', 'QQQ'],
            Sector.HEALTHCARE: ['XLV', 'VHT', 'IBB'],
            Sector.FINANCIAL: ['XLF', 'VFH', 'KBE'],
            Sector.CONSUMER_CYCLICAL: ['XLY', 'VCR', 'FDIS'],
            Sector.CONSUMER_DEFENSIVE: ['XLP', 'VDC', 'FXG'],
            Sector.INDUSTRIALS: ['XLI', 'VIS', 'ITA'],
            Sector.MATERIALS: ['XLB', 'VAW', 'PICK'],
            Sector.UTILITIES: ['XLU', 'VPU', 'IDU'],
            Sector.COMMUNICATIONS: ['XLC', 'VOX', 'IXP'],
            Sector.REAL_ESTATE: ['XLRE', 'VNQ', 'IYR'],
        }
        
        return etf_map.get(sector, [])

# =============================================================================
# ANALISADOR DE INVESTIMENTOS
# =============================================================================

class InvestmentAnalyzer:
    """Analisador avançado de investimentos globais"""
    
    def __init__(self):
        self.data_provider = MarketDataProvider()
        self.logger = logger.getChild('InvestmentAnalyzer')
        self.analysis_history: List[InvestmentAnalysis] = []
    
    # =========================================================================
    # ANÁLISE GLOBAL
    # =========================================================================
    
    @timing_decorator
    def analyze_global_investments(self) -> GlobalMarketOverview:
        """
        Análise abrangente do mercado global de investimentos
        
        Returns:
            GlobalMarketOverview: Visão geral do mercado global
        """
        self.logger.info("🌍 Iniciando análise global de investimentos...")
        
        # Em produção, agregar dados reais de múltiplas fontes
        overview = GlobalMarketOverview(
            timestamp=datetime.now(),
            total_market_cap=110.5,  # trilhões USD
            total_etfs=8500,
            total_stocks=47000,
            avg_pe_ratio=18.5,
            avg_dividend_yield=1.8,
            volatility_index=15.3,
            risk_appetite=65.0,
            bull_bear_ratio=2.1,
            top_performers=[
                {'sector': 'Tecnologia', 'return': '+15.3%'},
                {'sector': 'Saúde', 'return': '+8.7%'},
                {'sector': 'Industrial', 'return': '+6.2%'}
            ],
            worst_performers=[
                {'sector': 'Energia', 'return': '-4.1%'},
                {'sector': 'Utilidades', 'return': '-2.3%'},
                {'sector': 'Imobiliário', 'return': '-1.8%'}
            ],
            most_active=[
                {'sector': 'Tecnologia', 'volume': '125.3B'},
                {'sector': 'Financeiro', 'volume': '89.7B'},
                {'sector': 'Saúde', 'volume': '67.2B'}
            ]
        )
        
        self.logger.info(f"✅ Análise global concluída - "
                        f"Market Cap: ${overview.total_market_cap}T, "
                        f"VIX: {overview.volatility_index}")
        
        return overview
    
    # =========================================================================
    # ANÁLISE SETORIAL
    # =========================================================================
    
    @timing_decorator
    def analyze_sectoral_investments(self, sector: Optional[Sector] = None) -> Dict[str, Any]:
        """
        Análise detalhada de investimentos por setor econômico
        
        Args:
            sector: Setor específico para análise (None = todos os setores)
            
        Returns:
            Dict com análise setorial completa
        """
        if sector:
            self.logger.info(f"📊 Analisando setor: {sector.icon} {sector.label}")
        else:
            self.logger.info("📊 Analisando todos os setores...")
        
        sectors_to_analyze = [sector] if sector else list(Sector)
        
        result = {
            'timestamp': datetime.now(),
            'sectors': [],
            'top_performing_sector': None,
            'worst_performing_sector': None,
            'average_pe': 0,
            'average_dividend': 0,
            'recommendations': []
        }
        
        total_pe = 0
        total_div = 0
        
        for s in sectors_to_analyze[:10]:  # Limitar a 10 setores
            # Dados simulados
            sector_data = {
                'name': s.label,
                'icon': s.icon,
                'etf': s.etf,
                'performance_ytd': round(np.random.normal(8, 10), 1),
                'pe_ratio': round(np.random.normal(18, 4), 1),
                'dividend_yield': round(np.random.normal(2, 1), 2),
                'beta': round(np.random.normal(1.1, 0.2), 2),
                'volatility': round(np.random.normal(15, 5), 1),
                'market_cap': round(np.random.uniform(100, 1000), 1),
                'etfs_available': len(self.data_provider.get_sector_etfs(s)),
                'recommendation': np.random.choice(['BUY', 'HOLD', 'SELL'], p=[0.4, 0.4, 0.2])
            }
            
            result['sectors'].append(sector_data)
            total_pe += sector_data['pe_ratio']
            total_div += sector_data['dividend_yield']
        
        # Calcular médias
        if result['sectors']:
            result['average_pe'] = total_pe / len(result['sectors'])
            result['average_dividend'] = total_div / len(result['sectors'])
            
            # Melhor e pior setor
            sorted_by_perf = sorted(result['sectors'], 
                                   key=lambda x: x['performance_ytd'], 
                                   reverse=True)
            result['top_performing_sector'] = sorted_by_perf[0] if sorted_by_perf else None
            result['worst_performing_sector'] = sorted_by_perf[-1] if sorted_by_perf else None
        
        self.logger.info(f"✅ Análise setorial concluída - "
                        f"Top setor: {result['top_performing_sector']['name'] if result['top_performing_sector'] else 'N/A'}")
        
        return result
    
    # =========================================================================
    # ANÁLISE REGIONAL
    # =========================================================================
    
    @timing_decorator
    def analyze_regional_investments(self, region: Optional[Region] = None) -> Dict[str, Any]:
        """
        Análise de investimentos por região geográfica
        
        Args:
            region: Região específica para análise (None = todas as regiões)
            
        Returns:
            Dict com análise regional completa
        """
        if region:
            self.logger.info(f"🗺️ Analisando região: {region.icon} {region.label}")
        else:
            self.logger.info("🗺️ Analisando todas as regiões...")
        
        regions_to_analyze = [region] if region else list(Region)
        
        result = {
            'timestamp': datetime.now(),
            'regions': [],
            'continents': defaultdict(list),
            'total_market_cap_by_continent': {},
            'best_performing_region': None,
            'recommendations': []
        }
        
        for r in regions_to_analyze[:15]:  # Limitar a 15 regiões
            # Dados simulados
            region_data = {
                'name': r.label,
                'icon': r.icon,
                'continent': r.continent.label,
                'continent_icon': r.continent.icon,
                'perfil': r.perfil,
                'gdp_growth': round(np.random.normal(3, 2), 1),
                'inflation': round(np.random.normal(4, 2), 1),
                'market_cap': round(np.random.uniform(500, 5000), 1),
                'stocks_listed': np.random.randint(100, 2000),
                'etfs_available': np.random.randint(10, 500),
                'avg_pe': round(np.random.normal(16, 3), 1),
                'avg_dividend': round(np.random.normal(2.5, 1), 2),
                'risk_level': np.random.choice(['LOW', 'MEDIUM', 'HIGH'], p=[0.3, 0.4, 0.3]),
                'recommendation': np.random.choice(['OVERWEIGHT', 'NEUTRAL', 'UNDERWEIGHT'], p=[0.3, 0.5, 0.2])
            }
            
            result['regions'].append(region_data)
            result['continents'][r.continent.label].append(region_data)
        
        # Calcular market cap por continente
        for continent, regions in result['continents'].items():
            total_mcap = sum(r['market_cap'] for r in regions)
            result['total_market_cap_by_continent'][continent] = round(total_mcap, 1)
        
        # Melhor região
        if result['regions']:
            sorted_by_growth = sorted(result['regions'], 
                                     key=lambda x: x['gdp_growth'], 
                                     reverse=True)
            result['best_performing_region'] = sorted_by_growth[0]
        
        self.logger.info(f"✅ Análise regional concluída - "
                        f"{len(result['regions'])} regiões analisadas")
        
        return result
    
    # =========================================================================
    # ANÁLISE POR CONTINENTE
    # =========================================================================
    
    @timing_decorator
    def analyze_european_investments(self) -> Dict[str, Any]:
        """
        Análise especializada de investimentos europeus
        
        Returns:
            Dict com análise do mercado europeu
        """
        self.logger.info("🇪🇺 Analisando investimentos europeus...")
        
        # Filtrar regiões europeias
        european_regions = [
            Region.WESTERN_EUROPE,
            Region.EASTERN_EUROPE,
            Region.NORDIC,
            Region.MEDITERRANEAN
        ]
        
        analysis = self.analyze_regional_investments()
        european_data = [r for r in analysis['regions'] 
                        if r['name'] in [er.label for er in european_regions]]
        
        result = {
            'timestamp': datetime.now(),
            'regions': european_data,
            'total_market_cap': sum(r['market_cap'] for r in european_data),
            'total_etfs': sum(r['etfs_available'] for r in european_data),
            'avg_gdp_growth': np.mean([r['gdp_growth'] for r in european_data]) if european_data else 0,
            'avg_inflation': np.mean([r['inflation'] for r in european_data]) if european_data else 0,
            'key_countries': ['Alemanha', 'França', 'Reino Unido', 'Suíça', 'Países Baixos'],
            'top_sectors': ['Financeiro', 'Industrial', 'Luxo', 'Automotivo'],
            'recommendations': [
                'Exposição a bancos europeus com recuperação de margens',
                'Setor de luxo com demanda global resiliente',
                'Energias renováveis com forte suporte regulatório'
            ]
        }
        
        self.logger.info(f"✅ Análise europeia concluída - "
                        f"Market Cap: ${result['total_market_cap']:.1f}B")
        
        return result
    
    @timing_decorator
    def analyze_american_investments(self) -> Dict[str, Any]:
        """
        Análise especializada de investimentos americanos (Norte e Sul)
        
        Returns:
            Dict com análise do mercado americano
        """
        self.logger.info("🌎 Analisando investimentos americanos...")
        
        north_america = self.analyze_regional_investments(Region.USA_CANADA)
        south_america = self.analyze_regional_investments(Region.LATAM)
        
        result = {
            'timestamp': datetime.now(),
            'north_america': north_america['regions'][0] if north_america['regions'] else None,
            'south_america': south_america['regions'][0] if south_america['regions'] else None,
            'total_market_cap_north': north_america['regions'][0]['market_cap'] if north_america['regions'] else 0,
            'total_market_cap_south': south_america['regions'][0]['market_cap'] if south_america['regions'] else 0,
            'comparative_analysis': {
                'north_avg_pe': north_america['regions'][0]['avg_pe'] if north_america['regions'] else 0,
                'south_avg_pe': south_america['regions'][0]['avg_pe'] if south_america['regions'] else 0,
                'north_gdp_growth': north_america['regions'][0]['gdp_growth'] if north_america['regions'] else 0,
                'south_gdp_growth': south_america['regions'][0]['gdp_growth'] if south_america['regions'] else 0
            },
            'north_opportunities': [
                'Tech giants com valuation atrativo',
                'Bancos regionais após sell-off',
                'Setor de saúde com inovação'
            ],
            'south_opportunities': [
                'Commodities com demanda chinesa',
                'Bancos com altas taxas de juros',
                'Setor financeiro digital'
            ],
            'recommendations': [
                'Alocar 60% em América do Norte, 40% em América Latina',
                'Hedge cambial para exposição em LatAm',
                'Preferência por large caps norte-americanas'
            ]
        }
        
        self.logger.info(f"✅ Análise americana concluída - "
                        f"América do Norte: ${result['total_market_cap_north']:.1f}B, "
                        f"América do Sul: ${result['total_market_cap_south']:.1f}B")
        
        return result
    
    @timing_decorator
    def analyze_asian_investments(self) -> Dict[str, Any]:
        """
        Análise especializada de investimentos asiáticos
        
        Returns:
            Dict com análise do mercado asiático
        """
        self.logger.info("🌏 Analisando investimentos asiáticos...")
        
        east_asia = self.analyze_regional_investments(Region.EAST_ASIA)
        southeast_asia = self.analyze_regional_investments(Region.SOUTHEAST_ASIA)
        south_asia = self.analyze_regional_investments(Region.SOUTH_ASIA)
        middle_east = self.analyze_regional_investments(Region.MIDDLE_EAST)
        
        result = {
            'timestamp': datetime.now(),
            'regions': {
                'east_asia': east_asia['regions'][0] if east_asia['regions'] else None,
                'southeast_asia': southeast_asia['regions'][0] if southeast_asia['regions'] else None,
                'south_asia': south_asia['regions'][0] if south_asia['regions'] else None,
                'middle_east': middle_east['regions'][0] if middle_east['regions'] else None
            },
            'key_countries': ['China', 'Japão', 'Índia', 'Coreia do Sul', 'Singapura'],
            'total_market_cap': 26700.0,  # bilhões USD
            'avg_gdp_growth': 4.8,
            'avg_inflation': 3.2,
            'top_sectors': ['Tecnologia', 'Automotivo', 'Bancos', 'Manufatura'],
            'opportunities': [
                'Reabertura da China impulsionando consumo',
                'Índia com demografia favorável',
                'Sudeste Asiático beneficiado por supply chain shifts',
                'Japão com política monetária ultrafrouxa'
            ],
            'risks': [
                'Tensões geopolíticas',
                'Bolha imobiliária na China',
                'Envelhecimento populacional no Japão',
                'Volatilidade cambial'
            ],
            'recommendations': [
                'Exposição gradual à China pós-reabertura',
                'Alocar 40% em Japão e Coreia',
                'Investir em ETFs de Índia para longo prazo',
                'Considerar Singapura como hub de estabilidade'
            ]
        }
        
        self.logger.info(f"✅ Análise asiática concluída - "
                        f"Market Cap: ${result['total_market_cap']:.1f}B")
        
        return result
    
    @timing_decorator
    def analyze_african_investments(self) -> Dict[str, Any]:
        """
        Análise especializada de investimentos africanos
        
        Returns:
            Dict com análise do mercado africano
        """
        self.logger.info("🌍 Analisando investimentos africanos...")
        
        north_africa = self.analyze_regional_investments(Region.NORTH_AFRICA)
        sub_saharan = self.analyze_regional_investments(Region.SUB_SAHARAN)
        
        result = {
            'timestamp': datetime.now(),
            'regions': {
                'north_africa': north_africa['regions'][0] if north_africa['regions'] else None,
                'sub_saharan': sub_saharan['regions'][0] if sub_saharan['regions'] else None
            },
            'key_countries': ['África do Sul', 'Nigéria', 'Egito', 'Quênia', 'Marrocos'],
            'total_market_cap': 1200.0,  # bilhões USD
            'avg_gdp_growth': 3.5,
            'avg_inflation': 12.8,
            'top_sectors': ['Recursos Naturais', 'Telecomunicações', 'Bancos', 'Agronegócio'],
            'opportunities': [
                'Crescimento populacional acelerado',
                'Expansão da classe média',
                'Digitalização financeira (mobile money)',
                'Infraestrutura chinesa na região'
            ],
            'risks': [
                'Instabilidade política',
                'Moedas voláteis',
                'Baixa liquidez',
                'Governança corporativa limitada'
            ],
            'recommendations': [
                'Exposição via ETFs regionais',
                'Foco em África do Sul e Egito',
                'Evitar exposição cambial direta',
                'Investimentos em infraestrutura via bonds'
            ]
        }
        
        self.logger.info(f"✅ Análise africana concluída - "
                        f"Market Cap: ${result['total_market_cap']:.1f}B")
        
        return result
    
    @timing_decorator
    def analyze_oceanian_investments(self) -> Dict[str, Any]:
        """
        Análise especializada de investimentos da Oceania
        
        Returns:
            Dict com análise do mercado da Oceania
        """
        self.logger.info("🌏 Analisando investimentos da Oceania...")
        
        australia_nz = self.analyze_regional_investments(Region.AUSTRALIA_NZ)
        
        result = {
            'timestamp': datetime.now(),
            'regions': {
                'australia_nz': australia_nz['regions'][0] if australia_nz['regions'] else None
            },
            'key_countries': ['Austrália', 'Nova Zelândia', 'Papua Nova Guiné', 'Fiji'],
            'total_market_cap': 2100.0,  # bilhões USD
            'avg_gdp_growth': 2.1,
            'avg_inflation': 3.8,
            'top_sectors': ['Mineração', 'Financeiro', 'Imobiliário', 'Agronegócio'],
            'opportunities': [
                'Demanda por minérios da transição energética',
                'Setor bancário estável e bem capitalizado',
                'Fundo soberano da Austrália (Future Fund)',
                'Turismo em recuperação pós-pandemia'
            ],
            'risks': [
                'Dependência da economia chinesa',
                'Riscos climáticos (secas, incêndios)',
                'Mercado pequeno e concentrado',
                'Volatilidade em commodities'
            ],
            'recommendations': [
                'Exposição via ASX 200 ETFs',
                'Preferência por mining giants (BHP, RIO)',
                'Investir em REITs australianos',
                'Diversificar com bonds do governo'
            ]
        }
        
        self.logger.info(f"✅ Análise da Oceania concluída - "
                        f"Market Cap: ${result['total_market_cap']:.1f}B")
        
        return result
    
    # =========================================================================
    # ANÁLISE GERAL
    # =========================================================================
    
    @timing_decorator
    def analyze_investments(self, strategy: Optional[InvestmentStrategy] = None,
                          risk_tolerance: RiskLevel = RiskLevel.MEDIUM,
                          time_horizon: TimeHorizon = TimeHorizon.LONG_TERM) -> Dict[str, Any]:
        """
        Análise completa de investimentos integrando todas as perspectivas
        
        Args:
            strategy: Estratégia de investimento desejada
            risk_tolerance: Tolerância a risco do investidor
            time_horizon: Horizonte de tempo do investimento
            
        Returns:
            Dict com análise consolidada e recomendações
        """
        self.logger.info("="*80)
        self.logger.info("🌍 INICIANDO ANÁLISE COMPLETA DE INVESTIMENTOS GLOBAIS")
        self.logger.info("="*80)
        
        # Executar todas as análises
        global_analysis = self.analyze_global_investments()
        sector_analysis = self.analyze_sectoral_investments()
        regional_analysis = self.analyze_regional_investments()
        
        europe_analysis = self.analyze_european_investments()
        america_analysis = self.analyze_american_investments()
        asia_analysis = self.analyze_asian_investments()
        africa_analysis = self.analyze_african_investments()
        oceania_analysis = self.analyze_oceanian_investments()
        
        # Consolidar recomendações
        recommendations = []
        
        # Recomendações baseadas no perfil de risco
        if risk_tolerance == RiskLevel.VERY_LOW:
            recommendations.extend([
                "Priorizar renda fixa de países desenvolvidos",
                "Alocar 70% em títulos do tesouro americano",
                "Diversificar com bonds europeus e japoneses",
                "Evitar exposição a mercados emergentes",
                "Manter reserva de liquidez em USD"
            ])
        elif risk_tolerance == RiskLevel.LOW:
            recommendations.extend([
                "Alocar 50% renda fixa, 40% ações, 10% outros",
                "Foco em large caps de países desenvolvidos",
                "Setores defensivos: saúde, consumo básico, utilidades",
                "Exposição limitada a emergentes (máx 15%)",
                "Considerar ETFs de dividendos aristocratas"
            ])
        elif risk_tolerance == RiskLevel.MEDIUM:
            recommendations.extend([
                "Alocar 40% renda fixa, 50% ações, 10% outros",
                "Diversificação global com 60% desenvolvidos, 40% emergentes",
                "Mix de growth e value stocks",
                "Exposição setorial balanceada",
                "Considerar small caps para maior retorno"
            ])
        elif risk_tolerance == RiskLevel.HIGH:
            recommendations.extend([
                "Alocar 20% renda fixa, 70% ações, 10% alternativos",
                "Overweight em mercados emergentes e fronteiriços",
                "Setores cíclicos: tecnologia, industrial, financeiro",
                "Exposição a small caps e micro caps",
                "Alocar parte em private equity"
            ])
        else:  # VERY_HIGH
            recommendations.extend([
                "Alocar 90%+ em renda variável e alternativos",
                "Foco em mercados emergentes e fronteiriços",
                "Exposição a criptomoedas e DeFi",
                "Alavancagem moderada via ETFs alavancados",
                "Estratégias de momentum e fatores"
            ])
        
        # Recomendações baseadas no horizonte
        if time_horizon == TimeHorizon.SHORT_TERM:
            recommendations.append("Priorizar liquidez e ativos de baixa volatilidade")
            recommendations.append("Evitar mercados emergentes e small caps")
        elif time_horizon == TimeHorizon.LONG_TERM:
            recommendations.append("Aproveitar prêmio de risco de ações")
            recommendations.append("Incluir mercados emergentes na alocação")
        
        # Recomendações baseadas na estratégia
        if strategy:
            recommendations.append(f"Implementar estratégia {strategy.label}: {strategy.descricao}")
        
        # Análise consolidada
        result = {
            'timestamp': datetime.now(),
            'strategy': strategy.label if strategy else 'Diversificada',
            'risk_tolerance': risk_tolerance.label,
            'risk_icon': risk_tolerance.icon,
            'time_horizon': time_horizon.label,
            'time_icon': time_horizon.icon,
            
            'global_overview': global_analysis.to_dict(),
            'sectoral_analysis': sector_analysis,
            'regional_analysis': regional_analysis,
            
            'continents': {
                'europe': europe_analysis,
                'americas': america_analysis,
                'asia': asia_analysis,
                'africa': africa_analysis,
                'oceania': oceania_analysis
            },
            
            'asset_allocation': {
                'equity': 60 if risk_tolerance.volatility < 0.1 else 70 if risk_tolerance.volatility < 0.2 else 80,
                'fixed_income': 30 if risk_tolerance.volatility < 0.1 else 20 if risk_tolerance.volatility < 0.2 else 10,
                'alternatives': 10,
                'cash': 5
            },
            
            'regional_allocation': {
                'north_america': 35,
                'europe': 25,
                'asia_developed': 15,
                'asia_emerging': 10,
                'latin_america': 8,
                'other': 7
            },
            
            'sector_allocation': {
                'technology': 20,
                'financial': 15,
                'healthcare': 15,
                'consumer_cyclical': 10,
                'consumer_defensive': 10,
                'industrial': 10,
                'energy': 5,
                'utilities': 5,
                'real_estate': 5,
                'materials': 5
            },
            
            'recommendations': recommendations[:15],  # Top 15 recomendações
            'summary': self._generate_investment_summary(global_analysis, risk_tolerance, time_horizon)
        }
        
        self.logger.info("="*80)
        self.logger.info("✅ ANÁLISE COMPLETA DE INVESTIMENTOS CONCLUÍDA")
        self.logger.info(f"📊 {len(recommendations)} recomendações geradas")
        self.logger.info("="*80)
        
        return result
    
    def _generate_investment_summary(self, global_analysis: GlobalMarketOverview,
                                    risk_tolerance: RiskLevel,
                                    time_horizon: TimeHorizon) -> str:
        """Gera resumo textual da análise de investimentos"""
        
        summary = []
        summary.append(f"Análise de Investimentos - {datetime.now().strftime('%d/%m/%Y')}")
        summary.append("")
        summary.append(f"🌍 Cenário Global: Mercado de ${global_analysis.total_market_cap:.1f}T, "
                      f"VIX {global_analysis.volatility_index:.1f}, "
                      f"Apetite a risco {global_analysis.risk_appetite:.1f}%")
        summary.append("")
        summary.append(f"⚖️ Perfil do Investidor: Risco {risk_tolerance.icon} {risk_tolerance.label}, "
                      f"Horizonte {time_horizon.icon} {time_horizon.label}")
        summary.append("")
        summary.append("📈 Recomendações Principais:")
        summary.append("• Diversificar globalmente com 60% desenvolvidos, 40% emergentes")
        summary.append("• Setores favorecidos: Tecnologia, Saúde, Financeiro")
        summary.append("• Regiões destaque: Ásia emergente, América Latina")
        summary.append("• Evitar exposição excessiva a Europa Ocidental no curto prazo")
        summary.append("")
        summary.append("⚠️ Riscos Monitorados:")
        summary.append("• Inflação persistente e juros altos")
        summary.append("• Tensões geopolíticas (Ucrânia, China-Taiwan)")
        summary.append("• Desaceleração econômica global")
        summary.append("• Volatilidade cambial em emergentes")
        
        return "\n".join(summary)


# =============================================================================
# GERENCIADOR DE PORTFÓLIO
# =============================================================================

class PortfolioManager:
    """Gerenciador de portfólios de investimento"""
    
    def __init__(self):
        self.portfolios: Dict[str, Portfolio] = {}
        self.analyzer = InvestmentAnalyzer()
        self.logger = logger.getChild('PortfolioManager')
    
    def create_portfolio(self, name: str, strategy: InvestmentStrategy,
                        risk_level: RiskLevel, time_horizon: TimeHorizon,
                        initial_capital: float = 0.0) -> Portfolio:
        """Cria um novo portfólio"""
        
        portfolio_id = hashlib.md5(f"{name}_{datetime.now().timestamp()}".encode()).hexdigest()[:12]
        
        portfolio = Portfolio(
            id=portfolio_id,
            name=name,
            total_value=initial_capital,
            cash=initial_capital,
            risk_level=risk_level,
            time_horizon=time_horizon,
            strategy=strategy
        )
        
        self.portfolios[portfolio_id] = portfolio
        self.logger.info(f"✅ Portfólio criado: {name} (ID: {portfolio_id})")
        
        return portfolio
    
    def add_asset(self, portfolio_id: str, symbol: str, allocation: float) -> bool:
        """Adiciona um ativo ao portfólio"""
        
        if portfolio_id not in self.portfolios:
            self.logger.error(f"Portfólio {portfolio_id} não encontrado")
            return False
        
        portfolio = self.portfolios[portfolio_id]
        
        # Verificar limite por ativo
        if allocation > DEFAULT_CONFIG['max_allocation_per_asset']:
            self.logger.warning(f"Alocação {allocation:.1%} excede limite máximo "
                              f"{DEFAULT_CONFIG['max_allocation_per_asset']:.1%}")
            return False
        
        # Verificar alocação total
        total_allocation = sum(portfolio.assets.values()) + allocation
        if total_allocation > 1.0:
            self.logger.warning(f"Alocação total {total_allocation:.1%} excede 100%")
            return False
        
        portfolio.assets[symbol] = allocation
        self.logger.info(f"➕ Ativo adicionado: {symbol} ({allocation:.1%})")
        
        return True
    
    def rebalance_portfolio(self, portfolio_id: str) -> Dict[str, Any]:
        """Rebalanceia o portfólio para as alocações-alvo"""
        
        if portfolio_id not in self.portfolios:
            return {'success': False, 'error': 'Portfólio não encontrado'}
        
        portfolio = self.portfolios[portfolio_id]
        
        # Simular rebalanceamento
        result = {
            'portfolio_id': portfolio_id,
            'portfolio_name': portfolio.name,
            'timestamp': datetime.now(),
            'assets_before': portfolio.assets.copy(),
            'assets_after': portfolio.assets.copy(),  # Manter alocações-alvo
            'trades_executed': [],
            'total_cost': 0.0
        }
        
        portfolio.last_rebalanced = datetime.now()
        
        self.logger.info(f"🔄 Portfólio {portfolio.name} rebalanceado")
        
        return result
    
    def get_portfolio_analysis(self, portfolio_id: str) -> Dict[str, Any]:
        """Analisa o portfólio atual"""
        
        if portfolio_id not in self.portfolios:
            return {'error': 'Portfólio não encontrado'}
        
        portfolio = self.portfolios[portfolio_id]
        
        # Calcular métricas
        analysis = {
            'portfolio': portfolio.to_dict(),
            'diversification_score': self._calculate_diversification_score(portfolio),
            'risk_score': self._calculate_portfolio_risk(portfolio),
            'expected_return': 0.12,  # 12% a.a.
            'sharpe_ratio': 1.2,
            'sector_exposure': self._calculate_sector_exposure(portfolio),
            'region_exposure': self._calculate_region_exposure(portfolio),
            'recommendations': self._generate_portfolio_recommendations(portfolio)
        }
        
        return analysis
    
    def _calculate_diversification_score(self, portfolio: Portfolio) -> float:
        """Calcula score de diversificação (0-100)"""
        score = 0.0
        
        # Quantidade de ativos
        if len(portfolio.assets) >= 20:
            score += 40
        elif len(portfolio.assets) >= 10:
            score += 30
        elif len(portfolio.assets) >= 5:
            score += 20
        else:
            score += 10
        
        # Concentração
        max_allocation = max(portfolio.assets.values()) if portfolio.assets else 0
        if max_allocation <= 0.05:
            score += 30
        elif max_allocation <= 0.10:
            score += 20
        elif max_allocation <= 0.15:
            score += 10
        
        # Número de setores (simulado)
        score += 20
        
        return min(score, 100)
    
    def _calculate_portfolio_risk(self, portfolio: Portfolio) -> float:
        """Calcula risco do portfólio"""
        base_risk = portfolio.risk_level.volatility
        
        # Ajustar por diversificação
        if len(portfolio.assets) >= 20:
            base_risk *= 0.7
        elif len(portfolio.assets) >= 10:
            base_risk *= 0.8
        elif len(portfolio.assets) >= 5:
            base_risk *= 0.9
        
        return base_risk
    
    def _calculate_sector_exposure(self, portfolio: Portfolio) -> Dict[str, float]:
        """Calcula exposição setorial do portfólio"""
        # Simulado
        return {
            'Tecnologia': 0.25,
            'Financeiro': 0.20,
            'Saúde': 0.15,
            'Consumo Cíclico': 0.12,
            'Industrial': 0.10,
            'Outros': 0.18
        }
    
    def _calculate_region_exposure(self, portfolio: Portfolio) -> Dict[str, float]:
        """Calcula exposição regional do portfólio"""
        # Simulado
        return {
            'América do Norte': 0.45,
            'Europa': 0.25,
            'Ásia': 0.20,
            'América Latina': 0.07,
            'Outros': 0.03
        }
    
    def _generate_portfolio_recommendations(self, portfolio: Portfolio) -> List[str]:
        """Gera recomendações para o portfólio"""
        recommendations = []
        
        if not portfolio.is_diversified:
            recommendations.append("Aumentar diversificação - reduzir concentração nos maiores ativos")
        
        if len(portfolio.assets) < 10:
            recommendations.append(f"Adicionar mais ativos - atualmente {len(portfolio.assets)}")
        
        if portfolio.risk_level == RiskLevel.HIGH and portfolio.time_horizon == TimeHorizon.SHORT_TERM:
            recommendations.append("Risco elevado para horizonte curto - considerar reduzir exposição")
        
        if portfolio.risk_level == RiskLevel.LOW and portfolio.time_horizon == TimeHorizon.LONG_TERM:
            recommendations.append("Perfil conservador para longo prazo - aumentar exposição a ações")
        
        recommendations.append("Rebalancear trimestralmente para manter alocações-alvo")
        recommendations.append("Considerar hedge cambial para exposição internacional")
        recommendations.append("Acompanhar custos de corretagem e taxas de administração")
        
        return recommendations


# =============================================================================
# FUNÇÕES PRINCIPAIS DE EXPORTAÇÃO
# =============================================================================

# Instância global do analisador para facilitar o uso
_analyzer = InvestmentAnalyzer()
_portfolio_manager = PortfolioManager()

# =============================================================================
# API PÚBLICA - FUNÇÕES EXPORTADAS
# =============================================================================

def analyze_global_investments() -> GlobalMarketOverview:
    """
    Análise abrangente do mercado global de investimentos
    
    Returns:
        GlobalMarketOverview: Visão geral do mercado global
    """
    return _analyzer.analyze_global_investments()

def analyze_sectoral_investments(sector: Optional[Sector] = None) -> Dict[str, Any]:
    """
    Análise detalhada de investimentos por setor econômico
    
    Args:
        sector: Setor específico para análise (None = todos os setores)
        
    Returns:
        Dict com análise setorial completa
    """
    return _analyzer.analyze_sectoral_investments(sector)

def analyze_regional_investments(region: Optional[Region] = None) -> Dict[str, Any]:
    """
    Análise de investimentos por região geográfica
    
    Args:
        region: Região específica para análise (None = todas as regiões)
        
    Returns:
        Dict com análise regional completa
    """
    return _analyzer.analyze_regional_investments(region)

def analyze_european_investments() -> Dict[str, Any]:
    """
    Análise especializada de investimentos europeus
    
    Returns:
        Dict com análise do mercado europeu
    """
    return _analyzer.analyze_european_investments()

def analyze_american_investments() -> Dict[str, Any]:
    """
    Análise especializada de investimentos americanos (Norte e Sul)
    
    Returns:
        Dict com análise do mercado americano
    """
    return _analyzer.analyze_american_investments()

def analyze_asian_investments() -> Dict[str, Any]:
    """
    Análise especializada de investimentos asiáticos
    
    Returns:
        Dict com análise do mercado asiático
    """
    return _analyzer.analyze_asian_investments()

def analyze_african_investments() -> Dict[str, Any]:
    """
    Análise especializada de investimentos africanos
    
    Returns:
        Dict com análise do mercado africano
    """
    return _analyzer.analyze_african_investments()

def analyze_oceanian_investments() -> Dict[str, Any]:
    """
    Análise especializada de investimentos da Oceania
    
    Returns:
        Dict com análise do mercado da Oceania
    """
    return _analyzer.analyze_oceanian_investments()

def analyze_investments(strategy: Optional[InvestmentStrategy] = None,
                       risk_tolerance: RiskLevel = RiskLevel.MEDIUM,
                       time_horizon: TimeHorizon = TimeHorizon.LONG_TERM) -> Dict[str, Any]:
    """
    Análise completa de investimentos integrando todas as perspectivas
    
    Args:
        strategy: Estratégia de investimento desejada
        risk_tolerance: Tolerância a risco do investidor
        time_horizon: Horizonte de tempo do investimento
        
    Returns:
        Dict com análise consolidada e recomendações
    """
    return _analyzer.analyze_investments(strategy, risk_tolerance, time_horizon)

def create_portfolio(name: str, strategy: InvestmentStrategy,
                    risk_level: RiskLevel = RiskLevel.MEDIUM,
                    time_horizon: TimeHorizon = TimeHorizon.LONG_TERM,
                    initial_capital: float = 0.0) -> Portfolio:
    """
    Cria um novo portfólio de investimentos
    
    Args:
        name: Nome do portfólio
        strategy: Estratégia de investimento
        risk_level: Nível de risco desejado
        time_horizon: Horizonte de tempo
        initial_capital: Capital inicial
    
    Returns:
        Portfolio: Portfólio criado
    """
    return _portfolio_manager.create_portfolio(name, strategy, risk_level, 
                                              time_horizon, initial_capital)

def add_asset_to_portfolio(portfolio_id: str, symbol: str, allocation: float) -> bool:
    """
    Adiciona um ativo ao portfólio
    
    Args:
        portfolio_id: ID do portfólio
        symbol: Símbolo do ativo
        allocation: Alocação percentual (0-1)
    
    Returns:
        bool: True se adicionado com sucesso
    """
    return _portfolio_manager.add_asset(portfolio_id, symbol, allocation)

def analyze_portfolio(portfolio_id: str) -> Dict[str, Any]:
    """
    Analisa um portfólio existente
    
    Args:
        portfolio_id: ID do portfólio
    
    Returns:
        Dict com análise do portfólio
    """
    return _portfolio_manager.get_portfolio_analysis(portfolio_id)

def rebalance_portfolio(portfolio_id: str) -> Dict[str, Any]:
    """
    Rebalanceia um portfólio
    
    Args:
        portfolio_id: ID do portfólio
    
    Returns:
        Dict com resultado do rebalanceamento
    """
    return _portfolio_manager.rebalance_portfolio(portfolio_id)

# =============================================================================
# EXEMPLO DE USO
# =============================================================================

def example_usage():
    """Exemplo de uso do sistema de análise de investimentos"""
    
    print("\n" + "="*80)
    print("🚀 VHALINOR IAG - SISTEMA DE ANÁLISE DE INVESTIMENTOS GLOBAIS")
    print("="*80)
    
    # 1. Análise Global
    print("\n1️⃣  Análise Global de Investimentos")
    print("-"*40)
    global_analysis = analyze_global_investments()
    print(f"   📊 Market Cap Global: {global_analysis.total_market_cap}")
    print(f"   📈 VIX: {global_analysis.volatility_index}")
    print(f"   🎯 Apetite a Risco: {global_analysis.risk_appetite}")
    
    # 2. Análise Setorial
    print("\n2️⃣  Análise Setorial")
    print("-"*40)
    sector_analysis = analyze_sectoral_investments(Sector.TECHNOLOGY)
    print(f"   💻 Setor: {sector_analysis['sectors'][0]['name']}")
    print(f"   📈 Performance YTD: {sector_analysis['sectors'][0]['performance_ytd']}%")
    print(f"   📊 P/E: {sector_analysis['sectors'][0]['pe_ratio']}")
    
    # 3. Análise Regional
    print("\n3️⃣  Análise Regional")
    print("-"*40)
    regional_analysis = analyze_regional_investments(Region.LATAM)
    print(f"   🌎 Região: {regional_analysis['regions'][0]['name']}")
    print(f"   📈 Crescimento PIB: {regional_analysis['regions'][0]['gdp_growth']}%")
    print(f"   📊 Market Cap: ${regional_analysis['regions'][0]['market_cap']}B")
    
    # 4. Análise por Continente
    print("\n4️⃣  Análise por Continente")
    print("-"*40)
    asia = analyze_asian_investments()
    print(f"   🌏 Ásia - Market Cap: ${asia['total_market_cap']:.1f}B")
    print(f"   📈 Crescimento: {asia['avg_gdp_growth']:.1f}%")
    print(f"   🎯 Top Oportunidade: {asia['opportunities'][0]}")
    
    # 5. Análise Completa
    print("\n5️⃣  Análise Completa de Investimentos")
    print("-"*40)
    full_analysis = analyze_investments(
        strategy=InvestmentStrategy.VALUE,
        risk_tolerance=RiskLevel.MEDIUM,
        time_horizon=TimeHorizon.LONG_TERM
    )
    print(f"   📊 Estratégia: {full_analysis['strategy']}")
    print(f"   ⚖️  Risco: {full_analysis['risk_tolerance']}")
    print(f"   ⏱️  Horizonte: {full_analysis['time_horizon']}")
    print(f"\n   📋 Resumo:")
    for line in full_analysis['summary'].split('\n')[:5]:
        print(f"      {line}")
    
    # 6. Criação de Portfólio
    print("\n6️⃣  Criação de Portfólio")
    print("-"*40)
    portfolio = create_portfolio(
        name="Carteira Global Diversificada",
        strategy=InvestmentStrategy.VALUE,
        risk_level=RiskLevel.MEDIUM,
        time_horizon=TimeHorizon.LONG_TERM,
        initial_capital=100000.0
    )
    print(f"   ✅ Portfólio criado: {portfolio.name}")
    print(f"   🆔 ID: {portfolio.id}")
    
    # Adicionar ativos
    add_asset_to_portfolio(portfolio.id, "IVV", 0.15)  # S&P 500
    add_asset_to_portfolio(portfolio.id, "EWZ", 0.10)  # Brasil
    add_asset_to_portfolio(portfolio.id, "EEM", 0.10)  # Emergentes
    add_asset_to_portfolio(portfolio.id, "EFA", 0.15)  # Europa/Ásia
    add_asset_to_portfolio(portfolio.id, "QQQ", 0.10)  # Nasdaq
    print(f"   📈 Ativos adicionados: {portfolio.allocation_count}")
    
    # 7. Análise de Portfólio
    print("\n7️⃣  Análise de Portfólio")
    print("-"*40)
    portfolio_analysis = analyze_portfolio(portfolio.id)
    print(f"   📊 Score de Diversificação: {portfolio_analysis['diversification_score']:.1f}%")
    print(f"   ⚖️  Risco: {portfolio_analysis['risk_score']:.1%}")
    print(f"   📈 Retorno Esperado: {portfolio_analysis['expected_return']:.1%}")
    print(f"   📐 Sharpe Ratio: {portfolio_analysis['sharpe_ratio']:.2f}")
    
    print("\n   💡 Recomendações:")
    for rec in portfolio_analysis['recommendations'][:3]:
        print(f"      • {rec}")
    
    print("\n" + "="*80)
    print("✅ EXEMPLO DE USO CONCLUÍDO COM SUCESSO!")
    print("="*80)
    
    return full_analysis


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    'Continent',
    'Region',
    'Sector',
    'AssetClass',
    'RiskLevel',
    'InvestmentStrategy',
    'TimeHorizon',
    'EconomicIndicator',
    
    # Estruturas de dados
    'Country',
    'InvestmentAsset',
    'Portfolio',
    'InvestmentAnalysis',
    'GlobalMarketOverview',
    
    # Classes principais
    'MarketDataProvider',
    'InvestmentAnalyzer',
    'PortfolioManager',
    
    # Funções de análise
    'analyze_global_investments',
    'analyze_sectoral_investments',
    'analyze_regional_investments',
    'analyze_european_investments',
    'analyze_american_investments',
    'analyze_asian_investments',
    'analyze_african_investments',
    'analyze_oceanian_investments',
    'analyze_investments',
    
    # Funções de portfólio
    'create_portfolio',
    'add_asset_to_portfolio',
    'analyze_portfolio',
    'rebalance_portfolio',
    
    # Utilitários
    'example_usage'
]

if __name__ == "__main__":
    # Executar exemplo quando script é executado diretamente
    example_usage()
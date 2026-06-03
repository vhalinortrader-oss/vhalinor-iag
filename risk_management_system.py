"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                MODELO DE GERENCIAMENTO DE RISCO INTEGRADO                     ║
║                 Componente 7: Sistema de Controle de Risco Financeiro            ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import asyncio
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import warnings
import json
import pickle
from collections import deque, defaultdict
import time

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('RiskManagementSystem')

class RiskType(Enum):
    """Tipos de risco"""
    MARKET_RISK = "market_risk"
    CREDIT_RISK = "credit_risk"
    OPERATIONAL_RISK = "operational_risk"
    LIQUIDITY_RISK = "liquidity_risk"
    COUNTERPARTY_RISK = "counterparty_risk"
    MODEL_RISK = "model_risk"
    CONCENTRATION_RISK = "concentration_risk"
    REGULATORY_RISK = "regulatory_risk"

class RiskLevel(Enum):
    """Níveis de risco"""
    LOW = (1, "Baixo", "🟢", 0.02)
    MEDIUM = (2, "Médio", "🟡", 0.05)
    HIGH = (3, "Alto", "🟠", 0.10)
    CRITICAL = (4, "Crítico", "🔴", 0.20)
    EXTREME = (5, "Extremo", "⚫", 0.50)
    
    def __init__(self, level: int, label: str, icon: str, max_exposure: float):
        self.level = level
        self.label = label
        self.icon = icon
        self.max_exposure = max_exposure

class RiskMeasure(Enum):
    """Medidas de risco"""
    VAR = "value_at_risk"
    CVAR = "conditional_var"
    EXPECTED_SHORTFALL = "expected_shortfall"
    MAXIMUM_DRAWDOWN = "maximum_drawdown"
    VOLATILITY = "volatility"
    BETA = "beta"
    CORRELATION = "correlation"
    CONCENTRATION = "concentration"
    LIQUIDITY_GAP = "liquidity_gap"

@dataclass
class RiskMetrics:
    """Métricas de risco"""
    symbol: str
    timestamp: datetime
    risk_type: RiskType
    measure: RiskMeasure
    value: float
    confidence_level: float
    time_horizon: int  # dias
    currency: str = "USD"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'symbol': self.symbol,
            'timestamp': self.timestamp.isoformat(),
            'risk_type': self.risk_type.value,
            'measure': self.measure.value,
            'value': self.value,
            'confidence_level': self.confidence_level,
            'time_horizon': self.time_horizon,
            'currency': self.currency,
            'metadata': self.metadata
        }

@dataclass
class PositionRisk:
    """Risco de uma posição específica"""
    symbol: str
    position_type: str  # long, short, flat
    position_size: float
    current_price: float
    market_value: float
    unrealized_pnl: float
    daily_var: float
    weekly_var: float
    monthly_var: float
    beta: float
    volatility: float
    concentration_risk: float
    liquidity_risk: float
    total_risk_score: float
    risk_level: RiskLevel
    stop_loss_price: Optional[float] = None
    take_profit_price: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'symbol': self.symbol,
            'position_type': self.position_type,
            'position_size': self.position_size,
            'current_price': self.current_price,
            'market_value': self.market_value,
            'unrealized_pnl': self.unrealized_pnl,
            'daily_var': self.daily_var,
            'weekly_var': self.weekly_var,
            'monthly_var': self.monthly_var,
            'beta': self.beta,
            'volatility': self.volatility,
            'concentration_risk': self.concentration_risk,
            'liquidity_risk': self.liquidity_risk,
            'total_risk_score': self.total_risk_score,
            'risk_level': self.risk_level.label,
            'stop_loss_price': self.stop_loss_price,
            'take_profit_price': self.take_profit_price
        }

@dataclass
class PortfolioRisk:
    """Risco do portfólio"""
    total_value: float
    cash_balance: float
    total_exposure: float
    net_exposure: float
    leverage: float
    portfolio_var: float
    portfolio_cvar: float
    max_drawdown: float
    sharpe_ratio: float
    sortino_ratio: float
    beta_portfolio: float
    tracking_error: float
    concentration_risk: float
    liquidity_risk: float
    sector_exposure: Dict[str, float]
    geographic_exposure: Dict[str, float]
    currency_exposure: Dict[str, float]
    risk_level: RiskLevel
    risk_budget_utilization: float
    stress_test_results: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'total_value': self.total_value,
            'cash_balance': self.cash_balance,
            'total_exposure': self.total_exposure,
            'net_exposure': self.net_exposure,
            'leverage': self.leverage,
            'portfolio_var': self.portfolio_var,
            'portfolio_cvar': self.portfolio_cvar,
            'max_drawdown': self.max_drawdown,
            'sharpe_ratio': self.sharpe_ratio,
            'sortino_ratio': self.sortino_ratio,
            'beta_portfolio': self.beta_portfolio,
            'tracking_error': self.tracking_error,
            'concentration_risk': self.concentration_risk,
            'liquidity_risk': self.liquidity_risk,
            'sector_exposure': self.sector_exposure,
            'geographic_exposure': self.geographic_exposure,
            'currency_exposure': self.currency_exposure,
            'risk_level': self.risk_level.label,
            'risk_budget_utilization': self.risk_budget_utilization,
            'stress_test_results': self.stress_test_results
        }

@dataclass
class RiskLimit:
    """Limite de risco"""
    name: str
    risk_type: RiskType
    measure: RiskMeasure
    limit_value: float
    current_value: float
    utilization_rate: float
    warning_threshold: float = 0.8
    critical_threshold: float = 0.95
    is_breached: bool = False
    breach_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'risk_type': self.risk_type.value,
            'measure': self.measure.value,
            'limit_value': self.limit_value,
            'current_value': self.current_value,
            'utilization_rate': self.utilization_rate,
            'warning_threshold': self.warning_threshold,
            'critical_threshold': self.critical_threshold,
            'is_breached': self.is_breached,
            'breach_time': self.breach_time.isoformat() if self.breach_time else None
        }

class ValueAtRiskCalculator:
    """Calculadora de Value at Risk (VaR)"""
    
    def __init__(self):
        self.methods = ['historical', 'parametric', 'monte_carlo']
        logger.info("📊 Calculadora VaR inicializada")
    
    def calculate_var(self, returns: pd.Series, confidence_level: float = 0.95, 
                    time_horizon: int = 1, method: str = 'historical') -> float:
        """Calcula VaR usando diferentes métodos"""
        if len(returns) == 0:
            return 0.0
        
        if method == 'historical':
            return self._historical_var(returns, confidence_level, time_horizon)
        elif method == 'parametric':
            return self._parametric_var(returns, confidence_level, time_horizon)
        elif method == 'monte_carlo':
            return self._monte_carlo_var(returns, confidence_level, time_horizon)
        else:
            raise ValueError(f"Método VaR não suportado: {method}")
    
    def _historical_var(self, returns: pd.Series, confidence_level: float, 
                       time_horizon: int) -> float:
        """VaR histórico"""
        # Ajusta para o horizonte de tempo
        scaled_returns = returns * np.sqrt(time_horizon)
        
        # Calcula quantil
        var = -np.percentile(scaled_returns.dropna(), (1 - confidence_level) * 100)
        
        return var
    
    def _parametric_var(self, returns: pd.Series, confidence_level: float, 
                       time_horizon: int) -> float:
        """VaR paramétrico (normal)"""
        mean_return = returns.mean()
        std_return = returns.std()
        
        # Ajusta para o horizonte de tempo
        scaled_mean = mean_return * time_horizon
        scaled_std = std_return * np.sqrt(time_horizon)
        
        # Calcula VaR usando distribuição normal
        z_score = stats.norm.ppf(1 - confidence_level)
        var = -(scaled_mean + z_score * scaled_std)
        
        return var
    
    def _monte_carlo_var(self, returns: pd.Series, confidence_level: float, 
                         time_horizon: int, n_simulations: int = 10000) -> float:
        """VaR Monte Carlo"""
        mean_return = returns.mean()
        std_return = returns.std()
        
        # Simula retornos
        simulated_returns = np.random.normal(
            mean_return * time_horizon,
            std_return * np.sqrt(time_horizon),
            n_simulations
        )
        
        # Calcula VaR
        var = -np.percentile(simulated_returns, (1 - confidence_level) * 100)
        
        return var
    
    def calculate_cvar(self, returns: pd.Series, confidence_level: float = 0.95,
                      time_horizon: int = 1, method: str = 'historical') -> float:
        """Calcula Conditional VaR (Expected Shortfall)"""
        if len(returns) == 0:
            return 0.0
        
        # Calcula VaR primeiro
        var = self.calculate_var(returns, confidence_level, time_horizon, method)
        
        # Ajusta retornos para o horizonte
        scaled_returns = returns * np.sqrt(time_horizon)
        
        # CVAR é a média dos retornos que excedem o VaR
        tail_losses = scaled_returns[scaled_returns <= -var]
        
        if len(tail_losses) == 0:
            return var
        
        cvar = -tail_losses.mean()
        
        return cvar

class ConcentrationRiskCalculator:
    """Calculadora de risco de concentração"""
    
    def __init__(self):
        logger.info("🎯 Calculadora de concentração inicializada")
    
    def calculate_hhi(self, weights: pd.Series) -> float:
        """Calcula Índice Herfindahl-Hirschman"""
        # Normaliza pesos
        normalized_weights = weights / weights.sum()
        
        # Calcula HHI
        hhi = (normalized_weights ** 2).sum()
        
        return hhi
    
    def calculate_concentration_ratio(self, weights: pd.Series, n: int = 5) -> float:
        """Calcula razão de concentração dos top n"""
        # Normaliza pesos
        normalized_weights = weights / weights.sum()
        
        # Soma dos top n pesos
        top_n_sum = normalized_weights.nlargest(n).sum()
        
        return top_n_sum
    
    def calculate_shannon_entropy(self, weights: pd.Series) -> float:
        """Calcula entropia de Shannon"""
        # Normaliza pesos e remove zeros
        normalized_weights = weights / weights.sum()
        normalized_weights = normalized_weights[normalized_weights > 0]
        
        # Calcula entropia
        entropy = -np.sum(normalized_weights * np.log(normalized_weights))
        
        return entropy
    
    def calculate_diversification_ratio(self, cov_matrix: pd.DataFrame, 
                                     weights: pd.Series) -> float:
        """Calcula razão de diversificação"""
        # Pesos normalizados
        normalized_weights = weights / weights.sum()
        
        # Volatilidade ponderada
        weighted_vol = np.sqrt(np.sum(normalized_weights ** 2 * np.diag(cov_matrix)))
        
        # Volatilidade do portfólio
        portfolio_vol = np.sqrt(
            np.dot(normalized_weights.T, np.dot(cov_matrix, normalized_weights))
        )
        
        # Razão de diversificação
        if portfolio_vol == 0:
            return 1.0
        
        div_ratio = weighted_vol / portfolio_vol
        
        return div_ratio

class LiquidityRiskCalculator:
    """Calculadora de risco de liquidez"""
    
    def __init__(self):
        logger.info("💧 Calculadora de liquidez inicializada")
    
    def calculate_liquidity_gap(self, cash_flows: pd.Series, 
                              time_horizon: int = 30) -> Dict[str, float]:
        """Calcula gap de liquidez"""
        # Acumula cash flows no horizonte
        cumulative_flows = cash_flows.head(time_horizon).cumsum()
        
        # Calcula métricas
        min_balance = cumulative_flows.min()
        max_gap = abs(cumulative_flows.min())
        avg_gap = cumulative_flows.mean()
        
        return {
            'min_balance': min_balance,
            'max_gap': max_gap,
            'avg_gap': avg_gap,
            'time_horizon': time_horizon
        }
    
    def calculate_liquidity_coverage_ratio(self, liquid_assets: float, 
                                        net_cash_outflows: float) -> float:
        """Calcula LCR (Liquidity Coverage Ratio)"""
        if net_cash_outflows == 0:
            return float('inf')
        
        lcr = liquid_assets / net_cash_outflows
        
        return lcr
    
    def calculate_market_impact(self, order_size: float, avg_daily_volume: float,
                             price_impact_factor: float = 0.1) -> float:
        """Calcula impacto de mercado"""
        if avg_daily_volume == 0:
            return 0.0
        
        # Percentagem do volume diário
        volume_pct = order_size / avg_daily_volume
        
        # Impacto de preço (modelo quadrático)
        price_impact = price_impact_factor * (volume_pct ** 2)
        
        return price_impact

class StressTestEngine:
    """Motor de testes de estresse"""
    
    def __init__(self):
        self.scenarios = self._initialize_scenarios()
        logger.info("🔥 Motor de stress test inicializado")
    
    def _initialize_scenarios(self) -> Dict[str, Dict[str, Any]]:
        """Inicializa cenários de estresse"""
        return {
            'market_crash': {
                'market_shock': -0.30,
                'volatility_increase': 2.0,
                'correlation_increase': 0.5,
                'liquidity_decrease': 0.5
            },
            'interest_rate_shock': {
                'rate_change': 0.02,
                'curve_flattening': 0.1,
                'spread_widening': 0.005
            },
            'currency_crisis': {
                'fx_shock': -0.20,
                'inflation_spike': 0.05,
                'capital_flight': 0.3
            },
            'sector_rotations': {
                'tech_decline': -0.15,
                'energy_rise': 0.10,
                'volatility_shift': 1.5
            },
            'liquidity_crisis': {
                'bid_ask_widening': 3.0,
                'volume_reduction': 0.3,
                'market_depth_reduction': 0.5
            }
        }
    
    def run_stress_test(self, portfolio_data: Dict[str, Any], 
                       scenario_name: str) -> Dict[str, float]:
        """Executa teste de estresse para um cenário"""
        if scenario_name not in self.scenarios:
            raise ValueError(f"Cenário não encontrado: {scenario_name}")
        
        scenario = self.scenarios[scenario_name]
        results = {}
        
        # Aplica choques de mercado
        if 'market_shock' in scenario:
            market_impact = self._apply_market_shock(
                portfolio_data, scenario['market_shock']
            )
            results['market_shock_impact'] = market_impact
        
        # Aplica aumento de volatilidade
        if 'volatility_increase' in scenario:
            volatility_impact = self._apply_volatility_shock(
                portfolio_data, scenario['volatility_increase']
            )
            results['volatility_impact'] = volatility_impact
        
        # Aplica choque de liquidez
        if 'liquidity_decrease' in scenario:
            liquidity_impact = self._apply_liquidity_shock(
                portfolio_data, scenario['liquidity_decrease']
            )
            results['liquidity_impact'] = liquidity_impact
        
        # Calcula impacto total
        total_impact = sum(results.values())
        results['total_impact'] = total_impact
        
        return results
    
    def _apply_market_shock(self, portfolio_data: Dict[str, Any], 
                           shock: float) -> float:
        """Aplica choque de mercado"""
        total_value = portfolio_data.get('total_value', 0)
        beta = portfolio_data.get('beta', 1.0)
        
        # Impacto = beta * shock * portfolio_value
        impact = beta * shock * total_value
        
        return impact
    
    def _apply_volatility_shock(self, portfolio_data: Dict[str, Any], 
                              shock_factor: float) -> float:
        """Aplica choque de volatilidade"""
        current_vol = portfolio_data.get('volatility', 0.15)
        var_95 = portfolio_data.get('var_95', 0)
        
        # Nova volatilidade
        new_vol = current_vol * shock_factor
        
        # Novo VaR (aproximado)
        new_var = var_95 * shock_factor
        
        # Impacto = aumento no VaR
        impact = new_var - var_95
        
        return impact
    
    def _apply_liquidity_shock(self, portfolio_data: Dict[str, Any], 
                              shock_factor: float) -> float:
        """Aplica choque de liquidez"""
        position_size = portfolio_data.get('position_size', 0)
        avg_daily_volume = portfolio_data.get('avg_daily_volume', 1)
        
        # Novo impacto de mercado
        current_impact = self._calculate_market_impact(
            position_size, avg_daily_volume
        )
        
        # Impacto aumentado pelo choque
        new_impact = current_impact * shock_factor
        
        return new_impact - current_impact
    
    def _calculate_market_impact(self, order_size: float, 
                              avg_daily_volume: float) -> float:
        """Calcula impacto de mercado"""
        if avg_daily_volume == 0:
            return 0.0
        
        volume_pct = order_size / avg_daily_volume
        impact = 0.1 * (volume_pct ** 2)
        
        return impact

class RiskManagementSystem:
    """Sistema integrado de gerenciamento de risco"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Componentes
        self.var_calculator = ValueAtRiskCalculator()
        self.concentration_calculator = ConcentrationRiskCalculator()
        self.liquidity_calculator = LiquidityRiskCalculator()
        self.stress_test_engine = StressTestEngine()
        
        # Limites de risco
        self.risk_limits = {}
        
        # Histórico de métricas
        self.risk_history = defaultdict(list)
        
        # Alertas
        self.risk_alerts = []
        
        # Configurações padrão
        self.max_leverage = self.config.get('max_leverage', 2.0)
        self.max_position_size = self.config.get('max_position_size', 0.1)
        self.max_var_daily = self.config.get('max_var_daily', 0.02)
        self.max_concentration = self.config.get('max_concentration', 0.3)
        self.min_liquidity_ratio = self.config.get('min_liquidity_ratio', 1.0)
        
        logger.info("🛡️ Sistema de Gerenciamento de Risco inicializado")
    
    def assess_position_risk(self, position_data: Dict[str, Any], 
                           historical_data: pd.DataFrame) -> PositionRisk:
        """Avalia risco de uma posição"""
        symbol = position_data.get('symbol', 'UNKNOWN')
        position_type = position_data.get('position_type', 'long')
        position_size = position_data.get('position_size', 0)
        current_price = position_data.get('current_price', 0)
        
        # Calcula valor de mercado
        market_value = position_size * current_price
        
        # Obtém retornos históricos
        if 'close_price' in historical_data.columns:
            returns = historical_data['close_price'].pct_change().dropna()
        else:
            returns = pd.Series()
        
        # Calcula métricas de risco
        daily_var = self.var_calculator.calculate_var(
            returns, 0.95, 1, 'historical'
        ) if len(returns) > 0 else 0
        
        weekly_var = self.var_calculator.calculate_var(
            returns, 0.95, 7, 'historical'
        ) if len(returns) > 0 else 0
        
        monthly_var = self.var_calculator.calculate_var(
            returns, 0.95, 30, 'historical'
        ) if len(returns) > 0 else 0
        
        # Beta (simplificado)
        beta = position_data.get('beta', 1.0)
        
        # Volatilidade
        volatility = returns.std() * np.sqrt(252) if len(returns) > 0 else 0.15
        
        # Risco de concentração
        concentration_risk = min(position_size / self.max_position_size, 1.0)
        
        # Risco de liquidez
        avg_volume = position_data.get('avg_daily_volume', 1)
        liquidity_risk = self.liquidity_calculator.calculate_market_impact(
            position_size, avg_volume
        )
        
        # PnL não realizado
        entry_price = position_data.get('entry_price', current_price)
        if position_type == 'long':
            unrealized_pnl = (current_price - entry_price) * position_size
        else:
            unrealized_pnl = (entry_price - current_price) * position_size
        
        # Calcula score de risco total
        risk_scores = [
            concentration_risk * 0.3,
            liquidity_risk * 0.2,
            abs(beta - 1) * 0.1,
            volatility * 0.2,
            abs(daily_var) * 0.2
        ]
        
        total_risk_score = sum(risk_scores)
        
        # Determina nível de risco
        if total_risk_score < 0.1:
            risk_level = RiskLevel.LOW
        elif total_risk_score < 0.3:
            risk_level = RiskLevel.MEDIUM
        elif total_risk_score < 0.5:
            risk_level = RiskLevel.HIGH
        elif total_risk_score < 0.8:
            risk_level = RiskLevel.CRITICAL
        else:
            risk_level = RiskLevel.EXTREME
        
        # Calcula stop loss e take profit
        stop_loss_pct = 0.02  # 2%
        take_profit_pct = 0.05  # 5%
        
        if position_type == 'long':
            stop_loss_price = current_price * (1 - stop_loss_pct)
            take_profit_price = current_price * (1 + take_profit_pct)
        else:
            stop_loss_price = current_price * (1 + stop_loss_pct)
            take_profit_price = current_price * (1 - take_profit_pct)
        
        return PositionRisk(
            symbol=symbol,
            position_type=position_type,
            position_size=position_size,
            current_price=current_price,
            market_value=market_value,
            unrealized_pnl=unrealized_pnl,
            daily_var=daily_var,
            weekly_var=weekly_var,
            monthly_var=monthly_var,
            beta=beta,
            volatility=volatility,
            concentration_risk=concentration_risk,
            liquidity_risk=liquidity_risk,
            total_risk_score=total_risk_score,
            risk_level=risk_level,
            stop_loss_price=stop_loss_price,
            take_profit_price=take_profit_price
        )
    
    def assess_portfolio_risk(self, portfolio_data: Dict[str, Any], 
                            positions: List[PositionRisk]) -> PortfolioRisk:
        """Avalia risco do portfólio"""
        total_value = portfolio_data.get('total_value', 0)
        cash_balance = portfolio_data.get('cash_balance', 0)
        
        # Calcula exposições
        long_exposure = sum([p.market_value for p in positions 
                           if p.position_type == 'long'])
        short_exposure = sum([abs(p.market_value) for p in positions 
                            if p.position_type == 'short'])
        total_exposure = long_exposure + short_exposure
        net_exposure = long_exposure - short_exposure
        
        # Alavancagem
        leverage = total_exposure / max(total_value, 1)
        
        # VaR do portfólio (simplificado - assume correlação 1)
        portfolio_var = sum([abs(p.daily_var) for p in positions])
        
        # CVaR do portfólio
        portfolio_cvar = sum([abs(p.daily_var) * 1.2 for p in positions])  # Aproximação
        
        # Maximum drawdown
        max_drawdown = portfolio_data.get('max_drawdown', 0)
        
        # Sharpe ratio
        sharpe_ratio = portfolio_data.get('sharpe_ratio', 0)
        
        # Sortino ratio
        sortino_ratio = portfolio_data.get('sortino_ratio', 0)
        
        # Beta do portfólio
        beta_portfolio = portfolio_data.get('beta_portfolio', 1.0)
        
        # Tracking error
        tracking_error = portfolio_data.get('tracking_error', 0)
        
        # Risco de concentração
        position_weights = pd.Series({p.symbol: abs(p.market_value) 
                                   for p in positions})
        concentration_risk = self.concentration_calculator.calculate_hhi(
            position_weights
        )
        
        # Risco de liquidez
        liquidity_risk = sum([p.liquidity_risk for p in positions]) / len(positions)
        
        # Exposições por setor (simplificado)
        sector_exposure = portfolio_data.get('sector_exposure', {})
        
        # Exposições geográficas (simplificado)
        geographic_exposure = portfolio_data.get('geographic_exposure', {})
        
        # Exposições por moeda (simplificado)
        currency_exposure = portfolio_data.get('currency_exposure', {})
        
        # Utilização do budget de risco
        risk_budget_utilization = portfolio_var / self.max_var_daily
        
        # Determina nível de risco
        risk_factors = [
            leverage / self.max_leverage,
            concentration_risk,
            liquidity_risk,
            risk_budget_utilization
        ]
        
        avg_risk_factor = np.mean(risk_factors)
        
        if avg_risk_factor < 0.3:
            risk_level = RiskLevel.LOW
        elif avg_risk_factor < 0.5:
            risk_level = RiskLevel.MEDIUM
        elif avg_risk_factor < 0.7:
            risk_level = RiskLevel.HIGH
        elif avg_risk_factor < 0.9:
            risk_level = RiskLevel.CRITICAL
        else:
            risk_level = RiskLevel.EXTREME
        
        # Executa stress tests
        stress_test_results = {}
        for scenario_name in ['market_crash', 'liquidity_crisis']:
            try:
                stress_result = self.stress_test_engine.run_stress_test(
                    portfolio_data, scenario_name
                )
                stress_test_results[scenario_name] = stress_result['total_impact']
            except Exception as e:
                logger.warning(f"Erro no stress test {scenario_name}: {e}")
                stress_test_results[scenario_name] = 0
        
        return PortfolioRisk(
            total_value=total_value,
            cash_balance=cash_balance,
            total_exposure=total_exposure,
            net_exposure=net_exposure,
            leverage=leverage,
            portfolio_var=portfolio_var,
            portfolio_cvar=portfolio_cvar,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            beta_portfolio=beta_portfolio,
            tracking_error=tracking_error,
            concentration_risk=concentration_risk,
            liquidity_risk=liquidity_risk,
            sector_exposure=sector_exposure,
            geographic_exposure=geographic_exposure,
            currency_exposure=currency_exposure,
            risk_level=risk_level,
            risk_budget_utilization=risk_budget_utilization,
            stress_test_results=stress_test_results
        )
    
    def check_risk_limits(self, portfolio_risk: PortfolioRisk, 
                         positions: List[PositionRisk]) -> List[RiskLimit]:
        """Verifica limites de risco"""
        limits = []
        
        # Limite de alavancagem
        leverage_limit = RiskLimit(
            name="Alavancagem Máxima",
            risk_type=RiskType.MARKET_RISK,
            measure=RiskMeasure.CONCENTRATION,
            limit_value=self.max_leverage,
            current_value=portfolio_risk.leverage,
            utilization_rate=portfolio_risk.leverage / self.max_leverage
        )
        limits.append(leverage_limit)
        
        # Limite de VaR diário
        var_limit = RiskLimit(
            name="VaR Diário Máximo",
            risk_type=RiskType.MARKET_RISK,
            measure=RiskMeasure.VAR,
            limit_value=self.max_var_daily,
            current_value=portfolio_risk.portfolio_var,
            utilization_rate=portfolio_risk.portfolio_var / self.max_var_daily
        )
        limits.append(var_limit)
        
        # Limite de concentração
        concentration_limit = RiskLimit(
            name="Concentração Máxima",
            risk_type=RiskType.CONCENTRATION_RISK,
            measure=RiskMeasure.CONCENTRATION,
            limit_value=self.max_concentration,
            current_value=portfolio_risk.concentration_risk,
            utilization_rate=portfolio_risk.concentration_risk / self.max_concentration
        )
        limits.append(concentration_limit)
        
        # Verifica posições individuais
        for position in positions:
            if position.total_risk_score > 0.8:
                position_limit = RiskLimit(
                    name=f"Risco da Posição {position.symbol}",
                    risk_type=RiskType.MARKET_RISK,
                    measure=RiskMeasure.VOLATILITY,
                    limit_value=0.8,
                    current_value=position.total_risk_score,
                    utilization_rate=position.total_risk_score / 0.8
                )
                limits.append(position_limit)
        
        # Atualiza status de breach
        for limit in limits:
            if limit.utilization_rate >= limit.critical_threshold:
                limit.is_breached = True
                limit.breach_time = datetime.now()
                self.risk_alerts.append({
                    'timestamp': limit.breach_time,
                    'limit': limit.name,
                    'utilization': limit.utilization_rate,
                    'severity': 'CRITICAL'
                })
            elif limit.utilization_rate >= limit.warning_threshold:
                self.risk_alerts.append({
                    'timestamp': datetime.now(),
                    'limit': limit.name,
                    'utilization': limit.utilization_rate,
                    'severity': 'WARNING'
                })
        
        return limits
    
    def generate_risk_report(self, portfolio_risk: PortfolioRisk, 
                           positions: List[PositionRisk], 
                           limits: List[RiskLimit]) -> Dict[str, Any]:
        """Gera relatório de risco completo"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'portfolio_risk': portfolio_risk.to_dict(),
            'position_risks': [p.to_dict() for p in positions],
            'risk_limits': [l.to_dict() for l in limits],
            'risk_alerts': self.risk_alerts[-10:],  # Últimos 10 alertas
            'summary': {
                'total_positions': len(positions),
                'breached_limits': len([l for l in limits if l.is_breached]),
                'warning_limits': len([l for l in limits 
                                     if l.utilization_rate >= l.warning_threshold]),
                'overall_risk_level': portfolio_risk.risk_level.label,
                'recommendations': self._generate_recommendations(
                    portfolio_risk, positions, limits
                )
            }
        }
        
        return report
    
    def _generate_recommendations(self, portfolio_risk: PortfolioRisk, 
                                 positions: List[PositionRisk], 
                                 limits: List[RiskLimit]) -> List[str]:
        """Gera recomendações baseadas no risco"""
        recommendations = []
        
        # Recomendações de alavancagem
        if portfolio_risk.leverage > self.max_leverage * 0.8:
            recommendations.append(
                f"Reduzir alavancagem de {portfolio_risk.leverage:.2f}x "
                f"para abaixo de {self.max_leverage:.2f}x"
            )
        
        # Recomendações de concentração
        if portfolio_risk.concentration_risk > self.max_concentration * 0.8:
            recommendations.append(
                "Diversificar portfólio para reduzir concentração"
            )
        
        # Recomendações de VaR
        if portfolio_risk.portfolio_var > self.max_var_daily * 0.8:
            recommendations.append(
                "Reduzir tamanho das posições para controlar VaR"
            )
        
        # Recomendações de posições individuais
        high_risk_positions = [p for p in positions if p.risk_level.level >= 3]
        if high_risk_positions:
            recommendations.append(
                f"Revisar posições de alto risco: "
                f"{', '.join([p.symbol for p in high_risk_positions])}"
            )
        
        # Recomendações de liquidez
        if portfolio_risk.liquidity_risk > 0.5:
            recommendations.append(
                "Aumentar posições em ativos líquidos"
            )
        
        # Recomendações de stop loss
        positions_without_sl = [p for p in positions if p.stop_loss_price is None]
        if positions_without_sl:
            recommendations.append(
                "Implementar stop losses para todas as posições"
            )
        
        return recommendations
    
    def save_risk_data(self, filepath: str):
        """Salva dados de risco"""
        risk_data = {
            'config': self.config,
            'risk_history': dict(self.risk_history),
            'risk_alerts': self.risk_alerts,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(filepath, 'w') as f:
            json.dump(risk_data, f, indent=2, default=str)
        
        logger.info(f"Dados de risco salvos em {filepath}")
    
    def load_risk_data(self, filepath: str):
        """Carrega dados de risco"""
        try:
            with open(filepath, 'r') as f:
                risk_data = json.load(f)
            
            self.config = risk_data.get('config', {})
            self.risk_history = defaultdict(list, risk_data.get('risk_history', {}))
            self.risk_alerts = risk_data.get('risk_alerts', [])
            
            logger.info(f"Dados de risco carregados de {filepath}")
            
        except Exception as e:
            logger.error(f"Erro ao carregar dados de risco: {e}")

# Configuração padrão
DEFAULT_RISK_CONFIG = {
    'max_leverage': 2.0,
    'max_position_size': 0.1,
    'max_var_daily': 0.02,
    'max_concentration': 0.3,
    'min_liquidity_ratio': 1.0,
    'stress_test_scenarios': ['market_crash', 'liquidity_crisis'],
    'risk_monitoring_freq': 300,  # segundos
    'alert_thresholds': {
        'var_warning': 0.8,
        'var_critical': 0.95,
        'leverage_warning': 0.8,
        'leverage_critical': 0.95
    }
}

if __name__ == "__main__":
    # Exemplo de uso
    def create_sample_portfolio():
        """Cria portfólio de exemplo"""
        return {
            'total_value': 1000000,
            'cash_balance': 100000,
            'max_drawdown': 0.15,
            'sharpe_ratio': 1.2,
            'sortino_ratio': 1.5,
            'beta_portfolio': 1.1,
            'tracking_error': 0.08,
            'sector_exposure': {
                'Technology': 0.4,
                'Finance': 0.3,
                'Healthcare': 0.2,
                'Energy': 0.1
            },
            'geographic_exposure': {
                'US': 0.6,
                'Europe': 0.3,
                'Asia': 0.1
            },
            'currency_exposure': {
                'USD': 0.7,
                'EUR': 0.2,
                'JPY': 0.1
            }
        }
    
    def create_sample_positions():
        """Cria posições de exemplo"""
        positions_data = [
            {
                'symbol': 'AAPL',
                'position_type': 'long',
                'position_size': 1000,
                'current_price': 150.0,
                'entry_price': 145.0,
                'beta': 1.2,
                'avg_daily_volume': 50000000
            },
            {
                'symbol': 'MSFT',
                'position_type': 'long',
                'position_size': 500,
                'current_price': 300.0,
                'entry_price': 290.0,
                'beta': 0.9,
                'avg_daily_volume': 30000000
            },
            {
                'symbol': 'GOOGL',
                'position_type': 'short',
                'position_size': 200,
                'current_price': 2500.0,
                'entry_price': 2550.0,
                'beta': 1.1,
                'avg_daily_volume': 1000000
            }
        ]
        
        return positions_data
    
    def create_historical_data():
        """Cria dados históricos de exemplo"""
        dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='D')
        np.random.seed(42)
        
        # Simula preços
        prices = {}
        for symbol in ['AAPL', 'MSFT', 'GOOGL']:
            returns = np.random.normal(0.0005, 0.02, len(dates))
            base_price = {'AAPL': 150, 'MSFT': 300, 'GOOGL': 2500}[symbol]
            prices[symbol] = base_price * np.exp(np.cumsum(returns))
        
        # Cria DataFrame
        data = pd.DataFrame(index=dates)
        for symbol, price_series in prices.items():
            data[symbol] = price_series
        
        return data
    
    def test_risk_system():
        """Testa o sistema de risco"""
        # Cria sistema
        risk_system = RiskManagementSystem(DEFAULT_RISK_CONFIG)
        
        # Cria dados de exemplo
        portfolio_data = create_sample_portfolio()
        positions_data = create_sample_positions()
        historical_data = create_historical_data()
        
        # Avalia risco das posições
        positions_risk = []
        for pos_data in positions_data:
            symbol_data = historical_data[pos_data['symbol']].to_frame('close_price')
            position_risk = risk_system.assess_position_risk(pos_data, symbol_data)
            positions_risk.append(position_risk)
            
            print(f"\n📊 Risco da Posição {position_risk.symbol}:")
            print(f"Tipo: {position_risk.position_type}")
            print(f"Valor: ${position_risk.market_value:,.2f}")
            print(f"PnL: ${position_risk.unrealized_pnl:,.2f}")
            print(f"VaR Diário: {position_risk.daily_var:.2%}")
            print(f"Score Risco: {position_risk.total_risk_score:.3f}")
            print(f"Nível: {position_risk.risk_level.label}")
        
        # Avalia risco do portfólio
        portfolio_risk = risk_system.assess_portfolio_risk(
            portfolio_data, positions_risk
        )
        
        print(f"\n🎯 Risco do Portfólio:")
        print(f"Valor Total: ${portfolio_risk.total_value:,.2f}")
        print(f"Alavancagem: {portfolio_risk.leverage:.2f}x")
        print(f"VaR Portfólio: {portfolio_risk.portfolio_var:.2%}")
        print(f"CVaR Portfólio: {portfolio_risk.portfolio_cvar:.2%}")
        print(f"Sharpe Ratio: {portfolio_risk.sharpe_ratio:.2f}")
        print(f"Risco Concentração: {portfolio_risk.concentration_risk:.3f}")
        print(f"Nível: {portfolio_risk.risk_level.label}")
        
        # Verifica limites
        limits = risk_system.check_risk_limits(portfolio_risk, positions_risk)
        
        print(f"\n⚠️ Limites de Risco:")
        for limit in limits:
            status = "🔴 BREACH" if limit.is_breached else "⚠️ WARNING" if limit.utilization_rate >= limit.warning_threshold else "✅ OK"
            print(f"{limit.name}: {limit.utilization_rate:.1%} {status}")
        
        # Gera relatório
        report = risk_system.generate_risk_report(
            portfolio_risk, positions_risk, limits
        )
        
        print(f"\n📋 Recomendações:")
        for rec in report['summary']['recommendations']:
            print(f"• {rec}")
        
        # Salva relatório
        with open('risk_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n💾 Relatório de risco salvo em risk_report.json")
        
        return risk_system, report
    
    # Executa teste
    risk_system, risk_report = test_risk_system()
    print("✅ Sistema de gerenciamento de risco testado com sucesso!")

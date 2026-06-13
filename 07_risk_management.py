# 07_risk_management.py
"""
Sistema VhalinorTrade - Gestão de Risco Avançada
Stop-loss dinâmico, diversificação e proteção de capital
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from scipy.stats import norm

@dataclass
class PositionRisk:
    symbol: str
    position_size: float
    entry_price: float
    current_price: float
    stop_loss: float
    take_profit: float
    risk_amount: float
    risk_percentage: float
    unrealized_pnl: float
    var_95: float
    max_adverse_excursion: float

class RiskManager:
    def __init__(self, config):
        self.config = config
        self.positions = {}
        self.risk_metrics = {}
        self.reserve_fund = 0
        self.total_capital = 0
        
    def calculate_position_size(self, capital: float,
                               entry_price: float,
                               stop_loss_price: float,
                               max_risk_pct: float = None) -> float:
        """Calcula tamanho ideal da posição baseado no risco"""
        if max_risk_pct is None:
            max_risk_pct = self.config.trading.max_exposure_per_trade
            
        max_loss_amount = capital * max_risk_pct
        price_risk = abs(entry_price - stop_loss_price)
        
        if price_risk == 0:
            return 0
            
        position_size = max_loss_amount / (price_risk / entry_price)
        
        # Aplica limites
        max_position = capital * self.config.trading.max_total_exposure
        position_size = min(position_size, max_position)
        
        return position_size
    
    def calculate_dynamic_stop_loss(self, df: pd.DataFrame,
                                   entry_price: float,
                                   atr_multiplier: float = 2.0) -> float:
        """Calcula stop-loss dinâmico baseado em ATR e suportes"""
        # ATR-based stop
        atr = self.technical_analyzer.calculate_atr(
            df['high'], df['low'], df['close']
        )
        atr_stop = entry_price - atr.iloc[-1] * atr_multiplier
        
        # Suporte mais próximo
        supports, _ = self.technical_analyzer.detect_support_resistance(df)
        nearest_support = None
        
        for support in sorted(supports, reverse=True):
            if support < entry_price:
                nearest_support = support
                break
                
        if nearest_support:
            # Usa o mais conservador
            stop_loss = max(atr_stop, nearest_support * 0.995)
        else:
            stop_loss = atr_stop
            
        return stop_loss
    
    def calculate_dynamic_take_profit(self, entry_price: float,
                                     stop_loss: float,
                                     risk_reward_ratio: float = 2.0) -> Dict[str, float]:
        """Calcula múltiplos níveis de take-profit"""
        risk = entry_price - stop_loss
        
        return {
            'tp1': entry_price + risk * 1.5,  # 1.5:1 RR
            'tp2': entry_price + risk * 2.0,  # 2:1 RR
            'tp3': entry_price + risk * 3.0,  # 3:1 RR
        }
    
    def calculate_var(self, returns: np.ndarray,
                     confidence_level: float = 0.95) -> float:
        """Calcula Value at Risk (VaR)"""
        var = np.percentile(returns, (1 - confidence_level) * 100)
        return var
    
    def calculate_cvar(self, returns: np.ndarray,
                      confidence_level: float = 0.95) -> float:
        """Calcula Conditional Value at Risk (CVaR)"""
        var = self.calculate_var(returns, confidence_level)
        cvar = returns[returns <= var].mean()
        return cvar
    
    def calculate_correlation_matrix(self, 
                                    returns_dict: Dict[str, np.ndarray]
                                    ) -> pd.DataFrame:
        """Calcula matriz de correlação entre ativos"""
        returns_df = pd.DataFrame(returns_dict)
        return returns_df.corr()
    
    def optimize_diversification(self, available_capital: float,
                                correlations: pd.DataFrame,
                                predictions: Dict[str, float],
                                max_assets: int = 5) -> Dict[str, float]:
        """Otimiza alocação de capital com diversificação"""
        n_assets = len(predictions)
        if n_assets == 0:
            return {}
            
        assets = list(predictions.keys())
        
        # Otimização simples: weight = prediction / (1 + avg_correlation)
        weights = {}
        remaining_capital = available_capital
        
        # Ordena por predição
        sorted_assets = sorted(assets, 
                             key=lambda x: predictions[x],
                             reverse=True)[:max_assets]
        
        for asset in sorted_assets:
            if asset in correlations.index:
                avg_corr = correlations[asset].mean()
                diversification_factor = 1 / (1 + avg_corr * 3)
                
                weight = predictions[asset] * diversification_factor
                weights[asset] = max(0, weight)
                
        # Normaliza pesos
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {k: v/total_weight for k, v in weights.items()}
            
        return weights
    
    def update_reserve_fund(self, profit: float):
        """Atualiza fundo de reserva com parte dos lucros"""
        reserve_contribution = profit * self.config.trading.reinvestment_rate
        self.reserve_fund += reserve_contribution
        
        # Se reserva excede 30% do capital total, redistribui
        if self.total_capital > 0:
            max_reserve = self.total_capital * 0.3
            if self.reserve_fund > max_reserve:
                excess = self.reserve_fund - max_reserve
                self.reserve_fund = max_reserve
                return excess  # Retorna para reinvestimento
                
        return 0
    
    def calculate_exposure_limits(self) -> Dict[str, float]:
        """Calcula limites de exposição atuais"""
        total_exposure = sum(
            pos['size'] * pos['current_price'] 
            for pos in self.positions.values()
        )
        
        return {
            'total_exposure': total_exposure,
            'max_allowed': self.total_capital * self.config.trading.max_total_exposure,
            'remaining': max(0, self.total_capital * self.config.trading.max_total_exposure - total_exposure),
            'utilization': total_exposure / self.total_capital if self.total_capital > 0 else 0
        }
    
    def emergency_stop(self, market_conditions: Dict) -> bool:
        """Para todas as operações em caso de condições extremas"""
        triggers = [
            market_conditions.get('flash_crash', False),
            market_conditions.get('extreme_volatility', False),
            market_conditions.get('total_drawdown', 0) > self.config.risk.max_drawdown,
            market_conditions.get('correlation_spike', False)
        ]
        
        return any(triggers)
    
    def calculate_kelly_criterion(self, win_rate: float,
                                 avg_win: float,
                                 avg_loss: float) -> float:
        """Calcula critério de Kelly para dimensionamento de posição"""
        if avg_loss == 0:
            return 0
            
        kelly = (win_rate * avg_win - (1 - win_rate) * abs(avg_loss)) / (avg_win * abs(avg_loss))
        
        # Kelly fraction (mais conservador)
        return max(0, min(kelly * 0.5, 0.25))  # Máximo 25% do capital
    
    def monte_carlo_simulation(self, returns: np.ndarray,
                              num_simulations: int = 10000,
                              horizon: int = 30) -> Dict[str, float]:
        """Simulação de Monte Carlo para análise de risco"""
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        
        simulations = np.zeros((num_simulations, horizon))
        
        for i in range(num_simulations):
            random_returns = np.random.normal(mean_return, std_return, horizon)
            simulations[i] = np.cumprod(1 + random_returns)
            
        final_values = simulations[:, -1]
        
        return {
            'expected_return': np.mean(final_values) - 1,
            'var_95': np.percentile(final_values, 5) - 1,
            'var_99': np.percentile(final_values, 1) - 1,
            'cvar_95': np.mean(final_values[final_values <= np.percentile(final_values, 5)]) - 1,
            'best_case': np.max(final_values) - 1,
            'worst_case': np.min(final_values) - 1,
            'probability_of_loss': np.sum(final_values < 1) / num_simulations
        }
"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                AMBIENTE DE APRENDIZADO POR REFORÇO (RL)                          ║
║                 Componente 5: Environment para Trading Financeiro                   ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import asyncio
import numpy as np
import pandas as pd
import gym
from gym import spaces
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import json
import pickle
from collections import deque, defaultdict
import random

# Import dos módulos anteriores
from market_data_infrastructure import MarketDataPoint, DataFrequency
from financial_feature_engineering import FeatureSet

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ReinforcementLearningEnvironment')

class ActionType(Enum):
    """Tipos de ações de trading"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    CLOSE_LONG = "close_long"
    CLOSE_SHORT = "close_short"
    OPEN_LONG = "open_long"
    OPEN_SHORT = "open_short"

class PositionType(Enum):
    """Tipos de posição"""
    FLAT = "flat"
    LONG = "long"
    SHORT = "short"

class MarketRegime(Enum):
    """Regimes de mercado"""
    BULL = "bull"
    BEAR = "bear"
    SIDEWAYS = "sideways"
    VOLATILE = "volatile"
    TRENDING = "trending"
    MEAN_REVERTING = "mean_reverting"

@dataclass
class TradingState:
    """Estado de trading"""
    symbol: str
    timestamp: datetime
    current_price: float
    portfolio_value: float
    cash_balance: float
    position_type: PositionType
    position_size: float
    unrealized_pnl: float
    realized_pnl: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    max_drawdown: float
    sharpe_ratio: float
    volatility: float
    market_regime: MarketRegime
    features: Dict[str, float] = field(default_factory=dict)
    technical_indicators: Dict[str, float] = field(default_factory=dict)
    risk_metrics: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'symbol': self.symbol,
            'timestamp': self.timestamp.isoformat(),
            'current_price': self.current_price,
            'portfolio_value': self.portfolio_value,
            'cash_balance': self.cash_balance,
            'position_type': self.position_type.value,
            'position_size': self.position_size,
            'unrealized_pnl': self.unrealized_pnl,
            'realized_pnl': self.realized_pnl,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'max_drawdown': self.max_drawdown,
            'sharpe_ratio': self.sharpe_ratio,
            'volatility': self.volatility,
            'market_regime': self.market_regime.value,
            'features': self.features,
            'technical_indicators': self.technical_indicators,
            'risk_metrics': self.risk_metrics
        }

@dataclass
class TradingAction:
    """Ação de trading"""
    action_type: ActionType
    symbol: str
    timestamp: datetime
    price: Optional[float] = None
    quantity: Optional[float] = None
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'action_type': self.action_type.value,
            'symbol': self.symbol,
            'timestamp': self.timestamp.isoformat(),
            'price': self.price,
            'quantity': self.quantity,
            'confidence': self.confidence,
            'metadata': self.metadata
        }

@dataclass
class RewardComponents:
    """Componentes da função de recompensa"""
    return_component: float = 0.0
    risk_adjusted_return: float = 0.0
    sharpe_component: float = 0.0
    drawdown_penalty: float = 0.0
    transaction_cost: float = 0.0
    position_penalty: float = 0.0
    volatility_penalty: float = 0.0
    regime_bonus: float = 0.0
    total_reward: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'return_component': self.return_component,
            'risk_adjusted_return': self.risk_adjusted_return,
            'sharpe_component': self.sharpe_component,
            'drawdown_penalty': self.drawdown_penalty,
            'transaction_cost': self.transaction_cost,
            'position_penalty': self.position_penalty,
            'volatility_penalty': self.volatility_penalty,
            'regime_bonus': self.regime_bonus,
            'total_reward': self.total_reward
        }

@dataclass
class EnvironmentConfig:
    """Configuração do ambiente"""
    initial_balance: float = 100000.0
    transaction_cost_pct: float = 0.001
    slippage_pct: float = 0.0005
    max_position_size: float = 1.0
    leverage: float = 1.0
    lookback_window: int = 60
    reward_function: str = "sharpe_adjusted"
    risk_free_rate: float = 0.02
    max_drawdown_limit: float = 0.2
    volatility_window: int = 20
    regime_detection_window: int = 50
    position_holding_period_min: int = 1
    position_holding_period_max: int = 100
    enable_short_selling: bool = True
    enable_leverage: bool = False
    normalize_features: bool = True
    include_technical_indicators: bool = True
    include_market_regime: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'initial_balance': self.initial_balance,
            'transaction_cost_pct': self.transaction_cost_pct,
            'slippage_pct': self.slippage_pct,
            'max_position_size': self.max_position_size,
            'leverage': self.leverage,
            'lookback_window': self.lookback_window,
            'reward_function': self.reward_function,
            'risk_free_rate': self.risk_free_rate,
            'max_drawdown_limit': self.max_drawdown_limit,
            'volatility_window': self.volatility_window,
            'regime_detection_window': self.regime_detection_window,
            'position_holding_period_min': self.position_holding_period_min,
            'position_holding_period_max': self.position_holding_period_max,
            'enable_short_selling': self.enable_short_selling,
            'enable_leverage': self.enable_leverage,
            'normalize_features': self.normalize_features,
            'include_technical_indicators': self.include_technical_indicators,
            'include_market_regime': self.include_market_regime
        }

class TradingEnvironment(gym.Env):
    """Ambiente de trading para aprendizado por reforço"""
    
    metadata = {'render.modes': ['human', 'system']}
    
    def __init__(self, config: EnvironmentConfig):
        super(TradingEnvironment, self).__init__()
        
        self.config = config
        self.data = None
        self.current_step = 0
        self.max_steps = 0
        
        # Estado do portfólio
        self.initial_balance = config.initial_balance
        self.cash_balance = config.initial_balance
        self.position_type = PositionType.FLAT
        self.position_size = 0.0
        self.position_entry_price = 0.0
        self.position_entry_time = 0
        
        # Histórico
        self.portfolio_history = []
        self.trade_history = []
        self.reward_history = []
        self.action_history = []
        
        # Métricas
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.max_portfolio_value = config.initial_balance
        self.current_drawdown = 0.0
        self.max_drawdown = 0.0
        
        # Espaços de ação e observação
        self._setup_spaces()
        
        # Detectores de regime
        self.market_regime = MarketRegime.SIDEWAYS
        
        logger.info("🎮 Ambiente de Trading RL inicializado")
    
    def _setup_spaces(self):
        """Configura espaços de ação e observação"""
        # Espaço de ação: 0=HOLD, 1=BUY, 2=SELL, 3=CLOSE
        self.action_space = spaces.Discrete(4)
        
        # Espaço de observação (será definido quando os dados forem carregados)
        self.observation_space = None
    
    def load_data(self, data: pd.DataFrame):
        """Carrega dados históricos"""
        self.data = data.copy()
        self.max_steps = len(data) - self.config.lookback_window - 1
        
        # Calcula features adicionais
        self._calculate_additional_features()
        
        # Define espaço de observação
        feature_columns = [col for col in self.data.columns if col.startswith('feature_')]
        technical_columns = [col for col in self.data.columns if col.startswith('indicator_')]
        
        observation_size = (
            self.config.lookback_window * len(feature_columns) +
            len(technical_columns) +
            10  # Estado do portfólio
        )
        
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(observation_size,),
            dtype=np.float32
        )
        
        logger.info(f"📊 Dados carregados: {len(data)} pontos, {observation_size} features")
    
    def _calculate_additional_features(self):
        """Calcula features adicionais para o ambiente"""
        if 'close_price' not in self.data.columns:
            return
        
        # Retornos
        self.data['return_1d'] = self.data['close_price'].pct_change()
        self.data['return_5d'] = self.data['close_price'].pct_change(5)
        self.data['return_20d'] = self.data['close_price'].pct_change(20)
        
        # Volatilidade
        self.data['volatility_20d'] = self.data['return_1d'].rolling(20).std() * np.sqrt(252)
        
        # Drawdown
        self.data['cummax'] = self.data['close_price'].cummax()
        self.data['drawdown'] = (self.data['close_price'] - self.data['cummax']) / self.data['cummax']
        
        # Regime de mercado (simplificado)
        self.data['regime'] = self._detect_market_regime()
        
        # Indicadores técnicos básicos
        self._calculate_basic_indicators()
    
    def _calculate_basic_indicators(self):
        """Calcula indicadores técnicos básicos"""
        close = self.data['close_price']
        
        # Médias móveis
        self.data['indicator_sma_20'] = close.rolling(20).mean()
        self.data['indicator_sma_50'] = close.rolling(50).mean()
        self.data['indicator_ema_20'] = close.ewm(span=20).mean()
        
        # RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        self.data['indicator_rsi'] = 100 - (100 / (1 + rs))
        
        # Bandas de Bollinger
        sma_20 = close.rolling(20).mean()
        std_20 = close.rolling(20).std()
        self.data['indicator_bb_upper'] = sma_20 + (std_20 * 2)
        self.data['indicator_bb_lower'] = sma_20 - (std_20 * 2)
        self.data['indicator_bb_middle'] = sma_20
        
        # MACD
        ema_12 = close.ewm(span=12).mean()
        ema_26 = close.ewm(span=26).mean()
        self.data['indicator_macd'] = ema_12 - ema_26
        self.data['indicator_macd_signal'] = self.data['indicator_macd'].ewm(span=9).mean()
        self.data['indicator_macd_hist'] = self.data['indicator_macd'] - self.data['indicator_macd_signal']
    
    def _detect_market_regime(self) -> pd.Series:
        """Detecta regime de mercado"""
        regime = pd.Series(index=self.data.index, data='sideways')
        
        for i in range(self.config.regime_detection_window, len(self.data)):
            window_data = self.data['close_price'].iloc[i-self.config.regime_detection_window:i]
            
            # Tendência
            if len(window_data) >= 20:
                trend_slope = np.polyfit(range(len(window_data)), window_data, 1)[0]
                
                if trend_slope > 0.1:
                    regime.iloc[i] = 'bull'
                elif trend_slope < -0.1:
                    regime.iloc[i] = 'bear'
                else:
                    # Volatilidade para distinguir sideways/volatile
                    volatility = window_data.pct_change().std()
                    if volatility > 0.03:
                        regime.iloc[i] = 'volatile'
                    else:
                        regime.iloc[i] = 'sideways'
        
        return regime
    
    def reset(self) -> np.ndarray:
        """Reseta o ambiente"""
        self.current_step = 0
        self.cash_balance = self.initial_balance
        self.position_type = PositionType.FLAT
        self.position_size = 0.0
        self.position_entry_price = 0.0
        self.position_entry_time = 0
        
        # Reseta métricas
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.max_portfolio_value = self.initial_balance
        self.current_drawdown = 0.0
        self.max_drawdown = 0.0
        
        # Limpa históricos
        self.portfolio_history = []
        self.trade_history = []
        self.reward_history = []
        self.action_history = []
        
        return self._get_observation()
    
    def step(self, action: int) -> Tuple[np.ndarray, float, bool, Dict[str, Any]]:
        """Executa um passo no ambiente"""
        if self.current_step >= self.max_steps:
            return self._get_observation(), 0, True, {}
        
        # Obtém estado atual
        current_state = self._get_current_state()
        
        # Executa ação
        reward, done, info = self._execute_action(action, current_state)
        
        # Atualiza passo
        self.current_step += 1
        
        # Verifica se episódio terminou
        if self.current_step >= self.max_steps:
            done = True
        
        # Obtém nova observação
        observation = self._get_observation()
        
        # Atualiza histórico
        self.portfolio_history.append(current_state.portfolio_value)
        self.reward_history.append(reward)
        
        return observation, reward, done, info
    
    def _execute_action(self, action: int, state: TradingState) -> Tuple[float, bool, Dict[str, Any]]:
        """Executa uma ação de trading"""
        reward_components = RewardComponents()
        info = {}
        
        # Mapeia ação para tipo
        action_map = {
            0: ActionType.HOLD,
            1: ActionType.BUY,
            2: ActionType.SELL,
            3: ActionType.CLOSE
        }
        
        action_type = action_map[action]
        
        # Executa ação baseada no tipo e posição atual
        if action_type == ActionType.HOLD:
            reward = self._calculate_hold_reward(state, reward_components)
        
        elif action_type == ActionType.BUY:
            if self.position_type == PositionType.FLAT:
                reward = self._execute_buy(state, reward_components)
            elif self.position_type == PositionType.SHORT:
                reward = self._execute_close_short(state, reward_components)
            else:
                reward = self._calculate_hold_reward(state, reward_components)
        
        elif action_type == ActionType.SELL:
            if self.position_type == PositionType.FLAT:
                if self.config.enable_short_selling:
                    reward = self._execute_sell_short(state, reward_components)
                else:
                    reward = self._calculate_hold_reward(state, reward_components)
            elif self.position_type == PositionType.LONG:
                reward = self._execute_close_long(state, reward_components)
            else:
                reward = self._calculate_hold_reward(state, reward_components)
        
        elif action_type == ActionType.CLOSE:
            if self.position_type == PositionType.LONG:
                reward = self._execute_close_long(state, reward_components)
            elif self.position_type == PositionType.SHORT:
                reward = self._execute_close_short(state, reward_components)
            else:
                reward = self._calculate_hold_reward(state, reward_components)
        
        # Atualiza métricas de risco
        self._update_risk_metrics()
        
        # Registra ação
        self.action_history.append(TradingAction(
            action_type=action_type,
            symbol=state.symbol,
            timestamp=state.timestamp,
            confidence=1.0
        ))
        
        info['reward_components'] = reward_components.to_dict()
        info['portfolio_value'] = state.portfolio_value
        info['position_type'] = self.position_type.value
        info['position_size'] = self.position_size
        
        return reward_components.total_reward, False, info
    
    def _execute_buy(self, state: TradingState, reward_components: RewardComponents) -> float:
        """Executa compra (abre posição long)"""
        # Calcula tamanho da posição
        available_cash = self.cash_balance * self.config.max_position_size
        price_with_slippage = state.current_price * (1 + self.config.slippage_pct)
        transaction_cost = available_cash * self.config.transaction_cost_pct
        
        if available_cash > transaction_cost:
            # Abre posição long
            self.position_type = PositionType.LONG
            self.position_size = (available_cash - transaction_cost) / price_with_slippage
            self.position_entry_price = price_with_slippage
            self.position_entry_time = self.current_step
            self.cash_balance -= available_cash
            
            # Custo de transação
            reward_components.transaction_cost = -transaction_cost / self.initial_balance
        
        return self._calculate_total_reward(state, reward_components)
    
    def _execute_sell_short(self, state: TradingState, reward_components: RewardComponents) -> float:
        """Executa venda a descoberto"""
        if not self.config.enable_short_selling:
            return self._calculate_hold_reward(state, reward_components)
        
        # Calcula tamanho da posição
        available_cash = self.cash_balance * self.config.max_position_size
        price_with_slippage = state.current_price * (1 - self.config.slippage_pct)
        transaction_cost = available_cash * self.config.transaction_cost_pct
        
        if available_cash > transaction_cost:
            # Abre posição short
            self.position_type = PositionType.SHORT
            self.position_size = (available_cash - transaction_cost) / price_with_slippage
            self.position_entry_price = price_with_slippage
            self.position_entry_time = self.current_step
            self.cash_balance -= available_cash
            
            # Custo de transação
            reward_components.transaction_cost = -transaction_cost / self.initial_balance
        
        return self._calculate_total_reward(state, reward_components)
    
    def _execute_close_long(self, state: TradingState, reward_components: RewardComponents) -> float:
        """Fecha posição long"""
        if self.position_type != PositionType.LONG:
            return self._calculate_hold_reward(state, reward_components)
        
        # Calcula PnL
        price_with_slippage = state.current_price * (1 - self.config.slippage_pct)
        transaction_cost = self.position_size * price_with_slippage * self.config.transaction_cost_pct
        
        gross_proceeds = self.position_size * price_with_slippage
        net_proceeds = gross_proceeds - transaction_cost
        
        # PnL da posição
        position_cost = self.position_size * self.position_entry_price
        pnl = net_proceeds - position_cost
        
        # Atualiza balanço
        self.cash_balance += net_proceeds
        
        # Atualiza estatísticas
        self.total_trades += 1
        if pnl > 0:
            self.winning_trades += 1
        else:
            self.losing_trades += 1
        
        # Registra trade
        self.trade_history.append({
            'type': 'long',
            'entry_price': self.position_entry_price,
            'exit_price': price_with_slippage,
            'size': self.position_size,
            'pnl': pnl,
            'entry_time': self.position_entry_time,
            'exit_time': self.current_step,
            'holding_period': self.current_step - self.position_entry_time
        })
        
        # Reseta posição
        self.position_type = PositionType.FLAT
        self.position_size = 0.0
        self.position_entry_price = 0.0
        self.position_entry_time = 0
        
        # Componentes de recompensa
        reward_components.return_component = pnl / self.initial_balance
        reward_components.transaction_cost = -transaction_cost / self.initial_balance
        
        return self._calculate_total_reward(state, reward_components)
    
    def _execute_close_short(self, state: TradingState, reward_components: RewardComponents) -> float:
        """Fecha posição short"""
        if self.position_type != PositionType.SHORT:
            return self._calculate_hold_reward(state, reward_components)
        
        # Calcula PnL
        price_with_slippage = state.current_price * (1 + self.config.slippage_pct)
        transaction_cost = self.position_size * price_with_slippage * self.config.transaction_cost_pct
        
        # Custo para cobrir posição short
        cover_cost = self.position_size * price_with_slippage
        total_cost = cover_cost + transaction_cost
        
        # PnL da posição
        position_proceeds = self.position_size * self.position_entry_price
        pnl = position_proceeds - total_cost
        
        # Atualiza balanço
        self.cash_balance += position_proceeds - total_cost
        
        # Atualiza estatísticas
        self.total_trades += 1
        if pnl > 0:
            self.winning_trades += 1
        else:
            self.losing_trades += 1
        
        # Registra trade
        self.trade_history.append({
            'type': 'short',
            'entry_price': self.position_entry_price,
            'exit_price': price_with_slippage,
            'size': self.position_size,
            'pnl': pnl,
            'entry_time': self.position_entry_time,
            'exit_time': self.current_step,
            'holding_period': self.current_step - self.position_entry_time
        })
        
        # Reseta posição
        self.position_type = PositionType.FLAT
        self.position_size = 0.0
        self.position_entry_price = 0.0
        self.position_entry_time = 0
        
        # Componentes de recompensa
        reward_components.return_component = pnl / self.initial_balance
        reward_components.transaction_cost = -transaction_cost / self.initial_balance
        
        return self._calculate_total_reward(state, reward_components)
    
    def _calculate_hold_reward(self, state: TradingState, reward_components: RewardComponents) -> float:
        """Calcula recompensa para ação HOLD"""
        # Recompensa baseada no retorno não realizado
        if self.position_type != PositionType.FLAT:
            if self.position_type == PositionType.LONG:
                unrealized_return = (state.current_price - self.position_entry_price) / self.position_entry_price
            else:  # SHORT
                unrealized_return = (self.position_entry_price - state.current_price) / self.position_entry_price
            
            reward_components.return_component = unrealized_return * self.position_size * self.config.max_position_size
        
        return self._calculate_total_reward(state, reward_components)
    
    def _calculate_total_reward(self, state: TradingState, reward_components: RewardComponents) -> float:
        """Calcula recompensa total baseada na configuração"""
        if self.config.reward_function == "simple_return":
            reward_components.total_reward = reward_components.return_component
        
        elif self.config.reward_function == "risk_adjusted":
            # Ajusta pela volatilidade
            if state.volatility > 0:
                risk_adjusted = reward_components.return_component / state.volatility
            else:
                risk_adjusted = reward_components.return_component
            reward_components.risk_adjusted_return = risk_adjusted
            reward_components.total_reward = risk_adjusted
        
        elif self.config.reward_function == "sharpe_adjusted":
            # Usa Sharpe ratio como base
            reward_components.sharpe_component = state.sharpe_ratio
            reward_components.total_reward = state.sharpe_ratio * 0.1  # Scale down
        
        elif self.config.reward_function == "composite":
            # Combina múltiplos componentes
            weights = {
                'return': 0.4,
                'risk_adjusted': 0.3,
                'sharpe': 0.2,
                'transaction_cost': 0.1
            }
            
            reward_components.total_reward = (
                weights['return'] * reward_components.return_component +
                weights['risk_adjusted'] * reward_components.risk_adjusted_return +
                weights['sharpe'] * reward_components.sharpe_component +
                weights['transaction_cost'] * reward_components.transaction_cost
            )
        
        # Penalidades
        if self.max_drawdown > self.config.max_drawdown_limit:
            reward_components.drawdown_penalty = -0.1
        
        # Bônus por regime
        if state.market_regime == MarketRegime.BULL and self.position_type == PositionType.LONG:
            reward_components.regime_bonus = 0.01
        elif state.market_regime == MarketRegime.BEAR and self.position_type == PositionType.SHORT:
            reward_components.regime_bonus = 0.01
        
        reward_components.total_reward += (
            reward_components.drawdown_penalty +
            reward_components.regime_bonus
        )
        
        return reward_components.total_reward
    
    def _get_current_state(self) -> TradingState:
        """Obtém estado atual de trading"""
        if self.current_step >= len(self.data):
            return None
        
        current_data = self.data.iloc[self.current_step + self.config.lookback_window]
        current_price = current_data['close_price']
        
        # Calcula valor do portfólio
        portfolio_value = self.cash_balance
        unrealized_pnl = 0.0
        
        if self.position_type == PositionType.LONG:
            unrealized_pnl = (current_price - self.position_entry_price) * self.position_size
            portfolio_value += self.position_size * current_price
        elif self.position_type == PositionType.SHORT:
            unrealized_pnl = (self.position_entry_price - current_price) * self.position_size
            portfolio_value += self.position_size * self.position_entry_price
        
        # Calcula métricas
        self._update_risk_metrics()
        
        # Detecta regime
        regime_str = current_data.get('regime', 'sideways')
        market_regime = MarketRegime(regime_str)
        
        # Extrai features
        features = {}
        technical_indicators = {}
        
        for col in self.data.columns:
            if col.startswith('feature_'):
                features[col] = current_data.get(col, 0.0)
            elif col.startswith('indicator_'):
                technical_indicators[col] = current_data.get(col, 0.0)
        
        return TradingState(
            symbol="DEFAULT",
            timestamp=current_data.get('timestamp', datetime.now()),
            current_price=current_price,
            portfolio_value=portfolio_value,
            cash_balance=self.cash_balance,
            position_type=self.position_type,
            position_size=self.position_size,
            unrealized_pnl=unrealized_pnl,
            realized_pnl=sum([t['pnl'] for t in self.trade_history]),
            total_trades=self.total_trades,
            winning_trades=self.winning_trades,
            losing_trades=self.losing_trades,
            max_drawdown=self.max_drawdown,
            sharpe_ratio=self._calculate_sharpe_ratio(),
            volatility=current_data.get('volatility_20d', 0.0),
            market_regime=market_regime,
            features=features,
            technical_indicators=technical_indicators,
            risk_metrics={
                'current_drawdown': self.current_drawdown,
                'var_95': self._calculate_var(),
                'position_concentration': self.position_size / self.initial_balance
            }
        )
    
    def _get_observation(self) -> np.ndarray:
        """Obtém observação atual"""
        if self.current_step >= len(self.data):
            return np.zeros(self.observation_space.shape[0])
        
        # Features temporais (lookback window)
        start_idx = self.current_step
        end_idx = self.current_step + self.config.lookback_window
        
        feature_columns = [col for col in self.data.columns if col.startswith('feature_')]
        temporal_features = []
        
        if feature_columns:
            window_data = self.data[feature_columns].iloc[start_idx:end_idx].values
            temporal_features = window_data.flatten()
        
        # Indicadores técnicos atuais
        current_data = self.data.iloc[end_idx]
        technical_columns = [col for col in self.data.columns if col.startswith('indicator_')]
        technical_features = [current_data.get(col, 0.0) for col in technical_columns]
        
        # Estado do portfólio
        portfolio_features = [
            self.cash_balance / self.initial_balance,
            self.position_size / self.initial_balance,
            1.0 if self.position_type == PositionType.LONG else 0.0,
            1.0 if self.position_type == PositionType.SHORT else 0.0,
            1.0 if self.position_type == PositionType.FLAT else 0.0,
            self.current_drawdown,
            self._calculate_sharpe_ratio(),
            len(self.trade_history) / 1000.0,  # Normalizado
            self.winning_trades / max(1, self.total_trades),  # Win rate
            self.current_step / self.max_steps  # Progresso do episódio
        ]
        
        # Concatena todas as features
        observation = np.concatenate([
            temporal_features,
            technical_features,
            portfolio_features
        ])
        
        return observation.astype(np.float32)
    
    def _update_risk_metrics(self):
        """Atualiza métricas de risco"""
        if len(self.portfolio_history) > 0:
            current_value = self.portfolio_history[-1]
            
            # Drawdown atual
            if current_value > self.max_portfolio_value:
                self.max_portfolio_value = current_value
            
            self.current_drawdown = (self.max_portfolio_value - current_value) / self.max_portfolio_value
            self.max_drawdown = max(self.max_drawdown, self.current_drawdown)
    
    def _calculate_sharpe_ratio(self, risk_free_rate: float = None) -> float:
        """Calcula Sharpe ratio"""
        if risk_free_rate is None:
            risk_free_rate = self.config.risk_free_rate
        
        if len(self.portfolio_history) < 2:
            return 0.0
        
        returns = np.diff(self.portfolio_history) / self.portfolio_history[:-1]
        
        if len(returns) == 0 or np.std(returns) == 0:
            return 0.0
        
        excess_returns = returns - risk_free_rate / 252  # Diário
        sharpe = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
        
        return sharpe
    
    def _calculate_var(self, confidence_level: float = 0.95) -> float:
        """Calcula Value at Risk"""
        if len(self.portfolio_history) < 30:
            return 0.0
        
        returns = np.diff(self.portfolio_history) / self.portfolio_history[:-1]
        var = np.percentile(returns, (1 - confidence_level) * 100)
        
        return var
    
    def render(self, mode: str = 'human'):
        """Renderiza o ambiente"""
        if mode == 'human':
            state = self._get_current_state()
            if state:
                print(f"\n=== Trading Environment State ===")
                print(f"Step: {self.current_step}/{self.max_steps}")
                print(f"Price: ${state.current_price:.2f}")
                print(f"Portfolio Value: ${state.portfolio_value:.2f}")
                print(f"Cash Balance: ${state.cash_balance:.2f}")
                print(f"Position: {state.position_type.value} ({state.position_size:.2f})")
                print(f"Unrealized PnL: ${state.unrealized_pnl:.2f}")
                print(f"Realized PnL: ${state.realized_pnl:.2f}")
                print(f"Total Trades: {state.total_trades}")
                print(f"Win Rate: {state.winning_trades/max(1, state.total_trades):.2%}")
                print(f"Max Drawdown: {state.max_drawdown:.2%}")
                print(f"Sharpe Ratio: {state.sharpe_ratio:.2f}")
                print(f"Market Regime: {state.market_regime.value}")
                print("=" * 35)
        
        elif mode == 'system':
            # Log para sistema
            state = self._get_current_state()
            if state:
                logger.info(f"Step {self.current_step}: "
                          f"Value=${state.portfolio_value:.2f}, "
                          f"Pos={state.position_type.value}, "
                          f"PnL=${state.unrealized_pnl:.2f}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Retorna métricas de performance"""
        if len(self.portfolio_history) == 0:
            return {}
        
        total_return = (self.portfolio_history[-1] - self.initial_balance) / self.initial_balance
        win_rate = self.winning_trades / max(1, self.total_trades)
        
        return {
            'total_return': total_return,
            'sharpe_ratio': self._calculate_sharpe_ratio(),
            'max_drawdown': self.max_drawdown,
            'total_trades': self.total_trades,
            'win_rate': win_rate,
            'avg_trade_pnl': np.mean([t['pnl'] for t in self.trade_history]) if self.trade_history else 0,
            'profit_factor': self._calculate_profit_factor(),
            'var_95': self._calculate_var(),
            'final_portfolio_value': self.portfolio_history[-1],
            'initial_balance': self.initial_balance
        }
    
    def _calculate_profit_factor(self) -> float:
        """Calcula profit factor"""
        if not self.trade_history:
            return 0.0
        
        gross_profits = sum([t['pnl'] for t in self.trade_history if t['pnl'] > 0])
        gross_losses = abs(sum([t['pnl'] for t in self.trade_history if t['pnl'] < 0]))
        
        return gross_profits / max(gross_losses, 0.01)
    
    def save_episode_data(self, filepath: str):
        """Salva dados do episódio"""
        episode_data = {
            'config': self.config.to_dict(),
            'metrics': self.get_metrics(),
            'portfolio_history': self.portfolio_history,
            'trade_history': self.trade_history,
            'reward_history': self.reward_history,
            'action_history': [a.to_dict() for a in self.action_history]
        }
        
        with open(filepath, 'w') as f:
            json.dump(episode_data, f, indent=2, default=str)
        
        logger.info(f"Episode data saved to {filepath}")
    
    def plot_performance(self, save_path: str = None):
        """Plota performance do episódio"""
        if len(self.portfolio_history) == 0:
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Portfolio Value
        axes[0, 0].plot(self.portfolio_history)
        axes[0, 0].axhline(y=self.initial_balance, color='r', linestyle='--', alpha=0.5)
        axes[0, 0].set_title('Portfolio Value')
        axes[0, 0].set_ylabel('Value ($)')
        axes[0, 0].grid(True)
        
        # Drawdown
        drawdown_history = []
        peak = self.initial_balance
        for value in self.portfolio_history:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            drawdown_history.append(drawdown)
        
        axes[0, 1].fill_between(range(len(drawdown_history)), drawdown_history, 0, alpha=0.3, color='red')
        axes[0, 1].plot(drawdown_history, color='red')
        axes[0, 1].set_title('Drawdown')
        axes[0, 1].set_ylabel('Drawdown (%)')
        axes[0, 1].grid(True)
        
        # Rewards
        if self.reward_history:
            axes[1, 0].plot(self.reward_history)
            axes[1, 0].set_title('Rewards')
            axes[1, 0].set_ylabel('Reward')
            axes[1, 0].grid(True)
        
        # Trade PnL
        if self.trade_history:
            trade_pnl = [t['pnl'] for t in self.trade_history]
            trade_colors = ['green' if pnl > 0 else 'red' for pnl in trade_pnl]
            axes[1, 1].bar(range(len(trade_pnl)), trade_pnl, color=trade_colors, alpha=0.7)
            axes[1, 1].set_title('Trade P&L')
            axes[1, 1].set_ylabel('P&L ($)')
            axes[1, 1].grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Performance plot saved to {save_path}")
        
        plt.show()

# Configuração padrão
DEFAULT_RL_CONFIG = EnvironmentConfig(
    initial_balance=100000.0,
    transaction_cost_pct=0.001,
    slippage_pct=0.0005,
    max_position_size=1.0,
    leverage=1.0,
    lookback_window=60,
    reward_function="composite",
    risk_free_rate=0.02,
    max_drawdown_limit=0.2,
    volatility_window=20,
    regime_detection_window=50,
    position_holding_period_min=1,
    position_holding_period_max=100,
    enable_short_selling=True,
    enable_leverage=False,
    normalize_features=True,
    include_technical_indicators=True,
    include_market_regime=True
)

if __name__ == "__main__":
    # Exemplo de uso
    def create_sample_data():
        """Cria dados de exemplo"""
        dates = pd.date_range(start='2020-01-01', end='2023-12-31', freq='D')
        np.random.seed(42)
        
        # Simula preço com tendência e volatilidade
        returns = np.random.normal(0.0005, 0.02, len(dates))
        prices = 100 * np.exp(np.cumsum(returns))
        
        # Cria features sintéticas
        n_features = 20
        feature_data = np.random.randn(len(dates), n_features)
        
        data = pd.DataFrame(index=dates)
        data['close_price'] = prices
        data['timestamp'] = dates
        
        # Adiciona features
        for i in range(n_features):
            data[f'feature_{i}'] = feature_data[:, i]
        
        return data
    
    def test_environment():
        """Testa o ambiente"""
        # Cria dados
        data = create_sample_data()
        
        # Cria ambiente
        config = DEFAULT_RL_CONFIG
        env = TradingEnvironment(config)
        env.load_data(data)
        
        # Reseta ambiente
        observation = env.reset()
        print(f"Observation shape: {observation.shape}")
        
        # Executa episódio
        done = False
        step_count = 0
        
        while not done and step_count < 100:
            # Ação aleatória
            action = env.action_space.sample()
            
            # Executa passo
            observation, reward, done, info = env.step(action)
            
            # Renderiza a cada 10 passos
            if step_count % 10 == 0:
                env.render('system')
                print(f"Step {step_count}: Action={action}, Reward={reward:.4f}")
            
            step_count += 1
        
        # Mostra métricas finais
        metrics = env.get_metrics()
        print("\n=== Final Metrics ===")
        for key, value in metrics.items():
            print(f"{key}: {value}")
        
        # Plota performance
        env.plot_performance('trading_performance.png')
        
        # Salva dados do episódio
        env.save_episode_data('episode_data.json')
        
        return env
    
    # Executa teste
    env = test_environment()
    print("✅ Environment test completed successfully!")

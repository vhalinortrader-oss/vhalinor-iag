"""
╔═════════════════════════════════════════════════════════════════════════════╗
║                    SISTEMA DE VALIDAÇÃO ROBUSTO                           ║
║                 Componente 8: Validação e Backtesting Avançado          ║
╚═════════════════════════════════════════════════════════════════════════════╝
"""

import asyncio
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.model_selection import TimeSeriesSplit, KFold
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import warnings
import json
import pickle
from collections import defaultdict, deque
import time
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('RobustValidationSystem')

class ValidationType(Enum):
    """Tipos de validação"""
    HOLD_OUT = "hold_out"
    TIME_SERIES_SPLIT = "time_series_split"
    WALK_FORWARD = "walk_forward"
    CROSS_VALIDATION = "cross_validation"
    MONTE_CARLO = "monte_carlo"
    BOOTSTRAP = "bootstrap"
    PURGED_CROSS_VALIDATION = "purged_cross_validation"
    KFOLD_CROSS_VALIDATION = "kfold_cross_validation"

class PerformanceMetric(Enum):
    """Métricas de performance"""
    ACCURACY = "accuracy"
    PRECISION = "precision"
    RECALL = "recall"
    F1_SCORE = "f1_score"
    MEAN_SQUARED_ERROR = "mse"
    ROOT_MSE = "rmse"
    MEAN_ABSOLUTE_ERROR = "mae"
    MEAN_ABSOLUTE_PERCENTAGE_ERROR = "mape"
    R_SQUARED = "r2"
    SHARPE_RATIO = "sharpe_ratio"
    SORTINO_RATIO = "sortino_ratio"
    MAX_DRAWDOWN = "max_drawdown"
    CALMAR_RATIO = "calmar_ratio"
    INFORMATION_RATIO = "information_ratio"
    TREND_CORRECTNESS = "trend_correctness"

class OverfittingType(Enum):
    """Tipos de overfitting detectados"""
    HIGH_TRAINING_ACCURACY = "high_training_accuracy"
    LOW_VALIDATION_PERFORMANCE = "low_validation_performance"
    HIGH_VARIANCE = "high_variance"
    TRAIN_TEST_GAP = "train_test_gap"
    PARAMETER_INSTABILITY = "parameter_instability"
    FEATURE_DEPENDENCY = "feature_dependency"

@dataclass
class ValidationResult:
    """Resultado de validação"""
    validation_type: ValidationType
    model_name: str
    timestamp: datetime
    train_metrics: Dict[str, float]
    validation_metrics: Dict[str, float]
    test_metrics: Dict[str, float]
    overfitting_detected: bool
    overfitting_type: Optional[OverfittingType]
    confidence_interval: Optional[Dict[str, Tuple[float, float]]]
    sample_size: int
    training_time: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'validation_type': self.validation_type.value,
            'model_name': self.model_name,
            'timestamp': self.timestamp.isoformat(),
            'train_metrics': self.train_metrics,
            'validation_metrics': self.validation_metrics,
            'test_metrics': self.test_metrics,
            'overfitting_detected': self.overfitting_detected,
            'overfitting_type': self.overfitting_type.value if self.overfitting_type else None,
            'confidence_interval': self.confidence_interval,
            'sample_size': self.sample_size,
            'training_time': self.training_time,
            'metadata': self.metadata
        }

@dataclass
class BacktestResult:
    """Resultado de backtest"""
    strategy_name: str
    start_date: datetime
    end_date: datetime
    initial_capital: float
    final_capital: float
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    calmar_ratio: float
    win_rate: float
    profit_factor: float
    number_of_trades: int
    average_trade_return: float
    benchmark_return: float
    alpha: float
    beta: float
    information_ratio: float
    trades: List[Dict[str, Any]] = field(default_factory=list)
    equity_curve: List[float] = field(default_factory=list)
    drawdown_periods: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'strategy_name': self.strategy_name,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'initial_capital': self.initial_capital,
            'final_capital': self.final_capital,
            'total_return': self.total_return,
            'annualized_return': self.annualized_return,
            'volatility': self.volatility,
            'sharpe_ratio': self.sharpe_ratio,
            'max_drawdown': self.max_drawdown,
            'calmar_ratio': self.calmar_ratio,
            'win_rate': self.win_rate,
            'profit_factor': self.profit_factor,
            'number_of_trades': self.number_of_trades,
            'average_trade_return': self.average_trade_return,
            'benchmark_return': self.benchmark_return,
            'alpha': self.alpha,
            'beta': self.beta,
            'information_ratio': self.information_ratio,
            'trades_count': len(self.trades),
            'equity_curve_length': len(self.equity_curve),
            'drawdown_periods_count': len(self.drawdown_periods)
        }

class OverfittingDetector:
    """Detetor de overfitting"""
    
    def __init__(self):
        self.detection_methods = [
            'train_val_gap',
            'learning_curve_analysis',
            'cross_validation_variance',
            'parameter_stability'
        ]
        logger.info("🔍 OverfittingDetector inicializado")
    
    def detect_overfitting(self, train_metrics: Dict[str, float], 
                         val_metrics: Dict[str, float],
                         test_metrics: Dict[str, float] = None,
                         cv_results: List[Dict[str, float]] = None) -> Tuple[bool, Optional[OverfittingType], Dict[str, Any]]:
        """Detecta overfitting usando múltiplos métodos"""
        detection_results = {}
        overfitting_detected = False
        overfitting_type = None
        
        # Método 1: Gap entre treino e validação
        gap_result = self._detect_train_val_gap(train_metrics, val_metrics)
        detection_results['train_val_gap'] = gap_result
        
        if gap_result['detected']:
            overfitting_detected = True
            overfitting_type = OverfittingType.TRAIN_TEST_GAP
        
        # Método 2: Análise de curva de aprendizado
        if cv_results:
            learning_curve_result = self._analyze_learning_curve(cv_results)
            detection_results['learning_curve'] = learning_curve_result
            
            if learning_curve_result['overfitting']:
                overfitting_detected = True
                if not overfitting_type:
                    overfitting_type = OverfittingType.HIGH_VARIANCE
        
        # Método 3: Variância em cross-validation
        if cv_results:
            variance_result = self._detect_high_variance(cv_results)
            detection_results['variance'] = variance_result
            
            if variance_result['high_variance']:
                overfitting_detected = True
                if not overfitting_type:
                    overfitting_type = OverfittingType.HIGH_VARIANCE
        
        # Método 4: Estabilidade de parâmetros
        stability_result = self._check_parameter_stability(train_metrics, val_metrics)
        detection_results['stability'] = stability_result
        
        if stability_result['unstable']:
            overfitting_detected = True
            if not overfitting_type:
                overfitting_type = OverfittingType.PARAMETER_INSTABILITY
        
        return overfitting_detected, overfitting_type, detection_results
    
    def _detect_train_val_gap(self, train_metrics: Dict[str, float], 
                            val_metrics: Dict[str, float]) -> Dict[str, Any]:
        """Detecta gap entre performance de treino e validação"""
        result = {'detected': False, 'gaps': {}}
        
        for metric in ['mse', 'mae', 'rmse']:
            if metric in train_metrics and metric in val_metrics:
                train_val = train_metrics[metric]
                val_val = val_metrics[metric]
                
                # Para métricas de erro, overfitting se validação >> treino
                if val_val > train_val * 1.5:  # 50% pior na validação
                    result['detected'] = True
                    result['gaps'][metric] = {
                        'train': train_val,
                        'validation': val_val,
                        'ratio': val_val / train_val
                    }
        
        for metric in ['r2', 'accuracy', 'sharpe_ratio']:
            if metric in train_metrics and metric in val_metrics:
                train_val = train_metrics[metric]
                val_val = val_metrics[metric]
                
                # Para métricas de performance, overfitting se treino >> validação
                if train_val > val_val * 1.3:  # 30% melhor no treino
                    result['detected'] = True
                    result['gaps'][metric] = {
                        'train': train_val,
                        'validation': val_val,
                        'ratio': train_val / val_val
                    }
        
        return result
    
    def _analyze_learning_curve(self, cv_results: List[Dict[str, float]]) -> Dict[str, Any]:
        """Analisa curva de aprendizado"""
        if len(cv_results) < 3:
            return {'overfitting': False, 'reason': 'insufficient_data'}
        
        # Extrai métricas de treino e validação
        train_scores = []
        val_scores = []
        
        for result in cv_results:
            if 'train_score' in result:
                train_scores.append(result['train_score'])
            if 'val_score' in result:
                val_scores.append(result['val_score'])
        
        if len(train_scores) < 2 or len(val_scores) < 2:
            return {'overfitting': False, 'reason': 'missing_scores'}
        
        # Verifica se gap aumenta com mais dados
        gaps = [t - v for t, v in zip(train_scores, val_scores)]
        gap_trend = np.polyfit(range(len(gaps)), gaps, 1)[0]
        
        overfitting = gap_trend > 0.01  # Gap aumentando
        
        return {
            'overfitting': overfitting,
            'gap_trend': gap_trend,
            'final_gap': gaps[-1] if gaps else 0,
            'train_scores': train_scores,
            'val_scores': val_scores
        }
    
    def _detect_high_variance(self, cv_results: List[Dict[str, float]]) -> Dict[str, Any]:
        """Detecta alta variância nos resultados de cross-validation"""
        if len(cv_results) < 3:
            return {'high_variance': False, 'reason': 'insufficient_folds'}
        
        # Extrai scores de validação
        val_scores = []
        for result in cv_results:
            if 'val_score' in result:
                val_scores.append(result['val_score'])
        
        if len(val_scores) < 3:
            return {'high_variance': False, 'reason': 'missing_scores'}
        
        # Calcula variância
        mean_score = np.mean(val_scores)
        std_score = np.std(val_scores)
        cv_score = std_score / mean_score if mean_score != 0 else float('inf')
        
        # Alta variância se CV > 0.1
        high_variance = cv_score > 0.1
        
        return {
            'high_variance': high_variance,
            'cv_score': cv_score,
            'mean_score': mean_score,
            'std_score': std_score,
            'scores': val_scores
        }
    
    def _check_parameter_stability(self, train_metrics: Dict[str, float], 
                               val_metrics: Dict[str, float]) -> Dict[str, Any]:
        """Verifica estabilidade de parâmetros (simplificado)"""
        # Esta é uma implementação simplificada
        # Na prática, seria necessário acesso aos parâmetros do modelo
        
        result = {'unstable': False, 'reason': 'not_implemented'}
        
        # Verifica consistência entre métricas relacionadas
        if 'mse' in train_metrics and 'rmse' in train_metrics:
            expected_rmse = np.sqrt(train_metrics['mse'])
            actual_rmse = train_metrics['rmse']
            
            if abs(expected_rmse - actual_rmse) / expected_rmse > 0.1:
                result['unstable'] = True
                result['reason'] = 'inconsistent_error_metrics'
        
        return result

class WalkForwardValidator:
    """Validador Walk-Forward para séries temporais"""
    
    def __init__(self):
        self.validation_results = []
        logger.info("🚶 WalkForwardValidator inicializado")
    
    def validate_model(self, model, data: pd.DataFrame, target_column: str,
                     feature_columns: List[str], window_size: int = 252,
                     step_size: int = 21, test_size: int = 63) -> List[ValidationResult]:
        """Executa validação walk-forward"""
        results = []
        
        if len(data) < window_size + test_size:
            logger.error("Dados insuficientes para validação walk-forward")
            return results
        
        total_windows = (len(data) - window_size - test_size) // step_size + 1
        
        logger.info(f"Iniciando validação walk-forward: {total_windows} janelas")
        
        for i in range(total_windows):
            start_idx = i * step_size
            train_end_idx = start_idx + window_size
            test_end_idx = train_end_idx + test_size
            
            # Dados de treino
            train_data = data.iloc[start_idx:train_end_idx]
            X_train = train_data[feature_columns]
            y_train = train_data[target_column]
            
            # Dados de teste
            test_data = data.iloc[train_end_idx:test_end_idx]
            X_test = test_data[feature_columns]
            y_test = test_data[target_column]
            
            # Treina modelo
            start_time = time.time()
            model.fit(X_train, y_train)
            training_time = time.time() - start_time
            
            # Predições
            train_pred = model.predict(X_train)
            test_pred = model.predict(X_test)
            
            # Calcula métricas
            train_metrics = self._calculate_metrics(y_train, train_pred)
            test_metrics = self._calculate_metrics(y_test, test_pred)
            
            # Detecta overfitting
            overfitting_detector = OverfittingDetector()
            overfitting_detected, overfitting_type, _ = overfitting_detector.detect_overfitting(
                train_metrics, {}, test_metrics
            )
            
            # Cria resultado
            result = ValidationResult(
                validation_type=ValidationType.WALK_FORWARD,
                model_name=model.__class__.__name__,
                timestamp=datetime.now(),
                train_metrics=train_metrics,
                validation_metrics={},
                test_metrics=test_metrics,
                overfitting_detected=overfitting_detected,
                overfitting_type=overfitting_type,
                confidence_interval=None,
                sample_size=len(train_data),
                training_time=training_time,
                metadata={
                    'window_number': i + 1,
                    'train_start': data.index[start_idx],
                    'train_end': data.index[train_end_idx - 1],
                    'test_start': data.index[train_end_idx],
                    'test_end': data.index[test_end_idx - 1]
                }
            )
            
            results.append(result)
            
            if (i + 1) % 10 == 0:
                logger.info(f"Janela {i + 1}/{total_windows} concluída")
        
        self.validation_results.extend(results)
        logger.info(f"Validação walk-forward concluída: {len(results)} janelas")
        
        return results
    
    def _calculate_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """Calcula métricas de performance"""
        metrics = {}
        
        try:
            # Métricas de regressão
            metrics['mse'] = mean_squared_error(y_true, y_pred)
            metrics['rmse'] = np.sqrt(metrics['mse'])
            metrics['mae'] = mean_absolute_error(y_true, y_pred)
            
            # MAPE (evitando divisão por zero)
            mask = y_true != 0
            if mask.any():
                metrics['mape'] = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
            else:
                metrics['mape'] = float('inf')
            
            # R²
            metrics['r2'] = r2_score(y_true, y_pred)
            
            # Direção do movimento (para séries temporais)
            if len(y_true) > 1:
                true_direction = np.diff(y_true) > 0
                pred_direction = np.diff(y_pred) > 0
                metrics['direction_accuracy'] = np.mean(true_direction == pred_direction)
            
        except Exception as e:
            logger.error(f"Erro ao calcular métricas: {e}")
            # Retorna métricas padrão
            metrics = {
                'mse': float('inf'),
                'rmse': float('inf'),
                'mae': float('inf'),
                'mape': float('inf'),
                'r2': -float('inf')
            }
        
        return metrics
    
    def get_aggregate_results(self) -> Dict[str, Any]:
        """Obtém resultados agregados da validação walk-forward"""
        if not self.validation_results:
            return {}
        
        # Extrai métricas de teste
        test_metrics = []
        for result in self.validation_results:
            test_metrics.append(result.test_metrics)
        
        if not test_metrics:
            return {}
        
        # Calcula estatísticas agregadas
        aggregate_results = {}
        
        for metric in test_metrics[0].keys():
            values = [m[metric] for m in test_metrics if metric in m and not np.isinf(m[metric])]
            
            if values:
                aggregate_results[f'{metric}_mean'] = np.mean(values)
                aggregate_results[f'{metric}_std'] = np.std(values)
                aggregate_results[f'{metric}_min'] = np.min(values)
                aggregate_results[f'{metric}_max'] = np.max(values)
                aggregate_results[f'{metric}_median'] = np.median(values)
        
        # Estatísticas de overfitting
        overfitting_count = sum(1 for r in self.validation_results if r.overfitting_detected)
        aggregate_results['overfitting_rate'] = overfitting_count / len(self.validation_results)
        
        # Tempo médio de treinamento
        training_times = [r.training_time for r in self.validation_results]
        aggregate_results['avg_training_time'] = np.mean(training_times)
        
        return aggregate_results

class BacktestEngine:
    """Motor de backtesting robusto"""
    
    def __init__(self):
        self.results = []
        logger.info("📊 BacktestEngine inicializado")
    
    def run_backtest(self, strategy, data: pd.DataFrame, 
                    initial_capital: float = 100000,
                    commission: float = 0.001,
                    slippage: float = 0.0005,
                    benchmark_column: str = 'benchmark_return') -> BacktestResult:
        """Executa backtest completo"""
        logger.info(f"Iniciando backtest para {strategy.__class__.__name__}")
        
        # Inicializa variáveis
        capital = initial_capital
        position = 0
        trades = []
        equity_curve = [initial_capital]
        returns = []
        
        # Simula trading
        for i, (timestamp, row) in enumerate(data.iterrows()):
            # Obtém sinal da estratégia
            signal = strategy.generate_signal(row, i)
            
            # Executa lógica de trading
            if signal == 1 and position <= 0:  # Buy
                if position < 0:  # Fecha short
                    price = row['close_price'] * (1 + slippage)
                    position_value = abs(position) * price
                    capital += position_value
                    capital -= position_value * commission
                    trades.append({
                        'timestamp': timestamp,
                        'type': 'buy_cover',
                        'price': price,
                        'quantity': abs(position),
                        'commission': position_value * commission,
                        'pnl': 0  # PnL calculado no fechamento
                    })
                
                # Abre long
                price = row['close_price'] * (1 + slippage)
                quantity = capital / (price * (1 + commission))
                position = quantity
                capital -= quantity * price * commission
                
            elif signal == -1 and position >= 0:  # Sell
                if position > 0:  # Fecha long
                    price = row['close_price'] * (1 - slippage)
                    position_value = position * price
                    capital += position_value
                    capital -= position_value * commission
                    
                    # Calcula PnL
                    if trades:
                        last_buy = next((t for t in reversed(trades) if t['type'] == 'buy'), None)
                        if last_buy:
                            pnl = (price - last_buy['price']) * position
                            trades[-1]['pnl'] = pnl
                
                    trades.append({
                        'timestamp': timestamp,
                        'type': 'sell',
                        'price': price,
                        'quantity': position,
                        'commission': position_value * commission,
                        'pnl': 0
                    })
                
                # Abre short
                price = row['close_price'] * (1 - slippage)
                quantity = capital / (price * (1 + commission))
                position = -quantity
                capital += quantity * price
                capital -= quantity * price * commission
            
            # Calcula valor do portfólio
            portfolio_value = capital
            if position != 0:
                current_price = row['close_price']
                portfolio_value += position * current_price
            
            equity_curve.append(portfolio_value)
            
            # Calcula retorno diário
            if len(equity_curve) > 1:
                daily_return = (equity_curve[-1] - equity_curve[-2]) / equity_curve[-2]
                returns.append(daily_return)
        
        # Calcula métricas finais
        final_capital = equity_curve[-1]
        total_return = (final_capital - initial_capital) / initial_capital
        
        # Métricas de risco
        if returns:
            volatility = np.std(returns) * np.sqrt(252)
            sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else 0
            
            # Maximum drawdown
            peak = np.maximum.accumulate(equity_curve)
            drawdown = (peak - equity_curve) / peak
            max_drawdown = np.max(drawdown)
            
            # Calmar ratio
            calmar_ratio = total_return / max_drawdown if max_drawdown > 0 else 0
        else:
            volatility = 0
            sharpe_ratio = 0
            max_drawdown = 0
            calmar_ratio = 0
        
        # Estatísticas de trades
        winning_trades = [t for t in trades if t.get('pnl', 0) > 0]
        losing_trades = [t for t in trades if t.get('pnl', 0) < 0]
        
        win_rate = len(winning_trades) / len(trades) if trades else 0
        profit_factor = (sum(t['pnl'] for t in winning_trades) / 
                        abs(sum(t['pnl'] for t in losing_trades))) if losing_trades else float('inf')
        
        # Benchmark
        if benchmark_column in data.columns:
            benchmark_return = data[benchmark_column].sum()
        else:
            benchmark_return = 0
        
        # Alpha e Beta (simplificado)
        if returns and benchmark_column in data.columns:
            benchmark_returns = data[benchmark_column].values
            if len(benchmark_returns) == len(returns):
                beta = np.cov(returns, benchmark_returns)[0, 1] / np.var(benchmark_returns)
                alpha = np.mean(returns) - beta * np.mean(benchmark_returns)
                information_ratio = alpha / np.std(returns - benchmark_returns) if np.std(returns - benchmark_returns) > 0 else 0
            else:
                beta = 0
                alpha = 0
                information_ratio = 0
        else:
            beta = 0
            alpha = 0
            information_ratio = 0
        
        # Cria resultado
        result = BacktestResult(
            strategy_name=strategy.__class__.__name__,
            start_date=data.index[0],
            end_date=data.index[-1],
            initial_capital=initial_capital,
            final_capital=final_capital,
            total_return=total_return,
            annualized_return=total_return * (252 / len(data)),
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            calmar_ratio=calmar_ratio,
            win_rate=walk_rate,
            profit_factor=profit_factor,
            number_of_trades=len(trades),
            average_trade_return=np.mean([t.get('pnl', 0) for t in trades]) if trades else 0,
            benchmark_return=benchmark_return,
            alpha=alpha,
            beta=beta,
            information_ratio=information_ratio,
            trades=trades,
            equity_curve=equity_curve
        )
        
        self.results.append(result)
        logger.info(f"Backtest concluído: Retorno Total={total_return:.2%}, Sharpe={sharpe_ratio:.2f}")
        
        return result
    
    def generate_report(self, result: BacktestResult) -> str:
        """Gera relatório detalhado do backtest"""
        report = f"""
╔═════════════════════════════════════════════════════════════════════════════╗
║                    RELATÓRIO DE BACKTEST - {result.strategy_name}                    ║
╚═════════════════════════════════════════════════════════════════════════════╝

📅 PERÍODO:
  • Início: {result.start_date.strftime('%Y-%m-%d')}
  • Fim: {result.end_date.strftime('%Y-%m-%d')}
  • Dias: {(result.end_date - result.start_date).days}

💰 CAPITAL:
  • Inicial: ${result.initial_capital:,.2f}
  • Final: ${result.final_capital:,.2f}
  • Retorno Total: {result.total_return:.2%}
  • Retorno Anualizado: {result.annualized_return:.2%}

📊 PERFORMANCE:
  • Sharpe Ratio: {result.sharpe_ratio:.2f}
  • Sortino Ratio: {result.sortino_ratio:.2f}
  • Calmar Ratio: {result.calmar_ratio:.2f}
  • Volatilidade: {result.volatility:.2%}
  • Maximum Drawdown: {result.max_drawdown:.2%}

🔄 TRADING:
  • Número de Trades: {result.number_of_trades}
  • Taxa de Acerto: {result.win_rate:.2%}
  • Profit Factor: {result.profit_factor:.2f}
  • Retorno Médio por Trade: {result.average_trade_return:.2%}

📈 BENCHMARK:
  • Retorno Benchmark: {result.benchmark_return:.2%}
  • Alpha: {result.alpha:.2%}
  • Beta: {result.beta:.2f}
  • Information Ratio: {result.information_ratio:.2f}
"""
        return report

class MonteCarloValidator:
    """Validador Monte Carlo"""
    
    def __init__(self):
        self.results = []
        logger.info("🎲 MonteCarloValidator inicializado")
    
    def monte_carlo_validation(self, model, data: pd.DataFrame, 
                            target_column: str, feature_columns: List[str],
                            n_simulations: int = 1000,
                            sample_ratio: float = 0.8) -> Dict[str, Any]:
        """Executa validação Monte Carlo"""
        logger.info(f"Iniciando validação Monte Carlo: {n_simulations} simulações")
        
        simulation_results = []
        
        for i in range(n_simulations):
            # Amostragem aleatória com reposição
            sample_data = data.sample(frac=sample_ratio, replace=True)
            
            # Divide em treino/teste
            split_idx = int(len(sample_data) * 0.7)
            train_data = sample_data.iloc[:split_idx]
            test_data = sample_data.iloc[split_idx:]
            
            # Treina modelo
            model.fit(train_data[feature_columns], train_data[target_column])
            
            # Avalia no teste
            test_pred = model.predict(test_data[feature_columns])
            mse = mean_squared_error(test_data[target_column], test_pred)
            mae = mean_absolute_error(test_data[target_column], test_pred)
            r2 = r2_score(test_data[target_column], test_pred)
            
            simulation_results.append({
                'mse': mse,
                'mae': mae,
                'r2': r2
            })
            
            if (i + 1) % 100 == 0:
                logger.info(f"Simulação {i + 1}/{n_simulations} concluída")
        
        # Calcula estatísticas das simulações
        metrics = {}
        for metric in ['mse', 'mae', 'r2']:
            values = [s[metric] for s in simulation_results]
            metrics[f'{metric}_mean'] = np.mean(values)
            metrics[f'{metric}_std'] = np.std(values)
            metrics[f'{metric}_ci_95'] = np.percentile(values, [2.5, 97.5])
        
        # Adiciona informações adicionais
        metrics['n_simulations'] = n_simulations
        metrics['sample_ratio'] = sample_ratio
        metrics['original_data_size'] = len(data)
        
        self.results.append(metrics)
        logger.info("Validação Monte Carlo concluída")
        
        return metrics

class RobustValidationSystem:
    """Sistema robusto de validação"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Componentes
        self.overfitting_detector = OverfittingDetector()
        self.walk_forward_validator = WalkForwardValidator()
        self.backtest_engine = BacktestEngine()
        self.monte_carlo_validator = MonteCarloValidator()
        
        # Resultados
        self.validation_history = []
        self.backtest_history = []
        
        logger.info("🛡️ RobustValidationSystem inicializado")
    
    def comprehensive_validation(self, model, data: pd.DataFrame, 
                             target_column: str, feature_columns: List[str]) -> Dict[str, Any]:
        """Executa validação comprehensiva"""
        logger.info("🔍 Iniciando validação comprehensiva")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'model_name': model.__class__.__name__,
            'data_info': {
                'total_samples': len(data),
                'features': len(feature_columns),
                'start_date': data.index[0],
                'end_date': data.index[-1]
            }
        }
        
        # 1. Validação Walk-Forward
        try:
            walk_forward_results = self.walk_forward_validator.validate_model(
                model, data, target_column, feature_columns
            )
            
            results['walk_forward'] = {
                'results': [r.to_dict() for r in walk_forward_results],
                'aggregate': self.walk_forward_validator.get_aggregate_results()
            }
            
            logger.info(f"✅ Walk-Forward: {len(walk_forward_results)} janelas validadas")
            
        except Exception as e:
            logger.error(f"❌ Erro na validação walk-forward: {e}")
            results['walk_forward'] = {'error': str(e)}
        
        # 2. Validação Monte Carlo
        try:
            monte_carlo_results = self.monte_carlo_validator.monte_carlo_validation(
                model, data, target_column, feature_columns
            )
            results['monte_carlo'] = monte_carlo_results
            
            logger.info("✅ Monte Carlo: validação concluída")
            
        except Exception as e:
            logger.error(f"❌ Erro na validação Monte Carlo: {e}")
            results['monte_carlo'] = {'error': str(e)}
        
        # 3. Análise de overfitting
        try:
            # Usa resultados do walk-forward para análise
            if walk_forward_results:
                train_metrics = walk_forward_results[0].train_metrics
                test_metrics = walk_forward_results[-1].test_metrics
                
                overfitting_detected, overfitting_type, detection_details = \
                    self.overfitting_detector.detect_overfitting(
                        train_metrics, {}, test_metrics
                    )
                
                results['overfitting_analysis'] = {
                    'detected': overfitting_detected,
                    'type': overfitting_type.value if overfitting_type else None,
                    'details': detection_details
                }
                
                logger.info(f"✅ Overfitting: {'Detectado' if overfitting_detected else 'Não detectado'}")
            
        except Exception as e:
            logger.error(f"❌ Erro na análise de overfitting: {e}")
            results['overfitting_analysis'] = {'error': str(e)}
        
        # 4. Recomendações
        results['recommendations'] = self._generate_recommendations(results)
        
        # Salva resultados
        self.validation_history.append(results)
        
        logger.info("🎯 Validação comprehensiva concluída")
        return results
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Gera recomendações baseadas nos resultados"""
        recommendations = []
        
        # Análise de overfitting
        overfitting = results.get('overfitting_analysis', {})
        if overfitting.get('detected', False):
            recommendations.append("⚠️ Overfitting detectado: considere regularização ou reduzir complexidade do modelo")
        
        # Análise walk-forward
        walk_forward = results.get('walk_forward', {})
        if 'aggregate' in walk_forward:
            aggregate = walk_forward['aggregate']
            
            if aggregate.get('mse_std', 0) > aggregate.get('mse_mean', 0) * 0.5:
                recommendations.append("📊 Alta variância no walk-forward: modelo instável")
            
            if aggregate.get('overfitting_rate', 0) > 0.3:
                recommendations.append("🔄 Alta taxa de overfitting: revise arquitetura do modelo")
        
        # Análise Monte Carlo
        monte_carlo = results.get('monte_carlo', {})
        if 'r2_ci_95' in monte_carlo:
            r2_ci = monte_carlo['r2_ci_95']
            if r2_ci[1] - r2_ci[0] > 0.5:  # Intervalo muito largo
                recommendations.append("🎲 Alta incerteza no Monte Carlo: aumente dados ou simplifique modelo")
        
        if not recommendations:
            recommendations.append("✅ Modelo parece robusto e bem validado")
        
        return recommendations
    
    def save_results(self, filepath: str):
        """Salva resultados de validação"""
        try:
            with open(filepath, 'w') as f:
                json.dump({
                    'validation_history': self.validation_history,
                    'backtest_history': [r.to_dict() for r in self.backtest_history],
                    'timestamp': datetime.now().isoformat()
                }, f, indent=2, default=str)
            
            logger.info(f"💾 Resultados salvos em {filepath}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar resultados: {e}")
    
    def load_results(self, filepath: str):
        """Carrega resultados de validação"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            self.validation_history = data.get('validation_history', [])
            
            # Reconstrói BacktestResults
            backtest_data = data.get('backtest_history', [])
            self.backtest_history = []
            for bt_data in backtest_data:
                # Conversão simplificada - na prática precisaria reconstruir objeto completo
                pass
            
            logger.info(f"📂 Resultados carregados de {filepath}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar resultados: {e}")

# Configuração padrão
DEFAULT_VALIDATION_CONFIG = {
    'walk_forward': {
        'window_size': 252,  # 1 ano de dias úteis
        'step_size': 21,     # 1 mês
        'test_size': 63       # 3 meses
    },
    'monte_carlo': {
        'n_simulations': 1000,
        'sample_ratio': 0.8
    },
    'overfitting': {
        'train_val_gap_threshold': 1.5,
        'variance_threshold': 0.1
    },
    'backtest': {
        'initial_capital': 100000,
        'commission': 0.001,
        'slippage': 0.0005
    }
}

if __name__ == "__main__":
    # Exemplo de uso
    def create_sample_model():
        """Cria modelo de exemplo"""
        from sklearn.ensemble import RandomForestRegressor
        return RandomForestRegressor(n_estimators=100, random_state=42)
    
    def create_sample_data():
        """Cria dados de exemplo"""
        dates = pd.date_range(start='2020-01-01', end='2023-12-31', freq='D')
        np.random.seed(42)
        
        # Simula preços com tendência e ruído
        trend = np.linspace(100, 150, len(dates))
        noise = np.random.normal(0, 5, len(dates))
        prices = trend + noise
        
        # Features sintéticas
        features = {
            'feature_1': np.random.randn(len(dates)),
            'feature_2': np.random.randn(len(dates)),
            'feature_3': np.random.randn(len(dates)),
            'feature_4': np.random.randn(len(dates)),
            'feature_5': np.random.randn(len(dates))
        }
        
        # Target (próximo preço)
        target = np.roll(prices, -1)[:-1]
        prices = prices[:-1]
        dates = dates[:-1]
        
        # Cria DataFrame
        data = pd.DataFrame(features, index=dates)
        data['close_price'] = prices
        data['target'] = target
        data['benchmark_return'] = data['close_price'].pct_change()
        
        return data
    
    def test_validation_system():
        """Testa sistema de validação"""
        # Cria dados e modelo
        model = create_sample_model()
        data = create_sample_data()
        
        feature_columns = [f'feature_{i}' for i in range(1, 6)]
        target_column = 'target'
        
        # Cria sistema de validação
        validator = RobustValidationSystem(DEFAULT_VALIDATION_CONFIG)
        
        # Executa validação comprehensiva
        results = validator.comprehensive_validation(
            model, data, target_column, feature_columns
        )
        
        # Mostra resultados principais
        print("🎯 RESULTADOS DA VALIDAÇÃO COMPREHENSIVA")
        print("=" * 50)
        
        # Walk-Forward
        if 'walk_forward' in results:
            wf = results['walk_forward']
            if 'aggregate' in wf:
                agg = wf['aggregate']
                print(f"\n📊 WALK-FORWARD:")
                print(f"  MSE Médio: {agg.get('mse_mean', 0):.4f}")
                print(f"  R² Médio: {agg.get('r2_mean', 0):.4f}")
                print(f"  Taxa de Overfitting: {agg.get('overfitting_rate', 0):.2%}")
        
        # Monte Carlo
        if 'monte_carlo' in results:
            mc = results['monte_carlo']
            print(f"\n🎲 MONTE CARLO:")
            print(f"  MSE Médio: {mc.get('mse_mean', 0):.4f}")
            print(f"  R² Médio: {mc.get('r2_mean', 0):.4f}")
            if 'r2_ci_95' in mc:
                ci = mc['r2_ci_95']
                print(f"  R² IC 95%: [{ci[0]:.3f}, {ci[1]:.3f}]")
        
        # Overfitting
        if 'overfitting_analysis' in results:
            of = results['overfitting_analysis']
            print(f"\n🔍 OVERFITTING:")
            print(f"  Detectado: {'Sim' if of.get('detected', False) else 'Não'}")
            if of.get('type'):
                print(f"  Tipo: {of['type']}")
        
        # Recomendações
        if 'recommendations' in results:
            print(f"\n💡 RECOMENDAÇÕES:")
            for rec in results['recommendations']:
                print(f"  {rec}")
        
        # Salva resultados
        validator.save_results('validation_results.json')
        
        return validator, results
    
    # Executa teste
    validator, validation_results = test_validation_system()
    print("✅ Sistema de validação robusta testado com sucesso!")

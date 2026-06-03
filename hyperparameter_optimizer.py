"""
Hyperparameter Optimizer - Sistema de Ajuste de Hiperparâmetros
=============================================================
Grid Search, Random Search, Bayesian Optimization e Regularização
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import os
from pathlib import Path
import hashlib
import pickle
import math
import random

# Importações condicionais
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False

try:
    from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, cross_val_score
    from sklearn.metrics import accuracy_score, mean_squared_error
    from sklearn.base import BaseEstimator
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import optuna
    from optuna.samplers import TPESampler, RandomSampler
    from optuna.pruners import MedianPruner
    OPTUNA_AVAILABLE = True
except ImportError:
    OPTUNA_AVAILABLE = False

try:
    import hyperopt
    from hyperopt import fmin, tpe, hp, STATUS_OK, Trials
    HYPEROPT_AVAILABLE = True
except ImportError:
    HYPEROPT_AVAILABLE = False

from config import settings
from core import get_logger, log_execution
from .model_architect import ModelConfig, ModelType, TaskType, OptimizerType, ActivationFunction
from .model_trainer import TrainingConfig, TrainingResult
from .model_evaluator import EvaluationResult


class OptimizationMethod(str, Enum):
    """Métodos de otimização"""
    GRID_SEARCH = "grid_search"
    RANDOM_SEARCH = "random_search"
    BAYESIAN_OPTIMIZATION = "bayesian_optimization"
    GENETIC_ALGORITHM = "genetic_algorithm"
    PARTICLE_SWARM = "particle_swarm"
    SIMULATED_ANNEALING = "simulated_annealing"
    OPTUNA = "optuna"
    HYPEROPT = "hyperopt"
    CUSTOM = "custom"


class SearchSpaceType(str, Enum):
    """Tipos de espaço de busca"""
    CATEGORICAL = "categorical"
    DISCRETE_UNIFORM = "discrete_uniform"
    UNIFORM = "uniform"
    LOG_UNIFORM = "log_uniform"
    NORMAL = "normal"
    INT_UNIFORM = "int_uniform"


class PruningStrategy(str, Enum):
    """Estratégias de pruning"""
    NONE = "none"
    MEDIAN = "median"
    HYPERBAND = "hyperband"
    SUCCESSIVE_HALVING = "successive_halving"
    CUSTOM = "custom"


@dataclass
class HyperparameterSpace:
    """Espaço de busca para hiperparâmetros"""
    name: str
    space_type: SearchSpaceType
    low: Optional[Union[float, int]] = None
    high: Optional[Union[float, int]] = None
    choices: Optional[List[Any]] = None
    step: Optional[float] = None
    log: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'space_type': self.space_type.value,
            'low': self.low,
            'high': self.high,
            'choices': self.choices,
            'step': self.step,
            'log': self.log
        }


@dataclass
class OptimizationConfig:
    """Configuração de otimização"""
    method: OptimizationMethod
    n_trials: int = 100
    n_jobs: int = -1
    cv_folds: int = 5
    scoring_metric: str = "accuracy"
    timeout: Optional[int] = None  # em segundos
    early_stopping: bool = True
    pruning_strategy: PruningStrategy = PruningStrategy.MEDIAN
    random_state: int = 42
    verbose: int = 1
    save_trials: bool = True
    custom_params: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'method': self.method.value,
            'n_trials': self.n_trials,
            'n_jobs': self.n_jobs,
            'cv_folds': self.cv_folds,
            'scoring_metric': self.scoring_metric,
            'timeout': self.timeout,
            'early_stopping': self.early_stopping,
            'pruning_strategy': self.pruning_strategy.value,
            'random_state': self.random_state,
            'verbose': self.verbose,
            'save_trials': self.save_trials,
            'custom_params': self.custom_params
        }


@dataclass
class OptimizationResult:
    """Resultado da otimização"""
    best_params: Dict[str, Any]
    best_score: float
    best_model_config: ModelConfig
    optimization_history: List[Dict[str, Any]]
    n_trials_completed: int
    optimization_time: float
    method: OptimizationMethod
    convergence_curve: Optional[List[float]] = None
    feature_importance: Optional[Dict[str, float]] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'best_params': self.best_params,
            'best_score': self.best_score,
            'best_model_config': self.best_model_config.to_dict(),
            'optimization_history': self.optimization_history,
            'n_trials_completed': self.n_trials_completed,
            'optimization_time': self.optimization_time,
            'method': self.method.value,
            'convergence_curve': self.convergence_curve,
            'feature_importance': self.feature_importance,
            'timestamp': self.timestamp.isoformat()
        }


class SearchSpaceBuilder:
    """Construtor de espaços de busca"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.optimizer.space", "search_space_builder")
    
    def create_neural_network_space(self, model_type: ModelType) -> List[HyperparameterSpace]:
        """Cria espaço de busca para redes neurais"""
        spaces = []
        
        # Learning rate
        spaces.append(HyperparameterSpace(
            name="learning_rate",
            space_type=SearchSpaceType.LOG_UNIFORM,
            low=1e-5,
            high=1e-1,
            log=True
        ))
        
        # Batch size
        spaces.append(HyperparameterSpace(
            name="batch_size",
            space_type=SearchSpaceType.CATEGORICAL,
            choices=[16, 32, 64, 128, 256]
        ))
        
        # Hidden dimensions
        if model_type == ModelType.NEURAL_NETWORK:
            spaces.append(HyperparameterSpace(
                name="hidden_dims",
                space_type=SearchSpaceType.CATEGORICAL,
                choices=[
                    [64, 32],
                    [128, 64, 32],
                    [256, 128, 64],
                    [512, 256, 128],
                    [128, 64, 32, 16]
                ]
            ))
        
        # Dropout rate
        spaces.append(HyperparameterSpace(
            name="dropout_rate",
            space_type=SearchSpaceType.UNIFORM,
            low=0.0,
            high=0.5
        ))
        
        # Optimizer
        spaces.append(HyperparameterSpace(
            name="optimizer",
            space_type=SearchSpaceType.CATEGORICAL,
            choices=[opt.value for opt in OptimizerType]
        ))
        
        # Weight decay
        spaces.append(HyperparameterSpace(
            name="weight_decay",
            space_type=SearchSpaceType.LOG_UNIFORM,
            low=1e-6,
            high=1e-2,
            log=True
        ))
        
        return spaces
    
    def create_sklearn_space(self, model_type: ModelType) -> List[HyperparameterSpace]:
        """Cria espaço de busca para modelos sklearn"""
        spaces = []
        
        if model_type == ModelType.RANDOM_FOREST:
            spaces.extend([
                HyperparameterSpace(
                    name="n_estimators",
                    space_type=SearchSpaceType.INT_UNIFORM,
                    low=50,
                    high=500,
                    step=50
                ),
                HyperparameterSpace(
                    name="max_depth",
                    space_type=SearchSpaceType.CATEGORICAL,
                    choices=[None, 5, 10, 15, 20, 25, 30]
                ),
                HyperparameterSpace(
                    name="min_samples_split",
                    space_type=SearchSpaceType.INT_UNIFORM,
                    low=2,
                    high=20,
                    step=2
                ),
                HyperparameterSpace(
                    name="min_samples_leaf",
                    space_type=SearchSpaceType.INT_UNIFORM,
                    low=1,
                    high=10,
                    step=1
                )
            ])
        
        elif model_type == ModelType.SVM:
            spaces.extend([
                HyperparameterSpace(
                    name="C",
                    space_type=SearchSpaceType.LOG_UNIFORM,
                    low=1e-3,
                    high=1e3,
                    log=True
                ),
                HyperparameterSpace(
                    name="kernel",
                    space_type=SearchSpaceType.CATEGORICAL,
                    choices=["linear", "rbf", "poly", "sigmoid"]
                ),
                HyperparameterSpace(
                    name="gamma",
                    space_type=SearchSpaceType.LOG_UNIFORM,
                    low=1e-4,
                    high=1e1,
                    log=True
                )
            ])
        
        elif model_type == ModelType.GRADIENT_BOOSTING:
            spaces.extend([
                HyperparameterSpace(
                    name="n_estimators",
                    space_type=SearchSpaceType.INT_UNIFORM,
                    low=50,
                    high=500,
                    step=50
                ),
                HyperparameterSpace(
                    name="learning_rate",
                    space_type=SearchSpaceType.LOG_UNIFORM,
                    low=1e-4,
                    high=1e-1,
                    log=True
                ),
                HyperparameterSpace(
                    name="max_depth",
                    space_type=SearchSpaceType.INT_UNIFORM,
                    low=3,
                    high=10,
                    step=1
                )
            ])
        
        return spaces
    
    def create_training_space(self) -> List[HyperparameterSpace]:
        """Cria espaço de busca para parâmetros de treinamento"""
        return [
            HyperparameterSpace(
                name="epochs",
                space_type=SearchSpaceType.CATEGORICAL,
                choices=[50, 100, 150, 200, 300]
            ),
            HyperparameterSpace(
                name="early_stopping_patience",
                space_type=SearchSpaceType.INT_UNIFORM,
                low=5,
                high=30,
                step=5
            ),
            HyperparameterSpace(
                name="gradient_clipping",
                space_type=SearchSpaceType.CATEGORICAL,
                choices=[None, 0.5, 1.0, 2.0, 5.0]
            )
        ]


class GridSearchOptimizer:
    """Otimizador Grid Search"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.optimizer.grid", "grid_search")
    
    def optimize(self, model: Any, param_grid: Dict[str, List[Any]], X: Any, y: Any, config: OptimizationConfig) -> OptimizationResult:
        """Realiza Grid Search"""
        if not SKLEARN_AVAILABLE:
            raise ImportError("sklearn is required for Grid Search")
        
        start_time = time.time()
        self.logger.info(f"Starting Grid Search with {config.n_trials} max combinations")
        
        try:
            grid_search = GridSearchCV(
                estimator=model,
                param_grid=param_grid,
                cv=config.cv_folds,
                scoring=config.scoring_metric,
                n_jobs=config.n_jobs,
                verbose=config.verbose,
                return_train_score=True
            )
            
            grid_search.fit(X, y)
            
            # Preparar histórico
            optimization_history = []
            for i, params in enumerate(grid_search.cv_results_['params']):
                optimization_history.append({
                    'trial': i,
                    'params': params,
                    'mean_test_score': grid_search.cv_results_['mean_test_score'][i],
                    'std_test_score': grid_search.cv_results_['std_test_score'][i],
                    'mean_train_score': grid_search.cv_results_['mean_train_score'][i]
                })
            
            optimization_time = time.time() - start_time
            
            result = OptimizationResult(
                best_params=grid_search.best_params_,
                best_score=grid_search.best_score_,
                best_model_config=self._create_config_from_params(grid_search.best_params_),
                optimization_history=optimization_history,
                n_trials_completed=len(grid_search.cv_results_['params']),
                optimization_time=optimization_time,
                method=OptimizationMethod.GRID_SEARCH,
                convergence_curve=self._create_convergence_curve(optimization_history)
            )
            
            self.logger.info(f"Grid Search completed in {optimization_time:.2f}s - Best score: {grid_search.best_score_:.4f}")
            
            return result
        
        except Exception as e:
            self.logger.error(f"Error in Grid Search: {e}")
            raise
    
    def _create_config_from_params(self, params: Dict[str, Any]) -> ModelConfig:
        """Cria ModelConfig a partir de parâmetros otimizados"""
        # Implementar conversão baseada nos parâmetros
        return ModelConfig(
            model_type=ModelType.RANDOM_FOREST,  # Placeholder
            task_type=TaskType.CLASSIFICATION,     # Placeholder
            hyperparameters=params
        )
    
    def _create_convergence_curve(self, history: List[Dict[str, Any]]) -> List[float]:
        """Cria curva de convergência"""
        scores = [trial['mean_test_score'] for trial in history]
        # Ordenar e calcular melhor score até cada ponto
        best_so_far = []
        current_best = float('-inf')
        for score in scores:
            if score > current_best:
                current_best = score
            best_so_far.append(current_best)
        return best_so_far


class RandomSearchOptimizer:
    """Otimizador Random Search"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.optimizer.random", "random_search")
    
    def optimize(self, model: Any, param_distributions: Dict[str, List[Any]], X: Any, y: Any, config: OptimizationConfig) -> OptimizationResult:
        """Realiza Random Search"""
        if not SKLEARN_AVAILABLE:
            raise ImportError("sklearn is required for Random Search")
        
        start_time = time.time()
        self.logger.info(f"Starting Random Search with {config.n_trials} trials")
        
        try:
            random_search = RandomizedSearchCV(
                estimator=model,
                param_distributions=param_distributions,
                n_iter=config.n_trials,
                cv=config.cv_folds,
                scoring=config.scoring_metric,
                n_jobs=config.n_jobs,
                verbose=config.verbose,
                random_state=config.random_state,
                return_train_score=True
            )
            
            random_search.fit(X, y)
            
            # Preparar histórico
            optimization_history = []
            for i, params in enumerate(random_search.cv_results_['params']):
                optimization_history.append({
                    'trial': i,
                    'params': params,
                    'mean_test_score': random_search.cv_results_['mean_test_score'][i],
                    'std_test_score': random_search.cv_results_['std_test_score'][i],
                    'mean_train_score': random_search.cv_results_['mean_train_score'][i]
                })
            
            optimization_time = time.time() - start_time
            
            result = OptimizationResult(
                best_params=random_search.best_params_,
                best_score=random_search.best_score_,
                best_model_config=self._create_config_from_params(random_search.best_params_),
                optimization_history=optimization_history,
                n_trials_completed=len(random_search.cv_results_['params']),
                optimization_time=optimization_time,
                method=OptimizationMethod.RANDOM_SEARCH,
                convergence_curve=self._create_convergence_curve(optimization_history)
            )
            
            self.logger.info(f"Random Search completed in {optimization_time:.2f}s - Best score: {random_search.best_score_:.4f}")
            
            return result
        
        except Exception as e:
            self.logger.error(f"Error in Random Search: {e}")
            raise
    
    def _create_config_from_params(self, params: Dict[str, Any]) -> ModelConfig:
        """Cria ModelConfig a partir de parâmetros otimizados"""
        return ModelConfig(
            model_type=ModelType.RANDOM_FOREST,
            task_type=TaskType.CLASSIFICATION,
            hyperparameters=params
        )
    
    def _create_convergence_curve(self, history: List[Dict[str, Any]]) -> List[float]:
        """Cria curva de convergência"""
        scores = [trial['mean_test_score'] for trial in history]
        best_so_far = []
        current_best = float('-inf')
        for score in scores:
            if score > current_best:
                current_best = score
            best_so_far.append(current_best)
        return best_so_far


class BayesianOptimizer:
    """Otimizador Bayesian (Optuna)"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.optimizer.bayesian", "bayesian_optimizer")
    
    def optimize(self, model_creator: Callable, search_spaces: List[HyperparameterSpace], X: Any, y: Any, config: OptimizationConfig) -> OptimizationResult:
        """Realiza otimização bayesiana com Optuna"""
        if not OPTUNA_AVAILABLE:
            raise ImportError("optuna is required for Bayesian optimization")
        
        start_time = time.time()
        self.logger.info(f"Starting Bayesian optimization with {config.n_trials} trials")
        
        try:
            # Criar estudo
            sampler = TPESampler(seed=config.random_state)
            pruner = MedianPruner() if config.pruning_strategy == PruningStrategy.MEDIAN else None
            
            study = optuna.create_study(
                direction="maximize",
                sampler=sampler,
                pruner=pruner
            )
            
            # Definir função objetivo
            def objective(trial):
                # Sugerir hiperparâmetros
                params = {}
                for space in search_spaces:
                    if space.space_type == SearchSpaceType.CATEGORICAL:
                        params[space.name] = trial.suggest_categorical(space.name, space.choices)
                    elif space.space_type == SearchSpaceType.UNIFORM:
                        params[space.name] = trial.suggest_float(space.name, space.low, space.high)
                    elif space.space_type == SearchSpaceType.LOG_UNIFORM:
                        params[space.name] = trial.suggest_float(space.name, space.low, space.high, log=True)
                    elif space.space_type == SearchSpaceType.INT_UNIFORM:
                        params[space.name] = trial.suggest_int(space.name, space.low, space.high, step=space.step)
                
                # Criar modelo com parâmetros
                model = model_creator(params)
                
                # Avaliar com cross-validation
                scores = cross_val_score(model, X, y, cv=config.cv_folds, scoring=config.scoring_metric, n_jobs=1)
                
                return scores.mean()
            
            # Otimizar
            study.optimize(objective, n_trials=config.n_trials, timeout=config.timeout)
            
            # Preparar histórico
            optimization_history = []
            for trial in study.trials:
                optimization_history.append({
                    'trial': trial.number,
                    'params': trial.params,
                    'value': trial.value if trial.value is not None else float('-inf'),
                    'state': trial.state.name
                })
            
            optimization_time = time.time() - start_time
            
            result = OptimizationResult(
                best_params=study.best_params,
                best_score=study.best_value,
                best_model_config=self._create_config_from_params(study.best_params),
                optimization_history=optimization_history,
                n_trials_completed=len(study.trials),
                optimization_time=optimization_time,
                method=OptimizationMethod.BAYESIAN_OPTIMIZATION,
                convergence_curve=self._create_convergence_curve(optimization_history)
            )
            
            self.logger.info(f"Bayesian optimization completed in {optimization_time:.2f}s - Best score: {study.best_value:.4f}")
            
            return result
        
        except Exception as e:
            self.logger.error(f"Error in Bayesian optimization: {e}")
            raise
    
    def _create_config_from_params(self, params: Dict[str, Any]) -> ModelConfig:
        """Cria ModelConfig a partir de parâmetros otimizados"""
        return ModelConfig(
            model_type=ModelType.NEURAL_NETWORK,
            task_type=TaskType.CLASSIFICATION,
            hyperparameters=params
        )
    
    def _create_convergence_curve(self, history: List[Dict[str, Any]]) -> List[float]:
        """Cria curva de convergência"""
        values = [trial['value'] for trial in history if trial['value'] != float('-inf')]
        best_so_far = []
        current_best = float('-inf')
        for value in values:
            if value > current_best:
                current_best = value
            best_so_far.append(current_best)
        return best_so_far


class HyperparameterOptimizer:
    """Otimizador principal de hiperparâmetros"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.optimizer.main", "hyperparameter_optimizer")
        
        # Inicializar otimizadores
        self.grid_optimizer = GridSearchOptimizer()
        self.random_optimizer = RandomSearchOptimizer()
        self.bayesian_optimizer = BayesianOptimizer()
        self.space_builder = SearchSpaceBuilder()
        
        self.optimization_results = {}
    
    @log_execution(component="optimizer", operation="optimize_hyperparameters")
    async def optimize_hyperparameters(self, model_config: ModelConfig, X: Any, y: Any, config: OptimizationConfig) -> OptimizationResult:
        """Otimiza hiperparâmetros do modelo"""
        self.logger.info(f"Optimizing {model_config.model_type.value} hyperparameters with {config.method.value}")
        
        try:
            # Criar espaço de busca
            search_spaces = self._create_search_space(model_config)
            
            # Converter para formato do otimizador
            param_space = self._convert_search_space(search_spaces, config.method)
            
            # Criar modelo base
            base_model = self._create_base_model(model_config)
            
            # Otimizar baseado no método
            if config.method == OptimizationMethod.GRID_SEARCH:
                result = self.grid_optimizer.optimize(base_model, param_space, X, y, config)
            elif config.method == OptimizationMethod.RANDOM_SEARCH:
                result = self.random_optimizer.optimize(base_model, param_space, X, y, config)
            elif config.method == OptimizationMethod.BAYESIAN_OPTIMIZATION:
                result = await self.bayesian_optimizer.optimize(
                    lambda params: self._create_model_with_params(model_config, params),
                    search_spaces, X, y, config
                )
            else:
                raise ValueError(f"Unsupported optimization method: {config.method}")
            
            # Armazenar resultado
            result_key = f"{model_config.model_type.value}_{config.method.value}_{int(time.time())}"
            self.optimization_results[result_key] = result
            
            return result
        
        except Exception as e:
            self.logger.error(f"Error optimizing hyperparameters: {e}")
            raise
    
    def _create_search_space(self, model_config: ModelConfig) -> List[HyperparameterSpace]:
        """Cria espaço de busca para o modelo"""
        if model_config.model_type in [ModelType.NEURAL_NETWORK]:
            neural_spaces = self.space_builder.create_neural_network_space(model_config.model_type)
            training_spaces = self.space_builder.create_training_space()
            return neural_spaces + training_spaces
        else:
            return self.space_builder.create_sklearn_space(model_config.model_type)
    
    def _convert_search_space(self, search_spaces: List[HyperparameterSpace], method: OptimizationMethod) -> Dict[str, Any]:
        """Converte espaço de busca para formato do otimizador"""
        if method == OptimizationMethod.GRID_SEARCH:
            # Para Grid Search, usar valores discretos
            param_grid = {}
            for space in search_spaces:
                if space.space_type == SearchSpaceType.CATEGORICAL:
                    param_grid[space.name] = space.choices
                elif space.space_type == SearchSpaceType.INT_UNIFORM:
                    param_grid[space.name] = list(range(space.low, space.high + 1, space.step or 1))
                elif space.space_type == SearchSpaceType.UNIFORM:
                    # Discretizar espaço contínuo
                    n_points = 5
                    param_grid[space.name] = np.linspace(space.low, space.high, n_points).tolist()
            return param_grid
        
        elif method == OptimizationMethod.RANDOM_SEARCH:
            # Para Random Search, usar distribuições
            param_distributions = {}
            for space in search_spaces:
                if space.space_type == SearchSpaceType.CATEGORICAL:
                    param_distributions[space.name] = space.choices
                elif space.space_type == SearchSpaceType.UNIFORM:
                    param_distributions[space.name] = list(np.random.uniform(space.low, space.high, 20))
                elif space.space_type == SearchSpaceType.LOG_UNIFORM:
                    param_distributions[space.name] = list(np.random.uniform(space.low, space.high, 20))
                elif space.space_type == SearchSpaceType.INT_UNIFORM:
                    param_distributions[space.name] = list(range(space.low, space.high + 1, space.step or 1))
            return param_distributions
        
        else:
            return {}
    
    def _create_base_model(self, model_config: ModelConfig) -> Any:
        """Cria modelo base para otimização"""
        # Implementar criação de modelo base
        if SKLEARN_AVAILABLE:
            if model_config.model_type == ModelType.RANDOM_FOREST:
                from sklearn.ensemble import RandomForestClassifier
                return RandomForestClassifier(random_state=42)
            elif model_config.model_type == ModelType.SVM:
                from sklearn.svm import SVC
                return SVC(random_state=42)
            elif model_config.model_type == ModelType.GRADIENT_BOOSTING:
                from sklearn.ensemble import GradientBoostingClassifier
                return GradientBoostingClassifier(random_state=42)
        
        # Placeholder para outros tipos
        return None
    
    def _create_model_with_params(self, base_config: ModelConfig, params: Dict[str, Any]) -> Any:
        """Cria modelo com parâmetros específicos"""
        # Implementar criação de modelo com parâmetros
        if SKLEARN_AVAILABLE:
            if base_config.model_type == ModelType.RANDOM_FOREST:
                return RandomForestClassifier(**params, random_state=42)
            elif base_config.model_type == ModelType.SVM:
                return SVC(**params, random_state=42)
            elif base_config.model_type == ModelType.GRADIENT_BOOSTING:
                return GradientBoostingClassifier(**params, random_state=42)
        
        return None
    
    def get_optimization_result(self, result_key: str) -> Optional[OptimizationResult]:
        """Retorna resultado de otimização específico"""
        return self.optimization_results.get(result_key)
    
    def list_optimization_results(self) -> List[str]:
        """Lista todos os resultados de otimização"""
        return list(self.optimization_results.keys())
    
    def compare_optimization_methods(self, results: List[OptimizationResult]) -> Dict[str, Any]:
        """Compara diferentes métodos de otimização"""
        if not results:
            return {}
        
        comparison = {
            'methods': [],
            'best_method': None,
            'method_scores': {},
            'convergence_comparison': {}
        }
        
        # Coletar resultados por método
        method_results = {}
        for result in results:
            method = result.method.value
            if method not in method_results:
                method_results[method] = []
            method_results[method].append(result)
        
        # Comparar métodos
        best_score = float('-inf')
        best_method = None
        
        for method, method_results_list in method_results.items():
            # Melhor resultado para este método
            best_result = max(method_results_list, key=lambda x: x.best_score)
            
            comparison['method_scores'][method] = {
                'best_score': best_result.best_score,
                'best_params': best_result.best_params,
                'n_trials': best_result.n_trials_completed,
                'optimization_time': best_result.optimization_time
            }
            
            comparison['convergence_comparison'][method] = best_result.convergence_curve
            
            if best_result.best_score > best_score:
                best_score = best_result.best_score
                best_method = method
        
        comparison['best_method'] = best_method
        comparison['methods'] = list(method_results.keys())
        
        return comparison
    
    def create_standard_config(self, model_type: ModelType, method: OptimizationMethod) -> OptimizationConfig:
        """Cria configuração padrão de otimização"""
        return OptimizationConfig(
            method=method,
            n_trials=100 if method == OptimizationMethod.BAYESIAN_OPTIMIZATION else 50,
            cv_folds=5,
            scoring_metric="accuracy",
            early_stopping=True,
            pruning_strategy=PruningStrategy.MEDIAN,
            verbose=1
        )
    
    def get_optimizer_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do otimizador"""
        stats = {
            'total_optimizations': len(self.optimization_results),
            'available_methods': [method.value for method in OptimizationMethod],
            'search_space_types': [space_type.value for space_type in SearchSpaceType],
            'pruning_strategies': [strategy.value for strategy in PruningStrategy]
        }
        
        # Estatísticas por método
        method_counts = {}
        for result in self.optimization_results.values():
            method = result.method.value
            method_counts[method] = method_counts.get(method, 0) + 1
        
        stats['optimizations_by_method'] = method_counts
        
        return stats


# Função de conveniência
_optimizer_instance = None

def get_hyperparameter_optimizer() -> HyperparameterOptimizer:
    """Obtém instância singleton do otimizador de hiperparâmetros"""
    global _optimizer_instance
    if _optimizer_instance is None:
        _optimizer_instance = HyperparameterOptimizer()
    return _optimizer_instance

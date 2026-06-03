"""Módulos Principais do VHALINOR AI Geral"""

from .data_fetcher import DataFetcher, MarketData, OrderBookData, DataSourceType, get_data_fetcher
from .ai_analyzer import AIAnalyzer, AnalysisResult, Entity, SentimentScore, AnalysisType, get_ai_analyzer
from .predictor import Predictor, PredictionResult, BacktestResult, LSTMModel, TransformerModel, PredictionType, get_predictor
from .neural_network import DynamicNeuralNetwork, NeuralNetworkBuilder, NeuroEvolution, MultiHeadAttention, TransformerBlock, LayerConfig, LayerType, ActivationType
from .automation import AutomationManager, AutomationTask, AutomationResult, WebAutomation, DesktopAutomation, AutomationType, TaskStatus, Priority, get_automation_manager
from .blockchain import BlockchainManager, WalletAccount, Transaction, NetworkType, TransactionStatus, get_blockchain_manager

__all__ = [
    # Data Fetcher
    "DataFetcher",
    "MarketData", 
    "OrderBookData",
    "DataSourceType",
    "get_data_fetcher",
    
    # AI Analyzer
    "AIAnalyzer",
    "AnalysisResult",
    "Entity",
    "SentimentScore", 
    "AnalysisType",
    "get_ai_analyzer",
    
    # Predictor
    "Predictor",
    "PredictionResult",
    "BacktestResult",
    "LSTMModel",
    "TransformerModel",
    "PredictionType",
    "get_predictor",
    
    # Neural Network
    "DynamicNeuralNetwork",
    "NeuralNetworkBuilder",
    "NeuroEvolution",
    "MultiHeadAttention",
    "TransformerBlock",
    "LayerConfig",
    "LayerType",
    "ActivationType",
    
    # Automation
    "AutomationManager",
    "AutomationTask",
    "AutomationResult",
    "WebAutomation",
    "DesktopAutomation",
    "AutomationType",
    "TaskStatus",
    "Priority",
    "get_automation_manager",
    
    # Blockchain
    "BlockchainManager",
    "WalletAccount",
    "Transaction",
    "NetworkType",
    "TransactionStatus",
    "get_blockchain_manager"
]

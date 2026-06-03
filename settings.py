from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Configurações do sistema"""
    
    # API Keys
    BINANCE_API_KEY: Optional[str] = None
    BINANCE_SECRET_KEY: Optional[str] = None
    INFURA_URL: Optional[str] = None
    
    # Trading Config
    DEFAULT_TRADE_AMOUNT: float = 100.0
    MAX_RISK_PERCENT: float = 2.0
    STOP_LOSS_PERCENT: float = 1.0
    TAKE_PROFIT_PERCENT: float = 3.0
    
    # Database
    DATABASE_URL: str = "sqlite:///vhalinor_trader.db"
    REDIS_URL: str = "redis://localhost:6379"
    
    # AI Models
    AI_MODEL_PATH: str = "models/ai_model.pkl"
    NEURAL_NETWORK_PATH: str = "models/neural_network.h5"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/vhalinor_trader.log"
    
    # WebSocket
    WEBSOCKET_URL: str = "wss://stream.binance.com:9443/ws"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
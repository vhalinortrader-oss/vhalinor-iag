"""
Configuração do Módulo Autônomo LEXTRADER-IAG 4.0
"""

from typing import Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum


class ExecutionFrequency(str, Enum):
    """Frequências de execução pré-definidas"""
    REAL_TIME = "real_time"        # Execução contínua
    EVERY_MINUTE = "60"            # A cada minuto
    EVERY_5_MINUTES = "300"        # A cada 5 minutos
    EVERY_15_MINUTES = "900"       # A cada 15 minutos
    EVERY_HOUR = "3600"            # A cada hora
    EVERY_4_HOURS = "14400"        # A cada 4 horas
    EVERY_DAY = "86400"            # Diariamente
    EVERY_WEEK = "604800"          # Semanalmente
    EVERY_MONTH = "2592000"        # Mensalmente


@dataclass
class ActionConfig:
    """Configuração de uma ação autônoma"""
    name: str
    description: str
    action_type: str  # Referência a ActionType
    priority: str = "MEDIUM"
    frequency: str = ExecutionFrequency.EVERY_HOUR
    enabled: bool = True
    timeout: int = 300
    retry_count: int = 3
    dependencies: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModuleConfig:
    """Configuração completa do módulo autônomo"""
    # Configurações gerais
    module_name: str = "LEXTRADER-IAG Autonomous Module"
    version: str = "4.0.0"
    environment: str = "production"  # production, staging, development
    
    # Configurações de execução
    max_concurrent_actions: int = 10
    health_check_interval: int = 60
    performance_log_interval: int = 300
    
    # Configurações de logging
    log_level: str = "INFO"
    log_file: str = "autonomous_module.log"
    log_max_size: int = 10485760  # 10MB
    log_backup_count: int = 5
    
    # Configurações de alerta
    alert_channels: List[str] = field(default_factory=lambda: ["console"])
    email_alerts: bool = False
    email_recipients: List[str] = field(default_factory=list)
    slack_webhook: Optional[str] = None
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    
    # Configurações de monitoramento
    enable_resource_monitoring: bool = True
    cpu_threshold: float = 80.0  # %
    memory_threshold: float = 85.0  # %
    disk_threshold: float = 90.0  # %
    
    # Configurações de recuperação
    auto_recovery: bool = True
    max_failures_before_disable: int = 5
    failure_cooldown: int = 300  # segundos
    
    # Configurações de persistência
    persist_action_history: bool = True
    history_retention_days: int = 30
    backup_interval: int = 86400  # 24 horas
    
    # Ações configuradas
    actions: List[ActionConfig] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte configuração para dicionário"""
        return {
            "module_name": self.module_name,
            "version": self.version,
            "environment": self.environment,
            "max_concurrent_actions": self.max_concurrent_actions,
            "health_check_interval": self.health_check_interval,
            "actions": [
                {
                    "name": action.name,
                    "action_type": action.action_type,
                    "frequency": action.frequency,
                    "enabled": action.enabled
                }
                for action in self.actions
            ]
        }
    
    @classmethod
    def get_default_config(cls) -> 'ModuleConfig':
        """Retorna configuração padrão"""
        return cls(
            actions=[
                ActionConfig(
                    name="market_analysis",
                    description="Análise contínua de mercado",
                    action_type="MARKET_ANALYSIS",
                    priority="HIGH",
                    frequency=ExecutionFrequency.EVERY_5_MINUTES,
                    timeout=180
                ),
                ActionConfig(
                    name="portfolio_rebalance",
                    description="Rebalanceamento de portfólio",
                    action_type="PORTFOLIO_REBALANCE",
                    priority="MEDIUM",
                    frequency=ExecutionFrequency.EVERY_DAY,
                    timeout=600
                ),
                ActionConfig(
                    name="risk_assessment",
                    description="Avaliação de risco",
                    action_type="RISK_ASSESSMENT",
                    priority="CRITICAL",
                    frequency=ExecutionFrequency.EVERY_MINUTE,
                    timeout=120
                ),
                ActionConfig(
                    name="strategy_optimization",
                    description="Otimização de estratégias",
                    action_type="STRATEGY_OPTIMIZATION",
                    priority="LOW",
                    frequency=ExecutionFrequency.EVERY_WEEK,
                    timeout=1800
                ),
                ActionConfig(
                    name="data_collection",
                    description="Coleta de dados",
                    action_type="DATA_COLLECTION",
                    priority="MEDIUM",
                    frequency=ExecutionFrequency.EVERY_HOUR,
                    timeout=900
                ),
                ActionConfig(
                    name="model_training",
                    description="Treinamento de modelos",
                    action_type="MODEL_TRAINING",
                    priority="BACKGROUND",
                    frequency=ExecutionFrequency.EVERY_MONTH,
                    timeout=7200
                ),
            ]
        )


class ConfigManager:
    """Gerenciador de configuração"""
    
    def __init__(self, config_file: str = "autonomous_config.json"):
        self.config_file = config_file
        self.config: Optional[ModuleConfig] = None
    
    def load_config(self) -> ModuleConfig:
        """Carrega configuração do arquivo"""
        import json
        import os
        
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                data = json.load(f)
                # Converta o dicionário de volta para ModuleConfig
                # Implementação simplificada
                pass
        else:
            self.config = ModuleConfig.get_default_config()
            self.save_config()
        
        return self.config
    
    def save_config(self):
        """Salva configuração no arquivo"""
        import json
        
        if self.config:
            with open(self.config_file, 'w') as f:
                json.dump(self.config.to_dict(), f, indent=2)
    
    def update_config(self, updates: Dict[str, Any]):
        """Atualiza configuração"""
        if self.config:
            for key, value in updates.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
            self.save_config()
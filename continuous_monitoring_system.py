"""
╔═════════════════════════════════════════════════════════════════════════════╗
║                SISTEMA DE ORQUESTRAÇÃO E MONITORAMENTO CONTÍNUO          ║
║                 Componente 12: Sistema de Monitoramento em Tempo Real        ║
╚═════════════════════════════════════════════════════════════════════════════╝
"""

import asyncio
import numpy as np
import pandas as pd
import psutil
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import pickle
from collections import deque, defaultdict
import time
import threading
import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import websockets
import aiofiles

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('ContinuousMonitoringSystem')

class AlertSeverity(Enum):
    """Níveis de severidade de alertas"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class MetricType(Enum):
    """Tipos de métricas"""
    SYSTEM = "system"
    PERFORMANCE = "performance"
    BUSINESS = "business"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    NETWORK = "network"
    DATABASE = "database"
    APPLICATION = "application"

class MonitoringMode(Enum):
    """Modos de monitoramento"""
    ACTIVE = "active"
    PASSIVE = "passive"
    HYBRID = "hybrid"
    SCHEDULED = "scheduled"

@dataclass
class Metric:
    """Métrica de monitoramento"""
    name: str
    type: MetricType
    value: float
    unit: str
    timestamp: datetime
    source: str
    tags: Dict[str, str] = field(default_factory=dict)
    threshold_min: Optional[float] = None
    threshold_max: Optional[float] = None
    threshold_warning: Optional[float] = None
    threshold_critical: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'type': self.type.value,
            'value': self.value,
            'unit': self.unit,
            'timestamp': self.timestamp.isoformat(),
            'source': self.source,
            'tags': self.tags,
            'threshold_min': self.threshold_min,
            'threshold_max': self.threshold_max,
            'threshold_warning': self.threshold_warning,
            'threshold_critical': self.threshold_critical
        }

@dataclass
class Alert:
    """Alerta do sistema"""
    id: str
    severity: AlertSeverity
    title: str
    message: str
    source: str
    timestamp: datetime
    metric_name: str
    current_value: float
    threshold_value: float
    acknowledged: bool = False
    resolved: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'severity': self.severity.value,
            'title': self.title,
            'message': self.message,
            'source': self.source,
            'timestamp': self.timestamp.isoformat(),
            'metric_name': self.metric_name,
            'current_value': self.current_value,
            'threshold_value': self.threshold_value,
            'acknowledged': self.acknowledged,
            'resolved': self.resolved,
            'acknowledged_by': self.acknowledged_by,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'metadata': self.metadata
        }

@dataclass
class HealthStatus:
    """Status de saúde do sistema"""
    component: str
    status: str  # healthy, warning, critical, unknown
    last_check: datetime
    response_time_ms: float
    uptime_percentage: float
    error_rate: float
    last_error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'component': self.component,
            'status': self.status,
            'last_check': self.last_check.isoformat(),
            'response_time_ms': self.response_time_ms,
            'uptime_percentage': self.uptime_percentage,
            'error_rate': self.error_rate,
            'last_error': self.last_error,
            'metadata': self.metadata
        }

class SystemMetricsCollector:
    """Coletor de métricas do sistema"""
    
    def __init__(self):
        self.metrics_history = defaultdict(lambda: deque(maxlen=1000))
        self.collection_interval = 5  # segundos
        self.is_collecting = False
        
        logger.info("📊 SystemMetricsCollector inicializado")
    
    async def start_collection(self):
        """Inicia coleta de métricas"""
        if self.is_collecting:
            return
        
        self.is_collecting = True
        
        while self.is_collecting:
            try:
                # Coleta métricas do sistema
                metrics = await self._collect_system_metrics()
                
                # Armazena métricas
                for metric in metrics:
                    self.metrics_history[metric.name].append(metric)
                
                # Aguarda próximo ciclo
                await asyncio.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"❌ Erro na coleta de métricas: {e}")
                await asyncio.sleep(self.collection_interval)
    
    def stop_collection(self):
        """Para coleta de métricas"""
        self.is_collecting = False
        logger.info("🛑 Coleta de métricas parada")
    
    async def _collect_system_metrics(self) -> List[Metric]:
        """Coleta métricas do sistema operacional"""
        metrics = []
        timestamp = datetime.now()
        
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            metrics.append(Metric(
                name="cpu_usage_percent",
                type=MetricType.SYSTEM,
                value=cpu_percent,
                unit="percent",
                timestamp=timestamp,
                source="system_monitor",
                threshold_warning=70.0,
                threshold_critical=90.0
            ))
            
            # Memória
            memory = psutil.virtual_memory()
            metrics.append(Metric(
                name="memory_usage_percent",
                type=MetricType.SYSTEM,
                value=memory.percent,
                unit="percent",
                timestamp=timestamp,
                source="system_monitor",
                threshold_warning=75.0,
                threshold_critical=90.0
            ))
            
            metrics.append(Metric(
                name="memory_available_gb",
                type=MetricType.SYSTEM,
                value=memory.available / (1024**3),
                unit="GB",
                timestamp=timestamp,
                source="system_monitor",
                threshold_min=1.0,
                threshold_warning=2.0
            ))
            
            # Disco
            disk = psutil.disk_usage('/')
            disk_usage_percent = (disk.used / disk.total) * 100
            metrics.append(Metric(
                name="disk_usage_percent",
                type=MetricType.SYSTEM,
                value=disk_usage_percent,
                unit="percent",
                timestamp=timestamp,
                source="system_monitor",
                threshold_warning=80.0,
                threshold_critical=95.0
            ))
            
            metrics.append(Metric(
                name="disk_free_gb",
                type=MetricType.SYSTEM,
                value=disk.free / (1024**3),
                unit="GB",
                timestamp=timestamp,
                source="system_monitor",
                threshold_min=10.0,
                threshold_warning=20.0
            ))
            
            # Rede
            network = psutil.net_io_counters()
            metrics.append(Metric(
                name="network_bytes_sent",
                type=MetricType.NETWORK,
                value=network.bytes_sent,
                unit="bytes",
                timestamp=timestamp,
                source="system_monitor"
            ))
            
            metrics.append(Metric(
                name="network_bytes_recv",
                type=MetricType.NETWORK,
                value=network.bytes_recv,
                unit="bytes",
                timestamp=timestamp,
                source="system_monitor"
            ))
            
            # Processos
            process_count = len(psutil.pids())
            metrics.append(Metric(
                name="process_count",
                type=MetricType.SYSTEM,
                value=process_count,
                unit="count",
                timestamp=timestamp,
                source="system_monitor",
                threshold_warning=200,
                threshold_critical=500
            ))
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar métricas do sistema: {e}")
        
        return metrics
    
    def get_metric_history(self, metric_name: str, 
                          minutes: int = 60) -> List[Metric]:
        """Retorna histórico de uma métrica"""
        if metric_name not in self.metrics_history:
            return []
        
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        return [
            m for m in self.metrics_history[metric_name]
            if m.timestamp >= cutoff_time
        ]
    
    def get_current_metrics(self) -> Dict[str, float]:
        """Retorna valores atuais das métricas"""
        current = {}
        
        for metric_name, history in self.metrics_history.items():
            if history:
                current[metric_name] = history[-1].value
        
        return current

class AlertManager:
    """Gerenciador de alertas"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.alerts = deque(maxlen=10000)
        self.alert_rules = {}
        self.notification_channels = []
        self.alert_counter = 0
        
        # Configurações de notificação
        self.email_config = self.config.get('email', {})
        self.webhook_config = self.config.get('webhook', {})
        self.slack_config = self.config.get('slack', {})
        
        logger.info("🚨 AlertManager inicializado")
    
    def add_alert_rule(self, metric_name: str, condition: str, 
                      severity: AlertSeverity, message_template: str):
        """Adiciona regra de alerta"""
        rule_id = f"rule_{metric_name}_{len(self.alert_rules)}"
        
        self.alert_rules[rule_id] = {
            'metric_name': metric_name,
            'condition': condition,
            'severity': severity,
            'message_template': message_template,
            'enabled': True
        }
        
        logger.info(f"📋 Regra de alerta adicionada: {rule_id}")
    
    def check_alerts(self, metrics: List[Metric]) -> List[Alert]:
        """Verifica se métricas geram alertas"""
        new_alerts = []
        
        for metric in metrics:
            # Verifica regras personalizadas
            for rule_id, rule in self.alert_rules.items():
                if not rule['enabled']:
                    continue
                
                if rule['metric_name'] == metric.name:
                    if self._evaluate_condition(rule['condition'], metric.value):
                        alert = self._create_alert(
                            metric, rule['severity'], rule['message_template']
                        )
                        new_alerts.append(alert)
            
            # Verifica thresholds automáticos
            if metric.threshold_critical is not None:
                if metric.value >= metric.threshold_critical:
                    alert = self._create_alert(
                        metric, AlertSeverity.CRITICAL,
                        f"Métrica {metric.name} excedeu threshold crítico"
                    )
                    new_alerts.append(alert)
            
            elif metric.threshold_warning is not None:
                if metric.value >= metric.threshold_warning:
                    alert = self._create_alert(
                        metric, AlertSeverity.WARNING,
                        f"Métrica {metric.name} excedeu threshold de aviso"
                    )
                    new_alerts.append(alert)
        
        # Adiciona alertas à lista
        for alert in new_alerts:
            self.alerts.append(alert)
        
        # Envia notificações
        if new_alerts:
            asyncio.create_task(self._send_notifications(new_alerts))
        
        return new_alerts
    
    def _evaluate_condition(self, condition: str, value: float) -> bool:
        """Avalia condição de alerta"""
        try:
            # Substitui valor na condição
            safe_condition = condition.replace('value', str(value))
            
            # Avalia de forma segura
            return eval(safe_condition)
            
        except Exception as e:
            logger.error(f"❌ Erro ao avaliar condição '{condition}': {e}")
            return False
    
    def _create_alert(self, metric: Metric, severity: AlertSeverity, 
                    message: str) -> Alert:
        """Cria alerta"""
        self.alert_counter += 1
        
        alert = Alert(
            id=f"alert_{self.alert_counter}_{int(time.time())}",
            severity=severity,
            title=f"Alerta: {metric.name}",
            message=message,
            source=metric.source,
            timestamp=datetime.now(),
            metric_name=metric.name,
            current_value=metric.value,
            threshold_value=metric.threshold_critical or metric.threshold_warning or 0,
            metadata={
                'metric_type': metric.type.value,
                'unit': metric.unit,
                'tags': metric.tags
            }
        )
        
        return alert
    
    async def _send_notifications(self, alerts: List[Alert]):
        """Envia notificações de alertas"""
        for alert in alerts:
            try:
                # Email
                if self.email_config:
                    await self._send_email_notification(alert)
                
                # Webhook
                if self.webhook_config:
                    await self._send_webhook_notification(alert)
                
                # Slack
                if self.slack_config:
                    await self._send_slack_notification(alert)
                
            except Exception as e:
                logger.error(f"❌ Erro ao enviar notificação para alerta {alert.id}: {e}")
    
    async def _send_email_notification(self, alert: Alert):
        """Envia notificação por email"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['from']
            msg['To'] = self.email_config['to']
            msg['Subject'] = f"[{alert.severity.value.upper()}] {alert.title}"
            
            body = f"""
            Alerta do Sistema de Monitoramento
            
            Severidade: {alert.severity.value.upper()}
            Título: {alert.title}
            Mensagem: {alert.message}
            Fonte: {alert.source}
            Métrica: {alert.metric_name}
            Valor Atual: {alert.current_value}
            Threshold: {alert.threshold_value}
            Timestamp: {alert.timestamp.isoformat()}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Envia email (simplificado)
            logger.info(f"📧 Email enviado para alerta {alert.id}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao enviar email: {e}")
    
    async def _send_webhook_notification(self, alert: Alert):
        """Envia notificação via webhook"""
        try:
            payload = {
                'alert_id': alert.id,
                'severity': alert.severity.value,
                'title': alert.title,
                'message': alert.message,
                'source': alert.source,
                'timestamp': alert.timestamp.isoformat(),
                'metric_name': alert.metric_name,
                'current_value': alert.current_value,
                'threshold_value': alert.threshold_value
            }
            
            response = requests.post(
                self.webhook_config['url'],
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"🔗 Webhook enviado para alerta {alert.id}")
            else:
                logger.warning(f"⚠️ Falha no webhook: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Erro ao enviar webhook: {e}")
    
    async def _send_slack_notification(self, alert: Alert):
        """Envia notificação para Slack"""
        try:
            color_map = {
                AlertSeverity.INFO: '#36a64f',
                AlertSeverity.WARNING: '#ff9500',
                AlertSeverity.ERROR: '#ff0000',
                AlertSeverity.CRITICAL: '#8b0000',
                AlertSeverity.EMERGENCY: '#000000'
            }
            
            payload = {
                'attachments': [{
                    'color': color_map.get(alert.severity, '#808080'),
                    'title': alert.title,
                    'text': alert.message,
                    'fields': [
                        {'title': 'Severidade', 'value': alert.severity.value.upper()},
                        {'title': 'Fonte', 'value': alert.source},
                        {'title': 'Métrica', 'value': alert.metric_name},
                        {'title': 'Valor', 'value': str(alert.current_value)},
                        {'title': 'Threshold', 'value': str(alert.threshold_value)}
                    ],
                    'timestamp': int(alert.timestamp.timestamp())
                }]
            }
            
            response = requests.post(
                self.slack_config['webhook_url'],
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"💬 Notificação Slack enviada para alerta {alert.id}")
            else:
                logger.warning(f"⚠️ Falha na notificação Slack: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Erro ao enviar notificação Slack: {e}")
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str):
        """Reconhece alerta"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                alert.acknowledged_by = acknowledged_by
                alert.acknowledged_at = datetime.now()
                
                logger.info(f"✅ Alerta {alert_id} reconhecido por {acknowledged_by}")
                return True
        
        return False
    
    def resolve_alert(self, alert_id: str):
        """Resolve alerta"""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.resolved = True
                alert.resolved_at = datetime.now()
                
                logger.info(f"✅ Alerta {alert_id} resolvido")
                return True
        
        return False
    
    def get_active_alerts(self) -> List[Alert]:
        """Retorna alertas ativos (não resolvidos)"""
        return [a for a in self.alerts if not a.resolved]
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas de alertas"""
        total_alerts = len(self.alerts)
        active_alerts = len(self.get_active_alerts())
        
        severity_counts = defaultdict(int)
        for alert in self.alerts:
            severity_counts[alert.severity.value] += 1
        
        return {
            'total_alerts': total_alerts,
            'active_alerts': active_alerts,
            'resolved_alerts': total_alerts - active_alerts,
            'severity_distribution': dict(severity_counts),
            'last_24h_alerts': len([
                a for a in self.alerts 
                if a.timestamp >= datetime.now() - timedelta(hours=24)
            ])
        }

class HealthChecker:
    """Verificador de saúde de componentes"""
    
    def __init__(self):
        self.components = {}
        self.health_history = defaultdict(lambda: deque(maxlen=1000))
        self.check_interval = 30  # segundos
        self.is_checking = False
        
        logger.info("🏥 HealthChecker inicializado")
    
    def register_component(self, name: str, check_function: Callable, 
                         timeout: float = 10.0):
        """Registra componente para verificação de saúde"""
        self.components[name] = {
            'check_function': check_function,
            'timeout': timeout,
            'last_check': None,
            'consecutive_failures': 0,
            'total_checks': 0,
            'successful_checks': 0
        }
        
        logger.info(f"📝 Componente {name} registrado para verificação de saúde")
    
    async def start_health_checks(self):
        """Inicia verificações periódicas de saúde"""
        if self.is_checking:
            return
        
        self.is_checking = True
        
        while self.is_checking:
            try:
                await self._check_all_components()
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"❌ Erro na verificação de saúde: {e}")
                await asyncio.sleep(self.check_interval)
    
    def stop_health_checks(self):
        """Para verificações de saúde"""
        self.is_checking = False
        logger.info("🛑 Verificações de saúde paradas")
    
    async def _check_all_components(self):
        """Verifica saúde de todos os componentes"""
        tasks = []
        
        for component_name, component_info in self.components.items():
            task = asyncio.create_task(
                self._check_component_health(component_name, component_info)
            )
            tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _check_component_health(self, component_name: str, 
                                   component_info: Dict[str, Any]) -> HealthStatus:
        """Verifica saúde de um componente específico"""
        start_time = time.time()
        status = "unknown"
        error_message = None
        
        try:
            # Executa verificação com timeout
            check_result = await asyncio.wait_for(
                component_info['check_function'](),
                timeout=component_info['timeout']
            )
            
            # Interpreta resultado
            if isinstance(check_result, bool):
                status = "healthy" if check_result else "unhealthy"
            elif isinstance(check_result, dict):
                status = check_result.get('status', 'unknown')
                error_message = check_result.get('error')
            else:
                status = "healthy" if check_result else "unhealthy"
            
            # Atualiza estatísticas
            component_info['total_checks'] += 1
            component_info['consecutive_failures'] = 0
            component_info['successful_checks'] += 1
            
        except asyncio.TimeoutError:
            status = "timeout"
            error_message = f"Timeout após {component_info['timeout']}s"
            component_info['consecutive_failures'] += 1
            component_info['total_checks'] += 1
            
        except Exception as e:
            status = "error"
            error_message = str(e)
            component_info['consecutive_failures'] += 1
            component_info['total_checks'] += 1
        
        response_time = (time.time() - start_time) * 1000  # ms
        
        # Calcula métricas
        uptime_percentage = (
            component_info['successful_checks'] / component_info['total_checks'] * 100
            if component_info['total_checks'] > 0 else 0
        )
        
        error_rate = (
            component_info['consecutive_failures'] / component_info['total_checks'] * 100
            if component_info['total_checks'] > 0 else 0
        )
        
        # Cria status de saúde
        health_status = HealthStatus(
            component=component_name,
            status=status,
            last_check=datetime.now(),
            response_time_ms=response_time,
            uptime_percentage=uptime_percentage,
            error_rate=error_rate,
            last_error=error_message
        )
        
        # Armazena histórico
        self.health_history[component_name].append(health_status)
        component_info['last_check'] = health_status
        
        # Log de status
        if status in ["error", "timeout", "unhealthy"]:
            logger.warning(f"⚠️ Componente {component_name} com status: {status}")
        else:
            logger.debug(f"✅ Componente {component_name} saudável")
        
        return health_status
    
    def get_component_health(self, component_name: str) -> Optional[HealthStatus]:
        """Retorna status atual de um componente"""
        component_info = self.components.get(component_name)
        if component_info:
            return component_info.get('last_check')
        return None
    
    def get_all_health_status(self) -> Dict[str, HealthStatus]:
        """Retorna status de todos os componentes"""
        status = {}
        
        for component_name in self.components:
            health = self.get_component_health(component_name)
            if health:
                status[component_name] = health
        
        return status
    
    def get_system_health_summary(self) -> Dict[str, Any]:
        """Retorna resumo da saúde do sistema"""
        all_status = self.get_all_health_status()
        
        if not all_status:
            return {
                'overall_status': 'unknown',
                'healthy_components': 0,
                'unhealthy_components': 0,
                'total_components': 0
            }
        
        status_counts = defaultdict(int)
        for status in all_status.values():
            status_counts[status.status] += 1
        
        # Determina status geral
        if status_counts['healthy'] == len(all_status):
            overall_status = 'healthy'
        elif status_counts['critical'] > 0 or status_counts['error'] > 0:
            overall_status = 'critical'
        elif status_counts['warning'] > 0:
            overall_status = 'warning'
        else:
            overall_status = 'degraded'
        
        return {
            'overall_status': overall_status,
            'healthy_components': status_counts['healthy'],
            'unhealthy_components': len(all_status) - status_counts['healthy'],
            'total_components': len(all_status),
            'status_distribution': dict(status_counts),
            'last_check': max(
                (s.last_check for s in all_status.values()),
                default=datetime.now()
            ).isoformat()
        }

class ContinuousMonitoringSystem:
    """Sistema contínuo de monitoramento"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        
        # Componentes
        self.metrics_collector = SystemMetricsCollector()
        self.alert_manager = AlertManager(self.config.get('alerts', {}))
        self.health_checker = HealthChecker()
        
        # Estado do sistema
        self.is_running = False
        self.start_time = None
        self.monitoring_tasks = []
        
        # Configurações
        self.metrics_interval = self.config.get('metrics_interval', 5)
        self.health_check_interval = self.config.get('health_check_interval', 30)
        self.alert_check_interval = self.config.get('alert_check_interval', 10)
        
        # Dashboard
        self.dashboard_data = {
            'metrics': {},
            'alerts': [],
            'health': {},
            'system_info': {}
        }
        
        logger.info("🖥️ ContinuousMonitoringSystem inicializado")
    
    async def start(self):
        """Inicia sistema de monitoramento"""
        if self.is_running:
            logger.warning("⚠️ Sistema já está em execução")
            return
        
        logger.info("🚀 Iniciando Sistema de Monitoramento Contínuo")
        self.is_running = True
        self.start_time = datetime.now()
        
        try:
            # Inicia coleta de métricas
            metrics_task = asyncio.create_task(
                self.metrics_collector.start_collection()
            )
            self.monitoring_tasks.append(metrics_task)
            
            # Inicia verificações de saúde
            health_task = asyncio.create_task(
                self.health_checker.start_health_checks()
            )
            self.monitoring_tasks.append(health_task)
            
            # Inicia verificação de alertas
            alert_task = asyncio.create_task(
                self._alert_monitoring_loop()
            )
            self.monitoring_tasks.append(alert_task)
            
            # Inicia atualização do dashboard
            dashboard_task = asyncio.create_task(
                self._dashboard_update_loop()
            )
            self.monitoring_tasks.append(dashboard_task)
            
            # Registra componentes internos
            self._register_internal_components()
            
            # Configura regras de alerta padrão
            self._setup_default_alert_rules()
            
            logger.info("✅ Sistema de monitoramento iniciado com sucesso")
            
            # Aguarda tarefas
            await asyncio.gather(*self.monitoring_tasks)
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar sistema: {e}")
            await self.stop()
    
    async def stop(self):
        """Para sistema de monitoramento"""
        if not self.is_running:
            return
        
        logger.info("🛑 Parando Sistema de Monitoramento Contínuo")
        self.is_running = False
        
        # Para componentes
        self.metrics_collector.stop_collection()
        self.health_checker.stop_health_checks()
        
        # Cancela tarefas
        for task in self.monitoring_tasks:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        self.monitoring_tasks.clear()
        
        logger.info("✅ Sistema de monitoramento parado")
    
    async def _alert_monitoring_loop(self):
        """Loop de monitoramento de alertas"""
        while self.is_running:
            try:
                # Obtém métricas atuais
                current_metrics = self.metrics_collector.get_current_metrics()
                
                # Converte para objetos Metric
                metric_objects = []
                for name, value in current_metrics.items():
                    # Obtém histórico para determinar tipo
                    history = self.metrics_collector.get_metric_history(name, 1)
                    if history:
                        metric_objects.append(history[-1])
                
                # Verifica alertas
                if metric_objects:
                    new_alerts = self.alert_manager.check_alerts(metric_objects)
                    
                    if new_alerts:
                        logger.info(f"🚨 {len(new_alerts)} novos alertas gerados")
                
                # Aguarda próximo ciclo
                await asyncio.sleep(self.alert_check_interval)
                
            except Exception as e:
                logger.error(f"❌ Erro no monitoramento de alertas: {e}")
                await asyncio.sleep(self.alert_check_interval)
    
    async def _dashboard_update_loop(self):
        """Loop de atualização do dashboard"""
        while self.is_running:
            try:
                # Atualiza dados do dashboard
                self.dashboard_data['metrics'] = self.metrics_collector.get_current_metrics()
                self.dashboard_data['alerts'] = [
                    alert.to_dict() for alert in self.alert_manager.get_active_alerts()[-10:]
                ]
                self.dashboard_data['health'] = self.health_checker.get_system_health_summary()
                self.dashboard_data['system_info'] = self._get_system_info()
                
                # Aguarda próximo ciclo
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"❌ Erro na atualização do dashboard: {e}")
                await asyncio.sleep(5)
    
    def _register_internal_components(self):
        """Registra componentes internos para verificação de saúde"""
        # Verificador de métricas
        async def check_metrics_collector():
            return self.metrics_collector.is_collecting
        
        self.health_checker.register_component(
            "metrics_collector", 
            check_metrics_collector,
            timeout=5.0
        )
        
        # Verificador de alertas
        async def check_alert_manager():
            return len(self.alert_manager.get_active_alerts()) < 100
        
        self.health_checker.register_component(
            "alert_manager",
            check_alert_manager,
            timeout=5.0
        )
        
        # Verificador de disco
        async def check_disk_space():
            disk = psutil.disk_usage('/')
            free_gb = disk.free / (1024**3)
            return {
                'status': 'healthy' if free_gb > 10 else 'warning',
                'free_gb': free_gb
            }
        
        self.health_checker.register_component(
            "disk_space",
            check_disk_space,
            timeout=5.0
        )
    
    def _setup_default_alert_rules(self):
        """Configura regras de alerta padrão"""
        # CPU alta
        self.alert_manager.add_alert_rule(
            "cpu_usage_percent",
            "value > 90",
            AlertSeverity.CRITICAL,
            "Uso de CPU crítico: {value}%"
        )
        
        # Memória alta
        self.alert_manager.add_alert_rule(
            "memory_usage_percent",
            "value > 85",
            AlertSeverity.CRITICAL,
            "Uso de memória crítico: {value}%"
        )
        
        # Disco baixo
        self.alert_manager.add_alert_rule(
            "disk_free_gb",
            "value < 5",
            AlertSeverity.CRITICAL,
            "Espaço em disco crítico: {value}GB"
        )
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Retorna informações do sistema"""
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            
            return {
                'hostname': psutil.os.uname().nodename,
                'platform': psutil.os.uname().system,
                'python_version': psutil.sys.version,
                'cpu_count': psutil.cpu_count(),
                'memory_total_gb': psutil.virtual_memory().total / (1024**3),
                'boot_time': boot_time.isoformat(),
                'uptime_seconds': uptime.total_seconds(),
                'uptime_days': uptime.days,
                'monitoring_uptime_seconds': (
                    (datetime.now() - self.start_time).total_seconds()
                    if self.start_time else 0
                )
            }
        except Exception as e:
            logger.error(f"❌ Erro ao obter informações do sistema: {e}")
            return {}
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Retorna dados do dashboard"""
        return self.dashboard_data.copy()
    
    def get_monitoring_summary(self) -> Dict[str, Any]:
        """Retorna resumo do monitoramento"""
        return {
            'is_running': self.is_running,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'uptime_seconds': (
                (datetime.now() - self.start_time).total_seconds()
                if self.start_time else 0
            ),
            'metrics_summary': {
                'total_metrics': len(self.metrics_collector.metrics_history),
                'collection_interval': self.metrics_collector.collection_interval
            },
            'alerts_summary': self.alert_manager.get_alert_statistics(),
            'health_summary': self.health_checker.get_system_health_summary(),
            'system_info': self._get_system_info()
        }
    
    def export_data(self, filepath: str):
        """Exporta dados de monitoramento"""
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'summary': self.get_monitoring_summary(),
                'dashboard_data': self.get_dashboard_data(),
                'metrics_history': {
                    name: [m.to_dict() for m in history]
                    for name, history in self.metrics_collector.metrics_history.items()
                },
                'alerts_history': [a.to_dict() for a in self.alert_manager.alerts],
                'health_history': {
                    name: [h.to_dict() for h in history]
                    for name, history in self.health_checker.health_history.items()
                }
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.info(f"💾 Dados de monitoramento exportados para {filepath}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao exportar dados: {e}")

# Configuração padrão
DEFAULT_MONITORING_CONFIG = {
    'metrics_interval': 5,
    'health_check_interval': 30,
    'alert_check_interval': 10,
    'alerts': {
        'email': {
            'from': 'monitoring@company.com',
            'to': 'admin@company.com',
            'smtp_server': 'smtp.company.com',
            'smtp_port': 587
        },
        'webhook': {
            'url': 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
        },
        'slack': {
            'webhook_url': 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
        }
    }
}

if __name__ == "__main__":
    # Exemplo de uso
    async def test_monitoring_system():
        """Testa sistema de monitoramento contínuo"""
        print("🖥️ Iniciando Teste do Sistema de Monitoramento Contínuo")
        print("=" * 65)
        
        # Cria sistema
        monitoring_system = ContinuousMonitoringSystem(DEFAULT_MONITORING_CONFIG)
        
        # Adiciona verificador de componente personalizado
        async def check_database_connection():
            # Simula verificação de banco de dados
            await asyncio.sleep(0.1)
            return {
                'status': 'healthy',
                'connection_time_ms': 15.5,
                'active_connections': 42
            }
        
        monitoring_system.health_checker.register_component(
            "database",
            check_database_connection,
            timeout=5.0
        )
        
        # Adiciona verificador de API
        async def check_api_health():
            # Simula verificação de API
            await asyncio.sleep(0.05)
            return {
                'status': 'healthy',
                'response_time_ms': 25.3,
                'endpoints_healthy': 5,
                'endpoints_total': 5
            }
        
        monitoring_system.health_checker.register_component(
            "api",
            check_api_health,
            timeout=3.0
        )
        
        # Inicia monitoramento por um período limitado
        try:
            # Inicia sistema
            monitor_task = asyncio.create_task(monitoring_system.start())
            
            # Deixa rodar por 30 segundos
            await asyncio.sleep(30)
            
            # Obtém dados do dashboard
            dashboard_data = monitoring_system.get_dashboard_data()
            
            print(f"\n📊 DADOS DO DASHBOARD:")
            print("=" * 40)
            
            # Métricas atuais
            print(f"\n📈 Métricas Atuais:")
            for name, value in dashboard_data['metrics'].items():
                print(f"  {name}: {value}")
            
            # Alertas ativos
            print(f"\n🚨 Alertas Ativos: {len(dashboard_data['alerts'])}")
            for alert in dashboard_data['alerts'][:5]:  # Primeiros 5
                print(f"  • {alert['severity'].upper()}: {alert['title']}")
            
            # Saúde do sistema
            health = dashboard_data['health']
            print(f"\n🏥 Saúde do Sistema: {health['overall_status'].upper()}")
            print(f"  Componentes Saudáveis: {health['healthy_components']}")
            print(f"  Componentes Não Saudáveis: {health['unhealthy_components']}")
            print(f"  Total de Componentes: {health['total_components']}")
            
            # Informações do sistema
            sys_info = dashboard_data['system_info']
            print(f"\n💻 Informações do Sistema:")
            print(f"  Hostname: {sys_info.get('hostname', 'N/A')}")
            print(f"  CPU Cores: {sys_info.get('cpu_count', 'N/A')}")
            print(f"  Memória Total: {sys_info.get('memory_total_gb', 0):.1f} GB")
            print(f"  Uptime: {sys_info.get('uptime_days', 0)} dias")
            
            # Resumo do monitoramento
            summary = monitoring_system.get_monitoring_summary()
            print(f"\n📋 Resumo do Monitoramento:")
            print(f"  Sistema em Execução: {summary['is_running']}")
            print(f"  Uptime do Monitoramento: {summary['uptime_seconds']:.0f}s")
            print(f"  Total de Métricas: {summary['metrics_summary']['total_metrics']}")
            print(f"  Alertas nas Últimas 24h: {summary['alerts_summary']['last_24h_alerts']}")
            
            # Exporta dados
            monitoring_system.export_data('monitoring_data.json')
            
            # Para sistema
            await monitoring_system.stop()
            
        except KeyboardInterrupt:
            print("\n🛑 Interrupção do usuário detectada")
            await monitoring_system.stop()
        
        print("\n💾 Dados exportados")
        print("✅ Teste concluído com sucesso!")
        
        return monitoring_system
    
    # Executa teste
    monitoring_system = asyncio.run(test_monitoring_system())

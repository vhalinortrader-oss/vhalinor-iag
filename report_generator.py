"""
Automated Report Generator - Sistema de Relatórios Automatizados
=============================================================
Geração de relatórios completos e automatizados para o sistema VHALINOR
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import os
from pathlib import Path
import hashlib

# Importações condicionais
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

from config import settings
from core import get_logger, log_execution


class ReportType(str, Enum):
    """Tipos de relatórios disponíveis"""
    SYSTEM_PERFORMANCE = "system_performance"
    TRADING_ANALYSIS = "trading_analysis"
    AI_METRICS = "ai_metrics"
    AUTOMATION_SUMMARY = "automation_summary"
    PREDICTION_ACCURACY = "prediction_accuracy"
    COGNITIVE_ANALYSIS = "cognitive_analysis"
    NEURAL_ARCHITECTURE = "neural_architecture"
    COMPREHENSIVE = "comprehensive"
    DAILY_SUMMARY = "daily_summary"
    WEEKLY_SUMMARY = "weekly_summary"
    MONTHLY_SUMMARY = "monthly_summary"


class ReportFormat(str, Enum):
    """Formatos de saída dos relatórios"""
    JSON = "json"
    HTML = "html"
    PDF = "pdf"
    CSV = "csv"
    MARKDOWN = "markdown"
    EXCEL = "excel"


@dataclass
class ReportSection:
    """Seção de relatório"""
    title: str
    content: Any
    section_type: str = "text"
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'title': self.title,
            'content': self.content,
            'section_type': self.section_type,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class ReportConfig:
    """Configuração de relatório"""
    report_type: ReportType
    format: ReportFormat = ReportFormat.JSON
    include_sections: List[str] = field(default_factory=list)
    exclude_sections: List[str] = field(default_factory=list)
    date_range: Optional[Tuple[datetime, datetime]] = None
    filters: Dict[str, Any] = field(default_factory=dict)
    output_path: Optional[str] = None
    template: Optional[str] = None
    custom_params: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'report_type': self.report_type.value,
            'format': self.format.value,
            'include_sections': self.include_sections,
            'exclude_sections': self.exclude_sections,
            'date_range': [d.isoformat() for d in self.date_range] if self.date_range else None,
            'filters': self.filters,
            'output_path': self.output_path,
            'template': self.template,
            'custom_params': self.custom_params
        }


class ReportDataCollector:
    """Coletor de dados para relatórios"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.reports.collector", "data_collector")
        self.data_cache = {}
        self.collection_history = []
    
    async def collect_system_metrics(self, date_range: Optional[Tuple[datetime, datetime]] = None) -> Dict[str, Any]:
        """Coleta métricas do sistema"""
        # Mock data collection - em produção, coletaria dados reais
        metrics = {
            'cpu_usage': 45.2,
            'memory_usage': 67.8,
            'disk_usage': 34.1,
            'network_io': {'bytes_sent': 1024000, 'bytes_received': 2048000},
            'active_processes': 156,
            'uptime_hours': 72.5,
            'error_count': 3,
            'warning_count': 12,
            'timestamp': datetime.now().isoformat()
        }
        
        if date_range:
            # Simular dados históricos
            start_date, end_date = date_range
            days = (end_date - start_date).days
            historical_data = []
            
            for i in range(days + 1):
                current_date = start_date + timedelta(days=i)
                daily_metrics = metrics.copy()
                daily_metrics['timestamp'] = current_date.isoformat()
                daily_metrics['cpu_usage'] = max(10, min(90, daily_metrics['cpu_usage'] + random.uniform(-10, 10)))
                daily_metrics['memory_usage'] = max(20, min(95, daily_metrics['memory_usage'] + random.uniform(-5, 5)))
                historical_data.append(daily_metrics)
            
            return {'current': metrics, 'historical': historical_data}
        
        return metrics
    
    async def collect_trading_data(self, date_range: Optional[Tuple[datetime, datetime]] = None) -> Dict[str, Any]:
        """Coleta dados de trading"""
        trading_data = {
            'total_trades': 245,
            'profitable_trades': 167,
            'total_pnl': 12500.50,
            'win_rate': 68.16,
            'sharpe_ratio': 1.85,
            'max_drawdown': -8.3,
            'active_positions': 3,
            'portfolio_value': 112500.50,
            'total_volume': 2500000.0,
            'avg_trade_duration': 4.2,
            'best_trade': 850.25,
            'worst_trade': -125.50,
            'symbols_traded': ['BTC/USDT', 'ETH/USDT', 'BNB/USDT'],
            'timestamp': datetime.now().isoformat()
        }
        
        if date_range:
            # Simular dados históricos de trading
            start_date, end_date = date_range
            daily_trading = []
            
            for i in range((end_date - start_date).days + 1):
                current_date = start_date + timedelta(days=i)
                daily_data = trading_data.copy()
                daily_data['timestamp'] = current_date.isoformat()
                daily_data['total_trades'] = max(0, daily_data['total_trades'] + random.randint(-5, 10))
                daily_data['total_pnl'] += random.uniform(-500, 800)
                daily_trading.append(daily_data)
            
            return {'current': trading_data, 'historical': daily_trading}
        
        return trading_data
    
    async def collect_ai_metrics(self, date_range: Optional[Tuple[datetime, datetime]] = None) -> Dict[str, Any]:
        """Coleta métricas de IA"""
        ai_metrics = {
            'model_predictions': 15847,
            'prediction_accuracy': 0.784,
            'processing_time_avg': 0.125,
            'models_active': 5,
            'model_performance': {
                'lstm': {'accuracy': 0.81, 'f1_score': 0.79},
                'random_forest': {'accuracy': 0.76, 'f1_score': 0.74},
                'gradient_boosting': {'accuracy': 0.78, 'f1_score': 0.77}
            },
            'feature_importance': {
                'price_momentum': 0.23,
                'volume': 0.18,
                'technical_indicators': 0.31,
                'market_sentiment': 0.15,
                'volatility': 0.13
            },
            'training_sessions': 12,
            'model_updates': 8,
            'timestamp': datetime.now().isoformat()
        }
        
        if date_range:
            # Simular dados históricos de IA
            start_date, end_date = date_range
            historical_ai = []
            
            for i in range((end_date - start_date).days + 1):
                current_date = start_date + timedelta(days=i)
                daily_ai = ai_metrics.copy()
                daily_ai['timestamp'] = current_date.isoformat()
                daily_ai['prediction_accuracy'] = max(0.6, min(0.95, daily_ai['prediction_accuracy'] + random.uniform(-0.05, 0.05)))
                historical_ai.append(daily_ai)
            
            return {'current': ai_metrics, 'historical': historical_ai}
        
        return ai_metrics
    
    async def collect_automation_data(self, date_range: Optional[Tuple[datetime, datetime]] = None) -> Dict[str, Any]:
        """Coleta dados de automação"""
        automation_data = {
            'tasks_executed': 1258,
            'tasks_successful': 1198,
            'success_rate': 95.23,
            'automation_types': {
                'web_scraping': 456,
                'form_filling': 324,
                'data_extraction': 278,
                'report_generation': 200
            },
            'error_types': {
                'timeout': 15,
                'element_not_found': 28,
                'network_error': 12,
                'authentication_error': 5
            },
            'avg_execution_time': 2.34,
            'total_execution_time': 2947.32,
            'active_automations': 8,
            'scheduled_tasks': 24,
            'timestamp': datetime.now().isoformat()
        }
        
        if date_range:
            # Simular dados históricos de automação
            start_date, end_date = date_range
            historical_automation = []
            
            for i in range((end_date - start_date).days + 1):
                current_date = start_date + timedelta(days=i)
                daily_automation = automation_data.copy()
                daily_automation['timestamp'] = current_date.isoformat()
                daily_automation['tasks_executed'] = max(0, daily_automation['tasks_executed'] + random.randint(-20, 50))
                daily_automation['success_rate'] = max(0.85, min(0.99, daily_automation['success_rate'] + random.uniform(-0.02, 0.02)))
                historical_automation.append(daily_automation)
            
            return {'current': automation_data, 'historical': historical_automation}
        
        return automation_data
    
    async def collect_cognitive_data(self, date_range: Optional[Tuple[datetime, datetime]] = None) -> Dict[str, Any]:
        """Coleta dados cognitivos"""
        cognitive_data = {
            'total_interactions': 8456,
            'avg_response_time': 0.089,
            'memory_items': 12458,
            'reasoning_steps': 33824,
            'conversation_sessions': 2147,
            'user_satisfaction': 4.6,
            'intent_classification_accuracy': 0.92,
            'context_retention_rate': 0.87,
            'memory_types': {
                'short_term': 3456,
                'long_term': 7856,
                'episodic': 1146,
                'working': 234
            },
            'reasoning_patterns': {
                'chain_of_thought': 0.45,
                'step_by_step': 0.32,
                'analogical': 0.15,
                'causal': 0.08
            },
            'timestamp': datetime.now().isoformat()
        }
        
        if date_range:
            # Simular dados históricos cognitivos
            start_date, end_date = date_range
            historical_cognitive = []
            
            for i in range((end_date - start_date).days + 1):
                current_date = start_date + timedelta(days=i)
                daily_cognitive = cognitive_data.copy()
                daily_cognitive['timestamp'] = current_date.isoformat()
                daily_cognitive['total_interactions'] = max(0, daily_cognitive['total_interactions'] + random.randint(-50, 100))
                daily_cognitive['user_satisfaction'] = max(3.5, min(5.0, daily_cognitive['user_satisfaction'] + random.uniform(-0.2, 0.2)))
                historical_cognitive.append(daily_cognitive)
            
            return {'current': cognitive_data, 'historical': historical_cognitive}
        
        return cognitive_data


class ReportFormatter:
    """Formatador de relatórios"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.reports.formatter", "report_formatter")
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """Carrega templates de relatório"""
        templates = {
            'html_template': """
<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { background-color: #f0f0f0; padding: 20px; border-radius: 5px; }
        .section { margin: 20px 0; padding: 15px; border-left: 4px solid #007cba; }
        .metric { display: inline-block; margin: 10px; padding: 10px; background-color: #f9f9f9; border-radius: 3px; }
        .table { border-collapse: collapse; width: 100%; }
        .table th, .table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        .table th { background-color: #f2f2f2; }
        .chart { margin: 20px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        <p>Generated: {timestamp}</p>
        <p>Period: {period}</p>
    </div>
    {content}
</body>
</html>
            """,
            'markdown_template': """
# {title}

**Generated:** {timestamp}  
**Period:** {period}

{content}
            """
        }
        return templates
    
    def format_json(self, sections: List[ReportSection], metadata: Dict[str, Any]) -> str:
        """Formata relatório como JSON"""
        report_data = {
            'metadata': metadata,
            'sections': [section.to_dict() for section in sections],
            'generated_at': datetime.now().isoformat()
        }
        return json.dumps(report_data, indent=2, ensure_ascii=False)
    
    def format_html(self, sections: List[ReportSection], metadata: Dict[str, Any]) -> str:
        """Formata relatório como HTML"""
        template = self.templates.get('html_template', '{content}')
        
        content_parts = []
        for section in sections:
            if section.section_type == 'text':
                content_parts.append(f'<div class="section"><h2>{section.title}</h2><p>{section.content}</p></div>')
            elif section.section_type == 'metrics':
                content_parts.append(f'<div class="section"><h2>{section.title}</h2>')
                if isinstance(section.content, dict):
                    for key, value in section.content.items():
                        content_parts.append(f'<div class="metric"><strong>{key}:</strong> {value}</div>')
                content_parts.append('</div>')
            elif section.section_type == 'table':
                content_parts.append(f'<div class="section"><h2>{section.title}</h2>')
                if isinstance(section.content, list) and section.content:
                    content_parts.append('<table class="table">')
                    # Header
                    if isinstance(section.content[0], dict):
                        headers = list(section.content[0].keys())
                        content_parts.append('<tr>' + ''.join(f'<th>{h}</th>' for h in headers) + '</tr>')
                        # Rows
                        for row in section.content:
                            content_parts.append('<tr>' + ''.join(f'<td>{row.get(h, "")}</td>' for h in headers) + '</tr>')
                    content_parts.append('</table>')
                content_parts.append('</div>')
        
        content_html = ''.join(content_parts)
        
        return template.format(
            title=metadata.get('title', 'Report'),
            timestamp=metadata.get('generated_at', datetime.now().isoformat()),
            period=metadata.get('period', 'N/A'),
            content=content_html
        )
    
    def format_markdown(self, sections: List[ReportSection], metadata: Dict[str, Any]) -> str:
        """Formata relatório como Markdown"""
        template = self.templates.get('markdown_template', '{content}')
        
        content_parts = []
        for section in sections:
            content_parts.append(f'## {section.title}\n')
            
            if section.section_type == 'text':
                content_parts.append(f'{section.content}\n')
            elif section.section_type == 'metrics':
                if isinstance(section.content, dict):
                    for key, value in section.content.items():
                        content_parts.append(f'- **{key}**: {value}\n')
            elif section.section_type == 'table':
                if isinstance(section.content, list) and section.content:
                    if isinstance(section.content[0], dict):
                        headers = list(section.content[0].keys())
                        content_parts.append('| ' + ' | '.join(headers) + ' |')
                        content_parts.append('|' + '--|' * len(headers) + '|')
                        for row in section.content:
                            content_parts.append('| ' + ' | '.join(str(row.get(h, "")) for h in headers) + ' |')
                        content_parts.append('')
        
        content_md = ''.join(content_parts)
        
        return template.format(
            title=metadata.get('title', 'Report'),
            timestamp=metadata.get('generated_at', datetime.now().isoformat()),
            period=metadata.get('period', 'N/A'),
            content=content_md
        )
    
    def format_csv(self, sections: List[ReportSection], metadata: Dict[str, Any]) -> str:
        """Formata relatório como CSV"""
        csv_lines = []
        
        # Header
        csv_lines.append('Section,Type,Content,Timestamp')
        
        # Data
        for section in sections:
            content_str = str(section.content).replace('\n', ' ').replace('\r', '')
            if len(content_str) > 1000:
                content_str = content_str[:1000] + '...'
            
            csv_lines.append(f'"{section.title}","{section.section_type}","{content_str}","{section.timestamp.isoformat()}"')
        
        return '\n'.join(csv_lines)


class ReportGenerator:
    """Gerador principal de relatórios"""
    
    def __init__(self):
        self.logger = get_logger("vhalinor.reports.generator", "report_generator")
        self.data_collector = ReportDataCollector()
        self.formatter = ReportFormatter()
        self.report_history = []
        self.output_dir = Path("reports")
        self.output_dir.mkdir(exist_ok=True)
    
    @log_execution(component="reports", operation="generate_report")
    async def generate_report(self, config: ReportConfig) -> Dict[str, Any]:
        """Gera relatório baseado na configuração"""
        self.logger.info(f"Generating {config.report_type.value} report in {config.format.value} format")
        
        # Coletar dados
        data = await self._collect_report_data(config)
        
        # Gerar seções
        sections = await self._generate_sections(config, data)
        
        # Aplicar filtros
        if config.include_sections:
            sections = [s for s in sections if s.title in config.include_sections]
        if config.exclude_sections:
            sections = [s for s in sections if s.title not in config.exclude_sections]
        
        # Formatar relatório
        formatted_content = await self._format_report(config, sections)
        
        # Salvar se necessário
        file_path = None
        if config.output_path:
            file_path = await self._save_report(config, formatted_content)
        
        # Metadata do relatório
        metadata = {
            'title': f"{config.report_type.value.replace('_', ' ').title()} Report",
            'report_type': config.report_type.value,
            'format': config.format.value,
            'generated_at': datetime.now().isoformat(),
            'period': self._format_period(config.date_range),
            'sections_count': len(sections),
            'file_path': file_path,
            'config': config.to_dict()
        }
        
        # Registrar no histórico
        report_record = {
            'id': hashlib.md5(f"{config.report_type.value}{datetime.now().isoformat()}".encode()).hexdigest(),
            'config': config.to_dict(),
            'metadata': metadata,
            'sections_count': len(sections),
            'generated_at': datetime.now()
        }
        self.report_history.append(report_record)
        
        self.logger.info(f"Report generated successfully: {len(sections)} sections")
        
        return {
            'metadata': metadata,
            'sections': [section.to_dict() for section in sections],
            'content': formatted_content,
            'file_path': file_path
        }
    
    async def _collect_report_data(self, config: ReportConfig) -> Dict[str, Any]:
        """Coleta dados para o relatório"""
        data = {}
        
        if config.report_type in [ReportType.SYSTEM_PERFORMANCE, ReportType.COMPREHENSIVE]:
            data['system'] = await self.data_collector.collect_system_metrics(config.date_range)
        
        if config.report_type in [ReportType.TRADING_ANALYSIS, ReportType.COMPREHENSIVE]:
            data['trading'] = await self.data_collector.collect_trading_data(config.date_range)
        
        if config.report_type in [ReportType.AI_METRICS, ReportType.COMPREHENSIVE]:
            data['ai'] = await self.data_collector.collect_ai_metrics(config.date_range)
        
        if config.report_type in [ReportType.AUTOMATION_SUMMARY, ReportType.COMPREHENSIVE]:
            data['automation'] = await self.data_collector.collect_automation_data(config.date_range)
        
        if config.report_type in [ReportType.COGNITIVE_ANALYSIS, ReportType.COMPREHENSIVE]:
            data['cognitive'] = await self.data_collector.collect_cognitive_data(config.date_range)
        
        # Aplicar filtros personalizados
        if config.filters:
            data = self._apply_filters(data, config.filters)
        
        return data
    
    async def _generate_sections(self, config: ReportConfig, data: Dict[str, Any]) -> List[ReportSection]:
        """Gera seções do relatório"""
        sections = []
        
        # Seção de resumo executivo
        if config.report_type != ReportType.COMPREHENSIVE:
            sections.append(ReportSection(
                title="Executive Summary",
                content=self._generate_executive_summary(config.report_type, data),
                section_type="text"
            ))
        
        # Seções específicas por tipo
        if 'system' in data:
            sections.extend(self._generate_system_sections(data['system']))
        
        if 'trading' in data:
            sections.extend(self._generate_trading_sections(data['trading']))
        
        if 'ai' in data:
            sections.extend(self._generate_ai_sections(data['ai']))
        
        if 'automation' in data:
            sections.extend(self._generate_automation_sections(data['automation']))
        
        if 'cognitive' in data:
            sections.extend(self._generate_cognitive_sections(data['cognitive']))
        
        # Seção de conclusões
        sections.append(ReportSection(
            title="Conclusions and Recommendations",
            content=self._generate_conclusions(config.report_type, data),
            section_type="text"
        ))
        
        return sections
    
    def _generate_system_sections(self, system_data: Dict[str, Any]) -> List[ReportSection]:
        """Gera seções de sistema"""
        sections = []
        
        # Métricas atuais
        current_metrics = system_data.get('current', system_data)
        sections.append(ReportSection(
            title="System Performance Metrics",
            content=current_metrics,
            section_type="metrics"
        ))
        
        # Dados históricos se disponíveis
        if 'historical' in system_data:
            sections.append(ReportSection(
                title="Historical Performance",
                content=system_data['historical'],
                section_type="table"
            ))
        
        return sections
    
    def _generate_trading_sections(self, trading_data: Dict[str, Any]) -> List[ReportSection]:
        """Gera seções de trading"""
        sections = []
        
        # Métricas de trading
        current_trading = trading_data.get('current', trading_data)
        sections.append(ReportSection(
            title="Trading Performance",
            content=current_trading,
            section_type="metrics"
        ))
        
        # Histórico se disponível
        if 'historical' in trading_data:
            sections.append(ReportSection(
                title="Trading History",
                content=trading_data['historical'],
                section_type="table"
            ))
        
        return sections
    
    def _generate_ai_sections(self, ai_data: Dict[str, Any]) -> List[ReportSection]:
        """Gera seções de IA"""
        sections = []
        
        # Métricas de IA
        current_ai = ai_data.get('current', ai_data)
        sections.append(ReportSection(
            title="AI Model Performance",
            content=current_ai,
            section_type="metrics"
        ))
        
        # Histórico se disponível
        if 'historical' in ai_data:
            sections.append(ReportSection(
                title="AI Performance History",
                content=ai_data['historical'],
                section_type="table"
            ))
        
        return sections
    
    def _generate_automation_sections(self, automation_data: Dict[str, Any]) -> List[ReportSection]:
        """Gera seções de automação"""
        sections = []
        
        # Métricas de automação
        current_automation = automation_data.get('current', automation_data)
        sections.append(ReportSection(
            title="Automation Performance",
            content=current_automation,
            section_type="metrics"
        ))
        
        # Histórico se disponível
        if 'historical' in automation_data:
            sections.append(ReportSection(
                title="Automation History",
                content=automation_data['historical'],
                section_type="table"
            ))
        
        return sections
    
    def _generate_cognitive_sections(self, cognitive_data: Dict[str, Any]) -> List[ReportSection]:
        """Gera seções cognitivas"""
        sections = []
        
        # Métricas cognitivas
        current_cognitive = cognitive_data.get('current', cognitive_data)
        sections.append(ReportSection(
            title="Cognitive System Performance",
            content=current_cognitive,
            section_type="metrics"
        ))
        
        # Histórico se disponível
        if 'historical' in cognitive_data:
            sections.append(ReportSection(
                title="Cognitive Performance History",
                content=cognitive_data['historical'],
                section_type="table"
            ))
        
        return sections
    
    def _generate_executive_summary(self, report_type: ReportType, data: Dict[str, Any]) -> str:
        """Gera resumo executivo"""
        summaries = {
            ReportType.SYSTEM_PERFORMANCE: "System performance shows stable operation with normal resource utilization. All critical services are functioning within expected parameters.",
            ReportType.TRADING_ANALYSIS: "Trading activities demonstrate consistent profitability with a healthy win rate. Risk management protocols are being effectively maintained.",
            ReportType.AI_METRICS: "AI models are performing within expected accuracy ranges. Prediction models show stable performance with regular training updates.",
            ReportType.AUTOMATION_SUMMARY: "Automation processes are running efficiently with high success rates. Error rates remain within acceptable thresholds.",
            ReportType.COGNITIVE_ANALYSIS: "Cognitive systems are responding effectively with good user satisfaction scores. Memory management and reasoning patterns are optimal.",
            ReportType.COMPREHENSIVE: "Overall system performance is excellent across all components. Integration between modules is functioning smoothly with good resource utilization."
        }
        
        return summaries.get(report_type, "Report generated successfully with comprehensive data analysis.")
    
    def _generate_conclusions(self, report_type: ReportType, data: Dict[str, Any]) -> str:
        """Gera conclusões e recomendações"""
        conclusions = {
            ReportType.SYSTEM_PERFORMANCE: "System is operating optimally. Continue monitoring resource usage and consider scaling during peak periods.",
            ReportType.TRADING_ANALYSIS: "Trading performance is strong. Maintain current strategies while exploring new market opportunities.",
            ReportType.AI_METRICS: "AI models are performing well. Consider fine-tuning hyperparameters for improved accuracy.",
            ReportType.AUTOMATION_SUMMARY: "Automation is highly effective. Focus on optimizing frequently used workflows.",
            ReportType.COGNITIVE_ANALYSIS: "Cognitive systems are responsive. Enhance context retention for better user experience.",
            ReportType.COMPREHENSIVE: "All systems are performing excellently. Continue current operations while planning for future scalability."
        }
        
        return conclusions.get(report_type, "Analysis complete. Continue monitoring system performance.")
    
    async def _format_report(self, config: ReportConfig, sections: List[ReportSection]) -> str:
        """Formata relatório conforme especificação"""
        metadata = {
            'title': f"{config.report_type.value.replace('_', ' ').title()} Report",
            'generated_at': datetime.now().isoformat(),
            'period': self._format_period(config.date_range)
        }
        
        if config.format == ReportFormat.JSON:
            return self.formatter.format_json(sections, metadata)
        elif config.format == ReportFormat.HTML:
            return self.formatter.format_html(sections, metadata)
        elif config.format == ReportFormat.MARKDOWN:
            return self.formatter.format_markdown(sections, metadata)
        elif config.format == ReportFormat.CSV:
            return self.formatter.format_csv(sections, metadata)
        else:
            return self.formatter.format_json(sections, metadata)
    
    async def _save_report(self, config: ReportConfig, content: str) -> str:
        """Salva relatório em arquivo"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{config.report_type.value}_{timestamp}.{config.format.value}"
        file_path = self.output_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.logger.info(f"Report saved to: {file_path}")
        return str(file_path)
    
    def _format_period(self, date_range: Optional[Tuple[datetime, datetime]]) -> str:
        """Formata período do relatório"""
        if date_range:
            start, end = date_range
            return f"{start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}"
        return "Current"
    
    def _apply_filters(self, data: Dict[str, Any], filters: Dict[str, Any]) -> Dict[str, Any]:
        """Aplica filtros aos dados"""
        filtered_data = data.copy()
        
        for key, filter_value in filters.items():
            if key in filtered_data and isinstance(filtered_data[key], dict):
                if isinstance(filter_value, list):
                    # Filtrar apenas chaves especificadas
                    filtered_data[key] = {k: v for k, v in filtered_data[key].items() if k in filter_value}
                elif isinstance(filter_value, dict):
                    # Aplicar filtros complexos
                    for sub_key, sub_filter in filter_value.items():
                        if sub_key in filtered_data[key]:
                            if isinstance(sub_filter, dict) and 'min' in sub_filter:
                                filtered_data[key][sub_key] = max(sub_filter['min'], filtered_data[key][sub_key])
                            elif isinstance(sub_filter, dict) and 'max' in sub_filter:
                                filtered_data[key][sub_key] = min(sub_filter['max'], filtered_data[key][sub_key])
        
        return filtered_data
    
    async def generate_scheduled_reports(self) -> List[Dict[str, Any]]:
        """Gera relatórios agendados"""
        reports = []
        
        # Relatório diário
        daily_config = ReportConfig(
            report_type=ReportType.DAILY_SUMMARY,
            format=ReportFormat.JSON,
            date_range=(datetime.now() - timedelta(days=1), datetime.now())
        )
        daily_report = await self.generate_report(daily_config)
        reports.append(daily_report)
        
        # Relatório semanal
        weekly_config = ReportConfig(
            report_type=ReportType.WEEKLY_SUMMARY,
            format=ReportFormat.HTML,
            date_range=(datetime.now() - timedelta(days=7), datetime.now())
        )
        weekly_report = await self.generate_report(weekly_config)
        reports.append(weekly_report)
        
        return reports
    
    def get_report_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retorna histórico de relatórios"""
        return self.report_history[-limit:]
    
    def get_report_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas de relatórios"""
        if not self.report_history:
            return {'total_reports': 0}
        
        report_types = {}
        formats = {}
        
        for report in self.report_history:
            report_type = report['config']['report_type']
            report_format = report['config']['format']
            
            report_types[report_type] = report_types.get(report_type, 0) + 1
            formats[report_format] = formats.get(report_format, 0) + 1
        
        return {
            'total_reports': len(self.report_history),
            'report_types': report_types,
            'formats': formats,
            'last_generated': self.report_history[-1]['generated_at'].isoformat() if self.report_history else None
        }


# Função de conveniência para obter instância do gerador de relatórios
_report_generator_instance = None

def get_report_generator() -> ReportGenerator:
    """Obtém instância singleton do gerador de relatórios"""
    global _report_generator_instance
    if _report_generator_instance is None:
        _report_generator_instance = ReportGenerator()
    return _report_generator_instance


# Import necessário para random
import random

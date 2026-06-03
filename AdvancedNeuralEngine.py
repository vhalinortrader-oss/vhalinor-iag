import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Literal, Callable
from datetime import datetime
import threading
import time
import random
from enum import Enum
import webbrowser
import json

# Enums para tipos de dados
class AutonomyLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    AUTONOMOUS = "AUTONOMOUS"

class ModuleType(Enum):
    ANALYTICAL = "ANALYTICAL"
    CREATIVE = "CREATIVE"
    STRATEGIC = "STRATEGIC"
    OPERATIONAL = "OPERATIONAL"
    ADAPTIVE = "ADAPTIVE"

class ModuleStatus(Enum):
    ACTIVE = "ACTIVE"
    LEARNING = "LEARNING"
    CREATING = "CREATING"
    OPTIMIZING = "OPTIMIZING"
    STANDBY = "STANDBY"

class KnowledgeType(Enum):
    HISTORICAL_DATA = "HISTORICAL_DATA"
    NEWS = "NEWS"
    SOCIAL_MEDIA = "SOCIAL_MEDIA"
    ECONOMIC_REPORTS = "ECONOMIC_REPORTS"
    MARKET_BEHAVIOR = "MARKET_BEHAVIOR"

# Estruturas de dados equivalentes às interfaces TypeScript
@dataclass
class IAGDomain:
    name: str
    description: str
    competency: float
    autonomy_level: AutonomyLevel
    learning_progress: float
    active_connections: int
    is_adapting: bool

@dataclass
class CognitiveModule:
    id: str
    name: str
    type: ModuleType
    status: ModuleStatus
    intelligence: float
    creativity: float
    autonomy: float
    tasks: List[str]
    current_task: str

@dataclass
class KnowledgeSource:
    source: str
    type: KnowledgeType
    data_points: int
    reliability: float
    impact: float
    last_update: datetime
    insights: List[str]

@dataclass
class StrategicDecision:
    id: str
    context: str
    decision: str
    confidence: float
    risk_assessment: float
    expected_outcome: str
    adaptive_factor: float
    timestamp: datetime
    reasoning: List[str]

@dataclass
class IAGMetrics:
    overall_intelligence: float
    adaptability_index: float
    creativity_score: float
    autonomy_level: float
    learning_velocity: float
    strategy_generation: float
    risk_awareness: float
    market_understanding: float
    processed_data_points: int
    active_strategies: int

@dataclass
class MarketBase:
    name: str
    description: str
    url: str
    indicators: Optional[List[str]] = None

# Banco de dados de plataformas, ferramentas e fontes de dados
MARKET_BASES = {
    'technical_platforms': [
        MarketBase(
            name='TradingView',
            description='Interface intuitiva, gráficos interativos e uma comunidade ativa. Suporta indicadores como RSI, MACD, médias móveis e muito mais.',
            url='https://www.tradingview.com/',
            indicators=['RSI', 'MACD', 'Médias Móveis', 'Outros']
        ),
        MarketBase(
            name='MetaTrader 4 (MT4)',
            description='Muito usado no Forex, mas também útil para outros mercados. Permite automação com robôs de trading e personalização de indicadores.',
            url='https://www.metatrader4.com/',
            indicators=['Robôs', 'Personalização', 'Forex', 'Outros']
        ),
        MarketBase(
            name='MetaTrader 5 (MT5)',
            description='Muito usado no Forex, mas também útil para outros mercados. Permite automação com robôs de trading e personalização de indicadores.',
            url='https://www.metatrader5.com/',
            indicators=['Robôs', 'Personalização', 'Forex', 'Outros']
        ),
        MarketBase(
            name='Investing.com',
            description='Oferece gráficos e dados em tempo real para ações, commodities, forex e índices. Ideal para traders iniciantes.',
            url='https://www.investing.com/',
            indicators=['Ações', 'Commodities', 'Forex', 'Índices']
        )
    ],
    'day_trade_tools': [
        MarketBase(
            name='Profit (Nelogica)',
            description='Uma das plataformas mais populares no Brasil, com gráficos avançados e execução rápida.',
            url='https://www.nelogica.com.br/profit'
        ),
        MarketBase(
            name='Tryd',
            description='Foco em agilidade e profundidade de mercado. Muito usada por traders profissionais.',
            url='https://www.tryd.com.br/'
        ),
        MarketBase(
            name='Invest Flex',
            description='Boa integração com corretoras e recursos para análise técnica e fundamentalista.',
            url='https://www.investflex.com.br/'
        )
    ],
    'data_sources_and_community': [
        MarketBase(
            name='Learn 2 Trade',
            description='Plataforma com sinais de alta precisão e análises de mercado.',
            url='https://learn2.trade/'
        ),
        MarketBase(
            name='ZIGDAO',
            description='Foco em negociação social, especialmente em criptomoedas.',
            url='https://zigdao.com/'
        ),
        MarketBase(
            name='StockCharts',
            description='Excelente para análise técnica de ações e índices, com gráficos robustos.',
            url='https://stockcharts.com/'
        )
    ]
}

class AdvancedNeuralEngineApp:
    """Aplicação principal que replica a funcionalidade do componente React AdvancedNeuralEngine"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("🧠 Inteligência Artificial Geral (IAG) - Day Trade")
        self.root.geometry("1500x1000")
        self.root.configure(bg='#f8fafc')
        
        # Estado da aplicação (equivalente aos useState hooks)
        self.iag_domains: List[IAGDomain] = []
        self.cognitive_modules: List[CognitiveModule] = []
        self.knowledge_sources: List[KnowledgeSource] = []
        self.strategic_decisions: List[StrategicDecision] = []
        self.iag_metrics = IAGMetrics(0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        self.is_operational = True
        self.consciousness_level = 'SUPERINTELIGENTE'
        self.processing_load = 72.0
        self.uptime = 123456
        self.data_throughput = 1250.0
        
        # Containers para widgets que precisam ser atualizados
        self.metrics_labels = {}
        self.domain_frames = []
        self.module_frames = []
        
        # Configurar estilos
        self.setup_styles()
        
        # Inicializar dados
        self.initialize_data()
        
        # Configurar interface
        self.setup_ui()
        
        # Iniciar thread de atualização (equivalente ao useEffect)
        self.start_update_thread()
    
    def setup_styles(self) -> None:
        """Configurar estilos customizados para a aplicação"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar cores personalizadas
        style.configure('Primary.TButton', 
                       background='#3b82f6', 
                       foreground='white',
                       focuscolor='none')
        
        style.configure('Success.TLabel', foreground='#10b981')
        style.configure('Warning.TLabel', foreground='#f59e0b')
        style.configure('Error.TLabel', foreground='#ef4444')
        style.configure('Info.TLabel', foreground='#6366f1')
        style.configure('Purple.TLabel', foreground='#8b5cf6')
        
        style.configure('Card.TFrame', 
                       background='white', 
                       relief='solid',
                       borderwidth=1)
    
    # Funções utilitárias (equivalentes às funções do React)
    def get_autonomy_color(self, level: AutonomyLevel) -> str:
        """Obter cor para nível de autonomia (equivalente a getAutonomyColor)"""
        color_map = {
            AutonomyLevel.AUTONOMOUS: "#10b981",
            AutonomyLevel.HIGH: "#f59e0b",
            AutonomyLevel.MEDIUM: "#6b7280",
            AutonomyLevel.LOW: "#ef4444"
        }
        return color_map.get(level, "#6b7280")
    
    def get_module_type_color(self, module_type: ModuleType) -> str:
        """Obter cor para tipo de módulo (equivalente a getModuleTypeColor)"""
        color_map = {
            ModuleType.ANALYTICAL: "#3b82f6",
            ModuleType.CREATIVE: "#8b5cf6",
            ModuleType.STRATEGIC: "#10b981",
            ModuleType.OPERATIONAL: "#f59e0b",
            ModuleType.ADAPTIVE: "#ec4899"
        }
        return color_map.get(module_type, "#6366f1")
    
    def get_module_status_color(self, status: ModuleStatus) -> str:
        """Obter cor para status do módulo (equivalente a getModuleStatusColor)"""
        color_map = {
            ModuleStatus.ACTIVE: "#10b981",
            ModuleStatus.LEARNING: "#6b7280",
            ModuleStatus.CREATING: "#3b82f6",
            ModuleStatus.OPTIMIZING: "#f59e0b",
            ModuleStatus.STANDBY: "#ef4444"
        }
        return color_map.get(status, "#6b7280")
    
    def get_knowledge_type_color(self, knowledge_type: KnowledgeType) -> str:
        """Obter cor para tipo de conhecimento (equivalente a getKnowledgeTypeColor)"""
        color_map = {
            KnowledgeType.HISTORICAL_DATA: "#3b82f6",
            KnowledgeType.NEWS: "#10b981",
            KnowledgeType.SOCIAL_MEDIA: "#8b5cf6",
            KnowledgeType.ECONOMIC_REPORTS: "#f59e0b",
            KnowledgeType.MARKET_BEHAVIOR: "#ec4899"
        }
        return color_map.get(knowledge_type, "#6366f1")
    
    # Funções de inicialização de dados (equivalentes às funções init do React)
    def init_iag_domains(self) -> List[IAGDomain]:
        """Inicializar domínios IAG (equivalente a initIAGDomains)"""
        return [
            IAGDomain(
                name='Análise Multidisciplinar',
                description='Integração de dados históricos, notícias, redes sociais e relatórios econômicos',
                competency=999.2,
                autonomy_level=AutonomyLevel.AUTONOMOUS,
                learning_progress=9998.7,
                active_connections=932000,
                is_adapting=True
            ),
            IAGDomain(
                name='Interpretação Contextual',
                description='Compreensão do impacto de eventos geopolíticos e decisões de bancos centrais',
                competency=998.5,
                autonomy_level=AutonomyLevel.HIGH,
                learning_progress=997.1,
                active_connections=2500000,
                is_adapting=True
            ),
            IAGDomain(
                name='Execução Autônoma',
                description='Operação em múltiplos mercados e ativos simultaneamente',
                competency=999.7,
                autonomy_level=AutonomyLevel.AUTONOMOUS,
                learning_progress=999.1,
                active_connections=410000,
                is_adapting=False
            ),
            IAGDomain(
                name='Criação de Estratégias',
                description='Desenvolvimento de novas abordagens de trading baseadas em simulações',
                competency=997.8,
                autonomy_level=AutonomyLevel.HIGH,
                learning_progress=96.2,
                active_connections=180000,
                is_adapting=True
            ),
            IAGDomain(
                name='Gestão de Risco Dinâmica',
                description='Avaliação de exposição, correlação e volatilidade em tempo real',
                competency=998.9,
                autonomy_level=AutonomyLevel.AUTONOMOUS,
                learning_progress=998.3,
                active_connections=290000,
                is_adapting=False
            ),
            IAGDomain(
                name='Consciência Operacional',
                description='Reconhecimento de condições desfavoráveis e preservação de capital',
                competency=997.2,
                autonomy_level=AutonomyLevel.HIGH,
                learning_progress=995.7,
                active_connections=170000,
                is_adapting=True
            ),
            IAGDomain(
                name='Trading Spot',
                description='Execução e análise autônoma de operações spot em múltiplos ativos e mercados.',
                competency=996.8,
                autonomy_level=AutonomyLevel.AUTONOMOUS,
                learning_progress=995.5,
                active_connections=210000,
                is_adapting=True
            )
        ]
    
    def init_cognitive_modules(self) -> List[CognitiveModule]:
        """Inicializar módulos cognitivos (equivalente a initCognitiveModules)"""
        return [
            CognitiveModule(
                id='cognitive_analytical',
                name='Módulo Analítico',
                type=ModuleType.ANALYTICAL,
                status=ModuleStatus.ACTIVE,
                intelligence=999.1,
                creativity=989.5,
                autonomy=998.7,
                tasks=['Análise Técnica', 'Processamento de Dados', 'Pattern Recognition'],
                current_task='Análise de Correlações Complexas'
            ),
            CognitiveModule(
                id='cognitive_creative',
                name='Módulo Criativo',
                type=ModuleType.CREATIVE,
                status=ModuleStatus.CREATING,
                intelligence=997.8,
                creativity=999.2,
                autonomy=996.5,
                tasks=['Geração de Estratégias', 'Inovação Algorítmica', 'Cenários Alternativos'],
                current_task='Desenvolvendo Nova Estratégia Híbrida'
            ),
            CognitiveModule(
                id='cognitive_strategic',
                name='Módulo Estratégico',
                type=ModuleType.STRATEGIC,
                status=ModuleStatus.OPTIMIZING,
                intelligence=998.6,
                creativity=992.7,
                autonomy=997.3,
                tasks=['Planejamento de Curto Prazo', 'Planejamento de Medio Prazo', 'Planejamento de Longo Prazo', 'Otimização de Portfolio', 'Decisões Táticas'],
                current_task='Otimização de Alocação de Ativos'
            ),
            CognitiveModule(
                id='cognitive_operational',
                name='Módulo Operacional',
                type=ModuleType.OPERATIONAL,
                status=ModuleStatus.ACTIVE,
                intelligence=997.2,
                creativity=988.1,
                autonomy=999.5,
                tasks=['Execução de Ordens', 'Monitoramento Contínuo', 'Ajustes Automáticos', 'Trading Spot Autônomo'],
                current_task='Execução Multi-Asset Sincronizada'
            ),
            CognitiveModule(
                id='cognitive_adaptive',
                name='Módulo Adaptativo',
                type=ModuleType.ADAPTIVE,
                status=ModuleStatus.LEARNING,
                intelligence=996.7,
                creativity=997.4,
                autonomy=995.9,
                tasks=['Aprendizado Contínuo', 'Adaptação Contextual', 'Criação de Modelos', 'Evolução de Modelos'],
                current_task='Adaptação a Novas Condições de Mercado'
            )
        ]
    
    def init_knowledge_sources(self) -> List[KnowledgeSource]:
        """Inicializar fontes de conhecimento (equivalente a initKnowledgeSources)"""
        return [
            KnowledgeSource(
                source='Dados Históricos de Mercado',
                type=KnowledgeType.HISTORICAL_DATA,
                data_points=15420000,
                reliability=98.5,
                impact=94.2,
                last_update=datetime.now(),
                insights=['Padrões Sazonais Identificados', 'Correlações de Longo Prazo', 'Volatilidade Cíclica']
            ),
            KnowledgeSource(
                source='Análise de Notícias Financeiras',
                type=KnowledgeType.NEWS,
                data_points=2847000,
                reliability=89.7,
                impact=87.3,
                last_update=datetime.now(),
                insights=['Sentimento de Mercado Positivo', 'Expectativas de Política Monetária', 'Eventos Geopolíticos']
            ),
            KnowledgeSource(
                source='Redes Sociais e Sentiment',
                type=KnowledgeType.SOCIAL_MEDIA,
                data_points=8932000,
                reliability=76.4,
                impact=71.8,
                last_update=datetime.now(),
                insights=['Tendências Virais Emergentes', 'Comportamento Retail', 'Influenciadores de Mercado']
            ),
            KnowledgeSource(
                source='Relatórios Econômicos',
                type=KnowledgeType.ECONOMIC_REPORTS,
                data_points=1256000,
                reliability=96.8,
                impact=92.5,
                last_update=datetime.now(),
                insights=['Indicadores Macroeconômicos', 'Projeções do PIB', 'Políticas Fiscais']
            ),
            KnowledgeSource(
                source='Comportamento de Mercado',
                type=KnowledgeType.MARKET_BEHAVIOR,
                data_points=7421000,
                reliability=91.3,
                impact=89.6,
                last_update=datetime.now(),
                insights=['Flow de Investidores', 'Posicionamento Institucional', 'Liquidez de Mercado']
            )
        ]
    
    def init_strategic_decisions(self) -> List[StrategicDecision]:
        """Inicializar decisões estratégicas (equivalente a initStrategicDecisions)"""
        return [
            StrategicDecision(
                id='decision_001',
                context='Identificação de divergência em múltiplos timeframes',
                decision='Estabelecer posição longa em EUR/USD com stop dinâmico',
                confidence=94.7,
                risk_assessment=23.5,
                expected_outcome='Retorno de 2.8% em 3-5 dias úteis',
                adaptive_factor=87.2,
                timestamp=datetime.now(),
                reasoning=[
                    'Convergência de indicadores técnicos em H4 e D1',
                    'Sentimento de mercado favorável ao EUR',
                    'Redução da volatilidade sistêmica',
                    'Confirmação por múltiplos modelos de ML'
                ]
            ),
            StrategicDecision(
                id='decision_002',
                context='Detecção de padrão anômalo em índices asiáticos',
                decision='Reduzir exposição a ativos de risco e aumentar posições defensivas',
                confidence=91.2,
                risk_assessment=34.7,
                expected_outcome='Preservação de capital com possível ganho de 1.2%',
                adaptive_factor=92.8,
                timestamp=datetime.now(),
                reasoning=[
                    'Análise de correlações cruzadas anômalas',
                    'Indicadores de stress financeiro elevados',
                    'Padrão histórico similar em 2018',
                    'Consenso entre módulos de risco'
                ]
            ),
            StrategicDecision(
                id='decision_003',
                context='Oportunidade de arbitragem spot detectada entre BTC/USD e ETH/USD',
                decision='Executar trading spot autônomo para maximizar retorno instantâneo',
                confidence=92.3,
                risk_assessment=27.8,
                expected_outcome='Ganho potencial de 1.5% em operação spot',
                adaptive_factor=88.5,
                timestamp=datetime.now(),
                reasoning=[
                    'Diferença de preço detectada entre exchanges',
                    'Volume suficiente para execução sem slippage',
                    'Confirmação por múltiplos módulos operacionais',
                    'Gestão de risco aplicada para operação spot'
                ]
            )
        ]
    
    def calculate_iag_metrics(self) -> IAGMetrics:
        """Calcular métricas IAG (equivalente a calculateIAGMetrics)"""
        return IAGMetrics(
            overall_intelligence=98.7 + random.random() * 1.2,
            adaptability_index=97.5 + random.random() * 2,
            creativity_score=96.2 + random.random() * 2.5,
            autonomy_level=99.1 + random.random() * 0.7,
            learning_velocity=97.8 + random.random() * 2,
            strategy_generation=98.3 + random.random() * 1.5,
            risk_awareness=97.9 + random.random() * 1.8,
            market_understanding=98.4 + random.random() * 1.1,
            processed_data_points=15420000 + int(random.random() * 100000),
            active_strategies=3 + int(random.random() * 3)
        )
    
    def initialize_data(self) -> None:
        """Inicializar todos os dados da aplicação"""
        self.iag_domains = self.init_iag_domains()
        self.cognitive_modules = self.init_cognitive_modules()
        self.knowledge_sources = self.init_knowledge_sources()
        self.strategic_decisions = self.init_strategic_decisions()
        self.iag_metrics = self.calculate_iag_metrics()
    
    # Funções de controle principais
    def toggle_operational_status(self) -> None:
        """Alternar status operacional (equivalente ao onClick do botão)"""
        self.is_operational = not self.is_operational
        self.update_header_display()
        
        if self.is_operational:
            messagebox.showinfo("Sistema", "Sistema ativado e operacional!")
        else:
            messagebox.showinfo("Sistema", "Sistema em modo standby.")
    
    def open_url(self, url: str) -> None:
        """Abrir URL no navegador"""
        try:
            webbrowser.open(url)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir o link: {e}")
    
    # Configuração da interface gráfica
    def setup_ui(self) -> None:
        """Configurar interface principal"""
        # Frame principal com padding
        main_frame = ttk.Frame(self.root, padding="20", style='Card.TFrame')
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        
        # Cabeçalho
        self.setup_header(main_frame)
        
        # Notebook para abas (equivalente ao Tabs do React)
        self.setup_notebook(main_frame)
        
        # Configurar redimensionamento
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
    
    def setup_header(self, parent: ttk.Frame) -> None:
        """Configurar cabeçalho da aplicação"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Título
        title_label = ttk.Label(header_frame, 
                               text="🧠 Inteligência Artificial Geral (IAG) - Day Trade", 
                               font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        # Status e controles
        control_frame = ttk.Frame(header_frame)
        control_frame.grid(row=0, column=1, sticky=tk.E)
        
        # Badge de nível de consciência
        self.consciousness_label = ttk.Label(control_frame, 
                                           text=f"✨ Nível: {self.consciousness_level}", 
                                           style='Info.TLabel',
                                           font=("Arial", 10, "bold"))
        self.consciousness_label.grid(row=0, column=0, padx=(0, 10))
        
        # Badge de status operacional
        self.status_label = ttk.Label(control_frame, 
                                     text=f"📊 {'OPERACIONAL' if self.is_operational else 'STANDBY'}", 
                                     style='Success.TLabel' if self.is_operational else 'Warning.TLabel',
                                     font=("Arial", 10, "bold"))
        self.status_label.grid(row=0, column=1, padx=(0, 10))
        
        # Botão toggle operacional
        self.toggle_btn = ttk.Button(control_frame, 
                                   text="⏸️" if self.is_operational else "▶️", 
                                   command=self.toggle_operational_status,
                                   style='Primary.TButton')
        self.toggle_btn.grid(row=0, column=2)
        
        header_frame.columnconfigure(0, weight=1)
    
    def update_header_display(self) -> None:
        """Atualizar exibição do cabeçalho"""
        self.status_label.config(
            text=f"📊 {'OPERACIONAL' if self.is_operational else 'STANDBY'}",
            style='Success.TLabel' if self.is_operational else 'Warning.TLabel'
        )
        self.toggle_btn.config(text="⏸️" if self.is_operational else "▶️")
    
    def setup_notebook(self, parent: ttk.Frame) -> None:
        """Configurar notebook com abas (equivalente ao Tabs do React)"""
        self.notebook = ttk.Notebook(parent)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Aba Domínios
        domains_frame = ttk.Frame(self.notebook)
        self.notebook.add(domains_frame, text="📚 Domínios")
        self.setup_domains_tab(domains_frame)
        
        # Aba Módulos Cognitivos
        modules_frame = ttk.Frame(self.notebook)
        self.notebook.add(modules_frame, text="🧠 Módulos")
        self.setup_modules_tab(modules_frame)
        
        # Aba Conhecimento
        knowledge_frame = ttk.Frame(self.notebook)
        self.notebook.add(knowledge_frame, text="🔍 Conhecimento")
        self.setup_knowledge_tab(knowledge_frame)
        
        # Aba Decisões
        decisions_frame = ttk.Frame(self.notebook)
        self.notebook.add(decisions_frame, text="⚙️ Decisões")
        self.setup_decisions_tab(decisions_frame)
        
        # Aba Métricas
        metrics_frame = ttk.Frame(self.notebook)
        self.notebook.add(metrics_frame, text="📈 Métricas")
        self.setup_metrics_tab(metrics_frame)
        
        # Aba Bases de Mercado
        bases_frame = ttk.Frame(self.notebook)
        self.notebook.add(bases_frame, text="🗄️ Bases de Mercado")
        self.setup_bases_tab(bases_frame)
    
    def setup_domains_tab(self, parent: ttk.Frame) -> None:
        """Configurar aba de domínios (equivalente ao TabsContent domínios)"""
        # Cabeçalho da aba
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(10, 20))
        
        title_label = ttk.Label(header_frame, 
                               text="📚 Aprendizado Multidisciplinar", 
                               font=("Arial", 16, "bold"),
                               style='Info.TLabel')
        title_label.grid(row=0, column=0)
        
        desc_label = ttk.Label(header_frame, 
                              text="Competências cognitivas especializadas da IAG para dominar múltiplos aspectos do trading",
                              font=("Arial", 10))
        desc_label.grid(row=1, column=0, pady=(5, 0))
        
        # Canvas com scroll para domínios
        canvas = tk.Canvas(parent, bg='#f8fafc')
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        domains_container = ttk.Frame(canvas)
        
        domains_container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=domains_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Criar cards de domínios (equivalente ao IAGDomainCard)
        for i, domain in enumerate(self.iag_domains):
            self.create_domain_card(domains_container, domain, i)
        
        canvas.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        domains_container.columnconfigure(0, weight=1)
    
    def create_domain_card(self, parent: ttk.Frame, domain: IAGDomain, index: int) -> None:
        """Criar card individual de domínio (equivalente ao IAGDomainCard)"""
        card_frame = ttk.LabelFrame(parent, 
                                   text=f"📖 {domain.name}", 
                                   padding="15",
                                   style='Card.TFrame')
        card_frame.grid(row=index//2, column=index%2, sticky=(tk.W, tk.E), pady=8, padx=10)
        
        # Nível de autonomia
        autonomy_color = self.get_autonomy_color(domain.autonomy_level)
        autonomy_label = tk.Label(card_frame, 
                                 text=domain.autonomy_level.value,
                                 bg=autonomy_color,
                                 fg="white",
                                 font=("Arial", 8, "bold"),
                                 padx=8, pady=2)
        autonomy_label.grid(row=0, column=1, sticky=tk.E)
        
        # Descrição
        desc_label = ttk.Label(card_frame, text=domain.description, 
                              wraplength=350, font=("Arial", 9))
        desc_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 10))
        
        # Competência
        comp_frame = ttk.Frame(card_frame)
        comp_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Label(comp_frame, text="Competência:", font=("Arial", 8)).grid(row=0, column=0, sticky=tk.W)
        ttk.Label(comp_frame, text=f"{domain.competency:.1f}%", 
                 font=("Arial", 8, "bold"), style='Info.TLabel').grid(row=0, column=1, sticky=tk.E)
        
        # Simular barra de progresso
        progress_frame = ttk.Frame(comp_frame, relief='sunken', borderwidth=1)
        progress_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
        progress_width = int(domain.competency * 2)
        progress_label = tk.Label(progress_frame, 
                                text="", 
                                bg="#3b82f6", 
                                width=progress_width//8 if progress_width > 0 else 1,
                                height=1)
        progress_label.grid(row=0, column=0, sticky=tk.W)
        
        comp_frame.columnconfigure(0, weight=1)
        
        # Grid de métricas
        metrics_frame = ttk.Frame(card_frame)
        metrics_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 10))
        
        # Progresso
        ttk.Label(metrics_frame, text="Progresso", font=("Arial", 8)).grid(row=0, column=0)
        ttk.Label(metrics_frame, text=f"{domain.learning_progress:.1f}%", 
                 font=("Arial", 8, "bold"), style='Success.TLabel').grid(row=1, column=0)
        
        # Conexões
        ttk.Label(metrics_frame, text="Conexões", font=("Arial", 8)).grid(row=0, column=1, padx=(20, 0))
        ttk.Label(metrics_frame, text=f"{domain.active_connections:,}", 
                 font=("Arial", 8, "bold")).grid(row=1, column=1, padx=(20, 0))
        
        # Status de adaptação
        if domain.is_adapting:
            adapt_label = ttk.Label(card_frame, text="🔄 Adaptando-se...", 
                                   font=("Arial", 8), style='Warning.TLabel')
            adapt_label.grid(row=4, column=0, columnspan=2, sticky=tk.W)
        
        card_frame.columnconfigure(0, weight=1)
    
    def setup_modules_tab(self, parent: ttk.Frame) -> None:
        """Configurar aba de módulos cognitivos (equivalente ao TabsContent cognitivo)"""
        # Cabeçalho da aba
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(10, 20))
        
        title_label = ttk.Label(header_frame, 
                               text="🧠 Módulos Cognitivos", 
                               font=("Arial", 16, "bold"),
                               style='Info.TLabel')
        title_label.grid(row=0, column=0)
        
        desc_label = ttk.Label(header_frame, 
                              text="Sistemas especializados que operam em paralelo para decisões inteligentes",
                              font=("Arial", 10))
        desc_label.grid(row=1, column=0, pady=(5, 0))
        
        # Canvas com scroll para módulos
        canvas = tk.Canvas(parent, bg='#f8fafc')
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        modules_container = ttk.Frame(canvas)
        
        modules_container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=modules_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Criar cards de módulos (equivalente ao CognitiveModuleCard)
        for i, module in enumerate(self.cognitive_modules):
            self.create_module_card(modules_container, module, i)
        
        canvas.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        modules_container.columnconfigure(0, weight=1)
    
    def create_module_card(self, parent: ttk.Frame, module: CognitiveModule, index: int) -> None:
        """Criar card individual de módulo (equivalente ao CognitiveModuleCard)"""
        card_frame = ttk.LabelFrame(parent, 
                                   text=f"🤖 {module.name}", 
                                   padding="15",
                                   style='Card.TFrame')
        card_frame.grid(row=index, column=0, sticky=(tk.W, tk.E), pady=8, padx=10)
        
        # Header do módulo
        header_frame = ttk.Frame(card_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Tipo do módulo
        type_color = self.get_module_type_color(module.type)
        type_label = tk.Label(header_frame, 
                             text=module.type.value,
                             fg=type_color,
                             font=("Arial", 8, "bold"))
        type_label.grid(row=0, column=0, sticky=tk.W)
        
        # Status do módulo
        status_color = self.get_module_status_color(module.status)
        status_label = tk.Label(header_frame, 
                               text=module.status.value,
                               bg=status_color,
                               fg="white",
                               font=("Arial", 8, "bold"),
                               padx=8, pady=2)
        status_label.grid(row=0, column=1, sticky=tk.E)
        
        header_frame.columnconfigure(0, weight=1)
        
        # Tarefa atual
        task_label = ttk.Label(card_frame, 
                              text=f"Tarefa Atual: {module.current_task}",
                              font=("Arial", 9))
        task_label.grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        
        # Grid de métricas do módulo
        metrics_frame = ttk.Frame(card_frame)
        metrics_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Inteligência
        intel_frame = ttk.Frame(metrics_frame)
        intel_frame.grid(row=0, column=0, padx=(0, 15))
        
        ttk.Label(intel_frame, text="Inteligência", font=("Arial", 8)).grid(row=0, column=0)
        ttk.Label(intel_frame, text=f"{module.intelligence:.1f}%", 
                 font=("Arial", 8, "bold"), style='Info.TLabel').grid(row=1, column=0)
        
        # Criatividade
        creat_frame = ttk.Frame(metrics_frame)
        creat_frame.grid(row=0, column=1, padx=(0, 15))
        
        ttk.Label(creat_frame, text="Criatividade", font=("Arial", 8)).grid(row=0, column=0)
        ttk.Label(creat_frame, text=f"{module.creativity:.1f}%", 
                 font=("Arial", 8, "bold"), style='Purple.TLabel').grid(row=1, column=0)
        
        # Autonomia
        auton_frame = ttk.Frame(metrics_frame)
        auton_frame.grid(row=0, column=2)
        
        ttk.Label(auton_frame, text="Autonomia", font=("Arial", 8)).grid(row=0, column=0)
        ttk.Label(auton_frame, text=f"{module.autonomy:.1f}%", 
                 font=("Arial", 8, "bold"), style='Success.TLabel').grid(row=1, column=0)
        
        # Tarefas especializadas
        tasks_frame = ttk.Frame(card_frame)
        tasks_frame.grid(row=3, column=0, sticky=(tk.W, tk.E))
        
        ttk.Label(tasks_frame, text="Tarefas Especializadas:", 
                 font=("Arial", 8)).grid(row=0, column=0, sticky=tk.W)
        
        tasks_text = ", ".join(module.tasks)
        ttk.Label(tasks_frame, text=tasks_text, 
                 font=("Arial", 8), wraplength=600).grid(row=1, column=0, sticky=tk.W)
        
        card_frame.columnconfigure(0, weight=1)
    
    def setup_knowledge_tab(self, parent: ttk.Frame) -> None:
        """Configurar aba de conhecimento (equivalente ao TabsContent conhecimento)"""
        # Cabeçalho da aba
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(10, 20))
        
        title_label = ttk.Label(header_frame, 
                               text="🔍 Fontes de Conhecimento", 
                               font=("Arial", 16, "bold"),
                               style='Info.TLabel')
        title_label.grid(row=0, column=0)
        
        desc_label = ttk.Label(header_frame, 
                              text="Integração holística de dados para formar uma visão completa do mercado",
                              font=("Arial", 10))
        desc_label.grid(row=1, column=0, pady=(5, 0))
        
        # Canvas com scroll para fontes de conhecimento
        canvas = tk.Canvas(parent, bg='#f8fafc')
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        knowledge_container = ttk.Frame(canvas)
        
        knowledge_container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=knowledge_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Criar cards de fontes de conhecimento (equivalente ao KnowledgeSourceCard)
        for i, source in enumerate(self.knowledge_sources):
            self.create_knowledge_card(knowledge_container, source, i)
        
        canvas.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        knowledge_container.columnconfigure(0, weight=1)
    
    def create_knowledge_card(self, parent: ttk.Frame, source: KnowledgeSource, index: int) -> None:
        """Criar card individual de fonte de conhecimento (equivalente ao KnowledgeSourceCard)"""
        card_frame = ttk.LabelFrame(parent, 
                                   text=f"💾 {source.source}", 
                                   padding="15",
                                   style='Card.TFrame')
        card_frame.grid(row=index, column=0, sticky=(tk.W, tk.E), pady=8, padx=10)
        
        # Header com tipo e confiabilidade
        header_frame = ttk.Frame(card_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Tipo da fonte
        type_color = self.get_knowledge_type_color(source.type)
        type_label = tk.Label(header_frame, 
                             text=source.type.value.replace('_', ' ').title(),
                             fg=type_color,
                             font=("Arial", 8, "bold"))
        type_label.grid(row=0, column=0, sticky=tk.W)
        
        # Confiabilidade
        reliability_frame = ttk.Frame(header_frame)
        reliability_frame.grid(row=0, column=1, sticky=tk.E)
        
        ttk.Label(reliability_frame, text="Confiabilidade", font=("Arial", 8)).grid(row=0, column=0)
        ttk.Label(reliability_frame, text=f"{source.reliability:.1f}%", 
                 font=("Arial", 8, "bold"), style='Info.TLabel').grid(row=1, column=0)
        
        header_frame.columnconfigure(0, weight=1)
        
        # Pontos de dados
        data_label = ttk.Label(card_frame, 
                              text=f"📊 {source.data_points:,} pontos de dados",
                              font=("Arial", 9))
        data_label.grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        
        # Métricas
        metrics_frame = ttk.Frame(card_frame)
        metrics_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Impacto
        impact_frame = ttk.Frame(metrics_frame)
        impact_frame.grid(row=0, column=0)
        
        ttk.Label(impact_frame, text="Impacto", font=("Arial", 8)).grid(row=0, column=0)
        ttk.Label(impact_frame, text=f"{source.impact:.1f}%", 
                 font=("Arial", 8, "bold"), style='Success.TLabel').grid(row=1, column=0)
        
        # Última atualização
        update_frame = ttk.Frame(metrics_frame)
        update_frame.grid(row=0, column=1, padx=(30, 0))
        
        ttk.Label(update_frame, text="Última Atualização", font=("Arial", 8)).grid(row=0, column=0)
        ttk.Label(update_frame, text=source.last_update.strftime("%H:%M:%S"), 
                 font=("Arial", 8, "bold")).grid(row=1, column=0)
        
        # Insights recentes
        insights_frame = ttk.Frame(card_frame)
        insights_frame.grid(row=3, column=0, sticky=(tk.W, tk.E))
        
        ttk.Label(insights_frame, text="💡 Insights Recentes:", 
                 font=("Arial", 8)).grid(row=0, column=0, sticky=tk.W)
        
        for i, insight in enumerate(source.insights[:3]):  # Mostrar apenas os 3 primeiros
            insight_label = ttk.Label(insights_frame, 
                                     text=f"• {insight}",
                                     font=("Arial", 8),
                                     wraplength=600)
            insight_label.grid(row=i+1, column=0, sticky=tk.W, padx=(10, 0))
        
        card_frame.columnconfigure(0, weight=1)
    
    def setup_decisions_tab(self, parent: ttk.Frame) -> None:
        """Configurar aba de decisões (equivalente ao TabsContent decisões)"""
        # Cabeçalho da aba
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(10, 20))
        
        title_label = ttk.Label(header_frame, 
                               text="⚙️ Decisões Estratégicas Autônomas", 
                               font=("Arial", 16, "bold"),
                               style='Info.TLabel')
        title_label.grid(row=0, column=0)
        
        desc_label = ttk.Label(header_frame, 
                              text="Decisões inteligentes tomadas autonomamente com base em análise contextual",
                              font=("Arial", 10))
        desc_label.grid(row=1, column=0, pady=(5, 0))
        
        # Canvas com scroll para decisões
        canvas = tk.Canvas(parent, bg='#f8fafc')
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        decisions_container = ttk.Frame(canvas)
        
        decisions_container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=decisions_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Criar cards de decisões (equivalente ao StrategicDecisionCard)
        for i, decision in enumerate(self.strategic_decisions):
            self.create_decision_card(decisions_container, decision, i)
        
        canvas.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        decisions_container.columnconfigure(0, weight=1)
    
    def create_decision_card(self, parent: ttk.Frame, decision: StrategicDecision, index: int) -> None:
        """Criar card individual de decisão (equivalente ao StrategicDecisionCard)"""
        card_frame = ttk.LabelFrame(parent, 
                                   text=f"📝 Decisão Estratégica #{decision.id.split('_')[1]}", 
                                   padding="15",
                                   style='Card.TFrame')
        card_frame.grid(row=index, column=0, sticky=(tk.W, tk.E), pady=8, padx=10)
        
        # Contexto
        context_label = ttk.Label(card_frame, 
                                 text=f"Contexto: {decision.context}",
                                 font=("Arial", 9),
                                 wraplength=350)
        context_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # Decisão
        decision_frame = ttk.Frame(card_frame)
        decision_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(decision_frame, text="Decisão:", font=("Arial", 8)).grid(row=0, column=0, sticky=tk.W)
        ttk.Label(decision_frame, text=decision.decision, 
                 font=("Arial", 8, "bold"), style='Info.TLabel').grid(row=1, column=0, sticky=tk.W)
        
        # Confiança e Risco Avaliado
        risk_confidence_frame = ttk.Frame(card_frame)
        risk_confidence_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Confiança
        confidence_frame = ttk.Frame(risk_confidence_frame)
        confidence_frame.grid(row=0, column=0, padx=(0, 15))
        
        ttk.Label(confidence_frame, text="Confiança", font=("Arial", 8)).grid(row=0, column=0)
        ttk.Label(confidence_frame, text=f"{decision.confidence:.1f}%", 
                 font=("Arial", 8, "bold"), style='Info.TLabel').grid(row=1, column=0)
        
        # Risco Avaliado
        risk_frame = ttk.Frame(risk_confidence_frame)
        risk_frame.grid(row=0, column=1)
        
        ttk.Label(risk_frame, text="Risco Avaliado", font=("Arial", 8)).grid(row=0, column=0)
        ttk.Label(risk_frame, text=f"{decision.risk_assessment:.1f}%", 
                 font=("Arial", 8, "bold"), style='Warning.TLabel').grid(row=1, column=0)
        
        # Resultado Esperado e Fator Adaptativo
        outcome_factor_frame = ttk.Frame(card_frame)
        outcome_factor_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Resultado Esperado
        outcome_frame = ttk.Frame(outcome_factor_frame)
        outcome_frame.grid(row=0, column=0, padx=(0, 15))
        
        ttk.Label(outcome_frame, text="Resultado Esperado", font=("Arial", 8)).grid(row=0, column=0)
        ttk.Label(outcome_frame, text=decision.expected_outcome, 
                 font=("Arial", 8, "bold"), style='Success.TLabel').grid(row=1, column=0)
        
        # Fator Adaptativo
        factor_frame = ttk.Frame(outcome_factor_frame)
        factor_frame.grid(row=0, column=1)
        
        ttk.Label(factor_frame, text="Fator Adaptativo", font=("Arial", 8)).grid(row=0, column=0)
        ttk.Label(factor_frame, text=f"{decision.adaptive_factor:.1f}%", 
                 font=("Arial", 8, "bold")).grid(row=1, column=0)
        
        # Raciocínio da IA
        reasoning_frame = ttk.Frame(card_frame)
        reasoning_frame.grid(row=4, column=0, sticky=(tk.W, tk.E))
        
        ttk.Label(reasoning_frame, text="Raciocínio da IA:", 
                 font=("Arial", 8)).grid(row=0, column=0, sticky=tk.W)
        
        for i, reason in enumerate(decision.reasoning):
            reason_label = ttk.Label(reasoning_frame, 
                                   text=f"• {reason}",
                                   font=("Arial", 8),
                                   wraplength=600)
            reason_label.grid(row=i+1, column=0, sticky=tk.W, padx=(10, 0))
        
        card_frame.columnconfigure(0, weight=1)
    
    def setup_metrics_tab(self, parent: ttk.Frame) -> None:
        """Configurar aba de métricas (equivalente ao TabsContent métricas)"""
        # Cabeçalho da aba
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(10, 20))
        
        title_label = ttk.Label(header_frame, 
                               text="📈 Métricas de Performance da IAG", 
                               font=("Arial", 16, "bold"),
                               style='Info.TLabel')
        title_label.grid(row=0, column=0)
        
        desc_label = ttk.Label(header_frame, 
                              text="Indicadores de capacidade cognitiva e operacional da inteligência artificial",
                              font=("Arial", 10))
        desc_label.grid(row=1, column=0, pady=(5, 0))
        
        # Grid de métricas principais
        main_metrics_frame = ttk.Frame(parent)
        main_metrics_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Inteligência Geral
        intel_card = ttk.Card(main_metrics_frame, padding="10")
        intel_card.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(intel_card, text="Inteligência Geral", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W)
        intel_value = ttk.Label(intel_card, 
                               text=f"{self.iag_metrics.overall_intelligence:.1f}%",
                               font=("Arial", 16, "bold"),
                               style='Info.TLabel')
        intel_value.grid(row=1, column=0, sticky=tk.W)
        
        # Adaptabilidade
        adapt_card = ttk.Card(main_metrics_frame, padding="10")
        adapt_card.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(adapt_card, text="Adaptabilidade", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W)
        adapt_value = ttk.Label(adapt_card, 
                               text=f"{self.iag_metrics.adaptability_index:.1f}%",
                               font=("Arial", 16, "bold"),
                               style='Success.TLabel')
        adapt_value.grid(row=1, column=0, sticky=tk.W)
        
        # Criatividade
        creat_card = ttk.Card(main_metrics_frame, padding="10")
        creat_card.grid(row=0, column=2, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(creat_card, text="Criatividade", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W)
        creat_value = ttk.Label(creat_card, 
                               text=f"{self.iag_metrics.creativity_score:.1f}%",
                               font=("Arial", 16, "bold"),
                               style='Purple.TLabel')
        creat_value.grid(row=1, column=0, sticky=tk.W)
        
        # Autonomia
        auton_card = ttk.Card(main_metrics_frame, padding="10")
        auton_card.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=5, pady=5)
        
        ttk.Label(auton_card, text="Autonomia", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W)
        auton_value = ttk.Label(auton_card, 
                               text=f"{self.iag_metrics.autonomy_level:.1f}%",
                               font=("Arial", 16, "bold"),
                               style='Success.TLabel')
        auton_value.grid(row=1, column=0, sticky=tk.W)
        
        # Grid de métricas detalhadas
        detail_metrics_frame = ttk.Frame(parent)
        detail_metrics_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Velocidade de Aprendizado
        ttk.Label(detail_metrics_frame, text="Velocidade de Aprendizado", font=("Arial", 9)).grid(row=0, column=0, sticky=tk.W)
        learning_value = ttk.Label(detail_metrics_frame, 
                                   text=f"{self.iag_metrics.learning_velocity:.1f}%",
                                   font=("Arial", 10, "bold"),
                                   style='Info.TLabel')
        learning_value.grid(row=1, column=0, sticky=tk.W)
        
        # Geração de Estratégias
        ttk.Label(detail_metrics_frame, text="Geração de Estratégias", font=("Arial", 9)).grid(row=0, column=1, sticky=tk.W)
        strategy_value = ttk.Label(detail_metrics_frame, 
                                   text=f"{self.iag_metrics.strategy_generation:.1f}%",
                                   font=("Arial", 10, "bold"),
                                   style='Info.TLabel')
        strategy_value.grid(row=1, column=1, sticky=tk.W)
        
        # Consciência de Risco
        ttk.Label(detail_metrics_frame, text="Consciência de Risco", font=("Arial", 9)).grid(row=0, column=2, sticky=tk.W)
        risk_value = ttk.Label(detail_metrics_frame, 
                             text=f"{self.iag_metrics.risk_awareness:.1f}%",
                             font=("Arial", 10, "bold"),
                             style='Warning.TLabel')
        risk_value.grid(row=1, column=2, sticky=tk.W)
        
        # Compreensão de Mercado
        ttk.Label(detail_metrics_frame, text="Compreensão de Mercado", font=("Arial", 9)).grid(row=0, column=3, sticky=tk.W)
        market_value = ttk.Label(detail_metrics_frame, 
                                text=f"{self.iag_metrics.market_understanding:.1f}%",
                                font=("Arial", 10, "bold"),
                                style='Info.TLabel')
        market_value.grid(row=1, column=3, sticky=tk.W)
        
        # Grid de métricas operacionais
        oper_metrics_frame = ttk.Frame(parent)
        oper_metrics_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Pontos de Dados Processados
        ttk.Label(oper_metrics_frame, text="Pontos de Dados Processados", font=("Arial", 9)).grid(row=0, column=0, sticky=tk.W)
        data_value = ttk.Label(oper_metrics_frame, 
                             text=f"{self.iag_metrics.processed_data_points / 1000000:.1f}M",
                             font=("Arial", 10, "bold"),
                             style='Info.TLabel')
        data_value.grid(row=1, column=0, sticky=tk.W)
        
        # Estratégias Ativas
        ttk.Label(oper_metrics_frame, text="Estratégias Ativas", font=("Arial", 9)).grid(row=0, column=1, sticky=tk.W)
        active_strategies_value = ttk.Label(oper_metrics_frame, 
                                           text=f"{self.iag_metrics.active_strategies}",
                                           font=("Arial", 10, "bold"),
                                           style='Success.TLabel')
        active_strategies_value.grid(row=1, column=1, sticky=tk.W)
        
        # Domínios Especializados
        ttk.Label(oper_metrics_frame, text="Domínios Especializados", font=("Arial", 9)).grid(row=0, column=2, sticky=tk.W)
        domains_value = ttk.Label(oper_metrics_frame, 
                                 text=f"{len(self.iag_domains)}",
                                 font=("Arial", 10, "bold"),
                                 style='Info.TLabel')
        domains_value.grid(row=1, column=2, sticky=tk.W)
        
        # Módulos Cognitivos
        ttk.Label(oper_metrics_frame, text="Módulos Cognitivos", font=("Arial", 9)).grid(row=0, column=3, sticky=tk.W)
        modules_value = ttk.Label(oper_metrics_frame, 
                                 text=f"{len(self.cognitive_modules)}",
                                 font=("Arial", 10, "bold"),
                                 style='Info.TLabel')
        modules_value.grid(row=1, column=3, sticky=tk.W)
        
        # Seção de características da IAG
        features_frame = ttk.Frame(parent)
        features_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        ttk.Label(features_frame, 
                 text="Características da IAG para Day Trade", 
                 font=("Arial", 12, "bold"),
                 style='Info.TLabel').grid(row=0, column=0, sticky=tk.W)
        
        features_list = [
            "Compreensão contextual completa do mercado",
            "Adaptação autônoma a novas condições",
            "Criação independente de estratégias",
            "Processamento multi-domínio simultâneo",
            "Consciência operacional avançada",
            "Gestão dinâmica de risco em tempo real",
            "Aprendizado contínuo multi-fonte",
            "Execução autônoma inteligente"
        ]
        
        for i, feature in enumerate(features_list):
            ttk.Label(features_frame, 
                     text=f"• {feature}", 
                     font=("Arial", 10)).grid(row=i+1, column=0, sticky=tk.W)
        
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        oper_metrics_frame.columnconfigure(0, weight=1)
    
    def setup_bases_tab(self, parent: ttk.Frame) -> None:
        """Configurar aba de bases de mercado (equivalente ao TabsContent bases)"""
        # Cabeçalho da aba
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(10, 20))
        
        title_label = ttk.Label(header_frame, 
                               text="🗄️ Bases de Mercado", 
                               font=("Arial", 16, "bold"),
                               style='Info.TLabel')
        title_label.grid(row=0, column=0)
        
        desc_label = ttk.Label(header_frame, 
                              text="Plataformas, ferramentas e fontes de dados essenciais para análise técnica e day trade.",
                              font=("Arial", 10))
        desc_label.grid(row=1, column=0, pady=(5, 0))
        
        # Canvas com scroll
        canvas = tk.Canvas(parent, bg='#f8fafc')
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        bases_container = ttk.Frame(canvas)
        
        bases_container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=bases_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Seção de plataformas técnicas
        self.create_market_base_section(
            bases_container, 
            "📊 Plataformas de Análise Técnica", 
            MARKET_BASES['technical_platforms'], 
            0
        )
        
        # Seção de ferramentas de day trade
        self.create_market_base_section(
            bases_container, 
            "🖥️ Ferramentas Estratégicas para Day Trade", 
            MARKET_BASES['day_trade_tools'], 
            1
        )
        
        # Seção de fontes de dados
        self.create_market_base_section(
            bases_container, 
            "🌐 Fontes de Dados e Comunidade", 
            MARKET_BASES['data_sources_and_community'], 
            2
        )
        
        canvas.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        bases_container.columnconfigure(0, weight=1)
    
    def create_market_base_section(self, parent: ttk.Frame, title: str, items: List[MarketBase], row: int) -> None:
        """Criar seção de bases de mercado"""
        section_frame = ttk.LabelFrame(parent, text=title, padding="15")
        section_frame.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=10, padx=10)
        
        for i, item in enumerate(items):
            self.create_market_base_card(section_frame, item, i)
        
        section_frame.columnconfigure(0, weight=1)
    
    def create_market_base_card(self, parent: ttk.Frame, item: MarketBase, index: int) -> None:
        """Criar card individual de base de mercado (equivalente ao MarketBaseCard)"""
        card_frame = ttk.Frame(parent, style='Card.TFrame', padding="10")
        card_frame.grid(row=index//3, column=index%3, sticky=(tk.W, tk.E), pady=5, padx=5)
        
        # Nome da plataforma
        name_label = ttk.Label(card_frame, 
                              text=item.name,
                              font=("Arial", 10, "bold"),
                              style='Info.TLabel')
        name_label.grid(row=0, column=0, sticky=tk.W)
        
        # Descrição
        desc_label = ttk.Label(card_frame, 
                              text=item.description,
                              font=("Arial", 8),
                              wraplength=250)
        desc_label.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        # Indicadores (se houver)
        if item.indicators:
            indicators_text = f"Indicadores: {', '.join(item.indicators)}"
            indicators_label = ttk.Label(card_frame, 
                                        text=indicators_text,
                                        font=("Arial", 8))
            indicators_label.grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        
        # Link
        link_btn = ttk.Button(card_frame, 
                             text=f"🔗 Acessar {item.name}",
                             command=lambda url=item.url: self.open_url(url))
        link_btn.grid(row=3, column=0, sticky=tk.W, pady=(10, 0))
        
        card_frame.columnconfigure(0, weight=1)
    
    def start_update_thread(self) -> None:
        """Iniciar thread de atualização periódica (equivalente ao useEffect)"""
        def update_worker():
            while True:
                if not self.is_operational:
                    time.sleep(5)
                    continue
                
                # Atualizar dados (equivalente ao updateIAGSystem)
                self.iag_domains = [
                    IAGDomain(
                        name=domain.name,
                        description=domain.description,
                        competency=max(95, min(100, domain.competency + (random.random() - 0.1) * 1.2)),
                        autonomy_level=domain.autonomy_level,
                        learning_progress=max(95, min(100, domain.learning_progress + (random.random() - 0.1) * 1.5)),
                        active_connections=domain.active_connections + int((random.random() - 0.3) * 500),
                        is_adapting=random.random() > 0.2
                    )
                    for domain in self.iag_domains
                ]
                
                self.cognitive_modules = [
                    CognitiveModule(
                        id=module.id,
                        name=module.name,
                        type=module.type,
                        status=module.status,
                        intelligence=max(95, min(100, module.intelligence + (random.random() - 0.1) * 1.2)),
                        creativity=max(85, min(100, module.creativity + (random.random() - 0.1) * 1.5)),
                        autonomy=max(95, min(100, module.autonomy + (random.random() - 0.1) * 1.2)),
                        tasks=module.tasks,
                        current_task=module.current_task
                    )
                    for module in self.cognitive_modules
                ]
                
                self.iag_metrics = self.calculate_iag_metrics()
                self.uptime += 5
                self.processing_load = max(50, min(100, self.processing_load + (random.random() - 0.5) * 2))
                self.data_throughput = max(1000, min(2000, self.data_throughput + (random.random() - 0.5) * 10))
                
                time.sleep(5)  # Equivalente ao interval de 5000ms do React
        
        threading.Thread(target=update_worker, daemon=True).start()


def main() -> None:
    """Função principal para executar a aplicação (equivalente ao export do React)"""
    root = tk.Tk()
    app = AdvancedNeuralEngineApp(root)
    
    # Tornar a janela responsiva
    root.minsize(1200, 800)
    
    # Centralizar janela
    root.eval('tk::PlaceWindow . center')
    
    # Iniciar loop principal
    root.mainloop()


if __name__ == "__main__":
    main()
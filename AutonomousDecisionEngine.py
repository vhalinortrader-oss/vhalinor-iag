import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import dataclass
from typing import List, Dict, Optional, Literal
from datetime import datetime
import threading
import time
import random
from enum import Enum

# Enums para tipos de dados
class Action(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    TAKE_PROFIT = "TAKE_PROFIT"
    STOP_LOSS = "STOP_LOSS"

class Status(Enum):
    PENDING = "PENDING"
    EXECUTED = "EXECUTED"
    CANCELLED = "CANCELLED"

class BollingerPosition(Enum):
    UPPER = "UPPER"
    MIDDLE = "MIDDLE"
    LOWER = "LOWER"

# Estruturas de dados equivalentes às interfaces TypeScript
@dataclass
class TechnicalIndicators:
    rsi: float
    macd: float
    bollinger: BollingerPosition
    volume: float
    volatility: float

@dataclass
class AutonomousDecision:
    id: str
    symbol: str
    action: Action
    confidence: float
    reasoning: str
    entry_price: float
    current_price: float
    take_profit_price: float
    stop_loss_price: float
    risk_reward_ratio: float
    expected_return: float
    risk_level: float
    timeframe: str
    timestamp: datetime
    status: Status
    neural_network_score: float
    technical_indicators: TechnicalIndicators

@dataclass
class RiskManagementParams:
    max_risk_per_trade: float
    max_portfolio_risk: float
    dynamic_stop_loss: bool
    trailing_take_profit: bool
    risk_reward_min_ratio: float
    volatility_adjustment: bool

class AutonomousDecisionEngineApp:
    """Aplicação principal que replica a funcionalidade do componente React AutonomousDecisionEngine"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("🤖 Sistema Autônomo de Decisões")
        self.root.geometry("1500x1000")
        self.root.configure(bg='#f8fafc')
        
        # Estado da aplicação (equivalente aos useState hooks)
        self.decisions: List[AutonomousDecision] = []
        self.risk_params = RiskManagementParams(
            max_risk_per_trade=2.0,
            max_portfolio_risk=8.0,
            dynamic_stop_loss=True,
            trailing_take_profit=True,
            risk_reward_min_ratio=2.5,
            volatility_adjustment=True
        )
        self.is_autonomous_mode = True
        self.total_profit = 0.0
        self.success_rate = 0.0
        self.current_risk = 0.0
        
        # Containers para widgets que precisam ser atualizados
        self.autonomous_badge = None
        self.toggle_button = None
        self.metrics_labels = {}
        self.decision_frames = []
        
        # Configurar estilos
        self.setup_styles()
        
        # Inicializar dados
        self.initialize_data()
        
        # Configurar interface
        self.setup_ui()
        
        # Iniciar thread de decisões autônomas (equivalente ao useEffect)
        self.start_autonomous_engine()
    
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
        style.configure('Muted.TLabel', foreground='#6b7280')
        
        style.configure('Card.TFrame', 
                       background='white', 
                       relief='solid',
                       borderwidth=1)
    
    # Funções utilitárias (equivalentes às funções do React)
    def get_action_color(self, action: Action) -> str:
        """Obter cor para ação (equivalente a getActionColor)"""
        color_map = {
            Action.BUY: "#10b981",
            Action.SELL: "#ef4444",
            Action.TAKE_PROFIT: "#10b981",
            Action.STOP_LOSS: "#ef4444",
            Action.HOLD: "#6b7280"
        }
        return color_map.get(action, "#6b7280")
    
    def get_action_icon(self, action: Action) -> str:
        """Obter ícone para ação (equivalente a getActionIcon)"""
        icon_map = {
            Action.BUY: "📈",
            Action.SELL: "📉",
            Action.TAKE_PROFIT: "🎯",
            Action.STOP_LOSS: "🛡️",
            Action.HOLD: "📊"
        }
        return icon_map.get(action, "📊")
    
    def show_toast(self, message: str) -> None:
        """Mostrar notificação toast (equivalente ao toast)"""
        messagebox.showinfo("Sistema Autônomo", message)
    
    # Funções de geração de decisões (equivalentes às funções do React)
    def generate_decision(self) -> AutonomousDecision:
        """Gerar decisão autônoma (equivalente a generateDecision)"""
        symbols = ['PETR4', 'VALE3', 'ITUB4', 'BBDC4', 'ABEV3', 'BTCBRL', 'ETHBRL']
        actions = list(Action)
        
        symbol = random.choice(symbols)
        action = random.choice(actions)
        
        current_price = 20 + random.random() * 100
        volatility = 0.02 + random.random() * 0.08
        risk_level = random.random() * 10
        
        # Cálculos baseados em IA para take profit e stop loss
        stop_loss_distance = current_price * (0.03 + volatility)
        take_profit_distance = current_price * (0.08 + volatility * 2)
        
        if action == Action.BUY:
            entry_price = current_price
            take_profit_price = current_price + take_profit_distance
            stop_loss_price = current_price - stop_loss_distance
        elif action == Action.SELL:
            entry_price = current_price
            take_profit_price = current_price - take_profit_distance
            stop_loss_price = current_price + stop_loss_distance
        else:
            entry_price = current_price * (0.95 + random.random() * 0.1)
            take_profit_price = entry_price * 1.12 if action == Action.TAKE_PROFIT else entry_price * 0.88
            stop_loss_price = entry_price * 0.95 if action == Action.STOP_LOSS else entry_price * 1.05
        
        risk_reward_ratio = abs(take_profit_price - entry_price) / abs(entry_price - stop_loss_price)
        
        return AutonomousDecision(
            id=f"decision_{int(time.time())}_{random.randint(1000, 9999)}",
            symbol=symbol,
            action=action,
            confidence=70 + random.random() * 30,
            reasoning=self.generate_reasoning(action, symbol, risk_reward_ratio),
            entry_price=entry_price,
            current_price=current_price,
            take_profit_price=take_profit_price,
            stop_loss_price=stop_loss_price,
            risk_reward_ratio=risk_reward_ratio,
            expected_return=((take_profit_price - entry_price) / entry_price) * 100,
            risk_level=risk_level,
            timeframe=random.choice(['5M', '15M', '1H', '4H']),
            timestamp=datetime.now(),
            status=Status.EXECUTED if random.random() > 0.7 else Status.PENDING,
            neural_network_score=80 + random.random() * 20,
            technical_indicators=TechnicalIndicators(
                rsi=30 + random.random() * 40,
                macd=-0.5 + random.random(),
                bollinger=random.choice(list(BollingerPosition)),
                volume=1000000 + random.random() * 5000000,
                volatility=volatility * 100
            )
        )
    
    def generate_reasoning(self, action: Action, symbol: str, ratio: float) -> str:
        """Gerar raciocínio para a decisão (equivalente a generateReasoning)"""
        reasons = {
            Action.BUY: [
                f"Padrão de reversão alta detectado em {symbol}. RSI sobrevenda + divergência MACD positiva. R/R: {ratio:.2f}",
                f"Breakout confirmado acima da resistência key. Volume institucional aumentando. Momentum bullish forte.",
                f"Confluência de suportes técnicos. Análise neural indica probabilidade 87% de movimento ascendente."
            ],
            Action.SELL: [
                f"Sinal de exaustão de alta em {symbol}. RSI sobrecompra + padrão de distribuição detectado.",
                f"Ruptura de suporte crítico confirmada. Volume bearish crescente. Momentum descendente.",
                f"Divergência bearish identificada. Rede neural sugere correção iminente com R/R favorável."
            ],
            Action.TAKE_PROFIT: [
                f"Meta de lucro atingida. Preservação de ganhos prioritária. Sinais de possível reversão detectados.",
                f"R/R ótimo alcançado ({ratio:.2f}). Estratégia de realização parcial para maximizar lucros.",
                f"Resistência técnica forte próxima. Rede neural recomenda realização antes da correção."
            ],
            Action.STOP_LOSS: [
                f"Gestão de risco ativada. Cenário mudou desfavoravelmente. Preservação de capital prioritária.",
                f"Stop dinâmico ajustado pela volatilidade. Proteção contra movimento adverso maior.",
                f"Sinal de invalidação da tese original. Rede neural detectou mudança de tendência."
            ],
            Action.HOLD: [
                f"Posição mantida. Condições de mercado neutras. Aguardando sinal definitivo da IA.",
                f"Análise inconclusa. Manter posição até confirmação de breakout ou breakdown."
            ]
        }
        
        action_reasons = reasons.get(action, reasons[Action.HOLD])
        return random.choice(action_reasons)
    
    # Funções de controle principal
    def toggle_autonomous_mode(self) -> None:
        """Alternar modo autônomo (equivalente ao onClick do botão)"""
        self.is_autonomous_mode = not self.is_autonomous_mode
        self.update_autonomous_display()
        
        if self.is_autonomous_mode:
            self.show_toast("Modo Autônomo Ativado - IA assumiu controle das decisões")
        else:
            self.show_toast("Modo Manual Ativado - Decisões pausadas")
    
    def update_autonomous_display(self) -> None:
        """Atualizar display do modo autônomo"""
        if self.autonomous_badge:
            mode_text = "🧠 AUTÔNOMO" if self.is_autonomous_mode else "👤 MANUAL"
            mode_color = "#10b981" if self.is_autonomous_mode else "#6b7280"
            self.autonomous_badge.config(text=mode_text, bg=mode_color)
        
        if self.toggle_button:
            button_text = "Pausar IA" if self.is_autonomous_mode else "Ativar IA"
            self.toggle_button.config(text=button_text)
    
    # Inicialização de dados
    def initialize_data(self) -> None:
        """Inicializar dados da aplicação (equivalente ao useEffect inicial)"""
        # Gerar decisões iniciais
        initial_decisions = [self.generate_decision() for _ in range(12)]
        self.decisions = initial_decisions
        
        # Calcular métricas iniciais
        executed = [d for d in initial_decisions if d.status == Status.EXECUTED]
        profitable = [d for d in executed if d.expected_return > 0]
        
        self.success_rate = (len(profitable) / max(len(executed), 1)) * 100
        self.total_profit = sum(d.expected_return for d in executed)
        self.current_risk = random.random() * 5 + 2
    
    # Configuração da interface gráfica
    def setup_ui(self) -> None:
        """Configurar interface principal"""
        # Frame principal com scroll
        main_canvas = tk.Canvas(self.root, bg='#f8fafc')
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Container principal
        container = ttk.Frame(scrollable_frame, padding="20", style='Card.TFrame')
        container.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=20, pady=20)
        
        # Cabeçalho
        self.setup_header(container)
        
        # Sistema de proteção
        self.setup_protection_alert(container)
        
        # Notebook para abas (equivalente ao Tabs do React)
        self.setup_notebook(container)
        
        # Configurar scroll
        main_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configurar redimensionamento
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        scrollable_frame.columnconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)
    
    def setup_header(self, parent: ttk.Frame) -> None:
        """Configurar cabeçalho da aplicação"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Título
        title_label = ttk.Label(header_frame, 
                               text="🤖 Sistema Autônomo de Decisões", 
                               font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        # Controles
        control_frame = ttk.Frame(header_frame)
        control_frame.grid(row=0, column=1, sticky=tk.E)
        
        # Badge de modo
        mode_text = "🧠 AUTÔNOMO" if self.is_autonomous_mode else "👤 MANUAL"
        mode_color = "#10b981" if self.is_autonomous_mode else "#6b7280"
        self.autonomous_badge = tk.Label(control_frame, 
                                        text=mode_text,
                                        bg=mode_color,
                                        fg="white",
                                        font=("Arial", 10, "bold"),
                                        padx=10, pady=5)
        self.autonomous_badge.grid(row=0, column=0, padx=(0, 10))
        
        # Botão toggle
        button_text = "Pausar IA" if self.is_autonomous_mode else "Ativar IA"
        self.toggle_button = ttk.Button(control_frame, 
                                       text=button_text,
                                       command=self.toggle_autonomous_mode,
                                       style='Primary.TButton')
        self.toggle_button.grid(row=0, column=1)
        
        header_frame.columnconfigure(0, weight=1)
    
    def setup_protection_alert(self, parent: ttk.Frame) -> None:
        """Configurar alerta de proteção neural"""
        protection_frame = tk.Frame(parent, bg="#f0fdf4", relief='solid', 
                                   borderwidth=1, highlightbackground="#bbf7d0", 
                                   highlightthickness=1)
        protection_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Ícone e conteúdo
        content_frame = tk.Frame(protection_frame, bg="#f0fdf4")
        content_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=15, pady=10)
        
        # Ícone de proteção
        icon_label = tk.Label(content_frame, text="🛡️", bg="#f0fdf4", font=("Arial", 14))
        icon_label.grid(row=0, column=0, padx=(0, 10))
        
        # Texto de proteção
        text_frame = tk.Frame(content_frame, bg="#f0fdf4")
        text_frame.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        title_label = tk.Label(text_frame, text="Proteção Neural Ativa:", 
                              bg="#f0fdf4", fg="#15803d", font=("Arial", 10, "bold"))
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        desc_label = tk.Label(text_frame, 
                             text="Sistema bloqueando automaticamente decisões que possam prejudicar os ganhos. Proteção baseada em análises técnicas com 94.2% de eficiência.",
                             bg="#f0fdf4", fg="#16a34a", font=("Arial", 9),
                             wraplength=800)
        desc_label.grid(row=1, column=0, sticky=tk.W)
        
        text_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        protection_frame.columnconfigure(0, weight=1)
    
    def setup_notebook(self, parent: ttk.Frame) -> None:
        """Configurar notebook com abas (equivalente ao Tabs do React)"""
        self.notebook = ttk.Notebook(parent)
        self.notebook.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Aba Decisões IA
        decisions_frame = ttk.Frame(self.notebook)
        self.notebook.add(decisions_frame, text="🎯 Decisões IA")
        self.setup_decisions_tab(decisions_frame)
        
        # Aba Performance
        performance_frame = ttk.Frame(self.notebook)
        self.notebook.add(performance_frame, text="📈 Performance")
        self.setup_performance_tab(performance_frame)
        
        # Aba Gestão de Risco
        risk_frame = ttk.Frame(self.notebook)
        self.notebook.add(risk_frame, text="🛡️ Gestão de Risco")
        self.setup_risk_tab(risk_frame)
    
    def setup_decisions_tab(self, parent: ttk.Frame) -> None:
        """Configurar aba de decisões (equivalente ao TabsContent decisions)"""
        decisions_container = ttk.Frame(parent, padding="20")
        decisions_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Grid de métricas
        metrics_grid = ttk.Frame(decisions_container)
        metrics_grid.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Lucro Total
        profit_card = ttk.LabelFrame(metrics_grid, text="💰 Lucro Total", padding="15")
        profit_card.grid(row=0, column=0, padx=(0, 10), sticky=(tk.W, tk.E))
        
        profit_text = f"{'+' if self.total_profit > 0 else ''}{self.total_profit:.2f}%"
        self.metrics_labels['profit'] = ttk.Label(profit_card, text=profit_text, 
                                                 font=("Arial", 16, "bold"), style='Info.TLabel')
        self.metrics_labels['profit'].grid(row=0, column=0)
        
        # Taxa Sucesso
        success_card = ttk.LabelFrame(metrics_grid, text="🎯 Taxa Sucesso", padding="15")
        success_card.grid(row=0, column=1, padx=(0, 10), sticky=(tk.W, tk.E))
        
        self.metrics_labels['success'] = ttk.Label(success_card, text=f"{self.success_rate:.1f}%", 
                                                  font=("Arial", 16, "bold"), style='Info.TLabel')
        self.metrics_labels['success'].grid(row=0, column=0)
        
        # Risco Atual
        risk_card = ttk.LabelFrame(metrics_grid, text="⚡ Risco Atual", padding="15")
        risk_card.grid(row=0, column=2, sticky=(tk.W, tk.E))
        
        self.metrics_labels['risk'] = ttk.Label(risk_card, text=f"{self.current_risk:.1f}%", 
                                               font=("Arial", 16, "bold"), style='Info.TLabel')
        self.metrics_labels['risk'].grid(row=0, column=0)
        
        # Configurar grid
        for i in range(3):
            metrics_grid.columnconfigure(i, weight=1)
        
        # Canvas com scroll para decisões
        canvas = tk.Canvas(decisions_container, bg='#f8fafc', height=400)
        scrollbar = ttk.Scrollbar(decisions_container, orient="vertical", command=canvas.yview)
        decisions_scrollable = ttk.Frame(canvas)
        
        decisions_scrollable.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=decisions_scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Criar cards de decisões
        self.decision_frames = []
        for i, decision in enumerate(self.decisions):
            frame = self.create_decision_card(decisions_scrollable, decision, i)
            self.decision_frames.append(frame)
        
        canvas.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        decisions_container.columnconfigure(0, weight=1)
        decisions_container.rowconfigure(1, weight=1)
        decisions_scrollable.columnconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
    
    def create_decision_card(self, parent: ttk.Frame, decision: AutonomousDecision, index: int) -> ttk.Frame:
        """Criar card individual de decisão"""
        card_frame = ttk.LabelFrame(parent, text="", padding="15", style='Card.TFrame')
        card_frame.grid(row=index, column=0, sticky=(tk.W, tk.E), pady=8, padx=10)
        
        # Header da decisão
        header_frame = ttk.Frame(card_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Lado esquerdo: badges
        left_frame = ttk.Frame(header_frame)
        left_frame.grid(row=0, column=0, sticky=tk.W)
        
        # Badge de ação
        action_color = self.get_action_color(decision.action)
        action_icon = self.get_action_icon(decision.action)
        action_label = tk.Label(left_frame, 
                               text=f"{action_icon} {decision.action.value}",
                               bg=action_color,
                               fg="white",
                               font=("Arial", 8, "bold"),
                               padx=8, pady=2)
        action_label.grid(row=0, column=0, padx=(0, 5))
        
        # Badge símbolo
        symbol_label = tk.Label(left_frame, 
                               text=decision.symbol,
                               bg="white",
                               fg="#6b7280",
                               font=("Courier", 8, "bold"),
                               relief='solid',
                               borderwidth=1,
                               padx=6, pady=2)
        symbol_label.grid(row=0, column=1, padx=(0, 5))
        
        # Badge timeframe
        timeframe_label = tk.Label(left_frame, 
                                  text=decision.timeframe,
                                  bg="white",
                                  fg="#6b7280",
                                  font=("Arial", 8),
                                  relief='solid',
                                  borderwidth=1,
                                  padx=6, pady=2)
        timeframe_label.grid(row=0, column=2)
        
        # Lado direito: status e timestamp
        right_frame = ttk.Frame(header_frame)
        right_frame.grid(row=0, column=1, sticky=tk.E)
        
        # Status
        status_color = "#10b981" if decision.status == Status.EXECUTED else "#6b7280"
        status_label = tk.Label(right_frame, 
                               text=decision.status.value,
                               bg=status_color,
                               fg="white",
                               font=("Arial", 8, "bold"),
                               padx=6, pady=2)
        status_label.grid(row=0, column=0, padx=(0, 10))
        
        # Timestamp
        timestamp_str = decision.timestamp.strftime("%H:%M")
        ttk.Label(right_frame, text=timestamp_str, 
                 style='Muted.TLabel', font=("Arial", 8)).grid(row=0, column=1)
        
        header_frame.columnconfigure(0, weight=1)
        
        # Confiança IA
        confidence_frame = ttk.Frame(card_frame)
        confidence_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(confidence_frame, text="Confiança IA", 
                 style='Muted.TLabel', font=("Arial", 9)).grid(row=0, column=0, sticky=tk.W)
        ttk.Label(confidence_frame, text=f"{decision.confidence:.1f}%", 
                 font=("Arial", 9, "bold"), style='Info.TLabel').grid(row=0, column=1, sticky=tk.E)
        
        # Simular barra de progresso
        progress_frame = ttk.Frame(confidence_frame, relief='sunken', borderwidth=1)
        progress_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        
        progress_width = int(decision.confidence * 3)
        progress_label = tk.Label(progress_frame, 
                                 text="", 
                                 bg="#3b82f6", 
                                 width=progress_width//8 if progress_width > 0 else 1,
                                 height=1)
        progress_label.grid(row=0, column=0, sticky=tk.W)
        
        confidence_frame.columnconfigure(0, weight=1)
        
        # Grid de preços
        prices_frame = ttk.Frame(card_frame)
        prices_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        price_data = [
            ("Entrada", f"R$ {decision.entry_price:.2f}", "#6b7280"),
            ("Take Profit", f"R$ {decision.take_profit_price:.2f}", "#10b981"),
            ("Stop Loss", f"R$ {decision.stop_loss_price:.2f}", "#ef4444"),
            ("R/R Ratio", f"{decision.risk_reward_ratio:.2f}", "#3b82f6")
        ]
        
        for i, (label, value, color) in enumerate(price_data):
            price_col = ttk.Frame(prices_frame)
            price_col.grid(row=0, column=i, padx=(0, 15) if i < 3 else (0, 0))
            
            ttk.Label(price_col, text=label, style='Muted.TLabel', 
                     font=("Arial", 8)).grid(row=0, column=0)
            
            value_label = tk.Label(price_col, text=value, fg=color, 
                                  font=("Arial", 8, "bold"), bg='#f8fafc')
            value_label.grid(row=1, column=0)
        
        # Análise Neural
        analysis_frame = tk.Frame(card_frame, bg="#f1f5f9", relief='solid', borderwidth=1)
        analysis_frame.grid(row=3, column=0, sticky=(tk.W, tk.E))
        
        analysis_content = tk.Frame(analysis_frame, bg="#f1f5f9")
        analysis_content.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=15, pady=10)
        
        # Título da análise
        analysis_title = tk.Label(analysis_content, text="Análise Neural:", 
                                 bg="#f1f5f9", fg="#6b7280", font=("Arial", 8, "bold"))
        analysis_title.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # Reasoning
        reasoning_label = tk.Label(analysis_content, text=decision.reasoning, 
                                  bg="#f1f5f9", fg="#6b7280", font=("Arial", 8),
                                  wraplength=700, anchor="w", justify="left")
        reasoning_label.grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        
        # Métricas técnicas
        tech_frame = tk.Frame(analysis_content, bg="#f1f5f9")
        tech_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        tech_data = [
            ("Score IA", f"{decision.neural_network_score:.1f}"),
            ("RSI", f"{decision.technical_indicators.rsi:.1f}"),
            ("Vol", f"{decision.technical_indicators.volatility:.1f}%")
        ]
        
        for i, (label, value) in enumerate(tech_data):
            tech_label = tk.Label(tech_frame, text=f"{label}: {value}", 
                                 bg="#f1f5f9", fg="#6b7280", font=("Arial", 8, "bold"))
            tech_label.grid(row=0, column=i, padx=(0, 15) if i < 2 else (0, 0))
        
        tech_frame.columnconfigure(0, weight=1)
        analysis_content.columnconfigure(0, weight=1)
        analysis_frame.columnconfigure(0, weight=1)
        card_frame.columnconfigure(0, weight=1)
        
        return card_frame
    
    def setup_performance_tab(self, parent: ttk.Frame) -> None:
        """Configurar aba de performance (equivalente ao TabsContent performance)"""
        # ...existing code...
        pass
    
    def setup_risk_tab(self, parent: ttk.Frame) -> None:
        """Configurar aba de gestão de risco (equivalente ao TabsContent risk)"""
        # ...existing code...
        pass
    
    def update_displays(self) -> None:
        """Atualizar todos os displays da interface"""
        # Atualizar métricas
        if 'profit' in self.metrics_labels:
            profit_text = f"{'+' if self.total_profit > 0 else ''}{self.total_profit:.2f}%"
            self.metrics_labels['profit'].config(text=profit_text)
        
        if 'success' in self.metrics_labels:
            self.metrics_labels['success'].config(text=f"{self.success_rate:.1f}%")
        
        if 'risk' in self.metrics_labels:
            self.metrics_labels['risk'].config(text=f"{self.current_risk:.1f}%")
    
    def start_autonomous_engine(self) -> None:
        """Iniciar engine autônomo de decisões (equivalente ao useEffect)"""
        def autonomous_worker():
            while True:
                if self.is_autonomous_mode and random.random() > 0.4:
                    # Gerar nova decisão
                    new_decision = self.generate_decision()
                    self.decisions = [new_decision] + self.decisions[:19]  # Manter apenas 20
                    
                    # Atualizar métricas
                    if random.random() > 0.3:
                        self.total_profit += (random.random() - 0.3) * 5
                        self.success_rate = max(60, min(95, self.success_rate + (random.random() - 0.5) * 2))
                        self.current_risk = max(1, min(10, self.current_risk + (random.random() - 0.5) * 0.5))
                    
                    # Atualizar UI na thread principal
                    self.root.after(0, self.update_displays)
                
                time.sleep(5)  # Equivalente ao interval de 5000ms do React
        
        threading.Thread(target=autonomous_worker, daemon=True).start()


    def setup_performance_tab(self, parent: ttk.Frame) -> None:
        """Configurar aba de performance"""
        perf_container = ttk.Frame(parent, padding="20")
        perf_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Gráfico de performance simulado
        chart_frame = ttk.LabelFrame(perf_container, text="📊 Performance Histórica", padding="20")
        chart_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Simular gráfico com canvas
        canvas = tk.Canvas(chart_frame, width=800, height=200, bg='white')
        canvas.grid(row=0, column=0)
        
        # Desenhar linha de performance
        points = [(i * 80, 100 + random.randint(-50, 50)) for i in range(11)]
        for i in range(len(points) - 1):
            canvas.create_line(points[i][0], points[i][1], 
                             points[i+1][0], points[i+1][1],
                             fill='#3b82f6', width=2)
        
        # Estatísticas detalhadas
        stats_frame = ttk.LabelFrame(perf_container, text="📈 Estatísticas Detalhadas", padding="20")
        stats_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        stats_data = [
            ("Total de Decisões", str(len(self.decisions))),
            ("Decisões Executadas", str(len([d for d in self.decisions if d.status == Status.EXECUTED]))),
            ("Win Rate", f"{self.success_rate:.1f}%"),
            ("Lucro Médio", f"{self.total_profit / max(len(self.decisions), 1):.2f}%"),
            ("Melhor Trade", f"+{max([d.expected_return for d in self.decisions]):.2f}%"),
            ("Pior Trade", f"{min([d.expected_return for d in self.decisions]):.2f}%")
        ]
        
        for i, (label, value) in enumerate(stats_data):
            row = i // 3
            col = i % 3
            
            stat_frame = ttk.Frame(stats_frame)
            stat_frame.grid(row=row, column=col, padx=10, pady=5, sticky=tk.W)
            
            ttk.Label(stat_frame, text=label, style='Muted.TLabel', 
                     font=("Arial", 9)).grid(row=0, column=0, sticky=tk.W)
            ttk.Label(stat_frame, text=value, 
                     font=("Arial", 11, "bold")).grid(row=1, column=0, sticky=tk.W)
        
        perf_container.columnconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
    
    def setup_risk_tab(self, parent: ttk.Frame) -> None:
        """Configurar aba de gestão de risco"""
        risk_container = ttk.Frame(parent, padding="20")
        risk_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Parâmetros de risco
        params_frame = ttk.LabelFrame(risk_container, text="⚙️ Parâmetros de Risco", padding="20")
        params_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Max Risk per Trade
        ttk.Label(params_frame, text="Risco Máximo por Trade:", 
                 font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
        risk_scale = ttk.Scale(params_frame, from_=0.5, to=5.0, orient=tk.HORIZONTAL, length=300)
        risk_scale.set(self.risk_params.max_risk_per_trade)
        risk_scale.grid(row=0, column=1, padx=10)
        ttk.Label(params_frame, text=f"{self.risk_params.max_risk_per_trade:.1f}%", 
                 font=("Arial", 10, "bold")).grid(row=0, column=2)
        
        # Max Portfolio Risk
        ttk.Label(params_frame, text="Risco Máximo do Portfolio:", 
                 font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, pady=5)
        portfolio_scale = ttk.Scale(params_frame, from_=5.0, to=20.0, orient=tk.HORIZONTAL, length=300)
        portfolio_scale.set(self.risk_params.max_portfolio_risk)
        portfolio_scale.grid(row=1, column=1, padx=10)
        ttk.Label(params_frame, text=f"{self.risk_params.max_portfolio_risk:.1f}%", 
                 font=("Arial", 10, "bold")).grid(row=1, column=2)
        
        # Checkboxes
        ttk.Checkbutton(params_frame, text="Stop Loss Dinâmico", 
                       variable=tk.BooleanVar(value=self.risk_params.dynamic_stop_loss)).grid(
                           row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        ttk.Checkbutton(params_frame, text="Take Profit Trailing", 
                       variable=tk.BooleanVar(value=self.risk_params.trailing_take_profit)).grid(
                           row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        ttk.Checkbutton(params_frame, text="Ajuste por Volatilidade", 
                       variable=tk.BooleanVar(value=self.risk_params.volatility_adjustment)).grid(
                           row=4, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Análise de risco atual
        analysis_frame = ttk.LabelFrame(risk_container, text="🔍 Análise de Risco Atual", padding="20")
        analysis_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        risk_metrics = [
            ("Exposição Total", f"{self.current_risk:.1f}%", "#f59e0b"),
            ("Risco Disponível", f"{self.risk_params.max_portfolio_risk - self.current_risk:.1f}%", "#10b981"),
            ("Trades Ativos", str(len([d for d in self.decisions if d.status == Status.PENDING])), "#3b82f6"),
            ("Nível de Proteção", "ALTO", "#10b981")
        ]
        
        for i, (label, value, color) in enumerate(risk_metrics):
            metric_frame = ttk.Frame(analysis_frame)
            metric_frame.grid(row=i//2, column=i%2, padx=20, pady=10, sticky=tk.W)
            
            ttk.Label(metric_frame, text=label, style='Muted.TLabel', 
                     font=("Arial", 9)).grid(row=0, column=0, sticky=tk.W)
            
            value_label = tk.Label(metric_frame, text=value, fg=color, 
                                  font=("Arial", 14, "bold"), bg='#f8fafc')
            value_label.grid(row=1, column=0, sticky=tk.W)
        
        risk_container.columnconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)


def main() -> None:
    """Função principal para executar a aplicação"""
    root = tk.Tk()
    app = AutonomousDecisionEngineApp(root)
    
    # Tornar a janela responsiva
    root.minsize(1200, 800)
    root.mainloop()


if __name__ == "__main__":
    main()nsize(1300, 900)
    
    # Centralizar janela
    root.eval('tk::PlaceWindow . center')
    
    # Iniciar loop principal
    root.mainloop()


if __name__ == "__main__":
    main()
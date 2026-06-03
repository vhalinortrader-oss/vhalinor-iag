import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
import threading
import time as time_module
import random
from enum import Enum
import asyncio

# Enums para tipos de dados
class SystemStatus(Enum):
    STOPPED = "STOPPED"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    ERROR = "ERROR"

class RiskMode(Enum):
    CONSERVATIVE = "CONSERVATIVE"
    MODERATE = "MODERATE"
    AGGRESSIVE = "AGGRESSIVE"

class OrderType(Enum):
    BUY = "BUY"
    SELL = "SELL"

# Estruturas de dados equivalentes às interfaces TypeScript
@dataclass
class TradingHours:
    start: str
    end: str

@dataclass
class AutonomousConfig:
    enabled: bool
    max_concurrent_trades: int
    max_risk_per_trade: float
    max_daily_risk: float
    min_confidence_level: float
    auto_stop_loss: bool
    auto_take_profit: bool
    risk_management_mode: RiskMode
    trading_hours: TradingHours
    allowed_symbols: List[str]

@dataclass
class TradingSession:
    id: str
    start_time: datetime
    total_trades: int
    successful_trades: int
    profit: float
    max_drawdown: float
    active_trades: int

@dataclass
class Position:
    position_id: str
    symbol: str
    order_type: str  # Renomeado de 'type' para evitar conflito
    volume: float
    open_price: float
    profit: float

@dataclass
class Account:
    balance: float
    equity: float
    margin: float

@dataclass
class MarketPrice:
    symbol: str
    bid: float
    ask: float

@dataclass
class AIDecision:
    action: str
    confidence: float
    symbol: str
    reasoning: str

@dataclass
class OrderParams:
    symbol: str
    type: OrderType
    volume: float
    price: float
    stop_loss: float
    take_profit: float
    comment: str

# Mock classes para simular hooks do React
class MockWillTrader:
    """Mock da classe useWillTrader"""
    def __init__(self):
        self.is_connected = True
        self.account = Account(balance=10000.0, equity=10000.0, margin=0.0)
        self.positions: List[Position] = []
    
    async def place_order(self, params: OrderParams) -> bool:
        """Simular execução de ordem"""
        # Simular sucesso/falha
        success = random.random() > 0.1  # 90% de sucesso
        
        if success:
            # Adicionar posição simulada
            new_position = Position(
                position_id=f"pos_{int(time_module.time())}",
                symbol=params.symbol,
                order_type=params.type.value,
                volume=params.volume,
                open_price=params.price,
                profit=0.0
            )
            self.positions.append(new_position)
        
        return success
    
    async def close_position(self, position_id: str) -> bool:
        """Fechar posição"""
        self.positions = [p for p in self.positions if p.position_id != position_id]
        return True
    
    async def get_market_prices(self, symbols: List[str]) -> List[MarketPrice]:
        """Obter preços de mercado simulados"""
        prices = []
        for symbol in symbols:
            base_price = 1.2000 if 'USD' in symbol else 50000.0 if 'BTC' in symbol else 100.0
            bid = base_price + (random.random() - 0.5) * base_price * 0.01
            ask = bid + base_price * 0.0001
            prices.append(MarketPrice(symbol=symbol, bid=bid, ask=ask))
        return prices

class MockTradingContext:
    """Mock da classe useTradingContext"""
    def __init__(self):
        self.current_decision: Optional[AIDecision] = None
        self.is_market_open = True
        self.settings = {}
    
    def generate_ai_decision(self, symbol: str):
        """Gerar decisão de IA simulada"""
        actions = ['BUY', 'SELL', 'HOLD']
        confidence = 60 + random.random() * 40
        
        self.current_decision = AIDecision(
            action=random.choice(actions),
            confidence=confidence,
            symbol=symbol,
            reasoning=f"Análise técnica para {symbol} indica {random.choice(['alta', 'baixa'])} probabilidade"
        )

class AutonomousTradingControllerApp:
    """Aplicação principal que replica a funcionalidade do componente React AutonomousTradingController"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("🤖 Trading Autônomo Inteligente")
        self.root.geometry("1600x1000")
        self.root.configure(bg='#f8fafc')
        
        # Mocks dos hooks (equivalente aos useHooks do React)
        self.will_trader = MockWillTrader()
        self.trading_context = MockTradingContext()
        
        # Estado da aplicação (equivalente aos useState hooks)
        self.config = AutonomousConfig(
            enabled=False,
            max_concurrent_trades=3,
            max_risk_per_trade=2.0,
            max_daily_risk=10.0,
            min_confidence_level=75.0,
            auto_stop_loss=True,
            auto_take_profit=True,
            risk_management_mode=RiskMode.MODERATE,
            trading_hours=TradingHours(start='09:00', end='17:00'),
            allowed_symbols=['EURUSD', 'GBPUSD', 'USDJPY', 'BTCUSD', 'ETHUSD']
        )
        
        self.session = TradingSession(
            id=f"session_{int(time_module.time())}",
            start_time=datetime.now(),
            total_trades=0,
            successful_trades=0,
            profit=0.0,
            max_drawdown=0.0,
            active_trades=0
        )
        
        self.system_status = SystemStatus.STOPPED
        self.last_action = "Sistema inicializado"
        self.next_analysis_time: Optional[datetime] = None
        
        # Containers para widgets que precisam ser atualizados
        self.status_badge = None
        self.control_button = None
        self.metrics_labels = {}
        self.last_action_label = None
        self.next_analysis_label = None
        self.connection_badge = None
        self.notebook = None  # Inicializado aqui
        
        # Thread de análise
        self.analysis_thread = None
        self.stop_analysis = False
        
        # Configurar estilos
        self.setup_styles()
        
        # Configurar interface
        self.setup_ui()
        
        # Simular algumas posições iniciais
        self.simulate_initial_positions()
    
    def setup_styles(self) -> None:
        """Configurar estilos customizados para a aplicação"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar cores personalizadas
        style.configure('Primary.TButton', 
                       background='#3b82f6', 
                       foreground='white',
                       focuscolor='none')
        
        style.configure('Danger.TButton', 
                       background='#ef4444', 
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
    
    def show_toast(self, message: str, msg_type: str = "info") -> None:
        """Mostrar notificação toast (equivalente ao toast)"""
        if msg_type == "error":
            messagebox.showerror("Sistema Autônomo", message)
        elif msg_type == "success":
            messagebox.showinfo("Sucesso", message)
        else:
            messagebox.showinfo("Sistema Autônomo", message)
    
    # Funções utilitárias (equivalentes às funções do React)
    def get_status_color(self, status: SystemStatus) -> str:
        """Obter cor para status (equivalente a getStatusColor)"""
        color_map = {
            SystemStatus.RUNNING: "#10b981",
            SystemStatus.PAUSED: "#6b7280",
            SystemStatus.STOPPED: "#6b7280",
            SystemStatus.ERROR: "#ef4444"
        }
        return color_map.get(status, "#6b7280")
    
    def simulate_initial_positions(self) -> None:
        """Simular posições iniciais para demonstração"""
        initial_positions = [
            Position(
                position_id="pos_1",
                symbol="EURUSD",
                order_type="BUY",
                volume=0.1,
                open_price=1.2000,
                profit=15.50
            ),
            Position(
                position_id="pos_2",
                symbol="BTCUSD",
                order_type="SELL",
                volume=0.01,
                open_price=45000.0,
                profit=-8.20
            )
        ]
        self.will_trader.positions = initial_positions
        self.session.active_trades = len(initial_positions)
    
    # Função principal de análise autônoma (equivalente a executeAutonomousAnalysis)
    async def execute_autonomous_analysis(self) -> None:
        """Executar análise e trading autônomo (equivalente a executeAutonomousAnalysis)"""
        if not self.config.enabled or not self.will_trader.is_connected or self.system_status != SystemStatus.RUNNING:
            return
        
        try:
            self.last_action = 'Analisando mercado...'
            self.root.after(0, self.update_displays)
            
            # 1. Verificar horário de trading
            current_time = datetime.now().strftime("%H:%M")
            
            if current_time < self.config.trading_hours.start or current_time > self.config.trading_hours.end:
                self.last_action = f"Fora do horário de trading ({self.config.trading_hours.start}-{self.config.trading_hours.end})"
                self.root.after(0, self.update_displays)
                return
            
            # 2. Verificar limites de risco
            if len(self.will_trader.positions) >= self.config.max_concurrent_trades:
                self.last_action = f"Limite de trades simultâneos atingido ({self.config.max_concurrent_trades})"
                self.root.after(0, self.update_displays)
                return
            
            # 3. Obter preços atualizados
            _ = await self.will_trader.get_market_prices(self.config.allowed_symbols)
            self.last_action = 'Preços de mercado atualizados'
            self.root.after(0, self.update_displays)
            
            # 4. Análise por símbolo
            for symbol in self.config.allowed_symbols:
                if len(self.will_trader.positions) >= self.config.max_concurrent_trades:
                    break
                
                # Verificar se já existe posição
                existing_position = next((p for p in self.will_trader.positions if p.symbol == symbol), None)
                if existing_position:
                    continue
                
                # Gerar decisão de IA
                self.trading_context.generate_ai_decision(symbol)
                
                # Aguardar processamento
                await asyncio.sleep(1)
                
                decision = self.trading_context.current_decision
                if decision and decision.confidence >= self.config.min_confidence_level:
                    self.last_action = f"IA recomenda {decision.action} para {symbol} ({decision.confidence:.1f}%)"
                    self.root.after(0, self.update_displays)
                    
                    # Executar ordem automaticamente
                    if decision.action in ['BUY', 'SELL']:
                        await self.execute_automatic_order(symbol, decision)
            
            # 5. Monitorar posições existentes
            await self.monitor_existing_positions()
            
        except Exception as error:
            print(f'Erro na análise autônoma: {error}')
            self.system_status = SystemStatus.ERROR
            self.last_action = f"Erro: {error}"
            self.root.after(0, self.update_displays)
            self.show_toast("Falha na análise. Sistema pausado por segurança.", "error")
    
    async def execute_automatic_order(self, symbol: str, decision: AIDecision) -> None:
        """Executar ordem automaticamente (equivalente a executeAutomaticOrder)"""
        try:
            # Calcular volume baseado no risco
            risk_amount = self.will_trader.account.balance * (self.config.max_risk_per_trade / 100)
            current_price = await self.get_current_price(symbol)
            
            if not current_price:
                return
            
            # Calcular stop loss e take profit
            stop_loss_distance = current_price * 0.02  # 2% padrão
            take_profit_distance = current_price * 0.04  # 4% padrão
            
            order_params = OrderParams(
                symbol=symbol,
                type=OrderType.BUY if decision.action == 'BUY' else OrderType.SELL,
                volume=max(0.01, risk_amount / current_price),
                price=current_price,
                stop_loss=(current_price - stop_loss_distance) if decision.action == 'BUY' 
                         else (current_price + stop_loss_distance),
                take_profit=(current_price + take_profit_distance) if decision.action == 'BUY'
                           else (current_price - take_profit_distance),
                comment=f"AUTO_TRADE_AI_{decision.confidence:.0f}%"
            )
            
            result = await self.will_trader.place_order(order_params)
            
            if result:
                self.session.total_trades += 1
                self.session.active_trades += 1
                
                self.last_action = f"✅ ORDEM EXECUTADA: {decision.action} {symbol} - Vol: {order_params.volume:.3f}"
                self.show_toast(f"{decision.action} {symbol} executada automaticamente", "success")
            else:
                self.last_action = f"❌ FALHA NA ORDEM: {symbol}"
            
            self.root.after(0, self.update_displays)
            
        except Exception as error:
            print(f'Erro ao executar ordem automática: {error}')
            self.last_action = f"Erro ao executar ordem: {error}"
            self.root.after(0, self.update_displays)
    
    async def monitor_existing_positions(self) -> None:
        """Monitorar posições existentes (equivalente a monitorExistingPositions)"""
        for position in self.will_trader.positions[:]:  # Cópia da lista para modificação segura
            try:
                # Calcular percentual de lucro
                profit_percent = (position.profit / (position.volume * position.open_price)) * 100
                
                # Take profit automático
                if self.config.auto_take_profit and profit_percent >= 5:
                    await self.will_trader.close_position(position.position_id)
                    self.last_action = f"✅ TAKE PROFIT AUTOMÁTICO: {position.symbol} (+{profit_percent:.1f}%)"
                    
                    self.session.successful_trades += 1
                    self.session.profit += position.profit
                    self.session.active_trades -= 1
                    
                    self.root.after(0, self.update_displays)
                
                # Stop loss automático
                elif self.config.auto_stop_loss and profit_percent <= -3:
                    await self.will_trader.close_position(position.position_id)
                    self.last_action = f"🛡️ STOP LOSS AUTOMÁTICO: {position.symbol} ({profit_percent:.1f}%)"
                    
                    self.session.profit += position.profit
                    self.session.active_trades -= 1
                    
                    self.root.after(0, self.update_displays)
                    
            except Exception as error:
                print(f'Erro ao monitorar posição: {error}')
    
    async def get_current_price(self, symbol: str) -> Optional[float]:
        """Obter preço atual (equivalente a getCurrentPrice)"""
        try:
            prices = await self.will_trader.get_market_prices([symbol])
            return prices[0].bid if prices else None
        except Exception as error:
            print(f'Erro ao obter preço: {error}')
            return None
    
    # Controles do sistema (equivalentes às funções de controle do React)
    def start_system(self) -> None:
        """Iniciar sistema autônomo (equivalente a startSystem)"""
        if not self.will_trader.is_connected:
            self.show_toast("Conecte-se ao WillTrader primeiro", "error")
            return
        
        self.system_status = SystemStatus.RUNNING
        self.config.enabled = True
        self.session.start_time = datetime.now()
        self.last_action = 'Sistema autônomo INICIADO'
        
        self.update_displays()
        self.start_analysis_loop()
        
        self.show_toast("IA assumiu controle completo do trading", "success")
    
    def stop_system(self) -> None:
        """Parar sistema autônomo (equivalente a stopSystem)"""
        self.system_status = SystemStatus.STOPPED
        self.config.enabled = False
        self.last_action = 'Sistema autônomo PARADO'
        self.stop_analysis = True
        
        self.update_displays()
        
        self.show_toast("Trading autônomo interrompido")
    
    def emergency_stop(self) -> None:
        """Parada de emergência (equivalente a emergencyStop)"""
        self.system_status = SystemStatus.STOPPED
        self.config.enabled = False
        self.last_action = '🚨 PARADA DE EMERGÊNCIA ATIVADA'
        self.stop_analysis = True
        
        # Fechar todas as posições
        positions_to_close = self.will_trader.positions[:]
        for pos in positions_to_close:
            pos_id = pos.position_id
            threading.Thread(target=lambda pid=pos_id: asyncio.run(
                self.will_trader.close_position(pid)
            ), daemon=True).start()
        
        self.update_displays()
        
        self.show_toast("PARADA DE EMERGÊNCIA - Todas as posições foram fechadas", "error")
    
    # Loop principal do sistema (equivalente ao useEffect)
    def start_analysis_loop(self) -> None:
        """Iniciar loop de análise (equivalente ao useEffect com interval)"""
        def analysis_worker():
            self.stop_analysis = False
            while not self.stop_analysis and self.config.enabled and self.system_status == SystemStatus.RUNNING:
                # Executar análise
                asyncio.run(self.execute_autonomous_analysis())
                
                # Definir próxima análise
                self.next_analysis_time = datetime.now().replace(microsecond=0)
                self.next_analysis_time = self.next_analysis_time.replace(
                    second=self.next_analysis_time.second + 30
                )
                self.root.after(0, self.update_displays)
                
                # Aguardar 30 segundos
                for _ in range(30):
                    if self.stop_analysis:
                        break
                    time_module.sleep(1)
        
        self.analysis_thread = threading.Thread(target=analysis_worker, daemon=True)
        self.analysis_thread.start()
    
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
        
        # Painel de emergência
        self.setup_emergency_panel(container)
        
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
                               text="🤖 Trading Autônomo Inteligente", 
                               font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        # Controles
        control_frame = ttk.Frame(header_frame)
        control_frame.grid(row=0, column=1, sticky=tk.E)
        
        # Badge de status
        status_color = self.get_status_color(self.system_status)
        self.status_badge = tk.Label(control_frame, 
                                    text=f"📊 {self.system_status.value}",
                                    bg=status_color,
                                    fg="white",
                                    font=("Arial", 10, "bold"),
                                    padx=10, pady=5)
        self.status_badge.grid(row=0, column=0, padx=(0, 10))
        
        # Botão de controle
        if self.system_status == SystemStatus.RUNNING:
            button_text = "⏸️ Pausar"
            button_command = self.stop_system
            button_style = 'Danger.TButton'
        else:
            button_text = "▶️ Iniciar"
            button_command = self.start_system
            button_style = 'Primary.TButton'
        
        self.control_button = ttk.Button(control_frame, 
                                        text=button_text,
                                        command=button_command,
                                        style=button_style)
        self.control_button.grid(row=0, column=1)
        
        header_frame.columnconfigure(0, weight=1)
    
    def setup_emergency_panel(self, parent: ttk.Frame) -> None:
        """Configurar painel de emergência"""
        emergency_frame = tk.Frame(parent, bg="#fef2f2", relief='solid', 
                                  borderwidth=1, highlightbackground="#fecaca", 
                                  highlightthickness=1)
        emergency_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Conteúdo do painel
        content_frame = tk.Frame(emergency_frame, bg="#fef2f2")
        content_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=15, pady=10)
        
        # Ícone e texto
        left_frame = tk.Frame(content_frame, bg="#fef2f2")
        left_frame.grid(row=0, column=0, sticky=tk.W)
        
        ttk.Label(left_frame, text="⚠️", font=("Arial", 14)).grid(row=0, column=0, padx=(0, 10))
        
        text_label = tk.Label(left_frame, 
                             text="Sistema Autônomo Ativo: IA operando independentemente",
                             bg="#fef2f2", fg="#991b1b", font=("Arial", 10, "bold"))
        text_label.grid(row=0, column=1)
        
        # Botão de emergência
        emergency_btn = tk.Button(content_frame, 
                                 text="🚨 PARADA DE EMERGÊNCIA",
                                 bg="#ef4444", fg="white",
                                 font=("Arial", 10, "bold"),
                                 padx=15, pady=5,
                                 cursor="hand2",
                                 command=self.emergency_stop)
        emergency_btn.grid(row=0, column=1, sticky=tk.E)
        
        content_frame.columnconfigure(0, weight=1)
        emergency_frame.columnconfigure(0, weight=1)
    
    def setup_notebook(self, parent: ttk.Frame) -> None:
        """Configurar notebook com abas (equivalente ao Tabs do React)"""
        self.notebook = ttk.Notebook(parent)
        self.notebook.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Aba Status
        status_frame = ttk.Frame(self.notebook)
        self.notebook.add(status_frame, text="📊 Status")
        self.setup_status_tab(status_frame)
        
        # Aba Sessão
        session_frame = ttk.Frame(self.notebook)
        self.notebook.add(session_frame, text="📈 Sessão")
        self.setup_session_tab(session_frame)
        
        # Aba Configurações
        config_frame = ttk.Frame(self.notebook)
        self.notebook.add(config_frame, text="⚙️ Configurações")
        self.setup_config_tab(config_frame)
        
        # Aba Monitoramento
        monitoring_frame = ttk.Frame(self.notebook)
        self.notebook.add(monitoring_frame, text="👁️ Monitoramento")
        self.setup_monitoring_tab(monitoring_frame)
    
    def setup_status_tab(self, parent: ttk.Frame) -> None:
        """Configurar aba de status (equivalente ao TabsContent status)"""
        status_container = ttk.Frame(parent, padding="20")
        status_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Grid de métricas em tempo real
        metrics_grid = ttk.Frame(status_container)
        metrics_grid.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Métricas principais
        metrics_data = [
            ("💰", "Lucro Sessão", f"{'+' if self.session.profit > 0 else ''}{self.session.profit:.2f}", "profit"),
            ("🎯", "Taxa Sucesso", f"{((self.session.successful_trades / max(self.session.total_trades, 1)) * 100):.0f}%", "success_rate"),
            ("📊", "Trades Ativos", str(self.session.active_trades), "active_trades"),
            ("⏱️", "Tempo Ativo", f"{((datetime.now() - self.session.start_time).total_seconds() / 3600):.1f}h", "active_time")
        ]
        
        for i, (icon, label, value, key) in enumerate(metrics_data):
            metric_card = ttk.LabelFrame(metrics_grid, text=f"{icon} {label}", padding="15")
            metric_card.grid(row=0, column=i, padx=5, sticky=(tk.W, tk.E))
            
            self.metrics_labels[key] = ttk.Label(metric_card, text=value, 
                                               font=("Arial", 16, "bold"), style='Info.TLabel')
            self.metrics_labels[key].grid(row=0, column=0)
        
        for i in range(4):
            metrics_grid.columnconfigure(i, weight=1)
        
        # Status em tempo real
        status_card = ttk.LabelFrame(status_container, text="Status em Tempo Real", padding="20")
        status_card.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Última ação
        last_action_frame = ttk.Frame(status_card)
        last_action_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(last_action_frame, text="Última Ação:", 
                 style='Muted.TLabel', font=("Arial", 9)).grid(row=0, column=0, sticky=tk.W)
        self.last_action_label = ttk.Label(last_action_frame, text=self.last_action, 
                                          font=("Arial", 9, "bold"))
        self.last_action_label.grid(row=0, column=1, sticky=tk.E)
        
        last_action_frame.columnconfigure(0, weight=1)
        
        # Próxima análise
        if self.next_analysis_time:
            next_analysis_frame = ttk.Frame(status_card)
            next_analysis_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
            
            ttk.Label(next_analysis_frame, text="Próxima Análise:", 
                     style='Muted.TLabel', font=("Arial", 9)).grid(row=0, column=0, sticky=tk.W)
            self.next_analysis_label = ttk.Label(next_analysis_frame, 
                                               text=self.next_analysis_time.strftime("%H:%M:%S") if self.next_analysis_time else "N/A", 
                                               font=("Arial", 9, "bold"))
            self.next_analysis_label.grid(row=0, column=1, sticky=tk.E)
            
            next_analysis_frame.columnconfigure(0, weight=1)
        
        # Conexão
        connection_frame = ttk.Frame(status_card)
        connection_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        ttk.Label(connection_frame, text="Conexão WillTrader:", 
                 style='Muted.TLabel', font=("Arial", 9)).grid(row=0, column=0, sticky=tk.W)
        
        conn_color = "#10b981" if self.will_trader.is_connected else "#ef4444"
        conn_text = "CONECTADO" if self.will_trader.is_connected else "DESCONECTADO"
        self.connection_badge = tk.Label(connection_frame, 
                                        text=conn_text,
                                        bg=conn_color,
                                        fg="white",
                                        font=("Arial", 8, "bold"),
                                        padx=8, pady=2)
        self.connection_badge.grid(row=0, column=1, sticky=tk.E)
        
        connection_frame.columnconfigure(0, weight=1)
        status_card.columnconfigure(0, weight=1)
        status_container.columnconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
    
    def setup_session_tab(self, parent: ttk.Frame) -> None:
        """Configurar aba de sessão"""
        session_container = ttk.Frame(parent, padding="20")
        session_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Informações da sessão
        session_card = ttk.LabelFrame(session_container, text="📊 Sessão Atual", padding="20")
        session_card.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # ID da sessão
        id_frame = ttk.Frame(session_card)
        id_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        ttk.Label(id_frame, text="ID da Sessão:", style='Muted.TLabel').grid(row=0, column=0, sticky=tk.W)
        ttk.Label(id_frame, text=self.session.id, font=("Courier", 10, "bold")).grid(row=0, column=1, sticky=tk.E)
        id_frame.columnconfigure(0, weight=1)
        
        # Hora de início
        start_frame = ttk.Frame(session_card)
        start_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        ttk.Label(start_frame, text="Início:", style='Muted.TLabel').grid(row=0, column=0, sticky=tk.W)
        ttk.Label(start_frame, text=self.session.start_time.strftime("%d/%m/%Y %H:%M:%S"), 
                 font=("Arial", 10, "bold")).grid(row=0, column=1, sticky=tk.E)
        start_frame.columnconfigure(0, weight=1)
        
        # Estatísticas da sessão
        stats_card = ttk.LabelFrame(session_container, text="📈 Estatísticas", padding="20")
        stats_card.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        stats_data = [
            ("Total de Trades", str(self.session.total_trades)),
            ("Trades Bem-Sucedidos", str(self.session.successful_trades)),
            ("Lucro da Sessão", f"R$ {self.session.profit:.2f}"),
            ("Max Drawdown", f"{self.session.max_drawdown:.2f}%"),
            ("Trades Ativos", str(self.session.active_trades)),
            ("Taxa de Sucesso", f"{(self.session.successful_trades / max(self.session.total_trades, 1) * 100):.1f}%")
        ]
        
        for i, (label, value) in enumerate(stats_data):
            stat_frame = ttk.Frame(stats_card)
            stat_frame.grid(row=i//2, column=i%2, padx=20, pady=10, sticky=tk.W)
            
            ttk.Label(stat_frame, text=label, style='Muted.TLabel', 
                     font=("Arial", 9)).grid(row=0, column=0, sticky=tk.W)
            ttk.Label(stat_frame, text=value, 
                     font=("Arial", 12, "bold")).grid(row=1, column=0, sticky=tk.W)
        
        session_container.columnconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
    
    def setup_config_tab(self, parent: ttk.Frame) -> None:
        """Configurar aba de configurações"""
        config_container = ttk.Frame(parent, padding="20")
        config_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurações de Trading
        trading_card = ttk.LabelFrame(config_container, text="⚙️ Configurações de Trading", padding="20")
        trading_card.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Max Concurrent Trades
        ttk.Label(trading_card, text="Trades Simultâneos Máximos:", 
                 font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
        concurrent_scale = ttk.Scale(trading_card, from_=1, to=10, orient=tk.HORIZONTAL, length=300)
        concurrent_scale.set(self.config.max_concurrent_trades)
        concurrent_scale.grid(row=0, column=1, padx=10)
        ttk.Label(trading_card, text=str(self.config.max_concurrent_trades), 
                 font=("Arial", 10, "bold")).grid(row=0, column=2)
        
        # Max Risk per Trade
        ttk.Label(trading_card, text="Risco Máximo por Trade:", 
                 font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, pady=5)
        risk_scale = ttk.Scale(trading_card, from_=0.5, to=5.0, orient=tk.HORIZONTAL, length=300)
        risk_scale.set(self.config.max_risk_per_trade)
        risk_scale.grid(row=1, column=1, padx=10)
        ttk.Label(trading_card, text=f"{self.config.max_risk_per_trade:.1f}%", 
                 font=("Arial", 10, "bold")).grid(row=1, column=2)
        
        # Min Confidence Level
        ttk.Label(trading_card, text="Confiança Mínima:", 
                 font=("Arial", 10)).grid(row=2, column=0, sticky=tk.W, pady=5)
        confidence_scale = ttk.Scale(trading_card, from_=50, to=100, orient=tk.HORIZONTAL, length=300)
        confidence_scale.set(self.config.min_confidence_level)
        confidence_scale.grid(row=2, column=1, padx=10)
        ttk.Label(trading_card, text=f"{self.config.min_confidence_level:.0f}%", 
                 font=("Arial", 10, "bold")).grid(row=2, column=2)
        
        # Checkboxes
        ttk.Checkbutton(trading_card, text="Stop Loss Automático", 
                       variable=tk.BooleanVar(value=self.config.auto_stop_loss)).grid(
                           row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        ttk.Checkbutton(trading_card, text="Take Profit Automático", 
                       variable=tk.BooleanVar(value=self.config.auto_take_profit)).grid(
                           row=4, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Horário de Trading
        hours_card = ttk.LabelFrame(config_container, text="🕐 Horário de Trading", padding="20")
        hours_card.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        ttk.Label(hours_card, text="Início:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Label(hours_card, text=self.config.trading_hours.start, 
                 font=("Arial", 10, "bold")).grid(row=0, column=1, sticky=tk.W, padx=10)
        
        ttk.Label(hours_card, text="Fim:", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Label(hours_card, text=self.config.trading_hours.end, 
                 font=("Arial", 10, "bold")).grid(row=1, column=1, sticky=tk.W, padx=10)
        
        # Símbolos Permitidos
        symbols_card = ttk.LabelFrame(config_container, text="📊 Símbolos Permitidos", padding="20")
        symbols_card.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        symbols_text = ", ".join(self.config.allowed_symbols)
        ttk.Label(symbols_card, text=symbols_text, 
                 font=("Arial", 10), wraplength=600).grid(row=0, column=0, sticky=tk.W)
        
        config_container.columnconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
    
    def setup_monitoring_tab(self, parent: ttk.Frame) -> None:
        """Configurar aba de monitoramento (equivalente ao TabsContent monitoring)"""
        monitoring_container = ttk.Frame(parent, padding="20")
        monitoring_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        title_label = ttk.Label(monitoring_container, 
                               text="👁️ Monitoramento em Tempo Real", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 20))
        
        # Lista de posições
        for i, position in enumerate(self.will_trader.positions):
            position_card = ttk.Frame(monitoring_container, style='Card.TFrame', padding="15")
            position_card.grid(row=i+1, column=0, sticky=(tk.W, tk.E), pady=5)
            
            # Informações da posição
            left_frame = ttk.Frame(position_card)
            left_frame.grid(row=0, column=0, sticky=tk.W)
            
            # Symbol badge
            symbol_color = "#10b981" if position.profit > 0 else "#ef4444"
            symbol_badge = tk.Label(left_frame, 
                                   text=position.symbol,
                                   bg=symbol_color,
                                   fg="white",
                                   font=("Arial", 8, "bold"),
                                   padx=8, pady=2)
            symbol_badge.grid(row=0, column=0, padx=(0, 10))
            
            # Tipo e volume
            type_label = ttk.Label(left_frame, 
                                  text=f"{position.order_type} {position.volume}",
                                  font=("Arial", 10))
            type_label.grid(row=0, column=1)
            
            # Controles
            right_frame = ttk.Frame(position_card)
            right_frame.grid(row=0, column=1, sticky=tk.E)
            
            # Profit
            profit_color = "Info.TLabel" if position.profit > 0 else "Error.TLabel"
            profit_text = f"{'+' if position.profit > 0 else ''}{position.profit:.2f}"
            profit_label = ttk.Label(right_frame, text=profit_text, 
                                   font=("Arial", 10, "bold"), style=profit_color)
            profit_label.grid(row=0, column=0, padx=(0, 10))
            
            # Botão fechar
            close_btn = ttk.Button(right_frame, 
                                  text="Fechar",
                                  command=lambda pid=position.position_id: self.close_position_action(pid))
            close_btn.grid(row=0, column=1)
            
            position_card.columnconfigure(0, weight=1)
        
        # Mensagem quando não há posições
        if not self.will_trader.positions:
            no_positions_label = ttk.Label(monitoring_container, 
                                          text="Nenhuma posição ativa no momento",
                                          style='Muted.TLabel',
                                          font=("Arial", 12))
            no_positions_label.grid(row=1, column=0, pady=50)
        
        monitoring_container.columnconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
    
    def close_position_action(self, position_id: str) -> None:
        """Ação para fechar posição"""
        threading.Thread(target=lambda: asyncio.run(
            self.will_trader.close_position(position_id)
        ), daemon=True).start()
        
        # Atualizar displays após fechar
        self.root.after(1000, self.update_displays)
    
    def update_displays(self) -> None:
        """Atualizar todos os displays da interface"""
        # Atualizar badge de status
        if self.status_badge:
            status_color = self.get_status_color(self.system_status)
            self.status_badge.config(text=f"📊 {self.system_status.value}", bg=status_color)
        
        # Atualizar botão de controle
        if self.control_button:
            if self.system_status == SystemStatus.RUNNING:
                self.control_button.config(text="⏸️ Pausar")
            else:
                self.control_button.config(text="▶️ Iniciar")
        
        # Atualizar métricas
        if 'profit' in self.metrics_labels:
            profit_text = f"{'+' if self.session.profit > 0 else ''}{self.session.profit:.2f}"
            self.metrics_labels['profit'].config(text=profit_text)
        
        if 'success_rate' in self.metrics_labels:
            success_rate = (self.session.successful_trades / max(self.session.total_trades, 1)) * 100
            self.metrics_labels['success_rate'].config(text=f"{success_rate:.0f}%")
        
        if 'active_trades' in self.metrics_labels:
            self.metrics_labels['active_trades'].config(text=str(len(self.will_trader.positions)))
        
        if 'active_time' in self.metrics_labels:
            active_hours = (datetime.now() - self.session.start_time).total_seconds() / 3600
            self.metrics_labels['active_time'].config(text=f"{active_hours:.1f}h")
        
        # Atualizar labels de status
        if self.last_action_label:
            self.last_action_label.config(text=self.last_action)
        
        if self.next_analysis_label and self.next_analysis_time:
            self.next_analysis_label.config(text=self.next_analysis_time.strftime("%H:%M:%S"))
        
        # Atualizar badge de conexão
        if self.connection_badge:
            conn_color = "#10b981" if self.will_trader.is_connected else "#ef4444"
            conn_text = "CONECTADO" if self.will_trader.is_connected else "DESCONECTADO"
            self.connection_badge.config(text=conn_text, bg=conn_color)


def main() -> None:
    """Função principal para executar a aplicação"""
    root = tk.Tk()
    _ = AutonomousTradingControllerApp(root)  # App é mantido vivo pelo root
    
    # Tornar a janela responsiva
    root.minsize(1400, 900)
    
    # Centralizar janela
    root.eval('tk::PlaceWindow . center')
    
    # Iniciar loop principal
    root.mainloop()


if __name__ == "__main__":
    main()
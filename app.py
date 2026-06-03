"""
Interface Web do VHALINOR TRADER
Executar com: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import random
import time

# Configuração da página
st.set_page_config(
    page_title="VHALINOR TRADER - Sistema de Trading com IA",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS personalizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
    }
    .trade-signal-buy {
        background: #00ff00;
        color: #000;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
    }
    .trade-signal-sell {
        background: #ff0000;
        color: #fff;
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.running = False
    st.session_state.trades = []
    st.session_state.balance = 10000
    st.session_state.portfolio = {}
    st.session_state.price_history = []
    st.session_state.last_price = 46000

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/300x100/1e3c72/ffffff?text=VHALINOR+TRADER", use_column_width=True)
    st.title("🤖 VHALINOR TRADER")
    
    # Status
    status_color = "🟢" if st.session_state.running else "🔴"
    st.markdown(f"### {status_color} Status: {'ATIVO' if st.session_state.running else 'INATIVO'}")
    
    # Controles
    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ INICIAR", use_container_width=True):
            st.session_state.running = True
            st.rerun()
    with col2:
        if st.button("⏹️ PARAR", use_container_width=True):
            st.session_state.running = False
            st.rerun()
    
    st.divider()
    
    # Configurações
    st.subheader("⚙️ Configurações")
    exchange = st.selectbox("Exchange", ["Binance", "Coinbase", "Kraken"])
    trading_pair = st.selectbox("Par", ["BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT"])
    risk_level = st.select_slider("Nível de Risco", ["Baixo", "Médio", "Alto"], value="Médio")
    trade_amount = st.number_input("Valor por Trade (USDT)", min_value=10, max_value=10000, value=100)
    
    if st.button("💾 Salvar Configurações", use_container_width=True):
        st.success("Configurações salvas!")
        st.session_state.trade_amount = trade_amount
    
    st.divider()
    
    # Portfolio
    st.subheader("💰 Portfolio")
    st.metric("Saldo Total", f"${st.session_state.balance:,.2f}")
    st.metric("Lucro/Perda", "$1,234.56", "+12.34%")
    
    # Conectar Blockchain
    if st.button("🔗 Conectar Blockchain", use_container_width=True):
        st.success("Conectado à Ethereum Blockchain")
        st.info("Saldo: 0.5 ETH")

# Main content
st.markdown('<div class="main-header">', unsafe_allow_html=True)
st.title("📈 VHALINOR TRADER - Dashboard de Trading com IA")
st.markdown("Sistema avançado de trading automatizado com inteligência artificial")
st.markdown('</div>', unsafe_allow_html=True)

# Métricas principais
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("💰 Lucro Total", "$1,234.56", "+12.3%", delta_color="normal")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("🎯 Taxa de Acerto", "76.5%", "+5.2%", delta_color="normal")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("📊 Trades Hoje", "24", "+8", delta_color="normal")
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric("🤖 Modelos IA", "4", "Ativos", delta_color="off")
    st.markdown('</div>', unsafe_allow_html=True)

# Gráfico em tempo real
st.subheader("📊 Análise de Mercado em Tempo Real")

# Simular dados em tempo real
if st.session_state.running:
    # Atualizar preço
    change = random.uniform(-200, 200)
    st.session_state.last_price += change
    st.session_state.price_history.append({
        'time': datetime.now(),
        'price': st.session_state.last_price
    })
    
    # Manter apenas últimas 100 entradas
    if len(st.session_state.price_history) > 100:
        st.session_state.price_history = st.session_state.price_history[-100:]

# Criar gráfico
fig = make_subplots(
    rows=2, cols=1,
    shared_xaxes=True,
    vertical_spacing=0.03,
    row_heights=[0.7, 0.3]
)

# Dados para o gráfico
if st.session_state.price_history:
    df = pd.DataFrame(st.session_state.price_history)
    
    # Candlestick simulado
    fig.add_trace(
        go.Scatter(
            x=df['time'],
            y=df['price'],
            mode='lines',
            name='Preço BTC/USDT',
            line=dict(color='#00ff00', width=2)
        ),
        row=1, col=1
    )
    
    # Volume simulado
    fig.add_trace(
        go.Bar(
            x=df['time'],
            y=[random.uniform(50, 100) for _ in range(len(df))],
            name='Volume',
            marker_color='lightblue'
        ),
        row=2, col=1
    )

fig.update_layout(
    title='Mercado em Tempo Real',
    xaxis_title='Tempo',
    yaxis_title='Preço (USDT)',
    height=500,
    template='plotly_dark',
    showlegend=True
)

st.plotly_chart(fig, use_container_width=True)

# Análise da IA
st.subheader("🧠 Análise e Predições da IA")

col1, col2 = st.columns(2)

with col1:
    with st.expander("📊 Análise Técnica", expanded=True):
        st.info("""
        **Indicadores Técnicos:**
        - 📈 **Tendência:** Alta (Bullish)
        - 🎯 **RSI (14):** 65.2 (Neutro)
        - 📊 **MACD:** Sinal de Compra
        - 🛡️ **Suporte:** $45,200
        - 🚀 **Resistência:** $48,500
        - 📉 **Volatilidade:** Média (15.2%)
        """)

with col2:
    with st.expander("🧠 Análise Cognitiva IA", expanded=True):
        st.info("""
        **Processamento de Sentimento:**
        - 😊 **Sentimento Mercado:** Positivo (0.76)
        - 🔥 **Momentum:** Forte
        - 💧 **Liquidez:** Alta
        - ⚡ **Recomendação IA:** COMPRAR
        - 🎯 **Confiança:** 87.5%
        - 📊 **Score:** A (Excelente)
        """)

# Predições
st.subheader("🔮 Predições de Preço por Timeframe")

predictions = {
    'Timeframe': ['1 hora', '4 horas', '1 dia', '1 semana'],
    'Preço Previsto': ['$46,234', '$47,890', '$49,123', '$52,456'],
    'Variação': ['+0.5%', '+2.1%', '+4.8%', '+10.2%'],
    'Confiança': ['92%', '87%', '78%', '71%'],
    'Ação': ['COMPRAR', 'COMPRAR', 'COMPRAR FORTE', 'HOLD']
}

pred_df = pd.DataFrame(predictions)
st.dataframe(pred_df, use_container_width=True, hide_index=True)

# Sinais de Trading
st.subheader("🎯 Sinais de Trading em Tempo Real")

if st.session_state.running:
    # Simular sinais
    signals_placeholder = st.empty()
    
    for _ in range(5):
        signal = random.choice(['COMPRAR', 'VENDER', 'HOLD'])
        pair = random.choice(['BTC/USDT', 'ETH/USDT', 'BNB/USDT'])
        price = random.uniform(45000, 47000)
        confidence = random.uniform(70, 95)
        
        color = "#00ff00" if signal == "COMPRAR" else "#ff0000" if signal == "VENDER" else "#ffff00"
        
        signals_placeholder.markdown(f"""
        <div style="background: {color}20; padding: 10px; border-radius: 5px; margin: 5px 0; border-left: 4px solid {color}">
            <strong>{signal}</strong> {pair} @ ${price:,.2f} | Confiança: {confidence:.1f}% | {datetime.now().strftime('%H:%M:%S')}
        </div>
        """, unsafe_allow_html=True)
        time.sleep(1)
else:
    st.info("Sistema inativo. Clique em INICIAR para começar o trading automático.")

# Trades Executados
st.subheader("📝 Histórico de Trades")

if st.session_state.trades:
    trades_df = pd.DataFrame(st.session_state.trades)
    st.dataframe(trades_df, use_container_width=True)
else:
    trades_data = {
        'Data': [datetime.now() - timedelta(hours=x) for x in range(5, 0, -1)],
        'Par': ['BTC/USDT', 'ETH/USDT', 'BTC/USDT', 'SOL/USDT', 'BNB/USDT'],
        'Ação': ['COMPRAR', 'COMPRAR', 'VENDER', 'COMPRAR', 'VENDER'],
        'Preço': ['$46,234', '$3,245', '$46,890', '$98.50', '$312'],
        'Quantidade': ['0.0021', '0.03', '0.0021', '1.0', '0.32'],
        'Total': ['$97.09', '$97.35', '$98.47', '$98.50', '$99.84'],
        'Lucro/Perda': ['+$2.91', '-$2.65', '+$1.53', '-$1.50', '+$0.16']
    }
    st.dataframe(pd.DataFrame(trades_data), use_container_width=True)

# Logs do Sistema
st.subheader("📝 Logs do Sistema em Tempo Real")

log_placeholder = st.empty()

if st.session_state.running:
    logs = [
        f"[{datetime.now().strftime('%H:%M:%S')}] 🤖 Sistema VHALINOR TRADER ativo",
        f"[{datetime.now().strftime('%H:%M:%S')}] 📊 Conectado à {exchange}",
        f"[{datetime.now().strftime('%H:%M:%S')}] 🧠 IA analisando mercado...",
        f"[{datetime.now().strftime('%H:%M:%S')}] 🔮 Predição gerada: COMPRAR com 87% confiança",
        f"[{datetime.now().strftime('%H:%M:%S')}] 💰 Trade executado: {trading_pair}"
    ]
    log_placeholder.code("\n".join(logs), language="log")
else:
    log_placeholder.info("Sistema inativo. Inicie o sistema para ver os logs.")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: gray; padding: 20px;">
    <p>🤖 VHALINOR TRADER v1.0 - Sistema de Trading com Inteligência Artificial</p>
    <p>⚠️ Aviso: Trading envolve riscos. Use com responsabilidade.</p>
</div>
""", unsafe_allow_html=True)

# Auto-refresh se estiver rodando
if st.session_state.running:
    time.sleep(2)
    st.rerun()
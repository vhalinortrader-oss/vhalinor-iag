#!/bin/bash

# VHALINOR TRADER - Script de Inicialização

echo "==================================="
echo "🤖 VHALINOR TRADER"
echo "Sistema de Trading com IA"
echo "==================================="
echo ""

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instale o Python 3.8+"
    exit 1
fi

# Verificar pip
if ! command -v pip &> /dev/null; then
    echo "❌ Pip não encontrado. Instale o pip"
    exit 1
fi

# Criar ambiente virtual
echo "📦 Criando ambiente virtual..."
python3 -m venv venv

# Ativar ambiente virtual
echo "🔧 Ativando ambiente virtual..."
source venv/bin/activate

# Instalar dependências
echo "📚 Instalando dependências..."
pip install --upgrade pip
pip install streamlit pandas numpy plotly
pip install ccxt yfinance websocket-client
pip install spacy transformers torch
pip install backtrader selenium web3
pip install redis pydantic pydantic-settings
pip install python-dotenv loguru

# Baixar modelo spaCy
echo "🧠 Baixando modelo de linguagem..."
python -m spacy download pt_core_news_sm

# Criar diretórios necessários
echo "📁 Criando diretórios..."
mkdir -p logs models data

# Criar arquivo .env
if [ ! -f .env ]; then
    echo "🔐 Criando arquivo .env..."
    cat > .env << EOF
# API Keys
BINANCE_API_KEY=your_binance_api_key
BINANCE_SECRET_KEY=your_binance_secret
INFURA_URL=https://mainnet.infura.io/v3/your_project_id

# Trading Config
DEFAULT_TRADE_AMOUNT=100
MAX_RISK_PERCENT=2.0
STOP_LOSS_PERCENT=1.0
TAKE_PROFIT_PERCENT=3.0

# Database
DATABASE_URL=sqlite:///vhalinor_trader.db
REDIS_URL=redis://localhost:6379

# Logging
LOG_LEVEL=INFO
EOF
    echo "⚠️ Configure suas API keys no arquivo .env"
fi

# Verificar ports
echo "🔍 Verificando portas..."
if lsof -Pi :8501 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️ Porta 8501 já está em uso. Parando processo..."
    kill $(lsof -t -i:8501)
fi

# Iniciar aplicação
echo ""
echo "==================================="
echo "✅ Inicializando VHALINOR TRADER"
echo "==================================="
echo ""
echo "🌐 Interface Web: http://localhost:8501"
echo "📊 Dashboard: http://localhost:8501"
echo ""
echo "Pressione Ctrl+C para parar"
echo ""

# Executar Streamlit
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
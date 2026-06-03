# VHALINOR AI Geral - Documentação Completa

## Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Instalação e Configuração](#instalação-e-configuração)
4. [Estrutura do Projeto](#estrutura-do-projeto)
5. [Módulos Principais](#módulos-principais)
6. [Configuração](#configuração)
7. [Uso e Operação](#uso-e-operação)
8. [Testes](#testes)
9. [Relatórios](#relatórios)
10. [Troubleshooting](#troubleshooting)

---

## Visão Geral

VHALINOR AI Geral é um sistema profissional de Inteligência Artificial implementado com arquitetura escalável e moderna, focado em:

- **Trading Automatizado**: Análise de mercado e execução de trades
- **Aprendizado de Máquina**: Modelos preditivos e análise de dados
- **Processamento em Tempo Real**: WebSocket e streaming de dados
- **Automação Inteligente**: Workflows e tarefas automatizadas
- **Relatórios Avançados**: Geração automática de relatórios e dashboards

---

## Arquitetura do Sistema

### Camadas da Arquitetura

```
VHALINOR AI Geral
    |
    |-- UI Layer (Streamlit/FastAPI)
    |-- Service Layer (WebSocket, Redis)
    |-- Business Layer (AI, Trading, Automation)
    |-- Data Layer (Data Fetcher, Cache)
    |-- Core Layer (Logger, Config, Exceptions)
```

### Componentes Principais

1. **Core**: Funcionalidades centrais (logging, configuração, exceções)
2. **Modules**: Módulos de negócio (data_fetcher, ai_analyzer, predictor)
3. **Services**: Serviços externos (websocket, redis, automation)
4. **Utils**: Utilitários (report_generator, helpers)
5. **Tests**: Suite de testes completo
6. **Config**: Configurações e ambiente

---

## Instalação e Configuração

### Pré-requisitos

- Python 3.14+
- Redis Server (opcional, para cache)
- Microsoft Visual C++ Redistributable

### Instalação

```bash
# Clonar repositório
git clone https://github.com/vhalinor/ai-geral.git
cd ai-geral

# Criar ambiente virtual
python -m venv vhalinor_env
source vhalinor_env/bin/activate  # Linux/Mac
# ou
vhalinor_env\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp config/.env.example config/.env
# Editar config/.env com suas configurações
```

### Configuração do Ambiente

Edite o arquivo `config/.env`:

```env
# Ambiente
ENVIRONMENT=development
DEBUG=true

# API Keys
OPENAI_API_KEY=your_openai_key
BINANCE_API_KEY=your_binance_key
BINANCE_SECRET_KEY=your_binance_secret

# Database
DATABASE_URL=sqlite:///vhalinor.db
REDIS_URL=redis://localhost:6379

# Trading
TRADING_ENABLED=false
RISK_LEVEL=medium
MAX_INVESTMENT=1000
```

---

## Estrutura do Projeto

```
ai_geral/
    |
    |-- config/                 # Configurações
    |   |-- __init__.py
    |   |-- .env.example
    |   |-- settings.py
    |
    |-- core/                   # Funcionalidades centrais
    |   |-- __init__.py
    |   |-- logger.py
    |   |-- exceptions.py
    |
    |-- modules/                # Módulos de negócio
    |   |-- __init__.py
    |   |-- data_fetcher.py
    |   |-- ai_analyzer.py
    |   |-- predictor.py
    |   |-- neural_network.py
    |
    |-- services/               # Serviços externos
    |   |-- __init__.py
    |   |-- websocket_service.py
    |   |-- redis_service.py
    |   |-- automation_service.py
    |
    |-- utils/                  # Utilitários
    |   |-- __init__.py
    |   |-- report_generator.py
    |   |-- helpers.py
    |
    |-- tests/                  # Testes
    |   |-- __init__.py
    |   |-- test_simple.py
    |   |-- test_report_generator.py
    |
    |-- templates/              # Templates HTML
    |   |-- reports/
    |   |-- default.html
    |
    |-- logs/                   # Logs do sistema
    |-- data/                   # Dados persistentes
    |-- reports/                # Relatórios gerados
    |
    |-- main.py                 # Aplicação principal
    |-- requirements.txt         # Dependências
    |-- pyproject.toml         # Configuração do projeto
    |-- README.md              # Documentação
```

---

## Módulos Principais

### Data Fetcher (`modules/data_fetcher.py`)

Responsável por coletar dados de diversas fontes:

- **Exchanges de Criptomoedas**: Binance, Coinbase, etc.
- **Mercados Tradicionais**: Yahoo Finance
- **Dados em Tempo Real**: WebSocket streaming
- **Cache Inteligente**: Redis para performance

**Exemplo de uso:**

```python
from modules import get_data_fetcher

fetcher = get_data_fetcher()
data = await fetcher.get_ohlcv_data("BTC/USDT", "1h", limit=100)
```

### AI Analyzer (`modules/ai_analyzer.py`)

Implementa análise avançada com IA:

- **Processamento de Linguagem**: spaCy, Transformers
- **Análise de Sentimento**: Modelos pré-treinados
- **Análise Técnica**: Redes neurais customizadas
- **Ensemble de Modelos**: Combinação de múltiplos modelos

**Exemplo de uso:**

```python
from modules import get_ai_analyzer

analyzer = get_ai_analyzer()
analysis = await analyzer.analyze_market("BTC/USDT", market_data, news_data)
```

### Predictor (`modules/predictor.py`)

Sistema de predição avançado:

- **Modelos Ensemble**: Random Forest, Gradient Boosting
- **Redes Neurais**: LSTM, Transformer blocks
- **Backtesting**: Validação histórica
- **Métricas de Risco**: Sharpe, Sortino, Drawdown

**Exemplo de uso:**

```python
from modules import get_predictor

predictor = get_predictor()
prediction = await predictor.predict_price("BTC/USDT", timeframe="1h")
```

### WebSocket Service (`services/websocket_service.py`)

Comunicação em tempo real:

- **Clientes WebSocket**: Gerenciamento de conexões
- **Pub/Sub**: Canais de comunicação
- **Autenticação**: JWT tokens
- **Rate Limiting**: Controle de acesso

**Exemplo de uso:**

```python
from services import get_websocket_service

service = get_websocket_service()
await service.start_server()
```

---

## Configuração

### Settings (`config/settings.py`)

Configuração centralizada usando Pydantic:

```python
from config import settings

# Acessar configurações
print(settings.app_name)
print(settings.database_url)
print(settings.trading_enabled)
```

### Logging (`core/logger.py`)

Sistema de logging estruturado:

```python
from core import get_logger

logger = get_logger("my_module")
logger.info("Mensagem informativa")
logger.error("Mensagem de erro", extra={"context": "additional_data"})
```

---

## Uso e Operação

### Inicialização

```bash
# Modo desenvolvimento
python main.py

# Modo produção
python -m streamlit run main.py --server.port 8080
```

### Interface Principal

O sistema oferece uma interface web com:

- **Dashboard**: Métricas em tempo real
- **Trading**: Controles de operação
- **Análise**: Resultados de IA
- **Relatórios**: Relatórios gerados
- **Configurações**: Parâmetros do sistema

### API REST

Endpoints disponíveis:

```python
# Health check
GET /health

# Dados de mercado
GET /api/market/{symbol}

# Análise de IA
POST /api/analyze

# Predições
GET /api/predict/{symbol}
```

---

## Testes

### Executar Testes

```bash
# Testes simples (sem dependências externas)
python tests/test_simple.py

# Testes completos (com pytest)
python -m pytest tests/ -v

# Testes de performance
python -m pytest tests/ -m performance

# Cobertura de código
python -m pytest tests/ --cov=modules --cov-report=html
```

### Estrutura de Testes

- **Unitários**: Testes de funções individuais
- **Integração**: Testes de módulos juntos
- **Performance**: Testes de carga e tempo
- **End-to-End**: Testes completos do sistema

---

## Relatórios

### Geração de Relatórios

O sistema gera relatórios automáticos:

```python
from utils import get_report_generator

generator = get_report_generator()
report_path = await generator.generate_trading_report(config, trades_data)
```

### Tipos de Relatórios

1. **Performance**: Métricas de trading
2. **Análise IA**: Resultados de modelos
3. **Sistema**: Saúde e status
4. **Custom**: Template personalizável

### Formatos Suportados

- HTML (interativo)
- PDF (para impressão)
- Excel (dados brutos)

---

## Troubleshooting

### Problemas Comuns

#### 1. Erro de DLL no Windows

**Erro**: `OSError: [WinError 126] Não foi possível encontrar o módulo especificado`

**Solução**: Instalar Microsoft Visual C++ Redistributable:
```bash
# Baixar e instalar
https://aka.ms/vs/17/release/vc_redist.x64.exe
```

#### 2. PyTorch não funciona

**Erro**: `ImportError: No module named 'torch'`

**Solução**: Instalar versão compatível:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

#### 3. Redis não conecta

**Erro**: `Connection refused to Redis`

**Solução**: Iniciar Redis ou desativar cache:
```bash
# Iniciar Redis
redis-server

# Ou desativar no .env
REDIS_ENABLED=false
```

#### 4. Testes não executam

**Erro**: `ModuleNotFoundError: No module named 'pytest'`

**Solução**: Instalar pytest:
```bash
pip install pytest pytest-asyncio
```

### Logs e Debug

Ativar modo debug:

```env
# config/.env
DEBUG=true
LOG_LEVEL=DEBUG
```

Verificar logs em `logs/vhalinor.log`.

### Performance

Otimizações recomendadas:

1. **Cache Redis**: Ativar para dados frequentes
2. **Async/Await**: Usar operações assíncronas
3. **Pool de Conexões**: Configurar para banco de dados
4. **Rate Limiting**: Limitar requisições externas

---

## Suporte e Contribuição

### Documentação Adicional

- [API Reference](docs/api.md)
- [Development Guide](docs/development.md)
- [Deployment Guide](docs/deployment.md)

### Comunidade

- GitHub Issues: Reportar bugs
- Discord: Discussões e suporte
- Wiki: Documentação colaborativa

### Licença

MIT License - Ver arquivo [LICENSE](LICENSE) para detalhes.

---

## Roadmap

### v6.1 (Próximo)
- [ ] Melhorias na interface web
- [ ] Mais exchanges suportadas
- [ ] Modelos de IA avançados

### v6.2 (Futuro)
- [ ] Deploy em nuvem
- [ ] API pública
- [ ] Mobile app

---

**VHALINOR AI Geral v6.0** - Sistema profissional de Inteligência Artificial

*Desenvolvido com Python 3.14+, arquitetura moderna e melhores práticas.*

import os
import json
import time
import asyncio
import threading
import logging
import urllib.request
import urllib.parse
import http.server
import socketserver
import random
from datetime import datetime

try:
    from binance import Client, ThreadedWebsocketManager
    BINANCE_AVAILABLE = True
except ImportError:
    BINANCE_AVAILABLE = False

try:
    from dotenv import load_dotenv
    load_dotenv()
    HAS_DOTENV = True
except ImportError:
    HAS_DOTENV = False

# O Gemini agora é usado apenas no frontend para cumprir as diretrizes de segurança.
GEMINI_AVAILABLE = False

from vhalinor_analytics import vhalinor_analytics
from vhalinor_ai_modules import tech_module, sentiment_module, quantum_module, moral_module, arbitrage_module, risk_module
from vhalinor_central_ai import central_ai
from vhalinor_brokerage import broker

# Configuração de Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VhalinorEngine")

if HAS_DOTENV:
    load_dotenv()

class VhalinorEngine:
    def __init__(self):
        self.config = self.load_config()
        self.running = False
        self.market_data = {}
        self.last_analysis = {}
        self.model = None
        
        # Inicializa o Cérebro Central (Vhalinor Central AI)
        logger.info("Vhalinor Engine: Acionando Cérebro Central...")
        central_ai.initialize()
        central_ai.start_processing()
        
        # Clientes de Corretora
        self.binance_client = self.init_binance()
        self.profit_trader_active = True # Simulação ativa
        
        # API Keys Adicionais
        self.alpha_vantage_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        self.quandl_key = os.getenv("QUANDL_API_KEY")
        
        # Cache de Preços para Simulação
        self.prices = {s: 0.0 for s in self.config['symbols']}
        self.price_history = {s: [] for s in self.config['symbols']}
        
        # Configura o modelo de IA no módulo de sentimento
        sentiment_module.model = self.model
        
    def load_config(self):
        with open('bot_config.json', 'r') as f:
            return json.load(f)

    def init_binance(self):
        if not BINANCE_AVAILABLE:
            logger.warning("Biblioteca 'python-binance' não instalada. Operando em modo SIMULAÇÃO.")
            return None
            
        api_key = os.getenv("BINANCE_API_KEY")
        api_secret = os.getenv("BINANCE_API_SECRET")
        if not api_key or not api_secret:
            logger.warning("Binance API Keys não encontradas. Operando em modo SIMULAÇÃO.")
            return None
        try:
            return Client(api_key, api_secret)
        except Exception as e:
            logger.error(f"Erro ao conectar na Binance: {e}")
            return None

    def get_market_snapshot(self):
        """Retorna o estado atual do mercado para o Dashboard"""
        tickers = []
        for symbol in self.config['symbols']:
            # Simulação de preço baseada no tipo de ativo
            base_price = 50.0 # Default para stocks
            if 'BTC' in symbol: base_price = 50000.0
            elif 'ETH' in symbol: base_price = 2500.0
            elif 'SOL' in symbol: base_price = 140.0
            elif 'WIN' in symbol: base_price = 125000.0
            elif 'WDO' in symbol: base_price = 5100.0
            elif any(x in symbol for x in ['PETR', 'VALE', 'ITUB']): base_price = 35.0
            
            # Tenta buscar dados reais com fallback entre fontes
            real_price = None
            
            # 1. Tenta Binance (se for símbolo de crypto)
            if any(x in symbol for x in ['BTC', 'ETH', 'SOL', 'USDT']):
                real_price = self.fetch_binance(symbol)
            
            # 2. Fallback para Alpha Vantage (se Binance falhar ou não for crypto)
            if real_price is None and self.alpha_vantage_key:
                real_price = self.fetch_alpha_vantage(symbol)
                
            # 3. Fallback para Quandl (Nasdaq Data Link)
            if real_price is None and self.quandl_key:
                real_price = self.fetch_quandl(symbol)
            
            current = real_price if real_price else self.prices.get(symbol, base_price)
            if current == 0: current = base_price
            
            change = (random.random() * 2 - 1) * 0.001
            new_price = current * (1 + change)
            self.prices[symbol] = new_price
            
            tickers.append({
                "symbol": symbol.replace('/', ''),
                "curDayClose": f"{new_price:.2f}",
                "priceChangePercent": f"{change*100:.2f}"
            })
        return tickers

    def fetch_binance(self, symbol):
        """Busca preço em tempo real na Binance"""
        if not self.binance_client:
            return None
        try:
            # Converte formato BTC/USDT para BTCUSDT
            clean_symbol = symbol.replace("/", "")
            ticker = self.binance_client.get_symbol_ticker(symbol=clean_symbol)
            return float(ticker['price'])
        except Exception as e:
            logger.debug(f"Binance API ({symbol}): {e}")
            return None

    def fetch_alpha_vantage(self, symbol):
        """Busca preço em tempo real no Alpha Vantage"""
        if not self.alpha_vantage_key:
            return None
        try:
            # Converte formatos como BTC/USDT para BTC
            clean_symbol = symbol.split("/")[0]
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={clean_symbol}&apikey={self.alpha_vantage_key}"
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode())
                if "Global Quote" in data and "05. price" in data["Global Quote"]:
                    return float(data["Global Quote"]["05. price"])
        except Exception as e:
            if "timed out" in str(e).lower():
                logger.debug(f"Alpha Vantage ({symbol}): Timeout.")
            else:
                logger.debug(f"Alpha Vantage ({symbol}): {e}")
        return None

    def fetch_quandl(self, symbol):
        """Busca preço no Quandl (Nasdaq Data Link)"""
        if not self.quandl_key:
            return None
        try:
            # Nasdaq Data Link usa formatos como WIKI/AAPL
            url = f"https://data.nasdaq.com/api/v3/datasets/{symbol}/data.json?limit=1&api_key={self.quandl_key}"
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode())
                if "dataset_data" in data and len(data["dataset_data"]["data"]) > 0:
                    # O preço de fechamento geralmente é a 4ª coluna (índice 4)
                    return float(data["dataset_data"]["data"][0][4])
                elif "dataset" in data and len(data["dataset"]["data"]) > 0:
                    return float(data["dataset"]["data"][0][4])
        except Exception as e:
            logger.debug(f"Quandl API ({symbol}): {e}")
        return None

    async def analyze_market(self):
        """Loop principal de análise IA"""
        while self.running:
            try:
                # Watchdog: Garante que o Cérebro Central está processando
                if not central_ai.running:
                    logger.warning("Watchdog: Cérebro Central inativo. Reiniciando...")
                    central_ai.start_processing()

                for symbol in self.config['symbols']:
                    logger.debug(f"Analisando {symbol} com IA Avançada...")
                    
                    current_price = self.prices.get(symbol, 0)
                    if current_price == 0: continue
                    
                    # Atualiza histórico (Simulado se vazio)
                    if len(self.price_history[symbol]) < 50:
                        self.price_history[symbol] = [current_price * (1 + (random.random() * 0.02 - 0.01)) for _ in range(50)]
                    else:
                        self.price_history[symbol].append(current_price)
                        self.price_history[symbol] = self.price_history[symbol][-100:]

                    # 1. Análise Técnica (20 Indicadores)
                    tech_analysis = tech_module.calculate_all(self.price_history[symbol])
                    
                    # 2. Análise de Sentimento (IA)
                    sentiment_data = await sentiment_module.get_sentiment(symbol)
                    sentiment_score = sentiment_data.get('score', 0.0)
                    
                    # 3. Previsão Quântica
                    quantum_pred = quantum_module.predict_price_range(current_price, 0.02)
                    
                    # 4. Análise de Risco Especializada (Daytrade/Forex)
                    risk_data = risk_module.calculate_risk(symbol, current_price, 0.02)
                    
                    # 5. Avaliação Ética e Moral (Vhalinor IAG 4.0)
                    moral_eval = moral_module.evaluate_asset(symbol)

                    # 6. Detecção de Arbitragem (Simulado com spread de mercado)
                    mock_external = {
                        "BinanceGlobal": current_price * (1 + random.uniform(-0.006, 0.006)),
                        "Kraken": current_price * (1 + random.uniform(-0.004, 0.004))
                    }
                    arbitrage_ops = arbitrage_module.detect_arbitrage(symbol, current_price, mock_external)
                    
                    # Consolidação da Recomendação com Viés Daytrade
                    score = (sentiment_score * 0.2) + (quantum_pred['quantum_confidence'] * 0.3)
                    
                    # Peso maior para indicadores de Daytrade (VWAP e RSI)
                    if tech_analysis.get('rsi', 50) < 30: score += 0.25
                    elif tech_analysis.get('rsi', 50) > 70: score -= 0.25
                    
                    if tech_analysis.get('vwap_dist', 0) < -1.5: score += 0.15 # Preço muito abaixo do VWAP (Oportunidade)
                    elif tech_analysis.get('vwap_dist', 0) > 1.5: score -= 0.15 # Preço muito acima do VWAP (Exaustão)

                    # Bônus de Arbitragem
                    if arbitrage_ops:
                        score += 0.1 * len(arbitrage_ops)
                    
                    # Se não for ético, forçamos HOLD ou SELL
                    if moral_eval['status'] == "UNETHICAL":
                        score = -1.0
                        recommendation = "RESTRICTED (UNETHICAL)"
                    else:
                        recommendation = "STRONG BUY" if score > 0.6 else "BUY" if score > 0.2 else "STRONG SELL" if score < -0.6 else "SELL" if score < -0.2 else "HOLD"

                    self.last_analysis[symbol] = {
                        "timestamp": datetime.now().isoformat(),
                        "recommendation": recommendation,
                        "score": score,
                        "technical": tech_analysis,
                        "sentiment": {
                            "score": sentiment_score,
                            "label": "Bullish" if sentiment_score > 0.2 else "Bearish" if sentiment_score < -0.2 else "Neutral",
                            "keywords": sentiment_data.get('keywords', [])
                        },
                        "quantum": quantum_pred,
                        "risk": risk_data,
                        "moral": moral_eval,
                        "arbitrage": arbitrage_ops,
                        "forex_data": {
                            "pip_change": tech_analysis.get('pip_change'),
                            "spread_cost": tech_analysis.get('spread_cost')
                        }
                    }
                    
                    # 6. Processamento no Cérebro Central (Vhalinor Central AI)
                    try:
                        central_ai.process_market_data(symbol, self.last_analysis[symbol])
                    except Exception as e:
                        logger.error(f"Erro ao processar dados no Cérebro Central: {e}")

                    # 7. Execução de Ordens Automáticas (Se o modo for AUTO)
                    if self.config.get('mode') == 'AUTO' and abs(score) > 0.8:
                        side = "BUY" if score > 0.8 else "SELL"
                        # Quantidade fixa para exemplo (0.001 BTC ou equivalente)
                        quantity = 0.001 if "BTC" in symbol else 0.01
                        try:
                            order = broker.create_order(symbol.replace("/", ""), side, quantity)
                            self.last_analysis[symbol]["last_order"] = order
                        except Exception as e:
                            logger.error(f"Erro ao executar ordem automática para {symbol}: {e}")
                
                # Frequência baseada na config
                delay = 5 if self.config['analysisFrequency'] == 'FAST' else 30
                logger.debug(f"Vhalinor Engine: Ciclo de análise concluído. Próximo pulso em {delay}s.")
                await asyncio.sleep(delay)
            except Exception as e:
                logger.error(f"Erro no loop de análise: {e}")
                await asyncio.sleep(10)

    def start(self):
        self.running = True
        # Inicia o loop de análise em uma thread separada
        def run_async_loop():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Garante que o Central AI está rodando antes de começar
            if not central_ai.running:
                central_ai.start_processing()
                
            loop.run_until_complete(self.analyze_market())
            
        threading.Thread(target=run_async_loop, daemon=True).start()

# Inicialização do Motor e Servidor
engine = VhalinorEngine()
engine.start()

# Servidor HTTP nativo para comunicação com o Node.js
class EngineHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Silencia logs de acesso padrão (200 OK, etc) para reduzir ruído
        return

    def do_POST(self):
        if self.path == '/api/broker/trade':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode())
                symbol = data.get('symbol')
                side = data.get('side')
                quantity = float(data.get('quantity', 0.001))
                
                if not symbol or not side:
                    raise ValueError("Symbol and Side are required")
                
                order = broker.create_order(symbol, side, quantity)
                body = json.dumps(order).encode()
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except Exception as e:
                response = {"error": str(e)}
                body = json.dumps(response).encode()
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        if self.path == '/api/status':
            response = {
                "engine": "Vhalinor Python Core",
                "version": "8.0.1",
                "active_symbols": engine.config['symbols'],
                "mode": engine.config['mode']
            }
            body = json.dumps(response).encode()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == '/api/market':
            body = json.dumps(engine.get_market_snapshot()).encode()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == '/api/analysis/central_ai':
            body = json.dumps(central_ai.get_status()).encode()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == '/api/broker/status':
            response = {
                "balance_usdt": broker.get_balance("USDT"),
                "type": type(broker).__name__
            }
            body = json.dumps(response).encode()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path.startswith('/api/analysis/'):
            symbol = self.path.split('/')[-1]
            body = json.dumps(engine.last_analysis.get(symbol, {"status": "pending"})).encode()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/api/lextrader/analyze':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                request_data = json.loads(post_data.decode())
                
                prices = request_data.get('prices', [])
                indicators = request_data.get('indicators', {})
                
                logger.info(f"Recebida solicitação de análise para {len(prices)} pontos de preço.")
                
                # Calcula métricas de risco vhalinor
                returns = []
                if len(prices) > 1:
                    for i in range(1, len(prices)):
                        # Prevenção de divisão por zero
                        if prices[i-1] != 0:
                            returns.append((prices[i] - prices[i-1]) / prices[i-1])
                        else:
                            returns.append(0)
                
                risk_metrics = vhalinor_analytics.calculate_risk_metrics(returns)
                monte_carlo = vhalinor_analytics.run_monte_carlo(prices[-1], risk_metrics.get('volatility', 0.2)) if prices else {}
                stress_test = vhalinor_analytics.run_stress_test(prices[-1]) if prices else []
                
                # Análise Técnica Avançada (20 indicadores)
                tech_analysis = tech_module.calculate_all(prices)
                
                # Resposta consolidada
                response = {
                    "status": "success",
                    "vhalinor": {
                        "risk": risk_metrics,
                        "monte_carlo": monte_carlo,
                        "stress_test": stress_test
                    },
                    "technical": tech_analysis,
                    "timestamp": datetime.now().isoformat()
                }
                
                body = json.dumps(response).encode()
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except Exception as e:
                logger.error(f"Erro no processamento do POST /api/lextrader/analyze: {e}")
                body = json.dumps({"status": "error", "message": str(e)}).encode()
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)
        elif self.path == '/api/central_ai/command':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode())
            
            command = request_data.get('command')
            data = request_data.get('data')
            
            result = central_ai.process_command(command, data)
            body = json.dumps(result).encode()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    # Roda na porta 3001 (interna), o Node.js fará o proxy
    PORT = 3001
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("127.0.0.1", PORT), EngineHandler) as httpd:
        logger.info(f"Motor Python servindo na porta {PORT}")
        httpd.serve_forever()

import os
import time
import json
import asyncio
from binance import AsyncClient, BinanceSocketManager
from binance.enums import *
import google.generativeai as genai
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração Gemini AI
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# Configuração Binance
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")
SYMBOL = "BTCUSDT"
QUANTITY = 0.001 # Quantidade mínima para teste

async def get_ai_decision(klines):
    """
    Envia dados históricos para o Gemini e solicita uma decisão de trading.
    """
    # Formata os dados para a IA (últimos 20 candles)
    market_summary = []
    for k in klines[-20:]:
        market_summary.append({
            "time": k[0],
            "open": k[1],
            "high": k[2],
            "low": k[3],
            "close": k[4],
            "volume": k[5]
        })

    prompt = f"""
    Você é um trader quantitativo sênior. Analise os últimos 20 candles de 1 minuto do par {SYMBOL}:
    {json.dumps(market_summary)}

    Responda ESTRITAMENTE em formato JSON:
    {{
        "decision": "BUY", "SELL" ou "HOLD",
        "confidence": 0-100,
        "reason": "breve explicação técnica"
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        # Limpa a resposta para garantir que seja um JSON válido
        clean_json = response.text.strip().replace('```json', '').replace('```', '')
        return json.loads(clean_json)
    except Exception as e:
        print(f"Erro na análise da IA: {e}")
        return {"decision": "HOLD", "confidence": 0, "reason": "Erro na API"}

async def execute_trade(client, decision_data):
    """
    Executa a ordem na Binance com base na decisão da IA.
    """
    decision = decision_data.get("decision")
    confidence = decision_data.get("confidence")
    
    if confidence < 75:
        print(f"Confiança baixa ({confidence}%). Nenhuma ordem enviada.")
        return

    try:
        if decision == "BUY":
            print(f"🚀 Executando COMPRA de {SYMBOL}...")
            # order = await client.create_order(symbol=SYMBOL, side=SIDE_BUY, type=ORDER_TYPE_MARKET, quantity=QUANTITY)
            # print(f"Ordem de COMPRA enviada: {order['orderId']}")
        elif decision == "SELL":
            print(f"🔻 Executando VENDA de {SYMBOL}...")
            # order = await client.create_order(symbol=SYMBOL, side=SIDE_SELL, type=ORDER_TYPE_MARKET, quantity=QUANTITY)
            # print(f"Ordem de VENDA enviada: {order['orderId']}")
    except Exception as e:
        print(f"Erro ao executar ordem: {e}")

async def main():
    print(f"--- Iniciando Bot de IA Vhalinor ({SYMBOL}) ---")
    client = await AsyncClient.create(API_KEY, API_SECRET)
    bm = BinanceSocketManager(client)
    
    # Stream de preços em tempo real
    ts = bm.symbol_ticker_socket(SYMBOL)

    async with ts as tscm:
        while True:
            # 1. Recuperar dados históricos para contexto
            klines = await client.get_historical_klines(SYMBOL, AsyncClient.KLINE_INTERVAL_1MINUTE, "30 minutes ago UTC")
            
            # 2. Obter decisão da IA
            print("\nAnalisando mercado com Gemini...")
            decision = await get_ai_decision(klines)
            print(f"Decisão: {decision['decision']} | Confiança: {decision['confidence']}%")
            print(f"Motivo: {decision['reason']}")

            # 3. Executar Trade
            await execute_trade(client, decision)

            # 4. Aguardar próximo ciclo (ex: 1 minuto)
            await asyncio.sleep(60)

    await client.close_connection()

if __name__ == "__main__":
    asyncio.run(main())

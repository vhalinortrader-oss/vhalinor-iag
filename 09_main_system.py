# 09_main_system.py
"""
Sistema VhalinorTrade - Sistema Principal
Orquestrador central que coordena todos os módulos
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
import pickle
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vhalinor_trade.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("VhalinorTrade")

class VhalinorTrade:
    """
    Sistema principal de trading autônomo VhalinorTrade
    Integra todos os módulos em um sistema coeso e funcional
    """
    
    def __init__(self):
        logger.info("Inicializando VhalinorTrade...")
        
        # Carrega configurações
        self.config = config
        
        # Inicializa módulos
        self.data_collector = DataCollector(self.config)
        self.technical_analyzer = TechnicalAnalyzer(self.config)
        self.pattern_recognition = PatternRecognition(self.config)
        self.neural_network = VhalinorNeuralNetwork(self.config)
        self.prediction_engine = PredictionEngine(
            self.config,
            self.neural_network,
            self.technical_analyzer,
            self.pattern_recognition
        )
        self.risk_manager = RiskManager(self.config)
        self.execution_engine = ExecutionEngine(self.config, self.risk_manager)
        
        # Estado do sistema
        self.is_running = False
        self.market_data = {}
        self.predictions_history = []
        self.performance_metrics = {}
        self.sensory_system = SensorySystem(self.config)
        
        # Inicializa conexões
        asyncio.create_task(self._initialize_connections())
        
        logger.info("VhalinorTrade inicializado com sucesso!")
        
    async def _initialize_connections(self):
        """Inicializa conexões com exchanges"""
        await self.execution_engine.connect_binance()
        await self.execution_engine.connect_bybit()
        logger.info("Conexões com exchanges estabelecidas")
        
    async def start(self):
        """Inicia o sistema de trading"""
        logger.info("="*50)
        logger.info("VHALINOR TRADE - SISTEMA DE TRADING AUTÔNOMO")
        logger.info("="*50)
        
        self.is_running = True
        
        # Inicia coleta de dados
        asyncio.create_task(self.data_collector.continuous_data_collection())
        
        # Inicia WebSockets
        asyncio.create_task(
            self.data_collector.connect_binance_websocket(self.config.symbols)
        )
        
        # Loop principal
        await self._main_loop()
        
    async def _main_loop(self):
        """Loop principal de operação"""
        logger.info("Iniciando loop principal...")
        
        while self.is_running:
            try:
                # 1. Atualiza dados de mercado
                await self._update_market_data()
                
                # 2. Análise sensorial do mercado
                market_sentiment = await self.sensory_system.analyze_market_sentiment()
                
                # 3. Para cada ativo monitorado
                for symbol in self.config.symbols:
                    await self._process_symbol(symbol, market_sentiment)
                    
                # 4. Atualiza gestão de risco
                await self._update_risk_management()
                
                # 5. Aprendizado contínuo
                await self._continuous_learning()
                
                # 6. Logs e monitoramento
                await self._log_system_status()
                
                # Aguarda próximo ciclo
                await asyncio.sleep(60)  # 1 minuto
                
            except Exception as e:
                logger.error(f"Erro no loop principal: {e}")
                await asyncio.sleep(10)
                
    async def _process_symbol(self, symbol: str, market_sentiment: Dict):
        """Processa um ativo individual"""
        if symbol not in self.market_data:
            return
            
        market_data = self.market_data[symbol]
        
        # Análise técnica completa
        for timeframe, df in market_data.items():
            if df is not None and len(df) > 50:
                # Análise de mercado
                analysis = self.technical_analyzer.full_market_analysis(df)
                
                # Reconhecimento de padrões
                hidden_patterns = self.pattern_recognition.detect_hidden_patterns(df)
                
                # Armazena análise
                self.market_data[symbol][f'{timeframe}_analysis'] = analysis
                self.market_data[symbol][f'{timeframe}_hidden'] = hidden_patterns
                
        # Gera predições
        predictions = await self.prediction_engine.generate_predictions(
            symbol, market_data
        )
        
        if predictions:
            # Consolida predições
            ensemble = self.prediction_engine.ensemble_prediction(predictions)
            
            if ensemble and ensemble['signal'] in ['STRONG_BUY', 'STRONG_SELL', 'BUY', 'SELL']:
                # Verifica condições de risco
                if await self._check_trading_conditions(symbol, ensemble):
                    # Executa trade
                    await self._execute_trade_signal(symbol, ensemble)
                    
    async def _execute_trade_signal(self, symbol: str, signal: Dict):
        """Executa sinal de trading"""
        try:
            # Obtém dados atuais
            current_price = self._get_current_price(symbol)
            available_capital = self.risk_manager.total_capital * 0.1  # 10% por trade
            
            # Calcula tamanho da posição
            stop_loss = current_price * (1 - self.config.trading.stop_loss_percentage)
            position_size = self.risk_manager.calculate_position_size(
                available_capital, current_price, stop_loss
            )
            
            if position_size <= 0:
                logger.warning(f"Tamanho de posição inválido para {symbol}")
                return
                
            # Determina lado da ordem
            if signal['signal'] in ['STRONG_BUY', 'BUY']:
                side = OrderSide.BUY
            else:
                side = OrderSide.SELL
                
            # Executa ordem
            result = await self.execution_engine.place_order(
                symbol=symbol,
                side=side,
                order_type=OrderType.LIMIT,
                quantity=position_size / current_price,
                price=current_price
            )
            
            if result['status'] == 'SUCCESS':
                logger.info(f"Trade executado: {signal['signal']} {symbol} "
                          f"Qty: {position_size/current_price:.6f}")
                
                # Registra predição
                self.predictions_history.append({
                    'symbol': symbol,
                    'signal': signal,
                    'order_id': result['order_id'],
                    'timestamp': datetime.now()
                })
                
        except Exception as e:
            logger.error(f"Erro ao executar trade {symbol}: {e}")
            
    async def _check_trading_conditions(self, symbol: str, 
                                       signal: Dict) -> bool:
        """Verifica condições para trading"""
        # Confiança mínima
        if signal['confidence'] < 0.6:
            return False
            
        # Verifica exposição
        exposure = self.risk_manager.calculate_exposure_limits()
        if exposure['remaining'] <= 0:
            return False
            
        # Verifica condições extremas
        if self.risk_manager.emergency_stop({}):
            return False
            
        # Verifica sobreposição de trades
        active_trades = len([o for o in self.execution_engine.active_orders.values() 
                            if o['status'] == OrderStatus.FILLED])
        if active_trades >= self.config.trading.max_concurrent_trades:
            return False
            
        return True
        
    async def _continuous_learning(self):
        """Sistema de aprendizado contínuo"""
        for symbol in self.config.symbols:
            if symbol in self.market_data:
                for timeframe, df in self.market_data[symbol].items():
                    if isinstance(df, pd.DataFrame) and len(df) > 100:
                        # Atualiza padrões
                        self.pattern_recognition.learn_new_patterns(df)
                        
                        # Atualiza rede neural
                        await self.neural_network.continuous_learning(symbol, df)
                        
    async def _update_risk_management(self):
        """Atualiza parâmetros de gestão de risco"""
        total_equity = self._calculate_total_equity()
        self.risk_manager.total_capital = total_equity
        
        # Atualiza fundo de reserva
        if self.risk_manager.reserve_fund < total_equity * 0.2:
            self.risk_manager.reserve_fund += total_equity * 0.01
            
    def _calculate_total_equity(self) -> float:
        """Calcula patrimônio total"""
        # Implementar cálculo real
        return 100000  # Placeholder
        
    def _get_current_price(self, symbol: str) -> float:
        """Obtém preço atual"""
        # Implementar obtenção real
        return 50000  # Placeholder
        
    async def _update_market_data(self):
        """Atualiza dados de mercado"""
        for symbol in self.config.symbols:
            self.market_data[symbol] = {}
            
            for timeframe in self.config.timeframes:
                df = await self.data_collector.fetch_historical_data(
                    symbol, timeframe.value
                )
                self.market_data[symbol][timeframe.value] = df
                
    async def _log_system_status(self):
        """Loga status do sistema"""
        metrics = self.get_system_metrics()
        logger.info(f"Status: Trades ativos: {metrics['active_trades']}, "
                   f"Exposição: {metrics['exposure']:.2%}, "
                   f"Reserva: ${metrics['reserve_fund']:.2f}")
                   
    def get_system_metrics(self) -> Dict:
        """Retorna métricas do sistema"""
        return {
            'active_trades': len(self.execution_engine.active_orders),
            'exposure': self.risk_manager.calculate_exposure_limits()['utilization'],
            'reserve_fund': self.risk_manager.reserve_fund,
            'predictions_today': len([p for p in self.predictions_history 
                                      if p['timestamp'].date() == datetime.now().date()]),
            'win_rate': self.execution_engine.get_performance_metrics().get('win_rate', 0)
        }
        
    async def stop(self):
        """Para o sistema com segurança"""
        logger.info("Parando VhalinorTrade...")
        self.is_running = False
        
        # Fecha todas as posições
        await self.execution_engine.emergency_close_all()
        
        # Salva estado
        self._save_system_state()
        
        logger.info("Sistema parado com segurança")
        
    def _save_system_state(self):
        """Salva estado do sistema"""
        state = {
            'predictions_history': self.predictions_history,
            'performance_metrics': self.performance_metrics,
            'timestamp': datetime.now()
        }
        
        with open(f"{self.config.data_path}/system_state.pkl", 'wb') as f:
            pickle.dump(state, f)
            
    def _load_system_state(self):
        """Carrega estado anterior"""
        state_file = f"{self.config.data_path}/system_state.pkl"
        
        if os.path.exists(state_file):
            with open(state_file, 'rb') as f:
                state = pickle.load(f)
                self.predictions_history = state['predictions_history']
                self.performance_metrics = state['performance_metrics']
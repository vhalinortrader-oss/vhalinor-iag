# 10_sensory_system.py
"""
Sistema VhalinorTrade - Sistema Sensorial
Monitoramento de mercado, notícias e eventos externos
"""

import asyncio
import aiohttp
from textblob import TextBlob
from typing import Dict, List, Optional
import numpy as np
from datetime import datetime, timedelta
import re

class SensorySystem:
    """
    Sistema sensorial que monitora fatores externos:
    - Notícias de mercado
    - Redes sociais
    - On-chain data
    - Indicadores macro
    """
    
    def __init__(self, config):
        self.config = config
        self.sentiment_scores = {}
        self.news_cache = []
        self.social_signals = {}
        self.macro_indicators = {}
        
    async def analyze_market_sentiment(self) -> Dict[str, float]:
        """Análise completa de sentimento de mercado"""
        # Coleta múltiplas fontes
        news_sentiment = await self._analyze_news_sentiment()
        social_sentiment = await self._analyze_social_media()
        fear_greed = await self._get_fear_greed_index()
        onchain_metrics = await self._analyze_onchain_data()
        
        # Combina scores
        combined_sentiment = {
            'overall': np.mean([
                news_sentiment.get('score', 0.5),
                social_sentiment.get('score', 0.5),
                fear_greed.get('normalized', 0.5),
                onchain_metrics.get('sentiment', 0.5)
            ]),
            'news': news_sentiment,
            'social': social_sentiment,
            'fear_greed': fear_greed,
            'onchain': onchain_metrics,
            'timestamp': datetime.now()
        }
        
        self.sentiment_scores = combined_sentiment
        return combined_sentiment
    
    async def _analyze_news_sentiment(self) -> Dict[str, float]:
        """Analisa sentimento de notícias"""
        # Simulação - em produção, integrar com APIs de notícias
        headlines = await self._fetch_crypto_news()
        
        if not headlines:
            return {'score': 0.5, 'count': 0}
            
        sentiments = []
        for headline in headlines:
            blob = TextBlob(headline)
            sentiments.append(blob.sentiment.polarity)
            
        return {
            'score': (np.mean(sentiments) + 1) / 2,  # Normaliza para 0-1
            'count': len(headlines),
            'positive_ratio': sum(1 for s in sentiments if s > 0.2) / len(sentiments),
            'negative_ratio': sum(1 for s in sentiments if s < -0.2) / len(sentiments)
        }
    
    async def _fetch_crypto_news(self) -> List[str]:
        """Busca notícias de criptomoedas"""
        # Placeholder - implementar integração real
        return [
            "Bitcoin shows strong momentum ahead of halving",
            "Ethereum DeFi ecosystem continues to grow",
            "Institutional investors increase crypto allocation"
        ]
    
    async def _analyze_social_media(self) -> Dict[str, float]:
        """Analisa tendências em redes sociais"""
        # Simulação de métricas sociais
        return {
            'score': np.random.uniform(0.3, 0.7),
            'volume': np.random.uniform(0.5, 1.5),
            'engagement': np.random.uniform(0.4, 0.8),
            'influencer_sentiment': np.random.uniform(0.3, 0.7)
        }
    
    async def _get_fear_greed_index(self) -> Dict[str, float]:
        """Obtém índice de medo e ganância"""
        # Placeholder - integrar com API real
        fear_greed = np.random.randint(20, 80)
        
        return {
            'value': fear_greed,
            'normalized': fear_greed / 100,
            'classification': 'fear' if fear_greed < 35 else 
                            'greed' if fear_greed > 65 else 'neutral'
        }
    
    async def _analyze_onchain_data(self) -> Dict[str, float]:
        """Analisa dados on-chain"""
        # Placeholder - integrar com Glassnode/Dune Analytics
        return {
            'sentiment': np.random.uniform(0.4, 0.6),
            'active_addresses_trend': np.random.choice(['increasing', 'decreasing', 'stable']),
            'exchange_flows': np.random.uniform(-1, 1),
            'whale_activity': np.random.uniform(0, 1)
        }
    
    def detect_market_regime(self) -> Dict[str, any]:
        """Detecta regime atual de mercado"""
        sentiment = self.sentiment_scores.get('overall', 0.5)
        
        if sentiment > 0.7:
            regime = 'bullish'
            risk_level = 0.3
        elif sentiment < 0.3:
            regime = 'bearish'
            risk_level = 0.8
        elif 0.4 <= sentiment <= 0.6:
            regime = 'neutral'
            risk_level = 0.5
        else:
            regime = 'transitional'
            risk_level = 0.6
            
        return {
            'regime': regime,
            'risk_level': risk_level,
            'sentiment': sentiment,
            'recommended_exposure': 1 - risk_level
        }
    
    async def monitor_whale_movements(self) -> Dict[str, List]:
        """Monitora movimentos de grandes carteiras"""
        # Placeholder
        return {
            'large_transactions': [],
            'exchange_inflows': np.random.uniform(0, 1),
            'exchange_outflows': np.random.uniform(0, 1)
        }
    
    async def detect_anomalies(self) -> Dict[str, any]:
        """Detecta anomalias de mercado"""
        anomalies = {
            'flash_crash_risk': np.random.uniform(0, 0.1),
            'pump_risk': np.random.uniform(0, 0.15),
            'volume_anomaly': np.random.uniform(0, 0.2),
            'spread_anomaly': np.random.uniform(0, 0.1)
        }
        
        # Threshold para alerta
        high_risk = {k: v for k, v in anomalies.items() if v > 0.5}
        
        return {
            'anomalies': anomalies,
            'high_risk_factors': high_risk,
            'overall_anomaly_score': np.mean(list(anomalies.values())),
            'requires_action': len(high_risk) > 0
        }
    
    def get_trading_recommendations(self) -> Dict[str, any]:
        """Gera recomendações baseadas no sistema sensorial"""
        market_regime = self.detect_market_regime()
        
        recommendations = {
            'max_position_size': market_regime['recommended_exposure'] * 0.1,
            'preferred_timeframes': [],
            'risk_per_trade': 0.01,
            'max_trades': 3
        }
        
        if market_regime['regime'] == 'bullish':
            recommendations['preferred_timeframes'] = ['4h', '1d']
            recommendations['risk_per_trade'] = 0.02
            recommendations['max_trades'] = 5
        elif market_regime['regime'] == 'bearish':
            recommendations['preferred_timeframes'] = ['1m', '5m']
            recommendations['risk_per_trade'] = 0.005
            recommendations['max_trades'] = 1
            
        return recommendations
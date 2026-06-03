#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Simples do VHALINOR AI Modules
"""

import sys
import os

# Adicionar o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from vhalinor_ai_modules import (
        NeuralNetworkType, CognitiveState, QuantumState, PredictionType,
        AdvancedNeuralNetwork, RealTimeProcessor, AdvancedCognitiveAnalyzer, 
        AdvancedPredictionSystem, EnhancedTechnicalAnalysisModule,
        TechnicalAnalysisModule, SentimentAnalysisModule, QuantumAIModule,
        MoralEthicsModule, ArbitrageAnalysisModule, RiskManagementModule,
        tech_module, sentiment_module, quantum_module, moral_module,
        arbitrage_module, risk_module, neural_network_module,
        realtime_processor, cognitive_analyzer_module, prediction_system_module
    )
    
    print("SUCCESS: All modules imported successfully!")
    
    # Testar funcionalidades básicas
    print("\nTesting basic functionality...")
    
    # Testar rede neural
    nn = AdvancedNeuralNetwork()
    test_input = [0.1, 0.2, 0.3, 0.4, 0.5]
    output = nn.forward_pass(test_input)
    print(f"Neural Network Output: {len(output)} values")
    
    # Testar análise técnica
    prices = [100, 101, 102, 103, 104, 105] * 5
    indicators = tech_module.calculate_all(prices)
    print(f"Technical Analysis: SMA20 = {indicators.get('sma20', 'N/A')}")
    
    # Testar análise cognitiva
    analyzer = AdvancedCognitiveAnalyzer()
    market_data = {'price': 100, 'volume': 5000, 'price_change': 0.05, 'avg_volume': 4000}
    analysis = analyzer.analyze_market_data(market_data)
    print(f"Cognitive Analysis: Consciousness = {analysis['consciousness']:.3f}")
    
    # Testar sistema de predição
    pred_system = AdvancedPredictionSystem()
    features = [0.1, 0.2, 0.3, 0.4, 0.5]
    prediction = pred_system.predict_ensemble(features)
    print(f"Prediction System: Prediction = {prediction['prediction']:.3f}")
    
    print("\nAll basic tests passed!")
    print("VHALINOR AI Modules v5.0 is working correctly!")
    
except ImportError as e:
    print(f"ERROR: Import failed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"ERROR: Test failed: {e}")
    sys.exit(1)

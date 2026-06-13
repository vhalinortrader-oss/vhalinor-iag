# 04_pattern_recognition.py
"""
Sistema VhalinorTrade - Reconhecimento de Padrões Históricos
Identificação de padrões recorrentes e ocultos com ML
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
import pickle
from datetime import datetime

class PatternRecognition:
    def __init__(self, config):
        self.config = config
        self.pattern_database = {}
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=10)
        
    def extract_price_patterns(self, df: pd.DataFrame, 
                              window_size: int = 20,
                              step: int = 5) -> List[np.ndarray]:
        """Extrai segmentos de preço para análise de padrões"""
        patterns = []
        close_normalized = self._normalize_series(df['close'].values)
        
        for i in range(0, len(close_normalized) - window_size, step):
            window = close_normalized[i:i+window_size]
            patterns.append(window)
            
        return patterns
    
    def _normalize_series(self, series: np.ndarray) -> np.ndarray:
        """Normaliza série para comparação"""
        return (series - series.min()) / (series.max() - series.min() + 1e-8)
    
    def find_similar_patterns(self, current_pattern: np.ndarray,
                             historical_patterns: List[np.ndarray],
                             threshold: float = 0.1) -> List[int]:
        """Encontra padrões históricos similares usando DTW"""
        similar_indices = []
        
        for idx, hist_pattern in enumerate(historical_patterns):
            distance, _ = fastdtw(current_pattern, hist_pattern, dist=euclidean)
            normalized_distance = distance / len(current_pattern)
            
            if normalized_distance < threshold:
                similar_indices.append(idx)
                
        return similar_indices
    
    def cluster_patterns(self, patterns: List[np.ndarray], 
                        eps: float = 0.3,
                        min_samples: int = 5) -> Dict[int, List[int]]:
        """Agrupa padrões similares usando DBSCAN"""
        patterns_scaled = self.scaler.fit_transform(patterns)
        patterns_reduced = self.pca.fit_transform(patterns_scaled)
        
        clustering = DBSCAN(eps=eps, min_samples=min_samples)
        labels = clustering.fit_predict(patterns_reduced)
        
        clusters = {}
        for idx, label in enumerate(labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(idx)
            
        return clusters
    
    def analyze_pattern_outcome(self, df: pd.DataFrame,
                               pattern_indices: List[int],
                               window_size: int = 20,
                               future_window: int = 5) -> Dict[str, float]:
        """Analisa o resultado de padrões identificados"""
        outcomes = []
        
        for idx in pattern_indices:
            if idx + window_size + future_window < len(df):
                entry_price = df['close'].iloc[idx + window_size]
                exit_price = df['close'].iloc[idx + window_size + future_window]
                price_change = (exit_price - entry_price) / entry_price
                outcomes.append(price_change)
                
        if not outcomes:
            return {'avg_return': 0, 'win_rate': 0, 'avg_win': 0, 'avg_loss': 0}
            
        outcomes = np.array(outcomes)
        wins = outcomes[outcomes > 0]
        losses = outcomes[outcomes < 0]
        
        return {
            'avg_return': np.mean(outcomes),
            'win_rate': len(wins) / len(outcomes),
            'avg_win': np.mean(wins) if len(wins) > 0 else 0,
            'avg_loss': np.mean(losses) if len(losses) > 0 else 0,
            'max_win': np.max(outcomes),
            'max_loss': np.min(outcomes)
        }
    
    def detect_hidden_patterns(self, df: pd.DataFrame) -> Dict[str, any]:
        """Detecta padrões ocultos usando análise de Fourier e Wavelet"""
        close = df['close'].values
        
        # Análise de Fourier
        fft = np.fft.fft(close)
        frequencies = np.fft.fftfreq(len(close))
        
        # Encontra frequências dominantes
        magnitude = np.abs(fft)
        dominant_freq_idx = np.argsort(magnitude)[-5:]  # Top 5 frequências
        dominant_frequencies = frequencies[dominant_freq_idx]
        
        # Análise de ciclo
        cycles = []
        for freq in dominant_frequencies:
            if freq != 0:
                cycle_length = 1 / abs(freq)
                cycles.append(cycle_length)
                
        # Fractalidade
        hurst_exponent = self._calculate_hurst_exponent(close)
        
        return {
            'dominant_cycles': cycles,
            'hurst_exponent': hurst_exponent,
            'is_trending': hurst_exponent > 0.5,
            'is_mean_reverting': hurst_exponent < 0.5,
            'is_random_walk': abs(hurst_exponent - 0.5) < 0.1
        }
    
    def _calculate_hurst_exponent(self, ts: np.ndarray) -> float:
        """Calcula o expoente de Hurst para detectar regimes de mercado"""
        lags = range(2, min(100, len(ts)//2))
        tau = [np.sqrt(np.std(np.subtract(ts[lag:], ts[:-lag]))) for lag in lags]
        
        poly = np.polyfit(np.log(lags), np.log(tau), 1)
        return poly[0]
    
    def pattern_backtesting(self, df: pd.DataFrame,
                          pattern_detector_func,
                          train_ratio: float = 0.7) -> Dict[str, any]:
        """Backtesting de padrões históricos"""
        split_idx = int(len(df) * train_ratio)
        train_df = df[:split_idx]
        test_df = df[split_idx:]
        
        patterns_train = self.extract_price_patterns(train_df)
        patterns_test = self.extract_price_patterns(test_df)
        
        results = []
        
        for i, test_pattern in enumerate(patterns_test):
            similar_indices = self.find_similar_patterns(
                test_pattern, patterns_train
            )
            
            if similar_indices:
                outcome = self.analyze_pattern_outcome(
                    train_df, similar_indices
                )
                
                actual_idx = split_idx + i * 5
                if actual_idx + 25 < len(df):
                    actual_return = (
                        df['close'].iloc[actual_idx + 25] - 
                        df['close'].iloc[actual_idx + 20]
                    ) / df['close'].iloc[actual_idx + 20]
                    
                    results.append({
                        'predicted_return': outcome['avg_return'],
                        'actual_return': actual_return,
                        'predicted_win_rate': outcome['win_rate'],
                        'was_correct': np.sign(outcome['avg_return']) == np.sign(actual_return)
                    })
                    
        if not results:
            return {'accuracy': 0, 'total_trades': 0}
            
        df_results = pd.DataFrame(results)
        
        return {
            'accuracy': df_results['was_correct'].mean(),
            'total_trades': len(df_results),
            'avg_predicted_return': df_results['predicted_return'].mean(),
            'avg_actual_return': df_results['actual_return'].mean(),
            'correlation': df_results['predicted_return'].corr(df_results['actual_return'])
        }
    
    def learn_new_patterns(self, df: pd.DataFrame):
        """Aprendizado contínuo de novos padrões"""
        new_patterns = self.extract_price_patterns(df)
        clusters = self.cluster_patterns(new_patterns)
        
        # Atualiza banco de dados de padrões
        timestamp = datetime.now().isoformat()
        
        for label, indices in clusters.items():
            if label != -1 and len(indices) >= 5:
                representative_pattern = new_patterns[indices[len(indices)//2]]
                
                pattern_key = f"{timestamp}_{label}"
                self.pattern_database[pattern_key] = {
                    'pattern': representative_pattern,
                    'frequency': len(indices),
                    'outcomes': self.analyze_pattern_outcome(df, indices),
                    'timestamp': timestamp
                }
                
    def get_most_reliable_patterns(self, min_frequency: int = 10,
                                  min_win_rate: float = 0.6,
                                  top_n: int = 10) -> List[Dict]:
        """Retorna os padrões mais confiáveis do banco de dados"""
        reliable_patterns = []
        
        for key, pattern_data in self.pattern_database.items():
            if (pattern_data['frequency'] >= min_frequency and 
                pattern_data['outcomes']['win_rate'] >= min_win_rate):
                reliable_patterns.append({
                    'key': key,
                    **pattern_data
                })
                
        # Ordena por win_rate * frequency
        reliable_patterns.sort(
            key=lambda x: x['outcomes']['win_rate'] * x['frequency'],
            reverse=True
        )
        
        return reliable_patterns[:top_n]
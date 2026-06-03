import pandas as pd
import numpy as np

def vhalinor(df, 
             len_ema_fast=9, 
             len_ema_slow=21, 
             len_rsi=14, 
             len_macd_fast=12, 
             len_macd_slow=26, 
             len_macd_sig=9, 
             len_bb=20, 
             bb_mult=2.0, 
             len_stoch=14, 
             smooth_k=3, 
             smooth_d=3, 
             vol_ma_len=20):
    """
    Calcula o indicador VHALINOR completo.
    
    Parâmetros:
    df : DataFrame com colunas ['open', 'high', 'low', 'close', 'volume']
    
    Retorna: DataFrame original + colunas do VHALINOR
    """
    
    df = df.copy()
    
    # ====================== CÁLCULO DOS 7 INDICADORES ======================
    
    # 1. Médias Móveis + VWAP
    df['ema_fast'] = df['close'].ewm(span=len_ema_fast, adjust=False).mean()
    df['ema_slow'] = df['close'].ewm(span=len_ema_slow, adjust=False).mean()
    
    # VWAP (cumulativo do dia - simplificado para intraday)
    df['typical_price'] = (df['high'] + df['low'] + df['close']) / 3
    df['tp_volume'] = df['typical_price'] * df['volume']
    df['cum_tp_volume'] = df['tp_volume'].cumsum()
    df['cum_volume'] = df['volume'].cumsum()
    df['vwap'] = df['cum_tp_volume'] / df['cum_volume']
    
    # 2. RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=len_rsi).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=len_rsi).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # 3. MACD
    ema12 = df['close'].ewm(span=len_macd_fast, adjust=False).mean()
    ema26 = df['close'].ewm(span=len_macd_slow, adjust=False).mean()
    df['macd_line'] = ema12 - ema26
    df['macd_signal'] = df['macd_line'].ewm(span=len_macd_sig, adjust=False).mean()
    df['macd_hist'] = df['macd_line'] - df['macd_signal']
    
    # 4. Bandas de Bollinger
    df['bb_basis'] = df['close'].rolling(window=len_bb).mean()
    df['bb_dev'] = df['close'].rolling(window=len_bb).std()
    df['bb_upper'] = df['bb_basis'] + bb_mult * df['bb_dev']
    df['bb_lower'] = df['bb_basis'] - bb_mult * df['bb_dev']
    
    # 5. Volume MA
    df['vol_ma'] = df['volume'].rolling(window=vol_ma_len).mean()
    
    # 6. OBV
    df['obv'] = (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum()
    df['obv_ma'] = df['obv'].rolling(window=vol_ma_len).mean()
    
    # 7. Estocástico
    low_min = df['low'].rolling(window=len_stoch).min()
    high_max = df['high'].rolling(window=len_stoch).max()
    df['stoch_raw'] = 100 * ((df['close'] - low_min) / (high_max - low_min))
    df['stoch_k'] = df['stoch_raw'].rolling(window=smooth_k).mean()
    df['stoch_d'] = df['stoch_k'].rolling(window=smooth_d).mean()
    
    # ====================== SCORE VHALINOR (0-100) ======================
    score = pd.Series(50.0, index=df.index)
    
    # 1. MA + VWAP
    ma_bull = (df['close'] > df['ema_fast']) & (df['ema_fast'] > df['ema_slow']) & (df['close'] > df['vwap'])
    ma_bear = (df['close'] < df['ema_fast']) & (df['ema_fast'] < df['ema_slow']) & (df['close'] < df['vwap'])
    score += np.where(ma_bull, 20, np.where(ma_bear, -20, 0))
    
    # 2. RSI
    score += np.where(df['rsi'] > 50, 10, -10)
    score += np.where(df['rsi'] < 30, 15, 0)
    score += np.where(df['rsi'] > 70, -15, 0)
    
    # 3. MACD
    macd_bull = (df['macd_line'] > df['macd_signal']) & (df['macd_hist'] > 0)
    macd_bear = (df['macd_line'] < df['macd_signal']) & (df['macd_hist'] < 0)
    score += np.where(macd_bull, 15, np.where(macd_bear, -15, 0))
    
    # 4. Bollinger
    bb_bull = df['close'] > df['bb_upper']
    bb_bear = df['close'] < df['bb_lower']
    score += np.where(bb_bull, 10, np.where(bb_bear, -10, 0))
    
    # 5+6. Volume + OBV
    vol_bull = (df['volume'] > df['vol_ma']) & (df['close'] > df['open']) & (df['obv'] > df['obv_ma'])
    vol_bear = ((df['volume'] > df['vol_ma']) & (df['close'] < df['open'])) | (df['obv'] < df['obv_ma'])
    score += np.where(vol_bull, 15, np.where(vol_bear, -15, 0))
    
    # 7. Estocástico
    stoch_bull = (df['stoch_k'] > df['stoch_d']) & (df['stoch_k'] < 80)
    stoch_bear = (df['stoch_k'] < df['stoch_d']) & (df['stoch_k'] > 20)
    score += np.where(stoch_bull, 15, np.where(stoch_bear, -15, 0))
    
    # Limita entre 0 e 100
    df['vhalinor_score'] = np.clip(score, 0, 100)
    
    # Sinais de Compra e Venda
    df['buy_signal'] = (df['vhalinor_score'] > 70) & (df['vhalinor_score'].shift(1) <= 70)
    df['sell_signal'] = (df['vhalinor_score'] < 30) & (df['vhalinor_score'].shift(1) >= 30)
    
    return df


# ====================== EXEMPLO DE USO ======================
if __name__ == "__main__":
    # Exemplo com dados fictícios ou reais (substitua pelo seu DataFrame)
    # df = pd.read_csv('seu_arquivo.csv', parse_dates=['datetime'])
    # df = df.set_index('datetime')
    
    print("Função VHALINOR criada com sucesso!")
    print("Colunas adicionadas: ema_fast, ema_slow, vwap, rsi, macd_line, bb_upper, bb_lower, vol_ma, obv, stoch_k, vhalinor_score, buy_signal, sell_signal")
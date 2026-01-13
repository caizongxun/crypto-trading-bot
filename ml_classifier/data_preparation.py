import pandas as pd


def prepare_signal_data(df: pd.DataFrame) -> pd.DataFrame:
    """Filter to rows where there is a non-zero signal."""
    return df[df['signal'] != 0].copy()


def label_signals(df: pd.DataFrame, hold_period: int = 3, profit_threshold: float = 0.0005) -> pd.DataFrame:
    """Label each signal as true (1) or false (0) based on forward return."""
    df = df.copy()
    df['future_close'] = df['close'].shift(-hold_period)
    df['return_pct'] = 0.0
    
    buy_mask = df['signal'] == 1
    sell_mask = df['signal'] == -1
    
    df.loc[buy_mask, 'return_pct'] = (df.loc[buy_mask, 'future_close'] - df.loc[buy_mask, 'close']) / df.loc[buy_mask, 'close']
    df.loc[sell_mask, 'return_pct'] = (df.loc[sell_mask, 'close'] - df.loc[sell_mask, 'future_close']) / df.loc[sell_mask, 'close']
    
    df['label'] = (df['return_pct'] > profit_threshold).astype(int)
    
    df = df.dropna(subset=['future_close'])
    
    return df

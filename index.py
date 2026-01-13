import pandas as pd
import numpy as np
from modules.indicators import CompositeIndicator
from huggingface_hub import hf_hub_download
from pathlib import Path
import sys


def load_klines(symbol: str, timeframe: str, cache_dir: str = './data_cache') -> pd.DataFrame:
    """
    Load cryptocurrency OHLCV data from HuggingFace dataset
    
    Args:
        symbol: Trading pair (e.g., 'BTCUSDT', 'ETHUSDT')
        timeframe: Timeframe ('15m', '1h', '1d')
        cache_dir: Local cache directory
    
    Returns:
        DataFrame with OHLCV data
    """
    repo_id = "zongowo111/v2-crypto-ohlcv-data"
    base = symbol.replace("USDT", "")
    filename = f"{base}_{timeframe}.parquet"
    path_in_repo = f"klines/{symbol}/{filename}"
    
    Path(cache_dir).mkdir(parents=True, exist_ok=True)
    
    local_path = hf_hub_download(
        repo_id=repo_id,
        filename=path_in_repo,
        repo_type="dataset",
        cache_dir=cache_dir
    )
    
    df = pd.read_parquet(local_path)
    return df


def calculate_signals(symbol: str, timeframe: str = '1h', lookback: int = 500) -> pd.DataFrame:
    """
    Calculate trading signals for a symbol using composite indicator
    
    Args:
        symbol: Trading pair
        timeframe: Timeframe for analysis
        lookback: Number of recent candles to analyze
    
    Returns:
        DataFrame with signals and indicator values
    """
    print(f"Loading data for {symbol} ({timeframe})...")
    df = load_klines(symbol, timeframe)
    
    # Keep only recent data
    df = df.tail(lookback).reset_index(drop=True)
    
    print(f"Data shape: {df.shape}")
    print(f"Date range: {df['open_time'].min()} to {df['open_time'].max()}")
    
    # Calculate indicators
    print("Calculating composite indicators...")
    indicator = CompositeIndicator(
        lookback=20,
        volume_threshold=1.2,
        momentum_threshold=0.5,
        trend_strength=0.6
    )
    
    result_df = indicator.calculate(df)
    
    # Display results
    print("\n" + "="*80)
    print(f"SIGNAL ANALYSIS FOR {symbol} ({timeframe})")
    print("="*80)
    
    # Show recent signals
    display_cols = [
        'open_time', 'close', 'volume', 
        'momentum_score', 'trend_score', 'volume_score', 'volatility_score',
        'signal', 'signal_strength'
    ]
    
    recent_signals = result_df[display_cols].tail(20).copy()
    
    # Format display
    for col in ['momentum_score', 'trend_score', 'volume_score', 'volatility_score', 'signal_strength']:
        recent_signals[col] = recent_signals[col].apply(lambda x: f"{x:.3f}")
    
    recent_signals['signal'] = recent_signals['signal'].apply(
        lambda x: 'BUY' if x == 1 else ('SELL' if x == -1 else 'HOLD')
    )
    
    print("\nLast 20 Candles:")
    print(recent_signals.to_string(index=False))
    
    # Signal statistics
    print("\n" + "-"*80)
    print("SIGNAL STATISTICS")
    print("-"*80)
    
    total_signals = (result_df['signal'] != 0).sum()
    buy_signals = (result_df['signal'] == 1).sum()
    sell_signals = (result_df['signal'] == -1).sum()
    avg_strength = result_df[result_df['signal'] != 0]['signal_strength'].mean()
    
    print(f"Total Signals Generated: {total_signals}")
    print(f"Buy Signals: {buy_signals}")
    print(f"Sell Signals: {sell_signals}")
    print(f"Average Signal Strength: {avg_strength:.3f}")
    print(f"Signal Frequency: {total_signals / len(result_df) * 100:.2f}%")
    
    # Current status
    print("\n" + "-"*80)
    print("CURRENT STATUS")
    print("-"*80)
    
    latest = result_df.iloc[-1]
    print(f"Latest Close Price: {latest['close']:.2f}")
    print(f"Current RSI: {latest['rsi']:.2f}")
    print(f"Current MACD: {latest['macd']:.6f}")
    print(f"Current Trend Score: {latest['trend_score']:.3f}")
    print(f"Current Volume Ratio: {latest['volume_ratio']:.3f}")
    print(f"Last Signal: {'BUY' if latest['signal'] == 1 else ('SELL' if latest['signal'] == -1 else 'HOLD')}")
    print(f"Last Signal Strength: {latest['signal_strength']:.3f}")
    
    return result_df


if __name__ == "__main__":
    # Default symbols for testing
    symbols = ['BTCUSDT', 'ETHUSDT']
    timeframe = '1h'
    
    if len(sys.argv) > 1:
        symbols = [sys.argv[1]]
    
    if len(sys.argv) > 2:
        timeframe = sys.argv[2]
    
    for symbol in symbols:
        try:
            result_df = calculate_signals(symbol, timeframe)
            print("\n" + "#"*80 + "\n")
        except Exception as e:
            print(f"Error processing {symbol}: {str(e)}")
            continue

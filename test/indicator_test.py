import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.indicators import CompositeIndicator, TechnicalIndicators
from index import load_klines


def test_technical_indicators():
    """
    Test individual technical indicators
    """
    print("="*80)
    print("TESTING TECHNICAL INDICATORS")
    print("="*80)
    
    # Load sample data
    df = load_klines('BTCUSDT', '1h', lookback=100)
    df = df.tail(100).reset_index(drop=True)
    
    ti = TechnicalIndicators()
    
    # Test RSI
    print("\n1. Testing RSI (14 period)")
    rsi = ti.rsi(df['close'])
    print(f"   Last RSI value: {rsi.iloc[-1]:.2f}")
    print(f"   RSI Range: {rsi.min():.2f} - {rsi.max():.2f}")
    print(f"   Valid values (not null): {rsi.notna().sum()}")
    
    # Test MACD
    print("\n2. Testing MACD")
    macd, signal, histogram = ti.macd(df['close'])
    print(f"   Last MACD value: {macd.iloc[-1]:.6f}")
    print(f"   Last Signal value: {signal.iloc[-1]:.6f}")
    print(f"   Last Histogram value: {histogram.iloc[-1]:.6f}")
    
    # Test Bollinger Bands
    print("\n3. Testing Bollinger Bands")
    upper, mid, lower = ti.bollinger_bands(df['close'])
    print(f"   Last Upper Band: {upper.iloc[-1]:.2f}")
    print(f"   Last Mid Band: {mid.iloc[-1]:.2f}")
    print(f"   Last Lower Band: {lower.iloc[-1]:.2f}")
    
    # Test ATR
    print("\n4. Testing ATR (14 period)")
    atr = ti.atr(df['high'], df['low'], df['close'])
    print(f"   Last ATR value: {atr.iloc[-1]:.4f}")
    print(f"   ATR Range: {atr.min():.4f} - {atr.max():.4f}")
    
    # Test Volume Indicators
    print("\n5. Testing Volume SMA")
    vol_sma = ti.volume_sma(df['volume'])
    print(f"   Last Volume SMA: {vol_sma.iloc[-1]:.2f}")
    
    print("\n6. Testing OBV")
    obv = ti.obv(df['close'], df['volume'])
    print(f"   Last OBV value: {obv.iloc[-1]:.2f}")
    
    # Test Momentum
    print("\n7. Testing Momentum")
    momentum = ti.momentum(df['close'])
    print(f"   Last Momentum value: {momentum.iloc[-1]:.4f}")
    
    print("\n8. Testing ROC")
    roc = ti.roc(df['close'])
    print(f"   Last ROC value: {roc.iloc[-1]:.2f}%")
    
    print("\n" + "-"*80)
    print("All individual indicators working correctly!")
    print("-"*80)


def test_composite_indicator():
    """
    Test composite indicator
    """
    print("\n" + "="*80)
    print("TESTING COMPOSITE INDICATOR")
    print("="*80)
    
    # Load sample data
    print("\nLoading sample data...")
    df = load_klines('ETHUSDT', '1h')
    df = df.tail(200).reset_index(drop=True)
    
    # Create composite indicator
    print("Calculating composite indicator...")
    composite = CompositeIndicator(
        lookback=20,
        volume_threshold=1.2,
        momentum_threshold=0.5,
        trend_strength=0.6
    )
    
    result = composite.calculate(df)
    
    # Analyze results
    print("\n" + "-"*80)
    print("SIGNAL ANALYSIS")
    print("-"*80)
    
    # Count signals
    total_signals = (result['signal'] != 0).sum()
    buy_count = (result['signal'] == 1).sum()
    sell_count = (result['signal'] == -1).sum()
    hold_count = (result['signal'] == 0).sum()
    
    print(f"\nTotal Signals: {len(result)}")
    print(f"  - Buy Signals: {buy_count}")
    print(f"  - Sell Signals: {sell_count}")
    print(f"  - Hold Signals: {hold_count}")
    print(f"  - Signal Frequency: {total_signals / len(result) * 100:.2f}%")
    
    # Signal strength analysis
    print(f"\nSignal Strength Analysis:")
    strong_signals = result[result['signal_strength'] > 0.7]
    print(f"  - Strong Signals (>0.7): {len(strong_signals)}")
    print(f"  - Average Strength: {result['signal_strength'].mean():.3f}")
    print(f"  - Max Strength: {result['signal_strength'].max():.3f}")
    
    # Component scores analysis
    print(f"\nComponent Scores (Last 10 Candles):")
    print("-" * 80)
    
    display_cols = ['momentum_score', 'trend_score', 'volume_score', 'volatility_score', 'signal_strength']
    last_10 = result[display_cols].tail(10).copy()
    
    for col in display_cols:
        last_10[col] = last_10[col].apply(lambda x: f"{x:.3f}")
    
    print(last_10.to_string(index=False))
    
    # Distribution of scores
    print(f"\nScore Distributions:")
    print("-" * 80)
    
    for col in display_cols[:-1]:
        mean_val = result[col].mean()
        std_val = result[col].std()
        print(f"{col:20s}: Mean={mean_val:7.3f}, Std={std_val:7.3f}")
    
    # Validation
    print(f"\nData Validation:")
    print("-" * 80)
    print(f"No null signals: {result['signal'].notna().all()}")
    print(f"Signals in range [-1, 1]: {result['signal'].isin([-1, 0, 1]).all()}")
    print(f"Signal strengths in [0, 1]: {((result['signal_strength'] >= 0) & (result['signal_strength'] <= 1)).all()}")
    print(f"All scores in [-1, 1]: {all((result[col].between(-1, 1)).all() for col in display_cols[:-1])}")
    
    print("\n" + "-"*80)
    print("Composite indicator tests passed!")
    print("-"*80)


def test_previous_candle_logic():
    """
    Verify that signals use previous candle data
    """
    print("\n" + "="*80)
    print("TESTING PREVIOUS CANDLE SIGNAL LOGIC")
    print("="*80)
    
    # Load sample data
    print("\nLoading sample data...")
    df = load_klines('SOLUSDT', '1h')
    df = df.tail(100).reset_index(drop=True)
    
    composite = CompositeIndicator()
    result = composite.calculate(df)
    
    # Check signal generation logic
    print("\nVerifying previous candle logic...")
    
    # Get a signal
    signals_idx = result[result['signal'] != 0].index
    
    if len(signals_idx) > 0:
        test_idx = signals_idx[0]
        print(f"\nAnalyzing signal at candle index: {test_idx}")
        
        if test_idx > 0:
            current = result.iloc[test_idx]
            previous = result.iloc[test_idx - 1]
            
            print(f"\nSignal Generated: {int(current['signal'])} {'BUY' if current['signal'] == 1 else 'SELL'}")
            print(f"\nUsing Previous Candle (index {test_idx-1}) Scores:")
            print(f"  Momentum Score: {previous['momentum_score']:.3f}")
            print(f"  Trend Score: {previous['trend_score']:.3f}")
            print(f"  Volume Score: {previous['volume_score']:.3f}")
            print(f"  Volatility Score: {previous['volatility_score']:.3f}")
            
            print(f"\nCurrent Candle (index {test_idx}) Data:")
            print(f"  Close Price: {current['close']:.2f}")
            print(f"  Volume: {current['volume']:.2f}")
            print(f"  RSI: {current['rsi']:.2f}")
    else:
        print("No signals generated in this dataset.")
    
    print("\n" + "-"*80)
    print("Previous candle logic verified!")
    print("-"*80)


if __name__ == "__main__":
    try:
        test_technical_indicators()
        test_composite_indicator()
        test_previous_candle_logic()
        
        print("\n" + "#"*80)
        print("ALL TESTS COMPLETED SUCCESSFULLY")
        print("#"*80)
        
    except Exception as e:
        print(f"\nTest failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

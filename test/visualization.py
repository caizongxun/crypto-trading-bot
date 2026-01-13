import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.dates import DateFormatter
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from index import calculate_signals


def visualize_signals(symbol: str, timeframe: str = '1h', lookback: int = 200):
    """
    Visualize trading signals with indicators
    
    Args:
        symbol: Trading pair
        timeframe: Timeframe for analysis
        lookback: Number of candles to display
    """
    print(f"Generating visualization for {symbol} ({timeframe})...")
    
    # Get signal data
    result_df = calculate_signals(symbol, timeframe, lookback=lookback)
    
    # Prepare data for plotting
    plot_df = result_df.tail(lookback).reset_index(drop=True).copy()
    plot_df['datetime'] = pd.to_datetime(plot_df['open_time'])
    
    # Create figure with subplots
    fig = plt.figure(figsize=(16, 12))
    
    # 1. Price with Bollinger Bands and SMAs
    ax1 = plt.subplot(4, 1, 1)
    ax1.plot(plot_df.index, plot_df['close'], label='Close Price', linewidth=2, color='black')
    ax1.fill_between(plot_df.index, plot_df['bollinger_upper'], plot_df['bollinger_lower'], 
                      alpha=0.2, color='gray', label='Bollinger Bands')
    ax1.plot(plot_df.index, plot_df['sma_20'], label='SMA 20', linewidth=1.5, alpha=0.7, color='blue')
    ax1.plot(plot_df.index, plot_df['sma_50'], label='SMA 50', linewidth=1.5, alpha=0.7, color='red')
    
    # Add buy/sell signals
    buy_signals = plot_df[plot_df['signal'] == 1]
    sell_signals = plot_df[plot_df['signal'] == -1]
    
    ax1.scatter(buy_signals.index, buy_signals['close'], color='green', marker='^', 
               s=100, label='Buy Signal', zorder=5)
    ax1.scatter(sell_signals.index, sell_signals['close'], color='red', marker='v', 
               s=100, label='Sell Signal', zorder=5)
    
    ax1.set_title(f'{symbol} ({timeframe}) - Price & Bollinger Bands', fontsize=12, fontweight='bold')
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3)
    ax1.set_ylabel('Price')
    
    # 2. Momentum Indicators (RSI, MACD)
    ax2 = plt.subplot(4, 1, 2)
    ax2_twin = ax2.twinx()
    
    # RSI
    ax2.plot(plot_df.index, plot_df['rsi'], label='RSI (14)', color='purple', linewidth=1.5)
    ax2.axhline(y=70, color='gray', linestyle='--', alpha=0.5)
    ax2.axhline(y=30, color='gray', linestyle='--', alpha=0.5)
    ax2.fill_between(plot_df.index, 30, 70, alpha=0.1, color='gray')
    ax2.set_ylabel('RSI', color='purple')
    ax2.set_ylim(0, 100)
    
    # MACD
    colors = ['green' if x > 0 else 'red' for x in plot_df['histogram']]
    ax2_twin.bar(plot_df.index, plot_df['histogram'], label='MACD Histogram', alpha=0.3, color=colors)
    ax2_twin.plot(plot_df.index, plot_df['macd'], label='MACD', color='blue', linewidth=1.5)
    ax2_twin.plot(plot_df.index, plot_df['signal_line'], label='Signal Line', color='orange', linewidth=1.5)
    ax2_twin.set_ylabel('MACD')
    
    ax2.set_title('Momentum Indicators', fontsize=12, fontweight='bold')
    ax2.legend(loc='upper left')
    ax2_twin.legend(loc='upper right')
    ax2.grid(True, alpha=0.3)
    
    # 3. Component Scores
    ax3 = plt.subplot(4, 1, 3)
    ax3.plot(plot_df.index, plot_df['momentum_score'], label='Momentum Score', linewidth=1.5, color='purple')
    ax3.plot(plot_df.index, plot_df['trend_score'], label='Trend Score', linewidth=1.5, color='blue')
    ax3.plot(plot_df.index, plot_df['volume_score'], label='Volume Score', linewidth=1.5, color='green')
    ax3.plot(plot_df.index, plot_df['volatility_score'], label='Volatility Score', linewidth=1.5, color='orange')
    ax3.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax3.fill_between(plot_df.index, 0, 1, alpha=0.1, color='green')
    ax3.fill_between(plot_df.index, -1, 0, alpha=0.1, color='red')
    
    ax3.set_title('Component Signal Scores', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Score (-1 to 1)')
    ax3.set_ylim(-1.2, 1.2)
    ax3.legend(loc='best')
    ax3.grid(True, alpha=0.3)
    
    # 4. Volume Analysis
    ax4 = plt.subplot(4, 1, 4)
    
    # Volume bars
    colors_vol = ['green' if plot_df['close'].iloc[i] >= plot_df['close'].iloc[i-1] else 'red' 
                  for i in range(len(plot_df))]
    ax4.bar(plot_df.index, plot_df['volume'], color=colors_vol, alpha=0.6, label='Volume')
    
    # Volume SMA
    ax4_twin = ax4.twinx()
    ax4_twin.plot(plot_df.index, plot_df['volume_ratio'], label='Volume Ratio', 
                  color='blue', linewidth=2, marker='o', markersize=3)
    ax4_twin.axhline(y=1.0, color='gray', linestyle='--', alpha=0.5)
    ax4_twin.set_ylabel('Volume Ratio', color='blue')
    
    ax4.set_title('Volume Analysis', fontsize=12, fontweight='bold')
    ax4.set_xlabel('Candle Index')
    ax4.set_ylabel('Volume')
    ax4.legend(loc='upper left')
    ax4_twin.legend(loc='upper right')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save figure
    output_path = f'test/output_{symbol}_{timeframe}.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Visualization saved to: {output_path}")
    
    plt.show()
    
    # Summary statistics
    print("\n" + "="*80)
    print("VISUALIZATION SUMMARY")
    print("="*80)
    print(f"Date Range: {plot_df['datetime'].min()} to {plot_df['datetime'].max()}")
    print(f"Price Range: {plot_df['close'].min():.2f} - {plot_df['close'].max():.2f}")
    print(f"Volatility (ATR): {plot_df['atr'].mean():.4f}")
    print(f"Average Volume Ratio: {plot_df['volume_ratio'].mean():.3f}")
    print(f"Signal Win Rate Potential: {(buy_signals.shape[0] + sell_signals.shape[0]) / len(plot_df) * 100:.2f}%")


if __name__ == "__main__":
    symbol = 'BTCUSDT'
    timeframe = '1h'
    
    if len(sys.argv) > 1:
        symbol = sys.argv[1]
    if len(sys.argv) > 2:
        timeframe = sys.argv[2]
    
    visualize_signals(symbol, timeframe)

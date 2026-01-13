import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.indicators import CompositeIndicator, TechnicalIndicators
from index import load_klines


def test_btc_15m_comprehensive():
    """
    BTC 15分鐘級別的完整測試
    """
    print("="*80)
    print("BTC 15分鐘級別 - 綜合指標測試")
    print("="*80)
    
    # 載入數據
    print("\n正在載入數據...")
    df = load_klines('BTCUSDT', '15m')
    df = df.tail(500).reset_index(drop=True)
    
    print(f✓ 數據形狀: {df.shape}")
    print(f✓ 時間知域: {df['open_time'].min()} 到 {df['open_time'].max()}")
    print(f✓ 价的範圍: {df['close'].min():.2f} - {df['close'].max():.2f}")
    
    # 計算綜合指標
    print("\n正在計算綜合指標...")
    indicator = CompositeIndicator(
        lookback=20,
        volume_threshold=1.2,
        momentum_threshold=0.5,
        trend_strength=0.6
    )
    
    result = indicator.calculate(df)
    
    # 詳細綜合數据字序
    print("\n" + "-"*80)
    print("綜合數据分析")
    print("-"*80)
    
    print(f"\n信號統計:")
    print(f"  總 K棒: {len(result)}")
    print(f"  買入信號: {(result['signal'] == 1).sum()}")
    print(f"  賣出信號: {(result['signal'] == -1).sum()}")
    print(f"  持有信號: {(result['signal'] == 0).sum()}")
    print(f"  信號詻率: {(result['signal'] != 0).sum() / len(result) * 100:.2f}%")
    
    # 信號強度分析
    print(f"\n信號強度分析:")
    strong_signals = result[result['signal'] != 0]
    if len(strong_signals) > 0:
        print(f"  平均信號強度: {strong_signals['signal_strength'].mean():.3f}")
        print(f"  最高強度: {strong_signals['signal_strength'].max():.3f}")
        print(f"  最低強度: {strong_signals['signal_strength'].min():.3f}")
    
    # 丰分得分的統計
    print(f"\n四维分量得分:")
    for col in ['momentum_score', 'trend_score', 'volume_score', 'volatility_score']:
        print(f"  {col:20s}: Mean={result[col].mean():7.3f}, Std={result[col].std():7.3f}")
    
    # 最近20根 K棒
    print("\n" + "-"*80)
    print("最近20根 K棒的詳細信息")
    print("-"*80)
    
    display_cols = [
        'open_time', 'close', 'volume',
        'momentum_score', 'trend_score', 'volume_score', 'volatility_score',
        'rsi', 'macd', 'signal', 'signal_strength'
    ]
    
    last_20 = result[display_cols].tail(20).copy()
    
    # 格式化
    for col in ['momentum_score', 'trend_score', 'volume_score', 'volatility_score', 'signal_strength']:
        last_20[col] = last_20[col].apply(lambda x: f"{x:.3f}")
    
    last_20['close'] = last_20['close'].apply(lambda x: f"{x:.2f}")
    last_20['volume'] = last_20['volume'].apply(lambda x: f"{x:.2f}")
    last_20['rsi'] = last_20['rsi'].apply(lambda x: f"{x:.2f}")
    last_20['macd'] = last_20['macd'].apply(lambda x: f"{x:.6f}")
    last_20['signal'] = last_20['signal'].apply(
        lambda x: 'BUY' if x == 1 else ('SELL' if x == -1 else 'HOLD')
    )
    
    print("\n" + last_20.to_string(index=False))
    
    # 最新狀況
    print("\n" + "-"*80)
    print("當前市堍狀況")
    print("-"*80)
    
    latest = result.iloc[-1]
    
    print(f"\n最新收盘價: ${latest['close']:.2f}")
    print(f"RSI (14): {latest['rsi']:.2f}")
    print(f"MACD: {latest['macd']:.6f}")
    print(f"MACD 信號線: {latest['signal_line']:.6f}")
    print(f"MACD 柱状图: {latest['histogram']:.6f}")
    
    print(f"\n分量得分:")
    print(f"  动能得分: {latest['momentum_score']:.3f}")
    print(f"  趋势得分: {latest['trend_score']:.3f}")
    print(f"  成交量得分: {latest['volume_score']:.3f}")
    print(f"  波動率得分: {latest['volatility_score']:.3f}")
    
    print(f"\n最新信號:")
    signal_text = 'BUY' if latest['signal'] == 1 else ('SELL' if latest['signal'] == -1 else 'HOLD')
    print(f"  信號: {signal_text}")
    print(f"  強度: {latest['signal_strength']:.3f}")
    
    # 詳細綜合得分計算
    composite_score = (0.35 * latest['momentum_score'] + 
                      0.35 * latest['trend_score'] + 
                      0.20 * latest['volume_score'] + 
                      0.10 * latest['volatility_score'])
    print(f"\n綜合得分: {composite_score:.3f}")
    print(f"  > 0.4: 强烈看涨")
    print(f"  < -0.4: 强烈看跌")
    print(f"  -0.4 ~ 0.4: 中性")
    
    # 性能指標
    print("\n" + "-"*80)
    print("性能指標")
    print("-"*80)
    
    # 計算簡單勝率
    result['future_return'] = result['close'].pct_change().shift(-1)
    
    buy_signals = result[result['signal'] == 1]
    sell_signals = result[result['signal'] == -1]
    
    if len(buy_signals) > 0:
        buy_wins = (buy_signals['future_return'] > 0).sum()
        buy_rate = buy_wins / len(buy_signals) * 100
        print(f"\n買入信號:")
        print(f"  總數: {len(buy_signals)}")
        print(f"  勝利: {buy_wins}")
        print(f"  勝率: {buy_rate:.2f}%")
        print(f"  平均收益: {buy_signals['future_return'].mean()*100:.3f}%")
    
    if len(sell_signals) > 0:
        sell_wins = (sell_signals['future_return'] < 0).sum()
        sell_rate = sell_wins / len(sell_signals) * 100
        print(f"\n賣出信號:")
        print(f"  總數: {len(sell_signals)}")
        print(f"  勝利: {sell_wins}")
        print(f"  勝率: {sell_rate:.2f}%")
        print(f"  平均收益: {sell_signals['future_return'].mean()*100:.3f}%")
    
    # 整體勝率
    all_signals = result[result['signal'] != 0]
    if len(all_signals) > 0:
        buy_correct = ((all_signals['signal'] == 1) & (all_signals['future_return'] > 0)).sum()
        sell_correct = ((all_signals['signal'] == -1) & (all_signals['future_return'] < 0)).sum()
        total_correct = buy_correct + sell_correct
        overall_rate = total_correct / len(all_signals) * 100
        
        print(f"\n整體性能:")
        print(f"  總信號数: {len(all_signals)}")
        print(f"  正確信號: {total_correct}")
        print(f"  整體勝率: {overall_rate:.2f}%")
    
    print("\n" + "="*80)
    print("✓ BTC 15分鐘 測試完成！")
    print("="*80)
    
    return result


if __name__ == "__main__":
    try:
        result_df = test_btc_15m_comprehensive()
        print("\n✓ 所有測試通過！")
        
    except Exception as e:
        print(f"\n❌ 測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()

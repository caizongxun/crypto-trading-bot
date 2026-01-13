#!/usr/bin/env python3
"""
BTC 15分鐘級別 - 完整執行指令

使用方式:
    python run_btc_15m.py

功能:
1. 自動安裝依賴
2. 加載 BTC 15m 數據
3. 計算組合指標
4. 生成可視化
5. 輸出完整分析報告
"""

import subprocess
import sys
import os

def install_dependencies():
    """
    安裝所有必需的依賴
    移除版本限制以提高相容性
    """
    print("="*80)
    print("正在安裝依賴...")
    print("="*80)
    
    # 移除版本限制，改用可相容的版本
    packages = [
        "pandas",
        "numpy",
        "scikit-learn",
        "xgboost",
        "torch",
        "huggingface-hub",
        "matplotlib",
        "seaborn",
        "pyarrow",
        "tqdm",
        "requests",
        "datasets"
    ]
    
    try:
        # 先升級 pip 本身
        print("\n正在升級 pip...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade", "pip"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # 重新安裝一些核心依賴
        print("正在安裝核心依賴...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade", "--no-cache-dir",
            "setuptools", "wheel"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # 安裝主要依賴
        print("正在安裝主要程式包...")
        for package in packages:
            print(f"  安裝 {package}...", end="", flush=True)
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", "-q", package
                ], stderr=subprocess.DEVNULL)
                print(" 完成")
            except Exception as e:
                print(f" 失敗: {str(e)[:30]}")
                # 继续正常侟渐解决依賴问题
                pass
        
        print("\n依賴安裝完成")
        return True
    except Exception as e:
        print(f"\n依賴安裝处理时出现错誤: {str(e)}")
        print("\n尝试手动安裝:")
        print("pip install pandas numpy scikit-learn xgboost torch huggingface-hub matplotlib seaborn")
        return False

def run_btc_15m_test():
    """
    執行 BTC 15分鐘測試
    """
    print("\n" + "="*80)
    print("執行 BTC 15分鐘級別測試")
    print("="*80)
    
    try:
        from test.btc_15m_test import test_btc_15m_comprehensive
        result_df = test_btc_15m_comprehensive()
        return result_df
    except Exception as e:
        print(f"\n測試執行失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def generate_visualization():
    """
    生成可視化圖表
    """
    print("\n" + "="*80)
    print("生成可視化圖表")
    print("="*80)
    
    try:
        from test.visualization import visualize_signals
        visualize_signals('BTCUSDT', '15m', lookback=200)
        print("\n可視化圖表已生成: test/output_BTCUSDT_15m.png")
        return True
    except Exception as e:
        print(f"\n圖表生成失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def print_summary(result_df):
    """
    輸出執行總結
    """
    if result_df is None:
        return
    
    print("\n" + "="*80)
    print("執行完成 - 最終報告")
    print("="*80)
    
    print(f"\n數據統計:")
    print(f"  總 K 棒數: {len(result_df)}")
    print(f"  時間範圍: {result_df['open_time'].min()} 到 {result_df['open_time'].max()}")
    print(f"  價格範圍: {result_df['close'].min():.2f} - {result_df['close'].max():.2f}")
    
    print(f"\n信號統計:")
    print(f"  買入信號: {(result_df['signal'] == 1).sum()} 個")
    print(f"  賣出信號: {(result_df['signal'] == -1).sum()} 個")
    print(f"  持有信號: {(result_df['signal'] == 0).sum()} 個")
    print(f"  信號頻率: {(result_df['signal'] != 0).sum() / len(result_df) * 100:.2f}%")
    
    strong_signals = result_df[result_df['signal_strength'] > 0.7]
    if len(strong_signals) > 0:
        print(f"\n強信號分析 (強度 > 0.7):")
        print(f"  強信號數量: {len(strong_signals)}")
        print(f"  平均強度: {strong_signals['signal_strength'].mean():.3f}")
    
    latest = result_df.iloc[-1]
    print(f"\n最新狀態:")
    print(f"  最新收盤價: {latest['close']:.2f}")
    print(f"  RSI (14): {latest['rsi']:.2f}")
    print(f"  MACD: {latest['macd']:.6f}")
    signal_text = 'BUY' if latest['signal'] == 1 else ('SELL' if latest['signal'] == -1 else 'HOLD')
    print(f"  最後信號: {signal_text}")
    print(f"  信號強度: {latest['signal_strength']:.3f}")
    
    # 簡單的準確率計算
    result_df['future_return'] = result_df['close'].pct_change().shift(-1)
    buy_signals = result_df[result_df['signal'] == 1]
    sell_signals = result_df[result_df['signal'] == -1]
    
    if len(buy_signals) > 0:
        buy_wins = (buy_signals['future_return'] > 0).sum()
        buy_rate = buy_wins / len(buy_signals) * 100
        print(f"\n買入信號準確率: {buy_rate:.1f}% ({buy_wins}/{len(buy_signals)})")
    
    if len(sell_signals) > 0:
        sell_wins = (sell_signals['future_return'] < 0).sum()
        sell_rate = sell_wins / len(sell_signals) * 100
        print(f"賣出信號準確率: {sell_rate:.1f}% ({sell_wins}/{len(sell_signals)})")
    
    print(f"\n輸出檔案:")
    print(f"  可視化圖表: test/output_BTCUSDT_15m.png")
    print(f"  可視化已儲存，請查看圖表分析")
    
    print("\n" + "="*80)
    print("執行全程完成")
    print("="*80)

def main():
    """
    主執行函數
    """
    print("\n" + "#"*80)
    print("# BTC 15分鐘級別 - 完整執行")
    print("#"*80)
    
    # 步驟 1: 安裝依賴
    if not install_dependencies():
        print("\n無法自動安裝依賴，請手动安裝或检查网络連接")
        return False
    
    # 步驟 2: 執行測試
    result_df = run_btc_15m_test()
    if result_df is None:
        print("\n無法執行測試，程式終止")
        return False
    
    # 步驟 3: 生成可視化
    if not generate_visualization():
        print("\n無法生成圖表")
    
    # 步驟 4: 輸出報告
    print_summary(result_df)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n程式執行成功")
            sys.exit(0)
        else:
            print("\n程式執行失敗")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n程式被使用者中止")
        sys.exit(1)
    except Exception as e:
        print(f"\n意外錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

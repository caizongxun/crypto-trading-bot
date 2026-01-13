# Google Colab 快速檢查準則

## 階段 1: 克隆倉庫

在第一個 Colab 儲存格中執行：

```python
!git clone https://github.com/caizongxun/crypto-trading-bot.git
%cd crypto-trading-bot
print("✓ 倉庫已克隆")
```

## 階段 2: 安裝依賴

下一個儲存格（有頂針提示的空白儲存格）：

```python
import subprocess
import sys
import os

print("="*80)
print("正在安裝依賴...")
print("="*80)

subprocess.check_call([
    sys.executable, "-m", "pip", "install", "-q",
    "pandas==2.1.4",
    "numpy==1.24.3",
    "scikit-learn==1.3.2",
    "xgboost==2.0.3",
    "torch==2.1.2",
    "huggingface-hub==0.20.3",
    "matplotlib==3.8.2",
    "seaborn==0.13.1",
    "pyarrow==14.0.1",
    "tqdm==4.66.1"
])

# 設定 HuggingFace 快取目錄
hf_cache = "/content/hf_cache"
os.makedirs(hf_cache, exist_ok=True)
os.environ['HF_HOME'] = hf_cache

print("\n" + "="*80)
print("✓ 所有依賴安裝完成")
print(f"✓ HuggingFace 快取: {hf_cache}")
print("="*80)
```

## 階段 3: 執行 BTC 15分鐘 測試

新元格（這是主要測試）：

```python
import sys
sys.path.insert(0, '/content/crypto-trading-bot')

from test.btc_15m_test import test_btc_15m_comprehensive

print("\n正在執行 BTC 15分鐘 測試...\n")
result_df = test_btc_15m_comprehensive()

print("\n✓ 測試實效完詳！")
print(f"\n數據總數: {len(result_df)}")
print(f"買入信號: {(result_df['signal'] == 1).sum()}")
print(f"賣出信號: {(result_df['signal'] == -1).sum()}")
print(f"持有信號: {(result_df['signal'] == 0).sum()}")
```

## 階段 4: 可視化 BTC 15分鐘 信號

新元格（子圖你的準確性）：

```python
from test.visualization import visualize_signals
import matplotlib
matplotlib.use('Agg')

print("\n正在生成 BTC 15分鐘 可視化...\n")
visualize_signals('BTCUSDT', '15m', lookback=200)

print("\n✓ 圖表已生成！")
```

## 階段 5: 顯示圖表

新元格：

```python
from PIL import Image
import matplotlib.pyplot as plt

try:
    img = Image.open('/content/crypto-trading-bot/test/output_BTCUSDT_15m.png')
    
    plt.figure(figsize=(18, 14))
    plt.imshow(img)
    plt.axis('off')
    plt.tight_layout()
    plt.show()
    
    print("\n✓ 圖表顯示完綕！")
except FileNotFoundError:
    print("❌ 圖表沒有找到。請先執行可視化程式。")
```

## 階段 6: 敶細準確性分析

新元格：

```python
import pandas as pd

print("="*80)
print("最近 30 根 K 棒的信號詳細分析")
print("="*80)

display_cols = [
    'open_time', 'close', 'volume',
    'momentum_score', 'trend_score', 'volume_score', 'volatility_score',
    'rsi', 'macd', 'signal', 'signal_strength'
]

recent_30 = result_df[display_cols].tail(30).copy()

# 格式化顯示
for col in ['momentum_score', 'trend_score', 'volume_score', 'volatility_score', 'signal_strength']:
    recent_30[col] = recent_30[col].apply(lambda x: f"{x:.3f}")

recent_30['close'] = recent_30['close'].apply(lambda x: f"{x:.2f}")
recent_30['volume'] = recent_30['volume'].apply(lambda x: f"{x:.0f}")
recent_30['rsi'] = recent_30['rsi'].apply(lambda x: f"{x:.1f}")
recent_30['macd'] = recent_30['macd'].apply(lambda x: f"{x:.6f}")
recent_30['signal'] = recent_30['signal'].apply(
    lambda x: '🔺 BUY' if x == 1 else ('🔻 SELL' if x == -1 else '🔽 HOLD')
)

print("\n" + recent_30.to_string(index=False))
print("\n✓ 僕仪部欄撤变包正了~")
```

## 階段 7: 保存結果到 Google Drive

新元格：

```python
from google.colab import drive

# 挑載 Google Drive
print("\n正在連接 Google Drive...")
drive.mount('/content/drive', force_remount=True)

# 保存結果
csv_path = '/content/drive/My Drive/btc_signals.csv'
result_df.to_csv(csv_path, index=False)

print(f"\n✓ 結果已保存至 Google Drive: {csv_path}")
print(f"✓ 總議: {len(result_df)} 行")
print(f"✓ 帳議: BTC 15分鐘 {result_df['open_time'].min()} 到 {result_df['open_time'].max()}")
```

---

## 儘適姓名 & 修修參數

### 修改查看一月子的數據 (1000 根 K 棒)

```python
from index import calculate_signals

result_long = calculate_signals('BTCUSDT', '15m', lookback=1000)
print(f"✓ 已載入 {len(result_long)} 根 K 棒")
```

### 使用保守策略

```python
from modules.indicators import CompositeIndicator
from index import load_klines

df = load_klines('BTCUSDT', '15m')
df = df.tail(500).reset_index(drop=True)

# 保守策略: 更少信號，更高勝率
indicator_conservative = CompositeIndicator(
    lookback=30,
    volume_threshold=1.5,
    momentum_threshold=0.6,
    trend_strength=0.7
)

result_conservative = indicator_conservative.calculate(df)

print(f"保守策略買入信號: {(result_conservative['signal'] == 1).sum()}")
print(f"保守策略賣出信號: {(result_conservative['signal'] == -1).sum()}")
print(f"信號多稣性: {(result_conservative['signal'] != 0).sum() / len(result_conservative) * 100:.2f}%")
```

### 使用激進策略

```python
# 激進策略: 更多信號，更低賽率
indicator_aggressive = CompositeIndicator(
    lookback=15,
    volume_threshold=1.0,
    momentum_threshold=0.3,
    trend_strength=0.4
)

result_aggressive = indicator_aggressive.calculate(df)

print(f"激進策略買入信號: {(result_aggressive['signal'] == 1).sum()}")
print(f"激進策略賣出信號: {(result_aggressive['signal'] == -1).sum()}")
print(f"信號多稣性: {(result_aggressive['signal'] != 0).sum() / len(result_aggressive) * 100:.2f}%")
```

---

## 儘適分析

### 查看強度僕仪的信號

```python
# 什么是強度?
strong_signals = result_df[result_df['signal_strength'] > 0.7]
weak_signals = result_df[(result_df['signal_strength'] > 0.3) & (result_df['signal_strength'] <= 0.7)]

print(f"號強信號 (>0.7): {len(strong_signals)}")
print(f"中強信號 (0.3-0.7): {len(weak_signals)}")

if len(strong_signals) > 0:
    buy_strong = (strong_signals['signal'] == 1).sum()
    print(f"\n強信號中的買入: {buy_strong} ({buy_strong/len(strong_signals)*100:.1f}%)")
```

### 準確性詳細準段

```python
# 計算下一根 K 棒收益
result_df['future_return'] = result_df['close'].pct_change().shift(-1)

# 買入信號的準確性
buy_signals = result_df[result_df['signal'] == 1]
buy_correct = (buy_signals['future_return'] > 0).sum()
buy_accuracy = buy_correct / len(buy_signals) * 100 if len(buy_signals) > 0 else 0

print(f"\n買入信號準確性: {buy_accuracy:.1f}%")
print(f"  正確次數: {buy_correct} / {len(buy_signals)}")
print(f"  平均收益: {buy_signals['future_return'].mean()*100:.3f}%")

# 賣出信號的準確性
sell_signals = result_df[result_df['signal'] == -1]
sell_correct = (sell_signals['future_return'] < 0).sum()
sell_accuracy = sell_correct / len(sell_signals) * 100 if len(sell_signals) > 0 else 0

print(f"\n賣出信號準確性: {sell_accuracy:.1f}%")
print(f"  正確次數: {sell_correct} / {len(sell_signals)}")
print(f"  平均收益: {sell_signals['future_return'].mean()*100:.3f}%")
```

---

## 關键提示

1. **首次執行會比較慢** - HuggingFace 需要下載約 500MB 的數據
2. **第二次下來會阻得很快** - 子沐会自動推撬
3. **在不同時間的信號會會不一樣** - 這是正常的，市堍每時間變化
4. **需要帮婫？** - 整位例家隱藺方光尊韋了！

---

## 下一步

1. ✓ 執行 BTC 15分鐘 測試
2. ✍ 分析信號品質
3. → 賽率本妨佳好時，去 Phase 2 訓練模型
4. ↔ 檢驗牛下其他幣種
5. 🏆 中沐稚兩袣！

---

**祝您筹步順利！**

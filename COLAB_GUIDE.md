# Google Colab 執行指南

## 快速開始 (5分鐘)

### 步驟1：開啟新的 Colab 筆記本

1. 前往 [Google Colab](https://colab.research.google.com/)
2. 新增筆記本 (New Notebook)
3. 點擊「檔案」→「從 GitHub 載入」
4. 貼上專案 URL: `https://github.com/caizongxun/crypto-trading-bot`

或者直接在第一個儲存格執行：

```python
!git clone https://github.com/caizongxun/crypto-trading-bot.git
%cd crypto-trading-bot
```

### 步驟2：初始化環境

在 Colab 的第二個儲存格執行：

```python
import subprocess
import sys

# 安裝依賴
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q",
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

print("✓ 依賴安裝完成")
```

### 步驟3：執行 BTC 15分鐘測試

```python
import sys
sys.path.insert(0, '/content/crypto-trading-bot')

from index import calculate_signals

# 測試 BTC 15分鐘級別
result_df = calculate_signals('BTCUSDT', '15m', lookback=500)
```

### 步驟4：可視化分析

```python
from test.visualization import visualize_signals

# 生成分析圖表
visualize_signals('BTCUSDT', '15m', lookback=200)
```

---

## 完整 Colab 筆記本範例

### 儲存格1：克隆倉庫

```python
!git clone https://github.com/caizongxun/crypto-trading-bot.git
%cd crypto-trading-bot
!ls -la
```

### 儲存格2：安裝依賴

```python
import subprocess
import sys
import os

print("正在安裝依賴...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q",
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

print("\n✓ 所有依賴安裝完成！")
print(f"✓ HuggingFace 快取目錄: {hf_cache}")
```

### 儲存格3：載入模組並執行指標測試

```python
import sys
sys.path.insert(0, '/content/crypto-trading-bot')

from index import calculate_signals

print("="*80)
print("BTC 15分鐘級別 - 指標測試")
print("="*80)

# 執行信號計算
result_df = calculate_signals('BTCUSDT', '15m', lookback=500)

print("\n✓ 信號計算完成")
print(f"總 K棒數: {len(result_df)}")
print(f"買入信號: {(result_df['signal'] == 1).sum()}")
print(f"賣出信號: {(result_df['signal'] == -1).sum()}")
print(f"平均信號強度: {result_df[result_df['signal'] != 0]['signal_strength'].mean():.3f}")
```

### 儲存格4：可視化分析

```python
from test.visualization import visualize_signals
import matplotlib
matplotlib.use('Agg')  # 在 Colab 中使用非互動式後端

print("正在生成視覺化圖表...")
visualize_signals('BTCUSDT', '15m', lookback=200)
print("\n✓ 圖表已保存至 test/output_BTCUSDT_15m.png")
```

### 儲存格5：顯示圖表

```python
from PIL import Image
import matplotlib.pyplot as plt

# 載入並顯示圖表
img = Image.open('/content/crypto-trading-bot/test/output_BTCUSDT_15m.png')
plt.figure(figsize=(16, 12))
plt.imshow(img)
plt.axis('off')
plt.tight_layout()
plt.show()
```

### 儲存格6：詳細指標分析

```python
import pandas as pd

print("="*80)
print("最近 30 根 K 棒的詳細指標")
print("="*80)

# 顯示最近 30 根 K 棒的關鍵指標
display_cols = [
    'open_time', 'close', 'volume',
    'momentum_score', 'trend_score', 'volume_score', 'volatility_score',
    'rsi', 'macd', 'signal',
    'signal_strength'
]

latest_30 = result_df[display_cols].tail(30).copy()

# 格式化顯示
for col in ['momentum_score', 'trend_score', 'volume_score', 'volatility_score', 'signal_strength']:
    latest_30[col] = latest_30[col].apply(lambda x: f"{x:.3f}")

for col in ['close', 'volume']:
    latest_30[col] = latest_30[col].apply(lambda x: f"{x:.2f}")

latest_30['rsi'] = latest_30['rsi'].apply(lambda x: f"{x:.2f}")
latest_30['macd'] = latest_30['macd'].apply(lambda x: f"{x:.6f}")
latest_30['signal'] = latest_30['signal'].apply(
    lambda x: 'BUY' if x == 1 else ('SELL' if x == -1 else 'HOLD')
)

print(latest_30.to_string(index=False))
```

---

## 常見問題

### Q1: 如何定期執行指標計算？

**答:** 使用 Colab 的定時執行功能（Colab Pro）或將筆記本保存後定期手動運行。

```python
import time
from datetime import datetime

# 定期檢查信號
for i in range(24):  # 運行 24 小時
    current_time = datetime.now()
    print(f"\n[{current_time}] 檢查信號...")
    
    result_df = calculate_signals('BTCUSDT', '15m', lookback=500)
    latest = result_df.iloc[-1]
    
    if latest['signal'] == 1:
        print(f"⚠️ 買入信號! 強度: {latest['signal_strength']:.3f}")
    elif latest['signal'] == -1:
        print(f"⚠️ 賣出信號! 強度: {latest['signal_strength']:.3f}")
    else:
        print("保持持有")
    
    time.sleep(3600)  # 每小時檢查一次
```

### Q2: 如何保存結果？

**答:** 使用 Google Drive 或下載到本地：

```python
# 方法1：保存到 Google Drive
from google.colab import drive
drive.mount('/content/drive')

result_df.to_csv('/content/drive/My Drive/btc_signals.csv', index=False)

# 方法2：下載到本地
from google.colab import files
result_df.to_csv('btc_signals.csv', index=False)
files.download('btc_signals.csv')
```

### Q3: 為什麼下載速度很慢？

**答:** HuggingFace 數據集較大。可以在本地先下載一次，然後在 Google Drive 中快取。

```python
# 首次運行會下載，之後會使用快取
import os
os.environ['HF_HOME'] = '/content/hf_cache'
```

### Q4: 可以修改指標參數嗎？

**答:** 當然可以！

```python
from modules.indicators import CompositeIndicator

# 保守策略
conservative = CompositeIndicator(
    lookback=30,
    volume_threshold=1.5,
    momentum_threshold=0.6,
    trend_strength=0.7
)

# 激進策略
aggressive = CompositeIndicator(
    lookback=15,
    volume_threshold=1.0,
    momentum_threshold=0.3,
    trend_strength=0.4
)

result_conservative = conservative.calculate(df)
result_aggressive = aggressive.calculate(df)

print(f"保守策略買入信號: {(result_conservative['signal'] == 1).sum()}")
print(f"激進策略買入信號: {(result_aggressive['signal'] == 1).sum()}")
```

### Q5: 如何進行回測？

**答:** 在 Phase 2 會實現回測框架。現在可以手動分析：

```python
# 計算簡單的勝率
result_df['future_return'] = result_df['close'].pct_change().shift(-1)

# 買入後的收益
buy_signals = result_df[result_df['signal'] == 1].copy()
buy_signals['return'] = buy_signals['future_return']

win_count = (buy_signals['return'] > 0).sum()
win_rate = win_count / len(buy_signals) * 100 if len(buy_signals) > 0 else 0

print(f"買入信號數: {len(buy_signals)}")
print(f"勝率: {win_rate:.2f}%")
print(f"平均收益: {buy_signals['return'].mean()*100:.3f}%")
```

---

## Colab 優勢

✓ **免費使用** - 無需購買計算資源
✓ **高速網絡** - 下載 HuggingFace 數據集快速
✓ **GPU 支持** - 可選用 GPU 加速（Colab Pro）
✓ **內置可視化** - 直接顯示圖表
✓ **易於分享** - 可與他人共享筆記本連結
✓ **自動保存** - 自動保存至 Google Drive

---

## 下一步

1. **運行指標測試** - 確認 BTC 15分鐘級別信號
2. **分析信號品質** - 檢查信號強度和準確率
3. **優化參數** - 調整指標參數以改進信號
4. **準備 Phase 2** - 收集數據用於模型訓練
5. **擴展至其他幣種** - 驗證後套用到其他交易對

---

## 聯繫與支持

如有任何問題或建議，歡迎提出 GitHub Issue 或直接討論。

**祝您分析愉快！**

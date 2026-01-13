# ML 模型優化分析 - 真信號識別

## 當前問題診斷

### True Signal (真信號) 識別問題

```
當前性能:
  Precision: 0.4719 (47%)   ← 說是真信號時只有47%是對的
  Recall: 0.2069 (21%)      ← 真實的真信號中只能抓到21%
  F1-Score: 0.2876          ← 綜合分數很低

問題:
  ❌ 模型難以識別賺錢的信號
  ❌ 漏掉了 79% 的真實好機會
  ❌ 說是真信號時錯誤率高達 53%
```

### False Signal (假信號) 識別很好

```
當前性能:
  Precision: 0.5685 (57%)
  Recall: 0.8186 (82%)
  F1-Score: 0.6710

✓ 模型很擅長識別虧錢的信號
✓ 能抓到 82% 的假信號
✓ 避免虧損的能力強
```

### 根本原因分析

```
1. 數據不平衡
   真信號: 57,214 個 (43.8%)
   假信號: 73,326 個 (56.2%)
   → 假信號多 28%，模型偏向識別假信號

2. 特徵分離度差
   真信號的特徵可能與假信號特徵重疊較多
   → 模型難以找到清晰的決策邊界

3. 標籤定義問題
   當前標籤: 3 根 K 棒內賺 0.05% 就是真信號
   → 門檻可能太低，造成標籤噪音多

4. 類別權重不平衡
   訓練時沒有調整類別權重
   → 模型自動偏向多數類 (假信號)
```

---

## 優化策略 (3 個層次)

### Strategy 1: 調整類別權重 (快速)

**原理:** 告訴模型「真信號比較重要」

```python
# 當前: 沒有調整權重
model = xgb.XGBClassifier()

# 優化後: 加入類別權重
model = xgb.XGBClassifier(
    scale_pos_weight=1.28  # 假信號數 / 真信號數 = 73,326 / 57,214
)
```

**預期效果:**
- True Signal Recall: 21% → 40-50%
- True Signal Precision: 47% → 35-40% (降低是正常的)
- Overall Accuracy: 55% → 52-54% (略微下降但結構改善)

**執行時間:** 10 分鐘

---

### Strategy 2: 調整利潤門檻 (中等)

**原理:** 重新定義什麼是「真信號」

```python
# 當前: --profit-threshold 0.0005 (0.05%)
python train_ml_classifier.py --profit-threshold 0.001  # 提高到 0.1%

# 或更激進:
python train_ml_classifier.py --profit-threshold 0.002  # 提高到 0.2%
```

**效果分析:**

提高利潤門檻後:
- 真信號數量減少 (只算大獲利的)
- 假信號數量可能增加
- 真信號質量提升 (都是大獲利的)
- 模型專注於「高品質真信號」

**預期效果:**
- True Signal Precision: 47% → 55-65%
- True Signal Recall: 21% → 15-20% (會下降)
- 但保留下來的真信號質量更好

**執行時間:** 15 分鐘 (需要重新訓練)

---

### Strategy 3: 特徵工程優化 (深度)

**原理:** 添加更好的特徵來分離真假信號

#### 新增特徵 1: 信號強度加權

```python
# 當前: 只有二元信號 (BUY/SELL/NONE)
# 新增: 信號強度評分

signal_strength = (
    rsi_extreme * 0.25 +        # RSI 極值權重
    momentum_direction * 0.25 +  # 動量方向
    trend_alignment * 0.25 +     # 與趨勢對齊
    volume_confirmation * 0.25   # 成交量確認
)

# 只有 signal_strength > 0.6 才算有效信號
```

#### 新增特徵 2: 市場狀態

```python
# 當前: 沒有市場狀態識別
# 新增: 識別當前市場處於何種狀態

market_state = {
    'trending_up': trend_score > 0.5,
    'trending_down': trend_score < -0.5,
    'ranging': -0.5 <= trend_score <= 0.5,
    'volatile': volatility_score > 0.7,
    'calm': volatility_score < 0.3
}

# 真信號在順趨勢時更可靠
# 在震盪時不可靠
```

#### 新增特徵 3: 信號歷史

```python
# 當前: 每個信號獨立評估
# 新增: 追蹤信號序列

consecutive_same_signal = 3  # 連續 3 個 BUY 信號
signal_reversal_count = 5    # 過去 5 個反轉了 5 次

# 連續信號表示確信度高
# 頻繁反轉表示不確信
```

#### 新增特徵 4: 相對表現

```python
# 當前: 只看絕對指標值
# 新增: 看 vs 歷史的相對強度

rsi_percentile = percentile_rank(rsi, last_100_rsi)  # 0-100
volume_percentile = percentile_rank(volume, last_100_volume)
volatility_percentile = percentile_rank(volatility, last_100_volatility)

# 極端值往往更可靠
```

**預期效果:**
- True Signal Recall: 21% → 50-60%
- True Signal Precision: 47% → 55-70%
- Overall Accuracy: 55% → 62-68%

**執行時間:** 2-4 小時 (需要編寫新特徵)

---

## 立即實施方案 (最快見效)

### Option A: 快速優化 (15 分鐘) - 推薦先試

使用更高的利潤門檻重新訓練:

```bash
# 原版 (當前)
python train_ml_classifier.py --profit-threshold 0.0005

# 優化版本 1
python train_ml_classifier.py --profit-threshold 0.001

# 優化版本 2
python train_ml_classifier.py --profit-threshold 0.002

# 對比三個版本的性能
```

**預期結果:**
- 版本1: Precision ↑ Recall ↓
- 版本2: Precision ↑↑ Recall ↓↓

---

## 推薦行動方案

### 立即開始 (選一個):

**方案1 (推薦): 快速測試 - 30 分鐘**
```bash
python optimize_model.py --strategy threshold
```

這會自動測試 5 個不同的利潤門檻版本。

---

## 下一步

準備好開始嗎？

執行: `python optimize_model.py --strategy threshold`

或按照 OPTIMIZATION_QUICK_START.md 的詳細步驟進行。
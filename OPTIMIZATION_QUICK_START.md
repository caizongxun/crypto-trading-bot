# 模型優化 - 快速開始

## 目標

優化模型的真信號識別能力

```
當前問題:
  True Signal Recall: 21% (太低)
  True Signal Precision: 47%

目標:
  True Signal Recall: > 50% (能抓到一半以上)
  True Signal Precision: > 55% (品質更好)
  Overall Accuracy: > 58% (保持整體性能)
```

---

## 三個優化策略 (選一個)

### 策略 1: 利潤門檻調整 ⭐ 推薦先試

**原理:** 提高對「真信號」的定義標準

當前: 3 根 K 棒內賺 0.05% 就算真信號
優化: 改成 3 根 K 棒內賺 0.1-0.2% 才算真信號

**時間:** 15 分鐘
**難度:** ⭐ 最簡単

執行:
```bash
cd /content/crypto-trading-bot

# 快速測試 (5 個版本)
python optimize_model.py --strategy threshold

# 或手動測試
python train_ml_classifier.py --lookback 5000 --profit-threshold 0.0005  # 原版
python train_ml_classifier.py --lookback 5000 --profit-threshold 0.001   # 版本1
python train_ml_classifier.py --lookback 5000 --profit-threshold 0.002   # 版本2
```

預期結果:
- True Signal Precision: 47% → 55-65% ✓
- True Signal Recall: 21% → 15-20% (會下降)
- 但真信號質量有確實提升

---

### 策略 2: 類別權重調整

**原理:** 告訴模型「真信號比較重要」

當前: 模型平等對待真假信號
優化: 告訴模型真信號權重 1.5-3x

**時間:** 1 小時
**難度:** ⭐⭐ 中等

執行:
```bash
# 步驟1: 修改 ml_classifier/model_training.py
# 步驟2: 修改 train_ml_classifier.py
# 步驟3: 執行測試
python optimize_model.py --strategy weight
```

預期結果:
- True Signal Recall: 21% → 40-50% ✓
- True Signal Precision: 47% → 35-40% (會下降)
- Overall Accuracy: 55% → 52-54% (略下降但可接受)

---

### 策略 3: 特徵工程 (深度優化)

**原理:** 添加更好的特徵來區分真假信號

新特徵:
- Signal Strength (信號強度評分)
- Market Regime (市場狀態)
- Signal Confirmation (確認信號)
- Relative Strength (相對強度)
- Recent Win Rate (最近勝率)

**時間:** 4 小時
**難度:** ⭐⭐⭐ 最複雜

預期結果:
- True Signal Recall: 21% → 50-60% ✓✓
- True Signal Precision: 47% → 55-70% ✓✓
- Overall Accuracy: 55% → 62-68% ✓✓

---

## 推薦執行順序

### Day 1: 快速測試 (30 分鐘)

```bash
cd /content/crypto-trading-bot
git pull origin main

# 執行策略1: 測試利潤門檻
python optimize_model.py --strategy threshold

# 查看結果
python -m json.tool optimization_results_threshold_*.json
```

根據結果:
- 如果 Precision ↑ 連輅 → 使用新門檻
- 如果效果有限 → 進入 Day 2

### Day 2: 類別權重 (1.5 小時)

如果 Day 1 效果不佳:

```bash
# 1. 修改 ml_classifier/model_training.py (30 分鐘)
#    添加 scale_pos_weight 參數

# 2. 修改 train_ml_classifier.py (15 分鐘)
#    添加 CLI 參數支持

# 3. 執行優化 (45 分鐘)
python optimize_model.py --strategy weight
```

---

## 現在就開始 - 30 分鐘快速版

### Step 1: 進入策录
```bash
cd /content/crypto-trading-bot
```

### Step 2: 更新代碼
```bash
git pull origin main
```

### Step 3: 執行優化
```bash
python optimize_model.py --strategy threshold
```

這會自動:
- 測試 5 個不同利潤門檻
- 訓練 5 個模型
- 對比結果
- 產生報告

### Step 4: 查看結果
```bash
python -m json.tool optimization_results_threshold_*.json
```

### Step 5: 決策

根據輸出結果：

選擇:
- **Accuracy 最高的版本** → 使用該利潤門檻重新訓練
- **如果都不理想** → 進入策略 2

---

## 一折人寶寶手冊

如果要實施策略 2 (類別權重):

### File: `ml_classifier/model_training.py`

找到這一行:
```python
def train_signal_classifier(labeled_df, feature_columns, test_size=0.3):
```

改成:
```python
def train_signal_classifier(
    labeled_df,
    feature_columns,
    test_size=0.3,
    scale_pos_weight=None,  # ← 新增
):
```

找到這一行:
```python
model = xgb.XGBClassifier(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    random_state=42,
)
```

改成:
```python
# 計算類別權重
if scale_pos_weight is None:
    neg_count = (y_train == 0).sum()
    pos_count = (y_train == 1).sum()
    scale_pos_weight = neg_count / pos_count

model = xgb.XGBClassifier(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    scale_pos_weight=scale_pos_weight,  # ← 新增
    random_state=42,
)
```

### File: `train_ml_classifier.py`

找到:
```python
parser.add_argument(
    "--output-dir",
    ...
)
```

之後添加:
```python
parser.add_argument(
    "--scale-pos-weight",
    type=float,
    default=None,
    help="Class weight for true signals (default: auto)"
)
```

---

## 推薦時間表

| 階段 | 任務 | 時間 | 狀態 |
|------|------|------|------|
| 測試 | 利潤門檻優化 | 30 分鐘 | ⏳ 現在 |
| 決策 | 選擇最佳版本 | 10 分鐘 | ⏳ |
| 實施1 | 類別權重 (可選) | 1 小時 | ⏳ |
| 實施2 | 特徵優化 (可選) | 4 小時 | ⏳ |
| 驗證 | 回測測試 | 1 小時 | ⏳ |
| **總計** | | **6-7 小時** | |

---

## 成功指標

### 阶段1 成功 (利潤門檻)
✓ True Signal Precision > 55%
✓ Overall Accuracy > 52%

### 阶段2 成功 (類別權重)
✓ True Signal Recall > 40%
✓ True Signal Precision > 45%
✓ Overall Accuracy > 53%

### 阶段3 成功 (特徵優化)
✓ True Signal Recall > 55%
✓ True Signal Precision > 60%
✓ Overall Accuracy > 62%

---

## 準備好了？

執行這個命令開始:

```bash
cd /content/crypto-trading-bot && python optimize_model.py --strategy threshold
```

然後等待 30 分鐘，看結果！

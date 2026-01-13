# 组合指标系统设计说明

## 概述

本项目使用创新的组合指标系统，结合**成交量、动能、趋势和波动率**四个维度，生成高质量的交易信号。

该系统的核心特性：
- 基于**前一根K棒数据**进行信号生成（避免未来数据泄露）
- 多指标融合（RSI, MACD, 布林线, ATR, 成交量, OBV等）
- 信号强度评估（0-1分数，可信度指标）
- 可定制化参数调整

---

## 指标架构

### 1. 基础技术指标 (`TechnicalIndicators`)

提供原始的技术指标计算：

| 指标 | 用途 | 参数 |
|------|------|------|
| **RSI** | 超买超卖判断 | period=14 |
| **MACD** | 趋势和动能 | fast=12, slow=26, signal=9 |
| **布林线** | 波动率和支撑阻力 | period=20, std=2 |
| **ATR** | 真实波动范围 | period=14 |
| **OBV** | 成交量趋势 | cumulative |
| **Momentum** | 价格动能 | period=10 |
| **ROC** | 变化率 | period=12 |
| **Volume SMA** | 成交量均值 | period=20 |

---

## 组合指标系统 (`CompositeIndicator`)

### 工作流程

```
1. 计算基础指标
   ↓
2. 分别计算四个分量得分
   ├─ 动能得分 (Momentum Score)
   ├─ 趋势得分 (Trend Score)
   ├─ 成交量得分 (Volume Score)
   └─ 波动率得分 (Volatility Score)
   ↓
3. 复合加权求和
   ↓
4. 基于前一根K棒生成信号
   ↓
5. 计算信号强度
```

---

## 四个分量得分详解

### 1. 动能得分 (Momentum Score) - 权重 35%

**计算逻辑：**
```
Momentum Score = 0.35×RSI信号 + 0.35×MACD信号 + 0.20×Momentum + 0.10×ROC
```

**分量说明：**
- **RSI信号**：(RSI - 50) / 50，标准化到[-1, 1]
  - RSI > 70：正向，接近+1
  - RSI < 30：反向，接近-1
  - RSI = 50：中性，0

- **MACD信号**：柱状图的方向和大小
  - 正柱状图 & 增长：强看涨
  - 负柱状图 & 缩小：强看跌

- **Momentum**：当前价格 vs 10根K棒前
  - 正值：上升趋势
  - 负值：下降趋势

- **ROC**：12根K棒的变化率
  - 正百分比：加速上升
  - 负百分比：加速下降

**何时有效：**
- RSI离极端值（>70或<30）且MACD柱状图扩大
- 多个动能指标同向时信号最强

---

### 2. 趋势得分 (Trend Score) - 权重 35%

**计算逻辑：**
```
Trend Score = 0.40×价格相对SMA20 + 0.30×价格相对布林下轨 + 0.30×SMA对齐
```

**分量说明：**

- **价格相对SMA20**：(Close - SMA20) / SMA20
  - 价格 > SMA20：上升趋势
  - 价格 < SMA20：下降趋势

- **价格相对布林下轨**：(Close - BB Lower) / BB Mid
  - 接近下轨：底部机会
  - 接近上轨：顶部警告

- **SMA对齐**：sign(SMA20 - SMA50)
  - SMA20 > SMA50：强上升趋势
  - SMA20 < SMA50：强下降趋势
  - 交叉点：趋势转折

**何时有效：**
- 价格刚刚突破SMA时（新趋势开始）
- SMA已经排列良好（SMA20 > SMA50 > SMA100）
- 价格在布林线上升/下降通道内

---

### 3. 成交量得分 (Volume Score) - 权重 20%

**计算逻辑：**
```
Volume Score = 0.60×成交量激增 + 0.40×OBV趋势
```

**分量说明：**

- **成交量激增**：log(Volume / AvgVolume) / log(3)
  - Volume = 3×平均值：score = +1
  - Volume = 1/3×平均值：score = -1
  - 成交量倍增表示强势确认

- **OBV趋势**：sign(OBV - OBV SMA)
  - OBV上升：看多力量
  - OBV下降：看空力量
  - 与价格背离：警告信号

**何时有效：**
- 买入信号伴随成交量激增（+1.5倍以上）
- 卖出信号同时OBV趋势向下
- 缺乏成交量的信号可靠性降低

---

### 4. 波动率得分 (Volatility Score) - 权重 10%

**计算逻辑：**
```
Volatility Score = 0.50×(ATR相对值) + 0.50×(布林宽度)
```

**分量说明：**

- **ATR相对值**：ATR / Close（标准化）
  - 高波动：更大的盈利机会
  - 低波动：更稳定但机会少

- **布林宽度**：(BB Upper - BB Lower) / BB Mid
  - 宽度>10%：高波动环境
  - 宽度<5%：低波动环境

**何时有效：**
- 中等波动率最佳（5%-10%）
- 极低波动率后的突破（压低-放量）
- 极高波动率需谨慎（可能是假突破）

---

## 信号生成规则

### 买入信号 (Signal = 1)

**条件（必须全部满足）：**
```
1. 复合得分 > 0.4        (强烈看涨)
2. 成交量得分 > 0.2       (成交量确认)
3. 动能得分 > 0.2         (动能指标看好)
4. 趋势得分 > -0.3        (趋势不反对)
```

**实例：**
- RSI从30反弹到45 + MACD柱状图由负变正 + 成交量突增
- 价格突破SMA20 + OBV创新高 + ATR扩大

### 卖出信号 (Signal = -1)

**条件（必须全部满足）：**
```
1. 复合得分 < -0.4       (强烈看跌)
2. 成交量得分 > 0.2       (成交量确认)
3. 动能得分 < -0.2        (动能指标看空)
4. 趋势得分 < 0.3         (趋势不支持)
```

**实例：**
- RSI从70回落到55 + MACD柱状图由正变负 + 成交量突增
- 价格跌破SMA20 + OBV创新低 + ATR扩大

### 持有信号 (Signal = 0)

- 不满足买入或卖出条件
- 允许持有已有头寸
- 等待更清晰的信号

---

## 关键特性：前一根K棒数据

### 为什么使用前一根K棒？

在实时交易中，当前K棒仍在形成中。价格不断变动，导致指标值持续更新。

**问题：**
```
当前K棒数据变化
├─ 10:05 第1秒：Close=45000, RSI=65
├─ 10:05 第30秒：Close=45050, RSI=66  <-- 模型建议买入
├─ 10:05 第59秒：Close=44900, RSI=62  <-- 信号已失效！
└─ 10:06 K棒开始：Close已定，无法回到之前的信号
```

**解决方案：** 使用前一根完整的K棒数据
```
10:05 - 10:06 K棒（已完成）
├─ 所有指标基于完整数据计算
├─ 10:06 K棒开始时生成信号
├─ 交易执行于 10:06
└─ 避免了未来数据泄露
```

### 实现细节

在代码中使用 `.shift(1)` 将所有指标后移一根K棒：
```python
momentum_prev = df['momentum_score'].shift(1)  # 前一根K棒
trend_prev = df['trend_score'].shift(1)
volume_prev = df['volume_score'].shift(1)

# 基于前一根K棒生成信号
composite = (0.35*momentum_prev + 0.35*trend_prev + 0.20*volume_prev + 0.10*volatility_prev)
```

---

## 信号强度评估

**信号强度公式：**
```
Strength = agreement × volume_boost

where:
  agreement = (|momentum_score_prev| + |trend_score_prev|) / 2
  volume_boost = (volume_score_prev + 1) / 2
```

**强度范围：** 0 到 1

- **0.7-1.0**：非常可靠，多个指标同向
- **0.5-0.7**：中等可靠，需要谨慎
- **<0.5**：信号微弱，建议等待

---

## 参数调整指南

### 保守策略（低频交易）
```python
CompositeIndicator(
    lookback=30,              # 更长的历史
    volume_threshold=1.5,     # 更高的成交量要求
    momentum_threshold=0.6,   # 更强的动能
    trend_strength=0.7        # 更强的趋势要求
)
```

### 激进策略（高频交易）
```python
CompositeIndicator(
    lookback=15,              # 更短的历史
    volume_threshold=1.0,     # 较低的成交量要求
    momentum_threshold=0.3,   # 较弱的动能
    trend_strength=0.4        # 较弱的趋势要求
)
```

### 平衡策略（默认）
```python
CompositeIndicator(
    lookback=20,
    volume_threshold=1.2,
    momentum_threshold=0.5,
    trend_strength=0.6
)
```

---

## 使用示例

### 基本使用
```python
from modules.indicators import CompositeIndicator
from index import load_klines

# 加载数据
df = load_klines('BTCUSDT', '1h')

# 计算信号
indicator = CompositeIndicator()
result = indicator.calculate(df)

# 获取最后一个信号
last_signal = result.iloc[-1]
print(f"Signal: {last_signal['signal']}")  # 1=BUY, -1=SELL, 0=HOLD
print(f"Strength: {last_signal['signal_strength']:.3f}")
```

### 过滤弱信号
```python
# 只保留强度>0.6的信号
strong_signals = result[result['signal_strength'] > 0.6]
print(f"Strong buy signals: {(strong_signals['signal'] == 1).sum()}")
print(f"Strong sell signals: {(strong_signals['signal'] == -1).sum()}")
```

### 分析指标分布
```python
print(f"Momentum Score Range: {result['momentum_score'].min():.3f} to {result['momentum_score'].max():.3f}")
print(f"Trend Score Mean: {result['trend_score'].mean():.3f}")
print(f"Volume Score Std: {result['volume_score'].std():.3f}")
```

---

## 下一步：模型验证

目前指标生成的信号需要通过机器学习模型进行验证：

1. **特征工程**：使用前一根K棒的所有指标值
2. **标签生成**：根据未来N根K棒的收益率
3. **模型训练**：XGBoost/LightGBM进行二分类
4. **回测验证**：验证信号的实际盈利能力
5. **风险管理**：确定止损止盈比例

---

## 参考资源

- RSI：超买超卖指标
- MACD：趋势跟随指标
- 布林线：波动率指标
- ATR：风险度量
- OBV：成交量指标

更多详细说明见代码注释。

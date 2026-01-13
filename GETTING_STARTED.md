# Crypto Trading Bot - 入门指南

## 项目概览

这是一个量化加密货币交易机器人项目，分两个阶段开发：

1. **Phase 1（已完成）**: 指标开发 - 创建创新的组合指标系统
2. **Phase 2（开发中）**: 模型验证 - 使用机器学习验证信号有效性

---

## 目录说明

### 根目录文件

| 文件 | 功能 | 使用频率 |
|------|------|----------|
| **README.md** | 项目简介和快速开始 | 常用 |
| **PROJECT_SUMMARY.md** | 项目全面总结（本指南） | 参考 |
| **GETTING_STARTED.md** | 这个文件，入门指南 | 首次阅读 |
| **requirements.txt** | Python依赖包列表 | 安装时使用 |
| **index.py** | 指标计算入口脚本 | **经常使用** |
| **main.py** | 模型训练入口脚本（Phase 2） | 后期使用 |

### modules/文件夹（模块化代码）

```
modules/
├── __init__.py              # 包初始化
├── indicators.py            # 关键：指标定义和计算逻辑
├── feature_engineering.py   # 特征工程（Phase 2）
└── model.py                 # 模型定义（Phase 2）
```

**indicators.py是最重要的文件，包含：**
- `TechnicalIndicators`: 基础技术指标（RSI, MACD等）
- `CompositeIndicator`: 创新的四维组合指标

### test/文件夹（测试和可视化）

```
test/
├── __init__.py              # 包初始化
├── INDICATOR_DESIGN.md      # 指标设计详解（必读）
├── QUICKSTART.md            # 快速启动指南
├── indicator_test.py        # 指标测试套件（推荐首先运行）
├── model_test.py            # 模型测试（Phase 2）
├── visualization.py         # 指标可视化工具
└── output_*.png             # 可视化输出图表
```

---

## 快速开始（5分钟）

### 步骤1：安装依赖

```bash
pip install -r requirements.txt
```

### 步骤2：运行指标测试

```bash
python test/indicator_test.py
```

**预期输出：** 验证所有指标计算正确，生成测试报告

### 步骤3：查看实际信号

```bash
# 查看Bitcoin 1小时级别的信号
python index.py BTCUSDT 1h

# 或查看以太坊
python index.py ETHUSDT 1h
```

**输出包括：**
- 最近20根K棒的信号和指标值
- 信号统计（共生成多少信号、成功率等）
- 当前市场状态和最新信号

### 步骤4：可视化分析

```bash
python test/visualization.py BTCUSDT 1h
```

**生成文件：** `test/output_BTCUSDT_1h.png`

包含4个图表：
1. K线价格 + 布林线 + SMA
2. 动量指标 (RSI, MACD)
3. 四个分量得分趋势
4. 成交量分析

---

## 理解指标系统

### 核心概念

**这个系统结合四个维度生成交易信号：**

```
交易信号 = f(动能, 趋势, 成交量, 波动率)
```

每个维度都是0-1的得分，越接近1表示看涨，越接近-1表示看跌。

### 四个维度简介

#### 1. 动能得分 (Momentum Score) - 35%权重
- **包含指标**: RSI, MACD, Momentum, ROC
- **含义**: 当前价格的动能强度
- **信号**: RSI>70 + MACD正向 = 强看涨

#### 2. 趋势得分 (Trend Score) - 35%权重
- **包含指标**: SMA20, SMA50, 布林线
- **含义**: 长期趋势方向
- **信号**: 价格 > SMA20 > SMA50 = 上升趋势

#### 3. 成交量得分 (Volume Score) - 20%权重
- **包含指标**: 成交量比率, OBV
- **含义**: 成交量确认力度
- **信号**: 成交量 > 1.5倍平均值 = 强确认

#### 4. 波动率得分 (Volatility Score) - 10%权重
- **包含指标**: ATR, 布林线宽度
- **含义**: 价格波动剧烈程度
- **信号**: 中等波动(5%-10%) = 最佳交易环境

### 关键特性：前一根K棒

**所有指标都基于前一根K棒的完整数据。为什么？**

在实时交易中，当前K棒仍在形成，价格不断变动，指标值也在变化。这会导致虚假信号。

**解决方案：** 使用前一根K棒的完整数据生成信号

```
前K棒完整     当前K棒形成中
(05:00-06:00) (06:00-...)
     ↓              ↓
基于该数据    06:00开盘时生成信号
生成信号      执行交易
```

---

## 使用示例

### 示例1：查看BTC的买卖信号

```bash
python index.py BTCUSDT 1h
```

**输出示例：**
```
================================================================================
Last 20 Candles:
open_time                close     volume  momentum_score  trend_score  signal
2026-01-13 04:00:00  45234.50  1234567     0.456          0.234       BUY
2026-01-13 05:00:00  45289.00  1456789     0.523          0.367       BUY
2026-01-13 06:00:00  45156.23  1098765     0.234          0.145       HOLD
...

Total Signals Generated: 47
Buy Signals: 25
Sell Signals: 22
Average Signal Strength: 0.652
```

**含义：**
- Signal = BUY: 买入信号
- Signal = SELL: 卖出信号  
- Signal = HOLD: 保持持仓
- signal_strength: 信号强度 (0-1, 越高越可靠)

### 示例2：比较不同币种

```bash
# ETH
python index.py ETHUSDT 1h

# SOL
python index.py SOLUSDT 1h

# BNB
python index.py BNBUSDT 1d
```

### 示例3：分析15分钟级别（短线交易）

```bash
python index.py BTCUSDT 15m
```

**注意：** 15分钟级别信号更频繁，但可靠性相对较低。

---

## 深入学习

### 必读文档

1. **test/INDICATOR_DESIGN.md** （最详细）
   - 指标结构详解
   - 四个分量的计算逻辑
   - 信号生成规则
   - 参数调整指南

2. **test/QUICKSTART.md**
   - 快速启动命令
   - 测试推荐序列
   - 问题排查

3. **PROJECT_SUMMARY.md**
   - 项目全面介绍
   - Phase 2计划
   - 技术栈说明

### 代码级理解

**主要类和方法：**

```python
# 在 modules/indicators.py 中

# 1. 基础指标
ti = TechnicalIndicators()
rsi = ti.rsi(prices)           # RSI指标
macd, signal, hist = ti.macd(prices)  # MACD指标

# 2. 组合指标（核心）
indicator = CompositeIndicator(
    lookback=20,               # 回看周期
    volume_threshold=1.2,      # 成交量倍数
    momentum_threshold=0.5,    # 动能阈值
    trend_strength=0.6         # 趋势强度
)

# 3. 计算完整信号
result_df = indicator.calculate(df)

# 4. 获取信号
latest_signal = result_df.iloc[-1]
print(latest_signal['signal'])         # 1=BUY, -1=SELL, 0=HOLD
print(latest_signal['signal_strength']) # 信号强度 0-1
```

---

## 常见问题

### Q: 如何调整信号敏感度？

**A:** 修改 `CompositeIndicator` 的参数：

```python
# 保守策略（更少信号，更高胜率）
indicator = CompositeIndicator(
    lookback=30,
    volume_threshold=1.5,
    momentum_threshold=0.6,
    trend_strength=0.7
)

# 激进策略（更多信号，风险较高）
indicator = CompositeIndicator(
    lookback=15,
    volume_threshold=1.0,
    momentum_threshold=0.3,
    trend_strength=0.4
)
```

### Q: 信号强度低的信号可信吗？

**A:** 
- **>0.7**: 极度可靠，多个指标同向
- **0.5-0.7**: 中等可靠，大多数指标同向
- **0.3-0.5**: 信号微弱，建议等待
- **<0.3**: 极弱信号，建议忽略

### Q: 为什么有些币种很少产生信号？

**A:** 
- 该币种波动率低或方向不明确
- 参数设置过于严格
- 时间框架不合适（可尝试更短或更长的周期）

### Q: 可以用实时数据吗？

**A:** 
目前系统使用 HuggingFace 的历史数据。要使用实时数据，需要：
1. 连接到交易所API（Binance, Kraken等）
2. 动态更新DataFrame
3. Phase 2会实现这个功能

---

## 下一步

### 立即可以做的

1. **运行所有测试**
   ```bash
   python test/indicator_test.py
   ```

2. **分析不同币种**
   ```bash
   for symbol in BTCUSDT ETHUSDT SOLUSDT BNBUSDT; do
       python index.py $symbol 1h
   done
   ```

3. **生成可视化**
   ```bash
   python test/visualization.py BTCUSDT 1h
   python test/visualization.py ETHUSDT 1h
   ```

4. **阅读详细文档**
   ```bash
   # 打开以下文件详细研究指标逻辑
   cat test/INDICATOR_DESIGN.md
   ```

### Phase 2准备

当你完全理解指标系统后，下一个阶段需要：

1. **模型开发**
   - 使用前一根K棒特征训练模型
   - XGBoost/LightGBM进行分类
   - LSTM进行时间序列预测

2. **信号验证**
   - 计算模型预测精度
   - 生成混淆矩阵和ROC曲线
   - 评估实际盈利能力

3. **回测框架**
   - 构建完整的回测引擎
   - 计算Sharpe比、最大回撤等指标
   - 进行风险管理优化

---

## 支持的币种和时间框架

### 币种（38个）

AAVE, ADA, ALGO, ARB, ATOM, AVAX, BAL, BAT, BCH, BNB, BTC, COMP, CRV, DOGE, DOT, ENJ, ENS, ETC, ETH, FIL, GALA, GRT, IMX, KAVA, LINK, LTC, MANA, MATIC, MKR, NEAR, OP, SAND, SNX, SOL, SPELL, UNI, XRP, ZRX

### 时间框架

- **15分钟** (15m): 日内短线
- **1小时** (1h): 日内中线
- **1天** (1d): 中长期

---

## 技术支持

如有问题，检查以下内容：

1. **依赖安装**
   ```bash
   pip list | grep -E 'pandas|numpy|scikit|xgboost|matplotlib'
   ```

2. **数据下载**
   - 确保网络连接正常
   - 首次运行会自动缓存数据

3. **查看错误日志**
   ```bash
   python index.py BTCUSDT 1h 2>&1 | head -50
   ```

---

## 免责声明

本项目仅供学习和研究使用。加密货币交易具有高风险。过去的表现不代表未来结果。在进行实际交易前，请充分了解市场风险并咨询专业人士。

---

## 许可证

MIT

---

**现在就开始吧！** 运行 `python test/indicator_test.py` 验证系统是否正常工作。

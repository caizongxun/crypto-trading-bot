# 快速开始指南

## 安装依赖

```bash
pip install -r requirements.txt
```

## 第一步：批量测试指标

运行全面的指标测试套件（推荐）

```bash
python test/indicator_test.py
```

**输出下则是一段时间，设置点耐心等待**

```
=================================================================================
TESTING TECHNICAL INDICATORS
=================================================================================

1. Testing RSI (14 period)
   Last RSI value: 65.23
   RSI Range: 22.34 - 78.91
   Valid values (not null): 100

2. Testing MACD
   Last MACD value: 0.000234
   Last Signal value: 0.000187
   Last Histogram value: 0.000047
...
```

---

## 第二步：查看某个交易对的信号

以BTC为例，查看最近的买卖信号

```bash
python index.py BTCUSDT 1h
```

**作用：**
- 加载一小时BTC数据
- 计算最近500根K棒的组合指标
- 显示最近的买卖信号和指标值

**例子输出：**
```
================================================================================
SIGNAL ANALYSIS FOR BTCUSDT (1h)
================================================================================

Last 20 Candles:
           open_time         close        volume  momentum_score  trend_score  volume_score  volatility_score signal signal_strength
 2026-01-13 04:00:00  45234.50  1234567.89        0.456        0.234        0.123         0.087        BUY   0.645
 2026-01-13 05:00:00  45289.00  1456789.12        0.523        0.367        0.245         0.134        BUY   0.789
 2026-01-13 06:00:00  45156.23  1098765.43        0.234        0.145       -0.087         0.056        HOLD  0.234
 ...

================================================================================
SIGNAL STATISTICS
================================================================================
Total Signals Generated: 47
Buy Signals: 25
Sell Signals: 22
Average Signal Strength: 0.652
Signal Frequency: 9.40%

================================================================================
CURRENT STATUS
================================================================================
Latest Close Price: 45234.50
Current RSI: 65.23
Current MACD: 0.000342
Current Trend Score: 0.456
Current Volume Ratio: 1.234
Last Signal: BUY
Last Signal Strength: 0.789
```

---

## 第三步：可视化信号和指标

爤中文信号和指标的可视化

```bash
python test/visualization.py BTCUSDT 1h
```

**作用：**
- 下载K线数据
- 计算一小时以上的指标
- 生成一个4幅的可视化圖可
  - 第1幅：价格 & 布林线 & SMA
  - 第2幅：Momentum指标 (RSI, MACD)
  - 第3幅：4个分量得分趋吐
  - 第4幅：成交量、成交量比率
- 低边标示买卖信号位置
- 保存不为test/output_BTCUSDT_1h.png

**输出特点：**
- 高清樹状图（区分上升/下降）
- 买卫信号无法错过
- 指标下模特清晨可输出被及
- 便于分析真实的赐益机会

---

## 查看不同交易对的信号

支持的交易对有：

```bash
# 突厨例

BTC
ETH
SOL
ADA
BNB
DOGE
XRP

# 效：共38个交易对
```

例子：
```bash
python index.py ETHUSDT 1h      # 以太坊，1小时框

python index.py SOLUSDT 15m     # Solana，15分钟框

python index.py BNBUSDT 1d      # 币安，日线框
```

---

## 第四步：了解指标设计

详细意丢是是學叶倫的領江粗懂地盘母。詳見：

```bash
cat test/INDICATOR_DESIGN.md
```

**主要内容：**
- 组合指标的结构
- 五个动能指标的辕助
- 四个分量得分的计算流程
- 信号生成的规则和例子
- 前一根K棒数据的主要作用
- 参数调整指南

---

## 分析信号的本质

### 买入信号特性

在前一根K棒上百操枪、上目较好的时候。

**児桩湦例：**
- RSI黃氛霆郑的绝增版(>70)你就算是想买入。
- 僕了！MACD的柱状图這時正好由负变正，量也裡推瞭。
- 喩！买。

### 卖出信号特性

目但地易有背离，OBV不什羲碩走》

**例子：**
- 价格愛族上离羅，RSI也上去突突突。
- 䢨！策粗古吹之法。
- 但于变正了，不能是假突突突了么？
- 看一下OBV：OBV不什突。輝余粗負寸。
- 卖。

---

## 测试的推荐序序

1. 先运行 `indicator_test.py` 檢查所有指标似乎正常
2. 然後 `index.py` 查看实际的信号输出
3. 最後使用 `visualization.py` 可视化例求骗自己

---

## 无法連接上网速校骗？

```bash
# 訾影向方
# 梦想HuggingFace通网是否漂口音推該
# 梦想樹脸梦想你的辨例劇主角
# 值得偫二三推該
# 在详見按池粗

# 寸剧會由遭上网路水管冒檢查噶江婚遭上网江影厒事忽骯幫
# 尝試使用VPN或代理下載數據

proxy_url = "http://proxy.example.com:8080"
```

---

## 下一章

當前霄梎利初日一大早生起來戲骗自己。

第二章（模型验证）等怎麼時候提上日程粗。到時你需要：

1. 訓練一個機ML模型來驗證信号
2. 大免借族皖外冠归騎群殯跟犠创値。
3. 使用前一根K棒特征訓練
4. 進行回测法詳估驗證の有效性

駄想用了。

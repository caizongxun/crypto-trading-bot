# Crypto Trading Bot

量化加密货币交易机器人，结合技术指标和机器学习模型进行信号验证和交易执行。

## 项目架构

```
crypto-trading-bot/
├── main.py                 # 模型训练和评估主程序
├── index.py               # 指标计算和信号生成
├── requirements.txt       # 依赖项
├── README.md             # 本文件
├── modules/              # 可调整的模块化程式码
│   ├── __init__.py
│   ├── indicators.py     # 指标计算逻辑
│   ├── feature_engineering.py  # 特征工程
│   └── model.py          # 模型定义和训练
└── test/                 # 测试和可视化
    ├── __init__.py
    ├── indicator_test.py # 指标测试
    ├── model_test.py     # 模型测试
    └── visualization.py  # 可视化工具
```

## 工作流程

### 1. 指标层面（index.py）

- 使用历史K线数据计算技术指标
- 基于多个指标的组合生成信号（买入/卖出/持有）
- 使用前一根K棒的数据作为训练基准

### 2. 模型层面（main.py）

- 读取指标生成的信号
- 用前一根K棒数据训练ML模型
- 验证信号的有效性
- 进行回测评估

## 安装依赖

```bash
pip install -r requirements.txt
```

## 当前开发阶段

测试阶段 - 所有开发代码位于 `test/` 文件夹

## 使用指南

### 运行指标计算

```python
python index.py
```

### 训练和评估模型

```python
python main.py
```

### 执行测试

```python
python -m pytest test/
```

## 数据来源

HuggingFace Dataset: `zongowo111/v2-crypto-ohlcv-data`

支持的交易对: 38个主流加密货币（BTC, ETH, SOL 等）

支持的时间框架: 15分钟, 1小时, 日线

## 指标设计策略

结合以下因素生成进场信号:
- 成交量分析（Volume）
- 动能指标（Momentum）
- 趋势指标（Trend）
- 波动率指标（Volatility）

## 许可证

MIT

const express = require('express');
const fs = require('fs');
const path = require('path');
const fetch = require('node-fetch');
const app = express();

app.use(express.json());

// ==================== 持久化文件 ====================
const STATE_FILE = 'trading_state.json';
const LOGS_FILE = 'trading_logs.json';

let STATE = {
    isPaused: false,
    balance: 10000,
    initialBalance: 10000,
    positions: {},
    trades: [],
    priceHistory: {},
    priceIndicators: {},
    tradeId: 0,
    enabledStrategies: { ptsi: true, ptsia: true, ptsim: true, ptsiv: true },
    lastUpdate: new Date(),
    logs: []
};

const CONFIG = {
    CRYPTOS: [
        { id: 'bitcoin', symbol: 'BTC', name: 'Bitcoin' },
        { id: 'ethereum', symbol: 'ETH', name: 'Ethereum' },
        { id: 'binancecoin', symbol: 'BNB', name: 'BNB' },
        { id: 'solana', symbol: 'SOL', name: 'Solana' },
        { id: 'ripple', symbol: 'XRP', name: 'Ripple' },
        { id: 'cardano', symbol: 'ADA', name: 'Cardano' },
        { id: 'polkadot', symbol: 'DOT', name: 'Polkadot' },
        { id: 'dogecoin', symbol: 'DOGE', name: 'Dogecoin' },
        { id: 'polygon', symbol: 'MATIC', name: 'Polygon' },
        { id: 'chainlink', symbol: 'LINK', name: 'Chainlink' },
        { id: 'litecoin', symbol: 'LTC', name: 'Litecoin' },
        { id: 'monero', symbol: 'XMR', name: 'Monero' }
    ],
    STRATEGY_PARAMS: {
        ptsi: { period: 20, buyThreshold: 20, sellThreshold: 80 },
        ptsia: { period: 25, buyThreshold: 25, sellThreshold: 75 },
        ptsim: { period: 20, buyThreshold: 22, sellThreshold: 78 },
        ptsiv: { period: 20, buyThreshold: 24, sellThreshold: 76 }
    }
};

// ==================== 狀態管理 ====================
function loadState() {
    try {
        if (fs.existsSync(STATE_FILE)) {
            STATE = JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
            console.log('✅ 交易狀態已恢復');
        }
    } catch (e) {
        console.error('❌ 狀態讀取失敗:', e.message);
    }
}

function saveState() {
    try {
        fs.writeFileSync(STATE_FILE, JSON.stringify(STATE, null, 2));
    } catch (e) {
        console.error('❌ 狀態保存失敗:', e.message);
    }
}

function addLog(message, type = 'info') {
    const timestamp = new Date().toISOString();
    const logEntry = { timestamp, message, type };
    STATE.logs.push(logEntry);
    
    if (STATE.logs.length > 500) {
        STATE.logs.shift();
    }
    
    console.log(`[${type.toUpperCase()}] ${message}`);
}

// ==================== PTSI 指標計算 ====================
function calculatePTSI(prices, period = 20) {
    if (prices.length < period) return null;
    
    const slice = prices.slice(-period);
    const mean = slice.reduce((a, b) => a + b) / period;
    const variance = slice.reduce((sum, p) => sum + Math.pow(p - mean, 2), 0) / period;
    const timeVar = period * period / 12;
    const timeDeviation = Array.from({ length: period }, (_, k) => k - period / 2);
    const covariance = slice.reduce((sum, p, idx) => sum + (p - mean) * timeDeviation[idx], 0) / period;
    const correlation = covariance / (Math.sqrt(variance) * Math.sqrt(timeVar) + 0.0001);
    const symmetry = Math.sqrt(Math.abs(variance * timeVar)) / (Math.abs(correlation) + 0.0001);
    
    return Math.min(100, Math.max(0, symmetry * 5));
}

function calculatePTSIA(prices) {
    if (prices.length < 30) return null;
    let maxSymmetry = 0;
    for (let period = 10; period <= 30; period += 5) {
        const slice = prices.slice(-period);
        if (slice.length >= period) {
            const ptsi = calculatePTSI(slice, period);
            maxSymmetry = Math.max(maxSymmetry, ptsi || 0);
        }
    }
    return maxSymmetry;
}

function calculatePTSIM(prices) {
    if (prices.length < 20) return null;
    const ptsiBase = calculatePTSI(prices, 20) || 50;
    const momentum = ((prices[prices.length - 1] - prices[prices.length - 2]) / prices[prices.length - 2]) * 100;
    const momSmoothed = Math.tanh(momentum / 5) * 50;
    return ptsiBase * 0.6 + momSmoothed * 0.4;
}

function calculatePTSIV(prices, volumes) {
    if (prices.length < 20 || !volumes || volumes.length < 20) return null;
    
    const period = 20;
    const priceSlice = prices.slice(-period);
    const volSlice = volumes.slice(-period);
    const mean = priceSlice.reduce((a, b) => a + b) / period;
    
    const volNorm = volSlice.map(v => v / Math.max(...volSlice));
    const weightedVariance = priceSlice.reduce((sum, p, idx) => 
        sum + volNorm[idx] * Math.pow(p - mean, 2), 0) / period;
    
    return Math.min(100, Math.max(0, Math.sqrt(Math.abs(weightedVariance)) / (mean + 0.0001) * 50));
}

function calculateIndicator(cryptoId, strategy) {
    const prices = STATE.priceHistory[cryptoId];
    if (!prices || prices.length < 20) return null;

    switch (strategy) {
        case 'ptsi':
            return calculatePTSI(prices, 20);
        case 'ptsia':
            return calculatePTSIA(prices);
        case 'ptsim':
            return calculatePTSIM(prices);
        case 'ptsiv':
            return calculatePTSIV(prices, STATE.priceHistory[cryptoId + '_volume'] || []);
        default:
            return calculatePTSI(prices, 20);
    }
}

// ==================== 價格獲取 ====================
async function fetchPrices() {
    const prices = {};
    
    for (const crypto of CONFIG.CRYPTOS) {
        try {
            const response = await fetch(
                `https://api.coingecko.com/api/v3/simple/price?ids=${crypto.id}&vs_currencies=usd`
            );
            const data = await response.json();
            prices[crypto.id] = data[crypto.id]?.usd || null;
        } catch (e) {
            prices[crypto.id] = null;
        }
    }
    
    return prices;
}

// ==================== 交易邏輯 ====================
function checkAndExecuteTrades(prices) {
    const balance = STATE.balance;
    const positionSize = 0.03; // 3%
    const maxLeverage = 10;
    const stopLoss = 0.03; // 3%
    const takeProfit = 0.08; // 8%

    CONFIG.CRYPTOS.forEach(crypto => {
        if (!prices[crypto.id]) return;

        // 初始化價格歷史
        if (!STATE.priceHistory[crypto.id]) {
            STATE.priceHistory[crypto.id] = [];
        }
        STATE.priceHistory[crypto.id].push(prices[crypto.id]);
        
        if (STATE.priceHistory[crypto.id].length > 100) {
            STATE.priceHistory[crypto.id].shift();
        }

        // 更新價格指標
        STATE.priceIndicators[crypto.id] = {
            price: prices[crypto.id],
            change: prices[crypto.id] - (STATE.priceIndicators[crypto.id]?.price || prices[crypto.id]),
            prevPrice: STATE.priceIndicators[crypto.id]?.price || prices[crypto.id]
        };

        // 檢查持倉的止損/止盈
        const posKey = crypto.id;
        if (STATE.positions[posKey]) {
            const pos = STATE.positions[posKey];
            pos.currentPrice = prices[crypto.id];
            
            const unrealizedPnL = (prices[crypto.id] - pos.entryPrice) * pos.quantity * pos.leverage;
            const unrealizedPercent = unrealizedPnL / pos.entryPrice;

            if (unrealizedPercent <= -stopLoss || unrealizedPercent >= takeProfit) {
                const reason = unrealizedPercent <= -stopLoss ? 'STOP_LOSS' : 'TAKE_PROFIT';
                closeTrade(posKey, prices[crypto.id], reason, pos.strategy);
                return;
            }
        }

        if (STATE.positions[posKey]) return;

        // 執行所有啟用的策略
        for (const [strategyName, enabled] of Object.entries(STATE.enabledStrategies)) {
            if (!enabled) continue;

            const params = CONFIG.STRATEGY_PARAMS[strategyName];
            const indicator = calculateIndicator(crypto.id, strategyName);

            if (!indicator) continue;

            // BUY 信號
            if (indicator < params.buyThreshold) {
                const buyAmount = balance * positionSize;
                const quantity = buyAmount / prices[crypto.id];
                
                STATE.tradeId++;
                STATE.positions[posKey] = {
                    id: STATE.tradeId,
                    symbol: crypto.symbol,
                    cryptoId: crypto.id,
                    entryPrice: prices[crypto.id],
                    currentPrice: prices[crypto.id],
                    quantity,
                    leverage: maxLeverage,
                    entryTime: Date.now(),
                    strategy: strategyName,
                    side: 'LONG'
                };

                STATE.balance -= buyAmount;
                addLog(`📈 BUY ${crypto.symbol} | ${strategyName.toUpperCase()} @ $${prices[crypto.id].toFixed(2)} | 指標: ${indicator.toFixed(2)}`, 'buy');
                break;
            }
            // SELL 信號
            else if (indicator > params.sellThreshold && STATE.positions[posKey]) {
                closeTrade(posKey, prices[crypto.id], 'SIGNAL', strategyName);
                break;
            }
        }
    });
}

function closeTrade(posKey, exitPrice, reason, strategy) {
    const pos = STATE.positions[posKey];
    if (!pos) return;

    const pnl = (exitPrice - pos.entryPrice) * pos.quantity * pos.leverage;

    const trade = {
        id: pos.id,
        symbol: pos.symbol,
        entryPrice: pos.entryPrice,
        exitPrice: exitPrice,
        quantity: pos.quantity,
        leverage: pos.leverage,
        entryTime: pos.entryTime,
        exitTime: Date.now(),
        pnl: pnl,
        strategy: pos.strategy,
        reason: reason
    };

    STATE.trades.push(trade);
    STATE.balance += (pos.quantity * exitPrice * pos.leverage);
    
    delete STATE.positions[posKey];

    const pnlStr = pnl >= 0 ? `+$${pnl.toFixed(2)}` : `$${pnl.toFixed(2)}`;
    addLog(`📉 SELL ${pos.symbol} @ $${exitPrice.toFixed(2)} | P&L: ${pnlStr} | 原因: ${reason}`, 'sell');
}

// ==================== 主交易迴圈 ====================
async function tradingLoop() {
    if (STATE.isPaused) return;

    try {
        const prices = await fetchPrices();
        if (!prices) return;

        checkAndExecuteTrades(prices);
        STATE.lastUpdate = new Date();
        saveState();
    } catch (e) {
        addLog(`❌ 交易循環錯誤: ${e.message}`, 'error');
    }
}

// ==================== API 路由 ====================

// 獲取交易狀態
app.get('/api/state', (req, res) => {
    res.json({
        ...STATE,
        logs: STATE.logs.slice(-100) // 只返回最後 100 條日誌
    });
});

// 暫停交易
app.post('/api/pause', (req, res) => {
    STATE.isPaused = true;
    addLog('⏸ 交易已暫停', 'info');
    saveState();
    res.json({ status: 'paused', message: '交易已暫停' });
});

// 恢復交易
app.post('/api/resume', (req, res) => {
    STATE.isPaused = false;
    addLog('▶ 交易已恢復', 'info');
    saveState();
    res.json({ status: 'running', message: '交易已恢復' });
});

// 重置所有數據
app.post('/api/reset', (req, res) => {
    STATE = {
        isPaused: false,
        balance: 10000,
        initialBalance: 10000,
        positions: {},
        trades: [],
        priceHistory: {},
        priceIndicators: {},
        tradeId: 0,
        enabledStrategies: { ptsi: true, ptsia: true, ptsim: true, ptsiv: true },
        lastUpdate: new Date(),
        logs: []
    };
    addLog('🔄 交易已重置', 'info');
    saveState();
    res.json({ status: 'reset', message: '所有數據已重置' });
});

// 更新策略狀態
app.post('/api/strategy/:name', (req, res) => {
    const { name } = req.params;
    const { enabled } = req.body;
    
    if (STATE.enabledStrategies.hasOwnProperty(name)) {
        STATE.enabledStrategies[name] = enabled;
        addLog(`策略 ${name.toUpperCase()} 已${enabled ? '啟用' : '禁用'}`, 'info');
        saveState();
        res.json({ status: 'success', strategy: name, enabled });
    } else {
        res.status(404).json({ error: '未知的策略' });
    }
});

// 清除日誌
app.post('/api/logs/clear', (req, res) => {
    STATE.logs = [];
    res.json({ status: 'cleared', message: '日誌已清除' });
});

// 靜態文件服務
app.use(express.static('public'));

// 健康檢查
app.get('/health', (req, res) => {
    res.json({ 
        status: 'ok', 
        balance: STATE.balance,
        positions: Object.keys(STATE.positions).length,
        trades: STATE.trades.length,
        lastUpdate: STATE.lastUpdate
    });
});

// ==================== 初始化 ====================
loadState();

// 初始化價格歷史
CONFIG.CRYPTOS.forEach(crypto => {
    if (!STATE.priceHistory[crypto.id]) {
        STATE.priceHistory[crypto.id] = [];
    }
    if (!STATE.priceIndicators[crypto.id]) {
        STATE.priceIndicators[crypto.id] = null;
    }
});

addLog('🚀 Crypto Trading Bot v5 伺服器已啟動 - 24/7 自動交易模式', 'info');
addLog('💡 機器人正在後台無間斷運行所有啟用的策略', 'info');

// 啟動交易迴圈 (每分鐘執行一次)
setInterval(tradingLoop, 60000);

// 立即執行第一次
tradingLoop();

// ==================== 啟動伺服器 ====================
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`\n🚀 交易機器人伺服器運行於 http://localhost:${PORT}`);
    console.log(`📊 監控面板: http://localhost:${PORT}`);
    console.log(`💾 狀態文件: ${STATE_FILE}\n`);
});

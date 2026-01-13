import pandas as pd
import numpy as np
from typing import Tuple, List


class TechnicalIndicators:
    """Basic technical indicators calculation"""
    
    @staticmethod
    def rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Moving Average Convergence Divergence"""
        exp1 = prices.ewm(span=fast, adjust=False).mean()
        exp2 = prices.ewm(span=slow, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line
        return macd, signal_line, histogram
    
    @staticmethod
    def bollinger_bands(prices: pd.Series, period: int = 20, num_std: float = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Bollinger Bands"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper = sma + (std * num_std)
        lower = sma - (std * num_std)
        return upper, sma, lower
    
    @staticmethod
    def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Average True Range"""
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        return atr
    
    @staticmethod
    def volume_sma(volume: pd.Series, period: int = 20) -> pd.Series:
        """Volume Simple Moving Average"""
        return volume.rolling(window=period).mean()
    
    @staticmethod
    def obv(close: pd.Series, volume: pd.Series) -> pd.Series:
        """On-Balance Volume"""
        obv = np.zeros(len(close))
        obv[0] = volume.iloc[0]
        
        for i in range(1, len(close)):
            if close.iloc[i] > close.iloc[i-1]:
                obv[i] = obv[i-1] + volume.iloc[i]
            elif close.iloc[i] < close.iloc[i-1]:
                obv[i] = obv[i-1] - volume.iloc[i]
            else:
                obv[i] = obv[i-1]
        
        return pd.Series(obv, index=close.index)
    
    @staticmethod
    def momentum(prices: pd.Series, period: int = 10) -> pd.Series:
        """Price Momentum"""
        return prices - prices.shift(period)
    
    @staticmethod
    def roc(prices: pd.Series, period: int = 12) -> pd.Series:
        """Rate of Change"""
        return ((prices - prices.shift(period)) / prices.shift(period)) * 100


class CompositeIndicator:
    """Advanced composite indicator combining volume, momentum, trend and volatility"""
    
    def __init__(self, lookback: int = 20, 
                 volume_threshold: float = 1.2,
                 momentum_threshold: float = 0.5,
                 trend_strength: float = 0.6):
        """
        Initialize composite indicator
        
        Args:
            lookback: Lookback period for SMA
            volume_threshold: Volume ratio threshold (current/average)
            momentum_threshold: Momentum threshold percentage
            trend_strength: Trend strength requirement (0-1)
        """
        self.lookback = lookback
        self.volume_threshold = volume_threshold
        self.momentum_threshold = momentum_threshold
        self.trend_strength = trend_strength
        self.indicators = TechnicalIndicators()
    
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate composite signal
        
        Args:
            df: DataFrame with columns [open, high, low, close, volume]
        
        Returns:
            DataFrame with signal columns
        """
        result = df.copy()
        
        # 1. Momentum Analysis
        result['rsi'] = self.indicators.rsi(df['close'], period=14)
        result['macd'], result['signal_line'], result['histogram'] = self.indicators.macd(df['close'])
        result['momentum'] = self.indicators.momentum(df['close'], period=10)
        result['roc'] = self.indicators.roc(df['close'], period=12)
        
        # 2. Trend Analysis
        result['sma_20'] = df['close'].rolling(window=self.lookback).mean()
        result['sma_50'] = df['close'].rolling(window=50).mean()
        result['trend'] = (result['sma_20'] - result['sma_50']) / result['sma_50']
        
        # 3. Volatility Analysis
        result['atr'] = self.indicators.atr(df['high'], df['low'], df['close'], period=14)
        result['bollinger_upper'], result['bollinger_mid'], result['bollinger_lower'] = self.indicators.bollinger_bands(df['close'])
        result['volatility'] = (result['bollinger_upper'] - result['bollinger_lower']) / result['bollinger_mid']
        
        # 4. Volume Analysis
        result['volume_sma'] = self.indicators.volume_sma(df['volume'], period=self.lookback)
        result['volume_ratio'] = df['volume'] / result['volume_sma']
        result['obv'] = self.indicators.obv(df['close'], df['volume'])
        result['obv_sma'] = result['obv'].rolling(window=self.lookback).mean()
        
        # 5. Composite Signal Components
        result = self._compute_signal_components(result)
        
        # 6. Final Signal
        result['signal'] = self._generate_signal(result)
        result['signal_strength'] = self._calculate_signal_strength(result)
        
        return result
    
    def _compute_signal_components(self, df: pd.DataFrame) -> pd.DataFrame:
        """Compute individual signal components"""
        
        # Momentum Component (RSI + MACD)
        df['momentum_score'] = self._momentum_component(df)
        
        # Trend Component (Price vs SMA)
        df['trend_score'] = self._trend_component(df)
        
        # Volume Component (Volume ratio + OBV)
        df['volume_score'] = self._volume_component(df)
        
        # Volatility Component (ATR + Bollinger Bands)
        df['volatility_score'] = self._volatility_component(df)
        
        return df
    
    def _momentum_component(self, df: pd.DataFrame) -> pd.Series:
        """Calculate momentum score (-1 to 1)"""
        rsi_signal = (df['rsi'] - 50) / 50  # Normalize RSI
        macd_signal = np.sign(df['histogram']) * (abs(df['histogram']) / (abs(df['histogram']).rolling(20).max() + 1e-6))
        momentum_signal = np.sign(df['momentum'])
        roc_signal = np.sign(df['roc'])
        
        # Weighted average
        score = 0.35 * rsi_signal + 0.35 * macd_signal + 0.20 * momentum_signal + 0.10 * roc_signal
        return score.fillna(0).clip(-1, 1)
    
    def _trend_component(self, df: pd.DataFrame) -> pd.Series:
        """Calculate trend score (-1 to 1)"""
        # Price position relative to SMAs
        close_to_mid = (df['close'] - df['sma_20']) / (df['sma_20'] + 1e-6)
        close_to_lower = (df['close'] - df['bollinger_lower']) / (df['bollinger_mid'] + 1e-6)
        
        # SMA alignment
        sma_alignment = np.sign(df['sma_20'] - df['sma_50'])
        
        # Trend score
        score = 0.40 * close_to_mid.clip(-1, 1) + 0.30 * close_to_lower.clip(-1, 1) + 0.30 * sma_alignment
        return score.fillna(0).clip(-1, 1)
    
    def _volume_component(self, df: pd.DataFrame) -> pd.Series:
        """Calculate volume score (-1 to 1)"""
        # Volume surge detection
        volume_surge = np.log(df['volume_ratio'] + 1) / np.log(3)  # Log scale
        
        # OBV trend
        obv_trend = np.sign(df['obv'] - df['obv_sma'])
        
        # Volume score
        score = 0.60 * volume_surge.clip(-1, 1) + 0.40 * obv_trend
        return score.fillna(0).clip(-1, 1)
    
    def _volatility_component(self, df: pd.DataFrame) -> pd.Series:
        """Calculate volatility score (-1 to 1)"""
        # ATR relative to price
        atr_ratio = (df['atr'] / df['close']).clip(0, 0.1)  # Normalize
        
        # Bollinger Band width
        bb_width = df['volatility'] / 0.1  # Expected normalized width ~0.1
        
        # Volatility score (higher volatility with direction = higher opportunity)
        score = (atr_ratio + bb_width) / 2
        return score.fillna(0).clip(-1, 1)
    
    def _generate_signal(self, df: pd.DataFrame) -> pd.Series:
        """
        Generate trading signal: 1 (BUY), -1 (SELL), 0 (HOLD)
        Based on previous candle data
        """
        signal = pd.Series(0, index=df.index)
        
        # Shift all scores to use previous candle
        momentum_prev = df['momentum_score'].shift(1)
        trend_prev = df['trend_score'].shift(1)
        volume_prev = df['volume_score'].shift(1)
        volatility_prev = df['volatility_score'].shift(1)
        
        # Composite score
        composite = (0.35 * momentum_prev + 
                    0.35 * trend_prev + 
                    0.20 * volume_prev + 
                    0.10 * volatility_prev)
        
        # BUY Signal: Strong uptrend + volume + momentum
        buy_condition = (
            (composite > 0.4) &
            (volume_prev > 0.2) &
            (momentum_prev > 0.2) &
            (trend_prev > -0.3)
        )
        
        # SELL Signal: Strong downtrend + volume + momentum
        sell_condition = (
            (composite < -0.4) &
            (volume_prev > 0.2) &
            (momentum_prev < -0.2) &
            (trend_prev < 0.3)
        )
        
        signal[buy_condition] = 1
        signal[sell_condition] = -1
        
        return signal
    
    def _calculate_signal_strength(self, df: pd.DataFrame) -> pd.Series:
        """Calculate signal confidence (0 to 1)"""
        momentum_prev = df['momentum_score'].shift(1)
        trend_prev = df['trend_score'].shift(1)
        volume_prev = df['volume_score'].shift(1)
        
        # Strength based on agreement of indicators
        agreement = (abs(momentum_prev) + abs(trend_prev)) / 2
        volume_boost = (volume_prev + 1) / 2  # 0.5 to 1.0 range
        
        strength = agreement * volume_boost
        return strength.fillna(0).clip(0, 1)

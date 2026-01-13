import pandas as pd


FEATURE_COLUMNS = [
    'rsi',
    'macd',
    'histogram',
    'momentum',
    'momentum_score',
    'trend_score',
    'volume_score',
    'volatility_score',
    'volume_ratio',
    'atr',
    'roc',
]


def extract_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extract ML feature columns from a DataFrame with signals."""
    return df[FEATURE_COLUMNS].copy()


def get_feature_columns():
    return FEATURE_COLUMNS

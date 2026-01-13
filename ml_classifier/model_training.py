import xgboost as xgb
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
import pandas as pd


def train_signal_classifier(df: pd.DataFrame, feature_columns: list, test_size: float = 0.3, random_state: int = 42):
    """Train an XGBoost classifier to distinguish true vs false signals."""
    X = df[feature_columns].values
    y = df['label'].values
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=test_size, shuffle=False
    )
    
    model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=random_state,
        objective='binary:logistic',
        eval_metric='logloss'
    )
    
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    report = classification_report(y_test, y_pred, output_dict=True)
    
    return {
        'model': model,
        'scaler': scaler,
        'report': report
    }

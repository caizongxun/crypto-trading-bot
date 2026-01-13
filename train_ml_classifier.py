#!/usr/bin/env python3
"""
ML Signal Classifier Training Script

Usage:
    python train_ml_classifier.py
    python train_ml_classifier.py --lookback 5000
    python train_ml_classifier.py --lookback 10000 --symbol ETHUSDT
"""

import sys
import argparse
import pickle
import json
from pathlib import Path

import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score

from index import calculate_signals
from ml_classifier import (
    prepare_signal_data,
    label_signals,
    extract_features,
    get_feature_columns,
    train_signal_classifier,
)


def main():
    parser = argparse.ArgumentParser(description="Train ML signal classifier")
    parser.add_argument(
        "--lookback",
        type=int,
        default=5000,
        help="Number of recent candles to analyze (default: 5000)"
    )
    parser.add_argument(
        "--symbol",
        type=str,
        default="BTCUSDT",
        help="Trading symbol (default: BTCUSDT)"
    )
    parser.add_argument(
        "--timeframe",
        type=str,
        default="15m",
        help="Timeframe (default: 15m)"
    )
    parser.add_argument(
        "--hold-period",
        type=int,
        default=3,
        help="Hold period for label generation in candles (default: 3)"
    )
    parser.add_argument(
        "--profit-threshold",
        type=float,
        default=0.0005,
        help="Profit threshold for true signal label (default: 0.0005 = 0.05%%)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="ml_models",
        help="Output directory for trained models (default: ml_models)"
    )
    
    args = parser.parse_args()
    
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    print("\n" + "="*80)
    print("ML SIGNAL CLASSIFIER TRAINING")
    print("="*80)
    
    print(f"\nConfiguration:")
    print(f"  Symbol: {args.symbol}")
    print(f"  Timeframe: {args.timeframe}")
    print(f"  Lookback: {args.lookback} candles")
    print(f"  Hold Period: {args.hold_period} candles")
    print(f"  Profit Threshold: {args.profit_threshold * 100:.3f}%")
    print(f"  Output Directory: {output_dir}")
    
    print("\n" + "-"*80)
    print("Step 1: Loading and calculating signals")
    print("-"*80)
    
    try:
        df = calculate_signals(args.symbol, args.timeframe, lookback=args.lookback)
        print(f"\nLoaded {len(df)} candles")
        print(f"Date range: {df['open_time'].min()} to {df['open_time'].max()}")
    except Exception as e:
        print(f"Error loading data: {e}")
        return False
    
    print("\n" + "-"*80)
    print("Step 2: Preparing signal data")
    print("-"*80)
    
    signals_df = prepare_signal_data(df)
    print(f"\nFound {len(signals_df)} signals")
    print(f"  Buy signals: {(signals_df['signal'] == 1).sum()}")
    print(f"  Sell signals: {(signals_df['signal'] == -1).sum()}")
    
    print("\n" + "-"*80)
    print("Step 3: Labeling signals (true/false)")
    print("-"*80)
    
    labeled_df = label_signals(
        signals_df,
        hold_period=args.hold_period,
        profit_threshold=args.profit_threshold
    )
    
    true_count = (labeled_df['label'] == 1).sum()
    false_count = (labeled_df['label'] == 0).sum()
    true_pct = true_count / len(labeled_df) * 100 if len(labeled_df) > 0 else 0
    
    print(f"\nLabeled {len(labeled_df)} signals:")
    print(f"  True signals: {true_count} ({true_pct:.1f}%)")
    print(f"  False signals: {false_count} ({100-true_pct:.1f}%)")
    
    if len(labeled_df) < 100:
        print(f"\nWarning: Only {len(labeled_df)} labeled samples. Recommend at least 100-200.")
        print("Try increasing --lookback to get more samples.")
    
    print("\n" + "-"*80)
    print("Step 4: Extracting features")
    print("-"*80)
    
    feature_columns = get_feature_columns()
    print(f"\nUsing {len(feature_columns)} features:")
    for i, feat in enumerate(feature_columns, 1):
        print(f"  {i}. {feat}")
    
    print("\n" + "-"*80)
    print("Step 5: Training XGBoost classifier")
    print("-"*80)
    
    try:
        result = train_signal_classifier(
            labeled_df,
            feature_columns,
            test_size=0.3
        )
        
        model = result['model']
        scaler = result['scaler']
        report = result['report']
        
        print("\nTraining completed successfully!")
        
    except Exception as e:
        print(f"Error during training: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "-"*80)
    print("Step 6: Model evaluation")
    print("-"*80)
    
    print("\nClassification Report:")
    print("-" * 60)
    
    for key in ['0', '1']:
        if key in report:
            label_name = 'False Signal' if key == '0' else 'True Signal'
            metrics = report[key]
            print(f"{label_name}:")
            print(f"  Precision: {metrics['precision']:.4f}")
            print(f"  Recall: {metrics['recall']:.4f}")
            print(f"  F1-Score: {metrics['f1-score']:.4f}")
            print()
    
    if 'accuracy' in report:
        print(f"Overall Accuracy: {report['accuracy']:.4f}")
    if 'weighted avg' in report:
        print(f"Weighted Avg F1: {report['weighted avg']['f1-score']:.4f}")
    
    feature_importance = model.feature_importances_
    sorted_idx = np.argsort(feature_importance)[::-1]
    
    print("\nTop 5 Most Important Features:")
    print("-" * 60)
    for rank, idx in enumerate(sorted_idx[:5], 1):
        feat_name = feature_columns[idx]
        importance = feature_importance[idx]
        print(f"{rank}. {feat_name}: {importance:.4f}")
    
    print("\n" + "-"*80)
    print("Step 7: Saving models")
    print("-"*80)
    
    try:
        model_path = output_dir / f"classifier_{args.symbol}_{args.timeframe}.pkl"
        scaler_path = output_dir / f"scaler_{args.symbol}_{args.timeframe}.pkl"
        config_path = output_dir / f"config_{args.symbol}_{args.timeframe}.json"
        
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        
        with open(scaler_path, 'wb') as f:
            pickle.dump(scaler, f)
        
        config = {
            'symbol': args.symbol,
            'timeframe': args.timeframe,
            'lookback': args.lookback,
            'hold_period': args.hold_period,
            'profit_threshold': args.profit_threshold,
            'feature_columns': feature_columns,
            'num_samples': len(labeled_df),
            'true_signals': int(true_count),
            'false_signals': int(false_count),
            'accuracy': float(report.get('accuracy', 0)),
            'weighted_f1': float(report.get('weighted avg', {}).get('f1-score', 0))
        }
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"\nModels saved:")
        print(f"  Classifier: {model_path}")
        print(f"  Scaler: {scaler_path}")
        print(f"  Config: {config_path}")
        
    except Exception as e:
        print(f"Error saving models: {e}")
        return False
    
    print("\n" + "="*80)
    print("TRAINING COMPLETED SUCCESSFULLY")
    print("="*80)
    print(f"\nNext steps:")
    print(f"1. Review the model performance metrics above")
    print(f"2. If accuracy > 0.55, model is ready for use")
    print(f"3. To use model in trading:")
    print(f"   - Load model from {model_path}")
    print(f"   - Use scaler from {scaler_path}")
    print(f"   - Filter signals with model.predict_proba()")
    print()
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

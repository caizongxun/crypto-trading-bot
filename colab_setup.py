#!/usr/bin/env python3
"""
Google Colab 設置腳本
自動安裝依賴並初始化環境
"""

import subprocess
import sys
import os

def setup_colab():
    """在 Colab 中進行初始化設置"""
    
    print("="*80)
    print("Google Colab 初始化設置")
    print("="*80)
    
    # 安裝 requirements
    print("\n正在安裝依賴套件...")
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", "-q",
        "pandas==2.1.4",
        "numpy==1.24.3",
        "scikit-learn==1.3.2",
        "xgboost==2.0.3",
        "torch==2.1.2",
        "huggingface-hub==0.20.3",
        "matplotlib==3.8.2",
        "seaborn==0.13.1",
        "pyarrow==14.0.1",
        "tqdm==4.66.1"
    ])
    
    print("✓ 依賴安裝完成")
    
    # 設置 HuggingFace 快取目錄
    hf_cache = "/content/hf_cache"
    os.makedirs(hf_cache, exist_ok=True)
    os.environ['HF_HOME'] = hf_cache
    
    print(f"✓ HuggingFace 快取目錄設置: {hf_cache}")
    
    print("\n" + "="*80)
    print("Colab 環境設置完成！")
    print("="*80)
    print("\n接下來可以執行：")
    print("  python index.py BTCUSDT 15m")
    print("  python test/indicator_test.py")
    print("  python test/visualization.py BTCUSDT 15m")
    print("\n")

if __name__ == "__main__":
    setup_colab()

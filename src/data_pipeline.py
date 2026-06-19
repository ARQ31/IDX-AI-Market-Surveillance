# ==============================================================
# IDX UMA — AI Market Surveillance Dashboard
# Live Data Pipeline
# ==============================================================
# Pipeline terpadu: fetch data → feature engineering → anomaly detection
# Dirancang untuk digunakan langsung oleh dashboard Streamlit
# dengan caching agar tidak fetch berulang kali.
# ==============================================================

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta, timezone
from typing import List
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler, MinMaxScaler

from src.config import (
    FEATURE_COLUMNS,
    ISOLATION_FOREST_PARAMS,
    ANOMALY_REASON_THRESHOLDS,
    RISK_THRESHOLDS,
    HISTORY_DAYS,
)


# =========================
# 1. Fetch Data dari Yahoo Finance
# =========================
def fetch_live_data(tickers: List[str], days: int = HISTORY_DAYS) -> pd.DataFrame:
    """
    Download data OHLCV untuk semua ticker dari Yahoo Finance.
    Mengembalikan DataFrame gabungan dengan kolom: date, open, high, low, close, volume, ticker.
    """
    # Selalu gunakan zona waktu WIB (UTC+7)
    wib_tz = timezone(timedelta(hours=7))
    current_wib = datetime.now(wib_tz)
    
    # Tambahkan 1 hari karena parameter `end` di yfinance bersifat eksklusif (tidak dihitung)
    end_date = current_wib + timedelta(days=1)
    start_date = current_wib - timedelta(days=days)

    all_data = []

    for ticker in tickers:
        try:
            stock = yf.download(
                ticker,
                start=start_date.strftime("%Y-%m-%d"),
                end=end_date.strftime("%Y-%m-%d"),
                auto_adjust=False,
                progress=False,
            )

            if stock.empty:
                continue

            # Handle MultiIndex columns dari yfinance
            if isinstance(stock.columns, pd.MultiIndex):
                stock.columns = stock.columns.get_level_values(0)

            stock = stock.reset_index()
            stock.columns = stock.columns.str.lower()

            stock = stock.rename(columns={
                "date": "date",
                "open": "open",
                "high": "high",
                "low": "low",
                "close": "close",
                "volume": "volume",
            })

            # Ambil kolom yang dibutuhkan
            stock = stock[["date", "open", "high", "low", "close", "volume"]].copy()

            # Ticker tanpa .JK
            stock["ticker"] = ticker.replace(".JK", "")

            all_data.append(stock)

        except Exception as e:
            print(f"Error downloading {ticker}: {e}")
            continue

    if not all_data:
        return pd.DataFrame()

    df = pd.concat(all_data, ignore_index=True)
    df["date"] = pd.to_datetime(df["date"])
    return df


# =========================
# 2. Feature Engineering
# =========================
def compute_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Menghitung 8 fitur teknikal untuk setiap saham.
    Logika sama dengan feature_engineering.py yang sudah ada.
    """
    if df.empty:
        return df

    numeric_columns = ["open", "high", "low", "close", "volume"]
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["date", "ticker"] + numeric_columns)
    df = df.sort_values(["ticker", "date"])

    all_stock_data = []

    for ticker in df["ticker"].unique():
        stock = df[df["ticker"] == ticker].copy()

        if len(stock) < 30:
            continue

        # Return harian
        stock["daily_return"] = stock["close"].pct_change(fill_method=None)

        # Perubahan volume harian
        stock["volume_change"] = stock["volume"].pct_change(fill_method=None)

        # Rata-rata volume 20 hari
        stock["volume_ma_20"] = stock["volume"].rolling(window=20).mean()

        # Rasio lonjakan volume dibanding rata-rata 20 hari
        stock["volume_spike_ratio"] = stock["volume"] / stock["volume_ma_20"]

        # Range harga harian dalam bentuk persentase
        stock["price_range_pct"] = (stock["high"] - stock["low"]) / stock["close"]

        # Moving average harga close 20 hari
        stock["close_ma_20"] = stock["close"].rolling(window=20).mean()

        # Selisih harga close terhadap moving average 20 hari
        stock["price_gap_ma_20"] = (stock["close"] - stock["close_ma_20"]) / stock["close_ma_20"]

        # Volatilitas return selama 20 hari
        stock["rolling_volatility_20"] = stock["daily_return"].rolling(window=20).std()

        # Z-score return
        return_mean = stock["daily_return"].rolling(window=20).mean()
        return_std = stock["daily_return"].rolling(window=20).std()
        stock["return_zscore_20"] = (stock["daily_return"] - return_mean) / return_std

        # Z-score volume
        volume_mean = stock["volume"].rolling(window=20).mean()
        volume_std = stock["volume"].rolling(window=20).std()
        stock["volume_zscore_20"] = (stock["volume"] - volume_mean) / volume_std

        all_stock_data.append(stock)

    if not all_stock_data:
        return pd.DataFrame()

    feature_df = pd.concat(all_stock_data)
    feature_df = feature_df.replace([np.inf, -np.inf], np.nan)
    feature_df = feature_df.dropna(subset=FEATURE_COLUMNS)

    return feature_df


# =========================
# 3. Anomaly Detection
# =========================
def _generate_anomaly_reason(row: pd.Series) -> str:
    """
    Menghasilkan penjelasan alasan anomali berdasarkan nilai fitur.
    """
    thresholds = ANOMALY_REASON_THRESHOLDS
    reason_list = []

    if row["volume_spike_ratio"] >= thresholds["volume_spike_ratio"]:
        reason_list.append(
            f"Volume {row['volume_spike_ratio']:.1f}x lebih tinggi dari rata-rata 20 hari"
        )

    if abs(row["daily_return"]) >= thresholds["daily_return_abs"]:
        direction = "naik" if row["daily_return"] > 0 else "turun"
        reason_list.append(
            f"Return harian {direction} {abs(row['daily_return']) * 100:.2f}%"
        )

    if row["price_range_pct"] >= thresholds["price_range_pct"]:
        reason_list.append(
            f"Range harga harian sebesar {row['price_range_pct'] * 100:.2f}%"
        )

    if abs(row["price_gap_ma_20"]) >= thresholds["price_gap_ma_20_abs"]:
        reason_list.append(
            f"Harga menyimpang {row['price_gap_ma_20'] * 100:.2f}% dari MA 20 hari"
        )

    if abs(row["return_zscore_20"]) >= thresholds["return_zscore_20_abs"]:
        reason_list.append(
            f"Return z-score mencapai {row['return_zscore_20']:.2f}"
        )

    if abs(row["volume_zscore_20"]) >= thresholds["volume_zscore_20_abs"]:
        reason_list.append(
            f"Volume z-score mencapai {row['volume_zscore_20']:.2f}"
        )

    if len(reason_list) == 0:
        reason_list.append("Kombinasi pergerakan harga dan volume terlihat tidak biasa")

    return "; ".join(reason_list)


def _classify_risk(score: float) -> str:
    """Klasifikasi tingkat risiko berdasarkan skor anomali ternormalisasi."""
    if score >= RISK_THRESHOLDS["high"]:
        return "Risiko Tinggi"
    elif score >= RISK_THRESHOLDS["medium"]:
        return "Risiko Sedang"
    elif score >= RISK_THRESHOLDS["low"]:
        return "Risiko Rendah"
    else:
        return "Normal"


def run_anomaly_detection(df: pd.DataFrame) -> pd.DataFrame:
    """
    Menjalankan Isolation Forest per ticker.
    Menghasilkan: anomaly_score, anomaly_score_normalized (0–1), risk_level, anomaly_reason.
    """
    if df.empty:
        return df

    all_results = []

    for ticker in df["ticker"].unique():
        stock = df[df["ticker"] == ticker].copy()

        if len(stock) < 60:
            stock["is_anomaly"] = False
            stock["anomaly_score"] = 0.0
            stock["anomaly_score_normalized"] = 0.0
            stock["risk_level"] = "Normal"
            stock["anomaly_reason"] = "Data belum cukup"
            all_results.append(stock)
            continue

        X = stock[FEATURE_COLUMNS]

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        model = IsolationForest(**ISOLATION_FOREST_PARAMS)
        prediction = model.fit_predict(X_scaled)

        stock["anomaly_label"] = prediction
        stock["is_anomaly"] = stock["anomaly_label"] == -1

        # Raw anomaly score (semakin tinggi = semakin anomali)
        raw_scores = -model.decision_function(X_scaled)
        stock["anomaly_score"] = raw_scores

        # Normalized score 0–1 per ticker menggunakan MinMaxScaler
        normalizer = MinMaxScaler(feature_range=(0, 1))
        stock["anomaly_score_normalized"] = normalizer.fit_transform(
            raw_scores.reshape(-1, 1)
        ).flatten()

        # Risk level classification
        stock["risk_level"] = stock["anomaly_score_normalized"].apply(_classify_risk)

        # Anomaly reasons
        reasons = []
        for _, row in stock.iterrows():
            if not row["is_anomaly"]:
                reasons.append("Normal")
            else:
                reasons.append(_generate_anomaly_reason(row))
        stock["anomaly_reason"] = reasons

        all_results.append(stock)

    if not all_results:
        return pd.DataFrame()

    return pd.concat(all_results, ignore_index=True)


# =========================
# 4. Pipeline Master (untuk dipanggil dari dashboard)
# =========================
def get_surveillance_data(tickers: List[str], days: int = HISTORY_DAYS) -> pd.DataFrame:
    """
    Pipeline lengkap: fetch → feature engineering → anomaly detection.
    Fungsi ini akan di-cache oleh Streamlit di dashboard.py.
    """
    # Step 1: Download data
    raw_df = fetch_live_data(tickers, days)

    if raw_df.empty:
        return pd.DataFrame()

    # Step 2: Feature engineering
    feature_df = compute_features(raw_df)

    if feature_df.empty:
        return pd.DataFrame()

    # Step 3: Anomaly detection
    result_df = run_anomaly_detection(feature_df)

    return result_df

# ==============================================================
# IDX UMA — AI Market Surveillance Dashboard
# Configuration Module
# ==============================================================

# Daftar saham default yang dipantau
DEFAULT_TICKERS = [
    "BBRI.JK",
    "BBCA.JK",
    "BMRI.JK",
    "TLKM.JK",
    "GOTO.JK",
    "ANTM.JK",
    "ADRO.JK",
    "BRIS.JK",
    "MDKA.JK",
    "UNVR.JK",
]

# Fitur yang digunakan oleh model Isolation Forest
FEATURE_COLUMNS = [
    "daily_return",
    "volume_change",
    "volume_spike_ratio",
    "price_range_pct",
    "price_gap_ma_20",
    "rolling_volatility_20",
    "return_zscore_20",
    "volume_zscore_20",
]

# Threshold untuk klasifikasi risk level berdasarkan anomaly score (0–1)
RISK_THRESHOLDS = {
    "high": 0.75,    # >= 0.75 → High Risk
    "medium": 0.50,  # >= 0.50 → Medium Risk
    "low": 0.25,     # >= 0.25 → Low Risk
    # < 0.25  → Normal
}

# Cache TTL: data di-refresh setiap 30 menit (dalam detik)
CACHE_TTL = 1800

# Auto-refresh interval: dashboard auto-reload setiap 5 menit (dalam milidetik)
AUTO_REFRESH_INTERVAL_MS = 300_000

# Berapa hari data historis yang diambil
HISTORY_DAYS = 180

# Parameter model Isolation Forest
ISOLATION_FOREST_PARAMS = {
    "n_estimators": 300,
    "contamination": 0.03,
    "random_state": 42,
}

# Threshold untuk menjelaskan alasan anomali
ANOMALY_REASON_THRESHOLDS = {
    "volume_spike_ratio": 3.0,
    "daily_return_abs": 0.05,
    "price_range_pct": 0.05,
    "price_gap_ma_20_abs": 0.08,
    "return_zscore_20_abs": 2.0,
    "volume_zscore_20_abs": 2.0,
}

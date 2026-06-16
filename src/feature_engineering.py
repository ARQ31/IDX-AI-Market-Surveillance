import pandas as pd
import numpy as np

# File input dan output
input_file = "data/idx_stock_price.csv"
output_file = "data/idx_stock_features.csv"

# Membaca data saham
df = pd.read_csv(input_file)

# Membuat nama kolom menjadi huruf kecil agar mudah dipakai
df.columns = df.columns.str.lower()

# Menampilkan nama kolom untuk cek awal
print("Kolom di dataset:")
print(df.columns)

# Mengubah kolom date menjadi format datetime
df["date"] = pd.to_datetime(df["date"], errors="coerce")

# Kolom angka yang harus dibersihkan
numeric_columns = ["open", "high", "low", "close", "volume"]

# Mengubah kolom angka dari string menjadi numeric
for column in numeric_columns:
    df[column] = pd.to_numeric(df[column], errors="coerce")

# Menghapus baris yang datanya tidak lengkap
df = df.dropna(subset=["date", "ticker", "open", "high", "low", "close", "volume"])

# Mengurutkan data berdasarkan ticker dan tanggal
df = df.sort_values(["ticker", "date"])

# List untuk menampung hasil fitur dari setiap saham
all_stock_data = []

# Membuat fitur untuk setiap ticker saham
for ticker in df["ticker"].unique():
    print("Processing:", ticker)

    stock = df[df["ticker"] == ticker].copy()

    # Kalau data saham terlalu sedikit, dilewati dulu
    if len(stock) < 30:
        print("Data terlalu sedikit, dilewati:", ticker)
        continue

    # Return harian
    # fill_method=None dipakai supaya tidak muncul warning dari pandas
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

# Menggabungkan semua data saham
feature_df = pd.concat(all_stock_data)

# Menghapus nilai infinity dan missing value
feature_df = feature_df.replace([np.inf, -np.inf], np.nan)
feature_columns = [
    "daily_return",
    "volume_change",
    "volume_spike_ratio",
    "price_range_pct",
    "price_gap_ma_20",
    "rolling_volatility_20",
    "return_zscore_20",
    "volume_zscore_20"
]

feature_df = feature_df.replace([np.inf, -np.inf], np.nan)
feature_df = feature_df.dropna(subset=feature_columns)

# Menyimpan hasil feature engineering
feature_df.to_csv(output_file, index=False)

print("Feature engineering selesai.")
print("File berhasil disimpan ke:", output_file)
print(feature_df.head())
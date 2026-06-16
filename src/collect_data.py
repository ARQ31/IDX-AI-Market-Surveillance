import yfinance as yf
import pandas as pd
import os

# Membuat folder data jika belum ada
os.makedirs("data", exist_ok=True)

# List saham yang ingin diambil datanya
tickers = [
    "BBRI.JK",
    "TLKM.JK",
    "BMRI.JK",
    "BBCA.JK",
    "ANTM.JK",
    "GOTO.JK",
    "ADRO.JK",
    "MDKA.JK",
    "BRIS.JK",
    "UNVR.JK"
]

all_data = []

for ticker in tickers:
    print("Downloading:", ticker)

    # Download data satu per satu agar formatnya tidak berantakan
    stock = yf.download(
        ticker,
        start="2023-01-01",
        end="2026-06-17",
        auto_adjust=False,
        progress=False
    )

    # Kalau data kosong, lewati
    if stock.empty:
        print("Data kosong:", ticker)
        continue

    # Jika kolom dari yfinance berbentuk MultiIndex, ambil level pertama saja
    if isinstance(stock.columns, pd.MultiIndex):
        stock.columns = stock.columns.get_level_values(0)

    # Reset index agar Date menjadi kolom biasa
    stock = stock.reset_index()

    # Samakan nama kolom menjadi huruf kecil
    stock.columns = stock.columns.str.lower()

    # Rename kolom agar konsisten
    stock = stock.rename(columns={
        "date": "date",
        "open": "open",
        "high": "high",
        "low": "low",
        "close": "close",
        "volume": "volume"
    })

    # Ambil kolom yang dibutuhkan saja
    stock = stock[["date", "open", "high", "low", "close", "volume"]]

    # Tambahkan kode saham tanpa .JK
    stock["ticker"] = ticker.replace(".JK", "")

    all_data.append(stock)

# Gabungkan semua data saham
final_data = pd.concat(all_data, ignore_index=True)

# Simpan ke CSV
final_data.to_csv("data/idx_stock_price.csv", index=False)

print("Data berhasil disimpan ke data/idx_stock_price.csv")
print(final_data.head())
print(final_data.columns)
print(final_data.shape)
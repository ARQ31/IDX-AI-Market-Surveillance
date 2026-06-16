import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# File input dan output
input_file = "data/idx_stock_features.csv"
output_file = "data/idx_stock_anomaly_result.csv"
top_anomaly_file = "data/top_anomalies.csv"

# Membaca data hasil feature engineering
df = pd.read_csv(input_file)

# Mengubah date menjadi datetime
df["date"] = pd.to_datetime(df["date"])

# Fitur yang digunakan untuk mendeteksi anomali
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

# List untuk menyimpan hasil semua saham
all_results = []

# Model dijalankan per saham
for ticker in df["ticker"].unique():
    print("Detecting anomaly for:", ticker)

    stock = df[df["ticker"] == ticker].copy()

    # Jika data terlalu sedikit, model tidak dijalankan
    if len(stock) < 60:
        stock["is_anomaly"] = False
        stock["anomaly_score"] = 0
        stock["anomaly_reason"] = "Data belum cukup"
        all_results.append(stock)
        continue

    # Mengambil fitur untuk model
    X = stock[feature_columns]

    # Scaling data agar semua fitur memiliki skala yang seimbang
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Membuat model Isolation Forest
    # contamination 0.03 artinya sekitar 3% data dianggap anomali
    model = IsolationForest(
        n_estimators=300,
        contamination=0.03,
        random_state=42
    )

    # Melatih model dan membuat prediksi
    prediction = model.fit_predict(X_scaled)

    # Dalam Isolation Forest:
    # 1 berarti normal
    # -1 berarti anomali
    stock["anomaly_label"] = prediction
    stock["is_anomaly"] = stock["anomaly_label"] == -1

    # Semakin besar score ini, semakin tidak biasa datanya
    stock["anomaly_score"] = -model.decision_function(X_scaled)

    # Membuat alasan sederhana kenapa data dianggap anomali
    reasons = []

    for index, row in stock.iterrows():
        if row["is_anomaly"] == False:
            reasons.append("Normal")
        else:
            reason_list = []

            if row["volume_spike_ratio"] >= 3:
                reason_list.append(
                    f"Volume {row['volume_spike_ratio']:.1f}x lebih tinggi dari rata-rata 20 hari"
                )

            if abs(row["daily_return"]) >= 0.05:
                reason_list.append(
                    f"Return harian bergerak {row['daily_return'] * 100:.2f}%"
                )

            if row["price_range_pct"] >= 0.05:
                reason_list.append(
                    f"Range harga harian sebesar {row['price_range_pct'] * 100:.2f}%"
                )

            if abs(row["price_gap_ma_20"]) >= 0.08:
                reason_list.append(
                    f"Harga menyimpang {row['price_gap_ma_20'] * 100:.2f}% dari MA 20 hari"
                )

            if abs(row["return_zscore_20"]) >= 2:
                reason_list.append(
                    f"Return z-score mencapai {row['return_zscore_20']:.2f}"
                )

            if abs(row["volume_zscore_20"]) >= 2:
                reason_list.append(
                    f"Volume z-score mencapai {row['volume_zscore_20']:.2f}"
                )

            if len(reason_list) == 0:
                reason_list.append("Kombinasi pergerakan harga dan volume terlihat tidak biasa")

            reasons.append("; ".join(reason_list))

    stock["anomaly_reason"] = reasons

    all_results.append(stock)

# Menggabungkan semua hasil saham
result_df = pd.concat(all_results)

# Menyimpan hasil lengkap
result_df.to_csv(output_file, index=False)

# Mengambil hanya data yang anomali
top_anomalies = result_df[result_df["is_anomaly"] == True].copy()

# Mengurutkan berdasarkan anomaly score terbesar
top_anomalies = top_anomalies.sort_values("anomaly_score", ascending=False)

# Menyimpan data top anomaly
top_anomalies.to_csv(top_anomaly_file, index=False)

print("Anomaly detection selesai.")
print("File hasil lengkap disimpan ke:", output_file)
print("File top anomaly disimpan ke:", top_anomaly_file)

print("\nTop 10 anomaly:")
print(
    top_anomalies[
        [
            "date",
            "ticker",
            "close",
            "volume",
            "daily_return",
            "volume_spike_ratio",
            "anomaly_score",
            "anomaly_reason"
        ]
    ].head(10)
)
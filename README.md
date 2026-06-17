# 🛡️ IDX AI Market Surveillance Dashboard

Sistem pemantauan pasar saham Indonesia (Bursa Efek Indonesia) berbasis Artificial Intelligence (AI) untuk mendeteksi pergerakan harga dan volume yang tidak biasa secara real-time. Proyek ini terinspirasi dari konsep **Unusual Market Activity (UMA)** yang diterapkan oleh otoritas bursa.

Dashboard ini menggunakan **Isolation Forest** (algoritma *unsupervised machine learning*) untuk mendeteksi anomali pada pergerakan saham berdasarkan data historis dan teknikal.

---

## ✨ Fitur Utama

- **📡 Live Data Pipeline**: Mengambil data saham secara langsung dari Yahoo Finance (`yfinance`) dan memprosesnya secara *real-time* tanpa perlu menjalankan skrip pengumpulan data secara manual.
- **🤖 AI Anomaly Detection**: Menggunakan model *Isolation Forest* untuk menghasilkan skor anomali (0.00 hingga 1.00) dan mengklasifikasikan risiko saham menjadi *Normal, Low Risk, Medium Risk*, dan *High Risk*.
- **📊 Market Risk Heatmap**: Visualisasi peta risiko pasar secara interaktif untuk melihat saham mana yang sedang mengalami pergerakan paling ekstrem hari ini.
- **🔍 Analisis Saham Mendalam**: Halaman khusus untuk melihat grafik interaktif (Candlestick & Volume) dengan penanda (marker) yang secara presisi menunjukkan kapan anomali terjadi.
- **⚡ Auto-Refresh**: Dashboard otomatis memperbarui data setiap 5 menit untuk memastikan Anda selalu melihat kondisi pasar terbaru.

---

## 🛠️ Arsitektur Sistem

Proyek ini telah di-upgrade menjadi sistem pipeline langsung (live pipeline):
- `src/config.py`: Konfigurasi terpusat (daftar ticker saham, parameter model, threshold risiko).
- `src/data_pipeline.py`: Pipeline gabungan untuk *Data Fetching*, *Feature Engineering*, dan *Anomaly Detection*.
- `dashboard.py`: Aplikasi utama Streamlit (Multi-page dashboard).
- *Catatan: Skrip offline lama (`collect_data.py`, `feature_engineering.py`, `anomaly_model.py`) tetap dipertahankan untuk kebutuhan pemrosesan data secara batch/offline.*

---

## 📐 Fitur Teknikal yang Dianalisis

Sistem ini menghitung 8 indikator untuk setiap saham sebelum dimasukkan ke dalam model AI:
1. **Daily Return** (Perubahan harga harian)
2. **Volume Change** (Perubahan volume harian)
3. **Volume Spike Ratio** (Lonjakan volume dibanding rata-rata 20 hari)
4. **Price Range Percentage** (Jarak level High dan Low)
5. **Price Gap MA20** (Deviasi harga dari Moving Average 20 hari)
6. **Rolling Volatility 20** (Volatilitas selama 20 hari terakhir)
7. **Return Z-Score** (Seberapa ekstrem return dibandingkan pola normalnya)
8. **Volume Z-Score** (Seberapa ekstrem volume dibandingkan pola normalnya)

---

## 🚀 Panduan Instalasi dan Penggunaan

### Akses via Streamlit Community Cloud (Live Dashboard)
Anda dapat langsung mengakses dashboard ini secara online tanpa perlu melakukan instalasi di komputer Anda. Klik tautan berikut:

👉 **[Live Dashboard: IDX AI Market Surveillance](https://idx-ai-market-surveillance.streamlit.app/)** 

*(Catatan: Ganti URL di atas dengan link hasil deploy Anda di Streamlit Community)*

---

### Menjalankan di Komputer Lokal (Localhost)

#### 1. Persyaratan Sistem
Pastikan Anda menggunakan **Python 3.8** atau yang lebih baru.

### 2. Instalasi Dependensi
Buka terminal dan jalankan perintah berikut untuk menginstal semua *library* yang dibutuhkan:
```bash
pip install -r requirements.txt
```

### 3. Menjalankan Dashboard
Setelah proses instalasi selesai, jalankan Streamlit dengan perintah:
```bash
streamlit run dashboard.py
```
Aplikasi akan secara otomatis terbuka di browser Anda (biasanya pada `http://localhost:8501`).

---

## ⚙️ Konfigurasi (Opsional)

Anda dapat mengubah pengaturan sistem melalui file `src/config.py`:
- **Mengubah Saham Default**: Tambahkan atau kurangi kode saham pada list `DEFAULT_TICKERS`. Pastikan Anda menambahkan akhiran `.JK` untuk saham BEI (contoh: `BBRI.JK`).
- **Jendela Historis**: Ubah variabel `HISTORY_DAYS` (default 180 hari) untuk mengubah seberapa panjang data ke belakang yang digunakan model untuk mempelajari "pola normal" pasar.

Selain itu, Anda juga dapat menambahkan ticker saham secara langsung melalui bilah samping (sidebar) saat membuka Dashboard di browser.

---

## ⚠️ Disclaimer
**Bukan Rekomendasi Investasi.** 
Dashboard ini dibuat murni untuk **tujuan edukasi, riset, dan portofolio**. Hasil deteksi anomali (High Risk, dll) bukan merupakan rekomendasi untuk membeli, menjual, atau menahan saham tertentu. Sistem ini tidak menyatakan secara pasti adanya manipulasi pasar (cornering/pump & dump), melainkan hanya mendeteksi bahwa pola harga dan volume saat ini "berbeda secara statistik" dari pola normal historisnya. Segala keputusan investasi sepenuhnya menjadi tanggung jawab masing-masing individu.

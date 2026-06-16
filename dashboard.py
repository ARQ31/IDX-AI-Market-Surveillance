import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# =========================
# Konfigurasi halaman
# =========================
st.set_page_config(
    page_title="IDX UMA Early Warning System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# Custom CSS untuk tampilan premium
# =========================
st.markdown("""
<style>
    /* ===== Import Google Fonts ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ===== Root Variables ===== */
    :root {
        --primary: #6C5CE7;
        --primary-light: #A29BFE;
        --accent: #00CEC9;
        --accent-warm: #FDCB6E;
        --danger: #FF6B6B;
        --danger-light: #FF8A8A;
        --surface: #1E1E2E;
        --surface-light: #2A2A3E;
        --surface-lighter: #363652;
        --text-primary: #E8E8F0;
        --text-secondary: #A0A0B8;
        --border: rgba(108, 92, 231, 0.2);
        --shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        --gradient-primary: linear-gradient(135deg, #6C5CE7 0%, #A29BFE 100%);
        --gradient-accent: linear-gradient(135deg, #00CEC9 0%, #55EFC4 100%);
        --gradient-hero: linear-gradient(135deg, #0F0C29 0%, #302B63 50%, #24243E 100%);
    }

    /* ===== Global ===== */
    .stApp {
        font-family: 'Inter', sans-serif !important;
    }

    /* ===== Hero Header ===== */
    .hero-container {
        background: var(--gradient-hero);
        border-radius: 20px;
        padding: 2.5rem 3rem;
        margin-bottom: 2rem;
        border: 1px solid var(--border);
        position: relative;
        overflow: hidden;
    }

    .hero-container::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(108, 92, 231, 0.15) 0%, transparent 70%);
        border-radius: 50%;
    }

    .hero-container::after {
        content: '';
        position: absolute;
        bottom: -40%;
        left: -10%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(0, 206, 201, 0.1) 0%, transparent 70%);
        border-radius: 50%;
    }

    .hero-badge {
        display: inline-block;
        background: rgba(108, 92, 231, 0.2);
        border: 1px solid rgba(108, 92, 231, 0.4);
        padding: 0.3rem 1rem;
        border-radius: 50px;
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--primary-light);
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 1rem;
    }

    .hero-title {
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #FFFFFF 0%, #A29BFE 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0 0 0.3rem 0;
        line-height: 1.2;
        position: relative;
        z-index: 1;
    }

    .hero-subtitle {
        font-size: 1.1rem;
        color: var(--text-secondary);
        font-weight: 400;
        margin: 0 0 1.5rem 0;
        position: relative;
        z-index: 1;
    }

    .hero-description {
        font-size: 0.92rem;
        color: var(--text-secondary);
        line-height: 1.7;
        max-width: 800px;
        position: relative;
        z-index: 1;
    }

    /* ===== Disclaimer Box ===== */
    .disclaimer-box {
        background: linear-gradient(135deg, rgba(253, 203, 110, 0.08) 0%, rgba(255, 107, 107, 0.08) 100%);
        border: 1px solid rgba(253, 203, 110, 0.3);
        border-left: 4px solid var(--accent-warm);
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin-bottom: 2rem;
    }

    .disclaimer-title {
        font-size: 0.8rem;
        font-weight: 700;
        color: var(--accent-warm);
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .disclaimer-text {
        font-size: 0.85rem;
        color: var(--text-secondary);
        line-height: 1.6;
        margin: 0;
    }

    /* ===== KPI Cards ===== */
    .kpi-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    .kpi-card:hover {
        transform: translateY(-4px);
        border-color: rgba(108, 92, 231, 0.5);
        box-shadow: 0 12px 40px rgba(108, 92, 231, 0.15);
    }

    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        border-radius: 16px 16px 0 0;
    }

    .kpi-card.purple::before { background: var(--gradient-primary); }
    .kpi-card.teal::before { background: var(--gradient-accent); }
    .kpi-card.red::before { background: linear-gradient(135deg, #FF6B6B 0%, #FF8A8A 100%); }
    .kpi-card.gold::before { background: linear-gradient(135deg, #FDCB6E 0%, #FFEAA7 100%); }

    .kpi-icon {
        font-size: 1.8rem;
        margin-bottom: 0.5rem;
    }

    .kpi-label {
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }

    .kpi-value {
        font-size: 1.6rem;
        font-weight: 800;
        color: var(--text-primary);
    }

    .kpi-value.purple { color: var(--primary-light); }
    .kpi-value.teal { color: var(--accent); }
    .kpi-value.red { color: var(--danger-light); }
    .kpi-value.gold { color: var(--accent-warm); }

    /* ===== Section Headers ===== */
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin: 2.5rem 0 1rem 0;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid var(--border);
    }

    .section-header-icon {
        font-size: 1.4rem;
    }

    .section-header-text {
        font-size: 1.2rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
    }

    .section-header-badge {
        display: inline-block;
        background: rgba(108, 92, 231, 0.15);
        color: var(--primary-light);
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-size: 0.7rem;
        font-weight: 600;
        margin-left: auto;
    }

    /* ===== Data Table Styling ===== */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }

    /* ===== Info Box (How It Works) ===== */
    .info-box {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 2rem;
        margin-top: 1rem;
    }

    .info-box h4 {
        color: var(--primary-light);
        font-weight: 700;
        margin-bottom: 1rem;
        font-size: 1rem;
    }

    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 0.8rem;
    }

    .feature-item {
        display: flex;
        align-items: flex-start;
        gap: 0.6rem;
        padding: 0.7rem 1rem;
        background: var(--surface-light);
        border-radius: 10px;
        border: 1px solid rgba(108, 92, 231, 0.1);
        transition: all 0.2s ease;
    }

    .feature-item:hover {
        border-color: rgba(108, 92, 231, 0.3);
        background: var(--surface-lighter);
    }

    .feature-dot {
        width: 8px;
        height: 8px;
        background: var(--accent);
        border-radius: 50%;
        margin-top: 6px;
        flex-shrink: 0;
    }

    .feature-name {
        font-weight: 600;
        color: var(--text-primary);
        font-size: 0.85rem;
    }

    .feature-desc {
        color: var(--text-secondary);
        font-size: 0.8rem;
    }

    .model-box {
        background: linear-gradient(135deg, rgba(108, 92, 231, 0.1) 0%, rgba(0, 206, 201, 0.05) 100%);
        border: 1px solid rgba(108, 92, 231, 0.25);
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin-top: 1.5rem;
    }

    .model-box-title {
        font-weight: 700;
        color: var(--primary-light);
        font-size: 0.9rem;
        margin-bottom: 0.4rem;
    }

    .model-box-text {
        color: var(--text-secondary);
        font-size: 0.85rem;
        line-height: 1.6;
    }

    /* ===== Footer ===== */
    .footer {
        text-align: center;
        padding: 2rem 0 1rem 0;
        margin-top: 3rem;
        border-top: 1px solid var(--border);
        color: var(--text-secondary);
        font-size: 0.8rem;
    }

    .footer a {
        color: var(--primary-light);
        text-decoration: none;
    }

    /* ===== Sidebar Styling ===== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1A1A2E 0%, #16213E 100%);
    }

    [data-testid="stSidebar"] .stMarkdown h2 {
        color: var(--primary-light) !important;
    }

    .sidebar-brand {
        text-align: center;
        padding: 1rem 0 1.5rem 0;
        border-bottom: 1px solid var(--border);
        margin-bottom: 1.5rem;
    }

    .sidebar-brand-icon {
        font-size: 2.5rem;
        margin-bottom: 0.3rem;
    }

    .sidebar-brand-name {
        font-size: 1rem;
        font-weight: 700;
        color: var(--text-primary);
    }

    .sidebar-brand-version {
        font-size: 0.7rem;
        color: var(--text-secondary);
        margin-top: 0.2rem;
    }

    /* ===== Animations ===== */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .hero-container, .kpi-card, .info-box, .disclaimer-box {
        animation: fadeInUp 0.6s ease-out forwards;
    }

    .kpi-card:nth-child(2) { animation-delay: 0.1s; }
    .kpi-card:nth-child(3) { animation-delay: 0.2s; }
    .kpi-card:nth-child(4) { animation-delay: 0.3s; }

    /* ===== Success / Warning ===== */
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.4rem 1rem;
        border-radius: 50px;
        font-size: 0.85rem;
        font-weight: 600;
    }

    .status-pill.success {
        background: rgba(0, 206, 201, 0.15);
        color: #55EFC4;
        border: 1px solid rgba(0, 206, 201, 0.3);
    }

    .status-pill.warning {
        background: rgba(255, 107, 107, 0.15);
        color: var(--danger-light);
        border: 1px solid rgba(255, 107, 107, 0.3);
    }
</style>
""", unsafe_allow_html=True)


# =========================
# Plotly dark theme template
# =========================
PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(30,30,46,0)",
    plot_bgcolor="rgba(30,30,46,0.5)",
    font=dict(family="Inter, sans-serif", color="#A0A0B8"),
    xaxis=dict(
        gridcolor="rgba(108,92,231,0.1)",
        zerolinecolor="rgba(108,92,231,0.15)",
    ),
    yaxis=dict(
        gridcolor="rgba(108,92,231,0.1)",
        zerolinecolor="rgba(108,92,231,0.15)",
    ),
    hoverlabel=dict(
        bgcolor="#2A2A3E",
        font_size=13,
        font_family="Inter, sans-serif",
        bordercolor="#6C5CE7",
    ),
    margin=dict(l=20, r=20, t=40, b=20),
    legend=dict(
        bgcolor="rgba(30,30,46,0.8)",
        bordercolor="rgba(108,92,231,0.2)",
        borderwidth=1,
        font=dict(size=12),
    ),
)

# =========================
# Membaca data
# =========================
data_file = "data/idx_stock_anomaly_result.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(data_file)
    df["date"] = pd.to_datetime(df["date"])
    return df

df = load_data()

# =========================
# Sidebar
# =========================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div class="sidebar-brand-icon">📊</div>
        <div class="sidebar-brand-name">IDX UMA</div>
        <div class="sidebar-brand-version">Early Warning System v1.0</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("## 🔍 Filter Data")

    ticker_list = sorted(df["ticker"].unique())

    selected_ticker = st.selectbox(
        "Pilih kode saham",
        ticker_list,
        help="Pilih salah satu kode saham yang tersedia"
    )

    min_date = df["date"].min().date()
    max_date = df["date"].max().date()

    selected_date_range = st.date_input(
        "Pilih rentang tanggal",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        help="Filter data berdasarkan periode waktu"
    )

    st.markdown("---")
    st.markdown(
        f"<div style='text-align:center; font-size:0.75rem; color:#A0A0B8;'>"
        f"📈 Total <b>{len(ticker_list)}</b> saham tersedia<br>"
        f"📅 Data: <b>{min_date}</b> — <b>{max_date}</b>"
        f"</div>",
        unsafe_allow_html=True
    )

# Untuk menghindari error jika user hanya memilih satu tanggal
if len(selected_date_range) == 2:
    start_date = pd.to_datetime(selected_date_range[0])
    end_date = pd.to_datetime(selected_date_range[1])
else:
    start_date = pd.to_datetime(min_date)
    end_date = pd.to_datetime(max_date)

# Filter data berdasarkan ticker dan tanggal
stock_df = df[
    (df["ticker"] == selected_ticker) &
    (df["date"] >= start_date) &
    (df["date"] <= end_date)
].copy()

# Data anomaly saja
anomaly_df = stock_df[stock_df["is_anomaly"] == True].copy()


# =========================
# Hero Header
# =========================
st.markdown("""
<div class="hero-container">
    <div class="hero-badge">🛡️ Anomaly Detection System</div>
    <h1 class="hero-title">IDX UMA Early Warning System</h1>
    <p class="hero-subtitle">Unusual Market Activity Detection — Bursa Efek Indonesia</p>
    <p class="hero-description">
        Sistem peringatan dini untuk mendeteksi pergerakan harga dan volume saham yang tidak biasa
        di pasar saham Indonesia. Menggunakan algoritma <strong style="color:#A29BFE;">Isolation Forest</strong> 
        untuk menganalisis pola perdagangan dan mengidentifikasi aktivitas yang menyimpang dari kondisi normal, 
        terinspirasi dari konsep <strong style="color:#00CEC9;">Unusual Market Activity (UMA)</strong> 
        yang diterapkan oleh Bursa Efek Indonesia.
    </p>
</div>
""", unsafe_allow_html=True)


# =========================
# Disclaimer
# =========================
st.markdown("""
<div class="disclaimer-box">
    <div class="disclaimer-title">⚠️ Disclaimer — Bukan Rekomendasi Investasi</div>
    <p class="disclaimer-text">
        Dashboard ini dibuat murni untuk <strong>tujuan edukasi dan riset</strong>. 
        Hasil deteksi anomali bukan merupakan rekomendasi untuk membeli, menjual, atau menahan saham tertentu. 
        Sistem ini <strong>tidak menyatakan adanya manipulasi pasar</strong> dan hanya mendeteksi pola harga serta volume 
        yang terlihat tidak biasa berdasarkan data historis. Segala keputusan investasi sepenuhnya menjadi tanggung jawab 
        masing-masing individu. Selalu lakukan riset mandiri dan/atau konsultasi dengan penasihat keuangan profesional 
        sebelum mengambil keputusan investasi.
    </p>
</div>
""", unsafe_allow_html=True)


# =========================
# Jika data kosong
# =========================
if stock_df.empty:
    st.warning("⚠️ Data tidak tersedia untuk filter yang dipilih.")
    st.stop()


# =========================
# KPI Cards
# =========================
latest_data = stock_df.sort_values("date").iloc[-1]

latest_close = latest_data["close"]
total_anomaly = anomaly_df.shape[0]

if total_anomaly > 0:
    latest_anomaly_date = str(anomaly_df["date"].max().date())
else:
    latest_anomaly_date = "—"

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="kpi-card purple">
        <div class="kpi-icon">🏷️</div>
        <div class="kpi-label">Kode Saham</div>
        <div class="kpi-value purple">{selected_ticker}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card teal">
        <div class="kpi-icon">💰</div>
        <div class="kpi-label">Harga Close Terakhir</div>
        <div class="kpi-value teal">Rp {latest_close:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card red">
        <div class="kpi-icon">🚨</div>
        <div class="kpi-label">Total Anomaly</div>
        <div class="kpi-value red">{total_anomaly}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card gold">
        <div class="kpi-icon">📅</div>
        <div class="kpi-label">Anomaly Terakhir</div>
        <div class="kpi-value gold">{latest_anomaly_date}</div>
    </div>
    """, unsafe_allow_html=True)


# =========================
# Candlestick Chart
# =========================
st.markdown("""
<div class="section-header">
    <span class="section-header-icon">🕯️</span>
    <span class="section-header-text">Candlestick Chart dengan Titik Anomaly</span>
    <span class="section-header-badge">INTERACTIVE</span>
</div>
""", unsafe_allow_html=True)

fig_price = go.Figure()

# Warna candlestick
bullish_color = "#55EFC4"
bearish_color = "#FF6B6B"

fig_price.add_trace(
    go.Candlestick(
        x=stock_df["date"],
        open=stock_df["open"],
        high=stock_df["high"],
        low=stock_df["low"],
        close=stock_df["close"],
        name="OHLC",
        increasing_line_color=bullish_color,
        decreasing_line_color=bearish_color,
        increasing_fillcolor=bullish_color,
        decreasing_fillcolor=bearish_color,
    )
)

fig_price.add_trace(
    go.Scatter(
        x=anomaly_df["date"],
        y=anomaly_df["close"],
        mode="markers",
        marker=dict(
            size=12,
            color="#FDCB6E",
            symbol="diamond",
            line=dict(width=2, color="#E17055"),
        ),
        name="⚠ Anomaly",
    )
)

fig_price.update_layout(
    **PLOTLY_LAYOUT,
    xaxis_title="Tanggal",
    yaxis_title="Harga (Rp)",
    height=550,
    xaxis_rangeslider_visible=False,
    title=dict(
        text=f"Pergerakan Harga {selected_ticker}",
        font=dict(size=16, color="#E8E8F0"),
        x=0,
    ),
)

st.plotly_chart(fig_price, use_container_width=True)


# =========================
# Volume Chart
# =========================
st.markdown("""
<div class="section-header">
    <span class="section-header-icon">📊</span>
    <span class="section-header-text">Volume Perdagangan</span>
</div>
""", unsafe_allow_html=True)

fig_volume = go.Figure()

# Warna volume bar berdasarkan apakah anomaly atau tidak
volume_colors = [
    "#FF6B6B" if row["is_anomaly"] else "rgba(108,92,231,0.5)"
    for _, row in stock_df.iterrows()
]

fig_volume.add_trace(
    go.Bar(
        x=stock_df["date"],
        y=stock_df["volume"],
        name="Volume",
        marker=dict(
            color=volume_colors,
            line=dict(width=0),
        ),
        opacity=0.85,
    )
)

fig_volume.add_trace(
    go.Scatter(
        x=anomaly_df["date"],
        y=anomaly_df["volume"],
        mode="markers",
        marker=dict(
            size=10,
            color="#FDCB6E",
            symbol="diamond",
            line=dict(width=2, color="#E17055"),
        ),
        name="⚠ Anomaly Volume",
    )
)

fig_volume.update_layout(
    **PLOTLY_LAYOUT,
    xaxis_title="Tanggal",
    yaxis_title="Volume",
    height=350,
    title=dict(
        text=f"Volume Perdagangan {selected_ticker}",
        font=dict(size=16, color="#E8E8F0"),
        x=0,
    ),
)

st.plotly_chart(fig_volume, use_container_width=True)


# =========================
# Tabel Anomaly
# =========================
st.markdown(f"""
<div class="section-header">
    <span class="section-header-icon">📋</span>
    <span class="section-header-text">Daftar Tanggal Terdeteksi Anomaly — {selected_ticker}</span>
    <span class="section-header-badge">{total_anomaly} RECORDS</span>
</div>
""", unsafe_allow_html=True)

if anomaly_df.empty:
    st.markdown("""
    <div class="status-pill success">✅ Tidak ada anomaly terdeteksi pada saham dan rentang tanggal ini</div>
    """, unsafe_allow_html=True)
else:
    anomaly_table = anomaly_df[
        [
            "date",
            "ticker",
            "close",
            "volume",
            "daily_return",
            "volume_spike_ratio",
            "price_range_pct",
            "anomaly_score",
            "anomaly_reason"
        ]
    ].copy()

    anomaly_table["date"] = anomaly_table["date"].dt.date
    anomaly_table["daily_return"] = anomaly_table["daily_return"] * 100
    anomaly_table["price_range_pct"] = anomaly_table["price_range_pct"] * 100

    anomaly_table = anomaly_table.rename(columns={
        "date": "📅 Date",
        "ticker": "🏷️ Ticker",
        "close": "💰 Close Price",
        "volume": "📊 Volume",
        "daily_return": "📈 Daily Return (%)",
        "volume_spike_ratio": "⚡ Vol. Spike Ratio",
        "price_range_pct": "📐 Price Range (%)",
        "anomaly_score": "🎯 Anomaly Score",
        "anomaly_reason": "📝 Anomaly Reason"
    })

    anomaly_table = anomaly_table.sort_values("🎯 Anomaly Score", ascending=False)

    st.dataframe(
        anomaly_table,
        use_container_width=True,
        hide_index=True,
    )


# =========================
# Top anomaly dari semua saham
# =========================
st.markdown("""
<div class="section-header">
    <span class="section-header-icon">🏆</span>
    <span class="section-header-text">Top 10 Anomaly dari Seluruh Saham</span>
    <span class="section-header-badge">ALL TICKERS</span>
</div>
""", unsafe_allow_html=True)

top_all = df[df["is_anomaly"] == True].copy()
top_all = top_all.sort_values("anomaly_score", ascending=False).head(10)

top_all_table = top_all[
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
].copy()

top_all_table["date"] = top_all_table["date"].dt.date
top_all_table["daily_return"] = top_all_table["daily_return"] * 100

top_all_table = top_all_table.rename(columns={
    "date": "📅 Date",
    "ticker": "🏷️ Ticker",
    "close": "💰 Close Price",
    "volume": "📊 Volume",
    "daily_return": "📈 Daily Return (%)",
    "volume_spike_ratio": "⚡ Vol. Spike Ratio",
    "anomaly_score": "🎯 Anomaly Score",
    "anomaly_reason": "📝 Anomaly Reason"
})

st.dataframe(
    top_all_table,
    use_container_width=True,
    hide_index=True,
)


# =========================
# Penjelasan fitur (How It Works)
# =========================
st.markdown("""
<div class="section-header">
    <span class="section-header-icon">⚙️</span>
    <span class="section-header-text">Bagaimana Sistem Ini Bekerja</span>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
    <h4>📐 Fitur yang Digunakan untuk Deteksi Anomali</h4>
    <div class="feature-grid">
        <div class="feature-item">
            <div class="feature-dot"></div>
            <div>
                <span class="feature-name">Daily Return</span><br>
                <span class="feature-desc">Perubahan harga close dari hari sebelumnya</span>
            </div>
        </div>
        <div class="feature-item">
            <div class="feature-dot"></div>
            <div>
                <span class="feature-name">Volume Change</span><br>
                <span class="feature-desc">Perubahan volume dari hari sebelumnya</span>
            </div>
        </div>
        <div class="feature-item">
            <div class="feature-dot"></div>
            <div>
                <span class="feature-name">Volume Spike Ratio</span><br>
                <span class="feature-desc">Perbandingan volume hari ini dengan rata-rata 20 hari</span>
            </div>
        </div>
        <div class="feature-item">
            <div class="feature-dot"></div>
            <div>
                <span class="feature-name">Price Range Percentage</span><br>
                <span class="feature-desc">Selisih high dan low dibanding harga close</span>
            </div>
        </div>
        <div class="feature-item">
            <div class="feature-dot"></div>
            <div>
                <span class="feature-name">Price Gap MA 20</span><br>
                <span class="feature-desc">Jarak harga close terhadap moving average 20 hari</span>
            </div>
        </div>
        <div class="feature-item">
            <div class="feature-dot"></div>
            <div>
                <span class="feature-name">Rolling Volatility 20</span><br>
                <span class="feature-desc">Volatilitas return selama 20 hari terakhir</span>
            </div>
        </div>
        <div class="feature-item">
            <div class="feature-dot"></div>
            <div>
                <span class="feature-name">Return Z-score</span><br>
                <span class="feature-desc">Seberapa ekstrem return dibanding pola 20 hari terakhir</span>
            </div>
        </div>
        <div class="feature-item">
            <div class="feature-dot"></div>
            <div>
                <span class="feature-name">Volume Z-score</span><br>
                <span class="feature-desc">Seberapa ekstrem volume dibanding pola 20 hari terakhir</span>
            </div>
        </div>
    </div>

    <div class="model-box">
        <div class="model-box-title">🤖 Model: Isolation Forest</div>
        <div class="model-box-text">
            Model yang digunakan adalah <strong>Isolation Forest</strong>, yaitu algoritma unsupervised learning
            yang mendeteksi data yang berbeda dari pola normal. Algoritma ini bekerja dengan cara mengisolasi
            observasi — data yang lebih mudah diisolasi dianggap sebagai anomali. Dalam project ini, data yang
            teridentifikasi menyimpang dari pola perdagangan normal diberi label sebagai <strong>anomaly</strong>.
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# =========================
# Footer
# =========================
st.markdown("""
<div class="footer">
    <p>
        <strong style="color:#A29BFE;">IDX UMA Early Warning System</strong> — 
        Dibuat untuk tujuan edukasi & riset<br>
        Data bersumber dari Yahoo Finance • Tidak terafiliasi dengan Bursa Efek Indonesia
    </p>
</div>
""", unsafe_allow_html=True)
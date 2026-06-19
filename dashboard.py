# ==============================================================
# IDX UMA — Dasbor Pemantauan Pasar Berbasis AI
# Pemantauan pasar secara real-time untuk saham Indonesia
# ==============================================================

import streamlit as st
import pandas as pd
import numpy as np
import base64
import os
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta, timezone
from streamlit_autorefresh import st_autorefresh

from src.config import (
    DEFAULT_TICKERS,
    CACHE_TTL,
    AUTO_REFRESH_INTERVAL_MS,
    HISTORY_DAYS,
    FEATURE_COLUMNS,
)
from src.data_pipeline import get_surveillance_data


# =========================
# Konfigurasi halaman
# =========================
from PIL import Image

st.set_page_config(
    page_title="IDX AI — Pemantauan Pasar",
    page_icon=Image.open("assets/eye-protection.png"),
    layout="wide",
    initial_sidebar_state="expanded",
)

# Penyegaran otomatis setiap 5 menit
st_autorefresh(
    interval=AUTO_REFRESH_INTERVAL_MS,
    key="market_refresh",
)


# =========================
# Pemetaan label risiko ke Bahasa Indonesia
# =========================
RISK_CSS_CLASS = {
    "Risiko Tinggi": "high",
    "Risiko Sedang": "medium",
    "Risiko Rendah": "low",
    "Normal": "normal",
}

RISK_ICON = {
    "Risiko Tinggi": "",
    "Risiko Sedang": "",
    "Risiko Rendah": "",
    "Normal": "",
}

PERIOD_OPTIONS = {
    "1B": 30,
    "3B": 90,
    "6B": 180,
    "1T": 365,
    "YTD": None,
}


# =========================
# CSS Kustom
# =========================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    :root {
        --primary: #6C5CE7;
        --primary-light: #A29BFE;
        --accent: #00CEC9;
        --accent-light: #55EFC4;
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

    .stApp {
        font-family: 'Inter', sans-serif !important;
        background-color: #0B0E17 !important; /* Warna dasar Navy/Black yang dalam */
        background-image: 
            radial-gradient(circle at 0% 20%, rgba(108, 92, 231, 0.15) 0%, transparent 40%),
            radial-gradient(circle at 100% 40%, rgba(0, 206, 201, 0.1) 0%, transparent 35%),
            radial-gradient(circle at 30% 90%, rgba(108, 92, 231, 0.1) 0%, transparent 40%) !important;
        background-attachment: fixed !important;
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
        font-size: 2.2rem;
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
        font-size: 1rem;
        color: var(--text-secondary);
        font-weight: 400;
        margin: 0 0 1rem 0;
        position: relative;
        z-index: 1;
    }

    .hero-description {
        font-size: 0.88rem;
        color: var(--text-secondary);
        line-height: 1.7;
        max-width: 800px;
        position: relative;
        z-index: 1;
    }

    /* ===== Kartu KPI ===== */
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
        font-size: 0.7rem;
        font-weight: 600;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }

    .kpi-value {
        font-size: 1.5rem;
        font-weight: 800;
        color: var(--text-primary);
    }

    .kpi-value.purple { color: var(--primary-light); }
    .kpi-value.teal { color: var(--accent); }
    .kpi-value.red { color: var(--danger-light); }
    .kpi-value.gold { color: var(--accent-warm); }

    .kpi-trend {
        font-size: 0.72rem;
        font-weight: 600;
        margin-top: 0.4rem;
    }

    .kpi-trend.positive { color: #55EFC4; }
    .kpi-trend.negative { color: #FF8A8A; }
    .kpi-trend.neutral { color: var(--text-secondary); }

    /* ===== Header Bagian ===== */
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
        font-size: 1.15rem;
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

    /* ===== Tabel Saham Terindikasi ===== */
    .suspicious-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        font-size: 0.85rem;
    }

    .suspicious-table th {
        background: var(--surface-light);
        color: var(--text-secondary);
        font-weight: 600;
        padding: 0.8rem 0.8rem;
        text-align: left;
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        border-bottom: 1px solid var(--border);
    }

    .suspicious-table th:first-child { border-radius: 10px 0 0 0; }
    .suspicious-table th:last-child { border-radius: 0 10px 0 0; }

    .suspicious-table td {
        padding: 0.7rem 0.8rem;
        border-bottom: 1px solid rgba(108, 92, 231, 0.08);
        color: var(--text-primary);
        vertical-align: middle;
    }

    .suspicious-table tr:hover td {
        background: rgba(108, 92, 231, 0.06);
    }

    .suspicious-table tr:last-child td:first-child { border-radius: 0 0 0 10px; }
    .suspicious-table tr:last-child td:last-child { border-radius: 0 0 10px 0; }

    /* ===== Lencana Risiko ===== */
    .risk-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 50px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.3px;
    }

    .risk-badge.high {
        background: rgba(255, 107, 107, 0.18);
        color: #FF8A8A;
        border: 1px solid rgba(255, 107, 107, 0.35);
    }

    .risk-badge.medium {
        background: rgba(253, 203, 110, 0.18);
        color: #FDCB6E;
        border: 1px solid rgba(253, 203, 110, 0.35);
    }

    .risk-badge.low {
        background: rgba(108, 92, 231, 0.15);
        color: #A29BFE;
        border: 1px solid rgba(108, 92, 231, 0.3);
    }

    .risk-badge.normal {
        background: rgba(0, 206, 201, 0.12);
        color: #55EFC4;
        border: 1px solid rgba(0, 206, 201, 0.25);
    }

    /* ===== Bilah Skor ===== */
    .score-bar-container {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .score-bar-bg {
        flex: 1;
        height: 8px;
        background: var(--surface-lighter);
        border-radius: 4px;
        overflow: hidden;
        min-width: 50px;
    }

    .score-bar-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 0.6s ease;
    }

    .score-bar-fill.high { background: linear-gradient(90deg, #FF6B6B, #FF8A8A); }
    .score-bar-fill.medium { background: linear-gradient(90deg, #FDCB6E, #FFEAA7); }
    .score-bar-fill.low { background: linear-gradient(90deg, #6C5CE7, #A29BFE); }
    .score-bar-fill.normal { background: linear-gradient(90deg, #00CEC9, #55EFC4); }

    .score-text {
        font-weight: 700;
        font-size: 0.82rem;
        min-width: 32px;
        text-align: right;
    }

    /* ===== Kartu Fitur ===== */
    .feature-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 1.2rem;
        transition: all 0.3s ease;
    }

    .feature-card:hover {
        border-color: rgba(108, 92, 231, 0.4);
        box-shadow: 0 8px 24px rgba(108, 92, 231, 0.1);
    }

    .feature-card-label {
        font-size: 0.7rem;
        font-weight: 600;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 0.4rem;
    }

    .feature-card-value {
        font-size: 1.3rem;
        font-weight: 800;
        color: var(--text-primary);
    }

    .feature-card-desc {
        font-size: 0.75rem;
        color: var(--text-secondary);
        margin-top: 0.3rem;
    }

    /* ===== Kotak Informasi ===== */
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
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
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

    /* ===== Header Saham ===== */
    .stock-header {
        background: var(--gradient-hero);
        border-radius: 16px;
        padding: 2rem 2.5rem;
        border: 1px solid var(--border);
        display: flex;
        align-items: center;
        gap: 2rem;
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
    }

    .stock-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -15%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(108, 92, 231, 0.12) 0%, transparent 70%);
        border-radius: 50%;
    }

    .stock-ticker-big {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #FFFFFF 0%, #A29BFE 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        position: relative;
        z-index: 1;
    }

    .stock-info {
        position: relative;
        z-index: 1;
    }

    .stock-price {
        font-size: 1.6rem;
        font-weight: 700;
        color: var(--text-primary);
    }

    .stock-change {
        font-size: 0.9rem;
        font-weight: 600;
        margin-left: 0.5rem;
    }

    .stock-change.positive { color: var(--accent-light); }
    .stock-change.negative { color: var(--danger-light); }

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

    /* ===== Bilah Samping ===== */
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
        margin: 0 auto 0.5rem auto;
        width: 100px;  /* Sesuaikan ukuran lebar icon */
        height: 100px; /* Sesuaikan ukuran tinggi icon */
        
        background-image: none; /* Akan dioverride oleh Python jika ada file lokal */
        
        background-size: contain;
        background-repeat: no-repeat;
        background-position: center;
        border-radius: 50%; /* Membuat kotak putih menjadi lingkaran */
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

    /* ===== Daftar Ticker ===== */
    .ticker-list {
        display: flex;
        flex-wrap: wrap;
        gap: 0.35rem;
        margin: 0.5rem 0;
    }

    .ticker-tag {
        display: inline-block;
        background: rgba(108, 92, 231, 0.15);
        color: var(--primary-light);
        padding: 0.2rem 0.55rem;
        border-radius: 6px;
        font-size: 0.72rem;
        font-weight: 600;
        border: 1px solid rgba(108, 92, 231, 0.25);
    }

    .ticker-tag.custom {
        background: rgba(0, 206, 201, 0.15);
        color: var(--accent);
        border-color: rgba(0, 206, 201, 0.25);
    }

    /* ===== Status ===== */
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

    .reason-text {
        font-size: 0.75rem;
        color: var(--text-secondary);
        line-height: 1.5;
        max-width: 300px;
    }

    /* ===== Titik Langsung ===== */
    .live-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        background: var(--accent);
        border-radius: 50%;
        animation: pulse 2s infinite;
        margin-right: 0.4rem;
    }

    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(0, 206, 201, 0.5); }
        70% { box-shadow: 0 0 0 8px rgba(0, 206, 201, 0); }
        100% { box-shadow: 0 0 0 0 rgba(0, 206, 201, 0); }
    }

    /* ===== Keadaan Kosong ===== */
    .empty-state {
        text-align: center;
        padding: 2.5rem 2rem;
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 16px;
    }

    .empty-state-icon {
        font-size: 2.5rem;
        margin-bottom: 0.8rem;
    }

    .empty-state-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
    }

    .empty-state-desc {
        font-size: 0.85rem;
        color: var(--text-secondary);
        max-width: 520px;
        margin: 0 auto;
        line-height: 1.6;
    }

    /* ===== Sparkline ===== */
    .sparkline-cell {
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* ===== Animasi ===== */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .hero-container, .kpi-card, .info-box, .stock-header {
        animation: fadeInUp 0.6s ease-out forwards;
    }

    .kpi-card:nth-child(2) { animation-delay: 0.1s; }
    .kpi-card:nth-child(3) { animation-delay: 0.2s; }
    .kpi-card:nth-child(4) { animation-delay: 0.3s; }

    /* ===== DataFrame Styling ===== */
    [data-testid="stDataFrame"] {
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        overflow: hidden;
    }

    /* ===== Responsif Seluler ===== */
    @media (max-width: 768px) {
        .hero-container {
            padding: 1.5rem 1.2rem;
        }
        .hero-title {
            font-size: 1.4rem;
        }
        .hero-subtitle {
            font-size: 0.85rem;
        }
        .hero-description {
            font-size: 0.8rem;
        }
        .kpi-card {
            margin-bottom: 0.8rem;
            padding: 1rem;
        }
        .kpi-value {
            font-size: 1.2rem;
        }
        .suspicious-table {
            font-size: 0.72rem;
        }
        .suspicious-table th,
        .suspicious-table td {
            padding: 0.4rem 0.5rem;
        }
        .stock-header {
            flex-direction: column;
            text-align: center;
            padding: 1.5rem;
            gap: 1rem;
        }
        .stock-ticker-big {
            font-size: 1.6rem;
        }
        .feature-grid {
            grid-template-columns: 1fr;
        }
        .section-header {
            flex-wrap: wrap;
        }
        .section-header-badge {
            margin-left: 0;
        }
    }

    /* ===== Efek Transisi Halaman ===== */
    @keyframes smoothFadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Menerapkan animasi ke blok vertikal utama Streamlit agar ter-trigger tiap pergantian halaman */
    [data-testid="stVerticalBlock"] {
        animation: smoothFadeIn 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }
</style>
""", unsafe_allow_html=True)

# Helper untuk memuat gambar lokal sebagai Base64 agar bisa dipakai di CSS Streamlit
def inject_local_icon_css(image_path):
    if os.path.exists(image_path):
        try:
            with open(image_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            ext = image_path.split('.')[-1]
            css = f"""
            <style>
            .sidebar-brand-icon {{
                background-image: url('data:image/{ext};base64,{b64}') !important;
            }}
            </style>
            """
            st.markdown(css, unsafe_allow_html=True)
        except Exception:
            pass

# Masukkan path gambar lokal Anda di sini:
inject_local_icon_css("assets/eyestrain.gif")


# =========================
# Tata letak Plotly gelap
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
# Fungsi pembantu
# =========================
def get_risk_badge_html(risk_level: str) -> str:
    css_class = RISK_CSS_CLASS.get(risk_level, "normal")
    return f'<span class="risk-badge {css_class}">{risk_level}</span>'


def get_score_bar_html(score: float, risk_level: str) -> str:
    css_class = RISK_CSS_CLASS.get(risk_level, "normal")
    pct = min(score * 100, 100)
    return f"""
    <div class="score-bar-container">
        <div class="score-bar-bg">
            <div class="score-bar-fill {css_class}" style="width:{pct:.0f}%"></div>
        </div>
        <span class="score-text" style="color: var(--text-primary);">{score:.2f}</span>
    </div>
    """


def generate_sparkline_svg(values, width=70, height=22):
    if not values or len(values) < 2:
        return f'<svg width="{width}" height="{height}"></svg>'
    min_val = min(values)
    max_val = max(values)
    val_range = max_val - min_val if max_val != min_val else 1
    points = []
    for i, v in enumerate(values):
        x = (i / (len(values) - 1)) * width
        y = height - ((v - min_val) / val_range) * (height - 4) - 2
        points.append(f"{x:.1f},{y:.1f}")
    polyline = " ".join(points)
    color = "#55EFC4" if values[-1] >= values[0] else "#FF8A8A"
    return (
        f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">'
        f'<polyline points="{polyline}" fill="none" stroke="{color}" '
        f'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>'
        f'</svg>'
    )


def get_trend_html(delta, label=""):
    if delta > 0:
        return f'<div class="kpi-trend positive">▲ +{delta} {label}</div>'
    elif delta < 0:
        return f'<div class="kpi-trend negative">▼ {delta} {label}</div>'
    else:
        return f'<div class="kpi-trend neutral">— tidak berubah</div>'


def filter_chart_data(stock_df, period_key):
    days = PERIOD_OPTIONS.get(period_key)
    if days is not None:
        cutoff = stock_df["date"].max() - timedelta(days=days)
        return stock_df[stock_df["date"] >= cutoff]
    else:
        year_start = stock_df["date"].max().replace(month=1, day=1)
        return stock_df[stock_df["date"] >= year_start]


# =========================
# Bilah Samping
# =========================
with st.sidebar:
    st.markdown("""
<div class="sidebar-brand">
    <div class="sidebar-brand-icon"></div>
    <div class="sidebar-brand-name">IDX AI Surveillance</div>
    <div class="sidebar-brand-version">Dasbor Pemantauan Pasar v1.0</div>
</div>
    """, unsafe_allow_html=True)

    st.markdown("## Navigasi")

    page = st.radio(
        "Pilih halaman",
        ["Pemantauan Pasar", "Analisis Saham"],
        label_visibility="collapsed",
    )

    if "custom_tickers" not in st.session_state:
        st.session_state.custom_tickers = []
    
    all_tickers = DEFAULT_TICKERS + st.session_state.custom_tickers

    if page == "Pemantauan Pasar":
        st.markdown("---")
        st.markdown("## Pengaturan")

        st.markdown("**Saham yang Dipantau**")

        custom_ticker_input = st.text_input(
            "Tambah kode saham (contoh: BBNI.JK)",
            placeholder="Ketik kode saham, lalu tekan Enter",
            help="Masukkan kode saham Yahoo Finance. Contoh: BBNI.JK, ASII.JK",
        )

        if custom_ticker_input:
            ticker_upper = custom_ticker_input.strip().upper()
            if ticker_upper and ticker_upper not in DEFAULT_TICKERS and ticker_upper not in st.session_state.custom_tickers:
                if not ticker_upper.endswith(".JK"):
                    ticker_upper = ticker_upper + ".JK"
                st.session_state.custom_tickers.append(ticker_upper)
                st.rerun()

        pills_html = " ".join([
            f'<span class="ticker-tag{" custom" if t in st.session_state.custom_tickers else ""}">'
            f'{t.replace(".JK", "")}</span>'
            for t in all_tickers
        ])
        st.markdown(
            f"<div style='font-size:0.8rem; color:#A0A0B8; margin-bottom:0.3rem;'>"
            f"<b>{len(all_tickers)}</b> saham dipantau</div>"
            f"<div class='ticker-list'>{pills_html}</div>",
            unsafe_allow_html=True,
        )

        if st.session_state.custom_tickers:
            st.markdown(
                "<div style='font-size:0.75rem; color:#A0A0B8; margin-top:0.8rem; margin-bottom:0.3rem;'>"
                "Hapus saham tambahan:</div>",
                unsafe_allow_html=True,
            )
            for i, t in enumerate(st.session_state.custom_tickers):
                if st.button(
                    f"✕ {t.replace('.JK', '')}",
                    key=f"rm_{i}",
                    use_container_width=True,
                ):
                    st.session_state.custom_tickers.remove(t)
                    st.rerun()

        st.markdown("---")

        if st.button("Segarkan Data Sekarang", key="refresh_main", use_container_width=True):
            st.cache_data.clear()
            st.rerun()


# =========================
# Pemuatan Data
# =========================
@st.cache_data(ttl=CACHE_TTL, show_spinner="Mengambil data pasar terbaru...")
def load_surveillance_data(tickers_tuple):
    return get_surveillance_data(list(tickers_tuple))


tickers_tuple = tuple(all_tickers)

with st.spinner("Memuat data pemantauan pasar..."):
    df = load_surveillance_data(tickers_tuple)

if df.empty:
    st.error("❌ Gagal mengambil data. Periksa koneksi internet Anda atau coba segarkan halaman.")
    st.stop()

wib_tz = timezone(timedelta(hours=7))
last_update = datetime.now(wib_tz).strftime("%d %b %Y, %H:%M WIB")


# ==========================================================
# HALAMAN 1: PEMANTAUAN PASAR
# ==========================================================
if page == "Pemantauan Pasar":

    # --- Hero Header ---
    st.markdown(f"""
<div class="hero-container">
    <div class="hero-badge">Sistem Pemantauan Pasar Berbasis AI</div>
    <h1 class="hero-title">IDX AI Market Surveillance</h1>
    <p class="hero-subtitle">Pemantauan Aktivitas Pasar Tidak Biasa — Bursa Efek Indonesia</p>
    <p class="hero-description">
        Sistem pemantauan pasar berbasis kecerdasan buatan untuk mendeteksi pergerakan harga dan volume saham
        yang tidak biasa secara <em>real-time</em>. Menggunakan algoritma <strong style="color:#A29BFE;"><em>Isolation Forest</em></strong>
        untuk menganalisis pola perdagangan dan mengidentifikasi aktivitas yang menyimpang dari kondisi normal,
        terinspirasi dari konsep <strong style="color:#00CEC9;"><em>Unusual Market Activity</em> (UMA)</strong>
        yang diterapkan oleh Bursa Efek Indonesia.
    </p>
</div>
    """, unsafe_allow_html=True)

    # --- Sanggahan (dapat diciutkan) ---
    with st.expander("️ Sanggahan — Bukan Rekomendasi Investasi", expanded=False):
        st.markdown("""
Dasbor ini dibuat untuk **tujuan edukasi dan riset**.
Hasil deteksi anomali bukan merupakan rekomendasi untuk membeli, menjual, atau menahan saham tertentu.
Sistem ini **tidak menyatakan adanya manipulasi pasar** dan hanya mendeteksi pola harga serta volume
yang terlihat tidak biasa berdasarkan data historis. Segala keputusan investasi sepenuhnya menjadi
tanggung jawab masing-masing individu.
        """)

    # --- Kartu KPI dengan Indikator Tren ---
    latest_date = df["date"].max()
    latest_df = df[df["date"] == latest_date]
    anomalies_today = latest_df[latest_df["is_anomaly"] == True]
    total_monitored = df["ticker"].nunique()
    total_anomalies_today = anomalies_today["ticker"].nunique()

    if not anomalies_today.empty:
        highest_score = anomalies_today["anomaly_score_normalized"].max()
        highest_ticker = anomalies_today.loc[
            anomalies_today["anomaly_score_normalized"].idxmax(), "ticker"
        ]
    else:
        highest_score = 0.0
        highest_ticker = "—"

    # Hitung delta dibandingkan hari sebelumnya
    all_dates = sorted(df["date"].unique())
    if len(all_dates) >= 2:
        prev_date = all_dates[-2]
        prev_df = df[df["date"] == prev_date]
        prev_anomalies = prev_df[prev_df["is_anomaly"] == True]
        prev_total_anomalies = prev_anomalies["ticker"].nunique()
        prev_monitored = prev_df["ticker"].nunique()

        if not prev_anomalies.empty:
            prev_highest = prev_anomalies["anomaly_score_normalized"].max()
        else:
            prev_highest = 0.0

        delta_monitored = total_monitored - prev_monitored
        delta_anomalies = total_anomalies_today - prev_total_anomalies
        delta_score = highest_score - prev_highest
    else:
        delta_monitored = 0
        delta_anomalies = 0
        delta_score = 0.0

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        trend_html = get_trend_html(delta_monitored, "saham") if delta_monitored != 0 else '<div class="kpi-trend neutral">— tidak berubah</div>'
        st.markdown(f"""
<div class="kpi-card purple">
    <div class="kpi-icon"></div>
    <div class="kpi-label">Saham Dipantau</div>
    <div class="kpi-value purple">{total_monitored}</div>
    {trend_html}
</div>
        """, unsafe_allow_html=True)

    with col2:
        trend_html = get_trend_html(delta_anomalies, "anomali") if delta_anomalies != 0 else '<div class="kpi-trend neutral">— tidak berubah</div>'
        st.markdown(f"""
<div class="kpi-card red">
    <div class="kpi-icon"></div>
    <div class="kpi-label">Anomali Hari Ini</div>
    <div class="kpi-value red">{total_anomalies_today}</div>
    {trend_html}
</div>
        """, unsafe_allow_html=True)

    with col3:
        if abs(delta_score) > 0.001:
            trend_html = get_trend_html(round(delta_score, 2), "skor")
        else:
            trend_html = '<div class="kpi-trend neutral">— tidak berubah</div>'
        st.markdown(f"""
<div class="kpi-card gold">
    <div class="kpi-icon"></div>
    <div class="kpi-label">Skor Risiko Tertinggi</div>
    <div class="kpi-value gold">{highest_score:.2f}</div>
    {trend_html}
</div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
<div class="kpi-card teal">
    <div class="kpi-icon"></div>
    <div class="kpi-label">Terakhir Diperbarui</div>
    <div class="kpi-value teal" style="font-size:1rem;">{last_update}</div>
    <div class="kpi-trend neutral"><span class="live-dot"></span> langsung</div>
</div>
        """, unsafe_allow_html=True)


    # --- Saham Terindikasi Anomali Hari Ini ---
    st.markdown("""
<div class="section-header">
    <span class="section-header-icon"></span>
    <span class="section-header-text">Saham Terindikasi Anomali Hari Ini</span>
    <span class="section-header-badge">PERINGKAT LANGSUNG</span>
</div>
    """, unsafe_allow_html=True)

    latest_scores = latest_df.groupby("ticker").agg(
        anomaly_score_normalized=("anomaly_score_normalized", "max"),
        risk_level=("risk_level", "first"),
        is_anomaly=("is_anomaly", "any"),
        anomaly_reason=("anomaly_reason", "first"),
        close=("close", "last"),
        daily_return=("daily_return", "last"),
        volume_spike_ratio=("volume_spike_ratio", "last"),
        volume=("volume", "last"),
    ).reset_index()

    latest_scores = latest_scores.sort_values("anomaly_score_normalized", ascending=False)

    from src.data_pipeline import _classify_risk
    latest_scores["risk_level"] = latest_scores["anomaly_score_normalized"].apply(_classify_risk)

    # Pencarian
    search_query = st.text_input(
        "Cari kode saham",
        placeholder="Ketik kode saham untuk memfilter tabel...",
        label_visibility="collapsed",
    )

    if search_query:
        filtered_scores = latest_scores[
            latest_scores["ticker"].str.contains(search_query.upper(), na=False)
        ]
    else:
        filtered_scores = latest_scores

    if filtered_scores.empty:
        st.markdown("""
<div class="empty-state">
    <div class="empty-state-icon"></div>
    <div class="empty-state-title">Tidak Ditemukan</div>
    <div class="empty-state-desc">Tidak ada saham yang sesuai dengan kata kunci pencarian Anda. Silakan coba kata kunci lain.</div>
</div>
        """, unsafe_allow_html=True)
    else:
        # Data sparkline 7 hari terakhir
        sparkline_data_map = {}
        for ticker in filtered_scores["ticker"].unique():
            ticker_hist = df[df["ticker"] == ticker].sort_values("date").tail(7)
            sparkline_data_map[ticker] = ticker_hist["close"].tolist()

        table_rows = ""
        for rank, (_, row) in enumerate(filtered_scores.iterrows(), 1):
            badge_html = get_risk_badge_html(row["risk_level"])
            score_html = get_score_bar_html(row["anomaly_score_normalized"], row["risk_level"])

            if row["is_anomaly"] and row["anomaly_reason"] != "Normal":
                reason_text = row["anomaly_reason"]
            else:
                reason_text = "Tidak ada aktivitas mencurigakan"

            ret_val = row["daily_return"] * 100 if pd.notna(row["daily_return"]) else 0
            ret_color = "#55EFC4" if ret_val >= 0 else "#FF8A8A"
            ret_sign = "+" if ret_val >= 0 else ""
            ret_icon = "▲" if ret_val >= 0 else "▼"

            spark_svg = generate_sparkline_svg(sparkline_data_map.get(row["ticker"], []))

            table_rows += f"""<tr>
<td style="font-weight:700; color:var(--primary-light);">{rank}</td>
<td style="font-weight:700;">{row['ticker']}</td>
<td><div class="sparkline-cell">{spark_svg}</div></td>
<td>{score_html}</td>
<td>{badge_html}</td>
<td><span style="color:{ret_color}; font-weight:600;">{ret_icon} {ret_sign}{ret_val:.2f}%</span></td>
<td><div class="reason-text">{reason_text}</div></td>
</tr>"""

        st.markdown(f"""
<table class="suspicious-table">
    <thead>
        <tr>
            <th>#</th>
            <th>Kode Saham</th>
            <th>7 Hari</th>
            <th>Skor Anomali</th>
            <th>Status</th>
            <th>Imbal Hasil</th>
            <th>Indikasi Penyebab</th>
        </tr>
    </thead>
    <tbody>
        {table_rows}
    </tbody>
</table>
        """, unsafe_allow_html=True)

    # Unduh CSV
    download_cols = latest_scores[["ticker", "anomaly_score_normalized", "risk_level",
                                    "daily_return", "volume_spike_ratio", "anomaly_reason"]].copy()
    download_cols.columns = ["Kode Saham", "Skor Anomali", "Tingkat Risiko",
                              "Imbal Hasil Harian", "Rasio Lonjakan Volume", "Indikasi Penyebab"]
    csv_suspicious = download_cols.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Unduh Data CSV",
        data=csv_suspicious,
        file_name=f"saham_terindikasi_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )


    # --- Peta Risiko Pasar ---
    st.markdown("""
<div style="margin: 2.5rem 0 1rem 0; padding-bottom: 0.75rem; border-bottom: 1px solid rgba(255,255,255,0.1); display: flex; align-items: center;">
    <span style="font-family: 'Inter', sans-serif; font-size: 1.15rem; font-weight: 800; color: #E8E8F0; text-transform: uppercase; letter-spacing: 0.5px;">Peta Risiko Pasar</span>
    <span style="display: inline-block; background: transparent; color: #A0A0B8; border: 1px solid rgba(255,255,255,0.2); padding: 0.2rem 0.6rem; font-family: monospace; font-size: 0.7rem; font-weight: 700; margin-left: auto;">PETA PANAS</span>
</div>
    """, unsafe_allow_html=True)

    heatmap_data = latest_scores[["ticker", "anomaly_score_normalized", "risk_level", "volume"]].copy()
    heatmap_data["score_display"] = heatmap_data["anomaly_score_normalized"].apply(lambda x: f"{x:.2f}")
    heatmap_data["volume"] = heatmap_data["volume"].fillna(0).astype(int)
    heatmap_data["volume"] = heatmap_data["volume"].apply(lambda x: max(x, 1))

    # Skala logaritma agar kotak saham berukuran kecil tidak terlalu menyusut/penyok
    heatmap_data["size"] = np.log1p(heatmap_data["volume"])

    fig_heatmap = px.treemap(
        heatmap_data,
        path=["ticker"],
        values="size",
        color="anomaly_score_normalized",
        color_continuous_scale=[
            [0, "#1E1E2E"],
            [0.25, "#2A2A5E"],
            [0.5, "#6C5CE7"],
            [0.75, "#FDCB6E"],
            [1.0, "#FF6B6B"],
        ],
        custom_data=["score_display", "risk_level"],
    )

    fig_heatmap.update_traces(
        textinfo="label+text",
        texttemplate="<b>%{label}</b><br>Skor: %{customdata[0]}",
        textfont=dict(size=14, family="Inter, sans-serif", color="#FFFFFF"),
        hovertemplate="<b>%{label}</b><br>Skor Anomali: %{customdata[0]}<br>Status: %{customdata[1]}<extra></extra>",
        marker=dict(cornerradius=0),
    )

    fig_heatmap.update_layout(
        paper_bgcolor="#1E1E2E",
        plot_bgcolor="#1E1E2E",
        font=dict(family="Inter, sans-serif", color="#E8E8F0"),
        height=450,
        margin=dict(l=15, r=15, t=15, b=15),
        coloraxis_colorbar=dict(
            title=dict(text="Skor", font=dict(color="#A0A0B8")),
            tickfont=dict(color="#A0A0B8"),
        ),
    )

    st.plotly_chart(fig_heatmap, use_container_width=True)


    # --- Riwayat Anomali Terdeteksi ---
    st.markdown("""
<div class="section-header">
    <span class="section-header-icon"></span>
    <span class="section-header-text">Riwayat Anomali Terdeteksi</span>
    <span class="section-header-badge">SELURUH SAHAM</span>
</div>
    """, unsafe_allow_html=True)

    all_anomalies = df[df["is_anomaly"] == True].copy()

    if all_anomalies.empty:
        st.markdown("""
<div class="empty-state">
    <div class="empty-state-icon"></div>
    <div class="empty-state-title">Tidak Ada Anomali Terdeteksi</div>
    <div class="empty-state-desc">
        Seluruh saham yang dipantau menunjukkan pola perdagangan yang normal pada periode ini.
        Hal ini mengindikasikan kondisi pasar yang relatif stabil tanpa adanya pergerakan harga
        atau volume yang signifikan menyimpang dari pola historisnya.
    </div>
</div>
        """, unsafe_allow_html=True)
    else:
        all_anomalies_table = all_anomalies[
            ["date", "ticker", "close", "volume", "daily_return",
             "volume_spike_ratio", "anomaly_score_normalized", "risk_level", "anomaly_reason"]
        ].copy()

        all_anomalies_table = all_anomalies_table.sort_values("date", ascending=False).head(20)
        all_anomalies_table["date"] = all_anomalies_table["date"].dt.strftime("%Y-%m-%d")
        all_anomalies_table["daily_return"] = (all_anomalies_table["daily_return"] * 100).round(2)
        all_anomalies_table["anomaly_score_normalized"] = all_anomalies_table["anomaly_score_normalized"].round(3)
        all_anomalies_table["volume_spike_ratio"] = all_anomalies_table["volume_spike_ratio"].round(2)

        all_anomalies_table = all_anomalies_table.rename(columns={
            "date": "Tanggal",
            "ticker": "Kode Saham",
            "close": "Harga Penutupan",
            "volume": "Volume",
            "daily_return": "Imbal Hasil (%)",
            "volume_spike_ratio": "Lonjakan Vol.",
            "anomaly_score_normalized": "Skor",
            "risk_level": "Tingkat Risiko",
            "anomaly_reason": "Indikasi Penyebab",
        })

        st.dataframe(
            all_anomalies_table,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Harga Penutupan": st.column_config.NumberColumn(format="Rp %.0f"),
                "Volume": st.column_config.NumberColumn(format="%.0f"),
                "Imbal Hasil (%)": st.column_config.NumberColumn(format="%.2f"),
                "Lonjakan Vol.": st.column_config.NumberColumn(format="%.2f"),
                "Skor": st.column_config.NumberColumn(format="%.3f"),
            },
        )

        csv_anomaly = all_anomalies_table.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Unduh Riwayat CSV",
            data=csv_anomaly,
            file_name=f"riwayat_anomali_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )


    # --- Cara Kerja Sistem ---
    st.markdown("""
<div class="section-header">
    <span class="section-header-icon"></span>
    <span class="section-header-text">Cara Kerja Sistem</span>
</div>
    """, unsafe_allow_html=True)

    st.markdown("""
<div class="info-box">
    <h4>Fitur yang Digunakan untuk Deteksi Anomali</h4>
    <div class="feature-grid">
        <div class="feature-item">
            <div class="feature-dot"></div>
            <div>
                <span class="feature-name">Imbal Hasil Harian</span><br>
                <span class="feature-desc">Perubahan harga penutupan dari hari sebelumnya</span>
            </div>
        </div>
        <div class="feature-item">
            <div class="feature-dot"></div>
            <div>
                <span class="feature-name">Perubahan Volume</span><br>
                <span class="feature-desc">Perubahan volume perdagangan dari hari sebelumnya</span>
            </div>
        </div>
        <div class="feature-item">
            <div class="feature-dot"></div>
            <div>
                <span class="feature-name">Rasio Lonjakan Volume</span><br>
                <span class="feature-desc">Perbandingan volume hari ini terhadap rata-rata 20 hari</span>
            </div>
        </div>
        <div class="feature-item">
            <div class="feature-dot"></div>
            <div>
                <span class="feature-name">Persentase Rentang Harga</span><br>
                <span class="feature-desc">Selisih harga tertinggi dan terendah terhadap harga penutupan</span>
            </div>
        </div>
        <div class="feature-item">
            <div class="feature-dot"></div>
            <div>
                <span class="feature-name">Simpangan Harga MA 20</span><br>
                <span class="feature-desc">Jarak harga penutupan terhadap rata-rata bergerak 20 hari</span>
            </div>
        </div>
        <div class="feature-item">
            <div class="feature-dot"></div>
            <div>
                <span class="feature-name">Volatilitas 20 Hari</span><br>
                <span class="feature-desc">Volatilitas imbal hasil selama 20 hari terakhir</span>
            </div>
        </div>
        <div class="feature-item">
            <div class="feature-dot"></div>
            <div>
                <span class="feature-name"><em>Z-Score</em> Imbal Hasil</span><br>
                <span class="feature-desc">Tingkat ekstrem imbal hasil dibandingkan pola 20 hari terakhir</span>
            </div>
        </div>
        <div class="feature-item">
            <div class="feature-dot"></div>
            <div>
                <span class="feature-name"><em>Z-Score</em> Volume</span><br>
                <span class="feature-desc">Tingkat ekstrem volume dibandingkan pola 20 hari terakhir</span>
            </div>
        </div>
    </div>
<div class="model-box">
    <div class="model-box-title">Model: <em>Isolation Forest</em></div>
    <div class="model-box-text">
        Model yang digunakan adalah <strong><em>Isolation Forest</em></strong>, yaitu algoritma <em>unsupervised learning</em>
        yang mendeteksi data yang berbeda dari pola normal. Algoritma ini bekerja dengan cara mengisolasi
        observasi — data yang lebih mudah diisolasi dianggap sebagai anomali. Skor anomali dinormalisasi
        ke skala <strong>0,00</strong> (normal) hingga <strong>1,00</strong> (sangat tidak biasa).
    </div>
</div>
</div>
    """, unsafe_allow_html=True)


# ==========================================================
# HALAMAN 2: ANALISIS SAHAM
# ==========================================================
elif page == "Analisis Saham":

    available_tickers = sorted(df["ticker"].unique())

    with st.sidebar:
        st.markdown("## Pilih Saham")
        selected_ticker = st.selectbox(
            "Kode saham untuk analisis mendalam",
            available_tickers,
            help="Pilih saham yang ingin dianalisis secara mendalam",
        )

        if st.button("Segarkan Data Sekarang", key="refresh_analysis", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    stock_df = df[df["ticker"] == selected_ticker].copy().sort_values("date")
    anomaly_df = stock_df[stock_df["is_anomaly"] == True].copy()

    if stock_df.empty:
        st.warning(f"️ Data tidak tersedia untuk {selected_ticker}.")
        st.stop()

    # --- Header Saham ---
    latest = stock_df.iloc[-1]
    latest_close = latest["close"]
    latest_return = latest["daily_return"] * 100 if pd.notna(latest["daily_return"]) else 0
    latest_risk = latest["risk_level"]
    latest_score = latest["anomaly_score_normalized"]

    change_class = "positive" if latest_return >= 0 else "negative"
    change_sign = "+" if latest_return >= 0 else ""
    change_icon = "▲" if latest_return >= 0 else "▼"
    badge_html = get_risk_badge_html(latest_risk)

    st.markdown(f"""
<div class="stock-header">
    <div class="stock-ticker-big">{selected_ticker}</div>
    <div class="stock-info">
        <span class="stock-price">Rp {latest_close:,.0f}</span>
        <span class="stock-change {change_class}">{change_icon} {change_sign}{latest_return:.2f}%</span>
        <br>
        <span style="font-size:0.85rem; color: var(--text-secondary); margin-right: 0.5rem;">Skor: {latest_score:.2f}</span>
        {badge_html}
    </div>
</div>
    """, unsafe_allow_html=True)


    # --- Rincian Fitur Terkini ---
    st.markdown("""
<div class="section-header">
    <span class="section-header-icon"></span>
    <span class="section-header-text">Rincian Fitur Terkini</span>
    <span class="section-header-badge">TERKINI</span>
</div>
    """, unsafe_allow_html=True)

    fc1, fc2, fc3 = st.columns(3)

    with fc1:
        val = latest["daily_return"] * 100 if pd.notna(latest["daily_return"]) else 0
        color = "#55EFC4" if val >= 0 else "#FF8A8A"
        icon = "▲" if val >= 0 else "▼"
        st.markdown(f"""
<div class="feature-card">
    <div class="feature-card-label">Imbal Hasil Harian</div>
    <div class="feature-card-value" style="color:{color};">{icon} {val:+.2f}%</div>
    <div class="feature-card-desc">Perubahan harga penutupan harian</div>
</div>
        """, unsafe_allow_html=True)

    with fc2:
        val = latest["volume_spike_ratio"] if pd.notna(latest["volume_spike_ratio"]) else 0
        color = "#FF8A8A" if val >= 3 else "#A29BFE" if val >= 1.5 else "#55EFC4"
        st.markdown(f"""
<div class="feature-card">
    <div class="feature-card-label">Rasio Lonjakan Volume</div>
    <div class="feature-card-value" style="color:{color};">{val:.2f}x</div>
    <div class="feature-card-desc">Dibanding rata-rata 20 hari</div>
</div>
        """, unsafe_allow_html=True)

    with fc3:
        val = latest["rolling_volatility_20"] * 100 if pd.notna(latest["rolling_volatility_20"]) else 0
        st.markdown(f"""
<div class="feature-card">
    <div class="feature-card-label">📉 Volatilitas 20 Hari</div>
    <div class="feature-card-value" style="color:#FDCB6E;">{val:.2f}%</div>
    <div class="feature-card-desc">Volatilitas imbal hasil 20 hari</div>
</div>
        """, unsafe_allow_html=True)

    fc4, fc5, fc6 = st.columns(3)

    with fc4:
        val = latest["return_zscore_20"] if pd.notna(latest["return_zscore_20"]) else 0
        color = "#FF8A8A" if abs(val) >= 2 else "#A29BFE" if abs(val) >= 1 else "#55EFC4"
        icon = "▲" if val >= 0 else "▼"
        st.markdown(f"""
<div class="feature-card">
    <div class="feature-card-label"><em>Z-Score</em> Imbal Hasil</div>
    <div class="feature-card-value" style="color:{color};">{icon} {val:+.2f}</div>
    <div class="feature-card-desc">Deviasi imbal hasil dari pola 20 hari</div>
</div>
        """, unsafe_allow_html=True)

    with fc5:
        val = latest["volume_zscore_20"] if pd.notna(latest["volume_zscore_20"]) else 0
        color = "#FF8A8A" if abs(val) >= 2 else "#A29BFE" if abs(val) >= 1 else "#55EFC4"
        icon = "▲" if val >= 0 else "▼"
        st.markdown(f"""
<div class="feature-card">
    <div class="feature-card-label"><em>Z-Score</em> Volume</div>
    <div class="feature-card-value" style="color:{color};">{icon} {val:+.2f}</div>
    <div class="feature-card-desc">Deviasi volume dari pola 20 hari</div>
</div>
        """, unsafe_allow_html=True)

    with fc6:
        val = latest["price_gap_ma_20"] * 100 if pd.notna(latest["price_gap_ma_20"]) else 0
        color = "#FF8A8A" if abs(val) >= 8 else "#FDCB6E" if abs(val) >= 4 else "#55EFC4"
        icon = "▲" if val >= 0 else "▼"
        st.markdown(f"""
<div class="feature-card">
    <div class="feature-card-label">Simpangan Harga MA20</div>
    <div class="feature-card-value" style="color:{color};">{icon} {val:+.2f}%</div>
    <div class="feature-card-desc">Jarak harga dari rata-rata bergerak 20 hari</div>
</div>
        """, unsafe_allow_html=True)


    # --- Grafik Candlestick ---
    st.markdown(f"""
<div class="section-header">
    <span class="section-header-icon"></span>
    <span class="section-header-text">Grafik <em>Candlestick</em> — {selected_ticker}</span>
    <span class="section-header-badge">INTERAKTIF</span>
</div>
    """, unsafe_allow_html=True)

    selected_period = st.radio(
        "Periode Grafik",
        list(PERIOD_OPTIONS.keys()),
        horizontal=True,
        index=2,
        label_visibility="collapsed",
    )

    chart_df = filter_chart_data(stock_df, selected_period)
    chart_anomaly = chart_df[chart_df["is_anomaly"] == True]

    fig_price = go.Figure()

    bullish_color = "#55EFC4"
    bearish_color = "#FF6B6B"

    fig_price.add_trace(
        go.Candlestick(
            x=chart_df["date"],
            open=chart_df["open"],
            high=chart_df["high"],
            low=chart_df["low"],
            close=chart_df["close"],
            name="OHLC",
            increasing_line_color=bullish_color,
            decreasing_line_color=bearish_color,
            increasing_fillcolor=bullish_color,
            decreasing_fillcolor=bearish_color,
        )
    )

    if not chart_anomaly.empty:
        fig_price.add_trace(
            go.Scatter(
                x=chart_anomaly["date"],
                y=chart_anomaly["close"],
                mode="markers",
                marker=dict(
                    size=12,
                    color="#FDCB6E",
                    symbol="diamond",
                    line=dict(width=2, color="#E17055"),
                ),
                name="Anomali",
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


    # --- Grafik Volume ---
    st.markdown(f"""
<div class="section-header">
    <span class="section-header-icon"></span>
    <span class="section-header-text">Volume Perdagangan — {selected_ticker}</span>
</div>
    """, unsafe_allow_html=True)

    fig_volume = go.Figure()

    volume_colors = [
        "#FF6B6B" if row["is_anomaly"] else "rgba(108,92,231,0.5)"
        for _, row in chart_df.iterrows()
    ]

    fig_volume.add_trace(
        go.Bar(
            x=chart_df["date"],
            y=chart_df["volume"],
            name="Volume",
            marker=dict(
                color=volume_colors,
                line=dict(width=0),
            ),
            opacity=0.85,
        )
    )

    if not chart_anomaly.empty:
        fig_volume.add_trace(
            go.Scatter(
                x=chart_anomaly["date"],
                y=chart_anomaly["volume"],
                mode="markers",
                marker=dict(
                    size=10,
                    color="#FDCB6E",
                    symbol="diamond",
                    line=dict(width=2, color="#E17055"),
                ),
                name="Anomali Volume",
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


    # --- Riwayat Anomali Saham ---
    st.markdown(f"""
<div class="section-header">
    <span class="section-header-icon"></span>
    <span class="section-header-text">Riwayat Anomali — {selected_ticker}</span>
    <span class="section-header-badge">{len(anomaly_df)} CATATAN</span>
</div>
    """, unsafe_allow_html=True)

    if anomaly_df.empty:
        st.markdown(f"""
<div class="empty-state">
    <div class="empty-state-icon"></div>
    <div class="empty-state-title">Tidak Ada Anomali pada {selected_ticker}</div>
    <div class="empty-state-desc">
        Saham {selected_ticker} tidak menunjukkan anomali selama periode data yang tersedia.
        Pola perdagangan saham ini berada dalam batas normal berdasarkan analisis historis.
    </div>
</div>
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
                "anomaly_score_normalized",
                "risk_level",
                "anomaly_reason",
            ]
        ].copy()

        anomaly_table["date"] = anomaly_table["date"].dt.strftime("%Y-%m-%d")
        anomaly_table["daily_return"] = (anomaly_table["daily_return"] * 100).round(2)
        anomaly_table["price_range_pct"] = (anomaly_table["price_range_pct"] * 100).round(2)
        anomaly_table["anomaly_score_normalized"] = anomaly_table["anomaly_score_normalized"].round(3)
        anomaly_table["volume_spike_ratio"] = anomaly_table["volume_spike_ratio"].round(2)

        anomaly_table = anomaly_table.rename(columns={
            "date": "Tanggal",
            "ticker": "Kode Saham",
            "close": "Harga Penutupan",
            "volume": "Volume",
            "daily_return": "Imbal Hasil (%)",
            "volume_spike_ratio": "Lonjakan Vol.",
            "price_range_pct": "Rentang (%)",
            "anomaly_score_normalized": "Skor",
            "risk_level": "Tingkat Risiko",
            "anomaly_reason": "Indikasi Penyebab",
        })

        anomaly_table = anomaly_table.sort_values("Skor", ascending=False)

        st.dataframe(
            anomaly_table,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Harga Penutupan": st.column_config.NumberColumn(format="Rp %.0f"),
                "Volume": st.column_config.NumberColumn(format="%.0f"),
                "Imbal Hasil (%)": st.column_config.NumberColumn(format="%.2f"),
                "Lonjakan Vol.": st.column_config.NumberColumn(format="%.2f"),
                "Rentang (%)": st.column_config.NumberColumn(format="%.2f"),
                "Skor": st.column_config.NumberColumn(format="%.3f"),
            },
        )

        csv_stock_anomaly = anomaly_table.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Unduh Riwayat CSV",
            data=csv_stock_anomaly,
            file_name=f"riwayat_anomali_{selected_ticker}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )


# =========================
# Footer (kedua halaman)
# =========================
st.markdown(f"""
<div class="footer">
    <p>
        <span class="live-dot"></span>
        <strong style="color:#A29BFE;">IDX AI Market Surveillance</strong> —
        Dibuat untuk tujuan edukasi dan riset<br>
        Data bersumber dari Yahoo Finance | Tidak terafiliasi dengan BEI<br>
    </p>
</div>
""", unsafe_allow_html=True)

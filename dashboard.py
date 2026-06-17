# ==============================================================
# IDX UMA — AI Market Surveillance Dashboard
# Real-time market surveillance for Indonesian stocks
# ==============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
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
st.set_page_config(
    page_title="IDX AI Market Surveillance",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Auto-refresh setiap 5 menit
st_autorefresh(
    interval=AUTO_REFRESH_INTERVAL_MS,
    key="market_refresh",
)


# =========================
# Custom CSS
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
        font-size: 0.82rem;
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

    /* ===== Suspicious Stocks Table ===== */
    .suspicious-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        font-size: 0.88rem;
    }

    .suspicious-table th {
        background: var(--surface-light);
        color: var(--text-secondary);
        font-weight: 600;
        padding: 0.8rem 1rem;
        text-align: left;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        border-bottom: 1px solid var(--border);
    }

    .suspicious-table th:first-child { border-radius: 10px 0 0 0; }
    .suspicious-table th:last-child { border-radius: 0 10px 0 0; }

    .suspicious-table td {
        padding: 0.75rem 1rem;
        border-bottom: 1px solid rgba(108, 92, 231, 0.08);
        color: var(--text-primary);
        vertical-align: middle;
    }

    .suspicious-table tr:hover td {
        background: rgba(108, 92, 231, 0.06);
    }

    .suspicious-table tr:last-child td:first-child { border-radius: 0 0 0 10px; }
    .suspicious-table tr:last-child td:last-child { border-radius: 0 0 10px 0; }

    /* ===== Risk Badges ===== */
    .risk-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 50px;
        font-size: 0.75rem;
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

    /* ===== Score Bar ===== */
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
        min-width: 60px;
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
        font-size: 0.85rem;
        min-width: 35px;
        text-align: right;
    }

    /* ===== Feature Cards ===== */
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

    /* ===== Info Box ===== */
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

    /* ===== Coming Soon Section ===== */
    .coming-soon-container {
        background: var(--surface);
        border: 1px dashed rgba(108, 92, 231, 0.3);
        border-radius: 16px;
        padding: 2.5rem 2rem;
        text-align: center;
        position: relative;
        overflow: hidden;
        opacity: 0.7;
    }

    .coming-soon-container::before {
        content: '';
        position: absolute;
        inset: 0;
        background: repeating-linear-gradient(
            -45deg,
            transparent,
            transparent 10px,
            rgba(108, 92, 231, 0.03) 10px,
            rgba(108, 92, 231, 0.03) 20px
        );
    }

    .coming-soon-badge {
        display: inline-block;
        background: rgba(108, 92, 231, 0.2);
        color: var(--primary-light);
        padding: 0.3rem 1.2rem;
        border-radius: 50px;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 1rem;
        position: relative;
    }

    .coming-soon-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 0.5rem;
        position: relative;
    }

    .coming-soon-desc {
        font-size: 0.85rem;
        color: var(--text-secondary);
        max-width: 500px;
        margin: 0 auto;
        position: relative;
    }

    .coming-soon-metrics {
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin-top: 1.5rem;
        position: relative;
    }

    .coming-soon-metric {
        text-align: center;
    }

    .coming-soon-metric-value {
        font-size: 1.2rem;
        font-weight: 700;
        color: var(--text-secondary);
    }

    .coming-soon-metric-label {
        font-size: 0.7rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        opacity: 0.7;
    }

    /* ===== Stock Header ===== */
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

    /* ===== Timestamp Badge ===== */
    .timestamp-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: rgba(0, 206, 201, 0.1);
        border: 1px solid rgba(0, 206, 201, 0.25);
        color: var(--accent);
        padding: 0.3rem 0.8rem;
        border-radius: 8px;
        font-size: 0.75rem;
        font-weight: 600;
    }

    /* ===== Animations ===== */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .hero-container, .kpi-card, .info-box, .disclaimer-box, .stock-header {
        animation: fadeInUp 0.6s ease-out forwards;
    }

    .kpi-card:nth-child(2) { animation-delay: 0.1s; }
    .kpi-card:nth-child(3) { animation-delay: 0.2s; }
    .kpi-card:nth-child(4) { animation-delay: 0.3s; }

    /* ===== Status Pill ===== */
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

    /* ===== Reason Text ===== */
    .reason-text {
        font-size: 0.78rem;
        color: var(--text-secondary);
        line-height: 1.5;
        max-width: 350px;
    }

    /* ===== Live Pulse ===== */
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
# Helper functions
# =========================
def get_risk_badge_html(risk_level: str) -> str:
    """Menghasilkan HTML badge untuk risk level."""
    css_class = risk_level.lower().replace(" ", "").replace("risk", "")
    if risk_level == "High Risk":
        css_class = "high"
    elif risk_level == "Medium Risk":
        css_class = "medium"
    elif risk_level == "Low Risk":
        css_class = "low"
    else:
        css_class = "normal"
    return f'<span class="risk-badge {css_class}">{risk_level}</span>'


def get_score_bar_html(score: float, risk_level: str) -> str:
    """Menghasilkan HTML score bar visual."""
    css_class = "normal"
    if risk_level == "High Risk":
        css_class = "high"
    elif risk_level == "Medium Risk":
        css_class = "medium"
    elif risk_level == "Low Risk":
        css_class = "low"
    pct = min(score * 100, 100)
    return f"""
    <div class="score-bar-container">
        <div class="score-bar-bg">
            <div class="score-bar-fill {css_class}" style="width:{pct:.0f}%"></div>
        </div>
        <span class="score-text" style="color: var(--text-primary);">{score:.2f}</span>
    </div>
    """


# =========================
# Sidebar
# =========================
with st.sidebar:
    st.markdown("""
<div class="sidebar-brand">
    <div class="sidebar-brand-icon">🛡️</div>
    <div class="sidebar-brand-name">IDX AI Surveillance</div>
    <div class="sidebar-brand-version">Market Surveillance Dashboard 1.0</div>
</div>
    """, unsafe_allow_html=True)

    st.markdown("## 🧭 Navigasi")

    page = st.radio(
        "Pilih halaman",
        ["🛡️ Market Surveillance", "🔍 Analisis Saham"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("## ⚙️ Pengaturan")

    # Ticker management
    st.markdown("**Saham yang Dipantau**")

    # Custom ticker input
    custom_ticker_input = st.text_input(
        "Tambah ticker (misal: BBNI.JK)",
        placeholder="Ketik kode saham, lalu Enter",
        help="Masukkan kode saham Yahoo Finance. Contoh: BBNI.JK, ASII.JK",
    )

    # Session state untuk custom tickers
    if "custom_tickers" not in st.session_state:
        st.session_state.custom_tickers = []

    if custom_ticker_input:
        ticker_upper = custom_ticker_input.strip().upper()
        if ticker_upper and ticker_upper not in DEFAULT_TICKERS and ticker_upper not in st.session_state.custom_tickers:
            if not ticker_upper.endswith(".JK"):
                ticker_upper = ticker_upper + ".JK"
            st.session_state.custom_tickers.append(ticker_upper)
            st.rerun()

    # Gabungkan tickers
    all_tickers = DEFAULT_TICKERS + st.session_state.custom_tickers

    # Tampilkan ticker list
    ticker_display = ", ".join([t.replace(".JK", "") for t in all_tickers])
    st.markdown(
        f"<div style='font-size:0.8rem; color:#A0A0B8; line-height:1.6;'>"
        f"📈 <b>{len(all_tickers)}</b> saham: {ticker_display}"
        f"</div>",
        unsafe_allow_html=True,
    )

    # Remove custom tickers
    if st.session_state.custom_tickers:
        remove_ticker = st.selectbox(
            "Hapus ticker tambahan",
            ["—"] + st.session_state.custom_tickers,
        )
        if remove_ticker != "—":
            st.session_state.custom_tickers.remove(remove_ticker)
            st.rerun()

    st.markdown("---")

    # Refresh button
    if st.button("🔄 Refresh Data Sekarang", use_container_width=True):
        st.cache_data.clear()
        st.rerun()


# =========================
# Load Data (cached pipeline)
# =========================
@st.cache_data(ttl=CACHE_TTL, show_spinner="📡 Mengambil data market terbaru...")
def load_surveillance_data(tickers_tuple):
    """Wrapper dengan tuple agar bisa di-cache oleh Streamlit."""
    return get_surveillance_data(list(tickers_tuple))


# Convert list ke tuple agar bisa di-hash oleh st.cache_data
tickers_tuple = tuple(all_tickers)

with st.spinner("📡 Memuat data surveillance..."):
    df = load_surveillance_data(tickers_tuple)

if df.empty:
    st.error("❌ Gagal mengambil data. Periksa koneksi internet atau coba refresh.")
    st.stop()

# Timestamp update terakhir
last_update = datetime.now().strftime("%d %b %Y, %H:%M WIB")


# ==========================================================
# PAGE 1: MARKET SURVEILLANCE OVERVIEW
# ==========================================================
if page == "🛡️ Market Surveillance":

    # --- Hero Header ---
    st.markdown(f"""
<div class="hero-container">
    <div class="hero-badge">🛡️ AI Market Surveillance System</div>
    <h1 class="hero-title">IDX AI Market Surveillance</h1>
    <p class="hero-subtitle">Pemantauan Aktivitas Pasar Tidak Biasa — Bursa Efek Indonesia</p>
    <p class="hero-description">
        Sistem pemantauan pasar berbasis AI untuk mendeteksi pergerakan harga dan volume saham
        yang tidak biasa secara real-time. Menggunakan algoritma <strong style="color:#A29BFE;">Isolation Forest</strong>
        untuk menganalisis pola perdagangan dan mengidentifikasi aktivitas yang menyimpang dari kondisi normal,
        terinspirasi dari konsep <strong style="color:#00CEC9;">Unusual Market Activity (UMA)</strong>
        yang diterapkan oleh Bursa Efek Indonesia.
    </p>
</div>
    """, unsafe_allow_html=True)

    # --- Disclaimer ---
    st.markdown("""
<div class="disclaimer-box">
    <div class="disclaimer-title">⚠️ Disclaimer — Bukan Rekomendasi Investasi</div>
    <p class="disclaimer-text">
        Dashboard ini dibuat untuk <strong>tujuan edukasi dan riset</strong>.
        Hasil deteksi anomali bukan merupakan rekomendasi untuk membeli, menjual, atau menahan saham tertentu.
        Sistem ini <strong>tidak menyatakan adanya manipulasi pasar</strong> dan hanya mendeteksi pola harga serta volume
        yang terlihat tidak biasa berdasarkan data historis. Segala keputusan investasi sepenuhnya menjadi tanggung jawab
        masing-masing individu.
    </p>
</div>
    """, unsafe_allow_html=True)

    # --- KPI Cards ---
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

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
<div class="kpi-card purple">
    <div class="kpi-icon">📡</div>
    <div class="kpi-label">Saham Dipantau</div>
    <div class="kpi-value purple">{total_monitored}</div>
</div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
<div class="kpi-card red">
    <div class="kpi-icon">🚨</div>
    <div class="kpi-label">Anomali Hari Ini</div>
    <div class="kpi-value red">{total_anomalies_today}</div>
</div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
<div class="kpi-card gold">
    <div class="kpi-icon">🔥</div>
    <div class="kpi-label">Skor Risiko Tertinggi</div>
    <div class="kpi-value gold">{highest_score:.2f}</div>
</div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
<div class="kpi-card teal">
    <div class="kpi-icon">🕐</div>
    <div class="kpi-label">Terakhir Diperbarui</div>
    <div class="kpi-value teal" style="font-size:1rem;">{last_update}</div>
</div>
        """, unsafe_allow_html=True)


    # --- Top Suspicious Stocks Today ---
    st.markdown("""
<div class="section-header">
    <span class="section-header-icon">🔍</span>
    <span class="section-header-text">Saham Mencurigakan Hari Ini</span>
    <span class="section-header-badge">LIVE RANKING</span>
</div>
    """, unsafe_allow_html=True)

    # Ambil data terbaru per ticker: skor tertinggi
    latest_scores = latest_df.groupby("ticker").agg(
        anomaly_score_normalized=("anomaly_score_normalized", "max"),
        risk_level=("risk_level", "first"),
        is_anomaly=("is_anomaly", "any"),
        anomaly_reason=("anomaly_reason", "first"),
        close=("close", "last"),
        daily_return=("daily_return", "last"),
        volume_spike_ratio=("volume_spike_ratio", "last"),
    ).reset_index()

    latest_scores = latest_scores.sort_values("anomaly_score_normalized", ascending=False)

    # Reassign risk level berdasarkan score terbaru
    from src.data_pipeline import _classify_risk
    latest_scores["risk_level"] = latest_scores["anomaly_score_normalized"].apply(_classify_risk)

    # Build HTML table
    table_rows = ""
    for rank, (_, row) in enumerate(latest_scores.iterrows(), 1):
        badge_html = get_risk_badge_html(row["risk_level"])
        score_html = get_score_bar_html(row["anomaly_score_normalized"], row["risk_level"])

        # Ambil anomaly reason jika memang anomali
        if row["is_anomaly"] and row["anomaly_reason"] != "Normal":
            reason_text = row["anomaly_reason"]
        else:
            reason_text = "Tidak ada aktivitas mencurigakan"

        # Format return
        ret_val = row["daily_return"] * 100 if pd.notna(row["daily_return"]) else 0
        ret_color = "#55EFC4" if ret_val >= 0 else "#FF8A8A"
        ret_sign = "+" if ret_val >= 0 else ""

        table_rows += f"""<tr><td style="font-weight:700; color:var(--primary-light);">{rank}</td><td style="font-weight:700;">{row['ticker']}</td><td>{score_html}</td><td>{badge_html}</td><td><span style="color:{ret_color}; font-weight:600;">{ret_sign}{ret_val:.2f}%</span></td><td><div class="reason-text">{reason_text}</div></td></tr>"""

    st.markdown(f"""
<table class="suspicious-table">
    <thead>
        <tr>
            <th>Rank</th>
            <th>Ticker</th>
            <th>Skor Anomali</th>
            <th>Status</th>
            <th>Return</th>
            <th>Potensi Alasan</th>
        </tr>
    </thead>
    <tbody>
        {table_rows}
    </tbody>
</table>
    """, unsafe_allow_html=True)


    # --- Market Risk Heatmap ---
    st.markdown("""
<div class="section-header">
    <span class="section-header-icon">🗺️</span>
    <span class="section-header-text">Peta Risiko Pasar</span>
    <span class="section-header-badge">HEATMAP</span>
</div>
    """, unsafe_allow_html=True)

    heatmap_data = latest_scores[["ticker", "anomaly_score_normalized", "risk_level"]].copy()
    heatmap_data["score_display"] = heatmap_data["anomaly_score_normalized"].apply(lambda x: f"{x:.2f}")

    fig_heatmap = px.treemap(
        heatmap_data,
        path=["ticker"],
        values=[1] * len(heatmap_data),  # Equal size
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
        textfont=dict(size=16, family="Inter, sans-serif"),
        hovertemplate="<b>%{label}</b><br>Skor Anomali: %{customdata[0]}<br>Status: %{customdata[1]}<extra></extra>",
        marker=dict(cornerradius=8),
    )

    fig_heatmap.update_layout(
        paper_bgcolor="rgba(30,30,46,0)",
        plot_bgcolor="rgba(30,30,46,0)",
        font=dict(family="Inter, sans-serif", color="#E8E8F0"),
        height=400,
        margin=dict(l=10, r=10, t=10, b=10),
        coloraxis_colorbar=dict(
            title=dict(text="Skor", font=dict(color="#A0A0B8")),
            tickfont=dict(color="#A0A0B8"),
        ),
    )

    st.plotly_chart(fig_heatmap, use_container_width=True)


    # --- Historical Anomaly Events ---
    st.markdown("""
<div class="section-header">
    <span class="section-header-icon">📋</span>
    <span class="section-header-text">Riwayat Anomali Terdeteksi</span>
    <span class="section-header-badge">ALL TICKERS</span>
</div>
    """, unsafe_allow_html=True)

    all_anomalies = df[df["is_anomaly"] == True].copy()

    if all_anomalies.empty:
        st.markdown("""
<div class="status-pill success">✅ Tidak ada anomali terdeteksi pada periode ini</div>
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
            "date": "📅 Tanggal",
            "ticker": "🏷️ Ticker",
            "close": "💰 Harga Close",
            "volume": "📊 Volume",
            "daily_return": "📈 Return (%)",
            "volume_spike_ratio": "⚡ Vol. Spike",
            "anomaly_score_normalized": "🎯 Skor",
            "risk_level": "🔰 Risk Level",
            "anomaly_reason": "📝 Alasan",
        })

        st.dataframe(
            all_anomalies_table,
            use_container_width=True,
            hide_index=True,
        )


    # --- Cara Kerja Sistem ---
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
        observasi — data yang lebih mudah diisolasi dianggap sebagai anomali. Skor anomali dinormalisasi
        ke skala <strong>0.00</strong> (normal) hingga <strong>1.00</strong> (sangat tidak biasa).
    </div>
</div>
</div>
    """, unsafe_allow_html=True)


    # --- Official UMA Comparison (Coming Soon) ---
    st.markdown("""
<div class="section-header">
    <span class="section-header-icon">🏛️</span>
    <span class="section-header-text">Perbandingan dengan UMA Resmi BEI</span>
    <span class="section-header-badge">COMING SOON</span>
</div>
    """, unsafe_allow_html=True)

    st.markdown("""
<div class="coming-soon-container">
    <div class="coming-soon-badge">🔒 Coming Soon</div>
    <div class="coming-soon-title">Integrasi dengan Pengumuman UMA Resmi</div>
    <div class="coming-soon-desc">
        Fitur ini akan membandingkan hasil deteksi anomali sistem dengan pengumuman UMA resmi
        dari Bursa Efek Indonesia untuk mengukur akurasi prediksi.
    </div>
    <div class="coming-soon-metrics">
        <div class="coming-soon-metric">
            <div class="coming-soon-metric-value">—</div>
            <div class="coming-soon-metric-label">Status UMA Resmi</div>
        </div>
        <div class="coming-soon-metric">
            <div class="coming-soon-metric-value">—</div>
            <div class="coming-soon-metric-label">Risk Level Sistem</div>
        </div>
        <div class="coming-soon-metric">
            <div class="coming-soon-metric-value">—</div>
            <div class="coming-soon-metric-label">Hari Sebelum Pengumuman</div>
        </div>
    </div>
</div>
    """, unsafe_allow_html=True)


# ==========================================================
# PAGE 2: DETAILED STOCK ANALYSIS
# ==========================================================
elif page == "🔍 Analisis Saham":

    # Stock selector in sidebar is already available, add one here for clarity
    available_tickers = sorted(df["ticker"].unique())

    with st.sidebar:
        st.markdown("---")
        st.markdown("## 📊 Pilih Saham")
        selected_ticker = st.selectbox(
            "Kode saham untuk analisis detail",
            available_tickers,
            help="Pilih saham yang ingin dianalisis secara mendalam",
        )

    # Filter data
    stock_df = df[df["ticker"] == selected_ticker].copy().sort_values("date")
    anomaly_df = stock_df[stock_df["is_anomaly"] == True].copy()

    if stock_df.empty:
        st.warning(f"⚠️ Data tidak tersedia untuk {selected_ticker}.")
        st.stop()

    # --- Stock Header ---
    latest = stock_df.iloc[-1]
    latest_close = latest["close"]
    latest_return = latest["daily_return"] * 100 if pd.notna(latest["daily_return"]) else 0
    latest_risk = latest["risk_level"]
    latest_score = latest["anomaly_score_normalized"]

    change_class = "positive" if latest_return >= 0 else "negative"
    change_sign = "+" if latest_return >= 0 else ""
    badge_html = get_risk_badge_html(latest_risk)

    st.markdown(f"""
<div class="stock-header">
    <div class="stock-ticker-big">{selected_ticker}</div>
    <div class="stock-info">
        <span class="stock-price">Rp {latest_close:,.0f}</span>
        <span class="stock-change {change_class}">{change_sign}{latest_return:.2f}%</span>
        <br>
        <span style="font-size:0.85rem; color: var(--text-secondary); margin-right: 0.5rem;">Skor: {latest_score:.2f}</span>
        {badge_html}
    </div>
</div>
    """, unsafe_allow_html=True)


    # --- Feature Breakdown Cards ---
    st.markdown("""
<div class="section-header">
    <span class="section-header-icon">📊</span>
    <span class="section-header-text">Breakdown Fitur Terbaru</span>
    <span class="section-header-badge">LATEST</span>
</div>
    """, unsafe_allow_html=True)

    fc1, fc2, fc3 = st.columns(3)

    with fc1:
        val = latest["daily_return"] * 100 if pd.notna(latest["daily_return"]) else 0
        color = "#55EFC4" if val >= 0 else "#FF8A8A"
        st.markdown(f"""
<div class="feature-card">
    <div class="feature-card-label">📈 Daily Return</div>
    <div class="feature-card-value" style="color:{color};">{val:+.2f}%</div>
    <div class="feature-card-desc">Perubahan harga close harian</div>
</div>
        """, unsafe_allow_html=True)

    with fc2:
        val = latest["volume_spike_ratio"] if pd.notna(latest["volume_spike_ratio"]) else 0
        color = "#FF8A8A" if val >= 3 else "#A29BFE" if val >= 1.5 else "#55EFC4"
        st.markdown(f"""
<div class="feature-card">
    <div class="feature-card-label">⚡ Volume Spike Ratio</div>
    <div class="feature-card-value" style="color:{color};">{val:.2f}x</div>
    <div class="feature-card-desc">Dibanding rata-rata 20 hari</div>
</div>
        """, unsafe_allow_html=True)

    with fc3:
        val = latest["rolling_volatility_20"] * 100 if pd.notna(latest["rolling_volatility_20"]) else 0
        st.markdown(f"""
<div class="feature-card">
    <div class="feature-card-label">📉 Rolling Volatility 20</div>
    <div class="feature-card-value" style="color:#FDCB6E;">{val:.2f}%</div>
    <div class="feature-card-desc">Volatilitas return 20 hari</div>
</div>
        """, unsafe_allow_html=True)

    fc4, fc5, fc6 = st.columns(3)

    with fc4:
        val = latest["return_zscore_20"] if pd.notna(latest["return_zscore_20"]) else 0
        color = "#FF8A8A" if abs(val) >= 2 else "#A29BFE" if abs(val) >= 1 else "#55EFC4"
        st.markdown(f"""
<div class="feature-card">
    <div class="feature-card-label">🎯 Return Z-score</div>
    <div class="feature-card-value" style="color:{color};">{val:+.2f}</div>
    <div class="feature-card-desc">Deviasi return dari pola 20 hari</div>
</div>
        """, unsafe_allow_html=True)

    with fc5:
        val = latest["volume_zscore_20"] if pd.notna(latest["volume_zscore_20"]) else 0
        color = "#FF8A8A" if abs(val) >= 2 else "#A29BFE" if abs(val) >= 1 else "#55EFC4"
        st.markdown(f"""
<div class="feature-card">
    <div class="feature-card-label">📦 Volume Z-score</div>
    <div class="feature-card-value" style="color:{color};">{val:+.2f}</div>
    <div class="feature-card-desc">Deviasi volume dari pola 20 hari</div>
</div>
        """, unsafe_allow_html=True)

    with fc6:
        val = latest["price_gap_ma_20"] * 100 if pd.notna(latest["price_gap_ma_20"]) else 0
        color = "#FF8A8A" if abs(val) >= 8 else "#FDCB6E" if abs(val) >= 4 else "#55EFC4"
        st.markdown(f"""
<div class="feature-card">
    <div class="feature-card-label">📐 Price Gap MA20</div>
    <div class="feature-card-value" style="color:{color};">{val:+.2f}%</div>
    <div class="feature-card-desc">Jarak harga dari MA 20 hari</div>
</div>
        """, unsafe_allow_html=True)


    # --- Candlestick Chart ---
    st.markdown(f"""
<div class="section-header">
    <span class="section-header-icon">🕯️</span>
    <span class="section-header-text">Candlestick Chart — {selected_ticker}</span>
    <span class="section-header-badge">INTERACTIVE</span>
</div>
    """, unsafe_allow_html=True)

    fig_price = go.Figure()

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

    if not anomaly_df.empty:
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
                name="⚠ Anomali",
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


    # --- Volume Chart ---
    st.markdown(f"""
<div class="section-header">
    <span class="section-header-icon">📊</span>
    <span class="section-header-text">Volume Perdagangan — {selected_ticker}</span>
</div>
    """, unsafe_allow_html=True)

    fig_volume = go.Figure()

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

    if not anomaly_df.empty:
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
                name="⚠ Anomali Volume",
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


    # --- Historical Anomaly Timeline ---
    st.markdown(f"""
<div class="section-header">
    <span class="section-header-icon">📋</span>
    <span class="section-header-text">Riwayat Anomali — {selected_ticker}</span>
    <span class="section-header-badge">{len(anomaly_df)} RECORDS</span>
</div>
    """, unsafe_allow_html=True)

    if anomaly_df.empty:
        st.markdown("""
<div class="status-pill success">✅ Tidak ada anomali terdeteksi pada saham ini dalam periode data</div>
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
            "date": "📅 Tanggal",
            "ticker": "🏷️ Ticker",
            "close": "💰 Harga Close",
            "volume": "📊 Volume",
            "daily_return": "📈 Return (%)",
            "volume_spike_ratio": "⚡ Vol. Spike",
            "price_range_pct": "📐 Range (%)",
            "anomaly_score_normalized": "🎯 Skor",
            "risk_level": "🔰 Risk",
            "anomaly_reason": "📝 Alasan",
        })

        anomaly_table = anomaly_table.sort_values("🎯 Skor", ascending=False)

        st.dataframe(
            anomaly_table,
            use_container_width=True,
            hide_index=True,
        )


# =========================
# Footer (both pages)
# =========================
st.markdown(f"""
<div class="footer">
    <p>
        <span class="live-dot"></span>
        <strong style="color:#A29BFE;">IDX AI Market Surveillance Dashboard</strong> —
        Dibuat untuk tujuan edukasi & riset<br>
        Data bersumber dari Yahoo Finance • Auto-refresh setiap 5 menit • Tidak terafiliasi dengan BEI<br>
        <span style="font-size:0.7rem;">Update terakhir: {last_update}</span>
    </p>
</div>
""", unsafe_allow_html=True)
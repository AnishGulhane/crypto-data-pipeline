import streamlit as st
import pandas as pd
import psycopg2
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Crypto Terminal", layout="wide")
st_autorefresh(interval=5000, key="refresh")

theme = st.get_option("theme.base")
is_dark = theme == "dark"

# =========================
# COLORS
# =========================
if is_dark:
    BG = "rgba(255,255,255,0.05)"
    BORDER = "rgba(255,255,255,0.1)"
    TEXT = "#ffffff"
    SUBTEXT = "#a1a1aa"
else:
    BG = "rgba(255,255,255,0.9)"
    BORDER = "rgba(0,0,0,0.08)"
    TEXT = "#111827"
    SUBTEXT = "#6b7280"

COIN_COLORS = {
    "bitcoin": "#f7931a",
    "ethereum": "#627eea",
    "cardano": "#2a6df4",
    "solana": "#00ffa3",
    "dogecoin": "#c2a633"
}

# =========================
# CSS
# =========================
st.markdown(f"""
<style>
.glass {{
    background: {BG};
    backdrop-filter: blur(14px);
    border: 1px solid {BORDER};
    border-radius: 18px;
    padding: 20px;
}}
.empty {{
    text-align:center;
    padding:40px;
    color:{SUBTEXT};
}}
</style>
""", unsafe_allow_html=True)

# =========================
# DB
# =========================
conn = psycopg2.connect(
    host="localhost",
    port="5433",
    database="airflow",
    user="airflow",
    password="airflow"
)

df = pd.read_sql("SELECT * FROM crypto_raw ORDER BY processed_at ASC;", conn)
conn.close()

df["processed_at"] = pd.to_datetime(df["processed_at"])

# =========================
# SIDEBAR
# =========================
st.sidebar.markdown("## 💹 Terminal")

view = st.sidebar.radio("View", ["Market", "Charts"])

coin_list = sorted(df["coin"].unique())
selected_asset = st.sidebar.selectbox("Asset", coin_list)

timeframe = st.sidebar.selectbox(
    "Timeframe",
    ["1 Min", "5 Min", "15 Min", "1 Hour"]
)

# =========================
# TIMEFRAME FILTER
# =========================
if timeframe == "1 Min":
    df_filtered = df.tail(100)
elif timeframe == "5 Min":
    df_filtered = df.tail(300)
elif timeframe == "15 Min":
    df_filtered = df.tail(800)
else:
    df_filtered = df

# =========================
# DATA
# =========================
pivot_df = df_filtered.pivot_table(
    index="processed_at",
    columns="coin",
    values="price_usd",
    aggfunc="mean"
).ffill()

# =========================
# HEADER
# =========================
st.markdown(f"""
<div class="glass">
    <h2 style="color:{TEXT};">💹 Crypto Terminal</h2>
    <p style="color:{SUBTEXT};">
    Real-time crypto analytics pipeline
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# =========================
# HELPER: AUTO SCALE
# =========================
def auto_scale(fig, data):
    y_min = data.min().min()
    y_max = data.max().max()

    if y_max == y_min:
        pad = 1
    else:
        pad = (y_max - y_min) * 0.15

    fig.update_yaxes(range=[y_min - pad, y_max + pad])

# =========================
# MARKET VIEW
# =========================
if view == "Market":

    st.subheader("📊 Market Overview")

    cols = st.columns(len(pivot_df.columns))

    for i, c in enumerate(pivot_df.columns):
        latest = pivot_df[c].iloc[-1]
        prev = pivot_df[c].iloc[-2] if len(pivot_df[c]) > 1 else latest
        change = ((latest - prev) / latest) * 100 if latest else 0

        color = "#30d158" if change >= 0 else "#ff453a"
        arrow = "▲" if change >= 0 else "▼"

        with cols[i]:
            st.markdown(f"""
            <div class="glass">
                <div style="color:{SUBTEXT};">{c.upper()}</div>
                <div style="color:{TEXT}; font-size:26px;">
                    ${latest:,.0f}
                </div>
                <div style="color:{color};">
                    {arrow} {abs(change):.2f}%
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    selected = st.multiselect("Select coins", list(pivot_df.columns))

    if not selected:
        st.markdown("""
        <div class="empty">📊 Select coins to view charts</div>
        """, unsafe_allow_html=True)

    else:
        cols = st.columns(len(selected))

        for i, c in enumerate(selected):
            with cols[i]:

                color = COIN_COLORS.get(c, "#ffffff")

                st.markdown(f"""
                <div style="color:{color}; font-weight:600;">
                    {c.upper()} Price
                </div>
                """, unsafe_allow_html=True)

                fig = go.Figure()

                fig.add_trace(go.Scatter(
                    x=pivot_df.index,
                    y=pivot_df[c],
                    line=dict(color=color, width=3)
                ))

                auto_scale(fig, pivot_df[[c]])

                fig.update_layout(
                    template="plotly_dark" if is_dark else "plotly_white",
                    height=300,
                    margin=dict(l=10, r=10, t=10, b=10)
                )

                st.plotly_chart(fig, use_container_width=True)

    # =========================
    # ADVANCED ANALYTICS (FIXED)
    # =========================
    st.markdown("---")
    st.subheader("📈 Advanced Analytics")

    # Normalized
    norm_df = pivot_df / pivot_df.iloc[0] * 100

    fig_norm = go.Figure()
    for c in norm_df.columns:
        fig_norm.add_trace(go.Scatter(
            x=norm_df.index,
            y=norm_df[c],
            name=c,
            line=dict(color=COIN_COLORS.get(c, "#888"))
        ))

    auto_scale(fig_norm, norm_df)

    fig_norm.update_layout(
        template="plotly_dark" if is_dark else "plotly_white",
        title="Normalized Growth (Base = 100)"
    )

    st.plotly_chart(fig_norm, use_container_width=True)

    # % Change
    pct_df = pivot_df.pct_change() * 100

    fig_pct = go.Figure()
    for c in pct_df.columns:
        fig_pct.add_trace(go.Scatter(
            x=pct_df.index,
            y=pct_df[c],
            name=c,
            line=dict(color=COIN_COLORS.get(c, "#888"))
        ))

    auto_scale(fig_pct, pct_df)

    fig_pct.update_layout(
        template="plotly_dark" if is_dark else "plotly_white",
        title="Percentage Change (%)"
    )

    st.plotly_chart(fig_pct, use_container_width=True)

# =========================
# CHART VIEW
# =========================
if view == "Charts":

    st.subheader(f"📈 {selected_asset.upper()} Detailed View")

    color = COIN_COLORS.get(selected_asset, "#ffffff")

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=pivot_df.index,
        y=pivot_df[selected_asset],
        line=dict(color=color, width=3)
    ))

    auto_scale(fig, pivot_df[[selected_asset]])

    fig.update_layout(
        template="plotly_dark" if is_dark else "plotly_white",
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

# =========================
# TABLE
# =========================
st.markdown("---")
st.dataframe(df.tail(10), use_container_width=True)
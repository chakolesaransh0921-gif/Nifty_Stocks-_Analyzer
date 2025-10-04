import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# --- Page Setup ---
st.set_page_config(page_title="📊 Nifty Golden Dashboard", layout="wide", page_icon="💰")

st.markdown("""
# 💰 Nifty Stocks Golden Dashboard
Analyze your stocks with **SMA indicators**, **daily change metrics**, **golden-themed charts**, and interactive dashboards. 🚀
""")

# --- Load Data ---
try:
    df = pd.read_csv("Stocks_2025.csv")
except FileNotFoundError:
    st.error("❌ CSV file not found! Place `Stocks_2025.csv` in the same folder.")
    st.stop()

# --- Clean Data ---
if "Unnamed: 0" in df.columns:
    df.drop("Unnamed: 0", axis=1, inplace=True)

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df.dropna(subset=["Date"], inplace=True)
df["Stock"] = df["Stock"].astype(str).replace(" ", "", regex=True)

required_cols = {"Date", "Stock", "Category", "Close"}
missing = required_cols - set(df.columns)
if missing:
    st.error(f"❌ Missing columns: {missing}")
    st.stop()

# --- Feature Engineering ---
df["SMA_50"] = df["Close"].rolling(window=50, min_periods=1).mean()
df["SMA_100"] = df["Close"].rolling(window=100, min_periods=1).mean()
df["Change_%"] = df["Close"].pct_change() * 100
df["Volatility"] = df["Change_%"].rolling(window=20).std()

# --- Sidebar Filters ---
st.sidebar.header("🎛️ Filters & Options")

categories = sorted(df["Category"].dropna().unique())
category = st.sidebar.selectbox("Select Category", categories)

filtered_df = df[df["Category"] == category]
stocks = sorted(filtered_df["Stock"].dropna().unique())
selected_stocks = st.sidebar.multiselect("Select Stocks", stocks, default=[stocks[0]])

min_date, max_date = df["Date"].min(), df["Date"].max()
date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date])
start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
filtered_df = filtered_df[(filtered_df["Date"] >= start_date) & (filtered_df["Date"] <= end_date)]

# --- Toggle Buttons ---
st.sidebar.header("📌 Display Options")
show_close = st.sidebar.button("Toggle Close Price")
show_sma50 = st.sidebar.button("Toggle SMA 50")
show_sma100 = st.sidebar.button("Toggle SMA 100")

# --- Theme & Golden Colors ---
theme = st.sidebar.radio("Theme", ["Light", "Dark"])
template = "plotly_white" if theme == "Light" else "plotly_dark"

gold_color = "#FFD700"  # Golden for bars/lines
sma50_color = "#FFA500"
sma100_color = "#FF8C00"
change_color = "#FFD700"
vol_color = "#DAA520"

# --- Tabs ---
tab1, tab2, tab3, tab4 = st.tabs(["💹 Price & SMA", "📈 Daily Change", "📉 Volatility", "📥 Export Data"])

# --- Tab 1: Price & SMA ---
with tab1:
    st.subheader("💹 Price & SMA Dashboard")
    fig = go.Figure()
    for stock in selected_stocks:
        data = filtered_df[filtered_df["Stock"] == stock]
        if show_close or True:
            fig.add_trace(go.Scatter(x=data["Date"], y=data["Close"], mode="lines", name=f"{stock} Close", line=dict(color=gold_color, width=2)))
        if show_sma50 or True:
            fig.add_trace(go.Scatter(x=data["Date"], y=data["SMA_50"], mode="lines", name=f"{stock} SMA 50", line=dict(color=sma50_color, dash="dot")))
        if show_sma100 or True:
            fig.add_trace(go.Scatter(x=data["Date"], y=data["SMA_100"], mode="lines", name=f"{stock} SMA 100", line=dict(color=sma100_color, dash="dash")))
    fig.update_layout(title=f"Price & SMA - {category}", xaxis_title="Date", yaxis_title="Price (₹)", template=template, hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

# --- Tab 2: Daily % Change ---
with tab2:
    st.subheader("📈 Daily % Change")
    fig2 = go.Figure()
    for stock in selected_stocks:
        data = filtered_df[filtered_df["Stock"] == stock]
        fig2.add_trace(go.Bar(x=data["Date"], y=data["Change_%"], name=f"{stock} %Change", marker_color=change_color))
    fig2.update_layout(title="Daily % Change", xaxis_title="Date", yaxis_title="% Change", template=template)
    st.plotly_chart(fig2, use_container_width=True)

# --- Tab 3: Volatility ---
with tab3:
    st.subheader("📉 20-Day Rolling Volatility")
    fig3 = go.Figure()
    for stock in selected_stocks:
        data = filtered_df[filtered_df["Stock"] == stock]
        fig3.add_trace(go.Scatter(x=data["Date"], y=data["Volatility"], mode="lines+markers", name=f"{stock} Volatility", line=dict(color=vol_color)))
    fig3.update_layout(title="Volatility", xaxis_title="Date", yaxis_title="Volatility (%)", template=template)
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("✨ Key Metrics")
    for stock in selected_stocks:
        data = filtered_df[filtered_df["Stock"] == stock]
        avg_price = np.round(data["Close"].mean(), 2)
        total_change = np.round(((data["Close"].iloc[-1]-data["Close"].iloc[0])/data["Close"].iloc[0])*100, 2)
        vol = np.round(data["Volatility"].mean(), 2)
        col1, col2, col3 = st.columns(3)
        with col1: st.metric(f"{stock} Avg Price", f"₹{avg_price}", delta=None)
        with col2: st.metric(f"{stock} Total Change %", f"{total_change}%", delta=None)
        with col3: st.metric(f"{stock} Avg Volatility", f"{vol}%", delta=None)

# --- Tab 4: Export Data ---
with tab4:
    st.subheader("📥 Download Filtered Data")
    data_to_export = filtered_df[filtered_df["Stock"].isin(selected_stocks)]
    st.dataframe(data_to_export.tail(10))
    csv = data_to_export.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download CSV", data=csv, file_name="nifty_golden_data.csv", mime="text/csv")

st.markdown("---")
st.markdown("Developed with ❤️ by **Saransh Chakole**")

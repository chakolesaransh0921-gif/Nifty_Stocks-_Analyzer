import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# --- Page Setup ---
st.set_page_config(page_title="📊 Nifty Stocks Dashboard", layout="wide", page_icon="📈")

# --- Header ---
st.title("📈 Nifty Stocks Interactive Dashboard")
st.markdown("""
Analyze Nifty stocks dynamically with **SMA indicators**, **daily change metrics**, and **volatility insights**.  
Customize charts, select multiple stocks, and explore your data interactively. 🚀
""")

# --- Load Data ---
try:
    df = pd.read_csv("Stocks_2025.csv")
except FileNotFoundError:
    st.error("❌ CSV file not found! Place `Stocks_2025.csv` in the same folder.")
    st.stop()

# --- Clean & Prepare Data ---
if "Unnamed: 0" in df.columns:
    df.drop("Unnamed: 0", axis=1, inplace=True)

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df.dropna(subset=["Date"], inplace=True)
df["Stock"] = df["Stock"].astype(str).replace(" ", "", regex=True)

# Verify columns
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

# Category & Stock selection
categories = sorted(df["Category"].dropna().unique())
category = st.sidebar.selectbox("Select Category", categories)

filtered_df = df[df["Category"] == category]
stocks = sorted(filtered_df["Stock"].dropna().unique())
selected_stocks = st.sidebar.multiselect("Select Stocks", stocks, default=[stocks[0]])

# Date range filter
min_date, max_date = df["Date"].min(), df["Date"].max()
date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date])
start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
filtered_df = filtered_df[(filtered_df["Date"] >= start_date) & (filtered_df["Date"] <= end_date)]

# Theme & Colors
theme = st.sidebar.radio("Theme", ["Light", "Dark"])
template = "plotly_white" if theme == "Light" else "plotly_dark"

st.sidebar.subheader("🎨 Line Colors")
close_color = st.sidebar.color_picker("Close Price", "#00CC96")
sma50_color = st.sidebar.color_picker("SMA 50", "#636EFA")
sma100_color = st.sidebar.color_picker("SMA 100", "#EF553B")
change_color = st.sidebar.color_picker("Daily % Change", "#FFB700")
vol_color = st.sidebar.color_picker("Volatility", "#AB63FA")

# Toggle lines
show_close = st.sidebar.checkbox("Show Close Price", True)
show_sma50 = st.sidebar.checkbox("Show SMA 50", True)
show_sma100 = st.sidebar.checkbox("Show SMA 100", True)
show_change = st.sidebar.checkbox("Show Daily % Change", True)
show_volatility = st.sidebar.checkbox("Show Volatility", True)

# --- Tabs ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Price & SMA", "📈 Daily Change", "📉 Volatility", "📥 Export Data"])

# --- Tab 1: Price & SMA ---
with tab1:
    st.subheader("Price & SMA Trends")
    fig = go.Figure()
    for stock in selected_stocks:
        data = filtered_df[filtered_df["Stock"] == stock]
        if show_close:
            fig.add_trace(go.Scatter(x=data["Date"], y=data["Close"], mode="lines", name=f"{stock} Close", line=dict(color=close_color, width=2)))
        if show_sma50:
            fig.add_trace(go.Scatter(x=data["Date"], y=data["SMA_50"], mode="lines", name=f"{stock} SMA 50", line=dict(color=sma50_color, dash="dot")))
        if show_sma100:
            fig.add_trace(go.Scatter(x=data["Date"], y=data["SMA_100"], mode="lines", name=f"{stock} SMA 100", line=dict(color=sma100_color, dash="dash")))

    fig.update_layout(title=f"Price & SMA - {category}", xaxis_title="Date", yaxis_title="Price (₹)", template=template, hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

# --- Tab 2: Daily % Change ---
with tab2:
    st.subheader("Daily % Change")
    fig2 = go.Figure()
    for stock in selected_stocks:
        data = filtered_df[filtered_df["Stock"] == stock]
        if show_change:
            fig2.add_trace(go.Scatter(x=data["Date"], y=data["Change_%"], mode="lines+markers", name=f"{stock} %Change", line=dict(color=change_color)))
    fig2.update_layout(title=f"Daily % Change - {category}", xaxis_title="Date", yaxis_title="% Change", template=template)
    st.plotly_chart(fig2, use_container_width=True)

# --- Tab 3: Volatility ---
with tab3:
    st.subheader("20-Day Rolling Volatility")
    fig3 = go.Figure()
    for stock in selected_stocks:
        data = filtered_df[filtered_df["Stock"] == stock]
        if show_volatility:
            fig3.add_trace(go.Scatter(x=data["Date"], y=data["Volatility"], mode="lines+markers", name=f"{stock} Volatility", line=dict(color=vol_color)))
    fig3.update_layout(title=f"Volatility - {category}", xaxis_title="Date", yaxis_title="Volatility (%)", template=template)
    st.plotly_chart(fig3, use_container_width=True)

    # Metrics cards
    st.subheader("Key Metrics")
    for stock in selected_stocks:
        data = filtered_df[filtered_df["Stock"] == stock]
        avg_price = np.round(data["Close"].mean(), 2)
        total_change = np.round(((data["Close"].iloc[-1] - data["Close"].iloc[0]) / data["Close"].iloc[0]) * 100, 2)
        vol = np.round(data["Volatility"].mean(), 2)
        col1, col2, col3 = st.columns(3)
        with col1: st.metric(f"{stock} Average Price", f"₹{avg_price}")
        with col2: st.metric(f"{stock} Total Change %", f"{total_change}%")
        with col3: st.metric(f"{stock} Avg Volatility", f"{vol}%")

# --- Tab 4: Export Data ---
with tab4:
    st.subheader("Download Filtered Data")
    data_to_export = filtered_df[filtered_df["Stock"].isin(selected_stocks)]
    st.dataframe(data_to_export.tail(10))
    csv = data_to_export.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download CSV", data=csv, file_name="filtered_nifty_data.csv", mime="text/csv")

st.markdown("---")
st.markdown("Developed with ❤️ by **Saransh Chakole**")

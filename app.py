import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- Page Setup ---
st.set_page_config(page_title="📊 Nifty Stocks Analyzer", layout="wide", page_icon="📈")

# --- Title Section ---
st.title("📈 Nifty Stocks Analyzer Dashboard")
st.markdown("""
Enhance your stock analysis experience with dynamic **SMA indicators**,  
custom **color themes**, and **interactive stock comparisons**. 🚀
""")

# --- Load Data ---
try:
    df = pd.read_csv("Stocks_2025.csv")
except FileNotFoundError:
    st.error("❌ CSV file not found! Check the path: `../DataSets/Nifty/Stocks_2025.csv`")
    st.stop()

# --- Clean & Prepare Data ---
if "Unnamed: 0" in df.columns:
    df = df.drop("Unnamed: 0", axis=1)

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df.dropna(subset=["Date"])

df["Stock"] = df["Stock"].astype(str).replace(" ", "", regex=True)

required_cols = {"Date", "Stock", "Category", "Close"}
missing = required_cols - set(df.columns)
if missing:
    st.error(f"❌ Missing columns in CSV: {missing}")
    st.stop()

# --- Compute Moving Averages ---
df["SMA_50"] = df["Close"].rolling(window=50, min_periods=1).mean()
df["SMA_100"] = df["Close"].rolling(window=100, min_periods=1).mean()

# --- Sidebar Filters ---
st.sidebar.header("🎛️ Filter & Display Options")

# Category & Stock filters
categories = sorted(df["Category"].dropna().unique())
selected_category = st.sidebar.selectbox("Select Category", categories)

filtered_df = df[df["Category"] == selected_category]

stocks = sorted(filtered_df["Stock"].dropna().unique())
selected_stocks = st.sidebar.multiselect("Select Stock(s)", stocks, default=[stocks[0]])

# Date Range Filter
min_date, max_date = df["Date"].min(), df["Date"].max()
date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date])

# Visibility toggles
show_close = st.sidebar.checkbox("Show Close Price", True)
show_sma50 = st.sidebar.checkbox("Show SMA 50", True)
show_sma100 = st.sidebar.checkbox("Show SMA 100", True)

# Color pickers
st.sidebar.markdown("---")
st.sidebar.subheader("🎨 Customize Chart Colors")
close_color = st.sidebar.color_picker("Close Price Color", "#00cc96")
sma50_color = st.sidebar.color_picker("SMA 50 Color", "#636EFA")
sma100_color = st.sidebar.color_picker("SMA 100 Color", "#EF553B")

# --- Filter by Date ---
start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
df = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)]

# --- Plotly Interactive Chart ---
fig = go.Figure()

for stock in selected_stocks:
    stock_data = df[df["Stock"] == stock]
    if show_close:
        fig.add_trace(go.Scatter(
            x=stock_data["Date"], y=stock_data["Close"], mode='lines', name=f"{stock} Close",
            line=dict(color=close_color, width=2)
        ))
    if show_sma50:
        fig.add_trace(go.Scatter(
            x=stock_data["Date"], y=stock_data["SMA_50"], mode='lines', name=f"{stock} SMA 50",
            line=dict(color=sma50_color, dash='dot')
        ))
    if show_sma100:
        fig.add_trace(go.Scatter(
            x=stock_data["Date"], y=stock_data["SMA_100"], mode='lines', name=f"{stock} SMA 100",
            line=dict(color=sma100_color, dash='dash')
        ))

fig.update_layout(
    title=f"📊 Stock Trend Visualization ({selected_category})",
    xaxis_title="Date",
    yaxis_title="Price (₹)",
    template="plotly_white",
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=40, r=40, t=60, b=40),
)

# --- Display Chart ---
st.plotly_chart(fig, use_container_width=True)

# --- Data Preview ---
with st.expander("📋 View Data Table"):
    st.dataframe(df[df["Stock"].isin(selected_stocks)].tail(10))

# --- Footer ---
st.markdown("""
---
💡 *Tip:* Try selecting multiple stocks and changing colors to compare them visually in real time.  
Developed with ❤️ by **Saransh Chakole**
""")

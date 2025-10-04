import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sb
import matplotlib.pyplot as plt

# --- Page Config ---
st.set_page_config(page_title="Nifty Stocks Analyzer", page_icon="📈", layout="wide")

# --- App Title ---
st.title("📈 Nifty Stocks Analysis Dashboard")
st.markdown("Explore Nifty stock trends with **SMA 50** and **SMA 100** indicators")

# --- Load Data ---
try:
    df = pd.read_csv("Stocks_2025.csv")
except FileNotFoundError:
    st.error("❌ CSV file not found! Please check the file path: `../DataSets/Nifty/Stocks_2025.csv`")
    st.stop()

# --- Clean and Prepare Data ---
# Drop unwanted columns if present
if "Unnamed: 0" in df.columns:
    df = df.drop("Unnamed: 0", axis=1)

# Convert Date safely
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df.dropna(subset=["Date"])

# Clean Stock names
df["Stock"] = df["Stock"].astype(str).replace(" ", "", regex=True)

# --- Check required columns ---
required_cols = {"Date", "Stock", "Category", "Close"}
missing = required_cols - set(df.columns)
if missing:
    st.error(f"❌ Missing columns in CSV: {missing}")
    st.stop()

# --- Calculate Moving Averages ---
df["SMA_50"] = df["Close"].rolling(window=50, min_periods=1).mean()
df["SMA_100"] = df["Close"].rolling(window=100, min_periods=1).mean()

# --- Sidebar Filters ---
st.sidebar.header("🔍 Filter Options")

categories = sorted(df["Category"].dropna().unique())
selected_category = st.sidebar.selectbox("Select Category", categories)

filtered_df = df[df["Category"] == selected_category]

stocks = sorted(filtered_df["Stock"].dropna().unique())
selected_stock = st.sidebar.selectbox("Select Stock", stocks)

stock_data = filtered_df[filtered_df["Stock"] == selected_stock]

# --- Chart Section ---
st.markdown(f"### 📊 Stock Trend — {selected_stock}")

fig, ax = plt.subplots(figsize=(12, 6))
sb.lineplot(x="Date", y="Close", data=stock_data, label="Close Price", color="green", ax=ax)
sb.lineplot(x="Date", y="SMA_50", data=stock_data, label="SMA 50", color="blue", ax=ax)
sb.lineplot(x="Date", y="SMA_100", data=stock_data, label="SMA 100", color="orange", ax=ax)

plt.xticks(rotation=45)
plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()
plt.grid(True, linestyle="--", alpha=0.5)

st.pyplot(fig)

# --- Data Preview (Optional) ---
with st.expander("📋 View Raw Data"):
    st.dataframe(stock_data.tail(10))

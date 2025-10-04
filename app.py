import streamlit as st
import pandas as pd
import seaborn as sb
import matplotlib.pyplot as plt

# Load Data
df = pd.read_csv("Stocks_2025.csv")
df = df.drop("Unnamed: 0", axis=1)

# Convert Data Types
df["Date"] = pd.to_datetime(df["Date"])
df["Stock"] = df["Stock"].replace(" ", "", regex=True)

# Calculate Moving Averages
df["SMA_50"] = df["Close"].rolling(window=50, min_periods=1).mean()
df["SMA_100"] = df["Close"].rolling(window=100, min_periods=1).mean()

# Streamlit UI
st.title("📈 Nifty Stocks Analysis Dashboard")
st.markdown("### Explore stock trends with SMA indicators")

# Select Category
categories = sorted(df["Category"].dropna().unique())
selected_category = st.selectbox("Select a Category", categories)

filtered_df = df[df["Category"] == selected_category]

# Select Stock
stocks = sorted(filtered_df["Stock"].dropna().unique())
selected_stock = st.selectbox("Select a Stock", stocks)

stock_data = filtered_df[filtered_df["Stock"] == selected_stock]

# Display line chart
st.markdown(f"### Stock Price Trend — {selected_stock}")

fig, ax = plt.subplots(figsize=(12, 6))
sb.lineplot(x="Date", y="Close", data=stock_data, label="Close", color="green", ax=ax)
sb.lineplot(x="Date", y="SMA_50", data=stock_data, label="SMA 50", color="blue", ax=ax)
sb.lineplot(x="Date", y="SMA_100", data=stock_data, label="SMA 100", color="orange", ax=ax)

plt.xticks(rotation=45)
plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()
plt.grid(True, linestyle="--", alpha=0.5)

st.pyplot(fig)

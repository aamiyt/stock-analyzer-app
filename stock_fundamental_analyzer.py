import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Stock Screener App", layout="wide")
st.title("📈 Stock Screener Lite - Analyze, Compare, Filter Stocks")

# Input for Stock Symbols
symbols_input = st.text_input("Enter Stock Symbols (comma-separated, e.g., TCS, INFY, RELIANCE):", value="TCS, INFY")
symbols = [s.strip().upper() for s in symbols_input.split(',') if s.strip()]

# Input for Screener Query (optional)
st.sidebar.header("🔍 Screener Filters")
min_roe = st.sidebar.number_input("Minimum ROE (%)", value=15)
max_debt_equity = st.sidebar.number_input("Maximum Debt/Equity", value=1.0)
min_market_cap = st.sidebar.number_input("Minimum Market Cap (Cr)", value=1000)

# List of Indian Stocks (Example: Add real NSE/BSE symbols)
indian_stocks = [
    "TCS", "INFY", "RELIANCE", "HDFCBANK", "ICICIBANK", "HINDUNILVR", "BHARTIARTL", "KOTAKBANK", 
    "ITC", "LT", "M&M", "BAJFINANCE", "SUNPHARMA", "ULTRACEMCO", "NTPC", "HDFC", "ASIANPAINT", "TECHM"
    # Add more symbols as needed
]

def fetch_stock(symbol):
    stock = yf.Ticker(symbol)
    info = stock.info
    return info

def show_stock_info(info, symbol):
    st.subheader(f"{info.get('longName', 'N/A')} ({symbol})")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Current Price", f"${info.get('currentPrice', 0)}")
        st.metric("Market Cap", f"${info.get('marketCap', 0):,}")
        st.metric("PE Ratio", info.get('trailingPE', 'N/A'))

    with col2:
        st.metric("ROE (%)", f"{info.get('returnOnEquity', 0) * 100:.2f}")
        st.metric("ROA (%)", f"{info.get('returnOnAssets', 0) * 100:.2f}")
        st.metric("Debt/Equity", f"{info.get('debtToEquity', 'N/A')}")

    with col3:
        st.metric("Revenue", f"${info.get('totalRevenue', 0):,}")
        st.metric("Net Income", f"${info.get('netIncomeToCommon', 0):,}")
        st.metric("Dividend Yield", f"{info.get('dividendYield', 0) * 100:.2f}%")

    st.markdown("**Business Summary**")
    st.info(info.get('longBusinessSummary', 'Not Available'))

    st.markdown("---")

# Show Selected Stocks
filtered_stocks = []

for symbol in symbols:
    if symbol not in indian_stocks:
        st.error(f"{symbol} is not an Indian stock. Please enter a valid Indian stock symbol.")
        continue
    
    try:
        info = fetch_stock(symbol)

        # Apply Filters
        roe = info.get('returnOnEquity', 0) * 100
        debt_equity = info.get('debtToEquity', 0)
        market_cap = info.get('marketCap', 0) / 1e7  # Approx Cr

        if roe >= min_roe and debt_equity <= max_debt_equity and market_cap >= min_market_cap:
            filtered_stocks.append((symbol, info))
    except Exception as e:
        st.error(f"Error fetching {symbol}: {e}")

# Display Filtered Stocks
if filtered_stocks:
    for symbol, info in filtered_stocks:
        show_stock_info(info, symbol)
else:
    st.warning("No stocks matched your screener filters!")

# Download Button
if filtered_stocks:
    st.markdown("## 📄 Download Filtered Stocks")
    data = []
    for symbol, info in filtered_stocks:
        data.append({
            "Symbol": symbol,
            "Name": info.get('longName', 'N/A'),
            "Price": info.get('currentPrice', 'N/A'),
            "Market Cap (Cr)": info.get('marketCap', 0) / 1e7,
            "PE Ratio": info.get('trailingPE', 'N/A'),
            "ROE (%)": info.get('returnOnEquity', 0) * 100,
            "Debt/Equity": info.get('debtToEquity', 'N/A'),
            "Revenue": info.get('totalRevenue', 0),
            "Net Income": info.get('netIncomeToCommon', 0),
        })
    df = pd.DataFrame(data)
    st.dataframe(df)

    csv = df.to_csv(index=False)
    st.download_button("Download CSV", data=csv, file_name="filtered_stocks.csv", mime="text/csv")


import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Stock Fundamental Analyzer", layout="wide")
st.title("📈 Stock Fundamental Analyzer with Comparison & Charts")

# Input stock symbols
col1, col2 = st.columns(2)
with col1:
    symbol1 = st.text_input("Enter First Stock Symbol (e.g., AAPL):", value="AAPL").upper()
with col2:
    symbol2 = st.text_input("Enter Second Stock Symbol (optional):", value="TSLA").upper()

def fetch_data(symbol):
    stock = yf.Ticker(symbol)
    info = stock.info
    history = stock.history(period="1y")
    return info, history

def show_fundamentals(info, symbol):
    st.subheader(f"{info.get('longName', 'N/A')} ({symbol})")
    st.markdown(f"*Sector:* {info.get('sector', 'N/A')}  \n"
                f"*Industry:* {info.get('industry', 'N/A')}  \n"
                f"*Market Cap:* ${info.get('marketCap', 0):,}")

    st.markdown("#### Key Financial Metrics")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Current Price", f"${info.get('currentPrice', 0)}")
        st.metric("52-Week High", f"${info.get('fiftyTwoWeekHigh', 0)}")
        st.metric("52-Week Low", f"${info.get('fiftyTwoWeekLow', 0)}")
    with col2:
        st.metric("EPS", info.get('trailingEps', 'N/A'))
        st.metric("PE Ratio", info.get('trailingPE', 'N/A'))
        st.metric("Dividend Yield", str(info.get('dividendYield', 'N/A')))

    st.markdown("#### Financials")
    st.write(f"*Total Revenue:* ${info.get('totalRevenue', 0):,}")
    st.write(f"*Gross Profit:* ${info.get('grossProfits', 0):,}")
    st.write(f"*Net Income:* ${info.get('netIncomeToCommon', 0):,}")

    st.markdown("#### Description")
    st.info(info.get('longBusinessSummary', 'Not Available'))

def plot_price(history, symbol):
    st.markdown("#### 1-Year Price Trend")
    plt.figure(figsize=(10, 4))
    plt.plot(history.index, history['Close'], label=f'{symbol} Close Price')
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.title(f"{symbol} Price Trend (1 Year)")
    plt.legend()
    st.pyplot(plt.gcf())
    plt.clf()

def plot_financials(info, symbol):
    st.markdown("#### Revenue vs Net Income (bar chart)")
    labels = ['Revenue', 'Net Income']
    values = [info.get('totalRevenue', 0), info.get('netIncomeToCommon', 0)]
    fig, ax = plt.subplots()
    ax.bar(labels, values, color=['#4c9aff', '#36d399'])
    ax.set_ylabel('USD')
    ax.set_title(f"{symbol} Revenue vs Net Income")
    st.pyplot(fig)

def download_info(info, symbol):
    data = {
        "Symbol": symbol,
        "Name": info.get('longName', 'N/A'),
        "Price": info.get('currentPrice', 'N/A'),
        "PE Ratio": info.get('trailingPE', 'N/A'),
        "EPS": info.get('trailingEps', 'N/A'),
        "Revenue": info.get('totalRevenue', 'N/A'),
        "Net Income": info.get('netIncomeToCommon', 'N/A'),
    }
    df = pd.DataFrame([data])
    csv = df.to_csv(index=False)
    st.download_button(label="📄 Download Summary CSV", data=csv, file_name=f"{symbol}_fundamentals.csv", mime='text/csv')

# Show first stock
if symbol1:
    try:
        info1, history1 = fetch_data(symbol1)
        st.header(f"🔍 Analysis: {symbol1}")
        show_fundamentals(info1, symbol1)
        plot_price(history1, symbol1)
        plot_financials(info1, symbol1)
        download_info(info1, symbol1)
    except Exception as e:
        st.error(f"Error fetching data for {symbol1}: {e}")

# Show second stock if entered
if symbol2 and symbol2 != symbol1:
    st.markdown("---")
    try:
        info2, history2 = fetch_data(symbol2)
        st.header(f"🔍 Analysis: {symbol2}")
        show_fundamentals(info2, symbol2)
        plot_price(history2, symbol2)
        plot_financials(info2, symbol2)
        download_info(info2, symbol2)
    except Exception as e:
        st.error(f"Error fetching data for {symbol2}: {e}")

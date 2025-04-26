import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Stock Fundamental Analyzer", layout="wide")
st.title("📈 Stock Fundamental Analyzer with Multi-Stock Comparison")

# Input stock symbols
symbols_input = st.text_input("Enter Stock Symbols (comma-separated, e.g., AAPL, TSLA, MSFT):", value="AAPL, TSLA")
symbols = [s.strip().upper() for s in symbols_input.split(',') if s.strip()]

def fetch_data(symbol):
    stock = yf.Ticker(symbol)
    info = stock.info
    history = stock.history(period="1y")
    return info, history

def calculate_ratios(info):
    try:
        roe = info.get('netIncomeToCommon', 0) / info.get('totalStockholderEquity', 1)
        roa = info.get('netIncomeToCommon', 0) / info.get('totalAssets', 1)
        debt_equity = info.get('totalDebt', 0) / info.get('totalStockholderEquity', 1)
        return roe, roa, debt_equity
    except:
        return None, None, None

def show_fundamentals(info, symbol):
    st.subheader(f"{info.get('longName', 'N/A')} ({symbol})")
    st.markdown(f"*Sector:* {info.get('sector', 'N/A')}  \n"
                f"*Industry:* {info.get('industry', 'N/A')}  \n"
                f"*Market Cap:* ${info.get('marketCap', 0):,}")

    st.markdown("#### Key Financial Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Current Price", f"${info.get('currentPrice', 0)}")
        st.metric("52-Week High", f"${info.get('fiftyTwoWeekHigh', 0)}")
        st.metric("52-Week Low", f"${info.get('fiftyTwoWeekLow', 0)}")
    with col2:
        st.metric("EPS", info.get('trailingEps', 'N/A'))
        st.metric("PE Ratio", info.get('trailingPE', 'N/A'))
        st.metric("Dividend Yield", str(info.get('dividendYield', 'N/A')))
    with col3:
        roe, roa, debt_equity = calculate_ratios(info)
        st.metric("ROE", f"{roe:.2%}" if roe else "N/A")
        st.metric("ROA", f"{roa:.2%}" if roa else "N/A")
        st.metric("Debt/Equity", f"{debt_equity:.2f}" if debt_equity else "N/A")

    st.markdown("#### Financials")
    st.write(f"*Total Revenue:* ${info.get('totalRevenue', 0):,}")
    st.write(f"*Gross Profit:* ${info.get('grossProfit', 0):,}")
    st.write(f"*Net Income:* ${info.get('netIncomeToCommon', 0):,}")

    st.markdown("#### Analyst Info")
    st.write(f"*Recommendation:* {info.get('recommendationKey', 'N/A').capitalize()}")
    st.write(f"*Target Mean Price:* ${info.get('targetMeanPrice', 'N/A')}")
    st.write(f"*Price Target Range:* ${info.get('targetLowPrice', 'N/A')} - ${info.get('targetHighPrice', 'N/A')}")

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
    roe, roa, debt_equity = calculate_ratios(info)
    data = {
        "Symbol": symbol,
        "Name": info.get('longName', 'N/A'),
        "Price": info.get('currentPrice', 'N/A'),
        "PE Ratio": info.get('trailingPE', 'N/A'),
        "EPS": info.get('trailingEps', 'N/A'),
        "Revenue": info.get('totalRevenue', 'N/A'),
        "Net Income": info.get('netIncomeToCommon', 'N/A'),
        "ROE": roe,
        "ROA": roa,
        "Debt/Equity": debt_equity,
        "Target Price": info.get('targetMeanPrice', 'N/A'),
        "Recommendation": info.get('recommendationKey', 'N/A')
    }
    df = pd.DataFrame([data])
    csv = df.to_csv(index=False)
    st.download_button(label=f"📄 Download {symbol} Summary", data=csv,
                       file_name=f"{symbol}_fundamentals.csv", mime='text/csv')

# Display all stocks
for symbol in symbols:
    st.markdown("---")
    try:
        info, history = fetch_data(symbol)
        st.header(f"🔍 Analysis: {symbol}")
        show_fundamentals(info, symbol)
        plot_price(history, symbol)
        plot_financials(info, symbol)
        download_info(info, symbol)
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {e}")


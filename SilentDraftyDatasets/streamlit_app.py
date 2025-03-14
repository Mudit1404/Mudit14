import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import feedparser
from textblob import TextBlob
import plotly.express as px

# Set up Streamlit page
st.set_page_config(page_title="Stock & News Sentiment Dashboard", layout="wide")
st.title("📈 Real-Time Stock & Sentiment Dashboard")

# User Input for Stock Symbol
stock_symbol = st.text_input("Enter Stock Symbol (e.g., TSLA, AAPL):", "TSLA")


# Function to get live stock data
def get_stock_data(symbol):
    stock = yf.Ticker(symbol)
    hist = stock.history(period="1d", interval="1m")  # 1-day data with 1-minute interval
    return hist


# Function to get the current stock price
def get_current_price(symbol):
    stock = yf.Ticker(symbol)
    data = stock.history(period="1d")  # Fetch today's stock data
    if not data.empty:
        current_price = data["Close"].iloc[-1]  # Last closing price
        previous_close = data["Close"].iloc[-2] if len(data) > 1 else current_price
        price_change = current_price - previous_close
        percentage_change = (price_change / previous_close) * 100 if previous_close != 0 else 0
        return current_price, price_change, percentage_change
    return None, None, None


# Function to fetch Google News headlines
def fetch_news(stock_symbol):
    rss_url = f"https://news.google.com/rss/search?q={stock_symbol}%20stock&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(rss_url)
    
    headlines = [entry.title for entry in feed.entries[:10]]  # Get top 10 headlines
    return headlines if headlines else ["No news found"]


# Function to analyze sentiment
def analyze_sentiment(headlines):
    return [{"headline": h, "sentiment_score": TextBlob(h).sentiment.polarity} for h in headlines]


# 📊 **Main Dashboard Logic**
if st.button("Analyze Market Data"):

    # 📌 **Fetch & Display Current Stock Price**
    st.subheader("💰 Current Stock Price")
    current_price, price_change, percentage_change = get_current_price(stock_symbol)

    if current_price is not None:
        # Create three columns to display the price data neatly
        col1, col2, col3 = st.columns(3)

        # Current Price
        col1.metric(label="📌 Current Price", value=f"${current_price:.2f}")

        # Daily Price Change
        change_color = "green" if price_change >= 0 else "red"
        col2.metric(label="📈 Change", value=f"${price_change:.2f}", delta=f"{percentage_change:.2f}%", delta_color=change_color)

        # Percentage Change
        col3.metric(label="📊 Percentage Change", value=f"{percentage_change:.2f}%", delta_color=change_color)

    else:
        st.warning("⚠ Unable to retrieve stock price data.")

    # 📈 **Stock Price Chart**
    st.subheader("📉 Live Stock Price Chart")
    data = get_stock_data(stock_symbol)
    fig_stock = go.Figure(data=[go.Candlestick(x=data.index,
                                               open=data["Open"],
                                               high=data["High"],
                                               low=data["Low"],
                                               close=data["Close"])])
    st.plotly_chart(fig_stock)

    # Fetch News & Analyze Sentiment
    headlines = fetch_news(stock_symbol)
    sentiment_results = analyze_sentiment(headlines)

    # Convert results into DataFrame
    df_sentiment = pd.DataFrame(sentiment_results)

    # 📊 **Sentiment Bar Chart**
    st.subheader("📊 Sentiment Bar Chart")
    fig_bar = px.bar(df_sentiment, x="sentiment_score", y="headline", orientation='h', 
                     color="sentiment_score", color_continuous_scale="RdYlGn")
    st.plotly_chart(fig_bar, use_container_width=True)

    # 🔥 **Sentiment Heatmap**
    st.subheader("🌡 Sentiment Heatmap")
    fig_heatmap = px.imshow([df_sentiment["sentiment_score"]],
                            labels=dict(x="News Headlines", y="Sentiment", color="Score"),
                            x=df_sentiment["headline"], color_continuous_scale="RdYlGn")
    st.plotly_chart(fig_heatmap, use_container_width=True)

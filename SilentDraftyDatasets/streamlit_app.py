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
    col1, col2 = st.columns(2)

    with col1:
        # Fetch Stock Data
        data = get_stock_data(stock_symbol)

        # 📈 **Stock Price Chart**
        st.subheader("📉 Live Stock Price Chart")
        fig = go.Figure(data=[go.Candlestick(x=data.index,
                                             open=data["Open"],
                                             high=data["High"],
                                             low=data["Low"],
                                             close=data["Close"])])
        st.plotly_chart(fig)

    with col2:
        # Fetch News & Analyze Sentiment
        headlines = fetch_news(stock_symbol)
        sentiment_results = analyze_sentiment(headlines)

        # Convert results into DataFrame
        df_sentiment = pd.DataFrame(sentiment_results)

        # 📊 **Bar Chart for News Sentiment**
        st.subheader("📊 Sentiment Bar Chart")
        fig_bar = px.bar(df_sentiment, x="sentiment_score", y="headline", orientation='h', 
                         color="sentiment_score", color_continuous_scale="RdYlGn")
        st.plotly_chart(fig_bar, use_container_width=True)

        # 🔥 **Heatmap for Sentiment Scores**
        st.subheader("🌡 Sentiment Heatmap")
        fig_heatmap = px.imshow([df_sentiment["sentiment_score"]],
                                labels=dict(x="News Headlines", y="Sentiment", color="Score"),
                                x=df_sentiment["headline"], color_continuous_scale="RdYlGn")
        st.plotly_chart(fig_heatmap, use_container_width=True)

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

    # 📈 **Stock Price Chart (First)**
    st.subheader("📉 Live Stock Price Chart")
    data = get_stock_data(stock_symbol)
    fig_stock = go.Figure(data=[go.Candlestick(x=data.index,
                                               open=data["Open"],
                                               high=data["High"],
                                               low=data["Low"],
                                               close=data["Close"])])
    st.plotly_chart(fig_stock, use_container_width=True)

    # Fetch News & Analyze Sentiment
    headlines = fetch_news(stock_symbol)
    sentiment_results = analyze_sentiment(headlines)

    # Convert results into DataFrame
    df_sentiment = pd.DataFrame(sentiment_results)

    # 📊 **Sentiment Bar Chart (Headlines on Top)**
    st.subheader("📊 Sentiment Bar Chart")
    fig_bar = px.bar(df_sentiment, x="sentiment_score", y=df_sentiment.index.astype(str), 
                     text="headline", orientation='h', color="sentiment_score", 
                     color_continuous_scale="RdYlGn")

    fig_bar.update_traces(textposition="outside")  # Ensures headlines are readable
    fig_bar.update_layout(yaxis=dict(title="News Headlines", showticklabels=False))  
    st.plotly_chart(fig_bar, use_container_width=True)

    # 🔥 **Sentiment Heatmap (No Overlapping)**
    st.subheader("🌡 Sentiment Heatmap")
    heatmap_data = pd.DataFrame([df_sentiment["sentiment_score"]], 
                                columns=df_sentiment["headline"])

    fig_heatmap = px.imshow(heatmap_data, 
                            labels=dict(x="News Headlines", y="Sentiment", color="Score"),
                            color_continuous_scale="RdYlGn")

    st.plotly_chart(fig_heatmap, use_container_width=True)

import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import plotly.graph_objects as go
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Initialize FastAPI app
app = FastAPI()

# Enable CORS for frontend communication (Important for Next.js)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Function to fetch live stock data
def get_stock_data(symbol):
    stock = yf.Ticker(symbol)
    hist = stock.history(period="1d", interval="1m")  # 1-minute interval
    return hist


# Function to fetch news sentiment
def get_news_sentiment(ticker):
    url = f"https://newsapi.org/v2/everything?q={ticker}&apiKey=YOUR_NEWSAPI_KEY"
    response = requests.get(url).json()

    analyzer = SentimentIntensityAnalyzer()
    sentiments = []

    if "articles" in response:
        for article in response["articles"][:10]:  # Top 10 articles
            text = article["title"] + " " + article["description"]
            score = analyzer.polarity_scores(text)["compound"]
            sentiments.append({"title": article["title"], "sentiment": score})

    return sentiments


# 🎯 FastAPI Routes
@app.get("/stock/{symbol}")
def stock_api(symbol: str):
    data = get_stock_data(symbol)
    return data.to_dict()


@app.get("/news/{symbol}")
def news_api(symbol: str):
    return get_news_sentiment(symbol)


# 🎯 Streamlit UI (For Local Testing)
st.title("📈 Real-Time Stock Dashboard")
ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, TSLA, BTC-USD):")

if ticker:
    data = get_stock_data(ticker)

    # 📊 Stock Price Chart
    st.subheader("Stock Price Chart")
    fig = go.Figure(data=[
        go.Candlestick(x=data.index,
                       open=data["Open"],
                       high=data["High"],
                       low=data["Low"],
                       close=data["Close"])
    ])
    st.plotly_chart(fig)

    # 🔥 News Sentiment Analysis
    sentiments = get_news_sentiment(ticker)
    sentiment_df = pd.DataFrame(sentiments)
    st.subheader("📊 Sentiment Analysis")
    st.bar_chart(sentiment_df.set_index("title")["sentiment"])

# Run FastAPI server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

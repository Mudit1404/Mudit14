import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import plotly.graph_objects as go
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

st.title("📈 Real-Time Stock Dashboard")
ticker = st.text_input("Enter Stock Ticker (e.g., AAPL, TSLA, BTC-USD):")


def get_stock_data(symbol):
    stock = yf.Ticker(symbol)
    hist = stock.history(period="1d", interval="1m")
    return hist


def get_news_sentiment(ticker):
    url = f"https://newsapi.org/v2/everything?q={ticker}&apiKey=YOUR_NEWSAPI_KEY"
    response = requests.get(url).json()
    analyzer = SentimentIntensityAnalyzer()
    sentiments = []

    for article in response["articles"][:10]:
        text = article["title"] + " " + article["description"]
        score = analyzer.polarity_scores(text)["compound"]
        sentiments.append({"title": article["title"], "sentiment": score})

    return sentiments


if ticker:
    data = get_stock_data(ticker)

    st.subheader("Stock Price Chart")
    fig = go.Figure(data=[
        go.Candlestick(x=data.index,
                       open=data["Open"],
                       high=data["High"],
                       low=data["Low"],
                       close=data["Close"])
    ])
    st.plotly_chart(fig)

    sentiments = get_news_sentiment(ticker)
    sentiment_df = pd.DataFrame(sentiments)
    st.subheader("📊 Sentiment Analysis")
    st.bar_chart(sentiment_df.set_index("title")["sentiment"])

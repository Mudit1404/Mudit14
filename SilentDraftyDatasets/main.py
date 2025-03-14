
from typing import Dict, List
from fastapi import FastAPI
import random  # For demo data

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/stock/{symbol}")
def get_stock_price(symbol: str) -> Dict:
    # Demo data - replace with real API calls
    return {"price": round(random.uniform(100, 1000), 2)}

@app.get("/crypto/{symbol}")
def get_crypto_price(symbol: str) -> Dict:
    # Demo data - replace with real API calls
    return {"price": round(random.uniform(20000, 40000), 2)}

@app.get("/news_sentiment/{symbol}")
def get_news_sentiment(symbol: str) -> Dict:
    # Demo data - replace with real API calls
    headlines = [
        f"Company {symbol} announces new product",
        f"{symbol} reports strong quarterly earnings",
        f"Analysts upgrade {symbol} stock rating"
    ]
    sentiments = [
        {"sentiment_score": round(random.uniform(-1, 1), 2)} 
        for _ in headlines
    ]
    return {"headlines": headlines, "sentiments": sentiments}

@app.get("/twitter_sentiment/{symbol}")
def get_twitter_sentiment(symbol: str) -> Dict:
    # Demo data - replace with real API calls
    tweets = [
        f"Excited about {symbol}'s future! 🚀",
        f"Just bought more {symbol} shares! 📈",
        f"Great news from {symbol} today!"
    ]
    sentiments = [
        {"sentiment_score": round(random.uniform(-1, 1), 2)} 
        for _ in tweets
    ]
    return {"tweets": tweets, "sentiments": sentiments}

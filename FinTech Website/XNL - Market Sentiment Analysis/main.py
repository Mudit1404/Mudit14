
from fastapi import FastAPI
import feedparser
import tweepy
from textblob import TextBlob
import os

app = FastAPI()

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the Stock Market Sentiment Analysis API",
        "endpoints": {
            "/news_sentiment/{stock_symbol}": "Get sentiment analysis of news headlines",
            "/twitter_sentiment/{stock_symbol}": "Get sentiment analysis of tweets"
        }
    }

# 🐦 Twitter API Setup
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)

# 📰 Google News Sentiment Analysis
@app.get("/news_sentiment/{stock_symbol}")
def get_news_sentiment(stock_symbol: str):
    # Google News RSS Feed for Financial News
    rss_url = f"https://news.google.com/rss/search?q={stock_symbol}%20stock&hl=en-US&gl=US&ceid=US:en"
    
    # Parse RSS Feed
    feed = feedparser.parse(rss_url)

    if not feed.entries:
        return {"stock": stock_symbol, "headlines": [], "sentiments": [], "message": "No headlines found"}

    # Extract top 5 headlines
    headlines = [entry.title for entry in feed.entries[:5]]

    # Analyze sentiment using TextBlob
    sentiments = [{"headline": h, "sentiment_score": TextBlob(h).sentiment.polarity} for h in headlines]

    return {
        "stock": stock_symbol,
        "headlines": headlines,
        "sentiments": sentiments
    }

# 🐦 Twitter Sentiment Analysis
@app.get("/twitter_sentiment/{stock_symbol}")
def get_twitter_sentiment(stock_symbol: str):
    query = f"{stock_symbol} stock -is:retweet lang:en"
    
    try:
        tweets = client.search_recent_tweets(query=query, max_results=50, tweet_fields=["text"])
        
        if not tweets.data:
            return {"stock": stock_symbol, "tweets": [], "sentiments": [], "message": "No tweets found"}

        # Extract tweet texts
        tweet_texts = [tweet.text for tweet in tweets.data]

        # Analyze sentiment using TextBlob
        sentiments = [{"tweet": t, "sentiment_score": TextBlob(t).sentiment.polarity} for t in tweet_texts]

        return {
            "stock": stock_symbol,
            "tweets": tweet_texts,
            "sentiments": sentiments
        }

    except Exception as e:
        return {"error": str(e)}


import streamlit as st
import requests
import plotly.express as px

# Backend API URL
API_URL = "http://localhost:8000"  # FastAPI runs on port 8000

st.set_page_config(page_title="Market Sentiment Dashboard", layout="wide")

st.title("📊 Market Sentiment Dashboard")

st.markdown("""
### Welcome to the Market Sentiment Dashboard! 📈

This dashboard allows you to:
- 💰 Track real-time stock prices for any symbol
- 🪙 Monitor Bitcoin cryptocurrency prices
- 📰 Analyze news sentiment with interactive visualizations
- 🐦 View Twitter sentiment analysis through dynamic charts

Enter a stock symbol below to get started!
""")

# User selects stock symbol
stock_symbol = st.text_input("Enter Stock Symbol (e.g., TSLA, AAPL):", "TSLA")

if st.button("Get Market Data"):
    try:
        col1, col2 = st.columns(2)

        with col1:
            # Fetch Stock Price
            stock_response = requests.get(f"{API_URL}/stock/{stock_symbol}")
            stock_data = stock_response.json()
            
            # Fetch Crypto Price
            crypto_response = requests.get(f"{API_URL}/crypto/bitcoin")
            crypto_data = crypto_response.json()

            st.subheader("💰 Market Prices")
            st.metric(label=f"Stock Price ({stock_symbol})", value=f"${stock_data.get('price', 'N/A')}")
            st.metric(label="Bitcoin Price", value=f"${crypto_data.get('price', 'N/A')}")

        with col2:
            # Fetch News Sentiment
            news_response = requests.get(f"{API_URL}/news_sentiment/{stock_symbol}")
            news_data = news_response.json()

            # Fetch Twitter Sentiment
            twitter_response = requests.get(f"{API_URL}/twitter_sentiment/{stock_symbol}")
            twitter_data = twitter_response.json()

            # News Sentiment Visualization
            st.subheader("📰 News Sentiment")
            if "headlines" in news_data and news_data["headlines"]:
                news_sentiments = [
                    {"headline": h, "score": news_data["sentiments"][i]["sentiment_score"]}
                    for i, h in enumerate(news_data["headlines"])
                ]
                
                # Create DataFrame for news visualization
                import pandas as pd
                df_news = pd.DataFrame(news_sentiments)
                
                fig_news = px.bar(df_news, x="headline", y="score", color="score",
                                labels={"score": "Sentiment Score", "headline": "News Headlines"},
                                color_continuous_scale=["red", "yellow", "green"])
                fig_news.update_layout(showlegend=False)
                st.plotly_chart(fig_news, use_container_width=True)
            else:
                st.write("No news found.")

            # Twitter Sentiment Visualization
            st.subheader("🐦 Twitter Sentiment")
            if "tweets" in twitter_data and twitter_data["tweets"]:
                twitter_sentiments = [
                    {"tweet": t, "score": twitter_data["sentiments"][i]["sentiment_score"]}
                    for i, t in enumerate(twitter_data["tweets"])
                ]
                
                # Create DataFrame for twitter visualization
                import pandas as pd
                df_twitter = pd.DataFrame(twitter_sentiments)
                
                fig_twitter = px.bar(df_twitter, x="tweet", y="score", color="score",
                                    labels={"score": "Sentiment Score", "tweet": "Tweets"},
                                    color_continuous_scale=["red", "yellow", "green"])
                fig_twitter.update_layout(showlegend=False)
                st.plotly_chart(fig_twitter, use_container_width=True)
            else:
                st.write("No tweets found.")
                
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")

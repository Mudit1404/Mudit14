from fastapi import FastAPI
import requests

app = FastAPI()

DEFAULT_STOCKS = ["AAPL", "GOOGL", "MSFT", "AMZN", "META", "TSLA", "NVDA", "JPM", "V", "WMT", "DIS", "NFLX", "PYPL", "INTC", "AMD"]
DEFAULT_CRYPTOS = ["bitcoin", "ethereum", "dogecoin", "solana", "cardano", "polkadot", "ripple", "binancecoin", "avalanche-2", "chainlink", "polygon", "uniswap", "litecoin", "stellar", "monero"]

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Live Market Data - FinTech API",
        "available_endpoints": {
            "/stocks": "Get list of default stocks",
            "/cryptos": "Get list of default cryptocurrencies",
            "/stock/{symbol}": "Get price for any stock symbol (e.g., /stock/AAPL)",
            "/crypto/{coin}": "Get price for any cryptocurrency (e.g., /crypto/bitcoin)"
        }
    }

@app.get("/stocks")
def get_default_stocks():
    return {"default_stocks": DEFAULT_STOCKS}

@app.get("/cryptos")
def get_default_cryptos():
    return {"default_cryptos": DEFAULT_CRYPTOS}

@app.get("/stock/{symbol}")
def get_stock_price(symbol: str):
    API_KEY = "E51WWVGBCDS1VHDP"
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()

    try:
        price = data["Global Quote"]["05. price"]
        return {"symbol": symbol, "price": float(price)}
    except:
        return {"error": "Stock not found or API limit exceeded"}

@app.get("/crypto/{coin}")
def get_crypto_price(coin: str):
    coin = coin.lower()
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd"
    response = requests.get(url)
    
    if response.status_code != 200:
        return {"error": "API request failed"}

    data = response.json()
    
    if coin in data:
        return {"coin": coin, "price": data[coin]["usd"]}
    else:
        return {"error": f"Crypto '{coin}' not found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

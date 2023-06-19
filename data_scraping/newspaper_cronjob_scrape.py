import pandas as pd
from datetime import datetime, timedelta
from pymongo import MongoClient
from transformers import pipeline
from pygooglenews import GoogleNews

mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client.news
sentiment_model = pipeline(model="midwinter73/dipterv-finbert")

for stock_ticker in ['AAPL', 'BTC', 'GME', 'TSLA']:
    if stock_ticker == "AAPL":
        news_collection = db.AAPL
        query = f"{stock_ticker} OR Apple"
    elif stock_ticker == "BTC":
        news_collection = db.BTC
        query = f"{stock_ticker} OR Bitcoin"
    elif stock_ticker == "GME":
        news_collection = db.GME
        query = f"{stock_ticker} OR GameStop"
    elif stock_ticker == "TSLA":
        news_collection = db.TSLA
        query = f"{stock_ticker} OR Tesla"

    gn = GoogleNews(lang='en', country='US')
    entries = gn.search(query=query, helper=True, when='1h', proxies=None, scraping_bee=None)

    for entry in entries["entries"]:
        server_data = {}
        server_data['_id'] = entry["id"]
        server_data['title'] = entry["title"].split("-")[0]
        server_data['date'] = pd.to_datetime(entry["published"])
        server_data["sentiment"] = sentiment_model(entry['title'])
        try:
            news_collection.insert_one(server_data)
        except Exception as e:
            print("An exception occurred ::", e)
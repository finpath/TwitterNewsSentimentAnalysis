import pandas as pd
from datetime import datetime, timedelta
from pymongo import MongoClient
from transformers import pipeline
from pygooglenews import GoogleNews

mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client.news
news_collection = db.GME

sentiment_model = pipeline(model="midwinter73/dipterv-finbert")

startDate = datetime(2022, 1, 1)
startDayDate = datetime(2022, 1, 2)
endDate = datetime(2023, 6, 5)
add1Day = timedelta(days=1)

while startDate <= endDate:
    dt_startDate = startDate.strftime("%Y/%m/%d")
    dt_startDayDate = startDayDate.strftime("%Y/%m/%d")

    gn = GoogleNews(lang='en', country='US')
    entries = gn.search(query="GME OR GameStop", helper=True, when=None, from_=dt_startDate, to_=dt_startDayDate,
                        proxies=None, scraping_bee=None)

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

    startDate += add1Day
    startDayDate += add1Day
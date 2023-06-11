import requests
from transformers import pipeline

sentiment_model = pipeline(model="midwinter73/dipterv-finbert")

access_token = ""
access_token_secret = ""
bearer_token = ''

from pymongo import MongoClient

cluster = "mongodb://localhost:27017/"
mongo_client = MongoClient(cluster)

db = mongo_client.tweets
tweets_collection = db.TSLA

import tweepy

client = tweepy.Client(bearer_token=bearer_token,
                       access_token=access_token,
                       access_token_secret=access_token_secret,
                       return_type=requests.Response,
                       wait_on_rate_limit=True)

# Replace with your own search query
query = 'TSLA -is:retweet lang:en -has:links'

from datetime import datetime, timedelta

startDate = datetime(2022, 1, 1)
endDate = datetime(2023, 6, 5)
add2Hours = timedelta(hours=2)
add1Hour = timedelta(hours=1)

while startDate <= endDate:
    print(startDate)
    hours1ahead = startDate + add1Hour

    tweets = client.search_all_tweets(query=query,
                                      start_time=f"{startDate.year}-{startDate.month}-{startDate.day}T{startDate.hour}:00:00Z",
                                      end_time=f"{hours1ahead.year}-{hours1ahead.month}-{hours1ahead.day}T{hours1ahead.hour}:59:59Z",
                                      tweet_fields=['author_id', 'created_at', 'lang', 'public_metrics'],
                                      user_fields=['public_metrics', 'verified'], expansions='author_id',
                                      max_results=500)
    tweets_dict = tweets.json()
    for user in range(len(tweets_dict["includes"]["users"])):
        tweets_dict["includes"]["users"][user]["user_public_metrics"] = tweets_dict["includes"]["users"][user].pop(
            "public_metrics")
    if (tweets_dict["meta"]["result_count"] > 0):
        for tweet_index in range(len(tweets_dict["data"])):
            user_index = [x['id'] for x in tweets_dict["includes"]["users"]].index(tweets_dict["data"][tweet_index][
                                                                                       "author_id"])  # if same user tweeted twice user is only returned once: fix
            # tweets_dict["includes"]["users"][tweet_index].pop('id') #remove id to avoid conflict in when merging
            merged = {**tweets_dict["includes"]["users"][user_index], **tweets_dict["data"][tweet_index]}  # merging
            merged["_id"] = merged.pop("id")
            merged["sentiment"] = sentiment_model(merged['text'])
            try:
                tweets_collection.insert_one(merged)
            except Exception as e:
                print("An exception occurred ::", e)
    startDate += add2Hours
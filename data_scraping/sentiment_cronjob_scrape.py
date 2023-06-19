from datetime import datetime, timedelta
from pymongo import MongoClient
import tweepy
import requests
from transformers import pipeline

mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client.tweets

access_token = ""
access_token_secret = ""
bearer_token=''

client = tweepy.Client(bearer_token=bearer_token,
                        access_token=access_token,
                        access_token_secret=access_token_secret,
                        return_type = requests.Response,
                        wait_on_rate_limit=True)


sentiment_model = pipeline(model="midwinter73/dipterv-finbert")

for stock_ticker in ['AAPL', 'BTC', 'GME', 'TSLA']:
    query = f"{stock_ticker} -is:retweet lang:en -has:links"

    if stock_ticker == "AAPL":
        tweets_collection = db.AAPL
    elif stock_ticker == "BTC":
        tweets_collection = db.BTC
    elif stock_ticker == "GME":
        tweets_collection = db.GME
    elif stock_ticker == "TSLA":
        tweets_collection = db.TSLA

    now = datetime.utcnow()
    ten_seconds_earlier = now - timedelta(seconds=20)
    five_minutes_earlier = ten_seconds_earlier - timedelta(minutes=15)
    dt_string_ten_seconds_earlier = ten_seconds_earlier.strftime(
        "%Y-%m-%dT%H:%M:%SZ")  # 'start_time' must be a minimum of 10 seconds prior to the request time.
    dt_string_five_minutes_earlier = five_minutes_earlier.strftime(
        "%Y-%m-%dT%H:%M:%SZ")  # 'end_time' must be a minimum of 10 seconds prior to the request time.

    tweets = client.search_all_tweets(query=query, start_time=f"{dt_string_five_minutes_earlier}",
                                      end_time=f"{dt_string_ten_seconds_earlier}",
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

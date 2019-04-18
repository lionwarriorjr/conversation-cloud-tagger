import sys
import numpy as np
import scipy
import pandas as pd
import tweepy
import json
from googleapiclient import discovery

API_KEY='AIzaSyC7Q5tMmRksOdpe7zk8yBTpOOyMRSboYec'
access_token = "771910501727100932-RsADid5iaB9kH8OpDjz0JLIV7hpE3HK"
access_token_secret =  "tpJxinCvIzgCpNu1hd0c900Ko6N0itJiAdU5w3cHRcIKQ"
consumer_key =  "KVNV68TEpLeZLqLDvm3RqBvw9"
consumer_secret =  "6MTWXxKVSE5SqaD3MszzIce3MqTZEmHHvAgwtGRhSHYOwB4OFq"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)
topic, limit = sys.argv[1], int(sys.argv[2])
tweets = api.search(q=topic, lang="en", count=limit, tweet_mode="extended", since="2019-03-01", until="2019-04-18")
times = [tweet.created_at for tweet in tweets]
tweets = [tweet.full_text for tweet in tweets]

# Generates API client object dynamically based on service name and version.
service = discovery.build('commentanalyzer', 'v1alpha1', developerKey=API_KEY)

scores = []
for tweet in tweets:
  analyze_request = {
    'comment': { 'text': tweet },
    'requestedAttributes': {'TOXICITY': {}}
  }
  response = service.comments().analyze(body=analyze_request).execute()
  if 'en' in response['languages']:
    score = response['attributeScores']['TOXICITY']['summaryScore']['value']
    scores.append(score)
  else:
    scores.append(-1)

result = pd.DataFrame({'timestamp': times, 'text': tweets, 'toxicity': scores})
result.timestamp = pd.to_datetime(result.timestamp)
result.toxicity = pd.to_numeric(result.toxicity)
result = result[result.score != -1]
print(result.head())
result.to_csv('tweets_' + topic + '.csv', index=False)
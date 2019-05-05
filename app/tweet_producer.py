import string
import tweepy
import time
from kafka import KafkaConsumer, KafkaProducer
from datetime import datetime, timedelta
import json

FETCH_PERIOD = 2

# twitter credentials
consumer_key = 'IP6FvhnwcF4N8Cd3cTLW8dig7'
consumer_secret = '6Tov5W7fsSIDKcgrFR2FlGKDHzErL27DWkkjdPvQg07fYhSHRo'
access_token = '2608424010-KFYdiYn8VJ5cprSXZfVWRJ9kV5vXSjnYhWHretM'
access_token_secret = 'qkoveocNv5fg4Qe7BHz3pTaTgWjvEMShjtKlsqm7Gls1t'
  
###  KAFKA parameters
SERVER_URL = "kafka-29b24362-svindiana-22b8.aivencloud.com:29413"
TOPIC_NAME = "tweets"
CLIENT_ID = "mltox-kube-client"
GROUP_ID = "mltox-kube-group"
CA_FILENAME = "credentials/ca.pem"
CERT_FILENAME = "credentials/service.cert"
SSL_FILENAME = "credentials/service.key"

# Creating the authentication object
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
# Setting your access token and secret
auth.set_access_token(access_token, access_token_secret)
# Creating the API object by passing in auth information
api = tweepy.API(auth) 

topic_name = 'politics'
producer = KafkaProducer(value_serializer=lambda v:json.dumps(v).encode('utf-8'),
                         bootstrap_servers=SERVER_URL,
                         linger_ms=10,
                         security_protocol="SSL",
                         ssl_cafile=CA_FILENAME,
                         ssl_certfile=CERT_FILENAME,
                         ssl_keyfile=SSL_FILENAME
)

def get_twitter_data():
    for tweet in tweepy.Cursor(api.search, q=topic_name, lang="en").items(100):
        text = tweet.text.lower()
        text = text.translate(string.punctuation)
        text = ' '.join(text.split())
        created_at = tweet.created_at
        message = {"timestamp": str(created_at), "text": text}
        producer.send(topic_name, message)

    producer.flush()

def periodic_work(interval):
    while True:
        get_twitter_data()
        time.sleep(interval)

periodic_work(60 * FETCH_PERIOD) # fetch data every 2 minutes

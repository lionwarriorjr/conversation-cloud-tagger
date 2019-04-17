from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from kafka import SimpleProducer, KafkaClient

access_token = "771910501727100932-RsADid5iaB9kH8OpDjz0JLIV7hpE3HK"#"3255311624-UAbx3pb96fumDxVmPw3DlaLFPPtbfn75IWBJd98"
access_token_secret =  "tpJxinCvIzgCpNu1hd0c900Ko6N0itJiAdU5w3cHRcIKQ"#"Q1260yMSSie8MeT1FdaJfs2iBHLsFPIvRRseRfEIorUOQ"
consumer_key =  "KVNV68TEpLeZLqLDvm3RqBvw9"#"mOOCVojaX0Tm0GIm7h4BY4Muk"
consumer_secret =  "6MTWXxKVSE5SqaD3MszzIce3MqTZEmHHvAgwtGRhSHYOwB4OFq"#"NrkXszzgcmI2M5O4F2J9JkJ8JlsfWKWw0T0AVjIYhd4LNBPo3F"


class StdOutListener(StreamListener):
        def on_data(self, data):
                    producer.send_messages("trump", data.encode('utf-8'))
                    print (data)
                    return True
        def on_error(self, status):
                    print (status)

kafka = KafkaClient("localhost:9092")
producer = SimpleProducer(kafka)
l = StdOutListener()
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
stream = Stream(auth, l)
stream.filter(track="trump")

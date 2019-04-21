from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from kafka import SimpleProducer, KafkaClient

from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils

import json

access_token = "771910501727100932-RsADid5iaB9kH8OpDjz0JLIV7hpE3HK"#"3255311624-UAbx3pb96fumDxVmPw3DlaLFPPtbfn75IWBJd98"
access_token_secret =  "tpJxinCvIzgCpNu1hd0c900Ko6N0itJiAdU5w3cHRcIKQ"#"Q1260yMSSie8MeT1FdaJfs2iBHLsFPIvRRseRfEIorUOQ"
consumer_key =  "KVNV68TEpLeZLqLDvm3RqBvw9"#"mOOCVojaX0Tm0GIm7h4BY4Muk"
consumer_secret =  "6MTWXxKVSE5SqaD3MszzIce3MqTZEmHHvAgwtGRhSHYOwB4OFq"#"NrkXszzgcmI2M5O4F2J9JkJ8JlsfWKWw0T0AVjIYhd4LNBPo3F"

keyword = "trump"
class StdOutListener(StreamListener):
        '''
        def on_data(self, data):
                    json_load = json.loads(data)
                    text = json_load['text']
                    producer.send_messages(keyword, text.encode('utf-8'))
                    print (text)
                    return True
        '''
        def on_status(self, status): # TODO: pass in timestamp
            producer.send_messages(keyword,status.text.encode('utf-8'))
            # Prints the text of the tweet
            print('Tweet text: ' + status.text)
                             
            # There are many options in the status object,
            # hashtags can be very easily accessed.
            #            for hashtag in status.entries['hashtags']:
            #    print(hashtag['text'])
                                                                      
            return True
        def on_error(self, status):
                    print (status)
def streamTweets():
    # create kafka producer
    kafka = KafkaClient("localhost:9092") # TODO: CHANGE THIS TO BE NOT LOCAL
    producer = SimpleProducer(kafka)
    # stream to spark
    sc = SparkContext(appName="PythonStreamingDirectKafkaWordCount")
    ssc = StreamingContext(sc, 2)
    brokers = "localhost:9092"
    kvs = KafkaUtils.createDirectStream(ssc, [keyword], {"metadata.broker.list": brokers})
    #lines = kvs.map(lambda x: x[1])
    #counts = lines.flatMap(lambda line: line.split(" ")) \
    #        .map(lambda word: (word, 1)) \
    #            .reduceByKey(lambda a, b: a+b)


    counts.pprint()
    ssc.start()
    ssc.awaitTermination()

    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, l)
    stream.filter(track=[keyword])#,languages=["en"])
    return kvs

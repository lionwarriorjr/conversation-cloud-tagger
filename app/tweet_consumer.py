# This script receives messages from a Kafka topic
from kafka import KafkaConsumer
import pandas as pd
import json
import time
import spark_toxic_tagger as mltox

STREAMED_FILENAME = "app/toxic-data/tweets-timestamped.csv"

consumer = KafkaConsumer(
    "politics",
    bootstrap_servers="kafka-29b24362-svindiana-22b8.aivencloud.com:29413",
    client_id="mltox-predictor-client-forecaster-2",
    group_id="mltox-predictor-group-forecaster-2",
    security_protocol="SSL",
    ssl_cafile="credentials/ca.pem",
    ssl_certfile="credentials/service.cert",
    ssl_keyfile="credentials/service.key",
    auto_offset_reset="latest"
)

while True:
    kafka_msgs = consumer.poll(timeout_ms=1000)
    streamed = []
    for tp, msgs in kafka_msgs.items():
        for msg in msgs: 
            value = json.loads(msg.value.decode('utf-8'))
            streamed.append((value['timestamp'], value['text']))
    streamed = pd.DataFrame(streamed, columns=['timestamp', 'text'])
    if streamed.shape[0] > 0:
        streamed.to_csv(STREAMED_FILENAME, index=False)
        mltox.run()
        time.sleep(120)

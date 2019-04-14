import numpy as np
import pandas as pd
import nltk
import string
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
from nltk.stem.porter import *
from pyspark import SparkContext
from pyspark.ml import Pipeline, PipelineModel
from pyspark.ml.tuning import CrossValidator, CrossValidatorModel, ParamGridBuilder
from pyspark.ml.regression import GBTRegressor
from pyspark.ml.feature import * 
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.sql import SQLContext, SparkSession, Row
from pyspark.sql.types import *
import pyspark.sql.functions as F
from pyod.models.loci import LOCI
import pyflux as pf
from google.cloud import bigquery
from kafka import KafkaConsumer

spark = SparkSession.builder.appName('mltox').getOrCreate()

MODEL_PATH = "app/spark-gradientboosting-toxic-tagger-cv"
FORECAST_WINDOW_PCT = 0.25
FORECAST_MCMC_SIMULATIONS = 10000 # tunable
STREAMED_FILENAME = "app/toxic-data/tweets-timestamped.csv"
BQ_DATASET_NAME = "MLTOX"
BQ_TIME_SERIES_TABLE = "TIME_SERIES"
BQ_FORECAST_TABLE = "FORECAST"
###  KAFKA parameters here

def cleanText(column):
    return F.trim(F.lower(F.regexp_replace(column, '([^\s\w_]|_)+', ''))).alias('text')

# Spark Streaming component is the Kafka consumer
# streams messages from Kafka into a spark dataframe or alternatively a .csv
def consumeKafka():
    pass

def writeToBigQuery(df, dataset_id, table_id):
    client = bigquery.Client()
    table_ref = client.dataset(dataset_id).table(table_id)
    table = client.get_table(table_ref) # API request
    rowsToInsert = list(df.itertuples(index=False, name=None))
    client.insert_rows(table, rowsToInsert) # API request

def tagAnomalies(df):
    values = df.prediction.values.reshape(-1,1)
    anomalyDetector = LOCI()
    anomalyDetector.fit(values)
    anomalyLabels = np.asarray(anomalyDetector.labels_)
    df['isAnomaly'] = anomalyLabels
    return df

def predict():
    test = spark.read.csv(STREAMED_FILENAME, header=True, mode="DROPMALFORMED")
    test = test.select(F.col("timestamp"), cleanText(F.col("text")))
    times = test.select("timestamp")
    test = test.drop("timestamp")
    toxicTagger = PipelineModel.load(MODEL_PATH)
    predictions = toxicTagger.transform(test).select(F.col("prediction"))
    testIndex = predictions.withColumn("id", F.monotonically_increasing_id())
    timesIndex = times.withColumn("id", F.monotonically_increasing_id())
    tagged = timesIndex.join(testIndex, "id", "inner").drop("id")
    tagged = tagged.withColumn("datetime", F.from_unixtime(F.unix_timestamp("timestamp", "yyyy-MM-dd HH:mm:ss")))
    tagged = tagged.select(F.col("datetime"), F.col("prediction"))
    tagged = tagged.withColumn("timestamp", F.date_trunc("hour", F.col("datetime").cast("timestamp")))
    tagged = tagged.select(F.col("timestamp"), F.col("prediction"))
    result = tagged.groupBy("timestamp").mean("prediction").sort(F.col("timestamp").asc())
    result = result.na.drop(subset=["timestamp", "avg(prediction)"])
    result = result.toPandas()
    result['timestamp'] = pd.to_datetime(result.timestamp)
    result.columns = ['timestamp', 'prediction']
    return result

def forecast(df):

    #def runForecastModel(df):
        #forecaster = ToxicityForecaster(df.prediction.values)
        #return forecaster.forecast()

    #_, forecasted = runForecastModel(df)
    #start = [df.timestamp.iloc[-1]] * FORECAST_WINDOW
    #forecastDF = pd.DataFrame({'timestamp': start})
    #forecastDF['timestamp'] = pd.to_datetime(forecastDF.timestamp)
    #offsets = [pd.DateOffset(hours=i) for i in range(1, FORECAST_WINDOW)]
    #for i in range(len(offsets)):
        #forecastDF.loc[i,'timestamp'] += offsets[i]
    #forecastDF['prediction'] = forecasted
    #return forecastDF

    forecast_window = int(df.shape[0] * FORECAST_WINDOW_PCT)
    forecasted = pd.DataFrame(columns=['timestamp','prediction'])
    model = None
    if forecast_window > 0:
        ts = df.set_index('timestamp')
        model = pf.GARCH(p=1, q=1, data=ts)
        model.fit('M-H', nsims=FORECAST_MCMC_SIMULATIONS)
        forecasted = model.predict(forecast_window).reset_index()
    return forecasted, model

def run():
    # consumeKafka()
    history = predict()
    history = tagAnomalies(history)
    forecasted, model = forecast(history)
    print(history.head())
    print(forecasted.head())
    #writeToBigQuery(history, BQ_DATASET_NAME, BQ_TIME_SERIES_TABLE)
    #writeToBigQuery(forecast, BQ_DATASET_NAME, BQ_FORECAST_TABLE)

if __name__ == "__main__":
    run()

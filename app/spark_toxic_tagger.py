#!/usr/bin/env python3

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
import statsmodels.api as sm
from google.cloud import bigquery
#from google.oauth2 import service_account
import tweepy
import csv
import time
import os

spark = SparkSession.builder.appName('mltox').getOrCreate()

MODEL_PATH = "models/spark-gradientboosting-toxic-tagger-cv"
FORECAST_WINDOW_PCT = 0.25
FORECAST_MCMC_SIMULATIONS = 10000 # tunable
STREAMED_FILENAME = "app/toxic-data/tweets-timestamped.csv"

### BigQuery Parameters
GCP_PROJECT_ID = "cloud-computing-237814"
BQ_TIME_SERIES_TABLE = "MLTOX.TIME_SERIES"
BQ_FORECAST_TABLE = "MLTOX.FORECAST"
BQ_MESSAGES_TABLE = "MLTOX.MESSAGES"

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials/gcp-key.json"

def cleanText(column):
    return F.trim(F.lower(F.regexp_replace(column, '([^\s\w_]|_)+', ''))).alias('text')

def writeToBigQuery(df, table_id):
    df.to_gbq(table_id, GCP_PROJECT_ID, chunksize=None, if_exists='append', verbose=False)

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
    messages = test.toPandas()
    times = test.select("timestamp")
    test = test.drop("timestamp")
    toxicTagger = PipelineModel.load(MODEL_PATH)
    predictions = toxicTagger.transform(test).select(F.col("prediction"))
    testIndex = predictions.withColumn("id", F.monotonically_increasing_id())
    timesIndex = times.withColumn("id", F.monotonically_increasing_id())
    tagged = timesIndex.join(testIndex, "id", "inner").drop("id")
    tagged = tagged.withColumn("datetime", F.from_unixtime(F.unix_timestamp("timestamp", "yyyy-MM-dd HH:mm:ss")))
    tagged = tagged.select(F.col("datetime"), F.col("prediction"))
    tagged = tagged.withColumn("timestamp", F.date_trunc("minute", F.col("datetime").cast("timestamp")))
    tagged = tagged.select(F.col("timestamp"), F.col("prediction"))
    result = tagged.groupBy("timestamp").mean("prediction").sort(F.col("timestamp").asc())
    result = result.na.drop(subset=["timestamp", "avg(prediction)"])
    result = result.toPandas()
    result['timestamp'] = pd.to_datetime(result.timestamp)
    result.columns = ['timestamp', 'prediction']
    messages['timestamp'] = pd.to_datetime(messages.timestamp)
    return result, messages

def forecast(df):
    forecast_window = int(df.shape[0] * FORECAST_WINDOW_PCT)
    forecasted = pd.DataFrame(columns=['timestamp', 'prediction'])
    model = None
    if forecast_window > 0:
        history = df.prediction.values
        ssm = sm.tsa.SARIMAX(history, order=(1,1,1), seasonal_order=(0,1,1,4))
        model = ssm.fit()
        predictions = model.forecast(forecast_window)
        start = [df.timestamp.iloc[-1]] * forecast_window
        forecasted = pd.DataFrame({'timestamp': start, 'prediction': predictions})
        forecasted['timestamp'] = pd.to_datetime(forecasted.timestamp)
        offsets = [pd.DateOffset(hours=i) for i in range(1, forecast_window)]
        for i in range(len(offsets)):
            forecasted.loc[i,'timestamp'] += offsets[i]
    return forecasted, model

def run():
    history, messages = predict()
    history = tagAnomalies(history)
    #forecasted, model = forecast(history)
    print(history.head())
    print(messages.head())
    #print(forecasted.head())
    history.columns = ['times','prediction','isAnomaly']
    messages.columns = ['times', 'message']
    writeToBigQuery(history, BQ_TIME_SERIES_TABLE)
    writeToBigQuery(messages, BQ_MESSAGES_TABLE)
    #writeToBigQuery(forecast, BQ_FORECAST_TABLE)

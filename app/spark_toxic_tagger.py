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
import tweepy
import csv
import time
import os

spark = SparkSession.builder.appName('mltox').getOrCreate()

MODEL_PATH = "models/spark-gradientboosting-toxic-tagger-cv"
FORECAST_WINDOW_PCT = 0.25
FORECAST_MCMC_SIMULATIONS = 10000 # tunable
SSM_LAG = 1
STREAMED_FILENAME = "app/toxic-data/tweets-timestamped.csv"

### BigQuery Parameters
GCP_PROJECT_ID = "cloud-computing-237814"
BQ_TIME_SERIES_TABLE = "MLTOX.TIME_SERIES_V2"
BQ_FORECAST_TABLE = "MLTOX.FORECAST_V2"
BQ_MESSAGES_TABLE = "MLTOX.MESSAGES_V2"

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
    minutes = tagged.withColumn("timestamp", F.date_trunc("minute", F.col("datetime").cast("timestamp")))
    hours = tagged.withColumn("timestamp", F.date_trunc("hour", F.col("datetime").cast("timestamp")))
    minutes = minutes.select(F.col("timestamp"), F.col("prediction"))
    hours = hours.select(F.col("timestamp"), F.col("prediction"))
    resultMinutes = minutes.groupBy("timestamp").mean("prediction").sort(F.col("timestamp").asc())
    resultHours = hours.groupBy("timestamp").mean("prediction").sort(F.col("timestamp").asc())
    resultMinutes = resultMinutes.na.drop(subset=["timestamp", "avg(prediction)"])
    resultHours = resultHours.na.drop(subset=["timestamp", "avg(prediction)"])
    resultMinutes, resultHours = resultMinutes.toPandas(), resultHours.toPandas()
    resultMinutes['timestamp'] = pd.to_datetime(resultMinutes.timestamp)
    resultHours['timestamp'] = pd.to_datetime(resultHours.timestamp)
    resultMinutes.columns = ['timestamp', 'prediction']
    resultHours.columns = ['timestamp', 'prediction']
    messages['timestamp'] = pd.to_datetime(messages.timestamp)
    return resultMinutes, resultHours, messages

def forecast(df):
    forecast_window = int(df.shape[0] * FORECAST_WINDOW_PCT)
    forecasted = pd.DataFrame(columns=['timestamp', 'prediction'])
    model = None
    if forecast_window > SSM_LAG:
        history = df.prediction.values
        ssm = sm.tsa.SARIMAX(history, order=(1,0,0), seasonal_order=(1,1,0,12))
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
    history, forecasted, messages = predict()
    history = tagAnomalies(history)
    forecasted, model = forecast(forecasted)
    history.columns = ['times','prediction','isAnomaly']
    messages.columns = ['times', 'message']
    forecasted.columns = ['times','prediction']
    print(history.head())
    print(messages.head())
    print(forecasted.head())
    writeToBigQuery(history, BQ_TIME_SERIES_TABLE)
    writeToBigQuery(messages, BQ_MESSAGES_TABLE)
    if forecasted.shape[0] > 0:
        writeToBigQuery(forecasted, BQ_FORECAST_TABLE)
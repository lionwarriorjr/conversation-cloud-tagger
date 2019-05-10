#!/usr/bin/env python3

import numpy as np
import pandas as pd
#import nltk
import string
import itertools
#from nltk.stem.porter import PorterStemmer
#from nltk.corpus import stopwords
#from nltk.stem.porter import *
from pyspark import SparkContext
from pyspark.ml import Pipeline, PipelineModel
from pyspark.ml.tuning import CrossValidator, CrossValidatorModel, ParamGridBuilder
from pyspark.ml.regression import GBTRegressor
from pyspark.ml.feature import * 
from pyspark.ml.evaluation import RegressionEvaluator
from pyspark.sql import SQLContext, SparkSession, Row
from pyspark.sql.types import *
import pyspark.sql.functions as F
#from pyod.models.loci import LOCI
import statsmodels.api as sm
from statsmodels.tsa.ar_model import AR
#from google.cloud import bigquery
#from google.oauth2 import service_account
import tweepy
import csv
import matplotlib.pyplot as plt
import time
import os

#spark = SparkSession.builder.appName('mltox').getOrCreate()

MODEL_PATH = "../models/spark-gradientboosting-toxic-tagger-cv"
FORECAST_WINDOW_PCT = 0.25
FORECAST_MCMC_SIMULATIONS = 10000 # tunable
STREAMED_FILENAME = "../app/toxic-data/tweets-timestamped.csv"

### BigQuery Parameters
GCP_PROJECT_ID = "cloud-computing-237814"
BQ_TIME_SERIES_TABLE = "MLTOX.TIME_SERIES"
BQ_FORECAST_TABLE = "MLTOX.FORECAST"
BQ_MESSAGES_TABLE = "MLTOX.MESSAGES"

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "credentials/gcp-key.json"

def runOnActualData(filename):
    data = pd.read_csv(filename)
    timestamp= np.arange(data.shape[0])
    nums = data['prediction'].values
    doForecasting(nums,timestamp)


def doForecasting(nums,timestamp):
    forecast_window = int(len(nums) * FORECAST_WINDOW_PCT)
    forecasted = pd.DataFrame(columns=['timestamp', 'prediction'])
    model = None
    if forecast_window > 0:
        history = nums#nums[0:int(len(nums) * (1-FORECAST_WINDOW_PCT))]#data.prediction.values 
        ssm = sm.tsa.SARIMAX(history,order=(1,0,0), seasonal_order=(1,1,0,12), enforce_stationarity=False)
        model = ssm.fit()
        predictions = model.forecast(forecast_window) #model.predict(data.shape[0],data.shape[0]-1+forecast_window)
    plt.clf()
    plt.scatter(timestamp,nums)
    plt.show()
    plt.scatter( len(history)+np.arange(forecast_window),predictions)
    plt.show()
    
def runOnLinearData(n):
    nums = np.arange(n)# # linear
    timestamp= np.arange(n)
    doForecasting(nums,timestamp)
    
def runOnRandomData(n):
    nums = np.random.rand(n)*100 # random
    timestamp= np.arange(n)
    doForecasting(nums,timestamp)

def runOnSinusoidalData(n):
    Fs = n
    f = 5
    sample = n
    timestamp= np.arange(n)
    nums = np.sin(2 * np.pi * f * timestamp / Fs)
    doForecasting(nums,timestamp)
    
def doGridSearch(filename):
    data = pd.read_csv(filename)
    timestamp= np.arange(data.shape[0])
    nums = data['prediction'].values
    forecast_window = int(data.shape[0] * FORECAST_WINDOW_PCT)
    forecasted = pd.DataFrame(columns=['timestamp', 'prediction'])
    model = None
    if forecast_window > 0:
        history = nums#nums[0:int(data.shape[0] * (1-FORECAST_WINDOW_PCT))]#data.prediction.values 
        p = d = q = range(0, 2)
        pdq = list(itertools.product(p, d, q))
        seasonal_pdq = [(x[0], x[1], x[2], 12) for x in list(itertools.product(p, d, q))]
        min_aic = 100000
        best_param = ""
        for param in pdq:
            for param_seasonal in seasonal_pdq:
                try:
                    mod = sm.tsa.statespace.SARIMAX(y,
                                                    order=param,
                                                    seasonal_order=param_seasonal,
                                                    enforce_stationarity=False,
                                                    enforce_invertibility=False)
                    results = mod.fit()
                    print('ARIMA{}x{}12 - AIC:{}'.format(param, param_seasonal, results.aic))
                    if results.aic > 0 and results.aic < min_aic:
                        min_aic = results.aic
                        best_param = str(param) + "  " + str(param_seasonal)
                except:
                    continue
    
        print(best_param + "   " + str(min_aic))
        
#doGridSearch("../sampledata.csv")
runOnActualData("../sampledata2.csv")
#runOnActualData("../sampledata.csv")
#runOnLinearData(200)
#runOnSinusoidalData(55)
#runOnRandomData(132)



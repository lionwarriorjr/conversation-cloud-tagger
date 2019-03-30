## ML Pipeline for Detection of Aggressive/Nonconstructive Dialogue

import sys
import numpy as np
import pandas as pd
import nltk
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
from gensim import corpora, models
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline
from sklearn import metrics
from sklearn.model_selection import RandomizedSearchCV
from sklearn.utils import shuffle
from sklearn.externals import joblib
from imblearn.metrics import classification_report_imbalanced
from imblearn.pipeline import Pipeline as imb_Pipeline
from imblearn.over_sampling import SMOTE
import string
import praw

MODEL_PATH = '~/models/pipeline_SVM.pkl'
REDDIT_CLIENT_ID = 'oGWuKqgOA961MQ'
REDDIT_CLIENT_SECRET = 'aUQGgqElMF0uUY4RkP64wvexyKY'
REDDIT_USER_AGENT = 'cloudProject'
REDDIT_USERNAME = 'cloudproject'
REDDIT_PASSWORD = 'password'

def health():
    cloud_tagger = joblib.load(MODEL_PATH)
    reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID, client_secret=REDDIT_CLIENT_SECRET, \
                         user_agent=REDDIT_USER_AGENT, username=REDDIT_USERNAME, password=REDDIT_PASSWORD)
    searchVals = reddit.subreddit(subred).search(search_term, limit=100)
    # health check requires being able to pull 100 tweets from reddit and evaluate in under 5 sec
    for text in searchVals:
        cloud_tagger.predict(text)

def predict(text):
    # store model in container to be loaded and evaluated on example text
    cloud_tagger = joblib.load(MODEL_PATH)
    return cloud_tagger.predict(text)

def main():
    text = sys.argv[1]
    return predict(text)

if __name__ == "__main__":
    main()

#! usr/bin/env python3

import praw
import Pandas as dt
import datetime as dt


#reddit object: cornerstone of API
reddit = praw.Reddit(client_id='oGWuKqgOA961MQ', client_secret='aUQGgqElMF0uUY4RkP64wvexyKY', \
                     user_agent='cloudProject', username='cloudproject', password='password')


#main method
def main(search_term, subred = 'all'):

    #gets top 500 results from reddit api related to keyword
    searchVals = reddit.subreddit(subred).search(search_term, limit=500)

    #prints body
    for val in searchVals.comments:
        print(val.body)





if __name__ == "__main__":
    main()
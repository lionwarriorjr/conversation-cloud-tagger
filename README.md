# conversation-cloud-tagger
Tags the extent to which conversation dialogue is constructive vs. nonconstructive/aggressive/toxic.

Checkpoint 1:

Our initial work can be split into four parts:
Machine Learning Training/Deployment: Srihari packaged the model he found from (insert link here) into a Kubernetes container. He also found the new dataset (insert dataset here) and tested it on the model. This model is now trained and completely ready for deployment in our cloud setting. It is also setup to accept online training as described in our proposal (where the data is fetched from API queries).
Data Fetching: Parth created a scraper that will take in keywords and return all messages that fit the keyword from Reddit. This is the user’s initial interaction with our project - they enter in a user request specifying the topics to explore or particular entities (i.e. key people, articles, news content, etc.). This scraper can then get the necessary info we need to then make a determination about toxicity.
Data Streaming: Lalit is looking to use Kafka to set up a streaming pipeline that would take data returned from the data fetching program Parth wrote and efficiently stream it to the Spark code at scale, and pass back the result of the Kubernetes model back to the user. Lalit chose Kafka because it is built to stream messages in large quantities at low latency. He is also looking at using BigQuery on the Google cloud platform to be able to analyze large sets of twitter and reddit comments.
Data Application: Ben used Spark to create an application that would take in a Kubernetes model and data from Kafka and return back the toxicity level determined from the Kubernetes model back to the Kafka streaming pipeline. 

Things to Do:
As of now, each of these four parts are distinct and are mostly exploratory. The immediate next step is to connect them, starting with connecting the data fetching to the data streaming and the data application to the Kubernetes machine learning model. Then we will finally connect the two parts, build a simple user interface where the user can input their keywords and see the toxicity level returned, and run it at scale - where we will simulate multiple nodes submitting multiple user requests. If needed, we will expand our scraper to include other social media sites.

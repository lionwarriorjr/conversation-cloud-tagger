# MLTOX: Cloud-based ML Toxicity Detector

Team Members: Srihari Mohan, Lalit Verada, Ben Pikus, Parth Singh

This project exists as a cloud-based ML service that tags the extent to which conversation online is constructive vs. nonconstructive/aggressive/toxic. We leverage Machine Learning, Kubernetes, Spark, and Kafka as an exercise in building this system out from scratch in this novel and important area.

## Checkpoint 1:

Our initial work can be split into four parts:
Machine Learning Training/Deployment: Srihari worked on developing the machine learning pipeline for reading in text and classifying these examples in one of 3 categories, indicating the extent to which the example is toxic. Pipelines for text classification using Naive Bayes and SVMs are currently implemented. A pipeline for training/predicting with Recurrent Neural Networks (RNNs) is included but not yet tested. The test examples are trained with data from wikimedia comments that have been labeled by the wikimedia foundation as either non-toxic, aggressive, or toxic. The pipeline accommodates a grid search over the parameter space of the model's hyperparameters as well as running SMOTE (Synthetic Minority Oversampling) to accommodate for inbalanced class labels. The ML pipeline from start to finish is included in the notebook/cloud-conversation-tagger-unbalanced.ipynb. One needs to unzip the data to run it. Srihari also wrote the Kubernetes deployment, service, and Ingress configurations we will use to host our ML service on Kubernetes. The associated cluster is not yet set up, so it cannot yet be applied; however, it is templated and included for completeness. Srihari also wrote a python version of the notebook that reads in a pickled model and generates predictions, as well as a templated example that does the same but wraps the application for Flask. Lastly, Srihari containerized the project code to run in a Docker container by constructing a Docker image. This image will be hosted on Docker Hub and used by Kubernetes for our next checkpoint. This model is now trained and completely ready for deployment in our cloud setting. It is also setup to accept online training as described in our proposal (where the data is fetched from API queries).

Data Fetching: Parth created a scraper that will take in keywords and return all messages that fit the keyword from Reddit. This is the user’s initial interaction with our project - they enter in a user request specifying the topics to explore or particular entities (i.e. key people, articles, news content, etc.). This scraper can then get the necessary info we need to then make a determination about toxicity.
Data Streaming: Lalit is looking to use Kafka to set up a streaming pipeline that would take data returned from the data fetching program Parth wrote and efficiently stream it to the Spark code at scale, and pass back the result of the Kubernetes model back to the user. Lalit chose Kafka because it is built to stream messages in large quantities at low latency. He is also looking at using BigQuery on the Google cloud platform to be able to analyze large sets of twitter and reddit comments.

Data Application: Ben used Spark to create an application that would take in a Kubernetes model and data from Kafka and return back the toxicity level determined from the Kubernetes model back to the Kafka streaming pipeline. Currently it is setup to take a sample kubernetes container and is hooked up to a test site. As mentioned below, the next step will be to hook up the existing Kubernetes model.

Next Steps:
As of now, each of these four parts are distinct and are mostly exploratory. The immediate next step is to connect them, starting with connecting the data fetching to the data streaming and the data application to the machine learning service hosted on Kubernetes, by setting up the cluster and running the deployments. Then we will finally connect the two parts, build a simple user interface where the user can input their keywords and see the toxicity level returned, and run it at scale - where we will simulate multiple nodes submitting multiple user requests. If needed, we will expand our scraper to include other social media sites. Note that the models are not tuned as much as we'd like since they still struggle a bit in the imbalanced case. We will refine this as well for the next checkpoint. To be concrete, we will get the Kubernetes cluster up and running and have the appropriate Kubernetes configs deployed for our ML-service. We will refine the predictor we built for this checkpoint to increase both the classifier's sensitivity/specificity. We will also work on integrating Spark through MLLib into our predictive pipeline as well as using Kafka to help in our streaming job. We will try to have significant progress on all these fronts done by our next checkpoint.

Generating Reproducible results:
To run our notebook, you should be able to unzip the data in the toxic-data zip file and run the cloud-conversation-tagger-unbalanced notebook, up until the Deep Learning section (which is not yet tested). One can also run python app-toxic-tagger.py from within the app directory and pass a command line argument for the string of text to test (i.e python app-toxic-tagger.py "test example to tag"). You might need to specify python3 explicitly depending on which version of python is your default (i.e. python3 app-toxic-tagger.py "test example to tag"). Make sure to run the code in a virtual environment with Python 3.5.

## Checkpoint 2:

Our work on this project since the midterm presentation is substantial. At the midterm presentation, we had according to feedback, a somewhat vague representation of our overall architecture. The main feedback was that we should think more carefully about designing an architecture consistent with the needs of our application (and making sure that we were using the right technologies for the job). Our updated architecture is as follows: a .py file contains the code that fetches/streams tweets in real-time from Twitter using the tweepy library and pushes those tweets to a Kafka server run on GCP. The tweets pushed to the server will be constrained to a single topic (i.e. politics). The reason for this constraining is to better align our project with the cloud technologies we want to gain exposure to in this class. Namely, it makes sense to have a listener that repeatedly listens to new tweets on a topic and records them (i.e. pushes them to a server for processing). The data pushed can be fetched in real-time and used to update the analyses we run. This change is again more consistent with cloud technologies and an application that can always be up-and-running.

To be concrete, our updated infrastructure is as follows: a listener (.py file) acts as the producer to Kafka. It repeatedly streams tweets on the "politics" topic and pushes them to the Kafka server. This producer logic is one microservice that is deployed on Kubernetes. A second service houses the ML pipeline in Spark. We use Spark MLLib to train a cross-validated gradient boosting tree algorithm to learn a score with respect to how toxic a text is perceived to be. The MLLib pipeline streams the data from Kafka into a Spark DataFrame, enabling fast, parallel, and distributed processing over a potentially very large number of new tweets. Although we likely will not be able to appreciate the advantages of this approach due to the fact that we are using Twitter's free trial API (and so are limited with respect to the amount of tweets we can pull/push at a given time), we choose this approach to make it easily extensible in the event that we do get access to an even larger amount of text data we could stream through our service in real-time. The Spark pipeline transforms the data and processes it through its use of RDDs before output a result dataframe consisting of the text, its timetamp, and learned toxicity score. The toxicity scores are rolled on an averaged-per-hour basis, permitting an anomaly detection algorithm to run over this time series (tagging anomolous spikes in toxicity). A time series forecasting algorithm (a variant of state space models) is then run over the time series to learn a forecasted time series of toxicity scores one week into the future. These two dataframes are appended into tables in BigQuery. Once in BigQuery, we use Google Data Studio to generate automated dashboards of the toxicity trends, anomaly detection, and forecasted anomalies for users to interact with (DNS provided, etc. as part of GCP). These two services, the distributed ML prediction pipeline using Spark/Kafka and the Kafka producer service, are deployed onto Kubernetes pods as services/deployments in a Kubernetes cluster hosted on GKE (Google Kubernetes Engine). Kubernetes provides scalability and availability for our application. We are still in the process of finding the best way to benchmark our application against existing approaches.

Ultimately, the technologies selected, were in fact useful for MLTOX. Kafka enables real-time streaming of data from a source associated with a topic (in this case politics on Twitter). The pivot to focusing on a specific topic away from ad-hoc user queries makes Kafka a tool whose strengths (stream processing behind the scenes) are crucial. We will reemphasize that although the data we are running for this experiment makes the advantages that come from processing large streaming data using Kafka less applicable, this is only because we are using Twitter's free trial. We could conceivably set up a deployment that fetches tweets near continuously, pushing large quantities of logs every second from Twitter to the Kafka server to be analyzed in batch via Spark. This possibility is why we settled on the technologies we did. Namely, MLLib is optimized to not perform poorly on small data, but to perform extremely well when parallelizing and distributing computation across the Spark cluster with big data. We use Spark to enable our application to better scale into the future were we to remove our trial limit of Twitter and just stream large text logs continuously through Kafka and into the Spark pipeline.

### Who has done what
Described above is the MLTOX architecture. We got far in our implementation of it since the midterm presentation and describe our progress per team member next:

Srihari: Implemented working/tested Spark pipeline from start to finish using MLLib. Trained the MLLib gradient boosting tree algorithm and cross-validated the model. Containerized prediction pipeline in Docker and pushed final prediction pipeline image to Docker Hub. Deployed services on Kubernetes and tested deployments for prediction pipeline to ensure they work. Kubernetes deployments currently run on local via Minikube but will be transitioned to GCP for the final checkpoint. At this point, the Spark pipeline and Kubernetes deployment work are effectively completed for the project. Scraped training data from Twitter and helped integrate Perspective API to learn toxicity scores for the model. Researched Google BigQuery and Google Data Studio and revised architecture consistent with that described above.

Lalit:

Ben:

Parth:

### Remaining steps
We need to integrate Kafka producer code as a separate service on Kubernetes. We will then transition our Kubernetes deployment from minikube to being deployed on GCP (should be trivial). We must also integrate the Kafka consumer code to pull tweets from the server and stream them into a Spark DataFrame for distributed processing via the pipeline. Lastly, we must setup BigQuery on GCP to which we can stream our generated toxicity time series data to. From BigQuery, we will then setup Google Data Studio to generate the appropriate visualizations via a Dashboard visible to the public. One important step is to refine our forecasting code, which we noticed can be somewhat inaccurate. These are the last steps to our implementation. What remains after is writing the paper. Another key step is to better set up a framework for comparing the utility of our implementation with existing solutions. This was one of the main comments that was mentioned generally across all projects. It is one we still need to refine and are setting aside time after wrapping our implementation to consider more carefully before writing the paper.

### Pointer to Code 
The code for this checkpoint is in the same Git repo as in Checkpoint 1. The up-to-date Spark pipeline code is included on the spark-mllib branch. The code can be run by pulling this repo and building a Docker image from the provided Dockerfile using this command:

docker build -t "cloud-ml-toxic-tagger" .

Running the above should create a running container that can be viewed using docker ps -a. Grab the container just created and run:

docker run --name <container-name> -it bash

You can also run the code by setting up a Kubernetes context using minikube (install minikube first). Then cd into the kubernetes/ folder and run kubectl apply -f mltox.yaml. The ML prediction pipeline image will then be run on containers inside pods for this local deployment.

### Evaluation Plan

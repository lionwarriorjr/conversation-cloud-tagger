# conversation-cloud-tagger

Team Members: Srihari Mohan, Lalit Verada, Ben Pikus, Parth Singh

This project exists as a cloud-based ML service that tags the extent to which conversation online is constructive vs. nonconstructive/aggressive/toxic. We leverage Machine Learning, Kubernetes, Spark, and Kafka as an exercise in building this system out from scratch in this novel and important area.

Checkpoint 1:

Our initial work can be split into four parts:
Machine Learning Training/Deployment: Srihari worked on developing the machine learning pipeline for reading in text and classifying these examples in one of 3 categories, indicating the extent to which the example is toxic. Pipelines for text classification using Naive Bayes and SVMs are currently implemented. A pipeline for training/predicting with Recurrent Neural Networks (RNNs) is included but not yet tested. The test examples are trained with data from wikimedia comments that have been labeled by the wikimedia foundation as either non-toxic, aggressive, or toxic. The pipeline accommodates a grid search over the parameter space of the model's hyperparameters as well as running SMOTE (Synthetic Minority Oversampling) to accommodate for inbalanced class labels. The ML pipeline from start to finish is included in the notebook/cloud-conversation-tagger-unbalanced.ipynb. One needs to unzip the data to run it. Srihari also wrote the Kubernetes deployment, service, and Ingress configurations we will use to host our ML service on Kubernetes. The associated cluster is not yet set up, so it cannot yet be applied; however, it is templated and included for completeness. Srihari also wrote a python version of the notebook that reads in a pickled model and generates predictions, as well as a templated example that does the same but wraps the application for Flask. Lastly, Srihari containerized the project code to run in a Docker container by constructing a Docker image. This image will be hosted on Docker Hub and used by Kubernetes for our next checkpoint. This model is now trained and completely ready for deployment in our cloud setting. It is also setup to accept online training as described in our proposal (where the data is fetched from API queries).

Data Fetching: Parth created a scraper that will take in keywords and return all messages that fit the keyword from Reddit. This is the user’s initial interaction with our project - they enter in a user request specifying the topics to explore or particular entities (i.e. key people, articles, news content, etc.). This scraper can then get the necessary info we need to then make a determination about toxicity.
Data Streaming: Lalit is looking to use Kafka to set up a streaming pipeline that would take data returned from the data fetching program Parth wrote and efficiently stream it to the Spark code at scale, and pass back the result of the Kubernetes model back to the user. Lalit chose Kafka because it is built to stream messages in large quantities at low latency. He is also looking at using BigQuery on the Google cloud platform to be able to analyze large sets of twitter and reddit comments.

Data Application: Ben used Spark to create an application that would take in a Kubernetes model and data from Kafka and return back the toxicity level determined from the Kubernetes model back to the Kafka streaming pipeline. Currently it is setup to take a sample kubernetes container and is hooked up to a test site. As mentioned below, the next step will be to hook up the existing Kubernetes model.

Next Steps:
As of now, each of these four parts are distinct and are mostly exploratory. The immediate next step is to connect them, starting with connecting the data fetching to the data streaming and the data application to the machine learning service hosted on Kubernetes, by setting up the cluster and running the deployments. Then we will finally connect the two parts, build a simple user interface where the user can input their keywords and see the toxicity level returned, and run it at scale - where we will simulate multiple nodes submitting multiple user requests. If needed, we will expand our scraper to include other social media sites. Note that the models are not tuned as much as we'd like since they still struggle a bit in the imbalanced case. We will refine this as well for the next checkpoint. To be concrete, we will get the Kubernetes cluster up and running and have the appropriate Kubernetes configs deployed for our ML-service. We will refine the predictor we built for this checkpoint to increase both the classifier's sensitivity/specificity. We will also work on integrating Spark through MLLib into our predictive pipeline as well as using Kafka to help in our streaming job. We will try to have significant progress on all these fronts done by our next checkpoint.

Generating Reproducible results:
To run our notebook, you should be able to unzip the data in the toxic-data zip file and run the cloud-conversation-tagger-unbalanced notebook, up until the Deep Learning section (which is not yet tested). One can also run python app-toxic-tagger.py from within the app directory and pass a command line argument for the string of text to test (i.e python app-toxic-tagger.py "test example to tag"). You might need to specify python3 explicitly depending on which version of python is your default (i.e. python3 app-toxic-tagger.py "test example to tag"). Make sure to run the code in a virtual environment with Python 3.5.

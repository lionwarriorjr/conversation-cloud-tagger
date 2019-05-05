FROM jupyter/pyspark-notebook
MAINTAINER Srihari Mohan (smohan12@jhu.edu)
ADD . /app
WORKDIR /app
EXPOSE 80
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "app/tweet_consumer.py"]

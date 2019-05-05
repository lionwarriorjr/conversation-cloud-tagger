# FROM vaeum/ubuntu-python3-pip3
# MAINTAINER Srihari Mohan (smohan12@jhu.edu)
# ADD . /app
# WORKDIR /app
# EXPOSE 80
# RUN pip install --upgrade pip
# RUN pip install -r requirements.txt
# ENTRYPOINT ["python", "app/spark-toxic-tagger.py"]
# #ENTRYPOINT ["python", "app/app-toxic-tagger.py"]
# #CMD ["please provide text sample"]

FROM jupyter/pyspark-notebook
MAINTAINER Srihari Mohan (smohan12@jhu.edu)
ADD . /app
WORKDIR /app
EXPOSE 80
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "app/spark-toxic-tagger.py"]

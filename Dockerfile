#FROM avnergoncalves/ubuntu-python3.5
FROM vaeum/ubuntu-python3-pip3
MAINTAINER Srihari Mohan (smohan12@jhu.edu)
ADD . /app
WORKDIR /app
EXPOSE 80
#RUN apt-get -y install python3-pip
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
ENV MODEL svm
#ENTRYPOINT ["python", "app/app-toxic-tagger.py", "/app"]
ENTRYPOINT ["python", "app/app-toxic-tagger.py"]
CMD ["please provide text sample"]

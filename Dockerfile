FROM python:3.5-alpine
MAINTAINER Srihari Mohan (smohan12@jhu.edu)
ADD . /app
WORKDIR /app
RUN apk add --update alpine-sdk
RUN pip install -U pip
RUN python -m pip install --upgrade https://storage.googleapis.com/tensorflow/linux/gpu/tensorflow_gpu-1.12.0-cp35-cp35m-linux_x86_64.whl
RUN pip install -r requirements.txt
ENV MODEL svm
ENTRYPOINT ["python", "app-toxic-tagger.py"]
CMD ["test example to tag toxic text"]

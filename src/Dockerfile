FROM ubuntu:latest
COPY . /src
RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install -y python3 python3-pip

WORKDIR /src
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

EXPOSE 8888
ENTRYPOINT ["python3", "app.py"]
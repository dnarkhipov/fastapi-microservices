# pull official base image
FROM python:3.9-slim-buster

# set working directory
WORKDIR /opt/app

# set environment variables
# Prevents Python from writing pyc files to disc
#ENV PYTHONDONTWRITEBYTECODE 1
# Changed in version 3.7: The text layer of the stdout and stderr streams now is unbuffered.
#ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update \
  && apt-get -y install netcat gcc \
  && apt-get clean

# install python dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# add app
COPY ./nms ./loggers.json ./

# add entrypoint.sh
COPY ./entrypoint.sh .
RUN chmod +x /opt/app/entrypoint.sh

# run entrypoint.sh
ENTRYPOINT ["/opt/app/entrypoint.sh"]

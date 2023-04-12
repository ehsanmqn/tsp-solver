FROM python:3.10.6
ENV PYTHONUNBUFFERED 1

RUN mkdir /tsp-solver

WORKDIR /tsp-solver

ADD . /tsp-solver

RUN pip install -r requirements.txt
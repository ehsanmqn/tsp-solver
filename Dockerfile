FROM python:3.10.6
ENV PYTHONUNBUFFERED 1

RUN mkdir /tsp_solver

WORKDIR /tsp_solver

ADD . /tsp_solver

RUN pip install -r requirements.txt
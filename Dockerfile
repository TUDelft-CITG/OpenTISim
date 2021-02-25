# Start with docker image
FROM continuumio/miniconda3

ADD . /OpenTISim
WORKDIR /OpenTISim

RUN conda install nomkl pyproj

RUN pip install -e .
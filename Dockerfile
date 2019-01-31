# Start with pyramid app image
FROM continuumio/miniconda3

# Install conda stuff first
RUN conda install numpy pandas nomkl pyproj
RUN pip install pint

WORKDIR /Terminal-Optimization
ADD . /Terminal-Optimization

# Then install rest via pip
RUN python setup.py develop
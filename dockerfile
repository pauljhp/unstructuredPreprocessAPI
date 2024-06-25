FROM ubuntu:20.04 as base

# install miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O Miniconda3-latest-Linux-x86_64.sh && \
    sudo bash Miniconda3-latest-Linux-x86_64.sh
RUN conda create -n unstructured_env python=3.11

# install dependencies for unstructured seperately
RUN sudo apt-get install qpdf 
RUN conda run -n unstructured_env pip install pikepdf
RUN conda run -n unstructured_env pip install \
    numpy==1.26.4 \
    unstructured[all-docs]==0.12.4 \
    unstructured-inference==0.7.23 \
    unstructured.pytesseract==0.3.12 \
    onnx==1.16.0 \
    onnxruntime==1.15.1 \
    jose \
    passlib \
    fastapi \
    markdownify

# set environmental variables
ENV SQL_DB_CONN_STR = ""
ENV API_TOKEN = ""
ENV SECRET_KEY = ""
ENV HASH_ALGORITHM = "HS256"
ENV ACCESS_TOKEN_EXPIRE_MINUTES = 30
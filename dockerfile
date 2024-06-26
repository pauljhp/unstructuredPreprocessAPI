FROM ubuntu:20.04 as base

USER 0
# install miniconda
RUN apt-get update && apt-get install -y wget
RUN wget --output-document="Miniconda3-latest-Linux-x86_64.sh" https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
RUN bash Miniconda3-latest-Linux-x86_64.sh -b \
    -p /opt/miniconda3 && \
    /opt/miniconda3/bin/conda init
ENV PATH /opt/miniconda3/bin:$PATH
RUN conda create -n unstructured_env python=3.11 -y
SHELL ["conda", "run", "-n", "unstructured_env", "/bin/bash", "-c"]

# Install Python packages
RUN pip install pikepdf \
    numpy==1.26.4 \
    unstructured[all-docs]==0.12.4 \
    unstructured-inference==0.7.23 \
    unstructured.pytesseract==0.3.12 \
    onnx==1.16.0 \
    onnxruntime==1.15.1 \
    jose \
    passlib \
    fastapi \
    markdownify \
    uvicorn \
    pydantic

# Clone the repository
RUN git clone https://github.com/pauljhp/unstructuredPreprocessAPI /app

# Set the working directory
WORKDIR /app

# Set environment variables
ENV SQL_DB_CONN_STR=""
ENV API_TOKEN=""
ENV SECRET_KEY=""
ENV HASH_ALGORITHM="HS256"
ENV ACCESS_TOKEN_EXPIRE_MINUTES=30

# Expose port 8000 for the application
EXPOSE 8000

# Set the entrypoint to run the application
ENTRYPOINT ["conda", "run", "-n", \
    "unstructured_env", "uvicorn", \
    "main:app", "--host=0.0.0.0", "--port=8000"]
FROM ubuntu:20.04 AS base
ARG DEBIAN_FRONTEND=noninteractive

USER 0
# install miniconda
RUN apt-get update && \
        apt-get install -y --no-install-recommends \
        wget ca-certificates \
        git gnupg gnupg2 \
        libgl1 libasound2 libatk-bridge2.0-0 libc6 libcairo2 libcups2 libdbus-1-3 \ 
        libexpat1 libfontconfig1 libgbm1 libgcc1 libglib2.0-0 libgtk-3-0 libnspr4 \ 
        libnss3 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 \ 
        libxcb1 libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 \ 
        libxrandr2 libxrender1 libxss1 libxtst6 lsb-release xdg-utils \ 
        poppler-utils dbus-x11 \
        libmagic-dev xvfb \
        tesseract-ocr pandoc \
        && rm -rf /var/lib/apt/lists/* 
      
RUN wget --no-check-certificate --output-document="Miniconda3-latest-Linux-x86_64.sh" https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
RUN bash Miniconda3-latest-Linux-x86_64.sh -b \
    -p /opt/miniconda3 && \
    /opt/miniconda3/bin/conda init
ENV PATH /opt/miniconda3/bin:$PATH
RUN conda create -n unstructured_env python=3.11 -y
SHELL ["conda", "run", "-n", "unstructured_env", "/bin/bash", "-c"]

# Install Python packages
RUN pip install pikepdf \
    numpy==1.26.4 \
    nltk==3.8.1 \
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
RUN pip install \
    llama-index-readers-file \
    llama-index-readers-smart-pdf-loader \
    uuid \
    deprecated

# Clone the repository
SHELL ["/bin/bash", "-c"]
RUN git clone https://github.com/pauljhp/unstructuredPreprocessAPI /app

# Set the working directory
WORKDIR /app/src

# Set environment variables
ENV SQL_DB_CONN_STR=""
ENV API_TOKEN=""
ENV SECRET_KEY=""
ENV HASH_ALGORITHM="HS256"
ENV ACCESS_TOKEN_EXPIRE_MINUTES=30
ENV LLMSHERPA_API_URL="https://readers.llmsherpa.com/api/document/developer/parseDocument?renderFormat=all"

# Expose port 8000 for the application
EXPOSE 8000

# Set the entrypoint to run the application
ENTRYPOINT ["conda", "run", "-n", \
    "unstructured_env", "uvicorn", \
    "main:app", "--host=0.0.0.0", "--port=8000", \
    "--reload"]